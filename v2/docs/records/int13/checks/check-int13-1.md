mergeable: no

# AI review: independent check of the integrator's own work in set 12, fnd/int13 at 005e5f5e (MESHSAT-1357)

This is an AI review, not a qualified engineering review.

**Set-up**
- Clone: a scratch clone, a shared clone detached at `005e5f5e66ddb43dc7b81a88887b136182feeb35` (checked with `git rev-parse`).
- Evidence archive: `int13-evidence-005e5f5e.tar` installed; its sha256 is `e2256dd9777dd2714f...`.
- Time: 29 September 2026, 15:08 to 15:30 CEST (from `date`).

**What I wrote**
- In this clone: only this file.
- My own scripts and outputs are in the session scratchpad (`chk13/`): `netshow.py`, `netcmp.py`, `regdiff.py`, a replay clone and the scratch readings.
- `git status` of the clone is clean apart from `CHECK.md`.
- Every rule tool ran from a scratch cwd with `VERDICT_DIR` in the scratchpad. There is one exception: `constraints_bound.py --emit` ran with cwd in the clone's `v2/ecad/tools`. It printed to stdout only, and nothing in the tree changed.

**Base**
- `main..005e5f5e` holds 67 commits on the merge base `459fe5b8`.
- `64865df1` is an ancestor.
- Main is now `77e35dd3`, which is one commit touching `EXECUTION-PLAN.md` only. `git merge-tree` onto it is clean.

**Counts: 1 blocking, 9 minor.**
- The declarations are true and settle only their own nets.
- Every pin and sheet move is proved.
- The S-117 and S-118 closes stand on their evidence, and S-120 is well formed.
- Every reading reproduces.
- The generators, `intent_checks.py`, the decisions file, the EMC sheet and HW-FW-CONTRACT.md reproduce byte for byte from the named scripts replayed on main.
- One hand-read reason is false in a way that matters: B1 below.

## Blocking items

**B1. CFL-016 was rebound to board B's new netlist on a reason that is false, and set 12's change moves its reading.**

*Where:*
- `v2/docs/records/int13/rebind_reasons_set12.py` line 15 (B["CFL-016"]).
- As written into `v2/ecad/tools/pcb_requirements.yaml`: CFL-016's two board B entries of set 12, which start at lines 13568 and 13600.

*What the reason says:* "the published contracts this conflict resolved still describe the circuit".

*What CFL-016 rests on:*
- Its acceptance: "Each named document ... describes the circuit as generated".
- Its evidence (entry 16, r8int3): "section 4b describes board B's round 8 circuit radio by radio against that netlist".
- It is bound to `v2/docs/CONOPS.md@6cb7b241...`, which set 12 does not change.

*Why the reason is false:*
- `CONOPS.md` line 412, the E22 row of section 4b, says: "its TXEN pin is driven by slot 3 and is not on the line".
- On main that was true: U12 pin 7 sat on LORA_TXEN, from slot 3.
- On set 12's netlist (3ef9b8c49a01b728), U12 pin 7 is on LORA_TXEN_G, which U546 drives as LORA_TXEN AND LORA_GO.
- LORA_GO is U544's copy of E22_EN, and E22_EN is U504's EMCON_HW AND LORA_ON.
- So TXEN is now held low by the EMCON line through hardware, and the row no longer describes the circuit as generated.

*A pre-existing gap in the same table:*
- Line 411, the RockBLOCK row, still says "its ENABLE driven only by the firmware expander U6 ... OPEN until ENABLE is forced low in hardware".
- On main, U536 (EMCON_HW AND RB_SW_IEN, since stream w4b) already drove I_EN. `PANEL.md` line 46 and V2-SPEC line 24 were corrected for it; CONOPS 4b was not.
- Set 12 adds U543 (I_EN held low below 2.79 V) and U537 to that chain, which puts the row further out of date.

*Fix:*
- Correct CONOPS section 4b's E22 row, and the RockBLOCK row, to board B's set 12 netlist.
- Re-read CFL-016 against the corrected file, rebind its CONOPS.md binding and replace the reason with a true one.
- If the correction is left for later, do not rebind CFL-016 as "No result changes". Open an S item for the two rows and let CFL-016's reading say so.

## 1. The integrator's declarations

