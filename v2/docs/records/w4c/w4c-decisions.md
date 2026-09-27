# Stream w4c: board C, EQ-25 and PWR-001 (MESHSAT-1357, 27 September 2026)

Author stream `w4c` on `fnd/w4c` at main `91894cd7`, under the owner's handover prompt
(`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`, sections 2 and 4). Prototype framing throughout: nothing of
the V2 kit is built, powered or measured; every figure below is a desk reading of committed or candidate netlists, taken
in scratch on the KiCad box (vast.ai, KiCad 9.0.9), never in the tree's own evidence. Engineering choices are the
session's under the owner's standing rule of 26 September 2026, each with its reason and its reversal, never the owner's.

Files this stream wrote (the task names them): `v2/ecad/tools/gen_sch_c.py`, `v2/ecad/tools/boards/c.json`, and board
C's four regenerated schematic-phase files (`pcb-c-display-c8/pcb-c-display.kicad_sch`, `out/pcb-c-display.net`,
`out/pcb-c-display.net.prov.json`, `out/pcb-c-display-intent.json`). Everything else is a draft in this folder.

## 1. What changed on board C

| Change | Where | Why |
|---|---|---|
| R14 10k (C25804) to **2.2k 1%** (UNI-ROYAL 0603WAF2201T5E, C4190) | `gen_sch_c.py`, the R14 line | EQ-25 option (a) |
| **R50**, 10k 1% (0603WAF1002T5E, C25804), TX_INHIBIT_n to GND | same line | EQ-25 option (a) |
| **R51**, 10k (C25804), RAIL_SENSE to GND | the R15/R16 line | finding W4C-F1 |
| three rails (EPD_VCC, LED_RAIL_SW, LED_RAIL), forty-seven nodes, +3V3's Q5 load 1 mA to 30 mA | the block at the end of the design | PWR-001 on board C (EQ-19) |
| TX_INHIBIT_n safety-line note | `boards/c.json` `safety_lines` | states R14 2.2k and R50 |
| U9 and U14 notes (77 us to 17 us, 2.54 V to 2.57 V), in place, no line added | `gen_sch_c.py` | the old figures were R14 10k's |
| +3V3 0.12 / 0.20 A to **0.149 / 0.72 A** (its own loads plus EPD_VCC), and a check after EPD_VCC's declaration that stops the generator if +3V3 no longer covers it (pass 2) | `gen_sch_c.py`, the +3V3 declaration and after EPD_VCC's | finding W4C-F5 of the independent check |

## 2. Decisions (taken by the session under the owner's standing rule of 26 September 2026)

