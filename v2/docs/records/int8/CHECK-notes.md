# Independent check of integration set 7 (branch fnd/int8 at 7f6de345, onto main 6b419b02), AI review

Checker: an independent Claude session (an AI review, not a qualified engineering review). 28 September 2026,
21:35 to 21:52 CEST. Nothing of the kit has been built, ordered or measured; every verdict quoted below is a desk
reading of a prototype design. The worktree /home/claude-runner/worktrees/meshsat-fieldkit/int8 was read only.
Everything written is under /home/claude-runner/worktrees/meshsat-fieldkit/_scratch/chk-int8/ (this file, RESULT.md,
CLOSURE-draft.md, the registry diffs, the page copies and the five scenario logs).

Target: fnd/int8 moved to 38fd7cc9 at 21:36:37, one commit past the brief's 7f6de345, filing the box logs and the
suite log under v2/docs/records/int8/box/ (6 files, 3708 insertions, no tool, page or registry change). This check
reads 7f6de345 by hash; 38fd7cc9 was checked for identity, tag, trailer and dashes only (clean).

## 1. Commits and content hygiene (main..7f6de345)

- 82 commits; 0 not authored as Kyriakos Papadopoulos <ncpjfuzl@mxmx.email>; 0 subjects without [MESHSAT-1357];
  0 commit bodies with a co-author trailer; 0 em or en dashes in commit messages.
- Added lines carrying the trailer's literal name: 1. File v2/docs/records/w5tray/pass1/RESULT-w5tray-check-1.json
  line 27 (added by fb4a52eb, "the w5tray stream recovered from its transcripts, unchecked"): the sentence
  "... no the co-author trailer (its name is not written here) trailer in this repo." inside a quoted suggested commit body. scripts/pre-commit-check.sh
  rule 7 greps the staged diff for ^\+.*the co-author trailer (its name is not written here) (case-insensitive) and exits 1, so that checkpoint was committed
  without the check. A fast-forward of main makes no commit and runs no check; the string stays in fb4a52eb either
  way. Rated minor by me (it attributes no commit); the brief's literal criterion is not met.
- Em or en dashes in added lines: 4, all inside two fetched third-party pages, not drafted prose:
  v2/vendor/rf/amphenol-rf-132134-11-part-page-wayback-20260217.html (2) and
  v2/vendor/rf/amphenol-rf-132134-part-page-wayback-20260213.html (2). Every drafted line is clean.
