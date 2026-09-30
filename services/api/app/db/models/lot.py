"""Lot, Media, Classification, Valuation, and Location models."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, Index, BigInteger, Text, JSON, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.db.base import Base


class Lot(Base):
    __tablename__ = "lots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collector_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("collectors.id", ondelete="CASCADE"), index=True, nullable=False)
    material_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("materials.id"), index=True, nullable=True)
    material_context: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    regulatory_route: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # GENERAL_RECYCLING, AUTHORIZED_EWASTE, BATTERY_ISOLATION, HAZARDOUS_DISPOSAL
    estimated_weight_g: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    condition: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    collection_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", index=True, nullable=False)  # DRAFT, COLLECTED, LISTED, MATCHED, IN_TRANSIT, DELIVERED, CANCELLED
    version: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    origin_class: Mapped[str] = mapped_column(String(50), default="PLATFORM_GENERATED", nullable=False)
    source_kind: Mapped[str] = mapped_column(String(50), default="PLATFORM_OBSERVATION", nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    collector: Mapped["Collector"] = relationship("Collector", back_populates="lots")
    images: Mapped[list["LotImage"]] = relationship("LotImage", back_populates="lot", cascade="all, delete-orphan")
    classifications: Mapped[list["Classification"]] = relationship("Classification", back_populates="lot")
    valuations: Mapped[list["ValuationSnapshot"]] = relationship("ValuationSnapshot", back_populates="lot")

    __table_args__ = (
        CheckConstraint("estimated_weight_g IS NULL OR estimated_weight_g > 0", name="chk_positive_estimated_weight"),
        Index("ix_lots_collector_updated", "collector_id", "updated_at"),
    )


class MediaObject(Base):
    __tablename__ = "media_objects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    owner_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), index=True, nullable=True)
    storage_key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    pixel_width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pixel_height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    upload_state: Mapped[str] = mapped_column(String(50), default="STAGED", nullable=False)  # STAGED, UPLOADED, VALIDATED, REJECTED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class LotImage(Base):
    __tablename__ = "lot_images"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lots.id", ondelete="CASCADE"), index=True, nullable=False)
    media_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("media_objects.id"), index=True, nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), default="PHOTO", nullable=False)  # PHOTO, RECEIPT_EVIDENCE
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    captured_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    lot: Mapped["Lot"] = relationship("Lot", back_populates="images")
    media: Mapped["MediaObject"] = relationship("MediaObject")


class LocationRecord(Base):
    __tablename__ = "location_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    point: Mapped[Optional[Geometry]] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    coarse_area: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    accuracy_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="GPS", nullable=False)  # GPS, MANUAL, REGION, MISSING
    captured_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    age_ms: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    consent_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class Classification(Base):
    __tablename__ = "classifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lots.id", ondelete="CASCADE"), index=True, nullable=False)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    model_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    predicted_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    scores: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    threshold_version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)
    abstained: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_selected_material_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    lot: Mapped["Lot"] = relationship("Lot", back_populates="classifications")


class ValuationSnapshot(Base):
    __tablename__ = "valuation_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lots.id", ondelete="CASCADE"), index=True, nullable=False)
    price_summary_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("price_summaries.id"), nullable=True)
    input_weight_g: Mapped[int] = mapped_column(BigInteger, nullable=False)
    condition: Mapped[str] = mapped_column(String(50), nullable=False)
    low_total_paise: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    median_total_paise: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    high_total_paise: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    policy_version: Mapped[str] = mapped_column(String(50), default="PRICE_V1", nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    lot: Mapped["Lot"] = relationship("Lot", back_populates="valuations")
