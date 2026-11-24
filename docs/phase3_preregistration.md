# Pre-registration: Phase 3 (conditional), column 79 failure and global collapse

Draft, 2026-11-02. Written before any Phase 3 calculation, hand or finite-element. Its SHA-256 is
recorded in `docs/compute_log.md` before the first Phase 3 calculation; later edits follow the
same rule as `docs/preregistration.md`: every edit is listed in the change log at the bottom with
its reason, and no criterion or range changes after results for it exist.

Sources are cited by NCSTAR report and section. The citations in this file come from
`docs/phase3_sources/nist_facts.md`; those not yet checked against the PDF are marked "(sheet)".

## 1. Question and status

**Question.** If column 79 loses its support over part of its height, does WTC 7, as drawn and
under NIST's loads, collapse completely?

**Conditional, and out of order.** The study's phases are gated (`docs/preregistration.md`
Section 8). Phase 1 has not passed its gate and Phase 2 has not started. Phase 3 is run now on the
condition that column 79 fails, without asking how. Its result does not depend on Phase 1 or
Phase 2 and changes neither. The change log of `docs/preregistration.md` records the decision
(2026-11-02).

**What Phase 3 can and cannot show.**
- It can show whether column 79's failure is sufficient, in this model, for total collapse; and if
  so, how much failure is needed and how the collapse spreads.
- It cannot show why column 79 failed. Whether fire did it is Phase 1 and Phase 2. No other cause is
  modelled; a result that column 79's failure does not lead to total collapse would contradict
  NIST's sequence, not establish an alternative.

## 2. Events

All displacements are vertical, at 20 C, measured from the state at the end of the gravity step.
h = 153 in. (typical storey, 12 ft 9 in.; NCSTAR 1-9 Ch. 2, sheet).

| ID | Event | Definition |
|---|---|---|
| G1 | Column 79 fails | Removal runs: at the removal (imposed). Damage-state runs: the top of column 79 descends by more than h |
| G2 | East penthouse falls | The mean vertical displacement of the east penthouse roof framing exceeds h |
| G3 | First neighbour fails | The top of column 80 or column 81 descends by more than h |
| G4 | Interior progression complete | The tops of all 24 interior columns (58 to 81) have descended by more than h |
| G5 | Exterior descent | The mean vertical displacement of the north-face roofline (roof-level nodes of the north perimeter columns) exceeds h |

"The top of a column" is its highest node still connected to the column below. A column whose
splice or segment fails counts by the descent of the part that remains above the failure.

## 3. Outcome classes

Each run is classified at the end of its run time (Section 6):
- **TOTAL** if G4 and G5 both occur.
- **PARTIAL** if G2 or G3 occurs but not both G4 and G5.
- **LOCAL** if neither G2 nor G3 occurs: the failure stays at column 79 and the floor framing it
  carried.
- **INCOMPLETE** if the run stops for numerical reasons before TOTAL and before its end time.
  An incomplete run is never reported as PARTIAL or LOCAL.

The Phase 3 result:
- **SUFFICIENT** (agrees with NIST) if the baseline damage-state run (D0) is TOTAL.
- **NOT SUFFICIENT** (contradicts NIST) if no run in Section 5 is TOTAL, every parameter inside its
  range.
- **CONDITIONAL** in every other case. The report then lists each case and parameter whose change
  moves a run across the TOTAL line, with the value at which it flips.

The removal sweep (Section 5.2) is reported as the smallest removed length that gives TOTAL, or
"none up to nine storeys".

## 4. NIST reference values (compared with, not tuned to)

| Quantity | NIST | Source |
|---|---|---|
| Column 79 gravity load above floor 8 | 7,525 kip | NCSTAR 1-9 §11.3.1 (A60) |
| Damage state when column 79 buckled | unsupported E-W and to the south between floors 5 and 14; north restraint at floors 8 to 12 and 14 | 1-9 §12.4.4; 9A Fig. 4-17 (sheet) |
| Order after column 79 | 80 at -0.6 s, 81 at 0.0 s, core columns from 76 westward 3.5 to 6.1 s, exterior columns 5.5 to 7.4 s | 1-9 Table 12-2 (sheet) |
| Classic case (no fire, no debris): column 79 removed between floors 11 and 13 | total collapse; floors around 79 collapse to the roof, kink at the east penthouse at 0 s | 1-9 §12.4.7 (checked) |
| Without column 79's buckling | floor failures alone "would not have been sufficient" (no analysis cited) | 1A §3.4.6 (checked) |

Observations, for comparison (Section 7), not for classification: the east penthouse starts down
at 0 s and is below the roofline at 2.0 s; the north-face roofline starts down at 6.9 s; the
west penthouse is below the roofline at 9.3 s (1-9 Table 5-3, sheet); the roofline then falls at
about g for about 2.25 s, from 1.75 to 4.0 s after it starts (1-9 §12.5.3, checked;
`results/phase1/hand_calcs.md` Section 8).

## 5. Cases

### 5.1 Baseline structure and loads

