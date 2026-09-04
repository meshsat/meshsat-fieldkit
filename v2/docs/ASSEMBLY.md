# MeshSat Field Kit carrier set: assembly, fasteners, coatings, removal (Rev A, MESHSAT-709)

Companion to `MESHSAT-709-geometry-appendix.md` (sections 14.6, 22, 25, 32). Boards: PCB-A POWER + I/O (**A19**), PCB-B COMPUTE (**B12**), PCB-C CONTROL PANEL (**C4**), PCB-C spacer ring (R1, optional), PCB-D APRS (D5), PCB-E1 DOCK STRIP (**E4**), PCB-E5 DOCK BLOCK (**E5**). Nothing here has been built; this is how the first set is meant to go together.

A19 and B12 replaced A18 and B11 on 5 September 2026 after the rulings of appendix 32: the separate uninterruptible supply module is gone, PCB-A carries the charger, the fuel gauge, three 5 V converters and the main power control, PCB-B carries the Pi alone, and the cells left the boards for a battery module on the case floor that blind-mates through the dock. E4 is the dock strip that grew to four layers with a solar tracker, and E5 is the small raised block on it that presents the contacts the stack lands on.

## 1. Fasteners

| Joint | Fastener | Torque | Locking |
|---|---|---|---|
| Rod stack, 4 x | M3 stainless threaded rod, floor to the top nut above PCB-B; spacer tubes on the dock strip that set the 13.4 mm blind-mate gap under PCB-A; 35 mm and 59 mm bay spacers | 0.5 N m | Nyloc nuts top and bottom, no threadlocker on Nyloc |
| Panel to frame, 16 x | M3 x 8 pan head stainless into the frame inserts (confirm the insert thread from the kit; Ø5.2 bore) | 0.4 N m | Loctite 243, one drop |
| Junction strip to wall, 6 x | M3 x 12 pan head into the 1520 wall drill points (self-tapping brass inserts or M3 nuts inside the wall recess) | 0.3 N m | Loctite 243 |
| PCB-D on PCB-A, 4 x | M3 x 6 into the four standoffs at (10, -26), (80, -26), (10, 26), (80, 26) | 0.5 N m | Loctite 243 |
| DMR858M on PCB-D, 2 x | M2.5 x 11 standoff + M2.5 x 4 screw, connector-end fixed, module on the two 1x12 female headers | 0.3 N m | Loctite 243 |
| Touch Display 2 lugs | not used; the glass is taped (section 14.6): 3M 467MP or 9495LE, 0.05 mm, full flange | | |
| E-paper under PCB-C | WeAct 3.7 module face-up under the panel, glass through the 94.19 x 53.6 window, its two side lands (5.8 mm) taped to the panel underside with 3M 9495LE; for a flush face the 1.0 mm spacer ring (pcb-c-ring R1) taped on both sides between land and panel; no screws | | tape |
| Panel switches | supplied nuts, IP67 boots, guards oriented so the cover opens toward the operator | hand tight + 1/8 turn | none |
| Dock strip to floor | 4 x 3M VHB 5952 pads 20 x 20 at the corners, floor degreased with IPA | | |
| Blade fuses F2 to F5 on PCB-A | 10 A mini blade in F2 (cell node to `J_MEZZ_PWR1`), 10 A in F3 and F4 (node to the M1 and M2 converters), 15 A in F5 (node to the Pi converter), into Keystone 3568 holders | push fit, seated flush, no torque | none; check seating after any transport |
| Pi 5 on PCB-B, 4 x | M2.5 x 22 female-female standoffs on the 49 x 58 pattern, M2.5 x 6 screws from below (the pattern is unchanged from the earlier stack; nothing sits under the Pi now) | 0.2 N m | Loctite 243 on the standoff thread only |
| Pack to PCB-A | two 7.6 mm cable ties through the 25 x 4 slots at (-95, +-43), over the shrink sleeve, 1 mm silicone sheet under the pack | | |

Threadlocker: Loctite 243 (medium, oil tolerant) on every machine screw into metal; never on Nyloc nuts, never on the plastic-bodied switch nuts.

## 2. Build order

