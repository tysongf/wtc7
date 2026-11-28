"""Explicit shell solver for the Phase 1 detailed model (wtc7.xfe).

The numerical work is in kernel.c (Belytschko-Lin-Tsay shells with temperature-
dependent J2 plasticity, contact, springs, central-difference update), compiled on
first use with gcc and OpenMP. This module assembles a model (nodes, shells,
materials, constraints, contact sets, springs), sets lumped masses and the stable
time step, and runs the explicit loop.

Units: kip, in., s, C. Temperatures are given per temperature group (for example
0 = ambient, 1 = beams, 2 = girder); every element and spring end belongs to one.
"""
from __future__ import annotations

import ctypes as C
import hashlib
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE / "kernel.c"
RHO_STEEL = 0.2836e-3 / 386.1          # kip s^2 / in^4
GAUSS5 = (np.array([-0.9061798459386640, -0.5384693101056831, 0.0, 0.5384693101056831, 0.9061798459386640]),
          np.array([0.2369268850561891, 0.4786286704993665, 0.5688888888888889, 0.4786286704993665,
                    0.2369268850561891]))

_dp = C.POINTER(C.c_double)
_ip = C.POINTER(C.c_int)
_up = C.POINTER(C.c_ubyte)


def _lib_path():
    digest = hashlib.sha256(SRC.read_bytes()).hexdigest()[:12]
    return HERE / f"_kernel_{digest}.so"


