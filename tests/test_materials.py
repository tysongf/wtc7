"""Checks on the steel property sets (preregistration Section 4, 'Material curves')."""
import numpy as np

from wtc7 import materials as m


def _compare(grade, table_key):
    published = m.nist_table(grade)
    worst_first, worst_rest = 0.0, 0.0
    for T, (eps, sig) in published.items():
        ey, sy = m.rebuilt_yield(grade, T)
        worst_first = max(worst_first, abs(sy - sig[0]) / sig[0])
        pred = m.rebuilt_curve(grade, T, eps[1:])
        worst_rest = max(worst_rest, np.max(np.abs(pred - sig[1:]) / sig[1:]))
    return worst_first, worst_rest


def test_rebuild_reproduces_A36_table_E3():
    first, rest = _compare("A36", "E3")
    assert first < 0.02 and rest < 0.05, (first, rest)


def test_rebuild_reproduces_G4021_table_E5():
    first, rest = _compare("G40.21", "E5")
    assert first < 0.02 and rest < 0.05, (first, rest)


def test_published_E4_is_duplicate_of_E3():
    a = (m.ROOT / "data/nist/table_E3.csv").read_text()
    b = (m.ROOT / "data/nist/table_E4.csv").read_text()
    assert a == b


def test_A572_room_temperature_yield():
    ey, sy = m.rebuilt_yield("A572", 20.0)
    assert abs(sy - 369.6 * m.KSI_PER_MPA) / sy < 0.01


def test_E_nist_matches_section_8_7_2_example():
    # NCSTAR 1-9 Section 8.7.2: E(600 C) = 22,235 ksi
    assert abs(m.E_nist(600.0) - 22235) / 22235 < 0.01


def test_ec3_reduction_at_600C():
    # EN 1993-1-2 Table 3.1: k_y = 0.47 at 600 C (stress at 2 % strain)
    fy20 = 50.0
    assert abs(m.ec3_stress(600.0, 0.02, fy20) / fy20 - 0.47) < 1e-6
    sm = m.SteelModel("EC3", "A572")
    E = sm.E(600.0)
    ep = 0.02 - 0.47 * sm._fy20 / E
    assert abs(sm.flow(600.0, ep)[0] / sm._fy20 - 0.47) < 0.01


def test_flow_monotone_in_temperature():
    # first-yield points have the small 400-550 C hump NIST describes in Appendix E,
    # so monotonicity is checked on the flow stress at 2 % plastic strain
    for set_name in ("NIST", "EC3"):
        sm = m.SteelModel(set_name, "A572")
        fys = [sm.flow(T, 0.02)[0] for T in np.arange(20, 851, 50)]
        assert all(a >= b - 1e-9 for a, b in zip(fys, fys[1:])), (set_name, fys)
