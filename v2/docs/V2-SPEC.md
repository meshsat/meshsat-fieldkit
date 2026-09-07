# MeshSat field kit V2, approved specification (state of 7 Sep 2026, design record sections 32.40 to 32.61)

Prototype design. Nothing in this document has been built, ordered or field deployed; every line is an owner ruling recorded in `MESHSAT-709-geometry-appendix.md`, and the board generation that implements it is MESHSAT-830 (A22, B16, C7, D8, E6, face plate and case template). The generators of that generation ran on 7 September 2026 (the boards table below carries their numbers); items marked *owed* still need a document, a quote or a pick.

## Case and construction
| Item | Specification |
|---|---|
| Case | Peli 1450 (used unit bought 6 Sep 2026) with the 1450PF panel frame; IP67 by the case, pressure valve, padlock protectors; the kit is designed to an IP67-class construction and never labelled IP68 |
| Face | 3 mm black anodised aluminium plate on the frame's inserts, laser-marked legends and the MeshSat mark; the backer board C7 hangs under it |
| End walls | eleven SMA bulkheads at Z 88 (32.56): west VHF, HF, WIFI 2.4, GNSS, SDR; east 5G MAIN, 5G DIV, IRIDIUM, LORA, WIFI P2P A, WIFI P2P B, all clear of the moulded nubs; every cable ends at the dock strip's float clamp under the stack's blind-mate receptacle (`ecad/tools/panel1450.py` is the single source of the positions) |
| Back wall | connector plate between the ribs: MIL-DTL-38999 shore and USB receptacles, sealed Gigabit Ethernet with PoE out, sealed USB-C PD 45 W outlet (32.57) and console, ground stud |
| Interior | the A22 + D8 + B16 rod stack over the dock strip E6 and block; the BB-2590/U cradle at the west wall (position ruling owed, 32.60 item 7); on the lid's inner face the printed tray of the QMX HF unit over the right strip (32.60 item 5) and, over the left strip, a bracket for an 8 to 10 inch rugged tablet (not drawn) |
| Disassembly | face plate off (ten M3), the rod stack lifted straight up off the blind-mate joint without unscrewing a cable, the pack out of its cradle |

## Power

The node, the inputs, every rail with its part and its EMCON gate: appendix 32.55 (7 Sep 2026).
| Item | Specification |
|---|---|
| Battery | one BB-2590/U military pack (MIL-PRF-32383 family; 14.4 V, 250 to 300 Wh, SMBus and LED gauge, MIL-STD-810F and 461 tested, discharge -32 to +60 C), Army SC-C-179495 connector; quotes *owed* |
| Inputs | 9 to 36 V filtered vehicle and shore input (MIL-STD-461 class line filter, NATO 2-pin plug cable, the 38999 receptacle); the LT8705A solar tracker |
| Rails | 14.4 V node; SMBus charger; bucks for 5 V and 3.3 V; 13.8 V rail for the PA stage and the monitor; PoE out; USB-C PD out |
| Run time from the pack | about 8 to 9.5 h typical (29 W: monitor on, radios idle, APRS beacons), 5 to 6 h with the three-CM5 cluster busy, 11 to 13.5 h dimmed; peak about 150 W with everything transmitting |
| EMCON | a hardware line gates every transmitter rail and the PA bias (5G, WiFi cards, LoRa, Iridium, HF, APRS); blackout and NVG panel modes beside it |

