from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User, UserRole
from app.infrastructure.database.models.user import UserModel


class SqlAlchemyUserRepository:
    """Implementación concreta de UserRepository sobre SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            organization_id=user.organization_id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role,
            metadata_=user.metadata,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            organization_id=model.organization_id,
            email=model.email,
            hashed_password=model.hashed_password,
            role=UserRole(model.role),
            created_at=model.created_at,
            metadata=model.metadata_,
        )
