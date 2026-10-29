import { env } from "cloudflare:workers";
import manifest from "../../../data/release.json";
import { pickRelease } from "../../../lib/release.mjs";
import { groupKey, seriesMatches } from "../../../lib/proxies.mjs";
export const dynamic = "force-dynamic";
const LIMIT = 150000;
/** Complete selected series, never age-trimmed: z requires a fixed reference.
 * Explicit limit fails rather than silently thinning scientific observations. */
export async function GET(request: Request) {
  const db = env.DB;
  if (!db)
    return Response.json(
      { error: "Base de datos no disponible" },
      { status: 503 },
    );
  const p = new URL(request.url).searchParams,
    group = p.get("group");
  if (!group)
    return Response.json(
      { error: "Selecciona variable, método y unidad" },
      { status: 400 },
    );
  const served = pickRelease(
    manifest,
    (await db.prepare("SELECT id FROM atlas_releases").all()).results.map(
      (r: any) => r.id,
    ),
  );
  if (!served)
    return Response.json({ error: "Importación pendiente" }, { status: 409 });
  const f = {
    provider: p.get("provider") || "all",
    realm: p.get("realm") || "all",
    yearMin: Number(p.get("yearMin")) || 0,
    yearMax: Number(p.get("yearMax")) || 0,
    chronology: p.get("chronology") || "all",
  };
  let key: any[];
  try {
    key = JSON.parse(group);
  } catch {
    key = [];
  }
  if (!Array.isArray(key) || key.length !== 3)
    return Response.json({ error: "Grupo inválido" }, { status: 400 });
  // Filter in SQL so the Worker parses only the selected series (Free CPU limit).
  const ss = await db
    .prepare(
      "SELECT metadata_json FROM atlas_series WHERE proxy=? AND unit=? AND coalesce(json_extract(metadata_json,'$.compatibility_group'),id)=?",
    )
    .bind(String(key[0]), String(key[2]), String(key[1]))
    .raw();
  const candidates = (ss as any[][])
    .map((r) => JSON.parse(r[0]))
    .filter((s: any) => served.seriesIds.has(s.id) && groupKey(s) === group);
  const ids = [...new Set(candidates.map((s: any) => s.record_id))];
  const rr = ids.length
    ? await db
        .prepare(
          "SELECT id,metadata_json FROM atlas_records WHERE id IN (" +
            ids.map(() => "?").join(",") +
            ")",
        )
        .bind(...ids)
        .raw()
    : [];
  const records = new Map(
    (rr as any[][]).map((r) => [r[0], JSON.parse(r[1])]),
  );
  const selected = candidates.filter(
    (s: any) =>
      records.has(s.record_id) &&
      seriesMatches(s, records.get(s.record_id), f),
  );
  const n = selected.reduce(
    (v: number, s: any) => v + (s.observation_count || 0),
    0,
  );
  if (n > LIMIT || selected.length > 40)
    return Response.json(
      {
        error:
          "Selección demasiado grande (máximo 150.000 valores / 40 series). Reduce fuente, archivo o año. No se han truncado datos.",
      },
      { status: 413 },
    );
  const series = [];
  for (let start = 0; start < selected.length; start += 6) {
    const batch = await Promise.all(
      selected.slice(start, start + 6).map(async (s: any) => {
        const rows = await db
          .prepare(
            "SELECT age_ka_bp,value,source_row,source_line,original_age,original_value,age_uncertainty_ka,value_uncertainty,depth_original FROM atlas_observations WHERE series_id=? ORDER BY age_ka_bp,source_row",
          )
          .bind(s.id)
          .raw();
        if (rows.length !== s.observation_count)
          throw new Error("Recuento de serie no coincide con la versión");
        return { ...s, rows };
      }),
    );
    series.push(...batch);
  }
  return Response.json(
    { version: served.version, group, count: n, series },
    { headers: { "Cache-Control": "private, max-age=60" } },
  );
}
