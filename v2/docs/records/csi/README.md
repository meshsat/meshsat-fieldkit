# Stream csi: board C's SI-001, the 23 layout-bound nets decided (layer 9, MESHSAT-1357)

Written 29 September 2026 on branch `fnd/csi`, base `e553e43a` (`fnd/int13`, set 12, board C's latest generator).
Prototype design work: nothing here has been built, ordered or measured. No reading on this page is a PASS. The
decisions below are the session's under the owner's ruling of 21 September 2026 and his standing rule of 26 September
2026 (authority SESSION); none is the owner's. The work is a desk stream's, not a qualified engineering review.

## 1. The item and the result

SI-001 on board C read INCONCLUSIVE with 23 layout-bound nets, every one decided by a bound (a driver with no published
minimum edge: critical length 0.0 mm), and one net undecided for want of a class (`v2/ecad/pcb-c-display-c8/routed/edge_length.verdict.json`,
netlist sha256/16 `87b69472ac83ca5a`). Taken again in scratch (every reading under `readings/`):

| Reading | Signal | Slow | Decided | Undecided | Answered (by edge_allow) | Layout-bound | Result |
|---|---|---|---|---|---|---|---|
| before: base tool and table, committed netlist | 135 | 101 | 33 | 1 | 10 (0) | 23 | INCONCLUSIVE |
| declarations of this branch, committed netlist | 135 | 103 | 32 | 0 | 21 (11) | 11 | INCONCLUSIVE |
| after: the circuit draft applied in a scratch view, stand-in netlist | 139 | 103 | 36 | 0 | 29 (11) | 7 | INCONCLUSIVE |

**16 of the 23 are decided** (4 by a series termination at the driver, 11 by a declared allowance whose basis the tool
holds, 1 by a class correction on content); **7 stay open**, each named in section 7 with its next action. The one
undecided net (EMCON_HW_DRV, not among the 23) is declared as well. Board B's SI-001 is unchanged (section 5).

## 2. The 23 nets, one by one

The maker's edge was asked first (`readings/maker-search-2026-09-29.txt`): Raspberry Pi publishes no IBIS model of
the RP2040 (its Product Information Portal lists the datasheet, the hardware design guide, the product brief and the
minimal KiCad design, nothing else; its documentation repository and GitHub hold none) and no minimum transition;
Diodes publishes no IBIS model of the 74LVC1G34; TI's PCA9555 model is held and its INT pin is flagged (ER-D16); the
W25Q16JV's model would decide nothing while the RP2040 shares every QSPI net (ER-D13). So no net is decided by a
maker's figure, and the next means were taken in the brief's order.

| Net | Governing driver(s) | Decided by | Source |
|---|---|---|---|
| EPD_SCL | RP2040 GPIO2 | series termination at the driver: R53 27R, U3 side EPD_SCL_R (CSI-D3, a draft) | hardware design guide p. 12, "these I/Os do require 27 Ω series termination resistors" (the maker's value on this chip's USB pins); the value is INFERRED for a GPIO pad |
| EPD_SDA | RP2040 GPIO3; the panel's UC8253C only in a read | the same, R54 | as above; PANEL.md: "MOSI only, the display's read path is unused" |
| EPD_DC | RP2040 GPIO4 | the same, R55 | as above |
| EPD_CS | RP2040 GPIO5 | the same, R56 | as above |
| QSPI_SCLK, QSPI_D0 to D3 | RP2040 QSPI pads; W25Q16JV | edge_allow, held at 16.8 mm (CSI-D4) | hardware design guide p. 10: "the QSPI pins of RP2040 should be wired directly to the flash, using short connections to maintain the signal integrity" (so a series resistor is against the maker's guidance); the maker's minimal design routes clock and data at 8.20 to 16.85 mm |
| QSPI_SS | the same | edge_allow, held at 22.7 mm (CSI-D4) | the same words; the maker's QSPI_SS with its BOOTSEL resistor: 22.73 mm |
| XIN | RP2040 XOSC (bound) | edge_allow, held at 11.2 mm (CSI-D5) | p. 11: "Try and keep the layout as short as possible."; the maker's XIN 11.23 mm; CLK-001 holds the network (stray 3 pF, one series resistor) |
| XOUT_R | the same | edge_allow, held at 2.7 mm (CSI-D5) | the maker's pin-to-1 k run, 2.76 mm |
| XOUT | the same | edge_allow, held at 5.2 mm (CSI-D5) | the maker's 1 k-to-crystal node, 5.26 mm |
| SWCLK | a bench probe on TP1 | edge_allow, held at 25.9 mm (CSI-D6) | datasheet p. 62: "Each DAP will only respond to debug commands if correctly addressed by a SWD TARGETSEL command; all others tristate their outputs."; FAR-BENCH-PROBE; the maker's SWCLK 25.92 mm |
| SWDIO | RP2040 SWD, only when a probe addresses it | edge_allow, held at 24.3 mm (CSI-D6) | the same; the maker's SWD 24.34 mm |
| Q3_G | across R37 (1 k): board D's U18 74LVC1G34 and the RP2040's GPIO23 (ER-D10) | class LOW_SPEED_OR_DC ahead of `Q?_G` (CSI-D7, W5SI2-D2 taken) | a copy of TR_APRS, which the table declares a static level; the lamp FET's gate, as EMCLAMP_G is (W5SI2-D1) |
| EPD_SW | the e-paper boost's switch node | **open** | W5SI-D3 stands: no rule holds a power stage's copper, so no declaration is written |
| HB1, HB2, HB3 | board B's level shifters Q105, Q205, Q305 (drains, 10 k pull-ups) and supervisors | **open** | the drivers are board B's; a termination at them is board B's generator's |
| SCL, SDA | the kit bus on boards A, B, C and D | **open** | kit-wide (UM10204 7.3), and the three-segment design SC-HF-02 is not drawn |
| EXP_INT | the wired-OR interrupt on boards A, B, C and D (PCA9555 INT flagged, KSZ9897, TPS23861, DS3231, RP2040) | **open** | kit-wide, as SCL and SDA |

EMCON_HW_DRV (U9's own output to R52, since stream d4emcon) had no class entry; it is declared LOW_SPEED_OR_DC on its
content, the EMCON level (CSI-D8).

"Held at" is the declared `max_mm`: the length the layout may route the net, which the SI-001 table hands to the
layout (`length_limits`) and the routed half holds (section 3). The lengths are Raspberry Pi's own reference layout
(`tools/measure_minimal.py` over RP-008296-DS, MIT licence, sha256 of the archive and of the board file in
`readings/minimal-layout-lengths.txt`; the archive is not committed). They are the layout at which the maker's design
runs these nets: a board that routes them no longer is inside what the maker has drawn. The maker's board is two
layers at 1.0 mm; ours is four or six layers, so a crystal track of the same length carries more capacitance, which
is CLK-001's question (its 3 pF stray allowance), not SI-001's.

## 3. The tool change: an allowance carries its basis and the length it holds (edge_length.py)

Until today an `edge_allow` entry was a pattern and a sentence, and a sentence turned a net green: finding F-Q1
refused to write one for that reason (W5SI-D3, "a declaration names what holds a net's length"). No board carried one.

- **CSI-D1.** An entry answers a net only with its basis held the way a record of `pcb_edge_rates.yaml` is: `why`,
  `ruled_by`, and a citation (`document`, `sha256_16`, `page` or `where`, `quote`, and `checked`), held by the same
  checks (`_cite_shape`, `_quotes_hold`) on every run. A refused entry FAILS the reading and its nets stay
  layout-bound. The documents a held entry cites are inputs of the reading by sha (`document_N`).
- **CSI-D2.** An entry may state `max_mm` with `max_mm_basis`. The schematic table records it per net
  (`length_limits`), the evidence line `ALLOWED` names it, and the routed half (`edge_length_routed`) answers the net
  by the entry only while its routed length is at most that; past it the net is named and the routed verdict fails.
- A new count, `allowed_nets` (inside `answered_nets`; no sum changes).

Tests (`tools/tests/test_edge_length.py`): the old test that passed a board on a bare sentence now shows it refused
and FAIL, then PASS with a cited entry; `t_si001_an_allowance_answers_only_with_its_basis_held` (five refusals, each a
FAIL with the net layout-bound, and a held pair answering with its document recorded); `t_si001_an_allowance_hands_its_length_to_the_layout_and_the_routed_half_holds_it`;
`t_si001_the_board_tables_allowances_hold_against_their_documents` (the committed tables; it failed on the base
table, "no board table carries an edge_allow entry"). Run: `run.py edge_length signal_class netclass netlist_classes
rules_registry ibis_models`, 80 passed, 0 failed (`readings/tests-2026-09-29.txt`). The routed half needs pcbnew and
is exercised through `allow_answers`, its one decision.

## 4. The circuit change, drafted: `apply/apply_board_c_epd_series.py`

For the owner of `gen_sch_c.py`. U3's pins 4 to 7 move to EPD_SCL_R, EPD_SDA_R, EPD_DC_R and EPD_CS_R, and R53 to
R56 (27R, 0603, coded C25190 by `lcsc_fill.py` as R2 and R3 are) join each to its line; the lines keep their names
from the resistor to J_EPD, so the far-end record C-EPD and every reader of J_EPD are unchanged. It also writes the
four class entries (CLOCKED_DIGITAL) into `boards/c.json` ahead of the glob `EPD_*`, which is LOW_SPEED_OR_DC. It
asserts every anchor once, checks R53 to R56 are free in the committed netlist and the generator, parses the new
generator and reads U3's map and the four `r()` calls back from the parse, writes c.json in its own format and reads
it back, refuses a second run (exit 2), and has `--dry-run` and `--root`.

Read-back: `apply/readback_board_c_epd_series.py <netlist>`, sixteen checks (each stub carries only U3's pin and its
resistor's pin 1, 27R, the line carries the resistor's pin 2 and J_EPD's pin and no U3 pin). On the committed netlist
it FAILS 16 of 16; on the stand-in netlist (`tools/sim_netlist_c.py`, a text rewrite of the committed netlist for this
reading only, never a regenerated netlist) it HOLDS 16 of 16. Applied in a scratch view: first run written, second run
refused (`readings/apply-and-readback.txt`).

**What waits on regeneration:** the schematic, netlist and intent of board C regenerated on the box from the applied
generator; the read-back on that netlist; the four resistors placed within a few millimetres of U3's pins by
`gen_pcb_c3.py` (today it packs every such resistor into the cluster region, R2 and R3 included); SI-001 re-taken.
Until then the committed netlist has no R53 to R56 and the four class entries match nothing.

## 5. Board B, and the other boards

SI-001 on board B taken with the base tool and table and with this branch's: identical verdict (INCONCLUSIVE), counts
(908 signal, 184 layout-bound), evidence, inputs and table rows; the only difference is the new key `allowed_nets: 0`
(`readings/si001-b-before.txt`, `-after.txt`). No other board table carries an `edge_allow` entry, so CSI-D1 and
CSI-D2 change no other board's reading. The tool's code bundle changed, so every board's SI-001 reading is stale by
code until re-taken.

## 6. For the integrator, in order

1. Merge `fnd/csi` (with the owner's `-c` flags). Commit before any rules_status run: `tools/boards/c.json` and the
   records under `v2/docs/records/csi/` are inputs the readings cite by sha.
2. `python3 v2/docs/records/csi/apply/apply_board_c_epd_series.py` on the integrated tree (or not: the four e-paper
   nets then stay layout-bound and the allowances still stand). Then regenerate board C on the box and run
   `readback_board_c_epd_series.py` on the new netlist; commit only behind its HOLDS line.
3. The models fetched where the re-take runs (`python3 v2/ecad/tools/ibis_fetch.py --fetch`, then `--check`), then
   SI-001 re-taken on all six boards with `retake_gate.sh` (the tool's code changed).
4. `rules_render.py` if the coverage note of SI-001 is updated to say that board tables now carry allowances.
5. Optional: file CSI-D1 to CSI-D8 as rows of `pcb_decisions.yaml` on the pattern of `w5si/apply/apply_decisions_w5si.py`
   (with its rebind of the requirement records bound to that file, then `decisions_render.py`). The rows' fields are
   already on each board-table entry (ruled_by, ruled_on, authority, authority_why, reverse).

## 7. Open, each with its next action

| Open | Next action | Whose |
|---|---|---|
| EPD_SW | the power-stage rule of F-Q1 section 4, then the SW net class in `gen_pcb_c3.py` (F-Q1 section 5 item 5) | the registry writer, then board C's layout generator owner |
| HB1, HB2, HB3 | a series termination at each heartbeat's driver on board B (the level shifters' drains), then an `edge_allow` on board C naming it with its basis | board B's schematic owner |
| SCL, SDA, EXP_INT | a kit-wide decision: series resistors at the drivers (UM10204 Rev. 6, 7.3) or a bus allowance with a held basis, after the three-segment design SC-HF-02 is drawn; bench item V-K01 | layer 5's owner, boards A to D |
| the routed half's length limits decide no rule | bind `edge_length_routed` (or a successor) to a layout-phase rule so `max_mm` is held by a deciding reading | the registry writer |
| the 27R value | measured at bring-up: the edge at J_EPD at the drive the firmware sets | bring-up |
| the four resistors' placement | a site at U3's pins in `gen_pcb_c3.py` (the same is owed for R2 and R3, the USB pair) | board C's layout generator owner |
| the crystal nodes' stray | a layout-phase reading of the pins-and-tracks capacitance against CLK-001's 3 pF | CLK-001's owner |

## 8. Decisions taken (authority SESSION)

| Id | Decision | To reverse |
|---|---|---|
| CSI-D1 | an `edge_allow` entry answers only with its basis held; a refused one FAILS the reading | accept `why` alone in `allow_refusal` |
| CSI-D2 | `max_mm` is handed to the layout and held by the routed half | drop the length test in `allow_answers` |
| CSI-D3 | the four e-paper lines take 27R at the RP2040's pins (drafted, not applied) | delete R53 to R56, U3 pins back on the lines |
| CSI-D4 | the QSPI nets are answered by an allowance, not a series resistor, held to the maker's reference lengths | delete the three entries |
| CSI-D5 | the crystal nodes likewise, with CLK-001 holding the network | delete the three entries |
| CSI-D6 | the SWD nets likewise, on the port being driven only with a bench probe attached | delete the two entries |
| CSI-D7 | Q3_G is LOW_SPEED_OR_DC on content (W5SI2-D2 taken) | delete the `Q3_G` class entry |
| CSI-D8 | EMCON_HW_DRV is LOW_SPEED_OR_DC on content | delete its class entry |
| (kept) | W5SI-D3: no declaration for EPD_SW | as F-Q1 says |

## 9. What was run, and what was not

On the runner, single test files and SI-001 in scratch only (`VERDICT_DIR` and cwd in the session scratchpad; the
scratch views are `w5si2/tools/scratch_tree.py` copies outside every tree). No gate from `v2/ecad`, no rules_status,
no renderer in any tree; no box, no purchase, no contact, no agent, no other model. The thirteen models were copied
from `w5si2` into this worktree as ignored files (`ibis_fetch.py --check`: 13 present) and are not committed. The
test files `test_requirements` (five tests, bindings of CON-017, CON-019 and CFL-001 to board A's and B's generators
and netlists, and S-118, S-119 on the trace page) fail on the base as well (59 passed, the same 5 failed, in a scratch view holding
the base's versions of this branch's three changed files): nothing here touches the files they bind.
