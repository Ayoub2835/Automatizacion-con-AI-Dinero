from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.entities.client import Client
from app.domain.repositories.client_repository import ClientRepository


class ClientService:
    def __init__(self, clients: ClientRepository) -> None:
        self._clients = clients

    async def create(
        self, organization_id: UUID, name: str, email: str, phone: str | None
    ) -> Client:
        client = Client(
            id=uuid4(),
            organization_id=organization_id,
            name=name,
            email=email,
            phone=phone,
            created_at=datetime.now(UTC),
        )
        return await self._clients.create(client)

    async def list_for_organization(self, organization_id: UUID) -> list[Client]:
        return await self._clients.list_for_organization(organization_id)
