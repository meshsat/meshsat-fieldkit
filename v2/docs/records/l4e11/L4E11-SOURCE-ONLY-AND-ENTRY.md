# L4-E11: source-only and dead-pack operation (U-04), the vehicle-entry interconnect (D-06) and the hot swap's fault timer (D-09) (MESHSAT-1357, 2 October 2026)

**Prototype design, desk arithmetic.** Nothing is bought, built, powered or measured, and no board of this set has a layout.
This page edits no generator, registry record, interface, Layer 3 file or other record. Its circuit changes are two
release-guarded drafts (`apply_gen_sch_e_uvlo.py`, `apply_gen_sch_e_timer.py`); its interface and firmware texts are drafts
for Layer 5 (section 7a). Every figure is printed by `l4e11_power.py` into `l4e11_power.out` ("out N" is its section), which
reads each figure from a generator, a committed netlist, a record's committed output, a filed catalogue reading or a maker's
document, each pinned by sha256; L4-E9's output and its hot-swap draft are read from its commit `3c09b3da` and never retyped.
Classes: MAKER, CATALOGUE, NETLIST, REQUIREMENT, RECORD, INFERRED, CONDITIONAL, ASSUMPTION, and SESSION for a choice this
record takes under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026 that engineering
decisions are the session's.

**The task.** U-04 and D-06 were left open by L4-E9 (`L4-POWER-ARCHITECTURE.md` section 7, fix round at `71486686`); D-09 was
found by L4-E9's final round (`3c09b3da`) and added to this task by the coordinator on 2 October 2026.

## In short

- **U-04, the requirement.** No mandatory requirement names a load state or a wattage for the kit on a source alone, at any
  source voltage (out 1). REQ-015 says the input "runs the kit and charges the pack" and accepts on "Operates and charges
  across 9 to 36 V"; it names neither the load, nor the pack's state, nor where 9 V is measured. PS-IDLE-SPEC enters only
  through REQ-072, an objective. What the mandatory text does ask of a source alone: start the kit and warm a cold-soaked pack
  whose FETs are open (REQ-024 with D-02d, REQ-046, TEST-PLAN E4-O), and carry the kit with the charge held (REQ-077).
- **U-04, the charger.** TI states that the system is powered from the adapter through the charger once CHRG_OK is high (11),
  CHRG_OK's conditions do not name the battery (9.3.4), the converter powers up with no battery condition (9.3.1) and its
  power-up curves are drawn without a battery (Figures 10-4, 10-5); with charge disabled the converter keeps operating
  (9.3.21.5); in HIZ it shuts off (9.3.8). The pack's gauge opens only its discharge FET at CUV (SLUUAQ3A 2.2), so a dead pack
  takes charge through that FET's body diode, at the charger's own 384 mA clamp below 12.3 V at SRN (Table 9-2, 8.5). Not
  stated anywhere held: VSYS's regulation under load steps with no battery (N1), what the converter regulates with charge
  inhibited and no battery (N2, Q-TI-3), and four smaller items (out 2).
- **U-04, the selection (SESSION): arrangement (A), the drawn non-power-path charger kept, made defensible by four rules and
  one resistor.** (B) a charger with a battery FET and (C) a pre-charge path on board P were compared (section 4). (A) needs no
  power part; its rules stop the two holds that cut the source (finding U4-F1), cap the charge through Q2's body diode at
  1.0 A, keep the load inside the source envelope and recover the charger's VSYS_UVP latch. Its bounds: VIN_RAW at 9 V gives 19.7 to
  36.6 W at VBAT, 12 V 34.1 to 47.4 W, 24 V 71.9 to 90.6 W; a dead pack adds at most 4.22 W of charge; a pack self-discharged
  under about 2.4 V a cell holds VSYS under the converters' assumed 10.0 V floor until it precharges.
- **Two 9 V findings on the way (U4-F2, U4-F3).** The hot swap's UVLO turns on at 8.72 / 9.03 / 9.34 V, so at its nominal and
  upper corners a 9.00 V source never starts the entry: R21 to 42.2k (8.14 / 8.42 / 8.71 V), drafted. And H3's knee sits at
  VIN_RAW: a 9.00 V source at the kit's plug, through the kit's own series resistance, settles VIN_RAW at 8.82 V and gives
  8.3 W, not 19.7 W: L4-E5's knee and restart guard are to be re-derived for 9 V at the plug (E11-09).
