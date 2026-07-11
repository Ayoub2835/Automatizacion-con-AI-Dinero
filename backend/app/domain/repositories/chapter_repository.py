from typing import Protocol
from uuid import UUID

from app.domain.entities.book import Chapter


class ChapterRepository(Protocol):
    """Puerto (interfaz) para persistir los capítulos de un libro."""

    async def replace_outline(self, book_id: UUID, chapters: list[Chapter]) -> list[Chapter]:
        """Sustituye el esquema de capítulos de un libro (etapa OUTLINE).

        Solo se usa una vez por libro en el pipeline actual, así que un
        reemplazo completo es más simple que un diff — no hay regeneración
        parcial de esquema en este MVP.
        """
        ...

    async def update(self, chapter: Chapter) -> Chapter: ...

    async def list_for_book(self, book_id: UUID) -> list[Chapter]: ...
