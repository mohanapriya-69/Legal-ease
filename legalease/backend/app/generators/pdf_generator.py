"""A4 PDF export built with ReportLab.

Produces a professional legal document: branded header with logo, numbered
sections, optional tables, signature blocks, a running footer with page numbers
and the legal disclaimer.
"""

from __future__ import annotations

import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.generators.layout import (
    BODY_FONT_SIZE,
    HEADING_FONT_SIZE,
    INK,
    LINE_SPACING,
    MARGIN_MM,
    MUTED,
    PDF_BODY_FONT,
    PDF_BOLD_FONT,
    RULE,
    SIGNATURE_FIELDS,
    TITLE_FONT_SIZE,
    paragraph_paragraph_space,
)
from app.models import BrandProfile, Document
from app.schemas.ai import DocumentContent, DocumentSection
from app.templates.disclaimer import EXPORT_DISCLAIMER
from app.utils.errors import ExportError
from app.utils.security import build_logo_filename

ACCENT = colors.HexColor("#8C6D1F")
INK_COLOR = colors.HexColor(INK)
MUTED_COLOR = colors.HexColor(MUTED)
RULE_COLOR = colors.HexColor(RULE)

_STYLES = {
    "title": ParagraphStyle(
        "DocTitle",
        fontName=PDF_BOLD_FONT,
        fontSize=TITLE_FONT_SIZE,
        leading=TITLE_FONT_SIZE * 1.3,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=INK_COLOR,
    ),
    "brand": ParagraphStyle(
        "Brand",
        fontName=PDF_BODY_FONT,
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=MUTED_COLOR,
    ),
    "heading": ParagraphStyle(
        "Heading",
        fontName=PDF_BOLD_FONT,
        fontSize=HEADING_FONT_SIZE,
        leading=HEADING_FONT_SIZE * 1.4,
        spaceBefore=14,
        spaceAfter=6,
        alignment=TA_LEFT,
        textColor=INK_COLOR,
    ),
    "body": ParagraphStyle(
        "Body",
        fontName=PDF_BODY_FONT,
        fontSize=BODY_FONT_SIZE,
        leading=BODY_FONT_SIZE * LINE_SPACING,
        alignment=TA_JUSTIFY,
        spaceAfter=paragraph_paragraph_space(),
        textColor=INK_COLOR,
    ),
    "bullet": ParagraphStyle(
        "Bullet",
        fontName=PDF_BODY_FONT,
        fontSize=BODY_FONT_SIZE,
        leading=BODY_FONT_SIZE * LINE_SPACING,
        leftIndent=14,
        bulletIndent=4,
        spaceAfter=3,
        alignment=TA_LEFT,
        textColor=INK_COLOR,
    ),
    "small": ParagraphStyle(
        "Small",
        fontName=PDF_BODY_FONT,
        fontSize=7.5,
        leading=10,
        alignment=TA_LEFT,
        textColor=MUTED_COLOR,
    ),
    "tablecell": ParagraphStyle(
        "TableCell",
        fontName=PDF_BODY_FONT,
        fontSize=9,
        leading=12,
        textColor=INK_COLOR,
    ),
    "disclaimer": ParagraphStyle(
        "Disclaimer",
        fontName=PDF_BODY_FONT,
        fontSize=8,
        leading=11,
        alignment=TA_JUSTIFY,
        textColor=MUTED_COLOR,
    ),
    "siglabel": ParagraphStyle(
        "SigLabel",
        fontName=PDF_BOLD_FONT,
        fontSize=10.5,
        leading=14,
        textColor=INK_COLOR,
    ),
    "sigfield": ParagraphStyle(
        "SigField",
        fontName=PDF_BODY_FONT,
        fontSize=9,
        leading=18,
        textColor=MUTED_COLOR,
    ),
}


def _esc(text: str) -> str:
    """Escape text for ReportLab's mini-markup parser.

    Generated and user-edited content is rendered as text only, never as
    markup, so a stray ``<`` or ``&`` cannot break or inject into the PDF.
    """
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _paragraphs(content: str) -> list[str]:
    return [block for block in (content or "").split("\n\n") if block.strip()]


