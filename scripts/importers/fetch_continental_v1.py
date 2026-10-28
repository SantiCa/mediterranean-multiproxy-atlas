"""Download the two named NOAA studies and their three explicitly selected tables."""
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from medatlas.connectors import NOAAWDSConnector

DEST=ROOT/'data/interim/v1_continental'
FILES={'soreq_2003-noaa.txt','peqiin_2003-noaa.txt','sofular2009-noaa.txt'}

def preserve(path,raw):
    if path.exists() and path.read_bytes()!=raw:
        raise RuntimeError(f'Source changed: preserve and curate a new version instead of replacing {path}')
    path.write_bytes(raw)

if __name__=='__main__':
    DEST.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for study_id in (5423,8637):
        payload,response=NOAAWDSConnector().search_studies(NOAAStudyId=study_id)
        preserve(DEST/f'noaa_{study_id}.json',response.body)
        for study in payload['study']:
            for site in study['site']:
                for table in site.get('paleoData',[]):
                    for file in table.get('dataFile',[]):
                        url=file['fileUrl'];name=url.rsplit('/',1)[-1]
                        if name not in FILES:continue
                        if not url.startswith('https://www.ncei.noaa.gov/pub/data/paleo/'):
                            raise RuntimeError('Unexpected provider URL; manual review required')
                        with urlopen(Request(url,headers={'User-Agent':'medatlas/0.2'}),timeout=45) as r:raw=r.read()
                        preserve(DEST/name,raw)
                        manifest.append(dict(url=url,path=name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
    (DEST/'retrieval_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(f'Retrieved {len(manifest)} source tables. Run curate_continental_v1.py next.')
