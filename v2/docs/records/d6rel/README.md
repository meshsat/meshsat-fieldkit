# Stream d6rel: REL-001's population, its inputs and its binding (MESHSAT-1357)

Worker stream `d6rel` of the 28 September 2026 wave, branch `fnd/d6rel` from `73ae2f21` (the set 6 candidate), never
pushed. Finding **H3-01** of the independent review of handover H3
(`v2/docs/reviews/2026-09-27-h3-independent-review.md`), registry item **S-89** (`pcb_requirements.yaml` on the
integration line `fnd/int7`), erratum **h** of `v2/docs/handover/RELEASE-H3.md`. Prototype work: no board has been
built, ordered or measured; every number below is a reading of a netlist, a board file or a maker's document. The
checks of this stream are AI review, never a qualified review.

## 1. The finding, in one paragraph

`reliability.py` (rule REL-001: what carries load and what sees cycling) took the parts it inspected from twelve
words in each part's value text. A connector whose value carried none of them left the completeness denominator in
silence: the reviewer's undeclared `RJ45 MagJack` read PASS beside one declared connector, and board A's declaration
with no netlist at all read PASS of zero. On the six netlists of the set 6 candidate, 61 parts whose reference begins
J, BT, H, MP, W, SW, X or P were in neither the word set nor any class (A 18, B 18, C 12, E 11, P 2), among them
`J_ETH` (the RJ45 jack), `J_SIM1` and `J_SIM2`, `J_EPD` (the e-paper ZIF), `J_HSJ1` and `J_HSJ2` (the headset jacks)
and the dock's spring pins. The tool also took the newest netlist by file time and recorded none, so its readings
could not be bound to a board revision.

## 2. What the stream changed

| Item of the task | Where | State |
|---|---|---|
| 1. An explicit inventory by reference class and land; every mated or wearing part of A, B, C, D, E, E5 and P in the denominator, each classed with its maker's figure cited to a held document, or UNDECIDED (INCONCLUSIVE) where the maker states none or the part is not identified | `v2/ecad/tools/wear_inventory.py` (new), `v2/ecad/tools/pcb_reliability.yaml` (rewritten, schema 2.0.0: `inventory`, `open_items`, `boards`), `v2/ecad/tools/reliability.py` | done; section 4 |
| 2. A missing netlist, or one whose sha256 is not the declared phase's, reads INCONCLUSIVE; the declared phase's netlist is bound by sha256 in the reading | `reliability.py` (`phase_artefacts` resolution, `missing_input`, `written_against`, `--pins`) | done; section 5 |
| 3. The reviewer's four-case matrix as tests on isolated fixtures, plus fixtures for a connector with no wear word, the empty netlist, a part with no cycle figure, the sha mismatch | `v2/ecad/tools/tests/test_reliability.py`, `tests/test_reliability_inventory.py` | done; section 6 |
| 4. The detector parses (S-expressions through `netlist_parts.top_level`, YAML through `yaml.safe_load`), never greps prose | `wear_inventory.py`, `reliability.py` | done |
| 5. The shared files are not edited; an apply script carries the coverage note and the closure of S-89 | `v2/docs/records/d6rel/apply_rel001_coverage.py` | written and tested on a copy of `fnd/int7`; section 8 |
| 6. This record | `v2/docs/records/d6rel/` | this file |

Files of this stream: `reliability.py`, `wear_inventory.py`, `pcb_reliability.yaml`, `tests/test_reliability.py`,
`tests/test_reliability_inventory.py`, seven documents under `v2/vendor/` with their lines in `v2/vendor/sources.txt`
(plus five provenance lines for documents held before this stream), and everything under `v2/docs/records/d6rel/`.

## 3. The reviewer's four-case matrix, before and after

Both runs by `matrix.py` through the tool's command line on fixtures outside the tree (the verdict directed there
with `VERDICT_DIR`). The unrepaired tool is `git show 73ae2f21:v2/ecad/tools/reliability.py` (sha256/16
`71d0872195905c9d`) with its list of the same commit (`fbf56eb06df1d007`); the repaired tool is this branch's.

