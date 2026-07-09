from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class CampaignDocumentType:
    """Un tipo de documento que una campaña pide (ej. "DNI", "Recibo de autónomos").

    Texto libre a propósito (ver ADR 0008): cada gestoría pide lo que
    necesita, no hay catálogo normativo fijo en este MVP.
    """

    id: UUID
    campaign_id: UUID
    name: str
    created_at: datetime


@dataclass
class Campaign:
    """Una campaña de solicitud de documentación a clientes."""

    id: UUID
    organization_id: UUID
    name: str
    created_at: datetime
    document_types: list[CampaignDocumentType] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
