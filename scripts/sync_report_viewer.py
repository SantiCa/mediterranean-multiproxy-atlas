"""Update optional viewer source data. Rebuild its HTML with the viewer runtime."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sync_source(root: Path = ROOT) -> Path:
    source_path = root / "report-app/src/data.json"
    if not source_path.is_file():
        raise RuntimeError("Optional report-app is not distributed with the Git project")
    snapshot = json.loads((root / "reports/reviewed_snapshot.json").read_text(encoding="utf-8"))
    previous = json.loads(source_path.read_text(encoding="utf-8"))
    snapshot["id"] = previous["id"]
    snapshot.pop("buildStatus", None)
    source_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Compiled HTML embeds its snapshot path. Editing a dist manifest alone leaves
    # stale content visible, so only the supported full build may regenerate dist.
    return source_path


if __name__ == "__main__":
    print(f"Updated {sync_source()}. Rebuild the optional viewer before previewing.")
