# WTC 7 staged re-analysis: Phase 1 write-up

Revision 3, 2026-11-02 (draft). Status: the detailed model's runs are reported; the Phase 1 gate has
**not** passed (`docs/phase1_gate.md`). Nothing here is a finding about the collapse. Revision 1
(2026-10-22) reported a screening result that rested on wrong geometry; Section 2 explains what
changed. Revision 2 (2026-10-23) described the detailed model before its runs.

## 1. What was built

**Sources.**
- NIST NCSTAR 1-9, 1-9A, 1A and 1-3D, the 2009 and 2012 errata, and the WTC 7 FAQ
  All downloaded sources are archived in the repository with checksums (`sources/README.md`).
- Since revision 1: the Frankel shop and erection drawings and the Cantor structural drawings for the
  girder, column 79, column 44 and floors 12 and 13. These are NIST FOIA releases mirrored on
  archive.org (`sources/drawings/`, with the scans in `raw/`).
- The girder's own piece drawing (Frankel 2001) was not in the release and is still missing.

**Pre-registration.** Outcome classes, events, checks and every sweep range were hashed before the
first run (`docs/preregistration.md`, hashes in `docs/compute_log.md`). Section 9, for the detailed
model, was added and hashed before any thermal run of that model. Every later addition is a change-log
row, hashed before the runs it describes; none changed a criterion or a range.

**Inputs.** Every input has a value, range and source in `docs/assumptions.md`. Values read from the
drawings are A90 to A99; questions the documents leave open are in `docs/open_questions.md`.

**Models.**
- Hand calculations: `results/phase1/hand_calcs.md`.
- A plan-view beam-element screening model: `phase1/plan_model.py`, solver `wtc7/fe2d.py`.
- A detailed shell model of the northeast floor framing in the style of NIST's LS-DYNA model (§8.8):
  `phase1/shell_model.py`.
- The shell solver was written for this study (`wtc7/xfe`, Section 4), because the planned open-source
  explicit code, OpenRadioss, was withdrawn by its owner in October 2026.

## 2. What the drawings changed

| Item | Revision 1 (digitized from NCSTAR figures) | Drawings |
|---|---|---|
| Girder skew to the grid | 14.6 deg | 16.5 deg (3 9/16 in 12, E12/13) |
| Column 79 face the girder bears on | On the grid: 14.6 deg to the girder | Column rotated 12.3 deg: face 4.17 deg off square to the girder (7/8 in 12, 9114 and 1091) |
| Column 79 side cover plates (Q12) | Not modelled | 2 PL 26 x 2 project about 1.8 in. past the flange face; girder end at the mouth of that recess; 4.15 in. between the west flange tip and the west plate inside it |
| Beam stations from column 44 | 45.6 to 466.8 in. | 50.1 to 512.8 in.; southmost beam 22 in. from the girder end |
| Beam spans | 624 in. | 608 to 644 in. (east wall skewed) |
| Clip-angle holes at column 79 | Short slots | Standard round holes |
| Girder end stiffeners | Not known | PL 5 1/2 x 3/4 x 1'-6 both sides; NIST did not model them |
| Girder studs, floor 13 | None (NIST); 22 or 30 swept | None shown on E12/13 or S-8 |

The most consequential change is the face angle at column 79. With the face on the grid, the girder's
thrust against column 79 pushed its end sideways with about 0.26 of the thrust. With the drawn
4.17 deg it is 0.07. Revision 1's conclusion was that friction at the column 79 face decides walk-off,
switching between 0.22 and 0.24. That came from the wrong angle. Those runs are kept, marked as
superseded (`results/phase1/summary.md`).

## 3. Screening model with the drawings geometry

Twelve runs, ramped to 800 C beam temperature (`results/phase1/summary_drawings.md`,
`results/phase1/plots/drawings_col79.png`). The early sequence is the same in every run:
- the column 79 erection bolts all fail at 122 C (E1);
- the expanding girder then pushes its end about 1.5 in. toward column 79, into the side-plate recess,
  until it bears on the flange face;
- the column 44 bolts fail at 260 to 416 C (E3).

