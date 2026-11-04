"""Reviewed NOAA 43639 native calendar-age contracts, plus explicit 10418 hold.

No reconstruction is calculated. Age_BP is calendar year BP and is divided by
1000. Sample uncertainties and zero values are preserved; the oxygen index is
not equated to BFOI formulas whose definition is absent from this file.
"""
import argparse
from collections import Counter
import copy
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
import curate_pangaea_v5 as native
sys.path.insert(0,str(ROOT/'scripts/discovery'))
from priority_vocabulary import ratio_alias
RAW=ROOT/'data/interim/priority_v6/noaa'
CONTRACT=Path(__file__).with_name('noaa_priority_v6_sources.json')
POLICY='https://www.ncei.noaa.gov/products/paleoclimatology/contributing-data'

SPECS={
 'selvaggi2025-geochem.txt':{
  'Mn/Al':('Manganese/Aluminium ratio','sin unidad','Geoquímica elemental','XRF ratio as published',None),
  'Zr/Rb':('Zirconium/Rubidium ratio','sin unidad','Sedimentología','XRF ratio as published',None),
  'Ti/Ca':('Titanium/Calcium ratio','sin unidad','Geoquímica elemental','XRF ratio as published',None)},
 'selvaggi2025-ss.txt':{
  'SS%':('Size fraction 0.063-0.010 mm, sortable silt','%','Sedimentología','Published sortable-silt percentage','sortable_silt_percent_below63'),
  'SS_mean':('Sortable silt mean grain size','µm','Sedimentología','Published sortable-silt mean size','sortable_silt_mean_size')},
 'selvaggi2025-div-idx.txt':{
  'Oxy_Index':('Benthic oxygen index, Selvaggi2026, native definition','sin unidad','Oxigenación bentónica','Published benthic oxygen index, formula not independently harmonized','oxygen_index_selvaggi2026'),
  'Epifauna%':('Foraminifera, benthic, epifaunal','%','Oxigenación bentónica','Published benthic microhabitat assemblage',None),
  'Infauna%':('Foraminifera, benthic, infaunal','%','Oxigenación bentónica','Published benthic microhabitat assemblage',None),
  'Deep_infauna%':('Foraminifera, benthic, deep infaunal','%','Oxigenación bentónica','Published benthic microhabitat assemblage',None)},
 'selvaggi2025-u_mn.txt':{
  'U/Mn':('Uranium/Manganese ratio, planktic foraminiferal coatings','µmol/mol','Oxigenación bentónica','Foraminiferal coating U/Mn as published','foraminiferal_coating')},
}


def read_table(raw):
    """Preserve physical line and numeric source row; allow a documented final tab."""
    text=raw.decode('utf-8-sig')
    lines=[(i,l.rstrip('\t')) for i,l in enumerate(text.splitlines(),1) if l.strip() and not l.startswith('#')]
    header=lines[0][1].split('\t'); rows=[]
    for row,(line,value) in enumerate(lines[1:],1):
        cells=value.split('\t')
        if len(cells)!=len(header):raise ValueError('NOAA column width differs')
        rows.append((row,line,cells))
    return text,header,rows


def acquire(url,filename,expected=None,fetch=False):
    path=RAW/filename
    if not path.exists() and not fetch:raise FileNotFoundError(path)
    return native.get(url,path,expected,limit=8_000_000)


