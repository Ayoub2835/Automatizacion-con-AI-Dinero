from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.entities.campaign import Campaign
from app.domain.exceptions import EntityNotFoundError
from app.domain.repositories.campaign_repository import CampaignRepository


class CampaignService:
    def __init__(self, campaigns: CampaignRepository) -> None:
        self._campaigns = campaigns

    async def create(
        self, organization_id: UUID, name: str, document_type_names: list[str]
    ) -> Campaign:
        campaign = Campaign(
            id=uuid4(),
            organization_id=organization_id,
            name=name,
            created_at=datetime.now(UTC),
        )
        return await self._campaigns.create(campaign, document_type_names)

    async def list_for_organization(self, organization_id: UUID) -> list[Campaign]:
        return await self._campaigns.list_for_organization(organization_id)

    async def get(self, campaign_id: UUID, organization_id: UUID) -> Campaign:
        campaign = await self._campaigns.get_by_id(campaign_id, organization_id)
        if campaign is None:
            raise EntityNotFoundError(entity="Campaña", identifier=str(campaign_id))
        return campaign
