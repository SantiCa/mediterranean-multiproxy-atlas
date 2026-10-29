"""PANGAEA v5: lote por contrato a partir de la cola de cobertura (CUR-PRIORIDAD).

Fases (ver docs/curation/pangaea_v5.md):
  --propose N   Lee reports/proxy_coverage_pangaea.json, elige N datasets prioritarios
                (un solo evento, columna de edad propia, no curados), descarga TSV/XML/Crossref
                y escribe/actualiza el contrato pangaea_v5_sources.json con hashes y columnas.
                Las entradas existentes del contrato (y sus decisiones de revisión) no se tocan.
  (sin flags)   Curación offline desde el contrato: fragmento compatible con build v4/v5.

Reglas científicas (AGENTS.md): sin recalibrar 14C ni convertir proxies. Edad aceptada solo si la columna nativa es «Age [ka BP]», «Age [a BP]»
(÷1000, cambio de unidad) o «Age [a AD/CE]» ((1950−CE)/1000, cambio de referencia).
Sin columna de edad propia (autorización de Santiago, 29-10-2026): si otro dataset PANGAEA del
mismo evento (etiqueta y coordenadas idénticas) publica Depth sed + edad admitida, la edad se
interpola linealmente en profundidad entre sus puntos, sin extrapolar (fuera de rango: edad nula),
y la serie queda marcada `interpolated_from_age_model` con el DOI del modelo.
  --age-models  reevalúa entradas del contrato rechazadas por falta de edad.
Grupo de comparación = parámetro PANGAEA + método + unidad (vocabulario controlado del
repositorio); XRF de escáner/cuentas y razones de escáner quedan restringidas al dataset.
"""
import argparse, hashlib, json, math, re, sys, time
from collections import Counter
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/interim/quantitative_v5/pangaea'
CONTRACT_PATH = Path(__file__).with_name('pangaea_v5_sources.json')
OUTPUT = ROOT / 'data/interim/quantitative_v5/pangaea_curated.json'
AUDIT = ROOT / 'reports/pangaea_v5_audit.json'
PROPOSAL = ROOT / 'docs/curation/pangaea_v5_proposal.md'
COVERAGE = ROOT / 'reports/proxy_coverage_pangaea.json'
NS = {'p': 'http://www.pangaea.de/MetaData'}
UA = 'MediterraneanMultiproxyAtlas/0.5 (curation; contact via GitHub SantiCa)'
sys.path.insert(0, str(ROOT / 'scripts/discovery'))
from proxy_coverage import families_of, FAMILIES  # noqa: E402

# Prioridad de Santiago (29-10-2026). Orden = orden de selección.
PRIORITY = ['foram_planct_censo', 'foram_bent_censo', 'd18O_planct', 'd18O_bent', 'd13C_planct', 'd13C_bent', 'mgca_foram',
            'oxigenacion_bent', 'toc', 'redox', 'factores_enriquecimiento', 'bario', 'mo_ratios', 'biomarcadores_indices', 'mo_otros',
            'bioturbacion', 'xrf_razones', 'oligoelementos', 'bromo_mo', 'detritico_xrf', 'isot_radiogenicos', 'tierras_raras_eu',
            'corrientes', 'polen', 'sst', 'caco3', 'granulometria', 'nanofosiles', 'color_grises']
FAMILY_LABEL = {  # familia visible en la web (agrupación amplia; la clave fina está en compatibility_group)
    'foram': 'Foraminíferos', 'iso': 'Isótopos estables', 'geo': 'Geoquímica elemental', 'om': 'Materia orgánica y biomarcadores',
    'pol': 'Polen', 'rad': 'Isótopos radiogénicos', 'sed': 'Sedimentología', 'temp': 'Temperatura', 'nano': 'Nanofósiles', 'bio': 'Bioturbación'}
BROAD = {'foram_planct_censo': 'foram', 'foram_bent_censo': 'foram', 'oxigenacion_bent': 'foram', 'd18O_planct': 'iso', 'd18O_bent': 'iso',
         'd13C_planct': 'iso', 'd13C_bent': 'iso', 'mgca_foram': 'geo', 'toc': 'om', 'mo_ratios': 'om', 'biomarcadores_indices': 'om',
         'mo_otros': 'om', 'bromo_mo': 'geo', 'redox': 'geo', 'factores_enriquecimiento': 'geo', 'bario': 'geo', 'xrf_razones': 'geo',
         'xrf_escaner': 'geo', 'oligoelementos': 'geo', 'detritico_xrf': 'geo', 'tierras_raras_eu': 'geo', 'isot_radiogenicos': 'rad',
         'corrientes': 'sed', 'polen': 'pol', 'sst': 'temp', 'caco3': 'sed', 'granulometria': 'sed', 'nanofosiles': 'nano',
         'bioturbacion': 'bio', 'color_grises': 'sed'}
