/** Visual-only thinning retains extrema in consecutive sample-order blocks.
 * All numerical calculations and CSV/SVG exports use the complete selection. */
export function displayRows(rows, limit = 10000) {
  if (rows.length <= limit) return rows;
  if (limit < 4) return rows.length ? [rows[0], rows.at(-1)] : [];
  const blocks = Math.max(1, Math.floor((limit - 2) / 2)),
    out = [rows[0]];
  for (let b = 0; b < blocks; b++) {
    const start = 1 + Math.floor((b * (rows.length - 2)) / blocks),
      end = 1 + Math.floor(((b + 1) * (rows.length - 2)) / blocks);
    let lo = start,
      hi = start;
    for (let i = start + 1; i < end; i++) {
      if (rows[i].value < rows[lo].value) lo = i;
      if (rows[i].value > rows[hi].value) hi = i;
    }
    if (start < end) {
      out.push(rows[Math.min(lo, hi)]);
      if (lo !== hi) out.push(rows[Math.max(lo, hi)]);
    }
  }
  out.push(rows.at(-1));
  return out;
}
export function extent(values) {
  let min = Infinity,
    max = -Infinity;
  for (const v of values) {
    if (Number.isFinite(v)) {
      min = Math.min(min, v);
      max = Math.max(max, v);
    }
  }
  return [min, max];
}
