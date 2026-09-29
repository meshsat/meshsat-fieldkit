acceptable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026): the targeted check of patch_od01j.py. B1 and m1 to m8 answered by patch_od01k.py (the table replaced whole); m9 noted in LOG-od01b.md. -->

# AI review: targeted check of OD-01's correction T1 and the lid-pack applicability, fnd/od01b at dc45a87e (MESHSAT-1357)

This is an AI review, not a qualified engineering review. The checker wrote none of the work under review. It ran on 29
September 2026 from 12:15 to about 12:26 CEST (read from `date`) in the read-only scratch clone, detached at
`dc45a87ea42ce4aecd7ade9b46380af9a7680174` (parent `5c01fa6a`, author the owner's identity, 7 files changed).

Scope, as the brief sets it (not a full review): the one commit `5c01fa6a..dc45a87e` (`patch_od01j.py`) and what depends
on it: TEST-PROCEDURE sections 1, 5.4 and 8 read whole with sections 5.1 to 5.3, 6 step 1 and 9; the brief; the README;
the whole od01 folder searched; `POWER-THERMAL.md` section 10; Option A(i) as recorded on `fnd/a1int` at `637c9876`
(`a1mech/README.md`, `a1mech/DECISION-A1.md`, `a1int/RECONCILE.md`) and `ENERGY-RECONCILIATION.md` section 8 of this tree.
`patch_od01j.py` was replayed on a copy of the `5c01fa6a` tree in the session's scratch space. No box, agent or other
model was used, and nothing was committed.

T1 is corrected: no document in the folder still treats a stopped step as evidence of conductance, and the consumers agree.
One row of the new applicability table contradicts the Option A(i) record it cites, because the table describes A(i) as
the lid pack alone and leaves out its base half (the second 4S3P block in the west pocket).

## Blocking

**B1. The applicability table leaves out Option A(i)'s base block, so the T5 row contradicts the A(i) record.**
- Where: `TEST-PROCEDURE.md` lines 34 to 38 (the preamble describes A(i) as "a second pack of 56 or 60 cells in the lid
  over the face, a harness across the hinge and a stay") and line 49 (`Test B: T1, T2, T5, T11 | yes | case, frame, legs,
  walls, arrestor`).
- Against: A(i) as recorded is the lid pack PLUS the base pockets' 4S6P: `a1mech/README.md` lines 6 to 7 ("the base
  pockets' 4S6P (ENERGY-RECONCILIATION section 8) plus a lid module"), `a1int/RECONCILE.md` lines 18 to 19 (4S14P lid
  "4S20P" in all, 4S15P "4S21P"), main's `EXECUTION-PLAN.md` Q3 (4S20P). The second block takes the west pocket, and
  "the west RF entry is re-planned before the west block is taken" (`a1mech/README.md` lines 46 to 49 and 271 to 272;
  `ENERGY-RECONCILIATION.md` line 707 of this tree). `a1mech/README.md` line 293 lists "T10, T5 (west wall)" as the
  checks of that re-plan. T5 drills the end walls from the current templates and decides M17w, the west drops
  (`CASE-MARGINS.md` line 1072): under A(i) its west-wall holes and M17w reading belong to an entry A(i) sends back.
  So T5 does not apply unchanged, and the row is not true of A(i) as recorded.
- Fix (text only):
  1. Line 35 to 36: add the base half, for example "... and doubles the base pack to 4S6P with a second 4S3P block in
     the west pocket (`ENERGY-RECONCILIATION.md` section 8), which takes the west RF jumpers' drop zone".
  2. Line 49: move T5 out of the "yes" row: "T5 | partly | the east and back walls unchanged; the west wall's holes
     follow the west RF entry, which A(i)'s west block sends back for a re-plan (a1mech section 7: T10, T5 west wall)".
     If the table keeps T5 at the west wall, say that drilling the mock-up case's west wall from the current template
     would leave holes the re-plan may not use.
  3. Line 50, T4: add "and no west block stand-in (M4a west and M6w, board B's C33 at 3.99, OPEN at T4, a1mech
     section 6)".
  4. Line 46 (lid-open steps): name the missing west block as a difference of the set-up (H3 stands in the east pocket
     only; H2's west overhang would stand over a second block).
  5. Line 43: C4-W, like C1, is then a mock-up plate and not A(i)'s final west entry plate.

## Minor items

- **m1. The physics sentence's stated reason.** Section 8, lines 409 to 411. The equation and the numbers are right (64 W
  less 24 W stored is 40 W over 20 K = 2 W/K; 64 / 20 = 3.2). But "with several temperature nodes and a local trip no
  general bound holds in either direction" gives the wrong reason. In the one-node model the sentence uses, a step that
  warms from below its own steady state has `dT/dt` > 0, so `P / (T - T_room)` is at least `G`: an upper bound on G,
  the opposite of the old text. The same holds in a network of positive conductances and capacities started at or below
  its steady state. What removes a bound in general is a step that starts above its steady state (S4 after S3), room
  drift, and a point reading of stratified air under natural convection. The conclusion, that a stopped step yields no
  `G`, is conservative and stands. Suggest: "for a warming step the one-node reading is at most an upper bound on G;
  room drift, a step that cools and the stratified air's point reading remove even that, so a stopped step yields no G".
- **m2. Section 1's uncertainty row "Not yet steady" (line 60)** reads "at most 0.33 K = 1.1 % low" and "3.3 % low". The
  combined row (line 62) correctly treats it as reading `G` high. Now that section 8 states that an unfinished warm-up
  reads `G` high, write "the rise up to 0.33 K low, so `G` up to 1.1 % (3.3 %) high" so that the two cannot be read
  against each other.
- **m3. README lines 40 to 44, the release manifest.** The count is right (below). The sentence gives no directory for
  `MANIFEST.sha256`. Its paths are relative to `v2/release/case-2026-09-27/` (its own header: `sha256sum -c
  MANIFEST.sha256`); from the repository root, like the command before it, every line fails (49 "No such file" and one
  FAILED). It lists the release's 50 files of 27 September. The later folders `h1-heat-test-plate/` (6 files) and
  `lid-tray-qmx-r2/` (9 files) each carry their own manifest and are not in it, so "verifies the full release" should
  read "verifies the 50 files it lists (run inside `v2/release/case-2026-09-27/`; the two later folders have their own
  `MANIFEST.sha256`)".
- **m4. Line 37 cites "`v2/docs/EXECUTION-PLAN.md`, the standing rule of 29 September".** That text (the standing rule
  and Q1 to Q4) is on main at `bf68ad9e`, not in this branch's tree (its EXECUTION-PLAN names no Option A(i)) and not in
  the package. Say "on main" or name the commit until the branch is integrated.
- **m5. "56 or 60 cells" (line 36)** matches `a1int/RECONCILE.md` (4S14P or 4S15P) and main's Q1. `a1mech/DECISION-A1.md`
  lines 12 and 14 and the README section 3 still read "56 places (48 used)" and "61 places (48 used)". That conflict is
  a1int's own, but citing RECONCILE.md for the pack size would spare an OD-01 reader the conflict.
- **m6. T6 "partly" (line 50)** says the clearance "would change" without saying how. The lid pack is inside the lid and
  leaves the lid's outer skin unchanged. The stay (SC-A1-08) stops the lid at 100 degrees, short of Peli's stop, so T6's
  open-lid reading at Peli's stop bounds A(i) unless T-A1-3 finds otherwise. State the change, or the verdict reads as
  if T6's reading were unusable.
- **m7. The "New for the lid pack" row (line 51)** names T-A1-1 to T-A1-4 and S-95 correctly (each checked against
  a1mech lines 286 to 291). It omits a1mech section 7's extensions: T9 with a dummy module (line 287), T8's pull test at
  the module's 3.4 kN (line 288), E1 and E2 with an accelerometer on the lid (line 292), and T10 and T5 at the west wall
  (B1).
- **m8. The C1 row (line 44):** S-95 predates A(i) (the QMX leads' crossing, `REQUIREMENTS-TRACE.md` line 3951), so C1
  as drawn is not the final face under the current design either. True as written; optional.
- **m9. The README's scripts row** gained `patch_od01j.py` by hand, not by the script (the replay leaves that row
  unchanged). The earlier patches followed the same pattern. The log could say so.

## Verified

- **Replay.** `patch_od01j.py` on the `5c01fa6a` tree reproduces `TEST-PROCEDURE.md` and `TEST-BRIEF.md` byte for byte.
  `README.md` differs only in the scripts row (m9). A second run is refused ("already applied"). The LOG's 12:05 row
  matches the commit time, 12:05:11 CEST.
- **T1, section 8 (lines 405 to 415).** The stopped step is recorded with every reading, the time and what tripped, and
  kept as transient data. It is not a steady-state result and yields no `G`. An inferred value needs a stated,
  checked transient model before it closes anything. "Bound the conductance from below" survives only as the replaced
  literal inside `patch_od01j.py`.
- **The consumers agree.** Section 1 (lines 29 to 30: "a step stopped at a limit before steady state gives none"),
  section 5.4 (lines 333 to 334: only a step with `steady_utc` yields `G`), the brief (lines 29 to 30), S6's note
  (lines 414 to 415: the 64 W lid-closed point stays open), section 5.2 (the step ends at a limit), section 6 step 1
  (after S6 steady or stopped), and section 9 (`stopped_at_limit_utc`, `tripped_by`, empty for a steady step).
- **The folder search.** Every `.md` in the od01 folder, including the checks and the log, and `MACHINING-RFQ.md` and
  `CHECKOUT-LIST.md`, holds no other claim that a stopped or interrupted step bounds or measures conductance.
  `POWER-THERMAL.md` section 10 (the experiment, lines about 1044 to 1057) proposes the test and makes no such claim.
- **The applicability rows, each against the procedure and the A(i) record.** Correct: R1 to R8; H1 and C6; C1's
  missing crossing (S-95, a1mech lines 38 and 206 to 209); the shutdown; the lid-closed steps, since a1mech gives 24.00
  and 40.06 deep modules in a 44.39 room, so "mostly cells" holds; the patch runs; T1, T2 and T11; T-A1-1 to T-A1-4 as
  named. "400 Wp into a 200 W stage" matches `a1solar/ARRAY.md`. The a1 folders are on `fnd/a1int` and not on main. The
  four pending decisions match main's Q1 to Q4. Nothing in the table adopts A(i). The exceptions are B1 and m4 to m7.
- **README: 30 of 50, counted.** `MANIFEST.sha256` lists 50 files. 30 of them are in `PACKAGE.sha256`. The package
  carries 44 files under the release path: those 30, the manifest itself, and 13 files of the two later folders. The 20
  files not carried are the release's STLs, envelope and plan drawings, the marking SVG, the leg locator and wedge STEP,
  the QMX bracket and the zstack outputs. Inside the release folder, `MANIFEST.sha256` and both sub-manifests read OK.
  The package command is stated correctly for the repository root and for `repo/` of the export (`od01_pack.py` writes
  the files there at their repository paths).
- **Package.** From the clone root, `sha256sum -c v2/docs/records/od01/PACKAGE.sha256` reads OK for all 77 files. The
  77 rows of `PACKAGE.md` match the files in bytes and sha256 and are the same set as the sha256 list. They total
  14,878,512 bytes, which is "14.9 MB".
- **Brief.** pandoc with xelatex, A4, 10 pt, 2 cm margins: 2 pages
  (`_scratch/chk-od01c-pdf/brief10.pdf`).
- **Hygiene.** No em or en dash, or any character from U+2010 to U+2015 or U+2212, in any `.md` of the folder. They
  appear only in the scripts' dash-detector constants. No user path in the folder.
