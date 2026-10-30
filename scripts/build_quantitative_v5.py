"""v5: append the PANGAEA v5 contract batch to v4 (same admission gate as v4).

Append a reviewed batch to v3 without changing prior records or observations.

This assembler is a scientific admission gate, not a generic parser. Provider
curators own explicit source-column/age/unit contracts; originals stay immutable.
"""
import argparse
import copy
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
# Content-addressed suffix: D1 is append-only and keyed by release id, so any change of
# the v5 content must produce a new id (r1 kept for the first published content).
VERSION_PREFIX="atlas-quantitative-2026-10-29-v5-"
FIRST_SHA="3dfde3f8d3"
BASELINE=ROOT/"data/processed/atlas-v4.json"
spec=importlib.util.spec_from_file_location("v3_enrichment",ROOT/"scripts/build_quantitative_v3.py")
v3=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v3)

def digest(value):
    """Stable full-object fingerprint; no tolerance-based deduplication."""
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def core_key(record):
    """Normalized exact source core name for exclusion/review, never proximity."""
    return re.sub(r"[^a-z0-9]","",str(record.get("core") or record.get("source_event") or record["name"]).casefold())

def vector(series):
    """Exact age/value multiset preserves multiplicity, missing ages and zeros."""
    return sorted(((row[0],row[1]) for row in series["rows"]),key=lambda x:(x[0] is None,x[0] or 0,x[1]))

def quantity(series):
    """Only an identical declared variable and native unit can match here."""
    return (series.get("variable_id",series["proxy"]),series["unit"])

