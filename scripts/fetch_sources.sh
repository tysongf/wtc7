#!/usr/bin/env bash
# The NIST documents are archived in the repository (sources/nist, errata, faq). This script
# downloads any that are missing, checks them against sources/SHA256SUMS, and extracts text for
# scripts/extract_nist_tables.py. It never overwrites an archived file.
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
# FAQ page as retrieved 2026-10-22T06:44Z; the live page changes, so the archived copy is kept
[ -s faq/wtc7_faq.html ] || curl -fsSL -o faq/wtc7_faq.html "https://www.nist.gov/topics/disaster-failure-studies/faqs-nist-wtc-7-investigation" || \
  echo "warning: FAQ page not downloaded"
[ -s faq/wtc7diagramforfaqs_1.gif ] || curl -fsSL -o faq/wtc7diagramforfaqs_1.gif \
  "https://www.nist.gov/sites/default/files/images/el/disasterstudies/wtc/wtc7diagramforfaqs_1.gif" || \
  echo "warning: FAQ diagram not downloaded"
sha256sum -c --quiet SHA256SUMS
for f in nist/*.pdf; do pdftotext -layout "$f" "text/$(basename "$f" .pdf).txt"; done
pdftotext -layout errata/ncstar1-9_errata.pdf text/ncstar1-9_errata.txt
echo "sources ready"
