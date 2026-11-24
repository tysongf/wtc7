# Phase 3 plan: does column 79's failure bring down the whole building?

Draft, 2026-11-02. Criteria are in `docs/phase3_preregistration.md`; this file is the plan for
getting there. Source notes: `docs/phase3_sources/nist_facts.md` (NIST) and
`docs/phase3_sources/uaf_notes.md` (University of Alaska Fairbanks 2020, secondary).

## Why conditional, and why now

Phase 1 has not passed its gate, so the preregistered order would hold Phase 3 back. The question
Phase 3 asks ("if column 79 fails, does everything follow?") does not depend on how column 79
failed, so it can be answered now without touching the Phase 1 result. The decision is recorded in
the change log of `docs/preregistration.md`.

## What earlier work leaves open

- **NIST** ran two global cases that bear on this: its best estimate (fire and debris damage, column
  79 buckles after floors 5 to 13 fail around it) and a "classic" case with column 79 removed
  between floors 11 and 13 and no fire or debris. Both collapsed completely. The model (LS-DYNA,
  3.05 million elements) took up to eight weeks per run on 12 cores; its input files were not
  released. NIST ran no sweep of the removed length or of the connection capacities.
- **UAF** removed columns 79, 80 and 81 together (never 79 alone), kept every floor intact, and
  judged failure from linear analyses (a column fails when its linear axial force exceeds its design
  load; no P-delta). Its "no collapse" result for 79 to 81 is therefore not a test of this question
  either.

Neither tested column 79 alone with a nonlinear dynamic model, a removal-length sweep, and
published criteria. That is the gap Phase 3 fills.

## Steps

1. **Approve and hash** the Phase 3 preregistration and the change-log row, before any Phase 3
   calculation.
2. **Get the drawings.** Download and archive, with checksums, the Cantor structural set (FOIA
   11-209, 41 files, 131 MB) and the Frankel erection sheets (FOIA 12-009, 64 files, 168 MB),
   extending `scripts/fetch_drawings.sh`. We hold 16 drawing files now, almost all for floors 8 to 13 near column 79.
3. **Read the frame.** Grid coordinates, storey heights, column schedule and splices, floor framing
   by floor type, transfer trusses and girders at floors 5 to 7, the east penthouse, and the
   connection types. Inputs go into `wtc7/assumptions.py` as A100 onward with source and status;
   gaps go into `docs/open_questions.md`. NIST lists none of the grid, the column schedule or the
   truss member sizes (fact sheet Section 7), so the drawings are the only source.
4. **Phase 3 hand calculations** (`results/phase3/hand_calcs.md`), reported before any model run
   and setting no class:
   - column loads at each floor for columns 76 to 81, checked against NIST's 7,525 kip for column 79;
   - whether the floors above a removed segment of column 79 can bridge it (shear-tab connections
     in Vierendeel or catenary action, with the dynamic factor for sudden removal);
   - whether a falling floor stops on the one below (energy of a one-storey fall against what the
     floor connections can absorb), and how many floors the cascade needs;
   - the buckling capacity of columns 80, 81 and 76 to 78 as floors around them are lost, as in
     Phase 1 hand calculation Section 7;
   - Truss 2 against the loss of column 80 above floor 7.
5. **Solver set-up and checks**: the closed-form tests and the small benchmark of preregistration
   Section 8, before the building model is used.
6. **Build the model**: a 3D frame of all storeys with beam-column elements, nonlinear connection
   springs that fail, coarse slab shells for mass and membrane action, and contact so that falling
   floors land on the floors below. Gravity is ramped and settled before any trigger (the Phase 1
   lesson: an unsettled gravity step decided the order of the bolt failures).
7. **Pilot**: time one D0 run to replace the estimate below.
8. **Runs**, in order: D0 and RC; the mesh, removal-time and repeat checks; R1 to R9; the one-at-a-time
   sweeps; the two combined runs.
9. **Write-up and forensic page**, with the class, the sweep result and the comparison with the
   observations.

## Size and time (estimate, to be replaced by the pilot)

About 60,000 beam elements and 75,000 slab shells at about 5 ft. The time step is set by the
shortest beam elements (about 2 ft): about 1.2e-4 s, so 30 s takes about 250,000 cycles. At the
rate the Phase 1 shell runs achieved (about 4 million element updates per second on two threads),
that is 2 to 4 h per run before contact. Section 5 lists 11 triggers, 23 sweep runs, 2 combined
runs and 5 check runs: about 41 runs, roughly a week of laptop time, plus the fine-mesh runs at
several times the cost.

Reading the drawings and building the model are the long part: weeks, not days. The floors below
floor 7 (transfer trusses, the Con Ed substation) are the most complex and the least well drawn;
UAF's model started at floor 3 because the substation drawings were missing.

## Decision needed: the solver

| Option | For | Against |
|---|---|---|
| **OpenRadioss** (open-source explicit code, AGPL; beams, shells, contact, element deletion) | Mature collapse and impact code; contact between falling floors is built in; can be checked against the same closed-form tests | A new external dependency (download or build); its input format has to be learned |
| **Extend our explicit solver** (`wtc7/xfe`) with 3D beams, connection springs and floor contact | Same code and checks as Phase 1; every line is ours | Weeks of solver work before any building run; large-scale contact is the hardest part and is new |
| **OpenSees** | Standard for column-removal studies; good beam-column elements | No contact between falling floors, so the floor cascade and debris loading cannot be represented |

Recommended: OpenRadioss, verified against the closed-form tests and, on the small benchmark,
against our own solver.

## What this will not show

- Why column 79 failed. Phase 3 assumes it.
- Heated members: all steel is at 20 C (Phase 2 supplies temperatures).
- Local buckling of plates, weld fracture and bolt tear-out inside connections; connections are
  springs calibrated by hand calculation, not meshed.
- Anything about causes other than column 79's failure. A result that its failure is not
  sufficient would contradict NIST's sequence; it would not by itself show what happened instead.
