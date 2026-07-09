from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SendCampaignRequest(BaseModel):
    client_ids: list[UUID] = Field(min_length=1)


class CampaignClientResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    client_id: UUID
    client_name: str
    client_email: EmailStr
    status: str
    upload_url: str
    created_at: datetime
    last_reminder_sent_at: datetime | None = None
