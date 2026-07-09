from httpx import AsyncClient

from app.domain.ports.document_classifier import ClassificationResult
from tests.fakes import FakeDocumentClassifier, FakeEmailSender

_PDF_MAGIC_BYTES = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\ncontenido de prueba"


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Gestoría Recordatorios",
            "email": email,
            "password": "supersecret123",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "supersecret123"},
    )
    return str(login_response.json()["access_token"])


async def _setup_campaign_with_clients(
    client: AsyncClient, headers: dict[str, str], client_emails: list[str]
) -> tuple[str, list[str]]:
    client_ids = []
    for email in client_emails:
        response = await client.post(
            "/api/v1/clients",
            json={"name": "Cliente recordatorio", "email": email},
            headers=headers,
        )
        client_ids.append(response.json()["id"])

    campaign_response = await client.post(
        "/api/v1/campaigns",
        json={"name": "Campaña de recordatorio", "document_types": ["DNI"]},
        headers=headers,
    )
    campaign_id = campaign_response.json()["id"]

    await client.post(
        f"/api/v1/campaigns/{campaign_id}/send",
        json={"client_ids": client_ids},
        headers=headers,
    )
    return campaign_id, client_ids


async def test_remind_requires_authentication(client: AsyncClient) -> None:
    response = await client.post("/api/v1/campaigns/00000000-0000-0000-0000-000000000000/remind")
    assert response.status_code == 401


async def test_remind_resends_email_to_pending_clients(
    client: AsyncClient, email_sender: FakeEmailSender
) -> None:
    token = await _register_and_login(client, "recordatorio1@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    campaign_id, client_ids = await _setup_campaign_with_clients(
        client, headers, ["cliente-recordatorio1@example.com"]
    )
    assert len(email_sender.sent) == 1

    response = await client.post(f"/api/v1/campaigns/{campaign_id}/remind", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["client_id"] == client_ids[0]
    assert body[0]["status"] == "pending"
    assert body[0]["last_reminder_sent_at"] is not None

    assert len(email_sender.sent) == 2
    reminder_email = email_sender.sent[1]
    assert reminder_email.to == "cliente-recordatorio1@example.com"
    assert "Campaña de recordatorio" in reminder_email.subject


async def test_remind_skips_complete_clients(
    client: AsyncClient,
    email_sender: FakeEmailSender,
    document_classifier: FakeDocumentClassifier,
) -> None:
    token = await _register_and_login(client, "recordatorio2@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client_response = await client.post(
        "/api/v1/clients",
        json={"name": "Cliente completo", "email": "cliente-completo@example.com"},
        headers=headers,
    )
    complete_client_id = client_response.json()["id"]
    pending_client_response = await client.post(
        "/api/v1/clients",
        json={"name": "Cliente pendiente", "email": "cliente-pendiente@example.com"},
        headers=headers,
    )
    pending_client_id = pending_client_response.json()["id"]

    campaign_response = await client.post(
        "/api/v1/campaigns",
        json={"name": "Campaña mixta", "document_types": ["DNI"]},
        headers=headers,
    )
    campaign_id = campaign_response.json()["id"]

    send_response = await client.post(
        f"/api/v1/campaigns/{campaign_id}/send",
        json={"client_ids": [complete_client_id, pending_client_id]},
        headers=headers,
    )
    assert len(email_sender.sent) == 2
    invites = {invite["client_id"]: invite for invite in send_response.json()}
    complete_upload_token = invites[complete_client_id]["upload_url"].rsplit("/", 1)[-1]

    document_classifier.result = ClassificationResult(document_type_name="DNI", confidence=0.9)
    await client.post(
        f"/api/v1/public/campaigns/{complete_upload_token}/documents",
        files={"file": ("dni.pdf", _PDF_MAGIC_BYTES, "application/pdf")},
    )

    status_response = await client.get(f"/api/v1/campaigns/{campaign_id}/status", headers=headers)
    statuses = {c["client_id"]: c["status"] for c in status_response.json()["clients"]}
    assert statuses[complete_client_id] == "complete"
    assert statuses[pending_client_id] == "pending"

    remind_response = await client.post(f"/api/v1/campaigns/{campaign_id}/remind", headers=headers)
    assert remind_response.status_code == 200
    reminded_client_ids = {r["client_id"] for r in remind_response.json()}
    assert reminded_client_ids == {pending_client_id}
    assert len(email_sender.sent) == 3
    assert email_sender.sent[2].to == "cliente-pendiente@example.com"


async def test_remind_returns_empty_list_when_no_pending_clients(
    client: AsyncClient, email_sender: FakeEmailSender
) -> None:
    token = await _register_and_login(client, "recordatorio3@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    campaign_response = await client.post(
        "/api/v1/campaigns",
        json={"name": "Campaña sin clientes", "document_types": ["DNI"]},
        headers=headers,
    )
    campaign_id = campaign_response.json()["id"]

    response = await client.post(f"/api/v1/campaigns/{campaign_id}/remind", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
    assert len(email_sender.sent) == 0


async def test_remind_nonexistent_campaign_is_404(client: AsyncClient) -> None:
    token = await _register_and_login(client, "recordatorio4@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/campaigns/00000000-0000-0000-0000-000000000000/remind", headers=headers
    )
    assert response.status_code == 404
