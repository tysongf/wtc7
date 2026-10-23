# Reading of the WTC 7 fabrication, erection and structural drawings for Q12 and Q13

Read 2026-10-23 from the scans listed in `SOURCES.md`. Crops are in `crops/`. Each reading gives
the sheet, its revision and where on the sheet it is, then a confidence label:

- **clearly legible**: read directly, no doubt about the characters;
- **partly legible**: read, but a character or the reference line is uncertain;
- **not legible**: could not be read (no value given);
- **inferred**: not written on the drawing; derived from written dimensions or from scaling.

"Shown" lists what the drawing says. "Inferred" lists what I derived. Pixel boxes are in the full
resolution raw scan, (x0, y0)-(x1, y1).

Coordinates used for inferences: for column 79, N' is the column axis through the north (seat)
flange and the web, E' is perpendicular to it (along the flanges); origin at the column centre.
Frankel's actual column size is used (W 22 3/8 x 17 7/8, so the north flange face is at
N' = 11 3/16 in.).

## Short answers

**Q12 (side plates as a stop).** The shop drawings put the girder end at the mouth of the recess,
not inside it: by the written dimensions the girder end, at the girder centreline, is 1.78 in. from
the north flange face of column 79, and the side plates project 1 13/16 in. (1.81 in.), so the
end is flush with the outer ends of the side plates. Because the girder is 4.17 degrees off square
to the column, its west flange corner is about 0.4 in. outside the plane of the side-plate ends
and its east corner about 0.45 in. inside. As drawn (scaled), the west corner is level with the
side-plate end. Inside the recess, the room between the west flange tip and the west side plate is
about 4.1 in.

In plain terms: with the girder where the drawings put it, the bottom flange could slide 6 in. or
more sideways (perpendicular to the girder) without hitting a side plate, but only by a margin of
roughly 0.4 in. (zero as drawn). If the girder end is about 0.4 in. or more closer to the column
than detailed (girder elongation, fit-up tolerance, or a push that is not perpendicular to the
girder), the west flange corner is inside the recess and meets the west side plate after about
4.1 to 4.2 in. of westward travel, short of the 6.25 in. needed. The drawings alone do not decide
it; the girder's axial position at the time does. This is an inference from the drawings, not
something they state.

**Q13 (bearing-face orientation).** Column 79 is not on the building grid. Its axes are rotated
about 12.3 degrees (2 5/8 in 12) clockwise, square to girder A2002 on its south side, and girder
A2001 meets its north face 7/8 in 12 (4.17 degrees) off square. Column 44 is on the grid and A2001
meets its web 3 9/16 in 12 (16.5 degrees) off square. E12/13 gives the A2001 skew to the grid as
3 9/16 in 12 (16.5 degrees), not 14.6 degrees. The 7/8 in 12 and 3 9/16 in 12 bevels are written
on the drawings; the 12.3 degree column rotation is inferred from three members.

## Sheets used

| Sheet | Title (as written) | Revision | Scan |
|---|---|---|---|
| Frankel 1091 | Col. 79, 7th, 8th & 9th tier; contract 84-152 | 2 (rev 1 May 10/85 HSS; rev 2 May 23/85 GP) | `raw/FOIA12-009_1091.TIF` |
| Frankel 9114 | Beam to col. connections, core; contract 84-15 | 2 (rev 1 "Rev as shown" Apr 17/85 HL; rev 2 "To approval" May 13/85 BF); "July 8/85E" | `raw/FOIA12-009_9114.TIF` |
| Frankel E12/13 | 12th & 13th floor framing plan, 7th tier | 4 (1: 4/19/85 to approval; 2: 5/8/85 derrick support bms @ 13th; 3: 5/23/85 X26 opening @ col 66; 4: Aug 12/85 note for add. studs); "July 5/85E", "Aug 28/85E" | `raw/FOIA09-49_E12_13.tif` |
| Frankel 1370 | Columns (6 & 7th tier) (zone 2), column 44; contract 84-152 | 1 (11 June 85, MK) | `raw/FOIA09-49_1370.tif` |
| Frankel 9102 | Beam to column connections (north & south walls) | 4 (1: Apr 17/85; 2: May 13/85; 3: May 15/85 conn. capacity; 4: May 29/85) | `raw/FOIA12-009_9102.TIF` |
| Frankel 9100 | Conn. plan for 8th to 21st fl. (key plan) | 3 (July 18/85) | `raw/FOIA12-009_9100.TIF` |
| Cantor S-8 | Typ. floor framing plan, 8th to 20th & 24th to 45th | H (8-5-85) | `raw/FOIA11-209_S-8.tif` |
| Cantor S-8-10 | title block not read; same plan with floor 10 changes in revision clouds | not read | `raw/FOIA11-209_S-8-10.tif` |
| Steel Structures Corp. 3004, 3005, 3016 | Beams 8th to 21st fl. | not read | `raw/FOIA09-49_3004.tif`, `raw/FOIA09-49_3005.tif`, `raw/FOIA09-49_3016.tif` |

