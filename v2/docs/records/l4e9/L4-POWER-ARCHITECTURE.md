# L4-E9: the connected power architecture and Layer 4's closure gate for it (MESHSAT-1357, 1 October 2026)

**Prototype design, desk arithmetic.** Nothing is bought, built, powered or measured, and no board of this set has a layout.
This page edits no generator, registry record, Layer 3 file, `pcb_interfaces.yaml`, `HW-FW-CONTRACT.md` or other record; its
circuit change is a draft (`apply_gen_sch_e_q1.py`) and its interface changes are drafts for Layer 5 (`LAYER5-HANDOVER.md`).
Every figure below is printed by `l4e9_power_path.py` into `l4e9_power_path.out` ("out N" is its section), which reads each
figure from a generator, a committed netlist, a record's committed output or a maker's document, each pinned by sha256, and
never retypes a figure another record computed. Classes: MAKER, NETLIST, MODELED, INFERRED, CONDITIONAL (a calculated result
on an unwarranted assumption or an open measurement), ASSUMPTION, PENDING, and SESSION for a choice this record takes.

**Inputs.** The Layer 4 records on main: `../l4e/` (the energy architecture, A1 against A2, the findings A-1, A-2, B-1 to B-5,
C-1 to C-9, R138, O-1, O-2; the review L4-R01 to L4-R04), `../l4e4/` (current limits, PROVISIONAL), `../l4e5/` (source control,
H3), `../l4e6/` (fault handling), `../l4e7/` (the solar stage's settings and the qualification of its 100 W bound), `../r11dep/`,
`../s120/`, the power budget and load trace, `HW-FW-CONTRACT.md`, `pcb_interfaces.yaml`, `DECISION-31-PROTECTION-TOPOLOGY.md`.
**L4-E8** (the VBUS20 bank) is read from `fnd/l4e8` at `3c8f7a1f`, accepted by the coordinator's check 3 with its figures as at
`a282c8b7`. **L4-E7R** (the 100 W control decision on board E and the solar entry's surge protection) is in its fix round on
`fnd/l4e7`: every row that waits on it reads **PENDING**.

**The owner's frame** (the Current owner brief, `OWNER-INSTRUCTION-2026-09-30.md`; his instruction of 1 October 2026): battery
and solar both required; the store inside the Peli 1450, no external battery; HF and the tablet kept; D-06's single 4S3P stands;
48 to 72 hours an objective, tablet charging optional consumption; A2, the lid pack, the 16.340 V hold and P-03's 200 W stay
proposals. Layer 4 selects the power architecture and establishes its feasibility; Layer 5 writes the interfaces it creates.

## In short

- **Selected: A1**, D-06's one 4S3P pack inside the case, fed by two sources ORed onto one raw bus (the panel through board E's
  LT8705A stage, the vehicle or shore supply through its ideal diode and hot swap), converted once to a regulated 20 V charge bus
  by board A's LM5176 front end and once more by the BQ25731 charger onto the system node VBAT, from which every load converter
  and both outlets run. **A2** (base 4S6P plus a separately protected lid 4S9P) stays a proposal to change D-06.
- **Fourteen interfaces reconciled** (out 4): 4 MEET, 8 are CONDITIONAL, 2 are PENDING on L4-E7R. None reads NOT MET in the
  selected design. Five checks read NOT MET as drawn: four are defects the selected design resolves (C26 and C27 by L4-E5's
  re-rate; Q1 and U17 by this record; F1 by this record's specification) and one is the recorded residual A-N1.
- **New here, one stage's resolution overloading another:** L4-E5 raises the tracker's ceiling to 30.15 V, and the tracker
  back-feeds the vehicle entry's DC_P through the hot swap's body diode. A reversed vehicle input (REQ-015) then puts **66.15 V**
  across the entry's ideal-diode FET Q1, a 60 V part (51.56 V with the drawn ceiling). **Resolved (SESSION):** Q1 becomes the
  100 V CSD19532Q5B Q7 already carries, drafted in `apply_gen_sch_e_q1.py` (out 4 IF-04, out 7).
- **Protection on the other entries:** the vehicle entry's F1 has a 32 V rating (Littelfuse 297) on a line the hot swap admits to
  42.49 V: a fuse with a DC rating of at least 42.49 V and an interrupting rating of at least 561 A (the kit's own cable at -20 C)
  is specified, no such part's sheet is held (E-F2). The PoE monitor U17 sits at 54 V against the INA226's 40 V: resolved by a
  20 mOhm shunt in the stage's 20 V input, specified and not drafted (HF-F02). E-F1's input capacitor is drafted (d8dec31).
- **The closure gate (section 7): NOT CLOSED.** Criteria 3 and 4 PASS; 1, 2 and 5 are CONDITIONAL. The exact constraints:
  L4-E7R's control decision and solar entry protection (PENDING); F1's part (no held sheet); U17's change (not drafted); the 100 W
  bound's five unprinted values; PWR-F12 and FEA-008. None of them can overturn the selected architecture.
- **Endurance (section 10):** A1 runs 2.52 h on battery at +20 C and first interrupts at hour 6 or 2 on the candidate panel; it
  needs +1361.5 / +2094.1 Wh more storage for 48 / 72 h. DR-01 stands; every mandatory function is delivered, and no service
  is reduced to narrow the gap.

## 1. The selected architecture as one connected design

```
SOURCES
 panel (REQ-016: Voc <= 25 V at -20 C, <= 100 W into the stage)          vehicle or shore 9 to 36 V (REQ-015)
   | J_SOLAR (VH), F2 10 A, D4 SMCJ28A [L4-E7R]                             | J_DCIN (VH), F1 [rating: E-F2], D10 SMCJ40CA
   | PV_P -> R59 15 mOhm -> TRK_VIN                       board E          | U3/Q1 LM74700 ideal diode [Q1 100 V: L4-E9]
   v                                                                       | DC_P, D1 SMCJ40A, R19 10 mOhm
 U5 LT8705AI buck-boost: hold 17.593 V (16.970..18.221),                   | U6/Q7 LM5069 hot swap: UVLO 9 V, OVLO 37.78..42.49 V,
   input limit 3.4713 A (96.25 W CONDITIONAL), [100 W backstop: L4-E7R]    |   limit 4.85..6.15 A, timer 3.13..8.16 ms
   TRK_OUT ceiling 28.28..30.15 V (R10 232 k, L4-E5)                       | L2 SRF1260 choke
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
 PACK (D-06, 4S3P 35E):          LOAD CONVERTERS               OUTLETS                        PA AND HF
 R17 5 mOhm, A F1 25 A, pack     slot rails, device rail,      USB-C: U19 LM5176 5/9/15 V,    +13V8_PA (U13) to J_PA, keyed
 pins (4 x 9 A), E F3 25 A,      logic, monitor (U21), heater  Q27, R138 5 mOhm, U18 OCP       at most 60 s (D-11)
 XT60, board P: F1 25 A, F2      (U22), board E always-on on   3.793..4.576 A (tablet         +12V_HF (U15) to the QMX
 SCF9550 30 A, BQ4050, BQ7720700 CELL_F                        charge optional)              
 charge <= 3.0 A                 PS-IDLE-SPEC 42.8 W           PoE: U16 boost +54V_POE        both outlets dropped by
                                 PS-ALLTX 203.8 / 272.0 W      0.6 A; U17 on its VBAT shunt   OUTLET_OK while the PA keys
```

There is **no separate shore entry** (shore is J_DCIN) and **no USB-C input**: the USB-C port is a power-only outlet (D-12).

## 2. The interfaces (out 4: every figure, check and source)

Modes: PS-IDLE-SPEC (42.8 W at the pack terminals), PS-ALLTX (203.8 W plan, 272.0 W high) and the PA keyed alone at 113 W
(162.3 W), charging at the window (100 W into the stage, 86.5 W at VBUS20 on the declared efficiencies), and the tablet outlet
(45 W on PS-TYP, 112.3 W plan). Thermal basis everywhere: the worst inside air, 62.1 C lid closed (59.2 C lid open).

| Row | Interface | Voltage, both sides | Current asked / available (modes) | Losses | Protection, each side | Settled by | Status (class) |
|---|---|---|---|---|---|---|---|
| IF-01 | panel to the solar entry | at most 25 V at -20 C (candidate 24.05 V nominal) / D4 standoff 28 V | hot short circuit 6.42 A / F2 10 A; J_SOLAR's VH with AWG 18 has no stated rating (7 A shrouded) | the lead about 0.0465 Ohm | none / F2, D4 [L4-E7R] | l4e O-1, l4e7, L4-E7R | PENDING (PENDING) |
| IF-02 | PV_P through U5 to TRK_OUT | hold 16.970 / 17.593 / 18.221 V, at most 25 V / ceiling 28.28 to 30.15 V | limit 3.4713 A; the 25 V corner 96.25 W (99.90 W, every conservative assumption) against 100 W; 93 W out at the window | stage 0.93 DECLARED (C-8) | input limit, fault comparator, [backstop: L4-E7R] / U4 | l4e7, l4e5, L4-E7R | PENDING (PENDING) |
| IF-03 | TRK_OUT through U4/Q2 to VIN_RAW | at most 30.15 V / VIN_RAW to 42.49 V with TRK_OUT at 0 | 4.22 A at H3's lowest settle at the window / declared 10.33 A | Q2 | the stage / U4 blocks | l4e5, this record | MEETS (MAKER/NETLIST), with C26 and C27 re-rated (as drawn 121 % of 25 V) |
| IF-04 | vehicle and shore into DC_F and DC_P | 9 to 36 V, reversed to -36 V, OVLO max 42.49 V / D10 breakdown 44.4 V either way | entry limit 4.85 to 6.15 A / F1 10 A; J_DCIN's VH with AWG 18 no stated rating | about 0.2 V in series | supply's own / F1, D10, U3/Q1, D1, the LM5069 | d8dec31, this record, l4e5 | CONDITIONAL (ASSUMPTION): F1's part, the VH rating |
| IF-05 | DC_P through the hot swap and L2 to VIN_RAW | D1 clamp 64.5 V / LM5069 VIN 100 V, Q7 100 V | 6.15 A / L2 6.89 A Irms | R19 0.38 W | D1 / D2 | gen_sch_e.py, l4e5 | MEETS (MAKER/NETLIST) |
| IF-06 | VIN_RAW over the dock to board A | 8.466 V (HIZ, solar) to 30.15 V; vehicle 9 to 36 V; at most 42.49 V / U2 60 V | in service at most 4.629 A (9 V vehicle); fault at most 11.65 A (13.315 A at 7 mOhm) / declared 14.10 A, four 9 A pins | the dock's contacts | the entry, D2 / D2, U34 | l4e5, l4e6, IF-AE-DOCK | MEETS (INFERRED); A-N1 a recorded residual |
| IF-07 | VIN_RAW through U2 to VBUS20 | 8.466 to 42.49 V / 19.08 to 20.96 V, bound 23.40 V | 4.964 A asked through R11 / 4.986 A stacked minimum at 62.1 C with C-1's taps; highest permitted 7.262 A; R12 peak limit 8.06 A over a 6.50 A service peak | front end 0.93 DECLARED | U34, D2 / R11, R12, no hiccup, OVP; no clamp on VBUS20 (S-111) | l4e4, l4e5, l4e6, r11dep, s120 | CONDITIONAL (CONDITIONAL): C-7, V-A07, C-5, C-3 |
| IF-08 | VBUS20's bank | 23.40 V bound / the cans' 35 V | every can at most 2.4096 A against 2.7745 A (8 mOhm); 2.7661 against 2.7709 A at 7 mOhm | ballasts at most 2.09 W | R12, R11 / the ballasts | l4e8 (accepted) | CONDITIONAL (CONDITIONAL): lifetime, the cold envelope, the 7 mOhm fallback |
| IF-09 | VBUS20 through U3 to VBAT | 19.08 to 20.96 V / U3 32 V absolute; VBAT 10.0 to 16.884 V; SYSOVP 19.0 to 20.0 V | the window needs 4.517 A / U3 minimum 4.537 A (C-7); 84.5 to 99.6 W at VBAT; charge at most 3.0 A | U3 0.9733 INFERRED | H3 line, IIN_HOST, VINDPM, ACOV / BATOVP 17.64 V, SYSOVP, the gauge's OCC 5 A | l4e4, l4e5, s120, FW-A02 | CONDITIONAL (CONDITIONAL): C-7 |
| IF-10 | VBAT and the pack | 10.0 to 16.884 V / D1 standoff 18 V, the pack FETs 30 V | PS-IDLE-SPEC 2.5 to 4.3 A; the PA keyed at 113 W 16.6 A at 10.0 V; PS-ALLTX's 18 A at an 11.48 V stack / declared 10 A continuous, 18 A peak; OCD1 20 A for 2 s; XT60 30 A | 22.5 mOhm path | D1, A F1 / BQ4050, BQ7720700, F1, F2 | pcb_pack_protection.yaml, POWER-THERMAL 7, FEA-004, FEA-008 | CONDITIONAL (CONDITIONAL): PWR-F12, FEA-008 |
| IF-11 | VBAT to the load converters | 10.0 to 16.884 V / the converters assumed to run to 10.0 V | PS-IDLE-SPEC 33.1 / 42.8 / 82.8 W; PS-ALLTX 168.9 / 203.8 / 272.0 W; 8.4 W undocumented | the converters' floors | eFuses (TPS2596 21 V against SYSOVP 20.0 V) / each converter | pwr_budget, load_trace, POWER-THERMAL | CONDITIONAL (ASSUMPTION) |
| IF-12 | VBAT to the USB-C outlet | 5 / 9 / 15 V contracts | 3 A each / trip 3.793 to 4.576 A; receptacle 5 A; J_USBC_OUT unrated | U19 0.93 | OUTLET_OK, C2 / U18 OCP and OVP | l4e4 | CONDITIONAL (ASSUMPTION): VI(TRIP)'s row, the header |
| IF-13 | VBAT to the PoE stage and U17 | 54 V / U17 at most 20.0 V on its VBAT-side shunt (as drawn 54 V against 40 V) | 0.6 A; 3.682 A at the stage's input at 10.0 V / 73.64 mV against 81.92 mV | U16 0.88 | OUTLET_OK / U16, TPS23861 | HF-F02, this record | MEETS (INFERRED), the change specified, not drafted |
| IF-14 | VBAT to the PA rail | 13.8 V | declared 5 / 6 A, the drain 5.4 to 8.2 A uncharacterised / the stage's loop 7.2 to 9.5 A; the pack 16.6 A at 10.0 V | U13 0.93 | the K rules, OUTLET_OK / the stage | POWER-THERMAL 7.2, FEA-004 | CONDITIONAL (ASSUMPTION) |

**What the rows show about the stages together (no stage's resolution overloads another, with this record's changes):**
- H3 holds the front end's input under the vehicle entry's minimum limit at every voltage (4.629 A at 9 V against 4.85 A; it
  reaches the entry's 4.80 A basis only if the front end's 9 V efficiency falls to 0.897, C-8).
- R11 8 mOhm (L4-E4) carries U3's 4.964 A with +0.023 A at 62.1 C with C-1's full taps; H3's pin path (5.095 A on a stiff
  26.50 to 27.24 V source) holds on R11 alone and needs V-A07 for the full taps (else 7 mOhm, which changes nothing else).
- R12 12 mOhm (L4-E6) bounds L1 and the FETs at the highest permitted current, 1.56 A over H3's 6.50 A service peak.
- The bank (L4-E8) holds every can at the same highest permitted current, and goes in only with R12.
- The board A declarations need no raise at R11 8 mOhm: VBUS20 and FE_OUT's 8.0 A peak covers 7.262 A and VIN_RAW's 14.10 A
  covers the front end's 11.65 A fault; they rise (VBUS20 and FE_OUT to 8.300 A) only if V-A07 sends R11 to 7 mOhm (B-3).
- **The one overload found:** L4-E5's raised tracker ceiling on Q1 in reverse (above). The rest of the raised ceiling's reach:
  C26 and C27 (121 %, re-rated, R-14), C24 and C25 (86 %, the derating gate), Q2 and U4 (blocking 42.49 V against 60 and 75 V).

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

- **Cold start on the pack:** MAIN raises the panel controller (DEV_EN on by R42), which runs FW-C01's order: PI_KILL low,
  ZEROIZE read, the expanders' outputs before their configuration, the charger (FW-A01 first), then SLOT_EN one at a time; each
  stage soft-starts on VBAT; the pack's precharge pin J_PRE1 (10 Ohm, 2 W) mates first.
- **A source arriving:** the LM5069 starts at 9 V with its timer bounding the inrush; U3 is in HIZ below 8.466 V and out of it
  above 8.713 V, and the H3 line bounds its input from its first switching cycle with no host. The panel: the stage's own UVLO and
  soft start, then the hold at 17.593 V.
- **A source leaving:** VBAT is the system node with no battery FET, so the pack carries the loads without a break; U3 resets
  IIN_HOST to 3.25 A and firmware writes 4.70 A again (FW-A16 restated); VIN_RAW falls through the restart guard (8.31 V at its
  highest) and the front end stops; the bank bleeds in 0.455 to 1.494 s (L4-E8).
- **A dead pack** (the gauge's CUV opened the discharge FET): a source runs the loads through U3 at the pack's voltage while the
  charge clamps at 384 mA below VSYS_MIN; board E's always-on comes up on CELL_F from VBAT. **CONDITIONAL** on TI's answer to
  Q-TI-3 and O-CHG-2 (`CHARGER-STATE-SEQUENCE.md`), bench R-85.

## 5. Faults, traced across the stages (out 7)

| Fault | What acts, stage by stage | Bound, and its class |
|---|---|---|
| **Source short**, the vehicle lead shorted while the tracker holds the bus | U3/Q1 blocks the reverse current at DC_F; DC_P stays back-fed from VIN_RAW | Q1 stands off DC_P, at most 30.15 V (INFERRED) |
| **Source short**, the panel lead | U4/Q2 blocks VIN_RAW into TRK_OUT; U5's input falls through its UVLO | PENDING: L4-E7R (D4, the entry) |
| **Output short**, VBUS20 | R12 holds the front end's output at 4.57 A at 9 V, R11 at 7.262 A above 14 V; VIN_RAW carries at most 11.65 A; the vehicle entry limits at 4.85 to 6.15 A and opens after 3.13 to 8.16 ms (then retries); the stage limits at 3.4713 A; U34 cycles the front end | L1 at most 12.60 A, FETs at most 130 C on the assumed 50 C/W (CONDITIONAL, C-3, C-5) |
| **Output short**, VBAT | the gauge's SCD (60 A in 0.2 ms), OCD2, the 25 A blades, F2, against 240 to 480 A prospective; U3 at its input limit | MAKER thresholds (pcb_pack_protection.yaml) |
| **Output short**, an outlet | USB-C: U18's OCP at 3.793 to 4.576 A in 15 us, U19's own limit; PoE: U16's limit and board B's port limit; PA: U13's loop; monitor and heater: their eFuses | CONDITIONAL (VI(TRIP)'s row, bench (a)) |
| **Reverse**, the vehicle input at -36 V (REQ-015) | D10 (two-way, 44.4 V breakdown) does not conduct; U3/Q1 block; DC_P back-fed from the raised ceiling | **Q1 at 66.15 V: NOT MET on the drawn 60 V part, MEETS on the CSD19532Q5B (100 V)**; the LM74700-Q1 under its 70 V recommended, 75 V absolute (INFERRED) |
| **Reverse**, the panel | D4 forward at the panel's short circuit (E-N1) | PENDING: L4-E7R |
| **Surge, TRN-001** | The ruled level is IEC 61000-4-2 level 4, 8 kV contact and 15 kV air (decision 34); no surge level is ruled (D-16, CHO-003). Vehicle entry: D10 at the entry; E-F1's 1 uF holds a negative discharge to 2.25 V at 15 kV; VIN_RAW's 20 uF on board A to 0.11 V. Solar entry: PENDING (L4-E7R derives REQ-016's surge disturbance there) | INFERRED (DECISION-31); A-N1 a recorded residual |
| **A short behind F1** (a failed D10, D1, the input capacitor or Q1) | F1 alone clears it, at up to the OVLO maximum 42.49 V | the kit's cable and lead give 0.0758 Ohm at -20 C (copper alone), so at most 560.7 A; the 297 MINI is rated 32 V DC: **NOT MET as drawn**, the specification R-18 |
| **Pack fault**, the charge FET opening mid-charge (a designed event, REQ-046) | U3's voltage loop holds VBAT at 16.884 V at most; BATOVP stops switching at 17.64 V, SYSOVP at 20.0 V; L2's 0.1341 mJ goes into VBAT's 34 capacitors (248.2 uF nominal) | 20.135 V at a fifth of the nominal capacitance (ASSUMPTION), under the TPS2596's 21 V; 6.54 uF, 2.64 % of the nominal, would do |
| **Pack fault**, the discharge FET opening under load | on battery the kit stops (the hot stop REQ-077 acts first on temperature); with a source U3 carries up to 84.5 to 99.6 W | as section 3 |
| **Pack fault**, a cell or the block | BQ7720700's second level drives F2 (the chemical fuse); F1 25 A | MAKER thresholds |
| **Controller fault**, the host crashed | U3's watchdog falls back to 256 mA after 175 s (FW-A03); the H3 line is hardware and needs no host; the gauge's HWD stops charging in 10 s (FW-E01) | the source bound holds with no firmware |
| **Controller fault**, U2 (Q2 short, FB open) | VBUS20 follows VIN_RAW (35.2 V at 36 V in); U3's 32 V passed; no clamp on VBUS20 | outside every requirement (ASM-001); S-111's residual and options, R-48 |
| **Controller fault**, U5 | PENDING: L4-E7R | PENDING |

## 6. Decisions this record takes (SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026 that engineering decisions are the session's)

1. **Q1 to the CSD19532Q5B (100 V, C473333)**, on Q7's PPAK land. *Why:* L4-E5's raised ceiling makes the reversed vehicle input
   of REQ-015's acceptance put 66.15 V across Q1 (the back-feed diode's drop taken as zero), over the BSC039N06NS's 60 V; the
   part Q7 already carries stands off 100 V and keeps the LM74700-Q1 under its 70 V recommended. Keeping the drawn ceiling instead
   would undo L4-E5's H3 (the window needs the line's minimum at 27.98 V). *Draft:* `apply_gen_sch_e_q1.py`, release-guarded,
   composes with d8dec31's input capacitor in either order and with L4-E7's three drafts (`test_l4e9.py`). *Reversed by:* a
   measured back-feed that keeps DC_P under 24 V, or a blocking element on the back-feed path.
2. **U17's sense moved to a 20 mOhm shunt in the PoE stage's VBAT input** (HF-F02). *Why:* the INA226's inputs are 40 V absolute
   and the rail is 54 V; on the input side its common mode is at most SYSOVP's 20.0 V and the stage's 3.682 A input at a 10.0 V
   stack drops 73.64 mV against its 81.92 mV full scale; R71 stays the LM5176's own ISNS shunt, so the stage's limit is unchanged.
   *Not drafted:* a new resistor, two re-routed pins and a calibration (R-06, R-27). *Reversed by:* the generator owner choosing
   a low-side shunt in the rail's return or a part with a maker's rating at 54 V.
3. **F1's specification** (E-F2): a DC voltage rating of at least 42.49 V (the LM5069's OVLO maximum, the highest steady input
   that can reach a short behind F1) and an interrupting rating of at least 561 A at that voltage (the kit's own 2 m cable of
   1.0 mm2 a way and its 500 mm AWG 18 lead, copper alone at -20 C: a stiff source's upper bound). *No part is selected:* no
   maker's sheet for a MINI blade above 32 V is held; Layer 6 selects one (R-18). *Reversed by:* a cable or source impedance
   the requirement states.
4. **B-3 at R11 8 mOhm needs no declaration raised on board A** (R-10): VBUS20 and FE_OUT's 8.0 A peak covers 7.262 A and
   VIN_RAW's 14.10 A covers 11.65 A. *Reversed by:* V-A07 sending R11 to 7 mOhm (VBUS20 and FE_OUT's peak to 8.300 A).
