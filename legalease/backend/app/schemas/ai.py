"""Request/response contracts for AI generation and document content.

``DocumentDraft`` is the structured output contract handed to the LLM via
``response_json_schema``. It is the single most important schema in the
project: the AI, the database, the preview and all three exporters agree on
this shape.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import settings

# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


class Party(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200, description="Full legal name")
    role: str = Field(min_length=1, max_length=120, description="Role in the agreement")
    organization: str | None = Field(default=None, max_length=200)
    address: str | None = Field(default=None, max_length=1000)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=60)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str | None) -> str | None:
        if not value:
            return None
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Enter a valid email address.")
        return value

    def display(self) -> str:
        return f"{self.name} ({self.role})"

    def as_context(self) -> str:
        bits = [f"Name: {self.name}", f"Role: {self.role}"]
        if self.organization:
            bits.append(f"Organization: {self.organization}")
        if self.address:
            bits.append(f"Address: {self.address}")
        if self.email:
            bits.append(f"Email: {self.email}")
        if self.phone:
            bits.append(f"Phone: {self.phone}")
        return "\n".join(bits)


class Clause(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    clause_key: str | None = Field(default=None, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=settings.max_free_text_chars)
    is_required: bool = True

    def as_context(self) -> str:
        flag = "required" if self.is_required else "optional"
        return f"{self.title} ({flag}): {self.description}"


class Jurisdiction(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    country: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, max_length=120)
    city: str | None = Field(default=None, max_length=120)
    governing_law: str | None = Field(default=None, max_length=300)

    def is_empty(self) -> bool:
        return not any((self.country, self.state, self.city, self.governing_law))

    def as_context(self) -> str:
        bits = []
        if self.governing_law:
            bits.append(f"Governing law: {self.governing_law}")
        location = ", ".join(p for p in (self.city, self.state, self.country) if p)
        if location:
            bits.append(f"Location: {location}")
        return "\n".join(bits)

    def summary(self) -> str:
        if self.governing_law:
            return self.governing_law
        location = ", ".join(p for p in (self.city, self.state, self.country) if p)
        return location or "Not specified"


class BrandingInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    organization_name: str | None = Field(default=None, max_length=200)
    brand_profile_id: str | None = Field(default=None, max_length=32)
    logo_path: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=1000)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=60)
    website: str | None = Field(default=None, max_length=255)
    footer_text: str | None = Field(default=None, max_length=500)

    def is_empty(self) -> bool:
        return not any(self.model_dump().values())


class GenerateDocumentRequest(BaseModel):
    """Payload posted to ``POST /api/documents/generate``."""

    model_config = ConfigDict(str_strip_whitespace=True)

    document_type: str = Field(min_length=1, max_length=64)
    parties: list[Party] = Field(default_factory=list, max_length=20)
    clauses: list[Clause] = Field(default_factory=list, max_length=60)
    effective_date: date | None = None
    expiry_date: date | None = None
    jurisdiction: Jurisdiction = Field(default_factory=Jurisdiction)
    branding: BrandingInput = Field(default_factory=BrandingInput)
    additional_instructions: str = Field(
        default="", max_length=settings.max_instructions_chars
    )
    title: str | None = Field(default=None, max_length=300)

    @field_validator("parties")
    @classmethod
    def _require_named_parties(cls, value: list[Party]) -> list[Party]:
        if not value:
            raise ValueError("At least one party is required to generate a document.")
        return value

    @field_validator("clauses")
    @classmethod
    def _require_clauses(cls, value: list[Clause]) -> list[Clause]:
        if not value:
            raise ValueError("Add at least one term or clause.")
        return value


class RewriteAction(str):
    pass


RewriteActionLiteral = Literal[
    "rewrite_professional",
    "simplify",
    "more_formal",
    "expand",
    "shorten",
    "fix_grammar",
    "add_protection",
]

REWRITE_ACTION_LABELS: dict[str, str] = {
    "rewrite_professional": "Rewrite professionally",
    "simplify": "Simplify language",
    "more_formal": "Make more formal",
    "expand": "Expand section",
    "shorten": "Shorten section",
    "fix_grammar": "Fix grammar",
    "add_protection": "Add protection clause",
}


class RewriteSectionRequest(BaseModel):
    """Only the target section plus the minimum surrounding context."""

    model_config = ConfigDict(str_strip_whitespace=True)

    section_index: int = Field(ge=0, le=200)
    action: RewriteActionLiteral = "rewrite_professional"
    custom_instruction: str = Field(
        default="", max_length=settings.max_instructions_chars
    )


# ---------------------------------------------------------------------------
# Document content contract (AI output, storage and export format)
# ---------------------------------------------------------------------------


class DocumentTable(BaseModel):
    """An optional inline table inside a section."""

    headers: list[str] = Field(default_factory=list, max_length=12)
    rows: list[list[str]] = Field(default_factory=list, max_length=60)
    caption: str | None = Field(default=None, max_length=300)


class DocumentSection(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    heading: str = Field(min_length=1, max_length=300)
    content: str = ""
    bullets: list[str] = Field(default_factory=list, max_length=40)
    table: DocumentTable | None = None


class SignatureBlock(BaseModel):
    party_label: str = Field(min_length=1, max_length=200)
    role: str | None = Field(default=None, max_length=120)
    fields: list[str] = Field(
        default_factory=lambda: ["Signature", "Name", "Title", "Date"],
        max_length=10,
    )


class GenerationMeta(BaseModel):
    source: Literal["groq", "demo"] = "groq"
    model: str | None = None
    generated_at: str | None = None
    disclaimer: str | None = None


class DocumentDraft(BaseModel):
    """The structured contract the LLM must satisfy.

    Passed to the model as a ``json_schema`` response format and validated
    again on the way back in, so a malformed response becomes a clean 502
    rather than a corrupted document.
    """

    title: str = Field(min_length=1, max_length=300)
    intro: str = Field(default="", max_length=4000)
    sections: list[DocumentSection] = Field(
        default_factory=list, min_length=1, max_length=60
    )
    signature_blocks: list[SignatureBlock] = Field(
        default_factory=list, max_length=10
    )
    disclaimer: str = Field(min_length=1, max_length=2000)


class DocumentContent(BaseModel):
    """What actually gets persisted in ``Document.content_json``."""

    title: str = Field(min_length=1, max_length=300)
    subtitle: str | None = Field(default=None, max_length=300)
    intro: str = ""
    sections: list[DocumentSection] = Field(default_factory=list)
    signature_blocks: list[SignatureBlock] = Field(default_factory=list)
    disclaimer: str = ""
    generation: GenerationMeta | None = None

    def to_dict(self) -> dict:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict | None) -> "DocumentContent":
        return cls.model_validate(data or {})


def renumber_sections(sections: list[DocumentSection]) -> list[DocumentSection]:
    """Apply sequential ``N.`` prefixes to headings that lack one.

    The AI is asked for numbered headings, but user edits and restores can
    leave gaps - this keeps the document consistent without touching wording.
    """
    import re

    for index, section in enumerate(sections, start=1):
        stripped = re.sub(r"^\s*\d+(\.\d+)*[.)]?\s+", "", section.heading).strip()
        section.heading = f"{index}. {stripped}" if stripped else f"{index}."
    return sections

