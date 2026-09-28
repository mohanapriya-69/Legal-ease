"""ORM models: Document, DocumentVersion, BrandProfile."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return uuid.uuid4().hex


class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    COMPLETED = "completed"


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    organization_name: Mapped[str | None] = mapped_column(String(200))
    logo_path: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(String(320))
    phone: Mapped[str | None] = mapped_column(String(60))
    website: Mapped[str | None] = mapped_column(String(255))
    footer_text: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    documents: Mapped[list["Document"]] = relationship(back_populates="brand")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    title: Mapped[str] = mapped_column(String(300), default="Untitled Document")
    document_type: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, native_enum=False, length=16),
        default=DocumentStatus.DRAFT,
        index=True,
    )
    content_json: Mapped[dict] = mapped_column(JSON, default=dict)

    brand_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("brand_profiles.id", ondelete="SET NULL"), nullable=True
    )
    jurisdiction: Mapped[str | None] = mapped_column(String(200))
    effective_date: Mapped[date | None] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )

    brand: Mapped[BrandProfile | None] = relationship(back_populates="documents")
    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentVersion.version_number.desc()",
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = (UniqueConstraint("document_id", "version_number"),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer)
    content_json: Mapped[dict] = mapped_column(JSON, default=dict)
    label: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    document: Mapped[Document] = relationship(back_populates="versions")
