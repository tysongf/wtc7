<!-- Extracted 2026-11-02 from the University of Alaska Fairbanks report (March 2020), NIST's reply and the AE911Truth request for correction archived in sources/drawings/raw/secondary_*, read as text only. These are secondary sources; nothing here is used as an input without a primary source (drawings or NIST). The reviewer's own observations are labelled as such. -->

# UAF WTC 7 study: notes for the Phase 3 pre-registration

Prepared 2026-11-02 for the Phase 3 question "if column 79 loses support, does the whole building
collapse?". Attributed reporting only. Nothing here endorses the UAF report, the AE911Truth
request, or NIST's reply.

## Sources and handling

| Short name | File (in `sources/drawings/raw/`) | Pages |
|---|---|---|
| UAF | `secondary_UAF_A-Structural-Reevaluation-of-the-Collapse-of-WTC7-March2020.pdf`. Hulsey, J.L., Quan, Z., Xiao, F., "A Structural Reevaluation of the Collapse of World Trade Center 7", INE Report 18.17, University of Alaska Fairbanks, March 2020 | 125 PDF pages |
| RFC | `secondary_AE911Truth_RFC-to-NIST-WTC7-Report-04-15-20.pdf`. AE911Truth and co-signers, Request for Correction under the Data Quality Act, 2020-04-15 | 106 PDF pages |
| NIST reply | `secondary_NIST-Response-2020-001_hosted-by-AE911Truth.pdf`. NIST letter to Ted Walter (AE911Truth) denying the RFC, digitally signed by Catherine Fletcher, 2020-08-28 16:34:00 -04:00 | 10 PDF pages |

- All three were read only as text: `pdftotext -layout` into
  `/tmp/claude-1000/-home-tyson-Projects-wtc7/7433e66f-699e-4777-9242-02693b0c0fab/scratchpad/uaf_txt/`,
  with PDF page markers added. Nothing from them was executed and nothing was written into `sources/`.
- **Page convention.** UAF: printed page then PDF page, e.g. "p. 79 [PDF 92]". In the UAF main body,
  PDF page = printed page + 13; the front matter uses roman numerals (abstract p. ii [PDF 3]). The
  RFC cites UAF by printed page, the same convention. RFC and NIST reply: printed page = PDF page.
- **Figures are raster images with no text layer.** Every number that UAF shows only inside a figure
  (displacement contours, the axial-force values on the column-removal plots, the Column 79
  capacity curve, the velocity curves) is unavailable as text. Only the numbers in captions and body
  text are reported below.
- UAF states that all input data, results and simulations are at http://ine.uaf.edu/wtc7
  (p. ii [PDF 3]). Not accessed for these notes.
- Provenance stated by UAF: funded by AE911Truth (p. iii [PDF 4]; p. 1 [PDF 14]); external peer
  reviewers G. Szuladzinski and R. Korol (p. iii [PDF 4]); the impact calculation in Section 3.3.1
  was "originally performed by mechanical engineer Anthony Szamboti" and reproduced with permission
  (p. 89 [PDF 102]). The RFC (p. 94) says AE911Truth funded the UAF study and attached it as
  Exhibit A (RFC p. 105).

---

## 1. UAF's global model

### Software and workflow
- Geometry drawn "two floors at a time" in AutoCAD from the steel erection drawings, checked by all
  team members, then imported into SAP2000 and ABAQUS; "each program was used by a different
  researcher and the results were compared" (p. 14 [PDF 27]; p. 24 [PDF 37]).
- SAP2000: the 47-storey global model and the Floors 12 to 13 thermal sub-model. ABAQUS: Floors 12
  to 13 wire-and-shell sub-model, the connection models, and a solid-element model of the NE corner
  of Floor 13 (p. 24 [PDF 37]; p. 49 to 52 [PDF 62 to 65]; p. 75 [PDF 88]). SolidWorks: steady-state
  thermal models of the slab (p. 32 to 36 [PDF 45 to 49]).
- Versions: SAP2000 and ABAQUS are described only as "the latest versions" (p. 14 [PDF 27]). The
  reference list cites "Dassault Systèmes, 2014, ABAQUS Analysis User's Manual, Version 6.7"
  (p. 111 [PDF 124]). No SAP2000 version is given.
- Chapter 4 collapse runs: "We used both ABAQUS and SAP2000" (p. 94 [PDF 107]), but the results
  shown and the time histories are attributed to SAP2000 (p. 99 [PDF 112]; p. 106 [PDF 119]). The
  RFC describes them as SAP2000 simulations (RFC p. 42).

### Extent and element counts
- 47-storey SAP2000 model: 39,978 joints, 44,507 frame elements, 7,832 area elements
  (p. 24 [PDF 37]). Floors 12 and 13 alone: 2,026 frame elements and 4,390 area elements
  (p. 24 [PDF 37]); the Floor 12 to 13 sub-model has 5,785 joints, 2,026 frame and 4,390 area
  elements (p. 65 [PDF 78]).
- Base of the model: Floors 1 and 2 "could only be partially finished due to missing drawings for
  the electrical substation"; the substation roof (Floor 3, at 33 ft 4 in.) was used "as the bottom
  floor of the model" (p. 39 [PDF 52]).
- Fig. 2.21 is "SAP2000 model of entire WTC 7 without roof" (p. 40 to 41 [PDF 53 to 54]). Separate
  SAP2000 models of Floors 12 to 47 and Floors 3 to 12 were used for substructuring
  (p. 41 to 42 [PDF 54 to 55]).
- ABAQUS solid model of the NE corner of Floor 13: 49,270 nodes, 24,536 elements (p. 75 [PDF 88]).

### Element types
- Steel beams, girders (and, implicitly, columns): frame ("wire") elements; slabs: shell (area)
  elements (p. 24 [PDF 37]; p. 50 [PDF 63]).
- Bracing (perimeter and core, Floors 1 to 7 and Floors 22 to 24 shown): frame elements with
  "released joints" (no end moment) "because the bracing could barely sustain any bending"
  (p. 39 to 40 [PDF 52 to 53]).
