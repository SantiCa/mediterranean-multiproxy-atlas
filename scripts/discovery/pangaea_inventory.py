"""Discover PANGAEA sediment/core metadata via documented DataCite search.

Dataset points are deliberately not promoted to core identities. Native PANGAEA
XML enriches the explicitly selected seed events/campaigns; no measurements are
fetched. Cached responses are immutable and every request has a hash/locator.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'data/interim/discovery_pangaea'
BBOX=(-10.,28.,42.,48.)
QUERY=('geoLocations.geoLocationPoint.pointLatitude:[28 TO 48] AND '
       'geoLocations.geoLocationPoint.pointLongitude:[-10 TO 42] AND '
       '(subjects.subject:sediment* OR titles.title:core* OR subjects.subject:drilling)')
FIELDS='doi,titles,subjects,geoLocations,publicationYear,relatedIdentifiers,rightsList,url'
NS={'p':'http://www.pangaea.de/MetaData'}
UA='MediterraneanMultiproxyAtlas/0.3 (metadata discovery)'

def now(): return datetime.now(timezone.utc).isoformat()

def fetch(url,path,accept='application/json'):
    """Use immutable cached bytes, with bounded retries only for transient errors."""
    sidecar=path.with_suffix(path.suffix+'.request.json')
    if path.exists() and sidecar.exists():
        raw=path.read_bytes();info=json.loads(sidecar.read_text(encoding='utf-8'))
        if hashlib.sha256(raw).hexdigest()!=info['sha256']:raise RuntimeError(f'Corrupt cached source: {path}')
        if info['requested_url']!=url:raise RuntimeError(f'Cache query differs: {path}')
        return raw,info
    for attempt in range(4):
        try:
            headers={'User-Agent':UA}
            if accept:headers['Accept']=accept
            with urlopen(Request(url,headers=headers),timeout=90) as r:
                raw=r.read(25_000_001)
                if len(raw)>25_000_000:raise RuntimeError('Metadata response exceeds 25 MB limit')
                info=dict(requested_url=url,resolved_url=r.geturl(),accessed_at_utc=now(),content_type=r.headers.get('Content-Type'),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            break
        except (HTTPError,URLError,TimeoutError) as e:
            code=getattr(e,'code',None)
            if attempt==3 or (code is not None and code not in (429,500,502,503,504)):raise
            time.sleep(min(2**attempt,8))
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_bytes()!=raw:raise RuntimeError(f'Refusing source replacement: {path}')
    path.write_bytes(raw);sidecar.write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8')
    return raw,info

def in_bbox(lat,lon):
    return isinstance(lat,(int,float)) and isinstance(lon,(int,float)) and math.isfinite(lat) and math.isfinite(lon) and BBOX[1]<=lat<=BBOX[3] and BBOX[0]<=lon<=BBOX[2]

def text(n,path):
    child=n.find(path,NS);return child.text.strip() if child is not None and child.text else None

def native_event_records(doi):
    dataset_id=doi.rsplit('.',1)[-1]
    raw,info=fetch('https://doi.pangaea.de/'+doi,DEST/'native'/f'{dataset_id}.xml','application/vnd.pangaea.metadata+xml')
    root=ET.fromstring(raw);rows=[]
    for event in root.findall('.//p:event',NS):
        # Campaigns can also be represented as events after the 2026 hierarchy change.
        if 'campaign' in (event.get('typeName','')+' '+event.get('displayTypeName','')).lower():continue
        name=text(event,'p:label') or text(event,'p:name')
        try:lat,lon=float(text(event,'p:latitude')),float(text(event,'p:longitude'))
        except (TypeError,ValueError):continue
        if not name or not in_bbox(lat,lon):continue
        source_id=event.get('id');campaigns=[]
        candidates=event.findall('p:campaign',NS)+[x for x in event.findall('p:event',NS) if 'campaign' in (x.get('typeName','')+' '+x.get('displayTypeName','')).lower()]
        for c in candidates:
            label=text(c,'p:label') or text(c,'p:name')
            if not label:continue
            native_id=c.get('id') or c.get('legacyId')
            # IDs are event-scoped XML IDs; retain native ID plus URI, never guess a prefix.
            global_id=re.search(r'campaign(\d+)$',native_id or '')
            identity='pangaea:campaign:'+global_id.group(1) if global_id else 'pangaea:campaign:'+hashlib.sha256((text(c,'p:URI') or native_id or label).encode()).hexdigest()[:16]
            campaigns.append(dict(id=identity,name=label,url=text(c,'p:URI'),provider='PANGAEA',source_locator=f'{doi}#/{event.tag.split("}")[-1]}[@id="{source_id}"]/campaign[@id="{native_id}"]',source_native_id=native_id,optional_label=text(c,'p:optionalLabel') or text(c,'p:optionalName'),basis=text(c,'p:basis/p:name'),start=text(c,'p:dateTime') or text(c,'p:start'),end=text(c,'p:dateTime2') or text(c,'p:end')))
        method=text(event,'p:method/p:name')
        elevation=text(event,'p:elevation')
        rows.append(dict(id='pangaea:'+str(source_id),provider='PANGAEA',source_id=source_id,name=name,latitude=lat,longitude=lon,realm='marine' if elevation is not None and float(elevation)<0 else 'unknown',archive_type='sediment_core',source_url='https://doi.org/'+doi,dataset_doi=doi,campaigns=campaigns,proxies=[],source_locators=[{'doi':doi,'xml_event_id':source_id,'source_uri':info['resolved_url']}],metadata_status='native_event_metadata_not_numeric_review',raw_sha256=info['sha256'],method=method,elevation_m=float(elevation) if elevation is not None else None,optional_labels=[x.text for x in event.findall('p:optionalLabel',NS) if x.text],xml_schema_version=root.get('version'),accessed_at_utc=info['accessed_at_utc']))
    return rows,info

def main():
    p=argparse.ArgumentParser();p.add_argument('--offline',action='store_true',help='Require existing discovery pages; native seed metadata uses immutable cache');args=p.parse_args()
    DEST.mkdir(parents=True,exist_ok=True)
    manifests=[];datasets=[];seen=set();total=None;pages=0;next_url=None
    page=1
    while True:
        url='https://api.datacite.org/dois?'+urlencode({'query':QUERY,'client-id':'pangaea.repository','page[size]':1000,'page[number]':page,'fields[dois]':FIELDS,'sort':'name'})
        path=DEST/'pages'/f'{page:04d}.json'
        if args.offline and not path.exists():raise RuntimeError(f'Missing offline metadata page: {path}')
        raw,info=fetch(url,path);j=json.loads(raw);manifests.append(info);pages+=1
        if total is None:total=j['meta']['total']
        if total!=j['meta']['total']:raise RuntimeError('Result set changed during paging; retain pages and retry in a new snapshot')
        for item in j['data']:
            a=item['attributes'];doi=a['doi'].lower()
            if doi in seen:raise RuntimeError(f'Duplicate DOI across pages: {doi}')
            seen.add(doi)
            points=[]
            for i,g in enumerate(a.get('geoLocations',[])):
                point=g.get('geoLocationPoint',{});lat=point.get('pointLatitude');lon=point.get('pointLongitude')
                if in_bbox(lat,lon):points.append(dict(latitude=lat,longitude=lon,source_locator=f'geoLocations[{i}].geoLocationPoint'))
            datasets.append(dict(id='datacite:'+doi,provider='PANGAEA',source_id=doi,dataset_doi=doi,title='; '.join(x['title'] for x in a.get('titles',[])),publication_year=a.get('publicationYear'),source_url='https://doi.org/'+doi,points=points,places=[g['geoLocationPlace'] for g in a.get('geoLocations',[]) if g.get('geoLocationPlace')],subjects=a.get('subjects',[]),related_identifiers=a.get('relatedIdentifiers',[]),rights=a.get('rightsList',[]),metadata_status='dataset_metadata_not_a_core_identity',raw_sha256=info['sha256'],source_locator=f'data[{len(datasets)%1000}].attributes',accessed_at_utc=info['accessed_at_utc']))
        print(f'DataCite page {page}: {len(seen)}/{total}',flush=True)
        if len(seen)>=total:break
        if not j['data']:raise RuntimeError('Empty page before reported total')
        page+=1
    if len(seen)!=total:raise RuntimeError('Reported DOI count mismatch')
    seed=json.loads((ROOT/'data/processed/atlas-v1.json').read_text(encoding='utf-8'))
    seed_dois=sorted({r['dataset_doi'] for r in seed['records'] if r.get('provider')=='PANGAEA'})
    records={};native_manifest=[];native_failures=[]
    def retrieve(doi):
        try:return doi,native_event_records(doi),None
        except Exception as e:return doi,None,str(e)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for doi,result,error in pool.map(retrieve,seed_dois):
            if error:native_failures.append(dict(doi=doi,error=error));continue
            rows,meta=result;native_manifest.append(meta)
            for row in rows:
                if row['id'] in records:
                    existing=records[row['id']]
                    existing['source_locators'].extend(row['source_locators'])
                    existing.setdefault('dataset_dois',[existing['dataset_doi']]).append(doi)
                else:records[row['id']]=row
    coverage=dict(query=QUERY,repository_filter='client-id=pangaea.repository',reported_datasets=total,retrieved_unique_datasets=len(seen),page_size=1000,pages_retrieved=pages,pagination_complete=True,datasets_with_point_inside_bbox=sum(bool(d['points']) for d in datasets),point_count=sum(len(d['points']) for d in datasets),native_datasets_requested=len(seed_dois),native_datasets_retrieved=len(native_manifest),native_failures=native_failures,real_event_count=len(records),events_with_campaign=sum(bool(r['campaigns']) for r in records.values()),limitations=['Exhaustive only for this explicit DataCite query at retrieval time; not all PANGAEA sediment cores','Point filters omit records with only bounding boxes or missing georeferencing; query may match sediment datasets without cores','Separate latitude/longitude index fields can match different points; canonical points are post-filtered within bbox','DataCite points are dataset-level; not promoted to named cores or sampling events','Native event/campaign enrichment restricted explicitly to the ten existing PANGAEA seed datasets','Current source XML can contain old and new names; labels preferred and all unknown fields remain in cached originals','No measurements downloaded or parsed; publication_year here is dataset metadata year, not automatically paper year'])
    output=dict(source='PANGAEA via DataCite + source-native seed XML',scope=dict(bbox=list(BBOX),label='Mediterranean and adjacent regions, rectangular search domain'),coverage=coverage,records=list(records.values()),datasets=datasets,request_manifest=manifests+native_manifest,created_at_utc=now())
    target=DEST/'inventory.json';target.write_text(json.dumps(output,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    (DEST/'coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(coverage,ensure_ascii=True,indent=2));print('inventory bytes',target.stat().st_size)

if __name__=='__main__':main()
