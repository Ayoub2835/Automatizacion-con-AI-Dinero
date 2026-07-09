from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.api.v1.schemas.campaigns import CampaignResponse, CreateCampaignRequest
from app.application.services.campaign_service import CampaignService
from app.domain.entities.user import User
from app.infrastructure.database.repositories.campaign_repository import (
    SqlAlchemyCampaignRepository,
)

router = APIRouter()


def _get_campaign_service(session: AsyncSession = Depends(get_db_session)) -> CampaignService:
    return CampaignService(campaigns=SqlAlchemyCampaignRepository(session))


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
