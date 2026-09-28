"""DOCX export built with python-docx.

Uses Times New Roman throughout, A4 with 2.5 cm margins, numbered sections,
inline tables, a logo header block, signature tables and a page-numbered footer.
"""

from __future__ import annotations

import io

from docx import Document as DocxDocument
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from app.generators.layout import (
    BODY_FONT_SIZE,
    HEADING_FONT_SIZE,
    LINE_SPACING,
    MARGIN_MM,
    SERIF_FONT,
    SIGNATURE_FIELDS,
    TITLE_FONT_SIZE,
    paragraph_paragraph_space,
)
from app.models import BrandProfile, Document
from app.schemas.ai import DocumentContent
from app.templates.disclaimer import EXPORT_DISCLAIMER
from app.utils.errors import ExportError
from app.utils.security import build_logo_filename

INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x5A, 0x5A, 0x5A)
ACCENT = RGBColor(0x8C, 0x6D, 0x1F)


def _style_run(run, *, size: float, bold: bool = False, italic: bool = False, color=INK) -> None:
    run.font.name = SERIF_FONT
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color
    # Ensure the East Asian font mapping also resolves to the legal font.
    rpr = run._element.get_or_add_rPr()  # noqa: SLF001 - python-docx API
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attribute in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attribute), SERIF_FONT)


def _add_bottom_border(paragraph, color: str = "8C6D1F", size: int = 8) -> None:
    ppr = paragraph._p.get_or_add_pPr()  # noqa: SLF001
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), color)
    borders.append(bottom)
    ppr.append(borders)


def _set_spacing(paragraph, *, after: float = 0, before: float = 0, line: float = LINE_SPACING) -> None:
    fmt = paragraph.paragraph_format
    fmt.space_after = Pt(after)
    fmt.space_before = Pt(before)
    fmt.line_spacing = line


def _add_page_number_footer(section, text: str) -> None:
    footer = section.footer
    paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_spacing(paragraph, after=0, line=1.0)

    run = paragraph.add_run(f"{text}   |   Page ")
    _style_run(run, size=7.5, color=MUTED)

    # PAGE / NUMPAGES field codes.
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_text = OxmlElement("w:t")
    fld_text.text = "1"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")

    page_run = paragraph.add_run()
    _style_run(page_run, size=7.5, color=MUTED)
    page_run._r.append(fld_begin)  # noqa: SLF001
    page_run._r.append(instr)  # noqa: SLF001
    page_run._r.append(fld_sep)  # noqa: SLF001
    page_run._r.append(fld_text)  # noqa: SLF001
    page_run._r.append(fld_end)  # noqa: SLF001

    of_run = paragraph.add_run(" of ")
    _style_run(of_run, size=7.5, color=MUTED)

    num_run = paragraph.add_run()
    _style_run(num_run, size=7.5, color=MUTED)
    for tag, value in (("begin", None), ("instr", " NUMPAGES "), ("separate", None), ("text", "1"), ("end", None)):
        element = OxmlElement("w:fldChar" if tag in ("begin", "separate", "end") else f"w:{tag}")
        if tag in ("begin", "separate", "end"):
            element.set(qn("w:fldCharType"), tag)
        elif tag == "instr":
            element.set(qn("xml:space"), "preserve")
            element.text = value
        else:
            element.text = value
        num_run._r.append(element)  # noqa: SLF001


def _add_header(section, content: DocumentContent, brand: BrandProfile | None) -> None:
    header = section.header
    paragraph = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_spacing(paragraph, after=0, line=1.0)

    if brand and brand.logo_path:
        try:
            path = build_logo_filename(brand.logo_path)
            run = paragraph.add_run()
            run.add_picture(path, width=Cm(2.6))
        except Exception:
            pass  # a bad logo must not fail the export

    if brand and brand.organization_name:
        name_p = header.add_paragraph()
        name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _set_spacing(name_p, after=0, line=1.0)
        _style_run(name_p.add_run(brand.organization_name), size=9, color=MUTED)

    rule = header.add_paragraph()
    _set_spacing(rule, after=0, line=1.0)
    _add_bottom_border(rule)


def _body_paragraph(doc: DocxDocument, text: str, *, italic: bool = False, color=INK, size: float = BODY_FONT_SIZE):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    _set_spacing(paragraph, after=paragraph_paragraph_space(), line=LINE_SPACING)
    _style_run(paragraph.add_run(text), size=size, italic=italic, color=color)
    return paragraph


