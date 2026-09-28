# Stream w5si2: SI-001's edge rates made integrable without publishing a model, and board C (layer 9, MESHSAT-1357)

Written 28 September 2026 on branch `fnd/w5si2`, base `231b52b4` (stream w5si squashed onto the set 6 integration
line). Prototype design work: nothing here has been built, ordered or measured. No reading on this page is a PASS.
The checks this stream answers are two AI reviews (the first lens "edges" of 27 September and the drafts check of 28
September 2026); neither is a qualified engineering review. This page continues `v2/docs/records/w5si/w5si-record.md`
and supersedes its section 12.

## 1. What was closed

| Id | What it asked | How it is closed | Where |
|---|---|---|---|
| B1 | the stream must work with the models present and absent, and say which | a tracked manifest pins each model; the tool reads a model only when the file present is the file pinned; an absent model decides nothing; the reading records the state | `v2/vendor/ibis-manifest.yaml`, `tools/ibis_manifest.py`, `tools/ibis_fetch.py`, `tools/edge_length.py`, two drafts for `rules_status.py` |
| B2 | the coverage draft wrote typed sentences that were false with the models withheld | every count, reason and the models' state is read from the readings of the tree the draft runs on | `apply_coverage_si001.py` |
| B3 | the decisions draft cited a stale digest and line | the citation is derived from the tree and the facts it stands for are asserted | `apply_decisions_w5si.py` |
| M1 | CFL-016's binding moves with the decisions file | the rebind is part of the decisions draft, with a re-read sentence | `apply_decisions_w5si.py` |
| M2 | the coverage draft leaves two generated pages stale | the draft's output says `rules_render.py` is owed and names the pages | `apply_coverage_si001.py` |
| M3 | the test suite failed in a clean clone | the real-tree test is split: what needs the models is skipped with the reason, and a test asserts the fail-closed state in every state | `tools/tests/test_edge_length.py` |
| M4 | no draft asserted its preconditions | every draft checks them first and refuses in one sentence with exit code 2 | `_apply.py`, all seven drafts, `selftest.py` |
| M5 | four models had only an owed line | each has its address and full sha256 in the owed line, which says what is owed: a part entry, the parts stream's | `apply_sources_yaml_ibis.py` |
| M6 | the vendor lines said every file carries a redistribution notice | each line and the record say which wording each file carries | `v2/vendor/sources.txt`, `vendor-status.txt`, `w5si-record.md` 12.1 and 12.5 |
| M7 | "138 by a maker's figure" | 74 by IBIS cells and 64 by the USB 2.0 class records, counted by the draft; "AI review" | `apply_coverage_si001.py` |
| M8, first lens M5 | a [Ramp] cell its own V-t table contradicts | the reader flags it; the pin takes the instantaneous bound | `tools/ibis_read.py`, decision ER-D16 |
| M9 | netlists named by phase directory | kept, and said in the draft's output with what `--refresh` does | `apply_rules_status_config_inputs.py` |
| M10 | the BOB finding's stale pointers | both revisions named, the facts stated once | `w5si/F-BOB-common-mode-termination.md` |

## 2. For the integrator: the drafts, in this order

Each refuses a second run, refuses in one sentence when a precondition does not hold, and writes last. `--dry-run`
writes nothing. `--root <tree>` runs on another tree. All seven were run in this order, then a second time, on two
scratch views of this branch (models present, models absent): `readings/drafts-applied-in-scratch.txt`.

