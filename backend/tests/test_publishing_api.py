from httpx import AsyncClient

_FULL_KDP_METADATA = {
    "title": "Cocina rápida",
    "subtitle": "30 recetas",
    "description": "Un libro de cocina.",
    "keywords": "cocina, recetas, rápido",
    "categories": "Gastronomía",
    "price": "4.99",
}


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Editorial de prueba",
            "email": email,
            "password": "supersecret123",
        },
    )
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "supersecret123"}
    )
    return str(response.json()["access_token"])


async def _create_draft_book(client: AsyncClient, headers: dict[str, str]) -> str:
    response = await client.post(
        "/api/v1/books",
        json={
            "topic": "Cocina rápida",
            "niche": "Gastronomía",
            "target_audience": "Gente ocupada",
            "language": "español",
            "style": "directo",
            "target_pages": 20,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return str(response.json()["id"])


async def test_publication_lifecycle_via_api(client: AsyncClient) -> None:
    token = await _register_and_login(client, "editor@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    book_id = await _create_draft_book(client, headers)

    account_response = await client.post(
        "/api/v1/publishing/accounts",
        json={"platform": "kdp", "display_name": "Cuenta KDP de prueba"},
        headers=headers,
    )
    assert account_response.status_code == 201
    account = account_response.json()
    assert account["connection_status"] == "manual"

    prepare_response = await client.post(
        f"/api/v1/books/{book_id}/publications",
        json={"publishing_account_id": account["id"], "metadata": _FULL_KDP_METADATA},
        headers=headers,
    )
    assert prepare_response.status_code == 201
    publication = prepare_response.json()
    assert publication["status"] == "metadata_ready"
    assert publication["missing_metadata_fields"] == []
    publication_id = publication["id"]

    review_response = await client.post(
        f"/api/v1/publications/{publication_id}/request-review", headers=headers
    )
    assert review_response.json()["status"] == "pending_review"

    approve_response = await client.post(
        f"/api/v1/publications/{publication_id}/approve", headers=headers
    )
    assert approve_response.json()["status"] == "approved"

    submit_response = await client.post(
        f"/api/v1/publications/{publication_id}/submit", headers=headers
    )
    submitted = submit_response.json()
    assert submitted["status"] == "submitted"
    assert submitted["instructions"] is not None

    live_response = await client.post(
        f"/api/v1/publications/{publication_id}/mark-live",
        json={"external_book_id": "B0EXTERNAL"},
        headers=headers,
    )
    live = live_response.json()
    assert live["status"] == "live"
    assert live["external_book_id"] == "B0EXTERNAL"

    sale_response = await client.post(
        f"/api/v1/publications/{publication_id}/sales",
        json={
            "period_start": "2026-01-01T00:00:00Z",
            "period_end": "2026-01-31T00:00:00Z",
            "units_sold": 12,
            "revenue_amount": 47.88,
            "currency": "eur",
        },
        headers=headers,
    )
    assert sale_response.status_code == 201
    assert sale_response.json()["currency"] == "EUR"

    dashboard_response = await client.get("/api/v1/publishing/dashboard", headers=headers)
    summary = dashboard_response.json()
    assert summary["total_books"] == 1
    assert summary["total_publications"] == 1
    assert summary["publications_by_status"]["live"] == 1
    assert summary["total_units_sold"] == 12
    assert summary["revenue_by_currency"]["EUR"] == 47.88


async def test_cannot_submit_publication_before_approval(client: AsyncClient) -> None:
    token = await _register_and_login(client, "editor2@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    book_id = await _create_draft_book(client, headers)

    account_response = await client.post(
        "/api/v1/publishing/accounts",
        json={"platform": "kobo", "display_name": "Cuenta Kobo"},
        headers=headers,
    )
    account_id = account_response.json()["id"]

    prepare_response = await client.post(
        f"/api/v1/books/{book_id}/publications",
        json={"publishing_account_id": account_id, "metadata": _FULL_KDP_METADATA},
        headers=headers,
    )
    publication_id = prepare_response.json()["id"]

    response = await client.post(f"/api/v1/publications/{publication_id}/submit", headers=headers)
    assert response.status_code == 409
