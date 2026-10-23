# Phase 1 gate note

Date: 2026-10-22. Gate definition: `docs/preregistration.md` Section 8.

## Decision

**Phase 1 has not passed its gate. Phase 2 is not started.**

| Gate item | Status |
|---|---|
| 1. Hand calculations | Done: `results/phase1/hand_calcs.md` |
| 2. Beam-element model: checks, baseline, S1 to S15 | Done, with one exception noted below: `results/phase1/summary.md` |
| 3. Detailed shell model (NIST §8.8 approach) | **Not built.** Plan: `docs/phase1_detailed_model_plan.md` |
| 4. Column 79 buckling check at nine storeys | Done: hand calculation section 7 |
| 5. Outcome class from the detailed model | **Not available** (needs item 3) |

## What was decided before moving on

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

## Before Phase 2 can start

- Build and run the detailed model per `docs/phase1_detailed_model_plan.md`, with the
  preregistered sweeps and checks unchanged.
- Settle or sweep Q12 (column 79 side plates as a lateral stop) and Q13 (bearing-face
  orientation).
- State the detailed model's outcome class; if it differs from NIST, trace the
  difference to a specific modelling choice before going further.
