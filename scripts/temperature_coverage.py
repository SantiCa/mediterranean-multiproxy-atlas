"""Build a source-level temperature queue; metadata hits are never observations.

Offline by default. --fetch expands the previous sediment-biased DataCite query
without requiring 'core'/'sediment', so continental temperature is discoverable.
NOAA is inspected at table/file grain, not just its lossy canonical proxy list.
The two providers' counts have different grains and must not be added as cores.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/discovery'))
from pangaea_inventory import fetch, in_bbox, FIELDS

CACHE = ROOT / 'data/interim/temperature_coverage'
QUERY = ('geoLocations.geoLocationPoint.pointLatitude:[28 TO 48] AND '
         'geoLocations.geoLocationPoint.pointLongitude:[-10 TO 42] AND '
         '(subjects.subject:temperature OR titles.title:temperature OR '
         'titles.title:paleotemperature* OR subjects.subject:alkenone* OR '
         'titles.title:SST OR titles.title:TEX86)')


def classify(title, parameters):
    """Conservative triage, not scientific admission or method equivalence.

    Temperature can be an analytical setting (Rock-Eval, Curie) or a present-day
    measurement. Mg/Ca and delta18O alone do not establish a temperature estimate.
    Unknown season/calibration remain unknown; substring 'G.' is not a taxon.
    """
    text = (title + ' ' + ' '.join(parameters)).lower()
    if re.search(r'rock.?eval|thermomagnetic|curie temperature|pyrolysis', title.lower()):
        return 'outside_target_temperature', 'analytical_temperature_not_climate', None
    if re.search(r'downhole temperature|in situ|microelectrode|microsensor|ctd cast|benthic chamber|oxygen consumption|p-wave velocity', title.lower()):
        return 'outside_target_temperature', 'instrument_or_modern_profile_not_paleotemperature', None
    target = ('bottom_water' if re.search(r'bottom.water|deep.water|\bbwt\b', text)
              else 'sea_surface' if re.search(r'sea.surface|\bsst\b|paleo.sst', text)
              else 'air' if re.search(r'air temperature|july.air|pollen.based.*climate', text)
              else 'ground_surface' if 'borehole' in text else None)
    explicit = bool(re.search(r'temperature|paleotemperature|palaeotemperature|\bsst\b|\bbwt\b', text))
    return ('pending_native_review', 'temperature_metadata_requires_column_age_method_review', target) if explicit else (
        'metadata_ambiguous', 'index_ratio_or_related_keyword_is_not_temperature', target)


def datacite_pages(online=False):
    """Require stable totals/unique DOIs and retain exact requests and hashes."""
    datasets, receipts, seen = [], [], set()
    total = None
    for page in range(1, 51):
        url = 'https://api.datacite.org/dois?' + urlencode({
            'query': QUERY, 'client-id': 'pangaea.repository', 'page[size]': 1000,
            'page[number]': page, 'fields[dois]': FIELDS, 'sort': 'name'})
        path = CACHE / 'datacite' / f'{page:04d}.json'
        if not online and not path.exists():
            raise FileNotFoundError('Run --fetch once to establish the named metadata snapshot')
        raw, receipt = fetch(url, path)
        result = json.loads(raw)
        if total is None:
            total = result['meta']['total']
        if result['meta']['total'] != total:
            raise ValueError('Result total changed during pagination; new snapshot required')
        receipts.append(receipt)
        for index, item in enumerate(result['data']):
            a = item['attributes']; doi = a['doi'].lower()
            if doi in seen:
                raise ValueError('Duplicate DOI across pages: ' + doi)
            seen.add(doi)
            points = [g['geoLocationPoint'] for g in a.get('geoLocations', [])
                      if in_bbox(g.get('geoLocationPoint', {}).get('pointLatitude'),
                                 g.get('geoLocationPoint', {}).get('pointLongitude'))]
            datasets.append(dict(dataset_doi=doi, title='; '.join(t['title'] for t in a['titles']),
                subjects=a.get('subjects', []), points=points, publication_year=a.get('publicationYear'),
                rights=a.get('rightsList', []), related_identifiers=a.get('relatedIdentifiers', []),
                raw_sha256=receipt['sha256'], source_locator=f'data[{index}].attributes',
                request_url=url, accessed_at_utc=receipt['accessed_at_utc']))
        print(f'Temperature metadata page {page}: {len(seen)}/{total}', flush=True)
        if len(seen) == total:
            return datasets, receipts, total
        if not result['data'] or len(seen) > total:
            raise ValueError('Incomplete or inconsistent pagination')
    raise ValueError('Explicit metadata paging bound exceeded')


def admitted_sources(seed):
    """Index admitted temperature series by their actual source, not core DOI."""
    records = {r['id']: r for r in seed['records']}
    doi_index, noaa_index = {}, {}
    for s in seed['series']:
        if s.get('family_id') != 'temperature' and s.get('family') != 'Temperatura':
            continue
        r = records[s['record_id']]
        summary = {k: s.get(k) for k in ('id', 'record_id', 'compatibility_group', 'unit', 'method', 'chronology_status')}
        summary['observations'] = len(s['rows'])
        doi = s.get('dataset_doi') or r.get('dataset_doi')
        if doi:
            doi_index.setdefault(doi.lower(), []).append(summary)
        url = s.get('source_url') or s.get('data_url') or r.get('data_url')
        if r['provider'].startswith('NOAA') and url:
            noaa_index.setdefault(url, []).append(summary)
    return doi_index, noaa_index


def build(online=False, seed_path=None):
    """Save a reproducible queue plus separate denominators and limitations."""
    seed_path = seed_path or ROOT / 'data/processed/atlas-v3.json'
    seed_bytes = seed_path.read_bytes(); seed = json.loads(seed_bytes)
    admitted_doi, admitted_url = admitted_sources(seed)
    fresh, receipts, total = datacite_pages(online)
    old_path = ROOT / 'data/interim/discovery_pangaea/inventory.json'
    old_bytes = old_path.read_bytes(); old = json.loads(old_bytes)
    merged = {d['dataset_doi'].lower(): dict(d, query_origin=['temperature']) for d in fresh}
    for d in old['datasets']:
        text = d['title'] + ' ' + ' '.join(x['subject'] for x in d['subjects'])
        if not re.search(r'temperature|alkenone|\bsst\b|tex86|mg/ca', text, re.I):
            continue
        doi = d['dataset_doi'].lower()
        if doi in merged:
            merged[doi]['query_origin'].append('legacy_sediment')
        else:
            merged[doi] = dict(d, query_origin=['legacy_sediment'])
    rows = []
    for doi, d in sorted(merged.items()):
        if not d['points']:
            continue  # Separate indexed coordinates can match different locations.
        parameters = [x['subject'] for x in d['subjects'] if x.get('subjectScheme') == 'Parameter']
        status, reason, target = classify(d['title'], parameters)
        admitted = admitted_doi.get(doi, [])
        if admitted:
            status, reason = 'quantitative_admitted', 'temperature_series_present_in_selected_seed'
        rows.append(dict(id=doi, provider='PANGAEA', grain='dataset_doi_not_core',
            source_url='https://doi.org/' + doi, title=d['title'], points=d['points'],
            status=status, reason=reason, target_hint=target,
            original_parameters=parameters, methods=[x['subject'] for x in d['subjects'] if x.get('subjectScheme') == 'Method'],
            dataset_publication_year=d['publication_year'], rights=d.get('rights'),
            raw_sha256=d['raw_sha256'], source_locator=d['source_locator'],
            query_origin=d['query_origin'], admitted_series=admitted,
            seasonality=None, calibration=None, chronology=None,
            native_download_verified=bool(admitted)))
    # A metadata query is not a complete catalogue: retain reviewed temperature
    # sources absent from its result, rather than reporting them as unimported.
    seen_dois = {r['id'] for r in rows}
    by_record = {r['id']: r for r in seed['records']}
    for doi, series in sorted(admitted_doi.items()):
        r = by_record[series[0]['record_id']]
        if r['provider'] != 'PANGAEA' or doi in seen_dois or not in_bbox(r['latitude'], r['longitude']):
            continue
        rows.append(dict(id=doi, provider='PANGAEA', grain='dataset_doi_not_core',
            source_url='https://doi.org/' + doi, title=r.get('dataset_title') or r['name'],
            points=[dict(latitude=r['latitude'], longitude=r['longitude'])],
            status='quantitative_admitted', reason='reviewed_source_absent_from_metadata_query',
            target_hint=None, original_parameters=[], methods=[],
            dataset_publication_year=r.get('dataset_citation_year'), rights=r.get('license'),
            raw_sha256=r.get('raw_sha256') or r.get('source_sha256'), source_locator='selected_seed/series/source',
            query_origin=['active_seed_only'], admitted_series=series,
            seasonality=None, calibration=None, chronology=None, native_download_verified=True))
    # Inspect full NOAA file variables: canonical inventory tags lose tables.
    study_receipts = []
    for path in sorted((ROOT / 'data/interim/discovery_continental/studies').glob('*.json')):
        if path.name.endswith('.request.json'):
            continue
        raw = path.read_bytes(); source_hash = hashlib.sha256(raw).hexdigest()
        for study in json.loads(raw).get('study', []):
            for site in study.get('site', []):
                geo = site.get('geo', {}).get('geometry', {})
                if geo.get('type', '').upper() != 'POINT':
                    continue
                # NOAA paleo endpoint stores POINT as latitude, longitude;
                # canonical inventory cross-checks against named bounds.
                coord = geo.get('coordinates', [])
                if len(coord) != 2:
                    continue
                lat, lon = map(float, coord)
                bounds = site.get('geo', {}).get('properties', {})
                for field, value in (('southernmostLatitude', lat), ('northernmostLatitude', lat),
                                     ('westernmostLongitude', lon), ('easternmostLongitude', lon)):
                    if bounds.get(field) is not None and float(bounds[field]) != value:
                        raise ValueError('NOAA POINT and bounds disagree; manual spatial review required')
                if not in_bbox(lat, lon):
                    continue
                for table in site.get('paleoData', []):
                    for f in table.get('dataFile', []):
                        variables = f.get('variables', [])
                        thermal = [v for v in variables if 'temperature' in (v.get('cvWhat') or '').lower()]
                        if not thermal:
                            continue
                        title = study['studyName'] + ' | ' + (table.get('dataTableName') or '')
                        status, reason, target = classify(title, [v.get('cvWhat') or '' for v in thermal])
                        url = f['fileUrl']; admitted = admitted_url.get(url, [])
                        if admitted:
                            status, reason = 'quantitative_admitted', 'temperature_series_present_in_selected_seed'
                        rows.append(dict(id='noaa:' + str(study['NOAAStudyId']) + ':' + str(site['NOAASiteId']) + ':' + str(table['NOAADataTableId']) + ':' + hashlib.sha256(url.encode()).hexdigest()[:12],
                            provider='NOAA WDS', grain='site_table_file_not_core', source_url=url,
                            study_id=str(study['NOAAStudyId']), site_id=str(site['NOAASiteId']),
                            table_id=str(table['NOAADataTableId']), title=title, name=site['siteName'],
                            latitude=lat, longitude=lon, status=status, reason=reason, target_hint=target,
                            original_variables=thermal, admitted_series=admitted,
                            raw_sha256=source_hash, source_locator=f"study[{study['NOAAStudyId']}]/site[{site['NOAASiteId']}]/paleoData[{table['NOAADataTableId']}]/dataFile",
                            seasonality=None, calibration=None, chronology=None,
                            native_download_verified=bool(admitted)))
        study_receipts.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=source_hash))
    counts = {provider: dict(Counter(r['status'] for r in rows if r['provider'] == provider)) for provider in ('PANGAEA', 'NOAA WDS')}
    report = dict(task='PROXY-COVERAGE-TEMP', bbox=[-10, 28, 42, 48], seed_version=seed['version'],
        inputs=dict(seed_sha256=hashlib.sha256(seed_bytes).hexdigest(), legacy_pangaea_sha256=hashlib.sha256(old_bytes).hexdigest(),
                    datacite_query=QUERY, datacite_total=total, datacite_pagination_complete=True,
                    datacite_receipts=receipts, noaa_study_snapshots=study_receipts),
        counts_by_provider_and_status=counts,
        limitations=['Counts are dataset DOIs or NOAA site/table/files, never independent cores',
            'Complete only for named cached metadata searches and point post-filter, not all published temperature records',
            'Bounding boxes/missing points excluded; lack of proxy metadata is not absence of proxy',
            'Status quantitative_admitted means at least one reviewed temperature series, not every column or full original coverage',
            'Null seasonality/calibration/chronology are unresolved metadata, not annual/standard equivalents',
            'Native download verification only asserted for admitted series; other local draft files are not counted as reviewed',
            'Duplicate and ambiguous core identity require numerical/native review; DOIs are not merged by coordinates'],
        candidates=rows)
    target_path = ROOT / 'reports/temperature_coverage.json'
    target_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(counts, ensure_ascii=False))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--seed', type=Path)
    args = parser.parse_args()
    build(args.fetch, args.seed)
