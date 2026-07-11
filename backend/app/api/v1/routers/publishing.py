from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_user,
    get_db_session,
    get_ebook_exporter,
    get_publishing_connector_registry,
)
from app.api.v1.schemas.publishing import (
    ConnectAccountRequest,
    DashboardSummaryResponse,
    MarkPublicationLiveRequest,
    PreparePublicationRequest,
    PublicationResponse,
    PublishingAccountResponse,
    RejectPublicationRequest,
    SalesRecordRequest,
    SalesRecordResponse,
    UpdatePublicationMetadataRequest,
)
from app.application.services.export_service import ExportService
from app.application.services.publishing_service import DashboardSummary, PublishingService
from app.core.config import get_settings
from app.domain.entities.publishing import Publication, PublishingAccount, SalesRecord
from app.domain.entities.user import User
from app.domain.ports.ebook_exporter import EbookExporter
from app.infrastructure.database.repositories.book_repository import SqlAlchemyBookRepository
from app.infrastructure.database.repositories.chapter_repository import (
    SqlAlchemyChapterRepository,
)
from app.infrastructure.database.repositories.publication_repository import (
    SqlAlchemyPublicationRepository,
)
from app.infrastructure.database.repositories.publishing_account_repository import (
    SqlAlchemyPublishingAccountRepository,
)
from app.infrastructure.database.repositories.sales_record_repository import (
    SqlAlchemySalesRecordRepository,
)
from app.infrastructure.external.publishing.registry import PublishingConnectorRegistry

router = APIRouter()


def _get_publishing_service(
    session: AsyncSession = Depends(get_db_session),
    exporter: EbookExporter = Depends(get_ebook_exporter),
    connectors: PublishingConnectorRegistry = Depends(get_publishing_connector_registry),
) -> PublishingService:
    return PublishingService(
        accounts=SqlAlchemyPublishingAccountRepository(session),
        publications=SqlAlchemyPublicationRepository(session),
        sales_records=SqlAlchemySalesRecordRepository(session),
        books=SqlAlchemyBookRepository(session),
        chapters=SqlAlchemyChapterRepository(session),
        export_service=ExportService(
            books=SqlAlchemyBookRepository(session),
            chapters=SqlAlchemyChapterRepository(session),
            exporter=exporter,
            uploads_dir=get_settings().uploads_dir,
        ),
        get_connector=connectors.get,
    )


# ---- Cuentas conectadas ------------------------------------------------


