"""añade tablas de BookAgent AI (libros, capítulos, publicación y ventas)

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_BOOK_STATUS = sa.Enum(
    "draft", "generating", "ready", "exported", "failed", name="book_status", native_enum=False
)
_GENERATION_STAGE = sa.Enum(
    "research",
    "title",
    "outline",
    "chapters",
    "editing",
    "sales_copy",
    "cover_brief",
    "export",
    "done",
    name="book_generation_stage",
    native_enum=False,
)
_CHAPTER_STATUS = sa.Enum("pending", "drafted", "edited", name="chapter_status", native_enum=False)
_PUBLISHING_PLATFORM = sa.Enum(
    "kdp",
    "apple_books",
    "google_play_books",
    "kobo",
    name="publishing_platform",
    native_enum=False,
)
_ACCOUNT_CONNECTION_STATUS = sa.Enum(
    "manual", "connected", "needs_reauth", name="account_connection_status", native_enum=False
)
_PUBLICATION_STATUS = sa.Enum(
    "draft",
    "metadata_ready",
    "pending_review",
    "approved",
    "submitted",
    "live",
    "rejected",
    "failed",
    name="publication_status",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("topic", sa.String(), nullable=False),
        sa.Column("niche", sa.String(), nullable=False),
        sa.Column("target_audience", sa.String(), nullable=False),
        sa.Column("language", sa.String(), nullable=False),
        sa.Column("style", sa.String(), nullable=False),
        sa.Column("target_pages", sa.Integer(), nullable=False),
        sa.Column("status", _BOOK_STATUS, nullable=False, server_default="draft"),
        sa.Column("generation_stage", _GENERATION_STAGE, nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("subtitle", sa.String(), nullable=True),
        sa.Column("market_research", postgresql.JSONB(), nullable=True),
        sa.Column("sales_blurb", sa.Text(), nullable=True),
        sa.Column(
            "seo_keywords", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"
        ),
        sa.Column("categories", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("cover_brief", sa.Text(), nullable=True),
        sa.Column("epub_storage_path", sa.String(), nullable=True),
        sa.Column("pdf_storage_path", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_books_organization_id", "books", ["organization_id"])

    op.create_table(
        "book_chapters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "book_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("word_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", _CHAPTER_STATUS, nullable=False, server_default="pending"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_book_chapters_book_id", "book_chapters", ["book_id"])

    op.create_table(
        "publishing_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("platform", _PUBLISHING_PLATFORM, nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column(
            "connection_status",
            _ACCOUNT_CONNECTION_STATUS,
            nullable=False,
            server_default="manual",
        ),
        sa.Column("credentials_ref", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_publishing_accounts_organization_id", "publishing_accounts", ["organization_id"]
    )

    op.create_table(
        "publications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "book_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "publishing_account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("publishing_accounts.id"),
            nullable=False,
        ),
        sa.Column("platform", _PUBLISHING_PLATFORM, nullable=False),
        sa.Column("status", _PUBLICATION_STATUS, nullable=False, server_default="draft"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "missing_metadata_fields",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("external_book_id", sa.String(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_publications_organization_id", "publications", ["organization_id"])
    op.create_index("ix_publications_book_id", "publications", ["book_id"])
    op.create_index(
        "ix_publications_publishing_account_id", "publications", ["publishing_account_id"]
    )

    op.create_table(
        "sales_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "publication_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("publications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("units_sold", sa.Integer(), nullable=False),
        sa.Column("revenue_amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False, server_default="manual"),
        sa.Column(
            "recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_sales_records_organization_id", "sales_records", ["organization_id"])
    op.create_index("ix_sales_records_publication_id", "sales_records", ["publication_id"])


def downgrade() -> None:
    op.drop_index("ix_sales_records_publication_id", table_name="sales_records")
    op.drop_index("ix_sales_records_organization_id", table_name="sales_records")
    op.drop_table("sales_records")

    op.drop_index("ix_publications_publishing_account_id", table_name="publications")
    op.drop_index("ix_publications_book_id", table_name="publications")
    op.drop_index("ix_publications_organization_id", table_name="publications")
    op.drop_table("publications")

    op.drop_index("ix_publishing_accounts_organization_id", table_name="publishing_accounts")
    op.drop_table("publishing_accounts")

    op.drop_index("ix_book_chapters_book_id", table_name="book_chapters")
    op.drop_table("book_chapters")

    op.drop_index("ix_books_organization_id", table_name="books")
    op.drop_table("books")