| Case | Wanted | Unrepaired tool (`matrix-on-unrepaired-tool.txt`) | Repaired tool (`matrix-on-repaired-tool.txt`) |
|---|---|---|---|
| 1. one declared JST connector | PASS, exit 0 | PASS, exit 0 | PASS, exit 0 (1 candidate, 1 classed) |
| 2. plus an undeclared IDC header | FAIL, exit 1 | FAIL, exit 1 | FAIL, exit 1 (2 candidates, 1 refused) |
| 3. plus an undeclared `RJ45 MagJack` | FAIL, exit 1 | **PASS, exit 0** (the jack was in no denominator) | FAIL, exit 1 (2 candidates, `J_ETH` refused: a J on a connector land) |
| 4. board A's declaration, no netlist | INCONCLUSIVE, exit 3 | **PASS, exit 0** of 6 classes, 0 parts | INCONCLUSIVE, exit 3, `missing_input` names the absent netlist, no netlist recorded in `inputs` |
| The matrix | 4 of 4 | 2 of 4 (exit 1) | 4 of 4 (exit 0) |

The same four cases are `tests/test_reliability.py` `t_matrix_1_...` to `t_matrix_4_...`.

## 4. The inventory of the set 6 artefacts, before and after (`inventory-before-after.txt`)

Written by `measure_inventory.py` (read only). BEFORE is the population the inventory finds, disposed against the
classes of the 16 September list by their reference patterns alone; the old TOOL's own reading of the same netlists
was 111 covered, 0 refused (`v2/docs/records/r8int6/fix/wear-before-after.txt`). AFTER is the repaired tool with
this branch's list. A candidate is a part of a mechanical reference class (J, P, X, BT, H, MP, SW, W, WH, F, JP, K,
BZ, CAM, PAD, TP), or a part of an electrical class on a mechanical land (a connector library, a header, a holder, a
socket, a target), or one on a land declared neither mechanical nor soldered, or one with no land at all; the words
are a second net that adds and never removes.

| Board | Artefact (sha256/16) | Candidates | BEFORE classed / refused | AFTER classed / excluded / refused | Result |
|---|---|---|---|---|---|
| A | `pcb-a-power-a23/out/pcb-a-power.net` `0a2b59087bcc2678`, 612 parts | 82 | 39 / 43 | 57 / 25 / 0 | INCONCLUSIVE (REL-O-01, REL-O-02) |
| B | `pcb-b-compute-b19/out/pcb-b-compute.net` `028997a6c5e8810f`, 1280 parts | 153 | 38 / 115 | 46 / 107 / 0 | INCONCLUSIVE (REL-O-02, REL-O-03, REL-O-09) |
| C | `pcb-c-display-c8/out/pcb-c-display.net` `3fddbb3edcd4248a`, 219 parts | 74 | 9 / 65 | 24 / 50 / 0 | INCONCLUSIVE (REL-O-04, REL-O-05) |
| D | `pcb-d-aprs-d9/out/pcb-d-aprs.net` `7a2c0ac2190b141a`, 245 parts | 40 | 10 / 30 | 11 / 29 / 0 | INCONCLUSIVE (REL-O-10) |
| E | `pcb-e1-dock-e7/out/pcb-e1-dock.net` `56adc9746d61c4e0`, 189 parts | 35 | 8 / 27 | 21 / 14 / 0 | INCONCLUSIVE (REL-O-02) |
| E5 | `pcb-e5-block/pcb-e5-block.kicad_pcb` `686b29a734c55b9a`, 17 footprints | 17 | 0 / 17 | 17 / 0 / 0 | INCONCLUSIVE (REL-O-06) |
| P | `pcb-p-pack-p2/out/pcb-p-pack.net` `760ac6f74d62d194`, 85 parts | 26 | 7 / 19 | 9 / 17 / 0 | INCONCLUSIVE (REL-O-11) |
| Set | | 427 | 111 / 316 | 185 / 242 / 0 | |

