# Open questions

Things the public documents did not settle, found while building Phase 1. Each
lists what was done about it and the assumption ID (see `docs/assumptions.md`).

## Found in NIST's published material

**Q01. NCSTAR 1-9 Table E-4 (A572 Grade 50 stress-strain model) is a copy of Table E-3 (A36).**
The two tables are byte-identical after extraction, and the Table E-4 header comment
still reads "model for A36 steel" (`tests/test_materials.py::test_published_E4_is_duplicate_of_E3`).
A572 is the grade of every beam, girder and interior column (§11.2.2), so the curves NIST
used for the critical members are not published. Done: rebuilt from Appendix E Eqs. 1 to 6
with NIST's A572 constants (k = 1.0, static yield 369.6 MPa). The same rebuild reproduces
the published A36 and CSA G40.21 tables (A39).

**Q02. Appendix E Eq. 3 strain-rate term.** As printed, K(T) uses k2 + k3 x (strain rate). Read
that way, the rebuild misses the published tables by up to 173 %. Read as k2 + k3 x ln(strain
rate), it matches every plastic point within 1.7 % (A36) and 2.8 % (G40.21). The ln reading is
used.

**Q03. First point of each MISO curve.** Appendix E says the first point is where the E(T) line
meets the adjusted curve. At 20 °C it is the static yield. At 400 °C and above, the published
first points match the *unshifted* curve k K(T) eps^n(T), not the shifted curve the other
points follow. Done: reproduced as published; it gives the "hump" near 400 °C to 550 °C that
NIST mentions.

**Q04. Northmost floor beam.** Fig. 8-16 (drawing S-8) shows a W21x44 with 24 studs nearest
column 44; Fig. 8-22 labels all five beams in the LS-DYNA model "W24x55 Floor Beams". The
drawing is used (A02). *Settled by E12/13 (2026-10-23):* the northmost beam is G3005, a W21x44 with
<24> studs, as on S-8.

**Q05. Lateral walk-off distance.** The errata changed the column 79 seat from 11 in. to 12 in.
and the lateral walk-off distance from 5.5 in. to 6.25 in., describing 6.25 in. as "the length
from the flange tip to the far side of the web". For a W33x130 (bf = 11.5 in., tw = 0.58 in.)
that length is 6.04 in.; a girder centred on a 12 in. seat clears it when moved 6 + 0.29 =
6.29 in. The 0.2 in. difference is inside the S2 sweep (5.5 to 6.5 in.).

**Q06. Thermal expansion law.** §8.7.2 uses alpha = 1.4e-5 /°C. The ANSYS and LS-DYNA models
used a temperature-dependent coefficient (§12.2.1; NCSTAR 1-9A §2) that is not given. Done:
NIST set uses 1.4e-5; EC3 set uses EN 1993-1-2 Eq. 3.1a (A51).

**Q07. Stud strength at temperature.** §11.2.5 applies "the tensile strength reduction factor
for steel" above 300 °C, but NCSTAR 1-9 only prints the bolt factor (Table E-8). Done: bolt
factor used, scaled to 1.0 at 300 °C (A14). With the slab unheated, stud temperatures in Phase 1
stay near or below 300 °C until the beams pass about 580 °C, so the choice barely matters here.

**Q08. Column temperatures in the §8.8 partial-floor model** are not stated. Done: 20 °C (A16).

## Connection and geometry details not given

**Q09. Slot size** in the top clip angle at column 79 and the top plate at column 44 (A25, swept S3).
*Drawings (2026-10-23):* no slot is called out for the column 79 clip angle, so the sheet default
15/16 in. round holes apply; the column 44 top plate has 1 1/8 x 15/16 in. short slots (A95, A96).

**Q10. Clearances** between the girder ends and the column faces, and between the beam ends
and the girder web or exterior columns (A26, A27, A29; S11). *Drawings (2026-10-23):* at column 79
the girder end is 1.78 in. from the flange face at its centreline (1.36 in. at the nearest corner;
9114, partly legible). The column 44 end and the beam ends are not dimensioned.

**Q11. Lateral gap** between the girder and the inside of the column 44 flanges (A28, S12).
*Partly settled by 1370 and 9102 (2026-10-23):* the girder enters a 12.6 in. pocket between the W14x665
flanges at 16.5 deg, so its west flange edge had to be cut back to clear the column flange; the cut-back
is not dimensioned. The drawings set uses 0.25 in. on the west side and 1.38 in. on the east (A96), and
S12 still sweeps 0.5, 1.0 and 3.0 in.

