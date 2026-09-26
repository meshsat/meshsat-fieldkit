# Board P and the 4S3P pack: the temperature thresholds, coordinated

MeshSat field kit V2, MESHSAT-1357, round 8, stream r8bat, 26 September 2026. **Prototype design: no pack, board P or
kit has been built, programmed, heated or measured; every threshold below is a requirement on a golden image that does
not exist yet or a figure read from a maker's document, and every behaviour is NOT_YET_TESTED.** This page executes
finding B of the second checkpoint review (`v2/docs/reviews/2026-09-26-second-checkpoint-review.md` section 2 B): "The
review must establish coordinated thresholds, tolerances, sensor placement/lag, operating mode, and behavior when the
primary path fails." It is written for the qualified battery-and-protection review of D-09 and is not sign-off.

Labels, as in `PROTECTION-ARCHITECTURE.md`: **VERIFIED** = read in the named document or file; **INFERRED** = derived
from verified facts, with the step shown; **TBD** = not known, with what it moves. Decisions marked "taken by the
session" were taken under the owner's standing rule of 26 September 2026 and can be reversed; each says how.

## 0. The answers in short

1. **The ladder** (section 4). Every protective threshold on a cell limit now sits INSIDE that limit by its own error
   budget, instead of on it: the gauge's charge over-temperature at 44.0 C (limit 45 C), its discharge over-temperature
   at 57.5 C (limit 60 C), its charge under-temperature at 1.0 C (limit 0 C) and its discharge under-temperature at
   -9.0 C (limit -10 C). The charge algorithm's own window sits inside those: **no charge STARTS below T1 (1 C) or above
   T3 (42 C)**, because the charge inhibit (SLUUAQ3A 4.13) holds the charge FET off, with CHGIN = 1, whenever the pack is
   not already charging and its reading is in the High Temp range (T3 to T4) or beyond; and a running charge is
   suspended above T4 (43 C). T3 therefore decides whether a warm kit on shore charges at all. The first draft of this
   page left it at TI's 30 C and described the inhibit as acting only above T4, which misread 4.13: it would have
   refused every charge start above a sensed 30 C (corrected on 27 September 2026, section 5). Above the limits sit the
   permanent functions: the gauge's SOT at 65.0 C, the second level's over-temperature at 62.7 to 77.5 C, the PTC at
   about 110 to 133 C at the FETs. Taken by the session; the budget is arithmetic on published tolerances, and two of
   its terms (the gauge's own measurement error and the gradient to the hottest cell) are TBD until the bench.
   **The ladder is not closed: finding BAT-F20 is OPEN** (the independent check of 27 September 2026, section 11). With
   CHGIN = 1 the same inhibit holds the charge FET Q1 off whenever the pack is NOT charging and its reading is above T3
   or below T1, which includes discharge, so the kit's discharge current then runs through Q1's body diode: about 2 to
   3 W at the one-module reduced load and about 7 W at 10 A, on board P beside F2, R10 and RT1. Its consequences for F2,
   RT1, OTF and the E3-A, E4-O and P12 pass lines are not examined; the options go to the qualified reviewer (Q-P18).
2. **The second level cannot enforce the 60 C cell limit, in any state** (section 8). Its lowest possible trip is
   62.7 C; it is an emergency backstop that retires a pack which has already left its rating. The 60 C and 45 C limits
   are enforced only by the gauge's firmware (with the golden image) and, against the kit's own heat, by the panel and
   bridge firmware; against ambient heat nothing on the kit can enforce them, and the operating envelope and the
   procedures are what keep the cells inside. The circuit that would enforce them in hardware is specified in section 8;
   the session does not add it now and puts it to the reviewer (Q-P15).
3. **The +71 C storage question** (section 9). Four options are set against the product requirement. Recommended and
   taken by the session: every qualification margin runs in the configuration of the state it represents (storage with
   the pack out, transport and use with the pack fitted), and the exposures with the pack fitted are run at the cells'
   own rated limits. **The states are session text, not an owner ruling:** the owner approved on 6 September 2026 that a
   whole-kit test plan be written (item 16e, at 23:52); the session wrote its states within the hour (7 September,
   00:40, `2e33773b`), and the ConOps took them on 25 September.
   `OPERATING-ENVELOPE.md` section 4, also session text, reads as a kit stored with its pack; section 9 states that
   tension and the reading taken. **Two levels cannot be run in any configuration the product has:** the +55 C
   operating margin and E5's +60 C humidity dwell, at which the fitted cells would pass their maker's +60 C and no ConOps
   mode runs the kit without its pack. They run as stated test deviations with the cells kept out of the heat, and the
   product-level result is recorded, not hidden by them: **the kit with its own pack cannot meet those margins (finding
   BAT-F19, section 9a).** `v2/docs/TEST-PLAN.md` is written accordingly (sections 1, 2, 6 and 7).
4. **The fuse F2** (section 10, `FUSE-INTERPRETATION.md` section 1.1). Its suitability is not concluded: its local hot
   condition and its current behaviour are two open items, each with the evidence that closes it.
5. **The charger with a crashed host** (`CHARGER-STATE-SEQUENCE.md` section 6). "Charges safely" is not a result: it is
   restated as the obligations the design must demonstrate before that sentence may be written.

## 1. What is protected: the limits

| Limit | Value | Source (VERIFIED) |
|---|---|---|
| Cell charge temperature | 0 to 45 C at the cell surface | Samsung INR18650-35E Ver. 1.1 (`samsung-35e-orbtronic.pdf`) 3.12; the 2016 Version No. 1.0 (`samsung-35e-akkuzentrum.pdf`) 3.15 gives the same figures as ambient |
| Cell discharge temperature | -10 to 60 C at the cell surface | the same; Version 1.0 note (*2): "Discharge OTP(over temp. protection) should not be over 60'C of the cell surface temperature. Protection set should be based on the location of the cell surface with the highest temp increase part of the battery pack." |
| Cell storage | 1 year -20 to 25 C, 3 months -20 to 45 C, 1 month -20 to 60 C (Ver. 1.1 3.13); 1 year 0 to 23 C, 3 months 0 to 45 C, 1 month 0 to 60 C (Version 1.0 3.16); both at the ex-factory 30 % charge | as named; which revision governs the cells bought is TBD (BAT-F09) |
| The cell maker's own recovery tests at 60 C | "Capacity after storage for 20days at 60°C after the Standard charged ... Capacity recovery(after the storage) ≥ 3,183mAh (95% of Standard Discharge Capacity)" (Ver. 1.1 7.10); 30 days at 60 C, "≥ 2,680mAh (80% of Rated Discharge Capacity)" (Version 1.0 3.12 and 7.8) | as named: the maker's survive-and-recover line at its own top storage temperature, used as a pass line in section 9 |
| The cell maker's prohibition | "Don't leave, charge or use the battery in a car or similar place where inside of temperature may be over 60°C." and "Store the battery at temperature below 60°C" | Ver. 1.1, "Environmental misusage" and the handling list after it (PDF pages 16 and 17) |
| Chemical fuse F2, operating | -20 to +60 C; no current derating published | Eaton ELX1135 page 4 (`eaton-scf9550-elx1135.pdf`) |
| Protection FETs Q1, Q2 | TJ -55 to 150 C | TI SLPS471D (`ti-csd17570q5b.pdf`), absolute maximum ratings |
| Gauge U1 and second level U2 | TA -40 to 85 C recommended | SLUSC67B 6.3 (`ti-bq4050.pdf`); SLUSEG7D 6.3 (`ti-bq77207.pdf`) |

The cell limits are at the **cell surface** and at the **hottest** cell (the Version 1.0 note). Every threshold below
is judged against that point, which no sensor on this pack reads directly: section 2 says where each sensor is, and
section 3 carries the distance as an error term.

## 2. The sensors: placement, thermal lag and when each is read

| Sensor | Part and placement | Thermal lag | Read when | Feeds |
|---|---|---|---|---|
| TS1 to TS4 (J_TS) | four Semitec 103AT-2, one per series group, "taped to the middle cell of its three" (`gen_sch_p.py:214`, VERIFIED); which group is hottest depends on the pack's place in the east pocket (TBD, pack build) | "approx. 15" s thermal time constant for the AT-2, "Measured with sensor suspended in mid-air" (Semitec P12-13, VERIFIED); taped to a cell the coupling is conductive, so 15 s is an upper bound (INFERRED); Murata's NXRT15XH103, the documented alternative (`pcb_pack_protection.yaml` R10 row), states 4 s (`murata-nxrt15xh103fa1b.pdf`, VERIFIED) | NORMAL: "voltage, current, and temperature readings every 250 ms ... status decisions at 1-s intervals" (SLUUAQ3A 5.2); SLEEP: every Sleep Voltage Time, 5 s by default (5.3.1, 0x4424); SHUTDOWN: not read (5.4) | the gauge's Temperature(), the maximum of the four with DA Configuration[CTEMP] = 0 (2.7): OTC, OTD, UTC, UTD, SOT, the charge algorithm's ranges, the open-thermistor PF; and, through the SMBus, the kit's firmware controls |
| U2's own NTC (J_TS2) | one Semitec 103AT-2 through R34 270 ohm with R33 18 kohm at TS, "taped to the cell expected hottest" (`SECONDARY-OT-DECISION.md` section 4); which cell that is: TBD, pack build | the same 15 s upper bound; then tOT_DELAY, 4 s typical with a delay drift of -10 to +10 % over temperature (SLUSEG7D 6.6, VERIFIED) | whenever the cells power U2, SHUTDOWN included (2 uA, SLUSEG7D 6.5); the TS bias is pulsed and its timing is not published (Q-TI-1) | U2's OT: COUT and DOUT |
| RT1 | Murata PRF15BB103RB6RC chip PTC, 0402, beside Q1 and Q2 on board P (`gen_sch_p.py:228-244`) | not published (TBD); it follows the board copper near the FETs, not the cells | always: "This protection also works in SHUTDOWN mode" (SLUUAQ3A 3.15); tPTC(DELAY) 40 to 145 ms (SLUSC67B 6.23) | the gauge's hardware PTC trip: FETs off, PTC permanent fail |
| The gauge's die | U1's internal sensor; disabled in the image of cycle 3 (Temperature Enable 0x1E), which left no FET-temperature source at all | the board's own | as TS1 to TS4 | proposed here as the FET temperature (section 4, row OTF): Temperature Enable 0x1F, Temperature Mode 0x01 |
| Inside air and module temperatures (context) | the BME688 on board E and the TMP117 under the coolers on board B (`POWER-THERMAL.md` section 9.3) | the air's | while the sensor controller and the bridge run | the kit's controls C1 and C2; no pack protection reads them |

What no sensor reads: the hottest cell's surface as such, F2's body, and the air around the pack. The first is a
gradient term in section 3 and a bench reading in `TEST-PLAN.md` section 7 (P14); the second is `FUSE-INTERPRETATION.md`
section 1.1's first open item.

## 3. The error budget of the gauge's temperature thresholds

A threshold protects a limit only if the cell can never be past the limit when the threshold has not yet acted. So each
threshold is the limit less every way the gauge's reading can lag or read on the safe side of the truth (reading LOW on
the hot side, HIGH on the cold side). Computed by a stdlib script with its output, proposed for filing as this packet's
`evidence/thermal_budget.py` and `evidence/thermal_budget.out` (the round-8 stream could not write `evidence/`; the
integrator files them from its drafts and adds their rows to `MANIFEST.md`). INFERRED arithmetic on the published figures
named:

