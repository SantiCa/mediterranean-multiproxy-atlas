"""Cobertura de proxies por sondeo en PANGAEA para priorizar la curación (CUR-PRIORIDAD).

Entrada: la misma consulta DataCite reproducible de ``pangaea_inventory.py`` (caja
[-10,28,42,48]) y, para los datasets candidatos, el XML nativo PANGAEA (parámetros
de la matriz y eventos georreferenciados).
Resultado: ``reports/proxy_coverage_pangaea.json`` y ``docs/curation/proxy_coverage_pangaea.md``
con, por familia de proxy, datasets, eventos distintos y eventos con columna de edad.

Límites declarados: es una cola de priorización, no una ingestión. Un evento PANGAEA no
prueba un sondeo físico independiente (re-muestreos, compuestos y alias de campaña). Tener
una columna AGE no valida la cronología. La clasificación se hace por nombre de parámetro
nativo con expresiones explícitas; los falsos positivos/negativos se revisan antes de curar.
"""
import argparse, collections, json, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pangaea_inventory import fetch, in_bbox, text, NS, QUERY, FIELDS, ROOT, now  # noqa: E402

DEST = ROOT / 'data/interim/proxy_coverage'
REPORT = ROOT / 'reports/proxy_coverage_pangaea.json'
DOC = ROOT / 'docs/curation/proxy_coverage_pangaea.md'

PLANKTIC = r'Globigerin|Globorotal|Orbulina|Neogloboquadrin|Turborotalita|Hastigerin|Pulleniatina|Beella|Globoturborotalita|Trilobatus|planktic|planktonic'
BENTHIC = (r'Cibicid|Uvigerin|Bulimin|Bolivin|Brizalin|Globobulimin|Melonis|Hoeglundin|Gyroidin|Cassidulin|Chilostomell|'
           r'Elphidium|Ammonia|Planulina|Oridorsalis|Pullenia|Epistominella|Hyalinea|Nonion|Lenticulina|benthic|benthonic')
# Orden = prioridad pedida por Santiago (29-10-2026): foraminíferos, oxigenación/MO, bioturbación,
# después las familias más abundantes para mapas. Cada familia: regex sobre nombre de parámetro.
FAMILIES = {
    'foram_planct_censo': ('Foraminíferos planctónicos — censos/abundancias', lambda p: re.search(PLANKTIC, p, re.I) and not re.search(r'δ|delta|d1[38]|Mg/Ca|Sr/Ca|B/Ca|weight|size|fragment', p, re.I)),
    'foram_bent_censo': ('Foraminíferos bentónicos — censos/abundancias/diversidad', lambda p: re.search(BENTHIC, p, re.I) and not re.search(r'δ|delta|d1[38]|Mg/Ca|Sr/Ca|B/Ca', p, re.I)),
    'd18O_planct': ('δ18O foraminíferos planctónicos', lambda p: re.search(r'δ18O|delta 18O|d18O', p, re.I) and re.search(PLANKTIC, p, re.I)),
    'd18O_bent': ('δ18O foraminíferos bentónicos', lambda p: re.search(r'δ18O|delta 18O|d18O', p, re.I) and re.search(BENTHIC, p, re.I)),
    'd13C_planct': ('δ13C foraminíferos planctónicos', lambda p: re.search(r'δ13C|delta 13C|d13C', p, re.I) and re.search(PLANKTIC, p, re.I)),
    'd13C_bent': ('δ13C foraminíferos bentónicos', lambda p: re.search(r'δ13C|delta 13C|d13C', p, re.I) and re.search(BENTHIC, p, re.I)),
    'mgca_foram': ('Mg/Ca y otras razones en foraminíferos', lambda p: re.search(r'(Mg|Sr|B|Mn|U|Ba|Cd)/Ca', p) and re.search(PLANKTIC + '|' + BENTHIC, p, re.I)),
    'oxigenacion_bent': ('Indicadores bentónicos de oxigenación (BFOI, O2)', lambda p: re.search(r'oxygen index|BFOI|Oxygen, dissolved|dysox|suboxic|low.oxygen', p, re.I)),
    'redox': ('Elementos redox (Mo, U, V, Re, Mn, Cd y razones)', lambda p: re.search(r'\b(Molybdenum|Uranium|Vanadium|Rhenium|Manganese|Cadmium)\b|\b(Mo|U|V|Re|Mn|Cd)/(Al|Ti|Th|U|Fe)\b|U/Th|Fe/Mn', p) and not re.search(r'/Ca\b', p)),
    'bario': ('Bario / productividad exportada (Ba, Ba/Al, Ba exceso)', lambda p: re.search(r'\bBarium\b|\bBa/(Al|Ti)\b|Ba excess|Ba xs|Ba, biogenic', p)),
    'toc': ('Carbono orgánico (TOC/Corg)', lambda p: re.search(r'Carbon, organic|organic carbon|\bTOC\b|C org\b|Corg', p, re.I)),
    'mo_otros': ('Materia orgánica: N total, C/N, δ13Corg, Rock-Eval, biomarcadores totales', lambda p: re.search(r'Nitrogen, total|\bC/N\b|C org/N|δ13C, organic|δ13C org|Hydrogen index|Oxygen index, Rock|Rock-Eval|Kerogen|Alkenones, total|n-Alkanes, total|Chlorin|Porphyrin', p, re.I)),
    'bioturbacion': ('Bioturbación / icnología / laminación', lambda p: re.search(r'Bioturb|Ichno|Burrow|trace fossil|Zoophycos|Chondrites|Planolites|Thalassinoides|Skolithos|Mottl|Lamina', p, re.I)),
    # Litología: variable categórica (descripciones/facies), no numérica. Base de futuros mapas
    # litológicos por edad (petición 29-10-2026): requiere columna AGE o modelo de edad del sondeo.
    'litologia': ('Litología / facies / descripción sedimentaria (categórica)', lambda p: re.search(r'Lithology|Facies|Sediment type|Sedimentary structure|Color description|Colour description|Description\b|Composition', p, re.I)),
    'sst': ('Temperatura (SST/subsuperficial: UK′37, Mg/Ca, TEX86, MAT)', lambda p: re.search(r'Sea surface temperature|\bSST\b|U\[?K\]?.?37|UK.37|alkenone unsaturation|TEX86|Temperature, water', p, re.I)),
    'caco3': ('Carbonato (CaCO3)', lambda p: re.search(r'Calcium carbonate|CaCO3|Carbonate, total|Carbon, inorganic', p, re.I)),
    'detritico_xrf': ('Detrítico/elementos (Ti, Zr, K, Al, Rb, Fe y razones)', lambda p: re.search(r'\b(Titanium|Zirconium|Potassium|Aluminium|Aluminum|Rubidium|Iron)\b|\b(Ti|Zr|K|Rb|Fe)/(Al|Ca|Ti|Rb)\b', p)),
    'granulometria': ('Granulometría (arena/limo/arcilla, sortable silt)', lambda p: re.search(r'Grain size|^Sand|^Silt|^Clay|sortable silt|Size fraction', p, re.I)),
    'nanofosiles': ('Nanofósiles calcáreos', lambda p: re.search(r'Emiliania|Gephyrocapsa|Florisphaera|Helicosphaera|Coccolith|nannofossil|Calcidiscus|Syracosphaera', p, re.I)),
}


