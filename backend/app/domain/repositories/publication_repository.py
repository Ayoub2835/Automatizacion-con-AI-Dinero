from typing import Protocol
from uuid import UUID

from app.domain.entities.publishing import Publication


class PublicationRepository(Protocol):
    """Puerto (interfaz) para persistir intentos de publicación de un libro."""

    async def create(self, publication: Publication) -> Publication: ...

    async def update(self, publication: Publication) -> Publication: ...

    async def get_by_id(
        self, publication_id: UUID, organization_id: UUID
    ) -> Publication | None: ...

    async def list_for_book(self, book_id: UUID, organization_id: UUID) -> list[Publication]: ...

    async def list_for_organization(self, organization_id: UUID) -> list[Publication]: ...
