#!/usr/bin/env bash
# The WTC 7 shop, erection and structural drawing sheets used for Q12-Q14 (NIST FOIA releases
# mirrored on archive.org) are archived in sources/drawings/raw/. This script downloads any primary
# sheet that is missing and checks each against the SHA-256 recorded in
# sources/drawings/SOURCES.md (all archived files are also in sources/SHA256SUMS). The files are untrusted data: nothing in sources/drawings/raw/ is
# executed; read them with image tools or `python -I` scripts kept elsewhere.
set -euo pipefail
cd "$(dirname "$0")/.."
RAW=sources/drawings/raw
mkdir -p "$RAW"
A=https://archive.org/download
while read -r name sha url; do
  [[ -z "$name" || "$name" == \#* ]] && continue
  if [[ ! -f "$RAW/$name" ]]; then
    curl -sSfL --retry 3 -o "$RAW/$name" "$url"
  fi
  echo "$sha  $RAW/$name" | sha256sum -c --quiet
done <<LIST
FOIA12-009_1091.TIF 21ec08cebece53dce71374eb277949830ebead253472e5c861dc25e991f73fe6 $A/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_Details_1/Detail%20Sheets%201/1091.TIF
FOIA12-009_9114.TIF 194355bd4317cd3c2d9b78e0f5401390c70b790a74647fa947512003f4e57abd $A/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_Details_2/Detail%20Sheets%202/7WTC%20-%20D2/9114.TIF
FOIA09-49_E12_13.tif 553d9223ab77a422b1aea00489c2ce26aa9acf58fc78bd15da526fdccc61c4bc $A/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/E12%2013.tif
FOIA11-209_S-8.tif 980ba280fedd1fe2bdc851c58495617c06e2fb74b8f4e3fe52eb82f91ddb82df $A/NIST_WTC7_FOIA_11-209/NIST_WTC7_FOIA_11-209/2011-09-23%2C%20WTC%207%20Structural/S-8.tif
FOIA11-209_S-8-10.tif 69fdb4ee9464b7a384f28936d8a318898707639b9b1bda7354a95e7df6414b43 $A/NIST_WTC7_FOIA_11-209/NIST_WTC7_FOIA_11-209/2011-09-23%2C%20WTC%207%20Structural/S-8-10.tif
FOIA09-49_1370.tif 602a4b8dc8406bd96a2d2d815a94fbf4d5d5a51a07899828af62dc717c8cdd72 $A/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/1370.tif
FOIA12-009_9102.TIF d56694c2c56d0e7649720b307d6538f88412e88eb9ce09824253a6275a279e6a $A/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_Details_2/Detail%20Sheets%202/7WTC%20-%20D2/9102.TIF
FOIA12-009_9100.TIF a7d2d4deb1b280ece8910ac29bd060025a755f65f53424f30801ada1e06eaed7 $A/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_Details_2/Detail%20Sheets%202/7WTC%20-%20D2/9100.TIF
FOIA09-49_3004.tif 41740f98903e4075efe74b5901780ecd8da9129ed339aee51c7b8c978f6d0fc7 $A/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/3004.tif
FOIA09-49_3005.tif 5965e63050474cb58b40db22426b674885576c274c320b03c35ba0f2e64eb4b5 $A/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/3005.tif
FOIA09-49_3016.tif f63cfa4f6a585c501af88d36944b7bedd09af098144e344dc7e3436dc945d82c $A/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/3016.tif
LIST
echo "drawings OK in $RAW"
