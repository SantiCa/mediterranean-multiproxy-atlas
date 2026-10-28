import { env } from "cloudflare:workers";
import snapshot from "../../../data/inventory.json";
export const dynamic = "force-dynamic";
const seed: any = snapshot;

/** Idempotent batches import only versioned metadata; migrations own the schema. */
export async function POST(request: Request) {
  if (
    request.headers.get("origin") &&
    request.headers.get("origin") !== new URL(request.url).origin
  )
    return Response.json({ error: "Origen no permitido" }, { status: 403 });
  const db = env.DB;
  if (!db) return Response.json({ error: "DB unavailable" }, { status: 503 });
  if (
    await db
      .prepare("SELECT id FROM atlas_inventory_releases WHERE id=?")
      .bind(seed.version)
      .first()
  )
    return Response.json({ ready: true });
  let body: any;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "JSON inválido" }, { status: 400 });
  }
  const offset = body?.offset ?? 0;
  // Encode only the current batch: serializing the entire 15k-entry snapshot per
  // request wastes Worker CPU and memory without improving provenance.
  const links = seed.records.flatMap((r: any) =>
    (r.campaigns || []).map((c: any) => [r.id + "|" + c.id, r.id, c.id]),
  );
  const stages = [
    {
      table: "atlas_campaigns",
      columns: "id,name,provider,metadata_json",
      rows: seed.campaigns,
      encode: (c: any) => [c.id, c.name, c.provider, JSON.stringify(c)],
    },
    {
      table: "atlas_inventory",
      columns:
        "id,provider,source_id,name,realm,record_type,latitude,longitude,metadata_json",
      rows: seed.records,
      encode: (r: any) => [
        r.id,
        r.provider,
        r.source_id,
        r.name,
        r.realm,
        r.record_type || "core",
        r.latitude ?? null,
        r.longitude ?? null,
        JSON.stringify(r),
      ],
    },
    {
      table: "atlas_inventory_campaigns",
      columns: "id,record_id,campaign_id",
      rows: links,
      encode: (r: any) => r,
    },
  ];
  const total = stages.reduce((n, s) => n + s.rows.length, 0);
  if (!Number.isInteger(offset) || offset < 0 || offset > total)
    return Response.json({ error: "Offset inválido" }, { status: 400 });
  let start = 0;
  const queries = [];
  const end = Math.min(offset + 240, total);
  for (const stage of stages) {
    const batch = stage.rows.slice(
      Math.max(0, offset - start),
      Math.max(0, end - start),
    );
    start += stage.rows.length;
    for (let i = 0; i < batch.length; i += 10) {
      const rows = batch.slice(i, i + 10).map(stage.encode);
      queries.push(
        db
          .prepare(
            `INSERT OR IGNORE INTO ${stage.table}(${stage.columns}) VALUES ${rows.map(() => `(${rows[0].map(() => "?").join(",")})`).join(",")}`,
          )
          .bind(...rows.flat()),
      );
    }
  }
  if (queries.length) await db.batch(queries);
  if (end === total) {
    const n = await db
      .prepare("SELECT count(*) n FROM atlas_inventory")
      .first<{ n: number }>();
    if (n?.n !== seed.records.length)
      return Response.json(
        { error: "Recuento de importación no coincide" },
        { status: 500 },
      );
    await db
      .prepare("INSERT OR IGNORE INTO atlas_inventory_releases VALUES(?,?,?)")
      .bind(seed.version, seed.records.length, new Date().toISOString())
      .run();
  }
  return Response.json({ ready: end === total, next: end, total });
}

