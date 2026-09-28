"""Canonical legal disclaimer.

Single source of truth so the wizard, editor, landing page and exporters all
carry identical wording.
"""

from __future__ import annotations

LEGAL_DISCLAIMER = (
    "LegalEase provides AI-assisted drafting and general informational content. "
    "Generated documents are not a substitute for advice from a qualified legal "
    "professional. Laws vary by jurisdiction. Review important agreements with a "
    "licensed lawyer before signing."
)

LEGAL_DISCLAIMER_SHORT = (
    "AI-assisted draft. Not a substitute for advice from a qualified legal "
    "professional. Laws vary by jurisdiction."
)

# Short form used in exported footers / PDF pages where space is limited.
EXPORT_DISCLAIMER = (
    "This document was drafted with AI assistance by LegalEase and is provided for "
    "general informational purposes only. It is not legal advice and is not a "
    "substitute for review by a qualified legal professional. Laws vary by "
    "jurisdiction. Review before signing."
)

AI_MISSING_CONFIG_MESSAGE = (
    "AI configuration is missing. Add GROQ_API_KEY to backend/.env."
)

DEMO_BADGE = "Demo AI Response"

