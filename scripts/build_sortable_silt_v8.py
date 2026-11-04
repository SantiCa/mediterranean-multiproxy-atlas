"""Append sortable-silt series using reviewed age controls for the same depth frame."""
import argparse
from io import BytesIO
import json
from pathlib import Path
import sys

import build_quantitative_v5 as admission

sys.path.insert(0, str(Path(__file__).parent / 'importers'))
from curate_pangaea_v5 import get, interpolate, number, parse_tsv, sha, xml_meta

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/processed/atlas-v7.json'
RAW = ROOT / 'data/interim/ss_v8'
CONTRACT = ROOT / 'scripts/importers/ss_v8_sources.json'
RULE = 'Linear depth interpolation between published controls; no extrapolation'


def original(resource, fetch):
    path = RAW / resource['file']
    if not path.exists() and not fetch:
        raise FileNotFoundError(f'Restore {path.name} with --fetch')
    return get(resource['url'], path, resource['sha256'], accept=resource.get('accept'), limit=32_000_000)


def sample_tables(contract, fetch):
    """Read pinned proxy tables and keep each native row and line locator."""
    from openpyxl import load_workbook

    book = load_workbook(BytesIO(original(contract['workbook'], fetch)), data_only=True, read_only=True)
    try:
        for entry in contract['admitted']:
            if 'sheet' not in entry:
                source = entry['source']
                _, header, rows = parse_tsv(original(source, fetch))
                columns, events, _, _, license_url = xml_meta(original(entry['xml'], fetch))
                if (header != entry['header'] or columns[1]['name'] != 'Sortable-silt mean'
                        or columns[1]['unit'] != 'µm' or license_url != source['license_url']
                        or len(events) != 1 or events[0]['label'] != entry['core']
                        or (events[0]['lat'], events[0]['lon']) != (entry['latitude'], entry['longitude'])):
                    raise ValueError('PANGAEA variable, site or licence differs from contract')
                yield entry, source, [(row, line, cells[0], cells[1]) for row, line, cells in rows]
                continue
            sheet = book[entry['sheet']]
            header_row = entry['header_row']
            values = sheet.iter_rows(min_row=header_row, max_col=2, values_only=True)
            header = list(next(values))
            if header != entry['header'] or sheet.max_row != entry['last_row']:
                raise ValueError(f'{sheet.title}: original worksheet header or length changed')
            yield entry, contract['workbook'], [(i - header_row, i, str(z), str(value))
                    for i, (z, value) in enumerate(values, header_row + 1)]
    finally:
        book.close()


def controls(entry, fetch):
    """Validate an explicit published age-depth contract before any age assignment."""
    model = entry['chronology']
    if model['depth_frame'] != entry['depth_frame']:
        raise ValueError('Proxy and age model depth frames differ')
    if model.get('table'):
        # Factual controls transcribed from the named table. Preserve native years.
        points = [(float(z), float(age) / 1000) for z, age in model['table']]
    else:
        _, header, rows = parse_tsv(original(model['source'], fetch))
        _, events, _, _, license_url = xml_meta(original(model['xml'], fetch))
        if set(e['label'] for e in events) != set(model['component_events']) or license_url != model['license_url']:
            raise ValueError('Chronology source events or licence differ from the contract')
        if header != model['header'] or any(cells[0] not in model['component_events'] for _, _, cells in rows):
            raise ValueError('Unexpected source header or sample event in the chronology')
        points = sorted({(float(cells[2]), float(cells[3])) for _, _, cells in rows})
    if (len(points) < 2 or any(number(str(x)) is None for pt in points for x in pt)
            or any(b[0] <= a[0] or b[1] < a[1] for a, b in zip(points, points[1:]))):
        raise ValueError('Chronology is not a strictly ordered depth / monotone age sequence')
    return points


