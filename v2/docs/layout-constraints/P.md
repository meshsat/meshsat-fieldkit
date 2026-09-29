# Board P (pack BMS): layout constraints

**Bound to the set 6 candidate (27 September 2026, read at `760d7f41`).** This sheet's inputs stand in the block below,
one to a line, each with its sha256/16 and the commit it last changed in, with the model and the stack the widths were
computed on; `v2/ecad/tools/constraints_bound.py` fails when a committed input, the calculation or this sheet's power
table moves without the others (README, "The bound block"). **Re-read on this candidate: section 2 alone.** Its power
table is `calc/rail_widths.py`'s output on the inputs below, and the widths, currents and barrel counts the text under
the table quotes were compared with the table and agree. **Not re-read on this candidate: sections 1 and 3 to 10**,
which are the readings at `e3aedb25` with the H2 line's changes marked where they stand (`ef144760`, the paragraph
below). Set 6 changed board P's netlist and intent file in `932cf9d7` (the supplies PWR-001 refused are declared, with
the nodes PBI, CELL1 to CELL3, FUSE_G and FUSE_GQ): **BAT_F, VCC_F, SEC_VDD, SW and SCP_HTR are new rows**, each marked
**SET 6** in the table, and SW is judged at the pack path's 18 A. A line of the older sections that names a part, a net,
a current or a count is compared with the netlist and the intent file below before it is followed, and where this sheet
and a record disagree the record governs (README). Board P is not at layout entry: no board is
(`v2/docs/CURRENT-EVIDENCE.md`, which holds the reasons current on this candidate; a count of reasons in a paragraph
below is its own binding's).

```bound
sheet      P
board      p
read       2026-09-29 at d41f85ec
current    section 2: the power table, and the figures the text under it quotes from it
older      sections 1 and 3 to 10: read at e3aedb25, with the H2 line's changes marked at ef144760
netlist    v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net sha256/16 20c7b0795593d761 changed d41f85ec
intent     v2/ecad/pcb-p-pack-p2/out/pcb-p-pack-intent.json sha256/16 657f4c42db51e4da changed d41f85ec
board_file v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_pcb sha256/16 d79865e7b1aceb95 changed 6d1b5a15
model      track_current.width_for_current decision 35 rise 10 K plating 18 um
stack      JLC04162H-7628 outer 0.0700 mm inner 0.0152 mm
```

**As re-bound to the H2 line (after H2, 27 September 2026), kept as that binding's record.** Candidate re-read at `ef144760`: netlist
`v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net` sha256/16 `085f833362fbbda8` (round 8, `7bef62bd`), intent
`pcb-p-pack-intent.json` `6ff1b8129a5c5aff`; the committed board file `d79865e7b1aceb95` is the two-layer P4, which
predates the schematic and decision 28. The power figures of this sheet are checked against `calc/rail_widths.py` on
that intent: the pack path's rails read the same. Board P is not at layout entry: **6 reasons at H2**
(`CURRENT-EVIDENCE.md`): PWR-001 FAIL (BAT_F, PBI, SEC_VDD, SW and VCC_F declared by no rail), SI-001 INCONCLUSIVE,
BAT-001 FAIL (the gate's table `pcb_pack_protection.yaml` still describes the older generator, REQ-044), FEA-005,
FEA-006, FEA-007. Known changes of the H2 line: round 8 is merged (`7bef62bd`: the JST headers the catalogues list,
the supply filters declared class A, the FET bypass pair) with the temperature windows of `73d5df1e`. Every other line below is the reading at `e3aedb25`, not re-read against the H2 netlist; where it and a record disagree, the record governs (README).

As first written: a view over the records at `main` `e3aedb25` (conventions and shared rules: [README.md](README.md)),
candidate then netlist `4342c4cbe1b43dc4` (at `d90f30e4`), intent `59d679f0859fc203`, 14 blocker lines.

**Board P's placement is frozen only after the qualified battery review R-BAT has answered** (FEA-005's
FABRICATION_RELEASE stage: "its findings ... are answered before the placement is frozen and board P is released").
This sheet is an input to that review, not a substitute for it.

## 1. Stackup and layer use

- **Four layers, 2 oz outer, DECIDED** (owner decision 28 and ruling 7): JLC04162H-7628 recorded (0.070 mm outer,
  0.0152 mm inner, the fabricator's default). **Inner copper weight UNDECIDED** (0.5 oz recorded; 1 oz JLC041621-7628
  and 2 oz JLC041622-3313 exist) and decided by dc_drop on the first four-layer P with GND declared as a return
  (`v2/docs/STACKUP-DECISIONS.md` section 3.6).
- **Layer use (the P8 arm, 0 hard and 0 unrouted):** F sig and pack bands, **In1 GND, In2 GND**, B sig and pack bands.
- **Fabricator floors at 2 oz multilayer:** track and space 0.15 / 0.15 mm, solder-mask bridge 0.20 mm, PTH annular
  ring 0.254 mm (`jlcpcb-stackups-2026-09-25.md`, the 2 oz rows). P4's project classes carry 0.127 mm clearances
  (Default, GNDC, SENSE), under that floor; P8 routed at 0.16 mm, which clears it (decision 28 evidence).
- Single-sided SMD assembly (P4 carries nothing on its back); not conformally coated (`boards/p.json`).

## 2. Power: the pack path at 18 A on 2 oz

The table is `calc/rail_widths.py`'s output on the inputs this sheet's `bound` block names, row for row in the tool's
own order and cell for cell, and `v2/ecad/tools/constraints_bound.py` fails when the two differ; the `note` column is
this sheet's and is not compared (README, "The bound block"). A width printed 0.00 is under 0.005 mm, a current of a few
milliamperes: the fabricator's floor governs there, not the current.

| rail | V (working) | typ / peak A | governing A | outer mm | two outer faces, each mm | inner mm | barrels at the larger of peak and governing, 0.3 / 0.4 / 0.5 mm drill | note |
|---|---|---|---|---:|---:|---:|---|---|
| PACK_P | 14.4 (16.8) | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s | 11.95 | 3.36 | 195.80 (over 40 mm) | 25 / 21 / 18 | the pack path, the pack terminal |
| CELL4 | 14.40 | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s | 11.95 | 3.36 | 195.80 (over 40 mm) | 25 / 21 / 18 | the pack path, the top cell tap at the fuse |
| FUSED | 14.40 | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s | 11.95 | 3.36 | 195.80 (over 40 mm) | 25 / 21 / 18 | the pack path, after F1 |
| SCP_OUT | 14.40 | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s | 11.95 | 3.36 | 195.80 (over 40 mm) | 25 / 21 / 18 | the pack path, after F2 |
| PACK_N (return of PACK_P) | 0.1 (0.1) | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s | 11.95 | 3.36 | 195.80 (over 40 mm) | 25 / 21 / 18 | the pack path's return, W_N to R10; its stubs take the PACK class (item 2) |
| BAT_F | 14.4 (16.8) | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **SET 6**, new in `932cf9d7`, one of the supplies PWR-001 refused at H2: "U1's primary supply (SLUSC67B pin 32, 'Primary power supply input pin')"; 336 uA, which prints as 0.00 |
| VCC_F | 14.4 (16.8) | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **SET 6**, new in `932cf9d7`, one of the supplies PWR-001 refused at H2: "U1's secondary supply (SLUSC67B pin 26, 'Secondary power supply input'), from the pack terminal through R7 1 kohm" |
| SEC_VDD | 14.4 (16.8) | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **SET 6**, new in `932cf9d7`, one of the supplies PWR-001 refused at H2: "U2's supply (SLUSEG7D pin 1 VDD; RVD 300 ohm and CVD 100 nF, Table 8-1)"; "0.18 mA declared as the peak" |
| SW | 14.4 (16.8) | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s, series of SCP_OUT | 11.95 | 3.36 | 195.80 (over 40 mm) | 25 / 21 / 18 | **SET 6**, new in `932cf9d7`, one of the supplies PWR-001 refused at H2: "the common drain of Q1 and Q2 (CSD17570Q5B, TI SLPS471D), the pack's whole current: 10 A typical and 18 A peak as SCP_OUT and PACK_P carry it". **Pack path**: the intent file declares it a series segment of SCP_OUT at SCP_OUT's own currents, so it is judged at PWR-F12's 18 A with the rest of that conductor (`calc/rail_widths.py`, WHICH RAILS ARE THE PACK PATH; the session's, 27 September 2026). The FETs want their drain copper (item 4), and this is it |
| SCP_HTR | 14.4 (16.8) | 3.50 / 3.50 | 3.50, typical (PI-001) | 0.84 | 0.32 | 10.11 | 5 / 4 / 4 | **SET 6**, new in `932cf9d7`: "the chemical fuse's heater return (Eaton SCF9550-30-05, ELX1135: heater 4.8 to 8.0 ohm, operating 10.5 to 23.5 V, opens the fuse within 60 s)"; "declared at 3.5 A typical as well as peak because a 60 s event is a steady state for copper" |

1. **Pack bands on both outer faces, each at least 3.36 mm wherever the current is shared equally, or 11.95 mm on a
   face that carries it alone**, generator-laid and stitched (PWR-F12 carried to stages PACK_CELLS and PACK_FETS of
   `pcb_energy_chain.yaml`). The bands of P's earlier layouts were 3 mm on both faces (`LAYER-DECISIONS-2026-09-11.md`,
   the P row), under 3.36. At 10 A typical, the governing current before PWR-F12, 4.08 mm on one face or 1.38 mm each
   on two.
2. **PACK_N's stubs take the PACK class, 0.8 mm** (its own narrowest pad; the shared PWR class caps at 0.6 mm by the
   0.61 mm pads of Q1): proved on a routed arm, PACK_N MET at 0.800 mm (`boards/p.json`
   `_the_pack_return_gets_a_class_of_its_own`, `_pi001_passes_on_p10s_board_and_the_prediction_was_right`). The current
   itself runs in the bands.
