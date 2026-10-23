"""Phase 1 beam-element model of the WTC 7 northeast floor bay, in plan.

Girder W33x130 between columns 79 and 44, five floor beams framing into it from
the east, studs to the slab, seated girder connections at both columns, fin
connections at the girder and seated connections at the east exterior columns.
Boundary conditions and the temperature ramp follow NIST's partial-floor model
(NCSTAR 1-9 §8.8). Every value comes from wtc7.assumptions; Config holds the
baseline and one-at-a-time overrides (preregistration Section 6).

Coordinates: origin at column 79, x east, y north, inches.
"""
from __future__ import annotations

import math
import sys
from dataclasses import asdict, dataclass, replace

import numpy as np

from wtc7 import assumptions as asm
from wtc7 import fe2d
from wtc7 import materials as mat
from wtc7.geometry import LG, geometry_set
from wtc7.sections import shape

WALK_AX = asm.value("A22")
WALK_LATS = tuple(asm.get("A21").sweep)


@dataclass(frozen=True)
class Config:
    name: str = "baseline"
    girder_studs: int = 0                      # S1
    walk_lat: float = asm.value("A21")         # S2
    slot: float = -1.0                         # S3; -1 = from the geometry set (A25, or standard holes per 1091/9114)
    mu_seat: float = asm.value("A42")          # S4
    col79: str = "fixed"                       # S5
    slab: str = "fixed"                        # S6
    peak: float = 800.0                        # S7 values are read off one ramp (see run_phase1)
    history: str = "monotonic"                 # S8
    steel: str = "NIST"                        # S9
    fy_scale: float = 1.0                      # S10
    gap79: float = -1.0                        # S11; -1 = from the geometry set (A26, or 1.36 in. at the near corner)
    gap44_lat: float = -1.0                    # S12; -1 = from the geometry set (A28, or A96 per side)
    end79: float = 0.0                         # drawings set: shift of col 79 along the girder, + = away (S11 detailed)
    bolt_slip_fail: float = asm.value("A31")   # S13
    stud_slip_fail: float = asm.value("A32")   # S14
    mu_slab: float = asm.value("A43")          # S15
    bearing: str = "grid"                      # A48: bearing faces on the building grid; "square" = normal to girder
    skew: float = 0.0                          # girder skew (deg); 0 = from the geometry set (A05 or A90)
    geometry: str = "digitized"                # "drawings": A90 to A97 (sources/drawings/READING.md)
    side_plates: str = "auto"                  # Q12: "auto" = as drawn for drawings, none for digitized; "clear"; "drawn"
    refine: int = 1
    rate: float = 1.0                          # C per unit pseudo-time
    dt: float = 2.0
    damping: float = 2.0
    mass_scale: float = 100.0

    def label(self):
        return self.name


def girder_T(tb):
    return 20.0 + 0.828 * (tb - 20.0)


def beam_T(cfg, t):
    """Floor-beam temperature at pseudo-time t."""
    rise = cfg.rate * t
    span = cfg.peak - 20.0
    if cfg.history == "monotonic":
        return 20.0 + min(rise, span)
    # heat to peak, hold for 10 % of the ramp, then cool to 20 C at the same rate
    hold = 0.1 * span
    if rise <= span:
        return 20.0 + rise
    if rise <= span + hold:
        return cfg.peak
    return max(20.0, cfg.peak - (rise - span - hold))


def t_end(cfg):
    span = (cfg.peak - 20.0) / cfg.rate
    return span * (1.1 if cfg.history == "monotonic" else 2.1)


def stud_factor(T):
    """Stud strength retention: 1 up to 300 C, then the bolt curve scaled to be continuous (A14)."""
    return np.minimum(1.0, mat.bolt_strength_factor(T) / mat.bolt_strength_factor(300.0))


