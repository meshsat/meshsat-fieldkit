# Stream d6rel: REL-001's population, its inputs and its binding (MESHSAT-1357)

Worker stream `d6rel` of the 28 September 2026 wave, branch `fnd/d6rel` from `73ae2f21` (the set 6 candidate), never
pushed. Finding **H3-01** of the independent review of handover H3
(`v2/docs/reviews/2026-09-27-h3-independent-review.md`), registry item **S-89** (`pcb_requirements.yaml` on the
integration line `fnd/int7`), erratum **h** of `v2/docs/handover/RELEASE-H3.md`. Prototype work: no board has been
built, ordered or measured; every number below is a reading of a netlist, a board file or a maker's document. The
checks of this stream, and the fresh check of it, are AI review, never a qualified review.

This record was rewritten on 28 September 2026 after the fresh check of the branch at `efd6899a`
(`_scratch/chk-d6rel/RESULT-d6rel-check-1.md`: mergeable, no blocking item, ten minor items) and the integrator's
follow-up. Section 9 says what each of those items became.

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
| 1. An explicit inventory by reference class and land; every mated or wearing part that the artefacts of A, B, C, D, E, E5 and P carry is in the denominator, each classed with its maker's figure cited to a held document, or UNDECIDED (the board INCONCLUSIVE) where the maker states none, where the part is not identified or where nothing is designed yet | `v2/ecad/tools/wear_inventory.py` (new), `v2/ecad/tools/pcb_reliability.yaml` (schema 2.0.0: `inventory`, `open_items`, `boards`), `v2/ecad/tools/reliability.py` | done; sections 4 and 5 |
| 2. A missing netlist, or one whose sha256 is not the declared phase's, reads INCONCLUSIVE; the declared phase's netlist is bound by sha256 in the reading | `reliability.py` (`phase_artefacts` resolution, `missing_input`, `written_against`, `--pins`) | done; section 6 |
| 3. The reviewer's four-case matrix as tests on isolated fixtures, plus fixtures for a connector with no wear word, the empty netlist, a part with no cycle figure, the sha mismatch | `v2/ecad/tools/tests/test_reliability.py`, `tests/test_reliability_inventory.py` | done; section 7 |
| 4. The detector parses (S-expressions through `netlist_parts.top_level`, YAML through `yaml.safe_load`), never greps prose | `wear_inventory.py`, `reliability.py` | done |
| 5. The shared files are not edited; apply scripts carry the coverage entry, the closure of S-89 and the tool's declared inputs | `apply_rel001_coverage.py`, `apply_config_inputs_reliability.py` | written and exercised on a copy of `fnd/int7` at `1c4235ec`; section 10 |
| 6. This record | `v2/docs/records/d6rel/` | this file |

## 3. The reviewer's four-case matrix, before and after

Both runs by `matrix.py` through the tool's command line on fixtures outside the tree (the verdict directed there
with `VERDICT_DIR`). The unrepaired tool is `git show 73ae2f21:v2/ecad/tools/reliability.py` (sha256/16
`71d0872195905c9d`) with its list of the same commit (`fbf56eb06df1d007`); the repaired tool is this branch's
(`c50f2b8b35d1d57b`, list `40f2a98323b1f9ce`).

| Case | Wanted | Unrepaired tool (`matrix-on-unrepaired-tool.txt`) | Repaired tool (`matrix-on-repaired-tool.txt`) |
|---|---|---|---|
| 1. one declared JST connector, its figure cited | PASS, exit 0 | PASS, exit 0 | PASS, exit 0 (1 candidate, 1 classed) |
| 2. plus an undeclared IDC header | FAIL, exit 1 | FAIL, exit 1 | FAIL, exit 1 (2 candidates, 1 refused) |
| 3. plus an undeclared `RJ45 MagJack` | FAIL, exit 1 | **PASS, exit 0** (the jack was in no denominator) | FAIL, exit 1 (2 candidates, `J_ETH` refused: a J on a connector land) |
| 4. board A's declaration, no netlist | INCONCLUSIVE, exit 3 | **PASS, exit 0** of 6 classes, 0 parts | INCONCLUSIVE, exit 3, `missing_input` names the absent netlist, no netlist recorded |
| The matrix | 4 of 4 | 2 of 4 (exit 1) | 4 of 4 (exit 0) |