- **No owner question is forced** (section 5): no approved requirement names a load REQ-015's 9 V must carry, and no cap at
  9 V is independent of the arrangement: F1 admits 59.5 W at VBAT in the hottest air (under PS-TYP's 63.0 W only), 79.8 W cold,
  and a 15 A part with D-06's band re-rated to it would admit 89.6 W.
- **D-06, selected (SESSION): the interconnect rated to F1's whole weak-source envelope, with a resistance floor.** F1's
  0997010 prints no maximum time under 135 % (13.5 A), so every element must carry at least 13.5 A with no time limit; as drawn
  one element is rated 13 A and four state none. Every element is selected at 20 A or more continuous: MIL-DTL-38999 size 12
  contacts (23 A, insert 17-6), a board connector of the XT60 class (30 A rated, 60 A instantaneous), a holder whose maker
  prints 20 A or more, AWG 14 cores whose maker states 20 A or more, board E's copper at 20 A. The heavier lead raises a stiff
  source's current: 1236.9 A at 2.0 m of AWG 14, over F1's 1000 A; with the DC pair's run at least 3.0 m it is 883.5 A.
- **D-09, selected (SESSION): C5 becomes two Murata C0G parts in parallel**, GRM3195C1H104GA05D (100 nF 2 %, LCSC C907944) and
  GRM3195C1H683JA05D (68 nF 5 %, C3847777), 168 nF. The start into VIN_RAW at 43.18 V, now with the 34 uF the hot swap really
  charges, the power limit following VDS and the bias load, takes 3.062 ms at its corners, so the fault time must be at least
  4.593 ms; the pair gives 4.927 to 14.653 ms, and at the maximum the hot-short pulse (0.675 A) sits under Figure 10 at Q7's
  derated case (0.71 A, TI's power law carried 46.5 % past the 10 ms line, CONDITIONAL). The front end adds no load to the
  start: U34 holds it off for 79 ms at least. No 150 nF C0G part is stocked.
- **What stays conditional** (section 9): N1 for U-04 (the only item that could still change the charger, and then first by
  VSYS capacitance); the cable's, holder's and plug's makers' ratings and the contacts' short-time data for D-06; Figure 10
  past 10 ms and board E's copper under Q7 for D-09; 18 downstream items (section 8).

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
| REQ-077 | mandatory | on shore | no | the charge held by CHRG_INHIBIT while the charger carries the kit, a pack present |
| REQ-072 | objective | solar | yes (PS-IDLE-SPEC) | after a permitted pack cutoff the remaining supply carries the loads |

**So**, at 9 V REQ-015 does not mean the full PS-IDLE-SPEC profile: its text names no profile, and the record does not add one.
What the mandatory text asks of a source alone is a start and a pack warm-up with the pack's FETs open, and a charge hold that
leaves the kit carried. This page states, as bounds, which named states each source voltage carries (section 3).

## 2. The charger and the pack with no usable pack (U-04; out 2)

**What SLUSE66A states (MAKER):** no battery MOSFET (p.1); from VBUS the registers, the cell count, then "Converter powers up."
with no battery condition (9.3.1, p.24); power-up curves drawn "2-cell without battery" (Figures 10-4, 10-5, p.89); "When
CHRG_OK goes HIGH, the system is powered from adapter through the charger. When adapter is removed, the system is connected to
battery." (11, p.92); CHRG_OK's conditions are VBUS's window and the faults, not the battery (9.3.4, p.25); DPM cuts the charge
first and then "the system voltage starts to drop" while the battery supplements (9.3.17, p.29); 4S defaults ChargeVoltage
16.8 V, SYSOVP 19.5 V, VSYS_MIN 12.3 V (Table 9-2) and the charge clamped at 384 mA while SRN is under VSYS_MIN (8.5, p.10);
with charge disabled "the converter should keep operating without disturbance" (9.3.21.5, p.34); AUTO_WAKEUP_EN, 0 at POR,
would give a battery under VSYS_MIN 128 mA for 30 min, but only after a host sets it (p.61); HIZ: "converter shuts off"
under 0.4 V on ILIM_HIZ (9.3.8); VSYS under 1.6 V for 2 ms: "shut down and latched off" until a host write (9.3.21.8); "Overall
50-uF effective capacitance on VSYS net is necessary (POSCAP is preferred)" (10.1, p.83).

**What the boards and the pack's image add (NETLIST, RECORD):** board A's strap reads 4S (75.1 % of VDDA), so U3 never sees
"battery removal"; every load is on VSYS with the pack beyond R17; CHG_INHIBIT pulls ILIM_HIZ low (HIZ); SHORE_INHIBIT pulls the
hot swap's UVLO low (input off); board P's gauge has no PCHG FET and its image writes PCHG_COMM 1 (pre-charge through the
charge FET, SLUUAQ3A 4.9 and 14.2.1.1); a CUV trip sets XDSG only (2.2); UTD -9 C sets XDSG and UTC 1 C sets XCHG (4.12); Q2's
body diode is CSD17570Q5B's, VSD at most 1 V (at 50 A) and RthetaJA at most 50 C/W (p.3).

**What follows, by pack state (INFERRED from the rows above):**

| Pack state | VSYS | Charge | What holds it |
|---|---|---|---|
| absent, or both FETs open (below -9 C, SHUTDOWN, a permanent fail) | ChargeVoltage, at most 16.884 V written | none | the voltage loop on SRN with no current in R17 (11, 9.3.1); N1 |
| at CUV, charge FET on | the stack plus VSD, 10 to 11 V | 384 mA while SRN is under 12.3 V (0.038 C a cell, under Samsung's 0.1 to 0.5 C pre-charge range, a lower current with no consequence stated) | the clamp; rule R-b above it |
| self-discharged to the Shutdown Voltage (2.0 V a cell) | 8 to 9 V while it precharges | as above | under A-14's assumed 10.0 V floor: the loads wait (N5) |
| the clamp lifted (SRN at 12.3 V, a stack of 11.3 V or more) before CUV recovers (3.00 V a cell) | rising | ChargeCurrent through Q2's diode: 3.0 A would be 3 W, 150 K over the air | rule R-b: at most 1.0 A, 1 W, 50 K |
| CHG_INHIBIT (HIZ) or SHORE_INHIBIT asserted, the pack unable to discharge | none: the kit stops, its controller dies, the pull-downs release the line, it restarts: a loop | none | rule R-a forbids it |

**Finding U4-F1.** FW-C08 asserts SHORE_INHIBIT "on the bridge's request when the pack reads below 0 C" (and PANEL.md section
10 says the same). With a pack cold-soaked below -9 C both FETs are open, so the hold cuts the very source start REQ-024
requires; with HIZ the same follows (9.3.8). CONOPS already holds the H1 charge by the CHRG_INHIBIT bit for this reason.

**Not stated in any held document (named, not inferred):** N1 VSYS's regulation and transient response with no battery under
the kit's load steps; N2 what the converter regulates with CHRG_INHIBIT = 1 or ChargeCurrent 0 and no battery current
(Q-TI-3); N3 whether the charger charges before any host write (Q-TI-2); N4 VSYS's effective capacitance at 16.884 V against
TI's 50 uF; N5 every load converter's minimum input (A-14, R-49); N6 0-V charging before the gauge's SUV check (Q-TI-7).

## 3. The source envelope and two 9 V findings (U-04; out 3)

U3's delivery to VBAT with no pack (H3's line, L4-E5; U3 0.9733; VBUS20 19.146 V lowest, 20.96 V top; INFERRED):

| VIN_RAW | U3 board current, A | at VBAT, W | L4-E9 |
|---|---|---|---|
| 9 V | 1.057 to 1.793 | 19.7 to 36.6 | 19.9 to 36.6 W (R16's 1 % not applied there) |
| 12 V | 1.832 to 2.323 | 34.1 to 47.4 | up to 47.4 W |
| 24 V | 3.860 to 4.443 | 71.9 to 90.6 | up to 90.6 W |
| 36 V | 4.537 to 4.884 | 84.5 to 99.6 | the window |

| State (plan, at VBAT) | 9 V | 12 V | 24 V | 36 V |
|---|---|---|---|---|
| PS-RED 22.2 W | above the line's minimum only | carried | carried | carried |
| PS-RED with the heater 33.1 W | above the minimum only | carried | carried | carried |
| PS-IDLE-SPEC 42.8 W | not carried | above the minimum only | carried | carried |
| PS-IDLE-SPEC cold, heater on 45.46 W | not carried | above the minimum only | carried | carried |
| PS-TYP 63.0 W | not carried | not carried | carried | carried |
| the cold warm-up 71.06 W (CONOPS 4c) | not carried | not carried | carried | carried |

A dead pack's charge adds at most 0.384 A x 11 V = 4.22 W, which DPM gives up first. A pack able to discharge supplements any
shortfall (L4-E9 section 3); these bounds are for the pack that cannot.

**Finding U4-F2, the entry's UVLO against 9 V.** UVLOTH 2.45 / 2.5 / 2.55 V and UVLOHYS 12 / 21 / 30 uA (SNVS452G p.5) with
R20 100k and R21 38.3k at 1 % turn the entry on at 8.72 / 9.03 / 9.34 V: at its nominal and upper corners a 9.00 V source
never starts it (NOT MET as drawn). **SESSION: R21 42.2k 1 %** (draft `apply_gen_sch_e_uvlo.py`): on at 8.14 / 8.42 / 8.71 V,
0.29 V under 9.00 V at its maximum with no current flowing; off at 5.11 / 6.32 / 7.53 V, under H3's knee and the restart
guard. *Reversed by:* a measured UVLO trip that leaves the band, or REQ-015's floor restated.

**Finding U4-F3, where the 9 V is measured.** REQ-015 names no point; H3's knee is on VIN_RAW (zero at 8.75 V, the line from
9.00 V). Between the kit's plug and VIN_RAW lie the kit's cable and lead (L4-E9: 0.0899 ohm at 20 C) and board E's series parts
(L2's series DCR 0.0302 ohm, R19, Q1 and Q7 at 4.9 mOhm each at 25 C, F1's typical cold 7.42 mOhm: 0.0575 ohm; MAKER,
NETLIST; hot values higher, not counted). A 9.00 V plug then settles VIN_RAW at 8.819 V and U3 at 0.426 A, 8.3 W at VBAT
nominal against 30.2 W at VIN_RAW 9 V; with D-06's interconnect (0.1155 ohm) 8.833 V and 10.0 W. **SESSION: the design basis
for REQ-015's 9 V is the kit's plug**, the most demanding reading, which satisfies every other. Its consequence is L4-E5's:
the knee's top at most 8.318 V of VIN_RAW (8.465 V with D-06's interconnect) and the restart guard re-derived below it with
L4-E5's 0.1 V margin (E11-09, the Layer 4 coordinator's). This record does not draft it: it re-derives an accepted record's
network.

