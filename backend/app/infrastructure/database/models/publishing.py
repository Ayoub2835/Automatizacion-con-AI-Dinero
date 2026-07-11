import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.domain.entities.publishing import (
    AccountConnectionStatus,
    PublicationStatus,
    PublishingPlatform,
)
from app.infrastructure.database.base import Base


class PublishingAccountModel(Base):
    __tablename__ = "publishing_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    platform: Mapped[PublishingPlatform] = mapped_column(
        SAEnum(
            PublishingPlatform, name="publishing_platform", native_enum=False, validate_strings=True
        ),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    connection_status: Mapped[AccountConnectionStatus] = mapped_column(
        SAEnum(
            AccountConnectionStatus,
            name="account_connection_status",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=AccountConnectionStatus.MANUAL,
    )
    credentials_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)


class PublicationModel(Base):
    __tablename__ = "publications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    publishing_account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("publishing_accounts.id"), nullable=False, index=True
    )
    platform: Mapped[PublishingPlatform] = mapped_column(
        SAEnum(
            PublishingPlatform,
            name="publishing_platform",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )
    status: Mapped[PublicationStatus] = mapped_column(
        SAEnum(
            PublicationStatus, name="publication_status", native_enum=False, validate_strings=True
        ),
        nullable=False,
        default=PublicationStatus.DRAFT,
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    missing_metadata_fields: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_book_id: Mapped[str | None] = mapped_column(String, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SalesRecordModel(Base):
    __tablename__ = "sales_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    publication_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("publications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    units_sold: Mapped[int] = mapped_column(Integer, nullable=False)
    revenue_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False, default="manual")
    recorded_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
