"""Check that the numbers quoted in the PDF still match the model.

The report takes its quoted numbers from `numbers_source.py`; this gate recomputes them the
same way and refuses a PDF whose text does not contain them, so a stale build cannot pass.
"""

from __future__ import annotations

import pathlib
import re
import sys

from pypdf import PdfReader

from .numbers_source import quoted_numbers

HERE = pathlib.Path(__file__).resolve().parent
PDF = HERE / "Assignment_2_XRD_Diffractometer_Report.pdf"


def main() -> int:
    if not PDF.exists():
        print(f"FAIL: {PDF} does not exist")
        return 1
    text = re.sub(r"\s+", " ",
                  "\n".join(page.extract_text() or "" for page in PdfReader(str(PDF)).pages))
    numbers = quoted_numbers()
    failures = [f"{name}: {value!r} is not in the PDF"
                for name, value in numbers.items() if value not in text]
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print(f"PASS: {len(numbers)} quoted numbers match the model")
    return 0


if __name__ == "__main__":
    sys.exit(main())
