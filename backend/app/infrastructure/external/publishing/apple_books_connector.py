from app.domain.entities.publishing import PublishingPlatform
from app.infrastructure.external.publishing.manual_assisted import ManualAssistedConnector

_REQUIRED_FIELDS = [
    "title",
    "subtitle",
    "description",
    "keywords",
    "categories",
    "price",
]


class AppleBooksConnector(ManualAssistedConnector):
    """Apple Books no ofrece una API REST pública para que autores
    independientes suban libros mediante integración directa: el camino
    oficial es Apple Books for Authors (panel web) o iTunes Producer
    (herramienta de empaquetado de escritorio, sin API HTTP). Este conector
    se mantiene manual/asistido de forma permanente en este MVP (ver ADR
    0014); revisar si Apple abre en el futuro una API de partners.
    """

    def __init__(self) -> None:
        super().__init__(
            platform=PublishingPlatform.APPLE_BOOKS,
            required_fields=_REQUIRED_FIELDS,
            upload_url="https://authors.apple.com",
            notes=(
                "El interior se empaqueta como EPUB válido (Apple valida "
                "estrictamente el EPUB); portada en JPEG mínimo 1400x1873px."
            ),
        )
