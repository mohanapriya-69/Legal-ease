"""Shared export layout constants.

One source of truth so the web preview (CSS), the PDF (ReportLab) and the
DOCX (python-docx) all agree on page geometry and typography.
"""

from __future__ import annotations

# A4 geometry in millimetres, matching the on-screen preview.
PAGE_WIDTH_MM = 210
PAGE_HEIGHT_MM = 297
MARGIN_MM = 25

# Typography, in points.
BODY_FONT_SIZE = 11
LINE_SPACING = 1.5
HEADING_FONT_SIZE = 12
TITLE_FONT_SIZE = 18

SERIF_FONT = "Times New Roman"  # canonical legal font, available in DOCX
PDF_BODY_FONT = "Times-Roman"
PDF_BOLD_FONT = "Times-Bold"
PDF_ITALIC_FONT = "Times-Italic"

INK = "#1A1A1A"
MUTED = "#5A5A5A"
RULE = "#B8B0A0"

SIGNATURE_FIELDS = ("Signature", "Name", "Title", "Date")


def paragraph_paragraph_space() -> float:
    """Extra space after a body paragraph, in points."""
    return BODY_FONT_SIZE * 0.6
