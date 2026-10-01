"""store the asserting user for payment counterparty controls

Revision ID: 0002_payment_asserting_actor
Revises: 0001_initial_schema
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_payment_asserting_actor"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Nullable preserves pre-migration immutable entries. New assertions always
    # populate the column; legacy entries remain auditable through DomainEvent.
    op.add_column(
        "payment_entries",
        sa.Column("asserted_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_payment_entries_asserted_by_user_id", "payment_entries", ["asserted_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_payment_entries_asserted_by_user_id", table_name="payment_entries")
    op.drop_column("payment_entries", "asserted_by_user_id")
