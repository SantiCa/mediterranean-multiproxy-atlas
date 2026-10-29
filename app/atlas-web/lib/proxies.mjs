/** A map compares one variable/method/unit group. Labels never establish equivalence. */
export const groupKey = (s) =>
  JSON.stringify([s.proxy, s.compatibility_group || s.id, s.unit]);
export const fold = (s) =>
  String(s ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replaceAll("δ", "d")
    .replaceAll("¹", "1")
    .replaceAll("³", "3")
    .replaceAll("⁸", "8");
export const isContinental = (r) => r.realm !== "marine";
export function recordMatches(r, f) {
  return (
    (!f.provider || f.provider === "all" || r.provider === f.provider) &&
    (!f.realm ||
      f.realm === "all" ||
      (f.realm === "continental" ? isContinental(r) : r.realm === f.realm)) &&
    (!f.yearMin || r.publication_year >= f.yearMin) &&
    (!f.yearMax ||
      (r.publication_year != null && r.publication_year <= f.yearMax))
  );
}
export function seriesMatches(s, r, f) {
  return (
    recordMatches(r, f) &&
    (!f.chronology ||
      f.chronology === "all" ||
      s.chronology_status === f.chronology)
  );
}
export function proxyGroups(data, f = {}) {
  const records = new Map(data.records.map((r) => [r.id, r])),
    groups = new Map();
  for (const s of data.series) {
    const r = records.get(s.record_id);
    if (!r || !seriesMatches(s, r, f)) continue;
    const key = groupKey(s);
    if (!groups.has(key))
      groups.set(key, {
        key,
        id: s.proxy,
        label: s.label,
        unit: s.unit,
        family: s.family || "Otros",
        variable: s.variable_label || s.label,
        method: s.method || "Método archivado",
        compatibility: s.compatibility_group,
        evidence: s.evidence_type || "published_value",
        series: [],
        records: new Set(),
        count: 0,
        min: Infinity,
        max: -Infinity,
        search: "",
      });
    const g = groups.get(key);
    g.series.push(s);
    g.records.add(r.id);
    g.count += s.observation_count ?? s.rows?.length ?? 0;
    const ages = (s.rows || [])
      .filter((x) => Number.isFinite(x[0]))
      .map((x) => x[0]);
    const lo = s.age_min_ka_bp ?? (ages.length ? Math.min(...ages) : null),
      hi = s.age_max_ka_bp ?? (ages.length ? Math.max(...ages) : null);
    if (Number.isFinite(lo)) g.min = Math.min(g.min, lo);
    if (Number.isFinite(hi)) g.max = Math.max(g.max, hi);
    g.search +=
      " " +
      [
        s.proxy,
        s.label,
        s.variable_label,
        s.family,
        s.method,
        s.unit,
        s.taxon,
        r.name,
        r.provider,
        s.search_aliases,
      ]
        .flat()
        .filter(Boolean)
        .join(" ");
  }
  return [...groups.values()]
    .map((g) => ({ ...g, records: g.records.size, search: fold(g.search) }))
    .sort((a, b) => a.label.localeCompare(b.label, "es"));
}
export function filterGroups(groups, q = {}) {
  const terms = fold(q.search).split(/\s+/).filter(Boolean);
  return groups.filter(
    (g) =>
      (!q.family || q.family === "all" || g.family === q.family) &&
      (!q.variable || q.variable === "all" || g.variable === q.variable) &&
      (!q.method || q.method === "all" || g.method === q.method) &&
      (!q.unit || q.unit === "all" || g.unit === q.unit) &&
      (!q.favoritesOnly || q.favorites?.includes(g.key)) &&
      (!q.overlap || (g.min <= q.max && g.max >= q.min)) &&
      terms.every((t) => g.search.includes(t)),
  );
}