| Order | Draft (under `v2/docs/records/w5si/apply/`) | Changes |
|---|---|---|
| 1 | `apply_rules_status_config_inputs.py` | `rules_status.CONFIG_INPUTS["edge_length.py"]`: 6 inputs become 64; the manifest is declared, no model is |
| 2 | `apply_rules_status_pinned_models.py` | `rules_status.py`: `PINNED_INPUTS`, `_recorded_model`, `_pinned_state`; refuses until 1 is applied |
| 3 | `apply_sources_yaml_ibis.py` | `v2/vendor/SOURCES.yaml`: 9 document rows and 1 owed line, read from the manifest |
| 4 | `apply_board_b_declarations.py` | `boards/b.json` (3 entries) and `gen_pcb_b3.py` PATTERNS (40 become 41); unchanged but for its refusals |
| 5 | `apply_board_c_declarations.py` | `boards/c.json`: four entries after `EMCON_HW` |
| 6 | `apply_coverage_si001.py` | `pcb_rules_coverage.yaml`, record SI-001: note and remediation action. After 4 and 5, so its counts are the final tables' |
| 7 | `apply_decisions_w5si.py` | `pcb_decisions.yaml`: seven SESSION rows from the next free number; `pcb_requirements.yaml`: CFL-016 rebound |

**Before any of them:** commit `tools/pcb_edge_rates.yaml`, `v2/vendor/ibis-manifest.yaml` and
`v2/docs/records/w5si/readings/edge-search.txt` (they are on this branch). **Never commit a model.**

**Owed after them**, each said by the draft that causes it:
- `rules_render.py` (PCB-GOLDEN-RULES.md and PCB-GAP-REGISTER.md) and `rules_render.py --requirements`
  (REQUIREMENTS-TRACE.md). Until the second, two tests of `test_requirements` refuse the stale page; they pass
  before the draft and were seen failing after it in both scratch views, for that reason only.
- `decisions_render.py` (OWNER-DECISIONS-OPEN.md).
- SI-001 re-taken on all six boards together with `retake_gate.sh`, and the other readings of boards B and C that
  declare their board table.
- The models fetched where the re-take runs: `python3 v2/ecad/tools/ibis_fetch.py --fetch`, then `--check`.

## 3. The three states of the models

| State | What the tool does | What rules_status does (after drafts 1 and 2) |
|---|---|---|
| present, the file pinned | reads the model; records it by sha under `inputs.model_N` | BOUND |
| absent | decides nothing from it: each waiting net is UNDECIDED, reason kind MODEL_ABSENT, naming the file; `inputs.model_state` says ABSENT or PARTIAL; the record's own `edge_ns` is never used in its place | a reading taken WITH the model stays BOUND (the pin dates it); a reading taken without it is BOUND while the model is absent, and CONFIG_CHANGED, saying why, once the model is there |
| present, not the file pinned | decides nothing from it and says so; state DIFFERS | CONFIG_CHANGED |

The fetch script was proven once by hand into a scratch folder on 28 September 2026 16:15 UTC: all thirteen came from
the makers' own addresses and every sha256 was the one pinned (`readings/ibis-fetch-scratch-2026-09-28.txt`). st.com,
which refused this host on 27 September, answered it. The script tries the Internet Archive where a maker refuses.

## 4. SI-001 on the six boards, both states

Taken in scratch outside any tree, on the integration line's netlists, with the seven drafts applied in the scratch
view. Data file sha256/16 `0689086680f7a4a4`. Listings: `readings/si001-six-boards-models-present.txt` and
`-absent.txt`.

| Board | Non-slow | Models present: figure, bound, undecided | Models absent: figure, bound, undecided (no declaration + model absent) |
|---|---|---|---|
| A | 120 | 7, 75, 38 | 6, 71, 43 (38 + 5) |
| B | 562 | 103, 451, 8 | 30, 142, 390 (8 + 382) |
| C | 33 | 4, 29, 0 | 4, 22, 7 (0 + 7) |
| D | 47 | 20, 19, 8 | 20, 16, 11 (8 + 3) |
| E | 41 | 4, 37, 0 | 4, 37, 0 |
| P | 20 | 0, 5, 15 | 0, 5, 15 |
| all | 823 | 138, 616, 69 | 64, 293, 466 (69 + 397) |

Of the 138 decided by a published figure with the models present, 74 are by a maker's IBIS model and 64 by the USB
2.0 specification's class records; with the models absent only the 64 remain. Layout-bound: 324 (43 held by a
figure, 281 BOUND_DECIDES) with the models, 227 (2 and 225) without. **Every board reads INCONCLUSIVE in both states.**

## 5. Board C's four nets (decision W5SI2-D1)