The 242 exclusions, each with its reason and the land it speaks of, in the list: 219 test points (`TestPoint:*`), 6
solder jumpers, 3 resettable fuses soldered in 1812 packages (board B) and the pack's soldered self-control fuse
(board P), the three I/O controllers' programming pads (board B, no part fitted), and ten bench and commissioning
headers of board B (console, debug, breakout, jumpers the value calls not fitted in service; a session decision,
recorded in the list). Six parts carry a wear word only in the description of what they do (`U101`, `U116`, `U201`,
`U216`, `U301`, `U316`, the PCIe switches and the AND gates that enable a card socket's supply); they are named as
set aside and are not candidates: their lands are soldered packages.

The 57 classes: 24 cite the maker's figure, 16 read `none_published` (the maker's documents read give none), 8 read
`not_mated` (solder lands, screw joints: a load and a measure, no cycle), 9 read `owed` under an open item; 3 classes
owe their measure. Per board: A 11 classes (5 cited, 4 none published, 2 owed), B 14 (9, 3, 2 owed, 1 measure owed),
C 11 (5 cited, 4 not mated, 2 owed), D 7 (4, 3, 1 measure owed), E 6 (1, 3, 1 not mated, 1 owed), P 4 (0, 3, 1 not
mated, 1 measure owed), E5 4 (2 not mated, 2 owed). No board reads PASS while it owes a figure or a measure.

Corrections against the list of 16 September, each read on the netlists and the documents: board B's module
receptacles carried 60 cycles where Amphenol's product sheet of the 10164227 gives 30; board A's class "blind-mate
dock contacts" named Mill-Max pins and covered the eleven Radiall SMP-MAX receptacles while the seventeen Mill-Max
pins and the Preci-Dip connector were in no class; board D's class for "the radio module's sockets" covered two
JST-PH headers and its 500-cycle SMA class covered a U.FL socket (30) and a JST-PH header; board E5's classes named
references its board file does not carry; the JST classes carried 30 cycles "from the series specification" where
the held JST catalogues and JST's handling precautions state no mating-cycle figure; board B's class for three
soldered PCIe switches is gone (they are not candidates).

## 5. The inputs and the binding

* **A missing input is INCONCLUSIVE, never PASS.** A board of the manifest with no artefact of its declared phase, an
  artefact that cannot be read (not UTF-8, not one `(export ...)` or `(kicad_pcb ...)` expression, cut short, no
  `(components ...)` section, a component with no reference or a reference twice), an artefact with no component, a
  list that cannot be read, or a board the list declares nothing for: each reads INCONCLUSIVE with the reason in
  `missing_input` (exit 3).
* **The netlist is the declared phase's**, resolved by `phase_artefacts` the way `rules_status.candidate` resolves it
  (the manifest's stem and the routeflow profile's project directory), never the newest file by mtime; for board E5,
  which has no schematic, its declared phase's board file. The reading records it by path, sha256 and content
  identity (`regen_compare.content_hash`) beside the list's own sha256.
