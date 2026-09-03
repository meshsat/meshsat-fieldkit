# Building a V2 kit from this repository

Rev A of the carrier set has been designed, reviewed and prepared for order; no kit has been built from it yet. This page is the path from an empty JLCPCB cart to a running kit, in order, pointing at the documents that carry the detail. Read it together with `docs/ASSEMBLY.md` (fasteners, build order, the pack, leads, coating, labels, removal, bench checks, bench-fit lists) and `docs/PANEL.md` (what the software does with the panel). The design record with every number and every ruling is `docs/MESHSAT-709-geometry-appendix.md`, section 25 for the current design.

MeshSat is a prototype. The V2 boards have not been fabricated; expect Rev A to need a Rev B.

## 0. Before you start

- Three rulings are not open for redesign: the Geekworm X1202 is the only charger and UPS and the welded pack sits in parallel with its cells; EMCON is a hardware line from the panel toggle to the APRS PTT driver plus a software hold; the panel is driven per `docs/PANEL.md`.
- Nothing on the bench gates the first order (appendix 32): every COTS site was checked against the manufacturer's own drawing (the documents are in `vendor/`), and the X1202's undocumented figures are absorbed by the design, chiefly by the A17 module rail that takes every 5 V load but the Pi off the X1202. What the owner still names, without measuring anything: the panel switch parts, the SMA coupler for E2, the dock spring pin.
- The panel software (expanders, LED semantics, e-paper, sounder) is specified in `docs/PANEL.md` but not yet written in the Bridge (MESHSAT-773). A Rev A kit powers up and runs the Bridge; the panel lights and switches come alive with that software.

## 1. Order the boards

Seven boards, five assembled by JLCPCB (top side, standard PCBA; the economic tier is not offered for these boards), two bare. Everything you upload is in `release/revA/order/<board>/`: the Gerber zip, the JLC-format BOM and CPL (rotation offsets already applied, bench-fitted parts removed, designator ranges expanded) and `ORDER-NOTES.txt` with the exact settings. `ORDER-LOG.md` in the same folder records the 3 September 2026 run line by line, including what JLCPCB's checks answered.

| Board | Folder | Size (mm) | Layers | Stackup | Assembly |
|---|---|---|---|---|---|
| PCB-A POWER + I/O A17 | `PCB-A-POWER-A17/` | 285 x 160 | 4 | JLC04161H-7628 | top |
| PCB-B COMPUTE B11 | `PCB-B-COMPUTE-B11/` | 245 x 170 | 4 | JLC04161H-7628 | top, bottom 1 |
| PCB-C CONTROL PANEL C4 | `PCB-C-DISPLAY-C4/` | 442 x 311 | 2 | standard | top 18, bottom 70 |
| PCB-C SPACER RING R1 | `PCB-C-RING-R1/` | 106 x 54 | 2 | standard, 1.0 mm | none |
| PCB-D APRS D5 | `PCB-D-APRS-D5/` | 80 x 62 | 4 | JLC04161H-7628 | top 78, bottom 1 |
| PCB-E1 DOCK E1 | `PCB-E1-DOCK-E1/` | 250 x 44 | 2 | standard | top 15 |
| PCB-E2 RF JUNCTION E2 | `PCB-E2-RFJUNCTION-E2/` | 330 x 32 | 2 | standard, no copper | none |

Common settings, from the ORDER-NOTES: 1.6 mm FR-4 (the ring 1.0 mm), 1 oz outer copper, ENIG, matte black solder mask, white silkscreen, no castellations, order number removed, quantity 5 (the JLCPCB minimum). The four-layer boards carry USB 2.0 pairs at 0.2 mm track and 0.15 mm gap on the outer layers; ask for 90 ohm differential tuning on the 7628 stackup. Turn both free confirmation options on (production file review and the BOM/CPL confirmation) so the placement preview is checked before anything is cut. On the JLC preview, check the rotation of every polarised part against `release/revA/review/<board>/*-assembly-top.pdf`.

Parts JLCPCB does not fit are listed per board in the ORDER-NOTES ("fitted at the bench") and in `docs/ASSEMBLY.md` section 9. If JLCPCB has no stock for a line at order time (the Keystone 3568 fuse holders and the two white 3 mm LEDs were short in September 2026), let it drop to DNP and fit it at the bench.

