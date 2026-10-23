"""Temperature-dependent steel properties.

Two property sets, selected by name:

"NIST"  NCSTAR 1-9 Appendix E.
        E(T) from Eq. 7. Stress-strain curves are ANSYS MISO tables at
        20, 400, 450, ..., 850 C, interpolated linearly in temperature as ANSYS
        does. A36 and CSA G40.21-44W use the published Tables E-3 and E-5.
        The published A572 table (E-4) is a duplicate of E-3, so the A572 curve is
        rebuilt from Eqs. 1 to 6 with k_A572 = 1.0 and sigma_ys = 369.6 MPa
        (Appendix E). The same rebuild reproduces E-3 and E-5 (tests/test_materials.py).
        Thermal strain uses alpha = 1.4e-5 /C (NCSTAR 1-9 Section 8.7.2).

"EC3"   EN 1993-1-2:2005 Section 3.2 and Table 3.1 (reduction factors k_y, k_p, k_E),
        elliptical branch to 2 % strain, plateau beyond; thermal strain Eq. 3.1a.
        Values transcribed from the standard; not checked against a copy held in
        this repository. Room-temperature yield is taken equal to the NIST
        static yield for the same grade so the comparison isolates temperature
        dependence.

Units: ksi, strain dimensionless, temperature C.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
KSI_PER_MPA = 1.0 / 6.894757

NIST_TEMPS = np.array([20, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850], float)

# Appendix E, Table E-1
K0, K1, K2, K3 = 854.0, 4.11, 660.0, 10.27
N0, N1, N2 = 0.189, 4.099, 611.8
RATE = 1.0e-2           # strain rate used for the MISO curves, 1/s (Appendix E)
GRADES = {               # scale on K(T), static yield (MPa), Appendix E
    "A572": (1.000, 369.6),
    "A36": (0.862, 253.7),
    "G40.21": (0.941, 305.1),
}
PUBLISHED_TABLE = {"A36": "E3", "G40.21": "E5"}


def E_nist(T):
    """Young's modulus, ksi. NCSTAR 1-9 Appendix E Eq. 7 (GPa) converted."""
    T = np.asarray(T, float)
    gpa = 206.0 - 0.04326 * T - 3.502e-5 * T**2 - 6.592e-8 * T**3
    return gpa * 1000.0 * KSI_PER_MPA


def _n(T):
    return N0 * np.exp(-((T / N2) ** N1))


def _K(T, rate=RATE):
    # k3 enters through ln(rate); this reading reproduces Tables E-3 and E-5
    return K0 * np.exp(-((T / (K2 + K3 * np.log(rate))) ** K1))


def rebuilt_curve(grade, T, strains):
    """True stress (ksi) at given true strains from Appendix E Eqs. 1 to 6."""
    k, sys_mpa = GRADES[grade]
    eps_star = (sys_mpa / (k * _K(20.0))) ** (1.0 / _n(20.0))
    shift = eps_star - sys_mpa / (E_nist(20.0) / KSI_PER_MPA)
    return k * _K(T) * (np.asarray(strains) + shift) ** _n(T) * KSI_PER_MPA


def rebuilt_yield(grade, T):
    """First MISO point (strain, stress in ksi).

    At 20 C it is the static yield strength on the E line. Above that it is the
    intersection of the E(T) line with the unshifted curve k K(T) eps^n(T); this
    reproduces every first point of Tables E-3 and E-5 to 0.1 ksi, while the
    remaining points follow the shifted curve (rebuilt_curve).
    """
    from scipy.optimize import brentq
    k, sys_mpa = GRADES[grade]
    E = E_nist(T)
    if T <= 20.0:
        sy = sys_mpa * KSI_PER_MPA
        return sy / E, sy
    f = lambda e: E * e - k * _K(T) * e ** _n(T) * KSI_PER_MPA
    eps = brentq(f, 1e-7, 0.05)
    return eps, E * eps


@lru_cache(maxsize=None)
def nist_table(grade):
    """dict T -> (strain array, stress array) in the MISO format, 10 points."""
    if grade in PUBLISHED_TABLE:
        out = {}
        path = ROOT / "data" / "nist" / f"table_{PUBLISHED_TABLE[grade]}.csv"
        for r in csv.DictReader(open(path)):
            out.setdefault(float(r["temperature_C"]), []).append(
                (float(r["true_strain"]), float(r["true_stress_ksi"])))
        return {T: (np.array([p[0] for p in v]), np.array([p[1] for p in v]))
                for T, v in out.items()}
    out = {}
    for T in NIST_TEMPS:
        ey, sy = rebuilt_yield(grade, T)
        strains = np.concatenate([[ey], np.linspace(ey + 0.022, 0.2, 9)])
        stress = np.concatenate([[sy], rebuilt_curve(grade, T, strains[1:])])
        out[float(T)] = (strains, stress)
    return out


# EN 1993-1-2 Table 3.1
_EC3_T = np.array([20, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200], float)
_EC3_KY = np.array([1, 1, 1, 1, 1, .78, .47, .23, .11, .06, .04, .02, 0])
_EC3_KP = np.array([1, 1, .807, .613, .42, .36, .18, .075, .05, .0375, .025, .0125, 0])
_EC3_KE = np.array([1, 1, .9, .8, .7, .6, .31, .13, .09, .0675, .045, .0225, 0])
E20 = float(E_nist(20.0))  # ksi; same room-temperature modulus as the NIST set so S9 isolates temperature effects


