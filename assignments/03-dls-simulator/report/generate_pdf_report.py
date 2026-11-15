"""Build the assignment 3 PDF report.

Five inputs, three outputs, one simulator: the design and its screenshots, what each input
does to the measured curve and the reported size, and what the analysis can and cannot
resolve. One PDF, with the code appendix inside, as PS2 requires.

    uv run python -m report.generate_pdf_report
"""

from __future__ import annotations

import pathlib

import matplotlib
import reportlab.rl_config

reportlab.rl_config.invariant = 1   # fixed timestamps and IDs: the PDF rebuilds byte-identically

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

from . import numbers_source
from .cases import (ALPHA_FIGURE, BASE, PDI_LIMIT, RI_SWEEP, SIGMA_SWEEP, SIZES_NM,
                    SOLVENTS, TEMPERATURES_C, row, run)
from .size_study import rows as size_rows
from .tables import (aggregation_rows, angle_rows, noise_rows, noisy_inversion_rows,
                     polydispersity_rows, refractive_index_rows, solvent_rows)

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
REPO_URL = "https://github.com/OBODA0/quantum-physics"
PDF_PATH = HERE / "Assignment_3_DLS_Simulator_Report.pdf"
FIG = HERE / "figures"
COVER_PDF = HERE / "cover.pdf"
COVER_PAGES = 1
REPORT_TITLE = "Assignment 3: Dynamic Light Scattering Simulator"
FOOTER_TITLE = "Nanotechnology / Quantum Physics - DLS nanoparticle sizing simulator"
LINK_COLOR = "#1155cc"

REFERENCES = [
    ("A. Einstein, <i>Ueber die von der molekularkinetischen Theorie der Waerme geforderte "
     "Bewegung von in ruhenden Fluessigkeiten suspendierten Teilchen</i>, Annalen der Physik "
     "<b>322</b>(8), 549-560 (1905). doi:10.1002/andp.19053220806"),
    ("B. J. Berne and R. Pecora, <i>Dynamic Light Scattering: With Applications to Chemistry, "
     "Biology, and Physics</i>, Dover (2000), ISBN 978-0-486-41155-2."),
    ("D. E. Koppel, <i>Analysis of macromolecular polydispersity in intensity correlation "
     "spectroscopy: the method of cumulants</i>, Journal of Chemical Physics <b>57</b>(11), "
     "4814-4820 (1972). doi:10.1063/1.1678153"),
    ("ISO 22412:2025, <i>Particle size analysis - Dynamic light scattering (DLS)</i>, 3rd "
     "edition, International Organization for Standardization (2025). BSI identifier "
     "10.3403/30461404."),
    ("R. Pecora, <i>Doppler shifts in light scattering from pure liquids and polymer "
     "solutions</i>, Journal of Chemical Physics <b>40</b>(6), 1604-1614 (1964). "
     "doi:10.1063/1.1725368"),
    ("C. F. Bohren and D. R. Huffman, <i>Absorption and Scattering of Light by Small "
     "Particles</i>, Wiley (1983), ISBN 978-0-471-05772-7."),
    ("S. W. Provencher, <i>A constrained regularization method for inverting data represented "
     "by linear algebraic or integral equations</i>, Computer Physics Communications "
     "<b>27</b>(3), 213-227 (1982). doi:10.1016/0010-4655(82)90173-4"),
    ("J. Kestin, M. Sokolov and W. A. Wakeham, <i>Viscosity of liquid water in the range -8 C "
     "to 150 C</i>, Journal of Physical and Chemical Reference Data <b>7</b>(3), 941-948 "
     "(1978). doi:10.1063/1.555581"),
    ("G. M. Hale and M. R. Querry, <i>Optical constants of water in the 200 nm to 200 um "
     "wavelength region</i>, Applied Optics <b>12</b>(3), 555-563 (1973). "
     "doi:10.1364/AO.12.000555"),
    ("W. M. Haynes (editor), <i>CRC Handbook of Chemistry and Physics</i>, 97th edition, CRC "
     "Press (2016), ISBN 978-1-4987-5428-6."),
]

REFERENCE_URLS = [
    "https://doi.org/10.1002/andp.19053220806",
    "https://openlibrary.org/isbn/0486411559",
    "https://doi.org/10.1063/1.1678153",
    "https://doi.org/10.3403/30461404",
    "https://doi.org/10.1063/1.1725368",
    "https://openlibrary.org/isbn/0471057722",
    "https://doi.org/10.1016/0010-4655(82)90173-4",
    "https://doi.org/10.1063/1.555581",
    "https://doi.org/10.1364/AO.12.000555",
    "https://openlibrary.org/isbn/1498754287",
]

DOIS = [url.replace("https://doi.org/", "") for url in REFERENCE_URLS
        if url.startswith("https://doi.org/")]


def _register_fonts() -> None:
    ttf = pathlib.Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", str(ttf / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(ttf / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Oblique", str(ttf / "DejaVuSans-Oblique.ttf")))
    pdfmetrics.registerFont(
        TTFont("DejaVuSans-BoldOblique", str(ttf / "DejaVuSans-BoldOblique.ttf"))
    )
    pdfmetrics.registerFontFamily(
        "DejaVuSans",
        normal="DejaVuSans",
        bold="DejaVuSans-Bold",
        italic="DejaVuSans-Oblique",
        boldItalic="DejaVuSans-BoldOblique",
    )


def styles() -> dict:
    _register_fonts()
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("DocTitle", parent=base["Normal"], fontName="DejaVuSans-Bold",
                                fontSize=19, leading=23, textColor=colors.HexColor("#1a2a40"),
                                spaceAfter=6),
        "subtitle": ParagraphStyle("DocSubtitle", parent=base["Normal"], fontName="DejaVuSans",
                                   fontSize=9.2, leading=14, textColor=colors.HexColor("#4a5568"),
                                   spaceAfter=5),
        "h1": ParagraphStyle("H1", parent=base["Normal"], fontName="DejaVuSans-Bold", fontSize=13.5,
                             leading=17, textColor=colors.HexColor("#1b365d"),
                             spaceBefore=14, spaceAfter=7, keepWithNext=True),
        "h2": ParagraphStyle("H2", parent=base["Normal"], fontName="DejaVuSans-Bold", fontSize=10.8,
                             leading=14, textColor=colors.HexColor("#2c5282"),
                             spaceBefore=10, spaceAfter=5, keepWithNext=True),
        "h3": ParagraphStyle("H3", parent=base["Normal"], fontName="DejaVuSans-BoldOblique",
                             fontSize=9.6, leading=12.5, textColor=colors.HexColor("#2c5282"),
                             spaceBefore=8, spaceAfter=3, keepWithNext=True),
        "body": ParagraphStyle("Body", parent=base["Normal"], fontName="DejaVuSans", fontSize=8.9,
                               leading=13.0, textColor=colors.HexColor("#2d3748"), spaceAfter=6),
        "small": ParagraphStyle("Small", parent=base["Normal"], fontName="DejaVuSans", fontSize=8.0,
                                leading=10.6, textColor=colors.HexColor("#2d3748"), spaceAfter=4),
        "caption": ParagraphStyle("Caption", parent=base["Normal"], fontName="DejaVuSans-Oblique",
                                  fontSize=8.3, leading=11.2, textColor=colors.HexColor("#4a5568"),
                                  alignment=1, spaceAfter=10),
        "quote": ParagraphStyle("Quote", parent=base["Normal"], fontName="DejaVuSans-Oblique",
                                fontSize=8.5, leading=12.2,
                                textColor=colors.HexColor("#1f2937"), leftIndent=12,
                                rightIndent=10, spaceAfter=3),
        "eq": ParagraphStyle("Eq", parent=base["Normal"], fontName="DejaVuSans", fontSize=9.6,
                             leading=13.5, alignment=1,
                             textColor=colors.HexColor("#1f2937")),
        "eqnum": ParagraphStyle("EqNum", parent=base["Normal"], fontName="DejaVuSans", fontSize=8.5,
                                leading=12, textColor=colors.HexColor("#4a5568")),
        "ref": ParagraphStyle("Ref", parent=base["Normal"], fontName="DejaVuSans", fontSize=8.3,
                              leading=12.2, textColor=colors.HexColor("#2d3748"),
                              leftIndent=20, firstLineIndent=-20, spaceAfter=5),
        "code": ParagraphStyle("Code", parent=base["Normal"], fontName="Courier", fontSize=6.4,
                               leading=7.9),
    }


class NumberedCanvas(canvas.Canvas):
    """Canvas that stamps the running footer once the total page count is known."""

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_states = []

    def showPage(self):
        self._saved_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_states) + COVER_PAGES
        for state in self._saved_states:
            self.__dict__.update(state)
            self._draw_footer(total)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_footer(self, total: int) -> None:
        self.saveState()
        self.setFont("DejaVuSans", 8)
        self.setFillColor(colors.HexColor("#555555"))
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, REPORT_TITLE)
        self.drawString(54, 34, FOOTER_TITLE)
        self.drawRightString(8.5 * 72 - 54, 34,
                             f"Page {self._pageNumber + COVER_PAGES} of {total}")
        self.setStrokeColor(colors.HexColor("#dddddd"))
        self.setLineWidth(0.6)
        if self._pageNumber > 1:
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        self.line(54, 46, 8.5 * 72 - 54, 46)
        self.restoreState()


def _prepend_cover(report_path: pathlib.Path, cover_path: pathlib.Path, total: int) -> None:
    """Put the approved cover page in front of the report, carrying the report's footer."""
    import io

    from pypdf import PdfReader, PdfWriter

    buffer = io.BytesIO()
    overlay = canvas.Canvas(buffer, pagesize=letter)
    overlay.setFont("DejaVuSans", 8)
    overlay.setFillColor(colors.HexColor("#555555"))
    overlay.drawString(54, 34, FOOTER_TITLE)
    overlay.drawRightString(8.5 * 72 - 54, 34, f"Page 1 of {total}")
    overlay.setStrokeColor(colors.HexColor("#dddddd"))
    overlay.setLineWidth(0.6)
    overlay.line(54, 46, 8.5 * 72 - 54, 46)
    overlay.showPage()
    overlay.save()
    buffer.seek(0)

    writer = PdfWriter(clone_from=str(cover_path))
    writer.pages[0].merge_page(PdfReader(buffer).pages[0])
    writer.append(str(report_path))
    temporary = report_path.with_suffix(".with-cover.pdf")
    with open(temporary, "wb") as handle:
        writer.write(handle)
    temporary.replace(report_path)


def figure(name: str, width_mm: float = 165) -> Image:
    path = FIG / name
    image = Image(str(path))
    scale = (width_mm * mm) / image.imageWidth
    image.drawWidth = width_mm * mm
    image.drawHeight = image.imageHeight * scale
    return image


def table(rows, widths, s, header: bool = True):
    data = [[Paragraph(str(cell), s["small"]) for cell in row_] for row_ in rows]
    grid = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    grid.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#999999")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef1f6") if header else colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return grid


def equation(line: str, number: str, s: dict) -> Table:
    """A centred display equation with its number at the right margin."""
    grid = Table([[Paragraph(line, s["eq"]), Paragraph(number, s["eqnum"])]],
                 colWidths=[452, 45])
    grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return grid


def linked_reference(text: str, url: str) -> str:
    """Make the DOI, the ISBN, or (failing both) the title of a reference clickable."""
    if not url:
        return text
    link = '<link href="{url}" color="{colour}">{{token}}</link>'.format(url=url,
                                                                        colour=LINK_COLOR)
    match = __import__("re").search(r"doi:10\.\d{4,9}/\S+", text)
    if match:
        token = match.group(0).rstrip(".,;")
        return text.replace(token, link.format(token=token), 1)
    match = __import__("re").search(r"ISBN [0-9][0-9-]*[0-9X]", text)
    if match:
        token = match.group(0)
        return text.replace(token, link.format(token=token), 1)
    return text


def _wrap_code(text: str, width: int = 100) -> str:
    """Break over-long source lines at whitespace boundaries, preserving indentation."""
    lines = []
    for raw in text.splitlines():
        if len(raw) <= width:
            lines.append(raw)
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        prefix = " " * (indent + 4)
        line = raw
        while len(line) > width:
            cut = line.rfind(" ", indent + 1, width + 1)
            if cut <= indent:
                cut = width
            lines.append(line[:cut].rstrip())
            line = prefix + line[cut:].lstrip()
        lines.append(line)
    return "\n".join(lines)


def _cover_and_front(story, s, n) -> None:
    pass


