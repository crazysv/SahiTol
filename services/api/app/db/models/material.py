"""Material taxonomy, aliases, and safety guide models."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class MaterialCategory(Base):
    __tablename__ = "material_categories"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # PCB, BATTERY, CRT, LCD, CABLES, PLASTICS, MOTORS, OTHER
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    label_key: Mapped[str] = mapped_column(String(100), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    materials: Mapped[list["Material"]] = relationship("Material", back_populates="category")


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # MAT-PCB-01, MAT-BAT-01, etc.
    category_id: Mapped[str] = mapped_column(String(50), ForeignKey("material_categories.id"), index=True, nullable=False)
    subcategory_code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    description_key: Mapped[str] = mapped_column(String(100), nullable=False)
    condition_options: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    allowed_units: Mapped[str] = mapped_column(String(50), default="kg,g", nullable=False)
    default_route: Mapped[str] = mapped_column(String(50), nullable=False)  # GENERAL_RECYCLING, AUTHORIZED_EWASTE, BATTERY_ISOLATION, HAZARDOUS_DISPOSAL
    route_requires_context: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    safety_guide_ids: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    category: Mapped["MaterialCategory"] = relationship("MaterialCategory", back_populates="materials")
    aliases: Mapped[list["MaterialAlias"]] = relationship("MaterialAlias", back_populates="material")


class MaterialAlias(Base):
    __tablename__ = "material_aliases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id: Mapped[str] = mapped_column(String(50), ForeignKey("materials.id", ondelete="CASCADE"), index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)  # en, hi, mr
    local_term: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_term: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    material: Mapped["Material"] = relationship("Material", back_populates="aliases")

    __table_args__ = (
        UniqueConstraint("material_id", "language", "normalized_term", name="uq_material_alias_term"),
    )


class SafetyGuide(Base):
    __tablename__ = "safety_guides"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # SG-EWASTE-01, SG-BATTERY-01
    material_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    route: Mapped[str] = mapped_column(String(50), nullable=False)
    text_key: Mapped[str] = mapped_column(String(100), nullable=False)
    icon_asset_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    image_asset_ref: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    audio_keys: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)  # {"en": "...", "hi": "...", "mr": "..."}
    source_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="v1.0", nullable=False)
    review_status: Mapped[str] = mapped_column(String(50), default="APPROVED", nullable=False)
