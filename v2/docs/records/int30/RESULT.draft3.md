**DONE:** sections 1 to 8 written on commit 2b `d83d9f2d` (the candidate and the integration's commits, W15's classification bound with its 13 unreviewed changes, W16's review of 2b quoted, the integration as measured, the freeze and gate lines as placeholders with their log paths, the compute record, what set 30 closes and the three claims apart, the records bound); **NOT DONE:** every value that does not exist yet (the candidate commit, the two pending corrections after W16's review, the gates, the re-key's KEY, the promotion, the mirror); **NEXT:** the coordinator fills the placeholders from the named logs, and adopts, corrects or discards this text as `records/int30/RESULT.md`.

# Set 30: the result of the integration (DRAFT 3 of `RESULT.md`, for the coordinator's adoption at promotion; MESHSAT-1357)

**Status: DRAFT for the coordinator**, the one writer of `records/int30/RESULT.md`. Written by worker W18 on branch `fnd/w18result`
(base fnd/w15class `57bcdbfc`, which carries Slot K's `RESULT.draft2.md` and W15's `CLASSIFICATION.draft.md`) on 6 October 2026 from
04:51 CEST, on the integration's commit 2b `d83d9f2d`. Started from a copy of draft 2 (`v2/docs/records/int30/RESULT.draft2.md`,
kept unchanged beside this file): its sections 2 to 5 (the eighteen commits to `bbba3e53`, the equivalence at `bbba3e53`, the
pre-existing refusals, nine contradictions) stay there and are cited, not repeated; this draft replaces its header, its revision
table, its gate table and its claims table, and adds what happened after its base. It is record text: it runs no generator, suite,
gate or box job, accepts nothing, closes nothing, promotes nothing and changes no verdict. Prototype framing: nothing in the kit has
been built, bought, powered or measured; every figure below is a time, a count or a digest copied from a log or a commit, and no
figure is an engineering result.

**What governs it.** The owner's part 25 (`d83d9f2d:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:845` `Use the existing integration gate to record the reviewed and integrated revisions and the intervening changes.`)
and the constitution's section 2 (`d83d9f2d:v2/docs/EXECUTION-CONSTITUTION.md:23` `Report engineering-handover readiness, power-design closure and fabrication release separately. A promoted integration set is none of those by itself.`).
No blended percentage is given anywhere in this file.

**Citations and placeholders.** `<sha>:path:N` followed by a code span quotes line N of that file at that revision; a path under
`<worktrees>/_runs/` is a coordinator's log outside the tree, quoted with its line (`:N`) or, for the growing queue file
`<worktrees>/_runs/int30/QUEUE.md`, by its dated entry. `test_w18result.py` reads every quote, every commit named and every count.
The literal placeholders are the fixed set `__CANDIDATE__`, `__PROMOTED__`, `__MIRROR__`, `__KEY__`, `__GATE_BOX_PY312__`,
`__GATE_BOX_PY311__`, `__GATE_RUNNER__` and `__G7__`, with the two pending corrections the coordinator named after W16's review,
`__L6R2_FIX__` and `__W19__`; this draft fills none of them.

## 1. The candidate

| Role | Revision | State as given | Source |
|---|---|---|---|
| REVIEWED: the one targeted recheck, cx46 | `4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e` | CORRECTIONS NOT CLOSED; the second negative on this candidate, so the review method ended | `d83d9f2d:v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:10` `P0 RECHECK: CORRECTIONS NOT CLOSED.` (its base_commit at line 8; the filed check's path is this one) |
| Commit 2b: the integration's regenerated outputs, the last committed revision when this was written | `d83d9f2d720878ca5267dbf59bdc571c6890fd92` | no check has read it; W16's review is section 3f | section 3 |
| INTEGRATED: the candidate commit (the re-keyed record l4e7 cache installed) | `__CANDIDATE__` | none | section 4 |
| PROMOTED: main after the fast-forward | `__PROMOTED__` (mirror `__MIRROR__`) | a DESK candidate, not an accepted power design (section 6) | section 4 |

**The integration's commits, in first-parent order** (`git log --first-parent 3d2746c9^..d83d9f2d`; times are the committer dates in
Europe/Amsterdam). The disposition round between `4d0ff8a2` and `d5abed7c` is in W15's table (section 2), not repeated here.

