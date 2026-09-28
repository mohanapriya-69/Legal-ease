"""Document CRUD, generation, section rewriting, versioning and export."""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.ai.legal_generator import generate_document, rewrite_section
from app.database import get_db
from app.generators.docx_generator import build_docx
from app.generators.pdf_generator import build_pdf
from app.generators.txt_generator import build_txt
from app.models import BrandProfile, Document, DocumentStatus
from app.schemas.ai import (
    DocumentContent,
    GenerateDocumentRequest,
    RewriteSectionRequest,
)
from app.schemas.common import Page, PageMeta
from app.schemas.document import (
    DashboardStats,
    DocumentRead,
    DocumentStatusUpdate,
    DocumentSummary,
    DocumentUpdateRequest,
    DocumentVersionRead,
    GenerationResponse,
    RewriteResponse,
)
from app.services.document_service import (
    apply_generated_document,
    content_to_read,
    create_version,
    dashboard_stats,
    delete_document,
    duplicate_document,
    get_document,
    list_documents,
    list_versions,
    restore_version,
    update_document,
    version_to_read,
)
from app.utils.errors import NotFoundError
from app.utils.security import safe_download_filename

logger = logging.getLogger("legalease.documents")

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _to_read(document: Document) -> DocumentRead:
    return DocumentRead(
        id=document.id,
        title=document.title,
        document_type=document.document_type,
        status=document.status.value
        if isinstance(document.status, DocumentStatus)
        else str(document.status),
        content=content_to_read(document),
        brand_id=document.brand_id,
        jurisdiction=document.jurisdiction,
        effective_date=document.effective_date,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


# --- Generation --------------------------------------------------------


@router.post(
    "/generate",
    response_model=GenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a legal document with AI",
)
def generate(
    payload: GenerateDocumentRequest,
    db: Session = Depends(get_db),
) -> GenerationResponse:
    started = time.perf_counter()
    result = generate_document(payload)
    content = result.to_content()

    brand: BrandProfile | None = None
    branding = payload.branding
    if branding.brand_profile_id:
        brand = db.get(BrandProfile, branding.brand_profile_id)
        if brand is None:
            raise NotFoundError("The selected brand profile could not be found.")
    elif not branding.is_empty():
        brand = BrandProfile(
            organization_name=branding.organization_name,
            logo_path=branding.logo_path,
            address=branding.address,
            email=branding.email,
            phone=branding.phone,
            website=branding.website,
            footer_text=branding.footer_text,
        )
        db.add(brand)
        db.flush()

    document = apply_generated_document(
        db, request=payload, content=content, brand=brand
    )
    db.commit()

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    logger.info(
        "generated document %s type=%s source=%s in %sms",
        document.id,
        document.document_type,
        result.source,
        elapsed_ms,
    )

    return GenerationResponse(
        document=_to_read(document),
        generation_source=result.source,
        model=result.model,
        elapsed_ms=elapsed_ms,
        warnings=result.warnings,
    )


# --- CRUD --------------------------------------------------------------


@router.get("", response_model=Page[DocumentSummary], summary="List documents")
def documents(
    search: str | None = Query(default=None, max_length=200),
    document_type: str | None = Query(default=None, max_length=64),
    status_filter: str | None = Query(default=None, alias="status", max_length=16),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> Page[DocumentSummary]:
    items, total = list_documents(
        db,
        search=search,
        document_type=document_type,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return Page[DocumentSummary](
        items=items, meta=PageMeta(total=total, limit=limit, offset=offset)
    )


@router.get("/stats", response_model=DashboardStats, summary="Dashboard counters")
def stats(db: Session = Depends(get_db)) -> DashboardStats:
    return dashboard_stats(db)


@router.get("/{document_id}", response_model=DocumentRead, summary="Get one document")
def document_detail(document_id: str, db: Session = Depends(get_db)) -> DocumentRead:
    return _to_read(get_document(db, document_id))


@router.put("/{document_id}", response_model=DocumentRead, summary="Update a document")
def document_update(
    document_id: str,
    payload: DocumentUpdateRequest,
    db: Session = Depends(get_db),
) -> DocumentRead:
    document = get_document(db, document_id)
    update_document(db, document, payload)
    db.commit()
    return _to_read(document)


@router.patch(
    "/{document_id}/status",
    response_model=DocumentRead,
    summary="Update document status",
)
def document_status(
    document_id: str,
    payload: DocumentStatusUpdate,
    db: Session = Depends(get_db),
) -> DocumentRead:
    document = get_document(db, document_id)
    update_document(
        db, document, DocumentUpdateRequest(status=payload.status)
    )
    db.commit()
    return _to_read(document)


@router.delete(
    "/{document_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a document"
)
def document_delete(document_id: str, db: Session = Depends(get_db)) -> Response:
    document = get_document(db, document_id)
    delete_document(db, document)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{document_id}/duplicate",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate a document",
)
def document_duplicate(document_id: str, db: Session = Depends(get_db)) -> DocumentRead:
    clone = duplicate_document(db, get_document(db, document_id))
    db.commit()
    return _to_read(clone)


# --- AI section rewriting ---------------------------------------------


@router.post(
    "/{document_id}/rewrite-section",
    response_model=RewriteResponse,
    summary="Revise a single section with AI",
)
def document_rewrite_section(
    document_id: str,
    payload: RewriteSectionRequest,
    db: Session = Depends(get_db),
) -> RewriteResponse:
    document = get_document(db, document_id)
    content = content_to_read(document)

    # Snapshot before mutating so a rewrite is always reversible.
    create_version(
        db, document, label=f"Before AI rewrite: {payload.action}", force=True
    )

    result = rewrite_section(content, payload)
    content.sections[payload.section_index].content = result.text

    from app.schemas.ai import renumber_sections

    renumber_sections(content.sections)
    update_document(
        db, document, DocumentUpdateRequest(content=content, title=content.title)
    )
    version = create_version(
        db, document, label=f"AI rewrite: {payload.action.replace('_', ' ')}", force=True
    )
    db.commit()

    return RewriteResponse(
        document=_to_read(document),
        section_index=payload.section_index,
        action=payload.action,
        version_number=version.version_number if version else None,
        warnings=[]
        if result.source == "groq"
        else ["Demo AI response - no live model was called."],
    )


# --- Versions ----------------------------------------------------------


@router.get(
    "/{document_id}/versions",
    response_model=list[DocumentVersionRead],
    summary="Version history",
)
def document_versions(
    document_id: str, db: Session = Depends(get_db)
) -> list[DocumentVersionRead]:
    get_document(db, document_id)
    return [version_to_read(v) for v in list_versions(db, document_id)]


@router.post(
    "/{document_id}/versions/{version_number}/restore",
    response_model=DocumentRead,
    summary="Restore a previous version",
)
def document_version_restore(
    document_id: str, version_number: int, db: Session = Depends(get_db)
) -> DocumentRead:
    document = restore_version(db, get_document(db, document_id), version_number)
    db.commit()
    return _to_read(document)


# --- Exports -----------------------------------------------------------


def _export_context(db: Session, document: Document) -> tuple[DocumentContent, BrandProfile | None]:
    return content_to_read(document), (
        db.get(BrandProfile, document.brand_id) if document.brand_id else None
    )


@router.get("/{document_id}/export/pdf", summary="Export as PDF")
def export_pdf(
    document_id: str, db: Session = Depends(get_db)
) -> Response:
    document = get_document(db, document_id)
    content, brand = _export_context(db, document)
    data = build_pdf(document, content, brand)
    filename = safe_download_filename(document.title, ".pdf")
    return Response(
        content=data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(data)),
        },
    )


@router.get("/{document_id}/export/docx", summary="Export as DOCX")
def export_docx(
    document_id: str, db: Session = Depends(get_db)
) -> Response:
    document = get_document(db, document_id)
    content, brand = _export_context(db, document)
    data = build_docx(document, content, brand)
    filename = safe_download_filename(document.title, ".docx")
    return Response(
        content=data,
        media_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(data)),
        },
    )


@router.get("/{document_id}/export/txt", summary="Export as plain text")
def export_txt(
    document_id: str, db: Session = Depends(get_db)
) -> Response:
    document = get_document(db, document_id)
    content, brand = _export_context(db, document)
    text = build_txt(document, content, brand)
    filename = safe_download_filename(document.title, ".txt")
    return Response(
        content=text,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(text.encode("utf-8"))),
        },
    )