If you change a board first, regenerate it (`README.md`, "Regenerating a board"), then run `make_handoff.py`; it rewrites `order/` and `review/`. JLCPCB cannot swap Gerbers in an existing cart line, so batch changes before uploading.

## 2. Everything else to buy

Case and frame: Peli 1520EU without foam and the 1520PF special application panel frame (the frame kit brings the inserts; confirm the insert thread against the M3 x 8 screws before ordering fasteners). Orange was chosen for the kits.

Modules that mount on the boards (one kit): Raspberry Pi 5 8 GB with active cooler, Geekworm X1202, LilyGO T-Call A7670E, LilyGO T-Beam 1W (LoRa), RTL-SDR Blog V4, ZigBee CC2652P USB coordinator, RockBLOCK 9704 (or 9603) with the Ground Control bracket, Seeed Wio-SX1262, Raspberry Pi Touch Display 2, WeAct 3.7 inch e-paper module, NiceRF DMR858M (VHF 5 W), u-blox GPS puck, MT7612U WiFi dongle, TRACO TEN 40-2412WIN on the dock.

Pack: eight Samsung INR18650-35E, matched to the four in the X1202 (same model, same age, within 50 mV), 0.15 x 8 mm nickel strip, fish paper, a 1S BMS 15 A with NTC cutoff, a 10k NTC 103AT-2, XT60 male on 16 AWG silicone leads, blue PVC shrink sleeve. Spot welder or a shop that welds packs.

