"""Curate three NOAA WDS speleothem tables, preserving original cells and locators."""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parents[2] / "data/interim/v1_continental"
records = []
observations = []
manifest = []

sources = [
    ("noaa_5423.json", "soreq_2003-noaa.txt", "6550", "7158", "noaa-soreq-2003",
     "Soreq Cave composite", 1.0, "age_calkaBP"),
    ("noaa_5423.json", "peqiin_2003-noaa.txt", "6549", "7157", "noaa-peqiin-2003",
     "Peqiin Cave composite", 1.0, "age_calkaBP"),
    ("noaa_8637.json", "sofular2009-noaa.txt", "22943", "12506", "noaa-sofular-2009",
     "Sofular Cave · So-1", 0.001, "age_calBP"),
]

for metadata_file, filename, site_id, table_id, record_id, name, age_factor, age_col in sources:
    study = json.loads((HERE / metadata_file).read_text(encoding="utf-8"))["study"][0]
    # Match by table ID, not by site-list order. NOAA's POINT coordinates are [lat, lon].
    matches = [(site, table) for site in study["site"] for table in site["paleoData"]
               if str(table["NOAADataTableId"]) == table_id]
    assert len(matches) == 1
    site, table = matches[0]
    assert str(site["NOAASiteId"]) == site_id
    raw_path = HERE / filename
    raw = raw_path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    lines = raw.decode("utf-8-sig").splitlines()
    data_lines = [(number, line) for number, line in enumerate(lines, 1)
                  if line.strip() and not line.startswith("#")]
    header = data_lines[0][1].split("\t")
    properties = site["geo"]["properties"]
    files = [f for f in table["dataFile"] if f["fileUrl"].endswith(filename)]
    assert len(files) == 1
    data_url = files[0]["fileUrl"]
    pub = study["publication"][0]
    notes = []
    if "soreq" in record_id:
        notes.append("Coordinate conflict retained: file Site_Information/API bbox gives 31.8 N, 35.0 E, while source Description says 31.45 N, 35.03 E. Mapped coordinates use Site_Information, not a silently corrected location.")
    if age_factor == 1.0:
        notes.append("Data collection Time_Unit says cal yr BP but numeric variable age_calkaBP explicitly uses calendar kiloyears before present; values retained in ka BP per variable metadata.")
        notes.append("Composite cave record; individual stalagmite membership and individual age-model uncertainty not resolved in this first extraction.")
    else:
        notes.append("Published U-Th chronology retained. Calendar-year BP values divided by 1000 solely to express ka BP; no chronology recalibration or smoothing.")
        notes.append("February 2024 source update added SISAL depths; source dataset publication remains linked to the 2009 article.")
        notes.append("Published hiatus in So-1 between 21.2 and 24.8 ka BP (Fleitmann et al. 2009); do not interpolate or join a continuous curve across it.")
    record = {
        "id": record_id,
        "name": name,
        "site": site["siteName"],
        "realm": "speleothem",
        "archive_type": "speleothem calcite",
        "latitude": float(properties["southernmostLatitude"]),
        "longitude": float(properties["westernmostLongitude"]),
        "elevation_m": float(properties["minElevationMeters"]),
        "water_depth_m": None,
        "provider": "NOAA WDS Paleoclimatology",
        "source": "noaa_wds_paleo",
        "source_id": study["NOAAStudyId"],
        "source_site_id": site["NOAASiteId"],
        "source_table_id": table["NOAADataTableId"],
        "dataset_doi": study["doi"].removeprefix("https://doi.org/"),
        "dataset_title": study["studyName"],
        "paper_doi": pub["identifier"]["id"],
        "paper_title": pub["title"],
        "paper_year": pub["pubYear"],
        "publication_year": pub["pubYear"],
        "authors": study["investigators"],
        "related_publications": [{"year": p["pubYear"], "title": p["title"],
                                   "doi": p.get("identifier", {}).get("id")} for p in study["publication"]],
        "study_url": study["onlineResourceLink"],
        "data_url": data_url,
        "source_sha256": sha,
        "license": "NOAA WDS open archive: unrestricted public access and citation requested; specific Creative Commons license not supplied in this record",
        "license_url": "https://www.ncei.noaa.gov/products/paleoclimatology/contributing-data",
        "data_license_original": study.get("dataLicenseDescription"),
        "data_license_url_original": study.get("dataLicenseUrl"),
        "rights_basis": "NOAA WDS contribution policy: make data freely and permanently available without restrictions; the downloaded file explicitly requests citation of study, dataset DOI, paper DOI and access date.",
        "time_scale": "calendar BP (1950)",
        "age_unit_original": "calendar ka BP" if age_factor == 1.0 else "calendar yr BP",
        "age_model": "Published archived chronology; not recalculated",
        "method": "Isotope ratio mass spectrometry; calcium carbonate",
        "sample_type": "composite speleothem" if age_factor == 1.0 else "stalagmite So-1",
        "qc_notes": notes,
        "hiatus_intervals_ka": [[21.2, 24.8]] if "sofular" in record_id else [],
        "proxies": ["speleothem_d18O", "speleothem_d13C"],
    }
    proxy_cols = [("speleothem_d18O", "d18O_vpdb"), ("speleothem_d13C", "d13C_vpdb")]
    record_observations = []
    for source_row, (source_line, line) in enumerate(data_lines[1:], 1):
        cells = line.split("\t")
        if len(cells) != len(header):
            raise ValueError((filename, source_line, "unexpected column count"))
        row = dict(zip(header, cells))
        age_original = row[age_col]
        age = float(age_original) * age_factor if age_original.strip() else None
        assert age is None or math.isfinite(age)
        for proxy, source_column in proxy_cols:
            original = row[source_column]
            if original.strip().lower() in {"", "na", "nan", "-999", "-999.0"}:
                continue
            value = float(original)
            assert math.isfinite(value)
            item = {
                "id": f"{record_id}:{source_row}:{source_column}",
                "record_id": record_id,
                "proxy": proxy,
                "proxy_name": "Speleothem δ18O" if proxy.endswith("d18O") else "Speleothem δ13C",
                "age_ka_bp": age,
                "age_original": age_original,
                "age_unit_original": record["age_unit_original"],
                "time_scale": "calendar BP (1950)",
                "value": value,
                "value_original": original,
                "unit": "‰ VPDB",
                "material": "speleothem calcium carbonate",
                "source_column": source_column,
                "source_row": source_row,
                "source_line": source_line,
                "source_sha256": sha,
                "age_uncertainty_ka": None,
                "value_uncertainty": 0.07 if "sofular" in record_id and proxy.endswith("d18O") else (0.06 if "sofular" in record_id else None),
                "value_uncertainty_type": "analytical precision 1σ, source method statement" if "sofular" in record_id else None,
                "depth_original": row.get("depth_mm"),
                "depth_unit_original": "mm" if "depth_mm" in row else None,
                "transformation": "original value; age unit conversion yr/1000" if age_factor != 1 else "original value and age; no numerical transformation",
            }
            record_observations.append(item)
    ages = [x["age_ka_bp"] for x in record_observations if x["age_ka_bp"] is not None]
    record.update({"sample_rows": len(data_lines) - 1, "observation_count": len(record_observations),
                   "age_min_ka_bp": min(ages), "age_max_ka_bp": max(ages),
                   "values_missing_age": sum(x["age_ka_bp"] is None for x in record_observations)})
    records.append(record)
    observations.extend(record_observations)
    manifest.append({"file": filename, "url": data_url, "sha256": sha, "bytes": len(raw),
                     "metadata_file": metadata_file, "source_header_line": data_lines[0][0],
                     "downloaded_file_mtime_utc": datetime.fromtimestamp(raw_path.stat().st_mtime, timezone.utc).isoformat(),
                     "accessed_on": "2026-10-28"})

