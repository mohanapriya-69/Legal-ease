"""Pydantic schema package."""

from app.schemas.ai import (  # noqa: F401
    BrandingInput,
    Clause,
    DocumentContent,
    DocumentDraft,
    DocumentSection,
    DocumentTable,
    GenerationMeta,
    GenerateDocumentRequest,
    Jurisdiction,
    Party,
    RewriteSectionRequest,
    SignatureBlock,
    renumber_sections,
)
from app.schemas.branding import (  # noqa: F401
    BrandingListResponse,
    BrandingProfileCreate,
    BrandingProfileRead,
    LogoUploadResponse,
    SampleDataResponse,
    TemplateListResponse,
    TemplateRead,
)
from app.schemas.common import ErrorResponse, HealthResponse, Page  # noqa: F401
from app.schemas.document import (  # noqa: F401
    DashboardStats,
    DocumentRead,
    DocumentStatusUpdate,
    DocumentSummary,
    DocumentUpdateRequest,
    DocumentVersionRead,
    GenerationResponse,
    RewriteResponse,
)