def prepare(fetch=False):
    """Pin native metadata, tables and the DOI identity before extraction."""
    metadata_url='https://www.ncei.noaa.gov/access/paleo-search/study/search.json?NOAAStudyId=43639'
    path=RAW/'43639-metadata.json'
    if not path.exists():
        # Reuse the already retrieved full NOAA metadata snapshot, not a summary.
        original=ROOT/'data/interim/discovery_continental/studies/43639.json'
        if original.exists():path.write_bytes(original.read_bytes())
    metadata=acquire(metadata_url,path.name,fetch=fetch); study=json.loads(metadata)['study'][0]
    site=study['site'][0]
    if site['siteName']!='NDT_22_2016':raise ValueError('Reviewed NOAA site changed')
    pub=next(p for p in study['publication'] if p.get('identifier',{}).get('id')=='10.1016/j.quascirev.2026.109800')
    crossref_url='https://api.crossref.org/works/'+quote(pub['identifier']['id'],safe='')
    cr=acquire(crossref_url,'43639-crossref.json',fetch=fetch); message=json.loads(cr)['message']
    if message['DOI'].lower()!=pub['identifier']['id'].lower() or message['published']['date-parts'][0][0]!=pub['pubYear']:
        raise ValueError('NOAA article DOI/year differs from Crossref')
    entries=[]
    base=json.loads((ROOT/'data/processed/atlas-v5.json').read_text(encoding='utf8'))
    taxa={s.get('parameter_name_pangaea') for s in base['series'] if s['unit']=='%'}
    selected=copy.deepcopy(SPECS)
    for table in site['paleoData']:
        for f in table['dataFile']:
            filename=f['fileUrl'].rsplit('/',1)[-1]
            if filename=='selvaggi2025-forams.txt':
                # Expand existing named taxa, not every rare taxon in the source.
                raw=acquire(f['fileUrl'],'43639-'+filename,fetch=fetch)
                text,header,rows=read_table(raw); columns={}
                for h in header[2:]:
                    match=re.search(r'(?m)^## '+re.escape(h)+r'\t[^\n]*,N,([^\n]+)',text)
                    name=re.sub(r'\s*\(%\)\s*$','',match[1]).strip() if match else ''
                    if name in taxa:columns[h]=(name,'%','Foraminíferos','Published benthic foraminiferal percentage',None)
                selected[filename]=columns
            if filename not in selected:continue
            raw=acquire(f['fileUrl'],'43639-'+filename,fetch=fetch)
            text,header,rows=read_table(raw)
            if 'calendar year before present' not in text:raise ValueError('Native calendar BP definition missing')
            specs=[]
            for column,(name,unit,family,method,context) in selected[filename].items():
                if column not in header:raise ValueError('Reviewed NOAA source column absent')
                declaration=re.search(r'(?m)^## '+re.escape(column)+r'\t([^\n]+)',text)
                native_unit=(declaration[1].split(',')+['']*4)[3].strip() if declaration else None
                specs.append(dict(column=column,index=header.index(column),parameter=name,unit=unit,native_unit=native_unit or None,
                                  family=family,method=method,context=context,
                                  uncertainty_column='U/Mn_std' if column=='U/Mn' else None))
            entries.append(dict(table_id=str(table['NOAADataTableId']),url=f['fileUrl'],filename='43639-'+filename,
                sha256=native.sha(raw),header=header,columns=specs))
    hold=dict(study_id='10418',source_url='https://www.ncei.noaa.gov/pub/data/paleo/contributions_by_author/dean2010/dean2010.txt',
        sha256='1630a565ef14c57cf497a6a3917055fcb85f4693601e20de5141d76140e6d401',
        reason='11 native core tables have sediment depth but no point age column; no ages assigned from narrative boundaries',
        publication_doi='10.3133/ofr20101323')
    contract=dict(study_id='43639',metadata_url=metadata_url,metadata_sha256=native.sha(metadata),
        site=site,publication=pub,crossref_url=crossref_url,crossref_sha256=native.sha(cr),
        dataset_doi=re.sub(r'^https?://(?:dx\.)?doi\.org/','',study['doi']),files=entries,held=[hold])
    CONTRACT.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('NOAA priority native tables',len(entries))


