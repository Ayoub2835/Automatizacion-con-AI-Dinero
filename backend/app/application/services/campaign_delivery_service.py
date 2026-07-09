import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.entities.campaign import Campaign
from app.domain.entities.campaign_client import CampaignClient, CampaignClientStatus
from app.domain.entities.client import Client
from app.domain.exceptions import EntityNotFoundError
from app.domain.ports.email_sender import EmailSender
from app.domain.repositories.campaign_client_repository import CampaignClientRepository
from app.domain.repositories.client_repository import ClientRepository


@dataclass
class SentCampaignInvite:
    campaign_client: CampaignClient
    client: Client
    upload_url: str


def build_document_request_email(campaign: Campaign, upload_url: str) -> tuple[str, str]:
    """Construye (asunto, cuerpo) del email de solicitud de documentación.

    Reutilizado también por el recordatorio (T8) para mantener el mismo
    mensaje base.
    """
    document_type_list = "\n".join(f"- {t.name}" for t in campaign.document_types)
    subject = f"Documentación solicitada: {campaign.name}"
    body = (
        f"Hola,\n\n"
        f"Necesitamos que nos envíes los siguientes documentos "
        f"para «{campaign.name}»:\n\n"
        f"{document_type_list}\n\n"
        f"Puedes subirlos de forma segura desde este enlace:\n{upload_url}\n\n"
        f"Gracias."
    )
    return subject, body


class CampaignDeliveryService:
    """Asocia una campaña a un conjunto de clientes, genera su enlace seguro
    y envía el email de solicitud de documentación.

    Es idempotente: reenviar una campaña a un cliente que ya la tenía no
    crea una fila duplicada ni reenvía el email (para eso está el
    recordatorio explícito de T8).
    """

    def __init__(
        self,
        campaign_clients: CampaignClientRepository,
        clients: ClientRepository,
        email_sender: EmailSender,
        frontend_url: str,
    ) -> None:
        self._campaign_clients = campaign_clients
        self._clients = clients
        self._email_sender = email_sender
        self._frontend_url = frontend_url.rstrip("/")

    async def send_to_clients(
        self, campaign: Campaign, client_ids: list[UUID]
    ) -> list[SentCampaignInvite]:
        unique_ids = list(dict.fromkeys(client_ids))

        clients_by_id: dict[UUID, Client] = {}
        for client_id in unique_ids:
            client = await self._clients.get_by_id(client_id, campaign.organization_id)
            if client is None:
                raise EntityNotFoundError(entity="Cliente", identifier=str(client_id))
            clients_by_id[client_id] = client

        existing_ids = await self._campaign_clients.get_existing_client_ids(campaign.id, unique_ids)
        new_ids = [cid for cid in unique_ids if cid not in existing_ids]
        if not new_ids:
            return []

        new_rows = [
            CampaignClient(
                id=uuid4(),
                campaign_id=campaign.id,
                client_id=client_id,
                upload_token=secrets.token_urlsafe(32),
                status=CampaignClientStatus.PENDING,
                created_at=datetime.now(UTC),
            )
            for client_id in new_ids
        ]
        created = await self._campaign_clients.create_many(new_rows)

        invites = [
            SentCampaignInvite(
                campaign_client=cc,
                client=clients_by_id[cc.client_id],
                upload_url=f"{self._frontend_url}/upload/{cc.upload_token}",
            )
            for cc in created
        ]

        for invite in invites:
            subject, body = build_document_request_email(campaign, invite.upload_url)
            await self._email_sender.send(to=invite.client.email, subject=subject, body=body)

        return invites

    async def send_reminders(self, campaign: Campaign) -> list[SentCampaignInvite]:
        """Reenvía el email de solicitud a los clientes de la campaña que
        siguen `pending`. No toca a los ya `complete`.
        """
        campaign_clients = await self._campaign_clients.list_for_campaign(campaign.id)
        pending = [cc for cc in campaign_clients if cc.status == CampaignClientStatus.PENDING]
        if not pending:
            return []

        reminders = []
        for campaign_client in pending:
            client = await self._clients.get_by_id(
                campaign_client.client_id, campaign.organization_id
            )
            if client is None:
                continue
            upload_url = f"{self._frontend_url}/upload/{campaign_client.upload_token}"
            reminders.append(
                SentCampaignInvite(
                    campaign_client=campaign_client, client=client, upload_url=upload_url
                )
            )

        sent_at = datetime.now(UTC)
        for reminder in reminders:
            subject, body = build_document_request_email(campaign, reminder.upload_url)
            await self._email_sender.send(to=reminder.client.email, subject=subject, body=body)
            await self._campaign_clients.mark_reminder_sent(reminder.campaign_client.id, sent_at)
            reminder.campaign_client.last_reminder_sent_at = sent_at

        return reminders
