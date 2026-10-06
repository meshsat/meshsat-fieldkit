# Set 32: the result of the integration (MESHSAT-1357)

**DONE:** the record of set 32 drafted before its integration: what set 32 adopts and from whom (the two branches as last read, fourteen
commits), W36's independent read and its twelve findings with how each is met or carried, the coordinator's two decisions it applies
(Q-53, Q-55), the re-key they force, W43's dry run as logged, the compute already spent on set 31 that set 32 does not reuse, the three
claims as the assessment gives them, the classification bound. **NOT DONE:** everything the integration will give: set 31's promoted
revision (`__S31_PROMOTED__`), the chain's counts and the freeze's and the gate's lines (`__GATE__`), the re-key (`__REKEY__`), the
candidate (`__CANDIDATE__`) and the promotion (`__PROMOTED__`). **NEXT:** the coordinator fills them from git and the logs at the adoption,
adds the classification's integration rows, and adopts this file with `CLASSIFICATION.md`.

**Status: a draft for adoption** at set 32's promotion (queue item Q-64), written by worker W44 on branch fnd/res32 (base
`3057ae43f4fb7fc5e3d6282ce52d448c8ee27929`, set 31's lineage as the coordinator gave it, `<worktrees>/_runs/claude/w44res32/INBOX.md:3` `(W41's checkpoint commit on set 31's lineage; a committed sha, read-only to you)`)
on 6 October 2026 from 16:36 CEST, in the form of set 31's draft (`records/int31/RESULT.md` on fnd/res31 `4196e9df`, W39) and set 30's
record (`records/int30/RESULT.md`). The coordinator lifted the brief's wait for set 31's candidate (`<worktrees>/_runs/int30/QUEUE.md`, entry "16:36 (clock) W44 LAUNCHED", `the coordinator lifted its own "after set 31's candidate" condition`).
It is record text: its author ran no generator, suite, gate, chain or box job; it accepts nothing, closes nothing, promotes nothing and
changes no verdict. Prototype framing: nothing in the kit has been built, bought, powered or measured; every figure below is a time, a
count, a size or a digest copied from a log or a commit (elapsed times computed from logged stamps say so), and no figure is an
engineering result.

**What set 32 is.** The adoption of (a) the makers' PDF text as committed verbatim inputs of 25 record generators (fnd/w34pdftext: W34,
W37, W42), read independently by W36 with twelve findings; (b) Q-53, the handover ZIP's cap raised to 100 MiB with its reason
(fnd/s32small, W40); (c) Q-55, N1a's phrase carried into V-E16 row 3 by W40's apply script, with W47's change-record row and
`TP-SOLAR.md`'s quote of the annotated line (Q-65); (d) the l4e7 re-key that (a) and (c) force,
and the regeneration of every output they move. It closes NO power item, is not power-design closure and releases nothing; Layer 4's DESK
gate stays NOT PASSED as the coordinator judged it (section 6).

**What governs it.** The owner's part 25 (`3057ae43:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:845` `Use the existing integration gate to record the reviewed and integrated revisions and the intervening changes.`)
and the constitution's section 2 (`3057ae43:v2/docs/EXECUTION-CONSTITUTION.md:23` `Report engineering-handover readiness, power-design closure and fabrication release separately. A promoted integration set is none of those by itself.`).
No blended percentage is given anywhere in this file.

**Citations.** `<sha>:path:N` followed by a code span quotes line N of that file at that revision; `<worktrees>/_runs/<path>:N`
followed by a code span quotes line N of a coordinator's or worker's file outside the repository (`<worktrees>` is the folder holding the
worktrees); the growing queue file is quoted by its dated entry (`<worktrees>/_runs/int30/QUEUE.md`, entry "...", then the quote, found
in the file). A log path written with `<HHMM>` is one the chain will write; it does not exist yet. `test_res32.py` reads every quote,
every commit named, every count and every placeholder.

## 1. The candidate