def _logo_flowable(brand: BrandProfile | None, max_h: float = 16 * mm) -> Any | None:
    if brand is None or not brand.logo_path:
        return None
    try:
        path = build_logo_filename(brand.logo_path)
        image = Image(path)
        image._restrictSize(max_h * 4, max_h)  # noqa: SLF001 - ReportLab API
        return image
    except Exception:
        # A missing or corrupt logo must never fail the export.
        return None


def _table_flowable(section: DocumentSection) -> Table | None:
    table = section.table
    if table is None or (not table.headers and not table.rows):
        return None

    width = A4[0] - 2 * MARGIN_MM * mm
    column_count = max(
        len(table.headers), max((len(r) for r in table.rows), default=0), 1
    )
    col_width = width / column_count

    data: list[list[Any]] = []
    if table.headers:
        data.append(
            [Paragraph(f"<b>{_esc(h)}</b>", _STYLES["tablecell"]) for h in table.headers]
        )
    for row in table.rows:
        data.append([Paragraph(_esc(str(cell)), _STYLES["tablecell"]) for cell in row])

    rendered = Table(data, colWidths=[col_width] * column_count, repeatRows=1 if table.headers else 0)
    rendered.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, RULE_COLOR),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F4F0E6"))
                if table.headers
                else ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return rendered


def _signature_flowables(content: DocumentContent) -> list[Any]:
    flowables: list[Any] = [
        Paragraph("SIGNATURES", _STYLES["heading"]),
        Paragraph(
            "IN WITNESS WHEREOF, the Parties have executed this Agreement as of the "
            "Effective Date.",
            _STYLES["body"],
        ),
        Spacer(1, 8),
    ]

    blocks = content.signature_blocks or []
    column_count = max(len(blocks), 1)
    width = A4[0] - 2 * MARGIN_MM * mm
    col_width = width / column_count

    rows: list[list[Any]] = []
    for block in blocks:
        cell_flowables: list[Any] = [
            Paragraph(f"For and on behalf of <b>{_esc(block.party_label)}</b>", _STYLES["siglabel"])
        ]
        if block.role:
            cell_flowables.append(Paragraph(f"Capacity: {_esc(block.role)}", _STYLES["small"]))
        cell_flowables.append(Spacer(1, 6))
        for field in block.fields or SIGNATURE_FIELDS:
            cell_flowables.append(Paragraph(f"{_esc(field)}: " + "_" * 28, _STYLES["sigfield"]))
        rows.append([cell_flowables])

    grid = Table(rows, colWidths=[col_width] * column_count)
    grid.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    flowables.append(grid)
    return flowables


