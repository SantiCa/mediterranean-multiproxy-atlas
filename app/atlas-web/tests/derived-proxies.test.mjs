import test from "node:test";
import assert from "node:assert/strict";
import { computeDerivedProxy, planDerivedProxy, derivationRow, isAbundance } from "../lib/derived-proxies.mjs";
import { groupKey } from "../lib/proxies.mjs";
import { summarize } from "../lib/science.mjs";

const row = (sample, value, age = sample) => [age, value, sample, sample + 10, String(age), String(value), null, null, String(sample)];
const term = (id, rows, extra = {}) => ({ id, proxy: id, label: id, record_id: "core", family: "Polen", unit: "%", method: "counting", comparison_context_key: "total_pollen", raw_sha256: "abc", chronology_status: "published", rows, ...extra });
const recipe = (extra = {}) => ({ id: "test", version: 1, label: "Asociación de prueba", operation: "sum", numerator: ["a", "b"], denominator: [], disjointConfirmed: true, allCompatible: false, ...extra });
const catalog = (series) => ({ records: [{ id: "core", name: "core", realm: "lake" }], series });

test("sum preserves native zeros, negative BP and missing ages, with input provenance", () => {
  const data = catalog([term("a", [row(1, 0, -0.1), row(2, 3, null)]), term("b", [row(1, 0, -0.1), row(2, 4, null)])]);
  const output = computeDerivedProxy(data, recipe()).series[0];
  assert.deepEqual(output.rows.map((sample) => sample.slice(0, 2)), [[-0.1, 0], [null, 7]]);
  assert.equal(output.rows[0][5], null);
  assert.equal(output.rows[0][7], null);
  assert.equal(derivationRow(output, output.rows[0])[0].row[5], "0");
  assert.equal(output.age_missing_count, 1);
  assert.equal(data.series[0].rows[0][1], 0);
  assert.equal(summarize({ ...data, series: [output] }, { proxy: output.proxy, group: groupKey(output), min: -1, max: 1, mode: "raw", stat: "mean", minN: 1 })[0].value, 0);
});
test("sample joins require full native identity and matching age/depth; never age-only", () => {
  const data = catalog([term("a", [row(1, 10, 6), row(2, 10, 6), row(4, 10)]), term("b", [row(1, 20, 6), row(3, 20, 6), row(4, 20, 9)])]);
  const output = computeDerivedProxy(data, recipe()).series[0];
  assert.equal(output.rows.length, 1);
  assert.equal(output.derivation.exclusions.length, 3);
  assert.ok(output.derivation.exclusions.some((sample) => sample.reason === "age_depth_or_uncertainty_mismatch"));
});
test("ratios exclude zero denominator and shares use A/(A+B), retaining zero numerator", () => {
  const data = catalog([term("a", [row(1, 0), row(2, 20), row(3, 20)]), term("b", [row(1, 5), row(2, 0), row(3, 30)])]);
  const args = { numerator: ["a"], denominator: ["b"] };
  const ratio = computeDerivedProxy(data, recipe({ ...args, operation: "ratio" })).series[0];
  assert.deepEqual(ratio.rows.map((sample) => sample[1]), [0, 20 / 30]);
  assert.equal(ratio.derivation.exclusions[0].reason, "zero_denominator");
  const share = computeDerivedProxy(data, recipe({ ...args, operation: "share" })).series[0];
  assert.deepEqual(share.rows.map((sample) => sample[1]), [0, 100, 40]);
  assert.throws(() => planDerivedProxy(data, recipe({ operation: "share", numerator: ["a"], denominator: ["a"] })), /compartidos/);
});
test("units, denominators, tables, chronology and overlapping taxonomy are guarded", () => {
  for (const extra of [{ unit: "#" }, { raw_sha256: "other" }, { record_id: "other" }, { source_table_id: "other" }, { comparison_context_key: "no_pinus" }, { chronology_status: "other" }, { method: "other" }, { proxy: "a" }]) {
    const data = catalog([term("a", [row(1, 10)]), term("b", [row(1, 20)], extra)]);
    assert.throws(() => planDerivedProxy(data, recipe()));
  }
  assert.equal(isAbundance(term("x", [], { comparison_context_key: null })), false);
  assert.equal(isAbundance(term("x", [], { unit: "mmol/mol" })), false);
  assert.throws(() => planDerivedProxy(catalog([]), recipe({ disjointConfirmed: false })), /solapan/);
});
test("duplicate sample locators are excluded instead of overwritten; excessive percentages fail", () => {
  const data = catalog([term("a", [row(1, 10), row(1, 15), row(2, 80), row(3, 10)]), term("b", [row(1, 20), row(2, 50), row(3, 20)])]);
  const output = computeDerivedProxy(data, recipe()).series[0];
  assert.deepEqual(output.rows.map((sample) => sample[1]), [30]);
  assert.deepEqual(output.derivation.exclusions.map((sample) => sample.reason), ["missing_or_ambiguous_sample", "overlapping_or_inconsistent_percent_sum"]);
});
test("compatible multi-core plans require each taxon exactly once and preserve context", () => {
  const data = catalog([term("a", [row(1, 10)]), term("b", [row(1, 20)]), term("a2", [row(1, 15)], { proxy: "a", record_id: "core2", raw_sha256: "def" }), term("b2", [row(1, 30)], { proxy: "b", record_id: "core2", raw_sha256: "def" })]);
  const output = computeDerivedProxy(data, recipe({ allCompatible: true }));
  assert.equal(output.series.length, 2);
  assert.equal(groupKey(output.series[0]), groupKey(output.series[1]));
  data.series.push({ ...data.series[3], id: "ambiguous" });
  assert.equal(planDerivedProxy(data, recipe({ allCompatible: true })).length, 1);
});
