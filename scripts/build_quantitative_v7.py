"""Build and report coverage for the reviewed four-proxy batch over v6."""
import hashlib
import json
from pathlib import Path
import re

import build_quantitative_v5 as admission

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/processed/atlas-v6.json'
RAW = ROOT / 'data/interim/four_v7'
FRAGMENTS = [RAW / 'pangaea_curated.json', RAW / 'zenodo_curated.json']
RELEASE = ROOT / 'data/processed/atlas-v7.json'


def coverage(seed):
    """Count coverage by requested family. This is not a map-compatibility key."""
    records = {r['id']: r for r in seed['records']}
    # Verified lake archives inherited from a release that did not classify
    # their realm. Both Ohrid event labels refer to the published DEEP sequence.
    lakes = {'pangaea6-co1215': 'Prespa', 'pangaea5-icdp5045_1': 'Ohrid DEEP',
             'pangaea7-ohrid': 'Ohrid DEEP'}
    groups = {name: [] for name in ('Ti/Ca', 'Fe/Al', 'sortable silt mean', 'sortable silt %', 'forest pollen %')}
    for series in seed['series']:
        parameter = series.get('comparison_parameter_name') or series.get('parameter_name_pangaea') or ''
        label = series['label']
        if not any(row[0] is not None for row in series['rows']):
            continue
        if parameter == 'Titanium/Calcium ratio':
            key = 'Ti/Ca'
        elif parameter == 'Iron/Aluminium ratio':
            key = 'Fe/Al'
        elif re.search(r'sortable.silt', parameter + ' ' + label, re.I):
            if series['unit'] == '%':
                key = 'sortable silt %'
            elif series['unit'] in ('µm', 'μm'):
                key = 'sortable silt mean'
            else:
                continue
        elif (series['unit'] == '%' and (records[series['record_id']]['realm'] == 'continental' or series['record_id'] in lakes)
              and re.search(r'arboreal pollen|pollen, (?:temperate|boreal|mediterranean|mesophilous)|\b(?:pinus|fagus|quercus|abies|picea)\b', parameter, re.I)
              and not re.search(r'^non[- ]arboreal', parameter, re.I)):
            key = 'forest pollen %'
        else:
            continue
        groups[key].append(series)
    result = {}
    for key, group in groups.items():
        ids = sorted({s['record_id'] for s in group})
        # This reporting precision treats the two co-located Alboran deployments
        # as one location while preserving both original coordinates and event IDs.
        sites = {lakes.get(i, (round(records[i]['latitude'], 4), round(records[i]['longitude'], 4))) for i in ids}
        result[key] = dict(records=len(ids), locations=len(sites), series=len(group),
                           values=sum(len(s['rows']) for s in group), record_ids=ids)
    return result


def main():
    raw_parent = BASE.read_bytes()
    parent_hash = hashlib.sha256(raw_parent).hexdigest()
    for path in FRAGMENTS:
        if json.loads(path.read_bytes())['parent_sha256'] != parent_hash:
            raise ValueError(f'{path.name} has a stale v6 parent')
    seed, report = admission.assemble(baseline=BASE, fragment_paths=FRAGMENTS,
                                      provider_names=['pangaea', 'zenodo'],
                                      version_prefix='atlas-quantitative-2026-11-04-v7-')
    raw = json.dumps(seed, ensure_ascii=False, separators=(',', ':')).encode()
    report.update(parent_sha256=parent_hash, sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                  source_audits=['reports/four_v7_pangaea_audit.json', 'scripts/importers/four_v7_sources.json'],
                  coverage_before=coverage(json.loads(raw_parent)), coverage_after=coverage(seed),
                  coverage_scope='Coordinates rounded to 4 decimals. The two documented event labels for the Ohrid DEEP sequence count as one site. Methods, units and denominators remain separate for map compatibility.')
    RELEASE.write_bytes(raw)
    (ROOT / 'reports/quantitative_v7_release.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({key: report[key] for key in ('version', 'counts', 'coverage_before', 'coverage_after')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
