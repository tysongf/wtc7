<!-- Extracted 2026-11-02 from sources/text/ncstar1-9.txt, ncstar1-9a.txt, ncstar1a.txt and wtc7_faq.txt by a delegated reading pass. Spot-checked against the text: the classic removal case (1-9 12.4.7), the 2.25 s stage (1-9 12.5.3), the 1A statement that column 79's buckling initiated collapse, and the 8-week, 12-CPU run time (9A). Every other value is to be checked against its cited page before it is used. -->

# WTC 7 Phase 3: what NIST published that a whole-building frame model needs

Fact sheet for the pre-registered Phase 3 study ("if Column 79 loses support, does the whole building collapse?"). Every value carries a citation. Nothing here is estimated; where NIST is silent the entry says **Not stated** and names where I looked.

## How to read the citations

| Tag | Document | Local files | PDF page to printed page |
|---|---|---|---|
| 1-9 | NIST NCSTAR 1-9 (Nov 2008), Vols 1 and 2 | `sources/nist/ncstar1-9.pdf`, `sources/text/ncstar1-9.txt` | Vol 1: printed = PDF - 44. Vol 2 (from PDF 405): printed = PDF - 66 |
| 9A | NIST NCSTAR 1-9A (global LS-DYNA analysis, ARA) | `ncstar1-9a.pdf/.txt` | printed = PDF - 51 |
| 1A | NIST NCSTAR 1A (final summary report) | `ncstar1a.pdf/.txt` | printed = PDF - 42 |
| FAQ | NIST web page "FAQs - NIST WTC 7 Investigation" | `sources/text/wtc7_faq.txt` | cited by question number |

Format: `[1-9 §2.4.2, PDF 57 (p. 13)]`. The PDF page is the page index in the file in `sources/nist/`; the text extracts were checked to map one-to-one to those page indices.

Markers used:
- **[read from figure]**: value taken from a plot, drawing or table image, not from NIST's prose. Approximate where it says so.
- **[derived]**: my arithmetic on NIST numbers, shown so it can be checked. Not a NIST statement.
- **Not stated**: searched for and not found in the four sources; where I looked is given.

The 1-9 errata text (`ncstar1-9_errata.txt`) and NCSTAR 1-3D were not consulted (outside the listed sources). The January 2009 text changes are bound into the front of the 1-9A PDF (PDF 2) and into 1-9 at PDF 599 (p. 533); they concern Table P-2, the SFRM paragraph in §11.4.1, and Appendix D references, none of which change a value below.

---

## 1. Structural system

### 1.1 Overall geometry

| Item | Value | Citation |
|---|---|---|
| Storeys | 47 | [1-9 §2.1, PDF 53 (p. 9)]; [1A §1.2, PDF 47 (p. 5)] |
| Height | ~610 ft (186 m) "from the ground floor to its roofline" | [1-9 §5.3.2, PDF 142 (p. 98)] |
| Plan shape | Trapezoid. North side 329 ft (100.3 m), south side 247 ft (75.2 m), east side 149 ft (45.0 m), west side 153 ft (46.7 m) | [1-9 §5.3.2, PDF 142 (p. 98)] |
| Plan width (other statements) | "140 ft wide" [1-9 §2.1, PDF 53 (p. 9)]; "44 m (144 ft) wide" [1A §1.2, PDF 47 (p. 5)]. See §6 inconsistencies | as cited |
| Core | Columns 58 to 78 form a 15.7 m x 48.2 m (51.5 ft x 158 ft) rectangular core, long side east-west, offset toward the west | [1-9 §5.3.2, PDF 142 (p. 98)] |
| Floor area | ~2 million ft2 | [1-9 §2.1, PDF 53 (p. 9)] |
| Exterior column centre lines | 0.61 m (24 in.) inward from the outer face of the curtain wall | [1-9 §5.3.2, PDF 144 (p. 100)] |
| Parapet | 1.3 m (4 ft) high around the roof | [1-9 §5.3.2, PDF 143 (p. 99)] |
| Con Edison substation | Pre-existing (1967) 3-storey steel frame with concrete floors and walls on the north side, extending ~40 ft beyond the north face [1-9 §2.3, PDF 56 (p. 12)]; "two story" section ~278 ft wide extending 42 ft [1-9 §5.3.2, PDF 142 (p. 98)]; 13 m (42 ft), two storeys, coinciding with the first two floors [1A §1.2, PDF 45 (p. 3)] | as cited |
| Floors 41 and 43 | East half originally removed for trading floors; restored by 2001; columns in those areas reinforced | [1-9 §2.4.2, PDF 60 (p. 16)] |

### 1.2 Storey heights and elevations

| Item | Value | Citation |
|---|---|---|
| Typical tenant floor | 3.89 m (12 ft 9 in.) slab to slab | [1-9 §5.3.2, PDF 143 (p. 99)]; confirmed from facade dimensions [1-9 §5.3.2, PDF 144 (p. 100)] |
| Mechanical floors (5, 6, 22, 23, 46, 47 in part) | "about 4 m to 4.5 m (about 13 ft to 15 ft)" | [1-9 §5.3.2, PDF 143 (p. 99)] |
| Floor 5 | 4.0 m (13.0 ft) slab to slab | [1-9 §3.3.2, PDF 93 (p. 49)] |
| Floor 6 | 4.0 m (13 ft) slab to slab | [1-9 §3.3.2, PDF 94 (p. 50)] |
| Floor 47 | Double-height space from Floor 46 to underside of roof on the north side (cooling towers) | [1-9 §2.4.2, PDF 62 (p. 18)] |
| Floor 6 | Openings forming a double-height mechanical space on the east side; Truss 1, Truss 2 and Column 80 were in it | [1-9 §2.4.2, PDF 60 (p. 16)] |
| Top of parapet (north face, at east edge of louvers) | +925 ft 4 in. | [1-9 §12.5.3, PDF 666 (p. 600)] |
| Tops of Floor 29 windows (north face) | approximately +683 ft 6 in.; difference "about 242 ft" = 18 storeys | [1-9 §12.5.3, PDF 666 (p. 600)] |
| Heights of Floors 1 to 4, 7, 22, 23, 46, 47 individually; floor elevations; datum of the +925 ft figure | **Not stated.** Searched all four sources for "floor-to-floor", "story height", "elevation", "+[0-9] ft" | |

### 1.3 Column lines and numbering

- 82 columns: 24 interior (58 to 81) and 58 perimeter (1 to 57 plus 14A, near the south end of the west face) [1A §1.2, PDF 47 (p. 5)]; "one of 82 columns" [1-9 §14.2, PDF 684 (p. 618)].
- Perimeter numbering starts at the northwest corner and runs counterclockwise [1-9 §5.3.2, PDF 142 (p. 98)]. Plan with numbers: [1-9 Fig. 5-7, PDF 142]; [1A Fig. 1-5, PDF 48]; [1-9 Fig. 2-3, PDF 58].
- Interior rows **[read from figure]** (Fig. 5-7 and 1A Fig. 1-5; same grouping in [1-9 Fig. 12-57, PDF 650 (p. 584)]):
  - North row, west to east: 58, 61, 64, 67, 70, 73, 76, then 79 further northeast.
  - Middle row: 59, 62, 65, 68, 71, 74, 77, then 80.
  - South row: 60, 63, 66, 69, 72, 75, 78, then 81.
  - NIST's horizontal-progression groups: Group 1 = 79-81, Group 2 = 76-78, Group 3 = 73-75, Group 4 = 70-72, Group 5 = 67-69, Group 6 = 58, 61, 64, 67, Group 7 = 59, 62, 65, 68, Group 8 = 60, 63, 66, 69 [1-9 Figs. 12-58, 12-59, PDF 651 (p. 585)].
- Columns 79, 80 and 81 "provided additional support for the long floor spans between the east side of the core and the east face" [1-9 §5.3.2, PDF 142 (p. 98)]; they were "designed to carry gravity loads only" [1-9 §8.6, PDF 386 (p. 342)]; they "were the only interior support for the gravity loads in the eastern region" [1-9 §14.3.4, PDF 690 (p. 624)]; spans "approximately 15 m (50 ft)" on at least one side [1-9 §14.5.2, PDF 694 (p. 628)].
- Column 79 tributary floor area "approximately 2000 ft2 per floor" [1-9 §12.4.7, PDF 660 (p. 594)].
- Column 44 (north face) is tied to Column 79 by a girder at each floor [1-9 §13.2 item 12, PDF 678 (p. 612)]; Column 55 tied back to the west edge of the core by a similar girder [1-9 §13.2 item 14, PDF 679 (p. 613)].

**East-side columns 76 to 81**

