"""Export detailed-model runs for the 3D viewer: reports/forensic/viewer/data/.

The run outputs keep only node positions at the snapshot temperatures (results/phase1/shell/runs/*.npz),
so the mesh is rebuilt from each run's stored Config (phase1/shell_model.py) and checked against the
first snapshot. Each run is written as a classic script (data/<run>.js) so the viewer opens from
file:// without a server. Displacements are rounded to RES (0.005 in., coarser only if a run moves
more than 16383 x RES) and stored as int16 differences between snapshots, component-major, low bytes
then high bytes, gzip-compressed and base64-encoded: about 0.8 MB a run instead of 9 MB.

    .venv/bin/python scripts/export_viewer.py                  # the runs named in report figures
    .venv/bin/python scripts/export_viewer.py nist_holes ...   # any runs
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import sys
from dataclasses import fields
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "phase1"))
from shell_model import Config, build                        # noqa: E402
from summarize_shell import classify                         # noqa: E402
from report_figures import BASE, KEY                         # noqa: E402

SHELL = ROOT / "results" / "phase1" / "shell" / "runs"
OUT = ROOT / "reports" / "forensic" / "viewer" / "data"
NIST = ("nist_holes", "nist_face_drawn", "nist_mu0.3", "nist_face_plates")
DEFAULT = list(KEY) + [n for n in NIST if n not in KEY]
LABELS = {
    BASE: "Baseline (reported, half rate)",
    "mu0_r0.5": "Friction 0 at column 79",
    "Q12_clear_mu0_r0.5": "Side plates removed, friction 0",
    "S7_peak700_r0.5": "Peak 700 C",
    "favourable": "Combined run (preregistered)",
    "favourable_dump": "Combined run, repeat with state dumps",
    "favourable_s6": "Combined run, Section 6 repeat",
    "nist_replica": "NIST replica",
    "nist_holes": "NIST replica, standard holes restored",
    "nist_face_drawn": "NIST replica, drawn face restored",
    "nist_mu0.3": "NIST replica, friction 0.3",
    "nist_face_plates": "NIST replica, drawn face and side plates restored",
}
TRACE = ("lat79", "ax79", "dz79", "twist79")
SKIP_CFG = ("name", "threads", "dump_after", "dump_every", "t_end")
INF = 999.0                      # plane limits at or above this are unbounded (add_plane uses 1e3)
RES = 0.005                      # displacement resolution, in.


def b64gz(a: np.ndarray) -> str:
    return base64.b64encode(gzip.compress(np.ascontiguousarray(a).tobytes(), 9, mtime=0)).decode()


def pack(u):
    """Displacements (snapshot, node, 3) -> (resolution, bytes) in the layout viewer.js reads."""
    res = max(RES, float(np.abs(u).max()) / 16383)               # keeps every difference inside int16
    q = np.round(u / res).astype(np.int32).transpose(0, 2, 1)     # (snapshot, component, node)
    dq = np.ascontiguousarray(np.diff(q, axis=0, prepend=np.zeros_like(q[:1])), np.int16)
    b = dq.view(np.uint8).reshape(-1, 2)
    return res, np.concatenate([b[:, 0], b[:, 1]])


def unpack(packed, res, n_snap):
    """Inverse of pack(), as viewer.js does it (for the tests)."""
    n = len(packed) // 2
    d = (packed[:n].astype(np.uint16) | (packed[n:].astype(np.uint16) << 8)).view(np.int16)
    q = np.cumsum(d.reshape(n_snap, 3, -1).astype(np.int32), axis=0)
    return (q * res).transpose(0, 2, 1)


def config_of(r):
    names = {f.name for f in fields(Config)}
    return Config(**{k: v for k, v in r["config"].items() if k in names})


def plane_quad(m, pc):
    """Corners of a contact plane; unbounded directions are clipped to its slave nodes' extent + 2 in."""
    P = pc.P
    p0, t1, t2, lim = P[0:3], P[6:9], P[9:12], P[12:16].copy()
    rel = m.x0[pc.nodes] - p0
    for k, t in ((0, t1), (1, t2)):
        s = rel @ t
        if lim[2 * k] <= -INF:
            lim[2 * k] = s.min() - 2.0
        if lim[2 * k + 1] >= INF:
            lim[2 * k + 1] = s.max() + 2.0
    return [(p0 + a * t1 + b * t2).round(3).tolist() for a, b in
            ((lim[0], lim[2]), (lim[1], lim[2]), (lim[1], lim[3]), (lim[0], lim[3]))]


