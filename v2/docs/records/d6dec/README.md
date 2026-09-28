# Stream d6dec: decision 42's tool side, T1 to T10 (FEA-006), 27 to 29 September 2026

MESHSAT-1357. Prototype design: nothing has been built, ordered or measured. Branch `fnd/d6dec`, worktree
`/home/claude-runner/worktrees/meshsat-fieldkit/d6dec`. The first author wrote the class rules, the fan selection, the
seat search, the escape cost and the gate's class reading (commits 0f24f750 to 3c98a88e, 27 and 28 September); the
resumed author (29 September, brief `_runs/claude/d6dec/20260929T0032/BRIEF.md`) checkpointed the two files left
uncommitted, merged main 9147db5d (sets 6 to 8) with `merge --no-ff`, and finished the rest listed below. The running
log is `LOG.md`; the maker-clause check is `BASIS.md`.

The ruling this implements is `v2/docs/feasibility/DECOUPLING.md` section 6; the list is its section 8.1.

## T1 to T10

| item | what it became | tests | status |
|---|---|---|---|
| T1, the fan set follows the escape pass | `decoupling_rules.py`: `is_fine`, `min_pitch_nm`, `escaped` (escape.py's old selection with its two exemptions, unchanged), `copper_fanned` (eight or more numbered copper SMD pads at 1.0 mm or less, paste apertures not counted), `fanned` (the union). `fan_select.py` turns a KiCad footprint into those inputs (`is_escaped`, `is_fanned`, `escape_skip` from the caller's environment or `tools/boards/<x>.json`, `fan_boxes`, `tht_boxes`). `escape.py`, `bypass_slots.py`, `bypass_place.py` (through `bypass_search.Context`), `bypass_seats.py` and `intent_checks.py` all call it; none keeps a copy. | `test_decoupling_rules.py`: the SOIC-8-1EP not fanned, the WSON-6-1EP fanned, SOT-23-6 and MLPD-6 fanned, the 0.8 mm TQFP fanned, the fine-pitch parts fanned, an ESCAPE_SKIP part fanned only by its copper pads, the selection part by part against the record that measured the ruling (lands read from the committed boards into `tests/fixtures/decoupling/footprints.json`), and an AST check that none of the files defines its own selection. `box/escape_parity.py`: the escape pass of 73ae2f21 against this branch on the six committed boards stripped of copper: the same copper on all six (run5). | DONE |
| T2, one limit keyed by class | `decoupling_rules.limit` (screen 3.0 mm for R, D, L; 6.0 mm for B2; none for A and B1; the maker's `maker_mm` as a cap no allowance passes) and `judge` (pass, justified, recorded, fail; an allowance never gives pass). The gate, `bypass_search.search` (both placers) and `bypass_place`'s own "where it sits now" all measure rail pad to pin (`bypass_search.rail_pad_number`, from the netlist beside the board where there is one, else a bound: the farther pad). The value string is not an argument. | `test_decoupling_rules.py` (the value string cannot decide the limit, each class its own limit, an unclassed entry refused and never defaulted, a maker's distance no allowance passes); `test_decoupling_board.py` (the same on boards KiCad built, through the gate). | DONE. `bypass_seats.py`, the report of seats further out (not one of T2's three, named by DEC-001's coverage row), takes each entry's class screen too and measures rail pad to pin since 91e7649e; its walk still steps capacitor centres and keeps every fan closed, own-pin windows included (the windows are the placers'). |
| T3, four rotations | `decoupling_rules.rotations`, `rotate`, `best_rotation`; `bypass_search.search` tries every orientation at every seat and keeps the smallest loop-equivalent distance; `bypass_search.apply` turns the footprint. `bypass_slots.reserve` first drops the capacitor at rotation 0 and then hands it to the search (the `place(..., 0.0, ...)` the set 8 inventory flags is that first drop, not the seat). | `test_decoupling_rules.py` (the rotation kept is the one that brings the rail pad nearest); `test_decoupling_board.py` (a class D capacitor seated in its window with its rail pad toward the pin, turned). | DONE |
| T4, the fan opened for the own-pin window and R2 only, and the cost per part | `decoupling_rules.window_box`, `pin_side`, `fan_blocks` (the own-pin window of a class D or L entry, the converter's fan for its own class R parts, no other fan ever opened); `bypass_search._refuse` and `Context.converter_of`. `escape_cost.py`: every refused pad is asked again without the part's own-pin window capacitors, without its own power-stage parts, and without the declared capacitors of the other side; `pin_sites` and `site_refused` for parts left to the router (D5). **Closed again (29 September):** the parts whose absence alone clears a lost pad are named (all of the cause's parts when none does alone); `escape.py` writes `out/<stem>-escape-cost.json` with a `close` list; `bypass_search.closures` reads it and shuts that one opening while the part whose escape it cost stands where the pass measured it (a moved part makes the entry stale, counted and not applied); `bypass_place` re-seats a capacitor that sits in a closed opening, even to a seat further out, and reports STUCK when none is left inside the screen. | `test_escape_cost.py` (11: the three causes, a pad refused by something else blamed on nothing, bulk given no window, the question lays no copper, the culprit named alone, all named when none alone, nothing closed when nothing was lost); `test_decoupling_board.py` (an escape lost to an own-pin window reported by part and cause, the same capacitor undeclared blames nothing, a window that cost an escape closed again on the next placement, a stale closure not applied, a converter's fan open to its own input capacitor and to no other). | DONE in the tools. The chain (`full.sh`) still runs the placers before the escape pass and not again after it, so a closure acts at the board's next regeneration or at a `bypass_place.py` run, not in the same chain run: open item 2. |
| T5, a declaration carries its class and basis | `intent.bypass(cap, part, pin, net, cls, basis, **fields)` (`value_floor`, `esr_max`, `same_side`, `maker_mm`, `provisional`); `intent.bypass_form()`; `intent.write` refuses an entry with no ruled class or no basis. `decoupling_rules.CLASSES`, `normalise` (the round 8 aliases `floor`, `floor_uF`, `esr`, `esr_bound` read as the canonical keys), `form_problems`. The gate and both placers refuse an unclassed entry by name. | `test_intent_bypass_class.py` (6, new: keywords, the idiom the generators use, three refusals, class L's missing floor noted by name, and every committed intent's entries classed); `test_decoupling_rules.py` (form problems, class L and R fields, aliases); `test_decoupling_board.py` (the gate and the placer refuse an unclassed entry). | DONE, with decision S-1 below: class L's floor and ESR and class R's same side are printed by `intent.write`, not refused. On the committed intents that leaves 8 class R entries on A without `same_side` and, on D, 10 class L entries without an ESR statement and 5 without a floor (the set 8 inventory's schema rows). B1's "names the regulator and output pin" and the power-loop replacement of VISNS, FB and EN declarations are carried by the generators (G1, G10, G11, `power_loops`), not checked by a tool. |
| T6, an allowance names its capacitor | `decoupling_rules.parse_allow`; `intent_checks.py` and `place_audit.py` read the allow file through it; a line naming no capacitor allows nothing and is printed; an allowed capacitor is counted `justified` in the verdict's counts, never `pass`. The 8 September blanket line is removed from the twelve `bypass-allow.txt` files (six project folders and six phase folders). | `test_decoupling_rules.py` (a line naming none allows nothing, a named line allows that one, a reason nobody could check and a second line for one capacitor refused, and no allow file in the tree carries a line naming no capacitor); `test_decoupling_board.py` (the blanket line allows none; a named line gives a justified deviation and no pass); `test_board_gates.py` fixture updated to a classed entry. | DONE, with decision S-4 below (the phase-folder copies were cleared too). |
| T7, DEC-001's registry text | `apply_dec001_registry.py` in this folder, for the integrator: section 8.2's sources, status, acceptance and rationale into `pcb_rules.yaml` (the four source hashes written whole from the held files), and DEC-001's coverage row naming the new tools and fixtures with `HEURISTIC_AS_LAW` kept. Asserts the old text once inside DEC-001, the new text different, re-parses both files, runs `rules_lib.validate`, refuses a second run. | Run on a scratch copy of the tools: applied, 0 validation errors, the second run refused. | DELIVERED, not applied: both files are the integrator's. |
| T8, the re-render in the merge commit | the integrator's step: `python3 v2/ecad/tools/rules_render.py` in the commit that applies T7, committing the re-rendered `PCB-OPEN-PAIRS.md` and rule pages. | none here: a render writes the tree's generated pages. | NOT DONE by this stream, by the worker rules (never run `rules_render.py` in a tree). |
| T9, the other side | `decoupling_rules.two_sided`, `far_side` (refused on a one-sided board, for class R and `same_side`, inside any fanned part's fan box of either side, over a through-hole courtyard), `via_allowance_mm` (from the stackup row by the two closed forms of `rv-dec/dec_loop.py`), `stack_from_layers`, `loop_equivalent_mm`; `fan_select.smd_sides`, `tht_boxes`; `bypass_search.allowance` (the board file's own stackup, else `stackup_write`'s row for its layer count); the gate counts a board's sides without the declared capacitors that sit opposite their part, so a first far-side seat cannot make a board two-sided. | `test_decoupling_rules.py` (the allowance from the row: 2.26 mm on JLC04161H-7628, 3.54 mm on JLC06161H-3313; the board's own stackup gives the row's number; the refusals; D12's C53 reads 2.80 mm); `test_decoupling_board.py` (one-sided board refused, two-sided judged with the allowance, inside a fan refused whatever the allow file says, the maker's same side refused, the placer offers the other side only on a two-sided board). The real-board cases of the page (D12's C15, C16, C17) are read in the table below, not in a fixture. | DONE, with decision S-3 (3.54 mm, not the page's 3.7). On a placed board the gate re-reads a far-side seat's allowance at its OWN via pair's pitch (`decoupling_rules.seat_via_pitch`: the nearest via of each pad's net within 1.5 mm; the page's 0.8 mm kept, and said, where a pad has none; `bypass_search.allowance_row` gives the row); the placers, which seat before any via exists, use 0.8 mm. Test: `t_a_far_side_seat_is_priced_at_its_own_via_pitch_where_it_has_two_vias`. |
| T10, the ground pad's own via | `decoupling_rules.own_via`; the gate names the ground via of every class D and L capacitor, whether it is its own or also another pad's landing, and its distance; no via of its own, or none and a pour, is a justified deviation, never a pass; the rail pad keeps the old reach test. | `test_decoupling_rules.py` (shared, own, none); `test_decoupling_board.py` (a via that is a neighbour's landing is a deviation, an own via passes and is named, no via at all is a deviation). | DONE |

## Other deliverables

- `BASIS.md`, `basis.json`, `make_basis_md.py`, `box/basis_check.py`: the 440 declarations and power-loop rows of the
  six committed intents, their quoted maker clauses looked up in the 428 held PDFs. FOUND 262, PAGE 42, NOT_FOUND 3,
  NO_QUOTE 133; each NOT_FOUND row read in its document (two quotations not verbatim, one text layer without the micro
  sign; none changes a value or a class).
- `inventory-set8.json`: the first author's `inventory.py` re-run on the set 8 netlists (main 9147db5d merged): G1 to
  G14 read DONE on the committed netlists and intents. Its T3 and T4 rows read NOT DONE because their detectors predate
  the implementation (T3 looks at the first drop in `bypass_slots`, T4 asks whether `escape.py` itself reads a class;
  `escape_cost.py` does). The table above is this stream's reading of T1 to T10. `inventory.json` stays the set 6 read.
- `box/escape_parity.py`, `box/dec001_read.py`, `box/gen_check.py`, `box/run_box.sh`, `box/results_md.py`,
  `box/before_after.py`, `box/to_box.sh`: the box scripts; `box/run5/` and `box/run6/` their fetched outputs (tests,
  parity, generator check, DEC-001 read). The first author's box outputs of 27 September stay on the box under
  `/root/d6dec/run/` (escape parity then: same copper on all six; before_after: each fixture before and after).

## Results

### Tests on the KiCad box at 475586ca (the code of 91e7649e, the last code commit): the 33 test files of `box/run_box.sh`, the ones this branch adds or changes and every one that names a tool it changes, in one `run.py` call

`tests: 533 passed, 0 failed, 1 skipped`

- SKIP: `test_finish_order.t_routeflow_validate_agrees_with_these_rules SKIP the profiles pin /root/gitlab/products/meshsat/meshsat-fieldkit, which exists here and is not this tree, so validate's one-tree property is about`

Earlier box runs, kept for the record: run3 at c1a1f28e, 526 passed, 1 failed (the stale source check of S-5), 1
skipped; run4 at d62e768b, 532 passed, 0 failed, 1 skipped; run5 at cd28d77d, 533 passed, 0 failed, 1 skipped
(`box/run5/tests.log`). On this host, at 91e7649e: `test_decoupling_rules` 31 passed, `test_escape_cost` 11 passed,
`test_intent_bypass_class` 6 passed, `test_exposed_pad_vias` 9 passed, 0 failed, 0 skipped each; the pcbnew tests skip
here by design.

### The six schematic generators under this branch's `intent.py` (run5, `box/gen_check.py`)

All six exit 0 and write an intent identical to the committed one apart from `written`; `intent.write` refused
nothing; it printed 8 notes on board A (class R without `same_side`) and 15 on board D (class L without an ESR
statement or a floor), as S-1 says (`box/run5/gen_check.log`, `gen_check.json`).

### Escape parity at cd28d77d: 73ae2f21's escape.py against this branch's, six committed boards stripped of copper

`escape.py`, `escape_cost.py` and `fan_select.py` are unchanged from cd28d77d to the branch's tip, so this parity holds for the tip. Board B's pass took about 4.5 minutes before and 5.5 after, as on 27 September.

| board | same copper | vias | tracks | pads with no escape | decoupling cost line |
|---|---|---|---|---|---|
| A (pcb-a-power-a23) | yes | 467 / 467 | 452 / 452 | 0 / 0 | 0 refused pad(s) would have been escaped without a declared seat (56 declaration(s) read); 0 refused for another reason |
| B (pcb-b-compute-b19) | yes | 1477 / 1477 | 1631 / 1631 | 288 / 288 | 62 refused pad(s) would have been escaped without a declared seat (281 declaration(s) read); 226 refused for another reason |
| C (pcb-c-display-c8) | yes | 165 / 165 | 188 / 188 | 3 / 3 | 0 refused pad(s) would have been escaped without a declared seat (24 declaration(s) read); 3 refused for another reason |
| D (pcb-d-aprs-d9) | yes | 68 / 68 | 92 / 92 | 7 / 7 | 4 refused pad(s) would have been escaped without a declared seat (31 declaration(s) read); 3 refused for another reason |
| E (pcb-e1-dock-e7) | yes | 179 / 179 | 171 / 171 | 4 / 4 | 0 refused pad(s) would have been escaped without a declared seat (29 declaration(s) read); 4 refused for another reason |
| P (pcb-p-pack-p2) | yes | 46 / 46 | 62 / 62 | 0 / 0 | 0 refused pad(s) would have been escaped without a declared seat (4 declaration(s) read); 0 refused for another reason |

Before / after in each cell. The cost lines of the new pass (per part and cause) are in `box/run5/escape_parity.log`.

### What DEC-001 reads on each committed candidate under the new rules (NOT EVIDENCE: read outside the tree)

Read by `box/dec001_read.py` at 475586ca on the KiCad box: each phase folder copied whole to `/root/d6dec/run6/read/`, this branch's `intent_checks.py` run there. The boards are the committed candidates (A32, B21, C24, D12, E17, P4); the intents are the committed ones (A and B regenerated in set 8), so a declaration newer than its board's placement is read as not on the board. Nothing here is a reading the registry may count.

| board | verdict | declared | pass | justified | recorded | fail | no own ground via | far side | FAIL lines by cause |
|---|---|---|---|---|---|---|---|---|---|
| A (pcb-a-power-a23, board 58e26c67987b1daa, intent 35e430a791ab2b44) | FAIL | 56 | 0 | 0 | 1 | 55 | 0 | 0 | declared, not on this board (the intent is newer than the placement) 40; past the class screen, no allowance names it 15 |
| B (pcb-b-compute-b19, board 2e64b5bf2d9cd3bc, intent a7bf625c8b878dd5) | FAIL | 281 | 0 | 0 | 0 | 281 | 0 | 78 | declared, not on this board (the intent is newer than the placement) 125; past the class screen, no allowance names it 133; far side refused (inside a fan) 23 |
| C (pcb-c-display-c8, board 2a273803757c68fb, intent 270ebb4ccf1d0e8e) | FAIL | 24 | 1 | 0 | 0 | 23 | 0 | 0 | declared, not on this board (the intent is newer than the placement) 6; past the class screen, no allowance names it 17 |
| D (pcb-d-aprs-d9, board 929bf82d2bf6eed4, intent 8d9f3b2256521b0d) | FAIL | 31 | 3 | 0 | 0 | 28 | 0 | 10 | declared, not on this board (the intent is newer than the placement) 8; past the class screen, no allowance names it 15; past its maker's own distance 2; far side refused (inside a fan) 2; the capacitor is not on the pin's net on this board 1 |
| E (pcb-e1-dock-e7, board a462ac2620b9b8d3, intent dad1163afd720b5e) | FAIL | 29 | 2 | 0 | 1 | 26 | 0 | 0 | declared, not on this board (the intent is newer than the placement) 9; past the class screen, no allowance names it 17 |
| P (pcb-p-pack-p2, board d79865e7b1aceb95, intent 12f92bd3ce7a8264) | FAIL | 4 | 0 | 0 | 3 | 1 | 0 | 0 | declared, not on this board (the intent is newer than the placement) 1 |

The verdict's counts are the gate's lines, one per declared entry: `pass` is the lines that did not fail less the justified and recorded ones. Every FAIL and justified line is in `box/run6/dec001_read.json`. The gate's own summary line per board:

- A: `intent_checks: decoupling, 56 declared: 0 pass, 0 justified deviation(s), 1 recorded with no distance to judge, 55 fail (0 with no ruled class); 0 with no ground via of their own; 0 on the side opposite their part (SMD parts 343 front, 0 back without them, so the other side is no seat)`
- B: `intent_checks: decoupling, 281 declared: 0 pass, 0 justified deviation(s), 0 recorded with no distance to judge, 281 fail (0 with no ruled class); 0 with no ground via of their own; 78 on the side opposite their part (SMD parts 431 front, 386 back without them, so the other side is a seat)`
- C: `intent_checks: decoupling, 24 declared: 1 pass, 0 justified deviation(s), 0 recorded with no distance to judge, 23 fail (0 with no ruled class); 0 with no ground via of their own; 0 on the side opposite their part (SMD parts 31 front, 135 back without them, so the other side is a seat)`
- D: `intent_checks: decoupling, 31 declared: 3 pass, 0 justified deviation(s), 0 recorded with no distance to judge, 28 fail (0 with no ruled class); 0 with no ground via of their own; 10 on the side opposite their part (SMD parts 128 front, 61 back without them, so the other side is a seat)`
- E: `intent_checks: decoupling, 29 declared: 2 pass, 0 justified deviation(s), 1 recorded with no distance to judge, 26 fail (0 with no ruled class); 0 with no ground via of their own; 0 on the side opposite their part (SMD parts 148 front, 0 back without them, so the other side is no seat)`
- P: `intent_checks: decoupling, 4 declared: 0 pass, 0 justified deviation(s), 3 recorded with no distance to judge, 1 fail (0 with no ruled class); 0 with no ground via of their own; 0 on the side opposite their part (SMD parts 48 front, 0 back without them, so the other side is no seat)`

**What the table says, read against DECOUPLING.md's own predictions.** Every board reads FAIL, and none of it is
current evidence: the placed boards predate the round 8 declarations (40 of A's 56 entries, 125 of B's 281, and 6, 8,
9 and 1 on C, D, E and P name capacitors the placed board does not carry), and the rest sit where the shelf packer put
them. The page's real-board fixtures read as it said: D12's C53 passes at 2.80 mm loop-equivalent (0.54 mm in plane
plus the 2.3 mm allowance); C15 and C16 are refused inside U7's fan box; C31 and C32 are past the TPA6132A2's own
5 mm (18.10 and 13.59 mm), so D reads FAIL at U7 as section 9 predicted. C17 is declared against U17 pin 5 since
round 8 and is not on D12 at that pin. B21's allowance reads 3.5 mm from the board file's own stackup (S-3), D12's
2.3 mm. No far-side seat on B21, C24 or D12 has a via of its own within 1.5 mm on both pads (their rails reach
pours), so every far-side line is priced at the page's 0.8 mm pitch and says so. A32, E17 and P4 read one-sided (no
SMD part on the back), B21, C24 and D12 two-sided, as section 3.3 found. No allowance line remains in any allow file,
so no entry reads `justified`, and the 8 September lines' 33 passes on B and P are gone. Board P's three class A
entries are recorded (10.11 to 14.39 mm), not passed.

## Decisions taken by this stream (authority: SESSION, under the owner's standing rule of 26 September 2026)

| id | decision | why | how to reverse |
|---|---|---|---|
| S-1 | `intent.write` refuses an entry with no ruled class or no basis, and PRINTS by name (does not refuse) a class L entry without its value floor or ESR statement and a class R entry without `same_side`. | T5 names the refusal "an entry without one" (a class and a basis). The class fields belong to each board's generator; refusing them in `intent.py` would stop board A's regeneration (8 class R entries without `same_side`) and board D's (15 class L gaps) on a tools merge, while board A is being regenerated in integration set 9 (`fnd/int10`). The gate still refuses a class R seat on the other side whatever the flag says (`far_side` reads the class). | In `intent.bypass_form`, move the `notes` into `refused` once generators A and D write the fields. |
| S-2 | A lost escape is charged to the parts whose absence ALONE clears it; when none does alone, to every part of that cause. The closure is applied only while every costed part stands where the pass measured it. | D3 and T4 close "for the part that costs it"; asking each part alone names it without guessing, and when two parts block together neither alone is the cause, so both are closed (the conservative reading: a window stays shut rather than an escape staying lost). A part that moved invalidates the measurement. | Delete `out/<stem>-escape-cost.json` beside a board, or drop the read in `bypass_search.closures`. |
| S-3 | The via allowance is computed from the fabricator's stackup row: 3.54 mm on JLC06161H-3313 (B21), 2.26 mm on JLC04161H-7628 (D12), where DECOUPLING.md 5.2 and T9's fixture say 3.7 and 2.3. | The page's 3.7 mm took a six-layer board of 1.5832 mm; the row's own layers sum to 1.5384 mm (the first author's finding F-1, in `test_decoupling_rules.py`). The four-layer row gives the page's figure. The number is the row's, never typed, so a stackup change moves it. | Correct the row in `stackup_write.py` if the fabricator's thickness is the page's; the allowance follows. |
| S-4 | The 8 September blanket line was removed from the six phase-folder copies of `bypass-allow.txt` too (the first author's change, kept), where T6 says the snapshot copies "stay as history". | The phase folders hold the committed candidates the gate reads (A32, B21, C24, D12, E17, P4), not an archive, and `parse_allow` refuses a line that names no capacitor, so the verdict is the same with or without the line; the old text is in git. `test_decoupling_rules.t_no_allow_file_carries_a_line_that_names_no_capacitor` holds every allow file to the new form. | `git checkout 73ae2f21 -- v2/ecad/pcb-*-*/bypass-allow.txt` and narrow that test to the project folders. |
| S-5 | `test_exposed_pad_vias.t_the_thermal_vias_are_asked_of_every_footprint...` now accepts `if fan_select.is_escaped(fp)` beside the old `if is_fine(fp)`. | The first author moved the selection into `fan_select` (T1); the coarse loop skips exactly what it skipped before (`is_escaped` is the old `is_fine` less the J exemption the loop also applied), and the source check failed on the spelling alone (box run3 at c1a1f28e). | Revert the test's one line if the selection moves back. |
| S-6 | `box/basis_check.py` counts a single quote as opening a passage only where no letter or digit stands before it, reads the page that follows a passage first, and recognises TI literature numbers. | The first version let the apostrophe of "maker's" open a passage and swallow the real opening quote, read "p.2" out of "(Figure 21, p.28" and named no document for SLUSC67B: 13 ELSEWHERE and several wrong pages that were the tool's, not the bases'. | The first version is in commit ee5303a5. |

## Open items, each with its next action

1. The chain does not re-place after the escape pass, so a closure acts at the next regeneration or `bypass_place.py`
   run. Next action (the integrator, in `full.sh`): after `escape.py`, when `out/<stem>-escape-cost.json` has a
   non-empty `close`, run `bypass_place.py` and `escape.py` once more, then continue to the route.
2. T7 and T8: run `apply_dec001_registry.py <checkout root>` on the integration line, then `rules_render.py`, and
   commit both files and the rendered pages together.
3. The three NOT_FOUND quotations of `BASIS.md` (A's C4, B's C71; E's C58 is a text-layer artefact and needs nothing)
   and B's C37/C38 page: each board's writer corrects the basis text in its generator.
4. Boards A and D's class fields (S-1): board A's writer adds `same_side: true` to its 8 class R entries; board D's
   writer states the ESR (or "not stated by the maker") on its 10 class L entries and the floor on C19 to C23.
5. The inventory's T3 and T4 detectors (`inventory.py`) read the wrong places; next action if the inventory is re-used:
   point T3 at `bypass_search.search`'s rotation loop and T4 at `escape_cost`.
6. Every board's next placement under these tools, on the box, with the seats read and the escape cost measured
   (FEA-006's closing evidence); the integrator's, after this branch is merged.

## What remains of FEA-006's layout-entry stage, per board

FEA-006's LAYOUT_ENTRY stage (`pcb_requirements.yaml`) asks for four things. Read on this branch at its merge of main
9147db5d:

- **The per-class requirement from the makers' own words, with its source per class.** Written in DECOUPLING.md
  sections 4 and 6; every one of the 425 declarations on the six committed intents carries a class and a basis
  (`test_intent_bypass_class`), and `BASIS.md` looks their quotations up: 3 not verbatim, 1 page wrong, 133 quote
  nothing (most say the maker states no capacitor, rule D1).
- **T1 to T10 merged with DEC-001's registry text.** This branch holds T1 to T6, T9 and T10 in the tools and T7 as an
  apply script; T8 is the render in the merge commit. Open: items 1 and 2 of the list above.
- **G1 to G14 in each generator and the circuit gaps closed, read back on the committed netlist.** `inventory-set8.json`
  reads all fourteen DONE on the set 8 netlists and intents.
- **The PI7C9X2G404SL question asked of Diodes** (board B only): drafted in `v2/docs/records/rv-dec/`, not sent; outside
  contact is not a stream's.

| board | what remains of LAYOUT_ENTRY after this branch |
|---|---|
| A | the merge of this branch, T7 applied and T8 rendered; `same_side` on its 8 class R entries (S-1); C4's quotation (BASIS.md); A changes again in integration set 9 (`fnd/int10`, U41 with C227 to C232), whose new entries its generator must class (it already stops on an unclassed one); then the next placement read under the class rules (closing evidence). |
| B | the merge, T7, T8; C71's quotation and C37/C38's page (BASIS.md); the Diodes question; the next placement (B21 predates round 8's declarations, so most of its 281 entries are not on the placed board: see the table above). |
| C | the merge, T7, T8; the next placement, with C3 and C4 out of U11's fan box. |
| D | the merge, T7, T8; the ESR statement on its 10 class L entries and the floor on C19 to C23 (S-1); the next placement, with C31 and C32 inside the TPA6132A2's 5 mm and C15, C16 and C17 out of the fan boxes they sit in on D12. |
| E | the merge, T7, T8; the next placement. |
| P | the merge, T7, T8; class A stays provisional until the qualified battery review answers Q-P19 to Q-P21; the next placement. |
