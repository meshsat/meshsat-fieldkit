# L4-E9: Layer 4's connected power design and its closure statement (MESHSAT-1357; consolidated 2 October 2026)

**Status: known defects addressed in drafts; feasibility conditions remain open.** By the owner's corrections of 2 October
2026 (12:00) this is the status phrase while architecture-critical uncertainties remain, never "complete" or "closed"; an
unavailable measurement is never counted as done work.

**Prototype design, desk arithmetic.** Nothing is bought, built, powered or measured, and no board of this set has a layout.
This page edits no generator, registry record, Layer 3 file, `pcb_interfaces.yaml`, `HW-FW-CONTRACT.md` or other record; its
circuit changes are drafts (`apply_gen_sch_e_q1.py`, `apply_gen_sch_e_f1.py`, `apply_gen_sch_e_hotswap.py`, `apply_gen_sch_a_u17.py`, and
L4-E11's `apply_gen_sch_e_entry.py` and `apply_gen_sch_a_guard.py`, which it carries) and its interface
changes are drafts for Layer 5 (`LAYER5-HANDOVER.md`). Every figure below is printed by `l4e9_power_path.py` into
`l4e9_power_path.out` ("out N" is its section), which reads each figure from a generator, a committed netlist, a record's
committed output or a maker's document, each pinned by sha256, and never retypes a figure another record computed. Classes:
MAKER, NETLIST, MODELED, INFERRED, CONDITIONAL (a calculated result on an unwarranted assumption or an open measurement),
ASSUMPTION, PENDING, and SESSION for a choice this record takes.

**Fixed by the owner** (2 October 2026, 11:25; the frame of `OWNER-INSTRUCTION-2026-09-30.md`): battery and solar are
mandatory; HF and the tablet stay; the store is internal to the Peli 1450, no external battery; D-06's 4S3P with the ruled cell
is the baseline and every alternative (A2, the lid pack, the 16.340 V hold, P-03's 200 W, the proposed cell) stays a proposal;
REQ-016 and every other mandatory requirement are preserved; Layer 3 stays closed; 48 to 72 h is an endurance OBJECTIVE,
reported battery-only and solar-assisted separately, with what the tablet's optional charging takes; electrical feasibility
and endurance are separate questions; the approved profile is preserved and any other duty cycle is labelled as such.
Downstream tasks are kept apart from unresolved choices that could overturn the architecture, and an owner does not close a
choice. Layer 4 selects the power architecture and establishes its feasibility; Layer 5 writes the interfaces it creates.

**How the page is built.** Sections 1 to 6 are the consolidated design: one connected diagram, one budget, one change list,
the operating behaviour, the implementation handover and the exit statement against the owner's definition. Sections 7 to 12
carry the analyses and registers they rest on. The inputs of each round and the record's history are in Appendix A; the
traces as first written in Appendix B. Every table of sections 1 to 6 is printed by `l4e9_power_path.py` (out 15 to 21) and
held equal to it by `test_l4e9.py`.

## In short

- **The design.** A1 under D-06: one 4S3P pack inside the case, fed by the panel through board E's LT8705A stage and by the vehicle or shore supply through its ideal diode and the TPS48110-Q1 breaker, ORed onto VIN_RAW, converted once to VBUS20 by board A's LM5176 and once more by the charger onto VBAT, from which every load converter and both outlets run (section 1). The charger is (B1), TI's BQ25730 with the battery FET Q39, drafted (the board as drawn carries the BQ25731). A2 stays a proposal. There is no USB-C input.
- **Electrical feasibility** (apart from endurance): 14 interfaces, 2 MEET, 12 CONDITIONAL, 0 NOT MET, 0 PENDING (1d). IF-01 carries the KNOWN DEFECTS at the solar entry, single faults from L4-E7's panel-lead derivation: D-10, a stiff 36 V source on the port, and D-11, a reversed panel, ADDRESSED IN DRAFTS by L4-E7's selected remedies (the over-voltage cut-off U21 with Q12, the return switch Q13; R-173, apply_gen_sch_e_solar_guard.py, not applied; D-11 CONDITIONAL on Q13's leakage above +25 C), and a residual band between 25 V and the cut-off named for layer 8 (R-175); D-12, CS116 and CS115 on the panel lead, is resolved in the drafted entry with the guard (MEETS with the block on and off). D-01 to D-05 and D-08 are resolved in design, D-06 by L4-E11, D-07 and D-09 superseded (8a); every resolution is a DRAFT or a register row, none applied; the heat into the case per mode against T-H1's binding 2.159 W/K (2c).
- **Endurance** (apart from electrical feasibility; the approved profile 42.8 W kept): battery-only 2.52 h (2.515 h with (B1)'s Q39) (1.73 h with the tablet's window at the start) at room temperature and 1.04 h (1.037 h with (B1)'s Q39) with the cells at -10 C; solar-assisted on the candidate panel's day: first stop at h 6 (06 UTC start) / h 2 (18 UTC start), unserved 1367.4 / 1368.1 Wh at 48 h; the steady load carried 8.0 W at both horizons; with the tablet at most 1.61 W lower (6.4 to 8.0 W). The objective of 48 to 72 h is NOT MET: a deficit of 34.8 W against the profile, +1361.5 / +2094.1 Wh of storage to add; a charger change does not close it. The tablet's optional charging takes at most 38.7 Wh a day. The cold end's solar case is not computed. The proposed cells (PROPOSALS): the HL18650V 2.11 h, the Saft MP 176065 xtd 1.25 to 1.37 h (MODELLED; 2b').
- **The change list:** 63 changes in application order, none APPLIED (DRAFTED 28; MISSING DRAFT 19; OWED 16), each with its board, generator, apply script, dependency and release guard; the release records first (section 3).
- **Thermal feasibility in normal operation** (apart from both; L4-E12's reconciliation, check 7, which withdraws this record's earlier framing of the profile at +40 C): at REQ-024's +40 C the required state is the heat stage, 27.086 W, since C1 sheds the 42.8 W profile and D-02b runs the reduced mode above +35 C. **The owner's CFL-002 decides its line:** with option C (the SGP41 kept powered) K1, the SGP41's +55 C, 1.806 W/K (a bench reading of at least 1.958 W/K), at or over the case's cap at the conservative ends; with option A or B, K3, the +70 C class, 0.903 W/K (at least 0.941 W/K). The profile's own line is K6 at REQ-014's +20 C, 1.447 W/K (at least 1.508 W/K); charging with it running needs 1.627 to 1.977 W/K with the charge path counted, and the solar-assisted runtimes stay conditional on that line. On the conservative bound none of these is shown; T-H1 decides (2c, 2c', section 6).
- **The exit** (section 6, the owner's definition): Layer 4 power closure is not reached on this reading. U-02 is the closure condition T-H1's points decide against the line CFL-002 sets (K1 1.958 W/K with option C, K3 0.941 W/K with A or B); U-04 becomes a downstream qualification test once (B1) is applied and stays a closure condition on the board as drawn; U-01 has a supported route on published evidence (the Saft MP 176065 xtd), pending the owner's adoption, which the evidence does not yet support (five items awaited; the owner's approval required), and the ruled 35E is unsuitable on its own published evidence for the margins. Beside them, the solar faults D-10 and D-11 are addressed in drafts (L4-E7's selected remedies, R-173, not applied; D-11 CONDITIONAL on Q13's hot leakage), the band between 25 V and the cut-off a residual for layer 8 (R-175). Each has its exact missing fact and the smallest experiment or manufacturer clarification that resolves it. The findings ledger: 58 rows, 24 CLOSED, 23 CLOSED AS CONDITIONAL, 11 OPEN DOWNSTREAM, 0 STILL OPEN. **Status: known defects addressed in drafts; feasibility conditions remain open.**

## 1. The selected architecture as one connected design

![The connected power design: sources, protection, conversion, charging, storage, loads and controls](L4-POWER-DIAGRAM.svg)

**The one figure**, `L4-POWER-DIAGRAM.svg`, generated by `l4e9_power_path.py --write-svg` (the script refuses to run when the
committed file is not what it generates; out 15). Every source is traced through protection, conversion, charging and
storage to the loads; each power edge carries its interface row (1d), each block its settings and limits, and the blue
tags are the control edges of 1c: which controller, gauge, comparator or firmware rule acts on which block. Parts and settings
marked drafted are not applied to any generator.

### 1a. The blocks

| Block | What | Settings and limits (as read; drafted parts named) |
|---|---|---|
| SRC_PV | Panel (REQ-016) | Voc at most 25 V at -20 C; at most 100 W into the stage; PANEL-ACC unit: none accepted (U-03) |
| SRC_DC | Vehicle or shore DC (REQ-015) | 9 to 36 V at the plug, -36 V reversed; D38999 size 12, loop >= 56.93 mOhm; XT60-class J_DCIN (drafted, R-131) |
| SRC_USB | USB-C input: none (D-12) | the USB-C port is an outlet only |
| SOL_IN | Solar entry, board E | J_SOLAR VH 10 A; F2 10 A mini blade; D11 SMCJ40CA across the port; guard U21/Q12 off 28.55 to 31.06 V; Q13 in the return (drafted); D4 SMCJ30A; the 50 V bulk; ahead of the sense bank; (L4-E7R, L4-E7: drafted); R59 15 mOhm on TRK_VIN |
| DC_IN | Vehicle entry, board E | F1 0997010.WXN 58 V DC (drafted); D10 SMCJ40CA, D1 SMCJ40A; Q1 CSD19532Q5B 100 V (drafted); U3/Q1 LM74700-Q1 ideal diode |
| U5 | U5 LT8705AI stage | hold 16.970 / 17.593 / 18.221 V; regulation RIMON_IN 31.6k; 2.5485 A nominal, 2.9318 A highest; backstop on SWEN 3.0468 to 3.7408 A; TRK_OUT ceiling 28.28 to 30.15 V; U4/Q2 ideal diode out |
| ENTRY | Entry breaker (L4-E11, drafted) | U6 TPS48110-Q1, Q7 CSD19536KTT; UVLO on 7.87 to 8.44 V; OV off 39.6 to 41.22 V; 6.364 to 7.136 A after 0.247 to 0.49 ms; short 10.36 to 13.87 A, retry 0.5 s; R19 4.5 mOhm, L2 SRF1260-1R0Y |
| VINRAW | VIN_RAW (board E to A) | D2 SMCJ40A clamp; four Mill-Max 9 A dock pins; declared 14.10 A; basis 43.18 V maximum |
| FE | U2 LM5176 front end, board A | R11 8 mOhm, R12 12 mOhm (drafted); U34 guard R14 76.8k (drafted); VBUS20 19.08 to 20.96 V; efficiency 0.93 declared (C-8) |
| BANK | VBUS20 bank (L4-E8, drafted) | six EEHZK1V331P, 45 mOhm each; every can at most 2.4096 A; rule 2.7745 A; Cc2 3.3 nF |
| CHG | U3 charger, board A | (B1) BQ25730, drafted (drawn: BQ25731); BATDRV on pin 21 drives Q39; R16 10 mOhm; IIN_HOST 4.70 A; H3 line: flat 1.82 A, HIZ < 7.378 V; ChargeCurrent at most 3.0 A; BATOVP 17.64 V; the 4S strap fixed |
| VBAT | VBAT = VSYS node | 10.0 to 16.884 V; D1 SMCJ18A clamp; (B1): no battery, at least 12.054 V;; inhibited, VSRN + 150 mV; Q39 AONS21357 to CH_BATQ; (drafted; 0.0945 W at the profile) |
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
| P01 | SRC_PV | SOL_IN | J_SOLAR, D11, F2, the guard (U21, Q12, Q13), D4, the bulk, the sense bank | IF-01 (CONDITIONAL) |
| P02 | SOL_IN | U5 | PV_P to TRK_VIN, U5's input | IF-02 (CONDITIONAL) |
| P03 | U5 | VINRAW | TRK_OUT through U4/Q2 | IF-03 (MEETS) |
| P04 | SRC_DC | DC_IN | the plug, the interconnect, J_DCIN, F1, Q1 | IF-04 (CONDITIONAL) |
| P05 | DC_IN | ENTRY | DC_P into U6/Q7 | IF-05 (CONDITIONAL) |
| P06 | ENTRY | VINRAW | R19, L2 to VIN_RAW | IF-05 (CONDITIONAL) |
| P07 | VINRAW | FE | the dock's pins, U2's input | IF-06 (MEETS), IF-07 (CONDITIONAL) |
| P08 | FE | BANK | VBUS20 | IF-07 (CONDITIONAL) |
| P09 | BANK | CHG | VBUS20 through R16 into U3 | IF-08 (CONDITIONAL), IF-09 (CONDITIONAL) |
| P10 | CHG | VBAT | U3's output, VSYS | IF-09 (CONDITIONAL) |
| P11 | VBAT | PACK | (B1) Q39 to CH_BATQ, then R17, A F1, the pack pins, board P | IF-10 (CONDITIONAL) |
| P12 | VBAT | LOADS | the converters' inputs | IF-11 (CONDITIONAL) |
| P13 | VBAT | USBC | U19's input, R138 | IF-12 (CONDITIONAL) |
| P14 | VBAT | POE | R227 to POE_VIN | IF-13 (CONDITIONAL) |
| P15 | VBAT | PA | U13's and U15's inputs | IF-14 (CONDITIONAL) |
| N01 | VINRAW | DC_IN | the tracker back-feeds DC_P through Q7's body diode (no power is delivered this way) | none: no power is delivered this way |

### 1c. The control edges

| Control | Controller | Acts on | What | Kind |
|---|---|---|---|---|
| C01 | CTL_PANEL | CHG | FW-A01 to A03, A16, A17: RSNS_RAC, IIN_HOST 4.70 A, ChargeCurrent at most 3.0 A, the charger's 175 s watchdog; CHG_INHIBIT (FW-A14) and rules R-a to R-d (R-126); under (B1) EN_OOA 0 at boot, ChargeCurrent 0 A at POR, R-b' (R-158) | firmware |
| C02 | CTL_PANEL | LOADS | the expanders (FW-A08): SLOT_EN, DEV_EN, HEAT_EN; the margin hold (R-138, R-139); MAIN and PI_KILL (FW-A10 to A12) | firmware |
| C03 | CTL_PANEL | USBC | PD_SW_EN AND OUTLET_OK (FW-A06); the tablet's window (a proposal) | firmware and hardware |
| C04 | CTL_PANEL | POE | POE_SW_EN AND OUTLET_OK (FW-A06); U17 read on R227 (FW-A09, R-27) | firmware and hardware |
| C05 | CTL_PANEL | PA | the key-down rules K1 to K5 and C4 (FW-A05, D-11): at most 60 s, the rest floors 15.5 and 12.4 V | firmware |
| C06 | CTL_SENS | PACK | the gauge's SMBus (FW-E01): its ranges relayed to the charger by the host; SHUTDOWN for storage (FW-E09); HWD 10 s | firmware |
| C07 | CTL_SENS | LOADS | the mixer fans (FW-E07), the Geiger supply (FW-E08), VIN_MON for FW-A16 (FW-E04) | firmware |
| C08 | CTL_HW | U5 | the hold (FBIN divider R8, R9 at 0.1 %), the regulation (IMON_IN, RIMON_IN 31.6k), the backstop comparators on SWEN, off below 2.662 V of TRK_LDO33 | hardware |
| C09 | CTL_HW | ENTRY | the TPS48110-Q1's own UVLO, OV, breaker and short-circuit trip; the LM74700-Q1 blocks reverse current | hardware |
| C10 | CTL_HW | FE | U34's restart guard (R14 76.8k: 6.754 to 7.139 V); R11's average and R12's cycle-by-cycle limits | hardware |
| C11 | CTL_HW | CHG | the H3 line on ILIM_HIZ (the corrected knee), the charger's VINDPM, ACOV, BATOVP and SYSOVP; under (B1) BATDRV drives Q39 (LDO mode below VSYS_MIN) | hardware |
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
| IF-01 | panel to the solar entry | at most 25 V at -20 C; PANEL-ACC's A-1 Vm20 + U_V at most 25.000 V at -20 C and 1000 W/m2 (24.1505 V on the typical rows, margin 0.8495 V; Voc25 20.315 to 22.156 V) / D4 standoff 28 V on TRK_VS, reached by a unit at A-1's ceiling only above 8574 W/m2 at n 2; under CS101 the input at most 27.82 V; TRK_VS 44.25 V and PV_P 44.74 V at the capability scenario | hot short circuit 6.802 A with the sheet's tolerance; PANEL-ACC's A-3 (a) 3.987 A, (b) 8.1817 A, (c) 13.82 A at the design level 2111.4 W/m2 / F2 10 A; J_SOLAR's VH 10 A with the lead at AWG 16 (R-29); A-3(c) over JST VH's printed 10 A (R-148); under CS101 the filtered ripple at most 0.0585 A against a 0.1130 A margin | the lead about 0.0465 Ohm; the bank 0.5262 Wh a day | the entry at 62.1 C inside air; the bulk up to 4.45 times its ripple rating under CS101 (M2 reads it) | none / F2, the 50 V bulk ahead of the bank, D4 and C71 to C74, the INB filter (L4-E7R, drafted) | l4e O-1, L4-E7R (accepted), L4-E13 (accepted; PANEL-ACC), L4-E7's panel-lead derivation (set 27) and its solar-fault remedies (check 5) | CONDITIONAL (CONDITIONAL): the known defects D-10 (a stiff 36 V source on the port) and D-11 (a reversed panel) addressed in drafts by the solar guard (R-173, not applied; D-11 CONDITIONAL on Q13's leakage above +25 C); CS116 and CS115 MEET with the guard on and off (D-12, R-174); the band between 25 V and the cut-off a residual for layer 8 (R-175); no unit bought or measured (R-35), A-3(c)'s rating (R-148), M3's n (R-149), the lead at AWG 16 (R-29), the loop's typical rows (break-even 2.51 times), the bulk's temperature, the bank's pulse capability |
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
  the charge path, counted once in the energy and thermal budgets (section 2).
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
| M1 | PS-IDLE-SPEC, the approved profile (the tablet not charged) | 36.5 W at the load pins; 6.3 W in the converters and the distribution | 42.8 W (low 33.1, high 82.8 W, every load at its maximum) | inside the 42.8 W: 4 fans 3.128 W at the pack; 8.4 W of loads with no document (tier T); the board logic rows carry the power path's quiescent draws (not itemized by part); with (B1), Q39 0.0945 W more on battery (0.221 % of the pack's output; drafted) | 43.4 W (the pack's I2R 0.59 W inside), plus Q39's 0.0945 W with (B1) | 0 W | pwr_budget.out, load_trace.out, L4-E12 out 8c, L4-E11 out 12e |
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
| B1 | ruled 35E, D-06 4S3P | battery-only, room temperature (the chain's +20 C) | 107.9 Wh usable | 2.52 h (2.515 h with (B1)'s Q39) | 1.73 h (the window at the start, the worst placement) | 2.25 W over 48 h, 1.50 W over 72 h | l4e_replay.out 2 (MODELED) |
| B2 | ruled 35E | battery-only, the cells at -10 C (the 35E's discharge floor) | 44.5 Wh usable | 1.04 h (1.037 h with (B1)'s Q39) | 0.72 h | 0.93 W over 48 h, 0.62 W over 72 h | l4e_replay.out 2 |
| B3 | ruled 35E | battery-only, the cells at -5.52 C (REQ-024's -20 C with the kit's heat, LO-01b) | 54.0 Wh usable | 1.26 h | 0.87 h | 1.12 W over 48 h, 0.75 W over 72 h | L4-E10 out 9c |
| S1 | ruled 35E | solar-assisted, room temperature, the candidate panel's day (350.0 Wh into the stage, L4-E7's first round) | first stop at h 6 (06 UTC start) / h 2 (18 UTC start) | unserved 1367.4 / 1368.1 Wh at 48 h (33.4 % of the profile's 2054.4 Wh served at most), 2103.9 / 2104.6 Wh at 72 h (31.7 % served) | unserved at most 77.4 / 116.1 Wh more at 48 / 72 h (38.7 Wh a day for 2 / 3 windows; INFERRED bound); the first stops unchanged (they precede the 13 UTC window) | 8.0 W at both horizons; with the tablet at most 1.61 W lower (6.4 to 8.0 W) | l4e_replay.out 12 (MODELED; the corrected path, WE) |
| S2 | ruled 35E | solar-assisted, L4-E7R's accepted stage (336.6 Wh a day at the nominal hold) | as S1 (not re-run); the drafted solar guard takes 1.31 Wh more of SC-37's 336.6 Wh a day (0.39 %; 0.217 W at the regulation's highest current; L4-E7's remedies, check 5) | unserved at most 26.8 / 40.2 Wh more than S1 (13.4 Wh a day less into the stage; INFERRED bound) | as S1, plus S1's tablet bound | 7.4 to 8.0 W; with the tablet 5.8 to 8.0 W (INFERRED bounds) | L4-E13 check 4, l4e_replay.out 12 |
| S3 | ruled 35E | solar-assisted at the cold end | NOT COMPUTED: no cold-day sun trace is held, and the cells' temperature through the day is not modelled | not computed | not computed | 3.3 W if the steady load scales with the store as at room temperature (44.5 Wh against 107.9 Wh; INFERRED, an estimate, not a run) | this record (the method stated) |
| S4 | ruled 35E | solar-assisted: whether the sealed case admits the charge (the cells at or under the gauge's 42 C start) | the solar rows assume the pack accepts charge at +20 C | with the profile running, on the bound only below -30.6 C ambient; at the outside films' cap only below about 13.8 to 14.4 C (INFERRED, 2c); on SC-37's design day the charge path counted, T-H1's K7 and K8 admit it at a reading of at least 1.698 W/K (the day's cold end) to 2.081 W/K (its warm end), which the combined route does not reach on the bound (1.355 to 1.360 W/K; L4-E12 10d, 11e, check 7) | the window adds 1.4 W of heat in the case | where the case does not admit the charge the battery-only rows apply: S1 to S3 are CONDITIONAL on T-H1 (U-02) | L4-E10 out 10c, this record 2c (out 16e) |
| P1 | proposed HL18650V (a PROPOSAL, U-01; not adopted) | battery-only, room temperature (L4-E10's chain at +25 C) | 90.2 Wh usable | 2.11 h | 1.45 h | 1.88 W over 48 h, 1.25 W over 72 h | L4-E10 out 9c |
| P2 | proposed HL18650V (a PROPOSAL) | battery-only at the cold end (brackets, ASSUMPTION) | 45.1 to 69.6 Wh with the cells at -5.52 C; 37.2 to 54.1 Wh from a cold start at -20 C | 1.05 to 1.63 h; 0.87 to 1.26 h | less, by the same arithmetic | 0.94 to 1.45 W over 48 h at -5.52 C | L4-E10 out 9c |
| P4 | the Saft MP 176065 xtd as 4S1P (a PROPOSAL, U-01's supported route; not adopted) | battery-only, room temperature (L4-E10's chain, aged 0.80) | 53.5 to 58.8 Wh usable (81.76 Wh nominal; MODELLED: Saft prints no curve) | 1.25 to 1.37 h | 0.86 to 0.95 h | 1.11 to 1.22 W over 48 h, 0.74 to 0.82 W over 72 h | L4-E10 out 11c (check 6) |
| P5 | the Saft MP 176065 xtd (a PROPOSAL) | solar-assisted, room temperature; and the cold end | not run by the replay; no cold capacity is printed | not computed | as S1's bound | 4.0 to 4.4 W if the steady load scales with the store (INFERRED estimate) | L4-E10 out 11c |
| P3 | proposed HL18650V (a PROPOSAL) | solar-assisted, room temperature | not run by the replay | not computed | as S1's bound | 6.7 W if the steady load scales with the store (INFERRED estimate); every storage shortfall grows by at most 17.7 Wh | L4-E10 out 9c |

**Endurance, apart from electrical feasibility.** The objective of 48 to 72 h is NOT MET by A1 (DR-01): the steady load the
store and the sun carry through either horizon is the replay's 8.0 W against the approved profile's 42.8 W, a deficit of
34.8 W (81 % of the profile), and the least storage to add is +1361.5 / +2094.1 Wh at 48 / 72 h. **A charger change does not
close it:** the deficit is the store and the day's harvest, not a conversion efficiency. No mandatory function is reduced to
narrow it, and the profile is not lowered. The tablet's optional charging lowers what is carried by at most its 38.7 Wh a
day (S1, S2). The cold end's solar-assisted case is not computed (S3): no cold-day sun trace is held. **(B1)'s battery FET
Q39** (U-04's selected charger, drafted) takes 0.0945 W at PS-IDLE-SPEC on battery, 0.221 % of the pack's output: the battery-only
runtimes move by less than their printed precision (2.515 h, 1.038 h), and no other runtime figure changes. **U-01's supported
route** (L4-E10, checks 4 to 6 at `e2d20bf2`), the Saft MP 176065 xtd as 4S1P, stands beside the ruled pack as a labelled PROPOSAL
(P4, P5; 2b'): 53.5 to 58.8 Wh usable, 1.25 to 1.37 h battery-only (MODELLED), against 81.76 and 144.72 Wh nominal; the ruled 35E
stays the baseline, and it is UNSUITABLE on its own published evidence for E3-O, E5's dwell and the +71 C and -33 C storage rows
(section 6).
**Whether the sealed case admits the charge (S4):** the solar-assisted rows assume the pack accepts charge; with the profile
running the cells reach the gauge's 42 C start on the conservative bound above -30.6 C ambient, so the solar part of S1 to S3 is
CONDITIONAL on T-H1 (2c, normal operation): with the charge path counted, charging with the profile running needs 1.627 to 1.977
W/K on the design day (K7, K8; 2c'). **The drafted solar guard** (L4-E7's remedies, check 5; R-173) takes 0.217 W at the
regulation's highest current (0.353 W at the trip's), 1.31 Wh of SC-37's 336.6 Wh a day (0.39 %), an endurance cost carried in
S2; with its own currents around the bank the static bound at the panel entry is 93.5954 W (93.5521 W without it; IF-02, 2d).

### 2b'. The cell, compared on one boundary (L4-E10's battery comparison, its section 16; check 6 at `e2d20bf2`; out 24)

L4-E10's table as filed, carried as the budget's and the handover's cell row: the approved pack against the Saft route on the
42.8 W profile, the 3.00 V graceful line, 0.80 ageing and +20 C, each item classed **GUARANTEED** (a maker's printed limit),
**MODELLED** (L4-E10's model, its assumptions named) or **AWAITING** (evidence owed, and by whom). **Adoption is not supported
yet:** the fit mock-up (R-167), 18 A for 60 s (R-168), Saft's missing figures, the gauge data and T-H1 are awaited, and the
owner's approval of the cell change and of any purchase is required and not given.

| Item | Approved pack (D-06) | Saft route (a proposal) |
|---|---|---|
| Part and specification | Samsung SDI INR18650-35E; product specification Ver. 1.1, 2015-07-09 (GUARANTEED, filed) | Saft MP 176065 xtd; datasheet Doc. n 31109-2-0625, June 2025 (GUARANTEED, held back) |
| Chemistry, rechargeability | lithium-ion, rechargeable (GUARANTEED) | lithium-ion, rechargeable (GUARANTEED) |
| Arrangement | 4S3P, 12 cylindrical 18650 cells (D-06; the cell sizes GUARANTEED) | 4S1P, 4 prismatic cells (the sizes GUARANTEED; the pack's fit MODELLED, AWAITING the mock-up) |
| Nominal energy | 12 x 3.35 Ah (the minimum, 0.2C to 2.65 V) x 3.60 V = **144.72 Wh**, D-06's "about 145 Wh" (GUARANTEED inputs); 149.04 Wh on the typical 3.45 Ah | 4 x 5.60 Ah (typical, C/5 to 2.5 V) x 3.65 V = **81.76 Wh** (GUARANTEED as typical); 79.39 Wh on an assumed minimum (ASSUMPTION: Saft prints none) |
| Usable energy, one boundary | **107.9 Wh, 2.52 h** at +20 C; 44.5 Wh, 1.04 h with the cells at -10 C (MODELLED) | **53.5 to 55.1 Wh, 1.25 to 1.29 h** on the 35E's curves at the same current; 57.0 to 58.8 Wh, 1.33 to 1.37 h at the same C-rate; 22.1 to 24.3 Wh at -10 C (MODELLED; no Saft discharge or cold curve: AWAITING Saft) |
| Charge limits | 0 to 45 C at the surface; CC-CV 4.2 V; 1.70 A standard, 1.02 A for cycle life, 2.00 A at most a cell; ends at 0.02C (GUARANTEED) | -30 to +85 C; CC/CV 4.2 V; 5.6 A at most; under 0 C "consult Saft"; termination not printed (GUARANTEED; the termination AWAITING Saft) |
| Discharge limits | -10 to 60 C at the surface; 8 A continuous, 13 A not continuous (no duration); cut-off 2.65 V (GUARANTEED) | -40 to +85 C; 11 A continuous, 22 A pulses (no duration); cut-off 2.5 V (GUARANTEED); 18 A for 60 s on one cell AWAITING (Saft's answer or a bench pulse) |
| Storage limits | 1 month -20 to 60 C, 3 months -20 to 45 C, 1 year -20 to 25 C at 30 %, recovery over 80 % (GUARANTEED) | allowable -40 to +85 C, recommended +15 to +30 C; no time, charge or recovery printed (GUARANTEED range; its use for 24 h at the stored charge INFERRED, AWAITING Saft's confirmation) |
| Physical fit | the ruled block, 56.65 x 133.5 x 38.1 mm, 0.2881 L (GUARANTEED cell sizes) | four cells 0.308 L with terminals; along the axis +6.90 mm against 5.30 mm as designed, so at most 1.40 mm of wrap and spacers (the 35E block uses 3.00 mm); the room round the block 0.0865 L as designed, 0.0559 L at the worst stack; thickness at the beginning of life and full charge, "can increase with temperature and during battery life" (MODELLED fit; AWAITING the mock-up, the session and Layer 7, and Saft's life thickness) |
| Charger (the drawn BQ25731) | strap 16.800 V = 4 x 4.20 V; set 3.0 A = 1.00 A a cell; BATOVP 17.47 V; the gauge's taper 250 mA = 0.083 A a cell; the CUV 2.50 V (the 35E's pack guideline terminates at 2.50 V) (GUARANTEED settings, compatible) | the same 16.800 V; 3.0 A a cell against 5.6 A; BATOVP 17.47 V; taper 0.250 A a cell against no printed termination; the CUV 2.50 V against the 2.5 V cut-off (compatible; the termination AWAITING Saft) |
| Protection | U2 BQ7720700 (OVP 4.325 V, UVP 2.25 V, OT 70 C); the gauge's UTC 1.0, T3 42, OTC 44.0, OTD 57.5, UTD -9.0 C; F2 Eaton SCF9550-30-05, 30 A for 4 to 5 cells (compatible as drawn) | the same parts protect it as drawn, the gauge's thresholds inside its windows; using its +85 C needs U2's 83 C variant and a re-derived network and the ladder (drafts); the pack's 10 / 18 A fall on one cell; the gauge's capacity and chemistry data AWAITING (TI's list or a learning cycle, the firmware owner) |
| Cost | USD 8.25 a cell, USD 99.00 for 12 (the l3batt reading; a quote AWAITING the purchase) | NZ$ 238.72 a cell, NZ$ 954.88 for 4 (a distributor's listing archived in January 2025; a quote AWAITING the owner's purchase) |

### 2c. Heat into the sealed case per mode, against T-H1's lines

| Heat | Mode | Into the case (W) | T-H1's line | The inside air at the lines (INFERRED unless named) | On L4-E12's conservative bound (the fans' flow at zero) | With L4-E12's heat-rejection approaches (15, out 10b: the same bound) |
|---|---|---|---|---|---|---|
| H1 | PS-IDLE-SPEC (M1) | 43.40 | C1's inside-air trigger +50 C | at the binding line +20.1 K: C1 sheds the profile to the reduced mode above 29.9 C ambient; on W4's lid-open 1.22 to 2.85 W/K +15.2 to +35.6 K | 60 to 73 K over the bound's one-node lid-open points (0.598 to 0.720 W/K; INFERRED, computed at smaller rises): C1's trigger above about -23 to -10 C ambient; T-H1 decides this too | not a required state at +40 C (C1 sheds it; D-02b); at its heat on the bound (two nodes, +40 C) 0.767 W/K; fins on the face's free strips 0.821 (k 2) to 0.854 W/K (k 3); the large loads led into the plate 1.096 W/K, 1.339 W/K with the fins; the open lid's skin 0.801 W/K; all three 1.384 W/K against its own line K6 at REQ-014's +20 C, 1.447 W/K: 1.252 W (0.063 W/K) short; a reading at K6 of at least 1.508 W/K needs no route (L4-E12 15 and 11, checks 6 and 7) |
| H2 | PS-IDLE-SPEC with the tablet's window (M2) | 44.80 | as H1 | +20.8 K at the binding line; C1 above 29.2 C ambient | 62 to 75 K over the bound's one-node lid-open points (0.598 to 0.720 W/K; INFERRED, computed at smaller rises) | not computed: L4-E12 15 takes the profile's heat alone: the window adds 1.4 W, so K6's C1 line at +20 C needs 1.493 W/K, over the combined route's 1.384 W/K at the profile's heat (INFERRED) |
| H3 | E3-O, the heat stage with the ballasts (M3) | 27.09 | +70 C class at +55 C: 1.806 W/K | 67.55 C at the binding line (L4-E12) | the air 92.61 C (0.720 W/K at 37.6 K); with every session measure 0.691 against the 0.903 W/K the module's +85 C intake needs: a gap of 0.212 W/K (L4-E12 9d) | not computed: L4-E12 15 takes the profile's heat alone; E3-O's own options are L4-E12 9e's |
| H4 | E5 under the hold, with the ballasts (M4) | 21.59 | +70 C class at +60 C: 2.159 W/K, the BINDING line | 70.00 C at the line; T-H1 passes at a reading of at least 2.455 W/K at its own heat (K10; replaces 2.416 W/K at one heater's 21.2 W) | the air 90.93 C (0.698 W/K at 30.9 K), 83.41 C with F3; with every session measure 0.671 against the 0.621 W/K needed: it holds (L4-E12 9d) | not computed: L4-E12 15 takes the profile's heat alone; E5 holds on the bound with every session measure |
| H5 | E5 with no hold | 27.09 | +70 C class at +60 C: 2.709 W/K | the hold is what lowers E5's line to 2.159 W/K | not computed: the hold's case already passes +70 C on the bound | not computed: L4-E12 15 takes the profile's heat alone |
| H6 | source-only at a 9.00 V plug (M5) | 23.94 | none set by the record (the envelope's state) | +11.1 K at the binding line (the loads and the two stages' losses at the rule's bound; INFERRED) | 33 to 40 K over the bound's one-node lid-open points (0.598 to 0.720 W/K; INFERRED, computed at smaller rises) | not computed: L4-E12 15 takes the profile's heat alone |
| H7 | a charge running on shore (added to a mode) | 3.45 | LO-01a's floor 1.666 W/K (1.8058 W/K with the ballasts) | +1.60 K at the binding line | LO-01a's 1.6664 W/K lid closed lies far over the bound's 0.505 to 0.537 W/K lid closed: U-01's (L4-E12 14.2) | with the profile running on SC-37's design day (the air 13.2 to 18.3 C), the charge path counted (46.859 W): K7 and K8 need 1.627 to 1.977 W/K, read at 1.698 and 2.081 W/K (corrected from 1.507 to 1.832 W/K); the combined route reaches 1.355 to 1.360 W/K on the bound (L4-E12 11, check 7) |
| H8 | (B1)'s Q39 on battery (added to a mode; drafted) | 0.0945 | none: a load on the pack's path | 0.0945 W at PS-IDLE-SPEC, 0.2048 W at PS-TYP, 1.07 W at 10 A | +0.16 K at the profile at the bound's lowest point | not computed: added to a mode |
| H9 | the heat stage at REQ-024's +40 C (C1's end state; the REQUIRED state there) | 27.09 | K1 the SGP41's +55 C: 1.806 W/K (CFL-002 option C); K2 its Table 4 +50 C: 2.709 W/K; K3 the +70 C class: 0.903 W/K (options A, B) | a bench reading of at least 1.958 W/K (K1) or 0.941 W/K (K3), the heaters 25.136 W plus the fans (L4-E12 11e, 11g) | 0.598 to 0.661 W/K at K1's 15 K rise; the outside films' cap 1.504 W/K (1.859 W/K at the other ends): K1 at or over the cap at the conservative ends, K3 over the bound (L4-E12 11d) | not computed: L4-E12 15 takes the profile's heat; under the governing line the route is read at K1's point |

**Against L4-E12's conservative bound** (check 5 at `7f41632d`; the fans' airflow, the boards' radiation and the floor's
support credited at zero): 0.566 W/K at E5 and 0.607 W/K at E3-O lid open, under every stated line and under the outside films'
cap of 1.540 to 1.571 W/K that no inside film passes. On it E5's hold holds only with every session measure (0.671 against
0.621 W/K) and E3-O falls 0.212 W/K short (the module's intake at 92.61 C); the profile's own 43.4 W would, on the bound's
one-node points, put the mixed air past C1's +50 C trigger at any ambient above about -23 to -10 C (H1, INFERRED), so C1 would
shed it within the envelope. T-H1's two points measure what the bound credits at zero (5c), and they decide all of these; the
endurance runs of 2b assume the profile as approved and are not changed by them.

**The heat-rejection approaches beside the bound** (L4-E12 section 15, check 6 at `589f18ac`; out 16c'). Three passive approaches
inside the rulings (no vent or opening, 32.53; the Peli 1450; the 3 mm aluminium face, 32.40), computed at the profile's 43.413 W
on the same bound (two nodes, the inside air and the plate), each alone and together. They were asked against the profile at
+40 C, a state L4-E12's check 7 shows no requirement asks for; **their need is now K6**, the profile at REQ-014's +20 C under
C1's +50 C, which is the same 1.447 W/K, and K7 and K8 with the charge path counted. **None reaches it on the bound:** the
combined route falls 1.252 W (0.063 W/K) short of K6. Each item enters the register only under a T-H1 point reading under its
line (R-170 to R-172). **The heat stage at +40 C** (H9) is the required state there; its line is the owner's CFL-002 (2c').

| Approach | Its change, inside the rulings | +40 C: the air / the plate / G | Design day 13.2 C: the air / G | 18.3 C: the air / G | Against the need | Register |
|---|---|---|---|---|---|---|
| none | the bound: the inside by natural convection, the fans' film credited at zero | 96.61 C / 62.34 C / 0.767 W/K | 70.77 C / 0.754 W/K | 75.70 C / 0.756 W/K | under K6's 1.447 W/K and under K7's and K8's 1.627 to 1.977 W/K | R-104 (T-H1 reads it) |
| a2 | fins on the face's free strips, effective area multiplier k 2 (ASSUMPTION) | 92.89 C / 56.15 C / 0.821 W/K | 66.82 C / 0.810 W/K | 71.79 C / 0.812 W/K | under K6's 1.447 W/K and under K7's and K8's 1.627 to 1.977 W/K | R-170 |
| a3 | fins on the face's free strips, k 3 | 90.84 C / 52.78 C / 0.854 W/K | 64.62 C / 0.844 W/K | 69.62 C / 0.846 W/K | under K6's 1.447 W/K and under K7's and K8's 1.627 to 1.977 W/K | R-170 |
| b | the large loads, 23.641 W at their pins, led into the plate | 79.59 C / 70.08 C / 1.096 W/K | 53.98 C / 1.065 W/K | 58.86 C / 1.070 W/K | under K6's 1.447 W/K and under K7's and K8's 1.627 to 1.977 W/K | R-171 |
| ba | (b) with (a)'s fins, k 3 | 72.41 C / 56.96 C / 1.339 W/K | 46.40 C / 1.307 W/K | 51.36 C / 1.313 W/K | under K6's 1.447 W/K and under K7's and K8's 1.627 to 1.977 W/K | R-170, R-171 |
| c | a skin on the open lid's ceiling (at most 0.0803 m2) on a 2.56 K/W braid (ASSUMPTION) | 94.17 C / 58.27 C / 0.801 W/K | 68.10 C / 0.791 W/K | 73.07 C / 0.793 W/K | under K6's 1.447 W/K and under K7's and K8's 1.627 to 1.977 W/K | R-172 |
| all | (b) + (a) + (c): the combined route | 71.36 C / 55.12 C / 1.384 W/K | 45.25 C / 1.355 W/K | 50.22 C / 1.360 W/K | short by 1.252 W (0.063 W/K) of K6's 1.447 W/K; under K7's and K8's corrected 1.627 and 1.977 W/K (10d's 0.153 and 0.472 W/K short were against the uncorrected needs) | R-170 to R-172 |
| need | the profile's 43.413 W: K6, C1's +50 C at REQ-014's +20 C (once read as the +70 C class at +40 C, X2, no requirement) | K6: 1.447 W/K | K7, the charge path counted: 1.627 W/K | K8: 1.977 W/K | readings of at least 1.508 (K6), 1.698 (K7) and 2.081 W/K (K8) | R-104 |

### 2c'. Normal operation in the in-use envelope (out 16e)

On L4-E12's thermal reconciliation (its section 16, output section 11; the coordinator's check 7 at `6f8fd652`), which
corrects this section's earlier framing: each condition of the in-use envelope with its requirement and mode, its heat (the fans
counted once), its ambient, its limit, the conductance it needs and the bench reading that meets it, read from L4-E12's output.
The X rows are states no requirement asks for, kept to show what was withdrawn.

| Condition | Requirement and mode | Lid | Heat (W) | Ambient | The limit | Needs (W/K) | A bench reading of at least (W/K) | Governs |
|---|---|---|---|---|---|---|---|---|
| K1 | REQ-024 and E3-A at +40 C: C1's end state, the heat stage on shore with the ballasts | open | 27.086 | +40.0 C | the SGP41's +55 C (REQ-024's acceptance, every part in its range; REQ-052's and E3-L's line; its Table 5) | 1.806 | 1.958 | CFL-002 option C (the SGP41 kept powered) |
| K2 | the same, the SGP41 judged on its Table 4 +50 C (this record's corrected rule; the owner's CFL-002 open) | open | 27.086 | +40.0 C | the SGP41's +50 C (Table 4) | 2.709 | 3.081 | option C judged on Table 4 (the owner's CFL-002, open) |
| K3 | the same, the +70 C class in the heat stage (the H5007NL, the ATP16, the PXP4043/C and the radios C1 leaves on) | open | 27.086 | +40.0 C | +70 C (the makers' sheets of section 4) | 0.903 | 0.941 | CFL-002 options A and B |
| K4 | the same, the module's intake | open | 27.086 | +40.0 C | the module's +85 C (CM5 4.4) | 0.602 | 0.620 | always (under K3) |
| K5 | REQ-052 and E3-L at +40 C: the heat stage | closed | 27.086 | +40.0 C | the SGP41's +55 C (E3-L's line) | 1.806 | 1.958 | option C, lid closed (REQ-052, E3-L) |
| K6 | REQ-014 at +20 C: the profile on the pack, not shed by C1 | open | 43.413 | +20.0 C | C1's inside-air trigger +50 C (REQ-024) | 1.447 | 1.508 | REQ-014's runtime at +20 C |
| K7 | charging on SC-37's design day, the profile running and the charge path counted (on shore), cold end | open | 46.859 | +13.2 C | the gauge's charge start T3 42 C (E3-A; the cells at the air) | 1.627 | 1.698 | charging with the profile, the design day's cold end |
| K8 | the same, warm end | open | 46.859 | +18.3 C | T3 42 C | 1.977 | 2.081 | the design day's warm end |
| K9 | E3-O, D-02a's +55 C AMBIENT margin: the heat stage, every radio C1 leaves on | open | 27.086 | +55.0 C | +70 C (U-02) | 1.806 | 1.958 | E3-O's margin (D-02a) |
| K10 | E5's +60 C dwell under the hold | open | 21.587 | +60.0 C | +70 C (U-02) | 2.159 | 2.455 | E5's dwell (U-02's line) |
| X1 | the profile at +40 C (no requirement: C1 sheds it, REQ-024; D-02b runs one module above +35 C) | open | 43.413 | +40.0 C | C1's +50 C | 4.341 | none: no requirement | no requirement: C1 sheds the profile |
| X2 | the profile's +70 C class at +40 C (the consolidation's framing, no requirement) | open | 43.413 | +40.0 C | +70 C | 1.447 | none: no requirement | no requirement: the withdrawn framing |
| X3 | the owner's conditional check: 42.4 W under a +55 C inside-air limit at +40 C | open | 42.400 | +40.0 C | +55 C | 2.827 | none: no requirement | no requirement's mode |

<!-- gen:normal:begin -->
**The 42.8 W profile is not a required state at +40 C** (L4-E12's reconciliation, check 7; this section's earlier framing withdrawn). REQ-024's C1 sheds it on +50 C inside air or a +55 C cell to the reduced mode and the heat stage, and D-02b runs the reduced mode above +35 C ambient. The X rows show what no requirement asks: the profile under C1's +50 C at +40 C needs 4.341 W/K (X1), its +70 C class 1.447 W/K (X2, the reading 1.509 W/K once read as deciding), the owner's conditional 42.4 W under +55 C 2.827 W/K (X3).

**The required state at +40 C is the heat stage, 27.086 W, and the owner's CFL-002 sets its line** (section 6): K1, the SGP41's +55 C, 1.806 W/K (option C; a reading of at least 1.958 W/K), at or over the outside films' cap at the conservative ends (1.504 W/K); or K3, the +70 C class, 0.903 W/K (options A and B; at least 0.941 W/K). The conservative bound, 0.598 to 0.661 W/K at K1's rise, lies under both: T-H1 decides. The room reading is the conservative side: at +40 C the conductance is 1.6 to 3.7 % above the room's at the same rise (L4-E12 11d).

**The profile's own line is K6, at REQ-014's +20 C:** 43.413 W under C1's +50 C needs 1.447 W/K, a reading of at least 1.508 W/K. L4-E12's heat-rejection approaches (2c) compare against that need; computed at +40 C's ambient, they are the optimistic side for K6 at +20 C by the same 1.6 to 3.7 %.

**Charging with the profile running** (K7, K8; the charge path counted, 46.859 W): on SC-37's design day it needs 1.627 to 1.977 W/K, read at 1.698 and 2.081 W/K (corrected from 1.507 to 1.832 W/K, which left the charge path out). The solar-assisted rows of 2b assume a charge the sealed case may not admit, so their solar part stays CONDITIONAL on that line; the battery-only rows are not (INFERRED: a battery-only run, 2.52 h, is short against the case's 4.57 h time constant on the bound). On the bound the profile charges only below -30.6 C ambient (L4-E10).

**Electrical feasibility is a separate question** (1d, 8a): every interface row MEETS or is CONDITIONAL, D-10 and D-11 addressed in drafts. Thermal feasibility in normal operation is U-02's, decided by T-H1's points against the line CFL-002 sets.
<!-- gen:normal:end -->

### 2d. The reconciliation of every figure that differs between records

| Figure | Quantity | The figures, each with its basis and the file that prints it | Kept | Why |
|---|---|---|---|---|
| R01 | the 35E pack's usable energy at room temperature | 107.9 (l4e_replay.out: the energy chain (energy_budget.py: the 35E's rate, mean-voltage and end-fraction curves, aged 0.80, to the graceful 3.00 V line) at PS-IDLE-SPEC); 108.1 (pwr_budget.out: pwr_budget.py's derating chain (12 x 3.35 Ah x 3.60 V, rate 0.997, sag, ageing 0.80, the 5 % reserve)) | 107.9 Wh | the endurance runs (battery-only and solar-assisted) rest on the energy chain; 108.1 Wh stays only as L4-E10's first-chain comparison and in the U-01 bullet L4-E10 reads back (Appendix A) |
| R02 | the proposed HL18650V pack's usable energy | 90.2 (l4e10_cell_thermal.out: L4-E10's chain, the same as R01's 107.9 Wh); 90.4 (l4e10_cell_thermal.out: L4-E10's first chain, the same as R01's 108.1 Wh) | 90.2 Wh | one chain with the ruled cell; the difference to the 35E is 17.7 Wh on both chains |
| R03 | the panel's day into the stage at the nominal hold | 350.0 (l4e_replay.out: the candidate's trace with no input limit (L4-E7's first round); every solar-assisted run of the replay); 336.6 (l4e7_stage_settings.out: the same day under L4-E7R's accepted regulation (RIMON_IN 31.6k)) | 336.6 Wh for the design | the replay is not re-run: its solar rows stay on 350.0 Wh, bounded at most 13.4 Wh a day worse at the accepted stage (S2) |
| R04 | the hold corners' days | 344.0 (l4e7_stage_settings.out: L4-E7R, the hold 16.970 to 18.221 V with the regulation); 373.5 (l4e_replay.out: L4-E7's first round, the hold 16.695 to 18.490 V, no limit); 307.9 (l4e7_stage_settings.out: L4-E7R's upper corner); 280.6 (l4e_replay.out: L4-E7's first round's upper corner) | L4-E7R's 344.0 / 336.6 / 307.9 Wh | the accepted stage; the replay's corners are the first round's window |
| R05 | L4-E7R's highest regulated current | 2.9318 (l4e7_stage_settings.out: at the hold's corners, the stage's operating range); 2.9337 (l4e13_panel.out: at REQ-016's 25 V ceiling, A-3(a)'s conservative input) | both | two operating points of the same regulation; neither replaces the other |
| R06 | the 100 W bound's layers | 73.3436 (l4e13_panel.out: the regulation's own 25 V corner); 93.5521 (l4e7_stage_settings.out: the backstop's static bound, CONDITIONAL on G_CM and U18's VIN+ bias); 93.5954 (l4e7_stage_settings.out: the same at the panel entry with the solar guard's own currents (the remedies)); 96.25 (l4e7_stage_settings.out: L4-E7's stack A, CONDITIONAL on five unprinted values) | all three, each with its layer | the regulation acts first, the backstop second; 96.25 W is the earlier qualification, kept as context |
| R07 | A1's steady load through the horizon | 8.0 (l4e_replay.out: on the candidate panel's trace (350.0 Wh a day)); 8.8 (l4e_replay.out: on the 100 W screening stimulus (a 400 Wp series REQ-016 does not admit)) | 8.0 W | the screening stimulus is not a source REQ-016 admits |
| R08 | the profile's power | 42.8 (load_trace.out: the profile's stated figure); 42.82 (load_trace.out: load_trace's sum of 39 loads); 42.824 (l4e12_thermal.out: L4-E12's reproduction of the same sum) | 42.8 W | one quantity at three roundings |
| R09 | the enclosure lines (W/K) | 1.666 (l4e10_cell_thermal.out: LO-01a's floor: the inside air at the SGP41's +55 C at +40 C on shore, the heat stage); 1.8058 (l4e12_thermal.out: LO-01a's floor with L4-E8's ballasts counted); 1.806 (l4e12_thermal.out: E3-O alone: the heat stage with the ballasts, +55 to +70 C); 2.159 (l4e12_thermal.out: E5 under the hold, +60 to +70 C: the BINDING line); 2.709 (l4e12_thermal.out: E5 with no hold); 2.416 (l4e12_thermal.out: T-H1's pass reading at a 10 K rise: 2.159 W/K plus its expanded uncertainty) | all, each with its criterion | different states and limits; T-H1 is judged at 2.416 W/K for the binding 2.159 W/K |
| R10 | E5's heat under the hold | 18.152 (l4e12_thermal.out: at the pack); 19.497 (l4e12_thermal.out: into the case on shore); 21.587 (l4e12_thermal.out: with L4-E8's ballasts) | 21.587 W for the line | three boundaries of one budget |
| R11 | E3-O's heat | 24.996 (l4e12_thermal.out: into the case on shore); 27.086 (l4e12_thermal.out: with the ballasts) | 27.086 W | the ballasts counted once |
| R12 | the charge current | 3.0 A (HW-FW-CONTRACT.md: the drawn ChargeCurrent limit (FW-A02)); 3.06 A (l4e_replay.out: energy_inputs.yaml's D-06 figure (1.02 A a cell), the replay's runs) | 3.0 A for the design | the replay's solar rows charge 2 % faster than the drawn limit allows, so they lean optimistic (not re-run) |
| R13 | the 35E's usable energy cold | 44.5 (l4e_replay.out: the cells at -10 C, the 35E's discharge floor); 54.0 (l4e10_cell_thermal.out: the cells at -5.52 C, REQ-024's -20 C with the kit's heat (LO-01b)) | both, each at its cell temperature | two temperatures |
| R14 | the hold's point | 17.6 V (l4e7_stage_settings.out: REQ-016's stated point); 17.593 (l4e7_stage_settings.out: the FBIN divider's nominal (R8 102 k, R9 7.50 k at 0.1 %)) | 17.593 V nominal | the divider's own value; 17.6 V is the requirement's rounded point |
| R15 | ChargeCurrent at the charger's POR | 256 mA (l4e11_power.out: the drawn BQ25731: TI's E2E answer (the register's reset code)); 0 A (l4e11_power.out: the BQ25731's register description); 0000h (l4e11_power.out: the selected BQ25730 (B1): its printed reset, 0 A) | 256 mA on the board as drawn; 0 A once (B1) is applied | two parts; L4-E11 corrected the drawn part's figure, and SLUSE65A prints the BQ25730's |
| R16 | the ballasts' loss | 2.09 (ripple_dense.out: at the bound's worst corner); 0.0093 (ripple_dense.out: at L4-E8's nominal illustration) | 2.09 W in every heat budget | the worst corner is what the thermal lines carry |
| R17 | the pack heater | 7.5 W into the cells (l4e10_cell_thermal.out: the mat's output); 8.5 W at the pack (l4e10_cell_thermal.out: with its buck's loss) | both, each at its boundary | one heater, two boundaries |
| R18 | P1, the kit's shed state with no usable pack | 19.57 (l4e11_power.out: the plan figure at VBAT); 20.51 (l4e11_power.out: the rule's bound); 35.24 (l4e11_power.out: the loads' high corner) | 20.51 W as the bound | the high corner exceeds the source's least, which is why REQ-015 at 9.00 V is a CONDITIONAL CANDIDATE |
| R19 | the panel's day at the conditioned upper corner | 240.0 (l4e13_panel.out: the rated unit); 52.3 (l4e13_panel.out: a unit at A-2's floor) | both | PANEL-ACC accepts any unit inside the window; the unserved energy grows toward the floor's unit |
| R20 | T-H1's pass reading for the binding line | 2.416 (l4e12_thermal.out: the eight-point procedure at a 10 K rise, one heater's 21.2 W); 2.462 (l4e12_thermal.out: 9f's point at its 8.6 K rise); 2.455 (l4e12_thermal.out: K10: E5's own heat, 21.587 W with the fans counted (11e)) | 2.455 W/K | the same 2.159 W/K plus the expanded uncertainty; K10's point at E5's own heat replaces the 21.2 W lines (L4-E12 16.8) |
| R22 | the Saft pack's nominal energy | 81.6 (l4e10_cell_thermal.out: four times the sheet's 20.4 Wh); 81.8 (check-l4e10-5.md: 4 x 3.65 V x 5.6 Ah); 81.76 (l4e10_cell_thermal.out: the comparison: 4 x 5.60 Ah x 3.65 V (11b)) | 81.76 Wh | three roundings of the sheet's typical figures; the usable 53.5 to 58.8 Wh (MODELLED) is what the budget uses |
| R21 | the case's conductance lid open with the fans | 1.22 (pwr_budget.out: W4's lumped low case, the fans' inside film assumed (10 W/m2K)); 0.566 (l4e12_thermal.out: the conservative bound at E5, the fans' flow credited at zero); 0.607 (l4e12_thermal.out: the conservative bound at E3-O) | the bound for feasibility; W4's range as a sensitivity | W4's low end already assumes the fans' film, which no held document bounds (L4-E12 9c) |
| R23 | the conservative bound lid open at +40 C | 0.598 (l4e12_thermal.out: one node at the envelope's +40 C, the air 15 K up (9b)); 0.720 (l4e12_thermal.out: one node at E3-O's heat, its 37.6 K rise (9d)); 0.767 (l4e12_thermal.out: two nodes, the inside air and the plate, at the profile's 43.413 W (10b)) | all three, each at its rise and model | the conductance grows with the rise; 2c' and the heat table keep the one-node points as the conservative side and name 0.767 W/K at the profile's own heat |
| R24 | T-H1's readings near 1.5 W/K | 1.509 (l4e12_thermal.out: at 42.4 W, the fans left out: X2, the profile's +70 C class at +40 C, no requirement (10e, withdrawn in 11a)); 1.508 (l4e12_thermal.out: K6: the profile at REQ-014's +20 C under C1's +50 C, 43.413 W with the fans (11e)); 1.516 (l4e12_thermal.out: at E5's hold's 21.2 W: E3-O with F4, a fallback line (9f)) | 1.508 W/K for the profile; 1.516 W/K as a conservative fallback line | the 1.509 W/K reading established X2 only and is withdrawn (L4-E12 check 7) |
| R26 | the charging need with the profile running on the design day | 1.507 (l4e12_thermal.out: the profile's 43.413 W, the charge path left out (10a)); 1.832 (l4e12_thermal.out: the same, warm end (10a)); 1.627 (l4e12_thermal.out: K7: 46.859 W with the charge path counted (11c)); 1.977 (l4e12_thermal.out: K8: the same, warm end (11c)) | 1.627 to 1.977 W/K | the charge path's 3.446 W belongs in the heat while the pack charges (L4-E12 16.8) |
| R27 | K3's bench pass line | 0.941 (l4e12_thermal.out: 11e: at K3's own rise, 28.8 K, U 4.0 %); 0.98 (check-l4e12-7.md: check 7: 'near', K1's uncertainty applied) | 0.941 W/K | the expanded uncertainty is taken at the reading's own rise; check 7's figure is an approximation |
| R28 | the outside films' cap on the conductance | 1.540 (l4e12_thermal.out: 9b: at E5's rise); 1.571 (l4e12_thermal.out: 9b: at E3-O's rise); 1.504 (l4e12_thermal.out: 11d: at K1's 15 K rise at +40 C, the conservative ends); 1.859 (l4e12_thermal.out: 11d: the other ends) | all, each at its rise and ends | K1's 1.806 W/K lies over 1.504 and under 1.859 W/K: at or over the cap at the conservative ends |
| R30 | D4's clamp at CS116's 10 A at the hot end | 39.00 (l4e7_stage_settings.out: the drafted SMCJ28A (D1)); 41.91 (l4e7_stage_settings.out: the SMCJ30A with the guard (the remedies)) | 41.91 V | D4 changes to the SMCJ30A with the guard; both under the drafted entry's 50 V |
| R31 | the solar cut-off's rising band | 29.11 (l4e7_stage_settings.out: new parts); 28.55 (l4e7_stage_settings.out: aged by the divider's printed load-life, with the pin's leakage) | 28.55 to 31.06 V | the record's convention for a protection threshold: the aged band |
| R29 | the 35E pack's nominal energy | 145 (l4e10_cell_thermal.out: D-06's 'about 145 Wh'); 144.72 (l4e10_cell_thermal.out: 12 x 3.35 Ah (the minimum) x 3.60 V (11b)); 149.04 (l4e10_cell_thermal.out: on the typical 3.45 Ah (11b)) | 144.72 Wh | D-06's figure is the minimum capacity's; the usable 107.9 Wh is what the budget uses |
| R25 | the approved profile's heat into the case | 43.4 (l4e12_thermal.out: this record's figure at a0212d9e, as L4-E12 10a quotes it); 43.413 (l4e12_thermal.out: L4-E12 10a: 42.824 W at the pack plus the pack's own I2R) | 43.4 W in this record's tables; 43.413 W in L4-E12's thresholds | one quantity at two roundings; 1.447 W/K either way |

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
circuit changes. **U-04's selected charger (R-157, (B1): the BQ25730 with Q39)** goes into board A's round at step (a), with
U34's guard (R-124) in either order and before the regeneration, and its firmware rules (R-158) after it; the hold-up (R-152)
stays only for arrangement (A). **U-02's session measures** are carried as R-111 (the plate coupling, Layer 7), R-141 (the HX
magnetics and the wider buttons, Layer 6), R-163 and R-164 (F3's switches on board B and their firmware), R-165 and R-166
(board B's +85 C connectors and their fitting). The U-01 rows apply only under approach (II) after the owner's approval.

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
| 11 | 3a | R-157 | board A, gen_sch_a.py | apply_gen_sch_a_charger.py | U-04's selected charger (B1): the BQ25730 and Q39 in U3's land, with R-124 in either order; the strap kept fixed | L4-E11's RELEASE.md (R-147: check-l4e11-3.md at a15ab384) and its check 5 at 5aa18a69 | U-04's selected charger (B1, L4-E11's E11-27): U3 BQ25730RSNR (C5219071) with pin 21 on CH_BATDRV; Q39 AONS21357 (C404364) between VBAT and the new node CH_BATQ; R17 and R149 moved to CH_BATQ; C236 EEHZK1V181P (C242139) on VBAT; CH_BATQ declared a segment of the pack path; CELL_BATPRESZ kept a fixed 4S strap (75.14 % of VDDA), never wired to battery presence | DRAFTED (not applied) |
| 12 | 3b | R-04 | board A, gen_sch_a.py | apply_gen_sch_a_r11.py | after R-01: R11 never before R12 | L4-E4's RELEASE.md (R-90: accepted checks of L4-E4, L4-E5, L4-E6 and L4-E8) | R11 8 mOhm (HoJLR2512-3W-8mR-1%, C2904240), with IIN_HOST 4.70 A in firmware | DRAFTED (not applied) |
| 13 | 3c | R-07 | board A, gen_sch_a.py | apply_gen_sch_a_bank.py | after R-01: the ballasts and Cc2 only with R12 | L4-E8's RELEASE.md (R-91: check-l4e8-3.md), and the draft refuses a generator without R12 | Six ballasts R221 to R226, 45 mOhm (HoJLR2512-3W-45mR-1%, C2903491), one in series with each EEHZK1V331P, and Cc2 (C6) 680 pF to 3.3 nF (C1613) | DRAFTED (not applied) |
| 14 | 3c | R-08 | board A, lcsc_fill.py | none: a missing draft | with R-07 | no draft yet | The lcsc_fill.py line mapping "45mOhm 1% 2512" to C2903491 | MISSING DRAFT (not applied) |
| 15 | 3d | R-05 | board A, gen_sch_a.py | apply_gen_sch_a_r138.py | independent | L4-E4's RELEASE.md (R-90: accepted checks of L4-E4, L4-E5, L4-E6 and L4-E8) | R138 5 mOhm (HoJLR2512-3W-5mR-1%, C2903482) and its PD_SW note | DRAFTED (not applied) |
| 16 | 3e | R-06 | board A, gen_sch_a.py | apply_gen_sch_a_u17.py | after 3a to 3d | this record's RELEASE.md (R-93, after its check) | The PoE monitor U17 moved off the 54 V rail (HF-F02, S-60): R227 5 mOhm (HoJLR2512-3W-5mR-1%, C2903482) from VBAT to a new rail POE_VIN; U16's VIN and BIAS on POE_VIN; U17 IN+ on VBAT, IN- and VBUS on POE_VIN | DRAFTED (not applied) |
| 17 | 3f | R-09 | board A, gen_sch_a.py | a text draft (L4-E8) | with R-07 | a text draft | L4-E8's text corrections: gen_sch_a.py's third fix-up comment (the conservative bound replacing the lost dense figures) and the superseded bank notes of r11dep and L4-E6 | DRAFTED (not applied) |
| 18 | 3f | R-10 | board A, the declarations | none: a missing draft | with R-04 | no draft yet | The declarations on board A: VBUS20 and FE_OUT stay at 6.0 / 8.0 A (they cover 4.964 A in service and 7.262 A highest at 8 mOhm; their peak rises to 8.300 A only if V-A07 fails); VIN_RAW stays 14.10 A (it covers the front end's 11.65 A fault, 13.315 A at 7 mOhm); pcb_sensitive.yaml's FE_ISNS text (3.80 A) restated to 4.964 A | MISSING DRAFT (not applied) |
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
| 38 | 4e | R-173 | board E, gen_sch_e.py | apply_gen_sch_e_solar_guard.py | AFTER L4-E7's three drafts (R-19, R-20, R-21), L4-E9's hot swap (R-94) and L4-E11's entry draft (R-123): it uses their texts and the DGX19 land, and refuses a generator without them | L4-E7's RELEASE.md (R-92: L4-E7R's check 4) and its check 5 at 573fd5b8 | D-10 and D-11 (L4-E7's D4 and D5: a stiff 36 V source on the solar port and a reversed panel, single faults): the solar guard, L4-E7's selected remedies (check 5 at 573fd5b8), drafted in `apply_gen_sch_e_solar_guard.py` (7 edits, never applied): J_SOLAR.2 becomes PV_RTN; D11 SMCJ40CA across the port and C131 1 uF 100 V on PV_F; U21 TPS48110AQDGXRQ1 with R87 4.5 mOhm and Q12 CSD19532Q5B, L4-E11's network but the OV divider R98 90.9k + R99 95.3k over R100 7.68k (off above 28.55 to 31.06 V, back under 27.07 V or more, aged); Q13 CSD19532Q5B in the return with R101, R102 100k and D12 BZT52C12-7-F; D4 to the SMCJ30A | DRAFTED (not applied) |
| 39 | 4f | R-22 | board E, regenerated on the box | none: owed work | after 4a to 4e | the gates and the evidence re-taken | Board E regenerated with R-12 to R-21, its gates and evidence re-taken on the box | OWED (not applied) |
| 40 | B | R-107 | board B, gen_sch_b.py | none: a missing draft | board B's round | no draft yet | BANK-R1 in gen_sch_b.py (E3-L's stage criteria fail where the heat stage is entered without it) | MISSING DRAFT (not applied) |
| 41 | B | R-163 | board B, gen_sch_b.py | none: a missing draft | U-02's F3: board B's round | no draft yet | U-02's deeper hold in E5 (F3): supply switches for the KSZ9897R's rails, NVMe slot 3, the PCIe switch and the LG290P on board B, so E5's hold can turn them off while the module logs on its own storage | MISSING DRAFT (not applied) |
| 42 | B | R-166 | board B, gen_sch_b.py | none: a missing draft | U-02's +85 C connectors and HX magnetics, after R-165's picks | no draft yet | Board B for U-02: R-165's +85 C connectors and the H5007NL's HX version (R-141) fitted | MISSING DRAFT (not applied) |
| 43 | C | R-145 | board C, gen_sch_c.py | none: a missing draft | board C's round | no draft yet | Board C for U-02: the MAIN, PI and TEST pushbuttons (R-141's pick); U5 to the DRV package; U5's declared 0.72 A peak against its 500 mA (MESHSAT-1479) | MISSING DRAFT (not applied) |
| 44 | 5 | R-25 | firmware | none: owed work | only on a board A with the H3 line (else the derated limit) | firmware | Firmware: IIN_HOST 4.70 A (code 94, 0x5E00, RSNS_RAC 0b), rewritten after every adapter removal; on the drawn board the derated 4.00 A | OWED (not applied) |
| 45 | 5 | R-26 | firmware | apply_fw_a16.py | with R-23 | firmware | Firmware: FW-A18's diagnostic (the pin's band, three readings, the fallback) | OWED (not applied) |
| 46 | 5 | R-27 | firmware | none: owed work | after R-06 | firmware | Firmware: FW-A09's U17 row recalibrated to R227 (5 mOhm in the PoE stage's input): full scale 16.384 A, Current_LSB 0.5 mA, CAL 2048; the readings are the stage's INPUT current and POE_VIN (VBUS pin 8; VBAT is POE_VIN plus the shunt's drop); a full-scale sample is a saturated transient, not a current; the output power inferred through the stage's efficiency | OWED (not applied) |
| 47 | 5 | R-28 | firmware | none: owed work | with the D-11 rules | firmware | Firmware: FW-A05's D-11 thresholds (15.5 V and 12.4 V rest floors, 60 s, 18 A unkey) and ChargeCurrent at most 3.0 A (FW-A02) kept, re-derived at bring-up | OWED (not applied) |
| 48 | 5 | R-126 | firmware | none: owed work | with R-125 | firmware | Firmware: rules R-a to R-d: R-a's state table with its S4 exception and the hold's persistence; R-b's two settings (ChargeCurrent() 0x0000 or 0x0200 and no other value while U3's SRN reading is under 14.0 V or the gauge reports XDSG or PRECHARGE); R-c's shedding sequence with the mat on measured headroom and the VSYS_UVP recovery; R-d's PCHG_COMM 1 and SUV check | OWED (not applied) |
| 49 | 5 | R-139 | firmware | none: owed work | with R-138 | firmware | Firmware: the hold (the expanders' outputs and the software enables U503 RB_SW_EN, U504 LORA_ON, U505 ZB_ON and GEIGER_EN; the charge by the charger's bit; the running module idled with its logging) and the SGP41's switch, thresholds and bus handling | OWED (not applied) |
| 50 | 5 | R-158 | firmware | none: owed work | only on a board A carrying R-157 (the BQ25730's register rules) | firmware | Firmware for (B1) (E11-28): EN_OOA 0 at boot; ChargeCurrent written for any charge (0 A at POR and after the watchdog's 175 s), the watchdog serviced or WDTMR_ADJ 00; VSYS_MIN, EN_LDO, EN_PORT_CTRL, BATFET_ENZ and BATFETOFF_HIZ never written from their power-on values; the device ID D5h checked; R-a's bit following the hold flag in every state (S4's exception withdrawn); R-b' (under VSYS_MIN ChargeCurrent 0x0080 only, no charge under 7.8 V on SRN) | OWED (not applied) |
| 51 | 5 | R-164 | firmware | none: owed work | with R-163 (F3's switches) | firmware | Firmware for F3: E5's deeper hold (the switch chip, NVMe slot 3, the PCIe switch and the GNSS off, the module logging on its own storage) | OWED (not applied) |
| 52 | 8 | R-129 | Layer 7, the DC receptacle and plug | none: a missing draft | before the harness is built | no draft yet | The DC receptacle and plug on MIL-DTL-38999 size 12 contacts (insert 17-6, or 13-26 with the solar pair on rated contacts elsewhere) | MISSING DRAFT (not applied) |
| 53 | 8 | R-130 | Layer 7, the interconnect | none: a missing draft | with R-129 | no draft yet | The DC interconnect specified by its loop, the NATO plug's pins to J_DCIN's board pins: cores and the NATO plug with a maker's rating of at least 20 A, the selected construction 3.05 m of AWG 14 with the 0.5 m lead | MISSING DRAFT (not applied) |
| 54 | 8 | R-131 | Layer 7, the inside lead and J_DCIN | none: a missing draft | with R-129 | no draft yet | The inside lead (a maker's rating of at least 20 A) and J_DCIN as a board connector rated at least 20 A, XT60 class of the gender opposite J_BATT's, or soldered lands | MISSING DRAFT (not applied) |
| 55 | 8 | R-111 | Layer 7, the enclosure | none: owed work | U-02: to T-H1's line | no draft yet | MESHSAT-1478 (U-02): the enclosure designed to T-H1's 2.159 W/K lid open with the fans (inside fins on the plate, mixer flow); the plate coupling of the radio modules and the LimeSDR as the fallback if T-H1 reads between 1.806 and 2.159 W/K; the NKK MBN cutouts; the combined route, if a T-H1 point reads under its line (R-104), is R-170 to R-172. This assignment does not close U-02 | OWED (not applied) |
| 56 | 8 | R-170 | Layer 7, the face plate's fins | none: owed work | U-02's combined route, only under a T-H1 point reading under its line (R-104); with R-171 and R-172, read together at the same point | no draft yet; conditional on T-H1's reading (R-104) | Under a T-H1 point reading under its line only (R-104: K1's 1.958 W/K with CFL-002's option C or 0.941 W/K with A or B; K6's 1.508 W/K) (U-02's combined route, item (a)): fins on the face's free strips, 0.0552 m2 (the plate 0.0912 m2 less the monitor window 0.0288 m2 and the e-paper lens 0.0071 m2), bonded to the 3 mm plate under M3's space beneath the QMX tray (19.92 mm nominal, 14.11 mm with the unstated allowances doubled), about 0.39 kg of 1.5 mm fins at an 8 mm pitch, the light guides kept clear; or a clip-on exchanger with its stowage. Passive: no power, no endurance change | OWED (not applied) |
| 57 | 8 | R-171 | Layer 7, the plate's conduction kit (heat pipes, bars and pads from board B's and the face's parts) | none: owed work | with R-170 (the plate the kit loads carries the fins) | no draft yet; conditional on T-H1's reading (R-104) | Under a T-H1 point reading under its line only (R-104: K1's 1.958 W/K with CFL-002's option C or 0.941 W/K with A or B; K6's 1.508 W/K) (U-02's combined route, item (b)): the large loads, 23.641 W at their pins (the Xenarc, the live WiFi card, the three CM5, panel board C, the KSZ9897R's rails, the three NVMe, the VHF PA), led into the plate by heat pipes, bars and gap pads in the 11.9 to 22.9 mm between board B's tall parts and the face parts (W4); the face's switches to +85 C parts (Layer 6's picks); the face's touch temperature evaluated (the plate at 55.12 C in the combined route, 70.08 C with (b) alone, at +40 C on the bound). Passive | OWED (not applied) |
| 58 | 8 | R-172 | Layer 7, the open lid's skin and its braid | none: owed work | with R-170 and R-171 | no draft yet; conditional on T-H1's reading (R-104) | Under a T-H1 point reading under its line only (R-104: K1's 1.958 W/K with CFL-002's option C or 0.941 W/K with A or B; K6's 1.508 W/K) (U-02's combined route, item (c)): the open lid as a second radiator, a 1 mm aluminium skin on the lid's flat ceiling (at most 0.0803 m2, shared with the QMX tray and the tablet bracket; 0.329 m tall when open) on a copper braid from the plate's edge inside the seal line (0.20 m, 200 mm2, 2.56 K/W assumed), about 0.58 kg, no penetration; the strap carries 4.37 W in the route. Passive | OWED (not applied) |
| 59 | U-01 | R-105 | board P, gen_sch_p.py | none: owed work | only under U-01's approach (II), after the owner's approval | no draft yet | Under U-01's approach (II) only: gen_sch_p.py U2 to the BQ7720704 (83 C, OVP 4.275 V, UVP 2.0 V, COUT an open-drain active pulldown) and F2's drive re-drawn; pcb_pack_protection.yaml re-derived; the ladder C1 75.0, H1 76.5, H2 77.0, OTD 77.5 C (first cut), SOT, the PTC, the release | OWED (not applied) |
| 60 | U-01 | R-106 | firmware, the gauge image | none: owed work | only under (II) | firmware | Under U-01's approach (II) only: the gauge image with the new cell's data, the re-derived ladder and cold cutoffs | OWED (not applied) |
| 61 | U-01 | R-154 | firmware, the gauge image and the host | a text draft (L4-E10 section 14b (out 9b)) | only under (II), with R-106 | a text draft | Under U-01's approach (II) only: L4-E10 section 14b's charge drafts in the gauge image, relayed by the host to the charger: Low Temp T1 -9 C to T2 1 C at 0.84 A to 16.40 V (BATOVP 17.06 V); Standard Temp low T2 1 C to T5 11 C at 1.68 A to 16.80 V; T5 11 C to T3 42 C at the drawn 3.00 A to 16.80 V (BATOVP 17.47 V); UTC -9.0 C (recovery -5.0 C); T3 42 C, T4 43 C and OTC 44.0 C kept; the kit's charge hold below -7 C (from +3 C), the mat warming the block first; CUV 2.50 to 2.75 V a cell; the termination current 250 mA (TI's default, ASSUMPTION) | DRAFTED (not applied) |
| 62 | ALT | R-119 | board E, gen_sch_e.py | apply_gen_sch_e_timer.py | the LM5069 alternative only: refuses once the selected entry (R-123) has run | L4-E11's RELEASE.md (R-147: check-l4e11-3.md at a15ab384) | D-09, only if the LM5069 is kept (the selected entry has no fault timer against a power limit): L4-E11's `apply_gen_sch_e_timer.py` (C5 GRM3195C1H104GA05 with C121 GRM3195C1H683JA05), ITIMER and VTMRH at temperature, tFAULT and the 2 mA turn-off with Q7's gate charge, the start into VIN_RAW (34 uF) with the front end held off by U34 | DRAFTED, the alternative only (not applied) |
| 63 | ALT | R-152 | board A, gen_sch_a.py | none: a missing draft | arrangement (A) only: withdrawn once R-157 is applied (its zone and height Layer 9's) | no draft yet | Arrangement (A) only, withdrawn once R-157 (B1) is applied: U-04's bounded fallback on VBAT, the charger's VSYS (L4-E11's E11-24, SESSION, never applied): one Panasonic EEHZK1V181P directly on VSYS (C242139) and a hold-up bank of four EEHZK1E471P (C242138) charged through R_CH 330 Ohm RC2512FK-07330RL (C137025) and discharging through D_H B540C-13-F (C72264); it takes D2 and D5 off TI's statements, not D1 or D3; the zone and the height are Layer 9's | MISSING DRAFT (not applied) |

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
| pack disconnected, or both FETs open, with a source | (B1): the BQ25730 regulates VSYS at VSYS_MIN through Q39 in LDO mode; as drawn (A): U3 holds VBAT at ChargeVoltage, CONDITIONAL on TI's D1 | (B1) at least 12.054 V (SLUSE65A p.10, printed); as drawn VSYS at least 16.716 V against VSYS_MIN 12.3 V once the mode is shown | L4-E11 12c, 9 (D1) |
| the charge inhibited (the hold's flag), the pack present | (B1): Q39 off, VSYS at the pack plus 150 mV, no battery current; as drawn (A): D3 open | (B1) VSRN + 150 mV within +-2 % | L4-E11 12c |
| the pack present, the source on | (B1): the BATFET fully on while charging or supplementing, VSYS_MIN the floor | VSYS from 12.054 V to 17.375 V | L4-E11 12c |

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
| power-on under (B1) | ChargeCurrent 0 A until firmware writes it; EN_OOA written 0 at boot; CELL_BATPRESZ a fixed 4S strap, never wired to battery presence; the docking inrush through Q39's body diode | the strap 75.14 % of VDDA; 242.9 A for 17.7 us, over IDM's 144 A (no body-diode pulse rating printed: R-160) | L4-E11 12a, 12e (R-157, R-158) |
| a dead pack (at or under CUV) | the gauge's CUV holds; U3 charges through the open discharge FET's body diode at its clamp (as drawn); under (B1) R-b' precharges through Q39 in LDO mode; rules R-a to R-d; the image's pre-charge | CUV 2.50 V a cell; as drawn the clamp 384 mA typical (no maximum printed: D7) and ChargeCurrent 256 mA at POR; (B1) 0x0080, at most 332.8 mA, no charge under 7.8 V on SRN | L4-E11 2, 4, 9, 12e |
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
| the panel lead's surge (CS116, CS115; D-12) | D4 (the SMCJ30A, drafted) on PV_P under the drafted entry's 50 V parts; with the block off D11 clamps the port | D4 at most 41.91 V at CS116's 10 A and 40.04 V at CS115's 5 A (hot end); a pulse over the cut-off turns the block off within 4 us | no trip; MEETS with the block on and off (R-174 records the loop current) | L4-E7 (D1, D2, the remedies) |
| the solar guard's over-voltage cut-off (D-10, a single fault: a stiff 36 V source on the solar port) | U21 (TPS48110-Q1) holds Q12 off: rising 28.55 to 31.06 V, falling 27.07 V or more (aged); its UVLO on at 8.44 V at most, under the stage's enable | the panel port from PV_P: the block never turns on, Q12 holds 36 of 100 V, D4 and the bulk see nothing | on again once the input falls under the falling threshold (drafted, R-173, not applied) | L4-E7 (the remedies, check 5) |
| a reversed panel (D-11, a single fault) | Q13 in the return stays off, its body diode reverse biased | the reversed panel: no current; the high side within 1 V of GND | none needed (drafted, R-173; CONDITIONAL on Q13's leakage above +25 C) | L4-E7 (the remedies); DECISION-31 E-N1 closed |
| a stiff source between 25 V and the cut-off (the residual band, R-175) | nothing at the entry: the backstop's current trip only | the stage runs, at most 116.5 W, outside REQ-016's window | layer 8's TRN-001 judgement (R-175) | L4-E7 (the remedies) |

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
| the panel controller (C:U3) | the charger falls back after its 175 s watchdog (as drawn to 256 mA; under (B1) to 0 A); the H3 line, U34, the entry, the backstop, OUTLET_OK, the eFuses, BATOVP and SYSOVP; the RP2040's own watchdog restarts it | the margin hold (E5's +70 C class goes unprotected); the key-down time limit (OUTLET_OK still drops the outlets); the expanders keep their last outputs | HW-FW-CONTRACT FW-A03, FW-A05, FW-A08; L4-E12 |
| the sensor controller (E:U10) | the gauge stops charging after its host watchdog's 10 s; the gauge's protections and the second level act alone; the RP2040's watchdog restarts it | the mixer fans' control (a stopped fan is the fans-off case, 72.38 to 85.36 C in E5); VIN_MON for FW-A16's diagnostic; the SGP41's switch | HW-FW-CONTRACT FW-E01, FW-E07, FW-E09 |
| both controllers | every hardware limit of 4e acts; the source bound holds with no firmware (the H3 line and the knee) | the charge ranges relayed from the gauge (UTC still holds the charge FET); the hold; the heater's policy | this record out 7 |
| the gauge's own firmware | the BQ7720700 and F2 (hardware) | COV, CUV, OCD, SCD and the temperature limits, which are the gauge's | pcb_pack_protection.yaml |

## 5. The implementation handover (out 19)

The selected topology is section 1's; its settings are the blocks of 1a and the change list of section 3; its interface limits
are the rows of 1d, drafted for Layer 5 in `LAYER5-HANDOVER.md` (LH-01 to LH-11; `pcb_interfaces.yaml` and `HW-FW-CONTRACT.md`
are not edited); its control behaviour is 1c and section 4. Every item reaches its later layer as a register row with one
owner and an acceptance (`DOWNSTREAM-REGISTER.md`, section 11). **Drafted, not applied:** no row is applied; a DRAFTED row has
a script or a text that refuses the tree until its release record reads "released: yes". **(B1)** reaches Layer 8 as R-157
(board A), Layer 5 and the firmware as R-158, Layer 9 as R-159 and R-161, Layer 6 as R-160 and R-162. **T-H1 at Layer 9** (the
bench, R-104) runs the procedure's points in its order K1, K5, K10, K6, then K7 and K8 (5c). **The combined route** reaches
Layer 7 as R-170 to R-172, each only under a point's line. **The cell** (the budget's 2b', L4-E10's comparison): the ruled 35E
stays the baseline; the Saft route reaches Layer 7 and Layer 6 only as R-167 to R-169, its adoption the owner's.

### 5a. The selected parts and their document revisions

| Ref | Part | Role | Document revision | Read from | State |
|---|---|---|---|---|---|
| U5 | LT8705AIUHF#PBF | the solar stage: hold, regulation RIMON_IN 31.6k, backstop on SWEN | 8705af | l4e7_stage_settings.out | DRAFTED (R-12, R-19 to R-21, R-98) |
| U6, Q7 | TPS48110-Q1 with CSD19536KTT | the vehicle entry's breaker and its pass FET | SLUSEE5E | l4e11_power.out | DRAFTED (R-123) |
| U21, Q12 (board E) | TPS48110AQDGXRQ1 with CSD19532Q5B | the solar guard's over-voltage cut-off (off above 28.55 to 31.06 V) and its FET | SLUSEE5E | l4e7_stage_settings.out | DRAFTED (R-173); U21's DGX-19 land owed |
| Q13 (board E) | CSD19532Q5B | the solar guard's return switch (a reversed panel blocked) | SLPS414B | ti-csd19532q5b-n-fet.pdf | DRAFTED (R-173); its leakage above +25 C CONDITIONAL |
| D4 (board E) | SMCJ30A | the solar entry's clamp, from the SMCJ28A | SMCJ30A | littelfuse-smcj-series-tvs.pdf | DRAFTED (R-173); its LCSC code owed |
| D11 (board E) | SMCJ40CA | the solar port's two-way clamp | SMCJ40CA | littelfuse-smcj-series-tvs.pdf | DRAFTED (R-173) |
| Q7's sheet | CSD19536KTT | the pass FET's safe operating area | SLPS540C | l4e11_power.out | DRAFTED (R-123) |
| Q1 | CSD19532Q5B | the ideal diode's FET, 100 V | SLPS414B | ti-csd19532q5b-n-fet.pdf | DRAFTED (R-17) |
| U3 (board E) | LM74700-Q1 | the vehicle entry's ideal-diode controller | SNOSD17G | ti-lm74700-q1.pdf | as drawn |
| U2 | LM5176 | the front end to VBUS20 | SNVSAI1D | lm5176-datasheet.pdf | as drawn; R11, R12 DRAFTED (R-04, R-01) |
| U3 (board A) | BQ25731 | the charger onto VBAT = VSYS, as drawn | SLUSE66A | bq25731-datasheet.pdf | as drawn; replaced in (B1) by the BQ25730 (R-157) |
| U3 (board A), (B1) | BQ25730RSNR | the selected charger: VSYS bounded in all three modes; BATDRV on pin 21 | SLUSE65A | l4e11_power.out | DRAFTED (R-157), not applied; LCSC stock 0 (R-162) |
| Q39 (board A), (B1) | AOS AONS21357 | the battery FET between VBAT and CH_BATQ | Rev 2.1 | l4e11_power.out | DRAFTED (R-157); its thermal bar R-159, its pulse R-160 |
| U17 and five more | INA226 | the rail monitors; U17 moved onto R227 | SBOS547C | ti-ina226.pdf | DRAFTED (R-06) |
| eFuses | TPS2596 | the load converters' inputs, 21 V absolute | SLVSET8A | tps2596.pdf | as drawn |
| U1 (board P) | BQ4050 | the pack's gauge and its FETs | SLUUAQ3A | l4e11_power.out | as drawn; U-01's (II) re-derives it (R-106) |
| U2 (board P) | BQ7720700 | the second-level protector | BQ7720700 | gen_sch_p.py | as drawn; BQ7720704 under U-01's (II) (R-105) |
| F2 (board P) | SCF9550-30-05 | the self-control fuse | SCF9550-30-05 | gen_sch_p.py | as drawn; Eaton's statement owed (R-103) |
| F1 (board E) | Littelfuse 0997010.WXN | the vehicle fuse, 58 V DC | rev2025-11-18 | littelfuse-997-mini58v-rev2025-11-18.pdf | DRAFTED (R-18), its 20 A holder owed (R-132) |
| the bank | Panasonic EEHZK1V331P with HoJLR2512 45 mOhm | VBUS20's six cans and their ballasts | EEHZK1V331P | ripple_dense.out | DRAFTED (R-07) |
| the cells | Samsung INR18650-35E, 4S3P | D-06's ruled cell | INR18650-35E | pcb_pack_protection.yaml | as ruled (144.72 Wh nominal, 107.9 Wh, 2.52 h); the Saft MP 176065 xtd 4S1P a PROPOSAL compared in 2b' (81.76 Wh nominal, 53.5 to 58.8 Wh, 1.25 to 1.37 h, MODELLED): adoption not supported yet, the owner's approval required; the HL18650V a PROPOSAL (U-01) |
| the alternative only | LM5069 | the drawn hot swap, kept only as the alternative | SNVS452G | ti-lm5069.pdf | superseded by R-123 |

### 5b. Every register row by the later layer that receives it

| Layer | Owners | Register rows | By kind | By state |
|---|---|---|---|---|
| 4 (release records) | Layer 4 coordinator | 9: R-47, R-90, R-91, R-92, R-93, R-128, R-135, R-147, R-155 | EVIDENCE 3; IMPLEMENTATION 1; RELEASE 5 | DRAFTED 1; OWED 8; APPLIED 0 |
| 5 | Layer 5 interfaces, CONOPS owner | 5: R-23, R-24, R-125, R-133, R-138 | IMPLEMENTATION 5 | DRAFTED 5; APPLIED 0 |
| 5 (firmware, by the contract) | firmware owner | 10: R-25, R-26, R-27, R-28, R-106, R-126, R-139, R-154, R-158, R-164 | IMPLEMENTATION 10 | DRAFTED 1; OWED 9; APPLIED 0 |
| 6 | Layer 6 components | 24: R-30, R-31, R-32, R-33, R-34, R-35, R-36, R-101, R-102, R-103, R-113, R-114, R-115, R-136, R-141, R-142, R-143, R-148, R-149, R-150, R-160, R-162, R-165, R-168 | EVIDENCE 23; TEST 1 | OWED 24; APPLIED 0 |
| 7 | Layer 7 mechanical | 9: R-29, R-111, R-129, R-130, R-131, R-167, R-170, R-171, R-172 | EVIDENCE 1; IMPLEMENTATION 7; TEST 1 | MISSING DRAFT 3; OWED 6; APPLIED 0 |
| 8 | Layer 8 board A generator owner, Layer 8 board E generator owner, Layer 8 board P generator owner, Layer 8 board B generator owner, Layer 8 board C generator owner | 43: R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-08, R-09, R-10, R-11, R-12, R-13, R-14, R-15, R-16, R-17, R-18, R-19, R-20, R-21, R-22, R-94, R-95, R-96, R-98, R-100, R-105, R-107, R-116, R-123, R-124, R-132, R-144, R-145, R-152, R-156, R-157, R-163, R-166, R-173, R-174, R-175 | EVIDENCE 3; IMPLEMENTATION 39; TEST 1 | DRAFTED 20; MISSING DRAFT 16; OWED 7; APPLIED 0 |
| 9 | Layer 9 pre-layout analysis | 24: R-37, R-38, R-39, R-40, R-41, R-42, R-43, R-44, R-45, R-46, R-48, R-49, R-50, R-51, R-52, R-97, R-108, R-117, R-119, R-120, R-127, R-134, R-146, R-159 | EVIDENCE 10; LAYOUT 14 | OWED 24; APPLIED 0 |
| 9 (the bench) | prototype bench | 39: R-60, R-61, R-62, R-63, R-64, R-65, R-66, R-67, R-68, R-69, R-70, R-71, R-72, R-73, R-74, R-75, R-76, R-77, R-78, R-79, R-80, R-81, R-82, R-83, R-84, R-85, R-86, R-99, R-104, R-109, R-112, R-118, R-121, R-122, R-137, R-153, R-161, R-169, R-176 | TEST 39 | OWED 39; APPLIED 0 |
| 9 (the test plan) | TEST-PLAN owner | 3: R-110, R-140, R-151 | EVIDENCE 2; TEST 1 | DRAFTED 1; OWED 2; APPLIED 0 |

### 5c. T-H1's points at Layer 9, in order (out 19)

<!-- gen:th1:begin -->
**T-H1 at Layer 9 (the bench, R-104), in the procedure's order K1, K5, K10, K6, then K7 and K8** (L4-E12 11g, check 7). Each point runs at its mode's heat with the heaters set to it less the fans' measured draw (P = the heaters + the fans). This supersedes the earlier P1 at the profile's 42.4 W (X2, a state no requirement asks for, its fans left out) and the 21.2 W one-point bands where they differ: E5's line is read at its own heat (2.455 W/K at 21.587 W replaces 2.416 W/K), and 9f's fallback lines, computed at 21.2 W, stay as conservative lines. Authorising the bench is the owner's (OW-8); accepting a result goes through the coordinator's check.
<!-- gen:th1:end -->

| T-H1 point | Configuration | The reading | Settles | Read from |
|---|---|---|---|---|
| K1, first: the heat stage at +40 C | lid open; the heaters 25.136 W plus the fans' 1.95 W (P 27.086 W); room air; steady state or the three-time-constant fit (11g) | at least 1.958 W/K (rise 13.8 K, U 7.8 %) | closes K1, K3, K4 and K9 (needs 1.806, 0.903, 0.602 and 1.806 W/K); the line that governs is CFL-002's: K1 with option C, K3 with A or B (at least 0.941 W/K) | L4-E12 11e, 11f, check 7 |
| K5 | lid closed; the heaters 25.136 W plus the fans' 1.95 W (P 27.086 W); room air; steady state or the three-time-constant fit (11g) | at least 1.958 W/K (rise 13.8 K, U 7.8 %) | REQ-052 and E3-L at +40 C, lid closed (needs 1.806 W/K) | L4-E12 11e |
| K10 | lid open; the heaters 19.637 W plus the fans' 1.95 W (P 21.587 W); room air; steady state or the three-time-constant fit (11g) | at least 2.455 W/K (rise 8.8 K, U 12.1 %) | E5's line under the hold (needs 2.159 W/K; replaces 2.416 W/K at one heater's 21.2 W) | L4-E12 11e, 16.8 |
| K6 | lid open; the heaters 40.443 W plus the fans' 2.97 W (P 43.413 W); room air; steady state or the three-time-constant fit (11g) | at least 1.508 W/K (rise 28.8 K, U 4.0 %) | the profile unshed at REQ-014's +20 C, under C1's +50 C (needs 1.447 W/K) | L4-E12 11e |
| K7, K8 | lid open; the heaters 43.889 W plus the fans' 2.97 W (P 46.859 W); room air; steady state or the three-time-constant fit (11g) | at least 1.698 W/K (rise 27.6 K, U 4.2 %); at least 2.081 W/K (rise 22.5 K, U 5.0 %) | charging with the profile on SC-37's design day, cold and warm ends (needs 1.627 and 1.977 W/K) | L4-E12 11e |
| the route, only under a point's line | the same point with the combined route fitted (R-170 to R-172) | the point's own line | the route's effect at that heat (L4-E12 15 computed it at the profile's heat only); still short, the owner's: CFL-002's other options, or the case's thermal design or the device set | L4-E12 15, check 6 |
| 9f's fallback lines | read at K10's and K1's points | 1.516, 1.410, 1.199, 0.951 and 0.644 W/K (computed at 21.2 W) | the session measures' lines (section 8 of L4-E12); conservative at E3-O's own heat (16.8) | L4-E12 9f, 16.8 |
| open after the points | none on this bench | none | K2 (the SGP41 on Table 4, CFL-002), the part-level hot spots (T-H2, THM-001), the fans' rating (D-18), full sun (D-02e), the cells at +40 C (U-01) | L4-E12 11f |

## 6. The exit statement (out 20)

<!-- gen:deciding:begin -->
**The thermal question (U-02), corrected by L4-E12's reconciliation (check 7 at `6f8fd652`).** This record's earlier framing, that the approved profile is not thermally feasible at +40 C and that 1.447 W/K is the deciding reading, is WITHDRAWN: the 42.8 W profile is not required at +40 C. REQ-024's C1 sheds it to the reduced mode and the heat stage on +50 C inside air or a +55 C cell, and the decisions run the reduced mode above +35 C ambient (D-02b). **The required state at REQ-024's +40 C is the heat stage, 27.086 W**, and its lines are K1, the SGP41's +55 C (REQ-052: "an SGP41 above +55 C fails"; REQ-024's acceptance): 1.806 W/K, a bench reading of at least 1.958 W/K with the heaters at 25.136 W plus the fans; K2, the SGP41 on its Table 4 +50 C: 2.709 W/K; and K3, the +70 C class: 0.903 W/K, a reading of at least 0.941 W/K.

