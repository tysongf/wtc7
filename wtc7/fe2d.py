"""Plan-view (2D) nonlinear frame solver for the Phase 1 beam-element model.

Members: corotational Euler-Bernoulli beams (Crisfield 1991, Ch. 7) with fibre
sections, temperature-dependent elastoplastic steel and thermal strain.
Connections: zero-length springs (bolt groups with hole clearance and brittle
shear failure, Coulomb friction, compression-only contact with a gap, linear
springs). Solution: implicit Newmark time stepping in pseudo-time with
mass-proportional damping, so snap-through after buckling or connection failure
is followed rather than stopping the run; kinetic energy is tracked against
internal work to show the run is quasi-static.

Failure handling follows NIST's 16-story approach (NCSTAR 1-9 §11.2.9): after
each converged step every breakable spring is checked against its
temperature-dependent capacity; failed springs are removed and the step is
solved again until no new failures occur.

Units: in., kip, s, C. DOFs per node: ux, uy, rz.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

GP_XI = np.array([0.5 - math.sqrt(15) / 10, 0.5, 0.5 + math.sqrt(15) / 10])   # Gauss-Legendre on (0, 1)
GP_W = np.array([5 / 18, 8 / 18, 5 / 18])
RHO = 0.2836e-3 / 386.1          # steel mass density, kip s^2 / in^4
K_EPS = 1e-4                     # regularizing stiffness for open gaps, kip/in.


class ElasticSteel:
    """Linear-elastic material with constant E and alpha; used by the verification tests."""

    def __init__(self, E=29000.0, alpha=1.4e-5, fy=1e6):
        self._E, self.alpha, self._fy = E, alpha, fy

    def E(self, T):
        return self._E

    def eps_th(self, T):
        return self.alpha * (T - 20.0)

    def flow_table(self, T):
        return np.array([0.0, 1.0]), np.array([self._fy, self._fy])


def flow_table(steel, T, grid=np.concatenate([[0.0], np.geomspace(1e-5, 0.3, 120)])):
    """(eps_p grid, flow stress) at temperature T for a wtc7.materials.SteelModel."""
    if hasattr(steel, "flow_table"):
        return steel.flow_table(T)
    return grid, np.array([steel.flow(T, e)[0] for e in grid])


@dataclass
class BeamGroup:
    """Elements sharing a section, a material and a temperature."""
    name: str
    conn: np.ndarray            # (ne, 2) node indices
    fib_y: np.ndarray           # (nf,)
    fib_a: np.ndarray           # (nf,)
    steel: object
    temp_key: str
    L0: np.ndarray = None
    beta0: np.ndarray = None
    ep: np.ndarray = None       # committed plastic strain (ne, ngp, nf)
    eb: np.ndarray = None       # committed equivalent plastic strain
    ep_t: np.ndarray = None
    eb_t: np.ndarray = None


class Spring:
    """Base class. d = u_j - u_i (translations). Node j may be None (ground)."""
    breakable = False
    broken = False

    def __init__(self, i, j, name=""):
        self.i, self.j, self.name = i, j, name

    def dofs(self):
        out = [3 * self.i, 3 * self.i + 1]
        if self.j is not None:
            out += [3 * self.j, 3 * self.j + 1]
        return out

    def rel(self, u):
        di = u[3 * self.i:3 * self.i + 2]
        dj = u[3 * self.j:3 * self.j + 2] if self.j is not None else np.zeros(2)
        return dj - di

    def scatter(self, F, K):
        """Return (dofs, f_vec, k_mat). F is the internal (resisting) force on node j in the
        K u sign convention, so a spring stretched by d gives F = k d; node i gets -F."""
        if self.j is None:
            return self.dofs(), -F, K
        f = np.concatenate([-F, F])
        k = np.block([[K, -K], [-K, K]])
        return self.dofs(), f, k

    def commit(self):
        pass

    def revert(self):
        pass

    def energy(self):
        return 0.0


class Linear(Spring):
    def __init__(self, i, j, k, name=""):
        super().__init__(i, j, name)
        self.k = k

    def evaluate(self, u, temps):
        d = self.rel(u)
        self.e = 0.5 * self.k * (d @ d)
        return self.scatter(self.k * d, self.k * np.eye(2))

    def energy(self):
        return getattr(self, "e", 0.0)


class BoltGroup(Spring):
    """n bolts in shear sharing one radial hole clearance; brittle failure on the
    SRSS force (NIST break element USER103, K1 = 1)."""
    breakable = True

    def __init__(self, i, j, n, cap, k_bolt, gap, temp_fn, strength_fn, name=""):
        super().__init__(i, j, name)
        self.n, self.cap, self.k, self.gap = n, cap, n * k_bolt, gap
        self.temp_fn, self.strength_fn = temp_fn, strength_fn
        self.F = np.zeros(2)

    def evaluate(self, u, temps):
        if self.broken:
            self.F = np.zeros(2)
            return self.scatter(np.zeros(2), K_EPS * np.eye(2))
        d = self.rel(u)
        r = np.linalg.norm(d)
        if r <= self.gap:
            self.F = np.zeros(2)
            return self.scatter(np.zeros(2), K_EPS * np.eye(2))
        e = d / r
        self.F = self.k * (r - self.gap) * e
        K = self.k * ((1 - self.gap / r) * np.eye(2) + (self.gap / r) * np.outer(e, e))
        return self.scatter(self.F, K)

    def energy(self):
        return 0.5 * (self.F @ self.F) / self.k

    def capacity(self, temps):
        return self.n * self.cap * float(self.strength_fn(self.temp_fn(temps)))

    def check(self, temps):
        return np.linalg.norm(self.F) > self.capacity(temps)


class Friction(Spring):
    """Isotropic Coulomb friction with an elastic stick stiffness (radial return)."""

    def __init__(self, i, j, mu, N, slip0, name=""):
        super().__init__(i, j, name)
        self.limit = mu * N
        self.k = self.limit / slip0 if self.limit > 0 else 0.0
        self.s = np.zeros(2)
        self.s_t = np.zeros(2)
        self.F = np.zeros(2)

    def evaluate(self, u, temps):
        if self.limit <= 0:
            return self.scatter(np.zeros(2), K_EPS * np.eye(2))
        d = self.rel(u)
        Ftr = self.k * (d - self.s)
        m = np.linalg.norm(Ftr)
        if m <= self.limit:
            self.s_t = self.s.copy()
            self.F = Ftr
            return self.scatter(Ftr, self.k * np.eye(2))
        n = Ftr / m
        F = self.limit * n
        self.F = F
        self.s_t = d - F / self.k
        K = self.k * (self.limit / m) * (np.eye(2) - np.outer(n, n)) + K_EPS * np.eye(2)
        return self.scatter(F, K)

    def commit(self):
        self.s = self.s_t.copy()

    def energy(self):
        return 0.0 if self.k == 0 else 0.5 * (self.F @ self.F) / self.k


class Contact(Spring):
    """Compression-only contact: closes when d . n exceeds gap (node j moving along +n
    relative to i), then a stiff penalty pushes back."""

    def __init__(self, i, j, n, gap, k=5.0e4, name=""):
        super().__init__(i, j, name)
        self.n = np.asarray(n, float) / np.linalg.norm(n)
        self.gap, self.k = gap, k
        self.force = 0.0

    def evaluate(self, u, temps):
        c = self.rel(u) @ self.n - self.gap
        if c <= 0:
            self.force = 0.0
            return self.scatter(np.zeros(2), K_EPS * np.outer(self.n, self.n))
        self.force = self.k * c
        return self.scatter(self.force * self.n, self.k * np.outer(self.n, self.n))

    def energy(self):
        return 0.5 * self.force**2 / self.k


class FrictionalContact(Contact):
    """Contact on a flat face with Coulomb friction along the face.

    Normal behaviour as Contact. Along the face (t = n rotated +90 deg) the
    tangential force sticks with stiffness kt until it reaches mu times the
    normal force, then slides. While the gap is open the tangential anchor
    follows the node, so the face grips where it first touches."""

    def __init__(self, i, j, n, gap, mu, k=5.0e4, kt=2.0e4, name=""):
        super().__init__(i, j, n, gap, k, name)
        self.t = np.array([-self.n[1], self.n[0]])
        self.mu, self.kt = mu, kt
        self.s, self.s_t, self.ft = None, None, 0.0

    def evaluate(self, u, temps):
        d = self.rel(u)
        c = d @ self.n - self.gap
        dt = d @ self.t
        if c <= 0:
            self.force, self.ft, self.s_t = 0.0, 0.0, dt
            return self.scatter(np.zeros(2), K_EPS * np.eye(2))
        s = dt if self.s is None else self.s
        self.force = self.k * c
        ftr = self.kt * (dt - s)
        lim = self.mu * self.force
        nn, tt, tn = np.outer(self.n, self.n), np.outer(self.t, self.t), np.outer(self.t, self.n)
        if abs(ftr) <= lim:
            self.ft, self.s_t = ftr, s
            K = self.k * nn + self.kt * tt
        else:
            sg = np.sign(ftr)
            self.ft = sg * lim
            self.s_t = dt - self.ft / self.kt
            K = self.k * nn + sg * self.mu * self.k * tn + K_EPS * tt
        return self.scatter(self.force * self.n + self.ft * self.t, K)

    def commit(self):
        self.s = self.s_t

    def energy(self):
        return 0.5 * self.force**2 / self.k + 0.5 * self.ft**2 / self.kt


class RecessStop(Spring):
    """A point of member j (offset r from the node, rotation ignored) against a side plate of a
    recess in column i (screening model of the column 79 side cover plates, Q12).

    Column frame: a = unit axis out of the recess (toward the member), b = unit lateral axis
    pointing from the point toward the plate. The point starts at (a0, b0); the recess mouth
    is at a = a_mouth, the plate's inner face at b = b_plate and its outer face at
    b_plate + t_plate. Inside the recess (a < a_mouth) the point can bear on the plate's
    inner face (normal -b); entering the recess over the plate end, it bears on the end
    (normal +a). Coulomb friction along the face, as FrictionalContact. The branch is
    chosen from the committed state so it does not switch within a step's iterations."""

    def __init__(self, i, j, a, b, a0, b0, a_mouth, b_plate, t_plate, mu, k=5.0e4, kt=2.0e4, name=""):
        super().__init__(i, j, name)
        self.a, self.b = np.asarray(a, float), np.asarray(b, float)
        self.a0, self.b0, self.am, self.bp, self.tp = a0, b0, a_mouth, b_plate, t_plate
        self.mu, self.k, self.kt = mu, k, kt
        self.mode, self.mode_t = "free", "free"
        self.s, self.s_t, self.force, self.ft = None, None, 0.0, 0.0

    def _faces(self, pa, pb):
        side = pa < self.am and pb >= self.bp                        # point overlaps the plate in plan
        if self.mode == "side" or (side and self.mode == "free" and (pb - self.bp) < (self.am - pa)):
            return "side", -self.b, pb - self.bp
        if side and pb < self.bp + self.tp:
            return "end", self.a, self.am - pa
        return "free", None, 0.0

    def evaluate(self, u, temps):
        d = self.rel(u)
        pa, pb = self.a0 + d @ self.a, self.b0 + d @ self.b
        mode, n, pen = self._faces(pa, pb)
        if mode == "side" and pa >= self.am:                       # left the recess
            mode, n, pen = "free", None, 0.0
        self.mode_t = mode
        if mode == "free" or pen <= 0:
            self.mode_t, self.force, self.ft = "free", 0.0, 0.0
            self.s_t = None
            return self.scatter(np.zeros(2), K_EPS * np.eye(2))
        t = np.array([-n[1], n[0]])
        dt = d @ t
        s = dt if self.s is None else self.s
        self.force = self.k * pen
        ftr = self.kt * (dt - s)
        lim = self.mu * self.force
        nn, tt, tn = np.outer(n, n), np.outer(t, t), np.outer(t, n)
        # n is the outward face normal; the penetration grows along -n, so d(force)/dd = -k n
        if abs(ftr) <= lim:
            self.ft, self.s_t = ftr, s
            K = self.k * nn + self.kt * tt
        else:
            sg = np.sign(ftr)
            self.ft = sg * lim
            self.s_t = dt - self.ft / self.kt
            K = self.k * nn - sg * self.mu * self.k * tn + K_EPS * tt
        return self.scatter(-self.force * n + self.ft * t, K)

    def commit(self):
        self.mode = self.mode_t
        self.s = self.s_t

    def revert(self):
        self.mode_t = self.mode

    def energy(self):
        return 0.5 * self.force**2 / self.k + 0.5 * self.ft**2 / self.kt


