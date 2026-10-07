# Set 32: the rows for the adoption pages (START-HERE.md, SUPPLIER-HANDOVER.md, LAYER-STATUS.md, EXECUTION-PLAN.md; MESHSAT-1357)

**DONE:** 38 exact rows that bring the four adoption pages from set 31 to set 32: S-01 to S-15 for `v2/docs/handover/START-HERE.md`,
U-01 to U-16 for `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, L-01 to L-06 for `v2/docs/handover/LAYER-STATUS.md` and P-01 for
`v2/docs/EXECUTION-PLAN.md`, each with its page, its line, the old text, the new text and its basis, written by worker W95 on branch
fnd/res32 and corrected by worker W102 on W99's independent read of them (an AI review, not a qualified one): U-16's line on the
tree set 32's integration patches (B1), the known item's source (C2), the counts' scope (C1, C5), the held-back texts (C3), the tests
the rows break (C6), the candidate_guard line (C7), set 31's adoption dated (C8), L-03's wording (N8) and the claims pinned (N2);
`v2/ecad/tools/tests/test_patch32.py` holds every row against the pages as set 32's integration holds them (the paragraph "What the
rows are read against"); applied to the four pages on branch fnd/adopt32 by worker W105 (7 October
2026), each by its old text, the tokens left for the fill, and the tests of set 31's pages they break restated there with
`test_adopt32` new (the paragraph "The rows applied and the tests restated"); restated by worker W113 on W110's read (its B1, B2, C2
and C3) and W106's N-c, with the fill stages on the chain's own tree (the paragraph "The stages on the chain's own tree"). **NOT DONE:** the tokens in the rows' new texts, in this
file and on the four pages, are filled by the coordinator's fill tool (`<worktrees>/_bin/fill_res.py --set 32`, which reaches this
file because `records/int32/RESULT.md` names it, and the four pages since W103's extension, queue item Q-124); the adoption.
**NEXT:** at set 32's adoption, after its promotion, in this order: (1) fnd/adopt32 merged into set 32's lineage (set 31's step 12a
pattern); (2) the fill's first run (the CANDIDATE and GATE tokens of this file and of the four pages, each GATE from the source the
paragraph "Filling the GATE tokens" names); (3) W99's notes N6 and N7 confirmed (W106's N-b): L-05's "regenerates the cascade's
outputs", L-06's "re-cited at the chain's step a5" and L-06's note on 12.1 against RESULT's section 3b once its rows are filled, and
S-09's and U-07's "no independent check of the engineering read a later revision" against the scope of the planned independent read
of set 32's lineage (a read of the integration leaves them true; a read of the engineering restates both rows); (4) the adoption
commit; (5) the fill's second run (the ADOPTION token, here and in the pages' two ADOPTION cells, rows S-07 and U-05, which the
tool fills since W103's extension); (6) this header and RESULT's restated for the state after the fill and the adoption, and, since paragraph 0a at the candidate no longer
names set 30's integrator, rows S-05, U-03, L-02 and P-01's "is planned to be corrected" restated at the adoption as "is corrected",
with `test_patch32.py`'s pattern KNOWN, by `<worktrees>/_runs/int32/freeze/apply_known32.py` (W119, W123; W110's C2: the GATE
value is a clause of the regenerated paragraph 0a that set 31's paragraph 0a does not print, which `test_patch32.py` requires); (7) the
coordinator's dependency pass for the changed pages (l8gnd's pin of LAYER-STATUS and its cascade), as after set 31.

Record text only: it changes no state of any page, accepts nothing and closes nothing; prototype framing: nothing in the kit has been
built, bought, powered or measured.

**What the rows are read against.** The four pages as set 32's integration holds them before the rows are applied: main at
`ad757edb` (`ad757edb1be7e0fe3b586f986d2d704c9836fdcf`, set 31's adoption after the fill's second run, 6 October 2026, 23:44 CEST),
merged with the four other branches set 32's chain pins (fnd/w34pdftext `62300318`, fnd/s32attr `9210ab54`, fnd/s32small `7b7219a7`,
fnd/l4e7cache `5ee1e66e`; this branch changes no page), and the chain's step a5 (W42's `apply_supplier_0e_pointer.py`). Of those
branches only fnd/w34pdftext changes one of the four pages (fnd/s32attr carries the same commit): W37's re-take step adds 7 lines to
section 7 of `SUPPLIER-HANDOVER.md`, so U-16's old text stands on line 414 of the integrated page, not on main's line 407 (W99's
finding B1); step a5 adds a sentence inside line 146 and moves no line. W95 wrote the rows against fnd/adopt31's `b06ee99f` with set
31's fill values in memory, before main held set 31's adoption; W99 read them against main `ad757edb` and against the integrated
tree. On a tree that holds set 31's adoption (its `START-HERE.md` line 3 names set 31: the integrated tree after the chain's merges)
`test_patch32` reads the tree's own pages, and every row must hold there unchanged; a row that does not is restated before set 32's
adoption. On this branch before the integration it reads main's four pages at `ad757edb` through git, with no fill (no token is
left on them; W99's C4), and applies in memory each pinned branch's own change to the page (its diff from its merge base with
`ad757edb`, a change an earlier pin already made not applied twice) and step a5's `apply()` from the script at `62300318`. Every
"Old text" is one line, found exactly once on the line named; every "New text" differs from it. A row whose new text begins with the
whole old text inserts the lines after it. Two rows on one line (S-07 and S-08; U-05 and U-06) are applied in the order given, the
second on the line the first left. The rows of each page are applied on their own line numbers from the bottom of the page up, so
that an inserted paragraph moves no later row's line. Taken under the owner's standing rule of 26 September 2026 (authority SESSION,
W95, restated by W102): the test reads main and the pins through git rather than from copies under `inputs/` (set 31's form),
because `ad757edb` is main's and every pin is a commit set 32's chain merges, and copies of the four pages would add about 726 kB;
where `ad757edb` or a pin is absent and the tree's pages are not yet set 31's, the test raises Skip with that reason. Reversed by
copying the four integrated pages with their sha256 under `inputs/`.

**The revision rows, as set 30's pages define them.** Tested: the promoted revision, the commit the gated release suite and the
promotion gate ran on: set 32's candidate, to which main is fast-forwarded (the CANDIDATE token, as set 31's rows carry it after the
coordinator's ruling recorded in `records/int31/ENTRY-PAGES.patch.md`). Adopted: the adoption commit to which main is fast-forwarded
after the promotion (the ADOPTION token, filled in the fill's second run). Packaged: the commit the next supplier delta's README names
in its header, unchanged as a definition, so no row changes it. Reviewed: `4d0ff8a2` (cx46), unchanged: no independent check of the
engineering read a later revision (`records/int32/RESULT.md`, section 1: the candidate's row reads "no independent check of its
engineering"). The tokens are the CANDIDATE, the ADOPTION and the GATE tokens only; the PROMOTED and REKEY tokens are not used here,
because in set 32's record PROMOTED stands for two commits (the record's paragraph "Placeholders"). A GATE token stands where only a
printed line can give the value: the promotion's log line, the suite gate's verdict line, candidate_guard's check lines, and, for set
31's known item, paragraph 0a as the regenerated `l4e7_p0sol.out` prints it at the candidate, which exists only once set 32's re-key
and its dependents have run.

**Filling the GATE tokens (W99's C2 and C7).** The eight GATE tokens and their sources: P-01's promotion line, set 32's promote log
(the line naming main at the candidate); P-01's and L-02's gate, `suite_gate.txt` of set 32's freeze, its summary and PASS lines;
P-01's candidate_guard line, the PASS lines of `guard.log`, `rec-guard.log` and `runner/guard.log` joined by "; " in one value (W72's
N4; the line carries the words "candidate_guard check, every host", so `fill_res.py --set 32` suggests that source and raises its
three-host NOTE when the value carries fewer parts); and the known item in S-05, U-03, L-02 and P-01, the text of paragraph 0a of
`v2/docs/records/l4e7/l4e7_p0sol.out` at the candidate (`git show <candidate>:v2/docs/records/l4e7/l4e7_p0sol.out`), quoted without
a backtick, never a line of the dependents' log (W99's C2: that log prints the KEY check and the added rows' count, which cannot show
0a's sentence). `fill_res.py`'s suggestion for these four lines is its default, a step's log line; the value is not that, and
`test_patch32` refuses a value that is not in that paragraph. The rows say the known item is corrected: the adoption read paragraph
0a at the candidate, which no longer names set 30's integrator, and `apply_known32.py` (W119, W123) restated "is planned to be
corrected"; `test_patch32` refuses "is corrected" there while paragraph 0a at the candidate names set 30's integrator, and the planned
wording once the adoption read it; `records/int32/CLASSIFICATION.md`'s row 33 reads "no longer names set 30's integrator".

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

**How the rows were checked again (W102, 7 October 2026, from 00:18 CEST).** On this branch `test_patch32` reads main's pages at
`ad757edb` with the pins and step a5 in memory; those four pages equal, byte for byte, the pages of a scratch clone of W102's own
built as set 32's chain was then planned to build them (set 31's promoted `5f25daf3`, main `ad757edb` merged as step a1, the five pins with this
branch's checkpoint `57634a8e` for fnd/res32, fnd/w34pdftext's one conflict in the annex taken as ours in the clone only, step a5
run), where U-16's old text stands on line 414. In that clone, with stand-in commits for the re-key, the candidate and the
adoption: before the fill `test_patch32`, `test_res32` and `test_public_hygiene` read 11, 15 and 4 passed; the fill tool's template
read 97 rows, and its dry run with a one-part value for P-01's candidate_guard line printed the three-host NOTE for that line; the
first run applied 79 lines with 3 ADOPTION occurrences deferred, and the three modules read 30 passed; with the 38 rows applied the
three modules read 30 passed and set 31's page tests failed as the next paragraph lists; the second run applied 3 lines, after which
`test_patch32` refused S-07 and U-05 (the pages' two ADOPTION cells, W99's B2) until those two cells were filled by hand with the
second run's value, then 30 passed; a third run refused (exit 2). AI work, not a qualified review; no page of the tree was edited.
That hand fill described the tool before W103's extension (queue item Q-124, `<worktrees>/_bin/fill_res.py`, sha256
05d3017ce94d32a920c7fe4b0ebf41532e456c792600ae7dffb49bed28f2214f): the second run now fills S-07's and U-05's cells itself (W106's N-a;
W105's stages in the paragraph "The rows applied and the tests restated").

**The tests the rows break (W99's C6).** Applied to the integrated tree, the rows break these tests of set 31's pages, each to be
restated at the adoption with the row that moves the line it pins as its basis (as W65 restated set 30's for set 31): test_adopt31,
5 (`t_every_dated_citation_resolves_and_its_quote_is_found`, `t_the_checkers_refuse_their_defects`,
`t_the_claims_are_the_assessments_lines_verbatim`, `t_the_plan_entry_is_one_and_last`,
`t_the_set_31_blocks_sit_first_under_their_headings`); test_entrypage, 3
(`t_a_filled_placeholder_names_one_promoted_commit_and_the_adopted_files`, `t_every_section_a_page_points_to_exists`,
`t_the_six_states_stand_apart_in_each_page`); test_w30entry, 2 (`t_every_placeholder_is_filled_with_the_promoted_commit`,
`t_the_revision_rows_name_the_promoted_commit`); test_lstat31, 1
(`t_each_block_sits_between_its_heading_and_its_set_29_block_and_no_other_layer_has_one`). test_lstat32 and test_res31 hold. A sixth
of test_adopt31's, `t_the_entry_pages_are_the_copies_with_every_row_applied`, failed on the integrated tree before any row of set 32
when W99 read it (W99's N1) and is not counted among the five; since W103's `33a7b7d5` (queue item Q-123) it judges set 31's rows at
set 31's adoption commits through git and passes there (W106's N-a).

**The rows applied and the tests restated (W105, 7 October 2026, from 00:43 CEST, branch fnd/adopt32).** fnd/adopt32 starts at main
`ad757edb`, with W103's `33a7b7d5` and this branch's `607cd157` merged; the 38 rows were applied to main's four pages, each located by
its old text (exactly once on its page) and applied bottom-up, two rows on one line in the given order, every token left for the
fill. Every old text stood once on its named line but U-16's, which stands on main's line 407: the 7 lines fnd/w34pdftext adds to
section 7 of the supplier page are not on this branch (they arrive with set 32's lineage and do not touch U-16's lines, so the merge
carries U-16's paragraph to line 414's place). Applied before the fill (W65's form for set 31), the rows broke 15 tests on
fnd/adopt32: the eleven of the paragraph above; three that only the tokens standing before the fill break
(`test_adopt31.t_the_pages_carry_only_their_declared_tokens`, `test_entrypage.t_the_placeholder_is_literal_and_alone`,
`test_lstat32.t_the_placeholders_stand`); and `test_l8gnd.t_the_committed_output_is_what_the_script_prints`, whose output pins
LAYER-STATUS.md's digest and is owed to the coordinator's dependency pass, as after set 31. Each set 31 page test is restated with
these rows as its basis, in W103's form: a predicate that pins set 31's rows judges them at set 31's adoption commits `73941afc` and
`ad757edb` through git, with the same predicate; what set 32 does not change stays read on the working tree (test_entrypage's other
anchors and its five other states, test_w30entry's Packaged row and its refusal of the INTEGRATED placeholder and of any token but
set 32's three, test_lstat31's counts of set 30's and set 29's blocks), and test_lstat32's set 30 placeholders stay read on the tree
outside set 31's and set 32's blocks. The working tree's four pages are held by `test_adopt32` (new): each page equals set 31's
adopted page at `ad757edb` with the own change of each pinned branch the judged revision holds, step a5 where the page carries its
sentence, and these 38 rows, nothing else (so the eight texts of set 31's rows no set 32 row replaces, W106's N-d, are held there),
the tokens as the fill's stage leaves them, and set 32's added text without a dash, an acceptance word or a percentage; it judges
the newest revision whose START-HERE line 3 names set 32, so a later set's rows never fail it. In a scratch clone of W105's own, built as set 32's chain was then planned to build the tree (set 31's promoted `5f25daf3`, main
`ad757edb` merged as step a1, W103's `33a7b7d5`, the five pins with fnd/res32 at `607cd157`, fnd/w34pdftext's one conflict in the
annex taken as ours in the clone only, step a5 run), with stand-in commits for the re-key and the candidate, fnd/adopt32 at
`564dc7f6` merged clean as set 31's step 12a merged its branch (U-16's paragraph follows its old text, which stands at line 427 of
the merged page once the rows above it are in, line 414 before them); the ten modules `test_patch32`, `test_res32`, `test_adopt31`,
`test_adopt32`, `test_entrypage`, `test_w30entry`, `test_lstat31`, `test_lstat32`, `test_res31` and `test_public_hygiene` read 113
passed, 0 failed, 0 skipped before the fill; the fill tool's template read 122 rows (this file 25, RESULT.md 70, CLASSIFICATION.md 2,
the four pages 25: START-HERE.md 8, SUPPLIER-HANDOVER.md 8, LAYER-STATUS.md 3, EXECUTION-PLAN.md 6), its first run applied 101 lines
with 5 ADOPTION occurrences deferred, and the ten read 113 passed; with a stand-in adoption commit its second run applied 5 lines
(S-07's and U-05's cells among them, no hand fill), no token was left in the seven files, and the ten read 113 passed; a third run
refused (exit 2); with START-HERE's line 3 then rewritten as a later set's rows would, `test_adopt32` judged the newest commit naming
set 32 and read 4 passed. The 43 mutants of the restated predicates (the bytes read at either adoption commit, or the tree's page,
changed in memory) were each refused, on fnd/adopt32 and in that clone after the second run. AI work, not a qualified review.

**The stages on the chain's own tree (W113, 7 October 2026, from 01:43 CEST, on W110's B1, B2 and C3).** W105's clone and W102's
were not the tree set 32's chain builds: since W104 (W100's S1) the chain's base is main's tip at its start, `be07863b`
(`<worktrees>/_runs/int32/real-0115.log:1`), and on that tree W110 read the ten modules as 116 passed, 1 failed before the fill and
114 passed, 3 failed after each run (test_res31's W98 test and test_res32's `p_filled`, its B1 and B2). W113 merged main `be07863b`
into fnd/adopt32, restated those two tests (test_res31 reads LAYER-STATUS and the plan at set 31's adoption commits through git;
test_res32 places set 31's promoted revision as an ancestor of the re-key and the chain's base on its first-parent line) and named
the lineage's start beside the BASE row in rows L-01, L-02 and P-01 (C3). In a scratch clone of W113's own, built as W110 built it
(main's tip at the chain's start `be07863b`, the five pins with fnd/res32 at `607cd157` merged with `--no-ff`, fnd/w34pdftext's
one conflict in the annex taken as ours in the clone only, step a5 run, stand-in commits for the re-key and the candidate (the
candidate's with a stand-in paragraph 0a in WP-B's words, so that the known item's value is a clause set 31's paragraph does not
print), then fnd/adopt32 at its commit c1c67169 merged clean), the ten modules read 117 passed, 0 failed, 0 skipped before
the fill; the fill tool's template read 122 rows (this file 25, RESULT.md 70, CLASSIFICATION.md 2, START-HERE.md 8,
SUPPLIER-HANDOVER.md 8, LAYER-STATUS.md 3, EXECUTION-PLAN.md 6), its first run applied 101 lines with 5 ADOPTION occurrences deferred
and printed no NOTE (P-01's candidate_guard value three PASS lines), and the ten read 117 passed; with a stand-in adoption commit its
second run applied 5 lines, no token was left in the seven files, and the ten read 117 passed; a third run refused (exit 2); with
START-HERE's line 3 rewritten as a later set's rows would, `test_adopt32` read 4 passed. AI work, not a qualified review.

## START-HERE.md

### S-01. `v2/docs/handover/START-HERE.md`, line 3: the current revision

Old text:
```text
**Current revision: set 31 (6 October 2026), the revision `5f25daf3`, an adoption of record text over set 30's `dd1aed00d0a0a521063b5792550bc510c4707c59`. Read section 0 first.**
```
New text:
```text
**Current revision: set 32, the revision `f08e3961`, an adoption of record text and record tooling over set 31's `5f25daf3`. Read section 0 first.**
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

