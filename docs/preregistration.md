# Pre-registration: Phase 1 outcome criteria and parameter ranges

Written 2026-10-21, before any finite-element run. The SHA-256 of this file is
recorded in `docs/compute_log.md` before the first run; any later edit to this
file must be listed in the change log at the bottom with its reason, and must
not change a criterion or a range after results for that criterion exist.

Sources are cited as NCSTAR 1-9 section or table numbers. "Errata" means the
June 2012 errata to NCSTAR 1-9 (`sources/errata/ncstar1-9_errata.pdf`).

## 1. Events

| ID | Event | Definition | Source |
|----|-------|------------|--------|
| E1 | Col 79 connection damage | All four erection bolts at the col 79 seat (2 seat, 2 top clip) have failed in shear | NCSTAR 1-9 §2.4 (STC: 2 + 2 bolts), §11.2.5 |
| E2 | Walk-off at col 79 (loss of vertical support) | After E1, the girder web has moved off the seat: relative displacement perpendicular to the girder axis >= 6.25 in., or along the axis away from the column >= 5.5 in. | §11.2.5 and §11.2.9 as corrected by the errata (seat 12 in. wide) |
| E2r | Rocking or twist off the seat (detailed model only) | Girder twist at col 79 >= atan(bf/d) | §11.2.9 Eq. 1 |
| E3 | Col 44 connection damage | All four erection bolts at col 44 failed | Table 8-2 |
| E4 | First floor beam buckling | Lateral (in-plan) buckling of a floor beam, detected as loss of axial stiffness or lateral deflection > L/50 | Table 8-2 |

T_E1, T_E2 and so on denote the floor-beam temperature at which the event occurs.
Girder temperature follows NIST's prescribed ratio (T_girder - 20) = 0.828 (T_beam - 20),
which reproduces every row of Table 8-2.

## 2. NIST reference values the model is compared with (not tuned to)

| Quantity | NIST value | Source |
|----------|------------|--------|
| First stud failure | beam 103 °C | Table 8-2 |
| Col 79 seat bolts failed | beam 154 °C, girder 131 °C | Table 8-2 |
| Col 79 all four bolts failed (E1) | beam 194 °C, girder 164 °C | Table 8-2 |
| Col 44 all four bolts failed (E3) | beam 476 °C, girder 398 °C | Table 8-2 |
| First beam buckles (E4) | beam 436 °C | Table 8-2 |
| Girder off seat at col 79 | after all beams buckle (beam 600 °C), by rocking | §8.8, Table 8-2 |
| 16-story model walk-off at col 79, floor 13 | between 3.7 h and 4.0 h; floor 13 steel 300 °C to 700 °C | §11.3.2, §11.4.1 |
| Expansion damage | below about 400 °C (averaged over beam length) | §11.4.1, FAQ 11 |

## 3. Outcome classes (Phase 1)

Each run is classified with these rules. They apply first to the beam-element
screening model and then, for the gate, to the detailed shell model.

- **CONFIRMS** NIST's initiating mechanism if, under the baseline parameter set
  (Section 5), E1 occurs at T_beam <= 400 °C and E2 (or E2r in the detailed model)
  occurs at T_beam <= 700 °C. 700 °C is the top of NIST's reported floor 13 steel
  temperature range (§11.3.2). If E2 occurs at T_beam <= 600 °C, the
  confirmation is also reported as "within NIST's partial-floor ramp".
- **CONTRADICTS** if no E2 (or E2r) occurs at T_beam <= 700 °C in any run of the
  one-at-a-time sweeps and in the "most favourable to walk-off" combined run
  (Section 6), with every parameter inside its range.
- **CONDITIONAL** in every other case. The report then lists each parameter whose
  change moves the result across the 700 °C line, with the value at which it flips.
- A run that stops for numerical reasons before E2 and before 700 °C is reported
  as **INCOMPLETE**, never as "no walk-off".

Runs that continue past 700 °C (up to 800 °C) report T_E2 for information only;
they do not change the class.

## 4. Model checks (must pass before results are used)

| Check | Criterion |
|-------|-----------|
| Free thermal expansion | FE elongation of an unrestrained member within 1 % of the hand calculation, for both steel property sets |
| Fully restrained member | FE axial force within 1 % of A E(T) eps_th(T) while elastic |
| Euler buckling | FE buckling load of a pinned strut within 2 % of pi^2 EI / L^2 |
| Material curves | Rebuilt NIST curves reproduce published Tables E-3 (A36) and E-5 (G40.21-44W): first-point stress within 2 %, other points within 5 % |
| Mesh convergence | T_E1 and T_E2 change by less than 10 °C (or 2 %, whichever is larger) between the two finest meshes (element size ratio 2). If no E2, the col 79 lateral displacement at 700 °C changes by less than 2 % |
| Quasi-static (explicit or dynamic-relaxation runs only) | Kinetic energy below 5 % of internal energy throughout |

