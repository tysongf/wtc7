"""Verification of the plan-view solver (preregistration Section 4)."""
import math

import numpy as np

from wtc7 import fe2d
from wtc7.sections import shape

W = shape("W24X55")


def strut(n_el=10, L=624.0, imperf=0.0):
    x = np.linspace(0, L, n_el + 1)
    y = imperf * L * np.sin(math.pi * x / L)
    m = fe2d.Model(xy=np.column_stack([x, y]), damping=5.0)
    fy, fa = W.plan_fibres(24)
    conn = np.column_stack([np.arange(n_el), np.arange(1, n_el + 1)])
    m.add_group(fe2d.BeamGroup("s", conn, fy, fa, fe2d.ElasticSteel(), "T"))
    return m, n_el


def ramp(T1, t_end):
    return lambda t: {"T": 20.0 + (T1 - 20.0) * min(t / t_end, 1.0)}


def test_free_thermal_expansion():
    m, n = strut()
    m.fixed = {0, 1, 2}
    status, hist = fe2d.run(m, ramp(520.0, 50.0), 60.0, 1.0)
    tip = hist[-1].u[3 * n]
    exact = 1.4e-5 * 500 * 624.0
    assert status == "complete" and abs(tip - exact) / exact < 0.01


def test_fully_restrained_force():
    m, n = strut(L=120.0)
    m.fixed = {0, 1, 2, 3 * n, 3 * n + 1}
    status, hist = fe2d.run(m, ramp(30.0, 20.0), 25.0, 1.0)
    N = m.axial["s"]
    exact = -29000.0 * W.A * 1.4e-5 * 10.0
    assert abs(N.mean() - exact) / abs(exact) < 0.01


def test_euler_buckling_in_plan():
    m, n = strut(n_el=16, imperf=1e-4)
    m.fixed = {0, 1, 3 * n, 3 * n + 1}
    status, hist = fe2d.run(m, ramp(80.0, 60.0), 70.0, 0.5)
    PE = math.pi**2 * 29000.0 * W.Iy / 624.0**2
    N = -m.axial["s"].mean()
    assert status == "complete" and abs(N - PE) / PE < 0.02, (N, PE)


def test_rigid_rotation_gives_no_force():
    m, n = strut(n_el=2)
    f, K = m.internal(np.zeros(m.ndof), {"T": 20.0})
    th = 0.3
    u = np.zeros(m.ndof)
    for k, (x, y) in enumerate(m.xy):
        u[3 * k] = x * math.cos(th) - y * math.sin(th) - x
        u[3 * k + 1] = x * math.sin(th) + y * math.cos(th) - y
        u[3 * k + 2] = th
    f, K = m.internal(u, {"T": 20.0})
    assert np.max(np.abs(f)) < 1e-6


def test_contact_resists_closure_after_gap():
    # member heated with its far end fixed: the near end moves -x, closes a 0.05 in. gap, then bears
    m, n = strut(n_el=4, L=100.0)
    xy = np.vstack([m.xy, [[0.0, 0.0]]]); m.xy = xy
    gnd = len(xy) - 1
    m.fixed = {3 * gnd, 3 * gnd + 1, 3 * gnd + 2, 3 * n, 3 * n + 1, 1}
    c = fe2d.Contact(gnd, 0, [-1.0, 0.0], 0.05, k=1e6)
    m.springs = [c]
    status, hist = fe2d.run(m, ramp(120.0, 40.0), 45.0, 1.0)
    free = 1.4e-5 * 100.0 * 100.0
    assert status == "complete"
    assert abs(-hist[-1].u[0] - 0.05) < 0.01          # stopped at the gap, not at the free 0.14 in.
    assert c.force > 0 and abs(c.force + m.axial["s"].mean()) / c.force < 0.02


def test_bolt_group_breaks_at_capacity():
    m, n = strut(n_el=4, L=100.0)
    xy = np.vstack([m.xy, [[0.0, 0.0]]]); m.xy = xy
    gnd = len(xy) - 1
    m.fixed = {3 * gnd, 3 * gnd + 1, 3 * gnd + 2, 3 * n, 3 * n + 1, 1}
    b = fe2d.BoltGroup(gnd, 0, 2, 45.0, 180.0, 1 / 32, lambda T: 20.0, lambda T: 1.0, "b")
    m.springs = [b, fe2d.Friction(gnd, 0, 0.3, 10.0, 0.01, "f")]
    status, hist = fe2d.run(m, ramp(300.0, 60.0), 70.0, 0.5)
    assert b.broken
    # after the bolts go, only friction (3 kip) restrains the end
    assert abs(-m.axial["s"].mean() - 3.0) < 0.1


def _skewed_face_run(mu):
    """Strut heated against a face tilted 20 deg from square: with mu below tan(20 deg) = 0.36
    the end slides along the face, above it the end sticks."""
    m, n = strut(n_el=4, L=100.0)
    xy = np.vstack([m.xy, [[0.0, 0.0]]]); m.xy = xy
    gnd = len(xy) - 1
    m.fixed = {3 * gnd, 3 * gnd + 1, 3 * gnd + 2, 3 * n, 3 * n + 1}
    a = math.radians(20.0)
    face = fe2d.FrictionalContact(gnd, 0, [-math.cos(a), -math.sin(a)], 0.01, mu, name="face")
    m.springs = [face]
    status, hist = fe2d.run(m, ramp(220.0, 60.0), 65.0, 0.5)
    return status, hist[-1].u[1]


def test_frictional_contact_slides_below_tan_angle():
    s1, slide = _skewed_face_run(0.1)
    s2, stick = _skewed_face_run(0.6)
    assert s1 == "complete" and s2 == "complete"
    # sticking still allows the elastic tangential penalty deflection (thrust ~600 kip / kt)
    assert abs(slide) > 0.5 and abs(stick) < 0.03, (slide, stick)
