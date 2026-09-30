"""Price observation and statistical summary models."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Index, BigInteger, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class PriceObservation(Base):
    __tablename__ = "price_observations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id: Mapped[str] = mapped_column(String(50), ForeignKey("materials.id"), index=True, nullable=False)
    subcategory_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    region_id: Mapped[str] = mapped_column(String(50), ForeignKey("regions.id"), index=True, nullable=False)
    condition: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rate_paise_per_unit: Mapped[int] = mapped_column(BigInteger, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="kg", nullable=False)
    price_kind: Mapped[str] = mapped_column(String(20), default="BUY", nullable=False)  # BUY, QUOTE, SELL
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    facility_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    source_id: Mapped[str] = mapped_column(String(100), nullable=False)
    review_status: Mapped[str] = mapped_column(String(50), default="PENDING_REVIEW", nullable=False)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    origin_class: Mapped[str] = mapped_column(String(50), default="EXTERNAL_PUBLIC", nullable=False)
    source_kind: Mapped[str] = mapped_column(String(50), default="PUBLIC_MARKET_QUOTE", nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_price_obs_cohort_date", "material_id", "region_id", "observed_at"),
    )


class PriceSummary(Base):
    __tablename__ = "price_summaries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cohort_key: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # e.g., MAT-PCB-01:DELHI_NCR:CLEAN
    policy_version: Mapped[str] = mapped_column(String(50), default="PRICE_V1", nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    source_cutoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    q1_rate: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    median_rate: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    q3_rate: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    independent_sources: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence: Mapped[str] = mapped_column(String(50), default="INSUFFICIENT_DATA", nullable=False)  # HIGH, MEDIUM, LOW, INSUFFICIENT_DATA
    reason_codes: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    observation_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
