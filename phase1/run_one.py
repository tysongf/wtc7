"""Run one Phase 1 plan-model configuration and save it to results/phase1/runs/<name>.json.

Usage: python phase1/run_one.py <name> [key=value ...]
Keys are Config fields; values are parsed as float, int or string.
"""
import json
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plan_model import Config, simulate  # noqa: E402

import os

OUT = Path(__file__).resolve().parents[1] / "results" / "phase1" / os.environ.get("WTC7_RUNS", "runs")


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
    res = simulate(cfg, verbose=True)
    res["wall_s"] = time.time() - t0
    res["host"] = dict(python=platform.python_version(), machine=platform.machine())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(res, default=float))
    ev = {k: round(v["T_beam"], 1) for k, v in res["events"].items()}
    print(f"{name}: {res['status']} in {res['wall_s']:.0f} s, events (beam C): {ev}")


if __name__ == "__main__":
    main(sys.argv[1:])
