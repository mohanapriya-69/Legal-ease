"""Legal document generation orchestration.

Decides between the live Groq path and the deterministic demo path, builds
the prompts, validates the result and returns a consistent result object
regardless of which path ran.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from app.ai.client import get_ai_client
from app.ai.demo import build_demo_draft, build_demo_revision
from app.ai.prompts import (
    REWRITE_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_generation_prompt,
    build_rewrite_prompt,
)
from app.config import settings
from app.schemas.ai import (
    DocumentContent,
    DocumentDraft,
    DocumentSection,
    GenerateDocumentRequest,
    GenerationMeta,
    RewriteSectionRequest,
    SignatureBlock,
    renumber_sections,
)
from app.templates.disclaimer import LEGAL_DISCLAIMER
from app.templates.document_types import get_document_type
from app.utils.errors import AINotConfiguredError, AppError

logger = logging.getLogger("legalease.generator")

Source = Literal["groq", "demo"]


class SectionRevision(BaseModel):
    """Output contract for a single-section revision.

    Declared as a module-level model because its JSON schema is handed to the
    LLM, and Pydantic requires a stable, named type to generate it.
    """

    revised_text: str = Field(description="The revised clause text, without a heading.")


class GenerationResult:
    """A validated draft plus provenance metadata."""

    __slots__ = ("draft", "source", "model", "warnings")

    def __init__(
        self,
        draft: DocumentDraft,
        source: Source,
        model: str | None,
        warnings: list[str] | None = None,
    ) -> None:
        self.draft = draft
        self.source = source
        self.model = model
        self.warnings = warnings or []

    def to_content(self) -> DocumentContent:
        """Normalise the AI draft into the persisted document contract."""
        sections = [
            DocumentSection(
                id=section.id or section.heading[:12],
                heading=section.heading,
                content=section.content,
                bullets=section.bullets,
                table=section.table,
            )
            for section in self.draft.sections
        ]
        renumber_sections(sections)

        signature_blocks = self.draft.signature_blocks or [
            SignatureBlock(party_label="Authorised Signatory")
        ]

        return DocumentContent(
            title=self.draft.title,
            subtitle=None,
            intro=self.draft.intro,
            sections=sections,
            signature_blocks=signature_blocks,
            disclaimer=self.draft.disclaimer or LEGAL_DISCLAIMER,
            generation=GenerationMeta(
                source=self.source,
                model=self.model,
                generated_at=datetime.now(timezone.utc).isoformat(),
                disclaimer=LEGAL_DISCLAIMER,
            ),
        )


class SectionRewriteResult:
    __slots__ = ("text", "source", "model")

    def __init__(self, text: str, source: Source, model: str | None) -> None:
        self.text = text
        self.source = source
        self.model = model


def _resolve_template(request: GenerateDocumentRequest):
    """Find the catalog entry, falling back to a generic custom template."""
    template = get_document_type(request.document_type)
    if template is not None:
        return template

    from app.templates.document_types import DOCUMENT_TYPES

    return next(t for t in DOCUMENT_TYPES if t.id == "custom")


def generate_document(request: GenerateDocumentRequest) -> GenerationResult:
    """Generate a full draft. Raises :class:`AppError` on failure."""
    template = _resolve_template(request)

    if settings.ai_mode == "demo":
        logger.info("Generating document in DEMO mode (type=%s)", template.id)
        draft = build_demo_draft(
            request,
            template_title=template.title,
            template_sections=template.suggested_sections,
        )
        return GenerationResult(draft, "demo", "demo", ["Demo AI response - no live model was called."])

    if settings.ai_mode == "unconfigured":
        raise AINotConfiguredError()

    prompt = build_generation_prompt(
        document_type_title=template.title,
        document_type_description=template.description,
        suggested_sections=template.suggested_sections,
        request=request,
    )

    draft = get_ai_client().generate_structured(
        system_instruction=SYSTEM_PROMPT,
        prompt=prompt,
        response_model=DocumentDraft,
    )

    if not isinstance(draft, DocumentDraft):  # pragma: no cover - defensive
        raise AppError("The AI service returned an unexpected response.")

    warnings: list[str] = []
    required = [c for c in request.clauses if c.is_required]
    headings = {s.heading.strip().lower() for s in draft.sections}
    for clause in required:
        if not any(clause.title.strip().lower() in h for h in headings):
            warnings.append(
                f"The draft may not address the requested clause \"{clause.title}\"."
            )

    if not draft.signature_blocks:
        warnings.append("The draft did not include signature blocks.")

    return GenerationResult(draft, "groq", settings.groq_model, warnings)


def rewrite_section(
    content: DocumentContent,
    request: RewriteSectionRequest,
) -> SectionRewriteResult:
    """Revise a single section, sending only the required context."""
    index = request.section_index
    if index >= len(content.sections):
        from app.utils.errors import NotFoundError

        raise NotFoundError("That section no longer exists in this document.")

    section = content.sections[index]
    previous = content.sections[index - 1].heading if index > 0 else None
    following = (
        content.sections[index + 1].heading
        if index + 1 < len(content.sections)
        else None
    )

    if settings.ai_mode == "demo":
        text = build_demo_revision(
            heading=section.heading,
            content=section.content,
            action=request.action,
            custom_instruction=request.custom_instruction,
        )
        return SectionRewriteResult(text, "demo", "demo")

    if settings.ai_mode == "unconfigured":
        raise AINotConfiguredError()

    prompt = build_rewrite_prompt(
        action=request.action,
        heading=section.heading,
        content=section.content,
        custom_instruction=request.custom_instruction,
        document_title=content.title,
        previous_heading=previous,
        next_heading=following,
    )

    result = get_ai_client().generate_structured(
        system_instruction=REWRITE_SYSTEM_PROMPT,
        prompt=prompt,
        response_model=SectionRevision,
        temperature=0.25,
        max_output_tokens=2048,
    )

    text = (result.revised_text or "").strip()
    if not text:
        from app.utils.errors import AIInvalidResponseError

        raise AIInvalidResponseError(
            "The AI service returned an empty revision. Please try again."
        )

    return SectionRewriteResult(text, "groq", settings.groq_model)
