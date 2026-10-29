import test from "node:test";
import assert from "node:assert/strict";
import { prepareInventory, queryInventory } from "../lib/inventory-local.mjs";
const seed = {
  version: "inv-1", counts: {}, campaigns: [{ id: "c1", name: "Leg 161", provider: "ODP" }],
  records: [
    { id: "b", name: "Beta", provider: "NOAA", realm: "marine", record_type: "core", source_id: "X-2", latitude: 36, longitude: 2, campaigns: [{ id: "c1", name: "Leg 161" }] },
    { id: "a", name: "alpha", provider: "PANGAEA", realm: "lake", source_id: "Y", latitude: null, longitude: null, campaigns: [] },
    { id: "d", name: "Data", provider: "PANGAEA", realm: "marine", record_type: "dataset", source_id: "10.1594/x", campaigns: [] },
  ],
};
const inv = prepareInventory(seed, { records: [{ id: "cur", inventory_ids: ["b"] }], series: [{ observation_count: 5 }] });
test("views reproduce the former SQL semantics", () => {
  const list = queryInventory(inv, "view=list&kind=sites").body;
  assert.equal(list.total, 2);
  assert.deepEqual(list.records.map((r) => r.id), ["b", "a"]); // binary order: B < a
  assert.equal(queryInventory(inv, "view=list&kind=all&q=x-2").body.total, 1); // ASCII case-insensitive
  assert.equal(queryInventory(inv, "view=map&kind=sites").body.points.length, 1);
  assert.deepEqual(queryInventory(inv, "view=groups&kind=sites").body.groups.map((g) => [g.id, g.count]), [["c1", 1], ["unknown", 1]]);
  assert.equal(queryInventory(inv, "view=list&kind=sites&campaign=unknown").body.total, 1);
  assert.deepEqual(queryInventory(inv, "view=detail&id=b").body.curated_record_ids, ["cur"]);
  assert.equal(queryInventory(inv, "view=detail&id=zz").status, 404);
  const sum = queryInventory(inv, "").body;
  assert.equal(sum.quantitative.observations, 5);
  assert.equal(sum.campaigns[0].count, 1);
  assert.match(queryInventory(inv, "view=export&kind=all").csv, /^﻿"id"/);
});
