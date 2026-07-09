from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.campaign_client import CampaignClient, CampaignClientStatus
from app.infrastructure.database.models.campaign_client import CampaignClientModel


class SqlAlchemyCampaignClientRepository:
    """Implementación concreta de CampaignClientRepository sobre SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_many(self, campaign_clients: list[CampaignClient]) -> list[CampaignClient]:
        models = [
            CampaignClientModel(
                id=cc.id,
                campaign_id=cc.campaign_id,
                client_id=cc.client_id,
                upload_token=cc.upload_token,
                status=cc.status,
                last_reminder_sent_at=cc.last_reminder_sent_at,
            )
            for cc in campaign_clients
        ]
        self._session.add_all(models)
        await self._session.flush()
        return [self._to_entity(m) for m in models]

    async def get_existing_client_ids(self, campaign_id: UUID, client_ids: list[UUID]) -> set[UUID]:
        result = await self._session.execute(
            select(CampaignClientModel.client_id).where(
                CampaignClientModel.campaign_id == campaign_id,
                CampaignClientModel.client_id.in_(client_ids),
            )
        )
        return set(result.scalars().all())

    async def get_by_token(self, token: str) -> CampaignClient | None:
        result = await self._session.execute(
            select(CampaignClientModel).where(CampaignClientModel.upload_token == token)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_for_campaign(self, campaign_id: UUID) -> list[CampaignClient]:
        result = await self._session.execute(
            select(CampaignClientModel)
            .where(CampaignClientModel.campaign_id == campaign_id)
            .order_by(CampaignClientModel.created_at)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: CampaignClientModel) -> CampaignClient:
        return CampaignClient(
            id=model.id,
            campaign_id=model.campaign_id,
            client_id=model.client_id,
            upload_token=model.upload_token,
            status=CampaignClientStatus(model.status),
            last_reminder_sent_at=model.last_reminder_sent_at,
            created_at=model.created_at,
        )