SKIP_COLS = r'^(Depth|Age|Event|Date/Time|Latitude|Longitude|Elevation|Sample|Lab|Comment|Section|Core|Label|Sample label|Ref|Reference|Method)'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def get(url, path, expected=None, accept=None, limit=40_000_000):
    """Bytes inmutables en caché; descarga acotada solo si faltan; hash exigido si existe."""
    if path.exists():
        raw = path.read_bytes()
    else:
        for attempt in range(4):
            try:
                h = {'User-Agent': UA}
                if accept:
                    h['Accept'] = accept
                with urlopen(Request(url, headers=h), timeout=90) as r:
                    raw = r.read(limit + 1)
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        if len(raw) > limit:
            raise ValueError('Recurso excede el límite: ' + url)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    if expected and sha(raw) != expected:
        raise ValueError(f'Hash distinto del contrato (nuevo snapshot requiere revisión): {path.name}')
    return raw


def number(cell):
    """Ceros y signos se conservan; vacíos, censurados (<,>) y no finitos no son observaciones."""
    c = cell.strip()
    if not c or c.lower() in ('na', 'nan') or c[0] in '<>':
        return None
    try:
        v = float(c)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def parse_tsv(raw):
    text = raw.decode('utf-8-sig')
    head, tab = text.split('*/', 1)
    lines = text.splitlines()
    header = tab.strip().splitlines()[0].split('\t')
    start = next(n for n, t in enumerate(lines, 1) if t == '\t'.join(header))
    rows = []
    for n, t in enumerate(lines[start:], start + 1):
        if t.strip():
            cells = t.split('\t')
            if len(cells) != len(header):
                raise ValueError('Anchura de fila distinta de la cabecera')
            rows.append((len(rows) + 1, n, cells))
    return head, header, rows


def xml_meta(raw):
    root = ET.fromstring(raw)
    t = lambda n, p: (n.find(p, NS).text.strip() if n is not None and n.find(p, NS) is not None and n.find(p, NS).text else None)
    cols = []
    for c in root.findall('.//p:matrixColumn', NS):
        par = c.find('p:parameter', NS)
        cols.append(dict(name=t(par, 'p:name') or t(c, './/p:name'), short=t(par, 'p:shortName'), unit=t(par, 'p:unit'),
                         method=t(c, 'p:method/p:name'), comment=t(c, 'p:comment')))
    events = []
    for ev in root.findall('.//p:event', NS):
        if 'campaign' in (ev.get('typeName', '') + ev.get('displayTypeName', '')).lower():
            continue
        try:
            events.append(dict(label=t(ev, 'p:label') or t(ev, 'p:name'), lat=float(t(ev, 'p:latitude')), lon=float(t(ev, 'p:longitude')),
                               elevation=t(ev, 'p:elevation'), campaign=t(ev, 'p:campaign/p:label'), device=t(ev, 'p:device/p:name')))
        except (TypeError, ValueError):
            pass
    paper = None
    for el in root.iter():
        if el.tag.endswith('supplementTo'):
            uri = t(el, 'p:URI') or ''
            m = re.search(r'doi\.org/(10\.\S+)', uri)
            paper = dict(doi=m.group(1) if m else None, year=t(el, 'p:year'), title=t(el, 'p:title'))
            break
    lic = next((el for el in root.iter() if el.tag.endswith('license')), None)
    license_name = t(lic, 'p:name') if lic is not None else None
    license_uri = t(lic, 'p:URI') if lic is not None else None
    return cols, events, paper, license_name, license_uri


def age_rule(header):
    """Índice y transformación de la columna de edad admitida; None si no hay ninguna válida."""
    for k, h in enumerate(header):
        if h.startswith('Age [ka BP]'):
            return k, 'identity: source point age in ka BP', lambda v: v
        if h.startswith('Age [a BP]'):
            return k, 'unit: a BP / 1000 = ka BP', lambda v: v / 1000
        if h.startswith('Age [a AD/CE]'):
            return k, 'reference: (1950 - CE) / 1000 = ka BP', lambda v: (1950 - v) / 1000
    return None


AGE_MODEL_RULE = 'linear interpolation in sediment depth between published tie points of the same event; no extrapolation'


def depth_column(header):
    return next((k for k, h in enumerate(header) if h.startswith('Depth sed')), None)


