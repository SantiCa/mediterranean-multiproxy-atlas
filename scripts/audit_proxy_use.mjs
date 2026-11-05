import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { proxyCatalog, proxyGroups, proxyFamily, groupKey, fold, aggregatesOf } from "../app/atlas-web/lib/proxies.mjs";
import { isAbundance, abundanceTable } from "../app/atlas-web/lib/derived-proxies.mjs";
import { applyQc } from "../app/atlas-web/lib/qc-corrections.mjs";

const [seedPath = "data/processed/atlas-v17.json", output = "reports/proxy_use_audit.json"] = process.argv.slice(2);
const raw = readFileSync(seedPath), data = JSON.parse(raw);
const records = new Map(data.records.map((record) => [record.id, record]));
const groups = proxyGroups(data), catalog = proxyCatalog(data);
const errors = [], warnings = [], fingerprints = new Map();
const totals = { records: data.records.length, series: data.series.length, values: 0, missing_age: 0, negative_bp: 0, observed_zero: 0, percent_out_of_range: 0 };
if (records.size !== data.records.length) errors.push({ kind: "duplicate_record_id" });
if (new Set(data.series.map((series) => series.id)).size !== data.series.length) errors.push({ kind: "duplicate_series_id" });
const familyCorrections = [], sampleIssues = [];
for (const series of data.series) {
  const record = records.get(series.record_id);
  if (!record) errors.push({ kind: "orphan_series", series: series.id });
  if (!(series.raw_sha256 || record?.raw_sha256) || !(series.source_url || record?.source_url)) errors.push({ kind: "missing_provenance", series: series.id });
  if (proxyFamily(series) !== series.family) familyCorrections.push({ series: series.id, original: series.family, displayed: proxyFamily(series) });
  let noAge = 0, invalidPercent = 0, invalidValues = 0;
  const ages = [], samples = new Set();
  let repeatedLocators = 0;
  for (const row of series.rows) {
    totals.values++;
    if (!Number.isFinite(row[1])) invalidValues++;
    if (row[0] === null) { totals.missing_age++; noAge++; }
    else if (!Number.isFinite(row[0])) errors.push({ kind: "invalid_age", series: series.id, row: row[2] });
    else { ages.push(row[0]); if (row[0] < 0) totals.negative_bp++; }
    if (row[1] === 0) totals.observed_zero++;
    if (series.unit === "%" && (row[1] < 0 || row[1] > 100)) { totals.percent_out_of_range++; invalidPercent++; }
    const sample = JSON.stringify([row[2], row[3]]);
    if (samples.has(sample)) repeatedLocators++;
    samples.add(sample);
  }
  if (invalidValues) errors.push({ kind: "nonfinite_value", series: series.id, count: invalidValues });
  if (series.observation_count !== series.rows.length || series.age_missing_count !== noAge ||
      (ages.length && (series.age_min_ka_bp !== Math.min(...ages) || series.age_max_ka_bp !== Math.max(...ages))))
    errors.push({ kind: "metadata_counts_or_extent", series: series.id });
  if (invalidPercent || repeatedLocators) sampleIssues.push({ series: series.id, invalid_percent: invalidPercent, repeated_locators: repeatedLocators });
  if (series.rows.length >= 10) {
    const key = JSON.stringify([series.proxy, series.unit, createHash("sha256").update(JSON.stringify(series.rows.map((row) => [row[0], row[1], row[8]]).sort((left, right) => JSON.stringify(left).localeCompare(JSON.stringify(right))))).digest("hex")]);
    if (!fingerprints.has(key)) fingerprints.set(key, []);
    fingerprints.get(key).push(series.id);
  }
}
const duplicateCandidates = [...fingerprints.values()].filter((ids) => ids.length > 1);
const colocated = new Map();
for (const record of data.records) {
  if (![record.longitude, record.latitude].every(Number.isFinite) || Math.abs(record.longitude) > 180 || Math.abs(record.latitude) > 90) { errors.push({ kind: "invalid_coordinates", record: record.id }); continue; }
  const key = [record.longitude.toFixed(4), record.latitude.toFixed(4)].join(",");
  if (!colocated.has(key)) colocated.set(key, []);
  colocated.get(key).push(record.id);
}
const coverageRules = [
  ["Temperatura marina", /sst|sea.surface.temperature|temperatura superficial del mar/],
  ["Isótopos estables", /d18o|d13c|18o|13c/],
  ["Censos y asociaciones de foraminíferos", /foraminifer|globiger|globorotal|neoglobo|orbulina|quinqueloba/],
  ["Vegetación: taxones, AP/NAP y asociaciones", /pollen|polen|pinus|quercus/],
  ["Oxigenación y microhábitats bentónicos", /oxygen|oxigen|epifaun|infaun|redox/],
  ["Materia orgánica y productividad", /toc|carbon.organic|corg|biogenic|alkenone|ladderane/],
  ["Aporte detrítico y razones elementales", /titanium|aluminium|ti.ca|fe.al|zr.al|detriti/],
  ["Corrientes y tamaño de grano", /sortable.silt|grain.size|current|corriente/],
  ["Nanofósiles y diatomeas", /coccolith|nannofossil|nanofosil|diatom/],
  ["Bioturbación e icnofábrica", /bioturb|ichnofabric|ichnofossil/],
];
const coverage = coverageRules.map(([use, rule]) => {
  const series = data.series.filter((term) => use.startsWith("Vegetación") ? proxyFamily(term) === "Polen" :
    use.startsWith("Censos") ? proxyFamily(term) === "Foraminíferos" :
    use.startsWith("Oxigenación") && proxyFamily(term) === "Materia orgánica y biomarcadores" ? false :
    rule.test(fold([term.proxy, term.label, term.parameter_name_pangaea, term.search_aliases].flat().join(" "))));
  return { use, records: new Set(series.map((term) => term.record_id)).size, series: series.length, values: series.reduce((count, term) => count + term.rows.length, 0), example_series: series.slice(0, 4).map((term) => term.id), status: series.length ? "numeric_available_keyword_screen_not_environmental_validation" : "no_numeric_series_detected_by_rule", rule: rule.source };
});
const abundance = data.series.filter(isAbundance);
for (const group of groups) {
  if (new Set(group.series.map((term) => proxyFamily(term))).size > 1) warnings.push({ kind: "mixed_display_family_in_base_group", group: group.key });
  if (group.series.some((term) => groupKey(term) !== group.key)) errors.push({ kind: "invalid_base_membership", group: group.key });
}
const unidentifiedSeason = data.series.filter((term) => aggregatesOf(term).some((key) => key.includes('"sst_unspecified"'))).map((term) => term.id);
const usage = applyQc(data, JSON.parse(readFileSync("config/qc_corrections.json", "utf8")));
const report = {
  schema_version: 1, seed: seedPath, release: data.version, seed_sha256: createHash("sha256").update(raw).digest("hex"),
  scope: "Offline structural and scientific-use audit of every numeric cell and catalog group; no fresh calibration, provider verification or exhaustive physical-identity audit.",
  totals, errors, warnings, sample_issues: sampleIssues,
  usage_after_qc: { records: usage.seed.records.length, series: usage.seed.series.length,
    values: usage.seed.series.reduce((count, term) => count + term.rows.length, 0),
    base_groups: proxyGroups(usage.seed).length, qc: usage.qc },
  catalog: { base_groups: groups.length, aggregate_groups: catalog.length - groups.length, single_record_groups: catalog.filter((group) => group.records === 1).length, displayed_families: [...new Set(groups.map((group) => group.family))].sort(), family_corrections: familyCorrections, sst_season_not_declared: unidentifiedSeason },
  coverage, derivable: { series: abundance.length, records: new Set(abundance.map((term) => term.record_id)).size, source_tables: new Set(abundance.map(abundanceTable)).size },
  duplicate_vector_candidates: duplicateCandidates,
  colocated_record_candidates: [...colocated].filter(([, ids]) => ids.length > 1).map(([coordinates, ids]) => ({ coordinates, records: ids })),
  limits: ["Coverage categories overlap and are search aids, not validated environmental reconstructions.", "Unknown ages remain available by depth and are excluded from age maps.", "Matching vectors or coordinates flag review candidates; they do not prove duplicate physical cores.", "Partial duplicates, original table re-extraction and chronology independence are not exhaustively certified.", "Displayed family corrections preserve archived metadata; Sites production remains on its last deployment."],
};
writeFileSync(output, JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify({ release: report.release, totals, catalog: { base: groups.length, aggregate: report.catalog.aggregate_groups, single_record: report.catalog.single_record_groups }, errors: errors.length, warnings: warnings.length, sample_issues: sampleIssues.length, duplicate_vectors: duplicateCandidates.length, derivable: report.derivable, output }, null, 2));
if (errors.length) process.exitCode = 1;
