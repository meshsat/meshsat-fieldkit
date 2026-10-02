# L4-E9: the connected power architecture and Layer 4's closure gate for it (MESHSAT-1357, 1 October 2026; round 2, its fix rounds and the update rounds, 2 October 2026)

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
**L4-E13** (U-03, the panel) at `fnd/l4e13` `fae419d1`, accepted by the closing check 3 there, and its update after set 25 at
`33b6b7be` (check 4: A-3(a) and A-4 on L4-E7R's regulation and backstop, the nominal hold's day 336.6 Wh), read from the tree
after its merge into this line. Part A of round 2 (`L4E9-ENTRY-PROPOSALS.md`,
out 11) checks Q1, F1 and U17 against their makers' sheets. The fix round answered the collaborator's focused check
(`checks/astra-check-l4e9-1.md`, NOT YET) and the final round its targeted recheck (`checks/astra-check-l4e9-2.md`, NOT YET);
the coordinator's closing check (`checks/check-l4e9-3.md`) read the gate as not closed on D-06, D-09 and U-01 to U-04.
**The update round** (the coordinator's instruction of 2 October 2026, out 12) brings the architecture and its gate up to date
with the accepted results of L4-E10, L4-E11 and L4-E12, and answers L4-E11's E11-19: every finding that rested on the LM5069's
power limit re-judged for the TPS48110-Q1 entry L4-E11 selected. **Update round 3** (out 13) takes L4-E13's acceptance: U-03
becomes a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC) and moves from the choices that could overturn the architecture into
the register. **Update round 5** (out 14; the owner's instruction of 2 October 2026 to resolve Layer 4's remaining dependencies)
takes the dependency rounds of L4-E10 (`e464ff88`), L4-E12 (`c933724e`) and L4-E11 (`f1856bfd`), each accepted by the
coordinator's check 4 and merged into this line: U-01, U-02 and U-04 now carry their exact question, their evidence by vendor,
physical and owner, who supplies it, their fallback with its numbers and what each could overturn (7b), and stay
architecture-level choices; the register takes the rounds' rows and four items of the findings ledger
(`records/l4close/FINDINGS-LEDGER.md` at `fnd/l4close` `e1e99c4f`).

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
  - **three unresolved choices that could overturn the architecture**, which no owner closes: U-01 FEA-008's cell (the signed
    specification and the owner's two items; with the proposed cell 90.2 Wh usable against the 35E's 107.9 Wh at +25 C); U-02
    MESHSAT-1478, CONDITIONAL on T-H1 at or over 2.159 W/K (a reading of at least 2.416 W/K by the drafted procedure), with the
    session's fallbacks down to 1.125 W/K in E5 and 1.399 W/K in E3-O and the owner's below that, and CFL-002 the owner's
    question; U-04 source-only operation, a CONDITIONAL CANDIDATE that turns on TI's D1 and D3 (E11-24's hold-up takes D2 and D5
    off TI);
  - **U-03 moved downstream (update round 3):** L4-E13 makes it a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC): route 2,
    one identified SunPower SPR-E-Flex-100 measured against A-1 to A-3, is feasible on a unit equal to the typical rows (A-1
    24.1505 V against 25.000 V at -20 C and 1000 W/m2); route 1 closes nothing today; no unit is bought or measured. It decides
    which unit, not the topology or the source class (register R-35, R-52, R-148, R-149);
  - **the downstream tasks**, 146 register items, each with one owner and an acceptance that close the assignment, not the item;
  - **the owner's items** (section 7d): CFL-002 (A, B or C), U-01's specification request (ten questions) and then the cell
    change, the TI request (REVIEW-REQUEST.md with TI-QUESTIONS.md), T-H1's bench authorisation, the panel unit's purchase and
    measurement, and the other outside-contact drafts with their paths (SunPower's and Solbian's among them): actions, not
    questions.
- **Endurance (section 10):** A1 runs 2.52 h on battery at +20 C and first interrupts at hour 6 or 2 on the panel at its typical rows; it
  needs +1361.5 / +2094.1 Wh more storage for 48 / 72 h, plus at most 13.4 Wh a day at L4-E7R's accepted regulation and 17.7 Wh if U-01's
  cell is adopted; none of L4-E10 to L4-E12 moves these figures. DR-01 stands; every mandatory function is intended to be
  delivered, subject to the open conditions named here, and no service is reduced to narrow the gap.

## 1. The selected architecture as one connected design

![The connected power design: sources, protection, conversion, charging, storage, loads and controls](L4-POWER-DIAGRAM.svg)

**The one figure**, `L4-POWER-DIAGRAM.svg`, generated by `l4e9_power_path.py --write-svg` (the script refuses to run when the
committed file is not what it generates; out 15). Every source is traced through protection, conversion, charging and
storage to the loads; each power edge carries its interface row (section 2), each block its settings and limits, and the blue
tags are the control edges of 1c: which controller, gauge, comparator or firmware rule acts on which block. Parts and settings
marked drafted are not applied to any generator.

### 1a. The blocks

| Block | What | Settings and limits (as read; drafted parts named) |
|---|---|---|
| SRC_PV | Panel (REQ-016) | Voc at most 25 V at -20 C; at most 100 W into the stage; PANEL-ACC unit: none accepted (U-03) |
| SRC_DC | Vehicle or shore DC (REQ-015) | 9 to 36 V at the plug, -36 V reversed; D38999 size 12, loop >= 56.93 mOhm; XT60-class J_DCIN (drafted, R-131) |
| SRC_USB | USB-C input: none (D-12) | the USB-C port is an outlet only |
| SOL_IN | Solar entry, board E | J_SOLAR VH 10 A; F2 10 A mini blade; D4 SMCJ28A; the 50 V bulk; ahead of the sense bank; (L4-E7R, drafted); R59 15 mOhm on TRK_VIN |
| DC_IN | Vehicle entry, board E | F1 0997010.WXN 58 V DC (drafted); D10 SMCJ40CA, D1 SMCJ40A; Q1 CSD19532Q5B 100 V (drafted); U3/Q1 LM74700-Q1 ideal diode |
| U5 | U5 LT8705AI stage | hold 16.970 / 17.593 / 18.221 V; regulation RIMON_IN 31.6k; 2.5485 A nominal, 2.9318 A highest; backstop on SWEN 3.0468 to 3.7408 A; TRK_OUT ceiling 28.28 to 30.15 V; U4/Q2 ideal diode out |
| ENTRY | Entry breaker (L4-E11, drafted) | U6 TPS48110-Q1, Q7 CSD19536KTT; UVLO on 7.87 to 8.44 V; OV off 39.6 to 41.22 V; 6.364 to 7.136 A after 0.247 to 0.49 ms; short 10.36 to 13.87 A, retry 0.5 s; R19 4.5 mOhm, L2 SRF1260-1R0Y |
| VINRAW | VIN_RAW (board E to A) | D2 SMCJ40A clamp; four Mill-Max 9 A dock pins; declared 14.10 A; basis 43.18 V maximum |
| FE | U2 LM5176 front end, board A | R11 8 mOhm, R12 12 mOhm (drafted); U34 guard R14 76.8k (drafted); VBUS20 19.08 to 20.96 V; efficiency 0.93 declared (C-8) |
| BANK | VBUS20 bank (L4-E8, drafted) | six EEHZK1V331P, 45 mOhm each; every can at most 2.4096 A; rule 2.7745 A; Cc2 3.3 nF |
| CHG | U3 BQ25731 charger, board A | R16 10 mOhm; IIN_HOST 4.70 A; H3 line: flat 1.82 A, HIZ < 7.378 V; ChargeCurrent at most 3.0 A; BATOVP 17.64 V; no battery FET |
| VBAT | VBAT = VSYS node | 10.0 to 16.884 V; D1 SMCJ18A clamp; U-04: VSYS with no battery |
| PACK | Pack, board P (D-06 4S3P; U-01) | Samsung 35E x 12 (ruled cell); BQ4050 gauge and its FETs; BQ7720700 -> F2 SCF9550; F1 25 A; OCD1 20 A for 2 s; usable 107.9 Wh at +20 C |
| LOADS | Load converters | PS-IDLE-SPEC 42.8 W at the pack; slot, device, logic, monitor; heater U22/U33 12.0 V 7.5 W; eFuses TPS2596 21 V |
| USBC | USB-C outlet U19 + U18 | 5 / 9 / 15 V at 3 A; OCP 3.793 to 4.576 A; tablet budget 18 W cap (proposal) |
| POE | PoE stage | R227 5 mOhm, U17 on it (drafted); U16 boost 54 V at 0.6 A |
| PA | PA and HF rails | U13 13.8 V; key-down at most 60 s; U15 12 V to the QMX; outlets off while the PA keys |
| CTL_PANEL | Panel controller C:U3 RP2040 | the kit I2C: the charger,; the expanders, the INA226s; and the key-down rules |
| CTL_SENS | Sensor controller E:U10 RP2040 | the gauge's SMBus, the mixer; fans, VIN_MON; always on |
| CTL_HW | Hardware, no firmware | comparators, the gauge, the; breaker, the knee, OUTLET_OK |

### 1b. The power edges

| Edge | From | To | Through | Interface rows (status) |
|---|---|---|---|---|
| P01 | SRC_PV | SOL_IN | J_SOLAR, F2, D4, the bulk, the sense bank | IF-01 (CONDITIONAL) |
| P02 | SOL_IN | U5 | PV_P to TRK_VIN, U5's input | IF-02 (CONDITIONAL) |
| P03 | U5 | VINRAW | TRK_OUT through U4/Q2 | IF-03 (MEETS) |
| P04 | SRC_DC | DC_IN | the plug, the interconnect, J_DCIN, F1, Q1 | IF-04 (CONDITIONAL) |
| P05 | DC_IN | ENTRY | DC_P into U6/Q7 | IF-05 (CONDITIONAL) |
| P06 | ENTRY | VINRAW | R19, L2 to VIN_RAW | IF-05 (CONDITIONAL) |
| P07 | VINRAW | FE | the dock's pins, U2's input | IF-06 (MEETS), IF-07 (CONDITIONAL) |
| P08 | FE | BANK | VBUS20 | IF-07 (CONDITIONAL) |
| P09 | BANK | CHG | VBUS20 through R16 into U3 | IF-08 (CONDITIONAL), IF-09 (CONDITIONAL) |
| P10 | CHG | VBAT | U3's output, VSYS | IF-09 (CONDITIONAL) |
| P11 | VBAT | PACK | R17, A F1, the pack pins, board P | IF-10 (CONDITIONAL) |
| P12 | VBAT | LOADS | the converters' inputs | IF-11 (CONDITIONAL) |
| P13 | VBAT | USBC | U19's input, R138 | IF-12 (CONDITIONAL) |
| P14 | VBAT | POE | R227 to POE_VIN | IF-13 (CONDITIONAL) |
| P15 | VBAT | PA | U13's and U15's inputs | IF-14 (CONDITIONAL) |
| N01 | VINRAW | DC_IN | the tracker back-feeds DC_P through Q7's body diode (no power is delivered this way) | none: no power is delivered this way |

### 1c. The control edges

| Control | Controller | Acts on | What | Kind |
|---|---|---|---|---|
| C01 | CTL_PANEL | CHG | FW-A01 to A03, A16, A17: RSNS_RAC, IIN_HOST 4.70 A, ChargeCurrent at most 3.0 A, the charger's 175 s watchdog; CHG_INHIBIT (FW-A14) and rules R-a to R-d (R-126) | firmware |
| C02 | CTL_PANEL | LOADS | the expanders (FW-A08): SLOT_EN, DEV_EN, HEAT_EN; the margin hold (R-138, R-139); MAIN and PI_KILL (FW-A10 to A12) | firmware |
| C03 | CTL_PANEL | USBC | PD_SW_EN AND OUTLET_OK (FW-A06); the tablet's window (a proposal) | firmware and hardware |
| C04 | CTL_PANEL | POE | POE_SW_EN AND OUTLET_OK (FW-A06); U17 read on R227 (FW-A09, R-27) | firmware and hardware |
| C05 | CTL_PANEL | PA | the key-down rules K1 to K5 and C4 (FW-A05, D-11): at most 60 s, the rest floors 15.5 and 12.4 V | firmware |
| C06 | CTL_SENS | PACK | the gauge's SMBus (FW-E01): its ranges relayed to the charger by the host; SHUTDOWN for storage (FW-E09); HWD 10 s | firmware |
| C07 | CTL_SENS | LOADS | the mixer fans (FW-E07), the Geiger supply (FW-E08), VIN_MON for FW-A16 (FW-E04) | firmware |
| C08 | CTL_HW | U5 | the hold (FBIN divider R8, R9 at 0.1 %), the regulation (IMON_IN, RIMON_IN 31.6k), the backstop comparators on SWEN, off below 2.662 V of TRK_LDO33 | hardware |
| C09 | CTL_HW | ENTRY | the TPS48110-Q1's own UVLO, OV, breaker and short-circuit trip; the LM74700-Q1 blocks reverse current | hardware |
| C10 | CTL_HW | FE | U34's restart guard (R14 76.8k: 6.754 to 7.139 V); R11's average and R12's cycle-by-cycle limits | hardware |
| C11 | CTL_HW | CHG | the H3 line on ILIM_HIZ (the corrected knee), the charger's VINDPM, ACOV, BATOVP and SYSOVP | hardware |
| C12 | CTL_HW | PACK | the BQ4050's protections on its FETs (COV, CUV, OCC 5 A, OCD, SCD 60 A, UTC, OTC); the BQ7720700 drives F2 | hardware (the gauge's own firmware) |
| C13 | CTL_HW | USBC | OUTLET_OK = NOT (TR_APRS AND PA_EN), A:U30, drops both outlets while the PA keys; U18's OCP | hardware |

There is **no separate shore entry** (shore is J_DCIN) and **no USB-C input**: the USB-C port is a power-only outlet (D-12).

### 1d. The interface rows (out 4: every figure, check and source)

