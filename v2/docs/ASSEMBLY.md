# MeshSat Field Kit carrier set: assembly, fasteners, coatings, removal (Rev A, MESHSAT-709)

Companion to `MESHSAT-709-geometry-appendix.md` (sections 14.6, 22, 25, 32). Boards: PCB-A POWER + I/O (**A19**), PCB-B COMPUTE (**B12**), PCB-C CONTROL PANEL (**C5**, the sealed face of appendix 32.34), PCB-D APRS (D5), PCB-E1 DOCK STRIP (**E4**), PCB-E5 DOCK BLOCK (**E5**). Nothing here has been built; this is how the first set is meant to go together.

A19 and B12 replaced A18 and B11 on 4 September 2026 after the rulings of appendix 32: the separate uninterruptible supply module is gone, PCB-A carries the charger, the fuel gauge, three 5 V converters and the main power control, PCB-B carries the Pi alone, and the cells left the boards for a battery module on the case floor that blind-mates through the dock. E4 is the dock strip that grew to four layers with a solar tracker, and E5 is the small raised block on it that presents the contacts the stack lands on.

## 1. Fasteners

| Joint | Fastener | Torque | Locking |
|---|---|---|---|
| Rod stack, 4 x | M3 stainless threaded rod, floor to the top nut above PCB-B; spacer tubes on the dock strip that set the 13.4 mm blind-mate gap under PCB-A; 35 mm and 59 mm bay spacers | 0.5 N m | Nyloc nuts top and bottom, no threadlocker on Nyloc |
| Panel to frame, 16 x | M3 x 10 A2 pan head (RS PRO 528-744) through an internal-tooth star washer on the panel's 8.0 mm underside ring, into the frame inserts (confirm the insert thread from the kit; Ø5.2 bore); the die-cut 0.53 mm PORON 4701-30 gasket ring (User.2 outline, `pcb-c-display-seals.dxf`) sits on the frame's bearing ring, adhesive side to the frame | 0.4 N m | Loctite 243, one drop; the star washer is the GND bond (appendix 32.34) |
| Junction strip to wall, 6 x | M3 x 12 pan head into the 1520 wall drill points (self-tapping brass inserts or M3 nuts inside the wall recess) | 0.3 N m | Loctite 243 |
| PCB-D on PCB-A, 4 x | M3 x 6 into the four standoffs at (10, -26), (80, -26), (10, 26), (80, 26) | 0.5 N m | Loctite 243 |
| DMR858M on PCB-D, 2 x | M2.5 x 11 standoff + M2.5 x 4 screw, connector-end fixed, module on the two 1x12 female headers | 0.3 N m | Loctite 243 |
| Touch Display 2 lugs | not used; the glass is taped and sealed (14.6 as amended by 32.34): a die-cut frame of 3M VHB 5915 (0.4 mm closed-cell foam, outline on User.2) on the printed border, pressed 15 s, glass about 1.1 mm proud | | tape |
| E-paper under PCB-C | WeAct 3.7 module face-up under the panel, glass through the 94.19 x 53.6 window, its two side lands (5.8 mm) taped to the panel underside with 3M VHB 5915; on the face a 2.0 mm UV-grade polycarbonate lens 107.2 x 66.6 (User.3 outline) on a 6 mm die-cut frame of the same tape, 3M Primer 94 on the lens's bonded face; the spacer ring R1 is retired; no screws | | tape |
| Panel switches | supplied nuts; SW_MAIN, SW_PI, SW_TEST on a die-cut 1.0 mm Silex GP60 silicone washer under the bezel; SW_LIGHT (NKK D3 bushing) with its O-ring (spare AT516) under the nut on the face and the AT428H boot, its D flat east; SW_SOS, SW_EMCON, SW_ZERO with the APEM K seal (O-ring and U360 gasket) keyed into the notch toward the operator; flying leads soldered to the lands on the underside, then beaded | hand tight + 1/8 turn | none |
| Sounder BZ1 | Floyd Bell MC-09-530-Q through its 28.6 mm hole with the 61663 bezel gasket on the face, nut below, two leads to the lands | hand tight | none |
| Dock strip to floor | 4 x 3M VHB 5952 pads 20 x 20 at the corners, floor degreased with IPA | | |
| Blade fuses F2 to F5 on PCB-A | 10 A mini blade in F2 (cell node to `J_MEZZ_PWR1`), 10 A in F3 and F4 (node to the M1 and M2 converters), 15 A in F5 (node to the Pi converter), into Keystone 3568 holders | push fit, seated flush, no torque | none; check seating after any transport |
| Compute Module 5 on PCB-B, 4 x | M2.5 x 4.0 female-female standoffs on the module's 33 x 48 pattern (the height of the 10164227-1004 receptacle stack), M2.5 x 5 screws from below, M2.5 x 4 from above through the module; the CM5 Cooler clips on the module (appendix 32.35) | 0.2 N m | Loctite 243 on the standoff thread only |
| LTE card on PCB-B, 2 x | M2.5 x 4.0 standoffs at the card's far edge, M2.5 x 4 screws | 0.2 N m | none |
| Pack to PCB-A | two 7.6 mm cable ties through the 25 x 4 slots at (-95, +-43), over the shrink sleeve, 1 mm silicone sheet under the pack | | |

