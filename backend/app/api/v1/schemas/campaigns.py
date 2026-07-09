from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateCampaignRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    document_types: list[str] = Field(min_length=1, max_length=50)

    @field_validator("document_types")
    @classmethod
    def _normalize_document_types(cls, value: list[str]) -> list[str]:
        normalized = [name.strip() for name in value]
        if any(not name for name in normalized):
            raise ValueError("Los tipos de documento no pueden estar vacíos")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Los tipos de documento no pueden repetirse")
        return normalized


class CampaignDocumentTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    created_at: datetime
    document_types: list[CampaignDocumentTypeResponse]
