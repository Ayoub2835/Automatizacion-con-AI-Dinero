from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.publishing import PublishingAccount
from app.infrastructure.database.models.publishing import PublishingAccountModel


class SqlAlchemyPublishingAccountRepository:
    """Implementación concreta de PublishingAccountRepository sobre SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, account: PublishingAccount) -> PublishingAccount:
        model = PublishingAccountModel(
            id=account.id,
            organization_id=account.organization_id,
            platform=account.platform,
            display_name=account.display_name,
            connection_status=account.connection_status,
            credentials_ref=account.credentials_ref,
            notes=account.notes,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, account_id: UUID, organization_id: UUID) -> PublishingAccount | None:
        result = await self._session.execute(
            select(PublishingAccountModel).where(
                PublishingAccountModel.id == account_id,
                PublishingAccountModel.organization_id == organization_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_for_organization(self, organization_id: UUID) -> list[PublishingAccount]:
        result = await self._session.execute(
            select(PublishingAccountModel)
            .where(PublishingAccountModel.organization_id == organization_id)
            .order_by(PublishingAccountModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: PublishingAccountModel) -> PublishingAccount:
        return PublishingAccount(
            id=model.id,
            organization_id=model.organization_id,
            platform=model.platform,
            display_name=model.display_name,
            connection_status=model.connection_status,
            credentials_ref=model.credentials_ref,
            notes=model.notes,
            created_at=model.created_at,
        )
