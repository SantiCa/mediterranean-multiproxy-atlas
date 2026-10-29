import { env } from "cloudflare:workers";
import seed from "../../../data/seed.json";
export const dynamic = "force-dynamic";
/** Metadata only; observations are fetched separately for one compatible group. */
export async function GET() {
  const db = env.DB;
  if (!db)
    return Response.json(
      { error: "Base de datos no disponible" },
      { status: 503 },
    );
  const release = await db
    .prepare("SELECT * FROM atlas_releases WHERE id=?")
    .bind(seed.version)
    .first();
  if (!release) return Response.json({ needsBootstrap: true });
  const [rr, ss] = await Promise.all([
    db.prepare("SELECT metadata_json FROM atlas_records ORDER BY name").all(),
    db.prepare("SELECT metadata_json FROM atlas_series ORDER BY id").all(),
  ]);
  return Response.json(
    {
      release,
      records: rr.results.map((r: any) => JSON.parse(r.metadata_json)),
      series: ss.results.map((s: any) => ({
        ...JSON.parse(s.metadata_json),
        rows: [],
      })),
    },
    { headers: { "Cache-Control": "private, max-age=30" } },
  );
}