| Term | Basis (each input labelled) | OTD, limit 60 C | OTC, limit 45 C | UTC, limit 0 C | UTD, limit -10 C |
|---|---|---|---|---|---|
| Thermistor interchangeability | 103AT-2 R25 +-1 % and B25/85 3435 K +-1 % (VERIFIED, Semitec P12-13), added in the worse direction, at the table's slope | 0.71 K | 0.51 K | 0.48 K | 0.56 K |
| The gauge's pull-up drift | RNTC(DRIFT) -360 to -200 ppm/C (VERIFIED, SLUSC67B 6.22), counted from 25 C; trimmed at "factory calibration" (SLUUAQ3A 11.2.1.6.13), whose temperature TI does not state: an ASSUMPTION, TBD | 0.40 K | 0.21 K | 0.21 K | 0.28 K |
| Sensor lag | the 15 s time constant (VERIFIED, an upper bound, section 2) times a heating rate that is INFERRED: 3.2 K per minute, the 12 cells' adiabatic rise at the chain's declared 18 A peak (`POWER-THERMAL.md` section 7.2), computed on 600 g of cells, the Samsung sheet's maximum of 50 g each (VERIFIED, Ver. 1.1 3.10), at 0.8 J/gK, a specific heat INFERRED there ("no Samsung figure"). **It is not the fastest rate**: the sheet publishes no minimum mass, so lighter cells heat faster (the paragraph below). On charge, the cells' own 0.72 W of charge I2R into the same 600 g at 0.8 J/gK (the same page, section 9.2; INFERRED) | 0.80 K | 0.02 K | 0.02 K | 0.02 K |
| Detection | the 1 s decision interval plus the 2 s delay (VERIFIED, SLUUAQ3A 5.2 and 14.9.12 to 14.9.16), at the same INFERRED rate | 0.16 K | 0.00 K | 0.00 K | 0.00 K |
| **Sum of the published terms** | | **2.07 K** | **0.75 K** | **0.71 K** | **0.86 K** |
| The gauge's own ADC and polynomial fit | not published | TBD | TBD | TBD | TBD |
| Sensed cell to hottest cell surface | the pack's thermal layout | TBD | TBD | TBD | TBD |
| **Threshold at most (hot) or at least (cold)** | limit less the published sum | 57.9 C | 44.2 C | 0.7 C | -9.1 C |
| **Taken (0.1 C resolution, rounded inward)** | | **57.5 C** | **44.0 C** | **1.0 C** | **-9.0 C** |

**The heating rate and the cells' mass (INFERRED; corrected on 27 September 2026, when the independent check of this
round found the rate shown as VERIFIED and called the fastest).** The lag and detection terms scale with the heating
rate, and the rate with the inverse of the cells' mass, which the maker bounds only from above. `POWER-THERMAL.md`
section 7.2 says so of its own figure: "The sheet gives only a maximum mass, so this is the smallest rise it allows."
The thresholds survive it on the published terms: OTD keeps 0.43 K in hand (57.93 C less 57.5 C), which absorbs the
18 s of lag and detection up to 4.6 K per minute, that is cells down to about 35 g each at 0.8 J/gK (34.6 g,
`thermal_budget.out`); OTC's charge-side terms stay under 0.03 K at any plausible mass. The 35E's real mass is weighed
at the pack build and asked of the supplier (Q-S2), TBD. The same 0.43 K is all the two TBD terms below have as well, so
the three are judged together: whatever they need beyond it comes off OTD.

**How the two TBD terms close.** At commissioning, each External Temp Offset (SLUUAQ3A 11.2.1.4, 0.1 C units) is set
against a reference thermometer at room temperature, which removes the static part of the ADC and pull-up error at that
point. On the bench (`TEST-PLAN.md` section 7, P14) a thermocouple on every one of the twelve cells is logged against
TS1 to TS4 and U2's NTC in a slow chamber ramp and during the hot acceptance run E3-A: the largest difference between
the hottest cell surface and the gauge's Temperature() is the gradient term. **If the measured gradient plus the
residual ADC error exceeds the 0.4 K OTD keeps in hand (57.9 C less 57.5 C), OTD comes down by the excess; the same for
OTC (0.2 K in hand).** Until then the thresholds are PROVISIONAL.

**Taken by the session under the owner's standing rule of 26 September 2026:** the four thresholds above, and the rule
that no protective threshold on a cell limit sits on the limit itself. The alternative (the cycle-3 image: 45.0 C and
60.0 C, the limits themselves) lets the hottest cell pass the maker's limit by the whole budget before the gauge acts,
which is exactly what the Version 1.0 note asks a pack designer not to do. Cost: the charge window is 1 K narrower at
each end, a charge starts only up to 42 C (T3, section 5), and discharge stops 2.5 K earlier; `POWER-THERMAL.md`'s ambient ceilings for charge and discharge move down by
about the same (its owner re-derives them; a note to that owner this round). Reversed by: a measured budget smaller than the published one.

