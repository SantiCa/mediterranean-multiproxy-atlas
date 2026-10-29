"""Explicit API integration check; never downloads provider data.

Production requires the Sites-owned service credential supplied through hidden
stdin, sent only to the exact configured owner-private Site. It is never saved.
The public Cloudflare deployment (--public-https) sends no credential.

Several --seed files may be given (release chain). The API serves the newest
release whose load into D1 is complete; that release is compared cell by cell
against its own seed, and a pending newer release is reported, not failed.
"""
import argparse
import json
import getpass
import re
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode,urlsplit
ROOT=Path(__file__).resolve().parents[1]
def group_key(s):return json.dumps([s['proxy'],s['compatibility_group'],s['unit']],ensure_ascii=False,separators=(',',':'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:5173');p.add_argument('--site-service-access',action='store_true');p.add_argument('--public-https',action='store_true',help='Self-hosted public Cloudflare URL (no credentials sent)')
    p.add_argument('--seed',type=Path,action='append',help='Release seed(s), oldest first; default atlas-v3.json');p.add_argument('--report-prefix',default='quantitative');a=p.parse_args()
    if not re.fullmatch(r'[a-z0-9_]+',a.report_prefix):raise ValueError('Invalid report prefix')
    # Cloudflare's browser-integrity check rejects the default Python-urllib agent (403).
    headers={'Content-Type':'application/json','User-Agent':'medatlas-validator/1.0 (+https://github.com/SantiCa/mediterranean-multiproxy-atlas)'}
    if a.site_service_access:
        if a.url!='https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site':raise ValueError('Unexpected Site destination')
        headers['OAI-Sites-Authorization']='Bearer '+getpass.getpass('Sites service token (hidden): ')
    elif a.public_https:
        # Public self-hosted deployment: HTTPS only, *.workers.dev, never sends a credential.
        u=urlsplit(a.url)
        if u.scheme!='https' or not (u.hostname or '').endswith('.workers.dev'):raise ValueError('--public-https expects an https://*.workers.dev URL')
    elif urlsplit(a.url).hostname not in ('localhost','127.0.0.1'):raise ValueError('Nonlocal API requires explicit Site service access')
    def call(path,body=None):
        request=Request(a.url+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
        with urlopen(request,timeout=60) as response:return json.load(response)
    catalog=call('/api/catalog')
    if catalog.get('needsBootstrap'):raise AssertionError('No complete release in D1 yet (load pending)')
    seeds={}
    for path in a.seed or [ROOT/'data/processed/atlas-v3.json']:
        s=json.loads(path.read_text(encoding='utf8'));seeds[s['version']]=s
    latest=list(seeds)[-1];served=catalog['release']['id']
    if served not in seeds:raise AssertionError('Served release '+served+' not among given seeds')
    seed=seeds[served]
    assert len(catalog['records'])==len(seed['records'])
    assert len(catalog['series'])==len(seed['series'])
    assert all(not s['rows'] for s in catalog['series']), 'Metadata must not preload observations'
    expected={s['id']:s for s in seed['series']}
    groups={group_key(s) for s in seed['series']}
    checked=0;series_count=0;max_payload_group=0
    for key in sorted(groups):
        result=call('/api/observations?'+urlencode({'group':key}))
        assert result['version']==seed['version']
        max_payload_group=max(max_payload_group,result['count'])
        for s in result['series']:
            wanted=expected[s['id']]
            actual={r[2]:r for r in s['rows']}
            assert actual=={r[2]:r for r in wanted['rows']}, s['id']
            assert {k:v for k,v in s.items() if k!='rows'}=={k:v for k,v in wanted.items() if k!='rows'},s['id']+' metadata'
            checked+=len(s['rows']);series_count+=1
    assert checked==sum(len(s['rows']) for s in seed['series'])
    assert series_count==len(seed['series'])
    key=next(k for k in groups if 'sst_alkenone_mueller1998_annual' in k)
    filtered=call('/api/observations?'+urlencode({'group':key,'yearMin':2000,'yearMax':2004,'provider':'PANGAEA','realm':'marine'}))
    byrecord={r['id']:r for r in catalog['records']}
    assert all(2000<=byrecord[s['record_id']]['publication_year']<=2004 for s in filtered['series'])
    link=call('/api/inventory?view=detail&id=noaa%3A28070%3A58190')
    assert link['curated_record_id']=='noaa-28070-58190'
    inventory_links=0
    for record in seed['records']:
        for identifier in record.get('inventory_ids',[]):
            detail=call('/api/inventory?'+urlencode({'view':'detail','id':identifier}))
            assert record['id'] in detail.get('curated_record_ids',[]),identifier
            inventory_links+=1
    # One age filter stays separate from a series-level publication-year filter.
    for key in sorted(groups)[:8]:
        expected_ids={s['id'] for s in seed['series'] if group_key(s)==key and (s.get('publication_year',byrecord[s['record_id']].get('publication_year')) or 0)>=2020}
        selected=call('/api/observations?'+urlencode({'group':key,'yearMin':2020}))
        assert {s['id'] for s in selected['series']}==expected_ids
    report={'version':seed['version'],'latest_release':latest,'latest_loaded':served==latest,'inventory_links_checked':inventory_links,'records':len(catalog['records']),'series':series_count,'values_compared_cell_by_cell':checked,'groups':len(groups),'largest_group_values':max_payload_group,'metadata_has_no_observations':True,'combined_filter_checked':True,'exact_inventory_link_checked':True}
    report['destination']='owner-private production' if a.site_service_access else ('public cloudflare '+a.url if a.public_https else 'local')
    report_name=a.report_prefix+('_production_check.json' if a.site_service_access else '_public_check.json' if a.public_https else '_api_check.json')
    (ROOT/'reports'/report_name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    tail='' if served==latest else ' — '+latest+' en carga (límite diario D1); se reanuda sola'
    print('OK '+served+': '+str(checked)+'/'+str(checked)+' valores, '+str(len(groups))+' grupos'+tail)
if __name__=='__main__':main()