The same four cases are `tests/test_reliability.py` `t_matrix_1_...` to `t_matrix_4_...`. Case 1 may read PASS
because its one class CITES a figure; the same connector under a class whose maker publishes none reads
INCONCLUSIVE (section 5, and the fresh check's P1).

## 4. The inventory of the set 6 artefacts, before and after (`inventory-before-after.txt`)

**The population is the netlist's.** For a board with a schematic the inventory reads the declared phase's netlist;
for board E5, which has none, its board file. A footprint that only a board file carries is not in it. The
declared-phase board files of A, B, D, E and P do carry such footprints: mounting holes H1 to H8 on A, twenty on B
(with six `S_` references), H1 to H4 on D and P, twenty-eight on E, every H on a `MountingHole` land; and they are
another generation of each design than the netlists (board A's netlist holds 225 parts its board file does not).
Boards C and E5 class the same kind of joint because their own artefacts carry it. This is open item **REL-O-13**
of the list and it holds boards A, B, D, E and P.

Written by `measure_inventory.py` (read only). BEFORE is the population the inventory finds, disposed against the
classes of the 16 September list by their reference patterns alone; the old TOOL's own reading of the same netlists
was 111 covered, 0 refused (`v2/docs/records/r8int6/fix/wear-before-after.txt`). AFTER is the repaired tool with
this branch's list. A candidate is a part of a mechanical reference class (J, P, X, BT, H, MP, SW, W, WH, F, JP, K,
BZ, CAM, PAD, TP), or a part of an electrical class on a mechanical land, or one on a land declared neither
mechanical nor soldered, or one with no land at all; the words (the twelve, and since the fresh check `jack`, `RJ45`
and `plug`) are a second net that adds and never removes.

| Board | Artefact (sha256/16) | Candidates | BEFORE classed / refused | AFTER classed / excluded / refused |
|---|---|---|---|---|
| A | `pcb-a-power-a23/out/pcb-a-power.net` `0a2b59087bcc2678`, 612 parts | 82 | 39 / 43 | 57 / 25 / 0 |
| B | `pcb-b-compute-b19/out/pcb-b-compute.net` `028997a6c5e8810f`, 1280 parts | 155 | 38 / 117 | 56 / 99 / 0 |
| C | `pcb-c-display-c8/out/pcb-c-display.net` `3fddbb3edcd4248a`, 219 parts | 74 | 9 / 65 | 24 / 50 / 0 |
| D | `pcb-d-aprs-d9/out/pcb-d-aprs.net` `7a2c0ac2190b141a`, 245 parts | 40 | 10 / 30 | 11 / 29 / 0 |
| E | `pcb-e1-dock-e7/out/pcb-e1-dock.net` `56adc9746d61c4e0`, 189 parts | 35 | 8 / 27 | 21 / 14 / 0 |
| E5 | `pcb-e5-block/pcb-e5-block.kicad_pcb` `686b29a734c55b9a`, 17 footprints | 17 | 0 / 17 | 17 / 0 / 0 |
| P | `pcb-p-pack-p2/out/pcb-p-pack.net` `760ac6f74d62d194`, 85 parts | 26 | 7 / 19 | 9 / 17 / 0 |
| Set | | 429 | 111 / 318 | 195 / 234 / 0 |

The 234 exclusions under 15 declarations, each with its reason and the land it speaks of: 219 test points, 6 solder
jumpers, 3 resettable fuses soldered in 1812 packages (board B) and the pack's soldered self-control fuse (board
P), the three I/O controllers' SWD pads (board B, no part fitted: their values call them SWD pads), and two
soldered parts of board B that the word net finds because their values name the wall RJ45 they serve (`T1`, the
Pulse magnetics, and `U5`, the PoE controller). Board B's ten bench and commissioning headers were excluded until
the fresh check and are now a class that OWES its figure and its measure (section 9, m4). Six parts carry a wear
word only in the description of what they do (`U101`, `U116`, `U201`, `U216`, `U301`, `U316`); they are named as
set aside and are not candidates: their lands are soldered packages.

The 58 classes: 24 cite the maker's figure, 16 have none because the maker's documents that were read state none,
8 mate nothing (solder lands, screw joints: a load and a measure, no cycle), 10 owe their figure under an open item;
4 classes owe their measure.