## 5. Baseline parameter set (NIST partial-floor model, §8.8)

Columns 44, 79 and exterior columns fixed against lateral displacement; slab
unheated and constrained in-plane on all four edges; uniform monotonic ramp to
beam 600 °C / girder 500 °C; gravity 87.5 psf (75 psf dead plus 25 % of 50 psf
live, Fig. 11-17 and §11.2.7, consistent with the Fig. 8-24 plateau).

## 6. Sensitivity ranges (fixed now)

One parameter at a time from the baseline. "Favours walk-off" is the end of each
range that physical reasoning says should make walk-off easier; it defines the
combined "most favourable to walk-off" run. If a sweep shows the reasoning was
wrong, the report says so and the combined run is repeated with the end that
actually favoured walk-off; the result of both versions is reported.

| # | Parameter | Baseline | Values tested | Favours walk-off | Basis for baseline |
|---|-----------|----------|---------------|------------------|--------------------|
| S1 | Girder shear studs, cols 44 to 79 | 0 | 0; 22; 30 | 0 | FAQ 27; 22 and 30 are unverified estimates (see assumptions A40, A41) |
| S2 | Lateral walk-off distance at col 79 | 6.25 in. | 5.5 (original report text); 6.0; 6.25; 6.5 | 5.5 | Errata |
| S3 | Top-clip bolt slot half-allowance at col 79 | 0.125 in. (short slot) | 0; 0.125; 0.656 (long slot) | 0.656 | §11.2.5 says slotted, size not stated |
| S4 | Seat friction coefficient | 0.30 | 0 (reference, NIST describes none); 0.2; 0.3; 0.45; 0.6 | 0.2 (0 reported separately) | AISC 360 §J3.8 Class A slip coefficient 0.30, used as a proxy (not confirmed against a copy in this repo) |
| S5 | Lateral restraint at col 79 | fixed | fixed; elastic spring for a two-storey pinned W14x730 (see A30) | flexible | §8.8; FAQ 28 |
| S6 | Slab edge constraints | all edges fixed in-plane | fixed; west and south released | fixed | §8.8 |
| S7 | Peak temperature (beam / girder) | 600 / 500 °C | 400/332, 500/417, 600/500, 700/583 °C | 700 | §8.8, Fig. 8-25 |
| S8 | Heating then cooling | monotonic | heat to 600/500, cool to 20 °C | not assigned | brief |
| S9 | Steel property set | NIST (Appendix E rebuilt) | NIST; EN 1993-1-2 | EN 1993-1-2 (larger thermal strain above about 400 °C) | brief |
| S10 | Yield strength | nominal per set | -10 %; 0; +10 % | +10 % (beams buckle later, push longer) | brief |
| S11 | Girder-end clearance to col 79 face | 0.5 in. | 0.25; 0.5; 1.0 | 1.0 | not stated in NCSTAR 1-9 |
| S12 | Girder lateral gap at col 44 | 1.0 in. | 0.5; 1.0; 3.0 | 3.0 | not stated |
| S13 | Bolt shear deformation at failure | 0.25 in. | 0.15; 0.25; 0.35 | 0.15 | not stated |
| S14 | Stud slip at failure | 0.20 in. | 0.10; 0.20; 0.30 | 0.10 | not stated |
| S15 | Beam-to-slab interface friction after stud failure (girder-to-slab stays frictionless, §11.2.3) | 0.30 | 0; 0.3; 0.6 | 0.6 (beams stay braced and keep pushing) | not stated; same proxy as S4 |

## 7. What the beam-element model can and cannot decide

The Phase 1 beam-element model is a plan-view (horizontal plane) model. It
captures axial expansion, connection slip, bolt and stud failure, friction,
gaps and contact, girder weak-axis bending and in-plan buckling of beams. It
does not capture vertical sagging, lateral-torsional buckling with twist, or
rocking. Its outcome class is reported as a screening result. The Phase 1 gate
(Section 8) requires the detailed shell model.

## 8. Phase 1 gate

Phase 1 passes, and Phase 2 may start, only when all of the following hold:

1. Hand calculations complete (`results/phase1/hand_calcs.md`).
2. Beam-element model passes every check in Section 4 and the baseline and all S1 to S15 runs are reported.
3. Detailed shell model (NIST §8.8 approach) built, passes every check in Section 4, baseline and sweeps reported.
4. Column 79 buckling check at nine storeys complete.
5. The outcome class from the detailed model is stated. If it differs from NIST,
   the specific modelling choice that explains the difference is identified.

## 9. Detailed shell model (gate item 3)