| Case | Largest westward movement at column 79 | Walk-off (6.25 in.) |
|---|---|---|
| Friction 0.3 | 2.2 in. (friction holds) | none to 800 C |
| Friction 0.2 | 3.4 in. (friction holds) | none |
| Friction 0, 0.05 or 0.1 | 4.0 in. (west side plate stops it) | none |
| Friction 0.3 or 0.2, side plates removed | 2.2 or 3.4 in. | none |
| Friction 0, side plates removed | 10.6 in. | 625 C |
| Column 79 0.4 in. closer or further; heating then cooling | 1.6 to 4.0 in. | none |

So in the screening model the girder walks off only if the side plates are removed **and** the girder
end slides on its seat and the column face without friction. This model has no vertical direction, so
it cannot show the girder rocking or twisting off its seat, which is how NIST's partial-floor model
lost it. That is what the detailed model is for.

## 4. Detailed shell model

**Model** (`phase1/shell_model.py`; assumptions A70 to A99; preregistration Section 9):
- The W33x130 girder and the five floor beams are four-node shells at NIST's 1.8 in. size.
- The slab is one layer of 7.5 in. shells with separate tension and compression curves (NIST's
  approach, NCSTAR 1-9A §2.3.1).
- Studs and all erection and fin bolts are breakable springs with NIST's temperature-dependent
  strength.
- Seats, the column 79 flange face, its side plates and their ends, the column 44 pocket and the
  exterior columns are rigid planes with friction. The seat edges also bear on the girder flange.
- Gravity is ramped over 1 s, then the beams and girder are heated uniformly at NIST's rate to
  600/500 C and held for 1.4 s. The reported runs heat at half that rate (Section 4.2).
- The model has 51,149 shells. A half-rate run took 3.7 to 10 h on the laptop, two threads each,
  two runs at a time (`docs/compute_log.md`).

**Solver** (`wtc7/xfe`): Belytschko-Lin-Tsay shells with temperature-dependent plasticity (the same
NIST and EN 1993-1-2 curves as the screening model), penalty contact with Coulomb friction, and
central-difference time stepping. It is checked against closed-form results (`tests/test_xfe.py`,
22 tests):
- free thermal expansion within 0.4 %;
- restrained force exact while elastic;
- Euler buckling within 2 %;
- friction stick and slip thresholds;
- the wedge on a skewed face;
- bolt failure at the temperature-reduced capacity.

For lateral-torsional buckling it is within 1.6 % of CalculiX 2.20 (`results/phase1/shell/verification.md`).

**Gravity check.** Reactions balance the 215.6 kip floor load to 0.2 %. Each beam end rotates on the
toe of its seat and pries against the erection bolts and the slab. This puts about twice the simple
end shear into the seats, capped by the cracked slab's local strength.


### 4.1 Runs

65 runs, all in `results/phase1/shell/summary.md` (temperatures there and below are floor-beam
temperatures):
- **Reported set, half rate (41 runs):** the baseline (`check_rate_half`), the 15 other priority-1
  runs, the 23 priority-2 one-at-a-time runs and the two combined runs (Section 4.5).
- **Diagnostics (3 runs):** a quarter-rate baseline, and at half rate the 0.9 in. mesh baseline and
  `favourable_dump`, a repeat of the combined run with state dumps. They are reported and replace
  nothing.
- **NIST replica (5 runs, half rate, Section 5):** `nist_replica` and the four restore runs, for gate
  item 5. Diagnostics, not part of the reported set.
- **Full rate (16 runs):** the priority-1 set at NIST's rate. The rate check (4.2) moved them out of
  the reported set; they are kept and reported as full-rate runs.

### 4.2 Checks

| Check (preregistration Sections 4 and 9.4) | Result | Status |
|---|---|---|
| Closed-form tests (expansion, restraint, Euler, friction, bolt failure) and the CalculiX buckling comparison | Section 4 above | pass |
| Rate | Full to half rate moved T_E3 from 544 to 133 C, so the half-rate runs became the reported set (change log 2026-10-25). Half against quarter rate: every event within 3 C (E1 154.0 and 153.7 C, E3 132.8 and 131.4 C); lateral movement at column 79 1.467 and 1.471 in. | pass, at half rate |
| Mesh, 3.6 against 1.8 in. | T_E1 143.9 against 154.0 C (10.2 C); fails, so the 0.9 in. run decides | fail |
| Mesh, 0.9 against 1.8 in. | T_E1 160.2 against 154.0 C (passes). No E2 in either, so the lateral movement at column 79 decides: 1.501 against 1.467 in. at the end of the run, 2.3 % against the 2 % limit | **fail** |
| Quasi-static: kinetic energy below 5 % of internal energy throughout | Every run exceeds it during the gravity ramp (0.39 to 0.50, before any heating). During heating 31 of the 44 reported and diagnostic runs exceed it at some step: largest 0.21 in `S7_peak700_r0.5` when its girder buckles at 663 C, otherwise at most 0.076. In the fall after walk-off, 0.07 to 0.09 | **fail** |

