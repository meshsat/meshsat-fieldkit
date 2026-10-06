# Set 32: the rows for the adoption pages (START-HERE.md, SUPPLIER-HANDOVER.md, LAYER-STATUS.md, EXECUTION-PLAN.md; MESHSAT-1357)

**DONE:** 38 exact rows that bring the four adoption pages from set 31 to set 32: S-01 to S-15 for `v2/docs/handover/START-HERE.md`,
U-01 to U-16 for `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, L-01 to L-06 for `v2/docs/handover/LAYER-STATUS.md` and P-01 for
`v2/docs/EXECUTION-PLAN.md`, each with its page, its line, the old text, the new text and its basis, written by worker W95 on branch
fnd/res32 against the pages as they will read after set 31's adoption (the paragraph "What the rows are read against");
`v2/ecad/tools/tests/test_patch32.py` holds every row against those pages. **NOT DONE:** no page is edited here; the rows are
applied by the adoption author at set 32's adoption, and the tokens in their new texts are filled by the coordinator's fill tool
(`<worktrees>/_bin/fill_res.py --set 32`, which reaches this file because `records/int32/RESULT.md` names it).
**NEXT:** at set 32's adoption: the fill's first run (the CANDIDATE and GATE tokens), the rows applied on the named lines in the order
given, the tests that pin the replaced lines restated with their bases, and the fill's second run (the ADOPTION token).

Record text only: it changes no state of any page, accepts nothing and closes nothing; prototype framing: nothing in the kit has been
built, bought, powered or measured.

**What the rows are read against.** The four pages as they will read after set 31's adoption: branch fnd/adopt31 at `b06ee99f`
(`b06ee99fab04ab8fdfcbe39a30684efe9a1b8222`, 6 October 2026, 23:31 CEST, the tip when these rows were written) with set 31's fill
values applied in memory, the CANDIDATE and PROMOTED tokens both `5f25daf3` (set 31's candidate, to which main was fast-forwarded at
its promotion); set 31's ADOPTION and GATE occurrences are left as they stand, because no old text below reaches them. Once set 31's
adoption commit is in this record's tree, the test reads the tree's own pages instead, and every row must hold there unchanged; a
row that does not is restated before set 32's adoption. Every "Old text" is one line, found exactly once on the line named; every
"New text" differs from it. A row whose new text begins with the whole old text inserts the lines after it. Two rows on one line
(S-07 and S-08; U-05 and U-06) are applied in the order given, the second on the line the first left. The rows of each page are
applied on their own line numbers from the bottom of the page up, so that an inserted paragraph moves no later row's line.
Taken under the owner's standing rule of 26 September 2026 (authority SESSION, W95): the test reads `b06ee99f` through git rather
than from copies under `inputs/` (set 31's form), because those copies would carry set 31's CANDIDATE, ADOPTION and GATE tokens into
set 32's tree for good (the placeholder check of set 32's chain refuses an undeclared CANDIDATE token, and the four pages are about
726 kB); where `b06ee99f` is absent and the tree's pages are not yet set 31's, the test raises Skip with that reason. Reversed by
copying the four pages with their sha256 under `inputs/` and adding the deferral rows for their tokens.

**The revision rows, as set 30's pages define them.** Tested: the promoted revision, the commit the gated release suite and the
promotion gate ran on: set 32's candidate, to which main is fast-forwarded (the CANDIDATE token, as set 31's rows carry it after the
coordinator's ruling recorded in `records/int31/ENTRY-PAGES.patch.md`). Adopted: the adoption commit to which main is fast-forwarded
after the promotion (the ADOPTION token, filled in the fill's second run). Packaged: the commit the next supplier delta's README names
in its header, unchanged as a definition, so no row changes it. Reviewed: `4d0ff8a2` (cx46), unchanged: no independent check of the
engineering read a later revision (`records/int32/RESULT.md`, section 1: the candidate's row reads "no independent check of its
engineering"). The tokens are the CANDIDATE, the ADOPTION and the GATE tokens only; the PROMOTED and REKEY tokens are not used here,
because in set 32's record PROMOTED stands for two commits (the record's paragraph "Placeholders"). A GATE token stands where only a
log line can give the value: the promotion's log line, the suite gate's verdict line, candidate_guard's check lines, and the line that
shows set 31's known item corrected, which exists only once set 32's re-key and its dependents have run.

**The three claims are quoted, not restated.** Layer 4's DESK gate and the three completion claims stand on every page as set 30's
adoption wrote them; set 32 changes none of them and no line of the assessment (`records/int32/RESULT.md`, section 6). The rows quote
the assessment's three headings verbatim (`v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md`, section 6). No date is typed for
set 32: the rows were written before its promotion, and its adoption commit dates it (the Adopted row); taken under the owner's
standing rule of 26 September 2026 (authority SESSION, W95), reversed by adding the promotion's date by hand at the adoption.

**How the rows were checked (W95, 6 October 2026, from 23:35 CEST).** On this branch (the pages read at `b06ee99f` with set 31's
fill in memory) `test_patch32` and `test_res32` read 24 passed; in a scratch clone of W95's own, with stand-in commits for the
re-key (on `5f25daf3`, holding the five pinned tips), the candidate and the adoption: the fill tool's template read 97 rows (25 of
them this file's), its first run applied 79 lines with 3 ADOPTION occurrences deferred, its second 3 lines, a third refused, and the
two modules read 24 passed before the fill and after each run; with the four pages written as set 31's adoption leaves them
(stand-in values for set 31's ADOPTION and GATE) `test_patch32` read 9 passed, and with these rows applied to them 9 passed. AI
work, not a qualified review; no page of the tree was edited.

## START-HERE.md

### S-01. `v2/docs/handover/START-HERE.md`, line 3: the current revision

Old text:
```text
**Current revision: set 31 (6 October 2026), the revision `5f25daf3`, an adoption of record text over set 30's `dd1aed00d0a0a521063b5792550bc510c4707c59`. Read section 0 first.**
```
New text:
```text
**Current revision: set 32, the revision `__CANDIDATE__`, an adoption of record text and record tooling over set 31's `5f25daf3`. Read section 0 first.**
```
Basis: `v2/docs/records/int32/RESULT.md`, section 1 (the candidate's row; set 31's promoted revision is the base) and its paragraph "What set 32 is".

### S-02. `v2/docs/handover/START-HERE.md`, line 5: the edition history's list

Old text:
```text
2026, set 30, set 31); sections 1 to 9
```
New text:
```text
2026, set 30, set 31, set 32); sections 1 to 9
```
Basis: row S-03 adds set 32's paragraph to the history it lists.

### S-03. `v2/docs/handover/START-HERE.md`, after line 95: set 32's paragraph in the edition history

Old text:
```text
(`v2/docs/records/int31/RESULT.md`, section 6); no baseline circuit draft, board generator or netlist changed.
```
New text:
```text
(`v2/docs/records/int31/RESULT.md`, section 6); no baseline circuit draft, board generator or netlist changed.