5. **The 9 V envelope is stated, not corrected:** a 9 V vehicle runs the profile with the pack supplementing (section 3). *Why:*
   the entry's own limit bounds 9 V at 39.5 W at VBAT whatever the control; H3 keeps the entry under that limit. It changes no
   requirement and is handed to Layer 5 (LH-01).

## 7. The closure gate

The gate's rule, held by the script (out 9) and by `test_l4e9.py`: a criterion reads PASS only on interface rows that read
MEETS, never on an ASSUMPTION, CONDITIONAL or PENDING row.

| Criterion | Evidence | Verdict | The exact constraint (if not PASS) | Could it overturn the architecture? |
|---|---|---|---|---|
| 1. One architecture selected; its mandatory functions have a defensible feasibility basis | A1 under D-06 (section 1); rows IF-02, IF-04, IF-07, IF-09, IF-10, IF-12, IF-13: REQ-014 (the pack), REQ-015 (IF-04 to IF-06), REQ-016 (IF-01, IF-02), REQ-017 (IF-12, IF-13), REQ-018 (IF-10, IF-14), REQ-045 (section 5), REQ-046 and REQ-077 (IF-10), REQ-075 (IF-09) | CONDITIONAL | REQ-016: the stage's 100 W bound is a calculated result CONDITIONAL on EA2, A7, LINE, TCR and TJ (L4-E7, 99.90 W with all of them conservative) and its control decision is PENDING (L4-E7R); REQ-018: the chain at 18 A for 60 s with F2 near +60 C (PWR-F12); REQ-046: the cells' thermal design with the pack fitted (FEA-008); REQ-017: U18's VI(TRIP) row (bench (a)) and J_USBC_OUT's rating | No. Each resolves by a value, a part, a maker's answer or a thermal design on the same topology: A1's one pack, the two ORed sources, the two conversions, the system node |
| 2. Material power-path defects have engineering resolutions and bounded supporting calculations | rows IF-01, IF-04, IF-13; the as-drawn defects of out 4 and their resolutions: Q1 in reverse (SESSION, drafted), C26/C27 (L4-E5, R-14), E-F1 (drafted), U17 (SESSION, specified), F1 (specified) | CONDITIONAL | (a) the solar entry's surge protection and the 100 W control: PENDING on L4-E7R; (b) F1: a fuse with a DC rating of at least 42.49 V and an interrupting rating of at least 561 A, no maker's sheet held (E-F2, R-18); (c) U17: the 20 mOhm VBAT-side sense is specified, not drafted (R-06) | No. Each is a part or a protection element at an entry or an outlet; none moves a block or a source |
| 3. Remaining assumptions are explicit, with their impact and verification method | section 8's register A-01 to A-16 | PASS | | |
| 4. Downstream implementation changes, layout constraints and tests have named owners and acceptance criteria | `DOWNSTREAM-REGISTER.md`: 82 items, each with one owner and an acceptance; the release order (L4-E6's R12 before L4-E8's ballasts; L4-E4's release record first); `LAYER5-HANDOVER.md` LH-01 to LH-09 | PASS | | |
| 5. No unresolved uncertainty could overturn the selected architecture while described merely as routine later testing | rows IF-01, IF-02; section 8's impact column | CONDITIONAL | L4-E7R is PENDING; and the mandatory solar function's feasibility depends on a panel with a supported maximum open circuit at or below 25 V over -20 to +40 C (O-1, R-35). That dependency is named here, not left to routine testing; the solar function stays CONDITIONAL until a source is pinned | No for the topology: O-1 decides which panel, not whether the stage. A bench reading changes a value (RIMON_IN, R11's 8 or 7 mOhm, a compensation), not a block |

**Layer 4's power architecture closes: NO** (criteria 1, 2 and 5). **What closure needs, exactly:**
1. L4-E7R accepted (its control decision and the solar entry's protection), its rows rerun here (they replace the PENDING rows).
2. F1: a held maker's sheet for a fuse with a DC rating of at least 42.49 V and an interrupting rating of at least 561 A that the
   3568 holder takes, or a holder change. *Viable alternatives:* the maker's 58 V MINI class if its sheet is obtained; an ATO or
   MAXI class part with a 58 V rating and its holder (Layer 7 land); a fuse at the vehicle cable's plug with the entry's F1 kept
   only behind the hot swap (an architecture-neutral relocation, then re-traced here).
3. U17's change drafted for gen_sch_a.py (R-06). *Alternative:* a low-side shunt in the 54 V rail's return.
4. For criteria 1 and 5 the CONDITIONAL inputs need their named evidence, none of which moves the architecture: the five
   unprinted LT8705A and HoJLR values (R-33, R-70), PWR-F12 (R-46, R-83), FEA-008 (R-47), O-1 (R-35). The coordinator decides
   whether a CONDITIONAL criterion 1 with these named and owned is acceptable for Layer 4's closure; this record does not.

## 8. The assumptions register (criterion 3)

| ID | Assumption | Where it enters | Impact if wrong | Verification method |
|---|---|---|---|---|
| A-01 | The three efficiencies: stage 0.93, front end 0.93, pack charge 0.95 (C-8) | IF-02, IF-07, every energy figure | moves the gap, not a verdict (A2 +131.4 to +344.0 Wh at 48 h); the 9 V envelope needs the front end at least 0.897 | R-72, measured at bring-up |
| A-02 | U3's input-current minimum: the setting less an INFERRED 0.1 A (C-7) | IF-09 | the window's 4.517 A needs 4.537 A; below it the 100 W hour gives a little less | R-32 (TI), R-71 (bench) |
| A-03 | Board A's FET thermal resistance at the maker's 50 C/W (C-3) | IF-07 | Q2 at 130 C, 20 K under 150 C; a worse board raises it | R-42 (laid copper), R-63 (bench) |
| A-04 | L1's Isat at 85 C at least 14.00 A (C-5); L4-E8's restart ring at 16.13 A taken at constant inductance | IF-07, IF-08 | B-1 at temperature; a lower Isat needs R12 larger (a lower peak limit, against the 1.56 A service margin) or another L1; the ring's peak re-derived on the measured L(I) | R-31 (Coilcraft), R-65 (sweep through 16.2 A) |
| A-05 | The five unprinted values of the 100 W bound (EA2, A7, LINE, TCR below +25 C, U5's junction) | IF-02 | 99.90 W with all conservative, 0.10 W under 100 W; an adverse reading changes RIMON_IN | R-33 (makers), R-69 and R-70 (bench) |
| A-06 | H3's pin error at R16's 10 mOhm within +-0.2 A, and within 0.071 A in the 26.50 to 27.24 V band | IF-07 | R11 7 mOhm instead of 8 mOhm (R12, the bank and Cc2 unchanged) | R-75 (V-A07) |
| A-07 | The ILIM_HIZ network's tolerance +-0.5 % and the HIZ comparator's spread | IF-06, IF-09 | moves the knee's thresholds inside the guard's 0.156 V margin | R-03's drawn values, R-77 (V-A09) |
| A-08 | The cans' cold ESR envelope (300 mOhm at -40 C after endurance taken to -20 C), C190 and C191's regions, VIN and VBAT sampled | IF-08 | the 7 mOhm fallback's 0.005 A margin; the loop at the cold end | R-68 (7b.8) |
| A-09 | The cans' lifetime on their measured rise | IF-08 | service life, not the current bound | R-68 item 4 |
| A-10 | The back-feed diode's drop taken as zero (an upper bound on Q1's reverse stress) | IF-04 | none: a drop only lowers 66.15 V | R-80 |
| A-11 | The VH contacts at AWG 18 on the standard header (no stated rating) | IF-01, IF-04 | the contact margin at 6.15 and 6.42 A is unstated | R-29 (harness change) |
| A-12 | Copper at 0.01724 Ohm mm2/m and 0.00393 /K, 18 AWG at 0.823 mm2, the source's own resistance taken as zero | F1's specification | a lower prospective current, never higher | the part's selection (R-18) |
| A-13 | A fifth of VBAT's nominal capacitance kept under bias | the pack-open bound | 2.64 % of the nominal suffices, so none | R-85 region (bench, VBAT at a pack opening) |
| A-14 | Every load converter runs to the 10.0 V stack (SHORTLIST.md 2) | IF-11, the usable energy | the usable energy and the battery-only hours | R-49 |
| A-15 | PS-IDLE-SPEC's 8.4 W with no document; the PA's drain current 5.4 to 8.2 A (F-PR-02) | IF-11, IF-14 | the profile's load and endurance; the PA rail's current | R-82, PWR-F15 and TEST-PLAN |
| A-16 | The candidate panel's nominal sheet values (source compliance INCONCLUSIVE, O-1), SC-37's mean day | IF-01, the endurance | the solar energy (350.0 Wh a day at the nominal hold) | R-35, R-52 |

## 9. The downstream register and the release order (criterion 4)

`DOWNSTREAM-REGISTER.md` holds 82 items, each with one owner, an acceptance, a state and a step in the release order (out 10):
Layer 4 coordinator 6, Layer 5 interfaces 2, Layer 6 components 8, Layer 7 mechanical 1, Layer 8 board A generator owner 11,
Layer 8 board E generator owner 9, Layer 9 pre-layout analysis 15, prototype bench 26, firmware owner 4. By kind: 27
implementation changes (13 drafted, 7 missing a draft, 1 PENDING, 6 owed as work), 9 layout constraints, 26 tests, 16 pieces of
evidence, 4 release records.

**Every draft of L4-E4 to L4-E8 is in it** (R-01, R-02, R-04, R-05, R-07, R-09, R-12, R-19, R-20, R-23), with d8dec31's E-F1
draft (R-16) and this record's Q1 draft (R-17). **The missing drafts:** U3's ILIM_HIZ network (R-03, L4-E5), R10, C26/C27 and
TRK_OUT's declaration (R-13 to R-15, L4-E5), U17's sense (R-06), the 45 mOhm lcsc line (R-08), board A's declaration texts (R-10).

**The release order** (the register's own section): release records first (L4-E4's names accepted checks of L4-E4 to L4-E6 and
L4-E8); the missing drafts; board A in one round with **R12 and the ILIM_HIZ network first, R11 after them, the ballasts and Cc2
after R12**, R138 independent; board E in one round with **Q1 and E-F1's capacitor no later than R10**, R10 and C26/C27 only with
board A's H3 line; firmware's 4.70 A only on a board A that carries H3; the records re-issued; the bench, where V-A07 decides R11.

## 10. The endurance statement (out 8; DR-01)

- **Battery only, A1 (the ruled pack):** 107.9 Wh usable at +20 C and 44.5 Wh at -10 C (aged to 80 %): **2.52 h and 1.04 h**,
  short of 48 h by 45.5 h and of 72 h by 69.5 h.
- **Solar-assisted, A1, on the candidate panel** (SunPower SPR-E-Flex-100 on its nominal sheet, source compliance
  INCONCLUSIVE; L4-E7's settings, 350.0 Wh a day into the stage; SC-37's mean September day): the first interruption at hour
  **6 or 2** (06 or 18 UTC starts); **1367.4 / 1368.1 Wh unserved at 48 h and 2103.9 / 2104.6 Wh at 72 h**; it would need
  **+1361.5 / +2094.1 Wh** more usable storage; the steady load it carries through either horizon is 8.0 W against the profile's
  42.8 W. On the 100 W screening stimulus (a conditional comparison): hour 13 or 2, +654.8 / +873.1 Wh.
- **What moves these figures:** H3 gives up at most 7.1 Wh a day on the candidate's trace; L4-E8's ballasts dissipate at most
  2.09 W at the bound's worst corner (0.0093 W at nominal parts, an operating-point term for REQ-072's owner, not to be counted
  twice); the three efficiencies (A-01). None changes a verdict.
- **The objective of 48 to 72 hours is unmet** by the selected architecture on every trace (DR-01). It is an objective (D-28),
  not a minimum, and it reopens no requirement.
- **What A2 would change, as a proposal for the owner** (it changes D-06; its mechanical fit and FEA-008's lid obligations stay
  open): battery only 12.71 h and 5.24 h; on the candidate panel the first interruption at hour 18 or 11 and +979.2 / +1719.7 Wh
  still needed; on the screening stimulus +278.8 / +515.8 Wh. A2 also misses 48 h.
- **Every mandatory function is still delivered:** battery and solar both feed the kit; the store is inside the case; HF and the
  tablet are kept (the tablet's charge is optional and reduces endurance); the vehicle input runs the kit and charges the pack
  across 9 to 36 V (section 3); PS-ALLTX runs under D-11's floors; both outlets deliver their contracts within their protection.
  No service is reduced to narrow the gap.

## 11. What stays PENDING, CONDITIONAL or open

- **PENDING on L4-E7R** (`fnd/l4e7`): IF-01's protection, IF-02's control decision, the panel's reverse, a U5 fault, LH-02 and
  LH-09, R-21 and R-92. The coordinator's message lands them; this record's rows are re-run then.
- **CONDITIONAL:** the 100 W bound (A-05), C-7, C-3, C-5, V-A07, the bank's lifetime and cold envelope, PWR-F12, FEA-008, the
  dead-pack start (Q-TI-3), U18's trip row.
- **Recorded residuals outside every requirement:** A-N1 (the VIN_RAW clamps' 64.5 V against U2's 60 V at their rated pulse; no
  surge level is ruled, D-16) and S-111 (VBUS20's single faults; ASM-001), each with its options and an owner (R-48).
- **Not claimed:** nothing is verified, built or measured; every row is a desk reading of documents and records.
