#!/usr/bin/env bash
# Unpack CalculiX 2.20 (Debian bookworm packages, archived in tools/debs/) into tools/calculix
# without root, for the cross-check in phase1/verify_xfe.py. Needs dpkg-deb; apt-get only if the
# archived packages are missing.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p tools/debs tools/calculix
cd tools/debs
ls calculix-ccx_*.deb libarpack2_*.deb libspooles2.2_*.deb >/dev/null 2>&1 || \
  apt-get download calculix-ccx libarpack2 libspooles2.2
sha256sum -c --quiet SHA256SUMS
for d in *.deb; do dpkg -x "$d" ../calculix; done
LD_LIBRARY_PATH=$PWD/../calculix/usr/lib/x86_64-linux-gnu ../calculix/usr/bin/ccx -v | head -2