1. Dock strip E4: solder the entry leads (shore pair to J_DCIN, panel pair to J_SOLAR, VH crimps), fit the TRACO TEN 40-2412WIN, the two fuse holders with a 7.5 A and a 10 A blade, and check 12 V at the block lands with 9 V and 36 V in. The EL817 optocoupler and the tracker are fitted by the assembler.
2. Dock block E5 on its four M3 x 6 standoffs above the strip, face at 7.4 mm. Solder the twelve signal wires and the 12 AWG pair from the strip into the block's plated lands from below; the block's underside legend names every land. Check each wire end to end before the stack goes on, because the lands are covered once PCB-A is down.
3. Rods: four M3 rods through the floor holes of the strip, then the spacers that set the 13.4 mm gap on all four rods, so PCB-A's spring pins land on the block with the pins compressed about 1 mm.
4. PCB-A A19 with the Preci-Dip 813-S1-012-10-016101 connector and the nine Mill-Max 0858 class power pins soldered in from the underside (tails on the top face), the seven Radiall receptacles fitted, and the blade fuses in before anything is energised. Lower it onto the rods and check continuity from the block's wire lands up to the board.
5. 35 mm spacers, PCB-B B12 with the Pi 5 on its 22 mm standoffs in the orientation of section 1, the modules, the three rail leads into J_5V_M1, J_5V_M2 and J_5V_PI, the panel ribbon into J_PANEL and the 2x7 ribbon into J_AB1. Nyloc on top.
6. Battery module into its cradle on the floor, XT60 into the strip's J_BATT, thermistor pair into J_TS. The 40 A blade sits at the module end, so the cable is protected at the source.
7. RF: the seven right-angle plugs sit in their printed float clamps on the strip and mate with the receptacles under PCB-A as the stack comes down. The wall pigtails run from the clamps to the MIL-DTL-38999 receptacles, torqued once at the wall side and finger tight at the device side.
8. Panel C4: switches with their boots (APEM locking levers on SOS, EMCON and ZEROIZE), the e-paper module taped under its window (ring first if used, then the module, header to the east, 2x4 socket lead to J_EPD), the display glass taped, ribbon and the two XH leads plugged, then the 16 frame screws.
9. Lower the lid; the lid foam is pocketed over the switch strips (nothing on the panel face taller than 20 mm above it).

## 3. The battery module

Twelve Samsung INR18650-35E in parallel (1S12P), spot-welded nickel strip 0.15 x 8 mm, cells side by side in a flat three-row by four-column block, fish paper at both ends, blue PVC sleeve. Wrapped, the block is about 75 x 198 x 20 mm and about 640 g; complete with its protection board, fuse, holder and connector, about 0.7 kg. Capacity is 40.2 Ah at the specification minimum and about 41.5 Ah typical (appendix 32.27).

The module is a unit of its own, not a part of a board: it sits in a cradle on the case floor beside the dock strip and connects through one XT60 pair on 12 AWG and one thermistor pair. On the positive lead, at the module, sit a Littelfuse MAXI 40 A blade and its in-line holder, so the cable is protected at the source. A Semitec 103AT-2 thermistor is taped to a cell in the middle of the block and its pair runs out with the power leads, because the charger on PCB-A holds the Samsung charge window of 0 to 45 C from that reading.

The single-cell protection board is not chosen yet. No documented off-the-shelf module reaches 30 A continuous, so it is either a small board built around a TI BQ29700 with two CSD17570Q5B switches back to back, or a documented 15 A module with the requirement relaxed (appendix 32.27, MESHSAT-791).

Samsung's specification forbids soldering to the cell can: the cells are welded and the leads are soldered to the strip, never to a cell.

## 4. Leads