The census (`intent_checks.rails_on_netlist`) works like this:
- A declared node is removed from "undeclared", and a rail's current is not followed past it (`reach` returns at a node).
- A node fails only when it carries the supply pins of two or more parts.

A declaration therefore settles its net and can hide nothing downstream of it. I checked each one against its parts, the makers' figures and a counterfactual run with the declaration removed.

| Net (board) | Parts on it (committed netlist) | Declared | Maker / source | Without it | Judgement |
|---|---|---|---|---|---|
| EMCON_HW (C) | R52 (330R from U9's EMCON_HW_DRV), D23 anode (cathode on TX_INHIBIT_n), U13.2, U14.6 inputs, TP11, J_PANEL.8 | node, 3.333 V | TLV75533 1 % as TX_INHIBIT_n's own node. The far ends were checked too: board B has R58 4.7k to GND and only gate inputs; board A has R102 10k to GND and U35/U37 inputs. | undecided EMCON_HW only (INCONCLUSIVE) | true; a signal line, no supply |
| IADPT (A) | U3.8 (BQ25731), R219 191k and C233 33p to GND, TP19 | node, 3.3 V | SLUSE66A PDF p.8: IADPT, IBAT, COMP1 abs max 3.6 V, recommended 0 to 3.3 V. PDF p.12: VIADPT_CLAMP 3.1 to 3.3 V, IIADPT 1 mA, CIADPT_MAX 100 pF (C233 33p inside it). | undecided IADPT, CH_COMP1 only | true |
| CH_COMP1 (A) | U3.16, R25 40.2k to CH_COMP1C, C234 33p to GND | node, 3.3 V | the same p.8 row | as above | true |
| ZBA_RXD, ZBB_RXD (B) | U540.6 / U542.6 (SN74LVC2G07 open drain, on +3V3_DEV), R536 / R537 4.7k to +3V3_ZB, U13.7 / U14.7 (E72 RX input) | node, net_volts(+3V3_ZB) = 3.3 V | an open drain and a pull-up to the rail | FAIL on these two plus the three LED nets, nothing else | true |
| LED_ACT_A1..A3 (B) | R148 / R248 / R348 1k from +3V3_CM1..3, the LED anode; the cathode on LED_nACT (CM5) | node, net_volts(+3V3_CMs) = 3.3 V | about 1 mA LED feed; the tool's "one part at most" form, with Q1C as the precedent | as above | legitimate (see m7 on its wording) |

The re-taken PWR-001 on A, B and C in scratch reproduces the committed readings apart from provenance:
- A: 92 declared nodes, 0 undecided.
- B: 159 declared nodes.
- C: 58 declared nodes.

## 2. Pins and sheets

**Independent netlist comparison against main (my own parser, parts and pin-to-net maps)**
- Board A:
  - +5 parts: C233 to C235, R219, R220.
  - Changed: C26, C27, L2, Q7 to Q10, R25.
  - No pin moved on an existing part; one net added (CH_COMP2C).
  - This equals `apply_repin_a_set12.py`'s sets, and `readback_s117.py --fets --against main` reads 35 of 35.
- Board B:
  - +56 parts: U537 to U554, R532 to R551, C668 to C685.
  - Changed: R41, R42, R238, R527, U536.
  - 21 pins moved, none of them on a connector.
- Board C:
  - +R52 and D23.
  - U9.4 moved to EMCON_HW_DRV.

**Proofs**
- The reliability inventory re-run in scratch gives these counts, equal to main's and the committed ones:
  - A: 82 / 57 / 25 / 0.
  - B: 155 / 56 / 99 / 0.
  - C: 74 / 24 / 50 / 0.
- Board A's 22 reviewed external pins are on the same nets, because no pin moved at all.
- The three final re-exports differ from their predecessors only in `source` and `date`: C at e41df395 to 8fc5954a, A and B at 33fe3c9c to 3d3e32d6, B at 3d3e32d6 to a03b047e.

**Pins name the committed netlists**
- `pcb_reliability.yaml`: A 6c40250c47195ebb, B 3ef9b8c49a01b728, C 87b69472ac83ca5a.
- `pcb_board_holds.yaml` and `pcb_port_reviews.json`: A 6c40250c47195ebb.

**Sheets**
- A.md, B.md, C.md and `rail_widths.out` differ from main only on their `read`, `netlist`, `intent` and "Intent written" lines, and those name the committed files.
- Re-emitting all six sheets gives the committed text apart from the `read` line.
- `constraints_bound.py --no-git` reads PASS.

## 3. Registry rebinds

**Structured diff of `pcb_requirements.yaml` against main (parsed)**
- 24 records changed only `evidence` and `evidence_bound_to`.
- REQ-015 and REQ-072 changed only `waits_on`: S-117 to S-120, and S-119 added.
- `open_items`: S-119 and S-120 added, S-117 removed. `closed_items`: S-117 and S-118 added.
- Titles appended:
  - S-01 and S-92: text found in `records/d4emcon/apply_registry_d4e.py`.
  - S-115: text found in `records/s117/apply_registry_s117.py` open.
- No other field or section moved.
- Every `evidence_bound_to` entry of the registry matches its file's sha at 005e5f5e (0 stale).
- Every record bound on main to a file set 12 changed carries a set 12 entry: the netlists of A, B and C, gen_sch_a and gen_sch_b, the decisions file, EMCON.md and CURRENT-EVIDENCE.md.
- Every netlist and generator rebind carries a hand reason. None took the default text.

**Reasons spot-check (24 read against the record's statement or acceptance and the netlist diff)**

| Record (file) | Reason, short | Against the record and the change | Verdict |
|---|---|---|---|
| CFL-016 (B net) | contracts still describe the circuit | CONOPS 4b's E22 row is false after U546 and U544 (B1) | FALSE, blocking |
| CON-010 (A net) | "the L2 this record's evidence names is board D's" | The only L2 in CON-010's text is EMCON.md's item L2 ("section 7's L2 and L4 rows"), the line-hold limitation, not an inductor. Board A's L2 is still not what it rests on. | FALSE as written, conclusion holds (m1) |
| CFL-005 (A net) | R102 and the slot enables untouched | EMCON_HW on A: R102 10k to GND, U35 and U37; no change | true |
| CFL-014 (A net and gen) | strap 4S and loads on VSYS unchanged | R26, R27, R17 and F1 unchanged; PANEL, CONOPS and OPERATING-ENVELOPE name no inductor, FET or frequency | true |
| CON-018 (A) | USB-C CC ESD array untouched | U31 unchanged | true |
| CON-019 (A) | outlet interlock and PA key path untouched | U26 and U30 unchanged | true |
| REQ-077 (A) | not the thermistor, gauge or shed path | the changed nets are only CH_COMP1/2, CH_COMP2C, IADPT and GND's returns | true |
| CFL-016 (A net) | Q7 named is on another board | CFL-016's Q7 is board C's (round 8 lamp) | true |
| CON-016 (A, B, C) | no clamp or rectifier changes; D23 a signal clamp on a cathode-pin symbol | D23 pin 1 K on TX_INHIBIT_n, pin 2 A on EMCON_HW; port_protect counts unchanged on A, B and C | true |
| CHO-001 (B) | no ruled device added or substituted | the added parts are all logic, resistors and capacitors | true |
| CON-003 (B) | no fabric select, OE or hub reset touched | the new parts' nets are RB_*, ZB*_*, LORA_*, SPI3_*, 5G_TPR_n and 5G_PWROFF_n only | true |
| CON-022 (B) | the gates meeting slot 3's pins run from +3V3_CM3 | U544 to U553 on +3V3_CM3, U551 to U553 driving SPI3_* pins; U554 (on +3V3_CM2) drives only 5G_PWROFF_n, with no CM5 pin on it | true |
| CON-017 (B and gen) | supervisors untouched; differs only by FEA-002 | U543 is a TPS3808, not an I/O supervisor | true |
| CFL-004 (B and gen) | WL_nDIS and BT_nDIS rows as on main | not among the changed nets; the CM5 rows are absent from the UNDECIDED list at set 12 | true |
| CON-015 and CON-025 (B) | socket, key, jacks and SIM TVS untouched; U554 on FULL_CARD_POWER_OFF# only | 5G_PWROFF_n: J_M2C2.6, Q207, R238, U220, U554 | true |
| REQ-030, REQ-032, REQ-071 (B) | the FEA-002 rows stay open, so the result stays | all FAIL on other grounds; FEA-002 is 0 of 17 closed at desk | true |
| FEA-002 (B) | d4emcon's read-back differs only on the 3 minors' values; chk12 holds | re-run on 3ef9b8c4: exactly R527, R532, R238 fail; `readback_chk12` every check holds | true |
| REQ-012, CON-021 (C) | TX lamp path untouched; the EMCON lamp still hardware | `lamp_check.py` re-run: every check holds | true |
| CFL-016 (C net) | PANEL.md's EMCON_HW row still true | U9 buffers TX_INHIBIT_n through R52 and D23 | true |
| CFL-001, REQ-052 (gen B) | no bank adoption; radios stay on their modules | E22 still on slot 3's SPI | true |
| CFL-016 (decisions) | 56 and 57 added, none changed | parsed: 56 and 57 added, ruled SESSION; 28 and 40 identical | true |

**Board B's RF-002 rows**
- On board B, 4 RF-002 rows moved from PASS to UNDECIDED against main: RockBLOCK, E22, and AW7915 slots 1 and 3. `inhibit_chain_b` went from 16/4 to 12/8, and its result stays INCONCLUSIVE.
- `records/rf2walk/README.md` lines 57, 58 and 64 attribute this to d4emcon's walk `7dc74508` (checked stream).
- None of those rows is claimed PASS by a record rebound here: the only `inhibit_chain_b` counts in the registry are historical.

**Closes**
- **S-117**, closed on the evidence its title asks for:
  - `sch_prov.current` holds for A.
  - `readback_s117` reads 23 of 23 (I re-ran it).
  - `pcb_emc.yaml`'s U3 row reads f_khz 400 with "191 kOhm" in its basis.
  - FW-A17 holds PWM_FREQ with V-A05.
  - Decision 56 is ruled.
- **S-118**:
  - The four FETs are on the netlist; `--fets` reads 31 of 31 with the base checks.
  - `PIN_ROLES` names both parts.
  - Decision 57 is ruled.
  - It leaves REQ-015's `waits_on`.
- **S-120**:
  - Well formed; it answers the s117 re-check's n1.
  - It is linked from REQ-015 and appears on REQUIREMENTS-TRACE.md line 1284.
  - `rules_lib.py requirements` reads 0 errors.

## 4. Readings

**Page runs**
- `rules_status.py` was run 3 times: exit 1, with byte-identical output. Gate NOT_READY; FAIL of 338 (PASS 195, INCONCLUSIVE 104, FAIL 39).
- The rule audits a, b, c, d, e, e5 and p equal the archive's apart from the clone path. `summary.json` is identical.
- `rules_render.py` was run 2 times: exit 0, and `git status` stayed clean.

**Checks**

| Check | Result |
|---|---|
| `rules_render.py --check` | 16 documents, 0 out of date |
| `--requirements --check` | current |
| `decisions_render.py --check` | exit 0 |
| `rules_lib.py` | 59 rules, 0 errors |
| `rules_lib.py requirements` | 144 records, 0 errors |

**Routed verdicts against main's installed evidence**
- There are 615 `routed/*.verdict.json` on each side, and 0 verdicts moved.
- 20 count changes come from the netlists: derate, edge_length, erc_gate, intent_rails, pin_map_lands and reliability on A, B and C, plus `inhibit_chain_b` and `inhibit_chain_d`, both explained above.

**Layout entry and the page**
- Layout-entry reasons: 34 on both sides (A 6, B 8, C 4, D 6, E 3, P 5, E5 2), and the rows are identical.
- CURRENT-EVIDENCE.md differs from main only in the three netlist shas.
- The page-rebind entries' stated counts match the verdicts: `inhibit_chain_a` 7 pass and 2 undecided of 9, `inhibit_chain_d` 8 and 1 of 9, `inhibit_chain_c` 6 of 6, and `pack_protection` 3 of 63 failed.

**Tests (from scratch)**
- `test_requirements`, `test_rails_census`, `test_constraints_bound`, `test_rules_registry`, `test_decision_register`: 124 passed and 2 failed.
- Both failures are in `test_rails_census` and need the held FET datasheets, which a clean clone lacks (m5).

## 5. Content outside the checked streams and the named scripts

- I replayed on main, in a scratch clone:
  - `apply_b_d4e`, `apply_c_d4e_f1`, `apply_emcon_hw_node_c`, `apply_b_chk12`.
  - The five s117 generator and document scripts.
  - `apply_census_nodes_set12`, `apply_b_chk12_led`, `apply_census_nodes2_set12`.
- The replay gives `gen_sch_a/b/c.py`, `intent_checks.py`, `pcb_decisions.yaml`, `pcb_emc.yaml` and `HW-FW-CONTRACT.md` byte-identical to 005e5f5e.
- Every other changed file belongs to a named stream or step:
  - `tx_inhibit.py` and its tests: rf2walk.
  - EMCON.md: d4emcon and rf2walk2/3.
  - `.gitignore` and `sources.txt`: s117's held-back sheets.
  - Schematics, netlists, intents and provenance: the box regeneration.
  - Verdicts: the re-take.
  - Rendered pages, the pins and sheets, and the registry.
- Nothing unexplained found.

## Minor items

- **m1. CON-010's board A reason names the wrong L2.**
  - Where: `rebind_reasons_set12.py` line 42, written at `pcb_requirements.yaml` line 10347.
  - Fix: append an entry saying the L2 is EMCON.md's line-hold item, and correct the reasons file.
- **m2. Board A's netlist entries name the wrong change.**
  - Where: `apply_rebind_after_circuit.py` line 73. All eight board A netlist entries (CFL-005, CFL-014, CFL-016, CON-010, CON-016, CON-018, CON-019, REQ-077) say "the circuit change of stream d4emcon's FEA-002 remedies was compared ...".
  - Board A's change is S-117's.
  - Fix: make the change's name a parameter and add a correcting entry.
- **m3. The final page-rebind entries describe the branch incompletely.**
  - Where: CON-010 and REQ-044, written by `apply_rebind_page_set12.py`.
  - They describe the branch without S-117, board A's regeneration, the census nodes or the S-117 and S-118 closes.
- **m4. The generator entries leave out one change and the line shifts.**
  - The second-pass gen_sch_b entries list "the check's minors, the census nodes" and not the LED feed loads (`apply_b_chk12_led.py`).
  - Neither generator entry states the line shifts: gen_sch_a +35 after line 857 and +55 after line 907.
  - Older entries cite later lines, for example CON-019 `:1237-1245` and `:1291-1304`, CON-018 `:1200-1210` and REQ-077 lines 1262 and 1267. Those citations are dated to their shas, but a note would stop them being misread.
- **m5. The box re-take ran without the held FET datasheets.**
  - Board A's committed `intent_rails` reading records `sha256_16: None` for documents 7 and 8 (the held CSD17577Q5A and CSD17578Q5A sheets), and `test_rails_census` fails 2 tests in a clone without them.
  - The int13 worktree fetched them at 15:19, after the re-take.
  - Fix: run `records/s117/fetch_held_back.py` on the box before a re-take, or state the precondition in the int13 record.
- **m6. `apply_repin_bc_set12.py` contradicts itself.**
  - Line 13 says it refuses a second run.
  - Lines 10 to 11 and line 77 leave an already-pinned board as it is and write the file again.
- **m7. Two wording points in the new declarations.**
  - The LED_ACT_A* basis says "no part takes its supply from it", but the LED's forward current comes from that net. The node form is still right (Q1C is the precedent).
  - The ZBA/ZBB and LED nodes take v_max from the rail's nominal 3.3 V, not the 3.46 V upper figure PCB-BRING-UP prints. This matches precedent, and no part on them is near a limit.
- **m8. S-01's appended text names an older read-back.**
  - S-01's text (line 2543, from d4emcon's `after` phase) names d4emcon's read-back on board B at 5b89d5ef, before the check's minors.
  - On the final netlist that read-back fails the three values changed on purpose, and `readback_chk12` carries them. A dated pointer to readback_chk12 would keep the item true.
- **m9. `closed_by` on S-117 and S-118 overstates what 230fdd65 did.**
  - Both read "committed by 230fdd65". The netlist 6c40250c was first committed at 3d3e32d6; 230fdd65 carries it but did not commit it. "Carried at" would be exact.
