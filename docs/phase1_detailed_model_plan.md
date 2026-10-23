# Phase 1 detailed model: build plan

The Phase 1 gate (preregistration Section 8) needs a detailed partial-floor model in
the style of NIST's LS-DYNA model (NCSTAR 1-9 §8.8). This note fixed what it must
contain before the build started (2026-10-22). The model is built as
`phase1/shell_model.py`, with the changes recorded at the end of this note.

## Why the beam-element model is not enough

The plan-view model cannot show the mechanism NIST's partial-floor model actually
produced at column 79: floor beams buckling laterally and the girder **rocking** off
its seat (Table 8-2, Fig. 8-27b). It has no vertical direction, no twist and no
local buckling. It can show sliding walk-off and the order of connection failures,
which is what it is used for.

## Model content (from §8.8 unless noted)

| Item | Specification |
|---|---|
| Members | W33x130 girder and five floor beams (A02) as fully integrated shells, 5 through-thickness points, about 1.8 in. elements |
| Slab and deck | One layer of shells, about 7.5 in. elements, tension/compression asymmetric concrete with smeared WWF; unheated in the baseline |
| Studs | Discrete nonlinear springs, 28 or 24 per beam (A06), 19.5 kip (A13) |
| Bolts | Separate shear and axial springs per bolt: 2 + 2 at each girder seat, 6 per fin, 2 + 2 at each exterior seat |
| Seats, clip angles, top plates | Shells, welded edges fixed; seat at col 44 with its vertical stiffener |
| Columns | Short sections: col 79 north flange and the projecting parts of its side plates (open question Q12); col 44 web and near-side flanges; exterior columns likewise; fixed along web-flange and flange-plate junctions |
| Contact | Girder and beams on seats; girder and beams against column surfaces; slab on girder (gravity transfer, some rotational restraint); slab extended 8 in. beyond the girder flange |
| Slab boundary | North and east edges: translations fixed; south edge: symmetry; west edge: no in-plane movement, no rotation about the edge (S6 releases west and south) |
| Loading | Gravity ramped smoothly over 1 s to 87.5 psf (A34); then uniform ramp to beam 600 °C, girder 500 °C (S7 extends to 700 °C) |
| Materials | NIST set (Appendix E, A572 rebuilt, `wtc7/materials.py`) and EN 1993-1-2 |
| Outputs | Event temperatures as in preregistration Section 1 (including E2r rocking: twist >= atan(bf/d)); girder end displacement relative to seat at col 79 against temperature; KE/IE |

## Software

Explicit dynamics with contact and element erosion is needed. Free options: OpenRadioss
(explicit, LS-DYNA-like keyword input via its converter) or CalculiX (implicit and
explicit, contact; weaker for this kind of large-deformation contact problem). The
choice should be made after a two-member trial (one beam on a seat with contact and a
bolt spring) runs in each.

## Rough size and time (to be replaced by a timed pilot)

About 5 members x (perimeter about 60 in. / 1.8 in.) x (length about 600 in. / 1.8 in.)
gives roughly 60,000 shell elements for the steel, plus about 8,000 slab elements. The
explicit time step for 1.8 in. steel shells is about 1.8 in. / (sqrt(E / rho) = 199,000 in./s)
= 9e-6 s, so NIST's 4 s event needs about 450,000 cycles before any mass scaling; any mass
scaling must be reported with the KE/IE check. Plan a coarse pilot (3.6 in. elements) first and extrapolate (brief: Phase 3
compute plan, applied here too).

## Before running

1. Settle Q12 (column 79 side-plate projection relative to the girder end) from the
   Frankel shop drawing if it can be obtained; otherwise add it as a swept geometry case
   with both readings run.
2. Reuse the preregistered sweeps S1 to S15 and the mesh-convergence and quasi-static
   criteria unchanged.

## As built (2026-10-23)

- **Geometry.** The shop, erection and structural drawings were obtained (`sources/drawings/`).
  The model uses them rather than the digitized NCSTAR figures:
  - girder skew 16.5 deg;
  - column 79 rotated 12.3 deg, with its side plates as drawn;
  - beam stations and spans from E12/13;
  - seat plate 12 x 8 1/4 in.;
  - column 44 pocket.
  See assumptions A90 to A99 and preregistration Section 9.
- **Software.** Neither candidate was used.
  - OpenRadioss was withdrawn by its owner in October 2026; the repository and site are gone.
    The community fork (OpenCourant) is days old and depends on a proprietary input reader.
  - Radioss's tabulated thermal steel law (LAW109) also has no temperature-dependent Young's
    modulus.
  - CalculiX 2.20 runs here (`scripts/get_calculix.sh`). It is implicit, its shells are expanded
    to bricks, and it has no failure elements for breakable bolts. Following NIST's failure
    sequence would need a restart at every connection failure.
  - A purpose-built explicit solver (`wtc7/xfe`) was therefore written: Belytschko-Lin-Tsay shells
    with temperature-dependent J2 plasticity, penalty contact with friction, and breakable springs.
    It is verified against closed-form results (`tests/test_xfe.py`) and against CalculiX for
    lateral-torsional buckling (`phase1/verify_xfe.py`).
  - The CalculiX trial the plan called for became this cross-check.
- **Slab east edge.** The fixed slab edge is on the exterior column line, 8.5 in. beyond the beam
  ends (A99). Fixing it right at the beam ends clamped each beam end between its seat and the slab:
  in the gravity pilot the exterior seats carried about three times their share of the load.
- **Slab material.** The slab is linear elastic (A72), not NIST's tension/compression concrete
  model. The slab is unheated in Phase 1.