def section_intro(story, s, n) -> None:
    story.append(Paragraph("Assignment 3: a Dynamic Light Scattering simulator, and what "
                           "it measures", s["title"]))
    story.append(Paragraph("<b>Course:</b> Nanotechnology &amp; Quantum Physics &nbsp;|&nbsp; "
                           "<b>Topic:</b> dynamic light scattering, photon correlation "
                           "spectroscopy, nanoparticle sizing", s["subtitle"]))
    story.append(Paragraph("<b>Students:</b> Mohamed Oboda (2111011090) &nbsp;|&nbsp; "
                           "Mert SOLMAZ (2311011039)", s["subtitle"]))

    meta = [
        [Paragraph("<b>Simulator</b>", s["body"]),
         Paragraph("He-Ne laser at 632.8 nm, one cuvette, one detector at 173 deg, a "
                   "correlator model, cumulant analysis and a regularised inversion", s["body"])],
        [Paragraph("<b>Inputs</b>", s["body"]),
         Paragraph("solvent (water, ethanol), aggregation parameter, particle refractive "
                   "index, particle size, size-distribution width, temperature", s["body"])],
        [Paragraph("<b>Outputs</b>", s["body"]),
         Paragraph("autocorrelation on a log lag axis with the photon trace, number and "
                   "intensity size distributions, PDI and the monodisperse verdict", s["body"])],
        [Paragraph("<b>Built with</b>", s["body"]),
         Paragraph("Antigravity and Prime Agent (AI coding assistants); the complete "
                   "simulator and the figure scripts are in Appendix A", s["body"])],
        [Paragraph("<b>Repository</b>", s["body"]),
         Paragraph('<link href="{url}" color="{c}">{url}</link> - the code, the figures and '
                   "the checks behind every number in this report".format(url=REPO_URL,
                                                                          c=LINK_COLOR),
                   s["body"])],
    ]
    meta_table = Table(meta, colWidths=[110, 394])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Abstract", s["h1"]))
    story.append(Paragraph(
        "A dynamic light scattering (DLS) instrument was built as a Python model, and this "
        "report measures what it does. The model takes the five inputs named on the class "
        "page - solvent, aggregation parameter, particle refractive index, particle size and "
        "temperature - plus the width of the size distribution, which the outputs cannot be "
        "produced without, and produces the three outputs named "
        "there: an intensity autocorrelation on a logarithmic lag axis with the photon "
        "trace, number and intensity size distributions on a logarithmic size axis, and a "
        "polydispersity index with a monodisperse verdict. The physics is Stokes-Einstein "
        "diffusion of Brownian spheres, the Siegert relation between field and intensity "
        "correlation, Rayleigh-Gans scattering with a "
        "<i>d</i><super>6</super> intensity weight, the ISO 22412 cumulant analysis for the "
        "PDI, and a regularised non-negative inversion of the correlation curve to recover a "
        "distribution. Measured against its own inputs over 50x in diameter, the simulator "
        "reproduces the scaling the class page draws by hand: the decay time of "
        "<i>g</i><sub>2</sub>(&#964;) is proportional to the diameter ("
        f"{n['size10_tau_ms']} ms at 10 nm, {n['size500_tau_ms']} ms at 500 nm, a "
        f"{n['size_tau_ratio']}x change for a 50x change in size), a wider distribution bends "
        "the semilog decay and raises the PDI as 2(&#963;/<i>d</i>)"
        "<super>2</super>, and a second mode of clusters at 5.5 <i>d</i><sub>0</sub> leaves a "
        "slow tail in the correlation. The cumulant z-average comes back within 4 % of the "
        f"input diameter and the inversion mode within 6 % on noiseless data; with 1 % "
        f"correlation noise the same inversion reads {n['inv_noisy_min_error']} % low, and a "
        "2 % distribution then reports a PDI anywhere between "
        f"{n['pdi_noise_1pct_min']} and {n['pdi_noise_1pct_max']} depending only on the noise "
        "seed. Those limits are the useful part of the result: they say which quantity a "
        "DLS number can be trusted for.", s["body"]))

    story.append(Paragraph("The answer in one paragraph", s["h1"]))
    story.append(Paragraph(
        "Build a DLS instrument as a forward model of Brownian motion, then invert the "
        "correlation the way an instrument does, and every input the class page lists "
        "produces exactly one measurable signature. Size moves the decay time of "
        "<i>g</i><sub>2</sub>&#8722;1 in proportion to the diameter and leaves the shape "
        "alone; polydispersity changes the shape of the semilog decay and appears in the PDI "
        "as 2(&#963;/<i>d</i>)<super>2</super>; aggregation adds a second, slower mode that "
        "pushes the PDI past 0.2 while the primary mode stays where it was; solvent and "
        "temperature move the decay time through viscosity and leave the inferred diameter "
        "unchanged; and the particle refractive index moves the count rate by more than two "
        "decades without moving any size at all. The simulator reproduces all five, and the "
        "numbers in this report are the measured magnitudes of those five statements, not "
        "assertions about them.", s["body"]))


def section_one(story, s, n) -> None:
    story.append(Paragraph("1. What was asked", s["h1"]))
    story.append(Paragraph(
        "There is no Canvas item for assignment 3 yet. The only brief is the in-class "
        "debrief of 12 November 2026, transcribed from the notebook page marked "
        "<i>W7 L2 12/10</i> into <font face=\"Courier\">docs/brief_intake.md</font>. It is "
        "reproduced here verbatim, because everything in this report is written against "
        "these words and nothing else.", s["body"]))

    quote = [
        "1) DLS : Dynamic Light Scattering",
        "- to detect the size of nano particles",
        "",
        "Zeta potential",
        "- measures the surface charge of nano particles",
        "- those particles experience \"thermal motion\" -&gt; Brownian motion",
        "",
        "[diagram] Laser source -&gt; cuvette (sample containing particles in a solvent) "
        "-&gt; detector at 178 deg",
        "",
        "[plot] photon counts vs t -&gt; auto-correlation: if particle larger -&gt; slower; "
        "if particle smaller -&gt; faster",
        "",
        "[plot] Number/Intensity vs size -&gt; size distribution -&gt; PDI; if PDI &lt; 0.2",
        "",
        "Simulation task(s): design a DLS simulator",
        "",
        "Inputs:",
        "- select solvent (water, ethanol)",
        "- aggregation parameters",
        "- refractive index of the particle",
        "- size of the particle",
        "- temperature",
        "",
        "Outputs:",
        "- auto correlation function (x axis log), include photon count/t",
        "- size distribution [Number, Intensity]",
        "- PDI",
    ]
    block = Table([[Paragraph("<br/>".join(q if q else "&nbsp;" for q in quote), s["quote"])]],
                  colWidths=[500])
    block.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(block)
    story.append(Paragraph("The class page, transcribed. The page is a photograph of a "
                           "notebook, so five readings are uncertain; they are listed in "
                           "Table 1 with the reading this report uses and why.", s["caption"]))

    story.append(Paragraph("1.1 The readings that are not certain", s["h2"]))
    rows = [
        ["item", "transcription", "status and the reading used here"],
        ["detector angle", "178 deg",
         "uncertain: 173 or 179 is equally readable. Commercial backscatter instruments use "
         "173 deg. <b>This report fixes 173 deg everywhere</b> and states it in every figure; "
         "the difference is quantified in section 5.6."],
        ["autocorrelation x axis", "x axis log",
         "uncertain: could read <i>size axis log</i>. In DLS the correlation axis is delay "
         "time, normally log-spaced, which is the physical reading. Used: log lag time."],
        ["photon trace", "include photon count/t",
         "uncertain print. The page draws photon counts against time, so the trace is shown "
         "beside the correlation (Figure 2a)."],
        ["PDI threshold", "if PDI &lt; 0.2",
         "transcribed as written, and used as the criterion. It is the classroom limit, not "
         "a value read in the standard."],
        ["zeta potential", "separate bullet",
         "listed as a concept (surface charge), not as a simulator output. Not built. It is "
         "not modelled by a DLS size measurement and the page does not ask for it as an "
         "output."],
    ]
    story.append(table(rows, [72, 96, 336], s))
    story.append(Paragraph("Table 1: the five uncertain readings on the page, and the "
                           "reading this report commits to. The angle is the only one that "
                           "changes a computed number.", s["caption"]))

    story.append(Paragraph("1.2 What is in the brief, and what is inferred", s["h2"]))
    story.append(Paragraph(
        "The debrief asks for a simulator, names five inputs and three outputs, and sketches "
        "the two comparison plots (smaller against larger; number against intensity). It "
        "does not say how the work is to be submitted. Two submission requirements are "
        "<b>inferred from assignments 1 and 2</b> of this course, not from the debrief: "
        "(R4) screenshots of the simulator running, and the complete code as an appendix; "
        "(R5) an explanation of what the outputs mean. Both are treated as probable and are "
        "satisfied here - sections 3 to 5 and Appendix A - but they are labelled as "
        "inference wherever they shape the document, and <font face=\"Courier\">TASK.md</font> "
        "lists them separately from the five inputs and three outputs, which are the "
        "brief's own words.", s["body"]))
    story.append(Paragraph(
        "One input is in the simulator but not on the page: the width and shape of the size "
        "distribution. It is a derived requirement rather than an invented one. The page asks "
        "for a size <i>and</i> an intensity distribution and a PDI; none of the three exists "
        "for a sample described only by a single diameter, because a single diameter has "
        "PDI = 0 and a delta-function distribution. The width is therefore treated as an "
        "input, and it is one of the two variables in the polydispersity study of section "
        "5.2. It is listed in <font face=\"Courier\">TASK.md</font> under the inferences, not "
        "under the page's five inputs.", s["body"]))
    story.append(Paragraph(
        "One constraint does come from the course and not from this assignment. Problem "
        "statement PS1 states that a hallucinated or irrelevant reference scores zero for "
        "the whole assignment, and PS2 requires one PDF with figures, tables, references and "
        "the code appendix inside it. The reference list is therefore exactly the ten entries "
        "audited in <font face=\"Courier\">docs/research/reference_audit.md</font>, each one "
        "resolved through Crossref, the DOI registry, OpenLibrary or the BSI resolver, and "
        "each one used only for the claim its audit row says it can carry.", s["body"]))

    story.append(Paragraph("1.3 What changes when the digital brief arrives", s["h2"]))
    story.append(Paragraph(
        "The debrief is expected to be followed by a digital version on Canvas. The report "
        "is built so that the brief can be reconciled without rebuilding the simulator. "
        "Section 6.5 lists the specific places that would change: if the digital brief names "
        "178 deg, one constant changes and Table 10 gives the size shift; if it asks for zeta "
        "potential, that is a different instrument (electrophoretic light scattering) and is "
        "not in this model; if it names further graded items, section 7 states which of them "
        "these measurements already cover.", s["body"]))


