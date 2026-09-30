"""Provenance definitions, field assertions, and export sanitization.
Complies with docs/18_DATA_PROVENANCE.md and docs/06_SCHEMA.md.
"""

from __future__ import annotations
import enum
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OriginClass(str, enum.Enum):
    OFFICIAL = "OFFICIAL"
    EXTERNAL_PUBLIC = "EXTERNAL_PUBLIC"
    PLATFORM_GENERATED = "PLATFORM_GENERATED"
    SYNTHETIC = "SYNTHETIC"


class SourceKind(str, enum.Enum):
    REGULATOR_LIST = "REGULATOR_LIST"
    GOVERNMENT_PUBLICATION = "GOVERNMENT_PUBLICATION"
    PUBLIC_MARKET_QUOTE = "PUBLIC_MARKET_QUOTE"
    SECONDARY_STUDY = "SECONDARY_STUDY"
    PLATFORM_OBSERVATION = "PLATFORM_OBSERVATION"
    USER_SELF_DECLARED = "USER_SELF_DECLARED"
    VERIFIED_TRANSACTION = "VERIFIED_TRANSACTION"
    LICENSED_IMAGE_DATASET = "LICENSED_IMAGE_DATASET"
    SYNTHETIC_GENERATOR = "SYNTHETIC_GENERATOR"


class ReviewStatus(str, enum.Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"


class LocationQuality(str, enum.Enum):
    GPS_PRECISE = "GPS_PRECISE"
    MANUAL_PIN = "MANUAL_PIN"
    COARSE_DISTRICT = "COARSE_DISTRICT"
    GEOCODED_ROOFTOP = "GEOCODED_ROOFTOP"
    GEOCODED_APPROXIMATE = "GEOCODED_APPROXIMATE"
    UNKNOWN = "UNKNOWN"


def sanitize_csv_cell(value: Any) -> Any:
    """Neutralize spreadsheet formula injection for text exports.
    Prepends a single quote `'` if text starts with dangerous formula triggers (=, +, -, @, \\t, \\r).
    Maintains unmodified values for numbers, booleans, and safe text.
    """
    if not isinstance(value, str):
        return value
    if value and value[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{value}"
    return value


class DataSource(BaseModel):
    """Metadata describing a published source or platform generator."""
    source_id: str
    publisher: str
    title: str
    url: Optional[str] = None
    publication_date: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_kind: SourceKind
    license: Optional[str] = None
    license_url: Optional[str] = None
    sha256: Optional[str] = None
    local_snapshot: Optional[str] = None
    locator: Optional[str] = None
    review_status: ReviewStatus = ReviewStatus.PENDING_REVIEW

    @classmethod
    def compute_file_sha256(cls, filepath_or_bytes: str | bytes) -> str:
        """Calculate SHA-256 for a raw document snapshot."""
        h = hashlib.sha256()
        if isinstance(filepath_or_bytes, bytes):
            h.update(filepath_or_bytes)
        else:
            with open(filepath_or_bytes, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
        return h.hexdigest()


class FieldAssertion(BaseModel):
    """Field-level lineage tracking claim origin, transformation, and review status."""
    id: Optional[str] = None
    entity_type: str
    entity_id: str
    field_name: str
    assertion_value: Any
    source_id: str
    locator: Optional[str] = None
    transformation_version: str = "v1.0"
    reviewer: Optional[str] = None
    asserted_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    validation_status: ReviewStatus = ReviewStatus.PENDING_REVIEW
