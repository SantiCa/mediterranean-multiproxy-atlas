/** Inspect controlled aliases against the real catalogue without rewriting data. */
import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import {readFileSync, writeFileSync} from "node:fs";
import {canonicalParameterName, comparisonContext, proxyCatalog, groupKey} from "../app/atlas-web/lib/proxies.mjs";

const [input = "data/processed/atlas-v20.json", output = "reports/group_aliases_v20.json"] = process.argv.slice(2);
const raw = readFileSync(input, "utf8"), data = JSON.parse(raw);
const fingerprint = () => createHash("sha256").update(JSON.stringify(data)).digest("hex");
const before = fingerprint();
const catalog = proxyCatalog(data), aliases = new Map();
for (const s of data.series) {
  const name = canonicalParameterName(s);
  if (name !== "Carbono orgánico total (TOC)" && name !== "Calcium carbonate" && !/^[\w-]+\/[\w]+ ratio$/.test(name || "")) continue;
  const context = comparisonContext(s), key = JSON.stringify([name, s.unit, context]);
  if (!aliases.has(key)) aliases.set(key, {name, unit:s.unit, context, native_names:new Set(), records:new Set(), groups:new Set(), series:0, values:0});
  const a = aliases.get(key);
  a.native_names.add(s.comparison_parameter_name || s.parameter_name_pangaea || s.proxy);
  a.records.add(s.record_id);
  a.groups.add(groupKey(s));
  a.series++;
  a.values += s.rows.length;
}
const controlled = [...aliases.values()].map(a => ({...a, native_names:[...a.native_names].sort(), records:a.records.size, base_groups:a.groups.size, groups:undefined}));
for (const group of catalog.filter(g => g.aggregate && (g.variable === "Carbono orgánico total (TOC)" || /^[\w-]+\/[\w]+ ratio$/.test(g.variable)))) {
  assert.equal(new Set(group.series.map(s => s.unit)).size, 1, "Units cannot merge through aliases");
  assert.equal(new Set(group.series.map(comparisonContext)).size, 1, "Measurement contexts cannot merge through aliases");
  assert.equal(new Set(group.series.map(canonicalParameterName)).size, 1);
}
const toc = catalog.filter(g => g.aggregate && g.unit === "%" && g.series.every(s => canonicalParameterName(s) === "Carbono orgánico total (TOC)" && !comparisonContext(s)));
assert.equal(toc.length, 1, "One complete TOC percentage aggregate, no native-name subset duplicate");
assert.equal(toc[0].series.length, data.series.filter(s => s.unit === "%" && canonicalParameterName(s) === "Carbono orgánico total (TOC)" && !comparisonContext(s) && !s.derivation).length);
assert.equal(fingerprint(), before, "Alias discovery cannot modify native seed data");
const report = {release:data.version, checks:"passed", base_groups:catalog.filter(g => !g.aggregate).length, aggregate_groups:catalog.filter(g => g.aggregate).length, toc_percentage:{records:toc[0].records, series:toc[0].series.length, values:toc[0].count}, controlled_aliases:controlled, limits:["Canonical names are discovery aliases, not conversions or calibration equivalence", "Unknown ratio bases remain explicitly labelled; their aggregation does not establish scientific comparability"]};
writeFileSync(output, JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify({release:report.release, checks:report.checks, toc_percentage:report.toc_percentage, controlled_contexts:controlled.length}));