9100 (key plan, NE corner) assigns the column 79 end of A2001 to "DWG 9114" and the column 44 end
to "DWG 9102" (crop `9100_connection_key_plan_NE_corner.png`; clearly legible). 1091 lists
"REF. DWGS. E12/13; 14/15; 16/17; E117A; 9114".

## (a) Column 79 at floor 13

Floor assignment (shown, 1091 left elevation and column note, clearly legible): piece A1091
(DIV 1303) spans from 3'-6" above the 11th floor to 3'-6" above the 13th floor; the upper
connection level is marked "FIN. FLR. (13th, 15th, 17th)", so for A1091 it is floor 13. The same
details repeat at the middle level (floor 12).

### Shown

| Item | Reading | Where | Confidence | Crop |
|---|---|---|---|---|
| Column section | "W 22 3/8 x 17 7/8 x 3 1/16 @ 730 x 25'-6 (M.2.E.) (A572-GR50)", i.e. W14x730 | 1091, column note along the right of the left elevation, box (4250,1150)-(4700,4500); BOM line 21 "1303 A1091 ... W14x730 A572GR50 25'-6" | clearly legible | `1091_col79_column_designation_W14x730_plus_PL26x2.png`, `1091_bill_of_material_left.png` |
| Side (cover) plates | "2/PL's 26 x 2 x 25'-6 pa-A (mill 2 ends with col.) (A572-GR50)" and "2-PL's paa-B (... & prep. I.E.)"; BOM lines 02 (PAA, 4 PL 26 x 2 x 25'-6) and 03 (PA, 2 PL 26 x 2 x 25'-6). E12/13 at column 79: "W22 3/8 x 730 + PL's 26 x 2, A1091" | 1091 column note and BOM (upper right of lower half); E12/13 NE quadrant | clearly legible | as above; `E12-13_girder_A2001_col79_half.png` |
| Plate position | Welded across the flange tips, making a box; drawn about centred on the column depth, projecting past both flange faces (1091 Sections A-A and B-B; 9114 plans) | 1091 upper right; 9114 left panel | clearly legible (as drawn, no dimension) | `1091_col79_section_A-A_column_side_plates_x2.png` |
| Projection past flange face | No dimension found | 1091, 9114 | not legible (not dimensioned) | |
| Seat plate "pf" | BOM line 07: PF, 6 pieces, PL 8 1/4 x 1 x 1'-0, 44W (G40.21). 9114 elevation: "1" PL". Drawn in 1091 Section A-A as a plate rotated with the girder, reaching back to the north flange face across the recess and lying on "pg" | 1091 BOM; Section A-A box (4824,144)-(6100,1600); 9114 elevation | clearly legible | `1091_bill_of_material_left.png`, `1091_col79_section_A-A_seat_pf_pg_detail_x2.2.png`, `9114_col79_elevation_seat_and_pg_x2.5.png` |
| Seat support "pg" | BOM line 08: PG, 6 pieces, PL 14 x 2 x 1'-6 7/8, "GRD TO BEAR". 9114 elevation: "PL 14 x 2 x 1'-6 7/8", welded "3/8 [fillet] 14, typ @ both side PL's". Placed across the outer ends of the two side-plate projections, below the seat, 14 in. deep ("1'-2" on the 1091 north-face elevation); overlaps each side plate end by "1/2" | 1091 BOM, Section A-A, north-face elevation; 9114 elevation and seat plan | clearly legible | `1091_col79_section_A-A_seat_pf_pg_detail_x2.2.png`, `9114_col79_seat_conn_elevation.png`, `9114_col79_seat_conn_plan_at_seat.png` |
| Other seat stiffener | None shown besides pg | 1091, 9114 | clearly legible (absence) | |
| Seat bolts and holes | "2-7/8 dia x 3 1/4" at the seat (1091 north-face elevation); 9114 notes "All bolts 7/8 dia HT A325, friction value 10.5 kips/bolt". Hole size not called out at the seat; sheet defaults "HOLES 15/16 dia U/N" (1091) and "OPEN HOLES 15/16 dia" (9114). Gauge "5 1/2". Holes at "(5 13/16)" and "(6 3/16)" from the north flange face, at "4" and "1 1/2" either side of the column centreline; girder centreline "1 1/4" off the column centreline at the bolt line; bolt line "1'-5 1/4" from the column centre along the girder axis (bracketed dimensions are "based on accurate col sizes") | 1091 Section A-A and left elevation; 9114 seat plan and notes | clearly legible (hole size by sheet default) | `1091_col79_section_A-A_seat_pf_pg_detail_x2.2.png`, `9114_col79_seat_conn_plan_at_seat.png` |
| Top clip angle | BOM line 10: AA, L 6 x 4 x 3/8 x 0'-9". 9114: "L6x4x3/8 (LLH)" with "3/8 shims loose". 1091: "1-Laa", "2-7/8 dia x 3". Vertical leg on the north flange face inside the recess (1091 Section B-B). Holes at "(3 9/16)" and "(3 15/16)" from the flange face, "3 13/16" and "1 11/16" either side of the column centreline, gauge "5 1/2"; bolt line "1'-3" from the column centre along the girder (9114 top plan) | 1091 BOM, Section B-B box (6050,150)-(7150,1500); 9114 left panel top plan and elevation | clearly legible | `1091_col79_section_B-B_clip_angle_level_plan.png`, `1091_col79_section_B-B_clip_angle_dims_x2.png`, `9114_col79_seat_conn_plan_at_top_clip_angle.png`, `9114_col79_elevation_clip_angle_and_girder_end_x2.5.png` |
| Clip angle hole or slot size | No slot callout for the column 79 angle on 1091 or 9114; sheet default 15/16 in. round holes. (For comparison, the column 44 top plate is called out with "1 1/8 x 15/16 slots", 1370, and "slots 15/16 x 1 1/8 in top PL only (bolts wrench tight)", 9102.) | 1091, 9114 title blocks | clearly legible (default; no explicit callout) | `1091_title_block_revisions.png`, `9114_general_notes_and_title_block.png` |
| Girder end stiffeners | "PL 5 1/2 x 3/4 x 1'-6 (BS)", both sides of the web at the column 79 end, from the bottom flange up; fillet welds "5/16" and "3/8" | 9114 left panel elevation | clearly legible | `9114_col79_seat_conn_elevation.png` |
| Girder end position | 9114 seat plan: "4 1/4" from the seat bolt line to a line skewed with the girder at which the girder outline (web and flange edges) starts, read as the girder end; "3/4" between that line and a second parallel line further from the column (most likely the near face of the end stiffener). The bolt line is "1'-5 1/4" from the column centre | 9114 left panel bottom plan, box (750,2550)-(1450,3150) | partly legible (figures clear; which line is the girder end is my reading) | `9114_col79_seat_plan_girder_end_side_plate_x2.png`, `9114_col79_seat_plan_dim_4-1-4_bolt_line_to_girder_end_x3.png`, `9114_col79_seat_plan_dim_3-4_between_girder_skewed_lines_x3.png` |
| Gap girder end to column face | No gap dimension written | 1091, 9114 | not legible (not dimensioned) | |
| Girder line | The A2001 centreline passes through the column 79 centre at "7/8 in 12" to the column axis (1091 Sections A-A and B-B; 9114 both plans) | as above | clearly legible | `1091_col79_section_A-A_seat_level_plan.png` |
| Connection data | 9114: "Col. seat conn @ 79 (W14x730 + side PL's 1", 2" or 3"), core. For W33x130, 45'-7 5/8 span. Reaction 146 kip. Conn. capacity = 150 k"; "Conn's are for 8th to 21st fl. only u/n" | 9114 left panel text | clearly legible | `9114_col79_notes_span_reaction_capacity.png` |

