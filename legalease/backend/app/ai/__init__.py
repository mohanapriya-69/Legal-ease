"""AI layer: Groq client, prompts, demo generator and orchestration."""

from app.ai.client import GroqClient, get_ai_client  # noqa: F401
from app.ai.demo import build_demo_draft, build_demo_revision  # noqa: F401
from app.ai.legal_generator import (  # noqa: F401
    GenerationResult,
    SectionRewriteResult,
    generate_document,
    rewrite_section,
)
from app.ai.prompts import (  # noqa: F401
    REWRITE_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_generation_prompt,
    build_rewrite_prompt,
)
from app.schemas.ai import REWRITE_ACTION_LABELS  # noqa: F401
