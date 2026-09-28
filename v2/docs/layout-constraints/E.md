# Board E1 (dock strip): layout constraints

**Bound to the set 6 candidate (27 September 2026, read at `760d7f41`).** This sheet's inputs stand in the block below,
one to a line, each with its sha256/16 and the commit it last changed in, with the model and the stack the widths were
computed on; `v2/ecad/tools/constraints_bound.py` fails when a committed input, the calculation or this sheet's power
table moves without the others (README, "The bound block"). **Re-read on this candidate: section 2 alone.** Its power
table is `calc/rail_widths.py`'s output on the inputs below, and the widths, currents and barrel counts the text under
the table quotes were compared with the table and agree. **Not re-read on this candidate: sections 1 and 3 to 10**,
which are the readings at `e3aedb25` with the H2 line's changes marked where they stand (`ef144760`, the paragraph
below). Set 6 changed board E's netlist and intent file in `c4ad8350` (the hot stop line HOT-R1 drawn; the nodes FAN1_SW
and FAN2_SW declared). A node is not a rail: **no row of the power table moved**. A line of the older sections that
names a part, a net, a current or a count is compared with the netlist and the intent file below before it is followed,
and where this sheet and a record disagree the record governs (README). Board E is not at layout entry: no board is
(`v2/docs/CURRENT-EVIDENCE.md`, which holds the reasons current on this candidate; a count of reasons in a paragraph
below is its own binding's).

```bound
sheet      E
board      e
read       2026-09-27 at 760d7f41
current    section 2: the power table, and the figures the text under it quotes from it
older      sections 1 and 3 to 10: read at e3aedb25, with the H2 line's changes marked at ef144760
netlist    v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net sha256/16 56adc9746d61c4e0 changed c4ad8350
intent     v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock-intent.json sha256/16 dad1163afd720b5e changed c4ad8350
board_file v2/ecad/pcb-e1-dock-e7/pcb-e1-dock.kicad_pcb sha256/16 a462ac2620b9b8d3 changed bed211b6
model      track_current.width_for_current decision 35 rise 10 K plating 18 um
stack      JLC04161H-7628 outer 0.0350 mm inner 0.0152 mm
```

**As re-bound to the H2 line (after H2, 27 September 2026), kept as that binding's record.** Candidate re-read at `ef144760`: phase E17, netlist
`v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net` sha256/16 `d6137f50059e5cbc` (round 8 at `bc0f562f`, set 5 at `b7f96784`),
intent `pcb-e1-dock-intent.json` `5913e38b20333d35`; the committed board file `a462ac2620b9b8d3` is E17. Section 2's
table is regenerated from `calc/rail_widths.py` on that intent: VIN_RAW at 14.10 A and TRK_OUT at 10.33 A are now the
committed figures, not a round 8 note, and SGP_VDD is declared (marked **H2**). Board E is not at layout entry: **5
reasons at H2** (`CURRENT-EVIDENCE.md`): PWR-001 INCONCLUSIVE (FAN1_SW and FAN2_SW, S-76), SI-001 INCONCLUSIVE,
decision 31's protection review, FEA-006, FEA-007. Known changes of the H2 line: **section 6.1 item 1's defect is
corrected in the generator** (set 5, `b7f96784`: the tracker senses its current on its bottom leg, HC9-E1, S-47's
core; the item stays below as the reading that found it), and VIN_RAW crosses the dock on four 9 A power pins with
board A's half (SC-55, `b7f96784`). Every other line below is the reading at `e3aedb25`, not re-read against the H2 netlist; where it and a record disagree, the record governs (README).

As first written: a view over the records at `main` `e3aedb25` (conventions and shared rules: [README.md](README.md)),
candidate then netlist `d910e49c5f5f50b2`, intent `9ae33eb17d04670e`, 15 blocker lines. **Round 8** (`fnd/r8int1`, which reached `main` as `53a98a71` after this sheet was first
written; board E's part is `bc0f562f`, netlist sha256/16 `f3c1ad6153002976`) raises two of board E's declared
currents: **VIN_RAW from 6.15 A to 14.1 A and TRK_OUT from 6.16 A to 10.33 A** (its intent file compared rail by rail
for this sheet); section 2 gives both, and sections 5 and 6.1 cite `gen_sch_e.py` by its line numbers at `53a98a71`.
Re-read this sheet on that netlist before a layout starts.

**The tracker's maker constraints are read from the maker's own sheet, which is in the tree:**
`v2/vendor/power/lt8705a.pdf`, the LT8705A datasheet revision 8705af, 44 pages, sha256/16 `8f552a0b57677bfa`, filed in
`ada94128` (`v2/docs/respin-research-power-2026-09-04.md` line 24) and unchanged at `e3aedb25` and `53a98a71`; its
"Circuit Board Layout Checklist" is on pages 35 and 36. Reading it against board E's netlist found **a circuit defect
that blocks board E's layout entry** (section 6.1 item 1: the current-sense resistor R5 sits in series with the
inductor, where the controller's CSP and CSN pins would sit at up to about 15 V against a 3 V absolute maximum) and
three smaller circuit items (section 5: GATEVCC has no capacitor of its own and none of the controller's supply pins
carries a declared bypass; section 6.1 item 9, MODE; section 6.1 item 10, the boost diodes). Board A's LM5176 stages
were checked for the same pattern and do not carry it (section 6.1 item 1). **`v2/ecad/tools/pcb_emc.yaml` board e is
stale on this point:** U5's `basis` still reads "the part's datasheet is not in this tree"; the corrected text is
handed to the EMC sheet's writer with this layer's drafts.

## 1. Stackup and layer use: DECIDED, four layers

- **JLC04161H-7628, 1.6 mm, 1 oz outer (0.035 mm), 0.0152 mm inner** (`v2/docs/STACKUP-DECISIONS.md` section 3.5): In1
  as the solid ground and routing on a 267 x 68 mm strip whose open nets were end-to-end. The power half of the old
  argument is refuted by measurement.
- **Layer use:** F sig and pours, **In1 GND**, In2 power pours (CELL_F, PV_P, TRK_OUT, VIN_RAW) and a GND fill
  (decision 27's E treatment), B sig and pours. No routed track on either inner layer on E17.
- **Single-sided SMD assembly** (E17 carries nothing on its back); decision 42 allows no far-side seat on E.
- **The tracker's plane, from its maker** (`v2/vendor/power/lt8705a.pdf` p.35, Circuit Board Layout Checklist): "a
  dedicated ground plane layer ... should not have any traces and should be as close as possible to the layer with the
  power MOSFETs". In1 is that layer: GND, no router track on E17, 0.2104 mm below F.Cu where Q3 to Q6 sit
  (`stackup_write.STACKS` JLC04161H-7628; single-sided assembly). Met by the stackup as decided.
- **No GND or VIN copper under the switch nodes, from its maker** (p.35: "Minimize parasitic SW pin capacitance by
  removing GND and VIN copper from underneath the SW1 and SW2 regions"; p.36: "Except under the SW pin regions, flood all
  unused areas on all layers with copper ... Connect the copper areas to a DC net (e.g., quiet GND)"). On board E the
  tracker's VIN is PV_P, which In2 pours. **Constraint:** In2's PV_P pour, In2's GND fill and any B.Cu pour are cut
  back from under the TRK_SW1 copper (Q3 source, Q4 drain, L1 pin 1) and the TRK_SW2 copper (Q5 drain, Q6 source, and
  the inductor's SW2 end once section 6.1 item 1 is fixed), and every other unused area is flooded to GND.
  **In1 stays solid under them: a session choice** (the owner's standing rule of 26 September 2026). Reason: In1 as a
  solid ground on every board is the owner's ruling of 5 September 2026 (`MESHSAT-709-geometry-appendix.md` 32.40
  item 3, decision 3 of 17:08, applied to every board at its next regeneration), which this sheet cannot overwrite, and
  the maker's first clause asks for exactly that plane next to the FETs. Residual, stated: the switch-node copper
  couples to In1 at about 18.5 pF per 100 mm2 (INFERRED: parallel plate over 0.2104 mm at Dk 4.4,
  `stackup_write.STACKS`); comparing it with the FETs' own output capacitance needs the Infineon BSC028N06NS and
  BSC039N06NS sheets, which are not filed in `v2/vendor/` (`v2/vendor/PARTS.md` cites `power/lt8705a.pdf` for them
  without a page; p.41 is the only page naming those parts, so the page is INFERRED). Reversal: a switch-node ringing or loss measurement on the prototype (`PCB-BRING-UP.md` board E; section
  10), or board E's stream showing a plane void under the switch node that the owner's ruling admits, moves In1 to a
  void there.
- Conformally coated.
- **Board E's outer copper is 1 oz.** `pcb_energy_chain.yaml` stage DOCK_ENTRY says "board E's 2 oz power bands", and
  no ruling puts E at 2 oz (ruling 7 covers P and E5): a contradiction for the energy-chain writer
  (`STACKUP-DECISIONS.md` section 6 item 5).

## 2. Power: band widths at the declared currents

From `calc/rail_widths.py` (decision 35, 10 K; 1 oz outer, 0.0152 mm inner).

The table is `calc/rail_widths.py`'s output on the inputs this sheet's `bound` block names, row for row in the tool's
own order and cell for cell, and `v2/ecad/tools/constraints_bound.py` fails when the two differ; the `note` column is
this sheet's and is not compared (README, "The bound block"). A width printed 0.00 is under 0.005 mm, a current of a few
milliamperes: the fabricator's floor governs there, not the current.

| rail | V (working) | typ / peak A | governing A | outer mm | two outer faces, each mm | inner mm | barrels at the larger of peak and governing, 0.3 / 0.4 / 0.5 mm drill | note |
|---|---|---|---|---:|---:|---:|---|---|
| CELL_F | 14.4 (16.8) | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s | 23.91 | 6.72 | 195.80 (over 40 mm) | 25 / 21 / 18 | the pack path, F3 to the dock block; the inner width is not a conductor (item 1) |
| CELL+ | 14.4 (16.8) | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s | 23.91 | 6.72 | 195.80 (over 40 mm) | 25 / 21 / 18 | the pack path, J_BATT to F3 |
| VIN_RAW | 12.0 (36.0) | 14.10 / 14.10 | 14.10, typical (PI-001) | 15.29 | 4.43 | 125.22 (over 40 mm) | 20 / 16 / 14 | **H2**: 14.10 A since `bc0f562f` (round 8); at `e3aedb25` it was 6.15 A, which is 3.67 mm on one outer face and 9 / 7 / 6 barrels. The intent file: "Declared at 14.10 A typical and peak (R4A-N12, 26 September 2026): board A's front end at its ISNS limit (5.7 A at 20.7 V, 0.93) drawing from a 9.0 V bus"; "the 12 AWG pad to the dock's four VIN_RAW power pins (EQ-16, 27 September 2026; until then J_BLK pins 1 to 4)" |
| +3V3_E6 | 3.30 | 0.35 / 0.60 | 0.35, typical (PI-001) | 0.07 | 0.03 | 0.42 | 1 / 1 / 1 |  |
| +5V_E6 | 5.00 | 0.30 / 0.50 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1 |  |
| +5V_GEIGER | 5.00 | 0.10 / 0.10 | 0.10, typical (PI-001) | 0.01 | 0.00 | 0.08 | 1 / 1 / 1 |  |
| DC_IN | 12.0 (36.0) | 6.15 / 6.15 | 6.15, typical (PI-001) | 3.67 | 1.41 | 27.42 | 9 / 7 / 6 | the shore and vehicle inlet |
| DC_F | 12.0 (36.0) | 6.15 / 6.15 | 6.15, typical (PI-001) | 3.67 | 1.41 | 27.42 | 9 / 7 / 6 | the shore and vehicle inlet |
| DC_P | 12.0 (36.0) | 6.15 / 6.15 | 6.15, typical (PI-001) | 3.67 | 1.41 | 27.42 | 9 / 7 / 6 | the shore and vehicle inlet |
| HS_S | 12.0 (36.0) | 6.15 / 6.15 | 6.15, typical (PI-001) | 3.67 | 1.41 | 27.42 | 9 / 7 / 6 | the shore and vehicle inlet |
| DC_HS | 12.0 (36.0) | 6.15 / 6.15 | 6.15, typical (PI-001) | 3.67 | 1.41 | 27.42 | 9 / 7 / 6 | the shore and vehicle inlet |
| PV_P | 17.6 (25.0) | 5.68 / 6.25 | 5.68, typical (PI-001) | 3.29 | 1.27 | 23.70 | 9 / 7 / 6 | the solar input |
| PV_IN | 17.6 (25.0) | 5.68 / 6.25 | 5.68, typical (PI-001) | 3.29 | 1.27 | 23.70 | 9 / 7 / 6 | the solar input |
| TRK_OUT | 15.10 | 10.33 / 10.33 | 10.33, typical (PI-001) | 8.65 | 2.89 | 70.84 (over 40 mm) | 14 / 12 / 10 | **H2**: 10.33 A since `bc0f562f` (round 8); at `e3aedb25` it was 6.16 A, which is 3.68 mm on one outer face and 9 / 7 / 6 barrels. The intent file: "Declared at 10.33 A typical and peak (R4A-N12, 26 September 2026): the panel's 93 W at the 9 V bus floor, when a vehicle holds the bus under 15.1 V; 6.16 A is the figure at 15.1 V" |
| SGP_VDD | 3.30 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **H2**, new in `b7f96784`: "the SGP41's VDD behind its RC element"; 4.6 mA, which prints as 0.00 |

What the table asks of the layout:

1. **The pack path (CELL+, CELL_F) at 18 A needs 23.91 mm on one 1 oz face**, or both outer faces at 6.72 mm each only
   if dc_drop reads an equal share. **On E7 B.Cu carried 97 percent of CELL_F's current once In2 was emptied and In2 43
   percent with it** (`LAYER-DECISIONS-2026-09-11.md`, the E experiment), so the share is not equal by default: the
   generator lays the pack path as bands on both faces tied at both ends, and the finish reads the per-layer share. The
   In2 CELL_F pour counts only for what dc_drop solves on it.
2. **The inlet chain at 6.15 A** (3.67 mm at 1 oz) and, after round 8, **VIN_RAW at 14.1 A** (15.29 mm on one face)
   and TRK_OUT at 10.33 A (8.65 mm). VIN_RAW's In2 pour carried 20 percent on E7; the rest is outer copper.
3. **Rail current in generator-laid pours and bands, never router tracks** (`power_copper.py`); every layer transition
   carries the barrel count of the table.

## 3. Pairs

**USB_* (the RP2040 sensor controller's USB 1.1 port, 12 Mb/s):** no impedance target (`pcb_interfaces.yaml`
USB_FULL_SPEED; `boards/e.json` pair_classes null); edge 4 ns (`boards/e.json` signal classes). Route coupled over the
In1 plane. No RF line on board E (`rf_line.verdict.json` PASS with nothing judged).

## 4. Return paths and the ground partition

- `return_reach_mm: 3.0` (decision 32).
- **Two grounds, one crossing** (`boards/e.json` grounds; GND-001): GND_V is the vehicle-side return from the inlet
  through the fuse, the ideal diode and the hot-swap to the input filter; it meets GND only through the second winding
  of L2, the SRF1260 common-mode choke. It is not an isolation barrier. **DCIN_PGD and SHORE_INHIBIT are the only
  signals referenced across the partition, and both cross at the choke.** No other conductor crosses between GND_V and
  GND.
- **The tracker's power ground and signal ground** (`v2/vendor/power/lt8705a.pdf` p.36): "Partition the power ground
  from the signal ground. The small-signal component grounds should not return to the IC GND through the power ground
  path." On board E the power ground is the return of Q4, Q5 (through R5 once section 6.1 item 1 is fixed), C11 to C15
  and C24 to C27; the small-signal grounds are R9, R11, R12, R15, R16, R17, C20, C21, C22 and C23, which return to U5's
  GND pins (13 and the exposed pad 39; pins 11 SYNC and 37 MODE are tied to GND on the netlist) without sharing the
  power return's copper. "The output capacitor (-) terminals should be connected as closely as possible to the (-)
  terminals of the input capacitor" (p.36): C24 to C27 to C11 to C15. "Use immediate vias to connect the components
  (including the LT8705A's GND pins) to the ground plane. Use several vias for each power component" (p.35); the
  exposed pad "MUST BE SOLDERED TO PCB" (p.2) and GND is tied "directly to local ground plane" (p.12).

## 5. Decoupling (decision 42)

- **Generator items** (`DECOUPLING.md` section 8.3), owed at `e3aedb25`: G11 (U12, the AP63205: C31 at pin 3 VIN, not
  pin 2 EN; the generator's own comment reads "2 EN 3 VIN"), G13 (the RP2040's DVDD: 1 uF at VREG_VOUT class L, 100 nF
  at each DVDD pin class D, one 100 nF added; the VREG_IN 1 uF stays), G14 (classes on every entry). **Round 8 closes
  all three in the generator** (`bc0f562f`: C31 at U12 pin 3; C45 at VREG_VOUT, C46 and a new C59 at the DVDD pins; a
  class and the maker's clause on every entry, which the generator refuses to omit); DEC-001 reads the seats on the next
  placement.
- **Class R** at U12 (AP63205) and at the LT8705A tracker U5's power stage (Q3 to Q6, L1, R5, the input capacitors C11
  to C15, the output capacitors C24 to C27, the boost capacitors C17 and C18; decision 42's R2 frees them from the
  escape fan when they are placed against U5).
- **The tracker controller's supply pins carry no declared bypass, and GATEVCC has no capacitor of its own** (circuit item
  for board E's stream). The intent's bypass list names one U5 entry, C16 at pin 3, which is the sense filter (class
  A); read on the intent files at `e3aedb25` and `53a98a71`. The maker asks for four:
  - VIN, pin 34: "It must be locally bypassed to ground" (`v2/vendor/power/lt8705a.pdf` p.12); the front-page circuit
    fits 1 uF there (p.1).
  - INTVCC, pin 35: "Bypass this pin to ground with a minimum 4.7μF ceramic capacitor" (p.12). C19, 4.7 uF, is on
    TRK_INTVCC (`gen_sch_e.py` line 503) and declared against no pin.
  - GATEVCC, pin 15: "Must be connected to the INTVCC pin ... Locally bypass to GND" (p.11), and "The bypass capacitance
    from GATEVCC to GND should be at least ten times the CB1 or CB2 capacitance" (p.28), which with C17 and C18 at
    470 nF is 4.7 uF. The front-page circuit (p.1) and the 12 V 15 A converter (p.41) each fit 4.7 uF at INTVCC and a
    second 4.7 uF at GATEVCC. **Board E has none for pin 15:** it shares TRK_INTVCC with pin 35, which sits on the
    opposite edge of the package (Pin Configuration, p.2), so C19 cannot be close to both, and the checklist asks
    "Connect the INTVCC and GATEVCC bypass capacitors close to the IC. The capacitors carry the MOSFET drivers' current
    peaks" (p.36).
  - LDO33, pin 4: "Bypass this pin to ground with a minimum 0.1μF ceramic capacitor" (p.11). C20, 1 uF, is on
    TRK_LDO33 and declared against no pin.

  **Owed to board E's stream before the next placement:** a second 4.7 uF at GATEVCC, and C19, C20, the new capacitor
  and a VIN capacitor declared against pins 35, 4, 15 and 34, so DEC-001 measures their seats. RECOMMENDED classes, by
  decision 42's own reading of the LM5176, the same kind of controller (`DECOUPLING.md` section 6, R4: "The LM5176's
  VIN (pin 2) and BIAS (pin 24) take their own small capacitors under class D, and VCC (pin 23) under class L"): VIN
  and GATEVCC class D; INTVCC and LDO33 class L, value floors 4.7 uF and 0.1 uF (p.12, p.11). `DECOUPLING.md`'s maker
  table (section 4) has no LT8705A row: a gap for its writer.
- No far-side seat on E (decision 42, D5: E17 carries nothing on its back).

## 6. Placement

### 6.1 The tracker's block (U5, LT8705A), from its maker's checklist

Source: `v2/vendor/power/lt8705a.pdf`, "Circuit Board Layout Checklist" (pp.35 and 36) with Figure 14 (p.35), the pin
functions (pp.11 and 12), the block diagram (Figure 1, p.13), and two of the maker's own circuits: the front-page
telecom stabiliser (p.1, the same RT of 215k and 202 kHz as board E) and the 12 V 15 A converter (p.41, whose M1 and M2
are board E's Q3 and Q4 parts). The maker's names on board E (`gen_sch_e.py` lines 427 to 560 at `53a98a71`): M1 Q3,
M2 Q4, M3 Q5, M4 Q6, L L1, RSENSE R5, CB1 C17, CB2 C18, DB1 D5, DB2 D6, CIN C11 to C15, COUT C24 to C27; board E fits
no D1 or D2 (optional in Figure 1). The block's switching nodes TRK_SW1 and TRK_SW2 and its gate drives TRK_TG1,
TRK_TG2, TRK_BG1 and TRK_BG2 are the board's strict nets (`boards/e.json` signal classes).

1. **Circuit defect, blocking board E's layout entry: R5 is in the inductor's leg, not the bottom switches' leg.** The
   netlist puts R5 between L1 pin 2 (TRK_LSENSE) and TRK_SW2 (`gen_sch_e.py` line 481 at `53a98a71`, line 433 at
   `e3aedb25`), takes R6 from TRK_LSENSE to TRK_CSP and R7 from TRK_SW2 to TRK_CSN (line 492), and ties the sources of
   Q4 and Q5 (pins 1 to 3) straight to GND (lines 477 and 478). CSP and CSN are rated "-0.3V to 3V" (Absolute Maximum
   Ratings, p.2). TRK_SW2 sits at the output in the buck region, where M4 stays on, and switches between ground and the
   output in the boost region; its intent node is declared at 15.1 V (`gen_sch_e.py` line 549). So both pins would
   sit at up to about 15 V, five times their rating, in every region of operation. The maker puts RSENSE between the
   joined sources of M2 and M3 and GND, CSP on the source side and CSN on the ground side, in the block diagram
   (Figure 1, p.13), both switch layouts (Figure 14a and 14b, p.35) and both circuits (p.1, p.41); the checklist says
   "Minimize inductance from the sources of M2 and M3 to RSENSE by making the trace short and wide" (p.36). **Fix, owed
   to board E's stream in `gen_sch_e.py` before E's next placement:** Q4 and Q5 pins 1 to 3 on a new sense node; R5
   from that node to GND; R6 from R5's node-side pad to TRK_CSP and R7 from R5's GND pad to TRK_CSN (Kelvin, p.36); L1
   pin 2 straight to TRK_SW2. The net TRK_LSENSE goes away, and with it its entries in `pcb_sensitive.yaml` board e
   (`switch_nets` and the two Kelvin rows naming R5.1 on TRK_LSENSE and R5.2 on TRK_SW2, lines 275 to 305 at
   `53a98a71`), `gen_pcb_e3.py` PATTERNS (line 483) and `boards/e.json` (the pattern at line 254 and the pinned-net
   list at line 430). The current figures that use R5 stand (the 69 mV minimum buck valley over 5 mOhm, 13.8 A,
   `gen_sch_e.py` line 103): the maker's sizing assumes this placement. Board A's seven LM5176 stages were checked for
   the same pattern and do not carry it: each stage's low-side FET sources are on its CS node and the shunt runs from
   CS to GND (`gen_sch_a.py` lines 431, 432 and 446 at `53a98a71`).
2. **The two hot loops compact** (p.35, with Figure 14): "The high di/dt path formed by switch M1, switch M2, D1,
   RSENSE and the CIN capacitor should be compact with short leads and PC trace lengths. The high di/dt path formed by
   switch M3, switch M4, D2 and the COUT capacitor also should be compact". On board E: Q3, Q4, R5 (after item 1) and
   the input ceramics C13 to C15 in one tight loop; Q5, Q6 and the output ceramics C26 and C27 in the other; the
   polymer bulk (C11 and C12 on PV_P, C24 and C25 on TRK_OUT) beside them. "Connect the input capacitors, CIN, and
   output capacitors, COUT, closely to the power MOSFETs" (p.36).
3. **Q4 and Q5 at U5** (p.36): "Place switch M2 and switch M3 as close to the controller as possible, keeping the GND,
   BG and SW traces short", with the Q4 and Q5 sources to R5 "short and wide". The block's support parts sat 11 to
   27 mm from U5 on E38 (`boards/e.json`
   `_the_trackers_block_is_spread_and_it_is_one_cause_behind_both_of_board_e_s_open_items`), one cause behind two of
   E's open items: seat them at U5.
4. **Boost capacitors at their pins** (p.36): C17 at BOOST1 (pin 23) and SW1 (pin 21); C18 at BOOST2 (pin 17) and SW2
   (pin 19).
5. **Driver supply capacitors at the IC** (p.36, quoted in section 5): the INTVCC capacitor at pin 35 and the GATEVCC
   capacitor at pin 15, each at its own pin; board E owes the second one (section 5). LDO33's C20 at pin 4.
6. **Current sense** (p.36): "Route current sense traces (CSP/CSN, CSPIN/CSNIN, CSPOUT/CSNOUT) together with minimum
   PC trace spacing. Avoid having sense lines pass through noisy areas, such as switch nodes. The optional filter
   network capacitor between CSP and CSN should be as close as possible to the IC. Ensure accurate current sensing with
   Kelvin connections at the RSENSE resistors"; and of the filter, "The network should be placed as close as possible
   to the IC" (p.34, Figure 13a: 10 ohm per leg and 1 nF across, which round 8 fitted as R6, R7 and C16, `bc0f562f`).
   So C16 at pins 2 and 3, R6 and R7 with it, and the Kelvin pair from R5's two pads to the network routed together.
   ANA-001's keep stands: TRK_CSP and TRK_CSN at least 0.5 mm from TRK_SW1, TRK_SW2, E6_SW, FAN1_SW, FAN2_SW (and
   TRK_LSENSE while it exists), WATER_SENSE at least 1.0 mm (`pcb_sensitive.yaml` board e). On E37 the tightest
   approaches to the sense pair were gate drives (TRK_CSN 0.204 mm from TRK_TG2), which decision 45 reports rather than
   judges; E39's reading has no close approach left on the declared list (`boards/e.json`
   `_e39_is_read_and_board_e_has_no_close_approach_left_on_its_declared_list`). **A conflict, for board E's stream:**
   `gen_sch_e.py` lines 493 to 500 (at `53a98a71`) say "the next E placement pass seats R6 and R7 against R5"; the
   maker's p.34 clause places the network at the IC. **This sheet states the maker's placement, a session choice**
   (the owner's standing rule of 26 September 2026). Reason: it is the maker's own clause for its own part, and after
   item 1 the shunt sits at Q4 and Q5, which item 3 puts at U5, so the Kelvin run is short either way. Reversal: board
   E's stream showing on a placed board that resistors at the shunt give the pair less run beside the switching nodes
   than resistors at the IC.
7. **Fast nodes away from small signals** (pp.35 and 36): "Keep the high dV/dT nodes SW1, SW2, BOOST1, BOOST2, TG1 and
   TG2 away from sensitive small-signal nodes", and "Avoid running signal traces parallel to the traces that carry high
   di/dt current because they can receive inductively coupled voltage noise. This includes the SW1, SW2, TG1 and TG2
   traces to the controller." The block's small-signal nodes on board E: TRK_FBIN, TRK_FBOUT, TRK_VC, TRK_VCC1,
   TRK_SS, TRK_RT, TRK_IMONI, TRK_IMONO, TRK_SHDN, TRK_CSP and TRK_CSN.
8. **Feedback and compensation** (p.36): "Connect the FBOUT and FBIN pin resistor dividers to the (+) terminals of COUT
   and CIN respectively ... The resistor connections should not be along the high current or noise paths": R10 and R11
   tap TRK_OUT at C24 to C27, R8 and R9 tap PV_P at C11 to C15. "Connect the VC pin compensation network closely to
   the IC, between VC and the signal ground pins": R13, C21 and C22 at pin 8, returning to the signal ground of
   section 4.
9. **Circuit item, smaller: MODE is tied to GND** (pin 37, `gen_sch_e.py` line 475), which selects forced continuous
   mode ("less than 0.4V", p.12). Board E runs the input regulation loop (FBIN at the panel's 17.6 V point, R8 and R9),
   and the maker warns: "Note that using this function in forced continuous mode (MODE pin low) can result in current
   being drawn from the output and forced into the input. If this behavior is not desired then use discontinuous or
   Burst Mode operation" (p.29; "Reverse Current Limit", p.24). On board E the input is the panel. RECOMMENDED to board
   E's stream, not taken here because it is a circuit change: MODE to TRK_LDO33, discontinuous mode ("tie MODE to a
   voltage above 2.3V (i.e., LDO33)", p.18), in which "synchronous switch M4 is held off whenever reverse current in
   the inductor is detected" (p.18); a tie rather than Burst Mode's floating pin.
10. **Circuit item, smaller: the boost diodes are Schottky.** D5 and D6 are BAT54 (`gen_sch_e.py` line 502). The maker:
    Schottky diodes "can exhibit high reverse current leakage and have the potential for thermal runaway under high
    voltage and temperature conditions. Silicon diodes are thus recommended for diodes DB1 and DB2. Make sure that DB1
    and DB2 have reverse breakdown voltage ratings higher than VIN(MAX) and VOUT(MAX) and have less than 1mA of reverse
    leakage current at the maximum operating junction temperature" (p.29). No BAT54 sheet is filed in `v2/vendor/`, so
    its leakage at board E's hottest point is not read here. Owed to board E's stream: a silicon part, or the BAT54's
    own sheet read against the p.29 criteria. The maker also allows up to 5 ohm in series with DB1 and DB2 (one
    resistor from GATEVCC to their common anodes, as on p.1) where SW pin ringing needs it, judged by measurement at the
    SW pins (p.29): a prototype item (section 10).

The checklist's plane, copper-flood and switch-node clauses are in section 1; its ground-partition, capacitor-return
and via clauses in section 4.

### 6.2 The rest of the board

1. **Inlet order** follows the current (E35's input side in the order the current flows, `boards/e.json`): J_DCIN, F1,
   DC_F, Q1 (the ideal diode), DC_P, the hot-swap (LM5069, Q7), DC_HS, L2, VIN_RAW. Board E's typed barrel sites are
   derived from the placed pads, never literals (`boards/e.json` `_e36_four_typed_barrel_sites_were_in_empty_board...`).
2. **Case:** a 267 x 68 mm strip on the case floor; its VHB pads lift the whole stack (`ASSEMBLY.md` line 56, the dock strip's VHB
   pads; `CASE-MARGINS.md` finding 4 cites line 47, which is the RockBLOCK bracket row); the dock block E5 carries the pack path to board A; its outline and connector positions
   are frozen for routing after `CASE-MARGINS.md` finding 28's targeted checks, or with the OPEN rows named.
3. **Test access:** 13 test points; TP10 SWCLK, TP11 SWDIO, JP1 BOOTSEL on the committed netlist. Bring-up:
   `PCB-BRING-UP.md` board E (DC_IN at 12 V, 6.15 A; CELL+ at 14.4 V, 10 A; PV_IN at 17.6 V, 5.68 A; derived rails
   measured in order).

## 7. Protection placement (decision 31, TRN-001)

| Port (`boards/e.json` external_ports) | Conductor | Part (committed netlist) | Constraint |
|---|---|---|---|
| J_DCIN (shore and vehicle DC from the 38999 wall receptacle) | DC_IN, fused to DC_F | **D10 SMCJ40CA between F1 and Q1 on DC_F** (`pcb_board_holds.yaml` board e; the session's substitution for the ruled SMCJ40A, because DC_F is ahead of the reverse-polarity FET); D1 SMCJ40A behind Q1 | D10 at the entry after the fuse, so a sustained overvoltage opens F1 rather than the clamp; ground return short and on GND_V |
| J_POD pins 1, 3, 4 (the outside sensor pod over an M8 receptacle) | +3V3_E6, SDA1, SCL1 | D9 USBLC6-2SC6 | at the connector, return short and on the plane |
| J_SOLAR (a long outdoor lead) | PV_IN, fused by F2 to PV_P | D4 SMCJ28A on PV_P after F2 | at the entry after the fuse |

The decision 31 hold gates fabrication release; the review record is owed at layout entry (`CURRENT-EVIDENCE.md`
line 135).

## 8. Spacing (ISO-001)

- **DC_IN, DC_F, DC_P, HS_S, DC_HS and VIN_RAW (36 V working):** at least 0.160 mm outer coated, 0.150 mm inner,
  **0.500 mm where the coating is masked** (J_DCIN, J_BLK and the test points). E17 reads FAIL: 92 pairs under the
  limit on 8 high-voltage nets, the closest 0.129 mm (DC_HS to GND_V, DC_P to U3_VCAP, VIN_RAW to GND, SCL0,
  WATER_SENSE and TRK_OUT; `pcb-e1-dock-e7/routed/spacing.verdict.json`). Every class in E's project file carries a
  0.127 mm clearance except BANK (0.3 mm): these nets need a class at 0.16 mm or more.
- **PV_IN, PV_P (25 V working):** 0.120 mm outer coated, 0.104 inner, 0.300 where masked.

## 9. Thermal

- Named heat on board E: the tracker's FETs and inductor at up to 10.33 A (round 8), the ideal diode Q1 and the
  hot-swap FET Q7 at 6.15 A, the pack-path blade F3. THM-001 reads no verification. The always-on drain is 0.2 to 1.7 W,
  TBD (audit per-board record).
- The tracker's maker on heat: "for high current, a multilayer board provides heat sinking for power components" (p.35)
  and "Flooding with copper will reduce the temperature rise of power components" (p.36); both are in section 1's flood
  rule. The controller's exposed pad (pin 39) is its heat path to the plane (p.2, p.12; section 4).
- The BME688 on board E is the inside-air sensor that control C1 reads (`POWER-THERMAL.md` 9.3); place it in the case
  air, away from the tracker's heat, or C1 reads the board and not the air (INFERRED from C1's definition).

## 10. Analyses that need placed or routed geometry, or hardware

| Stage | What | Needs |
|---|---|---|
| SCHEMATIC (before the next placement) | the tracker's sense resistor in the bottom leg (section 6.1 item 1, blocking); GATEVCC's capacitor and the four supply-pin declarations (section 5); MODE and the boost diodes (section 6.1 items 9 and 10) | board E's stream, in `gen_sch_e.py`, regenerated with parity |
| PLACED_BOARD | SCH-002, DEC-001 (G11, G13, G14 and the tracker's supply pins), GND-002, IMP-002, ANA-001, THM-001, PLC-001, MEC-001 | the next E placement on the round 8 netlist |
| ROUTED_BOARD | PI-001 (the pack path at 18 A and its per-layer share; VIN_RAW at 14.1 A), PI-002, PI-003, GND-001 (the choke crossing), ISO-001 (section 8), RET-001 to RET-004, PAIR-001, RF-001, STK-001, EMC-001, RTE, VIA, PLN | the routed candidate |
| FABRICATION_RELEASE | decision 31 hold; FEA-006 | the routed candidate |
| PROTOTYPE | `TEST-PLAN.md` M1 (CE102 on the vehicle input), M3, M7 (ESD at J_POD, J_DCIN, J_SOLAR); the Geiger channel's count rate with the tracker switching (`pcb_emc.yaml` board e, pre_compliance); the tracker's SW pin ringing measured directly at the SW pins, which decides the optional DB1/DB2 series resistor (`lt8705a.pdf` p.29) and In1's void of section 1; `PCB-BRING-UP.md` board E | a built kit |
