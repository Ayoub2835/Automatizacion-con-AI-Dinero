from typing import Protocol
from uuid import UUID

from app.domain.entities.publishing import PublishingAccount


class PublishingAccountRepository(Protocol):
    """Puerto (interfaz) para persistir cuentas de plataformas de venta conectadas."""

    async def create(self, account: PublishingAccount) -> PublishingAccount: ...

    async def get_by_id(
        self, account_id: UUID, organization_id: UUID
    ) -> PublishingAccount | None: ...

    async def list_for_organization(self, organization_id: UUID) -> list[PublishingAccount]: ...