def assemble(baseline=None, fragment_paths=None, version_prefix=VERSION_PREFIX, provider_names=None):
    """Return immutable parent plus admitted new series and an inspectable audit."""
    base=json.loads(Path(baseline or BASELINE).read_text(encoding="utf8"))
    seed=copy.deepcopy(base)
    fragments=[json.loads(Path(path).read_text(encoding="utf8")) for path in (fragment_paths or [ROOT/"data/interim/quantitative_v5/pangaea_curated.json"])]
    providers=provider_names or ['pangaea']
    if len(fragments)!=len(providers):raise ValueError("One provider name is required per fragment")
    inventory=json.loads((ROOT/"data/processed/inventory-v2.json").read_text(encoding="utf8"))
    west,south,east,north=inventory['scope']['bbox']
    known_inventory={r["id"] for r in inventory["records"]}
    byrecord={r["id"]:r for r in base["records"]}
    oldcores={core_key(r):r["id"] for r in base["records"]}
    byseries={s["id"]:s for s in base["series"]}
    fingerprints=defaultdict(list)
    for s in base["series"]:
        fingerprints[(quantity(s),digest(vector(s)))].append(s["id"])
    admissions=[];quarantine=[];excluded_records=[];input_counts={};linked={}
    for provider,fragment in zip(providers,fragments):
        input_counts[provider]={"records":len(fragment["records"]),"series":len(fragment["series"]),"values":sum(len(s["rows"]) for s in fragment["series"])}
        incoming={r["id"]:copy.deepcopy(r) for r in fragment["records"]}
        if len(incoming)!=len(fragment["records"]):raise ValueError("Repeated physical-record ID in fragment")
        for r in incoming.values():
            if r["id"] in byrecord:raise ValueError("Existing record ID cannot be overwritten: "+r["id"])
            if not (west<=r["longitude"]<=east and south<=r["latitude"]<=north):raise ValueError("Outside declared region: "+r["id"])
            if not r.get("source_url"):raise ValueError("Missing native source URL")
            r["provider"]="NOAA WDS" if r["provider"].startswith("NOAA") else r["provider"]
            r["inventory_ids"]=r.get("inventory_ids",r.get("inventory_links",[]))
            if any(identifier not in known_inventory for identifier in r["inventory_ids"]):raise ValueError("Unresolved native inventory link: "+r["id"])
            if core_key(r) in oldcores:
                parent=byrecord[oldcores[core_key(r)]]
                # Vínculo v5: misma etiqueta de evento PANGAEA y coordenadas idénticas (±1e-4°) en ambos
                # registros PANGAEA = mismo evento del repositorio (identidad declarada, no proximidad).
                # Las series nuevas se cuelgan del registro padre sin modificarlo.
                if r["provider"]=="PANGAEA" and parent.get("provider")=="PANGAEA" and abs(parent["latitude"]-r["latitude"])<1e-4 and abs(parent["longitude"]-r["longitude"])<1e-4:
                    linked[r["id"]]=parent["id"];continue
                excluded_records.append({"id":r["id"],"matches":oldcores[core_key(r)],"reason":"normalized_exact_core_already_in_parent; held_for_linkage_review"})
        held={r["id"] for r in excluded_records}
        candidates=[]
        for source in fragment["series"]:
            s=copy.deepcopy(source)
            if s["record_id"] in linked:
                s["linked_from_record"]=s["record_id"];s["record_id"]=linked[s["record_id"]]
                s.setdefault("qc_notes",[]).append("Serie nueva enlazada a registro padre por evento PANGAEA idéntico (etiqueta+coordenadas)")
            if s["record_id"] in held:
                quarantine.append({"id":s["id"],"reason":"parent_core_identity_requires_linkage_review"});continue
            if s["id"] in byseries:raise ValueError("Series ID reused: "+s["id"])
            if s["record_id"] not in incoming and s["record_id"] not in linked.values():raise ValueError("Orphan incoming series")
            r=incoming.get(s["record_id"]) or incoming[s["linked_from_record"]]
            rows=s["rows"]
            if not rows or len({row[2] for row in rows})!=len(rows):raise ValueError("Source-row IDs are not unique")
            if any(len(row)!=9 or not v3.finite(row[1]) or (row[0] is not None and not v3.finite(row[0])) for row in rows):raise ValueError("Invalid compact observation")
            if not s.get("unit") or not s.get("compatibility_group") or not (s.get("raw_sha256") or r.get("raw_sha256")):raise ValueError("Missing units/comparison/provenance")
            if not (s.get("age_scale") or s.get("age_transformation") or r.get("age_scale_status") or r.get("time_scale")):raise ValueError("Missing age scale declaration")
            # Each selected source retains its own publication/license, including
            # explicit nulls; no first-table paper is inferred for another table.
            for field in ("dataset_doi","paper_doi","publication_year","license","license_url"):
                if field not in s:s[field]=r.get(field)
            if s["publication_year"] is not None and not 1800<=s["publication_year"]<=2026:raise ValueError("Publication year outside reviewed range")
            if not s.get("license"):raise ValueError("Missing documented reuse basis")
            fp=(quantity(s),digest(vector(s)))
            if len(rows)>=10 and fingerprints.get(fp):
                quarantine.append({"id":s["id"],"matches":fingerprints[fp],"reason":"exact_complete_variable_unit_vector_already_present"});continue
            fingerprints[fp].append(s["id"]);candidates.append(s);byseries[s["id"]]=s
        used={s["record_id"] for s in candidates}
        admitted_records=[r for r in incoming.values() if r["id"] in used]
        for r in admitted_records:
            if r['provider']=='PANGAEA':
                active_dois={s['dataset_doi'].casefold() for s in candidates if s['record_id']==r['id'] and s.get('dataset_doi')}
                original_links=r['inventory_ids']
                r['inventory_ids']=[identifier for identifier in original_links if not identifier.startswith('datacite:') or identifier.removeprefix('datacite:').casefold() in active_dois]
                r['held_quantitative_inventory_ids']=[identifier for identifier in original_links if identifier not in r['inventory_ids']]
        # Enrichment operates only on the new fragment; parent metadata is frozen.
        supplied={s['id']:{k:copy.deepcopy(s[k]) for k in ('chronology_label','variable_label','search_aliases') if k in s} for s in candidates}
        enriched=v3.enrich({"records":admitted_records+[copy.deepcopy(byrecord[x]) for x in set(linked.values())],"series":candidates})  # copias: el padre no se modifica
        for s in enriched["series"]:
            s.update(supplied[s['id']])
            byseries[s["id"]]=s;seed["series"].append(s);admissions.append(s["id"])
        for r in admitted_records:byrecord[r["id"]]=r;seed["records"].append(r)
    original={s["id"]:s for s in base["series"]}
    current={s["id"]:s for s in seed["series"]}
    if any(current[k]!=s for k,s in original.items()):raise ValueError("Parent series/metadata mutated")
    current_records={r["id"]:r for r in seed["records"]}
    if any(current_records[r["id"]]!=r for r in base["records"]):raise ValueError("Parent record metadata mutated")
    # Audit partial overlap separately. An equal age is not proof of duplication.
    overlaps=[]
    sets={s["id"]:set((row[0],row[1]) for row in s["rows"] if row[0] is not None) for s in seed["series"]}
    new=set(admissions);all_series=seed["series"]
    for index,a in enumerate(all_series):
        for b in all_series[index+1:]:
            if not ({a["id"],b["id"]}&new) or quantity(a)!=quantity(b):continue
            small=min(len(sets[a["id"]]),len(sets[b["id"]]))
            if small<10:continue
            shared=len(sets[a["id"]]&sets[b["id"]])
            if shared>=10 and shared/small>=.5:overlaps.append({"series":[a["id"],b["id"]],"exact_shared_pairs":shared,"fraction_of_smaller_unique_set":shared/small,"status":"review_link; not merged"})
    duplicates=[]
    for label,key in (("exact_core_name",core_key),("exact_position",lambda r:(r["latitude"],r["longitude"])),("dataset_doi",lambda r:r.get("dataset_doi"))):
        grouped=defaultdict(list)
        for r in seed["records"]:
            value=key(r)
            if value:grouped[value].append(r["id"])
        duplicates.extend({"basis":label,"records":ids,"status":"review_link; not merged"} for ids in grouped.values() if len(ids)>1)
    content_digest=hashlib.sha256(json.dumps([seed["records"],seed["series"]],ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:10]
    VERSION=version_prefix+("r1" if content_digest==FIRST_SHA else "c"+content_digest)
    seed.update(version=VERSION,parent_version=base["version"],append_series_ids=admissions)
    ages=[row[0] for s in seed["series"] for row in s["rows"] if row[0] is not None]
    counts={"records":len(seed["records"]),"series":len(seed["series"]),"values":sum(len(s["rows"]) for s in seed["series"]),"new_records":len(seed["records"])-len(base["records"]),"new_series":len(admissions),"new_values":sum(len(current[k]["rows"]) for k in admissions),"missing_age_values":sum(row[0] is None for s in seed["series"] for row in s["rows"])}
    report={"version":VERSION,"parent_version":base["version"],"parent_sha256":hashlib.sha256(BASELINE.read_bytes()).hexdigest(),"parent_unchanged":True,"counts":counts,"input_fragments":input_counts,"family_counts":dict(Counter(s["family"] for s in seed["series"])),"comparison_groups":len({(s["proxy"],s["compatibility_group"],s["unit"]) for s in seed["series"]}),"numeric_age_extent_ka_bp":[min(ages),max(ages)],"admitted_series":admissions,"integration_quarantine":quarantine,"held_core_records":excluded_records,"linked_to_parent_records":linked,"partial_numeric_overlap_links":overlaps,"possible_record_overlap_links":duplicates,"source_audits":["reports/pangaea_v5_audit.json"],"limitations":["Bounded reviewed batch, not a complete numerical harvest","Published chronologies retained; no independent recalibration. Series flagged interpolated_from_age_model take ages by linear depth interpolation from a published age model of the same PANGAEA event, without extrapolation","Exact and partial duplicates audited; positional/name similarity alone never establishes physical identity","Legacy v3 quality restrictions and quarantines remain in force"]}
    report['scope']=inventory['scope']
    report['provider_quarantines']={provider:[{k:v for k,v in s.items() if k not in ('rows','source_header_original')} for s in fragment.get('quarantined_series',[])] for provider,fragment in zip(providers,fragments)}
    report['pending_source_candidates']={provider:fragment.get('pending',fragment.get('rejected_candidates',[])) for provider,fragment in zip(providers,fragments)}
    return seed,report

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--site-dir",type=Path);a=p.parse_args()
    seed,report=assemble();raw=json.dumps(seed,ensure_ascii=False,separators=(",",":")).encode()
    (ROOT/"data/processed/atlas-v5.json").write_bytes(raw)
    if a.site_dir:(a.site_dir/"data/seed.json").write_bytes(raw)
    report["sha256"]=hashlib.sha256(raw).hexdigest();report["bytes"]=len(raw)
    (ROOT/"reports/quantitative_v5_release.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:report[k] for k in ("counts","comparison_groups","numeric_age_extent_ka_bp","sha256","bytes")}))