- Connections: nonlinear axial springs (shear) and nonlinear rotational springs (semi-rigid moment)
  (p. 26 to 27 [PDF 39 to 40]; p. 52 to 55 [PDF 65 to 68]).
- Penthouse beam-column connections: modelled as rigid "as it shortened modeling time while
  minimally affecting the response" (p. 94 [PDF 107]).

### Floors
- Typical slab: gauge 20 steel deck with 5.5 in. of concrete; 6x6-W1.4xW1.4 welded wire fabric at
  2.5 in. from the top (p. 45 [PDF 58]).
- Represented as a 5.5 in. homogeneous **orthotropic** shell, calibrated against a detailed
  frame/shell/solid slab model so deflections matched: E = 6,730,000 psi parallel to the flutes and
  3,285,000 psi perpendicular (concrete alone 3,408,800 psi) (p. 46 to 49 [PDF 59 to 62]). A mesh
  convergence study is mentioned but no mesh size is given (p. 46 [PDF 59]).
- Composite action (ABAQUS sub-model): slab shells linked to beam elements with joint offsets and
  "top center insertion points"; 3, 9 and 17 links per span tested; error against a hand
  calculation was -108.5 %, -9.6 % and -3.2 % (Table 2.2, p. 52 [PDF 65]). The number of links used
  in the global model is not stated.
- Floor 12 to 13 thermal sub-model (SAP2000): under NIST's assumption (beams studded, girders not),
  "more than 95% of the members acted compositely"; "all beams and girders in the model had released
  joints. The released joints did not have any bending resistance" (p. 65 [PDF 78]).
- Whether the global 47-storey model's slabs were composite with the beams is not stated.

### Connections
- Seven interior connection types, from NCSTAR 1A: fin (F), header (H), knife (K), seated top plate
  (STP), seated top clip (STC), seated web clip (SWC), seated moment (MC); exterior wind girders
  moment-connected to exterior columns (p. 29 [PDF 42]; p. 56 [PDF 69]).
- Each type modelled in detail in ABAQUS (Figs. 2.40 to 2.46, p. 56 to 59 [PDF 69 to 72]), giving
  moment-rotation and shear-displacement curves (Figs. 2.47 to 2.53, p. 59 to 63 [PDF 72 to 76]),
  each approximated by a simplified curve (red dotted line) for the springs (p. 59 [PDF 72]).
  The curves are images; no values are in the text.
- UAF states it "used a consistent method for modeling the connections in all floor story modeling
  and included nonlinear deformation and failure behavior in the connections" (p. 31 [PDF 44]), and
  that exterior frame connections were included as springs, unlike NIST (Table 2.3, p. 74 [PDF 87]).
  The failure criteria for the springs are not given.

### Columns
- No general description of how columns, splices or built-up sections were modelled in the global
  model.
- Column 79 at Floor 13: W14x730 with two 2 in. x 26 in. side plates welded on (p. 37 [PDF 50];
  Fig. 3.3, p. 78 [PDF 91]).
- In the Floor 12 to 13 sub-models, columns above and below were replaced by axial, bending and
  torsional springs (p. 64 [PDF 77]; p. 68 [PDF 81]); the Floor 12 boundary stiffness was taken
  from the Floor 3 to 12 model by unit loads at the four far corners (p. 44 to 45 [PDF 57 to 58]).

### Materials
- Steel: ASTM A572 Grade 50 for "all beams and interior columns", ASTM A36 for exterior moment
  frames (p. 32 [PDF 45]); no source given for this statement. Deck and WWF: A36, E = 29,000,000 psi,
  Fy = 36,000 psi (p. 46 [PDF 59]).
- Concrete: 3,500 psi, dolomite aggregate, 145 pcf, E = 3,408,800 psi (p. 32 [PDF 45];
  p. 46 [PDF 59]).
- Thermal: steel CTE 14 microstrain/°C (Wang 2002), concrete 10.6 microstrain/°C; conductivity steel
  35 BTU/(hr ft °F), concrete 1, equivalent slab 1.28 (p. 32 [PDF 45]; p. 35 [PDF 48]). Steel
  strength versus temperature from "Engineering tool box, 2011" (p. 37 [PDF 50]).
- No stress-strain law, plasticity model or failure strain for the global model is stated.

### Loads
- Dead load "based on the material density and the geometry of the sections"; live load "introduced
  as an external load" (stated for the simple beam test, p. 51 [PDF 64]).
- NIST's floor loading of 88 psf: "We confirmed this loading" (p. 76 [PDF 89]).
- Floor 12 to 13 sub-model loaded by column axial forces applied at the top of Floor 13
  (Table 2.1, p. 43 to 44 [PDF 56 to 57]; reproduced in Section 5).
- Debris damage: "For all collapse models and analyses, we included the debris damage assumed by
  NIST, which involved six exterior columns on the southwest face of the building reportedly being
  severed" (p. 94 [PDF 107]).
- The load combination for the Chapter 4 collapse runs is not stated.

### Damping
- Not stated anywhere in the text. Time step, integration parameters and run duration are not
  stated either; UAF says only that SAP2000 uses direct integration (p. 99 [PDF 112]).

### Analysis types: what was linear and what was nonlinear

