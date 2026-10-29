"""Reviewed PANGAEA v4 batch. Explicit native column contracts, offline by default.

One physical event becomes one record even when several source tables contribute.
Measurements, published transformations and reconstructions remain distinct. No
depth-age interpolation, new calibration, or inferred symmetric error is applied.
"""
import argparse
from collections import Counter, defaultdict
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.request import Request, urlopen
from urllib.parse import quote
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'data/interim/quantitative_v4/pangaea'
CONTRACT_PATH=Path(__file__).with_name('pangaea_v4_sources.json')
CONTRACT=json.loads(CONTRACT_PATH.read_text(encoding='utf8'))
OUTPUT=ROOT/'data/interim/quantitative_v4/pangaea_curated.json'
AUDIT=ROOT/'reports/pangaea_v4_audit.json'
IDS=sorted(int(k) for k in CONTRACT if k.isdigit())
BICH={962012,962033,962034}
VERNEY={878051,878053}
LAKES=BICH|VERNEY|{940127,995820,954457}
PRIMARY={944660:944656,667403:667328,962033:962012,962034:962012,995820:954457,878053:878051}

def sha(raw):
    """Fingerprint exact native bytes."""
    return hashlib.sha256(raw).hexdigest()

def number(cell):
    """Parse finite uncensored source numbers only; missing is never zero."""
    try:
        value=float(cell)
        return value if math.isfinite(value) else None
    except (TypeError,ValueError):
        return None

def acquire_resource(url,path,expected=None,limit=8_000_000):
    """Cache absent official resources; reject changed bytes before persisting."""
    if path.exists():
        raw=path.read_bytes()
    else:
        with urlopen(Request(url,headers={'User-Agent':'MediterraneanMultiproxyAtlas/0.4'}),timeout=45) as response:
            raw=response.read(limit+1)
        if len(raw)>limit:raise ValueError('Bounded resource exceeded')
        if expected and sha(raw)!=expected:raise ValueError('Upstream bytes changed; new review required')
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    if expected and sha(raw)!=expected:raise ValueError('Native hash contract mismatch: '+path.name)
    return raw

def acquire():
    """Download only explicit absent TSV/XML/Crossref resources."""
    for i in IDS:
        for ext,fmt in [('tsv','textfile'),('xml','metainfo_xml')]:
            acquire_resource(f'https://doi.pangaea.de/10.1594/PANGAEA.{i}?format={fmt}',RAW/f'{i}.{ext}',CONTRACT[str(i)][ext+'_sha256'])
    for i,expected in CONTRACT['_supporting_xml'].items():
        acquire_resource(f'https://doi.pangaea.de/10.1594/PANGAEA.{i}?format=metainfo_xml',RAW/f'{i}.xml',expected)
    for source in (CONTRACT[str(i)] for i in IDS):
        doi=source['paper_doi']
        acquire_resource('https://api.crossref.org/works/'+quote(doi,safe=''),RAW/('crossref-'+sha(doi.lower().encode())[:16]+'.json'),limit=2_000_000)

def read_native(dataset_id):
    """Return header, unique positional columns and physical-row locators."""
    raw=(RAW/f'{dataset_id}.tsv').read_bytes()
    if sha(raw)!=CONTRACT[str(dataset_id)]['tsv_sha256']:raise ValueError('TSV snapshot changed')
    xml=(RAW/f'{dataset_id}.xml').read_bytes()
    if sha(xml)!=CONTRACT[str(dataset_id)]['xml_sha256']:raise ValueError('XML snapshot changed')
    ET.fromstring(xml)
    text=raw.decode('utf-8-sig');head,tab=text.split('*/',1)
    header=tab.strip().splitlines()[0].split('\t')
    physical=text.splitlines()
    line=next(n for n,t in enumerate(physical,1) if t=='\t'.join(header))
    rows=[]
    for n,t in enumerate(physical[line:],line+1):
        if not t.strip():continue
        cells=t.split('\t')
        if len(cells)!=len(header):raise ValueError('Native table schema/row width changed')
        rows.append((len(rows)+1,n,cells))
    return head,header,rows,line

def specification(column,proxy,label,unit,family,method,evidence='measurement',taxon=None,error=None,error_type=None):
    """Describe an explicit native column and conservative compatibility group."""
    return dict(column=column,proxy=proxy,label=label,unit=unit,family=family,method=method,
                evidence_type=evidence,taxon=taxon,error=error,error_type=error_type)

