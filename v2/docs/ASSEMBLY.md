# MeshSat Field Kit carrier set: assembly, fasteners, coatings, removal (Rev A, MESHSAT-709)

Companion to `MESHSAT-709-geometry-appendix.md` (sections 14.6, 22, 25). Boards: PCB-A POWER + I/O (**A16**), PCB-B COMPUTE (B10), PCB-C CONTROL PANEL (**C4**), PCB-C spacer ring (R1, optional), PCB-D APRS (D5), PCB-E1 DOCK (E1), PCB-E2 RF JUNCTION (E2). Case: Peli 1520EU with the 1520PF panel frame.

A16 is A15 plus the two blade fuses F1 and F2 on the pack node and `SHORE_INHIBIT` on spring pin 8; C4 is C3 with the e-paper recessed into the panel instead of standing on standoffs. A15 and C3 no longer exist as deliverables. If a folder or a print says A15 or C3, it is superseded (appendix 25.13 to 25.15).

## 1. Fasteners

| Joint | Fastener | Torque | Locking |
|---|---|---|---|
| Rod stack, 4 x | M3 stainless threaded rod, floor to the top nut above PCB-B; spacer tube 6.0 mm (Ø7 OD, M3 clear) on the dock strip under PCB-A; 35 mm and 59 mm bay spacers | 0.5 N m | Nyloc nuts top and bottom, no threadlocker on Nyloc |
| Panel to frame, 16 x | M3 x 8 pan head stainless into the frame inserts (confirm the insert thread from the kit; Ø5.2 bore) | 0.4 N m | Loctite 243, one drop |
| Junction strip to wall, 6 x | M3 x 12 pan head into the 1520 wall drill points (self-tapping brass inserts or M3 nuts inside the wall recess) | 0.3 N m | Loctite 243 |
| PCB-D on PCB-A, 4 x | M3 x 6 into the four standoffs at (10, -26), (80, -26), (10, 26), (80, 26) | 0.5 N m | Loctite 243 |
| DMR858M on PCB-D, 2 x | M2.5 x 11 standoff + M2.5 x 4 screw, connector-end fixed, module on the two 1x12 female headers | 0.3 N m | Loctite 243 |
| Touch Display 2 lugs | not used; the glass is taped (section 14.6): 3M 467MP or 9495LE, 0.05 mm, full flange | | |
| E-paper under PCB-C | WeAct 3.7 module face-up under the panel, glass through the 94.19 x 53.6 window, its two side lands (5.8 mm) taped to the panel underside with 3M 9495LE; for a flush face the 1.0 mm spacer ring (pcb-c-ring R1) taped on both sides between land and panel; no screws | | tape |
| Panel switches | supplied nuts, IP67 boots, guards oriented so the cover opens toward the operator | hand tight + 1/8 turn | none |
| Dock strip to floor | 4 x 3M VHB 5952 pads 20 x 20 at the corners, floor degreased with IPA | | |
| Blade fuses F1, F2 on PCB-A | 15 A mini blade in F1 (pack node to `J_X1202BAT`), 10 A mini blade in F2 (node to `J_MEZZ_PWR1`), into Keystone 3568 holders | push fit, seated flush, no torque | none; check seating after any transport |
| Pack to PCB-A | two 7.6 mm cable ties through the 25 x 4 slots at (-95, +-43), over the shrink sleeve, 1 mm silicone sheet under the pack | | |

Threadlocker: Loctite 243 (medium, oil tolerant) on every machine screw into metal; never on Nyloc nuts, never on the plastic-bodied switch nuts.

## 2. Build order

