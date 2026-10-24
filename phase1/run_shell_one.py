"""Run one Phase 1 detailed (shell) model configuration.

Usage: python phase1/run_shell_one.py <name> [key=value ...]
Keys are fields of phase1/shell_model.Config. Writes results/phase1/shell/runs/<name>.json
(histories, events, connection failures, run info) and <name>.npz (deformed node positions at
every 50 C of beam temperature and at column 79 connection failures, float32).
"""
import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from shell_model import Config, simulate  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results" / "phase1" / "shell" / os.environ.get("WTC7_SHELL_RUNS", "runs")


def parse(v):
    for f in (int, float):
        try:
            return f(v)
        except ValueError:
            pass
    return v


def main(argv):
    name, kw = argv[0], dict(a.split("=", 1) for a in argv[1:])
    cfg = Config(name=name, **{k: parse(v) for k, v in kw.items()})
    t0 = time.time()
    res, mon = simulate(cfg, verbose=True)
    res["wall_s"] = time.time() - t0
    cpu = next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), "")
    res["host"] = dict(python=platform.python_version(), machine=platform.machine(), cpu=cpu,
                       logical_cpus=os.cpu_count(), threads=cfg.threads)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(res, default=float))
    if mon.snaps:
        np.savez_compressed(OUT / f"{name}.npz", t=np.array([s["t"] for s in mon.snaps]),
                            T_beam=np.array([s["T_beam"] for s in mon.snaps]),
                            x=np.stack([s["x"] for s in mon.snaps]))
    ev = {k: round(v["T_beam"], 1) for k, v in res["events"].items()}
    print(f"{name}: {res['status']} in {res['wall_s']:.0f} s, {res['info']['cycles']} cycles, events (beam C): {ev}",
          flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