## 4. The comparison and the selection (U-04; out 4)

| | (A) the drawn non-power-path charger, with rules | (B) a charger with a battery FET (NVDC power path) | (C) a pre-charge path on board P (PCHG FET and resistor) |
|---|---|---|---|
| Power at 9, 12, 24 V with no usable pack | section 3's envelope; the same in (B) and (C), whose limit is the source path, not the charger | the same | the same |
| Start from a dead pack | the source carries the kit at once when the pack is absent or both FETs open; a pack at CUV holds VSYS at 10 to 11 V; one self-discharged to 2.0 V a cell holds it at 8 to 9 V, under the converters' assumed floor, until it precharges | VSYS regulated at VSYS_MIN whatever the pack; the pack precharged through the battery FET | VSYS stays at ChargeVoltage while the resistor precharges the pack |
| Protection interaction | the gauge's window acts on the charge FET as now; rules R-a and R-b keep the holds off the source and the diode under 1 W | a series FET in the pack path, a new single point on the battery-only path, its own fault list | the PCHG FET short leaves a resistor path round both protection FETs; the resistor in the sealed case |
| Parts and board changes | none of power; R21 (U4-F2, needed by every option) | U3 replaced, a battery FET, every L4-E4 to L4-E8 setting on the charger re-derived (IIN_HOST, H3 on ILIM_HIZ, R11, R12, the bank) | a P-FET, a power resistor and its land on board P; PCHG_COMM 0 in the image |
| Energy cost | none | 0.324 W per mOhm at 18 A; 8.8 mW per mOhm at PS-IDLE-SPEC | 8.98 W in the resistor at 2.0 V a cell for 0.1 C (8.63 ohm), 3.38 W for the charger's 384 mA (22.9 ohm) |
| What still depends on a maker | N1 (TI); N2 avoided by R-a; N3 for a pack below the controllers' floor; Q-TI-7 | the new charger's sheet: the one NVDC charger held, TI's BQ25798, states the regulation (p.1) but its integrated battery FET carries 6 A RMS and 10 A for 1 s (p.7), under the pack's 18 A peak, so an external-FET part is needed, of which no sheet is held | Q-TI-7; the resistor's pulse rating |

