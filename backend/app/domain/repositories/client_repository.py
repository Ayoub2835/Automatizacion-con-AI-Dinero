from typing import Protocol
from uuid import UUID

from app.domain.entities.client import Client


class ClientRepository(Protocol):
    """Puerto (interfaz) para persistir clientes de una gestoría."""

    async def get_by_id(self, client_id: UUID, organization_id: UUID) -> Client | None: ...

    async def list_for_organization(self, organization_id: UUID) -> list[Client]: ...

    async def create(self, client: Client) -> Client: ...
