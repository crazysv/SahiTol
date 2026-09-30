"""SahiTol data import, cleaning, provenance, validation, and synthetic generation tools.
Implements T005, R-DATA-08, R-DATA-09, R-DATA-10 under docs/18_DATA_PROVENANCE.md.
"""

from .provenance import (
    OriginClass,
    SourceKind,
    ReviewStatus,
    LocationQuality,
    sanitize_csv_cell,
    FieldAssertion,
    DataSource,
)
from .staging import (
    normalize_text,
    normalize_phone,
    convert_to_paise,
    convert_to_grams,
    load_records,
)
from .validation import (
    ValidationResult,
    QuarantineRecord,
    DataValidator,
)
from .deduplication import (
    Deduplicator,
    DuplicateReport,
)
from .geocoding import (
    CachedGeocoder,
    GeocodeResult,
)
from .synthetic import (
    SyntheticGenerator,
    EdgeScenario,
)
from .manifest import (
    DatasetManifest,
    generate_manifest,
)

__all__ = [
    "OriginClass",
    "SourceKind",
    "ReviewStatus",
    "LocationQuality",
    "sanitize_csv_cell",
    "FieldAssertion",
    "DataSource",
    "normalize_text",
    "normalize_phone",
    "convert_to_paise",
    "convert_to_grams",
    "load_records",
    "ValidationResult",
    "QuarantineRecord",
    "DataValidator",
    "Deduplicator",
    "DuplicateReport",
    "CachedGeocoder",
    "GeocodeResult",
    "SyntheticGenerator",
    "EdgeScenario",
    "DatasetManifest",
    "generate_manifest",
]
