# MeshSat field kit V2, qualification test plan (MIL-STD-810 and MIL-STD-461 methods; approved 6 Sep 2026, appendix 32.50 item 16e)

Prototype design. This plan is written before the build and run on the built prototype; nothing below has been run. Every test names the method it follows, the way it is run here (in-house on the bench or at a laboratory), the pass criterion, and where the result goes (a dated section of the design record with the measured numbers and the fix if it failed). Tests that need a laboratory are marked; their cost is the owner's decision when the prototype exists.

## 1. Test articles and conditions

- **Article:** one complete kit as specified in `V2-SPEC.md`: Peli 1450 with the face plate, the A22 to E6 board set, the BB-2590/U pack, the Xenarc monitor, all radios and antennas fitted as for deployment, the lid tablet bracket loaded with a dummy mass.
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
| M6 | Self-compatibility: every transmitter keyed in turn at full power with every receiver listening (the SDR limiter, the GNSS, the LoRa, the 5G, the WiFi) | in-house | no receiver damaged, no false trigger of EMCON, ZEROIZE or the sensors, the GNSS keeps its fix or recovers within 10 s |

## 4. Functional check (run before and after every test)

Power on from the pack; the panel controller reports; every bearer comes up and passes traffic (Iridium message, 5G data, WiFi link to a second kit or a laptop, LoRa mesh packet, Zigbee and Thread join, APRS beacon heard by a receiver, HF CAT and audio, SDR capture, GNSS fix with time pulse); the display, touch, e-paper, LEDs, sounder, headset audio and PTT, camera; the sensors report; the seal check (inside against outside pressure after the valve settles) passes; EMCON silences every transmitter (measured with the SDR); blackout darkens the kit; ZEROIZE wipes the secure element (verified by a failed key operation afterwards); the tamper switch logs the lid; shore, solar and vehicle inputs charge the pack; the PoE and USB-C outlets deliver; the log holds every step.

## 5. Records

Each test writes a dated section into `MESHSAT-709-geometry-appendix.md` with the method, the setup, the measured numbers, the pass or fail, and the fix folded into the generators or the CAD; a failed test reruns after the fix. The summary table of results lives in `V2-SPEC.md` under Qualification once the campaign has run.
