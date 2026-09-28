"""Branding profile and logo upload endpoints."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import BrandProfile
from app.schemas.branding import (
    BrandingListResponse,
    BrandingProfileCreate,
    BrandingProfileRead,
    LogoUploadResponse,
)
from app.utils.errors import NotFoundError, UploadError
from app.utils.security import (
    build_logo_filename,
    extension_for,
    validate_logo_upload,
)

logger = logging.getLogger("legalease.branding")

router = APIRouter(prefix="/api/branding", tags=["branding"])

MAX_UPLOAD_BYTES = settings.max_logo_bytes


def _logo_url(logo_path: str | None) -> str | None:
    if not logo_path:
        return None
    return f"/api/branding/logo/{logo_path}"


def _to_read(profile: BrandProfile) -> BrandingProfileRead:
    return BrandingProfileRead(
        id=profile.id,
        organization_name=profile.organization_name,
        logo_path=profile.logo_path,
        logo_url=_logo_url(profile.logo_path),
        address=profile.address,
        email=profile.email,
        phone=profile.phone,
        website=profile.website,
        footer_text=profile.footer_text,
        created_at=profile.created_at,
    )


@router.get("", response_model=BrandingListResponse, summary="List brand profiles")
def list_profiles(db: Session = Depends(get_db)) -> BrandingListResponse:
    rows = db.scalars(
        select(BrandProfile).order_by(BrandProfile.created_at.desc())
    ).all()
    return BrandingListResponse(
        items=[_to_read(r) for r in rows], total=len(rows)
    )


@router.post(
    "",
    response_model=BrandingProfileRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create or replace the active brand profile",
)
def upsert_profile(
    payload: BrandingProfileCreate, db: Session = Depends(get_db)
) -> BrandingProfileRead:
    """Creates a new profile, or updates the most recent one when no id is given."""
    if payload.id:
        profile = db.get(BrandProfile, payload.id)
        if profile is None:
            raise NotFoundError("That brand profile could not be found.")
    else:
        existing = db.scalar(
            select(BrandProfile).order_by(BrandProfile.created_at.desc()).limit(1)
        )
        profile = existing or BrandProfile()

    for field, value in payload.model_dump(exclude={"id"}, exclude_unset=True).items():
        if field == "logo_path" and value is None:
            continue  # never clear an existing logo via a text update
        setattr(profile, field, value)
    db.add(profile)
    db.commit()
    return _to_read(profile)


@router.post(
    "/logo",
    response_model=LogoUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a company logo",
)
async def upload_logo(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> LogoUploadResponse:
    """Validates by magic bytes, caps size and never trusts the filename."""
    settings.ensure_directories()

    # Read one byte past the limit so an oversized file is detected without
    # buffering the whole thing.
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    await file.close()

    if not data:
        raise UploadError("The uploaded file is empty.")

    detected = validate_logo_upload(data, file.content_type)

    stored_name = f"{uuid.uuid4().hex}{extension_for(detected)}"
    target = settings.logo_dir / stored_name
    # `stored_name` is a freshly generated hex string, so this cannot traverse.
    target.write_bytes(data)

    profile = db.scalar(select(BrandProfile).order_by(BrandProfile.created_at.desc()).limit(1))
    created = False
    if profile is None:
        profile = BrandProfile()
        created = True
    profile.logo_path = stored_name
    db.add(profile)
    db.commit()

    logger.info("stored logo %s (%s bytes) on %s profile", stored_name, len(data), "new" if created else "existing")
    return LogoUploadResponse(
        id=profile.id,
        logo_path=stored_name,
        logo_url=_logo_url(stored_name) or "",
        size_bytes=len(data),
        content_type=detected,
    )


@router.get("/logo/{stored_name}", summary="Serve a stored logo")
def get_logo(stored_name: str) -> FileResponse:
    """Lookup is by the opaque stored name only - no user-controlled path."""
    path = build_logo_filename(stored_name)
    return FileResponse(
        path,
        media_type="image/png" if path.lower().endswith(".png") else "image/jpeg",
        headers={"Cache-Control": "public, max-age=3600"},
    )
