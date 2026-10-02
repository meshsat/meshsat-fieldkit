# L4-E9: the connected power architecture and Layer 4's closure gate for it (MESHSAT-1357, 1 October 2026; round 2, its fix rounds and the update round, 2 October 2026)

**Prototype design, desk arithmetic.** Nothing is bought, built, powered or measured, and no board of this set has a layout.
This page edits no generator, registry record, Layer 3 file, `pcb_interfaces.yaml`, `HW-FW-CONTRACT.md` or other record; its
circuit changes are drafts (`apply_gen_sch_e_q1.py`, `apply_gen_sch_e_f1.py`, `apply_gen_sch_e_hotswap.py`, `apply_gen_sch_a_u17.py`, and
L4-E11's `apply_gen_sch_e_entry.py` and `apply_gen_sch_a_guard.py`, which it carries) and its interface
changes are drafts for Layer 5 (`LAYER5-HANDOVER.md`). Every figure below is printed by `l4e9_power_path.py` into
`l4e9_power_path.out` ("out N" is its section), which reads each figure from a generator, a committed netlist, a record's
committed output or a maker's document, each pinned by sha256, and never retypes a figure another record computed. Classes:
MAKER, NETLIST, MODELED, INFERRED, CONDITIONAL (a calculated result on an unwarranted assumption or an open measurement),
ASSUMPTION, PENDING, and SESSION for a choice this record takes.

**Inputs.** The Layer 4 records on main: `../l4e/` (the energy architecture, A1 against A2, the findings A-1, A-2, B-1 to B-5,
C-1 to C-9, R138, O-1, O-2; the review L4-R01 to L4-R04), `../l4e4/` (current limits, PROVISIONAL), `../l4e5/` (source control,
H3), `../l4e6/` (fault handling), `../l4e7/` (the solar stage's settings), `../r11dep/`, `../s120/`, the power budget and load
trace, `HW-FW-CONTRACT.md`, `pcb_interfaces.yaml`, `DECISION-31-PROTECTION-TOPOLOGY.md`. Read from their branches, pinned:
**L4-E8** (the VBUS20 bank) at `fnd/l4e8` `3c8f7a1f`, accepted by the coordinator's check 3; **L4-E7R** (the solar stage's
control and entry, the selected solution (C) at R66 8.45k and RIMON_IN 31.6k with its CS101 correction) at `fnd/l4e7`
`675b8068`, ACCEPTED by the coordinator's check 4 at `91e9a4b5` with named conditions (D-01 resolved in design);
**L4-E10** (FEA-008, the cell and thermal design) at `fnd/l4e10` `79b2f568`, final, accepted by the closing check `573c8b8f`
as a decision-ready comparison that does not close FEA-008; **L4-E11** (source-only operation U-04, the vehicle-entry
interconnect D-06 and the entry's fault timer D-09) at `fnd/l4e11` `3298d1f1`, accepted by the closing check `a15ab384`; **L4-E12**
(MESHSAT-1478, the electronics against the inside air, U-02) at `fnd/l4e12` `a86be47b`, accepted by the closing check `db41c95d`.
**L4-E13** (U-03, the panel's open circuit) is pending: U-03 stays as it stood. Part A of round 2 (`L4E9-ENTRY-PROPOSALS.md`,
out 11) checks Q1, F1 and U17 against their makers' sheets. The fix round answered the collaborator's focused check
(`checks/astra-check-l4e9-1.md`, NOT YET) and the final round its targeted recheck (`checks/astra-check-l4e9-2.md`, NOT YET);
the coordinator's closing check (`checks/check-l4e9-3.md`) read the gate as not closed on D-06, D-09 and U-01 to U-04.
**The update round** (the coordinator's instruction of 2 October 2026, out 12) brings the architecture and its gate up to date
with the accepted results of L4-E10, L4-E11 and L4-E12, and answers L4-E11's E11-19: every finding that rested on the LM5069's
power limit re-judged for the TPS48110-Q1 entry L4-E11 selected.

**The owner's frame** (the Current owner brief, `OWNER-INSTRUCTION-2026-09-30.md`; his instructions of 1 and 2 October 2026):
battery and solar both required; the store inside the Peli 1450, no external battery; HF and the tablet kept; D-06's single 4S3P
stands; 48 to 72 hours an objective, tablet charging optional consumption; A2, the lid pack, the 16.340 V hold and P-03's 200 W
stay proposals. The applicable normal, reverse-input, transient and fault conditions are verified, not only headline ratings;
downstream tasks are kept apart from unresolved choices that could overturn the architecture, and an owner does not close a
choice. Layer 4 selects the power architecture and establishes its feasibility; Layer 5 writes the interfaces it creates.

## In short

- **Selected: A1**, D-06's one 4S3P pack inside the case, fed by two sources ORed onto one raw bus (the panel through board E's
  LT8705A stage, the vehicle or shore supply through its ideal diode and, since L4-E11, a TPS48110-Q1 breaker in place of the
  LM5069 hot swap), converted once to a regulated 20 V charge bus by board A's LM5176 front end and once more by the BQ25731
  charger onto the system node VBAT, from which every load converter and both outlets run. **A2** (base 4S6P plus a separately
  protected lid 4S9P) stays a proposal to change D-06.
- **The selected solutions are in the rows** (out 4): L4-E7R's regulation at RIMON_IN 31.6k (2.5485 A nominal, 2.9318 A highest)
  with its backstop on SWEN (static bound 93.5521 W, CONDITIONAL), corrected entry and CS101 correction (accepted); L4-E8's bank
  with its losses carried into the energy and thermal budgets; Q1 the CSD19532Q5B, F1 the Littelfuse 0997010.WXN and U17 on R227
  (part A); **L4-E11's vehicle entry**: UVLO on at 7.87 / 8.14 / 8.44 V of DC_P, OV off above 39.6 / 40.36 / 41.22 V, a breaker at
  6.364 / 6.8 / 7.136 A after 0.247 / 0.37 / 0.49 ms and a filtered short-circuit trip at 10.36 / 12.04 / 13.87 A, Q7 a CSD19536KTT,
  the interconnect at least 20 A continuous with its loop specified by resistance (900 A at most from a stiff source), the
  corrected knee (a flat 1.82 A from 7.95 V) and the guard's R14 76.8k; **L4-E12's route**: the hold in E5 only, T-H1's binding
  line 2.159 W/K lid open with the fans.
- **Fourteen interfaces: 2 MEET, 12 are CONDITIONAL, none NOT MET, none PENDING.** IF-05 moves from NOT MET (D-09) to CONDITIONAL
  (every start inside Q7's derated chart, the in-service hard short OPEN on the loop's inductance); IF-11 moves from NOT MET (75.00
  C at the floor) to CONDITIONAL (70.00 C in E5 under the hold at the binding line, U-02). The as-drawn defects stay visible as
  "as drawn" checks: the LM5069 cannot start from a 9.00 V plug (8.987 V against POREN's 9 V), its power limit at 4.7429 mV, the
  drawn restart guard above the plug's operating point, the drawn interconnect at 13.5 A against a 13 A contact.
- **E11-19 (out 12a):** the selected entry limits no power, so the LM5069's power-limit pulse, its 5 mV floor (D-07), its fault
  time against the start (D-09) and its breaker's event exist only for the LM5069 alternative. A start into a resistive fault uses
  0.704 of Q7's derated chart, the ordinary start 0.182, a start into a hard short 0.743 (CONDITIONAL on the transconductance
  bound); a hard short in service stays inside Q7's derated 178.2 A only with the loop's inductance at least 2.08 uH (2.084 uH
  reproduced here): OPEN, E11-20 (R-134). F1's I2t over every start and fault pulse is at most 6.7311 A2s, 7.24 % of its typical
  melting 93 A2s. R-118 is restated as E11-17. **No new material defect.**
- **The closure gate (section 7): NOT CLOSED.** Criteria 3 and 4 PASS; 1, 2 and 5 are CONDITIONAL. Kept apart:
  - **material defects: none open.** D-01 to D-05 and D-08 resolved (drafted or bounded), D-06 resolved in design by L4-E11's
    interconnect with its evidence items E11-10 to E11-16, D-07 and D-09 superseded by the replacement (they apply only if the
    LM5069 is kept, where L4-E11 resolved D-09 with C5 and C121);
  - **four unresolved choices that could overturn the architecture**, which no owner closes: U-01 FEA-008's cell (the owner's two
    items); U-02 MESHSAT-1478, CONDITIONAL on T-H1 at or over 2.159 W/K and L4-E12's conditions, with CFL-002 the owner's question;
    U-03 O-1 (pending L4-E13); U-04 source-only operation, a CONDITIONAL CANDIDATE on E11-05, E11-06, E11-09, E11-22 and E11-23;
  - **the downstream tasks**, 137 register items, each with one owner and an acceptance that close the assignment, not the item;
  - **the owner's items** (section 7d): CFL-002 (A, B or C), U-01's specification request and then the cell change, and the
    outside-contact drafts with their paths.
- **Endurance (section 10):** A1 runs 2.52 h on battery at +20 C and first interrupts at hour 6 or 2 on the candidate panel; it
  needs +1361.5 / +2094.1 Wh more storage for 48 / 72 h, plus at most 13.4 Wh a day at L4-E7R's accepted regulation and 17.7 Wh if U-01's
  cell is adopted; none of L4-E10 to L4-E12 moves these figures. DR-01 stands; every mandatory function is intended to be
  delivered, subject to the open conditions named here, and no service is reduced to narrow the gap.

## 1. The selected architecture as one connected design

```
SOURCES
 panel (REQ-016: Voc <= 25 V at -20 C, <= 100 W into the stage)          vehicle or shore 9 to 36 V (REQ-015)
   | J_SOLAR (VH), F2 10 A                                                  | D38999 size 12, J_DCIN 20 A class, F1 0997010.WXN, D10
   | PV_P -> sense bank -> TRK_VS: D4 SMCJ28A, 50 V bulk, C71..C74 [L4-E7R]  | U3/Q1 LM74700 ideal diode, Q1 CSD19532Q5B 100 V
   | R59 -> TRK_VIN                                       board E          | DC_P, D1 SMCJ40A, R19 4.5 mOhm            [L4-E11]
   v                                                                       | U6/Q7 TPS48110-Q1 breaker, CSD19536KTT: UVLO 7.87..8.44 V,
 U5 LT8705AI buck-boost: hold 17.593 V (16.970..18.221),                   |   OV 39.6..41.22 V, overcurrent 6.364..7.136 A after
                                                                           |   0.247..0.49 ms, short circuit 10.36..13.87 A, retry 0.5 s
   regulation RIMON_IN 31.6k 2.5485 / 2.9318 A; backstop on SWEN (U18,     | L2 SRF1260-1R0Y choke
   INB filter, U19, U20) trips 3.0468..3.7408 A, static bound 93.5521 W     |
   TRK_OUT ceiling 28.28..30.15 V (R10 232 k, L4-E5)                       |
   | U4/Q2 ideal diode                                                      |
   +--------------------------------> VIN_RAW <-----------------------------+   (the tracker back-feeds DC_P through Q7's body diode)
                                        | D2 SMCJ40A (E and A); dock: four Mill-Max 9 A pins J_VR1..4
                                        v                                                   board A
 U2 LM5176 front end: R11 8 mOhm (average limit), R12 12 mOhm (cycle-by-cycle), no hiccup, U34 restart guard (R14 76.8k)
                                        | VBUS20 19.08..20.96 V (bound 23.40 V); six EEHZK1V331P, each behind 45 mOhm; Cc2 3.3 nF
                                        v
 U3 BQ25731: R16 10 mOhm; IIN_HOST 4.70 A; the H3 line on ILIM_HIZ (in hardware; the corrected knee: flat 1.82 A, HIZ < 7.378 V)
                                        | VBAT = VSYS, the system node, 10.0..16.884 V; D1 SMCJ18A
             +--------------------------+--------------------------+-----------------------------+
             v                          v                          v                             v
 PACK (D-06, 4S3P 35E; U-01):    LOAD CONVERTERS               OUTLETS                        PA AND HF
 R17 5 mOhm, A F1 25 A, pack     slot rails, device rail,      USB-C: U19 LM5176 5/9/15 V,    +13V8_PA (U13) to J_PA, keyed
 pins (4 x 9 A), E F3 25 A,      logic, monitor (U21), heater  Q27, R138 5 mOhm, U18 OCP       at most 60 s (D-11)
 XT60, board P: F1 25 A, F2      (U22), board E always-on on   3.793..4.576 A (tablet         +12V_HF (U15) to the QMX
 SCF9550 30 A, BQ4050, BQ7720700 CELL_F                        charge optional)              
 charge <= 3.0 A                 PS-IDLE-SPEC 42.8 W           PoE: VBAT -> R227 5 mOhm ->    both outlets dropped by
                                 PS-ALLTX 203.8 / 272.0 W      POE_VIN -> U16 boost +54V_POE  OUTLET_OK while the PA keys
                                                               0.6 A; U17 across R227
```

There is **no separate shore entry** (shore is J_DCIN) and **no USB-C input**: the USB-C port is a power-only outlet (D-12).

## 2. The interfaces (out 4: every figure, check and source)

Modes: PS-IDLE-SPEC (42.8 W at the pack terminals), PS-ALLTX (203.8 W plan, 272.0 W high) and the PA keyed alone at 113 W
(162.3 W), charging at the window (the stage takes at most 53.42 W in at the hold under L4-E7R's regulation; 93 W out at the
window is a ceiling), and the tablet outlet (45 W on PS-TYP, 112.3 W plan). Thermal basis: the worst inside air, 62.1 C lid
closed (59.2 C lid open); at the margins L4-E12's route: at T-H1's binding line 2.159 W/K (lid open, fans) 67.55 C (E3-O) and
70.00 C (E5 under the hold); at LO-01a's floor with no hold 71.25 and 76.25 C (L4-E10's corner plus the ballasts).