@router.post(
    "/publishing/accounts",
    response_model=PublishingAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
async def connect_account(
    payload: ConnectAccountRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> PublishingAccountResponse:
    account = await publishing_service.connect_account(
        organization_id=current_user.organization_id,
        platform=payload.platform,
        display_name=payload.display_name,
        notes=payload.notes,
    )
    await session.commit()
    return _account_to_response(account)


@router.get("/publishing/accounts", response_model=list[PublishingAccountResponse])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> list[PublishingAccountResponse]:
    accounts = await publishing_service.list_accounts(current_user.organization_id)
    return [_account_to_response(a) for a in accounts]


@router.get("/publishing/dashboard", response_model=DashboardSummaryResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> DashboardSummaryResponse:
    summary = await publishing_service.dashboard_summary(current_user.organization_id)
    return _summary_to_response(summary)


# ---- Publicaciones -------------------------------------------------------


@router.post(
    "/books/{book_id}/publications",
    response_model=PublicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def prepare_publication(
    book_id: UUID,
    payload: PreparePublicationRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> PublicationResponse:
    publication = await publishing_service.prepare_publication(
        book_id=book_id,
        organization_id=current_user.organization_id,
        account_id=payload.publishing_account_id,
        metadata=payload.metadata,
    )
    await session.commit()
    return _publication_to_response(publication)


@router.get("/books/{book_id}/publications", response_model=list[PublicationResponse])
async def list_publications_for_book(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> list[PublicationResponse]:
    publications = await publishing_service.list_for_book(book_id, current_user.organization_id)
    return [_publication_to_response(p) for p in publications]


@router.get("/publications/{publication_id}", response_model=PublicationResponse)
async def get_publication(
    publication_id: UUID,
    current_user: User = Depends(get_current_user),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> PublicationResponse:
    publication = await publishing_service.get_publication(
        publication_id, current_user.organization_id
    )
    return _publication_to_response(publication)


@router.patch("/publications/{publication_id}", response_model=PublicationResponse)
async def update_publication_metadata(
    publication_id: UUID,
    payload: UpdatePublicationMetadataRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> PublicationResponse:
    publication = await publishing_service.update_metadata(
        publication_id, current_user.organization_id, payload.metadata
    )
    await session.commit()
    return _publication_to_response(publication)


@router.post("/publications/{publication_id}/request-review", response_model=PublicationResponse)
async def request_review(
    publication_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> PublicationResponse:
    publication = await publishing_service.request_review(
        publication_id, current_user.organization_id
    )
    await session.commit()
    return _publication_to_response(publication)


@router.post("/publications/{publication_id}/approve", response_model=PublicationResponse)
async def approve_publication(
    publication_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> PublicationResponse:
    publication = await publishing_service.approve(publication_id, current_user.organization_id)
    await session.commit()
    return _publication_to_response(publication)


@router.post("/publications/{publication_id}/reject", response_model=PublicationResponse)
async def reject_publication(
    publication_id: UUID,
    payload: RejectPublicationRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> PublicationResponse:
    publication = await publishing_service.reject(
        publication_id, current_user.organization_id, payload.reason
    )
    await session.commit()
    return _publication_to_response(publication)


@router.post("/publications/{publication_id}/submit", response_model=PublicationResponse)
async def submit_publication(
    publication_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> PublicationResponse:
    publication = await publishing_service.submit(publication_id, current_user.organization_id)
    await session.commit()
    return _publication_to_response(publication)


@router.post("/publications/{publication_id}/mark-live", response_model=PublicationResponse)
async def mark_publication_live(
    publication_id: UUID,
    payload: MarkPublicationLiveRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> PublicationResponse:
    publication = await publishing_service.mark_live(
        publication_id, current_user.organization_id, payload.external_book_id
    )
    await session.commit()
    return _publication_to_response(publication)


@router.post("/publications/{publication_id}/sync", response_model=PublicationResponse)
async def sync_publication_status(
    publication_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> PublicationResponse:
    publication = await publishing_service.sync_status(publication_id, current_user.organization_id)
    await session.commit()
    return _publication_to_response(publication)


# ---- Ventas (manuales en este MVP, ver ADR 0014) ------------------------


@router.post(
    "/publications/{publication_id}/sales",
    response_model=SalesRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_sale_record(
    publication_id: UUID,
    payload: SalesRecordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> SalesRecordResponse:
    record = await publishing_service.add_sale_record(
        publication_id=publication_id,
        organization_id=current_user.organization_id,
        period_start=payload.period_start,
        period_end=payload.period_end,
        units_sold=payload.units_sold,
        revenue_amount=payload.revenue_amount,
        currency=payload.currency,
    )
    await session.commit()
    return _sales_record_to_response(record)


@router.get("/publications/{publication_id}/sales", response_model=list[SalesRecordResponse])
async def list_sales_records(
    publication_id: UUID,
    current_user: User = Depends(get_current_user),
    publishing_service: PublishingService = Depends(_get_publishing_service),
) -> list[SalesRecordResponse]:
    records = await publishing_service.list_sales_for_publication(
        publication_id, current_user.organization_id
    )
    return [_sales_record_to_response(r) for r in records]


def _account_to_response(account: PublishingAccount) -> PublishingAccountResponse:
    return PublishingAccountResponse(
        id=account.id,
        organization_id=account.organization_id,
        platform=account.platform.value,
        display_name=account.display_name,
        connection_status=account.connection_status.value,
        notes=account.notes,
        created_at=account.created_at,
    )


def _publication_to_response(publication: Publication) -> PublicationResponse:
    return PublicationResponse(
        id=publication.id,
        organization_id=publication.organization_id,
        book_id=publication.book_id,
        publishing_account_id=publication.publishing_account_id,
        platform=publication.platform.value,
        status=publication.status.value,
        metadata=publication.metadata,
        missing_metadata_fields=publication.missing_metadata_fields,
        instructions=publication.instructions,
        review_notes=publication.review_notes,
        external_book_id=publication.external_book_id,
        submitted_at=publication.submitted_at,
        published_at=publication.published_at,
        last_synced_at=publication.last_synced_at,
        created_at=publication.created_at,
        updated_at=publication.updated_at,
    )


def _sales_record_to_response(record: SalesRecord) -> SalesRecordResponse:
    return SalesRecordResponse(
        id=record.id,
        organization_id=record.organization_id,
        publication_id=record.publication_id,
        period_start=record.period_start,
        period_end=record.period_end,
        units_sold=record.units_sold,
        revenue_amount=record.revenue_amount,
        currency=record.currency,
        source=record.source,
        recorded_at=record.recorded_at,
    )


def _summary_to_response(summary: DashboardSummary) -> DashboardSummaryResponse:
    return DashboardSummaryResponse(
        total_books=summary.total_books,
        books_by_status=summary.books_by_status,
        total_publications=summary.total_publications,
        publications_by_status=summary.publications_by_status,
        total_units_sold=summary.total_units_sold,
        revenue_by_currency=summary.revenue_by_currency,
    )
