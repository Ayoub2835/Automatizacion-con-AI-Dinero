from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.book_generation_service import BookGenerationService
from app.domain.entities.book import Book, BookStatus, ChapterStatus, GenerationStage
from app.domain.entities.organization import Organization
from app.infrastructure.database.repositories.book_repository import SqlAlchemyBookRepository
from app.infrastructure.database.repositories.chapter_repository import (
    SqlAlchemyChapterRepository,
)
from app.infrastructure.database.repositories.organization_repository import (
    SqlAlchemyOrganizationRepository,
)
from tests.fakes import FakeBookContentGenerator


async def _create_organization(session: AsyncSession) -> Organization:
    organizations = SqlAlchemyOrganizationRepository(session)
    return await organizations.create(
        Organization(id=uuid4(), name="Editorial de prueba", created_at=datetime.now(UTC))
    )


def _new_book(organization_id: UUID) -> Book:
    now = datetime.now(UTC)
    return Book(
        id=uuid4(),
        organization_id=organization_id,
        topic="Productividad para autónomos",
        niche="Negocios",
        target_audience="Autónomos que empiezan",
        language="español",
        style="cercano y práctico",
        target_pages=30,
        created_at=now,
        updated_at=now,
    )


async def test_run_pipeline_completes_all_stages(db_session: AsyncSession) -> None:
    org = await _create_organization(db_session)
    books = SqlAlchemyBookRepository(db_session)
    chapters = SqlAlchemyChapterRepository(db_session)
    book = await books.create(_new_book(org.id))

    service = BookGenerationService(books, chapters, FakeBookContentGenerator(chapter_count=3))
    result = await service.run_pipeline(book)

    assert result.status == BookStatus.READY
    assert result.generation_stage == GenerationStage.DONE
    assert result.error_message is None
    assert result.title is not None
    assert result.subtitle is not None
    assert result.market_research is not None
    assert result.market_research["summary"]
    assert result.sales_blurb is not None
    assert result.seo_keywords
    assert result.categories
    assert result.cover_brief is not None

    chapter_list = await chapters.list_for_book(book.id)
    assert len(chapter_list) == 3
    assert all(c.status == ChapterStatus.EDITED for c in chapter_list)
    assert all(c.content is not None and c.word_count > 0 for c in chapter_list)
    assert [c.order for c in chapter_list] == [1, 2, 3]


async def test_run_pipeline_preserves_progress_on_failure(db_session: AsyncSession) -> None:
    org = await _create_organization(db_session)
    books = SqlAlchemyBookRepository(db_session)
    chapters = SqlAlchemyChapterRepository(db_session)
    book = await books.create(_new_book(org.id))

    generator = FakeBookContentGenerator(chapter_count=2, fail_at="sales_copy")
    service = BookGenerationService(books, chapters, generator)
    result = await service.run_pipeline(book)

    assert result.status == BookStatus.FAILED
    assert result.error_message is not None
    # El trabajo de las etapas previas (título, esquema, capítulos) no se pierde.
    assert result.title is not None
    chapter_list = await chapters.list_for_book(book.id)
    assert len(chapter_list) == 2
    assert all(c.status == ChapterStatus.EDITED for c in chapter_list)
    # La etapa que falló nunca llegó a completarse.
    assert result.sales_blurb is None