| Row | Interface | Voltage, both sides | Current asked / available (modes) | Losses | Thermal assumption | Protection, each side | Settled by | Status (class) |
|---|---|---|---|---|---|---|---|---|
| IF-01 | panel to the solar entry | at most 25 V at -20 C (candidate 24.05 V nominal) / D4 standoff 28 V on TRK_VS; under CS101 the input at most 27.82 V; TRK_VS 44.25 V and PV_P 44.74 V at the capability scenario | hot short circuit 6.802 A with the sheet's tolerance / F2 10 A; J_SOLAR's VH with AWG 18 no stated rating (7 A shrouded); under CS101 the filtered ripple at most 0.0585 A against a 0.1130 A margin | the lead about 0.0465 Ohm; the bank 0.5262 Wh a day | the entry at 62.1 C inside air; the bulk up to 4.45 times its ripple rating under CS101 (M2 reads it) | none / F2, the 50 V bulk ahead of the bank, D4 and C71 to C74, the INB filter (L4-E7R, drafted) | l4e O-1, L4-E7R (accepted) | CONDITIONAL (ASSUMPTION): the VH rating, the loop's typical rows (break-even 2.51 times), the bulk's temperature, the bank's pulse capability |
| IF-02 | PV_P through U5 to TRK_OUT | hold 16.970 / 17.593 / 18.221 V, at most 25 V; SWEN off below 2.662 V on TRK_LDO33 / ceiling 28.28 to 30.15 V | the stage's input at most 100 W (REQ-016) / the regulation 2.5485 A nominal, 2.9318 A highest (44.84 and 53.42 W in); the backstop 3.0468 to 3.7408 A at 25 V; the static bound 93.5521 W, the regulation's corner 73.3436 W | stage 0.93 DECLARED (C-8) | U5's junction about 105.4 C (INFERRED) against the I grade's 125 C | the regulation, the backstop on SWEN inside 1.087 ms after the filter's 0.4205 J / U4 | l4e7, l4e5, L4-E7R (accepted) | CONDITIONAL (CONDITIONAL): G_CM and U18's VIN+ bias (break-evens 168.8 % and 22.0 mA), the 0.1 s interpretation |
| IF-03 | TRK_OUT through U4/Q2 to VIN_RAW | at most 30.15 V / VIN_RAW to the 43.18 V basis with TRK_OUT at 0 (the selected OV maximum 41.22 V) | 4.22 A at H3's lowest settle at the window / declared 10.33 A | Q2 | 62.1 C inside air | the stage / U4 blocks | l4e5, this record | MEETS (MAKER/NETLIST), with C26 and C27 re-rated (as drawn 121 % of 25 V) |
| IF-04 | vehicle and shore into DC_F and DC_P | 9 to 36 V at the plug with CS101's 2.83 V peak, reversed to -36 V / the selected entry's OV off above 39.6 / 40.36 / 41.22 V (as drawn the LM5069's 37.78 / 40.09 / 42.49 V); D10 44.4 V either way at 25 C, 42.4 V at -20 C on a typical coefficient (CONDITIONAL), above the OV maximum both ways | in service at most 5.983 A from a 9.00 V plug; the breaker 6.364 / 6.8 / 7.136 A; a stiff source's fault at most 900 A (the interconnect's specified floor; 569.8 A with the drawn cable) / F1 0997010.WXN 10 A (7.3 A at its 80 C column), 1000 A at 58 V DC; Q1 17 A; J_DCIN a 30 A class and the interconnect at least 20 A continuous (D-06, resolved in design) | the plug to DC_P 94.47 mOhm hot, 3.382 W at 5.983 A; Q1 at most 0.487 W at 7.136 A | Q1's junction at most 86.4 C; the interconnect's elements at 20 A where installed | supply's own / F1 in a 20 A holder, D10, U3/Q1 (CSD19532Q5B), D1, the entry's UVLO and OV | d8dec31, this record (part A, out 12), L4-E11, l4e5 | CONDITIONAL (CONDITIONAL): D10's cold coefficient, the four-wire loop acceptance (R-130), the interconnect's makers' ratings and F1's clearing I2t at 900 A (R-113, R-115, R-129 to R-132) |
| IF-05 | DC_P through the selected entry (TPS48110-Q1, CSD19536KTT, R19 4.5 mOhm) and L2 to VIN_RAW | D1 clamp 64.5 V; 8.971 V before any current and 8.435 V at 5.983 A from a 9.00 V plug / U6 VS 80 V (100 V absolute), its pins at most 18.36 V against 20 V; Q7 100 V; the UVLO on at most 8.44 V, off at most 7.95 V | in service 5.983 A, up to 7.136 A under the breaker; the start 0.382 to 1.219 A for at most 2.5 ms; starts into a resistive fault (0.704 of the derated chart) and into a hard short (73.4 A, 0.743); a hard short in service 13.87 A plus VIN x 8.31 us / L / the breaker 6.364 / 6.8 / 7.136 A after 0.247 / 0.37 / 0.49 ms, the short circuit 10.36 / 12.04 / 13.87 A filtered, retry 0.5 s; Q7's derated IDM 178.2 A; L2 98.2 C at 7.14 A against 105 C | DC_P to VIN_RAW 47.87 mOhm hot, 1.714 W at 5.983 A; Q7 0.22 W | the 0.4454 derating holds while Q7's case stays under 108.19 C | D1 / D2, the breaker, the UVLO and OV, the slew-limited start | L4-E11, this record (E11-19, out 12) | CONDITIONAL (CONDITIONAL): the in-service margin on the front end's efficiency at least 0.88021 (E11-06), the fault starts on the derating and the transconductance bound (E11-17), the hard short in service OPEN on the loop's inductance (E11-20); as drawn the LM5069 cannot start from a 9.00 V plug |
| IF-06 | VIN_RAW over the dock to board A | the corrected knee's certain HIZ 7.378 V (solar) to 30.15 V; vehicle 9 to 36 V at the plug (8.148 V at 5.983 A from 9.00 V); at most 41.22 V (43.18 V the basis) / U2 60 V | in service at most 5.983 A (a 9.00 V plug); fault at most 11.65 A (13.315 A at 7 mOhm) / declared 14.10 A, four 9 A pins | the dock's contacts | the pins about 6 K over air at 14.10 A (IF-AE-DOCK) | the entry, D2 / D2, U34 | l4e5, l4e6, IF-AE-DOCK, L4-E11 | MEETS (INFERRED); A-N1 a recorded residual |
| IF-07 | VIN_RAW through U2 to VBUS20 | 7.378 to 43.18 V / 19.08 to 20.96 V, bound 23.40 V | 4.964 A asked through R11 / 4.986 A stacked minimum at 62.1 C with C-1's taps; highest permitted 7.262 A; R12 peak limit 8.06 A over a 6.50 A service peak | front end 0.93 DECLARED (at 8.1 V at least 0.88021 for the entry's margin) | FETs at most 130 C on the assumed 50 C/W (C-3); L1 at most 85 C (C-5); R11 68.8 to 77.5 C | U34 (R14 76.8k: 6.754 to 7.139 V, 0.239 V under the certain HIZ), D2 / R11, R12, no hiccup, OVP; no clamp on VBUS20 (S-111) | l4e4, l4e5, l4e6, r11dep, s120, L4-E11 | CONDITIONAL (CONDITIONAL): C-7, V-A07, C-5, C-3; as drawn the guard falls at up to 8.309 V, over the 9.00 V plug's 8.148 V |
| IF-08 | VBUS20's bank | 23.40 V bound / the cans' 35 V | every can at most 2.4096 A (R11 8 mOhm), 2.7661 A (7 mOhm) / the rule's 2.7745 and 2.7709 A | ballasts at most 2.09 W (0.0093 W at nominal parts), in the energy and thermal budgets once | the cans' rise a bench reading (lifetime); the cold ESR envelope INFERRED; the ballasts' heat at most 1.25 K on the inside air at T-H1's floor | R12, R11 / the ballasts | l4e8 (accepted) | CONDITIONAL (CONDITIONAL): lifetime, the cold envelope, the 7 mOhm fallback |
| IF-09 | VBUS20 through U3 to VBAT | 19.08 to 20.96 V / U3 32 V absolute; VBAT 10.0 to 16.884 V; SYSOVP 19.0 to 20.0 V | the window needs 4.517 A / U3 minimum 4.537 A (C-7); 84.5 to 99.6 W at VBAT; charge at most 3.0 A; with no usable pack 29.09 to 42.52 W at a 9.00 V plug against the shed warm-up's 28.12 W | U3 0.9733 INFERRED | 62.1 C inside air; the charge only inside the cells' 0 to 45 C window (the gauge) | H3 line, IIN_HOST, VINDPM, ACOV / BATOVP 17.64 V, SYSOVP, the gauge's OCC 5 A; rules R-a to R-d | l4e4, l4e5, s120, FW-A02, L4-E11 | CONDITIONAL (CONDITIONAL): C-7; U-04 (E11-05, E11-06, E11-09, E11-22, E11-23) |
| IF-10 | VBAT and the pack | 10.0 to 16.884 V / D1 standoff 18 V, the pack FETs 30 V | PS-IDLE-SPEC 2.5 to 4.3 A; the PA keyed at 113 W 16.6 A at 10.0 V; PS-ALLTX's 18 A at an 11.48 V stack; a dead pack's charge under R-b at most 21.22 W / declared 10 A continuous, 18 A peak; OCD1 20 A for 2 s; XT60 30 A | 22.5 mOhm path | the cells 0 to 45 C charge, -10 to 60 C discharge (REQ-046); FEA-008 not closed (L4-E10: approach (II), CONDITIONAL); F2 near +60 C at 18 A (PWR-F12); Q2's diode under R-b at most 124.9 C | D1, A F1 / BQ4050, BQ7720700, F1, F2 | pcb_pack_protection.yaml, POWER-THERMAL 7, FEA-004, L4-E10, L4-E11 | CONDITIONAL (CONDITIONAL): PWR-F12, U-01, R-b's case (i) and board P's copper (E11-22) |
| IF-11 | VBAT to the load converters | 10.0 to 16.884 V / the converters assumed to run to 10.0 V | PS-IDLE-SPEC 33.1 to 82.8 W (42.8 W plan); PS-ALLTX 168.9 to 272.0 W (203.8 W plan); 8.4 W undocumented / each converter's own rating (pwr_budget.py) | the converters' floors | at T-H1's binding line 2.159 W/K (lid open, fans) E3-O's mixed air 67.55 C (27.086 W) and E5's 70.00 C under the hold (21.587 W), the ballasts counted once; the design as it stands (LO-01a's floor, no hold) 71.25 and 76.25 C | eFuses (TPS2596 21 V against SYSOVP 20.0 V) / each converter | pwr_budget, load_trace, POWER-THERMAL, L4-E12 | CONDITIONAL (ASSUMPTION): U-02 (T-H1 at or over 2.159 W/K, the hold's reference, the fans, placement); the 8.4 W; the converters' floor |
| IF-12 | VBAT to the USB-C outlet | VBAT 10.0 to 16.884 V into U19 / 5, 9 and 15 V contracts | 3 A each; with PS-TYP 112.3 W plan, 7.8 A at 14.4 V / trip 3.793 to 4.576 A; receptacle 5 A; J_USBC_OUT unrated | U19 0.93 | R138 its own 3.5 K at the trip (L4-E4); 62.1 C inside air | OUTLET_OK, C2 / U18 OCP and OVP | l4e4 | CONDITIONAL (ASSUMPTION): VI(TRIP)'s row, the header |
| IF-13 | VBAT through R227 to the PoE stage and U17 | VBAT 10.0 to 16.884 V, 20.135 V at the pack-open bound, 29.2 V at D1's pulse / 54 V; U17 on VBAT and POE_VIN, common mode at most 20.135 V against 36 V (as drawn 54 V against 40 V); POE_VIN at most 33.77 V at a hard connect; 0.072 V under VBAT in the boost current-limit case only | 0.6 A at 54 V; 3.682 A at the stage's input at 10.0 V, 14.33 A at its fault bound; a buck fault 11.71 A peak, 10.71 A RMS / R227 5 mOhm 3 W; 18.59 and 72.38 mV against 81.92 mV (16.384 A); a saturated sample is not damage (40 V differential) | U16 0.88; R227 at most 0.0685 W in service, 0.58 W in a buck fault, 2.879 mJ nominal at a hard connect (the maximum unresolved) | 62.1 C inside air | OUTLET_OK / U16's limits, TPS23861 | HF-F02, this record (part A, B3) | CONDITIONAL (CONDITIONAL): R227's pulse rating and capacitance envelope (R-101), L10's L(I) at temperature (R-120, R-121) |
| IF-14 | VBAT to the PA rail | VBAT 10.0 to 16.884 V into U13 / 13.8 V | the drain 5.4 to 8.2 A uncharacterised; the pack 16.6 A at 10.0 V / declared 5 / 6 A, the stage's loop 7.2 to 9.5 A | U13 0.93 | key-down at most 60 s, the flange gated at +75 C and cut at +85 C (D-11, PROVISIONAL) | the K rules, OUTLET_OK / the stage | POWER-THERMAL 7.2, FEA-004 | CONDITIONAL (ASSUMPTION) |

**What the rows show about the stages together:**
- With the corrected knee the in-service maximum is 5.983 A from a 9.00 V plug (VIN_RAW 8.148 V), 6.4 % under the selected
  breaker's lowest 6.364 A, while the front end's efficiency there is at least 0.88021 (L4-E11; E11-06 measures it); on
  L4-E5's drawn line at VIN_RAW 9 V it was 4.629 A against the LM5069's 4.85 A.
- R11 8 mOhm (L4-E4) carries U3's 4.964 A with +0.023 A at 62.1 C with C-1's full taps; H3's pin path (5.095 A on a stiff
  26.50 to 27.24 V source) holds on R11 alone and needs V-A07 for the full taps (else 7 mOhm, which changes nothing else).
