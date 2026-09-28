"""Document and version API schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ai import DocumentContent


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    document_type: str
    status: str
    content: DocumentContent
    brand_id: str | None = None
    jurisdiction: str | None = None
    effective_date: date | None = None
    created_at: datetime
    updated_at: datetime


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    document_type: str
    status: str
    word_count: int = 0
    section_count: int = 0
    jurisdiction: str | None = None
    effective_date: date | None = None
    created_at: datetime
    updated_at: datetime
    generation_source: str | None = None


class DocumentUpdateRequest(BaseModel):
    """Partial update. Omitted fields are left untouched."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=300)
    content: DocumentContent | None = None
    status: str | None = Field(default=None, pattern="^(draft|generated|completed)$")
    brand_id: str | None = None
    jurisdiction: str | None = Field(default=None, max_length=200)
    effective_date: date | None = None
    create_version: bool = False
    version_label: str | None = Field(default=None, max_length=200)


class DocumentStatusUpdate(BaseModel):
    status: str = Field(pattern="^(draft|generated|completed)$")


class DocumentVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    version_number: int
    label: str | None = None
    content: DocumentContent
    created_at: datetime


class DashboardStats(BaseModel):
    total_documents: int
    drafts: int
    generated: int
    completed: int
    documents_this_month: int


class GenerationResponse(BaseModel):
    document: DocumentRead
    generation_source: str
    model: str | None = None
    elapsed_ms: int
    warnings: list[str] = Field(default_factory=list)


class RewriteResponse(BaseModel):
    document: DocumentRead
    section_index: int
    action: str
    version_number: int | None = None
    warnings: list[str] = Field(default_factory=list)


def content_to_dict(content: DocumentContent | dict[str, Any] | None) -> dict[str, Any]:
    if isinstance(content, DocumentContent):
        return content.to_dict()
    return content or {}
