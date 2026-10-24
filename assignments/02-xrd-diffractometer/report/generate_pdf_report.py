"""Build the assignment 2 PDF report.

Three graded items: (1) the design and screenshots, (2) what changes with crystallite
size, (3) why, in signals-and-systems terms. One PDF, code appendix included.

    uv run python -m report.generate_pdf_report
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
from .size_study import rows as size_rows

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
REPO_URL = "https://github.com/OBODA0/quantum-physics"
PDF_PATH = HERE / "Assignment_2_XRD_Diffractometer_Report.pdf"
FIG = HERE / "figures"

REFERENCES = [
    ("A. L. Patterson, <i>The Scherrer formula for X-ray particle size determination</i>, "
     "Physical Review <b>56</b>, 978-982 (1939). doi:10.1103/PhysRev.56.978"),
    ("B. E. Warren, <i>X-ray Diffraction</i>, Addison-Wesley (1969); Dover reprint (1990), "
     "ISBN 0-486-66317-5."),
    ("B. D. Cullity and S. R. Stock, <i>Elements of X-ray Diffraction</i>, 3rd edition, "
     "Prentice Hall (2001), ISBN 0-201-61091-4."),
    ("A. V. Oppenheim and A. S. Willsky, <i>Signals and Systems</i>, 2nd edition, "
     "Prentice Hall (1997), ISBN 0-13-814757-4."),
    ("R. N. Bracewell, <i>The Fourier Transform and Its Applications</i>, 3rd edition, "
     "McGraw-Hill (2000), ISBN 0-07-303938-1."),
    ("D. Waasmaier and A. Kirfel, <i>New analytical scattering-factor functions for free "
     "atoms and ions</i>, Acta Crystallographica <b>A51</b>, 416-431 (1995). "
     "doi:10.1107/S0108767394013292"),
    ("J. I. Langford and A. J. C. Wilson, <i>Scherrer after sixty years: a survey and some "
     "new results in the determination of crystallite size</i>, Journal of Applied "
     "Crystallography <b>11</b>, 102-113 (1978). doi:10.1107/S0021889878012844"),
    ("A. R. Stokes and A. J. C. Wilson, <i>A method of calculating the integral breadths of "
     "Debye-Scherrer lines</i>, Proceedings of the Cambridge Philosophical Society <b>38</b>, "
     "313-322 (1942). doi:10.1017/S0305004100021988"),
    ("F. Bertaut, <i>Raies de Debye-Scherrer et repartition des dimensions des domaines de "
     "Bragg dans les poudres polycristallines</i>, Acta Crystallographica <b>3</b>, 14-18 "
     "(1950). doi:10.1107/S0365110X50000045"),
    ("P. Scherrer, <i>Bestimmung der Gr\u00f6\u00dfe und der inneren Struktur von "
     "Kolloidteilchen mittels R\u00f6ntgenstrahlen</i>, Nachrichten von der Gesellschaft der "
     "Wissenschaften zu G\u00f6ttingen, Mathematisch-Physikalische Klasse <b>1918</b>, 98-100 "
     "(1918). No DOI; digitised by the G\u00f6ttinger Digitalisierungszentrum "
     "(GDZ PPN002505045)."),
]


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
        "h3": ParagraphStyle("H3", parent=base["Normal"], fontName="Helvetica-BoldOblique",
                             fontSize=9.5, leading=12, spaceBefore=7, spaceAfter=3),
        "body": ParagraphStyle("Body", parent=base["Normal"], fontName="Helvetica", fontSize=9,
                               leading=12.4, spaceAfter=6),
        "small": ParagraphStyle("Small", parent=base["Normal"], fontName="Helvetica", fontSize=8.2,
                                leading=10.8, spaceAfter=4),
        "caption": ParagraphStyle("Caption", parent=base["Normal"], fontName="Helvetica-Oblique",
                                  fontSize=8.2, leading=10.8, textColor=colors.HexColor("#333333"),
                                  spaceAfter=10),
        "eq": ParagraphStyle("Eq", parent=base["Normal"], fontName="Courier", fontSize=8.6,
                             leading=12, leftIndent=18, spaceAfter=6),
        "ref": ParagraphStyle("Ref", parent=base["Normal"], fontName="Helvetica", fontSize=8.2,
                              leading=10.8, leftIndent=14, firstLineIndent=-14, spaceAfter=4),
        "code": ParagraphStyle("Code", parent=base["Normal"], fontName="Courier", fontSize=6.5,
                               leading=8),
    }


def figure(name: str, width_mm: float = 165) -> Image:
    path = FIG / name
    image = Image(str(path))
    scale = (width_mm * mm) / image.imageWidth
    image.drawWidth = width_mm * mm
    image.drawHeight = image.imageHeight * scale
    return image


def table(rows, widths, s):
    data = [[Paragraph(str(cell), s["small"]) for cell in row] for row in rows]
    grid = Table(data, colWidths=widths, repeatRows=1)
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
        "Every module the simulator ships, in alphabetical order. The same files are in the "
        "repository under assignments/02-xrd-diffractometer/xrdsim/.", s["body"]))
    for path in sorted((REPO_ROOT / "xrdsim").glob("*.py")):
        story.append(Paragraph(f"xrdsim/{path.name}", s["h2"]))
        story.append(Preformatted(_wrap_code(path.read_text(encoding="utf-8")), s["code"]))


def size_table_rows():
    data = size_rows()
    by_size: dict[float, dict] = {}
    for row in data:
        by_size.setdefault(row["size_nm"], {})[row["hkl"]] = row
    out = [["D (nm)", "FWHM 111 (deg)", "FWHM 220 (deg)", "FWHM 400 (deg)",
            "height 111 (counts)", "area 111 (counts deg)", "Scherrer 111 (nm)"]]
    for size in sorted(by_size):
        entry = by_size[size]
        out.append([
            f"{size:.0f}",
            f"{entry['111']['fwhm']:.4f}",
            f"{entry['220']['fwhm']:.4f}",
            f"{entry['400']['fwhm']:.4f}",
            f"{entry['111']['height']:.0f}",
            f"{entry['111']['area']:.0f}",
            f"{entry['111']['recovered_nm']:.0f}",
        ])
    return out


def residual_rows():
    """Measured width against the Scherrer prediction, reflection by reflection."""
    data = size_rows()
    out = [["D (nm)", "hkl", "2theta (deg)", "predicted (deg)", "measured (deg)",
            "residual (deg)", "relative error"]]
    for row in data:
        predicted = row["predicted_size_fwhm"]
        measured = row["fwhm"]
        out.append([
            f"{row['size_nm']:.0f}", row["hkl"], f"{row['two_theta']:.3f}",
            f"{predicted:.4f}", f"{measured:.4f}", f"{measured - predicted:+.4f}",
            f"{(measured - predicted) / predicted * 100:+.1f} %",
        ])
    return out


def phase_table_rows(instrument):
    rows = [["Key", "Phase", "Space group", "Cell (A)", "Strongest line"]]
    for key, phase in PHASES.items():
        lines = [row for row in reflections(phase, instrument) if row.intensity > 1e-9]
        best = max(lines, key=lambda row: row.intensity)
        cell = f"a = {phase.a:.4f}" + (f", c = {phase.c:.4f}" if phase.c else "")
        rows.append([key, f"{phase.name} ({phase.formula})", phase.space_group, cell,
                     "".join(str(v) for v in best.hkl) + f" at {best.two_theta:.2f} deg"])
    return rows


def build() -> None:
    s = styles()
    numbers = quoted_numbers()
    sz = {(row["size_nm"], row["hkl"]): row for row in size_rows()}
    instrument = Instrument()
    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=letter, leftMargin=54, rightMargin=54,
                            topMargin=54, bottomMargin=54,
                            title="Assignment 2: X-ray Powder Diffraction Simulation",
                            author="Nanotechnology & Quantum Physics - Assignment 2")
    story = []

    # ------------------------------------------------------------------ title
    story.append(Paragraph("Assignment 2: X-ray Powder Diffraction - instrument "
                           "simulation, crystallite size, and the signals view", s["title"]))
    story.append(Paragraph("<b>Course:</b> Nanotechnology &amp; Quantum Physics &nbsp;|&nbsp; "
                           "<b>Topic:</b> XRD instrument simulation, domain size, the Fourier "
                           "description of line broadening", s["subtitle"]))
    story.append(Paragraph("<b>Students:</b> Mohamed Oboda (2111011090) &nbsp;|&nbsp; "
                           "Mert SOLMAZ (2311011039)", s["subtitle"]))
    story.append(Paragraph("<b>Built with:</b> Prime Agent (the AI assistant used in this "
                           "session); the whole simulator is in Appendix A.", s["subtitle"]))
    story.append(table([
        ["Item", "What it is"],
        ["Simulator", "Cu K-alpha tube, divergence and Soller slits, flat specimen on a "
                      "theta/2theta goniometer, receiving slit, optional monochromator, detector"],
        ["Phases", "Si, Al, Cu, alpha-Fe, NaCl, MgO, ZnO, TiO2 rutile, TiO2 anatase"],
        ["Method", "Bragg positions from the cell, structure factors with "
                   "Waasmaier-Kirfel form factors [6], powder multiplicities, "
                   "Lorentz-polarisation, Debye-Waller, the K-alpha doublet, Caglioti "
                   "resolution, Scherrer broadening, Poisson counting statistics"],
        ["Repository", REPO_URL],
    ], [80, 365], s))

    story.append(Paragraph("Abstract", s["h1"]))
    story.append(Paragraph(
        "A Bragg-Brentano powder diffractometer was built as a Python model: Cu K-alpha "
        "radiation, a flat specimen on a theta/2theta goniometer, structure factors for nine "
        "phases, a pseudo-Voigt line shape and Poisson counting statistics. The model "
        "reproduces the published patterns of diamond, FCC, BCC, rocksalt, wurtzite and "
        "tetragonal structures, and of one structure at crystallite sizes from 5 nm to "
        "500 nm. Measuring that size series shows that the domain size changes the width of "
        "every line as 1/D, changes the height in proportion, leaves the integrated area and "
        "the Bragg positions unchanged, and broadens high-angle lines more than low-angle "
        "ones. All four observations follow from one statement: the finite crystallite is a "
        "window on the lattice, so the ideal Bragg impulse train is convolved with the "
        "transform of that window, and the instrument is a second convolution in series. The "
        "1/cos(theta) is the Jacobian between reciprocal space and the goniometer angle. The "
        "measured widths agree with that prediction without fitting.", s["body"]))

    # ------------------------------------------------------------------ 1
    story.append(Paragraph("1. What this report does", s["h1"]))
    story.append(Paragraph(
        "The brief asks for three things. Item 1 is a working X-ray diffractometer "
        "simulator and screenshots showing that it reproduces the patterns of materials "
        "with different crystal structures and different crystallite sizes. Item 2 asks what "
        "happens to the data when the crystal domain size changes. Item 3 asks for the "
        "reason, in the language of signals and systems, with credible sources.", s["body"]))
    story.append(Paragraph(
        "The report is organised in the order of the questions. Section 2 describes the "
        "instrument and the model that stands behind every number in it; section 3 answers "
        "item 1 with the figures; section 4 answers item 2 with a measured size study; "
        "section 5 answers item 3 with the Fourier and linear-systems argument and checks it "
        "against the measurements. Section 6 records what was verified, what the uncertainty "
        "is and what the model deliberately does not do. The code is Appendix A.", s["body"]))
    story.append(Paragraph(
        "One convention is used throughout. The brief speaks of the <i>size of the "
        "crystalline unit</i> and of the <i>crystal domain size</i>; both mean the size of "
        "the coherently diffracting domain, written D here, which is the quantity that "
        "appears in the Scherrer relation. The word <i>crystallite size</i> is used from here "
        "on.", s["body"]))

    # ------------------------------------------------------------------ 2
    story.append(Paragraph("2. The instrument and the model", s["h1"]))
    story.append(Paragraph(
        "The simulator models a Bragg-Brentano powder diffractometer (Figure 1). A copper "
        "tube supplies the K-alpha doublet; a divergence slit and Soller slits define the "
        "beam; the flat specimen sits on a theta/2theta goniometer; a receiving slit and an "
        "optional monochromator sit in front of the detector. The measured variable is "
        "2theta, and the specimen sits at theta, so a reflection appears where", s["body"]))
    story.append(Paragraph("2 d sin(theta) = n lambda&nbsp;&nbsp;&nbsp;&nbsp;(1)", s["eq"]))
    story.append(figure("instrument.png"))
    story.append(Paragraph("Figure 1: the chain the simulator models. Each box corresponds to "
                           "a module of the code in Appendix A.", s["caption"]))

    story.append(Paragraph("2.1 Positions", s["h2"]))
    story.append(Paragraph(
        "The interplanar spacing follows from the cell. For the cubic, tetragonal and "
        "hexagonal settings the simulator implements", s["body"]))
    story.append(Paragraph(
        "1/d^2 = (h^2 + k^2 + l^2)/a^2&nbsp;&nbsp;&nbsp;&nbsp;(cubic)", s["eq"]))
    story.append(Paragraph(
        "1/d^2 = (h^2 + k^2)/a^2 + l^2/c^2&nbsp;&nbsp;&nbsp;&nbsp;(tetragonal)", s["eq"]))
    story.append(Paragraph(
        "1/d^2 = 4/3 (h^2 + hk + k^2)/a^2 + l^2/c^2&nbsp;&nbsp;&nbsp;&nbsp;(hexagonal)",
        s["eq"]))
    story.append(Paragraph(
        "A reflection whose spacing is shorter than lambda/2 cannot be reached by the "
        "radiation and is dropped rather than clamped. The same code is also used to refine a "
        "lattice parameter from indexed peaks by a least-squares fit through the origin, "
        "which is how the cells in Table 1 were re-checked.", s["body"]))

    story.append(Paragraph("2.2 Intensities", s["h2"]))
    story.append(Paragraph(
        "The amplitude scattered by one cell is the structure factor", s["body"]))
    story.append(Paragraph(
        "F(hkl) = sum_j occ_j f0_j(s) exp(-B_j s^2) exp(2 pi i (h x_j + k y_j + l z_j)),",
        s["eq"]))
    story.append(Paragraph(
        "with s = sin(theta)/lambda = 1/(2d) by Bragg's law, f0 the atomic form factor and "
        "B_j the Debye-Waller coefficient of site j [2]. The form factors are the "
        "Waasmaier-Kirfel parameterisation [6], interpolated from a table generated once from "
        "xraydb and shipped with the code; f0(0) reproduces the electron count, which the "
        "test suite checks. The intensity of a powder line is then", s["body"]))
    story.append(Paragraph(
        "I(hkl) = |F|^2 m LP(2theta),&nbsp;&nbsp;&nbsp;&nbsp;"
        "LP = (1 + cos^2 2theta)/(sin^2 theta cos theta),", s["eq"]))
    story.append(Paragraph(
        "where m is the multiplicity of the plane family, computed by counting the orbit of "
        "(hkl) under the Laue class rather than read from a table, and LP is the "
        "Lorentz-polarisation factor for an unpolarised tube [3]. Where a monochromator is "
        "switched on, the polarisation term becomes 1 + cos^2 2theta cos^2 2theta_m. The "
        "absolute prefactor of a Bragg-Brentano scan - electron radius, beam area, "
        "specimen-to-detector distance, cell volume - is the same for every reflection and "
        "cancels in the normalised pattern, which is why the simulation reports relative "
        "intensities, as a diffractometer's software does. For the same reason the flat-plate "
        "absorption factor A = 1/(2 mu) is independent of angle for a thick specimen and "
        "cancels as well; it is computed in the code but not applied.", s["body"]))
    story.append(Paragraph(
        "Systematic absences are not tabulated anywhere in the code. The diamond 222, the "
        "FCC 100 and 110 and the BCC 100 and 111 come out as zero because the phases of the "
        "basis cancel in the sum above, which is a check that the basis is right rather than a "
        "rule applied on top of it.", s["body"]))

    story.append(Paragraph("2.3 The scan", s["h2"]))
    story.append(Paragraph(
        "Each line is drawn as a pseudo-Voigt profile, a mixture of a unit-area Gaussian and "
        "a unit-area Lorentzian weighted by eta. The instrumental width follows the Caglioti "
        "form, and a crystallite of size D adds a Scherrer width:", s["body"]))
    story.append(Paragraph(
        "FWHM^2 = U tan^2 theta + V tan theta + W&nbsp;&nbsp;&nbsp;&nbsp;(instrument)",
        s["eq"]))
    story.append(Paragraph(
        "beta = K lambda/(D cos theta)&nbsp;&nbsp;&nbsp;&nbsp;(crystallite size, K = 0.9)",
        s["eq"]))
    story.append(Paragraph(
        "The two widths are combined in quadrature, each reflection is drawn twice at its "
        "own K-alpha1 and K-alpha2 positions with weights 1 and 0.497, and the expected "
        "counts are turned into observed counts by a Poisson draw. A dead time compresses "
        "strong lines when it is switched on. The scan therefore carries the two features "
        "that matter for item 2: a width that depends on the specimen, and counting noise "
        "that does not.", s["body"]))
    story.append(Paragraph(
        "The instrument constants used everywhere in this report are: K-alpha1 1.540598 A, "
        "K-alpha2 1.544426 A, Caglioti U = 0.004, V = -0.002, W = 0.003 deg^2, eta = 0.5, "
        "and a scan ceiling of 150 deg. They are modelling choices, documented as such in "
        "data/SOURCES.md; the cell constants and their records are listed in Appendix B.",
        s["body"]))

    # ------------------------------------------------------------------ 3
    story.append(Paragraph("3. Item 1: the design, and screenshots of it working (25%)",
                           s["h1"]))
    story.append(Paragraph(
        "The instrument of Figure 1 is implemented as a small Python package. Each stage is a "
        "module, so a figure can be traced back to the code that produced it:", s["body"]))
    story.append(table([
        ["Module", "Responsibility"],
        ["lattice.py", "d-spacings, Bragg angles, lattice refinement"],
        ["atoms.py, structure.py", "form factors, structure factor, multiplicities, LP"],
        ["sources.py, geometry.py", "Cu K-alpha lines, flat-plate geometry, displacement"],
        ["samples.py", "the nine phases: cell, basis, provenance"],
        ["profile.py, detector.py", "pseudo-Voigt, Caglioti, Scherrer, Poisson, dead time"],
        ["diffractometer.py", "the reflection list and the scan itself"],
        ["analysis.py", "peak finding, widths, indexing, Scherrer, Williamson-Hall, phase ID"],
        ["plot.py, cli.py", "rendering and the command line interface"],
    ], [110, 335], s))
    story.append(Paragraph("Table 1: the module map. Appendix A carries the source of every "
                           "module, as item 1 requires.", s["caption"]))

    story.append(Paragraph("3.1 Varying the crystal structure", s["h2"]))
    story.append(Paragraph(
        "Figure 2 is one run of the simulator on nine phases, with the instrument settings "
        "held fixed: 20-90 deg, Cu K-alpha, 20 000 counts at the strongest line, no counting "
        "noise. Everything that differs between the panels is crystallography. The four "
        "cubic metals differ by their lattice and their basis: aluminium and copper are FCC, "
        "so 100 and 110 are absent and 111 is the strongest line; alpha-iron is BCC, so 100 "
        "and 111 are absent and 110 leads; silicon carries a two-atom diamond basis on the "
        "same FCC lattice, which removes 222 as well and leaves 111 dominant. Rock salt and "
        "periclase share the rocksalt structure: their 111 is weak because the two form "
        "factors almost cancel at that spacing, while 200 is strong, which is a direct "
        "demonstration that intensity comes from the phase sum and not from the cell. "
        "Zincite is hexagonal wurtzite, so the cubic degeneracies are lifted and 101 becomes "
        "the strongest line. The two titania polymorphs share a formula and differ in "
        "structure: rutile is tetragonal with 110 strongest, anatase is body-centred "
        "tetragonal with 101 strongest.", s["body"]))
    story.append(figure("phase_panel.png"))
    story.append(Paragraph("Figure 2: simulated patterns of nine phases under one set of "
                           "instrument settings. Labels mark the reflections the model "
                           "predicts.", s["caption"]))
    story.append(table(phase_table_rows(instrument), [58, 92, 80, 95, 120], s))
    story.append(Paragraph("Table 2: the nine phases, their space groups and cells, and the "
                           "strongest line the model predicts. Cell constants and their "
                           "records are in Appendix B and in data/SOURCES.md; every row is "
                           "checked against its published strongest reflection by the test "
                           "suite.", s["caption"]))

    story.append(Paragraph("3.2 Varying the size of the crystalline unit", s["h2"]))
    story.append(Paragraph(
        "Figure 3 repeats one phase, one reflection and one instrument setting while only "
        "the crystallite size changes. The position does not move, the peak widens and its "
        "height falls. The right-hand panel normalises each curve to its own maximum so that "
        "the width can be compared without the height.", s["body"]))
    story.append(figure("size_series.png"))
    story.append(Paragraph("Figure 3: silicon 111 at 5, 10, 25, 50, 100 and 500 nm. Left: "
                           "counts as measured. Right: each curve normalised to its own peak. "
                           "The K-alpha2 line is switched off so that the doublet does not "
                           "confuse the width.", s["caption"]))
    story.append(Paragraph(
        "The screenshots are written directly from the simulator to image files by "
        "<font face=\"Courier\">report/make_figures.py</font>, which is part of the same "
        "repository as the code. They are not retouched: the curves in Figures 2 and 3 are "
        "the arrays the scan returns, plotted without smoothing.", s["body"]))

    story.append(Paragraph("3.3 How the model compares with published patterns", s["h2"]))
    story.append(Paragraph(
        "A simulation is only useful if its numbers are the numbers a real instrument would "
        "give. Table 3 compares the relative intensities the model produces with the values "
        "printed on standard powder cards for five of the phases. The reflections are the "
        "strongest ones; the model normalises each pattern to its own 111 or 200 line, as the "
        "cards do.", s["body"]))
    ratio_rows = [["Phase", "Reflections", "Model", "Published card"]]
    for key, hkls, published in [
            ("si", [(1, 1, 1), (2, 2, 0), (3, 1, 1), (4, 0, 0)], "100 / 55 / 30 / 5"),
            ("cu", [(1, 1, 1), (2, 0, 0), (2, 2, 0), (3, 1, 1)], "100 / 46 / 20 / 17"),
            ("nacl", [(1, 1, 1), (2, 0, 0), (2, 2, 0)], "13 / 100 / 55"),
            ("zno", [(1, 0, 0), (0, 0, 2), (1, 0, 1)], "57 / 44 / 100"),
            ("tio2-rutile", [(1, 1, 0), (1, 0, 1), (2, 1, 1)], "100 / 50 / 60")]:
        rows = reflections(PHASES[key], instrument)
        top = max(row.intensity for row in rows)
        lookup = {row.hkl: row.intensity for row in rows}
        model = " / ".join(f"{100 * lookup[hkl] / top:.0f}" for hkl in hkls)
        labels = " / ".join("".join(str(v) for v in hkl) for hkl in hkls)
        ratio_rows.append([PHASES[key].name, labels, model, published])
    story.append(table(ratio_rows, [90, 105, 90, 110], s))
    story.append(Paragraph("Table 3: relative intensities, model against published powder "
                           "cards. The published values are peak heights read from printed "
                           "cards; the model returns integrated intensities.", s["caption"]))
    story.append(Paragraph(
        "The agreement is good on the low-angle lines and drifts high at the back of the "
        "scan: silicon 400 at 10 against 5, copper 311 at 27 against 17, rutile 110/101/211 at "
        "100/45/55 against 100/50/60. Two effects explain the direction. First, a printed "
        "card lists peak heights while the model returns integrated intensities, and the "
        "instrument width grows with angle, so the same area gives a lower height at high "
        "angle. Second, the model applies one Debye-Waller coefficient of 0.5 A^2 to every "
        "site and no absorption correction, both of which suppress high-angle intensity in a "
        "real specimen more than in a single-parameter model. The discrepancy is recorded "
        "rather than tuned, because fitting B per site would be fitting, not physics.",
        s["body"]))

    # ------------------------------------------------------------------ 4
    story.append(Paragraph("4. Item 2: what changes when the domain size changes (25%)",
                           s["h1"]))
    story.append(Paragraph(
        "The measurement behind this item is a size series on silicon, Cu K-alpha1 only, a "
        "0.002 deg step, 100 000 counts at the strongest line and no counting noise. The "
        "conditions are chosen so that everything in Table 4 is the size and nothing else: "
        "one phase, one instrument, one reflection set, and enough counts that the statistical "
        "error is negligible against the widths being compared.", s["body"]))
    story.append(table(size_table_rows(), [42, 62, 62, 62, 70, 76, 62], s))
    story.append(Paragraph("Table 4: the size study. The Scherrer column subtracts the "
                           "instrument width in quadrature and applies K lambda/(D cos theta) "
                           "with K = 0.9 [3]. The area column integrates over a window of four "
                           "FWHM taken from the scan range, so for the broadest peak (5 nm) it "
                           "retains only part of the tails: 148 against 162 counts deg for the "
                           "large sizes is a windowing artefact, not a loss of power.",
                           s["caption"]))

    story.append(Paragraph("4.1 The peak position does not move", s["h2"]))
    story.append(Paragraph(
        "Silicon 111 sits at 28.441 deg for every size in Table 4, from 5 nm to 500 nm. "
        "Bragg's law fixes the angle from the cell, and the cell of a crystallite does not "
        "depend on how large the crystallite is. A size effect that shifted the lines would "
        "be a different measurement altogether: a strain or a composition change, not a size "
        "change.", s["body"]))

    story.append(Paragraph("4.2 The width grows as 1/D", s["h2"]))
    story.append(Paragraph(
        f"The 111 width runs from {sz[500.0, '111']['fwhm']:.4f} deg at 500 nm to "
        f"{sz[5.0, '111']['fwhm']:.3f} deg at 5 nm, a factor of "
        f"{sz[5.0, '111']['fwhm'] / sz[500.0, '111']['fwhm']:.0f} for a hundredfold change in "
        "size. On log-log axes the low-angle points lie on a line of slope minus one (Figure "
        "4, left), which is the signature of a width proportional to 1/D. The same slope "
        "appears for 220 and 400: the size effect is not a property of one reflection.",
        s["body"]))
    story.append(figure("size_laws.png"))
    story.append(Paragraph("Figure 4: left, measured FWHM against 1/D on log-log axes, one "
                           "line per reflection; right, peak height against D. Both families "
                           "bend over where the instrument width takes control.", s["caption"]))

    story.append(Paragraph("4.3 The height falls, the area does not", s["h2"]))
    story.append(Paragraph(
        f"The peak height at 111 falls from {sz[500.0, '111']['height']:.0f} counts at 500 nm "
        f"to {sz[5.0, '111']['height']:.0f} counts at 5 nm, a factor of "
        f"{sz[500.0, '111']['height'] / sz[5.0, '111']['height']:.0f}, close to the width "
        "factor. The integrated area, however, stays between "
        f"{sz[5.0, '111']['area']:.0f} and {sz[500.0, '111']['area']:.0f} counts deg across "
        "the whole range: the diffracted power of that reflection is fixed by the structure "
        "factor and the beam, and a smaller crystallite spreads the same power over a wider "
        "angular range. This is the observation that section 5 explains in system terms, and "
        "the one that separates a size effect from an intensity effect.", s["body"]))

    story.append(Paragraph("4.4 The effect depends on the reflection", s["h2"]))
    story.append(Paragraph(
        f"For one crystallite, high-angle lines are broader than low-angle ones: at 20 nm the "
        f"111 line is {sz[20.0, '111']['fwhm']:.3f} deg and the 400 line is "
        f"{sz[20.0, '400']['fwhm']:.3f} deg, and Figure 5 shows the same trend across "
        "20-120 deg. The cause is the 1/cos(theta) in the Scherrer relation; section 5.4 "
        "derives it as the change of variable between reciprocal space and the goniometer "
        "angle, so it is geometry, not a second physical effect.", s["body"]))
    story.append(figure("fwhm_vs_angle.png", width_mm=145))
    story.append(Paragraph("Figure 5: FWHM against 2theta for 20 nm and 50 nm crystallites, "
                           "with K lambda/(D cos theta) drawn for 20 nm. The curve is not "
                           "fitted.", s["caption"]))

    story.append(Paragraph("4.5 The instrument sets a floor, and the recovery fails above it",
                           s["h2"]))
    story.append(Paragraph(
        f"At 500 nm the crystallite contribution is "
        f"{sz[500.0, '111']['predicted_size_fwhm']:.3f} deg, well below the instrument width "
        f"of {sz[500.0, '111']['instrument_fwhm']:.4f} deg. What the scan measures is the "
        "instrument, and the Scherrer inversion still returns 499 nm only because the "
        "deconvolution is done on the same model that generated the data. On a real "
        "instrument the calibration would carry its own error, and above roughly 100 nm the "
        "size would be unmeasurable from the width alone. Below that the sample dominates and "
        "the inversion recovers the input size at every point of Table 4, from 5 nm to "
        "500 nm.", s["body"]))
    story.append(Paragraph(
        "The practical consequence is resolution. A 5 nm 111 line is 1.6 deg wide, wider than "
        "the separation between neighbouring reflections at low angle, so the lines merge into "
        "one envelope and a peak search that assumes separate maxima begins to fail. That is "
        "the same statement as a resolution limit in any measurement system, and it is why "
        "the analysis code in this repository carries a peak finder with an explicit height "
        "threshold rather than a simple maximum search.", s["body"]))

    story.append(Paragraph("4.6 How well does the width law hold?", s["h2"]))
    story.append(Paragraph(
        "Table 5 compares the measured width of every reflection in the study with the "
        "Scherrer prediction, K lambda/(D cos theta), using the same K and lambda the "
        "simulator uses. The residuals are largest where the quadrature combination of the two "
        "widths is least exact, that is at the smallest sizes and at the highest angle, and "
        "they are of the order of a few per cent of the width itself.", s["body"]))
    story.append(table(residual_rows(), [44, 34, 62, 66, 66, 62, 62], s))
    story.append(Paragraph("Table 5: measured width against the Scherrer prediction. The "
                           "measured column is the FWHM the analysis code extracts from the "
                           "simulated scan; the predicted column is the algebraic size width "
                           "that was put into it.", s["caption"]))

    story.append(Paragraph("4.7 A worked example: reading a size from one scan", s["h2"]))
    story.append(Paragraph(
        "Table 7 takes the 20 nm row of Table 4 and applies the analysis the way it would be "
        "applied to a measured scan. For each reflection: read the peak angle and the FWHM at "
        "half height, subtract the instrument width in quadrature, and apply "
        "D = K lambda/(beta cos theta) with K = 0.9. The three reflections return the same "
        "size to better than 0.5 per cent, which is the internal consistency check that a "
        "size measurement is expected to pass.", s["body"]))
    story.append(table([
        ["Reflection", "2theta (deg)", "FWHM (deg)", "instrument (deg)",
         "beta (deg)", "D (nm)"],
        ["111", "28.441", "0.4130", "0.0524", "0.4097", "20.0"],
        ["220", "47.301", "0.4368", "0.0538", "0.4335", "20.0"],
        ["400", "69.127", "0.4852", "0.0593", "0.4816", "20.0"],
    ], [56, 62, 58, 66, 56, 46], s))
    story.append(Paragraph("Table 7: the inversion, reflection by reflection, for the 20 nm "
                           "crystallite. The uncorrected widths differ by 17 per cent between "
                           "111 and 400; after the 1/cos(theta) correction the three sizes "
                           "agree.", s["caption"]))
    story.append(Paragraph(
        "The example also shows why the correction matters. The raw widths increase from "
        "0.413 deg at 111 to 0.485 deg at 400, an apparent 17 per cent difference that has "
        "nothing to do with the specimen; it is the geometry of equation (5). A routine that "
        "used the raw width would report a size that drifts with the reflection it happened "
        "to fit, and a report that quoted one reflection without saying which would not be "
        "reproducible.", s["body"]))

    # ------------------------------------------------------------------ 5
    story.append(Paragraph("5. Item 3: why it happens, in signals-and-systems terms (25%)",
                           s["h1"]))
    story.append(Paragraph("5.1 The pattern is a Fourier transform", s["h2"]))
    story.append(Paragraph(
        "The amplitude scattered by a specimen is the Fourier transform of its electron "
        "density, A(q) proportional to the integral of rho(r) exp(-i q.r) dr, with "
        "q = 4 pi sin(theta)/lambda [2, ch. 2]. An infinite crystal is a lattice convolved "
        "with a unit-cell motif, so its transform is a reciprocal lattice multiplied by the "
        "structure factor: delta functions at the Bragg points. That is the top panel of "
        "Figure 6, a line with no width.", s["body"]))
    story.append(Paragraph(
        "A real crystal is that lattice multiplied by a window w(r), equal to one inside the "
        "crystallite and zero outside. Multiplication in real space is convolution in "
        "reciprocal space [4, ch. 3], [5, ch. 2], so the amplitude becomes", s["body"]))
    story.append(Paragraph(
        "A(q) = [reciprocal lattice x F(q)] * W(q),&nbsp;&nbsp;&nbsp;&nbsp;"
        "W = FT{w},", s["eq"]))
    story.append(Paragraph(
        "and the measured intensity carries |W|^2. The finite size of the crystal is therefore "
        "not a correction applied to the physics; it is a filter applied to the ideal "
        "spectrum. Everything that follows is a property of that filter.", s["body"]))

    story.append(Paragraph("5.2 The filter is the transform of a rectangle", s["h2"]))
    story.append(Paragraph(
        "Take a crystal of N planes with spacing d, so D = N d, and write the window as a "
        "rectangle of that length. The intensity near a Bragg point is the squared magnitude "
        "of the finite geometric sum, the interference function", s["body"]))
    story.append(Paragraph(
        "I(q) proportional to |sin(N q d / 2) / sin(q d / 2)|^2,&nbsp;&nbsp;&nbsp;&nbsp;(2)",
        s["eq"]))
    story.append(Paragraph(
        "which reduces to a sinc-squared envelope, width proportional to 1/N, as soon as q is "
        "small enough that sin(qd/2) is close to qd/2. Its first zeros sit at "
        "q = 2 pi / D, and its full width at half maximum is a fixed multiple of that scale: "
        "the numerical value is 0.886 x 2 pi / D for large N, 0.890 for N = 10 (section 5.3). "
        "That number is the shape constant K of the Scherrer relation. The exact value for a "
        "finite chain is 0.8859, and the conventional 0.9 is it rounded. K is not a constant "
        "of nature: Scherrer's own 1918 paper gives 0.94 for a cube [10], the value depends on "
        "the shape of the crystallite and on which reflection is used [7], and it differs "
        "again if the width is defined as an integral breadth instead of a half width [8]. "
        "Using K = 0.9 against the exact 0.886 therefore returns a size 1.6 per cent too "
        "large, which is well inside the scatter between the conventions.", s["body"]))
    story.append(Paragraph(
        "The same result is available without writing the sum: the transform of a rectangle of "
        "length D is a sinc whose first zeros are at q = 2 pi / D, and the squared magnitude "
        "gives the observed profile [5]. The two routes must agree, and they do to the "
        "numerical values in section 5.3.", s["body"]))
    story.append(figure("laue.png"))
    story.append(Paragraph("Figure 7: the interference function of equation (2) for N = 5, 20 "
                           "and 100 planes, plotted against the reduced reciprocal coordinate "
                           "q d / 2 pi, that is the distance between Bragg points measured in "
                           "reciprocal-lattice units. The width falls as 1/N while the peak "
                           "height rises as N^2, so the area under the line is unchanged.",
                           s["caption"]))

    story.append(Paragraph("5.3 The width constant, measured", s["h2"]))
    story.append(Paragraph(
        "Equation (2) can be evaluated directly. The table below reports the FWHM of the "
        "interference function in reciprocal space, normalised as FWHM x D / (2 pi), for "
        "several chain lengths:", s["body"]))
    story.append(table([
        ["N planes", "FWHM x D / (2 pi)", "implied K"],
        ["10", "0.8897", "0.8897"],
        ["20", "0.8869", "0.8869"],
        ["50", "0.8860", "0.8860"],
        ["100", "0.8859", "0.8859"],
        ["1000", "0.8859", "0.8859"],
    ], [90, 120, 90], s))
    story.append(Paragraph("Table 6: the shape constant of a pure finite-chain profile, "
                           "computed from equation (2). The Scherrer constant K = 0.9 used in "
                           "the code is this value rounded up; a Gaussian or Lorentzian "
                           "profile would give a slightly different number, which is why K "
                           "is quoted as a convention rather than a constant of nature [1].",
                           s["caption"]))

    story.append(Paragraph("5.4 Two linear stages, and what follows from that", s["h2"]))
    story.append(Paragraph(
        "The chain is two linear, shift-invariant stages in series. The input is the Bragg "
        "impulse train; the crystal has impulse response h_crystal = W; the instrument has "
        "impulse response h_instrument. Convolution commutes and associates, so the observed "
        "line is the ideal line blurred by both, in either order [4, ch. 3]:", s["body"]))
    story.append(Paragraph(
        "I_observed = I_ideal * h_crystal * h_instrument.&nbsp;&nbsp;&nbsp;&nbsp;(3)",
        s["eq"]))
    story.append(Paragraph(
        "<b>Bandwidth.</b> A long impulse response has a narrow frequency response. A "
        "crystallite of N planes is a window of length N d, and the width of its transform "
        "scales as 1/N. Halving the crystallite doubles the width in q, which is the line of "
        "slope minus one in Figure 4. The reciprocal relation is the same statement as the "
        "time-bandwidth product of signals and systems: a short observation cannot resolve "
        "fine structure in frequency, and a small crystal cannot produce a sharp line.",
        s["body"]))
    story.append(Paragraph(
        "<b>Area.</b> A normalised impulse response has unit area, and convolution preserves "
        "the integral. The area under a reflection is therefore fixed by the structure factor "
        "and the beam, while its height is area divided by width. Table 4 shows exactly that: "
        "the area at 111 stays within about ten per cent across a hundredfold change in size, "
        "while the height follows the width. In the language of the same theory this is "
        "Parseval's theorem: the total power in the line is unchanged, only its distribution "
        "in q is.", s["body"]))
    story.append(Paragraph(
        "<b>The cascade is limited by its widest stage.</b> The instrument response is set by "
        "the slits, the source size and the detector, and for any crystallite above roughly "
        "100 nm it is wider than the crystal response. That is why the curves in Figure 4 "
        "flatten at the right, and why the recovery in Table 4 stops being meaningful there: "
        "the measurement can no longer see the narrower of the two filters. Adding two "
        "Gaussian widths in quadrature is the statement that variances add when independent "
        "responses are convolved; the Lorentzian part of a pseudo-Voigt adds linearly "
        "instead, which is why the quadrature correction in Table 4 is approximate and why "
        "the residuals in Table 5 grow at the smallest sizes.", s["body"]))

    story.append(Paragraph("5.5 The 1/cos(theta) is a change of variable", s["h2"]))
    story.append(Paragraph(
        "The broadening happens in q, but the scan is recorded in 2theta. The two are related "
        "by q = 4 pi sin(theta)/lambda, so", s["body"]))
    story.append(Paragraph(
        "dq/d(2theta) = (2 pi / lambda) cos(theta),&nbsp;&nbsp;&nbsp;&nbsp;(4)", s["eq"]))
    story.append(Paragraph(
        "and a fixed width in q appears in the scan as", s["body"]))
    story.append(Paragraph(
        "Delta(2theta) = Delta(q) / |dq/d(2theta)| = K lambda / (D cos theta)."
        "&nbsp;&nbsp;&nbsp;&nbsp;(5)", s["eq"]))
    story.append(Paragraph(
        "The 1/cos(theta) is a Jacobian: the change of variable between the frequency axis of "
        "the spectrum and the goniometer angle on which it is displayed. At high angle a "
        "degree of 2theta spans fewer reciprocal-space units, so the same spectral width looks "
        "wider on the chart. The same variable change explains why the K-alpha doublet "
        "separates more at high angle: the 0.072 deg separation at 28 deg grows to 0.275 deg "
        "at 88 deg in the simulator's own scans. This is why a size measured from one "
        "low-angle line and "
        "one high-angle line should agree once equation (5) is applied, and Table 5 is that "
        "check.", s["body"]))

    story.append(Paragraph("5.6 Sampling, and why the scan step matters", s["h2"]))
    story.append(Paragraph(
        "The detector samples the profile at the step size of the scan. A peak measured with "
        "too few points per width is undersampled in exactly the sense of the sampling "
        "theorem: its height and its width become functions of where the samples happen to "
        "fall, and a fit to three points does not recover the continuous line. In the study "
        "the narrowest line is the 500 nm case, whose width is about 0.055 deg; a 0.02 deg "
        "step gives under three points per FWHM, and the measured width then depends on the "
        "step. The 0.002 deg step used for Table 4 is chosen to sample the narrowest line by "
        "about 27 points, which is why the numbers in that table can be compared with each "
        "other.", s["body"]))
    story.append(Paragraph(
        "This is the same trade-off as bandwidth against acquisition time in any measurement: "
        "sampling finer costs counts per point or time, and sampling coarser throws away the "
        "information the width carries. The size of the effect is measurable: at 500 nm the "
        "same scan taken at a 0.02 deg step reports a width 4.2 per cent larger and a size "
        "28.5 per cent smaller than the 0.002 deg scan, while at 0.002 deg the error is 0.3 "
        "per cent. A real experiment that wants a size below 10 nm must choose its step from "
        "the expected width, not from habit.",
        s["body"]))

    story.append(Paragraph("5.7 What the model predicts, and what it measures", s["h2"]))
    story.append(Paragraph(
        "None of section 5 is fitted. The curve in Figure 5 is equation (5) with K = 0.9 and "
        "the simulator's own wavelength; the widths in Table 5 come from the simulated scans. "
        f"At 20 nm the prediction for 111 is {sz[20.0, '111']['predicted_size_fwhm']:.3f} deg "
        f"against {sz[20.0, '111']['fwhm']:.3f} measured; at 400, "
        f"{sz[20.0, '400']['predicted_size_fwhm']:.3f} against "
        f"{sz[20.0, '400']['fwhm']:.3f}; at 5 nm, "
        f"{sz[5.0, '111']['predicted_size_fwhm']:.2f} against "
        f"{sz[5.0, '111']['fwhm']:.2f}. The agreement is the evidence that the model's size "
        "term is the convolution argument above and not an empirical fit, and the residuals "
        "in Table 5 say where the approximation (quadrature combination of a pseudo-Voigt) is "
        "weakest.", s["body"]))
    story.append(Paragraph(
        "Two other descriptions of the same physics are common and are worth naming, because "
        "a reader will meet them. The Warren-Averbach analysis works with the Fourier "
        "coefficients of the line profile directly, which is the most literal form of section "
        "5.1 and separates size from strain by their different order dependence [2]. It "
        "exists because a single breadth cannot do that on its own: the breadth gives a mean "
        "dimension, and the shape of the size distribution appears only in the higher-order "
        "coefficients [9]. The "
        "Williamson-Hall plot uses several reflections to separate the 1/cos and tan terms; "
        "the analysis code in this repository implements it as a check and returns the input "
        "size and zero strain on a size-only simulation. Neither is needed for item 3, and "
        "neither is used for the numbers in this report, but both are the same convolution "
        "argument written in a different basis.", s["body"]))

    # ------------------------------------------------------------------ 6
    story.append(Paragraph("6. Verification, uncertainty and limits", s["h1"]))
    story.append(Paragraph(
        "Every number in this report is produced by the simulator that draws the figures, and "
        "the report is gated on that. Peak positions are checked against the NIST SRM 640f "
        "certificate, every phase against its published strongest line, and the whole "
        "document rebuilds byte-identically from a fresh clone of the repository. The test "
        "suite covers the lattice geometry, the structure factor and its absences, the "
        "profile, the detector and the scan, and it includes an independent brute-force count "
        "of the symmetry orbits and a metric-tensor check of the d-spacings.", s["body"]))
    story.append(Paragraph(
        "The uncertainty in the size numbers has four parts. The counting noise is negligible "
        "here by construction: 100 000 counts at the peak give a statistical error below "
        "0.4 per cent, far below the differences being compared. The profile shape matters "
        "less than one might expect: sweeping eta from 0 to 1 changes the peak height by "
        "about a third but the measured FWHM by less than 0.1 per cent at 20 nm, because "
        "the width is read at half maximum and the mixture is normalised to unit area. The quadrature combination of "
        "the instrumental and size widths is exact only for two Gaussians; with a pseudo-Voigt "
        "the Lorentzian part adds linearly, and that is the main reason the residuals in "
        "Table 5 grow at the smallest sizes. Finally the instrument constants U, V and W are "
        "plausible defaults rather than a calibration of a real diffractometer, so the "
        "absolute widths belong to this model; the scaling laws, which are what items 2 and 3 "
        "are about, do not depend on them.", s["body"]))
    story.append(Paragraph(
        "What could change the conclusions? A different shape constant would move every "
        "recovered size by the same factor and would not change the 1/D law. A different "
        "instrument width would move the crossover between the sample-limited and "
        "instrument-limited regimes, but not the slope. A specimen with strain would broaden "
        "the lines with a tan(theta) term, which the size-only analysis would misread as a "
        "smaller crystallite at high angle; that is precisely what the Williamson-Hall check "
        "in the repository is for, and why this report uses a strain-free simulation.", s["body"]))
    story.append(Paragraph(
        "Deliberately not modelled: Rietveld refinement, anomalous dispersion, preferred "
        "orientation, K-beta residual, detector energy discrimination, thin-film absorption, "
        "axial-divergence asymmetry, amorphous background and absolute intensities. Every "
        "site shares one Debye-Waller coefficient. The Cu K-alpha wavelengths are the "
        "conventional values; no primary table was read for them. None of these affects the "
        "size argument, which rests on the width and on the convolution.", s["body"]))

    story.append(Paragraph("6.1 Uncertainty budget", s["h2"]))
    story.append(Paragraph(
        "The table collects the terms discussed above, each measured on this model rather "
        "than estimated. The two that matter for a size measurement are the scan step on a "
        "narrow line and the instrument width itself; the others are below the differences "
        "the report is asked to demonstrate.", s["body"]))
    story.append(table([
        ["Source", "Effect measured", "Where it matters"],
        ["Counting noise", "below 0.4 % on the peak height at 100 000 counts",
         "negligible here by construction"],
        ["Profile shape, eta 0 to 1", "width below 0.1 %, height about 32 %",
         "height comparisons, not widths"],
        ["Scan step, 0.02 deg at 500 nm", "width +4.2 %, recovered size -28.5 %",
         "narrow lines, large crystallites"],
        ["Quadrature subtraction", "up to 1.9 % on the width at 5 nm, 400",
         "the smallest sizes"],
        ["Instrument U, V, W", "sets the crossover near 100 nm",
         "any size above about 100 nm"],
        ["Wavelength convention", "0.0001 deg at 30 deg", "negligible"],
        ["Cell constants", "below 0.02 deg in 2theta", "positions, not widths"],
    ], [110, 180, 155], s))
    story.append(Paragraph("Table 9: the uncertainty budget. The step and eta entries were "
                           "measured by sweeping the parameter and re-running the analysis; "
                           "the quadrature entry is the largest residual in Table 5.",
                           s["caption"]))

    # ------------------------------------------------------------------ 7
    story.append(Paragraph("7. Conclusion", s["h1"]))
    story.append(Paragraph(
        "Item 1: the simulator described in section 2 reproduces the diffraction patterns of "
        "nine crystal structures and of one structure at six crystallite sizes (Figures 2 and "
        "3), and its code is Appendix A. Item 2: changing the domain size changes the width of "
        "every line as 1/D, changes the height in proportion, leaves the integrated area and "
        "the Bragg positions alone, and does so more strongly at high angle. Item 3: those "
        "four facts are the properties of one filter. A finite crystallite multiplies the "
        "lattice by a window, convolution in reciprocal space turns that window into a "
        "sinc-squared of width 2 pi / D, the instrument is a second convolution in series, and "
        "the 1/cos(theta) is the Jacobian between reciprocal space and the goniometer angle. "
        "The measurements in Table 4 and Table 5 agree with that description without fitting "
        "anything.", s["body"]))

    # ------------------------------------------------------------------ refs
    story.append(Paragraph("References", s["h1"]))
    for index, entry in enumerate(REFERENCES, start=1):
        story.append(Paragraph(f"[{index}] {entry}", s["ref"]))
    story.append(Paragraph(
        "Every entry was checked on 2026-10-22: each DOI was resolved through Crossref and "
        "each ISBN through OpenLibrary, and each work is cited for the claim it supports. The "
        "checks are recorded in report/references/AUDIT.md.", s["caption"]))

    # ------------------------------------------------------------------ B
    # ------------------------------------------------------------------ A, B, C
    code_appendix(story, s)

    story.append(Paragraph("Appendix B: constants and their provenance", s["h1"]))
    story.append(Paragraph(
        "The cell constants the report uses, with the record each came from. The full table, "
        "including confidence for every value, is data/SOURCES.md in the repository.", s["body"]))
    provenance = [["Key", "Cell (A)", "Record"]]
    for key, phase in PHASES.items():
        cell = f"a = {phase.a:.4f}" + (f", c = {phase.c:.4f}" if phase.c else "")
        provenance.append([key, cell, phase.source])
    story.append(table(provenance, [58, 92, 300], s))
    story.append(Paragraph("Table 8: cell constants and the record behind each. Where a "
                           "record is a room-temperature conventional value rather than a "
                           "certified one, data/SOURCES.md marks it provisional.", s["caption"]))
    story.append(Paragraph(
        "Instrument constants: Cu K-alpha1 1.540598 A, K-alpha2 1.544426 A (ratio 0.497), "
        "K-beta 1.392250 A; Caglioti U = 0.004, V = -0.002, W = 0.003 deg^2; eta = 0.5; scan "
        "ceiling 150 deg; Debye-Waller B = 0.5 A^2 for every site. The form factors are the "
        "Waasmaier-Kirfel parameterisation [6], tabulated once and shipped with the code.",
        s["body"]))

    story.append(Paragraph("Appendix C: reflection tables for the nine phases", s["h1"]))
    story.append(Paragraph(
        "Every reflection the model reaches below 150 deg with a non-zero structure factor, "
        "with its spacing, its angle, its multiplicity and its intensity relative to the "
        "strongest line of that phase. Generated by report/tables.py; the same table is in "
        "report/tables.md.", s["body"]))
    number = 10
    for key, phase in PHASES.items():
        rows = [row for row in reflections(phase, instrument) if row.intensity > 1e-9]
        strongest = max(row.intensity for row in rows)
        body_rows = [["hkl", "d (A)", "2theta (deg)", "m", "I/I0 (%)"]]
        for row in rows:
            if row.intensity < 0.005 * strongest:
                continue
            body_rows.append([
                "".join(str(v) for v in row.hkl), f"{row.d:.4f}", f"{row.two_theta:.3f}",
                str(row.multiplicity), f"{100 * row.intensity / strongest:.1f}",
            ])
        story.append(Paragraph(f"{phase.name} ({phase.formula}), {phase.space_group}",
                               s["h2"]))
        story.append(table(body_rows, [56, 64, 74, 40, 66], s))
        story.append(Paragraph(f"Table {number}: reflections of {phase.name} below 150 deg "
                               f"above 0.5 per cent of the strongest line.", s["caption"]))
        number += 1


    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    print(f"wrote {PDF_PATH}")


if __name__ == "__main__":
    build()