- **W4C-D1 (EQ-25, S-64, W3T-F1): option (a) on board C.** Options: (a) R14 2.2k 1% with a 10k 1% pull-down on board C;
  (b) board B's R59 to 10k 1% with R14 2.2k; (c) the three pull-downs to 47k with R14 4.7k. Taken: (a). Why: one board,
  the board whose round 8 lamp gate U14 added the Ioff that lifted the line; the lowest failed-safe level (0.24 V against
  0.26 V and 0.51 V); and it lifts the released level at the adverse ends from 2.11 V (under U9's interpolated 2.15 V VT+)
  to 2.37 V. Reverse by (b) or (c) if a measured Ioff (bench E-01, E-11) or a later reader on the line changes the sums.
  Registry: the first of the three session choices `apply_registry.py` adds (SC-58 on main 91894cd7), which closes S-64.
- **W4C-D2 (PWR-001 kinds on board C).** Rails for EPD_VCC, LED_RAIL_SW and LED_RAIL; a node for C_DVDD (the RP2040's own
  regulator output); nodes for the eleven undecided nets and for the lamp feed and return nets the rails' named loads
  reach. Options for each undecided net: declare it a node, or add a held pin-role row to `intent_checks.py` (not this
  stream's file; the PCA9555, 74LVC1G17 and the switches have no row). Taken: nodes, as board D and E's SC-57 did. Reverse
  any node by a load on it that is another part's supply. (SC-59 on main 91894cd7.)
- **W4C-D3 (W4C-F1): R51 makes RAIL_SENSE a divider.** Options: a larger series resistor (still above IOVDD, only less
  current), a clamp (a part that still injects), moving the sense to an expander input (moves a function the firmware
  reads today), or the bottom leg. Taken: the bottom leg, one 0603 of a reel the board carries. (SC-60 on main 91894cd7.)
- **W4C-D4 (EPD_VCC's figures).** Typical 30 mA: the UC8253c's 20.2 mA operating maximum (UltraChip UC8253c A0.6 page
  59: IVDD 0.1, IVDDIO 0.1, IVDDA 20.0 mA at 3.0 V and 25 C, the only column the sheet gives; the driver PDi's flyer names for the E2370KS0C1) plus 10 mA INFERRED
  for the boost's inductor current, whose output power no held document states. Peak 0.521 A: 0.5 A into L1 (PDi Rev.02
  page 4 note (1), the boost switch's current class) plus the 20.2 mA. No maker's product specification for the panel is
  public (pervasivedisplays.com and docs.pervasivedisplays.com read 27 September 2026 give none). Reverse by the bench
  reading at bring-up.
- **W4C-D5 (the lamps' figures and the three rails' switches).** The 3 mm lamps have no part number, so no maker states a
  forward voltage: typical 8 mA per lamp (the design current the generator's LED table states), 6.4 mA for the two 470R
  lamps on LED_RAIL_SW; peak 5.25 V / R per lamp (every lamp lit with its forward drop at zero at +5V 5 percent high), the
  bound that needs no lamp sheet. LED_RAIL_SW is declared always on with the reason that no line enables it (the LIGHTING
  toggle switches it by hand); LED_RAIL is switched by Q1 through Q1_G; EPD_VCC by Q5 through EPD_PWR_n. The +5V rail's
  own SW_LIGHT load (0.35 A) lies between LED_RAIL_SW's typical (0.159 A) and peak (0.462 A) and is not moved.
- **W4C-D6 (EPD_RESE by the maker's reference).** The boost's sense node carries a chopped current; a DC v_max would
  make derate judge R43 (0.47 ohm 0603 1/10 W) against a number no sheet states. The panel maker states the parts on the
  node (Rev.02 BOM item 9 'RES 0.47 ohm 0603 1% 1/10W', the Si2300DS), so it is declared as the pump nodes are.
- **W4C-D7 (value strings).** R14 and R50 state '1%' in their value so the RF-002 walk reads 1 percent (it takes 5 percent
  where none is stated, `tx_inhibit.TOL_DEFAULT`); R51 keeps '10k' as R15 does (its tolerance moves no judgement; C25804
  is a 1 percent part either way).
- **W4C-D9 (W4C-F5, pass 2: +3V3 covers its child EPD_VCC).** The independent check found +3V3 declaring a 0.20 A peak
  while its child EPD_VCC declares 0.521 A. Options it named: (a) bound what Q5 draws from +3V3 with C28 and C29's
  arithmetic and declare EPD_VCC consistently; (b) raise +3V3's figures to cover the child and open an item for U5's
  headroom. Taken: (b). Why: (a) does not hold on the arithmetic. C28 (4.7 uF) behind Q5's at most 85 mOhm (AOS AO3401A,
  RDS(ON) at VGS -2.5 V; `v2/vendor/power/aos-ao3401a-p-mosfet.pdf`) is a 0.40 us time constant against an on-phase of
  about 1.6 us (10 uH to the 0.5 A class figure from 3.135 V), so by the end of each on-phase about three quarters of the
  inductor's current or more comes through Q5 (0.38 A of 0.5 A for a linear ramp at 85 mOhm, more at the part's typical
  resistance); no bound materially under 0.5 A follows without a larger local bulk, which is a circuit change. So +3V3
  declares 0.149 A typical and 0.72 A peak (its own loads' 0.119 and 0.199 A, the figures it declared before less Q5's
  former 1 mA, plus EPD_VCC's 0.030 and 0.521 A), and the copper from U5 and C2 to Q5 is judged at what it can carry.
  U5's own share is the open item the registry draft adds (W4C-F5, the next free S-nn: S-80 on main 62f26a44, S-77 on
  91894cd7): the TLV75533 is rated 500 mA (IOUT; ICL 560 mA minimum; TI SBVS320D 5.3 and 5.5); the 0.22 A by which the
  peak exceeds it, held for no longer than one on-phase, is at most 0.35 uC, 24 mV on C2, C28 and C29 (14.8 uF nominal)
  against the rail's 99 mV budget; the average U5 carries through a refresh rests on the boost's output power, which no
  held document states, so it is read at bring-up. The same reading decides +5V: its declared 1.0 A peak covers U5 only
  while U5 draws at most 0.508 A beside LED_RAIL_SW's 0.462 A and the sounder's 0.03 A (power_path reads +5V's children
  at 0.94 A, scaling a rail without an efficiency by its voltage ratio), and +5V's figure is what
  `pcb_energy_chain.yaml`'s B_PANEL_5V peak_a (1.0 A, under board B's F1 at 1.1 A hold) carries. +5V is not moved here:
  a 1.21 A peak would read F1 as opening in normal use on a microsecond figure the bench has not measured; the item
  names it. Reverse by (a) with a local bulk on EPD_VCC sized from the measured on-phase, or by the bring-up reading.
- **W4C-D8 (seats).** R50 and R51 sit in the schematic's buffers section; `gen_pcb_c3.py` packs any unseated part into
  its CLUSTER region, so no placement edit is owed before the next layout phase.

## 3. EQ-25 in numbers (the walk's convention: resistors at the adverse end of their stated tolerance, rails 5 percent)

| State | main 91894cd7 | candidate |
|---|---|---|
| board C unpowered, every ribbon in | 1.085 V FAIL | **0.243 V** PASS |
| board C unpowered, A-D mezzanine out | 1.103 V FAIL | **0.178 V** PASS |
| panel ribbon out (A, B, D) | 0.385 V | 0.385 V |
| A-B ribbon out (A, D) | 0.578 V | 0.578 V |
| released, board C powered, nominal / adverse | 2.54 V / 2.11 V | 2.57 V / 2.37 V |
| asserted, board C powered | the contact, about 0 V | the contact, about 16 uV (1.6 mA x 10 mOhm) |

Latency: asserting is the contact (C24 discharged at the first touch, settled within the 2 ms bounce of APEM's page 2),
U9's EMCON_HW follows in nanoseconds; release rises with 17 us (was 77 us) and crosses U9's VT+ after about 31 us (was
144 us); with board C's supply gone R50 and the three pull-downs hold the line with 78 us. Each is far inside REQ-071's
1 s. The toggle's current (1.59 mA) is inside the 5636ADKB's gold-plated contacts' range (AD: 10 uA at 5 V to 100 mA at
30 VDC) and under the walk's 4 mA pull limit. Readings: `readings/*/fail-safe-states-TX_INHIBIT_n.txt` (every state the
walk solves, by `parity/fs_levels.py`, which wraps `tx_inhibit._fs_bound` read-only).

## 4. Readings, before and after (scratch on the KiCad box; `retake_schematic_phase.py --verdict-dir`, boards C, A, B, D)

Main's re-take in the same scratch reproduced the tree's committed readings. Pass 2 (after the independent check,
27 September 2026, 15:35 to 15:40 UTC on the box) regenerated the candidate and re-took both sides again: the same
table, with power_path's +3V3 line the only new figure. Only these moved (`readings/retake-table-main-vs-candidate.txt`):

| Reading | main 91894cd7 | candidate |
|---|---|---|
| RF-002 inhibit_chain_a | FAIL (1 fail, 6 pass, 2 undecided) | INCONCLUSIVE (0, 7, 2) |
| RF-002 inhibit_chain_b | FAIL (11, 6, 3) | FAIL (10, 7, 3), board B's own |
| RF-002 inhibit_chain_c | FAIL (1, 5, 0) | **PASS of 6** |
| RF-002 inhibit_chain_d | FAIL (2, 6, 0) | INCONCLUSIVE (0, 7, 1): the SA868's own threshold |
| PWR-001 intent_rails C | FAIL of 7 (4 undeclared, 11 undecided) | **PASS of 6** (0 undecided; census 5 counted, 57 declared node, 3 settled, 74 unmarked) |
| power_path C (beside the set) | PASS (+5V 0.60 / 1.00 A feeds 0.08 / 0.13) | PASS, 0 short (+3V3 0.15 / 0.72 feeds 0.03 / 0.52; +5V 0.60 / 1.00 feeds 0.26 / 0.94; LED_RAIL_SW 0.16 / 0.46 feeds 0.14 / 0.44) |
| SCH-001 erc_gate C | PASS, 350 violations, 0 blocking | PASS, 352, 0 blocking (R50, R51 lib_symbol_issues warnings, the class every symbol carries) |
| SCH-005 pin_map_lands_c | PASS of 217 | PASS of 219 |

Unchanged: PWR-001 on A (PASS of 35), B (PASS of 59), D (INCONCLUSIVE, its own RLY_K); derate, edge_length,
clock_check, port_protect, interfaces, check_contracts (PASS of 99) on all four. Also on C (not in its schematic-phase
set, run beside): power_path PASS (2 rails to 5, 0 short), power_sequence PASS (2 to 5 rails, 0 unresolved), safe_lines
PASS of 6. The walk's report (`readings/*/walk-tx_inhibit-report.txt`) differs only in the TX_INHIBIT_n line (FAIL to
PASS) and board D's SA868 keying (FAIL to UNDECIDED, its maker states no SA_PTT_n threshold).

## 5. Parity (`parity/`, pass 2: `p2_run.sh`, `p2_pack.sh`)

- main 91894cd7 regenerated by main's chain (`handover_exports.py regen --letters c`, PHASE C24): schematic, netlist,
  intent and ERC PARITY_AFTER_NOISE, BOM PARITY, no land moved, PARITY (`regen-main.json`); stream w4c's independent
  comparator (`netcmp_w4c.py`, its own s-expression reader, every component's fields and every net's (ref, pin,
  pinfunction, pintype)) read MATCH against an empty change list in pass 1 (217 components, 153 nets, 584 pins).
- the candidate (main 91894cd7 plus `gen_sch_c.py` and `boards/c.json` at the shas below, regenerated by the same chain)
  against main's committed netlist: MATCH against `expected-c-netlist.json` (R50 and R51 added; R14's value and LCSC
  field; TX_INHIBIT_n gains R50.1, RAIL_SENSE R51.1, GND R50.2 and R51.2; no other pin moved or retyped; 219, 153, 588;
  `w4c-parity-cand.json`). Stream w3a's `netcmp.py` agrees (`w3a-netcmp-cand.json`).
