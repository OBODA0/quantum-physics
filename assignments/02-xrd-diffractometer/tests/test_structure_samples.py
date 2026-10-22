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


KNOWN_STRONGEST = {
    "si": ((1, 1, 1), 28.44), "al": ((1, 1, 1), 38.47), "cu": ((1, 1, 1), 43.30),
    "fe": ((1, 1, 0), 44.67), "nacl": ((2, 0, 0), 31.69), "mgo": ((2, 0, 0), 42.92),
    "zno": ((1, 0, 1), 36.25), "tio2-rutile": ((1, 1, 0), 27.45),
    "tio2-anatase": ((1, 0, 1), 25.28),
}


def test_every_phase_reproduces_its_published_strongest_line():
    from xrdsim.diffractometer import Instrument, reflections
    for key, (hkl, expected) in KNOWN_STRONGEST.items():
        rows = [row for row in reflections(PHASES[key], Instrument()) if row.intensity > 1e-9]
        strongest = max(rows, key=lambda row: row.intensity)
        assert strongest.hkl == hkl, key
        assert strongest.two_theta == pytest.approx(expected, abs=0.03), key


def _brute_multiplicity(h, k, l, system):
    """Count the orbit by enumerating the operations, independently of multiplicity()."""
    import itertools

    def signed_permutations(values):
        out = set()
        for perm in itertools.permutations(values):
            for signs in itertools.product([1, -1], repeat=len(perm)):
                out.add(tuple(p * s for p, s in zip(perm, signs)))
        return out

    if system == "cubic":
        return len(signed_permutations((h, k, l)))

    if system == "tetragonal":
        out = set()
        for a, b in signed_permutations((h, k)):
            for c in ({l, -l} if l else {0}):
                out.add((a, b, c))
        return len(out)

    if system == "hexagonal":
        rotations = [(h, k), (k, -h - k), (-h - k, h), (-h, -k), (-k, h + k), (h + k, -h)]
        out = set()
        for a, b in rotations:
            for mirrored in ((a, b), (b, a)):
                for c in ({l, -l} if l else {0}):
                    out.add((mirrored[0], mirrored[1], c))
        return len(out)

    raise ValueError(system)


@pytest.mark.parametrize("system", ["cubic", "tetragonal", "hexagonal"])
def test_multiplicity_matches_a_brute_force_orbit(system):
    for h in range(0, 4):
        for k in range(0, 4):
            for l in range(0, 4):
                if h == k == l == 0:
                    continue
                assert multiplicity(h, k, l, system) == _brute_multiplicity(h, k, l, system), (
                    system, h, k, l)


def test_rocksalt_structure_factor_is_the_form_factor_difference():
    from xrdsim.lattice import d_spacing
    nacl = get_phase("nacl")
    for hkl, sign in [((1, 1, 1), -1.0), ((2, 0, 0), +1.0)]:
        d = d_spacing(*hkl, **nacl.cell_kwargs())
        s = LAM / (2 * d)
        expected = 4.0 * (f0("Na", s) + sign * f0("Cl", s)) * debye_waller(0.5, s)
        assert structure_factor(nacl, *hkl, LAM).real == pytest.approx(expected, rel=1e-12)


def test_fcc_structure_factor_is_four_times_the_form_factor():
    from xrdsim.lattice import d_spacing
    cu = get_phase("cu")
    d = d_spacing(1, 1, 1, **cu.cell_kwargs())
    expected = 4.0 * f0("Cu", LAM / (2 * d)) * debye_waller(0.5, LAM / (2 * d))
    assert structure_factor(cu, 1, 1, 1, LAM).real == pytest.approx(expected, rel=1e-12)


def test_bcc_structure_factor_is_twice_the_form_factor():
    from xrdsim.lattice import d_spacing
    fe = get_phase("fe")
    d = d_spacing(1, 1, 0, **fe.cell_kwargs())
    expected = 2.0 * f0("Fe", LAM / (2 * d)) * debye_waller(0.5, LAM / (2 * d))
    assert structure_factor(fe, 1, 1, 0, LAM).real == pytest.approx(expected, rel=1e-12)


def test_diamond_111_structure_factor_has_the_expected_modulus():
    from xrdsim.lattice import d_spacing
    si = get_phase("si")
    d = d_spacing(1, 1, 1, **si.cell_kwargs())
    expected = 4.0 * f0("Si", LAM / (2 * d)) * debye_waller(0.5, LAM / (2 * d))
    assert abs(structure_factor(si, 1, 1, 1, LAM)) == pytest.approx(
        expected * math.sqrt(2.0), rel=1e-12)


@pytest.mark.parametrize("key", sorted(PHASES))
def test_simulated_peaks_sit_on_the_predicted_reflections(key):
    from xrdsim.analysis import find_peaks
    from xrdsim.diffractometer import Instrument, scan
    phase = PHASES[key]
    result = scan(phase, 20.0, 90.0, 0.01,
                  Instrument(ka2=False, background_rate=0.0, rng_seed=None))
    found = [peak.two_theta for peak in find_peaks(result.two_theta, result.counts)]
    strongest = max(row.intensity for row in result.reflections)
    predicted = [row.two_theta for row in result.reflections
                 if row.intensity > 0.05 * strongest and 20.0 <= row.two_theta <= 90.0]
    assert predicted, key
    for angle in predicted:
        assert min(abs(angle - seen) for seen in found) < 0.1, (key, angle)