**Set 32** (the revision `__CANDIDATE__`). An adoption of record text and record tooling over set 31: 26 record generators read their
makers' PDF text from committed verbatim extractions instead of running pdftotext, and the tests' own reads of it are declared (W34,
W37, W42, W55, W81); each verdict word is attributed to its check (W53: cx45's "NOT CONFIRMED", cx46's "NOT CLOSED"); the handover
ZIP's cap is raised to 100 MiB (Q-53); N1a's phrase is carried into V-E16 row 3 of the firmware contract (Q-55); record l4e7's results
cache is keyed on the sixteen numbers the record reads of `l4e11_power.out` (WP-B), with ONE re-key; with its integration record and
the outputs these move, regenerated. "Set 32 closes NO power item." (`v2/docs/records/int32/RESULT.md`, section 6); no baseline circuit
draft, board generator or netlist changed.
```
Basis: `v2/docs/records/int32/RESULT.md`, the paragraph "What set 32 is", section 2a and section 6.

### S-04. `v2/docs/handover/START-HERE.md`, line 97: section 0's heading

Old text:
```text
## 0. Set 30's revision (6 October 2026): what it hands over, and set 31 over it
```
New text:
```text
## 0. Set 30's revision (6 October 2026): what it hands over, and sets 31 and 32 over it
```
Basis: row S-05 (set 32's paragraph in section 0); the test that pins this heading (`test_entrypage`) is restated at the adoption.

### S-05. `v2/docs/handover/START-HERE.md`, after line 111: what set 32 changes in section 0

Old text:
```text
carry another row's change into a file of the reviewed tree (set 30's rule, reading A), each "UNREVIEWED since cx46" (`v2/docs/records/int31/CLASSIFICATION.md`, section 2).
```
New text:
```text
carry another row's change into a file of the reviewed tree (set 30's rule, reading A), each "UNREVIEWED since cx46" (`v2/docs/records/int31/CLASSIFICATION.md`, section 2).

