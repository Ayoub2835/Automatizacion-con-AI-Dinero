from uuid import uuid4

from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Gestoría Campañas",
            "email": email,
            "password": "supersecret123",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "supersecret123"},
    )
    return str(login_response.json()["access_token"])


async def test_create_campaign_with_document_types(client: AsyncClient) -> None:
    token = await _register_and_login(client, "gestor-campanas@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/campaigns",
        json={
            "name": "Documentación Renta 2025",
            "document_types": ["DNI", "Recibo de autónomos"],
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Documentación Renta 2025"
    assert {t["name"] for t in body["document_types"]} == {"DNI", "Recibo de autónomos"}


async def test_create_campaign_rejects_duplicate_document_types(client: AsyncClient) -> None:
    token = await _register_and_login(client, "gestor-dup@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/campaigns",
        json={"name": "Campaña con duplicados", "document_types": ["DNI", "DNI"]},
        headers=headers,
    )
    assert response.status_code == 422


async def test_create_campaign_requires_at_least_one_document_type(client: AsyncClient) -> None:
    token = await _register_and_login(client, "gestor-vacia@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/campaigns",
        json={"name": "Campaña vacía", "document_types": []},
        headers=headers,
    )
    assert response.status_code == 422


async def test_list_and_get_campaign(client: AsyncClient) -> None:
    token = await _register_and_login(client, "gestor-listar@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/api/v1/campaigns",
        json={"name": "Campaña A", "document_types": ["DNI"]},
        headers=headers,
    )
    campaign_id = create_response.json()["id"]

    list_response = await client.get("/api/v1/campaigns", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = await client.get(f"/api/v1/campaigns/{campaign_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == campaign_id


async def test_get_campaign_not_found(client: AsyncClient) -> None:
    token = await _register_and_login(client, "gestor-404@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"/api/v1/campaigns/{uuid4()}", headers=headers)
    assert response.status_code == 404


async def test_campaigns_are_isolated_per_organization(client: AsyncClient) -> None:
    token_org1 = await _register_and_login(client, "campanas-org1@example.com")
    token_org2 = await _register_and_login(client, "campanas-org2@example.com")

    create_response = await client.post(
        "/api/v1/campaigns",
        json={"name": "Campaña de Org 1", "document_types": ["DNI"]},
        headers={"Authorization": f"Bearer {token_org1}"},
    )
    campaign_id = create_response.json()["id"]

    other_org_get = await client.get(
        f"/api/v1/campaigns/{campaign_id}", headers={"Authorization": f"Bearer {token_org2}"}
    )
    assert other_org_get.status_code == 404