**The owner's CFL-002 decides which line governs.** With option C (the SGP41 kept powered) K1 governs, and it lies at or over the case's cap: the outside films cap the conductance at 1.504 W/K at the conservative ends and 1.859 W/K at the other ends (K1 under it there by 0.053 W/K), so on the bound's outside no inside measure reaches K1 at the conservative ends. With option A (a +85 C gas sensor in its place) or B (the bay VOC channel dropped) K1 and K2 fall away and K3's 0.903 W/K governs, about half, read at 0.941 W/K. The conservative bound gives 0.598 to 0.661 W/K at K1's 15 K rise: under both lines, so T-H1 decides, it does not confirm; missing evidence is not proof of a shortfall.

**Its executable resolution path.** The owner rules CFL-002 (OW-1) and authorises T-H1 (OW-8); the bench (R-104) runs the procedure's points in order (L4-E12 11g): K1, the heat stage lid open, the heaters at 25.136 W plus the fans, a reading of at least 1.958 W/K closing K1, K3, K4 and K9 (0.941 W/K suffices for K3 alone); K5, the same lid closed (1.958 W/K); K10, E5's hold, 21.587 W (2.455 W/K); K6, the profile at REQ-014's +20 C, 43.413 W under C1's +50 C (needs 1.447 W/K, read at 1.508 W/K); then K7 and K8, charging with the profile running on SC-37's design day, 46.859 W with the charge path counted (needs 1.627 to 1.977 W/K, read at 1.698 and 2.081 W/K). Under a point's line the combined heat-rejection route (R-170 to R-172) is fitted and read at the same point; if it still reads short, the owner's: with option C, CFL-002's option A or B; with A or B, a deviation of E3-O or a device-set re-pick (CHO-001).
<!-- gen:deciding:end -->