def families_of(names):
    hits = collections.defaultdict(list)
    for n in names:
        for key, (_, rule) in FAMILIES.items():
            if rule(n):
                hits[key].append(n)
    return hits


def datacite_pages(offline):
    """Todas las páginas de la consulta de inventario v2; caché inmutable por URL."""
    datasets, page, total = [], 1, None
    while True:
        url = 'https://api.datacite.org/dois?' + urlencode({'query': QUERY, 'client-id': 'pangaea.repository', 'page[size]': 1000, 'page[number]': page, 'fields[dois]': FIELDS, 'sort': 'name'})
        path = DEST / 'pages' / f'{page:04d}.json'
        if offline and not path.exists():
            raise RuntimeError(f'Falta página offline {path}')
        raw, _ = fetch(url, path)
        j = json.loads(raw)
        total = total or j['meta']['total']
        for item in j['data']:
            a = item['attributes']
            pts = [g.get('geoLocationPoint', {}) for g in a.get('geoLocations', [])]
            if not any(in_bbox(p.get('pointLatitude'), p.get('pointLongitude')) for p in pts):
                continue
            datasets.append(dict(doi=a['doi'].lower(), title='; '.join(t['title'] for t in a.get('titles', [])),
                                 subjects=[s.get('subject', '') for s in a.get('subjects', [])],
                                 schemes=[s.get('subjectScheme') for s in a.get('subjects', [])]))
        print(f'DataCite página {page}: {len(datasets)} en caja / total {total}', flush=True)
        if page * 1000 >= total or not j['data']:
            return datasets, total
        page += 1


def native(doi):
    """Parámetros y eventos del XML nativo; ``has_age`` = existe columna AGE en la matriz."""
    try:
        raw, info = fetch('https://doi.pangaea.de/' + doi, DEST / 'xml' / (doi.rsplit('.', 1)[-1] + '.xml'), 'application/vnd.pangaea.metadata+xml')
        root = ET.fromstring(raw)
    except Exception as e:  # se registra; un fallo no se convierte en ausencia del proxy
        return doi, None, str(e)
    params = []
    for col in root.findall('.//p:matrixColumn', NS):
        name = text(col, 'p:parameter/p:name') or text(col, './/p:name')
        if name:
            params.append(dict(name=name, unit=text(col, 'p:parameter/p:unit') or text(col, './/p:unit')))
    events = []
    for ev in root.findall('.//p:event', NS):
        if 'campaign' in (ev.get('typeName', '') + ' ' + ev.get('displayTypeName', '')).lower():
            continue
        try:
            lat, lon = float(text(ev, 'p:latitude')), float(text(ev, 'p:longitude'))
        except (TypeError, ValueError):
            continue
        label = text(ev, 'p:label') or text(ev, 'p:name')
        if label and in_bbox(lat, lon):
            events.append(dict(label=label, lat=lat, lon=lon, elevation=text(ev, 'p:elevation'), method=text(ev, 'p:method/p:name')))
    has_age = any(re.match(r'(AGE|Age)\b', p['name']) for p in params)
    return doi, dict(params=params, events=events, has_age=has_age, xml_sha256=info['sha256']), None


