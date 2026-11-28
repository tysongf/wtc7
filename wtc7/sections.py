"""Wide-flange section properties from the AISC shapes table.

sources/aisc/W_shapes.csv is the W-shape table bundled with steelpy 1.1.1 (AISC
Shapes Database values). The two NCSTAR 1-9 values that can be checked against
it (W33x130 A = 38.3 in^2, Iy = 218 in^4; W24x55 A = 16.2 in^2, §8.7.2 and
§8.7.4) agree; tests/test_sections.py checks them.
"""
import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

CSV = Path(__file__).resolve().parents[1] / "sources" / "aisc" / "W_shapes.csv"


@dataclass(frozen=True)
class WShape:
    name: str
    A: float
    d: float
    bf: float
    tw: float
    tf: float
    Ix: float
    Iy: float
    J: float
    Cw: float
    weight: float  # lb/ft

    def plan_fibres(self, n_flange=12):
        """Fibres for weak-axis bending in plan: (y, area) arrays.

        The two flanges are lumped into strips across the flange width; the web
        is one fibre on the axis. Flange strip areas are scaled so the fibres
        reproduce the tabulated Iy, and the web fibre takes the remaining area so
        they reproduce the tabulated A (fillets included).
        """
        edges = np.linspace(-self.bf / 2, self.bf / 2, n_flange + 1)
        y = 0.5 * (edges[1:] + edges[:-1])
        a = 2 * self.tf * np.diff(edges)
        a *= self.Iy / (a * y**2).sum()
        return np.append(y, 0.0), np.append(a, self.A - a.sum())


# AISC 8th Edition (1980) W36x16.5 shapes specified on 1985 Cantor S-15 / S-23 drawings
# (superseded by W36x231..W36x302 in modern AISC tables):
_AISC8_SHAPES = {
    "W36X300": (88.3, 36.74, 16.655, 0.945, 1.680, 20300.0, 1300.0, 64.2, 398000.0, 300.0),
    "W36X280": (82.4, 36.52, 16.595, 0.885, 1.570, 18900.0, 1200.0, 52.6, 366000.0, 280.0),
    "W36X260": (76.5, 36.26, 16.550, 0.840, 1.440, 17300.0, 1090.0, 41.5, 330000.0, 260.0),
    "W36X245": (72.1, 36.08, 16.510, 0.800, 1.350, 16100.0, 1010.0, 34.6, 305000.0, 245.0),
    "W36X230": (67.6, 35.90, 16.470, 0.760, 1.260, 15000.0, 940.0,  28.6, 282000.0, 230.0),
}


@lru_cache(maxsize=None)
def shape(name):
    key = name.upper().replace(" ", "")
    if key in _AISC8_SHAPES:
        return WShape(name, *_AISC8_SHAPES[key])
    with open(CSV) as f:
        for r in csv.DictReader(f):
            if r["shape"].upper() == key:
                g = lambda k: float(r[k])
                return WShape(name, g("area"), g("d"), g("bf"), g("tw"), g("tf"), g("Ix"), g("Iy"),
                              g("J"), g("Cw"), g("weight"))
    raise KeyError(name)


def col79_section(plate_t):
    """Column 79: W14x730 with two 26 in. side cover plates across the flange tips.

    NCSTAR 1-9 Appendix D: 26 x 2 in. plates at floor 14, 26 x 3 in. at floor 5.
    Returns (A, I_min, I_y, I_x) in in^2 and in^4. Plates are parallel to the web.
    """
    w = shape("W14X730")
    b = 26.0
    x = w.bf / 2 + plate_t / 2
    A = w.A + 2 * b * plate_t
    Iy = w.Iy + 2 * (b * plate_t**3 / 12 + b * plate_t * x**2)
    Ix = w.Ix + 2 * (plate_t * b**3 / 12)
    return A, min(Ix, Iy), Iy, Ix
