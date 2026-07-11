from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.services.export_service import ExportService
from app.domain.entities.book import Book
from app.domain.entities.publishing import (
    Publication,
    PublicationStatus,
    PublishingAccount,
    PublishingPlatform,
    SalesRecord,
)
from app.domain.exceptions import EntityNotFoundError, InvalidStateTransitionError
from app.domain.ports.publishing_connector import PublishingConnector
from app.domain.repositories.book_repository import BookRepository
from app.domain.repositories.chapter_repository import ChapterRepository
from app.domain.repositories.publication_repository import PublicationRepository
from app.domain.repositories.publishing_account_repository import PublishingAccountRepository
from app.domain.repositories.sales_record_repository import SalesRecordRepository

_EDITABLE_STATUSES = {PublicationStatus.DRAFT, PublicationStatus.METADATA_READY}


@dataclass
class DashboardSummary:
    """Agregados para el panel (ver ADR 0014): libros/publicaciones por
    estado, unidades vendidas e ingresos por divisa (todo manual en este
    MVP, ver SalesRecord.source)."""

    total_books: int
    books_by_status: dict[str, int]
    total_publications: int
    publications_by_status: dict[str, int]
    total_units_sold: int
    revenue_by_currency: dict[str, float]


class PublishingService:
    """Casos de uso del Publishing Agent (ver ADR 0014): gestiona cuentas
    conectadas, prepara metadatos por plataforma, y aplica la máquina de
    estados de una Publication:

    DRAFT/METADATA_READY (según falten campos) → PENDING_REVIEW (revisión
    humana obligatoria) → APPROVED → SUBMITTED (enviado — automático si el
    conector lo soporta, asistido en caso contrario) → LIVE (confirmado).
    REJECTED es un estado terminal alcanzable desde PENDING_REVIEW.
    """

    def __init__(
        self,
        accounts: PublishingAccountRepository,
        publications: PublicationRepository,
        sales_records: SalesRecordRepository,
        books: BookRepository,
        chapters: ChapterRepository,
        export_service: ExportService,
        get_connector: Callable[[PublishingPlatform], PublishingConnector],
    ) -> None:
        self._accounts = accounts
        self._publications = publications
        self._sales_records = sales_records
        self._books = books
        self._chapters = chapters
        self._export_service = export_service
        self._get_connector = get_connector

    # ---- Cuentas -----------------------------------------------------

    async def connect_account(
        self,
        organization_id: UUID,
        platform: PublishingPlatform,
        display_name: str,
        notes: str | None = None,
    ) -> PublishingAccount:
        account = PublishingAccount(
            id=uuid4(),
            organization_id=organization_id,
            platform=platform,
            display_name=display_name,
            notes=notes,
            created_at=datetime.now(UTC),
        )
        return await self._accounts.create(account)

    async def list_accounts(self, organization_id: UUID) -> list[PublishingAccount]:
        return await self._accounts.list_for_organization(organization_id)

    # ---- Publicaciones -------------------------------------------------

    async def prepare_publication(
        self,
        book_id: UUID,
        organization_id: UUID,
        account_id: UUID,
        metadata: dict[str, str],
    ) -> Publication:
        book = await self._get_book(book_id, organization_id)
        account = await self._get_account(account_id, organization_id)
        connector = self._get_connector(account.platform)
        missing = _missing_fields(connector, metadata)

        publication = Publication(
            id=uuid4(),
            organization_id=organization_id,
            book_id=book.id,
            publishing_account_id=account.id,
            platform=account.platform,
            status=PublicationStatus.DRAFT if missing else PublicationStatus.METADATA_READY,
            metadata=metadata,
            missing_metadata_fields=missing,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        return await self._publications.create(publication)

    async def update_metadata(
        self, publication_id: UUID, organization_id: UUID, metadata: dict[str, str]
    ) -> Publication:
        publication = await self._get_publication(publication_id, organization_id)
        self._guard(publication, _EDITABLE_STATUSES, "editar metadatos de")

        connector = self._get_connector(publication.platform)
        merged = {**publication.metadata, **metadata}
        missing = _missing_fields(connector, merged)

        publication.metadata = merged
        publication.missing_metadata_fields = missing
        publication.status = (
            PublicationStatus.DRAFT if missing else PublicationStatus.METADATA_READY
        )
        return await self._publications.update(publication)

    async def request_review(self, publication_id: UUID, organization_id: UUID) -> Publication:
        publication = await self._get_publication(publication_id, organization_id)
        self._guard(publication, {PublicationStatus.METADATA_READY}, "enviar a revisión")
        publication.status = PublicationStatus.PENDING_REVIEW
        return await self._publications.update(publication)

    async def approve(self, publication_id: UUID, organization_id: UUID) -> Publication:
        publication = await self._get_publication(publication_id, organization_id)
        self._guard(publication, {PublicationStatus.PENDING_REVIEW}, "aprobar")
        publication.status = PublicationStatus.APPROVED
        return await self._publications.update(publication)

    async def reject(self, publication_id: UUID, organization_id: UUID, reason: str) -> Publication:
        publication = await self._get_publication(publication_id, organization_id)
        self._guard(publication, {PublicationStatus.PENDING_REVIEW}, "rechazar")
        publication.status = PublicationStatus.REJECTED
        publication.review_notes = reason
        return await self._publications.update(publication)

    async def submit(self, publication_id: UUID, organization_id: UUID) -> Publication:
        """Envía la publicación aprobada a la plataforma: automáticamente si
        el conector lo soporta, o generando un paquete de instrucciones para
        completar la subida a mano (ver PublishingConnector, ADR 0014)."""
        publication = await self._get_publication(publication_id, organization_id)
        self._guard(publication, {PublicationStatus.APPROVED}, "enviar a la plataforma de")

        book = await self._get_book(publication.book_id, organization_id)
        account = await self._get_account(publication.publishing_account_id, organization_id)
        chapters = await self._chapters.list_for_book(book.id)
        connector = self._get_connector(publication.platform)

        epub_bytes = await self._read_export(book.epub_storage_path)
        pdf_bytes = await self._read_export(book.pdf_storage_path)

        try:
            result = await connector.submit(
                book, chapters, account, publication, epub_bytes, pdf_bytes
            )
        except NotImplementedError as exc:
            publication.status = PublicationStatus.FAILED
            publication.review_notes = str(exc)
            return await self._publications.update(publication)

        publication.status = result.status
        publication.instructions = result.instructions
        if result.external_book_id:
            publication.external_book_id = result.external_book_id
        publication.submitted_at = datetime.now(UTC)
        return await self._publications.update(publication)

    async def mark_live(
        self, publication_id: UUID, organization_id: UUID, external_book_id: str | None
    ) -> Publication:
        """Confirmación manual de que la plataforma ya publicó el libro —
        necesaria porque ninguna de las plataformas soportadas notifica esto
        vía webhook en este MVP (ver ADR 0014)."""
        publication = await self._get_publication(publication_id, organization_id)
        self._guard(publication, {PublicationStatus.SUBMITTED}, "marcar como publicada")
        publication.status = PublicationStatus.LIVE
        publication.published_at = datetime.now(UTC)
        if external_book_id:
            publication.external_book_id = external_book_id
        return await self._publications.update(publication)

    async def sync_status(self, publication_id: UUID, organization_id: UUID) -> Publication:
        publication = await self._get_publication(publication_id, organization_id)
        account = await self._get_account(publication.publishing_account_id, organization_id)
        connector = self._get_connector(publication.platform)

        synced_status = await connector.fetch_status(account, publication)
        publication.last_synced_at = datetime.now(UTC)
        if synced_status is not None:
            publication.status = synced_status
        return await self._publications.update(publication)

    async def list_for_book(self, book_id: UUID, organization_id: UUID) -> list[Publication]:
        await self._get_book(book_id, organization_id)
        return await self._publications.list_for_book(book_id, organization_id)

    async def get_publication(self, publication_id: UUID, organization_id: UUID) -> Publication:
        return await self._get_publication(publication_id, organization_id)

    # ---- Ventas e ingresos (manual en este MVP) -------------------------

    async def add_sale_record(
        self,
        publication_id: UUID,
        organization_id: UUID,
        period_start: datetime,
        period_end: datetime,
        units_sold: int,
        revenue_amount: float,
        currency: str,
    ) -> SalesRecord:
        await self._get_publication(publication_id, organization_id)
        record = SalesRecord(
            id=uuid4(),
            organization_id=organization_id,
            publication_id=publication_id,
            period_start=period_start,
            period_end=period_end,
            units_sold=units_sold,
            revenue_amount=revenue_amount,
            currency=currency,
            source="manual",
            recorded_at=datetime.now(UTC),
        )
        return await self._sales_records.create(record)

    async def list_sales_for_publication(
        self, publication_id: UUID, organization_id: UUID
    ) -> list[SalesRecord]:
        await self._get_publication(publication_id, organization_id)
        return await self._sales_records.list_for_publication(publication_id, organization_id)

    # ---- Panel -----------------------------------------------------------

    async def dashboard_summary(self, organization_id: UUID) -> DashboardSummary:
        books = await self._books.list_for_organization(organization_id)
        publications = await self._publications.list_for_organization(organization_id)
        sales = await self._sales_records.list_for_organization(organization_id)

        revenue_by_currency: dict[str, float] = {}
        units_sold_total = 0
        for record in sales:
            revenue_by_currency[record.currency] = (
                revenue_by_currency.get(record.currency, 0.0) + record.revenue_amount
            )
            units_sold_total += record.units_sold

        return DashboardSummary(
            total_books=len(books),
            books_by_status=_count_by_status(b.status.value for b in books),
            total_publications=len(publications),
            publications_by_status=_count_by_status(p.status.value for p in publications),
            total_units_sold=units_sold_total,
            revenue_by_currency=revenue_by_currency,
        )

    # ---- Helpers -----------------------------------------------------

    async def _read_export(self, storage_path: str | None) -> bytes | None:
        if storage_path is None:
            return None
        return await self._export_service.read(storage_path)

    async def _get_book(self, book_id: UUID, organization_id: UUID) -> Book:
        book = await self._books.get_by_id(book_id, organization_id)
        if book is None:
            raise EntityNotFoundError(entity="Libro", identifier=str(book_id))
        return book

    async def _get_account(self, account_id: UUID, organization_id: UUID) -> PublishingAccount:
        account = await self._accounts.get_by_id(account_id, organization_id)
        if account is None:
            raise EntityNotFoundError(entity="Cuenta de publicación", identifier=str(account_id))
        return account

    async def _get_publication(self, publication_id: UUID, organization_id: UUID) -> Publication:
        publication = await self._publications.get_by_id(publication_id, organization_id)
        if publication is None:
            raise EntityNotFoundError(entity="Publicación", identifier=str(publication_id))
        return publication

    @staticmethod
    def _guard(publication: Publication, allowed: set[PublicationStatus], action: str) -> None:
        if publication.status not in allowed:
            raise InvalidStateTransitionError(
                entity="la publicación", from_state=publication.status.value, action=action
            )


def _missing_fields(connector: PublishingConnector, metadata: dict[str, str]) -> list[str]:
    return [field for field in connector.required_metadata_fields() if not metadata.get(field)]


def _count_by_status(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
