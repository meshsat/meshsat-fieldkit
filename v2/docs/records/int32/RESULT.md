# Set 32: the result of the integration (MESHSAT-1357)

**DONE:** the record of set 32 drafted before its integration and brought to every branch set 32's chain pins: what set 32 adopts and
from whom (five branches, thirty commits, among them WP-B's six on record l4e7's results cache), the independent reads of them and their
verdicts as given (W36, W52, W64, W70: AI reviews, not qualified ones), the coordinator's decisions it applies (Q-53, Q-55), the ONE
re-key set 32 is planned to carry and why one, the dry runs as logged, the compute already spent that set 32 does not reuse, the three
claims as the assessment gives them, the classification bound. **NOT DONE:** everything the integration will give: set 31's promoted
revision (set 32's base), the chain's counts and the freeze's and the gate's lines, the re-key's cache commit, the candidate, the
promotion and the adoption commit, each a placeholder that the coordinator's fill tool fills (the paragraph "Placeholders" below).
**NEXT:** the coordinator fills them from git and the logs at the adoption, writes the classification's integration rows in full, and
adopts this file with `CLASSIFICATION.md`.

**Status: a draft for adoption** at set 32's promotion (queue item Q-64), written by worker W44 on branch fnd/res32 (base
`3057ae43f4fb7fc5e3d6282ce52d448c8ee27929`, set 31's lineage as the coordinator gave it, `<worktrees>/_runs/claude/w44res32/INBOX.md:3` `(W41's checkpoint commit on set 31's lineage; a committed sha, read-only to you)`)
on 6 October 2026 from 16:36 CEST, in the form of set 31's draft (`records/int31/RESULT.md` on fnd/res31 `4196e9df`, W39) and set 30's
record (`records/int30/RESULT.md`). The coordinator lifted the brief's wait for set 31's candidate (`<worktrees>/_runs/int30/QUEUE.md`, entry "16:36 (clock) W44 LAUNCHED", `the coordinator lifted its own "after set 31's candidate" condition`).
Worker W50 restated its classification rule under the coordinator's ruling of 17:13 (reading A). Worker W73 brought it to every branch
the chain pins from 20:23 CEST (`<worktrees>/_runs/int30/QUEUE.md`, entry "20:23:00 (clock) W73 LAUNCHED", `set 32's record skeleton on fnd/res32 brought up to every branch chain.sh pins`).
It is record text: its authors ran no generator, suite, gate, chain or box job; it accepts nothing, closes nothing, promotes nothing and
changes no verdict. Prototype framing: nothing in the kit has been built, bought, powered or measured; every figure below is a time, a
count, a size or a digest copied from a log or a commit (elapsed times computed from logged stamps say so), and no figure is an
engineering result.

**What set 32 is.** The adoption of (a) the makers' PDF text as committed verbatim inputs of 26 record generators (fnd/w34pdftext: W34,
W37, W42, and W55's correction for `l8p_c4.py`), read independently by W36 with twelve findings; (b) W53's attribution of each verdict
word to its check at the remaining sites (fnd/s32attr: cx45's "NOT CONFIRMED", cx46's "NOT CLOSED"); (c) Q-53, the handover ZIP's cap
raised to 100 MiB with its reason (fnd/s32small, W40); (d) Q-55, N1a's phrase carried into V-E16 row 3 by W40's apply script, with W47's
change-record row and `TP-SOLAR.md`'s quote of the annotated line (Q-65); (e) WP-B, record l4e7's results cache KEY holding the sixteen
numbers the record reads of `l4e11_power.out` instead of the file's bytes (fnd/l4e7cache: W61, W67, W71), read independently by W64 and
rechecked by W70; (f) this record (fnd/res32); (g) ONE re-key of record l4e7's results cache that (a), (d) and (e) together force, and the
regeneration of every output they move. It closes NO power item, is not power-design closure and releases nothing; Layer 4's DESK gate
stays NOT PASSED as the coordinator judged it (section 6).

**What governs it.** The owner's part 25 (`3057ae43:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:845` `Use the existing integration gate to record the reviewed and integrated revisions and the intervening changes.`)
and the constitution's section 2 (`3057ae43:v2/docs/EXECUTION-CONSTITUTION.md:23` `Report engineering-handover readiness, power-design closure and fabrication release separately. A promoted integration set is none of those by itself.`).
No blended percentage is given anywhere in this file.

**Citations.** `<sha>:path:N` followed by a code span quotes line N of that file at that revision; `<worktrees>/_runs/<path>:N`
followed by a code span quotes line N of a coordinator's or worker's file outside the repository (`<worktrees>` is the folder holding the
worktrees); a file that its writer is still changing (the chain script and its README) is quoted without a line number, the quote found
in the file; the growing queue file is quoted by its dated entry (`<worktrees>/_runs/int30/QUEUE.md`, entry "...", then the quote, found
in the file). A log path written with `<HHMM>` is one the chain will write; it does not exist yet. `test_res32.py` reads every quote,
every commit named, every count and every placeholder.

**Placeholders.** Only the five token names the coordinator's fill tool fills appear (`<worktrees>/_runs/int31/freeze/fill_res31.py`, its
pattern TOK; W73's restatement, so the same tool can be pointed at set 32's files): REKEY (the re-key's cache commit), CANDIDATE (the
candidate commit), GATE (a log line, written as text), PROMOTED and ADOPTION, each written between two pairs of underscores. The tool
fills each occurrence by its file, line and place, so one name can stand for two commits: PROMOTED stands for set 31's promoted revision
where its line names set 31 (set 32's base: one occurrence, section 1's BASE row) and for set 32's promotion where its line names
set 32 (three occurrences). ADOPTION is the adoption commit, which cannot name itself: it is left for the tool's second run (its DEFER value), as set 31's.
Taken under the owner's standing rule of 26 September 2026 (authority SESSION, W73): reversed by giving set 31's promoted revision a
token of its own, which needs the fill tool's pattern widened first (a token the tool does not know is left in the file silently).

## 1. The candidate

