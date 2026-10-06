# Set 31: the result of the integration (MESHSAT-1357)

**DONE:** the record of set 31 drafted on its lineage as last read, `5f25daf3` (set 31's second candidate: the coordinator's test
correction after the first candidate `d0e283aa`, the re-key's dependents regenerated on the re-key's cache commit `aa332280`,
FAILED its four-log gate; main's adoption of set 30 merged at `d5d9c252` before them): what was adopted and from whom, W38's review
and its findings, W41's corrections, W48's recheck, the classification's reconciliation under the coordinator's ruling, the three
chain runs as logged, the refusals, the KEY before and after the re-key, the two spent re-keys as rework, the first candidate with
its gate's verdict, its two causes, the correction and the re-take, and the coordinator's known item (section 4a), the compute, the
three claims as the assessment gives them, the classification bound (W69 wrote the re-key's results and W68's findings in, 6
October 2026 from 19:46 CEST; W83 the first candidate, its gate and the second candidate, from 21:55 CEST). **NOT DONE:** what the
second candidate's freeze, its gate and the promotion will give (the placeholders for the candidate commit, the promoted revision and
the gate lines, sections 1, 2c, 4, 6 and 8). **NEXT:** the coordinator fills the placeholders line by line from git and the logs at
the adoption (`fill_res.py --set 31`, FREEZE-PLAN step 12) and adopts this file with `CLASSIFICATION.md` and `ENTRY-PAGES.patch.md`.

**Status: a draft for adoption** at set 31's promotion (queue item Q-58), written by worker W39 on branch fnd/res31 (base fnd/int31regen
`f0748b490e183082b2da4361a5d24ee60d5fba40`) on 6 October 2026 from 15:28 CEST, brought to `31928583` by worker W56 from 18:11 CEST
(W39 drafted it; W50 and W51 reconciled its classification), brought to the re-key's cache commit `aa332280` with W68's
findings by worker W69 from 19:46 CEST, and brought to set 31's second candidate `5f25daf3` after the first candidate's failed gate
by worker W83 from 21:55 CEST, in the form of set 30's record
(`v2/docs/records/int30/RESULT.md` at main `eff28be3`). It is record text: its author ran no generator, suite, gate or box job; it
accepts nothing, closes nothing, promotes nothing and changes no verdict. Prototype framing: nothing in the kit has been built, bought,
powered or measured; every figure below is a time, a count or a digest copied from a log or a commit (elapsed times computed from logged
stamps say so), and no figure is an engineering result.

**What set 31 is.** An adoption of record text prepared during set 30's integration by workers W3 to W28 (the queue's rows Q-13 to
Q-51), on the promoted set 30 (`dd1aed00`), with W31's tooling and the coordinator's items, regenerated to convergence by W29 and W35, and
with main's adoption of set 30 merged into the lineage (`d5d9c252`), and W41's second corrections round from W38's review with the
chain's third run on it (`3057ae43`, `31928583`; sections 2b and 3f), the re-key's cache commit and its dependents (`aa332280`, and
`d0e283aa`, the first candidate), and the coordinator's test correction after that candidate's gate FAILED (`5f25daf3`, the second
candidate; section 4a).
It closes NO power item, is not power-design closure and releases nothing; Layer 4's DESK gate stays NOT PASSED as the coordinator
judged it on set 30 (section 6).

**What governs it.** The owner's part 25 (`dd1aed00:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:845` `Use the existing integration gate to record the reviewed and integrated revisions and the intervening changes.`)
and the constitution's section 2 (`dd1aed00:v2/docs/EXECUTION-CONSTITUTION.md:23` `Report engineering-handover readiness, power-design closure and fabrication release separately. A promoted integration set is none of those by itself.`).
No blended percentage is given anywhere in this file.

**Citations.** `<sha>:path:N` followed by a code span quotes line N of that file at that revision; `<worktrees>/_runs/<path>:N`
followed by a code span quotes line N of a coordinator's or worker's log outside the repository (`<worktrees>` is the folder holding the
worktrees); the growing queue file is quoted by its dated entry (`<worktrees>/_runs/int30/QUEUE.md`, entry "...", then the quote,
found in the file). `v2/docs/records/int31/inputs/<file>:N` quotes line N of a verbatim copy of a page at main `eff28be3`, which is not
in this branch's history (`inputs/SOURCES.txt` names each copy's source path, git blob and sha256). `test_res31.py` reads every quote,
every commit named, every count and every placeholder.

## 1. The candidate

| Role | Revision | State as given | Source |
|---|---|---|---|
| BASE: set 30's promoted revision, set 31's base (W39's brief named this role REVIEWED; the entry pages' Reviewed revision is cx46's `4d0ff8a2`) | `dd1aed00d0a0a521063b5792550bc510c4707c59` | a DESK candidate, not an accepted power design; no independent check read it. The last independent check is cx46 on `4d0ff8a2`, "P0 RECHECK: CORRECTIONS NOT CLOSED." | `<worktrees>/_runs/int30/promote-1036.log:2` `main fast-forwarded to dd1aed00d0a0a521063b5792550bc510c4707c59`; `dd1aed00:v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:10` `P0 RECHECK: CORRECTIONS NOT CLOSED.` |
| The lineage when this record's branch was cut | `f0748b490e183082b2da4361a5d24ee60d5fba40` (fnd/int31regen) | 73 commits over the base; the l4e7 KEY MISMATCH until the re-key (section 3e) | `git rev-list --count dd1aed00..f0748b49` |
| The lineage at the merge of main | `d5d9c252db128bc71db42d068477e1b370e750b4` (fnd/int31regen: the merge of main `eff28be3`; `git rev-parse` at 15:55 and 16:10 CEST) | 101 commits over the base (rows 1 to 31 of the classification) | `git rev-list --count dd1aed00..d5d9c252` |
| W41's second corrections round (queue item Q-60) | `3057ae43f4fb7fc5e3d6282ce52d448c8ee27929` (W41's items, 16:14:18) | W38's F2, OW-4, F4 to F7 and F10 corrected (section 2b) | `git log -1 3057ae43` |
| W41's chain, the third run, converged | `31928583c612ea43df17df5d7e0cbb2f66090f8e` (18:10:32) | 25 outputs and 4 tool-moved pins with W48's N1 and N2; the l4e7 KEY MISMATCH on `l4e11_power.out` alone until the re-key (section 3f) | `<worktrees>/_runs/int31/chain3-1614.log:230` `== committed 31928583 at 18:10:37 (32 files); status empty` |
| The re-key's cache commit, the lineage as W69 last read it | `aa3322806da156d12f2b23dbe9fc98a8805926f0` (fnd/int31regen, 19:00:45; `git rev-parse` at 19:54 CEST) | record l4e7's results cache re-keyed on `31928583` on a fresh box (rekey10, rented 18:11:26, section 5), the KEY MATCH after it (section 3e); 104 commits over the base, classified (section 2, row 34); the re-keys on `aed4bd23` and `562edf6a` are spent (section 3g); the lineage moved twice after it, to the two candidates below | `git rev-list --count dd1aed00..aa332280`; `<worktrees>/_runs/int30/QUEUE.md`, entry "18:58 to 19:00 (clock) SET 31'S RE-KEY DONE", `the coordinator committed the one staged file with the script's message: CACHE COMMIT` |
| The first candidate: the re-key's dependents regenerated; SUPERSEDED | `d0e283aa52ceb7f303358862b539161b721475e5` (fnd/int31regen, 20:41:35) | 105 commits over the base (row 35 of the classification); its four-log gate FAILED and it was not promoted (section 4a) | `git rev-list --count dd1aed00..d0e283aa`; `<worktrees>/_runs/int31s1/superseded-d0e283aa/suite_gate.txt:7` `suite_gate: FAIL` |
| The coordinator's test correction, set 31's second candidate, the lineage as last read by this record | `5f25daf3762ecd69c8764bf60de81a80f4119eab` (fnd/int31regen, 21:48:00; `git rev-parse` at 22:05 CEST) | four fixed-size source windows converted in two test modules (section 4a); 106 commits over the base, classified (section 2, row 36); in its freeze when this record was last written | `git rev-list --count dd1aed00..5f25daf3`; `git log -1 5f25daf3` |
| INTEGRATED = CANDIDATE: the candidate commit | `__CANDIDATE__` | no independent check of its engineering | the coordinator's commit on fnd/int31regen |
| PROMOTED: main after the fast-forward | `__PROMOTED__` | a DESK candidate, not an accepted power design (section 6) | the promotion's log |

**The lineage's first-parent line** (`git log --first-parent dd1aed00..5f25daf3`; the 36 numbered rows of `CLASSIFICATION.md`, each
merge's branch commits listed under it there):

