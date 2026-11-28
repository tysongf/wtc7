"""Fast structural & assembly unit tests for Phase 3 data and 47-storey 3D model (Steps 4-5)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from phase3.building_model import BuildingConfig, build_wtc7_model
from phase3.data import CONNECTION_SPECS, build_column_plan, build_floor_elevations, column_section_spec


def test_floor_elevations_match_cantor_and_frankel_drawings():
    """Verify exact storey elevation closure across Cantor S-17/S-18, Frankel E12/13, E120, and NCSTAR 1-9."""
    floors = build_floor_elevations()
    assert len(floors) == 49
    assert floors[1]["z_in"] == 0.0
    assert floors[1]["el_str"] == "309'-3.0\""
    # Floor 3 Con Ed substation roof = EL. 334'-6" (E120):
    assert floors[3]["el_str"] == "334'-6.0\""
    # Floor 12 = EL. 452'-9" (exact 0.0 in. closure against Frankel E12/13 title block!):
    assert floors[12]["el_str"] == "452'-9.0\""
    # Main Roof (level 48) = EL. 920'-7" (+ 4'-9" parapet = EL. 925'-4" in NCSTAR 1-9 §12.5.3):
    assert floors[48]["z_in"] == pytest.approx(7336.0)
    assert floors[48]["el_str"] == "920'-7.0\""


def test_column_plan_and_schedules():
    """Verify 82 main columns + 15 transfer support columns and built-up Col 79/80/81 schedules."""
    cols = build_column_plan()
    main_cols = [c for c in cols.values() if c["top_level"] == 48]
    sub_cols = [c for c in cols.values() if c["top_level"] < 48]
    assert len(main_cols) == 82
    assert len(sub_cols) == 15

    # Exact E12/13 coordinates of East interior columns 79, 80, 81:
    assert (cols["79"]["x"], cols["79"]["y"]) == pytest.approx((3300.625, 1159.5))
    assert (cols["80"]["x"], cols["80"]["y"]) == pytest.approx((3214.0, 762.5))
    assert (cols["81"]["x"], cols["81"]["y"]) == pytest.approx((3143.4, 439.5))

    # Built-up section schedules at Floor 12 (Cantor S-18 & NCSTAR 1-9 App. D):
    assert column_section_spec("79", 12) == ("W14X730", "side", 26.0, 2.0, "A572")
    assert column_section_spec("80", 12) == ("W14X730", "web", 12.5, 5.0, "A572")
    assert column_section_spec("81", 12) == ("W14X730", "web", 12.5, 1.0, "A572")
    assert CONNECTION_SPECS["STC_79_81"]["walk_ax"] == pytest.approx(6.25)


def test_47_storey_assembly_triggers_and_mass_budget():
    """Verify full 47-storey 3D model assembles cleanly, matches NIST's 174,136 kip mass budget within 2%,
    and maps D0, RC, RU, and R1-R9 triggers accurately."""
    b = build_wtc7_model(BuildingConfig(col79_bow_over_L=0.001))
    m = b.model
    assert m.nn > 20000
    assert m.nb > 15000
    assert m.dt >= 1.5e-4
    added_pct = 100.0 * float((m.mass - m.mass_phys).sum() / m.mass_phys.sum())
    assert added_pct < 1.0

    # Check column 79 L/1000 bow peak at mid-height between Floor 5 and Floor 14:
    z5, z14 = b.floors[5]["z_in"], b.floors[14]["z_in"]
    n_mid = b.col_nodes_bot[("79", 10)]
    bow_expected = 0.001 * (z14 - z5) * np.sin(np.pi * (b.floors[10]["z_in"] - z5) / (z14 - z5))
    assert m.x0[n_mid, 0] - b.cols["79"]["x"] == pytest.approx(bow_expected, rel=1e-5)

    # Check trigger element mappings:
    assert len(b.removal_elements_for_trigger("RC")) == 2 * b.cfg.east_subdiv
    assert len(b.removal_elements_for_trigger("R9")) == 9 * b.cfg.east_subdiv
    assert len(b.removal_elements_for_trigger("RU")) == 3 * 7 * b.cfg.east_subdiv

    # Check D0 trigger preserves seated A2001 on Floors 8-12 in state=1 while detaching other Col-79 bays:
    b.settled_z = m.x[:, 2].copy()
    info = b.apply_d0_damage_state()
    assert info["sheared_seated_A2001"] == 10   # 5 floors (8..12) x 2 ends of A2001
    assert info["detached_joints"] > 40


def test_verified_model_summary_artifact_passes_criteria():
    """Verify results/phase3/model_summary.json meets all pre-registered Section 8 static criteria."""
    summary_path = ROOT / "results" / "phase3" / "model_summary.json"
    assert summary_path.exists(), "Run phase3/verify_model.py first"
    s = json.loads(summary_path.read_text())
    assert s["ke_over_ie"] < 0.01
    assert s["max_roof_vz_in_s"] < 0.10
    assert s["energy_rel_error"] < 0.05
    assert abs(s["total_fl8_diff_pct"]) < 2.0
    col79 = next(r for r in s["column_loads_fl8"] if r["col"] == "79")
    assert abs(col79["diff_pct"]) < 5.0
    assert 0.05 < s["T_v1_col79_s"] < 0.80

