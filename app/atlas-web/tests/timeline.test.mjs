import test from 'node:test';import assert from 'node:assert/strict';import {moveWindow,timeExtent} from '../lib/timeline.mjs';
test('global ages retain negative BP and are not tied to active series',()=>{assert.deepEqual(timeExtent({series:[{rows:[[-.056,1],[10,2]]},{rows:[[430,4],[null,1]]}]}),{min:-.056,max:430,numericMax:430});});
test('moving fixed window never shrinks at an edge',()=>{const d={min:-.056,max:430};assert.deepEqual(moveWindow(429,2,d),{min:428,max:430,width:2});assert.deepEqual(moveWindow(-2,2,d),{min:-.056,max:1.944,width:2});assert.throws(()=>moveWindow(1,0,d));});
test('reported metadata coverage can extend domain but is separate from numerical observations',()=>assert.deepEqual(timeExtent({series:[{rows:[[0,1],[430,2]]}]},1000),{min:0,max:1000,numericMax:430}));
