import test from "node:test";
import assert from "node:assert/strict";
import { applyQc } from "../lib/qc-corrections.mjs";

const seed = { version: "v", series: [
  { id: "a", dataset_doi: "D", rows: [[-1.5, 5, 1, 1, "-1.50", "5", null, null, null], [0.5, 6, 2, 2, "0.50", "6", null, null, null]] },
  { id: "b", dataset_doi: "X", rows: [[1, 2, 1, 1, "1", "2", null, null, null]] },
  { id: "c", dataset_doi: "X", rows: [[1, 2, 1, 1, "1", "2", null, null, null]] },
] };
const qc = { age_corrections: [{ dataset_doi: "D", transform: "ka_bp = 1.95 - ka_ce", reason: "r" }], holds: [{ id: "c", duplicate_of: "b" }] };

test("age correction keeps originals, holds drop duplicates, idempotent", () => {
  const { seed: s, qc: q } = applyQc(seed, qc);
  assert.deepEqual(s.series.map((x) => x.id), ["a", "b"]);
  assert.deepEqual(s.series[0].rows.map((r) => [r[0], r[4]]), [[3.45, "-1.50"], [1.45, "0.50"]]);
  assert.equal(s.series[0].age_min_ka_bp, 1.45);
  assert.equal(q.age_corrected_series, 1);
  assert.equal(applyQc(s, { age_corrections: qc.age_corrections }).qc.age_corrected_series, 0);
});
test("holds must reference existing series", () => {
  assert.throws(() => applyQc(seed, { holds: [{ id: "zz" }] }), /inexistente/);
});
