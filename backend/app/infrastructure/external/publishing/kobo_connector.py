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


class KoboConnector(ManualAssistedConnector):
    """Kobo Writing Life (el portal de autopublicación de Rakuten Kobo) no
    ofrece una API pública de publicación — es un panel web manual. Este
    conector se mantiene manual/asistido de forma permanente en este MVP
    (ver ADR 0014).
    """

    def __init__(self) -> None:
        super().__init__(
            platform=PublishingPlatform.KOBO,
            required_fields=_REQUIRED_FIELDS,
            upload_url="https://www.kobo.com/writinglife",
            notes="Formato aceptado para el interior: EPUB; portada en JPG/PNG.",
        )
