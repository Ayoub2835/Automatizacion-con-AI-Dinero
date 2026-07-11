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


class KdpConnector(ManualAssistedConnector):
    """Amazon Kindle Direct Publishing no ofrece una API pública de
    publicación para autores independientes, y sus términos de servicio
    prohíben automatizar la subida por scraping/RPA — este conector es
    manual/asistido de forma **permanente**, no una limitación temporal
    del MVP (ver ADR 0014). Si Amazon abriera en el futuro un programa de
    partners con API real, la sustitución es una nueva clase que implemente
    el mismo puerto `PublishingConnector`, sin tocar PublishingService.
    """

    def __init__(self) -> None:
        super().__init__(
            platform=PublishingPlatform.KDP,
            required_fields=_REQUIRED_FIELDS,
            upload_url="https://kdp.amazon.com/bookshelf",
            notes=(
                "Formatos aceptados para el interior: EPUB o DOCX (vía Kindle "
                "Create); portada en JPG/TIFF. Máximo 7 palabras clave y 2 "
                "categorías BISAC en el formulario de KDP."
            ),
        )