Considered and not compared: a source-fed keep-alive rail for the controllers. It keeps the controllers up but does not run the
kit, which still hangs on VSYS; whether the controllers' own converters reach down to a dead pack's VSYS is E11-08's reading.

**Selected (SESSION): (A).** *Why:* it is the only arrangement with no power part added; TI's own text covers its two central
behaviours (the system powered through the charger with no battery, 11 and Figures 10-4 and 10-5; the dead pack charged at a
clamped current, Table 9-2 and 8.5); its two hazards are rules, not topology (U4-F1's holds, R-a; Q2's diode, R-b); (B)
reopens five accepted records on a part whose sheet is not held, and (C) puts 3.4 to 9.0 W into the sealed case to buy a
faster start from a pack nobody requires the kit to start from at once. **Its bounds** are section 2's table and section 3's
envelope. **Its cost, stated:** a pack self-discharged under about 2.4 V a cell holds VSYS under 10 V until it precharges at
384 mA; the time is not computable from held data (the 35E's capacity between 2.0 and 2.4 V is not printed) and is measured by
E11-06. **Reversed by:** TI's answer to N1 (E11-05) or E11-06 showing VSYS does not hold under the kit's load steps with no
battery; the first remedy is VSYS's capacitance (TI's 50 uF effective, POSCAP preferred, E11-07), and only if that fails does
(B) return.

