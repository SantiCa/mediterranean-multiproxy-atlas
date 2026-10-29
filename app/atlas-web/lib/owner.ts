import { env } from "cloudflare:workers";
/** Single-owner private area. The password is the Worker secret OWNER_PASSWORD
 * (from the GitHub secret ATLAS_OWNER_PASSWORD); sessions are random tokens whose
 * SHA-256 is stored in D1, sent as an HttpOnly, Secure, SameSite=Strict cookie. */
export const COOKIE = "medatlas_owner";
const enc = new TextEncoder();
export async function sha256(s: string) {
  const b = await crypto.subtle.digest("SHA-256", enc.encode(s));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}
export function token(request: Request) {
  const m = (request.headers.get("cookie") || "").match(
    new RegExp("(?:^|;\\s*)" + COOKIE + "=([a-f0-9]{64})"),
  );
  return m ? m[1] : null;
}
export async function isOwner(request: Request) {
  const t = token(request),
    db = env.DB;
  if (!t || !db) return false;
  const row = await db
    .prepare("SELECT expires_at FROM atlas_private_sessions WHERE token_hash=?")
    .bind(await sha256(t))
    .first<any>();
  return !!row && row.expires_at > new Date().toISOString();
}
export function sameOrigin(request: Request) {
  const o = request.headers.get("origin");
  return !o || o === new URL(request.url).origin;
}
export const ownerPassword = () =>
  (env as any).OWNER_PASSWORD as string | undefined;