**The mesh failure cannot change an outcome.** The baseline girder end moves 1.5 in. sideways on
either mesh; walk-off needs 6.25 in. The 0.034 in. difference is 0.5 % of that distance, and the
event temperatures of the two meshes agree within 6.2 C. The 0.9 in. run's hourglass energy reached
0.22 of internal energy (0.09 at 1.8 in.), so the finer mesh is not clearly the more accurate one.
The criterion was set on the baseline only; no other run was checked on the 0.9 in. mesh.

**The quasi-static failure** is reported, not waived (Section 9.4). The large ratios fall in the
gravity ramp, before any temperature change. During heating the excursions are short, and the
evidence that the reported results are not rate effects is the half-against-quarter-rate agreement
above, not the energy ratio.

**Why the rate moved E3.** The two girder-end bolt groups fail within about 20 C of each other, and
whichever group fails first takes the thrust off the other. Up to about 100 C both ends move about
0.25 in.; then the column 44 end slips to about 0.47 in. at every rate. At full rate the column 79
seat bolts fail next (128 C), the column 79 end takes the rest of the expansion, and the column 44 end
stops 0.03 to 0.05 in. short of its failure movement; its bolts last to 544 C. At half and quarter
rate the column 79 seat bolts hold to 146 to 147 C, the column 44 end reaches its failure movement,
and E3 comes at 131 to 133 C. The full-rate run is still carrying the gravity transient when this
happens: heating starts 0.1 s after the gravity ramp ends, and at 95 to 120 C kinetic energy is about
5 to 6 % of internal energy, against 1 to 2 % at half rate from 110 C. The damping explanation recorded in
the change log (2026-10-25) is not supported: the damping work at 130 C is about the same at full and
half rate (8.1 and 8.1; 6.7 at quarter rate). Which group fails first also flips with the mesh (the
3.6 in. mesh at half rate fails column 79 first) and with several swept inputs (4.4); no walk-off
result depends on it.

### 4.3 Baseline

At half rate, with the drawn geometry and NIST's other inputs:
- first stud failure 101 C;
- all four column 44 bolts fail (E3) at 133 C;
- the column 79 seat bolts at 147 C, all four column 79 bolts (E1) at 154 C;
- first fin-plate bolt 597 C;
- no beam buckles (E4) and the girder does not buckle, through 600 C and the 1.4 s hold.

The girder end at column 79 moves 1.91 in. toward the column, closing the gap to the flange face
(1.36 in. at the nearest corner, 1.78 in. at the centreline), and 1.47 in. sideways to the west. It
never touches a side plate. With the face 4.17 deg off square, the sideways push is about 0.07 of the
thrust, well below the friction of 0.3. No walk-off.

### 4.4 One parameter at a time

**Friction (S4 and the added scan).** Largest movement of the girder end at column 79 toward the west:

| Friction | 0 | 0.1 | 0.2 | 0.22 | 0.24 | 0.26 | 0.28 | 0.3 (baseline) | 0.45 | 0.6 |
|---|---|---|---|---|---|---|---|---|---|---|
| West movement (in.) | 3.98 | 2.11 | 1.72 | 1.67 | 1.63 | 1.57 | 1.52 | 1.47 | 1.10 | 0.78 |

The movement changes smoothly with friction; the threshold between 0.22 and 0.24 that revision 1
reported does not exist with the drawn face. At friction 0 the girder end is stopped by the west side
plate (bearing from 489 C).

**Other priority-1 runs.**
- Side plates removed (Q12): at friction 0.3 nothing changes (1.47 in.; the plates are never touched).
  At friction 0 the end moves 5.06 in., against 3.98 in. with the plates, and stays on the seat.
