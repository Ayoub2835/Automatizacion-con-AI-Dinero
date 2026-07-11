from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.book import Chapter
from app.domain.exceptions import EntityNotFoundError
from app.infrastructure.database.models.book import ChapterModel


class SqlAlchemyChapterRepository:
    """Implementación concreta de ChapterRepository sobre SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def replace_outline(self, book_id: UUID, chapters: list[Chapter]) -> list[Chapter]:
        await self._session.execute(delete(ChapterModel).where(ChapterModel.book_id == book_id))
        models = [
            ChapterModel(
                id=c.id,
                book_id=book_id,
                order=c.order,
                title=c.title,
                summary=c.summary,
                status=c.status,
            )
            for c in chapters
        ]
        self._session.add_all(models)
        await self._session.flush()
        return [self._to_entity(m) for m in models]

    async def update(self, chapter: Chapter) -> Chapter:
        model = await self._session.get(ChapterModel, chapter.id)
        if model is None:
            raise EntityNotFoundError(entity="Capítulo", identifier=str(chapter.id))

        model.content = chapter.content
        model.word_count = chapter.word_count
        model.status = chapter.status
        # Ver nota en SqlAlchemyBookRepository.update sobre por qué se fija
        # aquí en vez de depender del `onupdate` server-side de la columna
        # (naive, igual que created_at en el resto del esquema).
        model.updated_at = datetime.now(UTC).replace(tzinfo=None)
        await self._session.flush()
        return self._to_entity(model)

    async def list_for_book(self, book_id: UUID) -> list[Chapter]:
        result = await self._session.execute(
            select(ChapterModel).where(ChapterModel.book_id == book_id).order_by(ChapterModel.order)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: ChapterModel) -> Chapter:
        return Chapter(
            id=model.id,
            book_id=model.book_id,
            order=model.order,
            title=model.title,
            summary=model.summary,
            content=model.content,
            word_count=model.word_count,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