| Rows | Commits | What they did |
|---|---|---|
| 1 to 10 | `ec85131c` to `a6e3a066` | W22's ten merges onto set 30's pre-candidate tree `c4492dd3`, in W10's plan order, one conflict resolved (`<worktrees>/_runs/int31/MERGE-LOG.md:31` `**Skipped:** none of the ten`; section 2 below) |
| 11 to 17 | `467c2aaa` to `f47189b1` | W24's application of the filed patch rows and the coordinator's N1a (fnd/int31l4e9) |
| 18 to 22 | `bf3a7b18` to `b0d85054` | W25's test restatements and the merge of W23's citation re-take (fnd/int31tests) |
| 23 | `b76c1480` | W28's application of the coordinator's Q-40 text items (fnd/int31q40) |
| 24 | `fdd20726` | the merge of the promoted set 30 `dd1aed00` (W29) |
| 25 | `aed4bd23` | W29's regeneration, the chain's first run (section 3a) |
| 26 | `0f5b512c` | the merge of W31's tooling, fnd/s31tool `d6ae0704` |
| 27 to 29 | `c724c1f8`, `6abf045c`, `562edf6a` | W35's corrections and the chain's second run (sections 2 and 3b) |
| 30 | `f0748b49` | the coordinator's restatement of `test_w8l5` (section 2) |
| 31 | `d5d9c252` | the coordinator's merge of main `eff28be3`, set 30's adoption (W38's F1; section 2a) |
| 32 | `3057ae43` | W41's items from W38's review (section 2b) |
| 33 | `31928583` | W41's chain, the third run, with W48's N1 and N2 (sections 2b, 2c and 3f) |
| 34 | `aa332280` | the coordinator's commit of record l4e7's results cache re-keyed on `31928583` (rekey10; sections 3e and 5) |
| 35 | `d0e283aa` | the coordinator's regeneration of the re-key's dependents, set 31's first candidate; its four-log gate FAILED (section 4a) |
| 36 | `5f25daf3` | the coordinator's test correction (four fixed-size source windows), set 31's second candidate (section 4a) |

## 2. What changed (every adopted branch, the coordinator's items, the tooling, the corrections)

**The classification is bound by its path:** `v2/docs/records/int31/CLASSIFICATION.md`, adopted with this file. It classes each of the
106 commits of `git rev-list dd1aed00..5f25daf3` (81 commits and 25 merges) from its diff into the brief's fixed set, and counts, first
class per row: REVIEWED-INPUT CHANGED 25; RECORD TEXT 36; GENERATOR DATA (text) 0; TEST 15; DIGEST RE-PIN 3; MERGE 25; TOOLING 2;
total 106 (its section 2; over the 73 commits to `f0748b49` alone, REVIEWED-INPUT CHANGED 17); W41's two commits, rows 32 and 33, are both
REVIEWED-INPUT CHANGED; the re-key's cache commit, row 34, is a DIGEST RE-PIN (the cache's KEY and one part's digest; its results
object equal before and after); the first candidate, row 35, the re-key's dependents regenerated, is REVIEWED-INPUT CHANGED by W83's
SESSION decision under reading A (record l4e7's paragraph 0a, in a file of the delta cx46 read, moves from the KEY not holding, as
cx46 read it, to the KEY holding, with a history sentence that is false for set 31's cache: the coordinator's known item, section
4a); and the coordinator's correction, row 36, is a TEST. Row 36 is the second candidate; the fill writes its name into that row at
the adoption. The class is set 30's rule (line 11 of
`records/int30/CLASSIFICATION.md` at main `eff28be3`), its second sentence read literally as the coordinator ruled on 6 October 2026
(reading A): a change of what cx46 read, or another row's change carried into a file of the reviewed tree, each reason saying whether
the file was in the delta cx46 read (its 60 files plus the L4-E9 page and output). **None of the 25 REVIEWED-INPUT CHANGED commits was read by an independent checker after cx46: each is UNREVIEWED since cx46,
never credited, and owes its own targeted verification before any credit.** The method ended with cx46's second negative, and no
further Astra run on this candidate is authorised; passing the suite transfers no engineering verdict to them. The reviews and the
reconciliation that shaped the lineage and this classification after the branch was cut are in sections 2a to 2d.

**The adopted branches, in W22's merge order** (`<worktrees>/_runs/int31/MERGE-LOG.md`, section 1; each with the finding it answers and
what it restated):

| Merge | Branch (author, queue item) | Finding answered | What it restated | Classification rows |
|---|---|---|---|---|
| `ec85131c` | fnd/w4l4e7 (W4, Q-15) | record l4e7's P0 text read "completed" for D-16 against R-240 PROVISIONAL, and the back-feed sentence against the ledger's HO-F | the three P0 pages: D-16 ADDRESSED IN DRAFTS and PROVISIONAL, route B2 in one wording, the back-feed inside E-1 | 1.1, 1.2 (REVIEWED-INPUT CHANGED) |
| `7992b2b0` | fnd/w5l8p (W5, Q-14) | record l8p's "one release for five drafts" against the register's six rows | one RELEASE.md for six drafts by register row; U101 the LM5069MM-1 in every file of the record; findings W5-F1 to W5-F3 for their owners | 2.1 (REVIEWED-INPUT CHANGED) to 2.3 |
| `16afba29` | fnd/w14l5 (W14, Q-30; with fnd/w8l5, W8, Q-18) | W1's finding L5-F14: the Layer 5 contract files carried set 28's D-10 reading | `pcb_interfaces.yaml` and `HW-FW-CONTRACT.md` restated to D-10 as set 31 left it; W1's two test_l5pwr tests restated to that tree | 3.1 (REVIEWED-INPUT CHANGED) to 3.5 |
| `0ed29a78` | fnd/w11l9t5 (W11, Q-26; with fnd/w9l9t5, W9, Q-24) | Slot L's K items on records l9t5's and l8r2's hand pages; K-26 and K-28 in the connected generator | twelve restatements (L9T5-F28, the two declared upper bounds, 15.1308 V, E-1 named, B2 with no owner item, l8r2's drafts as DRAFT); the generator's T10 and change-list rows | 4.1 and 4.4 (REVIEWED-INPUT CHANGED), 4.2, 4.3, 4.5 |
| `b7fa4bd9` | fnd/w13l4e9 (W13, Q-29; with fnd/w7rem, W7, Q-16) | the 45.88 K/W remnants; W5's findings on L4-E9's side | patch files only (P-01 to P-12, R-01 to R-09, WP-01 to WP-27), applied later by W24 | 5.1 to 5.5 |
| `99bd0af9` | fnd/w17p0list (W17, Q-32; with fnd/recpack, Slot K) | the P0 list revision 3 for set 30's adoption | drafts (RESULT draft 2, the P0 list drafts 2 and 3) as files | 6.1 to 6.6 |
| `6dbbddac` | fnd/w18result (W18, Q-33; with fnd/w15class, W15, Q-31) | set 30's RESULT and part 25's classification | drafts (RESULT draft 3, CLASSIFICATION draft) as files | 7.1 to 7.4 |
| `c378d0a8` | fnd/w20oneliners (W20, Q-34) | the next set's small items | one patch file, 24 rows and three items for the coordinator | 8.1, 8.2 |
| `8206d05b` | fnd/dgate2 (W12, Q-28; with fnd/dgate, Slot L) | Layer 4's DESK-gate assessment drafts | drafts 1 and 2 as files, the verdict placeholder kept | 9.1 to 9.5 |
| `a6e3a066` | fnd/w3annex (W3, Q-13) | the handover inconsistencies in the annex and TP-E11-29 | the annex's sections 6 to 8 (E11-37's section, R17's two prints, R-159, the back-feed as HO-F, D-06); TP-E11-29 re-quoted and kept NOT EXECUTABLE; the one conflict resolved to W3's file whole (`<worktrees>/_runs/int31/MERGE-LOG.md:44` `first note, per W10's plan section 3)`) | 10.1 and 10.2 (REVIEWED-INPUT CHANGED), 10.3 |

After the ten merges, on the first-parent line: W24 applied the filed patch rows (rows 11 to 17: W7's P-01 to P-12, W13's WP-01 to
WP-22, W20's rows for six files, W14's PATCH_L5F11_ORDER, the four typed-in pins; `<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W24 at about 05:45 CEST", `Q-38 DONE`);
W23 re-took the ledger's and the annex's citations (rows 20.1 and 20.2); W25 restated the tests that read the applied rows (rows 18, 19,
21, 22); W28 applied the Q-40 text items (row 23).

**The coordinator's items** (authority SESSION under the owner's standing rule; `<worktrees>/_runs/int30/QUEUE.md`, entry "05:28 CEST the coordinator's decisions on W20's three NEEDS-THE-COORDINATOR items", `N1a R-176 row 3's U5 line is ANNOTATED with R-240's "under 10 mV"`):

- **N1a:** R-176 row 3's U5 line annotated with R-240's drafted figure, not replaced (row 14, `b2564b59`); L4-E9's generator renders
  the annotation while R-240 reads DRAFTED (row 28).
- **N2:** R-217's release words WAIT for record l4e11's restatement of E11-43 (not applied; section 8).
- **N3:** the ledger's citation strings into record l4e7's pages re-cited from W20's map (W23, row 20.1), test_remeng left as it is
  (its keys moved with the re-cite, row 21).
- **Q-40:** the ledger's HO-F line restated to W4's passage, two re-cites, record l4e7's owner-file citations one line on, the annex's
  dated notes (W28, row 23); `[CON:21]` left for after the regeneration (`<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W28 at about 11:00 CEST", `[CON:21] left for after the regeneration`; section 8).
- **test_w8l5:** restated to the fixture form (row 30, `f0748b49`); `<worktrees>/_runs/int30/QUEUE.md`, entry "15:22 (clock) test_w8l5's failure decided by the coordinator", `restated on fnd/int31regen (commit f0748b49) to the fixture form`;
  carrying N1a into V-E16 is set 32's (Q-55, section 8).

**W31's tooling** (merged at row 26, `0f5b512c`; `<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W31 at about 11:46 CEST", `run.py reads a test's SystemExit as FAIL SystemExit(code)`):
`tests/run.py` records a test's or a module's SystemExit as FAIL and continues; `candidate_guard record`'s condition C5 refuses an
evidence list without a board-gate output unless a reason is given. Its consequence for this set's freeze, as the queue states it:
`<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W31 at about 11:46 CEST", `that install is a freeze step BEFORE the manifest`.

**W35's five corrections** (rows 27 to 29; `<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W35 at about 15:21 CEST", `Q-51 DONE: tip `):

1. OW-4's typed pin of `SUPPLIER-P1-1-P0SOL.md` moved to the file's bytes after W28's edit (W29's finding F3; row 27).
2. N1a's words kept in the register's R-176 row 3 and rendered by L4-E9's generator while R-240 reads DRAFTED (rows 27 and 28; a first
   fix that moved the annotation out of row 3 broke four tests pinning N1a's text and was reverted).
