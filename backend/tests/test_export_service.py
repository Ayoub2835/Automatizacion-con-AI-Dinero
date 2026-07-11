from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.export_service import ExportService
from app.domain.entities.book import Book, BookStatus, Chapter, ChapterStatus
from app.domain.entities.organization import Organization
from app.domain.exceptions import InvalidStateTransitionError
from app.infrastructure.database.repositories.book_repository import SqlAlchemyBookRepository
from app.infrastructure.database.repositories.chapter_repository import (
    SqlAlchemyChapterRepository,
)
from app.infrastructure.database.repositories.organization_repository import (
    SqlAlchemyOrganizationRepository,
)
from app.infrastructure.external.ebook_exporter import EbookLibExporter


async def _create_ready_book(session: AsyncSession) -> tuple[Book, list[Chapter]]:
    organizations = SqlAlchemyOrganizationRepository(session)
    org = await organizations.create(
        Organization(id=uuid4(), name="Editorial de prueba", created_at=datetime.now(UTC))
    )

    books = SqlAlchemyBookRepository(session)
    chapters = SqlAlchemyChapterRepository(session)
    now = datetime.now(UTC)
    book = await books.create(
        Book(
            id=uuid4(),
            organization_id=org.id,
            topic="Cocina rápida",
            niche="Gastronomía",
            target_audience="Gente ocupada",
            language="español",
            style="directo",
            target_pages=20,
            created_at=now,
            updated_at=now,
        )
    )
    book.title = "Cocina rápida para gente ocupada"
    book.subtitle = "30 recetas en menos de 20 minutos"
    book.sales_blurb = "Un libro para cocinar rico sin perder tiempo."
    book.status = BookStatus.READY
    book = await books.update(book)

    chapter_entities = [
        Chapter(
            id=uuid4(),
            book_id=book.id,
            order=1,
            title="Desayunos",
            summary="Recetas rápidas de desayuno",
            content="Contenido del capítulo de desayunos.\n\nSegundo párrafo.",
            word_count=6,
            status=ChapterStatus.EDITED,
            created_at=now,
            updated_at=now,
        )
    ]
    created_chapters = await chapters.replace_outline(book.id, chapter_entities)
    for chapter in created_chapters:
        chapter.content = chapter_entities[0].content
        chapter.word_count = chapter_entities[0].word_count
        chapter.status = ChapterStatus.EDITED
        await chapters.update(chapter)

    return book, created_chapters


async def test_export_book_generates_epub_and_pdf(db_session: AsyncSession, tmp_path: Path) -> None:
    book, _ = await _create_ready_book(db_session)
    books = SqlAlchemyBookRepository(db_session)
    chapters = SqlAlchemyChapterRepository(db_session)
    service = ExportService(
        books=books,
        chapters=chapters,
        exporter=EbookLibExporter(),
        uploads_dir=str(tmp_path),
    )

    result = await service.export_book(book)

    assert result.status == BookStatus.EXPORTED
    assert result.epub_storage_path is not None
    assert result.pdf_storage_path is not None

    epub_bytes = await service.read(result.epub_storage_path)
    pdf_bytes = await service.read(result.pdf_storage_path)
    assert epub_bytes.startswith(b"PK")  # firma de fichero ZIP (EPUB es un ZIP)
    assert pdf_bytes.startswith(b"%PDF")


async def test_export_book_rejects_book_not_ready(db_session: AsyncSession, tmp_path: Path) -> None:
    organizations = SqlAlchemyOrganizationRepository(db_session)
    org = await organizations.create(
        Organization(id=uuid4(), name="Editorial de prueba", created_at=datetime.now(UTC))
    )
    books = SqlAlchemyBookRepository(db_session)
    chapters = SqlAlchemyChapterRepository(db_session)
    now = datetime.now(UTC)
    book = await books.create(
        Book(
            id=uuid4(),
            organization_id=org.id,
            topic="Tema",
            niche="Nicho",
            target_audience="Público",
            language="español",
            style="neutro",
            target_pages=20,
            created_at=now,
            updated_at=now,
        )
    )
    service = ExportService(
        books=books, chapters=chapters, exporter=EbookLibExporter(), uploads_dir=str(tmp_path)
    )

    with pytest.raises(InvalidStateTransitionError):
        await service.export_book(book)
