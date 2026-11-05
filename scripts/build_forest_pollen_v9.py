"""Append native Monticchio percentages and explicitly normalized Iberian pollen.

Source contracts pin entire files, entity identities and columns. Reading's sum
is the retained 205-column assemblage, including any retained spores. It is not
interpreted as tree cover or as the original authors' terrestrial pollen sum.
"""
import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import sys

import build_quantitative_v5 as admission

sys.path.insert(0, str(Path(__file__).parent / 'importers'))
from curate_pangaea_v5 import get, number, sha

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/interim/pollen_v9'
BASE = ROOT / 'data/processed/atlas-v8.json'
CONTRACT = ROOT / 'scripts/importers/pollen_v9_sources.json'
TAXA = {
    'Abies_': ('Abies', ['Abies']),
    'Alnus_': ('Alnus', ['Alnus']),
    'Betula_': ('Betula', ['Betula']),
    'Fagus_': ('Fagus', ['Fagus']),
    'Pinus_': ('Pinus', ['Pinus', 'Pinus..diploxylon.', 'Pinus..haploxylon.']),
    'Quercus_deciduous_': ('Quercus, deciduous', ['Quercus.deciduous']),
}
READING_DOI = '10.17864/1947.000369'
READING_CONTEXT = 'reading_iberia_v3_retained_205_taxa_sum'


def original(resource, fetch):
    path = RAW / resource['file']
    if not path.exists() and not fetch:
        raise FileNotFoundError(f'Restore pinned original {path.name} with --fetch')
    return get(resource['url'], path, resource['sha256'], limit=16_000_000)


def abundance(values, columns):
    """A missing taxon is unknown. Only explicit finite nonnegative cells enter."""
    nums = [number(values[k]) for k in columns]
    if any(v is None or v < 0 for v in nums):
        raise ValueError('Missing, censored or negative native assemblage cell')
    return sum(nums)


def fraction(numerator, denominator):
    if not 0 <= numerator <= denominator or denominator <= 0:
        raise ValueError('Invalid abundance numerator or assemblage sum')
    return numerator * 100 / denominator


def monticchio(resource, contract, parent):
    """Link the native D/J pollen subset to its already imported NOAA study."""
    lines = (RAW / resource['file']).read_text(encoding='utf8').splitlines()
    table = list(csv.reader(lines, delimiter='\t'))
    header = table[2]
    if (header[:8] != ['Sample age', 'Pollen count', 'Woody taxa', 'Herbaceous taxa',
                      'Pinus', 'Juniperus type', 'Betula', 'Quercus']
            or table[3][:4] != ['lamination years BP', 'grains', '%', '%']
            or len(table[5:]) != contract['monticchio_rows']):
        raise ValueError('Monticchio native columns, age units or row count changed')
    rid = 'pollen9-monticchio-noaa-subset'
    record = dict(parent, id=rid)
    note = ('Polen de los núcleos D (1990) y J (1994), subconjunto del compuesto '
            'B-D-J-L del estudio NOAA 5463. La posición corresponde al punto '
            'archivado por NOAA para el estudio, sin atribuir precisión a cada perforación.')
    series = []
    for col in (2, 4, 5, 6, 7, 8, 9, 10):
        name = header[col]
        proxy = {'Woody taxa': 'Woody_taxa_percent_', 'Juniperus type': 'Juniperus_type_'}.get(name, name + '_')
        rows = []
        for row, cells in enumerate(table[5:], 1):
            if len(cells) != 18:
                raise ValueError('Unexpected Monticchio row width')
            age, value = number(cells[0]), number(cells[col])
            if age is None or value is None or not 0 <= value <= 100:
                raise ValueError('Invalid native Monticchio age or percent')
            if abs(float(cells[2]) + float(cells[3]) - 100) > .011:
                raise ValueError('Woody and herbaceous native groups do not close')
            rows.append([age / 1000, value, row, row + 5, cells[0], cells[col], None, None, None])
        series.append(dict(id=rid + '-' + proxy, record_id=rid, proxy=proxy,
            label=name + ' · Monticchio NOAA', unit='%', original_unit='%',
            family='Polen', proxy_families=['vegetacion'], taxon=name,
            compatibility_group=proxy + '_monticchio1999_native_published_sum',
            comparison_context_key='monticchio1999_native_published_pollen_percent',
            comparison_parameter_name=name, method='Published palynological relative abundance',
            evidence_type='published_value', source_url=resource['url'],
            source_column=header[col], source_column_index=col, source_header_original=header,
            source_core_original='D 1990 + J 1994', raw_sha256=resource['sha256'],
            dataset_doi=parent['dataset_doi'], paper_doi=parent['paper_doi'], publication_year=1999,
            citation='Allen et al. (1999), Nature, 400, 740–743. NOAA archive 2002-013.',
            license=parent['license'], license_url=parent['license_url'],
            age_scale='lamination years BP / 1000', age_column_original=table[3][0],
            age_transformation='Native lamination-year BP / 1000. No re-dating or interpolation.',
            chronology_status='published_lamination_BP', chronology_label='Laminación/tefras · BP publicado',
            qc_notes=[note, 'Porcentajes publicados conservados. Suma polínica original sin armonizar '
                      'con Reading. Woody taxa incluye árboles y arbustos, sin equivalencia con cubierta forestal.',
                      'Neotoma 47525 y ACER del mismo lago pueden compartir material. Se mantiene '
                      'Neotoma en espera para evitar incorporar una segunda versión como réplica.'],
            rows=sorted(rows, key=lambda r: (r[0], r[2]))))
    return record, series, note


