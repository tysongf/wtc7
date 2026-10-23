"""Verification of the explicit shell solver (wtc7.xfe) used by the Phase 1 detailed model.

Each test compares a small explicit run with a closed-form result. The longer benchmarks
(lateral-torsional buckling against theory and CalculiX, mesh studies) are in
phase1/verify_xfe.py and results/phase1/shell/verification.md.
"""
import ctypes as C

import numpy as np
import pytest

from wtc7 import xfe
from wtc7.materials import SteelModel, bolt_strength_factor, thermal_strain
from wtc7.xfe import mesh

G_ACC = 386.1


def strip(L, b, t, nx, ny, material):
    m = xfe.Model()
    m.add_material(material)
    idx, _ = mesh.plate(m, [0, 0, 0], [1, 0, 0], [0, 1, 0], np.linspace(0, L, nx + 1),
                        np.linspace(-b / 2, b / 2, ny + 1), t, 0, 1, "strip")
    return m, idx


def uniaxial(model, k, T, emax=0.05, n=200):
    """Material-point uniaxial stress path through the kernel's own stress update."""
    lib = model.lib
    s, ep, out = np.zeros(3), 0.0, []
    de = emax / n
    for _ in range(n):
        dy = -0.3 * de
        for _ in range(30):
            st = s.copy()
            dep = lib.stress_update(C.byref(model.matstruct), k, T, T, xfe.ptr(np.array([de, dy, 0.0])),
                                    xfe.ptr(st), ep)
            if abs(st[1]) < 1e-9:
                break
            st2 = s.copy()
            lib.stress_update(C.byref(model.matstruct), k, T, T, xfe.ptr(np.array([de, dy + 1e-9, 0.0])),
                              xfe.ptr(st2), ep)
            dy -= st[1] / ((st2[1] - st[1]) / 1e-9)
        s, ep = st, ep + dep
        out.append((s[0], ep))
    return np.array(out)


