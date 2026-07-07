from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.organization import Organization
from app.infrastructure.database.models.organization import OrganizationModel


class SqlAlchemyOrganizationRepository:
    """Implementación concreta de OrganizationRepository sobre SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, organization_id: UUID) -> Organization | None:
        model = await self._session.get(OrganizationModel, organization_id)
        return self._to_entity(model) if model else None

    async def create(self, organization: Organization) -> Organization:
        model = OrganizationModel(
            id=organization.id,
            name=organization.name,
            metadata_=organization.metadata,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: OrganizationModel) -> Organization:
        return Organization(
            id=model.id,
            name=model.name,
            created_at=model.created_at,
            metadata=model.metadata_,
        )
