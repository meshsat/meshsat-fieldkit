# Building a V2 kit from this repository

Rev A of the carrier set has been designed, reviewed and prepared for order; no kit has been built from it yet. This page is the path from an empty JLCPCB cart to a running kit, in order, pointing at the documents that carry the detail. Read it together with `docs/ASSEMBLY.md` (fasteners, build order, the pack, leads, coating, labels, removal, bench checks, bench-fit lists) and `docs/PANEL.md` (what the software does with the panel). The design record with every number and every ruling is `docs/MESHSAT-709-geometry-appendix.md`, section 25 for the current design.

MeshSat is a prototype. The V2 boards have not been fabricated; expect changes after the first build.

## 0. Before you start

- Three rulings are not open for redesign: the kit carries its own charger, fuel gauge and power control on PCB-A, with the cells in a battery module on the case floor that blind-mates through the dock; EMCON is a hardware line from the panel toggle to the APRS PTT driver plus a software hold; the panel is driven per `docs/PANEL.md`.
- Nothing on the bench gates the first order (appendix 32): every COTS site was checked against the manufacturer's own drawing, and the documents are in `vendor/`.
- The panel software (expanders, LED semantics, e-paper, sounder) is specified in `docs/PANEL.md` but not yet written in the Bridge (MESHSAT-773). A Rev A kit powers up and runs the Bridge; the panel lights and switches come alive with that software.

## 1. Order the boards

Seven boards, five assembled by the fabricator (top side, standard assembly; the economic tier is not offered for these boards), two bare. Everything you upload is in `release/revA/order/<board>/`: the Gerber zip, the JLC-format BOM and CPL (rotation offsets already applied, bench-fitted parts removed, designator ranges expanded) and `ORDER-NOTES.txt` with the exact settings. `ORDER-LOG.md` in the same folder records the 3 September 2026 run line by line, including what JLCPCB's checks answered.

| Board | Folder | Size (mm) | Layers | Stackup | Assembly |
|---|---|---|---|---|---|
| PCB-A POWER + I/O A19 | `PCB-A-POWER-A19/` | 285 x 160 | 4 | JLC04161H-7628 | top |
| PCB-B COMPUTE B12 | `PCB-B-COMPUTE-B12/` | 245 x 170 | 4 | JLC04161H-7628 | top, bottom 1 |
| PCB-C CONTROL PANEL C4 | `PCB-C-DISPLAY-C4/` | 442 x 311 | 2 | standard | top 18, bottom 70 |
| PCB-C SPACER RING R1 | `PCB-C-RING-R1/` | 106 x 54 | 2 | standard, 1.0 mm | none |
| PCB-D APRS D5 | `PCB-D-APRS-D5/` | 80 x 62 | 4 | JLC04161H-7628 | top 78, bottom 1 |
| PCB-E1 DOCK STRIP E4 | `PCB-E1-DOCK-E4/` | 278 x 60 | 4 | JLC04161H-7628 | top |
| PCB-E5 DOCK BLOCK E5 | `PCB-E5-BLOCK-E5/` | 43 x 26 | 2 | standard, 2 oz outer copper | none |

Common settings, from the ORDER-NOTES: 1.6 mm FR-4 (the ring 1.0 mm), 1 oz outer copper, ENIG, matte black solder mask, white silkscreen, no castellations, order number removed, quantity 5 (the JLCPCB minimum). The four-layer boards carry USB 2.0 pairs at 0.2 mm track and 0.15 mm gap on the outer layers; ask for 90 ohm differential tuning on the 7628 stackup. Turn both free confirmation options on (production file review and the BOM/CPL confirmation) so the placement preview is checked before anything is cut. On the JLC preview, check the rotation of every polarised part against `release/revA/review/<board>/*-assembly-top.pdf`.

Parts JLCPCB does not fit are listed per board in the ORDER-NOTES ("fitted at the bench") and in `docs/ASSEMBLY.md` section 9. If JLCPCB has no stock for a line at order time (the Keystone 3568 fuse holders and the two white 3 mm LEDs were short in September 2026), let it drop to DNP and fit it at the bench.

If you change a board first, regenerate it (`README.md`, "Regenerating a board"), then run `make_handoff.py`; it rewrites `order/` and `review/`. JLCPCB cannot swap Gerbers in an existing cart line, so batch changes before uploading.

## 2. Everything else to buy

Case and frame: Peli 1520EU without foam and the 1520PF special application panel frame (the frame kit brings the inserts; confirm the insert thread against the M3 x 8 screws before ordering fasteners). Orange was chosen for the kits.

