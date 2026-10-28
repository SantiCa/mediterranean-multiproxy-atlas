"""Reader for local LiPD (.lpd) exchange packages; does not rewrite source files."""

import json
import hashlib
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from .base import ConnectorError


class LiPDArchive:
    """Inspect package metadata and member names without extraction or conversion.

    This does not validate BagIt manifests, chronology, ontology or table mappings.
    """
    source = "lipd"

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def inspect(self) -> dict:
        if self.path.suffix.lower() != ".lpd":
            raise ConnectorError(f"LiPD archive must use .lpd extension: {self.path}")
        try:
            with ZipFile(self.path) as archive:
                names = archive.namelist()
                candidates = [name for name in names if name.endswith("metadata.jsonld")]
                if len(candidates) != 1:
                    raise ConnectorError("Expected exactly one metadata.jsonld in LiPD archive")
                metadata_name = candidates[0]
                metadata = json.loads(archive.read(metadata_name).decode("utf-8"))
                if not isinstance(metadata, dict):
                    raise ConnectorError("LiPD metadata must be a JSON object")
        except (OSError, BadZipFile, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ConnectorError(f"Invalid LiPD archive: {self.path}") from exc
        return {"path": str(self.path), "metadata_path": metadata_name, "metadata": metadata,
                "table_paths": [name for name in names if name.lower().endswith(".csv")],
                "archive_sha256": hashlib.sha256(self.path.read_bytes()).hexdigest()}