function filters(u: URL) {
  const conditions = ["1=1"],
    args: any[] = [];
  const kind = u.searchParams.get("kind") || "sites";
  if (kind === "sites") conditions.push("r.record_type<>'dataset'");
  else if (kind === "datasets") conditions.push("r.record_type='dataset'");
  for (const key of ["provider", "realm"]) {
    const v = u.searchParams.get(key);
    if (v && v !== "all") {
      conditions.push(`r.${key}=?`);
      args.push(v);
    }
  }
  const q = u.searchParams.get("q")?.trim().slice(0, 150);
  if (q) {
    conditions.push(
      "(r.name LIKE ? ESCAPE '\\' OR r.source_id LIKE ? ESCAPE '\\')",
    );
    const value = "%" + q.replace(/[\\%_]/g, "\\$&") + "%";
    args.push(value, value);
  }
  const campaign = u.searchParams.get("campaign");
  if (campaign && campaign !== "all") {
    if (campaign === "unknown")
      conditions.push(
        "NOT EXISTS(SELECT 1 FROM atlas_inventory_campaigns ic WHERE ic.record_id=r.id)",
      );
    else {
      conditions.push(
        "EXISTS(SELECT 1 FROM atlas_inventory_campaigns ic WHERE ic.record_id=r.id AND ic.campaign_id=?)",
      );
      args.push(campaign);
    }
  }
  return { where: conditions.join(" AND "), args };
}
export async function GET(request: Request) {
  const db = env.DB;
  if (!db) return Response.json({ error: "DB unavailable" }, { status: 503 });
  const u = new URL(request.url),
    view = u.searchParams.get("view") || "summary";
  if (
    !(await db
      .prepare("SELECT id FROM atlas_inventory_releases WHERE id=?")
      .bind(seed.version)
      .first())
  )
    return Response.json({
      needsBootstrap: true,
      version: seed.version,
      counts: seed.counts,
    });
  if (view === "summary") {
    const providers = await db
      .prepare(
        "SELECT provider,count(*) count FROM atlas_inventory GROUP BY provider ORDER BY provider",
      )
      .all();
    const campaigns = await db
      .prepare(
        "SELECT c.id,c.name,c.provider,c.metadata_json,count(*) count FROM atlas_campaigns c JOIN atlas_inventory_campaigns ic ON ic.campaign_id=c.id GROUP BY c.id ORDER BY c.name",
      )
      .all();
    return Response.json({
      version: seed.version,
      scope: seed.scope,
      counts: seed.counts,
      coverage: seed.coverage,
      time_extent: seed.time_extent,
      limitations: seed.limitations,
      providers: providers.results,
      campaigns: campaigns.results.map((c: any) => ({
        ...c,
        metadata_json: undefined,
        ...JSON.parse(c.metadata_json),
      })),
    });
  }
  if (view === "detail") {
    const row = await db
      .prepare("SELECT metadata_json FROM atlas_inventory WHERE id=?")
      .bind(u.searchParams.get("id") || "")
      .first<{ metadata_json: string }>();
    return row
      ? Response.json(JSON.parse(row.metadata_json))
      : Response.json({ error: "No encontrado" }, { status: 404 });
  }
  const { where, args } = filters(u);
  const n = await db
    .prepare(`SELECT count(*) n FROM atlas_inventory r WHERE ${where}`)
    .bind(...args)
    .first<{ n: number }>();
  if (view === "groups") {
    const rows = await db
      .prepare(
        `SELECT COALESCE(c.id,'unknown') id,COALESCE(c.name,'Sin campaña declarada') name,c.provider,count(DISTINCT r.id) count FROM atlas_inventory r LEFT JOIN atlas_inventory_campaigns ic ON ic.record_id=r.id LEFT JOIN atlas_campaigns c ON c.id=ic.campaign_id WHERE ${where} GROUP BY c.id ORDER BY count DESC`,
      )
      .bind(...args)
      .all();
    return Response.json({ total: n?.n, groups: rows.results });
  }
  if (view === "map") {
    const rows = await db
      .prepare(
        `SELECT id,name,provider,realm,record_type,latitude,longitude,(SELECT ic.campaign_id FROM atlas_inventory_campaigns ic WHERE ic.record_id=r.id LIMIT 1) campaign_id FROM atlas_inventory r WHERE ${where} AND latitude IS NOT NULL AND longitude IS NOT NULL ORDER BY id LIMIT 20001`,
      )
      .bind(...args)
      .all();
    return Response.json({
      total: n?.n,
      points: rows.results.slice(0, 20000),
      truncated: rows.results.length > 20000,
      limit: 20000,
    });
  }
  if (view === "export") {
    const rows = await db
      .prepare(
        `SELECT metadata_json FROM atlas_inventory r WHERE ${where} ORDER BY name LIMIT 20001`,
      )
      .bind(...args)
      .all();
    if (rows.results.length > 20000)
      return Response.json(
        {
          error: "Reduce la selección antes de exportar más de 20000 entradas",
        },
        { status: 422 },
      );
    const fields = [
      "id",
      "provider",
      "source_id",
      "name",
      "record_type",
      "realm",
      "latitude",
      "longitude",
      "source_url",
      "dataset_doi",
      "publication_year",
      "dataset_publication_year",
      "metadata_status",
      "raw_sha256",
    ];
    const quote = (v: any) => '"' + String(v ?? "").replaceAll('"', '""') + '"';
    const lines = [
      fields.concat(["campaigns", "campaign_source_ids"]).map(quote).join(","),
      ...rows.results.map((row: any) => {
        const r = JSON.parse(row.metadata_json);
        return fields
          .map((k) => quote(r[k]))
          .concat([
            quote(r.campaigns.map((c: any) => c.name).join(" | ")),
            quote(r.campaigns.map((c: any) => c.id).join(" | ")),
          ])
          .join(",");
      }),
    ];
    return new Response("\ufeff" + lines.join("\n"), {
      headers: {
        "Content-Type": "text/csv;charset=utf-8",
        "Content-Disposition": 'attachment; filename="medatlas-catalogue.csv"',
      },
    });
  }
  const offset = Math.max(
    0,
    Math.min(100000, Number(u.searchParams.get("offset")) || 0),
  );
  const rows = await db
    .prepare(
      `SELECT metadata_json FROM atlas_inventory r WHERE ${where} ORDER BY name,id LIMIT 60 OFFSET ?`,
    )
    .bind(...args, offset)
    .all();
  return Response.json({
    total: n?.n,
    offset,
    limit: 60,
    records: rows.results.map((r: any) => JSON.parse(r.metadata_json)),
  });
}
