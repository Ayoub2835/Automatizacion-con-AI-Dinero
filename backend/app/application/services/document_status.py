from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.campaign import Campaign
from app.domain.entities.document import Document, DocumentStatus


@dataclass
class DocumentTypeStatus:
    id: UUID
    name: str
    satisfied: bool


def compute_document_type_statuses(
    campaign: Campaign, documents: list[Document]
) -> list[DocumentTypeStatus]:
    """Para cada tipo de documento que pide la campaña, ¿hay ya un documento
    clasificado como ese tipo? Reutilizado por el flujo público (T5) y por
    el panel del gestor (T7)."""
    satisfied_type_ids = {
        d.campaign_document_type_id
        for d in documents
        if d.status == DocumentStatus.CLASSIFIED and d.campaign_document_type_id is not None
    }
    return [
        DocumentTypeStatus(id=t.id, name=t.name, satisfied=t.id in satisfied_type_ids)
        for t in campaign.document_types
    ]


def is_complete(document_type_statuses: list[DocumentTypeStatus]) -> bool:
    return all(s.satisfied for s in document_type_statuses)