3. `test_l5pwr`'s L5-F11 expectation restated to the script's refusal after W14's patch (row 27).
4. Record l4e7's generator gains `KEY_AT` for paragraph 0a's label (W29's finding F2; row 27).
5. The s122 and h3 outputs restored to HEAD after every pass (W29's finding F1; never committed).

**The test restatements** in the range: rows 2.2, 3.2, 3.4, 3.5, 4.2, 7.2, 17, 18, 19, 21, 22 and 30 (TEST first) and the TEST parts of
rows 1.1, 3.1, 4.4, 5.2, 5.3, 5.5, 6.2, 6.6, 7.4, 8.2, 9.2 to 9.5, 10.1 to 10.3, 20.2, 23, 26.1 and 27; each names its basis in its
commit; no predicate was weakened in a row this record read.

### 2a. W38's review of the lineage to `f0748b49` and its findings F1 to F10 (queue item Q-57)

W38, a reviewer reading beside this record (an AI review, not a qualified one), read `dd1aed00..f0748b49` from 15:23 to 15:43 CEST:
`<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md:3` `The lineage is record text as claimed, but it is not fit for the freeze yet`. Its findings, each with W38's class and what
became of it (W48's readings are section 2c's):

| Finding | W38's words (its report, the line named) | W38's class | What was done, and where |
|---|---|---|---|
| F1 | `<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md:22` `are not in the lineage. 18 files differ on both sides` (main's commits `836f711b` to `eff28be3`) | provenance | the coordinator merged main `eff28be3` into the lineage, `d5d9c252` (row 31); W48: closed |
| F2 | `<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md:23` `placeholders are unfilled. No recorded deferral in the QUEUE` (eleven, for set 30's promoted sha; OW-4 pinned to the unfilled bytes) | provenance | W41 filled them with `dd1aed00` and took OW-4 after the fill (`3057ae43`, row 32); W48: closed |
| F3 | `<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md:24` `The l4e7 KEY MISMATCH at the tip.` | provenance | known and owed: the re-key after W41's commit, done since, the cache commit `aa332280` with its KEY MATCH (sections 3e and 3g); W48: open as expected |
| F4 | `<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md:25` `A W11 statement is stale at the tip.` | figure | W41 restated it (`3057ae43`), printed at `31928583`; W48: closed, one residual (section 2c) |
| F5 | `<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md:26` `The annex contradicts a row applied in the same lineage` | figure (K-06) | W41 restated it (`3057ae43`); W48: closed |
| F6 | `<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md:27` `The section now cites on two bases.` | provenance | W41 restated the basis (`3057ae43`); W48: closed |
| F7 | `<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md:28` `test_l5pwr's prose contradicts its restated body.` | test | W41 restated the prose (`3057ae43`), which removed W20-18's applied words (W48's N2), kept again at `31928583`; W48: closed, with N2 |
| F8 | `<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md:29` `Tests changed in the lineage were not run on it` | test | W48 ran them on `3057ae43`; W41 ran them on the tree committed as `31928583` (section 3d); the 47 `test_l4e7` tests that reach the solver are owed after the re-key (section 4) |
| F9 | `<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md:30` `This matches its source and is not wider than it, so it is not an upgrade made in this lineage.` | verdict | nothing to do; W48: unchanged |
| F10 | `<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md:31` `NOT CLOSED is attributed to cx45.` | verdict (minor) | W41 restated it (`3057ae43`), printed at `31928583`; W48: closed at its site, one residual (section 2c) |

W38's own classification of the 73 commits is a report as received; section 2d gives how it was reconciled with this record's.

### 2b. W41's corrections (queue item Q-60; rows 32 and 33 of `CLASSIFICATION.md`)

W41, the writer of fnd/int31regen, corrected W38's F2, F4 to F7 and F10 at `3057ae43` (16:14:18), ran the chain's third run on it
(section 3f) and, after W48's recheck, corrected W48's N1 and N2 before committing the converged outputs `31928583` (18:10:32):
`<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W41 at about 18:12 CEST", `Q-60 DONE: fnd/int31regen`. Each change, from git:

- **F2:** the eleven placeholders for set 30's promoted sha filled with `dd1aed00` in the annex and five pages of records l4e7 and l8p;
  OW-4's typed pin of `SUPPLIER-P1-1-P0SOL.md` taken after the fill,
  `3057ae43:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1263` `in the tree, f64a657a4343954a, UNSENT`.
- **F4:** `d5d9c252:v2/docs/records/l9t5/l9t5_connected.py:1014` `at commit 2b's digests, refusing at those pins on a tree without them`
  now `3057ae43:v2/docs/records/l9t5/l9t5_connected.py:1014` `at those outputs' current digests, which the chain re-pins, refusing at a pin whose output differs`,
  and record l9t5's README at its line 158 to match.
- **F5:** `d5d9c252:v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:208` `Set 29's per-FET 45.88 K/W still stands in L4-E9's D-14 rows`
  now `3057ae43:v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:209` `those rows now label it SUPERSEDED beside 40.78 K/W without m and the 37.59 K/W target`.
- **F6:** `3057ae43:v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:967` `except [OWN:N], which is line N of the owner file as it stands at commit b0a67a45`.
- **F7 and N2:** test_l5pwr's prose brought to its body; the first form removed W20-18's applied words (W48's N2), and the converged
  commit keeps them with the correction after them, `31928583:v2/ecad/tools/tests/test_l5pwr.py:22` `Since f0d0e54e applied that correction to the second script in set 31`.
- **F10:** `d5d9c252:v2/docs/records/l9t5/l9t5_connected.py:1003` `cx45's Q3 NOT CLOSED (10j, after cx46);`
  now `3057ae43:v2/docs/records/l9t5/l9t5_connected.py:1003` `Q3: cx45 'P0-3: NOT CONFIRMED', cx46's items 5 to 8 'NOT CLOSED'`,
  printed at `31928583:v2/docs/records/l9t5/l9t5_connected.out:351` `Q3: cx45 'P0-3: NOT CONFIRMED'`.
- **F8:** the modules W38 named, main's adopted modules and W41's restated modules run on the tree committed as `31928583`, test_l4e7
  without its 47 tests that reach the solver (section 3d).
- **The annex's citations after the merge of main:** `3057ae43:v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:169` `HO-H to HO-K [REM:552-584]`; its alias P0L names revision 2
  of the P0 list at its dated file.
- **N1:** one locus for TP-E11-29's first condition, `31928583:v2/docs/test-procedures/TP-E11-29.md:21` `which adopts this page's restated condition`,
  and the annex at its line 207; W48: `<worktrees>/_runs/claude/w48rechk31/REPORT-AS-RECEIVED.md:100` `TP-E11-29 stays NOT EXECUTABLE either way.`
- **test_w11l9t5:** `<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W41 at about 18:12 CEST", `test_w11l9t5's two older failures restated with bases`
  (W48's N3 read the restatement's basis as true).

Both commits are classed REVIEWED-INPUT CHANGED (`CLASSIFICATION.md` rows 32 and 33: row 11's and row 4.4's changes carried into files
of the delta cx46 read, then printed). Each is UNREVIEWED since cx46; neither changes a circuit draft, a board generator or a netlist,
neither is a checked correction, and neither is credited.

### 2c. W48's targeted recheck (queue item Q-67)

The constitution's one targeted recheck of W38's findings (an AI review, not a qualified one), read from 16:56 to 17:54 CEST on
`3057ae43`; the converged commit had not landed: `<worktrees>/_runs/claude/w48rechk31/REPORT-AS-RECEIVED.md:29` `**Converged commit:** not landed.`

| Item | W48's reading on `3057ae43` | Since |
|---|---|---|
| F1, F2, OW-4, F4, F5, F6, F7, F8, F10 | `<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W48 at about 17:56 CEST", `F1, F2, OW-4, F4, F5, F6, F7, F8 (42 passed on W38's list in a scratch clone), F10 CLOSED` | unchanged at `31928583` by W41's account; not re-read by W48 |
| F3 | `<worktrees>/_runs/claude/w48rechk31/REPORT-AS-RECEIVED.md:15` `**Open as expected:** F3, the KEY` | open until the re-key; the re-key's cache commit `aa332280` since, its KEY MATCH (section 3e); W48 did not read it |
| F9 | `<worktrees>/_runs/claude/w48rechk31/REPORT-AS-RECEIVED.md:16` `**Unchanged:** F9.` | no action |
| N1, new (minor provenance) | `<worktrees>/_runs/claude/w48rechk31/REPORT-AS-RECEIVED.md:100` `Fix: state one locus in both pages.` | corrected at `31928583` (row 33; section 2b) |
| N2, new (a test regression) | `<worktrees>/_runs/claude/w48rechk31/REPORT-AS-RECEIVED.md:19` `the F7 rewrite removed W20-18's applied text. Three tests now fail` | corrected at `31928583`; W41's set A, which runs `test_w20oneliners` and `test_w25tests`, 284 passed, 0 failed (section 3d) |
| N3, new (an observation) | `<worktrees>/_runs/claude/w48rechk31/REPORT-AS-RECEIVED.md:20` `was restated to read W11's tip. Its basis is true.` | no action |
| Residuals, not new | F4's change table at record l9t5's README lines 449 and 452; F10's shorter words at three sites (`<worktrees>/_runs/claude/w48rechk31/REPORT-AS-RECEIVED.md:91` `held by four tests`) | set 32's: `<worktrees>/_runs/int30/QUEUE.md`, entry "17:56 (clock) N1 and N2 relayed", `the F10 and F4 residuals for set 32` |

W48's conditions for the re-key (`<worktrees>/_runs/claude/w48rechk31/REPORT-AS-RECEIVED.md:137` `conditionally on the converged commit. The conditions:`), as the coordinator
recorded them: `<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W41 at about 18:12 CEST", `W48's four conditions for the re-key: MET (1 to 3)`;
condition (4), the 47 `test_l4e7` tests that reach the solver, runs after the re-key (section 4, `__GATE__`). W48 did not read
`31928583`: its KEY line is the chain's, verified by the coordinator (the same entry, `verified by the coordinator`), and its tests are
W41's (section 3d); no independent reader has read row 33.

### 2d. The classification reconciled: W49, the coordinator's ruling, W50, W51 and W56

- **W49** (queue item Q-68; read-only, an AI review) compared W38's table with this one row by row:
  `<worktrees>/_runs/claude/w49recon/REPORT-AS-RECEIVED.md:5` `W38 and W39 differ on 16 of the 73 shared commits.` It found set 30's rule ambiguous in its second sentence and gave both
  readings, `<worktrees>/_runs/claude/w49recon/REPORT-AS-RECEIVED.md:9` `B follows how set 30 applied it at row 26; A reads the second sentence literally.`
- **The coordinator's ruling** (17:13 CEST, authority SESSION under the owner's standing rule of 26 September 2026):
  `<worktrees>/_runs/int30/QUEUE.md`, entry "17:13 (clock) COORDINATOR'S RULING", `READING A for set 31 and set 32`; its reason, in the same entry,
  `more commits labelled unreviewed since cx46, never fewer`; its consequence for set 30, in the same entry,
  `set 31's record states in one dated sentence that set 30's row 26 would read RIC under reading A` and
  `set 30's adopted record is not edited`. The dated sentence is beside the rule in `CLASSIFICATION.md`.
- **W50** (Q-69) applied W49's section 4 under reading A: `<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W50 at about 17:32 CEST",
  `rows 3.1, 10.1, 23 to RIC; 28 RIC+GD+TOOLING`, and rows 31.3, 31.5 and 31.16 to REVIEWED-INPUT CHANGED.
- **W51** (Q-70) read the five rows W49 left not determined line by line: row 31.24 to REVIEWED-INPUT CHANGED, rows 31.14, 31.17,
  31.21 and 31.25 kept as record text by W51's SESSION decision that the coordinator's DESK-gate judgement is not a value cx46 read:
  `<worktrees>/_runs/int30/QUEUE.md`, entry "native completion of W51 at about 17:45 CEST", `reversing it makes RIC 25` (over the 101 commits to `d5d9c252`; over the
  104 to `aa332280`, 27; over the 106 to `5f25daf3`, 28).
- **W56** classed W41's two commits under reading A (rows 32 and 33) and recomputed the counts from the table: REVIEWED-INPUT CHANGED
  24 of 103.
- **W69** wrote the re-key's cache commit `aa332280` as row 34 (DIGEST RE-PIN, as set 30's row 43 classed its own re-key) and kept the
  candidate commit a placeholder row (row 35), and recomputed the counts from the table: REVIEWED-INPUT CHANGED 24 of 104.
- **W83** wrote the first candidate `d0e283aa` as row 35 (REVIEWED-INPUT CHANGED + GENERATOR DATA (text) + DIGEST RE-PIN under
  reading A, taken under the owner's standing rule of 26 September 2026 with its reversal in `CLASSIFICATION.md`; set 30 classed
  the same move of paragraph 0a on its row 44 a digest re-pin and generator text) and the coordinator's correction `5f25daf3` as
  row 36 (TEST), in place of W69's placeholder row, and recomputed the counts from the table: REVIEWED-INPUT CHANGED 25 of 106.

## 3. The integration, measured

### 3a. W29's chain, the first run (on `b76c1480` with `dd1aed00` merged; committed `aed4bd23`)

- **The merge** `fdd20726`, clean: `<worktrees>/_runs/int31/chain-1059.log:1` `== W29 chain log, started 2026-10-06 10:59:11 CEST`.
- **repin_l4e9, first run: REFUSED** `<worktrees>/_runs/int31/chain-1059.log:83` `REFUSED: pinned file missing: fuse997 v2/vendor/power/held/littelfuse-997-mini58v-rev2025-11-18.pdf`
  (section 3c).
- **The L4 pin chain** ended `<worktrees>/_runs/int31/chain-1059.log:110` `freeze exit 0 at 11:08:09`; the staging brought foreign files,
  removed (`<worktrees>/_runs/int31/CHAIN-LOG.md:31` `brought 107 foreign files`).
- **Record l9t5's cascade twice:** pass 1 `<worktrees>/_runs/int31/chain-1059.log:195` `cascade pass 1 exit 0 at 11:19:03`, 17 replaced
  (`<worktrees>/_runs/int31/CHAIN-LOG.md:34` `exit 0, DONE): 17 replaced`); pass 2 `<worktrees>/_runs/int31/chain-1059.log:216` `cascade pass 2 exit 0 at 11:29:39`, every output "already identical".
- **L4-E9's l4e7p0 pin:** `<worktrees>/_runs/int31/chain-1059.log:218` `re-pinned l4e7p0     v2/docs/records/l4e7/l4e7_p0sol.out 430d1591714b -> 03d24a1d6cc5`.
- **The targeted passes, base `dd1aed00`:** `<worktrees>/_runs/int31/targeted-w29-1129.log:1` `== regen_targeted on`; round 1
  `<worktrees>/_runs/int31/targeted-w29-1129.log:24` `round 1: 18 replaced`, round 2 `<worktrees>/_runs/int31/targeted-w29-1129.log:34` `round 2: 5 replaced`,
  round 3 `<worktrees>/_runs/int31/targeted-w29-1129.log:40` `round 3: 1 replaced`, round 4 `<worktrees>/_runs/int31/targeted-w29-1129.log:45` `round 4: 0 replaced`: converged;
  ended `<worktrees>/_runs/int31/targeted-w29-1129.log:110` `== regen_targeted done at 2026-10-06 12:30:22 CEST`.
- **tp_check** (never selected by the targeted pass): `<worktrees>/_runs/int31/chain-1059.log:277` `tp_check exit 0 12:21:47`, one line
  replaced (TP-E11-29's digest).
- **The commit** `aed4bd23` (33 files, 31 outputs and 4 tool-moved pins) at 12:22:28, before the tests ended
  (`<worktrees>/_runs/int31/CHAIN-LOG.md:137` `the converged outputs were committed at 12:22 before the tests ended`).
- **Measured duration** (computed from the logged stamps): 10:59:11 to 12:30:22, 1 h 31 min 11 s.

### 3b. W35's chain, the second run (on `c724c1f8`, then `6abf045c`; committed `562edf6a`)

- **Iteration 1** `<worktrees>/_runs/int31/chain2-1241.log:1` `== W35 chain log, started 2026-10-06 12:41:57 CEST`: the L4 pin chain
  `<worktrees>/_runs/int31/chain2-1241.log:27` `freeze exit 0 at 12:50:14`; foreign files removed `<worktrees>/_runs/int31/chain2-1241.log:45` `removed 107 foreign files, never added; untracked now: 0`;
  repin `<worktrees>/_runs/int31/chain2-1241.log:48` `l4e9_power_path.py: 0 pins re-pinned`; the cascade's pass 1
  `<worktrees>/_runs/int31/chain2-1241.log:70` `cascade pass 1 exit 0 at 13:00:39` (17 replaced, one already identical, lines 51 to 68)
  and pass 2 `<worktrees>/_runs/int31/chain2-1241.log:91` `cascade pass 2 exit 0 at 13:10:56` (every line "already identical", 72 to 89);
  the pin `<worktrees>/_runs/int31/chain2-1241.log:93` `re-pinned l4e7p0     v2/docs/records/l4e7/l4e7_p0sol.out 03d24a1d6cc5 -> 061ddb2d6756`;
  the targeted rounds `<worktrees>/_runs/int31/chain2-1241.log:117` `round 1: 15 replaced`, `<worktrees>/_runs/int31/chain2-1241.log:127` `round 2: 5 replaced`,
  `<worktrees>/_runs/int31/chain2-1241.log:133` `round 3: 1 replaced`, `<worktrees>/_runs/int31/chain2-1241.log:138` `round 4: 0 replaced`;
  ended `<worktrees>/_runs/int31/chain2-1241.log:97` `regen_targeted exit 0 at 14:11:40`.
- **Iteration 2, after the item 2 revision** `<worktrees>/_runs/int31/chain2-1241.log:188` `== W35 iteration 2, started 2026-10-06 14:19:42 CEST`:
  the targeted rounds `<worktrees>/_runs/int31/targeted-w35-1419.log:13` `round 1: 7 replaced` and `<worktrees>/_runs/int31/targeted-w35-1419.log:18` `round 2: 0 replaced`;
  the cascade once `<worktrees>/_runs/int31/chain2-1241.log:215` `cascade: all already identical`; the L4 chain's five outputs "already
  identical" (lines 217 to 221); repin `<worktrees>/_runs/int31/chain2-1241.log:223` `l4e9_power_path.py: 0 pins re-pinned`; ended
  `<worktrees>/_runs/int31/chain2-1241.log:263` `== iteration 2 done at 15:09:03`.
- **The commit** `562edf6a` (28 files: 24 outputs and 4 tool-moved pins) at 15:14:04 (its committer date).
- **Measured duration** (computed from the logged stamps): 12:41:57 to 15:09:03, 2 h 27 min 6 s, two iterations.

### 3c. The refusals, each classified (no output of the lineage depends on them)

| Refusal | Where | Class | Disposition |
|---|---|---|---|
| repin_l4e9's first run, a held sheet missing | `<worktrees>/_runs/int31/chain-1059.log:83` | environment: a missing held input in a fresh worktree | staged by the L4 chain's sibling staging; the next runs read 0 and 1 re-pins |
| `h3/design_difference.py`, exit 1, every round | `<worktrees>/_runs/int31/targeted-w29-1129.log:3` `round 1 REFUSED v2/docs/records/h3/design_difference.py: regen_out: REFUSED, R1 run 1 exited 1:` | by design, pre-existing (also on set 30) | output left as committed; the h3 outputs restored to HEAD after every pass |
| `int10/dryrun.py`, exit 2, every round | `<worktrees>/_runs/int31/targeted-w29-1129.log:4` `round 1 REFUSED v2/docs/records/int10/dryrun.py: regen_out: REFUSED, R1 run 1 exited 2:` | by design: it needs a scratch-folder argument | output left as committed |
| `l4close/verify_risks.py`, exit 1, every round | `<worktrees>/_runs/int31/targeted-w29-1129.log:5` `round 1 REFUSED v2/docs/records/l4close/verify_risks.py: regen_out: REFUSED, R1 run 1 exited 1:` | by design: it exits 1 | output left as committed |
| s122's two outputs replaced by one-line summaries (no refusal printed) | `<worktrees>/_runs/int31/chain-1059.log:271` `Defective replacement, restored to HEAD, not committed` | tool defect (W29's F1): the targeted pass selects scripts that write their own output | restored to HEAD after every pass of both runs; the selection's exclusion is the coordinator's (section 8) |

| `h3/zip_size_estimate.py`, exit 3, every round of the third run only | `<worktrees>/_runs/int31/targeted-w41-1623.log:5` `round 1 REFUSED v2/docs/records/h3/zip_size_estimate.py: regen_out: REFUSED, R1 run 1 exited 3:` | by design: it exits 3 when its estimate of the handover ZIP is over `pack.yaml`'s cap, `31928583:v2/docs/records/h3/zip_size_estimate.py:121` `return 0 if est <= cap else 3` (the queue's Q-53, applied at set 32) | output left as committed; the h3 outputs restored to HEAD after every pass |

The same three by-design refusals print in every round of W35's run (`<worktrees>/_runs/int31/chain2-1241.log:99` `round 1 REFUSED v2/docs/records/h3/design_difference.py: regen_out: REFUSED, R1 run 1 exited 1:` and lines 100, 101, 120 to 122, 129 to 131, 135 to 137),
and with `h3/zip_size_estimate.py` in every round of W41's third run (`<worktrees>/_runs/int31/targeted-w41-1623.log`, lines 3 to 7, 25
to 28, 35 to 38 and 42 to 45); no line of W29's or W35's logs names `zip_size_estimate.py`. The third run's round 1 replaced the two s122
outputs and `h3/same_patches.out`, each restored to HEAD (`<worktrees>/_runs/int31/chain3-1614.log:138` `-- restores (after targeted pass 1): s122 changed 2, h3 outputs changed 1`).

### 3d. The tests, their counts, the failures and their fixes

| When | Run | Result as printed | Cause of each failure, and the fix |
|---|---|---|---|
| ended 12:30:22 | W29's targeted pass, the affected set | `<worktrees>/_runs/int31/targeted-w29-1129.log:108` `tests: 364 passed, 1 failed, 0 skipped; failed: test_l4e9.t_b6_the_solar_guard_already_on` | the generator printed R-176 row 3 without N1a's register annotation; W35's item 2 (rows 27, 28) |
| from 12:22:35 | W29's second set | `<worktrees>/_runs/int31/tests-w29-1222.log:307` `tests: 282 passed, 2 failed, 0 skipped` | test_l5pwr's L5-F11 expectation after W14's patch (W35's item 3); test_w24l4e9's OW-4 pin after W28's edit (W35's item 1) |
| ended 14:11:40 | W35 iteration 1, the affected set | `<worktrees>/_runs/int31/targeted-w35-1241.log:102` `tests: 365 passed, 0 failed, 0 skipped` | none |
| from 14:12:09 | W35 iteration 1, the second set | `<worktrees>/_runs/int31/tests-w35-1412.log:321` `tests: 280 passed, 4 failed, 0 skipped` | four tests pinning N1a's applied text after the first fix moved it; that fix reverted (`6abf045c`) |
| ended 14:54:21 | W35 iteration 2, the affected set | `<worktrees>/_runs/int31/targeted-w35-1419.log:77` `tests: 365 passed, 0 failed, 0 skipped` | none |
| from 15:09:24 | W35 iteration 2, the second set | `<worktrees>/_runs/int31/tests-w35-1509.log:291` `tests: 284 passed, 0 failed, 0 skipped` | none |
| from 15:09:24 | test_w8l5 (the same log) | `<worktrees>/_runs/int31/tests-w35-1509.log:308` `tests: 5 passed, 1 failed, 0 skipped; failed: test_w8l5.t_nothing_else_moved_and_the_bench_rows_are_still_the_registers` | V-E16 at W8's commit compared with the live register, which N1a annotated alone; restated by the coordinator (`f0748b49`) |
| ended 17:48:03 | W41's third run, the targeted pass's affected set | `<worktrees>/_runs/int31/targeted-w41-1623.log:106` `tests: 365 passed, 0 failed, 0 skipped` | none |
| from 18:02:55 | W41's set A (W35's first command line), on `3057ae43` with the working tree committed as `31928583` | `<worktrees>/_runs/int31/tests-w41-1802-a.log:292` `tests: 284 passed, 0 failed, 0 skipped` | none (W48's N2 corrected before the run) |
| from 18:06:31 | W41's set B, test_w8l5 | `<worktrees>/_runs/int31/tests-w41-1802-b.log:9` `tests: 6 passed, 0 failed, 0 skipped` | none (W38's F8: the run with a log) |
| from 18:06:33 | W41's F8 set (W38's modules, main's adopted modules, W41's restated modules; test_l4e7 without its 47 tests that reach the solver) | `<worktrees>/_runs/int31/tests-w41-1802-f8.log:127` `tests: 124 passed, 0 failed, 0 skipped` | none |
| from 18:09:19 | W41's modules that read the annex, TP-E11-29 or test_l5pwr, after N1 and N2 | `<worktrees>/_runs/int31/tests-w41-1802-n1.log:143` `tests: 137 passed, 0 failed, 0 skipped` | none |

