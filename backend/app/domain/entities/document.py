from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class DocumentStatus(StrEnum):
    CLASSIFIED = "classified"
    UNCLASSIFIED = "unclassified"


@dataclass
class Document:
    """Un fichero subido por un cliente para una CampaignClient.

    `campaign_document_type_id` es None hasta que se clasifica con
    confianza suficiente (ver ADR 0011); mientras tanto el documento
    aparece como "sin clasificar" para el gestor.
    """

    id: UUID
    campaign_client_id: UUID
    original_filename: str
    storage_path: str
    content_type: str
    status: DocumentStatus
    uploaded_at: datetime
    campaign_document_type_id: UUID | None = None
    classification_confidence: float | None = None
