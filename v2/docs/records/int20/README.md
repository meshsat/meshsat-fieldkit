# Integration set 19 (MESHSAT-1357, branch `fnd/int20`, 1 October 2026): the Layer 3 amendment and the Layer 4 energy records

Prototype design: nothing is bought, built or measured. The integrating session's records for set 19, from main
`d841540d`, with main's later commits `964795c8` and `1b1fe7df` (the owner's compute rulings of 1 October 2026 in the
execution plan) merged in at step 5. Requirements maturity, design compliance and physical verification stay apart.

| Step | Commit | What it did |
|---|---|---|
| 1 | `d5dab19f` | merge of `fnd/l4e` at `3ed52f3a`: Layer 4's energy records (L4-E1, the comparison L4-E2 with its service ledger and O-2's enumerated bound, the independent power review's items L4-E3 on a nominally compatible candidate panel, the engineer's packet), their checks (two of the engineering collaborator's not accepted, the coordinator's verifications accepted) |
| 2 | `a789a6c2` | merge of `fnd/l3am` at `d3e3b415`: the Layer 3 amendment on the independent review (L3-R01 the solar case labelled, L3-R02 REQ-042's end-to-end acceptance, L3-R04 the acceptance bound to the reviewed content, L3-R05 REQ-016's protection judged apart), with the collaborator's two checks of it (not accepted) |
| 3 | `cd231260` | the amendment's tests restated to hold before and after the review findings close (copies built from the open state; the tree's own closing check is never a fixture) |
| 4 | `7a1523d0` | the coordinator's amendment check `check-l3am-3` (reviewed revision `cd231260`) filed, the review findings CLOSED by `apply_l3am_findings_closed.py`, the pages rendered |
| 5 | `8e4262ce` | merge of main at `1b1fe7df`: the execution plan's two entries of 1 October 2026 (the compute ruling and its amendment); no other file |
| 6 | `41881d8f` | this record; the candidate promoted to main after its gates (below) |
| 7 | `8146b4cc` | the supersede test of `test_l3am.py` reads the history its copy already holds (below: the first acceptance attempt) |
| 8 | `aa9a1bef` | check 4 of the amendment (`check-l3am-4`, Claude's, reviewed revision `8146b4cc`) filed and named as the check that closed the findings (`apply_l3am_check4.py`, `apply_l3am_findings_rechecked.py`); the acceptance-guard check restated for the binding; the re-acceptance's status script and its test; the pages rendered |
| 9 | `d850141a` | merge of `fnd/l4e4` at `bb7ebf12`: Layer 4 task L4-E4, board A's current-limit coordination (U3's IIN_HOST 4.70 A with R16's tolerance in its bounds, R11 8 mOhm, the Kelvin allowance 0.38 mOhm at 25 C) and the outlet's R138 at 5 mOhm with a bench procedure that isolates U18's comparator; drafts for board A's generator owner, nothing applied; the collaborator's check and recheck (not accepted) and the coordinator's check 3 (accepted) |
| 10 | `87dfa55f` | this record's steps 7 to 9 |
| 11 | this commit | `r11_dep.py` compares revision A32's full hash by its recorded prefix (it compared git's abbreviated hash, whose length is the clone's choice: the box suite on `87dfa55f` failed 11 `test_l4e4` tests because the box's clone printed nine characters); `r11_dep.out` unchanged byte for byte; L4-E4's pin of the script and the one line of `l4e4_limits.out` that prints it updated; `tests/test_r11dep.py` runs the record under abbreviations of 7, 9, 12 and 40 characters |

**The amendment's checks, attributed.** The engineering collaborator (Astra, `gpt-6-astra` at `xhigh`, read-only)
checked the amendment twice, the owner's allowance of one assessment and one targeted follow-up: both read NOT
ACCEPTED (`../l3am/checks/astra-check-l3am-1.md`, `-2.md`), and each finding was answered on `fnd/l3am`. Check 3 is
Claude's (the coordinating session's) verification of B1 and B2 at `cd231260` by its own check
`../l3am/checks/verify_l3am.py` (16 of 16) and the refusal probes; it is not a model review and not an Astra check. A
first draft of check 3, written against `a789a6c2`, was discarded before commit when the test edits of step 3 changed
the amendment's files after it; it was re-issued against `cd231260`, so the closing check's reviewed revision holds the
amendment as it is promoted.

**Layer 4's checks, attributed.** The collaborator checked L4-E2 twice and L4-E3 once (none accepted); each was closed
by the coordinator's own verification of the corrected candidate (`../l4e/checks/check-l4e2-3.md`,
`../l4e/checks/check-l4e3-2.md`); the panel's source compliance stays INCONCLUSIVE under the maker's 10 % qualification.

**Acceptance.** The baseline accepted at `b4b199d0` stays filed until it is superseded. After this set's clean-clone
check and box suite pass on the candidate and the candidate is promoted, `../l3r5/apply_l3r5_accept.py --supersede`
files the acceptance against the promoted revision, with the content manifest the amendment added (L3-R04); the old
record is kept byte for byte in `baseline_acceptance_history`. The results are added below when they exist.

