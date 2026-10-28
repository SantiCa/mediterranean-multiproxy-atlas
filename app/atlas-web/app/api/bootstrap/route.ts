import { env } from 'cloudflare:workers';
import seed from '../../../data/seed.json';
export const dynamic='force-dynamic';

// The only seed writes are idempotent inserts. Schema changes are migration-owned.
export async function POST(request:Request){
  if(request.headers.get('origin') && request.headers.get('origin')!==new URL(request.url).origin)
    return Response.json({error:'Origen no permitido'},{status:403});
  const db=env.DB;if(!db)return Response.json({error:'Base de datos no disponible'},{status:503});
  const ready=await db.prepare('SELECT id FROM atlas_releases WHERE id=?').bind(seed.version).first();
  if(ready)return Response.json({ready:true});
  let body:any;try{body=await request.json();}catch{return Response.json({error:'JSON inválido'},{status:400});}
  if(!body||typeof body!=='object'||Array.isArray(body))return Response.json({error:'Objeto JSON requerido'},{status:400});
  const {offset=0}=body;
  const all=seed.series.flatMap(s=>s.rows.map(row=>({s:s.id,row})));
  if(!Number.isInteger(offset)||offset<0||offset>all.length)return Response.json({error:'Offset inválido'},{status:400});
  if(offset===0){
    // Keep each request under 50 SQL statements and each statement under 100 binds.
    const statements=[];
    for(let i=0;i<seed.records.length;i+=10){const batch=seed.records.slice(i,i+10);statements.push(db.prepare(`INSERT INTO atlas_records(id,name,realm,latitude,longitude,metadata_json) VALUES ${batch.map(()=>'(?,?,?,?,?,?)').join(',')} ON CONFLICT(id) DO UPDATE SET metadata_json=excluded.metadata_json`).bind(...batch.flatMap(r=>[r.id,r.name,r.realm,r.latitude,r.longitude,JSON.stringify(r)])));}
    for(let i=0;i<seed.series.length;i+=10){const batch=seed.series.slice(i,i+10);statements.push(db.prepare(`INSERT INTO atlas_series(id,record_id,proxy,label,unit,metadata_json) VALUES ${batch.map(()=>'(?,?,?,?,?,?)').join(',')} ON CONFLICT(id) DO UPDATE SET metadata_json=excluded.metadata_json`).bind(...batch.flatMap(s=>{const {rows,...meta}=s;return[s.id,s.record_id,s.proxy,s.label,s.unit,JSON.stringify(meta)];})));}
    await db.batch(statements);
  }
  const slice=all.slice(offset,offset+320);const queries=[];
  for(let i=0;i<slice.length;i+=8){const batch=slice.slice(i,i+8);const args=batch.flatMap(({s,row})=>[`${s}:${row[2]}`,s,...row]);
    // Revision r2 fills newly added nullable provenance fields without changing values or ages.
    queries.push(db.prepare(`INSERT INTO atlas_observations(id,series_id,age_ka_bp,value,source_row,source_line,original_age,original_value,age_uncertainty_ka,value_uncertainty,depth_original) VALUES ${batch.map(()=>'(?,?,?,?,?,?,?,?,?,?,?)').join(',')} ON CONFLICT(id) DO UPDATE SET original_age=excluded.original_age,original_value=excluded.original_value,age_uncertainty_ka=excluded.age_uncertainty_ka,value_uncertainty=excluded.value_uncertainty,depth_original=excluded.depth_original`).bind(...args));}
  if(queries.length)await db.batch(queries);
  const next=offset+slice.length;
  if(next>=all.length){const count=await db.prepare(`SELECT count(*) as n FROM atlas_observations WHERE series_id IN (${seed.series.map(()=>'?').join(',')})`).bind(...seed.series.map(s=>s.id)).first<{n:number}>();
    if(count?.n!==all.length)return Response.json({error:'Importación incompleta: recuento no coincide'},{status:500});
    await db.prepare('INSERT OR IGNORE INTO atlas_releases VALUES(?,?,?)').bind(seed.version,all.length,new Date().toISOString()).run();}
  return Response.json({ready:next>=all.length,next,total:all.length});
}
