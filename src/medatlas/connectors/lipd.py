"""Reader for local LiPD (.lpd) exchange packages; does not rewrite source files."""

import json
import hashlib
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from .base import ConnectorError


class LiPDArchive:
    source = "lipd"

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def inspect(self) -> dict:
        if self.path.suffix.lower() != ".lpd":
            raise ConnectorError(f"LiPD archive must use .lpd extension: {self.path}")
        try:
            with ZipFile(self.path) as archive:
                names = archive.namelist()
                metadata_name = next((name for name in names if name.endswith("metadata.jsonld")), None)
                if metadata_name is None:
                    raise ConnectorError("LiPD archive has no metadata.jsonld")
                metadata = json.loads(archive.read(metadata_name).decode("utf-8"))
        except (BadZipFile, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ConnectorError(f"Invalid LiPD archive: {self.path}") from exc
        return {"path": str(self.path), "metadata_path": metadata_name, "metadata": metadata,
                "table_paths": [name for name in names if name.lower().endswith(".csv")],
                "archive_sha256": hashlib.sha256(self.path.read_bytes()).hexdigest()}
