# Project Documents

Generated artefacts describing how LegalEase was built, from the written brief
through to a verified running application.

| File | What it is |
| --- | --- |
| `LegalEase-Project-Presentation.pptx` | 15-slide 16:9 deck for presenting or submitting |
| `LegalEase-Project-Report.pdf` | 13-page A4 report for reading alongside the code |

## Rebuilding

```powershell
python documents/build_all.py
```

Regenerates both files. `build_pptx.py` and `build_pdf.py` can also be run
individually.

### Editing the content

`content.py` holds every word of the narrative. **Edit that file, not the
generated documents** — the deck and the report are both built from it, so the
two can never drift apart.

Structure per slide kind is defined in `SLIDES`; the report prose lives in
`PDF_SECTIONS`. Colours are the `INK` / `SLATE` / `GOLD` / `TEAL` constants at
the top of `content.py`.

## Layout behaviour

`build_pptx.py` measures text before placing it. `wrapped_lines()` predicts line
counts from the character advance width, and the list renderers derive row
heights and gaps from the space actually remaining. Dense slides automatically
fall back to a two-column grid rather than overflowing.

`assert_on_canvas()` runs before every save and raises if any shape would render
off the slide, because PowerPoint silently clips overflow — a bug that would
otherwise only show up by eye.

## Requirements

```powershell
pip install python-pptx reportlab
```

## A note on the content

The deck and report state plainly what was not built, and record two failures
that turned out to be faults in the verification scripts rather than the
product. That is deliberate. A report that only lists successes is less useful
to whoever reviews or inherits the project.
