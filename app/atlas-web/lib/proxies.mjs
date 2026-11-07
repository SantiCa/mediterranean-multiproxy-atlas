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
/** Display vocabulary only: native metadata and observations remain unchanged. */
export function proxyFamily(s) {
  const parameter = s.comparison_parameter_name || s.parameter_name_pangaea || s.variable_label || s.label || "";
  if (/oxygen index.*(?:CO2|carbon)|oxygen index.*organic carbon/i.test(parameter)) return "Materia orgánica y biomarcadores";
  return ({ Palinología: "Polen", Biomarcadores: "Materia orgánica y biomarcadores" })[s.family] || s.family || "Otros";
}
export function associationAliases(s) {
  const family = proxyFamily(s);
  return /Polen|Foraminíferos|Micropaleontología|Oxigenación bentónica/.test(family)
    ? "asociación asociaciones ensamblaje assemblage especies taxones censo abundancia " +
      (/Polen/.test(family) ? "vegetación polen pollen" : "microfósiles")
    : "";
}
/** Search aliases do not transform the archived variable or its values. */
export function elementRatioAlias(name) {
  const elements = { titanium:"Ti", calcium:"Ca", aluminium:"Al", aluminum:"Al", iron:"Fe", potassium:"K", zirconium:"Zr", rubidium:"Rb", barium:"Ba", strontium:"Sr", manganese:"Mn", silicon:"Si", bromine:"Br", chlorine:"Cl", molybdenum:"Mo", uranium:"U", thorium:"Th" };
  return String(name || "").replace(/\b(titanium|calcium|aluminium|aluminum|iron|potassium|zirconium|rubidium|barium|strontium|manganese|silicon|bromine|chlorine|molybdenum|uranium|thorium)\b/gi, x => elements[x.toLowerCase()]);
}
/** Canonical discovery names only; base groups, units and native values stay intact. */
const UK37_PRIME = "Índice de insaturación de alquenonas (UK′37)";
export function canonicalParameterName(s) {
  const raw = s.comparison_parameter_name || s.parameter_name_pangaea || s.proxy || s.variable_label || s.label || "";
  const name = fold(raw).replace(/[_ ,]+/g, " ").replace(/\s+/g, " ").trim();
  if (["toc", "total organic carbon", "carbon organic total", "carbono organico total", "corg", "c org", "carbon organic per unit sediment mass"].includes(name)) return "Carbono orgánico total (TOC)";
  if (["caco3", "calcium carbonate", "carbonato calcico"].includes(name)) return "Calcium carbonate";
  const indexName = name.replace(/[′’]/g, "'");
  if (["uk'37", "alkenone uk37prime", "alkenone unsaturation index uk'37"].includes(indexName)
      || (indexName === "alkenone uk37" && /^uk['′’]37\b/i.test(s.source_column || ""))) return UK37_PRIME;
  if (["tic", "total inorganic carbon", "carbon inorganic total", "carbono inorganico total"].includes(name)) return "Carbono inorgánico total (TIC)";
  const ratio = fold(elementRatioAlias(raw)).replace(/_/g, " ").trim().match(/^(?:(ln|log|log10)[\s(-]*)?(ti|fe|si|zr|k|mn|u|mo|ba|br|sr|ca)\s*\/\s*(ca|al|ti|rb|th|sr)\)?(?:\s+ratio)?$/);
  if (ratio) {
    const symbols = { ti:"Ti", fe:"Fe", si:"Si", zr:"Zr", k:"K", mn:"Mn", u:"U", mo:"Mo", ba:"Ba", ca:"Ca", al:"Al", rb:"Rb", th:"Th", br:"Br", sr:"Sr" };
    return (ratio[1] ? ratio[1] + "-" : "") + symbols[ratio[2]] + "/" + symbols[ratio[3]] + " ratio";
  }
  return s.comparison_parameter_name || s.parameter_name_pangaea || null;
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
  // A newly linked series can come from another repository than the core record.
  const sourceRecord = { ...r, provider: s.provider || r.provider,
    publication_year: s.publication_year !== undefined ? s.publication_year : r.publication_year };
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
    const canonical = canonicalParameterName(s);
    const controlledAlias = [UK37_PRIME, "Carbono orgánico total (TOC)", "Carbono inorgánico total (TIC)", "Calcium carbonate"].includes(canonical)
      || /^[\w-]+\/[\w]+ ratio$/.test(canonical || "");
    if (!groups.has(key))
      groups.set(key, {
        key,
        id: s.proxy,
        label: controlledAlias ? canonical : s.label,
        unit: s.unit,
        family: proxyFamily(s),
        variable: controlledAlias ? canonical : s.variable_label || s.label,
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
        associationAliases(s),
        elementRatioAlias(s.comparison_parameter_name || s.parameter_name_pangaea),
        canonicalParameterName(s),
        canonical === "Carbono orgánico total (TOC)" ? "TOC total organic carbon Corg carbono orgánico total" : "",
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
  /late.summer.{0,12}autumn|final.{0,12}verano.{0,12}otono/.test(t)
    ? "other"
    : /summer|july|august|jul.?sep|verano|\bjas\b/.test(t)
    ? "summer"
    : /winter|january|february|jan.?mar|invierno|\bjfm\b/.test(t)
      ? "winter"
      : /spring|primavera|autumn|otono|fall/.test(t)
        ? "other"
        : /annual|anual|yearly|year.mean|mean.annual/.test(t) ? "annual" : "unspecified";
const isSST = (s, t) =>
  s.unit === "°C" &&
  s.comparison_context_key !== "black_sea_0_200m_archived" &&
  /sea.?surface.?temp|(^|[^a-z])sst([^a-z]|$)|temperatura superficial del mar/.test(t) &&
  !/maat|air|lake|lago|subsurface|subsuperficial/.test(t);
const foram = (s, t, iso) =>
  permil(s) &&
  (iso === "18" ? /18o|d18o/.test(t) : /13c|d13c/.test(t)) &&
  !/speleothem|espeleotema|carbonate bulk|bulk|organic|org/.test(t);
export const AGGREGATES = [
  { id: "sst_all", label: "Temperatura superficial del mar · todos los métodos y estaciones", unit: "°C", family: "Temperatura", test: (s, t) => isSST(s, t) },
  { id: "sst_annual", label: "Temperatura superficial del mar · anual (todos los métodos)", unit: "°C", family: "Temperatura", test: (s, t) => isSST(s, t) && season(t) === "annual" },
  { id: "sst_summer", label: "Temperatura superficial del mar · verano y meses estivales", unit: "°C", family: "Temperatura", test: (s, t) => isSST(s, t) && season(t) === "summer" },
  { id: "sst_winter", label: "Temperatura superficial del mar · invierno y meses invernales", unit: "°C", family: "Temperatura", test: (s, t) => isSST(s, t) && season(t) === "winter" },
  { id: "sst_unspecified", label: "Temperatura superficial del mar · estación no declarada (todos los métodos)", unit: "°C", family: "Temperatura", test: (s, t) => isSST(s, t) && season(t) === "unspecified" },
  { id: "d18o_planct", label: "δ18O foraminíferos planctónicos · todas las especies", unit: "‰ (V)PDB", family: "Isótopos estables", test: (s, t) => foram(s, t, "18") && PLANKTIC.test(t) && !BENTHIC.test(t) },
  { id: "d18o_bent", label: "δ18O foraminíferos bentónicos · todas las especies", unit: "‰ (V)PDB", family: "Isótopos estables", test: (s, t) => foram(s, t, "18") && BENTHIC.test(t) && !PLANKTIC.test(t) },
  { id: "d13c_planct", label: "δ13C foraminíferos planctónicos · todas las especies", unit: "‰ (V)PDB", family: "Isótopos estables", test: (s, t) => foram(s, t, "13") && PLANKTIC.test(t) && !BENTHIC.test(t) },
  { id: "d13c_bent", label: "δ13C foraminíferos bentónicos · todas las especies", unit: "‰ (V)PDB", family: "Isótopos estables", test: (s, t) => foram(s, t, "13") && BENTHIC.test(t) && !PLANKTIC.test(t) },
  { id: "toc_pct", label: "Carbono orgánico total (TOC) · todos los métodos", unit: "%", family: "Materia orgánica y biomarcadores", test: (s) => s.unit === "%" && canonicalParameterName(s) === "Carbono orgánico total (TOC)" && !comparisonContext(s) },
  { id: "caco3_pct", label: "Carbonato cálcico (CaCO3) · todos los métodos", unit: "%", family: "Sedimentología", test: (s, t) => s.unit === "%" && canonicalParameterName(s) === "Calcium carbonate" && !comparisonContext(s) && !/accumulation|flux|free/.test(t) },
];
export const aggregateKey = (a) => JSON.stringify(["agg", a.id, a.unit]);
export const isAggregateKey = (k) => typeof k === "string" && k.startsWith('["agg"');
/* Same PANGAEA parameter (controlled vocabulary) and same unit, any method: the
 * parameter defines the measured quantity; methods remain per series. */
const paramName = canonicalParameterName;
// The known UK′37 archive labels all describe the same dimensionless index.
const comparisonUnit = (s) => paramName(s) === UK37_PRIME && ["índice", "adimensional", "sin unidad"].includes(s.unit)
  ? "adimensional" : s.unit;
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
  if (/^(?:(?:ln|log|log10)-)?[A-Z][a-z]?\/[A-Z][a-z]? ratio$/.test(paramName(s) || "")) {
    const basis = fold([s.method, s.parameter_comment, s.source_column, s.original_unit].filter(Boolean).join(" "));
    if (/molar|mol\/mol|mmol\/mol|umol\/mol|atomic/.test(basis)) return "ratio_molar";
    if (/mass ratio|weight ratio|razon masica|concentration ratio/.test(basis)) return "ratio_mass";
    if (/scanner|xrf ratio|cps|counts|itrax|avaatech/.test(basis)) return "ratio_scanner:" + fold(s.method || "instrument unspecified");
    return "ratio_basis_unspecified";
  }
  return null;
}
const contextLabel = (context) => ({ pollen_sum_excludes_pinus:"suma sin Pinus", grain_fraction_noncarbonate:"fracción no carbonatada", grain_fraction_total:"fracción total", sortable_silt_percent_pelagics:"sedimento pelágico", sortable_silt_percent_contourites:"contornitas", matrix_pore_fluid:"fluido intersticial", matrix_soluble_salt:"sales solubles", ratio_molar:"razón molar", ratio_mass:"razón másica", ratio_basis_unspecified:"base de la razón no declarada" }[context]
  || (context?.startsWith("ratio_scanner:") ? "señal de escáner · " + context.slice("ratio_scanner:".length) : "contexto específico"));
export const paramKey = (s) =>
  paramName(s) && !s.derivation && !(s.unit === "#" && /polen|pollen/i.test(s.family || "")) &&
    !(s.unit === "%" && proxyFamily(s) === "Polen" && !comparisonContext(s))
    ? JSON.stringify(["agg", "p:" + fold(paramName(s)), comparisonUnit(s), ...(comparisonContext(s) ? [comparisonContext(s)] : [])]) : null;
export function aggregatesOf(s) {
  if (s.derivation) return [];
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
  const signature = (series) => JSON.stringify(series.map((s) => s.id).sort());
  const annualSst = new Set(out.find((g) => g.id === "agg:sst_annual")?.series.map((s) => s.id));
  const seen = new Set(out.map((g) => signature(g.series))),
    byParam = new Map();
  for (const g of groups)
    for (const s of g.series) {
      const k = paramKey(s);
      if (!k) continue;
      if (!byParam.has(k)) byParam.set(k, { name: paramName(s), unit: comparisonUnit(s), family: g.family, context: comparisonContext(s), members: new Map() });
      byParam.get(k).members.set(g.key, g);
    }
  for (const [key, a] of byParam) {
    const members = [...a.members.values()];
    if (members.length < 2) continue;
    const series = members.flatMap((g) => g.series.filter((s) => paramKey(s) === key));
    // Native annual SST is already represented by the annual card, including legacy aliases.
    if (a.name === "Sea surface temperature, annual mean" && !a.context
        && series.every((s) => annualSst.has(s.id))) continue;
    const selection = signature(series);
    if (seen.has(selection)) continue;
    const records = new Set(series.map((s) => s.record_id)).size;
    if (records < 2) continue;
    seen.add(selection);
    out.push({
      key,
      id: "agg:" + key,
      label: (a.name === "Sea surface temperature, summer"
        ? "Temperatura superficial del mar · verano declarado en la fuente" : a.name)
        + (a.context ? " · " + contextLabel(a.context) : "") + " · todos los métodos",
      unit: a.unit,
      family: a.family,
      variable: a.name,
      method: "Agrupado por variable: " + members.length + " grupos (" + [...new Set(members.map((g) => g.method))].slice(0, 4).join("; ") + (members.length > 4 ? "…" : "") + ")",
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
