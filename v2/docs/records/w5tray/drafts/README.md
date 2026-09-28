# drafts of the stream w5tray: the QMX lid tray r2 (MESHSAT-1357, S-63, EQ-24)

Branch `fnd/w5tray` from `c23c5e76`. The branch's own files (the generators, the r2 set with its manifest, the vendor documents, the
test, the CAD README) are committed on the branch. These two drafts touch shared records and pages and are applied by the integrator, in
this order, from the root of the integration tree, after the branch's files are in. Both were first drafted on 27 September 2026 for
the first pass of the design, lost with its worktree, recovered from the transcripts (`../RECOVERY.md`) and corrected the same day to
the second pass. Each asserts every old text it replaces, asserts that the new text differs, parses what it wrote, and refuses a
second run.

1. `python3 v2/docs/records/w5tray/drafts/apply_w5tray.py v2/docs/records/w5tray/drafts/ids-taken.json`
   - The registry (`v2/ecad/tools/pcb_requirements.yaml`): the next free SC-nn (drafted_as SC-TR-01) records the r2 set and closes
     S-63 (moved to closed_items, title unchanged); two next-free S-nn: the lid harness's crossing of the sealed face (not designed
     anywhere, with what it blocks) and the r2 set's verification; a header paragraph stating the difference; CFL-015, CON-006,
     REQ-019 and FEA-007 re-read and rebound to the edited ASSEMBLY.md, CASE-MARGINS.md and CASE-FIT-UNCERTAINTIES.md, the sections
     their readings cite asserted byte-identical.
   - ENGINEERING-QUESTIONS: EQ-24 answered; the next free EQ-nn for the harness crossing.
   - ASSEMBLY.md (the QMX tray row with its hardware and its torque of 0.25 N m, build steps 10 and 11, the three QMX lead rows with
     the bend radius said one way, the removal paragraph, the parts list, note (13)), CASE-FIT-UNCERTAINTIES.md section 3's QMX row,
     CASE-MARGINS.md (C5's r2 note, T8, T9, the knob height lookup), v2/README.md, v2/BUILD.md (the bill's sentence and build step 9),
     START-HERE's case release row, v2/vendor/README.md's materials row, and SOURCES.yaml's `documents_filed_w5tray` (six documents,
     every sha256 computed from the filed file).
   - The ids are the next free ones at apply time. On a copy of main `6ec37197` with this branch's files laid over it the script took
     **SC-64, S-82, S-83 and EQ-31**; the ids the first draft took on `c23c5e76` (S-81, S-82, EQ-31) are gone, main has used S-81.
2. `python3 v2/docs/records/w5tray/drafts/apply_frame_seat_r2.py`
   `v2/vendor/peli/frame_seat.py` reads the r2 stack: M3 becomes the room under the set's retaining frame, 32.30 from the ceiling,
   printed in its label; +15.62 nominal, +12.09 at the worst, +13.95 RSS low, +9.81 with unstated allowances twice, still OPEN, its
   note pointing at the r2 record's rows. M19 reads the east edge from the r2 module. No row is added, so the 70 rows and 35 OPEN do
   not move. It re-runs frame_seat.py into `frame_seat.out` and teaches `test_frame_seat_inputs.py`'s drift fixture to carry the r2
   module. If hc7's frame_seat.py draft lands first this one still applies (its anchors are the QMX lines only). **The r2 set is not
   touched by it:** the set's record prints the room (47.92, 44.39, 42.11), which is the same before and after. Then re-read
   CASE-MARGINS.md's M3 row and text and rebind what reads `frame_seat.out`.
3. `python3 v2/ecad/tools/rules_lib.py requirements`, re-render `v2/docs/REQUIREMENTS-TRACE.md`, and run
   `python3 v2/ecad/tools/tests/run.py lid_tray_qmx_r2 case_geometry frame_seat requirements`.

## What was tried, and its result

On 27 September 2026, on the runner, on a scratch copy made of main `6ec37197` (the tools, the documents, the CAD folder, the case
release, the boards and the vendor folders the tests read) with this branch's changed files laid over it:

| Step | Result |
|---|---|
| `run.py lid_tray_qmx_r2 case_geometry frame_seat` before the drafts | 24 passed, 0 failed, 0 skipped |
| `apply_w5tray.py` | SC-64, S-82, S-83, EQ-31 taken; both YAML files parse |
| `rules_lib.py requirements` before and after `apply_w5tray.py` | the same output line for line (144 records; the errors are the scratch copy's missing files, the same before and after) |
| `apply_w5tray.py` again | refuses: "already applied" |
| `apply_frame_seat_r2.py` | M3 and M19 are the only rows that change, as above; the label is whole |
| `apply_frame_seat_r2.py` again | refuses: "already applied" |
| `lid_tray_qmx_r2_check.py` before and after `apply_frame_seat_r2.py` | the same output byte for byte |
| `run.py lid_tray_qmx_r2 case_geometry frame_seat` after both drafts | 24 passed, 0 failed, 0 skipped |

Not tried: the full suite (it runs on the box, by the integrator), `rules_status.py`, the render of REQUIREMENTS-TRACE.md and the
handover packer. `test_requirements` was not judged on the scratch copy: it fails there before and after on the copy's missing files.

## For the integrator

- The LAYER-STATUS line for layer 7 is the integrator's to write: item (2) of its remaining list (the QMX lid tray) is answered by
  the r2 set; the two new open items and the new question replace it.
- **The handover ZIP's cap.** The dry build of a snapshot from `6ec37197` was 52,122,151 bytes against `max_zip_bytes` 52,428,800,
  306,649 bytes of room. The files of this branch that `pack.yaml`'s globs take (the r2 set without its STL files, the three CAD
  scripts, the test, the records, the vendor text files) compress to about 0.33 MB with deflate. The pack may pass its cap once this
  branch is in; what leaves the pack is a rule of `pack.yaml`.
- `v2/vendor/sources.txt` and `v2/vendor/vendor-status.txt` are edited on this branch by appending at the end; another stream's
  appended lines will meet them in a merge.
- `panel1450.QMX_TRAY_X` and `v2/cad/render/scene.py` still carry the r1 tray. Moving them is layer 7's single-source item:
  `test_case_geometry.t_the_qmx_lid_tray_is_released_at_its_place` ties `QMX_TRAY_X` to the r1 part's width, so the test and the
  constant change together, and sheet 14's generator with them. Not done here.
