from uuid import uuid4

from httpx import AsyncClient

from app.domain.ports.document_classifier import ClassificationResult
from tests.fakes import FakeDocumentClassifier

_PDF_MAGIC_BYTES = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\ncontenido de prueba"


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Gestoría Estado",
            "email": email,
            "password": "supersecret123",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "supersecret123"},
    )
    return str(login_response.json()["access_token"])


async def _setup_campaign(
    client: AsyncClient, headers: dict[str, str], document_types: list[str]
) -> tuple[str, str, str]:
    """Crea un cliente, una campaña y la envía. Devuelve (campaign_id, client_id, upload_token)."""
    client_response = await client.post(
        "/api/v1/clients",
        json={"name": "Cliente Estado", "email": "cliente-estado@example.com"},
        headers=headers,
    )
    client_id = client_response.json()["id"]

    campaign_response = await client.post(
        "/api/v1/campaigns",
        json={"name": "Campaña de estado", "document_types": document_types},
        headers=headers,
    )
    campaign_id = campaign_response.json()["id"]

    send_response = await client.post(
        f"/api/v1/campaigns/{campaign_id}/send",
        json={"client_ids": [client_id]},
        headers=headers,
    )
    upload_url = send_response.json()[0]["upload_url"]
    upload_token = upload_url.rsplit("/", 1)[-1]
    return campaign_id, client_id, upload_token


async def test_status_requires_authentication(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/campaigns/{uuid4()}/status")
    assert response.status_code == 401


async def test_status_for_nonexistent_campaign_is_404(client: AsyncClient) -> None:
    token = await _register_and_login(client, "estado-404@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/campaigns/{uuid4()}/status", headers=headers)
    assert response.status_code == 404


async def test_status_shows_pending_client_with_no_documents(client: AsyncClient) -> None:
    token = await _register_and_login(client, "estado1@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    campaign_id, client_id, _ = await _setup_campaign(client, headers, ["DNI"])

    response = await client.get(f"/api/v1/campaigns/{campaign_id}/status", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["campaign_name"] == "Campaña de estado"
    assert len(body["clients"]) == 1
    client_status = body["clients"][0]
    assert client_status["client_id"] == client_id
    assert client_status["status"] == "pending"
    assert client_status["document_types"] == [{"name": "DNI", "satisfied": False}]
    assert client_status["documents"] == []


async def test_status_becomes_complete_once_all_types_are_classified(
    client: AsyncClient, document_classifier: FakeDocumentClassifier
) -> None:
    token = await _register_and_login(client, "estado2@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    campaign_id, _client_id, upload_token = await _setup_campaign(
        client, headers, ["DNI", "Recibo de autónomos"]
    )

    document_classifier.result = ClassificationResult(document_type_name="DNI", confidence=0.9)
    await client.post(
        f"/api/v1/public/campaigns/{upload_token}/documents",
        files={"file": ("dni.pdf", _PDF_MAGIC_BYTES, "application/pdf")},
    )

    status_after_first = await client.get(
        f"/api/v1/campaigns/{campaign_id}/status", headers=headers
    )
    assert status_after_first.json()["clients"][0]["status"] == "pending"

    document_classifier.result = ClassificationResult(
        document_type_name="Recibo de autónomos", confidence=0.9
    )
    await client.post(
        f"/api/v1/public/campaigns/{upload_token}/documents",
        files={"file": ("recibo.pdf", _PDF_MAGIC_BYTES, "application/pdf")},
    )

    status_after_second = await client.get(
        f"/api/v1/campaigns/{campaign_id}/status", headers=headers
    )
    assert status_after_second.status_code == 200
    client_status = status_after_second.json()["clients"][0]
    assert client_status["status"] == "complete"
    satisfied_by_name = {t["name"]: t["satisfied"] for t in client_status["document_types"]}
    assert satisfied_by_name == {"DNI": True, "Recibo de autónomos": True}
    filenames = {d["original_filename"] for d in client_status["documents"]}
    assert filenames == {"dni.pdf", "recibo.pdf"}


async def test_status_lists_unclassified_documents_without_completing(
    client: AsyncClient, document_classifier: FakeDocumentClassifier
) -> None:
    document_classifier.result = ClassificationResult(document_type_name=None, confidence=0.1)
    token = await _register_and_login(client, "estado3@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    campaign_id, _client_id, upload_token = await _setup_campaign(client, headers, ["DNI"])

    await client.post(
        f"/api/v1/public/campaigns/{upload_token}/documents",
        files={"file": ("borroso.pdf", _PDF_MAGIC_BYTES, "application/pdf")},
    )

    response = await client.get(f"/api/v1/campaigns/{campaign_id}/status", headers=headers)
    client_status = response.json()["clients"][0]
    assert client_status["status"] == "pending"
    assert client_status["document_types"] == [{"name": "DNI", "satisfied": False}]
    assert len(client_status["documents"]) == 1
    assert client_status["documents"][0]["document_type_name"] is None
    assert client_status["documents"][0]["status"] == "unclassified"


async def test_status_of_other_organization_campaign_is_404(client: AsyncClient) -> None:
    token_org1 = await _register_and_login(client, "estado-org1@example.com")
    token_org2 = await _register_and_login(client, "estado-org2@example.com")
    headers_org1 = {"Authorization": f"Bearer {token_org1}"}
    headers_org2 = {"Authorization": f"Bearer {token_org2}"}

    campaign_id, _client_id, _token = await _setup_campaign(client, headers_org1, ["DNI"])

    response = await client.get(f"/api/v1/campaigns/{campaign_id}/status", headers=headers_org2)
    assert response.status_code == 404