Modes: PS-IDLE-SPEC (42.8 W at the pack terminals), PS-ALLTX (203.8 W plan, 272.0 W high) and the PA keyed alone at 113 W
(162.3 W), charging at the window (the stage takes at most 53.42 W in at the hold under L4-E7R's regulation; 93 W out at the
window is a ceiling), and the tablet outlet (45 W on PS-TYP, 112.3 W plan). Thermal basis: the worst inside air, 62.1 C lid
closed (59.2 C lid open); at the margins L4-E12's route: at T-H1's binding line 2.159 W/K (lid open, fans) 67.55 C (E3-O) and
70.00 C (E5 under the hold); at LO-01a's floor with no hold 71.25 and 76.25 C (L4-E10's corner plus the ballasts).

| Row | Interface | Voltage, both sides | Current asked / available (modes) | Losses | Thermal assumption | Protection, each side | Settled by | Status (class) |
|---|---|---|---|---|---|---|---|---|
| IF-01 | panel to the solar entry | at most 25 V at -20 C; PANEL-ACC's A-1 Vm20 + U_V at most 25.000 V at -20 C and 1000 W/m2 (24.1505 V on the typical rows, margin 0.8495 V; Voc25 20.315 to 22.156 V) / D4 standoff 28 V on TRK_VS, reached by a unit at A-1's ceiling only above 8574 W/m2 at n 2; under CS101 the input at most 27.82 V; TRK_VS 44.25 V and PV_P 44.74 V at the capability scenario | hot short circuit 6.802 A with the sheet's tolerance; PANEL-ACC's A-3 (a) 3.987 A, (b) 8.1817 A, (c) 13.82 A at the design level 2111.4 W/m2 / F2 10 A; J_SOLAR's VH 10 A with the lead at AWG 16 (R-29); A-3(c) over JST VH's printed 10 A (R-148); under CS101 the filtered ripple at most 0.0585 A against a 0.1130 A margin | the lead about 0.0465 Ohm; the bank 0.5262 Wh a day | the entry at 62.1 C inside air; the bulk up to 4.45 times its ripple rating under CS101 (M2 reads it) | none / F2, the 50 V bulk ahead of the bank, D4 and C71 to C74, the INB filter (L4-E7R, drafted) | l4e O-1, L4-E7R (accepted), L4-E13 (accepted; PANEL-ACC) | CONDITIONAL (CONDITIONAL): no unit bought or measured (R-35), A-3(c)'s rating (R-148), M3's n (R-149), the lead at AWG 16 (R-29), the loop's typical rows (break-even 2.51 times), the bulk's temperature, the bank's pulse capability |
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

## 2. The budget: one input set (out 16)

One set of inputs, each read by the script from its pinned file: the approved profile PS-IDLE-SPEC (`load_trace.out`, 42.8 W
at the pack terminals over 39 loads, kept as approved; any other duty cycle is labelled as such), the power budget
(`pwr_budget.out`), the energy replay (`l4e_replay.out`) and L4-E10's chain for the stores, L4-E7R's accepted stage and L4-E13
for the panel, L4-E12 for the modes at the margins, L4-E11 for the source-only state and the tablet's service budget
(`tablet.out`, a PROPOSAL). The component revisions are the drafted selection of section 3 (none applied). **Electrical
feasibility and endurance are separate questions:** 2a and 2c are the electrical and thermal budget of each mode; 2b is
endurance, reported battery-only and solar-assisted separately.

### 2a. Power per mode

| Mode | State | The loads | At the pack or VBAT | Auxiliaries | Into the case | Leaves the case | Read from |
|---|---|---|---|---|---|---|---|
| M1 | PS-IDLE-SPEC, the approved profile (the tablet not charged) | 36.5 W at the load pins; 6.3 W in the converters and the distribution | 42.8 W (low 33.1, high 82.8 W, every load at its maximum) | inside the 42.8 W: 4 fans 3.128 W at the pack; 8.4 W of loads with no document (tier T); the board logic rows carry the power path's quiescent draws (not itemized by part) | 43.4 W (the pack's I2R 0.59 W inside) | 0 W | pwr_budget.out, load_trace.out, L4-E12 out 8c |
| M2 | the same with the tablet charged in its window (a PROPOSAL: 13 to 15 UTC, the outlet capped at 18 W) | the outlet 18 W for 2 h, at 0.93 through U19 | 42.8 W plus 19.4 W at VBAT for 2 h: 38.7 Wh a day | the outlet converter's idle 1.09 to 1.44 W only while enabled (on all day: 73.4 Wh a day) | 43.4 W plus the converter's 1.4 W in the window | 18 W to the tablet in the window | tablet.out (l3batt) |
| M3 | E3-O: the heat stage on shore (PS-SURV-R), every radio C1 leaves on | one module running; the shed set off | 23.272 W at the pack | 2 fans 2.000 W at the pack; the ballasts at most 2.09 W (the bound's worst corner) | 24.996 W on shore (the front end's and the charger's loss on the loads), 27.086 W with the ballasts | 0 W | L4-E12 out 2a, 8a |
| M4 | E5: the hold at the +60 C dwell, on shore | 14.671 W at the load pins; 3.445 W in the converters; 0.036 W in the distribution | 18.152 W at the pack | 2 fans 2.010 W at the pack; the ballasts at most 2.09 W | 19.497 W on shore (+1.345 W), 21.587 W with the ballasts | 0 W | L4-E12 out 8a |
| M5 | source-only at a 9.00 V plug, no usable pack (state S4; U-04) | P1 at VBAT 19.57 W plan (11.17 to 35.24 W), at most 20.51 W by the rule; the shed warm-up P2 28.12 W plan | the source delivers 29.09 to 42.52 W at VBAT | the entry's loop 5.095 W at 5.983 A (on the source's side); the front end at least 0.88021 there | 23.94 W at the rule's bound (the loads, U3 at 0.9733 and the front end at 0.88021) | 0 W | L4-E11 out 3g, 3h |
| M6 | solar charging at the window (the source's side) | the stage takes at most 53.42 W in at the hold (44.84 W nominal) under L4-E7R's regulation | into VBUS20 through U4/Q2 | the stage's own drive and quiescent 1.27 W (from the panel); the sense bank 0.5262 Wh a day; the ballasts at most 2.09 W while U3 runs (0.0093 W at nominal parts) | a charge on shore adds 3.446 W | 0 W | L4-E7R, L4-E13 out (A-2), L4-E8, L4-E12 out 2d |

**The quiescent draws** of the power path are not itemized part by part in any record: the profile carries them inside the
declared board rows (board A's logic and board E's controller and sensors), the solar stage's own drive and quiescent power
comes from the panel (M6), and the outlet converter idles only while it is enabled (M2). An itemized list would move the
profile by the parts' printed quiescent currents; it is not counted here as done.

### 2b. Energy: battery-only and solar-assisted, separately

| Case | Cell | Basis | The store | Runtime, the tablet not charged | With the tablet's window | The steady load each horizon carries | Read from |
|---|---|---|---|---|---|---|---|
| B1 | ruled 35E, D-06 4S3P | battery-only, room temperature (the chain's +20 C) | 107.9 Wh usable | 2.52 h | 1.73 h (the window at the start, the worst placement) | 2.25 W over 48 h, 1.50 W over 72 h | l4e_replay.out 2 (MODELED) |
| B2 | ruled 35E | battery-only, the cells at -10 C (the 35E's discharge floor) | 44.5 Wh usable | 1.04 h | 0.72 h | 0.93 W over 48 h, 0.62 W over 72 h | l4e_replay.out 2 |
| B3 | ruled 35E | battery-only, the cells at -5.52 C (REQ-024's -20 C with the kit's heat, LO-01b) | 54.0 Wh usable | 1.26 h | 0.87 h | 1.12 W over 48 h, 0.75 W over 72 h | L4-E10 out 9c |
| S1 | ruled 35E | solar-assisted, room temperature, the candidate panel's day (350.0 Wh into the stage, L4-E7's first round) | first stop at h 6 (06 UTC start) / h 2 (18 UTC start) | unserved 1367.4 / 1368.1 Wh at 48 h (33.4 % of the profile's 2054.4 Wh served at most), 2103.9 / 2104.6 Wh at 72 h (31.7 % served) | unserved at most 77.4 / 116.1 Wh more at 48 / 72 h (38.7 Wh a day for 2 / 3 windows; INFERRED bound); the first stops unchanged (they precede the 13 UTC window) | 8.0 W at both horizons; with the tablet at most 1.61 W lower (6.4 to 8.0 W) | l4e_replay.out 12 (MODELED; the corrected path, WE) |
| S2 | ruled 35E | solar-assisted, L4-E7R's accepted stage (336.6 Wh a day at the nominal hold) | as S1 (not re-run) | unserved at most 26.8 / 40.2 Wh more than S1 (13.4 Wh a day less into the stage; INFERRED bound) | as S1, plus S1's tablet bound | 7.4 to 8.0 W; with the tablet 5.8 to 8.0 W (INFERRED bounds) | L4-E13 check 4, l4e_replay.out 12 |
| S3 | ruled 35E | solar-assisted at the cold end | NOT COMPUTED: no cold-day sun trace is held, and the cells' temperature through the day is not modelled | not computed | not computed | 3.3 W if the steady load scales with the store as at room temperature (44.5 Wh against 107.9 Wh; INFERRED, an estimate, not a run) | this record (the method stated) |
| P1 | proposed HL18650V (a PROPOSAL, U-01; not adopted) | battery-only, room temperature (L4-E10's chain at +25 C) | 90.2 Wh usable | 2.11 h | 1.45 h | 1.88 W over 48 h, 1.25 W over 72 h | L4-E10 out 9c |
| P2 | proposed HL18650V (a PROPOSAL) | battery-only at the cold end (brackets, ASSUMPTION) | 45.1 to 69.6 Wh with the cells at -5.52 C; 37.2 to 54.1 Wh from a cold start at -20 C | 1.05 to 1.63 h; 0.87 to 1.26 h | less, by the same arithmetic | 0.94 to 1.45 W over 48 h at -5.52 C | L4-E10 out 9c |
| P3 | proposed HL18650V (a PROPOSAL) | solar-assisted, room temperature | not run by the replay | not computed | as S1's bound | 6.7 W if the steady load scales with the store (INFERRED estimate); every storage shortfall grows by at most 17.7 Wh | L4-E10 out 9c |

**Endurance, apart from electrical feasibility.** The objective of 48 to 72 h is NOT MET by A1 (DR-01): the steady load the
store and the sun carry through either horizon is the replay's 8.0 W against the approved profile's 42.8 W, a deficit of
34.8 W (81 % of the profile), and the least storage to add is +1361.5 / +2094.1 Wh at 48 / 72 h. **A charger change does not
close it:** the deficit is the store and the day's harvest, not a conversion efficiency. No mandatory function is reduced to
narrow it, and the profile is not lowered. The tablet's optional charging lowers what is carried by at most its 38.7 Wh a
day (S1, S2). The cold end's solar-assisted case is not computed (S3): no cold-day sun trace is held.

### 2c. Heat into the sealed case per mode, against T-H1's lines

| Heat | Mode | Into the case (W) | T-H1's line | The inside air (INFERRED unless named) |
|---|---|---|---|---|
| H1 | PS-IDLE-SPEC (M1) | 43.40 | C1's inside-air trigger +50 C | at the binding line +20.1 K: C1 sheds the profile to the reduced mode above 29.9 C ambient; on W4's lid-open 1.22 to 2.85 W/K +15.2 to +35.6 K |
| H2 | PS-IDLE-SPEC with the tablet's window (M2) | 44.80 | as H1 | +20.8 K at the binding line; C1 above 29.2 C ambient |
| H3 | E3-O, the heat stage with the ballasts (M3) | 27.09 | +70 C class at +55 C: 1.806 W/K | 67.55 C at the binding line (L4-E12) |
| H4 | E5 under the hold, with the ballasts (M4) | 21.59 | +70 C class at +60 C: 2.159 W/K, the BINDING line | 70.00 C at the line; T-H1 passes at a reading of at least 2.416 W/K (its expanded uncertainty deducted) |
| H5 | E5 with no hold | 27.09 | +70 C class at +60 C: 2.709 W/K | the hold is what lowers E5's line to 2.159 W/K |
| H6 | source-only at a 9.00 V plug (M5) | 23.94 | none set by the record (the envelope's state) | +11.1 K at the binding line (the loads and the two stages' losses at the rule's bound; INFERRED) |
| H7 | a charge running on shore (added to a mode) | 3.45 | LO-01a's floor 1.666 W/K (1.8058 W/K with the ballasts) | +1.60 K at the binding line |

### 2d. The reconciliation of every figure that differs between records

| Figure | Quantity | The figures, each with its basis and the file that prints it | Kept | Why |
|---|---|---|---|---|
| R01 | the 35E pack's usable energy at room temperature | 107.9 (l4e_replay.out: the energy chain (energy_budget.py: the 35E's rate, mean-voltage and end-fraction curves, aged 0.80, to the graceful 3.00 V line) at PS-IDLE-SPEC); 108.1 (pwr_budget.out: pwr_budget.py's derating chain (12 x 3.35 Ah x 3.60 V, rate 0.997, sag, ageing 0.80, the 5 % reserve)) | 107.9 Wh | the endurance runs (battery-only and solar-assisted) rest on the energy chain; 108.1 Wh stays only as L4-E10's first-chain comparison and in the U-01 bullet L4-E10 reads back (Appendix A) |
| R02 | the proposed HL18650V pack's usable energy | 90.2 (l4e10_cell_thermal.out: L4-E10's chain, the same as R01's 107.9 Wh); 90.4 (l4e10_cell_thermal.out: L4-E10's first chain, the same as R01's 108.1 Wh) | 90.2 Wh | one chain with the ruled cell; the difference to the 35E is 17.7 Wh on both chains |
| R03 | the panel's day into the stage at the nominal hold | 350.0 (l4e_replay.out: the candidate's trace with no input limit (L4-E7's first round); every solar-assisted run of the replay); 336.6 (l4e7_stage_settings.out: the same day under L4-E7R's accepted regulation (RIMON_IN 31.6k)) | 336.6 Wh for the design | the replay is not re-run: its solar rows stay on 350.0 Wh, bounded at most 13.4 Wh a day worse at the accepted stage (S2) |
| R04 | the hold corners' days | 344.0 (l4e7_stage_settings.out: L4-E7R, the hold 16.970 to 18.221 V with the regulation); 373.5 (l4e_replay.out: L4-E7's first round, the hold 16.695 to 18.490 V, no limit); 307.9 (l4e7_stage_settings.out: L4-E7R's upper corner); 280.6 (l4e_replay.out: L4-E7's first round's upper corner) | L4-E7R's 344.0 / 336.6 / 307.9 Wh | the accepted stage; the replay's corners are the first round's window |
| R05 | L4-E7R's highest regulated current | 2.9318 (l4e7_stage_settings.out: at the hold's corners, the stage's operating range); 2.9337 (l4e13_panel.out: at REQ-016's 25 V ceiling, A-3(a)'s conservative input) | both | two operating points of the same regulation; neither replaces the other |
| R06 | the 100 W bound's layers | 73.3436 (l4e13_panel.out: the regulation's own 25 V corner); 93.5521 (l4e7_stage_settings.out: the backstop's static bound, CONDITIONAL on G_CM and U18's VIN+ bias); 96.25 (l4e7_stage_settings.out: L4-E7's stack A, CONDITIONAL on five unprinted values) | all three, each with its layer | the regulation acts first, the backstop second; 96.25 W is the earlier qualification, kept as context |
| R07 | A1's steady load through the horizon | 8.0 (l4e_replay.out: on the candidate panel's trace (350.0 Wh a day)); 8.8 (l4e_replay.out: on the 100 W screening stimulus (a 400 Wp series REQ-016 does not admit)) | 8.0 W | the screening stimulus is not a source REQ-016 admits |
| R08 | the profile's power | 42.8 (load_trace.out: the profile's stated figure); 42.82 (load_trace.out: load_trace's sum of 39 loads); 42.824 (l4e12_thermal.out: L4-E12's reproduction of the same sum) | 42.8 W | one quantity at three roundings |
| R09 | the enclosure lines (W/K) | 1.666 (l4e10_cell_thermal.out: LO-01a's floor: the inside air at the SGP41's +55 C at +40 C on shore, the heat stage); 1.8058 (l4e12_thermal.out: LO-01a's floor with L4-E8's ballasts counted); 1.806 (l4e12_thermal.out: E3-O alone: the heat stage with the ballasts, +55 to +70 C); 2.159 (l4e12_thermal.out: E5 under the hold, +60 to +70 C: the BINDING line); 2.709 (l4e12_thermal.out: E5 with no hold); 2.416 (l4e12_thermal.out: T-H1's pass reading at a 10 K rise: 2.159 W/K plus its expanded uncertainty) | all, each with its criterion | different states and limits; T-H1 is judged at 2.416 W/K for the binding 2.159 W/K |
| R10 | E5's heat under the hold | 18.152 (l4e12_thermal.out: at the pack); 19.497 (l4e12_thermal.out: into the case on shore); 21.587 (l4e12_thermal.out: with L4-E8's ballasts) | 21.587 W for the line | three boundaries of one budget |
| R11 | E3-O's heat | 24.996 (l4e12_thermal.out: into the case on shore); 27.086 (l4e12_thermal.out: with the ballasts) | 27.086 W | the ballasts counted once |
| R12 | the charge current | 3.0 A (HW-FW-CONTRACT.md: the drawn ChargeCurrent limit (FW-A02)); 3.06 A (l4e_replay.out: energy_inputs.yaml's D-06 figure (1.02 A a cell), the replay's runs) | 3.0 A for the design | the replay's solar rows charge 2 % faster than the drawn limit allows, so they lean optimistic (not re-run) |
| R13 | the 35E's usable energy cold | 44.5 (l4e_replay.out: the cells at -10 C, the 35E's discharge floor); 54.0 (l4e10_cell_thermal.out: the cells at -5.52 C, REQ-024's -20 C with the kit's heat (LO-01b)) | both, each at its cell temperature | two temperatures |
| R14 | the hold's point | 17.6 V (l4e7_stage_settings.out: REQ-016's stated point); 17.593 (l4e7_stage_settings.out: the FBIN divider's nominal (R8 102 k, R9 7.50 k at 0.1 %)) | 17.593 V nominal | the divider's own value; 17.6 V is the requirement's rounded point |
| R15 | ChargeCurrent at the charger's POR | 256 mA (l4e11_power.out: TI's E2E answer (the register's reset code)); 0 A (l4e11_power.out: the register description's text) | 256 mA | L4-E11's correction: the description is in error by TI's word; the hold's persistence already covers it |
| R16 | the ballasts' loss | 2.09 (ripple_dense.out: at the bound's worst corner); 0.0093 (ripple_dense.out: at L4-E8's nominal illustration) | 2.09 W in every heat budget | the worst corner is what the thermal lines carry |
| R17 | the pack heater | 7.5 W into the cells (l4e10_cell_thermal.out: the mat's output); 8.5 W at the pack (l4e10_cell_thermal.out: with its buck's loss) | both, each at its boundary | one heater, two boundaries |
| R18 | P1, the kit's shed state with no usable pack | 19.57 (l4e11_power.out: the plan figure at VBAT); 20.51 (l4e11_power.out: the rule's bound); 35.24 (l4e11_power.out: the loads' high corner) | 20.51 W as the bound | the high corner exceeds the source's least, which is why REQ-015 at 9.00 V is a CONDITIONAL CANDIDATE |
| R19 | the panel's day at the conditioned upper corner | 240.0 (l4e13_panel.out: the rated unit); 52.3 (l4e13_panel.out: a unit at A-2's floor) | both | PANEL-ACC accepts any unit inside the window; the unserved energy grows toward the floor's unit |