def section_two(story, s, n) -> None:
    story.append(Paragraph("2. The instrument and the physics model", s["h1"]))
    story.append(Paragraph(
        "The model is an instrument, not a formula: a light source, a sample, a detector at "
        "a known angle, and a correlator that turns photon arrivals into a correlation "
        "function. Figure 1 shows the chain and names the quantity that each stage produces. "
        "Every number in this report comes from that chain, so the assumptions that matter "
        "are the ones that fix the two conversion factors between what the bench measures and "
        "what the software reports: the scattering vector <i>q</i>, which converts a decay "
        "rate into a diffusion coefficient, and the scattering weight, which converts a "
        "number distribution into an intensity distribution.", s["body"]))
    story.append(KeepTogether([figure("fig_chain.png", 168),
                               Paragraph("Figure 1: the measurement chain. (a) A He-Ne laser "
                                         "illuminates a 10 mm cuvette; the detector sits at "
                                         "173 deg to the incident beam, behind a beam stop "
                                         "that removes the transmitted light. (b) The "
                                         "correlator turns the photon-count trace into "
                                         "g2(&#964;)&#8722;1, and the two analysis routes - "
                                         "cumulant moments and a regularised inversion - "
                                         "produce the reported numbers.", s["caption"])]))

    story.append(Paragraph("2.1 The scattering vector", s["h2"]))
    story.append(Paragraph(
        "The detector sees the sample at an angle &#952;, so the interference between light "
        "scattered from two points a distance <i>r</i> apart depends on the projection of "
        "<i>r</i> onto the difference between the incident and scattered wavevectors. That "
        "difference has magnitude", s["body"]))
    story.append(equation("q = (4&#960; <i>n</i><sub>s</sub> / &#955;<sub>0</sub>) "
                          "&#183; sin(&#952;/2)", "(1)", s))
    story.append(Paragraph(
        "where <i>n</i><sub>s</sub> is the solvent refractive index and "
        "&#955;<sub>0</sub> the vacuum wavelength. Equation (1) is geometry: it follows from "
        "the definition of the scattering vector in the standard treatment [2], and it is "
        "not a result of the 1964 Doppler paper [5], which supplies the physical picture "
        "(scattering from a moving particle is Doppler-shifted) rather than this "
        "trigonometric relation. At 632.8 nm in water at 25 C (<i>n</i><sub>s</sub> = "
        "1.3312) with the detector at 173 deg the model uses "
        f"<i>q</i> = {n['base_q_nm_inv']} nm<super>&#8722;1</super>.", s["body"]))
    story.append(Paragraph(
        "The angle is a choice in this report, because the class page's 178 deg is a "
        "photograph of handwriting and commercial backscatter instruments sit at 173 deg. "
        "<b>Every figure and table here uses 173 deg.</b> Section 5.6 measures what the choice "
        "is worth: 178 deg raises <i>q</i> by 0.17 %, which moves every reported diameter by "
        f"{n['angle_scale_178']} % if the analysis assumes the wrong angle. That is far below "
        "every other uncertainty in this report, which is why the choice can be made once and "
        "stated, instead of being carried through the analysis.", s["body"]))

    story.append(Paragraph("2.2 Brownian motion and the Stokes-Einstein relation", s["h2"]))
    story.append(Paragraph(
        "A particle suspended in a liquid is struck unevenly by solvent molecules, so it "
        "performs a random walk. Einstein's 1905 paper [1] relates the mean-square "
        "displacement to the diffusion coefficient, and for a sphere of hydrodynamic diameter "
        "<i>d</i> in a liquid of viscosity &#951; that coefficient is", s["body"]))
    story.append(equation("<i>D</i> = <i>k</i><sub>B</sub><i>T</i> / (3&#960;&#951;<i>d</i>)",
                          "(2)", s))
    story.append(Paragraph(
        "with <i>k</i><sub>B</sub> the Boltzmann constant (exact, 1.380649&#215;10"
        "<super>&#8722;23</super> J/K) and <i>T</i> the absolute temperature. Equation (2) "
        "is the whole reason a DLS measurement is a size measurement: the fluctuation rate "
        "depends on how fast the particle diffuses, and the diffusion coefficient depends on "
        "how big it is. Small particles wander quickly, so their scattering pattern "
        "decorrelates quickly.", s["body"]))
    story.append(Paragraph(
        "The decay rate of the field correlation is set by how far a particle moves in a "
        "time comparable with 1/<i>q</i>:", s["body"]))
    story.append(equation("&#915; = <i>D q</i><super>2</super>", "(3)", s))
    story.append(Paragraph(
        "For 100 nm polystyrene in water at 25 C, <i>D</i> = 4.76 "
        "&#181;m<super>2</super>/s and &#915; = 3315 s<super>&#8722;1</super>, a decay time "
        "of 0.30 ms. That value is the one the simulator reports and the one the sensitivity "
        "of a real instrument is judged against: a correlator has to resolve microseconds to "
        "see a 100 nm particle and milliseconds to see a 1 &#181;m one.", s["body"]))

    story.append(Paragraph("2.3 The correlation functions", s["h2"]))
    story.append(Paragraph(
        "The detector counts photons. The count rate fluctuates because the interference "
        "pattern of the scattered light (the speckle pattern) changes as the particles move. "
        "The correlator multiplies the signal by a delayed copy of itself and averages:", s["body"]))
    story.append(equation("<i>g</i><sub>1</sub>(&#964;) = &#931;<sub>i</sub> "
                          "<i>w</i><sub>i</sub> exp(&#8722;&#915;<sub>i</sub>&#964;)", "(4)", s))
    story.append(equation("<i>g</i><sub>2</sub>(&#964;) &#8722; 1 = &#946; |<i>g</i><sub>1</sub>"
                          "(&#964;)|<super>2</super>", "(5)", s))
    story.append(Paragraph(
        "Equation (4) is the field correlation for a mixture of decay rates with intensity "
        "weights <i>w</i><sub>i</sub>; equation (5) is the Siegert relation, which holds for "
        "a Gaussian field [2]. The factor &#946; (the coherence factor, 0.85 in this model) "
        "is not physics: it measures how much of the detected light is coherent with respect "
        "to the detector area and the collection optics, and the ideal relation has "
        "&#946; = 1 [2]. It multiplies the curve and changes nothing about its shape. The "
        "lag grid is fixed at 220 points from 10<super>&#8722;7</super> s to 1 s, "
        "log-spaced; that covers particles from roughly 2 nm to 2 &#181;m at 173 deg.", s["body"]))
    story.append(Paragraph(
        "The photon trace drawn beside the correlation is not the data that gets fitted. It "
        "is a complex Ornstein-Uhlenbeck field whose intensity follows equation (5) by "
        "construction, so it shows what a correlator is fed - the same mean level, the same "
        "fluctuation rate - but its individual peaks are an illustration, not a record. This "
        "is stated again in section 6.1 because a reader who mistakes the trace for data "
        "would over-read it.", s["body"]))

    story.append(Paragraph("2.4 What scatters, and why the intensity distribution is shifted",
                           s["h2"]))
    story.append(Paragraph(
        "A particle of diameter <i>d</i> and refractive index <i>n</i><sub>p</sub> in a "
        "medium of index <i>n</i><sub>s</sub> scatters with a differential cross-section "
        "proportional to", s["body"]))
    story.append(equation("<i>I</i>(<i>d</i>) &#8733; <i>K</i> &#183; <i>d</i><super>6"
                          "</super> &#183; <i>P</i>(<i>qd</i>/2),&nbsp;&nbsp; "
                          "<i>K</i> = [(<i>m</i><super>2</super>&#8722;1)/(<i>m</i>"
                          "<super>2</super>+2)]<super>2</super>,&nbsp; <i>m</i> = "
                          "<i>n</i><sub>p</sub>/<i>n</i><sub>s</sub>", "(6)", s))
    story.append(Paragraph(
        "The <i>K</i> factor is the Lorentz-Lorenz (Clausius-Mossotti) contrast: it is the "
        "reason the particle refractive index is an input at all, and it is zero when the "
        "particle is index-matched to the solvent. The <i>d</i><super>6</super> is the "
        "Rayleigh result in the small-particle limit: scattering amplitude grows as volume, "
        "and intensity as volume squared [6]. <i>P</i> is a form factor that corrects the "
        "small-particle limit when the particle is no longer small against 1/<i>q</i>. The "
        "simulator uses", s["body"]))
    story.append(equation("<i>P</i>(<i>qd</i>/2) = 0.35 <i>P</i><sub>sphere</sub> + 0.65 "
                          "<i>P</i><sub>Guinier</sub>", "(7)", s))
    story.append(Paragraph(
        "where <i>u</i> = <i>qd</i>/2, <i>P</i><sub>sphere</sub> = [3(sin <i>u</i> "
        "&#8722; <i>u</i> cos <i>u</i>)/<i>u</i><super>3</super>]<super>2</super> is the "
        "Rayleigh-Gans-Debye sphere form factor written out in "
        "<font face=\"Courier\">dlssim/mie.py</font> and traceable to equation (6.13) of "
        "Bohren and Huffman [6], and <i>P</i><sub>Guinier</sub> = [1 + <i>u</i>"
        "<super>2</super>/5]<super>&#8722;2</super>. <b>This blend is an approximation, not a "
        "Mie solution.</b> It is correct in the limit <i>qd</i> &#8594; 0, follows the sphere "
        "form factor at intermediate angles, and avoids the unphysical zeros the pure sphere "
        "form factor produces at large <i>qd</i>. The weights 0.35 and 0.65 are stated "
        "choices, not fitted constants; a Mie calculation would be needed for absorbing or "
        "micron-scale particles. The simulator never claims an absolute cross-section, only "
        "relative weights between size classes.", s["body"]))
    story.append(Paragraph(
        "The same weights convert a number distribution into an intensity distribution:", s["body"]))
    story.append(equation("<i>p</i><sub>I</sub>(<i>d</i>) &#8733; <i>p</i><sub>N</sub>(<i>d</i>) "
                          "&#183; <i>d</i><super>6</super> <i>P</i>(<i>qd</i>/2)", "(8)", s))
    story.append(Paragraph(
        "Equation (8) is the single most important line in this report for reading the "
        "outputs. Because the weight is the sixth power of the diameter, intensity is "
        "dominated by the largest particles present. A sample whose <i>number</i> "
        "distribution is narrow and centred at 50 nm can have an <i>intensity</i> "
        "distribution centred at 72 nm (the base case of section 3), and a sample with a few "
        "percent of clusters has an intensity distribution with a second peak. That is not an "
        "artefact of the simulator; it is why DLS reports the intensity-weighted size, and "
        "why the number distribution is the harder one to obtain.", s["body"]))

    story.append(Paragraph("2.5 The solvent: viscosity and refractive index", s["h2"]))
    story.append(Paragraph(
        "Both solvent properties in equations (1) and (2) depend on temperature, so the model "
        "carries a temperature model for each. The viscosity follows the Vogel-Fulcher-"
        "Tammann (Andrade) form", s["body"]))
    story.append(equation("&#951;(<i>T</i>) = <i>A</i> exp[<i>B</i>/(<i>T</i> &#8722; "
                          "<i>T</i><sub>0</sub>)]", "(9)", s))
    story.append(Paragraph(
        "anchored to the standard 25 C value for each liquid; the parameters are listed in "
        "Appendix B. For water, <i>A</i> = 0.02414 mPa&#183;s, <i>B</i> = 570.58 K and "
        "<i>T</i><sub>0</sub> = 140 K, which reproduces the standard values summarised by "
        "Kestin, Sokolov and Wakeham [8] to 0.2 % between 0 and 60 C - those authors give "
        "correlation equations rather than a printed per-degree table, so the comparison is "
        "against the correlation, not against a table row. The refractive index is linearised "
        "about 25 C with a thermooptic coefficient: <i>n</i><sub>s</sub>(<i>T</i>) = 1.3312 "
        "&#8722; 1.0&#215;10<super>&#8722;4</super>(<i>T</i>&#8722;298.15) for water, from "
        "Hale and Querry [9]. That source tabulates <i>n</i>(&#955;) to three decimals at "
        "25 C, so the 633 nm value used here is an interpolation of the table, not a printed "
        "entry.", s["body"]))
    story.append(Paragraph(
        "The package carries four solvents. This report uses two: water and ethanol, the two "
        "named on the class page. Phosphate-buffered saline and toluene exist in the code "
        "because they are common dispersion media, but their constants are stated handbook "
        "values without a line-checked source in the audit, so they are not used for any "
        "claim here - only listed by the CLI (Figure 4).", s["body"]))

    story.append(Paragraph("2.6 The analysis: cumulants and an inversion", s["h2"]))
    story.append(Paragraph(
        "Two quantities are extracted from the same curve. The first is a moment analysis: "
        "the logarithm of the field correlation is expanded about zero lag,", s["body"]))
    story.append(equation("ln |<i>g</i><sub>1</sub>(&#964;)| = &#8722;&#915;&#772;&#964; + "
                          "(&#956;<sub>2</sub>/2)&#964;<super>2</super> &#8722; ...", "(10)", s))
    story.append(Paragraph(
        "with &#915;&#772; the mean decay rate and &#956;<sub>2</sub> its second cumulant; the "
        "method is Koppel's [3]. The polydispersity index is then defined by ISO 22412:2025 "
        "as", s["body"]))
    story.append(equation("PDI = 2&#956;<sub>2</sub> / &#915;&#772;<super>2</super>", "(11)", s))
    story.append(Paragraph(
        "The factor of two belongs to the standard's definition of the index [4], not to "
        "Koppel's paper. This attribution matters: several textbooks and many web pages write "
        "the formula as Koppel's, and the reference audit for this assignment found that the "
        "DOI commonly quoted for the formula resolves to an unrelated paper. Citing the "
        "standard for the definition and Koppel for the method is the only attribution the "
        "audit supports.", s["body"]))
    story.append(Paragraph(
        "The mean decay rate also gives the z-average diameter, which is the number an "
        "instrument quotes as \"the size\":", s["body"]))
    story.append(equation("<i>D</i><sub>z</sub> = <i>k</i><sub>B</sub><i>T q</i>"
                          "<super>2</super> / (3&#960;&#951;&#915;&#772;)", "(12)", s))
    story.append(Paragraph(
        "It is called a z-average because the intensity weighting makes it a harmonic-mean-"
        "like average: for a polydisperse sample it sits above the number-mean diameter, and "
        "it converges to the diameter only as the distribution narrows. Section 4.1 measures "
        "that bias.", s["body"]))
    story.append(Paragraph(
        "The second route is the one an instrument uses to draw a distribution: invert the "
        "correlation curve. Equation (4) is linear in the weights if the decay rates are put "
        "on a fixed grid,", s["body"]))
    story.append(equation("<i>g</i><sub>1</sub>(&#964;<sub>k</sub>) = &#931;<sub>j</sub> "
                          "<i>w</i><sub>j</sub> exp(&#8722;&#915;<sub>j</sub>&#964;<sub>k"
                          "</sub>)", "(13)", s))
    story.append(Paragraph(
        "which is solved by non-negative least squares on a 240-point logarithmic grid from "
        "1 nm to 10 &#181;m, with a second-difference penalty on the weights so that the "
        "solution is smooth rather than a comb of spikes. This is the constrained "
        "regularisation of Provencher [7] in its simplest form; the implementation is in "
        "<font face=\"Courier\">dlssim/inversion.py</font> and the penalty strength is a "
        "declared constant (10<super>&#8722;6</super> relative), not a fitted parameter. Lags "
        "where <i>g</i><sub>1</sub> has fallen below 0.01 are dropped - they carry no size "
        "information - and a constant baseline is fitted, because the square root that turns "
        "<i>g</i><sub>2</sub>&#8722;1 into <i>g</i><sub>1</sub> leaves a small offset where "
        "the amplitude is small. The recovered weights are an intensity distribution; the "
        "number distribution is that divided by <i>d</i><super>6</super><i>P</i> and reported "
        "only where the intensity exceeds 1 % of its peak, because outside that support the "
        "measurement has no sensitivity.", s["body"]))


