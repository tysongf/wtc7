# Phase 3 plan: does column 79's failure bring down the whole building?

Finalized 2026-11-26 (updated from 2026-11-02 draft after design review). Pre-registered criteria:
`docs/phase3_preregistration.md`. Source fact sheets: `docs/phase3_sources/nist_facts.md` and
`docs/phase3_sources/uaf_notes.md`.

## Why conditional, and why skipping Phase 2

Phase 1 has not passed its gate (beam-buckling mismatch and two narrow numerical check thresholds), and
Phase 2 (multi-hour fire temperature histories) is skipped. Because Phase 3 asks a conditional
structural question—"if Column 79 fails or loses lateral bracing over `N` storeys, does the 47-storey
building arrest or collapse completely?"—it does not depend on how Column 79 failed. To guard against
missing a temperature-assisted progression while skipping Phase 2, baseline runs use 20 C steel
(favouring arrest) and sweep `T9` applies NIST's Case B (~4.0 h) Floor 8–14 steel temperatures.

## What earlier work leaves open

- **NIST (NCSTAR 1-9 / 1-9A)** ran two relevant global LS-DYNA cases (3.05M shells, ~8 weeks on 12
  cores, input files withheld): its 4.0 h fire-damage state (Floors 6–14 failing around Col 79 before
  Col 79 buckles over 9 storeys) and a fire-free "classic" removal of Col 79 between Floors 11 and 13.
  Both collapsed completely, and a 3.5 h damage case without Col 79 buckling arrested locally. NIST
  published no sweep of removed column length or connection capacities.
- **UAF (2020)** never removed Column 79 alone; its smallest removal set removed Columns 79, 80 and 81
  together (Floors 6–13) with all floors kept intact, evaluated via linear-static analysis without
  `P-Delta` or falling-floor impact, reporting ~10 in. eastward tilt and no collapse.

Phase 3 tests `D0` (NIST's 9-storey unbraced state with falling Floor 6–13 bays), `R1`–`R9` (1-to-9
storey removal sweep), `RC` (NIST classic Floors 11–13 removal), and `RU` (UAF's Columns 79–81 removal
in a nonlinear dynamic `P-Delta` + connection-fracture + floor-impact model) under pre-registered rules.

## Resolved architecture decisions

1. **Solver (`wtc7/xfe` extended in C/OpenMP):** Extend `wtc7/xfe/kernel.c` and `wtc7/xfe/` with 3D
   co-rotational elastoplastic fibre beam-columns, coupled 6-DOF breakable connection springs (`F`, `K`,
   `H`, `STC`, `STP`, `SWC`, perimeter moment joints) and explicit 2-storey column splices, plus
   mass-conserving storey-to-storey floor impact contact. Cross-check on a 2-bay x 3-storey sudden
   column-removal benchmark against CalculiX 2.20 (`tools/calculix/`).
2. **Base boundary & lower floors:** Match NIST's boundary—fix column bases below Floor 2, treat the
   1967 Con Edison substation up to Floor 3 as rigid, and explicitly model Floors 2 to 47 including
   Transfer Trusses 1, 2 and 3, transfer girders (`MG-21` to `MG-53`), and the Floor 5 and Floor 7
   diaphragms from the Cantor `S`-sheets.
3. **Storage & compute footprint:** Local `/dev/sda5` has ~2.5 GB free on a 4-core i5 laptop. Keep code,
   benchmarks, and compressed run histories lightweight (a few MB per run), stream/crop FOIA sheets as
   needed without bloating disk, and keep the runner portable to a larger multi-core machine if needed.
4. **Presentation:** Integrate Phase 3 into the unified website (`reports/forensic/index.html`) with a
   Phase 3 Plain-English Question-Driven Audit tab, technical report, and interactive 3D collapse viewer.

## Ordered steps

1. **Lock and hash pre-registration** (`docs/phase3_preregistration.md`, recorded in
   `docs/compute_log.md`) before any Phase 3 calculation.
2. **Phase 3 hand calculations** (`phase3/hand_calcs.py` -> `results/phase3/hand_calcs.md`):
   - Tributary gravity loads on Columns 76–81 and 44 from Floor 47 to Floor 2, checked against NIST's
     7,525 kip (Col 79 above Floor 8) and 174,136 kip total above Floor 8;
   - Double-span Vierendeel and catenary bridging check across a removed Column 79 segment (with the
     `2.0x` sudden-removal dynamic factor against shear/tension connection capacities);
   - One-storey falling-floor impact energy (`m g h` over `153 in.`) against the maximum strain/plastic
     energy absorbable by the connections of one floor bay, and cascade runaway storey count;
   - Elastic (`Pe`) and AISC 360 E3 inelastic (`Pn`) buckling capacities of Columns 80, 81, 76, 77 and
     78 for 1 to 10 unbraced storeys (at 20 C and 200 C);
   - Truss 2 demand check (Floors 5–7, carrying Col 77 and MG-23 / Col 78, supported at its east end by
     Col 80) under loss of Column 80 or debris accumulation on Floors 5–7.
3. **Solver extension & verification** (`wtc7/xfe/`, `tests/test_phase3_xfe.py`,
   `phase3/verify_benchmark.py` -> `results/phase3/verification.md`):
   - All six closed-form tests in `phase3_preregistration.md` Section 8;
   - Independent 2-bay x 3-storey sudden column-removal dynamic cross-check against CalculiX 2.20.
4. **FOIA Cantor & Frankel structural reading** (`A100` onward): grid coordinates, storey elevations,
   column schedule & splices, floor framing by floor group, Transfer Trusses 1–3 & `MG` girders, east
   and west penthouses, and connection capacities.
5. **Build the 47-storey 3D model** (`phase3/building_model.py`) with settled gravity initialization
   (`KE / IE < 1 %`, roof `|v_z| < 0.1 in./s` before any trigger).
6. **Pilot & verification checks** on `D0` and `RC` (energy balance, mesh refinement, `t_r` sensitivity,
   repeatability).
7. **Full run matrix**: `D0`, `RC`, `RU`, `RU_debris`, `R1`–`R9`, sweeps `T1`–`T9`, and the two combined
   `D0` runs.
8. **Unified website & write-up**: add Phase 3 audit cards, 2D diagrams, technical report, and 3D
   building-collapse viewer to `reports/forensic/index.html`.
