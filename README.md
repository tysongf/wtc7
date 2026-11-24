# WTC 7 staged re-analysis

Staged finite-element models of WTC 7 to test whether fire alone reproduces NIST's
reported failure sequence and timing (NIST NCSTAR 1-9). Built only from published
material. Phases are gated: Phase 2 starts only when Phase 1 passes its gate
(`docs/preregistration.md` Section 8).

**Status (2026-11-02): Phase 1 detailed model complete; outcome class CONDITIONAL; gate not passed.**
- Hand calculations: done (`results/phase1/hand_calcs.md`).
- Beam-element (plan-view) screening model: built and run (67 runs on digitized geometry, 12 on the
  drawings geometry).
- Shop, erection and structural drawings: obtained (`sources/drawings/`).
- Detailed shell model (NIST §8.8 approach, `phase1/shell_model.py`): built, verified and run (65
  runs total: 41 half-rate reported runs, 3 diagnostics, 5 NIST-replica runs, 16 full-rate runs;
  `results/phase1/shell/summary.md`).
- Phase 2: not started (gated on Phase 1).
- Phase 3 (conditional global collapse given column 79 failure): pre-registered and planned
  (`docs/phase3_preregistration.md`, `docs/phase3_plan.md`), calculations not started.

See `docs/phase1_gate.md` and `docs/writeup.md`.

## Summary of findings (Phase 1)

Phase 1 tests NIST NCSTAR 1-9 §8.8 (the Floor 13 northeast partial-floor model around girder A2001 between columns 44 and 79) against published documents and FOIA-released Frankel shop/erection and Cantor structural drawings.