| Column | Position and framing | Section (where NIST gives one) | Supported below Floor 7 by |
|---|---|---|---|
| 79 | Isolated, northeast of core. N-S girder to exterior Col 44 (W33x130, 45 ft, no studs, seated both ends); E-W girder to Col 76 (knife connections on the 79 side, per ANSYS failure description); girder to Col 80 | Floor 14: W14x730 with two 26 in. x 2 in. side cover plates. Floor 5: W14x730 with two 26 in. x 3 in. side cover plates [1-9 App. D §D.2, PDF 760 (p. 694)] | No transfer element shown; Fig. 1-6 draws 79 as a free-standing column **[read from figure]** [1A Fig. 1-6, PDF 48]. Its foundation is **Not stated** in text |
| 80 | East of Col 77, middle row | Floor 14: "Column 80 or Column 76 at Floor 14, W14x730 with two 12.5-in. x 4-in. web plates" [1-9 App. D, PDF 760 (p. 694)] | Carries the east end of Truss 2 [1-9 §2.4.5, PDF 74 (p. 30)] |
| 81 | Southeast; seated (STC) girder on its south side to exterior Col 26 | Floor 14: W14x730 with two 12.5 in. x 1 in. web plates [1-9 App. D, PDF 760 (p. 694)] | No transfer element shown **[read from figure]** [1A Fig. 1-6, PDF 48] |
| 76 | Northeast corner of core | Floor 14: as for 80 (see above) | Truss 1 at Floor 7 [1-9 §2.4.5, PDF 74 (p. 30)] |
| 77 | East end of middle core row | Floor 14: W14x665 [1-9 App. D, PDF 760 (p. 694)] | Truss 2 [1-9 §2.4.5, PDF 74 (p. 30)] |
| 78 | East end of south core row | **Not stated** | Girder MG-23 at Floor 7, spanning Col 77 to Col 78A [9A §3.4.1, PDF 94 (p. 43)] |

Also: "Interior columns 58, 61, and 73 to 81 also had this massive section" (W14x730 with plates welded across the flange tips), floor range not given [1-9 §4.7.2, PDF 125 (p. 81)]; W14x500 "typical of a number of columns in the building core and the exterior" [same]. W14x730: depth 22.4 in., flange width 17.9 in., flange thickness 4.91 in., web thickness 3.07 in.; W14x665: 21.6, 17.7, 4.52, 2.83 in. [1-9 App. D Table D-1, PDF 760 (p. 694)]. Truss 2 diagonal: W14x730 with two 8 in. x 3 in. web plates; Truss 1 diagonal and Column 78A at Floor 5: W14x665 [1-9 App. D, PDF 760 (p. 694)].

### 1.4 Columns, splices, plates

| Item | Value | Citation |
|---|---|---|
| Interior columns | Rolled W shapes, Grade 36 or 50; heavier ones built up from W14x730 with side cover plates (box) or web plates; continuous fillet welds | [1-9 §2.4.4, PDF 72-73 (p. 28-29)] |
| Plate thickness and grade | 1.5 in. to 8 in.; "2<t<4 ASTM A588 Grade 50; 4<t<6 ASTM A572 Grade 42; t>6 ASTM A588 Grade 42" (as printed) | [1-9 §2.4.4, PDF 73 (p. 29)]; repeated [1-9 §11.2.2, PDF 526 (p. 460)] |
| Splices | Every two storeys; milled ends; splice plates welded or bolted to web and flanges (fillet welded to plates on built-up columns) | [1-9 §2.4.4, PDF 73 (p. 29)] |
| Exterior columns | Nominally W14, ASTM A36; splices similar to interior | [1-9 §2.4.4, PDF 73 (p. 29)] |
| Column 79 seat support | Seat plate at 79 "supported by a plate welded to the side cover plates on the lower stories"; seat at 81 stiffened | [1-9 §2.4.3, PDF 67 (p. 23)] |
| Column schedule by floor; which floors have splices | **Not stated** (only the App. D sections above). Searched "W14", "column schedule", "splice" in all sources | |

### 1.5 Floor framing and slabs

Typical tenant floors (8 to 20 and 24 to 45 identical framing; 21 to 23 slightly heavier) [9A §3.4.1, PDF 88-89 (p. 37-38)]:

| Item | Value | Citation |
|---|---|---|
| Slab | 3 in. deep 20 gage metal deck + 2.5 in. of 3,500 psi normal-weight concrete = 5.5 in. total; one layer 6x6 W1.4xW1.4 WWF (second layer over girders at slab edges); elevator lobbies 1.5 in. deck + 4 in. topping | [1-9 §2.4.2, PDF 57 (p. 13)] |
| Deck fastening | Not on drawings; "standard practice" puddle welds 12 in. o.c. at beams | [1-9 §2.4.2, PDF 57 (p. 13)] |
| Beams | 50 ksi; ~9 ft o.c. between core and exterior. North and east: W24x55, 28 studs, ~53 ft span. South: W16x26, 24 studs, 36 ft | [1-9 §2.4.2, PDF 58 (p. 14)] |
| Core girders | W16x31 to W36x135 | [1-9 §2.4.2, PDF 58 (p. 14)] |
| Northeast corner | Girder Col 79 to Col 44: W33x130, 13.7 m (45 ft), no studs, seats at both ends; floor beams 15.8 m (52 ft) with studs framing into it from the east side only | [1-9 §8.7, PDF 386 (p. 342)] |
| Floors 21 to 23 | Core girders ~one size heavier; south beams W16x31 instead of W16x26; extra studs on W24x55 (north and west) | [1-9 §2.4.2, PDF 59 (p. 15)] |
| Studs | 0.75 in. x 5 in., ~1 ft to 2 ft o.c.; none on girders (composite beams, non-composite girders) | [1-9 §2.4.2, PDF 59 (p. 15)]; FAQ Q27 explains the no-stud decision |
| Spandrels | Nominal 0.9 m (36 in.) deep W shapes between all perimeter columns | [1-9 §5.3.2, PDF 142, 145 (p. 98, 101)] |

Other floors:

| Floor | Slab / framing | Citation |
|---|---|---|
| 1 | 14 in. formed slab (No. 5 at 10-12 in. top, No. 6 at 9 in. bottom); 6 in. over the truck ramp | [1-9 §2.4.2, PDF 59 (p. 15)] |
| 2, 3, 4, 6 | 3 in. 20 ga deck + 3 in. concrete = 6 in.; Floors 2, 3 partial; Floor 4 large opening on the south | [1-9 §2.4.2, PDF 59-60 (p. 15-16)] |
| 5 | 11 in. 3,500 psi concrete on 3 in. 18 ga deck = 14 in.; No. 7 at 12 in. top both ways, No. 9 at 12 in. bottom; 36 ksi WT sections embedded as an in-plane diaphragm truss | [1-9 §2.4.2, PDF 60 (p. 16)]. 1-9 §12.2.2 says "15 in." [PDF 613 (p. 547)], see §6 |
| 7 | 5 in. concrete on 3 in. 18 ga deck = 8 in., No. 5 at 6 in. both ways; south regions 8 in. formed slab, two layers | [1-9 §2.4.2, PDF 60 (p. 16)]; [1A §1.2, PDF 48-49 (p. 6-7)] |
| 46 | Heavier framing: W36x150 between posts, W36x260 under posts (cooling towers, north); W21x44 / W36x150 (south setback); 6 in. slab in part of core and under cooling towers | [1-9 §2.4.2, PDF 62 (p. 18)] |
| Roof | Slab sloped 8.5 in. to 5.5 in.; WWF 6x6 W2.4xW2.4; diagonal WT6x9 under grating over cooling towers | [1-9 §2.4.2, PDF 65 (p. 21)] |

### 1.6 Transfer trusses and girders, Floors 5 to 7

Three transfer trusses and eight cantilever transfer girders between the Floor 5 and Floor 7 slabs [1A §1.2, PDF 47 (p. 5)]. Schematic: [1-9 Fig. 2-24, PDF 74]; [1A Fig. 1-6, PDF 48].

| Element | Carries | Supported by | Notes / members | Citation |
|---|---|---|---|---|
| Truss 1 | Col 76 | Col 73 (west); east side on a N-S transfer girder on Cols E3 and E4 at Floor 5 (1-9) / "to columns E3 and E4" (9A); E3 and E4 start at Floor 7 and go to the foundation | Moment connections for the E-W beam at Floor 5 into Col 73 and girder MG-53. Diagonal W14x665 (App. D) | [1-9 §2.4.5, PDF 74 (p. 30)]; [9A §3.4.1, PDF 93 (p. 42)]; [1-9 App. D, PDF 760] |
| Truss 2 | Col 77 and girder MG-23 (hence Col 78) | Col 74 (west), Col 80 (east) | Moment connections in the Floor 5 girder framing between Cols 74 and 80. Diagonal W14x730 + two 8x3 in. web plates | [1-9 §2.4.5, PDF 74 (p. 30)]; [9A §3.4.1, PDF 94 (p. 43)]; [1-9 App. D, PDF 760] |
| MG-23 | Col 78 | Col 77 (on Truss 2) and Col 78A (starts at Floor 7, to foundation) | Floor 7 | [9A §3.4.1, PDF 94 (p. 43)] |
| Truss 3 | Col 61 (1-9); "loads from Columns 61 and 62" (9A) | Cols 62 and 61A (1-9); Col 61A (9A) | Runs N-S; 10 ft cantilever 61 to 61A, 18 ft back span to 62; moment connections in Floor 5 and 6 girders | [1-9 §2.4.5, PDF 74 (p. 30)]; [9A §3.4.1, PDF 95 (p. 44)] |
| MG-21, MG-22 | Col 58 to 58A and 58C; Col 59 to 59A and 59B (all start at Floor 7) | | Built-up; stiffener plates included | [9A §3.4.1, PDF 96 (p. 45)] |
| Cantilever girders (MG-27 typical) | North-face columns 47 to 54 (1-9) or 47 to 53 (9A), offset 6 ft 9 in. south onto substation columns | North-side core columns, 46 ft back span; easternmost connected to Truss 1, westernmost to Truss 3 | Floor 7 | [1-9 §2.4.5, PDF 73 (p. 29)]; [9A, PDF 97 (p. 46)] |
| Hung columns | 2 columns above the south loading dock and 8 above the north Con Ed vault hang from the Floor 5 to 7 belt truss | | | [1-9 §2.4.6, PDF 75 (p. 31)] |

