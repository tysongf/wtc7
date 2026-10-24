"""Figures for the forensic report (reports/forensic/), drawn from the model geometry and run outputs.

Each function writes one PNG into the given directory and returns its file name, or None when
the data it needs do not exist yet.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "phase1"))
from wtc7 import assumptions as asm  # noqa: E402
from wtc7.geometry import geometry_set  # noqa: E402
from wtc7.sections import shape  # noqa: E402

SHELL = ROOT / "results" / "phase1" / "shell" / "runs"
NIST_T82 = {"First stud": 103, "Col 79 seat bolts": 154, "Col 79 all bolts (E1)": 194,
            "Col 44 all bolts (E3)": 476, "First beam buckles (E4)": 436}
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 130})


class _Cfg:
    def __init__(self, geometry, **kw):
        self.geometry, self.skew, self.slot, self.gap79, self.gap44_lat = geometry, 0.0, -1.0, -1.0, -1.0
        self.side_plates, self.bearing, self.end79 = "auto", "grid", 0.0
        self.__dict__.update(kw)


def plan_geometry(out):
    """Girder and beams in plan, digitized (revision 1) against the drawings."""
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    for geo, col, lab in (("digitized", "0.6", "digitized from NCSTAR Fig. 8-16 (superseded)"),
                          ("drawings", "C0", "Frankel E12/13 and 9114")):
        G = geometry_set(_Cfg(geo))
        th = math.radians(G["skew"])
        eg = np.array([math.sin(th), math.cos(th)])
        ax.plot([0, G["LG"] * eg[0]], [0, G["LG"] * eg[1]], color=col, lw=2.5, label=f"girder, {lab}")
        for s, L in zip(G["stations"], G["spans"]):
            p = s * eg
            ax.plot([p[0], p[0] + L], [p[1], p[1]], color=col, lw=1.0)
        if geo == "drawings":
            c79 = G["centre"]
            rho = math.radians(asm.value("A93")["rotation"])
            Np, Ep = np.array([math.sin(rho), math.cos(rho)]), np.array([math.cos(rho), -math.sin(rho)])
            box = [c79 + a * 13.0 * Np + b * 10.94 * Ep for a, b in ((-1, -1), (-1, 1), (1, 1), (1, -1), (-1, -1))]
            ax.plot(*np.array(box).T, color="k", lw=1)
            ax.text(*(c79 + [-60, -10]), "col 79\n(rotated 12.3 deg)", fontsize=7)
            c44 = (asm.value("A91")["span"] - asm.value("A91")["end79"]) * eg
            ax.add_patch(plt.Rectangle(c44 - [10.8, 8.85], 21.6, 17.7, fill=False, color="k"))
            ax.text(*(c44 + [-70, 12]), "col 44 (on grid)", fontsize=7)
    ax.set_aspect("equal")
    ax.set_xlabel("x, east (in.)")
    ax.set_ylabel("y, north (in.)")
    ax.legend(fontsize=7, loc="lower right")
    ax.set_title("Floor 13, northeast bay: girder A2001 and the five beams framing into it")
    fig.tight_layout()
    fig.savefig(out / "plan_geometry.png")
    plt.close(fig)
    return "plan_geometry.png"


def recess_detail(out):
    """Column 79 north face, side plates and the girder end, in the column's own axes (A93 to A95)."""
    a94, a95 = asm.value("A94"), asm.value("A95")
    g = shape("W33X130")
    phi = math.radians(asm.value("A93")["girder_to_axis"])
    end = asm.value("A91")["end79"]
    gax = np.array([math.sin(phi), math.cos(phi)])          # girder axis in (E', N')
    glat = np.array([math.cos(phi), -math.sin(phi)])        # girder lateral, east
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    hd, pe, pi, t = a94["half_depth"], a94["plate_end"], a94["plate_inner"], a94["plate_t"]
    ax.add_patch(plt.Rectangle((-pi, -hd), 2 * pi, 2 * hd, color="0.85", label="W14x730 (flanges and web)"))
    for sgn in (-1, 1):
        ax.add_patch(plt.Rectangle((sgn * pi if sgn > 0 else -pi - t, -pe), t, 2 * pe, color="0.45",
                                   label="side cover plates 26 x 2" if sgn > 0 else None))
    c = end * gax
    corners = [c + sgn * g.bf / 2 * glat for sgn in (-1, 1)]
    far = [p + 30 * gax for p in corners]
    ax.plot([corners[0][0], corners[1][0]], [corners[0][1], corners[1][1]], color="C0", lw=2, label="girder end (flange)")
    for p, q in zip(corners, far):
        ax.plot([p[0], q[0]], [p[1], q[1]], color="C0", lw=1)
    seat = [c + (hd / math.cos(phi) - end) * gax + sgn * 6.0 * glat for sgn in (-1, 1)]
    seat += [p + a95["length"] * gax for p in seat[::-1]]
    ax.fill(*np.array(seat).T, color="C1", alpha=0.25, label="seat pf, 12 x 8 1/4")
    ax.axhline(pe, color="k", lw=0.6, ls=":")
    ax.text(-pi - t - 0.5, pe + 0.4, "plate ends (recess mouth)", fontsize=7, ha="left")
    w = corners[0]
    ax.annotate("", xy=(-pi, w[1] - 1.2), xytext=(w[0], w[1] - 1.2), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((w[0] - pi) / 2, w[1] - 2.4, f"{w[0] + pi:.2f} in.", ha="center", fontsize=7)
    ax.set_xlim(-16, 16)
    ax.set_ylim(-4, 26)
    ax.set_aspect("equal")
    ax.set_xlabel("E' (in.), column 79 transverse axis, east +")
    ax.set_ylabel("N' (in.), toward the girder")
    ax.set_title("Column 79 at the girder seat, as drawn (1091, 9114)")
    ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(out / "recess_detail.png")
    plt.close(fig)
    return "recess_detail.png"


def _runs():
    return {f.stem: json.loads(f.read_text()) for f in sorted(SHELL.glob("*.json"))}


def shell_histories(out):
    runs = _runs()
    if not runs:
        return None
    fig, axs = plt.subplots(2, 2, figsize=(9.5, 6.4))
    for n, r in runs.items():
        rows = r["rows"]
        t = np.array([x["t"] for x in rows])
        T = np.array([x["T_beam"] for x in rows])
        heat = t >= 1.1
        axs[0, 0].plot(t[heat], [x["lat79"] for x in np.array(rows)[heat]], label=n, lw=1)
        axs[0, 1].plot(t[heat], [-x["ax79"] for x in np.array(rows)[heat]], label=n, lw=1)
        axs[1, 0].plot(t[heat], [np.linalg.norm(x["face79"]) for x in np.array(rows)[heat]], label=n, lw=1)
        axs[1, 1].plot(t[heat], [x["twist79"] for x in np.array(rows)[heat]], label=n, lw=1)
    axs[0, 0].axhline(6.25, color="k", ls="--", lw=0.8)
    axs[0, 0].axhline(asm.value("A94")["plate_inner"] - 4.79, color="0.5", ls=":", lw=0.8)
    axs[0, 0].text(1.15, 6.4, "walk-off 6.25 in.", fontsize=7)
    axs[0, 0].text(1.15, 4.3, "west side plate (about 4.15 in.)", fontsize=7, color="0.4")
    axs[1, 1].axhline(math.degrees(math.atan(11.5 / 33.1)), color="k", ls="--", lw=0.8)
    axs[1, 1].text(1.15, 18.0, "E2r: atan(bf/d) = 19.2 deg", fontsize=7)
    for a, lab in zip(axs.ravel(), ("girder end at col 79, west (in.)", "girder end toward col 79 (in.)",
                                     "bearing force on col 79 face (kip)", "girder end twist (deg)")):
        a.set_ylabel(lab)
        a.set_xlabel("time (s); heating 1.1 to 2.6 s, hold to 4.0 s")
        sec = a.secondary_xaxis("top", functions=(lambda t: 20 + np.clip(t - 1.1, 0, 1.5) * 386.7,
                                                  lambda T: 1.1 + (T - 20) / 386.7))
        sec.set_xlabel("beam temperature (C)", fontsize=7)
    axs[0, 0].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(out / "shell_histories.png")
    plt.close(fig)
    return "shell_histories.png"


def shell_beam_forces(out):
    runs = _runs()
    if "baseline" not in runs:
        return None
    rows = runs["baseline"]["rows"]
    t = np.array([x["t"] for x in rows])
    N = np.array([x["beamN"] for x in rows])
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    names = ["K3004 (south)", "C3004", "B3004", "A3004", "G3005 (north)"]
    for k in range(N.shape[1]):
        ax.plot(t, N[:, k], lw=1, label=names[k])
    ax.set_xlabel("time (s)")
    ax.set_ylabel("beam axial force at quarter span (kip), - = compression")
    ax.set_title("Baseline: floor-beam axial forces")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "shell_beam_forces.png")
    plt.close(fig)
    return "shell_beam_forces.png"


