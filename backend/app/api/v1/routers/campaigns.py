from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session, get_email_sender
from app.api.v1.schemas.campaign_clients import CampaignClientResponse, SendCampaignRequest
from app.api.v1.schemas.campaign_status import (
    CampaignClientStatusResponse,
    CampaignStatusDocumentResponse,
    CampaignStatusDocumentTypeResponse,
    CampaignStatusResponse,
)
from app.api.v1.schemas.campaigns import CampaignResponse, CreateCampaignRequest
from app.application.services.campaign_delivery_service import CampaignDeliveryService
from app.application.services.campaign_service import CampaignService
from app.application.services.campaign_status_service import CampaignStatusService
from app.application.services.document_status import compute_document_type_statuses
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
from app.infrastructure.database.repositories.document_repository import (
    SqlAlchemyDocumentRepository,
)

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


def _get_status_service(
    session: AsyncSession = Depends(get_db_session),
) -> CampaignStatusService:
    return CampaignStatusService(
        campaigns=SqlAlchemyCampaignRepository(session),
        campaign_clients=SqlAlchemyCampaignClientRepository(session),
        clients=SqlAlchemyClientRepository(session),
        documents=SqlAlchemyDocumentRepository(session),
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


@router.get("/{campaign_id}/status", response_model=CampaignStatusResponse)
async def get_campaign_status(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    status_service: CampaignStatusService = Depends(_get_status_service),
) -> CampaignStatusResponse:
    """Panel del gestor: por cada cliente al que se envió la campaña, su
    estado (completo/pendiente), documentos recibidos y tipos que faltan.
    """
    campaign, rows = await status_service.get_status(campaign_id, current_user.organization_id)
    types_by_id = {t.id: t.name for t in campaign.document_types}

    clients_response = []
    for campaign_client, client, documents in rows:
        document_type_statuses = compute_document_type_statuses(campaign, documents)
        clients_response.append(
            CampaignClientStatusResponse(
                campaign_client_id=campaign_client.id,
                client_id=client.id,
                client_name=client.name,
                client_email=client.email,
                status=campaign_client.status,
                document_types=[
                    CampaignStatusDocumentTypeResponse(name=s.name, satisfied=s.satisfied)
                    for s in document_type_statuses
                ],
                documents=[
                    CampaignStatusDocumentResponse(
                        id=d.id,
                        original_filename=d.original_filename,
                        document_type_name=(
                            types_by_id.get(d.campaign_document_type_id)
                            if d.campaign_document_type_id
                            else None
                        ),
                        status=d.status,
                        uploaded_at=d.uploaded_at,
                    )
                    for d in documents
                ],
            )
        )

    return CampaignStatusResponse(
        campaign_id=campaign.id,
        campaign_name=campaign.name,
        clients=clients_response,
    )