## 4. The coordinated thresholds (the ladder)

"True temperature at the sensed cell" = the threshold widened by the published budget of section 3, both edges; the
TBD terms of section 3 widen it further. Rows run from the coldest threshold to the hottest; the kit's firmware controls
are included because they act first, and are marked as controls, not protections.

| # | Layer | Device and setting | Sensor | Threshold, delay | True temperature at the sensed cell when it acts (INFERRED) | Action | Recovers? | Active in | Needs the image? |
|---|---|---|---|---|---|---|---|---|---|
| L1 | primary | U1 UTD (2.12) | TS1 to TS4, max | -9.0 C, 2 s; recovery -4.0 C | -9.8 to -8.5 C (no discharge below -9.8 C) | discharge FET off (unconditional) | yes | NORMAL, SLEEP; discharge and relax | yes (value) |
| L2 | primary | U1 UTC (2.11) and charge algorithm T1 (4.2, 14.4.1.1) | the same | 1.0 C, 2 s, recovery 5.0 C; T1 1 C, hysteresis 1 C | 0.3 to 1.5 C (no charge below 0.3 C) | charge FET off (UTC unconditional; the T1 range with CHGSU and CHGIN = 1, 4.13, 4.14). OPEN, BAT-F20: with CHGIN = 1 the T1 range also holds the charge FET off while the pack DISCHARGES below T1, so the discharge current runs through Q1's body diode | yes | NORMAL, SLEEP; charge (and, through CHGIN, discharge: BAT-F20) | yes |
| L3 | kit control | panel and bridge hold on charge below +3 C, heater mat first below -10 C (`PANEL.md` section 10; FW-A13) | the gauge's readings via the sensor controller | +3 C | as L2 plus the SMBus path | the host does not start a charge | yes | kit powered, sensor controller alive | no (firmware) |
| L4a | primary | U1 charge inhibit at T3 (4.2, 4.13, 14.4.1.5) | TS1 to TS4, max | 42 C (integer): the High Temp range begins above T3 and ends below T3 less the 1 C hysteresis | 41.5 to 42.7 C; the return at 41 C: 40.5 to 41.7 C | **no charge starts**: while the pack is not charging (Current() at or below Chg Current Threshold, 50 mA) and the reading is in High Temp or Over Temp (or Under Temp, L2), ChargingStatus()[IN] = 1, ChargingCurrent() 0, and the charge FET is held off with CHGIN = 1; a charge already running is not stopped by it ("a FET action will not take place", 4.13). **OPEN, BAT-F20:** "not charging" is RELAX and DISCHARGE alike (4.13's trip condition; 4.12; FET Options 0x3D sets CHGIN = 1, "Charging and Precharging disabled, FETs off", 14.2.1.1), so above T3 the charge FET Q1 is held off DURING DISCHARGE too and the kit's discharge current runs through Q1's body diode (CSD17570Q5B, VSD 0.8 V typical, SLPS471D): about 2 to 3 W at 2.5 to 3.6 A, about 7 W at 10 A, on board P; neither SLUUAQ3A nor SLUSC67B documents a body-diode protection that would turn Q1 back on | yes, below 41 C | NORMAL, not charging: RELAX and DISCHARGE (in SLEEP the charge FET is off anyway, SLEEPCHG = 0) | yes |
| L4b | primary | U1 charge suspend at T4 (4.2, 4.14, 14.4.1.6) | the same | 43 C (integer), hysteresis 1 C | 42.5 to 43.7 C | **a running charge stops**: ChargingStatus()[SU] = 1, ChargingCurrent() 0, charge FET off with CHGSU = 1; after Chg Relax Time the gauge leaves CHARGING mode and the suspend becomes L4a's inhibit, so a charge starts again only below 41 C | yes, below 41 C | NORMAL, charging | yes |
| L5 | primary | U1 OTC (2.8) | the same | 44.0 C, 2 s; recovery 39.0 C | 43.5 to 44.7 C | charge FET off (only with FET Options[OTFET] = 1) | yes | CHARGE mode only (Current() above Chg Current Threshold, 2.7) | yes |
| | **cell limit** | charge 45 C | | | | | | | |
| L6 | kit control | C2, outlet shed (`POWER-THERMAL.md` section 9.3) | the same | any cell 50 C | 49.4 to 51.7 C, plus the SMBus polling interval (TBD) | USB-C then PoE off, latched | by the operator | kit powered | no (firmware) |
| L7 | kit control | C1, module shed, and K2, PA key gate (`POWER-THERMAL.md` sections 7.2, 9.3) | the gauge's readings | any cell 55 C (C1 restores 5 K below) | 54.4 to 56.8 C, plus the SMBus polling interval (TBD) | slots to one module; no new key-down | yes | kit powered, sensor controller alive | no (firmware) |
| L8 | primary | U1 OTD (2.9) | TS1 to TS4, max | 57.5 C, 2 s; recovery 52.5 C | 56.8 to 59.5 C | discharge FET off (only with OTFET = 1); the kit loses its pack, and keeps running only on shore, vehicle or solar | yes | NORMAL, SLEEP; discharge and relax | yes |
| | **cell limit** | discharge 60 C; storage 1 month 60 C; F2 operating 60 C | | | | | | | |
| L9 | second level | U2 BQ7720700 OT, fixed 70 C (SLUSEG7D section 4, 7.3.3) | its own 103AT-2 through R34 / R33 | 62.7 to 77.5 C at the network (reading B; 63.6 to 76.6 C reading A), `candidate/ts_network.out`; 4 s | 62.7 to about 78.5 C at its sensor: its lag and delay add up to 1.0 K at section 3's 3.2 K per minute (INFERRED; more for cells lighter than 50 g) | COUT: heater on, F2 opens (once JP1 is closed; within 60 s at 10.5 V or more); DOUT: Q2 off; U1 reads COUT as 2LVL and opens both FETs | F2: never. COUT itself returns 10 K below (TOT_HYS, SLUSEG7D 6.5) | every state, SHUTDOWN included | no |
| L10 | primary, permanent | U1 SOT (3.6, 14.10.5) | TS1 to TS4, max | 65.0 C, 5 s | 64.2 to 67.4 C | permanent fail: FETs off, data flash frozen; FUSE (SOT is on the Permanent Fail Fuse list, `PRIMARY-CONFIGURATION.md` section 2) | no | NORMAL, SLEEP | yes (PF_EN, Enabled PF A, PF Fuse A) |
| L11 | primary | U1 OTF (2.10) and SOTF (3.7) on the gauge's die as the FET temperature | U1's internal sensor | OTF 80.0 C, 2 s, recovery 65.0 C; SOTF 100.0 C, 5 s (TI's defaults, written explicitly) | the die; absolute accuracy not published (SLUSC67B 6.21 gives a slope only): TBD | OTF: both FETs off; SOTF: permanent fail, never mapped to the fuse | OTF yes, SOTF no | NORMAL, SLEEP | yes |
| L12 | primary, hardware | RT1 on PTC and PTCEN (3.15) | RT1 at the FETs | the gauge's 1.2 to 3.95 Mohm (SLUSC67B 6.23); the PRF15BB103RB6RC reads "＞110" C at 100 kohm and "130+/-3" C at 4.7 Mohm (Murata DM-SA16-E056 3.1): about 110 to 133 C at the element (INFERRED); 40 to 145 ms | the board, not the cells | CHG and DSG off in hardware; PTC permanent fail; SLUUAQ3A 3.15's action table lists "FUSE = high" (whether that follows Permanent Fail Fuse C or is unconditional: Q-TI-8) | no | every state, SHUTDOWN included | FET action: no; the PF record: yes |
| L13 | passive | F1, 25 A MINI blade | none | current only | n/a | clears a hard short | no | always | no |

**The coordination this ladder must keep, and its margin on the published terms (INFERRED).** Where two layers read
the same thermistors, their order is fixed by the difference of their thresholds in the reading itself, whatever the
sensor's error; where they read different sensors, only the true windows can be compared.

| Pair | Must hold | Same sensor? | Margin |
|---|---|---|---|
| L5 OTC against the 45 C charge limit | acts before the hottest cell passes 45 C | n/a | 0.3 K (44.7 C), less the TBD terms |
| L4a T3 against L4b T4 | a charge does not start where it would at once be suspended | yes | 1.0 K in the reading; after a suspend the charge restarts only below 41 C, 2 K under T4 |
| L4b T4 against L5 OTC | the algorithm ends charge before the protection trips | yes | 1.0 K in the reading |
| L4a T3 against the charging the product needs | a warm kit on shore still starts a charge at the point D-02b accepted (charging held off above about +25 C ambient with three loaded modules) | n/a | the start ceiling in ambient is T3 less the cells' rise over the air: 3 K under the 45 C basis of `OPERATING-ENVELOPE.md` section 3 and `POWER-THERMAL.md` section 9.3 (INFERRED); TI's 30 C would have put it 15 K under (section 5) |
| L7 C1 against L8 OTD | modules shed before the pack drops out | yes (through the sensor controller) | 2.5 K in the reading, less the SMBus polling interval (TBD) |
| L8 OTD against the 60 C limit | acts before the hottest cell passes 60 C | n/a | 0.5 K (59.5 C), less the TBD terms |
| L8 OTD against L10 SOT | a recoverable stop always before a permanent one | yes | 7.5 K in the reading |
| L8 OTD against L9 U2 | the same | no (U2 has its own sensor) | 3.2 K (59.5 against 62.7 C), less the gradient between the two sensed cells (TBD) |
| L2 UTC against the 0 C charge limit | no charge below 0 C | n/a | 0.3 K |
| L1 UTD against the -10 C discharge limit | no discharge below -10 C | n/a | 0.2 K |

**Coordination with the cells' own storage.** L9 and L10 retire a pack that has been above 62.7 C. The maker rates
storage to 60 C for a month and forbids more; so a pack that is only stored (no current) between 60 and 62.7 C is
outside its rating and nothing on the pack records it. The gauge's lifetime data (LF_EN, `PRIMARY-CONFIGURATION.md`
section 2) logs the maximum cell temperature it read when awake; in SHUTDOWN it reads nothing. The commissioning and
service record reads that maximum back (TBD: the service procedure, pack build).

## 5. Written into the golden image (the rows of `PRIMARY-CONFIGURATION.md` section 2 this page changes)

| Setting | Cycle 3 | This page |
|---|---|---|
| OTC Threshold / Recovery (14.9.12) | 45.0 / 40.0 C | **44.0 / 39.0 C** |
| OTD Threshold / Recovery (14.9.13) | 60.0 / 55.0 C | **57.5 / 52.5 C** |
| UTC Threshold / Recovery (14.9.15) | 0.0 / 5.0 C | **1.0 / 5.0 C** |
| UTD Threshold / Recovery (14.9.16) | -10.0 C (recovery not stated) | **-9.0 / -4.0 C** |
| OTC, OTD, UTC, UTD Delay | 2 s (TI's default, not written) | **2 s, written** |
| Charge Temperature Ranges T1, T2, T5, T6, T3, T4, Hysteresis (4.2, 14.4.1) | not stated (TI: 0, 12, 20, 25, 30, 55 C, 1 C) | **1, 12, 20, 25, 42, 43 C; hysteresis 1 C** (T3 corrected from 30 C on 27 September 2026); T4 at 55 C would let the charge algorithm call 44 to 55 C its "High Temp" range and charge on; T3 at 30 C would refuse every charge start above a sensed 30 C (L4a) |
| SOT Threshold / Delay (14.10.5) | 65.0 C (the default, named but not listed as a written word) | **65.0 C / 5 s, written** |
| OTF Threshold / Delay / Recovery (14.9.14), SOTF Threshold / Delay (14.10.6) | enabled (Enabled Protections C bit 0, Enabled PF A bit 6) with no FET-temperature source configured | **80.0 C / 2 s / 65.0 C; 100.0 C / 5 s, written, with the die as their source** |
| Temperature Enable / Temperature Mode (14.2.1.12, 14.2.1.13) | 0x1E / 0x00 | **0x1F / 0x01**: TS1 to TS4 as cell temperatures, the internal sensor as the FET temperature; DA Configuration[FTEMP] = 0 |
| Sleep Voltage Time (Table 14-1, 0x4424) | not stated (TI: 5 s) | **5 s, written** |

**T3, taken by the session under the owner's standing rule of 26 September 2026 (27 September 2026, second pass of
this round).** SLUUAQ3A 4.13's inhibit trips on "Not charging AND (ChargingStatus()[HT] = 1 OR ChargingStatus()[OT] = 1
OR ChargingStatus()[UT] = 1)", and with FET Options[CHGIN] = 1 its action is "OperationStatus()[XCHG] = 1": the charge
FET stays off. HT is the range from T3 to T4 (4.2). The first draft of this page kept TI's T3 of 30 C and wrote that the
algorithm inhibits "below T1 and above T4"; with CHGIN = 1 that image would have refused every charge start above a
sensed 30 C. At the envelope's 10 to 16 K rise of the cells over the air (`OPERATING-ENVELOPE.md` section 3) a warm kit
on shore with three modules would then start no charge above about +14 C ambient (+20 C with one module), against the
+25 C the owner accepted with D-02b; on `POWER-THERMAL.md` section 9.3's larger rise the ceiling falls further. The
ranges' other effect, the per-range charging voltage and current, reaches no charger here (BCAST = 0; the BQ25731
cannot read them, `PRIMARY-CONFIGURATION.md` section 2), so T3's only effect on this pack is which charges may start.
The cells' maker allows charging from 0 to 45 C at the cell surface and publishes no reduced-voltage band for this
cell (Ver. 1.1 3.12). **Taken: T3 = 42 C**, so a charge may start anywhere inside the budgeted window and 1 K below
T4's suspend, which keeps a charge from starting where it would at once be stopped. Consequence: the charge-start
ceiling in ambient is about 3 K under the 45 C basis `POWER-THERMAL.md` and `OPERATING-ENVELOPE.md` use (a note to the
power stream this round); E3-A's shore runs observe it (`TEST-PLAN.md` section 6). The alternative left to the reviewer
(Q-P17): a lower T3 for cell life, with the kit's charge ceilings restated to match. **Reversed by:** the D-09 reviewer
or a cell-life requirement asking for a lower start temperature.

