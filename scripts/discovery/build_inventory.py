"""Build source-linked discovery catalogue. Entries are not asserted to be unique cores.

PaleoMED20 and IMLGS sources preserve native core/cruise identities. DataCite DOI
records are explicitly dataset references, never guessed sediment-core identities.
"""
import json,hashlib,zipfile,re,math,argparse
from pathlib import Path
from collections import Counter,defaultdict
from urllib.request import Request,urlopen
from urllib.parse import urlencode
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'data/interim/discovery_paleomed'
NS={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def number(x):
 try:
  v=float(x);return v if math.isfinite(v) else None
 except (TypeError,ValueError):return None
def text(x):return str(x or '').strip()
def key(x):return re.sub(r'\s+','',text(x)).casefold()
def ident(provider,*parts):return provider+':'+hashlib.sha256('|'.join(map(str,parts)).encode()).hexdigest()[:20]
def sheet(z,n,strings):
 rows=[]
 for row in E.fromstring(z.read(f'xl/worksheets/sheet{n}.xml')).findall('x:sheetData/x:row',NS):
  d={}
  for c in row.findall('x:c',NS):
   v=c.find('x:v',NS);value=v.text if v is not None else ''
   if c.get('t')=='s' and value:value=strings[int(value)]
   if c.get('t')=='inlineStr':value=''.join(x.text or '' for x in c.findall('.//x:t',NS))
   d[re.sub(r'\d+$','',c.get('r'))]=value
  rows.append((int(row.get('r')),d))
 return rows

def paleomed():
 meta=json.loads((DEST/'figshare_metadata.json').read_text(encoding='utf8'));f=meta['files'][0];path=DEST/f['name']
 if not path.exists():path.write_bytes(urlopen(Request(f['download_url'],headers={'User-Agent':'MediterraneanMultiproxyAtlas/0.3'}),timeout=60).read())
 raw=path.read_bytes();assert hashlib.md5(raw).hexdigest()==f['computed_md5'];sha=hashlib.sha256(raw).hexdigest()
 z=zipfile.ZipFile(path);strings=[''.join(t.text or '' for t in e.findall('.//x:t',NS)) for e in E.fromstring(z.read('xl/sharedStrings.xml')).findall('x:si',NS)]
 cores=sheet(z,1,strings);proxies=sheet(z,3,strings);ages=sheet(z,6,strings);byproxy=defaultdict(set);byage=defaultdict(list)
 labels=proxies[1][1]
 for rn,d in proxies[2:]:
  for col,label in labels.items():
   if (len(col)==1 or col in ('AA','AB','AC')) and text(d.get(col)).lower()=='yes' and label:byproxy[key(d.get('AD'))].add(label)
 for rn,d in ages[1:]:
  for col in ('C','D'):
   v=number(d.get(col))
   if v is not None:byage[key(d.get('A'))].append(v)
 records=[];excluded=[]
 for rn,d in cores[1:]:
  lat,lon=number(d.get('K')),number(d.get('L'));name=text(d.get('H'))
  if not name or lat is None or lon is None or not (28<=lat<=48 and -10<=lon<=42):excluded.append(dict(row=rn,name=name,latitude=d.get('K'),longitude=d.get('L')));continue
  campaign=text(d.get('A'));platform=text(d.get('F'));year=text(d.get('E'));cid=ident('paleomed20:campaign',campaign,year,platform)
  age=byage[key(name)]
  records.append(dict(id=f'paleomed20:row:{rn}',provider='PaleoMED20',source_id=str(rn),name=name,latitude=lat,longitude=lon,realm='marine',archive_type='sediment_core',record_type='core',source_url='https://doi.org/'+meta['doi'],dataset_doi=meta['doi'],publication_year=int(float(d['Y'])) if number(d.get('Y')) is not None else None,campaigns=[dict(id=cid,name=campaign,provider='PaleoMED20',platform=platform,expedition_year=year,source_locator=f'Core database!A{rn}:F{rn}')] if campaign and campaign!='NA' else [],proxies=sorted(byproxy[key(name)]),age_min_ka_bp=min(age) if age else None,age_max_ka_bp=max(age) if age else None,age_basis='PaleoMED20 Record Density columns C/D, kyr as labelled; coverage metadata, not sample ages',source_locators=[dict(sheet='Core database',row=rn)],metadata_status='published_inventory_metadata_not_numeric_review',raw_sha256=sha,license=meta['license']['url'],basin=d.get('D'),area=d.get('G'),water_depth_m=number(d.get('M')),core_length_m=number(d.get('N')),reference=d.get('X'),paper_doi_as_archived=d.get('Z'),bibliographic_link_as_archived=d.get('AA'),proxy_data_reported=d.get('AB'),coordinate_basis='source decimal degrees WGS84',source_cells={k:d.get(k) for k in ('A','E','F','H','K','L','S','Y','Z')}))
 return records,dict(provider='PaleoMED20',reported_core_rows=1524,read_core_rows=len(cores)-1,mapped_entries=len(records),excluded_rows=excluded,version=meta['doi'],license=meta['license']['url'],source_url='https://doi.org/'+meta['doi'],source_sha256=sha,complete_for_published_file=len(cores)-1==1524,limitations=['Metadata inventory, not 1524 quantitative series','Publication DOI cells are retained as archived; not all original articles independently checked','Record Density intervals are coverage statements, not harmonized age models'])

def imlgs():
 p=ROOT/'data/interim/discovery_core_archives';raw=(p/'imlgs_probe.json').read_bytes();d=json.loads(raw)['table'];sha=hashlib.sha256(raw).hexdigest();records=[];excluded=Counter()
 query=(p/'imlgs_probe_url.txt').read_text().strip()
 for i,row in enumerate(d['rows'],1):
  r=dict(zip(d['columnNames'],row));device=text(r['DEVICE']).lower()
  if not (device.startswith('core') or device.startswith('corer') or device.startswith('drill')):excluded[device]+=1;continue
  cruise=text(r['CRUISE_NAME']);platform=text(r['PLATFORM']);facility=text(r['FACILITY']);cid=ident('imlgs:campaign',facility,platform,cruise)
  # The facility DOI describes a repository, never the individual core dataset.
  source='https://www.ncei.noaa.gov/erddap/tabledap/IMLGS_Marine_Geology.html?latitude,longitude,CRUISE_NAME,SAMPLE,IMLGS&'+urlencode({'IMLGS':'"'+r['IMLGS']+'"'})
  records.append(dict(id='imlgs:'+r['IMLGS'],provider='NOAA IMLGS',source_id=r['IMLGS'],name=f"{cruise} / {r['SAMPLE']}",latitude=r['latitude'],longitude=r['longitude'],realm='lake' if text(r['LAKE']) else 'marine',archive_type=device,record_type='core',source_url=source,campaigns=[dict(id=cid,name=cruise,provider='NOAA IMLGS',platform=platform,facility=facility,source_locator=f'table.rows[{i-1}].CRUISE_NAME',source_native_id=cruise)] if cruise else [],proxies=[],source_locators=[dict(row=i,imlgs_id=r['IMLGS'])],metadata_status='sample_repository_metadata_not_numeric_review',raw_sha256=sha,license='https://www.ncei.noaa.gov/erddap/info/IMLGS_Marine_Geology/index.html',sample_name=r['SAMPLE'],IGSN=r['IGSN'],facility=facility,repository_url=r['URL_LINK'],repository_doi_url=r['DOI_LINK'],water_depth_m=r['WATER_DEPTH'],core_length_cm=r['CORED_LENGTH'],collection_date=r['BEGIN_DATE'],coordinate_basis='source latitude/longitude',query_url=query))
 return records,dict(provider='NOAA IMLGS',queried_rows=len(d['rows']),mapped_entries=len(records),excluded_devices=dict(excluded),source_url=query,source_sha256=sha,pagination='ERDDAP server-filtered distinct response; no row limit applied',snapshot='Source ERDDAP metadata date_created 2024-11-11; legacy viewer retired in 2025',limitations=['Includes adjacent Atlantic/Black Sea/Red Sea sites in the declared rectangle','Samples with same cruise/sample can be distinct devices/IGSNs; retained separately','Current physical sample availability requires curator confirmation'])

def wpa():
 from html.parser import HTMLParser
 from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
 class Table(HTMLParser):
  def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
  def handle_starttag(self,t,a):
   if t=='tr':self.row=[]
   if t in ('td','th') and self.row is not None:self.cell=[]
  def handle_data(self,d):
   if self.cell is not None:self.cell.append(d)
  def handle_endtag(self,t):
   if t in ('td','th') and self.cell is not None:self.row.append(''.join(self.cell).strip());self.cell=None
   if t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
 folder=ROOT/'data/interim/discovery_core_archives';path=folder/'wpa_2025_search.html';url=(folder/'wpa_2025_search_url.txt').read_text().strip();raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
 parser=Table();parser.feed(raw.decode('utf8'));rows=parser.rows
 if not rows or rows[0][1:]!=['Core','Species','Longitude','Latitude','Depth']:raise RuntimeError('WPA table schema changed')
 records=[]
 for index,r in enumerate(rows[1:],1):
  if len(r)!=6 or number(r[3]) is None or number(r[4]) is None:continue
  parts=urlsplit(url);params=dict(parse_qsl(parts.query,keep_blank_values=True));params['q_core_sp']=r[1];source=urlunsplit((parts.scheme,parts.netloc,parts.path,urlencode(params),''))
  records.append(dict(id=ident('wpa2025',r[1],r[2]),provider='WPA 2025.0',source_id=r[1],name=r[1],latitude=float(r[4]),longitude=float(r[3]),realm='marine',record_type='core',archive_type='sediment_core',source_url=source,campaigns=[],proxies=[],species_as_archived=r[2],water_depth_m=number(r[5]),source_locators=[dict(table_row=index,collection='WPA_2025.0',query_url=url)],raw_sha256=sha,metadata_status='source_web_table_metadata_not_numeric_review',license=None,coordinate_basis='source table latitude/longitude'))
 return records,dict(provider='WPA 2025.0',mapped_entries=len(records),queried_table_rows=len(rows)-1,source_url=url,source_sha256=sha,limitations=['Exactly the named public Raw Data search result and table, not asserted complete across all WPA views','Species is preserved; no proxy variable is inferred from an undocumented query code','No numerical series ingested; native campaigns and paper relationships require further review'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--site-dir',type=Path);a=ap.parse_args();records=[];coverage=[]
 for fun in (paleomed,imlgs,wpa):
  r,c=fun();records+=r;coverage.append(c)
 for folder in ('discovery_pangaea','discovery_continental'):
  path=ROOT/'data/interim'/folder/'inventory.json'
  if not path.exists():raise RuntimeError('Required discovery source missing: '+str(path))
  d=json.loads(path.read_text(encoding='utf8'));coverage.append(dict(provider=d['source'],**d['coverage']))
  records+=d['records']
  for ds in d.get('datasets',[]):
   point=ds['points'][0] if len(ds.get('points',[]))==1 else {}
   records.append(dict(id=ds['id'],provider='PANGAEA discovery',source_id=ds['dataset_doi'],name=ds['title'],latitude=point.get('latitude'),longitude=point.get('longitude'),realm='unknown',archive_type='dataset_reference',record_type='dataset',source_url=ds['source_url'],dataset_doi=ds['dataset_doi'],dataset_publication_year=ds['publication_year'],campaigns=[],proxies=[],source_locators=[dict(locator=ds['source_locator'])],metadata_status='dataset_metadata_not_a_core_identity',raw_sha256=ds['raw_sha256'],license=ds.get('rights'),coordinate_basis='dataset-level point; not a named core identity',point_count=len(ds.get('points',[]))))
 # Exact source IDs only. Similar names/coordinates across repositories are not identity proof.
 byid={}
 for r in records:
  r['campaigns']=r.get('campaigns') or []
  r.setdefault('record_type','core')
  if r['id'] in byid:
   old=byid[r['id']]
   if (old['latitude'],old['longitude'])!=(r['latitude'],r['longitude']):raise RuntimeError('Conflicting source ID coordinates')
   old['proxies']=sorted(set(old.get('proxies',[]))|set(r.get('proxies',[])))
   if 'dataset_ids' in r:old['dataset_ids']=sorted(set(old.get('dataset_ids',[]))|set(r['dataset_ids']))
   continue
  byid[r['id']]=r
 campaigns={}
 for r in byid.values():
  for c in r['campaigns']:campaigns[c['id']]=c
 seed=json.loads((ROOT/'data/processed/atlas-v1.json').read_text(encoding='utf8'))
 # Links are exact DOI+event/core name matches, not a geographic nearest-neighbour merge.
 for r in byid.values():
  for core in seed['records']:
   if r.get('dataset_doi')==core.get('dataset_doi') and key(r['name'])==key(core['name']):r['curated_record_id']=core['id']
 numeric=[row[0] for s in seed['series'] for row in s['rows'] if isinstance(row[0],(int,float))]
 extents=[r for r in byid.values() if number(r.get('age_max_ka_bp')) is not None]
 maxmeta=max(extents,key=lambda r:r['age_max_ka_bp']) if extents else None
 out=dict(version='atlas-inventory-2026-10-28-v2-r2',scope=dict(label='Mediterráneo y zonas adyacentes',bbox=[-10,28,42,48]),records=sorted(byid.values(),key=lambda r:r['id']),campaigns=list(campaigns.values()),coverage=coverage,counts=dict(entries=len(byid),georeferenced=sum(r.get('latitude') is not None for r in byid.values()),core_site_entries=sum(r['record_type']!='dataset' for r in byid.values()),dataset_references=sum(r['record_type']=='dataset' for r in byid.values()),campaigns=len(campaigns)),time_extent=dict(numeric_min=min(numeric),numeric_max=max(numeric),metadata_max=maxmeta['age_max_ka_bp'] if maxmeta else None,metadata_max_record=maxmeta['name'] if maxmeta else None,metadata_max_source=maxmeta['source_url'] if maxmeta else None),limitations=['Counts are source entries, not de-duplicated independent physical cores','No campaigns inferred from core prefixes','Metadata locations and reported proxy presence do not imply reviewed numeric data','Coverage is documented per query/snapshot, never universal completeness'])
 raw=json.dumps(out,ensure_ascii=False,separators=(',',':')).encode();target=ROOT/'data/processed/inventory-v2.json';target.write_bytes(raw)
 if a.site_dir:(a.site_dir/'data/inventory.json').write_bytes(raw)
 print(json.dumps(dict(counts=out['counts'],time_extent=out['time_extent'],bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
