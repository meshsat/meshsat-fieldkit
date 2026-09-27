# c7: targeted fix of the two blocking items of "hc7 review 2" (MESHSAT-1357, layer 7, 27 September 2026)

Prototype design: nothing in the kit has been made, bought, cut, fitted or powered. This is AI work, and the reviews behind it are AI
review. Under the execution prompt of 27 September 2026 (section 4), the method changed after two failed full reviews: this pass redoes
nothing of layer 7. It fixes only the two blocking items of the second review, in the worktree `wt/hc7`, and then validates them with the
tree's own validators. Nothing was committed or pushed. Nothing was run in the main checkout. The box directory `/root/c7` was
created, used and deleted.

Every choice below was made by the session under the owner's standing rule of 26 September 2026. None is the owner's.

## Item 1. Mock-up timing made consistent in every live passage: CLOSED

**Finding (hc7 review 2, blocking 1).** After the drafts landed, four places still carried the old timing. The reviewer listed them:
- ASSEMBLY note (13) and section 3's pack paragraph: "recommended before the outlines of boards A, B, C, E and P freeze".
- READY-TO-ACT S-8: "does not gate their layout entry".
- READY-TO-ACT section 1: "the per-board path into layout" waits on nothing.
- READY-TO-ACT 6.1's first sentence: "recommends it for the build stage".
- CASE-MARGINS's "Why this document exists": "recommends before ... A, B, C, E and P are frozen for routing".

**The timing the closer adopted, which every passage now states.** It is option (b) of CASE-MARGINS section 7 as patched:
- The mock-up's checks of the rows that can move a board outline, a connector or a board part are **required before the layout entry of
  boards A, B, E and P**. These are the YES rows of `v2/docs/CASE-FIT-UNCERTAINTIES.md` section 2.
- That layout entry is BLOCKED on the owner's purchase decision (D-09). The registry carries it as FEA-007 and L-07.
- Boards C, D and E5 are not held by it.
- The other checks run at the build.

The sources are CASE-FIT sections 1, 2, 6 and 7, CASE-MARGINS section 7 and finding 28, and FEA-007 in `drafts/hc7/apply_registry.py`.

**What changed.** Each of the three patches was regenerated with `diff -u` against main `a8652172` (the old ones are kept in
`scratchpad/c7/drafts-prev/`):

- `drafts/hc7/ASSEMBLY.md.patch` (final file sha256/16 `cfe1942aa6fc8313`):
  - Note (13) now states the adopted timing and says that it replaces item (11), section 3 and the seventh revision.
  - Item (11)'s build-stage clause is marked as replaced by item (13).
  - Section 3's pack paragraph states the adopted timing. "There is no case measurement and no mock-up" becomes "no case measurement and
    no mock-up are asked of him", which is what D-08's reversal says.
  - The QMX row and the owed list were also changed (item 2).
