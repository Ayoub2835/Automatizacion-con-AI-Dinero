import secrets
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.entities.campaign_client import CampaignClient, CampaignClientStatus
from app.domain.entities.client import Client
from app.domain.exceptions import EntityNotFoundError
from app.domain.repositories.campaign_client_repository import CampaignClientRepository
from app.domain.repositories.client_repository import ClientRepository


class CampaignDeliveryService:
    """Asocia una campaña a un conjunto de clientes, generando su enlace seguro.

    No envía el email todavía (ver T4) — este servicio solo se encarga de
    crear la asociación y el token. Es idempotente: reenviar una campaña a
    un cliente que ya la tenía no crea una fila duplicada.
    """

    def __init__(
        self, campaign_clients: CampaignClientRepository, clients: ClientRepository
    ) -> None:
        self._campaign_clients = campaign_clients
        self._clients = clients

    async def send_to_clients(
        self, campaign_id: UUID, organization_id: UUID, client_ids: list[UUID]
    ) -> list[tuple[CampaignClient, Client]]:
        unique_ids = list(dict.fromkeys(client_ids))

        clients_by_id: dict[UUID, Client] = {}
        for client_id in unique_ids:
            client = await self._clients.get_by_id(client_id, organization_id)
            if client is None:
                raise EntityNotFoundError(entity="Cliente", identifier=str(client_id))
            clients_by_id[client_id] = client

        existing_ids = await self._campaign_clients.get_existing_client_ids(campaign_id, unique_ids)
        new_ids = [cid for cid in unique_ids if cid not in existing_ids]
        if not new_ids:
            return []

        new_rows = [
            CampaignClient(
                id=uuid4(),
                campaign_id=campaign_id,
                client_id=client_id,
                upload_token=secrets.token_urlsafe(32),
                status=CampaignClientStatus.PENDING,
                created_at=datetime.now(UTC),
            )
            for client_id in new_ids
        ]
        created = await self._campaign_clients.create_many(new_rows)
        return [(cc, clients_by_id[cc.client_id]) for cc in created]
