"""Extract reviewed PANGAEA columns and a published Zenodo sortable-silt sheet."""
import argparse
from io import BytesIO
import json
from pathlib import Path

import curate_priority_v6 as priority

ROOT = priority.ROOT
RAW = ROOT / 'data/interim/four_v7'
BASE = ROOT / 'data/processed/atlas-v6.json'
CONTRACT = Path(__file__).with_name('four_v7_sources.json')
PANGAEA = RAW / 'pangaea_curated.json'
ZENODO = RAW / 'zenodo_curated.json'


def age_rule(header):
    """Use an explicit calendar point column if present, ahead of BP of unknown basis."""
    for prefix in ('Cal age median [ka BP]', 'Cal age [ka BP]'):
        for index, name in enumerate(header):
            if name.startswith(prefix):
                return index, 'identity: published calendar point age in ka BP', float
    return priority.native.age_rule(header)


def zenodo_fragment(contract, fetch):
    """Keep cached numeric sheet cells, the sheet locator and the author's chronology."""
    from openpyxl import load_workbook

    info = contract['zenodo']
    path = RAW / 'u1389.xlsx'
    if not path.exists() and not fetch:
        raise FileNotFoundError(f'Restore {path} with --fetch')
    raw = priority.native.get(info['file_url'], path, info['sha256'], limit=1_500_000)
    book = load_workbook(BytesIO(raw), data_only=True, read_only=True)
    try:
        sheet = book[info['sheet']]
        header = list(next(sheet.values))
        if header != info['header'] or sheet.max_row != info['last_row']:
            raise ValueError('Zenodo worksheet differs from the reviewed contract')
        source_rows = list(sheet.iter_rows(min_row=2, values_only=True))
    finally:
        book.close()
    record = dict(info['record'], provider='Zenodo', realm='marine', archive_type='sediment',
                  source_url=info['url'], dataset_doi=info['doi'], raw_sha256=info['sha256'],
                  paper_doi=info['paper_doi'], publication_year=info['publication_year'],
                  license=info['license'], license_url=info['license_url'])
    series = []
    for spec in info['columns']:
        column = spec['index']
        rows = []
        for number, cells in enumerate(source_rows, start=2):
            value, age = cells[column], cells[2]
            if value is None:
                continue
            if (type(value) not in (float, int) or type(age) not in (float, int)
                    or not spec['range'][0] <= value <= spec['range'][1]):
                raise ValueError(f'Invalid Zenodo numeric cell at row {number}, column {column + 1}')
            rows.append([age, value, number - 1, number, str(age), str(value), None, None, str(cells[0])])
        rows.sort(key=lambda row: (row[0], row[2]))
        notes = [info['chronology_note'], spec['note']]
        series.append(dict(id=f'zenodo7-8163513-col{column}', record_id=record['id'], provider='Zenodo',
            proxy=spec['proxy'], variable_id=spec['proxy'], label=spec['label'],
            family='Sedimentología', proxy_families=['corrientes'],
            unit=spec['unit'], original_unit=spec['original_unit'],
            comparison_parameter_name=spec['comparison_parameter_name'],
            comparison_context_key='sortable_silt_bulk_laser_10_63_um',
            compatibility_group=spec['proxy'] + '_bulk_laser_10_63_um',
            method='Malvern Mastersizer S laser granulometer, bulk sediment',
            evidence_type='as_archived_parameter', source_url=info['file_url'],
            source_sheet=info['sheet'], source_column=header[column], source_column_index=column,
            source_header_original=header, source_event=record['core'],
            dataset_doi=info['doi'], raw_sha256=info['sha256'], citation=info['citation'],
            paper_doi=info['paper_doi'], publication_year=info['publication_year'],
            license=info['license'], license_url=info['license_url'],
            age_column_original=header[2], age_column_index=2, age_unit_original='ka',
            age_model='McCave (2023) orbital tuning, published ages',
            age_scale='published tuned ka, zero reference not independently verified',
            age_transformation='identity: published orbital-tuned age in ka',
            chronology_status='orbitally_tuned', chronology_label='Edad ajustada orbitalmente',
            depth_frame='mbsf', depth_column_index=0, qc_notes=notes, rows=rows,
            search_aliases=['sortable silt', 'corrientes', 'limo clasificable', header[column]]))
    return dict(parent_sha256=contract['parent_sha256'], records=[record], series=series,
                verified_parent_links={record['id']: info['parent_record_id']})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding='utf8'))
    priority.curate(args.fetch, contract_path=CONTRACT, baseline=BASE, raw_dir=RAW / 'pangaea',
                    fragment_path=PANGAEA, audit_path=ROOT / 'reports/four_v7_pangaea_audit.json',
                    namespace='pangaea7', age_rule=age_rule)
    fragment = zenodo_fragment(contract, args.fetch)
    ZENODO.write_text(json.dumps(fragment, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
    print('Zenodo observations:', sum(len(series['rows']) for series in fragment['series']))


if __name__ == '__main__':
    main()
