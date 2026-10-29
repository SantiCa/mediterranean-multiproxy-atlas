"""Curate an explicit bounded PANGAEA batch; never infer ages from depth.

Native bytes are cached immutably; offline mode is the default. Source-specific
column contracts below are reviewed against their native metadata before import.
"""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import math
from collections import Counter
from pathlib import Path
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/interim/quantitative_v3/pangaea'
IDS = [438384, 438795, 438799, 789685, 789686, 789690, 836213, 854682, 871130, 818921]
SELECTED = [x for x in IDS if x != 854682]
PINNED = {
438384: ('430d62ca710dc960809c7ac95bded76dc90bd4627e63e4a32979de5b56a16d30', '6fa5b2ce46fecae5c6b66abe12ab181271019828746ee808bba73d6da5257764'),
438795: ('88ed03dca47e57372458137a55c1dc5ebc2ee063f059a49be4e6bbbb5121db84', '8a37e9078beb57e2a4362557abb8010e825fe31c7c380e7e3806bf02a468b5ac'),
438799: ('2dcf8893b0d7ca9f8208ec52970742f56b60895153c1400f3c65f069697c3152', '75bcf054f844e22af826807e7cdfcee72c6c7c08540595ad9a1b579f1725ba5d'),
789685: ('f0b1c25227dca31e25eeaef7414e81afcaa9cca8c85b27f43793f035c657d1ce', '6d79e863afa4cbcf1a5abdd9a2377bb72113ef6816a96b22926eaa4aac586383'),
789686: ('e3c5584113401ffdc62a9f53802c5aa0b885dc0f8da87bccdaf2a497305116ae', 'b2da97b4293b5041e5ceb0c2b7d34c45f650bc624d81f07c5fce8b6f4833325b'),
789690: ('9bce660b8c88e89566257e6f32ce8df41ff9b2f314584ccb0d612db518016546', 'eaf946356684886a0dbf412dd9348b9875b9aa18f8a6b5117b289fd9ddf64f71'),
836213: ('c78fb4d5854d7bd35fba6ea3894fb3f030fffb95c7e60e5b413d5bcc484b7418', '50107c90c6e2dc73b3ac6f873ef1871c14e21ffc21ae084389df1be729e48c48'),
854682: ('e196b58943a8a65059c085523597555ac7785cea7d1607e78446bcbfb0f7b8a7', '2d6750d758ac3160dbea1c316aac382de8637e166ecb9d13e949ef2627ab5910'),
871130: ('c7569ea3c821d4b9bd49748604d82c1416ace403a0379e14ec131d3d739ba7c2', '3639b76a122282d60e545e752492cff35ec25a42cc2e9015b0b4891ae49d2ad7'),
818921: ('381bdaea32ee0bec69ad51585e725f8a303a091e315071cf75d8524a170d2bc8', '5499e1c591beaed6d6c82fe929f59d7b81c6f1e58da0d6e7e6153b76e5df0e4e'),
}
PAPERS = {
438384: ('10.1016/j.quascirev.2004.08.010', 2004, 'in_supplement_to'),
438795: ('10.1191/0959683603hl622ed', 2003, 'related_editorial_not_direct_data_article'),
438799: ('10.1029/2000PA000502', 2001, 'in_supplement_to'),
789685: ('10.1029/2006GC001543', 2007, 'in_supplement_to'),
789686: ('10.1029/2006GC001543', 2007, 'in_supplement_to'),
789690: ('10.1029/2006GC001543', 2007, 'in_supplement_to'),
836213: ('10.1016/j.gloplacha.2014.10.004', 2014, 'in_supplement_to'),
871130: ('10.5194/cp-12-849-2016', 2016, 'in_supplement_to'),
818921: ('10.1016/j.quascirev.2013.08.018', 2013, 'in_supplement_to'),
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def native(dataset_id, extension):
    """Read reviewed bytes; an updated source requires explicit new curation."""
    raw = (RAW / f'{dataset_id}.{extension}').read_bytes()
    expected = PINNED[dataset_id][0 if extension == 'tsv' else 1]
    if sha(raw) != expected:
        raise RuntimeError(f'{dataset_id}.{extension}: bytes differ from reviewed snapshot')
    return raw

def acquire(dataset_id):
    """Fetch at most 8 MB per native resource, refusing changed cached bytes."""
    RAW.mkdir(parents=True, exist_ok=True)
    for extension, fmt in [('tsv', 'textfile'), ('xml', 'metainfo_xml')]:
        path = RAW / f'{dataset_id}.{extension}'
        if path.exists():
            native(dataset_id, extension)
            continue
        url = f'https://doi.pangaea.de/10.1594/PANGAEA.{dataset_id}?format={fmt}'
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'MediterraneanMultiproxyAtlas/0.3'}), timeout=45) as response:
            raw = response.read(8_000_001)
        if len(raw) > 8_000_000:
            raise RuntimeError(f'{dataset_id}: resource exceeds 8 MB bound')
        if extension == 'tsv' and not raw.startswith(b'/* DATA DESCRIPTION:'):
            raise RuntimeError(f'{dataset_id}: not a native data table')
        if extension == 'xml':
            ET.fromstring(raw)
        if sha(raw) != PINNED[dataset_id][0 if extension == 'tsv' else 1]:
            raise RuntimeError(f'{dataset_id}: remote bytes changed; preserve and review separately')
        path.write_bytes(raw)
    return dataset_id

