# L4-E11: source-only and dead-pack operation (U-04), the vehicle-entry interconnect (D-06) and the hot swap's fault timer (D-09) (MESHSAT-1357, 2 October 2026)

**Prototype design, desk arithmetic.** Nothing is bought, built, powered or measured, and no board of this set has a layout.
This page edits no generator, registry record, interface, Layer 3 file or other record. Its circuit changes are three
release-guarded drafts (`apply_gen_sch_e_entry.py`, `apply_gen_sch_a_guard.py`, and `apply_gen_sch_e_timer.py` as the
alternative while the LM5069 stays) and one specification (the corrected knee, section 3f); its interface and firmware texts are
drafts for Layer 5 (section 7a). Every figure is printed by `l4e11_power.py` into `l4e11_power.out` ("out N" is its section),
which reads each figure from a generator, a committed netlist, a record's committed output, a filed catalogue reading or a
maker's document, each pinned by sha256; L4-E9's output and its hot-swap draft are read from its commit `3c09b3da` and never
retyped. Classes: MAKER, CATALOGUE, NETLIST, REQUIREMENT, RECORD, INFERRED, CONDITIONAL, ASSUMPTION, and SESSION for a choice
this record takes under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026 that engineering
decisions are the session's.

**The task.** U-04 and D-06 were left open by L4-E9 (`L4-POWER-ARCHITECTURE.md` section 7, fix round at `71486686`); D-09 was
found by L4-E9's final round (`3c09b3da`) and added to this task by the coordinator on 2 October 2026. **The fix round** (2
October 2026) answers the collaborator's focused check (`checks/astra-check-l4e11-1.md`, NOT YET, blockers B1 to B5 and three
minors): the first round's UVLO had its hysteresis on the wrong edge and ignored the LM5069's own power-on threshold (B1), its
holds conflated charge and discharge permission (B2), its source bounds left out the kit's own losses and named no functional
acceptance (B3), its weak-source band read the fuse's rows as points (B4), and it took typical charge currents as maxima (B5).

## In short

- **REQ-015 at 9 V at the plug: met with drafts.** The drawn entry cannot start from a 9.00 V plug; the selected replacement
  entry (section 3c, drafted), the corrected knee (section 3f, specified) and the restart guard (drafted) carry the functional
  warm-up of REQ-024, REQ-046 and REQ-077 at its plan figure: 30.37 W delivered at the least against 30.31 W (out 3g, 3h). Its hi
  corner (50.58 W) is not carried at 9 V (43.97 W at the most): rule R-c sheds there. CONDITIONAL on the front end's efficiency
  at 8.1 V (0.906 or more, C-8), the pin's error (L4-E5's INFERRED 0.2 A) and the bench rows of section 8.
- **B1, the entry.** By SNVS452G Equations 38 to 40 the drawn LM5069 turns on at 9.91 / 11.13 / 12.37 V (the withdrawn R21
  42.2k draft at 9.33 / 10.52 / 11.74 V). Worse, POREN (all functions enabled) is 9.0 V at most at the IC's own VIN, which sits
  behind the ideal diode: from a 9.00 V plug it is at most 8.987 V before any current flows, so no divider can make the LM5069
  start, and VIN is its sense reference, so it cannot be supplied from elsewhere. **SESSION: the TPS48110-Q1 replaces it**, with
  a CSD19536KTT pass FET, R19 4.5 mOhm and L2 SRF1260-1R0Y: on by 8.44 V, off by 7.95 V, a breaker at 6.364 to 7.136 A between
  the in-service maximum (6.2 A at a 9.00 V plug, hot) and F1's 7.3 A column. It limits no power, so a start into a resistive
  fault rests on the FET: the drawn CSD19532Q5B reaches 3.038 of its derated chart, the CSD19536KTT 0.685 (out 3c).
- **B2, the holds.** A state table (section 4) separates charge from discharge permission: every charge hold is made by the
  CHRG_INHIBIT bit (or ChargeCurrent 0), never by the CHG_INHIBIT line or SHORE_INHIBIT; in S2 (a warm CUV: the pack can take
  charge but cannot discharge) the gauge does not hold the charge, so the bit must, and whether VSYS stays regulated then is N2:
  OPEN until TI answers or the bench shows it. REQ-077 asks the charger to carry the kit; the first round's battery fallback is gone.
- **B3, the source bounds.** With the kit's losses hot (141.53 mOhm from plug to VIN_RAW, out 3d) and VBUS20's other loads, F1's
  columns admit 51.03 / 69.73 W and a 15 A part 72.5 W at a 9.00 V plug (the first round's 59.5 / 79.8 / 89.6 W left the losses
  out). The envelope at the plug (out 3h): 9 V 30.37 to 43.97 W, 12 V 32.23 to 47.72 W, 24 V 69.98 to 90.81 W.
- **B4, the weak-source envelope** is read monotone: up to 13.5 A with no time limit, then to 20 A for 600 s, to 35 A for 5 s,
  to 60 A for 0.5 s, and above 60 A up to the declared 883.5 A the fuse's total clearing I2t (not printed, R-115). The
  interconnect is specified by its loop resistance, 51.23 to 60.89 mOhm at 20 C, measured four-wire, not by a gauge and a length;
  the contacts' 23 A is Amphenol's crimp test current, so installed continuous evidence is an acceptance (E11-10).
- **B5, the charge bounds.** R-b sets ChargeCurrent() to 0x0200 (1024 mA) or less: at most 1.2567 A actual (TI's +21.5 %, R17 at
  -1 %), Q2's diode 1.257 W, TJ 124.9 C at the hottest air against 150 C. The 384 mA clamp is typical only; the first round's
  4.22 W dead-pack charge is withdrawn: up to 17.59 W, drawn only from what DPM leaves after the system.
- **No owner question is forced** (section 5); **D-06** stays resolved in design (section 6) with the corrected envelope; **D-09**
  keeps its reproduced margin (4.927 to 14.653 ms against 4.593 ms) and its conditional chart (0.71 A against 0.675 A), as the
  resolution while the LM5069 stays (section 7).

## 1. What the requirements demand of source-only operation (U-04; out 1)

Quoted from `pcb_requirements.yaml` and `TEST-PLAN.md`, not reinterpreted:

- **REQ-015**, statement: "A 9 to 36 V vehicle and shore input runs the kit and charges the pack, with reverse-polarity
  protection, under- and over-voltage limits, a line filter designed to MIL-STD-461 limits, a NATO 2-pin plug cable and the
  MIL-DTL-38999 receptacle. The input is not qualified against any vehicle surge standard and is not intended for 24 V military vehicle buses (D-16)."
  Acceptance: "Operates and charges across 9 to 36 V, and takes a reversed input and an over-voltage to the front end's limit
  (40 V, 32.55) without damage, on the prototype; CE102 under its limit line (TEST-PLAN M1)."
- **REQ-014**: "missions longer than the pack rely on vehicle or solar input (D-06)".
- **REQ-024**: "a pack cold-soaked below about -10 C at the cells is not started from (shore or vehicle power, or warming,
  first; D-02d)"; its acceptance, TEST-PLAN E4-O: "started warm or from shore or vehicle input (D-02d: a cold start from the
  pack below about -10 C cell temperature is out of scope; inside the envelope, so an acceptance test)".
