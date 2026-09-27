# Board B, stream w4b (MESHSAT-1357, 27 September 2026): RF-002, every transmitter's kill reachable from EMCON in hardware

Base: main `91894cd7`. Worktree `fnd/w4b`. Author of `v2/ecad/tools/gen_sch_b.py`, `v2/ecad/tools/boards/b.json` and board B's
regenerated schematic-phase files under `v2/ecad/pcb-b-compute-b19/` (schematic, netlist, intent, provenance sidecar). Nothing
is committed or pushed. Prototype framing: no board of the set has been built; every figure below is a maker's published figure
or arithmetic on one, or is marked INFERRED. This is a source-backed desk review of the changes, with the writers that read
them re-taken in scratch; it is not an automated PASS of anything the writers do not read. Every engineering choice is taken
by the session under the owner's standing rule of 26 September 2026, never as the owner's.

Files at the end of the stream (sha256/16): generator `60d577263816491c` (main `6957adda1bb5f23a`), netlist `028997a6c5e8810f`
(main `8b78c59754a6a0c7`), schematic `447dc56525eb0ae2`, intent `96ee391b3e3f638d`, sidecar `8a57607ba1c0dfa8` ("written by
this tree's own generator").

## 1. What the goal asked, and what the netlist said

The goal: `inhibit_chain_b` (RF-002) FAILs 11 of 20 on current evidence; make every transmitter's kill reachable by the EMCON
hardware line without firmware, as a dominant hardware path meeting EMCON.md section 5a's latency and fault conditions, choose
each path from the makers' documents, classify the radio census, and draft the EMCON.md and ARCHITECTURE rows.

What the walk's own output says (`evidence/walk/main-netlists_main-tool.txt`): nine of the eleven FAILs are the walk stopping
at the SN74LVC2G06 ("the walk stopped at U113 ... (no pin map)"), for which `tx_inhibit.py` holds no row; the tenth is the
census, which reads U221 (a TPS3808 supervisor whose value names the RM520N) as an unclassified radio; the eleventh is
`TX_INHIBIT_n`'s fail-safe state (W3T-F1, EQ-25, board C). The circuits those nine rows rest on are round 8's and were already
dominant hardware paths per maker's document: the CM5's `WL_nDisable` and `BT_nDisable` ("may only be driven low", pulled low
by U{s}13 open drains from `EMCON_ON{s}`, CM5 datasheet 2.1.1 and 2.1.2), the RM520N-GL's `W_DISABLE1#` and
`FULL_CARD_POWER_OFF#` (U215, U220) and its supply removed at once (SD-EMC-1r8), and each AW7915-AED's supply (its
`W_DISABLE1#` has no maker statement, adjudication A11, so the supply is the path). So the per-path choice the goal names is
already the makers' choice, and the circuit work of this stream is what those paths still lacked against section 5a:

- the RockBLOCK 9704's ENABLE was held by U6 alone while the module runs on its own supercapacitors (EMCON.md 4.4, 5a row 4);
- L4 case (2): U501 to U504 in their unspecified 0 to 1.65 V supply band could turn a radio's switch on (fault F6);
- fault F2 on the card rails, found here: once the walk was given the SN74LVC2G06's row (a draft), it read each card buck's
  enable with U{s}15 unpowered (the module's 3.3 V down, the slot's 5 V up) held only by 110 k against the AP64500's EN current,
  which has no stated maximum once the buck is on (DS41979), so a card, slot 2's 5G module included, could stay powered beyond
  EMCON's reach.

