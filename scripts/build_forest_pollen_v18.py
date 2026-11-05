"""Append two partially retained Reading v3 entities to the immutable v17 parent."""
import argparse
from collections import Counter
from decimal import Decimal
import json

import build_forest_pollen_v10 as pipeline

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v17.json'
CONTRACT = ROOT / 'scripts/importers/pollen_v18_sources.json'


def apply_reviewed_qc(seed, report, contract):
    """Apply only pinned v18 corrections; retain removed originals in quarantine."""
    qc = contract['integrated_qc']
    corrections = qc['age_corrections']
    if len(corrections) != 1 or corrections[0]['transform'] != 'ka_bp = 1.95 - ka_ce':
        raise ValueError('Unreviewed age correction contract')
    byid = {series['id']: series for series in seed['series']}
    excluded = []
    for hold in qc['holds']:
        original, retained = byid[hold['id']], byid[hold['duplicate_of']]
        if (original['record_id'] != retained['record_id']
                or pipeline.pollen.admission.vector(original) != pipeline.pollen.admission.vector(retained)):
            raise ValueError('Reviewed duplicate no longer has the same record and complete vector')
        excluded.append(dict(id=original['id'], duplicate_of=retained['id'],
            reason='reviewed_complete_vector_duplicate_across_importers', original_series=original))
    removed = {entry['id'] for entry in excluded}
    seed['series'] = [series for series in seed['series'] if series['id'] not in removed]
    corrected, corrected_values = [], 0
    correction = corrections[0]
    for series in seed['series']:
        if series.get('dataset_doi') != correction['dataset_doi']:
            continue
        rows = []
        for row in series['rows']:
            if row[0] is None or row[0] != float(row[4]):
                raise ValueError('Mondsee no longer uses the expected archived numeric age')
            age = float(Decimal('1.95') - Decimal(row[4]))
            rows.append([age, *row[1:]])
        series['rows'] = sorted(rows, key=lambda row: (row[0], row[2]))
        series['age_min_ka_bp'] = min(row[0] for row in rows)
        series['age_max_ka_bp'] = max(row[0] for row in rows)
        series['age_scale_before_correction'] = series['age_scale']
        series['age_scale'] = 'calendar ka BP (reference 1950)'
        series['age_transformation'] = 'ka BP = 1.95 - archived first-column ka CE; no recalibration'
        series['age_model'] = series['age_transformation']
        series['chronology_status'] = 'published_calendar_reference_corrected'
        series['chronology_label'] = 'Referencia calendario corregida a BP · sin recalibración'
        series['age_reference_correction'] = dict(transform=correction['transform'],
            source_handoff=qc['source_handoff'], source_sha256=qc['age_source']['sha256'])
        series['qc_notes'] = [*series.get('qc_notes', []), correction['reason'],
            'Ambos encabezados de edad originales son ambiguos: se conserva cada token y no se '
            'reinterpreta la segunda columna como un control independiente. La transformación '
            'concuerda con el intervalo 1500 BCE–500 CE publicado; tabla remuestreada a 20 años.']
        corrected.append(series['id'])
        corrected_values += len(rows)
    if len(corrected) != qc['age_source']['expected_series']:
        raise ValueError('Mondsee reviewed series count changed')
    seed['curation_excluded_series'] = excluded
    seed['version'] = 'atlas-quantitative-2026-11-05-v18-c' + pipeline.pollen.admission.digest(
        [seed['records'], seed['series']])[:10]
    report['version'] = seed['version']
    report['parent_unchanged'] = False
    report['parent_records_unchanged'] = True
    report['parent_series_exceptions'] = dict(corrected=corrected, held=sorted(removed))
    report['integrated_qc'] = dict(age_source=qc['age_source'], age_corrected_series=corrected,
        age_corrected_values=corrected_values, holds=[{key: value for key, value in entry.items()
        if key != 'original_series'} for entry in excluded],
        held_values=sum(len(entry['original_series']['rows']) for entry in excluded),
        original_quarantine_location='seed.curation_excluded_series')
    report['counts'].update(series=len(seed['series']), values=sum(len(series['rows']) for series in seed['series']),
        missing_age_values=sum(row[0] is None for series in seed['series'] for row in series['rows']))
    report['comparison_groups'] = len({(series['proxy'], series['compatibility_group'], series['unit'])
                                       for series in seed['series']})
    report['family_counts'] = dict(Counter(series['family'] for series in seed['series']))
    return seed, report


def build(fetch=False):
    """Return v18 and its audit; restore absent pinned originals only on request."""
    contract = json.loads(CONTRACT.read_bytes())
    source = contract['integrated_qc']['age_source']
    path = ROOT / source['path']
    if not path.exists() and not fetch:
        raise FileNotFoundError('Restore pinned Mondsee source with --fetch')
    pipeline.pollen.get(source['url'], path, source['sha256'], limit=16_000_000)
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT, version=18, finalize=apply_reviewed_qc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='Restore absent pinned Reading originals')
    args = parser.parse_args()
    _, report = build(args.fetch)
    print(json.dumps({key: report[key] for key in ('version', 'counts')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