Threadlocker: Loctite 243 (medium, oil tolerant) on every machine screw into metal; never on Nyloc nuts, never on the plastic-bodied switch nuts.

## 2. Build order

1. Dock strip E4: solder the entry leads (shore pair to J_DCIN, panel pair to J_SOLAR, VH crimps), fit the TRACO TEN 40-2412WIN, the two fuse holders with a 7.5 A and a 10 A blade, and check 12 V at the block lands with 9 V and 36 V in. The EL817 optocoupler and the tracker are fitted by the assembler.
2. Dock block E5 on its four M3 x 6 standoffs above the strip, face at 7.4 mm. Solder the twelve signal wires and the 12 AWG pair from the strip into the block's plated lands from below; the block's underside legend names every land. Check each wire end to end before the stack goes on, because the lands are covered once PCB-A is down.
3. Rods: four M3 rods through the floor holes of the strip, then the spacers that set the 13.4 mm gap on all four rods, so PCB-A's spring pins land on the block with the pins compressed about 1 mm.
4. PCB-A A19 with the Preci-Dip 813-S1-012-10-016101 connector and the nine Mill-Max 0858 class power pins soldered in from the underside (tails on the top face), the seven Radiall receptacles fitted, and the blade fuses in before anything is energised. Lower it onto the rods and check continuity from the block's wire lands up to the board.
5. 38 mm spacers (D7: 3 mm more than D6 planned, for the DMR858M heatsink), PCB-B B14 with the AsiaRF AW7915-AED WiFi P2P card in J_WIFI1 on its M2.5 standoff (two IPEX pigtails to the east wall P2P bulkheads), the Compute Module 5 pressed onto its receptacles and screwed to its four standoffs, the cooler on it (fan lead in J_FAN, antenna lead to the WiFi bulkhead), the LTE card in J_LTE1 with its SIM in J_SIM1, the SDR stick, the RockBLOCK, the display flex in J_DISP, the CR2032 in BT1, the three rail leads into J_5V_M1, J_5V_M2 and J_5V_PI (no plug on the module side), the GNSS, LoRa and ZigBee pigtails, the panel ribbon into J_PANEL and the 2x9 ribbon into J_AB1. Nyloc on top.
6. Battery module into its cradle on the floor, XT60 into the strip's J_BATT, thermistor pair into J_TS. The 40 A blade sits at the module end, so the cable is protected at the source.
7. RF: the seven right-angle plugs sit in their printed float clamps on the strip and mate with the receptacles under PCB-A as the stack comes down. The wall pigtails run from the clamps to the MIL-DTL-38999 receptacles, torqued once at the wall side and finger tight at the device side.
8. Panel C5 (sealed face, appendix 32.34): the eight panel-mount parts through the face with their seals (gasket washers under the three C&K bezels, the NKK O-ring and boot, the three APEM K seals keyed into their notches, the sounder with its bezel gasket), nuts from below, flying leads soldered to the underside lands; a bead of DOWSIL 3145 over the 32 LED joints and over every lead land, cured; the e-paper module taped under its window (header to the east, 1x8 lead to the SMD header J_EPD), then its lens on its tape frame on the face; the display glass on its tape frame; the underside coated (section 5); the MAIN and PI leads soldered to J_MAINSW and J_PIJ2 and beaded; the ribbon into J_PANEL; the PORON ring on the frame, the panel into the frame, 16 x M3 x 10 with star washers from below. Flood and hose the panel in its frame before the stack goes in (32.34, verification).
9. Lower the lid. The case is bought without foam; nothing on the panel face is taller than 20 mm and the lid cavity is 46 mm deep.