def specs(i,columns):
    """Reviewed selection by positional index preserves duplicate native headers."""
    S=specification
    if i==944656:return [S(3,'TOC','TOC · CP10BC','%','Geoquímica elemental','TOC as archived, Wu2016; no elemental depth-column reassignment')]
    if i==944660:return [
        S(4,'Sr_detrital','Sr · fracción detrítica','mg/kg','Geoquímica elemental','Published detrital Sr concentration, Wu2016'),
        S(5,'Sr87_Sr86_detrital','87Sr/86Sr · fracción detrítica','cociente','Isótopos radiogénicos','Published detrital 87Sr/86Sr, Wu2016'),
        S(6,'Nd143_Nd144_detrital','143Nd/144Nd · fracción detrítica','cociente','Isótopos radiogénicos','Published detrital 143Nd/144Nd, Wu2016'),
        S(7,'epsilon_Nd_detrital','εNd(0) · fracción detrítica','εNd','Isótopos radiogénicos','Published calculated epsilon Nd(0), Wu2016','published_transformation',error=8,error_type='Native epsilon-Nd uncertainty labelled calculated 2 sigma; no division by two')]
    if i==667403:return [S(2,'TOC','TOC · GeoB7608-1','%','Geoquímica elemental','Bahr2008: TC minus TIC; element analyser CHN as archived')]
    if i==667328:return [S(2,'Candona_d18O_PDB','δ18O · Candona spp.','‰ PDB','Isótopos estables','Finnigan MAT251; Candona spp.; PDB label retained; revised Bahr2008 age model',taxon='Candona spp.')]
    if i==962012:return [S(1,'TOC','TOC · Bichlersee','%','Geoquímica elemental','Published TOC, Prochnow2023'),S(2,'CaCO3','CaCO3 · Bichlersee','%','Sedimentología','Published CaCO3, Prochnow2023')]
    if i==962033:return [S(k,f'nC{chain}_dD','δ2H · n-C'+str(chain),'‰ VSMOW','Isótopos estables','Compound-specific n-alkane GC-IRMS, Prochnow2023','measurement',f'n-alkane C{chain}',k+1,'native analytical standard deviation') for k,chain in [(1,27),(3,29),(5,31)]]
    if i==962034:return [S(1,'fucose_d18O','δ18O · fucosa','‰ VSMOW','Isótopos estables','Fucose GC-IRMS, Prochnow2023','measurement','fucose',2,'native analytical standard error')]
    if i==940127:return [
        S(7,'C30_fatty_acid_dD','δ2H · ácido graso C30','‰ VSMOW','Isótopos estables','Compound-specific C30 fatty acid GC-IRMS, Tierney2022','measurement','C30 fatty acid',8,'native replicate analytical standard deviation'),
        S(9,'C30_fatty_acid_d13C','δ13C · ácido graso C30','‰ VPDB','Isótopos estables','Compound-specific C30 fatty acid GC-IRMS, Tierney2022','measurement','C30 fatty acid',10,'native replicate analytical standard deviation')]
    if i==961488:return [
        S(2,'nC31_dD_ice_corrected','δ2H · n-C31 · corregido hielo','‰ VSMOW','Isótopos estables','GC-IRMS n-C31; published ice-volume correction, Meyer2024','published_transformation','n-alkane C31',3,'native standard error'),
        S(4,'nC31_dD_vegetation_ice_corrected','δ2H · n-C31 · corregido vegetación/hielo','‰ VSMOW','Isótopos estables','GC-IRMS n-C31; published vegetation and ice-volume correction, Meyer2024','published_transformation','n-alkane C31',5,'native standard error'),
        S(6,'C4_plant_contribution','Aporte plantas C4 · n-C31','%','Biomarcadores','Published C4 contribution calculated from n-C31, Meyer2024','published_reconstruction','n-alkane C31',7,'native contribution error, level unspecified')]
    if i==995820:return [
        S(1,'leaf_wax_dD_NMF','δ2H · cera foliar NMF','‰ VSMOW','Isótopos estables','GC-IRMS and terrestrial NMF endmember, FernandezPerez2026','published_transformation','terrestrial leaf wax n-alkanes'),
        S(2,'precipitation_dD_leafwax','δ2H · precipitación reconstruida','‰ VSMOW','Isótopos estables','Published precipitation dD, epsilon_app -129 per mil, FernandezPerez2026','published_reconstruction'),
        S(5,'precipitation_dD_anomaly','Anomalía δ2H · precipitación','‰ VSMOW','Isótopos estables','Published deviation from OIPC MAP -56 per mil, FernandezPerez2026','published_transformation')]
    if i==954457:return [S(1,'TOC','TOC · Peixão','%','Geoquímica elemental','Published TOC, Hernandez2023')]
    if i==878051:return [
        S(3,'LOI_550C_4h','LOI · 550°C / 4h','%','Sedimentología','LOI 550 degrees C for 4 hours, Bajard2017'),
        S(4,'LOI_950C_2h','LOI · 950°C / 2h','%','Sedimentología','LOI 950 degrees C for 2 hours, Bajard2017'),
        S(5,'LOI_residual','Residuo · LOI','%','Sedimentología','Published LOI residue, Bajard2017')]
    if i==878053:
        return [S(k,'XRF_'+re.sub('[^A-Za-z0-9]','',columns[k].split(' [')[0]),columns[k].split(' [')[0]+' · XRF Verney','%','Geoquímica elemental','XRF mass fraction as archived, Bajard2017',error=k+1,error_type='native XRF standard deviation, same source mass-fraction scale') for k in range(2,len(columns),2)]
    if i in (69822,69823,69824,69825):return [S(2,'G_ruber_white_d18O_PDB','δ18O · G. ruber blanco','‰ PDB','Isótopos estables','Finnigan MAT251 G. ruber white, Weldeab2003; PDB not relabelled VPDB',taxon='Globigerinoides ruber white')]
    raise ValueError('Unreviewed dataset')

