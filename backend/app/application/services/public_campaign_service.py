import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.entities.campaign import Campaign
from app.domain.entities.campaign_client import CampaignClient
from app.domain.entities.document import Document, DocumentStatus
from app.domain.exceptions import EntityNotFoundError
from app.domain.ports.document_classifier import DocumentClassifier
from app.domain.ports.file_storage import FileStorage
from app.domain.repositories.campaign_client_repository import CampaignClientRepository
from app.domain.repositories.campaign_repository import CampaignRepository
from app.domain.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)

# Por debajo de esta confianza, el documento queda "sin clasificar" para que
# lo revise el gestor en vez de asignarlo a un tipo con dudas (ver ADR 0011).
_CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.6


class PublicCampaignService:
    """Casos de uso del flujo público (sin login): consultar el estado de una
    solicitud por su enlace seguro y subir documentos. Ver ADR 0008/0010/0011.
    """

    def __init__(
        self,
        campaign_clients: CampaignClientRepository,
        campaigns: CampaignRepository,
        documents: DocumentRepository,
        file_storage: FileStorage,
        classifier: DocumentClassifier,
    ) -> None:
        self._campaign_clients = campaign_clients
        self._campaigns = campaigns
        self._documents = documents
        self._file_storage = file_storage
        self._classifier = classifier

    async def get_status(self, token: str) -> tuple[Campaign, CampaignClient, list[Document]]:
        campaign_client = await self._get_campaign_client_or_raise(token)
        campaign = await self._get_campaign_or_raise(campaign_client)
        documents = await self._documents.list_for_campaign_clients([campaign_client.id])
        return campaign, campaign_client, documents

    async def upload_document(
        self, token: str, filename: str, content_type: str, content: bytes
    ) -> Document:
        campaign_client = await self._get_campaign_client_or_raise(token)
        campaign = await self._get_campaign_or_raise(campaign_client)
        storage_path = await self._file_storage.save(campaign_client.id, filename, content)

        status, campaign_document_type_id, confidence = await self._classify(
            campaign, content, content_type
        )

        document = Document(
            id=uuid4(),
            campaign_client_id=campaign_client.id,
            original_filename=filename,
            storage_path=storage_path,
            content_type=content_type,
            status=status,
            classification_confidence=confidence,
            uploaded_at=datetime.now(UTC),
            campaign_document_type_id=campaign_document_type_id,
        )
        return await self._documents.create(document)

    async def _classify(
        self, campaign: Campaign, content: bytes, content_type: str
    ) -> tuple[DocumentStatus, UUID | None, float | None]:
        allowed_names = [t.name for t in campaign.document_types]
        try:
            result = await self._classifier.classify(content, content_type, allowed_names)
        except Exception:
            logger.exception(
                "document_classification_failed", extra={"campaign_id": str(campaign.id)}
            )
            return DocumentStatus.UNCLASSIFIED, None, None

        if (
            result.document_type_name is not None
            and result.confidence >= _CLASSIFICATION_CONFIDENCE_THRESHOLD
        ):
            matched = next(
                (t for t in campaign.document_types if t.name == result.document_type_name),
                None,
            )
            if matched is not None:
                return DocumentStatus.CLASSIFIED, matched.id, result.confidence

        return DocumentStatus.UNCLASSIFIED, None, result.confidence

    async def _get_campaign_client_or_raise(self, token: str) -> CampaignClient:
        campaign_client = await self._campaign_clients.get_by_token(token)
        if campaign_client is None:
            raise EntityNotFoundError(entity="Enlace de subida", identifier=token)
        return campaign_client

    async def _get_campaign_or_raise(self, campaign_client: CampaignClient) -> Campaign:
        campaign = await self._campaigns.get_by_id_unscoped(campaign_client.campaign_id)
        if campaign is None:
            raise EntityNotFoundError(entity="Campaña", identifier=str(campaign_client.campaign_id))
        return campaign
