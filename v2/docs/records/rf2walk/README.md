# Stream rf2walk: RF-002 on set 12, instrument gap or circuit defect (MESHSAT-1357)

Set 12 (`fnd/int13` at `e41df395`) carries stream d4emcon's FEA-002 remedies on boards B and C, regenerated on the KiCad box
and read back (`readback_d4e.py` holds on both). RF-002's walk (`v2/ecad/tools/check_contracts.py`, which runs
`tx_inhibit.py`) then read 21 FAIL where main (`2c7730a4`) reads 0. This folder classes each FAIL from the walk's own trace and
the parts' documents, records the tool changes that answer them with their fixtures, and shows the readings before and
after. Prototype framing: every reading is of a committed netlist or a maker's document; nothing is built.

## The 21 FAILs, classed

| # | Row (set 12, `readings/contracts-set12-before.txt`) | Class | Evidence |
|---|---|---|---|
| 1 | the asserted line `EMCON_HW`: "C U9 pin 4 ... on EMCON_HW_DRV, reached through ... R52 330R 1%: a second BUF output on the net" and "with no source on the line at all, boards A, B, C: EMCON_HW rises to 3.18 V" | INSTRUMENT | `tx_inhibit.census` accepted the panel's buffer as the line's own source only when its output sits ON the line (`n in SOURCES`), and `_line_sources` looked only at the line's own net. D4E-F1 moved U9 pin 4 onto the private net `EMCON_HW_DRV` (U9 pin 4 and R52 pin 1, nothing else, on set 12's board C netlist `e41df395`), so `fail_safe` found no source on board C, never took board C down, and solved the line with U9 powered: U9 is a push-pull 74LVC1G17 (Diodes DS35124: Y = A) taken at its 3.3 V rail 5 percent high, 3.465 V through R52 (330 Ohm nominal) into R58 4.7 k 1% parallel R102 10 k 1% at their adverse ends (3.229 k), with the pin currents the line lists (about 111 uA): 3.18 V. The part holding the line up is therefore the line's own source, with board C powered, which is the census's state and not a fail-safe one. With board C down U9 passes its Ioff, 10 uA (DS35124), through R52, and the line reads 0.40 V (A, B, C) and 0.584 V worst (J_AB1 unplugged), the same as main in every fragment |
| 2 | the asserted line `TX_INHIBIT_n`: "C U9 pin 4 ... reached through ... D23 diode > R52: a second BUF output" | INSTRUMENT | The census walks from `TX_INHIBIT_n` through D23 (its cathode there: the far side can lift it) onto `EMCON_HW`, then through R52 to U9. U9's input IS `TX_INHIBIT_n`: with EMCON asserted its input is low, its output is low (FORCE BUF 0 to 0), and D23 can only conduct from `EMCON_HW` to `TX_INHIBIT_n` when `EMCON_HW` is the higher, so U9 cannot lift the line against the asserted level. The same rule that accepts U9 as `EMCON_HW`'s source, applied behind its series resistor, answers it. Fail-safe: `TX_INHIBIT_n` rises from 0.243 V (main) to 0.354 V with board C down (all four boards), because `EMCON_HW`'s pin currents now reach it through D23 forward; worst 0.578 V (A and D alone), unchanged from main |
| 3 to 20 | the 18 transmitter rows (LimeSDR, RockBLOCK, E22, both E72, RM520N-GL, both AW7915, six CM5 radios, SA868, the PA and its gate bias, the QMX) | INSTRUMENT (inherited) | Each reads "its line EMCON_HW fails" or "its line TX_INHIBIT_n fails ... (the line result names which)" and nothing of its own: they follow rows 1 and 2. After the fix each reads as it does on main with the same walk (below) |
| 21 | "B: every part that names a radio is a listed transmitter, an accessory or a receiver: unclassified: U543" | INSTRUMENT (declaration) | U543's value names the RockBLOCK ("holds the RockBLOCK's I_EN low"); it is a TPS3808G30 (TI SBVS050N page 1: "microprocessor supervisory circuits ... asserting an open-drain RESET signal when the SENSE voltage drops below a preset threshold"), whose one output pulls `RB_IEN` low. No list classified it, as U221 was not classified until stream w4b declared it |

