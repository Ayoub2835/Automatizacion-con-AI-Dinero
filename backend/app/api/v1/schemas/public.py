from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PublicDocumentTypeStatusResponse(BaseModel):
    name: str
    satisfied: bool


class PublicDocumentResponse(BaseModel):
    id: UUID
    original_filename: str
    document_type_name: str | None
    status: str
    uploaded_at: datetime


class PublicCampaignStatusResponse(BaseModel):
    campaign_name: str
    client_status: str
    document_types: list[PublicDocumentTypeStatusResponse]
    documents: list[PublicDocumentResponse]