| Role | Revision | State as given | Source |
|---|---|---|---|
| BASE (the REVIEWED role of the brief's form): set 31's promoted revision | `__PROMOTED__` | set 31's promoted revision, not yet promoted when this record was written; once promoted, a DESK candidate, not an accepted power design, and no independent check read it. The last independent check of the power candidate is cx46 on `4d0ff8a2`, "P0 RECHECK: CORRECTIONS NOT CLOSED." | `3057ae43:v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:10` `"summary": "P0 RECHECK: CORRECTIONS NOT CLOSED.` |
| Set 31's lineage tip as last read, against which the branches' bases are read | `aa3322806da156d12f2b23dbe9fc98a8805926f0` (fnd/int31regen, the re-key's cache commit on W41's converged commit) | set 31's lineage before its candidate and promotion; set 32's branches merge onto set 31's promoted revision, never onto this commit | `git rev-parse fnd/int31regen` at 20:30 CEST |
| The lineage this record's branch was cut from | `3057ae43f4fb7fc5e3d6282ce52d448c8ee27929` (fnd/int31regen, W41's checkpoint) | an ancestor of the tip above | the INBOX line above |
| Branch A: fnd/w34pdftext (chain step a2) | `b397aada17befd8c6ee8be09550a785139c45066` | 13 commits over `aed4bd234644c80fa494299b21099acf6d2454c1` (its merge base with set 31's lineage), no merge, no output committed; W36 read its commit `6dc69ad2` (section 2b) | `git rev-list --count aed4bd23..b397aada`; `git merge-base aa332280 b397aada` |
| Branch B: fnd/s32attr (step a2b) | `9210ab541e8144af530f928c1da98b96f90c89fd` | 2 commits over `5b3153aa4136f08ab186a2b5da53c1c4f0c3ecac` (W53 cut it from branch A's commit 5b3153aa, which step a2 merges first), no merge, no output committed; no independent reader | `git rev-list --count 5b3153aa..9210ab54` |
| Branch C: fnd/s32small (step a3) | `7b7219a7d0a695b6b866435116905964a68f5578` | 4 commits over `eff28be3b80f882db545a849b0da1def0217f63d` (main's follow-up after set 30's adoption), no merge, no output committed; W52 read it at this tip (section 2b) | `git rev-list --count eff28be3..7b7219a7` |
| Branch D: fnd/res32 (step a3b), this record | `7ae6175814b7824b3a9f69357ec75e9810a41da4` as the chain pinned it when W73 began | 5 commits over `3057ae43f4fb7fc5e3d6282ce52d448c8ee27929`, new files only (this record and `test_res32.py`); W73's commits after it are the integration's placeholder row | `git rev-list --count 3057ae43..7ae61758` |
| Branch E: fnd/l4e7cache (step a3c), WP-B | `5ee1e66eb8787a788647305509ae6c2700144d9a` | 6 commits over `31928583c612ea43df17df5d7e0cbb2f66090f8e` (its merge base with set 31's lineage, W41's converged commit), no merge, no output and no results cache committed; W64 read `849e66c7`, W70 rechecked `849e66c7..2d81d8b2` (section 2g) | `git rev-list --count 31928583..5ee1e66e`; `git merge-base aa332280 5ee1e66e` |
| The re-key's cache commit | `__REKEY__` | record l4e7's results cache re-keyed ONCE on a fresh debian:12 box at the lineage tip that holds `5ee1e66e`, after the converged commit and its independent read (section 3c) | the coordinator's commit on set 32's integration branch |
| INTEGRATED = CANDIDATE: the candidate commit | `__CANDIDATE__` | no independent check of its engineering | the coordinator's commit on set 32's integration branch |
| PROMOTED: main after the fast-forward, set 32's promotion | `__PROMOTED__` | a DESK candidate, not an accepted power design (section 6) | the promotion's log |
| ADOPTED: the commit that adopts this record | `__ADOPTION__` | named in the fill tool's second run, after it exists | git, after the adoption |

## 2. What changes (each branch, its finding, the independent reads, the coordinator's decisions)

**The classification is bound by its path:** `v2/docs/records/int32/CLASSIFICATION.md`, adopted with this file. It classes each of the
30 commits of the five branches over their bases (fnd/w34pdftext 13, fnd/s32attr 2, fnd/s32small 4, fnd/res32 5, fnd/l4e7cache 6; no merge) into W39's fixed set, and counts, first
class per row: REVIEWED-INPUT CHANGED 1; RECORD TEXT 15; GENERATOR DATA (text) 0; TEST 2; DIGEST RE-PIN 0; MERGE 0; TOOLING 12; total 30.
The one REVIEWED-INPUT CHANGED row is W53's attribution (row 14, `4d07a401`): under set 30's rule's second sentence as the coordinator
ruled it (reading A), it carries set 30's row 8's verdict words with each check's own word into four files of the delta cx46 read, as set
31's row 32 classed the same restatement at another site. 10 of the 30 touch a file cx46 read (16 distinct files: eight generators' input
route, the annex's citation line numbers, W53's attribution and the two tests that pin it, record l4e7's paragraph 0a logic and its
test); each is **UNREVIEWED since cx46**, never credited. The rows that change a reviewed generator without a figure, state word,
composition, case, requirement or limit are not REVIEWED-INPUT CHANGED (set 30's row 44 the precedent; the wider readings and their
counts, 10 rows and 3 rows, are stated in that file with the SESSION decisions of W44 and W73). The integration's own commits (the
merges, the converged outputs, this record's later commits, the re-key, the candidate) are placeholder rows there; the outputs they
regenerate include files cx46 read.

### 2a. The branches, in the chain's merge order

| Branch | Rows | Author, queue item | Finding or decision answered | What it does |
|---|---|---|---|---|
| fnd/w34pdftext | 1 to 5 | W34, Q-50 (Q-41 item 1) | set 30's first box pass, in the coordinator's values file: `<worktrees>/_runs/int30/ADOPTION-VALUES.md:12` `149 failures were the boxes' missing poppler-data` (the records extract makers' PDFs at run time); Q-41 item 1 (below the table) | 25 record generators read each maker's PDF text through `_lib/pdftext.py` from a committed verbatim extraction instead of running pdftotext; 171 extractions committed beside their PDFs with a sidecar each (342 files), 52 held back with their held sheets; the re-take script, the inventory, `test_pdftext_input`; in W34's words, `5b3153aa:v2/docs/records/_lib/PDFTEXT-INVENTORY.md:9` `This branch changes HOW a generator obtains a maker's PDF text, never WHAT it computes from it: no verdict, figure,` |
| fnd/w34pdftext | 6 to 8 | W37, Q-56 | W36's F-P1, F-P2, F-R1, F-R2, F-K5, F-C1 (section 2c) | the inventory restated (what still reads the host's poppler; the fetch route per held sheet; the integration order upstream first), `pdftext.FETCH`, the re-take's `.gitignore` check, generator runs with the tools refused in the regression, the supplier page's section 7 re-take step; the integration plan draft outside the tree (`<worktrees>/_runs/int32/PLAN.draft.md`) |
| fnd/w34pdftext | 9, 10 | W42, Q-61 | W36's F-K4 in the live pages | six citations into the edited generators re-pointed (the annex's five `[E11PY:n]` by 62 lines, the ledger's `[PAL:186-255]` to `[PAL:201-270]`), the citations bound to a commit and the filed checks left; the supplier page's section 0e sentence as `w42cite/apply_supplier_0e_pointer.py`; TP-E11-29's two prose citations left as a row for the chain (it pins `tp_check.out`) |
| fnd/w34pdftext | 11 to 13 | W55, Q-74 | W53's finding: `l8p_c4.py` read the BZT52C sheet through another script's reader, in no table, and refused on the branch | `l8p_c4.py` declares and reads its three sheets with its own table (so 26 record generators read each maker's PDF text through the helper, W34's 25 and this one), no new extraction; `test_pdftext_input` gains the static declaration check; the inventory's section 8 |
| fnd/s32attr | 14, 15 | W53, Q-72 | W38's F10 and W48's residuals: "cx45's Q3/Q5 NOT CLOSED" attributed per check | the generator lines of `l9t5_t10.py` (10j) and `l8p_c4.py` (10c) print each word as its check's (cx45 "NOT CONFIRMED", cx46's items "NOT CLOSED"); `T10-ROUND5.md` line 1 and record l8p's `README.md` line 3 keep the old words as labelled history with the restatement; two dated pointers in record l9t5's README; `test_l8p` and `test_l9t5` restated; outputs left for the chain (section 2f) |
| fnd/s32small | 16 | W40, Q-59 (Q-53) | W36's F-S1, decided by the coordinator (section 2d) | `pack.yaml`'s `max_zip_bytes` from 52,428,800 to 104,857,600 with its reason, the old comments dated, a test of the cap and of the estimate's positive margin |
| fnd/s32small | 17 | W40, Q-59 (Q-55) | the record's own invariant, V-E16 mirrors the register (section 2d) | `s32small/apply_q55_ve16.py`, run on the merged tree only: N1a's phrase into V-E16 row 3 of `HW-FW-CONTRACT.md`, `test_w8l5`'s tree check, `test_l5pwr`'s L5-F09 d reading; the README with Q-53's estimator readings |
| fnd/s32small | 18, 19 | W47, Q-65 | W40's and W43's left-outs: Q-55's change-record row and `TP-SOLAR.md` line 297's quote of V-E16 row 3 | the same script's edits 5 and 6 (one change-record row in `HW-FW-CONTRACT.md`; the register's annotated U5 line as `TP-SOLAR.md`'s own quote beside line 297, with a dated lead-in) and `test_w8l5`'s check of both; the README with the scratch-clone check and the added step (regenerate `tp_check.out`) |
| fnd/res32 | 20 to 24 | W44, Q-64; W50, Q-69 | set 32's adoption needs its record | this record's first draft and its rule restated under reading A (W73's commits after `7ae61758` are row 31's) |
| fnd/l4e7cache | 25 to 30 | W61, Q-80; W67, Q-86; W71, Q-91 | the owner's workflow request of 18:29, item 2, and the constitution's section 8 (a cache key covers model code, relevant inputs and material tool versions; unrelated prose need not invalidate) | WP-B: record l4e7's results cache KEY holds the sixteen numbers the record reads of `l4e11_power.out` (part `l4e11_numbers`, a strict extractor), the file's whole digest kept as evidence; W64's F-1 and F-4 and W70's R-2 to R-6 corrected; nothing re-keyed and no output regenerated on the branch (section 2g) |

Q-41 item 1, as the queue states it: `<worktrees>/_runs/int30/QUEUE.md`, entry "| Q-41 |", `pin the EXTRACTED TEXT as a verbatim input beside the PDF`.
No branch commits a `.out`, a baseline circuit draft, a board generator or a netlist (`CLASSIFICATION.md`, its bounds).

### 2b. W36's independent read (of fnd/w34pdftext at `6dc69ad2`, before W37's and W42's commits)

W36 read the branch's first five commits read-only on scratch clones (`<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:30` `five commits over`)
and labels its own read: `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:31` `This is an AI review, not a qualified review.` Its
evidence on the computation, as received: `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:47` `Every new output equals old plus added lines only: efuse +17, l5r2 +7`
(batch 1) and the texts `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:56` `223 checked; 223 byte-identical; 0 differ; 52 held`;
what it did not run: `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:127` `ripple_dense was not run`. Its verdict:
`<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:135` `The branch is fit for set 32's adoption on conditions.` After it, W52
read fnd/s32small at `7b7219a7` and W42's two commits (rows 9 and 10) read-only on a stand-in base, and labels its read:
`<worktrees>/_runs/claude/w52rev32b/REPORT-AS-RECEIVED.md:3` `This is an AI review, not a qualified one`; its verdicts as given:
`<worktrees>/_runs/claude/w52rev32b/REPORT-AS-RECEIVED.md:7` `**Part 1, fnd/s32small 7b7219a7: consistent.**` and
`<worktrees>/_runs/claude/w52rev32b/REPORT-AS-RECEIVED.md:11` `**Part 2, W42's commits: consistent.**` (its part 3 found W43's chain
not fit as written, which W54 then revised). W37's three commits (rows 6 to 8), W55's three (rows 11 to 13) and W53's two (rows 14 and
15) were read by no independent reader, as far as the queue records; WP-B's checks are section 2g's. Set 32's lineage read is a later
queue item, after the chain (section 8).

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
| F-S1 (size) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:88` `margin -17812603 bytes (OVER THE CAP)` | ANSWERED by the coordinator's decision Q-53 and W40's row 16; the next handover build's own margin is not measured here | `__GATE__` |
| F-S2 (size, minor) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:89` `**F-S2** (minor)` | CARRIED: the rule `"v2/docs/records/_lib/**",` in the runner-local `_bin/pack_supplier.py` INCLUDE list is the coordinator's (`<worktrees>/_runs/int32/README.md` `(lines 22 to 43): add`), not in any branch, and the coordinator added it (`<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W44 at about 16:58 CEST", `INCLUDE gains "v2/docs/records/_lib/**"`) | the next supplier delta |
| F-K1 (consequence) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:106` `**F-K1**: the order runs backwards` | ANSWERED in W37's text (row 8) and in the chain's order, steps d1 to d15 (`<worktrees>/_runs/int32/README.md` `W36's F-K1: W34's inventory had the order backwards`); its run is the chain's | `__GATE__` |
| F-K2 (consequence) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:107` `**F-K2**: l4e12 refuses until its source is re-pinned by hand` | CARRIED to the chain's step d2 (`repin_l4e8_out.py`, guarded), on the pin `5b3153aa:v2/docs/records/l4e12/l4e12_thermal.py:169` `L4E8_OUT: "c6181037bede1fec6b183bcb1d8eab66e0023bc23ae5e5374be4d22eedaf4333",` | `__GATE__` |
| F-K3 (consequence) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:108` `**F-K3**: W34 names only the re-key and a general regen_targeted pass, not these dependents` | CARRIED to the coordinator's step after the re-key (`_runs/int31/dependents.sh`, its base `dd1aed00` to be set to set 32's base first, `<worktrees>/_runs/int32/README.md` `types base`, at its d1 and d3) | `__REKEY__`, `__GATE__` |
| F-K4 (consequence, minor) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:109` `There are 108 such citations in 28 tracked files, most of them in filed checks.` | PARTLY ANSWERED: W37's classed list (`<worktrees>/_runs/int32/PLAN.draft.md:78` `the difference is not resolved here`), W42's six re-pointed citations (row 9), TP-E11-29's two at the chain's step a5; the citations INTO outputs are owed a re-take after the regeneration (W43's step h, item 2) | `__GATE__` |
| F-K5 (consequence) | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:110` `**F-K5**: for held sheets the host dependence moves from the reading to the re-take, and the supplier page lacks the step` | ANSWERED in the branch for the page's section 7 (row 7, `5b3153aa:v2/docs/handover/supplier/SUPPLIER-HANDOVER.md:158` `python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/<record>`); section 0e's sentence by `apply_supplier_0e_pointer.py` at the chain's step a5 (row 10) | `__GATE__` |

W36's other condition, the 52 held texts staged on every host that runs a converted record, is the chain's step b (section 3a: the dry
run staged 52 of 52) and, for a box, a held tar cut from the integration worktree after that step, with pdftotext 22.12.0 and
poppler-data on the box (`<worktrees>/_runs/int32/README.md` `converted records' tests needs a held tar cut from the integration worktree after step b`).

### 2d. The coordinator's two decisions set 32 applies

- **Q-53** (authority SESSION under the owner's standing rule): `<worktrees>/_runs/int30/QUEUE.md`, entry "13:35 (clock) Q-53 DECIDED", `rises from 52,428,800 to 104,857,600 (100 MiB) with its reason written in pack.yaml`;
  applied by row 16. The estimator's reading at main, as W40's record gives it: `a7a485ab:v2/docs/records/s32small/README.md:24` `Readings (the estimator writes nothing): at eff28be3,`
  `a7a485ab:v2/docs/records/s32small/README.md:24` `ESTIMATE: 70175272 bytes; H2 was 51894737; cap 52428800; margin -17746472`.
  H3's estimator output keeps its `089f7f27` reading (a plain regeneration would put the current HEAD under the name "H3"); a new record
  carries the current reading after the candidate (section 8).
- **Q-55**: `<worktrees>/_runs/int30/QUEUE.md`, entry "| Q-55 |", `in set 32 with its re-key`; applied at the chain's step a4 by row
  17's script on the merged tree, where the dry run read `<worktrees>/_runs/int32/dryrun-1632.log:25` `apply_q55_ve16: v2/docs/HW-FW-CONTRACT.md f26757c7c5004cdd -> c52eaa5f4ba501ab`;
  the two typed `hwfw` pins follow at step e1 (`<worktrees>/_runs/int32/dryrun-1632.log:94` `would re-pin l4e9_power_path.py hwfw`,
  `<worktrees>/_runs/int32/dryrun-1632.log:95` `would re-pin l4e11_power.py hwfw`). The change-record row for Q-55 and `TP-SOLAR.md`
  line 297's quote of V-E16 row 3, W43's step a6 items, are now the same script's edits 5 and 6 (rows 18 and 19; W47's brief:
  `<worktrees>/_runs/claude/w47s32txt/BRIEF.md:1` `set 32's two residual record-text items on fnd/s32small`); once applied, `TP-SOLAR.md`
  moves `tp_check.out`, which the chain regenerates (step d14). W47 found the second item's premise wrong and took a narrower edit:
  `<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W47 at about 16:56 CEST", `the brief's premise was WRONG (line 297 quotes L4E7-CONTROL-DECISION.md, which has no N1a words, so the quote is already verbatim)`.
  Whether step a6 is then acknowledged without a further hook is the coordinator's (`__GATE__`).

### 2e. The KEY consequence of the branches

`<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md:105` `Of the KEY's 178 files, only` `l4e11_power.out` is a converted
generator's output, and set 32 moves it four ways: `<worktrees>/_runs/int32/README.md` `and set 32 moves it four ways: W34's`
(the conversion's text lines, 68 on W36's old-against-new run, its report's line 47; Q-55's page through the `hwfw` pin; the
freeze's re-pin of the page; l4e11's typed pin of `l8p_c4.out`, which W34's and W53's changes move). Under the KEY set 31 re-keyed, each
of those moves forces a re-key of record l4e7's results cache. WP-B changes the KEY's own definition (its `src` part, and the part
`l4e11_numbers` in place of the file's bytes), which forces one too. Merged in the same set, the two are ONE re-key at the lineage tip
that holds `5ee1e66e` (section 2h); the chain's step f expects the moved parts named and the KEY unmoved by set 32's own regeneration
(section 3c).

### 2f. W53's attribution (fnd/s32attr)

The words "cx45's Q3 NOT CLOSED" and "cx45's Q5 NOT CLOSED", written after cx46 by set 30's row 8 (`6b768b1e`), gave cx46's word to
cx45. W53 prints each word as its check's at the generator lines and keeps the pages' old words as labelled history:
`4d07a401:v2/docs/records/l9t5/l9t5_t10.py:1378` `DISPOSITION (10j, after cx46): Q3: cx45 'P0-3: NOT CONFIRMED', cx46's items 5 to 8 'NOT CLOSED'.`
The check words are the checks' own: `3057ae43:v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:10` `"summary": "P0 RECHECK: CORRECTIONS NOT CLOSED.`
No figure changed and no state moved off OPEN; the classification classes the commit REVIEWED-INPUT CHANGED under reading A because it
carries set 30's row 8's verdict words into files of the delta cx46 read (row 14), and the two outputs move at the integration (row 31).
No independent reader read the branch.

### 2g. WP-B (fnd/l4e7cache): what it changes, and the independent checks with their verdicts as given

**What it changes.** Record l4e7's results cache was keyed on the whole sha256 of `l4e11_power.out`, so a change of the input digests
that file prints moved the KEY and forced a box re-key of the solver; in W61's words, `5ee1e66e:v2/docs/records/l4e7/CACHE-BOUNDARY-L4E11.md:16` `forced a box re-key of the solver (30 to 50 core-minutes).`
WP-B keys the cache on the sixteen numbers the record reads of that file (part `l4e11_numbers`, a strict extractor refusing a missing,
duplicated, unparsable or malformed value), keeps the file's whole sha256 as evidence beside the KEY, and restates record l4e7's
paragraph 0a to what the KEY check and the cache's own fields show. Its six commits, rows 25 to 30: `849e66c7` (W61, the KEY at the
boundary), `18982112` (W67, `re.ASCII`, W64's F-4), `2178cae5` (W67, paragraph 0a, W64's F-1), `2d81d8b2` (W67, the page's adoption
section), `935584bf` (W71, W70's R-2 to R-5 outside the KEY), `5ee1e66e` (W71, the page's sections 7 and 8); their parent on the branch,
`31928583`, is set 31's commit (set 31's row 33). It is cache tooling: it moves no computed figure, and nothing was re-keyed and no
output regenerated on the branch.

