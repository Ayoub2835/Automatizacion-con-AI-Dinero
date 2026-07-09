from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class CampaignClientStatus(StrEnum):
    PENDING = "pending"
    COMPLETE = "complete"


@dataclass
class CampaignClient:
    """Una campaña enviada a un cliente concreto: lleva el enlace seguro de subida.

    `upload_token` es el enlace seguro (ver ADR 0008): quien lo conoce puede
    subir documentos sin necesitar una cuenta ni iniciar sesión.
    """

    id: UUID
    campaign_id: UUID
    client_id: UUID
    upload_token: str
    status: CampaignClientStatus
    created_at: datetime
    last_reminder_sent_at: datetime | None = None