- R12 12 mOhm (L4-E6) bounds L1 and the FETs at the highest permitted current, 1.56 A over H3's 6.50 A service peak.
- The bank (L4-E8) holds every can at the same highest permitted current, and goes in only with R12; its ballasts are a loss on
  the charge path, counted once in the energy and thermal budgets (section 10).
- L4-E7R's regulation (2.9318 A at its highest) sits under its backstop's lowest trip (3.0468 A at 25 V) when the regulation's
  unprinted values are inside the joint assumptions, and the filtered CS101 ripple (0.0585 A) under that 0.1130 A margin; the
  stage takes at most 53.42 W in at the hold, so the 93 W out at the
  window that U3's IIN_HOST was sized for is a ceiling, not an expectation.
- **Stage resolutions that reached another stage:** L4-E5's raised tracker ceiling on Q1 in reverse (round 1; Q1 to the
  CSD19532Q5B); the vehicle entry's OVLO moved up by R22 and R23 (round 2): the raised maximum, 43.18 V, is re-checked on F1
  (58 V), Q2 and U2 (60 V), U4 (75 V), C26 and C27 (re-rated to 50 V) and D10 (44.4 V at 25 C); the LM5069's replacement
  (update round) moves the OV maximum to 41.22 V (the checks keep the 43.18 V basis), puts up to 7.136 A continuously through Q1
  (86.4 C) and F1 (its 7.3 A column), and changes the knee and the restart guard on board A (R-03, R-124).

## 3. Simultaneous operation (out 5)

Solar at the window, a vehicle at 24 V, the full load and charging together:
- **The sources share.** The tracker's ceiling (28.28 V at its lowest) sits above a 24 V vehicle, so the panel carries the bus
  first and the vehicle's ideal diode conducts only for what the panel does not give. The front end's input is H3's line at
  whatever VIN_RAW the sources settle at: at most 4.194 A at 24 V, 65.9 % of the selected breaker's lowest 6.364 A.
- **What reaches VBAT** is U3's: 84.5 to 99.6 W (its minimum at the lowest bus to its board-current maximum at the bus's top).
- **The loads take it first, the pack the rest.** PS-IDLE-SPEC (42.8 W) leaves up to 41.7 W to charge at most 3.0 A; PS-TYP with
  the tablet (112.3 W) draws at least 27.8 W from the pack; the PA keyed alone at 113 W draws at least 77.8 W; PS-ALLTX at least
  119.3 W (plan) and 187.5 W (high). With a source the pack's current is lower than on the pack alone, so D-11's floors hold as
  they do on the pack alone, and the outlets drop while the PA keys (OUTLET_OK).
- **No stage is pushed past its limit:** the entry under its minimum limit, R11 at 4.964 A at most, every can at most 2.4096 A,
  the charge at most 3.0 A against the gauge's OCC 5 A.
- **Per source at the plug (an envelope to state, not a defect; L4-E11 3h, the losses hot, the corrected knee).** At a 9.00 V
  plug the source delivers 29.09 to 42.52 W at VBAT; at 12 V 32.22 to 47.72 W; at 24 V 69.97 to 90.81 W; at 36 V 84.55 to
  99.64 W (round 2's figures at VIN_RAW with no loss: 19.9 to 36.6 W at 9 V). So a 9 V vehicle runs PS-IDLE-SPEC (42.8 W) with
  the pack supplementing, and charges only while the kit draws under 29.09 W. REQ-015's acceptance ("operates and charges
  across 9 to 36 V") is met in both of its parts with a working pack; with no usable pack it is U-04's CONDITIONAL CANDIDATE.

## 4. Startup (out 6)

- **Cold start on the pack** (`ARCHITECTURE.md` 4.3): with the pack connected the LTC2954 holds RAIL_EN low and board E's
  sensor controller runs on CELL_F; MAIN brings up board A's +3V3; DEV_EN is on by R42, so +5V_DEV and then the panel
  controller start; the panel runs FW-C01's order (PI_KILL low, ZEROIZE read, the expanders' outputs before their configuration,
  the charger with FW-A01 first, then SLOT_EN one at a time); each stage soft-starts on VBAT. The pack's precharge pin J_PRE1
  (10 Ohm, 2 W) mates first when the stack is seated.