def inspect(dataset_id):
    text = native(dataset_id, 'tsv').decode('utf-8-sig')
    header, table = text.split('*/', 1)
    lines = table.strip().splitlines()
    return dict(id=dataset_id, metadata=header, columns=lines[0].split('\t'), rows=len(lines)-1)

def acquire_papers():
    """Cache the named Crossref identity records, at most 2 MB each."""
    for doi, _, _ in set(PAPERS.values()):
        path = RAW / ('crossref-' + sha(doi.lower().encode())[:16] + '.json')
        if not path.exists():
            url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='')
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'MediterraneanMultiproxyAtlas/0.3'}), timeout=45) as response:
                raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise RuntimeError('Crossref response exceeds bounded limit')
            json.loads(raw)
            path.write_bytes(raw)

def number(cell):
    """Accept finite uncensored numeric cells only, never strip qualifiers."""
    try:
        value = float(cell)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None

def to_age(cell, age_column):
    value = number(cell)
    if value is None:
        return None
    if age_column == 'Age [a AD/CE]':
        return (1950 - value) / 1000
    if age_column == 'Varve age [a BP]':
        return value / 1000
    if age_column == 'Age [ka BP]':
        return value
    raise ValueError('Unreviewed chronology unit')

def specs(dataset_id):
    """Explicit reviewed column contracts; units alone never define compatibility."""
    if dataset_id in (438384, 438795, 438799):
        calibration = 'prahl1988' if dataset_id == 438384 else 'mueller1998'
        return [('SST (1-12) [°C]', 'alkenone_SST', 'SST · alquenonas · '+calibration,
                 '°C', 'sst_alkenone_'+calibration+'_annual', 'temperature', 'published_reconstruction',
                 "Calculated from UK37; "+calibration+'; annual mean as archived', None)]
    if dataset_id in (789685, 789686, 789690):
        return [
            ("UK'37", 'alkenone_UK37', "UK′37 · Versteegh 2007", 'adimensional', 'uk37_versteegh2007_conte2006', 'biomarkers', 'published_index', 'Calculated after Conte et al. (2006), as archived', None),
            ('SST [°C]', 'alkenone_SST', 'SST · alquenonas · Versteegh 2007', '°C', 'sst_alkenone_versteegh2007_as_archived', 'temperature', 'published_reconstruction', 'SST as published in Versteegh et al. (2007); temperature calibration not independently verified', None),
        ]
    if dataset_id == 836213:
        return [(f'{short} δ{isotope} [‰ PDB]', f'{proxy}_d{isotope}', f'δ{isotope} · {short}',
                 '‰ VPDB', f'{proxy}_d{isotope}_vpdb_kandiano2014', 'stable_isotopes', 'measurement',
                 'Foraminiferal stable isotope analysis; source explicitly states with respect to VPDB', taxon)
                for short, proxy, taxon in [('G. bulloides', 'G_bulloides', 'Globigerina bulloides'), ('G. ruber', 'G_ruber', 'Globigerinoides ruber')]
                for isotope in ('13C', '18O')]
    if dataset_id == 871130:
        return [('SST (1-12) [°C]', 'MgCa_SST', 'SST · Mg/Ca · Cisneros 2016', '°C', 'sst_mgca_cisneros2016_G_bulloides_spring', 'temperature', 'published_reconstruction',
                 'G. bulloides Mg/Ca reconstruction, Cisneros et al. (2016); article identifies spring signal despite annual source parameter label', 'Globigerina bulloides')]
    if dataset_id == 818921:
        return [('Ti [cps]', 'Ti_XRF_scanner', 'Ti · XRF · Mondsee Mo05', 'cps', 'Ti_XRF_cps_Mo05_PANGAEA818921', 'geochemistry', 'instrument_counts',
                 'X-ray fluorescence core scanning; dataset-scoped cps, not calibrated Ti concentration', None)]
    raise ValueError('Dataset not explicitly selected')