Netlist `v2/ecad/pcb-c-display-c8/out/pcb-c-display.net`, sha256/16 `3fddbb3edcd4248a`. None of the four has a
connector, a switch or a test point on it. All four follow the EMCON locking toggle, moved by a person.

| Net | Driver, and through what | The driver's fastest edge, from its maker | Reader |
|---|---|---|---|
| EMCLAMP_Y | U14 pin 4, SN74LVC1G57DBVR wired as a NOR of TX_INHIBIT_n and EMCON_HW | **0.221 ns**, TI's IBIS model SCEM292 Rev. A, `[Model] LVC1G57_OUT_33 [Ramp] dV/dt_f max`, cell `2.18/2.21E-10`, which its own V-t table holds. The datasheet SCES414P (revised November 2016, sha256/16 `078364de617898af`) prints no output transition: p. 3 "Logic output", p. 6 propagation delay only, 1.5 ns minimum | R48 |
| EMCLAMP_G | the same, through R48 (100R); R49 (10 k) to GND | the same 0.221 ns at U14's pin | Q7's gate (Si2300DS), the amber EMCON lamp's sink |
| EMCON_RD | U13 pin 4, 74LVC1G17 Schmitt buffer fed by EMCON_HW | **not published.** Diodes DS35124 Rev. 8-2 (sha256/16 `029f345a1e7be917`): p. 1 "standard push-pull output", p. 6 propagation delay only, 0.7 ns minimum. The instantaneous bound stands for it | R46 |
| EMCON_RD_R | the same, through R46 (1 k) | the same; and the RP2040 (datasheet build 2025-02-20, sha256/16 `be56fbb75ba0ae9e`, p. 303: a slew bit, no transition) publishes none | RP2040 GPIO21, an input by contract FW-C07 |

**The class: LOW_SPEED_OR_DC, on what the nets carry.** The rule's own definitions:
- `tools/signal_class.py`: "LOW_SPEED_OR_DC an enable, an inhibit, a sense line, a thermistor, an analogue level, a
  rail's feedback. There is no edge to speak of. The question that remains is whether a return path EXISTS at all".
- `tools/edge_length.py`: "LOW_SPEED_OR_DC is not asked for an edge. It is the class this project declares, with a
  basis per entry, for an enable, a sense line or a level".

These four are copies of an inhibit. Nothing samples them on their edge: one ends at a FET's gate behind 100R, the
other is read as a level by firmware behind 1 k. The line they copy, EMCON_HW, is declared LOW_SPEED_OR_DC on boards
A, B and C, as are TX_INHIBIT_n, board A's `*_TXOK` and board B's EMCON_SUP.

**What the class does not say.** The drivers are fast, and each entry's basis says so. The class is not a claim that
these nets have no edge. It rests on content.

**A non-slow class would not pass the board either.** Computed by the draft on the tree it runs on:

| Board C | Slow | Figure | Bound | Undecided | Answered | Layout-bound | Result |
|---|---|---|---|---|---|---|---|
| before, models present | 97 | 4 | 29 | 4 | 10 | 23 | INCONCLUSIVE |
| after, LOW_SPEED_OR_DC, present | 101 | 4 | 29 | 0 | 10 | 23 | INCONCLUSIVE |
| had they been CLOCKED_DIGITAL, present | 97 | 6 | 31 | 0 | 12 | 25 | INCONCLUSIVE |
| before, models absent | 97 | 4 | 22 | 11 | 10 | 16 | INCONCLUSIVE |
| after, LOW_SPEED_OR_DC, absent | 101 | 4 | 22 | 7 | 10 | 16 | INCONCLUSIVE |
| had they been CLOCKED_DIGITAL, absent | 97 | 4 | 24 | 9 | 10 | 18 | INCONCLUSIVE |

In the class not taken, EMCLAMP_Y and EMCLAMP_G are answered by R48 (inside the 10 to 150 ohm series screen), and
EMCON_RD and EMCON_RD_R are layout-bound and decided by a bound, because R46's 1 k is outside the screen.