Member sizes of truss chords, verticals, MG-21/22/23/27/53, and truss geometry: **Not stated** (searched 1-9 Ch. 2, 9A §3.4.1, App. D).

NIST conclusion: "Neither the transfer elements (trusses, girders, and cantilever overhangs) nor the 'strong' floors (Floors 5 and 7) played a significant role in the collapse" [1-9 §14.2, PDF 684 (p. 618)]; [1A, PDF 90 (p. 48)].

### 1.7 Lateral system, diaphragms, belt trusses

- Above Floor 7: exterior moment frame; column trees on the east and west facades with bolted field splices at spandrel midspan; north and south spandrels with moment-resisting bolted flange and web connections [1-9 §2.4.6, PDF 74 (p. 30)].
- Perimeter belt truss at Floors 5 to 7 and Floors 22 to 24 [1-9 §2.4.6, PDF 74 (p. 30)] (1A says "around Floors 22 and 23", PDF 47, and "Floors 22 through 24", PDF 100).
- Below Floor 7: combined moment and braced frames around the exterior, braced frames in the core; Floors 5 and 7 diaphragms transfer in-plane loads to the core [1-9 §2.4.6, PDF 74-75 (p. 30-31)].
- Core above Floor 7 simply connected, laterally supported by the moment frame through floor diaphragm action [1-9 §8.6, PDF 386 (p. 342)].
- "Above Floor 7, there was no bracing, or other load redistribution mechanism, to transfer gravity loads between interior columns. The floor framing, which was the only load path between columns, could not redistribute loads between columns because the shear connections ... were only designed for transferring vertical shear loads." [1-9 §14.5.2, PDF 694 (p. 628)]; [1A §4.5.2, PDF 100 (p. 58)].

### 1.8 Roof, penthouses, hat truss

- East penthouse added 1989 (chiller plant, cooling towers); roof beams and girders under it reinforced with cover plates on lower flanges; thick concrete equipment pad; penthouse posts framed into existing interior Columns 76, 77, 79 and 80; other posts on roof beams [1-9 §2.4.2, PDF 65 (p. 21)]; plan [1-9 Fig. 2-14, PDF 66].
- Two enclosed penthouses (east, west) joined by two parallel screenwalls; five cooling towers extend down to Floor 46 [1-9 §5.3.2, PDF 143 (p. 99)].
- Penthouse kink located at Post 17, which sat on the roof girder spanning Column 79 to Column 44 [1-9 §8.3.2, PDF 372 (p. 328)].
- 9A and 1-9 Ch. 12 say the east penthouse was "supported by Columns 79, 80, and 81" [9A §4.3.3, PDF 130 (p. 79)]; [1-9 §12.4.4, PDF 642 (p. 576)] (differs from the post list above, see §6).
- Hat truss or outrigger at roof: **Not stated / none described.** Searched "hat truss", "outrigger" in all sources; the only hat truss mentioned is in the towers (FAQ Q13).
- Penthouse member sizes, roof equipment weights: **Not stated** (searched 1-9 §2.4.2, 9A §3.4.1).

### 1.9 Connections

Types [1-9 §2.4.3, PDF 66-67 (p. 22-23)]; [9A §3.3.1, PDF 73 (p. 22)]:

| Type | Where | Bolts (typical) |
|---|---|---|
| Fin (F), single shear plate | Beam to girder; girder to interior column | Up to 6 bolts [1-9 §11.2.5, PDF 542 (p. 476)] |
| Knife (K), double angle shop-welded to girder/column | Beam or girder to column | Up to 8 [1-9, PDF 543 (p. 477)] |
| Header (H), double angle shop-welded to beam web | Beam to girder or column | Up to 10 (5 per row) [1-9, PDF 544 (p. 478)] |
| SWC, seat + web clip | Core floor beams to girders | 2 erection bolts in seat, 2 in clip |
| STC, seat + top clip | Beams/girders to north and south face columns; girders to north side of Col 79 and south side of Col 81 | 2 in seat, 2 in top clip |
| STP, seat + top plate | Beams/girders to east face columns | 2 in seat, 2 in top plate |
| Moment | Exterior spandrels (wind girders, WG); some core girders at Floors 5 and 7 | 1 in. A490 for brace and moment connections [1-9 §2.4.2, PDF 59 (p. 15)] |

- Typical bolt in shear connections: 7/8 in. ASTM A325 [1-9 §2.4.2, PDF 59 (p. 15)].
- Design shear forces for typical connections from AISC beam tables for beams without studs, 1.5 times those values for beams with studs [1-9 §2.4.2, PDF 59 (p. 15)].
- Erection bolts in seats carried no gravity load; NIST found no evidence that girders or beams were welded to seats [1-9 §8.7.5, PDF 392 (p. 348)].
- Details taken from ~2,500 fabrication shop drawings [1-9 §2.4.3, PDF 66 (p. 22)].

Capacities used by NIST (room temperature, resistance factors 1.0) [1-9 §11.2.4, PDF 529-535 (p. 463-469)]:

| Item | Value |
|---|---|
| 7/8 in. A325 bolt, shear | 0.601 in2 x 75 ksi = 45 kip (Fnv = 60/0.8) |
| A490 bolt shear stress | 93.75 ksi |
| Bolt tension | A325 90 ksi; A490 113 ksi |
| Fillet weld (E70) | Rn = 1.86 (1 + 0.50 sin^1.5 θ) Lw D (kip, D in sixteenths) |
| Tear-out | 1.5 Lc t Fu |
| Block shear | Fu Ant + min(0.6 Fy Agv, 0.6 Fu Anv) |
| Shear stud | Qsc = 19.5 kip (used for both directions); AISC average 19.4 kip |
| Deck puddle weld | ~2 kip; neglected in ANSYS |
| Four seat bolts together | "roughly 180 kip" [1-9 §8.7.2, PDF 388 (p. 344)] |
| Seat vertical capacity at Cols 79 and 81 | "much greater than the applied vertical loads, even for full design loads"; STC/STP evaluated for horizontal load only [1-9 §11.2.4, PDF 535 (p. 469)] |
| Vertical failure / design load, F, K, H connections | Average 3.2 (core), 4.4 (tenant); range 1.9 to 7.2. Per-connection values in Tables 11-2, 11-3, 11-4 [1-9, PDF 536-538 (p. 470-472)] |
| Walk-off travel | SWC 2.5 in. [PDF 546 (p. 480)]; exterior seats 4.5 in. [PDF 548 (p. 482)]; Cols 79 and 81: 6.25 in. along beam axis, 5.5 in. lateral [PDF 548 (p. 482)]; seat at Col 79 is 11 in. wide, so 5.5 in. lateral push removes support [1-9 §11.4.1, PDF 593 (p. 527)] |
| Top clip at Cols 79 and 81 | "weak in tension"; failure governed by bolt shear then walk-off before loss of vertical support [1-9 §11.2.5, PDF 548 (p. 482)] |

### 1.10 Steel grades and material properties

| Item | Value | Citation |
|---|---|---|
| Grades in WTC 7 | ASTM A36, A572 Grade 50, and Algoma CSA G40.21-44W plate for "all shear connections in the floor framing" | [1-9 §12.2.1, PDF 606 (p. 540)] |
| By member | All beams and interior columns A572 Gr 50; exterior moment frames A36; column cover plates per §1.4 | [1-9 §11.2.2, PDF 526 (p. 460)] |
| Room-temperature yield of A572 Gr 50 in NIST curve | 54 ksi | [1-9 §11.3.2, PDF 569 (p. 503)] |
| Algoma 44W | Yield 44 ksi, UTS 75 ksi at 16% true strain in LS-DYNA (70.6 ksi estimated in App. E); bilinear, hardening modulus 194 ksi; used only for seats | [9A §2.2.2, PDF 59 (p. 8)]; [1-9 §12.2.1, PDF 608 (p. 542)] |
| Tensile strengths (App. E) | A36 64.5 ksi (eTS 0.226); 44W 70.6 ksi (0.173); A572 74.3 ksi (0.173) | [1-9 App. E Table E-2, PDF 784 (p. 718)] |
| Steel E at room temperature | 30,000 ksi; α = 1.4x10^-5 /°C used in NIST hand examples | [1-9 §8.7.2, PDF 388 (p. 344)] |
| Concrete | Specified 3,500 psi (28-day) NW; LS-DYNA used 4.9 ksi (age gain ~40%) reached at ~0.2% strain; tension ~500 psi then cracks | [9A §2.3.1, PDF 62 (p. 11)] |
| Concrete unit weight; steel density | **Not stated** (searched "pcf", "density", "unit weight") | |
| Bolts at temperature | Retained-strength equations and parameters | [1-9 App. E §E.4, Table E-8, PDF 790 (p. 728-729)] |

### 1.11 Foundations and supports

- Caissons socketed in bedrock ~60 ft below grade; grillages of built-up girders; 8 ft to 30 ft between grillage and first floor braced by 1 ft to 2.5 ft concrete walls, with many columns embedded [1-9 §2.4.1, PDF 56 (p. 12)].
- Global model: free column ends below the Floor 2 framing fully fixed; substation rigid and fixed; columns on top of it tied to it [9A §3.4.2, PDF 102 (p. 51)]; [1-9 §12.3.1, PDF 629 (p. 563)].

---

## 2. Loads

### 2.1 Design loading schedule (the only per-floor psf values NIST prints)

Reproduced in [1-9 §11.2.7, Fig. 11-17 "Design load criteria for WTC 7", PDF 551 (p. 485)] (source: PANYNJ, also Fig. 5-4 of NCSTAR 1-1; the List of Figures calls it Fig. 11-18). Image transcribed **[read from figure]**, all rows checked to sum. Units psf.