def same_event(a, b):
    return bool(a and b) and a['label'] == b['label'] and abs(a['lat'] - b['lat']) < 1e-4 and abs(a['lon'] - b['lon']) < 1e-4


def model_points(header, rows):
    """(profundidad, edad ka BP) de un dataset con edad propia; error si no sirve como modelo."""
    d, age = depth_column(header), age_rule(header)
    if d is None or not age:
        raise ValueError('sin Depth sed o sin edad admitida')
    if re.search(r'radiocarbon|14C', header[age[0]], re.I):
        raise ValueError('edad radiocarbono, no calendario')
    pts = {}
    for _, _, cells in rows:
        z, a = number(cells[d]), number(cells[age[0]])
        if z is None or a is None:
            continue
        a = age[2](a)
        if z in pts and abs(pts[z] - a) > 1e-9:
            raise ValueError(f'edades distintas a la misma profundidad {z:g}')
        pts[z] = a
    pts = sorted(pts.items())
    if len(pts) < 2:
        raise ValueError('menos de 2 puntos edad-profundidad')
    if any(b[1] < a[1] for a, b in zip(pts, pts[1:])):
        raise ValueError('edad no monótona con la profundidad (inversiones o hiatos no resolubles por interpolación)')
    return header[d], age, pts


def interpolate(pts, z):
    """Edad lineal entre los dos puntos que rodean z; None fuera del rango del modelo."""
    if z is None or z < pts[0][0] or z > pts[-1][0]:
        return None
    lo, hi = 0, len(pts) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if pts[mid][0] <= z else (lo, mid)
    (z0, a0), (z1, a1) = pts[lo], pts[hi]
    return a0 if z1 == z0 else a0 + (a1 - a0) * (z - z0) / (z1 - z0)


def find_age_model(i, header, event, siblings):
    """Primer dataset hermano válido como modelo de edad; registra los descartados y su motivo."""
    d = depth_column(header)
    if d is None:
        return None, [dict(reason='el dataset no tiene Depth sed: no se puede asignar edad por profundidad')]
    tried = []
    for q in siblings:
        j = q['doi'].rsplit('.', 1)[-1]
        if j == i:
            continue
        try:
            tsv = get(f'https://doi.pangaea.de/10.1594/PANGAEA.{j}?format=textfile', RAW / f'{j}.tsv')
            xml = get(f'https://doi.pangaea.de/10.1594/PANGAEA.{j}', RAW / f'{j}.xml', accept='application/vnd.pangaea.metadata+xml')
            head, mh, mrows = parse_tsv(tsv)
            _, events, _, lic, lic_uri = xml_meta(xml)
            if len(events) != 1 or not same_event(events[0], event):
                raise ValueError('evento distinto (etiqueta o coordenadas)')
            mdepth, age, pts = model_points(mh, mrows)
            if mdepth != header[d]:
                raise ValueError(f'profundidad en otra unidad o marco ({mdepth} vs {header[d]})')
        except Exception as e:
            tried.append(dict(dataset=j, reason=str(e)[:200]))
            continue
        return dict(dataset=j, dataset_doi=f'10.1594/PANGAEA.{j}', tsv_sha256=sha(tsv), xml_sha256=sha(xml), header=mh,
                    depth_column=depth_column(mh), age_column=age[0], age_column_original=mh[age[0]], age_transformation=age[1],
                    tie_points=len(pts), depth_range=[pts[0][0], pts[-1][0]], age_range_ka=[pts[0][1], pts[-1][1]],
                    license=lic, license_url=lic_uri, citation=(re.search(r'Citation:\t(.+)', head) or [None, None])[1],
                    rule=AGE_MODEL_RULE), tried
    return None, tried or [dict(reason='ningún dataset hermano con edad en el informe de cobertura')]


def siblings_by_event(cov):
    out = {}
    for q in cov['queue']:
        if q['has_age'] and q['n_events'] == 1:
            out.setdefault(q['events'][0], []).append(q)
    for v in out.values():  # primero los de cronología explícita / modelo de edad
        v.sort(key=lambda q: ('cronologia' not in q['families'], not re.search(r'age model|chronolog|age-depth', q['title'], re.I), q['doi']))
    return out


def slug(s):
    return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')[:60]


MIN_EVENTS = 3  # petición 29-10-2026 (19:02): priorizar proxies con muchos registros (mapas)