## 3. The circuit-change list, in application order (out 17)

Every change L4-E4 to L4-E13 and this record hand to the generators, the firmware and the interface texts, with the U-01 and
U-04 drafts as they stand: each with its board and generator, apply script, dependency, release guard, what it changes and its
state. **None is APPLIED:** every apply script refuses the tree's own generator until its release record reads "released: yes".
**The release records come first:** R-90 (L4-E4's, naming the accepted checks of L4-E4 to L4-E6 and L4-E8), R-91 (L4-E8's),
R-92 (L4-E7's), R-93 (this record's) and R-147 (L4-E11's). **The order constraints**, each checked by the script on the list:
R12 (R-01) before R11 (R-04) and before the ballasts and Cc2 (R-07); the H3 line (R-03) with R12; Q1 and E-F1's capacitor
(R-17, R-16) no later than R10 (R-13), which goes only with board A's H3 line; F1 (R-18) before the hot-swap settings (R-94),
and those before the selected entry's draft (R-123), which replaces the timer draft (R-119, the LM5069 alternative only); L4-E7's
hold and input limit before its backstop; U17's move (R-06) before its recalibration (R-27); each board regenerated after its
circuit changes. The U-01 rows apply only under approach (II) after the owner's approval; the U-04 hold-up (R-152) has no draft
yet.

| # | Step | Row | Board and generator | Apply script | Depends on | Release guard | What it changes (the register's item) | State |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | R-23 | HW-FW-CONTRACT.md (Layer 5) | apply_fw_a16.py | with board A's H3 line | the draft refuses a second application | HW-FW-CONTRACT.md: FW-A16 restated (IIN_HOST a constant 4.70 A, EN_EXTILIM kept), FW-A18, V-A06 to V-A10, FW-E04 and FW-C01's touches; V-A08 and L4-E5's source-change transient cell as L4-E11 restates them for the selected entry (R-135) | DRAFTED (not applied) |
| 2 | 1 | R-24 | pcb_interfaces.yaml, HW-FW-CONTRACT.md (Layer 5) | a text draft (this record) | with the release records | a text draft | The Layer 5 handover entries LH-01 to LH-09 written into pcb_interfaces.yaml and HW-FW-CONTRACT.md | DRAFTED (not applied) |
| 3 | 1 | R-125 | HW-FW-CONTRACT.md, PANEL.md (Layer 5) | a text draft (L4-E11 7a (E11-03); LAYER5-HANDOVER LH-10) | with the release records | a text draft | FW-C08 (SHORE_INHIBIT), FW-A14 (CHG_INHIBIT) and PANEL.md section 10 restated as L4-E11 7a (rule R-a's state table, S4's exception, the hold's persistence); DCIN_PGD restated as the entry's fault flag (U6's FLT_I and FLT_T) | DRAFTED (not applied) |
| 4 | 1 | R-133 | CONOPS | a text draft (L4-E11 7b (E11-18)) | with the release records | a text draft | The source-only statement in CONOPS (L4-E11 7b): with no usable pack the kit runs within the source envelope at its plug (about 29 W at 9 V, 32 W at 12 V and 70 W at 24 V on its bus at the least), sheds at 9 V and warms a cold pack on the headroom; a deeply discharged pack holds the node under the converters' floor while it pre-charges; a brown-out may latch the charger off until a re-plug | DRAFTED (not applied) |
| 5 | 1 | R-135 | L4-E5's V-A08 (Layer 4) | a text draft (L4-E11 7a (E11-21)) | with the release records | a text draft | L4-E5's V-A08 and its source-change transient cell restated as L4-E11 7a drafts them for the selected entry: the breaker never trips (over 6.364 A for less than 0.247 ms, the filtered sense under 10.36 A) and VIN_RAW never under 7.24 V | DRAFTED (not applied) |
| 6 | 1 | R-138 | CONOPS 4, HW-FW-CONTRACT.md (Layer 5) | a text draft (L4-E12 sections 6 and 9; LAYER5-HANDOVER LH-11) | with the release records | a text draft | The margin hold as a mode (CONOPS 4, HW-FW-CONTRACT): its trigger at the window's middle (68.65 C of mixed air plus the calibrated offset), restore 5 K under after 30 minutes, its actions and enables, the SOS queue; the SGP41's own shutdown (off at a TMP117 reading of 54.0 C, on and used at or under 49.0 C, off at every start until then) | DRAFTED (not applied) |
| 7 | 3a | R-01 | board A, gen_sch_a.py | apply_gen_sch_a_r12.py | first in board A's round, together with R-03 and R-124: L4-E6 forbids R12 before the H3 line | none: L4-E6's draft carries no release guard | R12 12 mOhm (HoJLR2512-3W-12mR-1%, C2904242) and C147 330 pF C0G (C1664) on the front end U2 | DRAFTED (not applied) |
| 8 | 3a | R-02 | board A, lcsc_fill.py | apply_lcsc_fill_r12.py | with R-01 | none | The lcsc_fill.py line mapping "12mOhm 1% 2512" to C2904242 | DRAFTED (not applied) |
| 9 | 3a | R-03 | board A, gen_sch_a.py | none: a missing draft | with R-01 and R-124 (the corrected knee) | no draft yet | U3's ILIM_HIZ network (H3), drawn to L4-E11's corrected knee: a flat 1.82 A of board current from VIN_RAW 7.95 V up to 10.549 V, where L4-E5's line 1.000 V + 0.0690 V/V x VIN_RAW takes over; below 7.95 V L4-E5's knee slope (2.484 V/V at the pin), zero at 7.657 V, HIZ certain below 7.378 V; Q6's HIZ pull-down kept | MISSING DRAFT (not applied) |
| 10 | 3a | R-124 | board A, gen_sch_a.py | apply_gen_sch_a_guard.py | with R-03 (the guard under the corrected knee) | L4-E11's RELEASE.md (R-147: check-l4e11-3.md at a15ab384) | The front end's restart guard U34 with R14 76.8k (C23107), together with the corrected knee (R-03) | DRAFTED (not applied) |
| 11 | 3b | R-04 | board A, gen_sch_a.py | apply_gen_sch_a_r11.py | after R-01: R11 never before R12 | L4-E4's RELEASE.md (R-90: accepted checks of L4-E4, L4-E5, L4-E6 and L4-E8) | R11 8 mOhm (HoJLR2512-3W-8mR-1%, C2904240), with IIN_HOST 4.70 A in firmware | DRAFTED (not applied) |
| 12 | 3c | R-07 | board A, gen_sch_a.py | apply_gen_sch_a_bank.py | after R-01: the ballasts and Cc2 only with R12 | L4-E8's RELEASE.md (R-91: check-l4e8-3.md), and the draft refuses a generator without R12 | Six ballasts R221 to R226, 45 mOhm (HoJLR2512-3W-45mR-1%, C2903491), one in series with each EEHZK1V331P, and Cc2 (C6) 680 pF to 3.3 nF (C1613) | DRAFTED (not applied) |
| 13 | 3c | R-08 | board A, lcsc_fill.py | none: a missing draft | with R-07 | no draft yet | The lcsc_fill.py line mapping "45mOhm 1% 2512" to C2903491 | MISSING DRAFT (not applied) |
| 14 | 3d | R-05 | board A, gen_sch_a.py | apply_gen_sch_a_r138.py | independent | L4-E4's RELEASE.md (R-90: accepted checks of L4-E4, L4-E5, L4-E6 and L4-E8) | R138 5 mOhm (HoJLR2512-3W-5mR-1%, C2903482) and its PD_SW note | DRAFTED (not applied) |
| 15 | 3e | R-06 | board A, gen_sch_a.py | apply_gen_sch_a_u17.py | after 3a to 3d | this record's RELEASE.md (R-93, after its check) | The PoE monitor U17 moved off the 54 V rail (HF-F02, S-60): R227 5 mOhm (HoJLR2512-3W-5mR-1%, C2903482) from VBAT to a new rail POE_VIN; U16's VIN and BIAS on POE_VIN; U17 IN+ on VBAT, IN- and VBUS on POE_VIN | DRAFTED (not applied) |
| 16 | 3f | R-09 | board A, gen_sch_a.py | a text draft (L4-E8) | with R-07 | a text draft | L4-E8's text corrections: gen_sch_a.py's third fix-up comment (the conservative bound replacing the lost dense figures) and the superseded bank notes of r11dep and L4-E6 | DRAFTED (not applied) |
| 17 | 3f | R-10 | board A, the declarations | none: a missing draft | with R-04 | no draft yet | The declarations on board A: VBUS20 and FE_OUT stay at 6.0 / 8.0 A (they cover 4.964 A in service and 7.262 A highest at 8 mOhm; their peak rises to 8.300 A only if V-A07 fails); VIN_RAW stays 14.10 A (it covers the front end's 11.65 A fault, 13.315 A at 7 mOhm); pcb_sensitive.yaml's FE_ISNS text (3.80 A) restated to 4.964 A | MISSING DRAFT (not applied) |
| 18 | 3f | R-152 | board A, gen_sch_a.py | none: a missing draft | U-04's fallback, in board A's round once drafted (its zone and height Layer 9's) | no draft yet | U-04's bounded fallback on VBAT, the charger's VSYS (L4-E11's E11-24, SESSION, never applied): one Panasonic EEHZK1V181P directly on VSYS (C242139) and a hold-up bank of four EEHZK1E471P (C242138) charged through R_CH 330 Ohm RC2512FK-07330RL (C137025) and discharging through D_H B540C-13-F (C72264); it takes D2 and D5 off TI's statements, not D1 or D3; the zone and the height are Layer 9's | MISSING DRAFT (not applied) |
| 19 | 3g | R-11 | board A, regenerated on the box | none: owed work | after 3a to 3f | the gates and the evidence re-taken | Board A regenerated with R-01 to R-10, its gates and evidence re-taken on the box | OWED (not applied) |
| 20 | 4a | R-16 | board E, gen_sch_e.py | apply_gen_sch_e_cin.py | no later than R-13 | none: d8dec31's draft carries no release guard | E-F1: the LM74700-Q1's input capacitor, 1 uF 100 V X7R 1210 (C382212), DC_F to GND_V at U3's ANODE | DRAFTED (not applied) |
| 21 | 4a | R-17 | board E, gen_sch_e.py | apply_gen_sch_e_q1.py | no later than R-13 | this record's RELEASE.md (R-93, after its check) | Q1, the vehicle entry's ideal-diode FET, to the CSD19532Q5B (100 V, C473333, the part Q7 carries) on Q7's PPAK land | DRAFTED (not applied) |
| 22 | 4b | R-13 | board E, gen_sch_e.py | none: a missing draft | only in the same release as board A's H3 line (R-03) | no draft yet | R10 115 k to 232 k (E96, 1 %): TRK_OUT's ceiling 28.28 / 29.21 / 30.15 V | MISSING DRAFT (not applied) |
| 23 | 4b | R-14 | board E, gen_sch_e.py | none: a missing draft | with R-13 | no draft yet | C26 and C27 (10u 25 V on TRK_OUT) re-rated to the drawn C13's 10u 50 V part | MISSING DRAFT (not applied) |
| 24 | 4b | R-15 | board E, the declarations | none: a missing draft | with R-13 | no draft yet | TRK_OUT's declaration: v_work to the raised ceiling's 30.15 V | MISSING DRAFT (not applied) |
| 25 | 4c | R-12 | board E, gen_sch_e.py | apply_gen_sch_e_u5_grade.py | board E's round | L4-E7's RELEASE.md (R-92: L4-E7R's check 4) | U5 to the I grade, LT8705AIUHF#PBF (C674169); procurement from a distributor with stock (LCSC held none on 1 October 2026) | DRAFTED (not applied) |
| 26 | 4c | R-19 | board E, gen_sch_e.py | apply_gen_sch_e_hold.py | board E's round | L4-E7's RELEASE.md (R-92: L4-E7R's check 4) | R8 102 k and R9 7.50 k as 0.1 % 25 ppm/K parts (C861068, C728597): REQ-016's 17.6 V point kept | DRAFTED (not applied) |
| 27 | 4c | R-20 | board E, gen_sch_e.py | apply_gen_sch_e_input_limit.py | after R-19 | L4-E7's RELEASE.md (R-92: L4-E7R's check 4) | RSENSE1 R59 15 mOhm (C2903494) on the new net TRK_VIN, RIMON_IN R16 23.2 k (C861244), CIMON_IN C65 100 nF (C14663), their declarations | DRAFTED (not applied) |
| 28 | 4c | R-144 | board E, gen_sch_e.py | none: a missing draft | U-02's board E changes | no draft yet | Board E for U-02: the SGP41's load switch (a TPS22810 feeding +3V3_SGP from +3V3_E6, enabled from U10's GPIO20 with a 100k pull-down), its bus on GPIO21 and GPIO22 with pull-ups to +3V3_SGP, the TMP117 beside it on the always-powered sensor bus (or option A's or B's change, OW-1); U13 to a buck, or a DRV-package LDO with the rail's load re-derived under 0.323 A (MESHSAT-1479) | MISSING DRAFT (not applied) |
| 29 | 4d | R-21 | board E, gen_sch_e.py | apply_gen_sch_e_backstop.py | on the texts R-19 and R-20 leave | L4-E7's RELEASE.md (R-92: L4-E7R's check 4) | L4-E7R's backstop and corrected solar entry with its CS101 correction, `apply_gen_sch_e_backstop.py` (9 edits on the text the hold and input-limit drafts leave: the sense bank on PV_P to TRK_VS, R59 and CSPIN behind it, SWEN with R70 and R71 as the supply guard, the 50 V bulk on PV_P ahead of the bank, D4 and C71 to C74 on TRK_VS, the INB filter of five 100 nF C0G across R66, R66 8.45k, R14 on TRK_VS, R16 (RIMON_IN) 31.6k) | DRAFTED (not applied) |
| 30 | 4d | R-98 | board E, gen_sch_e.py | apply_gen_sch_e_backstop.py | with R-21 (the same draft) | L4-E7's RELEASE.md (R-92: L4-E7R's check 4) | L4-E7R's CS101 correction (D-01): the bulk ahead of the sense bank, the INB filter (five 100 nF C0G across R66, 3.960 to 4.496 ms), R66 8.45k, RIMON_IN 31.6k; drafted inside R-21's `apply_gen_sch_e_backstop.py` | DRAFTED (not applied) |
| 31 | 4e | R-18 | board E, gen_sch_e.py | apply_gen_sch_e_f1.py | after 4c and 4d | this record's RELEASE.md (R-93, after its check) | F1 (vehicle entry) to the Littelfuse 0997010.WXN, MINI 58 V DC, 1000 A at 58 V DC (E-F2, S-107), in a holder whose maker prints at least 20 A (R-132; the draft names the 3568, which prints none); the BOM, the kit's label and ASSEMBLY.md name the 0997, since a MINI holder also takes a 32 V MINI | DRAFTED (not applied) |
| 32 | 4e | R-95 | board E, pcb_energy_chain.yaml | none: a missing draft | with R-18 | no draft yet | pcb_energy_chain.yaml's SHORE_INPUT stage restated for the 0997 and the selected entry: the ATOF 287 table and 56 C ambient replaced by the 0997 derating table at its 80 C column; conductor 20 A (the interconnect, D-06); the breaker's 7.14 A; prospective high 900 A (the specified loop floor at 43.18 V); the stage names what it protects (the interconnect) | MISSING DRAFT (not applied) |
| 33 | 4e | R-96 | pcb_fuse_derating.yaml | none: a missing draft | with R-18 | no draft yet | pcb_fuse_derating.yaml: the 0997 table (-40 to 100 C columns) added from the held sheet | MISSING DRAFT (not applied) |
| 34 | 4e | R-132 | board E, gen_sch_e.py | none: a missing draft | with R-18 (F1's holder) | no draft yet | F1's holder: a MINI 297/997 holder whose maker prints a current rating of at least 20 A (the 3568 prints none) | MISSING DRAFT (not applied) |
| 35 | 4e | R-94 | board E, gen_sch_e.py | apply_gen_sch_e_hotswap.py | after R-18: the base the entry draft applies on | this record's RELEASE.md (R-93, after its check) | The vehicle entry's hot-swap settings (D-02, D-07) as the base the selected entry's draft applies on: R22 100k and R23 6.42k, both 0.1 %, so the LM5069's OVLO reads 39.71 / 41.44 / 43.18 V; R24 22k 1 %, at least 5.06 mV at 43.18 V. R-123's draft overwrites R20 to R24 and C5: these values stand only for the LM5069 alternative | DRAFTED (not applied) |
| 36 | 4e | R-123 | board E, gen_sch_e.py | apply_gen_sch_e_entry.py | AFTER R-94 (its old texts are that draft's results) and INSTEAD of the timer draft (R-119) | L4-E11's RELEASE.md (R-147: check-l4e11-3.md at a15ab384) | The selected vehicle entry: U6 TPS48110AQDGXRQ1, Q7 CSD19536KTT, R19 4.5 mOhm, L2 SRF1260-1R0Y and the network of L4-E11 3c; the DGX-19 land added to meshsat.pretty from TI's DGX0019A drawing and the D2PAK land checked against TI's KTT drawing; _VEH_T restated to 7.14 A | DRAFTED (not applied) |
| 37 | 4e | R-116 | board E, lcsc_fill.py | none: a missing draft | with R-123 | no draft yet | LCSC codes (or lcsc_fill.py lines) for the parts the selected entry's draft names without one (R20 59.0k, R21 10.0k, R22 332k 0.1 %, R23 10.0k 0.1 %, R80 100R 0.1 %, R81 3.01k, R82 36.5k, R83 10R, R84 100k, R85 39k, R86 100R, C123 1u 25V, C124 100n 100V, C125 1n C0G 100V); with the LM5069 kept, R22 100k 0.1 %, R23 6.42k 0.1 % and R24 22k 1 % | MISSING DRAFT (not applied) |
| 38 | 4f | R-22 | board E, regenerated on the box | none: owed work | after 4a to 4e | the gates and the evidence re-taken | Board E regenerated with R-12 to R-21, its gates and evidence re-taken on the box | OWED (not applied) |
| 39 | B | R-107 | board B, gen_sch_b.py | none: a missing draft | board B's round | no draft yet | BANK-R1 in gen_sch_b.py (E3-L's stage criteria fail where the heat stage is entered without it) | MISSING DRAFT (not applied) |
| 40 | C | R-145 | board C, gen_sch_c.py | none: a missing draft | board C's round | no draft yet | Board C for U-02: the MAIN, PI and TEST pushbuttons (R-141's pick); U5 to the DRV package; U5's declared 0.72 A peak against its 500 mA (MESHSAT-1479) | MISSING DRAFT (not applied) |
| 41 | 5 | R-25 | firmware | none: owed work | only on a board A with the H3 line (else the derated limit) | firmware | Firmware: IIN_HOST 4.70 A (code 94, 0x5E00, RSNS_RAC 0b), rewritten after every adapter removal; on the drawn board the derated 4.00 A | OWED (not applied) |
| 42 | 5 | R-26 | firmware | apply_fw_a16.py | with R-23 | firmware | Firmware: FW-A18's diagnostic (the pin's band, three readings, the fallback) | OWED (not applied) |
| 43 | 5 | R-27 | firmware | none: owed work | after R-06 | firmware | Firmware: FW-A09's U17 row recalibrated to R227 (5 mOhm in the PoE stage's input): full scale 16.384 A, Current_LSB 0.5 mA, CAL 2048; the readings are the stage's INPUT current and POE_VIN (VBUS pin 8; VBAT is POE_VIN plus the shunt's drop); a full-scale sample is a saturated transient, not a current; the output power inferred through the stage's efficiency | OWED (not applied) |
| 44 | 5 | R-28 | firmware | none: owed work | with the D-11 rules | firmware | Firmware: FW-A05's D-11 thresholds (15.5 V and 12.4 V rest floors, 60 s, 18 A unkey) and ChargeCurrent at most 3.0 A (FW-A02) kept, re-derived at bring-up | OWED (not applied) |
| 45 | 5 | R-126 | firmware | none: owed work | with R-125 | firmware | Firmware: rules R-a to R-d: R-a's state table with its S4 exception and the hold's persistence; R-b's two settings (ChargeCurrent() 0x0000 or 0x0200 and no other value while U3's SRN reading is under 14.0 V or the gauge reports XDSG or PRECHARGE); R-c's shedding sequence with the mat on measured headroom and the VSYS_UVP recovery; R-d's PCHG_COMM 1 and SUV check | OWED (not applied) |
| 46 | 5 | R-139 | firmware | none: owed work | with R-138 | firmware | Firmware: the hold (the expanders' outputs and the software enables U503 RB_SW_EN, U504 LORA_ON, U505 ZB_ON and GEIGER_EN; the charge by the charger's bit; the running module idled with its logging) and the SGP41's switch, thresholds and bus handling | OWED (not applied) |
| 47 | 8 | R-129 | Layer 7, the DC receptacle and plug | none: a missing draft | before the harness is built | no draft yet | The DC receptacle and plug on MIL-DTL-38999 size 12 contacts (insert 17-6, or 13-26 with the solar pair on rated contacts elsewhere) | MISSING DRAFT (not applied) |
| 48 | 8 | R-130 | Layer 7, the interconnect | none: a missing draft | with R-129 | no draft yet | The DC interconnect specified by its loop, the NATO plug's pins to J_DCIN's board pins: cores and the NATO plug with a maker's rating of at least 20 A, the selected construction 3.05 m of AWG 14 with the 0.5 m lead | MISSING DRAFT (not applied) |
| 49 | 8 | R-131 | Layer 7, the inside lead and J_DCIN | none: a missing draft | with R-129 | no draft yet | The inside lead (a maker's rating of at least 20 A) and J_DCIN as a board connector rated at least 20 A, XT60 class of the gender opposite J_BATT's, or soldered lands | MISSING DRAFT (not applied) |
| 50 | 8 | R-111 | Layer 7, the enclosure | none: owed work | U-02: to T-H1's line | no draft yet | MESHSAT-1478 (U-02): the enclosure designed to T-H1's 2.159 W/K lid open with the fans (inside fins on the plate, mixer flow); the plate coupling of the radio modules and the LimeSDR as the fallback if T-H1 reads between 1.806 and 2.159 W/K; the NKK MBN cutouts. This assignment does not close U-02 | OWED (not applied) |
| 51 | U-01 | R-105 | board P, gen_sch_p.py | none: owed work | only under U-01's approach (II), after the owner's approval | no draft yet | Under U-01's approach (II) only: gen_sch_p.py U2 to the BQ7720704 (83 C, OVP 4.275 V, UVP 2.0 V, COUT an open-drain active pulldown) and F2's drive re-drawn; pcb_pack_protection.yaml re-derived; the ladder C1 75.0, H1 76.5, H2 77.0, OTD 77.5 C (first cut), SOT, the PTC, the release | OWED (not applied) |
| 52 | U-01 | R-106 | firmware, the gauge image | none: owed work | only under (II) | firmware | Under U-01's approach (II) only: the gauge image with the new cell's data, the re-derived ladder and cold cutoffs | OWED (not applied) |
| 53 | U-01 | R-154 | firmware, the gauge image and the host | a text draft (L4-E10 section 14b (out 9b)) | only under (II), with R-106 | a text draft | Under U-01's approach (II) only: L4-E10 section 14b's charge drafts in the gauge image, relayed by the host to the charger: Low Temp T1 -9 C to T2 1 C at 0.84 A to 16.40 V (BATOVP 17.06 V); Standard Temp low T2 1 C to T5 11 C at 1.68 A to 16.80 V; T5 11 C to T3 42 C at the drawn 3.00 A to 16.80 V (BATOVP 17.47 V); UTC -9.0 C (recovery -5.0 C); T3 42 C, T4 43 C and OTC 44.0 C kept; the kit's charge hold below -7 C (from +3 C), the mat warming the block first; CUV 2.50 to 2.75 V a cell; the termination current 250 mA (TI's default, ASSUMPTION) | DRAFTED (not applied) |
| 54 | ALT | R-119 | board E, gen_sch_e.py | apply_gen_sch_e_timer.py | the LM5069 alternative only: refuses once the selected entry (R-123) has run | L4-E11's RELEASE.md (R-147: check-l4e11-3.md at a15ab384) | D-09, only if the LM5069 is kept (the selected entry has no fault timer against a power limit): L4-E11's `apply_gen_sch_e_timer.py` (C5 GRM3195C1H104GA05 with C121 GRM3195C1H683JA05), ITIMER and VTMRH at temperature, tFAULT and the 2 mA turn-off with Q7's gate charge, the start into VIN_RAW (34 uF) with the front end held off by U34 | DRAFTED, the alternative only (not applied) |

