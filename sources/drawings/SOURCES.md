# Drawing sources (Q12, Q13)

Retrieved 2026-10-23 (UTC) to answer `docs/open_questions.md` Q12 (column 79 side plates as a
lateral stop) and Q13 (bearing-face orientation). Readings are in `READING.md`; crops are in
`crops/`.

Handling: everything in `raw/` is untrusted downloaded data. Nothing in `raw/` was executed. The
scans were decoded with Pillow from scripts kept outside the repository, run as
`.venv/bin/python -I <script> <path>`; PDFs were read with `pdftotext`. The archive.org files were
checked against the SHA-1 and size listed in the archive.org item metadata (all match; metadata
saved in `raw/archive-org_metadata_*.json`).

## Where the primary scans are hosted

The Frankel Steel shop (detail) and erection drawings and the Irwin G. Cantor structural drawings
are on archive.org as single-sheet TIFFs, mirrored from three NIST FOIA releases (uploaded
2015-09-18 by TheMikeBest@gmail.com; each item also holds NIST's cover correspondence):

| archive.org item | What it holds | Item size | Bulk zip |
|---|---|---|---|
| [NIST_WTC7_FOIA_09-49](https://archive.org/details/NIST_WTC7_FOIA_09-49) | Folder "2010-10-13, WTC 7 Structural": Frankel 1091, 1370, 3004, 3005, 3016, E12 13, E120; Cantor S8, S15, S20, S24, S24A, S26; 7 photos | 62,483,937 bytes | 30,340,438 bytes |
| [NIST_WTC7_FOIA_11-209](https://archive.org/details/NIST_WTC7_FOIA_11-209) | Folder "2011-09-23, WTC 7 Structural": Cantor S-1 to S-28, S-8-10, S-8-19, S-8-20, SBR-1 to SBR-8 (request by R. Brookman, 2011-08-17) | 254,724,237 bytes | 121,942,458 bytes |
| [NIST_WTC7_FOIA_12-009](https://archive.org/details/NIST_WTC7_FOIA_12-009) | 2,772 files: Frankel detail sheets named by drawing number (0001 to 1469 in "Detail Sheets 1", 1470 to 9202 in "Detail Sheets 2"), erection sheets E1 to E123, and PDFs WTCI-000262-I to WTCI-000283-I | 2,045,671,835 bytes | 948,289,481 bytes |

Only individual sheets were downloaded; no bulk archive was downloaded. The 2000 series (girder
piece drawings, which would include the A2001 piece drawing 2001) is absent from FOIA 12-009
except for `2000.TIF`, which is a column 57 sheet.

Other places the drawings or copies were found (not downloaded):

- Metabunk attachment `9114.pdf`, https://www.metabunk.org/attachments/9114-pdf.29027/ (1,134,231
  bytes per HTTP header; a secondary copy of sheet 9114).
- 911datasets.org page cited on Metabunk for sheet 1091,
  http://911datasets.org/index.php/SFile:OQZFZY6XF4DCG6SWTREJENQFHBMHTTRV : host name did not
  resolve on 2026-10-23.
- archive.org item [911datasets](https://archive.org/details/911datasets) ("9/11 dataset - 305GB",
  328,518,615,937 bytes): over the 3 GB limit, not downloaded.
- The 2020 UAF report (downloaded, below) reproduces redrawn figures based on 9114 ("figure
  prepared by Brookman, 2012"), not original sheets; its project page
  (https://ine.uaf.edu/wtc7) lists no drawing or appendix downloads besides a 256 GB data zip.

## Downloaded files

Retrieval times are UTC. SHA-1 is listed because archive.org publishes it; every archive.org file
below matched its published SHA-1 and size.

### Primary drawings

| Local file (`raw/`) | Sheet | Source URL | Retrieved (UTC) | Size (bytes) | SHA-256 | SHA-1 |
|---|---|---|---|---|---|---|
| `FOIA12-009_1091.TIF` | Frankel 1091, Col. 79, 7th, 8th and 9th tier, rev 2 | https://archive.org/download/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_Details_1/Detail%20Sheets%201/1091.TIF | 2026-10-23T05:55:07Z | 563390 | `21ec08cebece53dce71374eb277949830ebead253472e5c861dc25e991f73fe6` | `62b92e48fcf97901985683815926ac5417ff75cf` |
| `FOIA12-009_9114.TIF` | Frankel 9114, beam to column connections, core, rev 2 | https://archive.org/download/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_Details_2/Detail%20Sheets%202/7WTC%20-%20D2/9114.TIF | 2026-10-23T05:55:09Z | 219692 | `194355bd4317cd3c2d9b78e0f5401390c70b790a74647fa947512003f4e57abd` | `524ab9c926aff4c94b70a1bd6ea4b448d59983fc` |
| `FOIA12-009_E12_13.tif` | Frankel E12/13, 12th and 13th floor framing plan, rev 4 (stored rotated 90 degrees) | https://archive.org/download/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_E_Sheets/E%20Sheets/7WTC%20-%20E1/E12_13.tif | 2026-10-23T05:55:10Z | 1539301 | `f12919bd465008cf67f3000dfddee9065077c8bab84364c11c5e1a47a3ada361` | `33c6105628a2a53fd0a31163ee6ae752909d6d58` |
| `FOIA09-49_E12_13.tif` | Frankel E12/13 (same scan, north up; used for readings) | https://archive.org/download/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/E12%2013.tif | 2026-10-23T05:55:11Z | 3087224 | `553d9223ab77a422b1aea00489c2ce26aa9acf58fc78bd15da526fdccc61c4bc` | `455ec800ba76051a8b2e6f9ba5b6c858369422bd` |
| `FOIA11-209_S-8.tif` | Cantor S-8, typical floor framing plan, 8th to 20th and 24th to 45th, rev H | https://archive.org/download/NIST_WTC7_FOIA_11-209/NIST_WTC7_FOIA_11-209/2011-09-23%2C%20WTC%207%20Structural/S-8.tif | 2026-10-23T05:55:12Z | 3032268 | `980ba280fedd1fe2bdc851c58495617c06e2fb74b8f4e3fe52eb82f91ddb82df` | `bf0541c252604980e6c68ef110acadf94b4308a2` |
| `FOIA09-49_S8.tif` | Cantor S-8 (second scan of the same sheet) | https://archive.org/download/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/S8.tif | 2026-10-23T06:26:46Z | 3115772 | `c72b3fa10c3d8f73ad7aa34444ff84b6e6bc8a3b526732a1e8ddc1c35da4391d` | `c2b3822d3124e6501794272493403d9b7009961e` |
| `FOIA11-209_S-8-10.tif` | Cantor S-8-10 (10th floor) | https://archive.org/download/NIST_WTC7_FOIA_11-209/NIST_WTC7_FOIA_11-209/2011-09-23%2C%20WTC%207%20Structural/S-8-10.tif | 2026-10-23T05:55:13Z | 3512920 | `69fdb4ee9464b7a384f28936d8a318898707639b9b1bda7354a95e7df6414b43` | `e2ddd897b17acf3589c95576e45cc7741a5dba23` |
| `FOIA09-49_1370.tif` | Frankel 1370, columns 6th and 7th tier (zone 2), column 44, rev 1 | https://archive.org/download/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/1370.tif | 2026-10-23T05:55:17Z | 159804 | `602a4b8dc8406bd96a2d2d815a94fbf4d5d5a51a07899828af62dc717c8cdd72` | `fa663fdb74c4f706b468195c770d965b46038f80` |
| `FOIA12-009_9102.TIF` | Frankel 9102, beam to column connections, north and south walls (column 44 seat), rev 4 | https://archive.org/download/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_Details_2/Detail%20Sheets%202/7WTC%20-%20D2/9102.TIF | 2026-10-23T06:10:55Z | 249266 | `d56694c2c56d0e7649720b307d6538f88412e88eb9ce09824253a6275a279e6a` | `1096b5bc2ce578aa28e375e3b11b867c9ea16a73` |
| `FOIA12-009_9100.TIF` | Frankel 9100, connection plan for 8th to 21st floor (key plan), rev 3 | https://archive.org/download/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_Details_2/Detail%20Sheets%202/7WTC%20-%20D2/9100.TIF | 2026-10-23T06:10:36Z | 318958 | `a7d2d4deb1b280ece8910ac29bd060025a755f65f53424f30801ada1e06eaed7` | `e0b8c4c21960326e51916a1f616dcccaf20e0aa0` |
| `FOIA09-49_3004.tif` | Steel Structures Corp. 3004, W24x55 beams (A3004, B3004, C3004, K3004 and others) | https://archive.org/download/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/3004.tif | 2026-10-23T05:55:15Z | 560602 | `41740f98903e4075efe74b5901780ecd8da9129ed339aee51c7b8c978f6d0fc7` | `230ba68b2cf4a7653a768e23eba1c23cacd9a834` |
| `FOIA09-49_3005.tif` | Steel Structures Corp. 3005, beams including G3005 (W21x44) | https://archive.org/download/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/3005.tif | 2026-10-23T05:55:16Z | 679834 | `5965e63050474cb58b40db22426b674885576c274c320b03c35ba0f2e64eb4b5` | `1f07d572fca1b22cb97d573b8100173a545bfa6d` |
| `FOIA09-49_3016.tif` | Steel Structures Corp. 3016, beams including P3016 (W12x26) | https://archive.org/download/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/3016.tif | 2026-10-23T05:55:17Z | 408166 | `f63cfa4f6a585c501af88d36944b7bedd09af098144e344dc7e3436dc945d82c` | `4da4ce856d95ff1d30ccff3bfc686413d8865815` |
| `FOIA09-49_E120.tif` | Frankel E120, east and west wind bracing elevations with structural steel notes | https://archive.org/download/NIST_WTC7_FOIA_09-49/NIST_WTC7_FOIA_09-49/2010-10-13%2C%20WTC%207%20Structural/E120.tif | 2026-10-23T05:55:19Z | 688016 | `5f824bba3574195afeb2f0555b6bcb9a8611dbd018e0639a0cb463afc628df24` | `2bb825d0a50e29c51f549bd172cf3ff21764fb9d` |
| `FOIA12-009_2000.TIF` | Frankel 2000 (checked because the girder piece drawing would be 2001; it is a column 57 sheet) | https://archive.org/download/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_Details_2/Detail%20Sheets%202/7WTC%20-%20D2/2000.TIF | 2026-10-23T06:10:37Z | 169830 | `30d3b204b14d82e16b6360721246fc0dcb9708ad0f6de0bc1c7e9c3e7026dc18` | `c0edffc7da8a8551aafdb2b63ec858451fe0a11e` |
| `FOIA12-009_WTCI-000271-I.PDF` | NIST-numbered greyscale scan (2 pages, 200 dpi JPEG, PDF created 2010-04-15); both pages are E10/11 (10th and 11th floor framing plan). Checked to see whether the WTCI PDFs held a better E12/13; not used for readings | https://archive.org/download/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_E_Sheets/E%20Sheets/WTCI-000271-I.PDF | 2026-10-23T06:55:54Z | 7346539 | `1fefb7c99f38b20ae3eec368486340dc4598488cd64fd77d719188d80d7a4c9a` | `0d72c1cf531cdce8a5777bbd3b281bb8105f6264` |
| `FOIA12-009_WTCI-000271-I_preview.gif` | archive.org thumbnail of the above (100 x 152 px; too small to use) | https://archive.org/download/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009/NIST_WTC7_FOIA_12-009_WTC7_E_Sheets/E%20Sheets/WTCI-000271-I.gif | 2026-10-23T06:55:44Z | 30915 | `59cddbfa909fc8a893b7ad63d99980d5281947756d6907a139efbdc092518609` | `01e18ca01b3d8dc6893c8f79e7485969455c00fb` |

### archive.org item metadata (file lists with published SHA-1)

| Local file (`raw/`) | Source URL | Retrieved (UTC) | Size (bytes) | SHA-256 |
|---|---|---|---|---|
| `archive-org_metadata_NIST_WTC7_FOIA_09-49.json` | https://archive.org/metadata/NIST_WTC7_FOIA_09-49 | 2026-10-23T06:44:22Z | 8393 | `0e590b1de46d6df7cb23e528ec2f25cc1f4fc3658a35a60facd62fa1f0171121` |
| `archive-org_metadata_NIST_WTC7_FOIA_11-209.json` | https://archive.org/metadata/NIST_WTC7_FOIA_11-209 | 2026-10-23T06:44:22Z | 17218 | `c14b655886f00c7de4b31f66621edd95347558cc78eb032e9871fc81764ba5cd` |
| `archive-org_metadata_NIST_WTC7_FOIA_12-009.json` | https://archive.org/metadata/NIST_WTC7_FOIA_12-009 | 2026-10-23T06:44:23Z | 815414 | `13f5df29c900ce39299dd0413891409128bb89adc913bbed89ce93859f117b4a` |

### Secondary documents (for the secondary-claims section of READING.md)

| Local file (`raw/`) | Document | Source URL | Retrieved (UTC) | Size (bytes) | SHA-256 |
|---|---|---|---|---|---|
| `secondary_UAF_A-Structural-Reevaluation-of-the-Collapse-of-WTC7-March2020.pdf` | Hulsey, Quan, Xiao, "A Structural Reevaluation of the Collapse of World Trade Center 7", UAF INE, March 2020 | https://files.wtc7report.org/file/public-download/A-Structural-Reevaluation-of-the-Collapse-of-World-Trade-Center-7-March2020.pdf | 2026-10-23T06:37:48Z | 45196602 | `f3a001ab68dcc6b6e230456aac4729613740336796c1b2515671141589c38bfa` |
| `secondary_AE911Truth_RFC-to-NIST-WTC7-Report-04-15-20.pdf` | AE911Truth request for correction to NIST, 2020-04-15 | https://files.wtc7report.org/file/public-download/RFC-to-NIST-WTC7-Report-04-15-20.pdf | 2026-10-23T06:36:33Z | 29676723 | `ccb2ebea1f8d4ba1759c82afb991d1860d9f3ab678007d599f7d332df6d92ae9` |
| `secondary_NIST-Response-2020-001_hosted-by-AE911Truth.pdf` | NIST initial denial of the 2020 request for correction, signed 2020-08-28 (copy hosted on an AE911Truth server) | https://casite-398799.cloudaccess.net/images/PDFs/NIST-Response-2020-001.pdf | 2026-10-23T06:43:19Z | 260407 | `472e180836bf3ab6770f31ded41493e39f06d59f1cfce5735f5892e78b4c27f5` |
| `secondary_Gage_Letter_to_Copan_2018-10-29.pdf` | R. Gage (AE911Truth) letter to the NIST Director, 2018-10-29, asking for the 2000-series girder shop drawings missing from FOIA 12-009 | https://casite-398799.cloudaccess.net/images/PDFs/Gage_Letter_to_Copan_102918.pdf | 2026-10-23T06:48:17Z | 556835 | `2566e4f41885c4875dbd04c14a8966ff0375bab795d75c79f23e98b540d1cfc1` |

Read online but not saved: the archive.org OCR text of AE911Truth's "Technical Discussion of the
NIST WTC 7 Report collapse initiation analysis and omissions" (item `TDotNISTWTC7R`, uploaded
2014-02-04), https://archive.org/download/TDotNISTWTC7R/ , and the Metabunk thread "Could Girder
A2001 Possibly Have got Past the Side Plate on Column 79?",
https://www.metabunk.org/threads/could-girder-a2001-possibly-have-got-past-the-side-plate-on-column-79.9069/
(fetched 2026-10-23).

## Notes on the copies

- Sheets 1091, 1370, 3004, 3005 and 3016 are byte-identical in FOIA 09-49 and FOIA 12-009 (same
  published SHA-1).
- The two E12/13 files are the same scan: the FOIA 12-009 file is stored rotated by 90 degrees and
  G4-compressed; after rotation it is pixel-identical to the FOIA 09-49 file over the girder area
  (Jaccard index 1.0 on a 1300 x 1600 px window). Readings use the FOIA 09-49 file.
- The two S-8 files show the same sheet (the 11-209 file is portrait, the 09-49 file landscape);
  they are not byte copies (Jaccard 0.86 on a test window, likely re-encoding). The girder area
  reads the same on both. Revision rows on the 11-209 copy: F 5-10-85, G 7-8-85, H 8-5-85.
- Scan resolution: Frankel and Steel Structures Corp. detail sheets 200 dpi bilevel (about 36 x 24
  in. sheets); E12/13 300 dpi; Cantor S sheets 400 dpi.
- The 22 PDFs WTCI-000262-I to WTCI-000283-I in the FOIA 12-009 "E Sheets" folder are NIST-numbered
  greyscale scans of erection sheets (OCR suggests WTCI-000280-I is E120). WTCI-000271-I turned out
  to be E10/11. The WTCI copy of E12/13 was not identified or downloaded; the greyscale scans look
  no more legible than the 300 dpi TIFF.
- `secondary_*` files are advocacy or correspondence documents, kept only to support the
  secondary-claims section of `READING.md`.