**Q12. Column 79 side plates as a lateral stop.** *Geometry settled from the shop drawings
(2026-10-23); the effect is now a model output.* Frankel 1091 and 9114 (`sources/drawings/READING.md`)
show 2 PL 26 x 2 welded across the flange tips of the W14x730, projecting 1 13/16 in. past the north
flange face (inferred from the plate width and the as-fabricated column depth). The girder end sits at
the mouth of the recess: by the written dimensions its centreline is 1.78 in. from the flange face,
the west flange corner 0.38 in. outside the plane of the plate ends and the east corner 0.45 in. inside
(as scaled, the west corner is level with the plate ends). Inside the recess the west flange tip has
about 4.15 in. of room before it meets the west plate, less than the 6.25 in. needed to walk off; the
east tip has 2.26 in. Whether the side plate stops the girder therefore depends on how far the girder
end moves toward the column before it is pushed west, which the models compute (A94; side plates are
in both models' 'drawings' geometry, with 'clear' runs to show their effect). Secondary sources (the
2020 UAF report, AE911Truth's 2020 request for correction, NIST's 2020 reply) are summarized in
READING.md; they agree with this reading of the room-temperature position.

**Q13. Bearing-face orientation.** *Settled from the drawings (2026-10-23), and the earlier
assumption was wrong.* Column 79 is not on the building grid: its axes are rotated about 12.3 deg
clockwise, and the girder meets its north face 7/8 in 12 (4.17 deg) off square (9114, 1091; the
rotation is inferred from three members). Column 44 is on the grid and the girder meets its web at
3 9/16 in 12 (16.5 deg). The screening runs reported on 2026-10-22 used faces on the grid at column 79
(14.6 deg to the girder, A48), which made the face push the girder end sideways about 3.5 times harder
than the drawings imply (tan 14.6 deg = 0.26 against tan 4.17 deg = 0.073). Those runs are kept as
superseded; the screening was repeated with the drawings geometry (A93).

**Q14. Beam positions and girder skew** *(settled from E12/13, 2026-10-23).* The digitized values
(A04, A05) were off: the girder skew is 3 9/16 in 12 = 16.5 deg (not 14.6), and the beam stations from
column 44 are 50.1, 151.7, 272.1, 392.4 and 512.8 in. (digitized: 45.6 to 466.8 in., about 10 % short).
The beam spans differ (piece lengths 608 to 644 in.) because the east wall is skewed. The southmost beam
(K3004) is only about 22 in. from the girder's column 79 end. A W12x26 (P3016) frames into the girder
from the west; it is not in NIST's model and is not modelled here (A92).

**Q15. Friction.** NIST describes no friction at the seats, on the bearing faces, or between the
slab and the steel. Done: 0.30 baseline (AISC Class A slip coefficient as a proxy), swept 0 to
0.6 (A42, A43, A49; S4, S15).

## Drawings and data not in hand

**Q16. Girder studs.** FAQ 27: S-8-10 shows studs on some girders for floor 10, and the Salvarinas
(1986) figure shows a "similar, but not exactly the same" number. The floor 13 erection drawing
E12/13 and S-8 rev H show no stud count on girder A2001 (2026-10-23); S-8-10 (floor 10) shows "<30>"
(partly legible). So floor 13 had none, as NIST modelled; 22 and 30 remain swept as the floor 10
pattern (A40, A41; S1).

**Q17. Drawings S-8, S-8-10, E10/11, E12/13 and Frankel shop drawings.** *Obtained 2026-10-23*
from NIST FOIA releases mirrored on archive.org (`sources/drawings/SOURCES.md`; the scans are archived in
`sources/drawings/raw/`). Still missing: the girder A2001 piece drawing (Frankel 2001; the 2000
series was not in the FOIA 12-009 release), so the girder's length, its column 44 end and its hole
layout are not drawn anywhere in hand; the girder end at column 44 is set from the column 44 geometry
with an assumed 0.5 in. clearance (A96).

**Q18. Floor 10 added loads (S-8-10)** are not stated on the drawing (FAQ 27). Not needed in
Phase 1 (floor 13 framing); needed in Phase 2 for floor 10.

**Q19. Steel temperature histories for Phase 2.** Chapter 10 presents them as colour plots
(e.g. Figs. 10-19, 10-39, 10-59); no data tables were found in NCSTAR 1-9. Phase 2 will need to
digitize them (brief: sweep +/-100 °C).

**Q20. Column 79 load after floor failures.** §11.3.1 gives 7,525 kip under gravity at floor 8;
§11.3.2 says column forces changed by less than 0.5 % through 4.0 h. The load the column carries
once nine floors have failed (debris, load paths through the remaining framing) is a Phase 2
output.

## Found in the drawings (2026-10-23)

**Q21. Girder end stiffeners.** 9114 shows PL 5 1/2 x 3/4 x 1'-6 stiffeners on both sides of the
girder web at the column 79 end. NIST says they were not in its models. The shell model omits them in
its baseline, as NIST did, and runs them as drawn as a sensitivity case (A97).

**Q22. Camber.** E12/13 gives 1 in. camber for the girder and 1 3/4 to 2 1/4 in. for the beams. NIST
does not mention camber; neither model includes it.