def build(cfg: Config):
    G = geometry_set(cfg)
    th = math.radians(G["skew"])
    eg = np.array([math.sin(th), math.cos(th)])        # along girder, col 79 -> col 44
    ng = np.array([math.cos(th), -math.sin(th)])       # girder web normal, pointing east
    LG = G["LG"]
    stations = G["stations"]                           # from col 79
    beam_sections = G["sections"]                      # sorted from col 79 northward
    spans = G["spans"]
    w = asm.value("A34") / 1000.0 / 144.0
    g = shape("W33X130")

    # gravity reactions (hand_calcs section 6), beams ordered from col 79
    spacing = np.diff(np.concatenate([[0.0], stations, [LG]])) * math.cos(th)
    trib = 0.5 * (spacing[:-1] + spacing[1:])
    R_beam = w * trib * np.array(spans) / 2
    R79 = sum(R * (1 - s / LG) for R, s in zip(R_beam, stations)) + g.weight / 12000 * LG / 2
    R44 = R_beam.sum() + g.weight / 12000 * LG - R79

    xy, fixed = [], set()

    def node(p, fix=()):
        xy.append(np.asarray(p, float))
        k = len(xy) - 1
        fixed.update(3 * k + d for d in fix)
        return k

    springs, groups = [], []
    # bearing faces (A48, or A93 and A96 for the drawings set)
    n79, n44, l44 = G["n79"], G["n44"], G["l44"]
    steel = mat.SteelModel(cfg.steel, "A572", cfg.fy_scale)
    k_bolt = asm.value("A11") / cfg.bolt_slip_fail
    hole = asm.value("A24")
    slip0 = asm.value("A33")
    bolt_f = mat.bolt_strength_factor

    # columns
    c79 = node([0, 0], (0, 1, 2) if cfg.col79 == "fixed" else (2,))
    if cfg.col79 != "fixed":
        springs.append(fe2d.Linear(c79, None, asm.value("A30"), "col79_spring"))
    c44 = node(LG * eg, (0, 1, 2))

    # girder
    gst = np.concatenate([[0.0], stations, [LG]])
    gnodes, gpos = [], []
    for a, b in zip(gst[:-1], gst[1:]):
        nsub = 2 * cfg.refine
        for s in np.linspace(a, b, nsub + 1)[:-1]:
            gpos.append(s)
    gpos.append(LG)
    for s in gpos:
        gnodes.append(node(s * eg))
    gconn = np.column_stack([gnodes[:-1], gnodes[1:]])
    fy_g, fa_g = g.plan_fibres(12)
    groups.append(fe2d.BeamGroup("girder", gconn, fy_g, fa_g, steel, "girder"))
    g79, g44 = gnodes[0], gnodes[-1]
    at_station = {round(s, 6): n for s, n in zip(gpos, gnodes)}

    Tconn_g = lambda T: 0.5 * (T["girder"] + T["col"])
    Tconn_b = lambda T: 0.5 * (T["beam"] + T["col"])
    Tfin = lambda T: 0.5 * (T["beam"] + T["girder"])
    Tstud = lambda T: 0.5 * (T["beam"] + 20.0)

    # girder seat at col 79 (STC)
    springs += [
        fe2d.BoltGroup(c79, g79, 2, 45.0, k_bolt, hole, Tconn_g, bolt_f, "g79_seat"),
        fe2d.BoltGroup(c79, g79, 2, 45.0, k_bolt, G["slot79"], Tconn_g, bolt_f, "g79_clip"),
        fe2d.Friction(c79, g79, cfg.mu_seat, R79, slip0, "g79_fric"),
        fe2d.FrictionalContact(c79, g79, n79, G["gap79"], cfg.mu_seat, name="g79_bear"),
    ]
    # column 79 side cover plates (Q12): flange corners of the girder end against the plates
    if G["side_plates"] == "drawn":
        R = G["recess"]
        for corner, sgn in (("west", -1.0), ("east", 1.0)):
            a0, e0 = R["corners"][corner]
            springs.append(fe2d.RecessStop(c79, g79, R["Np"], sgn * R["Ep"], a0, sgn * e0, R["mouth"], R["inner"],
                                           2.0, cfg.mu_seat, name=f"g79_side_{corner}"))
    # girder seat at col 44 (STP)
    springs += [
        fe2d.BoltGroup(c44, g44, 2, 45.0, k_bolt, hole, Tconn_g, bolt_f, "g44_seat"),
        fe2d.BoltGroup(c44, g44, 2, 45.0, k_bolt, G["slot44"], Tconn_g, bolt_f, "g44_top"),
        fe2d.Friction(c44, g44, cfg.mu_seat, R44, slip0, "g44_fric"),
        fe2d.FrictionalContact(c44, g44, n44, asm.value("A27"), cfg.mu_seat, name="g44_bear"),
        fe2d.FrictionalContact(c44, g44, l44, G["gap44_e"], cfg.mu_seat, name="g44_lat_e"),
        fe2d.FrictionalContact(c44, g44, -l44, G["gap44_w"], cfg.mu_seat, name="g44_lat_w"),
    ]
    # girder studs (S1): evenly spaced, to the slab
    if cfg.girder_studs:
        for k, s in enumerate((np.arange(cfg.girder_studs) + 0.5) * LG / cfg.girder_studs):
            n = gnodes[int(np.argmin(np.abs(np.array(gpos) - s)))]
            springs.append(fe2d.BoltGroup(n, None, 1, asm.value("A13"), asm.value("A13") / cfg.stud_slip_fail, 0.0,
                                          lambda T: 0.5 * (T["girder"] + 20.0), stud_factor, f"gstud{k}"))

    beams = []
    for b_idx, (s, secname) in enumerate(zip(stations, beam_sections)):
        sec = shape(secname)
        nst = G["studs"][b_idx]
        LB = spans[b_idx]
        p0 = s * eg
        xs = np.concatenate([[0.0], (np.arange(nst) + 0.5) * LB / nst, [LB]])
        bx = []
        for a, b in zip(xs[:-1], xs[1:]):
            bx += list(np.linspace(a, b, cfg.refine + 1)[:-1])
        bx.append(LB)
        bx = np.array(bx)
        imp = asm.value("A47") * LB * np.sin(math.pi * bx / LB)
        bn = [node(p0 + [x, yy]) for x, yy in zip(bx, imp)]
        fy_b, fa_b = sec.plan_fibres(12)
        groups.append(fe2d.BeamGroup(f"beam{b_idx}", np.column_stack([bn[:-1], bn[1:]]), fy_b, fa_b, steel, "beam"))
        gnode = at_station[round(s, 6)]
        # fin connection and bearing of the beam end on the girder web
        springs += [
            fe2d.BoltGroup(gnode, bn[0], 6, 45.0, k_bolt, hole, Tfin, bolt_f, f"fin{b_idx}"),
            fe2d.Contact(gnode, bn[0], -ng, asm.value("A27"), name=f"fin{b_idx}_bear"),
        ]
        # exterior seated connection
        ce = node(p0 + [LB, 0.0], (0, 1, 2))
        springs += [
            fe2d.BoltGroup(ce, bn[-1], 2, 45.0, k_bolt, hole, Tconn_b, bolt_f, f"ext{b_idx}_seat"),
            fe2d.BoltGroup(ce, bn[-1], 2, 45.0, k_bolt, G["slot44"], Tconn_b, bolt_f, f"ext{b_idx}_top"),
            fe2d.Friction(ce, bn[-1], cfg.mu_seat, R_beam[b_idx], slip0, f"ext{b_idx}_fric"),
            fe2d.Contact(ce, bn[-1], [1, 0], asm.value("A27"), name=f"ext{b_idx}_bear"),
            fe2d.Contact(ce, bn[-1], [0, 1], asm.value("A29"), name=f"ext{b_idx}_lat_n"),
            fe2d.Contact(ce, bn[-1], [0, -1], asm.value("A29"), name=f"ext{b_idx}_lat_s"),
        ]
        # studs and slab interface at the stud stations
        stud_x = xs[1:-1]
        line_load = w * trib[b_idx]
        dx_trib = LB / nst
        slab_nodes = []
        for k, x in enumerate(stud_x):
            bnode = bn[int(np.argmin(np.abs(bx - x)))]
            if cfg.slab == "fixed":
                anchor = None
            else:
                anchor = node(p0 + [x, 0.0], (1, 2))
                slab_nodes.append(anchor)
            springs.append(fe2d.BoltGroup(bnode, anchor, 1, asm.value("A13"),
                                          asm.value("A13") / cfg.stud_slip_fail, 0.0, Tstud, stud_factor,
                                          f"stud{b_idx}_{k}"))
            springs.append(fe2d.Friction(bnode, anchor, cfg.mu_slab, line_load * dx_trib, slip0, f"slabf{b_idx}_{k}"))
        if slab_nodes:
            # released slab: an axial strip per beam line anchored at the east spandrel only (S6)
            EA = asm.value("A52") * asm.value("A53")
            for a, b, xa, xb in zip(slab_nodes[:-1], slab_nodes[1:], stud_x[:-1], stud_x[1:]):
                springs.append(fe2d.Linear(a, b, EA / (xb - xa), f"slab{b_idx}"))
            springs.append(fe2d.Linear(slab_nodes[-1], None, EA / (LB - stud_x[-1]), f"slab{b_idx}_anchor"))
        beams.append(dict(nodes=bn, x=bx, L=LB, section=secname))
    LB = max(spans)

    model = fe2d.Model(xy=np.array(xy), fixed=fixed, damping=cfg.damping, mass_scale=cfg.mass_scale)
    for gr in groups:
        model.add_group(gr)
    model.springs = springs
    geo = dict(eg=eg, ng=ng, c79=c79, c44=c44, g79=g79, g44=g44, gnodes=gnodes, beams=beams, R79=R79, R44=R44,
               stations=stations, LG=LG, set=G)
    return model, geo