def atlas_dois():
    """DOIs ya curados (v3 activa y borrador v4) para no reabrirlos como candidatos."""
    out = set()
    for name in ('atlas-v3.json', 'atlas-v4.json'):
        p = ROOT / 'data/processed' / name
        if p.exists():
            s = json.loads(p.read_text(encoding='utf-8'))
            for r in s.get('records', []):
                for f in [r] + r.get('source_files', []):
                    if f.get('dataset_doi'):
                        out.add(f['dataset_doi'].lower())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--offline', action='store_true')
    ap.add_argument('--max-xml', type=int, default=4000, help='Tope explícito de XML nativos a pedir')
    a = ap.parse_args()
    datasets, total = datacite_pages(a.offline)
    schemes = collections.Counter(s for d in datasets for s in d['schemes'])
    # Primer filtro por subjects+título (barato); el XML nativo decide la clasificación final.
    cands = [d for d in datasets if families_of(d['subjects'] + [d['title']])]
    cands = cands[:a.max_xml]
    print(f'{len(datasets)} datasets en caja; {len(cands)} candidatos por subjects/título', flush=True)
    meta, failures = {}, []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for doi, m, err in pool.map(native, [d['doi'] for d in cands]):
            (failures.append(dict(doi=doi, error=err)) if err else meta.__setitem__(doi, m))
    done = atlas_dois()
    fam = {k: dict(label=v[0], datasets=set(), events={}, events_age=set(), events_new_age=set()) for k, v in FAMILIES.items()}
    queue = []
    for d in cands:
        m = meta.get(d['doi'])
        if not m:
            continue
        hits = families_of([p['name'] for p in m['params']])
        for ev in m['events']:
            key = f"{ev['label']}@{ev['lat']:.3f},{ev['lon']:.3f}"
            for k in hits:
                f = fam[k]
                f['datasets'].add(d['doi'])
                f['events'][key] = ev
                if m['has_age']:
                    f['events_age'].add(key)
                    if d['doi'] not in done:
                        f['events_new_age'].add(key)
        if hits:
            queue.append(dict(doi=d['doi'], title=d['title'], families=sorted(hits), has_age=m['has_age'],
                              already_in_atlas=d['doi'] in done, n_events=len(m['events']),
                              events=[e['label'] for e in m['events']][:20],
                              matched_parameters={k: v[:12] for k, v in hits.items()}, xml_sha256=m['xml_sha256']))
    summary = [dict(family=k, label=f['label'], datasets=len(f['datasets']), events=len(f['events']),
                    events_with_age=len(f['events_age']), events_with_age_not_in_atlas=len(f['events_new_age']))
               for k, f in fam.items()]
    out = dict(created_at_utc=now(), bbox=[-10, 28, 42, 48], datacite_query=QUERY, datacite_total=total,
               datasets_in_bbox=len(datasets), candidates=len(cands), xml_retrieved=len(meta), xml_failures=failures,
               subject_schemes=dict(schemes.most_common(20)), summary=summary, queue=queue,
               limitations=['Prioriza; no ingiere ni valida datos', 'Evento ≠ sondeo físico independiente',
                            'Columna AGE ≠ cronología verificada', 'Clasificación por regex de nombres de parámetro, revisar antes de curar',
                            'Solo datasets con punto DataCite dentro de la caja y que pasan el prefiltro de subjects/título'])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    rows = sorted(summary, key=lambda s: -s['events_with_age'])
    md = ['# Cobertura de proxies en PANGAEA (priorización de curación)', '',
          f"Generado {out['created_at_utc'][:10]} por `scripts/discovery/proxy_coverage.py`. Caja [-10,28,42,48]. "
          f"{len(datasets)} datasets DataCite con punto en la caja; {len(cands)} candidatos; {len(meta)} XML nativos leídos; {len(failures)} fallos.",
          '', 'Eventos = etiqueta+coordenada distintas (no sondeos físicos independientes). «Con edad» = matriz con columna AGE (sin validar cronología).', '',
          '| Familia | Datasets | Eventos | Eventos con edad | Con edad y no curados |', '|---|---:|---:|---:|---:|']
    md += [f"| {s['label']} | {s['datasets']} | {s['events']} | {s['events_with_age']} | {s['events_with_age_not_in_atlas']} |" for s in rows]
    md += ['', 'Cola completa por dataset en `reports/proxy_coverage_pangaea.json` (`queue`).', '']
    DOC.write_text('\n'.join(md), encoding='utf-8')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
