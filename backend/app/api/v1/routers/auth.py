from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.api.v1.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.application.services.auth_service import AuthService
from app.infrastructure.database.repositories.organization_repository import (
    SqlAlchemyOrganizationRepository,
)
from app.infrastructure.database.repositories.user_repository import SqlAlchemyUserRepository

router = APIRouter()


def _get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(
        users=SqlAlchemyUserRepository(session),
        organizations=SqlAlchemyOrganizationRepository(session),
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(_get_auth_service),
) -> UserResponse:
    """Crea una nueva organización (gestoría) junto con su usuario admin."""
    user = await auth_service.register(
        organization_name=payload.organization_name,
        email=payload.email,
        password=payload.password,
    )
    await session.commit()
    return UserResponse.model_validate(user, from_attributes=True)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(_get_auth_service),
) -> TokenResponse:
    tokens = await auth_service.authenticate(email=payload.email, password=payload.password)
    return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)
