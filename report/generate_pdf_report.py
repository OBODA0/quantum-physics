"""
Build the submission PDF for Assignment 1: PL spectroscopy simulation.

Text, numbers and figures all come from the repository: the numbers from
report/numbers.md (generated), the figures from report/report_figures/
(generated), the references from report/references/AUDIT.md (audited), and the
appendix from the source files themselves, read at build time.

Usage: python report/generate_pdf_report.py     (run from anywhere; paths resolve
against the repository root)
"""

import re
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, Preformatted,
    KeepTogether,
)
from reportlab.pdfgen import canvas

REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_FILENAME = "Assignment_1_PL_Spectroscopy_Simulation_Report.pdf"
PDF_PATH = Path(__file__).resolve().parent / PDF_FILENAME
FIG_DIR = Path(__file__).resolve().parent / "report_figures"
COVER_PDF = Path(__file__).resolve().parent / "cover.pdf"
# The submitted cover page is prepended after the build, so this document numbers itself from
# page 2 and counts one extra page.
COVER_PAGES = 1 if COVER_PDF.exists() else 0


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print 'Page X of Y'."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        # The replay below restores the canvas state page by page, which would also rewind the
        # destination table the internal citation links resolve through. Keep the completed table
        # and put it back before every page is written.
        num_pages = len(self._saved_page_states)
        destinations = dict(self._destinations)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._destinations = destinations
            self.draw_page_decorations(num_pages)
            super().showPage()
        self.__dict__["_destinations"] = destinations
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#555555"))
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "Assignment 1: Photoluminescence (PL) Spectroscopy Simulation")
            self.setStrokeColor(colors.HexColor("#dddddd"))
            self.setLineWidth(0.6)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        self.drawRightString(8.5 * 72 - 54, 34,
                             f"Page {self._pageNumber + COVER_PAGES} of {page_count + COVER_PAGES}")
        self.drawString(54, 34, "Nanotechnology / Quantum Physics - PL Spectrometer Simulation")
        self.setStrokeColor(colors.HexColor("#dddddd"))
        self.setLineWidth(0.6)
        self.line(54, 46, 8.5 * 72 - 54, 46)
        self.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("DocTitle", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=21, leading=25, textColor=colors.HexColor("#1a2a40"), spaceAfter=6),
        "subtitle": ParagraphStyle("DocSubtitle", parent=base["Normal"], fontName="Helvetica",
                                   fontSize=11, leading=15, textColor=colors.HexColor("#4a5568"), spaceAfter=14),
        "h1": ParagraphStyle("Heading1_Custom", parent=base["Normal"], fontName="Helvetica-Bold",
                             fontSize=14, leading=18, textColor=colors.HexColor("#1b365d"),
                             spaceBefore=14, spaceAfter=8, keepWithNext=True),
        "h2": ParagraphStyle("Heading2_Custom", parent=base["Normal"], fontName="Helvetica-Bold",
                             fontSize=11, leading=15, textColor=colors.HexColor("#2c5282"),
                             spaceBefore=10, spaceAfter=5, keepWithNext=True),
        "body": ParagraphStyle("Body_Custom", parent=base["Normal"], fontName="Helvetica",
                               fontSize=9.5, leading=14, textColor=colors.HexColor("#2d3748"), spaceAfter=7),
        "caption": ParagraphStyle("Caption_Custom", parent=base["Normal"], fontName="Helvetica-Oblique",
                                  fontSize=8.5, leading=12, textColor=colors.HexColor("#4a5568"),
                                  alignment=1, spaceAfter=10),
        "ref": ParagraphStyle("Ref_Custom", parent=base["Normal"], fontName="Helvetica",
                              fontSize=8.5, leading=12.5, textColor=colors.HexColor("#2d3748"),
                              leftIndent=20, firstLineIndent=-20, spaceAfter=5),
        "code": ParagraphStyle("Code_Custom", parent=base["Normal"], fontName="Courier",
                               fontSize=7.0, leading=8.8, textColor=colors.HexColor("#1a202c")),
    }


def wrapped_source(text, width=120):
    """Break over-long lines so nothing reaches the page edge.

    No source file in the appendix comes near this width, so code is passed through untouched;
    only the prose paragraphs of the generated number table are wrapped, and those are broken at
    a space so the result stays readable.
    """
    lines = []
    for line in text.splitlines():
        while len(line) > width:
            cut = line.rfind(" ", 1, width + 1)
            if cut <= 0:
                cut = width
            lines.append(line[:cut])
            line = "    " + line[cut:].lstrip()
        lines.append(line)
    return "\n".join(lines)


def figure(name, width, height):
    path = FIG_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"figure missing: {path}")
    return Image(str(path), width=width, height=height)


LINK_COLOR = "#1155cc"
REPO_URL = "https://github.com/OBODA0/pl-spectrometer-simulator"

DOI_RE = re.compile(r"DOI\s+(10\.\d{4,9}/\S+)")


def link_dois(text):
    """Make a printed DOI clickable, so every source is one click away."""
    def replace(match):
        raw = match.group(1)
        doi = raw.rstrip(".,;)")
        trailing = raw[len(doi):]  # the punctuation belongs to the sentence, not the link
        return '<link href="https://doi.org/{d}" color="{c}">DOI {d}</link>{t}'.format(
            d=doi, c=LINK_COLOR, t=trailing)
    return DOI_RE.sub(replace, text)


