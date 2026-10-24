# Sources (archived copies)

Every document this study downloaded is kept here, in the repository, so that the work can be
checked if the originals are moved, changed or taken down. The fetch scripts restore a missing file
from its original URL. They never overwrite an archived copy.

Check the archive:

```bash
cd sources && sha256sum -c SHA256SUMS          # every archived original below
cd tools/debs && sha256sum -c SHA256SUMS       # CalculiX packages (from the repository root)
```

All files are untrusted downloaded data. Nothing here is executed. Read the scans with image tools
or with `python -I` scripts kept outside this directory, and read the PDFs with `pdftotext`.

## What is archived

| Path | What | Original location | Retrieved (UTC) |
|---|---|---|---|
| `nist/ncstar1-9.pdf` | NIST NCSTAR 1-9, *Structural Fire Response and Probable Collapse Sequence of World Trade Center Building 7* (2008) | https://nvlpubs.nist.gov/nistpubs/Legacy/NCSTAR/ncstar1-9.pdf | 2026-10-22T06:44Z |
| `nist/ncstar1-9a.pdf` | NIST NCSTAR 1-9A, *Global Structural Analysis of the Response of World Trade Center Building 7 to Fires and Debris Impact Damage* (2008) | https://nvlpubs.nist.gov/nistpubs/Legacy/NCSTAR/ncstar1-9a.pdf | 2026-10-22T06:44Z |
| `nist/ncstar1a.pdf` | NIST NCSTAR 1A, *Final Report on the Collapse of World Trade Center Building 7* (2008) | https://nvlpubs.nist.gov/nistpubs/Legacy/NCSTAR/ncstar1a.pdf | 2026-10-22T06:44Z |
| `nist/ncstar1-3d.pdf` | NIST NCSTAR 1-3D, *Mechanical Properties of Structural Steels* (2005) | https://nvlpubs.nist.gov/nistpubs/Legacy/NCSTAR/ncstar1-3d.pdf | 2026-10-22T06:54Z |
| `errata/ncstar1-9_errata.pdf` | Combined January 2009, April 2012 and June 2012 errata to NCSTAR 1-9 | https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=901225 | 2026-10-22T06:45Z |
| `faq/wtc7_faq.html` | NIST web page "FAQs: NIST WTC 7 Investigation" as served then | https://www.nist.gov/topics/disaster-failure-studies/faqs-nist-wtc-7-investigation | 2026-10-22T06:44Z |
| `faq/wtc7diagramforfaqs_1.gif` | The diagram embedded in that page | https://www.nist.gov/sites/default/files/images/el/disasterstudies/wtc/wtc7diagramforfaqs_1.gif | 2026-10-24T02:03Z |
| `drawings/raw/` | Frankel Steel shop and erection drawings and Irwin G. Cantor structural drawings (NIST FOIA releases 09-49, 11-209 and 12-009, mirrored on archive.org), the archive.org item metadata, and four secondary documents | Per file in `drawings/SOURCES.md` | 2026-10-23, per file in `drawings/SOURCES.md` |
| `aisc/W_shapes.csv` | AISC Shapes Database W-shape table, as bundled with the Python package steelpy 1.1.1 (see `wtc7/sections.py`) | steelpy 1.1.1 on PyPI | 2026-10-22 |
| `../tools/debs/` | CalculiX 2.20 and its two libraries, Debian bookworm amd64 packages, used only by `phase1/verify_xfe.py` | `apt-get download calculix-ccx libarpack2 libspooles2.2` | 2026-10-23 |

The retrieval times for the NIST files are the file modification times written by `curl` when each
download finished.

## Made here from the archived files

These are derived, not downloaded, and are not in `SHA256SUMS`. They can be regenerated.

- `text/`: `pdftotext -layout` output of the NIST PDFs and errata, and text of the FAQ page.
  `scripts/fetch_sources.sh` regenerates it, and `scripts/extract_nist_tables.py` reads it.
- `figures/`: page renders and crops of NCSTAR 1-9 made with `pdftoppm` (file names give the PDF
  page: `p387-387.png` is page 387, `fig8-16_hi-387.png` a 300 dpi crop of Figure 8-16).
  The exception is `figure_002.jpg`, a redrawn elevation of the column 79 seat connection (girder
  end, stiffeners, bearing plate, clip angle). Where it came from was not recorded. It is not an
  original shop drawing and is not used for any reading.
- `drawings/crops/`: crops of the drawing scans cited in `drawings/READING.md`.

## Status of the material

- The NIST reports, errata and web page are works of the U.S. Government.
- The drawings were made by Frankel Steel, Steel Structures Corp. and Irwin G. Cantor and were
  released by NIST under FOIA. Third parties have mirrored them on archive.org.
- The `drawings/raw/secondary_*` files are third-party advocacy and correspondence documents
  (University of Alaska Fairbanks, AE911Truth, NIST's reply). They are kept only as the record
  behind the secondary-claims section of `drawings/READING.md`.

The repository holds them as a research archive. Check the rights before republishing any of them
outside it.