def chronology(i):
    """Explicit source age column; source clocks/models are never interpolated."""
    if i==940127:return 4,'published_age_model_median','Bacon · edad mediana publicada','Bacon posterior median calendar ka BP; no fitting; native probability bounds preserved'
    if i in BICH:return 0,'published_calendar','Calendario publicado · edad mediana','Median age ka BP, radiocarbon-based published chronology; no recalibration'
    if i in VERNEY:return (2 if i==878051 else 1),'published_calendar','Calendario publicado','Published cal ka BP from source parameter comment; no age-model fitting'
    if i in (995820,954457):return 0,'published_calendar','Calendario publicado','Hernandez2023 age model as archived; calibrated ka BP, reference 1950 CE'
    return (3 if i==944660 else 2 if i==944656 else 1),'published_BP','BP publicado · escala no armonizada','Published Age [ka BP] retained; independent chronology/calibration review not performed'

def curate():
    """Build an event-level fragment and full audit without changing native cells."""
    baseline=json.loads((ROOT/'data/processed/atlas-v3.json').read_text(encoding='utf8'))
    inventory=json.loads((ROOT/'data/processed/inventory-v2.json').read_text(encoding='utf8'))
    old_dois={str(r.get('dataset_doi') or '').lower() for r in baseline['records']}
    old_events={r.get('source_event',r.get('core',r['name'])) for r in baseline['records']}
    for i,expected in CONTRACT['_supporting_xml'].items():
        if sha((RAW/f'{i}.xml').read_bytes())!=expected:raise ValueError('Supporting XML changed')
    records={};series=[];quarantined=[];audits=[];all_dois=set();all_vectors={}
    for s in baseline['series']:
        fp=sha(json.dumps(sorted([[r[0],r[1]] for r in s['rows']],key=lambda r:(r[0] is None,r[0] or 0,r[1])),separators=(',',':')).encode());all_vectors[(s['unit'],fp)]=s['id']
    for i in IDS:
        source=CONTRACT[str(i)];head,columns,native_rows,line=read_native(i);doi=f'10.1594/PANGAEA.{i}'
        if doi.lower() in old_dois:raise ValueError('Dataset already in baseline')
        cr_raw=(RAW/('crossref-'+sha(source['paper_doi'].lower().encode())[:16]+'.json')).read_bytes();cr=json.loads(cr_raw)['message']
        if cr['DOI'].lower()!=source['paper_doi'].lower() or cr['published']['date-parts'][0][0]!=source['paper_year']:raise ValueError('Bibliographic identity/year changed')
        published=cr['published']['date-parts'][0]
        if date(*(published+[1,1])[:3])>date(2026,10,29):raise ValueError('Publication postdates reviewed snapshot')
        # Bichlersee child tables cite the bundle, whose native XML cites the paper.
        if source['paper_doi'].lower() not in head.lower():
            parent=962035 if i in BICH else None
            if not parent or f'PANGAEA.{parent}' not in head or source['paper_doi'].lower() not in (RAW/f'{parent}.xml').read_text(encoding='utf8').lower():raise ValueError('Unverified native paper relation')
        event_line=re.search(r'Event\(s\):\s*([^\n]+)',head).group(1);event=event_line.split(' * ')[0].split(' (')[0]
        if event in old_events:raise ValueError('Existing physical event: '+event)
        lat=float(re.search(r'LATITUDE:\s*([-\d.]+)',event_line).group(1));lon=float(re.search(r'LONGITUDE:\s*([-\d.]+)',event_line).group(1))
        if not (28<=lat<=48 and -10<=lon<=42):raise ValueError('Outside declared region')
        elev=float(re.search(r'ELEVATION:\s*([-\d.]+)',event_line).group(1))
        license_name=re.search(r'License:\s*([^\n]+)',head).group(1)
        license_code=re.search(r'\((CC-[A-Z0-9.-]+)\)',license_name).group(1)
        license_url=re.search(r'URI:\s*(https://creativecommons.org/[^)]+)',license_name).group(1)
        citation=re.search(r'Citation:\s*([^\n]+)',head).group(1)
        primary=PRIMARY.get(i,i);rid=f'pangaea-{primary}'
        age_col,status,chrono_label,age_model=chronology(i)
        if 'Age' not in columns[age_col] and 'age' not in columns[age_col]:raise ValueError('Reviewed age column absent')
        if rid not in records:
            records[rid]=dict(id=rid,name=event,core=event,source_event=event,physical_core_key='PANGAEA:event:'+event,provider='PANGAEA',realm='lake' if i in LAKES else 'marine',archive_type='lake_sediment' if i in LAKES else 'marine_sediment',latitude=lat,longitude=lon,elevation_m=elev if i in LAKES else None,water_depth_m=-elev if i not in LAKES else number((re.search(r'LAKE WATER DEPTH:\s*([-\d.]+)',event_line) or [None,None])[1]),dataset_doi=doi,publication_year=source['paper_year'],paper_doi=source['paper_doi'],paper_title=cr['title'][0],source_url='https://doi.pangaea.de/'+doi,license=license_code,license_url=license_url,raw_sha256=None,source_files=[],inventory_ids=[],chronology_status=status,time_scale=age_model,age_scale_status=age_model,review_status='native_columns_units_clock_and_article_identity_checked; independent age-model audit pending',qc_notes=['One event is one record; multiple tables are not independent cores','Chronology and values archived as published; no age fitting, recalibration or proxy conversion'])
        r=records[rid]
        if r['source_event']!=event or r['latitude']!=lat or r['longitude']!=lon:raise ValueError('Event/coordinate conflict among source tables')
        r['source_files'].append(dict(dataset_doi=doi,url='https://doi.pangaea.de/'+doi,raw_sha256=source['tsv_sha256'],xml_sha256=source['xml_sha256'],license=license_code,license_url=license_url,paper_doi=source['paper_doi'],publication_year=source['paper_year'],paper_title=cr['title'][0],citation=citation))
        r['inventory_ids']+= [x['id'] for x in inventory['records'] if str(x.get('dataset_doi') or '').lower()==doi.lower()]
        for spec in specs(i,columns):
            col=spec['column'];out=[];missing=0;rejected=[];age_bounds=[];native_bounds=[]
            for source_row,source_line,cells in native_rows:
                value=number(cells[col])
                if value is None:
                    if cells[col].strip():rejected.append(dict(source_row=source_row,cell=cells[col],reason='censored_or_nonfinite_or_nonnumeric'))
                    else:missing+=1
                    continue
                age=number(cells[age_col]);uncertainty=number(cells[spec['error']]) if spec['error'] is not None else None
                depth=next((cells[k] for k,c in enumerate(columns) if c.startswith('Depth sed')),None)
                out.append([age,value,source_row,source_line,cells[age_col],cells[col],None,uncertainty,depth])
                if i==940127:age_bounds.append([source_row,number(cells[2]),number(cells[3]),number(cells[5]),number(cells[6]),cells[2],cells[3],cells[5],cells[6]])
                if i==995820 and col==2:native_bounds.append(dict(source_row=source_row,epsilon_minus12_parameter=cells[3],epsilon_plus12_parameter=cells[4],note='Native min/max names are numerically reversed; not reordered or exported as standardized uncertainty'))
            if not out:continue
            out.sort(key=lambda r:(r[0] is None,r[0] or 0,r[2]))
            fingerprint=sha(json.dumps(sorted([[r[0],r[1]] for r in out],key=lambda r:(r[0] is None,r[0] or 0,r[1])),separators=(',',':')).encode())
            if len(out)>=10 and (spec['unit'],fingerprint) in all_vectors:raise ValueError('Exact complete series duplicate: '+all_vectors[(spec['unit'],fingerprint)])
            sid=f'pangaea-{i}:'+spec['proxy'];all_vectors[(spec['unit'],fingerprint)]=sid
            group=spec['proxy']+'_w:'+str(source['paper_year'])+'_'+str(i if i not in (69822,69823,69824,69825) else 69822)
            if i in (69822,69823,69824,69825):group='G_ruber_white_d18O_PDB_Weldeab2003_MAT251'
            s=dict(id=sid,record_id=rid,proxy=spec['proxy'],variable_id=spec['proxy'],label=spec['label'],unit=spec['unit'],family=spec['family'],method=spec['method'],compatibility_group=group,evidence_type=spec['evidence_type'],taxon=spec['taxon'],source_column=columns[col],source_column_index=col,source_header_original=columns,source_url=f'https://doi.pangaea.de/{doi}?format=textfile',dataset_doi=doi,paper_doi=source['paper_doi'],publication_year=source['paper_year'],citation=citation,authors=[dict(given=a.get('given'),family=a.get('family')) for a in cr.get('author',[])],license=license_code,license_url=license_url,raw_sha256=source['tsv_sha256'],xml_sha256=source['xml_sha256'],crossref_sha256=sha(cr_raw),source_event=event,age_column_original=columns[age_col],age_column_index=age_col,age_unit_original='ka BP',age_scale=age_model,chronology_status=status,chronology_label=chrono_label,age_model=age_model,age_transformation='identity: source point age in ka BP',original_unit=columns[col],uncertainty_type=spec['error_type'] or 'not_supplied_for_selected_column',value_uncertainty_source_column=columns[spec['error']] if spec['error'] is not None else None,depth_frame='native sediment depth m; no cross-table remapping',rows=out)
            if age_bounds:s['age_probability_bounds']=age_bounds;s['age_probability_levels']=[.025,.16,.84,.975]
            s['value_uncertainty_source_column_index']=spec['error']
            if spec['unit']=='‰ VSMOW':
                if 'VSMOW' not in head and 'V-SMOW' not in head:raise ValueError('VSMOW reference not explicit')
                s['standard_reference_evidence']='Native parameter COMMENT explicitly states VSMOW or V-SMOW; header shorthand SMOW preserved in original column; numerical identity'
            elif spec['unit']=='‰ VPDB':
                if 'vs. VPDB' not in head:raise ValueError('VPDB reference not explicit')
                s['standard_reference_evidence']='Native parameter COMMENT explicitly vs. VPDB; PDB header shorthand preserved; numerical identity'
            elif spec['unit']=='‰ PDB':s['standard_reference_evidence']='Native PDB label; equivalence to VPDB is not independently established and not assumed'
            if native_bounds:s['native_epsilon_sensitivity_parameters']=native_bounds
            if i==944656:s['qc_notes']=['Only the first depth/age/TOC block admitted; second conflicting Depth sed column and elemental block held pending source clarification']
            if i==667328:s['qc_notes']=['Source notes oxygen isotope values already published in 2006 with revised age model in this dataset; older version not separately ingested']
            if i in (69822,69823,69824,69825):s['qc_notes']=['Native PDB label retained; not assumed VPDB; old sapropel/stratigraphic chronology not independently audited']
            s['review_status']='native_cells_units_point_chronology_and_bibliography_checked'
            if i==995820:
                s['review_status']='quarantined_mixed_age_units_in_native_column'
                s['quarantine_reason']='Age [ka BP] column changes from fractional ka (-0.069 to 0.970) to integer-like 1003..11150 while source describes Holocene ~11100 years; no conditional division by 1000 inferred'
                s['chronology_status']='quarantined_mixed_units'
                quarantined.append(s)
            elif spec['unit']=='%' and any(x[1]<0 or x[1]>100 for x in out):
                s['review_status']='quarantined_percentage_outside_0_100'
                s['out_of_range_percent_cells']=sum(x[1]<0 or x[1]>100 for x in out)
                s['quarantine_reason']='Native percentage includes values outside [0,100]; whole series preserved without clipping or deletion'
                quarantined.append(s)
            else:series.append(s)
            ages=[x[0] for x in out if x[0] is not None];pairs=Counter((x[0],x[1]) for x in out);age_counts=Counter(ages)
            audits.append(dict(id=sid,record_id=rid,dataset_doi=doi,status=s['review_status'],values=len(out),value_min=min(x[1] for x in out),value_max=max(x[1] for x in out),age_min=min(ages) if ages else None,age_max=max(ages) if ages else None,values_missing_age=sum(x[0] is None for x in out),missing_value_cells=missing,rejected_cells=rejected,repeated_age_values=sum(n-1 for n in age_counts.values() if n>1),repeated_age_value_pairs=sum(n-1 for n in pairs.values() if n>1),zeros=sum(x[1]==0 for x in out),negative_age_values=sum(x[0] is not None and x[0]<0 for x in out),source_column_index=col,source_column=columns[col],raw_sha256=source['tsv_sha256']))
    # Record bibliographic fields refer to primary source; every series carries its
    # own paper/year/license so multi-table cores do not inherit a false source.
    for r in records.values():
        source=next(x for x in r['source_files'] if x['dataset_doi']==f"10.1594/PANGAEA.{int(r['id'].split('-')[1])}")
        for key in ('dataset_doi','paper_doi','publication_year','paper_title','citation','license','license_url'):r[key]=source[key]
        r['source_url']='https://doi.pangaea.de/'+source['dataset_doi']
        r['inventory_ids']=sorted(set(r['inventory_ids']))
        if len(r['source_files'])==1:r['raw_sha256']=r['source_files'][0]['raw_sha256']
    pending=[dict(dataset=944656,columns='elemental block after second depth column',reason='second native Depth sed conflicts with point age-depth block; no unsupported age assignment'),
       dict(dataset=995820,reason='All three series quarantined: mixed fractional ka and integer-like year magnitudes in a column labelled ka BP. No age repair inferred'),
       dict(dataset=944662,reason='SL114BC Sr/Nd table lacks point ages; no depth-age interpolation'),
       dict(dataset=878052,reason='grain-size table lacks ages; no join/interpolation to another table'),
       dict(dataset=115685,reason='foraminiferal assemblage table lacks ages'),
       dict(datasets=[951489,971569,971806,971862,208119],reason='downloaded depth-only tables not admitted to time-mapped collection'),
       dict(dataset=995820,columns=['native reconstructed min','native reconstructed max'],reason='epsilon sensitivity parameters numerically reversed relative to labels; preserved separately, not standardized confidence limits')]
    result=dict(fragment_version='pangaea-v4-2026-10-29-r1',baseline_version=baseline['version'],records=list(records.values()),series=series,quarantined_series=quarantined,audit=audits,pending=pending,transformations=['Source point ages in ka BP and numerical values preserved unchanged','Source PDB kept distinct from VPDB; VSMOW label only when explicit in native parameter comment','Native SD/SE/2-sigma types retained without rescaling','No averaging, smoothing, age interpolation or new climate calibration'])
    OUTPUT.parent.mkdir(parents=True,exist_ok=True);OUTPUT.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf8')
    report={k:v for k,v in result.items() if k not in ('records','series','quarantined_series')}
    report['quarantined_series']=[{k:v for k,v in s.items() if k!='rows'} for s in quarantined]
    report['counts']=dict(records=len(records),reviewed_datasets=len(IDS),active_datasets=len({s['dataset_doi'] for s in series}),series=len(series),values=sum(len(s['rows']) for s in series),quarantined_series=len(quarantined),quarantined_values=sum(len(s['rows']) for s in quarantined))
    report['active_age_extent_ka_bp']=[min(r[0] for s in series for r in s['rows'] if r[0] is not None),max(r[0] for s in series for r in s['rows'] if r[0] is not None)]
    report['records']=[dict(id=r['id'],event=r['source_event'],latitude=r['latitude'],longitude=r['longitude'],realm=r['realm'],datasets=[x['dataset_doi'] for x in r['source_files']]) for r in records.values()]
    AUDIT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--download',action='store_true');a=p.parse_args()
    if a.download:acquire()
    d=curate();print(json.dumps(dict(records=len(d['records']),datasets=len(IDS),series=len(d['series']),values=sum(len(s['rows']) for s in d['series']))))