### 3e. Record l4e7's results cache (the KEY)

Before the re-key, a MISMATCH on `l4e11_power.out` alone, as expected: on W29's run `<worktrees>/_runs/int31/chain-1059.log:269` `l4e7 KEY MISMATCH committed df9030eaf2c8e7bf now 564794027019bbec; parts moved: files`;
on W35's, after OW-4's re-pin moved the page and `l4e11_power.out` again (W29's F3), `<worktrees>/_runs/int31/chain2-1241.log:229` `l4e7 KEY MISMATCH committed df9030eaf2c8e7bf now 1623624b2ac67635; parts moved: files`,
the one moved part `<worktrees>/_runs/int31/chain2-1241.log:230` `   file v2/docs/records/l4e11/l4e11_power.out: a2089b3f6682 -> 4496ea7a4aa9`.
The re-key on `aed4bd23` was killed for F3 before it finished (section 5). The re-key on `562edf6a` ran on the rekey9 box
(`<worktrees>/_runs/int31/rekey9-chain-1515.log:16` `== polling the recompute (expected about 27 min) from 15:22:20`) and is SPENT
before its result was used: `<worktrees>/_runs/int31/rekey9/SPENT.txt:1` `SPENT: the re-key of 562edf6a (W38's F1 and F2 move l4e11_power.out and the KEY after it); not to be used`,
the coordinator's reading of it `<worktrees>/_runs/int30/QUEUE.md`, entry "15:46 (clock) COORDINATOR: W38's F1 acted on", `The re-key running on 562edf6a (rekey9) is SPENT`.
On W41's third run, after the fill of the placeholders (F2) and OW-4's re-pin moved the page and `l4e11_power.out` once more, the
KEY-only check read `<worktrees>/_runs/int31/chain3-1614.log:179` `l4e7 KEY MISMATCH committed df9030eaf2c8e7bf now b8fc6fe2d285112c; parts moved: files`,
the one moved part `<worktrees>/_runs/int31/chain3-1614.log:180` `   file v2/docs/records/l4e11/l4e11_power.out: a2089b3f6682 -> 36141414a1b6`,
and the same on the commit (`<worktrees>/_runs/int31/chain3-1614.log:233` `key check exit 1 (on the commit)`, after lines 231 and 232).
The re-key on `31928583` ran on a fresh box (`<worktrees>/_runs/int31/rekey10-chain-1811.log:1` `== rekey8_chain on 31928583c612ea43df17df5d7e0cbb2f66090f8e at 2026-10-06 18:11:24 CEST`;
section 5), its recompute from `<worktrees>/_runs/int31/rekey10-chain-1811.log:15` `== polling the recompute (expected about 27 min) from 18:25:14`
to `<worktrees>/_runs/int31/rekey10-chain-1811.log:22` `recompute ended 18:58:29`. Its cache was committed as `aa332280` (19:00:45, one
file, `v2/docs/records/l4e7/l4e7_stage_settings.results.json`; the coordinator's entry: `<worktrees>/_runs/int30/QUEUE.md`, entry "18:58 to 19:00 (clock) SET 31'S RE-KEY DONE",
`the numbers did not move, only the KEY`), and the KEY-only check after it read `<worktrees>/_runs/int31/cache-commit-1859.log:42` `l4e7 KEY MATCH b8fc6fe2d285112c`,
with the cache test `<worktrees>/_runs/int31/cache-commit-1859.log:45` `tests: 1 passed, 0 failed, 0 skipped`. On the first candidate
`d0e283aa`, after its dependents were regenerated, the KEY-only check read `<worktrees>/_runs/int31/dependents-1929.log:189` `l4e7 KEY MATCH b8fc6fe2d285112c` (section 4a; W72's note N3); the second
candidate `5f25daf3` changes two test modules only, and the KEY on it is the freeze's (section 4).

### 3f. W41's chain, the third run (on `3057ae43`; committed `31928583`)

- **The start** `<worktrees>/_runs/int31/chain3-1614.log:1` `== W41 chain log, started 2026-10-06 16:14:39 CEST`.
- **The L4 pin chain (the freeze)** moved `l4e11_power.out` (`<worktrees>/_runs/int31/chain3-1614.log:13` `regen_out: v2/docs/records/l4e11/l4e11_power.out replaced (284299 bytes, sha256 36141414a1b60011)`),
  its stability pass identical (lines 22 to 26), ended `<worktrees>/_runs/int31/chain3-1614.log:27` `freeze exit 0 at 16:22:58`; the
  staged foreign files removed, `<worktrees>/_runs/int31/chain3-1614.log:41` `untracked now: 0; held files present (gitignored): 70`.
- **repin** `<worktrees>/_runs/int31/chain3-1614.log:43` `l4e9_power_path.py: 0 pins re-pinned`.
- **Record l9t5's cascade twice:** pass 1 `<worktrees>/_runs/int31/chain3-1614.log:65` `cascade pass 1 exit 0 at 16:34:14` (17 replaced,
  one already identical, lines 46 to 63); pass 2 `<worktrees>/_runs/int31/chain3-1614.log:86` `cascade pass 2 exit 0 at 16:45:05`
  (every line "already identical", 67 to 84).
- **L4-E9's l4e7p0 pin:** `<worktrees>/_runs/int31/chain3-1614.log:88` `re-pinned l4e7p0     v2/docs/records/l4e7/l4e7_p0sol.out 061ddb2d6756 -> 7d0ec93f47ae`.
- **The targeted passes, base `dd1aed00`:** `<worktrees>/_runs/int31/targeted-w41-1623.log:1` `== regen_targeted on`; round 1
  `<worktrees>/_runs/int31/targeted-w41-1623.log:22` `round 1: 15 replaced`, round 2 `<worktrees>/_runs/int31/targeted-w41-1623.log:33` `round 2: 5 replaced`,
  round 3 `<worktrees>/_runs/int31/targeted-w41-1623.log:40` `round 3: 1 replaced`, round 4 `<worktrees>/_runs/int31/targeted-w41-1623.log:46` `round 4: 0 replaced`: converged;
  ended `<worktrees>/_runs/int31/targeted-w41-1623.log:142` `== regen_targeted done at 2026-10-06 17:48:03 CEST`.
- **The stability checks:** the cascade once `<worktrees>/_runs/int31/chain3-1614.log:143` `cascade exit 0 at 17:58:30` (every line
  "already identical", 144 to 161); the L4 chain's five outputs "already identical" (164 to 168); repin
  `<worktrees>/_runs/int31/chain3-1614.log:170` `l4e9_power_path.py: 0 pins re-pinned`; tp_check
  `<worktrees>/_runs/int31/chain3-1614.log:172` `regen_out: v2/docs/test-procedures/tp_check.out already identical`; the verdict
  `<worktrees>/_runs/int31/chain3-1614.log:176` `-- pass 1: targeted converged=1, cascade replaced 0, L4 five moved 0, repin 0, tp_check moved 0`
  and `<worktrees>/_runs/int31/chain3-1614.log:177` `== converged at pass 1`.
- **The KEY** (section 3e): `<worktrees>/_runs/int31/chain3-1614.log:179` `l4e7 KEY MISMATCH committed df9030eaf2c8e7bf now b8fc6fe2d285112c; parts moved: files`.
- **W48's N1 and N2 after the chain:** `<worktrees>/_runs/int31/chain3-1614.log:216` `N2 test_l5pwr's prose keeps W20-18's applied words`;
  TP-E11-29 changed, tp_check re-taken, `<worktrees>/_runs/int31/chain3-1614.log:220` `regen_out: v2/docs/test-procedures/tp_check.out replaced (13150 bytes, sha256 187c7beff421458d)`,
  and its stability `<worktrees>/_runs/int31/chain3-1614.log:223` `regen_out: v2/docs/test-procedures/tp_check.out already identical`.
- **The commit** `31928583` (32 files: 25 outputs, 4 tool-moved pins, the annex, TP-E11-29 and test_l5pwr) at 18:10:32 (its committer
  date), logged `<worktrees>/_runs/int31/chain3-1614.log:230` `== committed 31928583 at 18:10:37 (32 files); status empty`.
- **Measured duration** (computed from the logged stamps): 16:14:39 to the end of the chain's steps at 18:02:33
  (`<worktrees>/_runs/int31/chain3-1614.log:214` `== chain steps 2 done at 18:02:33`), 1 h 47 min 54 s; to the logged commit at 18:10:37,
  1 h 55 min 58 s.

### 3g. Rework: the two spent re-keys

Two recomputes of record l4e7's results cache were started and spent before their results could be used; each was rework, not a result.

| Re-key | Started | Stopped | Why it was spent | Measured (from the logged stamps) |
|---|---|---|---|---|
| rekey8 on `aed4bd23`, box 54468046 | `<worktrees>/_runs/int31/rekey8-chain-1228.log:9` `rekey8 start on aed4bd234644c80fa494299b21099acf6d2454c1`, polled from 12:29:35 (line 11) | killed at 12:33, `<worktrees>/_runs/vast/LOG-20261006.md:15` `the recompute on aed4bd23 KILLED (W29's finding F3` | W29's F3: OW-4's typed pin, moved after W28's edit, moves `l4e11_power.out` and with it the KEY, so the re-key would have run on a stale input (`<worktrees>/_runs/int30/QUEUE.md`, entry "12:35 (clock) ACTED ON F3", `the re-key on aed4bd23 was KILLED on box 54468046 at 12:33`) | the recompute's minutes to 12:33 (the vast log's stamp is to the minute); the box then stood idle until the watchdog stopped it at 15:10:11 (section 5) |
| rekey9 on `562edf6a`, box 54487140 | `<worktrees>/_runs/int31/rekey9-chain-1515.log:16` `== polling the recompute (expected about 27 min) from 15:22:20` | marked spent at 15:49 (`<worktrees>/_runs/int31/rekey9/SPENT.txt:1` `SPENT: the re-key of 562edf6a`), killed at poll 60, `<worktrees>/_runs/int31/rekey9-chain-1515.log:24` `recompute ended 15:57:50`; the box stopped, `<worktrees>/_runs/int31/rekey9-chain-1515.log:38` `== rekey8_chain done at 2026-10-06 15:58:12 CEST` | W38's F1 and F2: the merge of main and the fill of the placeholders both move `l4e11_power.out`; the coordinator's lesson, `<worktrees>/_runs/int30/QUEUE.md`, entry "15:46 (clock) COORDINATOR: W38's F1 acted on", `lesson: the review before the re-key, the constitution's section 9 order: merges and input changes first` | the recompute 15:22:20 to 15:57:50, 35 min 30 s; the box rented 15:15:17 to the chain's end 15:58:12, 42 min 55 s |

The re-key that counts ran on `31928583` (section 3e; its cache commit `aa332280`), after the merges and input changes, as the lesson asks.


## 4. The freeze and the gates (the coordinator's; every value to be copied from the logs, never typed)

| Step | Where the coordinator reads it | Result |
|---|---|---|
| W41's second corrections round and the chain to convergence (F2, F4 to F8, F10; W48's N1 and N2) | W41's commits and chain log | `3057ae43` and `31928583`, converged at pass 1 with the KEY MISMATCH on `l4e11_power.out` alone (section 3f) |
| The re-key's cache commit and its KEY (rekey10 on `31928583`, rented 18:11:26) | the cache commit on fnd/int31regen; the KEY-only check's line | `aa332280`; `<worktrees>/_runs/int31/cache-commit-1859.log:42` `l4e7 KEY MATCH b8fc6fe2d285112c` (section 3e) |
| W48's condition (4): the 47 `test_l4e7` tests that reach the solver, after the re-key | the box's or the runner pass's log | `__GATE__` |
| The re-key's dependents regenerated (record l4e7's P0 output, L4-E9's l4e7p0 pin, the connected output) | the dependents' log | `d0e283aa`, the first candidate (section 4a): `<worktrees>/_runs/int31/dependents-1929.log:189` `l4e7 KEY MATCH b8fc6fe2d285112c`; `<worktrees>/_runs/int31/dependents-1929.log:198` `== d6: ADDED ABSENT rows? 0` |
| Set 30's evidence archive installed before the manifest (W31's C5) | the freeze's log | `__GATE__` |
| The candidate commit | `git log` on fnd/int31regen | `__CANDIDATE__` |
| The manifest (candidate_guard record) and the evidence tar | `__GATE__` | `__GATE__` |
| candidate_guard check, every host | `__GATE__` | `__GATE__` |
| Box pass A (every module but the runner's and the records box's) | `__GATE__` | `__GATE__` |
| Box pass B, Python 3.11 | `__GATE__` | `__GATE__` |
| Records box pass (debian:12, poppler-data) | `__GATE__` | `__GATE__` |
| Runner pass (`test_l4e7`, and the modules that read `_runs`, section 8) | `__GATE__` | `__GATE__` |
| suite_gate with G7 over the logs | `__GATE__` | `__GATE__` |
| Promotion: fast-forward of main, push, the mirror, the guard on main | `__GATE__` | `__PROMOTED__` |
| Targeted verification of the 25 unreviewed changes of section 2 | the coordinator's choice of verifier; not the ended review method | owed; none performed |

