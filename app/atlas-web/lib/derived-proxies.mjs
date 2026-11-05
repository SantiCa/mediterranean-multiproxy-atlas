import { comparisonContext, proxyFamily, groupKey } from "./proxies.mjs";

export const DERIVED_VERSION = 1;
const finite = (value) => typeof value === "number" && Number.isFinite(value);
const parameter = (series) => series.comparison_parameter_name || series.parameter_name_pangaea || series.taxon || series.proxy;

/** Abundances only; percentages need an explicit common denominator context. */
export function isAbundance(series) {
  return !series.derivation && ["Polen", "Foraminíferos", "Micropaleontología", "Oxigenación bentónica"].includes(proxyFamily(series)) &&
    ["#", "%", "#/g"].includes(series.unit) &&
    (series.unit !== "%" || !!comparisonContext(series)) &&
    !/isotop|oxygen index|δ|ratio|coating/i.test(series.parameter_name_pangaea || series.label || "");
}

/** A source table, analytical method, fraction, denominator and chronology must agree. */
export function abundanceContext(series) {
  return JSON.stringify([series.unit, series.method || null, comparisonContext(series),
    series.depth_frame || null, series.chronology_status || null, series.age_model || null]);
}
export function abundanceTable(series) {
  return JSON.stringify([series.record_id, series.raw_sha256 || series.source_sha256 || null,
    series.source_table_id || null, abundanceContext(series)]);
}

/** Build explicit per-table plans; ambiguous or unavailable taxa never become zeros. */
export function planDerivedProxy(catalog, recipe) {
  if (recipe.version !== DERIVED_VERSION || !recipe.id || !recipe.label?.trim() || recipe.label.length > 160)
    throw new Error("Receta sin nombre, identificador o versión compatible.");
  if (!["sum", "ratio", "share"].includes(recipe.operation)) throw new Error("Operación desconocida.");
  const numerator = recipe.numerator || [], denominator = recipe.denominator || [];
  if (!numerator.length || numerator.length + denominator.length > 20 ||
      (recipe.operation === "sum" ? denominator.length : !denominator.length) ||
      new Set(numerator).size !== numerator.length || new Set(denominator).size !== denominator.length)
    throw new Error("Selecciona entre 1 y 20 términos, sin repeticiones dentro de cada suma.");
  if (recipe.operation === "share" && numerator.some((id) => denominator.includes(id)))
    throw new Error("La proporción A/(A+B) necesita conjuntos A y B sin términos compartidos.");
  if (!recipe.disjointConfirmed) throw new Error("Confirma que los taxones de cada suma no se solapan.");
  const byId = new Map(catalog.series.map((series) => [series.id, series]));
  const ids = [...new Set([...numerator, ...denominator])];
  const reference = ids.map((id) => byId.get(id));
  if (reference.some((series) => !series || !isAbundance(series))) throw new Error("Hay entradas ausentes o sin contexto de abundancia verificable.");
  if (recipe.input_hashes && reference.some((series) => recipe.input_hashes[series.id] !== (series.raw_sha256 || series.source_sha256)))
    throw new Error("Los originales han cambiado o no coinciden con los hashes de la receta.");
  if (!reference[0].raw_sha256 && !reference[0].source_sha256) throw new Error("Falta el hash de la tabla original.");
  if (new Set(reference.map(abundanceTable)).size !== 1) throw new Error("Los términos deben pertenecer a la misma tabla, sondeo, unidad, método y cronología.");
  if (new Set(reference.map(parameter)).size !== reference.length) throw new Error("Dos columnas representan el mismo taxón o grupo: revisa su identidad.");
  const tables = new Map();
  for (const series of catalog.series.filter(isAbundance)) {
    if (abundanceContext(series) !== abundanceContext(reference[0])) continue;
    if (!recipe.allCompatible && series.record_id !== reference[0].record_id) continue;
    if (!series.raw_sha256 && !series.source_sha256) continue;
    const key = abundanceTable(series);
    if (!tables.has(key)) tables.set(key, []);
    tables.get(key).push(series);
  }
  const plans = [];
  for (const table of tables.values()) {
    const matches = reference.map((term) => table.filter((series) => parameter(series) === parameter(term)));
    if (matches.some((terms) => terms.length !== 1)) continue;
    const mapped = new Map(ids.map((id, index) => [id, matches[index][0]]));
    plans.push({ numerator: numerator.map((id) => mapped.get(id)), denominator: denominator.map((id) => mapped.get(id)) });
  }
  if (!plans.length) throw new Error("No hay una tabla con todos los términos inequívocos.");
  if (plans.length > 200) throw new Error("Más de 200 tablas: reduce la selección.");
  return plans;
}

const sampleKey = (row) => Number.isInteger(row[2]) && Number.isInteger(row[3]) ? JSON.stringify([row[2], row[3]]) : null;
const sampleContext = (row) => JSON.stringify([row[0], row[4], row[6], row[8]]);

