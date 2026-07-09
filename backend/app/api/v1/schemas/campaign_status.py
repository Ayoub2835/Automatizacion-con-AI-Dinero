from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class CampaignStatusDocumentTypeResponse(BaseModel):
    name: str
    satisfied: bool


class CampaignStatusDocumentResponse(BaseModel):
    id: UUID
    original_filename: str
    document_type_name: str | None
    status: str
    uploaded_at: datetime


class CampaignClientStatusResponse(BaseModel):
    campaign_client_id: UUID
    client_id: UUID
    client_name: str
    client_email: EmailStr
    status: str
    document_types: list[CampaignStatusDocumentTypeResponse]
    documents: list[CampaignStatusDocumentResponse]


class CampaignStatusResponse(BaseModel):
    campaign_id: UUID
    campaign_name: str
    clients: list[CampaignClientStatusResponse]