Hardware per `docs/ASSEMBLY.md` section 1: four M3 stainless rods with Nyloc nuts, 6.0 mm spacers for the dock, 35 mm and 59 mm bay spacers, four M2.5 x 22 female-female standoffs with M2.5 x 6 screws for the X1202 stack (confirm the 22 mm against the module's holder side), 16 x M3 x 8 pan head for the panel, 6 x M3 x 12 for the junction strip, 4 x M3 x 6 for PCB-D, 2 x M2.5 x 11 standoffs with M2.5 x 4 screws for the DMR858M, Loctite 243, four M3 standoffs under PCB-D, two 7.6 mm cable ties for the pack strap and a 1 mm silicone sheet.

Consumables: 3M 467MP or 9495LE transfer tape (display and e-paper), 3M VHB 5952 pads (dock strip), MG Chemicals 422B acrylic conformal coating, kapton for the masks, IPA.

Electrical: eight spring pins for `J_DOCK` (2.54 pitch, the part named in appendix 32.6 once picked), Keystone 3568 mini blade holders with two 15 A, one 10 A and one 7.5 A blade, an 18 AWG JST-VH lead for the module rail (PCB-A `J_5V_MOD1` to PCB-B `J_5V_MOD`, 150 mm) and a 24 AWG XH lead for the X1202 5 V sense (one X1202 XH output to PCB-B `J_5V_IN1`), XT60 pairs, JST-XH 2.5 and JST-VH housings and crimps, 16 / 18 / 20 / 24 AWG silicone wire, a 20-way 1.27 mm ribbon with 2x10 IDC ends (350 mm), a 16-way ribbon with 2x8 IDC ends, a 5.5 x 2.1 barrel plug, an IP68 2-pin DC bulkhead (Bulgin PX0 or Amphenol C016 class) with a 12 V PD trigger lead for USB-C sources, seven SMA female-female bulkhead couplers for E2, SMA female bulkheads for the wall, RG-316 pigtails (SMA male ends, u.FL where the module has it).

Panel hardware: SW_MAIN 19 mm anti-vandal with green ring, SW_PI 16 mm amber ring, SW_TEST 16 mm white ring, one sealed DPDT ON-ON-ON toggle (SW_LIGHT), three SPDT guarded toggles with red covers (SW_SOS momentary, SW_EMCON latching, SW_ZERO momentary), an 85 dB piezo if not fitted by JLCPCB, the two white 3 mm LEDs D10 and D11.

## 3. Prepare the case

1. Fit the 1520PF frame per Peli's instructions; its 16 inserts are the panel's screw pattern (431.8 x 301.2 mm, appendix 25.1).
2. Junction strip E2 goes on the +Z wall between the wall ribs: six M3 wall screws into the 1520's drill points (self-tapping brass inserts or nuts inside the wall recess), seven SMA bulkheads in the wall next to it on the strip's D-hole pattern (6.5 mm). The strip's lower coupler sides face the wall pigtails, the upper sides the device pigtails.
3. Shore inlet: the IP68 2-pin bulkhead on the -Z wall, lead to the dock's `J_DCIN` (JST-VH, 18 AWG, 400 mm).
4. Dock strip E1 on the floor: degrease with IPA, four VHB pads at the corners, locate it by dropping two rods through its south rod holes before the pads touch.
5. Bulkhead legend strip (UHF SDR WIFI1 WIFI2 LTE IRID LORA) beside the SMA row, the "RF HAZARD DURING TX" label next to the UHF bulkhead, the asset label in Peli's recess (`docs/ASSEMBLY.md` section 6).

## 4. The pack

No X1202 measurement is needed before the pack is built (appendix 32.3): the charge current only sets the charge time (13 to 18 h for 42 Ah at Geekworm's 2.3 to 3.2 A), the bridge restarts the charger over GPIO 16 if it ever stops early, the pack and the APRS boost hang on the holder tabs behind F1 and F2 where the X1202's own protection never sees them, and every 5 V load but the Pi runs on the A17 module rail. Build the pack per `docs/ASSEMBLY.md` section 3 (1S8P, two rows of four, 130 x 74 x 18.5 mm, BMS on the negative lead, NTC inside, XT60 out), match it to the X1202's four cells within 50 mV, and commission everything together per section 8 of the same document after assembly.

## 5. Assemble

Follow `docs/ASSEMBLY.md` section 2 step by step; the short form:

1. Dock strip E1: solder the leads, fit the TEN 40-2412WIN, the fuse holder and a 7.5 A blade, test 12 V at the targets with 9 V and 36 V in, then stick it down.
2. Rods through the strip's holes with the 6.0 mm spacers (washer stack under the two north rods so all four sit level).
3. PCB-A A17: press the eight spring pins in from the underside, fit F1 (15 A), F2 (10 A) and F3 (15 A) before anything is energised, strap the pack on, plug `J_PACK`, route the `J_X1202BAT`, `J_X1202DC` and module-rail (`J_5V_MOD1`, VH) leads up the stack's edge. Nyloc on top.
4. 35 mm spacers, PCB-B B11 with the Pi 5 and X1202 stack on its 22 mm standoffs (Pi HDMI edge west, GPIO header edge east, SD card south; nothing under the X1202), the module-rail lead into `J_5V_MOD`, the modules, the panel ribbon in `J_PANEL`. Nyloc on top.
5. X1202 leads: battery lead to the B+ / B- holder tabs (16 AWG, XT60 at PCB-A, fused by F1 at the source), 12 V lead to the barrel, switch lead to the external-switch pins, Pi J2 lead to the Pi's J2 pads, and the 5 V sense lead from one XH 5 V output to PCB-B `J_5V_IN1` (it enables the module rail; PCB-B draws nothing through it).
6. Junction strip pigtails: wall side torqued once at 0.45 N m, device side finger tight; RG-316 with a 12.5 mm bend radius, tied at both ends.
7. Panel C4: switches with their boots and covers (covers open toward the operator), the e-paper module taped face-up under its window (spacer ring R1 first if a flush face is wanted, header to the east, 2x4 lead to `J_EPD`), the Touch Display 2 glass taped over its full flange, ribbon and the two XH leads plugged, 16 frame screws at 0.4 N m with a drop of Loctite 243.
8. Lid: the lid foam is pocketed over the switch strips (nothing on the panel face is taller than 20 mm).

Torque table, threadlocker rules and every lead's wire gauge, length and connector are in `docs/ASSEMBLY.md` sections 1 and 4. Never put threadlocker on Nyloc nuts or on the switch nuts.

## 6. Coating and labels

After the bench fit, two thin coats of acrylic conformal coating on A, B, D and E1 with the masks of `docs/ASSEMBLY.md` section 5 (connector faces, the spring pins and their targets, SMA bodies, the DMR858M sockets, the Pi and X1202 areas, the test points). The panel face is not coated; its underside cluster is, with `J_PANEL` masked. Labels per section 6: the panel nameplate with P/N MSK-FK-1520, S/N, REV A and a data matrix; P/N, S/N, REV silk fields on every board.

## 7. Software

The Pi provisioning is the V1 sequence in `../v1/BUILD.md` section 7 (Ubuntu Server 24.04, config.txt overlays, the EEPROM current setting, the kernel pin, the Bridge in standalone mode, the host services). On top of it, for the panel and the dock:

- `config.txt`: SPI0 with one chip select and no MISO for the e-paper (`dtoverlay=spi0-1cs,no_miso`), the PWM overlay for the LED rail and the sounder (`dtoverlay=pwm-2chan`), I2C on.
- I2C map: PCA9555 at 0x21 on PCB-A (USB eFuse enables and current-sense flags, `SHORE_INHIBIT` on port 0 bit 4), 0x22 and 0x23 on the panel (LED sinks, switches, e-paper reset and busy, sounder enable), the X1202 gauge at 0x36, the INA219 on PCB-A. The bit maps are in `docs/PANEL.md` section 1.
- Pi GPIO through the panel ribbon (`docs/PANEL.md` section 2): BCM 12 LED rail PWM, BCM 13 sounder, BCM 8/9/10/11 e-paper SPI with D/C on 9, BCM 7 alternative e-paper reset, BCM 6 the X1202 AC-loss line as before.
- Indicator, control, lighting and e-paper behaviour: `docs/PANEL.md` sections 3 to 7 are the contract the Bridge implements (MESHSAT-773); until that lands the panel's MAIN PWR ring (on the switched 5 V rail) and the TX lamp (hardware from the PTT mirror) work without software, everything else stays dark.
- The dock's shore inhibit is driven by the Bridge through the 0x21 expander (`docs/PANEL.md` section 9): asserting it drops the dock's 12 V within a second, the kit keeps running from the battery node.

## 8. Bring-up checks

From `docs/ASSEMBLY.md` section 8, after assembly (the full commissioning list, including the module-rail and burst checks, is there): E1 gives 12 V at the targets with 9, 12, 24 and 36 V in, survives reverse polarity for 10 s and blows its fuse on a bolted short; the lamp test lights all 17 LEDs, BLACKOUT kills the rail, the EMCON cover closed keeps the DMR858M in receive while the Bridge asserts PTT; `gpioget --bias=pull-up gpiochip4 6` follows the shore input; the shore inhibit drops and restores the dock 12 V and the kit keeps running inhibited (record the current, it sets the survival time on shore power); at full load measure the current on each of the three GND spring pins (about 1.1 A each at 40 W) against the pin's rating. Then the V1 checks (`../v1/BUILD.md` section 8) for the radios, the modem, the display and the demo.

Removal for maintenance (`docs/ASSEMBLY.md` section 7): lid, 16 screws, ribbon and two leads, panel out, seven pigtails at the strip, lift the A+B stack straight up; the south rods through the dock strip align the spring pins on refit.

## 9. Known gaps of Rev A

- RF is not blind-mate: the seven paths go through SMA couplers on the wall strip and must be unscrewed to lift the stack out. SMP blind-mate is Rev B (MESHSAT-775).
- The spring-pin return path is three pins; confirm the pin rating before the first full-load run (section 8).
- The module rail's boost (TPS61089, 10 A peak limit) carries one bearer burst at a time over the whole discharge; three at once is tolerated only above about 3.8 V cell voltage, and the bridge serialises them (`docs/PANEL.md` section 10). The TPS61288 is the Rev B option if that ever matters.
- The panel switch parts, the SMA coupler for E2 (its D-hole flat follows the part) and the dock spring pin (the footprint drill follows the part) are not yet named.
- The commissioning list (MESHSAT-774) and the panel software (MESHSAT-773) are open.
- The DMR858M carrier (PCB-D) has not been powered yet; the modules arrive mid September 2026 and the first bring-up uses the AIOC as a temporary codec into the existing Direwolf pipeline.
- Nothing here has been built. Report what does not fit on MESHSAT-709.