## Compute, storage, expansion (B16, about 330 x 200 mm; the distributed fabric of 32.52)
| Item | Specification |
|---|---|
| Requirement | no single CM5 is a single point of failure: one, two or three modules in any slot, every device visible to all modules, the OS and the HAL adopt devices, k3s on top |
| Compute | three identical CM5 slots (8 GB, 64 GB eMMC, wireless) joined by a five-port Gigabit switch chip with the sealed wall port and a spare header |
| Per slot | a PCIe switch (Diodes PI7C9X2G404SL, one upstream and three downstream lanes; 32.54) feeding one NVMe M.2 M-key 2242 (storage replicated across slots by k3s) and one card slot (slot 1 the WiFi link card, slot 2 the 5G module, slot 3 a spare M.2 M-key 2242); a four-port USB 3 hub with device headers; HDMI into the three-input display switch; time-pulse and heartbeat lines |
| Devices | every radio, sensor and the panel is a USB device on a slot's hub (USB-serial bridges for the UART radios, two RP2040-class controllers for the panel and the sensors, a USB audio and control set for the APRS board); the HAL shares them to the other modules over the network; the physical owner is a cabling choice recorded in the HAL configuration |
| Panel controller | LEDs, switches, sounder, e-paper, ambient light, blackout and NVG lighting, HDMI input select, heartbeats, and the hardware EMCON and ZEROIZE logic independent of any module; the secure element on its bus |
| Security | secure element behind ZEROIZE (element wiped, disk-key wipe line asserted), encrypted drives, case-open tamper switch, key fill as a signed procedure over the console |
| Time | LG290P and DCF77 pulses fanned out to every slot, a holdover RTC on the panel controller, chrony on each module |

## Bearers and radios
| Bearer | Device | Where |
|---|---|---|
| Satellite | RockBLOCK 9704 SMA (Iridium Messaging Transport) with the Maxtena M1621HCT-P-SMA helical | B16 UART, east jack |
| Cellular | 5G module on M.2 B-key (Quectel RM520N-GL assumed; module and jack count *owed*), dual SIM (eSIM plus nano-SIM) | B16 PCIe, east jacks |
| Kit-to-kit WiFi | AsiaRF AW7915-AED (MT7915, 2.4 and 5 GHz) for mesh or point-to-point links without an access point | B16 PCIe, two east jacks |
| Local WiFi and Bluetooth | the CM5's own radio with Raspberry Pi's certified antenna kit | west jack |
| LoRa mesh | bare 1 W SPI module of the E22-900M30S class (SX1262 + 30 dBm amplifier), meshtasticd on the CM5, EU power capped in software | B16 SPI, east jack |
| Zigbee | Ebyte E72-2G4M20S1E (CC2652P) as coordinator, on-board antenna | B16 UART |
| Thread and Matter | a second E72 as OpenThread radio for a Thread border router and Matter controller | B16 UART |
| APRS and VHF voice | NiceRF SA868 1 W with a 30 W VHF amplifier stage (RA30H1317M class, T/R relay, low-pass filter; sheet *owed*), Direwolf on the WM8960 codec, hardware PTT inhibit | D8, west jack |
| HF beyond line of sight | the assembled QRP Labs QMX (5 W, USB CAT and audio) in its lid tray, ARDOP or VARA, Winlink and TAK data; wire antenna kit outside | B16 USB (`J_QMX`), A22's 12 V HF rail, the HF jack |
| SDR | LimeSDR Mini 2.4 (10 MHz to 3.5 GHz, transmit and receive) with a receive limiter or relay during PA key-down | B16 USB 3, west jack |
| GNSS | Quectel LG290P (all six constellations, L1/L2/L5/E6, RTK capable) with the Quectel YEGD006U1A puck or the u-blox ANN-MB2 | B16 UART, west jack |
| RF protection | gas-discharge arrestors at the bulkheads, a shielded compartment for the PA |

