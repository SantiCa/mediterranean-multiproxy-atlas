"""Acquire a small explicit SST expansion from citable PANGAEA records.

Source-native ages/values are preserved. No interpolation or calibration is done.
Run from the project root; outputs are local staging artifacts for review.
"""
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[2] / "data/interim/v1_marine"
SOURCES = [
    (438371, "BS79-33", 2001, "10.1029/2000PA000502"),
    (438379, "BS79-38", 2001, "10.1029/2000PA000502"),
    (433068, "160-967D", 2000, "10.1016/S0031-0182(00)00053-5"),
    (438794, "M25/4-KL11", 2000, "10.1016/S0031-0182(00)00053-5"),
    (438366, "AD91-17", 2001, "10.13130/2039-4942/5447"),
]


def main():
    records, observations, downloads = [], [], []
    (ROOT / "raw").mkdir(parents=True, exist_ok=True)
    for dataset_id, core, paper_year, paper_doi in SOURCES:
        url = f"https://doi.pangaea.de/10.1594/PANGAEA.{dataset_id}?format=textfile"
        req = urllib.request.Request(url, headers={"User-Agent": "MediterraneanMultiproxyAtlas/0.2"})
        with urllib.request.urlopen(req, timeout=45) as response:
            raw = response.read()
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type")
        sha = hashlib.sha256(raw).hexdigest()
        accessed = datetime.now(timezone.utc).isoformat()
        path = ROOT / "raw" / f"{dataset_id}.tsv"
        if path.exists() and path.read_bytes() != raw:
            raise RuntimeError(f"Source changed; retain existing bytes and review a new version: {path}")
        if not path.exists():
            path.write_bytes(raw)
        text = raw.decode("utf-8-sig")
        if not text.startswith("/* DATA DESCRIPTION:"):
            raise RuntimeError(f"Not a native PANGAEA table: {url}")
        header, table = text.split("*/", 1)
        if "Müller et al, 1998" not in header:
            raise RuntimeError(f"Calibration mismatch requires manual review: {dataset_id}")
        if "CC-BY-3.0" not in header:
            raise RuntimeError(f"License requires manual review: {dataset_id}")
        if paper_doi not in header:
            raise RuntimeError(f"Article relation not stated in native metadata: {dataset_id}")
        latitude = float(re.search(r"LATITUDE:\s*([-\d.]+)", header).group(1))
        longitude = float(re.search(r"LONGITUDE:\s*([-\d.]+)", header).group(1))
        elevation = float(re.search(r"ELEVATION:\s*([-\d.]+)", header).group(1))
        citation = re.search(r"Citation:\s*(.+)", header).group(1)
        comment_match = re.search(r"Comment:\s*(.+)", header)
        source_comment = comment_match.group(1) if comment_match else None
        age_scale = "ka BP as archived; age-model calibration not independently audited"
        rec = dict(record_id=f"pangaea-{dataset_id}", dataset_id=dataset_id, core=core,
                   title=citation, realm="marine", latitude=latitude, longitude=longitude,
                   water_depth_m=-elevation, elevation_m=None, provider="PANGAEA",
                   dataset_doi=f"10.1594/PANGAEA.{dataset_id}", source_url=url,
                   paper_doi=paper_doi, publication_year=paper_year,
                   dataset_publication_year=2006 if dataset_id == 438366 else paper_year,
                   paper_relation="related_to" if dataset_id == 438366 else "in_supplement_to",
                   license="CC-BY-3.0", license_url="https://creativecommons.org/licenses/by/3.0/",
                   proxy_id="alkenone_SST", proxy_label="Annual alkenone sea surface temperature",
                   unit="degC", kind="published_reconstruction",
                   calibration="Müller et al. (1998)", calibration_doi="10.1016/S0016-7037(98)00097-0",
                   calibration_source="PANGAEA parameter metadata, as archived",
                   seasonality="annual mean as archived",
                   compatibility_group="sst_alkenone_mueller1998_annual",
                   age_scale_status=age_scale, source_raw=path.relative_to(ROOT).as_posix(),
                   raw_sha256=sha, accessed_at_utc=accessed,
                   review_status="native_table_metadata_and_article_relation_verified",
                   source_comment=source_comment,
                   limitations=["Source age model retained; no age recalibration or uncertainty ensemble audit",
                                "SST is a published proxy reconstruction; no local calibration or error invented",
                                "Same calibration does not remove seasonal/ecological/sedimentary differences"])
        if source_comment:
            rec["limitations"].append(source_comment)
        lines = table.strip().splitlines()
        rows = list(csv.DictReader(lines, delimiter="\t"))
        sst_col = next(name for name in rows[0] if name.startswith("SST (1-12)"))
        for index, row in enumerate(rows, 1):
            age, value = float(row["Age [ka BP]"]), float(row[sst_col])
            source_line = next(i for i, line in enumerate(text.splitlines(), 1)
                               if line.startswith("Depth sed [m]")) + index
            observations.append(dict(record_id=rec["record_id"], proxy_id="alkenone_SST",
                                     age_ka_bp=age, value=value, unit="degC",
                                     depth_m=float(row["Depth sed [m]"]),
                                     source_row=index, source_line=source_line, source_column=sst_col,
                                     source_value=row[sst_col], source_age=row["Age [ka BP]"],
                                     age_scale_status=age_scale, uncertainty=None,
                                     compatibility_group=rec["compatibility_group"], raw_sha256=sha))
        rec.update(sample_count=len(rows), age_min_ka_bp=min(float(r["Age [ka BP]"]) for r in rows),
                   age_max_ka_bp=max(float(r["Age [ka BP]"]) for r in rows))
        records.append(rec)
        downloads.append(dict(dataset_id=dataset_id, requested_url=url, resolved_url=final_url,
                              content_type=content_type, sha256=sha, bytes=len(raw),
                              accessed_at_utc=accessed, path=path.relative_to(ROOT).as_posix()))
        print(f"{core}: {len(rows)} SST observations, {rec['age_min_ka_bp']}–{rec['age_max_ka_bp']} ka BP")
    output = dict(schema_version="v1_marine_staging_1", records=records, observations=observations,
                  transformations=["Metadata extraction and selected native column parsing only; no values rescaled"],
                  downloads=downloads)
    (ROOT / "marine_sst.json").write_text(json.dumps(output, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
