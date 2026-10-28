"""Shared polite HTTP behavior and immutable raw-response capture."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from medatlas.models import RetrievedArtifact


class ConnectorError(RuntimeError):
    pass


class HTTPConnector:
    source = "unknown"
    user_agent = "medatlas/0.2 (research data discovery; contact: project maintainers)"

    def get(self, url: str, *, accept: str = "application/json", timeout: int = 45) -> RetrievedArtifact:
        request = Request(url, headers={"Accept": accept, "User-Agent": self.user_agent})
        try:
            with urlopen(request, timeout=timeout) as response:
                body = response.read()
                return RetrievedArtifact(
                    source=self.source,
                    request_url=url,
                    resolved_url=response.geturl(),
                    accessed_at_utc=datetime.now(timezone.utc),
                    content_type=response.headers.get("Content-Type"),
                    sha256=hashlib.sha256(body).hexdigest(),
                    body=body,
                )
        except (HTTPError, URLError, TimeoutError) as exc:
            raise ConnectorError(f"{self.source} request failed: {url}: {exc}") from exc

    def get_json(self, url: str) -> tuple[dict | list, RetrievedArtifact]:
        artifact = self.get(url)
        try:
            return json.loads(artifact.body.decode("utf-8-sig")), artifact
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ConnectorError(f"{self.source} returned invalid JSON: {artifact.resolved_url}") from exc


def preserve_raw(artifact: RetrievedArtifact, root: Path, extension: str) -> Path:
    """Write content-addressed source bytes; never replace a different payload."""
    target = root / "data" / "raw" / artifact.source / f"{artifact.sha256}.{extension.lstrip('.')}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != artifact.sha256:
        raise ConnectorError(f"Content-addressed raw file changed unexpectedly: {target}")
    if not target.exists():
        target.write_bytes(artifact.body)

    manifest_path = root / "data" / "provenance" / f"{artifact.source}_retrievals.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    entries = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    item = {
        "path": target.relative_to(root).as_posix(),
        "source": artifact.source,
        "request_url": artifact.request_url,
        "resolved_url": artifact.resolved_url,
        "accessed_at_utc": artifact.accessed_at_utc.isoformat(),
        "content_type": artifact.content_type,
        "sha256": artifact.sha256,
        "bytes": len(artifact.body),
    }
    if not any(entry.get("sha256") == artifact.sha256 and entry.get("request_url") == artifact.request_url for entry in entries):
        entries.append(item)
        temporary = manifest_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(manifest_path)
    return target
