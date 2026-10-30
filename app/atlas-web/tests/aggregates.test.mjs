import test from "node:test";
import assert from "node:assert/strict";
import { proxyCatalog as proxyGroups, sortGroups, inGroup, groupKey, filterGroups, paramKey, elementRatioAlias } from "../lib/proxies.mjs";
const rec = (id) => ({ id, name: id, provider: "PANGAEA", realm: "marine", publication_year: 2010 });
const ser = (id, r, proxy, cg, unit, label, n) => ({ id, record_id: r, proxy, compatibility_group: cg, unit, label, observation_count: n, rows: [] });
const data = {
  records: ["a", "b", "c"].map(rec),
  series: [
    ser("1", "a", "alkenone_SST", "sst_alk", "°C", "SST · alquenonas", 10),
    ser("2", "b", "MgCa_SST", "sst_mgca", "°C", "SST · Mg/Ca", 5),
    ser("3", "c", "Sea_surface_temperature_summer_C", "x", "°C", "Sea surface temperature, summer", 7),
    ser("4", "c", "MAAT_GDGT", "y", "°C", "MAAT", 3),
  ],
};
test("SST aggregation joins methods in °C, excludes air temperature", () => {
  const g = proxyGroups(data);
  const all = g.find((x) => x.id === "agg:sst_all");
  assert.equal(all.members.length, 3);
  assert.equal(all.records, 3);
  assert.equal(all.count, 22);
  assert.ok(!inGroup(data.series[3], all.key));
  assert.ok(inGroup(data.series[0], groupKey(data.series[0])));
  const annual = g.find((x) => x.id === "agg:sst_annual");
  assert.equal(annual.members.length, 2);
});
test("sorting by records and values; aggregation can be hidden", () => {
  const g = proxyGroups(data);
  assert.equal(sortGroups(g, "values")[0].id, "agg:sst_all");
  assert.ok(filterGroups(g, { aggregates: false }).every((x) => !x.aggregate));
  assert.ok(filterGroups(g, { minRecords: 2 }).every((x) => x.records >= 2));
});
test("same PANGAEA parameter and unit aggregate across methods", () => {
  const d = {
    records: ["a", "b"].map(rec),
    series: [
      { ...ser("p1", "a", "Foram_g", "F_PANGAEA_a", "#/g", "Foraminifera, benthic · a", 4), parameter_name_pangaea: "Foraminifera, benthic" },
      { ...ser("p2", "b", "Foram_g", "F_PANGAEA_b", "#/g", "Foraminifera, benthic · b", 6), parameter_name_pangaea: "Foraminifera, benthic" },
    ],
  };
  const p = proxyGroups(d).find((x) => x.id.includes("p:foraminifera"));
  assert.equal(p.members.length, 2);
  assert.ok(d.series.every((s) => inGroup(s, p.key)));
});
test("fractions, pollen sums and sample counts cannot be silently pooled", () => {
  const grain = { parameter_name_pangaea:"Median, grain size, D50", unit:"µm" };
  assert.notEqual(paramKey({...grain, comparison_context_key:"grain_fraction_total"}), paramKey({...grain, comparison_context_key:"grain_fraction_noncarbonate"}));
  const pollen = { parameter_name_pangaea:"Arboreal pollen", unit:"%", family:"Polen" };
  assert.notEqual(paramKey(pollen), paramKey({...pollen, source_column:"AP [%] (excl. Pines)"}));
  assert.equal(paramKey({...pollen,unit:"#"}),null);
  const ss = {parameter_name_pangaea:"Size fraction 0.063-0.010 mm, sortable silt",unit:"%"};
  assert.notEqual(paramKey({...ss,parameter_comment:"pelagics"}),paramKey({...ss,parameter_comment:"contourites"}));
});
test("inorganic ratio search accepts symbols without changing logs", () => {
  assert.equal(elementRatioAlias("Titanium/Calcium ratio"),"Ti/Ca ratio");
  assert.equal(elementRatioAlias("ln-Zirconium/Aluminium ratio"),"ln-Zr/Al ratio");
});
