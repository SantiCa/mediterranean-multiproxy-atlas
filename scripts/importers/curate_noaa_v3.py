"""Curate an explicit NOAA batch without estimating ages or climate variables.

Default: offline, using the immutable files named in noaa_v3_sources.json.
With --fetch: retrieve missing files only and reject changed source bytes. The
compact row contract is inherited from atlas-v1 (nine cells per observation).
Each NOAA site is one record even when it has several tables; file provenance
lives on each series so a multi-table core is not duplicated spatially.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
SOURCE_CONTRACT = Path(__file__).with_name("noaa_v3_sources.json")
CACHE = ROOT / "data/interim/quantitative_v3/noaa"
OUTPUT = ROOT / "data/interim/quantitative_v3/noaa_curated.json"
AUDIT = ROOT / "reports/noaa_v3_audit.json"
POLICY = "https://www.ncei.noaa.gov/products/paleoclimatology/contributing-data"
ROW_FORMAT = ["age_ka_bp", "value", "source_row", "source_line", "age_original",
              "value_original", "age_uncertainty_ka", "value_uncertainty", "depth_original"]


def slug(value):
    """Stable ASCII identifier from a source column, not a physical-core match."""
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def read_verified(filename, url, expected_sha, fetch=False):
    """Return cached exact source bytes; changed upstream resources need review."""
    path = CACHE / filename
    if not path.exists() and fetch:
        with urlopen(Request(url, headers={"User-Agent": "MediterraneanMultiproxyAtlas/0.3"}), timeout=45) as response:
            raw = response.read(8_000_001)
        if len(raw) > 8_000_000:
            raise ValueError(f"Bounded download exceeded: {filename}")
        if hashlib.sha256(raw).hexdigest() != expected_sha:
            raise ValueError(f"Upstream bytes changed: {filename}; review a new source version")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise ValueError(f"Cached source hash mismatch: {filename}")
    return raw


def numeric(cell):
    """Parse known NOAA missing tokens; preserve zero, negative BP and signs."""
    cleaned = cell.strip()
    if cleaned.lower() in {"", "na", "nan", "-999", "-999.0", "-999.00", "#div/0!"}:
        return None
    value = float(cleaned)
    if not math.isfinite(value):
        raise ValueError(f"Non-finite undocumented cell {cell!r}")
    return value


def read_table(raw):
    """Retain physical line numbers and source cells, including trailing tabs."""
    lines = raw.decode("utf-8-sig").splitlines()
    data = [(n, line) for n, line in enumerate(lines, 1) if line.strip() and not line.startswith("#")]
    header = [c.strip() for c in data[0][1].split("\t")]
    while header and not header[-1]:
        header.pop()
    if len(set(header)) != len(header):
        raise ValueError("Repeated source column labels")
    result = []
    for number, (line_no, line) in enumerate(data[1:], 1):
        cells = line.split("\t")
        # Several Ohrid files end every row with an empty tab. No interior or
        # scientifically meaningful cell is removed by this schema normalization.
        if len(cells) > len(header) and any(c.strip() for c in cells[len(header):]):
            raise ValueError(f"Extra nonempty source cell at line {line_no}")
        if len(cells) < len(header):
            raise ValueError(f"Short source row at line {line_no}")
        result.append((number, line_no, dict(zip(header, cells[:len(header)]))))
    definitions = {}
    for line in lines:
        if line.startswith("## ") and "\t" in line:
            key, definition = line[3:].split("\t", 1)
            definitions[key.strip()] = definition
    return header, result, definitions


def specs_for(filename):
    """Explicit proxy, unit and compatibility mappings; no unit-only pooling."""
    # column, proxy ID, human label, unit, family, variable, method, evidence
    def spec(column, proxy, label, unit, family, variable, method, evidence="measurement"):
        return dict(column=column, proxy=proxy, label=label, unit=unit, family=family,
                    variable_id=variable, method_id=method, evidence_type=evidence)
    if filename.startswith("jalali"):
        return [
            spec("Uk'37", "alkenone_UK37prime", "Uᵏ′₃₇ · alquenonas", "índice", "Biomarcadores", "alkenone_UK37prime", "alkenone_gc_UK37prime_jalali2018"),
            spec("SSTs", "alkenone_SST_Conte2006", "SST · alquenonas · Conte 2006", "°C", "Temperatura", "sea_surface_temperature", "sst_alkenone_conte2006", "published_reconstruction"),
            spec("N-alkanes", "TERR_alkanes_C27_C33", "n-alcanos terrestres · C₂₇–C₃₃", "ng/g", "Biomarcadores", "terrigenous_alkanes_C27_C33", "gc_odd_C27_C33_jalali2018"),
            spec("ACL", "ACL_C27_C33", "ACL · C₂₇–C₃₃", "índice", "Biomarcadores", "average_chain_length_C27_C33", "gc_odd_C27_C33_jalali2018"),
        ]
    if filename.startswith("bourget"):
        result = [spec("%terr", "terrigenous_fraction_Bourget", "Fracción terrígena · Bourget", "%", "Sedimentología", "terrigenous_fraction", "published_terrigenous_fraction_bourget2012")]
        if "ldb04" in filename:
            result.append(spec("K/Ti", "K_Ti_XRF", "K/Ti · XRF", "cociente", "Geoquímica elemental", "potassium_titanium_ratio", "xrf_K_Ti_bourget2012"))
        return result
    if "geochem" in filename:
        return [
            spec("sed_rate", "sedimentation_rate_Ohrid", "Tasa de sedimentación · Ohrid", "cm/año", "Sedimentología", "sedimentation_rate", "orbital_age_depth_Ohrid2020", "published_reconstruction"),
            spec("TIC%", "TIC_bulk", "Carbono inorgánico total · TIC", "%", "Geoquímica elemental", "total_inorganic_carbon", "carbon_analyzer_Ohrid2020"),
            spec("TOC%", "TOC_bulk", "Carbono orgánico total · TOC", "%", "Geoquímica elemental", "total_organic_carbon", "TC_minus_TIC_Ohrid2020"),
            spec("d13C", "lake_bulk_carbonate_d13C", "δ¹³C · carbonato lacustre", "‰ VPDB", "Isótopos estables", "carbonate_d13C", "bulk_calcite_VPDB_Ohrid2020"),
            spec("d18O", "lake_bulk_carbonate_d18O", "δ¹⁸O · carbonato lacustre", "‰ VPDB", "Isótopos estables", "carbonate_d18O", "bulk_calcite_VPDB_Ohrid2020"),
            spec("BSi%", "biogenic_silica", "Sílice biogénica · BSi", "%", "Geoquímica elemental", "biogenic_silica", "FTIR_Ohrid2020"),
        ]
    if "biomarker" in filename:
        return [spec(f"MAAT_{name}", f"MAAT_GDGT_{name}", f"MAAT · GDGT · {label}", "°C", "Temperatura", "mean_annual_air_temperature", f"GDGT_{method}", "published_reconstruction")
                for name, label, method in [("Peterse", "Peterse 2012", "Peterse2012"), ("Russell", "Russell 2018", "Russell2018"), ("deJonge", "de Jonge 2014", "deJonge2014")]] + [
            spec("BIT", "BIT_index", "BIT · índice de tetraéteres", "índice", "Biomarcadores", "branched_isoprenoid_tetraether_index", "published_BIT_Ohrid2020"),
            spec("Diol/Diol+Lolio", "diol_loliolide_ratio", "Dioles / (dioles + loliolidos) · etiqueta nativa", "cociente", "Biomarcadores", "diol_loliolide_ratio", "published_diol_ratio_Ohrid2020"),
        ]
    if "diatom" in filename:
        return [spec("diatom_sum", "diatom_count_sum", "Diatomeas · suma contada", "recuento", "Micropaleontología", "diatom_count_sum", "diatom_count_Ohrid2020")] + [
            spec(column, "diatom_" + slug(column), "Diatomeas · " + label, "%", "Micropaleontología", "diatom_" + slug(column), "ecological_group_Ohrid2020")
            for column, label in [("0-5m%", "grupo 0–5 m"), ("0-10m%", "grupo 0–10 m"), ("0-40m%", "grupo 0–40 m"), ("20-80m%", "grupo 20–80 m"), ("Eutrophic%", "grupo eutrófico")]
        ]
    if "pollen" in filename:
        # Denominators excluding Pinus remain separate variables and methods.
        specs = []
        for column, label in [("Relict%", "relictos"), ("Mesophilous%", "mesófilos"), ("Mesophilous%-pine", "mesófilos · sin Pinus"), ("Montane%", "montanos"), ("Montane%-pine", "montanos · sin Pinus"), ("Pines%", "Pinus"), ("AP%", "arbóreo AP"), ("AP%-pine", "arbóreo AP · sin Pinus"), ("NAP%", "no arbóreo NAP"), ("NAP%-pine", "no arbóreo NAP · sin Pinus"), ("Poaceae%", "Poaceae"), ("Poaceae%-pine", "Poaceae · sin Pinus"), ("Aquatics%", "acuáticos"), ("Aquatics%-pine", "acuáticos · sin Pinus")]:
            denominator = "excluding_Pinus" if "-pine" in column else "including_Pinus"
            specs.append(spec(column, "pollen_" + slug(column), "Polen · " + label, "%", "Palinología", "pollen_" + slug(column), f"pollen_percent_{denominator}_Ohrid2020"))
        specs.append(spec("Charcoal_Conc", "charcoal_concentration", "Carbón microscópico · concentración", "partículas/g", "Paleoincendios", "microscopic_charcoal_concentration", "particles_per_g_Ohrid2020"))
        return specs
    if "sand" in filename:
        return [spec("Sand%", "sand_detrital_pct", "Arena · fracción detrítica", "%", "Sedimentología", "detrital_sand_fraction", "laser_particle_analyzer_Ohrid2020")]
    if "xrf" in filename:
        return [spec("Ti/Ti+K", "Ti_TiK_XRF_Ohrid", "Ti/(Ti+K) · etiqueta nativa Ti/Ti+K", "cociente", "Geoquímica elemental", "Ti_TiK_XRF_Ohrid", "archived_XRF_ratio_Ohrid2020")]
    raise ValueError(f"File lacks a reviewed column mapping: {filename}")


def chronology_for(study_id):
    """Do not equate calendar units with independently dated chronology."""
    if study_id == "28070":
        return "orbital_tuning", "Calendar ka BP as archived; interval chronology uses orbital tuning of climate-sensitive carbon proxies. Not independent evidence for orbital phase/synchrony.", "https://nora.nerc.ac.uk/id/eprint/526047/1/Lake_Ohrid.pdf#page=4"
    if study_id == "13666":
        return "published_calibrated_radiocarbon", "Archived CLAM radiocarbon-based age-depth model, calendar yr BP /1000; no recalibration or age-model fitting.", "NOAA file Chronology_Information / Chronology_Notes"
    return "published_calendar_multi_method", "Archived calendar yr BP /1000. Published model uses 210Pb, calibrated 14C and tephrochronology as applicable; source header pools control-point information. No per-sample uncertainty inferred.", "https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2017PA003298#section-3"


def curate(fetch=False):
    """Return ready-to-merge fragment and audit, without changing canonical seed."""
    contract = json.loads(SOURCE_CONTRACT.read_text(encoding="utf8"))
    records, series, quarantined, manifest, study_reports = [], [], [], [], []
    inventory = json.loads((ROOT / "data/processed/inventory-v2.json").read_text(encoding="utf8"))
    inventory_ids = {r["id"] for r in inventory["records"]}
    existing = json.loads((ROOT / "data/processed/atlas-v1.json").read_text(encoding="utf8"))
    existing_hashes = {r.get("raw_sha256") or r.get("source_sha256") for r in existing["records"]}
    existing_dois = {str(r.get("dataset_doi", "")).lower() for r in existing["records"]}
    for cfg in contract["studies"]:
        sid = cfg["study_id"]
        metadata_raw = read_verified(sid + ".json", cfg["metadata_url"], cfg["metadata_sha256"], fetch)
        study = json.loads(metadata_raw)["study"][0]
        cr = json.loads(read_verified(cfg["crossref_file"], cfg["crossref_url"], cfg["crossref_sha256"], fetch))["message"]
        pub = study["publication"][0]
        if cr["DOI"].lower() != pub["identifier"]["id"].lower():
            raise ValueError("Crossref identity does not match native publication DOI")
        year = cr["published"]["date-parts"][0][0]
        dataset_doi = study["doi"].removeprefix("https://doi.org/")
        if dataset_doi.lower() in existing_dois:
            raise ValueError(f"Dataset already in seed: {dataset_doi}")
        status, chronology, chronology_evidence = chronology_for(sid)
        by_site = {}
        missing_cells, value_count = 0, 0
        for file in cfg["files"]:
            site, table = next((st, t) for st in study["site"] for t in st["paleoData"]
                               if str(st["NOAASiteId"]) == file["site_id"] and str(t["NOAADataTableId"]) == file["table_id"])
            record_id = f"noaa-{sid}-{file['site_id']}"
            inventory_id = f"noaa:{sid}:{file['site_id']}"
            if inventory_id not in inventory_ids:
                raise ValueError(f"Not a linked inventory site: {inventory_id}")
            if record_id not in by_site:
                props = site["geo"]["properties"]
                lat, lon = float(props["southernmostLatitude"]), float(props["westernmostLongitude"])
                if not (28 <= lat <= 48 and -10 <= lon <= 42):
                    raise ValueError("Source point is outside configured pilot scope")
                name = site["siteName"]
                qc = ["One source site record can contain multiple tables; table count does not imply independent cores.",
                      "Archived age model retained; sample-specific age and value uncertainties are unknown unless explicitly supplied."]
                if sid == "28070":
                    qc += ["Orbital tuning creates a dependency on climate-sensitive proxies; do not infer independent orbital synchrony.",
                           "NOAA bibliography uses 2019; Crossref issue/publication year is 2020. Filter uses 2020; both preserved.",
                           "XRF ratio is labelled Ti/Ti+K natively; paper also discusses Ti/K. Preserve original numbers and label, do not recompute the ratio."]
                if sid == "32914":
                    qc += ["SST uses Conte et al. 2006, not Müller et al. 1998; compatibility groups remain separate.",
                           "Native core Note can abbreviate INV12-15 as IN12-15; source site/table IDs govern linkage."]
                if sid == "13666":
                    qc.append("Two Bourget cores share rounded site coordinates and correlated chronology; retain distinct source IDs, not independent spatial replication.")
                by_site[record_id] = dict(id=record_id, name=name, core=name, site=name,
                    realm="marine" if sid == "32914" else "lake", archive_type="marine sediment" if sid == "32914" else "lake sediment",
                    latitude=lat, longitude=lon, provider="NOAA WDS Paleoclimatology", source="noaa_wds_paleo",
                    source_id=sid, source_site_id=file["site_id"], inventory_ids=[inventory_id],
                    dataset_doi=dataset_doi, dataset_title=study["studyName"], paper_doi=cr["DOI"],
                    paper_title=cr["title"][0], paper_year=year, publication_year=year,
                    publication_year_native=pub["pubYear"], publication_year_basis="Crossref published date-parts, contrasted with native NOAA bibliography",
                    authors=study["investigators"], source_url=study["onlineResourceLink"], study_url=study["onlineResourceLink"],
                    license="NOAA WDS open archive; citation requested; no record-specific Creative Commons license supplied",
                    license_url=POLICY, data_license_original=study.get("dataLicenseDescription"),
                    data_license_url_original=study.get("dataLicenseUrl"),
                    rights_basis="NOAA contribution policy makes WDS data freely and permanently available without restrictions; specific record license remains undeclared.",
                    age_model=chronology, time_scale="calendar BP (1950)", age_scale="calendar BP (1950)", chronology_status=status,
                    chronology_evidence=chronology_evidence, review_status="native_cells_units_chronology_and_article_identity_checked; independent chronology review pending",
                    qc_notes=qc, raw_sha256=None, metadata_sha256=cfg["metadata_sha256"], source_files=[], method="Methods vary by series; see series metadata")
            record = by_site[record_id]
            raw = read_verified(file["filename"], file["url"], file["sha256"], fetch)
            if file["sha256"] in existing_hashes:
                raise ValueError("Exact source file already in baseline seed")
            header, data, definitions = read_table(raw)
            # The sand file uses a capital S in the table and lower-case s in
            # its variable definition. This exact documented alias is reviewed.
            if file["filename"] == "panagiotopoulos2019-sand.txt":
                definitions["Sand%"] = definitions["sand%"]
            age_column, age_factor = ("age_ka", 1.0) if sid == "28070" else (("Age", .001) if sid == "32914" else ("age_calBP", .001))
            age_definition = definitions[age_column]
            required_unit = "calendar kiloyear before present" if age_factor == 1.0 else "calendar year before present"
            if required_unit not in age_definition:
                raise ValueError("Age column does not explicitly document expected calendar unit")
            mapping = specs_for(file["filename"])
            row_report = dict(file=file["filename"], url=file["url"], sha256=file["sha256"], bytes=len(raw),
                              study_id=sid, site_id=file["site_id"], table_id=file["table_id"],
                              original_header=header, source_rows=len(data), age_column=age_column,
                              original_age_definition=age_definition, age_factor_to_ka=age_factor,
                              ignored_columns=[c for c in header if c not in {x["column"] for x in mapping} | {age_column}],
                              chronology_status=status, chronology_evidence=chronology_evidence)
            record["source_files"].append({k: row_report[k] for k in ("file", "url", "sha256", "table_id", "original_header")})
            for spec in mapping:
                column = spec["column"]
                if column not in header or column not in definitions:
                    raise ValueError(f"Reviewed column missing from schema: {column}")
                rows, missing, bad_range = [], 0, 0
                for source_row, source_line, cells in data:
                    value = numeric(cells[column])
                    if value is None:
                        missing += 1
                        continue
                    native_age = numeric(cells[age_column])
                    age = native_age * age_factor if native_age is not None else None
                    depth_column = "depth_m" if "depth_m" in cells else "Depth" if "Depth" in cells else None
                    rows.append([age, value, source_row, source_line, cells[age_column], cells[column], None, None,
                                 cells[depth_column] if depth_column else None])
                    if spec["unit"] == "%" and not 0 <= value <= 100:
                        bad_range += 1
                rows.sort(key=lambda r: math.inf if r[0] is None else r[0])
                ages = [r[0] for r in rows if r[0] is not None]
                # Source row remains identity; equal age/value can be independent
                # samples. Audit repetitions rather than silently dropping them.
                age_counts = Counter(ages)
                pair_counts = Counter((r[0], r[1]) for r in rows)
                compatibility = spec["method_id"] + ":" + spec["variable_id"]
                item = dict(id=f"{record_id}:{file['table_id']}:{slug(column)}", record_id=record_id,
                    proxy=spec["proxy"], label=spec["label"], unit=spec["unit"], family=spec["family"],
                    variable_id=spec["variable_id"], method_id=spec["method_id"], method=spec["method_id"].replace("_", " "),
                    evidence_type=spec["evidence_type"], compatibility_group=compatibility,
                    source_column=column, source_table_id=file["table_id"], source_url=file["url"],
                    data_url=file["url"], raw_sha256=file["sha256"], source_sha256=file["sha256"],
                    source_header_original=header, source_variable_definition=definitions[column],
                    source_age_definition=age_definition, age_unit_original=required_unit,
                    age_scale="calendar BP (1950)", chronology_status=status, age_model=chronology,
                    age_min_ka_bp=min(ages) if ages else None, age_max_ka_bp=max(ages) if ages else None,
                    uncertainty_type="unknown; no per-sample uncertainty assigned", depth_frame="m composite depth" if sid == "28070" else "cm sediment depth" if sid == "32914" else None,
                    transformations=["Original numeric proxy values unchanged", "age_ka_bp=age_original/1000" if age_factor != 1 else "Age already calendar ka BP; no numerical age transformation", "Trim schema labels and discard only trailing empty tab fields", "Sort by age for display; original row and physical line preserved"],
                    qc_notes=["Missing source values excluded from observations, not imputed", "Same calendar age is not a unique sample identity"],
                    missing_value_cells=missing, values_missing_age=sum(r[0] is None for r in rows),
                    source_error_cells=sum(cells[column].strip() == "#DIV/0!" for _, _, cells in data),
                    out_of_range_percent_cells=bad_range,
                    repeated_age_observations=sum(n-1 for n in age_counts.values()),
                    repeated_age_value_pairs=sum(n-1 for n in pair_counts.values()), rows=rows)
                if column.endswith("-pine"):
                    item["denominator"] = "pollen sum excluding Pinus; native source definition preserved"
                elif "pollen" in file["filename"] and spec["unit"] == "%":
                    item["denominator"] = "native pollen group denominator including Pinus; source definition preserved"
                if bad_range:
                    # Do not clip or silently discard high percentage values.
                    # The entire series remains in staging until the source
                    # estimate/denominator can be independently resolved.
                    item["review_status"] = "quarantined_percentage_outside_0_100"
                    quarantined.append(item)
                    continue
                item["review_status"] = "native_cells_units_and_age_scale_checked"
                series.append(item)
                missing_cells += missing
                value_count += len(rows)
            manifest.append(row_report)
        for record in by_site.values():
            own = [s for s in series if s["record_id"] == record["id"]]
            ages = [r[0] for s in own for r in s["rows"] if r[0] is not None]
            record.update(age_min_ka_bp=min(ages), age_max_ka_bp=max(ages), proxies=sorted({s["proxy"] for s in own}),
                          observation_count=sum(len(s["rows"]) for s in own),
                          values_missing_age=sum(s["values_missing_age"] for s in own))
            if len(record["source_files"]) == 1:
                record["raw_sha256"] = record["source_files"][0]["sha256"]
                record["data_url"] = record["source_files"][0]["url"]
            records.append(record)
        study_reports.append(dict(study_id=sid, paper_doi=cr["DOI"], paper_year=year, publication_year_native=pub["pubYear"],
                                  records=len(by_site), observations=value_count, missing_cells_excluded=missing_cells))
    ids = [r["id"] for r in records] + [s["id"] for s in series]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate stable identity")
    result = dict(version="noaa-quantitative-v3-2026-10-28", row_format=ROW_FORMAT, records=records, series=series,
                  quarantined_series=quarantined)
    audit = dict(version=result["version"], accessed_on=contract["accessed_on"], studies=study_reports,
        counts=dict(records=len(records), series=len(series), observations=sum(len(s["rows"]) for s in series)),
        source_files=manifest, duplicate_review=dict(exact_source_hashes_against_v1="none", exact_dataset_DOIs_against_v1="none",
            physical_core_fusion="none inferred; exact NOAA source site IDs retained", cross_provider_review="Required by integrating assembler before counting spatial replicates"),
        quarantined_series=[{k: s[k] for k in ("id", "source_column", "raw_sha256", "source_url", "out_of_range_percent_cells", "review_status")} for s in quarantined],
        excluded_candidates=[dict(study_id="12909", name="Lake Cadagno", reason="Source supplies age_top_calBP and age_bot_calBP intervals. Downloaded but not ingested: compact point representation requires explicit interval/midpoint support, no implicit midpoint."),
                             dict(study_id="28070", columns="Pollen concentration columns, E-T400 biodiversity indices, predicted biome", reason="Outside first reviewed mapping or nonnumeric class; originals preserved and not fabricated as observations")],
        limitations=["Record-specific NOAA license fields are null; NOAA policy basis documented, no invented CC0.",
                     "No age model refit, 14C recalibration, chronological interpolation, smoothing or climate calibration computed.",
                     "One core can contain reconstructions with multiple calibrations. They remain separate groups, not independent observations.",
                     "Ohrid source has tuned ages and must not be used as independent evidence of orbital synchrony.",
                     "Per-sample uncertainty remains unknown. Published method precision is not substituted for each sample's uncertainty."])
    return result, audit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Fetch missing exact sources; default offline")
    args = parser.parse_args()
    fragment, report = curate(args.fetch)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(fragment, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    AUDIT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps(report["counts"]))