### 4a. The first candidate `d0e283aa`: its gate FAILED; the correction, the re-take and the known item

**The first candidate.** The coordinator committed the re-key's dependents regenerated on `aa332280` as set 31's candidate
`d0e283aa` (20:41:35; row 35 of the classification): the dependents' pass ended `<worktrees>/_runs/int31/dependents-1929.log:199` `== dependents done at 2026-10-06 20:40:42 CEST`, its KEY-only check
`<worktrees>/_runs/int31/dependents-1929.log:189` `l4e7 KEY MATCH b8fc6fe2d285112c`; the freeze followed
(`<worktrees>/_runs/int30/QUEUE.md`, entry "20:41 CANDIDATE COMMITTED", `pre-commit PASSED; the known item in its body`).

**Its four-log gate, verbatim** (`suite_gate.py` over the four pass logs, the coordinator's copy of the failed run kept under
`_runs/int31s1/superseded-d0e283aa/`):

- `<worktrees>/_runs/int31s1/superseded-d0e283aa/suite_gate.txt:1` `suite_gate: candidate d0e283aa52ce; totals tests: 2952 passed, 1 failed, 2 skipped; failed: test_rule_windows.t_the_number_of_fixed_window_rules_never_rises + tests: 26 passed, 0 failed, 0 skipped + tests: 234 passed, 0 failed, 0 skipped + tests: 150 passed, 0 failed, 1 skipped; result lines 3366 (3362 PASS, 3 SKIP, 1 FAIL); modules 261 of 261 ran`
- `<worktrees>/_runs/int31s1/superseded-d0e283aa/suite_gate.txt:2` `FAIL suite-box.log: G2 the last EXIT line reads 'EXIT 1'`
- `<worktrees>/_runs/int31s1/superseded-d0e283aa/suite_gate.txt:3` `FAIL suite-box.log: G3 the totals read 1 failed`
- `<worktrees>/_runs/int31s1/superseded-d0e283aa/suite_gate.txt:4` `FAIL suite-box.log: G4 a traceback (1 line(s))`
- `<worktrees>/_runs/int31s1/superseded-d0e283aa/suite_gate.txt:5` `FAIL suite-box.log: G4 1 FAIL result line(s)`
- `<worktrees>/_runs/int31s1/superseded-d0e283aa/suite_gate.txt:6` `FAIL G6 the suite changed 1 tracked file(s):  M v2/docs/CURRENT-EVIDENCE.md`
- `<worktrees>/_runs/int31s1/superseded-d0e283aa/suite_gate.txt:7` `suite_gate: FAIL`

