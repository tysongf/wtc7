# Pre-registration: Phase 3 (conditional), column 79 failure and global collapse

Written 2026-11-02 (draft); finalized and hashed 2026-11-26 before any Phase 3 calculation, hand or
finite-element. Its SHA-256 is recorded in `docs/compute_log.md` before the first Phase 3 calculation;
later edits follow the same rule as `docs/preregistration.md`: every edit is listed in the change log
at the bottom with its reason, and no criterion or range changes after results for it exist.

Sources are cited by NCSTAR report and section (`docs/phase3_sources/nist_facts.md`), with secondary
claims from the 2020 University of Alaska Fairbanks (UAF) report, AE911Truth Request for Correction,
and NIST's 2020 reply documented in `docs/phase3_sources/uaf_notes.md` (used only to define the `RU`
head-to-head benchmark, never as unverified structural inputs).

## 1. Question and status

**Question.** If column 79 loses its lateral or axial support over part of its height, does WTC 7, as
drawn and under NIST's service gravity loads, collapse completely?

**Conditional, and skipping Phase 2.** The study's phases were originally gated (`docs/preregistration.md`
Section 8). Phase 1 has not passed its gate (items 3 and 5 remain open) and Phase 2 (computed fire
temperature histories) is skipped. Phase 3 is run now on the explicit condition that column 79 fails
(or loses lateral support over a stated storey band), without asking how. Its result does not depend on
Phase 1 or Phase 2 and changes neither. Because Phase 2 is skipped, baseline runs use ambient 20 C
steel (stronger than heated steel, favouring arrest), while sweep `T9` applies NIST's approximate
Floor 8 to 14 Case B steel temperatures to test whether elevated neighbour temperatures change arrest
against collapse.

**What Phase 3 can and cannot show.**
- It can show whether column 79's failure is sufficient, in a nonlinear dynamic 3D model with P-delta,
  connection fracture, column-splice failure, and mass-conserving floor impact, for total collapse;
  how many storeys of loss are needed (`R1` to `R9`); and how both NIST's classic removal (`RC`) and
  UAF's three-column removal (`RU`) behave when analysed dynamically with failing connections.
- It cannot show why column 79 failed. Whether fire did it belongs to Phases 1 and 2. No non-structural
  cause is modelled; a result that column 79's failure is not sufficient would contradict NIST's global
  sequence, not establish an alternative cause.

## 2. Events

All displacements are vertical, measured downward from the settled state at the end of the gravity step.
`h = 153 in.` (typical tenant storey, 12 ft 9 in.; NCSTAR 1-9 §5.3.2).

| ID | Event | Definition |
|---|---|---|
| G1 | Column 79 fails | Removal runs (`R1`–`R9`, `RC`, `RU`): at completion of the removal ramp. Damage-state runs (`D0`): the top of column 79 descends by more than `h` |
| G2 | East penthouse falls | The mean vertical displacement of the east penthouse roof framing exceeds `h` |
| G3 | First neighbour fails | The top of column 80, column 81 or column 76 descends by more than `h` (in `RU`, where 80 and 81 are removed at G1, G3 tracks columns 76 to 78) |
| G4 | Interior progression complete | The tops of all 24 interior columns (58 to 81) have descended by more than `h` |
| G5 | Exterior descent | The mean vertical displacement of the north-face roofline (roof-level nodes of the north perimeter columns) exceeds `h` |

"The top of a column" is its roof-level node. A column whose splice or lower segment buckles or
separates counts by the descent of its roof-level node.

## 3. Outcome classes

Each run is classified at the end of its run time (Section 6):
- **TOTAL** if `G4` and `G5` both occur.
- **PARTIAL** if `G2` or `G3` occurs, but not both `G4` and `G5`.
- **LOCAL** if neither `G2` nor `G3` occurs: failure stays confined to the triggered column(s) and
  directly tributary floor bays.
- **INCOMPLETE** if the run stops for numerical reasons before `TOTAL` and before its end time.
  An incomplete run is never reported as `PARTIAL` or `LOCAL`.