| Role | Revision | State as given | Source |
|---|---|---|---|
| BASE (the REVIEWED role of the brief's form): set 31's promoted revision | `__S31_PROMOTED__` | not yet promoted when this record was written; once promoted, a DESK candidate, not an accepted power design, and no independent check read it. The last independent check of the power candidate is cx46 on `4d0ff8a2`, "P0 RECHECK: CORRECTIONS NOT CLOSED." | `3057ae43:v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:10` `"summary": "P0 RECHECK: CORRECTIONS NOT CLOSED.` |
| The lineage this record's branch was cut from | `3057ae43f4fb7fc5e3d6282ce52d448c8ee27929` (fnd/int31regen, W41's checkpoint) | set 31's lineage before its re-key, candidate and promotion; set 32's branches merge onto set 31's promoted revision, never onto this commit | the INBOX line above |
| Branch A: fnd/w34pdftext | `5b3153aa4136f08ab186a2b5da53c1c4f0c3ecac` | 10 commits over `aed4bd234644c80fa494299b21099acf6d2454c1` (its merge base with set 31's lineage), no merge, no output committed; W36 read its commit `6dc69ad2` (section 2b) | `git rev-list --count aed4bd23..5b3153aa`; `git merge-base 3057ae43 5b3153aa` |
| Branch B: fnd/s32small | `7b7219a7d0a695b6b866435116905964a68f5578` | 4 commits over `eff28be3b80f882db545a849b0da1def0217f63d` (main's follow-up after set 30's adoption), no merge, no output committed; no independent reader; W40's two commits to `a7a485ab`, then W47's two | `git rev-list --count eff28be3..7b7219a7` |
| The re-key's cache commit | `__REKEY__` | record l4e7's results cache re-keyed on a fresh debian:12 box after the converged commit and its independent read (section 3c) | the coordinator's commit on set 32's integration branch |
| INTEGRATED = CANDIDATE: the candidate commit | `__CANDIDATE__` | no independent check of its engineering | the coordinator's commit on set 32's integration branch |
| PROMOTED: main after the fast-forward | `__PROMOTED__` | a DESK candidate, not an accepted power design (section 6) | the promotion's log |

## 2. What changes (each branch, its finding, W36's conditions, the coordinator's decisions)

**The classification is bound by its path:** `v2/docs/records/int32/CLASSIFICATION.md`, adopted with this file. It classes each of the
14 commits of the two branches over their bases (fnd/w34pdftext 10, fnd/s32small 4; no merge) into W39's fixed set, and counts, first
class per row: REVIEWED-INPUT CHANGED 0; RECORD TEXT 7; GENERATOR DATA (text) 0; TEST 0; DIGEST RE-PIN 0; MERGE 0; TOOLING 7; total 14.
4 of the 14 touch a file cx46 read (8 files: seven generators' input route and the annex's citation line numbers); each is **UNREVIEWED
since cx46**, never credited. None is classed REVIEWED-INPUT CHANGED, because none changes a figure, state word, composition, case,
requirement or limit in a reviewed file (a SESSION decision under the owner's standing rule of 26 September 2026, stated with its wider
alternative, four rows, in that file). The integration's own commits (the merges, the converged outputs, the re-key, the candidate) are
placeholder rows there; the outputs they regenerate include files cx46 read.

### 2a. The branches, in the chain's merge order

| Branch | Rows | Author, queue item | Finding or decision answered | What it does |
|---|---|---|---|---|
| fnd/w34pdftext | 1 to 5 | W34, Q-50 (Q-41 item 1) | set 30's first box pass, in the coordinator's values file: `<worktrees>/_runs/int30/ADOPTION-VALUES.md:12` `149 failures were the boxes' missing poppler-data` (the records extract makers' PDFs at run time); Q-41 item 1 (below the table) | 25 record generators read each maker's PDF text through `_lib/pdftext.py` from a committed verbatim extraction instead of running pdftotext; 171 extractions committed beside their PDFs with a sidecar each (342 files), 52 held back with their held sheets; the re-take script, the inventory, `test_pdftext_input`; in W34's words, `5b3153aa:v2/docs/records/_lib/PDFTEXT-INVENTORY.md:9` `This branch changes HOW a generator obtains a maker's PDF text, never WHAT it computes from it: no verdict, figure,` |
| fnd/w34pdftext | 6 to 8 | W37, Q-56 | W36's F-P1, F-P2, F-R1, F-R2, F-K5, F-C1 (section 2c) | the inventory restated (what still reads the host's poppler; the fetch route per held sheet; the integration order upstream first), `pdftext.FETCH`, the re-take's `.gitignore` check, generator runs with the tools refused in the regression, the supplier page's section 7 re-take step; the integration plan draft outside the tree (`<worktrees>/_runs/int32/PLAN.draft.md`) |
| fnd/w34pdftext | 9, 10 | W42, Q-61 | W36's F-K4 in the live pages | six citations into the edited generators re-pointed (the annex's five `[E11PY:n]` by 62 lines, the ledger's `[PAL:186-255]` to `[PAL:201-270]`), the citations bound to a commit and the filed checks left; the supplier page's section 0e sentence as `w42cite/apply_supplier_0e_pointer.py`; TP-E11-29's two prose citations left as a row for the chain (it pins `tp_check.out`) |
| fnd/s32small | 11 | W40, Q-59 (Q-53) | W36's F-S1, decided by the coordinator (section 2d) | `pack.yaml`'s `max_zip_bytes` from 52,428,800 to 104,857,600 with its reason, the old comments dated, a test of the cap and of the estimate's positive margin |
| fnd/s32small | 12 | W40, Q-59 (Q-55) | the record's own invariant, V-E16 mirrors the register (section 2d) | `s32small/apply_q55_ve16.py`, run on the merged tree only: N1a's phrase into V-E16 row 3 of `HW-FW-CONTRACT.md`, `test_w8l5`'s tree check, `test_l5pwr`'s L5-F09 d reading; the README with Q-53's estimator readings |
| fnd/s32small | 13, 14 | W47, Q-65 | W40's and W43's left-outs: Q-55's change-record row and `TP-SOLAR.md` line 297's quote of V-E16 row 3 | the same script's edits 5 and 6 (one change-record row in `HW-FW-CONTRACT.md`; the register's annotated U5 line as `TP-SOLAR.md`'s own quote beside line 297, with a dated lead-in) and `test_w8l5`'s check of both; the README with the scratch-clone check and the added step (regenerate `tp_check.out`) |

Q-41 item 1, as the queue states it: `<worktrees>/_runs/int30/QUEUE.md`, entry "| Q-41 |", `pin the EXTRACTED TEXT as a verbatim input beside the PDF`.
Neither branch commits a `.out`, a baseline circuit draft, a board generator or a netlist (`CLASSIFICATION.md`, its preamble).

### 2b. W36's independent read (of fnd/w34pdftext at `6dc69ad2`, before W37's and W42's commits)

W36 read the branch's first five commits read-only on scratch clones (`<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:30` `five commits over`)
and labels its own read: `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:31` `This is an AI review, not a qualified review.` Its
evidence on the computation, as received: `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:47` `Every new output equals old plus added lines only: efuse +17, l5r2 +7`
(batch 1) and the texts `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:56` `223 checked; 223 byte-identical; 0 differ; 52 held`;
what it did not run: `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:127` `ripple_dense was not run`. Its verdict:
`<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:135` `The branch is fit for set 32's adoption on conditions.` The five commits
after `6dc69ad2` (rows 6 to 10: W37's three and W42's two) and fnd/s32small's four were read by no independent reader; set 32's lineage
read is a later queue item, after the chain (section 8).

### 2c. W36's twelve findings and how each is met or carried

ANSWERED means a branch or the chain carries a change written for the finding; it is not a verdict that the finding is closed, and
none of these answers was re-read by W36 or by any other independent reader. CARRIED means the answer is a later step's. STATED
means the finding is written down and nothing else changed.

| Finding | W36's words (as received) | Answered or carried | Where it is read |
|---|---|---|---|
| F-C1 (computation, minor) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:50` `**F-C1** (minor; W34 disclosed it at inventory lines 167-168)` | STATED (row 8): l4e12's count line moves with the widened pins dict, now `3057ae43:v2/docs/records/l4e12/l4e12_thermal.out:14` `0e 69 inputs pinned by sha256 (the list ends this output)`; CARRIED to the chain's diff read | `__GATE__` |
| F-P1 (provenance) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:14` `A close fourth is **F-P1**` | ANSWERED in the branch (row 6): `5b3153aa:v2/docs/records/_lib/PDFTEXT-INVENTORY.md:203` `**What still reads the host's poppler (restated by W37, 6 October 2026, on W36's finding F-P1;` | the inventory |
| F-P2 (provenance, minor) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:65` `**F-P2** (minor)` | ANSWERED in the branch (rows 6 and 8: `pdftext.FETCH`, the route per held sheet) | the inventory, section 3 |
| F-R1 (regression) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:80` `no test runs a generator with the fake on PATH, and (d) is syntactic only.` | ANSWERED in the branch (row 6, its subject: "11 passed") | `test_pdftext_input` in the chain's test group 1 (`__GATE__`) |
| F-R2 (regression, minor) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:81` `the untested CHANGED and not-ignored paths, and orphan texts.` | ANSWERED in the branch (row 6) | the same |
| F-S1 (size) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:88` `margin -17812603 bytes (OVER THE CAP)` | ANSWERED by the coordinator's decision Q-53 and W40's row 11; the next handover build's own margin is not measured here | `__GATE__` |
| F-S2 (size, minor) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:89` `**F-S2** (minor)` | CARRIED: the rule `"v2/docs/records/_lib/**",` in the runner-local `_bin/pack_supplier.py` INCLUDE list is the coordinator's (`<worktrees>/_runs/int32/README.md:80` `(lines 22 to 43): add`), not in either branch | the next supplier delta |
| F-K1 (consequence) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:106` `**F-K1**: the order runs backwards` | ANSWERED in W37's text (row 8) and in W43's chain order, steps d1 to d15 (`<worktrees>/_runs/int32/README.md:37` `W36's F-K1: W34's inventory had the order backwards`); its run is the chain's | `__GATE__` |
| F-K2 (consequence) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:107` `**F-K2**: l4e12 refuses until its source is re-pinned by hand` | CARRIED to the chain's step d2 (`repin_l4e8_out.py`, guarded), on the pin `5b3153aa:v2/docs/records/l4e12/l4e12_thermal.py:169` `L4E8_OUT: "c6181037bede1fec6b183bcb1d8eab66e0023bc23ae5e5374be4d22eedaf4333",` | `__GATE__` |
| F-K3 (consequence) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:108` `**F-K3**: W34 names only the re-key and a general regen_targeted pass, not these dependents` | CARRIED to the coordinator's step after the re-key (`_runs/int31/dependents.sh`, its base `dd1aed00` to be set to set 32's base first, `<worktrees>/_runs/int32/README.md:61` `types base`, at its d1 and d3) | `__REKEY__`, `__GATE__` |
| F-K4 (consequence, minor) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:109` `There are 108 such citations in 28 tracked files, most of them in filed checks.` | PARTLY ANSWERED: W37's classed list (`<worktrees>/_runs/int32/PLAN.draft.md:78` `the difference is not resolved here`), W42's six re-pointed citations (row 9), TP-E11-29's two at the chain's step a5; the citations INTO outputs are owed a re-take after the regeneration (W43's step h, item 2) | `__GATE__` |
| F-K5 (consequence) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:110` `**F-K5**: for held sheets the host dependence moves from the reading to the re-take, and the supplier page lacks the step` | ANSWERED in the branch for the page's section 7 (row 7, `5b3153aa:v2/docs/handover/supplier/SUPPLIER-HANDOVER.md:158` `python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/<record>`); section 0e's sentence by `apply_supplier_0e_pointer.py` at the chain's step a5 (row 10) | `__GATE__` |

W36's other condition, the 52 held texts staged on every host that runs a converted record, is the chain's step b (section 3a: the dry
run staged 52 of 52) and, for a box, a held tar cut from the integration worktree after that step, with pdftotext 22.12.0 and
poppler-data on the box (`<worktrees>/_runs/int32/README.md:75` `converted records' tests needs a held tar cut from the integration worktree after step b`).

### 2d. The coordinator's two decisions set 32 applies

- **Q-53** (authority SESSION under the owner's standing rule): `<worktrees>/_runs/int30/QUEUE.md`, entry "13:35 (clock) Q-53 DECIDED", `rises from 52,428,800 to 104,857,600 (100 MiB) with its reason written in pack.yaml`;
  applied by row 11. The estimator's reading at main, as W40's record gives it: `a7a485ab:v2/docs/records/s32small/README.md:24` `Readings (the estimator writes nothing): at eff28be3,`
  `a7a485ab:v2/docs/records/s32small/README.md:24` `ESTIMATE: 70175272 bytes; H2 was 51894737; cap 52428800; margin -17746472`.
  H3's estimator output keeps its `089f7f27` reading (a plain regeneration would put the current HEAD under the name "H3"); a new record
  carries the current reading after the candidate (section 8).
- **Q-55**: `<worktrees>/_runs/int30/QUEUE.md`, entry "| Q-55 |", `in set 32 with its re-key`; applied at the chain's step a4 by row
  12's script on the merged tree, where the dry run read `<worktrees>/_runs/int32/dryrun-1632.log:25` `apply_q55_ve16: v2/docs/HW-FW-CONTRACT.md f26757c7c5004cdd -> c52eaa5f4ba501ab`;
  the two typed `hwfw` pins follow at step e1 (`<worktrees>/_runs/int32/dryrun-1632.log:94` `would re-pin l4e9_power_path.py hwfw`,
  `<worktrees>/_runs/int32/dryrun-1632.log:95` `would re-pin l4e11_power.py hwfw`). The change-record row for Q-55 and `TP-SOLAR.md`
  line 297's quote of V-E16 row 3, W43's step a6 items, are now the same script's edits 5 and 6 (rows 13 and 14; W47's brief:
  `<worktrees>/_runs/claude/w47s32txt/BRIEF.md:1` `set 32's two residual record-text items on fnd/s32small`); once applied, `TP-SOLAR.md`
  moves `tp_check.out`, which the chain regenerates (step d14). W47 found the second item's premise wrong and took a narrower edit:
  `<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W47 at about 16:56 CEST", `the brief's premise was WRONG (line 297 quotes L4E7-CONTROL-DECISION.md, which has no N1a words, so the quote is already verbatim)`.
  Whether step a6 is then acknowledged without a further hook is the coordinator's (`__GATE__`).

### 2e. The re-key that (a) and (c) force

`<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:105` `Of the KEY's 178 files, only` `l4e11_power.out` is a converted
generator's output, and set 32 moves it three ways: `<worktrees>/_runs/int32/README.md:51` `and set 32 moves it three ways: W34's`
(the conversion's text lines, 68 on W36's old-against-new run, its report's line 47; Q-55's page through the `hwfw` pin; the
freeze's re-pin of the page). The chain's step f must read the
KEY MISMATCH on that file alone; the re-key follows the converged commit and its independent read, never before (section 3c).

## 3. The integration, measured

### 3a. W43's dry run (a stand-in base; measured, not the chain)

- **Its base** was set 31's lineage tip, not set 31's promoted revision (which did not exist):
  `<worktrees>/_runs/int32/dryrun-1632.log:1` `== set 32 chain at 2026-10-06 16:32:57 CEST: base 3057ae43`; scratch clone, branches
  fnd/w34pdftext `5b3153aa` and fnd/s32small `a7a485ab` (W47's two commits came after it).
- **a1:** `<worktrees>/_runs/int32/dryrun-1632.log:6` `main (eff28be3) is in the lineage: yes, no merge`.
- **a2, one conflict predicted:** `<worktrees>/_runs/int32/dryrun-1632.log:10` `pdftext: CONFLICTS predicted (git merge-tree), 1 file(s):`,
  `<worktrees>/_runs/int32/dryrun-1632.log:11` `v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md`; set to ours in the
  scratch clone only (`<worktrees>/_runs/int32/dryrun-1632.log:14` `conflicts set to ours in the scratch clone only (not a resolution)`);
  W43's resolution rule for the real chain: keep both clauses, set 31's first (`<worktrees>/_runs/int32/README.md:97` `Resolution: keep both clauses, set 31's first`).
- **a3:** `<worktrees>/_runs/int32/dryrun-1632.log:18` `s32small: no conflict predicted`.
- **b:** `<worktrees>/_runs/int32/dryrun-1632.log:66` `removed 107 foreign files, never added; untracked now: 0`;
  `<worktrees>/_runs/int32/dryrun-1632.log:67` `held texts present: 52 (expected 52); sidecars: 52`;
  `<worktrees>/_runs/int32/dryrun-1632.log:68` `held texts byte-identical to`.
- **c:** `<worktrees>/_runs/int32/dryrun-1632.log:89` `placeholders: every occurrence deferred` (13 files with their reasons in
  `<worktrees>/_runs/int32/placeholders-deferred.tsv`; this record's three files carry declared tokens too: section 8).
- **d, the selection only:** `<worktrees>/_runs/int32/dryrun-1632.log:148` `round 1 would select: 31 pairs`; regen_targeted alone does
  not select seven converted outputs, which the chain's explicit steps carry (`<worktrees>/_runs/int32/README.md:41` `does NOT select seven converted outputs`).
- **One record regenerated (efuse):** `<worktrees>/_runs/int32/dryrun-1632.log:155` `regen_out: v2/docs/records/efuse/efuse_check.out replaced (69230 bytes, sha256 46d1dede3ef0cfe2)`,
  `<worktrees>/_runs/int32/dryrun-1632.log:157` `1 file changed, 17 insertions(+)`, the same count W36 measured for efuse (section 2b).
- **The KEY, informational:** `<worktrees>/_runs/int32/dryrun-1632.log:176` `l4e7 KEY MISMATCH committed df9030eaf2c8e7bf now 1623624b2ac67635; parts moved: files`,
  `<worktrees>/_runs/int32/dryrun-1632.log:177` `file v2/docs/records/l4e11/l4e11_power.out: a2089b3f6682 -> 4496ea7a4aa9`: set 31's own re-key is
  still owed on the stand-in base, so this line says nothing about set 32's KEY.
- **End:** `<worktrees>/_runs/int32/dryrun-1632.log:184` `== DRY RUN done at 2026-10-06 16:33:50 CEST`. Measured duration (computed
  from the logged stamps): 16:32:57 to 16:33:50, 53 s, of which the efuse regeneration took 25 s
  (`<worktrees>/_runs/int32/dryrun-1632.log:156` `took 25 s`).

### 3b. The chain (W43's `_runs/int32/chain.sh` on set 31's promoted revision; every value from its log)

The chain's log is the path given as its second argument (`_runs/int32/chain-<HHMM>.log`); its targeted pass writes
`<worktrees>/_runs/int32/chain.sh:284` `TL=$I32/targeted-$HHMM.log` and its two test groups
`<worktrees>/_runs/int32/chain.sh:324` `TF=$I32/tests-g$grp-$HHMM.log`.

| Step | What the coordinator reads | Expected, as written before the run | Result |
|---|---|---|---|
| a2, a3: the two merges | the chain's log; the merge commits | one conflict, the annex's line 136, resolved by hand (both clauses, set 31's first); fnd/s32small clean | `__GATE__` |
| a4: Q-55's script | the chain's log | `HW-FW-CONTRACT.md` and two tests change, nothing else | `__GATE__` |
| a5: W42's two applies | the chain's log | section 0e's sentence; TP-E11-29's lines 791 and 794 re-cited | `__GATE__` |
| a6: the coordinator's input items | the chain's log | applied or declined before any re-pin | `__GATE__` |
| b: held material | the chain's log | 52 texts, 52 sidecars, byte-identical, all ignored | `__GATE__` |
| e1, d2: the typed pins and `L4E8_OUT` | the chain's log | two `hwfw` re-pins; `L4E8_OUT` after ripple_dense | `__GATE__` |
| d1 to d11: the regeneration in W36's order | the chain's log | each output gains only its text lines and moved source pins (l4e12's count line apart); a figure that moves is a defect of the branch (`<worktrees>/_runs/int32/PLAN.draft.md:71` `gains only its text lines and moved source pins (inventory section 4); a figure that moves is a defect of the branch.`) | `__GATE__` |
| d6, d7: the cascade twice | the chain's log | the second pass "already identical" for every output | `__GATE__` |
| d12: regen_targeted, base `__S31_PROMOTED__`, to convergence | `_runs/int32/targeted-<HHMM>.log` | a round with 0 replaced; only the three by-design refusals | `__GATE__` |
| d15: stability | the chain's log | the L4 five, the cascade once, 0 re-pins | `__GATE__` |
| The converged commit | `git log` on set 32's integration branch | committed before the independent read and before the re-key | `__GATE__` |
| The diff read of the converged outputs | the commit's diff | every changed line a text-input line, a moved source pin or a digest, l4e12's count line apart | `__GATE__` |

### 3c. Record l4e7's results cache (the KEY)

The chain's step f expects a MISMATCH on the KEY's "files" part with `l4e11_power.out` alone
(`<worktrees>/_runs/int32/chain.sh:310` `if go f "the l4e7 KEY-only check (MISMATCH expected on l4e11_power.out alone)"; then`); the
re-key runs on a fresh debian:12 box under a new label (`<worktrees>/_runs/int32/chain.sh:348` `3. the re-key on a fresh debian:12 box: LABEL_GIVEN=meshsat-1357-rekey10`)
after the converged commit, the re-take of the citations into outputs and the independent read, never before (set 31's rekey9 was spent
for that order: `<worktrees>/_runs/int31/rekey9/SPENT.txt:1` `SPENT: the re-key of 562edf6a`). The KEY on the candidate after the
re-key and the dependents: `__REKEY__`.

### 3d. The tests

| When | Run | Result as printed | Cause of each failure, and the fix |
|---|---|---|---|
| step d12 | the targeted pass's affected set (`_runs/int32/targeted-<HHMM>.log`) | `__GATE__` | `__GATE__` |
| step g, group 1 | set 32's own modules (`_runs/int32/tests-g1-<HHMM>.log`) | `__GATE__` | `__GATE__` |
| step g, group 2 | the regenerated records and the integration modules (`_runs/int32/tests-g2-<HHMM>.log`) | `__GATE__` | `__GATE__` |

## 4. The freeze and the gates (the coordinator's; every value to be copied from the logs, never typed)

| Step | Where the coordinator reads it | Result |
|---|---|---|
| The converged commit and the re-take of the citations into outputs | `git log` on set 32's integration branch | `__GATE__` |
| The independent read of set 32's lineage, its findings corrected | the reader's report | `__GATE__` |
| The re-key's cache commit and the KEY on it | the cache commit; the KEY check's line | `__REKEY__` |
| The re-key's dependents regenerated (l4e7_p0sol, L4-E9's `l4e7p0` pin, l4e9, l5pwr_contracts, l9t5_connected, l6r2_passives, l8p_c4; W36's F-K3) | the dependents' log | `__GATE__` |
| The evidence archive installed before the manifest | the freeze's log | `__GATE__` |
| The candidate commit | `git log` on set 32's integration branch | `__CANDIDATE__` |
| The manifest (candidate_guard record) and the evidence tar | `__GATE__` | `__GATE__` |
| candidate_guard check, every host | `__GATE__` | `__GATE__` |
| Box pass A (every module but the runner's and the records box's) | `__GATE__` | `__GATE__` |
| Box pass B, Python 3.11 | `__GATE__` | `__GATE__` |
| Records box pass (debian:12, pdftotext 22.12.0, poppler-data, the held tar cut after the chain's step b) | `__GATE__` | `__GATE__` |
| Runner pass (`test_l4e7`, and the modules that read `_runs`, section 8) | `__GATE__` | `__GATE__` |
| suite_gate with G7 over the logs | `__GATE__` | `__GATE__` |
| Promotion: fast-forward of main, push, the mirror, the guard on main | `__GATE__` | `__PROMOTED__` |
| Targeted verification of the rows UNREVIEWED since cx46 (`CLASSIFICATION.md`, four branch rows and the integration's rows) | the coordinator's choice of verifier; not the ended review method | owed; none performed |

## 5. Compute (compute and storage kept apart, no total computed)

**Spent on set 31 and not reused by set 32** (both stopped with their disks kept; set 32 rents its own box under a new label):

- **54468046, rekey8 (debian:12):** `<worktrees>/_runs/vast/LOG-20261006.md:14` `on offer 45602172 (debian:12, Poland, 0.058 USD/h`;
  its recompute on `aed4bd23` killed, `<worktrees>/_runs/vast/LOG-20261006.md:15` `the recompute on aed4bd23 KILLED (W29's finding F3`;
  stopped idle, `<worktrees>/_runs/vast/LOG-20261006.md:16` `STOPPED by the idle watchdog at 15:10:11 after 2.17 h idle (disk kept`.
- **54487140, rekey9 (debian:12):** `<worktrees>/_runs/vast/LOG-20261006.md:17` `RENTED 54487140 meshsat-1357-rekey9`; its recompute
  on `562edf6a` spent and killed, `<worktrees>/_runs/vast/LOG-20261006.md:18` `the SPENT recompute (562edf6a) killed by the coordinator at poll 60`;
  stopped, `<worktrees>/_runs/int31/rekey9-chain-1515.log:37` `stop sent: b'{"success": true}'` (the vast log's line 19 labels this
  stop "rekey8" with the instance number 54487140, quoted as written: `<worktrees>/_runs/vast/LOG-20261006.md:19` `54487140 rekey8: STOPPED after the fetch (disk kept)`).
- **Set 31's own next re-key** (on W41's commit) is set 31's record's (`records/int31/RESULT.md` section 5 on fnd/res31), not this set's.
- **When this record was written no instance ran:** `<worktrees>/_runs/vast/CREDIT-READINGS.tsv:1` `no instance running (all eleven stopped)`;
  none of the eleven stopped disks is destroyed, and their artifact inventory is W46's (queue item Q-63,
  `<worktrees>/_runs/vast/INVENTORY-2026-10-06.md:1` `# Artifact inventory of the eleven stopped vast.ai instances`; its sections
  3.10 and 3.11 are the two boxes above).

**Set 32's own** (none rented when this record was written):

- the re-key box (debian:12, label `meshsat-1357-rekey10`, section 3c): `__REKEY__`;
- the suite boxes of the freeze, and the records box with pdftotext 22.12.0, poppler-data and the held tar cut after the chain's step b
  (W37's plan, section 1): `__GATE__`.

## 6. What set 32 closes and what it does not

**Set 32 closes NO power item.** It adopts a change of how 25 record generators read their makers' PDF text (W36 read the computation
unchanged on the runs it made, section 2b), a packaging cap, one phrase carried into a contract row with its change-record row and a
procedure's quote, and the regenerated outputs and pins they move. It changes no baseline circuit draft, no board generator and no netlist (`CLASSIFICATION.md`, its preamble). None of its
14 branch commits is classed REVIEWED-INPUT CHANGED; the 4 that touch files cx46 read are UNREVIEWED since cx46 and none is credited.

**Layer 4's DESK gate stays NOT PASSED** as the coordinator judged it on set 30, in the assessment's words (set 32 changes no line of it):

- `3057ae43:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:492` `### Layer 4's DESK gate: NOT PASSED`
- `3057ae43:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:494` `The gate's own premise is not met.`

**The three completion claims, unchanged, each with its own state** (the constitution's section 2; never blended):

| Claim | State | Basis |
|---|---|---|
| Engineering-handover readiness | READY AS A DESK PACKAGE OF OPEN ITEMS | `3057ae43:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:496` `### Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS`, with its own limit `3057ae43:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:498` `"Ready" here means complete and internally consistent as a package of open items, not that any item is resolved.` |
| Power-design closure | BLOCKED | `3057ae43:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:500` `### Power-design closure: BLOCKED. Fabrication release: BLOCKED.` |
| Fabrication release | BLOCKED | the same line |

Kept apart from all three: documents and editable artifacts (a DESK candidate once promoted, `__PROMOTED__`); design reviewed and
accepted (NO: cx45 NOT CONFIRMED, cx46 CORRECTIONS NOT CLOSED, and the unreviewed changes of sets 30, 31 and 32); circuit changes
implemented (NONE); physical qualification (NONE). A promoted integration set is none of the three claims by itself.

## 7. The records this result binds

| Record | Path | State |
|---|---|---|
| The classification of set 32 | `v2/docs/records/int32/CLASSIFICATION.md` | 14 branch commits classified; 4 UNREVIEWED since cx46; three placeholder rows for the integration's commits |
| W34's inventory, with W37's restatements | `v2/docs/records/_lib/PDFTEXT-INVENTORY.md` on fnd/w34pdftext | in the tree from the merge |
| W40's and W47's record | `v2/docs/records/s32small/README.md` on fnd/s32small | in the tree from the merge |
| W42's record | `v2/docs/records/w42cite/README.md` on fnd/w34pdftext | in the tree from the merge |
| W36's report, W37's plan draft, W43's chain and README | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md`, `<worktrees>/_runs/int32/PLAN.draft.md`, `<worktrees>/_runs/int32/README.md`, `<worktrees>/_runs/int32/chain.sh` | outside the repository; cited, never copied (they carry host paths) |
| Set 31's records | `v2/docs/records/int31/RESULT.md` and `CLASSIFICATION.md` on fnd/res31 `4196e9df` | adopted at set 31's promotion; not in this record's branch history |
| The assessment and the three claims | `v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md` | in this branch's history since main's adoption was merged into set 31's lineage (`d5d9c252`) |

## 8. Left out, and why

- **Commits after the tips as last read** (fnd/w34pdftext `5b3153aa`, fnd/s32small `7b7219a7`) are not classified here; the coordinator
  adds their rows at the adoption.
- **The coordinator's items outside the tree:** `_bin/pack_supplier.py`'s INCLUDE rule for `_lib` (F-S2); the base typed in
  `_runs/int31/dependents.sh` and the wording of `_runs/int31/cache_commit.sh` before their reuse (W43's README section 3);
  `<worktrees>/_runs/int32/placeholders-deferred.tsv` needs a row for each of this record's three files before the chain's step c reads
  a tree that holds them (they carry the declared token `__CANDIDATE__` by design).
- **Open from W36's report, not settled by any branch:** ripple_dense's old-against-new run, the poppler-data dependence measured on a
  box, pdftocairo's host sensitivity, a built ZIP (W36's "Not checked" list), and the difference between W36's 108 and W37's 106 moved
  citations.
- **H3's estimator output** keeps its `089f7f27` reading; the current reading belongs in a new record made with the candidate's commit
  under its own version name (W40's README).
- **The citations into outputs** (`[E11:n]`, `[F01:n]`, `[CON:n]` and the rest) are owed a re-take after the regeneration and before
  the re-key (W43's step h, item 2); they cannot be read before the outputs exist.
- **The independent read of set 32's lineage** is a later queue item, after the chain; this record names no finding of it.
- **A note for the freeze:** `test_res32`'s predicate that reads the coordinator's files raises Skip where `_runs` is absent, which is
  every rented box; run it in the runner pass, as W39 recommended for `test_res31` (taken as this record's recommendation under the
  owner's standing rule of 26 September 2026; the coordinator applies or reverses it).
- No generator, suite, gate, chain, candidate_guard, regen_out or box job was run by this record's author; every chain, test and compute
  line is copied from the logs named.
