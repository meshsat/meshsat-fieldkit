# L4-E9: the connected power architecture and Layer 4's closure gate for it (MESHSAT-1357, 1 October 2026; round 2 and its fix round, 2 October 2026)

**Prototype design, desk arithmetic.** Nothing is bought, built, powered or measured, and no board of this set has a layout.
This page edits no generator, registry record, Layer 3 file, `pcb_interfaces.yaml`, `HW-FW-CONTRACT.md` or other record; its
circuit changes are drafts (`apply_gen_sch_e_q1.py`, `apply_gen_sch_e_f1.py`, `apply_gen_sch_e_hotswap.py`, `apply_gen_sch_a_u17.py`) and its interface
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
as a decision-ready comparison that does not close FEA-008. Part A of round 2 (`L4E9-ENTRY-PROPOSALS.md`, out 11) checks Q1,
F1 and U17 against their makers' sheets. The fix round answers the collaborator's focused check (`checks/astra-check-l4e9-1.md`,
NOT YET, four blockers B1 to B4 and the minors): sections 4, 5, 6, 7 and 11 of the output and this page carry the answers. The final
round answers the targeted recheck (`checks/astra-check-l4e9-2.md`, NOT YET): the breaker's event and the timer's components
stated as open evidence (D-09 new), R227's energy as nominal with its maximum unresolved, L10's own assignment (R-120, R-121),
and L4-E7R's acceptance carried in. D-06 and U-04 are left as they stand while L4-E11 (`fnd/l4e11`) works on them.

**The owner's frame** (the Current owner brief, `OWNER-INSTRUCTION-2026-09-30.md`; his instructions of 1 and 2 October 2026):
battery and solar both required; the store inside the Peli 1450, no external battery; HF and the tablet kept; D-06's single 4S3P
stands; 48 to 72 hours an objective, tablet charging optional consumption; A2, the lid pack, the 16.340 V hold and P-03's 200 W
stay proposals. The applicable normal, reverse-input, transient and fault conditions are verified, not only headline ratings;
downstream tasks are kept apart from unresolved choices that could overturn the architecture, and an owner does not close a
choice. Layer 4 selects the power architecture and establishes its feasibility; Layer 5 writes the interfaces it creates.

## In short

- **Selected: A1**, D-06's one 4S3P pack inside the case, fed by two sources ORed onto one raw bus (the panel through board E's
  LT8705A stage, the vehicle or shore supply through its ideal diode and hot swap), converted once to a regulated 20 V charge bus
  by board A's LM5176 front end and once more by the BQ25731 charger onto the system node VBAT, from which every load converter
  and both outlets run. **A2** (base 4S6P plus a separately protected lid 4S9P) stays a proposal to change D-06.
- **The selected solutions are in the rows** (out 4): L4-E7R's regulation at RIMON_IN 31.6k (2.5485 A nominal, 2.9318 A highest)
  with its backstop on SWEN (static bound 93.5521 W, CONDITIONAL), corrected entry and CS101 correction (accepted); L4-E8's bank with its losses carried into
  the energy and thermal budgets; Q1 the CSD19532Q5B, F1 the Littelfuse 0997010.WXN and U17 on R227 (part A); the vehicle
  entry's OVLO at 39.71 / 41.44 / 43.18 V (R22 and R23 at 0.1 %) and its power limit with R24 22k (the fix round, B1).
- **Fourteen interfaces:** 2 MEET, 10 are CONDITIONAL, none PENDING (L4-E7R is accepted), and **two read NOT MET**: IF-11,
  where L4-E10's conditioned corner puts the inside air at 75.00 C in E5's dwell against the +70 C parts (U-02, MESHSAT-1478),
  and IF-05, where at C5's printed corners the hot swap's fault time is not half again over the start into VIN_RAW (D-09).
  IF-13 is CONDITIONAL with its transient conditions named.
- **Part A (out 11):** Q1 holds the reversed input's 66.15 V on 100 V with its junction at most 80.2 C; F1's 0997 is rated 58 V
  DC and 1000 A at 58 V DC against 43.18 V and 569.8 A, and opens no sooner than its 80 C column's 7.3 A against 6.15 A; U17 on
  5 mOhm reads 18.59 mV in service and 72.38 mV at the stage's fault bound against 81.92 mV, its pins at most 20.135 V against 36 V.
  A new finding there: CS101 at REQ-015's 36 V reached the drawn OVLO minimum, resolved by the OVLO resistors (D-02).
- **The fix round:** B1, Q7's power limit at 4.7429 mV of sense at 43.18 V (under TI's 5 mV): R24 22k (5.06 mV at its low corner),
  and the hot short's power-limit part at 43.18 V inside Figure 10, read from TI's vector drawing and derated to Q7's 94.3 C case
  (0.675 A against 0.777 A at the fault time's maximum with C5's printed rows stacked, CONDITIONAL on board E's copper and TI's
  power law past 10 ms), with the breaker's event and the timer's components open (R-118, R-119, D-09); B2, no exemption is claimed: F1's let-through waits on Littelfuse
  and its long-time band against the interconnect is an open engineering question (D-06); B3, R227's transients are bounded (every
  required event under the INA226's 40 V, a saturated sample distinguished from damage; R227's energy 2.879 mJ nominal, the
  maximum unresolved; L10 assigned in R-120 and R-121); B4, source-only and dead-pack operation is unresolved by the held
  documents and joins the choices as U-04.
- **L4-E7R accepted:** the CS101 correction (the bulk ahead of the sense bank, five 100 nF C0G across R66, R66 8.45k, RIMON_IN
  31.6k) keeps the filtered ripple at 0.0585 A against a 0.1130 A margin; the regulation 2.5485 / 2.9318 A, the static bound
  93.5521 W, the response allowance 1.087 ms after the filter's 0.4205 J; D-01 is resolved in design (drafted, not applied).
