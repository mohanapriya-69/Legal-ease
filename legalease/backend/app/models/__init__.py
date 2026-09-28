"""Model package. Importing it registers every table on the metadata."""

from app.models.document import (
    BrandProfile,
    Document,
    DocumentStatus,
    DocumentVersion,
)

__all__ = [
    "BrandProfile",
    "Document",
    "DocumentStatus",
    "DocumentVersion",
]
