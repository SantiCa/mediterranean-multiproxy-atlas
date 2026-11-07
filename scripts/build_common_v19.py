"""Append a reviewed PANGAEA batch of common proxies and published composites."""
import argparse
import json
from pathlib import Path
import sys

import build_quantitative_v5 as admission

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/importers'))
import curate_priority_v6 as curator

BASE = ROOT / 'data/processed/atlas-v18.json'
CONTRACT = ROOT / 'scripts/importers/common_v19_sources.json'
RAW = ROOT / 'data/interim/common_v19'


def coverage(seed):
    """Count dated records and rounded locations by broad family, not equivalence."""
    records = {record['id']: record for record in seed['records']}
    result = {}
    for family in ('Temperatura', 'Isótopos estables', 'Biomarcadores', 'Micropaleontología'):
        selected = [series for series in seed['series'] if series['family'] == family
                    and any(row[0] is not None for row in series['rows'])]
        identifiers = {series['record_id'] for series in selected}
        locations = {(round(records[key]['latitude'], 4), round(records[key]['longitude'], 4))
                     for key in identifiers}
        result[family] = dict(records=len(identifiers), distinct_locations=len(locations),
            series=len(selected), values=sum(len(series['rows']) for series in selected))
    return result


def build(fetch=False, *, baseline=BASE, contract_path=CONTRACT, raw_dir=RAW, version=19,
          release_date='2026-11-06',
          age_rule=curator.native.age_rule):
    """Extract pinned native values and append compatible, traceable series to v18."""
    contract = json.loads(contract_path.read_bytes())
    curator.FAMILIES.update(sst='Temperatura', indices='Biomarcadores',
                            isotopes='Isótopos estables', productivity='Micropaleontología',
                            toc='Materia orgánica y biomarcadores', nutrients='Geoquímica elemental')
    fragment_path = raw_dir / 'curated.json'
    audit_path = ROOT / f'reports/common_v{version}_extraction_audit.json'
    curator.curate(fetch, contract_path=contract_path, baseline=baseline, raw_dir=raw_dir,
                   fragment_path=fragment_path, audit_path=audit_path, namespace=f'pangaea{version}', age_rule=age_rule)
    fragment = json.loads(fragment_path.read_bytes())
    specs = {entry['id']: entry for entry in contract['datasets'] if entry['status'] == 'ready'}
    native_tables = {}
    for ident, entry in specs.items():
        _, header, rows = curator.native.parse_tsv((raw_dir / f'{ident}.tsv').read_bytes())
        native_tables[ident] = {index: cells for index, _, cells in rows}
        if ident == 939417:
            for _, _, cells in rows:
                if abs((1950 - float(cells[1])) / 1000 - float(cells[2])) > 1e-9:
                    raise ValueError('Native CE and BP columns no longer agree')
    for series in fragment['series']:
        ident = int(series['dataset_doi'].rsplit('.', 1)[1])
        entry = specs[ident]
        spec = next(column for column in entry['columns']
                    if column['column'] == series['source_column_index'])
        series['qc_notes'] += entry['qc_notes'] + [
            'Variable ambiental interpretada/reconstruida: ' + spec['environmental_interpretation'],
            'Unidad estándar del proxy: ' + ('adimensional (1), archivada como sin unidad'
                if spec['unit'] == 'sin unidad' else spec['unit'])]
        series['evidence_type'] = spec['evidence_type']
        series['comparison_parameter_name'] = spec['name']
        series['search_aliases'] += [spec['environmental_interpretation'], spec['short']]
        if spec.get('taxon'):
            series['taxon'] = spec['taxon']
        if spec['family'] == 'isotopes':
            series['taxon'] = spec['name'].split(',')[0]
            isotope = 'd18O' if '18O' in spec['name'] else 'd13C'
            habitat = 'planct' if series['taxon'] == 'Globigerina bulloides' else 'bent'
            series['proxy_families'] = [isotope + '_' + habitat]
        elif spec['family'] == 'indices':
            series['proxy_families'] = ['biomarcadores_indices']
        if spec.get('error_column') is not None:
            error_column = spec['error_column']
            for row in series['rows']:
                error = curator.native.number(native_tables[ident][row[2]][error_column])
                if error is not None and error < 0:
                    raise ValueError('Negative native standard deviation')
                row[7] = error
            series['value_uncertainty_source_column'] = entry['header'][error_column]
            series['uncertainty_type'] = spec.get('uncertainty_type',
                'Published companion standard deviation; no propagated or calibration error invented')
        elif ident == 733103:
            series['uncertainty_type'] = 'Native standard-deviation columns retained in original; estimator assignment unresolved'
    for record in fragment['records']:
        entry = next(entry for entry in specs.values()
                     if record['core'] in {event['label'] for event in entry['events']})
        record.update(entry.get('record_metadata', {}))
    fragment_path.write_text(json.dumps(fragment, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
    seed, report = admission.assemble(baseline=baseline, fragment_paths=[fragment_path],
        provider_names=['pangaea_common'], version_prefix=f'atlas-quantitative-{release_date}-v{version}-')
    report.update(parent_sha256=contract['parent_sha256'],
        source_audits=[contract_path.relative_to(ROOT).as_posix(), audit_path.relative_to(ROOT).as_posix()],
        selection_limits=contract['selection_limits'],
        coverage_before=coverage(json.loads(baseline.read_bytes())), coverage_after=coverage(seed),
        coverage_scope='Broad native family and four-decimal coordinates; not methodological equivalence, SST-only coverage or independent neighbours')
    raw = json.dumps(seed, ensure_ascii=False, separators=(',', ':')).encode()
    report.update(sha256=curator.native.sha(raw), bytes=len(raw))
    (ROOT / f'data/processed/atlas-v{version}.json').write_bytes(raw)
    (ROOT / f'reports/quantitative_v{version}_release.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({key: report[key] for key in ('version', 'counts')}, ensure_ascii=False))
    return seed, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='Restore absent hash-pinned source resources')
    args = parser.parse_args()
    build(args.fetch)


if __name__ == '__main__':
    main()
