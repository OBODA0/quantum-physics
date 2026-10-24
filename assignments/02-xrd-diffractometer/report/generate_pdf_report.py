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
     "ISBN 0-486-66317-5. Chapters 2 and 3: scattering by a finite lattice, the interference "
     "function."),
    ("B. D. Cullity and S. R. Stock, <i>Elements of X-ray Diffraction</i>, 3rd edition, "
     "Prentice Hall (2001), ISBN 0-201-61091-4. Chapters 4 and 5: instrument broadening and "
     "crystallite-size measurement."),
    ("A. V. Oppenheim and A. S. Willsky, <i>Signals and Systems</i>, 2nd edition, "
     "Prentice Hall (1997), ISBN 0-13-814757-4. Convolution, the convolution theorem, and "
     "the frequency response of a linear system."),
    ("R. N. Bracewell, <i>The Fourier Transform and Its Applications</i>, 3rd edition, "
     "McGraw-Hill (2000), ISBN 0-07-303938-1. Transform pairs for the rectangle and the "
     "finite chain, and the scaling rule."),
    ("D. Waasmaier and A. Kirfel, <i>New analytical scattering-factor functions for free "
     "atoms and ions</i>, Acta Crystallographica <b>A51</b>, 416-431 (1995). "
     "doi:10.1107/S0108767394013292"),
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
        "body": ParagraphStyle("Body", parent=base["Normal"], fontName="Helvetica", fontSize=9,
                               leading=12.4, spaceAfter=6),
        "small": ParagraphStyle("Small", parent=base["Normal"], fontName="Helvetica", fontSize=8.2,
                                leading=10.8, spaceAfter=4),
        "caption": ParagraphStyle("Caption", parent=base["Normal"], fontName="Helvetica-Oblique",
                                  fontSize=8.2, leading=10.8, textColor=colors.HexColor("#333333"),
                                  spaceAfter=10),
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
def build() -> None:
    s = styles()
    numbers = quoted_numbers()
    sz = {(row["size_nm"], row["hkl"]): row for row in size_rows()}
    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=letter, leftMargin=54, rightMargin=54,
                            topMargin=54, bottomMargin=54,
                            title="Assignment 2: X-ray Powder Diffraction Simulation",
                            author="Nanotechnology & Quantum Physics - Assignment 2")
    story = []
    story.append(Paragraph("Assignment 2: X-ray Powder Diffraction - instrument simulation, "
                           "crystallite size, and the signals view", s["title"]))
    story.append(Paragraph("<b>Course:</b> Nanotechnology &amp; Quantum Physics &nbsp;|&nbsp; "
                           "<b>Topic:</b> XRD instrument simulation, domain size, Fourier "
                           "description of broadening", s["subtitle"]))
    story.append(Paragraph("<b>Students:</b> Mohamed Oboda (2111011090) &nbsp;|&nbsp; "
                           "Mert SOLMAZ (2311011039)", s["subtitle"]))
    story.append(Paragraph("<b>Built with:</b> Prime Agent (the AI assistant used in this "
                           "session); every line of the simulator is in Appendix A.", s["subtitle"]))
    story.append(table([
        ["Item", "What it is"],
        ["Simulator", "Cu K-alpha tube, divergence and Soller slits, flat specimen on a "
                      "theta/2theta goniometer, receiving slit, optional monochromator, detector"],
        ["Phases", "Si, Al, Cu, alpha-Fe, NaCl, MgO, ZnO, TiO2 rutile, TiO2 anatase"],
        ["Physics", "Bragg's law, structure factor with Waasmaier-Kirfel form factors [6], "
                    "multiplicities, Lorentz-polarisation, Debye-Waller, K-alpha doublet, "
                    "Caglioti resolution, Scherrer broadening, Poisson counts"],
        ["Repository", REPO_URL],
    ], [80, 365], s))

    # ------------------------------------------------------------------ item 1
    story.append(Paragraph("1. The design, and screenshots of it working (25%)", s["h1"]))
    story.append(Paragraph(
        "The simulator models a Bragg-Brentano powder diffractometer (Figure 1). A copper tube "
        "supplies the K-alpha doublet at 1.540598 and 1.544426 angstrom; a divergence slit and "
        "Soller slits define the beam; the flat specimen sits on a theta/2theta goniometer; a "
        "receiving slit and an optional monochromator sit in front of the detector. The "
        "measured variable is 2theta and the specimen sits at theta, so a reflection appears "
        "where 2 d sin(theta) = lambda.", s["body"]))
    story.append(figure("instrument.png"))
    story.append(Paragraph("Figure 1: the chain the simulator models. Each box is a module of "
                           "the code in Appendix A.", s["caption"]))

    story.append(Paragraph(
        "For every reflection the simulator computes a relative intensity |F|^2 m LP, where m "
        "is the powder multiplicity and LP the Lorentz-polarisation factor, then draws the "
        "line with a pseudo-Voigt profile whose width follows the Caglioti form. Counts are "
        "Poisson draws around the expected mean, so the output has the grain of a real scan. "
        "Because the absolute prefactor of a Bragg-Brentano scan is constant across "
        "reflections, intensities are relative, as on a real instrument.", s["body"]))

    story.append(Paragraph("1.1 Varying crystal structure", s["h2"]))
    story.append(Paragraph(
        "Figure 2 shows the simulator run on nine phases under one set of instrument "
        "settings. The differences are the crystallography, not the settings: an FCC metal "
        "has few strong lines and no 100; a BCC metal loses 100 and 111; silicon, with its "
        "diamond basis, loses 222 as well; rock salt has a weak 111 because the sodium and "
        "chlorine form factors nearly cancel; wurtzite splits what cubic symmetry would have "
        "degenerate; and the two titania polymorphs give different patterns from the same "
        "formula.", s["body"]))
    story.append(figure("phase_panel.png"))
    story.append(Paragraph("Figure 2: simulated patterns of nine phases, 20-90 deg, Cu K-alpha, "
                           "20 000 counts at the strongest line, no counting noise. The labels are "
                           "the reflections the model predicts.", s["caption"]))

    rows = [["Key", "Phase", "Space group", "Cell (A)", "Strongest line"]]
    instrument = Instrument()
    for key, phase in PHASES.items():
        lines = [row for row in reflections(phase, instrument) if row.intensity > 1e-9]
        best = max(lines, key=lambda row: row.intensity)
        cell = f"a = {phase.a:.4f}" + (f", c = {phase.c:.4f}" if phase.c else "")
        rows.append([key, f"{phase.name} ({phase.formula})", phase.space_group, cell,
                     "".join(str(v) for v in best.hkl) + f" at {best.two_theta:.2f} deg"])
    story.append(table(rows, [58, 92, 80, 95, 120], s))
    story.append(Paragraph("Table 1: the nine phases. The last column is the line the model "
                           "predicts; cell constants and their provenance are in "
                           "data/SOURCES.md, and every row is checked against its published "
                           "strongest reflection in the test suite.", s["caption"]))

    story.append(Paragraph("1.2 Varying the size of the crystalline unit", s["h2"]))
    story.append(Paragraph(
        "Figure 3 is the same phase, the same reflection and the same instrument, with only "
        "the crystallite size changed. The peak stays at 28.441 deg; its width grows and its "
        "height falls as the size shrinks. The right panel normalises each curve to its own "
        "maximum, which isolates the width from the height.", s["body"]))
    story.append(figure("size_series.png"))
    story.append(Paragraph("Figure 3: silicon 111 at 5, 10, 25, 50, 100 and 500 nm. Left: "
                           "counts as measured. Right: each curve normalised to its own peak. "
                           "Cu K-alpha1 only, so the doublet does not confuse the width.",
                           s["caption"]))

    # ------------------------------------------------------------------ item 2
    story.append(Paragraph("2. What happens to the data when the domain size changes (25%)",
                           s["h1"]))
    story.append(Paragraph(
        "Table 2 is the measurement behind this item: silicon, Cu K-alpha1, a 0.002 deg step, "
        "100 000 counts at the strongest line and no counting noise, so that everything in the "
        "table is the size and nothing else.", s["body"]))
    story.append(table(size_table_rows(), [42, 62, 62, 62, 70, 76, 62], s))
    story.append(Paragraph("Table 2: size study. The Scherrer column subtracts the instrument "
                           "width in quadrature and applies D = K lambda / (beta cos theta) with "
                           "K = 0.9 [1], [3]. The area window is four FWHM wide, so at the smallest "
                           "sizes it overlaps the neighbouring reflections and the area reads low.",
                           s["caption"]))

    story.append(Paragraph("2.1 Four things change, one thing does not", s["h2"]))
    story.append(Paragraph(
        "<b>Position does not move.</b> 111 stays at 28.441 deg for every size in Table 2: "
        "Bragg's law fixes the angle from the cell, and the cell does not change with the "
        "crystallite size.", s["body"]))
    story.append(Paragraph(
        f"<b>Width grows as 1/D.</b> FWHM at 111 goes from {sz[500.0, '111']['fwhm']:.4f} deg at "
        f"500 nm to {sz[5.0, '111']['fwhm']:.3f} deg at 5 nm, a factor of "
        f"{sz[5.0, '111']['fwhm'] / sz[500.0, '111']['fwhm']:.0f} for a factor of 100 in size. "
        "The relation is linear in 1/D while "
        "the sample dominates: the left panel of Figure 4 is a straight line of slope -1 on "
        "log-log axes over the whole range.", s["body"]))
    story.append(Paragraph(
        f"<b>Height falls, area stays.</b> Peak height at 111 drops from "
        f"{sz[500.0, '111']['height']:.0f} counts at 500 nm to {sz[5.0, '111']['height']:.0f} "
        f"counts at 5 nm, close to the {sz[5.0, '111']['fwhm'] / sz[500.0, '111']['fwhm']:.0f}x "
        f"width factor, while the integrated area stays between {sz[5.0, '111']['area']:.0f} and "
        f"{sz[500.0, '111']['area']:.0f} counts deg across the whole range. The diffracted power "
        "of that reflection is set by "
        "the structure factor and the beam, not by how the crystal is cut up; the power is "
        "redistributed into a wider peak.", s["body"]))
    story.append(Paragraph(
        "<b>The instrument sets a floor.</b> At 500 nm the sample width (0.016 deg) is smaller "
        "than the instrument width (0.052 deg), and the measured width is the instrument's. "
        "Below roughly 100 nm the sample dominates; above it, the size can no longer be read "
        "from the width without a careful instrumental correction.", s["body"]))
    story.append(figure("size_laws.png"))
    story.append(Paragraph("Figure 4: left, measured FWHM against 1/D on log-log axes, one "
                           "line per reflection; right, peak height against D. Both curves bend "
                           "over where the instrument width takes control.", s["caption"]))

    story.append(Paragraph("2.2 The effect depends on the reflection", s["h2"]))
    story.append(Paragraph(
        f"For one crystallite, high-angle reflections are broader than low-angle ones: at 20 nm "
        f"the 111 line is {sz[20.0, '111']['fwhm']:.3f} deg and the 400 line is "
        f"{sz[20.0, '400']['fwhm']:.3f} deg (Table 2), and Figure 5 shows "
        "the same trend over 20-120 deg. The reason is the 1/cos(theta) in the Scherrer "
        "relation, and section 3 derives it as a change of variable between reciprocal space "
        "and the goniometer angle.", s["body"]))
    story.append(figure("fwhm_vs_angle.png"))
    story.append(Paragraph("Figure 5: FWHM against 2theta for 20 nm and 50 nm crystallites, "
                           "with the Scherrer curve K lambda / (D cos theta) drawn for 20 nm.",
                           s["caption"]))

    story.append(Paragraph(
        "One more consequence is practical: as the peaks widen they start to overlap. In "
        "Figure 3 the 5 nm 111 peak is wider than the 220-111 separation at low angle, so "
        "neighbouring lines merge into one envelope and a peak-fitting routine that assumes "
        "separate maxima begins to fail. That is the same statement as a resolution limit in "
        "a measurement system.", s["body"]))

    # ------------------------------------------------------------------ item 3
    story.append(Paragraph("3. Why it happens, in signals-and-systems terms (25%)", s["h1"]))
    story.append(Paragraph("3.1 The pattern is a Fourier transform", s["h2"]))
    story.append(Paragraph(
        "The amplitude scattered by a specimen is the Fourier transform of its electron "
        "density, A(q) proportional to the integral of rho(r) exp(-i q.r) dr, with "
        "q = 4 pi sin(theta) / lambda [2, ch. 2]. An infinite crystal is a lattice convolved "
        "with a unit cell, so its transform is a reciprocal lattice multiplied by the "
        "structure factor: delta functions at the Bragg points, which is the ideal line in "
        "the top panel of Figure 6.", s["body"]))
    story.append(Paragraph(
        "A real crystal is that lattice multiplied by a window w(r), equal to one inside the "
        "crystallite and zero outside. Multiplication in real space is convolution in "
        "reciprocal space [4, ch. 3], [5, ch. 2]: the amplitude is the ideal pattern "
        "convolved with W, the transform of the window, and the measured intensity carries "
        "|W|^2. For a crystal of size D the window is a rectangle and |W|^2 is a sinc-squared "
        "with its first zeros at q = 2 pi / D. The finite size of the crystal is therefore "
        "not a correction to the physics; it is a filter applied to the ideal spectrum, and "
        "its bandwidth is set by 1/D.", s["body"]))
    story.append(figure("convolution.png"))
    story.append(Paragraph("Figure 6: the same reflection at four stages. Top: an ideal, "
                           "infinite crystal. Second: a 40 nm crystallite, which convolves the "
                           "line with the transform of its own finite window. Third: the same "
                           "crystal seen through the instrument, a second convolution. Bottom: a "
                           "500 nm crystallite, where the instrument response is again the wider "
                           "of the two and therefore sets the measured width.", s["caption"]))

    story.append(Paragraph("3.2 Two LTI stages, and what follows from that", s["h2"]))
    story.append(Paragraph(
        "The chain is two linear, shift-invariant stages in series. The input is the Bragg "
        "impulse train; the crystal has impulse response h_crystal = W; the instrument has "
        "impulse response h_instrument. The output is the convolution of all three. "
        "Convolution commutes and associates, so the order of the two stages does not matter "
        "and the observed line is the ideal line blurred by both responses. Two results of "
        "linear-systems theory then explain the whole of item 2 without any extra physics.", s["body"]))
    story.append(Paragraph(
        "<b>Bandwidth.</b> A long impulse response has a narrow frequency response. A "
        "crystallite of N planes is a window of length N d, and the width of its transform "
        "scales as 1/N. Halving the crystallite doubles the width in q, which is the straight "
        "line of slope minus one in Figure 4. The reciprocal relation is the same statement as "
        "the time-bandwidth product in signals and systems: a short observation cannot resolve "
        "fine frequency structure.", s["body"]))
    story.append(Paragraph(
        "<b>Area.</b> A normalised impulse response has unit area, and convolution preserves "
        "the integral. The area under a reflection is therefore fixed by the structure factor "
        "and the beam, while its height is area divided by width. Table 2 shows exactly that: "
        "the area at 111 stays within about ten per cent across a hundredfold change in size, "
        "while the height follows the width. In the language of the same theory this is "
        "Parseval's theorem: the total power in the line is unchanged, only its distribution "
        "in q is.", s["body"]))
    story.append(Paragraph(
        "The instrument is the second filter. Its impulse response is set by the slits, the "
        "source size and the detector, and it is wider than the crystal response for any "
        "crystallite above about 100 nm. That is why the curves in Figure 4 flatten at the "
        "right: once the crystal filter is narrower than the instrument filter, the measured "
        "width stops following the size. In system terms the cascade is limited by its widest "
        "stage, just as a measurement chain is limited by its slowest element.", s["body"]))

    story.append(Paragraph("3.3 Why the broadening depends on the angle", s["h2"]))
    story.append(Paragraph(
        "The broadening happens in q, but the scan is recorded in 2theta. The two are related "
        "by q = 4 pi sin(theta) / lambda, so dq / d(2theta) = (2 pi / lambda) cos(theta). A "
        "fixed width in q therefore appears in the scan as a width", s["body"]))
    story.append(Paragraph(
        "&nbsp;&nbsp;&nbsp;&nbsp;Delta(2theta) = Delta(q) lambda / (2 pi cos theta) "
        "= K lambda / (D cos theta),", s["body"]))
    story.append(Paragraph(
        "which is the Scherrer relation with K = 0.9 [1]. The 1/cos(theta) is a Jacobian: it "
        "is the change of variable between the frequency axis of the spectrum and the "
        "goniometer angle on which it is displayed. At high angle a degree of 2theta spans "
        "fewer reciprocal-space units, so the same spectral width looks wider on the chart. "
        "The same variable change is why the K-alpha doublet separates more at high angle.",
        s["body"]))
    story.append(Paragraph(
        "The scan step is the sampling rate of that displayed spectrum. Table 2 measures a "
        "0.055 deg width at 500 nm; at a 0.02 deg step that is under three points per FWHM, "
        "and the measured width becomes sensitive to where the samples land. The 0.002 deg "
        "step used for Table 2 is chosen for that reason: to sample the narrowest line of the "
        "study rather than to chase resolution the instrument does not have.", s["body"]))

    story.append(Paragraph("3.4 Does the prediction hold?", s["h2"]))
    story.append(Paragraph(
        f"The Scherrer curve drawn in Figure 5 is not fitted: it is K lambda / (D cos theta) "
        f"with the same K and lambda the simulator uses. At 20 nm it predicts "
        f"{sz[20.0, '111']['predicted_size_fwhm']:.3f} deg for 111 and the measured width is "
        f"{sz[20.0, '111']['fwhm']:.3f} deg; at 400 it predicts "
        f"{sz[20.0, '400']['predicted_size_fwhm']:.3f} and measures "
        f"{sz[20.0, '400']['fwhm']:.3f}. At 5 nm the prediction is "
        f"{sz[5.0, '111']['predicted_size_fwhm']:.2f} deg against "
        f"{sz[5.0, '111']['fwhm']:.2f} measured. The agreement is a check that the model's "
        f"size convolution is the transform argument above and not an empirical fit.", s["body"]))

    # ------------------------------------------------------------------ close
    story.append(Paragraph("4. Verification, and what the model does not do", s["h1"]))
    story.append(Paragraph(
        "The simulator is covered by a test suite; the numbers quoted here are produced by the "
        "same code that draws the figures, and the report is gated on them. Peak positions are "
        "checked against the NIST SRM 640f certificate, every phase against its published "
        "strongest line, and the whole report rebuilds from a fresh clone byte-identically. "
        "The suite, the gates and the provenance of every constant are documented in the "
        "repository.", s["body"]))
    story.append(Paragraph(
        "Not modelled: Rietveld refinement, anomalous dispersion, preferred orientation, "
        "K-beta residual, detector energy discrimination, thin-film absorption and absolute "
        "intensities. Every site shares one Debye-Waller factor. The Cu K-alpha wavelengths "
        "are the conventional values; no primary table was read. None of these affects the "
        "size argument, which depends only on the width and the convolution.", s["body"]))

    story.append(Paragraph("References", s["h1"]))
    for index, entry in enumerate(REFERENCES, start=1):
        story.append(Paragraph(f"[{index}] {entry}", s["ref"]))
    story.append(Paragraph(
        "Every entry was checked on 2026-10-22: the DOI resolves through Crossref, the ISBNs "
        "resolve through OpenLibrary, and each work is cited for the claim it supports.",
        s["caption"]))

    code_appendix(story, s)

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    print(f"wrote {PDF_PATH}")


if __name__ == "__main__":
    build()