def build_docx(
    document: Document, content: DocumentContent, brand: BrandProfile | None
) -> bytes:
    """Render a .docx and return its bytes."""
    try:
        doc = DocxDocument()

        normal = doc.styles["Normal"]
        normal.font.name = SERIF_FONT
        normal.font.size = Pt(BODY_FONT_SIZE)
        rpr = normal.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        for attribute in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rfonts.set(qn(attribute), SERIF_FONT)
        normal.paragraph_format.line_spacing = LINE_SPACING
        normal.paragraph_format.space_after = Pt(paragraph_paragraph_space())

        section = doc.sections[0]
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.left_margin = Cm(MARGIN_MM / 10)
        section.right_margin = Cm(MARGIN_MM / 10)
        section.top_margin = Cm(2.4)
        section.bottom_margin = Cm(2.2)

        _add_header(section, content, brand)

        footer_text = (brand.footer_text if brand and brand.footer_text else "Generated by LegalEase")
        _add_page_number_footer(section, footer_text)

        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _set_spacing(title_p, before=6, after=4, line=1.2)
        _style_run(title_p.add_run(content.title), size=TITLE_FONT_SIZE, bold=True)
        _add_bottom_border(title_p, color="8C6D1F", size=12)

        meta_bits: list[str] = []
        if content.subtitle:
            meta_bits.append(content.subtitle)
        if document.jurisdiction:
            meta_bits.append(document.jurisdiction)
        if document.effective_date:
            meta_bits.append(f"Effective {document.effective_date.isoformat()}")
        if meta_bits:
            meta_p = doc.add_paragraph()
            meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _set_spacing(meta_p, after=10, line=1.0)
            _style_run(meta_p.add_run("  |  ".join(meta_bits)), size=9, color=MUTED)

        if content.intro:
            for block in content.intro.split("\n\n"):
                if block.strip():
                    _body_paragraph(doc, block.strip())

        for doc_section in content.sections:
            heading = doc.add_paragraph()
            _set_spacing(heading, before=12, after=4, line=1.2)
            _style_run(heading.add_run(doc_section.heading), size=HEADING_FONT_SIZE, bold=True)
            heading.paragraph_format.keep_with_next = True

            for block in doc_section.content.split("\n\n"):
                if block.strip():
                    _body_paragraph(doc, block.strip())

            for bullet in doc_section.bullets:
                bullet_p = doc.add_paragraph(style="List Bullet")
                _set_spacing(bullet_p, after=3, line=LINE_SPACING)
                _style_run(bullet_p.add_run(bullet), size=BODY_FONT_SIZE)

            table = doc_section.table
            if table and (table.headers or table.rows):
                if table.caption:
                    caption_p = doc.add_paragraph()
                    _set_spacing(caption_p, before=6, after=3, line=1.0)
                    _style_run(
                        caption_p.add_run(table.caption), size=9, bold=True, color=ACCENT
                    )
                column_count = max(
                    len(table.headers), max((len(r) for r in table.rows), default=0), 1
                )
                rows = table.rows or [[""]]
                # The header occupies its own row, so the table needs one extra.
                header_rows = 1 if table.headers else 0
                rendered = doc.add_table(
                    rows=len(rows) + header_rows, cols=column_count
                )
                rendered.style = "Table Grid"
                rendered.alignment = WD_TABLE_ALIGNMENT.CENTER
                for c, header in enumerate(table.headers):
                    cell = rendered.rows[0].cells[c]
                    cell.text = ""
                    _style_run(cell.paragraphs[0].add_run(header), size=9, bold=True)
                for r, row in enumerate(table.rows, start=header_rows):
                    for c, value in enumerate(row):
                        if c >= column_count:
                            break
                        cell = rendered.rows[r].cells[c]
                        cell.text = ""
                        _style_run(cell.paragraphs[0].add_run(str(value)), size=9)
                doc.add_paragraph()

        # --- Signatures ---
        sig_heading = doc.add_paragraph()
        _set_spacing(sig_heading, before=16, after=4, line=1.2)
        _style_run(sig_heading.add_run("SIGNATURES"), size=HEADING_FONT_SIZE, bold=True)

        _body_paragraph(
            doc,
            "IN WITNESS WHEREOF, the Parties have executed this Agreement as of the "
            "Effective Date.",
        )

        blocks = content.signature_blocks or []
        column_count = max(len(blocks), 1)
        sig_table = doc.add_table(rows=1, cols=column_count)
        for index, block in enumerate(blocks):
            cell = sig_table.rows[0].cells[index]
            cell.text = ""
            first = cell.paragraphs[0]
            _set_spacing(first, after=2, line=1.1)
            _style_run(
                first.add_run(f"For and on behalf of {block.party_label}"), size=10.5, bold=True
            )
            if block.role:
                role_p = cell.add_paragraph()
                _set_spacing(role_p, after=6, line=1.0)
                _style_run(role_p.add_run(f"Capacity: {block.role}"), size=9, color=MUTED)
            for field in block.fields or SIGNATURE_FIELDS:
                field_p = cell.add_paragraph()
                _set_spacing(field_p, after=6, line=1.0)
                _style_run(field_p.add_run(f"{field}: " + "_" * 30), size=9, color=MUTED)

        disclaimer_p = doc.add_paragraph()
        _set_spacing(disclaimer_p, before=20, after=0, line=1.2)
        _style_run(
            disclaimer_p.add_run(content.disclaimer or EXPORT_DISCLAIMER),
            size=8,
            italic=True,
            color=MUTED,
        )

        buffer = io.BytesIO()
        doc.save(buffer)
        return buffer.getvalue()
    except ExportError:
        raise
    except Exception as exc:
        raise ExportError(
            "The DOCX could not be generated. Check the logo file and try again."
        ) from exc