| Analysis | As stated by UAF | Page |
|---|---|---|
| Method overall | "Both a static analysis and a linear dynamic time history analysis using the direct integration method were used"; "also checked this approach against a static non-linear evaluation considering both geometric non-linearity and material nonlinearity; P-delta was not included" | p. 26 to 27 [PDF 39 to 40] |
| Connections | Nonlinear axial and rotational springs | p. 26 to 27, 52 to 55 [PDF 39 to 40, 65 to 68] |
| Column 79, 80, 81 removal at six height bands (Figs. 4.2 to 4.7) | Linear static | p. 95 [PDF 108] |
| Column removal for "NIST's horizontal progression" (Figs. 4.8 to 4.15) | Linear static (captions); Fig. 4.16 "Dynamic analysis" | p. 101 to 105 [PDF 114 to 118] |
| Time histories in general | "We examined structural response for a time history analysis using linear elastic behavior. We also studied the behavior considering material and geometric non-linearity effects. P-delta was not included in these results." | p. 99 [PDF 112] |
| Core then exterior failure (global) | "Dynamic time history finite element analysis"; "an acceleration time dependent function accounted for impact resistance over time" (not further defined) | p. 105 to 106 [PDF 118 to 119] |
| Impact loading | "Impact loading was examined, and the influence of neglecting impact loads had a minimal effect on our results" (no detail) | p. 27 [PDF 40] |
| Kink in north face / buckling in time | "we were unable to simulate this phenomenon with the software" (needs small time steps and small incremental deformations) | p. 95 [PDF 108] |

Which Chapter 4 figures come from the nonlinear runs, if any, is not stated. The column-overload
sequence in Figs. 4.10 to 4.13 is labelled linear static throughout.

### Local sub-models (for context)
- Column 79 buckling check to the AISC Manual (14th ed.), pinned-pinned, effective lengths 12 ft 9 in.
  (one storey) and 25 ft 6 in. (two storeys); "buckling load capacity was significantly higher than
  the acting load over a two-story unsupported length" (p. 37 [PDF 50]; Fig. 2.18, p. 39 [PDF 52]).
  Capacity values are only in the figure.
- Thermal load on Floors 12 to 13 (SAP2000): NIST's computed temperatures reduced to three zones,
  1,211 °F, 941 °F and 68 °F (p. 65 [PDF 78]).
- ABAQUS solid model of NE corner, Floor 13: used to test NIST's initiation under NIST-type
  assumptions (Section 3.1, p. 75 to 76 [PDF 88 to 89]).

---

## 2. How UAF failed columns, and the cases run

How failure was imposed: in every case the columns are "removed" over a stated storey range
(Chapter 4 captions and text). The text never says whether removal was instantaneous or ramped,
and gives no removal duration, except that in the global case the exterior columns fail "1.3
seconds later" than the core columns (p. 95 [PDF 108]; p. 105 [PDF 118]). UAF frames its method as
the alternate load path method, "removes one or several major structural bearing elements"
(p. 26 [PDF 39]).

**No case removes Column 79 alone.** The smallest removal set in Chapter 4 is Columns 79, 80 and 81
together.

| # | Columns failed | Storeys | Analysis | Page |
|---|---|---|---|---|
| E1 | 79, 80, 81 | Floor 6 to Floor 13 | Linear static | Fig. 4.2, p. 96 [PDF 109] |
| E2 | 79, 80, 81 | Floor 13 to Floor 21 | Linear static | Fig. 4.3, p. 97 [PDF 110] |
| E3 | 79, 80, 81 | Floor 21 to Floor 29 | Linear static | Fig. 4.4, p. 97 [PDF 110] |
| E4 | 79, 80, 81 | Floor 29 to Floor 37 | Linear static | Fig. 4.5, p. 98 [PDF 111] |
| E5 | 79, 80, 81 | Floor 37 to Floor 45 | Linear static | Fig. 4.6, p. 98 [PDF 111] |
| E6 | 79, 80, 81 | Floor 45 to the penthouse | Linear static | Fig. 4.7, p. 99 [PDF 112] |
| H1 | 79, 80, 81 ("NIST's scenario") | Not stated in text or caption | Linear static and dynamic | Fig. 4.8, p. 101 [PDF 114]; text p. 99 [PDF 112] |
| H2 | 76 to 81 | Not stated | Linear static | Fig. 4.9, p. 101 [PDF 114] |
| H3 to H5 | 76 to 81, then the overloaded columns removed in successive steps (10 exterior columns at the SE corner, then numerous core and exterior, then the rest) | Not stated | Linear static, step by step | Figs. 4.10 to 4.13, p. 102 to 103 [PDF 115 to 116] |
| H6 | 76 to 81 | Not stated | Dynamic | Fig. 4.16, p. 105 [PDF 118] |
| G1 | All core columns, then all exterior columns 1.3 s later | Floors 12 to 19 | Dynamic time history | p. 95 [PDF 108]; p. 105 to 108 [PDF 118 to 121] |
| G2 | Same | Floors 6 to 13 | Dynamic time history | p. 108 [PDF 121] |

Context for E1 to E6: UAF set out to find "the height at which Columns 79, 80, and 81 most likely
failed", noting NIST had Column 79 losing lateral support from Floor 5 to 14 (p. 94 [PDF 107]).
The RFC treats E1 (Floors 6 to 13) as "approximately where these columns buckled in NIST's Probable
Collapse Sequence" (RFC p. 43).

---

## 3. Collapse criteria and results

### Criteria as stated
- **Penthouse collapse (E1 to E6):** judged from deflection of the penthouse in the linear static
  result: "The penthouse now collapses, as demonstrated from the significant amount of deflection
  given in the figure" (Fig. 4.7 caption, p. 99 [PDF 112]). No threshold is stated.