* **Each board's declaration is bound to the artefact it was written against** (`written_against: {sha256_16,
  content16}` under the board key, 28 September 2026, this stream's item 2). A class names a part and cites that
  part's figure, and the gate cannot read the part off the value text (that reading is the defect of H3-01), so an
  artefact of another sha is not the one the list speaks of: the reading is INCONCLUSIVE and declares it as a
  missing input, saying whether the components and nets are the same (a re-export of the same design: read the
  values against the list and re-pin) or differ (the design changed: re-declare the list against it). The
  comparison of the artefact that is there still runs, because a refusal on it is real and FAIL wins; a PASS cannot
  come of it. A declaration with no pin, or a pin that is not sixteen hex digits, reads INCONCLUSIVE the same way.
  `reliability.py --pins` prints the lines for every board of the manifest from the declared phase's artefacts and
  never writes them: re-pinning is a person reading the parts against the list.
* **The consumers** (`consumers_probe.py`, `consumers-probe.txt`, read only on in-memory records): an INCONCLUSIVE
  reading reaches `rules_status.result_for` as INCONCLUSIVE with the tool's reason (items 1, 4 and 5). But
  `rules_status._supersedes` keeps an OLDER reading that had its input in front of a NEWER one that declares its
  input absent (item 2), so a word-list PASS would stand in front of the repaired tool's INCONCLUSIVE. The floor
  that closes it is `evidence_not_before: {reliability: <instant>}` on REL-001 in `pcb_rules_coverage.yaml` (item 3,
  shown on fixtures): a reading before the instant is not current evidence whichever reading wins. The apply script
  of section 8 adds it.

## 6. The tests

`env -C <worktree>/v2/ecad/tools python3 tests/run.py reliability`, the last line on this branch at `59987cb9`:

    tests: 56 passed, 0 failed, 0 skipped

`tests/test_reliability.py` (46 tests, every fixture its own temporary tree with its own manifest, routeflow profile
directory, vendor folder and list): the four-case matrix (`t_matrix_1` to `t_matrix_4`, through `REL.main` as the
reviewer ran the command line); a connector whose value carries no wear word (`t_matrix_3`, and
`t_the_parts_the_word_list_never_found_are_in_the_inventory` on the real boards: `J_ETH`, `J_SIM1`, `J_EPD`,
`J_HSJ1`, `SW_MAIN`, `J_CN1`, `W_BN` and others, each asserted to be a part the word list does not find); the empty
netlist (`t_a_netlist_with_no_component_is_inconclusive`); a part with no cycle figure
(`t_a_class_with_no_cycle_figure_must_say_why`, `t_an_owed_figure_keeps_the_board_inconclusive_and_names_its_open_item`,
`t_nothing_mated_is_a_reason_and_needs_its_sentence`); the sha mismatch
(`t_a_declaration_written_against_another_netlist_is_inconclusive_and_says_whether_the_design_moved`: a re-export of
the same design, a changed design, a pin without a content identity), the absent pin
(`t_a_declaration_with_no_pin_is_inconclusive_and_never_pass`) and the printer
(`t_pins_prints_every_boards_line_from_the_declared_phase_and_edits_nothing`); the declared phase against the newest
file; the unreadable netlist in five shapes; the citation of every figure to a held document by sha, page and words;
disposal exactly once; a class or an exclusion that speaks of another land; and the real tree (every candidate of
every board disposed, no refusal, every board bound, INCONCLUSIVE only for owed items).
`tests/test_reliability_inventory.py` (10 tests): the reference class, the land kinds, candidacy by class, land, the
undeclared and the words, the netlist and board-file readers and what they refuse, and that every reference class the
real artefacts use is declared.

## 7. The documents cited (30, each held under `v2/vendor/`, cited by sha256/16, page and words)

Fetched by this stream (lines in `v2/vendor/sources.txt`, each with its URL, fetch time and full sha256): JST SH
catalogue (`connectors/jst-sh-catalogue.pdf`, `ea3071ca5ee5a606`), JST handling precautions
(`connectors/jst-handling-precautions-2020.pdf`, `c0f1b065990fe550`), Molex 2086581001 part page (Wayback capture of
16 November 2025, `2144edad4eb08bb3`), Keystone catalogue M65 page 9 (`keystone/M65p9.pdf`, `58aa74ce778e2b33`),
Hirose U.FL series catalogue edition 2009.2 (Digi-Key's copy, `6949727d3bc42a67`; hirose.com refused this host),
Amphenol RF 132134-11 and 132134 part pages (Wayback captures of 17 and 13 February 2026, `08292fb855ce95e8`,
`8abb34d101dcbe57`; amphenolrf.com answers 403).

Held before this stream and cited: Amphenol RF Radiall R222M00720 TDS (`849a5fd1a4084b6b`, page 2, "Mating life 100
Cycles mini"); Mill-Max 0858 product page (`7a11ec390b01e69f`, 100,000 to 1,000,000 cycles, the lower carried);
Preci-Dip 813 catalogue pages 31 to 34 (`d630c8a92e7f65fc`, 50,000); Wurth WR-BHD 61202621621, 61201021621,
61201621621 (`38509e478ba394d0`, `dbaa4765e57457ac`, `0df87add7e40d43c`, 30 each); JST VH, XH, PH catalogues
(`d51e669c597988b2`, `9426b136902f1190`, `447624f4f2f7d37c`, no figure); Keystone M65 page 42 (`caa141ea51ac68cf`, no
figure for the 3568); Amphenol 10164227 BergStak product sheet (`825f39e43efc199f`, 30); TE 2199119 M.2 guide
(`d8f58c5892aec2ef`, 60); Amphenol MDT420M02001 drawing and MDT420B01001 sheet (no figure for the part: REL-O-03);
Amphenol RJHSE5380 (`d6d6b918dec76c7b`, 750); HRO TYPE-C-31-M-12 (`6ae33d50ac478201`, 10,000); Wurth 692122030100
(`df28a01bf0fb46ac`, 5,000); GCT SIM8060 (`6f2c1c6cccd7b02c`, 5,000); Hirose FH34 (`bcd77fb04a18033d`, 20); C&K ATP19
and ATP16 (`ebf7ad2c6da083b2`, `fce6061e05364e61`, 50,000 and 200,000 make-and-break at full load, the lower figures
carried); APEM 5000 series (`87fc25f583563940`, 50,000 electrical, the lower carried); NKK M series
(`b9908fb47456b32d`, 25,000 for silver, the lowest carried); Omron G6K (`25d2046127b3ffa7`, 100,000 electrical, the
lower carried); Amass XT60 (`c2cbb5962c1f37da`, 1,000). Five of these (Hirose FH34, APEM 5000, C&K ATP16, ATP19, NKK M)
had no provenance line anywhere; this stream added one each to `v2/vendor/sources.txt` naming the commit that added
the file (and the RS-hosted URL for the APEM sheet from `v2/vendor/seals/README.md`) and the full sha256; no URL was
invented where the fetching session recorded none.

Every citation was checked on this branch: the 30 files exist, each at the sha256/16 the list cites.

## 8. What the apply script changes (the integrator runs it; this stream edits no shared file)

`apply_rel001_coverage.py --stage coverage (--commit <merge> | --floor <instant>) [--root <tree>]` replaces the
REL-001 entry of `v2/ecad/tools/pcb_rules_coverage.yaml`: `verification.fixtures` names both test files;
`evidence_not_before: {reliability: <floor>}` with its `_evidence_not_before_why`; the note says what the checker
reads now and what the set 6 artefacts read under it (the numbers of section 4); the remediation names the nine owed
figures, the three owed measures and REL-O-07 as what remains (owner SESSION, execution SEQUENTIAL, 4 to 10 hours).
**The floor is never a constant.** It is the instant the repaired tool enters the tree the readings live in: the
committer instant of the merge (`--commit`, read with git in the checkout), or an explicit `--floor`; and either
stage refuses a floor that is not after every reading of the unrepaired tool the tree holds (a reading with no
`candidates` count, read from every `reliability*.verdict.json` in the boards' evidence folders, not only the
winner). Why: the first draft of this script carried the instant of this branch's last tool commit (`59987cb9`,
16:46:27 CEST), and while this stream was running, the integration line re-took reliability with the unrepaired
tool at 16:54 CEST (`1c4235ec`, PASS on every board); under the fixed instant those seven word-list PASS readings
would have counted. The script asserts the 16 September note is present, that the new text differs, re-parses the
YAML and reads the entry back, and refuses a second run. It can run before or after the re-take with the repaired
tool: it changes no reading, it says which readings count.

`apply_rel001_coverage.py --stage close-s89 --commit <hash> [--root <tree>]` moves S-89 from `open_items` to
`closed_items` in `v2/ecad/tools/pcb_requirements.yaml` with `closed_by: commit <hash>` (the merge of this branch;
checked to be a commit the tree holds) and a `closing_evidence` that names the files, the matrix and inventory
records, and the re-take it READ from the tree: it refuses to run until every board of the manifest has a
`reliability` verdict found the way `rules_status` finds them, taken after the floor, with the list this tree holds
(by sha), bound to the declared phase's artefact (by sha), reading PASS or INCONCLUSIVE with no missing input and no
refusal. The title of S-89 is carried over unchanged; its `limits_reading` (REL-001 on every board) is not, because
no closed item of the registry carries one, and the closing evidence says what becomes of the limit (readings after
the floor are the repaired tool's and not LIMITED). The five records that wait on S-89 on the integration tip
(REQ-022, REQ-024, REQ-026, REQ-028, REQ-064) lose that wait and cite the closing in their `history`, which is the
registry's rule for a closed item and what its validator asks ("waits on S-89, which commit X closed; cite that
instead"); their result fields are not touched. The script re-parses the YAML, reads the five records and the closed
entry back, runs the tree's own validator (`python3 rules_lib.py requirements`, read only) before and after, and
restores the file if the change adds an error. Tested end to end on a copy of `fnd/int7` (`apply-script-test.txt`,
section 10).

## 9. Decisions taken by this stream (authority: SESSION, under the owner's standing rule of 26 September 2026)

| Decision | Reason | To reverse |
|---|---|---|
| The population is an inventory by reference class and land, declared as data in the list; the twelve words are a second net that adds and never removes | a completeness gate must fail towards asking for a part; a class or a land nobody declared makes the part a candidate | restore the word-list population (`git revert` of `da232ce7`); the tests of the inventory go with it |
| Each board's declaration is bound to its artefact by sha256 (`written_against`), a mismatch or an absent pin reads INCONCLUSIVE, the comparison still runs and FAIL wins | a class names a part and cites that part's figure; the gate cannot read the part off the value text; a substitution is a mismatch until proven; the same binding `reading_inputs` uses for declarations elsewhere | remove the pin block of `judge_board`, the pins from the list and the three pin tests (`59987cb9`) |
| Ten bench and commissioning headers of board B (`J_DBG?`, `J_GNSS2`, `J_ZBDBG?`, `J_IOCOFF_?`, `J_SPI3`) are excluded with their reason | not mated in the field; whether a header is fitted is a build choice not made | move them to the class of lead headers mated in service (recorded in the list) |
| Where a maker's document gives a range or several figures, the LOWEST is carried and the words say so | a bound is named a bound; never the number that passes | none needed: the words carry both figures |
| The JST classes read `none_published` with the documents read named, not "30 cycles from the series specification" | the held JST catalogues and the handling precautions state no mating-cycle figure; no number is invented | file a JST document that states one and cite it |
| Board B's CM5 receptacles carry 30 cycles (Amphenol's sheet), not 60 | the document says 30 | none |
| A figure that cannot be cited (no part picked, no document held, a plated pad) reads `owed` under an open item with a next action; the board reads INCONCLUSIVE until it is closed | UNDECIDED is never PASS | close the open item with the document and the figure |
| The evidence floor is the instant the repaired tool enters the integrated tree (the merge's committer instant), never a constant, and the script refuses a floor that is not after every reading of the unrepaired tool the tree holds | a fixed instant (this branch's last tool commit, 16:46 CEST) was overtaken within the hour by the integration line's re-take with the unrepaired tool (16:54 CEST); the property that matters is which tool wrote a reading, and that is read from the reading itself | pass `--floor` explicitly; the guard stays |
| S-89's closure requires the re-take evidence in the tree; the script refuses otherwise | the item's own closing condition names the re-take on every board | run the re-take first; the script does not bypass |
| Five previously held documents get provenance lines naming the adding commit where no URL was recorded | a held document with no provenance line is weaker than one with; no URL is invented | replace the line when the URL is found |
| `revision` is not added to each citation | the sha256 binds the exact bytes read, which is stronger than a revision string; reading each document's revision marking is a separate pass (open item below) | add `revision:` per source when read |

## 10. What was run, and the exact result lines

* `env -C <worktree>/v2/ecad/tools python3 tests/run.py reliability`: `tests: 56 passed, 0 failed, 0 skipped`.
* `python3 v2/docs/records/d6rel/matrix.py v2/ecad/tools v2/ecad/tools/reliability.py`: `the matrix: 4 of 4 case(s)
  as wanted, 0 not`, exit 0 (tool sha256/16 `a8d85b24b344e4dc`, list `f0912cb02741be21`).
* `python3 v2/docs/records/d6rel/matrix.py v2/ecad/tools $SP/old/reliability.py` (the tool of `73ae2f21`): `the
  matrix: 2 of 4 case(s) as wanted, 2 not`, exit 1.
* `python3 v2/docs/records/d6rel/measure_inventory.py v2/ecad/tools --old $SP/old`: `set 427 111 / 316 185 / 242 /
  0`, exit 0.
* `python3 v2/docs/records/d6rel/consumers_probe.py v2/ecad/tools`: five items as in `consumers-probe.txt`, exit 0.
* `python3 reliability.py --pins` (from `v2/ecad/tools`): the seven lines now in the list, exit 0.
* The apply script on a scratch copy of `fnd/int7` at `1c4235ec` (`apply-script-test.txt`, 28 September 2026 17:11
  CEST), the tip that carries the integration line's re-take of reliability with the unrepaired tool (PASS on every
  board, 16:54 CEST): stage coverage with `--floor 2026-09-28T16:46:27+02:00` `REFUSED: the floor ... is not after
  every reading of the unrepaired tool this tree holds` naming the seven readings; with `--floor
  2026-09-28T17:00:00+02:00` `REL-001 entry replaced ... re-parsed`, `exit 0`, then `REFUSED ... this stage has run`;
  stage close-s89 on the tip's own readings `REFUSED: REL-001 has not been re-taken as this closure needs` (each
  board: before the floor, no list sha, no artefact sha, no inventory counts); after a re-take with this branch's
  tool into the copy's `routed/` folders (every board INCONCLUSIVE, `refused 0`, `missing_input None`, list
  `f0912cb02741be21`, each artefact's sha the declared phase's) `S-89 moved to closed_items ... the wait on it
  cited instead in REQ-022, REQ-024, REQ-026, REQ-028, REQ-064; re-parsed`, `rules_lib.py requirements: 36 error(s)
  before this change, 36 after, 0 new`, `exit 0`; then `REFUSED: S-89 is already in closed_items`. The copy's 36
  baseline errors are all "source ... does not exist in this tree" for pages and documents the copy does not carry;
  the one validator line that names S-89 afterwards is `warn closed item S-89: git cannot say here whether commit
  59987cb9 exists`, which a checkout answers. On the real tree `--commit <merge>` gives the floor and the check of
  the commit.
* No gate, `rules_status.py` or `rules_render.py` was run in any tree; no verdict was written into the tree.

## 11. Open items left by this stream, each with its next action

| Item | Next action |
|---|---|
| REL-O-01 to REL-O-11 of `pcb_reliability.yaml` (nine owed figures, three owed measures, the service-life comparison) | each carries its `next_action` in the list; the boards read INCONCLUSIVE until closed |
| REL-001 re-taken on every board with the pinned list (the closure condition of S-89) | on the box: `gate_sweep.sh` or `retake_gate.sh` for `reliability` on every board of the manifest, after the merge; then `apply_rel001_coverage.py --stage close-s89 --commit <merge>` |
| The coverage note and floor | on the merged tree `apply_rel001_coverage.py --stage coverage --commit <merge>`, so the floor is the merge's instant; before or after the re-take with the repaired tool |
| The integration line's own re-take of REL-001 with the unrepaired tool (`1c4235ec`, 16:54 CEST, PASS on every board) is later than this branch's last tool commit, and `fnd/int7` moved to that commit while this stream ran | the script refuses a floor that is not after those seven readings; the order is coverage stage, re-take with the repaired tool, close-s89 stage; the tip's `CURRENT-EVIDENCE.md` already reports REL-001 LIMITED while S-89 stands and the integrator re-renders it |
| `revision` per cited document | read each document's own revision marking (edition, date, drawing revision) and add `revision:` to its `source` or `looked_in` entry; the sha binds the bytes meanwhile |
| The two Amphenol M.2 documents (`amphenol-mdt420m02001-m2-m-key.pdf`, `amphenol-mdt420b01001-m2-b-key.pdf`) are named in REL-O-03's statement but not cited as `looked_in`, because the class is `owed` | when GS-12-1142 or the part's own sheet is filed, cite it and carry the figure of the plating fitted |
| `RELEASE-H3.md` erratum h and `LAYER-STATUS.md`'s REL-001 rows | the integrator's pages: erratum h's "then re-taken" is met by the re-take; the rows quote the floor and the INCONCLUSIVE readings |
| The joints under heavy soldered parts (REL-O-08) | a mass-based class per board from the makers' documents; the inventory sees no mass |

## 12. Commits on `fnd/d6rel` (`git log --oneline 73ae2f21..HEAD`)

    59987cb9 feat(tools): reliability.py binds each board's declaration to the artefact it was written against by sha256 (written_against, --pins) and reads a mismatch or an absent pin as INCONCLUSIVE, with the fixtures, the pinned list, the re-taken matrix records and provenance lines for five cited documents [MESHSAT-1357]
    3bbc01df chore(records): checkpoint, the four-case matrix on the repaired reliability.py, the inventory before and after on the set 6 artefacts, and the consumers probe of an INCONCLUSIVE reading [MESHSAT-1357]
    7af28903 test(tools): checkpoint, the reviewer's four-case matrix and the inventory's fixtures for reliability.py, and the real-tree test that every candidate of every board is disposed [MESHSAT-1357]
    ae79b22d chore(tools): checkpoint, the reliability list rewritten for the inventory with every figure cited to a held document, seven maker documents filed, tests to follow [MESHSAT-1357]
    da232ce7 chore(tools): checkpoint, reliability.py reads an inventory by reference class and land, the declared phase's netlist by sha, and a missing input as INCONCLUSIVE; the list and the tests follow [MESHSAT-1357]
    1f3a6473 chore(records): checkpoint, the reviewer's four-case matrix of H3-01 reproduced on the unrepaired reliability.py [MESHSAT-1357]

and the commit that adds this README, the apply script and its test record.

## 13. Files in this folder

| File | What |
|---|---|
| `README.md` | this record |
| `matrix.py` | the reviewer's four cases through a tool's command line, fixtures outside the tree |
| `matrix-on-unrepaired-tool.txt` | the four cases on the tool of `73ae2f21`: 2 of 4 |
| `matrix-on-repaired-tool.txt` | the four cases on this branch's tool: 4 of 4 |
| `measure_inventory.py`, `inventory-before-after.txt` | the inventory of the seven artefacts, the old list's classes over it, the new list's disposal, every row |
| `consumers_probe.py`, `consumers-probe.txt` | how an INCONCLUSIVE reading reaches `rules_status`, and why the floor is needed |
| `apply_rel001_coverage.py` | the integrator's script for the coverage entry and the closure of S-89 |
| `apply-script-test.txt` | the script exercised on a scratch copy of `fnd/int7`: the refusals and the accepted runs |
