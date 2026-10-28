"""Export tracked project files; ignored local material never enters the archive."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def package_project(root: Path, target: Path) -> dict:
    root = root.resolve()
    # Match Git's explicit publication boundary, rather than walking the workspace.
    listing = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    files = [root / name.decode("utf-8") for name in listing.split(b"\0") if name]
    missing = [str(path) for path in files if not path.is_file() or path.is_symlink()]
    if missing:
        raise RuntimeError(f"Tracked files missing or symbolic links: {missing}")
    target.parent.mkdir(parents=True, exist_ok=True)
    members = []
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            raw = path.read_bytes()
            relative = path.relative_to(root).as_posix()
            archive.writestr(relative, raw)
            members.append(dict(path=relative, sha256=hashlib.sha256(raw).hexdigest()))
        archive.writestr("DELIVERY_MANIFEST.json", json.dumps(members, indent=2))
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Archive CRC verification failed")
        for entry in members:
            if hashlib.sha256(archive.read(entry["path"])).hexdigest() != entry["sha256"]:
                raise RuntimeError(f"Archive hash mismatch: {entry['path']}")
    return dict(path=str(target), members=len(members), bytes=target.stat().st_size,
                sha256=hashlib.sha256(target.read_bytes()).hexdigest())


if __name__ == "__main__":
    print(json.dumps(package_project(ROOT, ROOT.parent / "outputs" / "medatlas-source.zip"), indent=2))