3. **The return shares onto the inner GND planes** between R10 and the cell block's negative through every GND via;
   that share is what decides the inner copper weight (section 1). The PI-003 site P10 found (a 0.50 mm barrel at
   (87.6, 114.4) at 1.37 A against 1.30 A) is named for the next phase (`boards/p.json`).
4. **Parts on the path, at 18 A** (`records/rv-pwr/pwr-chain-redeclaration.yaml` parts_on_the_path): Q1 and Q2
   CSD17570Q5B rated 53 A at 25 C on a 1 in2 2 oz pad, about 0.3 W each at 18 A (so the FETs want their drain copper);
   R10, the 2 mOhm shunt, 0.65 W at 18 A, declared "2m 2512 2W" with no part number; F1 the 25 A blade in a Keystone
   3568 holder; **F2, the SCF9550-30-05 chemical fuse, 0.32 to 0.81 W of its own at 18 A, -20 to +60 C, no derating
   published: its margin during a key-down from a +55 C block is unknown** (PWR-F12, FEA-004).

## 3. Pairs

SMBus only (`pcb_interfaces.yaml` SMBUS_GAUGE: 100 kHz, open drain, no impedance target), the one conductor pair that
leaves the board, over the plane. SMBC and SMBD carry D2 and D3 PESD5V0S1BA (intent clamps).