def ec3_factors(T):
    return (np.interp(T, _EC3_T, _EC3_KY), np.interp(T, _EC3_T, _EC3_KP),
            np.interp(T, _EC3_T, _EC3_KE))


def ec3_stress(T, eps, fy20):
    """EN 1993-1-2 Fig. 3.1 stress-strain curve without the descending branch."""
    ky, kp, kE = ec3_factors(T)
    fy, fp, E = ky * fy20, kp * fy20, kE * E20
    ep, ey = fp / E, 0.02
    eps = np.asarray(eps, float)
    c = (fy - fp) ** 2 / ((ey - ep) * E - 2 * (fy - fp))
    a = np.sqrt((ey - ep) * (ey - ep + c / E))
    b = np.sqrt(c * (ey - ep) * E + c * c)
    mid = fp - c + (b / a) * np.sqrt(np.clip(a * a - (ey - np.minimum(eps, ey)) ** 2, 0, None))
    return np.where(eps <= ep, E * eps, np.where(eps < ey, mid, fy))


def thermal_strain(T, model):
    T = np.asarray(T, float)
    if model == "NIST":
        return 1.4e-5 * (T - 20.0)
    # EN 1993-1-2 Eq. 3.1a
    return np.where(T < 750, 1.2e-5 * T + 0.4e-8 * T**2 - 2.416e-4,
                    np.where(T < 860, 1.1e-2, 2e-5 * T - 6.2e-3))


class SteelModel:
    """Uniaxial flow description used by the fibre sections.

    For a given set and grade this provides E(T), thermal strain eps_th(T) and the
    flow stress as a function of equivalent plastic strain, sigma_f(T, eps_p),
    as piecewise-linear tables in eps_p. fy_scale applies the +/-10 % yield sweep.
    """

    def __init__(self, set_name="NIST", grade="A572", fy_scale=1.0):
        self.set_name, self.grade, self.fy_scale = set_name, grade, fy_scale
        if set_name == "NIST":
            tab = nist_table(grade)
            self._T = np.array(sorted(tab))
            self._ep, self._sf = [], []
            for T in self._T:
                eps, sig = tab[T]
                ep = np.clip(eps - sig / E_nist(T), 0, None)
                ep[0] = 0.0
                self._ep.append(ep)
                self._sf.append(sig * fy_scale)
        else:
            self._fy20 = GRADES[grade][1] * KSI_PER_MPA * fy_scale
            self._T = _EC3_T[:-1]
            grid = np.concatenate([[0], np.geomspace(1e-5, 0.2, 60)])
            self._ep, self._sf = [], []
            for T in self._T:
                E = self.E(T)
                ky, kp, _ = ec3_factors(T)
                eps = np.linspace(kp * self._fy20 / E, 0.2, 400)
                sig = ec3_stress(T, eps, self._fy20)
                ep = np.maximum.accumulate(np.clip(eps - sig / E, 0, None))
                self._ep.append(grid)
                self._sf.append(np.interp(grid, ep, sig))

    def E(self, T):
        if self.set_name == "NIST":
            return float(E_nist(T))
        return float(ec3_factors(T)[2] * E20)

    def eps_th(self, T):
        return float(thermal_strain(T, self.set_name))

    def flow(self, T, ep):
        """Flow stress and hardening slope d(sigma)/d(ep) at temperature T."""
        T = float(np.clip(T, self._T[0], self._T[-1]))
        j = int(np.searchsorted(self._T, T, side="right") - 1)
        j = min(j, len(self._T) - 2)
        w = (T - self._T[j]) / (self._T[j + 1] - self._T[j])
        out = []
        for k in (j, j + 1):
            ep_k, sf_k = self._ep[k], self._sf[k]
            s = np.interp(ep, ep_k, sf_k)
            i = min(max(int(np.searchsorted(ep_k, ep, side="right") - 1), 0), len(ep_k) - 2)
            h = (sf_k[i + 1] - sf_k[i]) / max(ep_k[i + 1] - ep_k[i], 1e-12) if ep < ep_k[-1] else 0.0
            out.append((s, h))
        return (1 - w) * out[0][0] + w * out[1][0], (1 - w) * out[0][1] + w * out[1][1]

    def fy(self, T):
        return self.flow(T, 0.0)[0]

    def flow_table(self, T, grid=np.concatenate([[0.0], np.geomspace(1e-5, 0.3, 120)])):
        """Flow stress on a fixed plastic-strain grid at T (vectorized form of flow()).

        Cached on T, since every Newton iteration within a step uses the same temperature."""
        key = round(float(T), 9)
        cache = self.__dict__.setdefault("_tables", {})
        if key not in cache:
            Tc = float(np.clip(T, self._T[0], self._T[-1]))
            j = min(int(np.searchsorted(self._T, Tc, side="right") - 1), len(self._T) - 2)
            w = (Tc - self._T[j]) / (self._T[j + 1] - self._T[j])
            sf = (1 - w) * np.interp(grid, self._ep[j], self._sf[j]) + w * np.interp(grid, self._ep[j + 1], self._sf[j + 1])
            if len(cache) > 64:
                cache.clear()
            cache[key] = (grid, sf)
        return cache[key]


def bolt_strength_factor(T):
    """Tensile-strength retention for bolts, NCSTAR 1-9 Appendix E Eq. 14, Table E-8."""
    A2, n1, n2, t1, t2 = 0.09, 5.0237, 5.0245, 478.0, 585.0
    T = np.asarray(T, float)
    return (1 - A2) * np.exp(-0.5 * ((T / t1) ** n1 + (T / t2) ** n2)) + A2