- Tracked IBIS models at 7f6de345: 0 (git ls-tree -r | grep -c '\.ibs$'); .gitignore line 41 reads
  v2/vendor/*/ibis/*.ibs and git check-ignore -v v2/vendor/ti/ibis/pca9555.ibs names that line (w5si2 check m4).

## 2. The registry (v2/ecad/tools/pcb_requirements.yaml, PyYAML, main against 7f6de345)

Counts: owner_rulings 29 -> 31 (D-19, D-20 added, none changed); session_choices 74 -> 75 (SC-75 added);
open_items 65 -> 82 (20 added, S-95 to S-114; 3 removed, S-63, S-88, S-89; 3 titles extended, L-07, M-02, S-92);
closed_items 59 -> 62 (S-63 closed_by SC-75; S-88 and S-89 closed_by commit aaed6daa, each with closing_evidence);
records 144 -> 144, 28 changed, needs 19 unchanged; needs_document_sha256 6ebe6760... -> 6cb7b241..., which is the
sha256 of v2/docs/CONOPS.md at 7f6de345 (computed). Full dumps: registry-diff.txt, registry-items.txt,
records-changed.txt beside this file.

Changed records, by field: waits_on only on REQ-007, REQ-009, REQ-015, REQ-016, REQ-017, REQ-018, REQ-021, REQ-029,
CON-018, CHO-003, FEA-002, REQ-041, REQ-058 (links to the new items); history plus waits_on on REQ-022, REQ-024,
REQ-026, REQ-028, REQ-064 (S-89 left waits_on and is cited in history, the d6rel closure stage); evidence plus
evidence_bound_to on REQ-005, CON-006, REQ-019, CON-010, REQ-044, CFL-014, CFL-015, CFL-016 (rebinding entries: the
page, CONOPS.md, CASE-MARGINS.md, ASSEMBLY.md, pcb_decisions.yaml); REQ-072 evidence (+1 entry), rulings (+D-20),
waits_on (+S-114); FEA-007 choices (+SC-75), evidence, evidence_bound_to, waits_on (S-63 out, S-95 and S-96 in).
No record's statement, acceptance, evidence_result, allocation or phase changed (checked field by field on all 28;
REQ-072's three protected fields compared explicitly: SAME, SAME, FAIL).

Closures, each opened in the tree:
- S-88 by commit aaed6daa: v2/ecad/pcb-a-power-a23/routed/port_protect_a.verdict.json at 7f6de345 reads verdict
  PASS, denominator 42, inputs.netlist.sha256_16 0a2b59087bcc2678 (board A's declared phase A32 on the page),
  writer port_protect.py sha16 7acd5333fc59f8d0 (equals sha256/16 of the file at 7f6de345), port_reviews
  dcaa890424a8d15f, counts ports 18, internal_pins 60, declarations_refused 0, uncovered_pins 0,
  review_disagreements 0, as the closing evidence states. The file in the tree is the second re-take's (ts
  2026-09-28T19:15:25Z, commit 9d89ffd3); the same file at aaed6daa (ts 18:42:46Z) carries the same verdict, counts
  and shas. The regression the evidence cites exists (tests/test_port_protect.py, 60 tests;
  records/d8dec31/readings/regress-reclassify.txt).
- S-89 by commit aaed6daa: the seven routed/reliability.verdict.json at 7f6de345 read INCONCLUSIVE with
  writer c50f2b8b35d1d57b (equals reliability.py at 7f6de345), list tools/pcb_reliability.yaml 40f2a98323b1f9ce,
  bound true, citations_unjudged 0, refused 0, and per board the artefact sha, held_by list and
  candidates/classed/excluded stated in the evidence: A 0a2b59087bcc2678 82/57/25 [REL-O-01, 02, 07, 08, 12, 13];
  B 028997a6c5e8810f 155/56/99 [02, 03, 07, 08, 09, 12, 13]; C 3fddbb3edcd4248a 74/24/50 [04, 05, 07, 08];
  D 7a2c0ac2190b141a 40/11/29 [07, 08, 10, 12, 13]; E 56adc9746d61c4e0 35/21/14 [02, 07, 08, 12, 13];
  E5 board file 686b29a734c55b9a 17/17/0 [06, 07]; P 760ac6f74d62d194 26/9/17 [07, 08, 11, 12, 13]. Their ts
  (19:17:38Z to 19:17:44Z) and the first re-take's (18:44:59Z to 18:45:05Z, at aaed6daa, same values) are both after
  the coverage floor evidence_not_before 2026-09-28T20:33:53+02:00.
- S-63 by SC-75: the session choice names v2/cad/lid_tray_qmx_r2.py and v2/release/case-2026-09-27/lid-tray-qmx-r2/
  (README, MANIFEST.sha256, check.out, drawing PDF, STEP and STL of tray, frame and plate), all in the tree at
  7f6de345; lid-tray-qmx-r2-check.out ends "RESULT: PASS: the table is what was built, nothing intersects in place
  or on the way in, and every control fails as it must" (a model check, nothing printed).

New open items S-95 to S-114: every one is either waited on by a record or carries a disposition with a reason:
S-95 (REQ-021, FEA-007), S-96 (FEA-007; cited by SC-75), S-97 (disposition TOOLING), S-98 (disposition
DECLARATION; cited by CON-010, REQ-044), S-99 (REQ-018, CON-010, REQ-044), S-100 and S-101 (REQ-007, REQ-029),
S-102 and S-103 (REQ-009, REQ-029), S-104 (REQ-029), S-105 (REQ-009), S-106 (REQ-015, REQ-029), S-107 (REQ-015),
S-108 and S-109 (REQ-029, REQ-041), S-110 (REQ-058), S-111 (REQ-015, CHO-003), S-112 (REQ-029), S-113 (REQ-029,
REQ-058), S-114 (REQ-016, REQ-072; named by M-02). Each of S-95 to S-113 states a finding with its source (the r2
set's check.out sections, CHECK-3.md p3, the pilot's ANALYSIS.md and CORRECTION.md, the review of decision 31 by
section, its T-2 and T-3). S-114 is a statement of owed work sourced from D-20 (see minor item 4).

The rulings against the owner's words: D-19 carries every element of OD-01 (buy route, staged purchasing; one
checkout-ready list with exact compatible part numbers, VAT, shipping and total; machining quotes separately; the
monitor and the logger deferred unless the procedure needs them and no existing or borrowed equipment suffices;
the physical-validation route selected, no unpriced purchase authorised, purchasing the owner's; a short test brief
naming the competence and equipment so the owner can assign the operator; buying parts closes no measurement gate;
the exact case variant confirmed before ordering, Peli's 1450PF for the 1450EU). "thermocouple logger" is the
session's gloss of "logger"; READY-TO-ACT.md line 429 lists the logger as the PicoLog TC-08 with 8 thermocouple
inputs, so the gloss is grounded. D-20 carries every element of OD-02 as corrected (M1 and REQ-072 preserved with
duration and operating conditions; external DC optional, requiring it overnight not an acceptable substitute; the
budget reconciled against verified loads, usable battery energy, night duration and solar contribution; feasible
options within the approved constraints; any change to capacity, placement or operating modes presented explicitly;
the conflict demonstrated and the smallest justified changes presented for the owner's decision; unmet criteria
visible). It records no external DC source and no option (e) as the mission's basis. It adds two sentences that are
the session's reading rather than the owner's words: the parenthetical "(the case that never changes, the pack of
D-06, the required mission)" and "The routes (c) to (e) of EQ-13 are not taken" (minor item 3). REQ-072's statement,
acceptance and evidence_result are unchanged from main; M-02 stays OPEN with its title extended by one sentence.

Validator, run in the worktree: rules_lib.py 59 rule(s), 0 error(s), 0 warning(s), fingerprint 635ff031f210f48c;
rules_lib.py requirements 144 requirement record(s), 0 error(s), 0 warning(s).

## 3. The pages (v2/docs/CURRENT-EVIDENCE.md, main 35 layout-entry reasons, 7f6de345 34)

Per board main -> candidate: A 7 -> 6, B 7 -> 8, C 3 -> 4, D 7 -> 6, E 4 -> 3, P 5 -> 5, E5 2 -> 2 (sums 35 and 34,
recomputed from the page). Row by row, from the readings:
- Gone on A, D and E: the row "decision 31 | review: not met" (no review record on file). The review
  v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md is now in the tree, pinned 094817023210d1b0 and read on each
  board's netlist (0a2b59087bcc2678, 7a2c0ac2190b141a, 56adc9746d61c4e0), so the hold's layout-entry requirement
  reads met on all three; the hold itself stays (FABRICATION_RELEASE). Minus 3.
- New on B and C: "TRN-001 INCONCLUSIVE | CURRENT_CANDIDATE (BOUND)". port_protect.py now reads INCONCLUSIVE a
  declaration whose external pins no review has enumerated into pcb_port_reviews.json, and boards B and C have no
  review yet (S-112). Their TRN-001 PASS rows left the PASS table (port_protect_b, port_protect_c). Plus 2.
- The "what closes it first" table: "the design or its declarations" 11 -> 13, the hold row (3) gone, the blockers
  row 21 unchanged; 11 + 3 + 21 = 35, 13 + 21 = 34.
- Evidence classes: PASS on either 71 -> 69 (the two TRN-001 rows), AWAITING_REVALIDATION 213 -> 206 and DESK_REVIEW
  21 -> 28 (REL-001 on the seven boards is now a bound, current desk reading INCONCLUSIVE, listed under "Desk reviews,
  which are not physical tests"), UNBOUND 20 -> 13 (those seven readings now record their artefact). The historical
  aggregate PASS 209 -> 200 and INCONCLUSIVE 89 -> 98 (the seven REL-001 word-list PASSes and the two TRN-001).
- The "readings limited by an open item" paragraph (S-88, S-89) is gone: no limits_reading item stands.
- Every PASS row: 69 rows on the candidate page, 62 name a netlist or board sha, each equal to the board table's
  declared-phase sha (0 mismatches; the 7 rows without a sha are the registry and package readings, the same 7 at
  main). Checked on the page, not by re-rendering.
- Tool age: no file under v2/ecad/tools changed between the second re-take's HEAD 05af085c and 7f6de345
  (git diff --stat empty); the writers of the readings I opened equal the files at 7f6de345 (port_protect.py
  7acd5333fc59f8d0, reliability.py c50f2b8b35d1d57b, edge_length.py 21d61d18e18e56a8). The page's TOOL_CHANGED count
  is 176 on both pages (readings of all revisions awaiting revalidation; "of which a re-take alone makes current" 9);
  the 83 CURRENT_CANDIDATE readings are by construction not TOOL_CHANGED.
- The models: the six SI-001 readings at 7f6de345 record inputs.model_state PRESENT for A (5 models), B (10), C (6),
  D (5), each model_N with sha256_16 equal to pinned_sha256_16, and NOT_ASKED for E and P (no model pinned for their
  drivers); every verdict INCONCLUSIVE, missing_input null. rules_status.py's _pinned_state (lines 1057 to 1112): a
  reading that read a model at the pinned sha is BOUND whether or not the model is in the checkout; a checkout without
  the models returns ABSENT from ibis_manifest.state_of (line 98), which is neither DIFFERS nor the "recorded absent,
  present now" case, so in a clean clone these readings stay current and the pages render the same. A RE-TAKE in a
  clean clone would record the models absent and read less (the w5si2 check's m3). The integrator's isolated clone
  check (pages byte-identical, 0 validator warnings) is consistent with this; I did not re-render.

## 4. The merge itself

- git merge-base --is-ancestor main fnd/int8: holds.
- Stream tips are ancestors of 7f6de345: w5tray 0ad773ab, w5si2 f84243ba, d8dec31 9057e668, d6rel 3d7c98d2,
  p3bind 3bfaa317, cx1 900ba526 (each also the current tip of its fnd/ branch).
- Seven merge commits: beaf7e3c (w5tray), 5e765762 (cx1 records), 475becd7 (w5si2), 80eda86e (d8dec31),
  dcf04c90 (cx1 check 2), 3208f1e9 (d6rel), 0f992417 (p3bind, last, as its check asked).
- Append-append files, compared with comm against each parent of every merge that touched them (sorted line sets):
  v2/vendor/sources.txt at beaf7e3c, 475becd7, 80eda86e, 3208f1e9; v2/vendor/vendor-status.txt at beaf7e3c, 475becd7;
  .gitignore at 475becd7: lines of a parent missing from the merge result = 0 in every case (sources.txt 348+354 ->
  360, 360+361 -> 373, 373+350 -> 375, 375+364 -> 391; vendor-status 267+274 -> 279, 279+280 -> 292; .gitignore
  38+38 -> 41). At 7f6de345 no line of main's version is missing from any of the three; the only duplicated line in
  sources.txt and vendor-status.txt is a bare "#" separator that main already had.
- The checks' minor items the integrator said were answered: w5si2 m1 (the note at
  records/w5si/apply/apply_board_c_declarations.py line 53, w5si2/README.md and pcb_rules_coverage.yaml name the
  EMC return rules' skip of LOW_SPEED_OR_DC), m4 (above), m5 (vendor-status.txt line 57 carries a folder-level
  "standards current" line, so UM10204 is covered as the RP2040 documents are), m6
  (v2/docs/records/w5si/check-edges-7f7721c4.md is filed); d8dec31 B2 (apply_registry_d31.py line 234 inserts the
  block on its own line whether or not a blank line precedes closed_items, with the fix comment) and B3 (lines 289
  to 297 resolve the reading at <phase>/out, <phase>/routed, then v2/ecad/out, as rules_status does); d6rel minor 1
  (the stage does not compare the writer's sha: the seven readings' writer c50f2b8b35d1d57b equals reliability.py at
  7f6de345, checked by me). Carried: d8dec31 N1 to N6, d6rel 2 to 5 and w5si2 m2, m3, m7 are in the filed check
  records under records/int8/checks/ (with the checkers' notes); I found no carry list in EXECUTION-PLAN.md or the
  registry that names them with an owner (minor item 7).

## 5. The apply scripts under v2/docs/records/int8/

Each was run on a scratch clone (git clone --shared, sparse) checked out at the parent of the commit that ran it,
with the script copied in from 7f6de345 (each is byte-identical to the version its commit ran, except
apply_rebind_page_int8.py, changed at 69ab7cb3 to compare with the bound page from history); the result was diffed
against that commit's files; then the script was run again. Logs: scenario1-carried_check3.log,
scenario2-i03.log, scenario3-owner_rulings.log, scenario4-rebind.log, scenario5-tray.log.
- apply_carried_check3.py at 420f252a: "S-92 reworded (p4, p5); FEA-002 waits on S-92 and S-93 (p7); S-97 opened
  with disposition TOOLING (p3)", exit 0; the registry identical to 5c8a6d22's; second run "REFUSED: S-97 exists
  already (a second run)", exit 2. Docstring states the four items and what it does.
- apply_i03_items.py and apply_contract_contact_rating.py at 5e765762: both exit 0; the registry and
  pcb_interfaces.yaml identical to a8607eab's; second runs refused (S-98 exists; the old line occurs 0 times), exit 2.
- apply_owner_rulings_2026_09_28.py then apply_needs_sha_conops.py at 038037ed: "D-19 and D-20 recorded; S-114
  opened (REQ-072 and REQ-016 wait on it); M-02 and L-07 extended; CONOPS.md section 7 and M1 written and REQ-005,
  CFL-016, CFL-014 rebound (6ebe6760c4312bca -> 6cb7b241cb84d729); EQ-13's table extended" and "needs table
  byte-identical; pin moved"; the registry, CONOPS.md and ENGINEERING-QUESTIONS.md identical to c5430071's; second
  runs refused, exit 2. It asserts that the CONOPS-bound records carry the tree's sha before it edits, that only the
  two named CONOPS sections changed (by heading), that REQ-072's result did not move, and re-parses.
- apply_rebind_page_int8.py at 15d23a3b (HEAD's page 719cca08a0823263, the records bound to a46365d4112c54ba, the
  history branch): "comparing with the bound page from history", both records rebound, "layout-entry reasons 41 to
  34 (A 8 to 6, B 8 to 8, C 4 to 4, D 8 to 6, E 5 to 3, P 6 to 5, E5 2 to 2)", the registry identical to 69ab7cb3's;
  second run "REFUSED: the tree's page is the page the records are bound to (719cca08a0823263)". At 9d89ffd3 with
  7f6de345's page copied in it refuses the same way and the registry equals 7f6de345's: the final commit rendered a
  page with the sha the records already carried, so the rebind of 69ab7cb3 is the one that binds the final page.
  The history lookup walks rev-list of the page for the sha the RECORDS carry (lines 92 to 98), not HEAD's.
- The tray: stream w5tray's apply_w5tray.py (c7447456's version) then apply_frame_seat_r2.py then
  apply_tray_links.py at beaf7e3c: ids taken SC-75, S-95, S-96, EQ-31 as committed; the registry and eleven documents
  identical to c7447456's; second runs refused ("AssertionError: already applied"; "FEA-007 already waits on S-95").
  My first attempt in a clone without v2/vendor/materials stopped in the draft at a missing PDF after it had written
  ASSEMBLY.md, CASE-MARGINS.md and ENGINEERING-QUESTIONS.md and before the registry (minor item 6).
- The validator in a sparse clone prints 75 errors of the form "evidence_bound_to names
  v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net, which is not in this tree": my clones' missing netlists, not the
  registry (0 errors in the full worktree on the same file).

## 6. Closure record

Drafted as CLOSURE-draft.md beside this file, by kind.

## What I could not check, and why

- I did not re-render the pages (rules_status.py and rules_render.py are verdict writers; the brief's own reading of
  the integrator's isolated clone check stands) and did not run the suite (the box did: 2171 passed, 0 failed,
  3 skipped, EXIT 0 at 7f6de345).
- The re-take's readings were compared for the closures and SI-001 only; the other 96 changed evidence files were
  not opened one by one.
- The engineering content of the streams (the tray's geometry, the port protection review, the reliability list,
  the edge rates, the constraint sheets) was not re-derived; their own checks under records/int7/checks/,
  records/int8/checks/ and records/cx1/checks/ did that and I read only their verdict lines and minor items.
