"""Phase 3 structural geometry, schedules, connection capacities, and assumptions (Step 4).

Sources:
  - Frankel erection plan E12/13 rev 4 (`sources/drawings/raw/FOIA09-49_E12_13.tif`)
  - Frankel wind-bracing elevations E120 (`sources/drawings/raw/FOIA09-49_E120.tif`)
  - Frankel connection details 1091, 1370, 9100, 9102, 9114 (`sources/drawings/READING.md`)
  - Irwin G. Cantor structural sheets S-8, S-14, S-15, S-16, S-17, S-17A, S-18, S-22, S-23 (FOIA 11-209)
  - NIST NCSTAR 1-9 (Ch. 2, 5, 8, 11, 12, App. D, App. E) & NCSTAR 1-9A (Ch. 2, 3, 4)

All lengths in inches, forces in kip, stresses in ksi, temperatures in C unless noted.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "phase3"
ASSUMP_MD = ROOT / "docs" / "phase3_assumptions.md"


# ==============================================================================
# 1. Storey elevations (Cantor S-17 & S-18 left margin; verified against E12/13 & E120)
#    Datum z = 0.0 in. at 1st Floor finished slab (EL. 309'-3").
#    Levels: 1..47 = Floors 1..47; 48 = Main Roof (EL. 920'-7"); 49 = Penthouse Roof.
# ==============================================================================

def build_floor_elevations() -> dict[int, dict]:
    """Return level -> {z_in, dh_below_in, el_ft_in, psf_dl_ll, group}."""
    # Storey heights dh from level k-1 to level k (in.), read directly from Cantor S-17 & S-18:
    dh = {
        1: 0.0,
        2: 133.5,   # 11'-1 1/2"  -> EL. 320'-4 1/2"
        3: 169.5,   # 14'-1 1/2"  -> EL. 334'-6" (Con Ed substation roof, matches E120)
        4: 168.0,   # 14'-0"      -> EL. 348'-6"
        5: 171.0,   # 14'-3"      -> EL. 362'-9" (14 in. diaphragm slab)
        6: 156.0,   # 13'-0"      -> EL. 375'-9" (NCSTAR 1-9 §3.3.2: 4.0 m = 13.0 ft)
        7: 159.0,   # 13'-3"      -> EL. 389'-0" (8 in. transfer slab)
    }
    for fl in range(8, 22):
        dh[fl] = 153.0   # 12'-9" typical -> Fl 12 = EL. 452'-9" (exact match to E12/13)
    dh[22] = 177.0       # 14'-9" mechanical
    dh[23] = 168.0       # 14'-0" belt truss (matches S-22)
    dh[24] = 177.0       # 14'-9" belt truss
    for fl in range(25, 46):
        dh[fl] = 153.0   # 12'-9" typical
    dh[46] = 171.0       # 14'-3" mechanical / cooling-tower support
    dh[47] = 153.0       # 12'-9" upper tenant / double-height cooling tower bay
    dh[48] = 178.0       # 14'-10" Main Roof -> z = 7336.0 in. = 611'-4" above Fl 1 (EL. 920'-7")
    dh[49] = 180.0       # 15'-0" East & West Penthouse roofs above Main Roof (S-16)

    # Unfactored service floor loads DL + SDL + 0.25 LL (psf) from NCSTAR 1-9 Fig. 11-17:
    # Tuple is (dead_sdl_psf, design_ll_psf) so live-load fraction (baseline 0.25, T1: 0.0 / 0.50) is parametric.
    def load_spec(fl: int) -> tuple[float, float, str]:
        if fl == 1:
            return (315.0, 100.0, "lobby")
        if fl == 2:
            return (131.0, 150.0, "lower")
        if fl in (3, 4):
            return (146.0, 100.0, "lower")
        if fl == 5:
            return (210.0, 100.0, "diaphragm_5")
        if fl == 6:
            return (115.0, 75.0, "mech_6")
        if fl == 7:
            return (177.5, 50.0, "transfer_7")
        if 8 <= fl <= 20 or 24 <= fl <= 45:
            return (75.0, 50.0, "tenant")
        if 21 <= fl <= 23:
            return (90.0, 75.0, "heavy_tenant")
        if fl == 46:
            return (90.0, 75.0, "mech_46")
        if fl == 47:
            return (75.0, 50.0, "upper_47")
        if fl == 48:
            return (75.0, 30.0, "main_roof")
        return (45.0, 20.0, "penthouse_roof")

    out = {}
    z = 0.0
    base_el_in = 309 * 12 + 3.0  # EL. 309'-3"
    for fl in sorted(dh):
        z += dh[fl]
        dl, ll, grp = load_spec(fl)
        tot_el = base_el_in + z
        ft = int(tot_el // 12)
        rem = tot_el - 12 * ft
        out[fl] = dict(
            level=fl,
            name="Main Roof" if fl == 48 else ("Penthouse Roof" if fl == 49 else f"Floor {fl}"),
            z_in=z,
            dh_below_in=dh[fl],
            el_str=f"{ft}'-{rem:.1f}\"",
            dl_psf=dl,
            ll_psf=ll,
            psf_baseline=dl + 0.25 * ll,
            group=grp,
        )
    return out


# ==============================================================================
# 2. Plan coordinates (X east, Y north in inches) of all 82 main columns +
#    lower-storey transfer support columns from Frankel E12/13 & Cantor S-17A/S-23.
#    Origin: X = 0 at Frankel E12/13 west datum (14'-10" west of Col 1);
#            Y = 0 at South perimeter column centerline (Cols 15..28);
#            North perimeter column centerline (Cols 1, 57..42) is at Y = 1685.0 in. (140'-5").
# ==============================================================================

Y_SOUTH = 0.0
Y_NORTH = 1685.0   # 140'-5" centerline-to-centerline (+ 2x24 in. curtain wall = 144'-5" on E12/13)


def build_column_plan() -> dict[str, dict]:
    """Return col_id -> {x, y, zone, face, z_bot_level, z_top_level, on_substation}."""
    cols: dict[str, dict] = {}

    def add(cid: str, x: float, y: float, zone: str, face: str,
            bot: int = 1, top: int = 48, sub: bool = False):
        cols[cid] = dict(id=cid, x=round(float(x), 3), y=round(float(y), 3),
                         zone=zone, face=face, bot_level=bot, top_level=top, on_substation=sub)

    # ---- North perimeter (Cols 1, 57..42 at Y = 1685.0 in., running stations from E12/13) ----
    north_stations = [
        ("1", 178.0), ("57", 422.5), ("56", 646.5), ("55", 926.5),
        ("54", 1155.0), ("53", 1372.0), ("52", 1589.0), ("51", 1807.0),
        ("50", 2025.0), ("49", 2243.0), ("48", 2460.0), ("47", 2677.0),
        ("46", 2906.5), ("45", 3181.5), ("44", 3456.5), ("43", 3742.5),
        ("42", 4058.25),
    ]
    # Note: Cols 47..53 above Floor 7 sit on MG-27 cantilevers; below Floor 7 they step 81 in. south to 47A..53A!
    for cid, x in north_stations:
        cnum = int(cid)
        if 47 <= cnum <= 53:
            add(cid, x, Y_NORTH, "perimeter", "north", bot=7, top=48, sub=False)
            add(f"{cid}A", x, Y_NORTH - 81.0, "transfer_sub", "north_sub", bot=3, top=7, sub=True)
        else:
            face = "nw_corner" if cid == "1" else ("ne_corner" if cid == "42" else "north")
            add(cid, x, Y_NORTH, "perimeter", face, bot=1, top=48, sub=(cid in ("54",)))

    # ---- South perimeter (Cols 15..28 at Y = 0.0 in., running stations from E12/13) ----
    south_stations = [
        ("15", 772.0), ("16", 981.5), ("17", 1146.5), ("18", 1366.5),
        ("19", 1586.5), ("20", 1807.0), ("21", 2026.5), ("22", 2246.5),
        ("23", 2466.5), ("24", 2686.5), ("25", 2964.5), ("26", 3196.5),
        ("27", 3428.5), ("28", 3701.625),
    ]
    for cid, x in south_stations:
        face = "sw_corner" if cid == "15" else ("se_corner" if cid == "28" else "south")
        add(cid, x, Y_SOUTH, "perimeter", face, bot=1, top=48, sub=False)

    # ---- West perimeter (Cols 2..14, 14A along inclined West wall from Col 1 to Col 15) ----
    p1 = np.array([178.0, Y_NORTH])
    p15 = np.array([772.0, Y_SOUTH])
    L_west = float(np.linalg.norm(p15 - p1))  # 1786.58 in.
    # Slope increments from Col 1 southward (E12/13 west edge):
    west_ds = [131.94, 113.06] + [118.0] * 10 + [119.0, 120.0]
    west_ids = [str(k) for k in range(2, 15)] + ["14A"]
    s_acc = 0.0
    for cid, ds in zip(west_ids, west_ds):
        s_acc += ds
        u = s_acc / (sum(west_ds) + 122.58)
        pt = (1.0 - u) * p1 + u * p15
        add(cid, pt[0], pt[1], "perimeter", "west", bot=1, top=48, sub=False)

    # ---- East perimeter (Cols 29..41 along inclined East wall from Col 28 to Col 42) ----
    p28 = np.array([3701.625, Y_SOUTH])
    p42 = np.array([4058.25, Y_NORTH])
    # 28->29 = 178 in., 12 equal spaces 29..41, 41->42 = 136.75 in. (E12/13 east edge)
    L_east = float(np.linalg.norm(p42 - p28))  # 1722.33 in.
    ds_mid = (L_east - 178.0 - 136.75) / 12.0
    east_ds = [178.0] + [ds_mid] * 12
    s_acc = 0.0
    for idx, ds in enumerate(east_ds):
        s_acc += ds
        cid = str(29 + idx)
        u = s_acc / L_east
        pt = (1.0 - u) * p28 + u * p42
        add(cid, pt[0], pt[1], "perimeter", "east", bot=1, top=48, sub=False)

    # ---- Core interior columns (Cols 58..78: 7 N-S lines x 3 E-W rows, E12/13) ----
    core_x = [
        (("58", "59", "60"), 874.0),    # 72'-10"
        (("61", "62", "63"), 1155.0),   # 96'-3"
        (("64", "65", "66"), 1397.0),   # 116'-5"
        (("67", "68", "69"), 1743.0),   # 145'-3"
        (("70", "71", "72"), 2089.0),   # 174'-1"
        (("73", "74", "75"), 2435.0),   # 202'-11"
        (("76", "77", "78"), 2771.0),   # 230'-11"
    ]
    y_core_rows = (1066.0, 706.0, 454.0)  # North (88'-10"), Middle (58'-10"), South (37'-10")
    # Columns transferred at Floor 7 (start at Floor 7): 58 (MG-21), 59 (MG-22), 61 (Truss 3 -> starts at Fl 5/7),
    # 76 (Truss 1), 77 (Truss 2), 78 (MG-23). Substation-bearing core cols at Floor 3 (S-17A): 64, 67, 70, 73.
    transferred_fl7 = {"58", "59", "76", "77", "78"}
    sub_core = {"64", "67", "70", "73"}
    for trio, xc in core_x:
        for cid, yc in zip(trio, y_core_rows):
            if cid in transferred_fl7:
                add(cid, xc, yc, "core", "interior", bot=7, top=48, sub=False)
            elif cid == "61":
                add(cid, xc, yc, "core", "interior", bot=5, top=48, sub=False)
            elif cid in sub_core:
                add(cid, xc, yc, "core", "interior", bot=3, top=48, sub=True)
            else:
                add(cid, xc, yc, "core", "interior", bot=1, top=48, sub=False)

    # ---- East interior gravity columns (Cols 79, 80, 81, E12/13) ----
    add("79", 3300.625, 1159.5, "east_interior", "interior", bot=1, top=48, sub=False)
    add("80", 3214.000, 762.5,  "east_interior", "interior", bot=1, top=48, sub=False)
    add("81", 3143.400, 439.5,  "east_interior", "interior", bot=1, top=48, sub=False)

    # ---- Lower-floor transfer support columns (Floors 1/3 to 5/7, Cantor S-17, S-17A, S-23) ----
    add("58A", 874.0, 1162.0, "transfer_sub", "core_transfer", bot=3, top=7, sub=True)
    add("58C", 874.0, 970.0,  "transfer_sub", "core_transfer", bot=1, top=7, sub=False)
    add("58B", 874.0, 802.0,  "transfer_sub", "core_transfer", bot=1, top=7, sub=False)
    add("59A", 874.0, 610.0,  "transfer_sub", "core_transfer", bot=1, top=7, sub=False)
    add("61A", 1155.0, 946.0, "transfer_sub", "core_transfer", bot=1, top=7, sub=False)
    add("78A", 2771.0, 334.0, "transfer_sub", "core_transfer", bot=1, top=7, sub=False)
    add("E3",  2915.0, 1126.0, "transfer_sub", "core_transfer", bot=3, top=7, sub=True)
    add("E4",  2915.0, 1006.0, "transfer_sub", "core_transfer", bot=3, top=7, sub=True)

    return cols


# ==============================================================================
# 3. Column & Splice Schedules (Cantor S-17, S-17A, S-18 + NCSTAR 1-9 App. D)
#    Each column tier entry gives (base_shape, plate_kind, pw, pt, grade) for a storey interval.
# ==============================================================================

# Valid AISC W14 shapes in W_shapes.csv ordered heavy to light:
W14_LADDER = [
    "W14X730", "W14X665", "W14X605", "W14X550", "W14X500", "W14X455", "W14X426",
    "W14X398", "W14X370", "W14X342", "W14X311", "W14X283", "W14X257", "W14X233",
    "W14X211", "W14X193", "W14X176", "W14X159", "W14X145", "W14X132", "W14X120",
    "W14X109", "W14X99", "W14X90",
]


def column_section_spec(col_id: str, fl_low: int) -> tuple[str, str, float, float, str]:
    """Return (w_shape, kind, pw, pt, grade) for column `col_id` in storey [fl_low, fl_low+1].

    Exact tier-by-tier transcription from Cantor S-17, S-17A, S-18 for East/Core Columns 76-81,
    73-75, 44, and transfer columns; systematic Cantor S-17/S-18 tier ladder for remaining core
    and perimeter columns.
    """
    # 1. Exact transcriptions for East & East-Core columns (S-17A & S-18):
    if col_id == "79":
        if fl_low < 3:   return ("W14X730", "side", 26.0, 5.0, "A572")
        if fl_low < 5:   return ("W14X730", "side", 26.0, 4.0, "A572")
        if fl_low < 7:   return ("W14X730", "side", 26.0, 3.25, "A572")
        if fl_low < 11:  return ("W14X730", "side", 26.0, 3.0, "A572")
        if fl_low < 17:  return ("W14X730", "side", 26.0, 2.0, "A572")
        if fl_low < 23:  return ("W14X730", "side", 26.0, 1.0, "A572")
        upper79 = {23: "W14X730", 25: "W14X665", 27: "W14X605", 29: "W14X550", 31: "W14X500",
                   33: "W14X455", 35: "W14X426", 37: "W14X370", 39: "W14X311", 41: "W14X257",
                   43: "W14X193", 45: "W14X132", 47: "W14X99"}
        tier = fl_low if fl_low % 2 == 1 else fl_low - 1
        return (upper79.get(tier, "W14X99"), "bare", 0.0, 0.0, "A572")

    if col_id == "80":
        if fl_low < 3:   return ("W14X730", "side", 26.0, 5.0, "A572")
        if fl_low < 9:   return ("W14X730", "web", 12.5, 8.0, "A572")
        if fl_low < 11:  return ("W14X730", "web", 12.5, 6.0, "A572")
        if fl_low < 13:  return ("W14X730", "web", 12.5, 5.0, "A572")
        if fl_low < 15:  return ("W14X730", "web", 12.5, 4.0, "A572")
        if fl_low < 17:  return ("W14X730", "web", 12.5, 3.0, "A572")
        if fl_low < 19:  return ("W14X730", "web", 12.5, 2.0, "A572")
        if fl_low < 21:  return ("W14X730", "web", 12.5, 1.0, "A572")
        upper80 = {21: "W14X730", 23: "W14X665", 25: "W14X605", 27: "W14X550", 29: "W14X500",
                   31: "W14X455", 33: "W14X398", 35: "W14X342", 37: "W14X283", 39: "W14X233",
                   41: "W14X193", 43: "W14X145", 45: "W14X99", 47: "W14X90"}
        tier = fl_low if fl_low % 2 == 1 else fl_low - 1
        return (upper80.get(tier, "W14X90"), "bare", 0.0, 0.0, "A572")

    if col_id == "81":
        if fl_low < 3:   return ("W14X730", "web", 12.5, 4.5, "A572")
        if fl_low < 5:   return ("W14X730", "web", 12.5, 6.5, "A572")
        if fl_low < 7:   return ("W14X730", "web", 12.5, 3.5, "A572")
        if fl_low < 9:   return ("W14X730", "web", 12.5, 3.0, "A572")
        if fl_low < 11:  return ("W14X730", "web", 12.5, 2.0, "A572")
        if fl_low < 15:  return ("W14X730", "web", 12.5, 1.0, "A572")
        upper81 = {15: "W14X730", 17: "W14X730", 19: "W14X665", 21: "W14X665", 23: "W14X605",
                   25: "W14X550", 27: "W14X500", 29: "W14X455", 31: "W14X426", 33: "W14X370",
                   35: "W14X311", 37: "W14X257", 39: "W14X211", 41: "W14X176", 43: "W14X145",
                   45: "W14X99", 47: "W14X90"}
        tier = fl_low if fl_low % 2 == 1 else fl_low - 1
        return (upper81.get(tier, "W14X90"), "bare", 0.0, 0.0, "A572")

    if col_id == "76":
        if fl_low < 9:   return ("W14X730", "web", 12.5, 8.0, "A572")
        if fl_low < 11:  return ("W14X730", "web", 12.5, 6.0, "A572")
        if fl_low < 13:  return ("W14X730", "web", 12.5, 5.0, "A572")
        if fl_low < 15:  return ("W14X730", "web", 12.5, 4.0, "A572")
        if fl_low < 17:  return ("W14X730", "web", 12.5, 3.0, "A572")
        if fl_low < 19:  return ("W14X730", "web", 12.5, 2.0, "A572")
        if fl_low < 21:  return ("W14X730", "web", 12.5, 1.0, "A572")
        upper76 = {21: "W14X730", 23: "W14X665", 25: "W14X605", 27: "W14X550", 29: "W14X500",
                   31: "W14X455", 33: "W14X426", 35: "W14X370", 37: "W14X311", 39: "W14X257",
                   41: "W14X193", 43: "W14X132", 45: "W14X99", 47: "W14X90"}
        tier = fl_low if fl_low % 2 == 1 else fl_low - 1
        return (upper76.get(tier, "W14X90"), "bare", 0.0, 0.0, "A572")

    if col_id in ("77", "78"):
        upper77 = {7: "W14X730", 9: "W14X730", 11: "W14X665", 13: "W14X665", 15: "W14X605",
                   17: "W14X605", 19: "W14X550", 21: "W14X500", 23: "W14X455", 25: "W14X426",
                   27: "W14X398", 29: "W14X370", 31: "W14X342", 33: "W14X283", 35: "W14X233",
                   37: "W14X176", 39: "W14X145", 41: "W14X120", 43: "W14X99", 45: "W14X90", 47: "W14X90"}
        tier = fl_low if fl_low % 2 == 1 else fl_low - 1
        return (upper77.get(tier, "W14X90"), "bare", 0.0, 0.0, "A572")

    # 2. Transfer support columns below Floor 7 (S-17, S-17A):
    if col_id.endswith("A") or col_id in ("58B", "58C", "E3", "E4"):
        if col_id == "61A":
            return ("W14X730", "web", 12.5, 5.5, "A572")
        if col_id == "78A":
            return ("W14X730", "bare", 0.0, 0.0, "A572")
        if col_id in ("E3", "E4"):
            return ("W14X605" if col_id == "E3" else "W14X342", "bare", 0.0, 0.0, "A572")
        return ("W14X665", "bare", 0.0, 0.0, "A572")

    # 3. Remaining Core Columns (58..75, S-17/S-17A/S-18, Grade 50):
    cnum = int(col_id) if col_id.isdigit() else 14
    if 58 <= cnum <= 75:
        # North & heavy core columns (58, 61, 64, 67, 70, 73, 74, 75) start at W14X730 (+ web plates on 70, 73-75 below Fl 15)
        heavy_core = cnum in (58, 61, 64, 67, 70, 73, 74, 75)
        if cnum == 73 and fl_low < 17:
            pt = 8.0 if fl_low < 5 else (6.0 if fl_low < 11 else 3.0)
            return ("W14X730", "web", 12.5, pt, "A572")
        start_idx = 0 if heavy_core else 2  # W14X730 vs W14X605 at Floor 7
        if fl_low < 7:
            return ("W14X730", "web", 12.5, 3.0 if heavy_core else 0.0, "A572") if heavy_core else ("W14X665", "bare", 0.0, 0.0, "A572")
        # Step down the W14 ladder smoothly from Floor 7 to Floor 47 (matching S-17A & S-18)
        prog = max(0.0, (fl_low - 7) / 40.0)
        idx = min(len(W14_LADDER) - 1, int(round(start_idx + prog * (len(W14_LADDER) - 1 - start_idx))))
        return (W14_LADDER[idx], "bare", 0.0, 0.0, "A572")

    # 4. Perimeter Columns (1..57, 14A, Grade A36 per S-17 Note 1 except corner/heavy columns):
    # Corner columns (1, 15, 28, 42) and Cols 44, 55 start at W14X730/W14X665; typical perimeter W14X550/W14X500 at Fl 9-13 (S-17, E12/13)
    if col_id in ("1", "15", "28", "42", "44", "43", "55", "56", "57"):
        start_idx = 0 if col_id in ("1", "15", "28", "42") else 1  # W14X730 or W14X665
    else:
        start_idx = 3 if fl_low < 15 else 4  # W14X550 / W14X500
    if fl_low < 7:
        return (W14_LADDER[max(0, start_idx - 1)], "bare", 0.0, 0.0, "A36")
    prog = max(0.0, (fl_low - 7) / 40.0)
    end_idx = len(W14_LADDER) - 2  # W14X99 / W14X90 at 47th-Roof (matches S-18_L!)
    idx = min(len(W14_LADDER) - 1, int(round(start_idx + prog * (end_idx - start_idx))))
    return (W14_LADDER[idx], "bare", 0.0, 0.0, "A36")


# ==============================================================================
# 4. Perimeter Wind Girder (Spandrel) Schedule (Cantor S-15)
# ==============================================================================

def spandrel_section_spec(face: str, level: int) -> tuple[str, float]:
    """Return (w_shape, mp_conn_kip_in) for perimeter spandrels at `level` from Cantor S-15.
    S-15 gives both member size (W36x300..W36x135, W30x99 at roof) and design moment (kip-ft)."""
    # Unfactored ultimate plastic moment capacity of bolted/welded wind-girder moment connection:
    # From S-15, North/South spandrels are W36x300 (Fl 8-13) tapering to W36x150 (Fl 43-45) and W30x99 (Roof);
    # East/West spandrels are W36x245 / W36x210 tapering to W36x135 and W30x99.
    if level <= 7:
        shape_name = "W36X300" if face in ("north", "south") else "W36X245"
    elif level <= 15:
        shape_name = "W36X300" if face == "north" else ("W36X230" if face == "south" else "W36X230")
    elif level <= 25:
        shape_name = "W36X260" if face == "north" else ("W36X210" if face == "south" else "W36X194")
    elif level <= 35:
        shape_name = "W36X210" if face in ("north", "south") else "W36X170"
    elif level <= 45:
        shape_name = "W36X160" if face in ("north", "south") else "W36X150"
    else:
        shape_name = "W30X99"
    # Plastic moment capacity of A36 (Fy_static ~ 38-42 ksi; NIST Table E-3 fy=36.8 ksi, weld zone)
    # Using Zx from W_shapes (~1110 in^3 for W36x300 down to 312 in^3 for W30x99), connection Mp ~ 0.85 * Fy * Zx:
    from wtc7.sections import shape as get_shape
    s = get_shape(shape_name)
    # Approximate Zx ~ 1.12 * (2 * Ix / d)
    zx_est = 1.12 * (2.0 * s.Ix / s.d)
    mp_conn = 0.85 * 38.0 * zx_est  # kip-in. (weld-zone reduced moment capacity per NCSTAR 1-9A §3.3.1)
    return (shape_name, float(mp_conn))


# ==============================================================================
# 5. Connection Capacity Rules (NCSTAR 1-9 §11.2.4, Tables 11-2, 11-3, 11-4, & Frankel 9114/9102/1091)
# ==============================================================================

CONNECTION_SPECS = {
    # Seated connections (kind = 1 in JointSet: bolts break -> seat bearing active until walk-off!)
    "STC_79_81": dict(
        kind=1, desc="Seated top clip at Cols 79 & 81 (4 x 7/8 A325 bolts, 12-in. seat, 6.25 in. walk-off)",
        vcap=180.0, ncap=180.0, kt=900.0, kc=8000.0, kv=2500.0, gap_c=0.50, walk_ax=6.25, walk_lat=5.50,
    ),
    "STP_EXT": dict(
        kind=1, desc="Seated top plate / clip at exterior columns (4 x 7/8 A325, 4.5 in. walk-off)",
        vcap=180.0, ncap=180.0, kt=900.0, kc=8000.0, kv=2500.0, gap_c=0.50, walk_ax=4.50, walk_lat=4.50,
    ),
    "SWC_CORE": dict(
        kind=1, desc="Seated web clip on core beams (4 x 7/8 A325, 2.5 in. walk-off, NCSTAR 1-9 §11.2.5)",
        vcap=160.0, ncap=140.0, kt=800.0, kc=6000.0, kv=1800.0, gap_c=0.50, walk_ax=2.50, walk_lat=3.50,
    ),
    # Simple shear connections (kind = 0 in JointSet: Table 11-2, 11-3, 11-4 vertical failure loads + bolt/weld tension)
    "K8_W36": dict(
        kind=0, desc="8-bolt knife/bent-plate connection on W36x135 (Table 11-4: V_ult = 436 kip)",
        vcap=436.0, ncap=260.0, kt=1600.0, kc=8000.0, kv=2200.0, gap_c=0.50, walk_ax=1.0, walk_lat=1.0,
    ),
    "H5_W27": dict(
        kind=0, desc="5-row header / knife connection on W27x94 / W27x84 / W30 (Table 11-4: V_ult = 264-267 kip)",
        vcap=265.0, ncap=200.0, kt=1300.0, kc=7000.0, kv=1800.0, gap_c=0.50, walk_ax=1.0, walk_lat=1.0,
    ),
    "F6_EAST": dict(
        kind=0, desc="6-bolt fin / header connection on W24x55 & W21x44 tenant framing (Table 11-2: V_ult = 229 kip)",
        vcap=229.0, ncap=190.0, kt=1200.0, kc=6000.0, kv=1600.0, gap_c=0.50, walk_ax=1.0, walk_lat=1.0,
    ),
    "H4_CORE": dict(
        kind=0, desc="4-row header / fin connection on core girders W21-W24 (Table 11-4: V_ult = 217 kip)",
        vcap=217.0, ncap=175.0, kt=1100.0, kc=6000.0, kv=1500.0, gap_c=0.50, walk_ax=1.0, walk_lat=1.0,
    ),
    "F4_SOUTH": dict(
        kind=0, desc="4-bolt fin connection on south/west W16x26-W16x31 beams (Table 11-2: V_ult = 123-135 kip)",
        vcap=130.0, ncap=120.0, kt=900.0, kc=5000.0, kv=1200.0, gap_c=0.50, walk_ax=1.0, walk_lat=1.0,
    ),
}


# ==============================================================================
# 6. Phase 3 Assumptions Ledger (A100 onward, per docs/phase3_plan.md Step 4)
# ==============================================================================

PHASE3_ASSUMPTIONS = [
    ("A100", "Base boundary & Con Ed substation", "Column bases fixed below Floor 2; substation columns fixed at Floor 3 (z = 303 in.)",
     "in.", "report", "", "NCSTAR 1-9A §3.4.2; Cantor S-17A", "Matches NIST global LS-DYNA boundary"),
    ("A101", "Storey elevations (Floors 1 to Main Roof)", "48 levels from EL. 309'-3\" to EL. 920'-7\" (611'-4\" height)",
     "in.", "drawing", "", "Cantor S-17 & S-18 left margins; verified at Fl 12 (EL. 452'-9\") on E12/13", "Exact to 0.0 in. across S-17, S-18, E12/13, and NCSTAR 1-9 §12.5.3"),
    ("A102", "82-column plan coordinates + 15 transfer sub-columns", "Exact E12/13 stationing (329 ft N, 247 ft S, 140'-5\" N-S col lines)",
     "in.", "drawing", "", "Frankel E12/13 rev 4; Cantor S-17A & S-23", "Closes all perimeter & core bevel triangles within < 1 in."),
    ("A103", "Column section schedule (Floors 1 to Roof)", "Exact S-17/S-17A/S-18 tiers on Cols 73, 76-81 & transfers; Cantor W14 ladder on remaining cols",
     "", "drawing", "", "Cantor S-17, S-17A, S-18; NCSTAR 1-9 App. D", "Includes side cover plates on Col 79 (5\" to 1\") and web plates on Cols 73, 76, 80, 81"),
    ("A104", "Two-storey column splices (odd floors 3..45)", "Milled compression bearing + bolted/welded flange & web splice plates (N_cap ~ 0.35 A Fy_pl)",
     "kip", "drawing", "T3: x 0.50, x 1.50", "Cantor S-17 & S-17A splice details (2'-6\" plates, 5/16\" fillet welds); S-17A tension table (~1000-1100 kip)", "Compression bears across milled ends until lateral shear slip exceeds column half-width"),
    ("A105", "Service gravity load schedule", "Unfactored DL + SDL + 0.25 LL + Fl 7 (22 kip) & Fl 46 (425 + 667 kip) equipment + penthouses",
     "psf, kip", "report", "T1: LL = 0.0, 0.50", "NCSTAR 1-9 Fig. 11-17; NCSTAR 1-9A §3.4.3; Cantor S-16", "Distributed onto floor framing nodes so detached floors carry full slab mass during collapse"),
    ("A106", "Interior shear & seated connection capacities", "Tables 11-2..11-4 ultimate capacities + STC 6.25-in. / STP 4.5-in. / SWC 2.5-in. walk-off",
     "kip, in.", "report", "T2: x 0.75, x 1.25", "NCSTAR 1-9 §11.2.4, §11.2.5, Tables 11-2 to 11-4; June 2012 errata", "Coupled (N/Ncap)^2 + (V/Vcap)^2 = 1 fracture; seated bearing maintained until walk-off"),
    ("A107", "Perimeter spandrel moment connections", "Cantor S-15 W36/W30 schedule, Mp = 0.85 Fy Zx (weld-zone reduced), thu = 0.06 rad",
     "kip-in., rad", "drawing", "", "Cantor S-15; NCSTAR 1-9A §3.3.1", "Elastoplastic rotational hinges with fracture rotation limit"),
    ("A108", "Composite slab in-plane diaphragm & membrane ties", "WWF 6x6 W1.4xW1.4 + deck membrane ties on tenant floors; reinforced concrete ties on Fl 5 & Fl 7",
     "kip", "report", "T4: x 0.50, x 2.0", "NCSTAR 1-9 §2.4.2; NCSTAR 1-9A §2.3.1; Cantor S-5A", "Provides diaphragm bracing while intact and catenary membrane pull up to tear-out"),
    ("A109", "Transfer Trusses 1, 2, 3 and MG-21, 22, 23, 27, 53", "Explicit 3D beam-column & built-up plate-girder elements between Floors 5 and 7",
     "in.", "drawing", "", "Cantor S-23 Plate Girder Schedule & Truss 1-3 elevations; NCSTAR 1-9A §3.4.1", "Captures Col 80 -> Truss 2 -> Col 77 & MG-23 -> Col 78 load path"),
    ("A110", "Storey-to-storey falling-floor impact contact", "Two-body reduced-mass penalty (alpha = 0.1) + viscous restitution (zeta = 0.35) + mu = 0.3",
     "", "assumed", "", "NCSTAR 1-9A §3.2.4 (SOFT=1, mu=0.3); verified in tests/test_phase3_xfe.py", "Zero element or nodal mass deletion upon connection fracture"),
    ("A111", "Mass-proportional damping during collapse", "0.5 % of critical at f_1 (~0.28 Hz -> c = 0.018 /s)",
     "1/s", "assumed", "T6: 0 %, 2.0 %", "Standard structural steel intrinsic damping; NIST value not stated", "Heavy damping used only during pre-trigger static gravity settling"),
    ("A112", "Column 79 initial lateral imperfection in D0", "L / 1000 eastward half-sine bow between Floors 5 and 14",
     "in.", "standard", "T7: L/2000, L/500", "AISC Code of Standard Practice out-of-straightness tolerance", "Used only in D0 where Column 79 is not artificially removed"),
]


def write_phase3_data():
    """Export JSON tables to data/phase3/ and write docs/phase3_assumptions.md."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    floors = build_floor_elevations()
    cols = build_column_plan()
    (DATA_DIR / "floors.json").write_text(json.dumps(floors, indent=2) + "\n")
    (DATA_DIR / "columns.json").write_text(json.dumps(cols, indent=2) + "\n")
    (DATA_DIR / "connections.json").write_text(json.dumps(CONNECTION_SPECS, indent=2) + "\n")

    lines = [
        "# Phase 3 assumptions and structural data provenance (`A100`–`A112`)",
        "",
        "Generated from `phase3/data.py` (`docs/phase3_plan.md` Step 4) before any full-building collapse run.",
        "Primary geometry, storey heights, column schedules, spandrel schedules, and transfer-truss member sizes",
        "are read directly from Frankel erection drawings (`E12/13`, `E120`) and Irwin G. Cantor structural drawings",
        "(`S-8`, `S-14`, `S-15`, `S-16`, `S-17`, `S-17A`, `S-18`, `S-22`, `S-23`).",
        "",
        "| ID | Input | Baseline value | Units | Status | Sweep | Source | Note |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in PHASE3_ASSUMPTIONS:
        aid, inp, val, unit, status, sweep, src, note = row
        lines.append(f"| {aid} | {inp} | {val} | {unit} | {status} | {sweep} | {src} | {note} |")
    lines.append("")
    ASSUMP_MD.write_text("\n".join(lines))
    return floors, cols


if __name__ == "__main__":
    fls, cls = write_phase3_data()
    main_cols = [c for c in cls.values() if c["top_level"] == 48]
    print(f"Wrote {len(fls)} levels (Main Roof z = {fls[48]['z_in']} in. = {fls[48]['el_str']}), "
          f"{len(main_cols)} main columns + {len(cls) - len(main_cols)} transfer sub-columns.")