**Set 32 over set 31.** This section was written for set 30. Set 32 changes the Tested and Adopted revisions below again, adds its
integration record to the list of what set 30 adds, and changes none of the states. Layer 4's DESK gate and the three completion
claims stand in the assessment's words, of which set 32 changes no line: "Layer 4's DESK gate: NOT PASSED"; "Engineering-handover
readiness: READY AS A DESK PACKAGE OF OPEN ITEMS"; "Power-design closure: BLOCKED. Fabrication release: BLOCKED."
(`v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md`, section 6). "Set 32 closes NO power item." (`v2/docs/records/int32/RESULT.md`,
section 6). Set 31's known item, record l4e7's paragraph 0a's history sentence (`v2/docs/records/int31/RESULT.md`, section 4a), is
corrected by set 32's one re-key and the regeneration of its dependents, as the dependents' log shows: `__GATE__`.
```
Basis: `v2/docs/records/int32/RESULT.md`, section 6 (no power item; the three claims unchanged, quoted from the assessment's lines
492, 496 and 500); `v2/docs/records/int31/RESULT.md`, section 4a (the known item, "to be corrected with set 32's single re-key").

### S-06. `v2/docs/handover/START-HERE.md`, line 117: the Tested row

Old text:
```text
| Tested | `5f25daf3` | set 31's promoted revision (set 30's was `dd1aed00d0a0a521063b5792550bc510c4707c59`, kept as dated history):
```
New text:
```text
| Tested | `__CANDIDATE__` | set 32's promoted revision (set 31's was `5f25daf3` and set 30's `dd1aed00d0a0a521063b5792550bc510c4707c59`, each kept as dated history):
```
Basis: the Tested row's definition on this page; `v2/docs/records/int32/RESULT.md`, section 1.

### S-07. `v2/docs/handover/START-HERE.md`, line 118: the Adopted row, its revision cell

Old text:
```text
| Adopted | `
```
New text:
```text
| Adopted | `__ADOPTION__` | set 32's adoption commit, to which main was fast-forwarded after the promotion: the first revision of main that holds these pages and the set 32 records as adopted (set 31's was `
```
Basis: the Adopted row's definition on this page; set 31's adoption commit, which the row's next code span holds after set 31's
fill, stays in the row as dated history (row S-08 closes the sentence).

### S-08. `v2/docs/handover/START-HERE.md`, line 118: the Adopted row, set 31's sentence made history (after S-07)

Old text:
```text
` | set 31's adoption commit, to which main was fast-forwarded after the promotion: the first revision of main that holds these pages and the set 31 records as adopted (set 30's was
```
New text:
```text
`, kept as dated history; set 30's was
```
Basis: as S-07; applied on the line S-07 left, so the row reads set 32's adoption commit, then set 31's, then set 30's.

### S-09. `v2/docs/handover/START-HERE.md`, line 120: the Reviewed row

Old text:
```text
; unchanged in set 31: no independent check of the engineering read a later revision (`v2/docs/records/int31/RESULT.md`, section 1) |
```
New text:
```text
; unchanged in set 31 and in set 32: no independent check of the engineering read a later revision (`v2/docs/records/int31/RESULT.md`, section 1; `v2/docs/records/int32/RESULT.md`, section 1: "no independent check of its engineering") |
```
Basis: `v2/docs/records/int32/RESULT.md`, section 1 (the candidate's row) and section 2 (the reads of set 32's branches are AI
reviews of their tooling and record text, W36, W52, W64 and W70; none read the engineering).

### S-10. `v2/docs/handover/START-HERE.md`, line 128: the unreviewed changes

Old text:
```text
the candidate commit `5f25daf3` is one of the 106, that file's row 36.
```
New text:
```text
the candidate commit `5f25daf3` is one of the 106, that file's row 36. Set 32 adds its own: of the 34 commits of its five branches, 12 touch a file cx46 read, 2 of them REVIEWED-INPUT CHANGED under set 30's rule (reading A), each "UNREVIEWED since cx46" (`v2/docs/records/int32/CLASSIFICATION.md`, section 2); the integration's own commits are that file's rows 31 to 33, the candidate commit `__CANDIDATE__` its row 33.
```
Basis: `v2/docs/records/int32/CLASSIFICATION.md`, section 2 (34 rows; `REVIEWED-INPUT CHANGED` 2; "The rows that touch a file cx46
read: 12, all UNREVIEWED since cx46.") and its rows 31 to 33.

### S-11. `v2/docs/handover/START-HERE.md`, line 134: the documents row

Old text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`5f25daf3`, set 31) |
```
New text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`__CANDIDATE__`, set 32) |
```
Basis: `v2/docs/records/int32/RESULT.md`, section 6 (kept apart from the three claims).

### S-12. `v2/docs/handover/START-HERE.md`, after line 171: set 32's record in the list

Old text:
```text
  of every commit after set 30's promoted revision.
