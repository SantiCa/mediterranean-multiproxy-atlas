/** Resolve a stable observation plan once per request. A known complete parent
 * allows an append-only delta; a fresh database always imports the full release. */
export function importSeries(seed, parentPresent) {
  if (!parentPresent || !seed.parent_version) return seed.series;
  if (!Array.isArray(seed.append_series_ids))
    throw new Error("La release no declara sus series nuevas");
  const requested = new Set(seed.append_series_ids),
    known = new Set(seed.series.map((s) => s.id));
  if (
    requested.size !== seed.append_series_ids.length ||
    [...requested].some((id) => !known.has(id))
  )
    throw new Error("Manifiesto incremental inválido");
  return seed.series.filter((s) => requested.has(s.id));
}
/** Read a bounded slice in immutable seed order without allocating a flat copy
 * of every observation for every batch. Source-row identity never changes. */
export function observationBatch(series, offset, limit = 240) {
  if (
    !Number.isInteger(offset) ||
    offset < 0 ||
    !Number.isInteger(limit) ||
    limit <= 0
  )
    throw new Error("Cursor inválido");
  const total = series.reduce((n, s) => n + s.rows.length, 0),
    rows = [];
  if (offset > total) throw new Error("Cursor fuera de rango");
  let before = 0;
  for (const s of series) {
    if (rows.length >= limit) break;
    const start = Math.max(0, offset - before),
      end = Math.min(s.rows.length, start + limit - rows.length);
    if (start < s.rows.length)
      for (let i = start; i < end; i++) rows.push({ id: s.id, row: s.rows[i] });
    before += s.rows.length;
  }
  return { rows, total };
}
