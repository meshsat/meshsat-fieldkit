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
