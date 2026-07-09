from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Gestoría Clientes",
            "email": email,
            "password": "supersecret123",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "supersecret123"},
    )
    return str(login_response.json()["access_token"])


async def test_create_and_list_clients(client: AsyncClient) -> None:
    token = await _register_and_login(client, "gestor1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/api/v1/clients",
        json={
            "name": "Panadería Ejemplo SL",
            "email": "contacto@panaderia.example",
            "phone": "600111222",
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["name"] == "Panadería Ejemplo SL"
    assert body["phone"] == "600111222"

    list_response = await client.get("/api/v1/clients", headers=headers)
    assert list_response.status_code == 200
    clients = list_response.json()
    assert len(clients) == 1
    assert clients[0]["email"] == "contacto@panaderia.example"


async def test_clients_are_isolated_per_organization(client: AsyncClient) -> None:
    token_org1 = await _register_and_login(client, "org1@example.com")
    token_org2 = await _register_and_login(client, "org2@example.com")

    await client.post(
        "/api/v1/clients",
        json={"name": "Cliente de Org 1", "email": "cliente1@example.com"},
        headers={"Authorization": f"Bearer {token_org1}"},
    )

    org2_clients = await client.get(
        "/api/v1/clients", headers={"Authorization": f"Bearer {token_org2}"}
    )
    assert org2_clients.status_code == 200
    assert org2_clients.json() == []


async def test_create_client_requires_authentication(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/clients", json={"name": "Sin sesión", "email": "x@example.com"}
    )
    assert response.status_code == 401