```
New text:
```text
  of every commit after set 30's promoted revision.
- `v2/docs/records/int32/RESULT.md`: set 32's integration record, with `v2/docs/records/int32/CLASSIFICATION.md`, its classification
  of every commit of its five branches and of the integration's rows, and `v2/docs/records/int32/ENTRY-PAGES.patch.md`, the rows that
  brought these pages to set 32.
```
Basis: `v2/docs/records/int32/RESULT.md`, section 7.

### S-13. `v2/docs/handover/START-HERE.md`, line 183: the checkout to reproduce from

Old text:
```text
From a full git checkout at `5f25daf3`:
```
New text:
```text
From a full git checkout at `__CANDIDATE__`:
```
Basis: the Tested row (S-06).

### S-14. `v2/docs/handover/START-HERE.md`, line 190: what below is history

Old text:
```text
revision is set 31 (section 0 states set 30's revision and what set 31 changes).
```
New text:
```text
revision is set 32 (section 0 states set 30's revision and what sets 31 and 32 change).
```
Basis: rows S-01 and S-05.

### S-15. `v2/docs/handover/START-HERE.md`, line 200: section 1's row for the layer-status page

Old text:
```text
and **since set 31** the blocks headed "After set 31" before those);
```
New text:
```text
and **since set 31** the blocks headed "After set 31" before those, and **since set 32** the blocks headed "After set 32" before all of them);
```
Basis: rows L-01 to L-06 (the layer-status page's blocks headed "After set 32", newest first under each layer's heading).

## SUPPLIER-HANDOVER.md

### U-01. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 8: the page's current set

Old text:
```text
**Brought to set 31 on 6 October 2026: read section 0 first.**
```
New text:
```text
**Brought to set 32: read section 0 first.**
```
Basis: `v2/docs/records/int32/RESULT.md`, section 1.

### U-02. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 22: section 0's heading

Old text:
```text
## 0. This revision: set 31 over set 30 (6 October 2026)
```
New text:
```text
## 0. This revision: set 32 over set 31 and set 30
```
Basis: row U-03.

### U-03. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, after line 36: what set 32 changes in section 0

Old text:
```text
counts 25 commits that change what cx46 read or carry another row's change into a file of the reviewed tree (set 30's rule, reading A), each "UNREVIEWED since cx46" (`records/int31/CLASSIFICATION.md`, section 2).
```
New text:
```text
counts 25 commits that change what cx46 read or carry another row's change into a file of the reviewed tree (set 30's rule, reading A), each "UNREVIEWED since cx46" (`records/int31/CLASSIFICATION.md`, section 2).