### Inferred

- **Projection of the side plates:** (26 - 22 3/8)/2 = 1 13/16 in. (1.81 in.) past each flange
  face if centred, as drawn. With the AISC depth of 22.42 in. it is 1.79 in. Scaled from the
  drawings: 1.65 to 1.95 in. **Inferred.**
- **Check on the geometry reading:** with the girder line through the column centre at 7/8 in 12
  and the bolt lines at 1'-5 1/4 (seat) and 1'-3 (clip angle) along it, the hole positions come
  out at 5.82 and 6.22 in. (seat) and 3.57 and 3.97 in. (clip) from the flange face, and 4.00,
  1.50, 3.84 and 1.66 in. off the column centreline. The drawing's bracketed values are 5 13/16,
  6 3/16, 3 9/16, 3 15/16, 4, 1 1/2, 3 13/16 and 1 11/16. All agree within 1/32 in.
- **Girder end (dimension based):** 1'-5 1/4 minus 4 1/4 puts the end 13.0 in. from the column
  centre along the girder axis, i.e. 1.78 in. from the north flange face at the girder centreline,
  0.03 in. short of the 1.81 in. projection (flush). With the end square to the girder (as drawn)
  and a 5.75 in. flange half-width, the west flange corner is 2.20 in. from the face (0.38 in.
  outside the plane of the side-plate ends) and the east corner 1.36 in. from the face (0.45 in.
  inside). **Inferred.**