- Column 79 moved 0.4 in. toward or away from the girder end (S11): 0.98 and 1.97 in.
- Peak 700 C (S7): the girder buckles (bow over L/50, a monitored event, not a preregistered one) at
  659 C and bears on the west plate at 663 C, but its end moves no more than in the baseline (1.47 in.).
- Heating then cooling (S8): 1.82 in. End stiffeners as drawn (A97): 1.60 in.

**Priority 2.** No one-at-a-time run reaches E2, E2r or E2s.

| Parameter | Values: west movement (in.) | Notes |
|---|---|---|
| S1 girder studs | 22: 1.24; 30: 1.21 | |
| S3 clip-angle slot | 0: 1.46; 0.125: 0.98; 0.656: 0.95 | standard holes (baseline) 1.47 |
| S4 friction | 0.45: 1.10; 0.6: 0.78 | |
| S5 column 79 restraint | flexible: 1.79 | the column 44 bolts never all fail |
| S6 slab edges | released: 1.47 | |
| S7 peak | 400 C: 1.46; 500 C: 1.47 | |
| S9 steel curves | EN 1993-1-2: 1.44 | a beam buckles (E4) at 594 C |
| S10 yield | -10 %: 1.46; +10 %: 1.48 | |
| S12 column 44 gap | 0.5: 1.42; 1.0: 1.26; 3.0: 1.22 | drawn (baseline) 1.47 |
| S13 bolt deformation at failure | 0.15: 1.21; 0.35: 0.93 | |
| S14 stud slip at failure | 0.10: 1.43; 0.30: 1.18 | |
| S15 beam-slab friction | 0: 1.50; 0.6: 1.46 | at 0 a beam buckles (E4) at 284 C |

**Which end's bolts fail first.** In the baseline the column 44 bolts go first (133 C). In nine
one-at-a-time runs the column 79 bolts go first and the column 44 bolts hold to 461 to 578 C:
friction 0 and 0.1, both stud counts, both slots, both S13 values and S14 0.30. Neither order leads to
walk-off.

### 4.5 The combined runs

**`favourable`**, the preregistered combination (Section 6 ends, column 79 0.4 in. further away, peak
700 C):
- first stud 85 C, column 79 seat bolts 95 C, E1 185 C;
- first beam buckles (E4) 444 C, all studs gone 526 C, E3 581 C, first fin bolt 609 C;
- the ramp reaches 700 C at 4.62 s and is held; the girder end bears on the west side plate at 4.63 s
  and the girder buckles at 4.71 s;
- the girder end twists past atan(bf/d) (E2r) at 5.018 s and moves 6.25 in. west (E2) at 5.125 s,
  both at 700 C, 0.40 and 0.51 s into the hold;
- the solver diverged at 5.133 s, 0.008 s after E2. Kinetic energy was at most 0.074 of internal
  energy up to that point.

Section 3 makes a run INCOMPLETE only if it stops before E2, so E2 and E2r stand.

**`favourable_dump`** (diagnostic, change log 2026-10-31) repeats it unchanged. The same sequence
comes within 5 C and 0.07 s (E2r 5.090 s, E2 5.185 s); then the girder end drops 2 in. (E2s) at
5.303 s, and the run stops as designed 0.3 s later, with the end 22.6 in. down and 17.5 in. to the
west; the twist peaked at 64 deg. There is no divergence. The walk-off is reproducible and the original divergence
came after it. The small differences between the two runs come from the order of floating-point sums
across threads, which is not fixed.

**`favourable_s6`**, the Section 6 repeat (change log 2026-10-31): the four ends the sweeps showed
were wrong are replaced by the values that gave the most movement (standard holes, friction 0.1, the
drawn column 44 gap, bolt deformation 0.25 in.):
- E1 162 C, first beam buckles 617 C, E3 621 C, the end bears on the west plate at 631 C;
- the girder does not buckle;
- largest west movement 2.83 in.; no walk-off to 700 C.

So the four inputs that each moved the end further on their own, together, prevent the girder
buckling that carried the original combination off its seat. The runs do not show which of the four
does it.

## 5. Agreement and disagreement with NIST

**Outcome class: CONDITIONAL** (preregistration Section 3). No run walks off under NIST's 600 C
ramp. One run walks off: the preregistered combined run, at 700 C during the hold. Section 3 asks
for the parameters whose change moves the result across the 700 C line; no single parameter does,
so that list is empty and the condition is the combination itself. The Section 6 repeat of the
combination does not walk off. NIST's partial-floor model lost the girder at column 79 by rocking
after the floor beams buckled (§8.8); this model, with the same inputs, does not.