**The rules (SESSION; drafts in section 7a):**

- **R-a.** While the pack cannot discharge (the gauge reports XDSG, the pack is absent, or both FETs are open), never assert
  SHORE_INHIBIT or CHG_INHIBIT; the cold and "no charge" holds then act by the gauge's own window (UTC, T1, CHGIN), which already
  keeps the charge FET open, and the charger is left enabled. While the pack can discharge, the holds act by the CHRG_INHIBIT
  bit, as REQ-077 does. SHORE_INHIBIT stays for the operator's "inputs off" and the water-on-floor isolation, with a warning
  first when the pack cannot carry the kit.
- **R-b.** ChargeCurrent at most 1.0 A while U3's own SRN reading is under 14.0 V or the gauge reports XDSG or PRECHARGE. With
  VSD at most 1 V that covers a cell up to 0.25 V under the stack's average without the gauge's report (the panel controller
  reaches the gauge only through a running module); Q2's diode then dissipates at most 1 W. Beyond it RT1's PTC beside the FETs
  turns them off (a permanent fail, safe, named).
- **R-c.** While the pack cannot discharge, the bridge keeps the kit's load under the envelope's minimum at the measured
  VIN_RAW (section 3), shedding in CONOPS 4c's order; on a source-only brown-out the charger may latch off (9.3.21.8): the host
  clears the fault bit when it can, or the operator re-plugs the source.
- **R-d.** The image keeps PCHG_COMM 1 and the SUV check (PRIMARY-CONFIGURATION.md), with Q-TI-7 open.

## 5. Is an owner question forced? (out 5)

No. The brief's test is whether REQ-015 as written cannot be met at 9 V by any arrangement because the source's own capability
(the fuse, the entry, the cable) caps the power below the required load. REQ-015 names no required load (section 1), and no
other mandatory requirement names one for a source alone. Nor is there a cap independent of the arrangement: F1 0997010 at
its 80 C column (7.3 A, the hottest air 62.1 C) admits 59.5 W at VBAT, under PS-TYP's 63.0 W and over every other state of
section 3; at its 0 C column (9.8 A) 79.8 W, over the cold states (the cold warm-up 71.06 W); D-06's interconnect at 20 A
admits 162.9 W; a 15 A MINI 58 V (its 80 C column 11 A) with D-06's band re-rated to it would admit 89.6 W; the entry's limit
and H3's line are settings. REQ-015 states no source current capability, so every figure takes the source as holding its
voltage (named). The 9 V shortfalls of section 3 (PS-IDLE-SPEC and above at 9 V) are a design envelope of H3's settings,
stated, not a requirement conflict.

## 6. D-06: the vehicle-entry interconnect (out 6)

**The band (MAKER, the held 0997 sheet p.3):** 110 %: at least 360000 s; 135 %: 0.75 to 600 s; 200 %: 0.15 to 5 s; 350 %:
0.08 to 0.5 s; 600 %: 0.03 to 0.1 s. No maximum time is printed under 135 %, so a source under 30 A (ECSS 6.17.3c's three
times) can leave **up to 13.5 A with no stated limit**, then from 13.5 A at most 600 s, from 20 A at most 5 s, from 35 A at most
0.5 s, from 60 A at most 0.1 s (INFERRED). PWR-003 asks the clearing characteristic to sit below the damage characteristic of
the weakest element downstream.

