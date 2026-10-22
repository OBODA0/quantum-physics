"""Correct the text layer of the submitted cover page, once, and write it back.

Two things are wrong in the cover OBODA assembled: the first student's name is spelled
"Mohammed OBADA" (it is Mohamed Oboda), and the tool that assembled the cover stamped a footer
whose page total no longer applies to this report. Nothing else is touched - the logo, the rules
and the layout are the submitted ones.

Run from the repository root:  .venv/bin/python report/fix_cover.py
"""
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DecodedStreamObject, NameObject
from reportlab.pdfbase.pdfmetrics import stringWidth

COVER = Path(__file__).resolve().parent / "cover.pdf"
FACE, SIZE = "Times-Bold", 11.88
FOOTER_BASELINE = "33.84"

# The page stores each line as kerning clusters; these are the exact runs to replace.
NAME_RUNS = [
    ("234.86", "313.34",
     "[(S)11(tu)-19(d)11(e)-10(n)11(ts)-4(:M)-25(o)-14(h)-19(a)15(m)-14(m)15(e)-10(d)-19( )]",
     "Students:Mohamed"),
    ("268.37", "292.44", "[(O)-9(BA)25(D)-35(A)]", "Oboda"),
]


def replace_run(content, x, y, old_array, new_text):
    """Swap one text run for another, keeping the line centred where it was."""
    letters = "".join(re.findall(r"\((.*?)\)", old_array))
    shift = (stringWidth(letters, FACE, SIZE) - stringWidth(new_text, FACE, SIZE)) / 2.0
    position = f"1 0 0 1 {x} {y} Tm"
    assert content.count(position) == 1, f"expected one run at {x},{y}"
    content = content.replace(
        position, "1 0 0 1 {:.2f} {} Tm".format(float(x) + shift, y))
    assert content.count(old_array + " TJ") == 1
    return content.replace(old_array + " TJ", "[({})] TJ".format(new_text))


def blank_footer(content):
    """The stamped footer carries a page total that does not apply here: empty its runs."""
    blanked = 0
    cursor = 0
    while True:
        at = content.find(FOOTER_BASELINE + " Tm", cursor)
        if at == -1:
            break
        start = content.find("[", at)
        end = content.find("] TJ", start)
        content = content[:start] + "[( )]" + content[end + 1:]  # keep the " TJ" operator
        cursor = start + 5
        blanked += 1
    return content, blanked


def main():
    reader = PdfReader(str(COVER))
    writer = PdfWriter()
    writer.add_page(reader.pages[0])
    page = writer.pages[0]
    content = page.get_contents().get_data().decode("latin-1")
    for x, y, old_array, new_text in NAME_RUNS:
        content = replace_run(content, x, y, old_array, new_text)
    content, blanked = blank_footer(content)
    print(f"footer runs blanked: {blanked}")
    stream = DecodedStreamObject()
    stream.set_data(content.encode("latin-1"))
    page[NameObject("/Contents")] = writer._add_object(stream)
    page[NameObject("/Annots")] = ArrayObject()  # a stale link the merge tool left mid-page
    temporary = COVER.with_suffix(".fixed.pdf")
    with open(temporary, "wb") as handle:
        writer.write(handle)
    temporary.replace(COVER)
    print(f"cover corrected: {COVER}")


if __name__ == "__main__":
    main()
