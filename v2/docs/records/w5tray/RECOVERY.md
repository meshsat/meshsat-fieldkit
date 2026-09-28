# The w5tray stream recovered (MESHSAT-1357, 27 September 2026)

Pre-PCB layer 7, open item S-63 and ENGINEERING-QUESTIONS EQ-24: the QMX lid tray r2. Prototype design: nothing here has been made,
printed, bought or fitted.

## What happened

The first author pass (27 September 2026, 18:36 to 19:52 CEST) designed the r2 tray in a worktree under `/tmp`, committed nothing, and a
reboot deleted the worktree. An independent checker had judged that pass NOT mergeable with two blocking items (B1, the unit cannot be
fitted; B2, the face-room limits are wrong); a second author pass had run seven read-only commands when the work was lost. What survived
is the agents' transcripts: every file written with the editor, every shell command with its output, and the two result records.

This file says what was recovered, what was regenerated and what was lost. The state recovered here is pass 1 as the checker saw it:
**unchecked, and known NOT to be mergeable**; it is commit `fb4a52eb` of this branch. The answers to B1 and B2 are later commits on
this branch (`README.md` beside this file), which rewrite the three CAD scripts, the test, the set's README and both drafts.

## Recovered (byte for byte, proved by sha256)

Ten files were written with the editor and are in the transcript whole. Six of them were then changed by shell commands (small Python
patches and `sed` lines), which the transcript also holds. `recovery/replay.py` re-ran those 20 commands in transcript order on the
written files (`recovery/parse_log.py` splits the shell log into its commands). The result is checked against the sha256 the first pass
itself printed at three points of its session:

| File | sha256 (16) after the replay | The first pass printed | Where it printed it |
|---|---|---|---|
| `v2/cad/lid_tray_qmx_r2.py` | `3e89a3ca4d3d1d3b` | `3e89a3ca4d3d1d3b` | input hashes at 17:31 and 17:48 UTC; the checker's own copy on the box |
| `v2/cad/lid_tray_qmx_r2_check.py` | `78c625d64341bd6b` after its fourth patch, `6810035b92416788` after its fifth and last | the same two | input hashes at 17:31 and at 17:48 UTC |
| `v2/cad/lid_tray_qmx_r2_drawing.py` | `21287961b3f5dd2a` | `21287961b3f5dd2a` | input hashes at 17:31 and 17:48 UTC |
| `v2/vendor/qrp-labs/measure_qmx_figures.py` | `792aa80d828329ab` | `792aa80d828329ab` | input hashes at 17:31 UTC |

The other recovered files have no printed digest to compare with; they are the written text with the transcript's commands applied, each
command's patch asserted to have changed the file:

| File | Made of |
|---|---|
| `v2/cad/build_lid_tray_r2.sh` | a shell here-document, then two `sed` lines (the read-back folder renamed to a dot folder) |
| `v2/cad/README.md`, `v2/cad/build_case_release.sh` | the tree's files at `c23c5e76` with the first pass's two patches |
| `v2/ecad/tools/tests/test_lid_tray_qmx_r2.py` | written, then two patches |
| `v2/release/case-2026-09-27/lid-tray-qmx-r2/README.md` | written and edited once; its last refresh of the input hashes is NOT replayed, because the generated files it names are regenerated below and the folder's README is rewritten for the answered design |
| `v2/vendor/materials/README.md` | written, unchanged |
| `drafts/apply_w5tray.py`, `drafts/apply_frame_seat_r2.py`, `drafts/README.md` | written under `drafts/w5tray/` of the lost worktree, then seven patches; moved here because a worker keeps no `drafts/` folder outside its records. As recovered they are in commit `fb4a52eb`; the files here now are corrected to the second pass |
| `pass1/RESULT-w5tray-author-1.json`, `pass1/RESULT-w5tray-check-1.json` | the first author's and the checker's result records, as the transcripts hold them |

## Fetched again (makers' documents)

Fetched by curl from the runner on 27 September 2026, 20:53 UTC, from the URLs the first pass used, and compared with the sha256 the
first pass recorded:

| File | URL | sha256 now | Against the first pass |
|---|---|---|---|
| `v2/vendor/materials/prusament-pc-blend-tds-v1.1-2022-02-16.pdf` | https://prusament.com/wp-content/uploads/2022/10/PCBlend_Prusament_TDS_2022_16_EN.pdf | `25f7aa7b99cc24e5` | identical |
| `v2/vendor/materials/prusament-petg-tds-v1.1-2022-02-16.pdf` | https://prusament.com/wp-content/uploads/2022/10/PETG_Prusament_TDS_2021_10_EN.pdf | `0159322f3d14300f` | identical |
| the whole assembly manual 1.04r (16 MB, not filed) | https://qrp-labs.com/images/qmx/manuals/assembly_1_04r.pdf | `55c08baaf6ca5fb2` | identical |
| `v2/vendor/qrp-labs/qmx-assembly-1_04r-pages-1-3-20-21-75-78.pdf` | derived from it with Ghostscript 10.00.0, the first pass's command | `ece9bed53713d5fa` | **DIFFERENT**: the first derivation was `4ef0119f832677b2`, 6 bytes shorter. Ghostscript writes its run time into the file. The source is identical, the command is the same; the first derivation itself is lost. |
| `v2/vendor/qrp-labs/qmx-product-photo-qmx4-right-panel.jpg` | https://qrp-labs.com/images/qmx/1/qmx4.jpg | `4eab70ca5c51f1d3` | identical |
| the product page HTML (not filed) | https://qrp-labs.com/qmx.html | `7da9d31b052540e1` | **DIFFERENT**: the first fetch was `377a906c03afe46a`, the same 105306 bytes long. The page carries a hit counter (1272916 now, 1272616 then) and the difference is not the counter alone: the HTML with the counter set back does not give the first digest. |
| `v2/vendor/qrp-labs/qmx-product-page-2026-09-27.txt` | the text extraction of that page | `ea72e0782d8ef822` | identical, by this proof: the second fetch's extraction differs from the first in the hit counter's line only; with that line set back to 1272616 and the first pass's header, it gives the first pass's digest. The file filed is that one, so it names the first fetch in its header. |
| `v2/vendor/qrp-labs/qmx-crops/opman-1_04_004-p7-left-panel.png`, `-p8-right-panel.png`, `-p13-top-face.png` | extracted from the held operating manual with `pdfimages` (poppler 22.12.0) | `8dfa27e73a1dc8a3`, `499221502290d6c0`, `767f10f3d868906a` | identical |

