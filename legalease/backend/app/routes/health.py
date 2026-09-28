"""Health and AI status endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.schemas.common import HealthResponse
from app.templates.disclaimer import (
    AI_MISSING_CONFIG_MESSAGE,
    LEGAL_DISCLAIMER,
)

router = APIRouter(tags=["system"])


def _database_status() -> str:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "connected"
    except Exception:  # pragma: no cover - environment issue
        return "unavailable"


def ai_status_payload() -> dict[str, Any]:
    """Public AI readiness. Deliberately never includes the key itself."""
    return {
        "mode": settings.ai_mode,
        "configured": settings.ai_configured,
        "model": settings.groq_model if settings.ai_configured else None,
        "demo_mode": settings.demo_mode,
        "available": settings.ai_mode in ("groq", "demo"),
        "message": (
            None
            if settings.ai_mode != "unconfigured"
            else AI_MISSING_CONFIG_MESSAGE
        ),
    }


@router.get("/api/health", response_model=HealthResponse, summary="Service health")
def health() -> HealthResponse:
    """Always returns 200 so a missing API key never looks like a crash."""
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        database=_database_status(),
        ai=ai_status_payload(),
        legal_disclaimer=LEGAL_DISCLAIMER,
    )


@router.get("/api/ai/status", summary="AI readiness for the client")
def ai_status() -> dict[str, Any]:
    return ai_status_payload()