| Area | Slab | Fill/finish/roofing | Ceiling/ductwork | Partitions | Flooring | Beams/encasement/fireproofing | Total DL | LL | Total | DL + 0.25 LL **[derived]** |
|---|---|---|---|---|---|---|---|---|---|---|
| Main roof, bulkhead roof | 50 | 10 | 8 | | | 7 | 75 | 30 | 105 | 82.5 |
| 8th-20th, 24th-46th Fl. | 50 | | 5 | 12 | | 8 | 75 | 50 | 125 | 87.5 |
| 21st-23rd Fl. | 50 | | 5 | 12 | 15 | 8 | 90 | 75 | 165 | 108.75 |
| 7th Fl. north side | 80 | | 5 | 12 | | 93 | 190 | 50 | 240 | 202.5 |
| 7th Fl. south side | 80 | 38 | 8 | 12 | | 27 | 165 | 50 | 215 | 177.5 |
| 6th Fl. office space | 56 | | 5 | 12 | | 7 | 80 | 50 | 130 | 92.5 |
| 6th Fl. switchboard room | 62 | 38 | | | | 55 | 155 | 100 | 255 | 180 |
| 5th Fl. office space | 150 | 38 | 5 | | | 17 | 210 | 50 | 260 | 222.5 |
| 5th Fl. mechanical space | 150 | 38 | 5 | | | 17 | 210 | 150 | 360 | 247.5 |
| 4th Fl. | 56 | 75 | 5 | | | 10 | 146 | 100 | 246 | 171 |
| 3rd Fl. new construction | 56 | 75 | 5 | | | 10 | 146 | 100 | 246 | 171 |
| 3rd Fl. over existing substation | | | | | | | 240 | 100 | 340 | 265 |
| 2nd Fl. new construction | 56 | 60 | 5 | | | 10 | 131 | 150 | 281 | 168.5 |
| 2nd Fl. existing substation | | | | | | | 240 | 150 | 390 | 277.5 |
| 1st Fl. lobby | 175 | 90 | | | | 50 | 315 | 100 | 415 | 340 |
| 1st Fl. existing substation | | | | | | | 300 | 225 | 525 | 356.25 |

Note: NIST does not say whether the 12 psf partition allowance was treated as superimposed dead load or omitted; its SDL list names "ceilings, mechanical and electrical equipment, thermal insulation, and floor finishes" [1-9 §11.2.7, PDF 551 (p. 485)]. The NE-corner LS-DYNA submodel ramped a slab pressure to a plateau of roughly 88 psf **[read from figure]** [1-9 Fig. 8-24, PDF 396 (p. 352)], consistent with 75 + 0.25 x 50 = 87.5 **[derived]**; NIST does not state the number.

### 2.2 Loads NIST applied in the analyses

| Item | Value | Citation |
|---|---|---|
| Combination | Dead load (self-weight of steel and slabs) + superimposed dead load + service live load = 25% of design live load. No load or resistance factors. Wind not considered ("not structurally significant") | ANSYS: [1-9 §11.1, PDF 524 (p. 458)], [§11.2.7, PDF 550-551]. LS-DYNA: [1-9 §12.1, PDF 605 (p. 539)], [§12.3.2, PDF 630 (p. 564)] |
| Basis of 25% LL | "based on estimates of the live loads in the building at the time of collapse" (no data given) | [9A §3.4.3, PDF 104 (p. 53)] |
| LS-DYNA load distribution | Dead and live loads "distributed evenly in the concrete slabs and steel structure" by multiplying material densities by a common scale factor. Scale factor value **Not stated** | [9A §3.4.3, PDF 104 (p. 53)]; [9A §5.3, PDF 169 (p. 118)] |
| Floor 7 equipment | 22 kip (98 kN) between Columns 76 and 81, modelled as two 11 kip rigid plates on the slab either side of Columns 76 to 78, held by gravity only | [9A §3.4.3, PDF 103 (p. 52)] |
| Floor 46 equipment | Cooling towers 425 kip (1.89 MN); mechanical equipment 667 kip (2.97 MN); rigid plates on the north span | [9A §3.4.3, PDF 104 (p. 53)] |
| Total above Floor 8, design target (DL + SDL + 0.25 LL) | 174,136 kip (9A) / about 174,100 kip (1-9) | [9A, PDF 105 (p. 54)]; [1-9 §12.4.1, PDF 634 (p. 568)] |
| Total above Floor 8, LS-DYNA after gravity | 172,897 kip (0.7% low) | [9A, PDF 105 (p. 54)]; [1-9, PDF 635 (p. 569)] |
| Total of column forces at Floor 8, ANSYS | 176,500 kip (text) / 176,550 kip (figure); interior 87,350, north 33,300, south 21,900, east 18,850, west 15,150 kip | [1-9 §11.3.1, PDF 557, 559 (p. 491, 493)] |
| ANSYS application | Two steps: (1) slab stiffness zero, shear connections pinned, self-weight + loads from above Floor 16; (2) composite slab active, SDL + service LL | [1-9 §11.2.8, PDF 553 (p. 487)] |
| Other load combinations (e.g., 1.2D + 0.5L, GSA 2D + 0.5L) | **Not stated / not used.** The classic progressive collapse run cites GSA 2003 and UFC 2005 as guidance but gives no combination | [1-9 §12.4.7, PDF 660 (p. 594)] |

### 2.3 Column gravity forces

ANSYS 16-storey model, gravity only, forces "above Floor 8" (compression positive). The text gives only Column 79; the figure has no column labels, so the others are mapped by position against Fig. 5-7 **[read from figure]**.

| Column | Gravity [1-9 Fig. 11-21, PDF 559] | Case B 3.5 h [Fig. 11-29, PDF 569] | Case B 4.0 h [Fig. 11-37, PDF 579] |
|---|---|---|---|
| 79 | **7,525 kip** (stated in text, "maximum column force") [1-9 §11.3.1, PDF 557 (p. 491)] | 7,412 | 7,282 |
| 80 | 5,478 | 5,490 | 5,437 |
| 81 | 4,945 | 4,885 | 4,778 |
| 76 | 5,854 | 5,810 | 5,767 |
| 77 | 3,346 | 3,303 | 3,311 |
| 78 | 3,409 | 3,404 | 3,376 |
| 73 / 74 / 75 | 4,619 / 2,539 / 3,203 | 4,770 / 2,558 / 3,193 | 4,748 / 2,560 / 3,204 |
| 44 (north face) | 2,962 | 2,942 | 2,926 |

Text statements: other interior columns 2,000 to 5,000 kip, exterior 1,000 to 3,000 kip; axial stress 15 to 28 ksi in interior columns and exterior Columns 44 and 55, 8 to 15 ksi in other exterior columns [1-9 §11.3.1, PDF 557 (p. 491)]. At 4.0 h, "axial forces in columns were reduced by less than 0.50 percent relative to the gravity load analysis" [1-9, PDF 571 (p. 505)].

LS-DYNA group sums **[read from figure, bar heights, approximate]** [1-9 Fig. 12-58, PDF 651 (p. 585)]: Group 1 (79-81) about 7.6E7 N at gravity, about 7.45E7 N after temperatures, about 3.7E7 N at -0.5 s ("Group 1 failing"); Group 2 (76-78) about 5.25E7 N at gravity, about 5.35E7 N at -0.5 s ("Group 2 loads up slightly"). The elevation at which these were extracted is not stated in the caption.

---

## 3. NIST's global model (LS-DYNA)

### 3.1 Software, hardware, run time

| Item | Value | Citation |
|---|---|---|
| Code | LS-DYNA mpp971dR4 beta, revision 41161, double precision (single precision rejected for round-off) | [9A §3.6.3, PDF 117 (p. 66)] |
| Pre-processor | TrueGrid 2.3.0, parametric, floor-by-floor | [9A §3.2.2, PDF 70 (p. 19)] |
| Drawings used | Cantor S-1 to S-28 and SBR-1 to SBR-8; Frankel shop drawings for connections; floor plans S-2 to S-14 | [9A §3.2.1, PDF 70 (p. 19)]; [9A §3.4.1, PDF 88 (p. 37)] |
| Cluster | Head node 2 x Opteron 250 2.4 GHz, 4 GB; 8 compute nodes each 2 x dual-core Opteron 285 2.6 GHz (six with 8 GB, two with 16 GB); Infiniband | [9A §3.6.1, PDF 117 (p. 66)] |
| Run time | ~25 s simulated (4.5 s gravity + 4 s damage/temperature + ~16 s collapse) "generally took up to 8 weeks using 12 CPUs across 3 nodes" | [9A §3.6.2, PDF 117 (p. 66)]; [1-9 §12.2.2, PDF 610 (p. 544)] |
| Units | SI internally | [9A §1.3, PDF 53 (p. 2)] |

### 3.2 Element types and counts

[9A §3.6.2, PDF 117 (p. 66)]; [1-9 Table 12-1, PDF 610 (p. 544)]; [9A Table 3-1, PDF 71 (p. 20)]

| Element | Count | Use |
|---|---|---|
| Nodes | 3,593,049 | |
| Belytschko-Tsay shells (type 2, 4-node, "4 integration points by default") | 3,006,910 | Beams, girders, columns, slabs, connections |
| Hughes-Liu beams (type 1, cross-section integration) | 3,190 | Cross bracing, truss diagonals, penthouse, Floor 5 WTs |
| Constant-stress solids (type 1), rigid only | 2,461 | Discrete masses (1-9 adds "some of the foundation structures") |
| Nonlinear discrete springs | 33,364 | Bolts; vertical capacity augmentation in shear connections |
| Rigid elements | 3,050 (9A only; the four counts above already sum to 3,045,925 **[derived]**, so these are outside the total) | |
| Total elements | 3,045,925 | |