def section_three(story, s, n) -> None:
    story.append(Paragraph("3. The simulator: inputs, outputs and screenshots", s["h1"]))
    story.append(Paragraph(
        "The simulator is a Python package, <font face=\"Courier\">dlssim</font>, with one "
        "module per physical stage. The command line and a Tk desktop interface are two "
        "front ends to the same function, <font face=\"Courier\">simulate_dls(DLSInputs(...))"
        "</font>, which returns a single immutable result object. That shape is deliberate: "
        "every figure in this report is a plot of that object, so a figure cannot show a case "
        "that a table does not.", s["body"]))
    rows = [
        ["module", "responsibility"],
        ["solvents.py", "water, ethanol, PBS, toluene: &#951;(T) by VFT, <i>n</i><sub>s</sub>(T)"],
        ["mie.py", "scattering vector <i>q</i>, Lorentz-Lorenz contrast, form factor blend"],
        ["distribution.py", "number, volume and intensity distributions; the aggregate mode"],
        ["autocorrelation.py", "Stokes-Einstein <i>D</i>, <i>g</i><sub>1</sub>, "
                              "<i>g</i><sub>2</sub>&#8722;1, the photon trace"],
        ["cumulants.py", "the second-cumulant fit, z-average, PDI, verdict"],
        ["inversion.py", "regularised non-negative inversion to a size distribution"],
        ["simulator.py", "the input and output dataclasses and the pipeline"],
        ["plot.py", "the four-panel dashboard and the whiteboard comparison figure"],
        ["cli.py, gui.py", "the command line and the Tk interface"],
    ]
    story.append(table(rows, [90, 414], s))
    story.append(Paragraph("Table 2: the module map. Appendix A carries every file in this "
                           "table, plus the report scripts that produced the figures, the "
                           "tables and the numbers quoted in the text.", s["caption"]))

    story.append(Paragraph("3.1 The interface, running", s["h2"]))
    story.append(Paragraph(
        "Figure 2 is the desktop interface, captured from the program itself. Its controls "
        "are the five inputs named on the class page (solvent, particle refractive index, "
        "size, aggregation, temperature) plus the width and shape of the distribution, with "
        "the PDI readout on the left, and "
        "the three outputs on the right: the photon trace, the autocorrelation on a log lag "
        "axis, and the number and intensity distributions on a log size axis, with the "
        "recovered distributions and the z-average overlaid. Moving a slider re-runs the "
        "simulation and redraws all four panels.", s["body"]))
    story.append(KeepTogether([figure("gui_screenshot.png", 168),
                               Paragraph("Figure 2: the Tk interface running the base case "
                                         "(water, 50 nm, &#963;/<i>d</i> = 0.12, &#945; = "
                                         "0.08, 25 C). Left, the input controls and the verdict "
                                         "readout; right, the four panels of the dashboard: "
                                         "(a) photon counts against time, (b) "
                                         "<i>g</i><sub>2</sub>(&#964;)&#8722;1 on a log lag "
                                         "axis with the monomer-only reference and the "
                                         "aggregation tail, (c) number and intensity "
                                         "distributions with the recovered curves and the "
                                         "z-average, (d) the input and output card. The "
                                         "window was drawn on a virtual X display so that the "
                                         "capture never touches a desktop session; the "
                                         "capture script is "
                                         "<font face=\"Courier\">report/capture_gui.py</font>.",
                                         s["caption"])]))

    story.append(Paragraph(
        "Figure 3 is the command line, and it is a transcript, not a mock-up: "
        "<font face=\"Courier\">report/make_figures.py</font> runs the installed CLI in a "
        "subprocess and renders the bytes it prints. The first block is the base case, the "
        "second is a 120 nm sample in ethanol with 25 % of its intensity in clusters - the "
        "case that comes back <i>polydisperse</i> - and the third lists the solvent database "
        "with the viscosity and refractive index the model will use at 25 C.", s["body"]))
    story.append(KeepTogether([figure("fig_cli.png", 168),
                               Paragraph("Figure 3: the command line. The same function that "
                                         "draws the interface prints this report, so the "
                                         "terminal and the window cannot disagree. The base "
                                         "case reports PDI = 0.177, monodisperse by the class "
                                         "criterion; the aggregated ethanol case reports PDI "
                                         "= 0.483, polydisperse.", s["caption"])]))

    story.append(Paragraph("3.2 The three outputs, for one case", s["h2"]))
    base = row(run(**BASE))
    story.append(Paragraph(
        f"The four-panel dashboard of Figure 4 is the same case drawn on one canvas, and "
        f"Table 3 lists every number it shows. That base case is deliberately not a single "
        f"size: 8 % of the scattered intensity sits in clusters at "
        f"{base['aggregate_diameter_nm']:.0f} nm. The three \"sizes\" that a DLS report can "
        f"quote therefore disagree, and it is worth seeing why before any of them is used: "
        f"the number mean is {base['number_mean_nm']:.2f} nm, the intensity mean is "
        f"{base['intensity_mean_nm']:.2f} nm and the cumulant z-average is "
        f"{base['z_avg_nm']:.2f} nm. The input diameter was 50 nm. The spread is equation (8) "
        f"doing its work: the clusters carry 8 % of the intensity but a negligible number "
        f"fraction, so they move the intensity-weighted averages and the PDI and barely touch "
        f"the number distribution.", s["body"]))
    story.append(KeepTogether([figure("fig_dashboard.png", 170),
                               Paragraph("Figure 4: the dashboard for the base case. (a) the "
                                         "speckle trace with the mean count rate; (b) the "
                                         "correlation with the aggregation tail marked and "
                                         "the decay time 1/&#915;&#772; drawn; (c) number "
                                         "and intensity distributions, the recovered curves "
                                         "and the z-average; (d) the input and output card. "
                                         "The takeaway is in panel (c): one sample, three "
                                         "different \"sizes\", all correct for their own "
                                         "definition.", s["caption"])]))

    base_rows = [
        ["input", "value used", "output", "value"],
        ["1. solvent", "water (H<sub>2</sub>O)", "<i>q</i>", f"{n['base_q_nm_inv']} nm<super>&#8722;1</super>"],
        ["", f"&#951; = {n['eta_water_25']} mPa&#183;s", "decay time 1/&#915;&#772;",
         f"{n['base_tau_ms']} ms"],
        ["2. particle refractive index", "1.590", "<i>D</i><sub>z</sub>",
         f"{n['base_diffusion_um2_s']} &#181;m<super>2</super>/s"],
        ["", f"contrast <i>K</i> = {base['contrast']:.5f}", "number mean",
         f"{n['base_number_mean_nm']} nm"],
        ["3. particle size", "50.0 nm", "intensity mean",
         f"{n['base_intensity_mean_nm']} nm"],
        ["4. size distribution", "&#963;/<i>d</i> = 0.120, lognormal", "z-average",
         f"{n['base_z_nm']} nm"],
        ["5. aggregation &#945;", f"0.080 (clusters at {base['aggregate_diameter_nm']:.0f} nm)",
         "PDI", f"{n['base_pdi']}"],
        ["6. temperature", "25.0 C (298.15 K)", "criterion", "monodisperse (PDI &lt; 0.20)"],
        ["", "", "count rate", f"{n['base_kcps']} kcps"],
        ["", "", "recovered peaks",
         f"{base['recovered_i_nm']:.0f} nm (I) / {base['recovered_n_nm']:.0f} nm (N)"],
    ]
    story.append(table(base_rows, [124, 150, 96, 134], s))
    story.append(Paragraph("Table 3: the base case, input by input and output by output. Every "
                           "value is computed at build time; the PDI is the ISO definition, "
                           "equation (11). The case is the package default, not a tuned "
                           "example.", s["caption"]))


