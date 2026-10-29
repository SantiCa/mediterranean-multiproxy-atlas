/** Owner-uploaded datasets: same row format, units and comparison groups as the
 * curated atlas. Shared by the browser (preview) and the Worker (authoritative check).
 * Rules mirror the curators: values and ages kept as given, no proxy conversion,
 * age-model interpolation only inside the model range (never extrapolated). */
export const LIMITS = { columns: 40, values: 25000, bytes: 1_800_000 };
export const AGE_UNITS = {
  "ka BP": (v) => v,
  "a BP": (v) => v / 1000,
  "a CE/AD": (v) => (1950 - v) / 1000,
  "Ma BP": (v) => v * 1000,
};
export const REALMS = ["marine", "lake", "continental", "speleothem", "other"];

/** Text table (CSV ; , or TSV, quotes allowed). A PANGAEA /* … *\/ header is skipped. */
export function parseTable(text) {
  let t = String(text || "").replace(/^﻿/, "");
  const end = t.indexOf("*/");
  if (t.trimStart().startsWith("/*") && end > 0) t = t.slice(end + 2);
  const lines = t.split(/\r?\n/);
  const first = lines.findIndex((l) => l.trim());
  if (first < 0) throw new Error("El archivo está vacío");
  const head = lines[first];
  const delim = ["\t", ";", ","].sort(
    (a, b) => split(head, b).length - split(head, a).length,
  )[0];
  const header = split(head, delim).map((h) => h.trim());
  if (header.length < 2) throw new Error("Se necesitan al menos dos columnas");
  const rows = [];
  for (let i = first + 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    const cells = split(lines[i], delim);
    if (cells.length !== header.length)
      throw new Error(
        `Línea ${i + 1}: ${cells.length} columnas, la cabecera tiene ${header.length}`,
      );
    rows.push({ line: i + 1, cells });
  }
  if (!rows.length) throw new Error("No hay filas de datos");
  return { header, rows, decimalComma: delim !== "," };
}
function split(line, d) {
  const out = [];
  let cur = "",
    q = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (q) {
      if (c === '"' && line[i + 1] === '"') (cur += '"'), i++;
      else if (c === '"') q = false;
      else cur += c;
    } else if (c === '"') q = true;
    else if (c === d) out.push(cur), (cur = "");
    else cur += c;
  }
  out.push(cur);
  return out;
}

/** Empty, NA and censored (<, >) cells are not observations; zeros and signs are kept. */
export function num(cell, decimalComma = false) {
  let c = String(cell ?? "").trim();
  if (!c || /^(na|nan|n\/a|-)$/i.test(c) || c[0] === "<" || c[0] === ">")
    return null;
  if (decimalComma && /^-?\d+,\d+$/.test(c)) c = c.replace(",", ".");
  if (!/^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$/.test(c)) return null;
  const v = Number(c);
  return Number.isFinite(v) ? v : null;
}

/** Depth–age tie points (age already in ka BP); monotonic, one age per depth. */
export function modelPoints(pairs) {
  const m = new Map();
  for (const [z, a] of pairs) {
    if (!Number.isFinite(z) || !Number.isFinite(a)) continue;
    if (m.has(z) && Math.abs(m.get(z) - a) > 1e-9)
      throw new Error(`Modelo de edad: dos edades a ${z} de profundidad`);
    m.set(z, a);
  }
  const pts = [...m].sort((a, b) => a[0] - b[0]);
  if (pts.length < 2) throw new Error("Modelo de edad: mínimo 2 puntos");
  for (let i = 1; i < pts.length; i++)
    if (pts[i][1] < pts[i - 1][1])
      throw new Error(
        "Modelo de edad: la edad disminuye con la profundidad (inversión/hiato); no se interpola",
      );
  return pts;
}
export function interpolate(pts, z) {
  if (!Number.isFinite(z) || z < pts[0][0] || z > pts.at(-1)[0]) return null;
  let lo = 0,
    hi = pts.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (pts[mid][0] <= z) lo = mid;
    else hi = mid;
  }
  const [z0, a0] = pts[lo],
    [z1, a1] = pts[hi];
  return z1 === z0 ? a0 : a0 + ((a1 - a0) * (z - z0)) / (z1 - z0);
}
const slug = (s) =>
  String(s)
    .normalize("NFKD")
    .replace(/[^A-Za-z0-9]+/g, "_")
    .replace(/^_|_$/g, "")
    .slice(0, 50) || "x";
