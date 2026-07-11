from typing import Protocol
from uuid import UUID

from app.domain.entities.book import Book


class BookRepository(Protocol):
    """Puerto (interfaz) para persistir libros."""

    async def create(self, book: Book) -> Book: ...

    async def update(self, book: Book) -> Book: ...

    async def get_by_id(self, book_id: UUID, organization_id: UUID) -> Book | None: ...

    async def list_for_organization(self, organization_id: UUID) -> list[Book]: ...
