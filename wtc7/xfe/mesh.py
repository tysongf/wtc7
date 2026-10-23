"""Structured shell meshes for wtc7.xfe: flat plates and wide-flange members.

Element nodes are ordered so that side 0-1 runs along the first grid direction
(the member axis for members), which makes the element frame's x axis the member
axis and the stored stress component 0 the axial stress.
"""
from __future__ import annotations

import numpy as np


def grid_conn(idx):
    """Quads of a (n1+1, n2+1) node-index grid, side 0-1 along the first index."""
    a, b = idx.shape
    q = [[idx[i, j], idx[i + 1, j], idx[i + 1, j + 1], idx[i, j + 1]] for i in range(a - 1) for j in range(b - 1)]
    return np.array(q, np.int32)


def plate(model, origin, u, v, s1, s2, h, mat, tgroup, part):
    """Flat plate on origin + s1 * u + s2 * v for the station arrays s1, s2.

    Returns (node index grid, element ids)."""
    origin, u, v = (np.asarray(a, float) for a in (origin, u, v))
    P = origin + s1[:, None, None] * u + s2[None, :, None] * v
    idx = model.add_nodes(P.reshape(-1, 3)).reshape(len(s1), len(s2))
    el = model.add_shells(grid_conn(idx), h, mat, tgroup, part)
    return idx, el


def stations(length, size, required=()):
    """Stations from 0 to length with spacing close to `size`, including every required station."""
    pts = sorted({0.0, float(length), *[float(r) for r in required if 0.0 < r < length]})
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(round((b - a) / size)))
        out += list(np.linspace(a, b, n + 1)[1:])
    return np.array(out)


def wshape(model, sec, origin, axis, up, s, n_flange, size_web, mat, tgroup, part, top_z=None, lateral=None,
           sweep=None, cope_top=0.0):
    """Wide-flange member of section `sec` (wtc7.sections.WShape) with mid-surface model.

    origin: point on the web line at the top-flange mid-surface level if top_z is None,
    else top_z gives that level directly (origin[2] ignored). axis: unit member axis;
    up: unit vertical; stations s along the axis (s[0] = 0). Flange mid-surfaces are
    (d - tf) apart; the web spans between them. n_flange: elements across each flange
    (even, so a node lies on the web line). sweep(s) -> lateral offset (initial
    out-of-straightness). cope_top: length from s = 0 over which the top flange is
    removed (coped beam end).

    Returns a dict of node grids (web, top, bot: (ns, n) arrays) and element ids.
    """
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    up = np.asarray(up, float) / np.linalg.norm(up)
    lat = np.cross(up, axis) if lateral is None else np.asarray(lateral, float)
    lat /= np.linalg.norm(lat)
    o = np.asarray(origin, float).copy()
    if top_z is not None:
        o[2] = top_z
    hw = sec.d - sec.tf
    nw = max(2, int(round(hw / size_web)))
    zw = np.linspace(-hw, 0.0, nw + 1)                       # bottom flange to top flange mid-surface
    yf = np.linspace(-sec.bf / 2, sec.bf / 2, n_flange + 1)
    off = np.zeros(len(s)) if sweep is None else np.array([sweep(x) for x in s])
    base = o + s[:, None] * axis + off[:, None] * lat           # web line, top mid-surface level
    jc = n_flange // 2
    # web nodes
    W = base[:, None, :] + zw[None, :, None] * up
    web = model.add_nodes(W.reshape(-1, 3)).reshape(len(s), nw + 1)
    grids = {"web": web}
    els = {}
    for name, row, zlev in (("bot", 0, -hw), ("top", nw, 0.0)):
        F = base[:, None, :] + zlev * up + yf[None, :, None] * lat
        idx = -np.ones((len(s), n_flange + 1), np.int64)
        others = [j for j in range(n_flange + 1) if j != jc]
        new = model.add_nodes(F[:, others].reshape(-1, 3)).reshape(len(s), len(others))
        idx[:, others] = new
        idx[:, jc] = web[:, row]
        grids[name] = idx.astype(np.int32)
    els["web"] = model.add_shells(grid_conn(web), sec.tw, mat, tgroup, part + ".web")
    els["bot"] = model.add_shells(grid_conn(grids["bot"]), sec.tf, mat, tgroup, part + ".bot")
    top = grids["top"]
    if cope_top > 0:
        k = int(np.searchsorted(s, cope_top - 1e-9))
        top_used = top[k:]
    else:
        top_used = top
    els["top"] = model.add_shells(grid_conn(top_used), sec.tf, mat, tgroup, part + ".top")
    return {"grids": grids, "els": els, "s": np.asarray(s), "axis": axis, "up": up, "lat": lat, "base": base,
            "zw": zw, "yf": yf, "sec": sec, "hw": hw}
