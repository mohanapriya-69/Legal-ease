"""LegalEase API.

Application entrypoint. CORS is configured from an explicit allowlist and every
unhandled failure is converted into a JSON error envelope so Python tracebacks
are never returned to a client.
"""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routes import branding, documents, health, templates
from app.templates.disclaimer import LEGAL_DISCLAIMER
from app.utils.errors import register_exception_handlers

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s :: %(message)s",
)
logger = logging.getLogger("legalease")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.ensure_directories()
    try:
        init_db()
        logger.info("database ready (%s)", settings.database_url.split("://")[0])
    except Exception:
        # A database problem must not prevent the app from booting and serving
        # the health endpoint, which is what surfaces the problem.
        logger.exception("database initialisation failed")

    logger.info(
        "LegalEase API %s ready | ai_mode=%s | model=%s",
        settings.app_version,
        settings.ai_mode,
        settings.groq_model if settings.ai_configured else "n/a",
    )
    if settings.ai_mode == "unconfigured":
        logger.warning(
            "AI configuration is missing. Add GROQ_API_KEY to backend/.env "
            "(or set DEMO_MODE=true for offline sample output)."
        )
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-assisted legal document drafting.\n\n"
        f"> {LEGAL_DISCLAIMER}"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Explicit allowlist - never "*" - and no credentialed cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["Content-Disposition", "Content-Length"],
    max_age=600,
)
app.add_middleware(GZipMiddleware, minimum_size=1024)


@app.middleware("http")
async def request_context(request: Request, call_next):
    """Attach a request id and log method, path, status and duration."""
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    request.state.request_id = request_id
    started = time.perf_counter()

    response = await call_next(request)

    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    if request.url.path.startswith("/api") and not request.url.path.endswith("/health"):
        logger.info(
            "%s %s -> %s in %.0fms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
    return response


register_exception_handlers(app)

app.include_router(health.router)
app.include_router(templates.router)
app.include_router(documents.router)
app.include_router(branding.router)


@app.get("/", tags=["system"], summary="Service banner")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health",
        "frontend": settings.frontend_url,
        "ai_mode": settings.ai_mode,
        "legal_disclaimer": LEGAL_DISCLAIMER,
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> JSONResponse:
    return JSONResponse(status_code=204, content=None)