The first candidate FAILED its gate and was not promoted; it is SUPERSEDED by the second candidate below. The box pass A log reads
`<worktrees>/_runs/int31s1/superseded-d0e283aa/suite-box.log:4033` `tests: 2952 passed, 1 failed, 2 skipped; failed: test_rule_windows.t_the_number_of_fixed_window_rules_never_rises`
and `<worktrees>/_runs/int31s1/superseded-d0e283aa/suite-box.log:4034` `EXIT 1`; the other three passes read 0 failed (the summary
line above).

**The two causes** (the coordinator's diagnosis as its brief to W83 states it, each read here against the log):

1. **A test-suite rule failed on tests of set 31's own lineage** (G2, G3 and both G4 lines): `<worktrees>/_runs/int31s1/superseded-d0e283aa/suite-box.log:3347` `fixed-size source windows in the suite: 87 against the declared 83`;
   the four windows over the declared count were added on set 31's lineage (`<worktrees>/_runs/claude/w83res31b/BRIEF.md:6` `in test_w11l9t5.py and test_w4l4e7.py`). It was not found before the
   freeze: `test_rule_windows` is a whole-suite rule, and no test log of the lineage under
   `_runs/int31` (section 3d, the dependents' pass) names it.
2. **The suite changed a tracked page on the box** (G6): `pcb_interfaces.yaml` changed on the lineage (rows 3.1, `8840adda`, and 13,
   `f08dbb97`) after the INT-001 readings that the installed evidence carried, so a page-writing test rewrote
   `v2/docs/CURRENT-EVIDENCE.md` on the box (`<worktrees>/_runs/claude/w83res31b/BRIEF.md:6` `pcb_interfaces.yaml changed on the lineage (8840adda, f08dbb97) after the INT-001 readings`).

Neither cause is in a circuit draft, a figure, a verdict or a case: one is a defect of the lineage's tests, the other a stale
reading in the evidence the freeze installed. Both are defects the four-log gate exists to find, and it refused the candidate on them.

**The correction.** The coordinator's commit `5f25daf3` (21:48:00; row 36 of the classification, TEST) converts the four windows in
`test_w4l4e7.py` (+15 -2) and `test_w11l9t5.py` (+4 -1): the first reads the note and the D-16 sentence to their own raw
paragraph's end, the second matches each run at its own length. Its commit message states the basis (`test_rule_windows`'s declared
count, which may fall and never rise) and the measured paragraph lengths, two mutants it refuses and its own run of
`test_rule_windows`, `test_w4l4e7` and `test_w11l9t5`, 23 passed, 0 failed. No independent reader has read the correction; whether
the second candidate's suite holds is the gate's (section 4).

**The re-take.** The coordinator re-took INT-001 (`interfaces.py`) on the committed tree `5f25daf3`, `<worktrees>/_runs/claude/w83res31b/BRIEF.md:8` `re-took interfaces.py on the committed tree (21:49:00; the`;
the re-taken verdict carries its own stamp (`ts` 2026-10-06T19:49:00Z, `version` 5f25daf3762e, verdict PASS; the int31 worktree's
gitignored evidence, `v2/ecad/out/interfaces.verdict.json`), and the evidence page re-renders byte-identical,
`<worktrees>/_runs/claude/w83res31b/BRIEF.md:9` `rules_render: 16 document(s), 0 out of date`. The re-take is evidence, not a
commit: it changes no tracked file.

**The coordinator's known item, carried and not corrected in set 31.** Record l4e7's paragraph 0a on the regenerated output is
printed by the script's typed template: `d0e283aa:v2/docs/records/l4e7/l4e7_p0sol.out:31` `its KEY holds on this tree: no part differs`
(true: the KEY-only check above) and `d0e283aa:v2/docs/records/l4e7/l4e7_p0sol.out:32` `re-keyed on the integrated tree by set 30's integrator`,
with L4-E11's rounds 12 to 16 as the re-key's history, which is false for set 31's cache: `<worktrees>/_runs/int30/QUEUE.md`, entry "20:40:42 set 31's DEPENDENTS PASS DONE", `FALSE for set 31's cache (re-keyed by set 31's coordinator at aa332280)`.
The coordinator's SESSION decision under the owner's standing rule of 26 September 2026 (the same entry,
`a template edit moves the output's lines that the supplier annex cites`): carried as a declared known item in the candidate's
commit message and named here, to be corrected with set 32's single re-key (WP-B, branch fnd/l4e7cache, which replaces the template with
what the KEY check proves); reversal: a set 31 fix with the annex re-cited. It is one of the reasons row 35 is classed
REVIEWED-INPUT CHANGED (section 2).

