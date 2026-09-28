# Second check of stream d6rel, the follow-up at 3d7c98d2 (AI review), 28 September 2026, 20:09 to 20:30 CEST

**This is an AI review, never a qualified engineering review.** Prototype design: no board has been built, ordered or measured; every number below is a reading of a netlist, a board file, a maker's document or a fixture. The worktree `/home/claude-runner/worktrees/meshsat-fieldkit/d6rel` was only read (its HEAD is `fnd/d6rel` at `3d7c98d2`, tracked status clean). Everything I ran, ran in scratch clones under `/home/claude-runner/worktrees/meshsat-fieldkit/_scratch/chk-d6rel-2/`; no gate, verdict writer, `rules_status.py` or `rules_render.py` ran in any tree. I authored nothing of what is checked.

What was checked: the five commits `7af28903..3d7c98d2` (3bbc01df, 59987cb9, efd6899a, 7eb03d7a, 3d7c98d2). The first check (`main:v2/docs/records/int7/checks/d6rel-check-1.md`) was written at `efd6899a`, the third of the five, so the author's answer to it is `7eb03d7a` (the tool, the list and the tests) and `3d7c98d2` (the record and the apply scripts). I read the whole range as asked. `main` is `6b419b02`; `fnd/int8` was `475becd7` when I cloned (20:10 CEST) and had moved to a later tip by the end (the handover checkpoint `38205171` is already in its history; nothing of that touches this stream's files).

```
mergeable: yes
```

## 1. The merge as it will happen

`git clone --shared <main checkout> view`, `git checkout -b chk origin/fnd/int8` (475becd7), `git merge --no-ff origin/fnd/d6rel`. Merge base `73ae2f21`.

**One conflict, mechanical: `v2/vendor/sources.txt`**, a single append-append hunk at the end of the file. The int8 side appended lines 349 to 374 (the QMX tray materials, the QRP Labs pages, the MIL-STD-810H transcription, the fourteen withheld IBIS model lines of stream w5si2); the d6rel side appended 16 lines (a blank, a header comment, the seven documents it fetched, a blank, a header comment, the five provenance lines for documents held before the stream). No line is shared. Resolution in the clone: delete the three marker lines, keep both blocks in the order int8 then d6rel; the result is 389 lines (base 348, plus 25, plus 16), every non-blank line of both parents present, no line of either parent lost (checked with `comm` on the sorted files; the only "extra" lines are the second copies of blank lines and of a lone `#` comment line that both blocks carry). Committed in the clone as `1adb3c80` (committer instant `2026-09-28T20:10:59+02:00`).

`v2/vendor/vendor-status.txt` is not touched by the branch (no conflict). The branch touches no shared file: `git diff --name-only main...fnd/d6rel` has no `pcb_requirements.yaml`, `pcb_decisions.yaml`, `pcb_interfaces.yaml`, `pcb_rules_coverage.yaml`, `pcb_board_holds.yaml`, `rules_status.py`, `EXECUTION-PLAN.md`, handover page or `CURRENT-EVIDENCE.md`, so the registry's open_items and the trace page do not conflict with this stream. The 25 files of the branch: `v2/docs/records/d6rel/` (12 files), `v2/ecad/tools/{reliability.py, wear_inventory.py, pcb_reliability.yaml}`, the two test files, seven vendor documents, `sources.txt`.

## 2. The repair itself, reproduced