def map_coverage(cov):
    """Parámetro PANGAEA → nº de eventos distintos con edad (propia o de un dataset hermano)
    en el informe de cobertura, más los registros del atlas que ya lo tienen."""
    sib = siblings_by_event(cov)
    ev = {}
    for q in cov['queue']:
        if q['n_events'] != 1 or not (q['has_age'] or q['events'][0] in sib):
            continue
        for ps in q['matched_parameters'].values():
            for p in ps:
                ev.setdefault(p, set()).add(q['events'][0])
    atlas = ROOT / 'data/processed/atlas-v5.json'
    if atlas.exists():
        for x in json.loads(atlas.read_text(encoding='utf-8'))['series']:
            if x.get('parameter_name_pangaea') and x.get('source_event'):
                ev.setdefault(x['parameter_name_pangaea'], set()).add(x['source_event'])
    return {p: len(v) for p, v in ev.items()}


def coverage_gate(spec, cover):
    """Columnas de parámetros con pocos sondeos quedan diferidas (reversibles), para no
    multiplicar proxies de un solo registro."""
    n = cover.get(spec['parameter'], 0)
    spec['map_events'] = n
    if spec.get('status') == 'approved' and n < MIN_EVENTS:
        spec.update(status='deferred_low_coverage', deferred_reason=f'parámetro en {n} sondeos (< {MIN_EVENTS}); se cura cuando haya más registros')
    return spec


def column_specs(header, cols):
    """Columnas de valor propuestas, alineadas por posición con el XML (verificando shortName)."""
    aligned = len(cols) == len(header) and all(not c['short'] or h.startswith(c['short']) for h, c in zip(header, cols))
    out = []
    for k, h in enumerate(header):
        if re.match(SKIP_COLS, h) or h.startswith('±') or 'std dev' in h.lower():
            continue
        c = cols[k] if aligned else dict(name=h, short=h, unit=None, method=None, comment=None)
        name = c['name'] or h
        fams = sorted(families_of([name]) | families_of([h]))
        fams = [f for f in fams if f not in ('cronologia', 'litologia')]
        if not fams:
            continue
        unit = (re.search(r'\[([^\]]+)\]', h) or [None, None])[1] or c['unit'] or 'sin unidad'
        nxt = header[k + 1] if k + 1 < len(header) else ''
        err = k + 1 if (nxt.startswith('±') or 'std dev' in nxt.lower()) else None
        scanner = bool(re.search(r'XRF|scanner|counts|cps|area', (c['method'] or '') + ' ' + unit, re.I)) or unit in ('cps', 'counts', 'area', '#')
        out.append(dict(column=k, header=h, parameter=name, unit=unit, method=c['method'], comment=c['comment'], families=fams,
                        error_column=err, scanner_or_counts=scanner, aligned_with_xml=aligned, status='approved'))
    return out


