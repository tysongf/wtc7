"""Geometry sets shared by the Phase 1 models (plan-view screening and shell).

'digitized': values read from NCSTAR 1-9 figures (assumptions A01 to A06, A20 to A28, A48),
used for the first screening runs. 'drawings': values read from the Frankel shop and erection
drawings and the Cantor structural drawings (A90 to A97; sources/drawings/READING.md).
Coordinates: origin at the girder's column 79 end on the web line, x east, y north, inches.
"""
from __future__ import annotations

import math

import numpy as np

from wtc7 import assumptions as asm
from wtc7.sections import shape

LG = 540.0          # girder length in the digitized set (A01)


def geometry_set(cfg):
    """Geometry inputs for the chosen set: 'digitized' (NCSTAR figures, A01 to A06, A20 to A28, A48)
    or 'drawings' (Frankel and Cantor sheets, A90 to A97). Coordinates: origin at the girder's
    col 79 end on the web line, x east, y north."""
    g = shape("W33X130")
    if cfg.geometry == "digitized":
        skew = cfg.skew or asm.value("A05")
        th = math.radians(skew)
        LG_ = LG
        stations = np.sort(LG_ - np.array(asm.value("A04")))
        sections = ["W24X55"] * 4 + ["W21X44"]
        studs = [asm.value("A06")[x.replace("X", "x")] for x in sections]
        spans = [asm.value("A03")] * 5
        out = dict(skew=skew, LG=LG_, stations=stations, sections=sections, studs=studs, spans=spans,
                   slot79=asm.value("A25") if cfg.slot < 0 else cfg.slot,
                   slot44=asm.value("A25") if cfg.slot < 0 else cfg.slot,
                   gap79=asm.value("A26") if cfg.gap79 < 0 else cfg.gap79,
                   gap44_w=asm.value("A28") if cfg.gap44_lat < 0 else cfg.gap44_lat,
                   gap44_e=asm.value("A28") if cfg.gap44_lat < 0 else cfg.gap44_lat,
                   side_plates="clear" if cfg.side_plates == "auto" else cfg.side_plates)
        if cfg.bearing == "grid":
            out.update(n79=np.array([0.0, -1.0]), n44=np.array([0.0, 1.0]), l44=np.array([1.0, 0.0]))
        else:
            eg = np.array([math.sin(th), math.cos(th)])
            out.update(n79=-eg, n44=eg, l44=np.array([math.cos(th), -math.sin(th)]))
        return out
    # drawings
    skew = cfg.skew or asm.value("A90")
    th = math.radians(skew)
    eg = np.array([math.sin(th), math.cos(th)])
    ng = np.array([math.cos(th), -math.sin(th)])
    span, end79 = asm.value("A91")["span"], asm.value("A91")["end79"] + getattr(cfg, "end79", 0.0)
    c44 = asm.value("A96")
    tw44 = shape(c44["section"]).tw
    end44 = span - (tw44 / 2 + c44["end_gap"] + g.bf / 2 * math.sin(th)) / math.cos(th)
    LG_ = end44 - asm.value("A91")["end79"]
    b = asm.value("A92")
    st = span - asm.value("A91")["end79"] - np.array(b["stations"])   # from the col 79 end of the girder
    order = np.argsort(st)
    rho = math.radians(asm.value("A93")["rotation"])
    Np = np.array([math.sin(rho), math.cos(rho)])          # col 79 axis toward its north face
    Ep = np.array([math.cos(rho), -math.sin(rho)])         # col 79 transverse axis, east
    c79 = asm.value("A94")
    centre = -end79 * eg                                    # col 79 centre relative to the girder end
    corner = {k: end79 * eg + sgn * g.bf / 2 * ng for k, sgn in (("east", 1.0), ("west", -1.0))}
    first = min(corner[k] @ Np for k in corner)
    gap79 = first - c79["half_depth"] if cfg.gap79 < 0 else cfg.gap79
    out = dict(skew=skew, LG=LG_, stations=st[order], sections=[b["sections"][i] for i in order],
               studs=[b["studs"][i] for i in order], spans=[b["lengths"][i] + 1.0 for i in order],
               slot79=asm.value("A24") if cfg.slot < 0 else cfg.slot, slot44=c44["slot"],
               gap79=gap79,
               gap44_w=c44["lat_west"] if cfg.gap44_lat < 0 else cfg.gap44_lat,
               gap44_e=c44["lat_east"] if cfg.gap44_lat < 0 else cfg.gap44_lat,
               side_plates="drawn" if cfg.side_plates == "auto" else cfg.side_plates,
               n79=-Np, n44=np.array([0.0, 1.0]), l44=np.array([1.0, 0.0]),
               recess=dict(Np=Np, Ep=Ep, corners={k: (v @ Np, v @ Ep) for k, v in corner.items()},
                           mouth=c79["plate_end"], inner=c79["plate_inner"]), centre=centre)
    if cfg.bearing == "square":
        out.update(n79=-eg, n44=eg, l44=ng)
    return out


