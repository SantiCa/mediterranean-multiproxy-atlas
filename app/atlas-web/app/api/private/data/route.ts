import { env } from "cloudflare:workers";
import { isOwner, sameOrigin } from "../../../../lib/owner";
import { buildPrivate, LIMITS } from "../../../../lib/private-data.mjs";
export const dynamic = "force-dynamic";
const json = (b: any, status = 200) =>
  new Response(typeof b === "string" ? b : JSON.stringify(b), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
/** Owner's datasets with all rows (small, private, never in public endpoints). */
export async function GET(request: Request) {
  if (!env.DB) return json({ error: "Base de datos no disponible" }, 503);
  if (!(await isOwner(request))) return json({ error: "Identifícate" }, 401);
  const rows = (await env.DB.prepare(
    "SELECT id,name,filename,created_at,record_json,series_json,warnings_json FROM atlas_private_datasets ORDER BY created_at DESC",
  ).raw()) as any[][];
  // Stored JSON is concatenated, not parsed (Workers Free CPU limit).
  return json(
    '{"datasets":[' +
      rows
        .map(
          (r) =>
            '{"id":' + JSON.stringify(r[0]) + ',"name":' + JSON.stringify(r[1]) + ',"filename":' + JSON.stringify(r[2]) +
            ',"created_at":' + JSON.stringify(r[3]) + ',"record":' + r[4] + ',"series":' + r[5] + ',"warnings":' + (r[6] || "[]") + "}",
        )
        .join(",") +
      "]}",
  );
}
export async function POST(request: Request) {
  if (!sameOrigin(request)) return json({ error: "Origen no permitido" }, 403);
  const db = env.DB;
  if (!db) return json({ error: "Base de datos no disponible" }, 503);
  if (!(await isOwner(request))) return json({ error: "Identifícate" }, 401);
  const body = await request.text();
  if (body.length > LIMITS.bytes) return json({ error: "Archivo demasiado grande (máx. 1,8 MB)" }, 413);
  let input: any;
  try {
    input = JSON.parse(body);
  } catch {
    return json({ error: "JSON inválido" }, 400);
  }
  input.id = crypto.randomUUID().replace(/-/g, "").slice(0, 12);
  // Existing comparison groups are resolved from the public catalogue, so the
  // uploaded series inherit its proxy, method and unit exactly.
  const groups = new Map();
  for (const c of input.columns || []) {
    if (c?.target?.type !== "group" || groups.has(c.target.key)) continue;
    let k: any;
    try {
      k = JSON.parse(c.target.key);
    } catch {}
    if (!Array.isArray(k) || k.length !== 3) return json({ error: "Grupo inválido" }, 400);
    const m = await db
      .prepare(
        "SELECT metadata_json FROM atlas_series WHERE proxy=? AND unit=? AND coalesce(json_extract(metadata_json,'$.compatibility_group'),id)=? LIMIT 1",
      )
      .bind(String(k[0]), String(k[2]), String(k[1]))
      .first<any>();
    if (m) groups.set(c.target.key, JSON.parse(m.metadata_json));
  }
  let built: any;
  try {
    built = buildPrivate(input, groups);
  } catch (e: any) {
    return json({ error: e.message }, 422);
  }
  const series = JSON.stringify(built.series);
  if (series.length > LIMITS.bytes) return json({ error: "Demasiados datos en una subida" }, 413);
  await db
    .prepare(
      "INSERT INTO atlas_private_datasets(id,name,filename,created_at,record_json,series_json,warnings_json) VALUES(?,?,?,?,?,?,?)",
    )
    .bind(input.id, built.record.name, built.record.source_file, new Date().toISOString(), JSON.stringify(built.record), series, JSON.stringify(built.warnings))
    .run();
  return json({ ok: true, id: input.id, series: built.series.length, values: built.values, warnings: built.warnings });
}
export async function DELETE(request: Request) {
  if (!sameOrigin(request)) return json({ error: "Origen no permitido" }, 403);
  if (!env.DB) return json({ error: "Base de datos no disponible" }, 503);
  if (!(await isOwner(request))) return json({ error: "Identifícate" }, 401);
  const id = new URL(request.url).searchParams.get("id") || "";
  await env.DB.prepare("DELETE FROM atlas_private_datasets WHERE id=?").bind(id).run();
  return json({ ok: true });
}
