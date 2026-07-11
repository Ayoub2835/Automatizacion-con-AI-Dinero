from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.domain.entities.publishing import PublishingPlatform


class ConnectAccountRequest(BaseModel):
    platform: PublishingPlatform
    display_name: str = Field(min_length=1, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)


class PublishingAccountResponse(BaseModel):
    id: UUID
    organization_id: UUID
    platform: str
    display_name: str
    connection_status: str
    notes: str | None
    created_at: datetime


class PreparePublicationRequest(BaseModel):
    publishing_account_id: UUID
    metadata: dict[str, str] = Field(default_factory=dict)


class UpdatePublicationMetadataRequest(BaseModel):
    metadata: dict[str, str] = Field(default_factory=dict)


class RejectPublicationRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=2000)


class MarkPublicationLiveRequest(BaseModel):
    external_book_id: str | None = Field(default=None, max_length=200)


class PublicationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    book_id: UUID
    publishing_account_id: UUID
    platform: str
    status: str
    metadata: dict[str, str]
    missing_metadata_fields: list[str]
    instructions: str | None
    review_notes: str | None
    external_book_id: str | None
    submitted_at: datetime | None
    published_at: datetime | None
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SalesRecordRequest(BaseModel):
    period_start: datetime
    period_end: datetime
    units_sold: int = Field(ge=0)
    revenue_amount: float = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def _uppercase_currency(cls, value: str) -> str:
        return value.upper()


class SalesRecordResponse(BaseModel):
    id: UUID
    organization_id: UUID
    publication_id: UUID
    period_start: datetime
    period_end: datetime
    units_sold: int
    revenue_amount: float
    currency: str
    source: str
    recorded_at: datetime


class DashboardSummaryResponse(BaseModel):
    total_books: int
    books_by_status: dict[str, int]
    total_publications: int
    publications_by_status: dict[str, int]
    total_units_sold: int
    revenue_by_currency: dict[str, float]
