# WTC 7 staged re-analysis: Phase 1 write-up

Revision 2, 2026-10-23. Status: Phase 1 in progress; the Phase 1 gate has **not** passed. Nothing
here is a finding about the collapse. Revision 1 (2026-10-22) reported a screening result that rested
on wrong geometry; Section 2 explains what changed.

## 1. What was built

**Sources.**
- NIST NCSTAR 1-9, 1-9A, 1A and 1-3D, the 2009 and 2012 errata, and the WTC 7 FAQ
  (`scripts/fetch_sources.sh`).
- Since revision 1: the Frankel shop and erection drawings and the Cantor structural drawings for the
  girder, column 79, column 44 and floors 12 and 13. These are NIST FOIA releases mirrored on
  archive.org (`sources/drawings/`, re-downloaded and checksummed by `scripts/fetch_drawings.sh`).
- The girder's own piece drawing (Frankel 2001) was not in the release and is still missing.

**Pre-registration.** Outcome classes, events, checks and every sweep range were hashed before the
first run (`docs/preregistration.md`, hashes in `docs/compute_log.md`). Section 9, for the detailed
model, was added and hashed before any thermal run of that model.

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
  600/500 C and held for 1.4 s.
- The model has 51,149 shells; a 4 s run takes about 1.6 h on four cores.

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

**Results.** *Pending: the priority-1 runs (baseline, friction 0 to 0.3, Q12, S11, S7, S8, mesh and
rate checks) are running; `results/phase1/shell/summary.md` will hold them.*

## 5. Agreement and disagreement with NIST

*Pending the detailed results.*

## 6. Guessed inputs the conclusion depends on

*Pending the detailed results.*

## 7. What this cannot show

- The real fire. Phase 1 uses NIST's uniform ramp, not its computed temperature histories (Phase 2).
- Fit-up. The drawn girder end is at the mouth of the side-plate recess with about 0.4 in. to spare.
  As-built positions could differ by that much (S11 sweeps ±0.4 in.).
- Seat and plate flexibility: the seats and top plates are rigid planes and springs, not meshed plates.
- Camber, the W12x26 framing into the girder from the west, and the slab's thermal response. None is
  modelled.

## 8. Next

*Pending the detailed results.*