**Circuit: no defect found.** R52 is in series between U9 and `EMCON_HW` and adds no path. D23 adds one real path, bounded:
`EMCON_HW`'s pin currents now also reach `TX_INHIBIT_n` through D23 forward (the walk's fail-safe sum, 0.354 V at most with
board C down, under 0.8 V); the other way only D23's reverse current, which DS30044 states at +25 C and TJ +60 C only
(0.3 uA and 5.0 uA at VR 1.5 V) and which in every fail-safe state the walk solves would flow from `TX_INHIBIT_n` to
`EMCON_HW` only if `TX_INHIBIT_n` were the higher node: it never is (the ideal reverse element never conducts on set 12). With
board C powered, U9 through R52 and D23 can raise `TX_INHIBIT_n` only while U9's own input, that line, is high; the toggle's
contact holds the line at 0 V at its lug whatever U9 does (at most 10.6 mA through 326.7 Ohm, D4E-F1's arithmetic), and the
ribbon to boards A, B and D carries none of that current. No apply script is owed by this stream for the 21 rows.

## The tool changes (`v2/ecad/tools/tx_inhibit.py`, sha256/16 before `326d0a4832273004`)

1. **The line's own source behind its series resistor** (`drive_net`, `_source_output`, `_line_sources`, and the census's
   buffer clause). A net that carries, test points aside, exactly two pins, the output of a mapped logic gate whose inputs
   all sit on asserted lines and one end of a two-pin resistor whose other end is an asserted line, is that line's drive
   net, and the gate is the line's source there. A second driver, a pull to a rail, a FET or a diode on the net, or an input
   on any other net, and it is an ordinary net again.
2. **A clamp diode's reverse current toward the other asserted line** (`REVERSE_IDEAL`). A diode is passive: its reverse
   current flows only from the higher node to the lower, so it cannot carry the net above the far node. Where the far node is
   the other asserted line (whose own fail-safe level the walk judges on the same states), the reverse direction enters the
   network as an ideal one-way element, the walk's own bound for a diode that can pass current toward the line; a state that
   fails only with it is UNDECIDED, not FAIL (the second solve, as for a diode whose orientation is not drawn). Toward a rail
   or any other node the reverse current stays unbounded and the state UNDECIDED, as before (the BAT54 fixture unchanged).
3. **U543 declared** in `ACCESSORIES` with SBVS050N's words.

