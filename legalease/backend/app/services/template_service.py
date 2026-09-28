"""Serves the document template catalog to the frontend."""

from __future__ import annotations

from app.schemas.branding import (
    SampleDataResponse,
    TemplateListResponse,
    TemplateRead,
)
from app.templates.document_types import (
    CATEGORIES,
    DOCUMENT_TYPES,
    DocumentTypeDefinition,
    get_document_type,
)
from app.templates.sample_data import SAMPLE_DATA, get_sample
from app.utils.errors import NotFoundError


def _to_read(template: DocumentTypeDefinition) -> TemplateRead:
    return TemplateRead(
        id=template.id,
        title=template.title,
        slug=template.slug,
        description=template.description,
        category=template.category,
        icon=template.icon,
        estimated_minutes=template.estimated_minutes,
        default_title=template.default_title,
        suggested_sections=template.suggested_sections,
        suggested_clauses=template.suggested_clauses,
        sample=template.sample,
        popular=template.popular,
        has_sample_data=template.id in SAMPLE_DATA,
    )


def list_templates(
    *, search: str | None = None, category: str | None = None
) -> TemplateListResponse:
    """Filter the catalog. Works with zero database records."""
    items = list(DOCUMENT_TYPES)

    if category and category.lower() != "all":
        items = [t for t in items if t.category.lower() == category.lower()]

    if search:
        needle = search.strip().lower()
        items = [
            t
            for t in items
            if needle in t.title.lower()
            or needle in t.description.lower()
            or needle in t.category.lower()
        ]

    return TemplateListResponse(
        items=[_to_read(t) for t in items],
        total=len(items),
        categories=list(CATEGORIES),
    )


def get_template(template_id: str) -> TemplateRead:
    template = get_document_type(template_id)
    if template is None:
        raise NotFoundError("That document template could not be found.")
    return _to_read(template)


def get_sample_data(template_id: str) -> SampleDataResponse:
    template = get_document_type(template_id)
    if template is None:
        raise NotFoundError("That document template could not be found.")

    sample = get_sample(template.id)
    if sample is None:
        raise NotFoundError(
            f"No sample data is available for \"{template.title}\"."
        )
    return SampleDataResponse(
        document_type=template.id,
        label=sample["label"],
        summary=sample["summary"],
        payload=sample["payload"],
    )


def clause_suggestions() -> list[dict]:
    from app.templates.document_types import COMMON_CLAUSES

    return [dict(c) for c in COMMON_CLAUSES]
