import { env } from 'cloudflare:workers';
import seed from '../../../data/seed.json';
export const dynamic='force-dynamic';
export async function GET(){
  const db=env.DB;if(!db)return Response.json({error:'Base de datos no disponible'},{status:503});
  const release=await db.prepare('SELECT * FROM atlas_releases WHERE id=?').bind(seed.version).first();
  if(!release)return Response.json({needsBootstrap:true},{status:200});
  const [rr,ss,oo]=await Promise.all([
    db.prepare('SELECT metadata_json FROM atlas_records ORDER BY name').all(),
    db.prepare('SELECT id,metadata_json FROM atlas_series').all(),
    db.prepare('SELECT series_id,age_ka_bp,value,source_row,source_line,original_age,original_value,age_uncertainty_ka,value_uncertainty,depth_original FROM atlas_observations ORDER BY age_ka_bp').all(),
  ]);
  const series=ss.results.map((s:any)=>({...JSON.parse(s.metadata_json),rows:[]}));const lookup=new Map(series.map(s=>[s.id,s]));
  for(const o of oo.results as any[]){const s=lookup.get(o.series_id);if(s)s.rows.push([o.age_ka_bp,o.value,o.source_row,o.source_line,o.original_age,o.original_value,o.age_uncertainty_ka,o.value_uncertainty,o.depth_original]);}
  return Response.json({release,records:rr.results.map((r:any)=>JSON.parse(r.metadata_json)),series},{headers:{'Cache-Control':'private, max-age=30'}});
}