Typical shell size 0.15 m to 0.30 m (6 in. to 12 in.), uniform through the building; splice plates 0.05 m to 0.08 m (2 in. to 3 in.) [9A §3.2.3, PDF 72 (p. 21)]; [9A §3.3.2, PDF 85 (p. 34)]. "approximately 3 million elements or on the order of 10 million degrees of freedom" [9A §2.4, PDF 65 (p. 14)].

### 3.3 What was modelled, and how

| Component | Treatment | Citation |
|---|---|---|
| Beams, girders, columns, slabs | Shells; all beams, girders and columns except "a few non-critical, small section beams in the core" | [9A §3.4.1, PDF 88 (p. 37)] |
| Columns | Two-storey lengths joined by shell splice plates (tied contact with offset); end plates added at column ends (thickness = flange thickness, half-shell gap) for contact stability | [9A §3.3.2, PDF 84-85 (p. 33-34)] |
| Transfer trusses, wind bracing, belt truss (22-24), penthouse | Beam elements merged into shell nodes; no connection model; a beam-shell joint fails only when an element reaches its material failure criterion | [9A, PDF 92-93, 97 (p. 41-42, 46)] |
| Floor 5 diaphragm WTs | Beam elements, not embedded in slab | [9A, PDF 99 (p. 48)] |
| Shear studs | Tied contact from beam top-flange centre nodes to slab; no failure in the tie; released only when the node/element fails (usually slab failure). Only on interior floor beams and spandrels; none on interior girders or MG sections | [9A §3.3.3, PDF 85 (p. 34)] |
| Con Edison substation | Rigid body | [9A, PDF 89 (p. 38)] |
| Penthouses | Simplified beam model; east penthouse decoupled from the screenwall (connecting beams deleted) at the time debris damage was applied | [9A, PDF 100 (p. 49)] |
| Non-structural components (cladding, partitions) | Not included in stiffness or strength | [FAQ Q25] |
| Contact | *CONTACT_AUTOMATIC_SINGLE_SURFACE, SOFT=1, IGNORE=1; static and dynamic friction 0.3; tied edge-to-surface (beam ends) and tied surface-to-surface (splices, clips, seats) with OFFSET | [9A §3.2.4, PDF 72 (p. 21)] |

### 3.4 Material models and erosion

| Item | Value | Citation |
|---|---|---|
| Steel, ambient | *MAT_024 piecewise linear plasticity, tabular true stress-strain curves (Fig. 2-6 for 36, 42, 50 ksi), with a plastic-strain failure (erosion) criterion | [9A §2.2, PDF 54-56 (p. 3-5)] |
| Steel, heated regions (Floors 7-14) | *MAT_106 elastic-viscoplastic thermal, same curves plus temperature-dependent yield, E, Poisson's ratio and thermal expansion; same failure strain as ambient | [9A §2.2.3, PDF 59 (p. 8)] |
| Erosion strain basis | Mesh-dependent. Tensile-test calibration gave critical plastic strains 1.00 (fine), 0.56 (medium), 0.18 (coarse single-shell-across-gauge, for a 75 ksi specimen whose engineering failure strain was 0.20). "The WTC 7 global collapse model was developed with shell elements and a resolution corresponding to the coarse model ... Therefore, the measured engineering elongation of the specimens was used for the critical strain." | [9A §2.4.1, PDF 66-67 (p. 15-16)] |
| Numerical failure strains for the 36/42/50 ksi WTC 7 steels | **Not stated** (only the method above) | searched 9A Ch. 2, 1-9 §12.2.1 |
| Composite slab | *MAT_124 (plasticity compression-tension), rule-of-mixtures curves; per inch width Aconc 4.0 in2, Adeck 0.062 in2 (strong direction only), Awire 0.00467 in2; strong and weak directions averaged | [9A §2.3.1, PDF 63-64 (p. 12-13)] |
| Moment connection material | Same as the wind girder but failure strain lowered 30% for the weld zone; continuity plates added | [9A, PDF 83 (p. 32)]; [1-9, PDF 627 (p. 561)] |

### 3.5 Connection models in LS-DYNA

| Connection | Model | Citation |
|---|---|---|
| Fin, knife, header | One simplified shell model per depth group (W12 to W36), ~20 groups; capacities normalised by weld size or plate thickness, CoV 0.3 guideline; horizontal capacity calibrated first by pulling; a discrete spring added across the tab for vertical shear (elastic-perfectly-plastic, ultimate = actual shear capacity minus shell-model shear capacity). Calibrated to the Sadek et al. (2008) spring model (bolt shear, transverse weld failure, block shear, tear-out) | [9A §3.3.1, PDF 73-77 (p. 22-26)]; [1-9 §12.2.3, PDF 618-621 (p. 552-555)] |
| Seated (STP/STC/SWC) | Shell seat and clip plates tied to columns (no failure in the tie); sliding contact beam to plates; each bolt a discrete spring: 35 kip (156 kN) yield, 45 kip (200 kN) failure in shear, 0.45 in. (0.011 m) displacement at failure | [9A, PDF 77 (p. 26)] |
| Seats at Cols 79 and 81 | STC; "Since vertical failure of the seat was not considered (Section 11.2.5), the connections at Columns 79 and 81 were both modeled as stiffened seats." | [1-9 §12.2.3, PDF 624 (p. 558)] |
| SWC | Modified 79/81 seat model with web clip approximated as flange clip | [9A, PDF 83 (p. 32)] |
| Splices | Explicit shell splice plates; can fail (e.g., Col 58 splice at Floor 31 in the classic run) | [9A §3.3.2, PDF 84 (p. 33)]; [1-9, PDF 662 (p. 596)] |
| Force-deflection curves per group, actual input files | Figures only (9A Figs. 3-4, 3-5, 3-9). Input files withheld under NCST Act §7d | [FAQ Q7] |

### 3.6 Initialisation and loading sequence (calculation time)

[9A §3.4.3, Fig. 3-48, PDF 102-103 (p. 51-52)]; [1-9 §12.3.2, Fig. 12-32, PDF 629-630 (p. 563-564)]

| Calc time | Step |
|---|---|
| 0 to 4.5 s | Gravity ramped with a sinusoidal curve "to damp residual vibrations and eliminate dynamic response" |
| 4.5 s | WTC 1 debris damage applied instantly by deleting elements (restart with element list) |
| 4.5 to 6.5 s | Settling ("allowed to damp residual vibrations for 2 s") |
| 6.5 to 8.5 s | Case B 4.0 h temperatures ramped sinusoidally (nodal temperatures) |
| 8.5 s | ANSYS fire damage applied instantly; structure then free |
| 16.0 s | East penthouse kink = collapse-frame 0.0 s |
| 24.59 s | Run stopped, building had fallen ~10 m |

Damping method or coefficient, explicit time step, mass scaling, hourglass control: **Not stated** (searched "damp", "time step", "mass scal", "hourglass", "Rayleigh" in 9A and 1-9; the only time-step remark is that subassemblies were used to check "time step size" [9A §3.5, PDF 115 (p. 64)]).

Response to initialisation: debris damage gave up to 8 in. (~1/900 of height) settlement at the south face, redistributed by Vierendeel action [1-9 §12.4.2, PDF 636 (p. 570)]; temperatures raised the roof ~0.015 m (0.6 in.) by column thermal expansion [9A, PDF 110 (p. 59)]; "The structure was stable at the end of initialization" [9A §4.3.2, PDF 126 (p. 75)].

### 3.7 Debris damage (WTC 1)

- LS-DYNA Zone 1 (lower southwest): exterior Columns 14A through 20 severed above Floor 7, floor framing removed to the south core perimeter, some floor left cantilevered from the core. Zone 2: Column 20 and floor structure to the core perimeter removed above Floor 43 [9A, PDF 105 (p. 54)]; [1-9 §12.3.2, PDF 630 (p. 564)].
- Floor-by-floor estimate (depth of interior damage by floor, Floors 5 to 17 and 44 to roof): [1-9 §5.5.3, Figs. 5-92 to 5-101, PDF 226-231 (p. 182-187)].

### 3.8 Temperatures

Case B (FDS gas temperatures +10%) at 4.0 h, Floors 7 to 14, applied as nodal temperatures [9A, PDF 107 (p. 56)]; [1-9 §12.3.2, PDF 631 (p. 565)]. Column temperatures stayed below 300 °C (interior below 200 °C in other statements, see §6) [1-9 §11.4.1, PDF 591 (p. 525)].

### 3.9 Import of the ANSYS damage state

ANSYS 16-storey model: lower 16 storeys; Floors 8 to 14 framing and Floors 7 to 14 columns explicit; Floor 7 and below and Floors 15-16 as superelements; loads from above Floor 16 applied as column point loads; top of columns fixed in x and y [1-9 §11.2.1, §11.2.7, PDF 524, 550 (p. 458, 484)]. 101,357 elements, 93,413 nodes; a full thermal case took ~6 months on one 64 GB workstation [1-9 Table 11-1, PDF 526 (p. 460)]. Connection failure (break elements) modelled only on Floors 8 to 14 east of the N-S line through Column 76 and the core east of Column 73 [1-9 §11.2.5, Fig. 11-9, PDF 541-542 (p. 475-476)].

