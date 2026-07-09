from collections import defaultdict
from uuid import UUID

from app.domain.entities.campaign import Campaign
from app.domain.entities.campaign_client import CampaignClient
from app.domain.entities.client import Client
from app.domain.entities.document import Document
from app.domain.exceptions import EntityNotFoundError
from app.domain.repositories.campaign_client_repository import CampaignClientRepository
from app.domain.repositories.campaign_repository import CampaignRepository
from app.domain.repositories.client_repository import ClientRepository
from app.domain.repositories.document_repository import DocumentRepository

ClientStatusRow = tuple[CampaignClient, Client, list[Document]]


class CampaignStatusService:
    """Caso de uso del panel del gestor: para cada cliente al que se le
    envió la campaña, su estado, documentos recibidos y tipos que faltan.
    """

    def __init__(
        self,
        campaigns: CampaignRepository,
        campaign_clients: CampaignClientRepository,
        clients: ClientRepository,
        documents: DocumentRepository,
    ) -> None:
        self._campaigns = campaigns
        self._campaign_clients = campaign_clients
        self._clients = clients
        self._documents = documents

    async def get_status(
        self, campaign_id: UUID, organization_id: UUID
    ) -> tuple[Campaign, list[ClientStatusRow]]:
        campaign = await self._campaigns.get_by_id(campaign_id, organization_id)
        if campaign is None:
            raise EntityNotFoundError(entity="Campaña", identifier=str(campaign_id))

        campaign_clients = await self._campaign_clients.list_for_campaign(campaign_id)
        if not campaign_clients:
            return campaign, []

        documents = await self._documents.list_for_campaign_clients(
            [cc.id for cc in campaign_clients]
        )
        documents_by_campaign_client: dict[UUID, list[Document]] = defaultdict(list)
        for document in documents:
            documents_by_campaign_client[document.campaign_client_id].append(document)

        rows: list[ClientStatusRow] = []
        for campaign_client in campaign_clients:
            client = await self._clients.get_by_id(campaign_client.client_id, organization_id)
            if client is None:
                # No debería ocurrir (un cliente no se borra tras enviarle una
                # campaña), pero si pasara, se omite en vez de romper el panel.
                continue
            rows.append(
                (campaign_client, client, documents_by_campaign_client.get(campaign_client.id, []))
            )

        return campaign, rows