@dataclass
class Model:
    xy: np.ndarray                                  # (nn, 2)
    groups: list = field(default_factory=list)
    springs: list = field(default_factory=list)
    fixed: set = field(default_factory=set)         # fixed dof indices
    damping: float = 2.0                            # mass-proportional, 1/s
    rot_mass_factor: float = 1.0 / 12.0
    mass_scale: float = 1.0                         # pseudo-time runs only; checked by KE / strain energy

    @property
    def ndof(self):
        return 3 * len(self.xy)

    def add_group(self, g: BeamGroup):
        dx = self.xy[g.conn[:, 1]] - self.xy[g.conn[:, 0]]
        g.L0 = np.hypot(dx[:, 0], dx[:, 1])
        g.beta0 = np.arctan2(dx[:, 1], dx[:, 0])
        shape = (len(g.conn), len(GP_XI), len(g.fib_y))
        g.ep, g.eb = np.zeros(shape), np.zeros(shape)
        g.ep_t, g.eb_t = g.ep.copy(), g.eb.copy()
        self.groups.append(g)

    def mass(self):
        m = np.zeros(self.ndof)
        for g in self.groups:
            me = RHO * g.fib_a.sum() * g.L0 / 2
            for k in (0, 1):
                n = g.conn[:, k]
                np.add.at(m, 3 * n, me)
                np.add.at(m, 3 * n + 1, me)
                np.add.at(m, 3 * n + 2, me * g.L0**2 * self.rot_mass_factor)
        m[m == 0] = 1e-9
        return m * self.mass_scale

    # ------------------------------------------------------------------ elements
    def _group_forces(self, g, u, temps):
        T = temps[g.temp_key]
        E = g.steel.E(T)
        eth = g.steel.eps_th(T)
        grid, sf = flow_table(g.steel, T)
        n1, n2 = g.conn[:, 0], g.conn[:, 1]
        U = np.stack([u[3 * n1], u[3 * n1 + 1], u[3 * n1 + 2], u[3 * n2], u[3 * n2 + 1], u[3 * n2 + 2]], axis=1)
        x1 = self.xy[n1] + U[:, 0:2]
        x2 = self.xy[n2] + U[:, 3:5]
        dx = x2 - x1
        Ln = np.hypot(dx[:, 0], dx[:, 1])
        c, s = dx[:, 0] / Ln, dx[:, 1] / Ln
        cb, sb = np.cos(g.beta0), np.sin(g.beta0)
        alpha = np.arctan2(cb * s - sb * c, cb * c + sb * s)       # rigid rotation since start
        ul = Ln - g.L0
        t1, t2 = U[:, 2] - alpha, U[:, 5] - alpha
        L0 = g.L0[:, None]
        xi = GP_XI[None, :]
        eps0 = (ul / g.L0)[:, None] * np.ones_like(xi)
        kap = ((6 * xi - 4) * t1[:, None] + (6 * xi - 2) * t2[:, None]) / L0
        eps = eps0[:, :, None] - g.fib_y[None, None, :] * kap[:, :, None] - eth
        # return mapping, isotropic hardening on the flow curve at T
        sig_tr = E * (eps - g.ep)
        sf_n = np.interp(g.eb, grid, sf)
        f = np.abs(sig_tr) - sf_n
        dl = np.zeros_like(sig_tr)
        H = np.zeros_like(sig_tr)
        plastic = f > 0
        if plastic.any():
            st, ebn = np.abs(sig_tr[plastic]), g.eb[plastic]
            x = np.zeros_like(st)
            slopes = np.diff(sf) / np.diff(grid)
            for _ in range(30):
                e = ebn + x
                k = np.clip(np.searchsorted(grid, e, side="right") - 1, 0, len(slopes) - 1)
                h = np.where(e < grid[-1], slopes[k], 0.0)
                r = st - E * x - np.interp(e, grid, sf)
                x = np.maximum(x + r / (E + h), 0.0)
                if np.max(np.abs(r)) < 1e-9 * max(E, 1.0):
                    break
            dl[plastic], H[plastic] = x, h
        sign = np.sign(sig_tr)
        sig = sig_tr - E * dl * sign
        Et = np.where(plastic, E * H / (E + H), E)
        g.ep_t = g.ep + dl * sign
        g.eb_t = g.eb + dl
        A, y = g.fib_a[None, None, :], g.fib_y[None, None, :]
        g.energy = float((0.5 * sig**2 / E * A * (GP_W[None, :, None] * L0[:, :, None])).sum())
        N = (sig * A).sum(-1)
        M = -(sig * A * y).sum(-1)
        kss, ksk, kkk = (Et * A).sum(-1), -(Et * A * y).sum(-1), (Et * A * y * y).sum(-1)
        # B rows: d eps0 = d ul / L0 ; d kap = b1 d t1 + b2 d t2
        b1, b2 = (6 * xi - 4) / L0, (6 * xi - 2) / L0
        w = GP_W[None, :] * L0
        q = np.stack([(w * N).sum(1) / g.L0, (w * M * b1).sum(1), (w * M * b2).sum(1)], axis=1)
        kl = np.zeros((len(Ln), 3, 3))
        kl[:, 0, 0] = (w * kss).sum(1) / g.L0**2
        kl[:, 0, 1] = kl[:, 1, 0] = (w * ksk * b1).sum(1) / g.L0
        kl[:, 0, 2] = kl[:, 2, 0] = (w * ksk * b2).sum(1) / g.L0
        kl[:, 1, 1] = (w * kkk * b1 * b1).sum(1)
        kl[:, 1, 2] = kl[:, 2, 1] = (w * kkk * b1 * b2).sum(1)
        kl[:, 2, 2] = (w * kkk * b2 * b2).sum(1)
        zero = np.zeros_like(c)
        r = np.stack([-c, -s, zero, c, s, zero], axis=1)
        z = np.stack([s, -c, zero, -s, c, zero], axis=1)
        Bg = np.zeros((len(Ln), 3, 6))
        Bg[:, 0] = r
        Bg[:, 1] = -z / Ln[:, None]
        Bg[:, 2] = -z / Ln[:, None]
        Bg[:, 1, 2] += 1.0
        Bg[:, 2, 5] += 1.0
        fe = np.einsum("eij,ei->ej", Bg, q)
        ke = np.einsum("eki,ekl,elj->eij", Bg, kl, Bg)
        ke += (q[:, 0] / Ln)[:, None, None] * np.einsum("ei,ej->eij", z, z)
        msum = ((q[:, 1] + q[:, 2]) / Ln**2)[:, None, None]
        ke += msum * (np.einsum("ei,ej->eij", r, z) + np.einsum("ei,ej->eij", z, r))
        dofs = np.stack([3 * n1, 3 * n1 + 1, 3 * n1 + 2, 3 * n2, 3 * n2 + 1, 3 * n2 + 2], axis=1)
        return dofs, fe, ke, q[:, 0]

    def internal(self, u, temps):
        """Internal force vector and tangent (sparse CSC) at displacement u."""
        f = np.zeros(self.ndof)
        rows, cols, vals = [], [], []
        self.axial = {}
        for g in self.groups:
            dofs, fe, ke, N = self._group_forces(g, u, temps)
            np.add.at(f, dofs, fe)
            rows.append(np.repeat(dofs, 6, axis=1).ravel())
            cols.append(np.tile(dofs, (1, 6)).ravel())
            vals.append(ke.ravel())
            self.axial[g.name] = N

        for spr in self.springs:
            d, fs, ks = spr.evaluate(u, temps)
            if not hasattr(spr, "_rc"):
                d = np.asarray(d)
                spr._d, spr._rc = d, (np.repeat(d, len(d)), np.tile(d, len(d)))
            f[spr._d] += fs
            rows.append(spr._rc[0])
            cols.append(spr._rc[1])
            vals.append(ks.ravel())
        K = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                          shape=(self.ndof, self.ndof)).tocsc()
        return f, K

    def strain_energy(self):
        """Elastic energy stored in fibres and springs at the last evaluation."""
        return sum(g.energy for g in self.groups) + sum(s.energy() for s in self.springs)

    def commit(self):
        for g in self.groups:
            g.ep, g.eb = g.ep_t.copy(), g.eb_t.copy()
        for s in self.springs:
            s.commit()