The LimeSDR's and the E72s' UNDECIDEDs are the walk's back-feed reading of their gated rails (the USBLC6-2's VBUS, the cJTAG
bench headers, the CP2102N pulls), not their kill paths, whose choice (the supply) the makers' documents set: the LimeSDR takes
its only power from USB VBUS (MyriadRF page, A11's copy), and each E72 has one supply pin on board B, pin 20 on the gated +3V3_ZB (EMCON.md 4.15).

## 2. Circuit changes (gen_sch_b.py; board B regenerated with main's chain)

| id | change | source | reversal |
|---|---|---|---|
| W4B-D1 | U536 (SN74LVC1G08, +3V3_DEV, C7666, 100 nF C559) drives `RB_IEN` (J_RB9704 pin 3, the RockBLOCK's I_EN) = `EMCON_HW AND RB_SW_IEN`; U6 pin 19 now drives the request `RB_SW_IEN`; R527 10 k holds `RB_IEN` low with U536 unpowered (0.10 V), R528 4.7 k holds the request low at power-on (0.47 V against U6's 100 uA pull-up) | Ground Control hardware page (fetched 27 September 2026, `datasheets/`): I_EN "is used to initiate startup and shutdown of the 9704 module", a 270k/430k divider "pull-up to the input voltage", "a series 10KOhm resistor", "can be driven directly with an MCU pin, or an open-drain output"; schematic rev 2B page 3 (R33, R32, R6, U2 74AUP1G125 on 3V3_IRID, "U2 V_IN_H_MIN = 2.0V"); TI SCES217AA 5.3, 5.5 | U6 pin 19 back on `RB_IEN`; U536, C559, R527, R528 out |
| W4B-D2 | the EN/UVLO of U23, U24 (TPS259631) and U21 (TPS22810) on their own nodes `LIME_UVLO`, `RB_UVLO`, `E22_UVLO` at 0.6 of the gate's output: R529 to R531 10 k 1 percent (C25804) in series, R514 to R516 now 15 k 1 percent (C22809) to GND; the three rails' intent names `switch` and `enable_net` (power_sequence reads EN by name); U505's E72_EN keeps its 10 k | TI SLVSET8A 7.5 (VUVLO(R) 1.22 V max, VUVLO(F) 1.08 V min, VSD 0.53 V min), SLVSDH0C 7.5 (VENR 1.30 V max, VENF 1.08 V min, VSHUTF 0.5 V min), SCES217AA 5.3 (VO 0 to VCC) and 5.5 (VOH 2.4 V at 16 mA, Ioff 10 uA); board A's SD-A8-3 | enables back on the gate outputs, R514 to R516 at 10 k, R529 to R531 out, the intent's `switch`/`enable_net` out |
| W4B-D3 | U116, U216, U316 (TI SN74LV1T08DBVR, C2682144, on +5V_S{s}, 100 nF C607, C637, C667) drive each card buck's EN `S{s}A_EN` = `EMCON_HW AND PCIE_PWR_EN{s}` push-pull; R164, R264, R364 removed; U115, U215, U315's second channel freed (2A on GND, SCES307J 6.3 note 1; 2Y open) and their value text says so; +5V_S{s}'s intent loads name U{s}16 | TI SCLS739F 6.3 and 6.5 (VCC 1.6 to 5.5 V; VIH 2.03 V at 4.5 to 5.0 V, 2.11 V at 5.5 V; VIL 0.8 V; VOL 0.1 V at 20 uA, 0.35 V at 8 mA; VOH 4.5 V at -8 mA; II +-1 uA at VCC 0 to 5.5 V), 9.1 (0.1 uF); Diodes DS41979 Enable and UVLO sections (EN a high-voltage pin; 1.5 uA source, 4 uA hysteresis; VEN_H 1.25 V max, VEN_L 1.03 V min; VIN UVLO 3.5 V typ, 3.7 V max rising) | R{s}64 from `PCIE_PWR_EN{s}` to `S{s}A_EN`, U{s}15's 2Y back on it, U{s}16 and its capacitor out |

The numbers each change rests on are in the generator's comment beside it and in the draft EMCON.md section 4c
(`page_drafts_w4b.py`). The part choices: the SN74LVC1G08 is the reel board B already buys for its EMCON gates; the
SN74LV1T08 is the TI part that reads a 3.3 V signal from a 5 V supply with 5.5 V tolerant inputs and a stated input current at
VCC 0 V, which the LVC family at 5 V cannot (VIH 0.7 x VCC, 3.57 V). Its maker's sheet is fetched and drafted for
`v2/vendor/ti/` (`sources-entries.yaml`).

## 3. Session decisions (drafted as SC-58 to SC-60 at the next free numbers by `apply_registry.py`)

| # | decision | why | what is given up | reversal |
|---|---|---|---|---|
| W4B-D1 | the RockBLOCK's I_EN is an AND of EMCON and the request, with a pull-down; Ground Control's I_EN/I_BTD sequencing warning, met by an EMCON during the module's boot, accepted as a stated residual | section 5a row 4 asks for the supply AND the ENABLE by hardware; the maker's own divider makes the same edge on every loss of external power, which EMCON also causes at that instant | nothing (the request keeps full control while EMCON is released) | as in section 2 |
| W4B-D2 | board A's divider remedy, not a supervisor | a stated bound at every band edge with parts board A already buys | 0.13 mA per enable while high | as in section 2 |
| W4B-D3 | a gate on the buck's own input driving the enable directly; U{s}15's 2Y taken off the node | the only choice that bounds the node in fault F2 from held documents: the EN current has no stated maximum once on, so any resistor between a driver and the pin leaves it unbounded; an open drain beside a push-pull gate would fight it whenever the two disagreed | a second EMCON path onto the node (U{s}15's 2Y from `EMCON_ON{s}`), which failed in exactly the state this closes | as in section 2 |
| W4B-D4 | the census and the walk's model gaps are drafted for the tools author, not worked round in the circuit | a value string or a part picked to please a checker is a rule about the tool, not the circuit (U221 keeps its value; the SN74LVC2G06 stays) | the merged walk reads board B worse until the rows land (section 4) | none needed |
| W4B-D5 | the new gates' value text names no power-part word | `test_rails_census` treats a part whose value says "buck" as a power part needing a PIN_ROLES row; the gates deliver no supply | none | none needed |

## 4. Readings, before (main 91894cd7) and after (the candidate), in scratch

The consolidated re-take driver (`retake_schematic_phase.py --run --board b --verdict-dir`) on the KiCad box, in clean scratch
trees: main as committed; the candidate with its regenerated board B committed as a scratch commit; and each of those with the
tool rows drafted for the tools author (`tools/apply_tx_inhibit_w4b.py`). Evidence: `evidence/retake/{rtb,cand,mt,ct}`.

| reading | main | candidate, main's tools | main + drafted rows | candidate + drafted rows |
|---|---|---|---|---|
| inhibit_chain_b (RF-002) | FAIL: 11 fail, 6 pass, 3 undecided | FAIL: 11, 3, 6 | FAIL: 3, 13, 4 | FAIL: 1, 15, 4 |
| inhibit_chain_a | FAIL: 1, 6, 2 | FAIL: 1, 5, 3 | FAIL: 1, 6, 2 | FAIL: 1, 6, 2 |
| inhibit_chain_c | FAIL: 1, 5, 0 | FAIL: 1, 4, 1 | FAIL: 1, 5, 0 | FAIL: 1, 5, 0 |
| erc_gate | PASS of 2912 (7 allowed) | PASS of 2945 (the same 7 allowed errors; the new are warnings of the classes already there) | as main | as candidate |
| derate | PASS of 240 (425 unrated) | PASS of 240 (429 unrated: the new gates and resistors) | | |
| edge_length | INCONCLUSIVE, 882 signal nets | INCONCLUSIVE, 886 (the four new nets low-speed) | | |
| pin_map_lands_b | PASS of 1270 | PASS of 1280 | | |
| intent_rails (PWR-001), power_sequence, check_contracts, clock_check, energy_chain_b, interfaces_b, port_protect_b, safe_lines_b | PASS | PASS (power_sequence read INCONCLUSIVE on an intermediate candidate until the three rails named their enable net; fixed in the generator) | | |

With the drafted rows, board B's 20 results: the one FAIL is `TX_INHIBIT_n`'s fail-safe state (W3T-F1, EQ-25, board C's round);
PASS are the six CM5 radios, both AW7915 cards, the RockBLOCK's supply, the E22, the `EMCON_HW` line (0.58 V worst bound, 0.50 V
on main) and the census; UNDECIDED are the LimeSDR (U33's VBUS on `+5V_LIME` beside the hub's pins), both E72 (the cJTAG
headers, the other module's pin 20, the CP2102N's RTS and DTR behind R28 to R31) and the RM520N-GL (U221, the TPS3808 on the
socket rail it watches, in no class of the walk). With main's tools the candidate reads worse on A, B and C because the walk
cannot read U116 to U316 on `EMCON_HW`: the rows and the board change must be integrated together.

`check_pcb_b.py` is a placed-board gate and no placement exists for this netlist: its EMCON block, run on the netlists by
`tools/emcon_block_harness.py` (evidence/check_pcb_b/): main's gate reads 31 of 31 on main and 7 FAIL on the candidate (the
round 8 topology assertions this stream moves); the drafted gate reads 32 of 32 on the candidate and refuses main (8 FAIL);
two value mutations (R514 at 10 k 1 percent, R516 at 47 k 1 percent) are each refused.

Tests (`tests/run.py sch_prov energy_chain order_codes interfaces tx_inhibit rails_census rails_netlist last_net kisch_tvs
signal_class requirements kelvin_check phase_directory gate_fixtures`): on the worktree with this stream's files only, 418
passed, 4 failed (test_requirements: the registry readings bound to the old generator and netlist, which `apply_registry.py`
rebinds), 6 skipped; on a throwaway worktree with every draft applied and the trace page re-rendered, 428 passed, 0 failed,
5 skipped, and `rules_lib.py requirements` reads 144 records, 0 errors, 0 warnings.

## 5. Parity (box 52646493, `tools/w4b_box.sh`)

- Main's generator against main's committed board B files: schematic PARITY, netlist, intent, provenance and ERC
  PARITY_AFTER_NOISE, BOM PARITY.
- The candidate against main, read by the integration's own comparator (`v2/docs/records/r8b/integration/indep_cmp.py`) with
  `expected_w4b.json`: 13 parts added (U536, C559, R527 to R531, U116, U216, U316, C607, C637, C667), 3 removed (R164, R264,
  R364), 6 changed (R514 to R516's value and code; U115, U215, U315's value), 7 nets added (RB_SW_IEN, LIME_UVLO, RB_UVLO,
  E22_UVLO, and U{s}15's freed pin 4), 19 changed; 0 unexplained against the committed netlist and against main regenerated;
  dropping W4B-D1's parts, W4B-D2's net changes, W4B-D3's removals or W4B-D3's net changes is refused (4, 3, 3 and 14
  unexplained).
- Determinism: the candidate generator twice gives an identical schematic.
- The box ran with `boards/b.json` at sha256/16 `92fd9bbd5b1d1100`; after it only the `_emcon_w4b_why` note was reworded (now `2cedcd91cb6198df`), which no generator input (`gen_env`) and no writer reads.

## 6. Drafts for other owners (applied together in a throwaway worktree; see section 4)

- `tools/apply_tx_inhibit_w4b.py` and `tools/apply_tx_inhibit_tests_w4b.py` (tools author): the SN74LVC2G06 and SN74LV1T08
  rows with their makers' words, the AO3400A as an N-channel FET, U221 and J_QMX in ACCESSORIES (QRP Labs' schematics, EMCON.md
  4.3), a `vil_ok_bands` field read by `_vcc_ok` (the LV1T08 states VIL 0.8 V at 4.5 to 5.5 V and 0.65 V at 3 to 3.6 V), and the
  three test changes they need; 179 tests of tx_inhibit, rails_census, interfaces and energy_chain pass with them.
- `tools/apply_check_pcb_b_w4b.py` (board B gate owner): the EMCON block's three assertions this stream moves, restated with
  their bounds.
- `page_drafts_w4b.py` (EMCON.md, ARCHITECTURE.md, PANEL.md, pcb_interfaces.yaml): EMCON.md section 4c and its rows, the
  ARCHITECTURE section 6.3 rows and three section 13.4 findings, PANEL.md's EMCON_HW row and correction (17), the two
  interface contracts. The claims screen reads 86 of 86 qualified with them.
- `apply_registry.py` (integrator; run after the page drafts): 31 rebinds with notes, FEA-002's ENABLE clause, S-01 restated,
  SC-58 to SC-60 and S-77 at the next free numbers of the tree.
- `sources-entries.yaml` and `datasheets/`: TI SN74LV1T08 (SCLS739F) and Ground Control's RockBLOCK 9704 hardware page, for
  `v2/vendor/`.

## 7. Open

- The Iridium 9704 module's response to ENABLE and the length of its shutdown on its own capacitors: no held document states
  them (Ground Control's page says only that I_EN initiates startup and shutdown); row 4's 1 s L_max is TBD at desk, bench E-04.
- U536's own L4 band (+3V3_DEV between 0 and 1.65 V): its output is unspecified; +5V_RB is off there (W4B-D2), so the module can
  run only on its own capacitors, the bound it had before this stream (bench E-11 with E-04).
- SD-EMC-2 back-feed, unchanged by this stream: the RockBLOCK (`RB_RXD`, `RB_CTRL`, and R41 and R42 pulling the module's
  outputs `RB_STATUS` and `RB_XMTG` up to +3V3_DEV, whose output type no held document states), the E22's SPI and control
  lines, the E72s' CP2102N lines (series resistance needs each interface's edge budget); the AW7915 cards (no maker floor).
- RF-002's instrument (S-77 as drafted): the TPS3808 class (U221), the USBLC6-2 beside a USB hub, declared bench headers and
  CP2102N pulls on a gated rail. `TX_INHIBIT_n`'s fail-safe state is W3T-F1 (EQ-25, board C).
- Q212's conduction over temperature (25 C rows only), bench E-12; every row's bench test (E-01 to E-12).
- The firmware contract (PANEL.md correction (17) as drafted): the panel writes `RB_SW_IEN` low on EMCON and raises it after a
  release only once `RB_STATUS` reads low.

## Ids taken at the r8int6 integration (corrected at integration)

The registry script ran at the r8int6 integration of 27 September 2026 (set 6 of the handover), where other branches had taken the numbers this record names as drafted; the ids it took there, read back from the registry by each record's own text: W4B-D1 is SC-64; W4B-D2 is SC-65; W4B-D3 is SC-66; RF-002 instrument is S-82. Where this record names another number for one of them, the id here is the one the registry holds.