- `drafts/hc7/READY-TO-ACT.mockup-timing.patch` (final file `ac039ca8011309bd`):
  - **Section 1.** The list now reads "the per-board path into layout up to layout entry, and layout entry itself for boards C, D and
    E5", with the correction that the layout entry of A, B, E and P waits on item 9.
  - **6.1.** The first sentence now gives the history (first the build stage, then the seventh revision, then since 27 September
    required before layout entry). The "Proceeds before it" line was split to match.
  - **S-8.** Rewritten with the adopted timing, its reason (prompt sections 2 and 5, and the review's 2A read correctly) and its
    reversal. The old sentence "`CASE-MARGINS.md` is not changed by this page" is gone, because that file now carries the same timing.
  - **Consequential edits** that follow from item 2's drawings:
    - Section 0 item 9's "Unblocks" cell now names the layout entry of A, B, E and P and cites the drawings.
    - 6.2's drawings bullet: the made parts are drawn in `v2/release/case-2026-09-27/`, and the tray's fit is open.
    - 6.4 no longer says "once drawn".
    - Section 12's drawings hand-off is updated.
- `drafts/hc7/CASE-MARGINS.md.patch`:
  - "Why this document exists" states the adopted timing (it read "recommends before ... A, B, C, E and P are frozen for routing").
  - The first paragraph's account of the seventh revision gains the 27 September change.
  - Finding 23's resolution read "now recommended before the affected outlines ... freeze". It now reads "required before the layout
    entry of boards A, B, E and P (finding 28, section 7)".
  - `CASE-MARGINS.frame_seat-draft.patch` still applies on top, 3 lines of offset. The file with both patches is `0fc449b72532ba7c`.
- `drafts/hc7/apply_registry.py`: the rebind notes for CASE-MARGINS.md and ASSEMBLY.md now also describe these timing and tray edits. No
  record, id or number changed, and the rebinds compute their sha from the file in the tree.

**Evidence.**
- A scripted audit of every "mock-up" sentence in the three patched files that mentions layout, freeze, build stage, recommend or gate.
  Two kinds of passage remain on purpose:
  - Historical passages: the seventh revision's own description, section 7's list of options (a), (b) and (c), and ASSEMBLY item (11),
    which is now marked as replaced.
  - T6: "no board's layout entry waits on it". This is consistent, because T6 closes no YES row.
- All four patches (`CASE-MARGINS.md`, `CASE-MARGINS.frame_seat-draft`, `ASSEMBLY.md`, `READY-TO-ACT.mockup-timing`) apply with
  `git apply` to `a8652172` and to `38dcd764` (main moved there during this pass: H1.1 and board B's round 8, and these three files did
  not change).

**Not changed.** The CONOPS D-06 label is a minor of the review, not a blocker. It stays with the layer 1 to 3 closers, and
`CONOPS.mockup-timing.patch` still passes `git apply --check` on `38dcd764`.

## Item 2. The QMX lid tray: STEP, STL and a dimensioned placement sheet in the case release: CLOSED

**Finding (hc7 review 2, blocking 2).**
- The rebuilt `v2/release/case-2026-09-27/` held no tray files and no sheet that drew the tray or its place.
- The only tray files were in `v2/release/revA/case/lid-bracket-qmx/`, which the HISTORICAL banner forbids anyone to make from.
- ASSEMBLY's QMX row still sent the builder there.

**What changed.**

The generator:
- `v2/cad/lid_bracket_qmx.py` (sha256/16 `67ee747c97d3cf67`). The part's numbers are now module constants and the solid is built in
  `build()`, so importing the module builds nothing.
- `PLACE_Y = (-51.5, 71.5)` is the tray's place along the case's Y. It has been unchanged since 9 September 2026: ASSEMBLY's QMX row
  gives "Y -51.5 to 71.5 in the plate frame", and `v2/cad/render/scene.py` places it at QY 10.0. The module asserts that `PLACE_Y` spans
  the part's length over its tabs (123.0).
- The geometry is untouched. On the box, with the pinned toolchain, the refactored generator's STL is byte-identical to the unrefactored
  one's (`4edf981fb42c7c6b`). It is also the same solid as revA's STL: 3260 facets, bounding box -61.5..61.5 x -34.5..34.5 x 0..28, volume
  24863.5 mm3.

The drawing and the build:
- `v2/cad/case_drawings.py` gains sheet 14, `drawings/lid-tray-qmx-drawing.pdf`, and the sheet count goes from 13 to 14. The sheet reads
  the part's constants and the solid `build()` returns, and asserts that the solid is 123.0 x 69.0 x 28.0. It asserts that
  `panel1450.QMX_TRAY_X` (102.0, 171.0) spans the part's 69.0 width. It then draws four views:
  - **A. Place on the lid, in plan.** X 102.0..171.0 (69.0) and Y -51.5..71.5 over the tabs (123.0). The four M3 hole centres are
    (106.0, -48.0), (106.0, 68.0), (167.0, -48.0) and (167.0, 68.0), on a 61.0 x 116.0 pattern. It also shows the lid's flat-ceiling edge
    at X 173.08 (M19 +2.08) and the face parts under the tray.
  - **B. Section at Y 10.0.** Lid ceiling Z 154.44 = Peli rim 108.97 + lid 45.47. The open face of the pocket is at Z 126.44 and the face
    top at 106.52, which gives M3 +19.92. It also shows M19.
  - **C. The part in plan.** 123.0 x 69.0, body 101.0, pocket 97 x 65 R3, tabs 12 x 8 x 3, 4 x d3.4 on 116.0 x 61.0, slots 3 x 18 at
    30.0, notches.
  - **D. Elevations.** Height 28.0, side walls open above the 2+6 lip over 81.0, notches 12 wide x 9.0 deep at 36.
  - Also on the sheet: the M3, M19 and M20 rows from `frame_seat.out`, tolerances, the input shas and four notes.
- `v2/cad/plate_drawing.py` prints "Sheet 1 of 14".
- `v2/cad/build_case_release.sh` builds `lid-tray-qmx/`.
- `v2/cad/README.md`: its rows for the drawings and the tray are updated.

The rebuilt release:
- `v2/release/case-2026-09-27/` was rebuilt a third time on the CAD box, 11:26:47 to 11:27:36 CEST, with `CASE_BASE_COMMIT=a8652172`,
  in a fresh venv whose `pip freeze` equals `requirements-cad.lock` line for line.
- It now holds `lid-tray-qmx/lid-bracket-qmx.step` and `.stl`, sheet 14, and `case-drawings-2-to-14.pdf`.
- The README was updated: C5's line, the Contents rows, the source revision and build, two new input rows, the CASE-FIT sha, and an open
  item for the tray's fit. The MANIFEST was written last and `sha256sum -c` passes (50 files).

Tests and pointers:
- `v2/ecad/tools/tests/test_case_geometry.py` gains `t_the_qmx_lid_tray_is_released_at_its_place`. It checks the width against
  QMX_TRAY_X, PLACE_Y against the length over the tabs, and that the hole pattern is symmetric. It shows the second build's manifest
  (without the tray) being refused and the current release passing.
- ASSEMBLY's QMX row (in the patch) now points at `v2/release/case-2026-09-27/lid-tray-qmx/` and sheet 14. It names the hole centres,
  calls revA history and states that the fit is OPEN.
- `v2/docs/CASE-FIT-UNCERTAINTIES.md` (`efc66afe9140e022`, copied into `margins/`) no longer says "this release draws every made part".
  Section 7 now says the release draws every made part of C1 to C6, the tray included, and names the pack hold-down and board E's clamp
  bar as not designed. Section 3 gains the tray's fit row.

**Evidence.**
- Box log: every generator printed DONE and the release was built. `zstack.json` was regenerated byte-identical (`b4fb79d90d2f3ee1`).
- Every STL in the release is byte-identical to the second build's. Every STEP differs only in its FILE_NAME line. Every DXF differs only
  in its dates, GUIDs and the order of its object table.
- Sheets 1 to 13 and the combined file were compared with the second build's at 50 dpi: 0 differing pixels above the title block. The
  1:1 template pages are identical everywhere, so the 1:1 scale measured in the second build still holds.
- Sheet 14 was rendered at 100 to 200 dpi and read back as an image: views A to D, the notes, the rows box, the tolerance box and the
  title block ("Sheet 14 of 14", source "tree a8652172 plus the case release's changes (fnd/hc7)", four input shas). Two layout faults
  seen in the preview were fixed before the final build: a drawn 3.0 cap height where the height is TBD, and overlapping labels.

**Found while drawing (not a blocker of this item; recorded as an open made-part item).** The tray does not fit the unit's connector
layout. Compact engineering question:

- **Issue.** The held QMX operating manual (`v2/vendor/qrp-labs/qmx-operating-manual-1_04_004.pdf`, sha256/16 `7d2616cdcadd2f7c`)
  shows the jacks on both end panels:
  - Page 7, left panel: Paddle, Audio and DC. Page 8 describes Audio and DC.
  - Page 8, right panel: RF (BNC), PTT and USB-C. Page 9 describes them.

  The tray (`lid_bracket_qmx.py`, the part of 9 September 2026) has its two cable notches in one end wall only: 12 wide, 9.0 deep from
  the open face, at +-18. The lid harness needs the DC lead (left panel), USB-C and the BNC jumper (right panel), so it cannot leave the
  tray. The notches' heights against the jacks are not checked, because the manual's panel drawings are not dimensioned. The unit's
  95 x 63 x 25 is the generator's own figure, which the held manual does not state.
- **Affected.** The tray (C5, a made part) and M3, if its depth changes. No board: the harness ends are B16 `J_QMX`, A22 `J_HF` and A22
  `J_RF2`, and none moves. No layout-entry decision and no FEA-007 row depend on it.
- **Evidence.** Sheet 14 note 4. `CASE-FIT-UNCERTAINTIES.md` section 3, new row. The manual pages above, rendered and read.
- **Options.**
  - (a) Revise the tray from the unit's enclosure drawing (the QMX assembly manual, online, not held) with an opening at each end at the
    jacks' heights, then re-read M3.
  - (b) Keep the tray and run leads with right-angle plugs out through the open side walls. This is not viable: the jacks face the end
    walls.
  - (c) Replace the tray with a strap-only mount. That loses the lip that holds the unit with the lid shut.
- **Recommendation.** (a), as desk work before the tray is printed. It does not hold the machined parts' quotes or any board.
- **Expertise or equipment.** CAD desk work. A 3D printer for PETG. T9 at the build, with the unit in the tray and the lid closed.
- **Cost and lead time.** No money for the desk step. The print is TBD. The unit is the prototype's own.

## Session choices (c7), each with its reason and reversal

1. **Where the tray's Y place lives.** `lid_bracket_qmx.PLACE_Y` holds it, not `panel1450.py`.
   - Reason: changing panel1450.py would change the sha that every sheet's title block, board C's gate reading and zstack.json carry. This
     fix must not move any other file's evidence.
   - Reversal: move it to panel1450 with its next change and re-take board C's MEC-001 there.
2. **Which way the notched end faces.** Not chosen. Sheet 14 draws the notched end where scene.py places it, with the part turned end
   for end shown dotted, and states that the hole pattern (so the lid's nuts) is the same either way.
   - Reason: the unit needs openings at both ends (the open item above), so choosing an end now would decide nothing that holds.
   - Reversal: the tray's revision (option a) fixes the orientation.
3. **How much to rebuild.** The whole case release was rebuilt a third time rather than one sheet added.
   - Reason: adding a sheet changes every sheet's "of N" and the manifest, and one build keeps one source revision for the whole folder.
   - Reversal: none needed. The geometry is proven equal file by file.
4. **Edits beyond the listed passages.** READY-TO-ACT section 0 item 9, 6.2, 6.4 and section 12, and CASE-MARGINS finding 23 and its
   first paragraph, were also edited.
   - Reason: each would otherwise have contradicted the adopted timing or the drawings that now exist (owner prompt section 6).
   - Reversal: none; they only state what the tree now holds.

## Validation with the tree's own validators

The run covered each part of the drafts:
- Scratch copies: main `a8652172` (as instructed) and main `38dcd764` (current main).
- Each copy was overlaid with this branch, with drafts steps 2 to 9 applied in APPLY order. `CONOPS.mockup-timing.patch` was left out, as
  APPLY step 6 says.
- The registry was pristine from each revision.

Results, the same on both:
- `apply_registry.py --rebind` added L-07, the next free L-number there. This pass adds no S-nn or SC-nn record.
- It added FEA-007, bound to `CASE-FIT-UNCERTAINTIES.md@efc66afe9140e022`.
- It rebound CON-006 and REQ-019 to `CASE-MARGINS.md@0fc449b72532ba7c`, and CFL-015 to `ASSEMBLY.md@cfe1942aa6fc8313` after checking
  that the Pack SMBus row and build step 7 are byte-identical.
- A second run changes nothing.
- `rules_lib.py requirements`: 133 records, 0 errors, 16 warnings. These are main's own: "git cannot say" and out/rule-audit in a tree
  without git.
- `rules_render.py --requirements --check` refuses the old REQUIREMENTS-TRACE.md, as it must after a registry change, and passes after
  `rules_render.py --requirements`.
- `run.py case_geometry frame_seat_inputs t_every_declared_writer test_gate_crash_guard test_verdict_channel test_layout_entry_stages
  test_requirements test_spacing`: 148 passed, 0 failed, 2 skipped (both need git).
- On the branch alone, `run.py case_geometry`: 11 passed. `case_geometry_check.py`: manifest OK.

`drafts/hc7/APPLY.txt` records all of this.

## Minors of review 2 not addressed here

These are outside the two blocking items and are left for the integrator:
- Drop `sources.txt.patch`'s duplicate JST line.
- Re-pin CASE-FIT's `frame_seat.out` and CASE-MARGINS shas once steps 3 and 4 land.
- Re-render the layer-4 `case-drawings.md` labels.
- Fix template sheet 4's B label overprint.
- ASSEMBLY's "RF jumpers, 11 x" row count and the superseded board names.
- The face-plate sheet's "17 x d2.6" wording.
- The CONOPS D-06 label and a session_choices record for timing choice (b).
- The partial "named spacers" acceptance.
- The FEA-004 stage conflict.

## Files

In `wt/hc7`:
- `v2/cad/lid_bracket_qmx.py`
- `v2/cad/case_drawings.py`
- `v2/cad/plate_drawing.py`
- `v2/cad/build_case_release.sh`
- `v2/cad/README.md`
- `v2/docs/CASE-FIT-UNCERTAINTIES.md`
- `v2/ecad/tools/tests/test_case_geometry.py`
- `v2/release/case-2026-09-27/`: rebuilt, with `lid-tray-qmx/`, `drawings/lid-tray-qmx-drawing.pdf` and
  `drawings/case-drawings-2-to-14.pdf`; README and MANIFEST rewritten
- `drafts/hc7/ASSEMBLY.md.patch`
- `drafts/hc7/READY-TO-ACT.mockup-timing.patch`
- `drafts/hc7/CASE-MARGINS.md.patch`
- `drafts/hc7/apply_registry.py`
- `drafts/hc7/APPLY.txt`
- this file