ANSYS damage near Columns 79-81, Case B 4.0 h [1-9 §11.3.2, PDF 570-571 (p. 504-505)]; [§11.4.1, PDF 591 (p. 525)]:
- Floor 13: all four N-S girders on Columns 79, 80, 81 failed (buckling, or walk-off at 79 and 81); girder 44-79 walked off its seat at 79; all east floor beams failed.
- Floors 10, 11, 12: girder 76-79 failed by tensile weld failure of the knife connection on the west side of Column 79 (temperatures there below 100 °C), driven by thermal expansion of the 76-79 girder on Floor 13.
- Floor 12: girder 26-81 buckled then walked off at 81; 2 to 3 seat bolts sheared at Column 79.
- Floor 14: all four erection bolts at the Column 79 seat failed; header connection of the girder west of Column 80 failed at the weld.
- Floors 11, 12, 14: one half to three quarters of east floor beams at damage level 0.75 to 0.99.
- Unsupported lengths at 4.0 h (ignoring east floor beams): Column 79 unsupported at three floors E-W and one floor N-S; Column 80 at one floor each way; Column 81 at one floor N-S [1-9, PDF 597 (p. 531)].
- At 3.5 h (the non-collapsing case): floor failures in the southeast at Floors 8, 13, 14, connection damage at Floor 12 [1-9 §12.4.5, PDF 655 (p. 589)]; girders bracing 79, 80, 81 still intact except 26-81 [1-9 §11.4.1, PDF 590 (p. 524)].

Transfer rules [1-9 Table 11-7, PDF 601 (p. 535)]; [9A, PDF 108-110 (p. 57-59)]; [1-9 Fig. 12-36, PDF 633 (p. 567)]:

| ANSYS connection | Damage index |
|---|---|
| Fin, knife | failed bolts / total bolts (horizontal and vertical) |
| Header | 1.0 if weld failed, else failed bolts / total |
| SWC (2 welds, 4 bolts) | Horizontal max(bolts/4, welds/2); vertical welds/2 |
| STC, STP | Horizontal 1.0 if walk-off, else bolts/total; vertical 1.0 if walk-off, else 0 |

| Index (F/K/H in LS-DYNA) | LS-DYNA action |
|---|---|
| 0 | none |
| 0 to 50% | lower shell element removed |
| 50 to 75% | discrete spring and lower shell removed |
| above 75% | connection failed |

Seated connections: discrete bolt springs deleted to match failed bolts; seat or clip damage applied directly. Buckled beams: flange and web elements removed so the beam loses axial and flexural strength but keeps its mass.

### 3.10 How Column 79 failure arose

- Best-estimate and no-debris runs: **not imposed.** After the ANSYS damage was applied, floor sections around 79-81 on Floors 13 and 14 fell; thermally weakened floors below failed in sequence down to Floor 5 where debris accumulated; Column 79 buckled (eastward) when its unsupported length became critical, aided by lateral perturbations from falling debris and girder connection failures [9A §4.3.3, PDF 130-131 (p. 79-80)]; [1-9 §12.4.4, PDF 638-639 (p. 572-573)].
- State at buckling: Column 79 laterally unsupported E-W and south between Floors 5 and 14; north restraint only at Floors 8-12 and 14 (seated girders to Col 44 still on their seats although all bolts had failed); at Floor 14 the girder to Column 76 still attached [1-9 §12.4.4, PDF 639 (p. 573)]; [9A, PDF 130 (p. 79)]. Column 80 unsupported between Floors 5 and 15; Column 81 between Floors 7 and 15 [9A §4.3.2, PDF 127 (p. 76)]; [1-9 §12.6, PDF 671 (p. 605)]. Girders 79-80 and 80-81 failed "immediately after 8.5 s" [9A, PDF 130 (p. 79)]. Cascading floors: "Floors 6 to 14, both inclusive" [1-9 §13.2 item 12, PDF 678 (p. 612)]; "over nine stories (between Floors 5 and 14)" [1-9 §13.2 item 11, PDF 677 (p. 611)].
- Lateral-support status per floor at buckling **[read from figure]** [9A Fig. 4-17, PDF 132 (p. 81)] (green full, yellow partial, red none): Column 79 full at Floors 15-18, partial at 14, none at 6-13 (8-12 annotated "vertical support and lateral restraint in north only"), partial at 4-5, full at 2-3. Column 80 full at 17-18, "near full" at 15-16, none at 6-14, partial at 2-5 ("no south framing by design" at 4 and 6). Column 81 "near full" at 15-18, none at 8-14, Floors 6-7 unmarked, partial at 4-5, full at 2-3 ("no north framing by design" at 6; "unconstrained at Floor 4 by design"; "no south or west framing by design" at 2).
- Column stresses at Floor 8 before buckling **[read from figure, approximate]** [9A Fig. 4-15, PDF 131 (p. 80)]: average vertical stress about -110 MPa (79), -85 MPa (81), -50 MPa (80); 80 and 81 show "increase in compressive stress immediately preceding column buckling".
- Imposed-failure cases: see §4.6.

---

## 4. Collapse sequence, timing, observations

### 4.1 Time frames

Calculation frame starts at 0.0 s; collapse frame 0.0 s = east penthouse kink = 16.0 s calc (13.3 s calc in the no-debris run, 5.3 s calc in the classic run). Written "collapse (calculation)" [9A §4.3.1, PDF 126 (p. 75)]; [9A §4.5, PDF 157 (p. 106)].

### 4.2 Best-estimate run (debris + Case B 4.0 h damage)

[9A §4.3.2, PDF 126-128 (p. 75-77)] unless noted.

| Collapse (calc) s | Event |
|---|---|
| -7.9 (8.1) | Connections fail in cantilevered floor framing in the debris zone [9A Fig. 4-19, PDF 133] |
| -7.5 (8.5) | ANSYS damage applied; sections of Floors 13 and 14 collapse around 79, 80, 81 |
| -6.6 (Table 12-2) / -6.5 (9.5) (Fig. 4-19) | Start of cascading floor failures around Column 79 [1-9 Table 12-2, PDF 665]; [9A Fig. 4-19, PDF 133] |
| -5.5 to -4.5 (10.5 to 11.5) | Floors collapse onto floors below around 79-81; debris strips framing from Columns 66, 69, 72 (Fig. 4-22) and hits Columns 65, 66 (Fig. 4-23) [9A, PDF 135-136] |
| -1.3 (14.7) | Column 79 buckles between Floors 5 and 14 |
| -1.1 (14.9) | Column 79 top starts down at roof level (0.2 s after buckling) [1-9 §12.6, PDF 671]; Fig. 4-16 labels -0.8 (15.2) for 80 and -0.3 (15.7) for 81 **[read from figure]** [9A, PDF 131] |
| -0.6 (15.4) | Column 80 buckles (0.7 s after 79 per 1-9 §12.6; "about 0.8 s" per 1-9 PDF 641) |
| -0.5 (15.5) | Group 1 (79-81) failing [1-9, PDF 650] |
| 0.0 (16.0) | Column 81 buckles (1.3 s after 79); kink appears in east penthouse roofline (north side) |
| 0.7+ (16.7+) | Top of east face deflects westward as floors around 79-81 pull it in |
| 1.0 (17.0) | First debris impact on Truss 2 [9A Fig. 4-28, PDF 139] |
| 2.0 (18.0) | East penthouse completely below roofline (overview; Table 4-1 gives 2.4-2.7 s) |
| 2.7 (18.7) | Truss 2 east diagonal buckles under debris, compromising 77, 78, 78A |
| 3.3 to 3.7 (19.3 to 19.7) | Columns 77 and 78 buckle (Truss 2 failure); Column 76 buckles (debris, load redistribution) |
| 3.9 to 6.1 (19.9 to 22.1) | Remaining interior columns buckle westward |
| 4.3+ (20.3+) | West core columns buckle between Floors 9 and 13 (Group 7 fails at 4.3 s) |
| 5.5 (21.5) | Exterior buckling starts at Column 14 (southwest, beside debris zone) between Floors 10 and 12 |
| 5.5 to 7.4 | Exterior columns buckle on south and west faces between Floors 7 and 14, then north and east; all within ~2 s [1-9, PDF 654] |
| 5.7 to 7.7 | West penthouse and screenwall fall below roofline |
| 6.2 to 6.3 | East side of north-face roofline starts down |
| 6.3 (22.3) | All interior column support lost [9A, PDF 143 (p. 92)] |
| 7.4 (23.4) | All interior and exterior columns buckled on the lower floors |
| 8.5 (24.5) | Roof falling at ~10 to 15 m/s |
| 8.59 (24.59) | Run stopped after ~10 m of fall |

Other quantitative remarks: southward sway of the upper floors grew to more than 1 m [9A Figs. 4-26 to 4-32, PDF 138-141]; northward buckling (~0.5 m) of west-core columns between Floors 9 and 13 [9A Fig. 4-32]. Truss 1 did not collapse [9A, PDF 137 (p. 86)]. Two debris impacts on the Truss 2 diagonal: Floors 8-14 collapse, then floors above 14 [9A, PDF 137]. "the failure of Truss 2 was not essential to the failure of Columns 77 and 78" [1-9, PDF 648 (p. 582)]. Exterior column loads fell on the north and east faces as floors fell away and rose on the south and west, dominated by Column 14 [1-9, PDF 652 (p. 586)].

### 4.3 Observations and NIST's comparison

