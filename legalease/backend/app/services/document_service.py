"""Document persistence, versioning and business logic."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import BrandProfile, Document, DocumentStatus, DocumentVersion
from app.schemas.ai import (
    DocumentContent,
    GenerateDocumentRequest,
    GenerationMeta,
    SignatureBlock,
    renumber_sections,
)
from app.schemas.document import (
    DashboardStats,
    DocumentSummary,
    DocumentUpdateRequest,
    DocumentVersionRead,
)
from app.utils.errors import NotFoundError

# --- Serialisation -----------------------------------------------------


def content_to_read(document: Document) -> DocumentContent:
    raw = document.content_json or {}
    try:
        return DocumentContent.model_validate(raw)
    except Exception:
        # A malformed stored row must not take down the whole listing.
        return DocumentContent(
            title=document.title,
            intro="",
            sections=[],
            signature_blocks=[],
            disclaimer="",
        )


def _word_count(content: DocumentContent) -> int:
    parts: list[str] = [content.title, content.intro, content.disclaimer]
    for section in content.sections:
        parts.append(section.heading)
        parts.append(section.content)
        parts.extend(section.bullets)
        if section.table:
            parts.extend(section.table.headers)
            for row in section.table.rows:
                parts.extend(row)
    return len(re.findall(r"\b\w+[\w'-]*\b", " ".join(p for p in parts if p)))


def _to_summary(document: Document) -> DocumentSummary:
    content = content_to_read(document)
    generation = content.generation
    return DocumentSummary(
        id=document.id,
        title=document.title,
        document_type=document.document_type,
        status=document.status.value
        if isinstance(document.status, DocumentStatus)
        else str(document.status),
        word_count=_word_count(content),
        section_count=len(content.sections),
        jurisdiction=document.jurisdiction,
        effective_date=document.effective_date,
        created_at=document.created_at,
        updated_at=document.updated_at,
        generation_source=generation.source if generation else None,
    )


def _canonical(content: dict[str, Any] | DocumentContent) -> str:
    """Stable representation used to skip no-op version snapshots."""
    data = content.to_dict() if isinstance(content, DocumentContent) else content
    volatile = ("generation",)
    trimmed = {k: v for k, v in (data or {}).items() if k not in volatile}
    return json.dumps(trimmed, sort_keys=True, default=str)


# --- Versioning --------------------------------------------------------


def create_version(
    db: Session,
    document: Document,
    *,
    content: dict[str, Any] | DocumentContent | None = None,
    label: str | None = None,
    force: bool = False,
) -> DocumentVersion | None:
    """Snapshot ``document``'s content.

    Returns ``None`` when the latest version already holds identical content,
    which keeps rapid autosaves from flooding the history.
    """
    payload = (
        content.to_dict()
        if isinstance(content, DocumentContent)
        else (content if content is not None else (document.content_json or {}))
    )

    latest = db.scalar(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document.id)
        .order_by(DocumentVersion.version_number.desc())
        .limit(1)
    )

    if latest is not None and not force:
        if _canonical(latest.content_json) == _canonical(payload):
            return None

    next_number = (latest.version_number + 1) if latest else 1

    version = DocumentVersion(
        document_id=document.id,
        version_number=next_number,
        content_json=payload,
        label=label,
    )
    db.add(version)
    return version


def list_versions(db: Session, document_id: str) -> Sequence[DocumentVersion]:
    return list(
        db.scalars(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
        )
    )


def restore_version(
    db: Session, document: Document, version_number: int
) -> Document:
    version = db.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == document.id,
            DocumentVersion.version_number == version_number,
        )
    )
    if version is None:
        raise NotFoundError(f"Version {version_number} was not found for this document.")

    # Snapshot the *current* state first so a restore is itself reversible.
    create_version(db, document, label=f"Before restoring v{version_number}", force=True)

    document.content_json = version.content_json
    try:
        restored = DocumentContent.model_validate(version.content_json or {})
        document.title = restored.title
    except Exception:
        pass
    document.updated_at = datetime.now(timezone.utc)
    db.flush()
    return document


def version_to_read(version: DocumentVersion) -> DocumentVersionRead:
    try:
        content = DocumentContent.model_validate(version.content_json or {})
    except Exception:
        content = DocumentContent(
            title="Restored document", sections=[], signature_blocks=[], disclaimer=""
        )
    return DocumentVersionRead(
        id=version.id,
        document_id=version.document_id,
        version_number=version.version_number,
        label=version.label,
        content=content,
        created_at=version.created_at,
    )


# --- CRUD --------------------------------------------------------------


def get_document(db: Session, document_id: str) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise NotFoundError("That document could not be found.")
    return document


def list_documents(
    db: Session,
    *,
    search: str | None = None,
    document_type: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[DocumentSummary], int]:
    stmt = select(Document)
    count_stmt = select(func.count(Document.id))

    conditions = []
    if search:
        pattern = f"%{search.strip()}%"
        conditions.append(Document.title.ilike(pattern))
    if document_type:
        conditions.append(Document.document_type == document_type)
    if status:
        conditions.append(Document.status == DocumentStatus(status))

    if conditions:
        stmt = stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)

    total = db.scalar(count_stmt) or 0
    rows = db.scalars(
        stmt.order_by(Document.updated_at.desc()).limit(limit).offset(offset)
    ).all()
    return [_to_summary(row) for row in rows], total


def dashboard_stats(db: Session) -> DashboardStats:
    def count_for(status_value: DocumentStatus) -> int:
        return (
            db.scalar(
                select(func.count(Document.id)).where(Document.status == status_value)
            )
            or 0
        )

    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if month_start.tzinfo is None:
        month_start = month_start.replace(tzinfo=timezone.utc)

    this_month = (
        db.scalar(
            select(func.count(Document.id)).where(Document.created_at >= month_start)
        )
        or 0
    )

    return DashboardStats(
        total_documents=db.scalar(select(func.count(Document.id))) or 0,
        drafts=count_for(DocumentStatus.DRAFT),
        generated=count_for(DocumentStatus.GENERATED),
        completed=count_for(DocumentStatus.COMPLETED),
        documents_this_month=this_month,
    )


def update_document(
    db: Session, document: Document, payload: DocumentUpdateRequest
) -> tuple[Document, DocumentVersion | None]:
    if payload.content is not None:
        content = payload.content
        renumber_sections(content.sections)
        if not content.signature_blocks:
            content.signature_blocks = [SignatureBlock(party_label="Authorised Signatory")]
        document.content_json = content.to_dict()
        document.title = content.title

    if payload.title:
        document.title = payload.title
    if payload.status:
        document.status = DocumentStatus(payload.status)
    if payload.brand_id is not None:
        if payload.brand_id:
            brand = db.get(BrandProfile, payload.brand_id)
            if brand is None:
                raise NotFoundError("That brand profile could not be found.")
        document.brand_id = payload.brand_id or None
    if payload.jurisdiction is not None:
        document.jurisdiction = payload.jurisdiction or None
    if payload.effective_date is not None:
        document.effective_date = payload.effective_date

    document.updated_at = datetime.now(timezone.utc)

    version = None
    if payload.create_version:
        version = create_version(
            db, document, label=payload.version_label or "Manual save"
        )

    db.flush()
    return document, version


def delete_document(db: Session, document: Document) -> None:
    db.delete(document)
    db.flush()


def duplicate_document(db: Session, document: Document) -> Document:
    source = content_to_read(document)
    content = source.model_copy(deep=True)
    content.title = f"{source.title} (Copy)"[:300]
    content.generation = GenerationMeta(
        source=source.generation.source if source.generation else "demo",
        model=source.generation.model if source.generation else None,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    clone = Document(
        title=content.title,
        document_type=document.document_type,
        status=DocumentStatus.DRAFT,
        content_json=content.to_dict(),
        brand_id=document.brand_id,
        jurisdiction=document.jurisdiction,
        effective_date=document.effective_date,
    )
    db.add(clone)
    db.flush()

    create_version(db, clone, label=f"Duplicated from {document.title[:60]}")
    db.flush()
    return clone


def apply_generated_document(
    db: Session,
    *,
    request: GenerateDocumentRequest,
    content: DocumentContent,
    brand: BrandProfile | None = None,
) -> Document:
    template_title = request.title or content.title
    document = Document(
        title=content.title or template_title,
        document_type=request.document_type,
        status=DocumentStatus.GENERATED,
        content_json=content.to_dict(),
        brand_id=brand.id if brand else None,
        jurisdiction=request.jurisdiction.summary()
        if not request.jurisdiction.is_empty()
        else None,
        effective_date=request.effective_date,
    )
    db.add(document)
    db.flush()

    create_version(db, document, label="Initial AI draft", force=True)
    db.flush()
    return document


def recent_days(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


__all__ = [
    "apply_generated_document",
    "content_to_read",
    "create_version",
    "dashboard_stats",
    "delete_document",
    "duplicate_document",
    "get_document",
    "list_documents",
    "list_versions",
    "recent_days",
    "restore_version",
    "update_document",
    "version_to_read",
]