@pytest.mark.parametrize("set_name", ["NIST", "EC3"])
def test_material_point_follows_flow_curves(set_name):
    m = xfe.Model()
    m.add_material(xfe.steel_material("s", set_name))
    nd = m.add_nodes([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
    m.add_shells([nd], 0.5, "s", 1, "p")
    m.finalize()
    sm = SteelModel(set_name, "A572")
    for T in (20.0, 400.0, 600.0):
        r = uniaxial(m, 0, T)
        sel = r[:, 1] > 1e-4
        ref = np.array([sm.flow(T, e)[0] for e in r[sel, 1]])
        assert np.max(np.abs(r[sel, 0] - ref) / ref) < 0.01


@pytest.mark.parametrize("set_name", ["NIST", "EC3"])
def test_free_thermal_expansion_within_1pct(set_name):
    """Preregistration Section 4: free expansion within 1 % of the hand calculation."""
    L = 60.0
    m, idx = strip(L, 4.0, 0.5, 30, 2, xfe.steel_material("s", set_name))
    m.fix(idx[0, :], (0,))
    m.fix(idx[0, 1], (1,))
    m.fix(idx.ravel(), (2, 3, 4, 5))
    m.finalize()
    m.damping = 300.0
    Tf = 600.0
    m.run(0.08, lambda t: np.array([20.0, 20.0 + min(t / 0.05, 1.0) * (Tf - 20)]))
    u = (m.x[idx[-1, :], 0] - m.x0[idx[-1, :], 0]).mean()
    assert u == pytest.approx(float(thermal_strain(Tf, set_name)) * L, rel=0.01)


@pytest.mark.parametrize("set_name", ["NIST", "EC3"])
def test_restrained_force_within_1pct(set_name):
    """Preregistration Section 4: axial force of a fully restrained member within 1 % of A E eps_th."""
    T, b, t = 100.0, 4.0, 0.5
    m, idx = strip(30.0, b, t, 15, 2, xfe.steel_material("s", set_name))
    m.fix(idx[0, :], (0,))
    m.fix(idx[-1, :], (0,))
    m.fix(idx[0, 1], (1,))
    m.fix(idx.ravel(), (2, 3, 4, 5))
    m.finalize()
    m.damping = 300.0
    m.run(0.08, lambda tt: np.array([20.0, 20.0 + min(tt / 0.05, 1.0) * (T - 20)]))
    N = (m.sig[:, :, 0] * (0.5 * t * xfe.GAUSS5[1])[None, :]).sum(1)
    sm = SteelModel(set_name, "A572")
    assert N.mean() * b == pytest.approx(-b * t * sm.E(T) * sm.eps_th(T), rel=0.01)


def test_cantilever_tip_deflection():
    L, b, t, P = 20.0, 2.0, 0.5, 0.05
    m, idx = strip(L, b, t, 20, 2, xfe.elastic_material("el", 29000.0))
    m.fix(idx[0, :], (0, 1, 2, 3, 4, 5))
    m.finalize()
    m.damping = 400.0
    f = np.zeros((m.nn, 3))
    f[idx[-1, :], 2] = P / 3
    m.set_load_pattern(f)
    m.run(0.15, lambda tt: np.array([20.0, 20.0]), lam=lambda tt: min(tt / 0.05, 1.0))
    w = m.x[idx[-1, :], 2].mean()
    assert w == pytest.approx(P * L**3 / (3 * 29000.0 * b * t**3 / 12), rel=0.01)


def test_euler_buckling_of_heated_restrained_strut():
    """Preregistration Section 4: buckling load of a pinned strut within 2 % of pi^2 EI / L^2.
    The plateau force is corrected for the initial imperfection (P = Pcr (1 - d0 / d))."""
    L, b, t, E, a = 40.0, 2.0, 0.25, 29000.0, 1.4e-5
    m = xfe.Model()
    m.add_material(xfe.elastic_material("el", E, alpha=a))
    idx, _ = mesh.plate(m, [0, 0, 0], [1, 0, 0], [0, 1, 0], np.linspace(0, L, 41), np.linspace(-b / 2, b / 2, 3),
                        t, 0, 1, "strut")
    d0 = L / 2000
    m._x[0][:, 2] += d0 * np.sin(np.pi * m._x[0][:, 0] / L)
    m.fix(idx[0, :], (0, 2))
    m.fix(idx[-1, :], (0, 2))
    m.fix(idx[:, 1], (1,))
    m.fix(idx.ravel(), (5,))
    m.finalize()
    m.damping = 30.0
    Pcr = np.pi**2 * E * (b * t**3 / 12) / L**2
    Tend = 20 + 4 * Pcr / (b * t * E * a)
    m.run(0.6, lambda tt: np.array([20.0, 20.0 + min(tt / 0.4, 1.0) * (Tend - 20)]))
    N = (m.sig[:, :, 0] * (0.5 * t * xfe.GAUSS5[1])[None, :]).sum(1)
    P = -N[:2].sum() * b / 2
    d = m.x[idx[20, 1], 2]
    assert P / (1 - d0 / d) == pytest.approx(Pcr, rel=0.02)


@pytest.mark.parametrize("th,mu", [(10, 0.3), (16, 0.3), (20, 0.3), (30, 0.3), (14.6, 0.24), (14.6, 0.28)])
def test_block_on_incline_sticks_or_slides(th, mu):
    """Coulomb friction: sticks when tan(th) < mu, else slides with a = g (sin th - mu cos th)."""
    T = 0.05
    m = xfe.Model()
    m.add_material(xfe.elastic_material("el", 29000.0))
    t = 0.5
    idx, _ = mesh.plate(m, [0, 0, t / 2], [1, 0, 0], [0, 1, 0], np.linspace(0, 4, 3), np.linspace(0, 4, 3), t, 0, 0,
                        "blk")
    m.finalize()
    r = np.radians(th)
    m.set_load_pattern(m.mass_phys[:, None] * G_ACC * np.array([np.sin(r), 0.0, -np.cos(r)])[None, :])
    m.add_plane("floor", idx.ravel(), t / 2, [0, 0, 0], [0, 0, 1], [1, 0, 0], [-1e3, 1e3, -1e3, 1e3], mu=mu)
    m.run(T, lambda tt: np.array([20.0]), lam=lambda tt: 1.0)
    ux = (m.x[:, 0] - m.x0[:, 0])[idx.ravel()].mean()
    a = max(0.0, G_ACC * (np.sin(r) - mu * np.cos(r)))
    assert ux == pytest.approx(0.5 * a * T**2, abs=2e-4 + 0.01 * 0.5 * a * T**2)


@pytest.mark.parametrize("mu,slides", [(0.20, True), (0.24, True), (0.27, False), (0.30, False)])
def test_skewed_face_wedge(mu, slides):
    """A plate pushed into a face skewed 14.6 deg slides along it only when mu < tan 14.6 deg."""
    th = np.radians(14.6)
    m = xfe.Model()
    m.add_material(xfe.elastic_material("el", 29000.0))
    idx, _ = mesh.plate(m, [0, 0, 0], [1, 0, 0], [0, 1, 0], np.linspace(-8, 0, 9), np.linspace(-1, 1, 3), 0.5, 0, 0,
                        "blk")
    m.fix(idx.ravel(), (2, 3, 4))
    m.prescribe(idx[0, :], (0,))
    m.finalize()
    m.vpres[idx[0, :], 0] = 5.0
    m.add_plane("wall", idx[-1, :], 0.0, [0.3, 0.0, 0.0], [-np.cos(th), -np.sin(th), 0.0], [0, 0, 1],
                [-1e3, 1e3, -1e3, 1e3], mu=mu)
    m.run(0.02, lambda tt: np.array([20.0]))
    uy = (m.x[idx[-1, :], 1] - m.x0[idx[-1, :], 1]).mean()
    assert (uy < -0.1) == slides


@pytest.mark.parametrize("T", [20.0, 500.0])
def test_bolt_spring_breaks_at_capacity(T):
    m = xfe.Model()
    m.add_material(xfe.elastic_material("el", 29000.0))
    idx, _ = mesh.plate(m, [0, 0, 0], [1, 0, 0], [0, 1, 0], np.linspace(0, 4, 5), np.linspace(-1, 1, 3), 0.5, 0, 1,
                        "p")
    m.fix(idx.ravel(), (1, 2, 3, 4, 5))
    m.prescribe(idx[-1, :], (0,))
    m.finalize()
    m.vpres[idx[-1, :], 0] = 2.0
    a = idx[0, 1]
    ss = xfe.SpringSet(["bolt"], [a, -1, -1, -1], [1, 0, 0, 0], [-1, -1, -1, -1], [0, 0, 0, 0], m.x0[a].copy(),
                       [0, 0, 1], [-1], [180.0], [1000.0], [1 / 32], [45.0], [1e9], [[0.0, 1.0]], [0],
                       [bolt_strength_factor], m.x0)
    m.spring_sets.append(ss)
    peak = []
    m.run(0.3, lambda t: np.array([20.0, T]), monitor=lambda mm: peak.append(ss.fsv[0, 0]), every=10)
    cap = 45.0 * float(bolt_strength_factor(T))
    assert ss.broken[0] == 1
    assert max(peak) == pytest.approx(cap, rel=0.01)


def test_node_on_shell_contact_carries_the_load():
    m = xfe.Model()
    m.add_material(xfe.elastic_material("el", 29000.0))
    low, el_low = mesh.plate(m, [0, 0, 0], [1, 0, 0], [0, 1, 0], np.linspace(-10, 10, 11), np.linspace(-10, 10, 11),
                             0.5, 0, 0, "low")
    top, _ = mesh.plate(m, [0, 0, 0.5], [1, 0, 0], [0, 1, 0], np.linspace(-3, 3, 7), np.linspace(-3, 3, 7), 0.5, 0, 0,
                        "top")
    m.fix(np.concatenate([low[0, :], low[-1, :], low[:, 0], low[:, -1]]), (0, 1, 2))
    m.fix(top.ravel(), (0, 1))
    m.finalize()
    m.damping = 200.0
    W = 5.0
    f = np.zeros((m.nn, 3))
    f[top.ravel(), 2] = -W / top.size
    m.set_load_pattern(f)
    sc = m.add_surface("contact", el_low, [0, 0, 1], mfac=0.5, nodes=top.ravel(), off=0.25)
    m.run(0.1, lambda t: np.array([20.0]), lam=lambda t: min(t / 0.05, 1.0))
    assert sc.out[2] == pytest.approx(W, rel=0.01)


def test_slab_material_tension_and_compression_curves():
    """Kind 2 (MAT_124 idea): uniaxial tension follows the tension curve, compression the compression curve."""
    tens = ((0.0, 0.0002, 0.002, 0.3), (0.50, 0.25, 0.33, 0.33))
    comp = ((0.0, 0.00055, 0.3), (2.2, 5.1, 5.1))
    m = xfe.Model()
    m.add_material(xfe.tension_compression_material("c", 3372.0, 0.2, 2.2e-7, tens, comp))
    nd = m.add_nodes([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
    m.add_shells([nd], 4.0, "c", 0, "p")
    m.finalize()
    for sign, (ep_pts, s_pts) in ((1.0, tens), (-1.0, comp)):
        r = uniaxial(m, 0, 20.0, emax=sign * 0.01, n=400)
        sel = r[:, 1] > 1e-5
        ref = np.interp(r[sel, 1], ep_pts, s_pts)
        assert np.max(np.abs(np.abs(r[sel, 0]) - ref) / ref) < 0.03   # one increment straddles the curve kink