def load_kernel():
    """Compile kernel.c (once per source version) and bind its functions."""
    os.environ.setdefault("GOMP_SPINCOUNT", "20000")
    so = _lib_path()
    if not so.exists():
        for old in HERE.glob("_kernel_*.so"):
            old.unlink()
        cmd = ["gcc", "-O3", "-march=native", "-fopenmp", "-fPIC", "-shared", "-o", str(so), str(SRC), "-lm"]
        subprocess.run(cmd, check=True)
    lib = C.CDLL(str(so))
    lib.shell_forces.argtypes = [C.c_int, _ip, _dp, _ip, _ip, _dp, _dp, _dp, C.c_double, _dp, _dp,
                                 C.c_void_p, C.c_int, _dp, _dp, C.c_double, C.c_double,
                                 _dp, _dp, _dp, _dp, _dp, _dp]
    lib.gather.argtypes = [C.c_int, _ip, _ip, _dp, _dp]
    lib.gather_add.argtypes = [C.c_int, _ip, _ip, _dp, _dp, C.c_int]
    lib.gather_sparse.argtypes = [C.c_int, _ip, _ip, _ip, _dp, _dp]
    lib.integrate.argtypes = [C.c_int, _dp, _dp, _dp, _dp, _dp, _dp, C.c_double, _dp, _dp, _up, _dp,
                              C.c_int, _ip, _ip, _dp, C.c_double, C.c_double, _dp]
    lib.contact_plane.argtypes = [C.c_int, _ip, _dp, _dp, _dp, _dp, _dp, C.c_double, C.c_double,
                                  _dp, C.c_double, C.c_double, _dp, _dp, _dp]
    lib.contact_surface.argtypes = [C.c_int, _ip, _dp, _dp, _ip, _ip, _ip, _dp, C.c_double, _dp, _dp, _dp,
                                    _dp, C.c_double, C.c_double, _dp, C.c_double, C.c_double,
                                    _dp, _dp, _dp]
    lib.springs.argtypes = [C.c_int, _ip, _dp, _ip, _dp, _dp, _dp, _dp, _ip, _ip, _dp, _dp, _dp, _dp, _dp,
                            _up, _dp, _dp, _dp]
    lib.beam_forces.argtypes = [C.c_int, _ip, _ip, _ip, _ip, _dp, _dp, _dp, _dp, _dp, _dp,
                                _dp, _dp, C.c_void_p, C.c_int, _ip, _dp, _dp, _dp, _dp, _dp,
                                _up, _dp, _dp, _dp, _dp, _dp, _dp, _dp, _dp, _dp]
    lib.joints.argtypes = [C.c_int, _ip, _ip, _ip, _dp, _dp, _dp,
                           _dp, _dp, _dp, _dp, _dp, _dp, _dp,
                           _dp, _dp, _dp, _dp, _up, _dp, _dp, _dp, _dp, _dp, _dp]
    lib.joints.restype = C.c_int
    lib.contact_impact.argtypes = [C.c_int, _ip, _ip, _dp, _dp, _dp, _dp, _dp, _dp,
                                   _dp, _dp, C.c_double, C.c_double, _dp, C.c_double, C.c_double,
                                   _dp, _dp, _dp]
    lib.stress_update.argtypes = [C.c_void_p, C.c_int, C.c_double, C.c_double, _dp, _dp, C.c_double]
    lib.stress_update.restype = C.c_double
    lib.set_threads.argtypes = [C.c_int]
    lib.get_threads.restype = C.c_int
    if "OMP_NUM_THREADS" not in os.environ:
        lib.set_threads(min(4, max(1, (os.cpu_count() or 2) // 2)))
    return lib


def ptr(a):
    """ctypes pointer to a contiguous numpy array (the array must stay alive)."""
    if a.dtype == np.float64:
        return a.ctypes.data_as(_dp)
    if a.dtype == np.int32:
        return a.ctypes.data_as(_ip)
    if a.dtype == np.uint8:
        return a.ctypes.data_as(_up)
    raise TypeError(a.dtype)


class MatStruct(C.Structure):
    _fields_ = [("nmat", C.c_int), ("nT", C.c_int), ("nep", C.c_int), ("T0", C.c_double), ("dT", C.c_double),
                ("E", _dp), ("eth", _dp), ("ep", _dp), ("sy", _dp), ("nu", _dp), ("kind", _ip), ("syt", _dp)]


T_GRID = np.arange(0.0, 1200.0 + 1e-9, 5.0)
EP_GRID = np.concatenate([[0.0], np.geomspace(1e-5, 0.3, 79)])


@dataclass
class Material:
    """Tabulated material: E(T), thermal strain eth(T), flow stress sy(T, ep), Poisson ratio, density."""
    name: str
    E: np.ndarray
    eth: np.ndarray
    sy: np.ndarray            # (nT, nep)
    nu: float = 0.3
    rho: float = RHO_STEEL
    kind: int = 0             # 0 = J2 plasticity, 1 = elastic, 2 = separate tension curve sy_t
    sy_t: np.ndarray = None   # (nT, nep) tension flow curve for kind 2


def steel_material(name, set_name="NIST", grade="A572", fy_scale=1.0, rho=RHO_STEEL):
    """Tables from wtc7.materials.SteelModel (the same curves as the beam-element model)."""
    from wtc7.materials import SteelModel
    s = SteelModel(set_name, grade, fy_scale)
    E = np.array([s.E(max(T, 20.0)) for T in T_GRID])
    eth = np.array([s.eps_th(T) for T in T_GRID])
    sy = np.array([s.flow_table(max(T, 20.0), EP_GRID)[1] for T in T_GRID])
    return Material(name, E, eth, sy, 0.3, rho, 0)


def tension_compression_material(name, E, nu, rho, tension, compression):
    """Unheated J2 material with separate tension and compression flow curves, each given as
    (plastic strain, stress) points; the curve is chosen by the sign of the mean in-plane stress
    (the idea of LS-DYNA MAT_124, which NIST used for the composite slab, NCSTAR 1-9A §2.3.1)."""
    Ev = np.full(T_GRID.shape, float(E))
    eth = np.zeros(T_GRID.shape)
    sy = np.tile(np.interp(EP_GRID, *compression), (T_GRID.size, 1))
    syt = np.tile(np.interp(EP_GRID, *tension), (T_GRID.size, 1))
    return Material(name, Ev, eth, sy, nu, rho, 2, syt)


def elastic_material(name, E, alpha=0.0, nu=0.3, rho=RHO_STEEL, fy=None):
    """Constant E and alpha (thermal strain alpha (T - 20)); elastic, or perfectly plastic at fy."""
    Ev = np.full(T_GRID.shape, float(E))
    eth = alpha * (T_GRID - 20.0)
    sy = np.full((T_GRID.size, EP_GRID.size), 1e9 if fy is None else float(fy))
    return Material(name, Ev, eth, sy, nu, rho, 1 if fy is None else 0)


@dataclass
class PlaneContact:
    name: str
    nodes: np.ndarray         # slave nodes (int32)
    off: np.ndarray           # slave offsets (half thickness toward the plane)
    P: np.ndarray             # p0, n, t1, t2, lim (16)
    kn: np.ndarray            # per-slave normal penalty, kip/in.
    ktf: float                # tangential (stick) penalty as a fraction of kn
    mu: float
    cn: np.ndarray            # per-slave normal damping, kip s/in.
    gmax: float = 2.0
    ft: np.ndarray = None
    out: np.ndarray = field(default_factory=lambda: np.zeros(5))


NFIB = 16


@dataclass
class BeamSection:
    """3D fibre beam-column cross section (padded to NFIB = 16 fibres)."""
    name: str
    yf: np.ndarray      # (NFIB,) weak-axis fibre coords (along e2, across flange width)
    zf: np.ndarray      # (NFIB,) strong-axis fibre coords (along e3, along web depth)
    Af: np.ndarray      # (NFIB,) fibre areas, in^2
    J: float            # Saint-Venant torsional constant, in^4
    depth: float = 0.0
    width: float = 0.0

    def __post_init__(self):
        yf = np.asarray(self.yf, float).ravel()
        zf = np.asarray(self.zf, float).ravel()
        Af = np.asarray(self.Af, float).ravel()
        if len(Af) > NFIB:
            raise ValueError(f"BeamSection {self.name} has {len(Af)} > {NFIB} fibres")
        nz = np.nonzero(Af > 0.0)[0]
        self.n_active = int(nz[-1] + 1) if len(nz) else 0
        pad = NFIB - len(Af)
        if pad > 0:
            yf = np.pad(yf, (0, pad))
            zf = np.pad(zf, (0, pad))
            Af = np.pad(Af, (0, pad))
        self.yf = np.ascontiguousarray(yf)
        self.zf = np.ascontiguousarray(zf)
        self.Af = np.ascontiguousarray(Af)
        self.A = float(self.Af.sum())
        self.Ix = float((self.zf**2 * self.Af).sum())
        self.Iy = float((self.yf**2 * self.Af).sum())
        act = self.Af > 0.0
        self.ymax = float(np.abs(self.yf[act]).max()) if act.any() else 0.0
        self.zmax = float(np.abs(self.zf[act]).max()) if act.any() else 0.0
        self.is_doubly_sym = (
            abs(float((self.Af * self.yf).sum())) <= 1e-8 * max(self.A, 1.0)
            and abs(float((self.Af * self.zf).sum())) <= 1e-8 * max(self.A, 1.0)
            and abs(float((self.Af * self.yf * self.zf).sum())) <= 1e-8 * max(self.Ix + self.Iy, 1.0)
        )


def rect_beam_section(name: str, b: float, h: float) -> BeamSection:
    """Exact rectangular b (width along e2) x h (depth along e3) fibre section.
    Splits [-h/2, 0] and [0, h/2] into 4 Gauss points each x 2 Gauss points across [-b/2, b/2] = 16 fibres,
    reproducing A, Ix, Iy, Zx and Zy to machine precision."""
    xi4, w4 = np.polynomial.legendre.leggauss(4)
    xi2, w2 = np.polynomial.legendre.leggauss(2)
    z_neg = -0.25 * h + 0.25 * h * xi4
    z_pos = +0.25 * h + 0.25 * h * xi4
    zs = np.concatenate([z_neg, z_pos])
    wz = np.concatenate([0.25 * h * w4, 0.25 * h * w4])
    ys = 0.5 * b * xi2
    wy = 0.5 * b * w2
    Y, Z = np.meshgrid(ys, zs, indexing="ij")
    A = np.outer(wy, wz)
    a_long, a_short = max(b, h), min(b, h)
    r = a_short / a_long
    J = a_long * (a_short**3) * (1.0 / 3.0 - 0.21 * r * (1.0 - (r**4) / 12.0))
    return BeamSection(name, Y.ravel(), Z.ravel(), A.ravel(), float(J), depth=h, width=b)


def w_beam_section(name: str, shape_or_name, kind: str = "bare", pw: float = 0.0, pt: float = 0.0) -> BeamSection:
    """W-shape (bare: 12 active fibres; built-up with 'side' or 'web' plates: 16 fibres).
    Reproduces exact A, Ix, Iy and accurate plastic moduli Zx, Zy."""
    from wtc7.sections import shape as get_shape
    s = get_shape(shape_or_name) if isinstance(shape_or_name, str) else shape_or_name
    # 2-point Gauss-Legendre on each half-interval [-1/2, 0] and [0, 1/2] integrates A, Z, and I exactly:
    g4 = 0.5 * np.array([-0.5 - 0.5 / np.sqrt(3.0), -0.5 + 0.5 / np.sqrt(3.0),
                         +0.5 - 0.5 / np.sqrt(3.0), +0.5 + 0.5 / np.sqrt(3.0)])
    yc = s.bf * g4
    afl = np.full(4, 0.25 * s.bf * s.tf)
    afl *= s.Iy / (2.0 * float((afl * yc**2).sum()))
    a_web_tot = max(s.A - 2.0 * float(afl.sum()), 1e-6)
    hw = max(s.d - 2.0 * s.tf, 0.1 * s.d)
    zw = hw * g4
    aw = np.full(4, a_web_tot / 4.0)
    ix_rem = max(s.Ix - float((aw * zw**2).sum()), 1e-6)
    zfl = np.sqrt(ix_rem / (2.0 * float(afl.sum())))

    yf = np.concatenate([yc, yc, np.zeros(4)])
    zf = np.concatenate([np.full(4, zfl), np.full(4, -zfl), zw])
    Af = np.concatenate([afl, afl, aw])
    J = float(s.J)
    width = float(s.bf)
    depth = float(s.d)

    if kind in ("side", "web") and pw > 0.0 and pt > 0.0:
        zp = np.array([-pw / np.sqrt(12.0), +pw / np.sqrt(12.0)])
        ap = np.full(2, 0.5 * pw * pt)
        xc = (s.bf / 2.0 + pt / 2.0) if kind == "side" else (s.tw / 2.0 + pt / 2.0)
        y_eff = np.sqrt(xc**2 + (pt**2) / 12.0)
        yf = np.concatenate([yf, np.full(2, -y_eff), np.full(2, +y_eff)])
        zf = np.concatenate([zf, zp, zp])
        Af = np.concatenate([Af, ap, ap])
        if kind == "side":
            # Closed box cell formed by flanges + side cover plates (Bredt torsion)
            a_enc = (s.bf + pt) * max(s.d - s.tf, 1.0)
            perim_t = 2.0 * (s.bf / max(s.tf, 0.1)) + 2.0 * (max(s.d - s.tf, 1.0) / pt)
            J += 4.0 * (a_enc**2) / perim_t
            width = s.bf + 2.0 * pt
            depth = max(s.d, pw)
        else:
            J += 2.0 * pw * (pt**3) / 3.0
    return BeamSection(name, yf, zf, Af, J, depth=depth, width=width)


@dataclass
class ImpactContact:
    """Mass-conserving node-to-master-patch (1 to 4 lower nodes, or fixed floor point) impact contact."""
    name: str
    snode: np.ndarray     # (ni,) int32 upper/falling nodes
    mnode: np.ndarray     # (ni, 4) int32 lower/receiving nodes (-1 padded; mnode[:,0] < 0 => fixed mpos)
    mw: np.ndarray        # (ni, 4) interpolation weights summing to 1
    mpos: np.ndarray      # (ni, 3) fixed points if mnode[:,0] < 0
    nrm: np.ndarray       # (ni, 3) unit contact normals (master -> slave)
    clr: np.ndarray       # (ni,) clearance offset along nrm
    kn: np.ndarray        # (ni,) normal penalty stiffness, kip/in.
    meff: np.ndarray      # (ni,) two-body reduced mass, kip s^2/in.
    ktf: float
    mu: float
    cn: np.ndarray        # (ni,) normal viscous damping, kip s/in.
    gmax: float = 60.0
    ft: np.ndarray = None
    out: np.ndarray = field(default_factory=lambda: np.zeros(6))


class JointSet:
    """Coupled 6-DOF breakable connections & column splices (see kernel.c joints()).

    jkind:
      0 = simple shear (F, K, H, STP): coupled tension-shear bolt/weld fracture -> detached (state 2)
      1 = seated (STC, SWC): bolt fracture -> seat-bearing state 1; walk-off (u1 > walk_ax or |u2| > walk_lat) -> state 2
      2 = moment connection (MC): elastoplastic bending (kr, mpcap20) + fracture rotation thu or bolt/weld fracture -> state 2
      3 = column splice: milled compression bearing (u1 < 0) + splice plate tension/shear/bending; plate fracture -> state 1,
          lateral shear offset > walk_lat -> state 2
    """

    def __init__(self, names, na, nb, kind, e10, e20, kt, kc, kv, ncap20, vcap20, x0,
                 pB=None, gap_c=0.0, walk_ax=6.25, walk_lat=5.5, kr=0.0, mpcap20=0.0, thu=0.0,
                 tgroup=0, factor_fn=None, initial_state=0):
        self.names = list(names)
        n = len(self.names)
        self.na = np.ascontiguousarray(np.broadcast_to(np.asarray(na, np.int32), (n,)).copy())
        self.nb = np.ascontiguousarray(np.broadcast_to(np.asarray(nb, np.int32), (n,)).copy())
        self.kind = np.ascontiguousarray(np.broadcast_to(np.asarray(kind, np.int32), (n,)).copy())
        if pB is None:
            pB_arr = np.zeros((n, 3))
            neg = self.nb < 0
            if neg.any():
                pB_arr[neg] = x0[self.na[neg]]
        else:
            pB_arr = np.broadcast_to(np.asarray(pB, float), (n, 3)).copy()
        self.pB = np.ascontiguousarray(pB_arr)

        xb0 = np.where((self.nb >= 0)[:, None], x0[np.maximum(self.nb, 0)], self.pB)
        self.r0 = np.ascontiguousarray(x0[self.na] - xb0)

        e1 = np.broadcast_to(np.asarray(e10, float), (n, 3)).copy()
        e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
        e2 = np.broadcast_to(np.asarray(e20, float), (n, 3)).copy()
        e2 = e2 - np.sum(e2 * e1, axis=1, keepdims=True) * e1
        e2 /= np.linalg.norm(e2, axis=1, keepdims=True)
        e3 = np.cross(e1, e2)
        self.je0 = np.ascontiguousarray(np.hstack([e1, e2, e3]))

        def _arr(v):
            return np.ascontiguousarray(np.broadcast_to(np.asarray(v, float), (n,)).copy())

        self.kt, self.kc, self.kv = _arr(kt), _arr(kc), _arr(kv)
        self.gap_c, self.walk_ax, self.walk_lat = _arr(gap_c), _arr(walk_ax), _arr(walk_lat)
        self.kr, self.thu = _arr(kr), _arr(thu)
        self.ncap20, self.vcap20, self.mpcap20 = _arr(ncap20), _arr(vcap20), _arr(mpcap20)
        self.ncap, self.vcap, self.mpcap = self.ncap20.copy(), self.vcap20.copy(), self.mpcap20.copy()
        self.tgroup = np.ascontiguousarray(np.broadcast_to(np.asarray(tgroup, np.int32), (n,)).copy())
        self.factor_fn = factor_fn
        self.state = np.ascontiguousarray(np.broadcast_to(np.asarray(initial_state, np.uint8), (n,)).copy())
        self.jq = np.zeros((n, 4))
        self.jfbe = np.zeros((n, 12))
        self.jg_ptr = None
        self.jg_idx = None
        self.jg_nodes = None
        self.fsv = np.zeros((n, 8))
        self._lost_buf = np.zeros(1)
        self._last_Tg = None
        self.lost_energy = 0.0
        self.break_time = np.full(n, np.nan)
        self.detach_time = np.full(n, np.nan)

    def build_gather(self, nn: int):
        """Build lock-free sparse CSR gather index mapping (2*i + 0 -> na[i], 2*i + 1 -> nb[i] if >= 0)."""
        n = len(self.names)
        slots_a = 2 * np.arange(n, dtype=np.int32)
        nodes_a = self.na
        has_b = self.nb >= 0
        slots_b = 2 * np.nonzero(has_b)[0].astype(np.int32) + 1
        nodes_b = self.nb[has_b]
        all_nodes = np.concatenate([nodes_a, nodes_b])
        all_slots = np.concatenate([slots_a, slots_b])
        order = np.argsort(all_nodes, kind="stable")
        counts = np.bincount(all_nodes, minlength=nn)
        self.jg_ptr = np.ascontiguousarray(np.concatenate([[0], np.cumsum(counts)]).astype(np.int32))
        self.jg_idx = np.ascontiguousarray(all_slots[order].astype(np.int32))
        self.jg_nodes = np.ascontiguousarray(np.nonzero(counts > 0)[0].astype(np.int32))

    def apply(self, model, Tg):
        if self.jg_ptr is None or len(self.jg_ptr) != model.nn + 1:
            self.build_gather(model.nn)
        if self._last_Tg is None or not np.array_equal(Tg, self._last_Tg):
            self._last_Tg = Tg.copy()
            if self.factor_fn is not None:
                T = Tg[np.minimum(self.tgroup, len(Tg) - 1)]
                fac = np.asarray(self.factor_fn(T), float)
                np.multiply(self.ncap20, fac, out=self.ncap)
                np.multiply(self.vcap20, fac, out=self.vcap)
                np.multiply(self.mpcap20, fac, out=self.mpcap)
            else:
                self.ncap[:] = self.ncap20
                self.vcap[:] = self.vcap20
                self.mpcap[:] = self.mpcap20
        n_changed = model.lib.joints(
            len(self.names), ptr(self.na), ptr(self.nb), ptr(self.kind), ptr(self.pB),
            ptr(self.r0), ptr(self.je0),
            ptr(self.kt), ptr(self.kc), ptr(self.kv), ptr(self.gap_c),
            ptr(self.walk_ax), ptr(self.walk_lat), ptr(self.kr),
            ptr(self.ncap), ptr(self.vcap), ptr(self.mpcap), ptr(self.thu),
            ptr(self.state), ptr(self.jq), ptr(model.x), ptr(model.Rnode),
            ptr(self.jfbe), ptr(self.fsv), ptr(self._lost_buf)
        )
        model.lib.gather_sparse(len(self.jg_nodes), ptr(self.jg_nodes), ptr(self.jg_ptr), ptr(self.jg_idx),
                                ptr(self.jfbe), ptr(model.fint))
        if n_changed > 0:
            self.lost_energy += float(self._lost_buf[0])
            b1 = np.nonzero(np.isnan(self.break_time) & (self.state >= 1))[0]
            if len(b1):
                self.break_time[b1] = model.t
            b2 = np.nonzero(np.isnan(self.detach_time) & (self.state == 2))[0]
            if len(b2):
                self.detach_time[b2] = model.t

    def stored_energy(self) -> float:
        return float(self.fsv[:, 5].sum())

    def plastic_work(self) -> float:
        return float(self.fsv[:, 6].sum())

    def internal_work(self) -> float:
        return float(self.fsv[:, 5].sum() + self.fsv[:, 6].sum())


@dataclass
class SurfaceContact:
    name: str
    snode: np.ndarray         # int32, -1 for fixed points
    spos: np.ndarray          # (ns, 3) fixed point positions
    soff: np.ndarray
    cur: np.ndarray           # int32 current master element
    nbr: np.ndarray           # int32 (nel, 4) neighbour table for the master set
    mfac: float
    dref: np.ndarray
    kn: np.ndarray
    ktf: float
    mu: float
    cn: np.ndarray
    gmax: float = 2.0
    ft: np.ndarray = None
    out: np.ndarray = field(default_factory=lambda: np.zeros(5))


class Model:
    """Explicit shell and 3D fibre beam-column model. Build with add_* calls, then finalize() and run()."""

    def __init__(self, nip=5, qhg=0.05, kappa=5.0 / 6.0, contact_alpha=0.1, contact_zeta=0.1):
        self.nip, self.qhg, self.kappa = nip, qhg, kappa
        self.contact_alpha, self.contact_zeta = contact_alpha, contact_zeta
        self.no_dt_parts = ("fin",)         # small plates that are mass-scaled rather than setting the time step
        self._x, self._conn, self._h, self._mat, self._tg, self._part = [], [], [], [], [], []
        self._bconn, self._bsec, self._bmat, self._btg, self._bup = [], [], [], [], []
        self._nn_count = 0
        self._ne_count = 0
        self._nb_count = 0
        self.beam_sections: list[BeamSection] = []
        self.sec_index = {}
        self.beam_parts = {}
        self._added_nodal_mass = []         # list of (node_idx, m, rin)
        self.materials: list[Material] = []
        self.mat_index = {}
        self.parts = {}
        self.planes: list[PlaneContact] = []
        self.surfaces: list[SurfaceContact] = []
        self.impacts: list[ImpactContact] = []
        self.spring_sets = []
        self.joint_sets: list[JointSet] = []
        self._fixed = []
        self._presc = []
        self._cons = []
        self.added_mass = None
        self.lib = load_kernel()

    # ---------------------------------------------------------------- building
    def add_nodes(self, xyz):
        xyz = np.atleast_2d(np.asarray(xyz, float))
        start = self._nn_count
        self._x.append(xyz)
        self._nn_count += len(xyz)
        return np.arange(start, start + len(xyz), dtype=np.int32)

    def add_material(self, m: Material):
        self.mat_index[m.name] = len(self.materials)
        self.materials.append(m)
        return self.mat_index[m.name]

    def add_beam_section(self, s: BeamSection):
        self.sec_index[s.name] = len(self.beam_sections)
        self.beam_sections.append(s)
        return self.sec_index[s.name]

    def add_shells(self, conn, h, mat, tgroup, part):
        conn = np.atleast_2d(np.asarray(conn, np.int32))
        start = self._ne_count
        n = len(conn)
        self._ne_count += n
        self._conn.append(conn)
        self._h.append(np.broadcast_to(np.asarray(h, float), (n,)).copy())
        self._mat.append(np.full(n, self.mat_index[mat] if isinstance(mat, str) else mat, np.int32))
        self._tg.append(np.full(n, tgroup, np.int32))
        ids = np.arange(start, start + n, dtype=np.int32)
        self.parts.setdefault(part, []).append(ids)
        return ids

    def add_beams(self, conn, section, mat, tgroup=0, part="beam", up=None):
        """Add 2-node 3D co-rotational fibre beam-column elements.
        `up` sets the reference strong-axis (+e3, web depth) direction; defaults to +Z for
        non-vertical members and +X for vertical columns."""
        conn = np.atleast_2d(np.asarray(conn, np.int32))
        start = self._nb_count
        n = len(conn)
        self._nb_count += n
        sec_id = self.sec_index[section] if isinstance(section, str) else int(section)
        mat_id = self.mat_index[mat] if isinstance(mat, str) else int(mat)
        self._bconn.append(conn)
        self._bsec.append(np.full(n, sec_id, np.int32))
        self._bmat.append(np.full(n, mat_id, np.int32))
        self._btg.append(np.broadcast_to(np.asarray(tgroup, np.int32), (n,)).copy())
        if up is None:
            up_arr = np.full((n, 3), np.nan)
        else:
            up_arr = np.broadcast_to(np.asarray(up, float), (n, 3)).copy()
        self._bup.append(up_arr)
        ids = np.arange(start, start + n, dtype=np.int32)
        self.beam_parts.setdefault(part, []).append(ids)
        return ids

    def add_mass(self, nodes, m, rinert=0.0):
        """Add physical lumped translational mass (kip s^2/in.) and optional rotary inertia to nodes."""
        nodes = np.atleast_1d(np.asarray(nodes, np.int32))
        m_arr = np.broadcast_to(np.asarray(m, float), nodes.shape).copy()
        r_arr = np.broadcast_to(np.asarray(rinert, float), nodes.shape).copy()
        self._added_nodal_mass.append((nodes, m_arr, r_arr))

    def beam_part(self, name):
        return np.concatenate(self.beam_parts[name])

    def fix(self, nodes, dofs=(0, 1, 2, 3, 4, 5)):
        for n in np.atleast_1d(nodes):
            for d in dofs:
                self._fixed.append((int(n), int(d)))

    def prescribe(self, nodes, dofs):
        """DOFs whose velocity is set each cycle from self.vpres (nn, 6)."""
        for n in np.atleast_1d(nodes):
            for d in dofs:
                self._presc.append((int(n), int(d)))

    def constrain(self, nodes, kind, direction):
        """Remove the velocity component along direction (kind 0 translation, 1 rotation)."""
        d = np.asarray(direction, float)
        d = d / np.linalg.norm(d)
        for n in np.atleast_1d(nodes):
            self._cons.append((int(n), int(kind), d))

    def part(self, name):
        return np.concatenate(self.parts[name])

    # ---------------------------------------------------------------- finalize
    def finalize(self, dt_safety=0.9, dt_min=None, rot_factor=0.125):
        """Lumped masses, rotary inertia, CSR gather table, time step.

        Supports shell-only, beam-only, and hybrid shell+beam models.
        """
        self.dt_safety = dt_safety
        self.x0 = np.ascontiguousarray(np.concatenate(self._x))
        nn = len(self.x0)
        self.nn = nn

        # ---- Shells ----
        if self._conn:
            self.conn = np.ascontiguousarray(np.concatenate(self._conn))
            self.h = np.concatenate(self._h)
            self.mat = np.concatenate(self._mat)
            self.tg = np.concatenate(self._tg)
            ne = len(self.conn)
        else:
            self.conn = np.zeros((0, 4), np.int32)
            self.h = np.zeros(0, float)
            self.mat = np.zeros(0, np.int32)
            self.tg = np.zeros(0, np.int32)
            ne = 0
        self.ne = ne

        # ---- Beams ----
        if self._bconn:
            self.bconn = np.ascontiguousarray(np.concatenate(self._bconn))
            self.bsec = np.ascontiguousarray(np.concatenate(self._bsec))
            self.bmat = np.ascontiguousarray(np.concatenate(self._bmat))
            self.btg = np.ascontiguousarray(np.concatenate(self._btg))
            bup = np.concatenate(self._bup)
            nb = len(self.bconn)
        else:
            self.bconn = np.zeros((0, 2), np.int32)
            self.bsec = np.zeros(0, np.int32)
            self.bmat = np.zeros(0, np.int32)
            self.btg = np.zeros(0, np.int32)
            bup = np.zeros((0, 3), float)
            nb = 0
        self.nb = nb

        self.mass = np.zeros(nn)
        self.mass_phys = np.zeros(nn)
        rin = np.zeros(nn)
        dt_candidates = []

        if ne > 0:
            X = self.x0[self.conn]
            d1 = np.linalg.norm(X[:, 2] - X[:, 0], axis=1)
            d2 = np.linalg.norm(X[:, 3] - X[:, 1], axis=1)
            area = 0.5 * np.linalg.norm(np.cross(X[:, 2] - X[:, 0], X[:, 3] - X[:, 1]), axis=1)
            self.area = area
            rho = np.array([m.rho for m in self.materials])[self.mat]
            E20 = np.array([m.E.max() for m in self.materials])[self.mat]
            nu = np.array([m.nu for m in self.materials])[self.mat]
            c = np.sqrt(E20 / (rho * (1 - nu**2)))
            Ls = area / np.maximum(d1, d2)
            dte = Ls / c
            me = rho * self.h * area
            scale = np.ones(ne)
            if isinstance(dt_min, str) and dt_min == "auto":
                dt_min = min(float(np.median(dte[np.concatenate(v)])) for k, v in self.parts.items()
                             if not k.startswith(self.no_dt_parts))
            self.dt_min = dt_min
            if dt_min is not None:
                small = dte < dt_min
                scale[small] = (dt_min / dte[small]) ** 2
                dte = np.maximum(dte, dt_min)
            self.elem_dt = dte
            for I in range(4):
                np.add.at(self.mass, self.conn[:, I], 0.25 * me * scale)
                np.add.at(self.mass_phys, self.conn[:, I], 0.25 * me)
                np.add.at(rin, self.conn[:, I], 0.25 * me * scale * np.maximum(self.h**2 / 12, rot_factor * area))
            dt_candidates.append(float(dte.min()))
            slots = np.argsort(self.conn.ravel(), kind="stable")
            counts = np.bincount(self.conn.ravel(), minlength=nn)
            self.g_ptr = np.concatenate([[0], np.cumsum(counts)]).astype(np.int32)
            self.g_idx = slots.astype(np.int32)
        else:
            self.area = np.zeros(0)
            self.elem_dt = np.zeros(0)
            self.dt_min = dt_min if not isinstance(dt_min, str) else None
            self.g_ptr = np.zeros(nn + 1, np.int32)
            self.g_idx = np.zeros(0, np.int32)

        if nb > 0:
            dX = self.x0[self.bconn[:, 1]] - self.x0[self.bconn[:, 0]]
            L0 = np.linalg.norm(dX, axis=1)
            self.bL0 = np.ascontiguousarray(L0)
            e10 = dX / L0[:, None]
            up_ref = bup.copy()
            auto = np.isnan(up_ref[:, 0])
            if auto.any():
                vert = np.abs(e10[:, 2]) >= 0.99
                up_def = np.where(vert[:, None], np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]))
                up_ref[auto] = up_def[auto]
            e20 = np.cross(up_ref, e10)
            n2 = np.linalg.norm(e20, axis=1)
            bad = n2 < 1e-6
            if bad.any():
                alt = np.where((np.abs(e10[:, 0]) < 0.9)[:, None], np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]))
                e20[bad] = np.cross(alt[bad], e10[bad])
                n2 = np.linalg.norm(e20, axis=1)
            e20 /= n2[:, None]
            e30 = np.cross(e10, e20)
            self.be0 = np.ascontiguousarray(np.hstack([e10, e20, e30]))

            sec_A = np.array([s.A for s in self.beam_sections])[self.bsec]
            sec_Imax = np.array([max(s.Ix, s.Iy) for s in self.beam_sections])[self.bsec]
            sec_J = np.array([s.J for s in self.beam_sections])[self.bsec]
            brho = np.array([m.rho for m in self.materials])[self.bmat]
            bE = np.array([m.E.max() for m in self.materials])[self.bmat]
            bnu = np.array([m.nu for m in self.materials])[self.bmat]
            bG = bE / (2.0 * (1.0 + bnu))
            bc = np.sqrt(bE / brho)
            rmax = np.sqrt(np.maximum(sec_Imax / np.maximum(sec_A, 1e-12), 1e-12))
            mb = brho * sec_A * L0
            dt_ax = L0 / bc
            kth_end = np.maximum(6.0 * bE * sec_Imax / L0, 2.0 * bG * sec_J / L0)
            rin_base = np.maximum(0.5 * mb * (rmax**2 + rot_factor * (L0**2)), kth_end * (dt_ax**2))
            w2_ax = (2.0 * bc / L0) ** 2
            w2_tors = (2.0 * bG * sec_J / L0) / rin_base
            w2_bend = (24.0 * bE * sec_Imax / (L0**3)) / (0.5 * mb) + (6.0 * bE * sec_Imax / L0) / rin_base
            dtb = 2.0 / np.sqrt(np.maximum(np.maximum(w2_ax, w2_tors), w2_bend))
            bscale = np.ones(nb)
            if self.dt_min is not None:
                small_b = dtb < self.dt_min
                bscale[small_b] = (self.dt_min / dtb[small_b]) ** 2
                dtb = np.maximum(dtb, self.dt_min)
            self.beam_dt = dtb
            rin_end = rin_base * bscale
            for I in range(2):
                np.add.at(self.mass, self.bconn[:, I], 0.5 * mb * bscale)
                np.add.at(self.mass_phys, self.bconn[:, I], 0.5 * mb)
                np.add.at(rin, self.bconn[:, I], rin_end)
            dt_candidates.append(float(dtb.min()))

            bslots = np.argsort(self.bconn.ravel(), kind="stable")
            bcounts = np.bincount(self.bconn.ravel(), minlength=nn)
            self.bg_ptr = np.concatenate([[0], np.cumsum(bcounts)]).astype(np.int32)
            self.bg_idx = bslots.astype(np.int32)

            nsec = len(self.beam_sections)
            self.s_nact = np.ascontiguousarray(np.array([s.n_active for s in self.beam_sections], np.int32))
            self.s_yf = np.ascontiguousarray(np.array([s.yf for s in self.beam_sections]))
            self.s_zf = np.ascontiguousarray(np.array([s.zf for s in self.beam_sections]))
            self.s_Af = np.ascontiguousarray(np.array([s.Af for s in self.beam_sections]))
            self.s_props = np.ascontiguousarray(np.array(
                [[s.A, s.Ix, s.Iy, s.ymax, s.zmax] for s in self.beam_sections], float
            ))
            self.s_J = np.ascontiguousarray(np.array([s.J for s in self.beam_sections], float))
        else:
            self.bL0 = np.zeros(0)
            self.be0 = np.zeros((0, 9))
            self.beam_dt = np.zeros(0)
            self.bg_ptr = np.zeros(nn + 1, np.int32)
            self.bg_idx = np.zeros(0, np.int32)
            self.s_nact = np.zeros(0, np.int32)
            self.s_yf = np.zeros((0, NFIB))
            self.s_zf = np.zeros((0, NFIB))
            self.s_Af = np.zeros((0, NFIB))
            self.s_props = np.zeros((0, 5))
            self.s_J = np.zeros(0)

        for nd_i, m_i, r_i in self._added_nodal_mass:
            np.add.at(self.mass, nd_i, m_i)
            np.add.at(self.mass_phys, nd_i, m_i)
            np.add.at(rin, nd_i, r_i)

        self.added_mass = float(self.mass.sum() - self.mass_phys.sum())
        orphan = self.mass == 0
        self.mass[orphan] = 1.0
        rin[orphan] = 1.0
        no_rin = rin == 0
        rin[no_rin] = self.mass[no_rin]
        self.rinert = rin
        self.dt = dt_safety * (min(dt_candidates) if dt_candidates else 1e-4)

        # constraints
        self.fixmask = np.zeros(nn * 6, np.uint8)
        for n, d in self._fixed:
            self.fixmask[6 * n + d] = 1
        for n, d in self._presc:
            self.fixmask[6 * n + d] = 2
        self.vpres = np.zeros((nn, 6))
        self.c_node = np.array([c[0] for c in self._cons], np.int32)
        self.c_type = np.array([c[1] for c in self._cons], np.int32)
        self.c_dir = np.ascontiguousarray(np.array([c[2] for c in self._cons], float).reshape(-1, 3))
        # materials
        nmat = len(self.materials)
        self.m_E = np.ascontiguousarray(np.array([m.E for m in self.materials]))
        self.m_eth = np.ascontiguousarray(np.array([m.eth for m in self.materials]))
        self.m_ep = np.ascontiguousarray(np.tile(EP_GRID, (nmat, 1)))
        self.m_sy = np.ascontiguousarray(np.array([m.sy for m in self.materials]))
        self.m_syt = np.ascontiguousarray(np.array([m.sy if m.sy_t is None else m.sy_t for m in self.materials]))
        self.m_nu = np.array([m.nu for m in self.materials], float)
        self.m_kind = np.array([m.kind for m in self.materials], np.int32)
        self.matstruct = MatStruct(nmat, T_GRID.size, EP_GRID.size, float(T_GRID[0]), float(T_GRID[1] - T_GRID[0]),
                                   ptr(self.m_E), ptr(self.m_eth), ptr(self.m_ep), ptr(self.m_sy), ptr(self.m_nu),
                                   ptr(self.m_kind), ptr(self.m_syt))
        self.zeta, self.wz = (GAUSS5 if self.nip == 5 else np.polynomial.legendre.leggauss(self.nip))
        self.zeta, self.wz = np.ascontiguousarray(self.zeta, float), np.ascontiguousarray(self.wz, float)
        # state
        self.x = self.x0.copy()
        self.Rnode = np.ascontiguousarray(np.tile(np.eye(3).ravel(), (nn, 1)))
        self.v = np.zeros((nn, 3))
        self.w = np.zeros((nn, 3))
        self.sig = np.zeros((ne, self.nip, 3))
        self.epsp = np.zeros((ne, self.nip))
        self.qs = np.zeros((ne, 2))
        self.hgs = np.zeros((ne, 5))
        self.fe = np.zeros((ne, 24))
        # beam state
        self.bfac = np.ones(nb, float)
        self.bfac_prev = np.ones(nb, float)
        sym_sec = np.array([s.is_doubly_sym for s in self.beam_sections], bool)
        self.b_plastic = np.ascontiguousarray((~sym_sec[self.bsec]).astype(np.uint8) if nb > 0 else np.zeros(0, np.uint8))
        self.bel = np.zeros((nb, 9))
        self.bq = np.zeros((nb, 6))
        self.bsig = np.zeros((nb, 3, NFIB))
        self.bepsp = np.zeros((nb, 3, NFIB))
        self.bm1 = np.zeros(nb)
        self.fbe = np.zeros((nb, 12))
        self.bdiag = np.zeros((nb, 6))
        self.removed_energy = np.zeros(1)

        self.fint = np.zeros((nn, 6))
        self.fpat = np.zeros((nn, 6))
        self._prepared = False
        self.energy = np.zeros(4)          # IE (elastic + plastic), hourglass, plastic, thermal input
        self.kinout = np.zeros(3)          # KE, damping work, w_ext
        self.w_ext = 0.0
        self.ke0 = None
        self.t = 0.0
        self.cycle = 0
        self.damping = 0.0
        self._pat_idx = None
        self._pat_rot_idx = None
        return self

    # ---------------------------------------------------------------- contact
    def neighbours(self, elems):
        """(ne, 4) neighbour table restricted to the element set elems (edge k = nodes k, k+1)."""
        nbr = -np.ones((self.ne, 4), np.int32)
        edge = {}
        for e in elems:
            c = self.conn[e]
            for k in range(4):
                key = tuple(sorted((int(c[k]), int(c[(k + 1) % 4]))))
                edge.setdefault(key, []).append((int(e), k))
        for lst in edge.values():
            if len(lst) == 2:
                (e1, k1), (e2, k2) = lst
                nbr[e1, k1], nbr[e2, k2] = e2, e1
        return nbr

    def penalty(self, masses, alpha=None, zeta=None):
        """Penalty stiffness alpha m / dt^2 and normal damping 2 zeta sqrt(k m) for slave masses m.

        Scaling the penalty with the slave mass keeps contact from lowering the stable
        time step (LS-DYNA's SOFT = 1 idea)."""
        alpha = self.contact_alpha if alpha is None else alpha
        zeta = self.contact_zeta if zeta is None else zeta
        m = np.asarray(masses, float)
        k = alpha * m / self.dt**2
        return k, 2.0 * zeta * np.sqrt(k * m)

    def add_plane(self, name, nodes, off, p0, n, t1, lim, mu=0.0, ktf=1.0, alpha=None, zeta=None, gmax=2.0):
        """Rigid rectangle p0 + s1 t1 + s2 t2, s1 in lim[0:2], s2 in lim[2:4], outward normal n."""
        n = np.asarray(n, float) / np.linalg.norm(n)
        t1 = np.asarray(t1, float)
        t1 = t1 - (t1 @ n) * n
        t1 /= np.linalg.norm(t1)
        t2 = np.cross(n, t1)
        P = np.concatenate([p0, n, t1, t2, lim]).astype(float)
        nodes = np.asarray(nodes, np.int32)
        off = np.broadcast_to(np.asarray(off, float), nodes.shape).copy()
        kn, cn = self.penalty(self.mass[nodes], alpha, zeta)
        pc = PlaneContact(name, nodes, off, P, kn, ktf, mu, cn, gmax, np.zeros((len(nodes), 3)))
        self.planes.append(pc)
        self._prepared = False
        return pc

    def add_surface(self, name, master, dref, mfac=0.5, mu=0.0, ktf=1.0, alpha=None, zeta=None, gmax=2.0,
                    nodes=None, points=None, off=0.0):
        """Slave nodes (or fixed points) against the shell surface made of elements `master`.

        The penalty uses the slave node mass, or for fixed points the mean node mass of
        the master elements."""
        from scipy.spatial import cKDTree
        master = np.asarray(master, np.int32)
        if nodes is not None:
            snode = np.asarray(nodes, np.int32)
            spos = np.zeros((len(snode), 3))
            P = self.x[snode]
            ms = self.mass[snode]
        else:
            spos = np.ascontiguousarray(np.asarray(points, float))
            snode = -np.ones(len(spos), np.int32)
            P = spos
        cen = self.x[self.conn[master]].mean(axis=1)
        cur = master[cKDTree(cen).query(P)[1]].astype(np.int32)
        if nodes is None:
            ms = self.mass[self.conn[cur]].mean(axis=1)
        soff = np.broadcast_to(np.asarray(off, float), snode.shape).copy()
        kn, cn = self.penalty(ms, alpha, zeta)
        sc = SurfaceContact(name, snode, spos, soff, cur, self.neighbours(master), mfac,
                            np.asarray(dref, float), kn, ktf, mu, cn, gmax, np.zeros((len(snode), 3)))
        self.surfaces.append(sc)
        self._prepared = False
        return sc

    def element_point(self, elems, p):
        """For each point p (n, 3) inside element elems[i], node ids and bilinear weights (n, 4)."""
        out_n, out_w = [], []
        for e, q in zip(np.atleast_1d(elems), np.atleast_2d(p)):
            X = self.x0[self.conn[e]]
            e1, e2, e3 = _frame(X)
            xc = X.mean(0)
            xl, yl = (X - xc) @ e1, (X - xc) @ e2
            px, py = (q - xc) @ e1, (q - xc) @ e2
            a = b = 0.0
            for _ in range(20):
                N = 0.25 * (1 + a * XI) * (1 + b * ETA)
                dxi = 0.25 * XI * (1 + b * ETA)
                deta = 0.25 * ETA * (1 + a * XI)
                J = np.array([[dxi @ xl, deta @ xl], [dxi @ yl, deta @ yl]])
                r = np.array([N @ xl - px, N @ yl - py])
                da = np.linalg.solve(J, r)
                a, b = a - da[0], b - da[1]
                if abs(da).sum() < 1e-13:
                    break
            out_n.append(self.conn[e])
            out_w.append(0.25 * (1 + a * XI) * (1 + b * ETA))
        return np.array(out_n, np.int32), np.array(out_w)

    def find_element(self, elems, p):
        """Element of the set containing each point (nearest centre, then checked by projection)."""
        from scipy.spatial import cKDTree
        elems = np.asarray(elems)
        tree = cKDTree(self.x0[self.conn[elems]].mean(axis=1))
        res = []
        for q in np.atleast_2d(p):
            order = tree.query(q, k=min(8, len(elems)))[1]
            best = None
            for k in order:
                _, wts = self.element_point([elems[k]], q[None])
                if wts.min() >= -1e-6:
                    best = elems[k]
                    break
            res.append(elems[order[0]] if best is None else best)
        return np.array(res)

    def add_impact(self, name, snode, mnode=None, mw=None, mpos=None, nrm=(0.0, 0.0, 1.0), clr=0.0,
                   mu=0.0, ktf=1.0, alpha=None, zeta=None, gmax=60.0):
        """Add mass-conserving node-to-master-patch (or node-to-node / fixed floor) impact contact.
        Uses the two-body reduced mass m_eff = (1/m_s + sum(w_I^2 / m_I))^-1 so impact never
        destabilizes the explicit time step regardless of falling-to-receiving mass ratio."""
        snode = np.atleast_1d(np.asarray(snode, np.int32))
        ni = len(snode)
        if mnode is not None:
            mn = np.asarray(mnode, np.int32)
            if mn.ndim == 1:
                mn_pad = np.full((ni, 4), -1, np.int32)
                mn_pad[:, 0] = mn
                mw_pad = np.zeros((ni, 4), float)
                mw_pad[:, 0] = 1.0
            else:
                mn_pad = np.full((ni, 4), -1, np.int32)
                mn_pad[:, :mn.shape[1]] = mn
                if mw is None:
                    cnt = (mn_pad >= 0).sum(axis=1, keepdims=True)
                    mw_pad = np.where(mn_pad >= 0, 1.0 / np.maximum(cnt, 1), 0.0)
                else:
                    mw_pad = np.zeros((ni, 4), float)
                    mw_arr = np.asarray(mw, float)
                    mw_pad[:, :mw_arr.shape[1]] = mw_arr
            mpos_arr = np.zeros((ni, 3), float)
        else:
            mn_pad = np.full((ni, 4), -1, np.int32)
            mw_pad = np.zeros((ni, 4), float)
            mpos_arr = np.broadcast_to(np.asarray(mpos, float), (ni, 3)).copy()

        inv_m = 1.0 / self.mass[snode]
        has_m = mn_pad[:, 0] >= 0
        if has_m.any():
            for I in range(4):
                valid = has_m & (mn_pad[:, I] >= 0)
                if valid.any():
                    inv_m[valid] += (mw_pad[valid, I] ** 2) / self.mass[mn_pad[valid, I]]
        m_eff = 1.0 / inv_m
        kn, cn = self.penalty(m_eff, alpha, zeta)
        nrm_arr = np.broadcast_to(np.asarray(nrm, float), (ni, 3)).copy()
        nrm_arr /= np.linalg.norm(nrm_arr, axis=1, keepdims=True)
        clr_arr = np.broadcast_to(np.asarray(clr, float), (ni,)).copy()
        ic = ImpactContact(
            name, np.ascontiguousarray(snode), np.ascontiguousarray(mn_pad),
            np.ascontiguousarray(mw_pad), np.ascontiguousarray(mpos_arr),
            np.ascontiguousarray(nrm_arr), np.ascontiguousarray(clr_arr),
            np.ascontiguousarray(kn), np.ascontiguousarray(m_eff), float(ktf), float(mu), np.ascontiguousarray(cn),
            float(gmax), np.zeros((ni, 3))
        )
        self.impacts.append(ic)
        self._prepared = False
        return ic

    def add_joint_set(self, js: JointSet, adjust_dt=True):
        """Attach a JointSet after finalize() and enforce full nodal Gershgorin Courant stability across all beams + joints."""
        self.joint_sets.append(js)
        if adjust_dt and hasattr(self, "mass"):
            K_tr = np.zeros(self.nn)
            K_rot = np.zeros(self.nn)
            if self.nb > 0:
                sec_A = np.array([s.A for s in self.beam_sections])[self.bsec]
                sec_Imax = np.array([max(s.Ix, s.Iy) for s in self.beam_sections])[self.bsec]
                sec_J = np.array([s.J for s in self.beam_sections])[self.bsec]
                bE = np.array([m.E.max() for m in self.materials])[self.bmat]
                bG = bE / (2.0 * (1.0 + np.array([m.nu for m in self.materials])[self.bmat]))
                L0 = self.bL0
                kb_tr = np.maximum(bE * sec_A / L0, 12.0 * bE * sec_Imax / (L0 ** 3))
                kb_rot = np.maximum(6.0 * bE * sec_Imax / L0, 2.0 * bG * sec_J / L0)
                for I in range(2):
                    np.add.at(K_tr, self.bconn[:, I], 2.0 * kb_tr)
                    np.add.at(K_rot, self.bconn[:, I], kb_rot)
            for jset in self.joint_sets:
                has_b = jset.nb >= 0
                is_tie = jset.kind == 4
                k_max = np.where(is_tie, jset.kt, np.maximum(np.maximum(jset.kt, jset.kc), jset.kv))
                np.add.at(K_tr, jset.na, 2.0 * k_max)
                if has_b.any():
                    np.add.at(K_tr, jset.nb[has_b], 2.0 * k_max[has_b])
                kr_eff = np.where(is_tie, 0.0, jset.kr)
                np.add.at(K_rot, jset.na, 2.0 * kr_eff)
                if has_b.any():
                    np.add.at(K_rot, jset.nb[has_b], 2.0 * kr_eff[has_b])
            if self.dt_min is not None:
                m_req = 0.25 * K_tr * (self.dt_min ** 2)
                I_req = 0.25 * K_rot * (self.dt_min ** 2)
                np.maximum(self.mass, m_req, out=self.mass)
                np.maximum(self.rinert, I_req, out=self.rinert)
                self.added_mass = float(self.mass.sum() - self.mass_phys.sum())
            w2_max = max(float((K_tr / self.mass).max()), float((K_rot / self.rinert).max()))
            if w2_max > 0.0:
                self.dt = min(self.dt, getattr(self, "dt_safety", 0.9) * 2.0 / float(np.sqrt(w2_max)))
        self._prepared = False
        return js

    # ---------------------------------------------------------------- running
    def set_load_pattern(self, f):
        """Load pattern (nn, 3) of nodal forces or (nn, 6) of forces+moments, scaled by lam(t)."""
        f = np.asarray(f, float)
        self.fpat.fill(0.0)
        if f.ndim == 2 and f.shape[1] == 6:
            self.fpat[:, :] = f
            f_tr, f_rot = f[:, :3].ravel(), f[:, 3:].ravel()
            nz_r = np.nonzero(f_rot)[0]
            self._pat_rot_idx = nz_r if len(nz_r) else None
            self._pat_rot_val = f_rot[nz_r] if len(nz_r) else None
        else:
            f3 = f.reshape(self.nn, 3)
            self.fpat[:, :3] = f3
            f_tr = f3.ravel()
            self._pat_rot_idx, self._pat_rot_val = None, None
        nz = np.nonzero(f_tr)[0]
        self._pat_idx = nz if len(nz) else None
        self._pat_val = f_tr[nz] if len(nz) else None

    def _prepare(self):
        max_tg = 0
        if self.ne:
            max_tg = max(max_tg, int(self.tg.max()))
        if self.nb:
            max_tg = max(max_tg, int(self.btg.max()))
        for js in self.joint_sets:
            if len(js.tgroup):
                max_tg = max(max_tg, int(js.tgroup.max()))
        self.Tnow = np.zeros(max_tg + 1)
        self.Tprev = np.zeros_like(self.Tnow)
        self._args_shell = (self.ne, ptr(self.conn), ptr(self.h), ptr(self.mat), ptr(self.tg), ptr(self.x),
                            ptr(self.v), ptr(self.w), 0.0, ptr(self.Tnow), ptr(self.Tprev), C.byref(self.matstruct),
                            self.nip, ptr(self.zeta), ptr(self.wz), self.qhg, self.kappa, ptr(self.sig),
                            ptr(self.epsp), ptr(self.qs), ptr(self.hgs), ptr(self.fe), ptr(self.energy))
        self._args_gather = (self.nn, ptr(self.g_ptr), ptr(self.g_idx), ptr(self.fe), ptr(self.fint))
        self._args_beam = (self.nb, ptr(self.bconn), ptr(self.bsec), ptr(self.bmat), ptr(self.btg),
                           ptr(self.bL0), ptr(self.be0), ptr(self.bfac), ptr(self.bfac_prev),
                           ptr(self.x), ptr(self.Rnode), ptr(self.Tnow), ptr(self.Tprev), C.byref(self.matstruct),
                           NFIB, ptr(self.s_nact), ptr(self.s_yf), ptr(self.s_zf), ptr(self.s_Af),
                           ptr(self.s_props), ptr(self.s_J), ptr(self.b_plastic), ptr(self.bel),
                           ptr(self.bq), ptr(self.bsig), ptr(self.bepsp), ptr(self.bm1),
                           ptr(self.fbe), ptr(self.bdiag), ptr(self.energy), ptr(self.removed_energy))
        self._args_bgather = (self.nn, ptr(self.bg_ptr), ptr(self.bg_idx), ptr(self.fbe), ptr(self.fint),
                              0 if self.ne > 0 else 1)
        self._args_int = [self.nn, ptr(self.x), ptr(self.Rnode), ptr(self.v), ptr(self.w), ptr(self.fint),
                          ptr(self.fpat), 0.0, ptr(self.mass), ptr(self.rinert), ptr(self.fixmask), ptr(self.vpres),
                          len(self.c_node), ptr(self.c_node), ptr(self.c_type), ptr(self.c_dir), 0.0, 0.0,
                          ptr(self.kinout)]
        self._args_planes = [(len(c.nodes), ptr(c.nodes), ptr(c.off), ptr(c.P), ptr(self.x), ptr(self.v), ptr(c.kn),
                              c.ktf, c.mu, ptr(c.cn), None, c.gmax, ptr(c.ft), ptr(self.fint), ptr(c.out))
                             for c in self.planes]
        self._args_surf = [(len(c.snode), ptr(c.snode), ptr(c.spos), ptr(c.soff), ptr(c.cur), ptr(self.conn),
                            ptr(c.nbr), ptr(self.h), c.mfac, ptr(c.dref), ptr(self.x), ptr(self.v), ptr(c.kn), c.ktf,
                            c.mu, ptr(c.cn), None, c.gmax, ptr(c.ft), ptr(self.fint), ptr(c.out))
                           for c in self.surfaces]
        self._args_impacts = [(len(c.snode), ptr(c.snode), ptr(c.mnode), ptr(c.mw), ptr(c.mpos), ptr(c.nrm),
                               ptr(c.clr), ptr(self.x), ptr(self.v), ptr(c.kn), ptr(c.meff), c.ktf, c.mu, ptr(c.cn),
                               None, c.gmax, ptr(c.ft), ptr(self.fint), ptr(c.out))
                              for c in self.impacts]
        self._prepared = True

    def step(self, lam):
        """One explicit cycle at time self.t with temperatures self.Tnow (previous: self.Tprev)."""
        L, dt = self.lib, self.dt
        if self.ne > 0:
            a = self._args_shell
            L.shell_forces(*a[:8], dt, *a[9:])
            L.gather(*self._args_gather)
        if self.nb > 0:
            L.beam_forces(*self._args_beam)
            L.gather_add(*self._args_bgather)
        if self.ne == 0 and self.nb == 0:
            self.fint.fill(0.0)
        for s in self.spring_sets:
            s.apply(self, self.Tnow)
        for j in self.joint_sets:
            j.apply(self, self.Tnow)
        for c, a in zip(self.planes, self._args_planes):
            c_ = list(a)
            c_[10] = dt
            L.contact_plane(*c_)
        for c, a in zip(self.surfaces, self._args_surf):
            c_ = list(a)
            c_[16] = dt
            L.contact_surface(*c_)
        for c, a in zip(self.impacts, self._args_impacts):
            c_ = list(a)
            c_[14] = dt
            L.contact_impact(*c_)
        ai = self._args_int
        ai[7], ai[16], ai[17] = lam, self.damping, dt
        L.integrate(*ai)
        self.w_ext = float(self.kinout[2])
        self.t += dt
        self.cycle += 1

    def energy_summary(self) -> dict:
        """Full mechanical + thermal energy ledger for preregistration Section 8 balance checks."""
        ke0 = 0.0 if self.ke0 is None else float(self.ke0)
        ke = float(self.kinout[0])
        damping = float(self.kinout[1])
        ie_elem = float(self.energy[0] + self.energy[1])  # elastic + plastic + hourglass
        plastic_elem = float(self.energy[2])
        e_th = float(self.energy[3])
        joint_int = sum(s.stored_energy() for s in self.spring_sets) + sum(j.internal_work() for j in self.joint_sets)
        # Note: removed_energy is already inside cumulative ie_elem (energy[0]), just as plastic_elem is.
        lost = sum(s.lost_energy for s in self.spring_sets) + sum(j.lost_energy for j in self.joint_sets)
        c_diss = (sum(float(c.out[3]) for c in self.planes)
                  + sum(float(c.out[3]) for c in self.surfaces)
                  + sum(float(c.out[3]) for c in self.impacts))
        c_el = sum(float(c.out[4]) for c in self.impacts)
        lhs = ke0 + float(self.w_ext) + e_th
        rhs = ke + ie_elem + joint_int + c_el + damping + c_diss + lost
        denom = max(abs(lhs), abs(rhs), 1e-12)
        return dict(
            ke0=ke0, w_ext=float(self.w_ext), e_thermal=e_th,
            ke=ke, ie_elem=ie_elem, plastic_elem=plastic_elem,
            removed_beam_elem=float(self.removed_energy[0]),
            joint_int=joint_int, contact_el=c_el,
            damping=damping, contact_diss=c_diss, lost_energy=lost,
            lhs=lhs, rhs=rhs, rel_error=abs(lhs - rhs) / denom,
        )

    def run(self, t_end, temps=None, lam=lambda t: 0.0, monitor=None, every=100, stop=None):
        """Advance to t_end. temps(t) -> array of group temperatures (defaults to 20 C everywhere);
        lam(t) scales the load pattern; monitor(model) is called every `every` cycles; stop(model) -> True ends."""
        if not getattr(self, "_prepared", False):
            self._prepare()
        if temps is None:
            t_const = np.full(len(self.Tnow), 20.0)
            temps = lambda _t: t_const
        if self.ke0 is None and self.cycle == 0:
            self.ke0 = float(0.5 * (self.mass * (self.v**2).sum(axis=1)).sum()
                             + 0.5 * (self.rinert * (self.w**2).sum(axis=1)).sum())
        t_init = np.asarray(temps(self.t), float)
        self.Tprev[:len(t_init)] = t_init
        while self.t < t_end - 0.5 * self.dt:
            t_cur = np.asarray(temps(self.t), float)
            self.Tnow[:len(t_cur)] = t_cur
            self.step(lam(self.t))
            self.Tprev[:] = self.Tnow
            if monitor is not None and self.cycle % every == 0:
                monitor(self)
                if stop is not None and stop(self):
                    return "stopped"
            if not np.isfinite(self.kinout[0]):
                return "diverged"
        return "complete"


