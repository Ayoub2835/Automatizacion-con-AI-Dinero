"""añade tablas campaigns y campaign_document_types

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_campaigns_organization_id", "campaigns", ["organization_id"])

    op.create_table(
        "campaign_document_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "campaign_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campaigns.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_campaign_document_types_campaign_id", "campaign_document_types", ["campaign_id"]
    )
    op.create_unique_constraint(
        "uq_campaign_document_type", "campaign_document_types", ["campaign_id", "name"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_campaign_document_type", "campaign_document_types", type_="unique")
    op.drop_index("ix_campaign_document_types_campaign_id", table_name="campaign_document_types")
    op.drop_table("campaign_document_types")
    op.drop_index("ix_campaigns_organization_id", table_name="campaigns")
    op.drop_table("campaigns")
