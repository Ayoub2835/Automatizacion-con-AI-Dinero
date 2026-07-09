from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session, get_email_sender
from app.api.v1.schemas.campaign_clients import CampaignClientResponse, SendCampaignRequest
from app.api.v1.schemas.campaigns import CampaignResponse, CreateCampaignRequest
from app.application.services.campaign_delivery_service import CampaignDeliveryService
from app.application.services.campaign_service import CampaignService
from app.core.config import get_settings
from app.domain.entities.user import User
from app.domain.ports.email_sender import EmailSender
from app.infrastructure.database.repositories.campaign_client_repository import (
    SqlAlchemyCampaignClientRepository,
)
from app.infrastructure.database.repositories.campaign_repository import (
    SqlAlchemyCampaignRepository,
)
from app.infrastructure.database.repositories.client_repository import SqlAlchemyClientRepository

router = APIRouter()


def _get_campaign_service(session: AsyncSession = Depends(get_db_session)) -> CampaignService:
    return CampaignService(campaigns=SqlAlchemyCampaignRepository(session))


def _get_delivery_service(
    session: AsyncSession = Depends(get_db_session),
    email_sender: EmailSender = Depends(get_email_sender),
) -> CampaignDeliveryService:
    return CampaignDeliveryService(
        campaign_clients=SqlAlchemyCampaignClientRepository(session),
        clients=SqlAlchemyClientRepository(session),
        email_sender=email_sender,
        frontend_url=get_settings().frontend_url,
    )


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CreateCampaignRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    campaign_service: CampaignService = Depends(_get_campaign_service),
) -> CampaignResponse:
    campaign = await campaign_service.create(
        organization_id=current_user.organization_id,
        name=payload.name,
        document_type_names=payload.document_types,
    )
    await session.commit()
    return CampaignResponse.model_validate(campaign, from_attributes=True)


@router.get("", response_model=list[CampaignResponse])
async def list_campaigns(
    current_user: User = Depends(get_current_user),
    campaign_service: CampaignService = Depends(_get_campaign_service),
) -> list[CampaignResponse]:
    campaigns = await campaign_service.list_for_organization(current_user.organization_id)
    return [CampaignResponse.model_validate(c, from_attributes=True) for c in campaigns]


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    campaign_service: CampaignService = Depends(_get_campaign_service),
) -> CampaignResponse:
    campaign = await campaign_service.get(campaign_id, current_user.organization_id)
    return CampaignResponse.model_validate(campaign, from_attributes=True)


@router.post(
    "/{campaign_id}/send",
    response_model=list[CampaignClientResponse],
    status_code=status.HTTP_201_CREATED,
)
async def send_campaign(
    campaign_id: UUID,
    payload: SendCampaignRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    campaign_service: CampaignService = Depends(_get_campaign_service),
    delivery_service: CampaignDeliveryService = Depends(_get_delivery_service),
) -> list[CampaignClientResponse]:
    """Asocia la campaña a los clientes indicados, genera su enlace seguro
    y envía el email de solicitud de documentación.

    Idempotente: un client_id ya asociado a la campaña se omite (no se
    duplica la fila ni se reenvía el email).
    """
    # Lanza 404 si la campaña no existe o no pertenece a esta organización.
    campaign = await campaign_service.get(campaign_id, current_user.organization_id)
    invites = await delivery_service.send_to_clients(campaign, payload.client_ids)
    await session.commit()

    return [
        CampaignClientResponse(
            id=invite.campaign_client.id,
            campaign_id=invite.campaign_client.campaign_id,
            client_id=invite.campaign_client.client_id,
            client_name=invite.client.name,
            client_email=invite.client.email,
            status=invite.campaign_client.status,
            upload_url=invite.upload_url,
            created_at=invite.campaign_client.created_at,
        )
        for invite in invites
    ]