def section_four(story, s, n) -> None:
    story.append(Paragraph("4. The analysis chain: cumulant, PDI and inversion", s["h1"]))
    story.append(Paragraph(
        "A correlation curve is one measurement, and two different analyses are applied to "
        "it. The moment analysis answers \"how big, and how wide?\" with two numbers. The "
        "inversion answers \"what does the distribution look like?\" with a curve. They "
        "should agree, and this section measures whether they do.", s["body"]))

    story.append(Paragraph("4.1 The cumulant fit and the PDI", s["h2"]))
    story.append(Paragraph(
        "The fit takes the logarithm of the field correlation, weights each lag by the square "
        "root of the amplitude (so that the noisiest, smallest-amplitude lags count least), "
        "and fits a quadratic in &#964; over the lags where the normalised correlation lies "
        "between 0.12 and 0.98. The linear coefficient is &#8722;&#915;&#772; and twice the "
        "quadratic coefficient is &#956;<sub>2</sub>; equation (11) then gives the PDI and "
        "equation (12) the z-average. The window matters: below 0.12 the curve is dominated "
        "by the baseline, above 0.98 by the intercept, and neither carries size information.", s["body"]))
    story.append(Paragraph(
        "Table 4 is the measurement that makes the PDI interpretable. A 100 nm mode is "
        "widened from &#963;/<i>d</i> = 0.02 to 0.30 and the PDI is read back from the fitted "
        "curve. It rises from 0.0008 to 0.1366, and the quantity &#8730;(PDI/2) tracks the "
        "input width to within 13 % over the whole range. That is not a coincidence: for a "
        "narrow distribution the square of the relative standard deviation of the decay rate "
        "is (&#963;/<i>d</i>)<super>2</super>, and equation (11) multiplies it by two. The "
        "factor of two in the ISO definition exists so that the index is of order the squared "
        "coefficient of variation, and this table is that statement measured.", s["body"]))
    pdi_rows = polydispersity_rows()
    rows = [["&#963;/<i>d</i>", "PDI (fit)", "PDI (exact)", "&#8730;(PDI/2)",
             "intensity mean (nm)", "z-average (nm)", "recovered I peak (nm)", "verdict"]]
    for entry in pdi_rows:
        rows.append([
            f"{entry['sigma_rel']:.2f}",
            f"{entry['pdi']:.4f}",
            f"{entry['pdi_exact']:.4f}",
            f"{(entry['pdi'] / 2.0) ** 0.5:.3f}",
            f"{entry['intensity_mean_nm']:.1f}",
            f"{entry['z_avg_nm']:.2f}",
            f"{entry['recovered_i_nm']:.0f}",
            "monodisperse" if entry["monodisperse"] else "polydisperse",
        ])
    story.append(table(rows, [46, 52, 56, 56, 78, 66, 80, 70], s))
    story.append(Paragraph("Table 4: 100 nm primary mode, width swept, no aggregation. "
                           "&#8730;(PDI/2) reproduces the input width to 13 % at the widest "
                           "case, and the classroom criterion PDI &lt; 0.2 keeps calling a "
                           "30 %-wide distribution monodisperse: the index measures the "
                           "variance, and 2&#215;0.09 is still only 0.18.", s["caption"]))
    story.append(Paragraph(
        "The last column is the point a marker should take from this table. The criterion "
        "\"if PDI &lt; 0.2\" is a <i>screen</i>, not a measurement: a distribution with "
        "&#963;/<i>d</i> = 0.30 - a third of the diameter - passes it, because the PDI is "
        "twice a squared relative width and 0.2 corresponds to a 32 % width. A PDI below 0.2 "
        "therefore does not mean monodisperse; it means the width is under about a third. The "
        "simulator reports the exact PDI of the input distribution beside the fitted one for "
        "exactly this reason, so that the gap between what was put in and what a curve can "
        "say is visible.", s["body"]))
    story.append(Paragraph(
        "The z-average column shows the second half of the same story. At &#963;/<i>d</i> = "
        f"0.02 it reads 100.12 nm for a 100 nm input, and at 0.30 it reads "
        f"{n['z_avg_sigma_030']} nm. The bias is not an error in the fit: the z-average is "
        "defined through the intensity-weighted mean of 1/<i>d</i> (equation 12), which sits "
        "above the number-mean diameter for any polydisperse sample, and the intensity "
        "weighting of equation (8) weights the large particles most. For &#963;/<i>d</i> = "
        "0.10 the same definition puts the z-average 3-4 % above the input diameter across "
        "the size sweep of section 5.1. A measured z-average and a nominal diameter are "
        "therefore not the same number, and a 3 % disagreement is not a disagreement.", s["body"]))

    story.append(Paragraph("4.2 The inversion", s["h2"]))
    story.append(Paragraph(
        "The inversion solves equation (13) for a distribution. Three choices in it are "
        "visible in every recovered curve and are declared here rather than buried in the "
        "code: the grid runs from 1 nm to 10 &#181;m in 240 logarithmic steps, so a mode "
        "narrower than one grid step is reported at the nearest step; the second-difference "
        "penalty smooths the solution, which trades resolution against stability; and the "
        "number distribution is reported only over the support where the intensity exceeds "
        "1 % of its peak, so a recovered number curve is flat at zero where the measurement "
        "is blind rather than merely small.", s["body"]))
    story.append(Paragraph(
        "Figure 5 tests it against the input it was given. Panel (a) plots the recovered "
        "intensity mode, the recovered number mode and the cumulant z-average against the "
        "input diameter for six sizes from 10 nm to 500 nm; panel (b) turns the same numbers "
        "into errors; panel (c) shows the recovered curve against the true distribution for "
        "two of the sizes. On noiseless data the inversion returns the mode to within "
        f"{abs(size_rows()[2]['recovered_i_error_pct']):.1f} % and the z-average to within "
        f"{abs(size_rows()[0]['z_error_pct']):.1f} % across the sweep, and the recovered "
        "curve follows the width of the input, not just its position.", s["body"]))
    story.append(KeepTogether([figure("fig_inversion.png", 168),
                               Paragraph("Figure 5: inversion validation over 50x in "
                                         "diameter. (a) both routes lie on the 1:1 line; (b) "
                                         "the errors: the z-average is high at small sizes "
                                         "because it is intensity-weighted, the intensity "
                                         "mode is high by 2-6 %, the number mode is low by "
                                         "2-6 %; (c) for 10 nm and 100 nm the recovered "
                                         "curve reproduces the width of the true curve.", s["caption"])]))
    size = size_rows()
    rows = [["<i>d</i><sub>0</sub> (nm)", "&#964;<sub>c</sub> (ms)", "<i>D</i> "
             "(&#181;m<super>2</super>/s)", "z-average (nm)", "z err (%)", "PDI",
             "recovered I (nm)", "err (%)", "recovered N (nm)", "err (%)", "residual"]]
    for entry in size:
        rows.append([
            f"{entry['size_nm']:.0f}",
            f"{entry['tau_c_ms']:.4f}",
            f"{entry['diffusion_m2_s'] * 1e12:.3f}",
            f"{entry['z_avg_nm']:.2f}",
            f"{entry['z_error_pct']:+.2f}",
            f"{entry['pdi']:.4f}",
            f"{entry['recovered_i_nm']:.0f}",
            f"{entry['recovered_i_error_pct']:+.1f}",
            f"{entry['recovered_n_nm']:.0f}",
            f"{entry['recovered_n_error_pct']:+.1f}",
            f"{entry['recovered_residual']:.4f}",
        ])
    story.append(table(rows, [38, 44, 50, 52, 42, 40, 52, 40, 52, 40, 48], s))
    story.append(Paragraph("Table 5: the size sweep with both analyses. Water, 25 C, n_p = "
                           "1.590, &#963;/<i>d</i> = 0.10, no aggregation, no noise. The "
                           "residual column is zero everywhere because the curve being "
                           "inverted was generated without noise; it measures nothing here, "
                           "which is why the noisy case in section 6.3 matters.", s["caption"]))

    story.append(Paragraph("4.3 Why two routes, and when they disagree", s["h2"]))
    story.append(Paragraph(
        "The cumulant fit and the inversion answer different questions and fail differently. "
        "The cumulant fit uses only the first two moments of the decay-rate distribution: it "
        "is stable, it needs no grid, and it cannot show a second population - two equal "
        "modes at 50 and 60 nm and one broad mode at 55 nm produce the same "
        "&#915;&#772; and &#956;<sub>2</sub> to first order. The inversion can show the "
        "second population, but it needs a regularisation choice, it produces a curve that "
        "looks equally plausible at neighbouring penalty strengths, and its mode is biased "
        "when the distribution is narrow enough that the grid, not the data, sets the width.", s["body"]))
    story.append(Paragraph(
        "In this report the two routes are used accordingly. Size statements use the "
        "cumulant z-average and the recovered intensity mode together, and are quoted with "
        "the spread between them. Shape statements - is there a second population? - use the "
        "recovered distribution, because the cumulant cannot see one. Section 5.3 is the case "
        "that shows why: when clusters appear, the mode of the recovered intensity "
        "distribution stays on the monomer while the PDI doubles, and a report that quoted "
        "only the mode would call an aggregated sample monodisperse.", s["body"]))


