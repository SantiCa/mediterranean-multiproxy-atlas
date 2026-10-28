"""Assemble curated source extractions into the atlas seed and a SQLite database.

Run source importers first. This assembler never estimates ages or proxy values.
The public compact row format is [age_ka, value, source_row, source_line,
original_age, original_value]. Full source metadata lives on records and series.
"""
import argparse
from collections import defaultdict
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
from prepare_seed import read_table

ROOT = Path(__file__).resolve().parents[1]
LABELS = {
    "alkenone_SST": ("SST · alquenonas", "°C", "sst_alkenone_mueller1998_annual"),
    "MgCa_SST": ("SST · Mg/Ca corregido", "°C", "sst_mgca_published"),
    "speleothem_d18O": ("δ¹⁸O · espeleotema", "‰ VPDB", "speleothem_d18O_vpdb"),
    "speleothem_d13C": ("δ¹³C · espeleotema", "‰ VPDB", "speleothem_d13C_vpdb"),
    "D50_noncarbonate": ("D50 · fracción no carbonatada", "µm", "D50_noncarbonate"),
    "UP10_noncarbonate": ("Fracción >10 µm", "%", "UP10_noncarbonate"),
    "silt_clay_noncarbonate": ("Limo / arcilla", "cociente", "silt_clay_noncarbonate"),
    "G_bulloides_MgCa_archived": ("Mg/Ca · G. bulloides", "mmol/mol", "G_bulloides_MgCa_archived"),
    "G_bulloides_MgCa_corrected": ("Mg/Ca · corregido", "mmol/mol", "G_bulloides_MgCa_corrected"),
    "BHT_isomer_per_TOC": ("BHT / TOC", "µg/g TOC", "BHT_isomer_per_TOC"),
    "ladderane_per_OC": ("Ladderanos / OC", "ng/g OC", "ladderane_per_OC"),
    "G_muellerae_relative_abundance": ("G. muellerae · abundancia relativa", "%", "G_muellerae_relative_abundance"),
    "coccolith_absolute_abundance": ("Cocolitos · abundancia absoluta", "10⁶/g", "coccolith_absolute_abundance"),
}


def assemble():
    records, grouped = {}, defaultdict(list)
    old_catalog = json.loads((ROOT / "data/processed/catalog.json").read_text(encoding="utf-8"))
    old_obs = json.loads((ROOT / "data/processed/observations.json").read_text(encoding="utf-8"))
    native_tables={r['dataset_id']:read_table(ROOT/f"data/raw/pangaea/{r['dataset_id']}.tsv")[1] for r in old_catalog}
    for record in old_catalog:
        key = f"pangaea-{record['dataset_id']}"
        records[key] = {**record, "id": key, "name": record["core"], "realm": "marine", "provider": "PANGAEA",
            "publication_year": record["paper_year"], "source_url": f"https://doi.pangaea.de/{record['dataset_doi']}",
            "qc_notes": [record["flags"]] if record["flags"] else [],
            "review_status": "native_table_and_metadata_verified; full chronology not audited"}
    for obs in old_obs:
        record_id = f"pangaea-{obs['dataset_id']}"
        grouped[(record_id, obs["proxy"])].append({**obs, "age_original": native_tables[obs['dataset_id']][obs['source_row']-1].get('Age [ka BP]'),
                                                  "value_original": obs["source_value"]})
    marine = json.loads((ROOT / "data/interim/v1_marine/marine_sst.json").read_text(encoding="utf-8"))
    for record in marine["records"]:
        records[record["record_id"]] = {**record, "id": record["record_id"], "name": record["core"],
                                       "qc_notes": record["limitations"], "source_url": record["source_url"]}
    for obs in marine["observations"]:
        grouped[(obs["record_id"], obs["proxy_id"])].append({**obs, "age_original": obs["source_age"], "value_original": obs["source_value"]})
    continental = json.loads((ROOT / "data/interim/v1_continental/continental_seed.json").read_text(encoding="utf-8"))
    for record in continental["records"]:
        records[record["id"]] = {**record, "source_url": record["data_url"],
                                "raw_sha256": record["source_sha256"], "review_status": "repository_table_and_paper_relation_verified"}
    for obs in continental["observations"]:
        grouped[(obs["record_id"], obs["proxy"])].append(obs)
    series = []
    for (record_id, proxy), observations in grouped.items():
        label, unit, compatibility = LABELS[proxy]
        rows = [[r.get("age_ka_bp"), r["value"], r["source_row"], r.get("source_line"),
                 r.get("age_original"), r.get("value_original", r.get("source_value")),
                 r.get('age_uncertainty_ka'),r.get('value_uncertainty'),r.get('depth_original',r.get('depth_source_value',str(r['depth_m']) if r.get('depth_m') is not None else None))] for r in observations]
        rows.sort(key=lambda row: float('inf') if row[0] is None else row[0])
        first = observations[0]
        series.append(dict(id=f"{record_id}:{proxy}", record_id=record_id, proxy=proxy,
                           label=label, unit=unit, compatibility_group=compatibility,
                           method=first.get("method", records[record_id].get("method", records[record_id].get("calibration", "As archived"))),
                           source_column=first.get("source_column"), uncertainty_type=first.get('uncertainty_type',first.get('value_uncertainty_type')),
                           depth_frame=first.get('depth_reference',first.get('depth_unit_original')),rows=rows))
    return dict(version="atlas-v1-2026-10-28-r2", row_format=["age_ka_bp", "value", "source_row", "source_line", "age_original", "value_original","age_uncertainty_ka","value_uncertainty","depth_original"],
                records=list(records.values()), series=series)


