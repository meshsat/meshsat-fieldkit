# w3t decisions and results (MESHSAT-1357, EQ-18, 27 September 2026)

Author: stream w3t (tools, RF-002's transmitter walk). Worktree `fnd/w3t` at main `38dcd764`. Prototype framing: nothing
of the kit is built; every reading below is a desk reading of committed netlists, and no bench measurement exists.

Files written (the task's two): `v2/ecad/tools/tx_inhibit.py`, `v2/ecad/tools/tests/test_tx_inhibit.py`.
Drafts: this file, `HANDOFF.md`, `apply_registry.py`, `readings/`. Nothing committed, nothing pushed, the main checkout
not touched, no gate run with the tree's own evidence as its output. No KiCad box was used: no generator, board file or
netlist changed, so there is no regeneration and no parity to prove (tx_inhibit.py is not in any generator's identity).

## 1. What changed in the tool

- **The SN74LVC1G57 row** (LOGIC, after the 74LVC1G17): TI SCES414P (November 2016), held as
  `v2/vendor/ti/ti-sn74lvc1g57.pdf` (sha256 078364de..., filed in round 8 with its SOURCES.yaml entry
  `panel-emcon-lamp-gate`). Pin map from Pin Functions (DBV, DCK, DRL): In1 1, GND 2, In0 3, Y 4, VCC 5, In2 6; the row
  matches the DBV and DCK lands only (`SOT-23-6|SC-70-6|SOT-363`), as the TI dual gates' rows do. II 1 uA and Ioff
  10 uA (6.5, page 5, over the recommended range, which is -40 to +125 C for every package but BGA, 6.3); input clamp IIK
  -50 mA for VI < 0 only and the input rated to 6.5 V with no VCC condition (6.1), "Inputs are over-voltage tolerant up to
  5.5 V" (8.3.2); page 1's Ioff sentence ("The Ioff circuitry disables the outputs, preventing damaging current backflow
  through the device when it is powered down"); vil_ceiling 1.87 V (VT- minimum at VCC 5.5 V).
- **The function is read by the wiring** (`configs`, `_wired()`, `_unmapped()`): the row holds one configuration,
  Figure 7's "2-Input NOR Gate" (page 9), In1 tied to the part's own GND pin. Table 1 (page 8) with In1 L gives Y H only
  for In2 L and In0 L, so Y = NOR(In0, In2) on pins 3 and 6 into pin 4. Any other wiring returns the family with no gates
  and `unwired` saying what was found; every reader of LOGIC treats it as it treats a gate on a land its map is not for:
  `reach()` stops there (named in `stopped`), the census, the fail-safe solve, `_class_pin`, `_net_sources` and the second
  feed check read its pins UNDECIDED with the wiring named. The VCC pin is still read from the pin map (`_supply_nets`).
- **A HIGH at a Schmitt input never passes** (`vih_gap`, `_threshold`): set on the SN74LVC1G57 and the 74LVC1G17.
- **Comments kept true**: VIL_LOW's list of readers (board C's Schmitt readers read at their 3 V rows), VIH_HIGH's basis,
  the vil_ceiling list, R4T-D45's list; a header paragraph for EQ-18; limit (7) names the unwired case; limits (13) and
  (14) are new.

## 2. Decisions (taken by the session under the owner's standing rule of 26 September 2026)

- **W3T-D1. One configuration, Figure 7's, and every other wiring UNDECIDED.** Options: (a) Figure 7 only; (b) every
  configuration of Table 2 (Figures 4 to 8); (c) clear the three inputs by the Pin Functions table whatever the wiring
  and read no function. Taken: (a). Why: it is the only wiring on the six committed netlists (board C's U14), EQ-18's
  option (a) names it, and the task asks that a different wiring read UNDECIDED; (b) adds rows no board draws, each
  unchecked by a fixture of a real wiring; (c) would clear U14's inputs on the lines while leaving its output's function
  unknown, so a path through it could not be judged and the wiring condition would not bind. Reverse by adding a
  `configs` entry for another figure, with its Table 1 check and a fixture both ways.
- **W3T-D2. The tie is read as In1 on the same net as the part's own GND pin, that net a ground.** Options: any ground
  net; the same net as pin 2; through a resistor to ground. Taken: the same net as pin 2. Why: Table 1's L is referred to
  the part's own GND, and Figure 7 draws In1 joined to pin 2; a resistor or another ground net is a different wiring
  (UNDECIDED), which can refuse a board that works and cannot pass one that does not. Reverse by accepting a named ground
  bond or a resistor value bound, with a fixture.
- **W3T-D3. An unwired part keeps its VCC pin.** Why: the Pin Functions table holds for any wiring, so the part's supply
  domain is still its pin 5; reading it as a wrong land would fall back to the '+' rails on its pins, which for U14 is
  the same net and in general a weaker reading. Reverse by treating `unwired` as `wrong_land` in `_supply_nets`.
- **W3T-D4. A HIGH at a Schmitt input never passes (both Schmitt families).** Options: (a) read VIH_HIGH 2.0 V as for the
  other families (as the 74LVC1G17 was read since round 6); (b) read the 4.5 V row's VT+ maximum (2.74 V) as the bound;
  (c) never pass a HIGH there (UNDECIDED at 2.0 V or more, FAIL under). Taken: (c), for the SN74LVC1G57 and the
  74LVC1G17 alike, as one class. Why: both sheets state VT+ at VCC 3 V and 4.5 V and at no VCC between; the 4.5 V rows
  (2.74 V maximum for both) are above 2.0 V; this tree's own reading of U14 at 3.3 V (gen_sch_c.py, linear between the
  rows) is about 2.04 V, over VIH_HIGH; (b) would rest on an interpolation the sheets do not state. It moves no reading on
  main 38dcd764's six netlists: no logic reader is judged at a held level there (checked by instrumenting
  `_threshold` over the six boards: no call). Reverse where a held sheet states VT+ over VCC 3 V to 3.6 V.
- **W3T-D5. The VT- side stays at the 3 V row.** The 74LVC1G17 was read so since round 6; the SN74LVC1G57's VT- minimum
  at 3 V is 0.84 V, above VIL_LOW 0.8 V, and every row either sheet states at 3 V and above is at or above 0.8 V (1G17:
  0.80, 1.21, 1.45 V; 1G57: 0.84, 1.41, 1.87 V). Named in limit (14) as an inference from rows that rise with VCC, not
  a stated band. Reverse where a sheet states a VT- below 0.8 V inside the band.

## 3. Checks

- **Independent check of the function** (`t_the_nor_the_row_reads_is_the_makers_function_table_with_in1_low_and_only_then`):
  Table 1 transcribed row by row; the four rows with In1 L equal NOR(In0, In2) and agree with FORCE["NOR"]; the rows with
  In1 H equal In2 OR NOT In0 and disagree with a NOR (In2 H, In1 H, In0 L gives H). The page images of pages 8 and 9 were
  read (the block diagram, Table 1, Figure 7's tie of pin 1 to pin 2).
- **Fixtures both ways** (five, at the end of the test file): the row and its wiring (In1 on GND: NOR; on +3V3, on a
  signal, on a ground net other than its GND pin's, floating: UNDECIDED; five-pin land: wrong land); the panel fixture
  with U14 on both lines (PASS at the fixture's pull-downs; FAIL with one more input on TX_INHIBIT_n, naming U14's Ioff;
  UNDECIDED with In1 on +3V3 or on a signal); the walk through a NOR (PASS through "U5 NOR 3->4"; with In1 on +3V3 the
  walk stops at U5 naming its wiring and the transmitter is not reached); the Schmitt HIGH (a 74LVC1G04 reader PASSES,
  the SN74LVC1G57 reader is UNDECIDED naming SCES414P 6.5).
- **Mutations** (scratch copies of the tools directory, each fixture run against each): reading the NOR whatever the
  wiring fails three fixtures; dropping `vih_gap` fails the Schmitt fixture; accepting any ground net for In1 fails the
  wiring fixture.
- **Tests run** (tests/run.py, the modules that read the two files and the scanners that read every tool file):
  test_tx_inhibit, test_tx_inhibit_split_guard, test_artefact_recording, test_gate_fixtures, test_import_before_use,
  test_swallowed_calls, test_swallowed_code, test_driver_hygiene, test_documented_options, test_verdict_channel: 318
  passed, 0 failed, 2 skipped (no pcbnew on the runner). The full suite was not run.
- **Gate that reads the file**: check_contracts.py on main 38dcd764's six netlists with VERDICT_DIR in the stream's scratch,
  before and after: check_contracts PASS of 96 both times.

## 4. Readings on main 38dcd764's six netlists (verdicts in scratch; netlists A 3a786cf3, B adcc3c67, C 11eabc2d, D 0dad82b4, E f3c1ad61, P 085f8333)

| board | before (main's tx_inhibit.py, sha256 1d01e6d2) | after (sha256 67cba7a5) |
|---|---|---|
| A | INCONCLUSIVE: 0 fail, 5 pass, 4 undecided | FAIL: 1 fail, 6 pass, 2 undecided |
| B | FAIL: 10 fail, 3 pass, 7 undecided | FAIL: 11 fail, 6 pass, 3 undecided |
| C | INCONCLUSIVE: 0 fail, 4 pass, 2 undecided | FAIL: 1 fail, 5 pass, 0 undecided |
| D | INCONCLUSIVE: 0 fail, 6 pass, 2 undecided | FAIL: 2 fail, 6 pass, 0 undecided |
| E | PASS: 1 pass | PASS: 1 pass |
| P | PASS: 1 pass | PASS: 1 pass |

What moved (the walk's 25 results, `readings/walk-before-main-38dcd764.json` against `readings/walk-after-w3t.json`):
- The EMCON_HW line: UNDECIDED at C U14 pin 6 to PASS (with board C unpowered it read 0.33 V from the known currents;
  U14's 10 uA Ioff is now counted and it stays under 0.8 V on R58 4.7 k and R102 10 k).
- Board B's RockBLOCK 9704 and E22-900M30S: UNDECIDED (their line) to PASS.
- The TX_INHIBIT_n line: UNDECIDED at C U14 pin 3 to FAIL (finding W3T-F1 below).
- Board D's SA868 keying: UNDECIDED to FAIL (it inherits its line; its own released-pin threshold stays undecided behind it).
- No other verdict moved. Corrected at integration (r8int5, from the independent check of 27 September 2026): the
  texts of five results whose verdict stayed UNDECIDED also changed, the LimeSDR Mini 2.4, both E72 CC2652P, the 30 W
  VHF PA and the QMX HF, each losing the clause 'its line EMCON_HW is undecided (the line result names why)'; the two
  walk JSONs in `readings/` differ in 10 details, not 5. Every other result's text is byte-identical.

## 5. Finding W3T-F1 (a FAIL under the walk's worst-case leakage convention)

Corrected at integration (r8int5, from the independent check): the FAIL rests on the walk's round 6 convention, an
unpowered part passes its Ioff and a part that may be either passes the larger of II and Ioff. The three sheets also
state II at VCC 0 V (SCES414P 1 uA, DS35124 5 uA, SCES217AA 5 uA, each for VCC 0 to 5.5 V): with only U14 at II the
line reads about 0.77 V, and with U9, U14 and board D's U12 at II about 0.42 V. So W3T-F1 is a FAIL under the tree's
worst-case convention, not a demonstrated defect; remedy (a) stays recommended as margin, since it also widens the
idle HIGH margin. The walk applies VIL 0.8 V to every family; TI states 0.9 V for board A's SN74AUP1G08 (SCES502Q, VCC
3 V to 3.6 V) and 0.8 V for board D's U12, which reads the line in the states where only board C is off, so the verdict
stands either way.

With board C unpowered, TX_INHIBIT_n is held only by its three 100 kOhm pull-downs (board A R145, board B R59, board D
R2; 35 kOhm together at the 5 percent a value that states none is taken at) against 31 uA of stated pin current: board
C's U9 (74LVC1G17, Ioff 10 uA, DS35124 Rev. 8-2) and U14 (SN74LVC1G57, Ioff 10 uA, SCES414P 6.5), board D's U12
(74LVC1G08, 10 uA, powered or not), board A's U35 and U37 (SN74AUP1G08, II 0.5 uA each). 31 uA x 35 kOhm = 1.09 V, over
the 0.8 V VIL the walk applies to the gates that read it (0.9 V stated for A's U35 and U37, 0.8 V for D's U12); the pull-downs hold at most 22.9 uA under 0.8 V. Without U14 the same
state read 0.74 V. RF-002 asks that "the inhibit is asserted by the unpowered and disconnected states", so the line
FAILS on A to D and board D's SA868 keying with it. Options, each checked with the walk on an in-memory copy of the
netlists (scratch only), all three reading the line PASS:
- (a) board C: R14 10 k to 2.2 k 1 percent and a new 10 k 1 percent pull-down on TX_INHIBIT_n on board C. Failed safe
  0.24 V; idle HIGH 2.57 V nominal, 2.37 V at the adverse ends (+3V3 5 percent low, R14 high, pull-downs low, 31 uA
  sunk); the toggle sinks 1.6 mA. One board, the one whose round 8 added the load. **Recommended.**
- (b) board B's R59 to 10 k 1 percent and R14 to 2.2 k 1 percent: 0.26 V; idle 2.61 V nominal, 2.41 V adverse. Two boards.
- (c) the three pull-downs to 47 k and R14 to 4.7 k 1 percent: 0.51 V; idle 2.54 V nominal, 2.27 V adverse. Four boards.
For comparison, main's own idle HIGH is 2.54 V nominal and 2.11 V at the adverse ends, against a VT+ this tree reads as
about 2.04 V at 3.3 V for U14 and about 2.15 V for U9 (gen_sch_c.py's notes; corrected at integration, U9's
figure is gen_sch_c.py line 181's): every option above also widens that margin. The choice and
its regeneration belong to board C's stream (option a) or to the streams of the boards each option names; the registry
item is drafted (`apply_registry.py`, the next free S-nn, S-48 in this tree).
