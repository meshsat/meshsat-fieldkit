# Stream w5tray: the QMX lid tray r2 (MESHSAT-1357, pre-PCB layer 7, S-63, EQ-24)

Branch `fnd/w5tray` from `c23c5e76`. Prototype design: nothing here has been made, printed, bought or fitted. AI work and AI review
only; no qualified mechanical engineer has looked at it. This is the second and last pass of the author and checker loop.

| Here | What |
|---|---|
| `RECOVERY.md` | what was recovered from the transcripts of the first pass, what was fetched again, what was regenerated, what was lost |
| `pass1/` | the first author's and the checker's result records, and the record and digests of the first pass rebuilt from the recovered scripts |
| `recovery/` | the two small tools that replayed the first pass's shell patches |
| `drafts/` | the registry and document changes and the `frame_seat.py` change, for the integrator, with what was tried |
| `../../../release/case-2026-09-27/lid-tray-qmx-r2/` | the set: three made parts, three sheets, the record, its README and its own manifest |

## The checker's two blocking items, and the answers

**B1, the unit cannot be fitted into the r2 tray as drawn.** True of the first pass: its keeper-end lintel covered x -50.5 to -47.5 over
the full width at z 27.1 to 29.1, the height of the unit's top face, and the unit was to slide in under it with its knobs on.

- The design changed: the unit is lowered into an open pocket from above, and a flat retaining frame is screwed over it (six M3 x 10
  into square nuts in the posts). Sliding the unit in was given up altogether, not only the lintel: a unit slid in under ledges has to
  pass over the pads, which stand 1.58 above the floor, and the 0.5 of room under the ledges falls to 0.1 at the tolerances.
- The check has a fitting section (E). It takes the unit at its largest (0.2 on each overall dimension, since the maker states no
  tolerance) with everything that stands proud of it (knobs, button actuators, the RF jack's nut and barrel, the 3.5 mm jacks'
  bushings, each 0.5 wider and further out), sweeps it along its way in, and gives the least clearance to every solid of the tray;
  then the same for the frame over the seated unit. It fails under 0.20, the printed parts' own tolerance. Result: 0.30 and 4.15.
- With `--solids` the same is done on the built solids, position by position (31 positions, every 2.0): no intersection, the least
  distances 0.30 and 4.15.
- Known-bad cases in the test: the first pass's tray with its documented way in (refused: the lintel 2.50 inside the knobs), the r2
  tray with a lintel printed across an end, a unit one millimetre wider, a frame ledge run through a knob zone.

**B2, the face-room limits are wrong.** True of the first pass: M3r2b measured the three buttons' room from 29.30 while they stand
under solids at 31.30, and the sensitivity column left out the set's own allowances.

- Section B is derived: for every face part of `panel1450.FACE_ITEMS` (and the light sensor's light guide, which that list lacks)
  whose footprint lies under any solid of the set, the unit, what stands proud of it, or a permanent plug, the row names the deepest
  solid over the footprint. Eighteen parts, and one row for the flat face under the deepest solid of all.
- The parts' heights are read from the makers' sheets the tree holds: C&K ATP19 S actuator 2.00 on a 1.50 O-ring, ATP16 1.5 on 1.0,
  Mentor 1282.5004 B - A = 1.5. Two are bounds: the monitor's glass (0.8, the most the ruling of 2 September lets a display surface
  stand proud) and the monitor frame's M4 heads (4.00, a cap head, because ASSEMBLY.md names no head).
- The set's own allowances are in every row: bond line 0.10, lid plate 0.13, printed height 0.20, and 0.20 more on the frame; none
  is stated by a source, so the sensitivity reading takes each twice.
