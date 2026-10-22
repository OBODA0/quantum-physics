"""Build the assignment 2 PDF report.

Draft: the assignment brief has not been received, so the sections below describe the
instrument, the model, the phase database, the results and the verification. The
brief-driven sections (the graded questions and their weights) are added when it arrives.

Run with `uv run python -m report.generate_pdf_report`.
"""

from __future__ import annotations

import pathlib

import reportlab.rl_config

reportlab.rl_config.invariant = 1   # fixed timestamps and IDs: the PDF rebuilds byte-identically

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Image, Paragraph, Preformatted, SimpleDocTemplate,
                                Table, TableStyle)

from xrdsim.diffractometer import Instrument, reflections
from xrdsim.samples import PHASES

from .numbers_source import quoted_numbers

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
REPO_URL = "https://github.com/OBODA0/quantum-physics"
PDF_PATH = HERE / "Assignment_2_XRD_Diffractometer_Report.pdf"
FIG = HERE / "figures"


def styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("DocTitle", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=17, leading=21, spaceAfter=10),
        "subtitle": ParagraphStyle("DocSubtitle", parent=base["Normal"], fontName="Helvetica",
                                   fontSize=9, leading=13, textColor=colors.HexColor("#333333"),
                                   spaceAfter=6),
        "h1": ParagraphStyle("H1", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=13,
                             leading=16, spaceBefore=14, spaceAfter=6),
        "h2": ParagraphStyle("H2", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=10.5,
                             leading=13, spaceBefore=9, spaceAfter=4),
        "body": ParagraphStyle("Body", parent=base["Normal"], fontName="Helvetica", fontSize=9,
                               leading=12.4, spaceAfter=6),
        "caption": ParagraphStyle("Caption", parent=base["Normal"], fontName="Helvetica-Oblique",
                                  fontSize=8.2, leading=10.8, textColor=colors.HexColor("#333333"),
                                  spaceAfter=10),
        "code": ParagraphStyle("Code", parent=base["Normal"], fontName="Courier", fontSize=8,
                               leading=10.5, leftIndent=10),
    }


def figure(name: str, width_mm: float = 165) -> Image:
    path = FIG / name
    image = Image(str(path))
    scale = (width_mm * mm) / image.imageWidth
    image.drawWidth = width_mm * mm
    image.drawHeight = image.imageHeight * scale
    return image


def table(rows, widths, s):
    data = [[Paragraph(cell, s["body"]) for cell in row] for row in rows]
    grid = Table(data, colWidths=widths)
    grid.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#999999")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef1f6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return grid


def _footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawRightString(letter[0] - 54, 32, str(doc.page))
    canvas.restoreState()


def _wrap_code(text: str, width: int = 110) -> str:
    """Break over-long source lines so the appendix cannot run off the page."""
    lines = []
    for line in text.splitlines():
        while len(line) > width:
            lines.append(line[:width])
            line = "    " + line[width:]
        lines.append(line)
    return "\n".join(lines)


def code_appendix(story, s) -> None:
    story.append(Paragraph("Appendix A: the code", s["h1"]))
    story.append(Paragraph(
        "Every module the simulator ships, in the order the README lists them. The same "
        "files are in the repository under assignments/02-xrd-diffractometer/xrdsim/.",
        s["body"]))
    for path in sorted((REPO_ROOT / "xrdsim").glob("*.py")):
        story.append(Paragraph(f"xrdsim/{path.name}", s["h2"]))
        story.append(Preformatted(_wrap_code(path.read_text(encoding="utf-8")), s["code"]))


