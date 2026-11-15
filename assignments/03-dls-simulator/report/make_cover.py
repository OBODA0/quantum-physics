"""Generate the pristine vector cover page for Assignment 3."""

from __future__ import annotations

import pathlib
import matplotlib
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / "cover.pdf"
LOGO_PATH = HERE / "figures" / "agu_logo.png"


def generate_cover() -> None:
    """Create a pristine cover page matching the official AGU assignment layout."""
    ttf = pathlib.Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", str(ttf / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(ttf / "DejaVuSans-Bold.ttf")))

    c = canvas.Canvas(str(TARGET), pagesize=letter)
    width, _ = letter

    # AGU Logo centered horizontally
    if LOGO_PATH.exists():
        c.drawImage(
            str(LOGO_PATH),
            250.0,
            602.8,
            width=112.2,
            height=112.2,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Department and University headers
    c.setFont("DejaVuSans", 22)
    c.drawCentredString(width / 2.0, 560, "Department of")
    c.drawCentredString(width / 2.0, 526, "Electrical & Electronics Engineering")

    c.setFont("DejaVuSans-Bold", 18)
    c.drawCentredString(width / 2.0, 485, "Abdullah Gül University")

    # Date
    c.setFont("DejaVuSans-Bold", 12)
    c.drawCentredString(width / 2.0, 395, "Submitted on: 15.11.2026")

    # Student Names & IDs
    c.drawCentredString(width / 2.0, 305, "Students:")
    c.drawCentredString(width / 2.0, 280, "Mohamed Oboda (2111011090)")
    c.drawCentredString(width / 2.0, 255, "Mert Solmaz (2311011039)")

    c.showPage()
    c.save()
    print(f"Generated clean cover page: {TARGET}")


if __name__ == "__main__":
    generate_cover()
