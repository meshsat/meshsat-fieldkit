# Stream od01b: running log (MESHSAT-1357, 29 September 2026)

Author: one AI session (Claude), worktree `od01b`, branch `fnd/od01b` from `40dd2690`. Brief: the owner's instruction of 29
September 2026 on OD-01 (R4, R5, R6) and the outside AI review of the package. Prototype: nothing here is bought, made, sent
or measured. Times are CEST.

| Time | What |
|---|---|
| 01:26 | Start. Read the brief, WORKER-RULES, the four OD-01 files, checks 1 and 2, the case release README and manifest, `face_plate.py`, `plate_drawing.py`, `panel1450.py`, `drawing_kit.py`, `POWER-THERMAL.md` section 10, `CASE-MARGINS.md` sections 2, 5 and 7. |
| 01:30 | Box reachable; a CAD venv matching the lock is on it (build123d 0.13.0, ezdxf 1.4.4, matplotlib 3.11.2). This host has matplotlib and reportlab but no ezdxf or build123d, so the DXF, STEP and STL of H1 are generated on the box under `/root/od01b/` only. |
| 01:32 | Arcol "HS Aluminium Housed Resistors" sheet 12/14.08 fetched (RS copy, the same bytes the independent check read) and filed as `v2/vendor/arcol/arcol-hs-datasheet-12-14-08.pdf` with `v2/vendor/arcol/sources.txt`. |
| 01:40 | Wrote `v2/cad/h1_heat_test_plate.py` (H1's features from `panel1450.py`, the HS100 pattern from Arcol's page 2, DXF, STEP, STL and a parsing check against the released C1 DXF) and `v2/cad/h1_heat_test_plate_drawing.py` (sheet H1-1). Rendered the sheet on this host and read it back (AI read-back): two label overlaps fixed. |
| 01:29 | Box run at `c0ec7684` (bundle against the box's main `82dd1e4d`, clone under `/root/od01b/repo`, the venv's `pip freeze` equal to the lock): `h1_heat_test_plate.py` wrote DXF, STEP, STL and the check (RESULT PASS, 15 checks: outline, rebate, relief and the ten screw holes equal the released C1 DXF within 0.001 mm; the pattern 37.0 (X) by 35.0 (Y) at (-45.0, 70.0); the HS100 footprint 2.92 mm inside the frame window); the drawing wrote sheet H1-1. Box image read back (AI read-back): legible, figures as the check. |
| 01:31 | Release folder `v2/release/case-2026-09-27/h1-heat-test-plate/` with its README and its own `MANIFEST.sha256` (the r2 convention; the release's manifest untouched, session choice 4 of that README). PEM's S bulletin not reachable (404, Archive 404): S-M3-2 labelled INFERRED. |
| 01:50 | **Correction found in the source.** Arcol's page 2 drawing puts the dimension L (4.4 +-0.25 for the HS100, 3.2 +-0.25 for the HS50) on the mounting hole; the "3.2 max." sits at the solder tag. The independent check (check-1, B1) and the RFQ read the HS100's mounting holes as 3.2 max: they are 4.4 +-0.25, so an M3 floats at least 0.5 and the tolerance stack the first render worried about does not arise. Both scripts and the H1 README corrected; box re-run owed. |
| 01:34 | Box re-run at `b8880536`: check RESULT PASS, 15 checks (only the script's own hash line moved); the STL bytes identical to the first build, DXF and STEP differ in their time stamps only. Section and note 2 of sheet H1-1 read back from the box image (AI read-back). Folder README and manifest re-written. |
