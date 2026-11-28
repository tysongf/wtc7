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
| 2026-10-31T16:56Z | docs/preregistration.md (change log: Section 6 repeat of the combined run and the divergence diagnostic; before either run) | 597ca147847bb51f997327b8fa253f41dadd140c44985c4bdcfea0741d3b8bb5 |
| 2026-11-01T06:52Z | docs/preregistration.md (change log: NIST-replica diagnostic for gate item 5; before any of its runs) | 9d4a8db1f39dba5abaefd55a4f5d9827d4de69bc68dbe6e67205a3774876004c |
| 2026-11-26T06:16Z | docs/preregistration.md (change log: conditional Phase 3 start recorded) | d0e104390c165922a533327bf069b4deeb35f30538184df42600a7ffeec57ed7 |
| 2026-11-26T06:16Z | docs/phase3_preregistration.md (Phase 3 finalized; before any Phase 3 calculation) | ae4ef1f3f1dd05ca3b1d7885270c055e7c12709836e6a8afb9d22f8851ff6cf5 |

No finite-element run had been made when the first two hashes were recorded. The third was recorded after the first (superseded) baseline run and the fourth after all reported runs; each adds a change-log entry only. The fifth was recorded after all priority-2 runs and before the two follow-up runs it describes; the sixth after those and before any NIST-replica run.

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

### 2026-11-01 to 2026-11-02: NIST-replica diagnostic

- `nist_replica` (`--set nist`, one job on 4 threads) started 2026-11-01T06:53Z, after the change-log
  hash above, and finished 2026-11-01T08:50Z (7,068 s). It walked off, so the four restore runs
  (`--set nist_restore`, two jobs on 2 threads each) ran from 2026-11-02T02:10Z to 2026-11-02T09:41Z,
  3.2 to 4.1 h each. The laptop was rebooted between the two sets; no run was in progress.

## Phase 3: hand calculations and solver verification

### 2026-11-26 to 2026-11-28: Steps 1 to 3

- `docs/phase3_preregistration.md` (`ae4ef1f3f1dd...`) and `docs/phase3_plan.md` were locked and hashed
  above at `2026-11-26T06:16Z` prior to any Phase 3 calculation.
- `phase3/hand_calcs.py` ran after the hash was recorded and wrote `results/phase3/hand_calcs.md` and
  `results/phase3/hand_calcs.json` (tributary loads within 1 to 2 % of NIST Floor-8 ANSYS loads; double-span
  bridging and falling-floor impact energy bounds; AISC 360 E3 critical unbraced storey counts for Columns
  79, 80, 81, 76, 77, 78; Truss 2 east-support loss check).
- `wtc7/xfe` (`wtc7/xfe/kernel.c`, `wtc7/xfe/__init__.py`) was extended with 3D co-rotational elastoplastic
  fibre beam-columns (3-point Gauss-Lobatto x 32-fibre sections, exact Rodrigues nodal orientation tracking,
  smooth removal multiplier `bfac`), coupled 6-DOF breakable connections and two-storey column splices, and
  mass-conserving node-to-floor impact contact.
- All 8 closed-form Phase 3 checks (`tests/test_phase3_xfe.py`) and all 41 Phase 1 tests pass (`49 passed`).
- Independent 3D frame sudden center-column removal benchmark (`phase3/verify_benchmark.py` ->
  `results/phase3/verification.md`): `wtc7.xfe` (1.45 s wall time, energy balance error `0.03 %`) matches
  CalculiX 2.20 (`B31`, `*DYNAMIC`) within **4.08 %** at Floor 1 and **4.07 %** at the roof (inside the
  pre-registered `10 %` gate).

### 2026-11-28: Steps 4 and 5 (FOIA drawing extraction and 47-storey 3D model verification)

- Extracted storey elevations, 82 main column + 15 transfer sub-column plan coordinates, built-up column and
  two-storey splice schedules, perimeter wind-girder schedules (`WG-1..58`), Transfer Trusses 1 to 3 and plate
  girders (`MG-21, 22, 23, 27, 53`), east/west penthouses, and coupled connection rules (`phase3/data.py` ->
  `data/phase3/*.json`, `docs/phase3_assumptions.md` `A100` to `A112`) from Frankel `E12/13`, `E120` and
  Cantor `S-14`, `S-15`, `S-16`, `S-17`, `S-17A`, `S-18`, `S-22`, `S-23`.
- Assembled the 47-storey + penthouse 3D model (`phase3/building_model.py`: `24,762` 6-DOF nodes = `148,572`
  DOFs, `16,939` 16-fibre co-rotational beam-columns, `17,736` breakable interior/spandrel/splice/slab-tie
  joints, `dt = 1.70e-4 s`, `0.337 %` added mass, `~2.68 ms/step` on 4 physical threads with L3-cached exact
  elastic resultant tracking, lock-free sparse CSR joint gather, fused single-pass central-difference update,
  and `.npz` settled-state checkpointing).
- Static gravity verification (`phase3/verify_model.py` -> `results/phase3/model_summary.md` & `.json`):
  settled at `t = 1.85 s` (`29.9 s` wall time) with `KE / IE = 0.065 %` (`< 1 %`), roof `|v_z| = 0.080 in./s`
  (`< 0.10 in./s`), energy balance error `0.061 %` (`< 5 %`), zero prematurely detached joints under `1.0x`
  service gravity, total Floor-8 gravity `173,637 kip` (`-0.29 %` vs NIST `174,136 kip` target), and East/Core
  column axial loads matching `NCSTAR 1-9 Fig. 11-21` (`Col 79 = 7,632 kip` vs `7,525 kip`, `+1.4 %`;
  `Col 80 = +0.2 %`; `Col 81 = -0.5 %`; `Col 76 = +0.3 %`; `Col 78 = +1.2 %`). First vertical superstructure
  period `T_v1 = 0.649 s` fixes pre-registered removal duration `t_r = 0.0649 s` prior to any removal run.
- Full test suite: `53 passed` (`41` Phase 1 + `8` Phase 3 solver + `4` Phase 3 47-storey building tests).