**(a) Tests.** `env -C view/v2/ecad/tools PYTHONDONTWRITEBYTECODE=1 python3 tests/run.py reliability` (the substring matches both test files, `test_reliability.py` with 50 tests and `test_reliability_inventory.py` with 10; no other file's name carries reliability or wear):

```
tests: test_reliability_inventory.t_the_reference_class_is_the_letters_a_reference_begins_with PASS
tests: test_reliability_inventory.t_the_rules_are_checked_before_they_are_used PASS
tests: test_reliability_inventory.t_what_cannot_be_read_says_why PASS
tests: 60 passed, 0 failed, 0 skipped
real 0m7.698s
```

Four tests are new since the first check: `t_an_open_item_that_names_no_board_and_no_class_refuses_the_list` (P15), `t_an_open_item_that_names_the_board_holds_it`, `t_a_jack_drawn_as_an_ic_on_a_soldered_land_is_found_by_the_words` (P14), `t_every_open_item_of_the_committed_list_holds_a_reading_and_every_board_says_what_holds_it` (the real-tree test; its line 930 also refuses a `w5ident` citation in the list's data, m6). `t_a_class_with_no_cycle_figure_must_say_why` (`test_reliability.py:146-186`) now asserts INCONCLUSIVE, `figures == {none_published: 1}`, one `undecided` entry naming the documents read, `classes_undecided == 1` in the verdict counts, and `held_by == ["O-1"]` when the class names an open item.

**(b) The four-case matrix**, run by me with `matrix.py` (TMPDIR in scratch, VERDICT_DIR set by the script to the fixture's own `out/`):

* repaired tool (`view/v2/ecad/tools/reliability.py`, sha256/16 `c50f2b8b35d1d57b`, list `40f2a98323b1f9ce`): case 1 PASS exit 0, case 2 FAIL exit 1, case 3 FAIL exit 1, case 4 INCONCLUSIVE exit 3; `the matrix: 4 of 4 case(s) as wanted, 0 not`, exit 0.
* unrepaired tool of main (`git show main:v2/ecad/tools/reliability.py`, sha256/16 `71d0872195905c9d`, identical to `73ae2f21`'s; main's list `fbf56eb06df1d007` beside it): cases 1 and 2 as wanted; **case 3 PASS exit 0 (wanted FAIL)** and **case 4 PASS exit 0 (wanted INCONCLUSIVE)**; `the matrix: 2 of 4 case(s) as wanted, 2 not`, exit 1.

The stream's records `matrix-on-repaired-tool.txt` and `matrix-on-unrepaired-tool.txt` say the same, with the same shas.

**(c) The binding.** A scratch `ecad/pcb-c-display-c8/out/pcb-c-display.net` copied from the merged tree, the repaired tool run with `--ecad <scratch> --board c --vendor view/v2/vendor` and `VERDICT_DIR` in scratch:

* unchanged copy: INCONCLUSIVE (held by REL-O-04, 05, 07, 08), `per_board.c.bound: true`, artefact `3fddbb3edcd4248a`, `missing_input: None`.
* one byte in a sheet comment (`Phase C24 schemat...`) and, separately, one byte in the `(date ...)` string: INCONCLUSIVE, `bound: false`, `missing_input` = "board C's declaration was written against the netlist of sha256 3fddbb3edcd4248a and the declared phase's netlist ... reads 3647bb27470dbcee: its components and nets are the same (a re-export of the same design): read the values against the list and re-pin it (reliability.py --pins)".
* one byte in the value of `J_EPD` (`Hirose` to `Xirose`): INCONCLUSIVE, `bound: false`, `missing_input` = "... reads b807339f4f314cf0: its components or nets differ, so the design changed: re-declare the list against it and re-pin".

No run printed PASS. The mismatch is named with both shas in every case.

**(d) The population.** My own probe (`probe61.py`, an S-expression read through `wear_inventory.read_netlist` of the six declared-phase netlists, the OLD twelve-word expression with the OLD `NOT_WEAR_PREFIX`, and the OLD list's class `refs` patterns from `git show main:v2/ecad/tools/pcb_reliability.yaml`): parts whose reference begins J, BT, H, MP, W, SW, X or P and are in neither the words nor an old class: **A 18, B 18, C 12, D 0, E 11, P 2, total 61**, the record's count exactly (README section 1). How the repaired tool disposes those 61 (`probe61b.py`, `reliability.judge()` read only): 28 in classes with a cited figure (A's dock spring pins 100,000 and `J_DOCK` 50,000; B's `J_ETH` 750 and `J_SIM1/2` 5,000; C's `J_EPD` 20 and the seven switches 25,000 to 200,000), 24 owed under an open item (`J_PRE1` REL-O-01; B's lead and bench headers and E's lead headers REL-O-02; C's headset jacks REL-O-05), 9 not mated (C's and E's soldered lead lands, P's `W_BN`/`W_BP` with their measure owed under REL-O-11). None of the 61 is in a `none_published` class. The tool's per-board totals equal the record's table: candidates 82/155/74/40/35/17/26 = 429, classed 195, excluded 234, refused 0, every board INCONCLUSIVE with the `held_by` of README section 5. My read-only run left the clone's tracked status clean.

The list, parsed by me: 58 classes, 24 cited, 16 `none_published` (every one naming REL-O-12), 8 `not_mated`, 10 `owed`; 4 measures owed; 15 exclusions; 30 distinct documents; 13 open items. README section 4 says 24/16/8/10 and 4: equal.

Sampled maker documents, opened at the cited page with `pdftotext` (sha256/16 of the held file first):

| Document | Cited | Read at the cited page |
|---|---|---|
| `rf/radiall-R222M00720-tds.pdf` `849a5fd1a4084b6b` | p2, 100, Issue 1107 B | `Mating life 100 Cycles mini`, `Issue : 1107 B` |
| `connectors/wurth-wr-bhd-box-header-61202621621.pdf` `38509e478ba394d0` | p2, 30, 002.001 2026-08-30 | `Durability 30 Mating cycles`, `002.001 2026-08-30` |
| `hirose/hirose-fh34-series-ffc-connectors.pdf` `bcd77fb04a18033d` | p4, 20 | `Mating Durability ... 20 times` |
| `connectors/gct-sim8060-nano-sim-socket.pdf` `6f2c1c6cccd7b02c` | p1, 5,000, A 6th September 2018 | `Durability : 5,000 cycles`, `6th September 2018` |
| `battery/amass-xt60-spec-tme.pdf` `c2cbb5962c1f37da` | p2, 1000, V1.2 | `USE TIMES 1000 TIMES`, `V1.2` |
| `omron/omron-g6k-signal-relay.pdf` `25d2046127b3ffa7` | p3, 100,000 | `Electrical 100,000 operations min.` |
| `m2/te-2199119-m2-b-key.pdf` `d8f58c5892aec2ef` | p6, 60 | `Durability 60 Cycles` |
| `hirose/hirose-ufl-series-catalogue-2009-02-digikey-copy.pdf` | p2, 30 | `5. Durability ... 30 cycles` |
| `connectors/amphenol-rjhse5380-rj45-jack.pdf` | p2, 750 | `Durability: 750 mating and unmating cycles` |
| `cm5/amphenol-10164227-bergstak-0.40mm-product-sheet.pdf` | p2, 30 | `Durability: 30 cycles` |
| `connectors/molex-2086581001-part-page-wayback-20251116.html` | JSON-LD, 10000 | the page's one `application/ld+json` block: `Durability Mating Cycles Max = 10000` (parsed with `json`) |
| `connectors/hro-type-c-31-m-12.pdf` | drawing note 3-3, 10000 | rendered at 110 dpi and read: `3-3.DURABILITY: 10000 CYCLES`, part `TYPE-C-31-M-12`, rev A, drawn 2020.12.08 |

The no-figure claims, sampled: the JST VH, PH, XH and SH catalogues and JST's handling precautions carry no line with "cycle" or "durab" (the VH catalogue's two "mating"/"insertion" hits are "Mating style" and "secure insertion and"); Keystone M65 page 42's one hit is "Low insertion force" (the 3568 holder), page 9 (the 3034 retainer) has none, its slug line reads `M65.1 S1p9r1 9/29/15` as cited.

**(e) The decision the first check asked for (m1).** The author decided at the class level: a `none_published` class is UNDECIDED and holds its board INCONCLUSIVE, named, exactly as an owed figure does (`reliability.py:263-278`, the comment names the decision, its date, the integrator as decider and the H3 review's condition; the list's header `pcb_reliability.yaml` lines 32 to 35 says the same; README section 5 and section 11 row 1 state it with authority SESSION, the reason "a statement about a document is not a figure", and the reversal "restore the PASS in reliability.py and the test"). The tool does what the record says: `judge_board` appends an `undecided` sentence per such class, the sentence names the documents that were read and the open item's next action, `why_not.extend(out["undecided"])` at `:436` makes the board INCONCLUSIVE, and `held_by` carries the item the class names. A board with such a class reads INCONCLUSIVE with `classes_undecided` counted in the verdict (P1 of the first check now reads INCONCLUSIVE; my run of the tree's board A: 4 of its 11 classes undecided). Why that is honest: the class is accepted as a declaration (no refusal, `refused 0`, the part is disposed), and the board is not passed on a figure nobody has; `not_mated` (a solder land, a screw joint) still holds nothing, which is right because no cycle applies to it.

Consequence stated by the author and true in the tool: with REL-O-07 `holds: all` (no expected number of mates is stated anywhere, REQ-028), **no board can read PASS on REL-001 until a service life is ruled**, whatever its classes cite. The record says so (README section 5 and the follow-up report's open items).

## 3. The two apply scripts, run on a scratch clone of the MERGED tree

Clone `apply` at the merge commit `1adb3c80` (a git checkout, so `--commit` works and `closed_by` can be checked). Log: `apply-sequence.txt`. Baseline `env -C apply/v2/ecad/tools python3 rules_lib.py requirements`: `144 requirement record(s), 0 error(s), 0 warning(s)` (the author's copy had 36 errors of its own because it lacked pages; the merged tree has none).

1. `apply_config_inputs_reliability.py --root apply`: `CONFIG_INPUTS['reliability.py'] declares the list and 30 cited document(s); pcb_board_facts.yaml is gone from it; re-parsed with ast, 24 other entries unchanged`, exit 0. Again: `REFUSED: the entry already describes the repaired tool: this script has run`, exit 2. Re-parsed by me with `ast`: 25 entries, the reliability entry declares 31 inputs, first `tools/pcb_reliability.yaml`, no `board_facts`. Precondition asserted: the old entry's exact text (as on int8), the repaired tool present (`written_against` in it, no `board_facts`), the list of the tree cited under `v2/vendor/` and every document on disk.
2. `apply_rel001_coverage.py --stage coverage`: with `--floor 2026-09-28T19:00:00` (no offset) `REFUSED ... carries no UTC offset`, exit 2; with `--floor 2026-09-28T16:46:27+02:00` `REFUSED: the floor ... is not after every reading of the unrepaired tool this tree holds` naming the seven 14:54Z readings, exit 2; with `--commit 1adb3c80`: `the floor is the committer instant of 1adb3c80: 2026-09-28T20:10:59+02:00`, `REL-001 entry replaced ... (sha256/16 d0ea449ec8909b8e -> bee04fa4ddec2cab)`, exit 0; again: `REFUSED: the REL-001 entry already carries the inventory note: this stage has run`, exit 2. Re-parsed: `evidence_not_before: {reliability: 2026-09-28T20:10:59+02:00}`, fixtures both files, maturity ENFORCED, remediation SESSION/SEQUENTIAL/4/10, the note carries "No board reads PASS." and the computed counts (429 candidates, A 82 ... P 26, 195 classed in 58 classes, 234 excluded under 15 exclusions, 0 refused). `rules_lib.py requirements` after: `0 error(s), 0 warning(s)`.
3. `--stage close-s89 --check --commit 1adb3c80` BEFORE any re-take: `REFUSED: REL-001 has not been re-taken as this closure needs` naming each board's reading as `taken 2026-09-28T14:54:5xZ, before the floor ...; carries no counts of the inventory for the board (a reading of the word-list tool?)`, exit 2.
4. Re-take per board in the clone with `env -C apply/v2/ecad/tools python3 reliability.py --board <b> --vendor apply/v2/vendor --out-dir <phase>/routed` (the box's re-take, done here on this host; it is light): every board INCONCLUSIVE of its candidate count, `writer` sha16 `c50f2b8b35d1d57b` (the merged tree's tool), `bound true`, `citations_unjudged 0`, `held_by` as the list.
5. **Probe 5a (a gap, see minor item m-1):** with the tree's `reliability.py` changed by one comment line AFTER the re-take (so the readings' `writer.sha16` no longer equals the tree's tool), `close-s89 --check` still says `the closure's conditions hold on 7 board(s)`, exit 0. The stage compares the list's sha, the floor, the artefact's sha against the declared phase's, `bound`, `citations_unjudged`, `refused`, `held_by` and the verdict, and never the reading's `writer` or `code_bundle` against the tree. Tool restored (`c50f2b8b35d1d57b`).
6. **Probe 5b (as required):** with board C's netlist changed by one byte in `J_EPD`'s value after the re-take, `close-s89 --check`: `REFUSED: a board of this tree cannot be read against the list: C: board C's declaration was written against the netlist of sha256 3fddbb3edcd4248a and the declared phase's netlist ... reads 4724bc116dd93e5d: its components or nets differ`, exit 2. Netlist restored.
7. `close-s89 --check` after the re-take: seven `check:` lines naming each board's verdict, artefact sha and `held_by`, then `the closure's conditions hold on 7 board(s); nothing was written`, exit 0. Then without `--check`: `S-89 moved to closed_items in v2/ecad/tools/pcb_requirements.yaml (closed_by commit 1adb3c80); the wait on it cited instead in REQ-022, REQ-024, REQ-026, REQ-028, REQ-064; re-parsed`, `rules_lib.py requirements: 0 error(s) before this change, 0 after, 0 new`, exit 0. Again: `REFUSED: S-89 is already in closed_items: this stage has run`, exit 2. Re-parsed: S-89 not in open_items, closed entry with keys `closed_by, closing_evidence, id, title`, REQ-024 keeps `waits_on: [S-55]`, the other four lose their `waits_on`, all five cite S-89 in `history`, no other record waits on S-89. Validator after: `0 error(s), 0 warning(s)`.

S-89 is closed by nothing else on the branch (the branch does not touch `pcb_requirements.yaml`), and the stage refuses until the re-take is in the tree. After the sequence, `git status` of the clone shows exactly: the seven `routed/reliability.verdict.json` (tracked files, so the box's re-take must be committed), `pcb_requirements.yaml`, `pcb_rules_coverage.yaml`, `rules_status.py`.

## 4. The first check's minor items, each answered

| Item | Answer, with file and line | Verified |
|---|---|---|
| m1 | class level: `reliability.py:263-278`, `:436`; `test_reliability.py:162-175`; list header lines 32-35; README sections 5 and 11 | yes, section 2(e) above; P1 shape reads INCONCLUSIVE in the test's `_cli` run |
| m2 | `check_open_items` `reliability.py:183-217` refuses an item named by no class and naming no board (P15 shape, test at `test_reliability.py` `t_an_open_item_that_names_no_board_...`); `holds` at `:177-180` and `:288-296`; REL-O-07 `holds: all`, REL-O-08 `holds: [a,b,c,d,e,p]`, REL-O-13 `holds: [a,b,d,e,p]`; the apply script's sentences computed from the list and the readings (`apply_rel001_coverage.py:146-153`, `:188-193`), no "REL-O-01 to REL-O-11" left | yes; the coverage note I obtained names each board's own items |
| m3 | open item REL-O-13 with `what`, `next_action`, `holds: [a, b, d, e, p]`; README section 4 says the population is the netlist's | yes (list); the footprint counts themselves not re-read by me |
| m4 | board B's ten bench headers are a class owed under REL-O-02 (figure) with `measure_owed: REL-O-02`, `count_expected: 10`, the decision, authority and reversal in its statement | yes; my probe shows the ten under that class |
| m5 | `WEAR = WEAR_TWELVE + jack, RJ45, plug` `reliability.py:72-79`; `T1` and `U5` excluded by name with their reason; test `t_a_jack_drawn_as_an_ic_on_a_soldered_land_is_found_by_the_words` `:636` | yes |
| m6 | REL-O-01, 02, 04 rewritten on the netlist values and `PROCUREMENT.md`/`SOURCES.yaml`; the SWD pads on their values; the real-tree test asserts no `w5ident` in the list's data (`test_reliability.py:930`) | yes: `grep w5ident` on the list's data: none |
| m7 | `revision:` on 22 citations of 17 documents; 13 documents state none (README section 8, `revision_scan.py`) | sampled: Radiall, Wurth, GCT, Amass, Hirose FH34 and U.FL, Keystone p9 slug line all read as cited |
| m8 | `apply_config_inputs_reliability.py` (run, section 3) | yes |
| m9 | (a) disclosed, README section 10; (b) PASS accepted only where the list holds the board by nothing, `apply_rel001_coverage.py:331-334`, and with REL-O-07 holding all no PASS is possible today; (c) binding read from `counts.per_board[<letter>].artefact` `:309-310, :321-322`; (d) `_floor_instant` `:90-100` refuses a floor with no offset (run); (e) `citations_unjudged != 0` refused `:324-326` and the tool declares the absent vendor library as `missing_input` `reliability.py:426-438` | yes; (e) also in the author's step 7 |
| m10 | `verify:` on the Molex and HRO citations (list diff lines 247 and 257) | both re-verified by me as the `verify:` text says |

## 5. Hygiene

`/tmp` held 20049 entries before my test run and 20157 after: **the two test files leave 108 directories per run** (`rel-` from `test_reliability.py:45` `tempfile.mkdtemp(prefix="rel-")`, 93 of them; `inv-` from `test_reliability_inventory.py:29`, 15), 2.2 MB, never removed (neither file has an `rmtree`, `TemporaryDirectory` or `atexit`; `harness.py` offers no cleanup). Before my run `/tmp` already held 1255 `rel-` and 207 `inv-` directories from the author's and the first checker's runs. It is the suite's habit rather than this stream's alone (82 of the test files call `mkdtemp`, 39 have any cleanup), but on a host whose `/tmp` carries 20,000 entries it is worth a `shutil.rmtree` in the fixture helper. `matrix.py:120` likewise leaves one `d6rel-matrix-*` directory per run. I removed the 108 my run created (`/tmp` back to 20049 of mine; the 235 entries other sessions added at 20:14 under `req-`, `si001-`, `ibis-`, `pinned-`, `evidence-` are not mine and were left alone) and ran the matrix with `TMPDIR` in my scratch.

## 6. Prose and scope

`git diff --stat main...fnd/d6rel`: 25 files, 60,201 insertions, 276 deletions (the two Wayback HTML captures are 45,800 of them). Added lines outside the vendor HTML captures: 0 em dashes, 0 en dashes (the two third-party HTML captures carry 4, in the makers' own text, not the stream's). "AI review, never a qualified review" in the README (line 8) and both apply scripts; "no board has been built" framing present; no "works", "proven" or "field deployed" claim (the one "proven" is "a substitution is a mismatch until proven", the standard's own words). The record traces H3-01 (README lines 4 to 6), **erratum h** of `RELEASE-H3.md` (line 113 there is REL-001's erratum; f is TRN-001's, H3-02; the task's "e or f" is not this stream's) and S-89. No claim of a result not obtained: every line of section 13 of the README I reproduced reads the same (60 passed; 4 of 4; 2 of 4; 429/111/318/195/234/0; the apply script's outcomes). No protection or requirement lowered: the list's corrections go towards the maker's figure (Amphenol 10164227 from 60 to 30, the JST "30 from the series specification" withdrawn to none published), REL-O-07's `holds: all` makes PASS harder, not easier. The record says what REL-001's PASS would and would not mean per board (section 5: the table of what holds each board, and the sentence "A board reads PASS only when every candidate is disposed, every class either cites its figure or mates nothing, no measure is owed and no open item names the board"), and the coverage note and closing evidence say it again in the tree's own words. Nine commits, all as `Kyriakos Papadopoulos <ncpjfuzl@mxmx.email>`, all tagged `[MESHSAT-1357]`, no `the co-author trailer (its literal name is not written in this repository)

## 7. Minor items

| id | item |
|---|---|
| m-1 | `close-s89` never compares the readings' `writer.sha16` (or `code_bundle`) with the tree's `reliability.py`: counter-example probe 5a in `apply-sequence.txt` (the tree's tool changed by a comment line after the re-take, `--check` still accepts, exit 0). It cannot admit the unrepaired tool (no `per_board`, no `candidates`) nor the intermediate tools of 59987cb9/efd6899a (no `held_by`), so the integrator's planned flow (merge, box re-take at the merged tip, close) is not exposed; a re-take taken with a tool edited between the merge and the closure would be. One guard closes it: in `retake_evidence`, `if (rec.get("writer") or {}).get("sha16") != sha16(<root>/v2/ecad/tools/reliability.py): problems.append(...)`. Until then, read each reading's `writer.sha16` against the merged tree's tool before closing (mine: all seven `c50f2b8b35d1d57b`). |
| m-2 | The two test files and `matrix.py` leave their `mkdtemp` directories behind (section 5): 108 per test run. |
| m-3 | `CONFIG_INPUTS["reliability.py"]` now names 30 vendor documents as configuration inputs of the tool, listed from the list on the day the script runs; a citation added to the list later must be added to the entry by hand (the script and README say so). Carried by the integrator. |
| m-4 | With REL-O-07 `holds: all`, no board can read PASS on REL-001 until REQ-028 rules a service life. Stated by the author; the integrator should know it before reading the readiness page. |
| m-5 | The first check's not-done items that nobody has done yet: the full suite (box), REL-O-03's two Amphenol M.2 documents, each order code's row for the series-level figures (FH34, RJHSE, U.FL). |

## 8. Not done, and why

* The full test suite: box only (owner rule on this host). Only the `reliability` subset ran here; nobody has run the suite on the branch or on a merged tree.
* `rules_status.py` and `rules_render.py` on the merged tree with the new readings: verdict and page writers, not run by a checker.
* The box re-take itself: my re-take in the scratch clone is the same tool on the same artefacts on this host; its `tools`/`runtime` provenance differs from the box's, nothing else should.
* REL-O-03's Amphenol M.2 documents; the H* footprint counts of REL-O-13; the per-order-code rows of the series-level sheets: not re-read.
* `fnd/int8` moved while I worked; the merge was tested against `475becd7`. Nothing that moved touches this stream's files, but the integrator's merge is the one that counts.

## 9. Files here

`CHECK.md` (this), `RESULT.md` (the final message), `tests-reliability.txt`, `matrix-repaired.txt`, `matrix-unrepaired.txt`, `apply-sequence.txt`, `probe61.py`, `probe61b.py`, `bind-*/run.txt` and their verdicts, `hro-1.png` (the rendered drawing), `tmp-before.txt`/`tmp-t0.txt`/`tmp-t1.txt`/`tmp-t2.txt` (the `/tmp` listings). The clones `view` and `apply` (1.5 GB each) are removed at the end; to reproduce: `git clone --shared <main checkout> view; git -C view checkout -b chk origin/fnd/int8; git -C view merge --no-ff origin/fnd/d6rel` and strip the three markers of `v2/vendor/sources.txt`.
