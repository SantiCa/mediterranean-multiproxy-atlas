/** Global extent is independent of proxy, publication and moving-window filters. */
export function timeExtent(data, metadataMax = null) {
  let min = Infinity,
    max = -Infinity;
  for (const s of data?.series || []) {
    if (Number.isFinite(s.age_min_ka_bp)) min = Math.min(min, s.age_min_ka_bp);
    if (Number.isFinite(s.age_max_ka_bp)) max = Math.max(max, s.age_max_ka_bp);
    for (const r of s.rows || [])
      if (typeof r[0] === "number" && Number.isFinite(r[0])) {
        min = Math.min(min, r[0]);
        max = Math.max(max, r[0]);
      }
  }
  if (!Number.isFinite(min)) return { min: 0, max: 1, numericMax: null };
  return {
    min,
    max: Math.max(max, Number.isFinite(metadataMax) ? metadataMax : max),
    numericMax: max,
  };
}
/** Clamp the position without shrinking a fixed window at a domain boundary. */
export function moveWindow(start, width, domain) {
  if (
    ![start, width, domain.min, domain.max].every(Number.isFinite) ||
    width <= 0 ||
    domain.max <= domain.min
  )
    throw new Error("Ventana o dominio inválido");
  const w = Math.min(width, domain.max - domain.min),
    a = Math.max(domain.min, Math.min(domain.max - w, start));
  return {
    min: Number(a.toFixed(8)),
    max: Number((a + w).toFixed(8)),
    width: w,
  };
}
