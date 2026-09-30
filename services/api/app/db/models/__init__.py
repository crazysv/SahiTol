"""SQLAlchemy ORM models export for SahiTol.
Registers all 41 schema tables with Base.metadata.
"""

from app.db.base import Base

from .auth import User, AuthSession
from .collector import Collector
from .facility import (
    Region,
    Facility,
    FacilityUser,
    FacilityAuthorization,
    FacilityMaterial,
    FacilityOperation,
    FacilityRate,
)
from .material import (
    MaterialCategory,
    Material,
    MaterialAlias,
    SafetyGuide,
)
from .price import (
    PriceObservation,
    PriceSummary,
)
from .lot import (
    Lot,
    MediaObject,
    LotImage,
    LocationRecord,
    Classification,
    ValuationSnapshot,
)
from .trade import (
    LotRequest,
    Offer,
    Transaction,
    TermsRevision,
    Handover,
    HandoverConfirmation,
    PaymentEntry,
)
from .provenance import (
    DataSource,
    SourceAssertion,
    DatasetVersion,
    ModelVersion,
    TrainingImage,
    ResearchInsight,
)
from .audit import (
    DomainEvent,
    AuditLog,
    SyncOperation,
    SyncChange,
    QualityFlag,
    EconomicsScenario,
)

__all__ = [
    "Base",
    "User",
    "AuthSession",
    "Collector",
    "Region",
    "Facility",
    "FacilityUser",
    "FacilityAuthorization",
    "FacilityMaterial",
    "FacilityOperation",
    "FacilityRate",
    "MaterialCategory",
    "Material",
    "MaterialAlias",
    "SafetyGuide",
    "PriceObservation",
    "PriceSummary",
    "Lot",
    "MediaObject",
    "LotImage",
    "LocationRecord",
    "Classification",
    "ValuationSnapshot",
    "LotRequest",
    "Offer",
    "Transaction",
    "TermsRevision",
    "Handover",
    "HandoverConfirmation",
    "PaymentEntry",
    "DataSource",
    "SourceAssertion",
    "DatasetVersion",
    "ModelVersion",
    "TrainingImage",
    "ResearchInsight",
    "DomainEvent",
    "AuditLog",
    "SyncOperation",
    "SyncChange",
    "QualityFlag",
    "EconomicsScenario",
]
