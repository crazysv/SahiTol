"""Data sources, field assertions, dataset manifests, ML metadata, and research insight models."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, Index, BigInteger, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)  # e.g., SRC-01, SRC-SYNTHETIC-GEN-01
    publisher: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    source_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    licence: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    licence_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    local_snapshot: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    locator: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    review_status: Mapped[str] = mapped_column(String(50), default="VERIFIED", nullable=False)


class SourceAssertion(Base):
    __tablename__ = "source_assertions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    field_path: Mapped[str] = mapped_column(String(100), nullable=False)
    value_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    source_id: Mapped[str] = mapped_column(String(100), ForeignKey("data_sources.id"), index=True, nullable=False)
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    reviewer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    supersedes_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    source: Mapped["DataSource"] = relationship("DataSource")


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), default="v1.0", nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    manifest_storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    manifest_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    counts_by_origin_demo: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    source_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    validation_status: Mapped[str] = mapped_column(String(50), default="VALID", nullable=False)
    data_card_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    labels_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    preprocess_version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)
    licence_manifest_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    metrics_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    data_manifest_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, default=0.70, nullable=False)
    supported_classes: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class TrainingImage(Base):
    __tablename__ = "training_images"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_or_object_key: Mapped[str] = mapped_column(String(255), nullable=False)
    source_id: Mapped[str] = mapped_column(String(100), ForeignKey("data_sources.id"), index=True, nullable=False)
    licence_ref: Mapped[str] = mapped_column(String(100), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    object_group_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    material_label: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    labeler: Mapped[str] = mapped_column(String(100), nullable=False)
    label_confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    split: Mapped[str] = mapped_column(String(20), default="train", nullable=False)  # train, val, test
    condition: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    weight_g: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    region_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)


class ResearchInsight(Base):
    __tablename__ = "research_insights"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # RC-01, RC-02, etc.
    evidence_type: Mapped[str] = mapped_column(String(50), default="SECONDARY", nullable=False)  # SECONDARY, SCENARIO
    source_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    paraphrase: Mapped[str] = mapped_column(Text, nullable=False)
    design_inference: Mapped[str] = mapped_column(Text, nullable=False)
    requirement_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    limitations: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
