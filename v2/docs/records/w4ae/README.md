# Stream w4ae: HOT-R1 on boards A and E, and board E's fan flyback sheet (MESHSAT-1357, 27 September 2026)

Author stream w4ae, worktree `fnd/w4ae` from main `91894cd7`. Prototype design: nothing here has been built, ordered,
powered or measured. Engineering choices are the session's under the owner's standing rule of 26 September 2026, each
with its reason and its reversal; nothing here is the owner's. File this folder as `v2/docs/records/w4ae/`.

## What the stream owns (its own files, in the worktree)

| File | Change |
|---|---|
| `v2/ecad/tools/gen_sch_e.py` | HOT-R1's driver: U10 pin 30 (GPIO19) on `HOT_R1_G`, Q11 (2N7002, the C8545 part of Q8 to Q10) with its drain on `BLK_SPARE` (J_BLK pin 12, TP7), R58 100 k gate pull-down (C25803); J_BLK's value names pin 12; D7 and D8 carry their order code C51897884; FAN1_SW and FAN2_SW declared nodes at 17.35 V; the section list |
| `v2/ecad/tools/gen_sch_a.py` | HOT-R1's pull-up: R216 10 k from `DOCK_SPARE` (J_DOCK pin 12, U27 pin 18 = P1.5, TP21) to +3V3, written as R110 is; J_DOCK's value names pin 12; the section list; the comment traces H2 to `PI_KILL` |
| `v2/ecad/tools/boards/a.json`, `boards/e.json` | signal classes (`DOCK_SPARE` ahead of `*_SPARE`, `BLK_SPARE`'s basis, `HOT_R1_G`), and the line declared a safety line on both boards (A listens, safe high by R216; E is its source) |
| A and E schematic, netlist, provenance and intent | regenerated on the KiCad box with main's chain (`handover_exports.py regen`, PHASE A65 and E42P) |
| `v2/vendor/zhengxin/zhengxin-ss12-ss120-c51897884.pdf` | the maker's sheet of D7 and D8 as JLCPCB serves it (the parts record's data manual), sha256 `a9f62a305c3afb75` |

## Integration order (`integrate.sh <worktree> <tree>`, run whole in a scratch clone of main `62f26a44`)

