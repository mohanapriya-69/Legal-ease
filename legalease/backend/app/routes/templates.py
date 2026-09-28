"""Template catalog endpoints. These never touch the database."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.schemas.branding import SampleDataResponse, TemplateListResponse, TemplateRead
from app.services.template_service import (
    clause_suggestions,
    get_sample_data,
    get_template,
    list_templates,
)
from app.schemas.ai import REWRITE_ACTION_LABELS

router = APIRouter(prefix="/api", tags=["templates"])


@router.get("/templates", response_model=TemplateListResponse, summary="List templates")
def templates(
    search: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, max_length=60),
) -> TemplateListResponse:
    return list_templates(search=search, category=category)


@router.get(
    "/templates/{template_id}", response_model=TemplateRead, summary="Get one template"
)
def template_detail(template_id: str) -> TemplateRead:
    return get_template(template_id)


@router.get(
    "/templates/{template_id}/sample",
    response_model=SampleDataResponse,
    summary="Prefilled wizard data",
)
def template_sample(template_id: str) -> SampleDataResponse:
    return get_sample_data(template_id)


@router.get("/clauses", summary="Common clause suggestions")
def clauses() -> dict[str, Any]:
    return {"items": clause_suggestions()}


@router.get("/rewrite-actions", summary="Available AI section actions")
def rewrite_actions() -> dict[str, Any]:
    return {"items": [{"key": k, "label": v} for k, v in REWRITE_ACTION_LABELS.items()]}