def section_five(story, s, n) -> None:
    story.append(Paragraph("5. What each input does to the measurement", s["h1"]))
    story.append(Paragraph(
        "This section is the heart of the assignment: for each of the five inputs on the "
        "class page, one figure and one table, and one sentence saying what a marker should "
        "see. The figures are plotted from the same run as the tables, and every number in "
        "the prose is read from those tables.", s["body"]))

    story.append(Paragraph("5.1 Size: the correlation moves, the shape does not", s["h2"]))
    size = {float(entry["size_nm"]): entry for entry in size_rows()}
    story.append(Paragraph(
        "Change the diameter and the whole correlation curve slides along the log lag axis "
        "(Figure 6a). Over the sweep of Table 5, from 10 nm to 500 nm, the decay time rises "
        f"from {n['size10_tau_ms']} ms to {n['size500_tau_ms']} ms: a factor of "
        f"{n['size_tau_ratio']} for a factor of 50 in diameter. The diffusion coefficient "
        f"falls by the same factor, from {n['size10_diffusion_um2_s']} to "
        f"{n['size500_diffusion_um2_s']} &#181;m<super>2</super>/s, because it is inversely "
        "proportional to the diameter (equation 2). Nothing else changes: &#946; stays 0.85, "
        "the curve keeps its exponential shape, and the recovered distribution keeps its "
        "width. That is the class page's hand-drawn statement - <i>if particle larger, "
        "slower; if particle smaller, faster</i> - measured rather than asserted, and it is "
        "the reason a DLS measurement is a size measurement at all.", s["body"]))
    story.append(KeepTogether([figure("fig_size_series.png", 168),
                               Paragraph("Figure 6: the size series. (a) the correlation "
                                         "slides right as the particle grows, keeping its "
                                         "shape; (b) the true intensity distribution (solid) "
                                         "and the inversion (dotted) at each size - no second "
                                         "mode, and the width is reproduced; (c) the measured "
                                         "decay time against the diameter on log axes, with "
                                         "the &#964;<sub>c</sub> &#8733; <i>d</i> guide.", s["caption"])]))
    story.append(Paragraph(
        f"The error columns of Table 5 are the interesting part. The z-average is "
        f"{n['size_z_error_small']} % high at 10 nm and {n['size_z_error_large']} % at "
        "500 nm, and the recovered intensity mode is between +1.9 % and +5.9 % across the "
        "sweep. Both drifts have the same cause: the intensity weighting of equation (8) "
        "weights the large particles of the distribution more than the small ones, so the "
        "recovered size is pulled up, and the pull is strongest where the form factor has "
        "not yet started to suppress the largest particles (small <i>qd</i>). At 500 nm the "
        "form factor is already flattening the upper tail, and the bias vanishes. A "
        "systematic error of a few percent that changes sign with <i>qd</i> is exactly what "
        "a form-factor approximation predicts, and it is the honest size of the model's "
        "error budget: below about 5 %, not below 1 %.", s["body"]))

    story.append(Paragraph("5.2 Polydispersity: the curve bends and the PDI rises", s["h2"]))
    pdi = {float(entry["sigma_rel"]): entry for entry in polydispersity_rows()}
    story.append(Paragraph(
        "A monodisperse sample has a correlation that is a single exponential, so "
        "<i>g</i><sub>2</sub>&#8722;1 is a straight line on a log-log plot. Widen the "
        "distribution and the line bends, because the curve becomes a sum of exponentials "
        "with different decay times (Figure 7a). The bend is what the second cumulant "
        "measures. Table 4 has the numbers, and Figure 7b plots them against the two-mode "
        "prediction 2(&#963;/<i>d</i>)<super>2</super>: the measured PDI rises from "
        f"{n['pdi_sigma_002']} at &#963;/<i>d</i> = 0.02 to {n['pdi_sigma_030']} at 0.30, "
        "and &#8730;(PDI/2) returns the input width to within 13 % over that whole range.", s["body"]))
    story.append(KeepTogether([figure("fig_polydispersity.png", 168),
                               Paragraph("Figure 7: widening a 100 nm mode. (a) on log-log "
                                         "axes a single exponential is a straight line; width "
                                         "bends it, and the bend starts earlier than the eye "
                                         "expects; (b) the fitted PDI against the input "
                                         "width, with 2(&#963;/<i>d</i>)<super>2</super> "
                                         "and the class criterion; (c) the inversion follows "
                                         "the width as well as the position.", s["caption"])]))
    story.append(Paragraph(
        f"The other half of the answer is what polydispersity does to the reported size. At "
        f"&#963;/<i>d</i> = 0.30 the number mean is still 100 nm, the intensity mean is "
        f"{n['intensity_mean_sigma_030']} nm and the z-average is {n['z_avg_sigma_030']} nm. "
        "A marker reading only \"the size\" would see a 25 % larger particle where the "
        "sample has a 30 % wider one. This is why the three distributions are drawn on the "
        "same axes in every figure of this report, and why the PDI is reported beside the "
        "size rather than instead of it.", s["body"]))

    story.append(Paragraph("5.3 Aggregation: a second mode, and the PDI as its detector",
                           s["h2"]))
    agg = {float(entry["aggregation"]): entry for entry in aggregation_rows()}
    story.append(Paragraph(
        "The aggregation parameter &#945; is the share of the scattered <i>intensity</i> "
        "carried by clusters, and the cluster mode is placed at 5.5 <i>d</i><sub>0</sub> - "
        "550 nm for a 100 nm primary mode. Figure 8 shows the three consequences. The "
        "correlation grows a slow tail: at a lag of about a millisecond, where the monomer "
        "correlation has already fallen by two decades, the aggregated samples still carry "
        "correlation from the clusters. The intensity distribution grows a second peak. And "
        "the PDI crosses the classroom threshold.", s["body"]))
    story.append(KeepTogether([figure("fig_aggregation.png", 168),
                               Paragraph("Figure 8: aggregation of a 100 nm mode. (a) the "
                                         "correlation with the slow cluster tail, and the "
                                         "same tail on a log scale in the inset; (b) the "
                                         "second mode at 5.5 <i>d</i><sub>0</sub>, which the "
                                         "inversion also recovers (dotted); (c) the PDI "
                                         "against &#945;, with the input distribution's own "
                                         "PDI beside it and the 0.2 criterion drawn.", s["caption"])]))
    rows = [["&#945;", "cluster intensity share", "cluster <i>d</i> (nm)",
             "intensity mean (nm)", "z-average (nm)", "PDI (fit)", "PDI (exact)",
             "recovered I peak (nm)", "verdict"]]
    for entry in aggregation_rows():
        rows.append([
            f"{entry['aggregation']:.2f}",
            f"{1.0 - entry['monomer_intensity_frac']:.3f}",
            f"{entry['aggregate_diameter_nm']:.0f}",
            f"{entry['intensity_mean_nm']:.1f}",
            f"{entry['z_avg_nm']:.2f}",
            f"{entry['pdi']:.4f}",
            f"{entry['pdi_exact']:.4f}",
            f"{entry['recovered_i_nm']:.0f}",
            "monodisperse" if entry["monodisperse"] else "polydisperse",
        ])
    story.append(table(rows, [38, 76, 58, 66, 60, 52, 56, 70, 78], s))
    story.append(Paragraph("Table 6: aggregation sweep, 100 nm primary mode, "
                           "&#963;/<i>d</i> = 0.10. Ten percent of the intensity in clusters "
                           "is enough to cross PDI = 0.2, while the recovered mode stays at "
                           "102 nm: the PDI, not the mode, is the aggregation detector.", s["caption"]))
    story.append(Paragraph(
        f"Table 6 carries a result that contradicts the intuitive reading of the "
        f"distribution plot and is worth stating plainly. At &#945; = 0.10 the PDI is "
        f"{n['agg_pdi_010']}, which crosses the criterion, but the recovered intensity "
        f"<i>mode</i> is still 102 nm - the monomer peak is taller than the cluster peak even "
        f"when the clusters carry a tenth of the intensity, because they are spread over a "
        f"wide logarithmic range. At &#945; = 0.30 the PDI is {n['agg_pdi_030']}, the "
        f"z-average has moved from 103 nm to {n['agg_z_030']} nm and the intensity mean to "
        f"{n['agg_intensity_mean_030']} nm, while the mode is <i>still</i> 102 nm. The mode "
        f"is therefore the wrong statistic for detecting aggregation; the moments are the "
        f"right one, which is exactly why an instrument reports a PDI beside a size.", s["body"]))
    story.append(Paragraph(
        "There is a second lesson in the same table. The PDI of the input distribution is "
        "known exactly in a simulation, and it is lower than the fitted PDI everywhere in the "
        f"table - {n['agg_exact_pdi_010']} against {n['agg_pdi_010']} at &#945; = 0.10. The "
        "two-cumulant fit is a truncated expansion, so a strongly bimodal decay is not "
        "described well by two moments, and the fit over-states the width. The simulator "
        "prints both numbers so that this gap is visible rather than hidden.", s["body"]))

    story.append(Paragraph("5.4 Solvent and temperature: the same particle, a different clock",
                           s["h2"]))
    solvent = {(entry["solvent"], float(entry["temperature_c"])): entry
               for entry in solvent_rows()}
    water_10, water_55 = solvent[("water", 10.0)], solvent[("water", 55.0)]
    story.append(Paragraph(
        "Solvent and temperature enter only through the viscosity in equation (2) and the "
        "refractive index in equation (1). Heating water from 10 C to 55 C drops its "
        f"viscosity from {water_10['viscosity_mpas']:.3f} to {water_55['viscosity_mpas']:.3f} "
        f"mPa&#183;s, and the decay time of the same 100 nm particle falls from "
        f"{n['tau_water_10']} to {n['tau_water_55']} ms - a factor of "
        f"{n['tau_temp_ratio']}, which is the 2.60x viscosity ratio multiplied by the 1.16x "
        f"rise in <i>T</i> and a 0.99x change in 1/<i>q</i><super>2</super> "
        f"(Figure 9a, 9b). The "
        "reported diameter does not move: it is "
        f"{n['z_water_10']} nm at 10 C and {n['z_water_55']} nm at 55 C, because the analysis "
        "divides the measured decay rate by the viscosity it is told the sample has. That is "
        "the whole content of the temperature input: <b>it changes the clock, not the "
        "particle</b>, and a DLS measurement is only as good as the viscosity used to reduce "
        "it.", s["body"]))
    story.append(KeepTogether([figure("fig_solvent_temperature.png", 168),
                               Paragraph("Figure 9: solvent and temperature, 100 nm mode. (a) "
                                         "the decay time against temperature for the two class "
                                         "solvents; (b) water at 10 C and 55 C - the same "
                                         "curve shifted, not reshaped; (c) every case plotted "
                                         "against the Stokes-Einstein prediction "
                                         "3&#960;&#951;<i>d</i>/(<i>k</i><sub>B</sub><i>Tq</i>"
                                         "<super>2</super>), on the 1:1 line to within 2 %.",
                                         s["caption"])]))
    rows = [["solvent", "<i>T</i> (C)", "&#951; (mPa&#183;s)", "<i>n</i><sub>s</sub>",
             "<i>q</i> (nm<super>&#8722;1</super>)", "<i>D</i> "
             "(&#181;m<super>2</super>/s)", "&#964;<sub>c</sub> (ms)", "z-average (nm)",
             "PDI", "count rate (kcps)"]]
    for entry in solvent_rows():
        rows.append([
            entry["solvent"],
            f"{entry['temperature_c']:.0f}",
            f"{entry['viscosity_mpas']:.3f}",
            f"{entry['solvent_ri']:.4f}",
            f"{entry['q_nm_inv']:.5f}",
            f"{entry['diffusion_m2_s'] * 1e12:.3f}",
            f"{entry['tau_c_ms']:.4f}",
            f"{entry['z_avg_nm']:.2f}",
            f"{entry['pdi']:.4f}",
            f"{entry['count_rate_kcps']:.1f}",
        ])
    story.append(table(rows, [52, 34, 58, 44, 58, 52, 50, 56, 42, 58], s))
    story.append(Paragraph("Table 7: solvent and temperature sweep at 100 nm. The decay time "
                           "changes by a factor of three across the table; the z-average "
                           "moves in the third digit. Viscosity is the input that a DLS "
                           "result is most sensitive to and least protected against.", s["caption"]))
    story.append(Paragraph(
        "The two solvents separate for a reason worth naming, because it is the second-order "
        "part of the same physics. At 25 C ethanol is "
        f"{n['eta_ratio']}x more viscous than water, which should slow the decay by that "
        f"factor; but its refractive index is higher, so <i>q</i> is larger "
        f"({n['q_ethanol_25']} against {n['q_water_25']} nm<super>&#8722;1</super>) and the "
        f"decay rate gains a factor of {n['solvent_q_factor']} from <i>q</i>"
        "<super>2</super>. The measured ratio of decay times is "
        f"{n['solvent_tau_ratio']}, which is the product of the two. This is why the model "
        "reports <i>n</i><sub>s</sub>(T) and not just &#951;(T), and why a sample measured in "
        "a different buffer is not directly comparable unless the analysis is told so.", s["body"]))

    story.append(Paragraph("5.5 Particle refractive index: signal, not size", s["h2"]))
    ri = {float(entry["particle_ri"]): entry for entry in refractive_index_rows()}
    story.append(Paragraph(
        "The particle refractive index appears in exactly one place, the contrast factor "
        "<i>K</i> of equation (6). Raise it from 1.40 to 2.00 and the count rate climbs from "
        f"{n['kcps_np_140']} to {n['kcps_np_200']} kcps, a factor of 75, while the "
        "correlation curve, the z-average, the PDI and both recovered modes are unchanged to "
        "the last digit (Figure 10, Table 8). The input that a beginner expects to matter most "
        "- how strongly the particle scatters - turns out to be the one that carries no size "
        "information at all. It carries the <i>signal-to-noise</i> ratio, and through that it "
        "decides whether any of the other inputs can be measured.", s["body"]))
    story.append(KeepTogether([figure("fig_refractive_index.png", 168),
                               Paragraph("Figure 10: the particle refractive index. (a) the "
                                         "mean count rate against <i>n</i><sub>p</sub>, with "
                                         "the index-matched case on the model floor and the "
                                         "ceiling marked; (b) three indices, one curve - the "
                                         "solid, dashed and marked lines lie on top of each "
                                         "other.", s["caption"])]))
    rows = [["<i>n</i><sub>p</sub>", "<i>n</i><sub>p</sub>/<i>n</i><sub>s</sub>",
             "contrast <i>K</i>", "count rate (kcps)", "z-average (nm)", "PDI",
             "recovered I (nm)", "recovered N (nm)"]]
    for entry in refractive_index_rows():
        rows.append([
            f"{entry['particle_ri']:.3f}",
            f"{entry['index_ratio']:.4f}",
            f"{entry['contrast']:.5f}",
            f"{entry['count_rate_kcps']:.1f}",
            f"{entry['z_avg_nm']:.2f}",
            f"{entry['pdi']:.4f}",
            f"{entry['recovered_i_nm']:.0f}",
            f"{entry['recovered_n_nm']:.0f}",
        ])
    story.append(table(rows, [46, 66, 66, 78, 66, 44, 70, 72], s))
    story.append(Paragraph("Table 8: the refractive-index sweep at 100 nm. Two decades of "
                           "count rate, no change in size: the index sets the signal and "
                           "nothing else. The 15 kcps entry is the model floor, not a "
                           "prediction (section 6.1).", s["caption"]))
    story.append(Paragraph(
        f"The contrast falls steeply as the particle approaches the index of water: "
        f"<i>K</i> = {n['contrast_np_159']} at <i>n</i><sub>p</sub> = 1.59 but "
        f"{n['contrast_np_140']} at 1.40, a factor of 13, which is why the count rate in the "
        f"table drops from {n['kcps_np_159']} to {n['kcps_np_140']} kcps. A particle that is "
        "nearly index-matched to its solvent is nearly invisible to DLS, however large it is. "
        "That is a real instrumental limit and it is the physical content of \"refractive "
        "index of the particle\" as an input: it decides whether the sample can be measured, "
        "not what the measurement says.", s["body"]))

    story.append(Paragraph("5.6 The detector angle, and the wavelength", s["h2"]))
    angle = {float(entry["angle_deg"]): entry for entry in angle_rows()}
    story.append(Paragraph(
        f"The class page says 178 deg and this report uses 173 deg. Table 9 puts the "
        f"difference on the record: 178 deg raises <i>q</i> from {n['q_173']} to "
        f"{n['q_178']} nm<super>&#8722;1</super>, which is +0.17 %, and would move every "
        f"reported diameter by {n['angle_scale_178']} % if the analysis assumed 173 deg while "
        f"the bench sat at 178. The same table carries a 90 deg case to show the size of the "
        f"effect that a wrong angle <i>can</i> have: there <i>q</i> is 29 % smaller and every "
        f"size would be {n['angle_scale_90']} % wrong, which is the difference between "
        f"\"100 nm\" and \"141 nm\". A backscatter angle is used in commercial instruments "
        f"because it shortens the path inside a turbid sample and because the large "
        f"<i>q</i> makes small particles decay faster and therefore measurable; that "
        f"practical argument is the reason both 173 and 178 appear in the literature.", s["body"]))
    rows = [["&#952; (deg)", "<i>q</i> (nm<super>&#8722;1</super>)",
             "<i>q</i> vs 173 deg (%)", "implied size scale vs 173 deg (%)",
             "&#964;<sub>c</sub> (ms)", "z-average (nm)", "PDI", "recovered I (nm)"]]
    for entry in angle_rows():
        rows.append([
            f"{entry['angle_deg']:.0f}",
            f"{entry['q_nm_inv']:.5f}",
            f"{entry['q_rel_pct']:+.3f}",
            f"{entry['size_scale_rel_pct']:+.3f}",
            f"{entry['tau_c_ms']:.4f}",
            f"{entry['z_avg_nm']:.2f}",
            f"{entry['pdi']:.4f}",
            f"{entry['recovered_i_nm']:.0f}",
        ])
    story.append(table(rows, [48, 70, 78, 110, 62, 66, 44, 72], s))
    story.append(Paragraph("Table 9: the detector angle, 100 nm mode. The 178 deg row is the "
                           "class page's reading and the 90 deg row is the counter-example "
                           "that shows why an angle must be stated precisely. The reported "
                           "sizes barely move because the analysis divides the measured decay "
                           "rate by the <i>same</i> assumed <i>q</i>; the last column of the "
                           "table is what an error in that assumption would cost.", s["caption"]))
    story.append(Paragraph(
        f"One subtlety is visible in the table and worth stating rather than hiding: the "
        f"z-average is {angle[173.0]['z_avg_nm']:.2f} nm at 173 deg and "
        f"{angle[90.0]['z_avg_nm']:.2f} nm at 90 deg - almost unchanged - because the "
        f"simulator computes the decay rate from the same <i>q</i> it later divides by, so an "
        f"error in the assumed angle cancels in the forward model. On a real instrument "
        f"nothing cancels: the correlator measures &#915; and the software supplies <i>q</i>, "
        f"and an error in <i>q</i> becomes an error of twice its relative size in every "
        f"reported diameter. The \"implied size scale\" column of Table 9 is that error, and "
        f"it is the number to quote when the angle is questioned.", s["body"]))
    story.append(Paragraph(
        "The wavelength is fixed at the He-Ne line, 632.8 nm, which is an instrument choice "
        "rather than a measurement. It enters only through equation (1), on the same footing "
        "as the index: a 1 % error in the wavelength would be a 1 % error in every size, and "
        "a real instrument knows its laser line far better than that.", s["body"]))


