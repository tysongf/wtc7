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
    lib.integrate.argtypes = [C.c_int, _dp, _dp, _dp, _dp, _dp, C.c_double, _dp, _dp, _up, _dp,
                              C.c_int, _ip, _ip, _dp, C.c_double, C.c_double, _dp]
    lib.contact_plane.argtypes = [C.c_int, _ip, _dp, _dp, _dp, _dp, _dp, C.c_double, C.c_double,
                                  _dp, C.c_double, C.c_double, _dp, _dp, _dp]
    lib.contact_surface.argtypes = [C.c_int, _ip, _dp, _dp, _ip, _ip, _ip, _dp, C.c_double, _dp, _dp, _dp,
                                    _dp, C.c_double, C.c_double, _dp, C.c_double, C.c_double,
                                    _dp, _dp, _dp]
    lib.springs.argtypes = [C.c_int, _ip, _dp, _ip, _dp, _dp, _dp, _dp, _ip, _ip, _dp, _dp, _dp, _dp, _dp,
                            _up, _dp, _dp, _dp]
    lib.stress_update.argtypes = [C.c_void_p, C.c_int, C.c_double, C.c_double, _dp, _dp, C.c_double]
    lib.stress_update.restype = C.c_double
    lib.set_threads.argtypes = [C.c_int]
    lib.get_threads.restype = C.c_int
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
    """Explicit shell model. Build with add_* calls, then finalize() and run()."""

    def __init__(self, nip=5, qhg=0.05, kappa=5.0 / 6.0, contact_alpha=0.1, contact_zeta=0.1):
        self.nip, self.qhg, self.kappa = nip, qhg, kappa
        self.contact_alpha, self.contact_zeta = contact_alpha, contact_zeta
        self.no_dt_parts = ("fin",)         # small plates that are mass-scaled rather than setting the time step
        self._x, self._conn, self._h, self._mat, self._tg, self._part = [], [], [], [], [], []
        self.materials: list[Material] = []
        self.mat_index = {}
        self.parts = {}
        self.planes: list[PlaneContact] = []
        self.surfaces: list[SurfaceContact] = []
        self.spring_sets = []
        self._fixed = []
        self._presc = []
        self._cons = []
        self.added_mass = None
        self.lib = load_kernel()

    # ---------------------------------------------------------------- building
    def add_nodes(self, xyz):
        xyz = np.atleast_2d(np.asarray(xyz, float))
        start = sum(len(a) for a in self._x)
        self._x.append(xyz)
        return np.arange(start, start + len(xyz), dtype=np.int32)

    def add_material(self, m: Material):
        self.mat_index[m.name] = len(self.materials)
        self.materials.append(m)
        return self.mat_index[m.name]

    def add_shells(self, conn, h, mat, tgroup, part):
        conn = np.atleast_2d(np.asarray(conn, np.int32))
        start = sum(len(c) for c in self._conn)
        n = len(conn)
        self._conn.append(conn)
        self._h.append(np.broadcast_to(np.asarray(h, float), (n,)).copy())
        self._mat.append(np.full(n, self.mat_index[mat] if isinstance(mat, str) else mat, np.int32))
        self._tg.append(np.full(n, tgroup, np.int32))
        ids = np.arange(start, start + n, dtype=np.int32)
        self.parts.setdefault(part, []).append(ids)
        return ids

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

        rot_factor: nodal rotary inertia = mass x max(h^2/12, rot_factor x element area),
        so rotations do not govern the time step. dt_min: elements whose stable step is
        below it get added mass (reported in self.added_mass).
        """
        self.x0 = np.ascontiguousarray(np.concatenate(self._x))
        self.conn = np.ascontiguousarray(np.concatenate(self._conn))
        self.h = np.concatenate(self._h)
        self.mat = np.concatenate(self._mat)
        self.tg = np.concatenate(self._tg)
        nn, ne = len(self.x0), len(self.conn)
        self.nn, self.ne = nn, ne
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
            # the smallest per-part median: only irregular elements (skewed ends, small plates) get added mass
            dt_min = min(float(np.median(dte[np.concatenate(v)])) for k, v in self.parts.items()
                         if not k.startswith(self.no_dt_parts))
        self.dt_min = dt_min
        if dt_min is not None:
            small = dte < dt_min
            scale[small] = (dt_min / dte[small]) ** 2
            dte = np.maximum(dte, dt_min)
        self.elem_dt = dte
        self.mass = np.zeros(nn)
        self.mass_phys = np.zeros(nn)
        rin = np.zeros(nn)
        for I in range(4):
            np.add.at(self.mass, self.conn[:, I], 0.25 * me * scale)
            np.add.at(self.mass_phys, self.conn[:, I], 0.25 * me)
            np.add.at(rin, self.conn[:, I], 0.25 * me * scale * np.maximum(self.h**2 / 12, rot_factor * area))
        self.added_mass = float(self.mass.sum() - self.mass_phys.sum())
        orphan = self.mass == 0
        self.mass[orphan] = 1.0
        rin[orphan] = 1.0
        self.rinert = rin
        self.dt = dt_safety * float(dte.min())
        # gather table
        slots = np.argsort(self.conn.ravel(), kind="stable")
        counts = np.bincount(self.conn.ravel(), minlength=nn)
        self.g_ptr = np.concatenate([[0], np.cumsum(counts)]).astype(np.int32)
        self.g_idx = slots.astype(np.int32)
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
        self.v = np.zeros((nn, 3))
        self.w = np.zeros((nn, 3))
        self.sig = np.zeros((ne, self.nip, 3))
        self.epsp = np.zeros((ne, self.nip))
        self.qs = np.zeros((ne, 2))
        self.hgs = np.zeros((ne, 5))
        self.fe = np.zeros((ne, 24))
        self.fint = np.zeros((nn, 6))
        self.fpat = np.zeros((nn, 6))
        self._prepared = False
        self.energy = np.zeros(4)          # IE, hourglass, plastic, thermal input
        self.kinout = np.zeros(2)          # KE, damping work
        self.w_ext = 0.0
        self.t = 0.0
        self.cycle = 0
        self.damping = 0.0
        self._pat_idx = None
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

    # ---------------------------------------------------------------- running
    def set_load_pattern(self, f):
        """Load pattern (nn, 3) of nodal forces, scaled by lam(t) during the run."""
        f = np.asarray(f, float).reshape(self.nn, 3)
        self.fpat[:, :3] = f
        nz = np.nonzero(f.ravel())[0]
        self._pat_idx, self._pat_val = nz, f.ravel()[nz]

    def _prepare(self):
        self.Tnow = np.zeros(int(self.tg.max()) + 1 if self.ne else 1)
        self.Tprev = np.zeros_like(self.Tnow)
        self._args_shell = (self.ne, ptr(self.conn), ptr(self.h), ptr(self.mat), ptr(self.tg), ptr(self.x),
                            ptr(self.v), ptr(self.w), 0.0, ptr(self.Tnow), ptr(self.Tprev), C.byref(self.matstruct),
                            self.nip, ptr(self.zeta), ptr(self.wz), self.qhg, self.kappa, ptr(self.sig),
                            ptr(self.epsp), ptr(self.qs), ptr(self.hgs), ptr(self.fe), ptr(self.energy))
        self._args_gather = (self.nn, ptr(self.g_ptr), ptr(self.g_idx), ptr(self.fe), ptr(self.fint))
        self._args_int = [self.nn, ptr(self.x), ptr(self.v), ptr(self.w), ptr(self.fint), ptr(self.fpat), 0.0,
                          ptr(self.mass), ptr(self.rinert), ptr(self.fixmask), ptr(self.vpres), len(self.c_node),
                          ptr(self.c_node), ptr(self.c_type), ptr(self.c_dir), 0.0, 0.0, ptr(self.kinout)]
        self._args_planes = [(len(c.nodes), ptr(c.nodes), ptr(c.off), ptr(c.P), ptr(self.x), ptr(self.v), ptr(c.kn),
                              c.ktf, c.mu, ptr(c.cn), None, c.gmax, ptr(c.ft), ptr(self.fint), ptr(c.out))
                             for c in self.planes]
        self._args_surf = [(len(c.snode), ptr(c.snode), ptr(c.spos), ptr(c.soff), ptr(c.cur), ptr(self.conn),
                            ptr(c.nbr), ptr(self.h), c.mfac, ptr(c.dref), ptr(self.x), ptr(self.v), ptr(c.kn), c.ktf,
                            c.mu, ptr(c.cn), None, c.gmax, ptr(c.ft), ptr(self.fint), ptr(c.out))
                           for c in self.surfaces]
        self._prepared = True

    def step(self, lam):
        """One explicit cycle at time self.t with temperatures self.Tnow (previous: self.Tprev)."""
        L, dt = self.lib, self.dt
        a = self._args_shell
        L.shell_forces(*a[:8], dt, *a[9:])
        L.gather(*self._args_gather)
        for s in self.spring_sets:
            s.apply(self, self.Tnow)
        for c, a in zip(self.planes, self._args_planes):
            c_ = list(a)
            c_[10] = dt
            L.contact_plane(*c_)
        for c, a in zip(self.surfaces, self._args_surf):
            c_ = list(a)
            c_[16] = dt
            L.contact_surface(*c_)
        work = self._pat_idx is not None and lam != 0.0
        if work:
            v_old = self.v.ravel()[self._pat_idx]
        ai = self._args_int
        ai[6], ai[15], ai[16] = lam, self.damping, dt
        L.integrate(*ai)
        if work:
            self.w_ext += lam * float(self._pat_val @ (0.5 * (v_old + self.v.ravel()[self._pat_idx]))) * dt
        self.t += dt
        self.cycle += 1

    def run(self, t_end, temps, lam=lambda t: 0.0, monitor=None, every=100, stop=None):
        """Advance to t_end. temps(t) -> array of group temperatures; lam(t) scales the load pattern;
        monitor(model) is called every `every` cycles; stop(model) -> True ends the run."""
        if not getattr(self, "_prepared", False):
            self._prepare()
        self.Tprev[:] = temps(self.t)
        while self.t < t_end - 0.5 * self.dt:
            self.Tnow[:] = temps(self.t)
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
