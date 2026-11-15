"""Run every build step in order and report what failed.

    uv run python -m tools.check_all

This is the close-out command: tests, figures, tables, PDF, the PDF gate and the number
gate. It prints ``all steps passed`` only when every step exits zero.
"""

from __future__ import annotations

import subprocess
import sys

STEPS = [
    ("tests", [sys.executable, "-m", "pytest", "-q"]),
    ("figures", [sys.executable, "-m", "report.make_figures"]),
    ("tables", [sys.executable, "-m", "report.tables"]),
    ("size", [sys.executable, "-m", "report.size_study"]),
    ("pdf", [sys.executable, "-m", "report.generate_pdf_report"]),
    ("gate", [sys.executable, "-m", "report.check_pdf"]),
    ("numbers", [sys.executable, "-m", "report.check_numbers"]),
]


def main() -> int:
    failures = []
    for name, command in STEPS:
        result = subprocess.run(command, capture_output=True, text=True)
        status = "ok" if result.returncode == 0 else "FAILED"
        print(f"{name:8s} {status}")
        if result.returncode != 0:
            failures.append(name)
            print((result.stdout + result.stderr).strip()[-2000:])
        elif name in {"gate", "numbers"}:
            print("         " + (result.stdout.strip().splitlines() or [""])[-1])
    if failures:
        print("failed: " + ", ".join(failures))
        return 1
    print("all steps passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