Written 2026-10-23, before any thermal run of the detailed model. Only gravity-only pilots of
the detailed model (load path and timing checks) had been run. The shop, erection and structural
drawings were obtained the same day (`sources/drawings/READING.md`). They settle Q12 and Q13 and
correct the digitized geometry the screening model used. The detailed model therefore uses the
drawings geometry (assumptions A90 to A99). The screening model was also re-run with that geometry
(`results/phase1/runs_drawings/`); those runs are reported as screening results and set no criterion
below.

### 9.1 Model

As in `docs/phase1_detailed_model_plan.md`, with the drawings geometry:
- girder skew 16.5 deg;
- beam stations and spans from E12/13;
- column 79 rotated 12.3 deg, so its north flange face is 4.17 deg off square to the girder;
- column 79 side cover plates as drawn, projecting 1.81 in. past that face; the girder end at the
  recess mouth;
- 12 x 8 1/4 in. seat plate aligned with the girder;
- standard holes at the column 79 clip angle;
- column 44 on the grid, its flanges confining the girder end, with slotted top-plate holes.

NIST omissions kept in the baseline:
- girder end stiffeners (run as drawn as a sensitivity, A97);
- the W12x26 framing in from the west;
- camber.

Solver: `wtc7.xfe` (Belytschko-Lin-Tsay shells, explicit), written for this study because OpenRadioss
was withdrawn by its owner in October 2026 and its fork depends on a proprietary input reader. It is
verified in `tests/test_xfe.py` and `results/phase1/shell/verification.md`.

### 9.2 Schedule and events

- **Schedule:** NIST's §8.8 schedule.
  - Gravity is ramped smoothly from 0 to 1 s.
  - Uniform heating starts at 1.1 s at 386.7 C/s (beam temperature); the girder follows A35.
  - The peak is 600 C beam / 500 C girder.
  - The temperature is held for 1.4 s after the peak.
- **Events:** as in Section 1, plus:
  - E2r: twist of the girder end at column 79 >= atan(bf/d);
  - E2s: physical loss of support, when the girder end at column 79 drops 2 in.;
  - side-plate bearing at column 79, recorded as the Q12 indicator.
- **E2 for classification:** the first of E2, E2r or E2s.

### 9.3 Parameter values

Section 6 applies, with these changes. Each is forced by the drawings or added before any thermal
run of this model.

| # | Change for the detailed model | Reason |
|---|---|---|
| S3 | Baseline: standard 15/16 in. holes (1/32 in. clearance). Swept 0, 0.125 and 0.656 in. as preregistered. | Drawings show no slot at the column 79 clip angle (A95). |
| S4 | Swept 0, 0.2, 0.3 (baseline), 0.45 and 0.6 as preregistered. Added: 0.1, 0.22, 0.24, 0.26, 0.28. | The 0.2 to 0.3 scan is where the screening model (digitized geometry) found its threshold. 0.1 is added because the drawn face angle puts the wedge threshold near tan 4.17 deg = 0.07. |
| S11 | The girder end position comes from the drawings (1.78 in. from the column 79 flange face at the girder centreline). Swept by moving column 79 0.4 in. toward and 0.4 in. away from the girder end. | 0.4 in. is the gap between the dimensioned and the scaled end position. The preregistered 0.25, 0.5 and 1.0 in. were placeholders for an unknown clearance. |
| S12 | Baseline from the drawings (0.25 in. west, 1.38 in. east). Swept 0.5, 1.0 and 3.0 in. on both sides, as preregistered. | A96. |
| Q12 | Side plates as drawn (baseline) and removed ('clear'), at friction 0.3 and 0. | Shows what the plates do. |
| A97 | Girder end stiffeners as drawn, as a sensitivity run. | NIST did not model them. |
| Combined | The "most favourable" run uses the Section 6 ends, with S11 at +0.4 in. and S7 at 700 C. Section 6's rule for repeating it applies. | |

### 9.4 Checks

- **Section 4 checks:** these apply.
- **Mesh:** baseline 1.8 in.; coarse 3.6 in. Both meshes keep at least four elements across every
  flange, because two elements across a flange gave 6 % low lateral-torsional buckling moments in
  verification. The Section 4 criterion is applied to the 3.6 and 1.8 in. pair. If it fails, the
  baseline is rerun at 0.9 in. and that pair decides; until then the result is reported as not
  mesh-converged.
- **Rate:** the baseline is rerun at half the heating rate. If T_E1, T_E2, T_E3 or T_E4 moves by more
  than 10 C (or 2 %), every priority-1 run is repeated at half rate, and the half-rate results become
  the reported ones.
- **Quasi-static:** criterion as in Section 4. Exceptions, such as transients after brittle connection
  failures, are reported, not waived.

### 9.5 Runs

