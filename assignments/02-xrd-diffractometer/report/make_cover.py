"""Regenerate assignment 2's cover page from assignment 1's approved cover page.

The only difference between the two submissions is the date, and that date is a single
kerning run (``TJ``) in the page's content stream. Times New Roman Bold gives every digit
the same advance width (5.94 pt at 11.88 pt), so writing "26.10.2026" into that run shifts
nothing: the logo, the rules, the centring and every other glyph are left untouched.

Run it with assignment 2's virtualenv (pypdf only, no network):

    assignments/02-xrd-diffractometer/.venv/bin/python \
        assignments/02-xrd-diffractometer/report/make_cover.py
"""
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent / "01-pl-spectrometer" / "report" / "cover.pdf"
TARGET = HERE / "cover.pdf"

OLD_DATE = "[(1)-14(8)-14(.)8(1)-14(0)-14(.)8(2)-14(0)-14(2)-14(6)] TJ"
NEW_DATE = "[(2)-14(6)-14(.)8(1)-14(0)-14(.)8(2)-14(0)-14(2)-14(6)] TJ"


def main():
    writer = PdfWriter()
    writer.add_page(PdfReader(str(SOURCE)).pages[0])
    page = writer.pages[0]
    content = page.get_contents().get_data().decode("latin-1")
    found = content.count(OLD_DATE)
    if found != 1:
        raise SystemExit(f"expected one date run in {SOURCE}, found {found}")

    stream = DecodedStreamObject()
    stream.set_data(content.replace(OLD_DATE, NEW_DATE).encode("latin-1"))
    page[NameObject("/Contents")] = writer._add_object(stream)

    with open(TARGET, "wb") as handle:
        writer.write(handle)
    print(f"wrote {TARGET}")


if __name__ == "__main__":
    main()