## Panel and human interface (face plate, C7)
| Item | Specification |
|---|---|
| Display | Xenarc 709GNK boxed monitor on the plate: 7 in, 1024 x 600, 1000 nits, projected-capacitive touch, HDMI, IP67, -20 to +70 C; connector side from Xenarc's drawing *owed* |
| E-paper | Pervasive Displays E2370KS0C1, 3.7 in 416 x 240 wide-temperature panel under the plate lens: identity, status and the QR code with the power off |
| Switches | APEM 5636ADKB-2V locking toggles for SOS, EMCON and ZEROIZE with hinged safety covers on SOS and ZEROIZE (cover part *owed*), C&K and NKK buttons for MAIN, PI and TEST, the LIGHT toggle |
| Indicators | sixteen LEDs through IP68 light guides, the Floyd Bell sounder; blackout and NVG modes |
| Audio | the monitor's built-in waterproof speaker over HDMI for the UI, spoken alerts and net monitoring (volume and mute in its menu); two sealed MIL headset jacks with PTT on the codec as the private path; net audio recording to the drives; blackout mutes the speaker and the sounder (32.53) |
| Camera | a sealed camera on the face or a USB camera on the wall port for image messages |
| Ambient light | a sensor behind a sealed window drives the monitor and panel brightness |

## Sensors (the sensor controller on E6: a second RP2040 as a USB device, the sensor board of the plan folded into the dock strip)
inside temperature, humidity and pressure with the outside pressure as a seal check; floor water sensor with alarm and pack shutdown; six-axis IMU with magnetometer (shock and tilt log, heading, motion wake-up); hydrogen and VOC sensing in the battery bay with shutdown; ambient light; AS3935 lightning detector with a mast-down alarm; Geiger-Mueller tube counter inside (dose rate logged and shared over the mesh); outside temperature, humidity, pressure and UV in a sealed pod on the outside of the connector plate over an M8 sealed receptacle, with a UV-transparent window (no vent anywhere, 32.53). Particulates and wind stay external accessories.

## Qualification

The method-by-method plan with pass criteria is `TEST-PLAN.md` (approved item 16e).
A whole-kit test plan to MIL-STD-810 (transit drop, vibration, temperature operation and storage, humidity, immersion) and MIL-STD-461 (conducted emissions and susceptibility on the power leads, radiated emissions) is part of the design: written before the build, run on the built prototype in-house where possible and at a lab where not, pass criteria per test, fixes fed back into the record (approved 6 Sep 2026).

## Thermal and environment
no vent opening anywhere in the case skin or the plate (owner ruling 7 Sep 2026, 32.53): the heat leaves through the aluminium face plate and the case walls; five IP68-rated internal fans (one per CM5 cooler, two mixer fans under the plate) driven by the sensor controller couple the inside air to the skin; the 30 W PA module bolts flat to the plate's underside on two PEM nuts with a thermal pad (32.56); estimated inside-air rise about 10 K with one module and 16 K with three loaded modules with the lid open (32.53), to be measured by `TEST-PLAN.md` E3; in direct sun the plate is shaded; with the lid closed the kit runs the reduced mode; the pack's heater mat and the inside climate sensor set the cold-weather behaviour; the case keeps Peli's own pressure equalisation valve.

## Open items (the generators have run; these remain owed)
the 5G module's hardware design and its jack count; the KSZ9897, ATECC608B, DS3231, LIS3MDL, TE and Amphenol M.2 drawings (laptop list, 32.54); the sealed USB-C and RJ45 wall parts; the U-174/U headset jacks; the SOS and ZEROIZE cover part; the 2 m antenna; the tablet; the IP68 fans; the BB-2590 quotes. Closed on 7 Sep 2026: the PCIe switch (Diodes), the hubs, the display switch, the bridges, the controllers, the sensors' stock, the SA868 sheet, the PA sheet and heat path, Xenarc's drawing, the vent (none), the ASM118x question (0 stock).