def curate():
    """Return source-linked records/series and an inspectable extraction audit.

    Depth is never used to construct an age. Missing values are not zero-filled;
    finite values lacking ages are preserved and excluded from age plots downstream.
    """
    records, series, audits = [], [], []
    old = json.loads((ROOT / 'data/processed/atlas-v1.json').read_text(encoding='utf-8'))
    old_dois = {str(r.get('dataset_doi', '')).lower() for r in old['records']}
    source_sigs = {}
    for old_s in old['series']:
        sig = sha(json.dumps([[r[0], r[1]] for r in old_s['rows']], separators=(',', ':')).encode())
        source_sigs.setdefault(sig, []).append(old_s['id'])
    inventory = json.loads((ROOT / 'data/processed/inventory-v2.json').read_text(encoding='utf-8'))
    for dataset_id in SELECTED:
        raw = native(dataset_id, 'tsv')
        xml = native(dataset_id, 'xml')
        text = raw.decode('utf-8-sig')
        head, tab = text.split('*/', 1)
        if 'CC-BY-3.0' not in head:
            raise RuntimeError('Source licence changed')
        doi = f'10.1594/PANGAEA.{dataset_id}'
        if doi.lower() in old_dois:
            raise RuntimeError('Dataset already ingested: ' + doi)
        article_doi, article_year, relation = PAPERS[dataset_id]
        if article_doi.lower() not in head.lower():
            raise RuntimeError('Native article relation missing')
        cr_path = RAW / ('crossref-' + sha(article_doi.lower().encode())[:16] + '.json')
        cr_bytes = cr_path.read_bytes()
        cr = json.loads(cr_bytes)['message']
        if cr['DOI'].lower() != article_doi.lower() or cr['published']['date-parts'][0][0] != article_year:
            raise RuntimeError('Crossref paper identity/year changed')
        reader = csv.DictReader(tab.strip().splitlines(), delimiter='\t')
        rows = list(reader)
        columns = reader.fieldnames
        if dataset_id == 818921:
            age_column, transform = 'Varve age [a BP]', 'ka BP = published varve age [a BP] / 1000'
        elif 'Age [ka BP]' in columns:
            age_column, transform = 'Age [ka BP]', 'identity: published age [ka BP]'
        else:
            age_column, transform = 'Age [a AD/CE]', 'ka BP = (1950 - published year CE) / 1000'
        if age_column not in columns:
            raise RuntimeError('Reviewed chronology column missing')
        header_line = next(i for i, line in enumerate(text.splitlines(), 1) if line == '\t'.join(columns))
        event_line = re.search(r'Event\(s\):\s*([^\n]+)', head).group(1)
        event = event_line.split(' * ')[0].split(' (')[0].strip()
        latitude = float(re.search(r'LATITUDE:\s*([-\d.]+)', event_line).group(1))
        longitude = float(re.search(r'LONGITUDE:\s*([-\d.]+)', event_line).group(1))
        elevation = float(re.search(r'ELEVATION:\s*([-\d.]+)', event_line).group(1))
        if not (28 <= latitude <= 48 and -10 <= longitude <= 42):
            raise RuntimeError('Event outside declared region')
        citation = re.search(r'Citation:\s*([^\n]+)', head).group(1)
        dataset_year = int(re.search(r'\((\d{4})\):', citation).group(1))
        campaign = re.search(r'CAMPAIGN:\s*([^*\n]+)', event_line)
        note = re.search(r'Comment:\s*([^\n]+)', head)
        qc = ['Published age model retained; no radiocarbon recalibration, tuning or interpolation performed',
              'Native parameter metadata reviewed; chronology uncertainty/model dependence not independently audited']
        if note:
            qc.append(note.group(1).strip())
        if dataset_id == 438795:
            qc.append('Related DOI identifies a contextual editorial, not a verified original data paper; dataset is citable independently')
        if dataset_id == 818921:
            qc += ['Use explicit varve BP column: AD/CE column includes unsigned pre-CE magnitudes and is not used',
                   'XRF cps are instrument response; no conversion to concentration or inter-instrument harmonization',
                   'Mo05 is a published composite of parallel cores, not an independent observation at each constituent core']
        if dataset_id in (789685, 789686, 789690):
            qc += ['Cores share a published age grid but contain different/missing values; missing cells are not observations',
                   'Co-located Gulf of Taranto cores are not asserted statistically independent; composite dataset789691 excluded']
        if dataset_id == 871130:
            qc += ['Source labels annual SST; article identifies G. bulloides Mg/Ca as spring signal; kept in a separate compatibility group',
                   'Source minimum/maximum bounds preserved separately, not converted to invented symmetric errors']
        rid = f'pangaea-{dataset_id}'
        rec = dict(id=rid, name=event, core=event, dataset_id=dataset_id, provider='PANGAEA', realm='continental' if dataset_id == 818921 else 'marine',
                   archive_type='lake_sediment' if dataset_id == 818921 else 'marine_sediment', latitude=latitude, longitude=longitude,
                   elevation_m=elevation if dataset_id == 818921 else None, water_depth_m=62 if dataset_id == 818921 else -elevation,
                   source_url=f'https://doi.pangaea.de/{doi}', data_url=f'https://doi.pangaea.de/{doi}?format=textfile', dataset_doi=doi,
                   dataset_publication_year=dataset_year, publication_year=article_year if dataset_id != 438795 else None,
                   paper_doi=article_doi if dataset_id != 438795 else None, paper_title=cr['title'][0] if dataset_id != 438795 else None,
                   related_reference_doi=article_doi if dataset_id == 438795 else None,
                   related_reference_year=article_year if dataset_id == 438795 else None,
                   related_reference_title=cr['title'][0] if dataset_id == 438795 else None,
                   paper_relation=relation, title=citation, citation=citation,
                   authors=[{'given': a.get('given'), 'family': a.get('family')} for a in cr.get('author', [])],
                   license='CC-BY-3.0', license_url='https://creativecommons.org/licenses/by/3.0/', raw_sha256=sha(raw), xml_sha256=sha(xml),
                   raw_path=str((RAW / f'{dataset_id}.tsv').relative_to(ROOT)).replace('\\', '/'),
                   crossref_sha256=sha(cr_bytes), source_event=event, physical_core_key='PANGAEA:event:'+event,
                   campaign=campaign.group(1).split(' (URI:')[0].strip() if campaign else None,
                   chronology_status='published_BP_as_archived_not_independently_recalibrated' if age_column != 'Age [a AD/CE]' else 'published_calendar_CE_converted_to_BP1950',
                   age_scale_status='Published '+age_column+'; '+transform, chronology_method=transform, age_unit_original=age_column,
                   review_status='native_table_metadata_and_bibliographic_identity_verified', qc_notes=qc,
                   inventory_links=[r['id'] for r in inventory['records'] if str(r.get('dataset_doi', '')).lower() == doi.lower()],
                   source_locators=[dict(resource='native TSV', parameter_section='Parameter(s)', header_line=header_line)])
        records.append(rec)
        per_series = []
        for column, proxy, label, unit, group, family, kind, method, taxon in specs(dataset_id):
            if column not in columns:
                raise RuntimeError('Reviewed proxy column missing: ' + column)
            selected_rows, missing, rejected = [], 0, []
            bounds = []
            for index, row in enumerate(rows, 1):
                val = number(row[column])
                if val is None:
                    if (row[column] or '').strip():
                        rejected.append(dict(source_row=index, value_original=row[column], reason='non_numeric_or_censored'))
                    else:
                        missing += 1
                    continue
                age = to_age(row[age_column], age_column)
                selected_rows.append([age, val, index, header_line+index, row[age_column], row[column], None, None, row.get('Depth sed [m]')])
                if dataset_id == 871130:
                    bounds.append([index, number(row['SST (1-12) min [°C]']), number(row['SST (1-12) max [°C]']), row['SST (1-12) min [°C]'], row['SST (1-12) max [°C]']])
            selected_rows.sort(key=lambda row: float('inf') if row[0] is None else row[0])
            signature = sha(json.dumps([[r[0], r[1]] for r in selected_rows], separators=(',', ':')).encode())
            if signature in source_sigs:
                raise RuntimeError('Exact age/value duplicate series: ' + str(source_sigs[signature]))
            source_sigs.setdefault(signature, []).append(rid+':'+proxy)
            obj = dict(id=rid+':'+proxy, record_id=rid, proxy=proxy, label=label, unit=unit, compatibility_group=group,
                       family=family, variable=proxy, method=method, evidence_type=kind, taxon=taxon,
                       source_column=column, original_unit='‰ PDB (metadata explicitly VPDB)' if dataset_id == 836213 else unit,
                       age_column_original=age_column, age_transformation=transform, raw_sha256=sha(raw), dataset_doi=doi,
                       depth_frame='m composite depth' if dataset_id in (836213, 818921) else 'm sediment depth' if 'Depth sed [m]' in columns else None,
                       uncertainty_type='source_asymmetric_min_max_unspecified_confidence' if bounds else 'not_supplied_for_selected_column',
                       rows=selected_rows)
            if bounds:
                obj['uncertainty_bounds_row_format']=['source_row', 'lower', 'upper', 'lower_original', 'upper_original']
                obj['uncertainty_bounds']=bounds
            ages = [r[0] for r in selected_rows if r[0] is not None]
            audit = dict(series_id=obj['id'], source_column=column, observations=len(selected_rows), source_rows=len(rows),
                         missing_cells=missing, rejected_cells=rejected, unknown_ages=sum(r[0] is None for r in selected_rows),
                         observed_zeros=sum(r[1] == 0 for r in selected_rows), negative_ages=sum(r[0] is not None and r[0] < 0 for r in selected_rows),
                         repeated_ages=sum(c-1 for c in Counter(ages).values() if c > 1), source_row_unique=len({r[2] for r in selected_rows}) == len(selected_rows),
                         repeated_age_value_depth=sum(c-1 for c in Counter((r[0], r[1], r[8]) for r in selected_rows).values() if c > 1),
                         age_min_ka_bp=min(ages) if ages else None, age_max_ka_bp=max(ages) if ages else None, numeric_signature_sha256=signature)
            series.append(obj)
            per_series.append(audit)
        rec['sample_count'] = len({r[2] for s in series if s['record_id'] == rid for r in s['rows']})
        record_ages = [r[0] for s in series if s['record_id'] == rid for r in s['rows'] if r[0] is not None]
        rec['age_min_ka_bp'], rec['age_max_ka_bp'] = min(record_ages), max(record_ages)
        audits.append(dict(dataset_id=dataset_id, record_id=rid, source_rows=len(rows), dataset_doi=doi, raw_sha256=sha(raw), xml_sha256=sha(xml), series=per_series))
    return dict(fragment_version='pangaea-quantitative-v3-2026-10-28', records=records, series=series,
                audit=audits, rejected_candidates=[dict(dataset_id=854682, reason='Native related citation is submitted without verified final paper DOI; retained for bibliography/chronology review')],
                duplicate_review=dict(exact_existing_datasets=0, exact_numeric_series=0, note='Cross-repository/physical-core identity remains a separate integration review; no fuzzy merge or independence claim'),
                transformations=['Selected finite native cells; missing/censored cells not coerced',
                                 'Age [ka BP] identity; AD/CE -> (1950-CE)/1000; explicit varve[a BP] /1000',
                                 'No calibration, concentration scaling, chronological interpolation or proxy imputation',
                                 'VPDB label follows explicit parameter comment; isotope numbers unchanged'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--inspect', action='store_true')
    args = parser.parse_args()
    if args.download:
        with ThreadPoolExecutor(max_workers=3) as executor:
            for dataset_id in executor.map(acquire, IDS):
                print('cached', dataset_id)
        acquire_papers()
    if args.inspect:
        for dataset_id in IDS:
            data = inspect(dataset_id)
            print(json.dumps(data, ensure_ascii=True))
    else:
        result = curate()
        output = RAW.parent / 'pangaea_curated.json'
        output.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':'))+'\n', encoding='utf-8')
        print(json.dumps(dict(path=str(output), records=len(result['records']), series=len(result['series']), observations=sum(len(s['rows']) for s in result['series']))))
