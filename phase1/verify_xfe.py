"""Benchmarks for the explicit shell solver beyond the unit tests (tests/test_xfe.py).

Lateral-torsional buckling of a simply supported I-beam under equal end moments: the
explicit solver (Southwell estimate from a slow load ramp with an L/2000 lateral sweep)
against the Vlasov closed form and against CalculiX 2.20 S4 shells (linear buckling, same
mesh). Writes results/phase1/shell/verification.md.

Usage: python phase1/verify_xfe.py   (CalculiX from tools/calculix, see scripts/get_calculix.sh)
"""
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wtc7 import xfe  # noqa: E402
from wtc7.xfe import mesh  # noqa: E402

OUT = ROOT / "results" / "phase1" / "shell"
CCX = ROOT / "tools" / "calculix" / "usr" / "bin" / "ccx"
CCX_LIB = ROOT / "tools" / "calculix" / "usr" / "lib" / "x86_64-linux-gnu"


@dataclass
class Sec:
    d: float
    bf: float
    tf: float
    tw: float


SEC = Sec(8.0, 4.0, 0.25, 0.2)
L, E, NU = 160.0, 29000.0, 0.3


def theory():
    G = E / (2 * (1 + NU))
    h0 = SEC.d - SEC.tf
    Iy = 2 * SEC.tf * SEC.bf**3 / 12 + h0 * SEC.tw**3 / 12
    J = (2 * SEC.bf * SEC.tf**3 + h0 * SEC.tw**3) / 3
    Cw = h0**2 / 4 * (2 * SEC.tf * SEC.bf**3 / 12)
    return np.pi / L * np.sqrt(E * Iy * G * J + (np.pi * E / L) ** 2 * Iy * Cw)


def beam(nel, nf, qhg, sweep=True):
    m = xfe.Model(qhg=qhg)
    m.add_material(xfe.elastic_material("el", E))
    s = np.linspace(0, L, nel + 1)
    h0 = SEC.d - SEC.tf
    mem = mesh.wshape(m, SEC, [0, 0, 0], [1, 0, 0], [0, 0, 1], s, nf, h0 / nf, 0, 1, "b",
                      sweep=(lambda x: L / 2000 * np.sin(np.pi * x / L)) if sweep else None)
    gr = mem["grids"]
    for k in (0, -1):
        m.fix(gr["web"][k, :], (1,))
        m.fix(gr["web"][k, 0], (2,))
    m.fix(gr["web"][0, 0], (0,))
    m.finalize()
    return m, mem


def end_couples(m, mem, nf):
    """Nodal x-forces giving a unit moment at each end (compression in the top flange)."""
    h0 = SEC.d - SEC.tf
    gr = mem["grids"]
    f = np.zeros((m.nn, 3))
    for k, sgn in ((0, 1.0), (-1, -1.0)):
        for row, zs in ((gr["top"], 1.0), (gr["bot"], -1.0)):
            w = np.full(nf + 1, 1.0 / nf)
            w[0] = w[-1] = 0.5 / nf
            f[row[k, :], 0] += -sgn * zs * w / h0
    return f


def xfe_ltb(nel, nf, qhg, Tr=1.5):
    m, mem = beam(nel, nf, qhg)
    Mcr = theory()
    m.set_load_pattern(end_couples(m, mem, nf))
    web = mem["grids"]["web"]
    mid = len(mem["s"]) // 2
    hist = []

    def mon(mm):
        hist.append((min(mm.t / Tr, 1.0) * 1.2 * Mcr, abs(mm.x[web[mid, -1], 1] - mm.x0[web[mid, -1], 1]),
                     mm.energy[0], mm.energy[1]))

    t0 = time.time()
    m.run(Tr, lambda t: np.array([20.0, 20.0]), lam=lambda t: min(t / Tr, 1.0) * 1.2 * Mcr, monitor=mon, every=500)
    h = np.array(hist)
    sel = (h[:, 0] > 0.4 * Mcr) & (h[:, 0] < 0.95 * Mcr)
    slope = np.polyfit(h[sel, 1], h[sel, 1] / h[sel, 0], 1)[0]
    return 1.0 / slope, h[-1, 3] / max(h[-1, 2], 1e-12), time.time() - t0