| Lead | From | To | Wire | Connector |
|---|---|---|---|---|
| Module power (**fused at the module: 40 A MAXI blade**) | battery module XT60 | dock strip J_BATT (XT60) | 12 AWG silicone, 300 mm | XT60 pair |
| Module thermistor | 103AT-2 on a cell | dock strip J_TS (XH2.5) | 26 AWG twisted, 300 mm | XH2.5 |
| Shore inlet | MIL-DTL-38999 receptacle on the -Z wall, DC pair | dock strip J_DCIN (JST-VH) | 18 AWG, 400 mm | VH crimp |
| Solar inlet | MIL-DTL-38999 receptacle, panel pair | dock strip J_SOLAR (JST-VH) | 18 AWG, 400 mm | VH crimp |
| Block signal wires | dock strip J_BLK (twelve lands) | dock block wire lands, underside | 24 AWG, 60 mm each, named on the block's legend | soldered both ends |
| Block power pair | dock strip P_CP and P_CN | dock block wire holes | 12 AWG silicone, 60 mm | soldered both ends |
| MAIN button | PCB-C J_MAINSW (XH2.5) | PCB-A J_MAINSW (XH2.5) | 24 AWG twisted | XH2.5 both ends |
| PI switch | PCB-C J_PIJ2 (XH2.5) | Pi 5 J2 pads | 24 AWG twisted | XH2.5 |
| Panel ribbon | PCB-B J_PANEL | PCB-C J_PANEL | 20-way 1.27 ribbon, 350 mm | IDC 2x10 both ends |
| A to B ribbon | PCB-A J_AB1 | PCB-B J_AB1 | 14-way 1.27 ribbon, 200 mm | IDC 2x7 both ends |
| Mezz harness | PCB-A J_MEZZ1 | PCB-D J_HARN1 | 16-way ribbon | IDC 2x8 |
| Mezz power (**fused at source: F2, 10 A, on A19**) | PCB-A J_MEZZ_PWR1 (VH) | PCB-D boost input | 18 AWG | VH |
| Rail M1 (**F3, 10 A**; hub, display, panel, LTE) | PCB-A J_5V_M1 (VH) | PCB-B J_5V_M1 (VH) | 18 AWG, 150 mm | VH crimp both ends |
| Rail M2 (**F4, 10 A**; SDR, ZigBee, LoRa, RockBLOCK) | PCB-A J_5V_M2 (VH) | PCB-B J_5V_M2 (VH) | 18 AWG, 150 mm | VH crimp both ends |
| Pi rail (**F5, 15 A**; 5.1 V, 5 A) | PCB-A J_5V_PI (VH) | Pi 5 USB-C power input | 18 AWG, 200 mm | VH at PCB-A, USB-C plug at the Pi |
| Heating pad | PCB-A J_HEAT (XH2.5) | pad on the battery module | 20 AWG, 350 mm | XH2.5 |
| Wall USB | PCB-A J_WALL1 (USB-A) | Glenair 233-370 wall receptacle | USB 2.0 cable, 300 mm | USB-A both ends |
| RF pigtails | device SMA on B / D | PCB-A J_RF1 to J_RF7 (SMA jacks) | RG-316, bend radius 12.5 mm | SMA male |
| Blind-mate jumpers | dock strip float clamps (Radiall R222M80500 right-angle plugs) | MIL-DTL-38999 wall receptacles | RG-316 | SMP-MAX at the clamp, wall connector at the other end |

Every lead tied at both ends; the rod stack's edge carries the vertical runs with a tie base per bay.

The dock interface is not a lead but belongs in the same reading. Twelve Preci-Dip 813 contacts in `J_DOCK` on A19's underside land on the raised block's targets: pins 1 to 4 are `SHORE_12V`, 5 to 7 and 10 are ground, 8 is `SHORE_INHIBIT`, 9 the module thermistor, 11 the cell sense and 12 spare. Beside them, nine Mill-Max 0858 class pins carry the module current: four on `CELL+`, four on the return, and one longer pre-charge pin that mates first through a 10 ohm resistor so the converters' input capacitance does not draw an arc across the main pins. The seven RF joints mate at the same time, and the whole set parts when the stack is lifted.

## 5. Conformal coating

IPC-CC-830 acrylic (MG Chemicals 422B or equal) on A, B, D and the dock strip after the bench fit, two thin coats. Masks (kapton) before coating: every connector face and its keying, the spring-pin targets on E1 and the pins on A, the SMA bodies, the DMR858M sockets, the X1202 and Pi stack areas (assembled parts are not coated), the test points that the bench list uses. PCB-C is not coated on the face (switch and tape band); the underside cluster is coated with J_PANEL masked. E2 has no copper.

## 6. Labels (MIL-STD-130 style)

- Panel nameplate field (0, -110), 76 x 26: "MESHSAT FIELD KIT", P/N MSK-FK-1520, S/N, REV A, a 10 x 10 mm data matrix with the S/N, "MADE IN NL".
- Every board: P/N, S/N, REV silk fields near the title block silk.
- Case: asset label on Peli's label recess; "RF HAZARD DURING TX" 20 x 40 mm next to the UHF bulkhead; the bulkhead legend strip (UHF SDR WIFI1 WIFI2 LTE IRID LORA) beside the SMA row.

## 7. Removal and refit

Appendix 25.3: lid, 16 screws, ribbon + two leads, panel out, seven pigtails at the strip, lift the A+B stack straight up. Refit in reverse; the south rods through the dock strip's holes align the spring pins.

## 8. Commissioning after assembly (appendix 32.3: no bench item gates the order)

The bench items that once hung on the separate supply module are gone with it: the charger, the gauge and the power control are on PCB-A and are commissioned with the rest of the board. The list below is what to check once, in this order, on the first kit.

