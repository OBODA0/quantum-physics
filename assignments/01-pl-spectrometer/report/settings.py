"""
The optical conditions shared by every figure and every number in the report.

They live here, in one place, because they were once written twice: the figures
used 0.1 % stray light while the instrument table in `numbers.md` still said
0.5 %, which would have put a wrong number in the report's own text.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CONCENTRATION_M = 1.0e-6
PATH_LENGTH_CM = 1.0
SCATTER_FRACTION = 0.001
DETECTION_RANGE_NM = (450.0, 900.0)

EXCITATION_START_NM = 400.0
EXCITATION_STOP_NM = 700.0
EXCITATION_STEP_NM = 2.0

# Cy3 is transparent at 450 and 650 nm, so those curves would be flat lines at
# zero and would only clutter the question-2 legend.
OVERLAY_EXCITATION_NM = (470.0, 500.0, 520.0, 540.0, 550.0, 560.0)
ASSIGNED_EXCITATION_NM = (450.0, 550.0, 650.0)

DYE_KEYS = ["cy3", "cy5", "methylene-blue"]
DYE_COLORS = {"cy3": "#d95f02", "cy5": "#7570b3", "methylene-blue": "#1b9e77"}
STRAY_COLOR = "#c1440e"

# The digitized absorption curves stop where they were measured. Beyond that the
# model has no data and reads zero absorption, which is a limit of the data, not
# physics: Cy3's absorption is small but non-zero past 590 nm in reality.
ABSORPTION_RANGE_NM = {"cy3": (450.0, 590.0), "cy5": (430.0, 734.0), "methylene-blue": (300.0, 800.0)}