def shell_girder_profile(out):
    """Lateral displacement of the girder along its length at 600 C (end of run), from saved node positions."""
    from shell_model import Config, build
    have = [n for n in ("baseline", "check_mesh_coarse") if (SHELL / f"{n}.npz").exists()]
    if not have:
        return None
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    for n in have:
        cfg = json.loads((SHELL / f"{n}.json").read_text())["config"]
        fl = build(Config(mesh=cfg["mesh"], threads=1))
        d = np.load(SHELL / f"{n}.npz")
        x = d["x"][-1].astype(float)
        web = fl.G["grids"]["web"]
        for row, ls, lab in ((0, "-", "bottom flange"), (web.shape[1] - 1, "--", "top flange")):
            nodes = web[:, row]
            ax.plot(fl.G["s"], (x[nodes] - fl.m.x0[nodes]) @ fl.west, ls=ls, lw=1,
                    label=f"{n}, {lab}")
        for s in fl.stations:
            ax.axvline(s, color="0.8", lw=0.6)
    ax.set_xlabel("station along the girder from its col 79 end (in.); grey lines: beams")
    ax.set_ylabel("movement west (in.)")
    ax.set_title(f"Girder lateral movement at the end of the run (beam {d['T_beam'][-1]:.0f} C)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "shell_girder_profile.png")
    plt.close(fig)
    return "shell_girder_profile.png"


def shell_energy(out):
    runs = _runs()
    if "baseline" not in runs:
        return None
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    for n, r in runs.items():
        rows = r["rows"]
        t = np.array([x["t"] for x in rows])
        ke = np.array([x["ke"] for x in rows])
        ie = np.array([x["ie"] for x in rows])
        ok = ie > 1.0
        ax.semilogy(t[ok], (ke / ie)[ok], lw=0.8, label=n)
    ax.axhline(0.05, color="k", ls="--", lw=0.8)
    ax.axvline(1.1, color="0.5", ls=":", lw=0.8)
    ax.text(1.12, 0.3, "heating starts", fontsize=7)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("kinetic / internal energy")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "shell_energy.png")
    plt.close(fig)
    return "shell_energy.png"


ALL = [plan_geometry, recess_detail, shell_histories, shell_beam_forces, shell_girder_profile, shell_energy]
