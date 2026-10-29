"""Assemble reviewed append-only quantitative release, preserving v1 immutable baseline.

The input curators own column contracts. This integration checks observation
identity, duplicate fingerprints, coordinates, units and metadata consistency;
it never recalibrates chronology or estimates missing measurements.
"""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
import math
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
VERSION="atlas-quantitative-2026-10-29-v3-r1"
FAMILIES={"temperature":"Temperatura","biomarkers":"Biomarcadores",
          "stable_isotopes":"Isótopos estables","geochemistry":"Geoquímica elemental"}
OLD_FAMILY={
"alkenone_SST":"Temperatura","MgCa_SST":"Temperatura",
"speleothem_d18O":"Isótopos estables","speleothem_d13C":"Isótopos estables",
"D50_noncarbonate":"Sedimentología","UP10_noncarbonate":"Sedimentología",
"silt_clay_noncarbonate":"Sedimentología","G_bulloides_MgCa_archived":"Geoquímica elemental",
"G_bulloides_MgCa_corrected":"Geoquímica elemental","BHT_isomer_per_TOC":"Biomarcadores",
"ladderane_per_OC":"Biomarcadores","G_muellerae_relative_abundance":"Micropaleontología",
"coccolith_absolute_abundance":"Micropaleontología"}
CHRONOLOGY_LABELS={
"legacy_archived":"Piloto · edad BP archivada",
"published_BP":"BP publicado · escala no armonizada",
"published_CE":"Calendario CE convertido a BP",
"published_varve_BP":"Edad varvada BP",
"orbital_tuning":"Edad ajustada orbitalmente",
"published_calendar_multi_method":"Calendario publicado · controles mixtos",
"published_calibrated_radiocarbon":"Calendario publicado · 14C calibrado"}

def digest(value):
    """Deterministic fingerprint of the full reviewed object, never fuzzy matching."""
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,separators=(",",":"),sort_keys=True).encode()).hexdigest()

def finite(value):
    """Reject nonnumeric and nonfinite cells while preserving real zero and signs."""
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def normalize_core(name):
    """Exact normalized names flag review candidates; never merge physical cores."""
    return re.sub(r"[^a-z0-9]","",str(name).lower())

def enrich(seed):
    """Add facets/counts without altering observations or compatibility contracts."""
    records={r["id"]:r for r in seed["records"]}
    for s in seed["series"]:
        r=records[s["record_id"]]
        s["family"]=FAMILIES.get(s.get("family"),s.get("family")) or OLD_FAMILY.get(s["proxy"],"Otros")
        s["variable_id"]=s.get("variable_id",s.get("variable",s["proxy"]))
        # Shared human labels may guide selection, but the compatibility key
        # still includes proxy ID, explicit method/calibration group and unit.
        s["variable_label"]=("Temperatura superficial del mar" if "SST" in s["proxy"]
          else "δ18O" if "d18O" in s["proxy"] else "δ13C" if "d13C" in s["proxy"]
          else s["label"].split(" · ")[0])
        if not s.get("chronology_status"):
            native=r.get("chronology_status","")
            s["chronology_status"]=("published_CE" if "CE" in s.get("age_transformation","")
              else "published_varve_BP" if "varve" in s.get("age_column_original","").lower()
              else "published_BP" if native else "legacy_archived")
        s["chronology_label"]=CHRONOLOGY_LABELS.get(s["chronology_status"],s["chronology_status"])
        s.setdefault("evidence_type","published_reconstruction" if "SST" in s["proxy"] else "published_value")
        ages=[row[0] for row in s["rows"] if finite(row[0])]
        s.update(observation_count=len(s["rows"]),age_min_ka_bp=min(ages) if ages else None,
                 age_max_ka_bp=max(ages) if ages else None,age_missing_count=sum(row[0] is None for row in s["rows"]))
        s["search_aliases"]=[s["proxy"],s["variable_id"],s["compatibility_group"],s.get("taxon",""),
                             "SST temperatura temperature" if "SST" in s["proxy"] else ""]
    return seed