- **What checked out & NCSTAR 1-9 documentation quirks:**
  - *Column 79 buckling:* Hand checks agree with NIST. Under 7,525 kip gravity load, column 79 loses capacity once unbraced over ~5–6 storeys (~2,000–2,900 kip at 9 storeys).
  - *Early thermal connection failures:* The detailed shell model (~51,149 shells at NIST's 1.8 in. mesh) closely tracks NIST Table 8-2 early on: first shear stud at 101 °C (NIST: 103 °C), column 79 seat bolts at 147 °C (NIST: 154 °C), and all four column 79 erection bolts at 154 °C (NIST: 194 °C).
  - *Appendix E steel tables & Eq. 3:* NCSTAR 1-9 Table E-4 (A572 Grade 50) is a byte-for-byte duplicate of Table E-3 (A36), and Appendix E Eq. 3 prints a linear strain-rate term (`k2 + k3 * rate`) where `k2 + k3 * ln(rate)` is required to reproduce NIST's published Tables E-3 and E-5 (matching within 1.7 % and 2.8 %, vs. up to 173 % error with the printed linear term). This is a report typesetting error rather than a simulation error (the published tables match the `ln(rate)` form); A572 curves were rebuilt from Eqs. 1–6 using `ln(rate)` (`wtc7/materials.py`, `docs/open_questions.md` Q01–Q02).
- **Geometry differences between NIST's idealizations and the drawings:**
  - *Column 79 bearing-face angle:* Column 79 is rotated ~12.3 deg clockwise off the building grid, so girder A2001 meets its north flange face at 4.17 deg (7/8 in 12) off square rather than ~14.6 deg digitized from NIST Fig. 8-16 (~3.5x smaller sideways wedge thrust).
  - *Column 79 side cover plates:* Two 26 x 2 in. side plates project ~1.8 in. past the north flange face, leaving ~4.15 in. to the west plate inside the recess (less than the 6.25 in. errata walk-off distance); NIST omitted them.
  - *Other details:* Standard 15/16 in. round holes (not slots) at the column 79 top clip angle; girder end stiffeners present (omitted by NIST); no floor 13 girder studs shown (matching NIST).
- **Detailed shell model results (half-rate reported set, 51,149 shells at 1.8 in.):**
  - *No walk-off under NIST's 600 °C ramp:* Zero of the 41 half-rate runs—the baseline (1.47 in. westward movement vs. 6.25 in. needed) plus all one-at-a-time sweeps—walk off under NIST's 600 °C beam / 500 °C girder ramp.
  - *Combined runs at 700 °C:* The pre-registered "most favourable" combined run walks off during the 700 °C hold after girder buckling (reproduced in a repeat with state dumps), while the Section 6 repeat with four parameters switched to the values giving the most individual movement does not buckle or walk off (2.83 in.).
  - *NIST-replica diagnostics:* Applying NIST's column 79 idealizations together (14.6 deg face, 0.5 in. clearance, no side plates, friction 0, short slot) produces walk-off at 511 °C by sliding. Restoring drawn features one at a time: standard holes change nothing (512 °C); the drawn 4.17 deg face delays walk-off to 655 °C; friction 0.3 stops sliding, though the girder buckles and twists off dynamically at 650–655 °C; restoring the drawn face and side cover plates holds the girder through 700 °C even at zero friction (stops at 3.98 in. against the west plate).
- **Why Phase 1 has not passed its gate (caveats):**
  - The outcome class is **CONDITIONAL**, not a finding about the collapse or a refutation of NIST.
  - *Unexplained mechanism mismatch (gate item 5):* No floor beam buckles in our baseline (expanding beams bow the girder 4.3 in. sideways instead, vs. NIST beam buckling at 436 °C followed by rocking), and even the NIST-replica run walks off by sliding without beam buckling.
  - *Two failed numerical checks (gate item 3):* The 0.9 in. vs. 1.8 in. mesh check missed the 2 % lateral-displacement limit (2.3 %, or 0.034 in. out of 6.25 in., with higher hourglass energy on the finer mesh), and KE/IE exceeded the 5 % quasi-static ceiling during the gravity ramp and brief heating transients (though half- and quarter-rate baselines agree within 3 °C on every event).

## Layout

| Path | Contents |
|---|---|
| `docs/preregistration.md` | Outcome criteria and parameter ranges, fixed before any run (hashes in `docs/compute_log.md`) |
| `docs/phase3_preregistration.md`, `docs/phase3_plan.md` | Phase 3 conditional global-collapse criteria and plan (draft) |
| `docs/assumptions.md`, `.csv` | Every input, its value, range and source (generated from `wtc7/assumptions.py`) |
| `docs/open_questions.md` | What the public documents do not settle |
| `docs/compute_log.md` | Hardware, solver settings, run times |
| `docs/phase1_gate.md` | Phase 1 gate note |
| `docs/running_elsewhere.md` | Moving the detailed-model runs to another machine |
| `reports/forensic/` | Forensic report web page (built by `scripts/build_report.py`) |
| `reports/forensic/viewer/` | 3D viewer of the detailed-model runs (data from `scripts/export_viewer.py`; Vue 3.5.13 and Three.js 0.147.0 vendored in `vendor/` with checksums); opens from `file://` |
| `docs/writeup.md` | Short write-up |
| `wtc7/` | Library: materials (NIST Appendix E rebuilt, EN 1993-1-2), sections, assumptions, geometry sets, plan-view solver (`fe2d.py`), explicit shell solver (`xfe/`) |
| `phase1/` | Hand calculations, beam-element model, shell model, run, verification and summary scripts |
| `tests/` | Verification tests (material tables, free and restrained expansion, buckling, contact, bolt failure) |
| `results/phase1/` | Hand-calculation sheet, run outputs, summary tables and plots |
| `data/nist/` | Appendix E stress-strain tables extracted from NCSTAR 1-9 |
| `sources/` | Archived copies of every downloaded source (NIST reports, errata, FAQ page, drawing scans), checksums (`SHA256SUMS`), extracted text and figures; see `sources/README.md` |
| `sources/drawings/` | Readings of the Frankel and Cantor drawings (`READING.md`), their sources and checksums (`SOURCES.md`), crops, and the scans themselves (`raw/`) |

## Software

Python 3.11, numpy 2.4.6, scipy 1.17.1, matplotlib 3.11.2, pytest (versions in
`requirements.txt`). The plan-view solver is in `wtc7/fe2d.py`. The explicit shell solver's C kernel
(`wtc7/xfe/kernel.c`) is compiled on first use with gcc and OpenMP. No commercial code is needed.
- `pdftotext` (poppler-utils) is needed only to re-extract the NIST tables.
- CalculiX 2.20 (Debian packages archived in `tools/debs/`, unpacked by `scripts/get_calculix.sh`) is needed only for the buckling
  cross-check in `phase1/verify_xfe.py`.

## Run order

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/pip install -e .
scripts/fetch_sources.sh                      # checks the archived sources, extracts text
.venv/bin/python scripts/extract_nist_tables.py
.venv/bin/python scripts/make_assumptions_table.py
.venv/bin/python -m pytest -q tests           # verification; must pass before any run is used
.venv/bin/python phase1/hand_calcs.py         # results/phase1/hand_calcs.md
.venv/bin/python phase1/run_phase1.py --jobs 4                 # 31 primary runs
.venv/bin/python phase1/run_phase1.py --set followup --jobs 4  # 36 follow-up runs (about 6 core-hours in all)
.venv/bin/python phase1/summarize.py          # results/phase1/summary.md and plots
# drawings geometry (screening re-run)
scripts/fetch_drawings.sh                     # checks the archived drawing scans used for A90 to A99
.venv/bin/python phase1/run_phase1.py --set drawings --jobs 4      # 12 screening runs, results/phase1/runs_drawings/
.venv/bin/python phase1/summarize_drawings.py # results/phase1/summary_drawings.md
# detailed shell model (preregistration Section 9)
.venv/bin/python phase1/verify_xfe.py         # buckling benchmark vs theory and CalculiX
.venv/bin/python phase1/run_shell.py --set p1 --jobs 2 --threads 2   # about 1 day on 4 cores
.venv/bin/python phase1/run_shell.py --set p2 --jobs 2 --threads 2
.venv/bin/python phase1/summarize_shell.py    # results/phase1/shell/summary.md and plots
.venv/bin/python scripts/export_viewer.py     # 3D viewer data, reports/forensic/viewer/data/ (about 15 s)
.venv/bin/python scripts/build_report.py      # reports/forensic/index.html
```

A single configuration: `.venv/bin/python phase1/run_one.py <name> key=value ...`
(keys are the fields of `phase1/plan_model.py::Config`).