1. Dock strip E1: solder the leads (shore inlet lead to J_DCIN, VH crimp), fit the TEN 40-2412WIN, fuse holder and 7.5 A fuse, test 12 V at the targets with 9 V and 36 V in. The EL817 optocoupler on the converter's remote pin is fitted by JLC; with nothing driving spring pin 8 its LED is off and the converter runs, which is the state you are testing in. Stick it to the floor with the two south rod holes on the rod pattern (drop two rods through to locate it before the VHB touches).
2. Rods: four M3 rods through the floor holes of the strip, Nyloc under the strip is not needed (the strip sits on the floor); a 6.0 mm spacer on each of the two south rods and on the two north rods (the north rods stand on the floor, add a 1.6 mm washer stack so all four spacers sit level).
3. PCB-A A16 with its spring pins pressed in from the underside (J_DOCK), the two fuse holders and their blades fitted (F1 15 A, F2 10 A) **before** any lead is energised, the pack strapped on, J_PACK plugged, the J_X1202BAT lead routed up the stack's edge, the J_X1202DC lead likewise. Nyloc on top.
4. 35 mm spacers, PCB-B B10 with the Pi 5 + X1202 stack, the modules, the panel ribbon plugged into J_PANEL on B10. Nyloc on top.
5. Connect the X1202 leads: battery lead to the B+ / B- holder solder tabs (16 AWG, XT60 at the PCB-A end), the 12 V lead to the barrel (5521 plug), the switch lead to the reserved external-switch pins, the Pi J2 lead to the Pi's J2 pads.
6. Junction strip E2 on the +Z wall; wall bulkhead pigtails to the lower coupler sides (torque 0.45 N m, once); device pigtails to the upper sides, finger tight.
7. Panel C4: switches, covers, the e-paper module taped under its window (ring first if used, then the module, header to the east, 2x4 socket lead to J_EPD), the display glass taped, ribbon and the two XH leads plugged; 16 frame screws.
8. Lower the lid; the lid foam is pocketed over the switch strips (nothing on the panel face taller than 20 mm above it).

## 3. The pack

8 x Samsung INR18650-35E, 1S8P, spot-welded nickel strip 0.15 x 8 mm (two strips per node), cells side by side in two rows of four along the pack's long axis (130 x 74 x 18.5), fish paper on both ends, a 1S BMS 15 A with NTC cutoff on the negative lead, XT60 male on 16 AWG silicone leads 150 mm, blue PVC shrink sleeve, a 10k NTC 103AT-2 inside for the BMS. The pack sits in parallel with the X1202's four cells (same model, same age, matched within 50 mV before connecting). Nothing else charges it; the X1202 does (appendix 25.6).

## 4. Leads

| Lead | From | To | Wire | Connector |
|---|---|---|---|---|
| Battery parallel lead (**fused at source: F1, 15 A, on A16**) | PCB-A J_X1202BAT (XT60) | X1202 B+ / B- holder solder tabs | 16 AWG silicone, 200 mm | XT60 female at PCB-A |
| Shore 12 V | PCB-A J_X1202DC (XH2.5) | X1202 barrel 5.5 x 2.1, centre positive | 20 AWG, 250 mm | XH2.5 + 5521 plug |
| Case USB-C inlet | not connected to the X1202 (audit 26.2: its two inputs must never be live together); a USB-C PD source feeds the dock inlet through a 12 V PD trigger lead | | | |
| Shore inlet | IP68 2-pin bulkhead on the -Z wall | E1 J_DCIN (JST-VH) | 18 AWG, 400 mm | VH crimp |
| MAIN PWR switch | PCB-C J_X1202SW (XH2.5) | X1202 external switch pins | 24 AWG twisted | XH2.5 |
| PI switch | PCB-C J_PIJ2 (XH2.5) | Pi 5 J2 pads | 24 AWG twisted | XH2.5 |
| Panel ribbon | PCB-B J_PANEL | PCB-C J_PANEL | 20-way 1.27 ribbon, 350 mm | IDC 2x10 both ends |
| Mezz harness | PCB-A J_MEZZ1 | PCB-D J_HARN1 | 16-way ribbon | IDC 2x8 |
| Mezz power (**fused at source: F2, 10 A, on A16**) | PCB-A J_MEZZ_PWR1 (VH) | PCB-D boost input | 18 AWG | VH |
| RF pigtails | device SMA on B / D / A | E2 coupler, upper side | RG-316, bend radius 12.5 mm | SMA male |
| Wall pigtails | E2 coupler, lower side | wall bulkhead (SMA female bulkhead, D-hole 6.5) | RG-316 | SMA male |

Every lead tied at both ends; the rod stack's edge carries the vertical runs with a tie base per bay.

The dock interface is not a lead but belongs in the same reading. Eight spring pins in `J_DOCK` on A16's underside land on E1's targets: pin 8 is `SHORE_INHIBIT` (it was GND before A16), which leaves **three** GND pins carrying the return. At the dock converter's full 40 W that is about 3.33 A total, so about 1.11 A per pin. Confirm that against the spring pin's own rating from the A16 BOM before the first full-load run, and measure it in section 8 test 9 rather than assuming it.

## 5. Conformal coating

IPC-CC-830 acrylic (MG Chemicals 422B or equal) on A, B, D and E1 after the bench fit, two thin coats. Masks (kapton) before coating: every connector face and its keying, the spring-pin targets on E1 and the pins on A, the SMA bodies, the DMR858M sockets, the X1202 and Pi stack areas (assembled parts are not coated), the test points that the bench list uses. PCB-C is not coated on the face (switch and tape band); the underside cluster is coated with J_PANEL masked. E2 has no copper.

