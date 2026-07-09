from httpx import AsyncClient

_PDF_MAGIC_BYTES = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\ncontenido de prueba"


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Gestoría Subida",
            "email": email,
            "password": "supersecret123",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "supersecret123"},
    )
    return str(login_response.json()["access_token"])


async def _get_upload_token(client: AsyncClient, headers: dict[str, str]) -> str:
    """Registra un cliente, crea una campaña y la envía; devuelve el token
    extraído de la upload_url (el mismo camino que seguiría un email real)."""
    client_response = await client.post(
        "/api/v1/clients",
        json={"name": "Cliente subida", "email": "cliente-subida@example.com"},
        headers=headers,
    )
    client_id = client_response.json()["id"]

    campaign_response = await client.post(
        "/api/v1/campaigns",
        json={"name": "Campaña de subida", "document_types": ["DNI", "Recibo de autónomos"]},
        headers=headers,
    )
    campaign_id = campaign_response.json()["id"]

    send_response = await client.post(
        f"/api/v1/campaigns/{campaign_id}/send",
        json={"client_ids": [client_id]},
        headers=headers,
    )
    upload_url = send_response.json()[0]["upload_url"]
    return upload_url.rsplit("/", 1)[-1]


async def test_get_status_for_unknown_token_is_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/public/campaigns/token-que-no-existe")
    assert response.status_code == 404


async def test_get_status_shows_required_document_types_unsatisfied(client: AsyncClient) -> None:
    token = await _register_and_login(client, "subida1@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    upload_token = await _get_upload_token(client, headers)

    response = await client.get(f"/api/v1/public/campaigns/{upload_token}")
    assert response.status_code == 200
    body = response.json()
    assert body["campaign_name"] == "Campaña de subida"
    assert body["client_status"] == "pending"
    assert {t["name"] for t in body["document_types"]} == {"DNI", "Recibo de autónomos"}
    assert all(t["satisfied"] is False for t in body["document_types"])
    assert body["documents"] == []


async def test_upload_document_succeeds(client: AsyncClient) -> None:
    token = await _register_and_login(client, "subida2@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    upload_token = await _get_upload_token(client, headers)

    response = await client.post(
        f"/api/v1/public/campaigns/{upload_token}/documents",
        files={"file": ("dni.pdf", _PDF_MAGIC_BYTES, "application/pdf")},
    )
    assert response.status_code == 201
    body = response.json()
    assert len(body["documents"]) == 1
    document = body["documents"][0]
    assert document["original_filename"] == "dni.pdf"
    # Todavía sin clasificar: la clasificación automática llega en T6.
    assert document["status"] == "unclassified"
    assert document["document_type_name"] is None


async def test_upload_rejects_unsupported_content_type(client: AsyncClient) -> None:
    token = await _register_and_login(client, "subida3@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    upload_token = await _get_upload_token(client, headers)

    response = await client.post(
        f"/api/v1/public/campaigns/{upload_token}/documents",
        files={"file": ("nota.txt", b"contenido", "text/plain")},
    )
    assert response.status_code == 415


async def test_upload_rejects_oversized_file(client: AsyncClient) -> None:
    token = await _register_and_login(client, "subida4@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    upload_token = await _get_upload_token(client, headers)

    oversized_content = b"0" * (15 * 1024 * 1024 + 1)
    response = await client.post(
        f"/api/v1/public/campaigns/{upload_token}/documents",
        files={"file": ("grande.pdf", oversized_content, "application/pdf")},
    )
    assert response.status_code == 413


async def test_upload_to_unknown_token_is_404(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/public/campaigns/token-que-no-existe/documents",
        files={"file": ("dni.pdf", _PDF_MAGIC_BYTES, "application/pdf")},
    )
    assert response.status_code == 404