- No row is NOT MET. The buttons are MET with 5.05 and 6.05 at the sensitivity reading. **The two knob rows are OPEN** (3.06 over the
  flat face and 2.26 over the monitor's window at the worst; 0.35 and -0.45 at the sensitivity reading), which is a finding the first
  pass's record hid: it called the knob row MET. The first pass also read the light guides' heads as 0.2; they are 1.5.
- Known-bad cases in the test: the first pass's row M3r2b against the solids of the first pass's tray (refused for all three
  buttons, 2.00 too shallow), and a knob 3 mm taller (NOT MET).
- With `--solids` the deepest point of the built set over each of the nineteen footprints is found by a boolean and equals section B's.

## The checker's minor list

| Item | Answer |
|---|---|
| wrong page cited for "95 x 63 x 25mm" | page 3, corrected in the module, in `measure_qmx_figures.py` (whose output is unchanged byte for byte) and in the set's README |
| v2/BUILD.md step 9 still says "strapped in" | the draft `apply_w5tray.py` edits step 9 as well |
| `panel1450.QMX_TRAY_X` and `scene.py` still carry r1 | NOT done: the constant is tied to the r1 part by `test_case_geometry` and read by the released sheet 14's generator. Stated in the set's README and in `drafts/README.md`; next action there |
| `frame_seat.out` changes after the draft, so the record could not be regenerated | the record prints the room, which the draft does not change; tried: the record is the same byte for byte before and after the draft. The cut label is fixed and asserted whole |
| the release's README and MANIFEST edited in place | not edited in this pass: the set has its own `MANIFEST.sha256` and README; the release's 50 files pass `sha256sum -c` unchanged |
| the bond across temperature | named in the record (section D), in the verification item and in T8 (a pull test after a thermal cycle); no expansion figure is held, so nothing is computed |
| the keeper's 0.34 under its screw heads | there is no keeper; the six frame screws are button heads on a flat 3.0 frame, the ten tray screws' countersinks leave 1.74 in 3.6 |
| the lintel is a 63.6 bridge | the printed parts have no overhang and no bridge but the six nut slots' roofs, 5.8 wide; the frame is flat |
| lettering of 4.3 to 5.0 pt on sheet 14r2-2 | a third sheet takes the notes and tables: notes 7.4 pt, tables 6.0 pt and more, labels 5.2 pt and more |
| "bend radius 20 or less" against "R 20 or more" | the draft says it one way: the lead is installed at R 20, so its own least bend radius must be 20 or under |
| 0.4 N m on 1.4 mm of thread | 0.25 N m on all sixteen M3 (INFERRED), with the load it puts on the thread and on the printed seats in the record |
| the QMX's own button actuators in no row | they are in the table of solids; row M3r2.XFRAME_2's deepest solid is one of them |
| vendor-status lines missing | added for every file this stream filed |

## Decisions taken (authority: SESSION, under the owner's standing rule of 26 September 2026)

Each with its reason and what reverses it; the first eight are the set's README section "What the set does", word for word there.

1. Both end panels open above a 1.5 sill; the sill cut to the floor under the RF jack.
2. The unit top face out, knob edge west, right panel toward the hinge (kept from the first pass).
3. The unit lowered in from above, held by a screwed retaining frame; six frame screws into square nuts in the posts.
4. Prusament PC Blend for both printed parts (kept).
5. A 2.0 mm 5052-H32 lid plate bonded with DP8005, ten flush M3 x 5 (kept).
6. 0.25 N m on all sixteen M3.
7. The load case: 100 g on the unit and its plugs, the peak CASE-MARGINS.md assumes for E1.
8. The place: east edge X 171.0, west to X 83.2, Y -45.9 to 65.9.
9. The clearance between the unit and the walls and sills is 0.4, not the first pass's 0.3. Reason: at 0.3 the unit at its largest
   kept exactly the printed part's tolerance to a wall, no more. Reverse by a measured unit.
10. The set stands beside the case release with its own manifest, and the release's README and MANIFEST are not edited. Reason: a
    release folder is an immutable copy. Reverse by the integrator cutting a new dated case release that lists the set.
11. The first pass's release README addendum and manifest lines are not re-applied (RECOVERY.md).
12. The reconstructed text of the maker's product page is filed under its first digest: the second fetch differs in the page's hit
    counter only, and with that one line set back it is the first file byte for byte. Reverse by filing the second fetch's text
    under a new name.
13. The knob rows are left OPEN and the unit is not lowered to gain room. Reason: the room a thinner floor or pad could give is 0.4
    to 0.6, less than the 1.45 the sensitivity reading lacks over the monitor's window, and it costs the pads' compression range; the
    row is decided by a height the maker does not state. Reverse by T9 or the unit in hand; the remedy if the knob is too tall is a
    lower knob or a lid plate cut out under the unit.
14. E2's level is transcribed from MIL-STD-810H 514.8 (a file the tree did not hold) and filed under `v2/vendor/standards/`.

## What was run, and where

| What | Where | Result |
|---|---|---|
| the first pass rebuilt from the recovered scripts, twice | the box, `/root/w5tray/`, venv equal to `requirements-cad.lock` | STL digests `02d9a3d9`, `26bac195` and the record's `1b0d7f6a`, the three the checker reproduced |
| `build_lid_tray_r2.sh` at commit `b92a678b`, twice | the box | both STL files and the record byte for byte the same; the record's two RESULT lines PASS |
| `lid_tray_qmx_r2_check.py` (sections A to E) | the runner | exit 0; the same twice; equal to the first 221 lines of the released record |
| `run.py lid_tray_qmx_r2` | the runner, this worktree | 10 passed, 0 failed, 0 skipped |
| `sha256sum -c MANIFEST.sha256` in the r2 folder | the runner | 9 OK |
| `sha256sum -c MANIFEST.sha256` in the case release | the runner | 50 OK, none changed |
| both drafts, the validator and three test files on a copy of main with this branch laid over | the runner, a scratch copy | `drafts/README.md` |

## Open, each with its next action

| Open | Next action |
|---|---|
| The lid harness's crossing of the sealed face plate: not designed anywhere. It blocks the harness picks, ASSEMBLY.md's lid harness steps, closing the lid on a wired QMX, and E6, E7 and E8 for a kit with its QMX connected. Not solved here | the case writer, at the next case release: option (a), a sealed panel-mount connector set in the plate's top strip near the hinge, from makers' sheets; a new face-plate version |
| The knob height (two rows OPEN) | T9 with chalk on the knob tips, or the unit measured in hand |
| The bond on polypropylene, and across temperature | T8: a pull test of a bonded coupon, before and after a thermal cycle |
| E1's peak on the lid | E1 with an accelerometer on the lid, against the 100 g load case |
| E2: the lid's response, the pads' real preload | E2, then the look named in the record |
| The frame's sustained stress and the screws' preload in storage heat | the look after E3-S and E4-S named in the record |
| The unit's heat in the pocket | the thermal stream: a dissipation figure of the maker's, or a measurement on the unit |
| The harness picks and a threadlocker | makers' sheets, against section A's bodies and R 20 |
| `panel1450.QMX_TRAY_X`, `scene.py`, sheet 14's generator | layer 7's single-source item, with `test_case_geometry` |
| The handover ZIP's cap | the integrator, `pack.yaml` (`drafts/README.md`) |