def assemble():
    """Return a release and audit from immutable baseline and curated fragments."""
    baseline=json.loads((ROOT/"data/processed/atlas-v1.json").read_text(encoding="utf8"))
    seed=copy.deepcopy(baseline)
    fragments=[json.loads((ROOT/f"data/interim/quantitative_v3/{provider}_curated.json").read_text(encoding="utf8"))
               for provider in ("pangaea","noaa")]
    record_ids={r["id"] for r in seed["records"]};series_ids={s["id"] for s in seed["series"]}
    original={s["id"]:digest(s["rows"]) for s in baseline["series"]}
    fingerprints=defaultdict(list)
    for s in seed["series"]:
        fingerprints[(s["unit"],digest(sorted([[x[0],x[1]] for x in s["rows"]],key=lambda x:(x[0] is None,x[0] or 0,x[1]))))].append(s["id"])
    rejected=[];matches=[]
    for fragment in fragments:
        for r in fragment["records"]:
            if r["id"] in record_ids:raise ValueError("Existing record ID reused: "+r["id"])
            if not (finite(r["latitude"]) and finite(r["longitude"]) and -90<=r["latitude"]<=90 and -180<=r["longitude"]<=180):
                raise ValueError("Invalid coordinates: "+r["id"])
            record_ids.add(r["id"]);seed["records"].append(copy.deepcopy(r))
        for s in fragment["series"]:
            if s["id"] in series_ids:raise ValueError("Existing series ID reused: "+s["id"])
            if not s.get("unit") or not s.get("compatibility_group"):raise ValueError("Missing comparison contract")
            if s["record_id"] not in record_ids:raise ValueError("Orphan series")
            rows=s["rows"]
            if not rows or len({r[2] for r in rows})!=len(rows):raise ValueError("Non-unique source-row identity: "+s["id"])
            if any(len(r)!=9 or not finite(r[1]) or (r[0] is not None and not finite(r[0])) for r in rows):raise ValueError("Invalid compact observation")
            fp=(s["unit"],digest(sorted([[x[0],x[1]] for x in rows],key=lambda x:(x[0] is None,x[0] or 0,x[1]))))
            if len(rows)>=10 and fingerprints.get(fp):
                # Exact full-vector identity is a quarantine trigger, not an
                # assertion that equal coordinates identify the same core.
                rejected.append({"series":s["id"],"reason":"exact_complete_numeric_vector_matches_existing","matches":fingerprints[fp]})
                continue
            fingerprints[fp].append(s["id"]);series_ids.add(s["id"]);seed["series"].append(copy.deepcopy(s))
    used={s["record_id"] for s in seed["series"]}
    seed["records"]=[r for r in seed["records"] if r["id"] in used]
    for r in seed["records"]:
        r["provider"]="NOAA WDS" if r["provider"].startswith("NOAA") else r["provider"]
        if r.get("inventory_links"):
            r["inventory_ids"]=r["inventory_links"]
    # Flag exact normalized core labels, dataset DOIs and coincident positions.
    # These are review links and never deduplicate on geography alone.
    for field,lookup in (("name",lambda r:normalize_core(r.get("core",r["name"]))),
                         ("dataset_doi",lambda r:str(r.get("dataset_doi") or "").lower()),
                         ("position",lambda r:(r["latitude"],r["longitude"]))):
        by=defaultdict(list)
        for r in seed["records"]:
            value=lookup(r)
            if value:by[value].append(r["id"])
        matches.extend({"basis":field,"records":ids,"status":"review_link_not_merged"} for ids in by.values() if len(ids)>1)
    for s in seed["series"]:
        if s["id"] in original and digest(s["rows"])!=original[s["id"]]:raise ValueError("Baseline numerical values changed")
    seed=enrich(seed);seed["version"]=VERSION
    seed["limitations"]=["Bounded reviewed batch, not all linked numerical datasets",
      "Published age models are retained; independent recalibration/chronology ensembles not implemented",
      "Observation counts are native finite cells, not independent samples",
      "Possible physical-core overlap remains explicit; matching positions alone never merge records"]
    ages=[row[0] for s in seed["series"] for row in s["rows"] if finite(row[0])]
    report={"version":VERSION,"baseline_version":baseline["version"],"baseline_unchanged":True,
      "counts":{"records":len(seed["records"]),"series":len(seed["series"]),"values":sum(len(s["rows"]) for s in seed["series"]),
       "new_records":len(seed["records"])-len(baseline["records"]),"new_series":len(seed["series"])-len(baseline["series"]),
       "new_values":sum(len(s["rows"]) for s in seed["series"])-sum(len(s["rows"]) for s in baseline["series"]),
       "missing_age_values":sum(s["age_missing_count"] for s in seed["series"])},
      "numeric_age_extent_ka_bp":[min(ages),max(ages)],
      "family_counts":dict(Counter(s["family"] for s in seed["series"])),
      "comparison_groups":len({(s["proxy"],s["compatibility_group"],s["unit"]) for s in seed["series"]}),
      "exact_vector_quarantine":rejected,"possible_overlap_links":matches,
      "source_audits":["reports/noaa_v3_audit.json","docs/curation/pangaea_v3.md"],
      "quarantined_series":[{"id":s["id"],"n":len(s["rows"]),"reason":s.get("quarantine_reason",s.get("review_status")),"out_of_range_percent_cells":s.get("out_of_range_percent_cells",0)}
                            for f in fragments for s in f.get("quarantined_series",[])]}
    return seed,report

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--site-dir",type=Path);args=p.parse_args()
    seed,report=assemble();raw=json.dumps(seed,ensure_ascii=False,separators=(",",":")).encode()
    (ROOT/"data/processed/atlas-v3.json").write_bytes(raw)
    if args.site_dir:(args.site_dir/"data/seed.json").write_bytes(raw)
    report["sha256"]=hashlib.sha256(raw).hexdigest();report["bytes"]=len(raw)
    (ROOT/"reports/quantitative_v3_release.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:report[k] for k in ("counts","comparison_groups","numeric_age_extent_ka_bp","bytes","sha256")}))