def write_sqlite(seed, path, migration_dir):
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite existing database: {path}. Choose a new output path.")
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("PRAGMA foreign_keys=ON")
        for migration in sorted(migration_dir.glob("*.sql")):
            db.executescript(migration.read_text(encoding="utf-8"))
        for r in seed["records"]:
            db.execute("INSERT INTO atlas_records VALUES(?,?,?,?,?,?)", (r["id"],r["name"],r["realm"],r["latitude"],r["longitude"],json.dumps(r,ensure_ascii=False)))
        for s in seed["series"]:
            meta={k:v for k,v in s.items() if k!='rows'}
            db.execute("INSERT INTO atlas_series VALUES(?,?,?,?,?,?)",(s["id"],s["record_id"],s["proxy"],s["label"],s["unit"],json.dumps(meta,ensure_ascii=False)))
            db.executemany("INSERT INTO atlas_observations VALUES(?,?,?,?,?,?,?,?,?,?,?)",[(f"{s['id']}:{row[2]}",s['id'],*row) for row in s['rows']])
        db.execute("INSERT INTO atlas_releases VALUES(?,?,?)", (seed['version'],sum(len(s['rows']) for s in seed['series']), '2026-10-28'))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--site-dir",type=Path)
    parser.add_argument("--sqlite",type=Path)
    parser.add_argument("--from-seed",action='store_true',help='Use the versioned compact seed without re-running source extraction')
    args=parser.parse_args()
    seed=json.loads((ROOT/'data/processed/atlas-v1.json').read_text(encoding='utf-8')) if args.from_seed else assemble()
    raw=json.dumps(seed,ensure_ascii=False,separators=(',',':')).encode()
    target=ROOT/'data/processed/atlas-v1.json'
    target.write_bytes(raw)
    if args.site_dir:
        (args.site_dir/'data').mkdir(exist_ok=True)
        (args.site_dir/'data/seed.json').write_bytes(raw)
    if args.sqlite:
        write_sqlite(seed,args.sqlite,args.site_dir/'drizzle' if args.site_dir else ROOT/'migrations')
    print(json.dumps(dict(records=len(seed['records']),series=len(seed['series']),observations=sum(len(s['rows']) for s in seed['series']),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())))