**Set 32** (the revision `f08e3961`). An adoption of record text and record tooling over set 31: 26 record generators read their
makers' PDF text from committed verbatim extractions instead of running pdftotext (a held-back sheet's text is held back with the
sheet and re-taken after the fetch: 57 texts, `v2/docs/records/int32/RESULT.md`, section 2a), and the tests' own reads of it are
declared (W34, W37, W42, W55, W81); each verdict word is attributed to its check (W53: cx45's "NOT CONFIRMED", cx46's "NOT CLOSED"); the handover
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
corrected by set 32's one re-key and the regeneration of its dependents (paragraph 0a at the candidate no longer names set 30's integrator: read at the adoption, after these rows were
written); the regenerated `v2/docs/records/l4e7/l4e7_p0sol.out` at the candidate prints in its paragraph 0a: `its key field is the key of its own parts and no part differs from this tree's`.
```
Basis: `v2/docs/records/int32/RESULT.md`, section 6 (no power item; the three claims unchanged, quoted from the assessment's lines
492, 496 and 500); `v2/docs/records/int31/RESULT.md`, section 4a (the known item, "to be corrected with set 32's single re-key");
`v2/docs/records/int32/CLASSIFICATION.md`, row 33 ("no longer names set 30's integrator"); the GATE's source, the
paragraph "Filling the GATE tokens".

### S-06. `v2/docs/handover/START-HERE.md`, line 117: the Tested row

Old text:
```text
| Tested | `5f25daf3` | set 31's promoted revision (set 30's was `dd1aed00d0a0a521063b5792550bc510c4707c59`, kept as dated history):
```
New text:
```text
| Tested | `f08e3961` | set 32's promoted revision (set 31's was `5f25daf3` and set 30's `dd1aed00d0a0a521063b5792550bc510c4707c59`, each kept as dated history):
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
`, 6 October 2026, pushed 23:43:17 CEST, kept as dated history; set 30's was
```
Basis: as S-07; applied on the line S-07 left, so the row reads set 32's adoption commit, then set 31's, then set 30's. Set 31's
date in set 30's form (W99's C8): the queue's entry "23:35 to 23:44 SET 31 ADOPTED" (`<worktrees>/_runs/int30/QUEUE.md`), which
gives the adoption commit `73941afc2d4698c5cf81da443064fe7ffe7ca620` and main "pushed 23:43:17".

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
the candidate commit `5f25daf3` is one of the 106, that file's row 36. Set 32 adds its own: of the 34 commits of its five branches, 12 touch a file cx46 read, 2 of them REVIEWED-INPUT CHANGED under set 30's rule (reading A), each "UNREVIEWED since cx46" (`v2/docs/records/int32/CLASSIFICATION.md`, section 2), counted over the branch commits alone; the integration's own commits are that file's rows 31 to 33, the candidate commit `f08e3961` its row 33, classed at the adoption (its row 31 expects the regenerated outputs that carry row 14's lines to be REVIEWED-INPUT CHANGED too), unlike set 31's 25, counted over all 106 of its commits.
```
Basis: `v2/docs/records/int32/CLASSIFICATION.md`, section 2 (34 rows; `REVIEWED-INPUT CHANGED` 2; "The rows that touch a file cx46
read: 12, all UNREVIEWED since cx46.") and its rows 31 to 33 (row 31's last cell: "row 14's lines reach `l9t5_t10.out` and
`l8p_c4.out`"); set 31's 25 over the 106 commits of `dd1aed00..5f25daf3` as the page states it (W99's C1: the scope stated now; the
counts are restated at the adoption if section 2's recount moves the branch rows' figures, which `test_patch32` reads from the
adopted classification).

### S-11. `v2/docs/handover/START-HERE.md`, line 134: the documents row

Old text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`5f25daf3`, set 31) |
```
New text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`f08e3961`, set 32) |
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
From a full git checkout at `f08e3961`:
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
PDF text from committed verbatim extractions (a held-back sheet's text is held back with the sheet and re-taken after the fetch,
as section 7 gives it: 57 texts), and the tests' own reads of it are declared; each verdict word is attributed to its check; the handover ZIP's cap is raised to 100 MiB; N1a's phrase is carried into V-E16 row 3 of the firmware contract; record l4e7's
results cache is keyed on the sixteen numbers the record reads of `l4e11_power.out`, with ONE re-key; the outputs these move are
regenerated. It changes the Tested and Adopted revisions of 0a, adds its integration record to 0c, and changes none of the states of
0b: "Set 32 closes NO power item." (`records/int32/RESULT.md`, section 6). The DESK gate and the three completion claims, in the
assessment's words, unchanged: "Layer 4's DESK gate: NOT PASSED"; "Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN
ITEMS"; "Power-design closure: BLOCKED. Fabrication release: BLOCKED." (`records/l4close/L4-DESK-GATE-ASSESSMENT.md`, section 6). Set
31's known item, record l4e7's paragraph 0a's history sentence (`records/int31/RESULT.md`, section 4a), is corrected by set 32's one
re-key and the regeneration of its dependents (paragraph 0a at the candidate no longer names set 30's integrator: read at the adoption, after these rows were written); the regenerated
`records/l4e7/l4e7_p0sol.out` at the candidate prints in its paragraph 0a: `its key field is the key of its own parts and no part differs from this tree's`.
```
Basis: `v2/docs/records/int32/RESULT.md`, the paragraph "What set 32 is", sections 2a and 6; `v2/docs/records/int31/RESULT.md`,
section 4a; `v2/docs/records/int32/CLASSIFICATION.md`, row 33; the GATE's source, the paragraph "Filling the GATE tokens"; the
re-take step, section 7 of the integrated page (W37 on fnd/w34pdftext).

### U-04. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 42: the Tested row

Old text:
```text
| Tested | `5f25daf3` | set 31's promoted revision (set 30's was `dd1aed00d0a0a521063b5792550bc510c4707c59`, kept as dated history):
```
New text:
```text
| Tested | `f08e3961` | set 32's promoted revision (set 31's was `5f25daf3` and set 30's `dd1aed00d0a0a521063b5792550bc510c4707c59`, each kept as dated history):
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
`, 6 October 2026, pushed 23:43:17 CEST, kept as dated history; set 30's was
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
the candidate commit `5f25daf3` is one of the 106, that file's row 36. Set 32 adds its own: of the 34 commits of its five branches, 12 touch a file cx46 read, 2 of them REVIEWED-INPUT CHANGED under set 30's rule (reading A), each "UNREVIEWED since cx46" (`records/int32/CLASSIFICATION.md`, section 2), counted over the branch commits alone; the integration's own commits are that file's rows 31 to 33, the candidate commit `f08e3961` its row 33, classed at the adoption (its row 31 expects the regenerated outputs that carry row 14's lines to be REVIEWED-INPUT CHANGED too), unlike set 31's 25, counted over all 106 of its commits.
```
Basis: as S-10.

