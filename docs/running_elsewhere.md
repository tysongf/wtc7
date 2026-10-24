# Running the detailed (shell) model on another machine

The preregistered detailed-model runs (preregistration Section 9) need several days on the
original laptop (4 cores). This note covers moving them to a faster Linux machine without
changing anything that affects results.

## What has to match

- **Code and inputs:** the git commit. Record it with `git rev-parse HEAD` before starting.
- **Nothing else.** Results depend only on the code and inputs. The C kernel is compiled on
  the machine that runs it (`gcc -O3 -march=native`), so the last digits of floating-point
  results can differ between CPUs. That does not change event temperatures beyond the
  monitoring interval of 0.0025 s, about 1 C of beam temperature. Each run records its CPU,
  thread count and Python version in its JSON (`host`).

## Requirements

- Linux x86_64 or arm64.
- Python 3.11 or newer.
- gcc with OpenMP (Debian/Ubuntu: `build-essential`).
- About 2 GB of RAM per concurrent run (4 GB for the 0.9 in. mesh run) and 1 GB of disk for outputs.
- The drawing scans and NIST PDFs are not needed to run the models, only to re-read the sources.
- CalculiX is only needed for `phase1/verify_xfe.py`.

## Setup

```bash
git clone <repo> wtc7 && cd wtc7          # or copy the directory; .venv and tools/ are not needed
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/pip install -e .
.venv/bin/python -m pytest -q tests        # must pass (39 tests) before any run is used
```

Copy over the finished runs so they are not repeated:
`results/phase1/shell/runs/*.json`, `*.npz` and `results/phase1/shell/logs/`.

## Choosing jobs and threads

One run uses OpenMP threads (`--threads`). Several runs go side by side (`--jobs`). Per-run
speed stops improving at about 4 threads, so on a big machine more jobs is better than more
threads. Time one short run first:

```bash
.venv/bin/python phase1/run_shell_one.py timing_test t_end=1.2 threads=4   # gravity phase plus a little heating
```

The log shows simulated time per progress line, every 0.1 s. A full run is 4.0 s, and up to
5.7 s for the heat-cool and half-rate runs. Starting points:

| Physical cores | Suggested |
|---|---|
| 8 | `--jobs 4 --threads 2` |
| 16 | `--jobs 8 --threads 2` |
| 32 or more | `--jobs 16 --threads 2` |

Leave a core or two free. Delete the `timing_test` outputs afterwards.

## Run order

```bash
.venv/bin/python phase1/run_shell.py --set p1   --jobs 8 --threads 2 --skip-done
.venv/bin/python phase1/run_shell.py --set mesh --jobs 1 --threads 8 --skip-done   # 0.9 in. baseline, Section 9.4
.venv/bin/python phase1/run_shell.py --set p2   --jobs 8 --threads 2 --skip-done
.venv/bin/python phase1/summarize_shell.py
.venv/bin/python scripts/build_report.py
```

The 0.9 in. run is the longest, at about 8 times a 1.8 in. run. Start it early, beside the
priority-1 set, if the machine has room. `--skip-done` skips any run whose JSON already exists,
so the queue can be stopped and restarted. A run that was interrupted leaves only a log and is
rerun from the start.

Priority 2 stays on the 1.8 in. mesh. The coarse-mesh option in Section 9.5 applies only if the
mesh check passes, and it has not.

## Bringing results back

Copy `results/phase1/shell/runs/` and `results/phase1/shell/logs/` back, along with any new
lines for `docs/compute_log.md` (machine, CPU, jobs and threads, wall times). Then rebuild the
report.
