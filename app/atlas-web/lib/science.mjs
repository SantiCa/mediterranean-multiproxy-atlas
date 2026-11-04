import { groupKey, seriesMatches, inGroup, isAggregateKey } from "./proxies.mjs";
export const finite = (x) => typeof x === "number" && Number.isFinite(x);
export const mean = (a) => a.reduce((s, v) => s + v, 0) / a.length;
export function median(a) {
  const s = [...a].sort((x, y) => x - y),
    n = s.length;
  return n ? s[Math.floor(n / 2)] / 2 + s[Math.floor((n - 1) / 2)] / 2 : NaN;
}
export function summarize(data, f) {
  if (
    ![f.min, f.max].every(finite) ||
    f.min > f.max ||
    (f.mode === "z" &&
      (![f.refMin, f.refMax].every(finite) || f.refMin >= f.refMax))
  )
    throw new Error("El intervalo de edad o de referencia no es válido.");
  const records = new Map(data.records.map((r) => [r.id, r]));
  const agg = isAggregateKey(f.group);
  const candidates = data.series.filter((s) =>
    agg ? inGroup(s, f.group) : s.proxy === f.proxy && (!f.group || groupKey(s) === f.group),
  );
  // An explicit aggregation may mix comparison groups; otherwise only one group.
  if (!agg && new Set(candidates.map(groupKey)).size > 1)
    throw new Error("Selecciona un único grupo de variable, método y unidad.");
  return candidates
    .map((s) => {
      const record = records.get(s.record_id),
        finiteRows = s.rows.filter((r) => finite(r[0]) && finite(r[1]));
      const target = finiteRows.filter((r) => r[0] >= f.min && r[0] <= f.max);
      const ref = finiteRows.filter(
          (r) => r[0] >= f.refMin && r[0] <= f.refMax,
        ),
        values = ref.map((r) => r[1]);
      const mu = values.length ? mean(values) : null,
        sd = values.length
          ? Math.sqrt(mean(values.map((x) => (x - mu) ** 2)))
          : null;
      let reason = null;
      if (!target.length) reason = "Sin muestras en el intervalo";
      else if (target.length < f.minN) reason = `Menos de ${f.minN} muestras`;
      else if (f.mode === "z" && (ref.length < 5 || !finite(sd) || sd <= 1e-10))
        reason = "Referencia insuficiente o constante (mínimo 5 valores)";
      const raw = target.length
        ? (f.stat === "mean" ? mean : median)(target.map((r) => r[1]))
        : null;
      const mapped = reason ? null : f.mode === "z" ? (raw - mu) / sd : raw;
      return {
        record,
        series: s,
        rows: finiteRows,
        target,
        n: target.length,
        nUnique: new Set(target.map((r) => r[0])).size,
        value: mapped,
        raw,
        reason,
        reference: {
          n: ref.length,
          mean: mu,
          sd,
          min: ref.length ? Math.min(...ref.map((r) => r[0])) : null,
          max: ref.length ? Math.max(...ref.map((r) => r[0])) : null,
        },
        ageMissing: s.rows.length - finiteRows.length,
      };
    })
    .filter((r) => seriesMatches(r.series, r.record, f));
}

