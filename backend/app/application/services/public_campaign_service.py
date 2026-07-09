from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities.campaign import Campaign
from app.domain.entities.campaign_client import CampaignClient
from app.domain.entities.document import Document, DocumentStatus
from app.domain.exceptions import EntityNotFoundError
from app.domain.ports.file_storage import FileStorage
from app.domain.repositories.campaign_client_repository import CampaignClientRepository
from app.domain.repositories.campaign_repository import CampaignRepository
from app.domain.repositories.document_repository import DocumentRepository


class PublicCampaignService:
    """Casos de uso del flujo público (sin login): consultar el estado de una
    solicitud por su enlace seguro y subir documentos. Ver ADR 0008/0010.
    """

    def __init__(
        self,
        campaign_clients: CampaignClientRepository,
        campaigns: CampaignRepository,
        documents: DocumentRepository,
        file_storage: FileStorage,
    ) -> None:
        self._campaign_clients = campaign_clients
        self._campaigns = campaigns
        self._documents = documents
        self._file_storage = file_storage

    async def get_status(self, token: str) -> tuple[Campaign, CampaignClient, list[Document]]:
        campaign_client = await self._get_campaign_client_or_raise(token)
        campaign = await self._campaigns.get_by_id_unscoped(campaign_client.campaign_id)
        if campaign is None:
            raise EntityNotFoundError(entity="Campaña", identifier=str(campaign_client.campaign_id))
        documents = await self._documents.list_for_campaign_clients([campaign_client.id])
        return campaign, campaign_client, documents

    async def upload_document(
        self, token: str, filename: str, content_type: str, content: bytes
    ) -> Document:
        campaign_client = await self._get_campaign_client_or_raise(token)
        storage_path = await self._file_storage.save(campaign_client.id, filename, content)

        document = Document(
            id=uuid4(),
            campaign_client_id=campaign_client.id,
            original_filename=filename,
            storage_path=storage_path,
            content_type=content_type,
            status=DocumentStatus.UNCLASSIFIED,
            uploaded_at=datetime.now(UTC),
        )
        return await self._documents.create(document)

    async def _get_campaign_client_or_raise(self, token: str) -> CampaignClient:
        campaign_client = await self._campaign_clients.get_by_token(token)
        if campaign_client is None:
            raise EntityNotFoundError(entity="Enlace de subida", identifier=token)
        return campaign_client