def simulate(cfg: Config, verbose=False):
    model, geo = build(cfg)
    eg, ng = geo["eg"], geo["ng"]
    by_name = {s.name: s for s in model.springs}
    rows, events, snaps = [], {}, []
    first = lambda key, Tb, Tg: events.setdefault(key, dict(T_beam=Tb, T_girder=Tg))

    def temps(t):
        tb = beam_T(cfg, t)
        return {"beam": tb, "girder": girder_T(tb), "col": 20.0}

    def rel(u, a, b):
        d = u[3 * b:3 * b + 2] - u[3 * a:3 * a + 2]
        return d @ ng, d @ eg

    def monitor(model, r):
        Tb, Tg = r.temps["beam"], r.temps["girder"]
        lat79, ax79 = rel(r.u, geo["c79"], geo["g79"])
        lat44, ax44 = rel(r.u, geo["c44"], geo["g44"])
        defl = []
        for b in geo["beams"]:
            xy = model.xy[b["nodes"]] + np.column_stack([r.u[3 * np.array(b["nodes"])], r.u[3 * np.array(b["nodes"]) + 1]])
            chord = xy[-1] - xy[0]
            nrm = np.array([-chord[1], chord[0]]) / np.linalg.norm(chord)
            defl.append(np.max(np.abs((xy - xy[0]) @ nrm)) - asm.value("A47") * b["L"])
        def deformed(nodes):
            nodes = np.asarray(nodes)
            return model.xy[nodes] + np.column_stack([r.u[3 * nodes], r.u[3 * nodes + 1]])

        gxy = deformed(geo["gnodes"])
        gch = gxy[-1] - gxy[0]
        gnrm = np.array([-gch[1], gch[0]]) / np.linalg.norm(gch)
        gdefl = (gxy - gxy[0]) @ gnrm                  # + = west of the chord
        if abs(gdefl).max() > geo["LG"] / 50:
            first("E5_girder_buckled", Tb, Tg)
        snap_due = int(Tb) // 100 > snaps[-1]["bin"] if snaps else True
        if snap_due or r.broke and any(n.startswith("g79") for n in r.broke):
            snaps.append(dict(bin=int(Tb) // 100, T_beam=Tb, girder=gxy.round(3).tolist(),
                              beams=[deformed(b["nodes"]).round(3).tolist() for b in geo["beams"]]))
        broken = {s.name for s in model.springs if s.broken}
        nstud = sum(1 for n in broken if n.startswith("stud"))
        if nstud:
            first("first_stud", Tb, Tg)
        if nstud and nstud == sum(1 for s in model.springs if s.name.startswith("stud")):
            first("all_studs", Tb, Tg)
        if {"g79_seat"} <= broken:
            first("g79_seat_bolts", Tb, Tg)
        if {"g79_seat", "g79_clip"} <= broken:
            first("E1_g79_all_bolts", Tb, Tg)
        if {"g44_seat", "g44_top"} <= broken:
            first("E3_g44_all_bolts", Tb, Tg)
        if any(n.startswith("fin") for n in broken):
            first("first_fin", Tb, Tg)
        if any(d > b["L"] / 50 for d, b in zip(defl, geo["beams"])):
            first("E4_beam_buckled", Tb, Tg)
        e1 = "E1_g79_all_bolts" in events
        for wl in WALK_LATS:                     # S2 thresholds evaluated on the same history
            if e1 and (abs(lat79) >= wl or ax79 >= WALK_AX):
                first(f"E2@{wl}", Tb, Tg)
        if f"E2@{cfg.walk_lat}" in events:
            first("E2_walkoff_79", Tb, Tg)
        beamN = [float(np.mean(model.axial[f"beam{k}"])) for k in range(len(geo["beams"]))]
        rows.append(dict(t=r.t, T_beam=Tb, T_girder=Tg, lat79=lat79, ax79=ax79, lat44=lat44, ax44=ax44,
                         girder_bow=float(gdefl[np.argmax(np.abs(gdefl))]), max_beam_defl=max(defl), n_studs_broken=nstud, ke=r.ke, ie=r.ie, se=r.se,
                         girderN=float(np.mean(model.axial["girder"])), beamN=beamN,
                         g79_bear=by_name["g79_bear"].force, broke=r.broke))
        if verbose and (r.broke or len(rows) < 2 or int(Tb) // 10 != int(rows[-2]["T_beam"]) // 10):
            print(f"t={r.t:8.2f} T_b={Tb:6.1f} lat79={lat79:+.3f} ax79={ax79:+.3f} Ng={rows[-1]['girderN']:8.1f} "
                  f"studs={nstud} broke={r.broke}", file=sys.stderr, flush=True)

    stop = lambda model, r: f"E2@{max(WALK_LATS)}" in events and "E2_walkoff_79" in events
    status, hist = fe2d.run(model, temps, t_end(cfg), cfg.dt, monitor=monitor, stop=stop, dt_min=cfg.dt / 4096,
                            line_search=3)
    return dict(config=asdict(cfg), status=status, events=events, rows=rows, snapshots=snaps, ndof=model.ndof,
                n_elements=int(sum(len(g.conn) for g in model.groups)))


def variant(**kw):
    name = kw.pop("name")
    return replace(Config(), name=name, **kw)
