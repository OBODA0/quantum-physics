"""The numbers the report quotes, computed once.

Both the PDF builder and the gate import this module, so a figure in the text cannot
disagree with the model that produced it. Every value here must appear literally in the
built PDF; `report/check_numbers.py` enforces that.
"""

from __future__ import annotations

from .size_study import rows as size_rows


def quoted_numbers() -> dict[str, str]:
    data = {(row["size_nm"], row["hkl"]): row for row in size_rows()}
    return {
        "si_111_position": f"{data[20.0, '111']['two_theta']:.3f}",
        "fwhm_5nm_111": f"{data[5.0, '111']['fwhm']:.3f}",
        "fwhm_500nm_111": f"{data[500.0, '111']['fwhm']:.4f}",
        "height_500nm_111": f"{data[500.0, '111']['height']:.0f}",
        "area_low": f"{data[5.0, '111']['area']:.0f}",
        "area_high": f"{data[500.0, '111']['area']:.0f}",
        "fwhm_20nm_111": f"{data[20.0, '111']['fwhm']:.3f}",
        "fwhm_20nm_400": f"{data[20.0, '400']['fwhm']:.3f}",
        "predicted_5nm_111": f"{data[5.0, '111']['predicted_size_fwhm']:.2f}",
    }
