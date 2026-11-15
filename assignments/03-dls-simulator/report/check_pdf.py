"""Gate the built PDF before it goes anywhere.

    uv run python -m report.check_pdf            # with reference resolution
    uv run python -m report.check_pdf --offline  # skip the network step

The document must be one self-contained PDF: the expected sections present, every image
embedded, no embedded files or file-launch actions, and every DOI in the reference list
resolving through the DOI handle registry. A citation that does not resolve would score
zero for the whole assignment (PS1), so resolution is part of the gate rather than a habit.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request

from pypdf import PdfReader

from .generate_pdf_report import DOIS, PDF_PATH

REQUIRED_TEXT = [
    "Assignment 3",
    "Dynamic Light Scattering",
    "Stokes-Einstein",
    "ISO 22412",
    "cumulant",
    "173 deg",
    "Appendix A: the code",
    "Appendix B: constants and records",
    "Appendix C: the generated tables",
    "References",
    "github.com/OBODA0/quantum-physics",
]

MIN_PAGES = 25


def _resolve(doi: str, timeout: float = 20.0) -> tuple[bool, str]:
    url = f"https://doi.org/api/handles/{doi}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            payload = json.load(response)
        code = payload.get("responseCode")
        return code == 1, f"handle responseCode {code}"
    except Exception as error:                      # noqa: BLE001 - reported, not raised
        return False, f"{type(error).__name__}: {error}"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    offline = "--offline" in argv
    if not PDF_PATH.exists():
        print(f"FAIL: {PDF_PATH.name} does not exist")
        return 1

    reader = PdfReader(str(PDF_PATH))
    failures: list[str] = []
    if len(reader.pages) < MIN_PAGES:
        failures.append(f"only {len(reader.pages)} pages (expected at least {MIN_PAGES})")

    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    flat = re.sub(r"\s+", " ", text)
    for needle in REQUIRED_TEXT:
        if needle not in flat:
            failures.append(f"missing from the text: {needle}")

    root = reader.trailer["/Root"]
    embedded = "/EmbeddedFiles" in root.get("/Names", {})
    if embedded:
        failures.append("the PDF carries embedded files")

    external_files = []
    link_count = 0
    for number, page in enumerate(reader.pages, start=1):
        for annotation in page.get("/Annots", []) or []:
            annotation = annotation.get_object()
            action = annotation.get("/A")
            if action is None:
                continue
            if action.get("/S") == "/URI":
                link_count += 1
            else:
                external_files.append(f"page {number}: {action.get('/S')}")
    if external_files:
        failures.append("non-URL actions: " + ", ".join(external_files))

    print(f"file             : {PDF_PATH.name}")
    print(f"pages            : {len(reader.pages)}")
    print(f"characters       : {len(flat)}")
    print(f"embedded files   : {'yes' if embedded else 'none'}")
    print(f"URI links        : {link_count}")

    if offline:
        print("reference DOIs   : skipped (--offline)")
    else:
        unresolved = []
        for doi in DOIS:
            ok, detail = _resolve(doi)
            print(f"reference DOIs   : {doi:34s} {'resolves' if ok else 'DOES NOT RESOLVE'}"
                  f" ({detail})")
            if not ok:
                unresolved.append(doi)
        if unresolved:
            failures.append("unresolved DOIs: " + ", ".join(unresolved))

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