bundle = {"schema": "medatlas.v1.continental.seed", "curated_at_utc": datetime.now(timezone.utc).isoformat(),
          "records": records, "observations": observations,
          "transformations": [
              {"id": "NOAA-speleo-cell-extract-v1", "description": "Select finite d18O_vpdb and d13C_vpdb cells, preserve source row/line and bytes hash; no interpolation, age-model recalculation, environmental conversion or normalisation."},
              {"id": "calendar-yr-BP-to-ka-BP", "formula": "age_ka_bp = age_calBP / 1000", "applies_to": "noaa-sofular-2009"}],
          "manifest": manifest,
          "limitations": ["Soreq coordinate disagreement preserved and flagged", "Individual age-model uncertainties not propagated", "Records are cave proxies, not interchangeable rainfall or temperature reconstructions", "No cross-proxy normalisation performed"]}
(HERE / "continental_seed.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
compact_keys = ("id", "record_id", "proxy", "age_ka_bp", "age_original", "value", "value_original",
                "source_line", "source_row", "source_column", "value_uncertainty")
compact = {**bundle, "observations": [{key: row[key] for key in compact_keys} for row in observations]}
compact["observation_metadata_inherited_from_record"] = ["source_sha256", "age_unit_original", "time_scale", "method"]
(HERE / "continental_compact.json").write_text(json.dumps(compact, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
print(json.dumps({"records": len(records), "observations": len(observations),
                  "counts": [{"id": r["id"], "rows": r["sample_rows"], "values": r["observation_count"],
                              "age_min": r["age_min_ka_bp"], "age_max": r["age_max_ka_bp"]} for r in records]}, indent=2))