## 4. The operating behaviour (out 18)

One table per item; every row names the record it rests on and a figure the script read. The traces as first written
(rounds 1 to 4) are kept in Appendix B for their narrative.

### 4a. Source changes

| Source change | What acts | The figure | Record |
|---|---|---|---|
| plug in (vehicle or shore) | the entry's UVLO, then its slewed start; U3 in HIZ under the knee; the H3 line from the first cycle; U34 releases the front end | on at 7.87 / 8.14 / 8.44 V of DC_P; 0.382 to 1.219 A for at most 2.5 ms; HIZ certain below 7.378 V; the flat 1.82 A from 7.95 V | L4-E11 3c, 3f |
| plug out | the LM74700-Q1 blocks; the pack carries VBAT with no break (no battery FET); U3 resets IIN_HOST and firmware rewrites it; U34's guard stops the front end; the bank bleeds | IIN_HOST 3.25 A at removal, 4.70 A rewritten (FW-A16); the guard 6.754 to 7.139 V; the bleed 0.455 to 1.494 s | CHARGER-STATE-SEQUENCE.md, L4-E11, L4-E8 |
| panel at dawn | U5's own UVLO and soft start; SWEN off while TRK_LDO33 is low; the hold; the regulation | SWEN off below 2.662 V; the hold 17.593 V; 2.5485 A nominal, at most 2.9318 A (44.84 / 53.42 W in) | L4-E7R |
| panel at dusk | the panel falls under the hold and the stage stops delivering; U4/Q2 blocks VIN_RAW from TRK_OUT; with no other source VIN_RAW falls into the knee's HIZ | HIZ below 7.378 V; the guard 6.754 to 7.139 V | L4-E7R, L4-E11 3f |
| pack connected | the gauge's FETs close onto VBAT; the always-on comes up on CELL_F; the inrush into VBAT's capacitors | 242.9 A peak, over ASCD's 55.6 A for 61.5 us against its 183 us delay (with E11-24's direct can; the drawn VBAT holds less) | L4-E11 out 10 |
| pack disconnected, or both FETs open, with a source | U3 holds VBAT at ChargeVoltage with no battery current (state S4), CONDITIONAL on TI's D1 (U-04) | VSYS at least 16.716 V against VSYS_MIN 12.3 V (a 4.416 V margin, once the mode is shown) | L4-E11 9 (D1) |

