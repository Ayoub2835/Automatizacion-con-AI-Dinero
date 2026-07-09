from typing import Protocol
from uuid import UUID

from app.domain.entities.campaign import Campaign


class CampaignRepository(Protocol):
    """Puerto (interfaz) para persistir campañas y sus tipos de documento requeridos."""

    async def create(self, campaign: Campaign, document_type_names: list[str]) -> Campaign: ...

    async def get_by_id(self, campaign_id: UUID, organization_id: UUID) -> Campaign | None: ...

    async def list_for_organization(self, organization_id: UUID) -> list[Campaign]: ...