**The independent checks (AI reviews, not qualified ones; quoted as received).**

| Check | Revision read | Verdict as given | Conditions or findings, and where each is carried |
|---|---|---|---|
| W64, the focused read (queue item Q-83) | `849e66c7` | `<worktrees>/_runs/claude/w64revkey/REPORT-AS-RECEIVED.md:11` `Fit for adoption: yes (AI review, not a qualified one; prototype framing), on these conditions:` | four conditions (one re-key on a rented box; `l4e11_numbers` in the KEY check; `l4e7_p0sol.out` and its dependents regenerated with 0a restated; the preflight's blind spot noted) and F-1 to F-4: F-1 and F-4 corrected by W67 (rows 26, 27), F-2 by W60's preflight and the KEY check's new version beside the old (`_runs/int30/l4e7_key_check.py.new`, the coordinator swaps it in), F-3 checked with no change; the re-key and the regeneration are the integration's (section 3c) |
| W70, the one targeted recheck (Q-90) | `849e66c7..2d81d8b2` | `<worktrees>/_runs/claude/w70rechkkey/REPORT-AS-RECEIVED.md:9` `**Fit for the re-key: yes, on these conditions:**` | five conditions: the re-key on set 32's tree holding WP-B; the KEY check swapped in first; a `--key-expect` names `src` too (R-7); `l4e7_stage_settings.out` byte-identical after the re-key (2ad2015b0c7aea91), then W67's list plus R-1 (the supplier annex's two `[SOLO]` citations re-cited after reading) with test_w3annex, test_w8l5, test_l5pwr and test_w11l9t5 among the dependents' tests; R-2 to R-6 optional outside the KEY. R-2 to R-6 corrected by W71 (rows 29, 30); R-1, R-7 and condition 4 are chain items (section 4) |

W71's change after W70's recheck was read by no independent checker. The constitution's default of one focused check and one targeted
recheck is spent on WP-B (`<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W71 at about 20:21 CEST", `No further independent check of WP-B is scheduled`);
W71 shows the KEY's parts at its tip equal to those at the commit W70 rechecked, on its own reading:
`5ee1e66e:v2/docs/records/l4e7/CACHE-BOUNDARY-L4E11.md:198` `KEY 2d81d8b2 6e11114faadda427, 935584bf 6e11114faadda427: EQUAL`
(at `935584bf`; `5ee1e66e` changes the page only). The chain's step f reads the KEY's parts again on the integrated tree (section 3c).

### 2h. Why ONE re-key, from W64's history (a rationale, not yet a measured saving)

W64 read the history of `l4e11_power.out` and of the committed caches: `<worktrees>/_runs/claude/w64revkey/REPORT-AS-RECEIVED.md:9` `History count: 61 of the file's 63 revisions print the numbers, and all 61 extract the same values; no consumed number ever moved.`
Of the past cache re-keys, six moved only on this file (its list there):
`<worktrees>/_runs/claude/w64revkey/REPORT-AS-RECEIVED.md:103` `In all 6 the numbers were equal, so these re-keys were avoidable.`; and set 31's:
`<worktrees>/_runs/claude/w64revkey/REPORT-AS-RECEIVED.md:105` `**Set 31's pending re-key** is a 7th avoidable one.` (set 31 has
since re-keyed on box rekey10, its cache commit `aa332280`). Set 32 therefore carries ONE re-key, not two: its own moves of
`l4e11_power.out` (section 2e) would force a re-key under the old KEY, and WP-B's new definition forces one at its adoption, so adopting
WP-B in the same set makes the second one the first. The expected consequence for later sets, that a change of `l4e11_power.out` which
moves none of the sixteen numbers no longer forces a re-key, rests on W64's reading of the history (seven past re-keys on this
boundary) and on the chain's expectation in step f; no set has yet run under the new KEY, so no saving is measured here. The re-key's
cache commit is `__REKEY__`; the KEY-only check's line on it is `__GATE__`.

## 3. The integration, measured

### 3a. W43's dry run (a stand-in base; measured, not the chain)

- **Its base** was set 31's lineage tip, not set 31's promoted revision (which did not exist):
  `<worktrees>/_runs/int32/dryrun-1632.log:1` `== set 32 chain at 2026-10-06 16:32:57 CEST: base 3057ae43`; scratch clone, branches
  fnd/w34pdftext `5b3153aa` and fnd/s32small `a7a485ab` (W47's two commits came after it).
- **a1:** `<worktrees>/_runs/int32/dryrun-1632.log:6` `main (eff28be3) is in the lineage: yes, no merge`.
- **a2, one conflict predicted:** `<worktrees>/_runs/int32/dryrun-1632.log:10` `pdftext: CONFLICTS predicted (git merge-tree), 1 file(s):`,
  `<worktrees>/_runs/int32/dryrun-1632.log:11` `v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md`; set to ours in the
  scratch clone only (`<worktrees>/_runs/int32/dryrun-1632.log:14` `conflicts set to ours in the scratch clone only (not a resolution)`);
  W43's resolution rule for the real chain: keep both clauses, set 31's first (`<worktrees>/_runs/int32/README.md` `Resolution: keep both clauses, set 31's first`).
- **a3:** `<worktrees>/_runs/int32/dryrun-1632.log:18` `s32small: no conflict predicted`.
- **b:** `<worktrees>/_runs/int32/dryrun-1632.log:66` `removed 107 foreign files, never added; untracked now: 0`;
  `<worktrees>/_runs/int32/dryrun-1632.log:67` `held texts present: 52 (expected 52); sidecars: 52`;
  `<worktrees>/_runs/int32/dryrun-1632.log:68` `held texts byte-identical to`.
- **c:** `<worktrees>/_runs/int32/dryrun-1632.log:89` `placeholders: every occurrence deferred` (13 files with their reasons in
  `<worktrees>/_runs/int32/placeholders-deferred.tsv`; this record's three files carry declared tokens too: section 8).
- **d, the selection only:** `<worktrees>/_runs/int32/dryrun-1632.log:148` `round 1 would select: 31 pairs`; regen_targeted alone does
  not select seven converted outputs, which the chain's explicit steps carry (`<worktrees>/_runs/int32/README.md` `It does NOT select l7r2_items and the other converted outputs that name no changed file`).
- **One record regenerated (efuse):** `<worktrees>/_runs/int32/dryrun-1632.log:155` `regen_out: v2/docs/records/efuse/efuse_check.out replaced (69230 bytes, sha256 46d1dede3ef0cfe2)`,
  `<worktrees>/_runs/int32/dryrun-1632.log:157` `1 file changed, 17 insertions(+)`, the same count W36 measured for efuse (section 2b).
- **The KEY, informational:** `<worktrees>/_runs/int32/dryrun-1632.log:176` `l4e7 KEY MISMATCH committed df9030eaf2c8e7bf now 1623624b2ac67635; parts moved: files`,
  `<worktrees>/_runs/int32/dryrun-1632.log:177` `file v2/docs/records/l4e11/l4e11_power.out: a2089b3f6682 -> 4496ea7a4aa9`: set 31's own re-key is
  still owed on the stand-in base, so this line says nothing about set 32's KEY.
- **End:** `<worktrees>/_runs/int32/dryrun-1632.log:184` `== DRY RUN done at 2026-10-06 16:33:50 CEST`. Measured duration (computed
  from the logged stamps): 16:32:57 to 16:33:50, 53 s, of which the efuse regeneration took 25 s
  (`<worktrees>/_runs/int32/dryrun-1632.log:156` `took 25 s`).

### 3a2. W66's dry run with WP-B merged (a scratch clone; measured, not the chain)

W66, the chain's writer, ran the chain in a scratch clone on set 31's lineage tip as a stand-in base, with WP-B pinned at `2d81d8b2`
(before W71's two commits, which change no file of the cache's KEY, section 2g):
`<worktrees>/_runs/int32/dryfull-1955-wpb.log` `pinned merges: SRC_PDFTEXT b397aada, SRC_ATTR 9210ab54, SRC_SMALL 7b7219a7, SRC_RES 7ae61758, SRC_L4E7CACHE 2d81d8b2`.
At the base the KEY read `<worktrees>/_runs/int32/dryfull-1955-wpb.log` `KEY at the base: MATCH (required: step f's MISMATCH is then set 32's own)`;
before any regeneration, with the branches merged, `<worktrees>/_runs/int32/dryfull-1955-wpb.log` `l4e7 KEY MISMATCH committed b8fc6fe2d285112c now 6e11114faadda427; parts moved: src, files, l4e11_numbers`;
and its step f printed `<worktrees>/_runs/int32/dryfull-1955-wpb.log` `KEY: as expected with WP-B merged: parts src, files, l4e11_numbers moved against a0`.
The KEY check that names the part `l4e11_numbers` is the new version; the current one is refused by the chain:
`<worktrees>/_runs/int32/dryfull-1955-wpb.log` `does not name the part l4e11_numbers in its PARTS (it predates WP-B)`. W66's run was still in
progress when this record was written; its full log and its post-re-key steps (`<worktrees>/_runs/int32/dryfull-1917.log`,
`<worktrees>/_runs/int32/dryfull-1917-postrekey.log`) are the coordinator's to cite at the adoption (`__GATE__`).

### 3b. The chain (`_runs/int32/chain.sh` on set 31's promoted revision; every value from its log)

The chain's log is the path given as its second argument (`_runs/int32/chain-<HHMM>.log`); its targeted pass writes
`<worktrees>/_runs/int32/chain.sh` `TL=$LOGSTEM.targeted.log` and its two test groups
`<worktrees>/_runs/int32/chain.sh` `TF=$LOGSTEM.tests-g$grp.log` (both named from the chain's log).

| Step | What the coordinator reads | Expected, as written before the run | Result |
|---|---|---|---|
| a0: the base | the chain's log | the KEY-only check reads MATCH at set 31's promoted revision (set 31's own re-key, `aa332280`, in its history) | `__GATE__` |
| a2 to a3c: the five merges, pinned | the chain's log; the merge commits | fnd/w34pdftext with one conflict, the annex's line 136, resolved with both clauses (set 31's first) by `resolve_annex_a2.py` or by hand; fnd/s32attr, fnd/s32small, fnd/res32 and fnd/l4e7cache clean | `__GATE__` |
| a4: Q-55's script | the chain's log | `HW-FW-CONTRACT.md`, `TP-SOLAR.md` and two tests change, nothing else | `__GATE__` |
| a5: W42's two applies | the chain's log | section 0e's sentence; TP-E11-29's lines 791 and 794 re-cited | `__GATE__` |
| a6: no open input item | the chain's log | a4's two insertions read once each | `__GATE__` |
| b: held material | the chain's log | 52 texts, 52 sidecars, byte-identical, all ignored | `__GATE__` |
| e1, d2, d2a: the typed pins, `L4E8_OUT`, l4e11's `l8p_c4` pin | the chain's log | two `hwfw` re-pins; `L4E8_OUT` after ripple_dense; `l8p_c4` after l8p's three regenerate | `__GATE__` |
| d1 to d11: the regeneration in W36's order | the chain's log | each output gains only its text lines and moved source pins (l4e12's count line apart) and W53's two generator lines; a figure that moves is a defect of the branch (`<worktrees>/_runs/int32/PLAN.draft.md:71` `gains only its text lines and moved source pins (inventory section 4); a figure that moves is a defect of the branch.`); record l4e7_p0sol held back until the re-key (WP-B) | `__GATE__` |
| d6, d7: the cascade twice | the chain's log | the second pass "already identical" for every output | `__GATE__` |
| d12: regen_targeted, base set 31's promoted revision, to convergence | the targeted log named from the chain's log | a round with 0 replaced; only the by-design refusals | `__GATE__` |
| d15: stability | the chain's log | the L4 five, the cascade once, 0 re-pins | `__GATE__` |
| f: the KEY-only check | the chain's log | with WP-B new on the lineage: parts `src`, `files` and `l4e11_numbers` moved against a0 and the KEY equal to e1's reading (set 32's regeneration moved no KEY part) | `__GATE__` |
| The converged commit | `git log` on set 32's integration branch | committed before the independent read and before the re-key | `__GATE__` |
| The diff read of the converged outputs | the commit's diff | every changed line a text-input line, a moved source pin, a digest or W53's attribution, l4e12's count line apart | `__GATE__` |

### 3c. Record l4e7's results cache (the KEY) and the one re-key

The chain's step f: `<worktrees>/_runs/int32/chain.sh` `if go f "the l4e7 KEY-only check (MISMATCH expected: l4e11_power.out alone; with WP-B new, src, files, l4e11_numbers and the KEY now = e1's)"; then`.
The re-key runs ONCE on a fresh debian:12 box, at the lineage tip that holds `5ee1e66e`, after the converged commit, the re-take of the
citations into outputs and the independent read, never before (set 31's rekey9 was spent for that order:
`<worktrees>/_runs/int31/rekey9/SPENT.txt:1` `SPENT: the re-key of 562edf6a`), with the KEY check's new version swapped in first and
any `--key-expect` naming `src` (W70's conditions 2 and 3). After it, `l4e7_stage_settings.out` must read byte-identical:
`<worktrees>/_runs/int32/chain.sh` `W70's condition 4: l4e7_stage_settings.out byte-identical, 2ad2015b0c7aea91, else STOP: five pins move`.
**A finding for the chain's writer (W73, not edited here):** the chain's stop line prints the re-key's box label as set 31 used it,
`<worktrees>/_runs/int32/chain.sh` `LABEL_GIVEN=meshsat-1357-rekey10`, and set 31's re-key rented a box under that label
(`<worktrees>/_runs/vast/LOG-20261006.md` `RENTED 54507159 meshsat-1357-rekey10`); W43's README asks for a NEW label so that the rental
script does not match a stopped box (`<worktrees>/_runs/int32/README.md` `NEW label, so vast_wait does not match a stopped box`),
written before set 31 used that label, so set 32's re-key needs another one. The re-key's cache commit is `__REKEY__`; the KEY-only
check's line after the re-key and the dependents is `__GATE__`.

### 3d. The tests

| When | Run | Result as printed | Cause of each failure, and the fix |
|---|---|---|---|
| step d12 | the targeted pass's affected set (the targeted log named from the chain's log) | `__GATE__` | `__GATE__` |
| step g, group 1 | set 32's own modules (the group 1 log named from the chain's log) | `__GATE__` | `__GATE__` |
| step g, group 2 | the regenerated records and the integration modules (the group 2 log) | `__GATE__` | `__GATE__` |
| after the re-key | the dependents' tests, with test_w3annex, test_w8l5, test_l5pwr and test_w11l9t5 (W70's condition 4) and test_l4e7's two p0sol output tests | `__GATE__` | `__GATE__` |

## 4. The freeze and the gates (the coordinator's; every value to be copied from the logs, never typed)

| Step | Where the coordinator reads it | Result |
|---|---|---|
| The KEY check's new version swapped in before the chain (W70's condition 2) | `_runs/int30/l4e7_key_check.py` against its `.new` | `__GATE__` |
| The converged commit and the re-take of the citations into outputs | `git log` on set 32's integration branch | `__GATE__` |
| The independent read of set 32's lineage, its findings corrected | the reader's report | `__GATE__` |
| The ONE re-key's cache commit and the KEY on it (a new box label, section 3c; `--key-expect` naming `src`) | the cache commit; the KEY check's line | `__REKEY__` |
| `l4e7_stage_settings.out` byte-identical after the re-key (W70's condition 4, 2ad2015b0c7aea91) | the post-re-key log | `__GATE__` |
| The re-key's dependents regenerated (l4e7_p0sol with its 0a, L4-E9's `l4e7p0` pin, l4e9, l5pwr_contracts, l9t5_connected, l6r2_passives; W36's F-K3, W67's list) and the annex's two `[SOLO]` citations re-cited from the regenerated output (W70's R-1) | the dependents' log | `__GATE__` |
| The evidence archive installed before the manifest | the freeze's log | `__GATE__` |
| The candidate commit | `git log` on set 32's integration branch | `__CANDIDATE__` |
| The manifest (candidate_guard record) and the evidence tar | `__GATE__` | `__GATE__` |
| candidate_guard check, every host | `__GATE__` | `__GATE__` |
| Box pass A (every module but the runner's and the records box's) | `__GATE__` | `__GATE__` |
| Box pass B, Python 3.11 | `__GATE__` | `__GATE__` |
| Records box pass (debian:12, pdftotext 22.12.0, poppler-data, the held tar cut after the chain's step b) | `__GATE__` | `__GATE__` |
| Runner pass (`test_l4e7`, and the modules that read `_runs`, section 8) | `__GATE__` | `__GATE__` |
| suite_gate with G7 over the logs | `__GATE__` | `__GATE__` |
| Promotion: fast-forward of main, push, the mirror, the guard on main | `__GATE__` | `__PROMOTED__` (set 32's promotion) |
| Targeted verification of the rows UNREVIEWED since cx46 (`CLASSIFICATION.md`, ten branch rows and the integration's rows) | the coordinator's choice of verifier; not the ended review method | owed; none performed |

## 5. Compute (compute and storage kept apart, no total computed)

**Spent on set 31 and not reused by set 32** (both stopped with their disks kept; set 32 rents its own box under a new label):

- **54468046, rekey8 (debian:12):** `<worktrees>/_runs/vast/LOG-20261006.md:14` `on offer 45602172 (debian:12, Poland, 0.058 USD/h`;
  its recompute on `aed4bd23` killed, `<worktrees>/_runs/vast/LOG-20261006.md:15` `the recompute on aed4bd23 KILLED (W29's finding F3`;
  stopped idle, `<worktrees>/_runs/vast/LOG-20261006.md:16` `STOPPED by the idle watchdog at 15:10:11 after 2.17 h idle (disk kept`.
- **54487140, rekey9 (debian:12):** `<worktrees>/_runs/vast/LOG-20261006.md:17` `RENTED 54487140 meshsat-1357-rekey9`; its recompute
  on `562edf6a` spent and killed, `<worktrees>/_runs/vast/LOG-20261006.md:18` `the SPENT recompute (562edf6a) killed by the coordinator at poll 60`;
  stopped, `<worktrees>/_runs/int31/rekey9-chain-1515.log:37` `stop sent: b'{"success": true}'` (the vast log's line 19 labels this
  stop "rekey8" with the instance number 54487140, quoted as written: `<worktrees>/_runs/vast/LOG-20261006.md:19` `54487140 rekey8: STOPPED after the fetch (disk kept)`).
- **Set 31's own re-key** ran on box 54507159 under the label `meshsat-1357-rekey10`: rented,
  `<worktrees>/_runs/vast/LOG-20261006.md:20` `RENTED 54507159 meshsat-1357-rekey10 (debian:12, disk 40, onstart_rekey_debian.sh with poppler-data): set 31's l4e7 re-key on`,
  and stopped, `<worktrees>/_runs/vast/LOG-20261006.md:21` `54507159 rekey8: STOPPED after the fetch (disk kept)` (the tag is the
  rental script's literal, as line 19's); it is set 31's record's (`records/int31/RESULT.md` section 5 on fnd/res31), not this set's, and
  set 32 does not reuse it.
- **When this record was first drafted (W44, about 16:40 CEST) no instance ran:** `<worktrees>/_runs/vast/CREDIT-READINGS.tsv:1` `no instance running (all eleven stopped)`;
  none of the eleven stopped disks is destroyed, and their artifact inventory is W46's (queue item Q-63,
  `<worktrees>/_runs/vast/INVENTORY-2026-10-06.md:1` `# Artifact inventory of the eleven stopped vast.ai instances`; its sections
  3.10 and 3.11 are the two boxes above). W73 rented, ran and read no box.

**Set 32's own** (none rented for set 32 when this record was written):

- the ONE re-key box (debian:12, under a label no earlier box carries, section 3c), its instance, label and hours from the vast log:
  `__GATE__`;
- the suite boxes of the freeze, and the records box with pdftotext 22.12.0, poppler-data and the held tar cut after the chain's step b
  (W37's plan, section 1): `__GATE__`.

## 6. What set 32 closes and what it does not

**Set 32 closes NO power item.** It adopts a change of how 26 record generators read their makers' PDF text (W36 read the computation
unchanged on the runs it made, section 2b), the attribution of verdict words to their checks, a packaging cap, one phrase carried into a
contract row with its change-record row and a procedure's quote, a change of record l4e7's cache KEY that moves no computed figure (in
its own words, `5ee1e66e:v2/docs/records/l4e7/CACHE-BOUNDARY-L4E11.md:6` `record's cache tooling, not of any computed figure.`), one
re-key, and the regenerated outputs and pins they move. It changes no baseline circuit draft, no board generator and no netlist
(`CLASSIFICATION.md`, its bounds). One of its 30 branch commits is classed REVIEWED-INPUT CHANGED (row 14, a restatement of verdict
words with no state moved off OPEN); the 10 that touch files cx46 read are UNREVIEWED since cx46 and none is credited. No branch's
record says that it closes a power item.

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
| The classification of set 32 | `v2/docs/records/int32/CLASSIFICATION.md` | 30 branch commits classified; 1 REVIEWED-INPUT CHANGED; 10 UNREVIEWED since cx46; three placeholder rows for the integration's commits |
| W34's inventory, with W37's restatements and W55's section 8 | `v2/docs/records/_lib/PDFTEXT-INVENTORY.md` on fnd/w34pdftext | in the tree from the merge |
| W40's and W47's record | `v2/docs/records/s32small/README.md` on fnd/s32small | in the tree from the merge |
| W42's record | `v2/docs/records/w42cite/README.md` on fnd/w34pdftext | in the tree from the merge |
| WP-B's record (W61, W67, W71) | `v2/docs/records/l4e7/CACHE-BOUNDARY-L4E11.md` on fnd/l4e7cache | in the tree from the merge |
| W36's, W52's, W64's and W70's reports as received; W37's plan draft; the chain, its README and W66's dry run logs | `<worktrees>/_runs/claude/w36rev/REPORT-AS-RECEIVED.md`, `<worktrees>/_runs/claude/w52rev32b/REPORT-AS-RECEIVED.md`, `<worktrees>/_runs/claude/w64revkey/REPORT-AS-RECEIVED.md`, `<worktrees>/_runs/claude/w70rechkkey/REPORT-AS-RECEIVED.md`, `<worktrees>/_runs/int32/PLAN.draft.md`, `<worktrees>/_runs/int32/README.md`, `<worktrees>/_runs/int32/chain.sh`, `<worktrees>/_runs/int32/dryfull-1955-wpb.log` | outside the repository; cited, never copied (they carry host paths) |
| Set 31's records | `v2/docs/records/int31/RESULT.md` and `CLASSIFICATION.md` on fnd/res31 `4196e9df` and later | adopted at set 31's promotion; not in this record's branch history |
| The assessment and the three claims | `v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md` | in this branch's history since main's adoption was merged into set 31's lineage (`d5d9c252`) |

## 8. Left out, and why

- **Commits after the tips as last read** (fnd/w34pdftext `b397aada`, fnd/s32attr `9210ab54`, fnd/s32small `7b7219a7`, fnd/l4e7cache
  `5ee1e66e`) are not classified here; the coordinator adds their rows at the adoption. This record's own commits after `7ae61758`
  (W73's) are the integration's placeholder row 31: a record cannot carry its own last commit's row.
- **The coordinator's items outside the tree:** the base typed in `_runs/int31/dependents.sh` and the wording of
  `_runs/int31/cache_commit.sh` before their reuse (W43's README section 3); the KEY check's swap (`l4e7_key_check.py.new`); a new box
  label for set 32's re-key (section 3c, W73's finding); the counts in `<worktrees>/_runs/int32/placeholders-deferred.tsv` for this
  record's files (rows written at W44's revision; this revision carries the candidate's token twice in `RESULT.md`, once in
  `CLASSIFICATION.md` and once in `test_res32.py`, and the name INTEGRATED as a token nowhere).
- **The fill tool's file list** names set 31's files; pointed at set 32 it needs `v2/docs/records/int32/RESULT.md` and
  `CLASSIFICATION.md` in its list (the tokens are already its own; `test_res32` checks that in the runner pass).
- **Open from W36's report, not settled by any branch:** ripple_dense's old-against-new run, the poppler-data dependence measured on a
  box, pdftocairo's host sensitivity, a built ZIP (W36's "Not checked" list), and the difference between W36's 108 and W37's 106 moved
  citations.
- **No independent reader** read W37's three, W55's three or W53's two commits, or W71's two after W70's recheck; WP-B's check
  allowance is spent (section 2g).
- **H3's estimator output** keeps its `089f7f27` reading; the current reading belongs in a new record made with the candidate's commit
  under its own version name (W40's README).
- **The citations into outputs** (`[E11:n]`, `[F01:n]`, `[CON:n]`, the annex's `[SOLO:n]` and the rest) are owed a re-take after the
  regeneration and, for `[SOLO:n]`, after the re-key's dependents (W43's step h, item 2; W70's R-1); they cannot be read before the
  outputs exist.
- **The independent read of set 32's lineage** is a later queue item, after the chain; this record names no finding of it.
- **After the fill**, `test_res32`'s placeholder predicates and the mutations anchored on a token (the placeholder rows' "not
  determined" cells, the GATE token in this file) no longer find their anchors, as W68's F1 found for `test_res31`; the coordinator
  restates them with the rows written in full (W69's method for set 31: anchors that survive the fill, the tip moved to the candidate).
- **A note for the freeze:** `test_res32`'s predicates that read the coordinator's files (the cited logs, the fill tool, the chain's
  pins) raise Skip where `_runs` is absent, which is every rented box; run them in the runner pass, as W39 recommended for `test_res31`
  (taken as this record's recommendation under the owner's standing rule of 26 September 2026; the coordinator applies or reverses it).
- No generator, suite, gate, chain, candidate_guard, regen_out or box job was run by this record's authors; every chain, test and compute
  line is copied from the logs named.
