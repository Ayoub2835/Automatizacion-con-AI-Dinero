from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.api.v1.schemas.clients import ClientResponse, CreateClientRequest
from app.application.services.client_service import ClientService
from app.domain.entities.user import User
from app.infrastructure.database.repositories.client_repository import SqlAlchemyClientRepository

router = APIRouter()


def _get_client_service(session: AsyncSession = Depends(get_db_session)) -> ClientService:
    return ClientService(clients=SqlAlchemyClientRepository(session))


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: CreateClientRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    client_service: ClientService = Depends(_get_client_service),
) -> ClientResponse:
    client = await client_service.create(
        organization_id=current_user.organization_id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
    )
    await session.commit()
    return ClientResponse.model_validate(client, from_attributes=True)


@router.get("", response_model=list[ClientResponse])
async def list_clients(
    current_user: User = Depends(get_current_user),
    client_service: ClientService = Depends(_get_client_service),
) -> list[ClientResponse]:
    clients = await client_service.list_for_organization(current_user.organization_id)
    return [ClientResponse.model_validate(c, from_attributes=True) for c in clients]
