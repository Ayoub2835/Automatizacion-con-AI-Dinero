from httpx import AsyncClient


async def test_register_and_login(client: AsyncClient) -> None:
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Gestoría Ejemplo",
            "email": "admin@example.com",
            "password": "supersecret123",
        },
    )
    assert register_response.status_code == 201
    body = register_response.json()
    assert body["email"] == "admin@example.com"
    assert body["role"] == "admin"

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "supersecret123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]


async def test_register_duplicate_email_fails(client: AsyncClient) -> None:
    payload = {
        "organization_name": "Gestoría Uno",
        "email": "duplicado@example.com",
        "password": "supersecret123",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


async def test_login_invalid_credentials(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "no-existe@example.com", "password": "whatever123"},
    )
    assert response.status_code == 401


async def test_me_returns_current_user(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Gestoría Me",
            "email": "me@example.com",
            "password": "supersecret123",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "supersecret123"},
    )
    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


async def test_me_without_token_is_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
