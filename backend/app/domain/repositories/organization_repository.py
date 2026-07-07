from typing import Protocol
from uuid import UUID

from app.domain.entities.organization import Organization


class OrganizationRepository(Protocol):
    """Puerto (interfaz) para persistir organizaciones.

    El dominio depende de esta interfaz, no de una implementación concreta.
    `app/infrastructure/database/repositories/` contiene la implementación
    real sobre SQLAlchemy/PostgreSQL.
    """

    async def get_by_id(self, organization_id: UUID) -> Organization | None: ...

    async def create(self, organization: Organization) -> Organization: ...
