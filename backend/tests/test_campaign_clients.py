from uuid import uuid4

from httpx import AsyncClient

from tests.fakes import FakeEmailSender


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Gestoría Envíos",
            "email": email,
            "password": "supersecret123",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "supersecret123"},
    )
    return str(login_response.json()["access_token"])


async def _create_client(client: AsyncClient, headers: dict[str, str], email: str) -> str:
    response = await client.post(
        "/api/v1/clients",
        json={"name": "Cliente de prueba", "email": email},
        headers=headers,
    )
    return str(response.json()["id"])


async def _create_campaign(client: AsyncClient, headers: dict[str, str]) -> str:
    response = await client.post(
        "/api/v1/campaigns",
        json={"name": "Campaña de prueba", "document_types": ["DNI"]},
        headers=headers,
    )
    return str(response.json()["id"])


async def test_send_campaign_creates_secure_links_and_sends_email(
    client: AsyncClient, email_sender: FakeEmailSender
) -> None:
    token = await _register_and_login(client, "envio1@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    client_id = await _create_client(client, headers, "cliente-envio1@example.com")
    campaign_id = await _create_campaign(client, headers)

    response = await client.post(
        f"/api/v1/campaigns/{campaign_id}/send",
        json={"client_ids": [client_id]},
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert len(body) == 1
    assert body[0]["client_id"] == client_id
    assert body[0]["status"] == "pending"
    assert body[0]["upload_url"].startswith("http://localhost:3000/upload/")

    assert len(email_sender.sent) == 1
    sent = email_sender.sent[0]
    assert sent.to == "cliente-envio1@example.com"
    assert "Campaña de prueba" in sent.subject
    assert body[0]["upload_url"] in sent.body
    assert "DNI" in sent.body


async def test_sending_campaign_twice_is_idempotent_and_does_not_resend_email(
    client: AsyncClient, email_sender: FakeEmailSender
) -> None:
    token = await _register_and_login(client, "envio2@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    client_id = await _create_client(client, headers, "cliente-envio2@example.com")
    campaign_id = await _create_campaign(client, headers)

    first = await client.post(
        f"/api/v1/campaigns/{campaign_id}/send",
        json={"client_ids": [client_id]},
        headers=headers,
    )
    assert len(first.json()) == 1

    second = await client.post(
        f"/api/v1/campaigns/{campaign_id}/send",
        json={"client_ids": [client_id]},
        headers=headers,
    )
    assert second.status_code == 201
    assert second.json() == []
    assert len(email_sender.sent) == 1


async def test_send_campaign_rejects_client_from_another_organization(client: AsyncClient) -> None:
    token_org1 = await _register_and_login(client, "envio-org1@example.com")
    token_org2 = await _register_and_login(client, "envio-org2@example.com")
    headers_org1 = {"Authorization": f"Bearer {token_org1}"}
    headers_org2 = {"Authorization": f"Bearer {token_org2}"}

    client_id_org2 = await _create_client(client, headers_org2, "cliente-org2@example.com")
    campaign_id_org1 = await _create_campaign(client, headers_org1)

    response = await client.post(
        f"/api/v1/campaigns/{campaign_id_org1}/send",
        json={"client_ids": [client_id_org2]},
        headers=headers_org1,
    )
    assert response.status_code == 404


async def test_send_nonexistent_campaign(client: AsyncClient) -> None:
    token = await _register_and_login(client, "envio-404@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    client_id = await _create_client(client, headers, "cliente-404@example.com")

    response = await client.post(
        f"/api/v1/campaigns/{uuid4()}/send",
        json={"client_ids": [client_id]},
        headers=headers,
    )
    assert response.status_code == 404