- the pass-2 candidate against pass 1's: the schematic byte-identical (9dfeeff5d8d6bdec), the netlist MATCH against an
  empty change list (`w4c-parity-cand-vs-pass1.json`; the file differs only in its export date line), the intent only in
  +3V3's typical, peak and note (`intent-diff.json`, `candidate_vs_pass1_candidate`), the provenance in the generator's
  sha and the time.
- final files: gen_sch_c.py 6405a8db2b21c662, boards/c.json e350024a1cc6fcd3, pcb-c-display.kicad_sch 9dfeeff5d8d6bdec,
  out/pcb-c-display.net 3fddbb3edcd4248a, .net.prov.json ce7701402d0f5d76, -intent.json 270ebb4ccf1d0e8e (sha256/16);
  `sch_prov.py read` in the worktree: written by this tree's own generator (0ace9f5aaf1f36b2).

## 6. Findings

- **W4C-F1 (drawn):** RAIL_SENSE sat on 5 V through R15 alone, above the RP2040's IOVDD (datasheet 2.9.5 and 4.9 notes,
  Table 622). R51 makes the divider PANEL.md already names.
- **W4C-F2 (closed by D1):** with R14 10k the released level at the adverse ends (2.11 V) was under U9's interpolated
  2.15 V VT+: the transmitters could have stayed inhibited (the safe direction, a functional gap). 2.37 V now.