**The owner's definition** (2 October 2026): "Layer 4 power closure requires a selected architecture whose mandatory operating
requirements have a defensible feasibility basis, consistent interfaces, and explicit implementation obligations. A downstream
qualification test may remain open where the design already has bounded supporting evidence and a workable fallback. An unknown
that could invalidate the selected architecture stays a closure condition."

**Against it, on this record's reading with the consolidation's results integrated:** the architecture is selected (section 1),
its interfaces are consistent and stated (1d, with no row NOT MET or PENDING),
and its implementation obligations are explicit
(sections 3 and 5). What is not met is the feasibility basis of three mandatory operating cases, each an architecture-level
choice on the board as drawn:

| U | Class | The exact missing fact | The smallest experiment or manufacturer clarification | The bounded evidence today | The fallback | What it decides | The result |
|---|---|---|---|---|---|---|---|
| U-01 | (ii) as ruled (the 35E unsuitable on its own published evidence); a supported route on published evidence exists (the Saft MP 176065 xtd), its adoption not supported yet and the owner's approval required | with the ruled 35E, LO-01d to LO-01g UNSUITABLE on its own published evidence (E3-O's cells 61.26 to 72.42 C over +60 C; E5's idle pack 74.73 C; +71 C and -33 C storage); with the Saft MP 176065 xtd: whether four cells fit along the pocket's axis with at most 1.40 mm of wrap, whether one cell carries 18 A for 60 s (its 22 A pulses state no duration), and T-H1 for LO-01a's complete pass and LO-01e | a printed mock-up of four cells at the sheet's maximum dimensions in the pocket (hours, no purchase; R-167); Saft's statement or one cell pulsed at 18 A for 60 s at +25 C and at the cold end (NZ$ 238.72 and a 20 A load, a day; R-168); T-H1 (R-104); for the higher-energy HL18650V its signed specification or a lot soak (USD 35.00, 4 to 12 days) | Saft's published datasheet covers every cell-limit row (charge -30 to +85 C, discharge -40 to +85 C at 11 A continuous, storage allowable -40 to +85 C); L4-E10's comparison (check 6): 81.76 Wh nominal against the 35E's 144.72 Wh, 53.5 to 58.8 Wh usable and 1.25 to 1.37 h battery-only against 107.9 Wh and 2.52 h (MODELLED: Saft prints no curve); L4-E12's bound lies far under LO-01a's 1.6664 W/K lid closed (0.505 to 0.537 W/K) | the HL18650V (90.2 Wh usable) on its specification or a soak; with no approval U-01 stays a release gate; (I)'s powered cooling is INCONCLUSIVE (8.18 to 35.21 W into the sealed case) | the owner's adoption of D-06's cell, energy (144.72 to 81.76 Wh nominal) and spend (NZ$ 954.88 for four), not yet supported: the fit mock-up, 18 A for 60 s, Saft's missing figures, the gauge data and T-H1 awaited, the owner's approval required; the topology stays; missing evidence is not proof that no cell meets the rows | integrated: L4-E10's cell route, checks 4 and 5 at 1c321773 (a supported route on published evidence) |
| U-02 | (ii) a closure condition | the sealed case's conductance lid open with the fans at full duty, at each required mode's heat: what the fans' inside film adds to L4-E12's conservative bound (0.598 to 0.661 W/K at K1's rise at +40 C; 0.566 W/K at E5, 0.607 W/K at E3-O; the film credited at zero); and which line governs at +40 C, the owner's CFL-002 | T-H1's points in the procedure's order (R-104; L4-E12 11g): K1, the heat stage lid open, the heaters 25.136 W plus the fans, a reading of at least 1.958 W/K closing K1, K3, K4 and K9 (0.941 W/K for K3 alone); K5 lid closed (1.958 W/K); K10, E5's hold (2.455 W/K); K6, the profile at REQ-014's +20 C (1.508 W/K); K7 and K8, charging with the profile (1.698 and 2.081 W/K); under a point's line the combined route (R-170 to R-172) read at the same point; CFL-002 ruled (OW-1); OW-8 authorises the bench | at +40 C the required state is the heat stage, 27.086 W (REQ-024's C1; D-02b): K1 the SGP41's +55 C 1.806 W/K (option C), K2 its Table 4 +50 C 2.709 W/K, K3 the +70 C class 0.903 W/K (options A, B); K1 at or over the outside films' cap at the conservative ends (1.504 W/K; 1.859 W/K at the other ends); the profile's own line K6 at +20 C 1.447 W/K, which the heat-rejection approaches reach to 1.384 W/K on the bound at the profile's heat; at E5's hold with every session measure E5 holds (0.671 against 0.621 W/K) and E3-O falls 0.212 W/K short (the module's intake 92.61 C) | the combined route, passive, under a point's line (R-170 to R-172); for E5 and E3-O the session's measures (F4, F3 in E5, board B's +85 C connectors, the HX magnetics, the wider buttons; R-111, R-141, R-163 to R-166); with option C still short, CFL-002's option A or B (the owner's); with A or B still short, a deviation of E3-O or a device-set re-pick (the owner's) | at or over the governing line at K1's point the architecture stands (option C: 1.958 W/K; options A, B: 0.941 W/K); under it, with the route reading at or over it, it stands with the route; still under, the owner's (CFL-002, the case's thermal design or the device set), never the power path's topology; T-H1 decides, it does not merely confirm; missing evidence is not proof of a shortfall | integrated: L4-E12's thermal verdict (check 5 at 7f41632d), its heat-rejection comparison (check 6 at 589f18ac) and its thermal reconciliation (check 7 at 6f8fd652: the heat stage at +40 C, its line the owner's CFL-002) |
| U-04 | (i) once R-157 (B1) is applied; (ii) on the board as drawn | with (B1): D2 (load steps against the 2.054 V margin), Q39's installed thermal path (at most 20.54 C/W) and its docking pulse (242.9 A for 17.7 us), D6, D8, D9, D10 and the BQ25730's supply; on the board as drawn, TI's D1 and D3 | apply R-157 (apply_gen_sch_a_charger.py, after L4-E11's release record); then the three modes and D2 on one build (R-161), the layout's RthJA (R-159) and AOS's pulse statement or a sample pulse (R-160); Q-TI-15, Q-TI-16 and Q-AOS-1 sent (OW-7) | SLUSE65A prints VSYS in all three modes: at least 12.054 V with no battery, VSRN + 150 mV within +-2 % inhibited, VSYS_MIN the floor; Q39 0.0945 W at the profile | R-c's step rule (D2); the gauge's OCD1 set to the installed path (the thermal bar); a slower discharge-FET turn-on (the docking pulse); arrangement (A) with E11-24's hold-up if (B1) fails | once R-157 is applied, nothing of the architecture (L4-E11 check 5); on the board as drawn TI's D1 and D3 decide the charger's power path | integrated: L4-E11's charger selection, check 5 at 5aa18a69 ((B1) selected) |

