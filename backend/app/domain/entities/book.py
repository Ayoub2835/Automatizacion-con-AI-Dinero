from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class BookStatus(StrEnum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    EXPORTED = "exported"
    FAILED = "failed"


class GenerationStage(StrEnum):
    """Etapa actual del pipeline autónomo (ver BookGenerationService).

    Se guarda para que el panel muestre progreso ("investigando mercado",
    "escribiendo capítulo 3/10"...) mientras `status` sigue en GENERATING.
    """

    RESEARCH = "research"
    TITLE = "title"
    OUTLINE = "outline"
    CHAPTERS = "chapters"
    EDITING = "editing"
    SALES_COPY = "sales_copy"
    COVER_BRIEF = "cover_brief"
    EXPORT = "export"
    DONE = "done"


class ChapterStatus(StrEnum):
    PENDING = "pending"
    DRAFTED = "drafted"
    EDITED = "edited"


@dataclass
class Book:
    """Un libro gestionado por BookAgent AI, desde el brief inicial del
    usuario hasta el manuscrito exportado y listo para publicar.

    Los campos de salida del pipeline (`market_research`, `sales_blurb`,
    `seo_keywords`, `categories`, `cover_brief`, `*_storage_path`) son
    `None`/vacíos hasta que su etapa correspondiente se completa — el
    panel los usa para mostrar progreso incremental, no solo estado final.
    """

    id: UUID
    organization_id: UUID
    topic: str
    niche: str
    target_audience: str
    language: str
    style: str
    target_pages: int
    created_at: datetime
    updated_at: datetime
    status: BookStatus = BookStatus.DRAFT
    generation_stage: GenerationStage | None = None
    error_message: str | None = None
    title: str | None = None
    subtitle: str | None = None
    market_research: dict[str, Any] | None = None
    sales_blurb: str | None = None
    seo_keywords: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    cover_brief: str | None = None
    epub_storage_path: str | None = None
    pdf_storage_path: str | None = None


@dataclass
class Chapter:
    """Un capítulo del manuscrito. `summary` viene de la etapa OUTLINE y se
    usa como brief para la etapa CHAPTERS (ver ClaudeBookContentGenerator)."""

    id: UUID
    book_id: UUID
    order: int
    title: str
    summary: str
    created_at: datetime
    updated_at: datetime
    content: str | None = None
    word_count: int = 0
    status: ChapterStatus = ChapterStatus.PENDING
