import pathlib

import pytest

from xrdsim.cli import main
from xrdsim.diffractometer import reflections
from xrdsim.samples import get_phase


def test_list_phases(capsys):
    assert main(["--list-phases"]) == 0
    out = capsys.readouterr().out
    assert "si" in out and "zno" in out


def test_table_lists_silicon_reflections(capsys):
    assert main(["--phase", "si", "--table"]) == 0
    out = capsys.readouterr().out
    assert "111" in out and "220" in out


def test_writes_a_png(tmp_path, capsys):
    target = tmp_path / "si.png"
    assert main(["--phase", "si", "--range", "25", "35", "--out", str(target)]) == 0
    assert target.exists() and target.stat().st_size > 5000


def test_requires_a_phase():
    with pytest.raises(SystemExit):
        main([])
