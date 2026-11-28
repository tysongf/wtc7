"""47-storey 3D WTC 7 global structural model in wtc7.xfe (Step 5).

Assembles Floors 2 through 47, Main Roof (level 48), and East/West Penthouses (level 49)
from the primary drawing data in `phase3/data.py`:
  - All 82 main columns + 15 lower-floor transfer support columns with Cantor S-17/S-17A/S-18
    built-up & W14 tiers and explicit two-storey column splices at odd floors (5..45);
  - Rigid Con Edison substation boundary at Floor 3 and fixed column bases at Floor 2
    (matching NIST NCSTAR 1-9A §3.4.2);
  - Transfer Trusses 1, 2, 3 and plate girders MG-21, MG-22, MG-23, MG-27, MG-53 (Floors 5-7,
    Cantor S-23);
  - Perimeter moment frame (WG-1..58, Cantor S-15) with belt trusses at Floors 5-7 and 22-24
    (Cantor S-22, Frankel E120) and lower-core wind bracing (Floors 2-7);
  - Breakable 6-DOF interior girders & floor-beam bands (`F`, `K`, `H`, `STC`, `STP`, `SWC`,
    NCSTAR 1-9 Tables 11-2..11-4), composite slab diaphragm/membrane ties (`T4`), and
    storey-to-storey falling-floor `ImpactContact` carrying full slab & framing mass;
  - Pre-registered event monitors (`G1`..`G5`) and triggers (`D0`, `R1`..`R9`, `RC`, `RU`, `RU_debris`).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from phase3.data import (
    CONNECTION_SPECS,
    build_column_plan,
    build_floor_elevations,
    column_section_spec,
    spandrel_section_spec,
)
from wtc7 import xfe
from wtc7.materials import bolt_strength_factor
from wtc7.sections import shape as get_shape

G_ACC = 386.1
H_TYP = 153.0   # typical storey height, in. (event threshold in phase3_preregistration.md §2)


@dataclass
class BuildingConfig:
    """Configuration for baseline, trigger, and parameter-sweep runs (T1..T9)."""
    ll_frac: float = 0.25               # T1: 0.0, 0.25, 0.50
    conn_scale: float = 1.0             # T2: 0.75, 1.0, 1.25 (interior shear & seated capacities)
    splice_scale: float = 1.0           # T3: 0.50, 1.0, 1.50 (column splice tension/shear/bending)
    slab_scale: float = 1.0             # T4: 0.50, 1.0, 2.0  (slab membrane tensile capacity)
    fy_scale: float = 1.0               # T5: 0.90, 1.0, 1.10 (steel yield strength)
    collapse_zeta: float = 0.005        # T6: 0.0, 0.005, 0.020 (fraction of critical at f1 ~ 0.28 Hz)
    col79_bow_over_L: float = 0.0       # T7: 0.001 baseline in D0 (0.0005, 0.002 in T7; 0 in removal runs)
    wtc1_debris: bool = False           # T8: SW Zone 1 (Cols 14A..20 Fl 7-17) + Zone 2 (Col 20 > Fl 43)
    elevated_temps: bool = False        # T9: Cols 76-81 at 200 C (Fl 7-14), east/core framing at 450 C (Fl 8-13)
    east_subdiv: int = 2                # Mesh refinement check: 2 baseline, 4 refined in east zone
    dt_min: float = 2.0e-4              # Courant floor (s) for short transfer stubs (< 0.1 % added mass)


def plate_girder_section(name: str, bf: float, tf: float, tw: float, d_total: float) -> xfe.BeamSection:
    """Built-up I-shaped plate girder section from Cantor S-23 Plate Girder Schedule (12 active fibres)."""
    hw = max(d_total - 2.0 * tf, 1.0)
    edges_y = np.linspace(-bf / 2.0, bf / 2.0, 5)
    yc = 0.5 * (edges_y[:-1] + edges_y[1:])
    afl = np.full(4, tf * (bf / 4.0))
    zfl = 0.5 * (d_total - tf)
    edges_z = np.linspace(-hw / 2.0, hw / 2.0, 5)
    zw = 0.5 * (edges_z[:-1] + edges_z[1:])
    aw = np.full(4, tw * (hw / 4.0))
    yf = np.concatenate([yc, yc, np.zeros(4)])
    zf = np.concatenate([np.full(4, zfl), np.full(4, -zfl), zw])
    Af = np.concatenate([afl, afl, aw])
    J = (2.0 * bf * (tf**3) + hw * (tw**3)) / 3.0
    return xfe.BeamSection(name, yf, zf, Af, float(J), depth=d_total, width=bf)


def grouped_w_section(name: str, shape_name: str, mult: float) -> xfe.BeamSection:
    """Multi-beam band section (e.g. `mult` parallel W24x55 beams representing a bay band)."""
    base = xfe.w_beam_section(name + "_1", shape_name)
    return xfe.BeamSection(name, base.yf[:12], base.zf[:12], base.Af[:12] * mult, base.J * mult,
                           depth=base.depth, width=base.width * mult)


def _point_in_poly(pts: np.ndarray, poly: np.ndarray) -> np.ndarray:
    """Vectorized ray-casting point-in-polygon for pts (N, 2) inside closed polygon poly (M, 2)."""
    x, y = pts[:, 0], pts[:, 1]
    inside = np.zeros(len(pts), dtype=bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        cond = (y1 > y) != (y2 > y)
        x_int = x1 + (y - y1) * (x2 - x1) / ((y2 - y1) if (y2 != y1) else 1e-12)
        inside ^= cond & (x < x_int)
    return inside


@dataclass
class WTC7Building:
    """Assembled 47-storey 3D model and structural metadata for triggers, monitors, and viewer export."""
    cfg: BuildingConfig
    model: xfe.Model
    floors: dict[int, dict]
    cols: dict[str, dict]
    col_nodes_bot: dict[tuple[str, int], int]      # (col_id, level) -> node id at top of lower segment
    col_nodes_top: dict[tuple[str, int], int]      # (col_id, level) -> node id at base of upper segment
    col_elem_ids: dict[tuple[str, int], np.ndarray]  # (col_id, fl_low) -> beam element ids in [fl_low, fl_low+1]
    roof_col_nodes: dict[str, int]                 # col_id ('1'..'81') -> Main Roof (level 48) node id
    north_roof_nodes: np.ndarray                   # North face roofline nodes (for G5)
    east_pent_nodes: np.ndarray                    # East penthouse roof nodes (for G2)
    west_pent_nodes: np.ndarray                    # West penthouse & screenwall roof nodes
    interior_joints: xfe.JointSet
    spandrel_joints: xfe.JointSet
    splice_joints: xfe.JointSet
    slab_ties: xfe.JointSet
    joint_meta: list[dict]                         # per interior joint: {floor, colA, colB, bay_col79, is_A2001_79}
    slab_meta: list[dict]                          # per slab tie: {floor, colA, colB, bay_col79}
    settled_z: np.ndarray = None                   # (nn,) settled vertical positions at end of gravity step

    def temperatures(self, _t: float) -> np.ndarray:
        """Group temperatures: [0: ambient 20 C, 1: heated cols (200 C in T9), 2: heated floors (450 C in T9)]."""
        if self.cfg.elevated_temps:
            return np.array([20.0, 200.0, 450.0])
        return np.array([20.0, 20.0, 20.0])

    def column_axial_loads_at_level(self, fl_low: int = 7) -> dict[str, float]:
        """Return compressive axial force (kip, positive in compression) in each column in [fl_low, fl_low+1].
        Default `fl_low = 7` is immediately below Floor 8, carrying all 40 supported levels (Floors 8..Roof)
        for direct comparison against NCSTAR 1-9 Fig. 11-21."""
        out = {}
        for (cid, fl), eids in self.col_elem_ids.items():
            if fl == fl_low and len(eids):
                # bdiag[:, 0] is N_ax (tension positive => compression = -N_ax)
                out[cid] = -float(self.model.bdiag[eids, 0].mean())
        return out

    def total_gravity_above_floor8(self) -> float:
        """Sum of all 82 column compressive forces supporting Floor 8 through Roof (kip)."""
        loads8 = self.column_axial_loads_at_level(7)
        return float(sum(loads8.values()))

    def settle_gravity(self, t_ramp: float = 0.60, t_settle: float = 1.85) -> dict:
        """Ramp unfactored gravity smoothly and damp vibrations until KE/IE < 1 % and roof |v_z| < 0.1 in./s."""
        m = self.model
        m._prepare()
        T_arr = self.temperatures(0.0)
        m.Tprev[:] = T_arr
        while m.t < t_settle - 0.5 * m.dt:
            m.Tnow[:] = T_arr
            if m.t < t_ramp:
                lam = 0.5 * (1.0 - math.cos(math.pi * m.t / t_ramp))
                m.damping = 10.0
            elif m.t < t_settle - 0.45:
                lam = 1.0
                m.damping = 15.0
            else:
                lam = 1.0
                m.damping = 32.0
            m.step(lam)
            m.Tprev[:] = m.Tnow

        self.settled_z = m.x[:, 2].copy()
        # Reset collapse-phase damping per T6 (f_1 ~ 0.28 Hz => omega_1 ~ 1.76 rad/s => c = 2 * zeta * omega_1)
        omega_1 = 2.0 * math.pi * 0.28
        m.damping = 2.0 * self.cfg.collapse_zeta * omega_1

        roof_ids = np.array(list(self.roof_col_nodes.values()), np.int32)
        ke_over_ie = float(m.kinout[0] / max(m.energy[0], 1e-12))
        max_roof_vz = float(np.max(np.abs(m.v[roof_ids, 2])))
        return dict(
            t_settled=float(m.t),
            ke_over_ie=ke_over_ie,
            max_roof_vz_in_s=max_roof_vz,
            total_above_fl8_kip=self.total_gravity_above_floor8(),
            col_loads_fl8=self.column_axial_loads_at_level(7),
        )

    def save_settled_checkpoint(self, path) -> None:
        """Save settled gravity state to compressed `.npz` (~2 MB) so multiple triggers skip re-settling."""
        m = self.model
        arrays = dict(
            t=np.array([m.t]), cycle=np.array([m.cycle]), w_ext=np.array([m.w_ext]),
            x=m.x, Rnode=m.Rnode, v=m.v, w=m.w, settled_z=self.settled_z,
            b_plastic=m.b_plastic, bel=m.bel, bq=m.bq, bsig=m.bsig, bepsp=m.bepsp, bm1=m.bm1, bdiag=m.bdiag,
            energy=m.energy, kinout=m.kinout,
        )
        for idx, js in enumerate(m.joint_sets):
            arrays[f"js{idx}_state"] = js.state
            arrays[f"js{idx}_jq"] = js.jq
            arrays[f"js{idx}_fsv"] = js.fsv
            arrays[f"js{idx}_lost"] = np.array([js.lost_energy])
        np.savez_compressed(path, **arrays)

    def load_settled_checkpoint(self, path) -> None:
        """Restore settled gravity state from `.npz` in ~0.03 s."""
        m = self.model
        if not getattr(m, "_prepared", False):
            m._prepare()
        d = np.load(path)
        m.t = float(d["t"][0])
        m.cycle = int(d["cycle"][0])
        m.w_ext = float(d["w_ext"][0])
        m.x[:] = d["x"]; m.Rnode[:] = d["Rnode"]; m.v[:] = d["v"]; m.w[:] = d["w"]
        self.settled_z = d["settled_z"].copy()
        m.b_plastic[:] = d["b_plastic"]; m.bel[:] = d["bel"]
        m.bq[:] = d["bq"]; m.bsig[:] = d["bsig"]; m.bepsp[:] = d["bepsp"]; m.bm1[:] = d["bm1"]; m.bdiag[:] = d["bdiag"]
        m.energy[:] = d["energy"]; m.kinout[:] = d["kinout"]
        for idx, js in enumerate(m.joint_sets):
            js.state[:] = d[f"js{idx}_state"]
            js.jq[:] = d[f"js{idx}_jq"]
            js.fsv[:] = d[f"js{idx}_fsv"]
            js.lost_energy = float(d[f"js{idx}_lost"][0])
        omega_1 = 2.0 * math.pi * 0.28
        m.damping = 2.0 * self.cfg.collapse_zeta * omega_1

    # ------------------------------------------------------------------
    # Triggers, event monitors (G1..G5), and collapse runner (§2-§7)
    # ------------------------------------------------------------------
    def removal_elements_for_trigger(self, trigger: str) -> np.ndarray:
        """Return beam element indices smoothly removed over `t_r` for removal triggers."""
        eids = []
        if trigger.startswith("R") and trigger[1:].isdigit():
            n_rem = int(trigger[1:])
            fl_lo, fl_hi = 14 - n_rem, 14
            for fl in range(fl_lo, fl_hi):
                eids.extend(self.col_elem_ids.get(("79", fl), []))
        elif trigger == "RC":
            for fl in (11, 12):
                eids.extend(self.col_elem_ids.get(("79", fl), []))
        elif trigger in ("RU", "RU_debris"):
            for cid in ("79", "80", "81"):
                for fl in range(6, 13):
                    eids.extend(self.col_elem_ids.get((cid, fl), []))
        return np.array(eids, dtype=np.int32)

    def apply_d0_damage_state(self) -> dict:
        """Apply pre-registered D0 trigger (phase3_preregistration.md §5.3):
        Release Column 79 floor bays on Floors 6-13 so they fall onto Floor 5, while keeping
        North seated girders A2001 on Floors 8-12 resting on their seats with sheared bolts (state=1)."""
        n_detached = 0
        n_seated = 0
        for idx, jm in enumerate(self.joint_meta):
            fl = jm["floor"]
            if jm["bay_col79"] and 6 <= fl <= 13:
                if (jm["is_A2001_79"] or jm["is_A2001_44"]) and 8 <= fl <= 12:
                    if self.interior_joints.state[idx] == 0:
                        self.interior_joints.state[idx] = 1
                        self.interior_joints.lost_energy += float(self.interior_joints.fsv[idx, 5])
                        self.interior_joints.break_time[idx] = self.model.t
                        n_seated += 1
                else:
                    if self.interior_joints.state[idx] < 2:
                        self.interior_joints.state[idx] = 2
                        self.interior_joints.lost_energy += float(self.interior_joints.fsv[idx, 5])
                        self.interior_joints.detach_time[idx] = self.model.t
                        n_detached += 1
        n_slab_rel = 0
        for idx, sm in enumerate(self.slab_meta):
            if sm["bay_col79"] and 6 <= sm["floor"] <= 13:
                if self.slab_ties.state[idx] < 2:
                    self.slab_ties.state[idx] = 2
                    self.slab_ties.lost_energy += float(self.slab_ties.fsv[idx, 5])
                    self.slab_ties.detach_time[idx] = self.model.t
                    n_slab_rel += 1
        return dict(detached_joints=n_detached, sheared_seated_A2001=n_seated, released_slab_ties=n_slab_rel)

    def run_collapse(
        self,
        trigger: str,
        t_r: float = 0.025,
        max_post_trigger_s: float = 30.0,
        sample_dt: float = 0.05,
        frame_dt: float = 0.25,
    ) -> dict:
        """Execute a governed collapse simulation from the settled gravity state (`self.settled_z` must exist)."""
        if self.settled_z is None:
            raise RuntimeError("Call settle_gravity() before run_collapse().")
        m = self.model
        t_trig = float(m.t)
        is_removal = trigger != "D0"
        rem_eids = self.removal_elements_for_trigger(trigger) if is_removal else np.zeros(0, np.int32)
        d0_info = self.apply_d0_damage_state() if trigger == "D0" else {}

        # Neighbour column set for G3 (§2):
        g3_cols = ("76", "77", "78") if trigger in ("RU", "RU_debris") else ("80", "81", "76")
        int24_nodes = np.array([self.roof_col_nodes[str(k)] for k in range(58, 82)], np.int32)
        east_roof_nodes = np.array([self.roof_col_nodes[str(k)] for k in range(28, 43)], np.int32)
        east_x0 = m.x[east_roof_nodes, 0].copy()
        col79_roof = self.roof_col_nodes["79"]

        events: dict[str, float | None] = {"G1": None, "G2": None, "G3": None, "G4": None, "G5": None}
        g3_first_col: str | None = None
        t_total: float | None = None
        t_north_onset_1in: float | None = None
        peak_east_tilt_before_g5_in = 0.0
        max_energy_rel_err = 0.0

        ts_hist, north_drop_hist, ep_drop_hist, c79_drop_hist, ke_hist, err_hist = [], [], [], [], [], []
        frames_t, frames_xyz = [], []
        next_sample = 0.0
        next_frame = 0.0
        diverged = False

        T_arr = self.temperatures(t_trig)
        m.Tprev[:] = T_arr
        while True:
            t_rel = float(m.t - t_trig)
            if t_rel >= max_post_trigger_s - 0.5 * m.dt:
                break
            if t_total is not None and t_rel >= (t_total + 2.0) - 0.5 * m.dt:
                break

            if is_removal and len(rem_eids):
                if t_rel < t_r:
                    fac = max(0.0, 1.0 - (t_rel + m.dt) / max(t_r, m.dt))
                    m.bfac[rem_eids] = fac
                else:
                    m.bfac[rem_eids] = 0.0
                    if events["G1"] is None:
                        events["G1"] = round(t_rel, 5)

            m.Tnow[:] = T_arr
            m.step(1.0)
            m.Tprev[:] = m.Tnow
            t_rel = float(m.t - t_trig)

            if not np.isfinite(m.kinout[0]):
                diverged = True
                break

            # Check G1..G5 every 10 cycles (~1.7 ms resolution)
            if m.cycle % 10 == 0:
                dz_79 = float(self.settled_z[col79_roof] - m.x[col79_roof, 2])
                dz_ep = float(np.mean(self.settled_z[self.east_pent_nodes] - m.x[self.east_pent_nodes, 2]))
                dz_north = float(np.mean(self.settled_z[self.north_roof_nodes] - m.x[self.north_roof_nodes, 2]))

                if not is_removal and events["G1"] is None and dz_79 > H_TYP:
                    events["G1"] = round(t_rel, 5)
                if events["G2"] is None and dz_ep > H_TYP:
                    events["G2"] = round(t_rel, 5)
                if events["G3"] is None:
                    for gc in g3_cols:
                        nd_gc = self.roof_col_nodes[gc]
                        if float(self.settled_z[nd_gc] - m.x[nd_gc, 2]) > H_TYP:
                            events["G3"] = round(t_rel, 5)
                            g3_first_col = gc
                            break
                if events["G4"] is None:
                    if float(np.min(self.settled_z[int24_nodes] - m.x[int24_nodes, 2])) > H_TYP:
                        events["G4"] = round(t_rel, 5)
                if events["G5"] is None:
                    east_dx = float(np.max(m.x[east_roof_nodes, 0] - east_x0))
                    if east_dx > peak_east_tilt_before_g5_in:
                        peak_east_tilt_before_g5_in = east_dx
                    if dz_north > H_TYP:
                        events["G5"] = round(t_rel, 5)
                if t_north_onset_1in is None and dz_north > 1.0:
                    t_north_onset_1in = round(t_rel, 5)
                if t_total is None and events["G4"] is not None and events["G5"] is not None:
                    t_total = max(events["G4"], events["G5"])

            if t_rel >= next_sample - 1e-9:
                es = m.energy_summary()
                max_energy_rel_err = max(max_energy_rel_err, float(es["rel_error"]))
                ts_hist.append(round(t_rel, 4))
                north_drop_hist.append(round(float(np.mean(self.settled_z[self.north_roof_nodes] - m.x[self.north_roof_nodes, 2])), 3))
                ep_drop_hist.append(round(float(np.mean(self.settled_z[self.east_pent_nodes] - m.x[self.east_pent_nodes, 2])), 3))
                c79_drop_hist.append(round(float(self.settled_z[col79_roof] - m.x[col79_roof, 2]), 3))
                ke_hist.append(round(float(es["ke"]), 2))
                err_hist.append(round(float(es["rel_error"]), 5))
                next_sample += sample_dt

            if frame_dt > 0.0 and t_rel >= next_frame - 1e-9:
                frames_t.append(round(t_rel, 3))
                frames_xyz.append(m.x.astype(np.float32).copy())
                next_frame += frame_dt

        # Outcome classification (§3):
        if events["G4"] is not None and events["G5"] is not None:
            outcome = "TOTAL"
        elif diverged:
            outcome = "INCOMPLETE"
        elif events["G2"] is not None or events["G3"] is not None:
            outcome = "PARTIAL"
        else:
            outcome = "LOCAL"

        # Informational kinematics (§7) for TOTAL runs:
        obs_metrics = {}
        if len(ts_hist) >= 4:
            t_arr = np.array(ts_hist)
            nd_arr = np.array(north_drop_hist)
            if t_north_onset_1in is not None and events["G2"] is not None:
                obs_metrics["g2_to_north_onset_s"] = round(t_north_onset_1in - events["G2"], 3)
            if t_north_onset_1in is not None and t_arr[-1] >= t_north_onset_1in + 5.4:
                drop_54 = float(np.interp(t_north_onset_1in + 5.4, t_arr, nd_arr))
                obs_metrics["north_drop_at_5p4s_ft"] = round(drop_54 / 12.0, 1)
            # Peak mean downward acceleration over any 2.25 s window:
            vel = np.gradient(nd_arr, t_arr)
            win = 2.25
            best_g = 0.0
            for i_s, t_s in enumerate(t_arr):
                if t_s + win <= t_arr[-1]:
                    v_end = float(np.interp(t_s + win, t_arr, vel))
                    a_mean_g = ((v_end - vel[i_s]) / win) / G_ACC
                    if a_mean_g > best_g:
                        best_g = a_mean_g
            obs_metrics["peak_2p25s_mean_accel_g"] = round(best_g, 3)

        return dict(
            trigger=trigger,
            outcome=outcome,
            t_end_rel_s=round(float(m.t - t_trig), 4),
            t_r_s=round(t_r, 5) if is_removal else 0.0,
            events=events,
            g3_first_col=g3_first_col,
            t_north_onset_1in=t_north_onset_1in,
            peak_east_tilt_before_g5_in=round(peak_east_tilt_before_g5_in, 3),
            max_energy_rel_err=round(max_energy_rel_err, 5),
            broken_interior_joints=int((self.interior_joints.state == 2).sum()),
            broken_spandrel_joints=int((self.spandrel_joints.state == 2).sum()),
            broken_splices=int((self.splice_joints.state == 2).sum()),
            broken_slab_ties=int((self.slab_ties.state == 2).sum()),
            observational=obs_metrics,
            d0_trigger_info=d0_info,
            history=dict(t=ts_hist, north_drop_in=north_drop_hist, east_pent_drop_in=ep_drop_hist,
                         col79_drop_in=c79_drop_hist, ke=ke_hist, energy_rel_err=err_hist),
            frames_t=frames_t,
            frames_xyz=frames_xyz,
        )


# ==============================================================================
# Floor framing graph builder (exact E12/13 connectivity)
# ==============================================================================

PERIMETER_RING_UPPER = (
    ["1"] + [str(k) for k in range(2, 15)] + ["14A"]
    + [str(k) for k in range(15, 29)]
    + [str(k) for k in range(29, 43)]
    + [str(k) for k in range(43, 58)]
)

INTERIOR_COLS_24 = [str(k) for k in range(58, 82)]


def _perimeter_ring_for_level(fl: int) -> list[str]:
    if fl >= 7:
        return list(PERIMETER_RING_UPPER)
    ring = []
    for c in PERIMETER_RING_UPPER:
        if c.isdigit() and 47 <= int(c) <= 53:
            ring.append(f"{c}A")
        else:
            ring.append(c)
    return ring


def _interior_girder_specs(fl: int) -> list[tuple[str, str, str, float, str, str]]:
    """Return list of (colA, colB, shape_name, mult, connA_key, connB_key) on floor `fl` (2..48)."""
    if fl == 48:
        # Main Roof framing (Cantor S-14, reinforced under East Penthouse per NCSTAR 1-9 §2.4.2)
        heavy_core = "W24X76"
        ns_core = "W21X50"
    elif fl in (5, 7, 21, 22, 23, 46):
        heavy_core = "W30X116"
        ns_core = "W24X62"
    else:
        heavy_core = "W24X76"
        ns_core = "W21X50"

    girders = []

    # 1. Core E-W girders (Cols 58..78)
    core_lines = [
        ("58", "59", "60"), ("61", "62", "63"), ("64", "65", "66"),
        ("67", "68", "69"), ("70", "71", "72"), ("73", "74", "75"), ("76", "77", "78"),
    ]
    for i in range(len(core_lines) - 1):
        for r in range(3):
            cA, cB = core_lines[i][r], core_lines[i + 1][r]
            # Below Floor 7, some core cols are replaced by transfer sub-columns or absent:
            if fl < 7:
                rep = {"58": "58C", "59": "58B", "61": ("61" if fl >= 5 else "61A"), "76": "E4", "77": "74", "78": "78A"}
                cA = rep.get(cA, cA)
                cB = rep.get(cB, cB)
                if cA == cB:
                    continue
            sh = "W36X135" if (r == 2 and i >= 4) else heavy_core
            ck = "H5_W27" if sh in ("W30X116", "W36X135") else "H4_CORE"
            girders.append((cA, cB, sh, 1.0, ck, ck))

    # 2. Core N-S girders
    for trio in core_lines:
        for k in range(2):
            cA, cB = trio[k], trio[k + 1]
            if fl < 7:
                if cA in ("58", "59", "76", "77", "78") or cB in ("58", "59", "76", "77", "78"):
                    continue
                if cA == "61" and fl < 5:
                    cA = "61A"
            girders.append((cA, cB, ns_core, 1.0, "SWC_CORE", "SWC_CORE"))

    # 3. East Interior Primary Girders around Columns 79, 80, 81 (E12/13)
    # Note: on Floor 6 double-height mechanical space, east floor framing has openings around 79-80 (1-9 §2.4.2)
    if fl != 6:
        # North-South line: 44 -> 79 -> 80 -> 81 -> 26
        girders.append(("44", "79", "W33X130", 1.0, "STP_EXT", "STC_79_81"))    # A2001!
        girders.append(("79", "80", "W27X94",  1.0, "H5_W27",  "H5_W27"))       # A2002
        girders.append(("80", "81", "W24X62",  1.0, "H4_CORE", "H4_CORE"))      # B2002
        girders.append(("81", "26", "W27X84",  1.0, "STC_79_81", "STP_EXT"))    # B2011

        # Core-to-East Girders: 76 -> 79, 77 -> 80, 78 -> 81
        c76 = "76" if fl >= 7 else ("E3" if fl >= 3 else None)
        c77 = "77" if fl >= 7 else None
        c78 = "78" if fl >= 7 else "78A"
        if c76:
            girders.append((c76, "79", "W36X135", 1.0, "K8_W36", "K8_W36"))     # A2015
        if c77:
            girders.append((c77, "80", "W27X94",  1.0, "H5_W27", "H5_W27"))     # A2029
        if c78:
            girders.append((c78, "81", "W27X84",  1.0, "H5_W27", "H5_W27"))     # A2034

        # East bay W24x55 floor-beam bands to East Wall (Cols 29..41, E12/13):
        # Note: beams at Cols 41 & 39 frame into Girder A2001 (44-79 midspan) and beams at Col 29 frame into
        # Girder B2011 (81-26 midspan), handled in the secondary girder-supported beam pass below;
        # here are the direct column-to-column bands:
        east_bands = [
            ("79", "37", "W24X55", 2.5),
            ("80", "35", "W24X55", 1.5),
            ("80", "33", "W24X55", 2.0),
            ("81", "31", "W24X55", 2.0),
        ]
        for c_in, c_out, sh, mu in east_bands:
            girders.append((c_in, c_out, sh, mu, "F6_EAST", "STP_EXT"))
        # NE and SE corner floor beams into Col 43 and Col 27
        girders.append(("44", "41", "W21X44", 1.5, "F6_EAST", "STP_EXT"))
        girders.append(("26", "29", "W21X44", 1.5, "F6_EAST", "STP_EXT"))

    # 4. North tenant floor beam bands (Core North Row to North Wall; omitted on Fl 47 cooling tower double-height!)
    if fl != 47:
        def _n_wall(c_str: str) -> str:
            return f"{c_str}A" if (fl < 7 and c_str.isdigit() and 47 <= int(c_str) <= 53) else c_str

        north_pairs = [
            ("58", "56", 2.0), ("58", "55", 2.0),
            ("61", "54", 2.0), ("64", "53", 2.0), ("64", "52", 2.0),
            ("67", "51", 2.0), ("67", "50", 2.0),
            ("70", "49", 2.0), ("70", "48", 2.0),
            ("73", "47", 2.0), ("76", "46", 2.5),
        ]
        for c_in, c_out, mu in north_pairs:
            if fl < 7:
                if c_in == "58": c_in = "58A" if fl >= 3 else None
                elif c_in == "61" and fl < 5: c_in = "61A"
                elif c_in == "76": c_in = "E3" if fl >= 3 else None
                elif c_in in ("64", "67", "70", "73") and fl < 3: c_in = None
            if c_in is not None:
                girders.append((c_in, _n_wall(c_out), "W24X55", mu, "F6_EAST", "STP_EXT"))

    # 5. South tenant floor beam bands (Core South Row to South Wall, W16x26 / W16x31, E12/13)
    sh_s = "W16X31" if fl in (21, 22, 23) else "W16X26"
    south_pairs = [
        ("60", "16", 2.0), ("60", "17", 2.0), ("63", "18", 2.5),
        ("66", "19", 2.0), ("66", "20", 2.0), ("69", "21", 2.5),
        ("72", "22", 2.0), ("72", "23", 2.0), ("75", "24", 2.5),
        ("78" if fl >= 7 else "78A", "25", 2.5),
    ]
    for c_in, c_out, mu in south_pairs:
        girders.append((c_in, c_out, sh_s, mu, "F4_SOUTH", "STP_EXT"))

    # 6. West tenant floor beam bands (Core West Line 58, 59, 60 to West Wall 2..14A, E12/13)
    west_pairs = [
        ("58" if fl >= 7 else "58C", "3", "W16X26", 2.0),
        ("58" if fl >= 7 else "58C", "5", "W30X99", 1.0),
        ("59" if fl >= 7 else "58B", "7", "W16X26", 2.5),
        ("59" if fl >= 7 else "58B", "9", "W16X26", 2.5),
        ("60", "11", "W14X22", 2.5),
        ("60", "13", "W14X22", 2.5),
        ("60", "14A", "W14X22", 2.0),
    ]
    for c_in, c_out, sh_w, mu in west_pairs:
        girders.append((c_in, c_out, sh_w, mu, "F4_SOUTH", "STP_EXT"))

    return girders


# ==============================================================================
# Main 47-storey 3D assembly
# ==============================================================================

_VORONOI_GLOBAL_CACHE: dict[tuple, np.ndarray] = {}
_VALID_SLAB_PTS_CACHE: np.ndarray | None = None


def _get_valid_slab_pts() -> np.ndarray:
    global _VALID_SLAB_PTS_CACHE
    if _VALID_SLAB_PTS_CACHE is not None:
        return _VALID_SLAB_PTS_CACHE
    poly_outer = np.array([
        [178.0 - 24.0, 1685.0 + 24.0],
        [772.0 - 24.0, -24.0],
        [3701.625 + 24.0, -24.0],
        [4058.25 + 24.0, 1685.0 + 24.0],
    ])
    xs_grid = np.arange(160.0, 4080.0, 24.0)
    ys_grid = np.arange(-18.0, 1705.0, 24.0)
    GX, GY = np.meshgrid(xs_grid, ys_grid, indexing="ij")
    pts_2d = np.column_stack([GX.ravel(), GY.ravel()])
    in_bldg = _point_in_poly(pts_2d, poly_outer)
    in_core_box = (pts_2d[:, 0] >= 980.0) & (pts_2d[:, 0] <= 2660.0) & (pts_2d[:, 1] >= 520.0) & (pts_2d[:, 1] <= 980.0)
    ix_cell = np.round(pts_2d[:, 0] / 24.0).astype(int)
    iy_cell = np.round(pts_2d[:, 1] / 24.0).astype(int)
    shaft_hole = in_core_box & (((ix_cell + iy_cell) % 2) == 0)
    _VALID_SLAB_PTS_CACHE = pts_2d[in_bldg & (~shaft_hole)]
    return _VALID_SLAB_PTS_CACHE


def build_wtc7_model(cfg: BuildingConfig | None = None) -> WTC7Building:
    cfg = BuildingConfig() if cfg is None else cfg
    floors = build_floor_elevations()
    cols = build_column_plan()

    m = xfe.Model(contact_alpha=0.10, contact_zeta=0.35)

    # Materials (NIST temperature-dependent steel curves, scaled by fy_scale for T5)
    m.add_material(xfe.steel_material("A572", "NIST", "A572", fy_scale=cfg.fy_scale))
    m.add_material(xfe.steel_material("A36",  "NIST", "A36",  fy_scale=cfg.fy_scale))

    sec_cache: dict[str, str] = {}

    def ensure_w_sec(shape_name: str, kind: str = "bare", pw: float = 0.0, pt: float = 0.0, mult: float = 1.0) -> str:
        key = f"{shape_name}_{kind}_{pw:g}_{pt:g}_m{mult:g}"
        if key not in sec_cache:
            if kind == "bare" and mult != 1.0:
                m.add_beam_section(grouped_w_section(key, shape_name, mult))
            else:
                m.add_beam_section(xfe.w_beam_section(key, shape_name, kind=kind, pw=pw, pt=pt))
            sec_cache[key] = key
        return key

    def ensure_pg_sec(name: str, bf: float, tf: float, tw: float, d_tot: float) -> str:
        if name not in sec_cache:
            m.add_beam_section(plate_girder_section(name, bf, tf, tw, d_tot))
            sec_cache[name] = name
        return name

    # ---- 1. Columns & Two-Storey Column Splices (Floors 2..48) ----
    col_nodes_bot: dict[tuple[str, int], int] = {}
    col_nodes_top: dict[tuple[str, int], int] = {}
    col_elem_ids: dict[tuple[str, int], np.ndarray] = {}

    splice_names, sp_na, sp_nb, sp_kt, sp_kc, sp_kv, sp_ncap, sp_vcap, sp_mp, sp_kr, sp_tg = (
        [], [], [], [], [], [], [], [], [], [], []
    )
    # Keep welded continuity (no breakable splice) right at Floor 5 & 7 transfer-truss chord nodes
    truss_chord_cols = {"61", "61A", "62", "73", "74", "76", "77", "78", "78A", "80", "E3", "E4", "58", "59"}
    east_focus_cols = {"73", "74", "75", "76", "77", "78", "79", "80", "81", "44", "26"}
    debris_zone1_cols = {"14A", "15", "16", "17", "18", "19", "20"}

    z5, z14 = floors[5]["z_in"], floors[14]["z_in"]

    def col_xy_at_z(cid: str, z_val: float) -> tuple[float, float]:
        c = cols[cid]
        x, y = c["x"], c["y"]
        if cid == "79" and cfg.col79_bow_over_L != 0.0 and z5 <= z_val <= z14:
            L_unb = z14 - z5
            x += (cfg.col79_bow_over_L * L_unb) * math.sin(math.pi * (z_val - z5) / L_unb)
        return x, y

    for cid, cinfo in cols.items():
        start_lvl = max(2, cinfo["bot_level"])
        end_lvl = cinfo["top_level"]
        if start_lvl >= end_lvl:
            continue

        # Create start node
        x0_c, y0_c = col_xy_at_z(cid, floors[start_lvl]["z_in"])
        n_start = int(m.add_nodes([[x0_c, y0_c, floors[start_lvl]["z_in"]]])[0])
        col_nodes_bot[(cid, start_lvl)] = n_start
        col_nodes_top[(cid, start_lvl)] = n_start

        # Base boundary per NCSTAR 1-9A §3.4.2:
        # Columns reaching Floor 2 are fixed at Floor 2; substation columns starting at Floor 3 are fixed at Floor 3.
        if start_lvl == 2 or (start_lvl == 3 and cinfo["on_substation"]):
            m.fix(n_start, (0, 1, 2, 3, 4, 5))

        for fl in range(start_lvl, end_lvl):
            fl_next = fl + 1
            z_a, z_b = floors[fl]["z_in"], floors[fl_next]["z_in"]
            w_sh, p_kind, pw, pt, grade = column_section_spec(cid, fl)
            s_key = ensure_w_sec(w_sh, p_kind, pw, pt)
            sec_obj = m.beam_sections[m.sec_index[s_key]]

            # Temperature group: 1 for interior cols 76-81 in Floors 7..14 (for T9), else 0
            tg_col = 1 if (cid in ("76", "77", "78", "79", "80", "81") and 7 <= fl <= 14) else 0

            # Subdivision per storey
            nsub = cfg.east_subdiv if (cid in east_focus_cols and fl >= 5) else 1
            n_prev = col_nodes_top[(cid, fl)]
            chain = [n_prev]
            for k in range(1, nsub):
                zk = z_a + (k / nsub) * (z_b - z_a)
                xk, yk = col_xy_at_z(cid, zk)
                chain.append(int(m.add_nodes([[xk, yk, zk]])[0]))
            xb, yb = col_xy_at_z(cid, z_b)
            n_top_seg = int(m.add_nodes([[xb, yb, z_b]])[0])
            chain.append(n_top_seg)

            # Column strong-axis orientation (E12/13 & 1370/1091):
            # Perimeter W14 webs lie in the plane of the facade wall so strong-axis Ix resists moment-frame sway along the wall:
            # North/South walls (running E-W) -> up=[1,0,0]; East/West walls (running N-S) -> up=[0,1,0];
            # Interior columns webs along E-W -> up=[1,0,0], rotated 12.36 deg CW on Col 79 per A93.
            if cid == "79":
                ang = math.radians(-12.36)
                up_vec = [math.cos(ang), math.sin(ang), 0.0]
            elif cinfo["face"] in ("east", "west"):
                up_vec = [0.0, 1.0, 0.0]
            else:
                up_vec = [1.0, 0.0, 0.0]

            eids = m.add_beams(np.column_stack([chain[:-1], chain[1:]]), s_key, grade, tg_col, f"col_{cid}", up=up_vec)
            col_elem_ids[(cid, fl)] = eids
            col_nodes_bot[(cid, fl_next)] = n_top_seg

            # Odd-floor two-storey column splice (5, 7, 9, ..., 45)
            is_splice = (
                fl_next < end_lvl
                and (fl_next % 2 == 1)
                and fl_next >= 5
                and not (fl_next in (5, 7) and cid in truss_chord_cols)
            )
            if is_splice:
                n_upper_base = int(m.add_nodes([[xb, yb, z_b]])[0])
                col_nodes_top[(cid, fl_next)] = n_upper_base
                fy_pl = 50.0 if grade == "A572" else 36.0
                ag = sec_obj.A
                imin = min(sec_obj.Ix, sec_obj.Iy)
                imax = max(sec_obj.Ix, sec_obj.Iy)
                z_est = 2.0 * imin / max(sec_obj.width, 14.0)
                k_col = 29000.0 * ag / H_TYP
                splice_names.append(f"sp_{cid}_F{fl_next}")
                sp_na.append(n_upper_base)
                sp_nb.append(n_top_seg)
                sp_kt.append(4.0 * k_col)
                sp_kc.append(8.0 * k_col)
                sp_kv.append(3.0 * k_col)
                sp_ncap.append(cfg.splice_scale * max(0.30 * ag * fy_pl, 600.0))
                sp_vcap.append(cfg.splice_scale * max(0.25 * ag * fy_pl, 500.0))
                sp_mp.append(cfg.splice_scale * 0.35 * fy_pl * z_est)
                sp_kr.append(6.0 * 29000.0 * imax / H_TYP)
                sp_tg.append(tg_col)
            else:
                col_nodes_top[(cid, fl_next)] = n_top_seg

        # Rigid substation lateral restraint at Floor 3 for columns passing through the Con Ed substation
        if cinfo["x"] <= 3460.0 and cinfo["y"] >= 1050.0 and (cid, 3) in col_nodes_bot:
            m.fix(col_nodes_bot[(cid, 3)], (0, 1, 2, 3, 4, 5))

    # ---- 2. Transfer Trusses 1, 2, 3 & Plate Girders MG-21, 22, 23, 27, 53 (Floors 5-7, Cantor S-23) ----
    # MG-53 at Floor 5 between Col E3 and Col E4, supporting east end of Truss 1:
    s_mg53 = ensure_pg_sec("MG53", 48.0, 6.0, 5.0, 48.0)
    n_e3_5, n_e4_5 = col_nodes_bot[("E3", 5)], col_nodes_bot[("E4", 5)]
    n_t1_e5 = int(m.add_nodes([[2915.0, 1066.0, floors[5]["z_in"]]])[0])
    n_t1_e7 = int(m.add_nodes([[2915.0, 1066.0, floors[7]["z_in"]]])[0])
    m.add_beams([[n_e3_5, n_t1_e5], [n_t1_e5, n_e4_5]], s_mg53, "A572", 0, "MG53")
    s_w14_665 = ensure_w_sec("W14X665")
    s_w36_300 = ensure_w_sec("W36X300")
    m.add_beams([[n_t1_e5, n_t1_e7]], s_w14_665, "A572", 0, "truss1_post", up=[1, 0, 0])

    # Truss 1 (Col 73 - Col 76 line - MG53, Floors 5-7):
    n_76_5 = int(m.add_nodes([[cols["76"]["x"], cols["76"]["y"], floors[5]["z_in"]]])[0])
    n_76_7 = col_nodes_bot[("76", 7)]
    n_73_5, n_73_7 = col_nodes_bot[("73", 5)], col_nodes_bot[("73", 7)]
    m.add_beams([[n_73_5, n_76_5], [n_76_5, n_t1_e5], [n_73_7, n_76_7], [n_76_7, n_t1_e7]], s_w36_300, "A572", 0, "truss1_chord")
    m.add_beams([[n_76_5, n_76_7], [n_73_5, n_76_7], [n_t1_e5, n_76_7]], s_w14_665, "A572", 0, "truss1_diag", up=[1, 0, 0])

    # MG-23 at Floor 7 (Col 77 - Col 78 - Col 78A, supporting Col 78!):
    s_mg23 = ensure_pg_sec("MG23", 30.0, 5.0, 4.0, 96.0)
    n_77_7, n_78_7, n_78a_7 = col_nodes_bot[("77", 7)], col_nodes_bot[("78", 7)], col_nodes_bot[("78A", 7)]
    m.add_beams([[n_77_7, n_78_7], [n_78_7, n_78a_7]], s_mg23, "A572", 0, "MG23")

    # Truss 2 (Col 74 - Col 77 - Col 80, Floors 5-7; diagonals W14x730 + 2 PL 8x3 web plates!):
    s_t2_diag = ensure_w_sec("W14X730", "web", 8.0, 3.0)
    s_w14_82 = ensure_w_sec("W14X82")
    n_74_5, n_74_7 = col_nodes_bot[("74", 5)], col_nodes_bot[("74", 7)]
    n_80_5, n_80_7 = col_nodes_bot[("80", 5)], col_nodes_bot[("80", 7)]
    n_77_5 = int(m.add_nodes([[cols["77"]["x"], cols["77"]["y"], floors[5]["z_in"]]])[0])
    n_t2_dW = int(m.add_nodes([[0.5 * (cols["74"]["x"] + cols["77"]["x"]), cols["77"]["y"], floors[6]["z_in"]]])[0])
    n_t2_dE = int(m.add_nodes([[0.5 * (cols["80"]["x"] + cols["77"]["x"]),
                                0.5 * (cols["80"]["y"] + cols["77"]["y"]), floors[6]["z_in"]]])[0])
    m.add_beams([[n_74_5, n_77_5], [n_77_5, n_80_5], [n_74_7, n_77_7], [n_77_7, n_80_7]], s_w36_300, "A572", 0, "truss2_chord")
    m.add_beams([[n_77_5, n_77_7]], s_w14_82, "A572", 0, "truss2_hanger", up=[1, 0, 0])
    m.add_beams([[n_74_5, n_t2_dW], [n_t2_dW, n_77_7], [n_80_5, n_t2_dE], [n_t2_dE, n_77_7]],
                s_t2_diag, "A572", 0, "truss2_diag", up=[1, 0, 0])

    # Truss 3 (Col 62 - Col 61A - Col 61, Floors 5-7, Cantor S-23):
    s_w14_342 = ensure_w_sec("W14X342")
    s_w14_605 = ensure_w_sec("W14X605")
    s_t3_cant = ensure_w_sec("W14X730", "web", 12.5, 3.0)
    for fl_t in (5, 6, 7):
        m.add_beams([[col_nodes_bot[("62", fl_t)], col_nodes_bot[("61A", fl_t)]],
                     [col_nodes_bot[("61A", fl_t)], col_nodes_bot[("61", fl_t)]]], s_w14_342, "A572", 0, "truss3_chord")
    m.add_beams([[col_nodes_bot[("62", 5)], col_nodes_bot[("61A", 7)]],
                 [col_nodes_bot[("61A", 5)], col_nodes_bot[("62", 7)]]], s_w14_605, "A572", 0, "truss3_diag", up=[1, 0, 0])
    m.add_beams([[col_nodes_bot[("61A", 5)], col_nodes_bot[("61", 7)]],
                 [col_nodes_bot[("61", 5)], col_nodes_bot[("61A", 7)]]], s_t3_cant, "A572", 0, "truss3_cant", up=[1, 0, 0])

    # MG-21 & MG-22 at Floor 7 (supporting Cols 58 and 59):
    s_mg21 = ensure_pg_sec("MG21", 30.0, 4.0, 3.5, 108.0)
    s_mg22 = ensure_pg_sec("MG22", 24.0, 2.0, 3.5, 60.0)
    m.add_beams([[col_nodes_bot[("58A", 7)], col_nodes_bot[("58", 7)]],
                 [col_nodes_bot[("58", 7)], col_nodes_bot[("58C", 7)]]], s_mg21, "A36", 0, "MG21")
    m.add_beams([[col_nodes_bot[("58B", 7)], col_nodes_bot[("59", 7)]],
                 [col_nodes_bot[("59", 7)], col_nodes_bot[("59A", 7)]]], s_mg22, "A36", 0, "MG22")

    # MG-27 North Cantilever Girders at Floor 7 (Cols 47..53 overhanging 6'-9" north of 47A..53A):
    s_mg27 = ensure_pg_sec("MG27", 30.0, 5.0, 2.5, 84.0)
    mg27_back = {"47": "73", "48": "70", "49": "70", "50": "67", "51": "67", "52": "64", "53": "64"}
    for c_n, c_core in mg27_back.items():
        m.add_beams([[col_nodes_bot[(c_core, 7)], col_nodes_bot[(f"{c_n}A", 7)]],
                     [col_nodes_bot[(f"{c_n}A", 7)], col_nodes_bot[(c_n, 7)]]], s_mg27, "A36", 0, "MG27")

    # ---- 3. Perimeter Spandrels (WG-1..58) & Belt Trusses (Fl 5-7, Fl 22-24) & Lower Core Bracing ----
    spand_names, spand_na, spand_nb, spand_e1, spand_e2, spand_kt, spand_kc, spand_kv, spand_kr, spand_mp = (
        [], [], [], [], [], [], [], [], [], []
    )
    spandrel_load_segments: dict[int, list[tuple[np.ndarray, np.ndarray, list[int]]]] = {fl: [] for fl in range(2, 49)}
    for fl in range(2, 49):
        ring = _perimeter_ring_for_level(fl)
        for i in range(len(ring)):
            cA, cB = ring[i], ring[(i + 1) % len(ring)]
            if (cA, fl) not in col_nodes_bot or (cB, fl) not in col_nodes_bot:
                continue
            face = cols[cA]["face"] if cols[cA]["face"] in ("north", "south", "east", "west") else "north"
            sh_wg, mp_wg = spandrel_section_spec(face, fl)
            s_wg = ensure_w_sec(sh_wg)
            sec_wg = m.beam_sections[m.sec_index[s_wg]]
            nColA, nColB = col_nodes_bot[(cA, fl)], col_nodes_bot[(cB, fl)]
            pA, pB = m._x[nColA][0], m._x[nColB][0]
            L_sp = float(np.linalg.norm(pB - pA))
            e1 = (pB - pA) / L_sp

            # Spandrel beam has its own end nodes tied to column nodes via Moment Connection JointSet (kind = 2)
            nA_g = int(m.add_nodes([pA])[0])
            nB_g = int(m.add_nodes([pB])[0])
            m.add_beams([[nA_g, nB_g]], s_wg, "A36", 0, f"wg_F{fl}")
            spandrel_load_segments[fl].append((pA[:2].copy(), pB[:2].copy(), [nA_g, nB_g]))

            k_wg = 29000.0 * sec_wg.A / L_sp
            kr_wg = 6.0 * 29000.0 * sec_wg.Ix / L_sp
            for tag, na_i, nb_i, dir_i in ((f"mc_{cA}_{cB}_F{fl}_A", nA_g, nColA, e1),
                                           (f"mc_{cA}_{cB}_F{fl}_B", nB_g, nColB, -e1)):
                e2_i = np.cross([0.0, 0.0, 1.0], dir_i)
                e2_i /= np.linalg.norm(e2_i)
                spand_names.append(tag)
                spand_na.append(na_i)
                spand_nb.append(nb_i)
                spand_e1.append(dir_i)
                spand_e2.append(e2_i)
                spand_kt.append(4.0 * k_wg)
                spand_kc.append(6.0 * k_wg)
                spand_kv.append(4.0 * k_wg)
                spand_kr.append(kr_wg)
                spand_mp.append(mp_wg)

    # Belt trusses at Floors 5-7 and Floors 22-24 (Cantor S-22 & Frankel E120) + Core wind bracing (Floors 2-7):
    s_belt = ensure_w_sec("W14X176")  # equivalent area/stiffness to 2 WT8x50 / W14 diagonals on E120 & S-22
    for fl_b in (5, 6, 22, 23):
        ring_lo = _perimeter_ring_for_level(fl_b)
        ring_hi = _perimeter_ring_for_level(fl_b + 1)
        if len(ring_lo) == len(ring_hi):
            for i in range(0, len(ring_lo), 2):
                c0, c1 = ring_lo[i], ring_lo[(i + 1) % len(ring_lo)]
                d0, d1 = ring_hi[i], ring_hi[(i + 1) % len(ring_hi)]
                if all((c, lv) in col_nodes_bot for c, lv in ((c0, fl_b), (c1, fl_b), (d0, fl_b + 1), (d1, fl_b + 1))):
                    m.add_beams([[col_nodes_bot[(c0, fl_b)], col_nodes_bot[(d1, fl_b + 1)]],
                                 [col_nodes_bot[(c1, fl_b)], col_nodes_bot[(d0, fl_b + 1)]]], s_belt, "A36", 0, "belt_truss")

    # Lower core wind bracing (Floors 3-7 along core lines, NCSTAR 1-9A Fig. 3-43):
    for fl_c in range(3, 7):
        for cA, cB in (("64", "67"), ("67", "70"), ("70", "73"), ("63", "66"), ("69", "72"), ("72", "75")):
            if (cA, fl_c) in col_nodes_bot and (cB, fl_c + 1) in col_nodes_bot and (cB, fl_c) in col_nodes_bot and (cA, fl_c + 1) in col_nodes_bot:
                m.add_beams([[col_nodes_bot[(cA, fl_c)], col_nodes_bot[(cB, fl_c + 1)]],
                             [col_nodes_bot[(cB, fl_c)], col_nodes_bot[(cA, fl_c + 1)]]], s_belt, "A572", 0, "core_brace")

    # ---- 4. Interior Floor Framing, Coupled Breakable Connections, Slab Ties & Impact Contact ----
    j_names, j_na, j_nb, j_kind = [], [], [], []
    j_e1, j_e2, j_kt, j_kc, j_kv, j_gap, j_wax, j_wlat, j_kr, j_ncap, j_vcap, j_tg = ([] for _ in range(12))
    joint_meta: list[dict] = []

    sl_names, sl_na, sl_nb, sl_e1, sl_e2, sl_ncap, sl_vcap, sl_kt, sl_tg = ([] for _ in range(9))
    slab_meta: list[dict] = []

    # Track floor girder midspan & end nodes per (floor, key) so Floor k impacts Floor k-1 directly below!
    floor_girder_nodes: dict[int, dict[tuple[str, str], list[int]]] = {}
    # Also store all girder segments per floor `(fl) -> list of (pA_xy, pB_xy, node_ids_for_load)` for exact Voronoi slab load integration
    floor_load_segments: dict[int, list[tuple[np.ndarray, np.ndarray, list[int]]]] = {}

    east_heated_cols = {"73", "74", "75", "76", "77", "78", "79", "80", "81", "44", "43", "41", "39", "37", "35", "33", "31", "29", "27", "26"}

    for fl in range(2, 49):
        floor_girder_nodes[fl] = {}
        floor_load_segments[fl] = list(spandrel_load_segments[fl])
        specs = _interior_girder_specs(fl)
        for cA, cB, sh_name, mult, ckA, ckB in specs:
            if (cA, fl) not in col_nodes_bot or (cB, fl) not in col_nodes_bot:
                continue
            # Skip already-built MG transfer girders at Floor 7
            if fl == 7 and ({cA, cB} in ({"77", "78"}, {"78", "78A"}, {"58", "58A"}, {"58", "58C"})):
                continue

            nColA, nColB = col_nodes_bot[(cA, fl)], col_nodes_bot[(cB, fl)]
            pA, pB = m._x[nColA][0], m._x[nColB][0]
            L_g = float(np.linalg.norm(pB - pA))
            if L_g < 12.0:
                continue
            e1 = (pB - pA) / L_g
            e2 = np.cross([0.0, 0.0, 1.0], e1)
            e2 /= np.linalg.norm(e2)

            s_key = ensure_w_sec(sh_name, mult=mult)
            sec_g = m.beam_sections[m.sec_index[s_key]]
            in_east = (cA in east_heated_cols or cB in east_heated_cols)
            tg_fl = 2 if (in_east and 8 <= fl <= 13) else 0

            # Number of beam elements along girder (2 baseline => 1 midspan node; 4 refined in east zone)
            nel_g = (2 * cfg.east_subdiv // 2) * 2 if in_east else 2
            nel_g = max(2, nel_g)

            nL = int(m.add_nodes([pA])[0])
            mids = [int(m.add_nodes([(1.0 - k / nel_g) * pA + (k / nel_g) * pB])[0]) for k in range(1, nel_g)]
            nR = int(m.add_nodes([pB])[0])
            chain = [nL] + mids + [nR]
            m.add_beams(np.column_stack([chain[:-1], chain[1:]]), s_key, "A572", tg_fl, f"fl_{fl}")

            gkey = tuple(sorted((cA, cB)))
            floor_girder_nodes[fl][gkey] = chain
            floor_load_segments[fl].append((pA[:2].copy(), pB[:2].copy(), chain))

            # Torsional roll restraint stiffness about e1
            kr_roll = 4.0 * 11200.0 * max(sec_g.J, 1.0) / L_g

            # End A and End B coupled 6-DOF connections (keep e3 = +Z upward at both ends!)
            for end_lbl, na_i, nb_i, col_i, other_i, ck_i, dir_i in (
                ("A", nL, nColA, cA, cB, ckA, e1),
                ("B", nR, nColB, cB, cA, ckB, -e1),
            ):
                e2_i = np.cross([0.0, 0.0, 1.0], dir_i)
                e2_i /= np.linalg.norm(e2_i)
                cs = CONNECTION_SPECS[ck_i]
                # Scale multi-beam band capacities by `mult`; reinforce lower concourse (Fl 2-4), Fl 5/7 diaphragms, & Fl 46/48 mech/penthouse levels
                diaph_fac = 2.5 if fl in (5, 7) else (2.0 if fl in (2, 3, 4, 46, 48) else 1.0)
                sc_cap = cfg.conn_scale * mult * diaph_fac
                j_names.append(f"j_{cA}_{cB}_F{fl}_{end_lbl}")
                j_na.append(na_i)
                j_nb.append(nb_i)
                j_kind.append(cs["kind"])
                j_e1.append(dir_i)
                j_e2.append(e2_i)
                j_kt.append(cs["kt"] * mult * diaph_fac)
                j_kc.append(cs["kc"] * mult)
                j_kv.append(cs["kv"] * mult * diaph_fac)
                j_gap.append(cs["gap_c"])
                j_wax.append(cs["walk_ax"])
                j_wlat.append(cs["walk_lat"])
                j_kr.append(kr_roll)
                j_ncap.append(cs["ncap"] * sc_cap)
                j_vcap.append(cs["vcap"] * sc_cap)
                j_tg.append(tg_fl)
                joint_meta.append(dict(
                    floor=fl, col=col_i, other=other_i, pair=gkey,
                    bay_col79=("79" in (cA, cB)),
                    is_A2001_79=({cA, cB} == {"44", "79"} and col_i == "79"),
                    is_A2001_44=({cA, cB} == {"44", "79"} and col_i == "44"),
                ))

            # Composite slab in-plane membrane / WWF tie across the bay (NCSTAR 1-9A §2.3.1, scaled by T4)
            # Floor 5 (14-in. rebar + WT diaphragm) ~ 600 kip; Floor 7 (8-in. #5@6 transfer slab) ~ 450 kip; tenant WWF ~ 45 kip*mult
            slab_base_cap = 600.0 if fl == 5 else (450.0 if fl == 7 else (250.0 if fl in (6, 8) else 45.0 * mult))
            sl_names.append(f"slab_{cA}_{cB}_F{fl}")
            sl_na.append(nColB)
            sl_nb.append(nColA)
            sl_e1.append(e1)
            sl_e2.append(e2)
            sl_ncap.append(cfg.slab_scale * slab_base_cap)
            sl_vcap.append(cfg.slab_scale * slab_base_cap)
            sl_kt.append(2500.0 if fl in (5, 7) else 450.0 * mult)
            sl_tg.append(tg_fl)
            slab_meta.append(dict(floor=fl, colA=cA, colB=cB, bay_col79=("79" in (cA, cB))))

        # Secondary floor-beam bands framing onto primary girders on E12/13 (A2001=44-79, A2015=76-79, A2029=77-80, B2011=26-81):
        sec_specs = []
        if fl != 6:
            c76_s = "76" if fl >= 7 else ("E3" if fl >= 3 else None)
            c77_s = "77" if fl >= 7 else None
            sec_specs.append((("44", "79"), "39", "W24X55", 2.5, True))   # E-W beams into A2001 midspan!
            sec_specs.append((("44", "79"), "43", "W21X44", 1.5, True))   # NE beams into A2001 midspan!
            if c76_s and fl != 47:
                sec_specs.append((tuple(sorted((c76_s, "79"))), "45", "W24X55", 2.5, True))   # N-S beams from 45 into 76-79!
            if c77_s:
                sec_specs.append((("77", "80"), "35", "W24X55", 1.0, False))  # Central-east tie into 77-80 midspan
            sec_specs.append((("26", "81"), "27", "W21X44", 1.5, False))  # SE beams into 81-26 midspan

        for g_pair, c_ext, sh_sec, mu_sec, in_b79 in sec_specs:
            g_chain = floor_girder_nodes[fl].get(g_pair)
            if not g_chain or (c_ext, fl) not in col_nodes_bot:
                continue
            n_gmid = g_chain[len(g_chain) // 2]
            n_cext = col_nodes_bot[(c_ext, fl)]
            pA_s, pB_s = m._x[n_gmid][0], m._x[n_cext][0]
            L_s = float(np.linalg.norm(pB_s - pA_s))
            if L_s < 12.0:
                continue
            e1_s = (pB_s - pA_s) / L_s
            s_key_s = ensure_w_sec(sh_sec, mult=mu_sec)
            sec_s = m.beam_sections[m.sec_index[s_key_s]]
            tg_s = 2 if (8 <= fl <= 13) else 0
            nL_s = int(m.add_nodes([pA_s])[0])
            nM_s = int(m.add_nodes([0.5 * (pA_s + pB_s)])[0])
            nR_s = int(m.add_nodes([pB_s])[0])
            ch_s = [nL_s, nM_s, nR_s]
            m.add_beams(np.column_stack([ch_s[:-1], ch_s[1:]]), s_key_s, "A572", tg_s, f"fl_{fl}")
            skey_id = (f"mid_{g_pair[0]}_{g_pair[1]}", c_ext)
            floor_girder_nodes[fl][skey_id] = ch_s
            floor_load_segments[fl].append((pA_s[:2].copy(), pB_s[:2].copy(), ch_s))
            kr_s = 4.0 * 11200.0 * max(sec_s.J, 1.0) / L_s
            diaph_s = 2.5 if fl in (5, 7) else (2.0 if fl in (2, 3, 4, 46, 48) else 1.0)
            for end_lbl, na_i, nb_i, ck_i, dir_i in (
                ("A", nL_s, n_gmid, "F6_EAST", e1_s),
                ("B", nR_s, n_cext, "STP_EXT", -e1_s),
            ):
                e2_i = np.cross([0.0, 0.0, 1.0], dir_i)
                e2_i /= np.linalg.norm(e2_i)
                cs = CONNECTION_SPECS[ck_i]
                sc_cap = cfg.conn_scale * mu_sec * diaph_s
                j_names.append(f"j_sec_{g_pair[0]}{g_pair[1]}_{c_ext}_F{fl}_{end_lbl}")
                j_na.append(na_i)
                j_nb.append(nb_i)
                j_kind.append(cs["kind"])
                j_e1.append(dir_i)
                j_e2.append(e2_i)
                j_kt.append(cs["kt"] * mu_sec * diaph_s)
                j_kc.append(cs["kc"] * mu_sec)
                j_kv.append(cs["kv"] * mu_sec * diaph_s)
                j_gap.append(cs["gap_c"])
                j_wax.append(cs["walk_ax"])
                j_wlat.append(cs["walk_lat"])
                j_kr.append(kr_s)
                j_ncap.append(cs["ncap"] * sc_cap)
                j_vcap.append(cs["vcap"] * sc_cap)
                j_tg.append(tg_s)
                joint_meta.append(dict(
                    floor=fl, col=(c_ext if end_lbl == "B" else "79"), other=c_ext, pair=skey_id,
                    bay_col79=in_b79, is_A2001_79=False, is_A2001_44=False,
                ))

    # ---- 5. East & West Penthouses above Main Roof (level 49, NCSTAR 1-9 Fig. 2-14 & 1-9A Fig. 3-46/3-47) ----
    s_pent_post = ensure_w_sec("W14X90")
    s_pent_gir = ensure_w_sec("W21X44")
    z_pent = floors[49]["z_in"]

    east_pent_cols = ["76", "77", "79", "80", "81", "44", "43", "41", "39", "37", "35"]
    west_pent_cols = ["58", "59", "61", "62", "64", "65", "67", "68", "70", "71", "73", "74"]
    pent_top_nodes: dict[str, int] = {}

    for pc in east_pent_cols + west_pent_cols:
        n_r = col_nodes_bot[(pc, 48)]
        pr = m._x[n_r][0]
        n_pt = int(m.add_nodes([[pr[0], pr[1], z_pent]])[0])
        pent_top_nodes[pc] = n_pt
        m.add_beams([[n_r, n_pt]], s_pent_post, "A572", 0, "pent_post", up=[1, 0, 0])

    # East Penthouse Post P17 sitting at midspan of the Roof A2001 girder (44-79) per NCSTAR 1-9 §8.3.2!
    a2001_roof_chain = floor_girder_nodes[48].get(("44", "79"))
    if a2001_roof_chain:
        n_p17_base = a2001_roof_chain[len(a2001_roof_chain) // 2]
        p17_xy = m._x[n_p17_base][0]
        n_p17_top = int(m.add_nodes([[p17_xy[0], p17_xy[1], z_pent]])[0])
        pent_top_nodes["P17"] = n_p17_top
        m.add_beams([[n_p17_base, n_p17_top]], s_pent_post, "A572", 0, "pent_post", up=[1, 0, 0])

    # East penthouse roof grid (decoupled from central screenwall per NCSTAR 1-9A Fig. 3-47!)
    ep_edges = [
        ("44", "P17"), ("P17", "79"), ("79", "80"), ("80", "81"), ("76", "77"),
        ("76", "79"), ("77", "80"), ("44", "43"), ("43", "41"), ("41", "39"), ("39", "37"), ("37", "35"),
        ("79", "39"), ("80", "35"), ("P17", "41"),
    ]
    for a, b in ep_edges:
        if a in pent_top_nodes and b in pent_top_nodes:
            m.add_beams([[pent_top_nodes[a], pent_top_nodes[b]]], s_pent_gir, "A572", 0, "east_pent_roof")

    # West penthouse & central screenwall roof grid
    wp_edges = [
        ("58", "61"), ("61", "64"), ("64", "67"), ("67", "70"), ("70", "73"),
        ("59", "62"), ("62", "65"), ("65", "68"), ("68", "71"), ("71", "74"),
        ("58", "59"), ("61", "62"), ("64", "65"), ("67", "68"), ("70", "71"), ("73", "74"),
    ]
    for a, b in wp_edges:
        if a in pent_top_nodes and b in pent_top_nodes:
            m.add_beams([[pent_top_nodes[a], pent_top_nodes[b]]], s_pent_gir, "A572", 0, "west_pent_roof")

    east_pent_nodes = np.array([pent_top_nodes[k] for k in east_pent_cols + (["P17"] if "P17" in pent_top_nodes else [])], np.int32)
    west_pent_nodes = np.array([pent_top_nodes[k] for k in west_pent_cols], np.int32)

    # ---- 6. Exact Geometric Slab Tributary Load & Mass Distribution (DL + SDL + ll_frac * LL) ----
    valid_pts = _get_valid_slab_pts()
    cell_area_ft2 = (24.0 * 24.0) / 144.0  # 4.0 ft^2 per quadrature point

    # Precompute point-to-nearest-girder-segment mapping (cached globally across identical typical floors & runs!)
    nodal_extra_weight = np.zeros(m._nn_count)
    voronoi_cache = _VORONOI_GLOBAL_CACHE

    for fl in range(2, 49):
        segs = floor_load_segments[fl]
        if not segs:
            continue
        fl_mode = "fl6" if fl == 6 else ("fl47" if fl == 47 else "std")
        cache_key = (fl_mode, tuple((round(float(s[0][0]), 1), round(float(s[0][1]), 1),
                                     round(float(s[1][0]), 1), round(float(s[1][1]), 1)) for s in segs))
        counts = voronoi_cache.get(cache_key)
        if counts is None:
            pts_fl = valid_pts
            if fl == 6:
                pts_fl = pts_fl[pts_fl[:, 0] <= 2850.0]
            elif fl == 47:
                cool_open = (pts_fl[:, 0] >= 1155.0) & (pts_fl[:, 0] <= 2906.0) & (pts_fl[:, 1] >= 1100.0)
                pts_fl = pts_fl[~cool_open]
            seg_a = np.array([s[0] for s in segs])
            seg_b = np.array([s[1] for s in segs])
            v = seg_b - seg_a
            v2 = np.maximum((v * v).sum(axis=1), 1e-12)
            t_seg = ((pts_fl[:, 0:1] - seg_a[None, :, 0]) * v[None, :, 0]
                     + (pts_fl[:, 1:2] - seg_a[None, :, 1]) * v[None, :, 1]) / v2[None, :]
            t_seg = np.clip(t_seg, 0.0, 1.0)
            dx = pts_fl[:, 0:1] - (seg_a[None, :, 0] + t_seg * v[None, :, 0])
            dy = pts_fl[:, 1:2] - (seg_a[None, :, 1] + t_seg * v[None, :, 1])
            nearest_g = np.argmin(dx * dx + dy * dy, axis=1)
            counts = np.bincount(nearest_g, minlength=len(segs))
            voronoi_cache[cache_key] = counts

        fl_info = floors[fl]
        net_psf = max(0.0, fl_info["dl_psf"] + cfg.ll_frac * fl_info["ll_psf"])
        for g_idx, cnt in enumerate(counts):
            if cnt == 0:
                continue
            w_kip = float(cnt) * cell_area_ft2 * net_psf / 1000.0
            n_chain = segs[g_idx][2]
            # Trapezoidal weights along chain (interior nodes get 2x end nodes):
            if len(n_chain) == 3:
                wts = (0.25, 0.50, 0.25)
            else:
                wts = np.ones(len(n_chain)) / len(n_chain)
            for nd_i, wt_i in zip(n_chain, wts):
                nodal_extra_weight[nd_i] += w_kip * wt_i

    # Mechanical & penthouse equipment weights (NCSTAR 1-9A §3.4.3 & Cantor S-16):
    # Floor 7: 22 kip near Cols 76-78
    for c_eq in ("76", "77", "78"):
        nodal_extra_weight[col_nodes_bot[(c_eq, 7)]] += 22.0 / 3.0
    # Floor 46: 425 kip cooling towers + 667 kip mechanical equipment across North bays (Cols 46..54 & 61..76)
    fl46_targs = [col_nodes_bot[(str(c), 46)] for c in list(range(46, 55)) + [61, 64, 67, 70, 73, 76]]
    for nd_i in fl46_targs:
        nodal_extra_weight[nd_i] += (425.0 + 667.0) / len(fl46_targs)
    # East penthouse chiller plant & concrete pad (~720 kip across east penthouse nodes) + West penthouse (~480 kip)
    for nd_i in east_pent_nodes:
        nodal_extra_weight[int(nd_i)] += 720.0 / len(east_pent_nodes)
    for nd_i in west_pent_nodes:
        nodal_extra_weight[int(nd_i)] += 480.0 / len(west_pent_nodes)

    nz_w = np.nonzero(nodal_extra_weight > 0)[0]
    m.add_mass(nz_w.astype(np.int32), nodal_extra_weight[nz_w] / G_ACC)

    # ---- 7. Finalize Model, Attach JointSets & Storey-to-Storey ImpactContact ----
    m.finalize(dt_safety=0.85, dt_min=cfg.dt_min)

    # Apply WTC 1 Southwest Debris Damage (T8 / RU_debris, NCSTAR 1-9A §3.4.3) if requested:
    if cfg.wtc1_debris:
        for (cid, fl), eids in col_elem_ids.items():
            if (cid in debris_zone1_cols and 7 <= fl <= 16) or (cid == "20" and fl >= 43):
                m.bfac[eids] = 0.0
                m.bfac_prev[eids] = 0.0

    # Attach 4 JointSets: (1) interior connections, (2) perimeter spandrel moment joints, (3) column splices, (4) slab ties
    interior_js = xfe.JointSet(
        j_names, j_na, j_nb, j_kind, j_e1, j_e2,
        j_kt, j_kc, j_kv, j_ncap, j_vcap, m.x0,
        gap_c=j_gap, walk_ax=j_wax, walk_lat=j_wlat, kr=j_kr,
        tgroup=j_tg, factor_fn=bolt_strength_factor,
    )
    spandrel_js = xfe.JointSet(
        spand_names, spand_na, spand_nb, 2, spand_e1, spand_e2,
        kt=spand_kt, kc=spand_kc, kv=spand_kv, ncap20=950.0, vcap20=800.0, x0=m.x0,
        kr=spand_kr, mpcap20=spand_mp, thu=0.06,
    )
    splice_js = xfe.JointSet(
        splice_names, sp_na, sp_nb, 3, [[0.0, 0.0, 1.0]] * len(splice_names), [[1.0, 0.0, 0.0]] * len(splice_names),
        kt=sp_kt, kc=sp_kc, kv=sp_kv, ncap20=sp_ncap, vcap20=sp_vcap, x0=m.x0,
        gap_c=0.0, walk_lat=10.0, kr=sp_kr, mpcap20=sp_mp,
        tgroup=sp_tg, factor_fn=bolt_strength_factor,
    )
    slab_js = xfe.JointSet(
        sl_names, sl_na, sl_nb, 4, sl_e1, sl_e2,
        kt=sl_kt, kc=0.0, kv=0.0, ncap20=sl_ncap, vcap20=sl_vcap, x0=m.x0,
        tgroup=sl_tg, factor_fn=bolt_strength_factor,
    )
    # If T8 WTC 1 debris is active, sever SW Zone 1/2 interior & spandrel joints initially too:
    if cfg.wtc1_debris:
        for idx_j, jm in enumerate(joint_meta):
            if (jm["col"] in debris_zone1_cols or jm["other"] in debris_zone1_cols) and 8 <= jm["floor"] <= 16:
                interior_js.state[idx_j] = 2

    m.add_joint_set(interior_js, adjust_dt=False)
    m.add_joint_set(spandrel_js, adjust_dt=False)
    m.add_joint_set(splice_js, adjust_dt=False)
    m.add_joint_set(slab_js, adjust_dt=True)

    # Storey-to-storey Floor Impact Contact: every girder chain on Floor `fl` impacts Floor `fl - 1`
    # (or Floor 5 when Floor 6 east bay is open, so Floors 7-13 east debris piles onto the 14-in. Floor 5 diaphragm!)
    imp_s, imp_m = [], []
    for fl in range(3, 49):
        for gkey, upper_chain in floor_girder_nodes[fl].items():
            # Find matching girder chain on nearest floor below (fl - 1, or fl - 2 across Floor 6 / Floor 47 double-height!)
            lower_chain = floor_girder_nodes.get(fl - 1, {}).get(gkey)
            if lower_chain is None and fl - 2 >= 2:
                lower_chain = floor_girder_nodes.get(fl - 2, {}).get(gkey)
            if lower_chain is not None and len(lower_chain) == len(upper_chain):
                imp_s.extend(upper_chain)
                imp_m.extend(lower_chain)

    # Also allow East Penthouse roof nodes to impact Main Roof east girder/column nodes:
    for pc in east_pent_cols:
        imp_s.append(pent_top_nodes[pc])
        imp_m.append(col_nodes_bot[(pc, 48)])
    if "P17" in pent_top_nodes and a2001_roof_chain:
        imp_s.append(pent_top_nodes["P17"])
        imp_m.append(a2001_roof_chain[len(a2001_roof_chain) // 2])

    m.add_impact("storey_impact", np.array(imp_s, np.int32), mnode=np.array(imp_m, np.int32),
                 nrm=[0.0, 0.0, 1.0], clr=14.0, mu=0.30, gmax=170.0)

    # Full gravity load vector (steel self-weight + slab/equipment lumped nodal masses)
    f_grav = np.zeros((m.nn, 3))
    f_grav[:, 2] = -m.mass_phys * G_ACC
    m.set_load_pattern(f_grav)

    roof_col_nodes = {cid: col_nodes_bot[(cid, 48)] for cid in PERIMETER_RING_UPPER + INTERIOR_COLS_24}
    north_cols = ["1"] + [str(k) for k in range(57, 41, -1)]
    north_roof_nodes = np.array([roof_col_nodes[c] for c in north_cols], np.int32)

    return WTC7Building(
        cfg=cfg, model=m, floors=floors, cols=cols,
        col_nodes_bot=col_nodes_bot, col_nodes_top=col_nodes_top, col_elem_ids=col_elem_ids,
        roof_col_nodes=roof_col_nodes, north_roof_nodes=north_roof_nodes,
        east_pent_nodes=east_pent_nodes, west_pent_nodes=west_pent_nodes,
        interior_joints=interior_js, spandrel_joints=spandrel_js, splice_joints=splice_js, slab_ties=slab_js,
        joint_meta=joint_meta, slab_meta=slab_meta,
    )