def extract(contract, fetch=False):
    records, series, audit = [], [], []
    for entry, source, samples in sample_tables(contract, fetch):
        pts = controls(entry, fetch)
        core, model = entry['core'], entry['chronology']
        xlsx = 'sheet' in entry
        rid = ('mendeley8-' if xlsx else 'pangaea8-') + core.lower()
        notes = [model['evidence'], model['uncertainty_note'],
                 'Edades estimadas por interpolación lineal. Fuera del rango del modelo se conserva la profundidad sin edad.']
        if xlsx:
            notes.append('La cabecera y el artículo identifican tamaño medio en µm. La nota «%» del preámbulo de la hoja contradice ambas fuentes.')
        provider = 'Mendeley Data' if xlsx else 'PANGAEA'
        common = dict(provider=provider, dataset_doi=source['doi'], paper_doi=source.get('paper_doi'),
                      publication_year=2022 if xlsx else None, license=source['license'],
                      license_url=source['license_url'], qc_notes=notes, raw_sha256=source['sha256'])
        records.append(dict(id=rid, name=core, core=core, source_event=core,
                            latitude=entry['latitude'], longitude=entry['longitude'], water_depth_m=entry['water_depth_m'],
                            realm='marine', archive_type='sediment', campaign='Exp339' if xlsx else entry['campaign'],
                            source_url=source['landing_page'], **common))
        rows = []
        for source_row, source_line, z, value in samples:
            if z == value == 'None':
                continue
            depth, mean_size = number(z), number(value)
            if depth is None or mean_size is None or depth < 0 or not 10 <= mean_size <= 63:
                raise ValueError(f'{core} row {source_row}: invalid sortable-silt mean or depth')
            age = interpolate(pts, depth)
            rows.append([age, mean_size, source_row, source_line, None, value, None, None, z])
        rows.sort(key=lambda r: (r[0] is None, r[0] or 0, r[2]))
        dated = [r[0] for r in rows if r[0] is not None]
        sid = rid + '-ss-mean'
        context = 'sortable_silt_bulk_laser_10_63_um' if xlsx else entry['comparison_context']
        proxy = 'sortable_silt_mean_bulk_laser_um' if xlsx else 'sortable_silt_mean_um'
        series.append(dict(id=sid, record_id=rid, proxy=proxy, variable_id=proxy,
                           label='Sortable silt · tamaño medio (10–63 µm)' if xlsx else 'Sortable silt · tamaño medio',
                           unit='µm', original_unit='µm', comparison_parameter_name='Sortable-silt mean',
                           comparison_context_key=context, compatibility_group=proxy + '_' + context.removeprefix('sortable_silt_'),
                           family='Sedimentología', proxy_families=['corrientes'],
                           method='Malvern Mastersizer S laser granulometer, bulk sediment' if xlsx else entry['method'],
                           source_url=source['url'], source_sheet=entry.get('sheet'), source_header_original=entry['header'],
                           source_column=entry['header'][1], source_column_index=1, source_event=core,
                           citation=source['citation'],
                           evidence_type='as_archived_parameter', depth_column_index=0, depth_frame=entry['depth_frame'],
                           age_scale='calendar ka BP', age_model=model['locator'], age_model_doi=model.get('doi'),
                           age_model_url=model['landing_page'], age_model_source_sha256=model['sha256'],
                           age_transformation=RULE, chronology_status='interpolated_from_age_model',
                           chronology_label='Edad interpolada desde controles publicados del mismo registro',
                           uncertainty_type='No propagated age uncertainty; see source tie points',
                           rows=rows, search_aliases=['sortable silt', 'limo clasificable', 'corrientes'], **common))
        audit.append(dict(core=core, series=sid, source_values=len(rows), dated_values=len(dated),
                          no_age_values=len(rows)-len(dated), model_depth_m=[pts[0][0], pts[-1][0]],
                          dated_age_ka_bp=[min(dated), max(dated)], chronology=model['locator']))
    return dict(records=records, series=series, pending=contract['held']), audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='Restore only missing pinned native sources')
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_bytes())
    parent_hash = sha(BASE.read_bytes())
    if parent_hash != contract['parent_sha256']:
        raise ValueError('Stale parent: review overlap and update the v8 source contract')
    fragment, audit = extract(contract, args.fetch)
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / 'sortable_silt_curated.json'
    path.write_text(json.dumps(fragment, ensure_ascii=False), encoding='utf8')
    seed, report = admission.assemble(baseline=BASE, fragment_paths=[path], provider_names=['sortable_silt'],
                                      version_prefix='atlas-quantitative-2026-11-05-v8-')
    raw = json.dumps(seed, ensure_ascii=False, separators=(',', ':')).encode()
    report.update(parent_sha256=parent_hash, sha256=sha(raw), bytes=len(raw), chronology_audit=audit,
                  source_audits=['scripts/importers/ss_v8_sources.json'])
    (ROOT / 'data/processed/atlas-v8.json').write_bytes(raw)
    (ROOT / 'reports/quantitative_v8_release.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: report[k] for k in ('version', 'counts', 'chronology_audit')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