## 3. The battery module

Twelve Samsung INR18650-35E in parallel (1S12P), spot-welded nickel strip 0.15 x 8 mm, cells side by side in a flat three-row by four-column block, fish paper at both ends, blue PVC sleeve. Wrapped, the block is about 75 x 198 x 20 mm and about 640 g; complete with its protection board, fuse, holder and connector, about 0.7 kg. Capacity is 40.2 Ah at the specification minimum and about 41.5 Ah typical (appendix 32.27).

The module is a unit of its own, not a part of a board: it sits in a cradle on the case floor beside the dock strip and connects through one XT60 pair on 12 AWG and one thermistor pair. On the positive lead, at the module, sit a Littelfuse MAXI 40 A blade and its in-line holder, so the cable is protected at the source. A Semitec 103AT-2 thermistor is taped to a cell in the middle of the block and its pair runs out with the power leads, because the charger on PCB-A holds the Samsung charge window of 0 to 45 C from that reading. Under the cells, on the enclosure floor, lies an RS PRO 245-556 silicone heater mat (50 x 150 mm, 12 V, 7.5 W, 0.63 A, self-adhesive, 500 mm PTFE leads, appendix 32.32) that PCB-A switches on from shore power when the module is below 0 C; its leads leave with the others and its floor witness in the enclosure fixes its place.

The single-cell protection board is the documented Batteryspace PCB-LIS1A15 (owner ruling 4 Sep, appendix 32.31): 15 A continuous, 20 A for five minutes, 35 A trip, 65 x 10 x 2.5 mm, in the pocket at the module's south end. It has no thermistor input; the charge window is held by the charger on PCB-A through the module's own thermistor.

Samsung's specification forbids soldering to the cell can: the cells are welded and the leads are soldered to the strip, never to a cell.

## 4. Leads