- **Building response (E1 to E6):** eastward tilt in inches, compared qualitatively with video
  ("would cause the building to tilt dramatically to the east, which would have been observed in the
  videos but was not", p. 95 [PDF 108]).
- **Column failure in the progression runs (H1 to H5):** a column fails when its axial load
  "would exceed design loads" (p. 100 [PDF 113]); for H1, "no other columns would buckle"
  (p. 99 [PDF 112]). How "design load" or buckling was evaluated is not stated.
- **Matching the observed collapse (G1, G2):** three key features taken from video and the NIST and
  FEMA reports: east penthouse collapse about 6.9 s before the roofline descends; screen wall and
  west penthouse about 0.5 to 1 s before; roofline free fall for about 2.25 to 2.5 s over about
  105 ft (8 storeys) with no visible differential movement of the exterior (p. 92 [PDF 105]).
  Agreement is judged visually against two videos (Fig. 4.17, p. 106 [PDF 119]) and against David
  Chandler's velocity measurement (Figs. 4.19 to 4.20, p. 107 to 108 [PDF 120 to 121]).
- **Overall:** UAF calls the result "a global failure involving the near-simultaneous failure of
  all columns" as opposed to "a progressive collapse involving the sequential failure of columns"
  (p. 110 [PDF 123]).

### Results, by case
- **E1 (79 to 81 out, Floors 6 to 13):** building tilts east "almost 10 inches"; penthouse does not
  collapse (Fig. 4.2, p. 96 [PDF 109]).
- **E2 (13 to 21):** tilt 7.2 in. east; no penthouse collapse (Fig. 4.3, p. 97 [PDF 110]).
- **E3 (21 to 29):** tilt 5.4 in.; no collapse; penthouse deflection increases (Fig. 4.4,
  p. 97 [PDF 110]).
- **E4 (29 to 37):** tilt 3.85 in.; no collapse (Fig. 4.5, p. 98 [PDF 111]).
- **E5 (37 to 45):** tilt "negligible"; penthouse deflection "much greater" (Fig. 4.6,
  p. 98 [PDF 111]).
- **E6 (45 to penthouse):** tilt negligible; penthouse collapses (Fig. 4.7, p. 99 [PDF 112]).
- UAF's reading: 79 to 81 failed high in the building; the east penthouse "collapsed only as far
  down as the upper 3 to 5 stories"; this was "a separate and distinct event from the global
  collapse"; since there were "no documented fires above Floor 30", fire did not cause it
  (p. 95 to 96 [PDF 108 to 109]).
- **H1 (79 to 81 out):** "no other columns would buckle, including neighboring Columns 76, 77, and
  78. This result is expected based on the design principle of redundancy" (p. 99 [PDF 112]).
  No displacement or demand numbers in the text.
- **H2 to H5 (76 to 81 out):** axial loads on exterior columns around the SE corner exceed design
  loads; 10 exterior columns overloaded but "not the next row of core columns to the west"
  (Fig. 4.10, p. 102 [PDF 115]); their removal overloads "numerous core and exterior columns"
  (Fig. 4.11); then the remaining core and many exterior columns, with some columns going into
  tension (Fig. 4.12, p. 103 [PDF 116]); then "nearly every remaining column" (Fig. 4.13). UAF says
  "a total collapse of the building would ensue" but it "would tip to the southeast" rather than
  fall straight down (p. 100 [PDF 113]; Figs. 4.14 to 4.16, p. 104 to 105 [PDF 117 to 118]).
  Displacement magnitudes are in the figures only.
- **G1 and G2:** "produces almost exactly the behavior observed in videos"; simulated velocity and
  acceleration "matches almost exactly" Chandler's, "including the approximately 2.5 seconds of
  free fall" (p. 106 [PDF 119]). G1 and G2 "were identical in terms of the downward velocity and
  acceleration of the northwest corner at the top of building"; from video, Floor 16 is "the
  uppermost floor where the collapse could have initiated" (p. 108 [PDF 121]).
- UAF's own caveat: "We cannot completely rule out the possibility that an alternative scenario may
  have caused the observed collapse" (p. 3 [PDF 16]).

### Numerical results from Chapters 2 and 3 (initiation, not global collapse)
- SAP2000 Floors 12 to 13 under NIST temperatures: Column 79 floor-system displacement 1.915 in.
  east and 0.7293 in. north; girder A2001 westward displacement relative to Column 79 "less than
  1 inch", against NIST's 6.25 in. (p. 66 [PDF 79]). Fully composite (girders included) differed by
  less than 5 % (p. 66 [PDF 79]).
- ABAQUS Floors 12 to 13: 1.85 in. (x) and 0.94 in. (y) at Column 79 (p. 68 [PDF 81]). Relative
  westward movement of A2001 at the Column 79 seat: 3.68 in. non-composite, 2.18 in. partially
  composite, less than 1 in. composite (p. 71 [PDF 84]).
- With NIST's boundary conditions, no slab, raised temperatures, and side plates ignored: 5.11 in.
  westward relative displacement, against 6.25 in. (NIST) and 6 in. needed to clear the 12 in.
  seat (p. 72 [PDF 85]).
- Solid model: A2001 trapped behind the west side plate of Column 79 (p. 77 to 79 [PDF 90 to 92]).
  To push the web past the seat in a model with the side plate removed, UAF had to raise the CTE of
  K3004, C3004, B3004 and A3004 by about 40 % to 11.5 x 10^-6 in/in/°F (p. 76 [PDF 89];
  p. 80 to 81 [PDF 93 to 94]); flange and stiffener stresses then "not sufficient to cause the
  flange to fail" (p. 82 [PDF 95]).
- G3005 buckles only if the lateral support beams S3007, G3007, K3007 are omitted; with NIST's
  constraints D3004 and K3004 also buckle, but adjacent beams do not, so "no full floor collapse
  would be expected" (p. 84 to 86 [PDF 97 to 99]).
- Impact of the Floor 13 assembly on Floor 12 (Szamboti calculation reproduced by UAF): weld shear
  capacity of the seat support plate 632,000 lb (from Nordenson); Floor 12 girder stiffness 7,627
  kips/in. at 10 in. from Column 79 (Nordenson); falling-assembly mode 0.52 Hz, weight about
  20,000 lb, giving K1 = 552.53 lb/in. and series stiffness 552.48 lb/in.; with Nordenson's
  potential energy of 3,473,000 in-lb, D = 112.13 in. and F = 61,950 lb, "less than 10%" of
  632,000 lb (Nordenson's figure was 4,133 kips) (p. 88 to 90 [PDF 101 to 103]).

---

## 4. UAF on NIST, and criticisms of UAF's method

### 4a. What UAF says about NIST's global model and initiation
- **Exterior frame stiffness:** NIST did not model exterior-frame connections, "essentially treating
  the exterior steel framing as thermally fixed"; UAF says the exterior was flexible and the point
  of zero thermal movement was "near the elevator shafts" (p. 3 [PDF 16]; p. 30 [PDF 43]) or "near
  the center of the building" (p. 74 [PDF 87]).
- **Inconsistent connection modelling:** NIST modelled connection failure only on Floors 8 to 14
  within a selected area (Fig. 2.5), making east and west stiffness differ and splitting its
  collapse simulation "into two parts" (p. 29 to 31 [PDF 42 to 44]).
- **Girder walk-off:** NIST's 6.25 in. (earlier 5.5 in.) relative displacement not reproduced; UAF
  gets less than 1 in. (p. 4 [PDF 17]; p. 66 [PDF 79]).
- **Side plates:** NIST "either minimized the side plate protrusion on Column 79 (nominally
  1.79 inches) or ignored it altogether" (p. 79 [PDF 92]).
- **Web stiffeners:** NIST omitted the 3/4 x 5.5 x 18 in. partial-height stiffeners on A2001, per
  Frankel shop drawing 9114 (p. 81 [PDF 94]); Figs. 8-21 and 8-23 of NCSTAR 1-9 show none
  (p. 82 to 83 [PDF 95 to 96]).
- **Shear studs:** NIST assumed none on A2001; the Arup and Nordenson reports showed it had them
  (p. 65 [PDF 78]; p. 76 [PDF 89]).
- **G3005:** NIST's preliminary model omitted lateral support beams S3007, G3007, K3007; analysed
  G3005 as W24x55 when erection drawing E12/13 shows W21x44; and framed it into an exterior column
  rather than the wind girder (p. 84 [PDF 97]).
- **Floor cascade mechanism:** "Although there is no described or apparent mechanism, NIST simply
  claims that this initial north girder failure at Floor 13 precipitated a collapse of the south
  girder" (p. 19 [PDF 32]); no fire on Floor 10 to break the girder connection below Floor 11
  (p. 20 [PDF 33]).
- **Global collapse simulation:** NIST's shows "significant differential movements in the exterior,
  both before and during the fall of the roofline, that were not observed in the video"
  (p. 92 [PDF 105]; Fig. 4.1, p. 93 [PDF 106]).
- Table 2.3 lists modelling features UAF says it included and NIST did not (p. 74 [PDF 87]).

### 4b. NIST's reply (2020-08-28): what it says
The reply responds to the RFC's items A to H. **It does not mention UAF's model, its column-removal
runs or its global scenario by name, and makes no direct critique of them.** UAF appears only inside
NIST's restatement of the RFC's requested correction ("e.g., the Scenario Simulated in the UAF
Analysis", NIST reply p. 6). Points that bear on UAF's claims:
- **A, side plate (NIST reply p. 2):** NIST "disagrees that the 16-story ANSYS model ignored the
  effect" of the side plate; the full-scale model has "detailed connection models that are
  consistent with the fabrication shop drawings" (Figs. 8-21 and 11-15); "The Girder A2001 and
  Column 79 connection locates the bolts on a seated connection attached to the exterior edges of the
  Column 79 side plates, with the girder axis at a slight angle to Column 79."
- **B, thermal expansion (NIST reply p. 3):** the 16-storey ANSYS model used thermal data from fire
  simulations "validated against numerous photograph and video records" (NCSTAR 1-9 Sections 5.6,
  9.5); all floor beams were connected to and expanded against A2001 "until the connection at Col 79
  failed, as shown in Figure 11-48."
- **C, web stiffeners (NIST reply p. 4):** the stiffener on Frankel 9114 was not in the preliminary
  analyses; stiffeners matter mainly under full design live load, but the building had been
  evacuated so live loads were minimal; in the preliminary shell-element analyses (NCSTAR 1-9
  Section 8.8), with loads and temperatures exceeding those of the 16-storey model "by a factor of 2
  or more", A2001 showed no web or flange deformation at the Column 79 seat without the stiffener.
- **D, floor cascade (NIST reply p. 5):** the LS-DYNA model "included the ability to simulate
  nonlinear responses, falling debris, and dynamic impact effects" (NCSTAR 1A p. 38). Sensitivity:
  with lesser damage (3.5 h), "several girders in Floors 12 to 14 that were connected to Columns 79,
  80, and 81 ... fell to the floors below. However, the damage was not sufficient to initiate a
  global collapse" (NCSTAR 1-9 pp. 603 to 604, as cited by NIST).
- **E, global collapse (NIST reply p. 6):** NIST lists matched observables (east-west motion,
  penthouse kink about 1 s after Column 79 buckled, east-side window breakage, global collapse onset
  within about 0.5 s); measured and predicted time from the start of floor failures around Column 79
  to roofline motion was 12.9 s (NCSTAR 1A Table 3-1); animation differs from video "only in the
  later stages ... and only after the initiation of global collapse"; nonstructural components
  (cladding, partitions) were not modelled.

### 4c. Criticisms of UAF's method in these files
There is no direct technical critique of UAF's model in any of the three files. The RFC is written
in support of UAF and relies on it (RFC p. 9 to 14, 19, 23 to 25, 42 to 48). What these files do
contain:
1. **NIST's indirect counterpoints** (4b above): its model represented the as-detailed seat
   geometry, including a girder skew UAF's text does not discuss (NIST reply p. 2); its temperatures
   were computed and time-varying rather than zoned (NIST reply p. 3; compare UAF's three uniform
   zones, p. 65 [PDF 78]); stiffeners were not needed in its analyses (NIST reply p. 4); its
   collapse model handled impact and debris dynamically, and floor failures around 79 to 81 alone
   did not always produce global collapse (NIST reply p. 5).
2. **NIST FAQ 35/28 as quoted in the RFC** (RFC p. 11 to 12): differences between the partial-floor
   model and the 16-storey model are expected because of simplified uniform temperatures, laterally
   fixed columns, and boundary constraints in the partial model. The same reasons apply to UAF's
   Chapter 3 solid model, which UAF built "with the aim of replicating" NIST's partial-floor results
   using NIST-type assumptions (p. 75 [PDF 88]). (The repo copy at `sources/text/wtc7_faq.txt`
   numbers this FAQ 28, lines 512 to 536; the RFC calls it FAQ #35.)
3. **Limitations UAF states itself:**
   - Removal sequences in Chapter 4 are linear static; time histories used "linear elastic
     behavior"; P-delta excluded (p. 99 [PDF 112]; p. 27 [PDF 40]).
   - Could not simulate buckling in time or the north-face kink (p. 95 [PDF 108]).
   - Penthouse connections rigid (p. 94 [PDF 107]).
   - Floors 1 and 2 only partly modelled; model starts at Floor 3 (p. 39 [PDF 52]).
   - Displayed deformations are scaled and "not scaled to the building geometry" (p. 94 [PDF 107]).
   - The CTE of four beams had to be raised about 40 % to get walk-off in the side-plate-removed
     model (p. 80 to 81 [PDF 93 to 94]).
   - Cannot rule out an alternative scenario (p. 3 [PDF 16]).
4. **Internal inconsistencies in the UAF text:**
   - Section 2.7 cites Fig. 2.66 for the "less than 1 inch" result (p. 74 [PDF 87]), but Fig. 2.66 is
     the 5.11 in. result under NIST's boundary conditions (p. 72 to 73 [PDF 85 to 86]).
   - Walk-off distance given as 6.290 in. (p. 79 [PDF 92]) and "6 inches" (p. 72 [PDF 85]); NIST's
     erratum value is 6.25 in.
   - Zero-movement point "near the elevator shafts" (p. 3 [PDF 16]) and "near the center of the
     building" (p. 74 [PDF 87]).
   - Connections described as nonlinear springs throughout (p. 31 [PDF 44]; p. 52 to 55 [PDF 65 to
     68]), but the Floor 12 to 13 thermal sub-model had "released joints" with no bending resistance
     (p. 65 [PDF 78]).
   - The text says Arup found A2001 trapped "after less than 4 inches of lateral travel"
     (p. 87 [PDF 100]) while UAF's own clearance is 3.678 in. (p. 79 [PDF 92]); not contradictory,
     but the figures differ.

### 4d. Reader's observations (mine, not stated in these files)
Flagged for the pre-registration; none of these is a claim made in the three documents.
1. **Column 79 alone was never removed.** UAF's smallest removal set is 79 to 81 (Section 2 above),
   so its report does not answer the Phase 3 question directly.
2. **H1 tests a different initial state from NIST's.** UAF removes column segments with all floors,
   connections and diaphragms intact. NIST's sequence, as quoted in the RFC (RFC p. 26 to 27, citing
   NCSTAR 1A p. 22 to 23), involves floor failures from Floor 5 to 14 around Column 79, debris
   loading on Truss 2 and loss of lateral support. The storey range for H1 is also not stated.
3. **The failure test is an elastic force check.** Columns "fail" when linear static axial force
   exceeds "design loads" (p. 100 [PDF 113]). No member capacity, buckling check, connection failure
   in the global runs, or dynamic amplification factor is reported, and P-delta is excluded. In
   SAP2000, link elements in a linear time history act with their linear properties, so the
   nonlinear connection springs may not have been active in the linear dynamic runs; UAF does not
   say.
4. **The G1/G2 free-fall match is largely built in.** With every column removed over 8 storeys,
   the upper block has nothing to resist it over that height, so near-free-fall descent follows from
   kinematics. The match constrains timing and shape more than it tests the structure. The
   "acceleration time dependent function" for impact resistance is not defined (p. 106 [PDF 119]).
5. **Column 79 capacity was checked over two storeys only** (p. 37 [PDF 50]), while UAF itself
   summarises NIST's mechanism as nine storeys without lateral support (p. 20 [PDF 33]).
6. **Slab representation outside Floors 12 to 13 appears coarse.** 7,832 area elements in the whole
   model minus 4,390 on Floors 12 to 13 leaves about 3,442 for the other floors
   (p. 24 [PDF 37]), roughly 80 per floor if spread evenly. This is arithmetic on UAF's counts, not
   something UAF states.
7. **The impact calculation uses a global-mode stiffness.** K1 comes from the 0.52 Hz vertical mode
   of the falling assembly (p. 89 [PDF 102]), which sets the series stiffness, and so the impact
   force, close to K1. The local contact stiffness and mass distribution are not considered. NIST's
   reply says impact was handled in LS-DYNA (NIST reply p. 5).
8. **Unreported inputs** for the global runs: damping, time step, removal duration, load
   combination and live load fraction, column section and splice modelling, transfer structure at
   Floors 5 to 7 (mentioned only in UAF's summary of FEMA, p. 17 [PDF 30]), spring failure criteria,
   mesh size.

### 4e. Cross-check against the repo's primary-drawing readings
The repo already holds the Frankel sheets UAF and the RFC cite (`sources/drawings/raw/`:
`FOIA12-009_1091.TIF`, `FOIA12-009_9114.TIF`, `FOIA09-49_E12_13.tif`, `FOIA12-009_E12_13.tif`),
read in `sources/drawings/READING.md`. Comparing UAF's numbers with that reading:
- Side-plate projection: UAF 1.79 in. "nominally" (p. 79 [PDF 92]); READING.md 1 13/16 in. as drawn,
  1.79 in. with AISC depth. Agree.
- Clear width between side plates: UAF 17.89 in. (p. 79 [PDF 92]); READING.md 17 7/8 in. Agree.
- Room from the A2001 west flange tip to the west side plate: UAF 3.678 in. (p. 79 [PDF 92]);
  READING.md infers 4.15 in. (east side 2.26 in.). Differ by about 0.5 in.
- Seat travel for web walk-off: UAF 6.290 in. (p. 79 [PDF 92]); READING.md 6.29 in.; NIST erratum
  6.25 in. (`sources/text/ncstar1-9_errata.txt`, lines 92 to 109, which also says the 16-storey model
  used a 12 in. plate "consistent with Frankel drawing 1091"). Agree.
- Stiffeners: UAF 3/4 x 5.5 x 18 in. (p. 81 [PDF 94]); 9114 "PL 5 1/2 x 3/4 x 1'-6 (BS)". Agree.
- Seat support plate: UAF (from Nordenson) 2 x 14 x 18 in. (p. 88 [PDF 101]); 9114/1091 "PL 14 x 2
  x 1'-6 7/8". Close (18 in. against 18 7/8 in.).
- **Girder skew and end position, which UAF's text does not discuss:** READING.md finds A2001 at
  7/8 in 12 (4.17 degrees) to the Column 79 axis, Column 79 rotated about 12.3 degrees from the grid,
  and the girder end about flush with the side-plate ends. From that position it infers that travel
  perpendicular to the girder is not blocked by the side plate, while travel due west on the grid
  enters the recess after about 1.8 in. and reaches the west side plate after about 4.2 in.
  UAF's "trapped" finding assumes the end inside the recess, where it can bear on the plate. NIST's
  reply mentions the angle (NIST reply p. 2). The project's own NIST-replica runs (commit 3e5b539)
  deal with this point and are not repeated here.
- RFC p. 25 describes the A2015 and A2002 connections at Column 79 as 3/8 in. knife brackets 24.5 in.
  and 15.5 in. long "per Frankel drawing 1091". READING.md's reading of 1091 Section A-A shows the
  south-flange member (A2002, W27x94) on two angles L4x3x3/8 and the west member (W36x135) on bent
  plates A778/B778. Not reconciled here; may be a different level or a different reading.

---

## 5. Data a WTC 7 frame model could use

"Primary source cited" gives what UAF or the RFC cites for the value. "None" means no source is
given in the text.

| Item | Value | Where | Primary source cited |
|---|---|---|---|
| Storey height (typical, near Floor 13) | 12 ft 9 in. one storey; 25 ft 6 in. two storeys | UAF p. 37 [PDF 50] | None (stated as effective lengths) |
| Floor 3 level (substation roof) | 33 ft 4 in. | UAF p. 39 [PDF 52] | None |
| Free-fall drop | about 105 ft, 8 storeys (NIST: 32.0 m) | UAF p. 92 [PDF 105]; Fig. 1.6 p. 12 [PDF 25] | NCSTAR 1A |
| Column 79 at Floor 13 | W14x730 + 2 PL 2 in. x 26 in. | UAF p. 37 [PDF 50]; Fig. 3.3 p. 78 [PDF 91]; RFC p. 8 | Drawings (Fig. 1.12 p. 16 [PDF 29], unnamed sheet); RFC cites Frankel drawing 1091 |
| Side plate projection; clear width | 1.79 in.; 17.89 in. | UAF p. 79 [PDF 92] | Frankel 9114 via Brookman 2012 (Fig. 3.5) |
| Girder A2001 | W33x130; bf 11.510 in.; tw 0.580 in. | UAF p. 79 [PDF 92] | Frankel 9114 via Brookman 2012 |
| A2001 seat at Column 79 | 12 in. wide; 6.290 in. lateral travel to clear web; 3.678 in. to west side plate | UAF p. 79 [PDF 92] | Frankel 9114 via Brookman 2012 |
| A2001 seat support plate | 2 in. x 14 in. x 18 in.; weld shear capacity 632,000 lb | UAF p. 88 [PDF 101] | Nordenson report (Arup and Nordenson 2010) |
| Support plate edge | 3.8 in. from column flange face | UAF p. 82 [PDF 95] | None stated (context Frankel 9114) |
| A2001 web stiffeners | 3/4 in. x 5.5 in. x 18 in. | UAF p. 81 [PDF 94]; RFC p. 18 | Frankel 9114 |
| A2001 length | 547 in. (Floor 12 girder) | UAF p. 88 [PDF 101] | Nordenson |
| A2001 length | 540 in. | RFC p. 12 | None |
| Axial gap, A2001 west corner to side-plate protrusion | 0.158 in. at 21 °C | RFC p. 12 | None |
| Floor 12 A2001 stiffness at 10 in. from Column 79 | 7,627 kips/in. | UAF p. 88 [PDF 101] | Nordenson |
| Beams east of A2001, Floor 13 | K3004, C3004, B3004, A3004: W24x55; G3005: W21x44, framing into the wind girder | UAF p. 84 [PDF 97] | Frankel erection drawing E12/13 |
| Lateral support beams | S3007, G3007, K3007 (G3005 to north wall); sizes not given | UAF p. 84 [PDF 97] | Frankel 1985 |
| G3005 position | about 4 ft from A2001's north end at Column 44 | UAF p. 19 [PDF 32] | NIST (as summarised) |
| K3004 length | 644 11/16 in. at 20 °C | RFC p. 13 | None |
| K3004 maximum net expansion | 5.728 in. at 654 °C | RFC p. 17 (Exhibit D) | None (RFC calculation) |
| A2015 and A2002 at Column 79 | 3/8 in. knife brackets, 24.5 in. and 15.5 in., 5/16 in. fillet welds, E70; derived shear 645,000 lb and 407,000 lb | RFC p. 25 | Frankel 1091 (see 4e: differs from repo reading) |
| Typical slab | 20 ga deck + 5.5 in. concrete; 6x6-W1.4xW1.4 WWF at 2.5 in. from top | UAF p. 45 [PDF 58] | None (Fig. 2.25 "Typical floor detail") |
| Equivalent slab moduli | 6,730,000 psi along flutes; 3,285,000 psi across | UAF p. 49 [PDF 62] | UAF calculation |
| Concrete | 3,500 psi; 145 pcf; E 3,408,800 psi; dolomite | UAF p. 32 [PDF 45]; p. 46 [PDF 59] | None |
| Steel grades | A572 Gr 50 beams and interior columns; A36 exterior moment frames | UAF p. 32 [PDF 45] | None |
| Floor load (NIST's) | 88 psf | UAF p. 76 [PDF 89] | NIST (UAF "confirmed") |
| Simple beam test | W24x55, span 52.75 ft, 0.657 kip/ft, slab effective width 114.25 in. | UAF p. 50 to 51 [PDF 63 to 64] | None |
| Connection types | 7 interior types (F, H, K, STP, STC, SWC, MC); exterior moment connections | UAF p. 29 [PDF 42]; p. 56 [PDF 69] | NCSTAR 1A; NCSTAR 1-9A |
| Fire floors | 7 to 9, 11 to 13, 19, 22, 29, 30 | UAF p. 17 [PDF 30] | NCSTAR 1A |
| NIST temperatures (northeast floor analysis) | beams 600 °C; A2001 and A2015 500 °C; columns 300 °C | UAF p. 76 [PDF 89] | NIST |
| Debris damage | 6 exterior columns severed, SW face | UAF p. 94 [PDF 107] | NIST |
| East penthouse support | Columns 79, 80, 81 | UAF p. 94 [PDF 107] | None |
| Column axial forces at Floor 12 to 13 | Table 2.1, below | UAF p. 43 to 44 [PDF 56 to 57] | Numbering from NCSTAR 1A (Fig. 2.24); **values: none** |
| NIST Stage 1/2/3 descent | Stage 1 to 1.75 s, about 2.2 m; Stage 2 free fall 32.0 m from 1.75 s to 4.0 s; Stage 3 4.0 to 5.4 s, 39.6 m | RFC p. 35 to 36 | NCSTAR 1A p. 45 (quoted) |
| NIST global analysis timing | global collapse at 6.3 s after penthouse onset; animation ends 8.1 s | RFC p. 29, 40 to 41 | RFC reading of NIST animation |

### Table 2.1, column axial forces (compressive, kips) for the Floor 12 and 13 assembly
UAF p. 44 [PDF 57]. "Calculated by imposing axial forces acting on the top of Floor 13"
(p. 43 [PDF 56]). Load case, live-load fraction and source of the values are not stated. Column 42
reads "1,6" in the source text layer itself (truncated in the original); the actual value is unknown.

| Col | kips | Col | kips | Col | kips |
|---|---|---|---|---|---|
| 1 | 1,551 | 28 | 1,326 | 56 | 2,854 |
| 2 | 1,161 | 29 | 1,124 | 57 | 2,591 |
| 3 | 916 | 30 | 1,000 | 58 | 3,588 |
| 4 | 935 | 31 | 1,049 | 59 | 1,812 |
| 5 | 984 | 32 | 1,014 | 60 | 1,874 |
| 6 | 931 | 33 | 1,064 | 61 | 3,072 |
| 7 | 883 | 34 | 1,056 | 62 | 1,923 |
| 8 | 861 | 35 | 1,095 | 63 | 1,864 |
| 9 | 793 | 36 | 1,112 | 64 | 3,221 |
| 10 | 799 | 37 | 1,117 | 65 | 1,327 |
| 11 | 772 | 38 | 1,064 | 66 | 2,037 |
| 12 | 728 | 39 | 1,146 | 67 | 3,655 |
| 13 | 775 | 40 | 1,132 | 68 | 1,989 |
| 14 | 810 | 41 | 1,390 | 69 | 2,461 |
| 14A | 1,006 | 42 | "1,6" (truncated in source) | 70 | 3,818 |
| 15 | 1,392 | 43 | 3,404 | 71 | 2,428 |
| 16 | 2,531 | 44 | 3,287 | 72 | 2,618 |
| 17 | 2,018 | 45 | 2,492 | 73 | 3,908 |
| 18 | 1,784 | 46 | 2,306 | 74 | 2,794 |
| 19 | 1,648 | 47 | 2,136 | 75 | 2,652 |
| 20 | 1,603 | 48 | 2,038 | 76 | 4,430 |
| 21 | 1,580 | 49 | 2,016 | 77 | 2,965 |
| 22 | 1,570 | 50 | 2,002 | 78 | 2,798 |
| 23 | 1,585 | 51 | 2,010 | 79 | 5,142 |
| 24 | 1,720 | 52 | 2,040 | 80 | 4,261 |
| 25 | 1,984 | 53 | 2,091 | 81 | 3,941 |
| 26 | 2,348 | 54 | 2,172 |  |  |
| 27 | 3,093 | 55 | 2,289 |  |  |

---

## 6. What this means for the Phase 3 design (short)
- UAF offers no Column 79-alone case, no stated removal time, no damping, and a linear force check
  as its failure criterion, so its "no collapse" result for 79 to 81 is not directly comparable to
  a nonlinear dynamic Column 79 removal.
- The UAF numbers most usable as cross-checks are the Table 2.1 column loads (Column 79: 5,142 kips
  at the Floor 12 to 13 assembly, provenance unstated) and the drawing-based seat geometry, which the
  repo can verify directly against Frankel 1091, 9114 and E12/13.
- NIST's own reply records a 3.5 h sensitivity case in which girders on Floors 12 to 14 around
  Columns 79 to 81 fell without global collapse (NIST reply p. 5, citing NCSTAR 1-9 pp. 603 to 604).
  Checked against the repo copy `sources/text/ncstar1-9.txt`: NCSTAR 1-9 Section 12.4.5, printed
  p. 589 (text lines 25552 onward; the reply's "603 to 604" is presumably PDF pagination), says the
  3.5 h damage had "a few girders connected to Columns 79, 80 and 81 in Floors 12 to 14" fall, "the
  damage was not sufficient to fail other floor structures below Floor 12 or to initiate a vertical
  collapse", and "the structure was stable at the end of the analysis". Section 12.4.4 (text line
  24607) adds that in this case "interior columns did not buckle". So in NIST's own model, local
  floor failures around Column 79 without Column 79 buckling did not lead to collapse; the 4.0 h case
  that did collapse had Column 79 buckle after floor failures from Floor 5 to 14 (RFC p. 22, quoting
  NCSTAR 1-9 pp. 572 to 573: Column 79 "laterally unsupported in the east-west and south directions
  between Floors 5 and 14").
