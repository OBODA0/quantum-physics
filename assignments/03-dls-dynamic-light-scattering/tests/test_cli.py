"""The command line interface end to end."""

import csv

from dlssim.cli import main


def test_cli_writes_outputs(tmp_path, capsys):
    code = main([
        "--diameter", "120",
        "--sigma", "1.1",
        "--duration", "5",
        "--out", str(tmp_path),
        "--no-plot",
    ])
    assert code == 0
    out = capsys.readouterr().out
    assert "z-average" in out
    assert "PDI" in out
    correlation = tmp_path / "correlation.csv"
    distribution = tmp_path / "distribution.csv"
    assert correlation.exists() and distribution.exists()
    with correlation.open() as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["tau_s", "g2_ideal", "g2_measured", "g1_measured"]
    assert len(rows) > 10


def test_cli_rejects_unknown_solvent():
    try:
        main(["--solvent", "benzene", "--no-plot", "--out", "/tmp"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("unknown solvent should exit")
