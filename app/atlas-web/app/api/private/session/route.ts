import { env } from "cloudflare:workers";
import { COOKIE, isOwner, ownerPassword, sameOrigin, sha256, token } from "../../../../lib/owner";
export const dynamic = "force-dynamic";
const DAYS = 30,
  WINDOW_MIN = 15,
  MAX_FAILURES = 5;
const json = (b: any, status = 200, headers: any = {}) =>
  Response.json(b, { status, headers: { "Cache-Control": "no-store", ...headers } });
export async function GET(request: Request) {
  return json({ configured: !!ownerPassword(), owner: await isOwner(request) });
}
/** Login. Failed attempts are rate-limited globally (single owner). */
export async function POST(request: Request) {
  if (!sameOrigin(request)) return json({ error: "Origen no permitido" }, 403);
  const db = env.DB,
    secret = ownerPassword();
  if (!db) return json({ error: "Base de datos no disponible" }, 503);
  if (!secret)
    return json({ error: "Cuenta privada sin configurar: falta el secreto ATLAS_OWNER_PASSWORD" }, 503);
  const since = new Date(Date.now() - WINDOW_MIN * 60000).toISOString();
  const fails = await db
    .prepare("SELECT count(*) n FROM atlas_private_failures WHERE at>?")
    .bind(since)
    .first<any>();
  if ((fails?.n || 0) >= MAX_FAILURES)
    return json({ error: `Demasiados intentos. Espera ${WINDOW_MIN} minutos.` }, 429);
  let password = "";
  try {
    password = String(((await request.json()) as any).password || "");
  } catch {}
  const [a, b] = await Promise.all([sha256(password), sha256(secret)]);
  let diff = a.length ^ b.length;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  if (diff || password.length < 12) {
    await db.prepare("INSERT INTO atlas_private_failures(at) VALUES(?)").bind(new Date().toISOString()).run();
    return json({ error: "Contraseña incorrecta" }, 401);
  }
  const raw = crypto.getRandomValues(new Uint8Array(32)),
    t = [...raw].map((x) => x.toString(16).padStart(2, "0")).join(""),
    now = new Date();
  await db.batch([
    db.prepare("DELETE FROM atlas_private_sessions WHERE expires_at<?").bind(now.toISOString()),
    db.prepare("DELETE FROM atlas_private_failures WHERE at<?").bind(since),
    db
      .prepare("INSERT INTO atlas_private_sessions(token_hash,created_at,expires_at) VALUES(?,?,?)")
      .bind(await sha256(t), now.toISOString(), new Date(+now + DAYS * 864e5).toISOString()),
  ]);
  return json({ owner: true }, 200, {
    "Set-Cookie": `${COOKIE}=${t}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${DAYS * 86400}`,
  });
}
/** Logout: invalidate this session only. */
export async function DELETE(request: Request) {
  if (!sameOrigin(request)) return json({ error: "Origen no permitido" }, 403);
  const t = token(request);
  if (t && env.DB)
    await env.DB.prepare("DELETE FROM atlas_private_sessions WHERE token_hash=?").bind(await sha256(t)).run();
  return json({ owner: false }, 200, {
    "Set-Cookie": `${COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0`,
  });
}