- **Girder end (as drawn):** scaled from the 9114 seat plan at 200 dpi (detail at about
  1 in. = 1 ft), the end is about 1.4 in. from the flange face at the centreline, the west corner
  about 1.7 in. (level with the drawn side-plate end) and the east corner about 1.1 in. This agrees
  with the dimension-based position within about 0.4 in. **Inferred (scaled).**
- **Lateral room in the recess:** the clear width between side plates is the flange width,
  17 7/8 in. At the girder end the girder centreline is 0.95 in. east of the column centreline, so
  the west flange tip is at E' = -4.79 in. and the west side plate's inner face at -8.94 in.:
  4.15 in. of room. East side: 2.26 in. **Inferred.**
- **Walk-off distance:** the 12 in. seat is drawn centred on the girder, so the web's far face
  leaves the seat after 6 + 0.29 = 6.29 in. of movement perpendicular to the girder (NIST errata:
  6.25 in.). **Inferred.**
- **Could the bottom flange move 6 in. west without hitting a side plate?** Moving
  perpendicular to the girder axis takes the girder end slightly away from the column (by 0.07 in.
  per inch of travel), so from the detailed position the west corner stays outside the side-plate
  ends and the move is not blocked. A move due west on the building grid has a component of 0.21 in.
  toward the column face per inch (because the column is rotated 12.3 degrees); from the detailed
  position the west corner would enter the recess after about 1.8 in. and reach the west side plate
  after about 4.2 in. Any axial shift of the end toward the column of more than about 0.4 in. has
  the same effect. **Inferred.**

## (b) Orientation of the bearing faces

### Shown

