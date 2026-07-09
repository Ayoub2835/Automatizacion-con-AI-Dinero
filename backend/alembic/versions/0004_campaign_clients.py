"""añade tabla campaign_clients

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "campaign_clients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "campaign_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campaigns.id"),
            nullable=False,
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id"),
            nullable=False,
        ),
        sa.Column("upload_token", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "complete", name="campaign_client_status", native_enum=False),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("last_reminder_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_campaign_clients_campaign_id", "campaign_clients", ["campaign_id"])
    op.create_index("ix_campaign_clients_client_id", "campaign_clients", ["client_id"])
    op.create_index(
        "ix_campaign_clients_upload_token", "campaign_clients", ["upload_token"], unique=True
    )
    op.create_unique_constraint(
        "uq_campaign_client", "campaign_clients", ["campaign_id", "client_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_campaign_client", "campaign_clients", type_="unique")
    op.drop_index("ix_campaign_clients_upload_token", table_name="campaign_clients")
    op.drop_index("ix_campaign_clients_client_id", table_name="campaign_clients")
    op.drop_index("ix_campaign_clients_campaign_id", table_name="campaign_clients")
    op.drop_table("campaign_clients")
