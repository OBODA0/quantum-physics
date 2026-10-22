import math

import pytest

from xrdsim.atoms import debye_waller, f0
from xrdsim.lattice import d_spacing, two_theta
from xrdsim.samples import PHASES, get_phase
from xrdsim.structure import (lorentz_polarisation, multiplicity, relative_intensity,
                              structure_factor)

LAM = 1.540598


def test_f0_reproduces_the_electron_count():
    for element, z in [("Si", 14), ("Cu", 29), ("O", 8), ("Fe", 26)]:
        assert f0(element, 0.0) == pytest.approx(z, rel=0.01)


def test_f0_falls_with_angle():
    assert f0("Si", 0.0) > f0("Si", 0.3) > f0("Si", 0.6)


def test_debye_waller_is_one_at_zero():
    assert debye_waller(0.5, 0.0) == 1.0
    assert debye_waller(0.5, 0.5) == pytest.approx(math.exp(-0.125))


@pytest.mark.parametrize("system,hkl,expected", [
    ("cubic", (1, 0, 0), 6), ("cubic", (1, 1, 0), 12), ("cubic", (1, 1, 1), 8),
    ("cubic", (2, 0, 0), 6), ("cubic", (2, 1, 0), 24), ("cubic", (2, 1, 1), 24),
    ("cubic", (2, 2, 0), 12), ("cubic", (2, 2, 1), 24),
    ("tetragonal", (1, 0, 0), 4), ("tetragonal", (1, 1, 0), 4), ("tetragonal", (1, 0, 1), 8),
    ("tetragonal", (1, 1, 1), 8), ("tetragonal", (2, 0, 0), 4), ("tetragonal", (2, 0, 1), 8),
    ("tetragonal", (2, 1, 0), 8), ("tetragonal", (2, 1, 1), 16),
    ("hexagonal", (1, 0, 0), 6), ("hexagonal", (1, 1, 0), 6), ("hexagonal", (1, 0, 1), 12),
    ("hexagonal", (1, 0, 2), 12), ("hexagonal", (1, 0, 3), 12), ("hexagonal", (0, 0, 2), 2),
    ("hexagonal", (2, 0, 1), 12), ("hexagonal", (1, 1, 2), 12),
])
def test_multiplicity_matches_the_powder_average(system, hkl, expected):
    assert multiplicity(*hkl, system) == expected


def test_fcc_absences():
    cu = get_phase("cu")
    for hkl in [(1, 0, 0), (1, 1, 0), (2, 1, 0), (2, 1, 1)]:
        assert abs(structure_factor(cu, *hkl, LAM)) < 1e-6
    for hkl in [(1, 1, 1), (2, 0, 0), (2, 2, 0)]:
        assert abs(structure_factor(cu, *hkl, LAM)) > 1.0


def test_bcc_absences():
    fe = get_phase("fe")
    assert abs(structure_factor(fe, 1, 0, 0, LAM)) < 1e-6
    assert abs(structure_factor(fe, 1, 1, 1, LAM)) < 1e-6
    assert abs(structure_factor(fe, 1, 1, 0, LAM)) > 1.0


def test_diamond_absence_at_222():
    si = get_phase("si")
    assert abs(structure_factor(si, 2, 2, 2, LAM)) < 1e-6
    assert abs(structure_factor(si, 1, 1, 1, LAM)) > 1.0


def test_rocksalt_111_is_weak_against_200():
    nacl = get_phase("nacl")
    i111 = relative_intensity(nacl, 1, 1, 1, LAM)
    i200 = relative_intensity(nacl, 2, 0, 0, LAM)
    assert i111 < 0.15 * i200


def test_silicon_phase_reaches_the_certified_positions():
    si = get_phase("si")
    for hkl, expected in [((1, 1, 1), 28.4410), ((4, 0, 0), 69.1264)]:
        d = d_spacing(*hkl, **si.cell_kwargs())
        assert two_theta(d, LAM) == pytest.approx(expected, abs=5e-3)


def test_lorentz_polarisation_is_positive_and_diverges_at_zero():
    assert lorentz_polarisation(45.0) > 0
    with pytest.raises(ZeroDivisionError):
        lorentz_polarisation(0.0)


def test_all_phases_have_sites_and_a_source():
    for phase in PHASES.values():
        assert phase.sites, phase.key
        assert phase.source, phase.key