/** Complete-case arithmetic on native sample locators, never on age alone. */
export function computeDerivedProxy(catalog, recipe) {
  const plans = planDerivedProxy(catalog, recipe);
  const series = [];
  let inputCount = 0;
  for (const plan of plans) {
    const inputs = [...new Map([...plan.numerator, ...plan.denominator].map((term) => [term.id, term])).values()];
    const first = inputs[0], samples = new Set(), indexes = new Map();
    for (const term of inputs) {
      const index = new Map();
      inputCount += term.rows.length;
      if (inputCount > 200000) throw new Error("Más de 200.000 valores de entrada: reduce la selección.");
      for (const row of term.rows) {
        const key = sampleKey(row);
        if (key === null) throw new Error("Faltan localizadores nativos de muestra.");
        samples.add(key);
        index.set(key, index.has(key) ? null : row);
      }
      indexes.set(term.id, index);
    }
    const rows = [], exclusions = [];
    for (const key of samples) {
      const sourceRows = inputs.map((term) => indexes.get(term.id).get(key));
      let reason = sourceRows.some((row) => !row) ? "missing_or_ambiguous_sample" : null;
      if (!reason && new Set(sourceRows.map(sampleContext)).size !== 1) reason = "age_depth_or_uncertainty_mismatch";
      if (!reason && sourceRows.some((row) => !finite(row[1]) || row[1] < 0 || (first.unit === "%" && row[1] > 100))) reason = "invalid_abundance";
      const sum = (terms) => terms.reduce((total, term) => total + indexes.get(term.id).get(key)[1], 0);
      let value;
      if (!reason) {
        const top = sum(plan.numerator), bottom = sum(plan.denominator);
        if (first.unit === "%" && (top > 100 + 1e-8 || bottom > 100 + 1e-8 || (recipe.operation === "share" && top + bottom > 100 + 1e-8))) reason = "overlapping_or_inconsistent_percent_sum";
        else if (recipe.operation !== "sum" && (recipe.operation === "share" ? top + bottom : bottom) <= 0) reason = "zero_denominator";
        else value = recipe.operation === "sum" ? top : recipe.operation === "ratio" ? top / bottom : 100 * top / (top + bottom);
        if (!reason && !finite(value)) reason = "nonfinite_result";
      }
      if (reason) { exclusions.push({ sample: JSON.parse(key), reason }); continue; }
      const row = sourceRows[0];
      rows.push([row[0], value, row[2], row[3], row[4], null, row[6], null, row[8]]);
    }
    const ages = rows.map((row) => row[0]).filter(finite);
    const unit = recipe.operation === "sum" ? first.unit : recipe.operation === "share" ? "%" : "adimensional";
    const terms = (list) => list.map((term) => parameter(term)).join(" + ");
    const formula = recipe.operation === "sum" ? terms(plan.numerator) : recipe.operation === "ratio" ? `(${terms(plan.numerator)}) / (${terms(plan.denominator)})` : `100 × (${terms(plan.numerator)}) / ((${terms(plan.numerator)}) + (${terms(plan.denominator)}))`;
    const metadata = { ...first };
    for (const field of ["rows", "parameter_name_pangaea", "comparison_parameter_name", "taxon", "uncertainty_bounds", "value_uncertainty_source_column", "source_column_index", "original_unit", "source_variable_definition"]) delete metadata[field];
    series.push({ ...metadata, id: `derived:${recipe.id}:${first.id}`, proxy: `derived:${recipe.id}`,
      label: recipe.label.trim(), variable_label: recipe.label.trim(), family: proxyFamily(first), unit,
      compatibility_group: `derived:${recipe.id}:${abundanceContext(first)}`, method: "Cálculo de usuario sobre abundancias; " + first.method,
      evidence_type: "user_transformation", source_column: null, uncertainty_type: "not_propagated",
      observation_count: rows.length, age_missing_count: rows.length - ages.length,
      age_min_ka_bp: ages.length ? Math.min(...ages) : null, age_max_ka_bp: ages.length ? Math.max(...ages) : null,
      rows, derivation: { version: DERIVED_VERSION, recipe, formula, inputs: inputs.map((term) => ({ id: term.id, parameter: parameter(term), unit: term.unit, source_column: term.source_column, group: groupKey(term), raw_sha256: term.raw_sha256 || term.source_sha256, source_url: term.source_url })),
        exclusions, inputs_by_sample: Object.fromEntries([...samples].map((key) => [key, inputs.map((term) => ({ series_id: term.id, row: indexes.get(term.id).get(key) ?? null }))])) },
      qc_notes: [...(first.qc_notes || []), "Transformación de usuario, sin calibración ambiental ni propagación de incertidumbre; muestras incompletas excluidas, sin interpolar.", "La ausencia de solapamiento taxonómico ha sido declarada por el usuario."] });
  }
  if (!series.some((term) => term.rows.length)) throw new Error("Ninguna muestra completa permite calcular la receta.");
  return { recipe, series };
}

export function derivationRow(series, row) {
  return series.derivation?.inputs_by_sample[sampleKey(row)] || null;
}