def section_six(story, s, n) -> None:
    story.append(Paragraph("6. Limits, approximations and uncertainties", s["h1"]))
    story.append(Paragraph(
        "A simulator is only useful if its own error bars are known. This section separates "
        "three different things that a reader might otherwise confuse: the approximations "
        "built into the physics, the numerical uncertainty of the analysis, and the "
        "quantities the model does not attempt at all.", s["body"]))

    story.append(Paragraph("6.1 The approximation register", s["h2"]))
    rows = [
        ["assumption", "what is used", "what it costs"],
        ["form factor", "0.35 <i>P</i><sub>sphere</sub> + 0.65 "
                        "<i>P</i><sub>Guinier</sub>, equation (7)",
         "not a Mie solution. Exact as <i>qd</i> &#8594; 0; approximate at large "
         "<i>qd</i>. Drives the few-percent size drift in Table 5."],
        ["aggregate population", "a second lognormal mode at 5.5 <i>d</i><sub>0</sub>, "
                                 "width 1.25x the primary",
         "a model of a cluster, not a fractal aggregate. The cluster size is a constant "
         "of the model, not a fitted result."],
        ["photon trace", "complex Ornstein-Uhlenbeck field, intensity by Siegert",
         "an illustration of speckle, not the data that is fitted. Its peaks carry no "
         "information about the sample beyond the mean rate."],
        ["count rate", "280 kcps at 50 nm and <i>K</i> = 0.025, scaling as "
                       "<i>K</i>(<i>d</i>/50)<super>1.2</super>, clipped to 15-2500 kcps",
         "an instrument model, not a radiometric calculation. Absolute kcps values in "
         "this report are illustrative; the ratios are the content."],
        ["inversion support", "number distribution reported where the intensity exceeds 1 % "
                              "of its peak",
         "a recovered number curve is flat outside that band because the measurement is "
         "blind there, not because the sample has no particles."],
        ["noise", "additive on <i>g</i><sub>2</sub>&#8722;1, as a fraction of the intercept, "
                  "clipped at zero",
         "one-sided where the correlation has decayed; it biases the inversion low "
         "(section 6.3). A real correlator's noise is Poisson and symmetric in the counts."],
        ["z-average", "computed from the moments of the input distribution",
         "carries no fitting noise in this model. An instrument would fit it from the "
         "same noisy curve, so its scatter is not shown here."],
        ["correlations between particles", "none: dilute, independent scatterers",
         "multiple scattering is not modelled, so the model describes a dilute sample and "
         "a real turbid one would read smaller and less stable."],
    ]
    story.append(table(rows, [78, 190, 236], s))
    story.append(Paragraph("Table 10: every approximation in the model, what it replaces, and "
                           "what it costs. Items in this table are the ones a marker is "
                           "entitled to ask about; each is also stated where it is used.", s["caption"]))

    story.append(Paragraph("6.2 The uncertainty budget", s["h2"]))
    rows = [
        ["source", "size of the effect", "how it was measured"],
        ["detector angle, 173 against 178 deg", f"{n['angle_scale_178']} % on every diameter",
         "Table 9, same sample at both angles"],
        ["solvent viscosity", "&#951; enters <i>D</i> linearly, so a 1 % viscosity error is "
                              "a 1 % size error",
         "equation (2); the VFT fits reproduce standard water values to 0.2 % over 0-60 C [8]"],
        ["solvent refractive index", "<i>q</i> enters as <i>q</i><super>2</super>, so 0.1 % "
                                     "in <i>n</i><sub>s</sub> is 0.1 % in size",
         "equation (1); <i>n</i>(633 nm) is interpolated from a three-decimal table [9]"],
        ["form-factor approximation", "2-6 % on the recovered mode, sign changing with "
                                      "<i>qd</i>", "Table 5, six sizes"],
        ["z-average definition", "+3 to +4 % for &#963;/<i>d</i> = 0.10, tending to 0 as the "
                                 "distribution narrows", "Table 5 against Table 4"],
        ["cumulant truncation", f"PDI over-stated: {n['agg_exact_pdi_010']} exact against "
                                f"{n['agg_pdi_010']} fitted at &#945; = 0.10",
         "Table 6, exact and fitted PDI in the same row"],
        ["correlation noise, 1 % of the intercept", "the inversion reads "
                                                    f"{n['inv_noisy_min_error']}-15.9 % low; "
                                                    "the PDI of a narrow sample scatters over "
                                                    "0.00-0.22",
         "Table 16 in Appendix C and Table 12"],
    ]
    story.append(table(rows, [120, 190, 194], s))
    story.append(Paragraph("Table 11: the uncertainty budget. The two largest items - the "
                           "angle assumption and the inversion's response to noise - are "
                           "larger than every numerical error in the code, which is why the "
                           "report quotes sizes to three significant figures and not more.", s["caption"]))

    story.append(Paragraph("6.3 Noise, the inversion and the PDI floor", s["h2"]))
    noisy = {float(entry["size_nm"]): entry for entry in noisy_inversion_rows()}
    story.append(Paragraph(
        "Everything above was measured on curves without noise, and that flatters the "
        "analysis. Adding noise at 1 % of the intercept - which is a quiet correlation "
        "function for a real instrument - changes both routes, and Table 16 in Appendix C "
        "gives the numbers. The inversion then reads "
        f"{n['inv_noisy_min_error']} % to 15.9 % <i>low</i> at every size, and the residual "
        f"rises from 0.0000 to {n['inv_residual_noisy']}. The mechanism is in the declared "
        "noise model of Table 10: the noise is added to <i>g</i><sub>2</sub>&#8722;1 and "
        "clipped at zero, so where the correlation has decayed to nothing the surviving "
        "noise is one-sided and positive, the square root turns it into a spurious slow "
        "component, and the fit answers with a distribution shifted to smaller sizes. The "
        "lesson is not that the inversion is broken; it is that a noiseless inversion "
        "accuracy means nothing, and that a real analysis needs many averaged correlation "
        "functions rather than one.", s["body"]))
    story.append(Paragraph(
        "The PDI is worse behaved than the size, which is the most useful single fact in this "
        "section. Table 12 repeats the same 2 %-wide 100 nm sample at four noise levels with "
        "five seeds each. Without noise the PDI is stable at "
        f"{n['pdi_noiseless']}. At 1 % noise the mean PDI is "
        f"{n['pdi_noise_1pct_mean']} and the five seeds span {n['pdi_noise_1pct_min']} to "
        f"{n['pdi_noise_1pct_max']} - the <i>same sample</i> is called monodisperse and "
        "polydisperse by the same code, depending only on the seed. A PDI is the difference of "
        "two large numbers divided by one of them, and it inherits every problem that this "
        "implies. Any PDI quoted from a single correlation function should carry that "
        "warning, and this is the reason the reports of this assignment quote the exact PDI "
        "of the input beside the fitted one wherever both are available.", s["body"]))
    rows = [["noise (fraction of intercept)", "PDI mean", "PDI min", "PDI max",
             "input distribution PDI"]]
    for entry in noise_rows():
        rows.append([
            f"{entry['noise_level']:.3f}",
            f"{entry['pdi_mean']:.4f}",
            f"{entry['pdi_min']:.4f}",
            f"{entry['pdi_max']:.4f}",
            "0.0008",
        ])
    story.append(table(rows, [130, 80, 80, 80, 134], s))
    story.append(Paragraph("Table 12: the PDI noise floor. One sample (100 nm, &#963;/<i>d</i> "
                           "= 0.02), five random seeds per noise level. Above 0.5 % noise "
                           "the reported PDI is no longer a measurement of the width.", s["caption"]))

    story.append(Paragraph("6.4 What is not modelled", s["h2"]))
    story.append(Paragraph(
        "Zeta potential is the largest omission, and it is deliberate. The class page lists "
        "it as a concept - the surface charge that makes particles stable - but not as an "
        "output, and it is measured by a different technique (electrophoretic light "
        "scattering, from the Doppler shift of particles driven by an electric field). A DLS "
        "size measurement says nothing about it, so this simulator says nothing about it.", s["body"]))
    story.append(Paragraph(
        "The others are listed here so that the boundary of the model is explicit: multiple "
        "scattering (the model assumes dilute, independently scattering particles), flow, "
        "sedimentation and convection (the sample is at rest), absorption and Mie resonances "
        "(the form factor is real and non-absorbing), detector dead time and afterpulsing "
        "(the correlator is ideal), aggregate polydispersity beyond the fixed width of the "
        "second mode, and any temperature gradient inside the cuvette (the sample has one "
        "temperature).", s["body"]))

    story.append(Paragraph("6.5 Reconciliation with the digital brief", s["h2"]))
    story.append(Paragraph(
        "The Canvas brief had not appeared when this report was built, so here is what would "
        "change if it differs from the in-class transcription. Each item is a small, isolated "
        "edit, which is why the simulator and the report are separated as they are.", s["body"]))
    rows = [
        ["if the digital brief says", "what changes", "where"],
        ["178 deg instead of 173", "one constant in "
                                   "<font face=\"Courier\">report/cases.py</font>; every figure "
                                   "and table regenerates; sizes shift by 0.17 % (Table 9)",
         "sections 2.1, 5.6"],
        ["a different PDI threshold", "one constant, "
                                      "<font face=\"Courier\">PDI_MONODISPERSE_LIMIT</font>, "
                                      "and the verdict strings follow it",
         "sections 4.1, 5.3"],
        ["zeta potential as an output", "a second instrument (electrophoretic light "
                                        "scattering) is needed; outside this model",
         "section 6.4"],
        ["further solvents", "add a row to <font face=\"Courier\">dlssim/solvents.py</font> "
                             "with a sourced &#951;(T) and <i>n</i>(T); the sweep picks it up",
         "section 2.5"],
        ["extra graded items", "sections 4 and 5 already cover size, width, aggregation, "
                               "solvent, temperature and index one at a time",
         "section 7"],
    ]
    story.append(table(rows, [110, 300, 94], s))
    story.append(Paragraph("Table 13: a reconciliation checklist. Nothing in the simulator is "
                           "tied to the report's structure, so a different brief changes the "
                           "document, not the physics.", s["caption"]))


def section_seven(story, s, n) -> None:
    story.append(Paragraph("7. Conclusion", s["h1"]))
    story.append(Paragraph(
        "A dynamic light scattering simulator was built to the in-class specification, and "
        "the report has measured what it does with each of the five inputs the class page "
        "names. The results are consistent, and they are the ones a marker can check against "
        "the figures: the correlation decay time is proportional to the particle diameter "
        f"({n['size_tau_ratio']}x over 50x in size); polydispersity bends the semilog decay "
        f"and produces a PDI that follows 2(&#963;/<i>d</i>)<super>2</super> to within 13 %; "
        f"clusters at 5.5 <i>d</i><sub>0</sub> add a second mode and cross the 0.2 criterion "
        f"at {n['agg_pdi_010']} for &#945; = 0.10; solvent and temperature change the decay "
        "time by a factor of three across 10-55 C and leave the reported diameter unchanged; "
        f"and the particle refractive index moves the count rate from {n['kcps_np_140']} to "
        f"{n['kcps_np_200']} kcps without moving any size at all.", s["body"]))
    story.append(Paragraph(
        "Two of those five statements are easy to get wrong, and they are the ones this "
        "report spends most of its space on. The first is that the PDI is a variance, not a "
        "purity test: a distribution with a 30 % spread passes the 0.2 criterion. The second "
        "is that the inversion is only as good as the noise on the curve it inverts: 1 % "
        f"noise moves every recovered mode {n['inv_noisy_min_error']}-15.9 % low and makes a "
        "2 % sample's PDI swing from 0.00 to 0.22 across random seeds. Both are properties of "
        "the method rather than of this implementation, and both are visible in the tables "
        "rather than asserted.", s["body"]))
    story.append(Paragraph(
        "What the simulator adds to the class page is therefore not only the plots it asks "
        "for, but the size of the errors attached to them. The three outputs the page names - "
        "the correlation with the photon trace, the number and intensity distributions, and "
        "the PDI - are each produced, and each is presented with the case where it misleads.", s["body"]))


