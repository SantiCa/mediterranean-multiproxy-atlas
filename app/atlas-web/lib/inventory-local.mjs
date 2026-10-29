/** Inventory queries computed in the browser from the static snapshot
 * (/snapshot/inventory.json), reproducing the former D1 views of /api/inventory:
 * summary, list (60 per page, by name then id), map (≤ 20 000 points), groups,
 * detail and export (CSV ≤ 20 000). No database reads. */
const byStr = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
// SQLite LIKE is case-insensitive for ASCII letters only.
const asciiLower = (s) => String(s ?? "").replace(/[A-Z]/g, (c) => c.toLowerCase());

export function prepareInventory(seed, curated) {
  const campaigns = new Map(seed.campaigns.map((c) => [c.id, c]));
  const records = seed.records.map((r) => ({
    ...r,
    record_type: r.record_type || "core",
    _name: asciiLower(r.name),
    _source: asciiLower(r.source_id),
    _campaigns: new Set((r.campaigns || []).map((c) => c.id)),
  }));
  const byId = new Map(records.map((r) => [r.id, r]));
  return { seed, campaigns, records, byId, curated };
}

function filtered(inv, p) {
  const kind = p.get("kind") || "sites",
    provider = p.get("provider"),
    realm = p.get("realm"),
    q = asciiLower(p.get("q")?.trim().slice(0, 150) || ""),
    campaign = p.get("campaign");
  return inv.records.filter(
    (r) =>
      (kind === "sites" ? r.record_type !== "dataset" : kind === "datasets" ? r.record_type === "dataset" : true) &&
      (!provider || provider === "all" || r.provider === provider) &&
      (!realm || realm === "all" || r.realm === realm) &&
      (!q || r._name.includes(q) || r._source.includes(q)) &&
      (!campaign || campaign === "all" || (campaign === "unknown" ? r._campaigns.size === 0 : r._campaigns.has(campaign))),
  );
}
const clean = ({ _name, _source, _campaigns, ...r }) => r;

/** Returns { status, body } (JSON) or { status, csv }. */
export function queryInventory(inv, search) {
  const p = new URLSearchParams(search),
    view = p.get("view") || "summary",
    seed = inv.seed;
  if (view === "summary") {
    const providers = new Map(),
      counts = new Map();
    for (const r of inv.records) {
      providers.set(r.provider, (providers.get(r.provider) || 0) + 1);
      for (const c of r._campaigns) counts.set(c, (counts.get(c) || 0) + 1);
    }
    const cur = inv.curated;
    return {
      status: 200,
      body: {
        version: seed.version,
        scope: seed.scope,
        counts: seed.counts,
        quantitative: {
          records: cur.records.length,
          series: cur.series.length,
          observations: cur.series.reduce((n, s) => n + (s.observation_count || 0), 0),
        },
        coverage: seed.coverage,
        time_extent: seed.time_extent,
        limitations: seed.limitations,
        providers: [...providers].sort((a, b) => byStr(a[0], b[0])).map(([provider, count]) => ({ provider, count })),
        campaigns: [...counts]
          .map(([id, count]) => ({ ...inv.campaigns.get(id), id, count }))
          .filter((c) => c.name)
          .sort((a, b) => byStr(a.name, b.name)),
      },
    };
  }
  if (view === "detail") {
    const r = inv.byId.get(p.get("id") || "");
    if (!r) return { status: 404, body: { error: "No encontrado" } };
    const linked = inv.curated.records.filter((c) => (c.inventory_ids || []).includes(r.id)).map((c) => c.id);
    return { status: 200, body: { ...clean(r), curated_record_ids: linked, curated_record_id: linked[0] || r.curated_record_id } };
  }
  const rows = filtered(inv, p);
  if (view === "groups") {
    const g = new Map();
    for (const r of rows) {
      const ids = r._campaigns.size ? [...r._campaigns] : ["unknown"];
      for (const id of ids) {
        if (!g.has(id)) {
          const c = inv.campaigns.get(id);
          g.set(id, { id, name: c?.name || "Sin campaña declarada", provider: c?.provider ?? null, count: 0 });
        }
        g.get(id).count++;
      }
    }
    return { status: 200, body: { total: rows.length, groups: [...g.values()].sort((a, b) => b.count - a.count) } };
  }
  if (view === "map") {
    const pts = rows
      .filter((r) => r.latitude != null && r.longitude != null)
      .sort((a, b) => byStr(a.id, b.id))
      .map((r) => ({ id: r.id, name: r.name, provider: r.provider, realm: r.realm, record_type: r.record_type, latitude: r.latitude, longitude: r.longitude, campaign_id: r.campaigns?.[0]?.id ?? null }));
    return { status: 200, body: { total: rows.length, points: pts.slice(0, 20000), truncated: pts.length > 20000, limit: 20000 } };
  }
  const sorted = [...rows].sort((a, b) => byStr(a.name, b.name) || byStr(a.id, b.id));
  if (view === "export") {
    if (sorted.length > 20000)
      return { status: 422, body: { error: "Reduce la selección antes de exportar más de 20000 entradas" } };
    const fields = ["id", "provider", "source_id", "name", "record_type", "realm", "latitude", "longitude", "source_url", "dataset_doi", "publication_year", "dataset_publication_year", "metadata_status", "raw_sha256"];
    const quote = (v) => '"' + String(v ?? "").replaceAll('"', '""') + '"';
    const lines = [
      fields.concat(["campaigns", "campaign_source_ids"]).map(quote).join(","),
      ...sorted.map((r) =>
        fields
          .map((k) => quote(r[k]))
          .concat([quote((r.campaigns || []).map((c) => c.name).join(" | ")), quote((r.campaigns || []).map((c) => c.id).join(" | "))])
          .join(","),
      ),
    ];
    return { status: 200, csv: "﻿" + lines.join("\n") };
  }
  const offset = Math.max(0, Math.min(100000, Number(p.get("offset")) || 0));
  return { status: 200, body: { total: rows.length, offset, limit: 60, records: sorted.slice(offset, offset + 60).map(clean) } };
}

let cache = null;
/** fetch()-compatible access to the static inventory, for /api/inventory URLs. */
/** @param {string} url @param {any} [_init] @returns {Promise<Response>} */
export function inventoryFetch(url, _init) {
  cache ||= Promise.all([
    fetch("/snapshot/inventory.json").then((r) => {
      if (!r.ok) throw new Error("No se pudo leer el inventario");
      return r.json();
    }),
    fetch("/snapshot/catalog.json").then((r) => r.json()),
  ]).then(([seed, curated]) => prepareInventory(seed, curated));
  cache.catch(() => (cache = null));
  return cache.then((inv) => {
    const out = queryInventory(inv, String(url).split("?")[1] || "");
    return out.csv != null
      ? new Response(out.csv, { status: out.status, headers: { "Content-Type": "text/csv;charset=utf-8" } })
      : new Response(JSON.stringify(out.body), { status: out.status, headers: { "Content-Type": "application/json" } });
  });
}
