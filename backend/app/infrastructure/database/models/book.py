import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.domain.entities.book import BookStatus, ChapterStatus, GenerationStage
from app.infrastructure.database.base import Base


class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    topic: Mapped[str] = mapped_column(String, nullable=False)
    niche: Mapped[str] = mapped_column(String, nullable=False)
    target_audience: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    style: Mapped[str] = mapped_column(String, nullable=False)
    target_pages: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[BookStatus] = mapped_column(
        SAEnum(BookStatus, name="book_status", native_enum=False, validate_strings=True),
        nullable=False,
        default=BookStatus.DRAFT,
    )
    generation_stage: Mapped[GenerationStage | None] = mapped_column(
        SAEnum(
            GenerationStage, name="book_generation_stage", native_enum=False, validate_strings=True
        ),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    subtitle: Mapped[str | None] = mapped_column(String, nullable=True)
    market_research: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    sales_blurb: Mapped[str | None] = mapped_column(Text, nullable=True)
    seo_keywords: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    categories: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    cover_brief: Mapped[str | None] = mapped_column(Text, nullable=True)
    epub_storage_path: Mapped[str | None] = mapped_column(String, nullable=True)
    pdf_storage_path: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    chapters: Mapped[list["ChapterModel"]] = relationship(
        back_populates="book", order_by="ChapterModel.order", cascade="all, delete-orphan"
    )


class ChapterModel(Base):
    __tablename__ = "book_chapters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[ChapterStatus] = mapped_column(
        SAEnum(ChapterStatus, name="chapter_status", native_enum=False, validate_strings=True),
        nullable=False,
        default=ChapterStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    book: Mapped["BookModel"] = relationship(back_populates="chapters")