The FET-temperature change is **taken by the session**: with no source configured as FET temperature, what DAStatus2()'s
FET Temperature reports, and so what OTF and SOTF do, is not stated by the manual (TBD); the die is TI's own documented
option ("All five temperature sensor options can be individually enabled and configured for cell or FET temperature
usage", SLUSC67B 7.3.13). The alternative, both functions disabled (Enabled Protections C 0xD6, Enabled PF A 0x13),
leaves FET over-temperature to RT1 alone; it is put to the reviewer as Q-P16. Either way SOTF is never mapped to the
fuse.

## 6. By operating mode: which layers act

| Mode (ConOps section 4) | Gauge state | Acting layers | What keeps the cells inside their limits |
|---|---|---|---|
| **Storage**: the kit closed, **pack out** (the ConOps' Storage row) | the pack alone, in SHUTDOWN (MAC 0x0010) | L9 (U2), L12 (RT1; the FETs are off anyway), F2 once armed | **nothing on the pack**: the heat is outside it. The storage procedure (inside the cells' storage rating, below 60 C always) and the storage place. L9 retires a pack that reached 62.7 C or more |
| **Transport**: closed, latched, **pack fitted**, the kit off | SHUTDOWN if the transport procedure sends the storage command, else SLEEP with board E's always-on domain drawing from it (`PROTECTION-ARCHITECTURE.md` section 4) | SHUTDOWN: as storage. SLEEP: L1, L8 (every 5 s), L10, L11, L9, L12 | the same: nothing on the kit acts on outside heat. The ConOps restriction proposed in section 9 (never where the temperature may exceed 60 C, Samsung's own words) |
| **Normal and reduced, on the pack** | NORMAL, discharge | L1, L6, L7, L8, L9 to L13; and **L4a above T3 (42 C) and L2 below T1 (1 C) in the reading, which hold the charge FET Q1 off during discharge (CHGIN = 1): the discharge current then flows through Q1's body diode, about 2 to 3 W at the reduced load and about 7 W at 10 A on board P (BAT-F20, OPEN: not examined against F2's local heat, RT1's 110 to 133 C trip, OTF on the die, or the E3-A, E4-O and P12 pass lines)** | L6 and L7 shed the kit's own heat, L8 stops the pack's I2R and removes the pack from the kit; the envelope (+40 C, reduced above +35 C, shaded) keeps the air round the pack below the limit, if the thermal model holds (`POWER-THERMAL.md` section 9.2: on the independent bound it does not, which is why the heat-balance test and E3-A come first) |
| **Charging**, on shore, vehicle or solar | NORMAL, CHARGE mode while Current() is above 50 mA (Chg Current Threshold, 14.13.4.2) | L2, L3, L4a, L4b, L5, and L9 to L13; **L8 does not act while the gauge is in CHARGE mode** (2.9: OTD is "for cells in DISCHARGE or RELAX state"); once L4b or L5 has stopped the charge the gauge is in RELAX and L8 acts again | the charge window of L2, L4a, L4b and L5: a charge starts only between T1 and T3 in the reading, 1 to 42 C (coming up from cold: above 2 C by T1's hysteresis, above 5.0 C after a UTC trip, and above +3 C by the kit's own hold L3), runs on to 43 C (T4) and at most 44.0 C (OTC), and after a stop starts again only below 41 C; the kit's heat on shore is carried by the input, not the pack, so L8 cannot shed it: L6 and L7 are the only layers that do, and they are firmware |
| **Lid closed, reduced mode** (D-02b) | as the two rows above | as above | the reduced mode's own heat bound; E3-L measures it (`TEST-PLAN.md` section 6) |
| **Commissioning, unarmed** (JP1 open) | TI's shipped image: FET_EN = 0, both FETs held off | L9's COUT reaches no fuse; DOUT still holds Q2; L12 | no current flows, so only outside heat matters; the pack is on the bench |
| **Service**, pack out of its cradle | SHUTDOWN | as storage | as storage |

