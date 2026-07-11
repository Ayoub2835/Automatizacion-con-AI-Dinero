from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.book import Book
from app.domain.exceptions import EntityNotFoundError
from app.infrastructure.database.models.book import BookModel


class SqlAlchemyBookRepository:
    """Implementación concreta de BookRepository sobre SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, book: Book) -> Book:
        model = BookModel(
            id=book.id,
            organization_id=book.organization_id,
            topic=book.topic,
            niche=book.niche,
            target_audience=book.target_audience,
            language=book.language,
            style=book.style,
            target_pages=book.target_pages,
            status=book.status,
            generation_stage=book.generation_stage,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def update(self, book: Book) -> Book:
        model = await self._session.get(BookModel, book.id)
        if model is None:
            raise EntityNotFoundError(entity="Libro", identifier=str(book.id))

        model.status = book.status
        model.generation_stage = book.generation_stage
        model.error_message = book.error_message
        model.title = book.title
        model.subtitle = book.subtitle
        model.market_research = book.market_research
        model.sales_blurb = book.sales_blurb
        model.seo_keywords = book.seo_keywords
        model.categories = book.categories
        model.cover_brief = book.cover_brief
        model.epub_storage_path = book.epub_storage_path
        model.pdf_storage_path = book.pdf_storage_path
        # Se fija en Python en vez de dejarlo solo en manos de `onupdate`
        # (columna server-side): con AsyncSession, leer un valor generado
        # por el servidor tras el UPDATE requeriría un refresh explícito
        # awaited — fijarlo aquí evita ese round-trip extra en cada etapa
        # del pipeline de generación (ver BookGenerationService). La columna
        # es TIMESTAMP WITHOUT TIME ZONE (igual que created_at en el resto
        # del esquema, ver campaign_client_repository.mark_reminder_sent),
        # así que se guarda naive.
        model.updated_at = datetime.now(UTC).replace(tzinfo=None)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, book_id: UUID, organization_id: UUID) -> Book | None:
        result = await self._session.execute(
            select(BookModel).where(
                BookModel.id == book_id, BookModel.organization_id == organization_id
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_for_organization(self, organization_id: UUID) -> list[Book]:
        result = await self._session.execute(
            select(BookModel)
            .where(BookModel.organization_id == organization_id)
            .order_by(BookModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: BookModel) -> Book:
        return Book(
            id=model.id,
            organization_id=model.organization_id,
            topic=model.topic,
            niche=model.niche,
            target_audience=model.target_audience,
            language=model.language,
            style=model.style,
            target_pages=model.target_pages,
            status=model.status,
            generation_stage=model.generation_stage,
            error_message=model.error_message,
            title=model.title,
            subtitle=model.subtitle,
            market_research=model.market_research,
            sales_blurb=model.sales_blurb,
            seo_keywords=list(model.seo_keywords),
            categories=list(model.categories),
            cover_brief=model.cover_brief,
            epub_storage_path=model.epub_storage_path,
            pdf_storage_path=model.pdf_storage_path,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
