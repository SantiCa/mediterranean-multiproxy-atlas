"""Explicit, bounded public-provider checks; excluded from the offline test suite."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from medatlas.connectors import DataCiteConnector, NeotomaConnector, NOAAWDSConnector, PANGAEAConnector


def check(source, operation):
    try:
        result = operation()
        payload, response = result if isinstance(result, tuple) else (None, result)
        return dict(source=source, status="retrieved", request_url=response.request_url,
                    resolved_url=response.resolved_url, accessed_at_utc=response.accessed_at_utc.isoformat(),
                    sha256=response.sha256, bytes=len(response.body), content_type=response.content_type,
                    top_level_keys=list(payload) if isinstance(payload, dict) else None)
    except Exception as exc:
        return dict(source=source, status="failed", error=f"{type(exc).__name__}: {exc}")


def main():
    operations = [
        ("pangaea", lambda: PANGAEAConnector().dataset_table("10.1594/PANGAEA.438816")),
        ("noaa_wds_paleo", lambda: NOAAWDSConnector().search_studies(dataPublisher="NOAA", headersOnly=True, limit=1)),
        ("neotoma", lambda: NeotomaConnector().search_sites(sitename="Marion Lake")),
        ("datacite", lambda: DataCiteConnector().fetch_doi("10.1594/PANGAEA.438816")),
    ]
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda item: check(*item), operations))
    report = dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),
                  scope="One bounded request per provider; retrieval only, not scientific or full schema validation",
                  results=results)
    path = ROOT / "reports/live_source_check.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int(any(item["status"] != "retrieved" for item in results))


if __name__ == "__main__":
    raise SystemExit(main())