| Lead | From | To | Wire | Connector |
|---|---|---|---|---|
| Module power (**fused at the module: 40 A MAXI blade**) | battery module XT60 | dock strip J_BATT (XT60) | 12 AWG silicone, 300 mm | XT60 pair |
| Module thermistor | 103AT-2 on a cell | dock strip J_TS (XH2.5) | 26 AWG twisted, 300 mm | XH2.5 |
| Shore inlet | MIL-DTL-38999 receptacle on the back-wall plate, DC pair | dock strip J_DCIN (JST-VH), the lead tied along the back wall, the west end wall and the front wall | 18 AWG, 500 mm | VH crimp |
| Solar inlet | MIL-DTL-38999 receptacle, panel pair | dock strip J_SOLAR (JST-VH), with the shore lead | 18 AWG, 500 mm | VH crimp |
| Block signal wires | dock strip J_BLK (twelve lands) | dock block wire lands, underside | 24 AWG, 60 mm each, named on the block's legend | soldered both ends |
| Block power pair | dock strip P_CP and P_CN | dock block wire holes | 12 AWG silicone, 60 mm | soldered both ends |
| MAIN button | PCB-C J_MAINSW (two solder lands on the underside, beaded) | PCB-A J_MAINSW (XH2.5) | 24 AWG twisted | XH2.5 at the PCB-A end; unplugs there |
| PI switch | PCB-C J_PIJ2 (two solder lands on the underside, beaded) | PCB-B J_PWRBTN (the module's PWR_Button pin, wake from soft-off) | 24 AWG twisted | 2-pin housing at the PCB-B end; unplugs there |
| Panel ribbon | PCB-B J_PANEL | PCB-C J_PANEL (SMD box header on the underside) | 20-way 1.27 ribbon, 350 mm | IDC 2x10 both ends |
| A to B ribbon | PCB-A J_AB1 | PCB-B J_AB1 | 18-way 1.27 ribbon, 200 mm | IDC 2x9 both ends |
| Mezz harness (I2S, I2C, the gated 3.3 V, PTT lines) | PCB-A J_MEZZ1 | PCB-D J_HARN1 | 16-way ribbon | IDC 2x8 |
| Mezz power (**fused at source: F2, 10 A, on A19**) | PCB-A J_MEZZ_PWR1 (VH) | PCB-D boost input | 18 AWG | VH |
| Rail M1 (**F3, 10 A**; hub, display, panel, LTE) | PCB-A J_5V_M1 (VH) | PCB-B J_5V_M1 (VH) | 18 AWG, 150 mm | VH crimp both ends |
| Rail M2 (**F4, 10 A**; SDR, ZigBee, LoRa, RockBLOCK) | PCB-A J_5V_M2 (VH) | PCB-B J_5V_M2 (VH) | 18 AWG, 150 mm | VH crimp both ends |
| Pi rail (**F5, 15 A**; 5.1 V, 5 A) | PCB-A J_5V_PI (VH) | PCB-B J_5V_PI (VH), straight into the module's 5 V pins | 18 AWG, 200 mm | VH crimp both ends |
| Display flex | PCB-B J_DISP (22-pin 0.5 mm) | Touch Display 2 (15-pin) | Raspberry Pi Standard-Mini display cable, 200 mm | FPC both ends |
| Fan | PCB-B J_FAN (JST-SH 4) | CM5 Cooler fan | the cooler's own lead | SH housing |
| GNSS, LoRa, ZigBee, WiFi antennas | PCB-B U.FL or module IPEX | SMA bulkheads on PCB-A's jacks | U.FL to SMA pigtails, RG-178, 150 mm | U.FL at the board, SMA at PCB-A |
| Heating pad | PCB-A J_HEAT (XH2.5) | the RS PRO 245-556 silicone mat under the cells inside the module, its own 500 mm PTFE leads brought out with the power leads | the mat's leads, spliced to 20 AWG where they leave the module | XH2.5 at PCB-A |
| Wall USB | PCB-A J_WALL1 (USB-A) | Glenair 233-370 receptacle on the connector plate | USB 2.0 cable, 300 mm | USB-A both ends |
| Connector plate | 82 x 54 x 3 aluminium over the wall window (appendix 32.29, `release/revA/case/`) | the back long wall (hinge side), plate centre 55 mm above the floor, X -92 | six M4 x 16 stainless, washers both sides, Nyloc inside, 1.2 N m in a cross pattern; 2 mm closed-cell gasket | carries the shore DC receptacle (D38999/20 shell 13) and the USB receptacle (233-370 shell 15), each on its own gasket with M3 x 10 and spring washers |
| RF pigtails | device SMA on B / D | PCB-A J_RF1 to J_RF7 (SMA jacks) | RG-316, bend radius 12.5 mm | SMA male |
| RF jumpers, 7 x | the float nests on the dock strip (Radiall R222M80500 right-angle plugs, crimped, tied into the nest) | the SMA bulkhead couplers on the end walls (Amphenol Connex 132170; west wall UHF, WIFI 2.4, GNSS, SDR at Y -60, -30, +30, +60; east wall LTE, IRIDIUM, LORA at Y -60, -30, +30, the +60 site plugged; 55 mm above the floor) | RG-316, 150 to 250 mm, bend radius 12.5 mm | SMP-MAX plug at the nest, SMA male at the coupler |
| WiFi P2P pigtails, 2 x | the two IPEX (MHF1) connectors of the AW7915-AED card on PCB-B B14 | the east wall couplers WIFI P2P A (Y +60, Z 55) and WIFI P2P B (Y -45, Z 90) | IPEX to SMA female bulkhead, about 250 mm, torqued once at the coupler  |

Every lead tied at both ends; the rod stack's edge carries the vertical runs with a tie base per bay.

**External cables (appendix 32.32, sheets in `vendor/d38999/`).** Two cables leave the case through the connector plate on the back wall.

| Cable | Kit end | Cable | Far end |
|---|---|---|---|
| Shore lead | Glenair D38999/26FC4SN plug (shell 13, insert 13-4, four M39029/56-352 size 16 socket contacts, key N, electroless nickel), crimped with the M22520/1-01 tool and the M22520/1-04 positioner, seated with M81969/14-03; Glenair M85049/38S13N self-locking straight strain relief on the plug's M18 x 1 thread | Lapp OLFLEX ROBUST 210 4 x 1.0 (article 0021917, 6.6 mm, TPE, outdoor), or Alpha Wire 25064 (18 AWG 4C, TPU, 6.58 mm) or 5064C (PVC); 2 m | the four cores split under adhesive-lined shrink into two 0.3 m tails: the DC pair to the shore supply, the solar pair to the panel; those two connectors follow the supply and the panel in use and are not fixed here |
| USB host lead | Glenair 233-340 plug (shell 15, USB 2.0 Type A male front and Type A female back, key N, horizontal, with the 770-028 shrink boot; code 233-340 M G6 -15 2 A A N H T per the sheet's part number development), screwed onto the feed-through | a standard USB 2.0 Type A male to Type A female extension, 1.5 m, its plug in the back of the 233-340 and the boot shrunk over its jacket | the extension's Type A female, into which the device's own lead plugs; where the outside device has an A or B receptacle instead, Glenair's potted cordsets 2330-0015 (A-male far end) or 2330-0069 (B-male far end) replace the whole lead |

Contact assignment of the shore plug (design, 32.32): A shore DC positive, B shore DC return (the dock's isolated DC_N), C solar positive, D solar return; Lapp cores 1 to 4 in that order, Alpha colours black, red, white, green. The cable's insulated cores must lie inside the size 16 grommet window of 1.65 to 2.77 mm (MIL-DTL-38999 Table IV); the Alpha cores are 2.0 mm, the Lapp core diameter is not on its sheet and is measured on the reel before that cable is used.

The dock interface is not a lead but belongs in the same reading. Twelve Preci-Dip 813 contacts in `J_DOCK` on A19's underside land on the raised block's targets: pins 1 to 4 are `SHORE_12V`, 5 to 7 and 10 are ground, 8 is `SHORE_INHIBIT`, 9 the module thermistor, 11 the cell sense and 12 spare. Beside them, nine Mill-Max 0858 class pins carry the module current: four on `CELL+`, four on the return, and one longer pre-charge pin that mates first through a 10 ohm resistor so the converters' input capacitance does not draw an arc across the main pins. The seven RF joints mate at the same time, and the whole set parts when the stack is lifted.

## 5. Conformal coating

IPC-CC-830 acrylic (MG Chemicals 422B or equal) on A, B, D, the dock strip E4 and the dock block E5 after the bench fit, two thin coats. Masks (kapton) before coating: every connector face and its keying, the spring-pin targets and the pack targets on E5 and the pins on A, the SMP-MAX receptacles and the SMA bodies, the DMR858M sockets, the Pi 5 site and its standoffs (assembled parts are not coated), the test points that the bench list uses. PCB-C (C5): the face is not coated (the seals sit on bare mask); the whole underside is coated after the silicone beads have cured, with J_PANEL, J_EPD, the two lead lands and the 16 frame rings masked (the star washers bond there). The wall receptacles sit on the aluminium plate of the back wall (appendix 32.29); there is no wall strip to coat.

## 6. Labels (MIL-STD-130 style)

- Panel nameplate field (0, -110), 76 x 26: "MESHSAT FIELD KIT", P/N MSK-FK-1520, S/N, REV A, a 10 x 10 mm data matrix with the S/N, "MADE IN NL".
- Every board: P/N, S/N, REV silk fields near the title block silk.
- Case: asset label on Peli's label recess; "RF HAZARD DURING TX" 20 x 40 mm next to the UHF bulkhead; the bulkhead legend strip (UHF SDR WIFI1 WIFI2 LTE IRID LORA) beside the SMA row.

## 7. Removal and refit

Appendix 25.3 as amended by 32.13: lid, 16 screws, ribbon and the rail leads, panel out, then lift the A+B stack straight up. No connector is unscrewed any more: the seven RF joints, the twelve signal contacts and the nine power pins all part as the stack rises. Refit in reverse; the rods through the dock strip's holes align everything, and the pre-charge pin meets its target before the four main ones.

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
- PCB-B B14: the AsiaRF AW7915-AED M.2 card on its M2.5 x 4 standoff, the Compute Module 5 (CM5108064) on its two receptacles and four M2.5 x 4 standoffs, the CM5 Cooler with its fan lead and the certified antenna lead, the Quectel EG25-G mini PCIe card on two M2.5 x 4 standoffs with a nano-SIM, the RTL-SDR or LimeSDR, the RockBLOCK, the Touch Display 2 flex, the CR2032, the three rail leads from PCB-A, the antenna pigtails, the panel ribbon and the 2x9 ribbon to PCB-A.
- PCB-C C5: the two white 3 mm LEDs D10 and D11 (no LCSC stock at order time), the Floyd Bell MC-09-530-Q sounder BZ1 with its 61663 gasket, two 19 mm and 16 mm anti-vandal switches with LED rings (SW_MAIN C&K ATP19-SL1-603-B0SA-03G green, SW_PI C&K ATP16-SL1-403-M0SA-04G orange as the amber, SW_TEST C&K ATP16-SL1-203-M0SA-04G white; solder lugs, gold, 3 V ring type because C4's 470 and 300 ohm resistors set the ring current), one DPDT ON-ON-ON sealed toggle (SW_LIGHT NKK M2044SD3A01, D3 bushing with its O-ring, AT428H boot), three locking toggles APEM 5636ADKB-2V (SW_SOS, SW_EMCON, SW_ZERO: single pole ON-NONE-ON with both positions locked, pull the lever before it moves; gold-plated contacts, front-panel seal, epoxy terminals, 1/4-40 bushing in the same 6.5 mm holes; owner ruling of 4 Sep 2026, design record 32.13; SOS and ZEROIZE are maintained switches, the bridge acts after 2 s / 5 s in position), the WeAct 3.7 e-paper module taped under the recessed window (optional 1.0 mm spacer ring pcb-c-ring) with a 2x4-to-1x8 lead to J_EPD, the Touch Display 2 on transfer tape, the piezo sounder if not JLC-fitted, the two XH leads.
- PCB-D D7: DMR858M on two 1x12 female headers and two M2.5 x 11 standoffs, heatsink up, SMA pigtail, the boost inductor L1 (Coilcraft XAL6030-152MEB, no JLC equivalent, hand-soldered); the WM8960, the 24 MHz oscillator and the PCA9536 are assembled. The module's channel knob and DIP switch (NORMAL) are set on the bench before it is plugged in; they face down into the socket gap and cannot be reached in the stack; the module's own USB-C is the bench configuration path, the kit reaches the module's control UART through the SC16IS740 bridge.
- PCB-E1 dock strip E4: TRACO TEN 40-2412WIN, two Keystone 3568 holders with a 7.5 A and a 10 A mini blade, the JST-VH shore and panel leads, the XT60 module entry, the twelve signal wires and the 12 AWG pair up to the block, the seven printed float nests (`v2/cad/float_clamp.py`, two M3 x 8 each into the strip's clamp holes, the plug's cable tied into the nest's slot) with their Radiall R222M80500 plugs, four VHB pads.
- Case: the connector plate with its two receptacles (section 4) on the back wall, each on a Glenair 930-001 silicone flange gasket (S06 for the shell 13, S07 for the shell 15), the six M4 plate screws with bonded sealing washers, and the seven Amphenol Connex 132170 SMA couplers in the end walls (D-holes, 8 mm nut and lock washer inside, an NBR O-ring 6.5 x 1.0 under the outside hex), all per `release/revA/case/wall-receptacles-1to1.pdf`.
- Panel seals (C5, `vendor/seals/` and `docs/respin-research-seal-2026-09-04.md`): two die-cut frames of 3M VHB 5915 and the die-cut PORON 4701-30 ring (0.53 mm on PET) from `pcb-c-display-seals.dxf`; the 2.0 mm UV polycarbonate lens from the same file with 3M Primer 94; three Silex GP60 silicone washers; the NKK AT516 spare O-ring and AT428H boot; the APEM K seals with the switches; the Floyd Bell 61663 sounder gasket; DOWSIL 3145 clear for the beads; MG Chemicals 422B for the underside; 16 star washers and M3 x 10; the 3M 7871EC serial label.
- PCB-E5 dock block E5: nothing is placed on it by the assembler. It goes on four M3 x 6 standoffs above the strip, and the twelve signal wires and the 12 AWG pair are soldered into its plated lands from below before the stack is fitted.
