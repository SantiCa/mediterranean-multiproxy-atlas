"""Append missing columns from a bounded PANGAEA priority batch to immutable v5.

--prepare writes inspectable column/event contracts; default extracts offline.
--fetch only restores the pinned native TSV/XML resources named in the manifest.
Multi-event tables require exact Event cells. No new age models or proxy values
are estimated here. Raw counts, percentages, logs and analytical contexts remain
distinct. Access errors and unresolved licences remain explicit review entries.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / 'scripts/discovery'))
import curate_pangaea_v5 as native
from priority_vocabulary import ratio_alias, target_family

RAW = ROOT / 'data/interim/priority_v6/pangaea'
MANIFEST = ROOT / 'reports/priority_v6_candidates.json'
CONTRACT = Path(__file__).with_name('priority_v6_sources.json')
FRAGMENT = ROOT / 'data/interim/priority_v6/pangaea_curated.json'
AUDIT = ROOT / 'reports/priority_v6_audit.json'
BASE = ROOT / 'data/processed/atlas-v5.json'
FAMILIES = {'polen': 'Polen', 'corrientes': 'Sedimentología',
            'oxigenacion_bent': 'Oxigenación bentónica', 'redox': 'Geoquímica elemental',
            'xrf_razones': 'Geoquímica elemental'}


def resource(entry, extension, fetch=False):
    """Require pinned bytes; do not silently refresh changed provider snapshots."""
    path = RAW / f"{entry['id']}.{extension}"
    if not path.exists() and not fetch:
        raise FileNotFoundError(f'Missing original {path}; restore with --fetch')
    url = entry['source_url'] + ('?format=textfile' if extension == 'tsv' else '')
    expected = entry['sha'] if extension == 'tsv' else entry['xml_sha']
    return native.get(url, path, expected, accept='application/vnd.pangaea.metadata+xml' if extension == 'xml' else None)


def source_title(head):
    """Dataset title only; never treat its citation year as article year."""
    line = next((x for x in head.splitlines() if x.startswith('Citation:')), '')
    return re.sub(r'^.*?\(\d{4}\):\s*', '', line).split('[dataset]')[0].strip()


def contexts(column, title=''):
    """Retain distinctions hidden by identical parameter labels/units."""
    p, h, comment = column['name'] or '', column['header'], column.get('comment') or ''
    text = h + ' ' + comment
    if 'sortable silt' in p.lower():
        if re.search(r'mean.*carb.free', text, re.I):
            return 'sortable_silt_native_mean_carb_free_percent_label_requires_review'
        if re.search('contourite', text, re.I):
            return 'sortable_silt_percent_contourites'
        if re.search('pelagic', text, re.I):
            return 'sortable_silt_percent_pelagics'
    if re.search(r'excl.*pin|without.*pin|sin.*pin', text, re.I):
        return 'pollen_sum_excludes_pinus'
    if column.get('family') == 'corrientes':
        if re.search(r'non.carbonate|carb.free|carbonate.free', title + ' ' + text, re.I):
            return 'grain_fraction_noncarbonate'
        if re.search(r'total fraction|bulk sediment', title, re.I):
            return 'grain_fraction_total'
    if re.search('pore fluids', title, re.I):
        return 'matrix_pore_fluid'
    if re.search('soluble salts', title, re.I):
        return 'matrix_soluble_salt'
    return None


def paper_reference(head, supplied, fetch):
    """Resolve an explicit native article relation without guessing a paper year.

    A unique Related-to DOI is retained as that relation, not asserted to be the
    original measurement paper. Multiple relations remain unresolved. Crossref
    identifies the publication; it does not validate its environmental argument.
    """
    doi = (supplied or {}).get('doi')
    relation = 'native_supplement_to' if doi else None
    if not doi:
        match = re.search(r'(?m)^(?:In supplement to|Supplement to|Related to):\t([^\n]*(?:\n\t[^\n]*)*)', head)
        candidates = sorted(set(re.findall(r'(?:doi\.org/|doi:\s*)(10\.[^\s;,]+)', match[0], re.I))) if match else []
        candidates = [d.rstrip('.') for d in candidates if not d.lower().startswith('10.1594/pangaea')]
        if len(candidates) == 1:
            doi = candidates[0]; relation = 'native_related_to' if match[0].startswith('Related to') else 'native_supplement_to'
    if not doi:
        return None
    path = RAW / ('crossref-' + native.sha(doi.lower().encode())[:16] + '.json')
    if not path.exists() and not fetch:
        return dict(doi=doi, relation=relation, status='native_relation_unverified_with_crossref', year=None)
    raw = native.get('https://api.crossref.org/works/' + quote(doi, safe=''), path, limit=3_000_000)
    message = json.loads(raw)['message']
    if message['DOI'].lower() != doi.lower():
        raise ValueError('Crossref DOI differs from native article relation')
    dates = {key: value['date-parts'] for key, value in message.items()
             if key in ('published', 'published-print', 'published-online', 'issued') and value.get('date-parts')}
    year = (dates.get('published-print') or dates.get('published-online') or dates.get('issued') or [[None]])[0][0]
    return dict(doi=doi, relation=relation, status='crossref_identity_verified',
                year=year, dates=dates, title=(message.get('title') or [None])[0], sha256=native.sha(raw))


def prepare(fetch=False):
    """Create explicit missing-column contracts without changing existing releases."""
    manifest = json.loads(MANIFEST.read_text(encoding='utf8'))
    base_bytes = BASE.read_bytes(); base = json.loads(base_bytes)
    existing = set()
    for s in base['series']:
        doi = (s.get('dataset_doi') or '').lower()
        if not doi:
            r = next(r for r in base['records'] if r['id'] == s['record_id'])
            doi = (r.get('dataset_doi') or '').lower()
        if s.get('source_column_index') is not None:
            existing.add((doi, s['source_column_index']))
        existing.add((doi, s.get('source_column')))
    entries = []
    for src in manifest['sources']:
        entry = {k: src.get(k) for k in ('id', 'source_url', 'sha', 'xml_sha', 'retrieved_at_utc')}
        if 'error' in src:
            entries.append(dict(entry, status='held', reason=src['error'])); continue
        tsv, xml = resource(src, 'tsv', fetch), resource(src, 'xml', fetch)
        head, header, rows = native.parse_tsv(tsv)
        cols, events, paper, lic, lic_url = native.xml_meta(xml)
        title = source_title(head)
        entry.update(title=title, header=header, events=events, license=lic,
                     license_url=lic_url, paper=paper, source_rows=len(rows), columns=[])
        reason = None
        if len(cols) != len(header) or any(c['short'] and not h.startswith(c['short']) for c, h in zip(cols, header)):
            reason = 'native XML columns do not align positionally with TSV'
        elif not lic or not re.search(r'/by/(3\.0|4\.0)/', lic_url or ''):
            reason = 'licence requires separate review before new redistribution (no adaptation assumed)'
        elif not events or any(not (-10 <= e['lon'] <= 42 and 28 <= e['lat'] <= 48) for e in events):
            reason = 'outside configured region or no named georeferenced event'
        elif len(events) > 1 and 'Event' not in header:
            reason = 'multi-event table lacks unambiguous Event column'
        age = native.age_rule(header)
        if not age:
            reason = reason or 'no admitted native age column; model link still needs review'
        elif re.search(r'14c|radiocarbon', header[age[0]] + ' ' + (cols[age[0]]['comment'] or ''), re.I):
            reason = reason or 'radiocarbon age requires explicit calendar chronology review'
        if reason:
            entries.append(dict(entry, status='held', reason=reason)); continue
        entry.update(age_column=age[0], age_transformation=age[1])
        entry['paper'] = paper_reference(head, paper, fetch)
        for k, col in enumerate(cols):
            family = target_family(col['name'] or '', title,
                'marine' if all(float(e.get('elevation') or 0) < 0 for e in events) else 'unknown')
            if not family or re.search(r'error|standard deviation|uncertainty', col['name'] or '', re.I):
                continue
            if (src['source_url'].split('/')[-1].lower(), k) in existing or (src['source_url'].split('/')[-1].lower(), header[k]) in existing:
                continue
            unit = col['unit'] or (re.search(r'\[([^\]]+)\]', header[k]) or [None, None])[1] or 'sin unidad'
            item = dict(col, column=k, header=header[k], unit=unit, family=family,
                        alias=ratio_alias(col['name'] or ''), status='native_contract_checked')
            item['comparison_context'] = contexts(item, title)
            entry['columns'].append(item)
        entry.update(status='ready' if entry['columns'] else 'already_covered_or_no_target_columns')
        entries.append(entry)
    result = dict(parent_version=base['version'], parent_sha256=native.sha(base_bytes),
                  bbox=[-10, 28, 42, 48], datasets=entries,
                  limits=['Column contracts checked against native TSV/XML; independent scientific peer review pending',
                          'Only native point ages; no new interpolation, normalization, ratio calculation or forest classification'])
    CONTRACT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print('Priority contracts', dict(Counter(e['status'] for e in entries)))


def curate(fetch=False):
    """Extract finite native cells, preserving row/line and explicit quality holds."""
    contract = json.loads(CONTRACT.read_text(encoding='utf8'))
    if native.sha(BASE.read_bytes()) != contract['parent_sha256']:
        raise ValueError('Parent changed; review and regenerate priority contracts')
    records, series, quarantined, audit = {}, [], [], []
    for entry in contract['datasets']:
        if entry['status'] != 'ready':
            continue
        raw = resource(entry, 'tsv', fetch); resource(entry, 'xml', fetch)
        head, header, rows = native.parse_tsv(raw)
        if header != entry['header']:
            raise ValueError('Pinned source header differs from contract')
        i = str(entry['id']); age = native.age_rule(header)
        labels = {e['label']: e for e in entry['events']}
        if len(labels) != len(entry['events']):
            raise ValueError('Ambiguous event labels')
        event_col = header.index('Event') if 'Event' in header else None
        if event_col is not None and any(cells[event_col] not in labels for _, _, cells in rows):
            raise ValueError('Row Event is absent from native XML')
        doi = '10.1594/PANGAEA.' + i
        paper = entry.get('paper') or {}
        if paper.get('sha256'):
            cr = RAW / ('crossref-' + native.sha(paper['doi'].lower().encode())[:16] + '.json')
            if native.sha(cr.read_bytes()) != paper['sha256']:
                raise ValueError('Pinned Crossref identity metadata changed')
        depth = native.depth_column(header)
        for label, event in labels.items():
            rid = 'pangaea6-' + native.slug(label).lower()
            elevation = native.number(event.get('elevation') or '')
            record = records.setdefault(rid, dict(id=rid, name=label, core=label, source_event=label,
                physical_core_key='PANGAEA:event:' + label, provider='PANGAEA',
                realm='marine' if elevation is not None and elevation < 0 else 'unknown',
                archive_type='sediment', latitude=event['lat'], longitude=event['lon'],
                elevation_m=elevation, water_depth_m=-elevation if elevation is not None and elevation < 0 else None,
                source_url=entry['source_url'], dataset_doi=doi, publication_year=paper.get('year'), paper_doi=paper.get('doi'),
                license=entry['license'], license_url=entry['license_url'], source_files=[],
                campaign=event.get('campaign'), inventory_ids=[], qc_notes=[],
                review_status='Native columns, units, events and age verified; interpretation/chronology review remains explicit'))
            record['source_files'].append(dict(dataset_doi=doi, url=entry['source_url'],
                raw_sha256=entry['sha'], xml_sha256=entry['xml_sha'],
                license=entry['license'], license_url=entry['license_url']))
            for col in entry['columns']:
                out, censored, missing = [], 0, 0
                for row, line, cells in rows:
                    if event_col is not None and cells[event_col] != label:
                        continue
                    value = native.number(cells[col['column']])
                    if value is None:
                        missing += not cells[col['column']].strip()
                        censored += bool(cells[col['column']].strip()); continue
                    age_value = native.number(cells[age[0]])
                    out.append([age[2](age_value) if age_value is not None else None, value,
                        row, line, cells[age[0]], cells[col['column']], None, None,
                        cells[depth] if depth is not None else None])
                if len(out) < 3:
                    continue
                out.sort(key=lambda r: (r[0] is None, r[0] or 0, r[2]))
                proxy = native.slug(col['name']) + '_' + native.slug(col['unit'])
                context = col.get('comparison_context')
                scanner = bool(re.search(r'core scanner|element scanner|\bcps\b|counts', (col['method'] or '') + ' ' + col['unit'], re.I))
                notes = ['Original source values; no new proxy calibration or forest-type inference']
                if not paper.get('year'):
                    notes.append('Article DOI/year not independently resolved; dataset citation is retained')
                elif paper.get('relation') == 'native_related_to':
                    notes.append('Article linked as Related to by PANGAEA; not an independent claim of original measurement provenance')
                if scanner:
                    notes.append('XRF scanner signal/ratio: instrument and matrix dependent; not calibrated elemental concentration')
                if col['family'] in ('redox', 'oxigenacion_bent'):
                    notes.append('Contextual benthic/redox indicator; not a direct dissolved-oxygen reconstruction')
                if col['family'] == 'corrientes':
                    notes.append('Published grain-size indicator; not converted to current velocity')
                if col['family'] == 'polen':
                    notes.append('Taxon/type and native denominator retained; count, concentration and percentage are different quantities')
                if context:
                    notes.append('Comparison context: ' + context)
                if 'mean_carb_free_percent' in (context or ''):
                    notes.append('Source labels this mean in percent; do not reinterpret as micrometres')
                if re.search(r'log-', col['name'], re.I):
                    notes.append('Native log ratio; logarithm base not independently verified, no exponentiation')
                ages = [r[0] for r in out if r[0] is not None]
                digest = native.sha(json.dumps(out, separators=(',', ':')).encode())[:10]
                sid = f'pangaea6-{i}:{native.slug(label)}:col{col["column"]}~{digest}'
                s = dict(id=sid, record_id=rid, proxy=proxy, variable_id=proxy,
                    label=col['name'] + (' · ' + col['comment'] if col.get('comment') else ''),
                    unit=col['unit'], original_unit=col['unit'], family=FAMILIES[col['family']],
                    proxy_families=[col['family']], parameter_name_pangaea=col['name'],
                    parameter_comment=col.get('comment'), method=col['method'] or 'not declared in native metadata',
                    compatibility_group=proxy + '_' + native.slug(col['method'] or 'unspecified') +
                        ('_context_' + native.slug(context) if context else '') +
                        ('_dataset_' + i if scanner or col['unit'] == '#' else ''),
                    comparison_context_key=context, evidence_type='as_archived_parameter', taxon=col['name'] if col['family'] == 'polen' else None,
                    dataset_doi=doi, source_url=entry['source_url'] + '?format=textfile',
                    source_column=col['header'], source_column_index=col['column'], source_header_original=header,
                    raw_sha256=entry['sha'], xml_sha256=entry['xml_sha'], source_event=label,
                    citation=next(l.split('\t',1)[-1] for l in head.splitlines() if l.startswith('Citation:')),
                    license=entry['license'], license_url=entry['license_url'], paper_doi=paper.get('doi'), publication_year=paper.get('year'),
                    publication_relation=paper.get('relation'), paper_identity_sha256=paper.get('sha256'),
                    chronology_status='published_ka_reference_unspecified' if age[1] == native.UNSPECIFIED_KA else 'published_BP',
                    chronology_label='Published native age; calendar harmonization not independently audited',
                    age_column_original=header[age[0]], age_column_index=age[0], age_unit_original=header[age[0]],
                    age_scale=age[1], age_model=age[1], age_transformation=age[1],
                    depth_frame=header[depth] if depth is not None else 'no depth column in source',
                    uncertainty_type='not supplied for selected value; no error estimated',
                    rows=out, qc_notes=notes, review_status='native_contract_checked; independent_scientific_review_pending',
                    source_dataset_title=entry['title'],
                    search_aliases=[col['name'], col.get('alias') or '', col['family'],
                        'bosque vegetación árboles pollen' if col['family'] == 'polen' else
                        'corrientes paleocorriente granulometría' if col['family'] == 'corrientes' else
                        'oxigenación profunda bentónica redox' if col['family'] in ('redox','oxigenacion_bent') else
                        'ratios razones elementos inorgánicos'])
                reason = ('native percentage outside [0,100]' if col['unit'] == '%' and any(r[1] < 0 or r[1] > 100 for r in out)
                          else 'no finite native ages' if not ages
                          else 'native percent label for sortable-silt mean conflicts with mean-size interpretation' if 'mean_carb_free_percent' in (context or '') else None)
                if reason:
                    s['quarantine_reason'] = reason; quarantined.append(s)
                else:
                    series.append(s)
                audit.append(dict(id=sid, dataset=doi, event=label, source_column=col['column'],
                    observations=len(out), missing_cells=missing, censored_or_non_numeric=censored,
                    status='quarantined' if reason else 'extracted', reason=reason))
                record['qc_notes'] = sorted(set(record['qc_notes'] + notes))
    used = {s['record_id'] for s in series}
    fragment = dict(records=[r for r in records.values() if r['id'] in used], series=series,
                    quarantined_series=quarantined, pending=[e for e in contract['datasets'] if e['status'] == 'held'])
    FRAGMENT.parent.mkdir(parents=True, exist_ok=True)
    FRAGMENT.write_text(json.dumps(fragment, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
    report = dict(parent_version=contract['parent_version'],
        counts=dict(records=len(used), series=len(series), observations=sum(len(s['rows']) for s in series),
                    quarantined_series=len(quarantined)), audit=audit,
        held=[{k:e.get(k) for k in ('id','status','reason')} for e in contract['datasets'] if e['status'] == 'held'])
    AUDIT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report['counts']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--fetch', action='store_true')
    args = parser.parse_args()
    if args.prepare:
        prepare(args.fetch)
    else:
        curate(args.fetch)
