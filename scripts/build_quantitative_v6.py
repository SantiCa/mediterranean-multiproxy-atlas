"""Append the priority coverage fragment to immutable v5 using its admission gate."""
import hashlib
import json
from pathlib import Path
import build_quantitative_v5 as admission

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    seed, report = admission.assemble(
        baseline=ROOT/'data/processed/atlas-v5.json',
        fragment_paths=[ROOT/'data/interim/priority_v6/pangaea_curated.json'],
        version_prefix='atlas-quantitative-2026-10-30-v6-')
    raw = json.dumps(seed, ensure_ascii=False, separators=(',', ':')).encode()
    (ROOT/'data/processed/atlas-v6.json').write_bytes(raw)
    report.update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    (ROOT/'reports/quantitative_v6_release.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps({k:report[k] for k in ('version','counts','comparison_groups','sha256')}))
