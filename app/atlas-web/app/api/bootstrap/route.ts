import { env } from "cloudflare:workers";
import snapshot from "../../../data/seed.json";
import { importSeries, observationBatch } from "../../../lib/import-plan.mjs";
export const dynamic = "force-dynamic";
const seed: any = snapshot;
/** Reviewed append-only release, bounded stages, migration-owned schema.
 * The assembler rejects changes to prior observation IDs/ages/values. */
export async function POST(request: Request) {
  if (
    request.headers.get("origin") &&
    request.headers.get("origin") !== new URL(request.url).origin
  )
    return Response.json({ error: "Origen no permitido" }, { status: 403 });
  const db = env.DB;
  if (!db)
    return Response.json(
      { error: "Base de datos no disponible" },
      { status: 503 },
    );
  if (
    await db
      .prepare("SELECT id FROM atlas_releases WHERE id=?")
      .bind(seed.version)
      .first()
  )
    return Response.json({ ready: true });
  let body: any;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "JSON inválido" }, { status: 400 });
  }
  if (!body || typeof body !== "object" || Array.isArray(body))
    return Response.json({ error: "Objeto JSON requerido" }, { status: 400 });
  const stages = ["records", "series", "observations"],
    stage = body.stage || "records",
    offset = body.offset ?? 0;
  if (!stages.includes(stage) || !Number.isInteger(offset) || offset < 0)
    return Response.json({ error: "Cursor inválido" }, { status: 400 });
  const parentPresent = seed.parent_version
    ? !!(await db
        .prepare("SELECT id FROM atlas_releases WHERE id=?")
        .bind(seed.parent_version)
        .first())
    : false;
  let table: string,
    columns: string,
    all: any[],
    encode: (r: any) => any[],
    conflict: string,
    observationTotal = 0;
  if (stage === "records") {
    table = "atlas_records";
    columns = "id,name,realm,latitude,longitude,metadata_json";
    all = seed.records;
    encode = (r) => [
      r.id,
      r.name,
      r.realm,
      r.latitude,
      r.longitude,
      JSON.stringify(r),
    ];
    conflict =
      "ON CONFLICT(id) DO UPDATE SET metadata_json=excluded.metadata_json";
  } else if (stage === "series") {
    table = "atlas_series";
    columns = "id,record_id,proxy,label,unit,metadata_json";
    all = seed.series;
    encode = (s) => {
      const { rows, ...meta } = s;
      return [
        s.id,
        s.record_id,
        s.proxy,
        s.label,
        s.unit,
        JSON.stringify(meta),
      ];
    };
    conflict =
      "ON CONFLICT(id) DO UPDATE SET metadata_json=excluded.metadata_json";
  } else {
    table = "atlas_observations";
    columns =
      "id,series_id,age_ka_bp,value,source_row,source_line,original_age,original_value,age_uncertainty_ka,value_uncertainty,depth_original";
    let batch: any;
    try {
      batch = observationBatch(importSeries(seed, parentPresent), offset, 240);
    } catch {
      return Response.json(
        { error: "Cursor o manifiesto de observaciones inválido" },
        { status: 400 },
      );
    }
    all = batch.rows;
    observationTotal = batch.total;
    encode = (o) => [o.id + ":" + o.row[2], o.id, ...o.row];
    conflict = "ON CONFLICT(id) DO NOTHING";
  }
  const total = stage === "observations" ? observationTotal : all.length;
  if (offset > total)
    return Response.json({ error: "Cursor fuera de rango" }, { status: 400 });
  const slice =
      stage === "observations" ? all : all.slice(offset, offset + 240),
    queries = [];
  for (let i = 0; i < slice.length; i += 8) {
    const batch = slice.slice(i, i + 8),
      args = batch.flatMap(encode),
      width = encode(batch[0]).length,
      marks = batch
        .map(() => "(" + Array(width).fill("?").join(",") + ")")
        .join(",");
    queries.push(
      db
        .prepare(
          "INSERT INTO " +
            table +
            "(" +
            columns +
            ") VALUES " +
            marks +
            " " +
            conflict,
        )
        .bind(...args),
    );
  }
  if (queries.length) await db.batch(queries);
  let next = offset + slice.length,
    nextStage = stage;
  if (next >= total) {
    nextStage = stages[stages.indexOf(stage) + 1];
    next = 0;
  }
  if (!nextStage) {
    const counts = await db
      .prepare(
        "SELECT series_id,count(*) n FROM atlas_observations GROUP BY series_id",
      )
      .all();
    const byId = new Map(counts.results.map((r: any) => [r.series_id, r.n]));
    if (seed.series.some((s: any) => byId.get(s.id) !== s.rows.length))
      return Response.json(
        { error: "Importación incompleta: recuento por serie no coincide" },
        { status: 500 },
      );
    await db
      .prepare("INSERT OR IGNORE INTO atlas_releases VALUES(?,?,?)")
      .bind(
        seed.version,
        seed.series.reduce((n: number, s: any) => n + s.rows.length, 0),
        new Date().toISOString(),
      )
      .run();
  }
  return Response.json({
    ready: !nextStage,
    next,
    stage: nextStage,
    total,
    mode: parentPresent ? "incremental" : "full",
  });
}
