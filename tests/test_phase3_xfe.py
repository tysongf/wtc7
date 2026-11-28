"""Closed-form verification suite for Phase 3 extensions to wtc7.xfe.

Implements every check required in docs/phase3_preregistration.md Section 8:
  1. 3D beam axial stiffness within 1 % of EA / L (plus section property accuracy).
  2. Euler buckling load of a 3D pinned strut within 2 % of pi^2 E I_min / L^2.
  3. Plastic collapse load of a fixed-base steel portal frame within 5 % of 4 Mp / H.
  4. Large-deflection elastic catenary tension of a pin-restrained beam within 5 %.
  5. Sudden removal of a middle support under an undamped elastic two-span beam:
     peak dynamic deflection equals 2.0 x static deflection within 5 %.
  6. Falling-mass floor impact: total 3D linear momentum conserved within 1 %,
     nodal physical mass conserved 100 %, and energy balance within 5 %.
  7. Coupled 6-DOF connection fracture (tension-shear interaction), seated walk-off
     loss of support, and two-storey column splice compression bearing vs uplift fracture.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from wtc7 import xfe
from wtc7.sections import col79_section, shape

G_ACC = 386.1


def test_section_builders_match_aisc_and_builtup():
    """Verify w_beam_section and rect_beam_section reproduce exact A, Ix, Iy and accurate Zx."""
    s24 = shape("W24X55")
    bs24 = xfe.w_beam_section("W24X55", s24)
    assert bs24.A == pytest.approx(s24.A, rel=1e-12)
    assert bs24.Ix == pytest.approx(s24.Ix, rel=1e-12)
    assert bs24.Iy == pytest.approx(s24.Iy, rel=1e-12)
    zx24 = float((np.abs(bs24.zf) * bs24.Af).sum())
    assert zx24 == pytest.approx(134.0, rel=0.015)

    # Built-up Column 79 at Floor 14 (W14X730 + two 26 x 2 in. side cover plates)
    A_ref, Imin_ref, Iy_ref, Ix_ref = col79_section(2.0)
    bs79 = xfe.w_beam_section("COL79_F14", "W14X730", kind="side", pw=26.0, pt=2.0)
    assert bs79.A == pytest.approx(A_ref, rel=1e-12)
    assert bs79.Ix == pytest.approx(Ix_ref, rel=1e-12)
    assert bs79.Iy == pytest.approx(Iy_ref, rel=1e-12)
    assert min(bs79.Ix, bs79.Iy) == pytest.approx(Imin_ref, rel=1e-12)

    # Rectangular section: exact A, Ix, Iy, Zx, Zy
    br = xfe.rect_beam_section("R", 2.0, 4.0)
    assert br.A == pytest.approx(8.0, rel=1e-12)
    assert br.Ix == pytest.approx(2.0 * 64.0 / 12.0, rel=1e-12)
    assert br.Iy == pytest.approx(4.0 * 8.0 / 12.0, rel=1e-12)
    assert float((np.abs(br.zf) * br.Af).sum()) == pytest.approx(2.0 * 16.0 / 4.0, rel=1e-12)


def test_beam_axial_stiffness_within_1pct():
    """Preregistration §8 (1): axial stiffness of a 3D skewed beam within 1 % of EA / L."""
    L, E, P = 180.0, 29000.0, 120.0
    axis = np.array([3.0, 4.0, 5.0])
    axis /= np.linalg.norm(axis)

    m = xfe.Model()
    m.add_material(xfe.elastic_material("el", E))
    sec = xfe.w_beam_section("W24X55", "W24X55")
    m.add_beam_section(sec)

    nel = 6
    s = np.linspace(0.0, L, nel + 1)
    nd = m.add_nodes(s[:, None] * axis[None, :])
    conn = np.column_stack([nd[:-1], nd[1:]])
    m.add_beams(conn, "W24X55", "el", 0, "bar")
    m.fix(nd[0], (0, 1, 2, 3, 4, 5))
    m.finalize()
    m.damping = 350.0

    f = np.zeros((m.nn, 3))
    f[nd[-1]] = P * axis
    m.set_load_pattern(f)
    m.run(0.08, lam=lambda t: min(t / 0.03, 1.0))

    u_tip = float((m.x[nd[-1]] - m.x0[nd[-1]]) @ axis)
    u_exact = P * L / (E * sec.A)
    assert u_tip == pytest.approx(u_exact, rel=0.01)
    assert float(m.bdiag[:, 0].mean()) == pytest.approx(P, rel=0.01)


def test_euler_buckling_3d_pinned_strut_within_2pct():
    """Preregistration §8 (2): Euler buckling load of a 3D pinned vertical strut within 2 % of pi^2 E I_min / L^2."""
    L, E, alpha = 240.0, 29000.0, 1.4e-5
    m = xfe.Model()
    m.add_material(xfe.elastic_material("el", E, alpha=alpha))
    sec = xfe.rect_beam_section("strut", b=2.0, h=4.0)  # Iy = 2.6667 in^4 (weak axis along e2)
    m.add_beam_section(sec)

    nel = 16
    zs = np.linspace(0.0, L, nel + 1)
    d0 = L / 2000.0
    # Vertical strut along +Z with up=[1,0,0] => e3 = +X (strong), e2 = -Y (weak); bow along Y
    xyz = np.column_stack([np.zeros_like(zs), d0 * np.sin(np.pi * zs / L), zs])
    nd = m.add_nodes(xyz)
    m.add_beams(np.column_stack([nd[:-1], nd[1:]]), "strut", "el", 1, "col", up=[1.0, 0.0, 0.0])

    # Pinned ends: fix translations (0, 1, 2) and twist about Z (5), leaving bending (3, 4) free
    m.fix([nd[0], nd[-1]], (0, 1, 2, 5))
    m.finalize()
    m.damping = 40.0

    Pcr = (math.pi**2) * E * min(sec.Ix, sec.Iy) / (L**2)
    Tend = 20.0 + 3.5 * Pcr / (sec.A * E * alpha)
    m.run(0.5, temps=lambda t: np.array([20.0, 20.0 + min(t / 0.3, 1.0) * (Tend - 20.0)]))

    P = -float(m.bdiag[:, 0].mean())
    d = abs(float(m.x[nd[nel // 2], 1]))
    assert d > 5.0 * d0
    assert P / (1.0 - d0 / d) == pytest.approx(Pcr, rel=0.02)


def test_plastic_collapse_fixed_base_portal_frame_within_5pct():
    """Preregistration §8 (3): plastic collapse load of a fixed-base steel portal frame within 5 % of 4 Mp / H."""
    B, H = 120.0, 100.0
    E, fy = 29000.0, 50.0
    b_w, h_d = 2.0, 4.0
    Mp = fy * (b_w * (h_d**2) / 4.0)  # 50 * 8 = 400 kip-in.
    H_collapse = 4.0 * Mp / H          # 16.0 kip

    m = xfe.Model()
    m.add_material(xfe.elastic_material("ep", E, fy=fy))
    m.add_beam_section(xfe.rect_beam_section("frame_sec", b_w, h_d))

    ncol, ngir = 12, 12
    z_col = np.linspace(0.0, H, ncol + 1)
    left = m.add_nodes(np.column_stack([np.zeros(ncol + 1), np.zeros(ncol + 1), z_col]))
    right = m.add_nodes(np.column_stack([np.full(ncol + 1, B), np.zeros(ncol + 1), z_col]))
    x_gir = np.linspace(0.0, B, ngir + 1)[1:-1]
    mid_gir = m.add_nodes(np.column_stack([x_gir, np.zeros_like(x_gir), np.full_like(x_gir, H)]))
    gir = np.concatenate([[left[-1]], mid_gir, [right[-1]]])

    m.add_beams(np.column_stack([left[:-1], left[1:]]), "frame_sec", "ep", 0, "colL", up=[1.0, 0.0, 0.0])
    m.add_beams(np.column_stack([right[:-1], right[1:]]), "frame_sec", "ep", 0, "colR", up=[1.0, 0.0, 0.0])
    m.add_beams(np.column_stack([gir[:-1], gir[1:]]), "frame_sec", "ep", 0, "gir", up=[0.0, 0.0, 1.0])

    # Fixed column bases; planar X-Z sway constraint (fix Y, rx, rz everywhere)
    m.fix([left[0], right[0]], (0, 1, 2, 3, 4, 5))
    m.fix(np.arange(m.nn if hasattr(m, "nn") else len(left) + len(right) + len(mid_gir)), (1, 3, 5))
    m.prescribe(left[-1], (0,))
    m.finalize()
    m.damping = 80.0

    # Push top-left node smoothly to 5.0 in. sway (~2.3x yield drift) and settle at zero velocity
    v_push = 12.5  # 5.0 in. over 0.40 s, then hold for 0.10 s so inertia/damping vanish
    def run_push():
        m._prepare()
        m.Tprev[:] = 20.0
        while m.t < 0.50:
            m.Tnow[:] = 20.0
            m.vpres[left[-1], 0] = v_push * math.sin(math.pi * m.t / 0.40) * (math.pi / 2.0) if m.t < 0.40 else 0.0
            m.step(0.0)
            m.Tprev[:] = m.Tnow

    run_push()
    base_shear = -(float(m.fint[left[0], 0]) + float(m.fint[right[0], 0]))
    assert base_shear == pytest.approx(H_collapse, rel=0.05)


def test_large_deflection_catenary_tension_within_5pct():
    """Preregistration §8 (4): large-deflection elastic catenary force of a pin-restrained tie within 5 %."""
    a = 120.0          # half-span, in. (total span 240 in.)
    E = 29000.0
    b_w, h_d = 2.0, 0.25
    A = b_w * h_d      # 0.50 in^2
    w_target = 15.0    # midspan vertical drop, in.

    ell = math.hypot(a, w_target)
    T_exact = E * A * (ell / a - 1.0)
    P_mid = 2.0 * T_exact * (w_target / ell)

    m = xfe.Model()
    m.add_material(xfe.elastic_material("el", E))
    m.add_beam_section(xfe.rect_beam_section("tie", b_w, h_d))

    nel = 16
    xs = np.linspace(0.0, 2.0 * a, nel + 1)
    nd = m.add_nodes(np.column_stack([xs, np.zeros_like(xs), np.zeros_like(xs)]))
    m.add_beams(np.column_stack([nd[:-1], nd[1:]]), "tie", "el", 0, "tie")

    # Pinned ends: translations + out-of-plane rotations fixed, ry free
    m.fix([nd[0], nd[-1]], (0, 1, 2, 3, 5))
    m.fix(nd[1:-1], (1, 3, 5))
    m.finalize()
    m.damping = 120.0

    f = np.zeros((m.nn, 3))
    f[nd[nel // 2], 2] = -P_mid
    m.set_load_pattern(f)
    m.run(0.35, lam=lambda t: min(t / 0.15, 1.0))

    w_num = -float(m.x[nd[nel // 2], 2])
    T_num = float(m.bdiag[:, 0].mean())
    assert w_num == pytest.approx(w_target, rel=0.05)
    assert T_num == pytest.approx(T_exact, rel=0.05)


def test_sudden_support_removal_two_span_beam_daf_2():
    """Preregistration §8 (5): sudden removal of a middle support under an undamped elastic
    two-span beam produces peak dynamic deflection equal to 2.0 x static within 5 %."""
    L_span = 120.0     # two spans of 120 in. = 240 in. total
    E = 29000.0
    W = 40.0           # downward point load at middle support, kip
    M_lump = W / G_ACC # dominant lumped mass at midspan

    sec = xfe.w_beam_section("W24X55", "W24X55")
    w_static = W * ((2.0 * L_span) ** 3) / (48.0 * E * sec.Ix)

    m = xfe.Model()
    m.add_material(xfe.elastic_material("el", E))
    m.add_beam_section(sec)
    m.add_beam_section(xfe.w_beam_section("POST", "W14X730"))

    nel = 16
    xs = np.linspace(0.0, 2.0 * L_span, nel + 1)
    nd = m.add_nodes(np.column_stack([xs, np.zeros_like(xs), np.zeros_like(xs)]))
    mid = nd[nel // 2]
    base_mid = m.add_nodes([[L_span, 0.0, -60.0]])[0]

    m.add_beams(np.column_stack([nd[:-1], nd[1:]]), "W24X55", "el", 0, "girder")
    post_id = m.add_beams([[base_mid, mid]], "POST", "el", 0, "post", up=[1.0, 0.0, 0.0])[0]
    m.add_mass(mid, M_lump)

    # Outer roller/pin supports + fixed base of middle post
    m.fix(nd[0], (0, 1, 2, 3, 5))
    m.fix(nd[-1], (1, 2, 3, 5))
    m.fix(nd[1:-1], (1, 3, 5))
    m.fix(base_mid, (0, 1, 2, 3, 4, 5))
    m.finalize()

    f = np.zeros((m.nn, 3))
    f[mid, 2] = -W
    m.set_load_pattern(f)

    # Stage 1: settle static equilibrium with middle post intact
    m.damping = 180.0
    m.run(0.12, lam=lambda t: min(t / 0.04, 1.0))
    z_settled = float(m.x[mid, 2])
    assert abs(z_settled) < 0.01 * w_static

    # Stage 2: turn off damping, suddenly remove middle post, record peak downward drop
    m.damping = 0.0
    m.bfac[post_id] = 0.0
    peaks = []
    m.run(0.30, lam=lambda _t: 1.0, monitor=lambda mm: peaks.append(z_settled - float(mm.x[mid, 2])), every=5)

    w_dyn_peak = max(peaks)
    assert w_dyn_peak == pytest.approx(2.0 * w_static, rel=0.05)
    assert m.energy_summary()["rel_error"] < 0.05


def test_falling_mass_floor_impact_momentum_mass_and_energy():
    """Preregistration §8 (6): falling-mass floor impact conserves total linear momentum within 1 %,
    conserves nodal physical mass 100 %, and maintains energy balance within 5 %."""
    E = 29000.0
    # Part A: isolated 3D oblique beam-to-beam floor impact (strict linear momentum + energy check)
    m = xfe.Model(contact_alpha=0.1, contact_zeta=0.25)
    m.add_material(xfe.elastic_material("el", E))
    m.add_beam_section(xfe.w_beam_section("W24X55", "W24X55"))

    xs = np.linspace(0.0, 120.0, 5)
    low = m.add_nodes(np.column_stack([xs, np.zeros_like(xs), np.zeros_like(xs)]))
    upp = m.add_nodes(np.column_stack([xs, np.zeros_like(xs), np.full_like(xs, 3.0)]))
    m.add_beams(np.column_stack([low[:-1], low[1:]]), "W24X55", "el", 0, "low_floor")
    m.add_beams(np.column_stack([upp[:-1], upp[1:]]), "W24X55", "el", 0, "upp_floor")
    m.add_mass(low, 0.04)
    m.add_mass(upp, 0.06)
    m.finalize()

    mass_before = float(m.mass_phys.sum())
    m.v[upp, 0] = 25.0
    m.v[upp, 2] = -120.0
    p0 = (m.mass[:, None] * m.v).sum(axis=0)
    p0_norm = float(np.linalg.norm(p0))

    m.add_impact("floor_hit", upp, mnode=low, nrm=[0.0, 0.0, 1.0], clr=1.0, mu=0.3)
    max_p_err = 0.0

    def check_mom(mm):
        nonlocal max_p_err
        p_now = (mm.mass[:, None] * mm.v).sum(axis=0)
        err = float(np.linalg.norm(p_now - p0)) / p0_norm
        if err > max_p_err:
            max_p_err = err

    m.run(0.06, monitor=check_mom, every=5)
    assert max_p_err < 0.01
    assert float(m.mass_phys.sum()) == pytest.approx(mass_before, rel=0.0)
    assert m.energy_summary()["rel_error"] < 0.05
    assert float(m.v[low, 2].mean()) < -30.0  # momentum transferred downward to receiving floor

    # Part B: shear-connection fracture -> detach without mass loss -> impact onto supported floor below
    m2 = xfe.Model(contact_alpha=0.1, contact_zeta=0.45)
    m2.add_material(xfe.elastic_material("el", E))
    m2.add_beam_section(xfe.w_beam_section("W24X55", "W24X55"))
    low2 = m2.add_nodes(np.column_stack([xs, np.zeros_like(xs), np.zeros_like(xs)]))
    upp2 = m2.add_nodes(np.column_stack([xs, np.zeros_like(xs), np.full_like(xs, 4.0)]))
    supL = m2.add_nodes([[0.0, 0.0, 4.0], [120.0, 0.0, 4.0]])
    m2.add_beams(np.column_stack([low2[:-1], low2[1:]]), "W24X55", "el", 0, "low")
    m2.add_beams(np.column_stack([upp2[:-1], upp2[1:]]), "W24X55", "el", 0, "upp")
    m2.add_mass(upp2, 0.04)
    m2.add_mass(low2, 0.04)
    m2.fix([low2[0], low2[-1]], (0, 1, 2, 3, 5))
    m2.fix(supL, (0, 1, 2, 3, 4, 5))
    m2.fix(np.concatenate([low2[1:-1], upp2]), (1, 3, 5))
    m2.finalize()

    js = xfe.JointSet(
        ["connL", "connR"], [upp2[0], upp2[-1]], [supL[0], supL[1]],
        kind=[0, 0], e10=[[1, 0, 0], [-1, 0, 0]], e20=[[0, 1, 0], [0, 1, 0]],
        kt=800.0, kc=2000.0, kv=800.0, ncap20=50.0, vcap20=25.0, x0=m2.x0,
    )
    m2.add_joint_set(js)
    ic2 = m2.add_impact("bay_drop", upp2, mnode=low2, nrm=[0.0, 0.0, 1.0], clr=2.0)

    mass2_before = float(m2.mass_phys.sum())
    W_upp = 80.0  # > 2 * 25 = 50 kip shear capacity => fractures both end joints
    f2 = np.zeros((m2.nn, 3))
    f2[upp2, 2] = -W_upp / len(upp2)
    m2.set_load_pattern(f2)
    m2.damping = 4.0
    m2.run(0.20, lam=lambda t: min(t / 0.02, 1.0))   # fracture + free-fall + dynamic impact
    m2.damping = 80.0
    m2.run(0.45, lam=lambda _t: 1.0)                 # post-impact settle to resting debris weight

    assert np.all(js.state == 2)
    assert float(m2.mass_phys.sum()) == pytest.approx(mass2_before, rel=0.0)
    assert ic2.out[2] == pytest.approx(W_upp, rel=0.03)
    assert m2.energy_summary()["rel_error"] < 0.05


def test_coupled_joint_mechanics_and_column_splice():
    """Verify (1) coupled (N/Ncap)^2 + (V/Vcap)^2 = 1 fracture, (2) STC seat bearing & 6.25-in. walk-off,
    and (3) column splice milled compression bearing vs uplift tension fracture."""
    # 1. Coupled tension-shear interaction: N = 60 kip (0.6 Ncap) => breaks at V = 80 kip (0.8 Vcap)
    m = xfe.Model()
    m.add_material(xfe.elastic_material("el", 29000.0))
    nA, nB = m.add_nodes([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    m.add_mass([nA, nB], 0.1)
    m.fix(nB, (0, 1, 2, 3, 4, 5))
    m.prescribe(nA, (0, 2))
    m.finalize()
    js = xfe.JointSet(["fin"], [nA], [nB], kind=[0], e10=[[1, 0, 0]], e20=[[0, 1, 0]],
                      kt=1000.0, kc=1000.0, kv=1000.0, ncap20=100.0, vcap20=100.0, x0=m.x0)
    m.add_joint_set(js)

    # Pull u1 = 0.06 in. (N = 60 kip) over 0.06 s, then shear u3 at 1.0 in./s until fracture at u3 = 0.08 in. (V = 80 kip)
    v_peaks = []
    m._prepare()
    while m.t < 0.18 and js.state[0] == 0:
        m.Tnow[:] = 20.0
        m.vpres[nA, 0] = 1.0 if m.t < 0.06 else 0.0
        m.vpres[nA, 2] = 0.0 if m.t < 0.06 else 1.0
        m.step(0.0)
        if js.state[0] == 0:
            v_peaks.append(float(js.fsv[0, 1]))
    assert js.state[0] == 2
    assert max(v_peaks) == pytest.approx(80.0, rel=0.02)

    # 2. Seated connection (STC): bolts break, girder stays supported on seat until u1 > 6.25 in. walk-off
    m2 = xfe.Model()
    m2.add_material(xfe.elastic_material("el", 29000.0))
    sA, sB = m2.add_nodes([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    m2.add_mass([sA, sB], 0.05)
    m2.fix(sB, (0, 1, 2, 3, 4, 5))
    m2.fix(sA, (1, 3, 4, 5))
    m2.prescribe(sA, (0,))
    m2.finalize()
    stc = xfe.JointSet(["A2001_STC"], [sA], [sB], kind=[1], e10=[[1, 0, 0]], e20=[[0, 1, 0]],
                       kt=500.0, kc=2000.0, kv=2000.0, ncap20=90.0, vcap20=90.0, walk_ax=6.25, x0=m2.x0)
    m2.add_joint_set(stc)
    m2.damping = 100.0
    f_down = np.zeros((m2.nn, 3))
    f_down[sA, 2] = -120.0
    m2.set_load_pattern(f_down)
    m2.vpres[sA, 0] = 20.0  # pulls out axially at 20 in./s: breaks bolts at ~0.009 s, walks off seat at 6.25/20 = 0.3125 s

    m2.run(0.20, lam=lambda _t: 1.0)
    assert stc.state[0] == 1                      # bolts broken, STILL resting on seat at u1 = 4.0 in. < 6.25 in.!
    assert abs(float(m2.x[sA, 2])) < 0.2          # seat is carrying the 120-kip vertical reaction!

    m2.run(0.42, lam=lambda _t: 1.0)
    assert stc.state[0] == 2                      # walked off 6.25-in. seat!
    assert float(m2.x[sA, 2]) < -1.0              # plunging freely after walk-off!

    # 3. Column splice (kind = 3): carries heavy milled compression even with broken plates; fails in uplift at Ncap
    m3 = xfe.Model()
    m3.add_material(xfe.elastic_material("el", 29000.0))
    cA, cB = m3.add_nodes([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    m3.add_mass([cA, cB], 0.2)
    m3.fix(cB, (0, 1, 2, 3, 4, 5))
    m3.fix(cA, (0, 1, 3, 4, 5))
    m3.finalize()
    sp = xfe.JointSet(["col_splice"], [cA], [cB], kind=[3], e10=[[0, 0, 1]], e20=[[1, 0, 0]],
                      kt=2000.0, kc=10000.0, kv=2000.0, ncap20=500.0, vcap20=500.0, walk_lat=14.0, x0=m3.x0)
    m3.add_joint_set(sp)
    m3.damping = 150.0

    # Compress with 5,000 kip (10x splice tension capacity!) -> milled bearing stays intact (state 0)
    fc = np.zeros((m3.nn, 3))
    fc[cA, 2] = -5000.0
    m3.set_load_pattern(fc)
    m3.run(0.08, lam=lambda t: min(t / 0.03, 1.0))
    assert sp.state[0] == 0
    assert float(m3.x[cA, 2]) == pytest.approx(-0.5, rel=0.02)

    # Reverse to +600 kip uplift (> 500 kip Ncap) -> splice plates fracture (state 1) and upper column lifts off!
    fc[cA, 2] = +600.0
    m3.set_load_pattern(fc)
    m3.run(0.16, lam=lambda _t: 1.0)
    assert sp.state[0] == 1
    assert float(m3.x[cA, 2]) > 0.5