PORON 4701-30: the first pass fetched nothing. It read the sheet the tree already holds,
`v2/vendor/seals/rogers-poron-4701-30-very-soft.pdf` (`9567c83b0d8d9e97`, the digest the first pass recorded), and so does this pass. The
same holds for `v2/vendor/adhesives/3m-scotch-weld-dp8005.pdf` (`90fdb06a6289827e`) and the operating manual (`7d2616cdcadd2f7c`).

`v2/vendor/sources.txt` and `v2/vendor/vendor-status.txt` carry the lines for these files (both fetches named).

## Regenerated (by running the recovered scripts)

| Output | How | Result |
|---|---|---|
| `v2/vendor/qrp-labs/qmx-figures.out` | `measure_qmx_figures.py` on the runner (Pillow 12.2.0, numpy 2.4.4) | `ec891c826be2d19b`, the first pass's digest |
| the r2 set of pass 1 (STL, STEP, DXF, the record, the sheets) | section "The faithful rebuild" below | see there |

## Not recovered, by decision

- **The first pass's edits of `v2/release/case-2026-09-27/README.md` and `MANIFEST.sha256`** (an addendum and nine manifest lines) are in
  the transcript and are NOT re-applied. They edited files of a released folder that the H2 snapshot had bundled, and the checker's
  minor item 6 found the addendum contradicting itself. The r2 set carries its own `MANIFEST.sha256` and its own README; the release's
  two files keep their bytes (session decision, reason: a release folder is an immutable copy, `test_case_geometry.py`; reverse by the
  integrator cutting a new dated case release that lists r2 in its manifest).

- **The first pass's one line in `v2/cad/build_case_release.sh`** (it chains the r2 build into the case release build) and its rows in
  `v2/cad/README.md` ARE re-applied, the rows rewritten for the second pass: neither file is part of a release.

## Lost

- The first pass's copies of the generated outputs (the files themselves; their digests are in the transcript and are compared below).
- The first fetch's HTML of the product page and the first Ghostscript subset of the assembly manual (see the table above).
- The first pass's scratch files that were never in its worktree: its trial renders, the page images of its read-back, its scratch copies
  for testing the drafts, the checker's `insertion_check.py` and `buttons_under.py` (both are in the checker's transcript as here-documents;
  this pass writes its own checks into `lid_tray_qmx_r2_check.py`, so they are not filed).
- The second author pass had written nothing.
- The transcripts themselves are not filed in this repository: they name the rented box's address. They stay on the runner under
  `~/worktrees/meshsat-fieldkit/_recovered/`.

## The faithful rebuild

Before anything was changed, the recovered scripts of commit `fb4a52eb` were built on the rented box (Ubuntu 24.04.5 LTS, Python 3.12.3,
x86_64) under `/root/w5tray/`, in a fresh venv installed from `v2/cad/requirements-cad.lock` (`pip freeze` equals the lock line for line;
build123d 0.13.0), from a sparse clone of this branch (a git bundle on the box's own repository). `v2/cad/build_lid_tray_r2.sh` ran twice
(27 September 2026, 20:58:03 to 20:58:19 and 20:58:19 to 20:58:36 UTC, `CASE_BASE_COMMIT=c23c5e76`):

| Output | sha256 (16), both runs | The first pass's digest | |
|---|---|---|---|
| `lid-tray-qmx-r2.stl` | `02d9a3d9177d8265` | `02d9a3d9177d8265` | identical |
| `lid-tray-qmx-r2-keeper.stl` | `26bac195260fb986` | `26bac195260fb986` | identical |
| `lid-tray-qmx-r2-check.out` (with `--solids`) | `1b0d7f6a930bf943` | `1b0d7f6a930bf943` | identical |
| the three STEP files, the DXF, the PDF | differ between the two runs, and from the first pass | | as the first pass found: a STEP carries its time stamp, the DXF its dates, the PDF its creation date |

Those are the three digests the checker reproduced on its own rebuild, so the recovered scripts are the ones the checker judged. The
record is filed as `pass1/lid-tray-qmx-r2-check.out` with both runs' digests (`pass1/rebuild-a.sha256`, `pass1/rebuild-b.sha256`); the
first pass's solids and sheets are not filed, because the checker found that design NOT mergeable (the unit cannot be fitted into it) and
the released set of this branch is the answered design.
