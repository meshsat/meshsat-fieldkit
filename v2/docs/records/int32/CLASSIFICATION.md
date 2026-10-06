# Set 32: every commit of set 32's branches over their bases, classified (bound by `records/int32/RESULT.md`; the owner's part 25; MESHSAT-1357)

**DONE:** the 14 commits of set 32's two branches as last read (fnd/w34pdftext `5b3153aa`, 10 commits over `aed4bd23`; fnd/s32small `7b7219a7`, 4 commits over `eff28be3`) classified, one row each, and the counts. **NOT DONE:** the rows of the integration's own commits (the chain's merges and converged outputs, the re-key's cache, the candidate commit), each a placeholder row below, and the rows of any commit a branch gains after this reading. **NEXT:** the coordinator fills the placeholder rows from git and the chain's log at the adoption and recomputes section 2.

**What this is.** Drafted by worker W44 on branch fnd/res32 (base `3057ae43`, set 31's lineage as the coordinator gave it) on 6
October 2026 from 16:36 CEST, for adoption with `records/int32/RESULT.md` at set 32's promotion (queue item Q-64), in the form of set 31's
draft (`records/int31/CLASSIFICATION.md` on fnd/res31 `4196e9df`, W39) and set 30's record (`records/int30/CLASSIFICATION.md`, W15 and
W26). It designs nothing, runs no generator, suite or box job, accepts nothing, promotes nothing and changes no verdict: it reads git.
Prototype framing: nothing in the kit is built, bought, powered or measured; the candidate is a desk design.

**The rule restated (6 October 2026, from 17:13 CEST).** Worker W50 applied W49's reconciliation
(`_runs/claude/w49recon/REPORT-AS-RECEIVED.md`, section 4, the rows for this record) under the coordinator's ruling (reading A, quoted
below): the class `REVIEWED-INPUT CHANGED` is now set 30's rule quoted verbatim, its two differences from W39's wording are stated, set
30's row 44 is the precedent for rows 2, 3 and 4, and the placeholder rows are to be classed under the rule's second sentence when
filled. No row changes class and no count moves; no verdict, figure or claim of any file was changed, and set 30's adopted record was
not edited.