**The elements in that loop, as drawn (NOT MET):** J_DCIN's VH contact with the drawn AWG 18 lead on the standard header (VH
prints 10 A at AWG 16 standard and 7 A at AWG 18 shrouded only: none stated); the D38999 size 16 contact, insert 13-4 (13 A,
Amphenol's test current); F1's holder Keystone 3568 (the catalogue page prints UL ratings of 15, 20 and 30 A for other MINI
clips and holders and none for the 3568); the DC lead, Lapp OLFLEX ROBUST 210 4 x 1.0 or Alpha Wire 25064 (no current rating in
either sheet); the inside lead, 500 mm of AWG 18 (no part, no rating); board E's input bands (10 A declared).

**The options:**

| Option | What it does | Verdict |
|---|---|---|
| (i) rate the interconnect to the whole band | every element at least 13.5 A with no time limit; at 20 A continuous the 600 s band is covered too | **selected (SESSION)** with a resistance floor (below) |
| (ii) a fuse and protection change | a smaller MINI 58 V: the 7.5 A part's 80 C column is 5.1 A, under the entry's 6.15 A (nuisance); lowering the entry's limit under 5.1 A puts it under H3's 4.629 A at 9 V and costs U-04's 9 V envelope; and its own band (10.1 A without limit) still passes the unrated cable | rejected: it fails no-nuisance or 9 V, and leaves the cable unrated |
| (iii) the source's capability stated in REQ-015 (ECSS 6.17.3c) | a requirement change, the owner's | not needed: (i) resolves it in design |

**Selected part classes and their ratings (SESSION; the exact parts Layer 7's and Layer 8's):**

| Element | Selected class | Rating, from the maker's sheet |
|---|---|---|
| receptacle and plug contacts | MIL-DTL-38999 size 12; insert 17-6 (six size 12: DC and solar pairs on four, the two unassigned between power and return, the ECSS 6.11.3a screen), or 13-26 (two size 12 and six 22D) with the solar pair moved to rated contacts elsewhere | 23 A test current (Amphenol p.28); arrangements p.5 |
| J_DCIN | a board connector of the XT60 class, of the gender opposite J_BATT's so the pack lead cannot mate it, or soldered lead lands | 30 A rated, 60 A instantaneous, 12 AWG recommended (Amass V1.2) |
| F1's holder | a MINI 297/997 holder whose maker prints at least 20 A | the 3568 prints none |
| DC lead and inside lead | cores of 2.081 mm2 (AWG 14, the size 12 crimp barrel's range) whose maker states at least 20 A continuous each | no sheet held: E11-11, E11-12 |
| board E's copper, J_DCIN to F1 to D10, C4 and Q1 | at least 20 A continuous | a layout constraint, E11-14 |
| F1 | unchanged, Littelfuse 0997010.WXN | 58 V DC, 1000 A at 58 V DC; 7.3 A at 80 C against 6.15 A |

The short-time points against an AWG 14 core are small (adiabatic: 20 A for 5 s 2.31 K, 35 A for 0.5 s 0.71 K, 60 A for 0.1 s
0.42 K, INFERRED); against the size 12 contact they equal its 23 A for 3.78, 1.16 and 0.68 s, inside a continuous rating, but
its short-time limit is not printed (E11-16).

**The stiff source again** (copper alone at -20 C, the source's resistance zero, A-12, at the OVLO maximum 43.18 V; INFERRED):
as drawn 0.07577 ohm, 569.9 A (L4-E9 569.8 A); AWG 14 at 2.0 m 0.03491 ohm, **1236.9 A against F1's 1000 A, NOT MET**; AWG 12
at 3.0 m 1404.8 A, NOT MET; **AWG 14 at 3.0 m 0.04888 ohm, 883.5 A, MEETS**. A heavier interconnect therefore needs a resistance
floor: at least 43.18 mOhm of copper loop at -20 C, which AWG 14 gives from 2.59 m of cable with the 0.5 m lead. **SESSION: the
DC pair's run at least 3.0 m of AWG 14** (the 2 m lead plus 0.3 m tail as assembled today become a 3.0 m run); a shorter or
heavier lead needs a fuse with a larger interrupting rating at 58 V DC, of which no sheet is held. F1's other checks hold: 6.15
A against its 80 C column 7.3 A; the lowest stiff fault at 9 V with the copper at 62.1 C is 133.2 A, 13.3 times the rating,
inside the 600 % row's 0.1 s; the longest start's I2t is 0.554 A2s against 93 A2s. **D-06 is resolved in design**, CONDITIONAL
on the makers' sheets the acceptances name (cable, inside lead, holder, NATO plug, the contacts' short-time data).

## 7. D-09: the hot swap's fault time against its start (out 7)

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
A, m 0.4299) carried past the 10 ms line by 46.5 % and derated to Q7's 94.3 C case by 0.4454 (L4-E9) allows 0.710 A against the
pulse's 0.675 A (MEETS, CONDITIONAL on the power law past 10 ms and on board E's copper under Q7). Sensitivities: a steeper law
past 10 ms (m 0.5) 0.691 A, MEETS; the damp-heat row stacked instead of endurance 4.699 to 15.293 ms and 0.697 A, MEETS; TI's
own basis (typical values) 7.906 ms against 2.382 ms. The DC line derated (0.271 A) is under the pulse; the pulse ends at the
fault time, so no steady rating is asked of it. *Reversed by:* a measured start (E11-17) longer than 3.285 ms at 43 V, or a
measured fault time outside the band; the alternatives then are a higher power limit (a shorter start against a larger pulse)
or a Q7 with a larger SOA. **D-09 is resolved in design**, CONDITIONAL as stated.

## 7a. The interface and firmware drafts (text, for Layer 5 and the firmware owner)

These replace rows of `HW-FW-CONTRACT.md` and a paragraph of `PANEL.md`; this record does not edit either.

