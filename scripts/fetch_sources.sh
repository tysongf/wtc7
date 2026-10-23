#!/usr/bin/env bash
# Download the public NIST documents used to build the model, check them against
# sources/SHA256SUMS, and extract text for scripts/extract_nist_tables.py.
# Needs curl, sha256sum and pdftotext (poppler-utils).
set -euo pipefail
cd "$(dirname "$0")/../sources"
mkdir -p nist errata faq text
base=https://nvlpubs.nist.gov/nistpubs/Legacy/NCSTAR
for f in ncstar1-9 ncstar1-9a ncstar1a ncstar1-3d; do
  [ -s nist/$f.pdf ] || curl -fsSL --max-time 600 -o nist/$f.pdf "$base/$f.pdf"
done
# combined January 2009, April 2012 and June 2012 errata to NCSTAR 1-9
[ -s errata/ncstar1-9_errata.pdf ] || curl -fsSL -o errata/ncstar1-9_errata.pdf \
  "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=901225"
# FAQ page (HTML changes over time, so it is not checksummed)
curl -fsSL -o faq/wtc7_faq.html "https://www.nist.gov/topics/disaster-failure-studies/faqs-nist-wtc-7-investigation" || \
  echo "warning: FAQ page not downloaded"
sha256sum -c SHA256SUMS
for f in nist/*.pdf; do pdftotext -layout "$f" "text/$(basename "$f" .pdf).txt"; done
pdftotext -layout errata/ncstar1-9_errata.pdf text/ncstar1-9_errata.txt
echo "sources ready"
