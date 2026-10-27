"""Phase 1 detailed (shell) model of the WTC 7 northeast floor framing, after NCSTAR 1-9 §8.8.

W33x130 girder A2001 from column 79 to column 44 and the five floor beams framing into it
from the east, all as Belytschko-Lin-Tsay shells (wtc7.xfe); the slab as one layer of
shells on top, in contact with the steel; studs, seat bolts, clip-angle and top-plate bolts
and fin-plate bolts as breakable springs; seats, column faces, the column 79 side cover
plates and the column 44 flanges as rigid planes with friction; slab edge conditions,
gravity ramp and uniform temperature ramp as in §8.8.

Geometry is the 'drawings' set (wtc7.geometry, assumptions A90 to A98, read from the
Frankel and Cantor sheets in sources/drawings/). Config fields mirror
phase1/plan_model.Config so the preregistered sweeps S1 to S15 mean the same thing.

Coordinates: origin on the girder web line at the column 79 end of the girder, at the top
of steel (underside of the slab); x east, y north, z up; inches.
"""
from __future__ import annotations

import math
import sys
from dataclasses import asdict, dataclass

import numpy as np

from wtc7 import assumptions as asm
from wtc7 import materials as mat
from wtc7 import xfe
from wtc7.geometry import geometry_set
from wtc7.sections import shape
from wtc7.xfe import mesh

WALK_AX = asm.value("A22")
WALK_LATS = tuple(asm.get("A21").sweep)
NIST_RATE = (600.0 - 20.0) / 1.5          # C/s, Fig. 8-25: 20 C at 1.1 s to 600 C at 2.6 s
EZ = np.array([0.0, 0.0, 1.0])


@dataclass(frozen=True)
class Config:
    name: str = "baseline"
    girder_studs: int = 0                      # S1
    walk_lat: float = asm.value("A21")         # S2 (thresholds evaluated on the same history)
    slot: float = -1.0                         # S3; -1 = standard holes at the col 79 clip angle (A95)
    mu_seat: float = asm.value("A42")          # S4, also the bearing faces and side plates (A49)
    col79: str = "fixed"                       # S5
    slab: str = "fixed"                        # S6
    peak: float = 600.0                        # S7
    history: str = "monotonic"                 # S8
    steel: str = "NIST"                        # S9
    fy_scale: float = 1.0                      # S10
    gap79: float = -1.0                        # (plan model only)
    end79: float = 0.0                         # S11 (detailed): shift of col 79 along the girder, + = away
    gap44_lat: float = -1.0                    # S12; -1 = from the drawings (A96)
    bolt_slip_fail: float = asm.value("A31")   # S13
    stud_slip_fail: float = asm.value("A32")   # S14
    mu_slab: float = asm.value("A43")          # S15
    bearing: str = "grid"                      # "grid" = faces as drawn (A93, A96); "square" = diagnostic
    side_plates: str = "auto"                  # Q12: "auto"/"drawn" = as drawn (A94); "clear" = removed
    stiffeners: str = "omitted"                # A97: "omitted" (as NIST) or "drawn"
    geometry: str = "drawings"
    skew: float = 0.0
    mesh: float = asm.value("A70")             # steel element size, in.
    slab_mesh: float = asm.value("A71")
    rate: float = 1.0                          # multiple of NIST's heating rate
    damping: float = asm.value("A84")          # mass-proportional, 1/s
    qhg: float = asm.value("A83")
    t_hold: float = asm.value("A85")           # hold after the ramp (NIST: 2.6 s to 4.0 s)
    threads: int = 4
    t_end: float = 0.0                         # 0 = from the schedule

    def label(self):
        return self.name


def girder_T(tb):
    return 20.0 + 0.828 * (tb - 20.0)


def schedule(cfg):
    """(beam temperature as a function of time, end time). Heating starts at 1.1 s (Fig. 8-25)."""
    t0, r = 1.1, NIST_RATE * cfg.rate
    tr = (cfg.peak - 20.0) / r
    if cfg.history == "monotonic":
        def Tb(t):
            return 20.0 + r * min(max(t - t0, 0.0), tr)
        t_end = t0 + tr + cfg.t_hold
    else:  # heat, hold 10 % of the ramp time, cool to 20 C at the same rate (as in the screening model)
        def Tb(t):
            u = max(t - t0, 0.0)
            if u <= tr:
                return 20.0 + r * u
            if u <= 1.1 * tr:
                return cfg.peak
            return max(20.0, cfg.peak - r * (u - 1.1 * tr))
        t_end = t0 + 2.1 * tr + cfg.t_hold
    return Tb, (cfg.t_end or t_end)


