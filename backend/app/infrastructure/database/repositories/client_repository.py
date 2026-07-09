from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.client import Client
from app.infrastructure.database.models.client import ClientModel


class SqlAlchemyClientRepository:
    """Implementación concreta de ClientRepository sobre SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, client_id: UUID, organization_id: UUID) -> Client | None:
        result = await self._session.execute(
            select(ClientModel).where(
                ClientModel.id == client_id,
                ClientModel.organization_id == organization_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_for_organization(self, organization_id: UUID) -> list[Client]:
        result = await self._session.execute(
            select(ClientModel)
            .where(ClientModel.organization_id == organization_id)
            .order_by(ClientModel.created_at.desc())
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def create(self, client: Client) -> Client:
        model = ClientModel(
            id=client.id,
            organization_id=client.organization_id,
            name=client.name,
            email=client.email,
            phone=client.phone,
            metadata_=client.metadata,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: ClientModel) -> Client:
        return Client(
            id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            created_at=model.created_at,
            metadata=model.metadata_,
        )
