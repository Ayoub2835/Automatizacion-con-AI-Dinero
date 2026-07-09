"""añade tabla documents

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "campaign_client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campaign_clients.id"),
            nullable=False,
        ),
        sa.Column(
            "campaign_document_type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("campaign_document_types.id"),
            nullable=True,
        ),
        sa.Column("original_filename", sa.String(), nullable=False),
        sa.Column("storage_path", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("classified", "unclassified", name="document_status", native_enum=False),
            nullable=False,
            server_default="unclassified",
        ),
        sa.Column("classification_confidence", sa.Float(), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_documents_campaign_client_id", "documents", ["campaign_client_id"])
    op.create_index(
        "ix_documents_campaign_document_type_id", "documents", ["campaign_document_type_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_documents_campaign_document_type_id", table_name="documents")
    op.drop_index("ix_documents_campaign_client_id", table_name="documents")
    op.drop_table("documents")
