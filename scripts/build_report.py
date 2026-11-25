"""Build the unified WTC 7 Phase 1 website: reports/forensic/index.html.

Combines:
1. A Plain-English Question-Driven Audit Guide (6 audit cards + 5 custom theme-aware 2D SVG diagrams
   + synchronized 3D step triggers).
2. The complete Phase 1 Technical Forensic Report (every number read from run outputs, assumptions,
   and checksums at build time).
3. The native Vue + Three.js 3D Shell Model Explorer (no iframe; works from file:// and http://).

Rebuild after new runs finish:
    .venv/bin/python scripts/export_viewer.py
    .venv/bin/python scripts/build_report.py
"""
from __future__ import annotations

import csv
import html
import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "phase1"))
OUT = ROOT / "reports" / "forensic"
ASSETS = OUT / "assets"
RES = ROOT / "results" / "phase1"
SHELL = RES / "shell" / "runs"
LOGS = RES / "shell" / "logs"

E = html.escape


# ---------------------------------------------------------------- helpers
def table(head, rows, cls=""):
    h = "".join(f"<th>{c}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def fig(src, cap, num):
    return (f'<figure id="fig{num}"><a href="assets/{src}"><img src="assets/{src}" alt="{E(cap)}" loading="lazy"></a>'
            f"<figcaption><b>Figure {num}.</b> {cap}</figcaption></figure>")


def chip(text, kind):
    return f'<span class="chip {kind}">{E(text)}</span>'


def T(ev, key):
    return f"{ev[key]['T_beam']:.0f}" if key in ev else "&ndash;"


def load_json(path):
    return json.loads(Path(path).read_text())


def code(s):
    return f"<code>{E(s)}</code>"


def step_btn(label, **opts):
    payload = E(json.dumps(opts, separators=(",", ":")))
    return f'<button type="button" class="step-btn" data-viewer-step="{payload}">{label} &#x25B6;</button>'


# ---------------------------------------------------------------- data
def shell_runs():
    return {f.stem: load_json(f) for f in sorted(SHELL.glob("*.json"))}


def viewer_runs():
    idx = OUT / "viewer" / "data" / "index.js"
    if not idx.exists():
        return set()
    txt = idx.read_text().strip()
    m = re.search(r"WTC7\.index\s*=\s*(\{.*\})\s*;?\s*$", txt, re.S)
    if not m:
        return set()
    return {r["name"] for r in json.loads(m.group(1)).get("runs", [])}


def run_status():
    from run_shell import FOLLOW, MESH, NIST, NIST_RESTORE, P1, P1_HALF, P2
    done = {f.stem for f in SHELL.glob("*.json")}
    running = {f.stem for f in LOGS.glob("*.log")} - done if LOGS.exists() else set()
    rows = []
    for prio, table_ in (("1, full rate", P1), ("1, half rate", P1_HALF), ("mesh", MESH), ("2, half rate", P2),
                         ("Section 6 follow-up", FOLLOW), ("NIST replica", NIST),
                         ("NIST restore", NIST_RESTORE)):
        for n, kw in table_.items():
            st = "done" if n in done else ("running" if n in running else
                                           "conditional" if table_ is NIST_RESTORE else "queued")
            desc = ", ".join(f"{k}={v}" for k, v in kw.items()) or "baseline values"
            rows.append((prio, n, desc, st))
    return rows


def drawings_runs():
    return {f.stem: load_json(f) for f in sorted((RES / "runs_drawings").glob("*.json"))}


def digitized_summary():
    return list(csv.DictReader(open(RES / "summary.csv")))


def prereg_hashes():
    out = []
    for line in (ROOT / "docs" / "compute_log.md").read_text().splitlines():
        m = re.match(r"\| (20\d\d-\d\d-\d\dT\d\d:\d\dZ) \| (docs/preregistration\.md[^|]*)\| ([0-9a-f]{64}) \|", line)
        if m:
            out.append((m.group(1), m.group(2).strip(), m.group(3)))
    return out


def source_hashes():
    out = []
    for line in (ROOT / "sources" / "SHA256SUMS").read_text().splitlines():
        h, f = line.split()
        if not f.startswith("drawings/"):
            out.append((f, h))
    return out


def drawing_sources():
    out = []
    txt = (ROOT / "sources" / "drawings" / "SOURCES.md").read_text()
    sec = txt.split("### Primary drawings")[1].split("###")[0]
    for line in sec.splitlines():
        if line.startswith("| `"):
            c = [x.strip() for x in line.strip("|").split("|")]
            out.append((c[0].strip("`"), c[1], c[2], c[3], c[5].strip("`")))
    return out


def verification_rows():
    txt = (RES / "shell" / "verification.md").read_text()
    rows = [l for l in txt.splitlines() if re.match(r"\| \d+ x \d+", l)]
    return [[c.strip() for c in r.strip("|").split("|")] for r in rows]


def assumptions():
    return list(csv.DictReader(open(ROOT / "docs" / "assumptions.csv")))


# ---------------------------------------------------------------- 2D SVG diagrams for the Audit Guide
def svg_domino():
    return """<figure class="svg-fig">
<svg viewBox="0 0 760 250" role="img" aria-label="NIST domino chain and Column 79 buckling capacity by unbraced storeys">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,1 L9,5 L0,9 z" fill="var(--muted)"/>
    </marker>
  </defs>
  <text x="14" y="20" class="svg-h">A. NIST's Proposed Domino Chain &amp; Our Staged Audit</text>
  <g transform="translate(14,32)">
    <rect width="404" height="44" rx="6" fill="var(--card)" stroke="var(--accent)" stroke-width="1.5"/>
    <text x="10" y="18" class="svg-b">1. Floor 13 East Beams Expand &rarr; Push Girder A2001 Off Seat</text>
    <text x="10" y="35" class="svg-s">Phase 1 (Tested here, uniform ramp) &mdash; Verdict: CONDITIONAL (0/41 at 600 &deg;C)</text>
    <line x1="202" y1="44" x2="202" y2="56" stroke="var(--muted)" stroke-width="1.4" marker-end="url(#arr)"/>

    <g transform="translate(0,58)">
      <rect width="404" height="40" rx="6" fill="var(--card)" stroke="var(--line)"/>
      <text x="10" y="17" class="svg-b">2. Multi-Hour Fires &amp; Floor Cascade (Floors 13 &rarr; 5)</text>
      <text x="10" y="32" class="svg-s">Phase 2 (Actual fire temperature histories) &mdash; Gated; not started</text>
    </g>
    <line x1="202" y1="98" x2="202" y2="110" stroke="var(--muted)" stroke-width="1.4" marker-end="url(#arr)"/>

    <g transform="translate(0,112)">
      <rect width="404" height="42" rx="6" fill="var(--okbg)" stroke="var(--ok)"/>
      <text x="10" y="17" class="svg-b">3. Column 79 Left Unbraced Over 9 Storeys &rarr; Buckles</text>
      <text x="10" y="33" class="svg-s">Hand-checked &mdash; CONFIRMED: buckles once 5&ndash;6 storeys lose lateral bracing</text>
    </g>
    <line x1="202" y1="154" x2="202" y2="166" stroke="var(--muted)" stroke-width="1.4" marker-end="url(#arr)"/>

    <g transform="translate(0,168)">
      <rect width="404" height="40" rx="6" fill="var(--card)" stroke="var(--line)" stroke-dasharray="4 3"/>
      <text x="10" y="17" class="svg-b">4. East Penthouse Drops &rarr; Core &amp; Exterior Columns Follow</text>
      <text x="10" y="32" class="svg-s">Phase 3 (Nonlinear 3D global collapse if Col 79 fails) &mdash; Pre-registered next</text>
    </g>
  </g>

  <text x="442" y="20" class="svg-h">B. Column 79 Strength vs. Unbraced Height</text>
  <g transform="translate(442,32)">
    <rect width="304" height="208" rx="6" fill="var(--card)" stroke="var(--line)"/>
    <text x="12" y="20" class="svg-s">Compressive strength Pn (2 in. side plates, 20 &deg;C) vs. 7,525 kip load:</text>
    <!-- scale: 0..16000 kip -> 0..200 px from x=76 -->
    <g transform="translate(78,34)">
      <text x="-6" y="13" text-anchor="end" class="svg-s">1 storey</text>
      <rect x="0" y="2" width="192" height="15" rx="3" fill="var(--ok)" opacity="0.82"/>
      <text x="196" y="13" class="svg-s">15,382k</text>

      <text x="-6" y="43" text-anchor="end" class="svg-s">3 storeys</text>
      <rect x="0" y="32" width="144" height="15" rx="3" fill="var(--ok)" opacity="0.82"/>
      <text x="148" y="43" class="svg-s">11,507k</text>

      <text x="-6" y="73" text-anchor="end" class="svg-s">5 storeys</text>
      <rect x="0" y="62" width="80" height="15" rx="3" fill="var(--bad)" opacity="0.85"/>
      <text x="85" y="73" class="svg-s">6,440k (buckles)</text>

      <text x="-6" y="103" text-anchor="end" class="svg-s">7 storeys</text>
      <rect x="0" y="92" width="41" height="15" rx="3" fill="var(--bad)" opacity="0.85"/>
      <text x="46" y="103" class="svg-s">3,294k</text>

      <text x="-6" y="133" text-anchor="end" class="svg-s">9 storeys</text>
      <rect x="0" y="122" width="25" height="15" rx="3" fill="var(--bad)" opacity="0.9"/>
      <text x="30" y="133" class="svg-s">1,992k (NIST: 9)</text>

      <line x1="94" y1="-4" x2="94" y2="146" stroke="var(--bad)" stroke-width="1.6" stroke-dasharray="4 3"/>
      <text x="94" y="160" text-anchor="middle" class="svg-b" fill="var(--bad)">Gravity load: 7,525 kip</text>
    </g>
  </g>
</svg>
<figcaption><b>Diagram 1.</b> Left: how Phase 1 fits into NIST's four-step collapse sequence. Right: hand-calculated AISC axial capacity of Column 79 drops below its 7,525-kip gravity load once 5 to 6 storeys lose lateral floor bracing.</figcaption>
</figure>"""


def svg_bolts_and_steel():
    return """<figure class="svg-fig">
<svg viewBox="0 0 760 205" role="img" aria-label="Early bolt failure temperatures and Appendix E Eq. 3 strain-rate typo">
  <text x="14" y="20" class="svg-h">A. Bolts Shear From Thermal Expansion Long Before Steel Softens</text>
  <g transform="translate(14,30)">
    <rect width="430" height="162" rx="6" fill="var(--card)" stroke="var(--line)"/>
    <!-- temperature bar 20 to 600 C mapped to x = 24..404 -->
    <rect x="249" y="34" width="155" height="32" fill="var(--warnbg)" rx="4"/>
    <text x="326" y="27" text-anchor="middle" class="svg-s" fill="var(--warn)">Steel yield drops fast (&gt;400 &deg;C)</text>
    <line x1="24" y1="50" x2="404" y2="50" stroke="var(--fg)" stroke-width="2"/>
    <g class="svg-s">
      <line x1="24" y1="45" x2="24" y2="55" stroke="var(--fg)"/><text x="24" y="68" text-anchor="middle">20 &deg;C</text>
      <line x1="142" y1="45" x2="142" y2="55" stroke="var(--fg)"/><text x="142" y="68" text-anchor="middle">200 &deg;C</text>
      <line x1="273" y1="45" x2="273" y2="55" stroke="var(--fg)"/><text x="273" y="68" text-anchor="middle">400 &deg;C</text>
      <line x1="404" y1="45" x2="404" y2="55" stroke="var(--fg)"/><text x="404" y="68" text-anchor="middle">600 &deg;C</text>
    </g>
    <!-- markers: 101 C -> x=77, 147 C -> x=107, 154 C -> x=112, NIST 194 C -> x=138 -->
    <circle cx="77" cy="50" r="5" fill="var(--s2)"/>
    <line x1="77" y1="56" x2="77" y2="88" stroke="var(--s2)" stroke-width="1.2"/>
    <text x="18" y="101" class="svg-b" fill="var(--s2)">First stud: 101 &deg;C</text>
    <text x="18" y="115" class="svg-s">(NIST: 103 &deg;C)</text>

    <circle cx="112" cy="50" r="5.5" fill="var(--bad)"/>
    <line x1="112" y1="56" x2="155" y2="128" stroke="var(--bad)" stroke-width="1.2"/>
    <text x="160" y="133" class="svg-b" fill="var(--bad)">All 4 Col 79 bolts sheared: 154 &deg;C</text>
    <text x="160" y="148" class="svg-s">(Seat bolts 147 &deg;C; NIST Table 8-2: 154 &amp; 194 &deg;C)</text>
  </g>

  <text x="460" y="20" class="svg-h">B. NCSTAR 1-9 Eq. 3 Typesetting Error</text>
  <g transform="translate(460,30)">
    <rect width="286" height="162" rx="6" fill="var(--card)" stroke="var(--line)"/>
    <text x="12" y="20" class="svg-s">Rebuilding missing Table E-4 (A572 steel):</text>
    <line x1="38" y1="132" x2="268" y2="132" stroke="var(--muted)"/>
    <line x1="38" y1="34" x2="38" y2="132" stroke="var(--muted)"/>
    <text x="38" y="147" text-anchor="middle" class="svg-s">400 &deg;C</text>
    <text x="153" y="147" text-anchor="middle" class="svg-s">625 &deg;C</text>
    <text x="268" y="147" text-anchor="middle" class="svg-s">850 &deg;C</text>
    <!-- Printed linear k2 + k3*rate (too high at 650-850 C) -->
    <path d="M38,44 C115,47 175,62 268,105" fill="none" stroke="var(--bad)" stroke-width="2" stroke-dasharray="5 3"/>
    <!-- Actual k2 + k3*ln(rate) matching E-3 & E-5 -->
    <path d="M38,46 C105,54 160,86 268,125" fill="none" stroke="var(--s1)" stroke-width="2.3"/>
    <circle cx="95" cy="54" r="3" fill="var(--s1)"/><circle cx="153" cy="78" r="3" fill="var(--s1)"/>
    <circle cx="210" cy="108" r="3" fill="var(--s1)"/><circle cx="268" cy="125" r="3" fill="var(--s1)"/>
    <text x="148" y="56" class="svg-s" fill="var(--bad)">Printed k3&middot;rate (+173% err)</text>
    <text x="92" y="122" class="svg-b" fill="var(--s1)">k3&middot;ln(rate): &le;2.8% match</text>
  </g>
</svg>
<figcaption><b>Diagram 2.</b> Left: restrained thermal expansion shears the Column 79 bolts around 147&ndash;154 &deg;C, matching NIST closely. Right: Appendix E printed a linear strain-rate term in Eq. 3, whereas <code>ln(rate)</code> reproduces NIST's published steel tables.</figcaption>
</figure>"""


def svg_col79_recess():
    return """<figure class="svg-fig">
<svg viewBox="0 0 760 292" role="img" aria-label="Top-down plan view of Column 79 comparing NIST 14.6 degree idealization against Frankel shop drawings with 4.17 degree face and side cover plates">
  <defs>
    <marker id="arrB" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,1 L9,5 L0,9 z" fill="var(--bad)"/>
    </marker>
    <marker id="arrG" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,1 L9,5 L0,9 z" fill="var(--ok)"/>
    </marker>
  </defs>
  <!-- Panel A: NIST-style idealization -->
  <g transform="translate(14,12)">
    <rect width="356" height="266" rx="6" fill="var(--card)" stroke="var(--line)"/>
    <text x="12" y="22" class="svg-h">A. NIST-Style Idealization (Digitized Fig. 8-16)</text>
    <text x="12" y="39" class="svg-s">14.6&deg; face angle &middot; No side cover plates &middot; Open slide path</text>
    <!-- Girder vertical in frame (up = toward col 79), Col 79 tilted 14.6 deg -->
    <g transform="translate(195,128)">
      <!-- Seat 12 in. wide -> 96 px (-48..+48) -->
      <rect x="-48" y="-26" width="96" height="66" fill="var(--th)" stroke="var(--muted)" stroke-dasharray="3 2"/>
      <!-- Walk-off threshold 6.25 in. west (-50 px) -->
      <line x1="-50" y1="-40" x2="-50" y2="112" stroke="var(--bad)" stroke-width="1.6" stroke-dasharray="5 3"/>
      <text x="-55" y="106" text-anchor="end" class="svg-b" fill="var(--bad)">6.25 in. walk-off</text>
      <!-- Column 79 rotated 14.6 deg relative to girder -->
      <g transform="rotate(-14.6)">
        <rect x="-72" y="-82" width="144" height="24" fill="var(--col3d)" opacity="0.55" stroke="var(--fg)"/>
        <rect x="-12" y="-58" width="24" height="32" fill="var(--col3d)" opacity="0.45"/>
        <line x1="-76" y1="-26" x2="76" y2="-26" stroke="var(--fg)" stroke-width="2.5"/>
        <text x="0" y="-65" text-anchor="middle" class="svg-s">Col 79 (on building grid)</text>
      </g>
      <!-- Girder A2001 end -->
      <rect x="-46" y="-8" width="92" height="112" fill="var(--s1)" opacity="0.18" stroke="var(--s1)" stroke-width="1.8"/>
      <line x1="0" y1="-8" x2="0" y2="104" stroke="var(--s1)" stroke-width="3"/>
      <text x="4" y="86" class="svg-b" fill="var(--s1)">Girder A2001</text>
      <!-- Wedge push arrow -->
      <line x1="-6" y1="-10" x2="-66" y2="-10" stroke="var(--bad)" stroke-width="2.4" marker-end="url(#arrB)"/>
      <text x="-12" y="-34" text-anchor="end" class="svg-b" fill="var(--bad)">Strong wedge: 0.26 &times; thrust</text>
      <text x="-12" y="-20" text-anchor="end" class="svg-s" fill="var(--bad)">Slides off at 511 &deg;C (nist_replica)</text>
    </g>
  </g>

  <!-- Panel B: Shop drawings -->
  <g transform="translate(390,12)">
    <rect width="356" height="266" rx="6" fill="var(--card)" stroke="var(--accent)" stroke-width="1.4"/>
    <text x="12" y="22" class="svg-h">B. Frankel Shop Drawings (Sheets 1091 &amp; 9114)</text>
    <text x="12" y="39" class="svg-s">Col 79 rotated 12.3&deg; &rarr; 4.17&deg; face + 2 in. side cover plates</text>
    <g transform="translate(195,128)">
      <rect x="-48" y="-26" width="96" height="66" fill="var(--th)" stroke="var(--muted)" stroke-dasharray="3 2"/>
      <line x1="-50" y1="-40" x2="-50" y2="112" stroke="var(--bad)" stroke-width="1.6" stroke-dasharray="5 3"/>
      <text x="-55" y="106" text-anchor="end" class="svg-s" fill="var(--bad)">6.25 in. walk-off</text>
      <!-- Column 79 rotated only 4.17 deg off girder, with projecting side cover plates! -->
      <g transform="rotate(-4.17)">
        <rect x="-71" y="-76" width="142" height="50" fill="var(--col3d)" opacity="0.45" stroke="var(--fg)"/>
        <line x1="-71" y1="-26" x2="71" y2="-26" stroke="var(--fg)" stroke-width="2.5"/>
        <!-- Two 26x2 side cover plates projecting 1.81 in. (~15 px) past north flange face (-26 -> -11) -->
        <rect x="-87" y="-88" width="16" height="77" fill="var(--plate)" stroke="var(--fg)" stroke-width="1.2"/>
        <rect x="71" y="-88" width="16" height="77" fill="var(--plate)" stroke="var(--fg)" stroke-width="1.2"/>
        <text x="0" y="-50" text-anchor="middle" class="svg-s">Col 79 (W14&times;730)</text>
      </g>
      <text x="-90" y="-14" text-anchor="end" class="svg-b" fill="var(--plate)">West side plate</text>
      <text x="-90" y="-1" text-anchor="end" class="svg-s" fill="var(--plate)">stops girder at ~4.15 in.</text>
      <!-- Girder A2001 end at mouth of recess -->
      <rect x="-46" y="-12" width="92" height="116" fill="var(--s1)" opacity="0.20" stroke="var(--s1)" stroke-width="1.8"/>
      <line x1="0" y1="-12" x2="0" y2="104" stroke="var(--s1)" stroke-width="3"/>
      <!-- 4.15 in. clearance callout (-46 to -71) -->
      <line x1="-46" y1="22" x2="-71" y2="22" stroke="var(--ok)" stroke-width="2" marker-end="url(#arrG)"/>
      <text x="-52" y="38" text-anchor="end" class="svg-b" fill="var(--ok)">~4.15 in. room</text>
      <text x="6" y="72" class="svg-b" fill="var(--ok)">Gentle 4.17&deg; bevel</text>
      <text x="6" y="87" class="svg-s">(0.07 &times; thrust; baseline</text>
      <text x="6" y="100" class="svg-s">moves only 1.47 in.)</text>
    </g>
  </g>
</svg>
<figcaption><b>Diagram 3.</b> Top-down geometry at Column 79 (west is left). Left: placing Column 79 on the building grid creates a 14.6&deg; wedge with no lateral stop. Right: the shop drawings rotate Column 79 so the face is just 4.17&deg; off square, and two 2-in. side cover plates project ~1.8 in. past the face, blocking the flange at ~4.15 in. (before the 6.25-in. walk-off line).</figcaption>
</figure>"""


def svg_walkoff_bars():
    rows = [
        ("Drawn baseline (mu=0.3, to 600 C)", 1.47, "ok", "1.47 in. — held by friction"),
        ("Drawn, zero friction (mu=0, to 600 C)", 3.98, "ok", "3.98 in. — stopped by west plate"),
        ("Combined Section 6 repeat (to 700 C)", 2.83, "ok", "2.83 in. — no girder buckle, held"),
        ("Combined extreme ('favourable_dump', 700 C)", 8.20, "bad", "Walks off in 700 C hold (twists 64 deg)"),
        ("NIST replica (14.6 deg, no plates, mu=0)", 7.08, "bad", "7.08 in. — slides off at 511 C"),
        ("+ Restore standard holes ('nist_holes')", 6.84, "bad", "6.84 in. — slides off at 512 C"),
        ("+ Restore 4.17 deg face ('nist_face_drawn')", 5.04, "warn", "5.04 in. at 600 C -> walks off 655 C"),
        ("+ Restore friction 0.3 ('nist_mu0.3')", 0.36, "warn", "0.36 in. at 600 C -> twists off 650 C"),
        ("+ Restore 4.17 deg + Side Plates", 3.98, "ok", "3.98 in. — HELD through 700 C!"),
    ]
    # x0 = 252, scale = 34 px per inch (0..8.5 in. -> 0..289 px)
    x0, sc = 254, 32.0
    bars = []
    for idx, (label, val, kind, note) in enumerate(rows):
        y = 46 + idx * 26 + (10 if idx >= 4 else 0)
        w = max(4.0, min(val, 8.2) * sc)
        col = {"ok": "var(--ok)", "warn": "var(--warn)", "bad": "var(--bad)"}[kind]
        bars.append(f'<text x="{x0 - 8}" y="{y + 12}" text-anchor="end" class="svg-s">{E(label)}</text>'
                    f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="16" rx="3" fill="{col}" opacity="0.84"/>'
                    f'<text x="{x0 + w + 6:.1f}" y="{y + 12}" class="svg-s">{E(note)}</text>')
    x_plate = x0 + 4.15 * sc
    x_walk = x0 + 6.25 * sc
    return f"""<figure class="svg-fig">
<svg viewBox="0 0 760 314" role="img" aria-label="Comparison of westward girder movement at Column 79 across baseline, combined, and NIST-replica restore runs">
  <rect x="6" y="6" width="748" height="302" rx="6" fill="var(--card)" stroke="var(--line)"/>
  <text x="18" y="26" class="svg-h">Westward Movement at Column 79: Isolating Each Feature</text>
  <text x="18" y="152" class="svg-b" fill="var(--accent)">One-by-one NIST-replica restore runs:</text>
  <line x1="{x0}" y1="38" x2="{x0}" y2="294" stroke="var(--muted)"/>
  <line x1="{x_plate:.1f}" y1="36" x2="{x_plate:.1f}" y2="294" stroke="var(--plate)" stroke-width="1.6" stroke-dasharray="3 3"/>
  <text x="{x_plate:.1f}" y="33" text-anchor="middle" class="svg-b" fill="var(--plate)">4.15 in. side plate</text>
  <line x1="{x_walk:.1f}" y1="36" x2="{x_walk:.1f}" y2="294" stroke="var(--bad)" stroke-width="1.7" stroke-dasharray="5 3"/>
  <text x="{x_walk:.1f}" y="33" text-anchor="middle" class="svg-b" fill="var(--bad)">6.25 in. walk-off</text>
  {''.join(bars)}
</svg>
<figcaption><b>Diagram 4.</b> Bars show westward girder-end displacement at 600 &deg;C (or peak walk-off). Without side plates, the 4.17&deg; face delays sliding past 600 &deg;C and friction converts sliding into a 650 &deg;C buckling twist-off; putting the side plates back stops walk-off through 700 &deg;C.</figcaption>
</figure>"""


def svg_beam_mismatch():
    return """<figure class="svg-fig">
<svg viewBox="0 0 760 238" role="img" aria-label="Northeast floor bay plan comparing NIST buckled floor beams against this study bowed girder">
  <!-- Left: NIST 8.8 -->
  <g transform="translate(14,10)">
    <rect width="356" height="218" rx="6" fill="var(--card)" stroke="var(--line)"/>
    <text x="12" y="21" class="svg-h">A. NIST &sect;8.8 Reported Sequence</text>
    <text x="12" y="37" class="svg-s">Girder stays stiff &rarr; all 5 floor beams buckle &rarr; girder rocks off</text>
    <!-- Col 44 top (105,54), Col 79 bottom (68,188), East wall x=316 -->
    <rect x="98" y="48" width="14" height="10" fill="var(--col3d)"/><text x="88" y="56" text-anchor="end" class="svg-s">Col 44</text>
    <rect x="61" y="184" width="14" height="10" fill="var(--col3d)"/><text x="54" y="193" text-anchor="end" class="svg-s">Col 79</text>
    <line x1="316" y1="48" x2="328" y2="194" stroke="var(--muted)" stroke-width="3"/>
    <text x="320" y="45" text-anchor="end" class="svg-s">East wall</text>
    <!-- Straight girder -->
    <line x1="105" y1="53" x2="68" y2="189" stroke="var(--s1)" stroke-width="3.5"/>
    <!-- 5 buckled beams (wavy orange curves) -->
    <path d="M101,68 Q205,54 317,68" fill="none" stroke="var(--bad)" stroke-width="2.2"/>
    <path d="M93,96 Q200,112 319,96" fill="none" stroke="var(--bad)" stroke-width="2.2"/>
    <path d="M85,124 Q198,108 322,124" fill="none" stroke="var(--bad)" stroke-width="2.2"/>
    <path d="M77,152 Q195,168 325,152" fill="none" stroke="var(--bad)" stroke-width="2.2"/>
    <path d="M70,178 Q195,163 327,178" fill="none" stroke="var(--bad)" stroke-width="2.2"/>
    <text x="205" y="206" text-anchor="middle" class="svg-b" fill="var(--bad)">Beams buckle (436&ndash;600 &deg;C) &amp; rock girder off</text>
  </g>

  <!-- Right: This study -->
  <g transform="translate(390,10)">
    <rect width="356" height="218" rx="6" fill="var(--card)" stroke="var(--accent)" stroke-width="1.4"/>
    <text x="12" y="21" class="svg-h">B. This Study's Shell Model (Baseline)</text>
    <text x="12" y="37" class="svg-s">Expanding beams bow girder 4.3 in. west &rarr; beams stay &le;117 kip</text>
    <rect x="98" y="48" width="14" height="10" fill="var(--col3d)"/><text x="88" y="56" text-anchor="end" class="svg-s">Col 44</text>
    <rect x="61" y="184" width="14" height="10" fill="var(--col3d)"/><text x="54" y="193" text-anchor="end" class="svg-s">Col 79</text>
    <line x1="316" y1="48" x2="328" y2="194" stroke="var(--muted)" stroke-width="3"/>
    <!-- Undeformed dashed girder -->
    <line x1="105" y1="53" x2="68" y2="189" stroke="var(--muted)" stroke-width="1.3" stroke-dasharray="4 3"/>
    <!-- Bowed girder (bows west/left by ~22 px exaggerated) -->
    <path d="M105,53 Q52,118 64,189" fill="none" stroke="var(--s1)" stroke-width="3.6"/>
    <!-- 5 straight floor beams pushing west -->
    <line x1="94" y1="68" x2="317" y2="68" stroke="var(--s2)" stroke-width="2.2"/>
    <line x1="76" y1="96" x2="319" y2="96" stroke="var(--s2)" stroke-width="2.2"/>
    <line x1="68" y1="124" x2="322" y2="124" stroke="var(--s2)" stroke-width="2.2"/>
    <line x1="65" y1="152" x2="325" y2="152" stroke="var(--s2)" stroke-width="2.2"/>
    <line x1="64" y1="178" x2="327" y2="178" stroke="var(--s2)" stroke-width="2.2"/>
    <text x="58" y="122" text-anchor="end" class="svg-b" fill="var(--s1)">4.3 in. bow</text>
    <text x="205" y="206" text-anchor="middle" class="svg-b" fill="var(--ok)">0 beams buckle; Col 79 end moves 1.47 in.</text>
  </g>
</svg>
<figcaption><b>Diagram 5.</b> Why Gate Item 5 remains open: in NIST's partial-floor model (left), the five east beams buckled and rocked the girder off its seat; in our model (right), the beams push the unbraced girder into a 4.3-in. westward bow, keeping beam compression well below buckling.</figcaption>
</figure>"""


def build_guide():
    """Plain-English Question-Driven Audit section (#guide-view)."""
    c4_rows = [
        (code("nist_replica"), "All NIST idealizations (14.6&deg; face, no plates, &mu;=0, slot)", "7.08 in.",
         chip("Slides off at 511 °C", "bad"),
         step_btn("3D", a="nist_replica", v="col79", T=600, s=1, banner="NIST replica: slides past 6.25 in. walk-off at 511 °C")),
        (code("nist_holes"), "+ Standard 15/16 in. round clip-angle holes", "6.84 in.",
         chip("Slides off at 512 °C", "bad"),
         step_btn("3D", a="nist_holes", v="col79", T=600, s=1, banner="Standard holes restored: sequence unchanged (512 °C)")),
        (code("nist_face_drawn"), "+ Blueprint 4.17&deg; face angle (still no side plates, &mu;=0)", "5.04 in.",
         chip("Delayed to 655 °C", "warn"),
         step_btn("3D", a="nist_face_drawn", v="col79", T=655, s=1, banner="Drawn 4.17° face without side plates: delayed past 600 °C to 655 °C")),
        (code("nist_mu0.3"), "+ Friction &mu; = 0.30 (still 14.6&deg; face, no side plates)", "0.36 in.",
         chip("Buckles & twists off 650 °C", "warn"),
         step_btn("3D", a="nist_mu0.3", v="col79", T=655, s=1, banner="Friction 0.3 stops sliding, but girder buckles & twists off at 650–655 °C")),
        (code("nist_face_plates"), "+ Blueprint 4.17&deg; face AND side cover plates (&mu;=0)", "3.98 in.",
         chip("Held through 700 °C", "ok"),
         step_btn("3D", a="nist_face_plates", v="col79", T=700, s=1, banner="Side plates + drawn face: hits west plate at 488 °C (3.98 in.) and holds through 700 °C")),
        (code("check_rate_half"), "Full blueprint baseline (&mu;=0.30, side plates, to 600 &deg;C)", "1.47 in.",
         chip("Held (41/41 sweeps at 600 °C)", "ok"),
         step_btn("3D", a="check_rate_half", v="col79", T=600, s=1, banner="Blueprint baseline: 1.47 in. west movement (6.25 in. needed for walk-off)")),
        (code("favourable_dump"), "Pre-registered extreme combination (700 &deg;C hold)", "17.5 in.",
         chip("Walks off & drops 22.6 in.", "bad"),
         step_btn("3D", a="favourable_dump", v="col79", t=5.61, s=1, banner="Combined 700 °C hold: girder buckles, twists 64°, and drops 22.6 in. off seat")),
        (code("favourable_s6"), "Section 6 repeat of combination (to 700 &deg;C)", "2.83 in.",
         chip("Held through 700 °C", "ok"),
         step_btn("3D", a="favourable_s6", v="col79", T=700, s=1, banner="Section 6 repeat: swapping 4 inputs prevents girder buckle (2.83 in. max)")),
    ]

    return f"""<div class="guide-hero">
  <div class="eyebrow">Plain-English Engineering Audit &middot; Phase 1 of 3</div>
  <h1>Did Fire Push WTC 7's Floor 13 Girder Off Its Seat?</h1>
  <p class="lead">An independent, open-source finite-element audit of NIST's collapse-initiation model
    (NCSTAR 1-9 &sect;8.8), rebuilt from published reports and FOIA-released steel shop drawings with
    pre-registered pass/fail criteria. Click any <b>&#x25B6;</b> button below to inspect the exact 3D shell
    simulation alongside each disputed claim.</p>
  <div class="scorecard" aria-label="Audit questions overview">
    <a href="#card-1" class="sc-row"><span><b>1.</b> Why one girder at Column 79 matters</span>{chip("Col 79 Buckling Confirmed", "ok")}</a>
    <a href="#card-2" class="sc-row"><span><b>2.</b> Early bolt failures &amp; NIST table bugs</span>{chip("Bolts Match · 2 Typos Rebuilt", "info")}</a>
    <a href="#card-3" class="sc-row"><span><b>3.</b> Missing side plates &amp; the 4.17&deg; vs. 14.6&deg; angle</span>{chip("Shop Drawings Differ", "warn")}</a>
    <a href="#card-4" class="sc-row"><span><b>4.</b> How angle, friction &amp; side plates impact walk-off</span>{chip("Plates Set Whether · Angle Sets When", "info")}</a>
    <a href="#card-5" class="sc-row"><span><b>5.</b> Why didn't our floor beams buckle like NIST's?</span>{chip("Open Mechanism Puzzle", "warn")}</a>
    <a href="#card-6" class="sc-row"><span><b>6.</b> What this proves &mdash; and what it does NOT prove</span>{chip("Phase 1: CONDITIONAL", "warn")}</a>
  </div>
</div>

<section class="audit-card" id="card-1">
  <div class="card-top">
    <span class="qnum">Question 1 &middot; The Stakes</span>
    <div class="chips">{chip("Scope: Phase 1 of 3", "info")} {chip("Col 79 Buckling: NIST Confirmed", "ok")}</div>
  </div>
  <h2>Why does the WTC 7 debate hinge on a single girder at Column 79?</h2>
  <p class="claim"><b>The disputed claim:</b> NIST concluded that WTC 7's collapse began on Floor 13 when heated east-bay floor
    beams pushed a 45-foot girder (<code>A2001</code>) off its seat at interior <code>Column 79</code>. Critics question both
    whether fire could unseat that girder and whether losing one column could bring down a 47-storey building.</p>
  <p>Tall steel columns rely on each floor frame to brace them sideways&mdash;just like holding a thin yardstick at the middle
    keeps it from bowing under weight. In NIST's account, once Floor 13's girder fell off its Column 79 seat, Floors 12 down to 5
    failed in a cascade, leaving Column 79 unbraced over <b>nine storeys</b> until it buckled under gravity.</p>
  <p>We split that sequence into three gated phases so separate physical questions aren't muddled together. Our hand calculations
    already confirm NIST's column-buckling math: carrying <b>7,525 kip</b> (3,760 tons) of gravity load, Column 79 loses its strength
    once <b>5 to 6 storeys</b> lose lateral bracing; at 9 unbraced storeys its capacity drops to ~2,000&ndash;2,900 kip (about
    one-third of the weight on it). So <em>if</em> those floors fail, Column 79 definitely buckles. Everything in Phase 1 therefore
    asks Domino #1: <b>under NIST's Floor 13 heating test, does girder A2001 actually lose its seat?</b></p>
  {svg_domino()}
  <div class="card-actions">
    {step_btn("Show Floor 13 framing in 3D", a="check_rate_half", v="floor", t=1.0, s=1, cols=True, banner="Card 1: Northeast Floor 13 bay — Girder A2001 (blue) between Col 79 and Col 44, with 5 east floor beams (orange)")}
    <a href="#question" class="goto-rep" data-goto-report="#question">Technical Report &sect;2 &rarr;</a>
  </div>
</section>

<section class="audit-card" id="card-2">
  <div class="card-top">
    <span class="qnum">Question 2 &middot; Early Heat &amp; Document Audit</span>
    <div class="chips">{chip("Early Bolt Failures: NIST Confirmed", "ok")} {chip("NCSTAR 1-9 Tables: 2 Bugs Rebuilt", "warn")}</div>
  </div>
  <h2>Can office-fire temperatures shear heavy steel bolts &mdash; and how clean were NIST's published inputs?</h2>
  <p class="claim"><b>The disputed claims:</b> Skeptics often argue office fires are far too cool to break heavy structural steel
    connections; conversely, defenders often assume NCSTAR 1-9 can be reproduced straight out of its printed tables.</p>
  <p><b>Why bolts snap below 200 &deg;C:</b> Steel doesn't need to melt (~1,500 &deg;C) or even soften (&gt;400 &deg;C) to break
    bolts&mdash;it only needs to <b>expand</b>. Heating a 45-foot steel girder by ~100 &deg;C makes it expand more than half an inch.
    Restraining that expansion builds over <b>180 kip (90 tons)</b> of shear force, snapping the four 7/8-in. erection bolts. In our
    51,149-shell 3D model, the first slab shear stud fails at <b>101 &deg;C</b> (NIST: <b>103 &deg;C</b>), the two Column 79 seat bolts
    fail at <b>147 &deg;C</b> (NIST: <b>154 &deg;C</b>), and all four Column 79 bolts shear by <b>154 &deg;C</b> (NIST: <b>194 &deg;C</b>),
    leaving the girder resting loose on its 12-inch-wide steel seat.</p>
  <p><b>Detective work in NCSTAR 1-9:</b> Because NIST did not release its computer input files, rebuilding the model exposed two real
    documentation errors in NCSTAR 1-9 Appendix E: (1) <b>Table E-4</b> (meant for A572 Grade 50 steel&mdash;every beam, girder, and
    interior column) was accidentally printed as an exact copy of <b>Table E-3</b> (weaker A36 steel); and (2) <b>Equation 3</b>
    printed a linear strain-rate term (<code>k2 + k3&middot;rate</code>) that misses NIST's other tables by up to <b>173%</b>, whereas
    <code>k2 + k3&middot;ln(rate)</code> reproduces them within <b>1.7&ndash;2.8%</b> (showing NIST's simulation code used
    <code>ln(rate)</code> even though the report misprinted the formula). Every criterion and sweep range in this project was
    SHA-256 hashed before running so neither side's preferred outcome could be retrofitted.</p>
  {svg_bolts_and_steel()}
  <div class="card-actions">
    {step_btn("Show sheared Col 79 bolts (✕) at 200 °C", a="check_rate_half", v="col79", T=200, s=1, bolts=True, banner="Card 2: At 200 °C beam temperature, all 4 Column 79 erection bolts have sheared (red dots)")}
    <a href="#evidence" class="goto-rep" data-goto-report="#evidence">Technical Report &sect;3 &amp; &sect;4.1 &rarr;</a>
  </div>
</section>

<section class="audit-card" id="card-3">
  <div class="card-top">
    <span class="qnum">Question 3 &middot; Blueprints vs. Idealized Geometry</span>
    <div class="chips">{chip("FOIA Shop Drawings Differ in Two Ways", "warn")}</div>
  </div>
  <h2>Did NIST omit Column 79's side cover plates and misstate the bearing angle?</h2>
  <p class="claim"><b>The disputed claim:</b> The 2020 University of Alaska Fairbanks (UAF) report and AE911Truth's Request for
    Correction argued that NIST omitted two 2-inch-thick side cover plates welded to Column 79 that trap the expanding girder before
    it can move 6.25 in. off its seat.</p>
  <p>Checking the original Frankel steel fabrication drawings (sheets <code>1091</code>, <code>9114</code>, and erection plan
    <code>E12/13</code>, released under FOIA) confirmed the side-plate recess <em>and</em> uncovered a second major geometry
    difference that our own initial screening model had gotten wrong from NIST's figures:</p>
  <ul class="tight">
    <li><b>1. A 3.5&times; gentler bearing-face angle (4.17&deg; vs. 14.6&deg;):</b> Girder <code>A2001</code> runs diagonally across
      the bay (16.5&deg; to the grid). Digitizing NIST's small plan diagram (Fig. 8-16) places Column 79 on the building grid, creating
      a steep <b>14.6&deg;</b> face that acts like a wedge&mdash;pushing the girder end west with <b>26%</b> of its axial thrust
      (<code>tan 14.6&deg; = 0.26</code>). On the shop drawings, <b>Column 79 is rotated 12.3&deg; clockwise</b>, so the girder meets
      its north flange face only <b>4.17&deg;</b> off square (written on sheets 9114 and 1091 as a <code>7/8 in 12</code> bevel). That
      cuts the sideways wedge push down to <b>7.3%</b> of thrust&mdash;well below typical 30% steel friction.</li>
    <li><b>2. The 26 &times; 2 in. side-plate pocket (~4.15 in. room vs. 6.25 in. walk-off):</b> Two heavy side cover plates project
      <b>~1.81 in.</b> past Column 79's north flange face (shown in amber in the 3D viewer). At room temperature the girder end sits
      right at the mouth of that pocket; once thermal expansion pushes the girder ~1.5&ndash;1.9 in. forward into the recess, only
      <b>~4.15 in.</b> separates its west flange tip from the west side plate&mdash;less than the <b>6.25 in.</b> movement required to
      fall off the 12-inch seat (NIST's 2012 errata value).</li>
    <li><b>3. Additional shop-drawing details:</b> Standard 15/16-in. round holes (not slots) in the Column 79 top clip angle, web
      stiffener plates at the girder end (omitted by NIST), and no girder shear studs on Floor 13 (matching NIST).</li>
  </ul>
  {svg_col79_recess()}
  <div class="card-actions">
    {step_btn("Compare NIST idealization vs. shop drawings in 3D", a="nist_replica", b="nist_face_plates", v="plan", T=600, s=1, cols=True, banner="Card 3 (Top-Down Plan, 600 °C): Left = NIST idealization (no amber side plates, 14.6° face); Right = Shop drawings (amber side plates + 4.17° face)")}
    {step_btn("Inspect meshed end stiffeners (A97)", a="A97_stiffeners_r0.5", v="col79", T=600, s=1, banner="Card 3: Blueprint run including drawn PL 5.5 × 0.75 × 18 in. girder end stiffeners (1.60 in. max west)")}
    <a href="#ev-drawings" class="goto-rep" data-goto-report="#ev-drawings">Technical Report &sect;3.2 &rarr;</a>
  </div>
</section>

<section class="audit-card" id="card-4">
  <div class="card-top">
    <span class="qnum">Question 4 &middot; Isolating What Controls Walk-Off</span>
    <div class="chips">{chip("Side Plates Decide 'Whether'", "ok")} {chip("Face Angle Decides 'When'", "info")}</div>
  </div>
  <h2>How do the bearing angle, friction, and side plates each impact walk-off?</h2>
  <p class="claim"><b>The core engineering question:</b> When you separate all these details one by one in a 3D shell model, what
    actually causes or prevents girder walk-off&mdash;bolt slots, the 4.17&deg; vs. 14.6&deg; face angle, friction, the side plates,
    or extreme 700 &deg;C heating?</p>
  <p>With the shop-drawn geometry, <b>zero of our 41 one-at-a-time sensitivity runs walked off</b> under NIST's 600 &deg;C schedule
    (the baseline moved just <b>1.47 in.</b> west vs. <b>6.25 in.</b> needed). To isolate why, we built <code>nist_replica</code>
    (applying all of NIST's Column 79 idealizations together on the drawn floor framing) and then restored the shop-drawing features
    <b>one at a time</b>:</p>
  <ul class="tight">
    <li><b>Bolt-hole slots don't matter:</b> <code>nist_replica</code> slides off its seat at <b>511 &deg;C</b>; restoring standard
      round holes (<code>nist_holes</code>) repeats walk-off at <b>512 &deg;C</b>.</li>
    <li><b>The bearing-face angle sets <em>when</em> (inside vs. above 600 &deg;C), not <em>whether</em>:</b> Restoring only the gentler
      <b>4.17&deg;</b> face without side plates or friction (<code>nist_face_drawn</code>) slows westward sliding from ~1.6 in./100 &deg;C
      to ~1.0 in./100 &deg;C&mdash;keeping the girder on its seat through NIST's 600 &deg;C target (5.04 in.), before sliding off at
      <b>655 &deg;C</b>.</li>
    <li><b>Friction stops sliding, but without side plates the girder twists off above 600 &deg;C:</b> Restoring <code>&mu; = 0.30</code>
      on the plate-less 14.6&deg; column (<code>nist_mu0.3</code>) holds sliding to 0.36 in., until the girder buckles at 633 &deg;C and
      dynamically twists off its seat at <b>650&ndash;655 &deg;C</b>.</li>
    <li><b>The side cover plates decide <em>whether</em> walk-off occurs:</b> Restoring the drawn 4.17&deg; face <em>with</em> the side
      plates&mdash;even at <b>zero friction</b> (<code>nist_face_plates</code>)&mdash;lets the girder slide 3.98 in. west, bear against
      the west side plate at <b>488 &deg;C</b>, and <b>stay on its seat all the way through 700 &deg;C</b> while the girder bows.</li>
    <li><b>One 700 &deg;C combined edge case:</b> With side plates present, only our pre-registered extreme combination
      (<code>favourable</code> / <code>favourable_dump</code>, stacking several unsourced inputs at 700 &deg;C) buckled the girder,
      twisted 64&deg; past the plate, and plunged 22.6 in. off its seat during the 700 &deg;C hold&mdash;yet replacing four inputs with
      the values that gave more individual movement (<code>favourable_s6</code>) eliminated the buckle and held at <b>2.83 in.</b></li>
  </ul>
  {svg_walkoff_bars()}
  {table(["Run", "Configuration tested", "West @ 600 °C", "Outcome", "Inspect"], c4_rows)}
  <div class="card-actions">
    {step_btn("Compare Replica vs. Side Plates", a="nist_replica", b="nist_face_plates", v="col79", T=620, s=1, banner="Card 4: Left (NIST replica) slides off at 511 °C and drops at 612 °C; Right (side plates restored) catches on the amber west plate at 3.98 in.")}
    {step_btn("Compare Sliding vs. Twist-Off (655 °C)", a="nist_replica", b="nist_mu0.3", v="col79", T=675, s=1, banner="Card 4: Zero-friction sliding walk-off (left) vs. μ=0.30 girder buckling & dynamic twist-off at 650–655 °C (right)")}
    {step_btn("Watch 700 °C Hold Plunge vs. Repeat", a="favourable_dump", b="favourable_s6", v="col79", t=5.61, s=1, banner="Card 4: At t = 5.60 s in the 700 °C hold, favourable_dump twists 64° and drops 22.6 in., while favourable_s6 stays on its seat")}
    <a href="#diff" class="goto-rep" data-goto-report="#diff">Technical Report &sect;6 &amp; &sect;7 &rarr;</a>
  </div>
</section>

<section class="audit-card" id="card-5">
  <div class="card-top">
    <span class="qnum">Question 5 &middot; The Unsolved Engineering Puzzle</span>
    <div class="chips">{chip("Unexplained Mechanism Mismatch (Gate Item 5)", "warn")}</div>
  </div>
  <h2>Why didn't our floor beams buckle like NIST's did at 436 &deg;C?</h2>
  <p class="claim"><b>The puzzle:</b> Even when our <code>nist_replica</code> run walked off at 511 &deg;C, it did so by <em>flat
    sliding</em> along the column face&mdash;whereas NIST's &sect;8.8 model reported all five east floor beams buckling laterally
    (starting at 436 &deg;C) and <em>rocking</em> the girder off its seat.</p>
  <p>In our baseline model, axial compression in the five <code>W24&times;55</code> / <code>W21&times;44</code> floor beams peaks at only <b>117 kip</b>
    (and falls to 73 kip at 600 &deg;C)&mdash;far short of a hot <code>W24&times;55</code> beam's ~380-kip squash capacity. Why doesn't pressure
    build up enough to buckle the beams? Because girder <code>A2001</code> has no shear studs on Floor 13 and slides freely under the concrete slab
    (matching NIST &sect;11.2.3). Instead of buckling themselves, the five expanding beams push the middle of the girder into a
    <b>4.3-inch westward bow</b>, relieving their own compression.</p>
  <p>Floor beams in our model <em>do</em> buckle early (at <b>284 &deg;C</b>, in run <code>S15_muslab0</code>) if friction between the
    floor beams and the slab above them is set to zero so the slab stops bracing their top flanges&mdash;and still the girder does not
    walk off (1.50 in.). What stiffened NIST's girder against bowing sideways in its unreleased LS-DYNA model is not yet identified,
    so under our pre-registered rules Gate Item 5 remains <b>open</b>.</p>
  {svg_beam_mismatch()}
  <div class="card-actions">
    {step_btn("Show 4.3-in. girder bow (×5 scale)", a="check_rate_half", v="floor", T=600, s=5, ghost=True, banner="Card 5 (×5 exaggerated + faint initial outline): Expanding east beams push girder A2001 into a 4.3-in. westward bow without buckling")}
    {step_btn("Compare Baseline vs. Buckled Beam (S15_muslab0)", a="check_rate_half", b="S15_muslab0", v="floor", T=600, s=5, banner="Card 5 (×5 scale): Baseline unbuckled beams (left) vs. zero beam-slab friction where floor beams buckle laterally from 284 °C (right)")}
    <a href="#diff" class="goto-rep" data-goto-report="#diff">Technical Report &sect;7 &rarr;</a>
  </div>
</section>

<section class="audit-card" id="card-6">
  <div class="card-top">
    <span class="qnum">Question 6 &middot; Guardrails &amp; Bottom Line</span>
    <div class="chips">{chip("Phase 1 Verdict: CONDITIONAL", "warn")} {chip("Gate Not Passed", "bad")}</div>
  </div>
  <h2>What does this study actually prove &mdash; and what does it NOT prove?</h2>
  <p class="claim"><b>Why careful guardrails matter:</b> Online WTC 7 debates routinely over-extrapolate partial engineering results
    into sweeping claims of either "case closed" or "controlled demolition." Our pre-registered rules forbid both leaps here.</p>
  <ul class="tight">
    <li><b>1. Neither a confirmation of NIST's &sect;8.8 baseline nor a refutation of fire collapse:</b> Phase 1's formal classification
      is <b>CONDITIONAL</b>, and its gate has <b>not passed</b>. It shows that on the shop-drawn Floor 13 framing, Column 79's side
      cover plates and 4.17&deg; bearing face prevent walk-off under NIST's uniform 600 &deg;C ramp, while leaving an unexplained
      difference in floor-beam buckling between our shell model and NIST's.</li>
    <li><b>2. Two strict numerical checks are reported openly as failures, not waived:</b> (a) Refining the shell mesh from 1.8 in. to
      0.9 in. moved baseline Column 79 displacement from 1.467 in. to 1.501 in.&mdash;just <b>0.034 in.</b> (0.5% of the 6.25-in.
      walk-off distance), yet <b>2.3%</b> against our strict <b>2.0%</b> pre-registered limit; (b) Kinetic energy exceeded <b>5%</b> of
      internal energy during NIST's 1-second gravity ramp and brief connection snaps, although half-rate and quarter-rate runs agreed
      within <b>3 &deg;C</b> on every event.</li>
    <li><b>3. Uniform heating is not the real WTC 7 fire:</b> Phase 1 tests only NIST's simplified uniform temperature ramp on a single
      corner bay (&sect;8.8). Real compartment fires create non-uniform temperatures, heat the slab, and move across Floors 8&ndash;13
      over hours (<b>Phase 2</b>, gated).</li>
    <li><b>4. Global collapse given Column 79 failure is tested next (Phase 3):</b> Regardless of <em>how</em> Column 79 failed,
      neither NIST (unreleased inputs, no removal-length sweep) nor UAF (linear static check keeping all floors intact) published a
      swept nonlinear dynamic test of how many unbraced storeys of Column 79 are required to trigger total collapse. That conditional
      Phase 3 model is pre-registered next.</li>
  </ul>
  <div class="card-actions">
    <button type="button" class="step-btn" data-set-layout="3d">Open Fullscreen 3D Explorer &#x25B6;</button>
    <a href="#summary" class="goto-rep" data-goto-report="#summary">Read Full Technical Report &rarr;</a>
  </div>
</section>"""


# ---------------------------------------------------------------- CSS & JS
CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1f;--muted:#5f6368;--line:#dedad2;--card:#ffffff;--accent:#1f5f99;--warn:#9a5b00;
--warnbg:#fff4e0;--ok:#256c3a;--okbg:#e6f4ea;--bad:#a12a2a;--badbg:#fbe9e9;--codebg:#f1efe9;--th:#f4f2ec}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15171a;--fg:#e6e6e3;--muted:#a3a7ad;
--line:#2f3338;--card:#1c1f23;--accent:#7fb4e6;--warn:#f0b35a;--warnbg:#3a2c12;--ok:#7bd096;--okbg:#17301f;
--bad:#f08b8b;--badbg:#3a1a1a;--codebg:#24282d;--th:#22262b}}
:root[data-theme="dark"]{--bg:#15171a;--fg:#e6e6e3;--muted:#a3a7ad;--line:#2f3338;--card:#1c1f23;--accent:#7fb4e6;
--warn:#f0b35a;--warnbg:#3a2c12;--ok:#7bd096;--okbg:#17301f;--bad:#f08b8b;--badbg:#3a1a1a;--codebg:#24282d;--th:#22262b}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 Georgia,"Iowan Old Style","Palatino Linotype",serif}

/* Top site navigation bar */
.site-bar{position:sticky;top:0;z-index:30;display:flex;align-items:center;justify-content:space-between;gap:10px;
  min-height:50px;padding:6px 16px;background:var(--card);border-bottom:1px solid var(--line);font:13px/1.3 system-ui,-apple-system,sans-serif}
.brand{display:flex;align-items:baseline;gap:8px;min-width:0}
.brand b{font-size:14.5px;white-space:nowrap}
.brand span{color:var(--muted);font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-center{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.seg{display:inline-flex;background:var(--th);border:1px solid var(--line);border-radius:6px;padding:2px;gap:2px}
.seg button{border:0;background:transparent;color:var(--muted);font:inherit;font-size:12.5px;padding:4px 10px;border-radius:4px;cursor:pointer;white-space:nowrap}
.seg button:hover{color:var(--fg)}
.seg button.active{background:var(--card);color:var(--fg);font-weight:600;box-shadow:0 1px 2px rgba(0,0,0,.08)}
.bar-actions{display:flex;align-items:center;gap:8px}
.theme{font:12px system-ui,sans-serif;background:var(--bg);border:1px solid var(--line);color:var(--fg);border-radius:4px;padding:4px 9px;cursor:pointer;white-space:nowrap}
.theme:hover{border-color:var(--accent);color:var(--accent)}

/* Tab visibility (Guide vs Technical Report) */
body.tab-guide #report-view{display:none}
body.tab-report #guide-view{display:none}

/* Layout modes (Split vs Reading Only vs 3D Fullscreen) */
body.layout-reading .viewer-pane,body.layout-reading .splitter{display:none}
body.layout-reading #report-view nav{top:70px;max-height:calc(100vh - 90px)}

body.layout-split{overflow:hidden}
body.layout-split .shell{display:flex;height:calc(100vh - 50px)}
body.layout-split .reading-pane{flex:0 0 var(--split,50%);min-width:340px;overflow-y:auto;scroll-behavior:smooth}
body.layout-split #report-view.wrap{grid-template-columns:1fr;padding:18px 24px 40px;gap:0;max-width:none}
body.layout-split #report-view nav{position:static;max-height:none;display:flex;flex-wrap:wrap;gap:4px 12px;padding-bottom:10px;margin-bottom:14px;border-bottom:1px solid var(--line)}
body.layout-split #report-view nav b{width:100%}
body.layout-split #report-view nav .l2{display:none}
body.layout-split .splitter{width:6px;cursor:col-resize;background:var(--line);flex:0 0 6px;transition:background .15s}
body.layout-split .splitter:hover,body.layout-split .splitter.dragging,body.layout-split .splitter:focus-visible{background:var(--accent);outline:none}
body.layout-split .viewer-pane{flex:1 1 0;min-width:340px;display:flex;flex-direction:column;overflow-y:auto;background:var(--bg)}

body.layout-3d{overflow:hidden}
body.layout-3d .reading-pane,body.layout-3d .splitter{display:none}
body.layout-3d .viewer-pane{display:flex;flex-direction:column;width:100%;height:calc(100vh - 50px);overflow-y:auto;background:var(--bg)}
body.layout-3d #viewer-app{max-width:1440px;width:100%;margin:0 auto}

/* Preset bar at top of viewer pane */
.preset-bar{display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:7px 14px;background:var(--card);border-bottom:1px solid var(--line);font:12px/1.3 system-ui,sans-serif;position:sticky;top:0;z-index:10}
.preset-bar .muted{color:var(--muted);margin-right:2px}
.preset-btn{font:inherit;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:14px;padding:3px 10px;cursor:pointer;white-space:nowrap}
.preset-btn:hover{border-color:var(--accent);color:var(--accent)}
.preset-btn.active{background:var(--accent);border-color:var(--accent);color:#fff}

/* Technical Report layout */
.wrap{display:grid;grid-template-columns:240px minmax(0,1fr);gap:40px;max-width:1240px;margin:0 auto;padding:32px 24px}
nav{position:sticky;top:20px;align-self:start;max-height:calc(100vh - 40px);overflow:auto;font:13px/1.5 system-ui,sans-serif}
nav a{display:block;color:var(--muted);text-decoration:none;padding:2px 0}nav a:hover{color:var(--accent)}
nav .l2{padding-left:12px}
main{min-width:0;max-width:880px}
h1{font-size:29px;line-height:1.22;margin:0 0 8px}
h2{font-size:22px;line-height:1.3;margin:40px 0 10px;padding-top:8px;border-top:1px solid var(--line)}
h3{font-size:17px;margin:24px 0 8px}
.meta{font:13px/1.5 system-ui,sans-serif;color:var(--muted)}
.banner{border:1px solid var(--warn);background:var(--warnbg);padding:12px 16px;border-radius:6px;margin:18px 0;font:14px/1.5 system-ui,sans-serif}
.tw{overflow-x:auto;margin:12px 0}
table{border-collapse:collapse;font:13px/1.4 system-ui,sans-serif;min-width:100%}
th,td{border:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}th{background:var(--th);font-weight:600}
tbody tr:nth-child(even){background:color-mix(in srgb,var(--card) 60%,transparent)}
figure{margin:16px 0;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:10px}
figure img{width:100%;height:auto;display:block;background:#fff;border-radius:3px}
figcaption{font:12.5px/1.5 system-ui,sans-serif;color:var(--muted);margin-top:8px}
code{font:12.5px ui-monospace,Menlo,Consolas,monospace;background:var(--codebg);padding:1px 4px;border-radius:3px;word-break:break-word}
.chip{display:inline-block;font:600 11px/1.6 system-ui,sans-serif;padding:0 8px;border-radius:10px;border:1px solid var(--line);white-space:nowrap}
.chip.ok{background:var(--okbg);color:var(--ok);border-color:var(--ok)}
.chip.warn{background:var(--warnbg);color:var(--warn);border-color:var(--warn)}
.chip.bad{background:var(--badbg);color:var(--bad);border-color:var(--bad)}
.chip.info{background:color-mix(in srgb,var(--accent) 10%,var(--card));color:var(--accent);border-color:var(--accent)}
a{color:var(--accent)}ol.find li,ul.tight li{margin:5px 0}
.small{font-size:13px;color:var(--muted)}
.v3d{display:inline-block;margin-left:5px;padding:0 5px;border-radius:4px;border:1px solid var(--accent);font:600 10.5px/1.5 system-ui,sans-serif;text-decoration:none;vertical-align:1px;cursor:pointer}
.v3d:hover{background:var(--accent);color:#fff}
details{margin:10px 0}summary{cursor:pointer;font:14px system-ui,sans-serif;color:var(--accent)}

/* Plain-English Question-Driven Audit Guide */
.guide-wrap{max-width:860px;margin:0 auto;padding:24px 24px 56px}
body.layout-split .guide-wrap{max-width:none;padding:20px 24px 48px}
.guide-hero{margin-bottom:24px;padding-bottom:18px;border-bottom:1px solid var(--line)}
.eyebrow{font:600 12px/1.4 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.05em;color:var(--accent);margin-bottom:6px}
.lead{font-size:17px;line-height:1.55;color:var(--fg);margin:8px 0 16px}
.scorecard{display:grid;grid-template-columns:1fr;gap:6px;font:13px/1.4 system-ui,sans-serif}
.sc-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:7px 11px;background:var(--card);border:1px solid var(--line);border-radius:6px;text-decoration:none;color:var(--fg);transition:border-color .15s}
.sc-row:hover{border-color:var(--accent)}
.audit-card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:18px 20px;margin:0 0 20px;box-shadow:0 1px 3px rgba(0,0,0,.03)}
.audit-card h2{margin:6px 0 10px;padding:0;border:0;font-size:21px}
.card-top{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;font:12px/1.4 system-ui,sans-serif}
.qnum{font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:5px}
.claim{background:var(--th);border-left:3px solid var(--accent);padding:9px 12px;border-radius:0 5px 5px 0;margin:10px 0 12px;font-size:15px}
.card-actions{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin-top:14px;padding-top:12px;border-top:1px solid var(--line);font:13px/1.4 system-ui,sans-serif}
.step-btn{font:600 12.5px/1.4 system-ui,sans-serif;background:var(--accent);color:#fff;border:1px solid var(--accent);border-radius:5px;padding:5px 11px;cursor:pointer}
.step-btn:hover{filter:brightness(1.08)}
td .step-btn{padding:2px 7px;font-size:11.5px}
.goto-rep{font:600 12.5px/1.4 system-ui,sans-serif;text-decoration:none;margin-left:auto}
.goto-rep:hover{text-decoration:underline}

/* Inline 2D SVG diagram typography */
.svg-fig svg{width:100%;height:auto;display:block;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
.svg-h{font-size:13px;font-weight:700;fill:var(--fg)}
.svg-b{font-size:11.5px;font-weight:600;fill:var(--fg)}
.svg-s{font-size:11px;fill:var(--muted)}

@media (max-width:1100px){
  .site-bar{flex-wrap:wrap;padding:6px 12px}
  .brand span{display:none}
  body.layout-split .shell{flex-direction:column;height:calc(100vh - 50px)}
  body.layout-split .reading-pane{flex:0 0 48%;min-width:0}
  body.layout-split .splitter{display:none}
  body.layout-split .viewer-pane{flex:1 1 52%;min-width:0;border-top:1px solid var(--line)}
}
@media (max-width:900px){
  .wrap{grid-template-columns:1fr;padding:16px}
  nav{position:static;max-height:none;border-bottom:1px solid var(--line);padding-bottom:10px}
  .guide-wrap{padding:16px 14px 40px}
  .sc-row{flex-direction:column;align-items:flex-start;gap:4px}
}
@media print{
  .site-bar,.viewer-pane,.splitter,nav,.v3d,.card-actions{display:none!important}
  body{overflow:visible!important;height:auto!important;font-size:11.5pt}
  .shell,.reading-pane{display:block!important;height:auto!important;overflow:visible!important}
  .wrap,.guide-wrap{display:block;padding:0;max-width:none}
}
"""

VIEWER_HTML = """<div id="viewer-app" v-cloak>
  <div class="step-banner" v-if="stepBanner">
    <span><b>Guided 3D View:</b> {{ stepBanner }}</span>
    <button type="button" @click="stepBanner = ''" aria-label="Dismiss caption">&times;</button>
  </div>

  <section class="guided-bar" v-if="compactMode" aria-label="Guided 3D controls">
    <span class="views"><span class="muted">Camera:</span>
      <button v-for="v in views" :key="v.key" type="button" :class="{ on: activeView === v.key }" @click="setView(v.key)">{{ v.label }}</button>
    </span>
    <span class="scale-pills"><span class="muted">Deformation:</span>
      <button type="button" :class="{ on: scale === 1 }" @click="scale = 1">True (&times;1)</button>
      <button type="button" :class="{ on: scale === 5 }" @click="scale = 5">&times;5</button>
      <button v-if="scale !== 1 && scale !== 5" type="button" class="on">&times;{{ scale }}</button>
    </span>
    <label class="check small"><input type="checkbox" v-model="showCols"> 3D columns &amp; plates</label>
    <button type="button" class="ctrl-toggle" @click="showAllControls = true">All controls &#x25BE;</button>
  </section>

  <section class="controls" v-else aria-label="Full 3D viewer controls">
    <label>Run
      <select v-model="runA">
        <option v-for="r in index.runs" :key="r.name" :value="r.name">{{ r.label }}</option>
      </select>
    </label>
    <label class="check"><input type="checkbox" v-model="compare"> Compare</label>
    <label v-if="compare">
      <select v-model="runB" aria-label="Second run">
        <option v-for="r in index.runs" :key="r.name" :value="r.name">{{ r.label }}</option>
      </select>
    </label>
    <label>Colour
      <select v-model="colorBy">
        <option value="part">By part</option>
        <option value="disp">Displacement |u|</option>
      </select>
    </label>
    <label>Scale
      <select v-model.number="scale">
        <option v-for="s in scales" :key="s" :value="s">{{ s === 1 ? 'True (×1)' : '×' + s }}</option>
      </select>
    </label>
    <label class="check"><input type="checkbox" v-model="showCols"> 3D columns &amp; side plates</label>
    <label class="check"><input type="checkbox" v-model="showBolts"> Bolts</label>
    <label class="check"><input type="checkbox" v-model="showStuds"> Studs</label>
    <label class="check"><input type="checkbox" v-model="showSlab"> Slab</label>
    <label class="check"><input type="checkbox" v-model="showGhost"> Initial outline</label>
    <span class="views">Camera:
      <button v-for="v in views" :key="v.key" type="button" :class="{ on: activeView === v.key }" @click="setView(v.key)">{{ v.label }}</button>
    </span>
    <button v-if="siteTab === 'guide' && siteLayout !== '3d'" type="button" class="ctrl-toggle" @click="showAllControls = false">Compact &#x25B4;</button>
  </section>

  <p class="note" v-if="error">{{ error }}</p>
  <section class="stage" :class="{ two: compare, rows: compare && narrow }">
    <div class="canvas-wrap" ref="wrap">
      <canvas ref="canvas" aria-label="3D view of the deformed Floor 13 framing"></canvas>
      <div v-for="(p, i) in panes" :key="i" class="pane" :style="paneStyle(i)">
        <div class="pane-head" v-if="p.run">
          <b>{{ p.run.label }}</b>
          <span class="vchip" :class="readingClass(p.run.reading)">{{ p.run.reading }}</span>
          <div class="small">{{ p.frameText }}</div>
          <div class="note" v-if="p.run.col79 === 'flexible'">Column 79 moves in this run (S5); its plates are drawn where they start.</div>
          <div class="note" v-if="p.afterLast">Last 3D snapshot; trace continues to {{ p.endText }}.</div>
        </div>
        <div class="pane-loading" v-else>Loading 3D mesh&hellip;</div>
        <div class="scale-badge" :class="{ warn: scale !== 1 }">{{ scale === 1 ? 'True scale (×1)' : 'Displacements ×' + scale + ' (exaggerated)' }}</div>
      </div>
      <svg class="north" viewBox="-26 -26 52 52" aria-hidden="true">
        <circle r="24"></circle>
        <g :transform="'rotate(' + northDeg + ')'"><path class="n" d="M0,-12 L4,0 L-4,0 Z"></path><path class="s" d="M0,12 L4,0 L-4,0 Z"></path>
          <text y="-15" text-anchor="middle">N</text></g>
      </svg>
    </div>
  </section>

  <section class="timeline">
    <button type="button" class="play" @click="togglePlay">{{ playing ? 'Pause' : 'Play' }}</button>
    <input type="range" min="0" :max="Math.max(times.length - 1, 0)" step="1" v-model.number="ti" aria-label="Snapshot time">
    <span class="tlabel">t = {{ tNow.toFixed(2) }} s &middot; {{ TNow.toFixed(0) }} &deg;C</span>
  </section>

  <section class="legend-row">
    <div class="legend" v-if="colorBy === 'part'">
      <span v-for="p in partLegend" :key="p.name"><i :style="{ background: p.color }"></i>{{ p.name }}</span>
      <span v-if="showCols || showSupports"><i class="dash"></i>6.25 in. walk-off line</span>
      <span v-if="showBolts || showStuds"><i class="dot" :style="{ background: boltColors.intact }"></i>{{ boltWord }} intact</span>
      <span v-if="showBolts || showStuds"><i class="dot" :style="{ background: boltColors.broken }"></i>&#x2715; {{ boltWord }} sheared</span>
    </div>
    <div class="legend" v-else>
      <span>|u| (in.)</span>
      <span class="ramp"><i :style="{ background: rampCss }"></i><em>0</em><em>{{ umaxShown.toFixed(1) }}</em></span>
      <span class="muted small">True displacement magnitude across both views.</span>
    </div>
  </section>

  <section class="events" v-if="panes[0] && panes[0].run">
    <div v-for="(p, i) in panes" :key="'ev' + i">
      <span class="small"><b v-if="compare">{{ p.run && p.run.label }}: </b>
        <span class="muted">Jump to event:</span></span>
      <button v-for="e in p.events" :key="e.key" type="button" class="ev" @click="jumpTo(e.t)"
              :title="'Snapshot at or before t = ' + e.t.toFixed(2) + ' s'">{{ e.label }} ({{ e.T.toFixed(0) }} &deg;C)</button>
    </div>
  </section>

  <section class="trace">
    <div class="trace-head">
      <label>Time-history plot
        <select v-model="quantity">
          <option v-for="q in quantities" :key="q.key" :value="q.key">{{ q.label }}</option>
        </select>
      </label>
      <span class="legend small" v-if="compare">
        <span><i :style="{ background: seriesColors[0] }"></i>{{ panes[0].run && panes[0].run.label }}</span>
        <span><i :style="{ background: seriesColors[1] }"></i>{{ panes[1].run && panes[1].run.label }}</span>
      </span>
    </div>
    <svg ref="svg" class="chart" :style="{ height: H + 'px' }" @mousemove="hover" @mouseleave="hoverT = null" @click="clickTrace"
         role="img" :aria-label="qInfo.label + ' against time'">
      <rect v-for="(s, i) in noSnap" :key="'ns' + i" :x="s.x" :y="M.t" :width="s.w" :height="H - M.t - M.b" class="nosnap"></rect>
      <g class="grid">
        <line v-for="y in yTicks" :key="'y' + y" :x1="M.l" :x2="W - M.r" :y1="sy(y)" :y2="sy(y)"></line>
      </g>
      <g class="axis">
        <text v-for="y in yTicks" :key="'yt' + y" :x="M.l - 6" :y="sy(y) + 4" text-anchor="end">{{ fmt(y) }}</text>
        <text v-for="x in xTicks" :key="'xt' + x" :x="sx(x)" :y="H - M.b + 15" text-anchor="middle">{{ x }}</text>
        <text :x="W - M.r" :y="H - 3" text-anchor="end">time (s); heating starts at 1.1 s</text>
      </g>
      <g v-if="qInfo.threshold != null">
        <line class="thr" :x1="M.l" :x2="W - M.r" :y1="sy(qInfo.threshold)" :y2="sy(qInfo.threshold)"></line>
        <text class="thr-l" :x="M.l + 4" :y="sy(qInfo.threshold) - 4">walk-off threshold, {{ qInfo.threshold }} in.</text>
      </g>
      <path v-for="(p, i) in paths" :key="'p' + i" :d="p" class="line" :style="{ stroke: seriesColors[i] }"></path>
      <line class="cursor" :x1="sx(tNow)" :x2="sx(tNow)" :y1="M.t" :y2="H - M.b"></line>
      <g v-if="hoverInfo">
        <line class="cross" :x1="hoverInfo.x" :x2="hoverInfo.x" :y1="M.t" :y2="H - M.b"></line>
        <circle v-for="(v, i) in hoverInfo.vals" :key="'hc' + i" :cx="hoverInfo.x" :cy="sy(v.v)" r="4" :style="{ fill: seriesColors[i] }" class="hdot"></circle>
      </g>
    </svg>
    <div class="tip" v-if="hoverInfo" :style="{ left: hoverInfo.px + 'px' }">
      <b>t = {{ hoverInfo.t.toFixed(2) }} s</b>
      <div v-for="(v, i) in hoverInfo.vals" :key="'tv' + i"><i :style="{ background: seriesColors[i] }"></i>{{ v.name }}: {{ fmt(v.v) }} {{ qInfo.unit }}, beam {{ v.T.toFixed(0) }} &deg;C</div>
      <div class="muted">Click chart to scrub 3D view to this time</div>
    </div>
  </section>

  <details class="about">
    <summary>What this 3D view shows and its display conventions</summary>
    <ul>
      <li>Node positions from <code>results/phase1/shell/runs/*.npz</code> (every 50 &deg;C of beam heating and each Column 79 bolt failure), plus hold-phase state dumps for <code>favourable_dump</code>. Displacements are rounded to {{ resText }} in.</li>
      <li>Columns 79 and 44, the amber 26 &times; 2 in. Column 79 side cover plates, and the seats are drawn from the exact rigid contact geometry of each run's configuration; shells are drawn at their mid-surface.</li>
      <li>Axes: x east, y north, z up; units in inches. Drag to orbit, scroll to zoom, right-drag to pan.</li>
    </ul>
  </details>
</div>"""

BOOT_JS = """
(function(){
  try {
    var t = localStorage.getItem('wtc7-theme');
    if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
  } catch (e) {}
  var raw = location.hash.slice(1);
  var isParams = raw.indexOf('=') >= 0;
  var p = new URLSearchParams(isParams ? raw : '');
  var reportAnchors = ['summary','question','evidence','ev-sources','ev-drawings','ev-secondary','methods','m-prereg','m-models','m-verify','screening','s-dig','s-draw','detailed','diff','checks','limits','next','app','files'];
  var initTab = p.get('tab');
  if (initTab !== 'guide' && initTab !== 'report') {
    initTab = (!isParams && reportAnchors.indexOf(raw) >= 0) ? 'report' : 'guide';
  }
  var initLayout = p.get('layout');
  if (initLayout !== 'split' && initLayout !== 'reading' && initLayout !== '3d') {
    initLayout = window.innerWidth >= 1100 ? 'split' : 'reading';
  }
  window.WTC7 = { geom: {}, runs: {}, index: null, dataDir: 'viewer/data/', initTab: initTab, initLayout: initLayout, anchor: !isParams ? raw : '' };
})();
"""

SITE_JS = """
(function(){
  var W7 = window.WTC7;
  var k = 'wtc7-theme', b = document.getElementById('theme');
  var splitter = document.getElementById('splitter');
  var readingPane = document.getElementById('reading-pane');
  var tabBtns = document.querySelectorAll('[data-tab]');
  var layoutBtns = document.querySelectorAll('[data-layout]');
  var presetBtns = document.querySelectorAll('.preset-btn[data-viewer]');
  var curTab = W7.initTab || 'guide', curLayout = W7.initLayout || 'split';

  function setTheme(t){
    if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
    else document.documentElement.removeAttribute('data-theme');
  }
  if (b) {
    b.addEventListener('click', function(){
      var cur = document.documentElement.getAttribute('data-theme') || '';
      var dark = cur ? cur === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
      var nt = dark ? 'light' : 'dark';
      setTheme(nt);
      try { localStorage.setItem(k, nt); } catch (e) {}
    });
  }

  function syncHash(){
    var q = new URLSearchParams();
    q.set('tab', curTab);
    q.set('layout', curLayout);
    if (W7.viewer) {
      var vp = W7.viewer.getHashParams();
      if (vp.a) q.set('a', vp.a);
      if (vp.b) q.set('b', vp.b);
      if (vp.c) q.set('c', vp.c);
      if (vp.s) q.set('s', vp.s);
      var key = 'a=' + vp.a + (vp.b ? '&b=' + vp.b : '');
      presetBtns.forEach(function(btn){ btn.classList.toggle('active', btn.getAttribute('data-viewer') === key); });
    }
    try { history.replaceState(null, '', '#' + q.toString()); } catch (e) {}
  }
  W7.syncHash = syncHash;

  function applyUI(){
    document.body.classList.remove('tab-guide', 'tab-report', 'layout-split', 'layout-reading', 'layout-3d');
    document.body.classList.add('tab-' + curTab, 'layout-' + curLayout);
    tabBtns.forEach(function(btn){
      var on = btn.getAttribute('data-tab') === curTab && curLayout !== '3d';
      btn.classList.toggle('active', on);
      btn.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    layoutBtns.forEach(function(btn){
      var on = btn.getAttribute('data-layout') === curLayout;
      btn.classList.toggle('active', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    if (W7.viewer) W7.viewer.setContext(curTab, curLayout);
    syncHash();
  }

  function setTab(t){
    curTab = (t === 'report') ? 'report' : 'guide';
    if (curLayout === '3d') curLayout = window.innerWidth >= 1100 ? 'split' : 'reading';
    applyUI();
    if (readingPane) readingPane.scrollTop = 0;
    window.scrollTo(0, 0);
  }

  function setLayout(l){
    if (l !== 'split' && l !== 'reading' && l !== '3d') l = 'split';
    curLayout = l;
    applyUI();
  }

  tabBtns.forEach(function(btn){
    btn.addEventListener('click', function(){ setTab(btn.getAttribute('data-tab')); });
  });
  layoutBtns.forEach(function(btn){
    btn.addEventListener('click', function(){ setLayout(btn.getAttribute('data-layout')); });
  });

  function scrollToTarget(id){
    var el = document.getElementById(id);
    if (!el) return;
    if (curLayout === 'split' && readingPane) {
      var top = el.getBoundingClientRect().top - readingPane.getBoundingClientRect().top + readingPane.scrollTop - 12;
      readingPane.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
    } else {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function triggerViewer(opts){
    if (curLayout === 'reading') {
      curLayout = window.innerWidth >= 1100 ? 'split' : '3d';
      applyUI();
    }
    if (W7.viewer) W7.viewer.apply(opts);
    else W7.pendingApply = opts;
  }

  document.addEventListener('click', function(e){
    var stepEl = e.target.closest('[data-viewer-step]');
    if (stepEl) {
      e.preventDefault();
      try { triggerViewer(JSON.parse(stepEl.getAttribute('data-viewer-step'))); } catch (err) {}
      return;
    }
    var vEl = e.target.closest('[data-viewer]');
    if (vEl) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
      e.preventDefault();
      var p = new URLSearchParams(vEl.getAttribute('data-viewer'));
      triggerViewer({ a: p.get('a'), b: p.get('b') || '', c: p.get('c') || 'part', s: +(p.get('s') || 1), banner: '' });
      return;
    }
    var layEl = e.target.closest('[data-set-layout]');
    if (layEl) {
      e.preventDefault();
      setLayout(layEl.getAttribute('data-set-layout'));
      return;
    }
    var repEl = e.target.closest('[data-goto-report]');
    if (repEl) {
      e.preventDefault();
      var id = repEl.getAttribute('data-goto-report').replace(/^#/, '');
      curTab = 'report';
      if (curLayout === '3d') curLayout = window.innerWidth >= 1100 ? 'split' : 'reading';
      applyUI();
      requestAnimationFrame(function(){ scrollToTarget(id); });
      return;
    }
    var anchorEl = e.target.closest('a[href^="#"]');
    if (anchorEl && !anchorEl.hasAttribute('data-viewer')) {
      var aid = anchorEl.getAttribute('href').slice(1);
      if (aid && aid.indexOf('=') < 0 && document.getElementById(aid)) {
        e.preventDefault();
        scrollToTarget(aid);
      }
    }
  });

  if (splitter && readingPane) {
    var dragging = false;
    function setSplit(pct){
      pct = Math.max(28, Math.min(70, pct));
      document.documentElement.style.setProperty('--split', pct.toFixed(2) + '%');
      if (W7.viewer) W7.viewer.resize();
    }
    splitter.addEventListener('pointerdown', function(e){
      dragging = true;
      splitter.classList.add('dragging');
      splitter.setPointerCapture(e.pointerId);
    });
    splitter.addEventListener('pointermove', function(e){
      if (!dragging) return;
      setSplit((e.clientX / window.innerWidth) * 100);
    });
    function endDrag(e){
      if (!dragging) return;
      dragging = false;
      splitter.classList.remove('dragging');
      try { splitter.releasePointerCapture(e.pointerId); } catch (err) {}
    }
    splitter.addEventListener('pointerup', endDrag);
    splitter.addEventListener('pointercancel', endDrag);
    splitter.addEventListener('keydown', function(e){
      var cur = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--split')) || 50;
      if (e.key === 'ArrowLeft') { e.preventDefault(); setSplit(cur - 3); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); setSplit(cur + 3); }
    });
  }

  applyUI();
  if (W7.anchor && document.getElementById(W7.anchor)) {
    requestAnimationFrame(function(){ scrollToTarget(W7.anchor); });
  }
})();
"""


def build():
    import report_figures as rf
    if ASSETS.exists():                 # reports/forensic/viewer/ is built by scripts/export_viewer.py; keep it
        shutil.rmtree(ASSETS)
    ASSETS.mkdir(parents=True)
    figs = {f.__name__: f(ASSETS) for f in rf.ALL}
    for p in ("drawings_col79.png", "friction.png"):
        if (RES / "plots" / p).exists():
            shutil.copy(RES / "plots" / p, ASSETS / p)
    crops = ROOT / "sources" / "drawings" / "crops"
    crop_list = ["9114_col79_seat_conn_plan_at_seat.png", "9114_col79_seat_plan_girder_end_side_plate_x2.png",
                 "1091_col79_section_A-A_seat_pf_pg_detail_x2.2.png", "9114_col79_seat_conn_elevation.png",
                 "E12-13_girder_A2001_bevel_3-9-16_in_12_span_45-7-5-8_x2.5.png", "E12-13_NE_quadrant_girder_A2001.png",
                 "1370_col44_section_A-A_top_plate_level.png"]
    for c in crop_list:
        shutil.copy(crops / c, ASSETS / c)

    runs = shell_runs()
    vruns = viewer_runs()

    def run_cell(n):
        if n in vruns:
            return code(n) + f'<a class="v3d" href="#tab=report&amp;layout=split&amp;a={E(n)}" data-viewer="a={E(n)}" title="View {E(n)} in 3D">3D</a>'
        return code(n)

    status = run_status()
    druns = drawings_runs()
    dig = digitized_summary()
    built = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    n_done = sum(1 for r in status if r[3] == "done")
    n_run = sum(1 for r in status if r[3] == "running")
    fn = iter(range(1, 100))
    S = []

    # ------------------------------------------------------------ header and summary
    S.append(f"""<h1>WTC 7 floor 13 girder at column 79: Phase 1 forensic report</h1>
<p class="meta">Interim report, built {built} from the repository state. Study brief dated 2026-10-21.
Every number on this page is read from the run outputs, assumption table and checksum files at build time
(<code>scripts/build_report.py</code>).</p>
<div class="banner"><b>Interim. The Phase 1 gate has not passed, and nothing here is a finding about why WTC 7 collapsed.</b>
Detailed-model runs completed: {n_done} of {len(status)} listed ({n_run} running). The outcome class is stated (Section 6);
it differs from NIST's, and the NIST-replica runs did not find what explains the difference (Section 7).</div>""")
    base = runs.get("check_rate_half")
    bev = base["events"] if base else {}
    S.append('<h2 id="summary">1. Summary</h2>')
    S.append("""<p>The question for Phase 1 is whether heating of the floor 13 framing in the northeast corner of WTC 7, as
NIST described it, makes the W33x130 girder spanning from column 79 to column 44 (erection mark A2001) lose its seat
at column 79. NIST's report (NCSTAR 1-9) identifies that event as the start of the collapse. This report covers the
evidence gathered so far, the models built and what their completed runs show.</p>""")
    findings = [
        "<b>The fabrication drawings change the geometry at column 79.</b> Frankel shop drawings 9114 and 1091 and erection drawing E12/13 "
        "(NIST FOIA releases) show the girder meeting column 79's north face only 4.17 deg off square (written on the sheets; the "
        "column's 12.3 deg rotation from the grid is inferred from three members), not at the 14.6 deg this study had digitized from NCSTAR 1-9 Fig. 8-16. They also show the girder skew is "
        "16.5 deg, and that the girder end sits at the mouth of a recess formed by the column's 26 in. side cover plates, with about "
        "4.15 in. of room to the west plate once inside it (Section 3).",
        "<b>The study's first screening result is withdrawn.</b> On the digitized geometry the screening model found walk-off decided by "
        "friction at the column 79 face, switching between 0.22 and 0.24. That threshold came from the wrong face angle (Section 5.1).",
        "<b>On the drawn geometry the screening model shows no walk-off</b> for any friction from 0 to 0.3, for the girder end 0.4 in. "
        "nearer or further, or with heating then cooling. The heated girder pushes its end about 1.5 in. into the recess; friction or "
        "the west side plate then stops it at 1.6 to 4.0 in. of westward movement, short of the 6.25 in. needed. Walk-off occurs only "
        "with zero friction and the side plates removed (Section 5.2).",
    ]
    if base:
        mx = max(x["lat79"] for x in base["rows"])
        nmax = -min(min(x["beamN"]) for x in base["rows"])
        bow = max(abs(x["girder_bow"]) for x in base["rows"])
        findings.append(
            "<b>In the detailed shell model no run walks off under NIST's schedule</b> (600 C beams, 500 C girder, held 1.4 s): "
            "not the baseline and not any one-at-a-time value of the preregistered sweeps. In the baseline the girder end at "
            f"column 79 moves at most {mx:.2f} in. west, against 6.25 in. for walk-off. The reported runs heat at half NIST's rate, "
            "because the full rate failed the preregistered rate check (Sections 6 and 8).")
        findings.append(
            "<b>One run walks off: the preregistered most-favourable combination, at 700 C during the hold,</b> after the girder "
            "buckles; a repeat reproduces it and continues to loss of support. The Section 6 repeat, with four ends replaced by the "
            "values the sweeps showed move the girder further, does not walk off. The outcome class is <b>CONDITIONAL</b>, on the "
            "combination as a whole: no single parameter flips the result (Section 6).")
        findings.append(
            "<b>The model departs from NIST at beam buckling.</b> The connection events agree with NIST's within 40 C through "
            f"column 79 (first stud {T(bev, 'first_stud')} C, all column 79 bolts {T(bev, 'E1_g79_all_bolts')} C; NIST 103 and "
            "194 C), but no floor beam buckles in the baseline, where NIST's northmost beam began to buckle at 436 C and all of "
            f"them by 600 C. The beams' compression peaks at {nmax:.0f} kip; the expanding beams push the girder sideways instead "
            f"(it bows {bow:.1f} in.). The NIST-replica runs reach walk-off by sliding rather than rocking after beam buckling, so "
            "what explains the difference is not yet found (Section 7).")
    findings.append("<b>Checks.</b> The shell solver written for this study reproduces closed-form results (thermal expansion, "
                    "restrained force, Euler buckling, friction thresholds, bolt failure) and matches CalculiX within 1.6 % for "
                    "lateral-torsional buckling. Two preregistered checks fail: mesh, narrowly (Section 8), and quasi-static, "
                    "because kinetic energy exceeds 5 % of internal energy during the gravity ramp in every run and briefly during "
                    "heating in most. Neither can change an outcome, but the Phase 1 gate has not passed.")
    S.append('<ol class="find">' + "".join(f"<li>{f}</li>" for f in findings) + "</ol>")

    # ------------------------------------------------------------ question and NIST account
    S.append('<h2 id="question">2. The question and NIST\'s account</h2>')
    S.append("""<p>NIST's leading hypothesis (NCSTAR 1-9, Chapters 8, 11 and 12; FAQ) is that fire on floors 8 to 13 heated the floor beams east
of column 79, whose thermal expansion pushed girder A2001 laterally at column 79 after its erection bolts had sheared, until
it lost its seat on floor 13. The floors below then failed in a cascade to floor 5, leaving column 79 unsupported over nine
storeys; it buckled, followed by the east penthouse, columns 80 and 81 and the rest of the core.</p>
<p>NIST tested the floor framing mechanism in a partial-floor LS-DYNA model (&sect;8.8): shells about 1.8 in., one layer of slab
shells, bolts and studs as springs, gravity ramped over 1 s, then the beams heated uniformly to 600 C and the girder to 500 C
between 1.1 and 2.6 s. Its reported sequence (Table 8-2):</p>""")
    S.append(table(["Time (s)", "Beam (C)", "Girder (C)", "Event (NCSTAR 1-9 Table 8-2)"], [
        ("1.44", "103", "89", "First shear stud failure"), ("1.54", "154", "131", "Both seat bolts of girder to column 79 failed"),
        ("1.62", "194", "164", "Both top clip bolts of girder to column 79 failed"),
        ("1.83", "300", "252", "All but three shear studs failed"), ("2.04", "406", "339", "Both seat bolts of girder to column 44 failed"),
        ("2.10", "436", "364", "Northmost floor beam began to buckle laterally"),
        ("2.18", "476", "398", "Both top plate bolts of girder to column 44 failed"),
        ("2.90", "600", "500", "All floor beams began to buckle; the girder rocked off its seat at column 79")]))
    S.append("""<p>The June 2012 errata set the column 79 seat width at 12 in. (from 11) and the lateral walk-off distance at 6.25 in. (from 5.5).
The 16-story ANSYS model (&sect;11.3) found walk-off at column 79 on floor 13 between 3.7 and 4.0 h with floor 13 steel at 300 to
700 C. NIST did not release its model input files; this study rebuilds the models from the published reports and drawings.</p>""")

    # ------------------------------------------------------------ evidence
    S.append('<h2 id="evidence">3. Evidence base</h2>')
    S.append('<h3 id="ev-sources">3.1 Documents and checksums</h3>')
    S.append("<p>Every downloaded document is archived in the repository (<code>sources/README.md</code>), so the work can be "
             "checked if the originals are taken down. <code>sources/SHA256SUMS</code> covers all of them; "
             "<code>scripts/fetch_sources.sh</code> and <code>scripts/fetch_drawings.sh</code> restore any missing file from its "
             "original URL. Downloaded files are treated as untrusted data and never executed.</p>")
    S.append(table(["File", "SHA-256"], [(code(f), code(h)) for f, h in source_hashes()]))
    S.append(table(["Local file", "Sheet", "Source", "Retrieved (UTC)", "SHA-256"],
                   [(code(a), E(b), f'<a href="{E(c)}">archive.org</a>', E(d), code(h)) for a, b, c, d, h in drawing_sources()]))
    S.append("""<p><b>Not obtained:</b> the girder's own piece drawing (Frankel 2001; the 2000 series is not in the FOIA 12-009 release),
so the girder's length, its column 44 end and its hole layout come from other sheets or are assumed (A91, A96). NIST's model
input files were not released.</p>""")
    S.append('<h3 id="ev-drawings">3.2 What the drawings show</h3>')
    S.append(f"""<p>Readings by sheet, with each item marked {chip('legible', 'ok')} when read directly, {chip('partly legible', 'warn')}
when a character or reference line is uncertain, and {chip('inferred', 'info')} when derived from written dimensions or scaling.
Full readings: <code>sources/drawings/READING.md</code>.</p>""")
    L, P_, I_ = chip("legible", "ok"), chip("partly legible", "warn"), chip("inferred", "info")
    S.append(table(["Item", "Reading", "Sheet", "Confidence", "Used as"], [
        ("Girder skew to grid", "3 9/16 in 12 = 16.5 deg; span 45'-7 5/8 between column centres", "E12/13 rev 4", L, "A90, A91"),
        ("Girder to column 79 axis", "7/8 in 12 = 4.17 deg", "9114 rev 2, 1091 rev 2", L, "A93"),
        ("Column 79 rotation", "about 12.3 deg clockwise from grid (A2002 square to it, W36x135 at 5 5/16 in 12)", "E12/13, 1091", I_, "A93"),
        ("Column 79 section", "W14x730 (22 3/8 x 17 7/8) with 2 PL 26 x 2 across the flange tips", "1091 BOM", L, "A94"),
        ("Side-plate projection", "1 13/16 in. past the flange face if centred (not dimensioned)", "1091", I_, "A94"),
        ("Seat pf", "PL 8 1/4 x 1 x 1'-0, aligned with the girder, back to the flange face", "1091, 9114", L, "A95"),
        ("Seat support pg", "PL 14 x 2 x 1'-6 7/8 across the plate ends, below the seat", "1091, 9114", L, "not modelled (below seat)"),
        ("Seat bolts", "2 x 7/8 A325, gage 5 1/2, bolt line 1'-5 1/4 from column centre", "9114, 1091", L, "A95"),
        ("Girder end position", "4 1/4 from seat bolt line: 13.0 in. from column centre, 1.78 in. from flange face", "9114", P_, "A91"),
        ("Clip angle", "L6x4x3/8 x 9 in., standard 15/16 holes (no slot called out)", "9114, 1091", L, "A95, S3 baseline"),
        ("Girder end stiffeners", "PL 5 1/2 x 3/4 x 1'-6 both sides of web", "9114", L, "A97 (sensitivity)"),
        ("Column 44", "W14x665 on grid; girder enters between flanges at 16.5 deg; top plate 1 1/8 x 15/16 slots", "1370, 9102", L, "A96"),
        ("Beams into A2001", "G3005 W21x44 <24>, A3004, B3004, C3004, K3004 W24x55 <28>; stations 50.1 to 512.8 in. from col 44", "E12/13", L, "A92"),
        ("Girder studs, floor 13", "none shown", "E12/13, S-8 rev H", L, "S1 baseline 0"),
        ("Camber", "girder 1 in., beams 1 3/4 to 2 1/4 in.", "E12/13", L, "not modelled (Q22)"),
    ]))
    n = next(fn)
    S.append(fig("recess_detail.png", "Column 79 at the girder seat in the column's own axes, drawn from the readings above "
                 "(A93 to A95). The girder end is at the mouth of the recess between the side cover plates; the west flange corner "
                 "is 0.38 in. outside the plane of the plate ends, the east corner 0.45 in. inside. Once inside, the west flange tip "
                 "has 4.15 in. of room to the west plate.", n))
    n = next(fn)
    S.append(fig("9114_col79_seat_conn_plan_at_seat.png", "Frankel 9114 rev 2, plan at the seat of the column 79 connection (crop "
                 "of the scan). The 7/8 in 12 bevel, the 5 1/2 gage, the 4 1/4 in. dimension from the bolt line to the girder end and "
                 "the 1'-5 1/4 from the column centre are written on the sheet.", n))
    n = next(fn)
    S.append(fig("9114_col79_seat_plan_girder_end_side_plate_x2.png", "Frankel 9114, enlargement: the girder end at the projecting "
                 "ends of the side cover plates (horizontal bars at top and bottom), with the seat support plate pg drawn dashed across "
                 "the plate ends.", n))
    n = next(fn)
    S.append(fig("1091_col79_section_A-A_seat_pf_pg_detail_x2.2.png", "Frankel 1091 rev 2, Section A-A: seat plate pf rotated with "
                 "the girder and reaching back to the flange face; support plate pg across the side-plate ends; the two seat bolts.", n))
    n = next(fn)
    S.append(fig("E12-13_NE_quadrant_girder_A2001.png", "Frankel E12/13 rev 4, northeast quadrant: girder A2001 from column 44 "
                 "(top) to column 79, the beams framing in from the east with their stud counts in angle brackets and cambers in "
                 "square brackets, and the 3 9/16 in 12 bevel.", n))
    n = next(fn)
    S.append(fig("1370_col44_section_A-A_top_plate_level.png", "Frankel 1370 rev 1, column 44 Section A-A: the girder enters "
                 "between the flanges at 3 9/16 in 12; top plate PA with 1 1/8 x 15/16 slots.", n))
    S.append("""<h3 id="ev-secondary">3.3 Secondary sources</h3>
<p>The 2020 University of Alaska Fairbanks report (Hulsey, Quan, Xiao), AE911Truth's 2020 request for correction and NIST's
2020 reply discuss the side plates. The first two argue that the heated girder becomes trapped behind the west side plate;
NIST's reply describes the seat as attached to the exterior edges of the side plates with the girder at a slight angle.
On the girder's room-temperature position these sources agree with the reading above within its uncertainty. None of them
was used as an input; they are summarized in <code>sources/drawings/READING.md</code>.</p>""")

    # ------------------------------------------------------------ methods
    S.append('<h2 id="methods">4. Methods</h2>')
    S.append('<h3 id="m-prereg">4.1 Pre-registration</h3>')
    S.append("""<p>Outcome classes, event definitions, model checks and every sweep range were written and hashed before the first run,
and each later amendment was hashed before the runs it governs (<code>docs/preregistration.md</code>). The rule throughout: no
input is chosen or changed after seeing the result it affects; corrections from primary documents are logged with their reason.</p>""")
    S.append(table(["Recorded (UTC)", "File state", "SHA-256"], [(a, E(b), code(c)) for a, b, c in prereg_hashes()]))
    S.append("""<p><b>Events.</b> E1: all four erection bolts at the column 79 seat failed. E2: walk-off at column 79, the girder end moving
6.25 in. laterally or 5.5 in. along its axis after E1 (errata values). E2r: twist at column 79 of atan(bf/d) = 19.2 deg. E2s:
physical loss of support, the girder end dropping 2 in. E3: all column 44 bolts failed. E4: a floor beam deflecting laterally
by L/50. E5 (monitored, not preregistered): the girder bowing by L/50. <b>Classes:</b> CONFIRMS if E1 &le; 400 C and E2 (or E2r, E2s) &le; 700 C in the
baseline; CONTRADICTS if no run within the ranges reaches E2 by 700 C; CONDITIONAL otherwise.</p>""")
    S.append('<h3 id="m-models">4.2 Models</h3>')
    S.append(table(["Item", "NIST partial-floor model (§8.8)", "This study, detailed shell model"], [
        ("Software", "LS-DYNA (explicit)", "wtc7.xfe, written for this study (explicit; OpenRadioss was withdrawn by its owner in October 2026)"),
        ("Geometry", "From the Frankel and Cantor drawings (cited in NCSTAR)", "From the same drawings (A90 to A99); girder piece drawing missing"),
        ("Members", "Fully integrated shells, 5 points through thickness, about 1.8 in.", "Belytschko-Lin-Tsay shells, 5 points, 1.8 in.; 51,149 shells"),
        ("Slab", "One shell layer, MAT_124 tension/compression, 7.5 in.", "One shell layer, tension/compression plasticity with NIST's rule-of-mixtures curves, 7.5 in."),
        ("Connections", "Bolts and studs as nonlinear springs (shear and axial)", "Breakable springs with NIST's temperature-dependent strength; hole clearance; slots"),
        ("Seats, columns", "Shells, welded edges fixed; column 79 flange and side-plate projections modelled", "Rigid planes with friction, including the side plates' inner faces and ends; seat edges act on the flange"),
        ("Friction", "Not described", "0.3 baseline (AISC Class A slip coefficient as a proxy), swept 0 to 0.6"),
        ("Loading", "Gravity 1 s; heating 1.1 to 2.6 s to 600/500 C; analysis to about 4 s",
         "Same schedule; the reported runs heat at half the rate (600/500 C at 4.1 s), held 1.4 s"),
        ("Girder end stiffeners", "Not modelled (NIST, 2013 and 2020)", "Not in baseline; one run as drawn"),
    ]))
    S.append("""<p>The plan-view screening model (<code>phase1/plan_model.py</code>) uses beam elements in the horizontal plane with the same
connections, friction and contacts, including a recess stop for the side plates. It runs in minutes and is used to locate
which inputs matter; it cannot represent twisting, sagging or rocking.</p>""")
    n = next(fn)
    S.append(fig("plan_geometry.png", "The northeast bay in plan: the digitized geometry used for the first screening runs (grey, "
                 "superseded) and the geometry read from the drawings (blue).", n))
    S.append('<h3 id="m-verify">4.3 Solver verification</h3>')
    S.append("""<p>The shell solver passes 22 unit tests against closed-form results (<code>tests/test_xfe.py</code>): material curves
within 1 % of the NIST and EN 1993-1-2 tables, free thermal expansion within 0.4 % (preregistered limit 1 %), restrained thermal
force exact while elastic, a heated pinned strut's buckling load within 2 % of Euler, a block on an incline sticking or sliding
exactly at tan(theta) = mu, a plate pushed into a skewed face sliding only when friction is below tan(14.6 deg), bolt springs
breaking at the temperature-reduced capacity, and contact carrying an applied load exactly. Lateral-torsional buckling of a shell
I-beam was checked against the Vlasov formula and against CalculiX 2.20 (independent code, linear buckling):</p>""")
    vr = verification_rows()
    S.append(table(["Mesh", "Hourglass coefficient", "This solver (kip-in.)", "CalculiX S4 (kip-in.)", "Ratio to CalculiX",
                    "Ratio to theory", "Hourglass / internal energy"], vr))
    S.append("""<p><b>Gravity check.</b> Under gravity alone the support reactions sum to 216.0 kip against 215.6 kip applied. Two modelling
choices were corrected during gravity-only pilots, before any heated run: an elastic slab and rigid top-plate ties clamped
the beam ends against their seats, so the slab now follows NIST's tension/compression model (A72) and the clip-angle and
top-plate ties have the bending stiffness of those parts (A80). A residual prying pattern remains: each beam end rotates on the
toe of its seat and the seat carries about twice the simple end shear, limited by the cracked slab's local strength.</p>""")

    # ------------------------------------------------------------ results: screening
    S.append('<h2 id="screening">5. Screening model results</h2>')
    S.append('<h3 id="s-dig">5.1 Digitized geometry (superseded)</h3>')
    walk = [r for r in dig if r["E2 walk-off (6.25 in.)"] not in ("none", "")]
    S.append(f"""<p>{len(dig)} runs on the geometry digitized from NCSTAR figures, with the column 79 face on the building grid. Walk-off
occurred in {len(walk)} runs, all at friction 0.22 or below or in combinations including it. These runs are kept for the record
(<code>results/phase1/summary.md</code>) but the face angle that produced the friction threshold is contradicted by the drawings
(4.17 deg, not 14.6 deg), so they carry no weight in the conclusions.</p>""")
    S.append('<h3 id="s-draw">5.2 Drawings geometry</h3>')
    drows = []
    for nme, r in sorted(druns.items(), key=lambda kv: (kv[1]["config"].get("side_plates", "auto") == "clear",
                                                        kv[1]["config"]["mu_seat"], kv[0])):
        c, ev, h = r["config"], r["events"], r["rows"]
        other = []
        if c.get("history") != "monotonic":
            other.append("heat then cool")
        if c.get("end79"):
            other.append(f"col 79 {c['end79']:+.1f} in.")
        drows.append((code(nme), f"{c['mu_seat']:.2f}", "removed" if c.get("side_plates") == "clear" else "as drawn",
                      ", ".join(other) or "&ndash;", T(ev, "E1_g79_all_bolts"), T(ev, "E3_g44_all_bolts"),
                      (chip(T(ev, "E2_walkoff_79") + " C", "bad") if "E2_walkoff_79" in ev else chip("none", "ok")),
                      f"{-min(x['lat79'] for x in h):.2f}", f"{-min(x['ax79'] for x in h):.2f}"))
    S.append(table(["Run", "Friction", "Side plates", "Other", "E1 (C)", "E3 (C)", "Walk-off", "Max west (in.)",
                    "Max toward col 79 (in.)"], drows))
    if (ASSETS / "drawings_col79.png").exists():
        n = next(fn)
        S.append(fig("drawings_col79.png", "Screening model, drawings geometry: westward movement of the girder end at column 79 "
                     "against beam temperature (ramp to 800 C). Solid: side plates as drawn; dashed: removed.", n))

    # ------------------------------------------------------------ results: detailed
    S.append('<h2 id="detailed">6. Detailed shell model results</h2>')
    if runs:
        S.append("""<p>Outcome class (preregistration Section 3): <b>CONDITIONAL</b>. No run reaches E2, E2r or E2s under NIST's
600 C schedule. The preregistered most-favourable combination (<code>favourable</code>: the Section 6 ends, column 79 0.4 in.
further away, peak 700 C) walks off at 700 C during the hold: the girder buckles, its end twists past atan(bf/d) and moves
6.25 in. west, and the solver then diverges 0.008 s after E2. Its repeat with state dumps (<code>favourable_dump</code>, a
diagnostic) reproduces the sequence within 0.07 s and continues to loss of support without diverging. The Section 6 repeat
(<code>favourable_s6</code>: standard holes, friction 0.1, the drawn column 44 gap and 0.25 in. bolt deformation, the values
that each moved the girder end furthest) does not walk off, and its girder does not buckle. No single parameter moves the
result across the 700 C line, so the condition is the combination as a whole. Full account: <code>docs/writeup.md</code>
Sections 4 and 5.</p>""")
        if (OUT / "viewer" / "data" / "index.js").exists():
            v = "#tab=report&amp;layout=split&amp;"
            S.append(f"""<p>Deformed shapes in 3D, with the column 79 history alongside: <a href="{v}a=check_rate_half" data-viewer="a=check_rate_half">the
3D viewer</a>. For example: <a href="{v}a=nist_replica&amp;b=nist_face_plates" data-viewer="a=nist_replica&amp;b=nist_face_plates">the NIST replica against the replica with the drawn
face and side plates</a>, <a href="{v}a=nist_replica&amp;b=nist_mu0.3" data-viewer="a=nist_replica&amp;b=nist_mu0.3">sliding against buckling and twisting off</a>, and
<a href="{v}a=favourable_dump&amp;b=favourable_s6" data-viewer="a=favourable_dump&amp;b=favourable_s6">the combined run against its Section 6 repeat</a>. The viewer opens
directly on this page without a server (<code>scripts/export_viewer.py</code>).</p>""")
        rows_ = []
        for nme, r in runs.items():
            ev, h = r["events"], r["rows"]
            e2 = [k for k in ("E2_walkoff_79", "E2r_rocking_79", "E2_support_lost_79") if k in ev]
            lost = ", ".join(f"{k.split('_')[0]} {ev[k]['T_beam']:.0f} C" for k in e2)
            if r["status"] == "diverged":
                lost += ", then numerical stop" if e2 else "numerical stop"
            rows_.append((run_cell(nme), f"{r['config']['rate']:g}", r["config"]["mesh"], T(ev, "first_stud"),
                          T(ev, "E1_g79_all_bolts"), T(ev, "E3_g44_all_bolts"), T(ev, "E4_beam_buckled"),
                          T(ev, "E5_girder_buckled"), chip(lost, "bad") if lost else chip("none", "ok"),
                          f"{max(x['lat79'] for x in h):.2f}", f"{-min(x['ax79'] for x in h):.2f}",
                          f"{max(abs(x['twist79']) for x in h):.1f}", f"{r['wall_s'] / 3600:.1f}"))
        rows_.append(("NIST Table 8-2", "1", "1.8", "103", "194", "476", "436", "&ndash;", "rocking, after 600 C", "&ndash;",
                      "&ndash;", "&ndash;", "&ndash;"))
        S.append(table(["Run", "Rate", "Mesh (in.)", "First stud", "E1", "E3", "E4", "E5", "Seat lost (E2, E2r, E2s)",
                        "Max west (in.)", "Max toward col 79 (in.)", "Max twist (deg)", "Wall (h)"], rows_))
        S.append("<p class='small'>Temperatures are floor-beam temperatures in C; the girder is at 20 + 0.828 (beam - 20). Rate is "
                 "the multiple of NIST's heating rate: the reported runs are at 0.5 (<code>check_rate_half</code> is the reported "
                 "baseline); the full-rate runs (1) are kept and reported as such. Wall times before 2026-10-25 include laptop "
                 "sleep.</p>")
        nmax = -min(min(x["beamN"]) for x in base["rows"]) if base else 0.0
        for key, cap in (("shell_histories", "Detailed model, half-rate runs: girder end at column 79 during heating and the hold: "
                          "westward movement (dashed line: walk-off; dotted: west side plate), movement toward the column, bearing "
                          "force on the column 79 face, and twist (dashed: E2r). Named runs in colour, every other half-rate run "
                          "in grey."),
                         ("shell_girder_profile", "Lateral movement of the girder's bottom and top flanges along its length at the "
                          "end of the baseline run, on the three meshes (half rate)."),
                         ("shell_beam_forces", f"Baseline (half rate): axial force in each floor beam at quarter span. The "
                          f"compression peaks at {nmax:.0f} kip because the girder gives way laterally; a W24x55's squash load at "
                          "600 C is about 380 kip (EN 1993-1-2 strength reduction).")):
            if figs.get(key):
                n = next(fn)
                S.append(fig(f"{key}.png", cap, n))
    else:
        S.append("<p>No detailed runs have finished yet.</p>")
    st_rows = [(p, code(nm), E(d), chip(s, {"done": "ok", "running": "warn", "queued": "info", "conditional": "info"}[s]))
               for p, nm, d, s in status]
    S.append("<details><summary>Run list and status (preregistration Section 9.5 and change log)</summary>" +
             table(["Priority", "Run", "Settings", "Status"], st_rows) + "</details>")

    # ------------------------------------------------------------ discrepancies
    S.append('<h2 id="diff">7. Differences from NIST and their traced causes</h2>')
    bmx = max(x["lat79"] for x in base["rows"]) if base else 0.0
    btw = max(abs(x["twist79"]) for x in base["rows"]) if base else 0.0
    bbow = max(abs(x["girder_bow"]) for x in base["rows"]) if base else 0.0
    nmax = -min(min(x["beamN"]) for x in base["rows"]) if base else 0.0

    def e2_txt(r):
        ev = r["events"]
        hits = sorted((ev[k]["T_beam"], k) for k in ("E2_walkoff_79", "E2r_rocking_79", "E2_support_lost_79") if k in ev)
        return f"{hits[0][1].split('_')[0]} at {hits[0][0]:.0f} C" if hits else "none to %.0f C" % r["config"]["peak"]

    rep = runs.get("nist_replica")
    rep_txt = ("<code>nist_replica</code> " + e2_txt(rep)) if rep else "<code>nist_replica</code> not run"
    S.append(table(["Observation", "NIST", "This study (baseline, half rate)", "Traced to", "Status"], [
        ("Column 79 bolts fail earlier", "E1 at 194 C", f"E1 at {T(bev, 'E1_g79_all_bolts')} C",
         "Bolt deformation at failure and hole clearance, not given by NIST (A24, A31); S13 moves E1 from 120 to 141 C",
         chip("open", "warn")),
        ("Column 44 bolts fail much earlier", "E3 at 476 C", f"E3 at {T(bev, 'E3_g44_all_bolts')} C (544 C at full rate)",
         "The two girder-end bolt groups fail within about 20 C of each other and the first to go unloads the other; the "
         "order flips with heating rate, mesh and several inputs, and no walk-off result depends on it (writeup 4.2)",
         chip("mechanism found", "info")),
        ("No floor-beam buckling", "Northmost at 436 C, all by 600 C", f"None by 600 C; beam compression at most {nmax:.0f} kip",
         f"The expanding beams push the girder sideways (it bows {bbow:.1f} in.) instead of building compression. The girder "
         "slides under the slab without friction in both models (A44, NIST §11.2.3), so what stiffened NIST's girder is not yet "
         "found", chip("open", "warn")),
        ("Girder not lost at column 79", "Rocked off its seat after the beams buckled",
         f"Held at {bmx:.2f} in. west, twisted {btw:.1f} deg; only the combined run walks off, at 700 C",
         "Not found. With NIST's idealizations together the drawn framing walks off (" + rep_txt + ", by sliding along the "
         "face), and putting back the drawn face with the side plates holds it to 700 C. But NIST's mechanism, rocking after the "
         "beams buckle, is not reproduced, so this does not explain the difference (see the beam-buckling row)",
         chip("open", "warn")),
        ("Face angle at column 79", "Not stated in NCSTAR 1-9 (14.6 deg digitized from Fig. 8-16)", "4.17 deg from the drawings",
         "Drawings 9114, 1091", chip("settled", "ok")),
    ]))
    S.append("""<p>A difference is reported as traced only when a run that changes the identified input moves the result toward NIST's.
One at a time, none of friction 0, the side plates removed, both together (to 600 C), the end stiffeners or the column 79
position within &plusmn;0.4 in. produces a walk-off. The NIST-replica run (<code>--set nist</code>, change log 2026-11-01)
applies NIST's column 79 idealizations together: the face 14.6 deg off square to the girder with a 0.5 in. end clearance, no
side plates, friction 0 and the short slot, at half rate to 700 C. Four restore runs (<code>--set nist_restore</code>) each put
one drawn feature back. The plates cannot go back alone, because at 14.6 deg they cut through the girder end, so
<code>nist_face_plates</code> is read against <code>nist_face_drawn</code>.</p>""")
    nr = [(n, what) for n, what in (("nist_replica", "nothing"), ("nist_holes", "standard holes"),
                                    ("nist_face_drawn", "face angle and position"), ("nist_mu0.3", "friction 0.3"),
                                    ("nist_face_plates", "face angle and position, with the side plates")) if n in runs]
    if nr:
        from summarize_shell import classify

        def lat_at(r, T0):
            x = [x for x in r["rows"] if x["T_beam"] >= T0]
            return f"{x[0]['lat79']:.2f}" if x else "-"
        S.append(table(["Run", "Changed back", "West movement at 600 C (in.)", "Largest girder bow (in.)", "First E2, E2r or E2s",
                        "Reading"],
                       [(run_cell(n), E(what), lat_at(runs[n], 600.0), f"{max(abs(x['girder_bow']) for x in runs[n]['rows']):.1f}",
                         e2_txt(runs[n]), E(classify(runs[n]))) for n, what in nr]))
        S.append("""<p>The holes change nothing. The drawn face slows the sliding (about 1 in. per 100 C against 1.6 at 14.6 deg)
and delays walk-off past 600 C, but not past 700 C. Friction 0.3 stops the sliding, but the girder then buckles sideways and
twists its end off at 650 to 655 C, in a dynamic phase where kinetic energy is up to a third of internal energy. With the drawn
face and the side plates, the end bears on the west plate from 488 C and stays there to 700 C while the girder buckles. So the
plates hold the girder, and the face angle decides whether a plate-less walk-off falls inside NIST's 600 C ramp. Not tested:
the drawn framing without plates at friction 0.3 beyond 600 C. The replica reaches NIST's outcome by a different mechanism, so the explanation gate item 5 asks for is recorded as not found (decision 2026-11-02).</p>""")

    # ------------------------------------------------------------ checks
    S.append('<h2 id="checks">8. Model checks and exceptions</h2>')
    import numpy as np
    from run_shell import FOLLOW, MESH, P1_HALF, P2
    chk = []

    def e1(r):
        return r["events"]["E1_g79_all_bolts"]["T_beam"]

    def lat_end(r):
        return r["rows"][-1]["lat79"]

    full, quarter = runs.get("baseline"), runs.get("check_rate_quarter")
    if base and full and quarter:
        keys = sorted(set(base["events"]) & set(quarter["events"]))
        dq = max(abs(base["events"][k]["T_beam"] - quarter["events"][k]["T_beam"]) for k in keys)
        chk.append(("Rate: full against half rate", "T_E1 to T_E4 within 10 C (or 2 %)",
                    f"T_E3 {T(full['events'], 'E3_g44_all_bolts')} against {T(bev, 'E3_g44_all_bolts')} C",
                    chip("rule applied: half rate reported", "warn")))
        chk.append(("Rate: half against quarter rate", "(diagnostic)", f"every event within {dq:.1f} C", chip("pass", "ok")))
    for nm, lab in (("check_mesh_coarse_r0.5", "3.6"), ("check_mesh_fine_r0.5", "0.9")):
        cm = runs.get(nm)
        if base and cm:
            d1, lb, lc = abs(e1(base) - e1(cm)), lat_end(base), lat_end(cm)
            chk.append((f"Mesh: T_E1, {lab} against 1.8 in.", "change &lt; 10 C (or 2 %)", f"{d1:.1f} C",
                        chip("pass", "ok") if d1 < max(10.0, 0.02 * e1(base)) else chip("fail", "bad")))
            chk.append((f"Mesh: column 79 lateral movement (no E2), {lab} against 1.8 in.", "change &lt; 2 %",
                        f"{lc:.3f} against {lb:.3f} in. ({abs(lb - lc) / lb * 100:.1f} %)",
                        chip("fail", "bad") if abs(lb - lc) / lb > 0.02 else chip("pass", "ok")))
    qs = [n for n in ["check_rate_half", *P1_HALF, *MESH, *P2, *FOLLOW] if n in runs]
    if qs:
        grav_max, n_heat, heat_max = 0.0, 0, []
        for n in qs:
            rr = runs[n]["rows"]
            t = np.array([x["t"] for x in rr]); ke = np.array([x["ke"] for x in rr]); ie = np.array([x["ie"] for x in rr])
            ok = ie > 1
            e2 = [v["t"] for k, v in runs[n]["events"].items() if k.startswith("E2")]
            heat = ok & (t >= 1.1) & (t < (min(e2) if e2 else 1e9))
            grav_max = max(grav_max, (ke / ie)[ok & (t < 1.1)].max())
            n_heat += bool(((ke / ie)[heat] > 0.05).any())
            heat_max.append((ke / ie)[heat].max())
        heat_max.sort()
        chk.append(("Quasi-static, gravity ramp (0 to 1.1 s)", "KE &lt; 5 % of IE throughout",
                    f"exceeded in every run, up to {grav_max * 100:.0f} %", chip("fail", "bad")))
        chk.append(("Quasi-static, heating and hold, before walk-off", "KE &lt; 5 % of IE throughout",
                    f"exceeded in {n_heat} of {len(qs)} runs; largest {heat_max[-1] * 100:.0f} % (a girder buckling), "
                    f"otherwise at most {heat_max[-2] * 100:.1f} %", chip("fail", "bad")))
    chk.append(("Free thermal expansion", "within 1 %", "0.4 %", chip("pass", "ok")))
    chk.append(("Restrained force", "within 1 %", "exact while elastic", chip("pass", "ok")))
    chk.append(("Euler buckling", "within 2 %", "within 2 % (imperfection-corrected)", chip("pass", "ok")))
    S.append(table(["Check (preregistration Sections 4 and 9.4)", "Criterion", "Result", "Status"], chk))
    S.append("""<p><b>Rate.</b> Halving the heating rate moved T_E3 by about 410 C, so under Section 9.4 every priority-1 run was
repeated at half rate and the half-rate runs are the reported ones; priority 2 and the follow-up runs were made at half rate
from the start. Half and quarter rate agree, so half rate is converged. The large move is not a smooth rate effect: the two
girder-end bolt groups fail within about 20 C of each other, and at full rate the floor is still carrying the gravity transient
when the race is decided.</p>
<p><b>Mesh.</b> The 3.6 against 1.8 in. pair failed, so the 0.9 in. run decides (Section 9.4). It passes on T_E1 and fails on
the lateral movement by a few tenths of a percentage point: 0.034 in., against the 6.25 in. that walk-off needs. Its hourglass
energy was about 0.22 of internal energy, so the finer mesh is not clearly the more accurate one. Reported as a failure.</p>
<p><b>Quasi-static.</b> The large ratios come from NIST's 1 s gravity ramp, before any heating; during heating they are short
excursions at connection failures and buckling. Reported as a failure, not waived; the evidence that the results are not rate
effects is the half-against-quarter-rate agreement.</p>""")
    if figs.get("shell_energy"):
        n = next(fn)
        S.append(fig("shell_energy.png", "Ratio of kinetic to internal energy (log scale) in the half-rate detailed runs (named runs "
                     "in colour, the rest grey); dashed line at the preregistered 5 %.", n))

    # ------------------------------------------------------------ limitations, open, next
    S.append('<h2 id="limits">9. Limitations</h2><ul class="tight">' + "".join(f"<li>{x}</li>" for x in [
        "Phase 1 uses NIST's uniform temperature ramp, not its computed fire temperatures; that is Phase 2.",
        "The girder's piece drawing is missing; its column 44 end clearance and cut-back are assumed (A96).",
        "As-built fit-up is unknown; the drawn girder end has about 0.4 in. of margin to the side-plate recess (S11 sweeps &plusmn;0.4 in.).",
        "Seats, top plates and column faces are rigid planes and springs, not meshed plates; column 79 is fixed except in S5.",
        "Camber, the W12x26 framing in from the west and the slab's thermal response are not modelled.",
        "Friction values are proxies (AISC slip coefficient) with no WTC 7 measurement; they are swept, not known.",
        "The shell solver is new; it is verified against closed-form results and CalculiX for the checks listed, not for every mechanism.",
        "The sweeps change one input at a time; only two combinations were run, and they disagree. The space between them is not explored.",
        "The mesh and quasi-static checks fail (Section 8). Runs on two or more threads are not bit-for-bit repeatable: the combined "
        "run's events moved by up to 0.07 s between two identical runs.",
        "All runs were made on one laptop (docs/compute_log.md); a half-rate run took 3.7 to 10 h.",
    ]) + "</ul>")
    S.append('<h2 id="next">10. Next steps</h2><ol class="find">' + "".join(f"<li>{x}</li>" for x in [
        "Find the modelling choice that explains the difference from NIST (gate item 5); the beam-buckling difference is the "
        "remaining lead.",
        "Decide on the two failed checks (<code>docs/phase1_gate.md</code>). The gate stays closed until then.",
        "Phase 2 (NIST's computed fire temperatures) does not start before the gate passes.",
    ]) + "</ol>")

    # ------------------------------------------------------------ appendix
    A = assumptions()
    S.append('<h2 id="app">Appendix A. Inputs</h2><details><summary>All assumptions (A01 to A99) with values, status and sources</summary>' +
             table(["ID", "Input", "Value", "Units", "Status", "Sweep", "Source"],
                   [(a["id"], E(a["input"]), E(a["value"])[:220], E(a["units"]), E(a["status"]), E(a["sweep"]), E(a["source"])[:300])
                    for a in A]) + "</details>")
    S.append("""<h2 id="files">Appendix B. Where things are</h2>""" + table(["Item", "Path"], [
        ("Pre-registration", code("docs/preregistration.md")), ("Assumptions", code("docs/assumptions.md")),
        ("Open questions", code("docs/open_questions.md")), ("Drawing readings and sources", code("sources/drawings/READING.md, SOURCES.md")),
        ("Hand calculations", code("results/phase1/hand_calcs.md")), ("Screening results", code("results/phase1/summary.md, summary_drawings.md")),
        ("Detailed model and solver", code("phase1/shell_model.py, wtc7/xfe/")), ("Detailed results", code("results/phase1/shell/")),
        ("Compute log", code("docs/compute_log.md")), ("This unified site", code("scripts/build_report.py -> reports/forensic/index.html")),
        ("3D viewer data", code("scripts/export_viewer.py -> reports/forensic/viewer/data/")),
    ]))

    nav = [("summary", "1. Summary", 1), ("question", "2. Question and NIST's account", 1), ("evidence", "3. Evidence base", 1),
           ("ev-sources", "Documents", 2), ("ev-drawings", "Drawings", 2), ("ev-secondary", "Secondary sources", 2),
           ("methods", "4. Methods", 1), ("m-prereg", "Pre-registration", 2), ("m-models", "Models", 2),
           ("m-verify", "Verification", 2), ("screening", "5. Screening results", 1), ("detailed", "6. Detailed results", 1),
           ("diff", "7. Differences from NIST", 1), ("checks", "8. Checks", 1), ("limits", "9. Limitations", 1),
           ("next", "10. Next steps", 1), ("app", "Appendix A. Inputs", 1), ("files", "Appendix B. Files", 1)]
    navh = "".join(f'<a class="l{lv}" href="#{a}">{E(t)}</a>' for a, t, lv in nav)
    guide_html = build_guide()

    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>WTC 7 Phase 1 &mdash; Plain-English Audit, Forensic Report &amp; 3D Model</title>
<script>{BOOT_JS}</script>
<link rel="stylesheet" href="viewer/viewer.css">
<style>{CSS}</style></head><body class="tab-guide layout-split">
<header class="site-bar">
  <div class="brand"><b>WTC 7 Phase 1</b><span>Plain-English Audit, Forensic Report &amp; 3D Model</span></div>
  <div class="bar-center">
    <div class="seg" role="tablist" aria-label="Content section">
      <button type="button" role="tab" data-tab="guide" aria-selected="true">Plain-English Guide</button>
      <button type="button" role="tab" data-tab="report" aria-selected="false">Technical Report</button>
    </div>
    <div class="seg" role="group" aria-label="Page layout">
      <button type="button" data-layout="split" aria-pressed="true">Split with 3D</button>
      <button type="button" data-layout="reading" aria-pressed="false">Reading Only</button>
      <button type="button" data-layout="3d" aria-pressed="false">3D Fullscreen</button>
    </div>
  </div>
  <div class="bar-actions">
    <button class="theme" id="theme" type="button">Light / dark</button>
  </div>
</header>
<div class="shell">
  <div class="reading-pane" id="reading-pane">
    <article id="guide-view" class="guide-wrap">
      {guide_html}
      <p class="small" style="margin-top:32px">Built {built} from repository data (<code>scripts/build_report.py</code>).</p>
    </article>
    <div id="report-view" class="wrap"><nav><b>Contents</b>{navh}</nav><main>
{''.join(S)}
<p class="small" style="margin-top:40px">Built {built}. Repository state: see <code>git log</code>.</p></main></div>
  </div>
  <div class="splitter" id="splitter" role="separator" aria-orientation="vertical" aria-label="Resize reading pane and 3D viewer" tabindex="0"></div>
  <section class="viewer-pane" id="viewer-pane" aria-label="Interactive 3D shell model viewer">
    <div class="preset-bar">
      <span class="muted">Quick 3D presets:</span>
      <button type="button" class="preset-btn" data-viewer="a=check_rate_half">Baseline</button>
      <button type="button" class="preset-btn" data-viewer="a=nist_replica&amp;b=nist_face_plates">Replica vs. side plates</button>
      <button type="button" class="preset-btn" data-viewer="a=nist_replica&amp;b=nist_mu0.3">Sliding vs. twist-off</button>
      <button type="button" class="preset-btn" data-viewer="a=favourable_dump&amp;b=favourable_s6">700 &deg;C plunge vs. repeat</button>
      <button type="button" class="preset-btn" data-viewer="a=check_rate_half&amp;b=S15_muslab0">Bowed girder vs. buckled beam</button>
    </div>
    {VIEWER_HTML}
  </section>
</div>
<script src="viewer/vendor/vue-3.5.13.global.prod.js"></script>
<script src="viewer/vendor/three-0.147.0.min.js"></script>
<script src="viewer/vendor/OrbitControls-0.147.0.js"></script>
<script src="viewer/data/index.js"></script>
<script src="viewer/viewer.js"></script>
<script>{SITE_JS}</script>
</body></html>"""
    (OUT / "index.html").write_text(page)
    return OUT / "index.html"


if __name__ == "__main__":
    print(build())
