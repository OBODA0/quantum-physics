"""Regenerate assignment 3's cover page from assignment 2's approved cover page.

The only difference between the two submissions is the date, and that date is a single
kerning run (``TJ``) in the page's content stream. Times New Roman Bold gives every digit
the same advance width, so writing "15.11.2026" into that run shifts nothing: the logo, the
rules, the centring and every other glyph are left untouched.

    uv run python -m report.make_cover
"""

from __future__ import annotations

import pathlib

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject

HERE = pathlib.Path(__file__).resolve().parent
SOURCE = HERE.parent.parent / "02-xrd-diffractometer" / "report" / "cover.pdf"
TARGET = HERE / "cover.pdf"

OLD_DATE = "[(2)-14(6)-14(.)8(1)-14(0)-14(.)8(2)-14(0)-14(2)-14(6)] TJ"
NEW_DATE = "[(1)-14(5)-14(.)8(1)-14(1)-14(.)8(2)-14(0)-14(2)-14(6)] TJ"


def main() -> int:
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