| Item | Reading | Where | Confidence | Crop |
|---|---|---|---|---|
| A2001 to column 79 | Bevel "12 / 7/8" between the girder and the column axes in both 9114 plans; "7/8 / 12" in 1091 Sections A-A and B-B; a "12 / 7/8" bevel triangle beside A2001 at the column 79 end on E12/13 | 9114 left panel; 1091 upper right; E12/13 at column 79 | clearly legible (9114, 1091); partly legible (E12/13) | `9114_col79_seat_conn_plan_at_seat.png`, `1091_col79_section_A-A_seat_level_plan.png`, `E12-13_girder_A2001_col79_end_bevel_7-8_in_12_x1.6.png` |
| Seat plate pf at column 79 | Drawn rotated to align with the girder; pg and the side plates square to the column | 1091 Section A-A; 9114 seat plan | clearly legible (as drawn) | `1091_col79_section_A-A_seat_pf_pg_detail_x2.2.png` |
| Other members at column 79 | 1091 Section A-A: the south flange takes a beam on 2 angles "L's 50KC" (BOM: L 4 x 3 x 3/8 x 1'-2 1/2) with no bevel; this is A2002, "W26 7/8 x 94" in the 1091 elevation and "W27x94" on E12/13. The west side plate takes bent plates A778/B778 at "5 5/16 / 12"; this is the W36x135 ("W35 1/2 x 135") | 1091 Section A-A | clearly legible | `1091_col79_section_A-A_south_flange_L50KC_x2.png`, `1091_col79_section_A-A_seat_level_plan.png` |
| Grid bevels on E12/13 | A2001: "12 / 3 9/16" with "45'-7 5/8" on the hypotenuse. A2002 (W27x94): "12 / 2 5/8" with "33'-10 3/8". W36x135 west of column 79: "12 / 2 7/16" with "45'-0 1/2" | E12/13 NE quadrant | clearly legible | `E12-13_girder_A2001_bevel_3-9-16_in_12_span_45-7-5-8_x2.5.png`, `E12-13_A2002_W27x94_bevel_2-5-8_in_12.png`, `E12-13_W36x135_bevel_2-7-16_in_12.png` |
| Column 79 symbol | Drawn rotated on E12/13 and on the 9100 key plan (hand-drawn symbol; its side lines lean about 10 to 14 degrees clockwise, scaled) | E12/13 at column 79; 9100 | partly legible (symbol only) | `E12-13_col79_symbol_x3.png`, `9100_connection_key_plan_NE_corner.png` |
| Column 44 section | "1, W14X665, X 25-6 00, A36, M2E COL" and "(W 21 5/8 x 17 5/8 x 2 13/16 @ 665)", DIV 1105 and 1305; the upper level is "(FIN. 11TH FLOOR) (FIN. 13TH FLOOR)". E12/13: "A1370 W21 5/8 x 665". 9102 says "W14x550 min" (generic) | 1370 elevation text; E12/13 | clearly legible | `1370_full_sheet_col44_tiers6-7.png` |
| Column 44 orientation | Sections A-A and B-B (CAD, sharp): web parallel to the north wall, flanges perpendicular to it; spandrel girders W36x300 ("GIRDER A", "GIRDER B") connect to the flanges with plates B752. A2001 enters the recess between the flanges from the south at "12 / 3 9/16". A "7/16" offset is dimensioned between the girder line and the column centreline | 1370 right side, Sections A-A box (5350,1250)-(7050,2580) and B-B box (5550,2650)-(7050,3550) | clearly legible | `1370_col44_section_A-A_top_plate_level.png`, `1370_col44_section_A-A_centre_x2.png`, `1370_col44_section_B-B_seat_level.png` |
| Column 44 seat parts | 1370 material list: PA, PL 7 1/2 x 3/8 x 1'-0 1/2 (top plate, "1 1/8 X 15/16 SLOTS"); PB, PL 8 1/2 x 3/4 x 1'-0 1/2 ("CUT TO FIT" between the flanges, square to the column); PC, PL 7 x 1 x 1'-9 (stiffener under the seat, drawn along the girder web, i.e. skewed); seat holes "15/16 (7/8 DIA. A325)". 9102 column 44 detail: "PL 6 x 3/8" top plate, "PL 3/4" seat, "PL 7 x 1 x 1'-9", "3 9/16 / 12"; "For W33x130, 45'-7 5/8 span, reaction = 127 kip, conn. capacity = 132 kip" | 1370 material list (upper right) and sections; 9102 third panel | clearly legible | `1370_material_list.png`, `9102_col44_seat_conn_plan_at_seat.png`, `9102_col44_seat_conn_elevation.png`, `9102_col44_seat_conn_notes.png` |
| A2001 flange at column 44 | 9102 plans draw the girder's west flange edge cut back near the end to clear the column flange; no dimension found | 9102 column 44 plans | partly legible | `9102_col44_seat_conn_plan_at_top_plate.png` |
| Beam end cuts | Steel Structures 3004 (W24x55 beams A3004, B3004, C3004, K3004) clips the west (girder) ends at "12 / 3 9/16"; 3016 cuts P3016 (W12x26) at "3 9/16 / 12"; 3005 cuts G3005 at "3 9/16 / 12" | 3004, 3005, 3016 | clearly legible | `3004_full_sheet_W24x55_beams_end_bevel_3-9-16.png`, `3016_full_sheet_P3016_W12x26.png` |

### Inferred

- **Girder skew to the grid:** 3 9/16 in 12 = 16.53 degrees. Cross-checks: E12/13 north-south
  bays converted to lengths along the girder (4'-0 to 4'-2 1/16; 8'-1 7/16 to 8'-5 5/8;
  9'-7 3/8 to 10'-0 3/8) all give 16.5 degrees; the column stations 288'-0 1/2 (col 44) and
  275'-0 5/8 (col 79) with the 43'-9 1/2 north-south distance give 16.52 degrees; the drawn line on
  the scan measures 16.8 degrees (beams within 0.13 degrees of horizontal). On Cantor S-8, the sheet
  NIST's April 2012 errata gives as the basis of Fig. 8-16, the drawn girder line measures about
  16.2 degrees (scaled from the scan, rough line fit). Not 14.6 degrees.
- **Column 79 rotation:** 16.53 - 4.17 = 12.36 degrees, which matches A2002 at 2 5/8 in 12
  (12.34 degrees) framing square into the south flange, and the W36x135 at 2 7/16 in 12 to east-west
  (11.48 degrees) meeting the west side plate at 12.34 + 11.48 = 23.82 degrees against the written
  5 5/16 in 12 (23.88 degrees). So column 79's axes are rotated about 12.3 degrees clockwise from
  the grid, and its north bearing face (flange, and pg below the seat) is 4.17 degrees off square to
  A2001: neither on the grid nor square to the girder.
- **Seat plates:** column 79, pf is aligned with the girder; column 44, PB is aligned with the
  column (on the grid) and its stiffener PC with the girder.
- **Column 44:** on the grid; A2001 bears toward the web face, which is parallel to the north wall,
  at 16.5 degrees off square.

## (c) Girder piece drawing

- **Not obtained.** The girder's erection mark is A2001 (E12/13), so its shop drawing would be
  2001 in Frankel's 2000 series. The FOIA 12-009 set on archive.org has no 2001; the only
  2000-series file, `2000.TIF`, is a column sheet ("Column (19th tier) (zone 3)", column 57).
  Length, end cut, hole layout and any notes on the girder piece are therefore not available.
- **9114 is not the girder piece drawing.** It is "Beam to Col. Connections, Core" (connection
  details for floors 8 to 21). What it shows about the girder at the column 79 end (rev 2,
  clearly legible unless noted):
  - "For W33x130, 45'-7 5/8 span; reaction 146 kip; conn. capacity 150 k".
  - End stiffeners "PL 5 1/2 x 3/4 x 1'-6 (BS)": 3/4 in. thick, 5 1/2 in. wide, 18 in. high,
    both sides of the web, from the bottom flange up, welds 5/16 and 3/8 fillet. Position: the
    "3/4" in the seat plan appears to set the stiffener 3/4 in. from the girder end (partly
    legible; inferred).
  - End cut: drawn square to the girder axis in both plans (partly legible, as drawn).
  - Girder end 4 1/4 in. from the seat bolt line (see (a); partly legible).
  - No shear studs are shown on 9114 (none would be expected on a connection sheet).
- **9102 (column 44 end):** "For W33x130, 45'-7 5/8 span; reaction = 127 kip; conn. capacity =
  132 kip"; west flange edge drawn cut back near the end (partly legible).
- **Studs on the girder:** E12/13 labels A2001 "W33 x 130 [1"]" (1 in. camber) with no stud count
  (clearly legible). S-8 rev H: "W33x130 [1"]", no stud count (clearly legible). S-8-10 (floor 10
  only): "<30>" beside the girder inside a revision cloud, second digit partly covered by the cloud
  line (partly legible).
