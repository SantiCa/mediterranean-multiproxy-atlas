// Publication-time QC corrections (config/qc_corrections.json) applied to a copy of the
// versioned seed. Originals stay in each row (age_original/value_original). Idempotent:
// an age correction only touches rows whose age still equals the archived string.
const TRANSFORMS = {
  "ka_bp = 1.95 - ka_ce": (ka) => Math.round((1.95 - ka) * 1e6) / 1e6,
};

export function applyQc(seed, qc) {
  const sitesByRecord = new Map();
  for (const site of qc.spatial_sites || []) {
    for (const id of site.record_ids) {
      if (sitesByRecord.has(id)) throw new Error("QC: sondeo asignado a más de un sitio " + id);
      sitesByRecord.set(id, site);
    }
  }
  const records = seed.records?.map((record) => {
    const site = sitesByRecord.get(record.id);
    return site ? { ...record, spatial_site_id: site.id, spatial_site_source_url: site.source_url,
      qc_notes: [...new Set([...(record.qc_notes || []), site.note])] } : record;
  });
  const holds = new Map((qc.holds || []).map((h) => [h.id, h]));
  const ids = new Set(seed.series.map((s) => s.id));
  for (const h of holds.values()) {
    if (!ids.has(h.id)) throw new Error("QC: retención de serie inexistente " + h.id);
    if (h.duplicate_of && !ids.has(h.duplicate_of)) throw new Error("QC: duplicado sin original " + h.id);
  }
  const applied = [];
  const series = seed.series
    .filter((s) => !holds.has(s.id))
    .map((s) => {
      const c = (qc.age_corrections || []).find((x) => x.dataset_doi === s.dataset_doi);
      if (!c) return s;
      const f = TRANSFORMS[c.transform];
      if (!f) throw new Error("QC: transformación desconocida " + c.transform);
      let changed = 0;
      const rows = s.rows.map((r) => {
        if (r[0] === null || r[4] === null || r[4] === "" || r[0] !== Number(r[4])) return r;
        changed++;
        return [f(r[0]), ...r.slice(1)];
      });
      if (!changed) return s;
      const ages = rows.map((r) => r[0]).filter((a) => a !== null);
      applied.push(s.id);
      return {
        ...s,
        rows,
        age_min_ka_bp: Math.min(...ages),
        age_max_ka_bp: Math.max(...ages),
        age_scale: "qc_corrected: " + c.transform,
        age_model: "qc_corrected: " + c.transform + " (original archivado conservado en age_original)",
        qc_notes: [...(s.qc_notes || []), "Corrección QC de edad: " + c.reason],
      };
    })
    .map((series) => {
      const annotation = qc.dataset_annotations?.[series.dataset_doi];
      if (!annotation) return series;
      if (series.raw_sha256 !== annotation.raw_sha256)
        throw new Error("QC: original distinto del auditado " + series.dataset_doi);
      if (annotation.age_model)
        return { ...series, age_model: annotation.age_model, age_model_source_url: annotation.source_url };
      const warning = annotation.chronology_warning;
      if (!warning) return series;
      const samples = warning.samples.filter((sample) => {
        const row = series.rows.find((row) => row[2] === sample.row && row[3] === sample.line);
        if (!row) return false;
        if (row[4] !== sample.age_original || row[8] !== sample.depth_original)
          throw new Error("QC: localizador distinto del auditado " + series.id + ":" + sample.line);
        return true;
      });
      return samples.length ? { ...series, chronology_warning: { ...warning, samples, source_url: annotation.source_url } } : series;
    });
  return {
    seed: { ...seed, ...(records ? { records } : {}), series },
    qc: {
      age_corrected_series: applied.length,
      age_corrections: (qc.age_corrections || []).map(({ dataset_doi, transform, reason }) => ({ dataset_doi, transform, reason })),
      holds: [...holds.values()].map((h) => ({ id: h.id, duplicate_of: h.duplicate_of || null, reason: h.reason || "Serie idéntica a otra del mismo sondeo (importada dos veces)" })),
    },
  };
}
