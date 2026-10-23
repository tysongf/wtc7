"""Run every Phase 1 beam-element configuration (preregistration Section 6) in parallel.

Usage: python phase1/run_phase1.py [--jobs N] [--only name1,name2]
Each run is saved by phase1/run_one.py to results/phase1/runs/<name>.json.
"""
import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable

FAVOURABLE = dict(girder_studs=0, slot=0.656, mu_seat=0.2, col79="flexible", slab="fixed", steel="EC3",
                  fy_scale=1.1, gap79=1.0, gap44_lat=3.0, bolt_slip_fail=0.15, stud_slip_fail=0.10, mu_slab=0.6)

RUNS = {
    "baseline": {},
    "S1_studs22": dict(girder_studs=22),
    "S1_studs30": dict(girder_studs=30),
    "S3_slot0": dict(slot=0.0),
    "S3_slot656": dict(slot=0.656),
    "S4_mu0": dict(mu_seat=0.0),
    "S4_mu0.2": dict(mu_seat=0.2),
    "S4_mu0.45": dict(mu_seat=0.45),
    "S4_mu0.6": dict(mu_seat=0.6),
    "S5_col79_flexible": dict(col79="flexible"),
    "S6_slab_released": dict(slab="released"),
    "S8_heat_cool_600": dict(history="heat-cool", peak=600.0),
    "S9_EC3": dict(steel="EC3"),
    "S10_fy0.9": dict(fy_scale=0.9),
    "S10_fy1.1": dict(fy_scale=1.1),
    "S11_gap79_0.25": dict(gap79=0.25),
    "S11_gap79_1.0": dict(gap79=1.0),
    "S12_gap44_0.5": dict(gap44_lat=0.5),
    "S12_gap44_3.0": dict(gap44_lat=3.0),
    "S13_bolt0.15": dict(bolt_slip_fail=0.15),
    "S13_bolt0.35": dict(bolt_slip_fail=0.35),
    "S14_stud0.10": dict(stud_slip_fail=0.10),
    "S14_stud0.30": dict(stud_slip_fail=0.30),
    "S15_muslab0": dict(mu_slab=0.0),
    "S15_muslab0.6": dict(mu_slab=0.6),
    "favourable": FAVOURABLE,
    "diag_square_bearing": dict(bearing="square"),
    "check_mesh_r2": dict(refine=2),
    "check_mesh_r4": dict(refine=4),
    "check_rate_half": dict(rate=0.5),
}


# Follow-up set, run after the primary set (see docs/phase1_gate.md): friction is the only
# swept input that produced walk-off, so (1) the friction threshold is located more finely,
# (2) the digitized girder skew that sets it is varied, (3) the walk-off runs are mesh-checked,
# and (4) every other parameter's ends are rerun at mu = 0.2 to find which ends actually favour
# walk-off when sliding is possible (preregistration Section 6 rule for the combined run).
FOLLOWUP = {
    **{f"F_mu{m}": dict(mu_seat=m) for m in (0.22, 0.24, 0.26, 0.28)},
    **{f"F_skew{a}_mu{m}": dict(skew=a, mu_seat=m) for a in (12.6, 16.6) for m in (0.2, 0.3)},
    **{f"F_mesh_r{k}_mu{m}": dict(refine=k, mu_seat=m) for k in (2, 4) for m in (0.0, 0.2)},
    "F_square_mu0": dict(bearing="square", mu_seat=0.0),
    # combined run rebuilt from the ends that gave the earliest walk-off in the C_ runs (preregistration
    # Section 6 rule); gap79 stays 0.5 because both 0.25 and 1.0 delayed or prevented walk-off
    "F_favourable_actual": dict(mu_seat=0.2, girder_studs=30, slot=0.0, col79="fixed", slab="released", steel="NIST",
                                fy_scale=1.1, gap79=0.5, gap44_lat=3.0, bolt_slip_fail=0.15, stud_slip_fail=0.10,
                                mu_slab=0.3),
    "F_rate_half_S5": dict(col79="flexible", rate=0.5),
    "F_rate_half_S11_1.0": dict(gap79=1.0, rate=0.5),
    **{f"C_{n}": dict(kw, mu_seat=0.2) for n, kw in RUNS.items()
       if n.startswith(("S1", "S3", "S5", "S6", "S8", "S9", "S10", "S11", "S12", "S13", "S14", "S15"))},
}


# Drawings geometry (A90 to A99, sources/drawings/READING.md): the screening model re-run after the
# shop, erection and structural drawings were obtained; saved to results/phase1/runs_drawings/.
DRAWINGS = {f"D_{k}": dict(v, geometry="drawings") for k, v in {
    "baseline": {},
    "mu0": dict(mu_seat=0.0),
    "mu0.05": dict(mu_seat=0.05),
    "mu0.1": dict(mu_seat=0.1),
    "mu0.2": dict(mu_seat=0.2),
    "clear": dict(side_plates="clear"),
    "mu0_clear": dict(mu_seat=0.0, side_plates="clear"),
    "mu0.2_clear": dict(mu_seat=0.2, side_plates="clear"),
    "heatcool": dict(history="heat-cool", peak=600),
    "heatcool_mu0": dict(history="heat-cool", peak=600, mu_seat=0.0),
    "end-0.4": dict(end79=-0.4),
    "end+0.4": dict(end79=0.4),
}.items()}


def launch(name, kw):
    args = [PY, str(HERE / "run_one.py"), name] + [f"{k}={v}" for k, v in kw.items()]
    t0 = time.time()
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    if kw.get("geometry") == "drawings":
        env["WTC7_RUNS"] = "runs_drawings"
    out = subprocess.run(args, capture_output=True, text=True, env=env)
    line = (out.stdout.strip().splitlines() or [out.stderr.strip()[-300:]])[-1]
    return f"[{time.time() - t0:6.0f} s] {line}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--only", default="")
    ap.add_argument("--set", choices=("primary", "followup", "drawings"), default="primary")
    a = ap.parse_args()
    table = {"primary": RUNS, "followup": FOLLOWUP, "drawings": DRAWINGS}[a.set]
    names = a.only.split(",") if a.only else list(table)
    # longest runs first so the pool stays busy
    names.sort(key=lambda n: -("r4" in n) * 4 - ("r2" in n) * 2 - ("half" in n) * 2 - ("S6" in n or "S8" in n) * 3)
    with ThreadPoolExecutor(a.jobs) as ex:
        for msg in ex.map(lambda n: launch(n, table[n]), names):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