| # | Commit | Time | What it did (from its subject and diff) |
|---|---|---|---|
| I1 | `3d2746c9` | 2026-10-05 23:06:30 | merge of fnd/remeng `6d9ec491`: the remaining-engineering ledger after cx46 and its test |
| I2 | `7070f106` | 2026-10-05 23:51:03 | integration 1: the L4-E9 change-list rows R-220 to R-245 applied by the reviewed draft (117 changes; no R-241, route B2 out of the baseline) |
| I3 | `bbba3e53` | 2026-10-06 01:17:21 | integration 2a: L4-E9's generator re-pinned to the merged rounds' bytes, its D-10/D-16 citation check reading L4-E7's P0 output too, its output regenerated; the change-list draft's applied-state reader |
| I4 | `6fe398e9` | 2026-10-06 01:56:48 | merge of fnd/l4e9s31 (set 31): L4-E9's page, register, generator data and test expectations brought to the candidate; the coordinator's criteria words 1 CONDITIONAL, 2 FAIL, 3 PASS, 4 PASS, 5 CONDITIONAL |
| I5 | `53a68c7c` | 2026-10-06 03:09:15 | integration 2c: the applied-state reader tests the presence of every added row and the page's note; record l8r2's board E round gains the p0sol draft (R-240); test_l9t5 accepts the applied state |
| I6 | `68e20e4d` | 2026-10-06 03:54:08 | pre-freeze merge 1 of 4: fnd/w2applier `2080a0ff` (the applied-state reader's fixtures) |
| I7 | `3c118b43` | 2026-10-06 03:54:08 | pre-freeze merge 2 of 4: fnd/w1l5pwr `6ab17e21` (Layer 5's S27-B6 reads D-10 as set 31 left it, output regenerated) |
| I8 | `5c414310` | 2026-10-06 03:54:08 | pre-freeze merge 3 of 4: fnd/ledgerfix `99bbc0c6` (the ledger's HO-L for E11-37, the back-feed's narrower reading) |
| I9 | `2ccf0f20` | 2026-10-06 03:54:08 | pre-freeze merge 4 of 4: fnd/w6tp `9802dfde` (the test procedures' quotes re-taken on set 31's cells) |
| I10 | `6bc4424e` | 2026-10-06 03:58:43 | merge of origin/main `24708af3` (MESHSAT-1500's compact folder and README; the owner's part 26 filing `b0a67a45`) |
| I11 | `d83d9f2d` | 2026-10-06 04:42:16 | integration 2b: the regenerated outputs, the four cascade generators' pins, the applier's reader deciding on every added row, the ledger's owner-file citations moved by one, two test modules restated to set 31 (34 files, 178 insertions, 139 deletions: `git show --stat`) |
| I12 | `__L6R2_FIX__` | pending | the coordinator's correction of record l6r2's generator and its regenerated output (W16's finding 1, section 3f) |
| I13 | `__W19__` | pending | the merge of fnd/w19applier: the applier's D1 regression test (W16's finding 3, section 3f) |
| I14 | `__CANDIDATE__` | pending | the candidate commit: record l4e7's results cache re-keyed on the integrated tree (section 3e) |

## 2. What changed after the review (the owner's part 25)

**W15's classification is bound by its path and revision:** `v2/docs/records/int30/CLASSIFICATION.draft.md` at fnd/w15class
`57bcdbfc` (in this branch's history). It classes every commit of `git rev-list 4d0ff8a2..6bc4424e`
(`57bcdbfc:v2/docs/records/int30/CLASSIFICATION.draft.md:7` `prints 38: 28 commits and 10 merges`) from its diff into a fixed set.
Its summary counts, first class per row (its lines 74 to 81): REVIEWED-INPUT CHANGED 13; RECORD TEXT (restatement) 7; GENERATOR DATA
(text) 1; TEST / FIXTURE 1; DIGEST RE-PIN / REGENERATED OUTPUT 2; MERGE 10; OUTSIDE P0 4; total 38. Its two placeholder rows (2b and
the candidate) are not determined there; 2b is read below, the candidate commit is the coordinator's.

**The 13 REVIEWED-INPUT CHANGED commits, as UNREVIEWED CHANGES after cx46** (W15's reasons, shortened to one line each; the six
marked NOT ONLY NARROWING are W15's "They do not only narrow (6)" list, `57bcdbfc:v2/docs/records/int30/CLASSIFICATION.draft.md:88` `They do not only narrow (6):`;
the other seven are its line 87, `57bcdbfc:v2/docs/records/int30/CLASSIFICATION.draft.md:87` `They narrow, withdraw, tighten or restate an OPEN state (7):`):

| W15 row | Commit | Reading | W15's reason in one line |
|---|---|---|---|
| 5 | `9cc6725d` | narrows | B-PA1's limit 6.352 A to 6.351 A; the PRINTED-rows band 6.3890 to 6.8942 A becomes 6.3888 to 6.8945 A; case row 3 to an open defect; V6-B1 OPEN; the connected verdict REMAINING ENGINEERING (cx46 items 2, 4, 7, 13) |
| 6 | `4d1d02de` | narrows | route B2 UNSELECTED and WITHDRAWN AS DRAFTED (cx46 item 18); the out-of-baseline draft's text only |
| 8 | `6b768b1e` | narrows | the rail trip's average 1.1 s to 1.17 s and its transient 171 ms to 181 ms; V-B23's 0.2 s withdrawn; the sustained bound withdrawn (cx46 items 5 to 10) |
| 10 | `0b33a1f9` | narrows | the change-list draft's C-PROT rev 1 from met to PROVISIONAL on the desk (cx46 item 10); the connected predicates |
| 11 | `1c6d56f5` | narrows | the 6.351 A limit carried to case row 1 (cx46 item 2); the band's label words |
| 17 | `7070f106` | NOT ONLY NARROWING | D-16 from OPEN to ADDRESSED IN DRAFTS in L4-E9's generator data (the reviewed draft's own text, applied); no cx46 item names D-16 |
| 18 | `bbba3e53` | NOT ONLY NARROWING | the regenerated output carries row 17's state: "17, 3 open; 4 addressed in drafts" becomes "17, 2 open; 5 addressed in drafts" |
| 19 | `bca7b0dc` | narrows | D-17 restated, OPEN kept (REMAINING ENGINEERING, RE-2) |
| 20 | `14082416` | NOT ONLY NARROWING | R-246 (board P's ideal diode) added to the register and the change order; R-159's acceptance 45.88 K/W to 40.78 K/W; R-189's acceptance replaced by S3 and S4 |
| 21 | `17ce29d5` | NOT ONLY NARROWING | criterion 2 CONDITIONAL to FAIL; D-16's ADDRESSED IN DRAFTS carried to the page's decision row |
| 23 | `53a68c7c` | NOT ONLY NARROWING | P0-7's draft added to record l8r2's board E composition, where L4-E9's table puts it (R-240) |
| 30 | `3088ee79` | NOT ONLY NARROWING | TP-SOLAR's acceptance quotes carry P1-1's narrowing to E-1 and R-189's replacement by S3 and S4 |
| 31 | `2f74beb5` | narrows | R-159's 40.78 K/W carried into TP-E11-29's quote (stricter) |

Three merges bring them (`f973b646`, `9cf3982a`, `6fe398e9`). W15 found no baseline circuit draft, no board generator and no netlist
changed in the range (its summary, line 90).

**None of these 13 was checked by an independent checker after cx46.** The method ended with cx46's second negative
(`d83d9f2d:v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:10` `P0 RECHECK: CORRECTIONS NOT CLOSED.`), and no
further Astra run on this candidate is authorised by the owner's ruling. The promoted DESK candidate therefore carries them as
**UNREVIEWED CHANGES**: never as checked, never credited, each owing its own targeted verification before any credit (part 25,
`d83d9f2d:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:845` `Use the existing integration gate to record the reviewed and integrated revisions and the intervening changes.`).
Passing the suite transfers no engineering verdict to them.

**Commit 2b, read here from its diff (W15's placeholder row; this worker's read, not a classification the coordinator has made).**
`git diff 6bc4424e d83d9f2d` over the 25 changed `.out` files: 210 changed lines, 154 of them carrying a hexadecimal digest of 12 or
more characters. The other 56 are in four outputs: `l6r2/l6r2_passives.out` (14: the board A, B, D and P chains now name the applied
P0 drafts, for example `d83d9f2d:v2/docs/records/l6r2/l6r2_passives.out:2418` `chain apply_gen_sch_p_breaker.py, apply_gen_sch_p_idealdiode.py`),
`l8r2/l8r2_drafts.out` (12: board E's round from 13 to 14 drafts, `d83d9f2d:v2/docs/records/l8r2/l8r2_drafts.out:535` `after the whole round (14 drafts, this one last): CELL_F accepted; GND accepted`,
row 23's composition carried into the output), `l8r2/l8r2_gndret.out` (28: board B's step list) and `l9t5/l9t5_connected.out` (2: "117 changes"
becomes "118 changes", `d83d9f2d:v2/docs/records/l9t5/l9t5_connected.out:62` `118 changes`, R-246 of row 20). No figure with a unit occurs
only in the removed or only in the added output lines (this worker's script over the diff, not committed). The same script found no
upper-case verdict word (PASS, FAIL, OPEN, CLOSED, BLOCKED, PROVISIONAL, CONDITIONAL, ACCEPTED, REFUSED, WITHDRAWN) in a changed
output line, **but that scan missed two lines whose meaning changed, which W16's review found** (section 3f, its findings 1 and 2):
`d83d9f2d:v2/docs/records/l6r2/l6r2_passives.out:2537` `the other drafts alone: v2/docs/records/d8dec31/apply_gen_sch_d_ptt.py refused: apply_gen_sch_d_ptt: already applied (its marker is in the file)`
replaces a line that read "commutes" (board D's ptt draft applied twice in the commutation reading; draft 2 named the same line in its
section 3b), and record l8r2's gndret order check, `d83d9f2d:v2/docs/records/l8r2/l8r2_gndret.out:110` `NOT THE ORDER THIS RECORD COMPOSES`,
where its "no change-list row" for panel5v and ph4 is now false against its own step list. **So `l8r2/l8r2_gndret.out` in 2b is NOT a
binding-only change** (W16's finding 2): the record's GND figures did not move but are readings on its own order, 6 of 15 drafted
board B rows (`<worktrees>/_runs/int30/REVIEW-2B.md:196` `its GND reproduction covers 6 of 15 drafted board B rows in its own order`);
board B's change-list composition is shown in `l9t5_connected.out` line 67, as W16 states. The rest of 2b: the pins of
`l4e10_cell_thermal.py`, `l4e11_power.py`, `l4e12_thermal.py` and `l4e9_power_path.py` (seven pinned digests, every new value equal to
the committed file, W16's section 2); the change-list applier's reader (`apply_l4e9_changelist_p0.py`, 23 lines: D1 and D2, section
3c); the ledger's owner-file citations moved by one (`REMAINING-ENGINEERING.md`, 20 lines); `test_applier_state.py`, `test_l9t5.py` and
`test_remeng.py`. Under W15's own rule (a file that carries another row's change is classed so too, its line 13), the l6r2, l8r2 and
connected lines carry rows 20 and 23 into outputs; their class is the coordinator's, and the gndret line cannot be classed a re-pin.

**W15's findings that touch this result** (its section 3): (1) `l4e9_power_path.out:975` "criterion 2 CONDITIONAL" against line
1017's FAIL: the coordinator read line 975 as an earlier round's block, history, to be confirmed by the block's heading in the next
L4-E9 round (`<worktrees>/_runs/int30/QUEUE.md`, entry "04:38 to 04:43 CEST (Q-01)", `history beside line 1017's current FAIL`);
(2) the band label and the 6.351 A limit are in `9cc6725d` and `1c6d56f5`, not in `ac8efbca` as the coordinator's notes had it;
(3) `7070f106`'s D-16 change is not a narrowing (row 17 above); (4) `cd559d20` and `0d5f855e` are record text filed as received, not
OUTSIDE P0; (5) `53a68c7c` came after draft 2's base, so draft 2's tables do not list it.

## 3. The integration, measured

### 3a. The regeneration passes

The passes before integrate7 (integrate3 to integrate6b, 23:06:30 to 01:53:09) are draft 2's measured table
(`v2/docs/records/int30/RESULT.draft2.md`, section 6). After it:

- **integrate7, base `3d2746c9`** (`<worktrees>/_runs/int30/integrate7b-0221.log:1` `at 2026-10-06 02:21:24 CEST; base 3d2746c9`):
  the L4 pin chain read already identical; L4-E9's own stale pin re-pinned and its output regenerated
  (`<worktrees>/_runs/int30/integrate7b-0221.log:25` `l4e9_power_path.py: 1 pins re-pinned`); record l9t5's dependency-ordered
  cascade twice, pass 2 changing no byte (every pass-2 line reads "already identical", lines 48 to 66). Targeted passes from 02:49:45
  (`<worktrees>/_runs/int30/integrate7b-0221.log.targeted:2` `round 1: 31 pairs selected (43 changed files)`): round 1 replaced 10
  (`:15` `round 1: 10 replaced`), round 2 replaced 5 (`<worktrees>/_runs/int30/integrate7b-0221.log.targeted:24` `round 2: 5 replaced`),
  round 3 replaced 1 (`<worktrees>/_runs/int30/integrate7b-0221.log.targeted:29` `round 3: 1 replaced`), round 4 replaced 0
  (`<worktrees>/_runs/int30/integrate7b-0221.log.targeted:33` `round 4: 0 replaced`): converged. Ended
  `<worktrees>/_runs/int30/integrate7b-0221.log:199` `== integrate7 done at 2026-10-06 03:48:29 CEST`.
- **post_integrate** (`<worktrees>/_runs/int30/post-0354.log:1` `at 2026-10-06 03:54:07 CEST; HEAD 53a68c7c; 33 files changed`): the
  applier's D1/D2 correction, the four pre-freeze merges I6 to I9, one stash conflict
  (`<worktrees>/_runs/int30/post-0354.log:12` `CONFLICT (content): Merge conflict in v2/docs/records/l5pwr/l5pwr_contracts.out`),
  resolved to W1's committed bytes and regenerated later; ended `<worktrees>/_runs/int30/post-0354.log:32` `== post_integrate done at 2026-10-06 03:54:37 CEST`
  (the queue's entry gives 03:54:45 for the same step; the log's stamp is copied here).
- **The targeted pass on the merged tree, first launch STOPPED** (`<worktrees>/_runs/int30/targeted8-0359-ABORTED-base-HEAD.log:1` `at 2026-10-06 03:59:04 CEST`):
  base HEAD would have missed the records pinning files the merges changed; stopped at 04:00:14 with 0 outputs replaced
  (`<worktrees>/_runs/int30/QUEUE.md`, entry "03:59 to 04:02 CEST (Q-01)", `was STOPPED at 04:00:14 (0 outputs replaced`).
- **The targeted pass, base `3d2746c9`** (`<worktrees>/_runs/int30/targeted8-0401.log:1` `at 2026-10-06 04:01:53 CEST`;
  `<worktrees>/_runs/int30/targeted8-0401.log:2` `round 1: 37 pairs selected (101 changed files)`): round 1 replaced 3
  (`<worktrees>/_runs/int30/targeted8-0401.log:11` `round 1: 3 replaced`: `h3/same_patches.out`, `l5pwr/l5pwr_contracts.out`,
  `l9t5/l9t5_connected.out`, lines 4, 8 and 9), round 2 replaced 0 (`<worktrees>/_runs/int30/targeted8-0401.log:18` `round 2: 0 replaced`):
  converged; ended `<worktrees>/_runs/int30/targeted8-0401.log:122` `== regen_targeted done at 2026-10-06 04:37:48 CEST`. The queue's
  04:29 entry says round 1 replaced "h3/same_patches.out, l5pwr_contracts.out, l9t5_connected.out and one more"; the log prints 3.
- **The h3 outputs restored to HEAD before 2b, by policy** (`<worktrees>/_runs/int30/regen_targeted.sh:12` `h3 dropped: its public_check prints the time it asked and never converges; the h3 outputs stay as on main`);
  2b carries no h3 file (`git show --stat d83d9f2d`).

### 3b. The refusals, each explained (no output of the candidate depends on them)

- `l5pwr/l5pwr_contracts.py` in integrate7's rounds 1 to 4 (`<worktrees>/_runs/int30/integrate7b-0221.log.targeted:4` `S27-B6: the replacing text is matched 0 times (not once)`):
  the record read L4-E9's D-10 in set 28's words; W1's `6ab17e21` (merged at I7) restates S27-B6 as set 31 left it, and the final
  pass regenerated the output (line 8 of `targeted8-0401.log`).
- `l4close/verify_risks.py`, exit 1 in every round: by design; its committed output's item 5 DIFFERS
  (`<worktrees>/_runs/int30/QUEUE.md`, entry "04:06 to 04:10 CEST (Q-01, Q-10)", `"SOURCE NOT AS READ: R-139's lag clause", pre-existing since set 27`).
- `h3/design_difference.py` (exit 1) and `h3/zip_size_estimate.py` (exit 2): h3 records, excluded by the policy above.
- `scrub/script_tests.py`, exit 1: 10 of its 12 sandboxed script tests pass; the two others need worktrees that no longer exist on
  the runner (`<worktrees>/_runs/int30/QUEUE.md`, entry "04:38 to 04:43 CEST (Q-01)", `the two failing ones need the worktrees`): an
  environment fact, no test module runs it; a note for the next set's record.
- `int10/dryrun.py`, exit 2: it needs a scratch-folder argument (`<worktrees>/_runs/int30/QUEUE.md`, entry "04:06 to 04:10 CEST (Q-01, Q-10)", `int10/dryrun.py exit 2 (needs a scratch-folder argument`).
- Draft 2's section 4 lists the same pre-existing refusals on the earlier passes and on main.

### 3c. The test runs, their counts, the failures and their fixes

| When | Run | Result as printed | Cause of each failure, and the fix |
|---|---|---|---|
| 01:56 | the affected tests before set 31's merge | `<worktrees>/_runs/int30/finish-0137.log:37` `tests: 346 passed, 16 failed, 0 skipped` | set 31 lag: 13 of test_l4e9 against the applied list (fixed by merging set 31, I4), 2 of test_l8r2 (E_ROUND gains the p0sol entry), 1 of test_l9t5 (accept the applied state); draft 2's section 6 |
| 03:48 | integrate7's affected tests | `<worktrees>/_runs/int30/integrate7b-0221.log:161` `tests: 361 passed, 1 failed, 0 skipped` | set 31 lag again: `<worktrees>/_runs/int30/QUEUE.md`, entry "03:48 to 03:54 CEST", `test_l9t5's change-list test lagged set 31 twice`; both expectations updated with their basis; green at 03:54 |
| 03:54 | the merges' modules and the applier | `<worktrees>/_runs/int30/post-0354.log:27` `tests: 64 passed, 5 failed, 0 skipped` | W2's fixture anchors: `<worktrees>/_runs/int30/QUEUE.md`, entry "03:48 to 03:54 CEST", `W2's mutation fixtures M1, M3, M4, M5 anchored on the reader's PRE-D1 lines`; anchors moved to the corrected reader's lines, no predicate weakened |
| 03:57 | the whole affected set relaunched | `<worktrees>/_runs/int30/post-tests-0357.log:80` `tests: 68 passed, 1 failed, 0 skipped; failed: test_l5pwr.t_output_reproduced_byte_for_byte` | l5pwr's output: W1's committed output against the merged tree; regenerated by the targeted pass (3a) |
| 04:37 | the targeted pass's affected tests | `<worktrees>/_runs/int30/targeted8-0401.log:82` `tests: 364 passed, 1 failed, 0 skipped; failed: test_remeng.t_the_amendments_citations_read_what_they_cite` | the owner file's part 26 shift: `b0a67a45` inserted a table row and every later line moved by one; the ledger's owner-file citations moved by one and the test's two numbers to 681 and 826 (`<worktrees>/_runs/int30/QUEUE.md`, entry "04:38 to 04:43 CEST (Q-01)", `the test's two typed numbers moved to 681 and 826`) |
| 04:42 | the merges' modules and test_remeng after the fix | `<worktrees>/_runs/int30/QUEUE.md`, entry "04:38 to 04:43 CEST (Q-01)", `63 passed then 17 passed, 0 failed` | none failing; no log file of this run is in `<worktrees>/_runs/int30` (the queue's entry is the source) |

Left in the candidate, named for the next set: L4-E9's generator's three and the page's four owner-file citations are off by one the
same way and are NOT corrected in this freeze, because a generator text change forces the cascade (the same queue entry).

### 3d. The diff read of 2b

The coordinator's read of the uncommitted tree at 04:29 (`<worktrees>/_runs/int30/diffread-2b-0429.txt`, 35 files):
`<worktrees>/_runs/int30/QUEUE.md`, entry "04:29 to 04:31 CEST (Q-01, Q-10)", `no unit figure and no verdict word changed in any output`.
This worker's read of the committed `d83d9f2d` (section 2, "Commit 2b") agrees that no figure with a unit moved; the non-digest lines
are composition chains, step lists and one count (117 to 118 changes). Both reads missed the two lines whose meaning changed that
W16 found (3f, findings 1 and 2): "no verdict word changed" holds only for the upper-case verdict words, not for l6r2's "commutes" to
"refused" or l8r2's order check. The committed 2b has 34 files (`git show --stat d83d9f2d`): the h3 outputs restored, the ledger and
test_remeng added after 04:29.

### 3e. Record l4e7's results cache (the KEY)

On 2b the KEY is a MISMATCH, expected until the re-key: `<worktrees>/_runs/int30/targeted8-0401.log:55` `l4e7 KEY MISMATCH committed 1718dfe54e5373e0 now df9030eaf2c8e7bf; parts moved: files`,
the one moved part `<worktrees>/_runs/int30/targeted8-0401.log:56` `file v2/docs/records/l4e11/l4e11_power.out: 3a46198439d5 -> a2089b3f6682`
(integrate7 read the same at `<worktrees>/_runs/int30/integrate7b-0221.log:134` `l4e7 KEY MISMATCH committed 1718dfe54e5373e0 now df9030eaf2c8e7bf; parts moved: files`).
The re-key runs on the suite5 box since 04:45:57 (section 5). After it: `__KEY__`, installed in `__CANDIDATE__`.

### 3f. The review of 2b (W16)

Filed: `<worktrees>/_runs/int30/REVIEW-2B.md` (W16, an AI review, read from 04:43 to 05:00 CEST by its own heading; file sha256 prefix
50e8f0fda536b9e0 as read here at 04:58). It is a reviewer's reading of commit 2b, not a verdict on the power design and not a check
of the 13 unreviewed changes of section 2. Its FINDINGS list, verbatim (its lines 190 to 213):

> 1. `v2/docs/records/l6r2/l6r2_passives.out` line 2537 (old 2532), cause `v2/docs/records/l6r2/l6r2_passives.py` lines 97 and 742: board D's
>    declaration-draft commutation with all pending drafts lost; "commutes" became "refused" because ptt is in both STANDALONE and R-239's
>    chain and the together list applies it twice. Severity: **fix before the candidate commit** (deduplicate `together` in compose_intent and
>    compose_land, or drop board D from STANDALONE now that R-239 carries ptt; regenerate l6r2_passives.out; no live pin of that output).
> 2. `v2/docs/records/l8r2/l8r2_gndret.out` line 110 (old 98), cause `v2/docs/records/l8r2/l8r2_gndret.py` lines 110 to 112 and 582 to 585:
>    the record's order check flipped to "NOT THE ORDER THIS RECORD COMPOSES" and its "no change-list row" for panel5v and ph4 is now false;
>    its GND reproduction covers 6 of 15 drafted board B rows in its own order. Severity: **note for the next set**, and the set 30
>    classification must name it as not a binding-only change (the record's figures are on its own order; board B's change-list composition
>    is shown in l9t5_connected.out line 67).
> 3. `v2/ecad/tools/tests/test_applier_state.py` lines 261 to 284 against `v2/docs/records/l9t5/apply_l4e9_changelist_p0.py` lines 108 to 121:
>    the D1 correction has no regression that fails on the parent's reader (the R-220-removed case is refused by both readers; the
>    pristine-page, partially-applied-register case is untested, and on the parent's reader it duplicates rows). Severity: **fix before the
>    candidate commit** (one test-only predicate plus a mutation restoring the old `"| R-220 |" not in reg` test).
> 4. `v2/ecad/tools/tests/test_l9t5.py` lines 1079 to 1081: for the seven KNOWN ENGINEERING DEFECT rows the exact next-action check became a
>    prefix and substring check; the RE item per row is no longer asserted. Severity: **note for the next set**.
> 5. `v2/ecad/tools/tests/test_l9t5.py` lines 1086 to 1090: the cited bases (SET31-CHANGES.md rows 2 and 23, L4E7-P0SOL.md section 4) do not
>    carry "OPEN (REMAINING ENGINEERING)" (cx46 line 188 does), and P0SOL line 142 still says "does not resolve D-10"; the B2 non-resolution
>    property is no longer asserted ("with no protection credit" could be). Severity: **note for the next set**.
> 6. `v2/ecad/tools/tests/test_remeng.py` line 250: the comment places b0a67a45's inserted row at line 29; it is line 26. Citations verified
>    correct. Severity: **note for the next set**.
> 7. `v2/docs/records/l9t5/l9t5_connected.out` lines 60 to 62 (unchanged prose): "applied in memory / tree's files unchanged" is stale since
>    7070f106. Severity: **note for the next set**.
> Per section: 1: findings 1 and 2. 2: no finding. 3: finding 3. 4: findings 3, 4, 5, 6. 5: no finding. 6: no finding.
> Nothing here blocks the freeze on what was read: no figure with a unit moved, no pin mismatches, h3 unchanged, nothing outside the two folders.

**What follows from it for this set (the coordinator's message of about 05:00 CEST, recorded here as given):** none of the seven blocks
the freeze; two are fixed before the candidate commit, both as PENDING CORRECTIONS:

- Finding 1: the coordinator corrects record l6r2's generator (board D's ptt draft no longer applied twice in the commutation reading)
  and regenerates `l6r2_passives.out` before the candidate commit: `__L6R2_FIX__`.
- Finding 3: W19 writes the applier's D1 regression test (a predicate that fails on the parent's reader, with its mutation) on branch
  fnd/w19applier from 2b, merged before the freeze: `__W19__`.
- Findings 2, 4, 5, 6 and 7: notes for the next set. Finding 2 is also carried into section 2 (record l8r2's gndret output is not a
  binding-only change in 2b).

## 4. The freeze and the gates (the coordinator's; every value a placeholder)

| Step | Where the coordinator reads it | Result |
|---|---|---|
| W16's finding 1: record l6r2's generator corrected, its output regenerated | the coordinator's commit on fnd/p0pwr | `__L6R2_FIX__` |
| W16's finding 3: the applier's D1 regression test merged | fnd/w19applier, merged before the freeze | `__W19__` |
| The re-key on suite5, its KEY | the box's re-key log; `v2/docs/records/l4e7/l4e7_stage_settings.results.json` in the candidate commit | `__KEY__` |
| The candidate commit | `git log` on fnd/p0pwr | `__CANDIDATE__` |
| The manifest (candidate_guard record) and the evidence tar | `<worktrees>/_runs/candidates/` and the runbook `<worktrees>/_runs/int30/PLAN.md`, sections 4 to 6 | not yet produced: the coordinator records the manifest's path and the tar's sha256 here |
| candidate_guard check on the runner | the runbook's freeze steps | not yet run |
| Box pass, Python 3.12 (every module but the Python 3.11 and runner ones) | `<worktrees>/_runs/int30s1/suite-box.log` | `__GATE_BOX_PY312__` |
| Box pass, Python 3.11 (`test_l4e10`, `test_l4e12`) | `<worktrees>/_runs/int30s1/suite-box-py311.log` | `__GATE_BOX_PY311__` |
| Runner pass (`test_l4e7`) | `<worktrees>/_runs/int30s1/runner/suite-runner.log` | `__GATE_RUNNER__` |
| suite_gate with G7 (identity, module coverage, 0 failed, 0 load errors, every skip explained, totals consistent) over the three logs | `<worktrees>/_bin/suite_gate.py` | `__G7__` |
| Promotion: fast-forward of main, push, the mirror, candidate_guard check on main | the runbook's section 5 | `__PROMOTED__`, mirror `__MIRROR__` |
| Targeted verification of the 13 unreviewed changes of section 2 | the coordinator's choice of verifier; not the ended review method | owed; none performed |

**Durations for comparison (measured on earlier sets; none of them is set 30's).** Set 29's passes A and B together
(`d83d9f2d:v2/docs/records/int29/RESULT.md:38` `17:26:09 to 18:00:17, 34 min 8 s`), its pass C
(`d83d9f2d:v2/docs/records/int29/RESULT.md:40` `Pass C took about one minute. Set 28's same run took at most 34 minutes.`), and set 29's
counts as the size of the run (`d83d9f2d:v2/docs/records/int29/RESULT.md:27` `2838 passed, 0 failed, 14 skipped`). Record l4e7's
re-key measured once on suite4 (`<worktrees>/_runs/int30/PLAN.md:9` `MEASURED 29 min on the suite4 box, 21:02 to 21:31`). The
queue's estimate for the present re-key's end, an ESTIMATE: `<worktrees>/_runs/int30/QUEUE.md`, entry "04:50 CEST", `the box runs the re-key (expected end about 05:15)`.

## 5. Compute

- **suite4 (instance 54347953) stopped by the idle watchdog at 01:30**: `<worktrees>/_runs/vast/watchdog.log:1847` `idle_h 2.00`, then
  `<worktrees>/_runs/vast/watchdog.log:1849` `54347953 STOPPED after 2.00 h idle` (a backup at line 1848). A checkpoint had said it was
  running; corrected and relayed at 04:10 (`<worktrees>/_runs/int30/QUEUE.md`, entry "04:06 to 04:10 CEST (Q-01, Q-10)", `was STOPPED by the watchdog at 01:30:06 after 2.00 h idle`).
- **Its restart refused twice**: the resume from 04:09 and the start answered `<worktrees>/_runs/int30/QUEUE.md`, entry "04:24 to 04:29 CEST (Q-10, compute)", `"resources_unavailable, state change queued", twice`;
  **the queued start cancelled at 04:27** (`its queued start CANCELLED with a stop PUT at 04:27`, the same entry;
  `<worktrees>/_runs/vast/LOG-20261006.md:1` `the queued start CANCELLED by a stop PUT at 04:27 (success true) so no unattended late start; disk kept`).
- **suite5 (instance 54417830) rented at 04:28**: `<worktrees>/_runs/vast/LOG-20261006.md:2` `RENTED 54417830 meshsat-1357-suite5 on offer 50747392`,
  the offer `50747392 EPYC 7B13 32 threads 63 GB Estonia 0.1223 USD/h` (the same line). The watchdog prints a higher hourly figure for
  the running instance, `<worktrees>/_runs/vast/watchdog.log:1958` `54417830 meshsat-1357-suite5 running dph 0.1663`; the difference is
  not explained in the logs read here (both are copied, neither is a measured cost).
- **SETUP-DONE at 04:31:34** (`<worktrees>/_runs/vast/LOG-20261006.md:3` `SETUP-DONE at 04:31:34 (3 min)`, measured: 3 min after the rental).
- **The re-key started at 04:45:57** (`<worktrees>/_runs/resume-20261005-morning.md:382` `re-key running on suite5 since 04:45:57`); its
  end and duration are not measured yet (the estimate is section 4's).
- **Storage of the stopped instances kept, nothing destroyed**: the watchdog's 04:40 lines list six instances with their retained
  storage, among them `<worktrees>/_runs/vast/watchdog.log:1964` `54347953 meshsat-1357-suite4 exited stopped_age_h 3.0 retained storage 0.0370 USD/h`
  (lines 1959 to 1964, each "kept; never destroyed without the owner's explicit instruction"). Compute and storage cost are kept
  apart (the constitution, section 12); no total is computed here.

## 6. What set 30 closes and what it does not

**Set 30 closes NO power item.** It is an integration of records: the disposition after cx46, the applied change-list rows, set 31's
restatement of L4-E9, the ledger, the procedures' quotes and the regenerated outputs. It changes no baseline circuit draft and no board
generator (W15's summary, line 90; 2b's diff, section 2). As the candidate's records state it:

- cx46's twelve NOT CLOSED findings stay REMAINING ENGINEERING (`d83d9f2d:v2/docs/records/l4close/REMAINING-ENGINEERING.md:100` `The twelve cx46 findings NOT CLOSED, each a REMAINING ENGINEERING item`);
  the ledger's counts (`d83d9f2d:v2/docs/records/l4close/REMAINING-ENGINEERING.md:669` `Counts: remaining engineering 20; qualification 1; external architecture fact 3; closed 4; conditional 2.`).
- D-10 stays OPEN as E-1 and D-17 as RE-2 (`d83d9f2d:v2/docs/records/l4e9/l4e9_power_path.out:560` `two material defects are open: D-10 (E-1) and D-17 (RE-2)`;
  `d83d9f2d:v2/docs/records/l4e9/l4e9_power_path.out:1017` `criterion 2 FAIL with 2 defects open`).
- The connected verdict (`d83d9f2d:v2/docs/records/l9t5/l9t5_connected.out:336` `THE CONNECTED ELECTRICAL VERDICT: REMAINING ENGINEERING.`) and every OPEN and
  PROVISIONAL claim of the records are unchanged by the integration's own commits.

**The three completion claims, each with its own state** (the constitution's section 2, cited above; never blended):

| Claim | State | Basis |
|---|---|---|
| Engineering-handover readiness | NOT YET ASSESSED | the coordinator's Layer 4 DESK-gate assessment (queue item Q-05) on the promoted revision decides it; W12's draft 2 (fnd/dgate2 `150e908b`) keeps the literal placeholder "[COORDINATOR: DESK-gate verdict]" and names what would support or deny it (its section 6, Y1 to Y7 and N1 to N5); the ledger hands over 20 remaining-engineering items, 1 qualification and 3 external architecture facts (line 669 above). This draft chooses no verdict word |
| Power-design closure | BLOCKED | `d83d9f2d:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1005` `on the set 30 candidate **the power-design closure gate is BLOCKED**`; `d83d9f2d:v2/docs/records/l4e9/l4e9_power_path.out:569` `the power-design closure gate: BLOCKED`; `d83d9f2d:v2/docs/records/l9t5/l9t5_connected.out:4` `No completion claim: power-design closure and fabrication release stay BLOCKED.` |
| Fabrication release | BLOCKED | `d83d9f2d:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:885` `**Fabrication release: BLOCKED.**` (no circuit change applied, no board laid out); the connected output's line 4 above |

Kept apart from all three: documents and editable artifacts (on main as a DESK candidate after the promotion, `__PROMOTED__`); design
reviewed and accepted (NO: cx45 NOT CONFIRMED, cx46 CORRECTIONS NOT CLOSED, and the 13 unreviewed changes of section 2); circuit
changes implemented (NONE); physical qualification (NONE). A promoted integration set is none of the three claims by itself.

**The next set's inputs** (W10's `<worktrees>/_runs/int31/PLAN.draft.md`, re-read on 2b from 04:43 to 04:49; summarised in
`<worktrees>/_runs/int30/QUEUE.md`, entry "04:49 CEST", `still ONE conflict (TP-E11-29.md, W3's file whole)`, `moved pins 28` and
`145 tests expected to fail before regeneration`): eight merges in the order the plan gives, the authors' branches by tip:

| Order | Branch | Tip |
|---|---|---|
| 1 | fnd/w4l4e7 | `786aed2f` |
| 2 | fnd/w5l8p | `cd19df59` |
| 3 | fnd/w14l5 | `910f08ef` (contains fnd/w8l5 and fnd/w1l5pwr) |
| 4 | fnd/w11l9t5 | `85b6f258` (contains fnd/w9l9t5) |
| 5 | fnd/w13l4e9 | `56ab0d01` (contains fnd/w7rem) |
| 6 | fnd/w15class | `57bcdbfc` |
| 7 | fnd/dgate2 | `150e908b` |
| 8 | fnd/w3annex | `686de0a2` (the one conflict, `TP-E11-29.md`, resolved to W3's whole file by the plan's reading) |

Also owed to the next set: the second l4e7 re-key once `l4e11_power.out` moves, the off-by-one owner-file citations of L4-E9 (3c),
and the coordinator items the queue lists as Q-27.

## 7. The records this result binds

| Record | Revision bound | State |
|---|---|---|
| The P0 power list, revision 3 | W17's draft 3 has not landed (fnd/w17p0list at its base `c79ae84f` when this was written); so Slot K's draft 2, `v2/docs/records/l4close/P0-POWER-LIST.rev3.draft2.md` (in this branch's history), with W7's nine patch rows R-01 to R-09 in `v2/docs/records/l4close/P0-POWER-LIST.rev3.patch.md` on fnd/w7rem `3e566c55` | a draft; the coordinator adopts revision 3 at Q-04a |
| LAYER-STATUS, the set 30 fold | fnd/lstat31 `87c5fb08` (`v2/docs/handover/LAYER-STATUS.md`, +90 lines, and `test_lstat31.py`) | a draft fold with the verdict placeholder; adopted after the promotion |
| Layer 4's DESK-gate assessment | fnd/dgate2 `150e908b` (`v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.draft2.md`) | draft 2; the verdict word is the coordinator's (Q-05) |
| The part 25 classification | fnd/w15class `57bcdbfc` (`v2/docs/records/int30/CLASSIFICATION.draft.md`) | 38 commits classified; 2b read in section 2 here; the candidate commit's row owed |

## 8. Left out, and why

- Every placeholder value: the candidate commit, the KEY, the gate lines, the promotion and the mirror do not exist yet.
- W16's findings 2 and 4 to 7 are carried as notes for the next set, not resolved here; the two corrections it asks before the
  candidate commit are placeholders (`__L6R2_FIX__`, `__W19__`).
- Draft 2's per-commit equivalence at `bbba3e53`, its pin read and its nine contradictions: cited by path, not re-read on 2b, except
  where section 2 reads 2b's own diff.
- The figure-by-figure comparison of the 13 unreviewed changes: W15's reasons are copied, not re-derived.
- The suite5 hourly figure's two values (0.1223 against 0.1663 USD/h): both copied; the logs read here do not reconcile them.
- No generator, suite, gate, candidate_guard, regen_out or box job was run; the diff counts of section 2 came from a read-only script
  over `git diff`, not committed.
