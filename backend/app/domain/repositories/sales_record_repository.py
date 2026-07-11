from typing import Protocol
from uuid import UUID

from app.domain.entities.publishing import SalesRecord


class SalesRecordRepository(Protocol):
    """Puerto (interfaz) para persistir registros de ventas/ingresos."""

    async def create(self, sales_record: SalesRecord) -> SalesRecord: ...

    async def list_for_organization(self, organization_id: UUID) -> list[SalesRecord]: ...

    async def list_for_publication(
        self, publication_id: UUID, organization_id: UUID
    ) -> list[SalesRecord]: ...