Modules that mount on the boards (one kit): Raspberry Pi 5 8 GB with active cooler, LilyGO T-Call A7670E, LilyGO T-Beam 1W (LoRa), RTL-SDR Blog V4, ZigBee CC2652P USB coordinator, RockBLOCK 9704 (or 9603) with the Ground Control bracket, Seeed Wio-SX1262, Raspberry Pi Touch Display 2, WeAct 3.7 inch e-paper, a GPS puck and a WiFi dongle on the USB-A receptacles. There is no separate uninterruptible supply module: PCB-A is the charger, the gauge and the power control.

Battery module: twelve Samsung INR18650-35E in parallel (1S12P, 40.2 Ah minimum from the specification, about 0.6 kg of cells), 0.15 x 8 mm nickel strip, fish paper, blue PVC sleeve, a Littelfuse MAXI 40 A blade with its in-line holder on the positive lead, an Amass XT60 pair on 12 AWG silicone, and a Semitec 103AT-2 thermistor taped to a cell for the charger's temperature window. The single-cell protection board is the documented Batteryspace PCB-LIS1A15 (15 A continuous, 20 A for five minutes, 35 A trip, 65 x 10 x 2.5 mm; appendix 32.31). An RS PRO 245-556 silicone heater mat (50 x 150 mm, 12 V, 7.5 W, self-adhesive) goes under the cells; PCB-A runs it from shore power below 0 C. Spot welder or a shop that welds packs. The module lives in a printed enclosure in a cradle on the case floor and plugs into the dock strip, so it is not strapped to a board.

Solar (optional): a bare 12 V class photovoltaic panel of your choice, up to about 40 W, wired to the second contact pair of the shore plug; the tracker on the dock strip regulates it (appendix 32.16 F). No panel part is prescribed.

Hardware per `docs/ASSEMBLY.md` section 1: four M3 stainless rods with Nyloc nuts, spacers for the 13.4 mm dock gap, 35 mm and 59 mm bay spacers, four M2.5 x 22 female-female standoffs with M2.5 x 6 screws for the Pi, four M3 x 6 standoffs for the raised dock block, 16 x M3 x 8 pan head for the panel frame.

Consumables: 3M 467MP or 9495LE transfer tape (display and e-paper), 3M VHB 5952 pads (dock strip), MG Chemicals 422B acrylic conformal coating, kapton for the masks, IPA.

Electrical: the Preci-Dip 813-S1-012-10-016101 spring-loaded connector for `J_DOCK` (2 x 6 at 2.54 mm, 7.0 mm high, solder tails), nine Mill-Max 0858 class 9 A spring pins for the module contacts and the pre-charge pin, seven Radiall R222M00720 receptacles with their R222M80500 right-angle plugs for the blind-mate RF, Keystone 3568 mini blade holders with three 10 A and one 15 A blade on PCB-A and a 7.5 A plus a 10 A on the dock strip, three 18 AWG JST-VH leads for the rails from PCB-A to PCB-B (the Pi lead ends in a USB-C plug), twelve hook-up wires and a 12 AWG pair from the dock strip up to the contact block.

External cables (`docs/ASSEMBLY.md` section 4): Glenair D38999/26FC4SN plug with its size 16 socket contacts and the M85049/38S13N strain relief, 2 m of Lapp OLFLEX ROBUST 210 4 x 1.0 (or Alpha Wire 25064), the crimp tool M22520/1-01 with positioner M22520/1-04 if you do not have a shop crimp them; a Glenair 233-340 USB plug with its 770-028 boot and a 1.5 m USB 2.0 A-male to A-female extension.