- **Priority 1** (`phase1/run_shell.py --set p1`):
  - baseline;
  - friction 0, 0.1, 0.2, 0.22, 0.24, 0.26, 0.28;
  - Q12 clear at friction 0.3 and 0;
  - S11 -0.4 and +0.4 in.;
  - S7 700 C;
  - S8 heat-cool;
  - coarse mesh;
  - half rate;
  - end stiffeners as drawn.
- **Priority 2** (`--set p2`):
  - S4 0.45 and 0.6;
  - S1 22 and 30;
  - S3 0, 0.125 and 0.656 in.;
  - S5 flexible;
  - S6 released;
  - S7 400 and 500 C;
  - S9 EC3;
  - S10 -10 % and +10 %;
  - S12 0.5, 1.0 and 3.0 in.;
  - S13 0.15 and 0.35 in.;
  - S14 0.10 and 0.30 in.;
  - S15 0 and 0.6;
  - the combined run.

Compute (timing pilot, gravity phase only): 51,149 shells, time step 5.14e-6 s, 7.6 ms per step
on 4 threads. A 4.0 s run takes about 1.6 h; runs go two at a time with two threads each.
Priority-2 runs use the 3.6 in. mesh if the mesh check (9.4) passes. A priority-2 run is then
repeated on the 1.8 in. mesh if either of these holds:
- its walk-off result (E2, E2r or E2s, yes or no) differs from the coarse baseline;
- any event temperature is more than 25 C from the coarse baseline.
Otherwise all priority-2 runs use the 1.8 in. mesh.

### 9.6 Outcome

The Section 3 classes are applied to the detailed model: the baseline, the priority-1 and priority-2
one-at-a-time runs, and the combined run. The gate (Section 8) needs this class and, if it differs
from NIST, the modelling choice that explains the difference.

## Change log

| Date | Change | Reason |
|------|--------|--------|
| 2026-10-21 | Created | |
| 2026-10-22 | Added S15 (beam-to-slab friction after stud failure). No run had been made. | In a plan-view model the beams are braced laterally only by studs and, after they fail, by friction against the slab; that bracing sets how hard the beams can push the girder, so it needs its own range. |
| 2026-10-22 | No criterion or range changed. Recorded a geometry correction: the first baseline run (beam-element model) placed the girder bearing faces at columns 79 and 44 square to the girder. NIST Fig. 2-20 Section A-A and Fig. 8-21 show the girder meeting column 79 at an angle, so the faces were re-oriented to the building grid (assumption A48) and friction was added on them (A49, same value as S4). | The first run showed the girder end sliding sideways at about 368 °C beam temperature; investigating it exposed the square-face simplification. The superseded run's result is reported alongside the corrected one, and 'square' is kept as a diagnostic run, not as a baseline. |
| 2026-10-22 | No criterion or range changed. Recorded the follow-up runs made after the primary set: a finer friction scan inside the S4 range (0.22 to 0.28), the digitized girder skew at +/-2 deg, mesh checks of the walk-off runs, every other parameter rerun at friction 0.20, half-rate reruns, a NIST-like idealization (square face, no friction), and the most-favourable combination rebuilt under the Section 6 rule. | The primary set showed that friction alone flips the outcome and that several preregistered 'favourable' ends delayed walk-off; Section 6 requires the combined run to be repeated with the ends that actually favour it. All follow-up runs are reported (`results/phase1/summary.md`). |
| 2026-10-23 | Added Section 9 (detailed shell model): drawings geometry, events E2r and E2s, the parameter changes forced by the drawings (S3 baseline, S11 range, S12 baseline), friction points 0.1 to 0.28, Q12 and stiffener runs, mesh and rate rules, run order. No thermal run of the detailed model existed. Recorded that the drawings show the screening model's geometry (girder skew, column 79 face orientation, beam positions) was wrong; the screening runs with that geometry are kept as superseded. | Drawings obtained (Q12 to Q17). |
| 2026-10-25 | No criterion or range changed. Applied the Section 9.4 rate rule: the half-rate baseline moved T_E3 from 544 C to 133 C (the column 44 bolts failed before the column 79 bolts), so every priority-1 run is repeated at half rate (`--set p1_half`) and those become the reported results; the full-rate runs are kept and reported as such. Two additions, both decided before either was run: (1) the 0.9 in. mesh run of Section 9.4 is made at half rate, because the mesh check has to describe the results that are reported; (2) a quarter-rate baseline is added as a diagnostic. It is reported and replaces nothing. | One halving moved an event by 411 C, so 9.4 as written does not show that half rate is converged. The likely cause is the mass-proportional damping, which drags on the slow thermal sliding in proportion to the heating rate. |
| 2026-10-25 | No criterion or range changed. The priority-2 runs (Section 9.5) are made at half rate. No priority-2 run had been made. | Section 9.4 names only priority 1, but each priority-2 run is read against the baseline, and the reported baseline is now the half-rate one. |
