"""Region, Facility, Authorization, and Operation models."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index, BigInteger, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.db.base import Base


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., DELHI_NCR, MAHARASHTRA
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    state_code: Mapped[str] = mapped_column(String(10), nullable=False)  # DL, MH
    kind: Mapped[str] = mapped_column(String(50), default="STATE", nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("regions.id"), nullable=True)
    centroid: Mapped[Optional[Geometry]] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    boundary: Mapped[Optional[Geometry]] = mapped_column(Geometry("POLYGON", srid=4326), nullable=True)


class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    facility_name: Mapped[str] = mapped_column(String(200), nullable=False)
    kind: Mapped[str] = mapped_column(String(50), nullable=False)  # RECYCLER, DISMANTLER, AGGREGATOR, COLLECTION_CENTRE
    address_public: Mapped[str] = mapped_column(Text, nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    region_id: Mapped[str] = mapped_column(String(50), ForeignKey("regions.id"), index=True, nullable=False)
    geo_point: Mapped[Optional[Geometry]] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    geocode_accuracy: Mapped[Optional[str]] = mapped_column(String(50), default="UNKNOWN", nullable=True)
    contact_public: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    region: Mapped["Region"] = relationship("Region")
    authorizations: Mapped[list["FacilityAuthorization"]] = relationship("FacilityAuthorization", back_populates="facility")
    materials: Mapped[list["FacilityMaterial"]] = relationship("FacilityMaterial", back_populates="facility")
    operations: Mapped[Optional["FacilityOperation"]] = relationship("FacilityOperation", back_populates="facility", uselist=False)
    rates: Mapped[list["FacilityRate"]] = relationship("FacilityRate", back_populates="facility")
    users: Mapped[list["FacilityUser"]] = relationship("FacilityUser", back_populates="facility")

    __table_args__ = (
        Index("ix_facilities_updated_at", "id", "updated_at"),
    )


class FacilityUser(Base):
    __tablename__ = "facility_users"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    facility_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), primary_key=True)
    membership_role: Mapped[str] = mapped_column(String(50), default="OPERATOR", nullable=False)  # OWNER, MANAGER, OPERATOR
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    facility: Mapped["Facility"] = relationship("Facility", back_populates="users")


class FacilityAuthorization(Base):
    __tablename__ = "facility_authorizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), index=True, nullable=False)
    route: Mapped[str] = mapped_column(String(50), nullable=False)
    authority: Mapped[str] = mapped_column(String(100), nullable=False)  # CPCB, DPCC, MPCB
    reference: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="VALID", nullable=False)
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_document_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_level: Mapped[str] = mapped_column(String(50), default="REGISTRY_MATCH", nullable=False)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    scope_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    facility: Mapped["Facility"] = relationship("Facility", back_populates="authorizations")


class FacilityMaterial(Base):
    __tablename__ = "facility_materials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), index=True, nullable=False)
    material_id: Mapped[str] = mapped_column(String(50), ForeignKey("materials.id"), index=True, nullable=False)
    route: Mapped[str] = mapped_column(String(50), nullable=False)
    accepted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_weight_g: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    max_weight_g: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    evidence_source_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    facility: Mapped["Facility"] = relationship("Facility", back_populates="materials")


class FacilityOperation(Base):
    __tablename__ = "facility_operations"

    facility_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), primary_key=True)
    pickup_status: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    service_regions: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    service_geometry: Mapped[Optional[Geometry]] = mapped_column(Geometry("POLYGON", srid=4326), nullable=True)
    accepting_status: Mapped[str] = mapped_column(String(50), default="ACCEPTING", nullable=False)
    operational_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    source_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    facility: Mapped["Facility"] = relationship("Facility", back_populates="operations")


class FacilityRate(Base):
    __tablename__ = "facility_rates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), index=True, nullable=False)
    material_id: Mapped[str] = mapped_column(String(50), ForeignKey("materials.id"), index=True, nullable=False)
    condition: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    region_id: Mapped[str] = mapped_column(String(50), ForeignKey("regions.id"), index=True, nullable=False)
    rate_paise_per_unit: Mapped[int] = mapped_column(BigInteger, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="kg", nullable=False)
    price_kind: Mapped[str] = mapped_column(String(20), default="QUOTE", nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_id: Mapped[str] = mapped_column(String(100), nullable=False)
    review_status: Mapped[str] = mapped_column(String(50), default="PENDING_REVIEW", nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    facility: Mapped["Facility"] = relationship("Facility", back_populates="rates")