def extract_markdown_sections(text, wanted):
    """Keep only the named '###' sections of a markdown file (the ones the report cites)."""
    kept, current = [], None
    for line in text.splitlines():
        if line.startswith("### "):
            current = line[:7] in wanted
        elif line.startswith("## "):
            current = None
        if current:
            kept.append(line)
    return "\n".join(kept)


class ReferenceParagraph(Paragraph):
    """A reference entry, with its DOI made clickable."""

    def __init__(self, text, style=None, **kwargs):
        # ReportLab re-constructs a paragraph with text=None when it splits one across pages.
        super().__init__(link_dois(text) if text is not None else None, style, **kwargs)


def _count_pages(path):
    from pypdf import PdfReader
    return len(PdfReader(str(path)).pages)


def _prepend_cover(report_path, cover_path, page_count):
    """Put the submitted cover in front of the report, carrying the report's own footer.

    The cover is used exactly as submitted; only the footer line is added to it, so the
    page numbering runs unbroken from page 1 to the last page.
    """
    import io

    from pypdf import PdfReader, PdfWriter

    overlay_buffer = io.BytesIO()
    overlay = canvas.Canvas(overlay_buffer, pagesize=letter)
    overlay.setFont("Helvetica", 9)
    overlay.setFillColor(colors.HexColor("#555555"))
    overlay.drawString(54, 34, "Nanotechnology / Quantum Physics - PL Spectrometer Simulation")
    overlay.drawRightString(8.5 * 72 - 54, 34, f"Page 1 of {page_count}")
    overlay.setStrokeColor(colors.HexColor("#dddddd"))
    overlay.setLineWidth(0.6)
    overlay.line(54, 46, 8.5 * 72 - 54, 46)
    overlay.showPage()
    overlay.save()
    overlay_buffer.seek(0)

    front = PdfReader(str(cover_path)).pages[0]
    front.merge_page(PdfReader(overlay_buffer).pages[0])

    writer = PdfWriter()
    writer.add_page(front)
    for page in PdfReader(str(report_path)).pages:
        writer.add_page(page)
    temporary = report_path.with_suffix(".with-cover.pdf")
    with open(temporary, "wb") as handle:
        writer.write(handle)
    temporary.replace(report_path)


