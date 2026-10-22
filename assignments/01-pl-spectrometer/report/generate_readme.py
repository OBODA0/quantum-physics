"""
Write README.md: the report in markdown, plus how to run the simulator.

The report part is not retyped. It is read out of `report/generate_pdf_report.py`, the same
source the submitted PDF is built from, so the two cannot drift: headings, paragraphs, figure
captions and the reference list all come from there. The code appendix is deliberately left out.

The surrounding sections come from `docs/readme_template.md`, which holds a single
`<!-- REPORT -->` placeholder where the report is inserted.

Run: python report/generate_readme.py
"""

import ast
import html
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_SOURCE = REPO_ROOT / "report" / "generate_pdf_report.py"
TEMPLATE = REPO_ROOT / "docs" / "readme_template.md"
OUTPUT = REPO_ROOT / "README.md"

# ReportLab inline markup -> markdown, and the entities the report writes by name.
ENTITIES = {
    "&lambda;": "\u03bb", "&micro;": "\u00b5", "&Phi;": "\u03a6", "&epsilon;": "\u03b5",
    "&eta;": "\u03b7", "&sect;": "\u00a7", "&minus;": "\u2212", "&times;": "\u00d7",
    "&prop;": "\u221d", "&nbsp;": " ", "&deg;": "\u00b0",
}

# The report's own figure files, in the order the story uses them. The alt text names the
# question the figure belongs to.
FIGURE_ALT = {
    "part1_instrument_diagram.png": "the instrument the simulator models",
    "part1_combined_overview.png": "the three dye spectra as the simulator produces them",
    "part2_cy3_excitation_sweep.png": "the Cy3 excitation sweep from 400 nm to 700 nm",
    "part3_absorption_overlay.png": "the three absorption bands on one axis",
    "part3_three_dyes_comparison.png": "the three dyes at 450, 550 and 650 nm",
    "part3_single_canvas_overlay.png": "the three dyes on a single graph",
}


def to_markdown(text):
    """Convert one reportlab paragraph into markdown."""
    text = html.unescape(text)
    for entity, character in ENTITIES.items():
        text = text.replace(entity, character)
    text = re.sub(r"<b>(.*?)</b>", r"**\1**", text, flags=re.S)
    text = re.sub(r"<i>(.*?)</i>", r"*\1*", text, flags=re.S)
    text = re.sub(r"<br\s*/?>", "  \n", text, flags=re.I)
    text = re.sub(r"</?(?!sub>|sup>)[a-zA-Z][^>]*>", "", text)
    # every printed DOI becomes a link, as in the PDF
    text = re.sub(r"DOI (10\.[^\s.,;)]+)", r"DOI [\1](https://doi.org/\1)", text)
    return re.sub(r"[ \t]+", " ", text).strip()


def style_of(node):
    """The style name of a Paragraph call, e.g. 'body' from s["body"]."""
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
        return node.slice.value
    return None


def literal(node):
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def figure_markdown(filename, label=None):
    alt = label or FIGURE_ALT.get(filename, Path(filename).stem.replace("_", " "))
    return f"![{alt}](report/report_figures/{filename})"


def extract_report():
    """Walk build_pdf() in order and emit the report as markdown."""
    tree = ast.parse(PDF_SOURCE.read_text(encoding="utf-8"))
    build = next(node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "build_pdf")
    out, figure_number, in_references = [], 0, False

    def plain(text):
        """Drop the bold the report uses to open a heading or a caption."""
        return re.sub(r"\*\*(.*?)\*\*", r"\1", text, flags=re.S)

    def emit(style, text, node=None):
        nonlocal figure_number
        if style == "title" or text is None:
            return
        if style == "h1":
            if text.startswith("Appendix"):
                raise StopIteration
            out.append(f"## {plain(to_markdown(text))}")
        elif style == "h2":
            out.append(f"### {plain(to_markdown(text))}")
        elif style == "caption":
            # the caption is already italic; inner *emphasis* would fight with it
            caption = re.sub(r"\*([^*]+)\*", r"\1", plain(to_markdown(text)))
            out.append(f"*{caption}*")
        elif style == "ref":
            out.append(f"- {to_markdown(text)}")
        else:
            if text.startswith("Figure "):
                figure_number += 1
            out.append(to_markdown(text))

    def walk(statements):
        nonlocal figure_number
        for node in statements:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) \
                    and node.targets[0].id == "references":
                for entry in literal(node.value):
                    emit("ref", entry)
                continue
            if isinstance(node, ast.For):
                # the three-dye panels, or the reference list
                items = literal(node.iter)
                if items is None:
                    continue
                for item in items:
                    if isinstance(item, tuple) and len(item) == 2 and str(item[0]).endswith(".png"):
                        file_name, label = item
                        figure_number += 1
                        out.append(figure_markdown(file_name, label))
                    elif isinstance(item, str):
                        emit("ref", item)
                continue
            if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
                continue
            call = node.value
            if not isinstance(call.func, ast.Attribute) or call.func.attr != "append":
                continue
            argument = call.args[0]
            if isinstance(argument, ast.Call) and isinstance(argument.func, ast.Name):
                if argument.func.id == "Paragraph":
                    text = literal(argument.args[0])
                    style = style_of(argument.args[1]) if len(argument.args) > 1 else "body"
                    if text is not None:
                        emit(style, text)
                elif argument.func.id == "figure":
                    file_name = literal(argument.args[0])
                    figure_number += 1
                    out.append(figure_markdown(file_name))

    try:
        walk(build.body)
    except StopIteration:
        pass
    # one blank line between blocks, never two
    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(out))


def main():
    report = extract_report()
    template = TEMPLATE.read_text(encoding="utf-8")
    if "<!-- REPORT -->" not in template:
        print("FAIL: the template has no <!-- REPORT --> placeholder")
        return 1
    OUTPUT.write_text(template.replace("<!-- REPORT -->", report), encoding="utf-8")
    print(f"wrote {OUTPUT} ({len(report.splitlines())} lines of report)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
