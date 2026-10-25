"""Run the Phase 1 detailed (shell) model set, preregistration Section 9.

Usage: python phase1/run_shell.py [--jobs N] [--threads T] [--set NAME] [--only a,b] [--skip-done]
Runs are taken in the listed order (priority 1 first). Each run is saved by
phase1/run_shell_one.py to results/phase1/shell/runs/<name>.json and .npz; its console output
goes to results/phase1/shell/logs/<name>.log.
"""
import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PY = sys.executable
RUNS_DIR = ROOT / "results" / "phase1" / "shell" / "runs"
LOGS = ROOT / "results" / "phase1" / "shell" / "logs"

# Priority 1: baseline, friction (S4 and the 0.2 to 0.3 scan), the column 79 side plates (Q12) and the
# girder end position (S11, detailed), peak temperature 700 C (S7), heating then cooling (S8), mesh and
# rate checks, and the girder end stiffeners as drawn.
P1 = {
    "baseline": {},
    "mu0": dict(mu_seat=0.0),
    "mu0.1": dict(mu_seat=0.1),
    "mu0.2": dict(mu_seat=0.2),
    "mu0.22": dict(mu_seat=0.22),
    "mu0.24": dict(mu_seat=0.24),
    "mu0.26": dict(mu_seat=0.26),
    "mu0.28": dict(mu_seat=0.28),
    "Q12_clear": dict(side_plates="clear"),
    "Q12_clear_mu0": dict(side_plates="clear", mu_seat=0.0),
    "S11_end-0.4": dict(end79=-0.4),
    "S11_end+0.4": dict(end79=0.4),
    "S7_peak700": dict(peak=700.0),
    "S8_heat_cool": dict(history="heat-cool", peak=600.0),
    "check_mesh_coarse": dict(mesh=3.6),
    "check_rate_half": dict(rate=0.5),
    "A97_stiffeners": dict(stiffeners="drawn"),
}
# Priority 2: the remaining preregistered one-at-a-time sweeps and the combined run, at half rate
# (change log 2026-10-25: they are compared against the reported, half-rate, baseline).
P2 = {
    "S4_mu0.45": dict(mu_seat=0.45),
    "S4_mu0.6": dict(mu_seat=0.6),
    "S1_studs22": dict(girder_studs=22),
    "S1_studs30": dict(girder_studs=30),
    "S3_slot0": dict(slot=0.0),
    "S3_slot125": dict(slot=0.125),
    "S3_slot656": dict(slot=0.656),
    "S5_col79_flexible": dict(col79="flexible"),
    "S6_slab_released": dict(slab="released"),
    "S7_peak400": dict(peak=400.0),
    "S7_peak500": dict(peak=500.0),
    "S9_EC3": dict(steel="EC3"),
    "S10_fy0.9": dict(fy_scale=0.9),
    "S10_fy1.1": dict(fy_scale=1.1),
    "S12_gap44_0.5": dict(gap44_lat=0.5),
    "S12_gap44_1.0": dict(gap44_lat=1.0),
    "S12_gap44_3.0": dict(gap44_lat=3.0),
    "S13_bolt0.15": dict(bolt_slip_fail=0.15),
    "S13_bolt0.35": dict(bolt_slip_fail=0.35),
    "S14_stud0.10": dict(stud_slip_fail=0.10),
    "S14_stud0.30": dict(stud_slip_fail=0.30),
    "S15_muslab0": dict(mu_slab=0.0),
    "S15_muslab0.6": dict(mu_slab=0.6),
    "favourable": dict(girder_studs=0, slot=0.656, mu_seat=0.2, col79="flexible", slab="fixed", steel="EC3",
                       fy_scale=1.1, end79=0.4, gap44_lat=3.0, bolt_slip_fail=0.15, stud_slip_fail=0.10,
                       mu_slab=0.6, peak=700.0),
}
# Rate check follow-up (Section 9.4): half rate moved E3 of the baseline by more than 10 C, so every
# priority-1 run is repeated at half rate and those become the reported results. check_rate_half is
# the baseline at half rate and is not repeated. Change log 2026-10-25: a quarter-rate baseline is
# added as a diagnostic (reported, replaces nothing).
P1_HALF = {"check_rate_quarter": dict(rate=0.25)}
P1_HALF.update({f"{n}_r0.5": dict(kw, rate=0.5) for n, kw in P1.items() if n not in ("baseline", "check_rate_half")})
# Mesh check follow-up (Section 9.4): the 3.6/1.8 in. pair missed the 2 % criterion on the column 79
# lateral movement, so the baseline is rerun at 0.9 in., at half rate (change log 2026-10-25).
MESH = {"check_mesh_fine_r0.5": dict(mesh=0.9, rate=0.5)}
P2 = {n: dict(kw, rate=0.5) for n, kw in P2.items()}
SETS = {"p1": P1, "p1_half": P1_HALF, "p2": P2, "mesh": MESH, "all": {**P1, **P1_HALF, **MESH, **P2}}


def launch(name, kw, threads):
    LOGS.mkdir(parents=True, exist_ok=True)
    args = [PY, str(HERE / "run_shell_one.py"), name, f"threads={threads}"] + [f"{k}={v}" for k, v in kw.items()]
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    t0 = time.time()
    with open(LOGS / f"{name}.log", "w") as log:
        out = subprocess.run(args, stdout=subprocess.PIPE, stderr=log, text=True, env=env)
    last = (out.stdout.strip().splitlines() or ["(no output)"])[-1]
    return f"[{time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())}] [{time.time() - t0:7.0f} s] {last}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--set", choices=sorted(SETS), default="p1")
    ap.add_argument("--only", default="")
    ap.add_argument("--skip-done", action="store_true")
    a = ap.parse_args()
    table = SETS[a.set]
    names = a.only.split(",") if a.only else list(table)
    if a.skip_done:
        names = [n for n in names if not (RUNS_DIR / f"{n}.json").exists()]
    with ThreadPoolExecutor(a.jobs) as ex:
        for msg in ex.map(lambda n: launch(n, table[n], a.threads), names):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