def build_pdf():
    s = styles()
    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=letter, leftMargin=54, rightMargin=54,
                            topMargin=54, bottomMargin=54,
                            title="Assignment 1: Photoluminescence (PL) Spectroscopy Simulation",
                            subject="PL spectrometer simulation: design, excitation sweep, multi-dye "
                                    "comparison",
                            author="Nanotechnology & Quantum Physics - Assignment 1")
    story = []

    # ---------------------------------------------------------------- title
    story.append(Paragraph("Assignment 1: Photoluminescence (PL) Spectroscopy Simulation", s["title"]))
    story.append(Paragraph("<b>Course:</b> Nanotechnology &amp; Quantum Physics &nbsp;|&nbsp; "
                           "<b>Topic:</b> instrument simulation, Kasha's rule, multi-dye spectroscopy", s["subtitle"]))
    story.append(Paragraph("<b>Students:</b> Mohamed Oboda (2111011090) &nbsp;|&nbsp; "
                           "Mert SOLMAZ (2311011039)", s["subtitle"]))

    meta = [
        [Paragraph("<b>Simulator</b>", s["body"]),
         Paragraph("Xenon arc lamp, excitation monochromator, harmonic filter, sample, detection "
                   "monochromator, silicon photodiode", s["body"])],
        [Paragraph("<b>Sample database</b>", s["body"]),
         Paragraph("Cy3, Cy5, methylene blue - absorption and emission bands digitized from vendor "
                   "datasheets, PhotochemCAD and OMLC measurements", s["body"])],
        [Paragraph("<b>Physics</b>", s["body"]),
         Paragraph("Beer-Lambert absorption, fluorescence quantum yield, Kasha's rule, monochromator "
                   "passband convolution, detector responsivity, stray excitation light", s["body"])],
        [Paragraph("<b>Built with</b>", s["body"]),
         Paragraph("Google Antigravity and a customized pi coding agent, using the DeepSeek v4.1 "
                   "Flash and Gemini models", s["body"])],
        [Paragraph("<b>Repository</b>", s["body"]),
         Paragraph('<link href="{url}" color="{c}">{url}</link> - the code, the data and the checks '
                   "behind every figure and number in this report".format(url=REPO_URL, c=LINK_COLOR),
                   s["body"])],
        [Paragraph("<b>Source of numbers</b>", s["body"]),
         Paragraph("every value quoted below is generated by the project code into "
                   "<i>report/numbers.md</i>; the source and confidence behind every dye value is the "
                   "data-sources appendix of this report", s["body"])],
    ]
    table = Table(meta, colWidths=[110, 394])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f7fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    # ================================================================ PART 1
    story.append(Paragraph("1. Design of the PL spectrometer and the three dye spectra (25%)", s["h1"]))
    story.append(figure("part1_instrument_diagram.png", 468, 201))
    story.append(Paragraph(
        "<b>Figure 1:</b> the instrument the simulator models. Every box is a module in the appendix "
        "code: the lamp spectrum (<i>sources.py</i>), the monochromators and harmonic filter "
        "(<i>sources.py</i>), the dye database (<i>samples.py</i>, <i>reference.py</i>), the detector "
        "(<i>detector.py</i>) and the scan that connects them (<i>spectrometer.py</i>). The three user "
        "settings act where the drawing shows them. The instrument, the model and the analysis code "
        "were built with the AI tools named on the title page, working from the block diagram of the "
        "class session; every physical assumption, source datum and check is documented in the "
        "repository.", s["caption"]))

    story.append(Paragraph("<b>1.1 The design.</b>", s["h2"]))
    story.append(Paragraph(
        "A xenon arc lamp provides a broad continuum across the visible and near infrared. The "
        "excitation monochromator isolates the excitation wavelength &lambda;<sub>exc</sub> with a 5 nm "
        "passband; a long-pass harmonic filter removes the second-order grating output below 400 nm, so "
        "the sample is not also illuminated at &lambda;<sub>exc</sub>/2 from second-order diffraction. "
        "The beam crosses a 1 cm "
        "cuvette holding the dye. The emitted light is collected and scanned by a second monochromator, "
        "2 nm passband, across the detection range [&lambda;<sub>min</sub>, &lambda;<sub>max</sub>] in "
        "steps of &Delta;&lambda;, and detected by a silicon photodiode whose responsivity "
        "<i>R</i>(&lambda;) grows through the visible and cuts off near 1100 nm. A small fraction of the "
        "excitation light reaches the detector as stray light; the figures that include it use 0.1 % of "
        "the excitation power, which is what a double monochromator with a harmonic filter is expected "
        "to leave. "
        "Intensities are relative: the model reproduces spectra and relative intensities, not absolute "
        "radiometric values.", s["body"]))
    story.append(Paragraph(
        "What the sample does is described by two bands per dye, absorption and emission, taken from "
        "measured data rather than from ideal Gaussians. The absorbed fraction follows the "
        "Beer-Lambert law, so the emitted power is "
        "<i>P</i><sub>exc</sub>(&lambda;<sub>exc</sub>) &times; [1 &minus; "
        "10<sup>&minus;A(&lambda;<sub>exc</sub>)</sup>] &times; &Phi;<sub>f</sub>, with "
        "<i>A</i> = &epsilon;&middot;<i>c</i>&middot;<i>l</i>. The emission band shape itself is "
        "independent of the excitation wavelength, which is the subject of section 2.", s["body"]))

    story.append(Paragraph("<b>1.2 Sample database and baseline spectra.</b>", s["h2"]))
    story.append(Paragraph(
        "Cy3 and Cy5 are the sulfoindocyanine dyes introduced as fluorescent labelling reagents by "
        "[3], and the model uses the vendor maxima, 550 nm for Cy3 and 649 nm for Cy5 [9]. The same "
        "vendor documentation names the lines the fluorescence literature conventionally uses, the "
        "633 nm helium-neon and 647 nm krypton-argon lines [9]. Methylene "
        "blue is a phenothiazinium dye whose excited state is quenched "
        "both by internal conversion and by intersystem crossing [4, 6], which is why its quantum "
        "yield is the lowest of the three: the 0.04 that is often quoted for it is the ethanol value, "
        "and the aqueous value used here is the 0.02 reference-standard convention declared in "
        "section 4. The database holds the three dyes named in the task, at "
        "the same concentration "
        "(1 &micro;mol/L in a 1 cm cuvette, so <i>A</i> = &epsilon;<i>c</i><i>l</i> differs between "
        "them: 0.150 for Cy3, 0.250 for Cy5, 0.067 for methylene blue). Each dye was excited at its own "
        "absorption maximum. The spectra below are the instrument output, not idealised curves: they "
        "carry the lamp and monochromator throughput, the 2 nm detection passband and the detector "
        "responsivity. Their peaks fall where the measured bands peak - 568.0 nm for Cy3, 668.0 nm for "
        "Cy5 and 685.0 nm for methylene blue on the digitized curves, read as 686 nm on the 1 nm scan "
        "grid - against the vendor maxima of 570, 670 and 685 nm: 2 nm for Cy3 and Cy5 and none at all "
        "for methylene blue. That difference is in the source data, not in the instrument: a symmetric "
        "passband widens a band without moving its centre.", s["body"]))
    story.append(figure("part1_combined_overview.png", 504, 151))
    story.append(Paragraph(
        "<b>Figure 2:</b> simulated PL spectra of Cy3 (&lambda;<sub>exc</sub> = 550 nm), Cy5 "
        "(649 nm) and methylene blue (664 nm), all at 1 &micro;mol/L in 1 cm, with the stray excitation "
        "line shown in each panel. Each panel has its own current scale; the peak absorbances differ by "
        "a factor of 3.7.", s["caption"]))
    for name, label in (("part1_cy3.png", "Cy3"), ("part1_cy5.png", "Cy5"),
                        ("part1_methylene-blue.png", "methylene blue")):
        story.append(figure(name, 296, 189))
    story.append(Paragraph(
        "<b>Figure 3:</b> the same three measurements at full scale, one per dye - the screen "
        "captures the task asks for, taken as the simulator's own output written straight to an image "
        "file, with no post-processing: "
        "<i>A</i>(&lambda;<sub>exc</sub>) and <i>A</i><sub>peak</sub> and &Phi;<sub>f</sub> are printed "
        "in each title. Peak currents: Cy3 5.2 &times; 10<sup>-3</sup>, Cy5 6.8 &times; "
        "10<sup>-2</sup>, methylene blue 1.6 &times; 10<sup>-3</sup> (relative units).", s["caption"]))
    story.append(PageBreak())

    # ================================================================ PART 2
    story.append(Paragraph("2. Excitation wavelength from 400 nm to 700 nm (50%)", s["h1"]))
    story.append(Paragraph(
        "<b>2.1 What was done.</b> Cy3 was chosen because its absorption (550 nm) and emission "
        "(570 nm) both sit comfortably inside the detector's useful range and it is the best documented "
        "of the three dyes. The excitation wavelength was swept from 400 nm to 700 nm in 2 nm steps "
        "while the whole emission band was recorded with the detection monochromator set to "
        "450-900 nm in 1 nm steps, and the plotted intensity is the integral of the "
        "emitted band over the detection range, not the height at one fixed wavelength: a fixed window "
        "stops watching the dye and starts watching the window as soon as &lambda;<sub>exc</sub> moves "
        "past it.", s["body"]))
    story.append(figure("part2_cy3_excitation_sweep.png", 504, 195))
    story.append(Paragraph(
        "<b>Figure 4:</b> (left) emission spectra for six excitation wavelengths, all peaking at "
        "568.0 nm with 28.0 nm FWHM; (right) the integrated PL intensity across the sweep, the model "
        "prediction <i>P</i><sub>exc</sub>(&lambda;)[1 &minus; "
        "10<sup>&minus;A(&lambda;)</sup>]&Phi;<sub>f</sub>, and the absorbance normalised to its own "
        "maximum. The two model curves lie on top of each other; the absorbance differs slightly "
        "because the intensity carries the xenon lamp spectrum as a weight. The left panel is the "
        "detected signal including stray light, so each curve carries a small spike at its own "
        "excitation wavelength; the sweep on the right uses the fluorescence alone, so stray light "
        "cannot contaminate it.", s["caption"]))

    story.append(Paragraph("<b>2.2 What is observed.</b>", s["h2"]))
    story.append(Paragraph(
        "1. <b>The emission band does not move.</b> Across every excitation wavelength that produces a "
        "signal the peak stays at 568.0 nm and the FWHM at 28.0 nm on the 1 nm scan grid, 28.6 nm on "
        "the digitized band, and this is Kasha's rule in the "
        "data rather than in prose. The overlay in Figure 4 shows six spectra between 470 nm and "
        "560 nm; the sweep itself is non-zero from about 452 nm to 588 nm.<br/>"
        "2. <b>The height follows the absorbed light.</b> The measured integrated intensity "
        "reproduces <i>P</i><sub>exc</sub>(&lambda;)[1 &minus; "
        "10<sup>&minus;A(&lambda;)</sup>]&Phi;<sub>f</sub> to within 10<sup>-16</sup> of full scale, "
        "the numerical noise of the comparison. That agreement is a check on the implementation - the "
        "lamp spectrum, the two monochromator passbands, the detector responsivity and the integration "
        "all have to be right to reach it - and it is not evidence about the dye, which is why 2.3 says "
        "so again. The curve rises towards the absorption maximum and collapses when the absorption "
        "does.<br/>"
        "3. <b>Below about 450 nm the model reads zero absorption.</b> The strip it uses begins at "
        "450 nm, and the same dye record's wider excitation strip gives 1.8 % of the peak at 450 nm "
        "and 0.2 % at 400 nm - absorbed fractions of 0.6 % and 0.07 % at the concentration used here - "
        "while the documented methanol spectrum gives 4.3 % at 450 nm, which is 1.5 % absorbed. All of "
        "that is far below what the figure can show, but none of it is zero (section 3.3 of the "
        "generated number table). So this end is a limit of the tabulated range "
        "rather than of the physics. (The 400 nm harmonic filter does not enter here: it only blocks "
        "wavelengths below 400 nm, which the sweep does not use.)<br/>"
        "4. <b>Above about 590 nm the simulation returns exactly zero</b>, for two different reasons. "
        "The strip the model uses was digitized over 450-590 nm, so between 590 and about 610 nm this "
        "is a limit of the data: the same record's corrected excitation strip runs to 649 nm and reads "
        "0.38 % of the peak at 600 nm and 0.02 % at 610 nm. From about 620 nm to 700 nm the curve is "
        "flat because the dye is, not because the data stops - that strip returns zero there, and the "
        "documented methanol spectrum of the same chromophore, which does reach 700 nm, reads 0.20 % at "
        "650 nm, an absorbed fraction of 0.07 % at the concentration used here (both in section 3.3 of "
        "the generated number table). A real instrument "
        "would record a weak, not vanishing, signal near 600 nm, and nothing measurable beyond it.<br/>"
        "5. <b>Stray light tracks the excitation wavelength.</b> With stray light enabled, the "
        "scattered line sits exactly at &lambda;<sub>exc</sub> and moves with it, which is why the "
        "harmonic filter and the second monochromator exist.", s["body"]))

    story.append(Paragraph("<b>2.3 Do the observations fit the literature?</b>", s["h2"]))
    story.append(Paragraph(
        "<b>Yes, and the reason is a separation of timescales.</b> Absorption promotes the molecule to "
        "higher vibrational levels of the first excited singlet state, or to higher electronic states. "
        "Internal conversion and vibrational relaxation then remove that excess energy in about "
        "10<sup>-13</sup>-10<sup>-12</sup> s, the range the fluorescence literature gives for those "
        "two processes [2, &sect;1.4.2], while fluorescence from Cy3 takes of order 0.2-2 ns [5]. The "
        "rule itself is Kasha's, stated for states in 1950 [1]. Emission is therefore two to four "
        "orders of magnitude slower than the "
        "relaxation, so every "
        "excited molecule emits from the same thermalized level, S<sub>1</sub>(v = 0), whatever photon "
        "it absorbed. The emission spectrum is therefore fixed in shape, position and width, and only "
        "the number of excited molecules - that is, the absorbed light - changes with "
        "&lambda;<sub>exc</sub>. The two dyes in our own database illustrate the same chain-length "
        "argument: Cy3 is a trimethine cyanine absorbing at 550 nm and Cy5 a pentamethine at 649 nm, so "
        "two extra methine units shift the band by 99 nm in our own data, which is the free-electron "
        "model of the cyanine chain in practice [7]. That is Kasha's rule as Kasha stated it for "
        "states [1] and as "
        "Lakowicz states it for wavelength, in the section whose title says exactly that [2, "
        "&sect;1.3.2].", s["body"]))
    story.append(Paragraph(
        "<b>The intensity behaviour is the excitation spectrum, with one honest caveat.</b> The "
        "absorbed photon rate follows Beer-Lambert, so "
        "<i>I</i><sub>PL</sub> &prop; <i>I</i><sub>0</sub>(&lambda;<sub>exc</sub>)[1 &minus; "
        "10<sup>&minus;&epsilon;(&lambda;<sub>exc</sub>)<i>c</i><i>l</i></sup>]&Phi;<sub>f</sub>, which "
        "for a dilute sample is &prop; &epsilon;(&lambda;<sub>exc</sub>)&Phi;<sub>f</sub>. The curve in "
        "Figure 4 (right) therefore tracks the absorption band, but the lamp spectrum "
        "<i>I</i><sub>0</sub>(&lambda;) sits inside that expression, so the two curves are similar "
        "rather than identical - the residual difference visible in the figure is the xenon lamp, not "
        "an error. Correcting for <i>I</i><sub>0</sub>(&lambda;) is what an instrument does when it "
        "records a quantum-corrected excitation spectrum.", s["body"]))
    story.append(Paragraph(
        "<b>A note on what this simulation can and cannot demonstrate.</b> The invariance of the band "
        "with &lambda;<sub>exc</sub> is built into the model, because that is what the timescale "
        "argument above requires. What the sweep verifies is the consequence: that the absorbed "
        "fraction, and nothing else, depends on the excitation wavelength, and that the resulting "
        "intensity agrees with the Beer-Lambert prediction to machine precision. In that sense the "
        "simulator is a test of the consequences of Kasha's rule rather than a discovery of it. The "
        "assumption is also falsifiable, and cheaply so: a drift of 0.05 nm of emission peak per 1 nm "
        "of excitation wavelength would put the peak at 563.0 nm under 450 nm excitation and 575.5 nm "
        "under 700 nm, so the left panel of Figure 4 would be a fan of six different peaks instead of "
        "six curves lying on one another. Nothing in the sweep would look the same.", s["body"]))
    story.append(Paragraph(
        "<b>The Stokes shift.</b> Absorption and emission maxima are separated by 20 nm, which is "
        "638 cm<sup>-1</sup> calculated from the quoted 550 and 570 nm values (the digitized curve "
        "peaks, 554 and 568 nm, give 14 nm and 445 cm<sup>-1</sup>; the figure is quoted from the "
        "sourced maxima). The shift is the Franck-Condon and solvent reorganisation energy, and it is "
        "why the emission sits at longer wavelength than the absorption, never at shorter.", s["body"]))
    story.append(PageBreak())

    # ================================================================ PART 3
    story.append(Paragraph("3. The three dyes on one graph at 450, 550 and 650 nm (25%)", s["h1"]))
    story.append(Paragraph(
        "<b>3.1 The colours come from the absorption bands.</b> All three dyes were simulated at the "
        "same concentration, 1 &micro;mol/L in a 1 cm cuvette, so their peak absorbances differ by their "
        "extinction coefficients: 0.150 (Cy3), 0.250 (Cy5) and 0.067 (methylene blue). \"The same "
        "concentration\" is not \"the same absorbance\" - that is the first thing to say about this "
        "question. The second is that each dye sits at a different point of its own absorption curve, "
        "shown in Figure 5.", s["body"]))
    story.append(figure("part3_absorption_overlay.png", 470, 251))
    story.append(Paragraph(
        "<b>Figure 5:</b> the three absorption bands, each normalised to its own maximum, with the "
        "three excitation wavelengths marked. At 550 nm Cy3 is near its maximum (its curve peaks at "
        "554 nm) while Cy5 and methylene "
        "blue are on their rising edges; at 650 nm Cy5 and methylene blue absorb while Cy3 has nothing "
        "left above its band.", s["caption"]))
    story.append(figure("part3_three_dyes_comparison.png", 504, 164))
    story.append(Paragraph(
        "<b>Figure 6:</b> the same graph for each excitation wavelength - 450 nm (left), 550 nm "
        "(centre), 650 nm (right) - on one shared scale in relative units, which is what makes the "
        "comparison meaningful. The legend gives <i>A</i>(&lambda;<sub>exc</sub>) for each curve in that "
        "panel.", s["caption"]))
    story.append(figure("part3_single_canvas_overlay.png", 470, 266))
    story.append(Paragraph(
        "<b>Figure 7:</b> all nine spectra on a single canvas, with the peak current of every curve "
        "printed beside it. The empty-looking curves are not an error: they are the dyes that do not "
        "absorb at that wavelength.", s["caption"]))

    story.append(Paragraph("<b>3.2 Why the peaks are not the same.</b>", s["h2"]))
    story.append(Paragraph(
        "The peak height is a product of four terms, and the first is the one the question is looking "
        "for:", s["body"]))
    story.append(Paragraph(
        "<b>(1) How much light the dye absorbs at &lambda;<sub>exc</sub>.</b> "
        "<i>A</i>(&lambda;<sub>exc</sub>) = &epsilon;(&lambda;<sub>exc</sub>)<i>c</i><i>l</i>, and "
        "&epsilon; at a given wavelength depends entirely on where that wavelength falls in the dye's "
        "own band. At 550 nm Cy3 absorbs 28.0 % of the incident light while Cy5 absorbs 2.81 % and "
        "methylene blue 1.19 %. At 650 nm it is Cy5 that absorbs 43.4 %, methylene blue 11.9 %, and Cy3 "
        "nothing in the model: its tabulated band ends at 590 nm.<br/>"
        "<b>(2) The quantum yield.</b> Of the photons absorbed, only the fraction &Phi;<sub>f</sub> is "
        "emitted: 0.28 for Cy5, 0.04 for Cy3, 0.02 for methylene blue in water. This is why the "
        "550 nm panel is not lopsided in favour of Cy3: Cy3 absorbs ten times more light than Cy5 "
        "there, yet the two peaks come out within 12 % of each other, because Cy5 converts absorbed "
        "photons into fluorescence seven times more efficiently.<br/>"
        "<b>(3) The detector's wavelength dependence.</b> A silicon photodiode of a given quantum "
        "efficiency has a responsivity proportional to wavelength [8], and this one is about a third "
        "higher at methylene blue's emission (686 nm) than at Cy3's (568 nm), so equal emitted power at "
        "those two wavelengths does not give equal photocurrent.<br/>"
        "<b>(4) The width of the emission band.</b> Measured on the digitized bands, Cy3, Cy5 and "
        "methylene blue are 28.6, 33.4 and 48.6 nm wide (the simulated curves read 28, 32 and 47 nm "
        "on a 1 nm grid); a published Cy5 bandwidth, 37.4 nm for an aptamer conjugate [10], is 4 nm "
        "wider than the 33.4 nm measured here, and no published bandwidth for Cy3 was found at all. This width is not a further factor inside the peak heights above: "
        "the model draws each band normalized to its own maximum, so a peak here is set by the "
        "absorbed fraction and the quantum yield, and the width shows up in the integral. It does "
        "enter the moment the comparison is made at equal emitted power, which is how a quantum yield "
        "is normally measured: the same photon budget spread over a wider band gives a lower peak, and "
        "methylene blue is the broadest of the three as well as the weakest emitter.", s["body"]))
    story.append(Paragraph(
        "<b>One honest caveat about 450 nm.</b> There the model returns exactly zero absorption for "
        "Cy3, because its tabulated band begins at 450 nm and reads zero at that edge, against 0.24 % "
        "for Cy5 and 0.20 % for methylene blue. The wider strip in the same record puts Cy3 near 0.6 % "
        "at 450 nm (section 3.3 of the generated number table), which is more than either of the other "
        "two - so the left panel of Figure 6 is nearly empty because all three dyes are effectively "
        "transparent there, not because the simulation failed. The comparison the question is really "
        "asking about is the 550 nm and 650 nm panels, where the dyes that absorb are also the dyes "
        "that light up.", s["body"]))
    story.append(Paragraph(
        "<b>Peak currents for the record</b> (relative units, 1 &micro;mol/L, 1 cm): at 450 nm Cy3 "
        "0.00000, Cy5 0.00040, methylene blue 0.00002; at 550 nm Cy3 0.00523, Cy5 0.00468, methylene "
        "blue 0.00015; at 650 nm Cy3 0.00000, Cy5 0.06824, methylene blue 0.00138.", s["body"]))
    story.append(PageBreak())

    # ============================================================ references
    story.append(Paragraph("4. References", s["h1"]))
    story.append(Paragraph(
        "Every entry below was checked to resolve, and each claim is attached to the work that carries "
        "it. Where a DOI circulates in a wrong form, the corrected one is given. Where a work is "
        "closed-access and could not be read beyond its table of contents, the citation points to the "
        "section whose stated subject carries the claim, and the claim is phrased as textbook content "
        "rather than as a quotation from a page that was not read.", s["body"]))

    references = [
        "[1] M. Kasha, \"Characterization of electronic transitions in complex molecules\", "
        "<i>Discussions of the Faraday Society</i> <b>9</b> (1950) 14-19. DOI 10.1039/DF9500900014. "
        "(The rule stated for states.)",

        "[2] J. R. Lakowicz, <i>Principles of Fluorescence Spectroscopy</i>, 3rd ed., Springer, 2006. "
        "DOI 10.1007/978-0-387-46312-4. (&sect;1.3.2, \"Emission Spectra Are Typically Independent of "
        "the Excitation Wavelength\", p. 7; &sect;1.4.2, \"Timescale of Molecular Processes in "
        "Solution\", p. 12.)",

        "[3] R. B. Mujumdar, L. A. Ernst, S. R. Mujumdar, C. J. Lewis and A. S. Waggoner, \"Cyanine dye "
        "labeling reagents: sulfoindocyanine succinimidyl esters\", <i>Bioconjugate Chemistry</i> "
        "<b>4</b> (1993) 105-111. DOI 10.1021/bc00020a001. (Introduction of the sulfoindocyanine "
        "succinimidyl esters; the vendor values for the maxima used here are in [9].)",

        "[4] E. M. Tuite and J. M. Kelly, \"Photochemical interactions of methylene blue and analogues "
        "with DNA and other biological substrates\", <i>Journal of Photochemistry and Photobiology B: "
        "Biology</i> <b>21</b> (1993) 103-124. DOI 10.1016/1011-1344(93)80173-7. (Excited-state "
        "behaviour of methylene blue.)",

        "[5] R. Berrocal-Martin et al., <i>Journal of Physical Chemistry B</i> <b>129</b> (2025) "
        "11626-11635. DOI 10.1021/acs.jpcb.5c03845. (Fluorescence lifetimes of sulfo-Cy3 on DNA "
        "constructs in Tris buffer, read from the paper's own text: about 0.2 ns for the free dye, "
        "with components of 0.6-1.1 ns and 1.5-2.5 ns.)",

        "[6] L. M. Moreira, J. P. Lyon, A. P. Romani, D. Severino, M. R. Rodrigues and "
        "H. P. M. de Oliveira, \"Phenotiazinium dyes as photosensitizers in photodynamic therapy: "
        "spectroscopic properties and photochemical mechanisms\" (title and spelling as printed), in "
        "<i>Advanced Aspects of Spectroscopy</i>, InTech, 2012, ch. 14. DOI "
        "10.5772/48087. (Methylene blue: the singlet state decays by internal conversion and by "
        "intersystem crossing, with a triplet yield of 0.52, which is why its quantum yield is the "
        "lowest of the three.)",

        "[7] H. Kuhn, \"A quantum-mechanical theory of light absorption of organic dyes and similar "
        "compounds\", <i>Journal of Chemical Physics</i> <b>17</b> (1949) 1198-1212. DOI "
        "10.1063/1.1747143. (Free-electron model of the cyanine chain, eq. (8); the report uses it for "
        "the chain-length argument and quotes the shift from our own data - 550 nm for the trimethine "
        "Cy3 against 649 nm for the pentamethine Cy5.)",

        "[8] Hamamatsu Photonics, \"Si photodiodes\", technical note KSPD9001E04, sec. 2-3, eq. (2-3), "
        "which prints the quantum-efficiency form QE = (S &times; 1240 / &lambda;) &times; 100 %; "
        "equivalently the responsivity of a detector of quantum efficiency &eta; is "
        "&eta;&lambda;[&micro;m]/1.24 A/W. A technical note has no DOI of its own; for the same relation "
        "from a citable source, RP Photonics, \"Responsivity\", DOI 10.61835/xal, an article on "
        "responsivity and how it relates to quantum efficiency.",

        "[9] Dye spectra and molar extinction coefficients, from the vendor documentation kept in "
        "<i>data/raw/</i>. Cy3: the Cytiva Cy3 instructions-for-use sheet and the Cy3 maleimide "
        "specification sheet 28954681, which print absorbance maximum 550 nm, emission maximum "
        "570 nm, and 150 000 M<sup>-1</sup>cm<sup>-1</sup> at 552 nm in the labelling formula. Cy5: "
        "the maleimide sheet 28954683, which prints 649 nm, 250 000 M<sup>-1</sup>cm<sup>-1</sup> at "
        "650 nm, and 670 nm. Methylene blue: the PhotochemCAD record PSW009, whose own reference is "
        "JACS Au (DOI 10.1021/jacsau.5c01463), and the OMLC/Prahl measured spectrum. The same vendor "
        "documentation names the conventional Cy5 excitation lines, the 633 nm helium-neon and "
        "647 nm krypton-argon lines. The full source table, with a confidence for each value and the "
        "raw files, is the data-sources appendix of this report, and the raw files themselves are in "
        "<i>data/raw/</i>.",

        "[10] A published Cy5 emission bandwidth, used only as a cross-check on the width measured here: "
        "<i>Biosensors</i> <b>13</b> (2023) 876, Table 2, DOI 10.3390/bios13090876 (open access, "
        "PMC10526137), which gives an Aptamer-Cy5 emission maximum at 665.0 nm with a 37.4 nm FWHM.",
    ]
    for reference in references:
        story.append(ReferenceParagraph(reference, s["ref"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Declared limitations.</b> No primary source was found for the widely repeated methylene "
        "blue extinction coefficient of 95,000 M<sup>-1</sup>cm<sup>-1</sup>, so it is not used: the "
        "pack carries 67,000 (PhotochemCAD, water), 74,028 (OMLC) and 107,800 for the deconvoluted "
        "monomer. The quantum yield of methylene blue in water, 0.02, is the value used in "
        "photodynamic-therapy work, where it serves as a reference standard; the measured value is "
        "0.04 in ethanol (the PhotochemCAD record I12 kept in <i>data/raw/</i>), and some readable "
        "sources also quote 0.04 for water, so the range is 0.02-0.04 rather than a single number. The emission bandwidths quoted here are measured on the digitized bands rather than "
        "taken from the literature; a published Cy5 emission FWHM of 37.4 nm [10], for an aptamer "
        "conjugate, is 4 nm wider than the 33.4 nm measured here, and no published bandwidth for Cy3 "
        "was found at all. The FPbase records from which the Cy3 and Cy5 bands are digitized do "
        "not state their provenance; the fully documented curves for the same chromophores are the "
        "PhotochemCAD methanol spectra kept in <i>data/raw/</i>. Section 3.1 of the generated number "
        "table tests how much any of this could move the result: re-run at the top of both unverified "
        "ranges at once, methylene blue reaches 0.00429 at 650 nm against Cy5's 0.06824 and Cy3's "
        "0.00523 at 550 nm, so the ranking between the three dyes does not depend on the numbers that "
        "could not be sourced.", s["body"]))
    story.append(PageBreak())

    # ============================================================== appendix
    story.append(Paragraph("Appendix: source code and data sources", s["h1"]))
    story.append(Paragraph(
        "The files below are read from the repository at build time, so the appendix cannot drift from "
        "the code that produced the figures. Every result in this report is reproducible with "
        "<i>uv sync</i> followed by the two generator scripts listed here. The first file is the source "
        "and confidence behind every dye value, and the second is the generated number table this "
        "report quotes its sections 3.1 and 3.3 from; both are what section 4 and the title page point "
        "at.", s["body"]))

    code_files = [
        ("report/data_provenance.md",
         "Source and confidence behind every dye value, and what could not be verified"),
        ("report/numbers.md",
         "The generated number table: the two sections this report cites (3.1 and 3.3); the "
         "whole table is report/numbers.md in the repository"),
        ("plsim/bands.py", "Band shapes: Gaussian model and tabulated measured bands"),
        ("plsim/sources.py", "Excitation arm: xenon lamp, monochromator, harmonic filter"),
        ("plsim/samples.py", "Sample database, absorbance, concentration"),
        ("plsim/reference.py", "Loader for the measured reference band data"),
        ("plsim/detector.py", "Silicon photodiode and its responsivity curve"),
        ("plsim/spectrometer.py", "The instrument: one PL scan end to end"),
        ("plsim/analysis.py", "Excitation scans and their model check"),
        ("plsim/plot.py", "Figure rendering"),
        ("plsim/cli.py", "Command line interface (the user settings)"),
        ("plsim/__init__.py", "Package interface"),
        ("report/settings.py", "The optical conditions shared by every figure and number"),
        ("report/generate_assignment_figures.py", "The figures for questions 1, 2 and 3"),
        ("report/generate_numbers.py", "The number table this report quotes from"),
        ("tests/test_simulator.py", "The checks behind the physics claims"),
    ]
    for rel_path, desc in code_files:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            raise FileNotFoundError(f"appendix source missing: {full_path}")
        story.append(Paragraph(f"<b>File: {rel_path}</b> - <i>{desc}</i>", s["h2"]))
        # Chunks keep a page break from leaving one or two lines stranded on a page
        # of their own; short tails are merged into the previous chunk.
        text = full_path.read_text(encoding="utf-8")
        if rel_path == "report/numbers.md":
            text = extract_markdown_sections(text, {"### 3.1", "### 3.3"})
        lines = wrapped_source(text).split("\n")
        chunk_size = 55
        chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
        if len(chunks) > 1 and len(chunks[-1]) < 6:
            chunks[-2].extend(chunks.pop())
        for chunk in chunks:
            story.append(KeepTogether(Preformatted("\n".join(chunk), s["code"])))
        story.append(Spacer(1, 10))

    doc.build(story, canvasmaker=NumberedCanvas)
    page_count = _count_pages(PDF_PATH) + COVER_PAGES
    if COVER_PDF.exists():
        _prepend_cover(PDF_PATH, COVER_PDF, page_count)
    print(f"PDF built: {PDF_PATH} ({page_count} pages)")


if __name__ == "__main__":
    build_pdf()