| Quantity | NIST (Table 8-2, §8.8) | Detailed baseline, half rate | NIST replica, half rate |
|---|---|---|---|
| First stud failure | 103 C | 101 C | 101 C |
| Column 79 seat bolts | 154 C | 147 C | 96 C |
| E1, all column 79 bolts | 194 C | 154 C | 131 C |
| E3, all column 44 bolts | 476 C | 133 C (544 C at full rate) | 524 C |
| E4, first beam buckles | 436 C | none to 600 C | none to 670 C |
| Girder off its seat at column 79 | after all beams buckle, by 600 C, by rocking | none; only the combined run, at 700 C | E2 511 C, by sliding along the face |

The connection events up to E1 agree within 40 C. The model departs from NIST at beam buckling: in
the baseline no beam buckles at all.

**Why it differs: not found** (gate item 5, decision 2026-11-02). The preregistration requires the
modelling choice that explains the difference. The one-at-a-time sweeps ruled out friction 0, side
plates removed, both together (to 600 C), end stiffeners, and the column 79 position within ±0.4 in.,
so NIST's idealizations were tested together and then taken back one at a time (change log
2026-11-01).

**The NIST replica walks off.** `nist_replica` applies NIST's column 79 idealizations together on the
drawn framing: the face 14.6 deg off square to the girder (digitized), 0.5 in. end clearance, no side
plates, friction 0 and the short slot, at half rate to 700 C.
- E1 at 131 C. The girder end then bears on the angled face and slides west along it: 2.9 in. at
  300 C, 4.6 in. at 400 C, 6.25 in. (E2) at 511 C. E3 follows at 524 C.
- It keeps sliding until the end drops 2 in. (E2s) at 612 C.
- No beam buckles. The end twists less than 4 deg up to E2, and E2r does not occur.
- Kinetic energy is at most 0.059 of internal energy before E2 (above 0.05 in 5 of 1,018 steps).

By the rule set before the run (E2 or E2r by 700 C) it reproduces NIST, and within NIST's 600 C ramp.

**Taking the idealizations back one at a time.** Each restore run changes one thing on the replica
back to the drawings:

| Run | Changed back | West movement at 600 C (in.) | Result |
|---|---|---|---|
| `nist_replica` | nothing | 7.08 | E2 511 C (sliding), E2s 612 C |
| `nist_holes` | standard holes | 6.84 | E2 512 C (sliding), E2s 615 C |
| `nist_face_drawn` | face angle and position | 5.04 | E2 655 C, E2s 667 C |
| `nist_mu0.3` | friction 0.3 | 0.36 | girder buckles 633 C; E2r 650 C, E2 655 C, E2s 672 C |
| `nist_face_plates` | face angle and position, with the side plates | 3.97 | bears on the west plate at 488 C; no walk-off to 700 C |

- **The holes do nothing**: the replica's sequence repeats within 4 C.
- **The face angle sets when, not whether.** With the drawn face the end slides west about 1 in. per
  100 C, as in `Q12_clear_mu0_r0.5`, against about 1.6 in. per 100 C at 14.6 deg (300 to 500 C). It
  reaches 5.57 in. at 650 C and then runs off the seat within about 5 C. `Q12_clear_mu0_r0.5` stopped
  at 5.06 in. only because its ramp ended at 600 C.
- **Friction stops the sliding but not a twist-off.** At 0.3 the end stays within 0.4 in. to 620 C.
  Then the girder buckles sideways (bow 4.5 in. at 600 C, 13 in. at 640 C), twists its end past
  atan(bf/d) at 650 C and carries it off. This passage is dynamic: kinetic energy is 0.18 to 0.35 of
  internal energy from 630 C.
- **The side plates hold it.** With the drawn face and the plates, still at friction 0, the end
  slides to 3.98 in., bears on the west plate from 488 C, and stays there through 700 C and the hold,
  while the girder buckles (bow 13.4 in. at 700 C, 19.6 in. in the hold). This is the same 3.98 in.
  as the drawn baseline at friction 0 (4.4).