1. Dock strip alone: 12 V at the block lands with 9, 12, 24 and 36 V in; reverse polarity applied for 10 s (no damage, no output); the fuse blows on a bolted short. Then the tracker: a panel or a bench supply through a series resistor, and the tracking point holds while the load changes.
2. Dock block alone, before the stack goes on: continuity from every wire land to its target, and no continuity between neighbours. This is the last moment the lands are reachable.
3. PCB-A alone, module not connected: a bench supply at 3.6 V on the CELL+ contacts through a 5 A limit. Each rail comes up at its own converter (M1 and M2 at 5.05 V within 0.1 V, the Pi rail at 5.1 V); 2 A drawn from each holds it above 4.9 V. The charger enumerates on the bus, the gauge reads the node voltage, and the main power control turns the rails off and on from the MAIN button.
4. Charge: 12.0 V on the shore inlet, the module's thermistor connected. The charger takes about 3 A into the pack and holds the 0 to 45 C window: warm the thermistor above 45 C by hand and the charge current stops, cool it and it resumes.
5. The stack with PCB-B: the Pi boots from its own rail, and both module rails stay up with every radio idle. Record each rail's current at idle and with the display on.
6. Bursts: LTE registration, one Iridium session and one LoRa transmission in turn, each rail watched at its connector, then all three within the same second. With three converters there is no serialisation rule left to test, so what is being recorded is the margin, not a limit.
7. Panel: lamp test lights all 17 LEDs; BLACKOUT kills the rail; the EMCON toggle locked closed keeps the DMR858M in receive while the bridge asserts PTT.
8. Power loss: pull the shore lead and confirm the power-loss line changes state at the Pi, and that the kit keeps running from the module.
9. Shore inhibit: `SHORE_INHIBIT` high drops the dock 12 V within a second, low restores it, and the converter stays on with the stack lifted.
10. Blind-mate: lift the stack and set it back three times. Every RF path still passes, the pre-charge pin still mates first, and nothing on the block is scored.

## 9. Bench-fit lists (hand-fitted parts per board, not on the JLC BOM)

- PCB-A A19: the Preci-Dip 813-S1-012-10-016101 spring connector and the nine Mill-Max 0858 class power pins on the underside (tails soldered on the top face), the seven Radiall R222M00720 blind-mate receptacles, the four Keystone 3568 blade holders with three 10 A and one 15 A mini blade, the Coilcraft inductors L2 to L4 (XAL1010-222MED, one per converter), L5 (XAL4030-222MEB) and L6 (XAL4020-332MEB), which have no assembler equivalent, the 0603 thermistor RT1 if it is short at order time, the three rail leads, the heating pad lead, the LED row lead, the MAIN button lead, the seven SMA pigtails, and the USB cable from J_WALL1 to the wall receptacle.
- PCB-B B12: Pi 5 on the 49 x 58 pattern on four M2.5 x 22 standoffs (HDMI edge west, header edge east, SD card south), the three rail leads from PCB-A, the module carriers, the panel ribbon and the 2x7 ribbon to PCB-A.
- PCB-C C4: the two white 3 mm LEDs D10 and D11 (no LCSC stock at order time), two 19 mm and 16 mm anti-vandal switches with LED rings (SW_MAIN C&K ATP19-SL1-603-B0SA-03G green, SW_PI C&K ATP16-SL1-403-M0SA-04G orange as the amber, SW_TEST C&K ATP16-SL1-203-M0SA-04G white; solder lugs, gold, 3 V ring type because C4's 470 and 300 ohm resistors set the ring current), one DPDT ON-ON-ON sealed toggle (SW_LIGHT NKK M2044SD3A01 with the AT401A boot), three locking toggles APEM 5636ADKB-2V (SW_SOS, SW_EMCON, SW_ZERO: single pole ON-NONE-ON with both positions locked, pull the lever before it moves; gold-plated contacts, front-panel seal, epoxy terminals, 1/4-40 bushing in the same 6.5 mm holes; owner ruling of 4 Sep 2026, design record 32.13; SOS and ZEROIZE are maintained switches, the bridge acts after 2 s / 5 s in position), the WeAct 3.7 e-paper module taped under the recessed window (optional 1.0 mm spacer ring pcb-c-ring) with a 2x4-to-1x8 lead to J_EPD, the Touch Display 2 on transfer tape, the piezo sounder if not JLC-fitted, the two XH leads.
- PCB-D D5: DMR858M on two 1x12 female headers and two M2.5 x 11 standoffs, heatsink up, SMA pigtail, the boost inductor L1 (Coilcraft XAL6030-152MEB, no JLC equivalent, hand-soldered; the ordering session left its line unticked).
- PCB-E1 dock strip E4: TRACO TEN 40-2412WIN, two Keystone 3568 holders with a 7.5 A and a 10 A mini blade, the JST-VH shore and panel leads, the XT60 module entry, the twelve signal wires and the 12 AWG pair up to the block, the seven printed float clamps with their Radiall R222M80500 plugs, four VHB pads.
- PCB-C ring R1: bare 1.0 mm frame, taped between the e-paper module lands and the panel underside when a flush glass face is wanted.
- PCB-E5 dock block E5: nothing is placed on it by the assembler. It goes on four M3 x 6 standoffs above the strip, and the twelve signal wires and the 12 AWG pair are soldered into its plated lands from below before the stack is fitted.
