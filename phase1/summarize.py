"""Summarize Phase 1 beam-element runs against the preregistered criteria.

Reads results/phase1/runs/*.json, writes results/phase1/summary.md, summary.csv and
plots in results/phase1/plots/.
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "results" / "phase1" / "runs"
OUT = ROOT / "results" / "phase1"
LIMIT_E1, LIMIT_E2 = 400.0, 700.0
WALKS = (5.5, 6.0, 6.25, 6.5)
SWEEP_NAMES = {
    "S1": "Girder studs", "S3": "Clip slot allowance", "S4": "Seat and face friction", "S5": "Col 79 restraint",
    "S6": "Slab constraint", "S8": "Heat then cool", "S9": "Steel property set", "S10": "Yield strength",
    "S11": "Girder end gap at col 79", "S12": "Lateral gap at col 44", "S13": "Bolt deformation at failure",
    "S14": "Stud slip at failure", "S15": "Beam-to-slab friction",
}


def load():
    runs = {}
    for p in sorted(RUNS.glob("*.json")):
        runs[p.stem] = json.loads(p.read_text())
    return runs


def ev(r, key):
    e = r["events"].get(key)
    return None if e is None else e["T_beam"]


def fmt(x):
    return "none" if x is None else f"{x:.0f}"


def lat_at(r, T):
    rows = [row for row in r["rows"] if row["T_beam"] <= T + 1e-6 and row["t"] <= first_peak_time(r)]
    return max((abs(row["lat79"]) for row in rows), default=float("nan"))


def first_peak_time(r):
    peak = r["config"]["peak"]
    ts = [row["t"] for row in r["rows"] if row["T_beam"] >= peak - 1e-6]
    return ts[0] if ts else float("inf")


def walk_T(r, w):
    if r["config"]["walk_lat"] == w and ev(r, "E2_walkoff_79") is not None:
        return ev(r, "E2_walkoff_79")
    return ev(r, f"E2@{w}")


def qs_ratio(r):
    """Largest kinetic / strain energy outside the steps where something broke."""
    vals = [row["ke"] / row["se"] for row in r["rows"] if row["se"] > 1e-6 and not row["broke"]]
    allv = [row["ke"] / row["se"] for row in r["rows"] if row["se"] > 1e-6]
    return (max(vals) if vals else float("nan"), max(allv) if allv else float("nan"))


def classify(runs):
    base = runs.get("baseline")
    if base is None:
        return "no baseline", []
    e1, e2 = ev(base, "E1_g79_all_bolts"), walk_T(base, 6.25)
    if base["status"] == "incomplete" and e2 is None:
        return "INCOMPLETE (baseline stopped before E2 and before 700 °C)", []
    sweeps = {k: v for k, v in runs.items() if k.startswith("S") or k == "favourable"}
    base_walk = e2 is not None and e2 <= LIMIT_E2
    flips = []
    for name, r in sweeps.items():
        walks = {w: walk_T(r, w) for w in WALKS}
        w = walks[r["config"]["walk_lat"]]
        walk = w is not None and w <= LIMIT_E2
        if walk != base_walk:
            flips.append((name, w))
    # S2: same histories, different thresholds
    for wl in WALKS:
        w = walk_T(base, wl)
        if (w is not None and w <= LIMIT_E2) != base_walk:
            flips.append((f"S2_walk{wl}", w))
    if base_walk and e1 is not None and e1 <= LIMIT_E1 and not flips:
        return "CONFIRMS (screening model; robust across all sweeps)", flips
    if base_walk and e1 is not None and e1 <= LIMIT_E1:
        return "CONFIRMS under baseline; CONDITIONAL across sweeps", flips
    any_walk = any((walk_T(r, w) or 1e9) <= LIMIT_E2 for r in sweeps.values() for w in WALKS
                   if w == r["config"]["walk_lat"]) or any((walk_T(base, w) or 1e9) <= LIMIT_E2 for w in WALKS)
    incomplete = [k for k, r in sweeps.items() if r["status"] == "incomplete"]
    if not any_walk and not incomplete:
        return "CONTRADICTS (screening model)", flips
    if not any_walk:
        return f"no walk-off in any completed run; INCOMPLETE runs: {', '.join(incomplete)}", flips
    return "CONDITIONAL (screening model)", flips


def plot_group(runs, names, title, fname):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for n in names:
        r = runs[n]
        T = [row["T_beam"] for row in r["rows"]]
        lat = [-row["lat79"] for row in r["rows"]]
        ref = n == names[0]
        ax.plot(T, lat, lw=1.8 if ref else 1.0, label=n, color="black" if ref else None)
    ax.axhline(6.25, color="0.4", ls="--", lw=0.8)
    ax.axhline(-6.25, color="0.4", ls="--", lw=0.8)
    ax.text(25, 6.4, "walk-off, 6.25 in.", fontsize=8, color="0.3")
    ax.axvline(LIMIT_E2, color="0.6", ls=":", lw=0.8)
    ax.set_xlabel("Floor beam temperature (°C)")
    ax.set_ylabel("Girder end movement at col 79,\nperpendicular to girder, west + (in.)")
    ax.set_title(title, fontsize=10)
    ax.legend(fontsize=7, frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    (OUT / "plots").mkdir(exist_ok=True)
    fig.savefig(OUT / "plots" / fname, dpi=130)
    plt.close(fig)


def followup_section(runs):
    """Tables for the follow-up runs (see docs/phase1_gate.md)."""
    out = ["\n## Follow-up analysis\n"]
    w = lambda n: walk_T(runs[n], 6.25) if n in runs else None
    w55 = lambda n: walk_T(runs[n], 5.5) if n in runs else None
    fr = [("S4_mu0", 0.0), ("S4_mu0.2", 0.2), ("F_mu0.22", 0.22), ("F_mu0.24", 0.24), ("F_mu0.26", 0.26),
          ("F_mu0.28", 0.28), ("baseline", 0.30), ("S4_mu0.45", 0.45), ("S4_mu0.6", 0.6)]
    out.append("### Friction at the column 79 seat and bearing face\n")
    out.append("| Friction | Walk-off at 6.25 in. (°C) | Walk-off at 5.5 in. (°C) | Girder bow > L/50 (°C) |\n|---|---|---|---|")
    for n, m in fr:
        if n in runs:
            out.append(f"| {m:.2f} | {fmt(w(n))} | {fmt(w55(n))} | {fmt(ev(runs[n], 'E5_girder_buckled'))} |")
    out.append("\nMesh check of the walk-off temperature (6.25 in.):\n")
    out.append("| Friction | Baseline mesh | Mesh x2 | Mesh x4 |\n|---|---|---|---|")
    for m, b in ((0.0, "S4_mu0"), (0.2, "S4_mu0.2")):
        out.append(f"| {m} | {fmt(w(b))} | {fmt(w(f'F_mesh_r2_mu{m}'))} | {fmt(w(f'F_mesh_r4_mu{m}'))} |")
    out.append("\n### Girder skew (digitized 14.6°)\n")
    out.append("| Skew (°) | tan(skew) | Friction 0.20 | Friction 0.30 |\n|---|---|---|---|")
    import math
    for a, n2, n3 in ((12.6, "F_skew12.6_mu0.2", "F_skew12.6_mu0.3"), (14.6, "S4_mu0.2", "baseline"),
                      (16.6, "F_skew16.6_mu0.2", "F_skew16.6_mu0.3")):
        out.append(f"| {a} | {math.tan(math.radians(a)):.3f} | {fmt(w(n2))} | {fmt(w(n3))} |")
    out.append("\n### Every other parameter, rerun at friction 0.20\n")
    out.append("Walk-off temperature at 6.25 in.; friction 0.20 alone gives "
               f"{fmt(w('S4_mu0.2'))} °C. 'none' means no walk-off up to 800 °C.\n")
    out.append("| Run | Walk-off (°C) | Change (°C) | E1 (°C) | Col 44 bolts (°C) |\n|---|---|---|---|---|")
    ref = w("S4_mu0.2")
    for n in sorted(k for k in runs if k.startswith("C_")):
        t = w(n)
        d = "n/a" if t is None or ref is None else f"{t - ref:+.0f}"
        out.append(f"| {n[2:]} | {fmt(t)} | {d} | {fmt(ev(runs[n], 'E1_g79_all_bolts'))} | "
                   f"{fmt(ev(runs[n], 'E3_g44_all_bolts'))} |")
    out.append("\n### Other diagnostics\n")
    for n, label in (("F_square_mu0", "Bearing face square to the girder, no friction anywhere (NIST-like idealization)"),
                     ("diag_square_bearing", "Bearing face square to the girder, friction 0.30"),
                     ("favourable", "Preregistered most-favourable combination"),
                     ("F_favourable_actual", "Most-favourable combination rebuilt from the friction-0.20 runs")):
        if n in runs:
            out.append(f"- {label}: walk-off at {fmt(w(n))} °C (5.5 in.: {fmt(w55(n))} °C).")
    for n in ("F_rate_half_S5", "F_rate_half_S11_1.0"):
        if n in runs:
            src = {"F_rate_half_S5": "S5_col79_flexible", "F_rate_half_S11_1.0": "S11_gap79_1.0"}[n]
            keys = ("E1_g79_all_bolts", "E3_g44_all_bolts", "first_fin", "E5_girder_buckled")
            pairs = ", ".join(f"{k.split('_')[0]} {fmt(ev(runs[n], k))} vs {fmt(ev(runs[src], k))}" for k in keys)
            out.append(f"- Half heating rate, {src}: {pairs} (°C, half rate vs normal rate).")
    return out


def plot_series(runs, names, key, ylabel, title, fname, scale=1.0):
    names = [n for n in names if n in runs and key in runs[n]["rows"][0]]
    if not names:
        return
    fig, ax = plt.subplots(figsize=(7, 4.0))
    for n in names:
        rows = runs[n]["rows"]
        ax.plot([r["T_beam"] for r in rows], [scale * r[key] for r in rows], lw=1.5 if n == "baseline" else 1.0,
                color="black" if n == "baseline" else None, label=n)
    ax.set_xlabel("Floor beam temperature (°C)")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    (OUT / "plots").mkdir(exist_ok=True)
    fig.savefig(OUT / "plots" / fname, dpi=130)
    plt.close(fig)


def plot_plan(runs, names, fname, mag=10.0):
    """Deformed plan of girder and beams at each saved temperature, displacements x mag."""
    names = [n for n in names if n in runs and runs[n].get("snapshots")]
    if not names:
        return
    fig, axes = plt.subplots(1, len(names), figsize=(5.2 * len(names), 5.0), squeeze=False)
    for ax, n in zip(axes[0], names):
        snaps = runs[n]["snapshots"]
        g0 = np.array(snaps[0]["girder"])
        b0 = [np.array(b) for b in snaps[0]["beams"]]
        cmap = plt.get_cmap("viridis")
        for k, sn in enumerate(snaps):
            col = cmap(k / max(len(snaps) - 1, 1))
            g = g0 + mag * (np.array(sn["girder"]) - g0)
            ax.plot(g[:, 0], g[:, 1], color=col, lw=2.0, label=f"{sn['T_beam']:.0f} °C")
            for b, bb in zip(b0, sn["beams"]):
                bb = b + mag * (np.array(bb) - b)
                ax.plot(bb[:, 0], bb[:, 1], color=col, lw=0.8)
        ax.plot([0], [0], "ks", ms=6)
        ax.annotate("col 79", (0, 0), xytext=(-60, -30), textcoords="offset points", fontsize=8)
        ax.plot([g0[-1, 0]], [g0[-1, 1]], "ks", ms=6)
        ax.annotate("col 44", tuple(g0[-1]), xytext=(-60, 8), textcoords="offset points", fontsize=8)
        ax.set_aspect("equal")
        ax.set_title(f"{n} (displacements x{mag:g})", fontsize=10)
        ax.set_xlabel("x, east (in.)")
        ax.set_ylabel("y, north (in.)")
        ax.legend(fontsize=7, frameon=False, loc="lower right")
        ax.grid(alpha=0.2)
    fig.tight_layout()
    (OUT / "plots").mkdir(exist_ok=True)
    fig.savefig(OUT / "plots" / fname, dpi=120)
    plt.close(fig)


def main():
    runs = load()
    if not runs:
        sys.exit("no runs")
    cls, flips = classify(runs)
    lines = ["# Phase 1 beam-element (plan-view) results\n",
             "Generated by `phase1/summarize.py` from `results/phase1/runs/`. Temperatures are floor-beam "
             "temperatures (girder = 20 + 0.828 (beam - 20)). 'none' means the event did not occur in the run. "
             "Lateral movement is the girder end at column 79 relative to its seat, perpendicular to the girder; "
             "west is positive.\n",
             f"**Outcome class (preregistration Section 3): {cls}.** This is the screening model (plan view, no "
             "vertical sagging, twist or rocking); the Phase 1 gate needs the detailed shell model.\n"]
    if flips:
        lines.append("Runs whose walk-off result (by 700 °C) differs from the baseline:\n")
        for n, w in flips:
            lines.append(f"- {n}: walk-off at {fmt(w)} °C")
        lines.append("")
    hdr = ["Run", "Status", "First stud", "Col 79 seat bolts", "E1 col 79 all bolts", "E3 col 44 all bolts",
           "First fin", "E4 beam buckled", "E5 girder bow > L/50", "E2 walk-off (6.25 in.)", "Max lateral by 700 °C (in.)",
           "KE/SE max (no-failure steps)", "KE/SE max (all steps)", "Wall (s)"]
    lines += ["| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
    rows_csv = []
    primary = [n for n in runs if not n.startswith(("F_", "C_"))]
    follow = sorted(n for n in runs if n.startswith(("F_", "C_")))
    order = sorted(primary, key=lambda n: (not n == "baseline", n)) + follow
    for n in order:
        if follow and n == follow[0]:
            lines.append("\n## Follow-up runs (friction threshold, skew, mesh, and every parameter at mu = 0.2)\n")
            lines += ["| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
        r = runs[n]
        q, qall = qs_ratio(r)
        vals = [n, r["status"], fmt(ev(r, "first_stud")), fmt(ev(r, "g79_seat_bolts")), fmt(ev(r, "E1_g79_all_bolts")),
                fmt(ev(r, "E3_g44_all_bolts")), fmt(ev(r, "first_fin")), fmt(ev(r, "E4_beam_buckled")),
                fmt(ev(r, "E5_girder_buckled")),
                fmt(walk_T(r, r["config"]["walk_lat"])), f"{lat_at(r, LIMIT_E2):.2f}", f"{q:.1e}", f"{qall:.1e}",
                f"{r['wall_s']:.0f}"]
        lines.append("| " + " | ".join(vals) + " |")
        rows_csv.append(dict(zip(hdr, vals)) | {"ndof": r["ndof"], "elements": r["n_elements"]})
    base = runs.get("baseline")
    if base:
        lines.append("\n## S2: walk-off distance (thresholds applied to the baseline history)\n")
        lines.append("| Lateral walk-off distance (in.) | Walk-off beam temperature (°C) |\n|---|---|")
        for w in WALKS:
            lines.append(f"| {w} | {fmt(walk_T(base, w))} |")
        lines.append("\n## S7: peak temperature (read off the baseline monotonic ramp)\n")
        lines.append("A rate-independent monotonic ramp to a lower peak follows the same path up to that peak, so "
                     "each S7 case is the baseline history truncated (the half-rate check below tests the "
                     "rate-independence).\n")
        lines.append("| Peak beam / girder (°C) | E1 by peak | Walk-off by peak | Max lateral at col 79 (in.) |\n|---|---|---|---|")
        for pk in (400, 500, 600, 700):
            e1 = ev(base, "E1_g79_all_bolts")
            w = walk_T(base, 6.25)
            lines.append(f"| {pk} / {20 + 0.828 * (pk - 20):.0f} | {'yes' if e1 and e1 <= pk else 'no'} | "
                         f"{'yes' if w and w <= pk else 'no'} | {lat_at(base, pk):.2f} |")
    # checks
    lines.append("\n## Numerical checks\n")
    mesh = [n for n in ("baseline", "check_mesh_r2", "check_mesh_r4") if n in runs]
    if len(mesh) > 1:
        lines.append("| Mesh | Elements | DOF | E1 (°C) | E2 (°C) | Max lateral by 700 °C (in.) |\n|---|---|---|---|---|---|")
        for n in mesh:
            r = runs[n]
            lines.append(f"| {n} | {r['n_elements']} | {r['ndof']} | {fmt(ev(r, 'E1_g79_all_bolts'))} | "
                         f"{fmt(walk_T(r, 6.25))} | {lat_at(r, LIMIT_E2):.2f} |")
    if "check_rate_half" in runs and base:
        r = runs["check_rate_half"]
        lines.append(f"\nHalf heating rate: E1 at {fmt(ev(r, 'E1_g79_all_bolts'))} °C (baseline "
                     f"{fmt(ev(base, 'E1_g79_all_bolts'))}), walk-off at {fmt(walk_T(r, 6.25))} °C (baseline "
                     f"{fmt(walk_T(base, 6.25))}), max lateral by 700 °C {lat_at(r, 700):.2f} in. (baseline "
                     f"{lat_at(base, 700):.2f}).")
    if follow:
        lines += followup_section(runs)
    lines.append("\n## Compute\n")
    lines.append("Solver `wtc7/fe2d.py`: implicit Newmark (beta 0.3025, gamma 0.6), mass-proportional damping, "
                 "pseudo-time step 2 s (= 2 °C at the baseline heating rate) halved on non-convergence down to "
                 "dt/4096, break checks after each converged step with re-solve (NCSTAR 1-9 §11.2.9 approach). "
                 "One process per run, single-threaded.\n")
    lines.append("| Run | Elements | DOF | Steps | Mass scale | Wall time (s) | Status |\n|---|---|---|---|---|---|---|")
    for n in order:
        r = runs[n]
        lines.append(f"| {n} | {r['n_elements']} | {r['ndof']} | {len(r['rows'])} | {r['config']['mass_scale']:g} | "
                     f"{r['wall_s']:.0f} | {r['status']} |")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n")
    with open(OUT / "summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_csv[0]))
        w.writeheader()
        w.writerows(rows_csv)
    # plots
    groups = {}
    for n in runs:
        key = n.split("_")[0]
        groups.setdefault(key, []).append(n)
    for key, names in groups.items():
        if key in SWEEP_NAMES and "baseline" in runs:
            plot_group(runs, ["baseline"] + names, f"{key}: {SWEEP_NAMES[key]}", f"{key}.png")
    extra = [n for n in ("baseline", "favourable", "F_favourable_actual", "diag_square_bearing", "F_square_mu0")
             if n in runs]
    plot_group(runs, extra, "Baseline, most-favourable combinations, square-face diagnostics", "overview.png")
    fric = [n for n in ("S4_mu0", "S4_mu0.2", "F_mu0.22", "F_mu0.24", "F_mu0.26", "F_mu0.28", "S4_mu0.45") if n in runs]
    if fric:
        plot_group(runs, ["baseline"] + fric, "Friction at the column 79 seat and face (baseline 0.30)", "friction.png")
    paired = sorted(n for n in runs if n.startswith("C_"))
    if paired:
        plot_group(runs, ["S4_mu0.2"] + paired, "Every parameter rerun at friction 0.20", "paired_mu0.2.png")
    mesh_runs = [n for n in ("baseline", "check_mesh_r2", "check_mesh_r4", "check_rate_half") if n in runs]
    plot_group(runs, mesh_runs, "Mesh refinement and heating-rate checks", "checks.png")
    plot_plan(runs, ["baseline", "S4_mu0.2"], "plan_deformed.png")
    s4 = ["baseline"] + sorted(n for n in runs if n.startswith("S4"))
    plot_series(runs, s4, "girderN", "Girder axial force (kip, compression negative)",
                "Girder axial force, friction sweep", "girder_force_S4.png")
    plot_series(runs, s4, "girder_bow", "Largest girder bow from its chord (in., west +)",
                "Girder bow in plan, friction sweep", "girder_bow_S4.png")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