1. The files above. 2. This folder as `v2/docs/records/w4ae/`. 3. `apply_registry.py <tree>`: takes the next two free SC
numbers (SC-64 and SC-65 on `62f26a44`), closes S-57, updates S-76, REQ-077 FAIL to INCONCLUSIVE, twelve rebinds; writes
`ids.json`. 4. `edit_docs.py <tree>`: CONOPS, HW-FW-CONTRACT, PANEL, IF-AE-DOCK, vendor sources, grade sources, EQ-22.
5. `post_docs_registry.py <tree>` before the commit (it reads HEAD). 6. `rules_lib.py requirements` (144 records, 0 errors,
0 warnings in the dry run), `rules_render.py --requirements` and `--check`. Then the parts stream re-runs
`v2/docs/parts/grade_check.py` (GRADE-CHECK.md was already behind main's board B lines; this row goes TBD to INSIDE (TJ)),
and the A and E readings are re-taken in a clean clone (`retake_schematic_phase.py --in-place --routed`) before
`rules_status.py`/`rules_render.py`.

| Draft | Owner of the file it edits | Why |
|---|---|---|
| `apply_registry.py` | `pcb_requirements.yaml` | SC for HOT-R1 as drawn (closes S-57), SC for D7/D8 and the fan nodes (S-76, board E's half), REQ-077's desk reading, the twelve records bound to the changed files |
| `edit_docs.py` conops | `v2/docs/CONOPS.md` (BASELINED) | section 4c's HOT-R1 paragraph said "owed" and "FAIL until drawn"; a post-baseline revision note says what changed and that no need, mode, trigger or decision did; whether the baseline needs a re-check is the layer 2 owner's call |
| `edit_docs.py` hwfw | `v2/docs/HW-FW-CONTRACT.md` | FW-C13, FW-C14, FW-E10 go OWED to DRAWN; FW-C14 gains the EXP_INT service and a once-a-second poll, FW-E10 the watchdog bound (below) |
| `edit_docs.py` panel | `v2/docs/PANEL.md` | GPIO24 and U27's row name HOT-R1 on P1.5 (S-57 named PANEL.md) |
| `edit_docs.py` interfaces | `pcb_interfaces.yaml` IF-AE-DOCK | a `hot_r1` entry for pin 12; the pin map and aliases are unchanged |
| `edit_docs.py` sources, grade | `v2/vendor/sources.txt`, `v2/docs/parts/grade-sources.yaml` | the new sheet's provenance line; C51897884's maker and Tj range |
| `edit_docs.py` eq | `v2/docs/handover/ENGINEERING-QUESTIONS.md` | EQ-22's index row, attempts and next action |
| `post_docs_registry.py` | `pcb_requirements.yaml` | CONOPS's needs pin and the readings bound to CONOPS, PANEL and grade-sources |
| `hot_r1_trace.py` | record | walks the H2 path hop by hop on the netlists and the contracts; `readings/hot_r1_trace-*.txt` |
| `parity/`, `readings/`, `jlc/` | records | the regeneration proof, the before and after readings, the part identity readings |

## How H2 reaches PI_KILL, read from the netlists (`readings/hot_r1_trace-candidate.txt`, every hop found)

E `U10` pin 30 (GPIO19; U10 is the gauge's only SMBus host) on `HOT_R1_G` to `Q11`'s gate (`R58` to GND); `Q11`'s
source on GND, drain on `BLK_SPARE` = `J_BLK` pin 12; IF-AE-DOCK pin 12 to A `J_DOCK` pin 12 = `DOCK_SPARE`, on `U27`
pin 18 (P1.5) with `R216` to `+3V3` (U27's VCC); an edge sets `U27` pin 1 = `EXP_INT` (R110; also U28 and J_MEZZ1) out
on `J_AB1` pin 13, board B's `EXP_INT` to `J_PANEL` pin 6, board C's `U3` pin 36 (GPIO24); the panel controller reads
U27 over SDA and SCL (A `J_AB1` 11 and 12, B `J_PANEL` 4 and 5, C `U3` pins 2 and 3 = GPIO0 and GPIO1); on a held low
it drives `U3` pin 30 (GPIO19) = `PI_KILL`, `J_PANEL` pin 25, board B (Q103, Q203, Q303 drains also on it), `J_AB1`
pin 10, A's `PI_KILL` on `Q1`'s gate (R5 1 k to GND); `Q1`'s drain `KILL` = `U1` (LTC2954) pin 8 (R4 to +3V3); `U1`
pin 6 `RAIL_EN` on `U12`'s EN (the +3V3 buck) and every converter's enable. Power without a compute module: E's U10 on
`+3V3_E6` from U13 and U12, whose EN is `CELL_F`; A's U27 on `+3V3` (U12, RAIL_EN); C's U3 on C's `+3V3` from U5, fed
from `J_PANEL` 1 and 2 = B's `PANEL_5V` behind F1 from `+5V_DEV` (J_5V_DEV, IF-AB-POWER) = A's U7, enabled by
`DEV_EN` (U27 P0.7 with R42's pull-up). No CM5 part is on any board B conductor of the path. On main's netlists
(`91894cd7`, identical at `62f26a44`) the walk stops at U10 pin 30, with no pull-up on DOCK_SPARE.

The path is FIRMWARE in two controllers (SC-49: a control, not a protection). Two firmware bounds found while drawing
it, drafted into HW-FW-CONTRACT: `EXP_INT` is wired-OR across A, B and C, so the panel must read U27's port 1 on every
edge (TI SCPS131J 8.4.1 and its errata 8.4.1.1) and poll it once a second; and a sensor controller that hangs with
GPIO19 high holds the line low until its watchdog resets it, so its watchdog period stays under FW-C14's 3 s held-line
rule. Whether a firmware-free stage must stand behind the stop stays S-58 (EQ-23).

## Parity (`parity/`)

main's generators reproduce main's A and E files (PARITY; `net_compare.py` no difference); the candidate generators
reproduce their own files (PARITY); candidate against main, by the independent comparison of every component and every
net's pins (`v2/docs/records/w3de/net_compare.py --expect`): ONLY THE EXPECTED CHANGES. A: R216 added (DOCK_SPARE, +3V3),
J_DOCK's value. E: Q11 and R58 added, U10 pin 30 from no connection to the new net HOT_R1_G, D7 and D8's LCSC field,
J_BLK's value. Intent: A unchanged; E adds the nodes FAN1_SW and FAN2_SW. ERC: warnings only (the new symbols'
lib_symbol_issues and layout-position warnings), erc_gate PASS. BOM: A's 10 k line gains R216; E adds Q11 and R58 and
D7/D8 carry C51897884.

## Readings (`readings/`, taken with `retake_schematic_phase.py --verdict-dir` on scratch commits of the box clone)

| Rule | A before | A after | E before | E after |
|---|---|---|---|---|
| PWR-001 (intent_rails) | PASS of 35 | PASS of 35 | INCONCLUSIVE of 16 (FAN1_SW, FAN2_SW undecided) | PASS of 16 (0 undecided, 15 declared nodes) |
| PWR-002 (power_sequence) | PASS of 34 | PASS of 34 | PASS of 15 | PASS of 15 |
| INT-001 contracts (check_contracts, interfaces) | PASS of 99 / PASS | same | PASS of 99 / PASS | same |
| SCH-004 (safe_lines) | PASS of 6 | PASS of 7 (DOCK_SPARE: pull-up R216, reader U27.18) | PASS of 1 | PASS of 2 (BLK_SPARE source) |
| SCH-001 (erc_gate) | PASS | PASS (1556 warnings, +2) | PASS | PASS (378, +3) |
| SCH-005, CMP-001, PWR-003, TRN-001, CLK-001, SI-001, RF-002 | unchanged | unchanged | unchanged | unchanged |

RF-002 on A reads FAIL before and after (EQ-25, W3T-F1, board C's stream); SI-001 INCONCLUSIVE and CLK-001 on A
INCONCLUSIVE before and after. REQ-077 (registry, desk): FAIL to INCONCLUSIVE; it cannot read PASS while FEA-004 holds it.

## Tests (in the scratch clone after `integrate.sh`, final files; `readings/tests-final.log`)

`run.py` test_block_contract test_board_file_format test_energy_chain test_kelvin_check test_pin_map_lands
test_rails_census test_sch_prov test_order_codes test_netlist_provenance test_rail_loads test_sensitive_nodes
test_safe_lines test_requirements test_rails_netlist test_smbus_lead_contract test_signal_class test_tx_inhibit
test_edge_length test_certify_identity test_certify_mismatch test_interfaces test_contract_attribution
test_stale_netlist test_retake_schematic_phase test_switch_list test_review_packet test_evidence_class
test_handover_pack test_footprint_library test_board_gates: 570 passed, 0 failed, 40 skipped (pcbnew fixtures).
In the worktree alone (main 91894cd7 plus the stream's own files, before apply_registry.py) the requirements
validator refuses the twelve stale bindings and REQ-077's, which is what apply_registry.py answers. `claims_check.py`
on CONOPS, PANEL and the trace page: nothing of this stream flagged.

## Ids taken at the r8int6 integration (corrected at integration)

The registry script ran at the r8int6 integration of 27 September 2026 (set 6 of the handover), where other branches had taken the numbers this record names as drafted; the ids it took there, read back from the registry by each record's own text: SC_HOT_R1 is SC-70; SC_FAN is SC-71; S_PI_KILL is S-84. Where this record names another number for one of them, the id here is the one the registry holds.