def references(story, s) -> None:
    story.append(PageBreak())
    story.append(Paragraph("References", s["h1"]))
    story.append(Paragraph(
        "These are the ten entries audited in "
        "<font face=\"Courier\">docs/research/reference_audit.md</font>, each resolved through "
        "Crossref, the DOI handle registry, OpenLibrary or the BSI resolver before this report "
        "was built, and each used only for the claim its audit row supports. Three "
        "identifiers commonly quoted elsewhere were found to resolve to unrelated papers and "
        "are not used: the audit records them.", s["body"]))
    for index, (text, url) in enumerate(zip(REFERENCES, REFERENCE_URLS), start=1):
        story.append(Paragraph(f"[{index}]&nbsp;&nbsp;{linked_reference(text, url)}", s["ref"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Attribution notes, from the audit: the PDI definition PDI = 2&#956;<sub>2</sub>/"
        "&#915;&#772;<super>2</super> is ISO 22412:2025 [4], not Koppel [3], who supplies the "
        "cumulant method; the coherence factor &#946; is an instrument property, and the ideal "
        "Siegert relation has &#946; = 1 [2]; the scattering vector <i>q</i> is geometry [2], "
        "not a result of the 1964 Doppler paper [5]; the water refractive index at 633 nm is "
        "interpolated from a three-decimal table [9]; Kestin et al. give correlation equations "
        "rather than a printed table [8].", s["body"]))


def appendix_a(story, s) -> None:
    story.append(PageBreak())
    story.append(Paragraph("Appendix A: the code", s["h1"]))
    package = sorted((REPO_ROOT / "dlssim").glob("*.py"))
    scripts = ["cases.py", "size_study.py", "tables.py", "make_figures.py",
               "capture_gui.py", "numbers_source.py"]
    story.append(Paragraph(
        f"This appendix contains all {len(package)} modules of the "
        "<font face=\"Courier\">dlssim</font> package, in alphabetical order, followed by the "
        f"{len(scripts)} report scripts that produce the figures, the tables and the numbers "
        "quoted in the text. Every line is wrapped at 100 characters so that the files can be "
        "copied out of the PDF without breaks. The two files that are not reproduced here are "
        "this report builder itself "
        "(<font face=\"Courier\">report/generate_pdf_report.py</font>, which would double the "
        "appendix) and the two gates "
        "(<font face=\"Courier\">report/check_pdf.py</font>, "
        "<font face=\"Courier\">report/check_numbers.py</font>); all of them, with the test "
        f"suite, are in the repository at {REPO_URL}/tree/main/assignments/03-dls-simulator.",
        s["body"]))
    for path in package:
        story.append(Paragraph(f"dlssim/{path.name}", s["h2"]))
        story.append(Preformatted(_wrap_code(path.read_text(encoding="utf-8")), s["code"]))
    for name in scripts:
        path = HERE / name
        story.append(Paragraph(f"report/{name}", s["h2"]))
        story.append(Preformatted(_wrap_code(path.read_text(encoding="utf-8")), s["code"]))


def appendix_b(story, s) -> None:
    story.append(PageBreak())
    story.append(Paragraph("Appendix B: constants and records", s["h1"]))
    story.append(Paragraph(
        "Every constant the model uses, where it comes from, and how firm it is. The "
        "\"status\" column is the same one used in "
        "<font face=\"Courier\">data/SOURCES.md</font>: <i>exact</i> means defined or "
        "measured to the digits shown, <i>interpolated</i> means read from a coarser table, "
        "and <i>choice</i> means a modelling decision rather than a measurement.", s["body"]))
    rows = [
        ["quantity", "value used", "source", "status"],
        ["Boltzmann constant", "1.380649&#215;10<super>&#8722;23</super> J/K",
         "SI 2019 definition", "exact"],
        ["laser wavelength", "632.8 nm", "He-Ne line", "instrument choice"],
        ["detector angle", "173 deg (178 deg on the class page)",
         "class debrief; commercial backscatter practice", "choice, configurable"],
        ["water <i>n</i>(25 C), d<i>n</i>/d<i>T</i>",
         "1.3312, &#8722;1.0&#215;10<super>&#8722;4</super> /K",
         "Hale and Querry [9]", "interpolated at 633 nm"],
        ["water viscosity VFT", "<i>A</i> = 0.02414 mPa&#183;s, <i>B</i> = 570.58 K, "
                                "<i>T</i><sub>0</sub> = 140 K",
         "Kestin, Sokolov and Wakeham [8]",
         "fit anchored at 0.890 mPa&#183;s at 25 C; 0.2 % over 0-60 C"],
        ["ethanol <i>n</i>(25 C), d<i>n</i>/d<i>T</i>", "1.3594, &#8722;4.0&#215;10"
                                                        "<super>&#8722;4</super> /K",
         "handbook value, not line-verified in the audit", "stated value"],
        ["ethanol viscosity VFT", "<i>A</i> = 0.00593, <i>B</i> = 1550 K, "
                                  "<i>T</i><sub>0</sub> = 0 K",
         "CRC Handbook [10]", "fit anchored at 1.074 mPa&#183;s at 25 C"],
        ["particle refractive index", "1.590 default", "polystyrene at 633 nm", "user input"],
        ["coherence factor &#946;", "0.85", "instrument property [2]", "choice"],
        ["cluster mode", "5.5 <i>d</i><sub>0</sub>, width 1.25x the primary",
         "aggregation model", "choice"],
        ["form factor", "0.35 <i>P</i><sub>sphere</sub> + 0.65 <i>P</i><sub>Guinier</sub>",
         "equation (7); Bohren and Huffman [6]", "approximation"],
        ["count rate", "280 kcps at 50 nm and <i>K</i> = 0.025, scaling "
                       "<i>K</i>(<i>d</i>/50)<super>1.2</super>, clipped 15-2500 kcps",
         "stated instrument model", "not absolute"],
        ["lag grid", "220 points, 10<super>&#8722;7</super> to 1 s, log-spaced",
         "model", "choice"],
        ["inversion grid", "240 points, 1 nm to 10 &#181;m, second-difference penalty "
                           "10<super>&#8722;6</super>, lags kept while "
                           "<i>g</i><sub>1</sub> &#8805; 0.01",
         "Provencher [7] in its simplest form", "choice"],
        ["number-distribution support", "intensity above 1 % of its peak", "model", "choice"],
        ["monodisperse criterion", "PDI &lt; 0.20", "the class page's criterion", "classroom"],
    ]
    story.append(table(rows, [104, 148, 140, 112], s))
    story.append(Paragraph("Table 14: the constants. Nothing in this table is typed into the "
                           "figures; they read the model, which reads this table.", s["caption"]))

    import platform

    import matplotlib
    import numpy
    import scipy

    story.append(Paragraph("Records of the build", s["h2"]))
    story.append(Paragraph(
        f"The report was built on 15 November 2026 with Python {platform.python_version()}, "
        f"NumPy {numpy.__version__}, SciPy {scipy.__version__} and Matplotlib "
        f"{matplotlib.__version__}, from a frozen lock file "
        "(<font face=\"Courier\">uv sync --frozen</font>). Every stochastic quantity uses the "
        "fixed seed 42, except the PDI noise study, which uses seeds 1-5 deliberately so that "
        "the scatter can be shown. The report is rebuilt by three commands, in order: "
        "<font face=\"Courier\">uv run python -m report.make_figures</font>, "
        "<font face=\"Courier\">uv run python -m report.tables</font> and "
        "<font face=\"Courier\">uv run python -m report.generate_pdf_report</font>, and the "
        "whole chain with its gates is "
        "<font face=\"Courier\">uv run python -m tools.check_all</font>. The PDF is built with "
        "reportlab's invariant mode, so a rebuild from the same commit produces the same bytes; "
        "the gates refuse a document that is not self-contained or whose quoted numbers no "
        "longer match the model.", s["body"]))


def appendix_c(story, s) -> None:
    story.append(Paragraph("Appendix C: the generated tables", s["h1"]))
    story.append(Paragraph(
        "The tables in the body of the report are the ones needed to follow the argument. "
        "These are the same measurements with every column the scripts compute, including the "
        "solvent data and the support of the inversion, so that a reader can re-derive any "
        "number quoted in the text. They are generated by "
        "<font face=\"Courier\">report/size_study.py</font> and "
        "<font face=\"Courier\">report/tables.py</font>.", s["body"]))

    rows = [["<i>d</i><sub>0</sub>", "&#951; (mPa&#183;s)", "<i>q</i> (nm<super>&#8722;1"
            "</super>)", "<i>D</i> (&#181;m<super>2</super>/s)", "&#964;<sub>c</sub> (ms)",
             "z-avg (nm)", "PDI", "I mean (nm)", "rec. I (nm)", "rec. N (nm)",
             "support (nm)", "residual"]]
    for entry in size_rows():
        low, high = entry["support_nm"]
        rows.append([
            f"{entry['size_nm']:.0f}",
            f"{entry['viscosity_mpas']:.3f}",
            f"{entry['q_nm_inv']:.5f}",
            f"{entry['diffusion_m2_s'] * 1e12:.3f}",
            f"{entry['tau_c_ms']:.4f}",
            f"{entry['z_avg_nm']:.2f}",
            f"{entry['pdi']:.4f}",
            f"{entry['intensity_mean_nm']:.1f}",
            f"{entry['recovered_i_nm']:.0f}",
            f"{entry['recovered_n_nm']:.0f}",
            f"{low:.0f}-{high:.0f}",
            f"{entry['recovered_residual']:.4f}",
        ])
    story.append(table(rows, [32, 54, 56, 54, 44, 48, 40, 48, 44, 44, 54, 44], s))
    story.append(Paragraph("Table 15: the size sweep in full. Water, 25 C, n_p = 1.590, "
                           "&#963;/<i>d</i> = 0.10, no aggregation, no noise.", s["caption"]))

    rows = [["<i>d</i><sub>0</sub> (nm)", "z-average (nm)", "z err (%)",
             "recovered I (nm)", "err (%)", "recovered N (nm)", "err (%)", "residual"]]
    for entry in noisy_inversion_rows():
        rows.append([
            f"{entry['size_nm']:.0f}",
            f"{entry['z_avg_nm']:.2f}",
            f"{entry['z_error_pct']:+.2f}",
            f"{entry['recovered_i_nm']:.0f}",
            f"{entry['i_error_pct']:+.1f}",
            f"{entry['recovered_n_nm']:.0f}",
            f"{100.0 * (entry['recovered_n_nm'] - entry['size_nm']) / entry['size_nm']:+.1f}",
            f"{entry['recovered_residual']:.4f}",
        ])
    story.append(table(rows, [70, 78, 64, 78, 60, 78, 60, 60], s))
    story.append(Paragraph("Table 16: the same inversion on a curve carrying 1 % correlation "
                           "noise. Every mode is 12.6-15.9 % low and the residual rises to "
                           "0.027-0.044: the fit is telling the truth about its own misfit, "
                           "which is the one warning it gives.", s["caption"]))

    rows = [["&#963;/<i>d</i>", "PDI (fit)", "PDI (exact)", "&#8730;(PDI/2)",
             "I mean (nm)", "z-average (nm)", "rec. I (nm)", "rec. N (nm)"]]
    for entry in polydispersity_rows():
        rows.append([
            f"{entry['sigma_rel']:.2f}",
            f"{entry['pdi']:.4f}",
            f"{entry['pdi_exact']:.4f}",
            f"{(entry['pdi'] / 2.0) ** 0.5:.3f}",
            f"{entry['intensity_mean_nm']:.1f}",
            f"{entry['z_avg_nm']:.2f}",
            f"{entry['recovered_i_nm']:.0f}",
            f"{entry['recovered_n_nm']:.0f}",
        ])
    story.append(table(rows, [56, 62, 66, 66, 78, 76, 62, 62], s))
    story.append(Paragraph("Table 17: the polydispersity sweep in full. 100 nm mode, no "
                           "aggregation, no noise.", s["caption"]))


def build() -> None:
    s = styles()
    n = numbers_source.quoted_numbers()
    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=letter, leftMargin=54, rightMargin=54,
                            topMargin=54, bottomMargin=54,
                            title=REPORT_TITLE,
                            author="Nanotechnology & Quantum Physics - Assignment 3",
                            subject="Dynamic light scattering simulator: design, measurements "
                                    "and limits")
    story = []
    section_intro(story, s, n)
    section_one(story, s, n)
    section_two(story, s, n)
    section_three(story, s, n)
    section_four(story, s, n)
    section_five(story, s, n)
    section_six(story, s, n)
    section_seven(story, s, n)
    references(story, s)
    appendix_a(story, s)
    appendix_b(story, s)
    appendix_c(story, s)

    doc.build(story, canvasmaker=NumberedCanvas)
    from pypdf import PdfReader
    pages = len(PdfReader(str(PDF_PATH)).pages)
    if COVER_PDF.exists():
        _prepend_cover(PDF_PATH, COVER_PDF, pages + COVER_PAGES)
        pages = len(PdfReader(str(PDF_PATH)).pages)
    print(f"wrote {PDF_PATH.name} ({pages} pages)")


if __name__ == "__main__":
    build()