## 7. When the primary path fails

| Failure | What remains on over-temperature | Gap | Where it is closed |
|---|---|---|---|
| No golden image (TI's image) | both FETs held off: no current, so only outside heat; L9, L12 | none for current; the pack is inert | `PRIMARY-CONFIGURATION.md` section 1 |
| Partial image: FET_EN = 1 with OTFET = 0 (TI's default) | OTC and OTD only raise flags (2.8, 2.9); UTC and UTD still act; SOT and SOTF not armed while PF_EN = 0; L9, L12 | **charge up to 55 C (TI's OTC) or on to 62.7 C, discharge on to 62.7 C**, then F2 | the commissioning read-back of every word, after a reset (`FUSE-INTERPRETATION.md` section 5, step 2) |
| Firmware hang with the AFE watchdog acting | FETs off within about 5.6 s at the longest watchdog setting (INFERRED, `PROTECTION-ARCHITECTURE.md` section 6); after the restart, every layer again | about 5.6 s with no firmware temperature layer | Q-P5, Q-TI-4 |
| Gauge dead with its FETs held on (not a documented mode) | L9 (fuse and Q2), L12 in hardware; F1 | charge between 45 C and 62.7 C and discharge between 60 C and 62.7 C are not stopped; the charger has no temperature input (SLUSE66A) | section 8: the hardware hold that would close it |
| A cell thermistor open or unplugged | reads very cold: UTC and UTD open the FETs; the open-thermistor permanent fail (3.20) | none (fails stopped) | image: Open Thermistor deltas 20.0 C |
| A cell thermistor displaced off its cell (reading air) | the other three thermistors; L9 on its own sensor | a displaced sensor reads nearer the air than the cell; if the displaced one was on the hottest group, the maximum can read low by the cell-to-air difference (TBD) | pack build (adhesive, strain relief) and P14's gradient reading |
| U2's NTC open or unplugged | nothing changes for the primary | L9 is lost silently (`SECONDARY-OT-DECISION.md` section 4) | the TP15 check at commissioning and service |
| The sensor controller (the gauge's host) down | the gauge's own layers all act; its host watchdog stops charging after 10 s (HWDF = 1) | L3, L6, L7 lose their readings: **nothing sheds the kit's own heat by cell temperature**, and on shore L8 cannot either | proposed firmware contract item (W5): the panel controller falls back to the reduced mode, outlets off, when the sensor controller's pack readings stop for 10 s (taken by the session; a draft for the contract's owner). As drafted it also holds a kit with no pack at all in the reduced mode, one reason section 9a leaves operation without a pack TBD |
| The panel controller down | the gauge's layers; the sensor controller's readings reach the bridge only if the bridge reads them | the charger keeps its last settings and falls back to 256 mA (`CHARGER-STATE-SEQUENCE.md`) | the obligations of `CHARGER-STATE-SEQUENCE.md` section 6 |

## 8. Where the second level cannot enforce 60 C, what does, and what would

**Stated plainly.** The BQ7720700's over-temperature is fixed at 70 C; with TI's +-5 C accuracy and the TS network's
tolerance it trips anywhere from 62.7 to 77.5 C (reading B), so it can never act at or below the cells' 60 C discharge
and storage limit, nor at their 45 C charge limit, in any state. No released variant does better: the orderable parts
offer 70, 75, 80 and 83 C, and the 62 and 65 C options are listed only for a custom BQ77207xy ("For future options,
contact TI", SLUSEG7D section 4, VERIFIED). And no part of this accuracy class could: a secondary whose window must end
at 60 C with +-5 C of chip accuracy starts near 50 C, inside the 45 to 60 C band in which the cells are rated to
discharge, and would retire packs in legitimate use. TI positions the part as "a secondary protector meant to flow [blow]
up a FUSE" (E2E 1421182), above the primary. **In this pack the second level is an emergency backstop that retires a
pack which has already left its rating; it is not the enforcement of the rating.** In storage and transport (the gauge
in SHUTDOWN) it is the only temperature function at all, and it can only record a pack that was too hot: opening a fuse
removes no heat.

**What does enforce the limits:**
- **Against the pack's own heat and its load**: the gauge's firmware, L5 (charge, 44.0 C) and L8 (discharge, 57.5 C),
  acting on the FETs only with the golden image's OTFET, CHGIN and CHGSU bits. Independent of the kit's host, not of
  software.
- **Against the kit's own heat**: the panel and bridge firmware, L6 and L7, on the gauge's readings through the sensor
  controller. Firmware, and lost with the sensor controller (section 7).
- **Against ambient and sun**: nothing on the kit. The operating envelope (+40 C, reduced above +35 C, shaded, D-02e),
  the storage and transport procedures, and the restriction proposed in section 9.

**What would enforce them in hardware (the circuit change, not taken now).** A firmware-free, recoverable over-temperature
hold on board P: its own 103AT-2 on the hottest cell into a comparator with its own reference (resistor divider at
0.1 %), two thresholds, at most 57.5 C for discharge and at most 44.0 C for charge including its own tolerance, 5 K of
hysteresis, its output pulling DSG_G to VSS beside Q5 (the way U2's under-voltage hold does) and CHG_G to VSS for the
charge threshold, an open or shorted sensor reading as hot (the pack stops), powered from the cell stack at microamps so
it acts in every state in which a FET can conduct. It would meet BAT-001's words ("in hardware, independent of any
software, with the trip points set from the cell manufacturer's own limits") for over-temperature, which nothing on the
board meets today (finding BAT-F16). Its limits: it uses the same two FETs, so a welded Q2 defeats it as it defeats the
gauge (F2 and U2 remain); pulling CHG_G to VSS puts Q1's gate at minus the stack voltage, the gate-rating question Q-P8
already asks for Q2; and it does nothing against outside heat either. No part for it is filed under `v2/vendor/`, so its
parts and accuracy are TBD.

**Taken by the session under the owner's standing rule of 26 September 2026:** the circuit is not added now. The layering
of a firmware primary at the maker's limits and a hardware second level above them is TI's own arrangement for these
parts; what the hold adds is independence from the gauge's firmware and image only, which the explicit write and
read-back of every word addresses; and the owner's D-15 set the hardware floor this board carries. Configuration (section
5) and firmware (section 7's fallback) are taken now. **Reversed by:** the D-09 reviewer asking for firmware-independent
enforcement at the limit (Q-P15), or BAT-001's owner keeping its words literal for over-temperature (S-45): then the hold
is specified with its parts and added at board P's 4-layer regeneration (O-11).

Two other routes were read and do not work: a PTC in series with RT1 on a cell would use the gauge's hardware PTC path,
but the lowest PRF15 10 kohm option reaches 4.7 Mohm at "80+/-3" C (PRF15BG103RB6RC, Murata DM-SA16-E056 3.1), far above
60 C, and a PTC trip is permanent (SLUUAQ3A 3.15), not a recoverable hold; a lower-threshold BQ77207 fails on its
accuracy, as above.

## 9. The +71 C storage margin, reconciled with the product requirement

**What the review asks.** "The proposal to remove the pack for the +71°C storage test changes the tested configuration
and operating procedure; reconcile it explicitly with the intended product requirement. Do not select a qualification
condition merely because the current circuit can pass it." (second checkpoint review, section 2 B.)

**What the requirement says, and whose words each part is (VERIFIED in the tree).** Corrected on 27 September 2026:
the first draft of this section called the test plan's states "approved by the owner" and the envelope's +65 to +71 C
sentence "the owner's own ruling". Neither is. Under this repository's rule, a session's text must not read back as the
owner's (the handover's section 5a).
- **Owner ruling D-02a (25 September 2026):** E3's +71 C storage and +55 C operation and E4's -33 C storage are
  qualification margins over the envelope's -20 to +45 C storage and -20 to +40 C use; the pass line at a margin is
  survive and recover, inside the envelope operate to specification. It names the levels and the pass lines. It says
  nothing about where the pack is.
- **Owner approval of item 16e (6 September 2026, 23:52, appendix 32.50):** that a whole-kit MIL-STD-810 and 461 test
  plan "is written into the record before the build and run on the built prototype ... with pass criteria per test". It
  approved that a plan be written and its scope; no text of it existed yet.
- **`TEST-PLAN.md` section 1, session text.** The session wrote it on 7 September 2026 at 00:40 (`2e33773b`), after that
  approval: "transit (closed, latched, antennas off, cables out, pack fitted), deployed (open, antennas on, cables in),
  stored (closed, pack out)". Its deployed state said nothing about the pack; "pack fitted" in the deployed states was
  added by this stream in round 8. It was written when the kit's pack was a bought BB-2590/U (that plan's own "Article"
  line), before board P or its second level existed.
- **`CONOPS.md` section 4, session text** (a draft for Review A, 25 September 2026; its Transport and Storage rows cite
  `TEST-PLAN.md` line 8): Transport "lid closed and latched, antennas off, cables out, pack fitted"; Storage "closed,
  pack out", power "none (pack out)". Only Storage and Service have the pack out. **No ConOps mode runs the kit without
  its pack.**
- **`OPERATING-ENVELOPE.md`, adopted by the session (decision 34, 21 September 2026).** Section 4: storage "-20 to +45 C
  for up to three months, -20 to +25 C for a year, at the pack's ex-factory 30 percent charge. The pack is the only part
  that makes storage narrower than use." Section 8 prints the owner's D-02a table and then, in the document's own words:
  "By this document's own arithmetic (section 3, a 10 to 16 K inside-air rise) an ambient of +55 C puts the inside air
  at +65 to +71 C, above the cells' +60 C discharge limit". That is the envelope's arithmetic beside the ruling, not
  part of it.
- **The cell maker (section 1):** storage to +60 C for one month at most, a recovery test at +60 C, and "Don't leave,
  charge or use the battery in a car or similar place where inside of temperature may be over 60°C."

**The tension these documents leave, stated.** Every text above that says where the pack is in storage is the session's,
and they disagree. `TEST-PLAN.md` and `CONOPS.md` store the kit with its pack out. `OPERATING-ENVELOPE.md` section 4 reads
as a kit stored with its pack: its storage limits are the pack's own rating at the pack's storage charge, and "the pack is
the only part that makes storage narrower than use" says so only of a kit that holds its pack (without the pack it is not
even true: the LimeSDR stores from 0 to +70 C only, `POWER-THERMAL.md` section 9.4). No owner ruling decides it. On the
first reading the storage margins run with the pack out. On the second they run with it fitted, and then +71 C takes the
cells 11 K past their maker's limit by outside heat, which no protection removes.

**The reading taken by the session under the owner's standing rule of 26 September 2026: a stored kit has its pack
out, and the pack is stored apart inside its cells' storage rating.** On the requirement rather than on what passes: the
two documents that define the kit's states say so (the test plan since 7 September 2026, the ConOps since 25 September),
while the envelope's sentence states limits, not a configuration; and the reading rescues nothing, because the other reading's
consequence is recorded rather than avoided (finding BAT-F19, section 9a, its third part). The envelope's storage
sentence goes to its owner as a note this round (it states the pack's rating: "the pack, stored apart"). **Reversed
by:** the owner ruling that a stored kit keeps its pack; then E3-S and E4-S run with the pack fitted, the pack's own
storage limits govern them, and BAT-F19's third part is no longer conditional.

**The options.**

| Option | E3 +71 C storage | E3 +55 C operation | E4 -33 C storage | E5 humidity, 30 to 60 C | Transport with the pack fitted | Consequence |
|---|---|---|---|---|---|---|
| A. Pack removed for every margin, the pack checked alone at its cells' limits (the proposal of cycle 3, SC-09) | pack out | pack out, on external input | pack out | not addressed (the plan left the pack fitted) | not tested | matches the stored state, but removes the pack from every margin as a test convenience, gives the transport state (pack fitted) no hot or cold exposure, leaves no hot test of the product as used, and states no product-level result for the levels the cells cannot take |
| B. Pack fitted for every margin (the plan's "Article" line read literally) | pack fitted | pack fitted | pack fitted | pack fitted | as E3 | contradicts the stored state as the ConOps defines it; puts the cells where their maker forbids; the outcome is decided before the test: L9's window (62.7 to 77.5 C) straddles 71 C and L10 fires at 65 C, so the pack is retired by design, and a pack that happened to survive would show nothing about cells taken past any rating |
| **C. Each margin in the configuration of the state it represents; the exposures with the pack fitted at the cells' own limits; the levels the cells cannot take run as stated deviations, with the product-level result recorded (taken)** | stored: **pack out** (E3-S) | **a test deviation** (E3-O): deployed on external input with the cells kept out of the heat (section 9a); the hot use of the product **with the pack fitted** tested inside the envelope, at +40 C and at the +25 C charge point (E3-A), and lid closed (E3-L) | stored: **pack out** (E4-S) | **a test deviation** as E3-O (E5), and the same cycle with the pack fitted up to the use envelope's +40 C (E5-A) | **its own soaks, pack fitted, kit closed and off**: hot at a +58 C set point, so no cell passes +60 C (E3-T); cold at the governing cell specification's floor (E4-T) | storage, transport and use with the pack are tested as the ConOps states have them; the pack is asked for exactly what its maker rates; the two levels no configuration of the product can take are run as deviations and **do not close anything for the product: the result they cannot give is finding BAT-F19** |
| D. Make the pack meet the margins fitted | as B | as B | as B | as B | as B | needs cells rated above +60 C, which reopens the owner's pack ruling D-06 (cell, energy, pocket, money): not the session's to take |

**Recommended and taken by the session under the owner's standing rule of 26 September 2026: C.** On the requirement:
the stored kit is tested as the session's reading above defines it (pack out); transport and use have the pack fitted,
so they are tested with it, at the limits the cell maker rates, and the hot and humid use of the product with its pack
is tested inside the envelope (E3-A, E3-L, E5-A). **For the +55 C operating margin and E5's +60 C dwell, C does what
option A did: the cells are kept out because they cannot take the level.** That is a deviation from the product's
configuration, not a reconciliation with it, and the review's warning applies to it. So it is written in `TEST-PLAN.md`
as a deviation, its pass says nothing about the kit with its pack, and the result it cannot give is recorded as the
finding it is (BAT-F19). No margin is lowered. **The test of whether C was chosen by the circuit:** would it change with
a different board P, or with none? It would not: the storage and transport clauses rest on the states the ConOps and the
test plan define, the pack-fitted limits on the cells' maker, and the deviations and BAT-F19 on the cells' +60 C rating;
B fails on that rating whatever protects the cells.

**What C writes and asks for.**
- `TEST-PLAN.md` (written this round, this stream): section 1's states (a closed-lid deployed state added, per D-02b,
  and the states marked as session text); E3 and E4 as the kit's margins in their states (E3-S, E3-O, E4-S, E4-O), E3-O
  and E5 written as deviations; section 6, the pack-fitted exposures E3-A, E3-L, E5-A, E3-T, E4-T and the pack's own
  soaks E3-P, E4-P, each with its pass line; section 7, the thermal protection tests P10 to P14.
- `CONOPS.md` (a draft handed to its owner this round): the Storage row says the pack is stored apart, inside its cells'
  storage rating; the Transport row carries the cell maker's restriction: a kit with its pack fitted is never left
  where the temperature may exceed +60 C ("a car or similar place" is the maker's own example); for such exposure the
  pack comes out.
- The requirements registry (a draft handed to its integrator this round): SC-09 withdrawn with its reason and this
  choice recorded in its place; S-43, REQ-051, REQ-046 and REQ-026 restated; CFL-017 restated as the product-level
  conflict BAT-F19 is, and left open; the readings that bind `TEST-PLAN.md` and this packet re-read.
- The pack soak's pass line is taken from the maker's own recovery test: after 20 days at 60 C from a standard charge
  the cells keep at least 95 % of their standard capacity (Ver. 1.1 7.10). Here the line is 95 % of the same pack's own
  capacity measured before the soak, the maker's way (0.2 C discharge to 2.65 V at 23 C), which is the stricter reading
  for cells that start above their standard capacity; a 24 h soak at up to 60 C is milder than the maker's 20 days, so
  the line is conservative (INFERRED); the soak runs at full charge, the maker's own condition.
- **Cold, BAT-F09:** the transport cold soak and the pack's own cold storage are at the governing revision's floor:
  -20 C (Ver. 1.1) or 0 C (Version 1.0). If the lot is governed by Version 1.0, the pack may not be stored or carried
  below 0 C at all, and the envelope's -20 C storage row is the kit's without its pack: TBD at the pack purchase (Q-S1).

**What changed from cycle 3.** `SECONDARY-OT-DECISION.md` section 5 proposed option A and argued it from the cells'
rating ("the pack is never asked to survive a temperature its maker does not rate"), which is true but does not say why
the product's configuration should differ from the tested one. Option C keeps the pack out where the ConOps has it out,
keeps it in where the ConOps has it in, adds the two exposures A left out (the transport state and the hot use of the
product with its pack), and states as deviations, with their product-level result, the two levels where the pack is
kept out only because its cells cannot take them.

### 9a. The levels the kit cannot take with its pack fitted: finding BAT-F19, and how E3-O and E5 are run

**Finding BAT-F19 (product level, INFERRED by arithmetic before any test).** With its own pack fitted, the kit cannot
meet D-02a's +55 C operating margin: by `OPERATING-ENVELOPE.md` section 8's arithmetic the inside air is then +65 to
+71 C; the cells are rated to +60 C at most and their maker forbids use above it; the gauge's OTD would drop the pack at
56.8 to 59.5 C and its SOT would retire it from 64.2 C, so "survive and recover" fails for the pack whatever else passes.
The same holds for E5's humidity dwell at +60 C, where the chamber air alone is at the cells' limit before the kit adds
any heat; and, if the owner were to rule that a stored kit keeps its pack (the reading section 9 did not take), for the
+71 C storage margin as well. E3-O and E5 as `TEST-PLAN.md` writes them measure the rest of the kit at those levels and
do not close this finding.

The routes that could close it, none taken by this finding:
- **the bounded enclosure heat experiment** (`POWER-THERMAL.md` section 10), which the review puts before freezing the
  pack design: it shows whether a pack pocket insulated from the electronics' heat keeps the cells under OTD at +55 C
  ambient. With 2.5 K between that ambient and OTD's 57.5 C, it is marginal at best (INFERRED); TBD;
- **cells rated above +60 C**, which reopens the owner's pack ruling D-06 and spends money: the owner's;
- **a ruling that D-02a's +55 C margin applies to the kit without its cells**: the owner's reading of his own ruling.

**How E3-O and E5 are run, taken by the session under the owner's standing rule of 26 September 2026.** The kit in its
deployed configuration, on shore or vehicle input, with the pack standing outside the chamber at room temperature on an
extension of its two leads to board E (the XT60 at `J_BATT` and the four-wire SMBus lead at `J_SMB`, which carries PRES;
`gen_sch_e.py:193, 218`), and a thermal dummy of the pack in its pocket (the pack's outline with the cells' heat capacity,
about 480 to 660 J/K, `POWER-THERMAL.md` section 7.2, INFERRED). So the deviation is where the cells are: the power path
and the gauge's readings are the product's, and the pocket keeps a thermal mass like the pack's. Two consequences are
recorded with the run: the kit's controls C1, C2 and K2 read room-temperature cells, so of their temperature triggers
only C1's inside-air trigger acts;
and in E5 the dummy, not the pack, is the pocket's cold mass on the rising ramp, where condensation forms first (INFERRED). The
extension harness and the dummy are test fixtures, specified before the test (TBD: the extension's resistance against
the pack path's voltage margin, the SMBus ground's share of the return current, the dummy's build).

**Operation with no pack at all is not established (TBD), which is why it is not the arrangement taken.** (1) Board E's
always-on domain (the sensor controller that reads the gauge, the sensors, the fans' logic, and the two mixer fans) sits
on CELL_F, the pack side of board A's charge shunt R17 (`gen_sch_e.py:32-34`; `CHARGER-STATE-SEQUENCE.md` section 3,
BAT-F06). With no pack it is fed only through R17 by the charger, which has no battery FET and regulates the pack node
itself. TI shows the BQ25731 powering up with no battery (SLUSE66A Figure 10-4, "2-cell without battery", VERIFIED), but
not how it behaves with this board's 4S strap, with its charge-current loop through R17 carrying board E's load, or with
loads above its input limit and nothing to supplement them (TBD: board A author, then the bench). (2) The W5 fallback of
section 7 would hold a pack-less kit in the reduced mode unless it told a missing pack (PRES) from a silent sensor
controller (TBD, W5 contract). (3) No ConOps mode has it. **Reversed by:** an extension harness that proves
impractical; then E3-O and E5 run with the pack out on external input, only after (1) and (2) are shown on the bench.

## 10. The fuse F2: what is open, and what closes it

`FUSE-INTERPRETATION.md` section 1.1 (rewritten this round) withdraws the cycle-3 conclusion that F2 "fits the assembled
pack as long as the pack is held within its cells' rating": the review found it unsupported, and it is. Two items stay
open:

| Open item | Why it is open | Evidence that closes it |
|---|---|---|
| **F2's local hot condition**: its body temperature in every allowed state against its -20 to +60 C operating range | F2 sits on board P beside the FETs, the shunt and the blade, and dissipates 0.1 to 0.25 W of its own at 10 A and 0.32 to 0.81 W at 18 A (ELX1135 fuse DCR 1.0 to 2.5 mohm; INFERRED); at the pack's hot limit (the cells up to 60 C) any rise of the board over the cells puts it past +60 C; Eaton publishes nothing above +60 C | (a) a thermocouple on F2's body, logged in E3-A (hot use), E3-T and E3-P (the soaks) and P13 (18 A for 60 s from a block at +55 C; 10 A for 1 h at the pack's hot limit), with the pass line "F2's body never above +60 C"; or (b) Eaton's written answer to Q-E2 covering the measured maximum; and, if (a) fails, (c) a placement on the 4-layer board P (O-11) that keeps F2 away from Q1, Q2, R10 and F1, measured again. No alternative part fits: the ITV9550 publishes a derating but operates from -10 C only |
| **F2's current behaviour** | ELX1135 states only "100% of current rating: 1 hour minimum" and "200% of current rating: 60 seconds maximum" at an unstated temperature, no derating, no melting I2t, and no test conditions for the 80 A breaking capacity | holding at temperature: Eaton's derating (Q-E2), or P13's hold test on a board P coupon at +60 C (10 A for 1 h, 18 A for 60 s: no opening, element resistance before and after); coordination with F1: Eaton's melting I2t and time-current curve (Q-E4), or a laboratory test of F1 and F2 in series on a representative fault (250 to 500 A at 16.8 V, destructive); the heater below 10.5 V: Eaton (Q-E3) or a bench opening test at 9.0 and 10.0 V (destructive per sample); the heater at the temperature ends: opening within 60 s at -20 C and +60 C (destructive per sample) |

## 11. Open items this page adds or moves

| ID | Item | Bound and effect | Owner |
|---|---|---|---|
| BAT-F15 | the cycle-3 image put OTC and OTD on the cell limits and left the charge algorithm's T4 at TI's 55 C, T3 at TI's 30 C (with CHGIN = 1, no charge start above a sensed 30 C) and no FET-temperature source | closed in the requirements (sections 3 and 5: T3 42 C, T4 43 C); PROVISIONAL until P14 measures the two TBD terms and the cells are weighed | golden image; bench; pack build |
| BAT-F19 | the kit with its own pack fitted cannot meet D-02a's +55 C operating margin, nor E5's +60 C humidity dwell (nor the +71 C storage margin, if a stored kit were to keep its pack): the cells' +60 C rating | recorded, open (section 9a); E3-O and E5 run as deviations and do not close it; routes: the enclosure heat experiment (TBD), cells above +60 C or a reading of D-02a (the owner's) | session (the experiment); owner (D-06, D-02a) |
| TBD | operation with no pack at all: board E's always-on domain on CELL_F behind R17, the BQ25731 without a battery at the 4S strap, the W5 fallback's PRES distinction | why E3-O and E5 keep the pack outside the chamber rather than out of the kit (section 9a) | board A and E authors; W5 contract; bench |
| BAT-F20 | with FET Options CHGIN = 1 the charge inhibit (L4a, above T3) and the T1 range (L2, below T1) hold the charge FET Q1 off whenever the pack is NOT charging, discharge included (SLUUAQ3A 4.12, 4.13, 14.2.1.1), so the kit's discharge current runs through Q1's body diode: about 2 to 3 W at the one-module reduced load of 2.5 to 3.6 A and about 7 W at the 10 A typical, on board P beside F2, R10 and RT1 (CSD17570Q5B VSD 0.8 V typical, SLPS471D; INFERRED at these currents). It happens in the envelope's own hot use (+40 C ambient plus the kit's rise takes the cells above 42 C) and in cold use (E4-O, cells below 1 C). Found by the round's second independent check, 27 September 2026 | **OPEN**; not examined for F2's local hot condition (FUSE-INTERPRETATION 1.1 counts only F2's own dissipation), RT1's 110 to 133 C permanent trip, OTF on the die, or the pass lines of E3-A, E4-O and P12; the ladder is not closed while it stands. Options, none taken: (a) a FET Options setting that keeps discharge on (CHGIN = 0, with the charge-start protection kept another way); (b) a separate charge-path FET, so the discharge path has no body diode in series under the inhibit; (c) a thermal budget for the diode's heat on board P, carried into the ladder, the mode table, the F2 analysis and the pass lines. Whether the AFE re-enables CHG during discharge is not documented: a question for TI | qualified battery reviewer (Q-P18); TI (Q-TI-10); board P's author; golden image |
| BAT-F16 | no firmware-independent over-temperature protection acts at the cells' limits; BAT-001's words are not met for over-temperature | the hold of section 8, not taken now; Q-P15 | D-09 reviewer; BAT-001's owner (S-45); board P's next circuit round |
| BAT-F17 | F2's suitability is not concluded: local hot condition and current behaviour open | section 10 | Eaton (Q-E2 to Q-E4); bench (P13); placement (O-11) |
| BAT-F18 | "charges safely with the host crashed" was written as a result | restated as obligations O-CHG-1 to O-CHG-8 (`CHARGER-STATE-SEQUENCE.md` section 6) | firmware; bench |
| W5 fallback | the kit's heat shedding is lost with the sensor controller | panel controller falls back to the reduced mode, outlets off, after 10 s without the pack's readings; whether it tells a missing pack (PRES) from a silent sensor controller is TBD | W5 contract owner (draft) |
| Q-TI-8 | does a PTC trip drive FUSE unconditionally (SLUUAQ3A 3.15 lists "FUSE = high") or only through Permanent Fail Fuse C | whether RT1 at 110 to 133 C always opens F2 | TI; prepared in `REVIEW-REQUEST.md` |
| Q-TI-9 | the gauge's worst-case thermistor-reading accuracy, the temperature its pull-up is trimmed at, and what the FET Temperature reports with no source | the budget's pull-up assumption and its ADC term (section 3), by document rather than by bench | TI; prepared in `REVIEW-REQUEST.md` |
| Q-S2 | the lowest mass of the cells supplied (the sheet gives only a maximum, 50 g) | whether section 3's 3.2 K per minute bounds the heating rate; OTD holds on the published terms down to about 35 g per cell | cell supplier; the cells weighed at the pack build |
| TBD | the gradient to the hottest cell; the gauge's residual measurement error; the hottest group and cell | the OTC and OTD margins of section 3 | bench (P14); pack build |

## 12. Documents read for this page

All filed in this tree; the sha256 of each is in `MANIFEST.md` ("Documents cited"). Semitec AT series P12-13
(`v2/vendor/battery/semitec-at-p12-13.pdf`); Murata NXRT15XH103FA1B010 product-search sheet
(`v2/vendor/battery/murata-nxrt15xh103fa1b.pdf`); Murata PRF series DM-SA16-E056 (`v2/vendor/battery/murata-prf-series.pdf`);
TI BQ4050 SLUSC67B (`v2/vendor/battery/ti-bq4050.pdf`) and its technical reference manual SLUUAQ3A
(`v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf`); TI BQ77207 SLUSEG7D (`v2/vendor/battery/ti-bq77207.pdf`); TI E2E thread
1421182 (`v2/vendor/battery/ti-e2e-1421182-bq77207-application.html`); Samsung INR18650-35E Ver. 1.1 and Version No. 1.0
(`v2/vendor/battery/samsung-35e-orbtronic.pdf`, `samsung-35e-akkuzentrum.pdf`); Eaton ELX1135
(`v2/vendor/battery/eaton-scf9550-elx1135.pdf`); TI CSD17570Q5B SLPS471D (`v2/vendor/battery/ti-csd17570q5b.pdf`); TI
BQ25731 SLUSE66A (`v2/vendor/ti/bq25731-datasheet.pdf`) for its operation without a battery; and, at main `fc144600`:
for the heating rates and the charge ceilings, `v2/docs/feasibility/POWER-THERMAL.md` sections 7.2, 9.2, 9.3, 9.4 and
10; for section 9, `v2/docs/CONOPS.md` section 4, `v2/docs/OPERATING-ENVELOPE.md` sections 3, 4 and 8,
`v2/docs/MESHSAT-709-geometry-appendix.md` section 32.50 (item 16e), `v2/docs/TEST-PLAN.md` as first committed
(`2e33773b`) and the owner's rulings D-02a and D-02b as the envelope records them; for section 9a, `v2/ecad/tools/gen_sch_e.py`
lines 32 to 34, 193 and 218.
