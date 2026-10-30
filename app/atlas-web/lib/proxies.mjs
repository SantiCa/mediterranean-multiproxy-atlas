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
/** Search aliases do not transform the archived variable or its values. */
export function elementRatioAlias(name) {
  const elements = { titanium:"Ti", calcium:"Ca", aluminium:"Al", aluminum:"Al", iron:"Fe", potassium:"K", zirconium:"Zr", rubidium:"Rb", barium:"Ba", strontium:"Sr", manganese:"Mn", silicon:"Si", bromine:"Br", chlorine:"Cl", molybdenum:"Mo", uranium:"U", thorium:"Th" };
  return String(name || "").replace(/\b(titanium|calcium|aluminium|aluminum|iron|potassium|zirconium|rubidium|barium|strontium|manganese|silicon|bromine|chlorine|molybdenum|uranium|thorium)\b/gi, x => elements[x.toLowerCase()]);
}
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
  const sourceRecord =
    s.publication_year !== undefined
      ? { ...r, publication_year: s.publication_year }
      : r;
  return (
    recordMatches(sourceRecord, f) &&
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
        elementRatioAlias(s.parameter_name_pangaea),
        /polen|pollen/i.test(s.family || "") ? "bosque vegetación árboles" : "",
      ]
        .flat()
        .filter(Boolean)
        .join(" ");
  }
  return [...groups.values()]
    .map((g) => ({ ...g, records: g.records.size, search: fold(g.search) }))
    .sort((a, b) => a.label.localeCompare(b.label, "es"));
}
/** Comparison groups preceded by the explicit aggregations they support. */
export function proxyCatalog(data, f = {}) {
  const g = proxyGroups(data, f);
  return [...aggregateGroups(g, data), ...g];
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
      (q.aggregates !== false || !g.aggregate) &&
      (!q.minRecords || g.records >= q.minRecords) &&
      (!q.overlap || (g.min <= q.max && g.max >= q.min)) &&
      terms.every((t) => g.search.includes(t)),
  );
}

/* Map aggregation of groups that measure the same quantity in the same unit (user
 * request 29-10-2026). Membership is explicit and rule-based; methods, calibrations
 * and seasons stay distinct per series and values are NOT harmonised. */
const txt = (s) =>
  fold(
    [s.proxy, s.variable_label, s.label, s.compatibility_group, s.parameter_name_pangaea, s.taxon]
      .filter(Boolean)
      .join(" "),
  );
const PLANKTIC = /bulloides|ruber|inflata|pachyderma|globigerin|globorotalia|neogloboquadrina|orbulina|sacculifer|truncatulinoides|scitula|planct|plankt/;
const BENTHIC = /cibicid|uvigerina|melonis|planulina|hoeglundina|bent|oridorsalis|pyrgo|globobulimina/;
const permil = (s) => /‰/.test(s.unit) && /pdb/i.test(s.unit) && !/smow/i.test(s.unit);
const season = (t) =>
  /summer|july|august|jul.?sep|verano|\bjas\b/.test(t)
    ? "summer"
    : /winter|january|february|jan.?mar|invierno|\bjfm\b/.test(t)
      ? "winter"
      : /spring|primavera|autumn|otono|fall/.test(t)
        ? "other"
        : "annual";
const isSST = (s, t) =>
  s.unit === "°C" &&
  /sea.?surface.?temp|(^|[^a-z])sst([^a-z]|$)|temperatura superficial del mar/.test(t) &&
  !/maat|air|lake|lago|subsurface|subsuperficial/.test(t);
const foram = (s, t, iso) =>
  permil(s) &&
  (iso === "18" ? /18o|d18o/.test(t) : /13c|d13c/.test(t)) &&
  !/speleothem|espeleotema|carbonate bulk|bulk|organic|org/.test(t);
