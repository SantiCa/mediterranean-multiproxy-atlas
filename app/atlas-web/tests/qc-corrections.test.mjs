import test from "node:test";
import assert from "node:assert/strict";
import { applyQc } from "../lib/qc-corrections.mjs";
import { rowQcNote } from "../lib/provenance.mjs";
import { fieldGrid, mapSiteCounts } from "../lib/science.mjs";

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

test("reviewed drilling holes retain identity and count as one spatial node", () => {
  const holes = [
    { id: "969D", longitude: 24.8833, latitude: 33.8386, realm: "marine" },
    { id: "969E", longitude: 24.8831, latitude: 33.8411, realm: "marine" },
  ];
  const source = { records: holes, series: [] };
  const settings = { spatial_sites: [{ id: "site969", record_ids: ["969D", "969E"], note: "Shared site" }] };
  const annotated = applyQc(source, settings).seed;
  assert.equal(annotated.records.length, 2);
  assert.deepEqual(annotated.records.map(({ id, longitude, latitude }) => ({ id, longitude, latitude })),
    holes.map(({ id, longitude, latitude }) => ({ id, longitude, latitude })));
  const points = annotated.records.map((record, index) => ({ record, value: index ? 0 : null }));
  assert.deepEqual(mapSiteCounts(points), { total: 1, withData: 1 });
  const third = { record: { longitude: 25, latitude: 34, realm: "marine" }, value: 3 };
  assert.equal(fieldGrid([{ ...points[0], value: 1 }, points[1], third]).cells.length, 0);
  assert.equal(holes[0].spatial_site_id, undefined);
  assert.deepEqual(applyQc(annotated, settings).seed, annotated);
});

test("published chronology and exact sample warning survive without changing any rows", () => {
  const rows = [[8.2, 10, 5, 17, "8.20", "10", null, null, "1.02"],
    [8.1, 11, 6, 18, "8.10", "11", null, null, "1.03"], [8.3, 12, 7, 19, "8.30", "12", null, null, "1.04"]];
  const source = { records: [], series: [
    { id: "ohrid", dataset_doi: "lake", raw_sha256: "lake-hash", rows },
    { id: "nile", dataset_doi: "nile", raw_sha256: "nile-hash", rows: [] },
  ] };
  const sample = { row: 6, line: 18, age_original: "8.10", depth_original: "1.03" };
  const settings = { dataset_annotations: {
    lake: { raw_sha256: "lake-hash", chronology_warning: { message: "Native inversion", samples: [sample] } },
    nile: { raw_sha256: "nile-hash", age_model: "Published calendar age model", source_url: "https://example.com/model" },
  } };
  const annotated = applyQc(source, settings).seed;
  assert.equal(annotated.series[0].rows, rows);
  assert.equal(rowQcNote(annotated.series[0], rows[1]), "Native inversion");
  assert.equal(rowQcNote(annotated.series[0], rows[2]), null);
  assert.equal(source.series[0].chronology_warning, undefined);
  assert.equal(annotated.series[1].age_model, "Published calendar age model");
  assert.equal(annotated.series[1].age_model_source_url, "https://example.com/model");
  assert.deepEqual(applyQc(annotated, settings).seed, annotated);
  assert.throws(() => applyQc(source, { dataset_annotations: { lake: { raw_sha256: "wrong" } } }), /original distinto/);
  assert.throws(() => applyQc(source, { dataset_annotations: { lake: { ...settings.dataset_annotations.lake,
    chronology_warning: { message: "Invalid", samples: [{ ...sample, depth_original: "2.00" }] },
  } } }), /localizador distinto/);
});