def geometry(fl):
    m = fl.m
    parts = sorted({k.split(".")[0].rstrip("0123456789") for k in m.parts})
    pid = np.zeros(m.ne, np.uint8)
    for k, els in m.parts.items():
        pid[np.concatenate(els)] = parts.index(k.split(".")[0].rstrip("0123456789"))
    conn = m.conn.astype(np.uint16 if m.nn < 65536 else np.uint32)
    g = dict(nn=int(m.nn), ne=int(m.ne), parts=parts, conn_type=conn.dtype.name,
             x0=b64gz(m.x0.astype(np.float32)), conn=b64gz(conn), pid=b64gz(pid))
    key = hashlib.sha256((g["x0"] + g["conn"] + g["pid"]).encode()).hexdigest()[:12]
    return key, g


def export(name):
    r = json.loads((SHELL / f"{name}.json").read_text())
    d = np.load(SHELL / f"{name}.npz")
    fl = build(config_of(r))
    m = fl.m
    x = d["x"]
    if x.shape[1] != m.nn or np.abs(x[0] - m.x0).max() > 1e-3:
        raise SystemExit(f"{name}: rebuilt mesh does not match the saved snapshots")
    gkey, g = geometry(fl)
    gfile = OUT / f"geom_{gkey}.js"
    if not gfile.exists():
        gfile.write_text(f"WTC7.geom[{json.dumps(gkey)}] = {json.dumps(g)};\n")

    u = x - m.x0[None].astype(np.float32)
    res, packed = pack(u)
    unorm = np.linalg.norm(u, axis=2).max(1)

    sp = fl.springs
    groups = [n.rstrip("0123456789").rstrip("_") for n in sp.names]
    brk = {n: round(b["t"], 4) for n, b in r["breaks"].items()}
    springs = dict(names=sp.names, group=groups, na=sp.na.tolist(), wa=sp.wa.round(5).tolist(),
                   t_break=[brk.get(n) for n in sp.names])

    rows = r["rows"]
    trace = {"t": [round(x["t"], 4) for x in rows], "T": [round(x["T_beam"], 1) for x in rows]}
    trace.update({k: [round(x[k], 4) for x in rows] for k in TRACE})

    base = json.loads((SHELL / f"{BASE}.json").read_text())["config"]
    diff = {k: v for k, v in r["config"].items() if k not in SKIP_CFG and base.get(k) != v}
    planes = [dict(name=pc.name, quad=plane_quad(m, pc)) for pc in m.planes]
    run = dict(name=name, label=LABELS.get(name, name), reading=classify(r), status=r["status"],
               rate=r["config"]["rate"], diff=diff, col79=r["config"]["col79"], walk_lat=r["config"]["walk_lat"],
               events={k: dict(t=round(v["t"], 4), T=round(v["T_beam"], 1)) for k, v in r["events"].items()},
               geom=gkey, frames=dict(t=d["t"].round(4).tolist(), T=d["T_beam"].round(1).tolist(),
                                      unorm=unorm.round(3).tolist()),
               res=res, u=b64gz(packed), planes=planes, springs=springs, trace=trace)
    (OUT / f"{name}.js").write_text(f"WTC7.runs[{json.dumps(name)}] = {json.dumps(run)};\n")
    return dict(name=name, label=run["label"], reading=run["reading"], frames=len(d["t"]),
                bytes=(OUT / f"{name}.js").stat().st_size)


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    names = argv or DEFAULT
    index = []
    for n in names:
        index.append(export(n))
        print(f"{n}: {index[-1]['frames']} snapshots, {index[-1]['bytes'] / 1e6:.1f} MB", flush=True)
    # keep runs exported earlier that are still on disk
    known = {i["name"] for i in index}
    old = OUT / "index.js"
    if old.exists() and argv:
        prev = json.loads(old.read_text().split("=", 1)[1].rstrip().rstrip(";"))
        index = [i for i in prev["runs"] if i["name"] not in known and (OUT / f"{i['name']}.js").exists()] + index
    order = {n: i for i, n in enumerate(DEFAULT)}
    index.sort(key=lambda i: order.get(i["name"], len(order)))
    old.write_text("WTC7.index = " + json.dumps(dict(base=BASE, runs=index)) + ";\n")


if __name__ == "__main__":
    main(sys.argv[1:])
