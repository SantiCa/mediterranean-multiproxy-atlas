"""Sync reviewed Markdown/data into the editable report and its static data snapshot.

Run build_report_snapshot.py first. The static HTML shell is unchanged; Vite should
still be run when source code or styling changes.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
app = ROOT / "report-app"
dist = app / "dist"
snapshot = json.loads((ROOT / "reports/reviewed_snapshot.json").read_text(encoding="utf-8"))

# Preserve the stable identity of the existing report app.
source_path = app / "src/data.json"
previous = json.loads(source_path.read_text(encoding="utf-8"))
snapshot["id"] = previous["id"]
snapshot.pop("buildStatus", None)  # clear the old paused state after this revision is complete
source_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Update the separate-data artifact consumed by the existing static HTML shell.
old_manifest = json.loads((dist / "data-app-build.json").read_text(encoding="utf-8"))
raw = (ROOT / "reports/reviewed_snapshot.json").read_bytes()
digest = hashlib.sha256(raw).hexdigest()
filename = f"snapshot.{digest}.json"
(dist / filename).write_bytes(raw)
manifest = dict(old_manifest)
manifest["snapshot"] = dict(path=filename, sha256=digest, bytes=len(raw))
manifest["sourceSnapshotSha256"] = digest
(dist / "data-app-build.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

print(json.dumps(dict(source=str(source_path), snapshot=str(dist / filename), sha256=digest), indent=2))