The primary Phase 3 verdict (governed by `D0` and its sweeps):
- **SUFFICIENT** (agrees with NIST's global propagation) if the baseline damage-state run (`D0`) is
  `TOTAL`.
- **NOT SUFFICIENT** (contradicts NIST's global propagation) if no `D0`, `RC`, or `R1`–`R9` run in
  Section 5 is `TOTAL` with every parameter inside its range.
- **CONDITIONAL** in every other case. The report then lists each trigger and parameter whose change
  moves the run across the `TOTAL` line, with the value at which it flips.

Reported alongside the primary verdict:
- **Minimum removal length:** smallest `N` in `R1` to `R9` that gives `TOTAL`, or "none up to nine
  storeys".
- **Head-to-head benchmarks:** outcome class, east roof tilt before `G5`, and progression sequence of
  `RC` (NIST's classic Floors 11–13 removal) and `RU` (UAF's Columns 79, 80, 81 Floors 6–13 removal).

## 4. Reference values (compared with, not tuned to)

| Quantity | Published value | Source |
|---|---|---|
| Column 79 gravity load above floor 8 | 7,525 kip | NCSTAR 1-9 §11.3.1 (A60) |
| Total building gravity load above floor 8 | 174,136 kip (target) / 172,897 kip (LS-DYNA) / 176,500 kip (ANSYS) | NCSTAR 1-9A §3.4.3; 1-9 §11.3.1 |
| Damage state when column 79 buckled | Unsupported E-W and south between floors 5 and 14; north seated girders on seats at floors 8–12 and 14 | NCSTAR 1-9 §12.4.4; 1-9A Fig. 4-17 |
| NIST column failure order (best estimate) | Col 79 at -1.3 s, 80 at -0.6 s, 81 at 0.0 s (penthouse kink), core 76 westward 3.5 to 6.1 s, exterior 5.5 to 7.4 s | NCSTAR 1-9 Table 12-2; 1-9A §4.3.2 |
| NIST classic case (no fire, no debris): Col 79 removed floors 11–13 | Total collapse; floors around 79 fail to roof, east penthouse kinks at 0 s | NCSTAR 1-9 §12.4.7 |
| UAF Case E1 / H1 (linear static, floors intact): Cols 79, 80, 81 removed floors 6–13 | Building tilts ~10 in. east; east penthouse does not collapse; no neighbour columns buckle | UAF (2020) p. 96, 99 |

Video observations, for comparison on `TOTAL` runs (Section 7; do not change outcome classes): east
penthouse starts down at 0.0 s and disappears below roofline at 2.0 s; north-face roofline starts down
at 6.9 s; west penthouse disappears at 9.3 s (NCSTAR 1-9 Table 5-3); north roofline accelerates near
`g` for ~2.25 s (from 1.75 s to 4.0 s after roofline motion starts, covering ~105 ft) and reaches
242 ft (18 storeys) at 5.4 s (NCSTAR 1-9 §12.5.3; `results/phase1/hand_calcs.md` Section 8).

## 5. Solver, model and cases

### 5.1 Solver (`wtc7/xfe`)

Phase 3 extends the in-repository C/OpenMP explicit solver (`wtc7/xfe`, central-difference integration
with 6 DOFs per node) with:
1. **3D co-rotational elastoplastic fibre beam-columns** capturing large rotations, `P-Delta` and
   `P-delta`, lateral/flexural buckling, catenary tension, and steel plasticity (`wtc7.materials`).
2. **Coupled 6-DOF breakable connection elements** for interior simple/seated connections (`F`, `K`,
   `H`, `STC`, `STP`, `SWC`: combined tension-shear interaction per NCSTAR 1-9 §11.2.4, axial bearing
   after gap closure, and seat walk-off travel limits) and perimeter moment connections (`MC` / wind
   girders: flexural plasticity and fracture rotation), plus **explicit two-storey column splices**
   (milled compression bearing maintained under compression; splice-plate tension-shear fracture under
   net uplift or lateral shear).
3. **Mass-conserving storey-to-storey floor impact contact**: failed connections detach member ends
   without deleting element or nodal mass; vertical/3D penalty-damping contact transfers falling-floor
   impact momentum and accumulated debris weight onto the floor framing directly below.

### 5.2 Baseline structure, boundaries and loads

- **Base boundary (matching NIST NCSTAR 1-9A §3.4.2):** Column bases below Floor 2 are fixed; the
  1967 Con Edison substation footprint up to Floor 3 is treated as rigid, with columns bearing on it
  tied at Floor 3. Floors 2 through 47 (and the east/west penthouses) are modelled explicitly,
  including Transfer Trusses 1, 2 and 3, cantilever/transfer girders `MG-21` to `MG-53` between Floors
  5 and 7, the Floor 5 and Floor 7 reinforced diaphragms, and the perimeter moment frames and belt
  trusses (Floors 5–7 and 22–24).
- **Geometry source:** Read from the Cantor structural drawings (FOIA 11-209) and Frankel erection and
  shop drawings (FOIA 12-009 / 09-49). Where sheets are missing or illegible, NCSTAR 1-9 / 1-9A values
  are used; where both are silent, assumptions `A100` onward are recorded with sweep ranges before any
  full-building run.
- **Gravity loads:** Unfactored `DL + SDL + 0.25 LL` from NIST's design load schedule (NCSTAR 1-9
  Fig. 11-17) plus Floor 7 and Floor 46 mechanical equipment weights (NCSTAR 1-9A §3.4.3), no wind.
- **Temperature:** 20 C everywhere in baseline runs (swept in `T9`).
- **Debris damage from WTC 1:** None in baseline runs (swept in `T8`).

### 5.3 Triggers

- **`D0`, NIST's 9-storey damage state (primary baseline).** After gravity settles, the floor-framing
  connections in the bays framing into Column 79 on Floors 6 to 13 are released so those bays fall onto
  Floor 5, leaving Column 79 unbraced E-W and south from Floor 5 to Floor 14 (nine storeys) with an
  initial eastward bow of `L/1000`. North seated girders (`A2001`) at Floors 8 to 12 remain on their
  seats with sheared bolts (bearing/walk-off only), as NIST describes (§12.4.4). Column 79 is not
  artificially deleted; whether it buckles is computed dynamically.
- **`R1` to `R9`, Column 79 removal-length sweep.** All floors initially intact; Column 79 is smoothly
  removed over `N` storeys (`N = 1..9`, from Floor `14 - N` to Floor 14).
- **`RC`, NIST's classic progressive-collapse benchmark (NCSTAR 1-9 §12.4.7).** All floors initially
  intact at 20 C; Column 79 removed between Floors 11 and 13.
- **`RU`, UAF head-to-head benchmark (UAF 2020 Case E1/H1).** All floors initially intact at 20 C;
  Columns 79, 80 and 81 removed simultaneously between Floors 6 and 13 (with `T8` debris damage also
  tested as `RU_debris`, matching UAF p. 94).

In removal runs (`R1`–`R9`, `RC`, `RU`), member internal forces in the removed column segment(s) are
ramped linearly to zero over duration `t_r = 0.1 * T_v1`, where `T_v1` is the first vertical natural
period of the framing above the removed segment computed before the removal runs.

### 5.4 Parameter sweeps (one at a time on `D0` and `RC`)

| ID | Parameter | Baseline | Sweep values |
|---|---|---|---|
| T1 | Service live-load fraction | 0.25 | 0.0; 0.50 |
| T2 | Interior shear & seated connection capacities | as calculated (NIST §11.2.4) | x 0.75; x 1.25 |
| T3 | Column splice tension & shear capacity | as drawn / calculated | x 0.50; x 1.50 |
| T4 | Slab tensile / membrane capacity | as calculated (NCSTAR 1-9A §2.3.1) | x 0.50; x 2.0 |
| T5 | Steel yield strength | nominal (NIST static yield) | -10 %; +10 % |
| T6 | Mass-proportional damping during collapse | 0.5 % of critical at `f_1` | 0 %; 2.0 % |
| T7 | Column 79 initial bow (`D0` only) | `L/1000` east | `L/2000`; `L/500` |
| T8 | WTC 1 southwest debris damage | none | Zone 1 + Zone 2 severed columns (Cols 14A–20 above Fl 7; Col 20 above Fl 43, NCSTAR 1-9A §3.4.3) |
| T9 | Floor 8–14 elevated steel temperatures (skipping-Phase-2 hedge) | 20 C everywhere | Interior cols 76–81 at 200 C and east/core floor framing on Floors 8–13 at 450 C (NIST Case B ~4.0 h band) |

Followed by two combined runs on `D0`: all parameters at the end of their range that individual sweeps
show move toward arrest ("most favourable to arrest"), and all at the end moving toward collapse ("most
favourable to collapse").

## 6. Run length

Each run continues to `30 s` after the trigger, or to `TOTAL` plus `2 s`, whichever comes first.

## 7. Comparison with observations and prior studies (informational; does not change classes)

- For every `TOTAL` run: time from `G2` (east penthouse) to onset of `G5` (north roofline > 1 in.)
  against `6.9 s` observed; whether `G2` precedes `G5`; peak mean downward acceleration of the north
  roofline over any `2.25 s` window against `1.0 g`; and north roofline drop `5.4 s` after onset
  against `242 ft` observed.
- For `RU` and `RU_debris`: eastward roof tilt (inches) and neighbour column demand/buckling compared
  directly against UAF's `~10 in.` linear-static result.
- Presentation: Phase 3 results, Plain-English Question-Driven Audit cards, and interactive 3D global
  collapse animations are added as a dedicated Phase 3 view in `reports/forensic/index.html`.

## 8. Model checks (must pass before full-building results are stated)

| Check | Criterion |
|---|---|
| Closed-form unit tests (`tests/test_phase3_xfe.py`) | (1) Axial stiffness within 1 %; (2) Euler buckling of a 3D pinned strut within 2 %; (3) Plastic collapse load of a fixed-base portal frame within 5 %; (4) Large-deflection elastic catenary force of a pin-restrained beam within 5 %; (5) Sudden removal of a support under an undamped elastic two-span beam: peak dynamic deflection equals `2.0 x static` within 5 %; (6) Falling-mass floor impact: total momentum conserved within 1 % and nodal mass conserved 100 % |
| Independent code benchmark (`phase3/verify_benchmark.py`) | Two-bay, three-storey 3D steel frame under sudden middle-column removal cross-checked against CalculiX 2.20 (`*DYNAMIC`): peak vertical deflection at the removed column line within 10 % |
| Gravity settled | At trigger onset (`t = t_trig`), kinetic energy `< 1 %` of internal energy and roof vertical velocity `< 0.1 in./s` |
| Energy balance | External work equals `KE + IE + dissipated energy` (plastic, damping, contact friction/damping, broken-connection lost energy) within `5 %` of external work throughout |
| Mesh refinement | Halving beam/column element length in the east zone (Columns 76–81, Floor 5 to roof) on `D0` and `RC`: outcome class unchanged; `G`-event times within `10 %` or `0.5 s` (whichever is larger) |
| Removal duration | `t_r` halved and doubled on `RC`: outcome class unchanged |
| Repeatability | `D0` repeated with identical settings: outcome class unchanged |

If `D0` or `RC` fails a check, the Phase 3 verdict is withheld until resolved, and the failure is
reported openly with its magnitude and cause. No check is waived after seeing results.

## Change log

| Date | Change | Reason |
|---|---|---|
| 2026-11-02 | Initial draft created. | Study lead decision to run Phase 3 conditionally before Phase 1 passes its gate (`docs/preregistration.md` change log). |
| 2026-11-26 | Finalized before any Phase 3 hand or FE calculation: locked solver (`wtc7/xfe` extended with 3D fibre beams, coupled joints/splices, and mass-conserving floor impact, benchmarked against CalculiX 2.20), Floor 2 / rigid Con Ed substation base boundary with explicit Trusses 1–3, added UAF head-to-head trigger `RU` and Floor 8–14 thermal sensitivity `T9` (since Phase 2 is skipped), and hashed in `docs/compute_log.md`. | Design review completed prior to any Phase 3 calculation. |
