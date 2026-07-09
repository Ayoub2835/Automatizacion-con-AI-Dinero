from typing import Protocol
from uuid import UUID

from app.domain.entities.campaign_client import CampaignClient, CampaignClientStatus


class CampaignClientRepository(Protocol):
    """Puerto (interfaz) para persistir el envío de campañas a clientes."""

    async def create_many(self, campaign_clients: list[CampaignClient]) -> list[CampaignClient]: ...

    async def get_existing_client_ids(
        self, campaign_id: UUID, client_ids: list[UUID]
    ) -> set[UUID]: ...

    async def get_by_token(self, token: str) -> CampaignClient | None: ...

    async def list_for_campaign(self, campaign_id: UUID) -> list[CampaignClient]: ...

    async def update_status(
        self, campaign_client_id: UUID, status: CampaignClientStatus
    ) -> None: ...
