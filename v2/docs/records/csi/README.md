# Stream csi: board C's SI-001, the 23 layout-bound nets (layer 9, MESHSAT-1357)

Written 29 September 2026 on branch `fnd/csi`, base `e553e43a` (`fnd/int13`, set 12, board C's latest generator);
corrected the same day on the independent check of `a2d9bd32` and on its re-check of `6605f3f6` (section 9).
Prototype design work: nothing here has been built, ordered or measured. No reading on this page is a PASS. The
decisions are the session's under the owner's ruling of 21 September 2026 and his standing rule of 26 September 2026
(authority SESSION); none is the owner's. The work is a desk stream's, not a qualified engineering review.

## 1. The item and the result

SI-001 on board C read INCONCLUSIVE with 23 layout-bound nets, every one decided by a bound (a driver with no published
minimum edge: critical length 0.0 mm), and one net undecided for want of a class (`v2/ecad/pcb-c-display-c8/routed/edge_length.verdict.json`,
netlist sha256/16 `87b69472ac83ca5a`). Of the 23:

| Outcome | Nets | Count |
|---|---|---|
| **decided** | Q3_G (class on content) | 1 |
| **decided in the schematic (drafted), pending the layout** | EPD_SCL, EPD_SDA, EPD_DC, EPD_CS: R53 to R56, 27R, at U3 pins 4 to 7 | 4 |
| **allowed, pending the layout** | QSPI_SCLK, QSPI_D0 to D3, QSPI_SS, XIN, XOUT, XOUT_R, SWCLK, SWDIO | 11 |
| **open** | EPD_SW, HB1, HB2, HB3, SCL, SDA, EXP_INT | 7 |

"Pending the layout" means the answer's condition is a placement and a routed length that nothing decides yet. The four
series terminations answer the lines only when each resistor sits at its pin, and the generator does not place them
there: this board's existing 27R pair, R2 and R3, sits 31.7 and 35.0 mm from U3 on C24 with pin-to-resistor stubs
routed 71.8 and 92.3 mm (section 2). The eleven allowances answer only within their `max_mm`, and C24 runs all eleven
at 4.3 to 30.7 times it. The routed half now holds the eleven (section 3) and `tools/board_c_layout.py` holds the
eleven and the stubs on a board file (a draft instrument), but no rule decides on either reading. The one undecided
net, EMCON_HW_DRV (not among the 23), is declared as well.

SI-001 taken again in scratch (readings under `readings/`):

| Reading | Signal | Slow | Undecided | Answered (of them allowed, pending the layout) | Layout-bound | Result |
|---|---|---|---|---|---|---|
| before: base tool and table, committed netlist | 135 | 101 | 1 | 10 (0) | 23 | INCONCLUSIVE |
| this branch's declarations, committed netlist | 135 | 103 | 0 | 21 (11) | 11 | INCONCLUSIVE |
| the circuit draft applied in a scratch view, stand-in netlist | 139 | 103 | 0 | 29 (11) | 7 | INCONCLUSIVE |

At the schematic phase an allowance whose basis holds is the rule's answer, so the layout-bound counts are 23, 11 and
7. **What keeps the reading from PASS once the seven open nets close (the re-check's m3): a pending count.** While
`edge_length.ALLOW_PENDS_LAYOUT` is set, any net an allowance answers (`allowed_nets`) keeps the schematic result
INCONCLUSIVE and the evidence line ALLOWED says so; it is lifted when a rule names the routed reading. The guard keys on
allowances only: the series-screen answers of every board (the four e-paper lines among them) are the tool's since 26
September and keying on them would change every other board's reading; the four are held pending by this record and by
`board_c_layout.py`, not by the tool.

## 2. The 23 nets, one by one

The maker's edge was asked first (`readings/maker-search-2026-09-29.txt`): Raspberry Pi publishes no IBIS model of the
RP2040 and no minimum transition; Diodes publishes no IBIS model of the 74LVC1G34; TI's PCA9555 INT pin is flagged
(ER-D16); the W25Q16JV's model would decide nothing while the RP2040 shares every QSPI net (ER-D13). So no net is
decided by a maker's figure, and the next means were taken in the brief's order.

The allowance lengths are Raspberry Pi's own reference layout (the minimal design example RP-008296-DS, MIT licence,
measured by `tools/measure_minimal.py`; archive and board file sha256 in `readings/minimal-layout-lengths.txt`, the
archive not committed). That board is 1.0 mm thick with two copper layers, and every net measured runs on F.Cu alone
with no via: a microstrip at 5.572 ps/mm by the formula `edge_length.py` uses. Board C's SI-001 takes its slowest
layer, 7.154 ps/mm, so each length is scaled by 5.572 / 7.154 = 0.779 and rounded down. Each entry names the reference
nets it rests on (`reference_nets`) and cites only their rows and the delay row, from that one listing. C24 is the only
routed board C (`v2/ecad/pcb-c-display-c8/pcb-c-display.kicad_pcb`, commit 9527a3d2, four layers, an older schematic),
measured by `tools/board_c_layout.py` (`readings/c24-layout.txt`).

| Net | Governing driver(s) | Means | Source | Limit (reference net, length) | C24 routed | Placement bound on C24 | U3 pin to its nearest via on C24 |
|---|---|---|---|---|---|---|---|
| EPD_SCL, EPD_SDA, EPD_DC, EPD_CS | RP2040 GPIO2 to 5; the panel's UC8253C only in a read | **decided in the schematic (drafted), pending the layout**: 27R at each pin (R53 to R56, CSI-D3); the stubs EPD_*_R held to 2.1 mm | hardware design guide p. 12: "these I/Os do require 27 Ω series termination resistors (R3 and R4 in Figure 9), placed close to the chip"; the value INFERRED for a GPIO pad; the stub limit is the maker's own pin-to-27R runs (Net-(U3-USB_DP) 2.56, Net-(U3-USB_DM) 2.81 mm), scaled | stub 2.1 (2.81 mm) | lines 354 to 415 mm (the check); no stub (older schematic) | | |
| (USB_DP_R, USB_DM_R, the existing pair) | RP2040 USB | the series screen, held by nothing until now | the same | stub 2.1 | 71.79, 92.31 mm | 31.72, 34.98 mm | 0.74, 1.52 mm |
| QSPI_SCLK | RP2040 QSPI pad; W25Q16JV | **allowed, pending the layout** (CSI-D4) | p. 10: "the QSPI pins of RP2040 should be wired directly to the flash, using short connections to maintain the signal integrity" | 8.0 (QSPI_SCLK 10.38) | 63.82 mm | 41.64 mm | 1.52 mm |
| QSPI_D0 to D3 | the same | the same | the same | 13.1 (QSPI_SD0 to SD3, longest 16.85) | 55.71, 67.86, 61.22, 58.59 mm | 39.6 to 42.1 mm | 0.74 to 1.52 mm |
| QSPI_SS | the same | the same | the same | 17.7 (QSPI_SS 22.73) | 103.26 mm | 46.19 mm | 5.68 mm |
| XIN | RP2040 XOSC (bound) | **allowed, pending the layout** (CSI-D5) | p. 11: "Try and keep the layout as short as possible."; CLK-001 holds the network | 8.7 (XIN 11.23) | 167.59 mm | 47.17 mm | 1.52 mm |
| XOUT_R | the same | the same | the same | 2.1 (XOUT 2.76) | 64.55 mm | 33.75 mm | 0.74 mm |
| XOUT | the same | the same | the same | 4.0 (Net-(C3-Pad1) 5.26) | 112.12 mm | 45.60 mm | no U3 pin |
| SWCLK | a bench probe on TP1 | **allowed, pending the layout** (CSI-D6) | datasheet p. 62: "Each DAP will only respond to debug commands if correctly addressed by a SWD TARGETSEL command; all others tristate their outputs." That the host is a bench probe present only at bring-up is the SESSION's reading of this board | 20.1 (SWCLK 25.92) | 159.62 mm | 146.19 mm | 1.52 mm |
| SWDIO | RP2040 SWD, only when a probe addresses it | the same | the same | 18.9 (SWD 24.34) | 167.59 mm | 147.00 mm | 0.74 mm |
| Q3_G | across R37 (1 k): board D's U18 74LVC1G34 and the RP2040's GPIO23 (ER-D10) | **decided**: LOW_SPEED_OR_DC ahead of `Q?_G` (CSI-D7, W5SI2-D2 taken) | a copy of TR_APRS, which the table declares a static level, as EMCLAMP_G is (W5SI2-D1); physically R37 into Q3's Ciss (at most 50 pF, JSCJ 2N7002 p. 2), tens of nanoseconds at the printed values, supporting and not a bound | | | | |
| EPD_SW | the e-paper boost's switch node | **open** | W5SI-D3 stands: no rule holds a power stage's copper | | | | |
| HB1, HB2, HB3 | the reading is decided by the RP2040's bound (U3 GPIO10 to 12, drivers by ER-D10); the real drivers are board B's level shifters Q105, Q205, Q305 | **open** | a termination at board B's drivers alone would not move board C's reading: board C also needs an answer for the RP2040's own pins | | | | |
| SCL, SDA | the kit bus on boards A, B, C and D | **open** | kit-wide (UM10204 Rev. 6, 7.3); SC-HF-02 not drawn | | | | |
| EXP_INT | the wired-OR interrupt on boards A, B, C and D | **open** | kit-wide, as SCL and SDA | | | | |

EMCON_HW_DRV (U9's own output to R52) had no class entry; it is declared LOW_SPEED_OR_DC on its content, the EMCON level
(CSI-D8). "Placement bound" is the largest distance between two pads of the net (for a stub, U3's pin to its resistor's
pad): any copper that connects it is at least that long, so on C24's placement no routing meets any limit.

## 3. The tool change (edge_length.py)

Until this stream an `edge_allow` entry was a pattern and a sentence (finding F-Q1's W5SI-D3 refused to write one).

- **CSI-D1, the basis.** An entry answers a net only with its basis held the way a record of `pcb_edge_rates.yaml` is
  (`why`, `ruled_by`, `document`, `sha256_16`, page, `quote`, `checked`), and is refused when its pattern has fewer than
  three characters that are no wildcard, its own quote is shorter than five words, it cites a PDF with no page, or it
  cites a file outside the repository (the last in `_quotes_hold`, for every record). A refused entry FAILS the reading.
- **CSI-D2, the length; its method replaced on the re-check (R2-B1, the second failure of the same fault).** An entry
  must state `max_mm` and `reference_nets`, the reference layout's nets it rests on. Every `checked` row is either a
  length row whose whole quote is "`<net> <x> mm`" for one of those nets, or the delay row "`reference t_pd <x> ps/mm`";
  every reference net has its row; all of them cite ONE document. A row naming another net, or no net, is refused.
  `max_mm` may be at most the longest of those lengths times the delay row's figure (`reference_ps_per_mm`) over the
  board's slowest delay (`allow_limit`). The three counterexamples of the re-check (XOUT_R on SWCLK's row at 20.1 mm,
  XOUT_R on an unrelated "extent 572.0 mm" at 445 mm, QSPI_SCLK on QSPI_SD1's row at 13.1 mm) and rows from two
  documents: the round 2 tool held all four, this one refuses all four (`readings/r2-counterexamples.txt`, run by
  `tools/r2_counterexamples.py` on board C's committed entries with every citation true).
- **The routed half.** `routed_main` holds every net a held entry names to its `max_mm` first, whatever its class, rise,
  critical length or series resistor; past it the net is named OVER ITS DECLARED LIMIT (both lengths to the hundredth,
  the re-check's m1) and the routed verdict FAILS. On C24's lengths: FAIL, 11 over (`readings/c24-routed-half.txt`).
- **The pending count (the re-check's m3).** `ALLOW_PENDS_LAYOUT`: a net an allowance answers keeps the schematic reading
  INCONCLUSIVE while no rule decides on the routed reading (section 1). Reverse: set it False once a rule names it.

Tests (`tools/tests/test_edge_length.py`): the refusal test now carries eighteen cases in its loop and one beside it
(among them a row naming another net, a row naming no net, rows from two documents, no `reference_nets`, and the
re-check's "extent 572.0 mm" of another document); the board-tables test runs the re-check's first and third
counterexamples on board C's committed entries (their citations true, the method refuses them); the routed test on a stub board with board C's table; the pending guard (INCONCLUSIVE with an allowance, PASS
with the guard lifted); m1's rounding. On the round 2 tool five edge_length tests fail; on this one nine test files:
152 passed, 0 failed, 1 skipped (`readings/tests-2026-09-29.txt`).

`rules_status.CONFIG_INPUTS["edge_length.py"]` declares the hardware design guide and `readings/minimal-layout-lengths.txt`
(the first check's m1); `--refresh` of that list would drop them, and its comment says so.

## 4. The circuit change, drafted: `apply/apply_board_c_epd_series.py`

For the owner of `gen_sch_c.py`. U3's pins 4 to 7 move to EPD_SCL_R, EPD_SDA_R, EPD_DC_R and EPD_CS_R, and R53 to
R56 (27R, 0603, coded C25190 as R2 and R3 are) join each to its line; four class entries go into `boards/c.json` ahead of
`EPD_*`. It asserts every anchor once, checks R53 to R56 are free, parses the new generator and reads the change back
from the parse, writes c.json in its own format and reads it back, refuses a second run (exit 2), and has `--dry-run`
and `--root`. Read-back, `apply/readback_board_c_epd_series.py <netlist>`: FAILS 16 of 16 on the committed netlist,
HOLDS 16 of 16 on the stand-in (`tools/sim_netlist_c.py`, never a regenerated netlist); applied once and refused once in
a scratch view of this round's tree (`readings/apply-and-readback.txt`). What waits: board C regenerated on the box, the
read-back on that netlist, ERC, the resistors seated at U3's pins (section 7), SI-001 re-taken.

## 5. The other boards, and what else moves on board C

SI-001 on boards A, B, D, E and P, base tool and table against this branch's: verdict, counts, evidence, inputs and
table rows identical on all five; the only difference is the new key `allowed_nets: 0`
(`readings/other-boards-unchanged.txt`). The tool's code bundle changed, so every board's SI-001 reading is stale by
code until re-taken.

On board C, Q3_G's class takes `models_asked` from 6 to 5, and `ti-sn74lvc1g34.pdf`, `diodes-74lvc1g34.pdf` and the
model `sn74lvc1g00.ibs` leave the reading; the two documents the allowances cite join it. `return_via.py` and
`ref_change.py` skip LOW_SPEED_OR_DC, so Q3_G and EMCON_HW_DRV are no longer judged by them, and any tool reading
`signal_class`'s class of those nets (via_audit, per the check) reads the new class: those readings owe a re-take.

## 6. For the integrator, in order

1. Merge `fnd/csi` (with the owner's `-c` flags). Commit before any rules_status run: `tools/boards/c.json`,
   `tools/rules_status.py` and the records under `v2/docs/records/csi/` are inputs the readings cite by sha.
2. `python3 v2/docs/records/csi/apply/apply_board_c_epd_series.py` on the integrated tree (or not: the four e-paper nets
   then stay layout-bound). Then regenerate board C on the box and run `readback_board_c_epd_series.py` on the new
   netlist; commit only behind its HOLDS line.
3. The models fetched where the re-take runs (`python3 v2/ecad/tools/ibis_fetch.py --fetch`, then `--check`), then
   SI-001 re-taken on all six boards with `retake_gate.sh`, and board C's `return_via`, `ref_change` and `via_audit`.
4. `rules_render.py` if the coverage note of SI-001 is updated to say that board tables now carry allowances.
5. Optional: file CSI-D1 to CSI-D9 as rows of `pcb_decisions.yaml` on the pattern of `w5si/apply/apply_decisions_w5si.py`
   (with its rebind, then `decisions_render.py`).

## 7. Open, each with its next action

| Open | Next action | Whose |
|---|---|---|
| **the placement of the fifteen pending nets** (the first check's B3, the re-check's R2-B2 and m2) | a draft for `gen_pcb_c3.py`, which today shelf-packs U4, Y1, C5, C6, R1, R5, R2 and R3 into the cluster by size and puts TP1 and TP2 in the test-point column about 150 mm from U3. Each net's pads must lie within its limit of each other: **R1** pad 1 within 2.1 mm of U3 pin 21 (XOUT_R); **Y1 pin 3, C6 pin 1 and R1 pad 2** within 4.0 mm of each other (XOUT); **Y1 pin 1, C5 pin 1 and U3 pin 20** within 8.7 mm (XIN); **U4** pin 6 within 8.0 mm of U3 pin 52 and pins 5, 2, 3, 7 within 13.1 mm of U3 pins 53, 55, 54, 51 (QSPI); **R5 pin 1 and U4 pin 1** within 17.7 mm of U3 pin 56; **TP1** within 20.1 mm of U3 pin 24 and **TP2** within 18.9 mm of pin 25; **R2, R3 and R53 to R56** with pad 1 within 2.1 mm of U3 pins 47, 46 and 4 to 7. These are necessary conditions only. **The escape fan occupies the space they need:** on C24 the escape vias sit 0.74 to 1.52 mm from U3 pins 20, 21, 24, 25, 46, 47 and 51 to 55, and this board's decoupling seats ended at a median 10.6 mm from their pins because seats must lie outside the fan (`gen_pcb_c3.py`, the block after line 90). XOUT_R's 2.1 mm is under the maker's own 2.76 mm and XOUT's 4.0 mm is tight: they need FIXED sites on U3's side with no escape via on pins 20 and 21 (and the same for pins 46, 47 and 51 to 56), and routed targets with margin under the straight-line bound. **Feasibility is unproven until a placed board passes `tools/board_c_layout.py`** (exit 0; C24 exits 1 on thirteen items). If 2.1 mm cannot be met, the fallback is the last row of this table | board C's layout generator owner |
| the routed reading decides no rule | bind `edge_length_routed` (or a successor) and the stub check of `board_c_layout.py` to a layout-phase rule, so the fifteen can become decided and `ALLOW_PENDS_LAYOUT` can be lifted | the registry writer |
| EPD_SW | the power-stage rule of F-Q1 section 4, then the SW net class in `gen_pcb_c3.py` | the registry writer, then board C's layout generator owner |
| HB1, HB2, HB3 | a series termination at each heartbeat's driver on board B, AND on board C an answer for the RP2040's own pins, whose bound decides the reading (ER-D10) | board B's schematic owner; this board's next author |
| SCL, SDA, EXP_INT | a kit-wide decision: series resistors at the drivers (UM10204 Rev. 6, 7.3) or a bus allowance with a held basis, after SC-HF-02 is drawn; bench item V-K01 | layer 5's owner, boards A to D |
| the 27R value | measured at bring-up: the edge at J_EPD at the drive the firmware sets | bring-up |
| the crystal nodes' stray | a layout-phase reading of the pins-and-tracks capacitance against CLK-001's 3 pF | CLK-001's owner |
| the scaled limits are the slowest layer's | a net kept on an outer layer without vias could be given the outer layer's delay (the maker's own condition; board C's outer layers are 5.52 and 5.37 ps/mm, faster than the reference's), which needs a declared routing layer per net | this board's next author |

## 8. Decisions taken (authority SESSION)

| Id | Decision | To reverse |
|---|---|---|
| CSI-D1 | an `edge_allow` entry answers only with its basis held (a pattern that names nets, a quote of five words or more, a PDF by page, a document inside the repository); a refused one FAILS the reading | accept `why` alone in `allow_refusal` |
| CSI-D2 | every entry names its `reference_nets` and holds a `max_mm` at most their longest length, from one document, scaled by the delays; the routed half holds every net an entry names to it | drop the tests in `allow_limit` and `allow_answers` |
| CSI-D3 | the four e-paper lines take 27R at the RP2040's pins (drafted, not applied), pending the layout | delete R53 to R56, U3 pins back on the lines |
| CSI-D4 | the QSPI nets are allowed, held to the maker's reference lengths scaled to board C (the clock to its own) | delete the three entries |
| CSI-D5 | the crystal nodes likewise, with CLK-001 holding the network | delete the three entries |
| CSI-D6 | the SWD nets likewise, on the session's reading that the port is driven only with a bench probe attached | delete the two entries |
| CSI-D7 | Q3_G is LOW_SPEED_OR_DC on content (W5SI2-D2 taken) | delete the `Q3_G` class entry |
| CSI-D8 | EMCON_HW_DRV is LOW_SPEED_OR_DC on content | delete its class entry |
| CSI-D9 | a net an allowance answers keeps the schematic reading INCONCLUSIVE while no rule decides the routed reading | `ALLOW_PENDS_LAYOUT = False` |
| (kept) | W5SI-D3: no declaration for EPD_SW | as F-Q1 says |

## 9. The checks, item by item

The independent check of `a2d9bd32`:

| Item | Answer |
|---|---|
| B1 the routed half never held `max_mm` on board C | fixed and re-checked: every net a held entry names is held first |
| B2 `max_mm` tied to nothing it cites | partly fixed in round 2 (the re-check's R2-B1), the method replaced in round 3 (below) |
| B3 the eleven counted as decided | "allowed, pending the layout"; C24's lengths and placement bounds; the placement draft (section 7) |
| m1 to m11 | answered in round 2 (CONFIG_INPUTS, the clock's own length, the 0.779 scale, Q3_G's RC, the return rules, HB's RP2040 bound, citation looseness, SWD labelled, the inputs that left, the series resistor answered first, line numbers); the re-check found them holding |

The re-check of `6605f3f6`:

| Item | Answer |
|---|---|
| R2-B1 `max_mm` on any length of any file | the method replaced (section 3, CSI-D2): `reference_nets`, only their rows and the delay row, one document; the three counterexamples and a second document refused, each held by the round 2 tool |
| R2-B2 the e-paper four counted decided on a placement nothing holds | counted "decided in the schematic (drafted), pending the layout"; `board_c_layout.py` holds the pin-to-resistor stubs to 2.1 mm, the maker's own pin-to-27R runs scaled, with the guide's "placed close to the chip"; C24's R2 and R3 stubs read 71.79 and 92.31 mm |
| m1 2.15 printed as 2.1 | both lengths to the hundredth; tested |
| m2 the escape fan | section 7 row 1: C24's escape vias at 0.74 to 1.52 mm from the pins, FIXED sites needed, feasibility unproven until a placed board passes |
| m3 a PASS about less than the pending nets need | a pending count: `ALLOW_PENDS_LAYOUT` keeps the schematic reading INCONCLUSIVE while any net is allowed (section 1 says which nets the guard covers and why the four series-screen answers are held by the record instead) |
| m4 `board_c_layout.py` used unheld entries | it reads `edge_length.load_allow("c")`, names a refused entry and exits 1 |

## 10. What was run, and what was not

On the runner, single test files and SI-001 in scratch only (`VERDICT_DIR` and cwd in the session scratchpad; the
scratch views are `w5si2/tools/scratch_tree.py` copies outside every tree). No gate from `v2/ecad`, no rules_status run,
no renderer in any tree; no box, no purchase, no contact, no agent, no other model. The thirteen models were copied from
`w5si2` into this worktree as ignored files and are not committed. The routed half was run only on stub boards (no
KiCad on the runner): a box run of `edge_length.py` on a board file is the routed reading. `test_requirements` fails
five tests on the base as well (bindings of CON-017, CON-019 and CFL-001 to board A's and B's generators and netlists,
and S-118, S-119 on the trace page): nothing here touches the files they bind.