**The second candidate.** `5f25daf3` = `d0e283aa` + the correction; its freeze's lines are the table's rows above, filled at the
adoption from the second freeze's logs (never from the first's).

## 5. Compute (the boxes rented for set 31; compute and storage kept apart, no total computed)

- **54468046, rekey8 (debian:12), rented 12:24** `<worktrees>/_runs/int31/rekey8-chain-1224.log:5` `RENTED 54468046 meshsat-1357-rekey8 12:24:18`;
  the offer as the vast log gives it `<worktrees>/_runs/vast/LOG-20261006.md:14` `on offer 45602172 (debian:12, Poland, 0.058 USD/h`
  (the chain log's offer list prints 0.0516 for the same offer, `<worktrees>/_runs/int31/rekey8-chain-1224.log:4` `offer 45602172 -> 54468046`
  and line 3; both copied, neither a measured cost). Its first staging exited 1 on a short sha
  (`<worktrees>/_runs/int31/rekey8-chain-1224.log:10` `rekey_box_fresh.sh FAILED exit 1`); relaunched, the recompute started on `aed4bd23`
  (`<worktrees>/_runs/int31/rekey8-chain-1228.log:9` `rekey8 start on aed4bd234644c80fa494299b21099acf6d2454c1`) and was **killed at
  12:33** for W29's F3 (`<worktrees>/_runs/vast/LOG-20261006.md:15` `the recompute on aed4bd23 KILLED (W29's finding F3`); the box stayed
  running idle and was **stopped idle at 15:10** (`<worktrees>/_runs/vast/LOG-20261006.md:16` `STOPPED by the idle watchdog at 15:10:11 after 2.17 h idle (disk kept`).
  Measured from the logged stamps: rented 12:24:18 to stopped 15:10:11, 2 h 45 min 53 s, of which no recompute finished.
- **54487140, rekey9 (debian:12), rented 15:15 for the re-key** `<worktrees>/_runs/int31/rekey9-chain-1515.log:5` `RENTED 54487140 meshsat-1357-rekey9 15:15:17`;
  the offer `<worktrees>/_runs/int31/rekey9-chain-1515.log:4` `offer 51708231 -> 54487140` at the listed 0.0667 USD/h (line 3, copied,
  not a measured cost); setup `<worktrees>/_runs/int31/rekey9-chain-1515.log:9` `setup: SETUP-DONE 15:21:22`; the recompute on `562edf6a`
  from 15:22:20 (section 3e). Its result is SPENT and not used (sections 3e and 3g); the chain ends on its own and stops the box
  (`<worktrees>/_runs/int30/QUEUE.md`, entry "15:49 (clock) W40 LAUNCHED", `The rekey9 chain (spent) ends on its own and stops box 54487140`),
  stopped at 15:58 (`<worktrees>/_runs/vast/LOG-20261006.md:19` `STOPPED after the fetch (disk kept)`). Measured from the logged stamps:
  rented 15:15:17 to the chain's end 15:58:12, 42 min 55 s, of which no result was used.
- **54507159, rekey10 (debian:12), rented 18:11 for the re-key on `31928583`** `<worktrees>/_runs/int31/rekey10-chain-1811.log:5` `RENTED 54507159 meshsat-1357-rekey10 18:11:26`;
  the offer `<worktrees>/_runs/int31/rekey10-chain-1811.log:4` `offer 52494645 -> 54507159` at the listed 0.0556 USD/h (line 3, copied,
  not a measured cost); the vast log's line `<worktrees>/_runs/vast/LOG-20261006.md:20` `2026-10-06 18:13 CEST RENTED 54507159 meshsat-1357-rekey10`.
  Its recompute ran 18:25:14 to 18:58:29 (section 3e), 33 min 15 s; the box was stopped after the fetch
  (`<worktrees>/_runs/int31/rekey10-chain-1811.log:33` `stop sent: b'{"success": true}'`; `<worktrees>/_runs/vast/LOG-20261006.md:21` `54507159 rekey8: STOPPED after the fetch (disk kept)`,
  the label rekey8 a fixed word of the chain script, the box rekey10's), the chain ending `<worktrees>/_runs/int31/rekey10-chain-1811.log:34` `== rekey8_chain done at 2026-10-06 18:59:12 CEST`.
  Measured from the logged stamps: rented 18:11:26 to the chain's end 18:59:12, 47 min 46 s; its result is the cache commit `aa332280`.
- **54526559, suite31-2041 (ubuntu:24.04), and 54526562, recbox31-2041 (debian:12), rented 20:41 for the first candidate's freeze**
  `<worktrees>/_runs/vast/LOG-20261006.md:22` `RENTED 54526559 meshsat-1357-suite31-2041` and
  `<worktrees>/_runs/vast/LOG-20261006.md:23` `RENTED 54526562 meshsat-1357-recbox31-2041`, at the listed 0.0681 and 0.0516 USD/h
  (copied, not measured costs); the records box stopped after its fetch,
  `<worktrees>/_runs/vast/LOG-20261006.md:24` `STOPPED after the fetch of the records pass (disk kept)`; their passes are section
  4a's (the first candidate's, FAILED at the gate). The suite box's stop and any box of the second candidate's freeze come after the
  vast log's line 24, as this record was last written.
- No other instance was rented for set 31 to the first candidate's gate (the vast log's lines 13 to 24 name these five boxes alone); every earlier instance stays
  stopped with its disk kept, none destroyed (the vast log's 10:38 line, `<worktrees>/_runs/vast/LOG-20261006.md:12` `Running instances: none.`).

## 6. What set 31 closes and what it does not

**Set 31 closes NO power item.** It adopts record text prepared during set 30's integration, with the regenerated outputs and pins that
text moves. It changes no baseline circuit draft, no board generator and no netlist (`CLASSIFICATION.md`, section 2). Its 25
REVIEWED-INPUT CHANGED commits narrow, tighten, restate, carry, re-take, re-adopt or annotate; none is a checked correction, and none is
credited.

**Layer 4's DESK gate stays NOT PASSED** as the coordinator judged it on set 30, in the assessment's words (quoted from the verbatim
copy of `v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md` at main `eff28be3`; set 31 changes no line of it):

- `v2/docs/records/int31/inputs/L4-DESK-GATE-ASSESSMENT-eff28be3.md:492` `### Layer 4's DESK gate: NOT PASSED`
- `v2/docs/records/int31/inputs/L4-DESK-GATE-ASSESSMENT-eff28be3.md:494` `The gate's own premise is not met.`

**The three completion claims, unchanged, each with its own state** (the constitution's section 2; never blended):

| Claim | State | Basis |
|---|---|---|
| Engineering-handover readiness | READY AS A DESK PACKAGE OF OPEN ITEMS | `v2/docs/records/int31/inputs/L4-DESK-GATE-ASSESSMENT-eff28be3.md:496` `### Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS`, with its own limit `v2/docs/records/int31/inputs/L4-DESK-GATE-ASSESSMENT-eff28be3.md:498` `"Ready" here means complete and internally consistent as a package of open items, not that any item is resolved.` |
| Power-design closure | BLOCKED | `v2/docs/records/int31/inputs/L4-DESK-GATE-ASSESSMENT-eff28be3.md:500` `### Power-design closure: BLOCKED. Fabrication release: BLOCKED.` |
| Fabrication release | BLOCKED | the same line |

Kept apart from all three: documents and editable artifacts (a DESK candidate once promoted, `__PROMOTED__`); design reviewed and
accepted (NO: cx45 NOT CONFIRMED, cx46 CORRECTIONS NOT CLOSED, set 30's 14 unreviewed changes and this set's 25); circuit changes
implemented (NONE); physical qualification (NONE). A promoted integration set is none of the three claims by itself.

## 7. The records this result binds

| Record | Path | State |
|---|---|---|
| The classification of set 31 | `v2/docs/records/int31/CLASSIFICATION.md` | 106 commits classified over `dd1aed00..5f25daf3`; 25 REVIEWED-INPUT CHANGED (set 30's rule, reading A), UNREVIEWED since cx46; the candidate's name in row 36 written by the fill |
| The entry pages' set 31 rows | `v2/docs/records/int31/ENTRY-PAGES.patch.md` | patch rows for `START-HERE.md` and `SUPPLIER-HANDOVER.md`, applied to the two pages by W65 on fnd/adopt31 (queue item Q-84) before the adoption; their revisions are filled at the adoption |
| Set 30's adopted records | `v2/docs/records/int30/RESULT.md`, `CLASSIFICATION.md`, `v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md` at main | on main since the adoption `836f711b` and the follow-up `eff28be3`, in the lineage since `d5d9c252`; not in this record's branch history, so the assessment and the two entry pages are copied verbatim under `inputs/` |
| The drafts set 31 adopts as files | `v2/docs/records/int30/RESULT.draft2.md`, `RESULT.draft3.md`, `CLASSIFICATION.draft.md`, `NEXT-SET-SMALL-ITEMS.patch.md`; `v2/docs/records/l4close/P0-POWER-LIST.rev3.draft2.md`, `.draft3.md`, `.patch.md`, `L4-DESK-GATE-ASSESSMENT.draft.md`, `.draft2.md`; `v2/docs/records/l4e9/L4E9-4588-PATCH.md`, `L4E9-W5-PATCH.md` | history and patch files; where main holds the adopted record, the adopted record governs |
| The chain's logs | `<worktrees>/_runs/int31/CHAIN-LOG.md`, `chain-1059.log`, `chain2-1241.log`, `chain3-1614.log`, the re-key logs and the test logs cited in section 3 | outside the repository; cited, never copied (they carry host paths) |
| The reviews and the reconciliation, as received | `<worktrees>/_runs/claude/w38rev31/REPORT-AS-RECEIVED.md`, `<worktrees>/_runs/claude/w48rechk31/REPORT-AS-RECEIVED.md`, `<worktrees>/_runs/claude/w49recon/REPORT-AS-RECEIVED.md` | outside the repository; each an AI review saved verbatim by the coordinator; cited in section 2, never copied |

## 8. Left out, and why

- **Set 32's items, not this set's:** W34's branch fnd/w34pdftext (the extracted PDF text as committed inputs; queue item Q-50, adopted
  in set 32 under W36's conditions, Q-54: `<worktrees>/_runs/int30/QUEUE.md`, entry "| Q-54 |", `set 32's adoption of fnd/w34pdftext under W36's conditions`);
  Q-53, the handover ZIP's cap raised to 100 MiB, applied at set 32 (`<worktrees>/_runs/int30/QUEUE.md`, entry "13:35 (clock) Q-53 DECIDED", `applied at set 32's integration, not now`);
  Q-55, N1a's phrase carried into V-E16 of `HW-FW-CONTRACT.md`, in set 32 with its re-key (`<worktrees>/_runs/int30/QUEUE.md`, entry "| Q-55 |", `in set 32 with its re-key`);
  W36's conditions F-K1 to F-K3, F-S2 and F-R1 (W37's branch, Q-56).
- **Open in this lineage when this record was written:** W48's condition (4) after the re-key (`__GATE__`); the coordinator's
  known item, record l4e7's paragraph 0a's history sentence (section 4a), set 32's with its re-key; the ledger's `[CON:21]` re-cite after the regeneration (section 2); the coordinator's N2, R-217's release words, waiting
  for record l4e11's E11-43 restatement; W13's WP-23 to WP-27 (with the next circuit change); the exclusion of s122's self-writing
  scripts from the targeted pass (W29's F1; the third run restored them again, section 3c); W48's residuals of F4 and F10, set 32's
  (section 2c). Answered since the first candidate's gate, the gate on the second candidate to read them: its two causes, by the correction
  `5f25daf3` and the re-take of INT-001 (section 4a). Closed since the first draft: W41's round (sections 2b and 3f), the re-key on `31928583` (its cache commit `aa332280` and its KEY MATCH, section 3e), and the eleven outputs both sides regenerated at the
  merge `d5d9c252`, regenerated on the merged tree by the third run (its cascade and targeted passes, section 3f).
- **A note for the freeze, found while writing this record:** the predicates of `test_w18result` (adopted in this set) and of
  `test_res31` that read the coordinator's logs raise Skip where `_runs` is absent, which is every rented box; suite_gate's G7 accepts
  no such skip today (`_bin/suite_gate_skips.tsv`). The recommendation, taken as this record's under the owner's standing rule of 26
  September 2026 and the coordinator's to apply or reverse: run those two modules in the runner pass, where `_runs` exists.
- **Not read line by line:** the regenerated outputs of `aed4bd23` and `562edf6a` (counts and quoted phrases, `CLASSIFICATION.md`
  section 2; those of `31928583` were read hunk by hunk where they differ beyond the digests, row 33); W38's independent table (running beside this record; compared row by row by W49 since). The five record text rows of main's
  adoption that W49 left unread for a carried change were read line by line by W51 since (`CLASSIFICATION.md`, section 2).
- No generator, suite, gate, candidate_guard, regen_out or box job was run by this record's author; every chain, test and compute line
  is copied from the logs named.
