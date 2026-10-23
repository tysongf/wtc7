# WTC 7 staged re-analysis

Staged finite-element models of WTC 7 to test whether fire alone reproduces NIST's
reported failure sequence and timing (NIST NCSTAR 1-9). Built only from published
material. Phases are gated: Phase 2 starts only when Phase 1 passes its gate
(`docs/preregistration.md` Section 8).

**Status (2026-10-23): Phase 1 in progress; gate not passed.**
- Hand calculations: done.
- Beam-element (plan-view) screening model: built and run (67 runs on digitized geometry, 12 on the
  drawings geometry).
- Shop, erection and structural drawings: obtained (`sources/drawings/`).
- Detailed shell model (NIST §8.8 approach, `phase1/shell_model.py`): built, verified and running
  (`docs/preregistration.md` Section 9).
- Phase 2 and Phase 3: not started.

See `docs/phase1_gate.md` and `docs/writeup.md`.

## Layout

| Path | Contents |
|---|---|
| `docs/preregistration.md` | Outcome criteria and parameter ranges, fixed before any run (hashes in `docs/compute_log.md`) |
| `docs/assumptions.md`, `.csv` | Every input, its value, range and source (generated from `wtc7/assumptions.py`) |
| `docs/open_questions.md` | What the public documents do not settle |
| `docs/compute_log.md` | Hardware, solver settings, run times |
| `docs/phase1_gate.md` | Phase 1 gate note |
| `docs/writeup.md` | Short write-up |
| `wtc7/` | Library: materials (NIST Appendix E rebuilt, EN 1993-1-2), sections, assumptions, geometry sets, plan-view solver (`fe2d.py`), explicit shell solver (`xfe/`) |
| `phase1/` | Hand calculations, beam-element model, shell model, run, verification and summary scripts |
| `tests/` | Verification tests (material tables, free and restrained expansion, buckling, contact, bolt failure) |
| `results/phase1/` | Hand-calculation sheet, run outputs, summary tables and plots |
| `data/nist/` | Appendix E stress-strain tables extracted from NCSTAR 1-9 |
| `sources/` | Checksums and the AISC W-shape table; NIST PDFs are downloaded by `scripts/fetch_sources.sh` |
| `sources/drawings/` | Readings of the Frankel and Cantor drawings (`READING.md`), their sources and checksums (`SOURCES.md`), crops; scans downloaded by `scripts/fetch_drawings.sh` |

## Software

Python 3.11, numpy 2.4.6, scipy 1.17.1, matplotlib 3.11.2, pytest (versions in
`requirements.txt`). The plan-view solver is in `wtc7/fe2d.py`. The explicit shell solver's C kernel
(`wtc7/xfe/kernel.c`) is compiled on first use with gcc and OpenMP. No commercial code is needed.
- `pdftotext` (poppler-utils) is needed only to re-extract the NIST tables.
- CalculiX 2.20 (`scripts/get_calculix.sh`, unpacked under `tools/`) is needed only for the buckling
  cross-check in `phase1/verify_xfe.py`.

## Run order

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/pip install -e .
scripts/fetch_sources.sh                      # NIST PDFs, checksums, text extraction
.venv/bin/python scripts/extract_nist_tables.py
.venv/bin/python scripts/make_assumptions_table.py
.venv/bin/python -m pytest -q tests           # verification; must pass before any run is used
.venv/bin/python phase1/hand_calcs.py         # results/phase1/hand_calcs.md
.venv/bin/python phase1/run_phase1.py --jobs 4                 # 31 primary runs
.venv/bin/python phase1/run_phase1.py --set followup --jobs 4  # 36 follow-up runs (about 6 core-hours in all)
.venv/bin/python phase1/summarize.py          # results/phase1/summary.md and plots
# drawings geometry (screening re-run)
scripts/fetch_drawings.sh                     # drawing scans used for A90 to A99
.venv/bin/python phase1/run_phase1.py --set drawings --jobs 4      # 12 screening runs, results/phase1/runs_drawings/
.venv/bin/python phase1/summarize_drawings.py # results/phase1/summary_drawings.md
# detailed shell model (preregistration Section 9)
.venv/bin/python phase1/verify_xfe.py         # buckling benchmark vs theory and CalculiX
.venv/bin/python phase1/run_shell.py --set p1 --jobs 2 --threads 2   # about 1 day on 4 cores
.venv/bin/python phase1/run_shell.py --set p2 --jobs 2 --threads 2
.venv/bin/python phase1/summarize_shell.py    # results/phase1/shell/summary.md and plots
```

A single configuration: `.venv/bin/python phase1/run_one.py <name> key=value ...`
(keys are the fields of `phase1/plan_model.py::Config`).