@dataclass
class StepResult:
    t: float
    temps: dict
    u: np.ndarray
    ke: float
    ie: float
    se: float
    broke: list


def run(model: Model, temps_fn, t_end, dt, monitor=None, stop=None, dt_min=None, max_iter=25,
        tol=1e-6, beta=0.3025, gamma=0.6, line_search=0):
    """Integrate from t = 0 to t_end. temps_fn(t) -> dict of group/connection temperatures.

    monitor(model, step_result) is called after every committed step; stop(...) returning
    True ends the run. Returns (status, history) where status is 'complete', 'stopped' or
    'incomplete' (step size fell below dt_min)."""
    n = model.ndof
    free = np.array(sorted(set(range(n)) - model.fixed))
    M = model.mass()
    C = model.damping * M
    u, v, a = np.zeros(n), np.zeros(n), np.zeros(n)
    f_old, _ = model.internal(u, temps_fn(0.0))
    model.commit()
    ie, t = 0.0, 0.0
    dt_min = dt_min or dt / 256
    h = dt
    history = []
    while t < t_end - 1e-9:
        h = min(h, t_end - t)
        tn = t + h
        temps = temps_fn(tn)
        broke_this_step = []
        while True:
            un = u + h * v + h * h * (0.5 - beta) * a      # predictor (a_{n+1} = 0)
            ok = False
            for it in range(max_iter):
                an = (un - u - h * v) / (beta * h * h) - (0.5 / beta - 1) * a
                vn = v + h * ((1 - gamma) * a + gamma * an)
                f, K = model.internal(un, temps)
                R = f + M * an + C * vn
                Rf = R[free]
                J = K + sp.diags(M / (beta * h * h) + C * gamma / (beta * h))
                Jf = J[free][:, free]
                du = spla.spsolve(Jf, -Rf)
                if np.linalg.norm(du) < tol * (1 + np.linalg.norm(un)) and np.linalg.norm(Rf) < 1e-3 + 1e-6 * np.linalg.norm(f):
                    un[free] += du
                    ok = True
                    break
                # backtracking line search on the residual norm (contact and stick-slip switches)
                r0, step = np.linalg.norm(Rf), 1.0
                for _ in range(line_search):
                    trial = un.copy()
                    trial[free] += step * du
                    at = (trial - u - h * v) / (beta * h * h) - (0.5 / beta - 1) * a
                    vt = v + h * ((1 - gamma) * a + gamma * at)
                    ft, _ = model.internal(trial, temps)
                    if np.linalg.norm((ft + M * at + C * vt)[free]) < r0:
                        break
                    step *= 0.5
                un[free] += step * du
            if not ok:
                break
            an = (un - u - h * v) / (beta * h * h) - (0.5 / beta - 1) * a
            vn = v + h * ((1 - gamma) * a + gamma * an)
            f, K = model.internal(un, temps)
            newly = [s for s in model.springs if s.breakable and not s.broken and s.check(temps)]
            if not newly:
                break
            for s in newly:
                s.broken = True
            broke_this_step += [s.name for s in newly]
        if not ok:
            for s in model.springs:
                if s.name in broke_this_step:
                    s.broken = False
            h /= 2
            if h < dt_min:
                return "incomplete", history
            continue
        ie += 0.5 * (f_old + f) @ (un - u)
        f_old = f
        u, v, a, t = un, vn, an, tn
        model.commit()
        res = StepResult(t, temps, u.copy(), 0.5 * v @ (M * v), ie, model.strain_energy(), broke_this_step)
        history.append(res)
        if monitor:
            monitor(model, res)
        if stop and stop(model, res):
            return "stopped", history
        h = min(dt, h * 2)
    return "complete", history
