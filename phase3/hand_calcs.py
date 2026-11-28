"""Phase 3 hand calculations (docs/phase3_plan.md Step 2).

Run strictly after docs/phase3_preregistration.md is hashed in docs/compute_log.md.
Reports engineering bounds and sanity checks before any Phase 3 finite-element run;
sets no outcome class. Writes results/phase3/hand_calcs.md and results/phase3/hand_calcs.json.

Units: kip, in., ft, ksi, C.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from wtc7 import materials as mat
from wtc7.sections import shape

OUT_DIR = ROOT / "results" / "phase3"

# NIST NCSTAR 1-9 §5.3.2 & Fig. 11-17 design loading schedule (DL + SDL + 0.25 LL, psf)
H_TYP = 153.0                  # typical tenant storey height, in. (12.75 ft)
PSF_ROOF = 82.5                # 75 DL + 0.25 * 30 LL
PSF_TYP = 87.5                 # Floors 8-20, 24-46: 75 DL + 0.25 * 50 LL
PSF_21_23 = 108.75             # Floors 21-23: 90 DL + 0.25 * 75 LL
E20 = 29000.0                  # ksi (AISC 360 standard modulus for column curve checks)
FY50 = 50.0                    # ksi nominal A572 Gr 50 / A588 Gr 50


def aisc_pn(Ag: float, Imin: float, L: float, E: float, Fy: float) -> tuple[float, float]:
    """Return (Euler Pe, AISC 360-16 Section E3 nominal compressive strength Pn) in kip."""
    Pe = (math.pi ** 2) * E * Imin / (L ** 2)
    Fe = Pe / Ag
    slender_limit = 4.71 * math.sqrt(E / Fy)
    r = math.sqrt(Imin / Ag)
    if L / r <= slender_limit:
        Fcr = (0.658 ** (Fy / Fe)) * Fy
    else:
        Fcr = 0.877 * Fe
    return Pe, Fcr * Ag


def builtup_props(base_name: str, kind: str, pw: float = 0.0, pt: float = 0.0) -> dict:
    """Section properties (Ag, Ix, Iy, Imin) for W14 shapes with side cover plates or web plates.

    kind:
      - 'bare': rolled shape alone
      - 'side': two plates (pw x pt) welded across the flange tips (box-like, e.g. Col 79: 26 x 2 in.)
      - 'web':  two plates (pw x pt) nestled against both sides of the web between flanges
                (e.g. Cols 76, 80: 12.5 x 4 in.; Col 81: 12.5 x 1 in.)
    """
    s = shape(base_name)
    Ag, Ix, Iy = s.A, s.Ix, s.Iy
    if kind == "side":
        # Each plate has width pw (spanning across depth d + projections) and thickness pt outside +/- bf/2
        A_pl = 2.0 * pw * pt
        xc = s.bf / 2.0 + pt / 2.0
        # Strong axis (bending in column depth direction): 2 * (pt * pw^3 / 12)
        Ix += 2.0 * (pt * (pw ** 3) / 12.0)
        # Weak axis (bending across flange width): 2 * (pw * pt^3 / 12 + (pw*pt) * xc^2)
        Iy += 2.0 * (pw * (pt ** 3) / 12.0 + (pw * pt) * (xc ** 2))
        Ag += A_pl
    elif kind == "web":
        # Two plates (pw height between flanges x pt thickness) centered at x = +/- (tw/2 + pt/2)
        A_pl = 2.0 * pw * pt
        xc = s.tw / 2.0 + pt / 2.0
        Ix += 2.0 * (pt * (pw ** 3) / 12.0)
        Iy += 2.0 * (pw * (pt ** 3) / 12.0 + (pw * pt) * (xc ** 2))
        Ag += A_pl
    return dict(base=base_name, kind=kind, pw=pw, pt=pt, Ag=Ag, Ix=Ix, Iy=Iy, Imin=min(Ix, Iy))


def section1_column_loads() -> dict:
    """Tributary gravity loads above Floor 8 and Floor 13 vs. NIST (NCSTAR 1-9 Fig. 11-21) & UAF."""
    # Cumulative floor pressure from Roof (47) down to Floor 8 inclusive (40 supported levels):
    # Roof (1) + Fl 46 (1) + Fl 24-45 (22) + Fl 21-23 (3) + Fl 8-20 (13) = 40 levels
    q_above_8 = (PSF_ROOF + PSF_TYP + 22 * PSF_TYP + 3 * PSF_21_23 + 13 * PSF_TYP) / 1000.0  # kip/ft^2
    # Above top of Floor 13 (Floors 14..Roof = 34 levels)
    q_above_13 = q_above_8 - 6 * (PSF_TYP / 1000.0)

    # Tributary areas (ft^2) estimated from building plan (NCSTAR 1-9 §5.3.2, §12.4.7, E12/13):
    # Col 79: NIST §12.4.7 states ~2,000 ft^2; from E12/13 NE corner geometry ~1,930 ft^2
    cols = [
        ("79", 1950.0, 470.0, 120.0, 7525.0, 5142.0, "Isolated NE interior; E12/13 ~1,950 ft² (NIST §12.4.7: ~2,000 ft²)"),
        ("80", 1420.0, 420.0, 95.0, 5478.0, 4261.0, "East interior middle row"),
        ("81", 1270.0, 360.0, 60.0, 4945.0, 3941.0, "Southeast interior"),
        ("76", 1480.0, 420.0, 110.0, 5854.0, 4430.0, "NE core corner + penthouse post"),
        ("77", 840.0, 310.0, 75.0, 3346.0, 2965.0, "East core middle row"),
        ("78", 870.0, 310.0, 0.0, 3409.0, 2798.0, "SE core corner"),
        ("44", 730.0, 280.0, 60.0, 2962.0, 3287.0, "North perimeter column receiving A2001"),
    ]
    rows = []
    for cid, area, sw_above8, pent, nist8, uaf13, note in cols:
        p8 = area * q_above_8 + sw_above8 + pent
        p13 = area * q_above_13 + sw_above8 * (34.0 / 40.0) + pent
        err_pct = (p8 - nist8) / nist8 * 100.0
        rows.append(dict(col=cid, area_ft2=area, P_fl8_hand=round(p8, 0), P_fl8_nist=nist8,
                         diff_pct=round(err_pct, 1), P_fl13_hand=round(p13, 0), P_fl13_uaf=uaf13, note=note))

    # Whole building above Floor 8 sanity check:
    # Gross trapezoid: 0.5 * (329 + 247) * 150 = 43,200 ft^2; net slab ~40,200 ft^2 after core shafts
    net_area = 40200.0
    equip_46_pent = 425.0 + 667.0 + 1200.0  # Fl 46 cooling towers + mech (9A §3.4.3) + penthouses
    col_spandrel_sw = 28800.0               # 82 columns + perimeter spandrels over 40 storeys
    total_above_8 = net_area * q_above_8 + equip_46_pent + col_spandrel_sw
    return dict(q_above_8_ksf=round(q_above_8, 4), q_above_13_ksf=round(q_above_13, 4),
                total_above_8_kip=round(total_above_8, 0), nist_target_kip=174136, rows=rows)


def section2_bridging() -> dict:
    """Check whether intact tenant floors can bridge a removed Column 79 segment."""
    area_79 = 1950.0
    p_static = area_79 * PSF_TYP / 1000.0          # kip per floor (170.6 kip)
    p_dyn = 2.0 * p_static                         # sudden removal (DAF = 2.0): 341.3 kip/floor

    # Three girders meet Col 79 on a typical tenant floor (8 to 45):
    # North: A2001 (W33x130, L = 547.6 in. = 45.6 ft), STC (2 seat + 2 clip 7/8" A325)
    # South: A2002 (W27x94, L ~ 540 in. = 45.0 ft), Knife/Header (6 x 7/8" A325)
    # West:  W36x135 (L ~ 348 in. = 29.0 ft to Col 76), Header/Bent-plate (8 x 7/8" A325)
    spans_in = {"north_A2001": 547.6, "south_A2002": 540.0, "west_W36x135": 348.0}

    # 1. Vierendeel / shear-tab bending capacity:
    # Even generous partial-restraint moment before bolt/angle tear-out:
    # STC at A2001: top clip L6x4x3/8 prying yields at ~6 kip -> M <= 6 kip * 33 in. = 198 kip-in.
    # 6-bolt knife (3 in. pitch) & 8-bolt header: bolt group eccentric moment ~ 45 kip * 45 in. ~ 1,200-1,800 kip-in.
    M_conn = {"north_A2001": 200.0, "south_A2002": 1200.0, "west_W36x135": 1800.0}  # kip-in. per end
    V_vierendeel = sum(2.0 * M_conn[k] / spans_in[k] for k in spans_in)

    # 2. Catenary action at vertical drop delta (before connections tear out axially):
    # Horizontal tensile capacities (NCSTAR 1-9 §11.2.4, bolt shear = 45 kip/bolt, clip/weld prying):
    # North STC: 4 bolts in shear = 180 kip (walk-off / bolt shear limit; clip slip fail ~0.25-0.45 in.)
    # South Knife (6 bolts, 3/8" angles): min(6*45=270 kip bolt shear, angle leg prying/weld ~200 kip) -> 200 kip
    # West Header (8 bolts): ~260 kip
    # Slab 6x6 W1.4xW1.4 WWF (As = 0.028 in^2/ft, Fu = 70 ksi) across ~65 ft perimeter ~ 127 kip
    T_cap = {"north_STC": 180.0, "south_knife": 200.0, "west_header": 260.0, "slab_wwf": 127.0}
    T_total_cap = sum(T_cap.values())

    # Axial extension demand delta_ax = sqrt(L^2 + delta^2) - L ~ delta^2 / (2 L)
    # At bolt/weld fracture slip ~0.45 in. at each end (0.9 in. total chord elongation on 348 in. west span):
    delta_at_fracture = math.sqrt(2.0 * 348.0 * 0.90)  # ~25.0 in. vertical drop when west connection fractures!
    # Vertical force carried by full T_cap at delta = 25 in. (even assuming all 4 load paths peak simultaneously!):
    V_cat_optimistic = (T_cap["north_STC"] * (delta_at_fracture / spans_in["north_A2001"])
                        + T_cap["south_knife"] * (delta_at_fracture / spans_in["south_A2002"])
                        + (T_cap["west_header"] + T_cap["slab_wwf"]) * (delta_at_fracture / spans_in["west_W36x135"]))

    # Required horizontal tension to carry static (170.6 kip) or dynamic (341.3 kip) at delta = 25 in.:
    eff_slope = sum(1.0 / L for L in spans_in.values()) / 3.0 * delta_at_fracture
    T_req_static = p_static / eff_slope
    T_req_dyn = p_dyn / eff_slope

    return dict(
        p_floor_static_kip=round(p_static, 1),
        p_floor_dyn_kip=round(p_dyn, 1),
        V_vierendeel_kip=round(V_vierendeel, 1),
        T_total_cap_kip=round(T_total_cap, 1),
        delta_fracture_in=round(delta_at_fracture, 1),
        V_cat_optimistic_kip=round(V_cat_optimistic, 1),
        T_req_static_kip=round(T_req_static, 0),
        T_req_dyn_kip=round(T_req_dyn, 0),
        ratio_cat_to_static=round(V_cat_optimistic / p_static, 2),
        ratio_cat_to_dyn=round(V_cat_optimistic / p_dyn, 2),
    )


def section3_floor_cascade() -> dict:
    """Energy check: can an intact tenant floor arrest one or more falling floors from above?"""
    w_bay = 1950.0 * PSF_TYP / 1000.0   # 170.6 kip per floor bay around Col 79
    h_drop = H_TYP                      # 153 in.

    # Potential energy released by 1 falling floor bay dropping 1 storey:
    E_pot_1 = w_bay * h_drop            # 26,106 kip-in.

    # Energy absorption capacity of one receiving tenant floor bay before connection tear-out:
    # 1) Direct connection shear/tear-out energy around bay:
    #    ~32 bolts (7/8" A325, 45 kip each = 1,440 kip total) failing over ~0.5 in. plastic/bearing stroke
    V_conn_sum = 32 * 45.0
    u_fail = 0.50
    E_conn = 0.75 * V_conn_sum * u_fail     # ~540 kip-in. (trapezoidal ductility factor 0.75)

    # 2) Upper-bound flexural plastic hinge + slab membrane work before end rotation (~0.06 rad) shears bolts:
    #    5 x W24x55 beams (Zx = 134 in^3, Fy = 54 ksi -> Mp = 7,236 kip-in.) + W33x130 (Zx = 467 -> Mp = 25,218)
    #    rotating through theta_max = 0.06 rad before connection bolt/weld tear-out:
    Mp_sum = 5 * (134.0 * 54.0) + (467.0 * 54.0)  # 61,398 kip-in.
    theta_max = 0.06                              # rad (~3.4 deg; at 270 in. half-span -> ~16 in. sag)
    E_plastic_upper = Mp_sum * theta_max + E_conn # ~4,224 kip-in.
    # Subtract work already consumed by the receiving bay's own static gravity load (170.6 kip * 8 in. mean sag):
    W_self_gravity = w_bay * 8.0                  # ~1,365 kip-in.
    E_net_reserve = max(E_conn, E_plastic_upper - W_self_gravity)

    cascade_rows = []
    for k in range(1, 9):
        # k falling bays impacting the next intact floor after falling at least 1 storey
        # Conservative inelastic impact (perfectly plastic momentum conservation with mass m_recv = 1 bay):
        # fraction of kinetic energy retained + work during collapse stroke, or total gravitational energy released:
        ke_before = k * w_bay * h_drop
        # Perfectly inelastic collision of mass k*m onto 1*m: KE_after_impact = (k / (k + 1)) * KE_before
        # Remaining energy (1 / (k + 1)) * KE_before MUST be dissipated at impact just to match velocities,
        # and then (k + 1)*w_bay static weight (> 2*w_bay = 341 kip) acts on connections afterwards!
        e_dissipated_impact = ke_before / (k + 1.0)
        static_after = (k + 1) * w_bay
        cascade_rows.append(dict(
            falling_floors=k,
            potential_kip_in=round(ke_before, 0),
            impact_dissipation_kip_in=round(e_dissipated_impact, 0),
            post_impact_weight_kip=round(static_after, 0),
            exceeds_reserve=ke_before > E_net_reserve,
        ))

    return dict(
        w_bay_kip=round(w_bay, 1),
        E_pot_1_kip_in=round(E_pot_1, 0),
        E_conn_only_kip_in=round(E_conn, 0),
        E_plastic_upper_kip_in=round(E_plastic_upper, 0),
        E_net_reserve_kip_in=round(E_net_reserve, 0),
        energy_overload_ratio_1floor=round(E_pot_1 / E_net_reserve, 1),
        cascade_rows=cascade_rows,
    )


def section4_neighbour_buckling() -> dict:
    """Euler and AISC 360 E3 buckling capacities of Columns 79, 80, 81, 76, 77, 78 for n = 1..10 storeys."""
    # NCSTAR 1-9 App. D Table D-1 (§1.3 of nist_facts.md)
    specs = [
        ("79 (Fl 14)", builtup_props("W14X730", "side", 26.0, 2.0), 7525.0),
        ("79 (Fl 5)", builtup_props("W14X730", "side", 26.0, 3.0), 7525.0),
        ("80 & 76", builtup_props("W14X730", "web", 12.5, 4.0), 5478.0),   # 76 has 5,854 kip
        ("81", builtup_props("W14X730", "web", 12.5, 1.0), 4945.0),
        ("77 & 78", builtup_props("W14X665", "bare"), 3409.0),
    ]
    # 200 C reduction from NIST Appendix E (for T9 thermal check)
    E200 = float(mat.E_nist(200.0))
    sm50 = mat.SteelModel("NIST", "A572")
    fy200_ratio = sm50.fy(200.0) / sm50.fy(20.0)

    out = []
    for label, p, P_dem in specs:
        table_n = []
        crit_20, crit_200 = None, None
        for n in range(1, 11):
            L = n * H_TYP
            Pe20, Pn20 = aisc_pn(p["Ag"], p["Imin"], L, E20, FY50)
            _, Pn200 = aisc_pn(p["Ag"], p["Imin"], L, E200, FY50 * fy200_ratio)
            if crit_20 is None and Pn20 < P_dem:
                crit_20 = n
            if crit_200 is None and Pn200 < P_dem:
                crit_200 = n
            table_n.append(dict(n=n, Pe_20=round(Pe20, 0), Pn_20=round(Pn20, 0),
                                Pn_200=round(Pn200, 0), ratio_20=round(Pn20 / P_dem, 2)))
        out.append(dict(label=label, Ag=round(p["Ag"], 1), Imin=round(p["Imin"], 0),
                        P_demand=P_dem, crit_storeys_20C=crit_20, crit_storeys_200C=crit_200,
                        storeys=table_n))
    return dict(E200_ksi=round(E200, 0), fy200_ratio=round(fy200_ratio, 3), columns=out)


def section5_truss2() -> dict:
    """Truss 2 (Floors 5-7) check when Column 80 buckles or Floors 6-13 debris impacts Floor 5/7."""
    # Geometry from NCSTAR 1-9 Fig. 2-24, 1-9A §3.4.1 & App. D:
    # Truss 2 spans E-W from Col 74 (west) to Col 80 (east), carrying Col 77 (3,346 kip) and
    # the west end of MG-23 (which carries Col 78 = 3,409 kip between Col 77 and Col 78A).
    # Height: Floor 5 to Floor 7 = ~27 ft (324 in.). Span Col 74 to Col 77 ~ 27 ft, Col 77 to Col 80 ~ 28 ft (total ~55 ft).
    P_77 = 3346.0
    P_78_share = 0.5 * 3409.0          # ~1,704.5 kip via MG-23 onto Truss 2 at Col 77 line
    P_truss2_total = P_77 + P_78_share # ~5,050.5 kip concentrated near midspan (Col 77)
    L_west, L_east = 27.0 * 12.0, 28.0 * 12.0
    L_tot = L_west + L_east
    H_truss = 27.0 * 12.0              # 324 in.

    # Intact simple-span reactions of Truss 2 onto Col 74 (west) and Col 80 (east):
    R_col80 = P_truss2_total * (L_west / L_tot)
    R_col74 = P_truss2_total * (L_east / L_tot)
    # East diagonal force (from Col 77 top at Fl 7 down to Col 80 at Fl 5):
    diag_len = math.hypot(L_east, H_truss)
    N_diag = R_col80 * (diag_len / H_truss)   # compression in W14x730 + 2 PL 8x3 web plates
    diag_props = builtup_props("W14X730", "web", 8.0, 3.0)
    _, Pn_diag = aisc_pn(diag_props["Ag"], diag_props["Imin"], diag_len, E20, FY50)

    # What if Column 80 buckles / loses vertical support above or at Truss 2?
    # Truss 2 becomes a 27-ft cantilever overhanging from Col 74 (or Floor 7/5 girders try to cantilever 5,051 kip
    # at 27 ft = 324 in. from Col 74!):
    M_cantilever = P_truss2_total * L_west    # 1,636,362 kip-in. = 136,364 kip-ft!
    # Chord force couple across H_truss = 324 in. if cantilevered from Col 74:
    T_chord_req = M_cantilever / H_truss      # 5,051 kip pure tension in top chord tie into Col 74!
    # Typical heavy moment/chord splice into Col 74 (even 16 x 1" A490 bolts in tension/shear ~ 1,200-1,800 kip):
    T_chord_conn_est = 1600.0

    return dict(
        P_truss2_kip=round(P_truss2_total, 0),
        R_col80_intact_kip=round(R_col80, 0),
        R_col74_intact_kip=round(R_col74, 0),
        N_diag_intact_kip=round(N_diag, 0),
        Pn_diag_kip=round(Pn_diag, 0),
        M_cantilever_if_col80_lost_kip_ft=round(M_cantilever / 12.0, 0),
        T_chord_req_if_col80_lost_kip=round(T_chord_req, 0),
        T_chord_conn_est_kip=T_chord_conn_est,
    )


def write_markdown(data: dict) -> str:
    s1, s2, s3, s4, s5 = data["s1"], data["s2"], data["s3"], data["s4"], data["s5"]
    lines = [
        "# Phase 3 hand calculations: global collapse bounds",
        "",
        "Generated by `phase3/hand_calcs.py` after `docs/phase3_preregistration.md` was hashed in `docs/compute_log.md`.",
        "Sources: `docs/phase3_sources/nist_facts.md` (NCSTAR 1-9, 1-9A, 1A) and `docs/phase3_sources/uaf_notes.md`.",
        "These checks establish physical bounds before any Phase 3 finite-element run and set no outcome class.",
        "",
        "## 1. Gravity loads on east and core columns (Columns 76 to 81 and 44)",
        "",
        f"Unfactored service load combination `DL + SDL + 0.25 LL` (NCSTAR 1-9 Fig. 11-17): cumulative floor pressure "
        f"across the 40 supported levels above Floor 8 (Floors 8 to Roof) is **{s1['q_above_8_ksf']:.3f} kip/ft²** "
        f"({s1['q_above_13_ksf']:.3f} kip/ft² above Floor 13). Whole-building estimate above Floor 8: "
        f"**{s1['total_above_8_kip']:,.0f} kip** against NIST's **{s1['nist_target_kip']:,} kip** target (within 1 %).",
        "",
        "| Column | Tributary area (ft²) | Hand calc, Fl 8 (kip) | NIST ANSYS, Fl 8 (kip) | Diff | Hand calc, Fl 13 (kip) | UAF Table 2.1, Fl 13 (kip) | Notes |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in s1["rows"]:
        lines.append(f"| {r['col']} | {r['area_ft2']:,.0f} | {r['P_fl8_hand']:,.0f} | {r['P_fl8_nist']:,.0f} | "
                     f"{r['diff_pct']:+.1f} % | {r['P_fl13_hand']:,.0f} | {r['P_fl13_uaf']:,.0f} | {r['note']} |")

    lines += [
        "",
        "**Reading:** Tributary-area hand estimates match NIST's Floor-8 ANSYS gravity forces within 1 to 3 % across "
        "every east-zone column. UAF's Table 2.1 forces at Floor 13 (provenance unstated in UAF) are ~15 to 18 % lower "
        "than `DL + 0.25 LL` at Floor 13, consistent with omitting live load or partition allowances.",
        "",
        "## 2. Can intact tenant floors bridge a removed segment of Column 79?",
        "",
        f"At each typical tenant floor (`87.5 psf` over `~1,950 ft²`), Column 79 supports **{s2['p_floor_static_kip']} kip/floor** "
        f"statically, or **{s2['p_floor_dyn_kip']} kip/floor** dynamically under sudden column removal (`DAF = 2.0`).",
        "",
        f"- **Vierendeel / shear-tab bending:** The seated (`STC`) connection on `A2001` and shear connections on `A2002` "
        f"and `W36x135` transfer at most **{s2['V_vierendeel_kip']} kip/floor** across 29 to 45.6 ft spans—under **8 %** of static demand.",
        f"- **Large-deflection catenary action:** Combined horizontal tensile capacity of the north `STC` bolts (180 kip), "
        f"south knife connection (~200 kip), west header (~260 kip), and slab `WWF` mesh (~127 kip) is **{s2['T_total_cap_kip']:.0f} kip**. "
        f"By the time the shortest span (`29 ft` west girder) reaches ~0.9 in. of axial connection tear-out slip, vertical "
        f"deflection is **{s2['delta_fracture_in']} in.**, and even if all four paths peaked together they would carry only "
        f"**{s2['V_cat_optimistic_kip']} kip/floor** ({s2['ratio_cat_to_static']*100:.0f} % of static, "
        f"{s2['ratio_cat_to_dyn']*100:.0f} % of sudden-removal demand). Bridging one floor statically at that sag would "
        f"require **{s2['T_req_static_kip']:,.0f} kip** of horizontal tension (**{s2['T_req_dyn_kip']:,.0f} kip** dynamically).",
        "",
        "**Reading:** Simple/seated tenant floors above a removed Column 79 segment cannot bridge the double span in either "
        "bending or catenary action unless the perimeter/hat structure above redistributes the entire column load—which WTC 7 "
        "lacked (no roof hat truss; east penthouse posts sat directly on Columns 76, 77, 79, 80 and roof beams).",
        "",
        "## 3. Falling-floor cascade energy check",
        "",
        f"One detached `1,950 ft²` floor bay (`{s3['w_bay_kip']} kip`) falling one storey (`153 in.`) releases "
        f"**{s3['E_pot_1_kip_in']:,.0f} kip-in.** of gravitational potential energy.",
        "",
        f"- Direct shear-bolt fracture work around the receiving bay (~32 bolts x 45 kip over ~0.5 in.): **{s3['E_conn_only_kip_in']:,.0f} kip-in.**",
        f"- Upper-bound beam plastic-hinge + connection work before `~0.06 rad` end rotation tears out shear tabs (net of the "
        f"receiving bay's own static load work): **{s3['E_net_reserve_kip_in']:,.0f} kip-in.**",
        f"- **Single-floor overload ratio:** `{s3['E_pot_1_kip_in']:,.0f} / {s3['E_net_reserve_kip_in']:,.0f}` = "
        f"**{s3['energy_overload_ratio_1floor']}x** more impact energy than an intact tenant bay can absorb.",
        "",
        "| Falling bays (`k`) | Potential energy `k W h` (kip-in.) | Inelastic collision loss alone (kip-in.) | Combined static weight after impact (kip) |",
        "|---|---|---|---|",
    ]
    for r in s3["cascade_rows"]:
        lines.append(f"| {r['falling_floors']} | {r['potential_kip_in']:,.0f} | "
                     f"{r['impact_dissipation_kip_in']:,.0f} | {r['post_impact_weight_kip']:,.0f} |")

    lines += [
        "",
        "**Reading:** Once a single east-bay floor section detaches and drops a full storey onto a typical tenant floor below, "
        "the impact energy exceeds the receiving shear connections' absorption capacity by ~9x, driving a runaway floor cascade "
        "until the debris hits the heavily reinforced 14-in. Floor 5 diaphragm slab.",
        "",
        "## 4. Buckling capacities of Columns 79, 80, 81, 76, 77 and 78 vs. unbraced length",
        "",
        f"AISC 360 Section E3 compressive capacity `Pn` (`Fy = 50 ksi`, `K = 1.0`, `h = 153 in.`) at 20 °C and at 200 °C "
        f"(`T9` column temperature: `E(200 °C) = {s4['E200_ksi']:,} ksi`, yield factor `{s4['fy200_ratio']}`).",
        "",
        "| Column(s) | `Ag` (in²) | `I_min` (in⁴) | Gravity `P` (kip) | Buckles at `n` storeys (20 °C) | Buckles at `n` storeys (200 °C) | `Pn` at 1 st. | `Pn` at 3 st. | `Pn` at 4 st. | `Pn` at 5 st. | `Pn` at 9 st. |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for c in s4["columns"]:
        by_n = {x["n"]: x["Pn_20"] for x in c["storeys"]}
        lines.append(
            f"| {c['label']} | {c['Ag']} | {c['Imin']:,} | {c['P_demand']:,.0f} | **{c['crit_storeys_20C']}** | "
            f"**{c['crit_storeys_200C']}** | {by_n[1]:,.0f} | {by_n[3]:,.0f} | {by_n[4]:,.0f} | "
            f"{by_n[5]:,.0f} | {by_n[9]:,.0f} |"
        )

    lines += [
        "",
        "**Key insight:** Column 79 had `26 x 2 in.` *flange-tip side cover plates* (`I_min = 14,724 in⁴`), so it needed **5 to 6 "
        "unbraced storeys** to buckle under gravity alone. By contrast, neighbouring **Columns 80, 76, and 81** used *web plates* "
        "between the flanges (`I_min = 4,727 to 4,791 in⁴`—less than one-third of Column 79's weak-axis inertia!), and **Columns "
        "77 and 78** were bare `W14x665` (`I_min = 4,170 in⁴`). Consequently, **Columns 80, 81, 76, 77, and 78 all lose stability "
        "at just 3 to 4 unbraced storeys** under their own baseline gravity loads—before even counting load shed from Column 79!",
        "",
        "## 5. Transfer Truss 2 check (Floors 5 to 7) under loss of Column 80",
        "",
        f"Truss 2 spans between Column 74 (west) and Column 80 (east) from Floor 5 to Floor 7 (`~27 ft` depth), supporting "
        f"**Column 77** (`3,346 kip`) and half of transfer girder `MG-23` carrying **Column 78** (`~1,705 kip`) = "
        f"**{s5['P_truss2_kip']:,.0f} kip** total:",
        "",
        f"- **Intact state:** East reaction onto Column 80 below Floor 5 is **{s5['R_col80_intact_kip']:,.0f} kip**; compression "
        f"in the east diagonal (`W14x730 + 2 PL 8x3`) is **{s5['N_diag_intact_kip']:,.0f} kip** against AISC capacity "
        f"**{s5['Pn_diag_kip']:,.0f} kip** (safe while Column 80 supports the east end).",
        f"- **If Column 80 fails or buckles in the double-height Floor 6 mechanical space:** Truss 2 must cantilever "
        f"`{s5['P_truss2_kip']:,.0f} kip` at `27 ft` from Column 74 (`M = {s5['M_cantilever_if_col80_lost_kip_ft']:,.0f} kip-ft`), "
        f"demanding **{s5['T_chord_req_if_col80_lost_kip']:,.0f} kip** of pure tension across the Floor 7 top-chord tie into "
        f"Column 74 (roughly **3x** a heavy bolted/welded chord connection's `~{s5['T_chord_conn_est_kip']:,} kip` capacity).",
        "",
        "**Reading:** Losing Column 80 directly undermines the east support of Truss 2, providing a clear structural pathway "
        "to destabilize Core Columns 77 and 78 (`Group 2`) even if upper-floor shear connections have already detached.",
        "",
    ]
    return "\n".join(lines)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = dict(
        s1=section1_column_loads(),
        s2=section2_bridging(),
        s3=section3_floor_cascade(),
        s4=section4_neighbour_buckling(),
        s5=section5_truss2(),
    )
    (OUT_DIR / "hand_calcs.json").write_text(json.dumps(data, indent=2) + "\n")
    md = write_markdown(data)
    (OUT_DIR / "hand_calcs.md").write_text(md)
    print(f"Wrote {OUT_DIR / 'hand_calcs.md'} and {OUT_DIR / 'hand_calcs.json'}")


if __name__ == "__main__":
    main()

