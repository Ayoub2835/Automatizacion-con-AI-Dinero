from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.campaign import Campaign, CampaignDocumentType
from app.infrastructure.database.models.campaign import (
    CampaignDocumentTypeModel,
    CampaignModel,
)


class SqlAlchemyCampaignRepository:
    """Implementación concreta de CampaignRepository sobre SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, campaign: Campaign, document_type_names: list[str]) -> Campaign:
        campaign_model = CampaignModel(
            id=campaign.id,
            organization_id=campaign.organization_id,
            name=campaign.name,
            metadata_=campaign.metadata,
        )
        self._session.add(campaign_model)

        type_models = [
            CampaignDocumentTypeModel(id=uuid4(), campaign_id=campaign.id, name=name)
            for name in document_type_names
        ]
        self._session.add_all(type_models)
        await self._session.flush()

        return Campaign(
            id=campaign_model.id,
            organization_id=campaign_model.organization_id,
            name=campaign_model.name,
            created_at=campaign_model.created_at,
            metadata=campaign_model.metadata_,
            document_types=[self._type_to_entity(m) for m in type_models],
        )

    async def get_by_id(self, campaign_id: UUID, organization_id: UUID) -> Campaign | None:
        result = await self._session.execute(
            select(CampaignModel)
            .options(selectinload(CampaignModel.document_types))
            .where(
                CampaignModel.id == campaign_id,
                CampaignModel.organization_id == organization_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_for_organization(self, organization_id: UUID) -> list[Campaign]:
        result = await self._session.execute(
            select(CampaignModel)
            .options(selectinload(CampaignModel.document_types))
            .where(CampaignModel.organization_id == organization_id)
            .order_by(CampaignModel.created_at.desc())
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    @staticmethod
    def _type_to_entity(model: CampaignDocumentTypeModel) -> CampaignDocumentType:
        return CampaignDocumentType(
            id=model.id,
            campaign_id=model.campaign_id,
            name=model.name,
            created_at=model.created_at,
        )

    @classmethod
    def _to_entity(cls, model: CampaignModel) -> Campaign:
        return Campaign(
            id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            created_at=model.created_at,
            metadata=model.metadata_,
            document_types=[cls._type_to_entity(t) for t in model.document_types],
        )
