"""Render LaTeX math to transparent PNGs for the PDF report.

ReportLab has no TeX engine, so every formula is typeset by matplotlib's mathtext (a
TeX-subset interpreter, DejaVu fonts to match the body text) and embedded as an image.
Rendering is cached in report/math_cache/, so a rebuild only renders new formulas.
"""

from __future__ import annotations

import hashlib
import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
from PIL import Image as PILImage

CACHE = pathlib.Path(__file__).resolve().parent / "math_cache"
DPI = 600
_PAD_PX = 4


def _baseline_offset(fontsize: float) -> tuple[float, float]:
    """Crop box padding around the glyphs, plus the distance from the box bottom to the baseline."""
    return _PAD_PX, _PAD_PX


def _render(latex: str, fontsize: float) -> pathlib.Path:
    key = hashlib.sha1(f"{latex}|{fontsize}|{DPI}".encode()).hexdigest()[:16]
    path = CACHE / f"{key}.png"
    if path.exists():
        return path
    CACHE.mkdir(exist_ok=True)
    figure = plt.figure(figsize=(7.0, 0.7), dpi=DPI)
    text = figure.text(0.02, 0.5, latex, fontsize=fontsize, ha="left", va="baseline")
    figure.canvas.draw()
    extent = text.get_window_extent(figure.canvas.get_renderer())
    baseline = 0.5 * figure.bbox.height
    bottom = min(extent.y0, baseline)
    top = max(extent.y1, baseline)
    # bbox_inches is expressed in inches, while get_window_extent returns pixels
    box = Bbox.from_extents((extent.x0 - _PAD_PX) / DPI, (bottom - _PAD_PX) / DPI,
                            (extent.x1 + _PAD_PX) / DPI, (top + _PAD_PX) / DPI)
    figure.savefig(path, dpi=DPI, transparent=True, bbox_inches=box)
    plt.close(figure)
    return path


def _geometry(path: pathlib.Path) -> tuple[float, float]:
    width, height = PILImage.open(path).size
    return width * 72.0 / DPI, height * 72.0 / DPI


def math_image(latex: str, fontsize: float = 10.5) -> tuple[pathlib.Path, float, float]:
    path = _render(latex, fontsize)
    width, height = _geometry(path)
    return path, width, height


def inline(latex: str, fontsize: float = 9.0) -> str:
    """A ReportLab <img> tag that sits on the text baseline."""
    path, width, height = math_image(latex, fontsize)
    descent = 0.24 * fontsize + 72.0 * _PAD_PX / DPI
    return ('<img src="{}" width="{:.2f}" height="{:.2f}" valign="{:.2f}"/>'
            .format(path, width, height, -descent))