**The known defects beside them** (L4-E7's panel-lead derivation, set 27; 7a and 8a). They are defects of the power path at
the solar entry, single faults, known and **addressed in drafts**: L4-E7's selected remedies (check 5 at `573fd5b8`), drafted in
`apply_gen_sch_e_solar_guard.py` (R-173), not applied, D-11 CONDITIONAL on Q13's hot leakage; the band between 25 V and the
cut-off is a residual named for layer 8 (R-175); none changes the topology:

| Defect | Its fault | State | The missing step | The evidence still needed | What it decides |
|---|---|---|---|---|---|
| D-10 | a stiff 36 V source on the solar port (a single fault) | ADDRESSED IN DRAFTS: a selected remedy (L4-E7, check 5), drafted in apply_gen_sch_e_solar_guard.py (R-173), not applied; the cut-off rises at 28.55 to 31.06 V, falls back at 27.07 V or more | the draft applied after its release record (R-92's L4-E7 RELEASE.md) | the SMCJ30A's LCSC code, U21's DGX-19 land, the regeneration and its gates, the bench rows (R-176) | nothing of the topology: protection added at the solar entry |
| D-11 | a reversed panel (E-N1, a single fault) | ADDRESSED IN DRAFTS: a selected remedy (L4-E7, check 5), drafted in apply_gen_sch_e_solar_guard.py (R-173), not applied; CONDITIONAL on Q13's leakage above +25 C | the same draft | Q13's leakage at the hot end (R-176) | nothing of the topology: protection added at the solar entry |
| D-12 | CS116 and CS115 on the panel lead, as drawn | RESOLVED in the drafted entry (R-21, R-173): MEETS with the block on and off | the loop current recorded (R-174) | the test of R-174 at layer 8 | nothing: the drafted entry's parts |
| residual | a stiff source between 25 V and the cut-off (outside the window) | a residual named for layer 8: the stage runs, at most 116.5 W under the backstop's trip | TRN-001's judgement whether the single fault needs more (R-175) | the cut-off cannot go below CS101's 27.82 V input peak without a different immunity basis | not the topology |

<!-- gen:ledger:begin -->
**The findings ledger** (`records/l4close/FINDINGS-LEDGER.md`, set 27's integration): 58 rows of rejected collaborator findings, 24 CLOSED, 23 CLOSED AS CONDITIONAL, 11 OPEN DOWNSTREAM and 0 STILL OPEN. The four rows that were still open (two findings) are CLOSED AS CONDITIONAL: L4-E12:1.3 and 2.2 on R-139's restated bench test (item 5's DIFFERS resolved by that correction, recorded in VERIFICATION-2026-10-02.md), and L4-E7R:1.6 and 2.4 on L4-E7's drafted, checked remedies (check-l4e7r-5), Q13's hot leakage and R-175.
<!-- gen:ledger:end -->

**The exit: Layer 4 power closure is not reached on this reading.** U-04's result is in: L4-E11 selects (B1), TI's BQ25730
with the battery FET Q39 (check 5 at `5aa18a69`), whose maker's sheet bounds VSYS in all three modes; once its draft (R-157) is
applied U-04 is a downstream qualification test with bounded evidence and a workable fallback, and on the board as drawn it
stays a closure condition. U-02's result is in: L4-E12's conservative bound (check 5 at `7f41632d`) lies under the stated lines,
so T-H1 decides rather than confirms, and U-02 stays a closure condition. Its reconciliation (check 7 at `6f8fd652`) withdraws
this record's earlier framing, the profile at +40 C with 1.447 W/K as the deciding reading: at +40 C the required state is the
heat stage, and **the owner's CFL-002 decides which line it must meet**, K1 (the SGP41's +55 C, 1.806 W/K) with option C or K3
(the +70 C class, 0.903 W/K) with options A and B (the top of this section). U-01's result is in: L4-E10 (checks 4, 5 and 6 at
`e2d20bf2`) finds a supported route on published manufacturer evidence, the Saft MP 176065 xtd as 4S1P, and compares it with
the approved pack on one boundary (2b'): 81.76 against 144.72 Wh nominal, 1.25 to 1.37 h against 2.52 h (MODELLED); the
evidence does not yet support its adoption (the fit mock-up, 18 A for 60 s, Saft's missing figures, the gauge data and T-H1
awaited), and the owner's approval is required; the ruled 35E is unsuitable on its own published evidence for the margins. The panel lead's surge is in too (L4-E7, set 27): CS116 meets on the drafted entry and CS115 is conditional on the loop current,
while a stiff 36 V source on the port (D-10) and a reversed panel (D-11) are addressed in drafts by L4-E7's selected remedies
(check 5; R-173, not applied), the band between 25 V and the cut-off named for layer 8 (R-175). **Missing evidence is not proof of impossibility:** every missing fact above has a named experiment
or manufacturer clarification that settles it, and none of them is counted as done.

## 7. Standalone analyses, each answering a named question

| Analysis | The question it answers | Where |
|---|---|---|
| Part A | Do Q1, F1 and U17 hold their normal, reverse, transient and fault conditions with the raised ceiling? | `L4E9-ENTRY-PROPOSALS.md`, out 11 |
| E11-19 | Does any finding that rested on the LM5069's power limit survive the selected TPS48110-Q1 entry? | out 12 |
| The budget's bounds | What do L4-E7R's accepted stage, the tablet's window and a cold store do to the replay's endurance figures, without re-running it? | 2b, out 16 (INFERRED bounds, the method stated) |
| The profile's heat at T-H1's line | At which ambient does the approved profile reach C1's shedding trigger at the binding line? | 2c (H1), out 16 |
| The heat rejection, read | If T-H1 reads under the profile's need, what restores it inside the rulings? | L4-E12 section 15 (check 6), read into 2c, 5c and section 6 (out 16c', 19, 20, 22); not recomputed |

| The panel lead's surge and its remedies, read | Which disturbances on the panel lead does the candidate meet, and what addresses the two that it did not? | 7a, out 23; L4-E7's verdicts and remedies read, not recomputed (check 5) |

No other analysis is added by the consolidation: every other figure is read from its record.

### 7a. The panel lead's surge: L4-E7's verdicts and the two remedies compared (out 23)

L4-E7's derivation (set 27 at `6d76453e`; `L4E7-CONTROL-DECISION.md`, "The panel lead's surge and sustained over-voltage,
derived") takes the panel lead's surge as MIL-STD-461G CS116 and CS115, the transients of the "Ground, Army" row REQ-063
commits to (both A), and adds the sustained cases: the panel's cold open circuit, a stiff source on the port by mistake and a
reversed panel. The criterion is REQ-016's: D4's clamp at the disturbance's current, with its tolerance, at or under the lowest
limit on PV_P (50 V on the drafted entry, 35 V as drawn). Two verdicts were **known defects of the candidate's power path at the
solar entry, single faults** (D-10, D-11). L4-E7's author selected a remedy for each in a separate round, with its circuit changes
and a bounded analysis (the owner's amendment of 2 October 2026, 14:20), accepted by the coordinator's check 5 at `573fd5b8`: the
table's "drafted entry" column reads the entry with that guard. The remedies below are L4-E7's comparison as filed.

| Disturbance | Source, waveform and duration | D4 at its current | The drafted entry | As drawn | Defect and register |
|---|---|---|---|---|---|
| D1 | CS116 on PV_IN alone and on the J_SOLAR cable (MIL-STD-461G 5.14): damped sinusoids, Ip to 10 A from 1 to 30 MHz, the lead's 15.0 MHz added; five minutes | 41.91 V with the SMCJ30A (10 A, hot end; 39.00 V with the drawn SMCJ28A) | MEETS (its 50 V parts; the block on or off) | NOT MET (39.00 > 35 V) | D-12 (R-21, R-173); R-174 |
| D2 | CS115 on the cable (5.13): 5 A, 30 ns, 30 Hz for one minute; the loop current recorded, not limited | 40.04 V with the SMCJ30A (5 A, hot end) | MEETS (the block on or off; a pulse over the cut-off turns it off within 4 us) | NOT MET (37.34 > 35 V) | D-12; R-174 |
| D3 | the panel's cold open circuit, 25 V at most at -20 C, held | 25 V, under its 28 V standoff (the SMCJ30A's 30 V drafted) | MEETS (CONDITIONAL on PANEL-ACC) | MEETS | R-35 |
| D4 | a stiff source on the port (the declared 9 to 36 V) through the lead's 0.0465 Ohm loop and F2, held | nothing with the guard; without it conducts 2.7 to 16.6 A, 95.9 to 585.8 W against 1.17 W on the board | MEETS with the guard: the cut-off rises at 28.55 to 31.06 V, the block never turns on, Q12 holds 36 of 100 V | NOT MET | D-10; R-173 (drafted) |
| D5 | a reversed panel (DECISION-31's E-N1), the panel's 6.802 A forward, held | nothing with the guard; without it forward, inside 1.17 W only below a 0.172 V drop | MEETS with Q13 in the return, CONDITIONAL on its leakage above +25 C | NOT MET | D-11; R-173 (drafted) |
| the residual band | a stiff source between 25 V and the cut-off (outside REQ-016's window, a single fault) | nothing: the block stays on | the stage runs under the backstop's current trip, at most 116.5 W: not claimed, a residual for layer 8 | the same | R-175 (TRN-001's judgement) |
| beyond the basis | a direct strike, or one nearer than MIL-STD-464's nearby lightning (CS117 S, not taken) | D11's own rating with the guard, 23.3 A at 10/1000 us | a residual outside every requirement | D4's own rating | R-156; REQ-041's mast-down alarm |

| Remedy | What it changes (as L4-E7 compared it) | D-10, a 36 V source | D-11, a reversed panel | L4-E7's verdict |
|---|---|---|---|---|
| (1) | the TPS48110-Q1 alone driving back-to-back FETs (SLUSEE5E Figure 9-14) | closed | its VS, CS+ and ISCP pins rated -1 V see the reversal | not taken (L4-E7) |
| (2) | the LM74700-Q1 ideal diode ahead of the TPS48110-Q1 (the vehicle entry's pair) | closed | closed | not taken: CATHODE to ANODE 76.21 V under CS116's negative lobes against 75 V, and CS101's ripple rectified inside M2's band (L4-E7) |
| (3) | U21 TPS48110AQDGXRQ1 with Q12 CSD19532Q5B and R87 4.5 mOhm (L4-E11's network but the OV divider, R98 90.9k + R99 95.3k over R100 7.68k); Q13 CSD19532Q5B in the return (PV_RTN) with R101, R102 and D12 BZT52C12; D11 SMCJ40CA across the port and C131 1 uF 100 V on PV_F; D4 to SMCJ30A | closed: off above 28.55 to 31.06 V rising, back under 27.07 V or more | closed, CONDITIONAL on Q13's leakage above +25 C | SELECTED by L4-E7 (SESSION; check 5): the path linear when on, no control on a reverse current; drafted in apply_gen_sch_e_solar_guard.py (7 edits), not applied |
| TVS only | SMCJ36A with the entry's 50 V parts at the 63 V class | closed at D4 | not closed | evaluated and not taken: it re-opens the CS101 correction and runs the stage at 105.73 to 135.26 W from 36 V |

<!-- gen:surge:begin -->
**The remedies are selected and drafted, not applied** (L4-E7, its check 5 at `573fd5b8`). D-10: the over-voltage cut-off, U21 with Q12, rises at 28.55 to 31.06 V and falls back at 27.07 V or more (aged), 0.731 V over CS101's peak at the input, 0.737 V under the SMCJ30A's least breakdown at the cold end and 2.07 V over 25 V on the fall, so it never trips inside REQ-016's window and the block never turns on under a 36 V source. D-11: Q13 in the return blocks a reversed panel, CONDITIONAL on its leakage above +25 C (printed at 25 C only). With the block in the path CS116 and CS115 MEET, on or off. Re-run: CS101's worst ripple 0.0591 A against the 0.113 A margin; check (b)'s allowance 1.021 ms (the accepted 1.087 ms); the static bound 93.5954 W (93.5521 W without it). The block's loss: 0.217 W at the regulation's highest current, 1.31 Wh on SC-37's day (0.39 %). **Named for layer 8:** a stiff source between 25 V and the cut-off is outside the window but still runs the stage, at most 116.5 W under the backstop's current trip (R-175); the cut-off cannot go below CS101's 27.82 V input peak without a different immunity basis. Owed: the SMCJ30A's LCSC code, U21's DGX-19 land, the regeneration and the bench rows (R-176). The guard adds protection and changes no topology.
<!-- gen:surge:end -->

## 8. The closure gate in detail (criteria 1 to 5)

The gate's rule, held by the script (out 9) and by `test_l4e9.py`: a criterion reads PASS only on interface rows that read
MEETS, never on an ASSUMPTION, CONDITIONAL or PENDING row; never while an unresolved choice it names stands; and criterion 2
never while a material defect is open. Every feasibility claim below cites its evidence by class; the software tests establish
tested behaviour of the record's own scripts and drafts only, never an electrical or thermal property.

| Criterion | Evidence | Verdict | The exact constraint (if not PASS) | Could it overturn the architecture? |
|---|---|---|---|---|
| 1. One architecture selected; its mandatory functions have a defensible feasibility basis | A1 under D-06 (section 1); rows IF-02, IF-04, IF-05, IF-07, IF-09, IF-10, IF-11, IF-12, IF-13: REQ-014 (the pack), REQ-015 (IF-04 to IF-06, MAKER and INFERRED; at 9.00 V at the plug with no usable pack U-04's CONDITIONAL CANDIDATE), REQ-016 (IF-01, IF-02, CONDITIONAL and MODELED; the panel PANEL-ACC, L4-E13), REQ-017 (IF-12, IF-13), REQ-018 (IF-10, IF-14), REQ-045 (4e, D-06 resolved in design), REQ-046 and REQ-077 (IF-10, L4-E10), REQ-075 (IF-09); the electronics at the margins (IF-11, L4-E12); choices U-01, U-02 and U-04 (U-03 moved downstream, update round 3), each restated by its dependency round (L4-E10, L4-E12 and L4-E11, update round 5, out 14) | CONDITIONAL | the solar function's 100 W bound is CONDITIONAL on G_CM and U18's VIN+ bias (L4-E7R) and its panel on PANEL-ACC (U-03, a CONDITIONAL DOWNSTREAM UNIT SELECTION since L4-E13: no unit bought or measured, R-35); REQ-015 at 9.00 V at the plug is a CONDITIONAL CANDIDATE on E11-05, E11-06, E11-09, E11-22 and E11-23 (U-04; L4-E11's consolidation, check 5 at 5aa18a69, selects (B1), the BQ25730 with Q39, drafted: once applied U-04 is a downstream qualification test, on the board as drawn TI's D1 and D3 decide it); the electronics at the margins and the heat stage at +40 C are CONDITIONAL on T-H1 (U-02; L4-E12's consolidation, check 5 at 7f41632d: the conservative bound, 0.566 to 0.607 W/K, lies under the lines, so T-H1 decides; its thermal reconciliation, check 7 at 6f8fd652: at +40 C the required state is the heat stage, its line set by the owner's CFL-002, K1 1.806 W/K with option C or K3 0.903 W/K with options A and B); the battery path's thermal design is FEA-008's (U-01; L4-E10's round, check 4 at e464ff88, states the limits by mode, the charge drafts and the usable energy); PS-ALLTX's chain at 18 A for 60 s (PWR-F12) is an open obligation | possibly, on named evidence only: U-01 on the HL18650V's signed specification (D-06's pack energy, protection settings and charge ranges), U-02 on T-H1's points under the line CFL-002 sets with the combined route also reading under it (CFL-002's other options, the sealed case's thermal design or a device-set re-pick, the owner's), U-04 on the board as drawn on TI's D1 or D3 (none once (B1) is applied); the rest, the panel unit included, resolves by a value, a part or a measurement on the same topology |
| 2. Material power-path defects have engineering resolutions and bounded supporting calculations | rows IF-01, IF-02, IF-04, IF-05, IF-13; defects D-01 to D-12 below: D-10 and D-11 (a stiff 36 V source on the solar port, a reversed panel; single faults from L4-E7's panel-lead derivation, set 27) ADDRESSED IN DRAFTS by L4-E7's selected remedies (check 5; the guard R-173, not applied; D-11 CONDITIONAL on Q13's hot leakage), the band between 25 V and the cut-off a residual for layer 8 (R-175); D-12 resolved in the drafted entry with the guard; D-06 resolved in design by L4-E11, D-07 and D-09 superseded by the replacement of the LM5069, the rest drafted or bounded with their conditions named; E11-19 in out 12a; the dependency rounds add none (out 14); the panel lead's verdicts in 7a (out 23) | CONDITIONAL | no material defect is open: the known defects at the solar entry, D-10 (a stiff 36 V source on the port) and D-11 (a reversed panel), single faults, are addressed in drafts, a selected remedy each (L4-E7, check 5 at 573fd5b8: the over-voltage cut-off U21 with Q12 and the return switch Q13, R-173, drafted, not applied), D-11 CONDITIONAL on Q13's leakage above +25 C; the band between 25 V and the cut-off, where a stiff source still runs the stage, is a residual for layer 8 (R-175); D-12 (CS116 and CS115 on the drawn entry) is resolved in the drafted entry, CS115 CONDITIONAL on the cable's loop current (L4-E7's derivation, set 27); D-01 to D-05 and D-08 are resolved in design (drafted or bounded), D-06 is resolved in design by L4-E11's interconnect with its evidence items (E11-10 to E11-16), D-07 and D-09 are superseded by the replacement of the LM5069 (E11-19 finds no new one); the resolutions rest on CONDITIONAL rows (the loop's typical rows, the makers' installed and short-time ratings, R227's pulse rating, the start into a hard short's transconductance bound) and the hot short in service on open evidence (the loop's inductance, E11-20); the dependency rounds add no defect: L4-E11's D9 and D10 are the entry's delay and transconductance rows already CONDITIONAL here, and E11-24 is U-04's fallback, a register row (R-152), not a defect's resolution | no: each resolves by a part, a rating or a measurement at the vehicle or the solar entry; D-10 and D-11 by the drafted guard, which adds protection at the solar entry and changes no topology |
| 3. Remaining assumptions are explicit, with their impact and verification method | section 10's register A-01 to A-30 | PASS |  |  |
| 4. Downstream implementation changes, layout constraints and tests have named owners and acceptance criteria | `DOWNSTREAM-REGISTER.md`: 166 items, each with one owner and an acceptance, among them L4-E11's E11-01 to E11-32 (deduplicated), L4-E10's and L4-E12's items, PANEL-ACC (R-35, R-52, R-148, R-149), L10's own assignment (R-120, R-121), M2 (R-122), the dependency rounds' rows (R-150 to R-154), the findings ledger's (R-155, R-156; R-102 and R-139 extended) and the consolidation's results (R-157 to R-172, the combined route's R-170 to R-172 only under T-H1's reading); the release order (L4-E6's R12 before L4-E8's ballasts; L4-E11's entry draft after this record's hot-swap draft); `LAYER5-HANDOVER.md` LH-01 to LH-11 | PASS |  |  |
| 5. No unresolved uncertainty could overturn the selected architecture while described merely as routine later testing | rows IF-09, IF-10, IF-11; choices U-01, U-02 and U-04 below, each with its exact question, its evidence by vendor, physical and owner, who supplies it, its fallback with its numbers and what it could overturn (update round 5, out 14); U-03 a downstream unit selection since L4-E13 | CONDITIONAL | three unresolved choices could overturn it and are named as such, not as later testing, each with its question, evidence, supplier and fallback stated by its dependency round: U-01 (FEA-008's cell: the signed specification and the owner's two items; L4-E10, check 4 at e464ff88), U-02 (MESHSAT-1478: T-H1 decides, in the procedure's order K1, K5, K10, K6, K7 and K8; at +40 C the heat stage against K1, 1.958 W/K with option C, or K3, 0.941 W/K with options A and B, the owner's CFL-002 deciding which (L4-E12, check 7 at 6f8fd652); E5's line read at 2.455 W/K), U-04 ((B1) selected and drafted, a downstream qualification test once applied; on the board as drawn TI's D1 and D3; L4-E11, check 5 at 5aa18a69); an owner and an acceptance criterion do not close them. U-03 left this category with L4-E13's acceptance: a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC, R-35) that decides which unit, not the topology or the source class | yes, on named evidence only: U-01 (D-06's pack energy and settings), U-02 (under the line CFL-002 sets with the route also short: CFL-002's other options, the sealed case's thermal design or the device set, the owner's), U-04 (on the board as drawn only, TI's D1 or D3: the charger's power path); U-03 no longer can, unless route 2 proves infeasible with route 1 still closed (L4E13-06) |

**Layer 4's power architecture closes: NO** (criteria 1, 2 and 5). Two categories, kept apart below: the material defects (8a,
none open since the update round) and the unresolved choices that could overturn the architecture (8b, three since update round
3: U-01, U-02, U-04; U-03 moved downstream as PANEL-ACC); the downstream tasks (8c) and the owner's items (8d) are neither.
**The reason it stays not closed, on this record's own reading:** criteria 1 and 5 cannot read PASS while U-01, U-02 and U-04
stand, and each can still overturn part of the architecture on named evidence (8b); criterion 2 has no open defect but its
resolutions rest on CONDITIONAL rows with named evidence, so it reads CONDITIONAL, not PASS; nothing L4-E13 settled changes
either reading, since U-03 was never what held criterion 2 and its move leaves three architecture-level choices in place.
**Update round 5 leaves the reading as it was:** the dependency rounds state each choice's question, evidence, supplier and
fallback, and none is yet answered by a held document or a measurement (U-01 waits on the signed specification, U-02 on T-H1,
U-04 on TI's D1 and D3); they add no material defect (out 14).

### 8a. The material power-path defects (criterion 2)

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
| D-10 | a stiff 36 V source on the solar port (a single fault: a vehicle or shore lead in the panel's receptacle) | without the guard D4, the drafted SMCJ28A, conducts 2.67 to 16.63 A and takes 95.9 to 585.8 W against its 1.17 W on the board at the hot end's air; the largest sustained source the drafted entry holds is 29.70 V (L4-E7's D4) | L4-E7's three, each on its held sheet: the TPS48110-Q1 alone on back-to-back FETs (its -1 V input pins on a reversal: not taken); the LM74700-Q1 ahead of the TPS48110-Q1 (76.21 V across CATHODE to ANODE under CS116 against 75 V: not taken); SELECTED, U21 TPS48110-Q1 with Q12 CSD19532Q5B as an over-voltage cut-off, rising at 28.55 to 31.06 V and falling at 27.07 V or more, with D4 the SMCJ30A: the block never turns on and Q12 holds 36 of 100 V (the TVS-only change, SMCJ36A with the 63 V class, evaluated and not taken) | ADDRESSED IN DRAFTS (a selected remedy, drafted, not applied): R-173: apply_gen_sch_e_solar_guard.py (7 edits, release-guarded), drafted, not applied (L4-E7, check 5 at 573fd5b8); owed: the SMCJ30A's LCSC code, U21's DGX-19 land, the regeneration, the bench rows (R-176); the band 25 V to the cut-off a layer 8 row (R-175) |
| D-11 | a reversed panel (DECISION-31's E-N1, a single fault) | without the guard D4 carries the panel's 6.802 A forward, held, and holds inside its 1.17 W on the board only below a 0.172 V drop, which no silicon junction has at that current (INFERRED); the keyed receptacle was the only barrier (L4-E7's D5) | SELECTED, Q13 CSD19532Q5B in the panel's return (J_SOLAR.2 becomes PV_RTN), its gate from R101 and R102 with a D12 BZT52C12 clamp: it blocks a reversal with its 100 V rating and no controller; the high side's pins stay within 1 V of GND while Q13 leaks under 31.5 uA, its sheet printing 1 uA at 25 C only (DECISION-31's E-N1 closed by it) | ADDRESSED IN DRAFTS (a selected remedy, drafted, not applied), CONDITIONAL on Q13's leakage above +25 C: R-173 with D-10 (the same draft, not applied); Q13's hot leakage a bench row (R-176) |
| D-12 | the panel lead's CS116 and CS115 (MIL-STD-461G under REQ-063) on the drawn entry | D4 clamps at 39.00 V at CS116's 10 A and 37.34 V at CS115's 5 A (hot end), over the drawn C11 and C12's 35 V (L4-E7's D1, D2) | the drafted entry's 50 V parts (L4-E7R) with the solar guard and D4 the SMCJ30A (R-173): D4 at 41.91 V (CS116) and 40.04 V (CS115) at the hot end, under 50 V; CS116 and CS115 MEET with the block on and off, a pulse over the cut-off turning it off within 4 us | RESOLVED (drafted): R-21 (apply_gen_sch_e_backstop.py) and R-173 (apply_gen_sch_e_solar_guard.py); R-174 records the loop current; R-156 judges under TRN-001 |

**E11-19 adds no material defect** (out 12a, decision 13). What it leaves open is evidence, not a defect: the loop's inductance
for a hard short in service (E11-20, R-134), the transconductance bound of a start into a hard short (A11-10, E11-17), and the
input current's transients against the breaker's 0.247 ms (E11-06, E11-21).

**L4-E7's panel-lead derivation adds D-10 to D-12** (set 27 at `6d76453e`, out 23, 7a). D-10 (a stiff 36 V source on the solar
port) and D-11 (a reversed panel, DECISION-31's E-N1) are single faults, **addressed in drafts** since L4-E7's remedies (check 5 at
`573fd5b8`): the over-voltage cut-off U21 with Q12 (rising 28.55 to 31.06 V, falling 27.07 V or more) and the return switch Q13,
drafted in `apply_gen_sch_e_solar_guard.py` (R-173), not applied; D-11 is CONDITIONAL on Q13's leakage above +25 C. D-12 (CS116
and CS115 on the drawn entry's 35 V bulk) is resolved in the drafted entry with the guard and D4 the SMCJ30A (R-21, R-173). The
band between 25 V and the cut-off, where a stiff source still runs the stage, is named for layer 8 (R-175). The guard adds
protection and changes no topology.

### 8b. The unresolved choices that could overturn the architecture (no owner closes them), and U-03 moved downstream

| Choice | Class | What | The exact unresolved question | The present state (the exact constraint) | The evidence: (vendor) / (physical) / (owner) | Who supplies it | The fallback, with its numbers | What it could overturn |
|---|---|---|---|---|---|---|---|---|
| U-01 | ARCHITECTURE-LEVEL CHOICE | FEA-008: the battery path's cell and thermal design (L4-E10; a supported route on published evidence, the Saft MP 176065 xtd, a PROPOSAL) | which cell does D-06's pocket carry? The ruled 35E is UNSUITABLE on its own published evidence for LO-01d (E3-O: the cells at 61.26 to 72.42 C over its +60 C), LO-01e (E5's dwell: the idle pack at 74.73 C), LO-01f (+71 C storage) and LO-01g (-33 C storage); the Saft MP 176065 xtd as 4S1P covers every cell-limit row on its published datasheet, subject to the owner's approval and three facts (the axial fit, 18 A for 60 s, T-H1); the HL18650V needs its signed specification to confirm the rows L4-E10 holds only on its product page (MAKER-PAGE): the idle hot limit (+80 C, the 30-day storage row), storage at -33 C, each storage row's state of charge and recovery, charge below 0 C, the charge current from +10 C (at least 0.357C), continuous discharge (at least 6.0 A a cell for PS-ALLTX), the end voltages and the minimum capacity | LO-01d to LO-01g (E3-O, E5, E3-S, E4-S with the pack fitted) have no route that holds on held evidence with the ruled cell; LO-01a holds only with T-H1 at least 1.666 W/K in both lid states (1.8058 W/K with L4-E8's ballasts counted, L4-E12). L4-E10's dependency round (check 4 at e464ff88) states the HL18650V's limits by mode and drafts the charge for the 4S3P, never applied: 0.84 A to 16.40 V from T1 -9 C, 1.68 A to 16.80 V from T2 1 C, the drawn 3.00 A to 16.80 V from T5 11 C to T3 42 C, UTC -9.0 C, the kit's hold below -7 C; usable energy 90.2 Wh (2.11 h) against the 35E's 107.9 Wh (2.52 h) at +25 C, 16.4 % less; at the cold end only brackets (45.1 to 69.6 Wh with the cells at -5.52 C, 37.2 to 54.1 Wh from a cold start at -20 C, ASSUMPTION). L4-E10's consolidation (check 5 at 1c321773): a supported route on published manufacturer evidence, the Saft MP 176065 xtd (3.65 V, 5.6 Ah; charge -30 to +85 C, discharge -40 to +85 C at 11 A continuous and 22 A pulses with no duration, storage allowable -40 to +85 C) as 4S1P: 81.6 Wh nominal, 53.5 to 55.1 Wh usable, 1.25 to 1.29 h battery-only, about NZ$ 954.88 for four cells; CONDITIONAL on the axial fit (at most 1.40 mm of wrap), 18 A for 60 s and T-H1 (LO-01a's complete pass and LO-01e); approach (III)'s E5 route REJECTED (the pocket's room as designed 0.0865 L) | (vendor) Saft's published datasheet (Doc. 31109-2-0625, held) for every cell-limit row of the MP 176065 xtd, and its statement on 18 A for 60 s (the drafted request); Yichun Topwell Power's signed product specification answering the drafted request's ten questions for the HL18650V; Eaton's statement on F2 above +60 C and in storage (R-103); (physical) a printed mock-up of four Saft cells at the sheet's maximum dimensions in the pocket at the built stack (hours, no purchase; R-167); one Saft cell pulsed at 18 A for 60 s at +25 C and at the cold end (NZ$ 238.72 and a 20 A load, a day; R-168); the lot's minimum capacity at receipt (R-169); T-H1 in both lid states (R-104, R-151); for the HL18650V a lot soak (about ten cells, USD 35.00, 4 and 12 days); with the cell chosen, L4-E10's margins re-run (1.06 K under H1 and 0.97 K under U2's INFERRED trip at LO-01e) and each LO row's TEST-PLAN run with the pack fitted (R-47, R-109); (owner) approve D-06's cell, energy and spend: the Saft as 4S1P (about 145 to about 82 Wh nominal, NZ$ 954.88; OW-3), or the HL18650V once its specification or a soak confirms; send the requests (OW-2, OW-9); if declined, LO-01d to g stay a release gate | Saft and Yichun Topwell Power, through the owner; Layer 7 (the mock-up); the prototype bench (the pulse test, T-H1, the LO rows); Layer 6 files the answers (R-103, R-168); the session re-runs L4-E10's margins (R-47); the owner approves the cell | the HL18650V, the higher-energy alternative (90.2 Wh usable), on its signed specification or a lot soak; with no answer and no approval, U-01 stays a release gate and every row CONDITIONAL (no ruling needed). With a narrower signed HL18650V figure, at L4-E10's thresholds: an idle limit under 78.94 C makes H1 act in E5's dwell, under 74.73 C E5's cells pass it, under 73.07 C E3-O loses its 'no shutdown', under 71.00 C E3-S fails, under 68.86 C E3-O's cells pass it; E3-O and E5 then fall back to (I)'s cooler (8.18 to 35.21 W into the sealed case, INCONCLUSIVE) and E3-S to requirement change A (the owner's); storage warmer than -33 C to (III)'s primary-fed heater (470 to 940 Wh of added storage, an owner's ruling under D-06) or requirement change A; continuous discharge under 6.0 A a cell back to (I); the charge current, the end voltage and the capacity (3.22 Wh per 100 mAh a cell) move energy, not the architecture; or the 35E kept with (I), or a requirement change (the owner's, D-29) | D-06's pack energy, not the power path's topology: with the Saft 53.5 to 55.1 Wh usable against the 35E's 107.9 Wh, with the HL18650V 16.4 % less (90.2 against 107.9 Wh at +25 C), each with its protection settings and charge ranges; with a narrower idle limit and no requirement change, (I)'s powered cooling (up to 35.21 W into the sealed case) would reopen U-02's heat budget, and a narrower storage floor would add 470 to 940 Wh of primary storage under D-06 |
| U-02 | ARCHITECTURE-LEVEL CHOICE | MESHSAT-1478: the electronics against the inside air at D-02a's +55 C margin and E5's +60 C dwell (L4-E12) | what does the sealed Peli 1450 with its 3 mm plate conduct lid open with the fans, against the binding 2.159 W/K: E5 under the hold puts 21.587 W into the case (19.497 W and L4-E8's 2.09 W of ballasts) across the 10 K from E5's +60 C dwell to the +70 C class, at 0 K of margin? L4-E12's conservative bound, with the fans' airflow, the boards' radiation and the floor's support credited at zero, gives 0.566 W/K at E5 and 0.607 W/K at E3-O, and no inside film passes the outside films' cap of 1.540 to 1.571 W/K, so T-H1 DECIDES what those three credits add (the fans' power and range also open, D-18); and, since L4-E12's check 7, at REQ-024's +40 C the heat stage's 27.086 W against the line the owner's CFL-002 sets: K1, the SGP41's +55 C, 1.806 W/K (option C), or K3, the +70 C class, 0.903 W/K (options A and B); the profile's own line is K6 at REQ-014's +20 C, 1.447 W/K | L4-E12's route (c), E3-O as stated and the hold in E5 only, is CONDITIONAL on T-H1 lid open with the fans at or over 2.159 W/K (E3-O alone 1.806 W/K; 2.709 W/K with no hold), the hold's reference within +-0.899099 K of the mixed air, the parts out of the cooler's exhaust, the fans' rating (D-18), the pushbuttons and two regulators changed and PDi's statement; at the line E3-O's air is 67.55 C and E5's 70.00 C, while the design as it stands (LO-01a's floor, no hold) reaches 76.25 C in E5; L4-E12's dependency round (check 4 at c933724e) counts the fans in the energy budget (pwr_budget.py's rows, tier R), and their picked power moves the line 0.100 W/K per W (2.071 to 2.333 W/K over the representatives); L4-E12's consolidation (check 5 at 7f41632d): on the conservative bound, with every session measure, E5 holds (0.671 against 0.621 W/K) and E3-O falls 0.212 W/K short (0.691 against 0.903 W/K, the module's intake at 92.61 C against its +85 C); inside the envelope no location holds the SGP41 to its maker's conditions (CFL-002); L4-E12's heat-rejection comparison (check 6 at 589f18ac): at the profile's heat fins on the face's free 0.0552 m2 give 0.821 to 0.854 W/K, the large loads (23.641 W) led into the plate 1.096 W/K (1.339 W/K with the fins), the open lid as a second radiator 0.801 W/K, all three 1.384 W/K: 1.252 W (0.063 W/K) short of K6's 1.447 W/K; its reconciliation (check 7 at 6f8fd652): K1 lies at or over the outside films' cap at the conservative ends (1.504 W/K; 1.859 W/K at the other ends), and charging with the profile running needs 1.627 to 1.977 W/K with the charge path counted | (vendor) D-18's picked fans: the maker's power at the duty the controls set and an operating range covering -20 C to the inside air (REQ-043; no held sheet gives a fan's operating temperature; R-142, R-150); PDi's and Sensirion's answers; (physical) T-H1's points in the procedure's order (R-104; T-H1-PROCEDURE-DRAFT.md as revised for L4-E12's check 7, R-151), each at its mode's heat with the heaters set to it less the fans' measured draw: K1, the heat stage lid open (the heaters 25.136 W plus the fans), a reading of at least 1.958 W/K closing K1, K3, K4 and K9 (0.941 W/K for K3 alone); K5 lid closed; K10 at E5's 21.587 W, at least 2.455 W/K; K6 at the profile's heat, at least 1.508 W/K; K7 and K8, at least 1.698 and 2.081 W/K; under a point's line the combined route (R-170 to R-172) read at the same point; section 9f's lower lines stay conservative at 21.2 W (a reading of at least 2.462 W/K keeps the design as stated, 1.516 W/K section 8's fallback, 0.951 W/K E3-O with every session measure; (5.9 to 21.1 h) a point there); the earlier single line, a reading of at least 2.416 W/K at a 10 K rise (2.285 W/K at 20 K) (k = 2, 10.7 % at a 10 K rise), is replaced by K10's, and the eight-point matrix at 21.2 and 42.4 W (29 to 84 h in all) by these points; the forced hold and the SGP41's shutdown at room temperature, its lag measured (R-138, R-139); then E3-O and E5 with thermocouples on the +70 C parts (R-109); (owner) authorise T-H1's bench (its purchase; a chamber run at +60 C only if wanted, his spend; OW-8); CFL-002 (OW-1); send PDi's and Sensirion's requests (OW-4); CFL-002 also sets the line at +40 C (K1 with option C, K3 with A or B) | the prototype bench, as Layer 9's physical verification, once the owner authorises it (the session cannot run it); Layer 6 components for D-18's pick (R-142, R-150); Layer 7 mechanical for the combined route (R-170 to R-172) if a point reads short; the makers, through the owner | under a point's line, the combined route inside the rulings (R-170 to R-172, passive: no power, no endurance change; 1.384 W/K on the bound at the profile's heat) read at the same point; with option C still short, CFL-002's option A or B removes K1 and K2 (the owner's). For E5 and E3-O the session's, inside the rulings (no vent, the Peli 1450 kept): F4, the RockBLOCK, board D and the LimeSDR on pads to the plate, holds E5 down to 1.564 W/K and E3-O down to 1.399 W/K (1.309 W/K with the +80 C connectors out of the exhaust); F3, a deeper hold in E5 that keeps the logging (13.429 W into the case), holds E5 to 1.552 W/K; F4 with F3 holds E5 down to 1.125 W/K, with no owner ruling and no change to E3-O; F1, fins on the plate, multiplies a reading by 1.125 to 1.131 (outside, twice the area) or 1.252 to 1.363 (both faces); the H5007NL, the ATP16 and the PXP4043/C take wider parts or makers' statements (R-141); with every session measure (F4, F3 in E5, board B's +80 C connectors to +85 C parts, the HX magnetics, the wider buttons; R-111, R-141, R-163 to R-166) the module's +85 C intake binds: E3-O needs 0.903 W/K, a reading of 0.951 W/K. Under a reading of 0.951 W/K the remaining option is the owner's: a deviation of E3-O's configuration (the hold in E3-O) or a device-set re-pick (CHO-001) | at K1's point: at or over the line CFL-002 sets (1.958 W/K with option C, 0.941 W/K with A or B) the architecture stands; under it, with the route reading at or over it, it stands with the route; still under, the owner's (CFL-002, the case or the device set), never the power path's topology; at E5's fallback lines: at or over a reading of 0.951 W/K the session's measures hold both margins and the architecture stays; under it the sealed case's thermal design (no vent, the ruling of 7 September 2026) or the device set (CHO-001) could change, the owner's; a stopped fan puts E5's mixed air at 72.38 to 85.36 C on W4's still values, the parts coupled to the plate at most 69.82 C; CFL-002 changes a sensor, not the architecture; never the power path's topology |
| U-03 | CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC) | O-1: the solar panel inside REQ-016's window (L4-E13, accepted) | which physical unit is inside REQ-016's window: a unit measured to PANEL-ACC and accepted on A-1 (Vm20 plus U_V at most 25.000 V at -20 C and 1000 W/m2), A-2 (at least 1.365591 W) and A-3(b); not whether the window can be met, which L4-E13 shows on a unit equal to the typical rows | L4-E13 (accepted, checks 3 and 4 at fae419d1 and 33b6b7be): route 1, a maker's warranted band, closes nothing today; route 2, one identified SunPower SPR-E-Flex-100 measured against A-1 to A-3, is feasible on a unit equal to the typical rows: A-1 Vm20 + U_V 24.1505 V against 25.000 V at -20 C and 1000 W/m2 (margin 0.8495 V), the window Voc25 20.315 to 22.156 V; A-2 27.0849 W above 1.365591 W; A-3 (a) 3.987 A, the conservative bound over L4-E7R's regulation (2.5485 A nominal, at most 2.9337 A at 25 V) and backstop (trip at most 3.7408 A), (b) 8.1817 A, (c) 13.82 A, a COMPONENT_LIMITATION on J_SOLAR and PV_IN; A-4 on L4-E7R's two layers (the regulation's 25 V corner 73.3436 W; the backstop's static bound 93.5521 W, CONDITIONAL on G_CM and the VIN+ bias); no physical unit accepted | (vendor) route 1, a maker's warranted Voc band inside the window (the drafts to SunPower and Solbian, OW-4); it closes nothing today; (physical) one unit bought, recorded by serial number and measured (M1 to M3 and A-2's reading at the specification) and accepted on A-1, A-2 and A-3(b) (R-35); its trace rerun (R-52); J_SOLAR and PV_IN with a rating that covers A-3(c) (R-148); M3's n at or under 2 for the disturbance check (R-149); L4-E7R's regulation and backstop applied (drafted) for A-3(a) and A-4; (owner) the purchase and the measurement of one unit (OW-6) and sending the two route-1 drafts (OW-4): actions, not questions | the owner (the purchase, the two drafts sent); the measurement to the specification under his authority; Layer 6 components (PANEL-ACC's acceptance R-35, J_SOLAR and PV_IN R-148, M3's n R-149); the makers, if they answer | another unit of the same curve shape inside the window; route 1 if a maker warrants a band; REQ-016's window restated (the owner's; not needed) | nothing of the architecture: it decides which unit, not the topology and not the source class; REQ-016's window, the stage, its hold and its 100 W control stay; it returns to an architecture-level choice only if route 2 proves infeasible with route 1 still closed (L4E13-06) |
| U-04 | ARCHITECTURE-LEVEL CHOICE | source-only and dead-pack operation (L4-E11: (B1) selected, the BQ25730 with Q39, drafted; the drawn board is arrangement (A)) | with (B1) selected and drafted, does the BQ25730's VSYS hold the kit's load steps with no battery current inside the 2.054 V margin (D2), can Q39's installed path carry OCD1's 20 A (a thermal bar of at most 20.54 C/W) and the docking pulse (242.9 A for 17.7 us through its body diode), and is the BQ25730 obtainable? On the board as drawn (arrangement (A)) D1 and D3 stay TI's | L4-E11's consolidation (check 5 at 5aa18a69) selects (B1), TI's BQ25730 with the battery FET Q39 (AONS21357), drafted in apply_gen_sch_a_charger.py and not applied: its sheet (SLUSE65A) bounds VSYS in all three modes, at least 12.054 V with no battery (LDO mode), VSRN + 150 mV within +-2 % with the charge inhibited, VSYS_MIN the floor with the pack present, removing D1, D3 and D4; 98 of the 107 row blocks are identical, so L4-E4 to L4-E8 carry over; Q39 takes 0.0945 W at PS-IDLE-SPEC (0.221 % of the pack's output); still open: D2 against the 2.054 V margin, D6, D8, D9, D10, Q39's thermal bar and docking pulse, the BQ25730's supply, and REQ-015 at 9.00 V at the plug, a CONDITIONAL CANDIDATE (P1 at most 20.51 W, the shed warm-up 28.12 W carried with 0.98 W in hand; at the load's hi corner P1 (35.24 W) exceeds the source's least); on the board as drawn the BQ25731 leaves D1 and D3 (Q-TI-3) to TI | (vendor) TI's SLUSE65A (held) bounds the three modes; Q-TI-15 (D2) and Q-TI-16 (VSYS_MIN's maximum) to TI and Q-AOS-1 (the body diode's pulse) to AOS, drafted in clarification/TI-QUESTIONS.md; the BQ25730's supply from an authorised source (R-162); (physical) the three modes and D2 on one BQ25730 build (R-161), every step's minimum over the converters' 10.0 V floor; Q39's installed RthJA at most 20.54 C/W (R-159); the docking pulse (R-160); R-85 extended at the plug (E11-06) and E4-O's warm-up (E11-23, R-137); (owner) send TI's and AOS's questions (OW-7); the BQ25730 bought for the build (money, the owner's) | Layer 8 board A applies R-157 under L4-E11's release record (R-147); the prototype bench (R-161); Layer 9 (R-159); Layer 6 (R-160, R-162); TI and AOS through the owner | inside (B1): R-c's step rule for D2; the gauge's OCD1 set to what the installed path carries, or the bridge shedding on IDCHG, for the thermal bar; a slower discharge-FET turn-on on board P for the docking pulse; if (B1) fails on these or on supply, arrangement (A) with its dependency round stands: E11-24's hold-up (54.07 mJ, 1.117 ms for the worst admitted step, R-152) for D2 and D5, with TI's D1 and D3 deciding | once R-157 is applied, nothing of the architecture: each open claim has a test or an analysis that bounds it and a fallback inside (B1), so U-04 becomes a downstream qualification test (L4-E11 check 5); on the board as drawn a negative D1 or D3 from TI changes the charger's power path, which (B1) already is; the efficiency, the pin's band or P1's load move the knee or F1, not the topology |

**Whether each can still overturn the architecture, and on exactly what:** U-01 on D-06's pack energy, not the topology: the
Saft route (a supported route on published evidence) halves the usable energy, and the HL18650V rests on its signed
specification (D-06's pack energy, its protection settings and charge ranges; a narrower idle limit or storage floor with no
requirement change would bring (I)'s powered cooling, up to 35.21 W into the sealed case, or (III)'s 470 to 940 Wh of primary
storage); U-02 yes, on T-H1's deciding point (L4-E12's consolidation): L4-E12's conservative bound (0.566 W/K at E5, 0.607 W/K
at E3-O, the fans' flow at zero) lies under the lines, and with every session measure E3-O falls 0.212 W/K short; at or over a
reading of 0.951 W/K the session's measures hold both margins, and under it a deviation of E3-O's configuration or a
device-set re-pick is the owner's, while CFL-002 changes a sensor and not the architecture; U-04 only on the board as drawn, on
TI's D1 or D3 (the charger's power path): (B1), the BQ25730 with Q39, is selected and drafted, and once applied its open claims
(D2, Q39's thermal bar and docking pulse, D6, D8, D9, D10, the supply) each have a test and a fallback inside (B1), while the
efficiency, the pin's band or P1's load move the knee or F1 and not the topology. **U-03 no longer can** (update round 3): L4-E13 makes it a CONDITIONAL DOWNSTREAM
UNIT SELECTION (PANEL-ACC) that decides which unit, not the topology and not the source class; REQ-016's window, the stage, its
hold and its 100 W control stay; it would return to this category only if route 2 proved infeasible with route 1 still closed
(L4E13-06). Its row stays in the table, with its class, so the move is visible; criteria 1 and 5 no longer name it.

### 8c. The downstream implementation and verification tasks (criterion 4)

`DOWNSTREAM-REGISTER.md` (section 9): an owner and an acceptance criterion close the ASSIGNMENT, not the item. The items that
exist only under a choice's outcome are marked there (Order "U-01"), and the items that carry a choice's evidence say so
("U-02"); none stands in for a choice.

**What closure needs, exactly:** U-04 settled by applying (B1) (R-157 with its firmware R-158), then the three modes and D2 on
the bench (R-161), Q39's installed path (R-159), the docking pulse (R-160) and the BQ25730's supply (R-162), with E11-06 (R-85
extended), E11-09 (the knee drawn) and E11-23 (the warm-up time); on the board as drawn, TI's D1 and D3 (R-114, E11-05, E11-25);
U-02 settled by T-H1's deciding point (R-104) at or over a reading of 0.951 W/K with the session's measures (R-111, R-141,
R-163 to R-166), then the full T-H1 (R-151) with the picked fans (R-142, R-150), the forced hold and the SGP41's shutdown with
its lag (R-138, R-139), the parts' readings in E3-O and E5 (R-109) and the owner's answer to CFL-002, and under 0.951 W/K the
owner's decision;
U-01 settled by the owner's adoption of the Saft route (OW-3) with its three checks (the mock-up R-167, the 18 A pulse R-168,
the lot's capacity R-169) and T-H1, or by the HL18650V's signed specification (R-103, R-47), or held open as a release gate; the
HL18650V's charge drafts applied only under (II) (R-154); D-06's CONDITIONAL parts by the makers' ratings and F1's clearing I2t (R-113, R-115, R-129 to R-132) and the
four-wire loop (R-130); the hot short in service by the loop's inductance (R-134); and for criterion 1 the CONDITIONAL inputs
with their named evidence (G_CM and U18's VIN+ bias R-101, PWR-F12 R-46 and R-83, C-7, C-3, C-5, V-A07). The coordinator decides
whether a CONDITIONAL criterion with these named is acceptable for Layer 4's closure; this record does not.

### 8d. The owner's items (decisions and outside contacts only; the session contacts no outside party)

Kept apart from the engineering work above: each is a decision only the owner takes, a text only the owner sends or an
action under his authority (a purchase, a bench's authorisation): actions, not questions. The script reads each document at its
pinned sha256 (out 9 (c)). Update round 5 adds OW-7 (the TI request: REVIEW-REQUEST.md with TI-QUESTIONS.md) and OW-8 (T-H1's
bench authorisation), and OW-2's request carries ten questions.

| Item | The decision or action | The document (path, where, sha256/16) |
|---|---|---|
| OW-1 | CFL-002 (U-02): the SGP41 in the battery bay against REQ-042's VOC channel inside the envelope: A, a BME688-class sensor in its place (L4-E12's recommendation); B, the VOC channel dropped; C, the SGP41 kept, its channel reported as not covered above a 49.0 C reading and after storage outside 5 to 30 C; it also sets the thermal line the sealed case must meet at +40 C: K1, 1.806 W/K, with C; K3, 0.903 W/K, with A or B (L4-E12's check 7) | L4-E12's page, section 8: `v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md`, at `6f8fd652`, 9117ee17ca8c98d0 |
| OW-2 | U-01, item 1: send the drafted request for the HL18650V's signed product specification (Yichun Topwell Power), ten questions since L4-E10's dependency round (7 to 10 added: the cold charge band and termination, the pulse current, the cold capacity, the end-of-life capacity and self-discharge) | Yichun Topwell Power: the HL18650V's signed specification, ten questions (U-01): `v2/docs/records/l4e10/clarification/topwell-hl18650v.txt`, at `e464ff88`, 1ca762d83bbb58b2 |
| OW-3 | U-01, item 2: approve D-06's cell, energy and spend: the Saft MP 176065 xtd as 4S1P (the supported route on published evidence: about 145 Wh to about 82 Wh nominal, 53.5 to 55.1 Wh usable, NZ$ 954.88 for four cells; CONDITIONAL on the fit, 18 A for 60 s and T-H1), or the HL18650V in the 4S3P (about 121 Wh nominal, about USD 42 a pack) once its specification or a soak confirms L4-E10's rows; REQ-046 and REQ-077 restated with the cell; if declined, LO-01d to g stay a release gate | L4-E10's page, sections 8 and 15: `v2/docs/records/l4e10/L4E10-CELL-THERMAL.md`, at `e2d20bf2`, 98efcee0bcac0d72 |
| OW-4 | the other outside-contact drafts to send (the owner chooses the channel; Topwell's is OW-2, TI's OW-7) | Pervasive Displays: the E2370KS0C1's storage and operation (U-02): `v2/docs/records/l4e12/clarification/pervasive-displays-e2370ks0c1.txt`, at `a86be47b`, 4f7db1348cc0b4ac; Sensirion: the SGP41's duration, recovery and storage (U-02, CFL-002): `v2/docs/records/l4e12/clarification/sensirion-sgp41.txt`, at `a86be47b`, 43c47549235fe6e8; Analog Devices: the LT8705A's IMON_IN limits (the 100 W bound; R-33, R-101): `v2/docs/records/l4e7/clarification/analog-devices-lt8705a.txt`, at `675b8068`, 97d8217092eae7ac; Milliohm: the HoJLR2512's temperature coefficient below +25 C (R-101): `v2/docs/records/l4e7/clarification/milliohm-hojlr2512.txt`, at `675b8068`, e920420419a677e0; Vishay: the WSL2512's pulse capability (R-101): `v2/docs/records/l4e7/clarification/vishay-wsl2512.txt`, at `675b8068`, 5d96017a5051257b; Texas Instruments: the INA169's error envelope (R-101): `v2/docs/records/l4e7/clarification/texas-instruments-ina169.txt`, at `675b8068`, 405fb3988f41d8ac; Eaton: the SCF9550 above +60 C and in storage (PWR-F12; R-103): `v2/docs/records/l4e10/clarification/eaton-scf9550.txt`, at `79b2f568`, 9dffb95e8b4874fc; SunPower (the module's maker): a warranted Voc band at STC for the SPR-E-Flex-100 (U-03's route 1): `v2/docs/records/l4e13/clarification/sunpower-spr-e-flex-100.txt`, in the tree, 453a5a957648a322; Solbian: a warranted Voc band for the SX 156 (U-03's route 1): `v2/docs/records/l4e13/clarification/solbian-sx-156.txt`, in the tree, fb66bfb76e7e252c |
| OW-5 | the fallbacks, to send only if T-H1 reads under 2.159 W/K (L4-E12) | Ground Control: the RockBLOCK 9704: `v2/docs/records/l4e12/clarification/ground-control-rockblock-9704.txt`, at `a86be47b`, 738245875bec70c5; NiceRF: the SA868: `v2/docs/records/l4e12/clarification/nicerf-sa868.txt`, at `a86be47b`, 92324668c17d4f6c; Bulgin: the PXP4043C: `v2/docs/records/l4e12/clarification/bulgin-pxp4043c.txt`, at `a86be47b`, c7accd3dd6dc1d89 |
| OW-6 | PANEL-ACC (U-03, L4-E13): buy one SunPower SPR-E-Flex-100, recorded by serial number, and have it measured to the specification (M1 to M3 and A-2's reading); actions under the owner's authority (money), not questions | L4-E13's page, PANEL-ACC: `v2/docs/records/l4e13/L4E13-PANEL.md`, in the tree, 1c7f11716db4c2f2 |
| OW-7 | U-04: send TI the battery packet's questions (REVIEW-REQUEST.md section 4) with L4-E11's TI-QUESTIONS.md: under (B1) Q-TI-15 (D2) and Q-TI-16 (VSYS_MIN's maximum) to TI and Q-AOS-1 (Q39's body-diode pulse) to AOS; on the board as drawn Q-TI-11 to Q-TI-14 and the addendum to Q-TI-3 (D1 and D3 decide U-04 there; E11-05, E11-25; R-114, R-160); an action, not a question | Texas Instruments: the battery packet: `v2/docs/review-packets/battery/REVIEW-REQUEST.md`, in the tree, 91a257430cbeb53a; Texas Instruments and AOS: the dependency rounds' questions: `v2/docs/records/l4e11/clarification/TI-QUESTIONS.md`, in the tree, 54e66d8c2d4ce3eb |
| OW-8 | U-02 (T-H1 decides): authorise T-H1 on the bench, its points in the procedure's order (K1 first: the heat stage lid open, one heater at 25.136 W plus the fans, one logger; then K5, K10, K6, K7 and K8), the combined route's kit (R-170 to R-172) only if a point reads under its line; its purchase (a current-moulding Peli 1450 with the 1450PF frame, a 3 mm plate blank, the heaters, the fans as stand-ins until D-18, a second PicoLog TC-08) and who runs it; a chamber run at +60 C only if wanted, at a laboratory, his spend; the procedure is drafted and the session cannot run it (R-104, R-151); an action, not a question | T-H1's procedure, drafted: `v2/docs/records/l4e12/T-H1-PROCEDURE-DRAFT.md`, in the tree, 9f8f1d092489f6bf |
| OW-9 | U-01's smallest experiments and Saft's statement: send the drafted request to Saft (the 18 A for 60 s, the capacity after storage, the swelling); authorise one Saft cell's 18 A pulse test (NZ$ 238.72 and a 20 A load, a day) and the printed mock-up of four cells in the pocket (no purchase); actions, not questions | Saft: the MP 176065 xtd in a 4S1P pack: `v2/docs/records/l4e10/clarification/saft-mp176065xtd.txt`, in the tree, 6a1a37509dcab422 |


Not yet drafted (engineering work first, then the owner sends): Littelfuse, F1's total clearing I2t at 900 A and 58 V DC
(R-115, E11-16); Coilcraft, L10's inductance against current at temperature (R-120) and L1's Isat at 85 C (R-31); Milliohm,
R227's single-pulse rating (R-101).

## 9. Decisions this record takes (SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026 that engineering decisions are the session's)

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
6. **The 9 V envelope is stated, not corrected** (4b), as round 1.
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
   the choices that can still overturn the architecture. Its row stays in 8b with its class so the move is visible. **J_SOLAR's
   rating amends LH-02 and adds no handover row:** it is a property of the existing interface IF-EXT-DC (its `current.solar`),
   whose envelope changes to PANEL-ACC's three cases (3.987, 8.1817 and 13.82 A); no interface is created. **R-29 moves to A-3(b)'s
   8.1817 A:** the shrouded AWG 18 row's 7 A no longer covers SunPower's own 1.25 allowance, so the lead goes to AWG 16 on the
   standard header (10 A). *Reversed by:* route 2 found infeasible with route 1 still closed (L4E13-06), which returns U-03 to an
   architecture-level choice.
18. **The heat-rejection result integrated with T-H1's point at the profile's heat first and the 21.2 W point kept after it**
   (the consolidation, L4-E12's check 6). *Why:* the approved profile's +70 C class at +40 C (1.447 W/K) is the need no passive
   route reaches on the bound, so the reading at the profile's own heat decides the architecture; the conductance grows with the
   rise, so a reading at 42.4 W overstates it at 21.2 W, and the 21.2 W bands still decide E5's and E3-O's lines. Both points
   are stated; P1 supersedes the 21.2 W bands for the profile only. **The combined route's three items enter the register
   conditional on the reading** (R-170 to R-172, Layer 7 mechanical, OWED, Order "8, U-02"): they are mechanical and passive, so
   they change no circuit, no power and no endurance, and they are built only under a reading under 1.509 W/K; Layer 7 is their
   one owner, with Layer 6's +85 C picks for the face's switches named in R-171. *Reversed by:* a P1 reading at or over
   1.509 W/K (the route not needed), or a maker's document that bounds the fans' inside film.
   **Superseded in part by L4-E12's check 7:** the point at the profile's heat at +40 C established X2, a state no requirement
   asks for; the procedure's order is K1, K5, K10, K6, then K7 and K8 (5c), and the line at +40 C is the owner's CFL-002.

## 10. The assumptions register (criterion 3)

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

## 11. The downstream register and the release order (criterion 4)

`DOWNSTREAM-REGISTER.md` holds 166 items, each with one owner, an acceptance, a state and a step in the release order (out 10):
Layer 4 coordinator 9, Layer 5 interfaces 4, Layer 6 components 24, Layer 7 mechanical 9, Layer 8 board A generator owner 14,
Layer 8 board B generator owner 3, Layer 8 board C generator owner 1, Layer 8 board E generator owner 24, Layer 8 board P
generator owner 1, Layer 9 pre-layout analysis 24, prototype bench 39, firmware owner 10, TEST-PLAN owner 3, CONOPS owner 1. By
kind: 62 implementation changes (27 drafted, 19 missing a draft, 16 owed as work, none PENDING), 14 layout constraints, 43
tests, 42 pieces of evidence (none PENDING since L4-E7's surge round landed), 5 release records. They are category (a): 166 items, each
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

**The heat-rejection result** (L4-E12's check 6 at `589f18ac`, out 22): R-170 to R-172, the combined route's three items (the
fins, the loads led into the plate, the open lid's skin and braid). **The owner's amendment of 14:20** (out 24): L4-E12's
reconciliation (check 7) withdraws the framing of the profile at +40 C, so R-104 and R-151 are restated to the procedure's
points (K1, K5, K10, K6, K7 and K8), R-170 to R-172 and R-111 apply under any point's line, and R-139's lag test is restated
after the findings ledger's item 5; L4-E10's comparison (check 6) changes no row.

**L4-E7's panel-lead surge** (set 27 at `6d76453e`, out 23): R-156 restated, its input landed (the drafted U18 is the INA169 at
75 V, not the INA250's 40 V) and now OWED, layer 8's judgement under TRN-001; R-173 the drafted solar guard for D-10 and D-11
(`apply_gen_sch_e_solar_guard.py`, L4-E7's check 5); R-174 the CS116 and CS115 test at layer 8, since TEST-PLAN runs M1 to M5 only; R-175 the residual band between 25 V and the cut-off (layer 8's TRN-001 judgement); R-176
the guard's bench rows.

**The release order** (the register's own section): release records first (L4-E4's names accepted checks of L4-E4 to L4-E6 and
L4-E8; L4-E7's names L4-E7R's check 4; L4-E11's its check 3), with the text drafts for Layer 5, CONOPS and L4-E5; the missing
drafts; board A in one round with **R12, the ILIM_HIZ network drawn to the corrected knee and U34's R14 first, R11 after them,
the ballasts and Cc2 after R12**, R138 independent, U17's R227 after them; board E in one round with **Q1 and E-F1's capacitor
no later than R10**, R10 and C26/C27 only with board A's H3 line, L4-E7's settings, L4-E7R's backstop, then F1, the hot-swap
settings and **L4-E11's entry on top of them**, F1's 20 A holder and U-02's board E changes, the solar guard (R-173) after the entry draft; firmware's 4.70 A only on a board A
that carries H3, rules R-a to R-d, the hold and the SGP41's shutdown; the records re-issued; the bench, where V-A07 decides
R11; Layer 7's interconnect and enclosure before the harness and the case are built (the combined route, R-170 to R-172, only under T-H1's reading); Layer 6's panel unit (PANEL-ACC) after the
owner's purchase. The items under U-01's approach (II)
(R-105, R-106, R-110) wait on the owner's approval.

## 12. What stays PENDING, CONDITIONAL or open

- **PENDING:** none in the rows. L4-E7R is accepted (check 4 at `91e9a4b5`); IF-01, IF-02, LH-02, R-21, R-92 and R-98 carry its
  figures. L4-E13 (U-03) is accepted (check 3 at `fae419d1`, check 4 at `33b6b7be` after set 25). R-156's input, L4-E7's
  surge round (the findings ledger's item 1), landed in set 27; the row is OWED, layer 8's judgement under TRN-001. R-173 is the drafted
  solar guard (L4-E7's check 5).
- **Unresolved choices (no owner closes them):** U-01 (FEA-008's cell: a supported route on published evidence, the Saft MP
  176065 xtd, compared on one boundary in 2b'; its adoption not supported yet: the fit, the 18 A pulse, Saft's missing figures, the
  gauge data and T-H1 awaited, the owner's approval required; the HL18650V on its signed specification),
  U-02 (MESHSAT-1478: T-H1 decides, in the procedure's order K1, K5, K10, K6, K7 and K8; at +40 C the heat stage against the
  line the owner's CFL-002 sets, K1 1.806 W/K (a reading of 1.958 W/K) with option C or K3 0.903 W/K (0.941 W/K) with A or B;
  K6, the profile at +20 C, 1.447 W/K; charging with it 1.627 to 1.977 W/K; under a line the combined route, then the owner's), U-04 (source-only and dead-pack operation:
  (B1) selected and drafted, a downstream qualification test once R-157 is applied; on the board as drawn a CONDITIONAL
  CANDIDATE turning on TI's D1 and D3).
- **U-03, a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC):** no unit bought or measured (MISSING_EVIDENCE, the owner's
  purchase, OW-6); n at or under 2 a MODELLING_ASSUMPTION (R-149); the irradiance below the disturbance threshold an ASSUMPTION;
  J_SOLAR and PV_IN for A-3(c) a COMPONENT_LIMITATION (R-148); A-3(a) and A-4 on L4-E7R's regulation and backstop (drafted; the backstop's 93.5521 W CONDITIONAL on G_CM and the VIN+ bias); route 1's
  drafts for SunPower and Solbian unsent (OW-4).
- **Material defects addressed in drafts:** D-10 (a stiff 36 V source on the solar port) and D-11 (a reversed panel), single
  faults from L4-E7's panel-lead derivation, by L4-E7's selected remedies (check 5; the guard R-173, not applied); D-11
  CONDITIONAL on Q13's leakage above +25 C. D-12 (CS116 and CS115 on the drawn entry) is resolved in the drafted entry. **Open
  material defects:** none. D-06 is resolved in design by L4-E11, CONDITIONAL on its evidence
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
- **Recorded residuals outside every requirement:** the panel lead beyond L4-E7's basis, a direct strike or one nearer than
  MIL-STD-464's nearby lightning (REQ-041's mast-down alarm; R-156; with the guard D11's own rating); the band between 25 V and
  the solar cut-off, where a stiff source runs the stage at up to 116.5 W under the backstop's current trip (R-175, layer 8); A-N1 (the VIN_RAW clamps' 64.5 V against U2's 60 V at their rated pulse; no
  surge level is ruled, D-16) and the capability scenario on Q1, the LM74700-Q1 and U17's POE_VIN (part A). S-111 (VBUS20's
  single faults) is an engineering decision still open (R-48), with no exemption claimed; the short at DC_P and the weak-source
  band behind F1 are traced in 4e (F1's let-through R-115, D-06), not exempted.
- **Not claimed:** nothing is verified, built or measured; every row is a desk reading of documents and records.

## Appendix A. History: the inputs of each round, the earlier summary and the endurance statement

### A1. The inputs and the rounds

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
physical and owner, who supplies it, their fallback with its numbers and what each could overturn (8b), and stay
architecture-level choices; the register takes the rounds' rows and four items of the findings ledger
(`records/l4close/FINDINGS-LEDGER.md` at `fnd/l4close` `e1e99c4f`).
**The consolidation** (the owner's instruction of 2 October 2026, 11:25, with his corrections at 12:00; out 15 to 22) restructures
the page into sections 1 to 6 and takes four accepted results, each merged into this line and re-pinned: L4-E11's charger
selection ((B1), check 5 at `5aa18a69`), L4-E12's thermal verdict (T-H1 decides, check 5 at `7f41632d`), L4-E10's cell route
(the Saft MP 176065 xtd, checks 4 and 5 at `1c321773`) and L4-E12's heat-rejection comparison (U-02 a closure condition decided
by one T-H1 point at the profile's heat, check 6 at `589f18ac`, a framing check 7 withdrew). Set 27 (`fnd/int27` at `7037d714`) then re-pinned the loop
between this page, L4-E10 and L4-E12 and brought L4-E7's panel-lead derivation (`6d76453e`): CS116 and CS115 under REQ-063,
the sustained over-voltage and the reversed panel, with D-10 and D-11 known defects, later addressed in drafts by L4-E7's remedies (check 5 at `573fd5b8`, out 23, 7a). **The owner's amendment of 14:20**
(out 24): L4-E12's thermal reconciliation (check 7 at `6f8fd652`) corrected the thermal framing (2c', section 6), L4-E10's
battery comparison (check 6 at `e2d20bf2`) entered as the budget's cell row (2b'), the findings ledger (`fnd/l4close` at
`65be2c2c`) is cited in the exit, and R-139's lag test was restated after its item 5.

### A2. The summary as written in rounds 2 to 5

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

### A3. The endurance statement as written in rounds 2 to 5 (out 8; superseded in presentation by 2b)

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
  runs at the dead pack's VBAT (A-14). It is U-04 (section 8b), not later testing; R-85 is its verification at 12 and 24 V and
  does not settle it alone. Board E's always-on comes up on CELL_F from VBAT. **L4-E11 (accepted) answers it as far as the held
  documents allow:** arrangement (A), the drawn charger with rules R-a to R-d (the holds as a state table with S4's exception,
  R-b's two charge settings, the shedding sequence, the image's pre-charge); at a 9.00 V plug the shed warm-up (28.12 W at the
  plan figure) is carried with 0.98 W in hand while P1 stays at most 20.51 W; REQ-015 at 9.00 V at the plug is a CONDITIONAL
  CANDIDATE on E11-05, E11-06, E11-09, E11-22 and E11-23 (section 8b).

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
| **Pack fault**, the discharge FET opening under load | on battery the kit stops (the hot stop REQ-077 acts first on temperature); with a source U3 carries up to 84.5 to 99.6 W | as B1 |
| **Pack fault**, a cell or the block | BQ7720700's second level drives F2 (the chemical fuse); F1 25 A; under U-01's approach (II) U2 becomes the BQ7720704 (R-105) | MAKER thresholds |
| **Controller fault**, the host crashed | U3's watchdog falls back to 256 mA after 175 s (FW-A03); the H3 line is hardware and needs no host; the gauge's HWD stops charging in 10 s (FW-E01); the solar backstop is hardware on SWEN | the source bound holds with no firmware |
| **Controller fault**, U2 (Q2 short, FB open) | VBUS20 follows VIN_RAW; U3's 32 V passed; no clamp on VBUS20 | a single fault with no exemption claimed: S-111's options, R-48's engineering decision (open) |
| **Controller fault**, U5 (the LT8705A) | the backstop on SWEN acts while the regulation fails; L4-E7R lists the single faults that defeat the backstop or stop charging | Layer 8's fault analysis (R-100): no single fault both defeats the backstop and removes U5's own limit |