## 4. Return paths

RET-001 and RET-002 were what two layers could not hold (decision 28); the four-layer stack with In1 and In2 as GND
answers them by construction. Board P's nets are CLOCKED_DIGITAL at most (SMBus, the battery-trip interrupt), the rest
DC (`boards/p.json` signal classes).

## 5. Sensing and protection placement (FEA-005's layout constraints)

These are the constraints FEA-005's layout-entry stage asks to have stated, collected from the battery packet
(`v2/docs/review-packets/battery/`) and the board's declarations. Each is for the R-BAT reviewer to confirm or change.

1. **Coulomb counter Kelvin pair:** SRP_F and SRN_F from R10's own pad centres (SRN_F taps R10.2 through R9.1), routed
   together, filtered at the gauge, at least 0.5 mm from any other conductor's copper (`pcb_sensitive.yaml` board p;
   `pcb_emc.yaml` board p: "the coulomb counter's SRP and SRN are a Kelvin pair at the shunt's own pads").
2. **Cell taps:** every tap a Kelvin connection through its 100 ohm and 100 nF filter to its own cell node, never
   sharing copper with the load current (VC1_F to VC4_F at 0.5 mm; `pcb_emc.yaml` board p, the path "IR drop in the
   copper the taps share with the load, read as a cell voltage").
3. **The second level's thermistor path** (`SECONDARY-OT-DECISION.md` section 4; `PROTECTION-ARCHITECTURE.md` O-11):
   U2 pin 12 (TS) to R34 (270 ohm) to J_TS2 pin 1, R33 (18 kohm) from TS to VSS, TP15 on TS_SEC; J_TS2 a separate
   two-way socket (JST B2B-PH-K-S-GW) so an unplugged J_TS blinds only the gauge. **TP15 and TP8 (PACK_N) are both
   reachable with the board assembled**, because commissioning proves J_TS2 by resistance between them before the cells
   are connected and by scope after (`FUSE-INTERPRETATION.md` steps 1 and 4; the board has no GND test point, so TP8
   stands in).
4. **The cell thermistors** on J_TS (four 103AT-2, one per series group) and the second level's own 103AT-2 on the
   hottest cell are off board; their leads' insulation and routing inside the pack is an open packet item
   (`SECONDARY-OT-DECISION.md` line 170).
5. **RT1, the PTC element (Murata PRF15BB103RB6RC) for the gauge's PTC input, sits beside Q1 and Q2**
   (`pcb_decisions.yaml` n 40 outcome; `gen_sch_p.py` line 243): its purpose is to read their heat, so it stays
   thermally coupled to their copper.
6. **F2 and its heater path:** F2 is fed from the cells through F1 and its own element whatever the FETs do
   (`FUSE-INTERPRETATION.md` line 62, TI's placement); its heater switch is driven by both U2's COUT and the gauge's FUSE
   output through the arming jumper JP1 (decision 40). **JP1 is reachable for commissioning** (closed only after the
   gauge's image is written and read back). **The session recommends F2 away from Q1, Q2 and R10's copper** so its body
   follows the cell block rather than the FETs' heat (INFERRED from PWR-F12: F2's +60 C rating with an unknown margin
   and 0.3 W per FET plus 0.65 W in R10 nearby; reason: it can only lower F2's temperature; reversal: the extended
   protection test's thermocouple on F2's body).
7. **PACK_P's clamp** D1 SMBJ20A (intent clamps) at the pack terminal lands.

## 6. Decoupling (decision 42)

- **G8:** C1, C6, C8 and C14 declared class A with their clauses (SLUSC67B, SLUSEG7D); class A takes the nearest free
  seat outside the fan at the pin end of its RC with no high-current conductor between (`DECOUPLING.md` sections 6 and
  8.3). The protector FET bypass capacitors on wide copper (W2's F-DC-03, BQ4050 10.1.1, INFERRED from TI's figure
  labels) stay with board P's writer.
- **No far-side seat on P** (single-sided). P's three gauge capacitors sat 11.0 to 15.0 mm from their pins on the
  regenerated placement because the gauge U1 is PACKED, not FIXED, so no slot can be reserved before the packer places
  it; giving U1 a FIXED seat is the answer the record names that decision 42 leaves open (`boards/p.json`
  `_p_decoupling_cannot_be_placed_and_both_passes_say_why`).
- Class A is provisional and goes to the R-BAT reviewer as an item (`DECOUPLING.md` section 10).

## 7. Mechanics and access

- **Outline 70 x 44 mm** in the pack pocket beside the 4S3P block: the pack group (block plus board P plus 2 mm) is
  205.5 mm in Y between the east legs (`CASE-MARGINS.md` M5, OPEN until the pack is placed and check T4 runs; M4a the
  block's corner to Peli's fillet, OPEN).
- **Leads:** 12 AWG PACK_P and PACK_N on the solder lands W_P and W_N to the XT60 (`pcb_energy_chain.yaml` PACK_LEAD).
- **Test access:** 15 test points; JP1 the arming jumper; the commissioning readings O-9 (TP11, TP15, RT1, JP1's closure
  with polarity, Q2's gate under a UV hold) need their pads reachable (`PROTECTION-ARCHITECTURE.md` line 191).
  Bring-up: `PCB-BRING-UP.md` board P.

## 8. Spacing

No declared rail reaches 20 V (the pack is 16.8 V at full charge); ISO-001 is not applicable to P by the registry.

## 9. Thermal

Q1, Q2, R10 and F2 are board P's own heat sources (section 2 item 4). The cells' temperature in
PS-TYP at +20 C is 45.4 to 81.3 C on the independent enclosure bound, against the 60 C discharge limit, a bound that
includes failure; the second level's own thermistor opens F2 at 62.7 to 77.5 C (`POWER-THERMAL.md` 9.2). What decides
it is the empty-case heat-balance test (FEA-004), which needs a purchase the owner has not authorised.

## 10. Analyses that need placed or routed geometry, or hardware

| Stage | What | Needs |
|---|---|---|
| PLACED_BOARD | SCH-002, DEC-001 (G8, U1 FIXED), IMP-002, ANA-001, THM-001, PLC-001, MEC-001 | the four-layer regeneration |
| ROUTED_BOARD | PI-001 (the pack bands at 18 A; PACK_N), PI-002, the inner planes' share of the return (the inner weight), RET-001, RET-002, GND-001, STK-001 (JLC04162H-7628 or the row the inner weight selects), EMC-001, RTE, VIA, PLN | the routed four-layer candidate |
| FABRICATION_RELEASE | FEA-005 (R-BAT answers BAT-F01 to BAT-F14 and Q-TI-1 to Q-TI-7 before the placement is frozen); FEA-004 (F2 inside +60 C at 18 A for 60 s from +55 C, by Eaton's written answer or a coupon test of the part); FEA-006; BAT-001 on the laid-out copper | the owner's engagement of R-BAT; Eaton's answer or a purchase |
| PROTOTYPE | the gauge's golden image written and read back; O-9 on the bench; `TEST-PLAN.md` section 5 on the built pack; the extended protection test (18 A for 60 s from a +55 C block, a thermocouple on F2's body at most +60 C) | a built pack |
