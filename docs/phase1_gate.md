# Phase 1 gate note

Gate definition: `docs/preregistration.md` Section 8. Current revision 2026-11-02 (draft); the
2026-10-22 decision is kept below.

## Decision (2026-11-02)

**Phase 1 has not passed its gate. Phase 2 is not started.**

| Gate item | Status |
|---|---|
| 1. Hand calculations | Done: `results/phase1/hand_calcs.md` |
| 2. Beam-element model: checks, baseline, S1 to S15 | Done (2026-10-22, below) |
| 3. Detailed shell model: built, every Section 4 check passed, baseline and sweeps reported | **Not met.** Built; baseline, every sweep and both combined runs reported (`results/phase1/shell/summary.md`, writeup Section 4). Two checks fail: mesh and quasi-static |
| 4. Column 79 buckling check at nine storeys | Done: hand calculation section 7 |
| 5. Outcome class from the detailed model; if it differs from NIST, the modelling choice that explains it | Class stated: **CONDITIONAL** (writeup Section 5). It differs from NIST. **Explanation found** (NIST-replica runs, change log 2026-11-01): NIST's model had no side plates at column 79. Without them the model walks off by 700 C whichever single drawn feature is put back; with them nothing walks off under the 600 C ramp. NIST's mechanism (rocking after the beams buckle) is not reproduced; that is reported as a separate, unexplained difference |

## The failed checks

| Check | By how much | Why it cannot change an outcome | What would clear it |
|---|---|---|---|
| Mesh (0.9 against 1.8 in.) | Lateral movement at column 79 1.501 against 1.467 in.: 2.3 % against 2 %. T_E1 passes (6.2 C) | Walk-off needs 6.25 in.; the difference is 0.034 in. The 0.9 in. run's hourglass energy is 0.22 of internal energy (0.09 at 1.8 in.) | A 0.45 in. run: about 8 times the 0.9 in. run's 39 h, about two weeks on the laptop |
| Quasi-static (kinetic energy below 5 % of internal energy throughout) | Every run during the gravity ramp (0.39 to 0.50); 31 of the 44 reported and diagnostic runs at some heating step (largest 0.21 at a girder buckle, otherwise at most 0.076) | Half and quarter rate agree within 3 C on every event, so the reported results are not rate effects | A slower gravity ramp and settling before heating, then rerunning the reported set (41 runs, about a week on the laptop) |

Either check can be cleared only by more runs. Waiving one would override the preregistration's
"must pass" wording; that decision, and the reason for it, would be recorded in the change log.

## What the detailed model shows

- No run walks off under NIST's 600 C ramp: not the baseline, not any one-at-a-time value.
- The preregistered combined run walks off at 700 C, during the hold, after the girder buckles; a
  repeat with state dumps reproduces it and continues to loss of support.
- The Section 6 repeat of the combination does not walk off; the girder does not buckle.
- No beam buckles in the baseline (NIST: 436 C).
- The NIST replica (NIST's column 79 idealizations on the drawn framing) walks off at 511 C by
  sliding along the 14.6 deg face, without any beam buckling. Taking the idealizations back one at a
  time: standard holes change nothing; the drawn face delays walk-off to 655 C; friction 0.3 stops
  the sliding, but the girder buckles and twists off at 650 to 655 C; the drawn face with the side
  plates holds the girder to 700 C.

## Before Phase 2 can start

- Clear or decide on the two failed checks (item 3).

## Decision (2026-10-22, superseded)

**Phase 1 has not passed its gate. Phase 2 is not started.**

| Gate item | Status |
|---|---|
| 1. Hand calculations | Done: `results/phase1/hand_calcs.md` |
| 2. Beam-element model: checks, baseline, S1 to S15 | Done, with one exception noted below: `results/phase1/summary.md` |
| 3. Detailed shell model (NIST §8.8 approach) | **Not built.** Plan: `docs/phase1_detailed_model_plan.md` |
| 4. Column 79 buckling check at nine storeys | Done: hand calculation section 7 |
| 5. Outcome class from the detailed model | **Not available** (needs item 3) |

## What was decided before moving on (2026-10-22)

1. **The screening result does not count as the Phase 1 outcome.** The beam-element
   model is plan-view only. It cannot represent the mechanism NIST's own partial-floor
   model produced at column 79 (beams buckling laterally, then the girder rocking off its
   seat), so its CONDITIONAL class is reported as a screening result only, as the
   preregistration requires (Section 7).
2. **The detailed model must resolve the column 79 face friction and geometry first.**
   In the screening model, walk-off at column 79 below 700 °C depends on one input:
   friction between the girder end and the column 79 face and seat. The outcome
   flips between 0.22 and 0.24, just below tan(14.6°) = 0.26, the tangent of the girder's
   skew to the column face (digitized from Fig. 8-16). At low friction, two connection
   details (a long slot in the column 79 clip angle, a tight girder end gap) can still
   prevent walk-off. The detailed model needs the face geometry from the shop
   drawings (open questions Q12, Q13) and must sweep friction across that threshold.
3. **Mesh for further beam-element runs.** Early events (studs, bolts) are converged at
   the baseline mesh; events after about 550 °C move by up to about 30 °C between the
   baseline and the finest mesh. Walk-off temperatures were checked on all three
   meshes and agree within 2 °C, so the baseline mesh is used for them.
4. **Quasi-static criterion.** Kinetic energy exceeded 5 % of strain energy only in
   short transients (within about 1 °C) right after brittle connection failures. That is
   at most 11 of about 500 steps in any run. Half-rate reruns check that the event
   temperatures do not depend on the loading rate. This is recorded as an exception to
   the preregistered "throughout" wording, not as a pass. The two half-rate reruns of the
   worst cases reproduce every event temperature within 2 °C.

## Before Phase 2 can start (2026-10-22)

- Build and run the detailed model per `docs/phase1_detailed_model_plan.md`, with the
  preregistered sweeps and checks unchanged.
- Settle or sweep Q12 (column 79 side plates as a lateral stop) and Q13 (bearing-face
  orientation).
- State the detailed model's outcome class; if it differs from NIST, trace the
  difference to a specific modelling choice before going further.