Fixtures (`v2/ecad/tools/tests/test_tx_inhibit.py`), each with an acceptable and a defective case:
`t_the_panels_buffer_behind_its_series_resistor_is_the_lines_own_source` (D4E-F1's shape passes both lines; a second driver on
the private net, the buffer's input elsewhere, or a pull-up on the private net each FAIL `EMCON_HW`),
`t_a_diodes_reverse_current_toward_a_line_is_bounded_by_that_lines_own_level` (D4E-F1's shape decides `EMCON_HW`; with
`TX_INHIBIT_n` held high by a pull-up on a live rail, `TX_INHIBIT_n` FAILS and `EMCON_HW` is UNDECIDED "only if a diode's
reverse current ... were as large as an ideal conductor's"), and
`t_a_supervisor_whose_value_names_the_rockblock_is_classified_only_when_declared`. The file reads 136 passed, 0 failed
(`readings/tests-test_tx_inhibit-after.txt`); the three new tests FAIL on the unfixed walk
(`readings/tests-new-fixtures-on-the-unfixed-walk.txt`).

## Readings (`readings/`, each `check_contracts.py` run into a scratch directory, never from `v2/ecad`)

| Tree | Walk | RF-002 rows | inhibit_chain A / B / C / D / E / P |
|---|---|---|---|
| set 12 `e41df395` | unfixed (`contracts-set12-before.txt`) | 21 FAIL, 5 PASS | FAIL 4 / FAIL 17 / FAIL 2 / FAIL 3 / PASS / PASS |
| set 12 | fixed (`contracts-set12-after.txt`) | 0 FAIL, 11 UNDECIDED, 15 PASS | INCONCLUSIVE (7 pass, 2 undecided) / INCONCLUSIVE (12, 8) / PASS (6) / INCONCLUSIVE (8, 1) / PASS / PASS |
| main `2c7730a4` | main's own (`contracts-main-2c7730a4-maintool.txt`, identical to the coordinator's file) | 0 FAIL, 7 UNDECIDED, 18 PASS | INCONCLUSIVE (7, 2) / INCONCLUSIVE (16, 4) / PASS (6) / INCONCLUSIVE (7, 1) / PASS / PASS |
| main | set 12's unfixed walk (`contracts-main-2c7730a4-set12tool-before.txt`) | 0 FAIL, 11 UNDECIDED, 15 PASS | as set 12 fixed |
| main | fixed (`contracts-main-2c7730a4-after.txt`) | byte-identical to the line above | as set 12 fixed |

Main is read in a scratch copy of its whole `v2/ecad` (`git archive 2c7730a4 v2/ecad`) with only `tx_inhibit.py` replaced; a
copy of the `out/` files alone is refused as UNKNOWN GENERATOR (the provenance check hashes the generators' input closure).
The difference between main's own walk and set 12's (7 against 11 UNDECIDED) is `7dc74508`, stream d4emcon's earlier walk
rows on the radios' own pins, carried on `fnd/int13`; this stream's fix moves nothing on main.

Set 12 against main with the same fixed walk: every row has the same verdict; four UNDECIDED rows name different grounds,
all narrower on set 12 (the remedies B-1 to B-3 at work): the RockBLOCK's host-driven inputs and pull-ups are gone from its
row, leaving U7's two inputs and U18's RXD on its outputs; the E22's nine host lines are gone, leaving its antenna pad's U.FL;
both E72's CP2102N TXD, RTS and DTR paths are gone, leaving the bench cJTAG headers and U16 and U17's RXD.

## Second round: the independent check of set 12 (29 September 2026, branch `fnd/rf2walk2` from `fnd/int13` at `eafb324d`)

The check (an AI review, `_scratch/chk-set12/CHECK.md`): mergeable no, 1 blocking, 7 minor; the remedies B-1 to B-5 and
D4E-F1 hold at their stated worst case, the regenerated netlists differ from main's by exactly the drafted parts, and every
reading of the first round reproduces byte for byte.

**B1 (blocking), the walk.** The first round's source rule (a logic output on, or behind its own series resistor onto, one
asserted line with its inputs on the other is "the line's own source") together with `fail_safe` taking the board of any
counted source down hid the check's CX9: two 74LVC1G34 on board B cross-coupled between the lines, a latch that can hold both
lines HIGH with board C down, read PASS on both lines; the same pair wired directly on the lines had read PASS under every walk
since the on-net rule. The fix (`tx_inhibit.py`, commit `149b15f7`):
- `_switch_board(nl)`: a board carrying a SW part with a pin on an asserted line (board C's SW_EMCON). A gate counts as a line's
  own source (the census's on-net clause, `_source_output`, hence `drive_net` and `_line_sources`) only on that board: its
  fail-safe state takes the gate down with the toggle. Anywhere else it is a second driver in the census and a source at its
  supply in the fail-safe states.
- `_fs_base` no longer forces a counted source off whatever its rails do: the toggle's board down removes the rails it makes,
  and a gate on a rail that board receives over a plugged ribbon stays powered and is solved (the same latch on board C, run
  from the +5V it receives from board B, now FAILS both lines; under the previous walk EMCON_HW read UNDECIDED there).
- Fixtures, both failing on the previous walk (`readings/b1/tests-new-fixtures-on-the-previous-walk.txt`):
  `t_a_latch_of_two_buffers_across_the_lines_fails_both_lines` (CX9 behind resistors and direct on board B, and on board C
  from its received +5V; D4E-F1's shape still passes) and `t_a_follower_off_the_switchs_board_is_a_second_driver` (the check's
  CX3b). `test_tx_inhibit`: 138 passed. `tests/run.py contract inhibit requirements evidence rules_status stale`: 388 passed,
  0 failed, 8 skipped.
- The check's own `cx_walk.py` (`readings/b1/check-cx-walk-before.txt`, `-after.txt`): CX9 behind and direct, CX3, CX3b and CX3c
  move from PASS to FAIL on EMCON_HW (CX9 also on TX_INHIBIT_n); every other counterexample reads as before.

| Tree | Walk | RF-002 rows | inhibit_chain A / B / C / D / E / P |
|---|---|---|---|
| set 12 `eafb324d` | previous (`readings/b1/contracts-set12-eafb324d-before.txt`) | 0 FAIL, 11 UNDECIDED, 15 PASS | INCONCLUSIVE (7, 2) / INCONCLUSIVE (12, 8) / PASS / INCONCLUSIVE (8, 1) / PASS / PASS |
| set 12 | fixed (`-after.txt`) | byte-identical to the line above | as above |
| main `2c7730a4` | previous (`contracts-main-2c7730a4-before.txt`) | 0 FAIL, 11 UNDECIDED, 15 PASS | as set 12 |
| main | fixed (`contracts-main-2c7730a4-after.txt`) | byte-identical to the line above | as set 12 |
| main | main's own (`contracts-main-2c7730a4-maintool.txt`) | 0 FAIL, 7 UNDECIDED, 18 PASS | the `7dc74508` rows, as in the first round |

**The minors that are this stream's remedies**, corrected in place in `v2/docs/feasibility/EMCON.md` section 4d.6 and bench
E-04, and drafted for board B as `apply_b_chk12.py` (not applied; the integrator applies it, regenerates board B once and runs
`tools/readback_chk12.py`, which parses the netlist and the intent file; on set 12's committed board B it reads 10 FAIL of 11,
as it must before regeneration, and `tools/selftest_readback_chk12.py` shows it passing a synthetic after-pair and failing
three mutants). No RF-002 row moves with it: its parts sit on RB_IEN, 5G_PWROFF_n and rail notes, off every path the walk
judges.

| Minor | What | Draft or statement |
|---|---|---|
| 1 | B-5's release rests on the module's 100 k pull-down, tolerance unstated | M1: R238 49.9 k 1% (C23184): held 72 uA (0.1 V row), released 2.08 V, at or over 1.19 V down to 30.8 k |
| 2 | B-4: U543 sank up to 1.17 mA above 1.65 V (VOL row 1 mA); its 12 to 28 ms pulse can re-assert I_EN before the 9704 ends its shutdown | M2: R532 2.7 k 1% (0.955 mA at most up to 2.90 V), R527 20.0 k 1% (released 2.10 V, asserted 0.16 V, every rail lost 0.37 V), CT to +5V_DEV through R551 49.9 k 1% (td 180 to 420 ms); bench E-04 measures the 9704's I_EN-low-to-I_BTD-low time, no held document states it |
| 3 | B-3: LORA_GO follows E22_EN, not +5V_LORA's level; J_SPI3's IO23 and IO24 are driven too | stated in 4d.6: a turn-on exposure, smaller than before B-3, not under EMCON and not claimed closed; the breakout cost widened to three pins |
| 4 | B-1: 80 mV release margin; P_EN after boot follows U6 pin 20 (pull-up, charger off) | the margin is 2.10 V with M2; P_EN is a firmware item for PANEL.md, not a regression |
| 5 | board B's intent: +3V3_CM2 and +3V3_CM3 notes stale, +3V3_CM{s} missing their EMCON gates since round 8, +3V3_ZB missing R536 to R538 | M5: loads and notes read from set 12's netlist |
| 6 | REVERSE_IDEAL narrowed to the other asserted line for a wording reason | kept: toward a rail or any other node the state stays UNDECIDED either way, and the narrow rule leaves every earlier fixture's wording as it was |
| 7 | D4E-F1's docstring gives 0.32 V where the walk reads 0.354 V | stated in 4d.6: cite the walk's 0.354 V |

**For the integrator.** Merge `fnd/rf2walk2`; run `apply_rebind_page_rf2walk2.py` (rebinds the seven records bound to
EMCON.md, whose sections 4d.6 and E-04 changed; tried and restored on this branch) and render; re-take RF-002 with the changed
walk; apply `apply_b_chk12.py`, regenerate board B, run `tools/readback_chk12.py`, and rebind board B's records as after set 12.

## Third round: the re-check of set 12 (29 September 2026, branch `fnd/rf2walk3` from `fnd/rf2walk2` at `06eb61ef`)

The re-check (an AI review, `_scratch/chk-set12/CHECK-2.md`): B1 not closed. The second round's `_switch_board` counted any
board with a switch on either asserted line as the toggle's board: a switch on board B from TX_INHIBIT_n to ground brought
CX9's latch back (CX10), and a switch on board B from TX_INHIBIT_n to +3V3_DEV was skipped as "the toggle" on every walk
(CX14). Two failures on one fault, so the method changed (the owner's rule): no inference of the source from the wiring.

**The declaration.** `EMCON_TOGGLES` in `v2/ecad/tools/tx_inhibit.py`, beside `SOURCES`, the walk's declaration of the two
lines: one entry, board C, `SW_EMCON`, value "EMCON locking toggle", its contact between `TX_INHIBIT_n` and GND, the one element
that asserts the inhibit; source `gen_sch_c.py` (the SW_EMCON part line: lug 1 TX_INHIBIT_n, lug 2 GND, lug 3 unconnected; lug 2
the common per the APEM sheet cited there) and `v2/docs/PANEL.md` (the Switches row). `_is_toggle(k, nl, ref)` returns the
declaration when the part on board `k` matches its board, reference, value and wiring (one pin on the line, one on ground,
every other pin unconnected). `_switch_board`, `_line_sources` (with `_source_output` and `drive_net`), the census and
`fail_safe` use only it. Every other switch or contact is an ordinary part: in the census a contact to ground can only
assert, to a rail FAILS ("a switch contact ties the net to ... when closed"), to a signal net is followed; in the fail-safe
network it is taken closed, an ideal one-way element the adverse way (it used to be taken open). `judge()` takes `toggles`
like its other tables; `tests/test_tx_inhibit.py` declares its fixtures' own toggles (`FIXTURE_TOGGLES`) and passes them.

**Every counterexample, previous walk (`06eb61ef`) against this walk** (`readings/b1r3/check-cx_walk*-previous-walk.txt` and
`-new-walk.txt`, the checker's own scripts run from scratch):

| Case | Previous: EMCON_HW / TX_INHIBIT_n | This walk |
|---|---|---|
| CX0, CX0' D4E-F1 shape | PASS / PASS | PASS / PASS |
| CX1 expander pin behind its own 330R (C) | FAIL | FAIL |
| CX2 second buffer on B, firmware input, behind 330R | FAIL | FAIL |
| CX3 second buffer on B from TX_INHIBIT_n behind 330R | FAIL / FAIL | FAIL / FAIL |
| CX3b, CX3c the same with a live pull-up on TX_INHIBIT_n | FAIL / FAIL | FAIL / FAIL |
| CX4a BAT46 from +3V3_DEV onto EMCON_HW | FAIL | FAIL |
| CX4b BAT46 from EMCON_HW to +3V3_DEV | UNDECIDED | UNDECIDED |
| CX5 pull-up on EMCON_HW (B) | FAIL / PASS | FAIL / PASS |
| CX6 clamp on EMCON_HW_DRV | FAIL | FAIL |
| CX7 inverter behind 330R (C) | FAIL | FAIL |
| CX8 D23 reversed | PASS / PASS | PASS / PASS |
| CX9, CX9c latch on B, behind 330R and direct | FAIL / FAIL | FAIL / FAIL |
| CX10 latch on B plus a switch on B to GND (behind 330R) | PASS / PASS | FAIL / FAIL |
| CX10b latch on B plus a switch on B to +3V3_DEV | PASS / PASS | FAIL / FAIL |
| CX11 second 74LVC1G17 on C behind 330R | PASS / PASS | PASS / PASS |
| CX12 latch on C from C's own +3V3 | PASS / PASS | PASS / PASS |
| CX13 EMCON_HW made on B from TX_INHIBIT_n | FAIL / PASS | FAIL / PASS (does not move: conservative, stated in `_switch_board`) |
| cx_walk3: latch on B, direct and behind 330R, main's and D4E-F1's shape | FAIL / FAIL | FAIL / FAIL |
| cx_walk3: the same plus a switch on B to GND, both forms and shapes | PASS / PASS | FAIL / FAIL |
| cx_walk3: CX14, main's shape | PASS / PASS | PASS / FAIL |
| cx_walk3: CX14, D4E-F1 shape | PASS / PASS | UNDECIDED / FAIL (only D23's reverse current, taken ideal, joins a lifted TX_INHIBIT_n to EMCON_HW) |

**Fixtures** (each FAILs on the previous walk where it asserts a FAIL): `t_a_second_switch_makes_no_board_the_toggles_board`
(CX10, both forms, both shapes), `t_a_switch_that_lifts_the_line_is_a_second_driver` (CX14, both shapes),
`t_the_toggles_board_keeps_its_legitimate_shapes` (CX11, CX12 PASS; the latch on C from its received +5V FAILS; CX13 FAIL),
`t_only_the_declared_toggle_is_a_source`. `test_tx_inhibit`: 142 passed, 0 failed. Groups contract, inhibit, requirements,
evidence: 346 passed, 0 failed, 5 skipped.

**Readings** (`readings/b1r3/`, `check_contracts.py` into scratch on a `git archive` of the whole `v2/ecad`):
- set 12 at `dd7230a7`: board B is refused as UNKNOWN GENERATOR on both walks (its `gen_sch_b.py` carries CHK12-B and board B is
  not regenerated), so the 20 RF-002 rows that need board B are UNJUDGED; identical bytes on both walks;
- set 12's netlists under the generator that wrote them (`eafb324d`'s tree): 0 FAIL, 11 UNDECIDED, 15 PASS on both walks,
  identical bytes;
- main `2c7730a4`: 0 FAIL, 11 UNDECIDED, 15 PASS on both walks, identical bytes; 7 UNDECIDED with main's own walk (`7dc74508`).

**The two minors.** R527's margin with every rail lost is 30 mV (0.37 V against 0.4 V, on the stated Ioff sum); 16.5 k would
raise it to 92 mV but cut the released level's margin to 51 mV, so the drafted 20.0 k stands and no follow-up is owed for it.
The Q{s}01 note: `apply_b_chk12_led.py`, a follow-up to CHK12-B for `dd7230a7`'s `gen_sch_b.py` (the same regeneration), puts
Q{s}01 (the BC857 buffering LED_nPWR, emitter on the rail) and R{s}48 (the ACT LED's 1 k) in the module rails' loads at 3.3 mA
each and corrects the note; `tools/readback_chk12.py` now finds each rail's LED feeds in the netlist and checks them (13 FAIL
on set 12's committed board B, as it must before regeneration; its self-test passes the synthetic after-pair and fails its
mutants). EMCON.md 4d.6 gains the declared toggle, B-4's margin and its start-up case (a dip while the supercapacitors charge
drives I_EN low before I_BTD rises, the other half of Ground Control's order), and the LED loads; bench E-04 gains the start-up
dip. `apply_rebind_page_rf2walk3.py` rebinds the seven records bound to EMCON.md (dry-run on this branch and on a scratch
clone of `dd7230a7`).

**For the integrator.** Merge `fnd/rf2walk3`; run `apply_rebind_page_rf2walk3.py` and render; re-take RF-002; apply
`apply_b_chk12_led.py` with CHK12-B's regeneration of board B, run `tools/readback_chk12.py`, rebind board B's records.

## What remains open

- The 11 UNDECIDED rows, the same rows as main's under the same walk: the LimeSDR (the USBLC6-2's VBUS with its I/O on the
  hub, tools author); the RockBLOCK (U7 pins 7 and 8, PCA9555 inputs a firmware error could turn to outputs, and U18's RXD on
  the module's outputs); the E22 (its antenna pad leaves the board on J_LORA1, whose far end, board A's LoRa jack, is not on
  board B's netlist); both E72 (the cJTAG bench headers, declared accessories, and U16 and U17's RXD); the RM520N-GL (U215's
  released `W_DISABLE1#` with its maker's threshold unstated, and on the supply path the socket's own pins that stay live,
  USB from U302 and the rest, which the walk does not sum into R295's 15 Ohm hold, EMCON.md 4b); both AW7915 (no maker
  document for W_DISABLE1#, and on the supply path the card's own pins that stay live: the PCIe pairs and REFCLK from U101
  and U301, its LED); the SA868 (S-92: pin 5's threshold and U13's off-state current); the PA's drain path (U14, the INA226 on
  +13V8_PA, and board D's Q1, S-93) and the QMX (the LM5176's high-side drive in shutdown, S-93).
- The CP2102N's RXD is read as a pin firmware sets; Silicon Labs' data sheet (held) gives the UART pins fixed functions, which
  the tools author can teach the walk from its pin table, with the pin's weak pull-up (IPU 10 to 30 uA) as its current.
- The walk's class for the TPS3808 on a line it reads (U543 on `RB_IEN`) is not needed by any row today: `RB_IEN` is not on a
  path the table walks.
- After the re-check: EMCON_HW made off the toggle's board from TX_INHIBIT_n reads FAIL (conservative; not the kit's
  design); a start-up dip against Ground Control's order (bench E-04); board B's regeneration with CHK12-B and CHK12-LED.
- After the check of set 12: the 9704's time from I_EN low to I_BTD low (bench E-04, sets U543's td); B-3's turn-on exposure
  (LORA_GO follows the enable, not the rail); B-5's module pull-down tolerance (unstated; the draft tolerates down to 30.8 k);
  the drafts of `apply_b_chk12.py` until board B is regenerated and read back.