def gravity(t):
    """Smooth ramp over 1 s (Fig. 8-24)."""
    u = min(max(t, 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


def stud_factor(T):
    return np.minimum(1.0, mat.bolt_strength_factor(T) / mat.bolt_strength_factor(300.0))


class Floor:
    """Builds the model and keeps the bookkeeping needed for monitoring."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        G = geometry_set(cfg)
        self.G0 = G
        th = math.radians(G["skew"])
        self.th = th
        self.eg = np.array([math.sin(th), math.cos(th), 0.0])     # along the girder, col 79 -> col 44
        self.ng = np.array([math.cos(th), -math.sin(th), 0.0])    # girder lateral, east
        self.west = -self.ng
        self.LG = G["LG"]
        m = xfe.Model(qhg=cfg.qhg, contact_alpha=asm.value("A82")[0], contact_zeta=asm.value("A82")[1])
        m.lib.set_threads(cfg.threads)
        self.m = m
        m.add_material(xfe.steel_material("A572", cfg.steel, "A572", cfg.fy_scale))
        m.add_material(xfe.steel_material("A36", cfg.steel, "A36", cfg.fy_scale))
        slab = asm.value("A72")
        m.add_material(xfe.tension_compression_material("concrete", slab["E"], slab["nu"], slab["rho"],
                                                        slab["tension"], slab["compression"]))
        self.slab_h = slab["h"]
        size = cfg.mesh
        g = shape("W33X130")
        self.gsec = g
        self.stations = np.asarray(G["stations"])
        self.beam_secs = G["sections"]
        st = asm.value("A97")

        # ---------------------------------------------------------------- girder
        nfg = max(4, 2 * int(round(g.bf / size / 2)))
        req = list(self.stations) + ([st["from_end"]] if cfg.stiffeners == "drawn" else [])
        s_g = mesh.stations(self.LG, size, required=req)
        self.G = mesh.wshape(m, g, [0, 0, 0], self.eg, EZ, s_g, nfg, size, "A572", 2, "girder", top_z=-g.tf / 2)
        if cfg.stiffeners == "drawn":
            self._stiffeners(st)

        # ---------------------------------------------------------------- beams and fin plates
        fin = asm.value("A77")
        self.B = []
        for b, (s_b, secname) in enumerate(zip(self.stations, self.beam_secs)):
            sec = shape(secname)
            xg, yb = s_b * self.eg[0], s_b * self.eg[1]
            c0 = (g.tw / 2) / math.cos(th) + asm.value("A27")          # setback at the web line
            Lb = G["spans"][b] - 1.0                                      # piece length (A92)
            cope = g.bf / 2 + asm.value("A78") - c0                      # top-flange cope length from the end
            nfb = max(4, 2 * int(round(sec.bf / size / 2)))
            s_b_st = mesh.stations(Lb, size, required=[cope])
            imp = asm.value("A47") * Lb
            mem = mesh.wshape(m, sec, [xg + c0, yb, 0.0], [1, 0, 0], EZ, s_b_st, nfb, size, "A572", 1, f"beam{b}",
                              top_z=-sec.tf / 2, sweep=lambda x, L=Lb, a=imp: a * math.sin(math.pi * x / L),
                              cope_top=cope)
            # end cut parallel to the girder web (beam sheets 3004, 3005: 3 9/16 in 12), tapered out over
            # the first stations reaching 1.5 x the flange-tip offset, so no element at the cut folds over
            # (one station at the 1.8 and 3.6 in. meshes, two at 0.9 in.)
            taper = s_b_st[np.searchsorted(s_b_st, 1.5 * sec.bf / 2 * math.tan(th))]
            for key in ("web", "bot", "top"):
                grid = mem["grids"][key]
                for i, sv in enumerate(s_b_st):
                    if sv >= taper:
                        break
                    w = 1.0 - sv / taper
                    for n in grid[i]:
                        p = self._node(n)
                        p[0] += (p[1] - yb) * math.tan(th) * w
            mem.update(dict(xg=xg, yb=yb, c0=c0, L=Lb, x_end=xg + c0 + Lb, sec=sec, cope=cope, imp=imp,
                            studs=G["studs"][b]))
            # fin plate in the beam web plane, welded to the girder web at station s_b
            zrows = self.G["zw"] - g.tf / 2                               # girder web node levels (z)
            zc = -(sec.tf / 2 + (sec.d - sec.tf) / 2)
            zb = zc + fin["pitch"] * (np.arange(fin["n"]) - (fin["n"] - 1) / 2)
            ztop, zbot = zb.max() + fin["edge"], zb.min() - fin["edge"]
            rows = np.nonzero((zrows <= ztop + 1e-6) & (zrows >= zbot - 1e-6))[0]
            rows = np.arange(max(rows.min() - 1, 0), min(rows.max() + 2, len(zrows)))
            i_st = int(np.argmin(np.abs(self.G["s"] - s_b)))
            weld = self.G["grids"]["web"][i_st, rows]
            xs = np.linspace(0.0, fin["width"], int(round(fin["width"] / min(size, 1.5))) + 1)[1:]
            P = np.array([[xg + xx, yb, zrows[r]] for xx in xs for r in rows])
            new = m.add_nodes(P).reshape(len(xs), len(rows))
            grid = np.vstack([weld[None, :], new]).astype(np.int32)
            fin_el = m.add_shells(mesh.grid_conn(grid), fin["t"], "A36", 2, f"fin{b}")
            mem.update(fin_grid=grid, fin_el=fin_el, bolt_z=zb, bolt_x=xg + fin["bolt_line"])
            self.B.append(mem)

        # ---------------------------------------------------------------- slab
        self._build_slab()
        m.finalize(dt_safety=asm.value("A86"), dt_min="auto")
        m.damping = cfg.damping
        self._loads()
        self._constraints_slab()
        self._columns()
        self._contacts()
        self._springs()

    # ------------------------------------------------------------------ helpers
    def _node(self, n):
        """Writable view of node n's coordinates before finalize()."""
        k = 0
        for blk in self.m._x:
            if n < k + len(blk):
                return blk[n - k]
            k += len(blk)
        raise IndexError(n)

    def gpos(self, s, l, which):
        """Point on the girder flange mid-surface (which = 'top'/'bot') at station s, lateral l (west +)."""
        g = self.gsec
        z = -g.tf / 2 if which == "top" else -(g.d - g.tf / 2)
        return s * self.eg + l * self.west + np.array([0, 0, z])

    def _stiffeners(self, st):
        """Girder end stiffeners at col 79 (A97, 9114): plates normal to the girder axis on both sides
        of the web, from the bottom flange up, welded to the web and the bottom flange. Their outer
        edge is put on the flange node nearest to the drawn 5 1/2 in. width."""
        m, G = self.m, self.G
        i = int(np.argmin(np.abs(G["s"] - st["from_end"])))
        web, bot = G["grids"]["web"], G["grids"]["bot"]
        zw, yf = G["zw"], G["yf"]
        rows = np.nonzero(zw - zw[0] <= st["height"] + 1e-6)[0]
        jc = bot.shape[1] // 2
        for side in (1, -1):
            cols = list(range(jc, bot.shape[1])) if side > 0 else list(range(jc, -1, -1))
            cols = [j for j in cols if abs(yf[j]) <= st["width"] + 0.5 * abs(yf[1] - yf[0]) + 1e-6]
            grid = np.zeros((len(cols), len(rows)), np.int64)
            for a, j in enumerate(cols):
                for c, r in enumerate(rows):
                    if a == 0:
                        grid[a, c] = web[i, r]
                    elif c == 0:
                        grid[a, c] = bot[i, j]
                    else:
                        p = G["base"][i] + zw[r] * G["up"] + yf[j] * G["lat"]
                        grid[a, c] = m.add_nodes(p[None])[0]
            m.add_shells(mesh.grid_conn(grid.astype(np.int32)), st["t"], "A572", 2, "stiffener")

    # ------------------------------------------------------------------ slab
    def _build_slab(self):
        cfg, m, g, th = self.cfg, self.m, self.gsec, self.th
        a73 = asm.value("A73")
        yK = self.B[0]["yb"]                                   # southmost beam (K3004)
        y_s = yK - asm.value("A98")["south_half_spacing"]
        span, end79 = asm.value("A91")["span"], asm.value("A91")["end79"]
        y_n = (span - end79) * self.eg[1]                      # col 44 line (north wall)
        self.y_n, self.y_s = y_n, y_s
        nrow = max(2, int(round((y_n - y_s) / cfg.slab_mesh)))
        ys = np.linspace(y_s, y_n, nrow + 1)
        w_off = (g.bf / 2 + a73["west_overhang"]) / math.cos(th)
        # east edge: line through the beam ends' exterior faces (east wall)
        ends = np.array([[B["x_end"] + asm.value("A99"), B["yb"]] for B in self.B])
        cE = np.polyfit(ends[:, 1], ends[:, 0], 1)
        self.east_line = cE
        xw = lambda y: y * math.tan(th) - w_off
        xe = lambda y: np.polyval(cE, y)
        ymid = 0.5 * (y_s + y_n)
        ncol = max(2, int(round((xe(ymid) - xw(ymid)) / cfg.slab_mesh)))
        us = np.linspace(0.0, 1.0, ncol + 1)
        P = np.array([[xw(y) + u * (xe(y) - xw(y)), y, self.slab_h / 2] for y in ys for u in us])
        idx = m.add_nodes(P).reshape(nrow + 1, ncol + 1)
        conn = np.array([[idx[j, i], idx[j, i + 1], idx[j + 1, i + 1], idx[j + 1, i]]
                         for j in range(nrow) for i in range(ncol)], np.int32)
        self.slab_el = m.add_shells(conn, self.slab_h, "concrete", 0, "slab")
        self.slab_idx = idx

    def _constraints_slab(self):
        cfg, m, idx = self.cfg, self.m, self.slab_idx
        north, east = idx[-1, :], idx[:, -1]
        south, westE = idx[0, :], idx[:, 0]
        fm = m.fixmask.reshape(-1, 6)
        fm[np.concatenate([north, east]), :3] = 1
        if cfg.slab == "fixed":
            fm[south, 1] = 1
            fm[westE, 0] = 1
            fm[westE, 1] = 1
        fm[south, 3] = 1                                             # no rotation about the south edge (x)
        cons_n = np.asarray(westE, np.int32)
        m.c_node = np.concatenate([m.c_node, cons_n]).astype(np.int32)
        m.c_type = np.concatenate([m.c_type, np.ones(len(cons_n), np.int32)]).astype(np.int32)
        m.c_dir = np.ascontiguousarray(np.vstack([m.c_dir.reshape(-1, 3), np.tile(self.eg, (len(cons_n), 1))]))

    def _loads(self):
        m = self.m
        p = asm.value("A34") / 144.0 / 1000.0                          # ksi
        f = np.zeros((m.nn, 3))
        el = self.slab_el
        for I in range(4):
            np.add.at(f[:, 2], m.conn[el, I], -0.25 * p * m.area[el])
        m.set_load_pattern(f)
        self.total_load = -f[:, 2].sum()

    # ------------------------------------------------------------------ columns
    def _columns(self):
        """Column 79 and column 44 frames (A93 to A96)."""
        cfg = self.cfg
        rho = math.radians(asm.value("A93")["rotation"])
        self.Np = np.array([math.sin(rho), math.cos(rho), 0.0])      # col 79 axis toward its north face
        self.Ep = np.array([math.cos(rho), -math.sin(rho), 0.0])     # col 79 transverse axis, east
        end79 = asm.value("A91")["end79"] + cfg.end79
        self.C79 = -end79 * self.eg                                  # col 79 centre
        span = asm.value("A91")["span"]
        self.C44 = (span - asm.value("A91")["end79"]) * self.eg     # col 44 centre (on the girder line)
        if cfg.bearing == "square":
            self.Np, self.Ep = self.eg.copy(), self.ng.copy()

    # ------------------------------------------------------------------ contact
    def _contacts(self):
        cfg, m, g = self.cfg, self.m, self.gsec
        G = self.G
        gs = G["s"]
        bot, top, web = G["grids"]["bot"], G["grids"]["top"], G["grids"]["web"]
        mu = cfg.mu_seat
        a95, a94 = asm.value("A95"), asm.value("A94")
        z_seat = -g.d
        Np, Ep, C79 = self.Np, self.Ep, self.C79
        face_s = (C79 + a94["half_depth"] * Np) @ self.eg          # flange face station on the girder line
        seat_far = face_s + a95["length"]
        self.seat_far = seat_far
        # girder on the seat pf at col 79 (aligned with the girder, 12 in. wide, centred on it)
        near79 = bot[gs <= seat_far + 6.0].ravel()
        self.seat79 = m.add_plane("seat79", near79, g.tf / 2, [0, 0, z_seat], EZ, self.eg,
                                  [face_s - 1.0, seat_far, -a95["width"] / 2, a95["width"] / 2], mu=mu)
        pts = []
        sp_e = asm.value("A74")["edge_spacing"]
        for l in (-a95["width"] / 2, a95["width"] / 2):
            for sv in np.arange(face_s, seat_far + 1e-9, sp_e):
                pts.append(sv * self.eg + l * self.west + [0, 0, z_seat])
        for l in np.arange(-a95["width"] / 2, a95["width"] / 2 + 1e-9, sp_e):
            pts.append(seat_far * self.eg + l * self.west + [0, 0, z_seat])
        bot_el = np.concatenate(m.parts["girder.bot"])
        cen_s = (m.x0[m.conn[bot_el]].mean(1) @ self.eg)
        self.seat79_edge = m.add_surface("seat79_edge", bot_el[cen_s < seat_far + 8.0], -EZ, mfac=0.5, mu=mu,
                                         points=np.array(pts))
        # north flange face of col 79 between the side plates, against the girder end section
        end = np.unique(np.concatenate([web[0], bot[0], top[0]]))
        d79 = (m.x0[end] - C79) @ Np
        self.end_gap79 = float(d79.min() - a94["half_depth"])
        self.face79 = m.add_plane("face79", end, 0.0, C79 + a94["half_depth"] * Np, Np, Ep,
                                  [-a94["plate_inner"], a94["plate_inner"], -2.0, g.d + 2.0], mu=mu)
        # side cover plates (Q12): inner faces and ends, against the girder nodes near its end
        self.side79 = []
        if cfg.side_plates in ("auto", "drawn"):
            near = gs <= 8.0
            fl = np.unique(np.concatenate([bot[near].ravel(), top[near].ravel(), web[near].ravel()]))
            t_pl = asm.value("A94")["plate_t"]
            for sgn, tag in ((-1.0, "w"), (1.0, "e")):
                inner = C79 + sgn * a94["plate_inner"] * Ep
                # gmax 0.5 in.: a node deep behind one face of the plate is handled by the other face
                self.side79.append(m.add_plane(f"side79_{tag}", fl, 0.0, inner, -sgn * Ep, Np,
                                               [a94["half_depth"], a94["plate_end"], -1e3, 1e3], mu=mu, gmax=0.5))
                lo, hi = sorted((sgn * a94["plate_inner"], sgn * (a94["plate_inner"] + t_pl)))
                self.side79.append(m.add_plane(f"side79_{tag}_end", fl, 0.0, C79 + a94["plate_end"] * Np, Np, Ep,
                                               [lo, hi, -1e3, 1e3], mu=mu, gmax=0.5))
        # col 44: seat between the flanges, web face, flange inner faces (on the grid, A96)
        c44 = asm.value("A96")
        sec44 = shape(c44["section"])
        y_web = self.C44[1] - sec44.tw / 2
        x_in = sec44.d / 2 - sec44.tf
        far = gs >= self.LG - 12.0
        self.seat44 = m.add_plane("seat44", bot[far].ravel(), g.tf / 2, [self.C44[0], y_web, z_seat], EZ,
                                  [1, 0, 0], [-x_in, x_in, -c44["seat_len"], 0.0], mu=mu)
        end44 = np.unique(np.concatenate([web[-1], bot[-1], top[-1]]))
        self.face44 = m.add_plane("face44", end44, 0.0, [0, y_web, 0], [0, -1.0, 0], [1, 0, 0],
                                  [-1e3, 1e3, -1e3, 1e3], mu=mu)
        reg = np.unique(np.concatenate([bot[far].ravel(), top[far].ravel()]))
        reg = reg[m.x0[reg, 1] > self.C44[1] - sec44.bf / 2]
        gw = c44["lat_west"] if cfg.gap44_lat < 0 else cfg.gap44_lat
        ge = c44["lat_east"] if cfg.gap44_lat < 0 else cfg.gap44_lat
        xw, xe = m.x0[reg, 0].min() - gw, m.x0[reg, 0].max() + ge
        ylo = self.C44[1] - sec44.bf / 2
        self.flange44 = [
            m.add_plane("flange44_w", reg, 0.0, [xw, ylo, 0], [1, 0, 0], [0, 1, 0], [0.0, sec44.bf / 2, -1e3, 1e3], mu=mu),
            m.add_plane("flange44_e", reg, 0.0, [xe, ylo, 0], [-1, 0, 0], [0, 1, 0], [0.0, sec44.bf / 2, -1e3, 1e3],
                        mu=mu)]
        self.c44_geom = dict(y_web=y_web, xw=xw, xe=xe, gap_w=gw, gap_e=ge)
        # beams: east-end seats, column faces and flanges; west ends bearing on the girder web
        ext = asm.value("A79")
        self.ext = []
        web_el = np.concatenate(m.parts["girder.web"])
        cen = m.x0[m.conn[web_el]].mean(1)
        for b, B in enumerate(self.B):
            sec = B["sec"]
            bb, bt, bw = B["grids"]["bot"], B["grids"]["top"], B["grids"]["web"]
            sb = B["s"]
            near = sb >= B["L"] - ext["slave_len"]
            xe_b = B["x_end"] + asm.value("A27")                         # column face
            seat = m.add_plane(f"ext{b}_seat", bb[near].ravel(), sec.tf / 2, [xe_b, B["yb"], -sec.d], EZ, [1, 0, 0],
                               [-ext["length"], 5.0, -ext["width"] / 2, ext["width"] / 2], mu=mu)
            endn = np.unique(np.concatenate([bw[-1], bb[-1], bt[-1]]))
            face = m.add_plane(f"ext{b}_face", endn, 0.0, [xe_b, B["yb"], 0], [-1, 0, 0], [0, 1, 0],
                               [-1e3, 1e3, -1e3, 1e3], mu=mu)
            tips = np.unique(np.concatenate([bb[near].ravel(), bt[near].ravel()]))
            lat = []
            for sgn in (1.0, -1.0):
                yl = B["yb"] + sgn * (sec.bf / 2 + asm.value("A29"))
                lat.append(m.add_plane(f"ext{b}_lat{'n' if sgn > 0 else 's'}", tips, 0.0, [xe_b, yl, 0],
                                       [0, -sgn, 0], [1, 0, 0], [-1e3, 1e3, -1e3, 1e3], mu=mu))
            endw = np.unique(np.concatenate([bw[0], bb[0]]))
            dist = np.abs((cen - B["xg"] * np.array([1, 0, 0]) - B["yb"] * np.array([0, 1, 0])) @ self.eg)
            patch = web_el[(dist < asm.value("A89")) & (cen[:, 2] > -sec.d - 2.0)]
            bear = m.add_surface(f"beam{b}_bear", patch, self.ng, mfac=0.5, mu=mu, nodes=endw, off=0.0)
            self.ext.append(dict(seat=seat, face=face, lat=lat, bear=bear))
        # slab on the steel: girder frictionless (A44), beams with friction (S15)
        top_g = np.unique(m.conn[np.concatenate(m.parts["girder.top"])].ravel())
        self.slab_girder = m.add_surface("slab_girder", self.slab_el, -EZ, mfac=0.5, mu=0.0, nodes=top_g,
                                         off=g.tf / 2, gmax=3.0)
        top_b, off_b = [], []
        for b, B in enumerate(self.B):
            nodes = np.unique(m.conn[np.concatenate(m.parts[f"beam{b}.top"])].ravel())
            top_b.append(nodes)
            off_b.append(np.full(len(nodes), B["sec"].tf / 2))
        self.slab_beams = m.add_surface("slab_beams", self.slab_el, -EZ, mfac=0.5, mu=cfg.mu_slab,
                                        nodes=np.concatenate(top_b), off=np.concatenate(off_b), gmax=3.0)

    # ------------------------------------------------------------------ springs
    def _springs(self):
        cfg, m, g = self.cfg, self.m, self.gsec
        bolt = asm.value("A80")
        ks = asm.value("A11") / cfg.bolt_slip_fail
        hole = asm.value("A24")
        a95 = asm.value("A95")
        end79 = asm.value("A91")["end79"]
        rows = []                       # (name, A elements, point, B, axis, ks, ka, clr, vcap, tcap, Tw, factor)
        Tw_conn_g = [0.5, 0.0, 0.5]     # (ambient, beam, girder): average of girder and column (A15)
        Tw_conn_b = [0.5, 0.5, 0.0]
        Tw_fin = [0.0, 0.5, 0.5]
        Tw_stud_b = [0.5, 0.5, 0.0]
        Tw_stud_g = [0.5, 0.0, 0.5]
        bot_el = np.concatenate(m.parts["girder.bot"])
        top_el = np.concatenate(m.parts["girder.top"])
        slot79 = hole if cfg.slot < 0 else cfg.slot
        slot44 = asm.value("A96")["slot"]
        gage = a95["gage"]
        pos44 = asm.value("A87")["edge"]
        for end, s_seat, s_top, clr_top, top_name in (
                ("g79", a95["seat_bolts"] - end79, a95["clip_bolts"] - end79, slot79, "clip"),
                ("g44", self.LG - pos44, self.LG - pos44, slot44, "top")):
            for which, els, kind, s_b, clr, nz, ka in (("seat", bot_el, "bot", s_seat, hole, 1.0, bolt["ka"]),
                                                       (top_name, top_el, "top", s_top, clr_top, -1.0, bolt["ka_top"])):
                for k, l in enumerate((-gage / 2, gage / 2)):
                    rows.append((f"{end}_{which}{k}", els, self.gpos(s_b, l, kind), None, [0, 0, nz], ks, ka,
                                 clr, asm.value("A11"), bolt["tcap"], Tw_conn_g, 0))
        web_parts = {b: np.concatenate(m.parts[f"beam{b}.web"]) for b in range(len(self.B))}
        for b, B in enumerate(self.B):
            for k, zb in enumerate(B["bolt_z"]):
                p = np.array([B["bolt_x"], B["yb"], zb])
                rows.append((f"fin{b}_{k}", web_parts[b], p, B["fin_el"], [0, 1, 0], ks, bolt["ka"], hole,
                             asm.value("A11"), 1e9, Tw_fin, 0))
            ext = asm.value("A79")
            bb_el = np.concatenate(m.parts[f"beam{b}.bot"])
            bt_el = np.concatenate(m.parts[f"beam{b}.top"])
            sec = B["sec"]
            xb = B["x_end"] - ext["bolt_edge"]
            for which, els, z, clr, nz, ka in (("seat", bb_el, -(sec.d - sec.tf / 2), hole, 1.0, bolt["ka"]),
                                               ("top", bt_el, -sec.tf / 2, slot44, -1.0, bolt["ka_top"])):
                for k, dy in enumerate((-ext["gage"] / 2, ext["gage"] / 2)):
                    p = np.array([xb, B["yb"] + dy, z])
                    rows.append((f"ext{b}_{which}{k}", els, p, None, [0, 0, nz], ks, ka, clr,
                                 asm.value("A11"), bolt["tcap"], Tw_conn_b, 0))
        stud = asm.value("A81")
        kst = asm.value("A13") / cfg.stud_slip_fail
        for b, B in enumerate(self.B):
            n = B["studs"]
            bt_el = np.concatenate(m.parts[f"beam{b}.top"])
            for k in range(n):
                xl = (k + 0.5) * B["L"] / n
                if xl < B["cope"]:
                    continue
                p = np.array([B["xg"] + B["c0"] + xl, B["yb"] + B["imp"] * math.sin(math.pi * xl / B["L"]),
                              -B["sec"].tf / 2])
                rows.append((f"stud{b}_{k}", bt_el, p, "slab", [0, 0, -1], kst, stud["ka"], 0.0, asm.value("A13"),
                             1e9, Tw_stud_b, 1))
        for k in range(cfg.girder_studs):
            sv = (k + 0.5) * self.LG / cfg.girder_studs
            rows.append((f"gstud{k}", top_el, self.gpos(sv, 0.0, "top"), "slab", [0, 0, -1], kst, stud["ka"], 0.0,
                         asm.value("A13"), 1e9, Tw_stud_g, 1))
        names, na, wa, nb, wb, pB, nfix, eax = [], [], [], [], [], [], [], []
        ksv, kav, clrv, vcap, tcap, Tw, fid = [], [], [], [], [], [], []
        for (name, elsA, p, B, nvec, k_s, k_a, clr, vc, tc, tw, f) in rows:
            eA = m.find_element(elsA, p[None])[0]
            nA, wA = m.element_point([eA], p[None])
            if B is None:
                nB, wB, pb = [-1, -1, -1, -1], [0, 0, 0, 0], p
            elif isinstance(B, str):           # slab point straight above
                q = np.array([p[0], p[1], self.slab_h / 2])
                eB = m.find_element(self.slab_el, q[None])[0]
                nBa, wBa = m.element_point([eB], q[None])
                nB, wB, pb = nBa[0], wBa[0], q
            else:                              # fin plate point at the same location
                eB = m.find_element(B, p[None])[0]
                nBa, wBa = m.element_point([eB], p[None])
                nB, wB, pb = nBa[0], wBa[0], p
            names.append(name)
            na.append(nA[0]); wa.append(wA[0]); nb.append(nB); wb.append(wB); pB.append(pb)
            nfix.append(nvec); eax.append(-1)
            ksv.append(k_s); kav.append(k_a); clrv.append(clr); vcap.append(vc); tcap.append(tc); Tw.append(tw)
            fid.append(f)
        self.springs = xfe.SpringSet(names, na, wa, nb, wb, pB, nfix, eax, ksv, kav, clrv, vcap, tcap, Tw, fid,
                                     [mat.bolt_strength_factor, stud_factor], m.x0)
        m.spring_sets.append(self.springs)
        self.sp_index = {n: i for i, n in enumerate(names)}


def build(cfg: Config) -> Floor:
    return Floor(cfg)


class Monitor:
    """Records histories and events (preregistration Section 1; E2r and E2 physical for the shell model)."""

    def __init__(self, fl: Floor, Tb_fn, verbose=False):
        self.fl, self.Tb_fn, self.verbose = fl, Tb_fn, verbose
        m, G = fl.m, fl.G
        web = G["grids"]["web"]
        self.g_end = dict(bot=web[0, 0], top=web[0, -1], mid=web[0, len(G["zw"]) // 2])
        self.g_end44 = dict(bot=web[-1, 0], top=web[-1, -1])
        self.g_mid = web[:, len(G["zw"]) // 2]
        self.rows, self.events, self.snaps = [], {}, []
        self.last_bin = -1
        self.sp = fl.springs
        names = self.sp.names
        self.grp = {k: np.array([i for i, n in enumerate(names) if n.startswith(k)]) for k in
                    ("g79_seat", "g79_clip", "g44_seat", "g44_top", "fin", "ext", "stud", "gstud")}
        self.beam_mid = []
        for B in fl.B:
            w = B["grids"]["web"]
            self.beam_mid.append(w[:, w.shape[1] // 2])
        # beam axial force section at quarter span: elements of each beam crossing it
        self.beam_sec = []
        for b, B in enumerate(fl.B):
            els = np.concatenate([np.concatenate(m.parts[f"beam{b}.{k}"]) for k in ("web", "bot", "top")])
            xc = m.x0[m.conn[els]].mean(1)[:, 0] - B["xg"] - B["c0"]
            ds = B["s"][1] - B["s"][0]
            pick = els[np.abs(xc - 0.25 * B["L"]) < 0.5 * ds + 1e-9]
            pick = pick[:len(pick)]
            self.beam_sec.append(pick)
        self.e2_lat = None

    def first(self, key, Tb, Tg, t):
        if key not in self.events:
            self.events[key] = dict(T_beam=Tb, T_girder=Tg, t=t)
            if self.verbose:
                print(f"  EVENT {key} at t={t:.3f} s, T_beam={Tb:.1f}", file=sys.stderr, flush=True)

    def axial(self, els):
        m = self.fl.m
        N = (m.sig[els, :, 0] * (0.5 * m.h[els, None] * m.wz[None, :])).sum(1)    # per unit width
        X = m.x[m.conn[els]]
        width = np.linalg.norm(X[:, 2] - X[:, 1], axis=1)
        return float((N * width).sum())

    def __call__(self, m):
        fl, cfg = self.fl, self.fl.cfg
        t = m.t
        Tb = self.Tb_fn(t)
        Tg = girder_T(Tb)
        u = m.x - m.x0
        west, eg = fl.west, fl.eg
        col = getattr(fl, "col79_disp", np.zeros(3))
        ub = u[self.g_end["bot"]] - col
        ut = u[self.g_end["top"]] - col
        lat79 = float(ub @ west)                     # + = west (toward walk-off)
        ax79 = float(ub @ eg)                        # + = away from col 79
        dz79 = float(ub[2])
        xb, xt = m.x[self.g_end["bot"]], m.x[self.g_end["top"]]
        dv = xt - xb
        twist = float(np.degrees(np.arctan2(dv @ west, dv[2])))   # + = top toward west
        u44 = u[self.g_end44["bot"]]
        lat44, ax44 = float(u44 @ west), float(u44 @ eg)
        gm = m.x[self.g_mid]
        ch = gm[-1] - gm[0]
        nrm = np.cross([0, 0, 1.0], ch)
        nrm /= np.linalg.norm(nrm)
        bow = (gm - gm[0]) @ nrm
        gbow = float(bow[np.argmax(np.abs(bow))])
        defl = []
        for B, mid in zip(fl.B, self.beam_mid):
            P = m.x[mid]
            P0 = m.x0[mid]
            c = P[-1] - P[0]
            nb = np.array([-c[1], c[0], 0.0])
            nb /= np.linalg.norm(nb)
            d = (P - P[0]) @ nb - (P0 - P0[0]) @ np.array([0, 1.0, 0])
            defl.append(float(np.max(np.abs(d))))
        sp = self.sp
        br = sp.broken.astype(bool)
        nstud = int(br[self.grp["stud"]].sum()) if len(self.grp["stud"]) else 0
        if nstud:
            self.first("first_stud", Tb, Tg, t)
        if len(self.grp["stud"]) and nstud == len(self.grp["stud"]):
            self.first("all_studs", Tb, Tg, t)
        if br[self.grp["g79_seat"]].all():
            self.first("g79_seat_bolts", Tb, Tg, t)
        if br[self.grp["g79_seat"]].all() and br[self.grp["g79_clip"]].all():
            self.first("E1_g79_all_bolts", Tb, Tg, t)
        if br[self.grp["g44_seat"]].all() and br[self.grp["g44_top"]].all():
            self.first("E3_g44_all_bolts", Tb, Tg, t)
        if br[self.grp["fin"]].any():
            self.first("first_fin_bolt", Tb, Tg, t)
        if any(d > B["L"] / 50 for d, B in zip(defl, fl.B)):
            self.first("E4_beam_buckled", Tb, Tg, t)
        if abs(gbow) > fl.LG / 50:
            self.first("E5_girder_buckled", Tb, Tg, t)
        e1 = "E1_g79_all_bolts" in self.events
        for wl in WALK_LATS:
            if e1 and (lat79 >= wl or ax79 >= WALK_AX):
                self.first(f"E2@{wl}", Tb, Tg, t)
        if f"E2@{cfg.walk_lat}" in self.events:
            self.first("E2_walkoff_79", Tb, Tg, t)
        if abs(twist) >= np.degrees(np.arctan(fl.gsec.bf / fl.gsec.d)):
            self.first("E2r_rocking_79", Tb, Tg, t)
        if dz79 <= -2.0:
            self.first("E2_support_lost_79", Tb, Tg, t)
        beamN = [self.axial(e) for e in self.beam_sec]
        side = {p.name: float(np.linalg.norm(p.out[:3])) for p in fl.side79}
        if side.get("side79_w", 0.0) > 1.0:
            self.first("Q12_west_plate_bearing", Tb, Tg, t)
        if side.get("side79_w_end", 0.0) > 1.0:
            self.first("Q12_west_plate_end_bearing", Tb, Tg, t)
        f79 = fl.face79.out[:3].copy()
        f44 = fl.face44.out[:3].copy()
        fric = sum(c.out[3] for c in m.planes) + sum(c.out[3] for c in m.surfaces)
        row = dict(t=t, T_beam=Tb, T_girder=Tg, lat79=lat79, ax79=ax79, dz79=dz79, twist79=twist, lat44=lat44,
                   ax44=ax44, girder_bow=gbow, max_beam_defl=max(defl), beam_defl=defl, beamN=beamN,
                   face79=f79.tolist(), face44=f44.tolist(), side79=side,
                   seat79_z=float(-fl.seat79.out[2] - fl.seat79_edge.out[2]),
                   n_studs_broken=nstud, n_fin_broken=int(br[self.grp["fin"]].sum()),
                   ke=float(m.kinout[0]), ie=float(m.energy[0]), hg=float(m.energy[1]), plastic=float(m.energy[2]),
                   thermal_in=float(m.energy[3]), friction=float(fric), damping=float(m.kinout[1]), w_ext=float(m.w_ext),
                   spring_stored=sp.stored_energy(), spring_lost=float(sp.lost_energy))
        self.rows.append(row)
        b = int(Tb) // 50
        if b != self.last_bin or (getattr(sp, "last_broken", None) and any(n.startswith("g79") for n in sp.last_broken)):
            self.last_bin = b
            self.snaps.append(dict(t=t, T_beam=Tb, x=m.x.astype(np.float32)))
            sp.last_broken = None
        if self.verbose and (len(self.rows) % 40 == 1):
            print(f"t={t:.3f} Tb={Tb:6.1f} lat79={lat79:+.3f} ax79={ax79:+.3f} dz79={dz79:+.3f} tw={twist:+.2f} "
                  f"bow={gbow:+.2f} bdefl={max(defl):.2f} studs={nstud} F79={np.linalg.norm(f79):.0f} "
                  f"KE/IE={row['ke'] / max(row['ie'], 1e-9):.3f}", file=sys.stderr, flush=True)

    def stop(self, m):
        ev = self.events.get("E2_support_lost_79")
        return ev is not None and m.t > ev["t"] + 0.3


def simulate(cfg: Config, verbose=False, every_s=0.0025):
    fl = build(cfg)
    m = fl.m
    Tb_fn, t_end = schedule(cfg)
    temps = lambda t: np.array([20.0, Tb_fn(t), girder_T(Tb_fn(t))])
    mon = Monitor(fl, Tb_fn, verbose)
    every = max(1, int(round(every_s / m.dt)))
    if cfg.col79 != "fixed":
        status = run_flexible(fl, temps, t_end, mon, every)
    else:
        status = m.run(t_end, temps, lam=gravity, monitor=mon, every=every, stop=mon.stop)
    sp = fl.springs
    breaks = {n: dict(t=float(sp.break_time[i]), T=float(sp.break_T[i])) for i, n in enumerate(sp.names)
              if sp.broken[i]}
    info = dict(n_nodes=int(m.nn), n_shells=int(m.ne), dt=float(m.dt), cycles=int(m.cycle),
                added_mass=float(m.added_mass), total_load=float(fl.total_load), n_springs=len(sp.names))
    return dict(config=asdict(cfg), status=status, events=mon.events, rows=mon.rows, breaks=breaks, info=info), mon


def run_flexible(fl, temps, t_end, mon, every):
    """S5: column 79 as a rigid body on a lateral spring (A30). Its seat, face, side plates and the
    fixed ends of its bolts move with it; it is driven by their reactions."""
    m, cfg = fl.m, fl.cfg
    k = asm.value("A30")
    mass = asm.value("A30m")
    planes = [fl.seat79, fl.face79, *fl.side79]
    p0 = {id(p): p.P[:3].copy() for p in planes}
    sp = fl.springs
    sel = np.array([i for i, n in enumerate(sp.names) if n.startswith("g79")])
    pB0 = sp.pB[sel].copy()
    edge_pts0 = fl.seat79_edge.spos.copy()
    u = np.zeros(3)
    v = np.zeros(3)
    fl.col79_disp = u
    if not getattr(m, "_prepared", False):
        m._prepare()
    m.Tprev[:] = temps(m.t)
    while m.t < t_end - 0.5 * m.dt:
        m.Tnow[:] = temps(m.t)
        m.step(gravity(m.t))
        m.Tprev[:] = m.Tnow
        # reactions on the column: contact forces on its planes and the bolt forces at their fixed ends
        F = sum(p.out[:3] for p in planes) + fl.seat79_edge.out[:3]
        F = F - sp.fsv[sel, 4:7].sum(0)
        F[2] = 0.0                                   # lateral (plan) movement only
        v += m.dt * (F - k * u) / mass
        u += m.dt * v
        for p in planes:
            p.P[:3] = p0[id(p)] + u
        sp.pB[sel] = pB0 + u
        fl.seat79_edge.spos[:] = edge_pts0 + u
        fl.col79_disp = u
        if m.cycle % every == 0:
            mon(m)
            if mon.stop(m):
                return "stopped"
        if not np.isfinite(m.kinout[0]):
            return "diverged"
    return "complete"
