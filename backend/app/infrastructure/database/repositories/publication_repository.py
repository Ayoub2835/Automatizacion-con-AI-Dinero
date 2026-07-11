from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.publishing import Publication
from app.domain.exceptions import EntityNotFoundError
from app.infrastructure.database.models.publishing import PublicationModel


class SqlAlchemyPublicationRepository:
    """Implementación concreta de PublicationRepository sobre SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, publication: Publication) -> Publication:
        model = PublicationModel(
            id=publication.id,
            organization_id=publication.organization_id,
            book_id=publication.book_id,
            publishing_account_id=publication.publishing_account_id,
            platform=publication.platform,
            status=publication.status,
            metadata_=publication.metadata,
            missing_metadata_fields=publication.missing_metadata_fields,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def update(self, publication: Publication) -> Publication:
        model = await self._session.get(PublicationModel, publication.id)
        if model is None:
            raise EntityNotFoundError(entity="Publicación", identifier=str(publication.id))

        model.status = publication.status
        model.metadata_ = publication.metadata
        model.missing_metadata_fields = publication.missing_metadata_fields
        model.instructions = publication.instructions
        model.review_notes = publication.review_notes
        model.external_book_id = publication.external_book_id
        model.submitted_at = publication.submitted_at
        model.published_at = publication.published_at
        model.last_synced_at = publication.last_synced_at
        # Ver nota en SqlAlchemyBookRepository.update sobre por qué se fija
        # aquí en vez de depender del `onupdate` server-side de la columna
        # (naive, igual que created_at en el resto del esquema).
        model.updated_at = datetime.now(UTC).replace(tzinfo=None)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, publication_id: UUID, organization_id: UUID) -> Publication | None:
        result = await self._session.execute(
            select(PublicationModel).where(
                PublicationModel.id == publication_id,
                PublicationModel.organization_id == organization_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_for_book(self, book_id: UUID, organization_id: UUID) -> list[Publication]:
        result = await self._session.execute(
            select(PublicationModel)
            .where(
                PublicationModel.book_id == book_id,
                PublicationModel.organization_id == organization_id,
            )
            .order_by(PublicationModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_for_organization(self, organization_id: UUID) -> list[Publication]:
        result = await self._session.execute(
            select(PublicationModel)
            .where(PublicationModel.organization_id == organization_id)
            .order_by(PublicationModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: PublicationModel) -> Publication:
        return Publication(
            id=model.id,
            organization_id=model.organization_id,
            book_id=model.book_id,
            publishing_account_id=model.publishing_account_id,
            platform=model.platform,
            status=model.status,
            metadata=model.metadata_,
            missing_metadata_fields=list(model.missing_metadata_fields),
            instructions=model.instructions,
            review_notes=model.review_notes,
            external_book_id=model.external_book_id,
            submitted_at=model.submitted_at,
            published_at=model.published_at,
            last_synced_at=model.last_synced_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
