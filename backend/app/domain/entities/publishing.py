from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class PublishingPlatform(StrEnum):
    KDP = "kdp"
    APPLE_BOOKS = "apple_books"
    GOOGLE_PLAY_BOOKS = "google_play_books"
    KOBO = "kobo"


class AccountConnectionStatus(StrEnum):
    """Ninguna de las plataformas soportadas ofrece hoy un flujo OAuth
    público de autoservicio (ver ADR 0014), así que `CONNECTED` no se usa
    todavía en este MVP — existe para cuando un conector real (ej. Google
    Play Books Partner API) lo permita sin cambiar el modelo de datos."""

    MANUAL = "manual"
    CONNECTED = "connected"
    NEEDS_REAUTH = "needs_reauth"


class PublicationStatus(StrEnum):
    DRAFT = "draft"
    METADATA_READY = "metadata_ready"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    LIVE = "live"
    REJECTED = "rejected"
    FAILED = "failed"


@dataclass
class PublishingAccount:
    """Una cuenta de una plataforma de venta conectada a la organización.

    `credentials_ref` es una referencia opaca (ej. id de un secreto en un
    vault) — nunca se guardan credenciales en claro aquí. En este MVP,
    todas las cuentas son `MANUAL` (ver AccountConnectionStatus).
    """

    id: UUID
    organization_id: UUID
    platform: PublishingPlatform
    display_name: str
    created_at: datetime
    connection_status: AccountConnectionStatus = AccountConnectionStatus.MANUAL
    credentials_ref: str | None = None
    notes: str | None = None


@dataclass
class Publication:
    """El intento de publicar un Book concreto en una PublishingAccount
    concreta. Ver ADR 0014 para la máquina de estados completa."""

    id: UUID
    organization_id: UUID
    book_id: UUID
    publishing_account_id: UUID
    platform: PublishingPlatform
    created_at: datetime
    updated_at: datetime
    status: PublicationStatus = PublicationStatus.DRAFT
    metadata: dict[str, Any] = field(default_factory=dict)
    missing_metadata_fields: list[str] = field(default_factory=list)
    instructions: str | None = None
    review_notes: str | None = None
    external_book_id: str | None = None
    submitted_at: datetime | None = None
    published_at: datetime | None = None
    last_synced_at: datetime | None = None


@dataclass
class SalesRecord:
    """Ventas/ingresos de una Publication en un periodo dado.

    `source` distingue una fila introducida a mano (todas en este MVP, ver
    ADR 0014) de una sincronizada por API cuando exista esa integración.
    """

    id: UUID
    organization_id: UUID
    publication_id: UUID
    period_start: datetime
    period_end: datetime
    units_sold: int
    revenue_amount: float
    currency: str
    source: str
    recorded_at: datetime