- **A source arriving:** the selected entry (L4-E11) turns on at 8.44 V of DC_P at the most and slews the bus up, 0.382 to
  1.219 A for at most 2.5 ms (the drawn LM5069 cannot start from a 9.00 V plug: 8.987 V against POREN's 9 V); U3 is in HIZ below
  the corrected knee's certain 7.378 V, and the H3 line bounds its input from its first switching cycle with no host. The panel:
  the stage's own UVLO and soft start, then the hold at 17.593 V; SWEN stays off while TRK_LDO33 is under 2.662 V whatever the
  ramp (L4-E7R), and each backstop trip restarts the stage through its soft start.
- **A source leaving:** VBAT is the system node with no battery FET, so the pack carries the loads without a break; U3 resets
  IIN_HOST to 3.25 A and firmware writes 4.70 A again (FW-A16 restated); VIN_RAW falls through the restart guard (7.139 V at its
  highest with R14 76.8k, R-124; 8.31 V as drawn, above a 9.00 V plug's operating point) and the front end stops; the bank
  bleeds in 0.455 to 1.494 s (L4-E8).
- **Source-only and dead-pack operation (the fix round, B4; U-04).** What SLUSE66A establishes: after VBUS qualification
  "Converter powers up" (9.3.1) with no battery condition, and its power-up figures are drawn "2-cell without battery"
  (Figures 10-4, 10-5); DPM gives the system priority and past the input's limit "the system voltage starts to drop" (9.3.17);
  below VSYS_MIN the charge is clamped at 384 mA (9.6.2.1). Board A straps CELL_BATPRESZ for 4S, so U3 never sees "battery
  removal": with the pack absent it holds VBAT at ChargeVoltage (at most 16.884 V; INFERRED), and with the pack's discharge FET
  open at CUV it charges through that FET's body diode at the clamp, VBAT near the pack's 10 V (INFERRED). **The source
  envelope with no usable pack**, at VBAT: 9 V 19.9 to 36.6 W, 12 V up to 47.4 W, 24 V up to 90.6 W, against PS-IDLE-SPEC's
  42.8 W; so at 9 V the kit cannot run its profile on the source alone, and at 12 and 24 V the line's maximum is above it (no
  minimum is printed there: CONDITIONAL). Before the host writes IIN_HOST the input limit gives about 1.6 to 1.7 A at the 20 V
  bus, about 31 W into VSYS (`CHARGER-STATE-SEQUENCE.md`, INFERRED); FW-C01's order puts the charger before any slot, which no
  record measures. **Not resolvable from the held documents:** whether the converter keeps VSYS up with charge inhibited and no
  battery FET (Q-TI-3), whether the gauge lets a pack at CUV take charge with no precharge FET, and whether every load converter
  runs at the dead pack's VBAT (A-14). It is U-04 (section 7b), not later testing; R-85 is its verification at 12 and 24 V and
  does not settle it alone. Board E's always-on comes up on CELL_F from VBAT. **L4-E11 (accepted) answers it as far as the held
  documents allow:** arrangement (A), the drawn charger with rules R-a to R-d (the holds as a state table with S4's exception,
  R-b's two charge settings, the shedding sequence, the image's pre-charge); at a 9.00 V plug the shed warm-up (28.12 W at the
  plan figure) is carried with 0.98 W in hand while P1 stays at most 20.51 W; REQ-015 at 9.00 V at the plug is a CONDITIONAL
  CANDIDATE on E11-05, E11-06, E11-09, E11-22 and E11-23 (section 7b).

## 5. Faults, traced across the stages (out 7, out 11)

| Fault | What acts, stage by stage | Bound, and its class |
|---|---|---|
| **Source short**, the vehicle lead shorted while the tracker holds the bus | U3/Q1 blocks the reverse current at DC_F; DC_P stays back-fed from VIN_RAW | Q1 stands off DC_P, at most 30.15 V (INFERRED) |
| **Source short**, the panel lead | U4/Q2 blocks VIN_RAW into TRK_OUT; U5's input falls through its UVLO; SWEN off by default | INFERRED (L4-E7R) |
| **Output short**, VBUS20 | R12 holds the front end's output at 4.57 A at 9 V, R11 at 7.262 A above 14 V; VIN_RAW carries at most 11.65 A; the vehicle entry's breaker opens on overcurrent (6.364 to 7.136 A) after 0.247 to 0.49 ms, or on its filtered short-circuit sense (10.36 to 13.87 A), and retries every 0.5 s (the drawn LM5069 limited at 4.85 to 6.15 A for 3.13 to 8.16 ms); the panel's stage regulates at 2.9318 A at most and its backstop trips at 3.7408 A at most, inside 1.087 ms after the INB filter's held charge; U34 cycles the front end | L1 at most 12.60 A, FETs at most 130 C on the assumed 50 C/W (CONDITIONAL, C-3, C-5) |
| **Output short**, behind the vehicle entry (E11-19) | the selected breaker (TPS48110-Q1): at the start, a resistive fault (0.1 to 1000 Ohm) ends on the short-circuit trip with Q7 at 0.704 of its derated chart (1.21 Ohm, 0.954 ms), a hard short at 73.4 A after 9.04 us (0.743 of the derated 100 us line); in service the current rises at VIN / L until the filtered sense (2.74 to 3.31 us) and PD (5 us) turn Q7 off, then a retry every 0.5 s. The LM5069's power-limit pulse, its 5 mV floor and its fault time (D-07, D-09) exist only for the LM5069 alternative | the starts inside Q7's derated chart (CONDITIONAL on the derating and the transconductance bound, E11-17); the hard short in service inside Q7's derated 178.2 A only with the loop's inductance at least 2.08 uH: OPEN (E11-20, R-134); F1's I2t at most 6.7311 A2s, 7.24 % of its typical melting I2t |
| **Output short**, VBAT | the gauge's SCD (60 A in 0.2 ms), OCD2, the 25 A blades, F2, against 240 to 480 A prospective; U3 at its input limit | MAKER thresholds (pcb_pack_protection.yaml) |
| **Output short**, an outlet | USB-C: U18's OCP at 3.793 to 4.576 A in 15 us, U19's own limit; PoE: U16 leaves boost and its buck valley limit holds the input under the boost bound, board B's port limit; PA: U13's loop; monitor and heater: their eFuses | CONDITIONAL (VI(TRIP)'s row, bench (a)); U17 reads the PoE fault inside its full scale (INFERRED) |
| **Reverse**, the vehicle input at -36 V (REQ-015) | D10 (two-way, 44.4 V breakdown) does not conduct; U3/Q1 block; DC_P back-fed from the raised ceiling through Q7's body diode | **Q1 at 66.15 V: NOT MET on the drawn 60 V part, MEETS on the CSD19532Q5B (100 V)**; the LM74700-Q1 under its 70 V recommended, 75 V absolute, its ANODE at -36 V against -65 V (INFERRED, MAKER) |
| **Reverse**, the panel | D4 forward at the panel's short circuit (DECISION-31 E-N1) | recorded by DECISION-31; F2 above the panel's 6.802 A |
| **Disturbance**, TEST-PLAN M2 (CS101), M3 (CS114), M7 (decision 34's 8 kV contact and 15 kV air); no surge level is ruled (D-16, CHO-003) | Vehicle entry: CS101's 2.83 V peak at 36 V reaches 38.83 V, past the drawn OVLO minimum, under the selected entry's OV minimum 39.6 V (D-02; the alternative's 39.71 V); CS114 holds DC_F to 3.17 V; E-F1's 1 uF holds a negative discharge to 2.25 V. Solar entry: CS101 keeps the input at 27.82 V under D4's 28 V; U5's differential at most 0.2094 V against 0.3 V; the backstop's filtered ripple 0.0585 A against its 0.1130 A margin (D-01, resolved in design) | INFERRED (part A), MODELED (L4-E7R, CONDITIONAL on the loop's typical rows); A-N1 a recorded residual |
| **Capability scenario**, D10 at its rated pulse (not a requirement) | negative: Q1 at 100.5 V with DC_P at 36 V, avalanche energy at most 83.6 mJ against EAS 274 mJ; the LM74700-Q1's 75 V passed once DC_P exceeds 10.5 V | NOT MET, outside every requirement (D-16; DECISION-31) |
| **A short behind F1, a stiff source** (it needs a prior short of D10, D1, E-F1's capacitor or C4) | F1 alone clears it, at up to the 43.18 V basis (the selected OV maximum 41.22 V); with the selected interconnect at most 900 A (its specified loop floor, 56.93 mOhm at 20 C; the construction 871 A; the drawn cable 569.8 A) | the 0997010.WXN: 58 V DC, 1000 A at 58 V DC: MEETS (MAKER), CONDITIONAL on the four-wire acceptance (R-130); the drawn 297 MINI's 32 V: NOT MET as drawn; the conductors' short-time capability against F1's clearing I2t at 900 A CONDITIONAL (R-113, R-115); Q1 in the path is not shown to hold it and is not a conductor or connector of REQ-045 (no exemption claimed) |
| **A short behind F1, a weak source** (under ECSS 6.17.3c's 30 A) | F1's long-time band: 10 to 11 A with no opening, 13.5 A up to 600 s, 20 A up to 5 s | D-06 resolved in design (L4-E11): every element of the interconnect at least 20 A continuous where installed, 35 A for 5 s, 60 A for 0.5 s; CONDITIONAL on the makers' installed and short-time ratings (R-113, R-129 to R-132); the drawn VH, size 16 contacts and cable stay NOT MET as drawn |
| **Pack fault**, the charge FET opening mid-charge (a designed event, REQ-046) | U3's voltage loop holds VBAT at 16.884 V at most; BATOVP stops switching at 17.64 V, SYSOVP at 20.0 V; L2's 0.1341 mJ goes into VBAT's 34 capacitors (248.2 uF nominal) | 20.135 V at a fifth of the nominal capacitance (ASSUMPTION), under the TPS2596's 21 V and U17's 36 V |
| **Pack fault**, the discharge FET opening under load | on battery the kit stops (the hot stop REQ-077 acts first on temperature); with a source U3 carries up to 84.5 to 99.6 W | as section 3 |
| **Pack fault**, a cell or the block | BQ7720700's second level drives F2 (the chemical fuse); F1 25 A; under U-01's approach (II) U2 becomes the BQ7720704 (R-105) | MAKER thresholds |
| **Controller fault**, the host crashed | U3's watchdog falls back to 256 mA after 175 s (FW-A03); the H3 line is hardware and needs no host; the gauge's HWD stops charging in 10 s (FW-E01); the solar backstop is hardware on SWEN | the source bound holds with no firmware |
| **Controller fault**, U2 (Q2 short, FB open) | VBUS20 follows VIN_RAW; U3's 32 V passed; no clamp on VBUS20 | a single fault with no exemption claimed: S-111's options, R-48's engineering decision (open) |
| **Controller fault**, U5 (the LT8705A) | the backstop on SWEN acts while the regulation fails; L4-E7R lists the single faults that defeat the backstop or stop charging | Layer 8's fault analysis (R-100): no single fault both defeats the backstop and removes U5's own limit |

## 6. Decisions this record takes (SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026 that engineering decisions are the session's)

1. **Q1 to the CSD19532Q5B (100 V, C473333)**, on Q7's PPAK land. *Why:* L4-E5's raised ceiling makes the reversed vehicle input
   of REQ-015's acceptance put 66.15 V across Q1 (the back-feed diode's drop taken as zero), over the BSC039N06NS's 60 V. Round 2
   checked it on TI's sheet (`L4E9-ENTRY-PROPOSALS.md` section 1): its junction at most 80.2 C at 6.15 A in 62.1 C air, the
   controller's pins inside their ratings in reverse, the gate drive inside +-20 V, the hot swap's faults inside Q7's SOA. TI
   recommends parts to 60 V with the LM74700-Q1 and a Vth to 2.5 V; the 100 V part departs from both, deliberately (the reason is
   the controller's own pins, checked), and the drawn part misses the Vth recommendation too (bench R-112). *Draft:*
   `apply_gen_sch_e_q1.py`. *Reversed by:* a measured back-feed that keeps DC_P under 24 V, or a blocking element on the path.
2. **U17 on R227, 5 mOhm, in the PoE stage's input** (HF-F02). *Why:* the INA226's inputs are 40 V absolute and the rail is 54 V.
   Round 1 specified 20 mOhm; round 2 found the stage's input at its fault bound (U16's boost peak limit over R72) is 14.33 A,
   which 20 mOhm would read past full scale and dissipate 4.1 W in, so 5 mOhm (the part L4-E4 chose for R138): 72.38 mV at that
   bound, 1.037 W against 3 W. U16's VIN and BIAS move to POE_VIN with it. *Draft:* `apply_gen_sch_a_u17.py`. *Reversed by:* a
   low-side shunt in the rail's return or a monitor with a maker's rating at 54 V.
3. **F1 to the Littelfuse 0997010.WXN** (E-F2): MINI, 58 V DC, 1000 A at 58 V DC, the same blade size and pitch, in the 3568
   holder that names the 997 series. *Why:* the drawn 297 MINI is rated 32 V DC; the selected OVLO maximum is 43.18 V and the
   kit's cable gives at most 569.8 A at -20 C from a stiff source; the 0997's 80 C derating column (7.3 A) is over the entry's
   6.15 A. *Draft:* `apply_gen_sch_e_f1.py`; the BOM, the label and ASSEMBLY.md name the 0997 (the 3568 also takes a 32 V MINI).
   *Reversed by:* a cable or source impedance the requirement states, or a holder change.
4. **The vehicle entry's OVLO moved: R22 100k and R23 6.42k, both 0.1 %** (D-02, new). *Why:* with a 36 V source CS101's peak
   takes DC_P to 38.83 V, past the drawn 37.78 V minimum, so the hot swap may open under M2; the new band, 39.71 / 41.44 / 43.18 V,
   clears it by 0.88 V and stays 1.22 V under D10's 44.4 V breakdown minimum at 25 C. Running M2 at the source's nominal instead
   was not taken: a test condition is not changed to fit the design. *Draft:* `apply_gen_sch_e_hotswap.py` (R-94, with R24). *Reversed by:* a measured OVLO
   threshold spread that leaves the band outside that window, or TEST-PLAN stating an M2 source voltage at which the drawn band clears the peak.
5. **B-3 at R11 8 mOhm needs no declaration raised on board A** (R-10), as round 1.
6. **The 9 V envelope is stated, not corrected** (section 3), as round 1.
8. **R24 22k 1 %** (D-07, the fix round's B1). *Why:* the drawn 20k gives the power limit 4.7429 mV of sense at the selected
   OVLO maximum, under the 5 mV TI does not recommend; 22k is the next standard value over Equation 9's 21443 Ohm at its low
   corner (5.06 mV), and the power-limit part of the hot short with TI's 1.3 margin fits Figure 10 at 43.18 V derated to Q7's
   94.3 C case at the fault time's stacked maximum. The breaker's event and the timer's components stay open (R-118, R-119), and
   C5 is not changed this round: the 150 nF C0G option of D-09 needs a part read.
   *Draft:* `apply_gen_sch_e_hotswap.py` (with D-02's R22 and R23). *Reversed by:* a measured limit (R-118) or a part whose PWRLIM
   rows cover this setting. **Update round:** superseded for the selected entry, which has no power limit (L4-E11's TPS48110-Q1);
   the draft stays the base L4-E11's entry draft applies on (R-94, R-123) and R24 22k stands only for the LM5069 alternative.
9. **D-06 left open in round 2, resolved in design by L4-E11 (update round):** an interconnect rated to F1's 20 A point with
   its loop specified by resistance (at least 56.93 mOhm at 20 C, so a stiff source stays at 900 A against F1's 1000 A), size 12
   contacts, an XT60-class J_DCIN and a 20 A holder; its evidence items E11-10 to E11-16 carry its CONDITIONAL parts (R-113,
   R-115, R-129 to R-132); no exemption is claimed.
10. **U-04 added, R227's capacitors kept behind it:** source-only operation is an architecture question the held documents do
   not settle (B4); C81, C82 and the bypass capacitors close U16's input loop, and the transient bounds hold with them behind R227
   (B3).
11. **L4-E8's ballast loss is counted once:** on the charge path in the energy budget and as heat in the thermal budget, never
   again once a measured efficiency includes it (L4-E8's own rule); L4-E12's figures (27.086 W and 21.587 W) already hold them.
12. **E11-19 judged on L4-E11's fault scan and charts, not recomputed** (update round). *Why:* they are the accepted readings of
   the selected parts. This record adds only what rests on its own figures: the inductance bound reproduced (2.084 uH against
   L4-E11's 2.08 uH), the derating's carry-over to the CSD19536KTT (its case under 108.19 C, a junction-to-air resistance under
   145.2 C/W at its 0.22 W), and the start's I2t through F1 as rectangles (the largest 6.7311 A2s, 7.24 % of the typical 93 A2s).
   *Reversed by:* a measured start or peak (E11-17, E11-20).
13. **No new material defect from E11-19.** *Why:* the hard short in service is unbounded only for want of the loop's inductance,
   with no figure showing the peak passes Q7's derated 178.2 A, so it is OPEN evidence with a bounded investigation (E11-20,
   R-134). *Reversed by:* a held inductance under 2.08 uH or a measured peak over 178 A: then a defect whose alternatives (a
   series inductance, a faster trip, a Q7 with a larger IDM) all keep the topology.
14. **The LM5069's findings kept as the alternative, not deleted.** *Why:* L4-E11's entry draft and its timer draft refuse each
   other, so which applies is the generator owner's step in the release order (R-123); D-07, D-09 and R-119 stand if the LM5069 is
   kept, and their rows are printed as "the alternative".
15. **The register deduplicated item by item.** *Why:* one item, one owner, one acceptance: where an L4-E11 item repeats one of
   this record's rows (R-03, R-43, R-49, R-85, R-95, R-113, R-114, R-115, R-118) the row is restated with L4-E11's acceptance
   and names the item; the rest are new rows (R-123 to R-137, R-147); L4-E10's and L4-E12's rows map by owner (out 10).
16. **The 43.18 V basis kept** for the voltage and prospective-current checks although the selected OV maximum is 41.22 V.
   *Why:* L4-E11 keeps it (conservative, over REQ-015's 40 V test) and the LM5069 alternative needs it.

## 7. The closure gate

The gate's rule, held by the script (out 9) and by `test_l4e9.py`: a criterion reads PASS only on interface rows that read
MEETS, never on an ASSUMPTION, CONDITIONAL or PENDING row; never while an unresolved choice it names stands; and criterion 2
never while a material defect is open. Every feasibility claim below cites its evidence by class; the software tests establish
tested behaviour of the record's own scripts and drafts only, never an electrical or thermal property.

| Criterion | Evidence | Verdict | The exact constraint (if not PASS) | Could it overturn the architecture? |
|---|---|---|---|---|
| 1. One architecture selected; its mandatory functions have a defensible feasibility basis | A1 under D-06 (section 1); rows IF-02, IF-04, IF-05, IF-07, IF-09, IF-10, IF-11, IF-12, IF-13: REQ-014 (the pack), REQ-015 (IF-04 to IF-06, MAKER and INFERRED; at 9.00 V at the plug with no usable pack U-04's CONDITIONAL CANDIDATE), REQ-016 (IF-01, IF-02, CONDITIONAL and MODELED), REQ-017 (IF-12, IF-13), REQ-018 (IF-10, IF-14), REQ-045 (section 5, D-06 resolved in design), REQ-046 and REQ-077 (IF-10, L4-E10), REQ-075 (IF-09); the electronics at the margins (IF-11, L4-E12); choices U-01 to U-04 | CONDITIONAL | the solar function's 100 W bound is CONDITIONAL on G_CM and U18's VIN+ bias (L4-E7R) and its source on O-1 (U-03); REQ-015 at 9.00 V at the plug is a CONDITIONAL CANDIDATE on E11-05, E11-06, E11-09, E11-22 and E11-23 (U-04); the electronics at the margins are CONDITIONAL on T-H1 at or over 2.159 W/K and L4-E12's conditions (U-02); the battery path's thermal design is FEA-008's (U-01); PS-ALLTX's chain at 18 A for 60 s (PWR-F12) is an open obligation | possibly, on named evidence only: U-01 on the HL18650V's specification (D-06's pack energy and protection settings), U-02 on T-H1's reading and the fans (the sealed case's thermal design or a device-set re-pick), U-04 on TI's N1 and the bench's VSYS (the charger's power path); the rest resolves by a value, a part or a measurement on the same topology |
| 2. Material power-path defects have engineering resolutions and bounded supporting calculations | rows IF-01, IF-02, IF-04, IF-05, IF-13; defects D-01 to D-09 below (none open: D-06 resolved in design by L4-E11, D-07 and D-09 superseded by the replacement of the LM5069, the rest drafted or bounded with their conditions named); E11-19 in out 12a | CONDITIONAL | no material defect is open: D-01 to D-05 and D-08 are resolved in design (drafted or bounded), D-06 is resolved in design by L4-E11's interconnect with its evidence items (E11-10 to E11-16), D-07 and D-09 are superseded by the replacement of the LM5069 (E11-19 finds no new one); the resolutions rest on CONDITIONAL rows (the loop's typical rows, the makers' installed and short-time ratings, R227's pulse rating, the start into a hard short's transconductance bound) and the hot short in service on open evidence (the loop's inductance, E11-20) | no: each resolves by a part, a rating or a measurement at the vehicle or the solar entry |
| 3. Remaining assumptions are explicit, with their impact and verification method | section 8's register A-01 to A-29 | PASS |  |  |
| 4. Downstream implementation changes, layout constraints and tests have named owners and acceptance criteria | `DOWNSTREAM-REGISTER.md`: 137 items, each with one owner and an acceptance, among them L4-E11's E11-01 to E11-23 (deduplicated), L4-E10's and L4-E12's items, L10's own assignment (R-120, R-121) and M2 (R-122); the release order (L4-E6's R12 before L4-E8's ballasts; L4-E11's entry draft after this record's hot-swap draft); `LAYER5-HANDOVER.md` LH-01 to LH-11 | PASS |  |  |
| 5. No unresolved uncertainty could overturn the selected architecture while described merely as routine later testing | rows IF-01, IF-09, IF-10, IF-11; choices U-01 to U-04 below, each with its constraint, the evidence that settles it, its alternatives and what it could overturn | CONDITIONAL | four unresolved choices could overturn it and are named as such, not as later testing: U-01 (FEA-008's cell; the owner's two items), U-02 (MESHSAT-1478; CONDITIONAL on T-H1 at or over 2.159 W/K and L4-E12's conditions, CFL-002 the owner's question), U-03 (O-1, pending L4-E13), U-04 (a CONDITIONAL CANDIDATE with the evidence that closes it); an owner and an acceptance criterion do not close them | yes, on named evidence only: U-01 (D-06's pack energy and settings), U-02 (the sealed case's thermal design, the fans, the device set), U-04 (the charger's power path); U-03 decides the solar source, not the topology |

**Layer 4's power architecture closes: NO** (criteria 1, 2 and 5). Two categories, kept apart below: the material defects (7a,
none open since the update round) and the unresolved choices that could overturn the architecture (7b, four); the downstream
tasks (7c) and the owner's items (7d) are neither.

### 7a. The material power-path defects (criterion 2)

| Defect | What | The constraint | The options | State |
|---|---|---|---|---|
| D-01 | the solar backstop trips under TEST-PLAN M2 (CS101) | CS101's injected current crossed the sense bank and its peaks over the trip less the operating current stopped the stage for td each time, so solar charging stopped for the test, against M2's 'no upset' line (L4-E7R's check 3) | the bulk moved ahead of the sense bank, five 100 nF C0G across R66 (3.960 to 4.496 ms), R66 8.45k and RIMON_IN 31.6k: the filtered ripple at most 0.0585 A against the 0.1130 A margin, the response allowance 1.087 ms after the filter's 0.4205 J; CONDITIONAL on the loop's typical rows (break-even 2.51 times), the bulk's temperature, the bank's pulse capability, the 0.1 s window | RESOLVED (drafted): L4-E7R accepted (check 4, fnd/l4e7 91e9a4b5, figures at 675b8068); register R-21 and R-98, apply_gen_sch_e_backstop.py; M2, R-122 |
| D-02 | the vehicle entry's over-voltage lockout opens under TEST-PLAN M2 (CS101) at REQ-015's 36 V | 36 V plus CS101's 2.83 V peak reaches 38.83 V, past the drawn OVLO minimum 37.78 V | the selected entry's OV (TPS48110-Q1, R22 332k over R23 10.0k at 0.1 %): off above 39.6 / 40.36 / 41.22 V, 0.77 V over the peak and 3.18 V under D10's breakdown minimum (L4-E11, selected); for the LM5069 alternative R22 100k and R23 6.42k at 0.1 %: 39.71 / 41.44 / 43.18 V; M2 at the source's nominal (not taken) | RESOLVED (drafted): apply_gen_sch_e_entry.py (E11-01, R-123) after apply_gen_sch_e_hotswap.py (R-94) |
| D-03 | Q1 over its rating on a reversed input with the raised ceiling | 66.15 V across the drawn 60 V BSC039N06NS | the CSD19532Q5B (100 V) | RESOLVED (drafted): register R-17, apply_gen_sch_e_q1.py |
| D-04 | F1 cannot interrupt at the entry's highest steady input | the drawn 32 V DC MINI against 43.18 V | the Littelfuse 0997010.WXN (58 V DC, 1000 A at 58 V DC), in a holder rated at least 20 A (E11-13) | RESOLVED (drafted): register R-18 and R-132, apply_gen_sch_e_f1.py |
| D-05 | U17 on the 54 V rail (HF-F02) | 54 V on the INA226's IN+ and IN- against its 40 V absolute | U17 on R227, 5 mOhm in the PoE stage's input | RESOLVED (drafted): register R-06, apply_gen_sch_a_u17.py |
| D-06 | the vehicle entry's interconnect in F1's long-time band from a weak source | a source under 30 A (ECSS 6.17.3c's three times) can leave 10 to 11 A flowing indefinitely, 13.5 A for up to 600 s and 20 A for up to 5 s through J_DCIN's VH contact (10 A), the D38999 size 16 contacts (13 A test current) and the kit's cable and lead, whose held sheets print no current or time-current rating | L4-E11's option (i), selected: every element at least 20 A continuous where installed, 35 A for 5 s, 60 A for 0.5 s and F1's total clearing I2t at 900 A; size 12 contacts (insert 17-6), J_DCIN an XT60-class connector, a holder rated at least 20 A, AWG 14 cores, the loop specified by its resistance (at least 56.93 mOhm at 20 C, accepted four-wire at 58.51 to 64.21 mOhm) so a stiff source stays at 900 A against F1's 1000 A; (ii) a smaller fuse rejected (it fails 9 V); (iii) the source's capability in REQ-015 not needed | RESOLVED (in design): L4-E11 (accepted, check a15ab384), CONDITIONAL on its evidence items E11-10 to E11-16 (R-129 to R-132, R-43, R-95, R-113, R-115) |
| D-07 | the hot swap's power limit under the sense voltage TI recommends | R24 20k gives 4.7429 mV at 43.18 V, under SNVS452G's 5 mV, and the hot-short pulse was compared at 36 V with a by-eye reading | the selected entry limits no power (E11-19, out 12): its starts sit inside Q7's derated chart (0.704 into a resistive fault, 0.743 into a hard short); for the alternative R24 22k 1 %: 5.06 mV at its low corner | SUPERSEDED (the LM5069 alternative only): superseded by E11-01's entry (R-123); R-94's R24 stands only if the LM5069 is kept |
| D-08 | R227's transients bypass U16's current control | the capacitors behind R227 (20.2 uF) charge outside U16's cycle limit, so 72.38 mV did not bound every transient | bounded in part A: the differential at most the VBAT step, POE_VIN under 40 V in every required event, a saturated sample distinguished from damage; R227's pulse energy 2.879 mJ nominal, the maximum unresolved until a capacitance envelope and the pulse's shape meet Milliohm's rating; moving the capacitors ahead of R227 not taken (they close U16's input loop) | RESOLVED (bounded, conditions named): IF-13's checks; R-101 (Milliohm's pulse rating), R-117 (the loop's inductance), R-120 and R-121 (L10) |
| D-09 | the hot swap's fault time against the start into VIN_RAW | with C5 (100 nF, K, X7R) at its printed rows stacked the fault time's minimum is 2.035 ms, under TI's half-again margin over the start into VIN_RAW at 43.18 V (3.814 ms; the start alone 2.542 ms at the corners, 1.324 ms nominal), the front end's own load during the start not included | the replacement has no fault timer against a power limit (its start 0.382 to 1.219 A for at most 2.5 ms); with the LM5069 kept, L4-E11's C5 GRM3195C1H104GA05 with C121 GRM3195C1H683JA05 (apply_gen_sch_e_timer.py): 4.927 to 14.653 ms against 4.593 ms on a recomputed 3.062 ms start (34 uF) | SUPERSEDED (the LM5069 alternative only): superseded by E11-01's entry (R-123); R-119 only if the LM5069 is kept |

**E11-19 adds no material defect** (out 12a, decision 13). What it leaves open is evidence, not a defect: the loop's inductance
for a hard short in service (E11-20, R-134), the transconductance bound of a start into a hard short (A11-10, E11-17), and the
input current's transients against the breaker's 0.247 ms (E11-06, E11-21).

### 7b. The unresolved choices that could overturn the architecture (no owner closes them)

| Choice | What | The exact constraint | The evidence that settles it | The alternatives | The owner's items | What it could overturn |
|---|---|---|---|---|---|---|
| U-01 | FEA-008: the battery path's cell and thermal design (L4-E10, final) | LO-01d to LO-01g (E3-O, E5, E3-S, E4-S with the pack fitted) have no route that holds on held evidence; LO-01a holds only with T-H1 at least 1.666 W/K in both lid states (1.8058 W/K with L4-E8's ballasts counted, L4-E12) | the HL18650V's signed specification confirming storage at +71 C and -33 C at the stored charge and the +80 C idle limit, then L4-E10's margins re-run (1.06 K under H1 and 0.97 K under U2's INFERRED trip at LO-01e); T-H1 measured in both lid states | (II) a wide-temperature 18650 in D-06's 4S3P (recommended, CONDITIONAL); (I) the 35E with powered cooling (INCONCLUSIVE: up to 35 W into the sealed case); (III) latent storage and a primary-fed heater (rejected at LO-01d to f; added energy storage under D-06); a requirement change (the owner's, D-29) | (1) send the drafted request for the specification; (2) once it confirms, approve the cell change (D-06's about 145 Wh to about 121 Wh nominal, REQ-046 and REQ-077 restated with the cell, about USD 42 a pack); if declined, LO-01d to g stay a release gate (OW-2, OW-3) | on the specification's answer: D-06's pack energy (16.4 % less usable) and the pack's protection settings under (II); with a negative answer and no requirement change LO-01d to g keep no route on held evidence, and (I)'s powered cooling (up to 35 W into the sealed case) would reopen U-02's heat budget; the power path's topology stays |
| U-02 | MESHSAT-1478: the electronics against the inside air at D-02a's +55 C margin and E5's +60 C dwell (L4-E12) | L4-E12's route (c), E3-O as stated and the hold in E5 only, is CONDITIONAL on T-H1 lid open with the fans at or over 2.159 W/K (E3-O alone 1.806 W/K; 2.709 W/K with no hold), the hold's reference within +-0.899099 K of the mixed air, the parts out of the cooler's exhaust, the fans' rating (D-18), the pushbuttons and two regulators changed and PDi's statement; at the line E3-O's air is 67.55 C and E5's 70.00 C, while the design as it stands (LO-01a's floor, no hold) reaches 76.25 C in E5; inside the envelope no location holds the SGP41 to its maker's conditions (CFL-002) | T-H1 measured in both lid states at or over 2.159 W/K with the picked fans; the forced hold and the SGP41's shutdown at room temperature; E3-O and E5 with thermocouples on the +70 C parts (R-104, R-109); PDi's and Sensirion's answers; the owner's answer to CFL-002 | (a) the enclosure alone at 2.709 W/K with no hold; (b) wider-rated parts (five are device-set parts, the owner's, CHO-001); the plate coupling if T-H1 reads between 1.806 and 2.159 W/K; a device-set re-pick or a stated deviation of E3-O's configuration (the owner's) | CFL-002, the SGP41 in the envelope: A (a BME688-class sensor in its place, L4-E12's recommendation), B (the VOC channel dropped) or C (the SGP41 kept, its channel reported as not covered); send PDi's and Sensirion's requests (OW-1, OW-4); later, only on T-H1's reading, a re-pick or a deviation | on T-H1's reading and the fans: under 2.159 W/K E5 fails for the +70 C class unless the plate coupling holds, under 1.806 W/K E3-O too, so the sealed case's thermal design (no vent, the ruling of 7 September 2026) or the device set (CHO-001) could change; a stopped fan takes the enclosure to its fans-off conductance; CFL-002 changes a sensor, not the architecture; never the power path's topology |
| U-03 | O-1: a solar panel with a supported maximum open circuit inside REQ-016's window | REQ-016 admits a panel only with an open circuit at or below 25 V at -20 C; the candidate's nominal sheet gives 24.05 V and no supported maximum (source compliance INCONCLUSIVE) | a panel maker's stated maximum, or a measured lot, at -20 C at or under 25 V | the SPR-E-Flex-100 with the maker's tolerance; another panel inside the window; REQ-016's window restated (the owner's) | none until a panel is pinned | which panel the mandatory solar function uses; the stage and the window stay |
| U-04 | source-only and dead-pack operation (L4-E11: arrangement (A), a CONDITIONAL CANDIDATE) | L4-E11 selects arrangement (A), the drawn charger with no battery FET, with rules R-a to R-d and the replaced entry: at a 9.00 V plug the source delivers 29.09 to 42.52 W at VBAT and the shed warm-up (28.12 W plan) is carried with 0.98 W in hand while P1 stays at most 20.51 W; REQ-015 at 9.00 V at the plug is a CONDITIONAL CANDIDATE, not closed: at the load's hi corner P1 (35.24 W) exceeds the source's least, TI states neither VSYS's regulation with no battery under load steps (N1) nor what it regulates with charge inhibited in state S2 (N2, Q-TI-3), the cells' warming time has no held model, and R-b's cases (ii) and (iii) are INCONCLUSIVE | E11-05 (TI's answers: N1, N2 for S2, Q-TI-2), E11-06 (R-85 extended: P1 at most 20.51 W, the front end at least 0.88021, the pin's band, the breaker never tripped, VSYS's step response), E11-09 (the knee drawn), E11-22 (R-b's cases), E11-23 (the warm-up time at the plug) | (B) a charger with a battery FET power path (it reopens L4-E4 to L4-E8's settings on a part whose sheet is not held); (C) a pre-charge path on board P (its resistor's heat in the sealed case); VSYS's capacitance first (E11-07); REQ-015's acceptance restated (the owner's; not needed while (A) stands) | none unless the evidence is negative and REQ-015 is restated; TI's questions are an outside contact the owner makes (REVIEW-REQUEST.md, Q-TI-3 restated as N2 with N1 added; OW-4) | on TI's N1 or the bench's VSYS under the kit's load steps with no battery: the charger's power path, VSYS's capacitance first (E11-07) and only then (B); on the efficiency, the pin's band or P1's load, the knee or F1, not the topology |

**Whether each can still overturn the architecture, and on exactly what:** U-01 yes, on the HL18650V's signed specification
(D-06's pack energy and protection settings; with a negative answer and no requirement change, powered cooling would reopen
U-02's heat budget); U-02 yes, on T-H1's reading against 2.159 W/K and on the fans' rating (the sealed case's thermal design or
the device set), while CFL-002 changes a sensor and not the architecture; U-03 not the topology, only which panel the solar
function uses (pending L4-E13, kept as it stood); U-04 yes, only on TI's N1 or the bench's VSYS with no battery under load
steps (the charger's power path, VSYS's capacitance first), while the efficiency, the pin's band or P1's load move the knee or
F1 and not the topology.

### 7c. The downstream implementation and verification tasks (criterion 4)

`DOWNSTREAM-REGISTER.md` (section 9): an owner and an acceptance criterion close the ASSIGNMENT, not the item. The items that
exist only under a choice's outcome are marked there (Order "U-01"), and the items that carry a choice's evidence say so
("U-02"); none stands in for a choice.

**What closure needs, exactly:** U-04 settled by E11-05 (TI's N1 and N2), E11-06 (R-85 extended), E11-09 (the knee drawn),
E11-22 (R-b's cases) and E11-23 (the warm-up time); U-02 settled by T-H1 at or over 2.159 W/K with the picked fans (R-104,
R-142), the forced hold and the SGP41's shutdown (R-138, R-139), the parts' readings in E3-O and E5 (R-109) and the owner's
answer to CFL-002; U-01 settled by its evidence and the owner's two items (or held open as a release gate); U-03 settled by a
panel (L4-E13); D-06's CONDITIONAL parts by the makers' ratings and F1's clearing I2t (R-113, R-115, R-129 to R-132) and the
four-wire loop (R-130); the hot short in service by the loop's inductance (R-134); and for criterion 1 the CONDITIONAL inputs
with their named evidence (G_CM and U18's VIN+ bias R-101, PWR-F12 R-46 and R-83, C-7, C-3, C-5, V-A07). The coordinator decides
whether a CONDITIONAL criterion with these named is acceptable for Layer 4's closure; this record does not.

### 7d. The owner's items (decisions and outside contacts only; the session contacts no outside party)

Kept apart from the engineering work above: each is a decision only the owner takes or a text only the owner sends. The
script reads each document at its pinned sha256 (out 9 (c)).

| Item | The decision or action | The document (path, where, sha256/16) |
|---|---|---|
| OW-1 | CFL-002 (U-02): the SGP41 in the battery bay against REQ-042's VOC channel inside the envelope: A, a BME688-class sensor in its place (L4-E12's recommendation); B, the VOC channel dropped; C, the SGP41 kept, its channel reported as not covered above a 49.0 C reading and after storage outside 5 to 30 C | L4-E12's page, section 8: `v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md`, at `a86be47b`, d6f501457675091c |
| OW-2 | U-01, item 1: send the drafted request for the HL18650V's signed product specification (Yichun Topwell Power) | the request: `v2/docs/records/l4e10/clarification/topwell-hl18650v.txt`, at `79b2f568`, 5e81a4a215bcc7e6 |
| OW-3 | U-01, item 2, once that specification confirms L4-E10's rows: approve the cell change inside D-06's 4S3P (about 145 Wh to about 121 Wh nominal, REQ-046 and REQ-077 restated with the cell, about USD 42 a pack); if declined, LO-01d to g stay a release gate | L4-E10's page, section 8: `v2/docs/records/l4e10/L4E10-CELL-THERMAL.md`, at `79b2f568`, e7d09066c77b6a84 |
| OW-4 | the outside-contact drafts to send (the owner chooses the channel) | Yichun Topwell Power: the HL18650V's signed specification (U-01): `v2/docs/records/l4e10/clarification/topwell-hl18650v.txt`, at `79b2f568`, 5e81a4a215bcc7e6; Pervasive Displays: the E2370KS0C1's storage and operation (U-02): `v2/docs/records/l4e12/clarification/pervasive-displays-e2370ks0c1.txt`, at `a86be47b`, 4f7db1348cc0b4ac; Sensirion: the SGP41's duration, recovery and storage (U-02, CFL-002): `v2/docs/records/l4e12/clarification/sensirion-sgp41.txt`, at `a86be47b`, 43c47549235fe6e8; Analog Devices: the LT8705A's IMON_IN limits (the 100 W bound; R-33, R-101): `v2/docs/records/l4e7/clarification/analog-devices-lt8705a.txt`, at `675b8068`, 97d8217092eae7ac; Milliohm: the HoJLR2512's temperature coefficient below +25 C (R-101): `v2/docs/records/l4e7/clarification/milliohm-hojlr2512.txt`, at `675b8068`, e920420419a677e0; Vishay: the WSL2512's pulse capability (R-101): `v2/docs/records/l4e7/clarification/vishay-wsl2512.txt`, at `675b8068`, 0d91a42dfa59432b; Texas Instruments: the INA169's error envelope (R-101): `v2/docs/records/l4e7/clarification/texas-instruments-ina169.txt`, at `675b8068`, 405fb3988f41d8ac; Texas Instruments: the battery packet's Q-TI-2 and Q-TI-3, with L4-E11's N1 and N2 for S2 added before sending (U-04; E11-05, R-114): `v2/docs/review-packets/battery/REVIEW-REQUEST.md`, in the tree, 91a257430cbeb53a; Eaton: the SCF9550 above +60 C and in storage (PWR-F12; R-103): `v2/docs/records/l4e10/clarification/eaton-scf9550.txt`, at `79b2f568`, 9dffb95e8b4874fc |
| OW-5 | the fallbacks, to send only if T-H1 reads under 2.159 W/K (L4-E12) | Ground Control: the RockBLOCK 9704: `v2/docs/records/l4e12/clarification/ground-control-rockblock-9704.txt`, at `a86be47b`, 738245875bec70c5; NiceRF: the SA868: `v2/docs/records/l4e12/clarification/nicerf-sa868.txt`, at `a86be47b`, 92324668c17d4f6c; Bulgin: the PXP4043C: `v2/docs/records/l4e12/clarification/bulgin-pxp4043c.txt`, at `a86be47b`, c7accd3dd6dc1d89 |


Not yet drafted (engineering work first, then the owner sends): Littelfuse, F1's total clearing I2t at 900 A and 58 V DC
(R-115, E11-16); Coilcraft, L10's inductance against current at temperature (R-120) and L1's Isat at 85 C (R-31); Milliohm,
R227's single-pulse rating (R-101).

## 8. The assumptions register (criterion 3)

| ID | Assumption | Where it enters | Impact if wrong | Verification method |
|---|---|---|---|---|
| A-01 | The three efficiencies: stage 0.93, front end 0.93, pack charge 0.95 (C-8) | IF-02, IF-07, every energy figure | moves the gap, not a verdict (A2 +131.4 to +344.0 Wh at 48 h); the 9 V envelope needs the front end at least 0.897 | R-72, measured at bring-up |
| A-02 | U3's input-current minimum: the setting less an INFERRED 0.1 A (C-7) | IF-09 | U3's 4.537 A covers the window's 4.517 A by 0.020 A; a lower minimum gives a little less in a 100 W hour | R-32 (TI), R-71 (bench) |
| A-03 | Board A's FET thermal resistance at the maker's 50 C/W (C-3) | IF-07 | Q2 at 130 C, 20 K under 150 C; a worse board raises it | R-42 (laid copper), R-63 (bench) |
| A-04 | L1's Isat at 85 C at least 14.00 A (C-5); L4-E8's restart ring at 16.13 A taken at constant inductance | IF-07, IF-08 | B-1 at temperature; a lower Isat needs R12 larger (a lower peak limit, against the 1.56 A service margin) or another L1; the ring's peak re-derived on the measured L(I) | R-31 (Coilcraft), R-65 (sweep through 16.2 A) |
| A-05 | The backstop's two assumptions carried past their meaning (L4-E7R, accepted): G_CM (break-even 168.8 %) and U18's VIN+ bias (break-even 22.0 mA); the IMON_IN loop's ripple on typical rows (break-even 2.51 times) | IF-01, IF-02 | the static bound 93.5521 W, margin 6.4479 W; the CS101 margin 0.1130 A over 0.0585 A; past them, the next stocked setting (L4-E7R's table) | R-101 (makers), R-99 (bench 7b.15 to 7b.17), R-122 (M2) |
| A-06 | H3's pin error at R16's 10 mOhm within +-0.2 A, and within 0.071 A in the 26.50 to 27.24 V band | IF-07 | R11 7 mOhm instead of 8 mOhm (R12, the bank and Cc2 unchanged) | R-75 (V-A07) |
| A-07 | The ILIM_HIZ network's tolerance +-0.5 % and the HIZ comparator's spread | IF-06, IF-09 | moves the knee's thresholds inside the guard's 0.156 V margin | R-03's drawn values, R-77 (V-A09) |
| A-08 | The cans' cold ESR envelope (300 mOhm at -40 C after endurance taken to -20 C), C190 and C191's regions, VIN and VBAT sampled | IF-08 | the 7 mOhm fallback's 0.005 A margin; the loop at the cold end | R-68 (7b.8), R-102 (C190 and C191) |
| A-09 | The cans' lifetime on their measured rise | IF-08 | service life, not the current bound | R-68 item 4 |
| A-10 | The back-feed diode's drop taken as zero (an upper bound on Q1's reverse stress) | IF-04 | none: a drop only lowers 66.15 V | R-80 |
| A-11 | The VH contacts at AWG 18 on the standard header (no stated rating) | IF-01, IF-04 | the contact margin at 6.15 and 6.802 A is unstated | R-29 (harness change) |
| A-12 | Copper at 0.01724 Ohm mm2/m and 0.00393 /K, 18 AWG at 0.823 mm2, the source's own resistance taken as zero | F1's prospective current (569.8 A at 43.18 V) | a lower prospective current, never higher | the part's selection (R-18) |
| A-13 | A fifth of VBAT's nominal capacitance kept under bias | the pack-open bound | none while 2.64 % of the nominal is kept | R-86 (VBAT's peak at a COV trip with the charger live) |
| A-14 | Every load converter runs to the 10.0 V stack (SHORTLIST.md 2) | IF-11, the usable energy | the usable energy and the battery-only hours | R-49 |
| A-15 | PS-IDLE-SPEC's 8.4 W with no document; the PA's drain current 5.4 to 8.2 A (F-PR-02) | IF-11, IF-14 | the profile's load and endurance; the PA rail's current | R-82, PWR-F15 and TEST-PLAN |
| A-16 | The candidate panel's nominal sheet values (source compliance INCONCLUSIVE, O-1), SC-37's mean day | IF-01, the endurance | the solar energy (344.0 / 336.6 / 307.9 Wh a day at L4-E7R's accepted regulation) | R-35, R-52 |
| A-17 | D10's breakdown temperature coefficient at its typical 0.1 %/K (no maximum printed) | IF-04, D-02 | the cold breakdown 42.4 V at -20 C; still above REQ-015's 40 V unless the coefficient is more than twice the typical | R-81 at the cold end |
| A-18 | Q1's RDS(on) normalised 1.95 at 150 C read by eye from Figure 8; Figure 10 now read from TI's vector drawing (no longer by eye; round 2's 3.0 A at 36 V withdrawn, 2.52 A); Q7's case at most 94.3 C, derived from the hottest inside air and RthetaJA on 1 in2 2 oz (board E's copper an ASSUMPTION) | IF-04, IF-05 (the LM5069 alternative) | Q1's junction (80.2 C) and Q7's hot-short margin (0.913 A against 0.675 A) | R-112, R-118 on the bench |
| A-19 | The OVLO's corners stacked: OVLOTH 2.4 to 2.6 V (MAKER) with R22 and R23 at 0.1 % | IF-04, D-02 (the LM5069 alternative) | D-02's 0.88 V and 1.22 V margins | R-81 (the OVLO trip recorded inside 39.71 to 43.18 V) |
| A-21 | The power limit's spread at R24 22k: TI's Equation 9 at the resistors' corners times TI's own 1.3 margin (SNVS452G 9.2.1.2.5); the PWRLIM rows are tested at 48 V and 150 kOhm only | IF-05 (the LM5069 alternative) | the hot-short pulse's 0.675 A against 0.777 A at the fault time's maximum | R-118 |
| A-23 | C5's printed rows stacked (K +-10 %, X7R +-15 % over temperature and +-15 % after endurance; DC bias not taken) for the fault time's envelope, and Figure 10 carried by TI's power law past its 10 ms line | IF-05, D-09 (the LM5069 alternative) | the fault time 2.035 to 11.871 ms; the start margin NOT MET at the corners; 0.777 A at the maximum | R-119 |
| A-22 | R227's loop inductance (no layout) and the undamped ideal step as the bound on POE_VIN's ringing | IF-13 | the capability pulse's 41.52 V in that limit; every required event under 40 V | R-117 |
| A-20 | L4-E10's conditioned corner (about 25 W of the kit's heat at E3-O, derived here from its 70.00 C and T-H1's floor) with L4-E8's 2.09 W added on the same conductance; replaced since the update round by L4-E12's model (A-29), which counts the ballasts once | IF-08, IF-11 (the design as it stands), U-02 | the inside air's +1.25 K, U-02's margin | R-104 (T-H1), R-111 |
| A-24 | TI's typical transconductance (329 S at 100 A) taken as the bound on a hard short's current rise at the start (L4-E11 A11-10) | IF-05 | the start into a hard short (73.4 A, 0.743 of the derated 100 us line) | E11-17 (R-118) |
| A-25 | Q7's chart derating carried from this record's 0.4454 (a 94.3 C case on a 150 C part) to the CSD19536KTT, every point of a fault pulse held against the chart for the whole pulse (L4-E11 A11-7) | IF-05 | the fault starts' 0.704 and 0.743; conservative while Q7's case stays under 108.19 C | E11-14 (R-43), E11-17 (R-118) |
| A-26 | The loop's inductance from the source to a fault on DC_HS or VIN_RAW: no held document gives it | IF-05 | a hard short in service passes Q7's derated 178.2 A below 2.08 uH | E11-20 (R-134) |
| A-27 | The interconnect specified by its measured loop (at least 56.93 mOhm at 20 C, read with 2 % and 2 K), copper's 0.00393 /K for the temperature only (L4-E11 A11-1) | IF-04, F1 | a loop under the floor passes more than 900 A | E11-11 (R-130) |
| A-28 | The front end at 0.93 at 8.1 V (L4-E5's figure, C-8; L4-E11 A11-9), the loss model's unprinted elements (A11-6) and the overcurrent delay's maximum (A11-11) | IF-05, IF-07 | the in-service maximum against the breaker's lowest (the efficiency floor 0.88021); the longest fault pulse | E11-06 (R-85), E11-17 (R-118) |
| A-29 | L4-E12's model: W4's lumped film coefficients, the plan heat (24.996 W into the case, 19.497 W under the hold), the hold's reference within +-0.899099 K, E5's 15 K/h with a 61 s lag | IF-11, U-02 | the binding line 2.159 W/K and the hold's window | R-104 (T-H1), R-109, R-139 |

## 9. The downstream register and the release order (criterion 4)

`DOWNSTREAM-REGISTER.md` holds 137 items, each with one owner, an acceptance, a state and a step in the release order (out 10):
Layer 4 coordinator 8, Layer 5 interfaces 4, Layer 6 components 17, Layer 7 mechanical 5, Layer 8 board A generator owner 12,
Layer 8 board B generator owner 1, Layer 8 board C generator owner 1, Layer 8 board E generator owner 20, Layer 8 board P
generator owner 1, Layer 9 pre-layout analysis 23, prototype bench 35, firmware owner 7, TEST-PLAN owner 2, CONOPS owner 1. By
kind: 51 implementation changes (24 drafted, 16 missing a draft, 11 owed as work, none PENDING), 13 layout constraints, 35
tests, 33 pieces of evidence, 5 release records. They are category (a): 137 items, each with one owner and an acceptance that
close the assignment, not the item, and none of them stands in for U-01 to U-04.

**Every draft of L4-E4 to L4-E8 is in it** (R-01, R-02, R-04, R-05, R-07, R-09, R-12, R-19, R-20, R-23), with d8dec31's E-F1
draft (R-16), L4-E7R's backstop draft (R-21), this record's four (Q1 R-17, F1 R-18, U17 R-06, the hot-swap settings R-94) and
L4-E11's two for the selected design (the entry R-123, the guard R-124; its timer draft only in R-119, for the LM5069
alternative). **The missing drafts:** U3's ILIM_HIZ network drawn to the corrected knee (R-03), R10, C26/C27 and TRK_OUT's
declaration (R-13 to R-15), the 45 mOhm lcsc line (R-08), board A's declaration texts (R-10), the 0997's energy chain and
derating entries (R-95, R-96), BANK-R1 on board B (R-107), the entry network's LCSC codes (R-116), the interconnect's parts
(R-129 to R-132) and U-02's board E and board C changes (R-144, R-145).

**The update round, deduplicated** (out 10 checks it): L4-E11's E11-01 to E11-23 are each named in a row's From column, as new
rows (R-123 to R-137) or restated ones (R-03, R-23, R-43, R-49, R-76, R-77, R-85, R-95, R-113, R-114, R-115, R-118); E11-19 is
answered here (out 12). L4-E10's rows map onto R-47 and R-103 to R-111; L4-E12's onto R-104, R-109, R-111 (restated as the
enclosure to T-H1's line) and the new R-138 to R-146; L4-E11's release record is R-147. The LM5069's own rows stay for the
alternative only (R-94 as the base the entry draft applies on, R-119).

**The release order** (the register's own section): release records first (L4-E4's names accepted checks of L4-E4 to L4-E6 and
L4-E8; L4-E7's names L4-E7R's check 4; L4-E11's its check 3), with the text drafts for Layer 5, CONOPS and L4-E5; the missing
drafts; board A in one round with **R12, the ILIM_HIZ network drawn to the corrected knee and U34's R14 first, R11 after them,
the ballasts and Cc2 after R12**, R138 independent, U17's R227 after them; board E in one round with **Q1 and E-F1's capacitor
no later than R10**, R10 and C26/C27 only with board A's H3 line, L4-E7's settings, L4-E7R's backstop, then F1, the hot-swap
settings and **L4-E11's entry on top of them**, F1's 20 A holder and U-02's board E changes; firmware's 4.70 A only on a board A
that carries H3, rules R-a to R-d, the hold and the SGP41's shutdown; the records re-issued; the bench, where V-A07 decides
R11; Layer 7's interconnect and enclosure before the harness and the case are built. The items under U-01's approach (II)
(R-105, R-106, R-110) wait on the owner's approval.

## 10. The endurance statement (out 8; DR-01)

- **Battery only, A1 (the ruled pack):** 107.9 Wh usable at +20 C and 44.5 Wh at -10 C (aged to 80 %): **2.52 h and 1.04 h**,
  short of 48 h by 45.5 h and of 72 h by 69.5 h.
- **Solar-assisted, A1, on the candidate panel** (SunPower SPR-E-Flex-100 on its nominal sheet, source compliance
  INCONCLUSIVE; SC-37's mean September day; the replay at L4-E7's 350.0 Wh a day): the first interruption at hour **6 or 2**
  (06 or 18 UTC starts); **1367.4 / 1368.1 Wh unserved at 48 h and 2103.9 / 2104.6 Wh at 72 h**; it would need
  **+1361.5 / +2094.1 Wh** more usable storage; the steady load it carries through either horizon is 8.0 W against the profile's
  42.8 W. On the 100 W screening stimulus (a conditional comparison): hour 13 or 2, +654.8 / +873.1 Wh.
- **At the selected solar control (L4-E7R, accepted):** the day's energy is 344.0 / 336.6 / 307.9 Wh on SC-37 (lower, nominal
  and upper hold corner) and 431.9 Wh on the bright day. The replay is not re-run here: at the nominal hold the unserved energy
  grows by at most 13.4 Wh a day, 26.8 Wh at 48 h and 40.2 Wh at 72 h (INFERRED: harvest lost can at most add to it); the sense
  bank's 0.5262 Wh a day is carried beside it (counted twice if the day's figure already holds it, the conservative side).
- **L4-E8's losses in the budgets, once:** the ballasts dissipate at most 2.09 W while U3 runs at the bound's worst corner
  (0.0093 W at nominal parts), a loss on the charge path only (battery-only endurance does not carry it), outside the DECLARED
  efficiencies (C-8) and dropped once a measured efficiency with the ballasts fitted includes it (R-51). As heat, at most 2.09 W
  more into the sealed case: 1.25 K on the inside air at T-H1's 1.666 W/K floor, on top of L4-E10's conditioned corner, and
  0.968 K at T-H1's binding line, inside L4-E12's figures (U-02).
- **The thermal budget at the margins (L4-E12, the update round):** T-H1's binding line is 2.159 W/K lid open with the fans,
  set by E5 under the hold (19.497 W plus the ballasts' 2.09 W, 21.587 W, over 10 K to the +70 C parts); E3-O with every radio on
  carries 27.086 W (24.996 W plus 2.09 W) over 15 K and needs 1.806 W/K; 2.709 W/K with no hold. At the line the mixed air is
  67.55 C in E3-O and 70.00 C in E5; the hold powers off board D, the PA rail, the RockBLOCK, the LoRa module, both E72 and the
  Geiger module, idles the running module and holds the charge, on a reference within +-0.899099 K of the mixed air.
- **The energy budget (the update round):** none of L4-E10 to L4-E12 moves the battery-only or solar figures above; the vehicle
  entry's loop costs 5.095 W at a 9.00 V plug (5.983 A through 142.34 mOhm hot), on the source's side; a dead pack's charge
  under R-b takes at most 21.22 W, and only from DPM's surplus; L4-E12's hold is a state at the margins (E5), not an endurance
  state.
- **Under U-01's recommended cell** (CONDITIONAL, not taken): usable 90.4 Wh against the 35E's 108.1 Wh (16.4 % less), 2.11 h
  against 2.52 h battery-only at PS-IDLE-SPEC (L4-E10's basis); D-06's about 145 Wh becomes about 121 Wh nominal, and every
  storage shortfall above grows by at most 17.7 Wh (INFERRED).
- **What else moves these figures:** H3 gives up at most 7.1 Wh a day on the candidate's trace; the three efficiencies (A-01).
  None changes a verdict.
- **The objective of 48 to 72 hours is unmet** by the selected architecture on every trace (DR-01). It is an objective (D-28),
  not a minimum, and it reopens no requirement.
- **What A2 would change, as a proposal for the owner** (it changes D-06; its mechanical fit and FEA-008's lid obligations stay
  open): battery only 12.71 h and 5.24 h; on the candidate panel the first interruption at hour 18 or 11 and +979.2 / +1719.7 Wh
  still needed; on the screening stimulus +278.8 / +515.8 Wh. A2 also misses 48 h.
- **Every mandatory function is intended to be delivered, subject to the open conditions named here** (the CONDITIONAL
  resolutions of D-01 and D-06, U-01 to U-04 and the CONDITIONAL rows): battery and solar both feed the kit; the store is inside the case; HF and the tablet are kept
  (the tablet's charge is optional and reduces endurance); the vehicle input runs the kit and charges the pack across 9 to 36 V
  with a working pack (section 3; without one, U-04); PS-ALLTX runs under D-11's floors; both outlets deliver their contracts
  within their protection. No service is reduced to narrow the gap. Software tests establish the record's own behaviour, not
  these properties.

## 11. What stays PENDING, CONDITIONAL or open

- **PENDING:** none in the rows. L4-E7R is accepted (check 4 at `91e9a4b5`); IF-01, IF-02, LH-02, R-21, R-92 and R-98 carry its
  figures. L4-E13 (U-03) is pending; U-03 stays as it stood.
- **Unresolved choices (no owner closes them):** U-01 (FEA-008's cell, with the owner's two items), U-02 (MESHSAT-1478,
  CONDITIONAL on T-H1 at or over 2.159 W/K and L4-E12's conditions; CFL-002 the owner's question), U-03 (O-1, pending L4-E13),
  U-04 (source-only and dead-pack operation, a CONDITIONAL CANDIDATE on E11-05, E11-06, E11-09, E11-22 and E11-23).
- **Open material defects:** none since the update round. D-06 is resolved in design by L4-E11, CONDITIONAL on its evidence
  items (E11-10 to E11-16); D-07 and D-09 are superseded by the replacement of the LM5069 and stand only for the LM5069
  alternative.
- **Open evidence (not defects):** the hot short in service against Q7's derated 178.2 A on the loop's inductance (E11-20,
  R-134); the start into a hard short on the transconductance bound (A11-10, E11-17); the input current's transients against
  the breaker's 0.247 ms (E11-06, E11-21).
- **CONDITIONAL:** the backstop's static bound on G_CM and U18's VIN+ bias, the 0.1 s interpretation (layer 8), C-7, C-3, C-5,
  V-A07, the bank's lifetime and cold envelope, PWR-F12, U18's trip row, D10's cold breakdown (a typical coefficient), the
  entry's in-service margin on the front end's efficiency at 8.1 V (0.88021, E11-06), the fault starts on Q7's derating
  (E11-14, E11-17), the interconnect's makers' ratings and F1's clearing I2t at 900 A (R-113, R-115, R-129 to R-132), the
  four-wire loop (R-130), R-b's case (i) and board P's copper (E11-22), R227's pulse rating and capacitance envelope (R-101),
  L10's L(I) at temperature (R-120, R-121), L4-E7R's loop on typical rows, the bulk's temperature under CS101 and the bank's
  pulse capability (R-122, R-101), and U-02's conditions (T-H1, the hold's reference, the fans, the parts out of the exhaust,
  the pushbuttons and regulators, PDi's statement, the 33 lines cleared only by an absolute rating).
- **Recorded residuals outside every requirement:** A-N1 (the VIN_RAW clamps' 64.5 V against U2's 60 V at their rated pulse; no
  surge level is ruled, D-16) and the capability scenario on Q1, the LM74700-Q1 and U17's POE_VIN (part A). S-111 (VBUS20's
  single faults) is an engineering decision still open (R-48), with no exemption claimed; the short at DC_P and the weak-source
  band behind F1 are traced in section 5 (F1's let-through R-115, D-06), not exempted.
- **Not claimed:** nothing is verified, built or measured; every row is a desk reading of documents and records.