Observed timeline relative to start of east penthouse descent [1-9 §5.7.6, Table 5-3, PDF 334 (p. 290)]: -3 s dust/smoke pushed across West Broadway; 0 s east edge of east penthouse moves down, folds ~40% across from the east; 0.6 s windows 40-44B and 40-44D break; 1.3 s NE corner of penthouse out of view; 2.0 s whole east penthouse out of view (2.0 ± 0.2 s [PDF 314]); 6.9 s global collapse starts on the north face, roofline below the east penthouse and east end of screenwall drop together, kink near Column 47; 8.5 s east end of screenwall out of view; 9.3 s west penthouse out of view; 12.0 s upper building breaks up; 13.5 s disappears into dust. Timing uncertainty between clips 6 frames or 0.2 s [1-9 §5.7.1, PDF 306 (p. 262)]. Penthouse descent began at 5:20:45 p.m. ± 1 s local time [1-9 §5.7.4, PDF 317 (p. 273)]; global collapse (north face first moving down) 5:20:52 p.m. [1-9 §5.7, PDF 305 (p. 261)].

[1-9 Table 12-2, PDF 665 (p. 599)] (= [1A Table 3-1, PDF 85 (p. 43)]; [9A Table 4-2, PDF 163 (p. 112)]):

| Event | Observed (s) | With debris (s) | Without debris (s) |
|---|---|---|---|
| Start of cascading floor failure around 79 | ≈ -6 (vibration, App. C) | -6.6 | -6.6 |
| Column 79 buckles, then 80 and 81 | not observable | -1.3 | -1.4 |
| East penthouse starts down | 0 | 0 | 0 |
| East penthouse below roofline | 2.0 | 2.4-2.7 | 2.3-2.6 |
| Core columns buckle across core, from 76 | not observable | 3.5-6.1 | 3.2-13.5 |
| North-face roofline starts down (east section) | 6.9 | 6.3 | 9.8 (threshold 1 m/s) |
| East end of screenwall below roofline | 8.5 | 7.3-7.7 | 8.7-9.2 |
| West penthouse below roofline | 9.3 | 6.9, 7.3 | 10.6, 10.9 |

FAQ Q25: from the start of floor failures around 79 to first north-face motion, measured and predicted times were both 12.9 s.

### 4.4 The 2.25 s free-fall stage

[1-9 §12.5.3, PDF 666-669 (p. 600-603)]; SI version [1A §3.6, PDF 86-88 (p. 44-46)]; [FAQ Q32].
- Video: Camera 3, West Street near Harrison Street. Point tracked near the centre of the north-face roofline. Roofline motion onset 6.9 s (pixel brightness), out of view at 12.3 s; 242 ft (73.8 m, 18 storeys) in about 5.4 s versus 3.9 s free fall, i.e. about 40% longer.
- Fit: z(t) = 379.62 {1 - exp[-(0.18562 t)^3.5126]} ft; v(t) = 247.52 (0.18562 t)^2.5126 exp[-(0.18562 t)^3.5126] ft/s; regression over the constant-slope range v(t) = -44.773 + 32.196 t (R2 = 0.9906), i.e. 32.2 ft/s2 = g (t = 0 at 6.9 s).
- Stage 1, 0 to 1.75 s: less than g; ~7 ft (2.2 m) of descent; corresponds to buckling of lower-storey north-face exterior columns.
- Stage 2, 1.75 to 4.0 s (~2.25 s): gravitational acceleration over ~8 storeys, 105 ft (32.0 m); "the columns provided negligible support".
- Stage 3, 4.0 to 5.4 s: reduced acceleration, a further 130 ft (39.6 m).
- NIST says the three stages "are consistent with the results of the global collapse analyses" [1-9, PDF 669 (p. 603)]. A model north-face displacement, velocity or acceleration history to compare against the fit: **Not stated / not presented** (the LS-DYNA run stopped ~10 m into the fall [9A, PDF 128]).

### 4.5 Building vibration before collapse

[1-9 App. C §C.3, PDF 757 (p. 691)]; [1-9 §8.3.2, PDF 373 (p. 329)]: northwest edge moved about ±2 in. (east-west, the strong direction) at least 6 s before the east penthouse moved; ~15 in. peak-to-peak as it collapsed. Fitted modes: undamped 3.61 s period, amplitude slightly over 1 in., in the 6 s before penthouse descent; afterwards a damped 3.46 s mode plus an undamped 1.65 s mode, ~14 in. total range. A seismic signal ~10 s before collapse onset attributed to falling debris [1A §3.5.1, PDF 84-85 (p. 42-43)]. NIST model natural periods: **Not stated.**

### 4.6 Sensitivity and imposed-failure cases

| Case | Set-up | Result | Citation |
|---|---|---|---|
| Earlier damage (Case B 3.5 h) | Same as best estimate but 3.5 h ANSYS damage | A few girders on 79, 80, 81 at Floors 12-14 fell; figure note "Column 76-79 girder connection failed at Column 76, stable afterward"; no initiating event; run stopped 4.26 s after damage (12.76 s calc). "debris impact damage, by itself, was not sufficient to initiate global collapse" | [9A §4.4, PDF 156-157]; [1-9 §12.4.5, PDF 655-656]; [1-9 §12.6, PDF 670] |
| No debris damage | Best estimate without WTC 1 damage | Same initiation, same order and "essentially the same times" (79 at -1.4 s); horizontal progression 3.2 to 13.5 s, over 10.3 s (9A text says 10.6 s) vs 2.6 s with debris; some mid-height floor failures near 73-75; all interior columns buckled by 13.5 (26.8) s; exterior columns buckled at mid-height, Floors 17 to 29, at ~15.5 (28.8) s, which "would have been visible" and "did not closely simulate the observed failure of the exterior façade"; screenwall fell before west penthouse (as observed). NIST: damage scenario in the best estimate "was slightly more severe than actually occurred" | [9A §4.5, PDF 157-163]; [1-9 §12.4.6, PDF 657-660]; [1-9 §12.6, PDF 672 (p. 606)] |
| Classic progressive collapse (no fire, no debris) | After gravity initialisation, a two-storey segment of Column 79 between Floors 11 and 13 removed at -0.8 (4.5) s. Removal method (instant or ramped) not stated | Floors around 79 collapsed to the roof; kink at 0 (5.3) s; Column 80 buckled between Floors 37 and 39 at 6.6 s calc (1.3 s); Column 81 failed at roof level by lateral loads, sharp load drop at Floor 8 between 2.6 (7.9) and 5.1 (10.4) s; Truss 2 diagonal partially buckled at 4.9 (10.2) s without buckling 77, 78; east penthouse fell in at 7.5 (12.8) s; Column 76 hit near Floor 35 at 10.8 (16.1) s; 77 buckled near Floor 36 at 11.0 (16.3) s; 78 between Floors 25 and 33 at 14.0 (19.3) s; 58 buckled at 14.7 (20.0) s after a splice failure at Floor 31 at 6.9 (12.2) s; 73 between Floors 35 and 37 at 15.0 (20.3) s; all interior columns buckled above Floor 23 by 21.2 (26.5) s, then exterior buckling and global collapse. Bimodal kinetic energy; NIST warns a run stopped between 6.7 (12.0) and 14.7 (20.0) s would wrongly suggest damage limited to the east side | [9A §4.6, PDF 163-166]; [1-9 §12.4.7, PDF 660-664 (p. 594-598)] |
| Two-floor subassembly (Floors 10-11) | Gravity then removal of Column 79 support; also Case A/B 5 h temperatures with Load Case 2 (release three girder connections around 79 on upper floor) and 3 (release connections around 81) | Column 79 removal: "unstable collapse of the entire bay surrounding the column", rest stable; LC2 Case A: floor collapse between 79 and 81, lower NE floor carried much of it; LC2 Case B: large part of both floors on the east end collapsed; LC3: SE corner floor collapse in both cases | [9A §4.2.1, PDF 118-123 (p. 67-72)] |
| 14-floor subassembly (Floors 10-23) | Debris damage; then abrupt removal of the support at the bottom of Column 79 | Debris: upper floors dropped ~0.15 m (6 in.), Vierendeel redistribution, stable. Column 79 removal: "The entire bay surrounding the column collapsed" | [9A §4.2.2, PDF 124-125 (p. 73-74)] |

NIST statements on what would have happened:
- "If Column 79 had not buckled, due to a larger section or bracing, for instance, the floor failures would not have been sufficient to initiate a progression of failure that would result in global collapse." [1A §3.4.6, PDF 81 (p. 39)]. No analysis is cited for this sentence.
- "WTC 7 was prone to classic progressive collapse in the absence of debris impact and fire-induced damage when a section of Column 79 between Floors 11 and 13 was removed." [1-9 §12.6, PDF 673 (p. 607)]; [1-9 §14.2, PDF 684].
- "Even without the initial structural damage caused by debris impact ... WTC 7 would have collapsed" [1-9 §14.2, PDF 684 (p. 618)]; [FAQ Q17].
- The initial westward progression and overall speed were "not sensitive" to the debris damage; small sensitivity near the end [1-9 §14.3.4, PDF 691 (p. 625)]. But 1-9 §12.6 says the horizontal progression and exterior failures "were sensitive to the extent of the estimated initial structural damage" [PDF 672 (p. 606)] (see §6).

---

## 5. Column 79 load, load path, and margins of neighbouring columns