**Set 32 over set 31.** Set 32 is an adoption of record text and record tooling over set 31: 26 record generators read their makers'
PDF text from committed verbatim extractions, and the tests' own reads of it are declared; each verdict word is attributed to its
check; the handover ZIP's cap is raised to 100 MiB; N1a's phrase is carried into V-E16 row 3 of the firmware contract; record l4e7's
results cache is keyed on the sixteen numbers the record reads of `l4e11_power.out`, with ONE re-key; the outputs these move are
regenerated. It changes the Tested and Adopted revisions of 0a, adds its integration record to 0c, and changes none of the states of
0b: "Set 32 closes NO power item." (`records/int32/RESULT.md`, section 6). The DESK gate and the three completion claims, in the
assessment's words, unchanged: "Layer 4's DESK gate: NOT PASSED"; "Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN
ITEMS"; "Power-design closure: BLOCKED. Fabrication release: BLOCKED." (`records/l4close/L4-DESK-GATE-ASSESSMENT.md`, section 6). Set
31's known item, record l4e7's paragraph 0a's history sentence (`records/int31/RESULT.md`, section 4a), is corrected by set 32's one
re-key and the regeneration of its dependents, as the dependents' log shows: `__GATE__`.
```
Basis: `v2/docs/records/int32/RESULT.md`, the paragraph "What set 32 is" and section 6; `v2/docs/records/int31/RESULT.md`, section 4a.

### U-04. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 42: the Tested row

Old text:
```text
| Tested | `5f25daf3` | set 31's promoted revision (set 30's was `dd1aed00d0a0a521063b5792550bc510c4707c59`, kept as dated history):
```
New text:
```text
| Tested | `__CANDIDATE__` | set 32's promoted revision (set 31's was `5f25daf3` and set 30's `dd1aed00d0a0a521063b5792550bc510c4707c59`, each kept as dated history):
```
Basis: as S-06.

### U-05. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 43: the Adopted row, its revision cell

Old text:
```text
| Adopted | `
```
New text:
```text
| Adopted | `__ADOPTION__` | set 32's adoption commit, to which main was fast-forwarded after the promotion: the first revision of main that holds these pages and the set 32 records as adopted (set 31's was `
```
Basis: as S-07.

### U-06. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 43: the Adopted row, set 31's sentence made history (after U-05)

Old text:
```text
` | set 31's adoption commit, to which main was fast-forwarded after the promotion: the first revision of main that holds these pages and the set 31 records as adopted (set 30's was
```
New text:
```text
`, kept as dated history; set 30's was
```
Basis: as S-08.

### U-07. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 45: the Reviewed row

Old text:
```text
; unchanged in set 31: no independent check of the engineering read a later revision (`records/int31/RESULT.md`, section 1) |
```
New text:
```text
; unchanged in set 31 and in set 32: no independent check of the engineering read a later revision (`records/int31/RESULT.md`, section 1; `records/int32/RESULT.md`, section 1: "no independent check of its engineering") |
```
Basis: as S-09.

### U-08. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 48: where the adopted records are committed

Old text:
```text
and, for set 31's records, in set 31's adoption commit (the Adopted row);
```
New text:
```text
and, for set 31's records, in set 31's adoption commit (the Adopted row's dated history) and, for set 32's records, in set 32's adoption commit (the Adopted row);
```
Basis: rows U-05 and U-06.

### U-09. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 57: the unreviewed changes

Old text:
```text
the candidate commit `5f25daf3` is one of the 106, that file's row 36.
```
New text:
```text
the candidate commit `5f25daf3` is one of the 106, that file's row 36. Set 32 adds its own: of the 34 commits of its five branches, 12 touch a file cx46 read, 2 of them REVIEWED-INPUT CHANGED under set 30's rule (reading A), each "UNREVIEWED since cx46" (`records/int32/CLASSIFICATION.md`, section 2); the integration's own commits are that file's rows 31 to 33, the candidate commit `__CANDIDATE__` its row 33.
```
Basis: as S-10.

### U-10. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 63: the documents row

Old text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`5f25daf3`, set 31) |
```
New text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`__CANDIDATE__`, set 32) |
```
Basis: as S-11.

### U-11. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, after line 101: set 32's record in 0c

Old text:
```text
| `v2/docs/records/int31/RESULT.md`, with `v2/docs/records/int31/CLASSIFICATION.md` | set 31's integration record: set 30's promoted revision and set 31's bound, every intervening commit classified, the gate lines |
```
New text:
```text
| `v2/docs/records/int31/RESULT.md`, with `v2/docs/records/int31/CLASSIFICATION.md` | set 31's integration record: set 30's promoted revision and set 31's bound, every intervening commit classified, the gate lines |
| `v2/docs/records/int32/RESULT.md`, with `v2/docs/records/int32/CLASSIFICATION.md` and `v2/docs/records/int32/ENTRY-PAGES.patch.md` | set 32's integration record: set 31's promoted revision and set 32's bound, every commit of its five branches classified and the integration's rows, the gate lines, and the rows that brought these pages to set 32 |
```
Basis: `v2/docs/records/int32/RESULT.md`, section 7.

### U-12. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 140: section 0e's heading

Old text:
```text
### 0e. How to reproduce set 31's figures
```
New text:
```text
### 0e. How to reproduce set 32's figures
```
Basis: rows U-13 to U-15.

### U-13. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 142: the checkout to reproduce from

Old text:
```text
From a full git checkout at `5f25daf3`
```
New text:
```text
From a full git checkout at `__CANDIDATE__`
```
Basis: as S-13.

### U-14. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 157: the suite's line

Old text:
```text
The gated release suite's line for `5f25daf3` is in the package's `README.md` and in
```
New text:
```text
The gated release suite's line for `__CANDIDATE__` is in the package's `README.md` and in
```
Basis: `v2/docs/records/int32/RESULT.md`, section 4 (the gate lines).

### U-15. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 158: the record that carries it

Old text:
```text
   `records/int31/RESULT.md` (set 30's, for `dd1aed00`, in `records/int30/RESULT.md`).
```
New text:
```text
   `records/int32/RESULT.md` (set 31's, for `5f25daf3`, in `records/int31/RESULT.md`; set 30's, for `dd1aed00`, in `records/int30/RESULT.md`).
```
Basis: as U-14.

### U-16. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, after line 407: the dated entry

Old text:
```text
  Layer 4's DESK gate and the three completion claims stand as set 30's assessment gives them.
```
New text:
```text
  Layer 4's DESK gate and the three completion claims stand as set 30's assessment gives them.
- **Set 32, the revision `__CANDIDATE__`, dated by its adoption commit** (section 0). An adoption of record text and record tooling
  over set 31: the makers' PDF text as committed verbatim inputs of 26 record generators, the verdict words attributed to their checks,
  the ZIP's cap, N1a's phrase in V-E16 row 3, record l4e7's cache KEY on the sixteen numbers it reads, ONE re-key, regenerated
  (`v2/docs/records/int32/RESULT.md`). No circuit change is applied, and nothing in it accepts, closes or promotes a design claim;
  Layer 4's DESK gate and the three completion claims stand as set 30's assessment gives them.
```
Basis: `v2/docs/records/int32/RESULT.md`, the paragraph "What set 32 is" and section 6.

## LAYER-STATUS.md

The layer-status page keeps its head paragraphs oldest first (set 30's, then set 31's) and, under each layer's heading, its blocks
newest first (W65's placement for set 31): set 32's head paragraph follows set 31's, and each set 32 block goes directly under its
layer's heading, above the set 31 block. **Citations in the set 32 blocks** read commit, path and line at the commit they name, a
code span right after one being the words quoted from that line: set 32's record at fnd/res32's `ee940742` and the assessment at
`3057ae43`, both in set 32's lineage, and W53's generator line at fnd/s32attr's `4d07a401`, merged by set 32's chain;
`test_patch32.py` reads each of them.

### L-01. `v2/docs/handover/LAYER-STATUS.md`, after line 38: set 32's head paragraph

Old text:
```text
`v2/ecad/tools/tests/test_adopt31.py` holds them.
```
New text:
```text
`v2/ecad/tools/tests/test_adopt31.py` holds them.

**After set 32 (an adoption of record text and record tooling over set 31, MESHSAT-1357).** Layers 4, 5, 8, 9 and 12 open with a block headed After set 32, directly under the layer's heading and above its set 31 block: the items set 32's records move, each naming its record; every row and note not named there keeps its set 31, set 30, set 29 or H2 text. Set 32 adopts, on set 31's promoted revision `5f25daf3`, five branches, `ee940742:v2/docs/records/int32/RESULT.md:88` `34 commits of the five branches over their bases`, regenerated to convergence, with record l4e7's results cache re-keyed ONCE; in its integration record's words, `ee940742:v2/docs/records/int32/RESULT.md:385` `**Set 32 closes NO power item.**`, and `ee940742:v2/docs/records/int32/RESULT.md:389` `It changes no baseline circuit draft, no board generator and no netlist`. No item is raised to MET by set 32 and no layer from 4 on is COMPLETE; nothing has been built, bought or measured. **Citations in the After set 32 blocks** read commit, path and line at the commit they name, a code span right after one being the words quoted from that line: set 32's integration record at fnd/res32's `ee940742`, the assessment at `3057ae43` and W53's generator line at `4d07a401` (each in this page's history after set 32's adoption); `v2/ecad/tools/tests/test_patch32.py` holds them.
```
Basis: `v2/docs/records/int32/RESULT.md`, sections 1, 2 and 6; set 31's head paragraph (line 38) as the form.

### L-02. `v2/docs/handover/LAYER-STATUS.md`, after line 352: Layer 4's set 32 block

Old text:
```text
## Layer 4. System architecture
```
New text:
```text
## Layer 4. System architecture

**After set 32: IN_PROGRESS.** Set 32 moves no state of this layer: `ee940742:v2/docs/records/int32/RESULT.md:40` `It closes NO power item, is not power-design closure and releases nothing; Layer 4's DESK gate`.
The set 31 and set 30 blocks below stand; the notes here name what set 32's records change.

- The chain. REVIEWED: `4d0ff8a2`, unchanged: no independent check of the engineering read a later revision. The base: set 31's
  promoted revision `5f25daf3`. CANDIDATE: `__CANDIDATE__`, the commit the gated release suite and the promotion gate ran on, to
  which main was fast-forwarded (written at the adoption). The gate, suite_gate's verdict line over the four pass logs: `__GATE__`.
- Record l4e7's results cache (WP-B: W61, W67, W71 on fnd/l4e7cache), `ee940742:v2/docs/records/int32/RESULT.md:387` `a change of record l4e7's cache KEY that moves no computed figure`,
  re-keyed ONCE in set 32 (`v2/docs/records/int32/RESULT.md`, sections 2h and 3c). Set 31's known item, record l4e7's paragraph 0a's
  history sentence (the set 31 block below; `v2/docs/records/int31/RESULT.md`, section 4a), is corrected by that re-key and the
  regeneration of its dependents, as the dependents' log shows: `__GATE__`.
- Unreviewed changes after cx46. Set 32's classification (`v2/docs/records/int32/CLASSIFICATION.md`, section 2) classes the 34
  commits of its five branches, `ee940742:v2/docs/records/int32/CLASSIFICATION.md:269` `12 of the 34 touch a file cx46 read`, 2 of
  them REVIEWED-INPUT CHANGED (W53's attribution and its tests), each UNREVIEWED since cx46 and credited nothing; the integration's
  own commits are its rows 31 to 33. They come beside set 31's 25 and set 30's 14 (the blocks below).
- The DESK gate and the three completion claims, unchanged, in the assessment's words (set 32 changes no line of it):
  `3057ae43:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:492` `### Layer 4's DESK gate: NOT PASSED`;
  `3057ae43:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:496` `### Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS`;
  `3057ae43:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:500` `### Power-design closure: BLOCKED. Fabrication release: BLOCKED.`. No claim is blended with
  another and none is given as a percentage; a promoted integration set is none of the three by itself.
```
Basis: `v2/docs/records/int32/RESULT.md`, sections 1, 2g, 2h, 3c and 6; `v2/docs/records/int32/CLASSIFICATION.md`, section 2;
`v2/docs/records/int31/RESULT.md`, section 4a; set 31's Layer 4 block as the form.

### L-03. `v2/docs/handover/LAYER-STATUS.md`, after line 609: Layer 5's set 32 block

Old text:
```text
## Layer 5. Partitioning and interfaces
```
New text:
```text
## Layer 5. Partitioning and interfaces

**After set 32: IN_PROGRESS.** Set 32 carries Q-55, N1a's phrase into V-E16 row 3 of the firmware contract (Layer 12's note below),
which record l5pwr's L5-F09 reading quotes, `ee940742:v2/docs/records/int32/RESULT.md:113` `run on the merged tree only: N1a's phrase into V-E16 row 3 of`;
no state of this layer moves, and the rows below keep their set 31 or set 29 text.
```
Basis: `v2/docs/records/int32/RESULT.md`, sections 2a (row 17) and 2d.

