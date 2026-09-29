# Stream w5identc: board C's part identities (layer 6's exact-part requirement)

MESHSAT-1357, branch `fnd/w5identc` from main `b874b744` (set 13), 29 September 2026, three rounds. Prototype work:
nothing is built, bought or deployed, and nothing here orders anything. Every rule and choice here is the session's
under the owner's standing rules (`authority: SESSION`, reversal stated). The checks named are AI reviews.

## The result, with its denominators

Board C's committed netlist (`v2/ecad/pcb-c-display-c8/out/pcb-c-display.net`, sha256 `c9f73945...`) carries 225
parts; 50 are marked exclude_from_bom (48 test points, the camera module's two screws), so **175 BOM parts** in
**87 selections** (`part_identities.py selections --board c`).

| State | Selections | Rows |
|---|---|---|
| RESOLVED, PRINTED: the maker's document prints the part number on the cited page | 21 | 27 |
| RESOLVED, DECODED: the maker's ordering-code table on the cited page decodes it against the selection | 23 | 89 |
| UNRESOLVED | 40 | 56 |
| NOT_A_PART (two solder jumpers, the PI button's lands) | 3 | 3 |

UNRESOLVED by reason class (each selection's reason names only facts `build_table.py` asserts when it runs):

| Reason class | Selections | What |
|---|---|---|
| CHOICE_OWED | 23 | 17 panel lamps (no intensity or angle through the 17 Mentor 1282.5004 guides ASSEMBLY.md names), BZ1 (Floyd Bell MC-09-530-Q named as a class; its held sheet gives quick connect blades where the value asks two flying leads), two U-174/U jacks (a class, drawing owed), H1 to H8 (no screw standard or plating), J_MAINSW (the lead and its XH2.5 housing are bought, rule N-1), C28 (requirement known, no part chosen) |
| DOCUMENT_OWED | 8 | BAT54W, the Everlight status LED, BH254VS-26P, GZ1608D601TF, ABM8-272-T3 (printed only in Raspberry Pi's RP2040 documents), three APEM 5636ADKB-2V: no PDF under v2/vendor prints them (`scan_vendor.py`: 429 PDFs read, 11 without text) |
| DOCUMENT_DOES_NOT_NAME_THE_PART | 8 | the C&K ATP19 and ATP16 (two) and NKK M2044 switches, whose makers' series sheets are held with their ordering schemes and print no part number (decision 59's schemes are for capacitors and resistors only); Fenghua 0603B103K500NT and 0402CG150J500NT, Arlitech ATNR4010100MT and Uniroyal CS03W5F470LT5E, whose sheets are on fnd/w5ident only |
| PART_DOES_NOT_MEET_THE_REQUIREMENT | 1 | C31: the generator names Murata GRM188R61E475KE11D, X5R, where rule C-D3 asks X7R |

Order codes: 13 RESOLVED selections carry a code this tree's catalogue reading does not hold (C106248, C106858,
C23138, C25190, C324726, C326595, C485080); their code to part mapping is stream w5ident's reading of 27 September 2026,
recorded per selection (`order_code.read_by`). One selection's netlist orders another code than its identity: C1 and C2
(below, round 3 minor 9).

## The tool's identity check on board C

`env -C v2/ecad/tools python3 part_identities.py check --out <this folder>/readings/check-board-c-b874b744.json`, with
the held Uniroyal sheet fetched: **175 rows, 87 selections, 0 rows uncovered, READ 21 and DECODED 23, 0 problems,
verdict HOLDS** (reading `602b2c24...`, table `2dce2a39...`, tool `20adab11...`). Without the fetched sheet it reads 13
bindings UNREAD and 13 problems; `--unfetched-ok` then writes verdict `HOLDS_WITH_UNREAD` with `unfetched_ok: true`, which
`apply_identities_c.py` refuses.

Tests: `test_part_identities` 24 passed, 0 failed. Lint tests once each: test_rule_windows 6/0, test_import_before_use
3/0, test_documented_options 6/0, test_swallowed 6/0, test_shipped_strings 5/0, test_driver_hygiene 78/0,
test_public_tables 2/0.

On a scratch clone of `fnd/int15` at `097d2517` with this branch merged (clean): the check 0 problems;
`apply_decision_decoded.py` wrote decision 59 and rebound CFL-016 (`a41df5d1...` to `c8c51927...`), refused a second run;
`rules_lib.py requirements` 0 errors, 0 warnings before and after; `decisions_render.py`; `apply_identities_c.py` opened
S-125 (set 14 holds S-124), refused a second run; `rules_lib.py validate` 0 errors; `rules_render.py --requirements`;
test_requirements, test_layout_entry_stages, test_decision_register and test_part_identities 102 passed, 0 failed, 3
skipped. The same chain on the branch tip itself (main-based): S-124, 102 passed, 0 failed, 3 skipped. The clone was
removed.

## Round 3: the check's five blocking items

| Item | Answer |
|---|---|
| B1, the table's own requirements | `check` derives every selection's requirements and kind from the committed netlist, the intent and the generator's value (the rows' `requirements`, `v_working_bound` aside), refuses a table whose stated requirements differ, and judges every binding on the derived ones. Test `t_the_check_judges_on_requirements_derived_from_the_netlist` is the check's mutant (C37 lowered to 6.3 V with CC0603KRX7R5BB105): refused twice over |
| B2, part numbers outside the scheme | The schemes live in the tool (`part_identities.SCHEMES`, pinned to the document's sha256 and page); the layout is read from the page (Yageo's placeholders numbered by "(1) SIZE" to "(5) CAPACITANCE VALUE", Uniroyal's "1st~4th codes" to "14th code"), the whole part number is sliced by it with nothing left over, each field must be the one at its position and each literal the scheme's, each row must lie in its own position's part of the page, the kind must be the scheme's (a capacitor scheme only for a capacitor), and every deciding property of the kind must be decoded (a property the scheme cannot decode, such as a shunt's TCR, refuses). Tests: every probe of the check (tolerance and packing swapped, a padding X, an extra BB, Uniroyal's packaging and special swapped, a pushbutton and a crystal) refused on the makers' own pages |
| B3, CFL-016 stale | `apply_rebind_decisions_w5identc.rebind` (the int14 pattern: HEAD's file parsed, every decision identical, exactly decision 59 added, the decisions CFL-016 names in satisfied_by, 28 and 40, asserted identical) is called by `apply_decision_decoded.py` in the same run; exercised on int15 and on the tip as above |
| B4, the table contradicts its rule | D-2 and `what` state PRINTED or DECODED per decision 59, its limit, and the packing placeholder rule |
| B5, false UNRESOLVED reasons | Every UNRESOLVED and NOT_A_PART reason re-read (`build_table.reread`, each fact asserted): J_EPD RESOLVED PRINTED on Hirose's FH34 catalogue page 6 (FH34SRJ-24S-0.5SH(##) keyed "(##) : (50)", "(50): Standard" on page 5); BZ1's true facts; C31's X5R stated; the switches name their held series sheets; J_MAINSW moved from NOT_A_PART to UNRESOLVED (rule N-1); the lamps, jacks, screws, C28 and the far series sheets restated on read facts; the DOCUMENT_OWED reasons rest on the vendor scan |

## Round 3: the twelve minors

| Minor | Answer |
|---|---|
| 1, "15 lamps" | 17 (the table's CHOICE_OWED rows and ASSEMBLY.md's "Light guides, 17 x") |
| 2, the doubled marker | title rewritten; the marker "(stream w5identc)" appears once |
| 3, authority_why | the residual-risk half added, citing the check's reading of Yageo's range tables |
| 4, `ask` and `outcome` | the "do not publish" claim replaced by what build_table.py read; the outcome says the value code is computed by its row's rule |
| 5, the docstring | states what the code asserts |
| 6, LAYOUT_STAGE | disposition now LAYOUT_ENTRY_PACKET, whose why says it does not hold layout entry. It should: review D makes identities a precondition of board C's layout entry. How: a feasibility record staged at LAYOUT_ENTRY holding board C (FEA-006's shape: parent, statement, acceptance, the three stages, owner, evidence FAIL) whose waits_on names the open item. Not drafted as a script: layer 6 item 6.1 asks it of every board with a schematic, and staging it moves every board's layout readiness, which is the integrator's |
| 7, Yageo's sources.txt line | reworded on the a1solar precedent, quoting page 29's revision sentence |
| 8, `--unfetched-ok` | recorded in the reading (`unfetched_ok`) with verdict `HOLDS_WITH_UNREAD` |
| 9, C1 and C2 | the identity is right under the table's rules: the value states no dielectric, rule C-D3 asks X7R, YAGEO CC0805KKX7R7BB106 decodes against it; the netlist's C15850 is Samsung CL21A106KAYNNNE, X5R (this tree's catalogue reading). `draft_gen_c_c1_c2.py` moves both rows to C326595 (check mode run, not applied; C326595 is w5ident's reading, not this tree's). The table records it (`order_code.netlist_agrees: false`) |
| 10, codes outside the tree's reading | recorded per selection (`in_this_trees_reading`, `read_by`); 13 RESOLVED selections, 7 codes |
| 11, next actions | the DECODED route first where a maker's table exists |
| 12, packing suffixes | D-2: a packing code may be printed as the maker's placeholder where the same page keys it (J_EPD); a part number without one (SS2040FL) is printed as is |

Observation passed on, not this stream's: `v2/vendor/power/panjit-ss2020fl-series.pdf` (on main) reads, in the check's
words, "Reproducing and modifying information of the document is prohibited without permission from Panjit International
Inc."; under the owner's rule of 27 September it would be held back. It is still bound here (the SS2040FL selections).

## Decision 59 and the documents

`apply_decision_decoded.py` appends decision 59 (number computed; SESSION; ruled_by "SESSION under the owner's ruling of
21 September 2026"; ruled_on 2026-09-29; reversed_by) and rebinds CFL-016 in the same run. Documents:
`v2/vendor/passives/yageo-cc-series.pdf` filed (no terms stated; a1solar precedent); Uniroyal's thick film sheet held
back (`fetch_held_back.py`, sha256 `11cd644d...`).

## The stale BOM export (facts, round 2; not regenerated)

`v2/release/handover/_generated/pcb-c-display-c8/NOT_FOR_FAB-pcb-c-display-bom-per-reference.csv`: tracked, one commit
(`6dc4e708`, the H2 exports of `99cde56b`), written by `handover_exports.py exports` on the KiCad box; it agrees with the
netlist until `e28f91a6` and lacks 8 parts at `b874b744` (`readings/bom-export-history.txt`). The check reads it as a
dated handover snapshot that names its own commit, to be regenerated at the next handover; the integrator decides
whether it needs an item.

## What was brought from w5ident

`part_identities.py` and its tests (`c08f4d5a`), the Yageo sheet, board C's identities and rules
(`w5ident-board-c-identities.json`). Not brought: the resolver, the six-board table, the readings, the drafts, the other
vendor files. `adapt_tool.py` replays round 1's first edits; `git diff fnd/w5ident -- v2/ecad/tools/part_identities.py`
shows all.

## Integrator's run order

1. Merge `fnd/w5identc` (clean on `097d2517`).
2. `python3 v2/docs/records/w5identc/fetch_held_back.py`.
3. `python3 v2/docs/records/w5identc/build_table.py` and `env -C v2/ecad/tools python3 part_identities.py check`: both
   reproduce with 0 problems while board C's netlist and intent are `b874b744`'s (they are on `097d2517`). If they moved,
   re-run the builder, the check with `--out v2/docs/records/w5identc/readings/check-board-c-b874b744.json`, and re-pin
   `READING_SHA256` in `apply_identities_c.py`.
4. `apply_decision_decoded.py --check`, then without it: decision 59 and CFL-016's rebind in one run. Then
   `decisions_render.py` and `rules_lib.py requirements` (0 errors on int15 and on the tip).
5. `apply_identities_c.py --check`, then without it (S-125 on int15, S-124 on main). Then `rules_lib.py validate` and
   `rules_render.py --requirements`.
6. The box suite with the Uniroyal sheet fetched on the box. Optional, the integrator's: the feasibility stage of minor
   6; `draft_gen_c_c1_c2.py --apply` with a box regeneration of board C; the BOM export at the next handover.

## What stays open

- 40 UNRESOLVED selections (56 rows), each with its next action.
- Decision 59's limit: no range-table citation, so a decoded part may not be made at that rating.
- Switch schemes (C&K, NKK) would widen decision 59 beyond capacitors and resistors.
- Documents not obtained on 29 September 2026: Abracon's ABM8-272-T3 (404 at abracon.com and the archive).
- Not judged: DC bias, grade against the envelope, surge levels, stock (w5ident's reading of 27 September 2026).
