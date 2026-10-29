import test from "node:test";
import assert from "node:assert/strict";
import { importSeries, observationBatch } from "../lib/import-plan.mjs";
const seed = {
  parent_version: "v3",
  append_series_ids: ["new"],
  series: [
    {
      id: "base",
      rows: [
        [0, 1, 1],
        [1, 2, 2],
      ],
    },
    {
      id: "new",
      rows: [
        [2, 3, 8],
        [3, 4, 9],
        [4, 5, 10],
      ],
    },
  ],
};
test("known parent imports only declared new series; fresh storage imports all", () => {
  assert.deepEqual(
    importSeries(seed, true).map((s) => s.id),
    ["new"],
  );
  assert.deepEqual(
    importSeries(seed, false).map((s) => s.id),
    ["base", "new"],
  );
  assert.deepEqual(
    importSeries({ ...seed, parent_version: null }, true).map((s) => s.id),
    ["base", "new"],
  );
  assert.throws(() =>
    importSeries({ ...seed, append_series_ids: ["absent"] }, true),
  );
  assert.throws(() =>
    importSeries({ ...seed, append_series_ids: ["new", "new"] }, true),
  );
});
test("resumed bounded batches exactly equal seed order across series boundaries", () => {
  const plan = importSeries(seed, false),
    result = [];
  let offset = 0;
  while (offset < 5) {
    const batch = observationBatch(plan, offset, 2);
    assert.equal(batch.total, 5);
    result.push(...batch.rows);
    offset += batch.rows.length;
  }
  assert.deepEqual(
    result,
    seed.series.flatMap((s) => s.rows.map((row) => ({ id: s.id, row }))),
  );
  assert.deepEqual(observationBatch(plan, 5, 2).rows, []);
  assert.throws(() => observationBatch(plan, 6));
  assert.throws(() => observationBatch(plan, -1));
  assert.equal(
    observationBatch(importSeries(seed, true), 1, 1).rows[0].row[2],
    9,
  );
});
