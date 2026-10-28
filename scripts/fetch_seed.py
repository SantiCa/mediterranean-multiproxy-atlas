"""Download a small, explicit PANGAEA evidence seed. No crawling or inferred data.

Raw bytes are immutable by default; --refresh refuses changed content rather than
silently replacing it. Internet access is required only for absent files.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
IDS = (438816, 901666, 759535, 898587, 921230)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "MediterraneanMultiproxyAtlas-feasibility/0.1"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read(), response.geturl(), response.headers.get("Content-Type")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    raw = ROOT / "data" / "raw" / "pangaea"
    raw.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / "data" / "provenance" / "downloads.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    records = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    by_path = {record["path"]: record for record in records}
    for dataset in IDS:
        for suffix, query in (("tsv", "?format=textfile"), ("html", "")):
            url = f"https://doi.pangaea.de/10.1594/PANGAEA.{dataset}{query}"
            target = raw / f"{dataset}.{suffix}"
            relative = target.relative_to(ROOT).as_posix()
            if target.exists() and not args.refresh:
                if relative not in by_path:
                    raise RuntimeError(f"Unmanifested existing raw file: {target}")
                data = target.read_bytes()
                if hashlib.sha256(data).hexdigest() != by_path[relative]["sha256"]:
                    raise RuntimeError(f"Raw integrity mismatch: {target}")
                continue
            data, resolved, content_type = fetch(url)
            if suffix == "tsv" and (b"/* DATA DESCRIPTION:" not in data or b"*/" not in data):
                raise RuntimeError(f"Not a PANGAEA text table: {url}")
            sha = hashlib.sha256(data).hexdigest()
            if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != sha:
                raise RuntimeError(f"Source changed; preserve old release and curate a new version: {url}")
            target.write_bytes(data)
            by_path[relative] = dict(path=relative, doi=f"10.1594/PANGAEA.{dataset}", requested_url=url,
                                     resolved_url=resolved, content_type=content_type, sha256=sha,
                                     accessed_at_utc=datetime.now(timezone.utc).isoformat(), bytes=len(data))
            manifest_path.write_text(json.dumps(list(by_path.values()), ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Saved {relative}: {len(data)} bytes")
    print(f"Verified {len(by_path)} source objects")


if __name__ == "__main__":
    main()
