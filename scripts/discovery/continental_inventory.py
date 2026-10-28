"""Versioned, bounded NOAA/Neotoma metadata discovery; never downloads observations."""
import json, hashlib, time, math
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'data/interim/discovery_continental'
BBOX=(-10,28,42,48)
def fetch(url,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists(): raw=path.read_bytes()
    else:
        error=None
        for attempt in range(3):
            try:
                with urlopen(Request(url,headers={'User-Agent':'MediterraneanMultiproxyAtlas/0.3','Accept':'application/json'}),timeout=50) as r: raw=r.read()
                path.write_bytes(raw);break
            except Exception as e:error=e;time.sleep(attempt+1)
        else:raise error
    return json.loads(raw),dict(url=url,path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def inside(lat,lon):return all(isinstance(x,(int,float)) and math.isfinite(x) for x in (lat,lon)) and 28<=lat<=48 and -10<=lon<=42

def main():
    records=[];manifest=[];failures=[]
    headers_url='https://www.ncei.noaa.gov/access/paleo-search/study/search.json?'+urlencode(dict(dataPublisher='NOAA',minLat=28,maxLat=48,minLon=-10,maxLon=42,headersOnly='true',limit=10000))
    headers,m=fetch(headers_url,DEST/'noaa_headers_all.json');manifest.append(m)
    allowed={'PALEOCEANOGRAPHY':'marine','SPELEOTHEMS':'speleothem','PALEOLIMNOLOGY':'lake','BOREHOLE':'terrestrial','LOESS AND PALEOSOL':'terrestrial','LAKE LEVELS':'lake'}
    selected=[s for s in headers['study'] if s.get('dataType') in allowed]
    def study(h):
        sid=str(h['NOAAStudyId']);url='https://www.ncei.noaa.gov/access/paleo-search/study/search.json?'+urlencode({'NOAAStudyId':sid})
        try:return h,fetch(url,DEST/'studies'/f'{sid}.json'),None
        except Exception as e:return h,None,str(e)
    for number,(h,result,error) in enumerate(ThreadPoolExecutor(max_workers=3).map(study,selected),1):
        if error:failures.append(dict(study=h['NOAAStudyId'],error=error));continue
        d,m=result;manifest.append(m)
        for s in d['study']:
            for site in s.get('site',[]):
                geo=site.get('geo',{});g=geo.get('geometry',{});prop=geo.get('properties',{})
                if g.get('type','').upper()!='POINT':continue
                # NOAA POINT arrays are latitude, longitude (not GeoJSON lon, lat).
                try:lat,lon=map(float,g['coordinates'])
                except (ValueError,TypeError):continue
                if not inside(lat,lon):continue
                pubs=s.get('publication') or [];doi=(s.get('doi') or '').replace('https://doi.org/','')
                tables=site.get('paleoData') or [];ages=[]
                for t in tables:
                    for k in ('earliestYearBP','mostRecentYearBP'):
                        try:ages.append(float(t[k])/1000)
                        except (KeyError,TypeError,ValueError):pass
                records.append(dict(id=f"noaa:{s['NOAAStudyId']}:{site['NOAASiteId']}",provider='NOAA WDS',source_id=str(site['NOAASiteId']),study_id=str(s['NOAAStudyId']),name=site['siteName'],latitude=lat,longitude=lon,realm=allowed[h['dataType']],archive_type=h['dataType'].lower(),record_type='site',source_url=s['onlineResourceLink']+'?siteId='+str(site['NOAASiteId']),dataset_doi=doi or None,publication_year=pubs[0].get('pubYear') if pubs else None,campaigns=[],proxies=sorted({v.get('cvShortName') or v.get('cvWhat') for t in tables for f in t.get('dataFile',[]) for v in f.get('variables',[]) if v.get('cvShortName') or v.get('cvWhat')})[:100],source_locators=[dict(study=s['NOAAStudyId'],site=site['NOAASiteId'])],metadata_status='source_site_metadata_not_numeric_review',raw_sha256=m['sha256'],age_max_ka_bp=max(ages) if ages else None,age_min_ka_bp=min(ages) if ages else None,age_basis='archived NOAA table coverage in years BP divided by 1000, not individual samples',study_name=s['studyName'],publications=[{k:p.get(k) for k in ('title','pubYear','identifier')} for p in pubs],license=s.get('dataLicenseUrl'),coordinate_basis='source POINT, no bounding-box centroid'))
        if number%25==0:print('NOAA',number,'/',len(selected),flush=True)
    noaa_count=len(records)
    # Use the documented GeoJSON form: WKT was observed not to filter this endpoint.
    polygon={'type':'Polygon','crs':{'type':'name','properties':{'name':'EPSG:4326'}},'coordinates':[[[-10,28],[42,28],[42,48],[-10,48],[-10,28]]]}
    offset=0;sites=[];seen=set();neo_pages=0
    while True:
        url='https://api.neotomadb.org/v2.0/data/sites?'+urlencode({'loc':json.dumps(polygon,separators=(',',':')),'limit':1000,'offset':offset})
        d,m=fetch(url,DEST/'neotoma'/f'{offset:05d}.json');manifest.append(m);neo_pages+=1
        if d.get('status')!='success':raise RuntimeError('Neotoma failed: '+str(d.get('message')))
        batch=d.get('data',[])
        for s in batch:
            if s['siteid'] in seen:raise RuntimeError('Repeated site ID during pagination')
            seen.add(s['siteid']);sites.append(s)
            g=json.loads(s['geography']) if isinstance(s.get('geography'),str) else s.get('geography',{})
            if not g or g.get('type')!='Point':continue
            lon,lat=g['coordinates'][:2]
            if not inside(lat,lon):continue
            units=s.get('collectionunits') or []
            for unit in units:
                kind=(unit.get('collectionunittype') or '').lower()
                if kind not in ('core','speleothem','section','outcrop','excavation','surface sample'):continue
                ds=unit.get('datasets') or [];uid=unit['collectionunitid']
                records.append(dict(id=f"neotoma:{s['siteid']}:{uid}",provider='Neotoma',source_id=str(uid),name=unit.get('collectionunit') or unit.get('handle') or s['sitename'],site_name=s['sitename'],site_id=s['siteid'],latitude=lat,longitude=lon,realm='continental',archive_type=kind,record_type='core' if kind=='core' else 'collection_unit',source_url=f"https://apps.neotomadb.org/explorer/?siteid={s['siteid']}",campaigns=[],proxies=sorted({x['datasettype'] for x in ds}),dataset_ids=[x['datasetid'] for x in ds],source_locators=[dict(site_id=s['siteid'],collectionunit_id=uid)],metadata_status='source_collection_unit_not_numeric_review',raw_sha256=m['sha256'],license=None,coordinate_basis='source site coordinate, not independently measured collection-unit position'))
        if len(batch)<1000:break
        offset+=len(batch)
    coverage=dict(noaa_header_rows=len(headers['study']),noaa_selected_studies=len(selected),noaa_retrieved_studies=len(selected)-len(failures),noaa_failures=failures,noaa_entries=noaa_count,neotoma_sites=len(sites),neotoma_pages=neo_pages,neotoma_entries=len(records)-noaa_count,neotoma_pagination_complete=True,limitations=['Point locations only; site bounds are not converted to invented coordinates','NOAA archive-type filter excludes global climate reconstructions/tree rings/corals; campaigns are not inferred from studies','Neotoma includes collection units; multiple units at a site are not automatically independent locations','No observations downloaded; licenses and chronology require record-level review'])
    out=dict(source='NOAA WDS and Neotoma',scope=dict(bbox=BBOX),coverage=coverage,records=records,request_manifest=manifest,accessed_at_utc=datetime.now(timezone.utc).isoformat())
    (DEST/'inventory.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf8');print(coverage,flush=True)
if __name__=='__main__':main()