Corrections against the list of 16 September, each read on the netlists and the documents: board B's module
receptacles carried 60 cycles where Amphenol's product sheet of the 10164227 gives 30; board A's class "blind-mate
dock contacts" named Mill-Max pins and covered the eleven Radiall SMP-MAX receptacles while the seventeen Mill-Max
pins and the Preci-Dip connector were in no class; board D's class for "the radio module's sockets" covered two
JST-PH headers and its 500-cycle SMA class covered a U.FL socket (30) and a JST-PH header; board E5's classes named
references its board file does not carry; the JST classes carried 30 cycles "from the series specification" where
the held JST catalogues and JST's handling precautions state no mating-cycle figure; board B's class for three
soldered PCIe switches is gone (they are not candidates).

## 5. What each board reads, and why

**No board reads PASS, and a class whose maker publishes no figure never lets one** (the integrator's decision of
28 September 2026, authority SESSION, on the H3 review's condition; reverse by restoring the PASS in
`reliability.py` and `t_a_class_with_no_cycle_figure_must_say_why`). A board reads PASS only when every candidate is
disposed, every class either cites its figure or mates nothing, no measure is owed and no open item names the
board. What holds each board is named in its reading (`held_by` in the verdict's `counts.per_board`), and the test
`t_every_open_item_of_the_committed_list_holds_a_reading_and_every_board_says_what_holds_it` holds the reading equal
to the list.

| Board | Reads | Held by | Why |
|---|---|---|---|
| A | INCONCLUSIVE | REL-O-01, REL-O-02, REL-O-07, REL-O-08, REL-O-12, REL-O-13 | the pre-charge pin has no order code; the USB-C outlet's pigtail header names no part; four classes' makers publish no figure (JST VH, XH, PH, Keystone 3568); plus the three board-level items below |
| B | INCONCLUSIVE | REL-O-02, REL-O-03, REL-O-07, REL-O-08, REL-O-09, REL-O-12, REL-O-13 | the lead headers and the ten bench headers name no part; the Amphenol NVMe sockets' document states no durability; the coin cell retainer's measure is not recorded; three classes' makers publish no figure (JST VH, SH, Keystone 3034) |
| C | INCONCLUSIVE | REL-O-04, REL-O-05, REL-O-07, REL-O-08 | the panel ribbon header is a pick with no document held; the headset jacks have no part picked |
| D | INCONCLUSIVE | REL-O-07, REL-O-08, REL-O-10, REL-O-12, REL-O-13 | the relay's measure is owed (the transmit sequence); three classes' makers publish no figure (JST VH, PH, XH) |
| E | INCONCLUSIVE | REL-O-02, REL-O-07, REL-O-08, REL-O-12, REL-O-13 | six lead headers name no part; three classes' makers publish no figure (Keystone 3568, JST VH, XH) |
| E5 | INCONCLUSIVE | REL-O-06, REL-O-07 | the contact targets are the board's own plated pads: no maker rates them |
| P | INCONCLUSIVE | REL-O-07, REL-O-08, REL-O-11, REL-O-12, REL-O-13 | the pack lead's strain relief is not designed; three classes' makers publish no figure (Keystone 3568, JST XH, PH); none of its four classes cites a figure |

The board-level items, which name the boards they hold (`holds`) because they are about a board and not about one
class: **REL-O-07** (the expected number of mates over a service life is stated nowhere, REQ-028, so every cited
rating is compared with nothing: all seven boards), **REL-O-08** (the joints under heavy soldered parts are outside
an inventory that sees no mass: A, B, C, D, E, P) and **REL-O-13** (section 4: A, B, D, E, P). **REL-O-12** is named
by the sixteen classes whose makers publish no figure and says what is done about it (the question to each maker
prepared for the owner to send, or the prototype's mate-cycle test). Every open item of the list holds a reading:
an item that names no board and that no class names is refused by the tool's own check of its list, before any
board is judged (`check_open_items`; the fresh check's P15).

## 6. The inputs and the binding

* **A missing input is INCONCLUSIVE, never PASS.** A board of the manifest with no artefact of its declared phase, an
  artefact that cannot be read (not UTF-8, not one `(export ...)` or `(kicad_pcb ...)` expression, cut short, no
  `(components ...)` section, a component with no reference or a reference twice), an artefact with no component, a
  list that cannot be read or that its own check refuses, a board the list declares nothing for, or a vendor
  library that is not in the tree (since the fresh check: `missing_input` is set and the verdict counts the
  citations nobody checked, `citations_unjudged`): each reads INCONCLUSIVE with the reason (exit 3).
* **The netlist is the declared phase's**, resolved by `phase_artefacts` the way `rules_status.candidate` resolves it,
  never the newest file by mtime; for board E5 its declared phase's board file. The reading records it by path,
  sha256 and content identity beside the list's own sha256, and per board in `counts.per_board[<letter>].artefact`
  with `bound`, so a set-level reading says its binding board by board.
* **Each board's declaration is bound to the artefact it was written against** (`written_against: {sha256_16,
  content16}`). A class names a part and cites that part's figure, and the gate cannot read the part off the value
  text, so an artefact of another sha is not the one the list speaks of: the reading is INCONCLUSIVE and declares it
  as a missing input, saying whether the components and nets are the same (a re-export: read the values against
  the list and re-pin) or differ (the design changed: re-declare). The comparison of the artefact that is there
  still runs, because a refusal on it is real and FAIL wins. `reliability.py --pins` prints the lines and never
  writes them.
* **The consumers** (`consumers_probe.py`, `consumers-probe.txt`): an INCONCLUSIVE reading reaches
  `rules_status.result_for` as INCONCLUSIVE with the tool's reason, but `rules_status._supersedes` keeps an OLDER
  reading that had its input in front of a NEWER one that declares its input absent, so a word-list PASS would stand
  in front of the repaired tool's INCONCLUSIVE. The floor that closes it is `evidence_not_before` on REL-001
  (section 10).

## 7. The tests

`env -C <worktree>/v2/ecad/tools python3 tests/run.py reliability`, the last line on this branch:

    tests: 60 passed, 0 failed, 0 skipped

`tests/test_reliability.py` (50 tests, every fixture its own temporary tree with its own manifest, routeflow profile
directory, vendor folder and list): the four-case matrix; a connector whose value carries no wear word
(`t_matrix_3`, and `t_the_parts_the_word_list_never_found_are_in_the_inventory` on the real boards); the empty
netlist; a part with no cycle figure (`t_a_class_with_no_cycle_figure_must_say_why`, which now asserts INCONCLUSIVE
for a class whose maker publishes none, the fresh check's P1; `t_an_owed_figure_...`;
`t_nothing_mated_is_a_reason_...`); the sha mismatch, the absent pin and the printer; an open item that holds
nothing refuses the list (P15) and one that names the board holds it; a jack drawn as an integrated circuit on a
soldered land is found by the words (P14); the vendor library that is not there is a missing input; the declared
phase against the newest file; the unreadable netlist in five shapes; the citation of every figure by sha, page and
words; disposal exactly once; and the real tree (every candidate disposed, every board bound, every open item
holding a reading, each board held by exactly what the list says). `tests/test_reliability_inventory.py` (10
tests): the reference class, the land kinds, candidacy, the readers and what they refuse.

The fresh check's own probes, run against this branch's tool in the session's scratch directory: P1 to P14 and P15
all read as he wanted them (P1 INCONCLUSIVE, P14 FAIL, P15 INCONCLUSIVE).

## 8. The documents cited (30, each held under `v2/vendor/`, cited by sha256/16, page and words)

Fetched by this stream (lines in `v2/vendor/sources.txt` with URL, fetch time and full sha256): JST SH catalogue,
JST handling precautions, the Molex 2086581001 part page (Wayback capture of 16 November 2025), Keystone catalogue
M65 page 9, Hirose's U.FL series catalogue 2009.2 (Digi-Key's copy), the Amphenol RF 132134-11 and 132134 part
pages (Wayback captures of 17 and 13 February 2026). Held before this stream: the Radiall R222M00720 sheet, the
Mill-Max 0858 page, Preci-Dip 813, the three Wurth WR-BHD sheets, JST VH, XH and PH, Keystone M65 page 42,
Amphenol's 10164227 sheet, TE's M.2 guide, Amphenol RJHSE5380, HRO TYPE-C-31-M-12, Wurth 692122030100, GCT
SIM8060, Hirose FH34, C&K ATP19 and ATP16, APEM 5000, NKK M, Omron G6K, Amass XT60. Five of these had no
provenance line anywhere; this stream added one each to `sources.txt` naming the commit that added the file and the
full sha256, and invented no URL.

**Revisions** (`revision_scan.py`, read only, prints each document's candidate lines for a person to read). A
citation carries `revision:` where the document states its own, or where the tree's identity record
`v2/vendor/SOURCES.yaml` records it as stated: Amass XT60 (V1.2), GCT SIM8060 (A, 6th September 2018), the three
Wurth WR-BHD sheets (002.001, 2026-08-30), Wurth 692122030100 (001.003, 2025-06-12), Hirose FH34 (Mar. 2025),
Hirose U.FL (2009.2), Keystone M65 page 9 (its slug line, 9/29/15), TE (CS 01/2014), Omron (Cat. No. K106-E1-11),
Radiall (Issue 1107 B), C&K ATP19 (Revised: VL 02/05/25), and the four HTML captures by their capture instant: 22
citations of 17 documents. Thirteen documents state none that could be read (the five JST documents, Keystone M65
page 42, Preci-Dip, Amphenol 10164227, Amphenol RJHSE5380, HRO, APEM, C&K ATP16, and NKK M, whose one date line
does not call itself a revision); for them the sha256 binds the bytes and the open item of section 12 stands.

**Two citations say how to re-verify them** (`verify:` in the list): the Molex figure is not in the page's visible
text but in its one `application/ld+json` block (the `PropertyValue` named `Durability Mating Cycles Max`, value
`10000`); the HRO drawing has no text layer (pdftotext returns 18 characters) and its page must be rendered to read
note 3-3.

## 9. The fresh check's items and what each became

| Item | What the check found | What was done |
|---|---|---|
| m1 | a `none_published` class did not hold its board; a test pinned that PASS | the class holds its board INCONCLUSIVE, named, with the documents read; the test asserts it; section 5 says what each board reads |
| m2 | REL-O-07 and REL-O-08 were named by no class and held no board; fixed sentences said "REL-O-01 to REL-O-11" | an open item names the boards it holds (`holds`) or a class names it, or the list is refused; every sentence the apply script writes names each board's own items, read from the list and from each reading |
| m3 | board-file footprints (H*) in no netlist, undisclosed | open item REL-O-13 with its next action, holding A, B, D, E, P; section 4 says the population is the netlist's |
| m4 | board B's ten bench headers were excluded on an uncertainty that is owed elsewhere | they are a class owed under REL-O-02, figure and measure |
| m5 | the word net lacked jack, RJ45 and plug | added; P14's fixture is a test; board B's `T1` and `U5`, which the words now find, are excluded by name with their reason |
| m6 | the list cited a table that is on no integrated line | removed: REL-O-01 and REL-O-02 rest on what the netlist values say, REL-O-04 on `PROCUREMENT.md` and `SOURCES.yaml`, the SWD pads on their values; a test refuses the citation |
| m7 | no citation carried a revision | section 8: 22 citations carry one; 13 documents state none |
| m8 | `rules_status.CONFIG_INPUTS` described the old tool | `apply_config_inputs_reliability.py` (section 10) |
| m9 | apply script: (a) remediation owner and hours, accepted as disclosed; (b) PASS accepted against "never PASS"; (c) a set-level re-take would print no sha; (d) a floor with no offset read as UTC; (e) a reading with the vendor folder absent accepted | (b) a PASS is accepted only for a board the list holds by nothing, and the text says that; (c) the binding is read from `counts.per_board`; (d) refused; (e) refused, and the tool declares it a missing input |
| m10 | Molex and HRO need care to re-verify | `verify:` on both citations |

## 10. The apply scripts (the integrator runs them; this stream edits no shared file)

Order on the merged tree: `apply_config_inputs_reliability.py`, then `apply_rel001_coverage.py --stage coverage
--commit <merge>`, then the re-take of `reliability` on every board with the repaired tool, then
`apply_rel001_coverage.py --stage close-s89 --check --commit <merge>` and the same without `--check`.

**`apply_config_inputs_reliability.py [--root <tree>]`** replaces the `reliability.py` entry of
`rules_status.CONFIG_INPUTS`, which named `tools/pcb_board_facts.yaml` (no longer read) and said the readings "do not
bind anyway". It declares exactly what the repaired tool reads as configuration: `tools/pcb_reliability.yaml` and
every document the list cites (30, listed from the list of the tree it runs in, as `../vendor/...`). The artefact is
the thing judged and is recorded by sha; what the tool reads to find it is not declared, as for every tool there.
It asserts the old entry, that the new text differs, re-parses with `ast` and reads the entry back, checks that no
other entry changed, and refuses a second run.

**`apply_rel001_coverage.py --stage coverage (--commit <merge> | --floor <instant with its offset>)`** replaces the
REL-001 entry of `pcb_rules_coverage.yaml`: both test files; `evidence_not_before: {reliability: <floor>}`; a note
and a remediation whose numbers and whose sentence on what holds each board are COMPUTED on the tree it runs in
(`reliability.judge()`, read only) and never typed. **The floor is never a constant**: it is the instant the
repaired tool enters the tree the readings live in (the merge's committer instant), it must say its UTC offset, and
it is refused unless it is after every reading of the unrepaired tool the tree holds. Why: a first draft carried
this branch's last tool commit (16:46 CEST), and the integration line re-took reliability with the unrepaired tool
at 16:54 CEST (`1c4235ec`, PASS on every board); under the fixed instant those seven readings would have counted.
The remediation changes from `owner: OWNER, execution: OWNER, 0 h` to `SESSION, SEQUENTIAL, 4 to 10 h` (the
fresh check's m9a, accepted as disclosed): what remains is part picks, makers' sheets and design items.

**`apply_rel001_coverage.py --stage close-s89 --commit <merge> [--check]`** moves S-89 to `closed_items` with
`closed_by: commit <merge>` and a closing evidence read from the tree. It refuses until every board of the manifest
has a `reliability` reading found the way `rules_status` finds them that was taken after the coverage entry's
floor, with the list this tree holds, bound to the declared phase's artefact, with every citation checked, no
refusal and no missing input, held by exactly what the list holds the board by, and PASS only where the list holds
it by nothing. The five records that wait on S-89 (REQ-022, REQ-024, REQ-026, REQ-028, REQ-064) lose that wait and
cite the closing in their `history`; S-89's `limits_reading` is not carried into the closed entry. The validator is
read before and after and the file is restored if the change adds an error. `--check` asks every guard and writes
nothing.

## 11. Decisions (authority: SESSION, under the owner's standing rule of 26 September 2026)

| Decision | By | Reason | To reverse |
|---|---|---|---|
| A class whose maker publishes no figure never lets a board read PASS | the integrator | the H3 review's condition; a statement about a document is not a figure | restore the PASS in `reliability.py` and the test |
| Board B's bench headers are owed, not excluded | the integrator | the same uncertainty is owed elsewhere; owed is the safer reading | restore the exclusion of `efd6899a` |
| Open items are bound to the boards they hold; REL-O-07 holds all seven, REL-O-08 the six boards with a netlist, REL-O-13 A, B, D, E, P | this stream | the rule asks for the expected cycles and for every joint that carries load; what the list cannot compare or cannot see on a board must not read as done | remove `holds` and the item, or close the item |
| The population is an inventory by reference class and land; the words are a second net | this stream | a completeness gate must fail towards asking for a part | `git revert` of `da232ce7` |
| Each board's declaration is bound to its artefact by sha256 | this stream | a class names a part; the gate cannot read the part off the value text; a substitution is a mismatch until proven | remove the pin block, the pins and the three pin tests (`59987cb9`) |
| A soldered part the word net finds is excluded by name with its reason, not dropped from the net | this stream | the words add and never remove | remove the word, and the exclusion with it |
| Where a document gives a range, the LOWEST figure is carried and the words say so | this stream | a bound is named a bound | none needed |
| The evidence floor is the merge's instant, with its offset, checked against the tree | this stream | a fixed instant was overtaken within the hour | pass `--floor`; the guard stays |
| A citation carries a revision only where the document states one | this stream | no revision is invented; the sha binds the bytes | add it when read |

## 12. Open items left by this stream, each with its next action

| Item | Next action |
|---|---|
| REL-O-01 to REL-O-13 of `pcb_reliability.yaml` | each carries its `next_action` in the list and the boards it holds (section 5) |
| The merge and the re-take (the closure condition of S-89) | the order of section 10, on the merged tree and the box |
| Thirteen cited documents state no revision that could be read | where a maker's site gives a revision for the same bytes, record it; the sha binds them meanwhile |
| The ribbon box headers' figure (Wurth WR-BHD, 30 cycles, boards A, B, D) is the figure of a session pick that no generator carries (`PROCUREMENT.md` HC6-SC-7; `SOURCES.yaml` reads the pick's identity NOT_PINNED) | when a generator names the header, read the class's part against it; if it differs, the class owes its figure |
| REL-O-03's two Amphenol M.2 documents were not opened by the fresh check | file Amphenol's GS-12-1142 or the part's own sheet and carry the figure of the plating fitted |
| Series-level figures (Hirose FH34, Amphenol RJHSE, Hirose U.FL) were confirmed at the page, not against each order code's row | read each order code's row at layout entry (CMP-002) |
| The full suite has not been run on this branch (box only) | the integrator's box run on the merged tree |
| `RELEASE-H3.md` erratum h, `LAYER-STATUS.md` and `CURRENT-EVIDENCE.md` (which reads REL-001 LIMITED while S-89 stands) | the integrator's pages, re-rendered after the closure |

## 13. What was run, and the exact result lines

* `env -C <worktree>/v2/ecad/tools python3 tests/run.py reliability`: `tests: 60 passed, 0 failed, 0 skipped`.
* `python3 v2/docs/records/d6rel/matrix.py v2/ecad/tools v2/ecad/tools/reliability.py`: `the matrix: 4 of 4 case(s)
  as wanted, 0 not`, exit 0.
* The same on the tool of `73ae2f21`: `the matrix: 2 of 4 case(s) as wanted, 2 not`, exit 1.
* `python3 v2/docs/records/d6rel/measure_inventory.py v2/ecad/tools --old $SP/old`: `set 429 111 / 318 195 / 234 /
  0`, exit 0.
* The fresh check's `probe.py` and `probe2.py` against this branch's tool, in the scratch directory: P1 to P14 and
  P15 `ok`.
* Both apply scripts on a scratch copy of `fnd/int7` at `1c4235ec` (`apply-script-test.txt`): a floor with no
  offset `REFUSED`; the 16:46 floor `REFUSED` naming the tip's seven word-list readings; the 17:00 floor `exit 0`,
  then `REFUSED ... this stage has run`; `close-s89 --check` on the tip's readings `REFUSED`; on a re-take without
  the vendor library `REFUSED` (citations not checked); on a set-level re-take `the closure's conditions hold on 7
  board(s); nothing was written`; after the per-board re-take `S-89 moved to closed_items ... cited instead in
  REQ-022, REQ-024, REQ-026, REQ-028, REQ-064`, `36 error(s) before this change, 36 after, 0 new`, `exit 0`, then
  `REFUSED: S-89 is already in closed_items`; `apply_config_inputs_reliability.py`: `declares the list and 30 cited
  document(s) ... 24 other entries unchanged`, `exit 0`, then `REFUSED ... this script has run`.
* No gate, `rules_status.py` or `rules_render.py` was run in any tree; no verdict was written into the tree.

## 14. Files in this folder

| File | What |
|---|---|
| `README.md` | this record |
| `matrix.py`, `matrix-on-unrepaired-tool.txt`, `matrix-on-repaired-tool.txt` | the reviewer's four cases through a tool's command line: 2 of 4 and 4 of 4 |
| `measure_inventory.py`, `inventory-before-after.txt` | the inventory of the seven artefacts, before and after, every row |
| `consumers_probe.py`, `consumers-probe.txt` | how an INCONCLUSIVE reading reaches `rules_status`, and why the floor is needed |
| `revision_scan.py` | which cited document states its own revision |
| `apply_rel001_coverage.py`, `apply_config_inputs_reliability.py` | the integrator's scripts for the three shared files |
| `apply-script-test.txt` | both scripts exercised on a scratch copy of the integration tip |
