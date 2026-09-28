"""Common schema helpers."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorBody(BaseModel):
    code: str = Field(examples=["AI_NOT_CONFIGURED"])
    message: str
    fields: list[str] | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int


class Page(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    environment: str
    database: str
    ai: dict[str, Any]
    legal_disclaimer: str