### 4b. Simultaneous operation

| Together | What acts | The figure | Record |
|---|---|---|---|
| the profile with solar at the window and a 24 V vehicle | the tracker's ceiling above 24 V: the panel carries the bus first; the H3 line at VIN_RAW | at most 4.194 A at 24 V, 65.9 % of the breaker's lowest 6.364 A | L4-E5, L4-E11 |
| what reaches VBAT from the sources | U3 between its minimum at the lowest bus and its board-current maximum | 84.5 to 99.6 W | this record out 5 |
| PS-IDLE-SPEC, 42.8 W | the loads take the sources first, the pack the rest; the outlets drop while the PA keys (OUTLET_OK) | up to 41.7 W left to charge, at most 3.0 A | this record out 5 |
| PS-TYP with the USB-C outlet at 45 W, 112.3 W | the loads take the sources first, the pack the rest; the outlets drop while the PA keys (OUTLET_OK) | the pack supplies at least 27.8 W | this record out 5 |
| the PA keyed alone at 113 W, 162.3 W | the loads take the sources first, the pack the rest; the outlets drop while the PA keys (OUTLET_OK) | the pack supplies at least 77.8 W | this record out 5 |
| PS-ALLTX (plan), 203.8 W | the loads take the sources first, the pack the rest; the outlets drop while the PA keys (OUTLET_OK) | the pack supplies at least 119.3 W | this record out 5 |
| a 9.00 V plug with the profile | the pack supplements; it charges only while the kit draws under the source's least | 29.09 to 42.52 W at VBAT from the plug | L4-E11 3h |

### 4c. Startup: cold, dead pack, source-only

| Start | What acts | The figure | Record |
|---|---|---|---|
| cold start on the pack | MAIN brings up board A's +3V3; DEV_EN on by its pull-up; the panel controller runs FW-C01's order: PI_KILL low, the expanders' outputs before their configuration, the charger with FW-A01 first, then SLOT_EN one at a time | before the host writes IIN_HOST the input limit gives about 31 W into VSYS (INFERRED) | ARCHITECTURE.md 4.3, HW-FW-CONTRACT, CHARGER-STATE-SEQUENCE.md |
| a dead pack (at or under CUV) | the gauge's CUV holds; U3 charges through the open discharge FET's body diode at its clamp; rules R-a to R-d; the image's pre-charge | CUV 2.50 V a cell; the clamp 384 mA typical (no maximum printed: D7); ChargeCurrent 256 mA at POR | L4-E11 2, 4, 9 |
| a cold pack | UTC holds the charge FET; the mat warms the block first (FW-A13); under U-01's (II) the kit's hold moves to -7 C | warm before charge below -10 C at the cell; the mat 12.0 V, 7.5 W | HW-FW-CONTRACT FW-A13, L4-E10 14b |
| source-only at a 9.00 V plug | the shedding sequence P0 to P3 (L4-E11 3g): P1 kept, the warm-up P2 on the source's headroom | P1 at most 20.51 W; P2 28.12 W plan carried with 0.98 W in hand; the source 29.09 to 42.52 W at VBAT | L4-E11 3g, 3h (U-04) |

### 4d. Shutdown

| Stop | What acts | The figure | Record |
|---|---|---|---|
| graceful, on battery | the firmware's graceful line ends the run before either cell's end voltage | 3.00 V a cell under load | L4-E10 9b, 9c |
| the gauge's under-voltage | CUV opens the discharge FET | 2.50 V a cell (2.75 V under U-01's (II)) | pcb_pack_protection.yaml, L4-E10 14b |
| MAIN pressed | an ordinary press asks the modules to shut down (PI_SHDN_REQ), then PI_KILL; held, the LTC2954 forces the kit off | forced off after about 4.4 s (3.3 to 6.0 s) | HW-FW-CONTRACT FW-A10 to A12 |
| C1 at the inside air | module shedding: normal to the reduced mode, then the heat stage; restores 5 K below | inside air +50 C or any cell +55 C | CONOPS 4 via L4-E12 1f |

### 4e. Faults: each trip, what it isolates, the recovery

| Trip | What acts, its threshold and time | What it isolates | The recovery | Record |
|---|---|---|---|---|
| the vehicle entry's breaker | 6.364 / 6.8 / 7.136 A after 0.247 / 0.37 / 0.49 ms | the vehicle source from VIN_RAW (Q7 off) | retry every 0.5 s | L4-E11 3c |
| the entry's short-circuit trip | 10.36 / 12.04 / 13.87 A filtered | the same | retry every 0.5 s; a hard short in service inside Q7's derated 178.2 A only with the loop's inductance at least 2.08 uH (OPEN, R-134) | L4-E11, out 12 |
| the entry's OV and UVLO | off above 39.6 / 40.36 / 41.22 V; off under 7.46 / 7.66 / 7.95 V | the vehicle source | on again inside the window | L4-E11 3c |
| F1, the vehicle fuse | the 0997010.WXN (58 V DC, drafted); a stiff source's fault at most 900 A by the specified loop | the vehicle lead | replace the fuse | part A, L4-E11 6 |
| the solar backstop | trips at 3.0468 to 3.7408 A, inside 1.087 ms after the filter | the panel (SWEN off) | restarts through the stage's soft start | L4-E7R |
| F2, the panel fuse | 10 A mini blade (Keystone 3568 holder) | the panel lead | replace the fuse | board E as drawn |
| the front end's limits | R11's average and R12's cycle-by-cycle limit (peak 8.06 A, L1 at most 12.6 A) | nothing: they limit, no hiccup | U34 cycles the front end when VIN_RAW falls | L4-E4, L4-E6 |
| U18's outlet OCP | 3.793 to 4.576 A | the USB-C outlet | the PD contract renegotiated | L4-E4 |
| OUTLET_OK | while the PA keys (a key-down at most 60 s) | both outlets | on again when the key ends | HW-FW-CONTRACT FW-A05, FW-A06 |
| the gauge's SCD and OCD | SCD 60 A; OCD1 20 A for 2 s | the pack from VBAT (its FETs) | the gauge's own recovery | pcb_pack_protection.yaml |
| the gauge's OCC | 5 A | the charge path | the gauge's own recovery | pcb_pack_protection.yaml |
| A F1, the pack fuse | 25 A | the pack from VBAT | replace the fuse | board A as drawn |
| F2 SCF9550, the BQ7720700 | the second level drives SCF9550-30-05 self-control fuse (Eaton, 30 A, 4-5 cells) | the pack, for good (a chemical fuse) | none: the pack is replaced | pcb_pack_protection.yaml |
| BATOVP and SYSOVP | BATOVP 17.64 V; SYSOVP 19.0 to 20.0 V | U3's switching | U3 resumes | SLUSE66A via this record |
| the charge FET opening mid-charge (a designed event) | U3's voltage loop holds VBAT; BATOVP stops switching | nothing: VBAT reaches 20.135 V at a fifth of the capacitance (ASSUMPTION), under the TPS2596's 21 V | the charge resumes when the FET closes | this record out 7 |
| the vehicle input reversed (-36 V) | D10 does not conduct; the LM74700-Q1 and Q1 block | Q1 sees 66.15 V (the raised ceiling plus the reversed input) against the CSD19532Q5B's 100 V (the drawn 60 V part fails: NOT MET as drawn) | none needed | part A (R-17, drafted) |
| a disturbance (M2 CS101, M3 CS114, M7) | the entry's OV stays off above CS101's peak at 36 V; the solar input stays under D4 | the OV minimum 39.6 V; the solar input at most 27.82 V; the backstop's filtered ripple 0.0585 A against 0.113 A | no trip, no upset (CONDITIONAL on the loop's typical rows) | part A, L4-E7R (D-01, D-02) |
| a short behind F1 from a weak source | F1's long-time band | every element of the interconnect at least 20 A continuous where installed (D-06, CONDITIONAL on the makers' ratings) | replace the fuse | L4-E11 6 (R-129 to R-132) |
| U2's single faults (Q2 short, FB open) | nothing: VBUS20 follows VIN_RAW past U3's 32 V | no clamp on VBUS20 | S-111's decision is open (R-48) | s120 11 |
| U5's regulation failing | the backstop on SWEN | trip at most 3.7408 A | the stage restarts; a fault defeating both is Layer 8's analysis (R-100) | L4-E7R |

### 4f. Thermal management: the hold, the heater, the fans

| Thermal | What acts | The figure | Record |
|---|---|---|---|
| the margin hold (E5) | off board D, the PA rail, the RockBLOCK, the LoRa module, both E72 and the Geiger module; the running module idled; the charge held | trigger 68.65 C of mixed air plus the calibrated offset (the reference within +-0.899099 K); restore 5 K under after 30 minutes (PROVISIONAL) | L4-E12 6 (R-138, R-139) |
| C1, module shedding | normal to the reduced mode, reached again to the heat stage | inside air +50 C or any cell +55 C; restores 5 K below | CONOPS 4 |
| the SGP41's own shutdown | its load switch from board E's controller | off at 54.0 C on the TMP117, used at or under 49.0 C; the lag assumed 61 s (R-139) | L4-E12 6 |
| the pack heater | the mat on U22/U33 at 12.0 V; UTC holds the charge FET until the block warms | warm before charge below -10 C at the cell; 1.6 Wh to T1 from -20 C (the HL18650V class) | FW-A13, L4-E10 14b |
| the fans | two mixers on board E from the inside climate; each running slot's cooler; a stalled fan reported | the hold's 2 fans 2.010 W; a stall reported within 5 s; with the fans stopped E5's air 72.38 to 85.36 C | FW-E07, V-E07, L4-E12 8b |
| the PA's key-down | the K rules and OUTLET_OK | at most 60 s a key-down, 2 s apart; gates at +55 C cells, +50 C air, +75 C flange | FW-A05, D-11 (PROVISIONAL) |

