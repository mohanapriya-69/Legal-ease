"""Shared pytest fixtures.

Every test runs against a throwaway SQLite database in a temp directory and in
demo mode, so the suite is hermetic and never calls a live model.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

TEMP_DIR = tempfile.mkdtemp(prefix="legalease-tests-")
DB_PATH = Path(TEMP_DIR) / "test.db"
LOGO_DIR = Path(TEMP_DIR) / "logos"

# Must be set before app.config is imported.
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "false"
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"
os.environ["groq_api_key"] = ""
os.environ["DEMO_MODE"] = "true"
os.environ["FRONTEND_URL"] = "http://localhost:5173"
os.environ["UPLOAD_DIR"] = str(Path(TEMP_DIR))

from fastapi.testclient import TestClient  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _prepare_database() -> None:
    settings.ensure_directories()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture()
def db_session():
    from app.database import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def payload() -> dict:
    """A complete, valid generate request."""
    return {
        "document_type": "freelance-agreement",
        "parties": [
            {
                "name": "Karthikeyan",
                "role": "Freelancer",
                "address": "12 Anna Salai, Chennai 600002, India",
                "email": "karthikeyan@example.com",
                "phone": "+91 90000 12345",
            },
            {
                "name": "ABC Technologies",
                "role": "Client",
                "organization": "ABC Technologies",
                "address": "5 Park Street, Kolkata 700016, India",
                "email": "accounts@abctech.example",
            },
        ],
        "clauses": [
            {
                "clause_key": "deadlines",
                "title": "Deadlines",
                "description": "The project must be completed within 30 days.",
                "is_required": True,
            },
            {
                "clause_key": "payment_terms",
                "title": "Payment Terms",
                "description": "Payment must be completed within 15 days after delivery.",
                "is_required": True,
            },
            {
                "clause_key": "confidentiality",
                "title": "Confidentiality",
                "description": "Both parties must maintain confidentiality.",
                "is_required": True,
            },
            {
                "clause_key": "termination",
                "title": "Termination",
                "description": "Either party may terminate with 15 days notice.",
                "is_required": True,
            },
        ],
        "effective_date": "2026-10-15",
        "expiry_date": None,
        "jurisdiction": {
            "country": "India",
            "state": "Tamil Nadu",
            "city": "Chennai",
            "governing_law": "Laws of India",
        },
        "branding": {
            "organization_name": "ABC Technologies",
            "email": "legal@abctech.example",
            "website": "www.abctech.example",
            "footer_text": "ABC Technologies",
        },
        "additional_instructions": "Keep the numbering sequential.",
    }


@pytest.fixture()
def generated_document(client: TestClient, payload: dict) -> dict:
    response = client.post("/api/documents/generate", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["document"]


# --- Fixtures for security tests --------------------------------------

PNG_1x1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d494844520000000100000001080600000"
    "01f15c4890000000a49444154789c6360000002000100ffff03000006"
    "0005570bf5d40000000049454e44ae426082"
)


@pytest.fixture()
def png_bytes() -> bytes:
    return PNG_1x1