XI = np.array([-1.0, 1.0, 1.0, -1.0])
ETA = np.array([-1.0, -1.0, 1.0, 1.0])


def _frame(X):
    e3 = np.cross(X[2] - X[0], X[3] - X[1])
    e3 /= np.linalg.norm(e3)
    r21 = X[1] - X[0]
    e1 = r21 - (r21 @ e3) * e3
    e1 /= np.linalg.norm(e1)
    return e1, np.cross(e3, e1), e3


class SpringSet:
    """Breakable bolt and stud springs (see kernel.c springs()).

    Each spring: end A = nodes na (4, -1 padded) with weights wa; end B = nodes nb with
    weights wb, or fixed at pB (nb[0] = -1); axis nfix (unit, from B toward A), or the
    current normal of element eax. ks, ka: shear and axial stiffness; clr: radial
    shear clearance. Capacities at temperature: vcap20 x factor(T), tcap20 x factor(T),
    with T = Tw @ T_groups (Tw rows sum to 1) and factor one of `factors` per spring.
    """

    def __init__(self, names, na, wa, nb, wb, pB, nfix, eax, ks, ka, clr, vcap20, tcap20, Tw, factor_id, factors,
                 x0):
        self.names = list(names)
        n = len(self.names)
        self.na = np.ascontiguousarray(na, np.int32).reshape(n, 4)
        self.wa = np.ascontiguousarray(wa, float).reshape(n, 4)
        self.nb = np.ascontiguousarray(nb, np.int32).reshape(n, 4)
        self.wb = np.ascontiguousarray(wb, float).reshape(n, 4)
        self.pB = np.ascontiguousarray(pB, float).reshape(n, 3)
        self.nfix = np.ascontiguousarray(nfix, float).reshape(n, 3)
        self.eax = np.ascontiguousarray(eax, np.int32).reshape(n)
        self.ks, self.ka, self.clr = (np.ascontiguousarray(a, float).reshape(n) for a in (ks, ka, clr))
        self.vcap20, self.tcap20 = (np.ascontiguousarray(a, float).reshape(n) for a in (vcap20, tcap20))
        self.Tw = np.asarray(Tw, float)
        self.factor_id = np.asarray(factor_id, int)
        self.factors = factors
        self.broken = np.zeros(n, np.uint8)
        self.fsv = np.zeros((n, 7))
        self.vcap = self.vcap20.copy()
        self.tcap = self.tcap20.copy()
        self.lost_energy = 0.0
        xa = np.einsum("ij,ijk->ik", self.wa, x0[np.maximum(self.na, 0)] * (self.na >= 0)[..., None])
        xb = np.where((self.nb[:, :1] >= 0), np.einsum("ij,ijk->ik", self.wb, x0[np.maximum(self.nb, 0)]
                                                         * (self.nb >= 0)[..., None]), self.pB)
        self.d0 = np.ascontiguousarray(xb - xa)
        self.break_time = np.full(n, np.nan)
        self.break_T = np.full(n, np.nan)

    def temperatures(self, Tg):
        return self.Tw @ Tg

    def apply(self, model, Tg):
        T = self.temperatures(Tg)
        fac = np.empty(len(T))
        for k, f in enumerate(self.factors):
            sel = self.factor_id == k
            if sel.any():
                fac[sel] = f(T[sel])
        np.multiply(self.vcap20, fac, out=self.vcap)
        np.multiply(self.tcap20, fac, out=self.tcap)
        before = self.broken.copy() if self._watch else None
        model.lib.springs(len(self.names), ptr(self.na), ptr(self.wa), ptr(self.nb), ptr(self.wb), ptr(self.pB),
                          ptr(self.d0), ptr(self.nfix), ptr(self.eax), ptr(model.conn), ptr(self.ks), ptr(self.ka),
                          ptr(self.clr), ptr(self.vcap), ptr(self.tcap), ptr(self.broken), ptr(model.x),
                          ptr(model.fint), ptr(self.fsv))
        if before is not None:
            new = np.nonzero(self.broken != before)[0]
            if len(new):
                self.break_time[new] = model.t
                self.break_T[new] = T[new]
                self.lost_energy += float(self.fsv[new, 3].sum())
                self.last_broken = [self.names[i] for i in new]

    def stored_energy(self):
        return float(self.fsv[self.broken == 0, 3].sum())

    _watch = True
