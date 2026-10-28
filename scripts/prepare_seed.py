"""Create traceable long-form observations without interpolation or recalibration."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
from statistics import median

ROOT = Path(__file__).resolve().parents[1]


def read_table(path):
    text = path.read_text(encoding="utf-8-sig")
    end = text.index("*/") + 2
    meta = text[:end]
    reader = csv.DictReader(io.StringIO(text[end:].lstrip("\r\n")), delimiter="\t")
    if len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError(f"Duplicate column labels in {path}")
    rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError(f"Malformed TSV row in {path}")
    # TSV header is one physical line immediately after the metadata terminator.
    first_data_line = text[:end].count("\n") + 3
    return meta, rows, first_data_line


def number(value):
    if value is None or value.strip() == "":
        return None
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"Non-finite numeric cell: {value!r}")
    return result


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    config = json.loads((ROOT / "config/seed.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "data/provenance/downloads.json").read_text(encoding="utf-8"))
    checksums = {r["path"]: r["sha256"] for r in manifest}
    observations, catalog, warnings = [], [], []
    for dataset in config:
        dataset_id = dataset["id"]
        path = ROOT / f"data/raw/pangaea/{dataset_id}.tsv"
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        assert sha == checksums[path.relative_to(ROOT).as_posix()], f"Changed raw source: {path}"
        meta, rows, first_line = read_table(path)
        latitude = float(re.search(r"LATITUDE: ([\d.-]+)", meta)[1])
        longitude = float(re.search(r"LONGITUDE: ([\d.-]+)", meta)[1])
        water_depth = -float(re.search(r"ELEVATION: ([\d.-]+)", meta)[1])
        license_id = re.search(r"\((CC-BY-[\d.]+)\)", meta)[1]
        authors = meta.split("Citation:\t", 1)[1].split(" (", 1)[0]
        age_column = "Age [ka BP]" if "Age [ka BP]" in rows[0] else None
        ages = [number(r[age_column]) for r in rows if age_column and r[age_column]]
        positive_steps = [b - a for a, b in zip(ages, ages[1:]) if b > a]
        flags = []
        if not age_column:
            flags.append("no_age_column_depth_only")
        if any(a < 0 for a in ages):
            flags.append("negative_BP_age_preserved")
        if any(b < a for a, b in zip(ages, ages[1:])):
            flags.append("age_inversion_requires_review")
        if len(ages) != len(set(ages)):
            flags.append("duplicate_age_preserved")
        if dataset_id == 921230:
            flags.append("depth_header_m_vs_metadata_comment_cmbsf_conflict")
        if dataset_id == 898587:
            flags.append("section_bottom_zeros_preserved_no_geometry_inference")
        catalog.append(dict(dataset_id=dataset_id, core=dataset["core"], authors=authors,
                            dataset_doi=f"10.1594/PANGAEA.{dataset_id}", paper_doi=dataset["paper_doi"],
                            paper_year=dataset["paper_year"], dataset_citation_year=dataset["dataset_citation_year"],
                            latitude=latitude, longitude=longitude, water_depth_m=water_depth,
                            raw_rows=len(rows), selected_series=len(dataset["proxies"]), license=license_id,
                            age_min_ka_bp=min(ages) if ages else None,
                            age_max_ka_bp=max(ages) if ages else None,
                            median_positive_age_step_ka=median(positive_steps) if positive_steps else None,
                            age_scale_status="as_archived_calibration_not_audited" if age_column else "unavailable",
                            flags=";".join(flags), raw_sha256=sha))
        warnings.extend(dict(dataset_id=dataset_id, flag=f) for f in flags)
        for row_index, row in enumerate(rows, 1):
            for proxy in dataset["proxies"]:
                value = number(row[proxy["column"]])
                observations.append(dict(
                    observation_id=f"pangaea:{dataset_id}:row{row_index}:{proxy['proxy']}",
                    dataset_id=dataset_id, core=dataset["core"], source_row=row_index,
                    source_line=first_line + row_index - 1, source_column=proxy["column"],
                    source_value=row[proxy["column"]], value=value, unit=proxy["unit"],
                    proxy=proxy["proxy"], evidence_kind=proxy["kind"], method=proxy["method"],
                    depth_source_value=row[dataset["depth_column"]], depth_source_column=dataset["depth_column"],
                    depth_reference=dataset["depth_reference"],
                    age_ka_bp=number(row[age_column]) if age_column else None,
                    age_model_id=f"archived:{dataset_id}" if age_column else None,
                    age_calibration_status="as_archived_not_audited" if age_column else "unavailable",
                    age_uncertainty_ka=None,
                    value_uncertainty=number(row[proxy["uncertainty_column"]]) if proxy.get("uncertainty_column") else None,
                    uncertainty_type=proxy.get("uncertainty_type", "not_reported_in_selected_table"),
                    stratigraphic_label=row.get("Sapropel"), sample_label=row.get("Sample label"),
                    publication_year=dataset["paper_year"], dataset_citation_year=dataset["dataset_citation_year"],
                    paper_doi=dataset["paper_doi"], dataset_doi=f"10.1594/PANGAEA.{dataset_id}",
                    latitude=latitude, longitude=longitude, license=license_id, raw_sha256=sha,
                    transform_id="T001_extract_selected_columns_v1"))
    for name, data in (("observations", observations), ("catalog", catalog)):
        write_csv(ROOT / f"data/processed/{name}.csv", data)
        (ROOT / f"data/processed/{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    result = dict(datasets=len(catalog), cores=len({r["core"] for r in catalog}),
                  raw_sample_rows=sum(r["raw_rows"] for r in catalog),
                  selected_series=sum(r["selected_series"] for r in catalog), observations=len(observations),
                  dated_observations=sum(r["age_ka_bp"] is not None for r in observations),
                  null_values=sum(r["value"] is None for r in observations), warnings=warnings,
                  transformations=[dict(id="T001_extract_selected_columns_v1", action="Select columns; parse decimal strings to floats; attach archived age and provenance; do not alter raw text, normalize ages, interpolate, smooth, or impute")])
    out = ROOT / "reports/seed_audit.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
