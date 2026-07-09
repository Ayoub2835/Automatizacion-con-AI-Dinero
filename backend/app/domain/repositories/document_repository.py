from typing import Protocol
from uuid import UUID

from app.domain.entities.document import Document


class DocumentRepository(Protocol):
    """Puerto (interfaz) para persistir documentos subidos."""

    async def create(self, document: Document) -> Document: ...

    async def list_for_campaign_clients(
        self, campaign_client_ids: list[UUID]
    ) -> list[Document]: ...
