"""Health, system banner and AI status behaviour."""

from __future__ import annotations


def test_root_banner(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["name"]
    assert body["health"] == "/api/health"
    assert "not a substitute for advice" in body["legal_disclaimer"]


def test_health_returns_200(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"
    assert "ai" in body


def test_health_never_leaks_the_api_key(client):
    raw = client.get("/api/health").text
    assert "groq_api_key" not in raw
    assert "api_key" not in raw.lower()
    # The key must not appear under any nested field either.
    body = client.get("/api/health").json()
    assert "groq_api_key" not in str(body)


def test_ai_status_reports_demo_mode(client):
    body = client.get("/api/ai/status").json()
    assert body["mode"] in ("groq", "demo", "unconfigured")
    assert isinstance(body["available"], bool)


def test_ai_status_explains_missing_key(monkeypatch, client):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "groq_api_key", None, raising=False)
    monkeypatch.setattr(get_settings(), "demo_mode", False, raising=False)

    body = client.get("/api/ai/status").json()
    assert body["mode"] == "unconfigured"
    assert body["available"] is False
    assert body["message"] == (
        "AI configuration is missing. Add GROQ_API_KEY to backend/.env."
    )


def test_openapi_schema_is_generated(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    for expected in (
        "/api/health",
        "/api/documents/generate",
        "/api/documents",
        "/api/documents/{document_id}",
        "/api/documents/{document_id}/export/pdf",
        "/api/documents/{document_id}/export/docx",
        "/api/documents/{document_id}/export/txt",
        "/api/documents/{document_id}/rewrite-section",
        "/api/documents/{document_id}/duplicate",
        "/api/documents/{document_id}/versions",
        "/api/documents/{document_id}/versions/{version_number}/restore",
        "/api/branding",
    ):
        assert expected in paths, f"missing route {expected}"


def test_cors_allows_configured_frontend(client):
    response = client.get(
        "/api/health", headers={"Origin": "http://localhost:5173"}
    )
    assert response.headers.get("access-control-allow-origin") == (
        "http://localhost:5173"
    )


def test_cors_does_not_wildcard(client):
    response = client.get(
        "/api/health", headers={"Origin": "https://evil.example"}
    )
    assert response.headers.get("access-control-allow-origin") != "*"

