"""Retrieve the four explicit public inventory resources with immutable local caching."""
from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
config=json.loads((ROOT/'config/discovery.json').read_text(encoding='utf8'));manifest=[]
for source in config['resources']:
 path=ROOT/source['path'];path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():raw=path.read_bytes();status='existing_cache'
 else:
  with urlopen(Request(source['url'],headers={'User-Agent':'MediterraneanMultiproxyAtlas/0.3'}),timeout=90) as response:raw=response.read(64*1024*1024+1)
  if len(raw)>64*1024*1024:raise RuntimeError('Resource exceeds declared bound')
  path.write_bytes(raw);status='retrieved'
 manifest.append({**source,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'status':status})
# These are saved source URLs, not generated identifiers.
(ROOT/'data/interim/discovery_core_archives/imlgs_probe_url.txt').write_text(config['resources'][2]['url'],encoding='utf8')
(ROOT/'data/interim/discovery_core_archives/wpa_2025_search_url.txt').write_text(config['resources'][3]['url'],encoding='utf8')
(ROOT/'data/interim/discovery_retrieval_manifest.json').write_text(json.dumps({'run_at_utc':datetime.now(timezone.utc).isoformat(),'resources':manifest},indent=2)+'\n',encoding='utf8')
print('Inventory resources ready; cached bytes were not replaced.')
