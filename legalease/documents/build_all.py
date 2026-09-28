"""Build both project documents.

    python documents/build_all.py

Regenerates the PowerPoint deck and the PDF report from ``content.py``. Editing
the narrative means editing that one file, then running this.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pdf
import build_pptx


def main() -> int:
    print("building presentation...")
    pptx = build_pptx.build()
    print(f"  {pptx.name}  {pptx.stat().st_size:,} bytes")

    print("building report...")
    pdf = build_pdf.build()
    print(f"  {pdf.name}  {pdf.stat().st_size:,} bytes")

    print("\ndone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
