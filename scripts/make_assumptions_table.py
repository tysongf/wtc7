"""Render wtc7/assumptions.py to docs/assumptions.md and docs/assumptions.csv."""
import csv
from pathlib import Path

from wtc7.assumptions import ASSUMPTIONS

ROOT = Path(__file__).resolve().parents[1]


def show(v):
    if isinstance(v, float):
        return f"{v:g}"
    if isinstance(v, (tuple, list)):
        return ", ".join(show(x) for x in v)
    if isinstance(v, dict):
        return "; ".join(f"{k}: {show(x)}" for k, x in v.items())
    return str(v)


def main():
    rows = [dict(id=a.id, input=a.name, value=show(a.value), units=a.units, status=a.status,
                 sweep=a.sweep_id + (": " + show(a.sweep) if a.sweep else ""), source=a.source, note=a.note)
            for a in ASSUMPTIONS]
    with open(ROOT / "docs" / "assumptions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    lines = ["# Assumptions table (Phase 1)\n",
             "Generated from `wtc7/assumptions.py` by `scripts/make_assumptions_table.py`; the model reads the same list, "
             "so this table is what was run. Status: **report** = NIST NCSTAR 1-9, 1-9A, 1A, errata or FAQ; "
             "**drawing** = read from a drawing reproduced in NCSTAR 1-9; **standard** = published standard, not "
             "checked against a copy in this repository; **secondary** = secondary source, unverified; **assumed** = "
             "no published value, best guess (swept where it can matter).\n",
             "| ID | Input | Value | Units | Status | Sweep | Source | Note |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| " + " | ".join(r[k].replace("|", "/") for k in r) + " |")
    (ROOT / "docs" / "assumptions.md").write_text("\n".join(lines) + "\n")
    print(f"{len(rows)} assumptions written")


if __name__ == "__main__":
    main()
