import test from 'node:test';
import assert from 'node:assert/strict';
import {groupKey,proxyGroups,filterGroups,recordMatches} from '../lib/proxies.mjs';
import {summarize,fieldGrid} from '../lib/science.mjs';
import {timeExtent} from '../lib/timeline.mjs';
import {displayRows,extent} from '../lib/plot.mjs';
const records=[{id:'m',name:'MD1',provider:'PANGAEA',realm:'marine',publication_year:2004},{id:'l',name:'Lake',provider:'NOAA WDS',realm:'lake',publication_year:2020},{id:'u',name:'Unknown paper',provider:'PANGAEA',realm:'marine',publication_year:null}];
const series=[{id:'s1',record_id:'m',proxy:'sst',label:'SST',family:'Temperatura',variable_label:'Temperatura del mar',method:'Müller 1998',unit:'°C',compatibility_group:'muller',rows:[],observation_count:100,age_min_ka_bp:-.05,age_max_ka_bp:12},{id:'s2',record_id:'l',proxy:'sst',label:'SST',family:'Temperatura',method:'Conte 2006',unit:'°C',compatibility_group:'conte',rows:[],observation_count:50,age_min_ka_bp:1100,age_max_ka_bp:1365}];
test('metadata proxy facets separate calibrations, search diacritics and exact units',()=>{
 const groups=proxyGroups({records,series});assert.equal(groups.length,2);assert.equal(filterGroups(groups,{search:'muller'}).length,1);assert.equal(filterGroups(groups,{family:'Temperatura',unit:'°C'}).length,2);
 assert.equal(filterGroups(groups,{overlap:true,min:6,max:8})[0].count,100);
 assert.equal(proxyGroups({records,series},{realm:'continental'})[0].records,1);
 assert.equal(recordMatches(records[2],{yearMin:2000}),false);assert.equal(recordMatches(records[2],{yearMax:2025}),false);
});
test('scientific summary cannot mix calibrations sharing a proxy and unit',()=>{
 const data={records,series:series.map(s=>({...s,rows:[[6,10]]}))},f={proxy:'sst',min:6,max:8,mode:'raw',minN:1,stat:'mean',realm:'all'};
 assert.throws(()=>summarize(data,f));assert.equal(summarize(data,{...f,group:groupKey(series[0])}).length,1);
});
test('global numeric extent comes from complete metadata, independent of lazy rows',()=>{
 assert.deepEqual(timeExtent({series},121000),{min:-.05,max:121000,numericMax:1365});
});
test('dense display thinning preserves extrema and full source array',()=>{
 const rows=Array.from({length:36000},(_,i)=>({age:i,value:i===12345?90000:i===23456?-90000:i}));
 const shown=displayRows(rows,1000);assert.ok(shown.length<=1000);assert.equal(shown[0],rows[0]);assert.equal(shown.at(-1),rows.at(-1));assert.ok(shown.includes(rows[12345]));assert.ok(shown.includes(rows[23456]));assert.equal(rows.length,36000);assert.deepEqual(extent(rows.map(x=>x.value)),[-90000,90000]);
});
test('coincident records are not independent spatial neighbours: one node (median)',()=>{
 const items=[[0,0,1],[0,0,3],[1,0,2],[0,1,2],[1,1,2]].map(c=>({record:{longitude:c[0],latitude:c[1],realm:'marine'},value:c[2]}));
 const g=fieldGrid(items,1000);
 assert.equal(g.merged,1);assert.match(g.reason,/mismas coordenadas/);
 // only 4 distinct sites support each cell; the duplicated site counts once with median 2
 assert.ok(g.cells.every(c=>c.neighbors<=4));assert.ok(g.cells.every(c=>Math.abs(c.value-2)<1e-9));
});