export function haversine(a, b) {
  const rad = Math.PI / 180,
    dlat = (b[1] - a[1]) * rad,
    dlon = (b[0] - a[0]) * rad;
  return (
    6371 *
    2 *
    Math.asin(
      Math.min(
        1,
        Math.sqrt(
          Math.sin(dlat / 2) ** 2 +
            Math.cos(a[1] * rad) *
              Math.cos(b[1] * rad) *
              Math.sin(dlon / 2) ** 2,
        ),
      ),
    )
  );
}
const cross = (o, a, b) =>
  (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
export function convexHull(points) {
  const p = [...new Map(points.map((x) => [x.join(","), x])).values()].sort(
    (a, b) => a[0] - b[0] || a[1] - b[1],
  );
  if (p.length < 3) return [];
  const lo = [],
    hi = [];
  for (const x of p) {
    while (lo.length >= 2 && cross(lo.at(-2), lo.at(-1), x) <= 0) lo.pop();
    lo.push(x);
  }
  for (const x of p.slice().reverse()) {
    while (hi.length >= 2 && cross(hi.at(-2), hi.at(-1), x) <= 0) hi.pop();
    hi.push(x);
  }
  return lo.slice(0, -1).concat(hi.slice(0, -1));
}
export function inside(p, ring) {
  let yes = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const a = ring[i],
      b = ring[j];
    if (
      a[1] > p[1] !== b[1] > p[1] &&
      p[0] < ((b[0] - a[0]) * (p[1] - a[1])) / (b[1] - a[1]) + a[0]
    )
      yes = !yes;
  }
  return yes;
}
export function landMask(geojson) {
  const polygons = geojson.features.flatMap((f) =>
    f.geometry.type === "Polygon"
      ? [f.geometry.coordinates]
      : f.geometry.type === "MultiPolygon"
        ? f.geometry.coordinates
        : [],
  );
  const indexed = polygons.map((rings) => ({
    rings,
    minX: Math.min(...rings[0].map((p) => p[0])),
    maxX: Math.max(...rings[0].map((p) => p[0])),
    minY: Math.min(...rings[0].map((p) => p[1])),
    maxY: Math.max(...rings[0].map((p) => p[1])),
  }));
  return (p) =>
    indexed.some(
      (g) =>
        p[0] >= g.minX &&
        p[0] <= g.maxX &&
        p[1] >= g.minY &&
        p[1] <= g.maxY &&
        inside(p, g.rings[0]) &&
        !g.rings.slice(1).some((h) => inside(p, h)),
    );
}
export function fieldGrid(items, radiusKm = 600, isLand = null) {
  // Co-located deployments can differ only in published coordinate precision.
  // Group to four decimals (about 11 m in latitude) for the regional surface.
  // Keep the original coordinates, measurements and record identities on the map.
  const bySite = new Map();
  for (const s of items.filter((x) => finite(x.value))) {
    const k = Math.round(s.record.longitude * 1e4) + "," + Math.round(s.record.latitude * 1e4);
    if (!bySite.has(k)) bySite.set(k, []);
    bySite.get(k).push(s);
  }
  const a = [...bySite.values()].map((list) =>
      list.length === 1 ? list[0] : { ...list[0], value: median(list.map((x) => x.value)) },
    ),
    merged = [...bySite.values()].filter((l) => l.length > 1).length,
    coords = a.map((s) => [s.record.longitude, s.record.latitude]);
  const hull = convexHull(coords);
  if (hull.length < 3)
    return {
      cells: [],
      reason: "Se necesitan al menos 3 sitios distintos y no alineados.",
    };
  const xs = coords.map((p) => p[0]),
    ys = coords.map((p) => p[1]),
    minX = Math.min(...xs),
    maxX = Math.max(...xs),
    minY = Math.min(...ys),
    maxY = Math.max(...ys);
  if (maxX - minX > 180)
    return {
      cells: [],
      reason:
        "La superficie v1 no admite dominios que crucen el antimeridiano.",
    };
  const dx = (maxX - minX) / 56,
    dy = (maxY - minY) / 32,
    cells = [];
  const marine = a.every((s) => s.record.realm === "marine"),
    continental = a.every((s) => s.record.realm !== "marine");
  for (let ix = 0; ix < 56; ix++)
    for (let iy = 0; iy < 32; iy++) {
      const p = [minX + (ix + 0.5) * dx, minY + (iy + 0.5) * dy];
      if (!inside(p, hull)) continue;
      if (isLand && ((marine && isLand(p)) || (continental && !isLand(p))))
        continue;
      const near = a
        .map((s) => ({
          value: s.value,
          d: haversine(p, [s.record.longitude, s.record.latitude]),
        }))
        .filter((s) => s.d <= radiusKm);
      if (near.length < 3) continue;
      const exact = near.find((s) => s.d < 0.001);
      const value = exact
        ? exact.value
        : near.reduce(
            (sum, s) => sum + s.value / Math.max(s.d * s.d, 0.001),
            0,
          ) / near.reduce((sum, s) => sum + 1 / Math.max(s.d * s.d, 0.001), 0);
      cells.push({
        lon: p[0],
        lat: p[1],
        dx,
        dy,
        value,
        neighbors: near.length,
      });
    }
  return {
    cells,
    hull,
    merged,
    reason: cells.length
      ? merged
        ? `${merged} sitios con varias series en las mismas coordenadas a cuatro decimales. Cada sitio cuenta una vez en la superficie (mediana).`
        : null
      : "Sin celdas con 3 vecinos dentro del radio. Se conservan los puntos observados.",
  };
}
export function color(value, min, max, z = false) {
  if (!finite(value)) return "#a9b4b9";
  const t =
    max === min ? 0.5 : Math.max(0, Math.min(1, (value - min) / (max - min)));
  const stops = z
    ? [
        [31, 115, 140],
        [244, 239, 211],
        [201, 88, 49],
      ]
    : [
        [45, 115, 139],
        [233, 209, 133],
        [188, 70, 40],
      ];
  const x = t * 2,
    i = Math.min(1, Math.floor(x)),
    f = x - i;
  return `rgb(${stops[i].map((v, k) => Math.round(v + (stops[i + 1][k] - v) * f)).join(",")})`;
}
export function colorDomain(items, z) {
  const v = items.filter((s) => finite(s.value)).map((s) => s.value);
  if (!v.length) return [-1, 1];
  if (z) {
    const max = Math.max(1, ...v.map(Math.abs));
    return [-max, max];
  }
  return [Math.min(...v), Math.max(...v)];
}