export const AGGREGATES = [
  { id: "sst_all", label: "Temperatura superficial del mar · todos los métodos y estaciones", unit: "°C", family: "Temperatura", test: (s, t) => isSST(s, t) },
  { id: "sst_annual", label: "Temperatura superficial del mar · anual (todos los métodos)", unit: "°C", family: "Temperatura", test: (s, t) => isSST(s, t) && season(t) === "annual" },
  { id: "sst_summer", label: "Temperatura superficial del mar · verano (todos los métodos)", unit: "°C", family: "Temperatura", test: (s, t) => isSST(s, t) && season(t) === "summer" },
  { id: "sst_winter", label: "Temperatura superficial del mar · invierno (todos los métodos)", unit: "°C", family: "Temperatura", test: (s, t) => isSST(s, t) && season(t) === "winter" },
  { id: "d18o_planct", label: "δ18O foraminíferos planctónicos · todas las especies", unit: "‰ (V)PDB", family: "Isótopos estables", test: (s, t) => foram(s, t, "18") && PLANKTIC.test(t) && !BENTHIC.test(t) },
  { id: "d18o_bent", label: "δ18O foraminíferos bentónicos · todas las especies", unit: "‰ (V)PDB", family: "Isótopos estables", test: (s, t) => foram(s, t, "18") && BENTHIC.test(t) && !PLANKTIC.test(t) },
  { id: "d13c_planct", label: "δ13C foraminíferos planctónicos · todas las especies", unit: "‰ (V)PDB", family: "Isótopos estables", test: (s, t) => foram(s, t, "13") && PLANKTIC.test(t) && !BENTHIC.test(t) },
  { id: "d13c_bent", label: "δ13C foraminíferos bentónicos · todas las especies", unit: "‰ (V)PDB", family: "Isótopos estables", test: (s, t) => foram(s, t, "13") && BENTHIC.test(t) && !PLANKTIC.test(t) },
  { id: "toc_pct", label: "Carbono orgánico total (TOC) · todos los métodos", unit: "%", family: "Materia orgánica y biomarcadores", test: (s, t) => s.unit === "%" && /carbon.?organic|(^|[^a-z])toc([^a-z]|$)|corg|carbono organico/.test(t) && !/isotop|13c|accumulation|flux/.test(t) },
  { id: "caco3_pct", label: "Carbonato cálcico (CaCO3) · todos los métodos", unit: "%", family: "Sedimentología", test: (s, t) => s.unit === "%" && /calcium carbonate|caco3|carbonato/.test(t) && !/accumulation|flux|free/.test(t) },
];
export const aggregateKey = (a) => JSON.stringify(["agg", a.id, a.unit]);
export const isAggregateKey = (k) => typeof k === "string" && k.startsWith('["agg"');
/* Same PANGAEA parameter (controlled vocabulary) and same unit, any method: the
 * parameter defines the measured quantity; methods remain per series. */
const paramName = (s) => s.parameter_name_pangaea || null;
/** Identical parameter names can hide different fractions or pollen sums.
 * Native counts remain sample counts, not abundance percentages. */
export function comparisonContext(s) {
  if (s.comparison_context_key) return s.comparison_context_key;
  const t = fold([s.source_column, s.parameter_comment, s.source_dataset_title, s.compatibility_group].filter(Boolean).join(" "));
  if (/excl.{0,12}pin|without.{0,12}pin|sin.{0,12}pin/.test(t)) return "pollen_sum_excludes_pinus";
  if (/sortable silt/i.test(paramName(s) || "")) {
    if (/mean.*carb.free/.test(t)) return "sortable_silt_native_mean_carb_free_percent_label_requires_review";
    if (/contourite/.test(t)) return "sortable_silt_percent_contourites";
    if (/pelagic/.test(t)) return "sortable_silt_percent_pelagics";
  }
  if (/grain|size fraction|silt|clay/i.test(paramName(s) || "")) {
    if (/non.carbonate|carb.free|carbonate.free/.test(t)) return "grain_fraction_noncarbonate";
    if (/total fraction|bulk sediment/.test(t)) return "grain_fraction_total";
  }
  if (/pore fluids/.test(t)) return "matrix_pore_fluid";
  if (/soluble salts/.test(t)) return "matrix_soluble_salt";
  return null;
}
export const paramKey = (s) =>
  paramName(s) && !(s.unit === "#" && /polen|pollen/i.test(s.family || ""))
    ? JSON.stringify(["agg", "p:" + fold(paramName(s)), s.unit, ...(comparisonContext(s) ? [comparisonContext(s)] : [])]) : null;
