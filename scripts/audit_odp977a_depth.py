"""Reproduce CUR-ODP977A evidence, without altering any data or age/depth value.

Optional PDF extraction dependency: pypdf. HTTP uses the project's immutable
content-addressed source capture. Download only with --fetch; otherwise offline.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from medatlas.connectors.base import HTTPConnector,preserve_raw

RESOURCES={
"accepted_manuscript":{"url":"https://ricerca.uniba.it/retrieve/28f431ac-919a-4bd9-ab13-86998b1abe1e/Gonza%CC%81lez-Lanchas%20et%20al.%2C%202020_QSR_preprint.pdf","extension":"pdf"},
"odp_initial_report":{"url":"https://www-odp.tamu.edu/publications/161_IR/VOLUME/CHAPTERS/ir161_07.pdf","extension":"pdf"},
"odp_preliminary_report":{"url":"https://www-odp.tamu.edu/publications/prelim/161_Prelim/OP977.HTML","extension":"html"},
"pangaea_current_table":{"url":"https://doi.pangaea.de/10.1594/PANGAEA.921230?format=textfile","extension":"tsv"},
}

def normalized(text):
    """Normalize ligatures/whitespace only for locating a source statement."""
    return re.sub(r"\s+"," ",unicodedata.normalize("NFKC",text))

def acquire(resource,fetch):
    """Retrieve or reuse one exact official source with an immutable manifest."""
    manifest=ROOT/'data/provenance/odp977a_audit_retrievals.json'
    previous=json.loads(manifest.read_text(encoding='utf8')) if manifest.exists() else []
    for item in previous:
        if item['request_url']==resource['url']:
            path=ROOT/item['path']
            if path.exists():
                if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Changed cached source')
                return path,item
    if not fetch:raise FileNotFoundError('Original absent; rerun with --fetch')
    client=HTTPConnector();client.source='odp977a_audit'
    artifact=client.get(resource['url'],accept=None,timeout=45,max_bytes=20*1024*1024)
    if resource['extension']=='pdf' and not artifact.body.startswith(b'%PDF'):raise ValueError('Expected PDF, no access bypass attempted')
    path=preserve_raw(artifact,ROOT,resource['extension'])
    item=next(x for x in json.loads(manifest.read_text(encoding='utf8')) if x['sha256']==artifact.sha256 and x['request_url']==artifact.request_url)
    return path,item

def audit(fetch=False):
    """Return source evidence and numerical-range checks, not a new depth model."""
    originals={};sources={};failures={}
    for name,resource in RESOURCES.items():
        try:
            path,item=acquire(resource,fetch);originals[name]=path;sources[name]=item
            print(name+': cached/verified',flush=True)
        except Exception as exc:
            failures[name]=type(exc).__name__+': '+str(exc)
            print(name+': unavailable',flush=True)
    cached=ROOT/'data/raw/pangaea/921230.tsv'
    text=cached.read_text(encoding='utf-8-sig')
    rows=list(csv.DictReader(io.StringIO(text.split('*/',1)[1].lstrip()),delimiter='\t'))
    depths=[float(r['Depth corr [m]']) for r in rows];ages=[float(r['Age [ka BP]']) for r in rows]
    assert 'COMMENT: [cmbsf]' in text
    pdf_evidence={}
    try:
        from pypdf import PdfReader
        if 'accepted_manuscript' in originals:
            reader=PdfReader(originals['accepted_manuscript'])
            locations=[]
            for page_no,page in enumerate(reader.pages,1):
                flat=normalized(page.extract_text() or '')
                if re.search(r'cmbsf\s*:?\s*corrected meters below sea\s*floor',flat,re.I):
                    locations.append(page_no)
            if not locations:raise ValueError('Exact primary definition not found in PDF')
            pdf_evidence['accepted_manuscript']={'pdf_pages_1_based':locations,'locator':'Table1 caption; definition of cmbsf','definition':'corrected meters below seafloor'}
        if 'odp_initial_report' in originals:
            reader=PdfReader(originals['odp_initial_report'])
            locations=[]
            for page_no,page in enumerate(reader.pages,1):
                flat=normalized(page.extract_text() or '')
                if ('1984' in flat or '1,984' in flat) and '977' in flat:locations.append(page_no)
            pdf_evidence['odp_initial_report']={'pdf_pages_1_based_water_depth_context':locations,'scope':'Shipboard mbsl/mbsf/mbrf context, not the later corrected-depth transform'}
    except Exception as exc:failures['pdf_extraction']=type(exc).__name__+': '+str(exc)
    source_unchanged=None
    if 'pangaea_current_table' in originals:
        source_unchanged=originals['pangaea_current_table'].read_bytes()==cached.read_bytes()
    result={'audit_id':'CUR-ODP977A','dataset_doi':'10.1594/PANGAEA.921230',
      'finding':'cmbsf explicitly means corrected meters below seafloor in the source article; no factor100 conversion',
      'status':'unit_resolved_from_primary_article; corrected-frame join still requires correspondence',
      'reviewed_assertion':json.loads((ROOT/'config/curation_assertions.json').read_text(encoding='utf8'))['assertions'][0],
      'native_column':'Depth corr [m]','native_comment':'[cmbsf]','unit_interpretation':'m',
      'depth_frame':'corrected meters below seafloor, author-defined',
      'numerical_transform':'none','automatic_join_to_shipboard_mbsf':'not_permitted_without_correspondence',
      'native_sha256':hashlib.sha256(cached.read_bytes()).hexdigest(),'native_sample_rows':len(rows),
      'native_depth_range':[min(depths),max(depths)],'archived_age_range_ka_bp':[min(ages),max(ages)],
      'current_tsv_identical_to_preserved_tsv':source_unchanged,
      'sources':sources,'pdf_evidence':pdf_evidence,'failures':failures,
      'chronology_caution':'Published SST correlation with U1313; no independent synchrony validation',
      'versioned_seeds_or_observations_changed':False}
    target=ROOT/'reports/odp977a_depth_audit.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ('status','native_sample_rows','native_depth_range','current_tsv_identical_to_preserved_tsv','pdf_evidence','failures')},ensure_ascii=True))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--fetch',action='store_true')
    audit(parser.parse_args().fetch)