### 4g. Control dependencies: what still acts if the firmware stalls

| If it stalls | What still acts with no firmware | What does not (not fail-safe) | Record |
|---|---|---|---|
| the panel controller (C:U3) | the charger falls back to 256 mA after its 175 s watchdog; the H3 line, U34, the entry, the backstop, OUTLET_OK, the eFuses, BATOVP and SYSOVP; the RP2040's own watchdog restarts it | the margin hold (E5's +70 C class goes unprotected); the key-down time limit (OUTLET_OK still drops the outlets); the expanders keep their last outputs | HW-FW-CONTRACT FW-A03, FW-A05, FW-A08; L4-E12 |
| the sensor controller (E:U10) | the gauge stops charging after its host watchdog's 10 s; the gauge's protections and the second level act alone; the RP2040's watchdog restarts it | the mixer fans' control (a stopped fan is the fans-off case, 72.38 to 85.36 C in E5); VIN_MON for FW-A16's diagnostic; the SGP41's switch | HW-FW-CONTRACT FW-E01, FW-E07, FW-E09 |
| both controllers | every hardware limit of 4e acts; the source bound holds with no firmware (the H3 line and the knee) | the charge ranges relayed from the gauge (UTC still holds the charge FET); the hold; the heater's policy | this record out 7 |
| the gauge's own firmware | the BQ7720700 and F2 (hardware) | COV, CUV, OCD, SCD and the temperature limits, which are the gauge's | pcb_pack_protection.yaml |

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
17. **U-03 moved from the choices into the register as PANEL-ACC** (update round 3). *Why:* L4-E13, accepted, shows route 2
   feasible on a unit equal to the typical rows and REQ-016's window, the stage, its hold and its 100 W control unchanged, so
   what remains decides a unit (a purchase and a measurement), not the topology or the source class; criteria 1 and 5 name only
   the choices that can still overturn the architecture. Its row stays in 7b with its class so the move is visible. **J_SOLAR's
   rating amends LH-02 and adds no handover row:** it is a property of the existing interface IF-EXT-DC (its `current.solar`),
   whose envelope changes to PANEL-ACC's three cases (3.987, 8.1817 and 13.82 A); no interface is created. **R-29 moves to A-3(b)'s
   8.1817 A:** the shrouded AWG 18 row's 7 A no longer covers SunPower's own 1.25 allowance, so the lead goes to AWG 16 on the
   standard header (10 A). *Reversed by:* route 2 found infeasible with route 1 still closed (L4E13-06), which returns U-03 to an
   architecture-level choice.

## 7. The closure gate

The gate's rule, held by the script (out 9) and by `test_l4e9.py`: a criterion reads PASS only on interface rows that read
MEETS, never on an ASSUMPTION, CONDITIONAL or PENDING row; never while an unresolved choice it names stands; and criterion 2
never while a material defect is open. Every feasibility claim below cites its evidence by class; the software tests establish
tested behaviour of the record's own scripts and drafts only, never an electrical or thermal property.

| Criterion | Evidence | Verdict | The exact constraint (if not PASS) | Could it overturn the architecture? |
|---|---|---|---|---|
| 1. One architecture selected; its mandatory functions have a defensible feasibility basis | A1 under D-06 (section 1); rows IF-02, IF-04, IF-05, IF-07, IF-09, IF-10, IF-11, IF-12, IF-13: REQ-014 (the pack), REQ-015 (IF-04 to IF-06, MAKER and INFERRED; at 9.00 V at the plug with no usable pack U-04's CONDITIONAL CANDIDATE), REQ-016 (IF-01, IF-02, CONDITIONAL and MODELED; the panel PANEL-ACC, L4-E13), REQ-017 (IF-12, IF-13), REQ-018 (IF-10, IF-14), REQ-045 (section 5, D-06 resolved in design), REQ-046 and REQ-077 (IF-10, L4-E10), REQ-075 (IF-09); the electronics at the margins (IF-11, L4-E12); choices U-01, U-02 and U-04 (U-03 moved downstream, update round 3), each restated by its dependency round (L4-E10, L4-E12 and L4-E11, update round 5, out 14) | CONDITIONAL | the solar function's 100 W bound is CONDITIONAL on G_CM and U18's VIN+ bias (L4-E7R) and its panel on PANEL-ACC (U-03, a CONDITIONAL DOWNSTREAM UNIT SELECTION since L4-E13: no unit bought or measured, R-35); REQ-015 at 9.00 V at the plug is a CONDITIONAL CANDIDATE on E11-05, E11-06, E11-09, E11-22 and E11-23 (U-04; L4-E11's dependency round, check 4 at f1856bfd, leaves TI's D1 and D3 deciding it); the electronics at the margins are CONDITIONAL on T-H1 at or over 2.159 W/K and L4-E12's conditions (U-02; L4-E12's round, check 4 at c933724e, states the basis, the fans and T-H1's procedure); the battery path's thermal design is FEA-008's (U-01; L4-E10's round, check 4 at e464ff88, states the limits by mode, the charge drafts and the usable energy); PS-ALLTX's chain at 18 A for 60 s (PWR-F12) is an open obligation | possibly, on named evidence only: U-01 on the HL18650V's signed specification (D-06's pack energy, protection settings and charge ranges), U-02 only on a T-H1 reading under E3-O's floor with the session's fallbacks (1.399 W/K: the sealed case's thermal design or a device-set re-pick, the owner's), U-04 on TI's D1 or D3 (the charger's power path); the rest, the panel unit included, resolves by a value, a part or a measurement on the same topology |
| 2. Material power-path defects have engineering resolutions and bounded supporting calculations | rows IF-01, IF-02, IF-04, IF-05, IF-13; defects D-01 to D-09 below (none open: D-06 resolved in design by L4-E11, D-07 and D-09 superseded by the replacement of the LM5069, the rest drafted or bounded with their conditions named); E11-19 in out 12a; the dependency rounds add none (out 14) | CONDITIONAL | no material defect is open: D-01 to D-05 and D-08 are resolved in design (drafted or bounded), D-06 is resolved in design by L4-E11's interconnect with its evidence items (E11-10 to E11-16), D-07 and D-09 are superseded by the replacement of the LM5069 (E11-19 finds no new one); the resolutions rest on CONDITIONAL rows (the loop's typical rows, the makers' installed and short-time ratings, R227's pulse rating, the start into a hard short's transconductance bound) and the hot short in service on open evidence (the loop's inductance, E11-20); the dependency rounds add no defect: L4-E11's D9 and D10 are the entry's delay and transconductance rows already CONDITIONAL here, and E11-24 is U-04's fallback, a register row (R-152), not a defect's resolution | no: each resolves by a part, a rating or a measurement at the vehicle or the solar entry |
| 3. Remaining assumptions are explicit, with their impact and verification method | section 8's register A-01 to A-30 | PASS |  |  |
| 4. Downstream implementation changes, layout constraints and tests have named owners and acceptance criteria | `DOWNSTREAM-REGISTER.md`: 146 items, each with one owner and an acceptance, among them L4-E11's E11-01 to E11-26 (deduplicated), L4-E10's and L4-E12's items, PANEL-ACC (R-35, R-52, R-148, R-149), L10's own assignment (R-120, R-121), M2 (R-122), the dependency rounds' rows (R-150 to R-154) and the findings ledger's (R-155, R-156; R-102 and R-139 extended); the release order (L4-E6's R12 before L4-E8's ballasts; L4-E11's entry draft after this record's hot-swap draft); `LAYER5-HANDOVER.md` LH-01 to LH-11 | PASS |  |  |
| 5. No unresolved uncertainty could overturn the selected architecture while described merely as routine later testing | rows IF-09, IF-10, IF-11; choices U-01, U-02 and U-04 below, each with its exact question, its evidence by vendor, physical and owner, who supplies it, its fallback with its numbers and what it could overturn (update round 5, out 14); U-03 a downstream unit selection since L4-E13 | CONDITIONAL | three unresolved choices could overturn it and are named as such, not as later testing, each with its question, evidence, supplier and fallback stated by its dependency round: U-01 (FEA-008's cell: the signed specification and the owner's two items; L4-E10, check 4 at e464ff88), U-02 (MESHSAT-1478: T-H1 at or over 2.159 W/K by the drafted procedure, the session's fallbacks down to 1.125 W/K in E5 and 1.399 W/K in E3-O, the owner's below E3-O's floor; CFL-002 the owner's question; L4-E12, check 4 at c933724e), U-04 (TI's D1 and D3; E11-24 takes D2 and D5 off TI; L4-E11, check 4 at f1856bfd); an owner and an acceptance criterion do not close them. U-03 left this category with L4-E13's acceptance: a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC, R-35) that decides which unit, not the topology or the source class | yes, on named evidence only: U-01 (D-06's pack energy and settings), U-02 (only below E3-O's floor: the sealed case's thermal design or the device set), U-04 (TI's D1 or D3: the charger's power path); U-03 no longer can, unless route 2 proves infeasible with route 1 still closed (L4E13-06) |

**Layer 4's power architecture closes: NO** (criteria 1, 2 and 5). Two categories, kept apart below: the material defects (7a,
none open since the update round) and the unresolved choices that could overturn the architecture (7b, three since update round
3: U-01, U-02, U-04; U-03 moved downstream as PANEL-ACC); the downstream tasks (7c) and the owner's items (7d) are neither.
**The reason it stays not closed, on this record's own reading:** criteria 1 and 5 cannot read PASS while U-01, U-02 and U-04
stand, and each can still overturn part of the architecture on named evidence (7b); criterion 2 has no open defect but its
resolutions rest on CONDITIONAL rows with named evidence, so it reads CONDITIONAL, not PASS; nothing L4-E13 settled changes
either reading, since U-03 was never what held criterion 2 and its move leaves three architecture-level choices in place.
**Update round 5 leaves the reading as it was:** the dependency rounds state each choice's question, evidence, supplier and
fallback, and none is yet answered by a held document or a measurement (U-01 waits on the signed specification, U-02 on T-H1,
U-04 on TI's D1 and D3); they add no material defect (out 14).

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

### 7b. The unresolved choices that could overturn the architecture (no owner closes them), and U-03 moved downstream

| Choice | Class | What | The exact unresolved question | The present state (the exact constraint) | The evidence: (vendor) / (physical) / (owner) | Who supplies it | The fallback, with its numbers | What it could overturn |
|---|---|---|---|---|---|---|---|---|
| U-01 | ARCHITECTURE-LEVEL CHOICE | FEA-008: the battery path's cell and thermal design (L4-E10, final) | does the HL18650V class's signed product specification confirm the rows D-06's pack needs, which L4-E10 holds only on the maker's product page (MAKER-PAGE: unsigned, no test conditions): the idle hot limit (+80 C, the 30-day storage row), storage at -33 C, each storage row's state of charge and recovery, charge below 0 C, the charge current from +10 C (at least 0.357C), continuous discharge (at least 6.0 A a cell for PS-ALLTX), the end voltages and the minimum capacity? | LO-01d to LO-01g (E3-O, E5, E3-S, E4-S with the pack fitted) have no route that holds on held evidence; LO-01a holds only with T-H1 at least 1.666 W/K in both lid states (1.8058 W/K with L4-E8's ballasts counted, L4-E12). L4-E10's dependency round (check 4 at e464ff88) states the limits by mode and drafts the charge for the 4S3P, never applied: 0.84 A to 16.40 V from T1 -9 C, 1.68 A to 16.80 V from T2 1 C, the drawn 3.00 A to 16.80 V from T5 11 C to T3 42 C, UTC -9.0 C, the kit's hold below -7 C; usable energy 90.2 Wh (2.11 h) against the 35E's 107.9 Wh (2.52 h) at +25 C, 16.4 % less; at the cold end only brackets (45.1 to 69.6 Wh with the cells at -5.52 C, 37.2 to 54.1 Wh from a cold start at -20 C, ASSUMPTION) | (vendor) Yichun Topwell Power's signed product specification answering the drafted request's ten questions (the storage rows with their charge and recovery, the basis with the rest at high charge, the gauge's data, the cold charge band and termination, the pulse current, the cold capacity, the end-of-life capacity and self-discharge); Eaton's statement on F2 above +60 C and in storage (R-103); (physical) T-H1 in both lid states (R-104, R-151); with the cell chosen, L4-E10's margins re-run on the signed rows (1.06 K under H1 and 0.97 K under U2's INFERRED trip at LO-01e) and each LO row's TEST-PLAN run with the pack fitted (R-47, R-109); (owner) send the request (OW-2); once the specification confirms, approve the cell change inside D-06's 4S3P (about 145 Wh to about 121 Wh nominal, REQ-046 and REQ-077 restated with the cell, about USD 42 a pack; OW-3); if declined, LO-01d to g stay a release gate | the maker, through the owner, who sends the request; Layer 6 components files it (R-103); the session re-runs L4-E10's margins (R-47); the prototype bench runs T-H1 and the LO rows; the owner approves the cell | with no answer, U-01 stays a release gate and every row CONDITIONAL (no ruling needed). With a narrower signed figure, at L4-E10's thresholds: an idle limit under 78.94 C makes H1 act in E5's dwell, under 74.73 C E5's cells pass it, under 73.07 C E3-O loses its 'no shutdown', under 71.00 C E3-S fails, under 68.86 C E3-O's cells pass it; E3-O and E5 then fall back to (I)'s cooler (8.18 to 35.21 W into the sealed case, INCONCLUSIVE) and E3-S to requirement change A (the owner's); storage warmer than -33 C to (III)'s primary-fed heater (470 to 940 Wh of added storage, an owner's ruling under D-06) or requirement change A; continuous discharge under 6.0 A a cell back to (I); the charge current, the end voltage and the capacity (3.22 Wh per 100 mAh a cell) move energy, not the architecture; or the 35E kept with (I), or a requirement change (the owner's, D-29) | on the specification's answer: D-06's pack energy (16.4 % less usable, 90.2 against 107.9 Wh at +25 C) and the pack's protection settings and charge ranges under (II); with a narrower idle limit and no requirement change, (I)'s powered cooling (up to 35.21 W into the sealed case) would reopen U-02's heat budget, and a narrower storage floor would add 470 to 940 Wh of primary storage under D-06; the power path's topology stays |
| U-02 | ARCHITECTURE-LEVEL CHOICE | MESHSAT-1478: the electronics against the inside air at D-02a's +55 C margin and E5's +60 C dwell (L4-E12) | does the sealed Peli 1450 with its 3 mm plate, lid open with the fans, conduct at least 2.159 W/K: E5 under the hold puts 21.587 W into the case (19.497 W and L4-E8's 2.09 W of ballasts) across the 10 K from E5's +60 C dwell to the +70 C class, at 0 K of margin, with fans whose power and operating range are not yet known (D-18 open)? | L4-E12's route (c), E3-O as stated and the hold in E5 only, is CONDITIONAL on T-H1 lid open with the fans at or over 2.159 W/K (E3-O alone 1.806 W/K; 2.709 W/K with no hold), the hold's reference within +-0.899099 K of the mixed air, the parts out of the cooler's exhaust, the fans' rating (D-18), the pushbuttons and two regulators changed and PDi's statement; at the line E3-O's air is 67.55 C and E5's 70.00 C, while the design as it stands (LO-01a's floor, no hold) reaches 76.25 C in E5; L4-E12's dependency round (check 4 at c933724e) counts the fans in the energy budget (pwr_budget.py's rows, tier R), and their picked power moves the line 0.100 W/K per W (2.071 to 2.333 W/K over the representatives); inside the envelope no location holds the SGP41 to its maker's conditions (CFL-002) | (vendor) D-18's picked fans: the maker's power at the duty the controls set and an operating range covering -20 C to the inside air (REQ-043; no held sheet gives a fan's operating temperature; R-142, R-150); PDi's and Sensirion's answers; (physical) T-H1 by the drafted procedure (T-H1-PROCEDURE-DRAFT.md, R-151): an empty Peli 1450 with the 1450PF frame and a plate blank, heaters spread as E5's hold, eight points (two powers, both lid states, fans on and off), 29 to 84 h; it passes only if the reading less its expanded uncertainty (k = 2, 10.7 % at a 10 K rise) reaches 2.159 W/K, so a reading of at least 2.416 W/K at a 10 K rise (2.285 W/K at 20 K) on the assumed budget, which the bench replaces with its own; the forced hold and the SGP41's shutdown at room temperature, its lag measured (R-138, R-139); then E3-O and E5 with thermocouples on the +70 C parts (R-104, R-109); (owner) authorise T-H1's bench (its purchase; a chamber run at +60 C only if wanted, his spend; OW-8); CFL-002 (OW-1); send PDi's and Sensirion's requests (OW-4) | the prototype bench, as Layer 9's physical verification, once the owner authorises it (the session cannot run it); Layer 6 components for D-18's pick (R-142, R-150); the makers, through the owner | the session's, inside the rulings (no vent, the Peli 1450 kept): F4, the RockBLOCK, board D and the LimeSDR on pads to the plate, holds E5 down to 1.564 W/K and E3-O down to 1.399 W/K (1.309 W/K with the +80 C connectors out of the exhaust); F3, a deeper hold in E5 that keeps the logging (13.429 W into the case), holds E5 to 1.552 W/K; F4 with F3 holds E5 down to 1.125 W/K, with no owner ruling and no change to E3-O; F1, fins on the plate, multiplies a reading by 1.125 to 1.131 (outside, twice the area) or 1.252 to 1.363 (both faces); the H5007NL, the ATP16 and the PXP4043/C take wider parts or makers' statements (R-141). Below E3-O's floor (1.399 W/K) the remaining option is the owner's: a deviation of E3-O's configuration (the hold in E3-O) or a device-set re-pick (CHO-001) | on T-H1's reading and the fans: from 2.159 W/K down to E5's 1.125 W/K and E3-O's 1.399 W/K the session's fallbacks hold and the architecture stays; under E3-O's floor the sealed case's thermal design (no vent, the ruling of 7 September 2026) or the device set (CHO-001) could change, the owner's; a stopped fan puts E5's mixed air at 72.38 to 85.36 C on W4's still values, the parts coupled to the plate at most 69.82 C; CFL-002 changes a sensor, not the architecture; never the power path's topology |
| U-03 | CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC) | O-1: the solar panel inside REQ-016's window (L4-E13, accepted) | which physical unit is inside REQ-016's window: a unit measured to PANEL-ACC and accepted on A-1 (Vm20 plus U_V at most 25.000 V at -20 C and 1000 W/m2), A-2 (at least 1.365591 W) and A-3(b); not whether the window can be met, which L4-E13 shows on a unit equal to the typical rows | L4-E13 (accepted, checks 3 and 4 at fae419d1 and 33b6b7be): route 1, a maker's warranted band, closes nothing today; route 2, one identified SunPower SPR-E-Flex-100 measured against A-1 to A-3, is feasible on a unit equal to the typical rows: A-1 Vm20 + U_V 24.1505 V against 25.000 V at -20 C and 1000 W/m2 (margin 0.8495 V), the window Voc25 20.315 to 22.156 V; A-2 27.0849 W above 1.365591 W; A-3 (a) 3.987 A, the conservative bound over L4-E7R's regulation (2.5485 A nominal, at most 2.9337 A at 25 V) and backstop (trip at most 3.7408 A), (b) 8.1817 A, (c) 13.82 A, a COMPONENT_LIMITATION on J_SOLAR and PV_IN; A-4 on L4-E7R's two layers (the regulation's 25 V corner 73.3436 W; the backstop's static bound 93.5521 W, CONDITIONAL on G_CM and the VIN+ bias); no physical unit accepted | (vendor) route 1, a maker's warranted Voc band inside the window (the drafts to SunPower and Solbian, OW-4); it closes nothing today; (physical) one unit bought, recorded by serial number and measured (M1 to M3 and A-2's reading at the specification) and accepted on A-1, A-2 and A-3(b) (R-35); its trace rerun (R-52); J_SOLAR and PV_IN with a rating that covers A-3(c) (R-148); M3's n at or under 2 for the disturbance check (R-149); L4-E7R's regulation and backstop applied (drafted) for A-3(a) and A-4; (owner) the purchase and the measurement of one unit (OW-6) and sending the two route-1 drafts (OW-4): actions, not questions | the owner (the purchase, the two drafts sent); the measurement to the specification under his authority; Layer 6 components (PANEL-ACC's acceptance R-35, J_SOLAR and PV_IN R-148, M3's n R-149); the makers, if they answer | another unit of the same curve shape inside the window; route 1 if a maker warrants a band; REQ-016's window restated (the owner's; not needed) | nothing of the architecture: it decides which unit, not the topology and not the source class; REQ-016's window, the stage, its hold and its 100 W control stay; it returns to an architecture-level choice only if route 2 proves infeasible with route 1 still closed (L4E13-06) |
| U-04 | ARCHITECTURE-LEVEL CHOICE | source-only and dead-pack operation (L4-E11: arrangement (A), a CONDITIONAL CANDIDATE) | does the BQ25731 regulate VSYS at ChargeVoltage with no battery current (D1: without it arrangement (A) cannot run state S4), and what does it regulate with the charge inhibited (CHRG_INHIBIT = 1 or ChargeCurrent 0) and no battery current (D3: REQ-077's hold in every state and R-a's S2)? The held datasheet (SLUSE66A) states neither as a behaviour of the part | L4-E11 selects arrangement (A), the drawn charger with no battery FET, with rules R-a to R-d and the replaced entry: at a 9.00 V plug the source delivers 29.09 to 42.52 W at VBAT and the shed warm-up (28.12 W plan) is carried with 0.98 W in hand while P1 stays at most 20.51 W; REQ-015 at 9.00 V at the plug is a CONDITIONAL CANDIDATE, not closed: at the load's hi corner P1 (35.24 W) exceeds the source's least, TI states neither VSYS's regulation with no battery current (D1) nor what it regulates with the charge inhibited (D3, Q-TI-3), the cells' warming time has no held model, and R-b's cases (ii) and (iii) are INCONCLUSIVE (D8, D7); L4-E11's dependency round (check 4 at f1856bfd) maps every specification left to a maker to its claim (D1 to D10) and narrows the dependence on TI from D1, D2, D3, D5 to D1, D3; ChargeCurrent at POR is 256 mA (TI's E2E answer), under R-b's bound | (vendor) TI's statements of D1 and D3 as behaviours of the part, or a datasheet revision (Q-TI-11 and the addendum to Q-TI-3 in clarification/TI-QUESTIONS.md, with REVIEW-REQUEST.md's Q-TI-2 and Q-TI-3); D2, D4 and D6 to D8 from TI too, D9 and D10 from the entry's makers (Q-TI-12 to Q-TI-14); an answer stated as a limit settles a row production-wide, a typical figure does not (R-114); (physical) one bench sample per row (R-153): for D1 the mode on that silicon revision, where VSYS needs 12.3 V against ChargeVoltage's floor 16.716 V (a 4.416 V margin once the mode is shown); for D3 the mode with the bit set and with ChargeCurrent 0; evidence for that unit and revision, never a production-wide bound; R-85 extended at the plug (E11-06) and E4-O's warm-up (E11-23, R-137); (owner) send TI's questions (REVIEW-REQUEST.md with TI-QUESTIONS.md; OW-7); a change to REQ-077's acceptance only if both the bit and ChargeCurrent 0 fail D3 | Texas Instruments, through the owner (E2E or TI support); Layer 6 components files and judges the answers (R-114); the prototype bench runs the one-sample methods (R-153) and R-85 | for D2 and D5, E11-24 (the session's, a register row, R-152): one EEHZK1V181P directly on VSYS and a hold-up bank of four EEHZK1E471P charged through R_CH 330 Ohm and discharging through D_H, a B540C-13-F: 54.07 mJ, 1.117 ms of hold for the worst admitted step (the USB-C PD outlet, 48.39 W) over the 1 ms assumed, the bank charging at 51.2 mA at most (0.864 W in a 1 W part); D4 and D6 to D10 have remedies inside (A). For D1 and D3 there is none inside (A): a negative answer returns (B), a charger whose battery FET regulates VSYS by design (an architecture change; five records reopen); for D3 alone, a change to REQ-077's acceptance (the owner's); (C), a precharge path, answers D6 only | on TI's D1 or D3, or a bench sample showing the mode absent: the charger's power path, to (B) with a battery FET; D2 no longer can once E11-24 is fitted, within its 1.117 ms and CONDITIONAL on the 1 ms that D2's bench reading turns into a margin; the efficiency, the pin's band or P1's load move the knee or F1, not the topology |

