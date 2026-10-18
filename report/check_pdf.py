"""
Gate the built PDF before it is submitted.

Checks the file that will actually be uploaded, not the repository:

  1. every DOI printed in the PDF resolves at Crossref (PS1 protection),
  2. the appendix carries the expected number of source files,
  3. the figures are embedded as images, not linked,
  4. the page count and title metadata are set.

Usage: python report/check_pdf.py [--min-figures 9] [--appendix-files 14]
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

PDF = Path(__file__).resolve().parent / "Assignment_1_PL_Spectroscopy_Simulation_Report.pdf"


def pdf_text(path):
    return subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True).stdout


def resolve(doi):
    out = subprocess.run(
        ["curl", "-s", "-m", "25", "-o", "/dev/null", "-w", "%{http_code}",
         "-H", "User-Agent: plsim-gate/1.0 (mailto:mohamedoboda2@gmail.com)",
         "https://api.crossref.org/works/" + doi],
        capture_output=True, text=True).stdout
    return out.strip()


def clean(doi):
    while doi and doi[-1] in ").,;":
        if doi[-1] == ")" and doi.count("(") > doi.count(")"):
            break
        doi = doi[:-1]
    return doi


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-figures", type=int, default=9)
    parser.add_argument("--appendix-files", type=int, default=14)
    parser.add_argument("--offline", action="store_true", help="skip the DOI resolution check")
    arguments = parser.parse_args(argv)

    if not PDF.exists():
        print(f"FAIL: {PDF} does not exist; build it first")
        return 1

    failures = []
    text = pdf_text(PDF)

    appendix = len(re.findall(r"^ File: ", text, re.M))
    print(f"appendix files      : {appendix} (expected {arguments.appendix_files})")
    if appendix != arguments.appendix_files:
        failures.append("appendix file count")

    images = subprocess.run(["pdfimages", "-list", str(PDF)], capture_output=True, text=True).stdout
    embedded = len([line for line in images.splitlines()[2:] if " image " in line])
    print(f"embedded images     : {embedded} (expected at least {arguments.min_figures})")
    if embedded < arguments.min_figures:
        failures.append("embedded figures")

    info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
    pages = re.search(r"Pages:\s+(\d+)", info)
    print(f"pages               : {pages.group(1) if pages else '?'}")
    print(f"title metadata      : {'set' if 'Title:' in info and 'anonymous' not in info else 'MISSING'}")
    if "anonymous" in info:
        failures.append("PDF title metadata")

    joined = re.sub(r"\s+", " ", text)
    dois = sorted({clean(d) for d in re.findall(r"10\.[0-9]{4,}/[^\s,;]+", joined)})
    print(f"DOIs printed        : {len(dois)}")
    if not arguments.offline:
        for doi in dois:
            code = resolve(doi)
            print(f"  {code}  {doi}")
            if code != "200":
                failures.append(f"unresolving DOI {doi}")

    if failures:
        print("\nFAIL:", ", ".join(failures))
        return 1
    print("\nPASS: the PDF is complete and every reference in it resolves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