def ccx_ltb(nel, nf, work):
    m, mem = beam(nel, nf, 0.1, sweep=False)
    gr = mem["grids"]
    job = f"ltb_{nel}_{nf}"
    f = end_couples(m, mem, nf)
    with open(work / f"{job}.inp", "w") as fh:
        fh.write("*NODE, NSET=NALL\n")
        for i, p in enumerate(m.x0):
            fh.write(f"{i + 1}, {p[0]:.6f}, {p[1]:.6f}, {p[2]:.6f}\n")
        for part, key, t in (("WEB", "web", SEC.tw), ("TOP", "top", SEC.tf), ("BOT", "bot", SEC.tf)):
            fh.write(f"*ELEMENT, TYPE=S4, ELSET={part}\n")
            for e in mem["els"][key]:
                c = m.conn[e] + 1
                fh.write(f"{e + 1}, {c[0]}, {c[1]}, {c[2]}, {c[3]}\n")
        fh.write("*MATERIAL, NAME=EL\n*ELASTIC\n29000., 0.3\n")
        for part, t in (("WEB", SEC.tw), ("TOP", SEC.tf), ("BOT", SEC.tf)):
            fh.write(f"*SHELL SECTION, ELSET={part}, MATERIAL=EL\n{t}\n")
        fh.write("*BOUNDARY\n")
        for k in (0, -1):
            for n in gr["web"][k, :]:
                fh.write(f"{n + 1}, 2, 2\n")
            fh.write(f"{gr['web'][k, 0] + 1}, 3, 3\n")
        fh.write(f"{gr['web'][0, 0] + 1}, 1, 1\n")
        fh.write("*STEP\n*BUCKLE\n2\n*CLOAD\n")
        for n in np.nonzero(f[:, 0])[0]:
            fh.write(f"{n + 1}, 1, {f[n, 0]:.8e}\n")
        fh.write("*END STEP\n")
    env = dict(os.environ, LD_LIBRARY_PATH=str(CCX_LIB), OMP_NUM_THREADS="2")
    subprocess.run([str(CCX), "-i", job], cwd=work, env=env, capture_output=True, check=True)
    dat = (work / f"{job}.dat").read_text()
    vals = re.findall(r"^\s+1\s+([-+0-9.Ee]+)\s*$", dat.split("B U C K L I N G")[1], re.M)
    return float(vals[0])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    work = OUT / "ccx_work"
    work.mkdir(exist_ok=True)
    Mcr = theory()
    rows = []
    for nel, nf in ((80, 4), (160, 8)):
        ccx = ccx_ltb(nel, nf, work) if CCX.exists() else float("nan")
        for qhg in (0.05, 0.1):
            if nel == 160 and qhg == 0.05:
                continue
            sw, hg, wall = xfe_ltb(nel, nf, qhg)
            rows.append((nel, nf, qhg, sw, ccx, hg, wall))
            print(rows[-1], flush=True)
    lines = ["# Explicit shell solver: lateral-torsional buckling benchmark", "",
             "Simply supported I-beam (d = 8, bf = 4, tf = 0.25, tw = 0.2 in., L = 160 in., E = 29,000 ksi), fork",
             "supports, equal end moments. Explicit run: moment ramped to 1.2 Mcr over 1.5 s with an L/2000 lateral",
             "sweep; Mcr from a Southwell fit between 0.4 and 0.95 Mcr. CalculiX 2.20: S4 shells, *BUCKLE, same mesh,",
             "no sweep. Generated by `phase1/verify_xfe.py`.", "",
             f"Vlasov closed form (flange-only warping constant): Mcr = {Mcr:.1f} kip-in.", "",
             "| Mesh (along x per flange) | Hourglass coefficient | Explicit, Southwell (kip-in.) | CalculiX S4 (kip-in.) | Explicit / CalculiX | Explicit / theory | Hourglass / internal energy |",
             "|---|---|---|---|---|---|---|"]
    for nel, nf, qhg, sw, ccx, hg, wall in rows:
        lines.append(f"| {nel} x {nf} | {qhg} | {sw:.1f} | {ccx:.1f} | {sw / ccx:.3f} | {sw / Mcr:.3f} | {hg:.3f} |")
    lines += ["", "The detailed model uses hourglass coefficient 0.1 (A83) and at least four elements across every",
              "flange; its beam flanges are about 1.75 in. per element at the 1.8 in. mesh."]
    (OUT / "verification.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
