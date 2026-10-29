import { env } from "cloudflare:workers";
import manifest from "../../../data/release.json";
import { pickRelease } from "../../../lib/release.mjs";
export const dynamic = "force-dynamic";
// Workers Free allows ~10 ms CPU per request: the catalog (700+ series) is built by
// string concatenation of stored JSON, never parsed, and kept per isolate and release.
let cache: { version: string; body: string } | null = null;
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
  if (cache?.version !== served.version) {
    const release = done.results.find((r: any) => r.id === served.version);
    const [rr, ss] = await Promise.all([
      db
        .prepare("SELECT id,metadata_json FROM atlas_records ORDER BY name")
        .raw(),
      db.prepare("SELECT id,metadata_json FROM atlas_series ORDER BY id").raw(),
    ]);
    const records = (rr as any[][])
      .filter((r) => served.recordIds.has(r[0]))
      .map((r) => r[1]);
    // Stored series metadata excludes rows; append the empty array without parsing.
    const series = (ss as any[][])
      .filter((s) => served.seriesIds.has(s[0]))
      .map((s) => String(s[1]).replace(/\}\s*$/, ',"rows":[]}'));
    cache = {
      version: served.version,
      body:
        '{"release":' +
        JSON.stringify(release) +
        ',"records":[' +
        records.join(",") +
        '],"series":[' +
        series.join(",") +
        "]}",
    };
  }
  return new Response(cache!.body, {
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "private, max-age=30",
    },
  });
}
