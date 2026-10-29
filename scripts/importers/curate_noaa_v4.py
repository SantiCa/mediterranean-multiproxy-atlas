"""Curate the explicit NOAA v4 batch using pinned official source bytes.

Default execution is offline. --fetch retrieves absent contract resources only;
changed remote bytes require review. No age-depth interpolation, recalibration,
smoothing, temperature reconstruction or chemical conversion is performed.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'data/interim/quantitative_v4/noaa'
CONTRACT=Path(__file__).with_name('noaa_v4_sources.json')
OUTPUT=ROOT/'data/interim/quantitative_v4/noaa_curated.json'
AUDIT=ROOT/'reports/noaa_v4_audit.json'
POLICY='https://www.ncei.noaa.gov/products/paleoclimatology/contributing-data'

def sha(raw):
    """Fingerprint source bytes or deterministic numeric vectors."""
    return hashlib.sha256(raw).hexdigest()

REFRESHED=[]  # metadatos JSON aceptados con --refresh-metadata: [{filename, contract_sha256, new_sha256}]
REFRESH_METADATA=__import__('os').environ.get('MEDATLAS_REFRESH_METADATA')=='1'  # también para tests en CI

def native(resource,fetch=False):
    """Read immutable cached bytes, optionally fetching only an absent resource.

    Las tablas de datos (.txt) exigen siempre el hash del contrato. Solo con --refresh-metadata,
    las respuestas JSON de API (búsqueda NOAA, Crossref, BioC), que cambian sin cambiar las
    mediciones, pueden aceptarse con hash nuevo; quedan listadas en REFRESHED y el flujo CI exige
    después que la release reconstruida sea idéntica a la comprometida.
    """
    path=CACHE/resource['filename']
    tolerant=REFRESH_METADATA and resource['filename'].endswith('.json')
    if not path.exists() and fetch:
        with urlopen(Request(resource['url'],headers={'User-Agent':'MediterraneanMultiproxyAtlas/0.4'}),timeout=45) as response:
            raw=response.read(8_000_001)
        if len(raw)>8_000_000:raise ValueError('Bounded resource size exceeded')
        if sha(raw)!=resource['sha256'] and not tolerant:raise ValueError('Upstream bytes changed: '+resource['filename'])
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    raw=path.read_bytes()
    if sha(raw)!=resource['sha256']:
        if not tolerant:raise ValueError('Native hash mismatch: '+resource['filename'])
        if not any(x['filename']==resource['filename'] for x in REFRESHED):
            REFRESHED.append(dict(filename=resource['filename'],url=resource['url'],contract_sha256=resource['sha256'],new_sha256=sha(raw)))
    return raw

def number(cell):
    """Keep zeros and signed values; missing/censored cells remain unobserved."""
    cleaned=cell.strip()
    if cleaned.lower() in ('','na','nan') or cleaned.startswith(('<','>')):return None
    value=float(cleaned)
    if not math.isfinite(value):return None
    return value

def age_ka(cell,mode):
    """Convert only declared sample-reference scales; never infer age from depth."""
    value=number(cell)
    if value is None:return None
    if mode=='BP_years':return value/1000
    if mode=='CE':return (1950-value)/1000
    raise ValueError('Unsupported age scale: '+mode)

def read_table(raw,table):
    """Retain native data-row ordinal and physical line with explicit encodings."""
    # Three files claim UTF8 while containing legacy Windows1252 author bytes.
    # Numeric cells are ASCII and preserved verbatim; the contract fixes decoding.
    text=raw.removeprefix(b'\xef\xbb\xbf').decode(table['encoding'])
    lines=text.splitlines();definitions={}
    for line in lines:
        if line.startswith('## ') and '\t' in line:
            label,description=line[3:].split('\t',1);definitions[label.strip()]=description
    if table.get('legacy_header_line'):
        line_no=table['legacy_header_line'];header=lines[line_no-1].split('\t');data=[(n,l) for n,l in enumerate(lines[line_no:],line_no+1) if l.strip()]
    else:
        data=[(n,line) for n,line in enumerate(lines,1) if line.strip() and not line.startswith('#')]
        line_no,header_line=data.pop(0);header=header_line.split('\t')
    while header and not header[-1].strip():header.pop()
    header=[h.strip() for h in header]
    if len(set(header))!=len(header):raise ValueError('Duplicate native columns')
    rows=[]
    for row,(physical,line) in enumerate(data,1):
        cells=line.split('\t')
        if len(cells)>len(header) and any(x.strip() for x in cells[len(header):]):raise ValueError('Extra nonempty cell')
        if len(cells)<len(header):
            omitted=header[len(cells):]
            if any(c not in table.get('optional_trailing_columns',[]) for c in omitted):raise ValueError('Short numeric row')
            cells+=['']*len(omitted)
        rows.append((row,physical,dict(zip(header,cells[:len(header)]))))
    return header,rows,definitions

def fingerprint(rows):
    """Full age/value fingerprint, not a fuzzy physical-core merge."""
    vector=sorted([[r[0],r[1]] for r in rows],key=lambda x:(x[0] is None,x[0] or 0,x[1]))
    return sha(json.dumps(vector,separators=(',',':')).encode())

def curate(fetch=False):
    """Return source-linked records/series and transparent quarantines/audits."""
    contract=json.loads(CONTRACT.read_text(encoding='utf8'))
    resources={r['filename']:r for r in contract['resources']}
    for r in resources.values():native(r,fetch)
    baseline=json.loads((ROOT/'data/processed/atlas-v3.json').read_text(encoding='utf8'))
    baseline_ids={r['id'] for r in baseline['records']}
    baseline_dois={str(r.get('dataset_doi') or '').lower() for r in baseline['records']}
    baseline_vectors={(s['unit'],fingerprint(s['rows'])):s['id'] for s in baseline['series']}
    inventory=json.loads((ROOT/'data/processed/inventory-v2.json').read_text(encoding='utf8'))
    inventory_ids={r['id'] for r in inventory['records']}
    records=[];record_map={};series=[];quarantine=[];audit=[];duplicates=[]
    sites={s['study_id']:s for s in contract['sites']}
    for sid,site_contract in sites.items():
        study=json.loads(native(resources[str(sid)+'.json']))['study'][0]
        metadata_site=next(s for s in study['site'] if int(s['NOAASiteId'])==site_contract['site_id'])
        point=list(map(float,metadata_site['geo']['geometry']['coordinates']))
        publication=study['publication'][0]
        crossref=json.loads(native(resources['crossref-'+str(sid)+'.json']))['message']
        doi=publication['identifier']['id']
        if crossref['DOI'].lower()!=doi.lower():raise ValueError('Article DOI mismatch')
        year=crossref['published']['date-parts'][0][0]
        dataset_doi=study['doi'].replace('https://doi.org/','')
        record_id=f"noaa-{sid}-{site_contract['site_id']}"
        if record_id in baseline_ids or dataset_doi.lower() in baseline_dois:raise ValueError('Baseline source already ingested')
        inventory_id=f"noaa:{sid}:{site_contract['site_id']}"
        if inventory_id not in inventory_ids:raise ValueError('Unresolved inventory identity')
        source_files=[resources[t['filename']] for t in contract['tables'] if t['study_id']==sid]
        record=dict(id=record_id,name=site_contract['name'],core=site_contract['core'],provider='NOAA WDS',
                    realm=site_contract['realm'],archive_type=study['dataType'].lower(),
                    latitude=site_contract.get('latitude',point[0]),longitude=site_contract.get('longitude',point[1]),
                    coordinate_basis=site_contract.get('coordinate_basis','NOAA native study POINT; not a centroid'),
                    source_coordinates_noaa_json=point,physical_core_key=site_contract['physical_core_key'],
                    source_id=str(sid),source_site_id=str(site_contract['site_id']),inventory_ids=[inventory_id],
                    source_url=study['onlineResourceLink'],dataset_doi=dataset_doi,
                    dataset_title=study['studyName'],paper_doi=doi,paper_title=crossref['title'][0],
                    publication_year=year,publication_year_native=publication['pubYear'],
                    publication_year_basis='Crossref published date-parts checked against native NOAA bibliography',
                    authors=study.get('investigators'),raw_sha256=source_files[0]['sha256'] if len(source_files)==1 else None,
                    source_files=source_files,metadata_sha256=resources[str(sid)+'.json']['sha256'],
                    chronology_status=site_contract['chronology_status'],chronology_label=site_contract['chronology_label'],
                    age_model=site_contract['age_model'],time_scale='Published BP or CE sample ages; transforms specified per series',
                    qc_notes=site_contract['notes'],review_status='native_units_reference_scales_and_source_identity_checked; not independently re-dated',
                    license=study.get('dataLicenseDescription') or 'NOAA WDS open archive; no record-specific Creative Commons license declared',
                    license_url=study.get('dataLicenseUrl') or POLICY,data_license_original=study.get('dataLicenseDescription'),
                    rights_basis='WDS contribution policy provides freely available archived data without restrictions; original article license not transferred to data')
        if sid==33716:
            record['source_coordinates_noaa_text']=[43.33,-3.66]
            record['coordinate_primary_source']='https://pmc.ncbi.nlm.nih.gov/articles/PMC11559594/'
            record['coordinate_primary_sha256']=resources['kaite2021-primary-bioc.json']['sha256']
            record['coordinate_precision']='Rounded published cave location, not a surveyed stalagmite position'
        if not (28<=record['latitude']<=48 and -10<=record['longitude']<=42):raise ValueError('Outside declared scope')
        records.append(record);record_map[sid]=record
    for table in contract['tables']:
        resource=resources[table['filename']];header,rows,defs=read_table(native(resource),table)
        record=record_map[table['study_id']]
        if table['age_column'] not in header:raise ValueError('Age column missing')
        if table.get('consistency_ce_column'):
            for _,_,r in rows:
                bp=number(r[table['age_column']]);ce=number(r[table['consistency_ce_column']])
                if bp is not None and ce is not None and abs(bp-(1950-ce))>1e-6:raise ValueError('CE/BP columns disagree')
        for spec in table['specs']:
            if spec['column'] not in header:raise ValueError('Proxy column missing')
            observations=[];missing=0;censored=0;negatives=0;zeros=0
            for row,line,r in rows:
                original_value=r[spec['column']];value=number(original_value)
                if value is None:
                    missing+=1;censored+=int(original_value.strip().startswith(('<','>')));continue
                age_original=r[table['age_column']];age=age_ka(age_original,table['age_transform'])
                uncertainty=number(r[spec['uncertainty_column']]) if spec.get('uncertainty_column') else None
                observations.append([age,value,row,line,age_original,original_value,None,uncertainty,
                                     r.get(table.get('depth_column'))])
                negatives+=int(value<0);zeros+=int(value==0)
            observations.sort(key=lambda r:(r[0] is None,r[0] or 0,r[2]))
            ages=[r[0] for r in observations if r[0] is not None]
            slug=re.sub(r'[^a-z0-9]+','_',spec['column'].lower()).strip('_')
            table_id=Path(table['filename']).stem
            metadata={k:spec[k] for k in ('proxy','label','unit','family','variable_id','method_id','evidence_type')}
            item=dict(**metadata,id=record['id']+':'+table_id+':'+slug,record_id=record['id'],
                      compatibility_group=spec['method_id']+':'+spec['proxy'],
                      method=spec['method_id'].replace('_',' '),source_column=spec['column'],source_table_id=table_id,
                      source_url=resource['url'],data_url=resource['url'],raw_sha256=resource['sha256'],source_sha256=resource['sha256'],
                      source_variable_definition=defs.get(spec['column'],spec['column']),
                      source_age_definition=defs.get(table.get('age_definition_alias',table['age_column']),table['age_column']),
                      source_header_original=header,source_encoding=table['encoding'],
                      age_column_original=table['age_column'],age_transform=table['age_transform'],
                      age_transformation='age_ka_bp=(1950-age_CE)/1000' if table['age_transform']=='CE' else 'age_ka_bp=published_BP_years/1000',
                      age_scale='CE converted to BP (1950)' if table['age_transform']=='CE' else ('lamination-year BP as archived' if table['study_id']==5463 else 'calendar BP (1950) as archived'),
                      age_unit_original=table['age_column'],
                      chronology_status=record['chronology_status'],chronology_label=record['chronology_label'],age_model=record['age_model'],
                      age_min_ka_bp=min(ages) if ages else None,age_max_ka_bp=max(ages) if ages else None,
                      missing_value_cells=missing,censored_value_cells=censored,negative_value_cells=negatives,zero_value_cells=zeros,
                      values_missing_age=sum(r[0] is None for r in observations),
                      original_unit=(defs[spec['column']].split(',')[3].strip() if spec['column'] in defs else 'wt %'),depth_frame=table.get('depth_column'),
                      uncertainty_type='Published error estimate; confidence level unspecified' if spec.get('uncertainty_column') else 'Per-sample uncertainty not supplied; age-control errors not assigned to sample rows',
                      transformations=['Source proxy values unchanged','Explicit published sample age reference/scale conversion','Sort for display; native row and physical line retained'],
                      review_status='native_cells_unit_reference_scale_and_identity_checked',rows=observations,
                      qc_notes=list(record['qc_notes']))
            if not observations:raise ValueError('Empty selected series')
            if spec.get('quarantine_if_negative') and negatives:
                item['review_status']='quarantined_negative_reported_concentrations'
                item['quarantine_reason']='Entire concentration or ratio series held: negative native values require interpretation of analytical background/correction'
                quarantine.append(item)
            elif spec.get('force_quarantine'):
                item['review_status']='quarantined_ratio_with_unresolved_denominator'
                item['quarantine_reason']='Underlying Th concentration contains negative values; ratio interpretation unresolved'
                quarantine.append(item)
            elif (item['unit'],fingerprint(observations)) in baseline_vectors:
                item['review_status']='quarantined_exact_numeric_duplicate'
                item['quarantine_reason']='Complete numeric vector duplicates an existing baseline series'
                quarantine.append(item);duplicates.append(dict(series=item['id'],baseline=baseline_vectors[(item['unit'],fingerprint(observations))]))
            else:series.append(item)
            audit.append({k:item[k] for k in ('id','record_id','proxy','unit','source_column','raw_sha256','age_min_ka_bp','age_max_ka_bp','missing_value_cells','censored_value_cells','negative_value_cells','zero_value_cells','values_missing_age','review_status')})
            audit[-1].update(values=len(observations),repeated_ages=len(ages)-len(set(ages)),repeated_age_value_pairs=len(observations)-len({(r[0],r[1]) for r in observations}))
    partial=[]
    for s in series:
        pairs={(r[0],r[1]) for r in s['rows'] if r[0] is not None}
        for old in baseline['series']:
            if old['proxy']!=s['proxy'] or old['unit']!=s['unit']:continue
            oldpairs={(r[0],r[1]) for r in old['rows'] if r[0] is not None}
            n=len(pairs&oldpairs)
            if n>=10 and n>=.8*min(len(pairs),len(oldpairs)):partial.append(dict(series=s['id'],baseline=old['id'],overlap_pairs=n,status='review_candidate_not_merged'))
    if partial:raise ValueError('Large partial baseline overlap requires manual resolution')
    output=dict(fragment_version='noaa-v4-2026-10-29',records=records,series=series,quarantined_series=quarantine,
                audit=audit,rejected_candidates=contract['rejected_candidates'],duplicate_review=dict(exact_vector_duplicates=duplicates,large_partial_matches=partial,coordinate_similarity_not_used_for_merging=True),
                limitations=['Bounded explicit batch, not exhaustive NOAA ingestion','Published chronologies retained; no independent refit or uncertainty propagation',
                             'Data are finite native cells, not necessarily independent samples','No record-specific CC license supplied; NOAA WDS policy basis retained'])
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fetch',action='store_true');p.add_argument('--refresh-metadata',action='store_true',help='Aceptar JSON de API con hash nuevo (registrado en REFRESHED)');a=p.parse_args()
    if getattr(a,'refresh_metadata',False):
        REFRESH_METADATA=True
    result=curate(a.fetch);OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
    report={k:v for k,v in result.items() if k not in ('records','series','quarantined_series')}
    report.update(counts=dict(records=len(result['records']),series=len(result['series']),values=sum(len(s['rows']) for s in result['series']),
                              quarantined_series=len(result['quarantined_series']),quarantined_values=sum(len(s['rows']) for s in result['quarantined_series'])),
                  quarantine=[{k:s[k] for k in ('id','quarantine_reason','negative_value_cells')}|{'values':len(s['rows'])} for s in result['quarantined_series']])
    AUDIT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if REFRESHED:(ROOT/'reports/noaa_v4_metadata_refresh.json').write_text(json.dumps(REFRESHED,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report['counts']),'refreshed_metadata',len(REFRESHED))