**The bounds.** Set 32's base is set 31's promoted revision, `__S31_PROMOTED__` (it does not exist when this table is written). Set 32 adopts
two branches, each read over the commit where it leaves set 31's lineage or main: fnd/w34pdftext, tip
`5b3153aa4136f08ab186a2b5da53c1c4f0c3ecac`, over `aed4bd234644c80fa494299b21099acf6d2454c1` (set 31's regenerated lineage, row 25 of set
31's draft; `git merge-base 3057ae43 5b3153aa` prints it), `git rev-list --count aed4bd23..5b3153aa` prints 10; fnd/s32small, tip
`7b7219a7d0a695b6b866435116905964a68f5578`, over `eff28be3b80f882db545a849b0da1def0217f63d` (main's follow-up after set 30's adoption,
in set 31's lineage since its merge `d5d9c252`), `git rev-list --count eff28be3..7b7219a7` prints 4. Neither branch holds a merge
(`--merges` prints nothing on both). The tips were read with `git rev-parse` at 16:38 CEST (fnd/s32small then at W40's `a7a485ab`), again at 16:55 CEST when W47's two
commits had landed, and again at the last commit of this file.
Rows 1 to 10 are fnd/w34pdftext's commits and rows 11 to 14 fnd/s32small's, each oldest first (`git rev-list --topo-order --reverse`);
every commit of the two ranges has exactly one row.

**How it was read.** `git log`, `git show --stat`, `git show --name-only` and `git diff -U0` per commit; for every file a row calls
reviewed, the diff read line by line. Dates are the committer dates in Europe/Amsterdam. The sha, date, subject and file-count columns were
printed by a script from git, not typed; `test_res32.py` reads them back. Citations: `<sha>:path:N` followed by a code span quotes line N
of that file at that revision. The folders column groups every file under `v2/vendor/` as one entry (all of them, on these branches,
extracted texts and their sidecars under a `pdftext/` folder).

**The delta cx46 read, the set each row's reason states membership in** ("a reviewed file" and "a file cx46 read" below mean a file of
it; the class itself is set 30's rule, the paragraph after next). This table takes the set as W39 took it: the 60 files of `git diff --name-only 06077cee 4d0ff8a2` (the delta cx46 read; cx46's own base is
`3057ae43:v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:8` `"base_commit": "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e",`)
plus the L4-E9 page `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md` and its output `l4e9_power_path.out`. 8 of the two ranges' 382
changed files are in that set, all on fnd/w34pdftext: `l8r2_gndret.py`, `l8r2_p0.py`, `l4e11_power.py`, `l4e9_power_path.py`,
`l9t5_f01.py`, `l9t5_paloop.py`, `l9t5_t10.py` and `SUPPLIER-VALIDATION-ANNEX-2026-10-05.md`. No baseline circuit draft
(`apply_gen_sch_*`), no board generator (`gen_sch_*`), no netlist and no `.out` file changed on either branch. Every row that touches a
reviewed file says so at the end of its reason and says **UNREVIEWED since cx46**: no independent checker read any change of these ranges
after cx46 (W36's read of fnd/w34pdftext at `6dc69ad2` is a worker's AI review of the branch, section 2 of RESULT.md, and is not that
check), and none is credited.

**The REVIEWED-INPUT CHANGED rule: set 30's, quoted verbatim.** The class is set 30's, line 11 of
`v2/docs/records/int30/CLASSIFICATION.md` (in this tree as at main `eff28be3`; `eff28be3:v2/docs/records/int30/CLASSIFICATION.md:11`):

> - `REVIEWED-INPUT CHANGED`: a figure, a verdict word, a circuit draft or a composition of drafts, a case row, a requirement or a limit that cx46 read in `4d0ff8a2` is different now; the reason quotes the old and the new value with file and line, and names the cx46 item that read it, or says that none names it. A quote or restatement that carries another row's change into a file of the reviewed tree is classed so too, its reason naming the source row and whether the file was in the delta cx46 read (`cx46:17`).

**How its second sentence is read: reading A, the coordinator's ruling for set 31 and set 32** (authority SESSION under the owner's
standing rule of 26 September 2026; `<worktrees>/_runs/int30/QUEUE.md`, entry "17:13 (clock) COORDINATOR'S RULING", `READING A for set 31 and set 32 (the literal second sentence`):
a quote or restatement that carries another row's change into any file present at `4d0ff8a2` is classed `REVIEWED-INPUT CHANGED`,
whether or not the file was in the delta cx46 read. This rule replaces the class words this table first took from set 31's draft
(W39's, which begin `4196e9df:v2/docs/records/int31/CLASSIFICATION.md:40` `a figure, a state or verdict word, a composition or release grouping, a case or its placement, an`,
and which the first draft of this paragraph called "the same in substance" as W15's). They differ from set 30's in two ways (W49's
reconciliation, sections 0 and 4): (1) set 30's rule covers a change carried into any file of the reviewed tree, where W39's covers a
reviewed file only, the 62 files below; (2) set 30's rule requires each such reason to name the source row and whether the file was in
the delta cx46 read.

**Applied to the two branches.** The seven reviewed generators on fnd/w34pdftext change HOW they obtain a maker's PDF text (the
extraction call becomes the helper's call on the same PDF with the same options, the input list gains the text), never a figure, state
word, composition, case, requirement or limit in their diff, and the annex's change is five line numbers in citations whose cited words
are unchanged and one sentence inside its citation-form paragraph's line; no row carries another row's change into a file of the
reviewed tree (W49's reconciliation, section 3). So no row of the two branches is classed REVIEWED-INPUT CHANGED, and the four rows that
touch a reviewed file carry **UNREVIEWED since cx46** with their other classes. The precedent is set 30's row 44, a guard's logic
corrected in `l4e7_p0sol.py`, a generator of cx46's delta, with its printed figures unchanged and classed DIGEST RE-PIN and GENERATOR
DATA (text) there, its reason reading `eff28be3:v2/docs/records/int30/CLASSIFICATION.md:68` `no figure or verdict word moved`: rows 2,
3 and 4 are that case; row 9's moved citation line numbers are also set 30's rows 1 and 13 (one line of a delta file changed, RECORD TEXT). Read with
the wider rule (a touched reviewed file alone), rows 2, 3, 4 and 9 would be REVIEWED-INPUT CHANGED (4 rows); set 30's rows 1, 13 and 44
did not take it (each touched a file of cx46's delta and was not classed REVIEWED-INPUT CHANGED). W44's choice of the narrower reading
(a SESSION decision under the owner's standing rule of 26 September 2026) now rests on those precedents; reversed by re-classing the
four rows and recounting section 2. The reviewed OUTPUTS these generators write (for example `l4e11_power.out`, `l4e9_power_path.out`,
`l9t5_f01.out`, `l8r2_gndret.out`, `efuse_check.out`) move only at the integration, in the rows that are placeholders here; each
placeholder row is classed under the second sentence when filled, against the reviewed tree (the files present at `4d0ff8a2`): an
output that prints a figure or state different from the reviewed one carries another row's change and is REVIEWED-INPUT CHANGED (set
30's `RESULT.md` lines 114 to 115 apply the sentence to a regeneration the same way).

**The classes (W39's fixed set; a commit carrying more than one kind of change carries each, the first the most material).**

- `REVIEWED-INPUT CHANGED`: set 30's rule as quoted above, its second sentence read as ruled (reading A); a file of the delta whose
  changed lines are all digests is `DIGEST RE-PIN`.
- `RECORD TEXT`: prose, citations, quotes, patch rows, notes, an apply script's carried text; no figure, state or limit of a reviewed
  file, and no other row's change carried into a file of the reviewed tree.
- `GENERATOR DATA (text)`: a generator's printed text or data rows changed without a computed figure changing (here: the input lines the
  converted generators print for their texts).
- `TEST`: tests and their expectations only.
- `DIGEST RE-PIN`: outputs regenerated and pins moved, digest lines.
- `MERGE`: a merge commit (none on these branches).
- `TOOLING`: the logic of a tool, of a record's generator or of an apply script (an input route, a refusal condition, a packer's
  threshold). The committed extractions ride with the generator commits that read them (a SESSION decision, W44: they are the inputs of
  the changed route, byte-identical to this host's pdftotext by W36's check 2; reversed by giving them a row class of their own).

## 1. The table, branch by branch, oldest first

| # | sha (short / full) | date and time (Europe/Amsterdam) | subject | branch (author, queue item) | files changed (count: folders) | class | reason (what was read) |
|---|---|---|---|---|---|---|---|
| 1 | `b03c5570` / `b03c5570d9c3566739b9911b610d1e76f1d5a293` | 2026-10-06 12:37:26 | chore(records): checkpoint W34 from aed4bd23: the pdftotext inventory (63 scripts classified), the helper that returns a maker's PDF text as a committed verbatim input and refuses when it is absent, the re-take script and the regression test_pdftext_input (fixtures green; the tree predicates wait for the conversions) [MESHSAT-1357] | fnd/w34pdftext (W34, Q-50) | 4: v2/docs/records/_lib/ (3), v2/ecad/tools/ (1) | TOOLING + RECORD TEXT + TEST | the helper `v2/docs/records/_lib/pdftext.py` (returns a maker's PDF text as a committed verbatim input and refuses when it is absent) and the re-take script `_lib/retake_pdf_text.py` (writes a text and its sidecar), both new; the inventory `_lib/PDFTEXT-INVENTORY.md` (63 scripts classified) and a new `test_pdftext_input.py`; no generator, output or file cx46 read |
| 2 | `e50fa0e9` / `e50fa0e9cd0dbd0fc3a23af8fc3ab67606126ff1` | 2026-10-06 12:41:26 | chore(records): checkpoint W34: records efuse, l5r2 and l8r2 (drafts, gndret, p0) read their makers' PDF text through the helper; 24 committed extractions beside their PDFs, two held-back ones under held/ (ignored); each run with pdftotext denied made no call and printed its committed output plus the text input lines [MESHSAT-1357] | fnd/w34pdftext (W34) | 53: v2/docs/records/efuse/ (1), v2/docs/records/l5r2/ (1), v2/docs/records/l8r2/ (3), v2/vendor/ (48) | TOOLING + GENERATOR DATA (text) | records efuse, l5r2 and l8r2 (drafts, gndret, p0) read their makers' PDF text through the helper: each extraction call replaced by the helper's call on the same PDF with the same options, for example `aed4bd23:v2/docs/records/l8r2/l8r2_gndret.py:158` `r = subprocess.run(["pdftotext", "-layout", P(SHEETS[key]), "-"], capture_output=True, check=True)` now `e50fa0e9:v2/docs/records/l8r2/l8r2_gndret.py:172` `_PDF[key] = PT.pdf_text(ROOT, SHEETS[key], ["-layout"], PDFTEXT, "v2/docs/records/l8r2")`; each generator's input list gains its texts (printed as input lines when the output is regenerated); 24 committed extractions with their sidecars (48 files under `v2/vendor/*/pdftext/`); no figure, state word, composition, case, requirement or limit in the diff, so not REVIEWED-INPUT CHANGED under the rule stated above; no output committed (the integration regenerates them, rows 15 to 17); reviewed files it touches (2): `l8r2_gndret.py`, `l8r2_p0.py`; UNREVIEWED since cx46 |
| 3 | `acdcb22e` / `acdcb22e5a7dc59be72c85403ae371040831600a` | 2026-10-06 12:45:40 | chore(records): checkpoint W34: records l4e13 (its own pages), l4e11 and l4e9 read their makers' PDF text through the helper, only the extraction call sites and the input lines changed; their committed extractions beside the PDFs, held-back ones under held/; with pdftotext denied l4e11 and l4e9 made no call and printed their committed outputs plus the text lines (l4e13 the same with the replay's calls left); test_pdftext_input 6 passed [MESHSAT-1357] | fnd/w34pdftext (W34) | 139: v2/docs/records/l4e11/ (1), v2/docs/records/l4e13/ (1), v2/docs/records/l4e9/ (1), v2/vendor/ (136) | TOOLING + GENERATOR DATA (text) | records l4e13 (its own pages), l4e11 and l4e9 read their makers' PDF text through the helper, for example `aed4bd23:v2/docs/records/l4e9/l4e9_power_path.py:777` `t = subprocess.run(["pdftotext", os.path.join(TOP, PINS["millmax"][0]), "-"], capture_output=True).stdout.decode()` now `acdcb22e:v2/docs/records/l4e9/l4e9_power_path.py:802` `t = PT.pdf_text(TOP, PINS["millmax"][0], [], PDFTEXT, "v2/docs/records/l4e9")` and `aed4bd23:v2/docs/records/l4e11/l4e11_power.py:650` `ks = flat(subprocess.run(["pdftotext", read("keystone"), "-"]` now `acdcb22e:v2/docs/records/l4e11/l4e11_power.py:712` `ks = flat(PT.pdf_text(TOP, PINS["keystone"][0], [], PDFTEXT, "v2/docs/records/l4e11"))`; the pdftocairo calls of both stay (W36's F-P1); 68 committed extractions with their sidecars (136 files); no figure, state word, composition, case, requirement or limit in the diff; no output committed; reviewed files it touches (2): `l4e11_power.py`, `l4e9_power_path.py`; UNREVIEWED since cx46 |
| 4 | `4f66a0f1` / `4f66a0f188ef5c8ced1538734fc26ee7eae15cab` | 2026-10-06 12:53:32 | chore(records): checkpoint W34: the remaining run-time callers outside the l4e7 KEY's group and the accepted Layer 3 records read their makers' PDF text through the helper (l4e10, l4e12, l7pwr, l7r2, l8p drafts and guard, l9pwr, l9stk copper and protection, seven l9t5 modules); each run with pdftotext denied made no call and printed its committed output plus the text input lines and the moved source pins; the helper gains merge and declared_in; test_pdftext_input covers 24 generators, 6 passed [MESHSAT-1357] | fnd/w34pdftext (W34) | 140: v2/docs/records/_lib/ (1), v2/docs/records/l4e10/ (1), v2/docs/records/l4e12/ (1), v2/docs/records/l7pwr/ (1), v2/docs/records/l7r2/ (1), v2/docs/records/l8p/ (2), v2/docs/records/l9pwr/ (1), v2/docs/records/l9stk/ (2), v2/docs/records/l9t5/ (7), v2/ecad/tools/ (1), v2/vendor/ (122) | TOOLING + GENERATOR DATA (text) + TEST | sixteen more generators read their makers' PDF text through the helper (records l4e10, l4e12, l7pwr, l7r2, l8p drafts and guard, l9pwr, l9stk copper and protection, seven l9t5 modules), for example `aed4bd23:v2/docs/records/l9t5/l9t5_t10.py:95` `r = subprocess.run(["pdftotext", "-layout", os.path.join(ROOT, SHEETS[key]), "-"], capture_output=True, check=True)` now `4f66a0f1:v2/docs/records/l9t5/l9t5_t10.py:112` `_PDF[key] = PDFT.pdf_text(ROOT, SHEETS[key], ["-layout"], PDFTEXT, "v2/docs/records/l9t5")`; the helper gains `merge` and `declared_in`; 61 committed extractions with their sidecars (122 files); `test_pdftext_input.py` over 24 generators; no figure, state word, composition, case, requirement or limit in the diff; no output committed; reviewed files it touches (3): `l9t5_f01.py`, `l9t5_paloop.py`, `l9t5_t10.py`; UNREVIEWED since cx46 |
| 5 | `6dc69ad2` / `6dc69ad2b8e774f281b0a94ad6667f5184ff731f` | 2026-10-06 13:02:50 | fix(records): the makers' PDF text as a committed verbatim input: 25 record generators read it through v2/docs/records/_lib/pdftext.py instead of running pdftotext (l4e8's own pages last), the inventory's final classification and the set 32 adoption steps, test_pdftext_input over 25 generators, 6 passed [MESHSAT-1357] | fnd/w34pdftext (W34) | 40: v2/docs/records/_lib/ (2), v2/docs/records/l4e8/ (1), v2/ecad/tools/ (1), v2/vendor/ (36) | TOOLING + GENERATOR DATA (text) + RECORD TEXT + TEST | record l4e8's `ripple_dense.py` reads its makers' PDF text through the helper (the 25th generator); 18 committed extractions with their sidecars (36 files); the inventory's final classification and its set 32 adoption steps; `test_pdftext_input.py` over 25 generators; no file cx46 read; the commit W36 read (section 2 of RESULT.md) |
| 6 | `1d3dc437` / `1d3dc43715740036846421f4e819a011bf634a41` | 2026-10-06 15:37:39 | chore(records): checkpoint W37 on W36's review of W34: the inventory states what still reads the host's poppler (F-P1), each held sheet's refusal names the fetch script that fetches it (pdftext.FETCH, F-P2), the re-take checks .gitignore before writing, test_pdftext_input runs five converted generators with the tools refused or logged, widens predicate (d) with KNOWN callers, and covers CHANGED, the not-ignored refusal and orphan texts (F-R1, F-R2), 11 passed [MESHSAT-1357] | fnd/w34pdftext (W37, Q-56) | 4: v2/docs/records/_lib/ (3), v2/ecad/tools/ (1) | TOOLING + RECORD TEXT + TEST | W36's F-P1 (the inventory states what still reads the host's poppler), F-P2 (`pdftext.FETCH`: a held sheet's refusal names the script that fetches it; the re-take checks `.gitignore` before writing), F-R1 and F-R2 (`test_pdftext_input.py` runs converted generators with pdftotext and pdftocairo refused or logged, widens predicate (d), covers the CHANGED path, the not-ignored refusal and orphan texts); no generator, output or file cx46 read |
| 7 | `82e1e1c6` / `82e1e1c64e2966be78874219903b21027f2af4db` | 2026-10-06 15:39:19 | docs(handover): the supplier page's reproduction steps gain the held-back text's re-take (fetch by the script that fetches the sheet, retake_pdf_text.py on pdftotext 22.12.0 with poppler-data, then the record's script; the outputs pin each text's sha256, so another poppler shows as a refusal), W36's F-K5; main's test_entrypage and test_w30entry 25 passed on main with this page and the helper [MESHSAT-1357] | fnd/w34pdftext (W37) | 1: v2/docs/handover/supplier/ (1) | RECORD TEXT | W36's F-K5: `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md` section 7 item 2 gains the held-back text's re-take step (+8 -1); not a file cx46 read |
| 8 | `886704ea` / `886704ea78f9c93b3b06f52e2db27f1de87a9702` | 2026-10-06 15:42:51 | chore(records): checkpoint W37: the inventory records the fetch route per held sheet (43 sheets, every one with a route; efuse and l4e8 have no fetch script of their own, their sheets come from l4e11's and w5identc's), l4e12's pin count line (F-C1), the integration order restated upstream first with L4E8_OUT's re-pin and the post-re-key dependents (F-K1 to F-K3), and section 7 listing W37's changes [MESHSAT-1357] | fnd/w34pdftext (W37) | 1: v2/docs/records/_lib/ (1) | RECORD TEXT | the inventory (+69 -21): the fetch route per held sheet (F-P2), l4e12's count line stated (F-C1), the integration order restated upstream first with `L4E8_OUT`'s re-pin and the post-re-key dependents (F-K1 to F-K3), section 7 listing W37's changes; no generator |
| 9 | `81ecc1f2` / `81ecc1f2a32478bd92239d6c85966acde56d8cee` | 2026-10-06 16:23:34 | chore(records): checkpoint W42: the citations into the edited generators re-pointed in the live pages (the annex's five E11PY citations moved by 62 lines, the ledger's PAL range by 15; the cx46 quotations kept as bound to 4d0ff8a2), test_w3annex's four anchor keys restated with their basis, 10 passed [MESHSAT-1357] | fnd/w34pdftext (W42, Q-61) | 3: v2/docs/records/l4close/ (2), v2/ecad/tools/ (1) | RECORD TEXT + TEST | W36's F-K4 in two live pages: the annex's five `[E11PY:n]` citations moved by 62 lines, for example `886704ea:v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:183` `[E11PY:5957]` now `81ecc1f2:v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:183` `[E11PY:6019]`, and the ledger's `886704ea:v2/docs/records/l4close/REMAINING-ENGINEERING.md:169` `[PAL:186-255]` now `81ecc1f2:v2/docs/records/l4close/REMAINING-ENGINEERING.md:169` `[PAL:201-270]`; each page's citation-form paragraph gains a set 32 sentence inside its line; `test_w3annex.py`'s four anchor keys restated; the cited words, figures and states unchanged; reviewed files it touches (1): `SUPPLIER-VALIDATION-ANNEX-2026-10-05.md`; UNREVIEWED since cx46 |
| 10 | `5b3153aa` / `5b3153aa4136f08ab186a2b5da53c1c4f0c3ecac` | 2026-10-06 16:28:58 | docs(records): set 32's moved line citations re-taken in the live pages (the annex's five E11PY and the ledger's PAL range, the cx46 quotations and the commit-bound citations kept), the supplier page's section 0e pointer to the held-back text's re-take as an apply script for the integrated tree, TP-E11-29's row left with its reason, test_w42cite 8 passed [MESHSAT-1357] | fnd/w34pdftext (W42) | 3: v2/docs/records/w42cite/ (2), v2/ecad/tools/ (1) | RECORD TEXT + TOOLING + TEST | `v2/docs/records/w42cite/README.md` (the method, the six re-pointed citations, what is left: TP-E11-29's two prose citations as a row for the coordinator, the citations into outputs owed after the regeneration), `apply_supplier_0e_pointer.py` (the supplier page's section 0e sentence, applied once on the integrated tree: the section exists on main only) and a new `test_w42cite.py`; no file cx46 read |
| 11 | `dabfe4ca` / `dabfe4ca04095b8818f6c32961540fd3a84b8010` | 2026-10-06 15:54:30 | chore(handover): Q-53, the handover ZIP's cap raised to 104,857,600 bytes (100 MiB) with its reason in pack.yaml, the comments quoting the old cap dated as history, and a test of the cap and of the estimate's positive margin at the tree [MESHSAT-1357] | fnd/s32small (W40, Q-59 (Q-53)) | 2: v2/docs/handover/ (1), v2/ecad/tools/ (1) | TOOLING + RECORD TEXT + TEST | the handover packer's refusal threshold: `eff28be3:v2/docs/handover/pack.yaml:21` `max_zip_bytes: 52428800` now `dabfe4ca:v2/docs/handover/pack.yaml:33` `max_zip_bytes: 104857600`, the coordinator's reason in the comment above it, three comments quoting the old cap dated as history; a new test of the cap and of the estimate's positive margin in `test_handover_pack.py`; a packaging limit, not a requirement or limit of the design; not a file cx46 read |
| 12 | `a7a485ab` / `a7a485abf19875055c60f7438e8d3fe24cdeb344` | 2026-10-06 16:15:55 | chore(records): Q-55 for set 32, V-E16's row 3 takes N1a's annotation as the register's R-176 row 3 carries it, delivered as apply_q55_ve16.py for the merged tree (with test_w8l5's tree check and test_l5pwr's L5-F09 d reading), and the record's README with Q-53's reading of the estimator [MESHSAT-1357] | fnd/s32small (W40, Q-59 (Q-55)) | 2: v2/docs/records/s32small/ (2) | RECORD TEXT + TOOLING | `v2/docs/records/s32small/apply_q55_ve16.py` (241 lines) carries N1a's annotation into V-E16 row 3 of `HW-FW-CONTRACT.md` as the register's R-176 row 3 carries it, with `test_w8l5.py`'s tree check and `test_l5pwr.py`'s L5-F09 d reading, for set 32's merged tree (nothing applied on this branch: main lacks the files' set 31 state); the record's README (88 lines) with Q-53's estimator readings; `HW-FW-CONTRACT.md` is not a file cx46 read; once applied it moves `l4e11_power.out` (a file cx46 read) through the `hwfw` pin, which is the integration's row |
| 13 | `44891f15` / `44891f15efd0181ecae64d10a6230c7959b0b23c` | 2026-10-06 16:51:53 | chore(records): checkpoint, Q-65 for set 32, Q-55's change record row in HW-FW-CONTRACT.md and the register's annotated U5 line as TP-SOLAR.md's own quote, as edits 5 and 6 of apply_q55_ve16.py with test_w8l5's check of both [MESHSAT-1357] | fnd/s32small (W47, Q-65) | 2: v2/docs/records/s32small/ (2) | RECORD TEXT + TOOLING | `v2/docs/records/s32small/apply_q55_ve16.py` gains edits 5 and 6 (+130 -12): one change-record row for Q-55 appended in W8's form to `HW-FW-CONTRACT.md` after the V-E16 edit, and the register's annotated U5 line entering `TP-SOLAR.md` beside line 297 as its own text quote with a dated lead-in (the quote of record l4e7's page already there stays verbatim), with `test_w8l5.py`'s check of both; the README (+49 -3); nothing applied on this branch; neither page is a file cx46 read; `TP-SOLAR.md` is pinned by `tp_check.out`, which the chain regenerates |
| 14 | `7b7219a7` / `7b7219a7d0a695b6b866435116905964a68f5578` | 2026-10-06 16:55:09 | chore(records): Q-65 checked on a scratch clone of 3057ae43 with fnd/s32small merged, the results and set 32's added step (regenerate tp_check.out) in record s32small's README [MESHSAT-1357] | fnd/s32small (W47) | 1: v2/docs/records/s32small/ (1) | RECORD TEXT | the README (+32 -1): the script checked on a scratch clone of `3057ae43` with the branch merged (it applies once, to four files; a second run exits 3; a half-applied tree and the branch's own tree are refused), the test counts before and after the apply as the commit message gives them, and set 32's added step (regenerate `tp_check.out`); not a file cx46 read |
| 15 | `__GATE__` | not determined | the integration's commits on set 32's lineage: the merges of fnd/w34pdftext (one conflict predicted, the annex's line 136) and fnd/s32small onto `__S31_PROMOTED__`, the commit of the converged outputs and of the inputs the chain changes (Q-55's three files, the supplier page's 0e sentence, TP-E11-29's two re-cites, the four typed pins, `L4E8_OUT`), the re-take of the citations into outputs, the merge of this record's branch | set 32's integration branch (the coordinator) | not determined | not determined | filled from git and the chain's log at the adoption; one row per commit, classed under the second sentence when filled (a regenerated output carrying a row's change into a file of the reviewed tree is REVIEWED-INPUT CHANGED, reading A) |
| 16 | `__REKEY__` | not determined | the re-key's commit of record l4e7's results cache, after the converged commit and its independent read | set 32's integration branch (the coordinator) | not determined | not determined | filled from git at the adoption; classed under the second sentence when filled |
| 17 | `__CANDIDATE__` | not determined | set 32's candidate commit (the re-key's dependents, the evidence install, `candidate_guard record`) | set 32's integration branch (the coordinator) | not determined | not determined | filled from git at the adoption; classed under the second sentence when filled |

## 2. Summary

**Counts per class** over the 14 commits of the two ranges (the first class of each row; each row counted once; the three placeholder
rows not counted; recomputed by `test_res32.py` from the table):

| Class | Rows (first class) | Rows carrying it at all |
|---|---|---|
| `REVIEWED-INPUT CHANGED` | 0 | 0 |
| `RECORD TEXT` | 7 | 11 |
| `GENERATOR DATA (text)` | 0 | 4 |
| `TEST` | 0 | 7 |
| `DIGEST RE-PIN` | 0 | 0 |
| `MERGE` | 0 | 0 |
| `TOOLING` | 7 | 10 |
| total | 14 | |

**Per branch** (first class): fnd/w34pdftext, 10 rows: RECORD TEXT 4, TOOLING 6; fnd/s32small, 4 rows: RECORD TEXT 3, TOOLING 1.

**The rows that touch a file cx46 read: 4, all UNREVIEWED since cx46.** In table order: `e50fa0e9` (2), `acdcb22e` (3), `4f66a0f1` (4),
`81ecc1f2` (9); 8 files among them, each named in its row.

**The statement RESULT.md binds** (every number from the table above):

> Set 32's two branches carry 14 commits over their bases (fnd/w34pdftext 10 over `aed4bd23`, fnd/s32small 4 over `eff28be3`, no
> merge). None is classed REVIEWED-INPUT CHANGED: 7 are TOOLING first (the PDF-text helper, the re-take script, 25 generators' input
> route with 171 committed extractions, W37's regression and fetch map, the handover packer's cap) and 7 RECORD TEXT first (the
> inventory, the supplier page's re-take step, the moved citations, the apply scripts' carried text and its check). 4 of the 14 touch a
> file cx46 read
> (8 files: seven generators' input route and the annex's citation line numbers); each is UNREVIEWED since cx46, never credited. The
> outputs those generators write, several of them files cx46 read, move only at the integration, whose rows are placeholders until the
> adoption. Passing the suite transfers no engineering verdict to any row.

**Not determined here:**

- The rows after the two tips (placeholder rows 15 to 17, and any commit a branch gains after `5b3153aa` or `7b7219a7`); this table's
  counts are over the 14 rows only.
- Whether a second reader classes the same rows: no independent table of these ranges exists when this one is written (set 32's lineage
  read is a later queue item).
- The 342 vendor files (171 texts, 171 sidecars) were counted and grouped, not read line by line; W36 compared all of them with this
  host's pdftotext (RESULT.md, section 2).
