"""Small, source-neutral domain records; original source payloads stay intact."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Realm = Literal["marine", "terrestrial", "lacustrine", "fluvial", "speleothem", "ice", "other"]


@dataclass(frozen=True)
class Site:
    site_key: str
    name_original: str
    realm: Realm
    latitude: float | None
    longitude: float | None
    elevation_m: float | None
    water_depth_m: float | None
    vertical_reference_original: str | None
    spatial_uncertainty_m: float | None
    source_id: str


@dataclass(frozen=True)
class Dataset:
    source_id: str
    title_original: str
    dataset_url: str
    doi: str | None
    publication_year: int | None
    record_year: int | None
    license_original: str | None
    realm: Realm | None


@dataclass(frozen=True)
class Observation:
    """A value or category as provided by a source or an explicit derivation."""

    observation_id: str
    dataset_id: str
    site_key: str | None
    sample_key: str | None
    variable_original: str
    value_original: str
    unit_original: str | None
    depth_value_original: str | None
    depth_unit_original: str | None
    age_value_original: str | None
    age_unit_original: str | None
    time_scale_original: str | None
    age_model_id: str | None
    publication_year: int | None
    source_locator: str
    source_payload_sha256: str
    transformation_id: str | None = None


@dataclass(frozen=True)
class RetrievedArtifact:
    source: str
    request_url: str
    resolved_url: str
    accessed_at_utc: datetime
    content_type: str | None
    sha256: str
    body: bytes