Panel hardware: two 19 mm and 16 mm anti-vandal switches with LED rings (SW_MAIN C&K ATP19-SL1-603-B0SA-03G green, SW_PI C&K ATP16-SL1-403-M0SA-04G orange as the amber, SW_TEST C&K ATP16-SL1-203-M0SA-04G white; solder lugs, gold, 3 V ring type because C4's 470 and 300 ohm resistors set the ring current), one DPDT ON-ON-ON sealed toggle (SW_LIGHT NKK M2044SD3A01 with the AT401A boot), three locking toggles APEM 5636ADKB-2V (SW_SOS, SW_EMCON, SW_ZERO: single pole ON-NONE-ON with both positions locked, pull the lever before it moves; gold-plated contacts, front-panel seal, epoxy terminals, 1/4-40 bushing in the same 6.5 mm holes; owner ruling of 4 Sep 2026, design record 32.13; SOS and ZEROIZE are maintained switches, the bridge acts after 2 s / 5 s in position), seven Amphenol Connex 132170 SMA bulkhead couplers for the junction strip, an 85 dB piezo if not fitted by JLCPCB, the two white 3 mm LEDs D10 and D11.

## 3. Prepare the case

1. Fit the 1520PF frame per Peli's instructions; its 16 inserts are the panel's screw pattern (431.8 x 301.2 mm, appendix 25.1).
2. Junction strip E2 goes on the +Z wall between the wall ribs: six M3 wall screws into the 1520's drill points (self-tapping brass inserts or nuts inside the wall recess), seven SMA bulkheads in the wall next to it on the strip's D-hole pattern (6.5 mm). The strip's lower coupler sides face the wall pigtails, the upper sides the device pigtails.
3. Shore inlet: the IP68 2-pin bulkhead on the -Z wall, lead to the dock's `J_DCIN` (JST-VH, 18 AWG, 400 mm).
4. Dock strip E1 on the floor: degrease with IPA, four VHB pads at the corners, locate it by dropping two rods through its south rod holes before the pads touch.
5. Bulkhead legend strip (UHF SDR WIFI1 WIFI2 LTE IRID LORA) beside the SMA row, the "RF HAZARD DURING TX" label next to the UHF bulkhead, the asset label in Peli's recess (`docs/ASSEMBLY.md` section 6).

## 4. The battery module

The cells are no longer strapped to a board. Twelve INR18650-35E are welded in parallel, sleeved, fused at the positive terminal with a 40 A MAXI blade in its in-line holder, and terminated in an XT60 pair on 12 AWG. A 103AT-2 thermistor goes on a cell and its pair runs to the dock, because the charger on PCB-A holds the Samsung charge window of 0 to 45 C from that reading. The module sits in a cradle on the case floor beside the dock strip and plugs into the strip, so it can be lifted out on its own.

Charge time is set by the charger on PCB-A at 3 A, which is about 14 hours for a flat pack plus the constant voltage tail, and the gauge on the same board reports state of charge over the panel. Nothing on the bench has to be measured before the module is built (appendix 32.3 and 32.27).

Two figures worth keeping straight: the pack is 40.2 Ah at the specification minimum and about 41.5 Ah typical, not the 42 Ah of the early notes, and twelve cells are 600 g at the specification maximum, so the finished module is about 0.7 kg.

## 5. Assemble

Follow `docs/ASSEMBLY.md` section 2 step by step; the short form:

1. Dock strip E4: solder the leads, fit the TRACO TEN 40-2412WIN, the two fuse holders with a 7.5 A and a 10 A blade, and check 12 V at the block lands with 9 V and 36 V in. Then fit the raised block E5 on its four 6 mm standoffs, solder the twelve signal wires and the 12 AWG pair from the strip into the block's plated lands from below, and stick the strip down on its VHB pads.
2. Rods through the strip's holes with the spacers that set the 13.4 mm gap (washer stack under the two north rods so all four sit level).
3. PCB-A A19: solder the Preci-Dip 813-S1-012-10-016101 connector and the nine Mill-Max power pins in from the underside (tails on the top face), fit the seven blind-mate receptacles, then the blade fuses before anything is energised. Lower the board onto the rods so its pins land on the block, and check continuity from the block's lands to the board with a meter before the first power-up.
4. 35 mm spacers, PCB-B B12 with the Pi 5 on its 22 mm standoffs (HDMI edge west, GPIO header edge east, SD card south), the three rail leads from PCB-A into `J_5V_M1`, `J_5V_M2` and `J_5V_PI` (the Pi lead ends in a USB-C plug), the modules, the panel ribbon in `J_PANEL` and the 2x7 ribbon in `J_AB1`. Nyloc on top.
5. Battery module into its cradle, thermistor pair and the XT60 into the dock strip. The module's own fuse is at its positive terminal, so it is fused before the cable.
6. RF: the seven right-angle plugs sit in their printed clamps on the dock strip and mate blind with the receptacles under PCB-A when the stack is lowered. The wall connectors are the MIL-DTL-38999 receptacles; their pigtails are torqued once at the wall side and finger tight at the device side, RG-316 with a 12.5 mm bend radius, tied at both ends.
7. Panel C4: switches with their boots (APEM locking levers on SOS, EMCON and ZEROIZE), the e-paper module taped face-up under its window (spacer ring R1 first if a flush face is wanted, header to the east, 2x4 lead to `J_EPD`), the Touch Display 2 glass taped over its aperture, then the 16 frame screws.
8. Lid: the lid foam is pocketed over the switch strips (nothing on the panel face is taller than 20 mm).

Torque table, threadlocker rules and every lead's wire gauge, length and connector are in `docs/ASSEMBLY.md` sections 1 and 4. Never put threadlocker on Nyloc nuts or on the switch nuts.

## 6. Coating and labels

After the bench fit, two thin coats of acrylic conformal coating on A, B, D and the dock strip with the masks of `docs/ASSEMBLY.md` section 5 (connector faces, the spring pins and their targets, SMA bodies, the DMR858M sockets, the Pi area, the test points). The panel face is not coated; its underside cluster is, with `J_PANEL` masked. Labels per section 6: the panel nameplate with P/N MSK-FK-1520, S/N, REV A and a data matrix; P/N, S/N, REV silk fields on every board.

## 7. Software

The Pi provisioning is the V1 sequence in `../v1/BUILD.md` section 7 (Ubuntu Server 24.04, config.txt overlays, the EEPROM current setting, the kernel pin, the Bridge in standalone mode, the host services). On top of it, for the panel and the dock:

- `config.txt`: SPI0 with one chip select and no MISO for the e-paper (`dtoverlay=spi0-1cs,no_miso`), the PWM overlay for the LED rail and the sounder (`dtoverlay=pwm-2chan`), I2C on.
- I2C map: PCA9555 at 0x21 on PCB-A (USB eFuse enables and current-sense flags, `SHORE_INHIBIT` on port 0 bit 4), 0x24 on PCB-A as well (the second expander), 0x22 and 0x23 on the panel (LED sinks, switches, e-paper reset and busy, sounder enable), the BQ34Z100-G1 fuel gauge and the BQ25792 charger on PCB-A, the INA219 on PCB-A. The bit maps are in `docs/PANEL.md` section 1.
- Pi GPIO through the panel ribbon (`docs/PANEL.md` section 2): BCM 12 LED rail PWM, BCM 13 sounder, BCM 8/9/10/11 e-paper SPI with D/C on 9, BCM 7 alternative e-paper reset, BCM 6 the shutdown request from the power controller on PCB-A.
- Indicator, control, lighting and e-paper behaviour: `docs/PANEL.md` sections 3 to 7 are the contract the Bridge implements (MESHSAT-773); until that lands the panel's MAIN PWR ring (on the switched 5 V rail) and the TX lamp (hardware from the PTT mirror) work without software, everything else stays dark.
- The dock's shore inhibit is driven by the Bridge through the 0x21 expander (`docs/PANEL.md` section 9): asserting it drops the dock's 12 V within a second, the kit keeps running from the battery node.

## 8. Bring-up checks

From `docs/ASSEMBLY.md` section 8, after assembly (the full commissioning list, including the module-rail and burst checks, is there): the dock strip gives 12 V at the block lands with 9, 12, 24 and 36 V in, survives reverse polarity for 10 s and blows its fuse on a bolted short; the lamp test lights all 17 LEDs, BLACKOUT kills the rail, the EMCON cover closed keeps the DMR858M in receive while the Bridge asserts PTT; `gpioget --bias=pull-up gpiochip4 6` follows the shore input; the shore inhibit drops and restores the dock 12 V and the kit keeps running inhibited (record the current, it sets the survival time on shore power); at full load measure the current on each of the three GND spring pins (about 1.1 A each at 40 W) against the pin's rating. Then the V1 checks (`../v1/BUILD.md` section 8) for the radios, the modem, the display and the demo.

Removal for maintenance (`docs/ASSEMBLY.md` section 7): lid, 16 screws, ribbon and the rail leads, panel out, then lift the A+B stack straight up. Nothing has to be unscrewed at the radio side any more: the seven RF joints and the power contacts part as the stack rises, and the rods through the dock strip line them up again on refit.

## 9. Known gaps of Rev A

- Nothing here has been built and no board has been fabricated. Report what does not fit on MESHSAT-709.
- The spring-pin return path is three contacts at about 1.1 A each, inside the Preci-Dip contact's 3.5 A rating; the module current runs on the separate 9 A pins.
- The commissioning list (MESHSAT-774) and the panel software (MESHSAT-773) are open. A Rev A kit powers up and runs the Bridge; the panel lights and switches come alive with that software.
- The DMR858M carrier (PCB-D) has not been powered yet; the modules arrive mid September 2026 and the first bring-up uses the AIOC as a temporary codec into the existing Direwolf pipeline.
- The case wall receptacles and the battery module cradle are drawn and modelled (`release/revA/case/`, `release/revA/module/`) but nothing has been cut or printed.