- **FW-C08 (SHORE_INHIBIT), proposed behaviour:** "Boot low. Asserted only on the operator's 'inputs off' and on the
  water-on-floor isolation, never for a temperature or 'no charge' hold. When the pack cannot discharge (the gauge's XDSG, no
  pack, or both FETs open) the bridge first warns that asserting it removes the kit's supply." (as written: "Boot low; assert on
  the bridge's request when the pack reads below 0 C and clear above 3 C, or when the operator sets 'no charge'")
- **FW-A14 (CHG_INHIBIT, HIZ), proposed behaviour:** "Held low (charger enabled) at power-up; asserted only by firmware, and
  never while the pack cannot discharge." (as written: "Held low (charger enabled) at power-up; asserted only by firmware")
- **PANEL.md section 10, proposed sentence** in place of "The bridge asks the controller to assert it when the pack temperature
  (...) is below 0 C, when the operator sets 'no charge', and clears it with hysteresis (charge again above 3 C).": "The bridge's
  cold and 'no charge' holds act by the charger's CHRG_INHIBIT bit while the pack can discharge, and by the pack gauge's own
  charge window alone while it cannot (the charger left enabled); they clear with hysteresis (charge again above 3 C). The
  bridge asks the controller to assert SHORE_INHIBIT only for 'inputs off' and the water-on-floor isolation."