**Whether each can still overturn the architecture, and on exactly what (update round 5):** U-01 yes, on the HL18650V's signed
specification (D-06's pack energy, its protection settings and charge ranges; a narrower idle limit or storage floor with no
requirement change would bring (I)'s powered cooling, up to 35.21 W into the sealed case, or (III)'s 470 to 940 Wh of primary
storage); U-02 yes, but only on a T-H1 reading under E3-O's floor of 1.399 W/K: from 2.159 W/K down to E5's 1.125 W/K and
E3-O's 1.399 W/K the session's fallbacks F4 and F3 hold with no owner ruling, and below it a deviation of E3-O's configuration or
a device-set re-pick is the owner's, while CFL-002 changes a sensor and not the architecture; U-04 yes, only on TI's D1 or D3
(the charger's power path, arrangement (B)), since E11-24's hold-up takes D2 and D5 off TI and D4 and D6 to D10 have remedies
inside (A), while the efficiency, the pin's band or P1's load move the knee or F1 and not the topology. **U-03 no longer can** (update round 3): L4-E13 makes it a CONDITIONAL DOWNSTREAM
UNIT SELECTION (PANEL-ACC) that decides which unit, not the topology and not the source class; REQ-016's window, the stage, its
hold and its 100 W control stay; it would return to this category only if route 2 proved infeasible with route 1 still closed
(L4E13-06). Its row stays in the table, with its class, so the move is visible; criteria 1 and 5 no longer name it.

### 7c. The downstream implementation and verification tasks (criterion 4)

`DOWNSTREAM-REGISTER.md` (section 9): an owner and an acceptance criterion close the ASSIGNMENT, not the item. The items that
exist only under a choice's outcome are marked there (Order "U-01"), and the items that carry a choice's evidence say so
("U-02"); none stands in for a choice.

**What closure needs, exactly:** U-04 settled by TI's D1 and D3 (R-114 with TI-QUESTIONS.md, E11-05, E11-25), with E11-06
(R-85 extended), E11-09 (the knee drawn), E11-22 (R-b's cases), E11-23 (the warm-up time), the one-sample bench rows (R-153)
and E11-24's hold-up for D2 (R-152); U-02 settled by T-H1 by its drafted procedure (R-151, R-104) at or over 2.159 W/K with the
picked fans (R-142, R-150), the forced hold and the SGP41's shutdown with its lag (R-138, R-139), the parts' readings in E3-O
and E5 (R-109) and the owner's answer to CFL-002, or by the session's fallbacks down to 1.125 W/K in E5 and 1.399 W/K in E3-O;
U-01 settled by its evidence (the signed specification, R-103, R-47) and the owner's two items (or held open as a release
gate), its charge drafts applied only under (II) (R-154); D-06's CONDITIONAL parts by the makers' ratings and F1's clearing I2t (R-113, R-115, R-129 to R-132) and the
four-wire loop (R-130); the hot short in service by the loop's inductance (R-134); and for criterion 1 the CONDITIONAL inputs
with their named evidence (G_CM and U18's VIN+ bias R-101, PWR-F12 R-46 and R-83, C-7, C-3, C-5, V-A07). The coordinator decides
whether a CONDITIONAL criterion with these named is acceptable for Layer 4's closure; this record does not.

### 7d. The owner's items (decisions and outside contacts only; the session contacts no outside party)

Kept apart from the engineering work above: each is a decision only the owner takes, a text only the owner sends or an
action under his authority (a purchase, a bench's authorisation): actions, not questions. The script reads each document at its
pinned sha256 (out 9 (c)). Update round 5 adds OW-7 (the TI request: REVIEW-REQUEST.md with TI-QUESTIONS.md) and OW-8 (T-H1's
bench authorisation), and OW-2's request carries ten questions.

| Item | The decision or action | The document (path, where, sha256/16) |
|---|---|---|
| OW-1 | CFL-002 (U-02): the SGP41 in the battery bay against REQ-042's VOC channel inside the envelope: A, a BME688-class sensor in its place (L4-E12's recommendation); B, the VOC channel dropped; C, the SGP41 kept, its channel reported as not covered above a 49.0 C reading and after storage outside 5 to 30 C | L4-E12's page, section 8: `v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md`, at `c933724e`, e1aaf1c4562cecb6 |
| OW-2 | U-01, item 1: send the drafted request for the HL18650V's signed product specification (Yichun Topwell Power), ten questions since L4-E10's dependency round (7 to 10 added: the cold charge band and termination, the pulse current, the cold capacity, the end-of-life capacity and self-discharge) | Yichun Topwell Power: the HL18650V's signed specification, ten questions (U-01): `v2/docs/records/l4e10/clarification/topwell-hl18650v.txt`, at `e464ff88`, 1ca762d83bbb58b2 |
| OW-3 | U-01, item 2, once that specification confirms L4-E10's rows: approve the cell change inside D-06's 4S3P (about 145 Wh to about 121 Wh nominal, REQ-046 and REQ-077 restated with the cell, about USD 42 a pack); if declined, LO-01d to g stay a release gate | L4-E10's page, section 8: `v2/docs/records/l4e10/L4E10-CELL-THERMAL.md`, at `e464ff88`, 576dbf0ac06bcd7a |
| OW-4 | the other outside-contact drafts to send (the owner chooses the channel; Topwell's is OW-2, TI's OW-7) | Pervasive Displays: the E2370KS0C1's storage and operation (U-02): `v2/docs/records/l4e12/clarification/pervasive-displays-e2370ks0c1.txt`, at `a86be47b`, 4f7db1348cc0b4ac; Sensirion: the SGP41's duration, recovery and storage (U-02, CFL-002): `v2/docs/records/l4e12/clarification/sensirion-sgp41.txt`, at `a86be47b`, 43c47549235fe6e8; Analog Devices: the LT8705A's IMON_IN limits (the 100 W bound; R-33, R-101): `v2/docs/records/l4e7/clarification/analog-devices-lt8705a.txt`, at `675b8068`, 97d8217092eae7ac; Milliohm: the HoJLR2512's temperature coefficient below +25 C (R-101): `v2/docs/records/l4e7/clarification/milliohm-hojlr2512.txt`, at `675b8068`, e920420419a677e0; Vishay: the WSL2512's pulse capability (R-101): `v2/docs/records/l4e7/clarification/vishay-wsl2512.txt`, at `675b8068`, 0d91a42dfa59432b; Texas Instruments: the INA169's error envelope (R-101): `v2/docs/records/l4e7/clarification/texas-instruments-ina169.txt`, at `675b8068`, 405fb3988f41d8ac; Eaton: the SCF9550 above +60 C and in storage (PWR-F12; R-103): `v2/docs/records/l4e10/clarification/eaton-scf9550.txt`, at `79b2f568`, 9dffb95e8b4874fc; SunPower (the module's maker): a warranted Voc band at STC for the SPR-E-Flex-100 (U-03's route 1): `v2/docs/records/l4e13/clarification/sunpower-spr-e-flex-100.txt`, in the tree, 453a5a957648a322; Solbian: a warranted Voc band for the SX 156 (U-03's route 1): `v2/docs/records/l4e13/clarification/solbian-sx-156.txt`, in the tree, fb66bfb76e7e252c |
| OW-5 | the fallbacks, to send only if T-H1 reads under 2.159 W/K (L4-E12) | Ground Control: the RockBLOCK 9704: `v2/docs/records/l4e12/clarification/ground-control-rockblock-9704.txt`, at `a86be47b`, 738245875bec70c5; NiceRF: the SA868: `v2/docs/records/l4e12/clarification/nicerf-sa868.txt`, at `a86be47b`, 92324668c17d4f6c; Bulgin: the PXP4043C: `v2/docs/records/l4e12/clarification/bulgin-pxp4043c.txt`, at `a86be47b`, c7accd3dd6dc1d89 |
| OW-6 | PANEL-ACC (U-03, L4-E13): buy one SunPower SPR-E-Flex-100, recorded by serial number, and have it measured to the specification (M1 to M3 and A-2's reading); actions under the owner's authority (money), not questions | L4-E13's page, PANEL-ACC: `v2/docs/records/l4e13/L4E13-PANEL.md`, in the tree, 1c7f11716db4c2f2 |
| OW-7 | U-04: send TI the battery packet's questions (REVIEW-REQUEST.md section 4, Q-TI-2 and Q-TI-3 above all) with L4-E11's TI-QUESTIONS.md (Q-TI-11 to Q-TI-14 and the addendum to Q-TI-3, each tied to its row D1 to D10; Q-TI-2 partly answered on E2E, the POR value 256 mA); D1 and D3 decide U-04 (E11-05, E11-25; R-114); an action, not a question | Texas Instruments: the battery packet: `v2/docs/review-packets/battery/REVIEW-REQUEST.md`, in the tree, 91a257430cbeb53a; Texas Instruments: the dependency round's questions: `v2/docs/records/l4e11/clarification/TI-QUESTIONS.md`, in the tree, 2789ce47a4e81fb6 |
| OW-8 | U-02: authorise T-H1 on the bench, its purchase (a current-moulding Peli 1450 with the 1450PF frame, a 3 mm plate blank, the heaters, the fans as stand-ins until D-18, a second PicoLog TC-08) and who runs it; a chamber run at +60 C only if wanted, at a laboratory, his spend; the procedure is drafted and the session cannot run it (R-104, R-151); an action, not a question | T-H1's procedure, drafted: `v2/docs/records/l4e12/T-H1-PROCEDURE-DRAFT.md`, in the tree, 07b94e2ff18647a1 |


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
| A-16 | The panel at its typical rows (PANEL-ACC's unit, none bought or measured; L4-E13's demonstration), SC-37's mean day | IF-01, the endurance | the solar energy (344.0 / 336.6 / 307.9 Wh a day at L4-E7R's accepted regulation); a unit at A-2's floor gives 52.3 Wh at the conditioned upper corner against the rated unit's 240.0 Wh | R-35, R-52 |
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
| A-30 | L4-E13's disturbance check: the junction's ideality at most 2 (a MODELLING_ASSUMPTION) and the plane-of-array irradiance below the threshold, 8574 W/m2 at n 2 (an ASSUMPTION); A-3(c)'s design level 2111.4 W/m2 a SESSION level for a double contingency, not a claimed maximum | IF-01 | above the threshold D4 rises over its 28 V standoff and conducts under 1 mA up to its breakdown; A-3(c)'s current scales with the level | R-149 (M3's n), R-148 |

## 9. The downstream register and the release order (criterion 4)

`DOWNSTREAM-REGISTER.md` holds 146 items, each with one owner, an acceptance, a state and a step in the release order (out 10):
Layer 4 coordinator 9, Layer 5 interfaces 4, Layer 6 components 20, Layer 7 mechanical 5, Layer 8 board A generator owner 13,
Layer 8 board B generator owner 1, Layer 8 board C generator owner 1, Layer 8 board E generator owner 21, Layer 8 board P
generator owner 1, Layer 9 pre-layout analysis 23, prototype bench 36, firmware owner 8, TEST-PLAN owner 3, CONOPS owner 1. By
kind: 53 implementation changes (25 drafted, 17 missing a draft, 11 owed as work, none PENDING), 13 layout constraints, 38
tests, 37 pieces of evidence (R-156 PENDING L4-E7's surge round), 5 release records. They are category (a): 146 items, each
with one owner and an acceptance that
close the assignment, not the item, and none of them stands in for U-01, U-02 or U-04. U-03 is now among them: PANEL-ACC is
R-35 (Layer 6 component selection; the purchase and the measurement the owner's, OW-6), with R-52 (the unit's trace rerun),
R-148 (A-3(c)'s J_SOLAR and PV_IN rating) and R-149 (M3's n at or under 2).

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

**Update round 5** (out 10, out 14): R-150 (L4-E12's drafted fan row, inserted), R-151 (T-H1's procedure), R-152 (E11-24, the
VSYS hold-up), R-153 (E11-26, the one-sample bench rows D1 to D10) and R-154 (L4-E10 section 14's charge drafts, under U-01's
(II)); R-114 restated with TI-QUESTIONS.md (E11-25), so L4-E11's E11-01 to E11-26 are each named in a From column. From the
findings ledger (`records/l4close/FINDINGS-LEDGER.md` at `fnd/l4close` `e1e99c4f`, "Concrete remaining risks"): R-102 extended
to L4-E8's per-can bound (item 8), R-139 with the SGP41's shutdown lag (item 5), R-155 the 7 mOhm fallback's interval bound
(item 10) and R-156 TRN-001's judgement of the panel lead's surge, PENDING L4-E7's surge round (item 1).

**The release order** (the register's own section): release records first (L4-E4's names accepted checks of L4-E4 to L4-E6 and
L4-E8; L4-E7's names L4-E7R's check 4; L4-E11's its check 3), with the text drafts for Layer 5, CONOPS and L4-E5; the missing
drafts; board A in one round with **R12, the ILIM_HIZ network drawn to the corrected knee and U34's R14 first, R11 after them,
the ballasts and Cc2 after R12**, R138 independent, U17's R227 after them; board E in one round with **Q1 and E-F1's capacitor
no later than R10**, R10 and C26/C27 only with board A's H3 line, L4-E7's settings, L4-E7R's backstop, then F1, the hot-swap
settings and **L4-E11's entry on top of them**, F1's 20 A holder and U-02's board E changes; firmware's 4.70 A only on a board A
that carries H3, rules R-a to R-d, the hold and the SGP41's shutdown; the records re-issued; the bench, where V-A07 decides
R11; Layer 7's interconnect and enclosure before the harness and the case are built; Layer 6's panel unit (PANEL-ACC) after the
owner's purchase. The items under U-01's approach (II)
(R-105, R-106, R-110) wait on the owner's approval.

## 10. The endurance statement (out 8; DR-01)

- **Battery only, A1 (the ruled pack):** 107.9 Wh usable at +20 C and 44.5 Wh at -10 C (aged to 80 %): **2.52 h and 1.04 h**,
  short of 48 h by 45.5 h and of 72 h by 69.5 h.
- **Solar-assisted, A1, on the panel at its typical rows** (SunPower SPR-E-Flex-100, PANEL-ACC's unit; none bought or
  measured; SC-37's mean September day; the replay at L4-E7's first-round limit, 350.0 Wh a day, which L4-E13 reproduces for
  the rated unit; under L4-E7R's accepted regulation its nominal hold gives 336.6 Wh, the next bullet's figures; a unit
  at A-2's floor gives 52.3 Wh at the conditioned upper corner against the rated unit's 240.0 Wh): the first interruption at hour **6 or 2**
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
  open): battery only 12.71 h and 5.24 h; on the panel at its typical rows the first interruption at hour 18 or 11 and +979.2 / +1719.7 Wh
  still needed; on the screening stimulus +278.8 / +515.8 Wh. A2 also misses 48 h.
- **Every mandatory function is intended to be delivered, subject to the open conditions named here** (the CONDITIONAL
  resolutions of D-01 and D-06, U-01 to U-04 and the CONDITIONAL rows): battery and solar both feed the kit; the store is inside the case; HF and the tablet are kept
  (the tablet's charge is optional and reduces endurance); the vehicle input runs the kit and charges the pack across 9 to 36 V
  with a working pack (section 3; without one, U-04); PS-ALLTX runs under D-11's floors; both outlets deliver their contracts
  within their protection. No service is reduced to narrow the gap. Software tests establish the record's own behaviour, not
  these properties.

## 11. What stays PENDING, CONDITIONAL or open

- **PENDING:** none in the rows. L4-E7R is accepted (check 4 at `91e9a4b5`); IF-01, IF-02, LH-02, R-21, R-92 and R-98 carry its
  figures. L4-E13 (U-03) is accepted (check 3 at `fae419d1`, check 4 at `33b6b7be` after set 25). In the register, R-156
  (TRN-001's judgement of the panel lead's surge) waits on L4-E7's surge round (the findings ledger's item 1).
- **Unresolved choices (no owner closes them):** U-01 (FEA-008's cell: the signed specification, with the owner's two items),
  U-02 (MESHSAT-1478, CONDITIONAL on T-H1 at or over 2.159 W/K and L4-E12's conditions, the session's fallbacks down to
  1.125 W/K in E5 and 1.399 W/K in E3-O; CFL-002 the owner's question), U-04 (source-only and dead-pack operation, a
  CONDITIONAL CANDIDATE on E11-05, E11-06, E11-09, E11-22 and E11-23, turning on TI's D1 and D3).
- **U-03, a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC):** no unit bought or measured (MISSING_EVIDENCE, the owner's
  purchase, OW-6); n at or under 2 a MODELLING_ASSUMPTION (R-149); the irradiance below the disturbance threshold an ASSUMPTION;
  J_SOLAR and PV_IN for A-3(c) a COMPONENT_LIMITATION (R-148); A-3(a) and A-4 on L4-E7R's regulation and backstop (drafted; the backstop's 93.5521 W CONDITIONAL on G_CM and the VIN+ bias); route 1's
  drafts for SunPower and Solbian unsent (OW-4).
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

## Appendix B. The traces as first written (rounds 1 to 4; superseded in presentation by section 4)

### B1. Simultaneous operation (out 5)

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

### B2. Startup (out 6)

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

### B3. Faults, traced across the stages (out 7, out 11)

| Fault as first traced | What acts, stage by stage | Bound, and its class |
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