## 6. Labels (MIL-STD-130 style)

- Panel nameplate field (0, -110), 76 x 26: "MESHSAT FIELD KIT", P/N MSK-FK-1520, S/N, REV A, a 10 x 10 mm data matrix with the S/N, "MADE IN NL".
- Every board: P/N, S/N, REV silk fields near the title block silk.
- Case: asset label on Peli's label recess; "RF HAZARD DURING TX" 20 x 40 mm next to the UHF bulkhead; the bulkhead legend strip (UHF SDR WIFI1 WIFI2 LTE IRID LORA) beside the SMA row.

## 7. Removal and refit

Appendix 25.3: lid, 16 screws, ribbon + two leads, panel out, seven pigtails at the strip, lift the A+B stack straight up. Refit in reverse; the south rods through the dock strip's holes align the spring pins.

## 8. Bench verification before the pack is welded (X1202 in hand)

1. Charge current from the barrel input at 12.0 V (sets charge time; 42 Ah at 3 A is about 14 h).
2. One full charge of the 12-cell node without a timer cutoff.
3. Over-current trip: pull 12.5 A from the battery node at 3.2 V for 5 s (the Pi at 5 V 4.5 A is about 7.8 A at the node, plus the APRS boost about 4.7 A); the X1202 must not trip (audit 26.6).
4. B+ / B- solder points on the holder tabs, and that the X1202's gauge (0x36) still reads the node sensibly.
5. E1: 12 V at the targets with 9, 12, 24 and 36 V in; reverse polarity applied for 10 s (no damage, no output); fuse blows at a bolted short.
6. Panel: lamp test lights all 17 LEDs; BLACKOUT kills the rail; the EMCON cover closed keeps the DMR858M in receive while the bridge asserts PTT.
7. Repeat items 2 and 3 with the finished pack and its BMS in circuit, and watch the BMS reconnect after a trip (audit 26.5).
8. GPIO 6 power-loss line: `gpioget --bias=pull-up gpiochip4 6` with and without an input plugged; if it does not move, run a lead from the X1202 AC-loss pad (audit 26.4).
9. Shore inhibit: drive SHORE_INHIBIT high from the expander and confirm the dock 12 V drops out within a second; release it and confirm it returns; pull the stack off the dock and confirm the converter stays on. Then leave it asserted and confirm the kit **keeps running from the battery node** with the dock inhibited, and record that current: it is the whole kit's draw with no external input, so it sets how long an inhibited kit survives on shore power (audit 28.1). While at full load, measure the current on each of the three remaining GND spring pins (section 4).

## 9. Bench-fit lists (hand-fitted parts per board, not on the JLC BOM)

- PCB-A A16: the welded pack (section 3) and its strap, the two Keystone 3568 blade holders F1 and F2 if JLC could not place them (stock was 2 against 10 at order time) with a 15 A mini blade in F1 and a 10 A in F2, 8 spring pins in J_DOCK, the four M3 standoffs for PCB-D, the GPS puck and the WiFi dongle in their brackets, the leads of section 4.
- PCB-B B10: Pi 5 + X1202 on the 49 x 58 pattern, T-Call, T-Beam 1W, RTL-SDR, ZigBee dongle, RockBLOCK with the GC bracket, Wio-SX1262, the panel ribbon.
- PCB-C C4: the two white 3 mm LEDs D10 and D11 (no LCSC stock at order time), two 19 mm and 16 mm anti-vandal switches with LED rings (SW_MAIN 19 mm green, SW_PI 16 mm amber, SW_TEST 16 mm white), one DPDT ON-ON-ON sealed toggle (SW_LIGHT), three SPDT guarded toggles with red covers (SW_SOS momentary, SW_EMCON latching, SW_ZERO momentary), the WeAct 3.7 e-paper module taped under the recessed window (optional 1.0 mm spacer ring pcb-c-ring) with a 2x4-to-1x8 lead to J_EPD, the Touch Display 2 on transfer tape, the piezo sounder if not JLC-fitted, the two XH leads.
- PCB-D D5: DMR858M on two 1x12 female headers and two M2.5 x 11 standoffs, heatsink up, SMA pigtail.
- PCB-E1: TEN 40-2412WIN, Keystone 3568 holder + 7.5 A mini blade, JST-VH shore lead, four VHB pads.
- PCB-C ring R1: bare 1.0 mm frame, taped between the e-paper module lands and the panel underside when a flush glass face is wanted.
- PCB-E2: seven SMA female-female bulkhead couplers in the D-holes, six M3 wall screws.