### L-04. `v2/docs/handover/LAYER-STATUS.md`, after line 725: Layer 8's set 32 block

Old text:
```text
## Layer 8. Schematics
```
New text:
```text
## Layer 8. Schematics

**After set 32: IN_PROGRESS on every board.** Set 32 changes how record l8p's and record l8r2's generators and tests read their
makers' PDF text and how record l8p's check 10c names each verdict word's check; no board is regenerated,
`ee940742:v2/docs/records/int32/RESULT.md:389` `It changes no baseline circuit draft, no board generator and no netlist`.

- Record l8p's `l8p_c4.py` (W55), `ee940742:v2/docs/records/int32/RESULT.md:109` `declares and reads its three sheets with its own table (so 26 record generators read each maker's PDF text through the helper, W34's 25 and this one)`;
  and its check 10c (W53), `ee940742:v2/docs/records/int32/RESULT.md:111` `print each word as its check's (cx45 "NOT CONFIRMED", cx46's items "NOT CLOSED")`.
  Both are UNREVIEWED since cx46 (`v2/docs/records/int32/CLASSIFICATION.md`, section 2).
```
Basis: `v2/docs/records/int32/RESULT.md`, sections 2a (rows 11 to 15), 2f and 6.

### L-05. `v2/docs/handover/LAYER-STATUS.md`, after line 793: Layer 9's set 32 block

