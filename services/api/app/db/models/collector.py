"""Collector profile model."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, BigInteger, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Collector(Base):
    __tablename__ = "collectors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    display_alias: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="hi", nullable=False)  # en, hi, mr
    region_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("regions.id", ondelete="SET NULL"), index=True, nullable=True)
    general_area: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    consent_version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)
    version: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="collector")
    region: Mapped[Optional["Region"]] = relationship("Region")
    lots: Mapped[list["Lot"]] = relationship("Lot", back_populates="collector")

    __table_args__ = (
        Index("ix_collectors_updated_at", "id", "updated_at"),
    )
