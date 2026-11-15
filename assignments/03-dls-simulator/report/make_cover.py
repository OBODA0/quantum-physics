"""Regenerate assignment 3's cover page from assignment 1's approved cover page."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent / "01-pl-spectrometer" / "report" / "cover.pdf"
TARGET = HERE / "cover.pdf"

OLD_DATE = "[(1)-14(8)-14(.)8(1)-14(0)-14(.)8(2)-14(0)-14(2)-14(6)] TJ"
NEW_DATE = "[(1)-14(5)-14(.)8(1)-14(1)-14(.)8(2)-14(0)-14(2)-14(6)] TJ"

OLD_STUDENTS = "[(Students:Mohamed)] TJ"
NEW_STUDENTS = "[(Students: Mohamed)] TJ"

OLD_MERT = "[(M)-25(e)-10(r)-10(t )7(S)11(O)-9(LM)-24(A)25(Z )] TJ"
NEW_MERT = "[(Mert Solmaz)] TJ"

OLD_OBODA = "[(Oboda)] TJ"
NEW_OBODA = "[(Mohamed Oboda)] TJ"


def main() -> None:
    """Write report/cover.pdf with cleaned formatting and date."""
    writer = PdfWriter()
    writer.add_page(PdfReader(str(SOURCE)).pages[0])
    page = writer.pages[0]
    content = page.get_contents().get_data().decode("latin-1")

    if OLD_DATE in content:
        content = content.replace(OLD_DATE, NEW_DATE)
    if OLD_STUDENTS in content:
        content = content.replace(OLD_STUDENTS, NEW_STUDENTS)

    stream = DecodedStreamObject()
    stream.set_data(content.encode("latin-1"))
    page[NameObject("/Contents")] = writer._add_object(stream)

    with open(TARGET, "wb") as handle:
        writer.write(handle)
    print(f"wrote {TARGET}")


if __name__ == "__main__":
    main()