## Boards of this generation
| Board | Role |
|---|---|
| A22 | power and I/O, 240 x 160 mm, six layers (In1 and In4 solid ground): 14.4 V node, BQ25731 SMBus charger, the 9 to 36 V input passed up from E6, three 5.1 V slot rails and a device rail (AP64500, INA226 monitored), the 13.8 V PA and 12 V HF rails (LM5176, EMCON gated), the 54 V PoE rail, the 45 W USB-C outlet (TPS25740 and TPS55288), 3.3 V logic, eleven SMP-MAX blind-mate sites, the D8 mezzanine site, the 2x13 ribbon to B16 |
| B16 | compute and radios, 330 x 200 mm, six layers (In1 solid ground, In4 the 5 V planes): three CM5 slots, per slot a PI7C9X2G404 PCIe switch, an NVMe 2242 socket, a card socket, a TUSB8041 USB 3 hub and a cooler fan header; the KSZ9897 Ethernet switch, the TMDS341A display switch, the LimeSDR bay, the RockBLOCK site, the LG290P, the E22 LoRa module, two E72, the DS3231M clock, the ATECC608B, the TMP117, the panel and A22 ribbons |
| C7 | panel backer under the plate, a 344 x 228 ring with a 240 x 176 void, four layers: the RP2040 panel controller (a USB device with the hardware EMCON and ZEROIZE lines), sixteen LEDs under light guides, two PCA9555, the PDi e-paper ZIF and its boost stage, the sounder driver, the VEML7700, the switch lands, the headset jack and camera holes, the notch for the monitor's connector block; the PA flange sits in its void |
| D8 | VHF APRS mezzanine on A22, 100 x 80 mm, four layers: the SA868 exciter, the G6K T/R relay, the low-pass filter and the leads to the RA30H1317M1 on the plate, the PCM2912A USB codec and TPA6132A2 amplifier for the two headset jacks, the TUSB2046B hub and CP2102N bridge, the PTT and EMCON gate logic, the TPS22810 gate-bias switch, a PCA9555 |
| E6 | dock strip, 267 x 68 mm, four layers, and the block E5: the LM5176 9 to 36 V front end, the LT8705A solar tracker, the pack entry (XT60, 25 A fuse, SMBus), eleven float clamps, the sensor controller with the BME688, BMI270 and magnetometer, the water electrodes, the gas sensor, the DCF77, Geiger, lightning and outside-pod headers, two mixer fan headers |

## Estimated cost per kit (parts only, prototype quantities, 6 Sep 2026)

Estimates in euros at single-unit or five-off prices; documented prices where the record has them (case, monitor, RockBLOCK, RRC pack), the rest from the makers' list prices as remembered and to be replaced by quotes. Labour, subscriptions (Iridium messaging line, cellular SIM) and accessories are outside the total.

| Group | Estimate (EUR) |
|---|---|
| Case, frame, machined and anodised face plate | 350 |
| Xenarc 709GNK monitor | 520 |
| BB-2590/U pack with our SMBus charger parts | 600 to 850 |
| Three CM5 8 GB / 64 GB wireless | 300 |
| LimeSDR Mini 2.4 | 275 |
| 5G module | 150 to 250 |
| AW7915-AED WiFi card | 70 |
| RockBLOCK 9704 SMA and Maxtena helical | 395 |
| LG290P module and GNSS puck | 160 |
| LoRa 1 W module, two E72, SA868, PA module, QMX HF module | 225 |
| PDi e-paper | 30 |
| Two NVMe drives, two PCIe switches, secure element, RTC, DCF77 | 165 |
| Sensor board with Geiger counter and the outside sensor pod | 130 |
| Panel parts: toggles and covers, buttons, LEDs and light guides, sounder | 200 |
| Two headset jacks, camera | 125 |
| Connectors: two MIL-DTL-38999, sealed Ethernet and USB-C, SMA bulkheads, the nine-path SMP-MAX blind-mate set, arrestors | 700 to 850 |
| External antennas (seven Quectel picks plus 5G) | 240 |
| Five PCBs with assembly, per kit at five-off | 400 |
| Board components (converters, charger, PA stage, codec, expanders, passives) | 300 |
| Rods, standoffs, cradle, cables, heater mat, PA heat column, five IP68 fans | 190 |
| **Total, parts** | **about 5,700 (4,800 to 6,800)** |

Accessories outside the total: rugged tablet for the lid (500 to 700), mast, coax set and HF wire antenna kit (about 300), personal locator beacon (about 300). The pack, the monitor, the connector set, the Iridium modem and the SDR are about 60 percent of the parts total.