const text = (v, n = 300) => (v == null ? null : String(v).slice(0, n));

/** Validate an upload and build atlas-shaped record + series.
 * input: { id, filename, record:{name,latitude,longitude,realm,...}, table:{header,rows,decimalComma},
 *   depthColumn, ageColumn, ageUnit, ageModel:{pairs:[[depth, age]], unit, source}|null,
 *   columns:[{index, target:{type:"group",key}|{type:"new",label,unit,method,family}}] }
 * groups: Map key → metadata of one public series of that group (unit, family, …). */
export function buildPrivate(input, groups) {
  const r = input.record || {},
    lat = Number(r.latitude),
    lon = Number(r.longitude);
  if (!String(r.name || "").trim()) throw new Error("Falta el nombre del sondeo");
  if (!(lat >= -90 && lat <= 90) || !(lon >= -180 && lon <= 180))
    throw new Error("Coordenadas fuera de rango (lat −90…90, lon −180…180)");
  if (!REALMS.includes(r.realm)) throw new Error("Tipo de archivo no válido");
  const { header, rows, decimalComma } = input.table || {};
  if (!Array.isArray(header) || !Array.isArray(rows) || !rows.length)
    throw new Error("Tabla vacía");
  const col = (i) => Number.isInteger(i) && i >= 0 && i < header.length;
  const cols = (input.columns || []).filter((c) => c && c.target);
  if (!cols.length) throw new Error("Elige al menos una columna de valores");
  if (cols.length > LIMITS.columns) throw new Error("Demasiadas columnas");
  if (cols.some((c) => !col(c.index)))
    throw new Error("Columna de valores inexistente");
  let ageOf, chronology, warnings = [];
  if (input.ageModel) {
    if (!col(input.depthColumn))
      throw new Error("El modelo de edad requiere una columna de profundidad");
    const f = AGE_UNITS[input.ageModel.unit];
    if (!f) throw new Error("Unidad de edad del modelo no admitida");
    const pts = modelPoints(
      (input.ageModel.pairs || []).map(([z, a]) => [Number(z), f(Number(a))]),
    );
    ageOf = (cells) => {
      const z = num(cells[input.depthColumn], decimalComma);
      return [interpolate(pts, z), null];
    };
    chronology = {
      chronology_status: "private_interpolated_age_model",
      chronology_label:
        "Privado · edad interpolada en profundidad desde tu modelo (sin extrapolar)",
      age_model:
        "linear interpolation in depth between owner-supplied tie points; no extrapolation",
      age_model_tie_points: pts.length,
      age_model_source: text(input.ageModel.source),
      age_scale: input.ageModel.unit,
    };
  } else {
    if (!col(input.ageColumn))
      throw new Error("Elige la columna de edad o aporta un modelo de edad");
    const f = AGE_UNITS[input.ageUnit];
    if (!f) throw new Error("Unidad de edad no admitida");
    if (/14C|radiocarb/i.test(header[input.ageColumn]))
      throw new Error(
        "La columna parece edad radiocarbono: aporta edades calendario (no se recalibra)",
      );
    ageOf = (cells) => {
      const a = num(cells[input.ageColumn], decimalComma);
      return [a == null ? null : f(a), cells[input.ageColumn]];
    };
    chronology = {
      chronology_status: "private_age_column",
      chronology_label: "Privado · edad aportada por el propietario",
      age_model: "owner age column: " + input.ageUnit + " → ka BP",
      age_scale: input.ageUnit,
    };
  }
  const id = String(input.id || "").replace(/[^a-z0-9]/gi, "").slice(0, 16);
  if (!id) throw new Error("Identificador inválido");
  const rid = "private-" + id;
  const record = {
    id: rid,
    name: text(r.name, 120).trim(),
    core: text(r.name, 120).trim(),
    provider: "Privado",
    realm: r.realm,
    archive_type: text(r.archive_type || r.realm, 60),
    latitude: lat,
    longitude: lon,
    water_depth_m: Number.isFinite(Number(r.water_depth_m)) && r.water_depth_m !== "" ? Number(r.water_depth_m) : null,
    publication_year: null,
    reference: text(r.reference),
    notes: text(r.notes, 1000),
    source_file: text(input.filename, 200),
    private: true,
    inventory_ids: [],
    review_status: "private_owner_upload",
    qc_notes: ["Datos privados del propietario; visibles solo con su sesión"],
  };
  let total = 0;
  const series = cols.map((c) => {
    let meta;
    if (c.target.type === "group") {
      const g = groups.get(c.target.key);
      if (!g) throw new Error("Grupo de comparación desconocido: " + c.target.key);
      const hu = (header[c.index].match(/\[([^\]]+)\]/) || [])[1];
      const norm = (u) => String(u).toLowerCase().replace(/\s+/g, "").replace("permil", "‰").replace("degc", "°c");
      if (hu && norm(hu) !== norm(g.unit))
        throw new Error(`«${header[c.index]}»: unidad [${hu}] distinta de la del grupo (${g.unit})`);
      // Coherence: proxy, method, unit and comparison group are inherited, never edited.
      meta = {
        proxy: g.proxy,
        compatibility_group: g.compatibility_group,
        unit: g.unit,
        family: g.family,
        variable_label: g.variable_label || g.label?.split(" · ")[0],
        method: g.method,
        evidence_type: g.evidence_type || "published_value",
      };
    } else if (c.target.type === "new") {
      const t = c.target;
      if (!String(t.label || "").trim() || !String(t.unit || "").trim())
        throw new Error("Proxy nuevo: indica nombre y unidad");
      const p = "private_" + slug(t.label) + "_" + slug(t.unit);
      meta = {
        proxy: p,
        compatibility_group: p + "_" + slug(t.method || "metodo_no_declarado"),
        unit: text(t.unit, 40),
        family: text(t.family || "Privado", 60),
        variable_label: text(t.label, 120),
        method: text(t.method || "no declarado", 200),
        evidence_type: "owner_value",
      };
    } else throw new Error("Destino de columna no válido");
    const out = [];
    let blank = 0,
      rejected = 0;
    for (let k = 0; k < rows.length; k++) {
      const cells = rows[k].cells,
        v = num(cells[c.index], decimalComma);
      if (v == null) {
        String(cells[c.index] ?? "").trim() ? rejected++ : blank++;
        continue;
      }
      const [age, ageText] = ageOf(cells);
      out.push([
        age,
        v,
        k + 1,
        rows[k].line ?? null,
        ageText == null ? null : String(ageText),
        String(cells[c.index]),
        null,
        null,
        col(input.depthColumn) ? String(cells[input.depthColumn]) : null,
      ]);
    }
    if (out.length < 1) throw new Error(`Columna «${header[c.index]}» sin valores numéricos`);
    total += out.length;
    out.sort((a, b) => (a[0] == null) - (b[0] == null) || (a[0] ?? 0) - (b[0] ?? 0) || a[2] - b[2]);
    const ages = out.map((x) => x[0]).filter(Number.isFinite);
    if (rejected)
      warnings.push(`«${header[c.index]}»: ${rejected} celdas no numéricas o censuradas ignoradas`);
    if (out.length - ages.length)
      warnings.push(`«${header[c.index]}»: ${out.length - ages.length} valores sin edad (fuera del modelo o vacía)`);
    if (meta.unit === "%" && out.some((x) => x[1] < 0 || x[1] > 100))
      warnings.push(`«${header[c.index]}»: porcentajes fuera de 0–100 (conservados)`);
    return {
      id: rid + ":" + slug(header[c.index]) + "_" + c.index,
      record_id: rid,
      ...meta,
      label: (meta.variable_label || header[c.index]) + " · " + record.name,
      source_column: header[c.index],
      source_column_index: c.index,
      ...chronology,
      observation_count: out.length,
      age_min_ka_bp: ages.length ? Math.min(...ages) : null,
      age_max_ka_bp: ages.length ? Math.max(...ages) : null,
      private: true,
      license: "Privado (propietario)",
      review_status: "private_owner_upload",
      rows: out,
    };
  });
  if (total > LIMITS.values)
    throw new Error(`Demasiados valores (${total}; máximo ${LIMITS.values} por subida)`);
  return { record, series, warnings, values: total };
}
