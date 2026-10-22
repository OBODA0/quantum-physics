"""Gate the built PDF before it goes anywhere.

Checks that the document is the right one and that it is self-contained, the way
assignment 1's gate did.
"""

from __future__ import annotations

import pathlib
import re
import sys

from pypdf import PdfReader

HERE = pathlib.Path(__file__).resolve().parent
PDF = HERE / "Assignment_2_XRD_Diffractometer_Report.pdf"


def main() -> int:
    if not PDF.exists():
        print(f"FAIL: {PDF} does not exist")
        return 1
    reader = PdfReader(str(PDF))
    failures = []
    if len(reader.pages) < 3:
        failures.append(f"only {len(reader.pages)} pages")
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    flat = re.sub(r"\s+", " ", text)
    for needle in ["Assignment 2", "XRD", "Bragg", "github.com/OBODA0/quantum-physics"]:
        if needle not in flat:
            failures.append(f"missing from the text: {needle}")
    root = reader.trailer["/Root"]
    if "/EmbeddedFiles" in root.get("/Names", {}):
        failures.append("the PDF carries embedded files")
    print(f"pages            : {len(reader.pages)}")
    print(f"characters       : {len(flat)}")
    print(f"attachments      : {'yes' if '/EmbeddedFiles' in root.get('/Names', {}) else 'none'}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