| Topic | What NIST says | Citation |
|---|---|---|
| Column 79 load | 7,525 kip above Floor 8 (ANSYS, DL + SDL + 0.25 LL), the largest column force in the building; ~7,282 kip at 4.0 h **[read from figure]** | §2.3 |
| Column 79 tributary area | ~2,000 ft2 per floor | [1-9, PDF 660 (p. 594)] |
| Effect of floor failures on column load (ANSYS) | Column axial stresses "remained essentially constant"; "the failure of girders in a floor did not noticeably decrease the column load ... small compared to the total column loads from the tenant floors above"; interior columns not thermally restrained | [1-9 §11.3, PDF 556 (p. 490)] |
| Load redistribution path | "the only path for redistribution of gravity loads in WTC 7 between interior columns was through the floor framing. Any load redistribution would have occurred until the beam or girder connections failed at the column." | [1-9, PDF 556 (p. 490)]; see also §1.7 |
| Neighbours at 79's buckling (LS-DYNA) | Buckling of 80 and 81 "preceded by a slight increase in compressive stress due to load redistribution and pulling on the column from floor systems being pulled downward by Column 79, then by Column 80" | [9A §4.3.3, PDF 130 (p. 79)] |
| Mechanism for 80, 81 | Increased unsupported length, debris impact, loads redistributed from adjacent columns | [1-9 §13.2 item 12, PDF 678]; [1-9 §14.3.4, PDF 690] |
| Floor connections pulled apart | As 79 moved down, floor framing connections to 76, 80 and exterior 44 failed "under increasing tensile in-plane floor forces"; line of window breakage Floors 37-44 around Column 44 | [1-9 §12.6, PDF 671 (p. 605)]; [1-9 §13.2, PDF 678] |
| Through the transfer level | 79 and 81: no transfer element shown (§1.3). 80 carries the east end of Truss 2, which carries 77 and (via MG-23) 78; 76 sits on Truss 1 (to 73 and E3/E4) | §1.6 |
| Group 2 (76-78) load at -0.5 s | "Group 2 loads up slightly"; about 5.35E7 N vs 5.25E7 N at gravity **[read from figure]** | [1-9 Fig. 12-58, PDF 651] |
| Axial capacity, buckling load, effective length or demand/capacity ratio of Columns 76 to 81 at any unbraced length | **Not stated.** Searched "capacity", "demand", "margin", "Euler", "slenderness", "effective length", "KL/r" in all four sources. The only capacity-to-design ratios given are for floor connections (§1.9) | |
| Column 79 heating | 6 h of a ~1100 °C fully developed fire needed to reach 500-600 °C; not possible from contents fires | [1-9 §8.4.1, PDF 374 (p. 330)] |

---

## 6. Inconsistencies inside the NIST documents

| Item | Statement A | Statement B |
|---|---|---|
| Plan width | 140 ft [1-9, PDF 53] | 144 ft [1A, PDF 47]; east 149 ft, west 153 ft [1-9, PDF 142] |
| Con Ed extension north | ~40 ft [1-9, PDF 56] | 42 ft [1-9, PDF 142]; [1A, PDF 45] |
| Con Ed substation height | "three-story steel framed structure" [1-9 §2.3, PDF 56] | "two stories in height" [1A, PDF 45]; "two story section" [1-9, PDF 142] |
| Floor 5 slab | 14 in. (11 + 3 deck) [1-9, PDF 53, 60]; [1A, PDF 48] | "15 in." [1-9 §12.2.2, PDF 613] |
| Upper belt truss | Floors 22 to 24 [1-9, PDF 74]; [9A, PDF 97]; [1A, PDF 100] | "around Floors 22 and 23" [1A, PDF 47] |
| North cantilever girders | Columns 47 through 54 [1-9, PDF 73]; eight girders [1A, PDF 47] | Columns 47 to 53 [9A, PDF 97] |
| Truss 3 | Supports 61; carried by 62 and 61A [1-9, PDF 74] | Transfers 61 and 62 to 61A [9A, PDF 95] |
| Algoma plate nominal yield | 42 ksi [9A §2.2.1, PDF 55] | 44 ksi [9A §2.2.2, PDF 59]; [1-9, PDF 527, 606] |
| Severed columns | 6 south + 1 west [1-9, PDF 82, 686] | 5 south + 2 west [1-9 §13.2, PDF 676] |
| Column 80 after 79 | 0.7 s [1-9 §12.6, PDF 671]; figure times -1.3 and -0.6 | "about 0.8 s" [1-9, PDF 641] |
| All interior columns buckled | 6.5 s after kink "and 6.7 s after Column 79 buckled" [1-9, PDF 647] (79 buckled at -1.3 s, so 6.5 + 1.3 = 7.8 **[derived]**) | support lost by 6.3 (22.3) s [9A, PDF 143] |
| East penthouse below roofline (best estimate) | 2.0 (18.0) s [9A overview, PDF 127] | 2.4-2.7 s [9A Table 4-1, PDF 151] |
| No-debris horizontal progression | 10.6 s [9A, PDF 162] | 10.3 s [1-9, PDF 665]; [1A, PDF 85] |
| Classic run, Column 78 | "9.5 s (19.3 s)" [1-9, PDF 661]; [9A, PDF 164] | 14.0 s (19.3 s) [1-9, PDF 663]; [9A, PDF 165]; 19.3 - 5.3 = 14.0 **[derived]** |
| Interior column temperatures | below 200 °C [1-9, PDF 556, 689] | did not exceed 300 °C [1-9, PDF 591, 677, 690]; [FAQ Q11] |
| East penthouse support | Posts on Columns 76, 77, 79, 80 [1-9 §2.4.2, PDF 65] | "supported by Columns 79, 80, and 81" [9A, PDF 130]; [1-9, PDF 642] |
| Column-force change at 4.0 h | "reduced by less than 0.50 percent" [1-9, PDF 571] | Column 79 plotted 7,525 to 7,282 kip, -3.2% **[derived]**; total 176,550 to 175,700 kip, -0.48% **[derived]** |
| Sensitivity of horizontal progression to debris | "not sensitive" (initial westward progression and overall speed) [1-9, PDF 691] | "sensitive to the extent of the estimated initial structural damage" [1-9, PDF 672] |
| Medium tensile mesh | "0.10 in (0.254 mm)" [9A, PDF 55] (0.10 in. = 2.54 mm) | |
| App. E Table E-4 (A572 MISO) | Printed table (titled A 572) is headed "model for A36 steel" and repeats the Table E-3 values, first point 36.8 ksi [1-9, PDF 786 (p. 720), checked on the page image] | Ch. 11 gives A572 yield 54 ksi at room temperature [PDF 569] |
| Design-load figure number | Caption "Figure 11-17" [1-9, PDF 551] | List of Figures "Figure 11-18" [1-9, PDF 417] |

---

## 7. What NIST does not state that a frame model needs

Each item searched in all four sources unless narrower scope given.

1. **Storey heights other than typical (12 ft 9 in.) and Floors 5 and 6 (13 ft)**; no floor elevation table; mechanical floors only "13 ft to 15 ft". Only two absolute elevations (+925 ft 4 in. parapet top, +683 ft 6 in. Floor 29 window tops), datum unstated.
2. **Column grid coordinates and bay dimensions.** Only scattered spans (45 ft girder 44-79, 52-53 ft east/north beams, 36 ft south beams, ~9 ft beam spacing, 51.5 ft x 158 ft core, 6 ft 9 in. north offset, 46 ft cantilevers, Truss 3 10 ft / 18 ft). Plans are drawings without dimensions in the text.
3. **Column schedule** (section per column per storey) and **splice levels**. Only App. D sections at Floors 5 and 14 for 76-81, 77, 78A, and "W14x730 + plates" for 58, 61, 73-81 at unstated floors.
4. **Transfer-structure member sizes and geometry** (chords, verticals, MG-21/22/23/27/53, Truss 1-3 dimensions), except the Truss 1 and Truss 2 diagonals.
5. **Girder and beam sizes by location** beyond the typical-floor examples and Tables 11-2 to 11-4.
6. **How SDL and partitions were applied in LS-DYNA**: density scale factor, per-floor masses, facade/cladding weight, roof and penthouse equipment weights (only Floor 7 22 kip and Floor 46 425 + 667 kip given).
7. **Per-column gravity loads at any level other than "above Floor 8"**, and any column load in the LS-DYNA model in numbers (only plots).
8. **Axial capacity, effective length, buckling load or demand/capacity margin** for Columns 76, 77, 78, 80, 81 (or 79) at any unbraced length.
9. **Column 79 axial load at the moment it buckled**, and its initial imperfection or out-of-straightness (buckling was triggered by "lateral perturbations").
10. **Numerical erosion strains** for the 36, 42, 50 ksi steels and connection materials (method only), and connection force-deflection data per group (figures only; input files withheld, FAQ Q7).
11. **Damping** (method and value), **explicit time step**, **mass scaling**, **hourglass control**.
12. **Floor-by-floor failure times** in the LS-DYNA cascade from 8.5 s to 14.7 s calc (only snapshots at 9.5, 10.5, 11.5, 14.5 s).
13. **Method of removing Column 79** in the classic run (instant or ramped), and whether loads were identical to the best-estimate run (text says only "after gravity initialization").
14. **Any removal length other than two storeys (Floors 11-13)**; NIST ran no sweep over unsupported length.
15. **Model natural periods** (only video-derived 3.61 s, 3.46 s, 1.65 s).
16. **A model north-face descent history** to compare with the 2.25 s free-fall stage.
17. **Concrete and steel densities**, concrete elastic modulus.
18. **Column 79 and 81 foundation/continuity below Floor 5** in words (only shown in Fig. 1-6 / 2-24).
19. **Vertical failure of the Column 79/81 seats**: explicitly not modelled; seat weld strength not given.
20. **Hat truss or roof outrigger**: none described; penthouse member sizes not given.
21. **Load combinations other than DL + SDL + 0.25 LL**, and the data behind the 25% live-load estimate.
