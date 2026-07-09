from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.api.v1.schemas.public import (
    PublicCampaignStatusResponse,
    PublicDocumentResponse,
    PublicDocumentTypeStatusResponse,
)
from app.application.services.document_status import compute_document_type_statuses
from app.application.services.public_campaign_service import PublicCampaignService
from app.core.config import get_settings
from app.domain.entities.campaign import Campaign
from app.domain.entities.campaign_client import CampaignClient
from app.domain.entities.document import Document
from app.infrastructure.database.repositories.campaign_client_repository import (
    SqlAlchemyCampaignClientRepository,
)
from app.infrastructure.database.repositories.campaign_repository import (
    SqlAlchemyCampaignRepository,
)
from app.infrastructure.database.repositories.document_repository import (
    SqlAlchemyDocumentRepository,
)
from app.infrastructure.external.local_file_storage import LocalFileStorage

router = APIRouter()

# Solo se admiten los formatos que Claude puede clasificar de forma fiable
# en este MVP (ver ADR 0011). Ampliar la lista es una decisión deliberada,
# no un descuido.
_ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}
_MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024


def _get_public_campaign_service(
    session: AsyncSession = Depends(get_db_session),
) -> PublicCampaignService:
    return PublicCampaignService(
        campaign_clients=SqlAlchemyCampaignClientRepository(session),
        campaigns=SqlAlchemyCampaignRepository(session),
        documents=SqlAlchemyDocumentRepository(session),
        file_storage=LocalFileStorage(get_settings().uploads_dir),
    )


def _to_status_response(
    campaign: Campaign, campaign_client: CampaignClient, documents: list[Document]
) -> PublicCampaignStatusResponse:
    types_by_id = {t.id: t.name for t in campaign.document_types}
    document_type_statuses = compute_document_type_statuses(campaign, documents)
    return PublicCampaignStatusResponse(
        campaign_name=campaign.name,
        client_status=campaign_client.status,
        document_types=[
            PublicDocumentTypeStatusResponse(name=s.name, satisfied=s.satisfied)
            for s in document_type_statuses
        ],
        documents=[
            PublicDocumentResponse(
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


@router.get("/campaigns/{token}", response_model=PublicCampaignStatusResponse)
async def get_public_campaign_status(
    token: str,
    service: PublicCampaignService = Depends(_get_public_campaign_service),
) -> PublicCampaignStatusResponse:
    campaign, campaign_client, documents = await service.get_status(token)
    return _to_status_response(campaign, campaign_client, documents)


@router.post(
    "/campaigns/{token}/documents",
    response_model=PublicCampaignStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_public_document(
    token: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
    service: PublicCampaignService = Depends(_get_public_campaign_service),
) -> PublicCampaignStatusResponse:
    """Sube un documento para el enlace seguro `token`.

    Validación de formato/tamaño a nivel de transporte (HTTPException, no
    excepción de dominio): son restricciones de la petición HTTP en sí, no
    reglas de negocio.
    """
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato no admitido (solo PDF, JPG o PNG)",
        )

    content = await file.read()
    if len(content) > _MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="El fichero supera el tamaño máximo permitido (15 MB)",
        )

    await service.upload_document(
        token=token,
        filename=file.filename or "documento",
        content_type=file.content_type,
        content=content,
    )
    await session.commit()

    campaign, campaign_client, documents = await service.get_status(token)
    return _to_status_response(campaign, campaign_client, documents)
