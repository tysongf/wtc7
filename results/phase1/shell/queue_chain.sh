#!/usr/bin/env bash
# After the p1_half queue (pid 2656741) exits: the 0.9 in. mesh run on 4 threads, then priority 2.
cd /home/tyson/Projects/wtc7
while kill -0 2656741 2>/dev/null; do sleep 60; done
.venv/bin/python phase1/run_shell.py --set mesh --jobs 1 --threads 4 --skip-done >> results/phase1/shell/mesh_queue.log 2>&1
.venv/bin/python phase1/run_shell.py --set p2 --jobs 2 --threads 2 --skip-done >> results/phase1/shell/p2_queue.log 2>&1
