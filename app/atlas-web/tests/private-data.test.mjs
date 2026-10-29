import test from "node:test";
import assert from "node:assert/strict";
import { parseTable, num, buildPrivate, interpolate, modelPoints } from "../lib/private-data.mjs";
const group = { proxy: "alkenone_SST", compatibility_group: "sst_alkenone_mueller1998_annual", unit: "°C", family: "Temperatura", method: "UK'37", variable_label: "SST" };
const key = JSON.stringify([group.proxy, group.compatibility_group, group.unit]);
const base = (over = {}) => ({
  id: "abc123",
  filename: "x.csv",
  record: { name: "MiSondeo", latitude: "36.5", longitude: "-2.1", realm: "marine" },
  table: parseTable("Depth [m];Age [ka BP];SST [°C];TOC [%]\n0,1;1,0;18,5;0,8\n0,2;2,0;<1;1,2\n0,3;3,0;17,0;\n"),
  depthColumn: 0,
  ageColumn: 1,
  ageUnit: "ka BP",
  columns: [{ index: 2, target: { type: "group", key } }],
  ...over,
});
test("parses ; CSV with decimal comma and keeps censored cells out", () => {
  const out = buildPrivate(base(), new Map([[key, group]]));
  const s = out.series[0];
  assert.equal(s.proxy, group.proxy);
  assert.equal(s.compatibility_group, group.compatibility_group);
  assert.equal(s.unit, "°C");
  assert.deepEqual(s.rows.map((r) => [r[0], r[1]]), [[1, 18.5], [3, 17]]);
  assert.ok(out.warnings.some((w) => w.includes("censuradas")));
  assert.equal(out.record.provider, "Privado");
});
test("rejects a unit different from the group", () => {
  const t = parseTable("Age [ka BP]\tSST [K]\n1\t290\n");
  assert.throws(() => buildPrivate(base({ table: t, depthColumn: -1, ageColumn: 0, columns: [{ index: 1, target: { type: "group", key } }] }), new Map([[key, group]])), /unidad/);
});
test("age model interpolates in depth, never extrapolates", () => {
  const out = buildPrivate(base({ ageColumn: -1, ageModel: { unit: "ka BP", pairs: [[0.15, 1.5], [0.3, 3]] } }), new Map([[key, group]]));
  assert.deepEqual(out.series[0].rows.map((r) => r[0]), [3, null]);
  assert.equal(out.series[0].chronology_status, "private_interpolated_age_model");
  assert.throws(() => modelPoints([[1, 5], [2, 1]]), /inversión/);
  assert.equal(interpolate(modelPoints([[0, 0], [2, 10]]), 1), 5);
});
test("new private proxy never joins public groups; radiocarbon refused", () => {
  const out = buildPrivate(base({ columns: [{ index: 3, target: { type: "new", label: "TOC", unit: "%", method: "LECO" } }] }), new Map());
  assert.match(out.series[0].compatibility_group, /^private_/);
  const t = parseTable("Age 14C [ka]\tX\n1\t2\n");
  assert.throws(() => buildPrivate(base({ table: t, depthColumn: -1, ageColumn: 0, columns: [{ index: 1, target: { type: "new", label: "X", unit: "u" } }] }), new Map()), /radiocarbono/);
  assert.equal(num("1,5", true), 1.5);
  assert.equal(num("1,5", false), null);
});
