import { env } from 'cloudflare:workers';
export const dynamic='force-dynamic';
export async function GET(){
  if(!env.DB)return Response.json({error:'DB unavailable'},{status:503});
  const result=await env.DB.prepare('SELECT id,doi,title,state,created_at FROM atlas_candidates ORDER BY created_at DESC LIMIT 100').all();
  return Response.json({candidates:result.results});
}
export async function POST(request:Request){
  if(request.headers.get('origin') && request.headers.get('origin')!==new URL(request.url).origin)return Response.json({error:'Origen no permitido'},{status:403});
  if(!env.DB)return Response.json({error:'DB unavailable'},{status:503});
  const body=await request.text();if(body.length>2000)return Response.json({error:'Solicitud demasiado grande'},{status:413});
  let doi:string;try{doi=String(JSON.parse(body).doi||'').trim().replace(/^https?:\/\/(?:dx\.)?doi\.org\//i,'');}catch{return Response.json({error:'JSON inválido'},{status:400});}
  if(!/^10\.\d{4,9}\/\S{1,220}$/.test(doi))return Response.json({error:'Introduce un DOI válido'},{status:400});
  try{
    // Public registries verify bibliographic identity; they do not supply curated values.
    const dataDoi=/^10\.(1594|25921)\//.test(doi);
    const response=await fetch(dataDoi?`https://api.datacite.org/dois/${encodeURIComponent(doi)}`:`https://api.crossref.org/works/${encodeURIComponent(doi)}`,{headers:{Accept:'application/json'},signal:AbortSignal.timeout(15000)});
    if(!response.ok)return Response.json({error:'El registro DOI no respondió. Verifica la fuente y vuelve a intentarlo.'},{status:422});
    const meta:any=await response.json();const title=dataDoi?meta.data?.attributes?.titles?.[0]?.title:meta.message?.title?.[0];
    if(!title)return Response.json({error:'No se encontró un título verificable'},{status:422});
    const id=crypto.randomUUID();await env.DB.prepare('INSERT OR IGNORE INTO atlas_candidates(id,doi,title,state,metadata_json,created_at) VALUES(?,?,?,?,?,?)').bind(id,doi.toLowerCase(),title,'pending_review',JSON.stringify(meta),new Date().toISOString()).run();
    return Response.json({ok:true,title,state:'pending_review'});
  }catch{return Response.json({error:'No fue posible verificar el DOI en este momento.'},{status:502});}
}
