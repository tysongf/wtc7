# Compute log

Hardware for all runs below unless stated: 8 logical CPUs (Intel(R) Core(TM) i5-8365U CPU @ 1.60GHz), 15 GB RAM, Linux 6.1.0-54-amd64.

## Pre-registration hash

| Time (UTC) | File | SHA-256 |
|------------|------|---------|
| 2026-10-22T06:56Z | docs/preregistration.md | 8732aee0e240e548d8a61a95614644d6ee7b7438caebd623eee1a07a8afb9335 |
| 2026-10-22T07:02Z | docs/preregistration.md (amended: S15 added) | 26c283764387fda59ca62aeb93b427a2eed4312c58cccb2c041186d010e9f2b8 |
| 2026-10-22T07:20Z | docs/preregistration.md (change log: A48 geometry correction; no criterion changed) | dc163303c816f19b3ac03a101259df556cf66b4eef56d69aa4fda7194e087486 |
| 2026-10-22T09:25Z | docs/preregistration.md (change log: follow-up runs recorded; no criterion changed) | a5af34e3868ffa4f3ee0f95eabe9f5024f1ff30c360d38fc3da46c6f93d7f2bd |
| 2026-10-23T09:29Z | docs/preregistration.md (Section 9 added: detailed model; before any thermal run of it) | e82ed1730ab327835debb6ad36bbd919f8d049bf07369b66b9bf4ed3f0a74a88 |
| 2026-10-25T20:54Z | docs/preregistration.md (change log: Section 9.4 rate rule applied; 0.9 in. mesh run at half rate; quarter-rate diagnostic added; before any of those runs) | 68ced1e6022e3fe03aa7437fc56970bf2e0849cd49b4227a1665770351bad7e4 |
| 2026-10-25T20:57Z | docs/preregistration.md (change log: priority 2 at half rate; before any priority-2 run) | 00615045e1c4c5acf9cd32d1f4bfcd7341b08849d567124bdf95640401338e0c |

No finite-element run had been made when the first two hashes were recorded. The third was recorded after the first (superseded) baseline run and the fourth after all reported runs; each adds a change-log entry only.

## Runs

### Solver and settings (Phase 1 beam-element model)

`wtc7/fe2d.py`: 2D corotational Euler-Bernoulli beams (3 Gauss points, 13 fibres per section:
12 flange strips + 1 web), temperature-dependent elastoplastic steel with isotropic hardening on
the NIST or EC3 flow curve, thermal strain. Connections are zero-length springs. Implicit Newmark
(beta 0.3025, gamma 0.6) in pseudo-time with lumped mass scaled by 100 and mass-proportional
damping 2 /s; step 2 s (2 °C), halved on non-convergence down to 2/4096 s; Newton with up to 25
iterations and a 3-step backtracking line search; after each converged step every breakable
spring is checked and the step re-solved with failed springs removed (the NIST §11.2.9 approach).
Contact penalties: normal 5.0e4 kip/in., tangential 2.0e4 kip/in. Quasi-static checks: kinetic over
stored strain energy, and a run at half the heating rate.

### Run history before the reported set

| Run | Code state | Outcome | Wall time | Use |
|---|---|---|---|---|
| baseline, first attempt | contact force sign error | diverged at 124 °C | 45 s | none (bug found, unit tests added) |
| baseline, second attempt | square bearing faces (normal to girder), contact penalties 5,000 / 1,000 kip/in., no line search | girder end snapped 6.1 in. east at 368 °C beam, solver stopped (INCOMPLETE) | 280 s | superseded; led to the A48 geometry correction (preregistration change log) |
| baseline, third attempt | grid bearing faces, soft penalties | stopped by hand at about 130 °C to stiffen contact (penetration about 0.2 in. at 1,000 kip) | n/a | none |
| check_solver_nolinesearch | grid faces, stiff penalties, no line search, no flow-table cache | see summary | see summary | solver cross-check against the reported baseline |

### Reported runs (2026-10-22)

67 runs: 31 primary (baseline, S1 to S15, the preregistered most-favourable combination,
mesh, rate and solver checks, square-face diagnostic) and 36 follow-up (friction scan,
skew, mesh checks of the walk-off runs, every parameter at friction 0.20, half-rate checks,
NIST-like idealization, corrected most-favourable combination). Total wall time 5.7 h on the
hardware above, 3 or 4 runs at a time, one core each. Median run 268 s (range 77 s to 1,303 s;
runs with the released slab are the slowest because of the extra slab nodes).