**To reverse:** change `class` to CLOCKED_DIGITAL in the four entries of `tools/boards/c.json`, correct their basis,
and re-take SI-001.

## 6. Board C's 23 layout-bound nets: what is proposed for each

**SI-001 passes a board at the schematic phase only when no net is left to the layout.** A maker's model alone does
not do that: a net with a published edge is still layout-bound, held by a figure, unless its critical length is past
the board's corner-to-corner run. On board C that run is 572 mm (344 by 228), which at k 6 and 7.154 ps/mm needs an
edge of 24.6 ns or slower. So every net below needs an ANSWER: a series resistor, an impedance target, or an
`edge_allow` declaration. No board table of this project carries an `edge_allow` entry today.

Nothing below is applied. A series resistor is a draft for the owner of `gen_sch_c.py`.

| Nets | What governs them | Proposed remedy | What it rests on | Closable at the desk |
|---|---|---|---|---|
| EPD_CS, EPD_DC, EPD_SCL, EPD_SDA (4) | the RP2040's GPIO5, 4, 2, 3; the e-paper's controller beyond J_EPD | **a series resistor of 33 ohm at the RP2040's pin** | RP2040 datasheet Table 625 (PDF p. 617): at IOVDD 3.3 V, VOH 2.62 V minimum and VOL 0.5 V maximum at the set drive current. At the default 4 mA the pad's resistance is at most 170 ohm sourcing and 125 ohm sinking. The maker prints no minimum or typical, so the value cannot be computed to a match; 33 ohm is a proposal inside the screen, and the pad's own resistance only adds to it | **yes**, by a circuit draft |
| SWCLK, SWDIO (2) | a bench probe on TP1; the RP2040's SWD pin and TP2 | **`edge_allow`**, reason: the debug port is driven only while a bench probe is attached, in no state of the kit's use | the reason does not depend on the unknown edge | **yes**, by declaration |
| EPD_SW (1) | the e-paper boost converter's switch node | **the net class SW** in `gen_pcb_c3.py` PATTERNS | the first author's finding F-Q1, item 5: its 32 siblings on the set already have it. A power class takes the net out of the signal set | **yes**, by the layout generator's owner |
| Q3_G (1) | the TX lamp's FET gate, behind R37 (1 k) from TR_APRS, R38 (100 k) to GND. TR_APRS is driven by board D's U18 (a 74LVC1G34, behind R48 on board D) and read by the RP2040's GPIO23 | **a signal-class entry `Q3_G`, LOW_SPEED_OR_DC, ahead of the glob `Q?_G`** (proposed W5SI2-D2) | the same reasoning as section 5: TR_APRS is already declared "a static level"; the glob `Q?_G` was written for the PWM gates. Neither maker of a 74LVC1G34 held (TI, Diodes) publishes an output transition, so the driver's fastest edge is not known. With the models absent the net waits on TI's SN74LVC1G00 model (board A's U30) only to learn that U30's pin on the net is an input | **yes**, by declaration |
| QSPI_D0 to D3, QSPI_SCLK, QSPI_SS (6) | the RP2040's QSPI pads and the W25Q16JV, neither with a published edge | **none at the desk.** A series resistor is against the maker's guidance | Hardware design with RP2040 (build 20/08/2026, sha256/16 `51c4f430153fcdbf`), p. 10: "the QSPI pins of RP2040 should be wired directly to the flash, using short connections to maintain the signal integrity" | **no** |
| HB1, HB2, HB3 (3) | board B's FET drains and STM32H743 pins, beyond J_PANEL; the RP2040 reads | **a series resistor at the driver, on board B**, then an `edge_allow` on board C naming it | board C's netlist does not show board B's parts, and a resistor at the receiving end terminates nothing | **no**, not on board C alone |
| SCL, SDA, EXP_INT (3) | the kit bus across boards A, B, C and D: the RP2040, VEML7700, BQ25731 and ATECC608B publish no fall; the PCA9555's INT pin is flagged | **series resistors at the devices' pins**, a kit-wide decision | UM10204 Rev. 6 (sha256/16 `b7619700e8bb9dd4`), section 7.3, p. 58: "series resistors (Rs) of, for example, 300 Ω can be used for protection", and "designers must add the additional resistance into their calculations for Rp and allowable bus capacitance" | **no**, four boards and the bench item V-K01 |
| XIN, XOUT, XOUT_R (3) | the 12 MHz crystal's nodes | **`edge_allow` naming CLK-001**, once CLK-001 states the node's longest length | Hardware design with RP2040, p. 11: "Try and keep the layout as short as possible". SI-001's bound asks a crystal node the wrong question | **no**, CLK-001's owner first |