export function aggregatesOf(s) {
  const t = txt(s),
    out = AGGREGATES.filter((a) => a.test(s, t)).map(aggregateKey),
    p = paramKey(s);
  return p ? [...out, p] : out;
}
/** Series selected by a group key: one comparison group, or an explicit aggregation. */
export const inGroup = (s, key) =>
  isAggregateKey(key) ? aggregatesOf(s).includes(key) : groupKey(s) === key;
/** Aggregation cards built from the comparison groups (≥ 2 member groups). */
export function aggregateGroups(groups, data) {
  const out = [];
  for (const a of AGGREGATES) {
    const key = aggregateKey(a),
      members = groups.filter((g) => !g.aggregate && g.series.some((s) => aggregatesOf(s).includes(key)));
    if (members.length < 2) continue;
    const series = members.flatMap((g) => g.series.filter((s) => aggregatesOf(s).includes(key)));
    out.push({
      key,
      id: "agg:" + a.id,
      label: a.label,
      unit: a.unit,
      family: a.family,
      variable: a.label,
      method: "Agrupado: " + members.length + " grupos (" + [...new Set(members.map((g) => g.method))].slice(0, 4).join("; ") + (members.length > 4 ? "…" : "") + ")",
      compatibility: null,
      evidence: "aggregation",
      aggregate: true,
      members: members.map((g) => g.key),
      series,
      records: new Set(series.map((s) => s.record_id)).size,
      count: series.reduce((n, s) => n + (s.observation_count ?? s.rows?.length ?? 0), 0),
      min: Math.min(...members.map((g) => g.min)),
      max: Math.max(...members.map((g) => g.max)),
      search: fold(a.label + " agrupado " + members.map((g) => g.search).join(" ")),
    });
  }
  const seen = new Set(out.map((g) => g.members.join("|"))),
    byParam = new Map();
  for (const g of groups)
    for (const s of g.series) {
      const k = paramKey(s);
      if (!k) continue;
      if (!byParam.has(k)) byParam.set(k, { name: paramName(s), unit: s.unit, family: g.family, context: comparisonContext(s), members: new Map() });
      byParam.get(k).members.set(g.key, g);
    }
  for (const [key, a] of byParam) {
    const members = [...a.members.values()];
    if (members.length < 2 || seen.has(members.map((g) => g.key).join("|"))) continue;
    const series = members.flatMap((g) => g.series.filter((s) => paramKey(s) === key));
    const records = new Set(series.map((s) => s.record_id)).size;
    if (records < 2) continue;
    out.push({
      key,
      id: "agg:" + key,
      label: a.name + (a.context ? " · " + ({pollen_sum_excludes_pinus:"suma sin Pinus",grain_fraction_noncarbonate:"fracción no carbonatada",grain_fraction_total:"fracción total",sortable_silt_percent_pelagics:"sedimento pelágico",sortable_silt_percent_contourites:"contornitas",matrix_pore_fluid:"fluido intersticial",matrix_soluble_salt:"sales solubles"}[a.context] || "contexto específico") : "") + " · todos los métodos",
      unit: a.unit,
      family: a.family,
      variable: a.name,
      method: "Agrupado por parámetro PANGAEA: " + members.length + " grupos (" + [...new Set(members.map((g) => g.method))].slice(0, 4).join("; ") + (members.length > 4 ? "…" : "") + ")",
      compatibility: null,
      evidence: "aggregation",
      aggregate: true,
      members: members.map((g) => g.key),
      series,
      records,
      count: series.reduce((n, s) => n + (s.observation_count ?? s.rows?.length ?? 0), 0),
      min: Math.min(...members.map((g) => g.min)),
      max: Math.max(...members.map((g) => g.max)),
      search: fold(a.name + " agrupado " + members.map((g) => g.search).join(" ")),
    });
  }
  return out;
}
/** Sort options of the proxy explorer. */
export function sortGroups(groups, by = "records") {
  const g = [...groups];
  if (by === "records") g.sort((a, b) => b.records - a.records || b.count - a.count || a.label.localeCompare(b.label, "es"));
  else if (by === "values") g.sort((a, b) => b.count - a.count || b.records - a.records);
  else g.sort((a, b) => a.label.localeCompare(b.label, "es"));
  return g;
}
