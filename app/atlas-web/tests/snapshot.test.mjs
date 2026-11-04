import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, mkdirSync, existsSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

test('stale child release cannot erase or publish a previously checked snapshot',()=>{
  const root=mkdtempSync(join(tmpdir(),'medatlas-snapshot-'));
  try {
    const seed=join(root,'atlas-v6.json'),out=join(root,'snapshot');
    mkdirSync(out);writeFileSync(join(out,'checked.txt'),'previous checked snapshot');
    writeFileSync(join(root,'atlas-v5.json'),JSON.stringify({version:'atlas-quantitative-v5-new'}));
    writeFileSync(seed,JSON.stringify({version:'atlas-quantitative-v6-old',parent_version:'atlas-quantitative-v5-old',records:[],series:[]}));
    const script=resolve(dirname(fileURLToPath(import.meta.url)),'../scripts/snapshot.mjs');
    const result=spawnSync(process.execPath,[script,seed,out],{encoding:'utf8'});
    assert.notEqual(result.status,0);
    assert.match(result.stderr,/Release padre modificada/);
    assert.ok(existsSync(join(out,'checked.txt')));
  } finally {
    assert.equal(dirname(resolve(root)),resolve(tmpdir()));
    rmSync(root,{recursive:true,force:true});
  }
});
