"""Shared polite HTTP behavior and immutable raw-response capture."""

from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from medatlas.models import RetrievedArtifact


class ConnectorError(RuntimeError):
    pass


class HTTPConnector:
    source = "unknown"
    user_agent = "medatlas/0.2 (research data discovery; contact: project maintainers)"

    def get(self, url: str, *, accept: str | None = "application/json", timeout: int = 45,
            max_bytes: int = 64 * 1024 * 1024) -> RetrievedArtifact:
        if max_bytes <= 0:
            raise ValueError("max_bytes must be positive")
        headers = {"User-Agent": self.user_agent}
        if accept is not None:
            headers["Accept"] = accept
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=timeout) as response:
                # Bound provider responses; large datasets need an explicit limit.
                body = response.read(max_bytes + 1)
                if len(body) > max_bytes:
                    raise ConnectorError(f"{self.source} response exceeds {max_bytes} bytes")
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
            payload = json.loads(artifact.body.decode("utf-8-sig"))
            if not isinstance(payload, (dict, list)):
                raise ConnectorError(f"{self.source} JSON must contain an object or array")
            return payload, artifact
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ConnectorError(f"{self.source} returned invalid JSON: {artifact.resolved_url}") from exc


def preserve_raw(artifact: RetrievedArtifact, root: Path, extension: str) -> Path:
    """Write content-addressed source bytes; never replace a different payload."""
    extension = extension.lstrip(".")
    if not re.fullmatch(r"[a-z0-9_-]+", artifact.source) or not re.fullmatch(r"[a-z0-9]+", extension):
        raise ConnectorError("Invalid source identifier or file extension")
    if hashlib.sha256(artifact.body).hexdigest() != artifact.sha256:
        raise ConnectorError("Artifact checksum does not match its body")
    root = Path(root).resolve()
    target = root / "data" / "raw" / artifact.source / f"{artifact.sha256}.{extension.lstrip('.')}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != artifact.sha256:
        raise ConnectorError(f"Content-addressed raw file changed unexpectedly: {target}")
    if not target.exists():
        target.write_bytes(artifact.body)

    manifest_path = root / "data" / "provenance" / f"{artifact.source}_retrievals.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
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
    # A per-provider lock prevents concurrent agents from losing manifest entries.
    # Contention fails explicitly; callers retry after the other writer completes.
    lock = manifest_path.with_suffix(".lock")
    try:
        with lock.open("x", encoding="utf-8"):
            pass
    except FileExistsError as exc:
        raise ConnectorError(f"Manifest busy: {manifest_path}") from exc
    try:
        entries = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
        if not any(entry.get("sha256") == artifact.sha256 and entry.get("request_url") == artifact.request_url for entry in entries):
            entries.append(item)
            temporary = manifest_path.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(manifest_path)
    finally:
        lock.unlink()
    return target