Old text:
```text
## Layer 9. Pre-layout design analysis
```
New text:
```text
## Layer 9. Pre-layout design analysis

**After set 32: IN_PROGRESS.** Set 32 changes record l9t5's check 10j to name each verdict word's check (W53) and regenerates the
cascade's outputs on set 32's lineage (`v2/docs/records/int32/RESULT.md`, section 3b); every figure stays a MODEL reading on the
composed candidate, and nothing was routed, built or measured.

- Record l9t5's check 10j, `4d07a401:v2/docs/records/l9t5/l9t5_t10.py:1378` `DISPOSITION (10j, after cx46): Q3: cx45 'P0-3: NOT CONFIRMED', cx46's items 5 to 8 'NOT CLOSED'.`;
  no state moved off OPEN (`v2/docs/records/int32/RESULT.md`, section 2f), and the change is UNREVIEWED since cx46.
```
Basis: `v2/docs/records/int32/RESULT.md`, sections 2a (rows 14 and 15), 2f and 3b.

### L-06. `v2/docs/handover/LAYER-STATUS.md`, after line 872: Layer 12's set 32 block

Old text:
```text
## Layer 12. Firmware, bring-up, test plans and build documentation
```
New text:
```text
## Layer 12. Firmware, bring-up, test plans and build documentation