def _build_story(
    document: Document, content: DocumentContent, brand: BrandProfile | None
) -> list[Any]:
    story: list[Any] = []

    logo = _logo_flowable(brand)
    if logo is not None:
        story.append(logo)
        story.append(Spacer(1, 6))

    if brand and brand.organization_name:
        story.append(Paragraph(_esc(brand.organization_name), _STYLES["brand"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph(_esc(content.title), _STYLES["title"]))

    subtitle_bits: list[str] = []
    if content.subtitle:
        subtitle_bits.append(content.subtitle)
    if document.jurisdiction:
        subtitle_bits.append(document.jurisdiction)
    if subtitle_bits:
        story.append(Paragraph(_esc(" · ".join(subtitle_bits)), _STYLES["brand"]))

    story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT, spaceAfter=4))
    story.append(HRFlowable(width="100%", thickness=0.4, color=RULE_COLOR, spaceAfter=14))

    meta: list[str] = []
    if document.effective_date:
        meta.append(f"Effective date: {document.effective_date.isoformat()}")
    if content.generation and content.generation.generated_at:
        meta.append(f"Drafted: {content.generation.generated_at[:10]}")
    if meta:
        story.append(Paragraph(_esc("   |   ".join(meta)), _STYLES["brand"]))
        story.append(Spacer(1, 12))

    if content.intro:
        for block in _paragraphs(content.intro):
            story.append(Paragraph(_esc(block), _STYLES["body"]))

    for section in content.sections:
        block: list[Any] = [Paragraph(_esc(section.heading), _STYLES["heading"])]
        for text in _paragraphs(section.content):
            block.append(Paragraph(_esc(text), _STYLES["body"]))
        for bullet in section.bullets:
            block.append(Paragraph(_esc(bullet), _STYLES["bullet"], bulletText="•"))
        table = _table_flowable(section)
        if table is not None:
            block.extend([Spacer(1, 4), table, Spacer(1, 4)])

        if len(block) > 1:
            story.append(KeepTogether(block))
        else:
            story.extend(block)

    story.extend(_signature_flowables(content))

    story.append(Spacer(1, 18))
    story.append(HRFlowable(width="100%", thickness=0.4, color=RULE_COLOR, spaceAfter=6))
    story.append(
        Paragraph(_esc(content.disclaimer or EXPORT_DISCLAIMER), _STYLES["disclaimer"])
    )

    return story


def _make_page_callback(document: Document, content: DocumentContent, brand: BrandProfile | None):
    footer_text = (brand.footer_text if brand and brand.footer_text else "") or (
        "Generated by LegalEase"
    )

    def _draw(canvas: Any, doc: Any) -> None:
        canvas.saveState()
        width, height = A4

        canvas.setStrokeColor(ACCENT)
        canvas.setLineWidth(0.8)
        canvas.line(MARGIN_MM * mm, height - 16 * mm, width - MARGIN_MM * mm, height - 16 * mm)

        if brand and brand.organization_name:
            canvas.setFont(PDF_BODY_FONT, 8)
            canvas.setFillColor(MUTED_COLOR)
            canvas.drawString(MARGIN_MM * mm, height - 13 * mm, brand.organization_name)

        canvas.setFont(PDF_BODY_FONT, 8)
        canvas.setFillColor(MUTED_COLOR)
        canvas.drawRightString(
            width - MARGIN_MM * mm, height - 13 * mm, content.title[:70]
        )

        canvas.setStrokeColor(RULE_COLOR)
        canvas.setLineWidth(0.4)
        canvas.line(MARGIN_MM * mm, 16 * mm, width - MARGIN_MM * mm, 16 * mm)

        canvas.setFont(PDF_BODY_FONT, 7.5)
        canvas.setFillColor(MUTED_COLOR)
        canvas.drawString(MARGIN_MM * mm, 12 * mm, footer_text[:90])

        page_label = f"Page {doc.page}"
        canvas.drawRightString(width - MARGIN_MM * mm, 12 * mm, page_label)
        canvas.drawCentredString(
            width / 2, 8 * mm, "AI-assisted draft - not legal advice - review before signing"
        )

        canvas.restoreState()

    return _draw


def build_pdf(
    document: Document, content: DocumentContent, brand: BrandProfile | None
) -> bytes:
    """Render an A4 PDF and return its bytes."""
    try:
        buffer = io.BytesIO()
        doc = BaseDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=MARGIN_MM * mm,
            rightMargin=MARGIN_MM * mm,
            topMargin=24 * mm,
            bottomMargin=22 * mm,
            title=content.title or document.title,
            author=(brand.organization_name if brand else None) or "LegalEase",
            subject="AI-assisted legal document draft",
        )
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id="body",
        )
        doc.addPageTemplates(
            [
                PageTemplate(
                    id="legal",
                    frames=[frame],
                    onPage=_make_page_callback(document, content, brand),
                )
            ]
        )
        doc.build(_build_story(document, content, brand))
        return buffer.getvalue()
    except ExportError:
        raise
    except Exception as exc:
        raise ExportError(
            "The PDF could not be generated. Check the logo file and try again."
        ) from exc