def curate(fetch=False):
    c=json.loads(CONTRACT.read_text(encoding='utf8'))
    acquire(c['metadata_url'],'43639-metadata.json',c['metadata_sha256'],fetch)
    acquire(c['crossref_url'],'43639-crossref.json',c['crossref_sha256'],fetch)
    site=c['site'];lat,lon=map(float,site['geo']['geometry']['coordinates'])
    bounds=site['geo']['properties']
    if not(-10<=lon<=42 and 28<=lat<=48):raise ValueError('Outside region')
    if float(bounds['southernmostLatitude'])!=lat or float(bounds['westernmostLongitude'])!=lon:
        raise ValueError('NOAA POINT and bounds disagree')
    elev=float(bounds['minElevationMeters'])
    rid='noaa-43639-'+str(site['NOAASiteId'])
    inv={r['id'] for r in json.loads((ROOT/'data/processed/inventory-v2.json').read_text(encoding='utf8'))['records']}
    link='noaa:43639:'+str(site['NOAASiteId'])
    record=dict(id=rid,name=site['siteName'],core=site['siteName'],provider='NOAA WDS',realm='marine',archive_type='marine_sediment',
        latitude=lat,longitude=lon,water_depth_m=-elev,elevation_m=elev,source_id='43639',source_site_id=str(site['NOAASiteId']),
        dataset_doi=c['dataset_doi'],paper_doi=c['publication']['identifier']['id'],publication_year=c['publication']['pubYear'],
        source_url='https://www.ncei.noaa.gov/access/paleo-search/study/43639',
        license='NOAA WDS availability/citation policy; no dataset-specific Creative Commons licence assigned',license_url=POLICY,
        source_files=[{k:f[k] for k in ('url','sha256','table_id')} for f in c['files']],inventory_ids=[link] if link in inv else [],
        qc_notes=['Registro de aguas intermedias a432m: no es una reconstrucción abisal de oxígeno.',
                  'Edades calendario publicadas conservadas; división de años BP entre1000, sin recalibración.'])
    series=[];audit=[];quarantine=[]
    for f in c['files']:
        raw=acquire(f['url'],f['filename'],f['sha256'],fetch);text,h,rows=read_table(raw)
        if h!=f['header']:raise ValueError('Pinned NOAA header changed')
        for spec in f['columns']:
            out=[];missing=0
            for row,line,cells in rows:
                value=native.number(cells[spec['index']]);age=native.number(cells[h.index('Age_BP')])
                if value is None:missing+=1;continue
                uncertainty=native.number(cells[h.index(spec['uncertainty_column'])]) if spec['uncertainty_column'] else None
                out.append([age/1000 if age is not None else None,value,row,line,cells[h.index('Age_BP')],cells[spec['index']],None,uncertainty,cells[h.index('Depth_cm')]])
            proxy=native.slug(spec['parameter'])+'_'+native.slug(spec['unit'])
            digest=native.sha(json.dumps(out,separators=(',',':')).encode())[:10]
            sid=f'noaa6-43639:{f["table_id"]}:{native.slug(spec["column"])}~{digest}'
            notes=list(record['qc_notes'])
            if spec['column'] in ('Mn/Al','Zr/Rb','Ti/Ca'):notes.append('Razón XRF publicada: no convertir en concentración ni velocidad.')
            if spec['column']=='Oxy_Index':notes.append('Índice bentónico nativo; definición no equiparada automáticamente a BFOI de Kaiho o Schmiedl.')
            if not spec.get('native_unit'):notes.append('La cabecera no declara unidad de esta razón; etiqueta adimensional, sin conversión de valores ni interpretación de masa.')
            s=dict(id=sid,record_id=rid,proxy=proxy,variable_id=proxy,label=spec['parameter'],unit=spec['unit'],original_unit=spec.get('native_unit'),
                family=spec['family'],method=spec['method'],compatibility_group=proxy+'_NOAA43639_table'+f['table_id'],
                comparison_parameter_name=spec['parameter'],comparison_context_key=spec['context'],evidence_type='as_archived_parameter',
                source_url=f['url'],source_table_id=f['table_id'],source_column=spec['column'],source_column_index=spec['index'],source_header_original=h,
                dataset_doi=c['dataset_doi'],paper_doi=record['paper_doi'],publication_year=record['publication_year'],
                raw_sha256=f['sha256'],metadata_sha256=c['metadata_sha256'],license=record['license'],license_url=POLICY,
                citation=c['publication']['citation'],source_event=site['siteName'],qc_notes=notes,
                chronology_status='published_calendar_multi_method',chronology_label='Edad calendario BP nativa /1000',
                age_column_original='Age_BP',age_scale='calendar years before present1950',age_transformation='source calendar years BP /1000 = ka BP',
                uncertainty_type='source one standard deviation' if spec['uncertainty_column'] else 'not reported for selected column',
                value_uncertainty_source_column=spec['uncertainty_column'],depth_frame='source sediment depth in cm',rows=out,
                review_status='native_table_units_calendar_age_and_DOI_identity_checked',
                search_aliases=[spec['parameter'],ratio_alias(spec['parameter']) or '', 'corrientes oxigenación bentónica ratios inorgánicos Liguria'])
            reason='native percentage outside[0,100]' if spec['unit']=='%' and any(r[1]<0 or r[1]>100 for r in out) else None
            if reason:s['quarantine_reason']=reason;quarantine.append(s)
            else:series.append(s)
            audit.append(dict(id=sid,table=f['table_id'],column=spec['column'],observations=len(out),missing=missing,quarantine=reason))
    fragment=dict(records=[record],series=series,quarantined_series=quarantine,pending=c['held'])
    out=ROOT/'data/interim/priority_v6/noaa_curated.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(fragment,ensure_ascii=False,separators=(',',':')),encoding='utf8')
    report=dict(counts=dict(records=1,series=len(series),observations=sum(len(s['rows']) for s in series),quarantined=len(quarantine)),audit=audit,held=c['held'])
    (ROOT/'reports/noaa_priority_v6_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report['counts']))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--fetch',action='store_true');a=p.parse_args()
    prepare(a.fetch) if a.prepare else curate(a.fetch)
