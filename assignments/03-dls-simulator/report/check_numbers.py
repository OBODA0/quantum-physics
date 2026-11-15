"""Check that the numbers quoted in the PDF still match the model.

The report takes every quoted number from ``numbers_source.py``; this gate recomputes them
the same way and refuses a PDF whose text does not contain them, so a stale build cannot
pass. The builder and the gate import the same module, so the two cannot drift.
"""

from __future__ import annotations

import re
import sys

from pypdf import PdfReader

from .generate_pdf_report import PDF_PATH
from .numbers_source import quoted_numbers


def main() -> int:
    if not PDF_PATH.exists():
        print(f"FAIL: {PDF_PATH.name} does not exist")
        return 1
    text = re.sub(r"\s+", " ",
                  "\n".join(page.extract_text() or "" for page in PdfReader(str(PDF_PATH)).pages))
    numbers = quoted_numbers()
    failures = [f"{name}: {value!r} is not in the PDF text"
                for name, value in numbers.items() if value not in text]
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        print(f"{len(failures)} of {len(numbers)} quoted numbers are missing")
        return 1
    print(f"PASS: {len(numbers)} quoted numbers match the model")
    return 0


if __name__ == "__main__":
    sys.exit(main())