In these runs the side plates at column 79, which NIST's model did not have, separate walk-off from
no walk-off. Without them, the model walks off by 700 C whichever single drawn feature is put back;
with them, no run walks off under the 600 C ramp. The face angle decides whether the plate-less
walk-off falls inside NIST's 600 C ramp (14.6 deg) or after it (the drawn 4.17 deg). The plates and
the face cannot be separated: at 14.6 deg the drawn plates cut through the girder end.

This is not accepted as the explanation gate item 5 asks for. The replica reaches NIST's outcome by a
different mechanism (sliding along the face, with no beam buckling), so it does not show why this
model departs from NIST's partial-floor result, in which the girder rocked off after the beams
buckled. The explanation is recorded as not found.

Two further limits. The drawn framing without plates at friction 0.3 was run only to 600 C
(`Q12_clear`, 1.47 in.), so whether its girder buckles off between 600 and 700 C, as in `nist_mu0.3`,
is not tested. And the walk-offs after 600 C come in or after a dynamic phase (kinetic energy up to
0.13 of internal energy in `nist_face_drawn` at 660 C, 0.33 in `nist_mu0.3`), where the quasi-static
check fails (4.2).

**Beam buckling is a separate difference.** In the baseline the floor beams' axial compression peaks
at 117 kip and is 73 kip at 600 C, well below a W24x55's squash load at that temperature (about
380 kip with the EN 1993-1-2 strength reduction). The expanding beams push the girder sideways
instead; it bows 4.3 in. between its ends. Its top flange slides under the slab without friction, as
NIST assumed (§11.2.3, A44), so what stiffened NIST's girder against this is not yet found. The
replica walks off without any beam buckling, so walk-off in this model does not need it. NIST's
mechanism (rocking off after the beams buckle) is therefore not reproduced, and this difference is
reported as unexplained.

## 6. Guessed inputs the conclusion depends on

- **"No walk-off under the baseline"** holds at every swept value, including the inputs with no
  source: friction (A42, a proxy), bolt deformation at failure (A31), stud slip (A32), beam-slab
  friction (A43), the column 44 gaps and the column 79 position.
- **The one walk-off** depends on several unsourced values at once: friction 0.2, the long slot,
  a 3 in. column 44 gap, 0.15 in. bolt deformation and 0.10 in. stud slip, with the column 79 position
  and the peak at the ends of their ranges. Changing four of them to the values that each gave more
  movement removes it.
- **The face angle at column 79** (4.17 deg, A93) is read from a legible bevel on two sheets (9114,
  1091). It sets how fast the girder end slides when nothing else holds it: with NIST's digitized
  14.6 deg about 1.7 times faster, enough to bring a plate-less walk-off inside the 600 C ramp
  (Section 5).
- **The side plates at column 79** (drawn, absent from NIST's model) keep the girder on its seat
  under the 600 C ramp in every run (Section 5). The one run that walks off with them, the combined
  run, does so at 700 C after bearing on the west plate. Their position is drawn, not guessed; the
  fit-up limit in Section 7 applies.
- **Which end's bolts fail first** depends on the heating rate, the mesh and A31 (4.2, 4.4); no
  walk-off result depends on it.

## 7. What this cannot show

- The real fire. Phase 1 uses NIST's uniform ramp, not its computed temperature histories (Phase 2).
- Fit-up. The drawn girder end is at the mouth of the side-plate recess with about 0.4 in. to spare.
  As-built positions could differ by that much; S11 sweeps ±0.4 in. and neither end walks off.
- Seat and plate flexibility: the seats and top plates are rigid planes and springs, not meshed plates.
- Camber, the W12x26 framing into the girder from the west, and the slab's thermal response. None is
  modelled.
- Interactions. The sweeps change one input at a time; only two combinations were run, and they
  disagree. The space between them is not explored.
- Numerical limits. The mesh and quasi-static checks fail (4.2). Runs with two or more threads are not
  bit-for-bit repeatable: the combined run's events moved by up to 0.07 s between two identical runs.
- The girder-buckling event (bow over L/50) is monitored, not preregistered.

## 8. Next

1. Gate item 5 is open: the NIST-replica run and the four restore runs (change log 2026-11-01) did
   not find the modelling choice that explains the difference from NIST (Section 5). The beam-buckling
   difference is the remaining lead.
2. A decision on the two failed checks (`docs/phase1_gate.md`). The gate stays closed until then.
3. Phase 2 does not start before the gate passes.