### U-10. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 63: the documents row

Old text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`5f25daf3`, set 31) |
```
New text:
```text
| Documents and editable artifacts | on main as a DESK candidate (`f08e3961`, set 32) |
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
From a full git checkout at `f08e3961`
```
Basis: as S-13.

### U-14. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, line 157: the suite's line

Old text:
```text
The gated release suite's line for `5f25daf3` is in the package's `README.md` and in
```
New text:
```text
The gated release suite's line for `f08e3961` is in the package's `README.md` and in
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

### U-16. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, after line 414: the dated entry

Old text:
```text
  Layer 4's DESK gate and the three completion claims stand as set 30's assessment gives them.
```
New text:
```text
  Layer 4's DESK gate and the three completion claims stand as set 30's assessment gives them.
- **Set 32, the revision `f08e3961`, dated by its adoption commit** (section 0). An adoption of record text and record tooling
  over set 31: the makers' PDF text as committed verbatim inputs of 26 record generators (a held-back sheet's text held back with the
  sheet and re-taken after the fetch: 57 texts), the verdict words attributed to their checks, the ZIP's cap, N1a's phrase in V-E16
  row 3, record l4e7's cache KEY on the sixteen numbers it reads, ONE re-key, regenerated
  (`v2/docs/records/int32/RESULT.md`). No circuit change is applied, and nothing in it accepts, closes or promotes a design claim;
  Layer 4's DESK gate and the three completion claims stand as set 30's assessment gives them.
```
Basis: `v2/docs/records/int32/RESULT.md`, the paragraph "What set 32 is", sections 2a and 6. Line 414 is the line on the page as
set 32's integration holds it (main's line 407 plus the 7 lines fnd/w34pdftext adds to section 7; W99's B1).

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

