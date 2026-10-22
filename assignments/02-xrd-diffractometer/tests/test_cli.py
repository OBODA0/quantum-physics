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


def test_index_and_scherrer_flags(capsys):
    assert main(["--phase", "si", "--range", "20", "60", "--step", "0.01",
                 "--size", "300", "--no-ka2", "--index", "--scherrer"]) == 0
    out = capsys.readouterr().out
    assert "(1, 1, 1)" in out and "(2, 2, 0)" in out
    assert "Scherrer" in out
    assert "30.0" in out or "30.1" in out


def test_identify_ranks_the_simulated_phase_first(capsys):
    assert main(["--phase", "zno", "--range", "20", "90", "--step", "0.01",
                 "--no-ka2", "--identify"]) == 0
    out = capsys.readouterr().out
    block = out.split("identification:")[1].strip().splitlines()
    assert block[0].startswith("phase")  # header
    assert block[1].split()[0] == "zno"
