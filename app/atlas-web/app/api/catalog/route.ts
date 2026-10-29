import { env } from "cloudflare:workers";
import manifest from "../../../data/release.json";
import { pickRelease } from "../../../lib/release.mjs";
export const dynamic = "force-dynamic";
/** Metadata only; observations are fetched separately for one compatible group. */
export async function GET() {
  const db = env.DB;
  if (!db)
    return Response.json(
      { error: "Base de datos no disponible" },
      { status: 503 },
    );
  const done = await db.prepare("SELECT * FROM atlas_releases").all();
  const served = pickRelease(
    manifest,
    done.results.map((r: any) => r.id),
  );
  if (!served) return Response.json({ needsBootstrap: true });
  const release = done.results.find((r: any) => r.id === served.version);
  const [rr, ss] = await Promise.all([
    db.prepare("SELECT metadata_json FROM atlas_records ORDER BY name").all(),
    db.prepare("SELECT metadata_json FROM atlas_series ORDER BY id").all(),
  ]);
  return Response.json(
    {
      release,
      records: rr.results
        .map((r: any) => JSON.parse(r.metadata_json))
        .filter((r: any) => served.recordIds.has(r.id)),
      series: ss.results
        .map((s: any) => ({ ...JSON.parse(s.metadata_json), rows: [] }))
        .filter((s: any) => served.seriesIds.has(s.id)),
    },
    { headers: { "Cache-Control": "private, max-age=30" } },
  );
}
