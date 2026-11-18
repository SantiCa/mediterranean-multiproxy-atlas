import { env } from "cloudflare:workers";
import { getChatGPTUser } from "../../chatgpt-auth";

export const dynamic = "force-dynamic";

function json(body: object, status = 200) {
  return Response.json(body, { status, headers: { "Cache-Control": "private, no-store" } });
}

export async function GET() {
  if (!(await getChatGPTUser())) return json({ error: "Identifícate en Sites." }, 401);
  if (!env.DB) return json({ error: "Base de datos no disponible." }, 503);
  const result = await env.DB.prepare(
    "SELECT id,doi,title,state,created_at FROM atlas_candidates ORDER BY created_at DESC LIMIT 100",
  ).all();
  return json({ candidates: result.results });
}

export async function POST(request: Request) {
  if (!(await getChatGPTUser())) return json({ error: "Identifícate en Sites." }, 401);
  if (request.headers.get("origin") !== new URL(request.url).origin)
    return json({ error: "Origen no permitido." }, 403);
  const db = env.DB;
  if (!db) return json({ error: "Base de datos no disponible." }, 503);

  if (Number(request.headers.get("content-length")) > 2000)
    return json({ error: "Solicitud demasiado grande." }, 413);
  const body = await request.text();
  if (body.length > 2000) return json({ error: "Solicitud demasiado grande." }, 413);
  let doi: string;
  try {
    const payload = JSON.parse(body);
    doi = typeof payload?.doi === "string"
      ? payload.doi.trim().replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, "")
      : "";
  } catch {
    return json({ error: "JSON inválido." }, 400);
  }
  if (!/^10\.\d{4,9}\/\S{1,220}$/.test(doi))
    return json({ error: "Introduce un DOI válido." }, 400);

  try {
    const normalized = doi.toLowerCase();
    const existing = await db.prepare("SELECT title,state FROM atlas_candidates WHERE doi=?")
      .bind(normalized).first<{ title: string; state: string }>();
    if (existing) return json({ ok: true, ...existing });

    const fromDataCite = /^10\.(1594|25921)\//.test(doi);
    const registry = fromDataCite ? "https://api.datacite.org/dois/" : "https://api.crossref.org/works/";
    const response = await fetch(registry + encodeURIComponent(doi), {
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(15000),
    });
    if (!response.ok)
      return json({ error: "El registro DOI no respondió. Verifica la fuente y vuelve a intentarlo." }, 422);
    const metadata = await response.json() as {
      data?: { attributes?: { titles?: { title?: string }[] } };
      message?: { title?: string[] };
    };
    const title = fromDataCite ? metadata.data?.attributes?.titles?.[0]?.title : metadata.message?.title?.[0];
    if (!title) return json({ error: "No se encontró un título verificable." }, 422);
    const state = "pending_review";
    await db.prepare(
      "INSERT OR IGNORE INTO atlas_candidates(id,doi,title,state,metadata_json,created_at) VALUES(?,?,?,?,?,?)",
    ).bind(crypto.randomUUID(), normalized, title, state, JSON.stringify(metadata), new Date().toISOString()).run();
    return json({ ok: true, title, state });
  } catch {
    return json({ error: "No fue posible verificar el DOI en este momento." }, 502);
  }
}
