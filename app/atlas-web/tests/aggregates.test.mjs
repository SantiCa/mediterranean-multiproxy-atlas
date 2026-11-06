import test from "node:test";
import assert from "node:assert/strict";
import { proxyCatalog as proxyGroups, sortGroups, inGroup, groupKey, filterGroups, paramKey, elementRatioAlias, canonicalParameterName } from "../lib/proxies.mjs";
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
  const unspecified = g.find((x) => x.id === "agg:sst_unspecified");
  assert.equal(unspecified.members.length, 2);
  assert.equal(g.find((x) => x.id === "agg:sst_annual"), undefined);
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
  assert.equal(paramKey(pollen), null);
  assert.notEqual(paramKey(pollen), paramKey({...pollen, source_column:"AP [%] (excl. Pines)"}));
  assert.equal(paramKey({...pollen,unit:"#"}),null);
  const ss = {parameter_name_pangaea:"Size fraction 0.063-0.010 mm, sortable silt",unit:"%"};
  assert.notEqual(paramKey({...ss,parameter_comment:"pelagics"}),paramKey({...ss,parameter_comment:"contourites"}));
});
test("inorganic ratio search accepts symbols without changing logs", () => {
  assert.equal(elementRatioAlias("Titanium/Calcium ratio"),"Ti/Ca ratio");
  assert.equal(elementRatioAlias("ln-Zirconium/Aluminium ratio"),"ln-Zr/Al ratio");
});

test("TOC aliases give one complete aggregate and a shared variable filter", () => {
  const names = ["TOC", "total organic carbon", "Carbon, organic, total"];
  const d = { records: ["a", "b", "c"].map(rec), series: names.map((name, i) => ({
    ...ser(String(i), ["a", "b", "c"][i], name, String(i), "%", name, 5),
    parameter_name_pangaea: name,
  })) };
  const before = structuredClone(d);
  const groups = proxyGroups(d);
  const aggregates = groups.filter(g => g.aggregate);
  assert.equal(aggregates.length, 1);
  assert.equal(aggregates[0].series.length, 3);
  assert.equal(aggregates[0].records, 3);
  assert.equal(new Set(groups.filter(g => !g.aggregate).map(g => g.variable)).size, 1);
  assert.equal(filterGroups(groups, {search: "total organic carbon", aggregates: false}).length, 3);
  assert.ok(d.series.every(s => inGroup(s, aggregates[0].key)));
  assert.deepEqual(d, before, "discovery must not rewrite native metadata or values");
});

test("organic carbon names do not merge units, fractions, isotope ratios or inorganic carbon", () => {
  const toc = {parameter_name_pangaea: "TOC", unit: "%"};
  assert.equal(paramKey(toc), paramKey({...toc, parameter_name_pangaea: "Carbon, organic, total"}));
  for (const change of [
    {unit:"mg/g"}, {comparison_context_key:"organic_carbon_dissolved"},
    {parameter_name_pangaea:"Carbon, inorganic, total"},
    {parameter_name_pangaea:"Carbon, organic, total, delta13C", unit:"‰ PDB"},
    {parameter_name_pangaea:"TOC/TN"}, {parameter_name_pangaea:"Organic carbon accumulation rate"},
  ]) assert.notEqual(paramKey(toc), paramKey({...toc, ...change}));
  assert.equal(canonicalParameterName({parameter_name_pangaea:"CaCO3"}), "Calcium carbonate");
  assert.notEqual(paramKey({parameter_name_pangaea:"TIC", unit:"%"}), paramKey({parameter_name_pangaea:"CaCO3", unit:"%"}));
});

test("element ratio aliases unify only the same ratio and measurement basis", () => {
  const ratio = {parameter_name_pangaea:"Titanium/Calcium ratio", unit:"sin unidad", method:"X-ray fluorescence core scanner (XRF)"};
  assert.equal(paramKey(ratio), paramKey({...ratio,parameter_name_pangaea:"Ti/Ca"}));
  for (const change of [
    {parameter_name_pangaea:"ln-Ti/Ca ratio"}, {parameter_name_pangaea:"log10(Ti/Ca)"},
    {parameter_name_pangaea:"Ti/Al"}, {method:"molar ratio"}, {method:"mass ratio"},
    {method:"not documented"}, {method:"ITRAX scanner"}, {unit:"mmol/mol"},
  ]) assert.notEqual(paramKey(ratio), paramKey({...ratio, ...change}));
  assert.equal(canonicalParameterName({parameter_name_pangaea:"Iron/Calcium ratio"}), "Fe/Ca ratio");
  assert.equal(canonicalParameterName({parameter_name_pangaea:"ln(Titanium/Calcium)"}), "ln-Ti/Ca ratio");
});
