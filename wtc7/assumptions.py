"""Single source of truth for every Phase 1 input.

Each entry has an ID, the value used in the baseline, the range swept (if any),
units, the source, and a status:
    report     taken from NCSTAR 1-9 / 1-9A / 1A / errata / FAQ
    drawing    read from a drawing reproduced in NCSTAR 1-9 (digitized)
    standard   taken from a published standard, not checked against a copy here
    secondary  from a secondary source, unverified against a primary document
    assumed    best guess with no published value; swept where it can matter

`scripts/make_assumptions_table.py` renders this list to docs/assumptions.md and
docs/assumptions.csv. Model code reads values through `value(id)` so the table
and the model cannot drift apart.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class A:
    id: str
    name: str
    value: object
    units: str
    source: str
    status: str
    sweep: tuple = field(default=())
    sweep_id: str = ""
    note: str = ""


ASSUMPTIONS = [
    # geometry and members
    A("A01", "Girder, col 44 to col 79", "W33x130, 540 in. long", "", "NCSTAR 1-9 §8.7, Fig. 8-16", "report"),
    A("A02", "Floor beams framing into the girder from the east", "W21x44 (northmost) + 4 x W24x55", "",
      "Fig. 8-16 (Structural Drawing S-8 per April 2012 errata); Fig. 8-22 labels all five as W24x55", "drawing",
      note="Open question Q04: drawing shows W21x44 at the north end, LS-DYNA figure labels all W24x55"),
    A("A03", "Floor beam span", 624.0, "in.", "NCSTAR 1-9 §8.7 (52 ft)", "report",
      note="Applied to all five beams; Fig. 8-16 suggests the spans differ slightly (skewed east face)"),
    A("A04", "Beam positions along girder, measured from col 44", (45.6, 136.8, 246.0, 355.2, 466.8), "in.",
      "Digitized from Fig. 8-16 (3.8, 11.4, 20.5, 29.6, 38.9 ft)", "drawing", note="Estimated +/-6 in."),
    A("A05", "Girder skew from the beam-normal direction", 14.6, "deg",
      "Digitized from Fig. 8-16 (girder runs NNE from col 79 to col 44; beams run east)", "drawing"),
    A("A06", "Studs per floor beam", {"W24x55": 28, "W21x44": 24}, "", "Fig. 8-16 <28>, <24>", "drawing"),
    A("A07", "Fin connection, beam to girder", "F6: 6 x 7/8 in. A325, standard holes", "",
      "NCSTAR 1-9 Table 11-2 (east tenant floor W24x55 and W21x44: F6); §2.4 designation", "report"),
    A("A08", "Seat at col 79 (STC)", "2 seat bolts (standard holes) + 2 top-clip bolts (slotted)", "",
      "NCSTAR 1-9 §2.4, §11.2.5, Fig. 2-20", "report"),
    A("A09", "Seat at col 44 (STP)", "2 seat bolts + 2 top-plate bolts", "", "NCSTAR 1-9 §2.4, §11.2.5", "report",
      note="Top-plate holes assumed slotted like the STC clip"),
    A("A10", "Beam seats at east exterior columns (STP)", "2 seat bolts + 2 top-plate bolts; lateral restraint by column flanges",
      "", "NCSTAR 1-9 §11.2.5", "report"),
    # connection strengths
    A("A11", "Bolt shear strength, 7/8 in. A325, 20 C", 45.0, "kip/bolt", "NCSTAR 1-9 §11.2.4", "report"),
    A("A12", "Bolt strength retention with temperature", "Eq. 14, Table E-8 (tensile strength)", "",
      "NCSTAR 1-9 Appendix E.4", "report"),
    A("A13", "Stud shear strength, 3/4 in., 20 C", 19.5, "kip/stud", "NCSTAR 1-9 §11.2.4", "report"),
    A("A14", "Stud strength retention", "Bolt factor (A12), applied only above 300 C", "",
      "§11.2.5 says 'tensile strength reduction factor for steel' above 300 C; the steel factor itself is in NCSTAR 1-3D, not 1-9, so the bolt factor is used as a proxy",
      "assumed"),
    A("A15", "Connection and stud temperature", "Average of the two connected parts", "", "NCSTAR 1-9 §11.2.5", "report"),
    A("A16", "Column temperature in Phase 1", 20.0, "C", "Not stated for the §8.8 model; columns heated little (FAQ 11: about 300 C peak, later in time)",
      "assumed"),
    # walk-off geometry
    A("A20", "Col 79 seat width", 12.0, "in.", "June 2012 errata (report text said 11 in.)", "report"),
    A("A21", "Lateral walk-off distance at col 79", 6.25, "in.", "June 2012 errata; §11.2.9", "report",
      sweep=(5.5, 6.0, 6.25, 6.5), sweep_id="S2"),
    A("A22", "Axial walk-off distance at col 79", 5.5, "in.", "June 2012 errata", "report"),
    A("A23", "Axial walk-off distance at exterior seats", 4.5, "in.", "NCSTAR 1-9 §11.2.5", "report"),
    A("A24", "Standard-hole half clearance (seat bolts, fin bolts)", 1.0 / 32.0, "in.",
      "AISC 360 Table J3.3: 15/16 in. hole for 7/8 in. bolt", "standard"),
    A("A25", "Top-clip / top-plate slot half allowance", 0.125, "in.",
      "§11.2.5 says slotted, size not given; AISC 360 Table J3.3 short slot 15/16 x 1-1/8 in.", "assumed",
      sweep=(0.0, 0.125, 0.656), sweep_id="S3", note="0.656 in. = long slot 15/16 x 2-3/16 in."),
    A("A26", "Girder end clearance to col 79 face", 0.5, "in.", "§11.2.5 models a gap; value not stated", "assumed",
      sweep=(0.25, 0.5, 1.0), sweep_id="S11"),
    A("A27", "Girder end clearance to col 44 face, beam end clearances", 0.5, "in.", "Not stated", "assumed"),
    A("A28", "Girder lateral gap to col 44 flange", 1.0, "in.", "§8.8 describes contact with the inside of the col 44 flange; gap not stated",
      "assumed", sweep=(0.5, 1.0, 3.0), sweep_id="S12"),
    A("A29", "Beam lateral gap to exterior column flanges", 0.25, "in.", "Not stated", "assumed"),
    # stiffnesses
    A("A30", "Col 79 lateral stiffness when flexible", 731.0, "kip/in.",
      "48 E I / (2h)^3, two storeys pinned, I = 15,051 in.^4 (W14x730 + two 26 x 2 in. plates, App. D), h = 153 in.",
      "assumed", sweep=("fixed", "flexible"), sweep_id="S5"),
    A("A31", "Bolt shear deformation at failure", 0.25, "in.", "Not stated (§11.2.5 uses secant stiffness at ultimate)", "assumed",
      sweep=(0.15, 0.25, 0.35), sweep_id="S13"),
    A("A32", "Stud slip at failure", 0.20, "in.", "Not stated", "assumed", sweep=(0.10, 0.20, 0.30), sweep_id="S14"),
    A("A33", "Friction elastic slip", 0.01, "in.", "Numerical regularization", "assumed"),
    # loads and temperatures
    A("A34", "Floor load for the fire case", 87.5, "psf", "Fig. 11-17 (75 psf dead, 50 psf live) and §11.2.7 (25 % live); matches Fig. 8-24 plateau",
      "report"),
    A("A35", "Girder temperature rule", "(Tg - 20) = 0.828 (Tb - 20)", "", "Fits every row of Table 8-2 and Fig. 8-25", "report"),
    A("A36", "Peak beam temperature, uniform ramp", 600.0, "C", "§8.8, Fig. 8-25", "report",
      sweep=(400.0, 500.0, 600.0, 700.0), sweep_id="S7"),
    A("A37", "Heating then cooling", "monotonic", "", "brief", "assumed", sweep=("monotonic", "heat-cool"), sweep_id="S8"),
    # materials
    A("A38", "Steel for beams and girder", "ASTM A572 Gr. 50", "", "NCSTAR 1-9 §11.2.2", "report"),
    A("A39", "Steel property set", "NIST", "", "NCSTAR 1-9 Appendix E (A572 rebuilt; Table E-4 duplicates E-3)", "report",
      sweep=("NIST", "EC3"), sweep_id="S9"),
    A("A50", "Yield strength scale", 1.0, "", "brief: no WTC 7 steel recovered (FAQ 21)", "assumed",
      sweep=(0.9, 1.0, 1.1), sweep_id="S10"),
    A("A51", "Thermal expansion, NIST set", 1.4e-5, "1/C", "NCSTAR 1-9 §8.7.2 (temperature-dependent function used in LS-DYNA not given)",
      "report"),
    A("A52", "Concrete modulus (slab strips, S6 released)", 3372.0, "ksi", "57000 sqrt(f'c), f'c = 3500 psi (§11.2.2)", "standard"),
    A("A53", "Slab strip area per beam line (S6 released)", 446.0, "in.^2", "4.0 in. average depth (2.5 in. topping + half of 3 in. ribs, §2.4) x 111 in. beam spacing",
      "assumed"),
    # boundary conditions and friction
    A("A40", "Girder studs, lower estimate", 22, "studs", "Metabunk forum estimate (one stud per 2 ft); not a drawing count", "secondary",
      sweep=(0, 22, 30), sweep_id="S1"),
    A("A41", "Girder studs, S-8-10 / Salvarinas", 30, "studs",
      "Reported by an advocacy site citing FOIA drawing S-8-10 and the Salvarinas paper; not verified", "secondary"),
    A("A42", "Seat friction coefficient", 0.30, "", "AISC 360 §J3.8 Class A slip coefficient (proxy); NIST does not describe seat friction",
      "standard", sweep=(0.0, 0.2, 0.3, 0.45, 0.6), sweep_id="S4"),
    A("A43", "Beam-to-slab interface friction after stud failure", 0.30, "", "Not stated; same proxy as A42", "assumed",
      sweep=(0.0, 0.3, 0.6), sweep_id="S15"),
    A("A44", "Girder-to-slab interface", "frictionless contact", "", "NCSTAR 1-9 §11.2.3 (contact transfers gravity, not lateral shear)",
      "report"),
    A("A45", "Slab in-plane constraint", "fixed on all edges", "", "NCSTAR 1-9 §8.8", "report",
      sweep=("fixed", "released"), sweep_id="S6"),
    A("A46", "Column lateral restraint", "fixed", "", "NCSTAR 1-9 §8.8", "report"),
    A("A48", "Orientation of girder bearing faces", "On the building grid: col 79 north flange face and col 44 web face normal N-S; col 44 flange insides normal E-W",
      "", "Fig. 2-20 Section A-A and Fig. 8-21 draw the girder at an angle to column 79; §8.8 names the col 79 north flange and the col 44 web and flanges as contact surfaces; skew 14.6 deg from Fig. 8-16",
      "drawing", sweep=("grid", "square"), note="'square' (face normal to the girder) is the geometry used in the first, superseded baseline run"),
    A("A49", "Friction on bearing faces", "same as seat friction (S4)", "", "Not stated", "assumed"),
    A("A47", "Beam initial out-of-straightness in plan", 1.0 / 1000.0, "x span", "Common design value (AISC Code of Standard Practice L/1000)",
      "standard"),
    # detailed (shell) model, Phase 1 gate item 3 (phase1/shell_model.py)
    A("A70", "Steel shell element size", 1.8, "in.", "NCSTAR 1-9 §8.8 ('typical element sizes ... 1.8 in.')", "report",
      sweep=(3.6, 1.8), sweep_id="mesh", note="3.6 in. is the coarse mesh of the convergence check"),
    A("A71", "Slab shell element size", 7.5, "in.", "NCSTAR 1-9 §8.8", "report"),
    A("A72", "Slab shell",
      {"h": 4.0, "E": 3372.0, "nu": 0.2, "rho": 145.0 / 1728.0 / 386.1 / 1000.0,
       "tension": ((0.0, 0.0002, 0.002, 0.3), (0.50, 0.25, 0.33, 0.33)),
       "compression": ((0.0, 0.00055, 0.3), (2.2, 5.1, 5.1))},
      "in., ksi, -, kip s^2/in.^4; curves as (plastic strain, stress in ksi)",
      "NCSTAR 1-9A §2.3.1: one shell layer, MAT_124 (separate tension and compression curves by rule of mixtures over 4.0 in. of concrete, 0.062 in.^2/in. deck in the strong direction only (averaged over both directions here) and 0.00467 in.^2/in. wire mesh; concrete cracks at about 0.5 ksi; aged f'c 4.9 ksi). Curve points rebuilt from those numbers with deck yield 33 ksi and wire 65 ksi (assumed; NIST's Figs. 2-12 to 2-14 give them only graphically). E from A52; normal-weight concrete, 145 pcf assumed",
      "report", note="An elastic slab clamped the beam ends against their seats in the gravity pilot; NIST's cracking slab does not"),
    A("A73", "Slab extent", {"west_overhang": 8.0, "south_half_spacing": 55.5}, "in.",
      "§8.8: west edge parallel to the girder, about 8 in. beyond the flange; south edge at the midline between two beams (half of the 111 in. spacing of A53); north edge on the col 44 line; east edge on the beam ends",
      "report"),
    A("A74", "Col 79 seat", {"width": 12.0, "slave_len": 12.0, "edge_spacing": 0.25}, "in.",
      "Width: errata (A20). Seat extends 5.5 in. along the girder from its end (axial walk-off distance, A22), aligned with the girder (Fig. 8-21 Section A-A). Seat edges also act on the flange underside (edge contact)",
      "report"),
    A("A75", "Col 79 bearing face half-width", 10.95, "in.", "Half of W14x730 flange width plus one 2 in. side plate (Fig. 8-21 'Plate' spanning the side-plate projections)", "assumed"),
    A("A76", "Col 44 flange contact length along the girder", {"flange_len": 8.0}, "in.", "About half the depth of the exterior column", "assumed"),
    A("A77", "Fin plate", {"t": 0.375, "n": 6, "pitch": 3.0, "edge": 1.5, "width": 4.5, "bolt_line": 3.0}, "in.",
      "F6 connection (A07): 6 bolts. Plate thickness, pitch, edge distance and bolt line are typical single-plate values (AISC), not from a WTC 7 drawing. Plate modelled in the beam web plane, welded to the girder web",
      "assumed"),
    A("A78", "Beam top-flange cope beyond the girder flange tip", 0.5, "in.", "Flush tops (Fig. 8-19 elevation) need a cope; length not stated", "assumed"),
    A("A79", "Exterior seat at the east columns", {"width": 8.0, "length": 4.5, "gage": 3.5, "bolt_edge": 2.0, "slave_len": 10.0},
      "in.", "Seat engagement from the axial walk-off distance (A23); width and bolt layout assumed", "assumed"),
    A("A80", "Bolt axial spring", {"ka": 1000.0, "ka_top": 100.0, "tcap": 54.1}, "kip/in., kip",
      "§8.8: separate shear and axial springs. Seat bolts: 1000 kip/in. (bolt through a stiff seat plate). Clip-angle and top-plate bolts: 100 kip/in., the bending stiffness of the L6x4x3/8 clip angle leg (3EI/L^3, L about 3.4 in.) or of the 3/8 in. top plate between the column flanges (about 192EI/L^3), in series with the bolt; the plates themselves are not meshed. Tension capacity Fnt Ab = 90 ksi x 0.601 in.^2 (AISC 360 Table J3.2, not checked against a copy here) times the bolt factor (A12)",
      "assumed", note="A rigid 1000 kip/in. top tie clamped the beam ends in the gravity pilot"),
    A("A81", "Stud axial spring", {"ka": 500.0}, "kip/in.", "Ties the slab to the beam in tension; no tension failure modelled", "assumed"),
    A("A82", "Contact penalty and normal damping", (0.1, 0.1), "(m/dt^2 fraction, damping ratio)",
      "Penalty scaled by the slave nodal mass so contact does not reduce the stable time step (LS-DYNA SOFT = 1 practice); stick stiffness equal to the normal penalty",
      "assumed"),
    A("A83", "Hourglass coefficient (stiffness form)", 0.1, "", "LS-DYNA default QM = 0.1; checked against CalculiX S4 buckling (results/phase1/shell/verification.md)", "standard"),
    A("A84", "Mass-proportional damping", 1.26, "1/s", "5 % of critical at 2 Hz (about the floor's first vertical mode); NIST does not state damping", "assumed"),
    A("A85", "Hold after the temperature ramp", 1.4, "s", "§8.8, Figs. 8-24 and 8-25: ramp ends at 2.6 s, analysis shown to 4.0 s", "report"),
    A("A86", "Time-step safety factor", 0.9, "", "Fraction of the smallest element's stable step", "assumed"),
    A("A87", "Girder erection bolt positions", {"gage": 5.5, "edge": 2.5}, "in.",
      "Two bolts each in the seat and in the clip angle or top plate (A08, A09), on either side of the web; gage and end distance assumed (Fig. 8-21 draws them close to the web)",
      "assumed"),
    A("A88", "Col 79 side cover plates as a lateral stop (Q12)", {"clear_half_width": 8.95, "depth": 1.8}, "in.",
      "W14x730 flange width 17.9 in. between the plates; projection (26 - 22.4) / 2 = 1.8 in. (App. D). 'clear': girder end outside the recess (Fig. 8-21 Section A-A reading); 'stop': end inside it",
      "drawing", sweep=("clear", "stop"), sweep_id="Q12"),
    A("A30m", "Col 79 effective mass when flexible (S5)", 0.03, "kip s^2/in.",
      "About half of two storeys of W14x730 with side plates (900 lb/ft x 25.5 ft / g); only sets the column's lateral frequency (about 25 Hz)",
      "assumed"),
    A("A89", "Girder web region in contact with each beam end", 12.0, "in.", "Half-length of the girder web patch searched for beam-end bearing", "assumed"),
    # geometry read from the shop, erection and structural drawings (sources/drawings/READING.md);
    # used when a model is run with geometry = "drawings". A01 to A05, A20, A25, A26, A28 and A48
    # above are the earlier values digitized from NCSTAR 1-9 figures (geometry = "digitized").
    A("A90", "Girder skew to the north-south grid", 16.53, "deg", "Frankel E12/13 rev 4: bevel 3 9/16 in 12 (clearly legible); S-8 scales to about 16.2 deg",
      "drawing", note="Supersedes A05 (14.6 deg, digitized from Fig. 8-16)"),
    A("A91", "Girder span and end position", {"span": 547.625, "end79": 13.0}, "in.",
      "Span between column centres 45'-7 5/8 (E12/13, 9114, 9102). Girder end at col 79 13.0 in. from the column centre along the girder (9114: bolt line 1'-5 1/4 from the centre, 4 1/4 from the end; partly legible)",
      "drawing"),
    A("A92", "Floor beams framing into the girder from the east, stations from col 44 centre along the girder",
      {"stations": (50.0625, 151.6875, 272.0625, 392.375, 512.75), "sections": ("W21X44", "W24X55", "W24X55", "W24X55", "W24X55"),
       "lengths": (608.25, 616.25, 625.75, 635.25, 644.0), "studs": (24, 28, 28, 28, 28)}, "in.",
      "E12/13: G3005, A3004, B3004, C3004, K3004 (running sums of written segments; the sum is 1/2 in. short of the stated span); piece lengths as written (K3004 fraction not legible)",
      "drawing", note="Supersedes A02 to A04 and A06; a W12x26 (P3016) framing in from the west is not modelled, as in NIST's model"),
    A("A93", "Col 79 orientation", {"rotation": 12.36, "girder_to_axis": 4.17}, "deg",
      "Girder meets col 79 at 7/8 in 12 (9114, 1091; clearly legible); column axes rotated about 12.3 deg clockwise from the grid (inferred from three members)",
      "drawing", note="Supersedes A48 for col 79: the north flange face is 4.17 deg off square to the girder, not 14.6 deg"),
    A("A94", "Col 79 north flange and side plates", {"half_depth": 11.1875, "plate_end": 13.0, "plate_inner": 8.9375, "plate_t": 2.0}, "in.",
      "W14x730 as fabricated 22 3/8 x 17 7/8 (1091); 2 PL 26 x 2 across the flange tips, centred: face at 11 3/16, plate ends at 13.0, inner faces at +/-8 15/16 from the column centre",
      "drawing", note="Projection 1 13/16 in. is inferred (not dimensioned)"),
    A("A95", "Col 79 seat (pf) and bolts", {"width": 12.0, "length": 8.25, "seat_bolts": 17.25, "clip_bolts": 15.0, "gage": 5.5},
      "in.", "PL 8 1/4 x 1 x 1'-0 aligned with the girder, back edge at the flange face; bolt lines from the column centre along the girder (1091, 9114). Clip angle L6x4x3/8 with standard 15/16 in. holes (sheet default)",
      "drawing"),
    A("A96", "Col 44", {"section": "W14X665", "slot": 0.125, "lat_west": 0.25, "lat_east": 1.38, "end_gap": 0.5, "seat_len": 8.5}, "in.",
      "On the grid, web parallel to the north wall (1370, 9102). Girder enters between the flanges (12.6 in. clear) at 16.5 deg; west flange cut back to clear the column flange (cut-back not dimensioned: 0.25 in. clearance assumed); east gap from geometry; top plate 1 1/8 x 15/16 slots",
      "drawing", note="Girder end to web face not shown (girder piece drawing 2001 not released): 0.5 in. at the nearest corner assumed (A27)"),
    A("A98", "Slab south edge (drawings set)", {"south_half_spacing": 54.0}, "in.",
      "Midline between K3004 and the next beam south, D3004, 9'-0 away (E12/13); §8.8 puts the south edge on such a midline",
      "drawing"),
    A("A99", "Slab east edge beyond the beam ends", 8.5, "in.",
      "§8.8 fixes the slab edges along the exterior girders; the east spandrel runs on the exterior column line, taken as the 0.5 in. end gap (A27) plus half the depth of a W14 exterior column (about 8 in.; column sizes on the east wall not read)",
      "assumed", note="Placing the fixed edge right at the beam ends clamps them between seat and slab (found in the gravity pilot)"),
    A("A97", "Girder end stiffeners at col 79", {"width": 5.5, "t": 0.75, "height": 18.0, "from_end": 0.75}, "in.",
      "PL 5 1/2 x 3/4 x 1'-6 both sides of the web (9114, clearly legible); 3/4 in. from the end (partly legible). NIST says they were not modelled",
      "drawing", sweep=("omitted", "as drawn"), note="Baseline omits them, as NIST did; 'as drawn' is a sensitivity run"),
    # column 79 check
    A("A60", "Col 79 axial load, floor 8, gravity", 7525.0, "kip", "NCSTAR 1-9 §11.3.1", "report"),
    A("A61", "Col 79 section, floors 5 to 14", "W14x730 + two 26 in. side plates, 2 in. (floor 14) to 3 in. (floor 5)", "",
      "NCSTAR 1-9 Appendix D", "report"),
    A("A62", "Storey height, tenant floors", 153.0, "in.", "NCSTAR 1-9 §5.3 (12 ft 9 in.)", "report"),
]

_BY_ID = {a.id: a for a in ASSUMPTIONS}


def value(aid):
    return _BY_ID[aid].value


def get(aid):
    return _BY_ID[aid]
