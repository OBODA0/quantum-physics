"""Capture the Tk GUI's window as the screenshot the report shows.

A screen capture is a photograph of a running program, not a build product: it is checked in
and re-generated only when the interface changes. It is taken on a virtual X display, so the
capture never touches the desktop session of the machine it runs on.

    uv run python -m report.capture_gui

Needs Xvfb, Tk and ImageMagick on the host; it refuses to run without them.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import signal
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "figures" / "gui_screenshot.png"
DISPLAY = ":97"
WIDTH, HEIGHT = 1500, 960


def main() -> int:
    for tool in ("Xvfb", "import", "magick"):
        if shutil.which(tool) is None:
            print(f"FAIL: {tool} is not on PATH")
            return 1
    project = HERE.parent
    raw = HERE / "figures" / "gui_raw.png"
    xvfb = subprocess.Popen(
        ["Xvfb", DISPLAY, "-screen", "0", f"{WIDTH}x{HEIGHT}x24"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    environment = {**os.environ, "DISPLAY": DISPLAY, "MPLBACKEND": "TkAgg"}
    gui = None
    try:
        time.sleep(2.0)
        gui = subprocess.Popen([sys.executable, "-m", "dlssim", "--gui"], cwd=str(project),
                               env=environment, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        time.sleep(10.0)
        if gui.poll() is not None:
            print("FAIL: the GUI exited before the capture")
            print((gui.stdout.read() + gui.stderr.read()).decode(errors="replace")[-2000:])
            return 1
        subprocess.run(["import", "-display", DISPLAY, "-window", "root", str(raw)],
                       check=True)
        subprocess.run(["magick", str(raw), "-trim", "+repage", str(OUT)], check=True)
        raw.unlink(missing_ok=True)
    finally:
        for process in (gui, xvfb):
            if process is not None and process.poll() is None:
                process.send_signal(signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
