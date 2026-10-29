"""Explicit API integration check; never downloads provider data.

Production requires the Sites-owned service credential supplied through hidden
stdin, sent only to the exact configured owner-private Site. It is never saved.
"""
import argparse
import json
import getpass
import re
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode,urlsplit
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:5173');p.add_argument('--site-service-access',action='store_true');p.add_argument('--seed',type=Path,default=ROOT/'data/processed/atlas-v3.json');p.add_argument('--report-prefix',default='quantitative_v3');a=p.parse_args()
    if not re.fullmatch(r'[a-z0-9_]+',a.report_prefix):raise ValueError('Invalid report prefix')
    headers={'Content-Type':'application/json'}
    if a.site_service_access:
        if a.url!='https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site':raise ValueError('Unexpected Site destination')
        headers['OAI-Sites-Authorization']='Bearer '+getpass.getpass('Sites service token (hidden): ')
    elif urlsplit(a.url).hostname not in ('localhost','127.0.0.1'):raise ValueError('Nonlocal API requires explicit Site service access')
    def call(path,body=None):
        request=Request(a.url+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
        with urlopen(request,timeout=60) as response:return json.load(response)
    catalog=call('/api/catalog')
    requests=0; modes=set(); observation_batches=0
    if catalog.get('needsBootstrap'):
        cursor={'stage':'records','offset':0}
        for _ in range(2000):
            result=call('/api/bootstrap',cursor);requests+=1
            modes.add(result.get('mode','legacy'));observation_batches+=int(cursor['stage']=='observations')
            if requests%40==0:print('Import batches: '+str(requests),flush=True)
            if result.get('ready'):break
            cursor={'stage':result['stage'],'offset':result['next']}
        else:raise AssertionError('Import did not finish')
        catalog=call('/api/catalog')
    seed=json.loads(a.seed.read_text(encoding='utf8'))
    assert catalog['release']['id']==seed['version']
    assert len(catalog['records'])==len(seed['records'])
    assert len(catalog['series'])==len(seed['series'])
    assert all(not s['rows'] for s in catalog['series']), 'Metadata must not preload observations'
    expected={s['id']:s for s in seed['series']}
    groups={json.dumps([s['proxy'],s['compatibility_group'],s['unit']],ensure_ascii=False,separators=(',',':')) for s in seed['series']}
    checked=0;series_count=0;max_payload_group=0
    byrecord={r['id']:r for r in seed['records']}
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
    if 'v4' in a.report_prefix:
        for key in sorted(groups)[:8]:
            expected_ids={s['id'] for s in seed['series'] if json.dumps([s['proxy'],s['compatibility_group'],s['unit']],ensure_ascii=False,separators=(',',':'))==key and (s.get('publication_year',byrecord[s['record_id']].get('publication_year')) or 0)>=2020}
            selected=call('/api/observations?'+urlencode({'group':key,'yearMin':2020}))
            assert {s['id'] for s in selected['series']}==expected_ids

    report={'version':seed['version'],'bootstrap_requests':requests,'bootstrap_modes':sorted(modes),'observation_batches':observation_batches,'inventory_links_checked':inventory_links,'records':len(catalog['records']),'series':series_count,'values_compared_cell_by_cell':checked,'groups':len(groups),'largest_group_values':max_payload_group,'metadata_has_no_observations':True,'combined_filter_checked':True,'exact_inventory_link_checked':True}
    report['destination']='owner-private production' if a.site_service_access else 'local'
    report_name=a.report_prefix+('_production_check.json' if a.site_service_access else '_api_check.json')
    (ROOT/'reports'/report_name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))
if __name__=='__main__':main()
