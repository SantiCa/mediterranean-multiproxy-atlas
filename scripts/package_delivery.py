"""Create a local handoff archive with source report and reviewed evidence."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "outputs"
OUT.mkdir(exist_ok=True)
target = OUT / "Mediterranean_Multiproxy_Atlas_viabilidad_2026-10-28.zip"
members = []
with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, strict_timestamps=False) as archive:
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in {"__pycache__", ".git", "node_modules", ".data-app-offline"} for part in rel.parts):
            continue
        # The installed Node/NPM build toolchain is unavailable here; exclude the
        # older compiled preview so this package cannot present stale report text.
        if rel.parts[:2] == ("report-app", "dist"):
            continue
        archive.write(path, rel.as_posix())
        members.append(dict(path=rel.as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    archive.writestr("DELIVERY_MANIFEST.json", json.dumps(members, indent=2))
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
    for entry in members:
        assert hashlib.sha256(archive.read(entry["path"])).hexdigest() == entry["sha256"]
print(json.dumps(dict(path=str(target), members=len(members), bytes=target.stat().st_size, sha256=hashlib.sha256(target.read_bytes()).hexdigest()), indent=2))
