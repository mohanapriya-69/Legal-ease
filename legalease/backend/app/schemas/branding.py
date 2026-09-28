"""Branding and template API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ai import BrandingInput


class BrandingProfileCreate(BrandingInput):
    """A brand profile.

    ``id`` is the profile to update. Omit it to create, or to update the most
    recently created profile.
    """

    id: str | None = Field(default=None, max_length=32)


class BrandingProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_name: str | None = None
    logo_path: str | None = None
    logo_url: str | None = None
    address: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    footer_text: str | None = None
    created_at: datetime


class BrandingListResponse(BaseModel):
    items: list[BrandingProfileRead]
    total: int


class LogoUploadResponse(BaseModel):
    id: str
    logo_path: str
    logo_url: str
    size_bytes: int
    content_type: str


class TemplateRead(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    category: str
    icon: str
    estimated_minutes: int
    default_title: str
    suggested_sections: list[str]
    suggested_clauses: list[str]
    sample: bool
    popular: bool
    has_sample_data: bool = False


class TemplateListResponse(BaseModel):
    items: list[TemplateRead]
    total: int
    categories: list[str]


class SampleDataResponse(BaseModel):
    document_type: str
    label: str
    summary: str
    payload: dict
