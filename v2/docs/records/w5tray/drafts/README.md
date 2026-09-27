# drafts/w5tray: the QMX lid tray r2 (MESHSAT-1357, 27 September 2026, S-63, EQ-24)

Worktree `fnd/w5tray` from `c23c5e76`. The branch's own files (generators, the r2 release set, the vendor documents, the tests, the
CAD README, the release README addendum and manifest) are in the worktree, not here. These drafts touch shared records and are applied
by the integrator, in this order, from the worktree root of the integration branch, after the branch's files are in:

1. `python3 drafts/w5tray/apply_w5tray.py drafts/w5tray/ids-taken.json`
   The registry (`v2/ecad/tools/pcb_requirements.yaml`): the next free SC-nn (drafted_as SC-TR-01) records the r2 tray and closes
   S-63 (moved to closed_items, title unchanged); two next-free S-nn: the lid harness's crossing of the sealed face (not designed
   anywhere) and the r2 tray's verification; a header paragraph stating the difference; CFL-015, CON-006, REQ-019 and FEA-007 re-read
   and rebound to the edited ASSEMBLY.md, CASE-MARGINS.md and CASE-FIT-UNCERTAINTIES.md, the sections their readings cite asserted
   byte-identical. ENGINEERING-QUESTIONS: EQ-24 answered, the next free EQ-nn for the harness crossing. ASSEMBLY.md (the QMX tray row,
   build steps 10 and 11, the three QMX lead rows, the removal paragraph, the parts list, note (13)), CASE-FIT-UNCERTAINTIES.md section
   3's QMX row, CASE-MARGINS.md (C5's r2 note, T8, T9, the knob height lookup), v2/README.md, v2/BUILD.md, START-HERE's case release
   row, v2/vendor/README.md's materials row, and SOURCES.yaml's `documents_filed_w5tray` (every sha256 computed from the filed file).
   Tested on a scratch copy of `c23c5e76` plus this branch: `rules_lib.py requirements` gives exactly the output it gives without the
   draft (no new error or warning); both YAML files parse.
2. `python3 drafts/w5tray/apply_frame_seat_r2.py`
   `v2/vendor/peli/frame_seat.py` reads the r2 stack (M3 under the r2 tray's open face, 31.30 from the ceiling, printed in its label;
   M19 reads the east edge from the r2 module; no row added, so the 70 rows and 35 OPEN do not move); it re-runs frame_seat.py into
   `frame_seat.out` and teaches `test_frame_seat_inputs.py`'s drift fixture to carry the r2 module. If hc7's frame_seat.py draft lands
   first this one still applies (its anchors are the QMX lines only). Then re-read CASE-MARGINS.md's M3 row and text (M3 becomes
   +16.62 / +13.09 / +14.95 / +10.81, still OPEN on the button caps) and rebind what reads frame_seat.out.
3. `python3 v2/ecad/tools/rules_lib.py requirements`, re-render `v2/docs/REQUIREMENTS-TRACE.md`, and run
   `python3 v2/ecad/tools/tests/run.py lid_tray_qmx_r2 case_geometry frame_seat requirements` (22 of the case and tray tests pass on
   the branch alone and with step 2 applied on a scratch copy).

The LAYER-STATUS integrator line for layer 7 is the integrator's to write: item (2) of its remaining list (the QMX lid tray) is
answered by the r2 set; the two new open items and EQ-nn replace it.