def propose(n):
    cov = json.loads(COVERAGE.read_text(encoding='utf-8'))
    contract = json.loads(CONTRACT_PATH.read_text(encoding='utf-8')) if CONTRACT_PATH.exists() else {}
    rank = {f: i for i, f in enumerate(PRIORITY)}
    sib = siblings_by_event(cov)
    cover = map_coverage(cov)
    pool = [q for q in cov['queue'] if (q['has_age'] or q['events'][0] in sib) and not q['already_in_atlas'] and q['n_events'] == 1
            and any(f in rank for f in q['families'])]
    # Reparto por turnos entre bloques de prioridad para que cada lote cubra foraminíferos,
    # oxigenación/MO, bioturbación, geoquímica inorgánica y el resto (petición 29-10-2026).
    # Orden (29-10, 19:02): primero los datasets cuyos parámetros están en más sondeos con edad
    # (mapas espaciales); a igualdad, prioridad científica de familia.
    def score(q):
        ps = [p for f, v in q['matched_parameters'].items() if f in rank for p in v]
        return -max([cover.get(p, 0) for p in ps] or [0]), min(rank.get(f, 99) for f in q['families']), q['doi']
    pool = sorted(pool, key=score)
    added = 0
    for q in pool:
        if added >= n:
            break
        i = q['doi'].rsplit('.', 1)[-1]
        if i in contract:
            continue
        try:
            tsv = get(f'https://doi.pangaea.de/10.1594/PANGAEA.{i}?format=textfile', RAW / f'{i}.tsv')
            xml = get(f'https://doi.pangaea.de/10.1594/PANGAEA.{i}', RAW / f'{i}.xml', accept='application/vnd.pangaea.metadata+xml')
            head, header, rows = parse_tsv(tsv)
            cols, events, paper, lic, lic_uri = xml_meta(xml)
        except Exception as e:
            contract[i] = dict(status='rejected', reason=f'descarga/parseo: {e}'[:300], families=q['families'])
            continue
        age = age_rule(header)
        model, tried = (None, []) if age or not events else find_age_model(i, header, events[0], sib.get(q['events'][0], []))
        entry = dict(status='proposed', families=q['families'], tsv_sha256=sha(tsv), xml_sha256=sha(xml), event=events[0] if events else None,
                     header=header, n_rows=len(rows), age_column=age[0] if age else None, age_transformation=age[1] if age else None,
                     paper=paper, license=lic, license_url=lic_uri, citation=(re.search(r'Citation:\t(.+)', head) or [None, None])[1],
                     columns=[coverage_gate(c, cover) for c in column_specs(header, cols)])
        if model or tried:
            entry.update(age_model=model, age_model_rejected=tried)
        if paper and paper.get('doi'):
            try:
                cr = get('https://api.crossref.org/works/' + quote(paper['doi'], safe=''), RAW / f'crossref-{sha(paper["doi"].lower().encode())[:16]}.json', limit=3_000_000)
                entry['crossref_sha256'] = sha(cr)
            except Exception as e:
                entry['crossref_error'] = str(e)[:200]
        reasons = []
        if not age and not model:
            reasons.append('sin columna de edad admitida (ka BP, a BP o a AD/CE) ni modelo de edad del mismo evento')
        if not entry['event']:
            reasons.append('sin evento georreferenciado')
        if not entry['columns']:
            reasons.append('ninguna columna de familia prioritaria')
        if not lic:
            reasons.append('licencia no documentada')
        if reasons:
            entry.update(status='rejected', reason='; '.join(reasons))
        contract[i] = entry
        added += 1
    CONTRACT_PATH.write_text(json.dumps(contract, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'Propuestos {added}; contrato con {len(contract)} entradas')


def prune():
    """Aplica el umbral de cobertura a columnas ya aprobadas del contrato (reversible)."""
    cov = json.loads(COVERAGE.read_text(encoding='utf-8'))
    cover = map_coverage(cov)
    contract = json.loads(CONTRACT_PATH.read_text(encoding='utf-8'))
    n = 0
    for e in contract.values():
        for c in e.get('columns') or []:
            before = c.get('status')
            coverage_gate(c, cover)
            n += before != c['status']
    CONTRACT_PATH.write_text(json.dumps(contract, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'Columnas diferidas por baja cobertura: {n}')


def age_models():
    """Reevalúa entradas rechazadas solo por falta de edad buscando un modelo del mismo evento."""
    cov = json.loads(COVERAGE.read_text(encoding='utf-8'))
    contract = json.loads(CONTRACT_PATH.read_text(encoding='utf-8'))
    sib, fixed = siblings_by_event(cov), 0
    for i, e in contract.items():
        if e.get('status') != 'rejected' or not str(e.get('reason', '')).startswith('sin columna de edad') or not e.get('event'):
            continue
        if any(r for r in e['reason'].split('; ') if not r.startswith('sin columna de edad')):
            continue
        tsv = get(f'https://doi.pangaea.de/10.1594/PANGAEA.{i}?format=textfile', RAW / f'{i}.tsv', e['tsv_sha256'])
        _, header, _ = parse_tsv(tsv)
        model, tried = find_age_model(i, header, e['event'], sib.get(e['event']['label'], []))
        e.update(age_model=model, age_model_rejected=tried)
        if model:
            e.update(status='proposed', reason=None)
            fixed += 1
        else:
            e['reason'] = 'sin columna de edad admitida ni modelo de edad válido del mismo evento'
    CONTRACT_PATH.write_text(json.dumps(contract, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'Modelos de edad asignados: {fixed}')


def curate():
    contract = json.loads(CONTRACT_PATH.read_text(encoding='utf-8'))
    inventory = {r['id'] for r in json.loads((ROOT / 'data/processed/inventory-v2.json').read_text(encoding='utf-8'))['records']}
    records, series, quarantined, audits = {}, [], [], []
    for i, e in sorted(contract.items(), key=lambda kv: int(kv[0])):
        if e['status'] not in ('proposed', 'approved'):
            continue
        tsv = get(f'https://doi.pangaea.de/10.1594/PANGAEA.{i}?format=textfile', RAW / f'{i}.tsv', e['tsv_sha256'])
        get(f'https://doi.pangaea.de/10.1594/PANGAEA.{i}', RAW / f'{i}.xml', e['xml_sha256'], accept='application/vnd.pangaea.metadata+xml')
        head, header, rows = parse_tsv(tsv)
        if header != e['header']:
            raise ValueError(f'{i}: cabecera distinta del contrato')
        age, model, pts = age_rule(header), e.get('age_model'), None
        if not age and model:
            mtsv = get(f'https://doi.pangaea.de/10.1594/PANGAEA.{model["dataset"]}?format=textfile', RAW / f'{model["dataset"]}.tsv', model['tsv_sha256'])
            _, mh, mrows = parse_tsv(mtsv)
            if mh != model['header']:
                raise ValueError(f'{i}: cabecera del modelo de edad distinta del contrato')
            _, _, pts = model_points(mh, mrows)
        elif not age:
            continue
        ev, doi = e['event'], f'10.1594/PANGAEA.{i}'
        paper = dict(e.get('paper') or {})
        year = None
        if not paper.get('doi'):
            # Respaldo: cabecera nativa «In supplement to:» del TSV (relación declarada por PANGAEA).
            m = re.search(r'(?:In supplement to|Supplement to):\t([^\n]+)', head)
            d = re.search(r'(?:doi\.org/|doi:\s*)(10\.[^\s;,]+)', m.group(1), re.I) if m else None
            if d:
                paper = dict(doi=d.group(1).rstrip('.'), source='TSV header In supplement to', native_line=m.group(1)[:400])
        if paper.get('doi'):
            crp = RAW / f'crossref-{sha(paper["doi"].lower().encode())[:16]}.json'
            craw = get('https://api.crossref.org/works/' + quote(paper['doi'], safe=''), crp, e.get('crossref_sha256'), limit=3_000_000)
            paper['crossref_sha256'] = sha(craw)
            cr = json.loads(craw)['message']
            parts = (cr.get('published-print') or cr.get('published-online') or cr.get('issued') or {}).get('date-parts', [[None]])[0]
            year = parts[0]
            paper_title = (cr.get('title') or [None])[0]
        else:
            paper_title = paper.get('title')
        elev = number(ev['elevation'] or '') if ev.get('elevation') else None
        rid = 'pangaea5-' + slug(ev['label']).lower()
        r = records.get(rid)
        if not r:
            r = records[rid] = dict(id=rid, name=ev['label'], core=ev['label'], source_event=ev['label'], physical_core_key='PANGAEA:event:' + ev['label'],
                                    provider='PANGAEA', realm='marine' if elev is not None and elev < 0 else 'unknown',
                                    archive_type='marine_sediment' if elev is not None and elev < 0 else 'sediment', latitude=ev['lat'], longitude=ev['lon'],
                                    elevation_m=elev, water_depth_m=-elev if elev is not None and elev < 0 else None, campaign=ev.get('campaign'),
                                    device=ev.get('device'), dataset_doi=doi, publication_year=year, paper_doi=paper.get('doi'), paper_title=paper_title,
                                    source_url='https://doi.pangaea.de/' + doi, license=e['license'], license_url=e['license_url'], raw_sha256=e['tsv_sha256'],
                                    source_files=[], inventory_ids=[], chronology_status='published_BP', time_scale=e['age_transformation'],
                                    age_scale_status='published age column as archived; independent age-model audit pending',
                                    review_status='contract_v5_columns_units_age_column_checked; independent age-model audit pending',
                                    qc_notes=['Un evento = un registro; varias tablas no son sondeos independientes',
                                              'Edades y valores archivados tal cual; sin ajuste de edad, recalibración ni conversión de proxy'])
        r['source_files'].append(dict(dataset_doi=doi, url='https://doi.pangaea.de/' + doi, raw_sha256=e['tsv_sha256'], xml_sha256=e['xml_sha256'],
                                      license=e['license'], license_url=e['license_url'], paper_doi=paper.get('doi'), publication_year=year,
                                      paper_title=paper_title, citation=e['citation']))
        if 'datacite:' + doi.lower() in inventory:
            r['inventory_ids'] = sorted(set(r['inventory_ids'] + ['datacite:' + doi.lower()]))
        depth_col = depth_column(header)
        if pts:
            # Edad asignada, no archivada: se distingue en la cronología y en cada serie.
            chron = dict(chronology_status='interpolated_from_age_model',
                         chronology_label='Edad interpolada en profundidad desde el modelo publicado del mismo evento (sin extrapolar)',
                         age_column_original=None, age_column_index=None, age_unit_original=model['age_column_original'] + ' (dataset ' + model['dataset_doi'] + ')',
                         age_scale=model['age_transformation'], age_model=model['rule'] + '; model ' + model['dataset_doi'],
                         age_transformation=model['age_transformation'] + '; then ' + model['rule'],
                         age_model_dataset_doi=model['dataset_doi'], age_model_raw_sha256=model['tsv_sha256'], age_model_citation=model['citation'],
                         age_model_tie_points=model['tie_points'], age_model_depth_range_m=model['depth_range'])
            r['chronology_status'] = 'mixed' if r['chronology_status'] not in ('interpolated_from_age_model', 'mixed') and r.get('_has_archived') else 'interpolated_from_age_model'
            r['qc_notes'] = sorted(set(r['qc_notes'] + ['Algunas series con edad interpolada desde un modelo de edad publicado del mismo evento']))
        else:
            chron = dict(chronology_status='published_BP', chronology_label='Edad publicada en el dataset · escala no armonizada',
                         age_column_original=header[age[0]], age_column_index=age[0], age_unit_original=header[age[0]],
                         age_scale=e['age_transformation'], age_model=e['age_transformation'], age_transformation=e['age_transformation'])
            r['_has_archived'] = True
        for c in e['columns']:
            if c['status'] != 'approved':
                continue
            k, out, missing, rejected, outside = c['column'], [], 0, 0, 0
            for src_row, line, cells in rows:
                v = number(cells[k])
                if v is None:
                    missing += not cells[k].strip()
                    rejected += bool(cells[k].strip())
                    continue
                if pts:
                    a_ka, a_txt = interpolate(pts, number(cells[depth_col])), None
                    if a_ka is None:
                        # Fuera del rango del modelo (o sin profundidad): no se extrapola y la
                        # muestra no entra en el atlas; queda contada y en el original (hash).
                        outside += 1
                        continue
                else:
                    a = number(cells[age[0]])
                    a_ka, a_txt = (age[2](a) if a is not None else None), cells[age[0]]
                out.append([a_ka, v, src_row, line, a_txt, cells[k], None,
                            number(cells[c['error_column']]) if c['error_column'] is not None else None,
                            cells[depth_col] if depth_col is not None else None])
            if len(out) < 3:
                continue
            out.sort(key=lambda x: (x[0] is None, x[0] or 0, x[2]))
            fam0 = min(c['families'], key=lambda f: PRIORITY.index(f) if f in PRIORITY else 99)
            proxy = slug(c['parameter']) + '_' + slug(c['unit'])
            group = proxy + '_PANGAEA_' + slug(c['method'] or 'metodo_no_declarado')
            if c['scanner_or_counts'] or fam0 in ('xrf_razones', 'xrf_escaner'):
                group += '_dataset_' + i  # cuentas/razones de escáner: instrumento y laboratorio específicos
            label = c['parameter'] + ' · ' + ev['label']
            sid = f'pangaea5-{i}:{proxy}'
            if any(x['id'] == sid for x in series + quarantined):
                sid += f'_col{k}'  # cabeceras nativas repetidas: identidad por posición
            s = dict(id=sid, record_id=rid, proxy=proxy, variable_id=proxy, label=label, unit=c['unit'],
                     family=FAMILY_LABEL[BROAD.get(fam0, 'geo')], method=c['method'] or 'no declarado en metadatos PANGAEA', compatibility_group=group,
                     evidence_type='as_archived_parameter', taxon=None, source_column=c['header'], source_column_index=k,
                     source_header_original=header, source_url=f'https://doi.pangaea.de/{doi}?format=textfile', dataset_doi=doi,
                     paper_doi=paper.get('doi'), publication_year=year, citation=e['citation'], license=e['license'], license_url=e['license_url'],
                     raw_sha256=e['tsv_sha256'], xml_sha256=e['xml_sha256'], source_event=ev['label'], **chron, original_unit=c['unit'], parameter_name_pangaea=c['parameter'],
                     parameter_comment=c['comment'], proxy_families=c['families'],
                     uncertainty_type='native column adjacent (±/std dev), type as labelled' if c['error_column'] is not None else 'not_supplied_for_selected_column',
                     value_uncertainty_source_column=header[c['error_column']] if c['error_column'] is not None else None,
                     depth_frame='native sediment depth m; no cross-table remapping', rows=out,
                     rows_outside_age_model=outside if pts else None,
                     review_status='contract_v5_auto_rules; manual review ' + ('done' if c['status'] == 'approved' and e['status'] == 'approved' else 'pending'))
            vals = [x[1] for x in out]
            ages = [x[0] for x in out if x[0] is not None]
            reason = None
            if c['unit'] == '%' and any(v < 0 or v > 100 for v in vals):
                reason = 'porcentaje fuera de [0,100]; serie completa preservada sin recortar'
            elif not ages:
                reason = 'ninguna fila con edad'
            elif not pts and re.search(r'radiocarbon|14C', header[age[0]], re.I):
                # La columna «Age [ka BP]» describe una edad radiocarbono: no es calendario y no se recalibra.
                reason = 'columna de edad declarada como radiocarbono; sin recalibración ni equiparación a calendario'
            elif max(ages) > 2600 and not re.match(r'^\d{1,3}-\w', ev['label']):
                # Fuera de sitios DSDP/ODP/IODP, >2,6 Ma en testigos de gravedad/pistón/lagos es sospecha de
                # unidades mezcladas (años etiquetados como ka). Se preserva y se revisa a mano.
                reason = f'edad máxima {max(ages):g} ka BP implausible para el tipo de sondeo; posible unidad mezclada'
            if reason:
                s.update(review_status='quarantined', quarantine_reason=reason)
                quarantined.append(s)
            else:
                series.append(s)
            audits.append(dict(id=s['id'], status=s['review_status'], values=len(out), missing=missing, rejected_cells=rejected,
                               value_min=min(vals), value_max=max(vals), age_min=min(ages) if ages else None, age_max=max(ages) if ages else None,
                               missing_age=sum(x[0] is None for x in out), negative_ages=sum(a < 0 for a in ages), group=group,
                               age_model=model['dataset_doi'] if pts else None))
    for r in records.values():
        r.pop('_has_archived', None)
    result = dict(fragment_version='pangaea-v5-2026-10-29-r2', records=list(records.values()), series=series, quarantined_series=quarantined, audit=audits,
                  pending=[dict(dataset=i, reason=e.get('reason')) for i, e in contract.items() if e['status'] == 'rejected'],
                  transformations=['Edades: ka BP identidad; a BP/1000; (1950−CE)/1000. Valores sin transformar',
                                   'Sin columna de edad: interpolación lineal en profundidad desde el modelo publicado del mismo evento, sin extrapolar (series interpolated_from_age_model)',
                                   'Sin promedios, suavizado ni nuevas calibraciones'])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    counts = dict(records=len(records), series=len(series), values=sum(len(s['rows']) for s in series), quarantined_series=len(quarantined),
                  quarantined_values=sum(len(s['rows']) for s in quarantined))
    AUDIT.write_text(json.dumps(dict(counts=counts, audit=audits, pending=result['pending']), ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    write_proposal(contract, audits, counts)
    print(json.dumps(counts))


def write_proposal(contract, audits, counts):
    """Resumen compacto por dataset para la revisión humana (una línea por dataset)."""
    by = Counter(a['id'].split(':')[0].split('-')[1] for a in audits)
    q = Counter(a['id'].split(':')[0].split('-')[1] for a in audits if a['status'] == 'quarantined')
    md = ['# PANGAEA v5 — propuesta de lote', '', f"Activos: {counts['records']} registros, {counts['series']} series, {counts['values']} valores; "
          f"cuarentena {counts['quarantined_series']} series. Revisar y marcar `status` en `scripts/importers/pangaea_v5_sources.json`.", '',
          '| Dataset | Evento | Lat, Lon | Estado | Familias | Series (cuar.) | Edad | Referencia |', '|---|---|---|---|---|---:|---|---|']
    for i, e in sorted(contract.items(), key=lambda kv: int(kv[0])):
        ev = e.get('event') or {}
        ages = [a for a in audits if a['id'].startswith(f'pangaea5-{i}:') and a['age_min'] is not None]
        span = f"{min(a['age_min'] for a in ages):.2f}–{max(a['age_max'] for a in ages):.2f} ka" if ages else '—'
        ref = (e.get('paper') or {}).get('doi') or '—'
        fam = ', '.join(sorted({f for c in e.get('columns', []) for f in c['families']})) or ', '.join(e.get('families', []))
        md.append(f"| [{i}](https://doi.pangaea.de/10.1594/PANGAEA.{i}) | {ev.get('label', '—')} | {ev.get('lat', 0):.3f}, {ev.get('lon', 0):.3f} | "
                  f"{e['status']}{': ' + e['reason'] if e.get('reason') else ''} | {fam} | {by.get(i, 0)} ({q.get(i, 0)}) | {span} | {ref} |")
    PROPOSAL.write_text('\n'.join(md) + '\n', encoding='utf-8')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--propose', type=int, default=0, help='Añadir N datasets nuevos al contrato (requiere red)')
    ap.add_argument('--age-models', action='store_true', help='Reevaluar rechazados sin edad con el modelo del mismo evento (requiere red)')
    ap.add_argument('--prune', action='store_true', help='Diferir columnas de parámetros con < MIN_EVENTS sondeos')
    a = ap.parse_args()
    if a.prune:
        prune()
    if a.age_models:
        age_models()
    if a.propose:
        propose(a.propose)
    curate()
