# Stream csi: board C's SI-001, the 23 layout-bound nets (layer 9, MESHSAT-1357)

Written 29 September 2026 on branch `fnd/csi`, base `e553e43a` (`fnd/int13`, set 12, board C's latest generator), and
corrected the same day on the independent check of `a2d9bd32` (three blocking items, eleven minors; section 9).
Prototype design work: nothing here has been built, ordered or measured. No reading on this page is a PASS. The
decisions are the session's under the owner's ruling of 21 September 2026 and his standing rule of 26 September 2026
(authority SESSION); none is the owner's. The work is a desk stream's, not a qualified engineering review.

## 1. The item and the result

SI-001 on board C read INCONCLUSIVE with 23 layout-bound nets, every one decided by a bound (a driver with no published
minimum edge: critical length 0.0 mm), and one net undecided for want of a class (`v2/ecad/pcb-c-display-c8/routed/edge_length.verdict.json`,
netlist sha256/16 `87b69472ac83ca5a`). Of the 23:

| Outcome | Nets | Count |
|---|---|---|
| **decided** | EPD_SCL, EPD_SDA, EPD_DC, EPD_CS (series termination at the driver, drafted; applied and regenerated owed); Q3_G (class on content) | 5 |
| **allowed, pending the layout** | QSPI_SCLK, QSPI_D0 to D3, QSPI_SS, XIN, XOUT, XOUT_R, SWCLK, SWDIO | 11 |
| **open** | EPD_SW, HB1, HB2, HB3, SCL, SDA, EXP_INT | 7 |

"Allowed, pending the layout" means: an `edge_allow` entry answers the net at the schematic phase with a basis the tool
holds and a length tied to what it cites, and the routed half now holds the net to that length (section 3), but the
only routed board C (C24) runs all eleven at 4.3 to 30.7 times their limits (section 2), its placement generator does
not seat the parts close enough (section 7), and no rule names the routed reading yet. They are not decided until the
layout meets the limits and a rule decides on that reading. The one undecided net, EMCON_HW_DRV (not among the 23), is
declared as well.

SI-001 taken again in scratch (readings under `readings/`):

| Reading | Signal | Slow | Undecided | Answered (of them allowed, pending the layout) | Layout-bound | Result |
|---|---|---|---|---|---|---|
| before: base tool and table, committed netlist | 135 | 101 | 1 | 10 (0) | 23 | INCONCLUSIVE |
| this branch's declarations, committed netlist | 135 | 103 | 0 | 21 (11) | 11 | INCONCLUSIVE |
| the circuit draft applied in a scratch view, stand-in netlist | 139 | 103 | 0 | 29 (11) | 7 | INCONCLUSIVE |

The counts did not move in the second round: at the schematic phase an allowance whose basis holds and whose length
is tied to its citations is still the rule's answer, and every `max_mm` now sits under its scaled limit. What moved is
what the answer is worth: the routed half, on C24's lengths, now reads FAIL with 11 nets over their declared limits
(`readings/c24-routed-half.txt`), where the tool before this round read INCONCLUSIVE with none. Were the seven open nets
closed, SI-001 would read PASS at the schematic phase with eleven nets pending the layout; the open row of section 7
("the routed reading decides no rule") is what stands between that and a decision.

## 2. The 23 nets, one by one

The maker's edge was asked first (`readings/maker-search-2026-09-29.txt`): Raspberry Pi publishes no IBIS model of the
RP2040 (its Product Information Portal lists the datasheet, the hardware design guide, the product brief and the
minimal KiCad design, nothing else; its documentation repository and GitHub hold none) and no minimum transition;
Diodes publishes no IBIS model of the 74LVC1G34; TI's PCA9555 model is held and its INT pin is flagged (ER-D16); the
W25Q16JV's model would decide nothing while the RP2040 shares every QSPI net (ER-D13). So no net is decided by a
maker's figure, and the next means were taken in the brief's order.

The allowance lengths are Raspberry Pi's own reference layout (the minimal design example RP-008296-DS, MIT licence,
fetched and measured by `tools/measure_minimal.py`; the archive and board file sha256 are in
`readings/minimal-layout-lengths.txt`, the archive is not committed). The maker's board is 1.0 mm thick with two copper
layers, and every one of these nets runs on F.Cu alone with no via: a microstrip at 5.572 ps/mm by the formula
`edge_length.py` uses. Board C's SI-001 takes its slowest layer, 7.154 ps/mm (JLC04161H-7628 In2.Cu), so each length
is scaled by 5.572 / 7.154 = 0.779 to hold the same delay, and rounded down (the check's m3). C24 is the only routed
board C (`v2/ecad/pcb-c-display-c8/pcb-c-display.kicad_pcb`, commit 9527a3d2, four layers, an older schematic);
`tools/board_c_layout.py` measures it (`readings/c24-layout.txt`, the check's own figures reproduced).

| Net | Governing driver(s) | Means | Source | max_mm (reference, scaled) | C24 routed | Placement bound on C24 |
|---|---|---|---|---|---|---|
| EPD_SCL, EPD_SDA, EPD_DC, EPD_CS | RP2040 GPIO2 to 5; the panel's UC8253C only in a read | **decided**: 27R at each RP2040 pin (R53 to R56, CSI-D3, a draft) | hardware design guide p. 12, "these I/Os do require 27 Ω series termination resistors" (the maker's value on this chip's USB pins); INFERRED for a GPIO pad (the datasheet's DC limits bound the pad's own resistance at roughly 125 to 170 ohm worst case, so 27R adds damping, not a computed match); PANEL.md: "MOSI only, the display's read path is unused" | none | 354 to 415 mm (the check) | not asked |
| QSPI_SCLK | RP2040 QSPI pad; W25Q16JV | **allowed, pending the layout** (CSI-D4) | p. 10: "the QSPI pins of RP2040 should be wired directly to the flash, using short connections to maintain the signal integrity" (a series resistor is against it) | 8.0 (the clock's own 10.38 mm, the check's m2) | 63.82 mm, 6 vias | 41.64 mm |
| QSPI_D0 to D3 | the same | the same | the same | 13.1 (16.85 mm, the longest data line) | 55.71, 67.86, 61.22, 58.59 mm | 39.6 to 42.1 mm |
| QSPI_SS | the same | the same | the same | 17.7 (22.73 mm, with the BOOTSEL resistor) | 103.26 mm | 46.19 mm |
| XIN | RP2040 XOSC (bound) | **allowed, pending the layout** (CSI-D5) | p. 11: "Try and keep the layout as short as possible."; CLK-001 holds the network (stray 3 pF, one series resistor) | 8.7 (11.23 mm) | 167.59 mm | 47.17 mm |
| XOUT_R | the same | the same | the maker's pin-to-1 k run | 2.1 (2.76 mm) | 64.55 mm | 33.75 mm |
| XOUT | the same | the same | the maker's 1 k-to-crystal node | 4.0 (5.26 mm) | 112.12 mm | 45.60 mm |
| SWCLK | a bench probe on TP1 | **allowed, pending the layout** (CSI-D6) | datasheet p. 62: "Each DAP will only respond to debug commands if correctly addressed by a SWD TARGETSEL command; all others tristate their outputs." That the host is a bench probe present only at bring-up is the SESSION's reading of this board, not the maker's words (the check's m8) | 20.1 (25.92 mm) | 159.62 mm | 146.19 mm |
| SWDIO | RP2040 SWD, only when a probe addresses it | the same | the same | 18.9 (24.34 mm) | 167.59 mm | 147.00 mm |
| Q3_G | across R37 (1 k): board D's U18 74LVC1G34 and the RP2040's GPIO23 (ER-D10) | **decided**: LOW_SPEED_OR_DC ahead of `Q?_G` (CSI-D7, W5SI2-D2 taken) | a copy of TR_APRS, which the table declares a static level, as EMCLAMP_G is (W5SI2-D1); physically R37 into Q3's Ciss (at most 50 pF, JSCJ 2N7002 p. 2), tens of nanoseconds at the printed values; no minimum capacitance is published, so that is supporting and not a bound (the check's m4) | none | | |
| EPD_SW | the e-paper boost's switch node | **open** | W5SI-D3 stands: no rule holds a power stage's copper, so no declaration is written | | | |
| HB1, HB2, HB3 | the reading is decided by the RP2040's bound (U3 GPIO10 to 12, counted as drivers by ER-D10); the lines' real drivers are board B's level shifters Q105, Q205, Q305 (drains, 10 k pull-ups) | **open** | a termination at board B's drivers alone would not move board C's reading: board C also needs an entry that answers the RP2040's pins, with a held basis (the check's m6) | | | |
| SCL, SDA | the kit bus on boards A, B, C and D | **open** | kit-wide (UM10204 Rev. 6, 7.3), and the three-segment design SC-HF-02 is not drawn | | | |
| EXP_INT | the wired-OR interrupt on boards A, B, C and D (PCA9555 INT flagged, KSZ9897, TPS23861, DS3231, RP2040) | **open** | kit-wide, as SCL and SDA | | | |

EMCON_HW_DRV (U9's own output to R52, since stream d4emcon) had no class entry; it is declared LOW_SPEED_OR_DC on its
content, the EMCON level (CSI-D8).

"Placement bound on C24" is the largest distance between two pads of the net: any copper that connects it is at least
that long, so on C24's placement no routing can meet any of the eleven limits.

## 3. The tool change (edge_length.py)

Until this stream an `edge_allow` entry was a pattern and a sentence, and a sentence turned a net green (finding F-Q1's
W5SI-D3 refused to write one for that reason). No board carried one.

- **CSI-D1, the basis.** An entry answers a net only with its basis held the way a record of `pcb_edge_rates.yaml` is
  (`why`, `ruled_by`, `document`, `sha256_16`, `page` or `where`, `quote`, `checked`; `_cite_shape`, `_quotes_hold`).
  Since the check (m7) it is also refused when its pattern has fewer than three characters that are no wildcard, its
  own quote is shorter than five words, it cites a PDF with no page, or it cites a file outside the repository (the
  last in `_quotes_hold`, for every record: every committed citation is inside, so no reading moves). A refused entry
  FAILS the reading and leaves its nets layout-bound.
- **CSI-D2, the length (the check's B2).** An entry must state `max_mm` with `max_mm_basis`, or it is refused. `max_mm`
  must be at most the longest length its `checked` rows quote ("`<net> <x> mm`") times the reference layout's delay (a
  checked row quoting "`t_pd <x> ps/mm`", stated as `reference_ps_per_mm`) over this board's slowest delay
  (`worst_delay`): `allow_limit`. An entry with 500 mm on the same citations, or with its length rows dropped, is refused.
- **The routed half (the check's B1 and m10).** `routed_main` holds EVERY net a held entry names to its `max_mm` first,
  whatever its class, its rise time, its critical length or a series resistor on it; past it the net is named OVER ITS
  DECLARED LIMIT and the routed verdict FAILS (counts `over_declared_limit`, `held_within_declared_limit`). A net held
  within its limit is answered and no longer counted under "no declared edge".
- The schematic table records `length_limits` per net, the evidence line reads "ALLOWED ... pending the layout", and
  a count `allowed_nets` sits inside `answered_nets` (no sum changes).

Tests (`tools/tests/test_edge_length.py`): the old test that passed a board on a bare sentence shows it refused, then
PASS with a cited entry; `t_si001_an_allowance_answers_only_with_its_basis_held` (fourteen refusals, each a FAIL with
the net layout-bound, among them 500 mm, no `max_mm`, rows dropped, `*`, a one-word quote, a PDF by `where`, a file
outside the repository); `..._hands_its_length_to_the_layout_and_the_routed_half_holds_it` (`allow_limit`,
`allow_answers`); `t_si001_the_routed_half_holds_every_allowance_net_to_its_declared_length` (`routed_main` on a stub
board with board C's committed table: C24's QSPI_SCLK 63.82 mm and a QSPI_D0 with a 22R on it FAIL over their limits,
within them the reading passes); `..._the_board_tables_allowances_hold_against_their_documents`. On the previous
tool (`a18e90e9`) the three new or changed ones fail, the routed one reading INCONCLUSIVE with nothing over its limit.
Nine test files: 152 passed, 0 failed, 1 skipped (`readings/tests-2026-09-29.txt`).

`rules_status.CONFIG_INPUTS["edge_length.py"]` now declares the two documents board C's entries cite, the hardware
design guide and `readings/minimal-layout-lengths.txt` (the check's m1), so a change to either stales board C's
reading; its comment's line numbers are brought to this tool (m11). The documents recorded by board C's reading are all
declared (checked). `apply_rules_status_config_inputs.py --refresh` derives its list from `pcb_edge_rates.yaml` alone
and would drop the two: the comment says to add them back after a refresh.

## 4. The circuit change, drafted: `apply/apply_board_c_epd_series.py`

For the owner of `gen_sch_c.py`. U3's pins 4 to 7 move to EPD_SCL_R, EPD_SDA_R, EPD_DC_R and EPD_CS_R, and R53 to
R56 (27R, 0603, coded C25190 by `lcsc_fill.py` as R2 and R3 are) join each to its line; the lines keep their names
from the resistor to J_EPD. It also writes four class entries (CLOCKED_DIGITAL) into `boards/c.json` ahead of the glob
`EPD_*`. It asserts every anchor once, checks R53 to R56 are free, parses the new generator and reads U3's map and the
four `r()` calls back from the parse, writes c.json in its own format and reads it back, refuses a second run (exit
2), and has `--dry-run` and `--root`. Read-back, `apply/readback_board_c_epd_series.py <netlist>`: 16 checks; FAILS 16
of 16 on the committed netlist, HOLDS 16 of 16 on the stand-in (`tools/sim_netlist_c.py`, a text rewrite of the
committed netlist, never a regenerated netlist). Applied in a scratch view of the second round's tree: written, then
refused (`readings/apply-and-readback.txt`). What waits on regeneration: board C's schematic, netlist and intent on the
box; the read-back on that netlist; ERC; the four resistors seated at U3's pins (section 7); SI-001 re-taken.

## 5. The other boards, and what else moves on board C

SI-001 on boards A, B, D, E and P, base tool and table against this branch's: verdict, counts, evidence, inputs and
table rows identical on all five; the only difference is the new key `allowed_nets: 0`
(`readings/other-boards-unchanged.txt`). The tool's code bundle changed, so every board's SI-001 reading is stale by
code until re-taken.

On board C the reading's inputs also change with Q3_G's class (the check's m9): `models_asked` 6 to 5, and the
documents `ti-sn74lvc1g34.pdf` and `diodes-74lvc1g34.pdf` and the model `sn74lvc1g00.ibs` leave the reading (they were
asked for Q3_G's drivers), and the two documents the allowances cite join it. The two class entries also change what the EMC return rules judge on board C (the check's
m5): `return_via.py` and `ref_change.py` skip LOW_SPEED_OR_DC, so Q3_G (HIGH_SPEED_DIGITAL before) and EMCON_HW_DRV
(UNKNOWN before, judged at the strictest bar) are no longer judged by them, and any tool reading `signal_class`'s class
of those two nets (via_audit, per the check) reads the new class. Their board C readings owe a re-take.

## 6. For the integrator, in order

1. Merge `fnd/csi` (with the owner's `-c` flags). Commit before any rules_status run: `tools/boards/c.json`,
   `tools/rules_status.py` and the records under `v2/docs/records/csi/` are inputs the readings cite by sha.
2. `python3 v2/docs/records/csi/apply/apply_board_c_epd_series.py` on the integrated tree (or not: the four e-paper nets
   then stay layout-bound). Then regenerate board C on the box and run `readback_board_c_epd_series.py` on the new
   netlist; commit only behind its HOLDS line.
3. The models fetched where the re-take runs (`python3 v2/ecad/tools/ibis_fetch.py --fetch`, then `--check`), then
   SI-001 re-taken on all six boards with `retake_gate.sh` (the tool's code changed), and board C's `return_via`,
   `ref_change` and `via_audit` readings re-taken (section 5).
4. `rules_render.py` if the coverage note of SI-001 is updated to say that board tables now carry allowances.
5. Optional: file CSI-D1 to CSI-D8 as rows of `pcb_decisions.yaml` on the pattern of `w5si/apply/apply_decisions_w5si.py`
   (with its rebind of the requirement records bound to that file, then `decisions_render.py`). The rows' fields are
   already on each board-table entry (ruled_by, ruled_on, authority, authority_why, reverse).

## 7. Open, each with its next action

| Open | Next action | Whose |
|---|---|---|
| **the eleven allowed nets' placement** (the check's B3) | a draft for `gen_pcb_c3.py`, which today shelf-packs U4, Y1, C5, C6, R1 and R5 into the cluster by size and puts TP1 and TP2 in the test-point column, about 150 mm from U3. Each net's pads must lie within its `max_mm` of each other, which on board C's netlist means: **R1** with pad 1 within 2.1 mm of U3 pin 21 (XOUT_R); **Y1, C6 and R1 pad 2** within 4.0 mm of each other (XOUT); **Y1 pin 1, C5 pin 1 and U3 pin 20** within 8.7 mm (XIN); **U4** with pins 6 and 5, 2, 3, 7 within 8.0 mm of U3 pin 52 and 13.1 mm of pins 53, 55, 54, 51 (QSPI_SCLK, QSPI_D0 to D3); **R5 pin 1 and U4 pin 1** within 17.7 mm of U3 pin 56 (QSPI_SS); **TP1** within 20.1 mm of U3 pin 24 and **TP2** within 18.9 mm of pin 25 (SWD). These are necessary conditions (the farthest pad pair); the routed length must also meet them, on whatever layers. `tools/board_c_layout.py <board>` checks a placed or routed board against the table's limits (exit 0 needed; C24 exits 1 on all eleven). The same generator change owes R2, R3 (USB) and R53 to R56 (section 4) sites at U3's pins | board C's layout generator owner |
| the routed reading decides no rule | bind `edge_length_routed` (or a successor) to a layout-phase rule, so that `max_mm` is held by a deciding reading and the eleven can become decided | the registry writer |
| EPD_SW | the power-stage rule of F-Q1 section 4, then the SW net class in `gen_pcb_c3.py` (F-Q1 section 5 item 5) | the registry writer, then board C's layout generator owner |
| HB1, HB2, HB3 | a series termination at each heartbeat's driver on board B (the level shifters' drains), AND on board C an answer for the RP2040's own pins, whose bound decides the reading (ER-D10): an entry with a held basis, or a firmware-held input declared as the pins' state | board B's schematic owner; this board's next author |
| SCL, SDA, EXP_INT | a kit-wide decision: series resistors at the drivers (UM10204 Rev. 6, 7.3) or a bus allowance with a held basis, after SC-HF-02 is drawn; bench item V-K01 | layer 5's owner, boards A to D |
| the 27R value | measured at bring-up: the edge at J_EPD at the drive the firmware sets | bring-up |
| the crystal nodes' stray | a layout-phase reading of the pins-and-tracks capacitance against CLK-001's 3 pF | CLK-001's owner |
| the scaled limits are the slowest layer's | a net kept on an outer layer without vias could be given the outer layer's delay (the maker's own condition), which needs a declared routing layer per net; until then the limits hold for any layer | this board's next author |

## 8. Decisions taken (authority SESSION)

| Id | Decision | To reverse |
|---|---|---|
| CSI-D1 | an `edge_allow` entry answers only with its basis held (and, since the check, a pattern that names nets, a quote of five words or more, a PDF by page, a document inside the repository); a refused one FAILS the reading | accept `why` alone in `allow_refusal` |
| CSI-D2 | every entry holds a `max_mm` tied to its cited lengths scaled by the delays; the routed half holds every net an entry names to it | drop the length tests in `allow_limit` and `allow_answers` |
| CSI-D3 | the four e-paper lines take 27R at the RP2040's pins (drafted, not applied) | delete R53 to R56, U3 pins back on the lines |
| CSI-D4 | the QSPI nets are allowed, not series-terminated, held to the maker's reference lengths scaled to board C (the clock to its own) | delete the three entries |
| CSI-D5 | the crystal nodes likewise, with CLK-001 holding the network | delete the three entries |
| CSI-D6 | the SWD nets likewise, on the session's reading that the port is driven only with a bench probe attached | delete the two entries |
| CSI-D7 | Q3_G is LOW_SPEED_OR_DC on content (W5SI2-D2 taken) | delete the `Q3_G` class entry |
| CSI-D8 | EMCON_HW_DRV is LOW_SPEED_OR_DC on content | delete its class entry |
| (kept) | W5SI-D3: no declaration for EPD_SW | as F-Q1 says |

## 9. The independent check of `a2d9bd32`, item by item

| Item | Answer |
|---|---|
| B1 the routed half never held `max_mm` on board C | fixed: every net a held entry names is held first, whatever its class, rise or series resistor; test on a stub board with board C's table; C24's lengths FAIL 11 of 11 (`readings/c24-routed-half.txt`) |
| B2 `max_mm` tied to nothing it cites | fixed: `max_mm` required and at most the cited lengths scaled by the delays; 500 mm, no `max_mm` and rows dropped are refused (tests) |
| B3 the eleven counted as decided | re-counted as allowed, pending the layout, here and in `c.json`'s `_edge_allow_why`; C24's lengths and placement bounds recorded (section 2); the placement draft for the layout generator is the first row of section 7; `gen_pcb_c3.py` is not changed (a placement change is the generator owner's and needs the box to test) |
| m1 CONFIG_INPUTS | the two documents declared (section 3) |
| m2 the clock held to the data lines' length | QSPI_SCLK has its own entry at the clock's own 10.38 mm, scaled: 8.0 mm |
| m3 the reference is F.Cu on two layers at 1.0 mm | stated and applied: every limit scaled by 5.572 / 7.154 (section 2) |
| m4 Q3_G's RC | in its basis, as supporting and not a bound |
| m5 the class entries change the EMC return rules on C | stated in section 5, re-take owed |
| m6 HB names the RP2040 bound | section 2 and section 7 |
| m7 citation looseness | pattern, quote length, PDF by page, documents outside the repository refused (tests) |
| m8 SWD reasoning labelled | the entries' `why` and section 2 say it is the session's reading |
| m9 the inputs that left board C's reading | section 5 |
| m10 a series resistor answered before the allowance | fixed with B1 (a test net carries a 22R) |
| m11 rules_status line numbers | brought to this tool |

## 10. What was run, and what was not

On the runner, single test files and SI-001 in scratch only (`VERDICT_DIR` and cwd in the session scratchpad; the
scratch views are `w5si2/tools/scratch_tree.py` copies outside every tree). No gate from `v2/ecad`, no rules_status run,
no renderer in any tree; no box, no purchase, no contact, no agent, no other model. The thirteen models were copied
from `w5si2` into this worktree as ignored files (`ibis_fetch.py --check`: 13 present) and are not committed. The
routed half was run only on stub boards (no KiCad on the runner): a box run of `edge_length.py` on a board file is the
routed reading. `test_requirements` fails five tests (bindings of CON-017, CON-019 and CFL-001 to board A's and B's
generators and netlists, and S-118, S-119 on the trace page) on the base as well: nothing here touches the files they
bind.
