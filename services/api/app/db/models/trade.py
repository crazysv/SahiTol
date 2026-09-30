"""Offers, Transactions, Handovers, and Payments models."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index, BigInteger, Text, JSON, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class LotRequest(Base):
    __tablename__ = "lot_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lots.id", ondelete="CASCADE"), index=True, nullable=False)
    facility_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), index=True, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING, REJECTED, ACCEPTED, EXPIRED
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lot_requests.id"), index=True, nullable=False)
    lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lots.id", ondelete="CASCADE"), index=True, nullable=False)
    facility_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), index=True, nullable=False)
    rate_paise_per_kg: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    fixed_total_paise: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    price_basis: Mapped[str] = mapped_column(String(50), default="RATE_PER_KG", nullable=False)  # RATE_PER_KG, FIXED_TOTAL
    condition: Mapped[str] = mapped_column(String(50), nullable=False)
    weight_basis_g: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False)  # OPEN, ACCEPTED, REJECTED, EXPIRED, WITHDRAWN
    terms_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lots.id"), unique=True, index=True, nullable=False)
    collector_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("collectors.id"), index=True, nullable=False)
    facility_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("facilities.id"), index=True, nullable=False)
    accepted_offer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("offers.id"), nullable=False)
    estimated_weight_g: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agreed_weight_g: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    quoted_total_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agreed_total_paise: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    lifecycle: Mapped[str] = mapped_column(String(50), default="AGREED", nullable=False)  # AGREED, IN_TRANSIT, DELIVERED, CONFIRMED, CLOSED, CANCELLED
    version: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    terms_revisions: Mapped[list["TermsRevision"]] = relationship("TermsRevision", back_populates="transaction")
    handovers: Mapped[list["Handover"]] = relationship("Handover", back_populates="transaction")
    payments: Mapped[list["PaymentEntry"]] = relationship("PaymentEntry", back_populates="transaction")

    __table_args__ = (
        CheckConstraint("agreed_total_paise IS NULL OR agreed_total_paise >= 0", name="chk_tx_non_negative_agreed_paise"),
    )


class TermsRevision(Base):
    __tablename__ = "terms_revisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), index=True, nullable=False)
    previous_revision_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    final_material_id: Mapped[str] = mapped_column(String(50), ForeignKey("materials.id"), nullable=False)
    measured_weight_g: Mapped[int] = mapped_column(BigInteger, nullable=False)
    final_total_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    proposed_by: Mapped[str] = mapped_column(String(50), nullable=False)  # COLLECTOR, FACILITY
    proposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    collector_ack_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    recycler_ack_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    terms_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="terms_revisions")

    __table_args__ = (
        CheckConstraint("measured_weight_g > 0", name="chk_terms_rev_positive_weight"),
        CheckConstraint("final_total_paise >= 0", name="chk_terms_rev_non_negative_paise"),
    )


class Handover(Base):
    __tablename__ = "handovers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id"), index=True, nullable=False)
    lot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lots.id"), index=True, nullable=False)
    proposal_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    proposal_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), default="v1.0", nullable=False)
    proposed_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    proposed_at_client: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at_server: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    collection_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    handover_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    agreed_terms_revision_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING_CONFIRMATION", nullable=False)  # PENDING_CONFIRMATION, CONFIRMED, DISPUTED, VOIDED
    public_token_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    version: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="handovers")
    confirmation: Mapped[Optional["HandoverConfirmation"]] = relationship("HandoverConfirmation", back_populates="handover", uselist=False)


class HandoverConfirmation(Base):
    __tablename__ = "handover_confirmations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    handover_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("handovers.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    terms_revision_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    recycler_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    handover: Mapped["Handover"] = relationship("Handover", back_populates="confirmation")


class PaymentEntry(Base):
    __tablename__ = "payment_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), index=True, nullable=False)
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    method: Mapped[str] = mapped_column(String(50), default="CASH", nullable=False)  # CASH, UPI, OTHER
    private_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    asserted_by: Mapped[str] = mapped_column(String(50), nullable=False)  # FACILITY, COLLECTOR
    asserted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="ASSERTED", nullable=False)  # ASSERTED, ACKNOWLEDGED, DISPUTED, REVERSED
    counterparty_ack_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    ack_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reversal_of: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="payments")

    __table_args__ = (
        CheckConstraint("amount_paise > 0", name="chk_payment_positive_amount"),
    )