- **Web openings:** S-8 marks two openings on the A2001 line near column 44, "2'-0" x 1'-2" OPNG.,
  centre -1'-9"" and "3'-2" x 1'-6" OPNG., centre -1'-9"", located with "3'-0"" and "5'-0""
  dimensions; E12/13 carries the same callouts. Exact stations partly legible.

## (d) Erection drawing E12/13

Sheet facts (clearly legible): "12th & 13th floor framing plan", 7th tier, Frankel contract 84-15,
north arrow up. Notes: "Fin. conc. slab 12th floor el. 452'-9"; "13th floor el. 465'-6"; "Top of
steel 5 1/2" below fin. conc. slab u.n."; "<...> indicates 3/4 dia x 5 shear studs, field
applied"; "[...] indicates camber"; "For general notes see E120"; note 4 "For additional studs see
Cust. Dwg. S8 Rev. 1". Crops: `E12-13_notes_and_stud_legend.png`, `E12-13_revision_block.png`.

Location on the sheet: north-east corner, raw box (8700,700)-(11500,3700) in the FOIA 09-49 scan.

- **Girder:** mark A2001, "W33 x 130 [1"]", from column 44 (piece A1370, "W21 5/8 x 665") to
  column 79 (piece A1091, "W22 3/8 x 730 + PL's 26 x 2", marked * for A572 Gr. 50). Clearly
  legible. Crop `E12-13_NE_quadrant_girder_A2001.png`.
- **Skew:** bevel triangle "12 / 3 9/16" with "45'-7 5/8" (16.53 degrees to the north-south grid).
  Clearly legible. Crop `E12-13_girder_A2001_bevel_3-9-16_in_12_span_45-7-5-8_x2.5.png`.
