import asyncio
from pathlib import Path
from uuid import UUID

from app.domain.entities.book import Book, BookStatus
from app.domain.exceptions import InvalidStateTransitionError
from app.domain.ports.ebook_exporter import EbookExporter
from app.domain.repositories.book_repository import BookRepository
from app.domain.repositories.chapter_repository import ChapterRepository

_EXPORTABLE_STATUSES = {BookStatus.READY, BookStatus.EXPORTED}


class ExportService:
    """Genera los ficheros EPUB/PDF finales de un libro y los guarda en disco
    local (mismo patrón que LocalFileStorage, ver ADR 0010 y ADR 0014)."""

    def __init__(
        self,
        books: BookRepository,
        chapters: ChapterRepository,
        exporter: EbookExporter,
        uploads_dir: str,
    ) -> None:
        self._books = books
        self._chapters = chapters
        self._exporter = exporter
        self._base_dir = Path(uploads_dir) / "books"

    async def export_book(self, book: Book) -> Book:
        if book.status not in _EXPORTABLE_STATUSES:
            raise InvalidStateTransitionError(
                entity="el libro", from_state=book.status.value, action="exportar"
            )

        chapters = await self._chapters.list_for_book(book.id)

        epub_bytes = await asyncio.to_thread(self._exporter.export_epub, book, chapters)
        pdf_bytes = await asyncio.to_thread(self._exporter.export_pdf, book, chapters)

        book.epub_storage_path = await self._save(book.id, "book.epub", epub_bytes)
        book.pdf_storage_path = await self._save(book.id, "book.pdf", pdf_bytes)
        book.status = BookStatus.EXPORTED
        return await self._books.update(book)

    async def read(self, storage_path: str) -> bytes:
        full_path = self._base_dir / storage_path
        return await asyncio.to_thread(full_path.read_bytes)

    async def _save(self, book_id: UUID, filename: str, content: bytes) -> str:
        relative_path = Path(str(book_id)) / filename
        full_path = self._base_dir / relative_path

        def _write() -> None:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_bytes(content)

        await asyncio.to_thread(_write)
        return str(relative_path)
