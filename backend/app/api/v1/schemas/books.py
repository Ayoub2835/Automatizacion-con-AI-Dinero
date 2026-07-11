from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CreateBookRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=300)
    niche: str = Field(min_length=1, max_length=200)
    target_audience: str = Field(min_length=1, max_length=200)
    language: str = Field(min_length=1, max_length=50)
    style: str = Field(min_length=1, max_length=200)
    target_pages: int = Field(ge=10, le=1000)


class BookResponse(BaseModel):
    id: UUID
    organization_id: UUID
    topic: str
    niche: str
    target_audience: str
    language: str
    style: str
    target_pages: int
    status: str
    generation_stage: str | None
    error_message: str | None
    title: str | None
    subtitle: str | None
    market_research: dict[str, Any] | None
    sales_blurb: str | None
    seo_keywords: list[str]
    categories: list[str]
    cover_brief: str | None
    has_epub: bool
    has_pdf: bool
    created_at: datetime
    updated_at: datetime


class ChapterResponse(BaseModel):
    id: UUID
    book_id: UUID
    order: int
    title: str
    summary: str
    content: str | None
    word_count: int
    status: str
    created_at: datetime
    updated_at: datetime
