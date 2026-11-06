"""3D viewer export (scripts/export_viewer.py): the rebuilt mesh matches the saved run and the packed
displacements come back within half the stored resolution."""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results" / "phase1" / "shell" / "runs" / "nist_replica.npz"
pytestmark = pytest.mark.skipif(not RUN.exists(), reason="run output not present")


def exporter():
    spec = importlib.util.spec_from_file_location("export_viewer", ROOT / "scripts" / "export_viewer.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["export_viewer"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_pack_round_trip():
    ev = exporter()
    x = np.load(RUN)["x"]
    u = x - x[0]
    res, packed = ev.pack(u)
    back = ev.unpack(packed, res, len(u))
    assert np.abs(back - u).max() <= res / 2 + 1e-5


def test_export_one_run(tmp_path, monkeypatch):
    ev = exporter()
    monkeypatch.setattr(ev, "OUT", tmp_path)
    info = ev.export("nist_replica")
    r = json.loads((tmp_path / "nist_replica.js").read_text().split("=", 1)[1].rstrip().rstrip(";"))
    assert info["frames"] == len(r["frames"]["t"]) == len(np.load(RUN)["t"])
    assert (tmp_path / f"geom_{r['geom']}.js").exists()
    assert r["reading"] == "walk-off"