**After set 32 (an adoption of record text and record tooling over set 31, MESHSAT-1357).** Layers 4, 5, 8, 9 and 12 open with a block headed After set 32, directly under the layer's heading and above its set 31 block: the items set 32's records move, each naming its record; every row and note not named there keeps its set 31, set 30, set 29 or H2 text. Set 32 adopts, on set 31's promoted revision `5f25daf3` (the record's BASE row; its lineage starts at main's tip `be07863b`, the chain's base, which carries set 31's adoption and follow-ups over it), five branches, `ee940742:v2/docs/records/int32/RESULT.md:88` `34 commits of the five branches over their bases`, regenerated to convergence, with record l4e7's results cache re-keyed ONCE; in its integration record's words, `ee940742:v2/docs/records/int32/RESULT.md:385` `**Set 32 closes NO power item.**`, and `ee940742:v2/docs/records/int32/RESULT.md:389` `It changes no baseline circuit draft, no board generator and no netlist`. No item is raised to MET by set 32 and no layer from 4 on is COMPLETE; nothing has been built, bought or measured. **Citations in the After set 32 blocks** read commit, path and line at the commit they name, a code span right after one being the words quoted from that line: set 32's integration record at fnd/res32's `ee940742`, the assessment at `3057ae43` and W53's generator line at `4d07a401` (each in this page's history after set 32's adoption); `v2/ecad/tools/tests/test_patch32.py` holds them.
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
  promoted revision `5f25daf3` (the record's BASE row); the lineage starts at main's tip `be07863b`, the chain's base, which descends
  from it. CANDIDATE: `f08e3961`, the commit the gated release suite and the promotion gate ran on, to
  which main was fast-forwarded (written at the adoption). The gate, suite_gate's verdict line over the four pass logs: `suite_gate: candidate f08e396175dd; totals tests: 2973 passed, 0 failed, 2 skipped + tests: 26 passed, 0 failed, 0 skipped + tests: 253 passed, 0 failed, 0 skipped + tests: 213 passed, 0 failed, 1 skipped; result lines 3468 (3465 PASS, 3 SKIP, 0 FAIL); modules 269 of 269 ran; suite_gate: PASS`.
- Record l4e7's results cache (WP-B: W61, W67, W71 on fnd/l4e7cache), `ee940742:v2/docs/records/int32/RESULT.md:387` `a change of record l4e7's cache KEY that moves no computed figure`,
  re-keyed ONCE in set 32 (`v2/docs/records/int32/RESULT.md`, sections 2h and 3c). Set 31's known item, record l4e7's paragraph 0a's
  history sentence (the set 31 block below; `v2/docs/records/int31/RESULT.md`, section 4a), is corrected by that re-key and the
  regeneration of its dependents (paragraph 0a at the candidate no longer names set 30's integrator: read at the adoption, after these rows were written); the regenerated
  `v2/docs/records/l4e7/l4e7_p0sol.out` at the candidate prints in its paragraph 0a: `its key field is the key of its own parts and no part differs from this tree's`.
- Unreviewed changes after cx46. Set 32's classification (`v2/docs/records/int32/CLASSIFICATION.md`, section 2) classes the 34
  commits of its five branches, `ee940742:v2/docs/records/int32/CLASSIFICATION.md:269` `12 of the 34 touch a file cx46 read`, 2 of
  them REVIEWED-INPUT CHANGED (W53's attribution and its tests), each UNREVIEWED since cx46 and credited nothing, counted over the
  branch commits alone; the integration's own commits are its rows 31 to 33, classed at the adoption. They come beside set 31's 25
  over all 106 of its commits (its integration's among them) and set 30's 14 over its 45 (the blocks below).
- The DESK gate and the three completion claims, unchanged, in the assessment's words (set 32 changes no line of it):
  `3057ae43:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:492` `### Layer 4's DESK gate: NOT PASSED`;
  `3057ae43:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:496` `### Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS`;
  `3057ae43:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:500` `### Power-design closure: BLOCKED. Fabrication release: BLOCKED.`. No claim is blended with
  another and none is given as a percentage; a promoted integration set is none of the three by itself.
```
Basis: `v2/docs/records/int32/RESULT.md`, sections 1, 2g, 2h, 3c and 6; `v2/docs/records/int32/CLASSIFICATION.md`, section 2;
`v2/docs/records/int31/RESULT.md`, section 4a; set 31's Layer 4 block as the form; the known item's GATE, the paragraph "Filling
the GATE tokens"; the counts' scope as S-10's basis gives it (W99's C1).

### L-03. `v2/docs/handover/LAYER-STATUS.md`, after line 609: Layer 5's set 32 block

Old text:
```text
## Layer 5. Partitioning and interfaces
```
New text:
```text
## Layer 5. Partitioning and interfaces

**After set 32: IN_PROGRESS.** Set 32 carries Q-55, N1a's phrase into V-E16 row 3 of the firmware contract (Layer 12's note below;
V-E16's rows 2 and 3 are the rows record l5pwr's L5-F09 d wrote, and `test_l5pwr`'s reading of L5-F09 d admits N1a's words there once
Q-55's script has run), `ee940742:v2/docs/records/int32/RESULT.md:113` `run on the merged tree only: N1a's phrase into V-E16 row 3 of`;
no state of this layer moves, and the rows below keep their set 31 or set 29 text.
```
Basis: `v2/docs/records/int32/RESULT.md`, sections 2a (row 17) and 2d; the docstring of record s32small's `apply_q55_ve16.py` at
fnd/s32small `7b7219a7`, its lines 4 and 17 (record l5pwr's L5-F09 d wrote V-E16's rows 2 and 3; test_l5pwr's reading of L5-F09 d
admits N1a's words; W99's N8).

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

### Milestone: integration set 32 promoted as a DESK candidate (main `f08e3961`)

**Promoted:** main `f08e3961`, the candidate on set 32's integration branch, by fast-forward, the promotion log's line: `GitHub main at f08e396175dd418434061d731e08111d006d6efa (_runs/int32/promote-1041.log)`.
INTEGRATED = CANDIDATE = PROMOTED. REVIEWED: `4d0ff8a2` (cx46, "P0 RECHECK: CORRECTIONS NOT CLOSED."), unchanged: no independent
check of the engineering read a later revision. The base: set 31's promoted `5f25daf3` (the record's BASE row; the lineage starts at main's tip `be07863b`, the chain's base, which descends from it); five branches, 34 commits over their bases
(`records/int32/RESULT.md`, section 1), merged and regenerated to convergence, with record l4e7's results cache re-keyed ONCE (section
3c). Gated by suite_gate with G7 (`_bin/suite_gate.py`), its verdict line over the four pass logs: `suite_gate: candidate f08e396175dd; totals tests: 2973 passed, 0 failed, 2 skipped + tests: 26 passed, 0 failed, 0 skipped + tests: 253 passed, 0 failed, 0 skipped + tests: 213 passed, 0 failed, 1 skipped; result lines 3468 (3465 PASS, 3 SKIP, 0 FAIL); modules 269 of 269 ran; suite_gate: PASS`.
The candidate_guard check, every host, its PASS line on each host in one value: `candidate_guard: PASS candidate f08e396175dd418434061d731e08111d006d6efa: 1111 evidence file(s) present and unchanged, every output binds but the 4 declared, 1 results cache(s) frozen; candidate_guard: PASS candidate f08e396175dd418434061d731e08111d006d6efa: 1111 evidence file(s) present and unchanged, every output binds but the 4 declared, 1 results cache(s) frozen; candidate_guard: PASS candidate f08e396175dd418434061d731e08111d006d6efa: 1111 evidence file(s) present and unchanged, every output binds but the 4 declared, 1 results cache(s) frozen`.

**What it closes:** no power item. "Set 32 closes NO power item." (`records/int32/RESULT.md`, section 6). Set 32 adopts the makers' PDF
text as committed verbatim inputs of 26 record generators (a held-back sheet's text held back with the sheet and re-taken after the
fetch: 57 texts) with the tests' own reads of it declared (W34, W37, W42, W55, W81), each
verdict word attributed to its check (W53), the handover ZIP's cap at 100 MiB (Q-53), N1a's phrase in V-E16 row 3 (Q-55), and record
l4e7's results cache keyed on the sixteen numbers it reads of `l4e11_power.out` (WP-B) with ONE re-key; no baseline circuit draft,
board generator or netlist changed. Its classification counts 2 REVIEWED-INPUT CHANGED commits among the 34 of its five branches and
12 that touch a file cx46 read (`records/int32/CLASSIFICATION.md`, section 2), each UNREVIEWED since cx46 and credited nothing,
counted over the branch commits alone (the integration's rows 31 to 33 are classed at the adoption), beside set 31's 25 over all 106
of its commits (its integration's among them) and set 30's 14 over its 45. Set 31's known item, record l4e7's paragraph 0a's history
sentence (`records/int31/RESULT.md`, section 4a), is corrected by set 32's re-key and its dependents' regeneration (paragraph 0a at the candidate no longer names set 30's integrator: read at the adoption);
the regenerated `records/l4e7/l4e7_p0sol.out` at the candidate prints in its paragraph 0a: `its key field is the key of its own parts and no part differs from this tree's`.

**The three claims, apart, and the gate, unchanged from set 30** (the coordinator's judgement of 6 October 2026, 10:45 CEST, in
`records/l4close/L4-DESK-GATE-ASSESSMENT.md`, section 6, of which set 32 changes no line): engineering-handover readiness READY AS A
DESK PACKAGE OF OPEN ITEMS; power-design closure BLOCKED; fabrication release BLOCKED. Layer 4's DESK gate NOT PASSED.

**Pending:** as after set 31, the owner's decision on Layer 5 (reported, not asked).

**The records:** `records/int32/RESULT.md`, `records/int32/CLASSIFICATION.md` and `records/int32/ENTRY-PAGES.patch.md` (the entry
pages' rows, applied); `handover/START-HERE.md` and `handover/supplier/SUPPLIER-HANDOVER.md` (section 0's revisions at set 32);
`handover/LAYER-STATUS.md` (the blocks headed After set 32, Layers 4, 5, 8, 9 and 12). Compute: `records/int32/RESULT.md`, section 5
(compute and storage apart, no total).
```
Basis: `v2/docs/records/int32/RESULT.md`, sections 1, 2, 2a, 3c, 4, 5 and 6; `v2/docs/records/int32/CLASSIFICATION.md`, section 2
and row 33; set 31's milestone entry (lines 1731 to 1757) as the form; the four GATE tokens' sources, the paragraph "Filling the GATE
tokens" (the candidate_guard line on its own line, so the fill tool's suggestion for it names the three hosts; W99's C7).
