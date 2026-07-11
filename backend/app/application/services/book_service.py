from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.entities.book import Book, Chapter
from app.domain.exceptions import EntityNotFoundError
from app.domain.repositories.book_repository import BookRepository
from app.domain.repositories.chapter_repository import ChapterRepository


class BookService:
    """Casos de uso de gestión básica de libros (alta, consulta) — la
    generación de contenido en sí vive en BookGenerationService (ver ADR 0014).
    """

    def __init__(self, books: BookRepository, chapters: ChapterRepository) -> None:
        self._books = books
        self._chapters = chapters

    async def create(
        self,
        organization_id: UUID,
        topic: str,
        niche: str,
        target_audience: str,
        language: str,
        style: str,
        target_pages: int,
    ) -> Book:
        now = datetime.now(UTC)
        book = Book(
            id=uuid4(),
            organization_id=organization_id,
            topic=topic,
            niche=niche,
            target_audience=target_audience,
            language=language,
            style=style,
            target_pages=target_pages,
            created_at=now,
            updated_at=now,
        )
        return await self._books.create(book)

    async def get(self, book_id: UUID, organization_id: UUID) -> Book:
        book = await self._books.get_by_id(book_id, organization_id)
        if book is None:
            raise EntityNotFoundError(entity="Libro", identifier=str(book_id))
        return book

    async def list_for_organization(self, organization_id: UUID) -> list[Book]:
        return await self._books.list_for_organization(organization_id)

    async def get_chapters(self, book_id: UUID, organization_id: UUID) -> list[Chapter]:
        await self.get(book_id, organization_id)  # 404 si no existe o no es de esta organización
        return await self._chapters.list_for_book(book_id)