**The first acceptance attempt, at `41881d8f` (not committed).** After promotion the acceptance was filed against
`41881d8f` in the coordinator's worktree, the pages rendered and LAYER-STATUS restated, and the acceptance-guard check read
18 of 18; the Layer 3 modules then read 142 passed and 2 failed on that tree, so nothing was committed and the edits were
set aside (the diff is kept with the session's evidence). Both failures were tests pinned to the state before the
re-acceptance: the supersede test of `test_l3am.py` expected an empty history in its copy, which the tree's own superseded
record now fills; the amendment's status test expected its script to refuse a second run by finding the open status on
LAYER-STATUS.md, which the restatement had removed. The first is corrected in the test (`8146b4cc`), an amendment file, so
check 3 stopped verifying (the binding of B2 doing its work) and check 4 re-verifies the amendment at that revision; the
second is answered on the page, which keeps the open status once as what the layer read until the acceptance. The
acceptance's post-filing state is now simulated before promotion: a single-branch clone holding this set's content, the
acceptance filed there, the pages rendered, the status restated, and every Layer 3 module and check run on it.

## The gates, candidate by candidate

Each suite judged by the coordinator's promotion gate on its log (the candidate named, the last EXIT 0, totals 0 failed
matching the result lines, no load failure, every test module of the candidate's tree ran, the named modules required,
no tracked file changed), never by a wrapper's exit code; every clone `--no-local --single-branch`, the evidence archive
installed (942 files, sha256/16 `e8636c65d84c0250`). Times CEST, 1 October 2026; the box is vast.ai 53619970.

**`7a1523d0` and `41881d8f` (promoted).** The suite on `7a1523d0` (04:23 to 04:46) and on `41881d8f` (04:31 to 04:54):
2378 passed, 0 failed, 3 skipped (host properties: a path pinned by a routing profile exists there, no numba, pcbnew
importable), 201 of 201 modules, gate PASS. The clone of each: every merge present, the render order 0 changed and stable
twice (page `85256b70`), validators 0 errors 0 warnings, the decision pages current, the dry run reproduced, `verify_b2.py`
0 findings, `verify_l3am.py` 16 of 16, the six Layer 3 modules with `test_public_hygiene` 141 passed, 0 failed. Promoted by
fast-forward; the acceptance attempt there is described above.

**`87dfa55f` (not promoted).** The clone (05:59 to 06:21): as above, with `verify_acceptance.py` 18 of 18 and eight modules,
156 passed, 0 failed. The suite (05:59 to 06:22): 2382 passed, 11 failed, 3 skipped, gate FAIL: every failure in
`test_l4e4`, because `r11_dep.py` refused on the box ("revision A32's last commit is not b7e0d28f"): it compared git's
abbreviated hash, and the box's clone prints nine characters for that commit where the runner's prints eight. Fixed in step
11 (`3b4b92cf`), reproduced on the runner first by forcing a longer abbreviation.

**`3b4b92cf` (promoted).** Before it: the pre-acceptance state on the worktree, 144 passed, 0 failed over seven modules; the
post-acceptance simulation (a clone holding step 8's content as a commit, the acceptance filed there, the pages rendered,
the status restated): `verify_l3am.py` 16 of 16, `verify_acceptance.py` 18 of 18, 144 passed, 0 failed. The clone
(06:25 to 06:47): every commit present, the render order 0 changed and stable twice, validators 0 errors 0 warnings, the dry
run reproduced, `verify_b2.py` 0 findings, `verify_l3am.py` 16 of 16, `verify_acceptance.py` 18 of 18; `test_requirements`
66, `test_l3r2` 27, `test_l3r4` 15, `test_l3r5` 21, `test_l3am` 8, `test_l3_reaccept` 3, `test_l4e4` 12, `test_r11dep` 2 and
`test_public_hygiene` 4: 158 passed, 0 failed. The suite (06:25 to 06:48): 2395 passed, 0 failed, 3 skipped (the same host
properties), 204 of 204 modules, the nine above required, gate PASS; the box was stopped after its logs were fetched
(stopped, not destroyed). Promoted by fast-forward: main at `3b4b92cf`, pushed, mirror synced.

## After promotion: the acceptance at `3b4b92cf`

`apply_l3r5_accept.py --supersede` filed the acceptance against `3b4b92cf` under D-39, its evidence the amendment's checks
(check 4 the newest independent check, check 3, the collaborator's two), the dispositions and this record, with the content
manifest of the registry's normative content, the owner brief, the change record and the acceptance policy; the record at
`b4b199d0` is kept in `baseline_acceptance_history`. The pages were rendered and LAYER-STATUS's layer 3 restated by
`../l3am/apply_layer_status_reaccept.py` (the accepted revision and check 4 named, the open status kept once as what the
layer read until then). On the accepted tree: the status level VALIDATED with `acceptance_ok` true; the render order stable twice (page `85256b70`, only the four files of the acceptance changed); validators 0 errors 0 warnings; the dry run reproduced; `verify_b2.py` 0 findings; `verify_l3am.py` 16 of 16; `verify_acceptance.py` 18 of 18; the nine modules 158 passed, 0 failed (06:50 to 07:10).

