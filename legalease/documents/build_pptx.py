"""Generate the LegalEase project presentation (.pptx).

Content lives in ``content.py`` so the deck and the PDF report cannot drift
apart. Run from anywhere:  python documents/build_pptx.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))

import content as C  # noqa: E402

OUT = Path(__file__).resolve().parent / "LegalEase-Project-Presentation.pptx"

# 16:9 canvas, in inches
W, H = 13.333, 7.5
MARGIN = 0.85
CONTENT_W = W - 2 * MARGIN


def rgb(triple) -> RGBColor:
    return RGBColor(*triple)


def blank(prs: Presentation, bg=C.PAPER) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bgshape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bgshape.fill.solid()
    bgshape.fill.fore_color.rgb = rgb(bg)
    bgshape.line.fill.background()
    bgshape.shadow.inherit = False
    return slide


def textbox(
    slide,
    x,
    y,
    w,
    h,
    text,
    *,
    size=18,
    color=C.INK,
    bold=False,
    font="Georgia",
    align=PP_ALIGN.LEFT,
    spacing=1.0,
    anchor=MSO_ANCHOR.TOP,
    italic=False,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    lines = text.split("\n")
    for index, line in enumerate(lines):
        para = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        para.alignment = align
        para.line_spacing = spacing
        run = para.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.name = font
        run.font.color.rgb = rgb(color)
    return box


def rect(
    slide,
    x,
    y,
    w,
    h,
    *,
    fill=None,
    line=None,
    line_w=1.0,
    shape=MSO_SHAPE.ROUNDED_RECTANGLE,
    radius=0.04,
):
    shp = slide.shapes.add_shape(
        shape, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(line_w)
    shp.shadow.inherit = False
    # Rounded-rectangle adjustment value controls corner radius.
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            shp.adjustments[0] = radius
        except (IndexError, ValueError):
            pass
    return shp


# Vertical space reserved above the footer rule.
FOOTER_TOP = H - 0.78

# Rough advance width as a fraction of point size, used to predict line counts.
# Generous on purpose: over-reserving space is harmless, under-reserving
# overflows. Verdana (the sans face) is wider than Georgia, so it sets the bar.
ADVANCE = 0.62
ADVANCE_SERIF = 0.505


def wrapped_lines(text: str, box_in: float, size: float, serif: bool = False) -> int:
    """Predict how many lines ``text`` needs inside a box ``box_in`` wide."""
    adv = ADVANCE_SERIF if serif else ADVANCE
    per_line = max(1, int((box_in * 72) / (size * adv)))
    total = 0
    for paragraph in text.split("\n"):
        total += max(1, -(-len(paragraph) // per_line))
    return total


def rows_fit(y: float, count: int, gap: float, reserve: float = 0.0) -> float:
    """Per-row height that fits ``count`` rows in the space left below ``y``."""
    space = FOOTER_TOP - y - reserve
    return max(0.3, (space - gap * (count - 1)) / count)


def split_gap(y: float, row_h: float, count: int, max_gap: float) -> float:
    """Gap that keeps ``count`` rows of ``row_h`` above the footer.

    Returns the gap to use. When the rows genuinely do not fit even at the
    minimum gap, the caller is told so via a non-positive sentinel rather than
    being allowed to draw off the canvas.
    """
    if count <= 1:
        return 0.0
    slack = FOOTER_TOP - y - row_h * count
    return min(max_gap, slack / (count - 1))


def header(slide, eyebrow: str, title: str, lead: str | None = None) -> float:
    """Draw the standard slide header. Returns the y where content may start."""
    textbox(
        slide,
        MARGIN,
        0.55,
        CONTENT_W,
        0.3,
        eyebrow,
        size=11,
        color=C.GOLD,
        bold=True,
        font="Verdana",
    )
    textbox(
        slide,
        MARGIN,
        0.92,
        CONTENT_W,
        0.75,
        title,
        size=32,
        color=C.INK,
        bold=True,
        font="Georgia",
    )
    y = 1.78
    if lead:
        lead_w = CONTENT_W - 0.6
        lines = wrapped_lines(lead, lead_w, 14, serif=True)
        textbox(
            slide,
            MARGIN,
            y,
            lead_w,
            0.6,
            lead,
            size=14,
            color=C.SLATE,
            font="Georgia",
            italic=True,
            spacing=1.25,
        )
        y += lines * (14 * 1.25 / 72) + 0.16
    rect(slide, MARGIN, y, 1.5, 0.035, fill=C.GOLD, shape=MSO_SHAPE.RECTANGLE)
    return y + 0.3


def footer(slide, number: int) -> None:
    rect(
        slide,
        MARGIN,
        H - 0.72,
        CONTENT_W,
        0.012,
        fill=C.RULE,
        shape=MSO_SHAPE.RECTANGLE,
    )
    textbox(
        slide,
        MARGIN,
        H - 0.58,
        CONTENT_W - 0.75,
        0.3,
        "Not legal advice - generated documents require review by a qualified lawyer",
        size=8,
        color=C.MUTED,
        font="Verdana",
    )
    textbox(
        slide,
        W - MARGIN - 0.6,
        H - 0.58,
        0.6,
        0.3,
        f"{number:02d}",
        size=9,
        color=C.MUTED,
        font="Verdana",
        align=PP_ALIGN.RIGHT,
    )


# --- Slide renderers -------------------------------------------------------


def slide_title(prs) -> None:
    slide = blank(prs, C.INK)
    # Gold hairline accent down the left.
    rect(slide, 0, 0, 0.22, H, fill=C.GOLD, shape=MSO_SHAPE.RECTANGLE)
    # Faint watermark block.
    rect(slide, 8.6, 1.1, 4.2, 5.3, fill=(30, 37, 55), radius=0.03)

    textbox(
        slide,
        1.15,
        1.5,
        7.4,
        0.35,
        C.TITLE_SLIDE["eyebrow"],
        size=12,
        color=C.GOLD,
        bold=True,
        font="Verdana",
    )
    textbox(
        slide,
        1.15,
        2.0,
        7.6,
        1.3,
        C.TITLE_SLIDE["title"],
        size=60,
        color=C.WHITE,
        bold=True,
        font="Georgia",
    )
    textbox(
        slide,
        1.15,
        3.35,
        7.4,
        0.9,
        C.TITLE_SLIDE["subtitle"],
        size=24,
        color=(214, 219, 228),
        font="Georgia",
        spacing=1.15,
    )
    rect(slide, 1.15, 4.42, 1.9, 0.04, fill=C.GOLD, shape=MSO_SHAPE.RECTANGLE)
    textbox(
        slide,
        1.15,
        4.72,
        7.4,
        0.4,
        C.TITLE_SLIDE["tagline"],
        size=14,
        color=(150, 160, 178),
        font="Verdana",
    )
    y = 5.5
    for line in C.TITLE_SLIDE["meta"]:
        textbox(slide, 1.15, y, 7.4, 0.3, line, size=11, color=(120, 132, 152), font="Verdana")
        y += 0.3
    textbox(
        slide,
        1.15,
        6.55,
        7.4,
        0.5,
        "Not legal advice. LegalEase produces drafts for review, never a substitute "
        "for a qualified lawyer.",
        size=8.5,
        color=(104, 114, 132),
        font="Verdana",
        spacing=1.2,
    )


def slide_agenda(prs, spec, number) -> None:
    slide = blank(prs)
    y = header(slide, spec["eyebrow"], spec["title"])
    col_w = (CONTENT_W - 0.7) / 2
    per_col = (len(spec["items"]) + 1) // 2
    row_h = min(0.86, rows_fit(y, per_col, 0.0, reserve=0.04))
    for index, (num, label, sub) in enumerate(spec["items"]):
        col, row = divmod(index, per_col)
        x = MARGIN + col * (col_w + 0.7)
        yy = y + row * row_h
        textbox(slide, x, yy + 0.04, 0.55, 0.36, num, size=16, color=C.GOLD, bold=True, font="Georgia")
        textbox(slide, x + 0.58, yy, col_w - 0.6, 0.3, label, size=14.5, color=C.INK, bold=True, font="Georgia")
        textbox(slide, x + 0.58, yy + 0.3, col_w - 0.6, 0.3, sub, size=11, color=C.MUTED, font="Verdana")
        rect(slide, x, yy + row_h - 0.14, col_w - 0.1, 0.008, fill=C.RULE, shape=MSO_SHAPE.RECTANGLE)
    footer(slide, number)


def slide_bullets(prs, spec, number) -> None:
    slide = blank(prs)
    has_foot = bool(spec.get("foot"))
    y = header(slide, spec["eyebrow"], spec["title"], spec.get("lead"))
    body_w = CONTENT_W - 0.6

    # Long-form variant: label + prose, one card per item.
    if any(len(b) == 2 and len(b[1]) > 110 for b in spec["bullets"]):
        reserve = 0.72 if has_foot else 0.04
        h = max(
            0.5 + wrapped_lines(prose, body_w, 12, serif=True) * 0.21
            for _, prose in spec["bullets"]
        )
        h = min(h, rows_fit(y, len(spec["bullets"]), 0.16, reserve=reserve))
        for label, prose in spec["bullets"]:
            rect(slide, MARGIN, y, CONTENT_W, h, fill=C.WHITE, line=C.RULE, radius=0.05)
            rect(slide, MARGIN, y, 0.05, h, fill=C.GOLD, shape=MSO_SHAPE.RECTANGLE)
            textbox(slide, MARGIN + 0.32, y + 0.13, body_w, 0.3, label, size=14.5, color=C.INK, bold=True, font="Georgia")
            textbox(slide, MARGIN + 0.32, y + 0.47, body_w, h - 0.55, prose, size=12, color=C.SLATE, font="Georgia", spacing=1.2)
            y += h + 0.16
    else:
        # Two-column definition list.
        col_w = (CONTENT_W - 0.8) / 2
        half = (len(spec["bullets"]) + 1) // 2
        row_h = min(0.78, rows_fit(y, half, 0.14, reserve=0.68 if has_foot else 0.04))
        for index, (label, value) in enumerate(spec["bullets"]):
            col, row = (0, index) if index < half else (1, index - half)
            x = MARGIN + col * (col_w + 0.8)
            yy = y + row * row_h
            textbox(slide, x, yy, col_w, 0.28, label.upper(), size=10, color=C.GOLD, bold=True, font="Verdana")
            textbox(slide, x, yy + 0.25, col_w, row_h - 0.3, value, size=13.5, color=C.INK, font="Georgia", spacing=1.15)

    if has_foot:
        fh = min(0.46, wrapped_lines(spec["foot"], CONTENT_W - 0.56, 11, serif=True) * 0.2 + 0.16)
        rect(slide, MARGIN, FOOTER_TOP - fh, CONTENT_W, fh, fill=C.GOLD_SOFT, radius=0.08)
        textbox(slide, MARGIN + 0.28, FOOTER_TOP - fh + 0.11, CONTENT_W - 0.56, fh - 0.2, spec["foot"], size=11, color=(122, 95, 40), font="Georgia", italic=True, spacing=1.15)
    footer(slide, number)


def slide_compare(prs, spec, number) -> None:
    slide = blank(prs)
    y = header(slide, spec["eyebrow"], spec["title"], spec.get("lead"))
    col_w = (CONTENT_W - 0.6) / 2
    h = 3.55

    for x, title, items, tint, accent in (
        (MARGIN, spec["left_title"], spec["left"], C.RED_SOFT, C.RED),
        (MARGIN + col_w + 0.6, spec["right_title"], spec["right"], C.GREEN_SOFT, C.GREEN),
    ):
        rect(slide, x, y, col_w, h, fill=C.WHITE, line=C.RULE, radius=0.04)
        rect(slide, x, y, col_w, 0.44, fill=tint, shape=MSO_SHAPE.RECTANGLE)
        textbox(slide, x + 0.26, y + 0.11, col_w - 0.5, 0.3, title, size=12, color=accent, bold=True, font="Verdana")
        iy = y + 0.66
        for item in items:
            rect(slide, x + 0.28, iy + 0.09, 0.1, 0.1, fill=accent, shape=MSO_SHAPE.OVAL)
            textbox(slide, x + 0.52, iy, col_w - 0.8, 0.34, item, size=12, color=C.INK, font="Georgia")
            iy += 0.42

    vy = y + h + 0.3
    rect(slide, MARGIN, vy, CONTENT_W, 0.72, fill=C.INK, radius=0.05)
    textbox(slide, MARGIN + 0.3, vy + 0.14, CONTENT_W - 0.6, 0.5, spec["verdict"], size=12.5, color=(226, 231, 238), font="Georgia", italic=True, spacing=1.15)
    footer(slide, number)


def slide_layers(prs, spec, number) -> None:
    slide = blank(prs)
    y = header(slide, spec["eyebrow"], spec["title"], spec.get("lead"))
    h = min(1.06, rows_fit(y, len(spec["layers"]), 0.14, reserve=0.04))
    for label, body, detail in spec["layers"]:
        rect(slide, MARGIN, y, CONTENT_W, h, fill=C.WHITE, line=C.RULE, radius=0.04)
        rect(slide, MARGIN, y, 0.05, h, fill=C.TEAL, shape=MSO_SHAPE.RECTANGLE)
        textbox(slide, MARGIN + 0.3, y + 0.13, 2.15, 0.28, label, size=11, color=C.TEAL, bold=True, font="Verdana")
        textbox(slide, MARGIN + 0.3, y + 0.42, CONTENT_W - 0.65, 0.32, body, size=13, color=C.INK, font="Georgia")
        textbox(slide, MARGIN + 0.3, y + 0.72, CONTENT_W - 0.65, 0.24, detail, size=10.5, color=C.MUTED, font="Verdana")
        y += h + 0.14
    footer(slide, number)


def slide_numbered(prs, spec, number) -> None:
    slide = blank(prs)
    y = header(slide, spec["eyebrow"], spec["title"], spec.get("lead"))
    items = spec["items"]

    def split(item) -> tuple[str | None, str]:
        return (item[2], item[3]) if len(item) == 4 else (None, item[2])

    # A single column needs roughly this much room per row to stay readable; fall
    # back to two columns when the stack would not fit.
    def stack_height(col_w: float, font: float) -> float:
        return 0.34 + max(
            wrapped_lines(split(i)[1], col_w, font) for i in items
        ) * 0.21

    two_col = stack_height(W - MARGIN - 4.1, 11.5) * len(items) > (FOOTER_TOP - y)
    if two_col:
        col_w = (CONTENT_W - 0.6) / 2
        per_col = (len(items) + 1) // 2
        sub_w = col_w - 1.3
        row_h = 0.32 + max(
            wrapped_lines(split(i)[1], sub_w, 10.5) for i in items
        ) * 0.2
        gap = split_gap(y, row_h, per_col, 0.16)
        for index, item in enumerate(items):
            num, label, effort, sub = (item[0], item[1], *split(item))
            col, row = divmod(index, per_col)
            x = MARGIN + col * (col_w + 0.6)
            yy = y + row * (row_h + gap)
            textbox(slide, x, yy + 0.02, 0.5, 0.3, num, size=13, color=C.GOLD, bold=True, font="Georgia")
            textbox(slide, x + 0.52, yy, 2.0, 0.28, label, size=12.5, color=C.INK, bold=True, font="Georgia")
            if effort:
                textbox(slide, x + col_w - 1.15, yy + 0.02, 1.15, 0.24, effort, size=9, color=(150, 124, 70), bold=True, font="Verdana", align=PP_ALIGN.RIGHT)
            textbox(slide, x + 0.52, yy + 0.29, sub_w, row_h - 0.34, sub, size=10.5, color=C.SLATE, font="Verdana", spacing=1.12)
            rect(slide, x, yy + row_h - 0.05, col_w, 0.008, fill=C.RULE, shape=MSO_SHAPE.RECTANGLE)
    else:
        sub_x = MARGIN + 4.1
        sub_w = W - MARGIN - sub_x
        row_h = stack_height(sub_w, 11.5)
        gap = split_gap(y, row_h, len(items), 0.2)
        for item in items:
            num, label, effort, sub = (item[0], item[1], *split(item))
            textbox(slide, MARGIN, y + 0.03, 0.6, 0.32, num, size=15, color=C.GOLD, bold=True, font="Georgia")
            textbox(slide, MARGIN + 0.62, y, 3.4, 0.3, label, size=14, color=C.INK, bold=True, font="Georgia")
            if effort:
                rect(slide, MARGIN + 4.1, y - 0.02, 1.1, 0.3, fill=C.GOLD_SOFT, radius=0.35)
                textbox(
                    slide, MARGIN + 4.1, y + 0.035, 1.1, 0.24, effort,
                    size=9, color=(122, 95, 40), bold=True, font="Verdana", align=PP_ALIGN.CENTER,
                )
            textbox(
                slide, sub_x, y + 0.02, sub_w, row_h - 0.08,
                sub, size=11.5, color=C.SLATE, font="Verdana", spacing=1.15,
            )
            rect(slide, MARGIN, y + row_h - 0.06, CONTENT_W, 0.008, fill=C.RULE, shape=MSO_SHAPE.RECTANGLE)
            y += row_h + gap
    footer(slide, number)


def slide_bug(prs, spec, number) -> None:
    slide = blank(prs)
    y = header(slide, spec["eyebrow"], spec["title"], spec.get("lead"))
    inner = CONTENT_W - 0.6

    # Two banners, the detail rows, then the fix and lesson boxes. Heights are
    # derived from the space actually left so the stack never runs off-canvas.
    banner_w = CONTENT_W - 2.0
    banner = max(
        0.56,
        0.22 + max(
            wrapped_lines(spec[k], banner_w, 12, serif=True)
            for k in ("symptom", "root_cause")
        ) * 0.2,
    )
    detail_gap = 0.1
    fix_h = 0.7
    lesson_h = 0.46
    stack = (
        banner * 2
        + len(spec["detail"]) * 0.5
        + fix_h
        + lesson_h
        + detail_gap * (len(spec["detail"]) + 3)
    )
    slack = max(0.0, (FOOTER_TOP - y) - stack)
    banner += min(slack * 0.34, 0.16)
    fix_h += min(slack * 0.26, 0.14)

    rect(slide, MARGIN, y, CONTENT_W, banner, fill=C.RED_SOFT, radius=0.06)
    textbox(slide, MARGIN + 0.3, y + 0.1, 1.4, 0.3, "SYMPTOM", size=10, color=C.RED, bold=True, font="Verdana")
    textbox(slide, MARGIN + 1.7, y + 0.11, CONTENT_W - 2.0, banner - 0.2, spec["symptom"], size=12, color=(122, 42, 37), font="Georgia", spacing=1.15)
    y += banner + detail_gap

    rect(slide, MARGIN, y, CONTENT_W, banner, fill=C.WHITE, line=C.RULE, radius=0.05)
    textbox(slide, MARGIN + 0.3, y + 0.1, 1.4, 0.3, "ROOT CAUSE", size=10, color=C.GOLD, bold=True, font="Verdana")
    textbox(slide, MARGIN + 1.7, y + 0.11, CONTENT_W - 2.0, banner - 0.2, spec["root_cause"], size=12, color=C.INK, font="Georgia", spacing=1.15)
    y += banner + detail_gap

    for label, detail in spec["detail"]:
        rect(slide, MARGIN, y, 0.05, 0.5, fill=C.GOLD, shape=MSO_SHAPE.RECTANGLE)
        textbox(slide, MARGIN + 0.26, y + 0.02, CONTENT_W * 0.4, 0.46, label, size=12, color=C.INK, bold=True, font="Georgia", spacing=1.1)
        textbox(slide, MARGIN + 0.26 + CONTENT_W * 0.42, y + 0.04, CONTENT_W * 0.53, 0.44, detail, size=11, color=C.SLATE, font="Verdana", spacing=1.15)
        y += 0.5 + detail_gap

    rect(slide, MARGIN, y, CONTENT_W, fix_h, fill=C.GREEN_SOFT, radius=0.05)
    textbox(slide, MARGIN + 0.3, y + 0.1, 1.2, 0.3, "FIX", size=10, color=C.GREEN, bold=True, font="Verdana")
    textbox(slide, MARGIN + 1.05, y + 0.1, CONTENT_W - 1.35, fix_h - 0.18, spec["fix"], size=11, color=(33, 92, 59), font="Georgia", spacing=1.15)
    y += fix_h + detail_gap

    rect(slide, MARGIN, y, CONTENT_W, lesson_h, fill=C.INK, radius=0.06)
    textbox(slide, MARGIN + 0.3, y + 0.1, CONTENT_W - 0.6, 0.32, "LESSON:  " + spec["lesson"], size=10.5, color=(220, 226, 234), font="Georgia", italic=True, spacing=1.1)
    footer(slide, number)


def slide_verify(prs, spec, number) -> None:
    slide = blank(prs)
    y = header(slide, spec["eyebrow"], spec["title"], spec.get("lead"))
    checks = spec["checks"]

    def tone_of(status: str):
        return {
            "pass": (C.GREEN, C.GREEN_SOFT, "PASS"),
            "warn": (C.GOLD, C.GOLD_SOFT, "RECHECKED"),
        }[status]

    # Two columns when there are enough rows that a single stack would need
    # more height than the canvas has.
    label_w = 2.1
    two_col = len(checks) > 5
    if two_col:
        col_w = (CONTENT_W - 0.5) / 2
        per_col = (len(checks) + 1) // 2
        # Inside a card the detail sits under the label, so it gets full width.
        row_h = 0.34 + max(
            wrapped_lines(d, col_w - 0.9, 10.5) for _, _, d, _ in checks
        ) * 0.2
        gap = split_gap(y, row_h, per_col, 0.12)
        for index, (label, value, detail, status) in enumerate(checks):
            accent, tint, tag = tone_of(status)
            col, row = divmod(index, per_col)
            x = MARGIN + col * (col_w + 0.5)
            yy = y + row * (row_h + gap)
            rect(slide, x, yy, col_w, row_h, fill=C.WHITE, line=C.RULE, radius=0.04)
            rect(slide, x, yy, 0.045, row_h, fill=accent, shape=MSO_SHAPE.RECTANGLE)
            textbox(slide, x + 0.24, yy + 0.1, label_w, 0.26, label, size=12, color=C.INK, bold=True, font="Georgia")
            textbox(slide, x + col_w - 1.6, yy + 0.11, 1.36, 0.24, value, size=11, color=accent, bold=True, font="Verdana", align=PP_ALIGN.RIGHT)
            textbox(slide, x + 0.24, yy + 0.38, col_w - 0.48, row_h - 0.44, detail, size=10.5, color=C.SLATE, font="Verdana", spacing=1.15)
    else:
        label_x = MARGIN + 0.26
        value_x = MARGIN + 2.9
        detail_x = MARGIN + 4.85
        detail_w = W - MARGIN - detail_x - 0.2
        row_h = 0.62 + max(
            wrapped_lines(d, detail_w, 11) for _, _, d, _ in checks
        ) * 0.2
        gap = split_gap(y, row_h, len(checks), 0.14)
        for label, value, detail, status in checks:
            accent, tint, tag = tone_of(status)
            rect(slide, MARGIN, y, CONTENT_W, row_h, fill=C.WHITE, line=C.RULE, radius=0.04)
            rect(slide, MARGIN, y, 0.045, row_h, fill=accent, shape=MSO_SHAPE.RECTANGLE)
            textbox(slide, label_x, y + 0.12, 2.5, 0.28, label, size=12.5, color=C.INK, bold=True, font="Georgia")
            textbox(slide, label_x, y + 0.42, 2.5, 0.22, tag, size=8.5, color=accent, bold=True, font="Verdana")
            textbox(slide, value_x, y + 0.13, 1.9, 0.3, value, size=12, color=accent, bold=True, font="Georgia", spacing=1.1)
            textbox(slide, detail_x, y + 0.13, detail_w, row_h - 0.2, detail, size=11, color=C.SLATE, font="Verdana", spacing=1.15)
            y += row_h + gap
    footer(slide, number)


def slide_gaps(prs, spec, number) -> None:
    slide = blank(prs)
    y = header(slide, spec["eyebrow"], spec["title"], spec.get("lead"))
    tone = {
        "significant": (C.RED, C.RED_SOFT, "SIGNIFICANT"),
        "minor": (C.GOLD, C.GOLD_SOFT, "MINOR"),
        "not built": (C.SLATE, (238, 239, 241), "NOT BUILT"),
    }
    gaps = spec["gaps"]
    body_w = CONTENT_W - 0.62
    h = max(0.55 + wrapped_lines(body, body_w, 11.5) * 0.2 for _, _, body in gaps)
    h = min(h, rows_fit(y, len(gaps), 0.16, reserve=0.04))
    for title, severity, body in gaps:
        accent, tint, tag = tone[severity]
        rect(slide, MARGIN, y, CONTENT_W, h, fill=tint, radius=0.04)
        rect(slide, MARGIN, y, 0.05, h, fill=accent, shape=MSO_SHAPE.RECTANGLE)
        textbox(slide, MARGIN + 0.3, y + 0.12, body_w - 1.7, 0.3, title, size=14, color=C.INK, bold=True, font="Georgia")
        textbox(slide, MARGIN + CONTENT_W - 2.0, y + 0.15, 1.7, 0.26, tag, size=9.5, color=accent, bold=True, font="Verdana", align=PP_ALIGN.RIGHT)
        textbox(slide, MARGIN + 0.3, y + 0.46, body_w, h - 0.54, body, size=11.5, color=C.SLATE, font="Georgia", spacing=1.18)
        y += h + 0.16
    footer(slide, number)


def slide_closing(prs, spec, number) -> None:
    slide = blank(prs, C.INK)
    rect(slide, 0, 0, 0.22, H, fill=C.GOLD, shape=MSO_SHAPE.RECTANGLE)
    textbox(slide, MARGIN + 0.3, 0.75, CONTENT_W, 0.3, spec["eyebrow"], size=12, color=C.GOLD, bold=True, font="Verdana")
    textbox(slide, MARGIN + 0.3, 1.15, CONTENT_W, 0.8, spec["title"], size=36, color=C.WHITE, bold=True, font="Georgia")
    rect(slide, MARGIN + 0.3, 2.08, 1.9, 0.04, fill=C.GOLD, shape=MSO_SHAPE.RECTANGLE)

    y = 2.5
    for label, body in spec["points"]:
        rect(slide, MARGIN + 0.3, y + 0.08, 0.09, 0.09, fill=C.GOLD, shape=MSO_SHAPE.OVAL)
        textbox(slide, MARGIN + 0.6, y, 3.4, 0.3, label, size=14, color=C.GOLD, bold=True, font="Georgia")
        textbox(slide, MARGIN + 4.15, y + 0.02, CONTENT_W - 4.5, 0.5, body, size=12, color=(198, 205, 216), font="Georgia", spacing=1.15)
        y += 0.78

    rect(slide, MARGIN + 0.3, y + 0.18, CONTENT_W - 0.3, 0.82, fill=(30, 37, 55), radius=0.04)
    textbox(slide, MARGIN + 0.6, y + 0.34, CONTENT_W - 0.9, 0.56, spec["close"], size=12.5, color=(214, 219, 228), font="Georgia", italic=True, spacing=1.18)
    textbox(
        slide,
        MARGIN + 0.3,
        H - 0.72,
        CONTENT_W - 1.0,
        0.3,
        "Not legal advice - generated documents require review by a qualified lawyer",
        size=8,
        color=(104, 114, 132),
        font="Verdana",
    )
    textbox(slide, W - MARGIN - 0.6, H - 0.72, 0.6, 0.3, f"{number:02d}", size=9, color=(120, 132, 152), font="Verdana", align=PP_ALIGN.RIGHT)


RENDERERS = {
    "agenda": slide_agenda,
    "bullets": slide_bullets,
    "compare": slide_compare,
    "layers": slide_layers,
    "numbered": slide_numbered,
    "bug": slide_bug,
    "verify": slide_verify,
    "gaps": slide_gaps,
    "closing": slide_closing,
}


def assert_on_canvas(prs: Presentation) -> None:
    """Fail loudly if any shape would render off the slide.

    PowerPoint silently clips overflow, so a shape that runs past the edge is a
    content bug that would otherwise only be noticed by eye.
    """
    limit_h, limit_w = prs.slide_height, prs.slide_width
    problems = []
    for index, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            if shape.top is None or shape.height is None:
                continue
            bottom = shape.top + shape.height
            right = (shape.left or 0) + shape.width
            if bottom > limit_h or right > limit_w or (shape.left or 0) < 0 or shape.top < 0:
                label = (
                    shape.text_frame.text[:40]
                    if shape.has_text_frame and shape.text_frame.text
                    else shape.name
                )
                problems.append((index, round(bottom / 914400, 2), round(right / 914400, 2), label))
    if problems:
        detail = "\n  ".join(
            f"slide {n}: bottom={b}in right={r}in :: {t!r}" for n, b, r, t in problems
        )
        raise AssertionError(f"{len(problems)} shape(s) exceed the canvas:\n  {detail}")


def build() -> Path:
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)

    slide_title(prs)
    for index, spec in enumerate(C.SLIDES, start=2):
        RENDERERS[spec["kind"]](prs, spec, index)

    assert_on_canvas(prs)

    prs.core_properties.title = f"{C.PROJECT_NAME} - {C.SUBTITLE}"
    prs.core_properties.subject = C.TAGLINE
    prs.core_properties.comments = "Generated from documents/content.py"

    prs.save(str(OUT))
    return OUT


if __name__ == "__main__":
    path = build()
    slides = len(Presentation(str(path)).slides._sldIdLst)
    print(f"wrote {path}")
    print(f"slides: {slides}")