- **The closure gate (section 7): NOT CLOSED.** Criteria 3 and 4 PASS; 1, 2 and 5 are CONDITIONAL. Kept apart:
  - **two open material defects**: D-06, the vehicle entry's interconnect in F1's long-time band from a weak source, and D-09,
    the hot swap's fault time against the start at C5's printed corners (open engineering questions with alternatives; D-01 is
    resolved in design since L4-E7R's acceptance);
  - **four unresolved choices that could overturn the architecture**, which no owner closes: U-01 FEA-008's cell (L4-E10
    recommends a wide-temperature 18650, CONDITIONAL on its signed specification and the owner's two items), U-02 MESHSAT-1478
    (the inside air at the enclosure's floor against the +70 C parts), U-03 O-1 (a panel with a supported cold open circuit),
    U-04 source-only and dead-pack operation (the charger's behaviour with no usable pack);
  - **the downstream tasks**, 112 register items, each with one owner and an acceptance that close the assignment, not the item.
- **Endurance (section 10):** A1 runs 2.52 h on battery at +20 C and first interrupts at hour 6 or 2 on the candidate panel; it
  needs +1361.5 / +2094.1 Wh more storage for 48 / 72 h, plus at most 13.4 Wh a day at L4-E7R's accepted regulation and 17.7 Wh if U-01's
  cell is adopted. DR-01 stands; every mandatory function is intended to be delivered, subject to the open conditions named here,
  and no service is reduced to narrow the gap.

## 1. The selected architecture as one connected design

```
SOURCES
 panel (REQ-016: Voc <= 25 V at -20 C, <= 100 W into the stage)          vehicle or shore 9 to 36 V (REQ-015)
   | J_SOLAR (VH), F2 10 A                                                  | J_DCIN (VH), F1 0997010.WXN 58 V DC, D10 SMCJ40CA
   | PV_P -> sense bank -> TRK_VS: D4 SMCJ28A, 50 V bulk, C71..C74 [L4-E7R]  | U3/Q1 LM74700 ideal diode, Q1 CSD19532Q5B 100 V
   | R59 -> TRK_VIN                                       board E          | DC_P, D1 SMCJ40A, R19 10 mOhm
   v                                                                       | U6/Q7 LM5069 hot swap: UVLO 9 V, OVLO 39.71..43.18 V
 U5 LT8705AI buck-boost: hold 17.593 V (16.970..18.221),                   |   (R22, R23 0.1 %), limit 4.85..6.15 A, timer 3.13..8.16 ms,
                                                                           |   power limit R24 22k (22.02 W, 5.06 mV at 43.18 V)
   regulation RIMON_IN 31.6k 2.5485 / 2.9318 A; backstop on SWEN (U18,     | L2 SRF1260 choke
   INB filter, U19, U20) trips 3.0468..3.7408 A, static bound 93.5521 W     |
   TRK_OUT ceiling 28.28..30.15 V (R10 232 k, L4-E5)                       |
   | U4/Q2 ideal diode                                                      |
   +--------------------------------> VIN_RAW <-----------------------------+   (the tracker back-feeds DC_P through Q7's body diode)
                                        | D2 SMCJ40A (E and A); dock: four Mill-Max 9 A pins J_VR1..4
                                        v                                                   board A
 U2 LM5176 front end: R11 8 mOhm (average limit), R12 12 mOhm (cycle-by-cycle), no hiccup, U34 restart guard
                                        | VBUS20 19.08..20.96 V (bound 23.40 V); six EEHZK1V331P, each behind 45 mOhm; Cc2 3.3 nF
                                        v
 U3 BQ25731: R16 10 mOhm; IIN_HOST 4.70 A; the H3 line on ILIM_HIZ (U3 follows VIN_RAW in hardware, knee into HIZ < 9 V)
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
closed (59.2 C lid open); at the enclosure's floor (T-H1 1.666 W/K) L4-E10's conditioned corner, 70.00 C (E3-O) and 75.00 C (E5).

| Row | Interface | Voltage, both sides | Current asked / available (modes) | Losses | Thermal assumption | Protection, each side | Settled by | Status (class) |
|---|---|---|---|---|---|---|---|---|
| IF-01 | panel to the solar entry | at most 25 V at -20 C (candidate 24.05 V nominal) / D4 standoff 28 V on TRK_VS; under CS101 the input at most 27.82 V; TRK_VS 44.25 V and PV_P 44.74 V at the capability scenario | hot short circuit 6.802 A with the sheet's tolerance / F2 10 A; J_SOLAR's VH with AWG 18 no stated rating (7 A shrouded); under CS101 the filtered ripple at most 0.0585 A against a 0.1130 A margin | the lead about 0.0465 Ohm; the bank 0.5262 Wh a day | the entry at 62.1 C inside air; the bulk up to 4.45 times its ripple rating under CS101 (M2 reads it) | none / F2, the 50 V bulk ahead of the bank, D4 and C71 to C74, the INB filter (L4-E7R, drafted) | l4e O-1, L4-E7R (accepted) | CONDITIONAL (ASSUMPTION): the VH rating, the loop's typical rows (break-even 2.51 times), the bulk's temperature, the bank's pulse capability |
| IF-02 | PV_P through U5 to TRK_OUT | hold 16.970 / 17.593 / 18.221 V, at most 25 V; SWEN off below 2.662 V on TRK_LDO33 / ceiling 28.28 to 30.15 V | the stage's input at most 100 W (REQ-016) / the regulation 2.5485 A nominal, 2.9318 A highest (44.84 and 53.42 W in); the backstop 3.0468 to 3.7408 A at 25 V; the static bound 93.5521 W, the regulation's corner 73.3436 W | stage 0.93 DECLARED (C-8) | U5's junction about 105.4 C (INFERRED) against the I grade's 125 C | the regulation, the backstop on SWEN inside 1.087 ms after the filter's 0.4205 J / U4 | l4e7, l4e5, L4-E7R (accepted) | CONDITIONAL (CONDITIONAL): G_CM and U18's VIN+ bias (break-evens 168.8 % and 22.0 mA), the 0.1 s interpretation |
| IF-03 | TRK_OUT through U4/Q2 to VIN_RAW | at most 30.15 V / VIN_RAW to 43.18 V with TRK_OUT at 0 | 4.22 A at H3's lowest settle at the window / declared 10.33 A | Q2 | 62.1 C inside air | the stage / U4 blocks | l4e5, this record | MEETS (MAKER/NETLIST), with C26 and C27 re-rated (as drawn 121 % of 25 V) |
| IF-04 | vehicle and shore into DC_F and DC_P | 9 to 36 V with CS101's 2.83 V peak, reversed to -36 V / OVLO 39.71 / 41.44 / 43.18 V (37.78 / 40.09 / 42.49 V as drawn); D10 44.4 V either way at 25 C, 42.4 V at -20 C on a typical coefficient (CONDITIONAL) | entry limit 4.85 to 6.15 A; a stiff source's fault at most 569.8 A / F1 0997010.WXN 10 A (7.3 A at its 80 C column), 1000 A at 58 V DC; Q1 17 A; J_DCIN's VH with AWG 18 no stated rating; F1's long-time band from a weak source against the interconnect (D-06) | about 0.2 V in series; Q1 at most 0.361 W | R19 and Q7 at 6.15 A, 32 K rise (gen_sch_e.py); Q1's junction at most 80.2 C | supply's own / F1, D10, U3/Q1 (CSD19532Q5B), D1, the LM5069 | d8dec31, this record (part A, the fix round), l4e5 | CONDITIONAL (ASSUMPTION): the VH rating, F1's let-through (R-115), D-06 |
| IF-05 | DC_P through the hot swap and L2 to VIN_RAW | D1 clamp 64.5 V; the hot short at 43.18 V / LM5069 VIN 100 V, Q7 100 V | 6.15 A; the power limit with R24 22k 22.02 W nominal, 29.14 W with TI's 1.3 at its corners, 0.675 A at 43.18 V for the fault time (8.16 ms at C5's nominal, 2.035 to 11.871 ms with its printed rows stacked); the breaker's event (VCB's 13.131 A a threshold) OPEN / L2 6.89 A Irms; Q7's Figure 10 at 43.18 V and 11.871 ms derated to its 94.3 C case 0.777 A | R19 0.38 W | Q7's case at most 94.3 C in the hottest air the record holds (76.25 C) | D1 / D2, the LM5069's limits and timer | gen_sch_e.py, l4e5, this record (B1, `apply_gen_sch_e_hotswap.py`) | NOT MET (CONDITIONAL): the start-up margin at C5's printed corners (D-09); the power-limit part CONDITIONAL on board E's copper and TI's power law past 10 ms; the breaker's event OPEN (R-118); 4.7429 mV as drawn |
| IF-06 | VIN_RAW over the dock to board A | 8.466 V (HIZ, solar) to 30.15 V; vehicle 9 to 36 V; at most 43.18 V / U2 60 V | in service at most 4.629 A (9 V vehicle); fault at most 11.65 A (13.315 A at 7 mOhm) / declared 14.10 A, four 9 A pins | the dock's contacts | the pins about 6 K over air at 14.10 A (IF-AE-DOCK) | the entry, D2 / D2, U34 | l4e5, l4e6, IF-AE-DOCK | MEETS (INFERRED); A-N1 a recorded residual |
| IF-07 | VIN_RAW through U2 to VBUS20 | 8.466 to 43.18 V / 19.08 to 20.96 V, bound 23.40 V | 4.964 A asked through R11 / 4.986 A stacked minimum at 62.1 C with C-1's taps; highest permitted 7.262 A; R12 peak limit 8.06 A over a 6.50 A service peak | front end 0.93 DECLARED | FETs at most 130 C on the assumed 50 C/W (C-3); L1 at most 85 C (C-5); R11 68.8 to 77.5 C | U34, D2 / R11, R12, no hiccup, OVP; no clamp on VBUS20 (S-111) | l4e4, l4e5, l4e6, r11dep, s120 | CONDITIONAL (CONDITIONAL): C-7, V-A07, C-5, C-3 |
| IF-08 | VBUS20's bank | 23.40 V bound / the cans' 35 V | every can at most 2.4096 A (R11 8 mOhm), 2.7661 A (7 mOhm) / the rule's 2.7745 and 2.7709 A | ballasts at most 2.09 W (0.0093 W at nominal parts), in the energy and thermal budgets once | the cans' rise a bench reading (lifetime); the cold ESR envelope INFERRED; the ballasts' heat at most 1.25 K on the inside air at T-H1's floor | R12, R11 / the ballasts | l4e8 (accepted) | CONDITIONAL (CONDITIONAL): lifetime, the cold envelope, the 7 mOhm fallback |
| IF-09 | VBUS20 through U3 to VBAT | 19.08 to 20.96 V / U3 32 V absolute; VBAT 10.0 to 16.884 V; SYSOVP 19.0 to 20.0 V | the window needs 4.517 A / U3 minimum 4.537 A (C-7); 84.5 to 99.6 W at VBAT; charge at most 3.0 A | U3 0.9733 INFERRED | 62.1 C inside air; the charge only inside the cells' 0 to 45 C window (the gauge) | H3 line, IIN_HOST, VINDPM, ACOV / BATOVP 17.64 V, SYSOVP, the gauge's OCC 5 A | l4e4, l4e5, s120, FW-A02 | CONDITIONAL (CONDITIONAL): C-7 |
| IF-10 | VBAT and the pack | 10.0 to 16.884 V / D1 standoff 18 V, the pack FETs 30 V | PS-IDLE-SPEC 2.5 to 4.3 A; the PA keyed at 113 W 16.6 A at 10.0 V; PS-ALLTX's 18 A at an 11.48 V stack / declared 10 A continuous, 18 A peak; OCD1 20 A for 2 s; XT60 30 A | 22.5 mOhm path | the cells 0 to 45 C charge, -10 to 60 C discharge (REQ-046); FEA-008 not closed (L4-E10: approach (II), CONDITIONAL); F2 near +60 C at 18 A (PWR-F12) | D1, A F1 / BQ4050, BQ7720700, F1, F2 | pcb_pack_protection.yaml, POWER-THERMAL 7, FEA-004, L4-E10 | CONDITIONAL (CONDITIONAL): PWR-F12, U-01 |
| IF-11 | VBAT to the load converters | 10.0 to 16.884 V / the converters assumed to run to 10.0 V | PS-IDLE-SPEC 33.1 to 82.8 W (42.8 W plan); PS-ALLTX 168.9 to 272.0 W (203.8 W plan); 8.4 W undocumented / each converter's own rating (pwr_budget.py) | the converters' floors | the heat per state (POWER-THERMAL 9); at L4-E10's conditioned corner the inside air 70.00 C (E3-O) and 75.00 C (E5) plus up to 1.25 K, against the +70 C parts | eFuses (TPS2596 21 V against SYSOVP 20.0 V) / each converter | pwr_budget, load_trace, POWER-THERMAL, L4-E10 | NOT MET (ASSUMPTION): E5's inside air against the +70 C parts (U-02); the 8.4 W |
| IF-12 | VBAT to the USB-C outlet | VBAT 10.0 to 16.884 V into U19 / 5, 9 and 15 V contracts | 3 A each; with PS-TYP 112.3 W plan, 7.8 A at 14.4 V / trip 3.793 to 4.576 A; receptacle 5 A; J_USBC_OUT unrated | U19 0.93 | R138 its own 3.5 K at the trip (L4-E4); 62.1 C inside air | OUTLET_OK, C2 / U18 OCP and OVP | l4e4 | CONDITIONAL (ASSUMPTION): VI(TRIP)'s row, the header |
| IF-13 | VBAT through R227 to the PoE stage and U17 | VBAT 10.0 to 16.884 V, 20.135 V at the pack-open bound, 29.2 V at D1's pulse / 54 V; U17 on VBAT and POE_VIN, common mode at most 20.135 V against 36 V (as drawn 54 V against 40 V); POE_VIN at most 33.77 V at a hard connect; 0.072 V under VBAT in the boost current-limit case only | 0.6 A at 54 V; 3.682 A at the stage's input at 10.0 V, 14.33 A at its fault bound; a buck fault 11.71 A peak, 10.71 A RMS / R227 5 mOhm 3 W; 18.59 and 72.38 mV against 81.92 mV (16.384 A); a saturated sample is not damage (40 V differential) | U16 0.88; R227 at most 0.0685 W in service, 0.58 W in a buck fault, 2.879 mJ nominal at a hard connect (the maximum unresolved) | 62.1 C inside air | OUTLET_OK / U16's limits, TPS23861 | HF-F02, this record (part A, B3) | CONDITIONAL (CONDITIONAL): R227's pulse rating and capacitance envelope (R-101), L10's L(I) at temperature (R-120, R-121) |
| IF-14 | VBAT to the PA rail | VBAT 10.0 to 16.884 V into U13 / 13.8 V | the drain 5.4 to 8.2 A uncharacterised; the pack 16.6 A at 10.0 V / declared 5 / 6 A, the stage's loop 7.2 to 9.5 A | U13 0.93 | key-down at most 60 s, the flange gated at +75 C and cut at +85 C (D-11, PROVISIONAL) | the K rules, OUTLET_OK / the stage | POWER-THERMAL 7.2, FEA-004 | CONDITIONAL (ASSUMPTION) |

**What the rows show about the stages together:**
- H3 holds the front end's input under the vehicle entry's minimum limit at every voltage (4.629 A at 9 V against 4.85 A; it
  reaches the entry's 4.80 A basis only if the front end's 9 V efficiency falls to 0.897, C-8).
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
  (58 V), Q2 and U2 (60 V), U4 (75 V), C26 and C27 (re-rated to 50 V) and D10 (44.4 V at 25 C).

## 3. Simultaneous operation (out 5)

Solar at the window, a vehicle at 24 V, the full load and charging together:
- **The sources share.** The tracker's ceiling (28.28 V at its lowest) sits above a 24 V vehicle, so the panel carries the bus
  first and the vehicle's ideal diode conducts only for what the panel does not give. The front end's input is H3's line at
  whatever VIN_RAW the sources settle at: at most 4.194 A at 24 V, 87.4 % of the entry's basis.
- **What reaches VBAT** is U3's: 84.5 to 99.6 W (its minimum at the lowest bus to its board-current maximum at the bus's top).
- **The loads take it first, the pack the rest.** PS-IDLE-SPEC (42.8 W) leaves up to 41.7 W to charge at most 3.0 A; PS-TYP with
  the tablet (112.3 W) draws at least 27.8 W from the pack; the PA keyed alone at 113 W draws at least 77.8 W; PS-ALLTX at least
  119.3 W (plan) and 187.5 W (high). With a source the pack's current is lower than on the pack alone, so D-11's floors hold as
  they do on the pack alone, and the outlets drop while the PA keys (OUTLET_OK).
- **No stage is pushed past its limit:** the entry under its minimum limit, R11 at 4.964 A at most, every can at most 2.4096 A,
  the charge at most 3.0 A against the gauge's OCC 5 A.
- **Per source at the 9 V floor (an envelope to state, not a defect).** At 9 V H3 admits 19.9 to 36.6 W at VBAT, and the entry's
  own limit bounds any control at 39.5 W. So a 9 V vehicle runs PS-IDLE-SPEC (42.8 W) with the pack supplementing, and charges
  only while the kit draws under 19.9 W. REQ-015's acceptance ("operates and charges across 9 to 36 V") is met in both of its
  parts; the profile's load and a charge together at 9 V are not in its text. At 12 V up to 47.4 W, at 24 V up to 90.6 W.

## 4. Startup (out 6)

- **Cold start on the pack** (`ARCHITECTURE.md` 4.3): with the pack connected the LTC2954 holds RAIL_EN low and board E's
  sensor controller runs on CELL_F; MAIN brings up board A's +3V3; DEV_EN is on by R42, so +5V_DEV and then the panel
  controller start; the panel runs FW-C01's order (PI_KILL low, ZEROIZE read, the expanders' outputs before their configuration,
  the charger with FW-A01 first, then SLOT_EN one at a time); each stage soft-starts on VBAT. The pack's precharge pin J_PRE1
  (10 Ohm, 2 W) mates first when the stack is seated.
- **A source arriving:** the LM5069 starts at 9 V with its timer bounding the inrush; U3 is in HIZ below 8.466 V and out of it
  above 8.713 V, and the H3 line bounds its input from its first switching cycle with no host. The panel: the stage's own UVLO and
  soft start, then the hold at 17.593 V; SWEN stays off while TRK_LDO33 is under 2.662 V whatever the ramp (L4-E7R), and each
  backstop trip restarts the stage through its soft start.
- **A source leaving:** VBAT is the system node with no battery FET, so the pack carries the loads without a break; U3 resets
  IIN_HOST to 3.25 A and firmware writes 4.70 A again (FW-A16 restated); VIN_RAW falls through the restart guard (8.31 V at its
  highest) and the front end stops; the bank bleeds in 0.455 to 1.494 s (L4-E8).
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
  does not settle it alone. Board E's always-on comes up on CELL_F from VBAT.

## 5. Faults, traced across the stages (out 7, out 11)

| Fault | What acts, stage by stage | Bound, and its class |
|---|---|---|
| **Source short**, the vehicle lead shorted while the tracker holds the bus | U3/Q1 blocks the reverse current at DC_F; DC_P stays back-fed from VIN_RAW | Q1 stands off DC_P, at most 30.15 V (INFERRED) |
| **Source short**, the panel lead | U4/Q2 blocks VIN_RAW into TRK_OUT; U5's input falls through its UVLO; SWEN off by default | INFERRED (L4-E7R) |
| **Output short**, VBUS20 | R12 holds the front end's output at 4.57 A at 9 V, R11 at 7.262 A above 14 V; VIN_RAW carries at most 11.65 A; the vehicle entry limits at 4.85 to 6.15 A and opens after 3.13 to 8.16 ms (then retries); the panel's stage regulates at 2.9318 A at most and its backstop trips at 3.7408 A at most, inside 1.087 ms after the INB filter's held charge; U34 cycles the front end | L1 at most 12.60 A, FETs at most 130 C on the assumed 50 C/W (CONDITIONAL, C-3, C-5) |
| **Output short**, behind the vehicle hot swap (B1 and the recheck) | the breaker's event (VCB's maximum over R19 at -1 %, 13.131 A, is a threshold; tCB is measured with no GATE load, so the event's peak and Q7's loaded turn-off are OPEN, R-118), then the power limit with R24 22k: 22.02 W nominal, 22.41 W at its corners, 29.14 W with TI's 1.3 margin, 0.675 A at 43.18 V for the fault time (2.035 to 11.871 ms with C5's printed rows stacked), then off and a retry at 0.5 % duty (the drawn R24 20k: 4.7429 mV of sense, under TI's 5 mV) | the power-limit part inside Q7's Figure 10 at 43.18 V, read from TI's vector drawing and derated to its 94.3 C case: 0.777 A at 11.871 ms (TI's power law 18.7 % past 10 ms; CONDITIONAL on board E's copper); the start-up margin NOT MET at C5's corners (D-09, R-119) |
| **Output short**, VBAT | the gauge's SCD (60 A in 0.2 ms), OCD2, the 25 A blades, F2, against 240 to 480 A prospective; U3 at its input limit | MAKER thresholds (pcb_pack_protection.yaml) |
| **Output short**, an outlet | USB-C: U18's OCP at 3.793 to 4.576 A in 15 us, U19's own limit; PoE: U16 leaves boost and its buck valley limit holds the input under the boost bound, board B's port limit; PA: U13's loop; monitor and heater: their eFuses | CONDITIONAL (VI(TRIP)'s row, bench (a)); U17 reads the PoE fault inside its full scale (INFERRED) |
| **Reverse**, the vehicle input at -36 V (REQ-015) | D10 (two-way, 44.4 V breakdown) does not conduct; U3/Q1 block; DC_P back-fed from the raised ceiling through Q7's body diode | **Q1 at 66.15 V: NOT MET on the drawn 60 V part, MEETS on the CSD19532Q5B (100 V)**; the LM74700-Q1 under its 70 V recommended, 75 V absolute, its ANODE at -36 V against -65 V (INFERRED, MAKER) |
| **Reverse**, the panel | D4 forward at the panel's short circuit (DECISION-31 E-N1) | recorded by DECISION-31; F2 above the panel's 6.802 A |
| **Disturbance**, TEST-PLAN M2 (CS101), M3 (CS114), M7 (decision 34's 8 kV contact and 15 kV air); no surge level is ruled (D-16, CHO-003) | Vehicle entry: CS101's 2.83 V peak at 36 V reaches 38.83 V, past the drawn OVLO minimum, under the selected 39.71 V (D-02); CS114 holds DC_F to 3.17 V; E-F1's 1 uF holds a negative discharge to 2.25 V. Solar entry: CS101 keeps the input at 27.82 V under D4's 28 V; U5's differential at most 0.2094 V against 0.3 V; the backstop's filtered ripple 0.0585 A against its 0.1130 A margin (D-01, resolved in design) | INFERRED (part A), MODELED (L4-E7R, CONDITIONAL on the loop's typical rows); A-N1 a recorded residual |
| **Capability scenario**, D10 at its rated pulse (not a requirement) | negative: Q1 at 100.5 V with DC_P at 36 V, avalanche energy at most 83.6 mJ against EAS 274 mJ; the LM74700-Q1's 75 V passed once DC_P exceeds 10.5 V | NOT MET, outside every requirement (D-16; DECISION-31) |
| **A short behind F1, a stiff source** (it needs a prior short of D10, D1, E-F1's capacitor or C4) | F1 alone clears it, at up to the selected OVLO maximum 43.18 V; at most 569.8 A (copper alone at -20 C; 623.9 A with an AWG 16 lead); 0.286 ms is an illustration from the typical melting I2t, not a clearing time | the 0997010.WXN: 58 V DC, 1000 A at 58 V DC: MEETS (MAKER); the drawn 297 MINI's 32 V: NOT MET as drawn; the conductors' withstand against the let-through CONDITIONAL on the total clearing I2t (R-115); Q1 in the path is not shown to hold it and is not a conductor or connector of REQ-045 (no exemption claimed) |
| **A short behind F1, a weak source** (under ECSS 6.17.3c's 30 A) | F1's long-time band: 10 to 11 A with no opening, 13.5 A up to 600 s, 20 A up to 5 s | through VH 10 A, D38999 size 16 13 A and a cable and lead with no held rating: NOT ESTABLISHED, defect D-06, an open engineering question (section 7a) |
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
   rows cover this setting.
9. **D-06 left open, not selected:** an interconnect rated to F1's 20 A point is the engineering resolution, but its parts are
   the receptacle's contacts and the harness (Layer 7) and a heavier cable raises the stiff-source current toward F1's 1000 A,
   so the selection waits on the makers' data and the harness (R-113, R-29); no exemption is claimed meanwhile.
10. **U-04 added, R227's capacitors kept behind it:** source-only operation is an architecture question the held documents do
   not settle (B4); C81, C82 and the bypass capacitors close U16's input loop, and the transient bounds hold with them behind R227
   (B3).
11. **L4-E8's ballast loss is counted once:** on the charge path in the energy budget and as heat in the thermal budget, never
   again once a measured efficiency includes it (L4-E8's own rule).

## 7. The closure gate

The gate's rule, held by the script (out 9) and by `test_l4e9.py`: a criterion reads PASS only on interface rows that read
MEETS, never on an ASSUMPTION, CONDITIONAL or PENDING row; never while an unresolved choice it names stands; and criterion 2
never while a material defect is open. Every feasibility claim below cites its evidence by class; the software tests establish
tested behaviour of the record's own scripts and drafts only, never an electrical or thermal property.

| Criterion | Evidence | Verdict | The exact constraint (if not PASS) | Could it overturn the architecture? |
|---|---|---|---|---|
| 1. One architecture selected; its mandatory functions have a defensible feasibility basis | A1 under D-06 (section 1); rows IF-02, IF-04, IF-05, IF-07, IF-09, IF-10, IF-11, IF-12, IF-13: REQ-014 (the pack), REQ-015 (IF-04 to IF-06, MAKER and INFERRED; source-only operation U-04), REQ-016 (IF-01, IF-02, CONDITIONAL and MODELED), REQ-017 (IF-12, IF-13), REQ-018 (IF-10, IF-14), REQ-045 (section 5, D-06), REQ-046 and REQ-077 (IF-10, L4-E10), REQ-075 (IF-09); choices U-01 to U-04 | CONDITIONAL | the solar function's 100 W bound is CONDITIONAL on G_CM and U18's VIN+ bias (L4-E7R) and its source on O-1 (U-03); PS-ALLTX's chain at 18 A for 60 s (PWR-F12) is an open obligation; the battery path's thermal design (FEA-008, U-01), the electronics' inside air at the enclosure's floor (MESHSAT-1478, U-02) and source-only operation with a dead or absent pack (U-04) are unresolved choices | possibly: U-01, U-02 and U-04 could change D-06's pack, the sealed case's thermal design or the charger's power path; the rest resolves by a value, a part or a measurement on the same topology |
| 2. Material power-path defects have engineering resolutions and bounded supporting calculations | rows IF-01, IF-02, IF-04, IF-05, IF-13; defects D-01 to D-09 below (D-06 and D-09 open; D-01 resolved in design since L4-E7R's acceptance; the rest drafted or bounded with their conditions named) | CONDITIONAL | two material defects are open: D-06, the vehicle entry's interconnect in F1's long-time band from a weak source, where no maker's time-current limit is held for the contacts and the cable; D-09, the hot swap's fault time against the start into VIN_RAW at C5's printed corners; both open engineering questions with alternatives. D-01 is resolved in design (L4-E7R accepted, drafted, not applied) | no: an interconnect, a cable or a stated source capability, and a timer capacitor, at the vehicle entry |
| 3. Remaining assumptions are explicit, with their impact and verification method | section 8's register A-01 to A-23 | PASS | | |
| 4. Downstream implementation changes, layout constraints and tests have named owners and acceptance criteria | `DOWNSTREAM-REGISTER.md`: 112 items, each with one owner and an acceptance, among them L10's own assignment (R-120, R-121), the timer's (R-119) and M2 (R-122); the release order (L4-E6's R12 before L4-E8's ballasts; L4-E4's release record first); `LAYER5-HANDOVER.md` LH-01 to LH-09 | PASS | | |
| 5. No unresolved uncertainty could overturn the selected architecture while described merely as routine later testing | rows IF-01, IF-10, IF-11; choices U-01 to U-04 below, each with its constraint, the evidence that settles it and its alternatives | CONDITIONAL | four unresolved choices could overturn it and are named as such, not as later testing: U-01 (FEA-008's cell), U-02 (MESHSAT-1478, the inside air against the +70 C parts), U-03 (O-1, a panel with a supported cold open circuit), U-04 (source-only operation with a dead or absent pack); an owner and an acceptance criterion do not close them | yes for U-01, U-02 and U-04 (D-06's pack, the sealed case's thermal design, the charger's power path); U-03 decides the solar source, not the topology |

**Layer 4's power architecture closes: NO** (criteria 1, 2 and 5).

### 7a. The material power-path defects (criterion 2)

| Defect | What | The constraint | The options | State |
|---|---|---|---|---|
| D-01 | the solar backstop trips under TEST-PLAN M2 (CS101) | CS101's injected current crossed the sense bank and its peaks over the trip less the operating current stopped the stage for td each time, so solar charging stopped for the test, against M2's 'no upset' line (L4-E7R's check 3) | the bulk moved ahead of the sense bank, five 100 nF C0G across R66 (3.960 to 4.496 ms), R66 8.45k and RIMON_IN 31.6k: the filtered ripple at most 0.0585 A against the 0.1130 A margin, the response allowance 1.087 ms after the filter's 0.4205 J; CONDITIONAL on the loop's typical rows (break-even 2.51 times), the bulk's temperature, the bank's pulse capability, the 0.1 s window | RESOLVED (drafted): L4-E7R accepted (check 4, fnd/l4e7 91e9a4b5, figures at 675b8068); register R-21 and R-98, apply_gen_sch_e_backstop.py; M2, R-122 |
| D-02 | the vehicle entry's hot swap opens under TEST-PLAN M2 (CS101) at REQ-015's 36 V | 36 V plus CS101's 2.83 V peak reaches 38.83 V, past the drawn OVLO minimum 37.78 V | R22 100k and R23 6.42k, both 0.1 %: OVLO 39.71 / 41.44 / 43.18 V (selected, SESSION); M2 at the source's nominal (not taken) | RESOLVED (drafted): register R-94, apply_gen_sch_e_hotswap.py |
| D-03 | Q1 over its rating on a reversed input with the raised ceiling | 66.15 V across the drawn 60 V BSC039N06NS | the CSD19532Q5B (100 V) | RESOLVED (drafted): register R-17, apply_gen_sch_e_q1.py |
| D-04 | F1 cannot interrupt at the entry's highest steady input | the drawn 32 V DC MINI against 43.18 V | the Littelfuse 0997010.WXN (58 V DC, 1000 A at 58 V DC) | RESOLVED (drafted): register R-18, apply_gen_sch_e_f1.py |
| D-05 | U17 on the 54 V rail (HF-F02) | 54 V on the INA226's IN+ and IN- against its 40 V absolute | U17 on R227, 5 mOhm in the PoE stage's input | RESOLVED (drafted): register R-06, apply_gen_sch_a_u17.py |
| D-06 | the vehicle entry's interconnect in F1's long-time band from a weak source | a source under 30 A (ECSS 6.17.3c's three times) can leave 10 to 11 A flowing indefinitely, 13.5 A for up to 600 s and 20 A for up to 5 s through J_DCIN's VH contact (10 A), the D38999 size 16 contacts (13 A test current) and the kit's cable and lead, whose held sheets print no current or time-current rating | an interconnect rated to the fuse's 20 A point (size 12 contacts at 23 A, a 30 A board connector, a cable whose maker rates it, with the stiff-source current re-checked against 1000 A); the source's capability stated in REQ-015 (the owner's); the makers' overload data obtained (Lapp, JST, Amphenol) | OPEN: an open engineering question (R-113) |
| D-07 | the hot swap's power limit under the sense voltage TI recommends | R24 20k gives 4.7429 mV at 43.18 V, under SNVS452G's 5 mV, and the hot-short pulse was compared at 36 V with a by-eye reading | R24 22k 1 %: 5.06 mV at its low corner; the power-limit part at 43.18 V and the timer's stacked maximum inside Figure 10 derated to Q7's case; the breaker's event and the timer's components stay open (R-118, R-119, D-09) | RESOLVED (drafted): register R-94, apply_gen_sch_e_hotswap.py |
| D-08 | R227's transients bypass U16's current control | the capacitors behind R227 (20.2 uF) charge outside U16's cycle limit, so 72.38 mV did not bound every transient | bounded in part A: the differential at most the VBAT step, POE_VIN under 40 V in every required event, a saturated sample distinguished from damage; R227's pulse energy 2.879 mJ nominal, the maximum unresolved until a capacitance envelope and the pulse's shape meet Milliohm's rating; moving the capacitors ahead of R227 not taken (they close U16's input loop) | RESOLVED (bounded, conditions named): IF-13's checks; R-101 (Milliohm's pulse rating), R-117 (the loop's inductance), R-120 and R-121 (L10) |
| D-09 | the hot swap's fault time against the start into VIN_RAW | with C5 (100 nF, K, X7R) at its printed rows stacked the fault time's minimum is 2.035 ms, under TI's half-again margin over the start into VIN_RAW at 43.18 V (3.814 ms; the start alone 2.542 ms at the corners, 1.324 ms nominal), the front end's own load during the start not included | C5's real envelope read and the start re-run with the front end's load; a C5 with a tighter envelope (150 nF C0G at 5 % gives 4.46 to 12.852 ms, inside both the start margin and Figure 10's power law derated, no part read); a higher power limit (a larger pulse against the SOA) | OPEN: an open engineering question (R-119) |

### 7b. The unresolved choices that could overturn the architecture (no owner closes them; U-04 added by the fix round, B4)

| Choice | What | The exact constraint | The evidence that settles it | The alternatives | The owner's items | What it could overturn |
|---|---|---|---|---|---|---|
| U-01 | FEA-008: the battery path's cell and thermal design (L4-E10, final) | LO-01d to LO-01g (E3-O, E5, E3-S, E4-S with the pack fitted) have no route that holds on held evidence; LO-01a holds only with T-H1 at least 1.666 W/K in both lid states | the HL18650V's signed specification confirming storage at +71 C and -33 C at the stored charge and the +80 C idle limit, then L4-E10's margins re-run (1.06 K under H1 and 0.97 K under U2's INFERRED trip at LO-01e); T-H1 measured in both lid states | (II) a wide-temperature 18650 in D-06's 4S3P (recommended, CONDITIONAL); (I) the 35E with powered cooling (INCONCLUSIVE: up to 35 W into the sealed case); (III) latent storage and a primary-fed heater (rejected at LO-01d to f; added energy storage under D-06); a requirement change (the owner's, D-29) | (1) send the drafted request for the specification; (2) once it confirms, approve the cell change (D-06's about 145 Wh to about 121 Wh nominal, REQ-046 and REQ-077 restated with the cell, about USD 42 a pack); if declined, LO-01d to g stay a release gate | D-06's pack energy (16.4 % less usable) and the pack's protection settings; the power path's topology stays |
| U-02 | MESHSAT-1478: the inside air at the enclosure's floor against the +70 C parts | at T-H1's 1.666 W/K floor the uncooled inside air is 70.00 C in E3-O and tends to 75.00 C in E5's +60 C dwell (L4-E10, MODELED), plus up to 1.25 K from L4-E8's ballasts, at or past the +70 C ratings of the SA868, the AW7915-AED cards, the LimeSDR and the Xenarc | T-H1 measured in both lid states and the parts' temperatures in E3-O and E5 on the prototype, or a thermal design whose modelled inside air stays under +70 C at those levels | an enclosure conductance above LO-01a's floor (the plate, the fans, the case); parts rated past +70 C; D-02a's +55 C margin and E5 restated (the owner's, D-29); a reduced mode at those levels | none yet: an architecture-level thermal question for the kit's thermal owner (MESHSAT-1478); a requirement change would be the owner's | the sealed case's thermal design (no vent, the ruling of 7 September 2026) or D-02a's margin; not the power path's topology |
| U-03 | O-1: a solar panel with a supported maximum open circuit inside REQ-016's window | REQ-016 admits a panel only with an open circuit at or below 25 V at -20 C; the candidate's nominal sheet gives 24.05 V and no supported maximum (source compliance INCONCLUSIVE) | a panel maker's stated maximum, or a measured lot, at -20 C at or under 25 V | the SPR-E-Flex-100 with the maker's tolerance; another panel inside the window; REQ-016's window restated (the owner's) | none until a panel is pinned | which panel the mandatory solar function uses; the stage and the window stay |
| U-04 | source-only and dead-pack operation (the focused check's B4) | U3 has no battery FET: with the pack absent it holds VBAT at ChargeVoltage and with the pack's discharge FET open at CUV it charges at the 384 mA clamp, VBAT near the pack's 10 V (INFERRED from SLUSE66A 9.3.1, 9.3.17, 9.6.2.1); at a 9 V source the line gives 19.9 to 36.6 W against PS-IDLE-SPEC's 42.8 W, and before the host writes IIN_HOST about 31 W; whether the converter keeps VSYS up with charge inhibited (Q-TI-3), whether the gauge lets a pack at CUV take charge with no precharge FET, and whether every load converter runs at the dead pack's VBAT (A-14) are not in any held document | TI's answer to Q-TI-3 and O-CHG-2, the gauge's FET states at and below CUV read in SLUUAQ3A for this image, the load converters' minimum input read from their sheets, then R-85 run at 12 V and 24 V with the pack's discharge FET open and with the pack absent | a charger with a battery FET power path, so VSYS is regulated apart from the pack; a source-fed keep-alive rail for the controllers and the gauge's host; a precharge path on board P for a pack at or below CUV; REQ-015's acceptance restated to a pack above CUV (the owner's) | none unless the answer is negative and REQ-015 is restated; sending Q-TI-3 is an outside contact the owner makes (the request is prepared in REVIEW-REQUEST.md) | the charger's power path (a battery FET or an added rail) if the converter cannot carry the loads without a pack; with a negative answer the kit with a dead or absent pack does not run from a source and a dead pack is not recovered in the kit |

### 7c. The downstream implementation and verification tasks (criterion 4)

`DOWNSTREAM-REGISTER.md` (section 9): an owner and an acceptance criterion close the ASSIGNMENT, not the item. The items that
exist only under a choice's outcome are marked there (Order "U-01"); they do not stand in for the choice.

**What closure needs, exactly:** D-09 answered by C5's real envelope and the start with the front end's load (R-119), and the
breaker's event measured (R-118); D-06 answered by an interconnect, a
stated source capability or the makers' data (R-113), and F1's let-through filed (R-115); U-04 settled by TI's answer, the
gauge's FET states and the converters' minimum input (R-114) with R-85 run at 12 and 24 V; U-01 settled by its evidence and the
owner's items (or held open as a release gate); U-02 settled by T-H1 and the parts' readings or a thermal design; U-03 settled
by a panel; and for criterion 1 the CONDITIONAL inputs with their named evidence (G_CM and U18's VIN+ bias R-101, PWR-F12 R-46
and R-83, C-7, C-3, C-5, V-A07). The coordinator decides whether a CONDITIONAL criterion with these named is acceptable for
Layer 4's closure; this record does not.

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
| A-18 | Q1's RDS(on) normalised 1.95 at 150 C read by eye from Figure 8; Figure 10 now read from TI's vector drawing (no longer by eye; round 2's 3.0 A at 36 V withdrawn, 2.52 A); Q7's case at most 94.3 C, derived from the hottest inside air and RthetaJA on 1 in2 2 oz (board E's copper an ASSUMPTION) | IF-04, IF-05 | Q1's junction (80.2 C) and Q7's hot-short margin (0.913 A against 0.675 A) | R-112, R-118 on the bench |
| A-19 | The OVLO's corners stacked: OVLOTH 2.4 to 2.6 V (MAKER) with R22 and R23 at 0.1 % | IF-04, D-02 | D-02's 0.88 V and 1.22 V margins | R-81 (the OVLO trip recorded inside 39.71 to 43.18 V) |
| A-21 | The power limit's spread at R24 22k: TI's Equation 9 at the resistors' corners times TI's own 1.3 margin (SNVS452G 9.2.1.2.5); the PWRLIM rows are tested at 48 V and 150 kOhm only | IF-05 | the hot-short pulse's 0.675 A against 0.777 A at the fault time's maximum | R-118 |
| A-23 | C5's printed rows stacked (K +-10 %, X7R +-15 % over temperature and +-15 % after endurance; DC bias not taken) for the fault time's envelope, and Figure 10 carried by TI's power law past its 10 ms line | IF-05, D-09 | the fault time 2.035 to 11.871 ms; the start margin NOT MET at the corners; 0.777 A at the maximum | R-119 |
| A-22 | R227's loop inductance (no layout) and the undamped ideal step as the bound on POE_VIN's ringing | IF-13 | the capability pulse's 41.52 V in that limit; every required event under 40 V | R-117 |
| A-20 | L4-E10's conditioned corner (about 25 W of the kit's heat at E3-O, derived here from its 70.00 C and T-H1's floor) with L4-E8's 2.09 W added on the same conductance | IF-08, IF-11, U-02 | the inside air's +1.25 K, U-02's margin | R-104 (T-H1), R-111 |

## 9. The downstream register and the release order (criterion 4)

`DOWNSTREAM-REGISTER.md` holds 112 items, each with one owner, an acceptance, a state and a step in the release order (out 10):
Layer 4 coordinator 5, Layer 5 interfaces 2, Layer 6 components 13, Layer 7 mechanical 2, Layer 8 board A generator owner 11,
Layer 8 board B generator owner 1, Layer 8 board E generator owner 17, Layer 8 board P generator owner 1, Layer 9 pre-layout
analysis 20, prototype bench 34, firmware owner 5, TEST-PLAN owner 1. By kind: 36 implementation changes (18 drafted, 10
missing a draft, 8 owed as work, none PENDING), 12 layout constraints, 34 tests, 26 pieces of evidence, 4 release records. They
are category (a): an owner and an acceptance close the assignment, not the item, and none of them stands in for U-01 to U-04
or for the open defects D-06 and D-09.

**Every draft of L4-E4 to L4-E8 is in it** (R-01, R-02, R-04, R-05, R-07, R-09, R-12, R-19, R-20, R-23), with d8dec31's E-F1
draft (R-16), L4-E7R's backstop draft (R-21) and this record's four (Q1 R-17, F1 R-18, U17 R-06, the hot-swap settings R-94).
**The missing drafts:** U3's ILIM_HIZ network (R-03, L4-E5), R10, C26/C27 and TRK_OUT's declaration (R-13 to R-15, L4-E5), the
45 mOhm lcsc line (R-08), board A's declaration texts (R-10), the 0997's energy chain and derating entries (R-95, R-96), BANK-R1
on board B (R-107), the hot-swap resistors' LCSC codes (R-116). **New this round:** L4-E7R's follow-up, bench rows, fault list and clarifications (R-98 to R-101),
L4-E8's C190 and C191 evidence (R-102), L4-E10's downstream items (R-103 to R-110), MESHSAT-1478's verification (R-111) and
the fix round's (R-112 Q1's turn-on and light load, R-113 D-06's data, R-114 U-04's evidence, R-115 F1's let-through, R-116 the
hot-swap codes, R-117 R227's loop, R-118 the hot short on the bench) and the final round's (R-119 the timer's components and the
start, R-120 and R-121 L10's saturation-aware hard short and its bench sweep, R-122 M2 on the solar lead).

**The release order** (the register's own section): release records first (L4-E4's names accepted checks of L4-E4 to L4-E6 and
L4-E8; L4-E7's waits on L4-E7R's follow-up); the missing drafts; board A in one round with **R12 and the ILIM_HIZ network
first, R11 after them, the ballasts and Cc2 after R12**, R138 independent, U17's R227 after them; board E in one round with
**Q1 and E-F1's capacitor no later than R10**, R10 and C26/C27 only with board A's H3 line, L4-E7's settings, L4-E7R's backstop
with its follow-up, then F1 and the hot-swap resistors R22, R23 and R24; firmware's 4.70 A only on a board A that carries H3; the records re-issued;
the bench, where V-A07 decides R11. The items under U-01's approach (II) (R-105, R-106, R-110) wait on the owner's approval.

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
  more into the sealed case: 1.25 K on the inside air at T-H1's 1.666 W/K floor, on top of L4-E10's conditioned corner (U-02).
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
- **Every mandatory function is intended to be delivered, subject to the open conditions named here** (D-01, D-06, U-01 to
  U-04 and the CONDITIONAL rows): battery and solar both feed the kit; the store is inside the case; HF and the tablet are kept
  (the tablet's charge is optional and reduces endurance); the vehicle input runs the kit and charges the pack across 9 to 36 V
  with a working pack (section 3; without one, U-04); PS-ALLTX runs under D-11's floors; both outlets deliver their contracts
  within their protection. No service is reduced to narrow the gap. Software tests establish the record's own behaviour, not
  these properties.

## 11. What stays PENDING, CONDITIONAL or open

- **PENDING:** none. L4-E7R is accepted (check 4 at `91e9a4b5`); IF-01, IF-02, LH-02, R-21, R-92 and R-98 carry its figures.
- **Unresolved choices (no owner closes them):** U-01 (FEA-008's cell, with the owner's two items), U-02 (MESHSAT-1478), U-03
  (O-1), U-04 (source-only and dead-pack operation).
- **Open material defects:** D-06 (the vehicle entry's interconnect in F1's long-time band) and D-09 (the hot swap's fault time
  against the start at C5's printed corners).
- **CONDITIONAL:** the backstop's static bound on G_CM and U18's VIN+ bias, the 0.1 s interpretation (layer 8), C-7, C-3, C-5,
  V-A07, the bank's lifetime and cold envelope, PWR-F12, U18's trip row, D10's cold breakdown (a typical coefficient), Q7's
  hot short on board E's copper and TI's power law past 10 ms, the breaker's event (R-118), F1's let-through (R-115), R227's
  pulse rating and capacitance envelope (R-101), L10's L(I) at temperature (R-120, R-121), L4-E7R's loop on typical rows, the
  bulk's temperature under CS101 and the bank's pulse capability (R-122, R-101).
- **Recorded residuals outside every requirement:** A-N1 (the VIN_RAW clamps' 64.5 V against U2's 60 V at their rated pulse; no
  surge level is ruled, D-16) and the capability scenario on Q1, the LM74700-Q1 and U17's POE_VIN (part A). S-111 (VBUS20's
  single faults) is an engineering decision still open (R-48), with no exemption claimed; the short at DC_P and the weak-source
  band behind F1 are traced in section 5 (F1's let-through R-115, D-06), not exempted.
- **Not claimed:** nothing is verified, built or measured; every row is a desk reading of documents and records.