- **Girder stud count:** none shown. Clearly legible (absence).
- **Members framing into A2001**, in order from column 44. "Along girder" values are the written
  segment lengths on the girder line and their running sum; "N-S" values are the written
  north-south dimensions from the column 44 line (4'-0, 8'-1 7/16, then 9'-7 3/8 "(TYP)").

| From col 44 | Mark | Size | Studs | Camber | Length (as written) | Side | Segment along girder | Station along girder | N-S from col 44 line | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | G3005 | W21x44 | <24> | [1 3/4] | 50'-8 1/4 | east | 4'-2 1/16 | 4'-2 1/16 | 4'-0 | clearly legible |
| 2 | A3004 | W24x55 | <28> | [2] | 51'-4 1/4 | east | 8'-5 5/8 | 12'-7 11/16 | 12'-1 7/16 | clearly legible |
| 3 | B3004 | W24x55 | <28> | [2] | 52'-1 3/4 | east | 10'-0 3/8 | 22'-8 1/16 | 21'-8 13/16 | clearly legible |
| 4 | P3016 | W12x26 | <14> | none shown | 26'-9 | west (runs north-south from the north wall) | 4'-2 1/4 | 26'-10 5/16 | not dimensioned | clearly legible (segment partly legible) |
| 5 | C3004 | W24x55 | <28> | [2] | 52'-11 1/4 | east | 5'-10 1/16 | 32'-8 3/8 | 31'-4 3/16 | clearly legible |
| 6 | K3004 | W24x55 | <28> | [2 1/4] | 53'-8 and a fraction | east | 10'-0 3/8 | 42'-8 3/4 | 40'-11 9/16 | length fraction not legible |
| end | column 79 | | | | | | 2'-10 3/8 | 45'-7 1/8 (sum) | 43'-9 1/2 | segment partly legible |

  Stations and N-S running totals are sums of the written values (inferred). Crops:
  `E12-13_girder_A2001_col44_half.png`, `E12-13_girder_A2001_col79_half.png`,
  `E12-13_girder_A2001_first_segment_4-2-1-16_x2.6.png`,
  `E12-13_girder_A2001_mid_segments_4-2-1-4_5-10-1-16_x2.6.png`,
  `E12-13_girder_A2001_col79_end_segments_x2.6.png`,
  `E12-13_east_beams_framing_into_A2001_labels.png`.

- **Not into the girder:** three short W12x19 members marked S3007, G3007 and K3007 ("W12x19
  (-7 1/2)", spandrel brace beams per the E12/13 notes) run from the north wall to G3005.
  Partly legible. Crop `E12-13_NE_corner_G3005_and_W12x19_braces.png`.
- **Unresolved:** the written segments sum to 45'-7 1/8, against "45'-7 5/8" on the bevel
  triangle and in 9114 and 9102, and against 45'-8 1/8 between column centres from the north-south
  and east-west stations. The last segment "2'-10 3/8" (partly legible) is about 1 in. shorter than
  the 2'-9 15/16 north-south dimension converted along the girder (2'-11 3/8). Not resolved from
  the drawings.
- **S-8 cross-check (rev H):** same framing in the NE bay, beams "W24 x 55 <28>", "W21 x 44 <24>",
  "W12x26 <14>"; girder "W33x130 [1"]" without studs. S-8-10 (floor 10) shows the east beams at
  <32> and the girder at <30> (partly legible). Crops `S-8_rev-H_NE_framing_girder_W33x130_north_up.png`,
  `S-8-10_NE_framing_girder_W33x130_studs_north_up.png`, `S-8-10_girder_stud_label_zoom_north_up.png`.

## Secondary claims (not from the drawings)

These are what other parties say. None was used for the readings above.

- **NIST, NCSTAR 1-9 Section 8.8 (p. 351 and 352, local text `sources/text/ncstar1-9.txt`):**
  "For Column 79, the flange on the north face and the extending portions of the side cover plates
  were modeled to allow for contact with the girder." In the partial-floor LS-DYNA model,
  "Continued axial expansion of the girder caused it to bear against the face of Column 79".
- **NIST errata, June 2012:** seat at column 79 corrected from 11 in. to 12 in. "consistent with
  Frankel drawing 1091"; walk-off 6.25 in. lateral ("from the flange tip to the far side of the
  web") and 5.5 in. axial.
- **NIST e-mail of 2013-10-25 (quoted by AE911Truth, not seen in the original):** drawings used
  for NCSTAR figures (Fig. 8-21: 1091, 9114; Fig. 8-23 and 8-26: 1091, 3004, 9114; Fig. 8-27:
  E12-13; Fig. 12-25: 1091, 9114, E12-13); the 9114 web stiffeners "prevent web crippling" and
  were not modelled.
