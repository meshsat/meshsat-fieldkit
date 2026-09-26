# MeshSat field kit V2, qualification test plan (MIL-STD-810 and MIL-STD-461 methods; approved 6 Sep 2026, appendix 32.50 item 16e)

Prototype design. This plan is written before the build and run on the built prototype; nothing below has been run. Every test names the method it follows, the way it is run here (in-house on the bench or at a laboratory), the pass criterion, and where the result goes (a dated section of the design record with the measured numbers and the fix if it failed). Tests that need a laboratory are marked; their cost is the owner's decision when the prototype exists.

## 1. Test articles and conditions

- **Article:** one complete kit as specified in `V2-SPEC.md`: Peli 1450 with the face plate, the A22 to E6 board set, the built 4S pack (fitted or out as the state of each test says), the Xenarc monitor, all radios and antennas fitted as for deployment, the lid tablet bracket loaded with a dummy mass.
- **States:** transit (closed, latched, antennas off, cables out, pack fitted, the kit off), deployed (open, antennas on, cables in, pack fitted, shaded, D-02e), deployed closed-lid (the reduced mode of D-02b: lid closed, antennas on, cables in, pack fitted), stored (closed, pack out; the pack is stored apart, inside its cells' storage rating). These are `CONOPS.md` section 4's Transport, Deploy and Normal, Reduced and Storage rows. **The states are session text, not an owner ruling:** the owner approved item 16e on 6 September 2026 (appendix 32.50: that this plan be written, with pass criteria per test); the session wrote the first three states on 7 September 2026 (`2e33773b`), whose deployed state said nothing about the pack, and round 8 added "pack fitted" to the deployed states, the closed-lid state and "the kit off". Each test runs the kit in the state its row names, and a row that cannot says so as a **test deviation**: E3-O and E5 keep the cells out of the heat, because fitted they would pass their maker's +60 C, and the product-level result they cannot give is finding BAT-F19. A margin run in the stored state has no pack in the case because this plan's storage state has none (the session's reading where `OPERATING-ENVELOPE.md` section 4 reads the other way), and the exposures of the pack itself, fitted in transport and use or alone, are section 6 (corrected 26 and 27 September 2026, round 8, `review-packets/battery/THERMAL-COORDINATION.md` sections 9 and 9a).
- **Instrumentation:** the kit's own sensor board (inside temperature, humidity, pressure, shock and tilt log, water sensor, gas) logs every test; the bridge's logs and the panel controller's event log are the record; external references are a calibrated thermometer, a pressure gauge for the seal check, and the laboratory's equipment where a laboratory runs the test.
- **Order:** the seal check first and after every environmental test; the functional check (section 4) before and after every test; a failure stops the sequence until its cause is recorded.

## 2. MIL-STD-810 methods, as applied

| # | Method | How it is run | Pass criterion |
|---|---|---|---|
| E1 | 516, shock, transit drop: 26 drops from 1.22 m onto plywood over concrete (faces, edges, corners), closed and latched, pack fitted | in-house | no structural damage, latches and seals intact, seal check passes, functional check passes |
| E2 | 514, vibration, composite wheeled vehicle profile, 1 hour per axis, closed, pack fitted | laboratory (shaker) or in-house on a vehicle drive of 2 hours over unpaved roads with the shock log as the record | no loosened fastener, connector or pigtail; no resonance damage; functional check passes |
| E3 | 501, high temperature, the kit's qualification margins (D-02a): **E3-S** storage 24 hours at +71 C in the stored state (closed, pack out), then **E3-O** operation 4 hours at +55 C deployed with the monitor and radios on, on shore or vehicle input, **as a test deviation with the cells kept out of the heat** (the pack outside the chamber on an extension of its leads, a thermal dummy in its pocket, section 6), because by `OPERATING-ENVELOPE.md` section 8's own arithmetic the inside air is then +65 to +71 C and the cells' maker rates them to +60 C at most and forbids their use above it. **The kit with its own pack fitted cannot meet this margin** (finding BAT-F19, `review-packets/battery/THERMAL-COORDINATION.md` section 9a); E3-O measures the rest of the kit at the margin and does not close that finding. The hot acceptance with the pack fitted (E3-A), the closed-lid test (E3-L), the transport soak with the pack fitted (E3-T) and the pack's own soak (E3-P) are section 6 | in-house with a climate cabinet or a heated enclosure with the reference thermometer | survive and recover (D-02a): no damage, no deformation, no lost data or keys, CM5 throttling logged but no shutdown, and the functional check passes once the kit is back inside the envelope with its pack refitted; the LimeSDR (storage 0 to +70 C) and the SGP41 (+70 C short-term storage) are rated below +71 C and are judged here (`feasibility/POWER-THERMAL.md` section 9.4, PWR-F11) |
| E4 | 502, low temperature: **E4-S** storage 24 hours at -33 C in the stored state (closed, pack out; a qualification margin, D-02a), then **E4-O** operation 4 hours at -20 C with the pack fitted and its heater active, started warm or from shore or vehicle input (D-02d: a cold start from the pack below about -10 C cell temperature is out of scope; inside the envelope, so an acceptance test). The transport soak with the pack fitted (E4-T) and the pack's own cold storage (E4-P) are section 6 | in-house with a freezer or winter exposure | E4-S: survive and recover. E4-O: operate to specification: the pack heats to its charge window before charging is allowed (the gauge's charge floor at +1.0 C and the panel's hold, which clears above +3 C), discharge stops at the gauge's -9.0 C, the monitor and e-paper operate at -20 C, functional check passes |
| E5 | 507, humidity: 10 cycles of 24 hours at 95 percent relative humidity, 30 to 60 C, deployed (lid open; the case has no vent opening, ruling of 7 September 2026, and Peli's pressure valve is its only opening; a qualification margin, SC-03), on shore or vehicle input with the kit logging, **as a test deviation with the cells kept out of the heat as in E3-O**, because at the +60 C dwell the chamber air alone is at the cells' +60 C limit before the kit adds its own heat (finding BAT-F19); the thermal dummy in the pack's pocket keeps the pocket's cold mass, on which condensation forms first as the chamber warms (INFERRED). The same cycle with the pack fitted, its upper level at the use envelope's +40 C, is the acceptance E5-A in section 6 | laboratory or in-house chamber | no condensation inside (inside humidity log), no corrosion, functional check passes |
| E6 | 512, immersion: closed and latched, 1 m of water for 30 minutes | in-house tank | no water inside (water sensor and inspection), seal check passes |
| E7 | 506, rain: deployed, 15 minutes of driven rain on every face at 40 mm per hour with the antennas fitted | in-house with a hose rig | no water inside, the plate seals and pass-throughs dry, functional check passes |
| E8 | 510, sand and dust: deployed, 6 hours of blowing dust | laboratory | no dust inside, latches, Peli's pressure valve and connectors operate |
| E9 | 500, altitude: storage at the equivalent of 4,500 m for 1 hour, then operation at 3,000 m equivalent | laboratory (chamber) or a mountain drive as the in-house substitute | the pressure valve equalises, seal check passes, no capacitor or pack anomaly |
| E10 | 513, acceleration, and 528, shipboard vibration | not planned for the prototype; recorded as out of scope |

## 3. MIL-STD-461 tests, as applied

| # | Test | How it is run | Pass criterion |
|---|---|---|---|
| M1 | CE102, conducted emissions on the power leads, 10 kHz to 10 MHz, on the vehicle input cable | laboratory (LISN); in-house first look with the LimeSDR and a current probe | under the limit line; the filter of the wide-range input carries the fix if not |
| M2 | CS101, conducted susceptibility on the power leads, 30 Hz to 150 kHz | laboratory | no upset of the kit's operation, no reset, no loss of a bearer |
| M3 | CS114, bulk cable injection on the antenna and power cables, 10 kHz to 200 MHz | laboratory | no upset; the arrestors and filters carry the fix |
| M4 | RE102, radiated emissions, 10 kHz to 18 GHz, deployed with the radios receiving and then transmitting on each bearer in turn | laboratory; in-house first look with the LimeSDR at 3 m | under the limit line outside the intentional transmissions |
| M5 | RS103, radiated susceptibility, 2 MHz to 18 GHz at 50 V/m | laboratory | no upset, no reset, the touchscreen and the panel keep working |
| M7 | Electrostatic discharge to every touchable surface and every exposed conductor, at the level decision 34 rules (the proposal is IEC 61000-4-2 level 4, 8 kV contact and 15 kV air) | laboratory (ESD gun); the kit powered from its pack with every bearer up | no upset, no reset, no loss of a bearer, no lost secure-element key, no damage |
| M6 | Self-compatibility: every transmitter keyed in turn at full power with every receiver listening (the SDR limiter, the GNSS, the LoRa, the 5G, the WiFi) | in-house | no receiver damaged, no false trigger of EMCON, ZEROIZE or the sensors, the GNSS keeps its fix or recovers within 10 s |

**M7 was added on 17 September 2026** and the plan approved on 6 September did not have it: owner decision 31
asks whether every conductor that leaves the case meets a protection device, ten of them do not, and the level
such a part is chosen against was written in no document of this tree. The level itself is decision 34's to
rule; the method is here so that the ruling has a test to point at.

## 4. Functional check (run before and after every test)

Power on from the pack; the panel controller reports; every bearer comes up and passes traffic (Iridium message, 5G data, WiFi link to a second kit or a laptop, LoRa mesh packet, Zigbee and Thread join, APRS beacon heard by a receiver, HF CAT and audio, SDR capture, GNSS fix with time pulse); the display, touch, e-paper, LEDs, sounder, headset audio and PTT, camera; the sensors report; the seal check (inside against outside pressure after the valve settles) passes; EMCON silences every transmitter, measured with a receiver or spectrum analyser outside the kit and never with the kit's own SDR, whose supply EMCON removes (the per-transmitter bench tests of `feasibility/EMCON.md` section 6; corrected 26 September 2026, S-07); blackout darkens the kit; ZEROIZE wipes the secure element (verified by a failed key operation afterwards); the tamper switch logs the lid; shore, solar and vehicle inputs charge the pack; the PoE and USB-C outlets deliver; the log holds every step.

## 5. Pack protection (rule BAT-001), function by function

Prototype design. **Nothing below has been run**, and none of it can be until a pack is built. These are
the tests the protection thresholds are derived FOR: `v2/ecad/tools/pcb_pack_protection.yaml` carries the
intended BQ4050RSMR configuration, every threshold inside the Samsung INR18650-35E's own limit at the pack's worst
parallel count (4S3P, the Pack Design Guideline's Portable IT column), and `pack_protection.py` judges that table
against the cell maker's own specification on every run. A test here is what turns a configured number
into a measured one.

Run them on a block that can be replaced, behind a current-limited supply and a fire blanket, with the
cell taps on a datalogger. Record every trip level AND its delay: a threshold that trips at the right
level and the wrong time is not the protection this rule asks for.

| # | function | threshold (device U1 unless stated) | the cell limit it comes from | the test |
|---|---|---|---|---|
| 1 | **cell over voltage**: a cell is charged above its own charging voltage | 4.25 V, 2 s | 4.20 V, 3.2 Charging Voltage | charge one cell block from a bench supply through the pack's own charge path with the gauge live, raise the supply until the gauge opens Q1, and read the cell voltage at the trip on the tap it measures: 4.25 V +- 0.05 V, and the FET must open within 2 s of the threshold being crossed |
| 2 | **cell under voltage**: a cell is discharged below the voltage the cell maker sets for over-discharge protection | 2.5 V, 4 s | 2.30 V, Pack Design Guideline, NCA/NCM min. voltage of over-discha | discharge the block at 1 A until the gauge opens Q2; read the lowest cell tap at the trip (2.50 V +0.05/-0.00) and confirm the pack terminal falls to zero and the gauge stays awake |
| 3 | **pack over current discharge**: the pack delivers more than the cells are rated for, continuously | 20 A, 2 s | 8.0 A per cell (24 A at 3P), 3.8 Max. Discharge Current | an electronic load stepped to 20 A on the pack terminal with the gauge live: Q2 opens within 2 s, and the same load at the declared 10 A continuous runs for an hour without tripping |
| 4 | **pack over current discharge 2**: the pack delivers more than the cells' pulse rating | 30 A, 0.02 s | 13.0 A per cell (39 A at 3P), 3.8 Max. Discharge Current | a 30 A pulse of 100 ms into the load: Q2 opens within 20 ms, and an 18 A pulse of the same length (the chain's declared peak) does not open it |
| 5 | **pack short circuit discharge**: a short across the pack terminal | 60 A, 0.0002 s | 13.0 A per cell (39 A at 3P), 3.8 Max. Discharge Current | a bolted short through a 1 mOhm shunt with a scope on the gate of Q2: the gate collapses within 200 us and F1 does not blow, which is what tells the gauge protected the pack rather than the fuse |
| 6 | **pack over current charge**: the pack is charged above the cells' own charge-current limit | 5 A, 2 s | 2.0 A per cell (6 A at 3P), 3.7 Max. Charge Current | the charger set to 5 A into a half-charged block: Q1 opens within 2 s; at the design's 4 A it does not |
| 7 | **charge temperature window**: the cells are charged outside the temperature window the cell maker allows | inside 0 to 45 C by the gauge's own error budget: UTC +1.0 C (recovery +5.0 C) and OTC +44.0 C (recovery +39.0 C), 2 s, with the charge algorithm's T1 at 1 C, T3 at 42 C (no charge starts above it: the charge inhibit) and T4 at 43 C (a running charge is suspended above it) (`review-packets/battery/THERMAL-COORDINATION.md` sections 3 to 5) | 0.0 to 45.0 C, 3.12 Operating Temperature | the block in a chamber at -5 C and at +48 C with the charger live and a reference thermocouple on every cell: Q1 stays open at both and closes between 5 C and 39 C, and it is open before any cell surface reads above 45.0 C or below 0.0 C on the references; then the block held until the gauge reads between 42.5 and 43.0 C with the charger disconnected: when it is connected, no charge starts (the charge inhibit at T3); cooled with the charger connected, a charge starts only once the gauge reads below 41 C; the thermistors read the CELL SURFACE, so the sensor's own position is part of the test |
| 8 | **discharge temperature window**: the cells are discharged outside the temperature window the cell maker allows | inside -10 to 60 C by the same budget: UTD -9.0 C (recovery -4.0 C) and OTD +57.5 C (recovery +52.5 C), 2 s | -10.0 to 60.0 C, 3.12 Operating Temperature | the block in a chamber at -15 C, then at +59 C raised in 0.5 K steps to +60 C at most, under a 2 A load with a reference thermocouple on every cell: Q2 opens at both before any cell surface passes -10.0 C or +60.0 C on the references, and closes inside the window. Never above +60 C: the second level's lowest trip is 62.7 C and the gauge's permanent SOT can act from 64.2 C |
| 9 | **precharge window**: a deeply discharged cell is charged at full current, or a dead cell is charged at all | 1 to 3 V | 1.00 to 3.00 V, Pack Design Guideline, pre-charging voltage range | a block brought to 2.5 V per cell: the gauge pre-charges at about 1 A and does not raise the current until every cell is above 3.00 V; a block below 1.00 V per cell is not charged at all and the gauge says so |

**And the one this table cannot test.** BAT-001 asks for protection in hardware INDEPENDENT OF ANY
SOFTWARE. Every function above is the gauge's, whose thresholds live in data flash. **Corrected 26 September 2026
(S-07), as generated at `45bde541`:** owner decision 40 (D-15) is ruled and board P's schematic carries its floor
since `faf8c981`: a BQ7720700 second level on its own tap filters (cell over-voltage 4.325 V and under-voltage 2.25 V,
open wire, and a fixed 70 C over-temperature on its own thermistor since `d90f30e4`), whose fault output and the
gauge's FUSE output both blow the Eaton SCF9550-30-05 chemical fuse F2 once the arming jumper JP1 is closed, whose
under-voltage output holds the discharge FET off, and the gauge's PTC input enabled with its own PTC element
(`gen_sch_p.py` lines 243, 288 and 414 to 502). Those need no firmware, and they sit beyond the gauge's thresholds
rather than beside them, so they are not rows of the table above; their bench checks are items of the battery review
packet (`review-packets/battery/PROTECTION-ARCHITECTURE.md`, its commissioning readings O-9 among them, and
`SECONDARY-OT-DECISION.md` sections 4 and 5), and none has run. The 25 A blade stays the gross-fault device. Until `faf8c981` this
paragraph said board P carried no second protector, no chemical fuse and a PTC input tied off, which was then true. **Added 26 September 2026, round 8:** the thresholds of every temperature layer, their tolerances, the sensors and their lag, and the modes each acts in are in `review-packets/battery/THERMAL-COORDINATION.md`; the bench tests of the second level's over-temperature, the PTC, the fuse at temperature and the whole ladder are section 7 below.

## 6. The hot, cold and humid exposures in each state: the kit, the transport state and the pack (E3, E4 and E5 in detail)

Written 26 September 2026 (round 8, S-43, CFL-017) from `review-packets/battery/THERMAL-COORDINATION.md` section 9, which
sets the four options against the product requirement; the session took option C under the owner's standing rule of 26
September 2026. Corrected on 27 September 2026 (the same round's independent check): E3-O and E5 are written as the test
deviations they are, E5-A is added, the charge-start threshold T3 is in E3-A's pass line, and the states are marked as
session text (section 1). Each exposure runs in the configuration of the state it represents (section 1), except the
two deviations, which say so. The margins of D-02a stay the kit's and are not lowered; the pack is asked for exactly what
its cells' maker rates (Samsung INR18650-35E Ver. 1.1: charge 0 to 45 C and discharge -10 to 60 C at the cell surface,
storage to +60 C for one month at most, and "Don't leave, charge or use the battery in a car or similar place where
inside of temperature may be over 60°C"). **A product restriction follows from it and belongs in `CONOPS.md` (draft
handed to its owner): a kit with its pack fitted is never left where the temperature may exceed +60 C; for such
exposure the pack comes out.** Nothing below has been run.

**The finding the deviations do not close (BAT-F19, `review-packets/battery/THERMAL-COORDINATION.md` section 9a).** With its
own pack fitted, the kit cannot meet D-02a's +55 C operating margin nor E5's +60 C dwell: the cells are rated to +60 C
at most, and at those levels the inside air is past it before any test is run. E3-O and E5 measure the rest of the kit
there; a pass of either is reported as that and never as the kit's margin with its pack.

**The deviation's arrangement (E3-O and E5).** The kit deployed, on shore or vehicle input; the pack outside the chamber
at room temperature, joined to board E by an extension of its XT60 lead (`J_BATT`) and its four-wire SMBus lead
(`J_SMB`, with PRES); a thermal dummy of the pack in its pocket (the pack's outline with the cells' heat capacity, about
480 to 660 J/K). The extension harness and the dummy are test fixtures, specified before the test (TBD). Recorded with
each run: the kit's controls read room-temperature cells, so of their temperature triggers only C1's inside-air trigger
sheds modules. Running the kit with no pack at all is not the arrangement, because it is not shown to work (board E's
always-on domain sits on the pack side of the charge shunt, and the W5 fallback would hold the kit in its reduced mode;
TBD in the same section 9a).

Every exposure with the pack fitted logs a thermocouple on every cell (the hottest cell surface is what the cells' limits
are judged at), one on the body of the chemical fuse F2, and the gauge's four cell thermistors and pack current.

| # | State and configuration | Level and duration | What it is | Pass line |
|---|---|---|---|---|
| E3-S | stored: closed, pack out | +71 C, 24 h | qualification margin (D-02a) over the +45 C storage envelope | survive and recover: as E3 in section 2 |
| E3-O | **test deviation**: deployed, monitor and radios on, on shore or vehicle input, the cells kept out of the heat (the arrangement above) | +55 C, 4 h, after E3-S | qualification margin over the +40 C use envelope, for the kit without its cells in the heat; the kit with its pack: BAT-F19, not closed here | survive and recover: as E3 in section 2 |
| E3-A | deployed, pack fitted, lid open, shaded; the kit in the mode its controls select (one module above +35 C, `OPERATING-ENVELOPE.md` section 4) | +40 C for 4 h on the pack, then shore applied for 2 h; and +25 C for 4 h with three loaded modules on shore (D-02b's charge point) | acceptance inside the envelope: the hot use of the product with its pack | operate to specification (functional check); every cell surface at most +60 C throughout; no charge current while any cell surface is above 45 C; **no charge starts while the gauge reads above 42 C (T3) and a running charge stops once it reads above 43 C (T4)**, with the charge held off by OTC whenever it reads 44.0 C or more; while the charge is held off the kit's loads are carried by shore; whether a charge starts at all at D-02b's +25 C point with three loaded modules is recorded with the cell temperatures (the charge-start ceiling in ambient is T3 less the cells' rise over the air, `feasibility/POWER-THERMAL.md` section 9.3); F2's body at most +60 C; the controls C1, C2 and K2 act at their triggers and are logged; no permanent protection action; the four cell thermistors against the twelve thermocouples recorded for the gradient term (section 7, P14) |
| E3-L | deployed closed-lid, the reduced mode (D-02b), pack fitted | at the reduced mode's highest ambient, 4 h (TBD: the session fixes the reduced mode and its ceiling against the thermal bound, D-02b); on the pack, then on shore | acceptance inside the envelope | as E3-A, with the lid closed; the reduced mode's bearers pass traffic |
| E5-A | deployed, pack fitted, lid open, on shore with the kit logging (the pack charging when its window allows) | 10 cycles of 24 hours at 95 percent relative humidity, the cycle of E5 with its upper level at the use envelope's +40 C | acceptance inside the envelope: REQ-026, non-condensing in use, with the pack as the pocket's cold mass | no condensation inside (the inside humidity log, and inspection of the pack's wrap, board P and its connectors), no corrosion, every cell surface at most +60 C, the functional check passes |
| E3-T | transit: closed, latched, pack fitted, the kit off; the pack in the state the transport procedure leaves it (shutdown or not, recorded) | a chamber set to +58 C holding +-2 K or better, 24 h, so no cell passes +60 C | the pack's own limit in the product's transport configuration: the storage envelope's +45 C is inside it | survive and recover: every cell surface at most +60 C; F2 intact and its body at most +60 C; no permanent fail logged and the second level not fired (its lowest trip is 62.7 C); the functional check passes after return; the pack's capacity afterwards at least 95 % of its capacity before, measured the maker's way (0.2 C to 2.65 V at 23 C, Ver. 1.1 7.10) |
| E3-P | the pack alone, armed (JP1 closed), at full charge (the maker's own storage-test condition) | +58 C set point, +-2 K, 24 h; then discharged at 2 A from +58 C until the gauge stops discharge by its own heating | the pack at its cells' own storage and discharge limits | F2 intact and its body at most +60 C; the gauge's OTD opens Q2 before any cell surface passes +60 C and recovers at or below +52.5 C; the second level does not fire; capacity recovery at least 95 % as E3-T |
| E4-S | stored: closed, pack out | -33 C, 24 h | qualification margin over the -20 C storage envelope | survive and recover |
| E4-O | deployed, pack fitted, heater active, started warm or on external input (D-02d) | -20 C, 4 h, after E4-S | acceptance inside the envelope | as E4 in section 2 |
| E4-T | transit: closed, latched, pack fitted, the kit off | the lowest storage temperature of the governing cell specification, 24 h: -20 C (Ver. 1.1) or 0 C (Version 1.0); which revision governs the cells bought is TBD (BAT-F09) | the pack's own limit in the transport configuration | survive and recover: no permanent fail, F2 intact, full function after return to 25 C, capacity within 5 % of its value before (PROVISIONAL: the maker publishes no cold-storage recovery figure) |
| E4-P | the pack alone | as E4-T | the pack at its own cold storage limit | as E4-T |

If the governing revision is Version 1.0 (storage floor 0 C), the pack may not be stored or carried below 0 C at all, and
the envelope's -20 C storage figure applies to the kit without its pack: E4-T and E4-P then run at 0 C, and the ConOps
restriction above gains its cold half.

## 7. The pack's thermal protection, tested layer by layer

Prototype design; **nothing below has been run**. These are the bench tests of the layers in
`review-packets/battery/THERMAL-COORDINATION.md` section 4 that section 5's table does not already test (rows 7 and 8
test the gauge's charge and discharge windows). The same set-up as section 5: a replaceable block, a current-limited
supply, a fire blanket, the cell taps on a datalogger, and a thermocouple on every cell.

| # | Layer | How | Pass |
|---|---|---|---|
| P10 | the second level's over-temperature (BQ7720700, fixed 70 C, window 62.7 to 77.5 C at its network) | before the golden image is written (TI's image: FETs held off, permanent fails not armed, so the gauge cannot latch 2LVL) and with JP1 open: a decade resistance in place of J_TS2's thermistor, stepped down from 3.0 kohm; read TP11 (FUSE_G, COUT) and Q5's gate (DOUT) | COUT and DOUT go active 3.6 to 4.4 s after the resistance falls below the value that maps to 62.7 to 77.5 C through R34 and R33 (`review-packets/battery/candidate/ts_network.py`), and return about 10 K cooler (TOT_HYS); F2 untouched because JP1 is open |
| P11 | the PTC element RT1 and the gauge's hardware PTC trip | on a spare board P with RT1 not fitted and the image written: a resistance across PTC and PTCEN stepped from 1.0 to 4.0 Mohm with the FETs on; separately, RT1 samples in an oven | the FETs open within 145 ms of the resistance passing a value between 1.2 and 3.95 Mohm and PTC is logged as a permanent fail; the samples cross 1.2 Mohm between 110 and 133 C; whether F2 is driven follows TI's answer to Q-TI-8 |
| P12 | the whole ladder in order, on a sacrificial block | only after the D-09 reviewer agrees: the armed block in a chamber stepped from +40 C through +60 C to +70 C at most, under a 2 A load and then on a charger | in order, on the reference thermocouples: no charge starts above 42 C in the gauge's reading (T3) and a running charge stops at or below 45 C at the cells (T4, OTC), discharge stops at or below 60 C (OTD), and only above 60 C does SOT or the second level retire the block (F2 opens); no venting; the block and its F2 are retired afterwards |
| P13 | the chemical fuse F2 at temperature (`feasibility/POWER-THERMAL.md` PWR-F12) | the block at +55 C: 18 A for 60 s; the block at the pack's hot limit: 10 A for 1 h; a thermocouple on F2's body | F2 does not open; its body never above +60 C; its element resistance before and after logged. A body reading above +60 C is a finding for `review-packets/battery/FUSE-INTERPRETATION.md` section 1.1 and for the key-down gate |
| P14 | the gauge's reading against the hottest cell | a slow chamber ramp from +20 to +58 C, and E3-A's log: the four cell thermistors, the second level's thermistor and the twelve thermocouples | the largest difference between the hottest cell surface and the gauge's Temperature() is the gradient term of the budget; if it and the residual measurement error exceed the margin the thresholds keep in hand (0.4 K for OTD, 0.2 K for OTC, less what cells lighter than about 35 g take from it, `review-packets/battery/THERMAL-COORDINATION.md` section 3), those thresholds come down by the excess before any other test is judged |

## 8. Records

Each test writes a dated section into `MESHSAT-709-geometry-appendix.md` with the method, the setup, the measured numbers, the pass or fail, and the fix folded into the generators or the CAD; a failed test reruns after the fix. The summary table of results lives in `V2-SPEC.md` under Qualification once the campaign has run.
