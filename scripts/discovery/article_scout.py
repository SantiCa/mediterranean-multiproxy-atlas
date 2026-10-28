"""Scout named primary articles and public supplementary spreadsheets without access bypass."""
import json,hashlib,re,urllib.request,urllib.parse,zipfile,xml.etree.ElementTree as E
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'data/interim/article_scout';DEST.mkdir(parents=True,exist_ok=True)
PAPERS=[
 ('10.1038/s41467-024-45123-3','https://www.nature.com/articles/s41467-024-45123-3','continental','Lake Bourget: lake sediment and source-to-sink geochemistry'),
 ('10.1038/s41467-024-53781-6','https://www.nature.com/articles/s41467-024-53781-6','marine','Aphrodite2 and DSDP halite/chlorine isotope measurements; depth is not a sample age'),
 ('10.1016/j.palaeo.2024.112427','https://digibug.ugr.es/handle/10481/109754','marine','GP03PC; institutional author version and data availability need review'),
 ('10.1016/j.heliyon.2021.e07880','https://doi.org/10.1016/j.heliyon.2021.e07880','marine','Alboran living benthic foraminifera: surface ecological reference, not automatically a paleo time series'),
 ('10.1038/s43247-023-00947-7','https://www.nature.com/articles/s43247-023-00947-7','marine','Already linked by the article to PANGAEA.955024: possible duplicate, not a new independent dataset'),
]
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='a' and d.get('href'):self.urls.append(d['href'])
def fetch(url,path):
 if path.exists():return path.read_bytes()
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MediterraneanMultiproxyAtlas/0.3'}),timeout=45) as response:
  raw=response.read(10_000_001)
  if len(raw)>10_000_000:raise RuntimeError('Resource exceeds bounded 10 MB scouting limit')
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);return raw
records=[]
for doi,url,realm,note in PAPERS:
 rid=doi.rsplit('/',1)[-1];record=dict(doi=doi,primary_url=url,realm=realm,notes=note,review_state='pending_curator_review',supplements=[])
 try:
  cr=json.loads(fetch('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''),DEST/(rid+'-crossref.json')))['message']
  record.update(title=cr.get('title',[''])[0],publication_year=(cr.get('published',{}).get('date-parts') or [[None]])[0][0],source_links=cr.get('link',[]))
  raw=fetch(url,DEST/(rid+'.html'));html=raw.decode('utf8',errors='replace');record['html_sha256']=hashlib.sha256(raw).hexdigest()
  if any(token in html.lower() for token in ('client challenge','captcha','<title>redirecting')) and len(html)<100000:record['access_status']='challenge page; not bypassed';records.append(record);continue
  parser=Links();parser.feed(html);files=sorted({urllib.parse.urljoin(url,h) for h in parser.urls if '.xlsx' in h.lower() or '.csv' in h.lower()})
  for index,fileurl in enumerate(files[:8]):
   if not fileurl.startswith('https://'):continue
   f=dict(url=fileurl,status='linked')
   try:
    data=fetch(fileurl,DEST/(rid+f'-supplement-{index}.xlsx'));f.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),status='downloaded_for_review')
    if data[:2]==b'PK':
     import io
     z=zipfile.ZipFile(io.BytesIO(data));n={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
     f['sheets']=[s.get('name') for s in E.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',n)]
   except Exception as e:f['status']='retrieval_failed';f['error']=str(e)
   record['supplements'].append(f)
  record['access_status']='primary_page_retrieved';record['not_in_database_claim']='Not established: absence from every repository cannot be inferred from article availability'
 except Exception as e:record['access_status']='retrieval_failed';record['error']=str(e)
 records.append(record);print(doi,record['access_status'],'supplements',len(record['supplements']),flush=True)
out=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),scope='Initial named-article scout, not a systematic literature review',records=records,policy='Public publisher/author-repository pages only; no paywall or CAPTCHA bypass; no article values ingested without curation')
(ROOT/'reports/article_scout_2026-10-28.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

# Supplement names and converted contents come from the documented NCBI BioC API.
# The conversion is a scouting artifact, not an exact native-cell numeric import.
pmcs={'10.1038/s41467-024-45123-3':'PMC10858959','10.1038/s41467-024-53781-6':'PMC11573988','10.1016/j.heliyon.2021.e07880':'PMC8417336'}
for record in records:
 pmc=pmcs.get(record['doi'])
 if not pmc:continue
 try:
  url='https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/supplmat.cgi/bioc_json/'+pmc+'/list'
  items=json.loads(fetch(url,DEST/(pmc+'-supplement-list.json')))
  for item in items:
   if not item['original_file'].endswith('.xlsx'):continue
   raw=fetch(item['bioc_file'],DEST/(pmc+'-converted-'+item['num']+'.json'))
   record['supplements'].append(dict(original_url=item['original_file'],bioC_url=item['bioc_file'],converted_bytes=len(raw),converted_sha256=hashlib.sha256(raw).hexdigest(),status='converted_content_retrieved_pending_native_structure_and_license_review'))
 except Exception as e:record['supplement_api_error']=str(e)
pdf=DEST/'GP03PC-author-preprint.pdf'
for record in records:
 if record['doi']=='10.1016/j.palaeo.2024.112427' and pdf.exists():record['author_pdf']=dict(status='public_author_version_downloaded',bytes=pdf.stat().st_size,sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),source='Institutional landing-page bitstream; not a publisher-final-version assertion')
out['records']=records
(ROOT/'reports/article_scout_2026-10-28.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