- **NIST letter of 2020-08-28 denying AE911Truth's request for correction:** "The Girder A2001 and
  Column 79 connection locates the bolts on a seated connection attached to the exterior edges of
  the Column 79 side plates, with the girder axis at a slight angle to Column 79." Also: the partial
  height web stiffener on 9114 was not included in the preliminary analyses.
- **UAF report (Hulsey, Quan, Xiao, March 2020, p. 77 to 79, 71, 87):** side plates protrude
  "nominally 1.79 inches"; 17.89 in. between side plates; 12 in. seat, flange 11.510 in. "centered
  on the seat", 6.290 in. needed to walk off; "girder and bearing seat are slightly off center to
  the east, with just 3.678 inches between the girder's western edge and Column 79's western side
  plate"; when heated the girder "expands axially towards column 79, such that it becomes trapped
  behind the side plate on the western side of Column 79"; with NIST's boundary conditions and the
  side plates removed, the westward displacement relative to column 79 is 5.11 in.; Arup's analysis
  (Aegis litigation) is said to show trapping "after less than 4 inches of lateral travel". Its
  Figures 3.5 and 3.6 are redrawn from 9114 ("figure prepared by Brookman, 2012").
- **AE911Truth request for correction, 2020-04-15 (p. 8 to 14):** repeats the UAF figures; a table
  gives the west corner of A2001 0.158 in. outside the side-plate protrusion at 21 degrees C,
  moving inside it after about 0.19 in. of elongation toward column 79 (about 70 degrees C, taking
  half the expansion of a 540 in. girder); cites NCSTAR Figs. 8-23 and 8-26 as showing the girder
  trapped in NIST's partial-floor model.
- **AE911Truth "Technical Discussion" (archive.org, 2014):** seat pf is 12 in. per 1091; argues
  the axial bearing length is 6.25 in.; notes the 9114 stiffeners and the W12x19 braces S3007,
  G3007 and K3007 to G3005 as omitted from NIST's models.
- **R. Gage letter to the NIST Director, 2018-10-29:** "the 2000 series, which shows the girders in
  question, was not included in that release" (FOIA 12-009).
- **Metabunk thread "Could Girder A2001 Possibly Have got Past the Side Plate on Column 79?"
  (September 2017):** T. Szamboti: plates "2" thick x 26" wide"; "The western corner of girder
  A2001 was about 1.8 inches from the column flange" and "the side plates protruded about 1.8
  inches"; once heated the girder is "inside the envelope of the side plates" and is stopped after
  about 3.6 in. of westward travel; girder length "531.625"". Christopher 7: 22.4 x 17.9 in. column,
  1.8 in. protrusion. Others argue the girder was cooling when NIST found walk-off and could have
  been clear of the side plates, and that NIST's 6.25 in. movement "misses the side plate".

Comparison with this reading: the secondary sources that place the girder end (Szamboti, the
AE911Truth table) also put the west corner at, or 0.16 in. outside, the end of the side plates at
room temperature, which agrees with the drawings within the reading uncertainty. Their 3.68 in.
lateral gap is smaller than the 4.15 in. derived here. My interpretation (not stated by them): the
3.68 in. matches an eastward offset of the girder line of about 0.49 in., whereas the offset at the
girder end is 0.95 in. (it grows from 0 at the column centre because of the 4.17 degree skew).

## What could not be obtained or read

- The A2001 girder piece drawing (Frankel 2001): not in the archive.org copy of FOIA 12-009, and
  reported by AE911Truth as not released. Girder length, end cut and hole positions from the
  girder side are therefore not available.
- An explicit dimension for the side-plate projection or for the gap between the girder end and
  the column 79 face: none is written on 1091 or 9114; both are derived above.
- The fraction of the K3004 length on E12/13, and a certain reading of the last girder segment
  near column 79.
- 911datasets.org did not resolve during retrieval.

## Crops index

All in `crops/`. Sheet name first, then subject. Scale factors in names are relative to the raw
scan (200 dpi for Frankel and Steel Structures sheets, 300 dpi for E12/13, 400 dpi for S sheets).
Full-sheet overviews: `1091_full_sheet_col79_tiers7-9.png`, `9114_full_sheet_core_connections.png`,
`E12-13_full_sheet.png`, `1370_full_sheet_col44_tiers6-7.png`,
`9102_full_sheet_north_south_wall_connections.png`. Title blocks: `1091_title_block_revisions.png`,
`9114_general_notes_and_title_block.png`, `9102_title_block_revisions.png`,
`9100_title_block_revisions.png`, `1370_title_block.png`, `E12-13_revision_block.png`,
`S-8_rev-H_revision_rows.png`.
