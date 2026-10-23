#!/usr/bin/env bash
# Unpack CalculiX 2.20 (Debian bookworm packages) into tools/calculix without root, for the
# cross-check in phase1/verify_xfe.py. Requires apt-get (download only) and dpkg-deb.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p tools/debs tools/calculix
cd tools/debs
apt-get download calculix-ccx libarpack2 libspooles2.2
for d in *.deb; do dpkg -x "$d" ../calculix; done
LD_LIBRARY_PATH=$PWD/../calculix/usr/lib/x86_64-linux-gnu ../calculix/usr/bin/ccx -v | head -2