- **W4C-F3 (for the order owner):** C25804 (UNI-ROYAL 10k 1% 0603: R50, R51 and eight more board C resistors, R9 to R13, R15, R16 and R49) read stock 0
  at 2026-09-27T00:05Z (`v2/docs/parts/readings/lcsc-2026-09-27.json`). Nothing changed here.
- **W4C-F4 (for the vendor owner):** UltraChip publishes no UC8253c sheet; the copy filed here as a draft is UltraChip's
  own document (03-DTS-1891, UC8253c A0.6, 13 Oct 2020) as Elecrow serves it for its module DIE01237S.
- **W4C-F5 (the independent check, pass 2; drawn by D9, open for U5):** +3V3 declared a 0.20 A peak under its child
  EPD_VCC's 0.521 A. +3V3 now covers it (0.149 / 0.72 A) and the generator refuses a file where it does not; U5's
  headroom under the 0.5 A class figure, and with it +5V's 1.0 A peak, is the open item `apply_registry.py` adds, read at
  bring-up.
- **The independent check's document item (pass 2):** the drafted patches left R14 at 10k and the pull-downs without R50
  in PANEL.md section 6, EMCON.md section 2 and 4.1 and ARCHITECTURE.md 6.2. `patch_docs.py` now edits those too, names
  every changed place in its re-read notes, and finds the records bound to each edited document itself (refusing one it
  has no note for). No record binds ARCHITECTURE.md on 91894cd7 or on 62f26a44; the diagrams' MANIFEST.json reads it as an
  input of five arch-* diagrams whose Mermaid blocks the edit does not touch, and already records another sha of it on
  62f26a44 (the second release attempt edited section 8); the rebuild is the diagrams writer's. `diagrams/control-lines.md`
  (generated from the netlists at b7f96784) still lists R14 10k and no R50 until that writer re-renders it.

## Ids taken at the r8int6 integration (corrected at integration)

The registry script ran at the r8int6 integration of 27 September 2026 (set 6 of the handover), where other branches had taken the numbers this record names as drafted; the ids it took there, read back from the registry by each record's own text: EQ-25 (W4C-D1) is SC-67; PWR-001 on board C (W4C-D2) is SC-68; W4C-F1 (W4C-D3) is SC-69; W4C-F5 is S-83. Where this record names another number for one of them, the id here is the one the registry holds.