What the QSPI nets need: a length limit for them that a layout gate holds, then an `edge_allow` naming it. With no
published edge the limit cannot come from l = t_r / (k t_pd). Winbond's model is a browser fetch; Raspberry Pi
publishes none, and asking for one is outside contact, the owner's to send.

**What SI-001 would read on board C after the four desk remedies**, simulated outside every tree
(`tools/board_c_remedies.py`, `readings/board-c-remedies.txt`):

| Step, cumulative | Models present: undecided, answered, layout-bound | Models absent: undecided, answered, layout-bound |
|---|---|---|
| 0 the tree as it is | 4, 10, 23 | 11, 10, 16 |
| 1 the four EMCON copies declared (W5SI2-D1) | 0, 10, 23 | 7, 10, 16 |
| 2 Q3_G declared slow | 0, 10, 22 | 6, 10, 16 |
| 3 EPD_SW in net class SW | 0, 10, 21 | 6, 10, 15 |
| 4 SWCLK, SWDIO in `edge_allow` | 0, 12, 19 | 6, 12, 13 |
| 5 33 ohm at the four e-paper pins | 0, 20, 15 | 6, 20, 9 |

**After all of them board C still reads INCONCLUSIVE.** With the models present 15 nets hold it: EXP_INT, HB1 to
HB3, the six QSPI nets, SCL, SDA, XIN, XOUT, XOUT_R. With the models absent 9 are layout-bound (the six QSPI nets
and the three crystal nodes) and 6 are undecided, each waiting on a model of board A's or board B's parts.

**For board C's layout-entry packet:** SI-001 cannot be stated PASS. It can be stated INCONCLUSIVE with 8 of its 23
nets closable at the desk and 15 named with what each needs.

## 7. Decisions taken (authority SESSION)

Under the owner's ruling of 21 September 2026 and his standing rule of 26 September 2026. None is the owner's.
`apply_decisions_w5si.py` files ER-D16, ER-D17 and W5SI2-D1 with the first author's four.