| Mesh | Elements | DOF | Wall time, baseline configuration |
|---|---|---|---|
| Baseline (2 elements per girder segment, 1 per stud spacing) | 153 | 498 | 326 s |
| x2 | 306 | 957 | 372 s |
| x4 | 612 | 1,875 | 458 s |

Per-run element counts, steps, wall times and statuses: `results/phase1/summary.md`, section
"Compute". Raw histories: `results/phase1/runs/*.json`.

To budget a rerun of all 67 runs: about 6 core-hours with this code and hardware.

## 2026-10-23: drawings, screening re-run, detailed model

### Screening model with the drawings geometry

`phase1/plan_model.py` with `geometry=drawings` (assumptions A90 to A99), same solver and settings as
above. Output in `results/phase1/runs_drawings/` (`WTC7_RUNS=runs_drawings phase1/run_one.py ...`).
One core per run, three or four at a time; about 350 to 470 s per run.

### Detailed (shell) model

Solver `wtc7/xfe` (C kernel `wtc7/xfe/kernel.c`, compiled on first use with
`gcc -O3 -march=native -fopenmp`; gcc 12, Debian 12). Belytschko-Lin-Tsay shells with five Gauss
points through the thickness. Stiffness hourglass control with coefficient 0.1. Central differences
at 0.9 of the smallest stable element step; elements below the per-part median step get added mass,
which is reported for each run. Mass-proportional damping 1.26 /s. Penalty contact at 0.1 m/dt^2.

| Item | Value |
|---|---|
| Speed on a 44k-shell test model, 4 s of simulated time | 1 thread 2.5 h; 2 threads 1.4 h; 4 threads 1.0 h (4.8 ms/cycle) |
| CalculiX for the verification cross-check | 2.20 from the Debian packages, unpacked locally (`scripts/get_calculix.sh`) |

Gravity-only pilots (no heating) were run on the coarse mesh to check the load path. They are
not results. The first pilots found the exterior-seat clamping that led to A99.

### 2026-10-24: wall times and where the runs were made

The full-mesh baseline took 14.7 h of wall time on the laptop (four cores, two runs at a time),
against about 2.5 h predicted from a short timing pilot. The cause was not the CPU: the laptop was
suspending (37 suspends since boot by 2026-10-25), and the run's process had about 15 % of the wall
time on the CPU. Suspend was disabled at about 2026-10-25T02:50Z; after that a full-rate 1.8 in. run
took 2.9 to 3.1 h with two threads (about 13.4 ms per cycle). The plan to move the runs to a faster
machine (`docs/running_elsewhere.md`) was dropped on 2026-10-25, and all runs are made on the laptop.
Wall times recorded before that (`wall_s` in the run JSONs of baseline, mu0, mu0.1, mu0.2 and mu0.22)
include sleep. The suspend count reached 40 by 2026-10-26T22:00Z, so a few later runs include short
sleeps as well (the half-rate runs took 3.7 to 4.7 h). No result depends on wall time.

### 2026-10-25 to 2026-10-27: rate check, half-rate set and the 0.9 in. mesh

- The full-rate priority-1 set (17 runs) was completed on 2026-10-25. The half-rate baseline moved
  T_E3 by 411 C, so the Section 9.4 rule applies (change log and hashes above). The half-rate set
  (`--set p1_half`, 15 runs and a quarter-rate baseline) ran from 2026-10-25T21:00Z to
  2026-10-27T07:12Z.
- The 0.9 in. half-rate mesh run (`check_mesh_fine_r0.5`) first diverged after 30 cycles. The cause was
  a mesh-generation fault, not the solver. Each beam's skewed end cut (flange-tip offset up to 1.04 in.)
  was tapered over the first station interval only; at 0.9 in. that interval is shorter than the offset,
  so the corner elements at the flange tips folded nearly flat (smallest edge 0.057 in., characteristic
  length 0.003 in.). The taper now runs to the first station at least 1.5 times the offset
  (`phase1/shell_model.py`). The 1.8 and 3.6 in. meshes are unchanged: their node coordinates and
  connectivity hash the same before and after the change. At 0.9 in. the smallest edge is now 0.387 in.,
  and 2,000 cycles step stably. The diverged attempt is kept in `results/phase1/shell/superseded/`, and
  the run was restarted on 2026-10-27, beside the priority-2 queue.
