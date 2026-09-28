"""Generate the LegalEase project report (.pdf).

Uses ReportLab's Platypus so the document reflows and paginates properly.
Content lives in ``content.py``, shared with the PPTX deck.

Run from anywhere:  python documents/build_pdf.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import content as C  # noqa: E402

OUT = Path(__file__).resolve().parent / "LegalEase-Project-Report.pdf"

INK = colors.Color(*C.INK)
SLATE = colors.Color(*C.SLATE)
MUTED = colors.Color(*C.MUTED)
GOLD = colors.Color(*C.GOLD)
GOLD_SOFT = colors.Color(*C.GOLD_SOFT)
PAPER = colors.Color(*C.PAPER)
RULE = colors.Color(*C.RULE)
TEAL = colors.Color(*C.TEAL)
TEAL_SOFT = colors.Color(*C.TEAL_SOFT)
RED = colors.Color(*C.RED)
RED_SOFT = colors.Color(*C.RED_SOFT)
GREEN = colors.Color(*C.GREEN)
GREEN_SOFT = colors.Color(*C.GREEN_SOFT)

PAGE_W, PAGE_H = A4
LM = RM = 22 * mm
TM = 20 * mm
BM = 20 * mm
CONTENT_W = PAGE_W - LM - RM

SERIF = "Times-Roman"
SERIF_B = "Times-Bold"
SERIF_I = "Times-Italic"
SANS = "Helvetica"
SANS_B = "Helvetica-Bold"
SANS_O = "Helvetica-Oblique"


def style(name, **kw) -> ParagraphStyle:
    return ParagraphStyle(name, **kw)


S = {
    "cover_kicker": style(
        "cover_kicker", fontName=SANS_B, fontSize=9, leading=12, textColor=GOLD, spaceAfter=6
    ),
    "cover_title": style(
        "cover_title", fontName=SERIF_B, fontSize=40, leading=45, textColor=INK, spaceAfter=4
    ),
    "cover_sub": style(
        "cover_sub", fontName=SERIF, fontSize=15, leading=20, textColor=SLATE, spaceAfter=14
    ),
    "cover_tag": style(
        "cover_tag", fontName=SANS, fontSize=8.5, leading=12, textColor=MUTED
    ),
    "h1": style(
        "h1", fontName=SERIF_B, fontSize=17, leading=21, textColor=INK, spaceBefore=2, spaceAfter=3
    ),
    "h2": style(
        "h2", fontName=SANS_B, fontSize=8.5, leading=11, textColor=GOLD, spaceAfter=5
    ),
    "body": style(
        "body",
        fontName=SERIF,
        fontSize=10.2,
        leading=15.4,
        textColor=INK,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    ),
    "lead": style(
        "lead",
        fontName=SERIF_I,
        fontSize=11,
        leading=16.5,
        textColor=SLATE,
        spaceAfter=10,
    ),
    "cell": style("cell", fontName=SANS, fontSize=8.6, leading=12, textColor=INK),
    "cell_b": style("cell_b", fontName=SANS_B, fontSize=8.6, leading=12, textColor=INK),
    "foot": style("foot", fontName=SANS, fontSize=7.2, leading=9, textColor=MUTED),
    "stat_num": style("stat_num", fontName=SERIF_B, fontSize=20, leading=23, textColor=GOLD),
    "stat_lab": style("stat_lab", fontName=SANS, fontSize=7.2, leading=9.5, textColor=SLATE),
}


def P(text: str, st: str = "body") -> Paragraph:
    return Paragraph(text, S[st])


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# --- Page furniture --------------------------------------------------------


def cover_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canvas.setFillColor(GOLD)
    canvas.rect(0, PAGE_H - 4 * mm, PAGE_W, 4 * mm, stroke=0, fill=1)
    canvas.setFillColor(GOLD)
    canvas.rect(LM, PAGE_H - 62 * mm, 34 * mm, 1.2, stroke=0, fill=1)
    canvas.setFont(SANS, 7.5)
    canvas.setFillColor(colors.Color(0.42, 0.47, 0.56))
    canvas.drawString(LM, 20 * mm, "Generated from the project record - all figures verified")
    canvas.restoreState()


def body_page(canvas, doc) -> None:
    canvas.saveState()
    # Header rule.
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(LM, PAGE_H - TM + 7 * mm, PAGE_W - RM, PAGE_H - TM + 7 * mm)
    canvas.setFont(SANS, 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(LM, PAGE_H - TM + 9.5 * mm, f"{C.PROJECT_NAME}  -  {C.TAGLINE}")
    canvas.drawRightString(
        PAGE_W - RM, PAGE_H - TM + 9.5 * mm, "Project report"
    )

    # Footer rule and page number.
    canvas.setStrokeColor(RULE)
    canvas.line(LM, BM + 6 * mm, PAGE_W - RM, BM + 6 * mm)
    canvas.setFont(SANS, 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(LM, BM, "Not legal advice. Generated documents require review by a qualified lawyer.")
    canvas.drawRightString(PAGE_W - RM, BM, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def build() -> Path:
    doc = BaseDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=LM,
        rightMargin=RM,
        topMargin=TM,
        bottomMargin=BM,
        title=f"{C.PROJECT_NAME} - {C.SUBTITLE}",
        author="Project record",
        subject=C.TAGLINE,
    )
    frame_cover = Frame(LM, BM, CONTENT_W, PAGE_H - TM - BM, id="cover")
    frame_body = Frame(LM, BM, CONTENT_W, PAGE_H - TM - BM - 4 * mm, id="body")
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=[frame_cover], onPage=cover_page),
            PageTemplate(id="body", frames=[frame_body], onPage=body_page),
        ]
    )

    story: list = []

    # --- Cover ---
    story += [
        Spacer(1, 96 * mm),
        P(C.TITLE_SLIDE["eyebrow"], "cover_kicker"),
        P(esc(C.TITLE_SLIDE["title"]), "cover_title"),
        P(esc(C.TITLE_SLIDE["subtitle"]), "cover_sub"),
        P(esc(C.TITLE_SLIDE["tagline"]), "cover_tag"),
        Spacer(1, 6 * mm),
    ]
    for line in C.TITLE_SLIDE["meta"]:
        story.append(P(esc(line), "cover_tag"))
    story.append(PageBreak())

    # --- Intro and stat band ---
    story.append(P("Executive summary", "h2"))
    story.append(P(esc(C.PROJECT_NAME), "h1"))
    story.append(P(esc(C.PDF_INTRO), "lead"))

    stat_cells = []
    for value, label, note in C.PDF_STATS:
        stat_cells.append(
            Paragraph(
                f'<font name="{SERIF_B}" size="20" color="#{GOLD.hexval()[2:]}">{esc(value)}</font><br/>'
                f'<font name="{SANS}" size="7.2" color="#{SLATE.hexval()[2:]}">{esc(label)}</font><br/>'
                f'<font name="{SANS}" size="6.6" color="#{MUTED.hexval()[2:]}">{esc(note)}</font>',
                S["cell"],
            )
        )
    band = Table([stat_cells], colWidths=[CONTENT_W / len(stat_cells)] * len(stat_cells))
    band.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(band)
    story.append(Spacer(1, 5 * mm))

    # --- Contents ---
    story.append(P("Contents", "h2"))
    toc_rows = [
        [
            Paragraph(f"{i:02d}", S["cell_b"]),
            Paragraph(esc(sec["heading"].split(".", 1)[-1].strip()), S["cell"]),
        ]
        for i, sec in enumerate(C.PDF_SECTIONS, 1)
    ]
    toc = Table(toc_rows, colWidths=[12 * mm, CONTENT_W - 12 * mm])
    toc.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("LINEBELOW", (0, 0), (-1, -2), 0.3, RULE),
                ("TEXTCOLOR", (0, 0), (0, -1), GOLD),
            ]
        )
    )
    story.append(toc)

    # --- Sections ---
    for index, section in enumerate(C.PDF_SECTIONS):
        story.append(PageBreak())
        block = [P(esc(section["heading"]), "h1")]
        for para in section["body"]:
            block.append(P(esc(para), "body"))
        story.append(KeepTogether(block[:1]))
        story.extend(block[1:])

    # --- Closing ---
    story.append(PageBreak())
    story.append(P("In summary", "h2"))
    story.append(P(esc(C.PROJECT_NAME), "h1"))
    story.append(Spacer(1, 2 * mm))
    story.append(
        Table(
            [[P(esc(C.PDF_CLOSING), "body")]],
            colWidths=[CONTENT_W],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), GOLD_SOFT),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.Color(0.83, 0.77, 0.62)),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ]
            ),
        )
    )

    doc.build(story)
    return OUT


if __name__ == "__main__":
    path = build()
    size = path.stat().st_size
    print(f"wrote {path}")
    print(f"size: {size:,} bytes")