def build() -> None:
    s = styles()
    numbers = quoted_numbers()
    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=letter, leftMargin=54, rightMargin=54,
                            topMargin=54, bottomMargin=54,
                            title="Assignment 2: XRD Diffractometer Simulation",
                            author="Nanotechnology & Quantum Physics - Assignment 2")
    story = []
    story.append(Paragraph("Assignment 2: X-ray Powder Diffraction (XRD) Diffractometer Simulation",
                           s["title"]))
    story.append(Paragraph("<b>Course:</b> Nanotechnology &amp; Quantum Physics &nbsp;|&nbsp; "
                           "<b>Topic:</b> instrument simulation, Bragg-Brentano geometry, "
                           "structure factors, crystallite size", s["subtitle"]))
    story.append(Paragraph("<b>Students:</b> Mohamed Oboda (2111011090) &nbsp;|&nbsp; "
                           "Mert SOLMAZ (2311011039)", s["subtitle"]))
    story.append(Paragraph("<b>Status:</b> draft. The graded questions are not yet in this "
                           "document because the assignment brief has not been received; "
                           "everything below describes the simulator itself.", s["subtitle"]))

    meta = [
        ["Simulator", "Cu K-alpha tube, divergence and Soller slits, flat sample on a "
                      "theta/2theta goniometer, receiving slit, optional monochromator, "
                      "detector with Poisson counting statistics"],
        ["Phase database", "Si, Al, Cu, alpha-Fe, NaCl, MgO, ZnO, TiO2 rutile and anatase, "
                           "with the source of every cell constant in <font face=\"Courier\">"
                           "data/SOURCES.md</font>"],
        ["Physics", "Bragg's law, structure factor with Waasmaier-Kirfel form factors, "
                    "multiplicities, Lorentz-polarisation, Debye-Waller, K-alpha doublet, "
                    "Caglioti resolution, Scherrer broadening, Poisson noise"],
        ["Repository", REPO_URL],
    ]
    story.append(table([["<b>Item</b>", "<b>What it is</b>"]] + meta, [90, 355], s))

    # 1 -------------------------------------------------------------------
    story.append(Paragraph("1. The instrument", s["h1"]))
    story.append(Paragraph(
        "The simulator models the chain in Figure 1. A copper tube emits the K-alpha doublet "
        "at 1.540598 and 1.544426 angstrom, with K-beta removed by a filter or a monochromator. "
        "The beam leaves a divergence slit, is collimated by Soller slits, strikes a flat "
        "powder specimen on a theta/2theta goniometer, and reaches the detector through a "
        "receiving slit. The measured variable is 2theta; the specimen sits at theta, so a "
        "reflection appears when 2 d sin(theta) = n lambda.", s["body"]))
    story.append(figure("instrument.png"))
    story.append(Paragraph("Figure 1: the chain the simulator models. Every box is a module: "
                           "the tube and lines in <font face=\"Courier\">sources.py</font>, the "
                           "slits and flat-plate geometry in <font face=\"Courier\">geometry.py"
                           "</font>, the specimen in <font face=\"Courier\">samples.py</font>, "
                           "the detector in <font face=\"Courier\">detector.py</font>, and the "
                           "scan in <font face=\"Courier\">diffractometer.py</font>.",
                           s["caption"]))

    # 2 -------------------------------------------------------------------
    story.append(Paragraph("2. The model", s["h1"]))
    story.append(Paragraph(
        "Positions come from Bragg's law and the cell. Intensities are relative, as in "
        "assignment 1: the model reproduces patterns and intensity ratios, not absolute "
        "radiometry. For each reflection the relative intensity is |F|^2 m LP, where m is the "
        "powder multiplicity and LP = (1 + cos^2 2theta) / (sin^2 theta cos theta) without a "
        "monochromator. The structure factor sums the basis with the Waasmaier-Kirfel form "
        "factor f0(s), s = sin(theta)/lambda, and a Debye-Waller term exp(-B s^2).", s["body"]))
    story.append(Paragraph(
        "Each line is drawn with a pseudo-Voigt profile whose FWHM follows the Caglioti form "
        "sqrt(U tan^2 theta + V tan theta + W), combined with the Scherrer width K lambda / "
        "(D cos theta) for a crystallite size D. Counts are Poisson draws around the expected "
        "mean; the detector's dead time is available as a control.", s["body"]))
    story.append(Paragraph(
        "The model's absences are not tabulated. The 222 line of diamond, the 100 and 110 of "
        "an FCC metal and the 100 and 111 of a BCC metal are zero because the summed phases "
        "cancel, which is a check that the basis is right.", s["body"]))

    # 3 -------------------------------------------------------------------
    story.append(Paragraph("3. The phase database", s["h1"]))
    rows = [["Key", "Phase", "Space group", "Cell (A)", "Strongest line"]]
    instrument = Instrument()
    for key, phase in PHASES.items():
        lines = [row for row in reflections(phase, instrument) if row.intensity > 1e-9]
        best = max(lines, key=lambda row: row.intensity)
        label = "".join(str(v) for v in best.hkl)
        cell = f"a = {phase.a:.4f}" + (f", c = {phase.c:.4f}" if phase.c else "")
        rows.append([key, f"{phase.name} ({phase.formula})", phase.space_group, cell,
                     f"{label} at {best.two_theta:.2f} deg"])
    story.append(table(rows, [58, 92, 80, 95, 120], s))
    story.append(Paragraph("Table 1: the phases the simulator ships. Cell constants, their "
                           "sources and their confidence are listed in "
                           "<font face=\"Courier\">data/SOURCES.md</font>; every row is checked "
                           "against its published strongest reflection in the test suite.",
                           s["caption"]))

    # 4 -------------------------------------------------------------------
    story.append(Paragraph("4. Results", s["h1"]))
    story.append(Paragraph(
        "Figure 2 shows the nine phases under the same instrument settings. The differences "
        "are the physics: an FCC metal has few strong lines, a rocksalt has a weak 111 because "
        "the two form factors nearly cancel, wurtzite breaks the cubic degeneracy, and the two "
        "titania polymorphs give different patterns from the same formula.", s["body"]))
    story.append(figure("phase_panel.png"))
    story.append(Paragraph("Figure 2: simulated patterns, 20-90 deg, Cu K-alpha, 20 000 counts "
                           "at the strongest line, no noise. The hkl labels are the reflections "
                           "the model predicts.", s["caption"]))

    story.append(Paragraph("4.1 Crystallite size", s["h2"]))
    story.append(Paragraph(
        "Broadening combines the instrument and the specimen in quadrature. Figure 3 fixes the "
        "instrument (U, V, W) and varies the crystallite size; the Scherrer analysis in "
        "<font face=\"Courier\">xrdsim/analysis.py</font> subtracts the instrumental width in "
        "quadrature and recovers the input size to within about 1 % on a noiseless scan "
        f"({numbers['scherrer_range']} nm for an input of 30 nm).", s["body"]))
    story.append(figure("scherrer.png"))
    story.append(Paragraph("Figure 3: the silicon 111 line at 5, 20 and 200 nm. The curves are "
                           "normalised; the K-alpha2 line is switched off so that only the "
                           "intrinsic width remains.", s["caption"]))

    story.append(Paragraph("4.2 The K-alpha doublet", s["h2"]))
    story.append(Paragraph(
        "The doublet separation grows with angle, Delta(2theta) = 2 tan(theta) (lambda2 - "
        "lambda1)/lambda1: about 0.07 deg at 28 deg and 0.28 deg at 88 deg. Whether the two "
        "lines resolve depends on the peak width. With the default Caglioti width here "
        "(0.05-0.07 deg) silicon's 111 pair is barely separated and every higher line is "
        "resolved; a broader instrument merges them into one asymmetric peak, which is why a "
        "fitted width at low angle is not the instrument width.", s["body"]))
    story.append(figure("doublet.png"))
    story.append(Paragraph("Figure 4: silicon 422 with and without the K-alpha2 line, at the "
                           "same instrument settings.", s["caption"]))

    # 5 -------------------------------------------------------------------
    story.append(Paragraph("5. Verification", s["h1"]))
    story.append(Paragraph(
        "The suite covers lattice geometry, profiles, the detector, the structure factor and "
        "its absences, the scan, the analysis and the command line interface. Independent "
        "checks compare simulated peak positions with certified and published values: silicon "
        f"111/220/311/400 at {numbers['si_positions']} deg against the NIST SRM 640d values "
        "28.4425/47.3034/56.1211/69.1295, and the relative intensities "
        f"{numbers['si_ratios']} against the standard 100/55/30/5. The 0.001-0.003 deg residual on these four lines "
        "is the wavelength convention: the certificates quote 1.5405929 angstrom, the simulator "
        "uses 1.540598.", s["body"]))
    story.append(Paragraph(
        "Multiplicities are checked against a brute-force enumeration of the symmetry "
        "operations for cubic, tetragonal and hexagonal families. Intensity ratios agree with "
        "published patterns to within about a third on strong lines: copper 111/200/220 comes "
        f"out at {numbers['cu_ratios']} against the published 100/46/20, and rutile 110/101/211 "
        f"at {numbers['rutile_ratios']} against 100/50/60. The deviations are largest on weak "
        "lines and are not tuned: every site shares one Debye-Waller factor and no absorption "
        "correction is applied. The whole assignment rebuilds from a fresh clone: uv sync, the "
        "test suite, figures, tables, PDF and both gates.", s["body"]))
    story.append(Paragraph(
        "Defects found and fixed during the build are listed in "
        "<font face=\"Courier\">VERIFICATION.md</font>: a missing step factor in the profile, "
        "duplicate reflections from permuted indices, a Lorentz-polarisation divergence at "
        "180 deg, cell constants taken from primitive-cell conversions, and a hand-written "
        "anatase basis that produced a forbidden 001 line.", s["body"]))

    # 6 -------------------------------------------------------------------
    story.append(Paragraph("6. What is not modelled", s["h1"]))
    story.append(Paragraph(
        "Rietveld refinement, anomalous dispersion, texture beyond a single orientation "
        "factor, K-beta residual, detector energy discrimination and absolute intensities. "
        "The Cu K-alpha wavelengths are provisional: no primary table could be read from the "
        "build host. No simulated pattern has yet been compared with a measured scan; the "
        "comparisons above are with published peak positions and intensity ratios.", s["body"]))

    code_appendix(story, s)

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    print(f"wrote {PDF_PATH}")


if __name__ == "__main__":
    build()
