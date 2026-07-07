from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.domain.entities.organization import Organization
from app.domain.entities.user import User, UserRole
from app.domain.exceptions import AlreadyExistsError, InvalidCredentialsError
from app.domain.repositories.organization_repository import OrganizationRepository
from app.domain.repositories.user_repository import UserRepository


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthService:
    """Casos de uso de registro y autenticación.

    Nota de diseño: para esta base, cada repositorio hace `flush` (no
    `commit`) y es la capa de API quien decide cuándo confirmar la
    transacción. Si en el futuro un caso de uso necesita coordinar más de
    dos agregados, considerar introducir un patrón Unit of Work explícito
    en vez de seguir inyectando repositorios sueltos.
    """

    def __init__(self, users: UserRepository, organizations: OrganizationRepository) -> None:
        self._users = users
        self._organizations = organizations

    async def register(self, organization_name: str, email: str, password: str) -> User:
        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise AlreadyExistsError(entity="usuario", field="email", value=email)

        organization = await self._organizations.create(
            Organization(
                id=uuid4(),
                name=organization_name,
                created_at=datetime.now(UTC),
            )
        )

        user = User(
            id=uuid4(),
            organization_id=organization.id,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
            created_at=datetime.now(UTC),
        )
        return await self._users.create(user)

    async def authenticate(self, email: str, password: str) -> TokenPair:
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        return TokenPair(
            access_token=create_access_token(subject=str(user.id)),
            refresh_token=create_refresh_token(subject=str(user.id)),
        )