- **REQ-046**: "The cells are charged only between 0 and +45 C and discharged only between -10 and +60 C at the cell surface;
  below 0 C the pack is warmed by its heater mat before charge."; its acceptance: "the bridge's own hold clears above 3 C
  (PANEL.md section 10)".
- **REQ-077**, acceptance: "the charge held by the charger's CHRG_INHIBIT with the charger still carrying the kit on shore".
- **REQ-072** (obligation OBJECTIVE): "after a permitted pack cutoff the remaining supply carries the loads, D-26".

| Requirement | Obligation | Source voltage | Names a load state | What it asks of a source alone |
|---|---|---|---|---|
| REQ-015 | mandatory | 9 to 36 V, the measuring point not stated | no | operates and charges; the pack's state not named |
| REQ-014 | mandatory | none | no | longer missions rely on the input |
| REQ-024 (D-02d), E4-O | mandatory | shore or vehicle (9 to 36 V by REQ-015) | no | a start with a cold-soaked pack, both of whose FETs are open below -9 C (the image's UTD; UTC 1 C) |
| REQ-046 | mandatory | none | no | the pack warmed by its heater before charge; the bridge's hold clears above 3 C |
| REQ-077 | mandatory | on shore | no | the charge held by CHRG_INHIBIT while the charger carries the kit |
| REQ-072 | objective | solar | yes (PS-IDLE-SPEC) | after a permitted pack cutoff the remaining supply carries the loads |

**So**, at 9 V REQ-015 does not mean the full PS-IDLE-SPEC profile: its text names no profile, and the record does not add one.
The mandatory text does ask a function of a source alone: a start and a pack warm-up with the pack's FETs open, and a charge hold
during which the charger carries the kit. The fix round turns that into a functional acceptance at 9 V at the plug (section 3g):
the least state that performs the sequence (one module running the bridge, the heater on, the charge held) carried by the source.

## 2. The charger and the pack with no usable pack (U-04; out 2)

**What SLUSE66A states (MAKER):** no battery MOSFET (p.1); from VBUS the registers, the cell count, then "Converter powers up."
with no battery condition (9.3.1, p.24); power-up curves drawn "2-cell without battery" (Figures 10-4, 10-5, p.89); "When
CHRG_OK goes HIGH, the system is powered from adapter through the charger. When adapter is removed, the system is connected to
battery." (11, p.92); CHRG_OK's conditions are VBUS's window and the faults, not the battery (9.3.4, p.25); DPM cuts the charge
first and then "the system voltage starts to drop" while the battery supplements (9.3.17, p.29); 4S defaults ChargeVoltage
16.8 V, SYSOVP 19.5 V, VSYS_MIN 12.3 V (Table 9-2) and the charge clamped at 384 mA while SRN is under VSYS_MIN (8.5, p.10), **a
typical figure with no minimum or maximum printed**; ChargeCurrent with the 5 mOhm RSR in 128 mA steps, 0 A at POR, and at
REG0x03/02 = 0x0200 (1024 mA) regulated within -18 % to +21.5 %, a row printed for VBAT above VSYS_MIN (8.5, p.10); in the BATOVP
paragraph, with charge enabled the converter shuts down and "if charge is disabled the converter should keep operating without
disturbance" (9.3.21.5, p.34): **a sentence about a battery over-voltage event, not a specification of VSYS's regulation or
transient response with no battery** (N1, N2); AUTO_WAKEUP_EN, 0 at POR, would give a battery under VSYS_MIN 128 mA for 30 min,
but only after a host sets it (p.61); HIZ: "converter shuts off" under 0.4 V on ILIM_HIZ (9.3.8); VSYS under 1.6 V for 2 ms:
"shut down and latched off" until a host write (9.3.21.8); "Overall 50-uF effective capacitance on VSYS net is necessary
(POSCAP is preferred)" (10.1, p.83).

**What the boards and the pack's image add (NETLIST, RECORD):** board A's strap reads 4S (75.1 % of VDDA), so U3 never sees
"battery removal"; every load is on VSYS with the pack beyond R17; CHG_INHIBIT pulls ILIM_HIZ low (HIZ); SHORE_INHIBIT pulls the
hot swap's UVLO low (input off); board P's gauge has no PCHG FET and its image writes PCHG_COMM 1 (pre-charge through the
charge FET, SLUUAQ3A 4.9 and 14.2.1.1); a CUV trip sets XDSG only (2.2); UTD -9 C sets XDSG and UTC 1 C sets XCHG (4.12); Q2's
body diode is CSD17570Q5B's, VSD at most 1 V (at 50 A) and RthetaJA at most 50 C/W (p.3).

**What follows, by pack state (INFERRED from the rows above):**

| Pack state | VSYS | Charge | What holds it |
|---|---|---|---|
| absent, or both FETs open (below -9 C, SHUTDOWN, a permanent fail) | ChargeVoltage, at most 16.884 V written | none | the voltage loop on SRN with no current in R17 (11, 9.3.1); N1 |
| at CUV, charge FET on | the stack plus VSD, 10 to 11 V | the clamp, 384 mA typical, while SRN is under 12.3 V (0.038 C a cell, under Samsung's 0.1 to 0.5 C pre-charge range, a lower current with no consequence stated) | the clamp; rule R-b above it, its 1.2567 A taken as the bound here too (CONDITIONAL) |
| self-discharged to the Shutdown Voltage (2.0 V a cell) | 8 to 9 V while it precharges | as above | under A-14's assumed 10.0 V floor: the loads wait (N5) |
| the clamp lifted (SRN at 12.3 V, a stack of 11.3 V or more) before CUV recovers (3.00 V a cell) | rising | ChargeCurrent through Q2's diode: 3.0 A would be 3 W, 150 K over the air | rule R-b: 0x0200 or less, at most 1.2567 A actual, 1.257 W, 62.8 K, TJ 124.9 C at 62.1 C air |
| CHG_INHIBIT (HIZ) or SHORE_INHIBIT asserted, the pack unable to discharge | none: the kit stops, its controller dies, the pull-downs release the line, it restarts: a loop | none | rule R-a forbids it |

**Finding U4-F1.** FW-C08 asserts SHORE_INHIBIT "on the bridge's request when the pack reads below 0 C" (and PANEL.md section
10 says the same). With a pack cold-soaked below -9 C both FETs are open, so the hold cuts the very source start REQ-024
requires; with HIZ the same follows (9.3.8). CONOPS already holds the H1 charge by the CHRG_INHIBIT bit for this reason.

**Not stated in any held document (named, not inferred):** N1 VSYS's regulation and transient response with no battery under
the kit's load steps; N2 what the converter regulates with CHRG_INHIBIT = 1 or ChargeCurrent 0 and no battery current
(Q-TI-3); N3 whether the charger charges before any host write (Q-TI-2); N4 VSYS's effective capacitance at 16.884 V against
TI's 50 uF; N5 every load converter's minimum input (A-14, R-49); N6 0-V charging before the gauge's SUV check (Q-TI-7).

## 3. The entry at a 9.00 V plug, the kit's own losses and the source envelope (U-04, B1 and B3; out 3)

### 3a. The drawn LM5069 cannot start from a 9.00 V plug (finding U4-F2, corrected)

SNVS452G gives UVLOTH 2.45 / 2.5 / 2.55 V and UVLOHYS 12 / 21 / 30 uA (p.5), and Equations 38 to 40 (p.24): the **falling**
threshold is UVLOTH x (1 + R20/R21) and the **rising** one adds UVLOHYS x R20 (MAKER). The first round placed the hysteresis on
the falling edge; its numbers and its R21 draft were wrong and the draft is withdrawn. Corrected (INFERRED): as drawn (R20 100k,
R21 38.3k, 1 %) the entry turns on at 9.91 / 11.13 / 12.37 V and off at 8.72 / 9.03 / 9.34 V; the withdrawn R21 42.2k would turn
it on at 9.33 / 10.52 / 11.74 V: neither starts from 9.00 V.

No divider fixes it. POREN, the threshold at which the LM5069 enables all its functions, is 8.4 V typical and **9.0 V at most**
at its own VIN; PORIT 7.6 / 8 V; the operating range starts at 9 V (p.1, p.5; MAKER). U6's VIN is DC_P, behind the LM74700 ideal
diode (NETLIST), whose regulated forward drop is 13 / 20 / 29 mV (SNOSD17G): before the hot swap conducts, VIN is at most
**8.987 V** from a 9.00 V plug, under POREN's 9.0 V maximum (NOT MET, INFERRED); with the in-service current flowing it falls
further, to 8.42 V at the plug's maximum (3e), under POREN less its 90 mV typical hysteresis. The IC cannot be supplied from elsewhere: VIN is
the current-sense reference (VCL is the VIN-SENSE voltage), so it sits at R19's top (MAKER, NETLIST).

### 3b. What a replacement must do, and the candidates

(1) Operate and enable below its own supply at the in-service maximum from a 9.00 V plug (DC_P 8.42 V hot); (2) act on overcurrent
between the in-service maximum at 9 V (6.2 A) and F1's 80 C column (7.3 A); (3) keep the pass FET inside its derated chart in
every start, a start into a resistive fault included; (4) lock out over-voltage above CS101's 38.83 V peak and under D10's
42.4 V breakdown at -20 C (L4-E9), with a 100 V class rating like the LM5069's.

| Candidate (TI sheet, held back) | Rows read (MAKER) | Verdict |
|---|---|---|
| TPS1663 eFuse (SLVSET9G) | 4.5 to 60 V, 67 V absolute; its highest current limit (RILIM 3 k) 5.58 / 6 / 6.42 A | fails (2): its lowest limit is under the 6.2 A in-service maximum |
| TPS4811-Q1 (SLUSEE5E) | VS 3.5 to 80 V, 100 V absolute, VS POR 2.75 / 3 / 3.2 V; EN/UVLO and OV 1.16 / 1.18 / 1.2 V rising, 1.1 / 1.11 / 1.13 V falling; OCP 29.2 / 30.6 / 31.5 mV at RSET 100 Ohm, RIWRN 39.7 k; ISCP bias 13.7 / 15.6 / 17.6 uA (Equation 11); TMR 73 / 82 / 91 uA to 1.112 / 1.2 / 1.3 V; short-circuit response 4 / 5 us; Equation 3's gate-slew inrush | meets (1), (2) and (4); it limits no power, so (3) rests on the pass FET: **selected** with a FET that carries it |
| a power-limiting controller under 9 V | none among the held sheets (TI's power-limiting hot-swap family starts at 9 V or above) | not drafted (named) |

### 3c. The selected entry (SESSION; draft `apply_gen_sch_e_entry.py`)

U6 **TPS48110AQDGXRQ1** (LCSC C17556513, the OV-pin variant with auto-retry), Q7 **CSD19536KTT** (C2687963, D2PAK), R19 **4.5
mOhm** 1 % 50 ppm/K (C2985708), L2 **SRF1260-1R0Y** (C7084461); RSET 100 Ohm and RIWRN 39.7 k at 0.1 % (TI's characterised point;
C861872), RISCP 3.01 k, CTMR 22 nF C0G (C97929), gate slew R1 36.5 k with C1 10 nF C0G 100 V (C184799) and R2 10 Ohm, CBST 1 uF;
UVLO 59.0k over 10.0k, OV 332k over 10.0k at 0.1 %, INP 100k over 39k, TI's 100 Ohm and 100 nF VS filter and 1 nF CSCP. Its
figures (INFERRED from the rows of 3b and the parts' tolerances):

| Function | Value |
|---|---|
| UVLO (DC_P) | on at 7.87 / 8.14 / 8.44 V, off at 7.46 / 7.66 / 7.95 V |
| OV | off above 39.6 / 40.36 / 41.22 V, on again under 37.55 / 37.96 / 38.82 V |
| overcurrent (the breaker) | 6.364 / 6.8 / 7.136 A for 0.247 / 0.322 / 0.426 ms (CTMR on the GRM3195 family's rows, an ASSUMPTION for this part), retry 0.5 s |
| short circuit | 10.36 / 12.04 / 13.87 A, off within 5 us (14 us with CSCP's filter) |
| the start | slew 17.28 / 20.71 / 24.65 V/ms; inrush 0.382 to 1.219 A into 22.1 to 49.5 uF; at most 2.5 ms to 43.18 V |
| pins at the clamps' 64.5 V | INP 18.36 V, EN/UVLO 9.35 V, OV 1.89 V, under the 20 V absolute; INP high from 7.23 V |

**A start into a resistive fault** is where a breaker without power limiting is weak. Out 3c scans faults from 0.1 to 1000 Ohm on
VIN_RAW at 43.18 V with the breaker at its slowest (7.14 A for 0.426 ms, 13.87 A) and both slew and capacitance corners, holding
every point of the pulse against the chart for the whole pulse (conservative: no thermal-impedance superposition), derated by
L4-E9's 0.4454 (a 150 C part at a 94.3 C case; the CSD19536KTT's TJ is 175 C, so conservative). The drawn **CSD19532Q5B reaches
3.038** of its derated Figure 10 (NOT MET); the **CSD19536KTT reaches 0.685** of its Figure 4-10 (read from TI's vector drawing:
at 43.18 V 100 us 221.7 A, 1 ms 20.02 A, 10 ms 6.228 A; MAKER), and its ordinary start 0.182 (MEETS, INFERRED). A hard short in
service is off within 14 us; the peak before that is set by the loop's inductance, which no document gives (L4-E9's open item,
carried; E11-20; CONDITIONAL).

### 3d. The kit's series resistance from the plug, hot

The interconnect loop at its resistance ceiling (6 m outside at REQ-024's +40 C, 1 m inside at the 62.1 C air) 66.432 mOhm
(SESSION, INFERRED); the D38999 size 12 pair 3.652 mOhm (MAKER, 42 mV at 23 A each); the NATO plug's pair 3.652 mOhm
(ASSUMPTION, as a size 12 contact); J_DCIN of the XT60 class 1.1 mOhm (MAKER, 0.55 mOhm a contact); F1 at its rated current
10.8 mOhm (MAKER, 108 mV typical); its holder 1 mOhm (ASSUMPTION); Q1 hot 7.02 mOhm (NETLIST 3.9 mOhm x 1.8, ASSUMPTION); R19
4.556 mOhm (CATALOGUE); Q7 hot 4.32 mOhm (MAKER 2.4 mOhm x 1.8); L2 at the air plus its rise 33.992 mOhm (MAKER, INFERRED); board
copper and the dock's pins 5 mOhm (ASSUMPTION). **93.66 mOhm from the plug to DC_P, 47.87 mOhm on to VIN_RAW, 141.53 mOhm in
all**; the first round's 115.511 mOhm model was at 20 C without the contacts.

### 3e. The in-service maximum at a 9.00 V plug

With the corrected knee's high band, VBUS20 at 20.96 V and the front end at 0.93: **VIN_RAW 8.123 V, 6.2 A from the plug, DC_P
8.419 V** (INFERRED). Against the selected entry: the UVLO's highest rise (8.44 V) under DC_P before any current (8.971 V) and its
highest fall (7.95 V) under DC_P in service (MEETS); the breaker's lowest 6.364 A over 6.2 A, 2.6 % in hand, so the front end's
efficiency at 8.1 V must be 0.906 or more (C-8, CONDITIONAL); the breaker's highest 7.136 A under F1's 7.3 A (MEETS); L2 at 7.14 A
36.1 K over the air, 98.2 C against its 105 C (MEETS); Q7 0.22 W.

### 3f. The corrected knee (SESSION, a specification) and the restart guard (draft `apply_gen_sch_a_guard.py`)

L4-E5's H3 network is not drawn (its own missing draft), so this record specifies the shape it is to be drawn to: **a flat 1.89 A
of board current** (the pin at 1.756 V) from VIN_RAW **7.95 V** up to 10.955 V, where L4-E5's line takes over; below 7.95 V
L4-E5's knee slope (2.484 V/V at the pin): zero at 7.646 V, HIZ entry 7.404 V, exit 7.565 V. With L4-E5's +-0.5 % the knee's top
is at most 7.99 V, 0.133 V under the plug's operating point, and HIZ is certain below **7.367 V**. The functional need (3g) sets
the flat target at 1.8867 A or more.

The front end's restart guard (U34, board A) as drawn falls at 7.856 / 8.08 / 8.309 V, over the plug's 8.123 V operating point.
**R14 76.8k 1 % (C23107)** puts its fall at **6.754 / 6.944 / 7.139 V** and its rise at 6.889 / 7.083 / 7.282 V, 0.228 V under the
knee's certain HIZ (L4-E5's rule: 0.1 V or more); at its lowest fall the guard's running levels scale to FE_VZ 4.64 V, FE_RUN
2.75 V (Q36 and Q37 need 2.5 V at most) and EN 1.89 V (VEN(OP) 1.29 V at most) (INFERRED).

### 3g. The functional warm-up at a 9.00 V plug (B3's acceptance)

REQ-024's start with the pack cold-soaked (both FETs open), REQ-046's heater before any charge, and the charge held while the
charger carries the kit (REQ-077) are done by the bridge on one module. **SESSION: the least state that performs the sequence is
PS-SURV, slot 2 alone** (hc2 `pwr_red2.out`: 12.45 / 21.73 / 42 W) **with the heater** (8.58 W, its overlay on PS-IDLE-SPEC):
**21.03 / 30.31 / 50.58 W** at VBAT (RECORD). At 9.00 V at the plug, hot, the source delivers **30.37 to 43.97 W**: the plan figure
is carried at every corner (MEETS); its hi corner is not, by 6.61 W, and there rule R-c's shed applies (the heater cycled or the
module's radios held; CONDITIONAL on the measured state, E11-06). CONOPS 4c's warm-up with three modules (71.06 W) is an operating
choice that sheds to this state at a weak source.

### 3h. The source envelope at the plug

The low side with the losses hot and VBUS20 at 19.146 V, the high side with no loss and 20.96 V, U3 0.9733 (INFERRED):

| Plug | VIN_RAW at the low side | U3 board current, A | at VBAT, W | L4-E9 at VIN_RAW (no loss) |
|---|---|---|---|---|
| 9 V | 8.408 V | 1.63 to 2.155 | 30.37 to 43.97 | 19.9 to 36.6 W |
| 12 V | 11.544 V | 1.729 to 2.339 | 32.23 to 47.72 | up to 47.4 W |
| 24 V | 23.525 V | 3.755 to 4.451 | 69.98 to 90.81 | up to 90.6 W |
| 36 V | 35.622 V | 4.537 to 4.884 | 84.55 to 99.64 | the window |

| State (plan, at VBAT) | 9 V | 12 V | 24 V | 36 V |
|---|---|---|---|---|
| PS-RED 22.2 W | carried | carried | carried | carried |
| the functional warm-up 30.31 W | carried | carried | carried | carried |
| PS-RED with the heater 33.1 W | above the minimum only | above the minimum only | carried | carried |
| PS-IDLE-SPEC 42.8 W | above the minimum only | above the minimum only | carried | carried |
| PS-IDLE-SPEC cold, heater on 45.46 W | not carried | above the minimum only | carried | carried |
| PS-TYP 63.0 W | not carried | not carried | carried | carried |
| the cold warm-up 71.06 W (CONOPS 4c) | not carried | not carried | above the minimum only | carried |

A dead pack's charge on top: at most 1.257 A x 14 V = 17.59 W under R-b, drawn only from what DPM leaves after the system
(9.3.17), so it never pushes the kit out of the envelope (INFERRED). A pack able to discharge supplements any shortfall (L4-E9
section 3); these bounds are for the pack that cannot.

**Finding U4-F3, kept.** REQ-015 names no measuring point; **SESSION (first round): the design basis for its 9 V is the kit's
plug**, the most demanding reading. Through the drawn knee (zero at 8.75 V of VIN_RAW) a 9.00 V plug settles VIN_RAW at 8.833 V
and gives 10 W (8.819 V and 8.3 W with the drawn lead), against 30.2 W at VIN_RAW 9 V: 3f replaces that knee (out 3i).

## 4. The comparison, the selection and the rules (U-04; out 4)

| | (A) the drawn non-power-path charger, with rules | (B) a charger with a battery FET (NVDC power path) | (C) a pre-charge path on board P (PCHG FET and resistor) |
|---|---|---|---|
| Power at 9, 12, 24 V with no usable pack | section 3h's envelope; the same in (B) and (C), whose limit is the source path, not the charger | the same | the same |
| Start from a dead pack | the source carries the kit at once when the pack is absent or both FETs open; a pack at CUV holds VSYS at 10 to 11 V; one self-discharged to 2.0 V a cell holds it at 8 to 9 V, under the converters' assumed floor, until it precharges | VSYS regulated at VSYS_MIN whatever the pack; the pack precharged through the battery FET | VSYS stays at ChargeVoltage while the resistor precharges the pack |
| Protection interaction | the gauge's window acts on its FETs as now; rules R-a and R-b keep the holds off the source and the diode's junction under its maximum | a series FET in the pack path, a new single point on the battery-only path, its own fault list | the PCHG FET short leaves a resistor path round both protection FETs; the resistor in the sealed case |
| Parts and board changes | none of power for the charger (the entry's replacement, 3c, is needed by every option) | U3 replaced, a battery FET, every L4-E4 to L4-E8 setting on the charger re-derived (IIN_HOST, H3 on ILIM_HIZ, R11, R12, the bank) | a P-FET, a power resistor and its land on board P; PCHG_COMM 0 in the image |
| Energy cost | none | 0.324 W per mOhm at 18 A; 8.8 mW per mOhm at PS-IDLE-SPEC | 8.98 W in the resistor at 2.0 V a cell for 0.1 C (8.63 ohm), 3.38 W for the charger's 384 mA (22.9 ohm) |
| What still depends on a maker | N1 (TI); N2 for state S2 (open); N3 for a pack below the controllers' floor; Q-TI-7 | the new charger's sheet: the one NVDC charger held, TI's BQ25798, states the regulation (p.1) but its integrated battery FET carries 6 A RMS and 10 A for 1 s (p.7), under the pack's 18 A peak, so an external-FET part is needed, of which no sheet is held | Q-TI-7; the resistor's pulse rating |

Considered and not compared: a source-fed keep-alive rail for the controllers. It keeps the controllers up but does not run the
kit, which still hangs on VSYS; whether the controllers' own converters reach down to a dead pack's VSYS is E11-08's reading.

**Selected (SESSION): (A).** *Why:* it is the only arrangement with no power part added to the charger; TI's own text covers its
two central behaviours (the system powered through the charger with no battery, 11 and Figures 10-4 and 10-5; the dead pack
charged at a clamped current, Table 9-2 and 8.5); its hazards are rules, not topology (U4-F1's holds, R-a; Q2's diode, R-b); (B)
reopens five accepted records on a part whose sheet is not held, and (C) puts 3.4 to 9.0 W into the sealed case to buy a faster
start from a pack nobody requires the kit to start from at once. **Its cost, stated:** a pack self-discharged under about 2.4 V a
cell holds VSYS under 10 V until it precharges at the clamp; the time is not computable from held data and is measured by
E11-06. **Reversed by:** TI's answer to N1 (E11-05) or E11-06 showing VSYS does not hold under the kit's load steps with no
battery; the first remedy is VSYS's capacitance (TI's 50 uF effective, POSCAP preferred, E11-07), and only if that fails does
(B) return.

**Rule R-a, the charge holds as a state table (SESSION; B2).** The gauge's own FETs give two separate permissions (SLUUAQ3A 2.2
and 4.12; INFERRED):

| State | Charge FET | Discharge FET | Examples | What carries the kit | How a charge hold is made |
|---|---|---|---|---|---|
| S1 | on | on | in both windows | the pack and the source together | the CHRG_INHIBIT bit or ChargeCurrent 0 (9.4.1): the converter keeps carrying the kit from the source (11), REQ-077 as written |
| S2 | on | off | a warm CUV trip; an OCD, AOLD or SCD latch | the source alone; the pack can still take charge through Q2's diode, so the gauge does NOT hold the charge | only the bit or ChargeCurrent 0; whether VSYS stays regulated with charge inhibited while the pack cannot discharge is N2 (Q-TI-3): OPEN, the bench shows it (E11-06) before the hold is relied on |
| S3 | off | on | between UTD -9 C and UTC 1 C; OTC; COV | the pack or the source | the gauge already holds; a requested hold (REQ-077's hot hold, the operator's "no charge") by the bit as in S1 |
| S4 | off | off | below -9 C; SHUTDOWN; a permanent fail; no pack | the source alone | the gauge already holds; no bit is set, so N2 does not arise |

In every state, a charge hold (the cold hold, REQ-046's, REQ-077's hot hold, the operator's "no charge") is made by the
CHRG_INHIBIT bit or ChargeCurrent 0, never by the CHG_INHIBIT line (HIZ) or SHORE_INHIBIT; in S2 and S4 neither line is asserted,
because each removes the kit's only supply. SHORE_INHIBIT stays for the operator's "inputs off" and the water-on-floor isolation,
with a warning first in S2 and S4. REQ-077 asks the charger to carry the kit while the charge is held; the first round's reading
that a pack could carry it instead is withdrawn.

**R-b (SESSION; B5).** ChargeCurrent() at **0x0200 (1024 mA set) or less** while U3's own SRN reading is under 14.0 V or the gauge
reports XDSG or PRECHARGE: at most **1.2567 A** actual (TI's +21.5 % at 0x0200, R17 at -1 %), at least 0.8314 A; Q2's diode then
dissipates 1.257 W at most, 62.8 K over the air, TJ 124.9 C at the 62.1 C inside air against 150 C (MEETS, INFERRED). Without
the gauge's report the 14.0 V threshold covers a cell up to 0.25 V under the stack's average (the panel controller reaches the
gauge only through a running module). Below VSYS_MIN the clamp is the limit TI states and its maximum is not printed: the
setting's 1.2567 A is taken as the bound there too (CONDITIONAL; E11-06 measures it). Beyond it RT1's PTC beside the FETs turns
them off (a permanent fail, safe, named).

**R-c.** While the pack cannot discharge (S2, S4), the bridge keeps the kit's load under the envelope's minimum at the measured
input (section 3h), shedding in CONOPS 4c's order; on a source-only brown-out the charger may latch off (9.3.21.8): the host
clears the fault bit when it can, or the operator re-plugs the source.

**R-d.** The image keeps PCHG_COMM 1 and the SUV check (PRIMARY-CONFIGURATION.md), with Q-TI-7 open.

## 5. Is an owner question forced? (out 5)

No. The brief's test is whether REQ-015 as written cannot be met at 9 V by any arrangement because the source path's own
capability caps the power below the required load. The functional sequence the mandatory text asks of a source alone is carried
at 9 V at the plug at its plan figure (section 3g), and no requirement names a larger load. What the source path admits at a
9.00 V plug, with the kit's losses and VBUS20's other loads (INFERRED; the check's reference without either: 53.9 / 69.79 / 76.96
W):

| Ceiling | Loop | VIN_RAW | at VBAT |
|---|---|---|---|
| F1's 80 C column, 7.3 A, the losses hot | 141.53 mOhm | 7.967 V | 51.03 W |
| F1's 0 C column, 9.8 A, the losses cold | 97.66 mOhm | 8.043 V | 69.73 W |
| a 15 A MINI's 80 C column, 11 A, the losses hot | 141.53 mOhm | 7.443 V | 72.5 W |

These are ceilings with the electronics set to use all of them; the breaker's band and the knee's spread keep the least delivered
figure at 30.37 W. PS-TYP (63.0 W) and the CONOPS cold warm-up (71.06 W) exceed the 9 V ceilings of F1 as fitted: a design
envelope of the kit at 9 V, not a conflict with an approved requirement. REQ-015 states no source current capability, so every
figure takes the source as holding its voltage (named).

## 6. D-06: the vehicle-entry interconnect (out 6)

**The envelope (MAKER, the held 0997 sheet p.3; read monotone, INFERRED; B4).** 110 %: at least 360000 s; 135 %: 0.75 to 600 s;
200 %: 0.15 to 5 s; 350 %: 0.08 to 0.5 s; 600 %: 0.03 to 0.1 s. A larger current clears no later than a smaller one, so a source
can leave:

| Current | For at most | Energy at the interval's top |
|---|---|---|
| up to 13.5 A | no maximum printed: with no time limit | continuous |
| 13.5 to 20 A | 600 s | 240000 A2s (a continuous rating of 20 A covers it) |
| 20 to 35 A | 5 s | 6125 A2s |
| 35 to 60 A | 0.5 s | 1800 A2s |
| 60 A to the declared prospective 883.5 A | 0.1 s | the 600 % row bounds it only by 78053 A2s; F1's total clearing I2t at 58 V DC is not printed (the sheet's 93 A2s is a typical melting figure), so the elements are judged against it once filed (R-115) |

PWR-003 asks the clearing characteristic to sit below the damage characteristic of the weakest element downstream.

**The elements as drawn (NOT MET):** J_DCIN's VH contact with the drawn AWG 18 lead on the standard header (VH prints 10 A at AWG
16 standard and 7 A at AWG 18 shrouded only: none stated); the D38999 size 16 contact, insert 13-4 (13 A, Amphenol's test
current); F1's holder Keystone 3568 (the catalogue page prints UL ratings of 15, 20 and 30 A for other MINI clips and holders and
none for the 3568); the DC lead, Lapp OLFLEX ROBUST 210 4 x 1.0 or Alpha Wire 25064 (no current rating in either sheet); the
inside lead, 500 mm of AWG 18 (no part, no rating); board E's input bands (10 A declared).

**The options:**

| Option | What it does | Verdict |
|---|---|---|
| (i) rate the interconnect to the whole envelope | every element at least 20 A continuous where installed, and the short-time obligations of the table above | **selected (SESSION)** |
| (ii) a fuse and protection change | the 7.5 A MINI's 80 C column is 5.1 A. An entry limit whose maximum is 5.1 A has its minimum at 3.942 A for the LM5069 (VCL 48.5 over 61.5 mV, R19 at +-1 %) and at 4.548 A for the selected breaker: both under the in-service 6.2 A at 9 V (and L4-E5's 4.629 A); its own envelope still passes the unrated cable | rejected: it fails 9 V, and leaves the cable unrated |
| (iii) the source's capability stated in REQ-015 (ECSS 6.17.3c) | a requirement change, the owner's | not needed: (i) resolves it in design |

**Selected part classes and their obligations (SESSION; the exact parts Layer 7's and Layer 8's):**

| Element | Selected class | Rating and evidence |
|---|---|---|
| receptacle and plug contacts | MIL-DTL-38999 size 12; insert 17-6 (six size 12: DC and solar pairs on four, the two unassigned between power and return, the ECSS 6.11.3a screen), or 13-26 (two size 12 and six 22D) with the solar pair moved to rated contacts elsewhere | Amphenol prints 23 A as a crimp-contact test current (p.28), not an installed rating: the insert's installed continuous rating of 20 A at the case's air (the maker's derating, or a measured rise) is E11-10; short-time data E11-16 |
| J_DCIN | a board connector of the XT60 class, of the gender opposite J_BATT's so the pack lead cannot mate it, or soldered lead lands | 30 A rated, 60 A instantaneous, 12 AWG recommended (Amass V1.2); the 60 A's duration is unstated: E11-16 |
| F1's holder | a MINI 297/997 holder whose maker prints at least 20 A | the 3568 prints none |
| the interconnect's conductors | cores whose maker states at least 20 A continuous each; the loop specified by its resistance (below) | no sheet held: E11-11, E11-12 |
| board E's copper, J_DCIN to F1 to D10, C4 and Q1 | at least 20 A continuous | a layout constraint, E11-14 |
| F1 | unchanged, Littelfuse 0997010.WXN | 58 V DC, 1000 A at 58 V DC; 7.3 A at 80 C against the selected breaker's 7.136 A (the drawn LM5069's 6.15 A) |

The interval tops against an AWG 14 core, adiabatic: 35 A for 5 s 7.07 K, 60 A for 0.5 s 2.08 K (INFERRED); at 883.5 A the
monotone bound alone would give 90.07 K, so F1's clearing I2t decides that interval. Against the size 12 contact's 23 A the same
I2t equals 11.578 s (35 A for 5 s) and 3.403 s (60 A for 0.5 s) at its test current, which is not a short-time rating (E11-16).

**The interconnect by its resistance (SESSION; the minor on A11-1).** A larger or purer conductor raises a stiff fault, so the
check cannot rest on copper constants or on a gauge and a length. The loop from the plug's pins to J_DCIN, both conductors and
the inside lead, is specified at **51.23 mOhm or more at 20 C** (the floor of 43.18 mOhm at -20 C, which keeps a stiff source at
the OVLO's 43.18 V under F1's 1000 A) **and at most 60.89 mOhm at 20 C** (the selected 57.99 mOhm plus 5 %, the 9 V envelope's
basis), **measured four-wire on every assembly and every replacement** (E11-11). The selected construction is one way inside it:
3.0 m of AWG 14 with the 0.5 m lead.

**The stiff source again** (copper alone at -20 C, the source's resistance zero, A-12, at 43.18 V; INFERRED): as drawn 0.07577
ohm, 569.9 A (L4-E9 569.8 A); AWG 14 at 2.0 m 0.03491 ohm, **1236.9 A against F1's 1000 A, NOT MET**; AWG 12 at 3.0 m 1404.8 A,
NOT MET; **AWG 14 at 3.0 m 0.04888 ohm, 883.5 A, MEETS**; AWG 14 reaches the floor from 2.59 m of cable with the 0.5 m lead. A
shorter or heavier lead needs a fuse with a larger interrupting rating at 58 V DC, of which no sheet is held. The lowest stiff
fault at 9 V with the copper at 62.1 C is 133.2 A, 13.32 times the rating, inside the 600 % row's 0.1 s. **D-06 is resolved in
design**, CONDITIONAL on the makers' data the acceptances name (cable, inside lead, holder, NATO plug, the contacts' installed
rating and short-time data, F1's clearing I2t).

## 7. D-09: the hot swap's fault time against its start (out 7)

**This section stands for the LM5069 as drawn.** The selected entry of 3c removes the LM5069 and its timer; `apply_gen_sch_e_timer.py`
is the alternative to `apply_gen_sch_e_entry.py` while the LM5069 stays, and the two drafts refuse each other (SESSION).

**The rows (MAKER, SNVS452G):** VTMRH 3.76 / 4 / 4.16 V, ITIMER 51 / 85 / 120 uA, VCL 48.5 / 55 / 61.5 mV, Equation 9, and TI's
9.2.1.2.4: "TI recommends setting the minimum fault time (tflt) to be greater than the start time (tstart) by adding an
additional margin of 50% of the fault time". The power limit with L4-E9's R24 22k is 22.018 W at 43.18 V and falls with VDS
(Equation 9), which TI notes makes the start "slightly longer".

**The start, recomputed (INFERRED):** the hot swap charges 34 uF, not 31 (NETLIST: board E C6 on DC_HS, C7, C8; board A C11,
C12, and C207 and C210 behind D19 and R196); the resistive load on VIN_RAW is bounded by its resistors alone (R27 with LED1,
R40, R14, R200: 21.8 mA at 43.18 V) plus U2's 10 uA shutdown current. **The front end's own load:** U34 holds U2 off until 79 /
127 / 201 ms after VIN_RAW passes its UV rise (gen_sch_a.py's derivation from SNVSBJ1E), 25.8 times the start's maximum, so the
soft start never overlaps the hot swap's start and the front end's load during it is its bias network. Integrating Equation 12
with the limit following VDS: nominal 1.588 ms (L4-E9 1.324 ms); at the corners (the X7R rows stacked as L4-E9, R24 -1 %, R19
+1 %, the limit over TI's 1.3, VCL's minimum) **3.062 ms**, so the fault time's minimum must be at least **4.593 ms**.

**C5 as drawn** (100 nF K X7R, stacked) gives 2.037 to 11.866 ms: NOT MET. **No single 150 nF C0G part is stocked** (49 rows
read, none in stock at JLCPCB or LCSC; CATALOGUE). The stocked Murata GRM3195 C0G 50 V 1206 parts, read on their makers'
reference sheets (as of Jun.11,2026; held back): 0+-30 ppm/K, Table A +0.58 / -0.24 % at -55 C, endurance +-3 %, damp heat
+-7.5 % (MAKER).

| Candidate (at most two parts, SESSION) | C, nF | fault time, ms (tolerance, temperature, endurance stacked) | start | Figure 10 at its maximum |
|---|---|---|---|---|
| one 100 nF G | 100 | 2.970 to 8.619 | NOT MET | MEETS |
| one 68 nF J | 68 | 1.958 to 6.034 | NOT MET | MEETS |
| two 100 nF G | 200 | 5.939 to 17.239 | MEETS | NOT MET (0.662 A) |
| two 68 nF J | 136 | 3.915 to 12.067 | NOT MET | MEETS |
| **100 nF G with 68 nF J** | **168** | **4.927 to 14.653** | **MEETS** | **MEETS (0.710 A)** |

**Selected (SESSION): C5 GRM3195C1H104GA05D (C907944) with C121 GRM3195C1H683JA05D (C3847777)**, both on HS_TIMER, 1206 (draft
`apply_gen_sch_e_timer.py`; C121 a free designator). Fault time 7.906 ms nominal, 4.927 to 14.653 ms stacked: 0.334 ms over the
4.593 ms margin (MEETS, INFERRED). At the maximum, Q7's Figure 10 at 43.18 V from TI's vector drawing (10 ms 1.879 A, 1 ms 5.055
A, m 0.4299) carried past the 10 ms line by 46.5 % and derated to Q7's 94.3 C case by 0.4454 (L4-E9) allows 0.71 A against
the pulse's 0.675 A (MEETS, CONDITIONAL on the power law past 10 ms and on board E's copper under Q7). Sensitivities: a steeper
law past 10 ms (m 0.5) 0.691 A, MEETS; the damp-heat row stacked instead of endurance 4.699 to 15.293 ms and 0.697 A, MEETS; TI's
own basis (typical values) 7.906 ms against 2.382 ms. The DC line derated (0.271 A) is under the pulse; the pulse ends at the
fault time, so no steady rating is asked of it. *Reversed by:* a measured start (E11-17) longer than 3.285 ms at 43 V, or a
measured fault time outside the band; the alternatives then are a higher power limit (a shorter start against a larger pulse)
or a Q7 with a larger SOA. **D-09 is resolved in design for the LM5069**, CONDITIONAL as stated.

## 7a. The interface and firmware drafts (text, for Layer 5 and the firmware owner)

These replace rows of `HW-FW-CONTRACT.md` and a paragraph of `PANEL.md`; this record does not edit either.

- **FW-C08 (SHORE_INHIBIT), proposed behaviour:** "Boot low. Asserted only on the operator's 'inputs off' and on the
  water-on-floor isolation, never for a temperature or 'no charge' hold. When the pack cannot discharge (states S2 and S4: the
  gauge's XDSG, no pack, or both FETs open) the bridge first warns that asserting it removes the kit's supply." (as written: "Boot
  low; assert on the bridge's request when the pack reads below 0 C and clear above 3 C, or when the operator sets 'no charge'")
- **FW-A14 (CHG_INHIBIT, HIZ), proposed behaviour:** "Held low (charger enabled) at power-up; asserted only by firmware, never as a
  charge hold, and never while the pack cannot discharge (S2, S4)." (as written: "Held low (charger enabled) at power-up; asserted
  only by firmware")
- **PANEL.md section 10, proposed sentence** in place of "The bridge asks the controller to assert it when the pack temperature
  (...) is below 0 C, when the operator sets 'no charge', and clears it with hysteresis (charge again above 3 C).": "Every charge
  hold (cold, hot, or the operator's 'no charge') is made by the charger's CHRG_INHIBIT bit or ChargeCurrent 0, never by the
  CHG_INHIBIT line or SHORE_INHIBIT; with both pack FETs open the gauge already holds and no bit is set; the cold hold clears with
  hysteresis (charge again above 3 C). The bridge asks the controller to assert SHORE_INHIBIT only for 'inputs off' and the
  water-on-floor isolation."
- **DCIN_PGD (board E's RP2040 input), proposed meaning** with the selected entry: the entry's fault flag (U6's FLT_I and FLT_T,
  open drain, low on an overcurrent, a short circuit or an overtemperature), no longer a power-good line.
- **New firmware rows:** R-a (the state table of section 4); R-b (ChargeCurrent() at 0x0200 or less while U3's SRN reading is
  under 14.0 V or the gauge reports XDSG or PRECHARGE); R-c (the source-only shed and the VSYS_UVP recovery); R-d (the image's
  PCHG_COMM 1 and SUV check kept).

## 7b. The CONOPS statement (draft, for the CONOPS owner)

"With no usable pack (absent, at its cutoff, or cold-soaked with its FETs open) the kit runs from its vehicle or shore input
within the source envelope at its input plug: about 30 W at 9 V, 32 W at 12 V and 70 W at 24 V on its bus at the least, which
carries one module and the pack heater for a cold start. A pack self-discharged under about 2.4 V a cell holds the system node
under the converters' floor while it pre-charges, so the kit's loads wait for it. A brown-out on the input alone may latch the
charger off until the input is re-plugged."

## 8. The downstream items (out 8)

An owner and an acceptance close the assignment, not the item.

| ID | Kind | Owner | Acceptance |
|---|---|---|---|
| E11-01 | implementation | Layer 8 board E generator owner | `apply_gen_sch_e_entry.py` after L4-E9's `apply_gen_sch_e_hotswap.py`, instead of `apply_gen_sch_e_timer.py`: U6 TPS48110AQDGXRQ1, Q7 CSD19536KTT, R19 4.5 mOhm, L2 SRF1260-1R0Y and the network of 3c; the DGX-19 land added to meshsat.pretty from TI's DGX0019A drawing and the D2PAK land checked against TI's KTT drawing; _VEH_T restated to 7.14 A; the regenerated netlist reads every value of 3c |
| E11-02 | implementation | Layer 8 board A generator owner | `apply_gen_sch_a_guard.py` with the corrected knee (E11-09): R14 76.8k (C23107); U34's fall from the fitted parts 6.75 to 7.14 V |
| E11-03 | interface | Layer 5 interfaces | FW-C08, FW-A14 and PANEL.md section 10 restated as section 7a (R-a's state table); DCIN_PGD restated as the entry's fault flag; REQ-046's hold still clears above 3 C |
| E11-04 | firmware | firmware owner | rules R-a to R-d implemented (section 7a) and checked on the bench (E11-06) |
| E11-05 | evidence | Layer 6 components | TI's answers filed: Q-TI-3 restated as N2 for S2 (VSYS's regulation with CHRG_INHIBIT = 1 while the pack can take charge but cannot discharge, under a 5 A load step) and N1, and Q-TI-2 |
| E11-06 | test | prototype bench | R-85 extended: at 9.00 V at the plug with the interconnect at its resistance ceiling, and at 12 and 24 V: the functional warm-up of 3g with the pack cold-soaked (S4), at a warm CUV (S2, the charge held by the bit: VSYS stays up) and absent; the entry does not trip (the front end's input under 6.36 A); VSYS's step response; Q2's case at R-b's current; the latch recovery by a re-plug |
| E11-07 | analysis | Layer 9 pre-layout analysis | VSYS's effective capacitance at 16.884 V from the makers' DC-bias curves at least 50 uF, else a polymer capacitor added |
| E11-08 | evidence | Layer 9 pre-layout analysis | every load converter's and the controllers' minimum input against 10.0 V (A-14, R-49) and 8.0 V |
| E11-09 | analysis | Layer 4 coordinator | L4-E5's undrawn H3 network drawn to 3f's specification (flat 1.89 A from 7.95 V to 10.955 V, zero 7.646 V, HIZ certain below 7.367 V) with E11-02's guard; L4-E5's low-light settle and the solar line re-run on it |
| E11-10 | implementation | Layer 7 mechanical | the DC receptacle and plug on size 12 contacts (17-6, or 13-26 with the solar pair elsewhere) with the insert's installed continuous rating of 20 A at the case's air filed; the plate cut-out checked against CASE-MARGINS 3.3 |
| E11-11 | implementation | Layer 7 mechanical | the DC interconnect's loop at 51.23 to 60.89 mOhm at 20 C, measured four-wire on every assembly and replacement; cores and the NATO plug with a maker's rating of at least 20 A; sheets filed |
| E11-12 | implementation | Layer 7 mechanical | the inside lead (at least 20 A) and J_DCIN at least 20 A (XT60 class, gender opposite J_BATT's, or soldered lands); board E's generator names the part |
| E11-13 | implementation | Layer 8 board E generator owner | F1's holder with a maker's rating of at least 20 A; its sheet filed |
| E11-14 | layout | Layer 9 pre-layout analysis | board E's copper from J_DCIN through F1 to D10, C4 and Q1 at 20 A continuous, and Q7's D2PAK land with its copper |
| E11-15 | implementation | Layer 8 board E generator owner | `pcb_energy_chain.yaml` SHORE_INPUT restated with L4-E9's R-95: conductor 20 A, the breaker's 7.14 A, prospective high 883.5 A |
| E11-16 | evidence | Layer 6 components | the size 12 contact's, the board connector's and the cable's short-time withstand against the monotone envelope (35 A for 5 s, 60 A for 0.5 s) and F1's total clearing I2t at 58 V DC from 60 A to 883.5 A (R-115) against each, filed |
| E11-17 | test | prototype bench | R-118 for the selected entry at 43 V: the start inside 2.5 ms with at most 1.22 A, a start into a resistive fault near 1.1 Ohm and a hard short, the breaker opening at 10.36 to 13.87 A, Q7 unharmed; with the LM5069 kept, D-09's rows (4.927 to 14.653 ms, the start inside 3.062 ms) |
| E11-18 | document | CONOPS owner | section 7b's statement in CONOPS |
| E11-19 | analysis | Layer 4 coordinator | L4-E9's entry findings that rest on the LM5069 (IF-05's hot short, D-07's power limit, R-118, the start's I2t) re-judged for the selected entry |
| E11-20 | evidence | Layer 9 pre-layout analysis | the loop inductance from the source to Q7, so the hot-short peak before the breaker opens (within 14 us) is bounded, with L4-E9's open item |

## 9. What stays conditional, and the decisions this record takes

**Conditional or open (named):** U-04: N1 (VSYS under load steps with no battery: TI and E11-06; the only item that could still
change the charger), **N2 for state S2** (OPEN: the bit's hold with the pack unable to discharge), N3, N4 (E11-07), N5 (E11-08),
N6 (Q-TI-7); the front end's efficiency at 8.1 V (0.906 or more for the breaker's 2.6 %, C-8); the pin's error (L4-E5's 0.2 A,
INFERRED); the clamp's unprinted maximum under VSYS_MIN; the functional state's hi corner (R-c's shed); a deeply discharged
pack's wait (E11-06); the hot-short peak before the breaker (E11-20); REQ-015's unstated source capability. D-06: the cable's,
inside lead's, holder's and NATO plug's makers' ratings (E11-11 to E11-13), the contacts' installed rating and short-time data
(E11-10, E11-16), F1's total clearing I2t (R-115), the plate's fit for shell 17 (E11-10). D-09 (for the LM5069): Figure 10 past
10 ms, board E's copper under Q7, the X7R stack for every start capacitor (an ASSUMPTION, as L4-E9), Murata's sheet as fetched.

**SESSION decisions:** (1) U-04: arrangement (A) with rules R-a to R-d, R-a a state table; (2) the entry replaced: TPS48110-Q1
with a CSD19536KTT, R19 4.5 mOhm, L2 SRF1260-1R0Y and the network of 3c (the first round's R21 42.2k withdrawn); (3) REQ-015's
9 V taken at the kit's plug as the design basis (U4-F3); (4) the corrected knee's flat 1.89 A from 7.95 V; (5) the guard's R14
76.8k; (6) the functional warm-up's state (PS-SURV slot 2 alone with the heater); (7) R-b at 0x0200 and 14.0 V; (8) D-06: every
element of the interconnect at 20 A or more continuous where installed, with the classes of section 6; (9) the interconnect by
its loop resistance, 51.23 to 60.89 mOhm at 20 C (the ceiling 5 % over the selected construction); (10) insert 17-6 preferred to
13-26; (11) J_DCIN of the gender opposite J_BATT's; (12) D-09: C5 and C121, at most two parts, for the LM5069. Each carries its
reason and reversal above.

**The gate's view (for the coordinator, not decided here):** U-04 moves from "unresolved by the held documents" to a selected
arrangement whose 9 V at the plug is met with drafts, CONDITIONAL on N1, N2 for S2 and the bench rows named; D-06 stays resolved
in design with the corrected envelope; D-09 stays resolved for the LM5069, the alternative to the selected entry.

## 10. Assumptions

| ID | Assumption | Impact if wrong | Verification |
|---|---|---|---|
| A11-1 | The stiff-source check rests on the interconnect's measured loop floor (51.23 mOhm at 20 C), with copper's 0.00393 /K for the temperature only; AWG 14's 2.081 mm2 describes one construction inside the window, not the check | a loop under the floor passes more than F1's 1000 A | E11-11 (each assembly measured) |
| A11-2 | The budget's battery-terminal watts taken at VBAT | a small overstatement of each state | E11-06 |
| A11-3 | Q2's VSD at most 1 V at R-b's current, from its 50 A row; board P's copper giving 50 C/W | Q2's rise under R-b | E11-06 |
| A11-4 | The start's capacitors at the Yageo X7R rows stacked, for parts of other makers too | the start's corner | E11-17 |
| A11-5 | Each VIN_RAW load path bounded by its resistor alone | the start a little shorter in fact | E11-17 |
| A11-6 | The loss model's unprinted elements: MOSFETs at 1.8 times their 25 C maximum hot, the NATO plug's contacts as size 12 contacts, the holder 1 mOhm, board copper and the dock's pins 5 mOhm, F1 at its typical rated-current drop | the 9 V operating point and the breaker's 2.6 % | E11-06 |
| A11-7 | The power law between Figure 10's 1 and 10 ms lines carried past 10 ms (as L4-E9); a fault start judged with every point held against the chart for the whole pulse, derated by L4-E9's 0.4454 | the timer's maximum (D-09) and the fault start (3c) against the charts | E11-17, R-118 |
| A11-8 | The 22 nF and 10 nF C0G parts on the GRM3195 family's rows held for the 100 nF and 68 nF parts | the breaker's delay and the slew within a few percent | E11-17 |
| A11-9 | The front end at 0.93 at 8.1 V (L4-E5's figure, C-8) | the in-service maximum against the breaker's lowest (break-even 0.906) | E11-06 |

Not claimed: nothing here is verified, built or measured; software tests establish this record's own behaviour only.