- **Structure as drawn.** Member sizes, column schedule, splices, transfer trusses and girders at
  floors 5 to 7, and connection types are read from the Cantor structural drawings (FOIA 11-209)
  and the Frankel erection drawings (FOIA 12-009). Where the drawings are missing or illegible,
  NIST's description is used; where both are silent, an assumption is recorded (A100 onward) with a
  sweep range, before the first run.
- **Loads.** Dead load plus superimposed dead load plus 25 % of the design live load, unfactored,
  no wind, as in all of NIST's analyses (1-9 §11.2.7, §12.3.2, sheet). Per-floor values from NIST's
  design loading schedule (1-9 Fig. 11-17).
- **Temperature.** 20 C everywhere. NIST's global runs included heated floors; that is Phase 2.
  Ambient steel is stronger than heated steel, so this choice favours arrest.
- **Debris damage from WTC 1.** None in the baseline. NIST reports collapse with and without it
  (1-9 §14.2, sheet).

### 5.2 Triggers

- **D0, NIST's damage state (baseline).** After the gravity step, the floor framing in the bays
  that frame into column 79 on floors 6 to 13 is released from its connections and falls; column 79
  is then unbraced from floor 5 to floor 14 (nine storeys), with an initial bow of L/1000 in the
  east direction. North restraint is kept at floors 8 to 12 by the girders to column 44 still on
  their seats, as NIST describes. Column 79 is not removed; whether it buckles is a result.
- **R1 to R9, removal sweep.** Column 79 is removed over N storeys, N = 1 to 9, from floor 14 - N
  to floor 14; all floors intact.
- **RC, NIST's classic case.** Column 79 removed between floors 11 and 13; all floors intact.

Removals take a time t_r, linear in force, equal to one tenth of the first vertical-mode period of
the structure above the removed segment, computed before the first removal run. NIST does not
state its removal time (1-9 §12.4.7, sheet).

### 5.3 Parameter sweeps (one at a time, on D0 and RC)

| ID | Parameter | Baseline | Range |
|---|---|---|---|
| T1 | Live load fraction | 0.25 | 0; 0.5 |
| T2 | Shear and seated connection capacities | as calculated | x 0.75; x 1.25 |
| T3 | Column splice tension capacity | as drawn | x 0.5 |
| T4 | Slab tensile and membrane capacity | as calculated | x 0.5; x 2 |
| T5 | Steel yield strength | nominal | -10 %; +10 % |
| T6 | Viscous damping | 0 | 2 % of critical at the first mode |
| T7 | Column 79 initial bow (D0 only) | L/1000 | L/500 |
| T8 | Debris damage from WTC 1 | none | NIST's severed columns (the larger of the two counts NIST gives) |

Then two combined runs on D0: every parameter at the end of its range that the one-at-a-time runs
show moves toward arrest ("most favourable to arrest"), and every one at the end that moves toward
collapse. Where a parameter moves nothing, its baseline value is kept. This rule is fixed now; the
directions come from the runs.

## 6. Run length

Each run continues to 30 s after the trigger, or to TOTAL plus 2 s, whichever comes first. NIST's
best-estimate run reached the north-face descent about 7.6 s after column 79 buckled, and its run
without debris damage about 11 s after (1-9 Table 12-2, sheet); in the classic case column 78
buckled last, 10 to 15 s after the removal (1-9 §12.4.7 gives 9.5 s in collapse time and 19.3 s in
calculation time, which do not agree with each other).

## 7. Comparison with observations (for information; does not change a class)

For every TOTAL run:
- time from G2 to the start of G5 (roofline mean descent over 1 in.), against 6.9 s observed;
- whether the east penthouse falls before the north face moves;
- the largest mean downward acceleration of the north-face roofline over any 2.25 s window, against
  g, and the descent at 5.4 s after the roofline starts, against 242 ft observed.

## 8. Checks (must pass before results are used)

| Check | Criterion |
|---|---|
| Closed-form tests | Axial stiffness within 1 %; Euler load of a pinned strut within 2 %; plastic collapse load of a portal frame within 5 %; elastic catenary force of a restrained beam at large deflection within 5 %; sudden removal of a support under an elastic beam: peak deflection twice the static within 5 % (undamped); impact of a falling mass: momentum conserved within 1 % |
| Independent code | One small removal benchmark (two bays, three storeys) against CalculiX or another code: peak deflection within 10 % |
| Gravity settled | At the trigger, kinetic energy below 1 % of internal energy and roof vertical velocity below 0.1 in./s |
| Energy balance | External work equals kinetic plus internal plus dissipated energy (plastic, friction, contact, damping, deleted elements) within 5 % of the external work throughout |
| Mesh | Halving the element length in the east region (columns 76 to 81, floor 5 to roof): run class unchanged; G-event times within 10 % or 0.5 s, whichever is larger. Run on D0 and RC |
| Removal time | t_r halved and doubled: class unchanged. Run on RC |
| Repeatability | D0 run twice on the same settings: class unchanged |

If D0 or RC fails a check, the Phase 3 result is not stated; the failure is reported with where
and why. No waiver is written in advance.

## Change log

| Date | Change | Reason |
|---|---|---|
| 2026-11-02 | Created | |
