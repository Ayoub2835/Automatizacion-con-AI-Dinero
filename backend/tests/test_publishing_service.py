from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.export_service import ExportService
from app.application.services.publishing_service import PublishingService
from app.domain.entities.book import Book
from app.domain.entities.organization import Organization
from app.domain.entities.publishing import PublicationStatus, PublishingPlatform
from app.domain.exceptions import InvalidStateTransitionError
from app.infrastructure.database.repositories.book_repository import SqlAlchemyBookRepository
from app.infrastructure.database.repositories.chapter_repository import (
    SqlAlchemyChapterRepository,
)
from app.infrastructure.database.repositories.organization_repository import (
    SqlAlchemyOrganizationRepository,
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
from app.infrastructure.external.ebook_exporter import EbookLibExporter
from app.infrastructure.external.publishing.registry import PublishingConnectorRegistry

_FULL_KDP_METADATA = {
    "title": "Cocina rápida",
    "subtitle": "30 recetas",
    "description": "Un libro de cocina.",
    "keywords": "cocina, recetas, rápido",
    "categories": "Gastronomía",
    "price": "4.99",
}


async def _build_service(session: AsyncSession, tmp_path: Path) -> PublishingService:
    registry = PublishingConnectorRegistry()
    return PublishingService(
        accounts=SqlAlchemyPublishingAccountRepository(session),
        publications=SqlAlchemyPublicationRepository(session),
        sales_records=SqlAlchemySalesRecordRepository(session),
        books=SqlAlchemyBookRepository(session),
        chapters=SqlAlchemyChapterRepository(session),
        export_service=ExportService(
            books=SqlAlchemyBookRepository(session),
            chapters=SqlAlchemyChapterRepository(session),
            exporter=EbookLibExporter(),
            uploads_dir=str(tmp_path),
        ),
        get_connector=registry.get,
    )


async def _create_book(session: AsyncSession) -> Book:
    organizations = SqlAlchemyOrganizationRepository(session)
    org = await organizations.create(
        Organization(id=uuid4(), name="Editorial de prueba", created_at=datetime.now(UTC))
    )
    books = SqlAlchemyBookRepository(session)
    now = datetime.now(UTC)
    return await books.create(
        Book(
            id=uuid4(),
            organization_id=org.id,
            topic="Cocina rápida",
            niche="Gastronomía",
            target_audience="Gente ocupada",
            language="español",
            style="directo",
            target_pages=20,
            created_at=now,
            updated_at=now,
        )
    )


async def test_prepare_publication_flags_missing_fields(
    db_session: AsyncSession, tmp_path: Path
) -> None:
    service = await _build_service(db_session, tmp_path)
    book = await _create_book(db_session)
    account = await service.connect_account(
        book.organization_id, PublishingPlatform.KDP, "Cuenta KDP de prueba"
    )

    publication = await service.prepare_publication(
        book.id, book.organization_id, account.id, metadata={"title": "Cocina rápida"}
    )

    assert publication.status == PublicationStatus.DRAFT
    assert "price" in publication.missing_metadata_fields


async def test_full_lifecycle_to_live_with_manual_connector(
    db_session: AsyncSession, tmp_path: Path
) -> None:
    service = await _build_service(db_session, tmp_path)
    book = await _create_book(db_session)
    account = await service.connect_account(
        book.organization_id, PublishingPlatform.KDP, "Cuenta KDP de prueba"
    )

    publication = await service.prepare_publication(
        book.id, book.organization_id, account.id, metadata=_FULL_KDP_METADATA
    )
    assert publication.status == PublicationStatus.METADATA_READY
    assert publication.missing_metadata_fields == []

    publication = await service.request_review(publication.id, book.organization_id)
    assert publication.status == PublicationStatus.PENDING_REVIEW

    publication = await service.approve(publication.id, book.organization_id)
    assert publication.status == PublicationStatus.APPROVED

    # KDP no tiene API pública: el envío queda en modo asistido (ver ADR 0014).
    publication = await service.submit(publication.id, book.organization_id)
    assert publication.status == PublicationStatus.SUBMITTED
    assert publication.instructions is not None
    assert publication.submitted_at is not None

    publication = await service.mark_live(
        publication.id, book.organization_id, external_book_id="B0EXTERNAL123"
    )
    assert publication.status == PublicationStatus.LIVE
    assert publication.external_book_id == "B0EXTERNAL123"
    assert publication.published_at is not None


async def test_cannot_approve_publication_that_was_never_sent_to_review(
    db_session: AsyncSession, tmp_path: Path
) -> None:
    service = await _build_service(db_session, tmp_path)
    book = await _create_book(db_session)
    account = await service.connect_account(
        book.organization_id, PublishingPlatform.KOBO, "Cuenta Kobo de prueba"
    )
    publication = await service.prepare_publication(
        book.id, book.organization_id, account.id, metadata=_FULL_KDP_METADATA
    )

    with pytest.raises(InvalidStateTransitionError):
        await service.approve(publication.id, book.organization_id)


async def test_reject_publication_from_pending_review(
    db_session: AsyncSession, tmp_path: Path
) -> None:
    service = await _build_service(db_session, tmp_path)
    book = await _create_book(db_session)
    account = await service.connect_account(
        book.organization_id, PublishingPlatform.APPLE_BOOKS, "Cuenta Apple de prueba"
    )
    publication = await service.prepare_publication(
        book.id, book.organization_id, account.id, metadata=_FULL_KDP_METADATA
    )
    publication = await service.request_review(publication.id, book.organization_id)

    publication = await service.reject(
        publication.id, book.organization_id, reason="Portada de baja calidad"
    )
    assert publication.status == PublicationStatus.REJECTED
    assert publication.review_notes == "Portada de baja calidad"


async def test_dashboard_summary_aggregates_sales(db_session: AsyncSession, tmp_path: Path) -> None:
    service = await _build_service(db_session, tmp_path)
    book = await _create_book(db_session)
    account = await service.connect_account(
        book.organization_id, PublishingPlatform.GOOGLE_PLAY_BOOKS, "Cuenta Google Play"
    )
    publication = await service.prepare_publication(
        book.id, book.organization_id, account.id, metadata=_FULL_KDP_METADATA
    )

    await service.add_sale_record(
        publication.id,
        book.organization_id,
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 1, 31, tzinfo=UTC),
        units_sold=10,
        revenue_amount=39.9,
        currency="EUR",
    )
    await service.add_sale_record(
        publication.id,
        book.organization_id,
        period_start=datetime(2026, 2, 1, tzinfo=UTC),
        period_end=datetime(2026, 2, 28, tzinfo=UTC),
        units_sold=5,
        revenue_amount=19.95,
        currency="EUR",
    )

    summary = await service.dashboard_summary(book.organization_id)

    assert summary.total_books == 1
    assert summary.total_publications == 1
    assert summary.total_units_sold == 15
    assert summary.revenue_by_currency["EUR"] == pytest.approx(59.85)
    assert summary.publications_by_status[PublicationStatus.METADATA_READY.value] == 1