| Id | Decision | Reason | To reverse |
|---|---|---|---|
| ER-D16 | a [Ramp] cell is held to its model's own V-t table: dV 50 to 70 percent of the swing, dt within 25 percent of the table's 20 to 80 percent time; a pin with a contradicted cell has no figure | measured on the 13 models: of 585 driven cells 537 have a table, 522 hold, 15 do not, and the tolerances sit in the gap. It can only take a figure away | `ibis_read.RAMP_DV`, `RAMP_DT` |
| ER-D17 | the models are pinned by a tracked manifest and are not in the repository; an absent model decides nothing | five headers forbid distribution, eight grant nothing, the repository is mirrored publicly, publication is the owner's | the owner publishes; drop the ignore rule |
| (in ER-D16) | a flagged pin takes the instantaneous bound, its net is not left undecided | ER-D8 already gives that bound to a driver with no published minimum | `edge_length.pin_candidates` |
| (in ER-D16) | a pin is flagged when ANY of its admitted driven cells is contradicted | leaving the cell out and reading the next gives a slower figure than the table may hold (TMP117's SDA: 44 ns where its table shows 34 ns) | `ibis_read.pin_edge` |
| W5SI2-D1 | board C's four EMCON copies are LOW_SPEED_OR_DC | section 5 | section 5 |
| W5SI2-D2, PROPOSED, not filed | Q3_G is LOW_SPEED_OR_DC | section 6 | not applicable |
| (draft design) | `apply_board_b_declarations.py` does not require the stream to be merged | it needs only the two files it changes | add `AP.need_stream` |
| (draft design) | the coverage draft applies with the models absent and says so, it does not refuse | the task asks that it say which state; its output repeats it | add a refusal on `absent` |

ER-D16 changed two records: TI-PCA9555 from 0.121 to 5.89 ns and TI-TMP117 from 7.6757 to 12.6129 ns. Each now
states its fastest pin that has a figure and names its flagged pin. No count of any reading moved: both pins sit on
nets a bound already decided.

## 8. What was run

Single test files only, from `v2/ecad/tools/tests`. No gate, no `rules_status.py`, no renderer in any tree. Nothing
on the rented box, nothing spent. The models were moved aside inside the worktree for the absent state and moved
back; `ibis_fetch.py --check` reads 13 present.

| What | Models present | Models absent |
|---|---|---|
| `run.py edge_length`, in the worktree | 42 passed, 0 failed, 0 skipped | 41 passed, 0 failed, 1 skipped |
| `run.py ibis_models`, in the worktree | 6 passed, 0 failed, 0 skipped | 6 passed, 0 failed, 0 skipped |
| `run.py pinned_models`, in the worktree (draft 2 not applied) | 0 passed, 0 failed, 6 skipped | the same |
| `apply/selftest.py` | 18 checks, 0 failures | it reads no model |

With all seven drafts applied, in the two scratch views (no git there, which is what the skips are):

| Test file | View with the models | View without |
|---|---|---|
| edge_length | 42 passed, 0 skipped | 41 passed, 1 skipped |
| ibis_models | 5 passed, 1 skipped | 5 passed, 1 skipped |
| pinned_models | 6 passed | 6 passed |
| rules_status | 35 passed, 1 skipped | 35 passed, 1 skipped |
| evidence_class | 26 passed, 1 skipped | 26 passed, 1 skipped |
| signal_class, netclass, netlist_classes, rules_registry | 8, 8, 2, 5 passed | the same |
| decision_register | 3 passed, 2 skipped | the same |
| requirements | 62 passed, **2 failed**, 2 skipped | the same |
| review_packet, handover_pack, certify_mismatch | 15, 15 (1 skipped), 26 passed | the same |

The two failures are `t_check_refuses_a_hand_edited_trace_page` and `t_the_trace_page_is_generated_not_hand_kept`:
the trace page is stale after the rebind until `rules_render.py --requirements` runs. In the worktree, with no draft
applied, `run.py test_requirements.` reads 65 passed, 0 failed, 1 skipped.

## 9. Open, each with its next action

| Open item | Next action | Whose |
|---|---|---|
| Q3_G, SWCLK and SWDIO: the declarations of section 6 are proposed, not drafted | an apply script for `boards/c.json` on the pattern of `apply_board_c_declarations.py`; the entries' words are in `tools/board_c_remedies.py` | the next author of this stream |
| EPD_SW's net class | `("EPD_SW", "SW")` in `gen_pcb_c3.py` PATTERNS | board C's layout generator owner |
| the four e-paper series resistors | four resistors and four class entries in `gen_sch_c.py` and `boards/c.json`; the new nets' names must not fall under the glob `EPD_*`, which is LOW_SPEED_OR_DC | board C's schematic generator owner |
| 15 nets of board C not closable at the desk | section 6, per group | board B's owner, layer 5's owner, CLK-001's owner, a browser fetch |
| 48 [Ramp] cells have no V-t table and are read as written | an instrument limit, said in `ibis_read.py`; none governs a net that a table could have contradicted | none |
| first lens M1 (three netlist shapes that fail open, none on a committed netlist), M2, M3, M4, M6, M7, M8, M10 | not in this stream's list; M1 is three fixtures and a fix in `_Ctx.resolve` | the next author |
| a part entry for SN74LVC08APWR, SN74LVC32APWR, INA226 and TMP117AIDRVR | an identity audit, then the model's row | the parts stream |
| the scratch views are no git repository | the commit-dating paths were exercised only by `test_pinned_models.py`, on its own repository | none |
| publication of the models | not taken | the owner |
