# MeshSat field kit V2, qualification test plan (MIL-STD-810 and MIL-STD-461 methods; approved 6 Sep 2026, appendix 32.50 item 16e)

Prototype design. This plan is written before the build and run on the built prototype; nothing below has been run. Every test names the method it follows, the way it is run here (in-house on the bench or at a laboratory), the pass criterion, and where the result goes (a dated section of the design record with the measured numbers and the fix if it failed). Tests that need a laboratory are marked; their cost is the owner's decision when the prototype exists.

## 1. Test articles and conditions

- **Article:** one complete kit as specified in `V2-SPEC.md`: Peli 1450 with the face plate, the A22 to E6 board set, the built 4S pack, the Xenarc monitor, all radios and antennas fitted as for deployment, the lid tablet bracket loaded with a dummy mass.
- **States:** transit (closed, latched, antennas off, cables out, pack fitted), deployed (open, antennas on, cables in), stored (closed, pack out).
- **Instrumentation:** the kit's own sensor board (inside temperature, humidity, pressure, shock and tilt log, water sensor, gas) logs every test; the bridge's logs and the panel controller's event log are the record; external references are a calibrated thermometer, a pressure gauge for the seal check, and the laboratory's equipment where a laboratory runs the test.
- **Order:** the seal check first and after every environmental test; the functional check (section 4) before and after every test; a failure stops the sequence until its cause is recorded.

## 2. MIL-STD-810 methods, as applied

| # | Method | How it is run | Pass criterion |
|---|---|---|---|
| E1 | 516, shock, transit drop: 26 drops from 1.22 m onto plywood over concrete (faces, edges, corners), closed and latched, pack fitted | in-house | no structural damage, latches and seals intact, seal check passes, functional check passes |
| E2 | 514, vibration, composite wheeled vehicle profile, 1 hour per axis, closed, pack fitted | laboratory (shaker) or in-house on a vehicle drive of 2 hours over unpaved roads with the shock log as the record | no loosened fastener, connector or pigtail; no resonance damage; functional check passes |
| E3 | 501, high temperature: storage 24 hours at +71 C closed, then operation 4 hours at +55 C deployed with the monitor and radios on | in-house with a climate cabinet or a heated enclosure with the reference thermometer | inside temperature stays under the parts' limits (pack under 60 C, CM5 throttling logged but no shutdown), no deformation, functional check passes |
| E4 | 502, low temperature: storage 24 hours at -33 C closed, then operation 4 hours at -20 C with the pack's heater active | in-house with a freezer or winter exposure | the pack heats to its charge window before charging is allowed, the monitor and e-paper operate at -20 C, functional check passes |
| E5 | 507, humidity: 10 cycles of 24 hours at 95 percent relative humidity, 30 to 60 C, deployed with the vent open | laboratory or in-house chamber | no condensation inside (inside humidity log), no corrosion, functional check passes |
| E6 | 512, immersion: closed and latched, 1 m of water for 30 minutes | in-house tank | no water inside (water sensor and inspection), seal check passes |
| E7 | 506, rain: deployed, 15 minutes of driven rain on every face at 40 mm per hour with the antennas fitted | in-house with a hose rig | no water inside, the plate seals and pass-throughs dry, functional check passes |
| E8 | 510, sand and dust: deployed, 6 hours of blowing dust | laboratory | no dust inside, latches, vent and connectors operate |
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
| 7 | **charge temperature window**: the cells are charged outside the temperature window the cell maker allows | 0 to 45 C | 0.0 to 45.0 C, 3.12 Operating Temperature | the block in a chamber at -5 C and at +50 C with the charger live: Q1 stays open at both, and closes between 5 C and 40 C; the thermistors read the CELL SURFACE, so the sensor's own position is part of the test |
| 8 | **discharge temperature window**: the cells are discharged outside the temperature window the cell maker allows | -10 to 60 C | -10.0 to 60.0 C, 3.12 Operating Temperature | the block in a chamber at -15 C and at +65 C under a 2 A load: Q2 opens at both and closes inside the window |
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
paragraph said board P carried no second protector, no chemical fuse and a PTC input tied off, which was then true.

## 6. Records

Each test writes a dated section into `MESHSAT-709-geometry-appendix.md` with the method, the setup, the measured numbers, the pass or fail, and the fix folded into the generators or the CAD; a failed test reruns after the fix. The summary table of results lives in `V2-SPEC.md` under Qualification once the campaign has run.
