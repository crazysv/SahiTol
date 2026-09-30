"""Shared test database engine, tables, and session maker for API tests."""
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.auth import User, AuthSession
from app.db.models.collector import Collector
from app.db.models.facility import (
    Region,
    Facility,
    FacilityUser,
    FacilityAuthorization,
    FacilityMaterial,
    FacilityOperation,
    FacilityRate,
)
from app.db.models.lot import Lot, LotImage, MediaObject, LocationRecord, Classification, ValuationSnapshot

from app.db.models.provenance import DataSource
from app.db.models.material import MaterialCategory, Material, MaterialAlias, SafetyGuide
from app.db.models.audit import SyncChange, SyncOperation, DomainEvent, QualityFlag, EconomicsScenario
from app.db.models.price import PriceObservation, PriceSummary
from app.db.models.trade import (
    LotRequest,
    Offer,
    Transaction,
    TermsRevision,
    Handover,
    HandoverConfirmation,
    PaymentEntry,
)

# Single shared in-memory SQLite database
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

@event.listens_for(test_engine, "connect")
def register_sqlite_spatial_stubs(dbapi_connection, connection_record):
    """Stub spatial functions for in-memory SQLite test database."""
    def sqlite_as_ewkb(val, *args):
        if not val:
            return None
        if isinstance(val, (bytes, memoryview)):
            return val
        s = str(val)
        try:
            srid = 4326
            if s.startswith("SRID="):
                parts = s.split(";", 1)
                srid = int(parts[0].replace("SRID=", ""))
                wkt_text = parts[1]
            else:
                wkt_text = s
            from shapely import wkt, wkb
            geom = wkt.loads(wkt_text)
            return wkb.dumps(geom, srid=srid, hex=True)
        except Exception:
            return s

    dbapi_connection.create_function("GeomFromEWKT", -1, lambda x, *args: x)
    dbapi_connection.create_function("AsEWKB", -1, sqlite_as_ewkb)
    dbapi_connection.create_function("RecoverGeometryColumn", -1, lambda *a: 1)
    dbapi_connection.create_function("CreateSpatialIndex", -1, lambda *a: 1)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create all tables needed for API tests
Base.metadata.create_all(
    bind=test_engine,
    tables=[
        User.__table__,
        AuthSession.__table__,
        Collector.__table__,
        Region.__table__,
        Facility.__table__,
        FacilityUser.__table__,
        FacilityAuthorization.__table__,
        FacilityMaterial.__table__,
        FacilityOperation.__table__,
        FacilityRate.__table__,
        Lot.__table__,
        LotImage.__table__,
        MediaObject.__table__,
        LocationRecord.__table__,
        Classification.__table__,
        ValuationSnapshot.__table__,
        DataSource.__table__,
        MaterialCategory.__table__,
        Material.__table__,
        MaterialAlias.__table__,
        SafetyGuide.__table__,
        SyncChange.__table__,
        SyncOperation.__table__,
        DomainEvent.__table__,
        QualityFlag.__table__,
        PriceObservation.__table__,
        PriceSummary.__table__,
        LotRequest.__table__,
        Offer.__table__,
        Transaction.__table__,
        TermsRevision.__table__,
        Handover.__table__,
        HandoverConfirmation.__table__,
        PaymentEntry.__table__,
        EconomicsScenario.__table__,
    ]
)


def override_get_db() -> Generator[Session, None, None]:
    """Dependency override for get_db using test SQLite database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
