/** Provenance belongs to the selected series when one physical core has
 * multiple datasets/publications. Explicit null never becomes a guessed DOI. */
export function seriesSource(s, r) {
  const own = (field) => (s[field] !== undefined ? s[field] : r[field]);
  return {
    dataset_doi: own("dataset_doi"),
    paper_doi: own("paper_doi"),
    publication_year: own("publication_year"),
    source_url: s.source_url || r.source_url,
    raw_sha256: s.raw_sha256 || r.raw_sha256,
    license: own("license"),
    license_url: own("license_url"),
    citation: s.citation || r.citation || r.paper_title || null,
    method: s.method,
    unit: s.unit,
    source_column: s.source_column,
    source_column_index: s.source_column_index,
    original_unit: s.original_unit,
    chronology_status: s.chronology_status,
    age_scale: s.age_scale || s.age_transformation || r.time_scale,
    age_model: s.age_model || r.age_model,
    uncertainty_type: s.uncertainty_type,
    age_probability_levels: s.age_probability_levels,
    age_probability_bounds: s.age_probability_bounds,
  };
}

/** Keep native interval quantiles and their labels; never manufacture a sigma. */
export function rowUncertainty(s, row) {
  return {
    value_uncertainty_type: s.uncertainty_type ?? null,
    age_probability_levels: s.age_probability_levels ?? null,
    age_probability_bounds:
      s.age_probability_bounds?.find((b) => b[0] === row[2]) ?? null,
  };
}
