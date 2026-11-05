"""Append ten reviewed inland Reading v3 entities using the frozen v9 parser."""
import argparse
import json
import math

import build_forest_pollen_v9 as pollen

ROOT = pollen.ROOT
BASE = ROOT / 'data/processed/atlas-v9.json'
CONTRACT = ROOT / 'scripts/importers/pollen_v10_sources.json'


def build(fetch=False, *, baseline=BASE, contract_path=CONTRACT, version=10):
    """Build a pinned Reading-only child from a contract, parent and release number."""
    contract = json.loads(contract_path.read_bytes())
    if pollen.sha(baseline.read_bytes()) != contract['parent_sha256']:
        raise ValueError('Stale parent. Review overlaps before rebuilding the child.')
    if pollen.sha(pollen.CONTRACT.read_bytes()) != contract['parser_contract_sha256']:
        raise ValueError('Reading parser contract changed; review before rebuilding the child.')
    previous = json.loads(pollen.CONTRACT.read_bytes())
    entities = contract['reading_entities']
    names = {entry['entity'] for entry in entities}
    if not 1 <= len(entities) <= 10 or len(names) != len(entities):
        raise ValueError('Expected at most ten distinct reviewed entities')
    if names & {entry['entity'] for entry in previous['reading_entities']}:
        raise ValueError('Entity already admitted in v9')
    resources = {entry['file']: entry for entry in previous['resources']}
    for filename in ('iberia.csv', 'iberia-readme.docx'):
        pollen.original(resources[filename], fetch)
    parent = json.loads(baseline.read_bytes())
    if names & {series.get('source_event') for series in parent['series']}:
        raise ValueError('Entity already present in parent')
    records, series, audit = pollen.reading(
        resources['iberia.csv'], dict(previous, reading_entities=entities))
    notes = {entry['entity']: entry.get('qc_notes', []) for entry in entities}
    for item in records + series:
        entity_notes = notes[item.get('core') or item['source_event']]
        if entity_notes:
            item['qc_notes'] = item['qc_notes'] + entity_notes
    for record in records:
        if record['core'] in ('MAI', 'MOLINAES'):
            record['qc_notes'].append(
                'Reading v3 corrige el tratamiento de fechas postmodernas del techo '
                'respecto de v2. Se usa exclusivamente la mediana de v3, sin restaurar v2.')
    for entry, record in zip(audit, records):
        nearest = min(parent['records'], key=lambda old: math.hypot(
            record['latitude'] - old['latitude'], record['longitude'] - old['longitude']))
        distance = math.hypot(record['latitude'] - nearest['latitude'],
                              record['longitude'] - nearest['longitude'])
        if distance == 0:
            raise ValueError('Coincident parent location requires identity review')
        entry['nearest_parent'] = dict(record_id=nearest['id'], name=nearest['name'],
            angular_distance_degrees=distance,
            status='Screening only; proximity does not establish physical identity')
    fragment = dict(records=records, series=series, pending=contract['held'])
    path = pollen.RAW / f'forest_pollen_v{version}_curated.json'
    path.write_text(json.dumps(fragment, ensure_ascii=False), encoding='utf8')
    seed, report = pollen.admission.assemble(
        baseline=baseline, fragment_paths=[path], provider_names=[f'reading_pollen_v{version}'],
        version_prefix=f'atlas-quantitative-2026-11-05-v{version}-')
    if report['counts']['new_records'] != len(entities) or report['counts']['new_series'] != 6 * len(entities):
        raise ValueError('Admission quarantined a reviewed entity or series; inspect duplicates')
    raw = json.dumps(seed, ensure_ascii=False, separators=(',', ':')).encode()
    report.update(parent_sha256=contract['parent_sha256'], sha256=pollen.sha(raw), bytes=len(raw),
        chronology_and_denominator_audit=audit, held=contract['held'],
        source_audits=[contract_path.relative_to(ROOT).as_posix(),
                       'scripts/importers/pollen_v9_sources.json'],
        resources=[resources[name] for name in ('iberia.csv', 'iberia-readme.docx')])
    (ROOT / f'data/processed/atlas-v{version}.json').write_bytes(raw)
    (ROOT / f'reports/quantitative_v{version}_release.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    return seed, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='Restore absent pinned Reading originals')
    args = parser.parse_args()
    _, report = build(args.fetch)
    print(json.dumps({key: report[key] for key in ('version', 'counts')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