- **New firmware rows:** R-b (ChargeCurrent at most 1.0 A while U3's SRN reading is under 14.0 V or the gauge reports XDSG or
  PRECHARGE); R-c (the source-only shed and the VSYS_UVP recovery); R-d (the image's PCHG_COMM 1 and SUV check kept).

## 7b. The CONOPS statement (draft, for the CONOPS owner)

"With no usable pack (absent, at its cutoff, or cold-soaked with its FETs open) the kit runs from its vehicle or shore input
within the source envelope: about 20 W at 9 V, 34 W at 12 V and 72 W at 24 V on its bus at the least (9 V at the input
plug once its threshold is re-derived, E11-09). A pack self-discharged under about
2.4 V a cell holds the system node under the converters' floor while it pre-charges, so the kit's loads wait for it. A
brown-out on the input alone may latch the charger off until the input is re-plugged."

## 8. The downstream items (out 8)

An owner and an acceptance close the assignment, not the item.

| ID | Kind | Owner | Acceptance |
|---|---|---|---|
| E11-01 | implementation | Layer 8 board E generator owner | `apply_gen_sch_e_uvlo.py` applied after L4-E9's `apply_gen_sch_e_hotswap.py`; the netlist carries R21 42.2k 1 % with an LCSC code; the UVLO band recomputed reads 8.14 to 8.71 V rising |
| E11-02 | implementation | Layer 8 board E generator owner | `apply_gen_sch_e_timer.py` applied; the netlist carries C5 (C907944) and C121 (C3847777) on HS_TIMER; the fault time recomputed from the fitted parts reads 4.927 to 14.653 ms |
| E11-03 | interface | Layer 5 interfaces | FW-C08, FW-A14 and PANEL.md section 10 restated as section 7a; REQ-046's hold still clears above 3 C |
| E11-04 | firmware | firmware owner | rules R-a to R-d implemented and checked on the bench (E11-06) |
| E11-05 | evidence | Layer 6 components | TI's answers filed: Q-TI-3 restated (VSYS's regulation with no battery current possible, under a 5 A load step, and with CHRG_INHIBIT = 1) and Q-TI-2; N1 to N3 re-judged |
| E11-06 | test | prototype bench | R-85 extended: 9 V at the plug, 12 and 24 V, the pack absent, at CUV and cold-soaked: the kit boots and runs within the envelope; VSYS and its step response; the 384 mA clamp; Q2's case at 1.0 A; the latch recovery by a re-plug |
| E11-07 | analysis | Layer 9 pre-layout analysis | VSYS's effective capacitance at 16.884 V from the makers' DC-bias curves at least 50 uF, else a polymer capacitor added |
| E11-08 | evidence | Layer 9 pre-layout analysis | every load converter's and the controllers' minimum input against 10.0 V (A-14, R-49) and 8.0 V |
| E11-09 | analysis | Layer 4 coordinator | L4-E5's knee and restart guard re-derived for 9 V at the kit's plug (knee top at most 8.318 V drawn, 8.465 V with D-06's interconnect); the plug's 9 V envelope re-run at 19.7 W or more |
| E11-10 | implementation | Layer 7 mechanical | the DC receptacle and plug on size 12 contacts (17-6, or 13-26 with the solar pair elsewhere); the plate cut-out checked against CASE-MARGINS 3.3 |
| E11-11 | implementation | Layer 7 mechanical | the DC lead: AWG 14 cores with a maker's rating of at least 20 A, the DC pair's run at least 3.0 m (a copper loop of at least 43.18 mOhm at -20 C with the inside lead), the NATO plug with a maker's rating of at least 20 A; sheets filed |
| E11-12 | implementation | Layer 7 mechanical | the inside lead (AWG 14, at least 20 A) and J_DCIN at least 20 A (XT60 class, gender opposite J_BATT's, or soldered lands); board E's generator names the part |
| E11-13 | implementation | Layer 8 board E generator owner | F1's holder with a maker's rating of at least 20 A; its sheet filed |
| E11-14 | layout | Layer 9 pre-layout analysis | board E's copper from J_DCIN through F1 to D10, C4 and Q1 at 20 A continuous |
| E11-15 | implementation | Layer 8 board E generator owner | `pcb_energy_chain.yaml` SHORE_INPUT restated with L4-E9's R-95: conductor 20 A, protects the interconnect, prospective high 883.5 A |
| E11-16 | evidence | Layer 6 components | the size 12 contact's and the board connector's short-time data at 35 A for 0.5 s and 60 A for 0.1 s, or F1's total clearing I2t (R-115) against them |
| E11-17 | test | prototype bench | R-118 with the fitted C5 pair at 43 V: the fault time inside 4.927 to 14.653 ms and the start inside 3.062 ms |
| E11-18 | document | CONOPS owner | section 7b's statement in CONOPS |

## 9. What stays conditional, and the decisions this record takes

**Conditional or open (named):** U-04: N1 (VSYS under load steps with no battery: TI and E11-06; the only item that could
still change the charger), N2 (avoided by R-a; REQ-077's hold with a pack present is carried by the pack either way), N3, N4
(E11-07), N5 (E11-08), N6 (Q-TI-7); the plug's 9 V (E11-09); a deeply discharged pack's wait (E11-06); REQ-015's unstated source
capability. D-06: the cable's, inside lead's, holder's and NATO plug's makers' ratings (E11-11 to E11-13), the contacts' short-time
data (E11-16), F1's total clearing I2t (R-115), the plate's fit for shell 17 (E11-10). D-09: Figure 10 past 10 ms, board E's
copper under Q7 (RthetaJA), the X7R stack taken for every start capacitor (an ASSUMPTION, as L4-E9), Murata's sheet as fetched
(generated on request).

**SESSION decisions:** (1) U-04: arrangement (A) with rules R-a to R-d; (2) R21 42.2k 1 % (U4-F2); (3) REQ-015's 9 V taken at the
kit's plug as the design basis (U4-F3); (4) R-b's 1.0 A and 14.0 V; (5) D-06: every element of the interconnect at 20 A or more
continuous, with the classes of section 6; (6) the DC pair's run at least 3.0 m of AWG 14; (7) insert 17-6 preferred to 13-26;
(8) J_DCIN of the gender opposite J_BATT's; (9) D-09: C5 and C121, at most two parts. Each carries its reason and reversal
above.

**The gate's view (for the coordinator, not decided here):** U-04 moves from "unresolved by the held documents" to a selected
arrangement whose feasibility rests on TI's stated behaviour, CONDITIONAL on N1 with a named first remedy; D-06 and D-09 move
from open defects to resolutions in design, CONDITIONAL on the makers' sheets and bench rows named.

## 10. Assumptions

| ID | Assumption | Impact if wrong | Verification |
|---|---|---|---|
| A11-1 | Copper at 0.01724 ohm mm2/m and 0.00393 /K, AWG 14 2.081 mm2, the source's resistance zero (as L4-E9's A-12) | the stiff-source current lower, never higher | E11-11 (the maker's cross-section) |
| A11-2 | The budget's battery-terminal watts taken at VBAT | a small overstatement of each state | E11-06 |
| A11-3 | Q2's VSD at most 1 V at 1 A, from its 50 A row; board P's copper giving 50 C/W | Q2's rise under R-b | E11-06 |
| A11-4 | The start's capacitors at the Yageo X7R rows stacked, for parts of other makers too | the start's corner | E11-17 |
| A11-5 | Each VIN_RAW load path bounded by its resistor alone | the start a little shorter in fact | E11-17 |
| A11-6 | Board E's series resistance at 25 C maxima with F1 typical | the plug's 9 V figure a little high | E11-09, E11-06 |
| A11-7 | The power law between Figure 10's 1 and 10 ms lines carried past 10 ms (as L4-E9) | the timer's maximum against the SOA | E11-17, R-118 |

Not claimed: nothing here is verified, built or measured; software tests establish this record's own behaviour only.