**After set 32: IN_PROGRESS.** Set 32 carries Q-55 into the firmware contract and W42's re-cites into TP-E11-29; nothing has run on
hardware.

- 12.1 (as the set 31 note below): `v2/docs/HW-FW-CONTRACT.md`'s V-E16 row 3 gains N1a's phrase by W40's apply script with its
  change-record row (W47), `ee940742:v2/docs/records/int32/RESULT.md:113` `run on the merged tree only: N1a's phrase into V-E16 row 3 of`,
  and `v2/docs/test-procedures/TP-SOLAR.md` quotes the register's annotated U5 line beside its line 297,
  `ee940742:v2/docs/records/int32/RESULT.md:114` `the register's annotated U5 line as`.
- 12.3 (as the set 31 note below): `ee940742:v2/docs/records/int32/RESULT.md:108` `TP-E11-29's two prose citations left as a row for the chain`,
  re-cited at the chain's step a5.
```
Basis: `v2/docs/records/int32/RESULT.md`, sections 2a (rows 9, 10, 17 to 19) and 2d.

## EXECUTION-PLAN.md

### P-01. `v2/docs/EXECUTION-PLAN.md`, after line 1757: set 32's milestone, after set 31's (the plan's entries are in time order)

Old text:
```text
(compute and storage apart, no total).
```
New text:
```text
(compute and storage apart, no total).

### Milestone: integration set 32 promoted as a DESK candidate (main `__CANDIDATE__`)

**Promoted:** main `__CANDIDATE__`, the candidate on set 32's integration branch, by fast-forward, the promotion log's line: `__GATE__`.
INTEGRATED = CANDIDATE = PROMOTED. REVIEWED: `4d0ff8a2` (cx46, "P0 RECHECK: CORRECTIONS NOT CLOSED."), unchanged: no independent
check of the engineering read a later revision. The base: set 31's promoted `5f25daf3`; five branches, 34 commits over their bases
(`records/int32/RESULT.md`, section 1), merged and regenerated to convergence, with record l4e7's results cache re-keyed ONCE (section
3c). Gated by `_bin/suite_gate.py`, its verdict line over the four pass logs: `__GATE__`. `candidate_guard`, its check line on every
host: `__GATE__`.

**What it closes:** no power item. "Set 32 closes NO power item." (`records/int32/RESULT.md`, section 6). Set 32 adopts the makers' PDF
text as committed verbatim inputs of 26 record generators with the tests' own reads of it declared (W34, W37, W42, W55, W81), each
verdict word attributed to its check (W53), the handover ZIP's cap at 100 MiB (Q-53), N1a's phrase in V-E16 row 3 (Q-55), and record
l4e7's results cache keyed on the sixteen numbers it reads of `l4e11_power.out` (WP-B) with ONE re-key; no baseline circuit draft,
board generator or netlist changed. Its classification counts 2 REVIEWED-INPUT CHANGED commits among the 34 of its five branches and
12 that touch a file cx46 read (`records/int32/CLASSIFICATION.md`, section 2), each UNREVIEWED since cx46 and credited nothing, beside
set 31's 25 and set 30's 14. Set 31's known item, record l4e7's paragraph 0a's history sentence (`records/int31/RESULT.md`, section
4a), corrected by set 32's re-key and its dependents' regeneration: `__GATE__`.

**The three claims, apart, and the gate, unchanged from set 30** (the coordinator's judgement of 6 October 2026, 10:45 CEST, in
`records/l4close/L4-DESK-GATE-ASSESSMENT.md`, section 6, of which set 32 changes no line): engineering-handover readiness READY AS A
DESK PACKAGE OF OPEN ITEMS; power-design closure BLOCKED; fabrication release BLOCKED. Layer 4's DESK gate NOT PASSED.

**Pending:** as after set 31, the owner's decision on Layer 5 (reported, not asked).

**The records:** `records/int32/RESULT.md`, `records/int32/CLASSIFICATION.md` and `records/int32/ENTRY-PAGES.patch.md` (the entry
pages' rows, applied); `handover/START-HERE.md` and `handover/supplier/SUPPLIER-HANDOVER.md` (section 0's revisions at set 32);
`handover/LAYER-STATUS.md` (the blocks headed After set 32, Layers 4, 5, 8, 9 and 12). Compute: `records/int32/RESULT.md`, section 5
(compute and storage apart, no total).
```
Basis: `v2/docs/records/int32/RESULT.md`, sections 1, 2, 3c, 4, 5 and 6; `v2/docs/records/int32/CLASSIFICATION.md`, section 2; set
31's milestone entry (lines 1731 to 1757) as the form.