def reading(resource, contract):
    with (RAW / resource['file']).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != contract['reading_header'] or len(reader.fieldnames[15:]) != 205:
            raise ValueError('Reading assemblage columns changed')
        taxa = reader.fieldnames[15:]
        groups = defaultdict(list)
        for index, row in enumerate(reader, 1):
            groups[row['entity_name']].append((index, reader.line_num, row))
    records, series, audit = [], [], []
    for entry in contract['reading_entities']:
        samples = groups[entry['entity']]
        if len(samples) != entry['rows'] or [samples[0][0], samples[-1][0]] != [entry['first_row'], entry['last_row']]:
            raise ValueError('Reading entity row contract changed')
        first = samples[0][2]
        if (first['reference'] != entry['reference'] or first['site_name'] != entry['site']
                or float(first['latitude']) != entry['latitude'] or float(first['longitude']) != entry['longitude']):
            raise ValueError('Reading entity metadata changed')
        rid = 'reading9-' + entry['entity'].lower().replace(' ', '-')
        note = ('Porcentajes calculados sobre las 205 columnas del conjunto armonizado '
                'Reading v3. La fuente mezcla recuentos y porcentajes sin indicador por entidad. '
                'Se conserva abundancia original y denominador por muestra. Incluye los taxones '
                'retenidos por los compiladores, con posibles esporas. No representa cubierta forestal.')
        age_note = ('Edad mediana INTCAL2020 publicada, años calendario BP / 1000. '
                    'Sin recalibración local. Los campos uncert_5/95 y 25/75 se conservan como '
                    'publicados en pollen_sample_audit. Su interpretación como límites absolutos '
                    'es inconsistente con algunas medianas, por lo que no se dibujan bandas de edad.')
        common = dict(provider='University of Reading', dataset_doi=READING_DOI,
                      paper_doi=None, related_paper_dois=entry['paper_dois'], publication_year=None,
                      dataset_publication_year=2022, citation=entry['reference'],
                      compilation_citation='Harrison, S. P.; Shen, Y.; Sweeney, L. (2022). Iberia pollen v3.',
                      license='Creative Commons Attribution 4.0 International',
                      license_url='https://creativecommons.org/licenses/by/4.0/', raw_sha256=resource['sha256'],
                      qc_notes=[note, age_note])
        source_audit, derived = [], {proxy: [] for proxy in TAXA}
        points = []
        for rowid, line, row in samples:
            if any(row[k] != first[k] for k in ('latitude', 'longitude', 'elevation', 'reference', 'site_name')):
                raise ValueError('Entity identity varies between samples')
            total = abundance(row, taxa)
            age, depth = number(row['INTCAL2020_median']), number(row['avg_depth..cm.'])
            if age is None or depth is None or total <= 0:
                raise ValueError('Missing age/depth or empty retained assemblage')
            points.append((depth, age))
            source_audit.append([rowid, line, row['avg_depth..cm.'], total, row['INTCAL2020_median'],
                *[row[k] for k in ('IPE.age..cal.', 'INTCAL2020_mean', 'INTCAL2020_uncert_5',
                                  'INTCAL2020_uncert_95', 'INTCAL2020_uncert_25', 'INTCAL2020_uncert_75')]])
            for proxy, (_, columns) in TAXA.items():
                value = abundance(row, columns)
                # Single-column native tokens stay exact. Composite Pinus retains
                # all input cells in source columns and the native source row.
                original_value = row[columns[0]] if len(columns) == 1 else str(value)
                derived[proxy].append([age / 1000, fraction(value, total), rowid, line,
                                       row['INTCAL2020_median'], original_value, None, None, row['avg_depth..cm.']])
        points.sort()
        if any(b[0] <= a[0] or b[1] < a[1] for a, b in zip(points, points[1:])):
            raise ValueError('Duplicate depth or age reversal requires entity-specific review')
        records.append(dict(id=rid, name=entry['site'], core=entry['entity'], realm='continental',
            archive_type='continental pollen sediment', latitude=entry['latitude'], longitude=entry['longitude'],
            elevation_m=float(first['elevation']), source_url='https://researchdata.reading.ac.uk/369/',
            coordinate_basis='Native sampling-entity coordinates in Reading v3',
            source_database_original=first['source'],
            pollen_sample_audit_fields=['source_row', 'source_line', 'depth_cm', 'retained_205_sum',
                'INTCAL2020_median', 'IPE.age..cal.', 'INTCAL2020_mean', 'INTCAL2020_uncert_5',
                'INTCAL2020_uncert_95', 'INTCAL2020_uncert_25', 'INTCAL2020_uncert_75'],
            pollen_sample_audit=source_audit, **common))
        for proxy, (name, columns) in TAXA.items():
            series.append(dict(id=rid + '-' + proxy, record_id=rid, proxy=proxy,
                label=name + ' · suma armonizada Reading', unit='%',
                original_unit='native taxon abundance (counts or %, not identified per entity)',
                family='Polen', proxy_families=['vegetacion'], taxon=name,
                compatibility_group=proxy + '_' + READING_CONTEXT,
                comparison_context_key=READING_CONTEXT, comparison_parameter_name=name,
                method='Palynology; harmonized archived assemblage renormalized to retained 205-taxon sum',
                evidence_type='derived_relative_abundance',
                value_transformation='100 * sum(source_columns) / sum(all 205 native taxon columns)',
                denominator_columns=taxa, denominator_metadata='record.pollen_sample_audit.retained_205_sum',
                source_url=resource['url'], source_column=' + '.join(columns), source_columns=columns,
                source_column_index=contract['reading_header'].index(columns[0]),
                source_header_original=contract['reading_header'],
                source_event=entry['entity'], depth_unit_original='cm',
                age_scale='calendar ka BP', age_column_original='INTCAL2020_median',
                age_transformation='Published IntCal20 model median in calendar years BP / 1000',
                chronology_status='published_calibrated_radiocarbon',
                chronology_label='IntCal20/Bacon · mediana publicada',
                uncertainty_type='Native uncertainty fields retained without reinterpretation or plotted intervals',
                rows=sorted(derived[proxy], key=lambda r: (r[0], r[2])), **common))
        audit.append(dict(entity=entry['entity'], samples=len(samples),
                          age_ka_bp=[min(p[1] for p in points)/1000, max(p[1] for p in points)/1000],
                          denominator_range=[min(x[3] for x in source_audit), max(x[3] for x in source_audit)]))
    return records, series, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='Restore missing hash-pinned original files')
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_bytes())
    if sha(BASE.read_bytes()) != contract['parent_sha256']:
        raise ValueError('Stale v8 parent. Review overlaps before rebuilding v9.')
    for resource in contract['resources']:
        original(resource, args.fetch)
    resources = {s['file']: s for s in contract['resources']}
    parent = next(r for r in json.loads(BASE.read_bytes())['records'] if r['id'] == contract['monticchio_parent'])
    record, native, note = monticchio(resources['pollen.txt'], contract, parent)
    records, series, audit = reading(resources['iberia.csv'], contract)
    fragment = dict(records=[record] + records, series=native + series,
                    verified_parent_links={record['id']: parent['id']},
                    parent_link_notes={record['id']: note}, pending=contract['held'])
    path = RAW / 'forest_pollen_curated.json'
    path.write_text(json.dumps(fragment, ensure_ascii=False), encoding='utf8')
    seed, report = admission.assemble(baseline=BASE, fragment_paths=[path], provider_names=['forest_pollen'],
                                      version_prefix='atlas-quantitative-2026-11-05-v9-')
    raw = json.dumps(seed, ensure_ascii=False, separators=(',', ':')).encode()
    report.update(parent_sha256=contract['parent_sha256'], sha256=sha(raw), bytes=len(raw),
                  chronology_and_denominator_audit=audit, held=contract['held'],
                  source_audits=['scripts/importers/pollen_v9_sources.json'])
    (ROOT / 'data/processed/atlas-v9.json').write_bytes(raw)
    (ROOT / 'reports/quantitative_v9_release.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: report[k] for k in ('version', 'counts')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
