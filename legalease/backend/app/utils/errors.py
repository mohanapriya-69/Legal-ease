"""Typed application errors and the JSON error envelope.

Clients always receive ``{"error": {"code", "message"}}``. Tracebacks are
logged server-side and never serialised into a response body.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("legalease.errors")


class AppError(Exception):
    """Base class for every error the API surfaces to a client."""

    code: str = "INTERNAL_ERROR"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Something went wrong. Please try again."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.message = message or self.message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)

    def to_payload(self) -> dict[str, Any]:
        return {"error": {"code": self.code, "message": self.message}}


# --- Domain errors ----------------------------------------------------


class NotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND
    message = "The requested resource was not found."


class ValidationError(AppError):
    code = "VALIDATION_ERROR"
    status_code = 422
    message = "The submitted data is invalid."


class AIError(AppError):
    code = "AI_ERROR"
    status_code = status.HTTP_502_BAD_GATEWAY
    message = "The AI service could not complete the request."


class AINotConfiguredError(AppError):
    code = "AI_NOT_CONFIGURED"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    message = "AI configuration is missing. Add GROQ_API_KEY to backend/.env."


class AITimeoutError(AIError):
    code = "AI_TIMEOUT"
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    message = "The AI service took too long to respond. Please try again."


class AIAuthError(AIError):
    code = "AI_AUTH_FAILED"
    status_code = status.HTTP_502_BAD_GATEWAY
    message = "The AI service rejected the configured credentials."


class AIQuotaError(AIError):
    code = "AI_QUOTA_EXCEEDED"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "The AI service quota has been exhausted. Please try again later."


class AIInvalidResponseError(AIError):
    code = "AI_INVALID_RESPONSE"
    status_code = status.HTTP_502_BAD_GATEWAY
    message = "The AI service returned an unreadable response. Please try again."


class UploadError(AppError):
    code = "UPLOAD_REJECTED"
    status_code = status.HTTP_400_BAD_REQUEST
    message = "The uploaded file was rejected."


class ExportError(AppError):
    code = "EXPORT_FAILED"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "The document could not be exported. Please try again."


# --- Handler registration --------------------------------------------


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=exc.to_payload())

    @app.exception_handler(RequestValidationError)
    async def _validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Only field locations are echoed back - never the submitted value,
        # which could contain sensitive text.
        fields = [
            ".".join(str(part) for part in err.get("loc", ())[1:]) or "body"
            for err in exc.errors()
        ]
        logger.info("validation rejected on %s: %s", _request_id(request), fields)
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Please correct the highlighted fields and try again.",
                    "fields": fields,
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
        message = (
            "The requested endpoint does not exist."
            if exc.status_code == 404
            else str(exc.detail)
        )
        if request.url.path.startswith("/api"):
            return JSONResponse(
                status_code=exc.status_code, content={"error": {"code": code, "message": message}}
            )
        return JSONResponse(status_code=exc.status_code, content={"detail": message})

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        # Full detail stays in the server log; the client gets a generic message.
        logger.exception("unhandled error on %s (%s)", _request_id(request), request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again.",
                }
            },
        )
