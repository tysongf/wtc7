"""Extract NIST NCSTAR 1-9 Appendix E stress-strain tables (E-3, E-4, E-5) to CSV.

The PDF text puts two table columns side by side, so each page column is read
as its own stream. Output: data/nist/table_E{3,4,5}.csv with columns
temperature_C, true_strain, true_stress_ksi.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "sources" / "text" / "ncstar1-9.txt"
TABLES = {"E3": "Table E–3. ANSYS stress-strain model for A 36 steel.",
          "E4": "Table E–4. ANSYS stress-strain model for A 572 steel.",
          "E5": "Table E–5. ANSYS stress-strain model for CSA G40.21-44W steel."}
TOKEN = re.compile(r"TBTEMP,(\d+)|TBPT,,([0-9.eE+-]+)[ ,]+([0-9.]+)")


def parse(lines):
    left, right = [], []
    for line in lines:
        # the right-hand column starts at the second TB token on the line
        idx = [m.start() for m in re.finditer(r"TB(TEMP|PT)", line)]
        if len(idx) == 2:
            left.append(line[:idx[1]]); right.append(line[idx[1]:])
        elif len(idx) == 1:
            (left if idx[0] < 40 else right).append(line[idx[0]:])
    rows = []
    for stream in (left, right):
        temp = None
        for s in stream:
            m = TOKEN.search(s)
            if not m:
                continue
            if m.group(1):
                temp = int(m.group(1))
            else:
                rows.append((temp, float(m.group(2)), float(m.group(3))))
    return sorted(rows)


def main():
    lines = TEXT.read_text().splitlines()
    out = ROOT / "data" / "nist"
    out.mkdir(parents=True, exist_ok=True)
    for key, caption in TABLES.items():
        start = max(i for i, l in enumerate(lines) if caption in l)
        # stop at the next table caption so its first rows are not picked up
        end = next((i for i in range(start + 1, start + 120) if "Table E–" in lines[i]), start + 80)
        rows = parse(lines[start:end])
        with open(out / f"table_{key}.csv", "w") as f:
            f.write("temperature_C,true_strain,true_stress_ksi\n")
            for r in rows:
                f.write(f"{r[0]},{r[1]:.4e},{r[2]}\n")
        temps = sorted({r[0] for r in rows})
        print(key, len(rows), "points at", temps)


if __name__ == "__main__":
    sys.exit(main())
