# MeshSat Field Kit carrier set: assembly, fasteners, coatings, removal (Rev A, MESHSAT-830)

Companion to `MESHSAT-709-geometry-appendix.md` (sections 32.49 to 32.61) and `../BUILD.md`. Boards: PCB-A POWER + I/O (**A22**), PCB-B COMPUTE (**B16**), PCB-C PANEL BACKER (**C7**, the ring under the aluminium face plate), PCB-D VHF APRS (**D8**, the mezzanine on A22), PCB-E1 DOCK STRIP (**E6**, with the sensor controller on it), PCB-E5 DOCK BLOCK (**E5**). Nothing here has been built; this is how the first set is meant to go together. The previous generation's page (the twelve-cell battery module, the previous display, the single Compute Module) is in the git history of this file.

The set of 7 September 2026: three Compute Module 5 slots on B16 with a PCIe switch, a USB 3 hub and an NVMe drive each, the radios as USB devices, an Ethernet switch to a sealed wall port, the Xenarc 709GNK monitor lying on the face plate, the Pervasive Displays e-paper under a lens, the RP2040 panel controller on C7, the SA868 exciter and the RA30H1317M1 30 W amplifier (the module bolted under the plate) on D8, a BB-2590/U pack in a cradle at the west wall, the 9 to 36 V front end and the solar tracker on E6, eleven blind-mate RF paths through the dock, and the QMX HF unit in a tray on the lid.

## 1. Fasteners

| Joint | Fastener | Torque | Locking |
|---|---|---|---|
| Rod stack, 4 x | M3 stainless threaded rod, floor to the top nut above B16; spacer tubes on the dock strip that set the 13.4 mm blind-mate gap under A22; 38 mm bay spacers between A22 and B16 (B16's top copper at 56 mm above the floor, `panel1450.py` B_TOP_Z) | 0.5 N m | Nyloc nuts top and bottom, no threadlocker on Nyloc |
| Face plate to frame, 10 x (Peli 1450PF) | M3 x 10 A2 pan head through an internal-tooth star washer into the 1450PF inserts (confirm the insert thread from the kit); the die-cut 0.53 mm PORON 4701-30 gasket ring (the plate's 8 mm band, outline from `face-plate.dxf`) sits on the frame's bearing ring, adhesive side to the frame | 0.4 N m | Loctite 243, one drop; the star washers bond the anodised plate to the frame |
| Backer C7 to the plate, 8 x | M3 x 6 A2 into the eight PEM SO-M3-10 self-clinching standoffs pressed into the plate from below (4.2 mm holes; `panel1450.py` STANDOFFS), through the backer's GND rings H1 to H8, which bond the backer to the plate | 0.4 N m | Loctite 243 |
| PA module to the plate, 2 x | Mitsubishi RA30H1317M1 flange under the plate at `PA_MOUNT` (flange holes 60 mm apart, 3.26 mm), M3 x 8 into two PEM S-M3 nuts pressed into the plate's underside, a 1.0 mm thermal pad the size of the flange between module and plate; the plate is the heat spreader (appendix 32.56) | 0.6 N m in two steps | Loctite 243 |
| Xenarc 709GNK on the plate, 4 x | M4 x 8 through the plate's VESA 50 holes into the monitor's inserts, the monitor lying on the plate at `XENARC["c"]`, its connector block down through the 60 x 46 cutout with a closed-cell foam gasket ring between the monitor's back and the plate around the cutout (the monitor itself is IP67; the gasket keeps water off the leads) | 1.0 N m | Loctite 243 |
| Light guides, 16 x | Mentor 1282.5004 (IP68, 2.5 mm shaft, 3.2 mm spherical head, 7.5 mm long) pressed from the face into the 2.6 H7 reamed holes over D1 to D16; the LEDs on the backer stand 5.3 mm high, 0.2 mm under the guide tips | press fit | none |
| Connector plate to the back wall, 6 x | M4 x 16 A2 through the 1450's back wall between the inner ribs at X -95 and -18 (`case/wall-receptacles-1to1.pdf`), washers both sides, Nyloc inside, 2 mm closed-cell gasket between plate and wall | 1.2 N m | Nyloc |
| D8 on A22, 4 x | M3 x 6 into four M3 x 22.6 mm standoffs at A22's mezzanine site (5, +-35) and (95, +-35) (`gen_pcb_a.py` MEZZ_RECT) | 0.5 N m | Loctite 243 |
| Compute Modules on B16, 3 x 4 | M2.5 x 4.0 female-female standoffs on each module's 33 x 48 pattern (the height of the 10164227-1004 receptacle stack), M2.5 x 5 from below, M2.5 x 4 from above; the CM5 Cooler clips on each module, its fan lead in `J_FAN1..3` | 0.2 N m | Loctite 243 on the standoff thread only |
| M.2 cards on B16, 6 x | M2.5 x 4.0 standoff at the far end of each socket (`J_M2C1` E-key 2230, `J_M2C2` B-key 3052, `J_M2C3` M-key 2242 spare, `J_M2N1..3` M-key 2242 NVMe), M2.5 x 4 screw | 0.2 N m | none |
| RockBLOCK 9704 on B16 | the Ground Control bracket on its four M2.5 standoffs, the 2x8 IDC lead to `J_RB9704` | 0.2 N m | none |
| LimeSDR Mini in its bay | plugged into the USB 3 A receptacle `J_LIME`; a cable tie base beside the bay and one tie over the board keep it seated | | tie |
| E-paper under the plate | Pervasive Displays E2370KS0C1 face-up under the plate, glass up in the 94.19 x 53.6 window, its side lands taped to the plate's underside with 3M VHB 5915; in the plate's 1.0 mm top pocket a 2.0 mm UV-grade polycarbonate lens 107.19 x 66.6 on a 6 mm die-cut frame of the same tape, 3M Primer 94 on the lens's bonded face; the 24-way flex leaves the left short edge into `J_EPD` on the backer's top strip; no screws | | tape |
| Panel switches (in the plate, their bodies through the backer's slots and holes) | supplied nuts; SW_MAIN, SW_PI, SW_TEST on a die-cut 1.0 mm Silex GP60 silicone washer under the bezel; SW_LIGHT (NKK D3 bushing) with its O-ring (spare AT516) under the nut on the face and the AT428H boot, its D flat east; SW_SOS, SW_EMCON, SW_ZERO with the APEM K seal keyed into the notch toward the operator and the hinged safety covers on SOS and ZEROIZE (cover part owed); flying leads soldered to the backer's lands beside each site, then beaded | hand tight + 1/8 turn | none |
| Headset jacks, 2 x | U-174/U panel jacks (Amphenol Nexus class, drawing owed) through the plate's holes at `HEADSETS`, bushing nut below the backer's 17 mm holes, sealing washer on the face; five-lead pigtail to D8 `J_HS1`/`J_HS2` | hand tight | none |
| Camera module | the USB camera board (about 25 x 25 mm, part owed) on two M2 standoffs behind the plate's 8 mm sealed window at `CAMERA` (`CAM_H1`/`CAM_H2` on the backer), the window glazed from the outside with a 1.0 mm PC disc on VHB 5915; its USB lead to B16 `J_CAM` | 0.15 N m | none |
| Light sensor window | the VEML7700 on the backer under its own Mentor light guide in the plate at `LIGHT_SENSOR` | press fit | none |
| Sounder BZ1 | Floyd Bell MC-09-530-Q through the plate's 28.6 mm hole with the 61663 bezel gasket on the face, nut below the plate, two leads to the lands | hand tight | none |
| QMX tray on the lid, 4 x | the printed tray (`case/lid-bracket-qmx/`) on the lid's inner face over the right strip (X 103.5 to 172.5, Y -51.5 to 71.5 in the plate frame), four M3 into bonded nut plates or bosses on the lid (the lid's inner face is unribbed in Peli's model; the bond is the assembler's: a 2 mm ABS plate with four PEM nuts bonded with DP8005), the unit held by a 16 mm hook-and-loop strap through the tray's slots and by the 6 mm lip | 0.4 N m | Loctite 243 |
| Dock strip to floor | 4 x 3M VHB 5952 pads 20 x 20 at the corners, floor degreased with IPA | | |
| Pack cradle to floor | the printed cradle (`v2/cad/pack_cradle_2590.py`, after the position ruling) on four VHB 5952 pads, the RS PRO 245-556 heater mat stuck to the cradle's floor under the pack | | |
| Blade fuses | 25 A mini blade in A22 `F1` (the pack node), 25 A in E6 `F3` (pack), 10 A in E6 `F1` (vehicle input) and `F2` (solar), Keystone 3568 holders | push fit, seated flush | none; check seating after any transport |
| Dock block E5 | four M3 x 6 standoffs above the strip, face at 7.4 mm | 0.4 N m | Loctite 243 |

Threadlocker: Loctite 243 (medium, oil tolerant) on every machine screw into metal; never on Nyloc nuts, never on the plastic-bodied switch nuts.

## 2. Build order

1. Dock strip E6: solder the entry leads (vehicle and shore pair to `J_DCIN`, solar pair to `J_SOLAR`, VH crimps), the pack cable's XT60 counterpart at `J_BATT` and the SMBus header `J_SMB`, the sensor headers (`J_DCF`, `J_GEIGER`, `J_LTG`, `J_POD`), the two mixer fans (`J_FAN1`, `J_FAN2`), the water electrode leads; fit the three fuse holders with their blades, and check the 20 V bus at the block lands with 9 V and 36 V in. The front end, the tracker and the sensor controller are assembled parts.
2. Dock block E5 on its four M3 x 6 standoffs above the strip. Solder the twelve signal wires and the 12 AWG pair from the strip into the block's plated lands from below; the block's underside legend names every land. Check each wire end to end before the stack goes on, because the lands are covered once A22 is down.
3. Rods: four M3 rods through the floor holes of the strip, then the spacers that set the 13.4 mm gap on all four rods, so A22's spring pins land on the block with the pins compressed about 1 mm.
4. A22 with the Preci-Dip 813-S1-012-10-016101 connector and the nine Mill-Max 0858 class power pins soldered in from the underside (tails on the top face), the eleven Radiall receptacles fitted, and the blade fuse in before anything is energised. Lower it onto the rods and check continuity from the block's wire lands up to the board.
5. D8 onto A22's four 22.6 mm standoffs: the 2x8 harness ribbon `J_MEZZ1` to `J_HARN1`, the 5 V lead `J_MEZZ_PWR1` to `J_PWR1`, the antenna pigtail from `J_ANT` to A22's VHF jack `J_RF1`; the PA drive coax (`J_PAIN`), the PA output coax (`J_PAOUT`), the gate bias lead (`J_VGG`) and A22's 13.8 V lead (`J_PA`) coiled and tied for the plate.
6. 38 mm spacers, B16: the three Compute Modules pressed onto their receptacle pairs and screwed to the standoffs, the coolers clipped on with their fan leads in `J_FAN1..3`, the NVMe drives in `J_M2N1..3`, the WiFi link card in `J_M2C1` (slot 1) with its two MHF4 pigtails to the east wall P2P A and P2P B couplers, the 5G module in `J_M2C2` (slot 2) with its SIMs in `J_SIM1`/`J_SIM2` and its two pigtails to 5G MAIN and 5G DIV, the LimeSDR into `J_LIME` with its pigtail to SDR, the RockBLOCK on its bracket into `J_RB9704` with its pigtail to IRIDIUM, the GNSS pigtail from `J_GNSS1` to A22 `J_RF4`, the LoRa pigtail from `J_LORA1` to `J_RF11`, one module's antenna-kit lead to `J_RF3`, the CR2032, the four rail leads from A22 into `J_5V_S1..3` and `J_5V_DEV`, the PoE lead into `J_54V`, the 26-way ribbon between A22's and B16's `J_AB1` (the two headers sit at the same case XY, one on A22's top and one on B16's underside), the HDMI cable in `J_HDMI` and the camera and QMX leads in `J_CAM` and `J_QMX` left for the face and the lid, the panel ribbon in `J_PANEL`. Nyloc on top.
7. Pack into its cradle, the BTA-70762-2 cable's XT60 into E6 `J_BATT`, its SMBus pair into `J_SMB`.
8. RF: the eleven right-angle plugs sit in their printed float clamps on the strip and mate with the receptacles under A22 as the stack comes down. The wall pigtails run from the clamps to the end-wall couplers, torqued once at the wall side and finger tight at the device side.
9. The face (appendix 32.56, 32.60): press the eight PEM standoffs, the two PA nuts and the sixteen light guides into the plate; the PA module on its thermal pad under the plate with its two coax leads and the bias lead to D8 and the 13.8 V lead to A22; the Xenarc on the plate with its block through the cutout and the gasket ring; the switches, the sounder and the two headset jacks through the plate with their seals, nuts from below; the camera on its standoffs behind the window; the e-paper taped under its window with its lens on the tape frame in the top pocket; then the backer onto the standoffs (its LEDs under the light guides, 8 x M3 x 6), the e-paper flex into `J_EPD`, the switch and sounder leads soldered to the lands beside each site, a bead of DOWSIL 3145 over the LED joints and every lead land, cured; the backer's underside coated (section 5); the MAIN lead to A22 `J_MAINSW` and the PI button leads to `J_PIJ2`'s lands, beaded; the headset pigtails to D8; the HDMI, USB touch and 12 V leads of the monitor below the plate to B16 `J_HDMI`, the slot hub header and A22 `J_MON`; the ribbon into `J_PANEL`; the PORON ring in the plate's band, the plate into the frame, 10 x M3 x 10 with star washers from below. Flood and hose the face in its frame before the stack goes in (appendix 32.34, verification).
10. Lid: the QMX tray screwed to the lid's inner face over the right strip, the unit strapped in, its USB-C lead to B16 `J_QMX`, its 12 V lead to A22 `J_HF` and its BNC-to-SMA jumper to A22's HF jack `J_RF2`, the three in one lid harness tied along the hinge side with a service loop.
11. Lower the lid. With the lid closed the Xenarc stands 28.7 mm above the plate and the tray hangs 28 mm from the lid's inner face over the buttons; the two do not overlap (appendix 32.60 item 5).

## 3. The pack

One BB-2590/U (Bren-Tronics BT-70791CK or Epsilor ELI-2590 NG; sheets in `vendor/battery/2590/`): 125.6 x 111 x 62 mm, about 1.4 kg, two sections with their own protection and gauge on the SMBus. It stands in the printed cradle at the west wall (the position needs the owner's ruling of appendix 32.60 item 7: the pack needs 62 mm beside A22 where the 1450 floor leaves 60 to 64 mm, so either the stack moves 5 mm east or the pack goes into the external box on the back wall) and connects through the BTA-70762-2 cable on an XT60 (pin 2, the pad nearer `F3`, is positive) and the SMBus pair. The heater mat under the cradle runs from A22 `J_HEAT` on shore power below 0 C (`PANEL.md` section 10). Nothing is welded, sleeved or fused inside the pack; the kit fuses the cable at 25 A on E6 and again at A22's node.

## 4. Leads

| Lead | From | To | Wire | Connector |
|---|---|---|---|---|
| Pack power | BB-2590/U, BTA-70762-2 cable | E6 `J_BATT` (XT60) | the cable's 12 AWG | XT60 pair |
| Pack SMBus | the 2590's data pins in the same cable | E6 `J_SMB` (section A on the kit bus, section B on the sensor bus) | 26 AWG twisted | XH2.5 x 6 |
| Vehicle and shore DC | D38999 receptacle on the back-wall plate, DC pair | E6 `J_DCIN` (JST-VH), the lead tied along the back wall, the west end wall and the front wall | 18 AWG, 500 mm | VH crimp |
| Solar | D38999 receptacle, spare pair | E6 `J_SOLAR` (JST-VH), with the DC lead | 18 AWG, 500 mm | VH crimp |
| Block signal wires | E6 `J_BLK` (twelve lands) | dock block wire lands, underside | 24 AWG, 60 mm each, named on the block's legend | soldered both ends |
| Block power pair | E6 `P_CP` and `P_CN` | dock block wire holes | 12 AWG silicone, 60 mm | soldered both ends |
| MAIN button | C7 `J_MAINSW` (two solder lands on the underside, beaded) | A22 `J_MAINSW` (XH2.5) | 24 AWG twisted | XH2.5 at the A22 end; unplugs there |
| PI button | SW_PI's contacts | C7 `J_PIJ2` lands (the panel controller reads it; nothing leaves the backer) | 24 AWG | soldered, beaded |
| Panel ribbon | B16 `J_PANEL` | C7 `J_PANEL` (SMD box header on the underside) | 26-way 1.27 ribbon, 350 mm | IDC 2x13 both ends |
| A to B ribbon | A22 `J_AB1` (top) | B16 `J_AB1` (underside, the same case XY) | 26-way 1.27 ribbon, 80 mm, folded once | IDC 2x13 both ends |
| Mezzanine harness (USB pair, PTT mirror, inhibit, PA rail state, I2C, 3.3 V) | A22 `J_MEZZ1` | D8 `J_HARN1` | 16-way ribbon, 60 mm | IDC 2x8 |
| Mezzanine 5 V (2 A eFuse on A22) | A22 `J_MEZZ_PWR1` (VH) | D8 `J_PWR1` (VH) | 18 AWG, 60 mm | VH |
| Slot rails, 3 x (5.1 V, 6 A converters, INA226 monitored) | A22 `J_5V_S1..3` (VH) | B16 `J_5V_S1..3` (VH) | 16 AWG, 150 mm | VH crimp both ends |
| Device rail | A22 `J_5V_DEV` (VH) | B16 `J_5V_DEV` (VH) | 16 AWG, 150 mm | VH crimp both ends |
| PoE feed (54 V) | A22 `J_54V` (VH) | B16 `J_54V` (VH) | 18 AWG, 150 mm | VH crimp both ends |
| PA rail (13.8 V, EMCON gated) | A22 `J_PA` (VH) | the RA30H1317M1 VCC pins on the plate | 16 AWG, 300 mm | VH at A22, soldered at the module |
| PA gate bias | D8 `J_VGG` (PH 1x2) | the module's VGG pin | 24 AWG twisted, 250 mm | PH at D8, soldered at the module |
| PA drive | D8 `J_PAIN` (U.FL) | the module's RF input pin | RG-178, 250 mm | U.FL at D8, soldered at the module |
| PA output | the module's RF output pin | D8 `J_PAOUT` (SMA) | RG-316, 250 mm, bend radius 12.5 mm | soldered at the module, SMA at D8 |
| VHF antenna | D8 `J_ANT` (SMA) | A22 `J_RF1` (VHF jack) | RG-316, 120 mm | SMA both ends |
| Headsets, 2 x | D8 `J_HS1`/`J_HS2` (PH 1x5: SPK GND MIC GND PTT) | the U-174/U jacks on the plate | 5 x 24 AWG, 300 mm | PH at D8, soldered at the jack |
| HF rail (12.0 V, EMCON gated) | A22 `J_HF` (VH) | the QMX's DC lead (2.1 mm barrel) in the lid harness | 18 AWG, 500 mm | VH at A22 |
| QMX USB | B16 `J_QMX` (PH 1x4) | the QMX's USB-C in the lid harness | USB 2.0 lead, 500 mm | PH at B16, USB-C at the unit |
| HF antenna | the QMX's BNC in the lid harness | A22 `J_RF2` (HF jack) | RG-316, 500 mm | BNC male at the unit, SMA male at A22 |
| Monitor 12 V | A22 `J_MON` (VH, 1.2 A eFuse) | the Xenarc's DC lead below the plate | the monitor's own lead, spliced under shrink | VH at A22 |
| Monitor HDMI | B16 `J_HDMI` | the Xenarc's HDMI lead | the monitor's own cable, 500 mm | HDMI A at B16 |
| Monitor touch USB | a B16 slot hub header | the Xenarc's USB lead | the monitor's own cable | PH at B16 |
| Camera | B16 `J_CAM` (PH 1x4) | the camera module behind the plate window | USB 2.0 lead, 300 mm | PH both ends |
| Ethernet | B16 `J_ETH` (RJ45) | the sealed RJ45 on the connector plate (PoE out on 1-2 and 3-6) | Cat 5e patch, 400 mm | RJ45 both ends |
| USB-C outlet, power side | A22 `J_USBC_OUT` (5-pin: VBUS CC1 CC2 GND GND) | the sealed USB-C receptacle on the connector plate | 18 AWG VBUS and GND, 26 AWG CC | soldered at the receptacle |
| USB-C outlet, data side | A22 `J_USBW` (PH 1x4: D+ D- GND GND; the pair reaches B16's slot hubs over the A-B ribbon) | the same USB-C receptacle | USB 2.0 pair, 150 mm | PH at A22 |
| Wall USB host | the Glenair 233-370 feed-through on the connector plate | B16 `J_USBX` (PH 1x4, slot 3 hub port 4) | USB 2.0 lead, 400 mm | USB-A at the feed-through, PH at B16 |
| Cooler fans, 3 x | the CM5 Coolers | B16 `J_FAN1..3` (SH 1.0) | the coolers' own leads | SH housing |
| Mixer fans, 2 x | the two IP68 fans on their brackets at the stack's ends | E6 `J_FAN1`/`J_FAN2` | the fans' own leads | SH housing |
| Heater mat | A22 `J_HEAT` (XH2.5) | the RS PRO 245-556 mat under the cradle | the mat's PTFE leads | XH2.5 at A22 |
| Outside sensor pod | the pod on the connector plate | E6 `J_POD` (PH 1x4: 3.3 V GND SDA SCL) | the M8 receptacle's inside pigtail, 400 mm | PH at E6 |
| Sensor modules | the DCF77, Geiger and lightning boards on their standoffs beside E6 | E6 `J_DCF`, `J_GEIGER`, `J_LTG` | 3, 3 and 5 x 24 AWG, 100 mm | PH |
| Water electrodes | E6 `PAD_W1`/`PAD_W2` | two bare copper strips on the floor at the low corner | 22 AWG, 150 mm | soldered |
| GNSS, LoRa pigtails | B16 `J_GNSS1`, `J_LORA1` (U.FL) | A22 `J_RF4`, `J_RF11` | U.FL to SMA, RG-178, 150 mm | U.FL at B16, SMA at A22 |
| WiFi link card pigtails, 2 x | the AW7915-AED's two MHF4 connectors | A22 `J_RF6`, `J_RF7` (P2P A, P2P B) | MHF4 to SMA, 200 mm | MHF4 at the card, SMA at A22 |
| 5G pigtails, 2 x | the RM520N-GL's MAIN and DIV connectors | A22 `J_RF8`, `J_RF9` | MHF4 to SMA, 200 mm | MHF4 at the module, SMA at A22 |
| Iridium | the RockBLOCK 9704's SMA | A22 `J_RF10` | RG-316, 120 mm | SMA both ends |
| SDR | the LimeSDR Mini's SMA | A22 `J_RF5` | RG-316, 150 mm | SMA both ends |
| WiFi 2.4 | one Compute Module's antenna-kit lead (slot 1) | A22 `J_RF3` | the kit's own lead (U.FL to SMA) | SMA at A22 |
| RF jumpers, 11 x | the float clamps on E6 (Radiall R222M80500 right-angle plugs, crimped, tied into the clamp) | the SMA couplers in the end walls (Amphenol Connex 132170, NBR O-ring 6.5 x 1.0 under the outside hex; west VHF, HF, WIFI 2.4, GNSS, SDR at Y -72, -48, -24, +24, +72; east 5G MAIN, 5G DIV, IRIDIUM, LORA, WIFI P2P A, WIFI P2P B at Y -96, -72, -48, -24, +48, +96; all at Z 88) | RG-316, 150 to 250 mm, bend radius 12.5 mm | SMP-MAX plug at the clamp, right-angle SMA male at the coupler |
| Connector plate | 54 x 82 x 3 aluminium, upright over the wall window (`case/wall-receptacles-1to1.pdf`, appendix 32.29 and 32.42) | the back long wall (hinge side) between the inner ribs at X -95 and -18, plate centre X -56, 54 mm above the floor | six M4 x 16 stainless, washers both sides, Nyloc inside, 1.2 N m in a cross pattern; 2 mm closed-cell gasket | carries the D38999 DC receptacle (shell 13) and the 233-370 USB feed-through (shell 15), each on its own gasket with M3 x 10 and spring washers; the sealed RJ45, the sealed USB-C, the pod's M8 receptacle and the ground stud join it when their parts are picked (the plate is regenerated by `tools/case_wall_cutouts.py`) |

Every lead tied at both ends; the rod stack's edge carries the vertical runs with a tie base per bay; the lid harness (QMX USB, 12 V, BNC jumper) has a service loop at the hinge.

**External cables (appendix 32.32, sheets in `vendor/d38999/`).** Two cables leave the case through the connector plate on the back wall.

| Cable | Kit end | Cable | Far end |
|---|---|---|---|
| DC lead | Glenair D38999/26FC4SN plug (shell 13, insert 13-4, four M39029/56-352 size 16 socket contacts, key N, electroless nickel), crimped with the M22520/1-01 tool and the M22520/1-04 positioner, seated with M81969/14-03; Glenair M85049/38S13N self-locking straight strain relief on the plug's M18 x 1 thread | Lapp OLFLEX ROBUST 210 4 x 1.0 (article 0021917, 6.6 mm, TPE, outdoor), or Alpha Wire 25064 (18 AWG 4C, TPU, 6.58 mm); 2 m | the four cores split under adhesive-lined shrink into two 0.3 m tails: the DC pair to the shore supply or to the NATO 2-pin vehicle plug (9 to 36 V, the front end takes either), the solar pair to the panel |
| USB host lead | Glenair 233-340 plug (shell 15, USB 2.0 Type A male front and Type A female back, key N, horizontal, with the 770-028 shrink boot), screwed onto the feed-through | a standard USB 2.0 Type A male to Type A female extension, 1.5 m, its plug in the back of the 233-340 and the boot shrunk over its jacket | the extension's Type A female, into which the device's own lead plugs |

Contact assignment of the DC plug: A DC positive, B DC return, C solar positive, D solar return; Lapp cores 1 to 4 in that order, Alpha colours black, red, white, green. The cable's insulated cores must lie inside the size 16 grommet window of 1.65 to 2.77 mm (MIL-DTL-38999 Table IV); the Alpha cores are 2.0 mm, the Lapp core diameter is measured on the reel before that cable is used.

The dock interface is not a lead but belongs in the same reading. Twelve Preci-Dip 813 contacts in `J_DOCK` on A22's underside land on the raised block's targets: pins 1 to 4 carry `VIN_RAW` (the 9 to 36 V input passed up for the monitors), 5 to 7 ground, 8 `SHORE_INHIBIT`, 9 and 10 the USB pair of the wall outlet's console path, 11 and 12 the sensor controller's lines. Beside them, nine Mill-Max 0858 class pins carry the pack current: four on the node, four on the return, and one longer pre-charge pin that mates first through a 10 ohm resistor so the converters' input capacitance does not draw an arc across the main pins. The eleven RF joints mate at the same time, and the whole set parts when the stack is lifted.

## 5. Conformal coating

IPC-CC-830 acrylic (MG Chemicals 422B or equal) on A22, B16, D8, the dock strip E6 and the dock block E5 after the bench fit, two thin coats. Masks (kapton) before coating: every connector face and its keying, the spring-pin targets and the pack targets on E5 and the pins on A22, the SMP-MAX receptacles and the SMA and U.FL bodies, the six Compute Module receptacles and the seven M.2 sockets (assembled cards are not coated), the RockBLOCK bracket, the LimeSDR receptacle, the SA868 module and the relay, the water electrodes and the sensor headers on E6, the test points that the bench list uses. C7: the whole underside is coated after the silicone beads have cured, with `J_PANEL`, `J_EPD`, the lead lands and the eight standoff rings masked (the rings bond the backer to the plate); the top side is not coated where the LEDs stand. The plate is bare anodised aluminium.

## 6. Labels (MIL-STD-130 style)

- Plate nameplate field at `NAMEPLATE` (78, -101), 76 x 26: "MESHSAT FIELD KIT", P/N MSK-FK-1450, S/N, REV A, a 10 x 10 mm data matrix with the S/N, "MADE IN NL"; laser-marked with the plate's other legends (`v2/cad/face_plate.py`).
- Every board: P/N, S/N, REV silk fields near the title block silk.
- Case: asset label in Peli's label recess; "RF HAZARD DURING TX" 20 x 40 mm next to the VHF coupler; the bulkhead legend strips (west VHF HF WIFI 2.4 GNSS SDR, east 5G MAIN 5G DIV IRIDIUM LORA P2P A P2P B) beside the SMA rows.

## 7. Removal and refit

Open the lid (the QMX tray swings with it; unplug the lid harness at B16 `J_QMX`, A22 `J_HF` and `J_RF2` if the lid is to come off its hinge), take out the ten plate screws, lift the face plate with the backer C7, the monitor, the PA module and the switches hanging under it (the panel ribbon, the MAIN lead, the headset pigtails, the PA leads and the monitor's three leads unplug at the B16, A22 and D8 ends), then lift the A22 + D8 + B16 stack straight up through the frame window (349.65 x 233.83; A22 is 240 x 160, B16 330 x 200). No connector is unscrewed: the eleven RF joints, the twelve signal contacts and the nine power pins all part as the stack rises. The pack lifts out of its cradle after its XT60 and SMBus are unplugged at E6. Refit in reverse; the rods through the dock strip's holes align everything, and the pre-charge pin meets its target before the four main ones.

## 8. Commissioning after assembly

`TEST-PLAN.md` is the qualification programme; the list below is what to check once, in this order, on the first kit.

1. Dock strip alone: the 20 V bus at the block lands with 9, 12, 24 and 36 V in; reverse polarity applied for 10 s (no damage, no output); the fuse blows on a bolted short. Then the tracker: a panel or a bench supply through a series resistor, and the tracking point holds while the load changes. The sensor controller enumerates on the bench USB lead and reports every sensor it has.
2. Dock block alone, before the stack goes on: continuity from every wire land to its target, and no continuity between neighbours. This is the last moment the lands are reachable.
3. A22 alone, pack not connected: a bench supply at 14.4 V on the node contacts through a 5 A limit. Each rail comes up at its own converter (the three slot rails and the device rail at 5.1 V within 0.1 V, the PA rail at 13.8 V, the HF rail at 12.0 V, the PoE rail at 54 V, the 3.3 V logic); 3 A drawn from a slot rail holds it above 5.0 V. The charger enumerates on the bus, the monitors read, and the main power control turns the rails off and on from the MAIN button. With `EMCON_HW` high the PA and HF rails stay off.
4. Charge: 12.0 V on the DC inlet, the pack connected with its SMBus. The charger takes its programmed current into the pack and stops when the pack's own thermistor reports outside the window.
5. The stack with B16: each module boots from its rail with the other two slots disabled, then all three together; every USB device enumerates on its hub; the Ethernet switch links all three and the wall port. Record each rail's current at idle and with the display on.
6. Bursts: 5G registration, one Iridium session, one LoRa transmission and one VHF key-down in turn, each rail watched at its connector, then all within the same second: what is being recorded is the margin.
7. Panel: the panel controller enumerates; lamp test lights all 17 LEDs; BLACKOUT kills the rail; the EMCON toggle locked closed keeps the SA868 and the PA in receive while the bridge asserts PTT and opens every transmitter rail gate; ZEROIZE armed shows on the e-paper and wipes the secure element at 5 s.
8. Power loss: pull the DC lead and confirm the kit keeps running from the pack and the panel shows SHORE off.
9. Shore inhibit: `SHORE_INHIBIT` high holds the front end off within a second, low restores it.
10. PA: 10 minutes of key-down at 30 W into a load; the plate temperature at the flange and the case skin temperature recorded, the fans running.
11. Blind-mate: lift the stack and set it back three times. Every RF path still passes, the pre-charge pin still mates first, and nothing on the block is scored.

## 9. Bench-fit lists (hand-fitted parts per board, not on the JLC BOM)

- A22: the Preci-Dip 813-S1-012-10-016101 spring connector and the nine Mill-Max 0858 class power pins on the underside (tails soldered on the top face), the eleven Radiall R222M00720 blind-mate receptacles, the Keystone 3568 holder with its 25 A mini blade, the inductors that have no assembler equivalent (read the ORDER-NOTES), the rail leads, the PA, HF, monitor and heater leads, the MAIN button lead, the wall USB-C leads.
- B16: the three Compute Modules (CM5108064) on their receptacles and standoffs, the three coolers with their fan leads, the WiFi link card, the 5G module with its two SIMs, the three NVMe drives, the LimeSDR, the RockBLOCK on its bracket, the CR2032, the rail and PoE leads from A22, the antenna pigtails, the HDMI cable, the camera and QMX leads, the panel and A-B ribbons; the LG290P, the E22 and the two E72 are assembled where JLCPCB stocks them, else hand-soldered.
- C7 (the backer under the plate; the switches, the jacks, the camera and the sounder mount in the plate and only their leads reach the board): the sixteen 3 mm LEDs standing on the top face under the light guides (beaded to 5.3 mm), the Floyd Bell sounder with its gasket, the three C&K switches, the NKK toggle, the three APEM toggles with their covers, the two U-174/U jacks, the camera module, the PDi e-paper on its ZIF, the RP2040 and its flash if JLCPCB has no stock, the two XH leads.
- D8: the SA868 module where JLCPCB has no stock, the G6K relay if short, the U.FL and SMA leads to the PA and the antenna, the two headset pigtails, the VGG lead; the PA module itself is a plate part.
- E6: the three Keystone holders with their blades, the JST-VH DC and solar leads, the XT60 counterpart and the SMBus header, the twelve signal wires and the 12 AWG pair up to the block, the eleven printed float clamps (`v2/cad/float_clamp.py`, two M3 x 8 each into the strip's clamp holes, the plug's cable tied into the clamp's slot) with their Radiall R222M80500 plugs, the DCF77, Geiger and lightning modules on standoffs beside the strip, the two mixer fans, the water strips, four VHB pads.
- E5: nothing is placed on it by the assembler. It goes on four M3 x 6 standoffs above the strip, and the twelve signal wires and the 12 AWG pair are soldered into its plated lands from below before the stack is fitted.
- Case and face: the connector plate with its receptacles on the back wall, each on a Glenair 930-001 silicone flange gasket, the six M4 plate screws with bonded sealing washers, the eleven Amphenol Connex 132170 SMA couplers in the end walls at Z 88 (D-holes, 8 mm nut and lock washer inside, an NBR O-ring 6.5 x 1.0 under the outside hex), the sensor pod on its M8; the face seals and hardware of `vendor/seals/` and `vendor/mentor/`: the die-cut PORON ring and the e-paper tape frames from `face-plate.dxf`, the 2.0 mm UV polycarbonate lens with 3M Primer 94, three Silex GP60 silicone washers, the NKK AT516 spare O-ring and AT428H boot, the APEM K seals, the Floyd Bell 61663 gasket, sixteen Mentor 1282.5004 light guides, eight PEM SO-M3-10 standoffs and two S-M3 nuts, the Xenarc gasket ring, DOWSIL 3145 clear for the beads, MG Chemicals 422B for the backer's underside, ten star washers and M3 x 10, the 3M 7871EC serial label; the QMX tray with its nut plates and strap.

## Disassembly and reassembly in pictures (render set eight, 7 Sep 2026)

The concept set `v2/images/concept-1450/` carries the sequence a technician follows; every removed part is set down beside the case in the picture:

1. `meshsat-1450-assembly-1-closed.png`: the kit closed, latches shut, antennas off, cables out.
2. `meshsat-1450-assembly-2-lid-open.png`: lid open; the face plate with the monitor, the switches, the headset jacks and the e-paper is the first thing seen, the QMX tray on the lid's inner face.
3. `meshsat-1450-assembly-3-plate-off.png`: the ten M3 screws out, the face plate assembly (plate, backer C7, monitor, PA module, switches, jacks, e-paper) lifted on its ribbon and set down east of the case.
4. `meshsat-1450-assembly-4-stack-out.png`: the A22 + D8 + B16 rod stack lifted straight up off the dock's blind-mate joint (no cable unscrewed: every antenna path mates at the dock strip) and set down west of the case.
5. `meshsat-1450-assembly-5-battery-out.png`: the BB-2590/U lifted out of its cradle at the west wall (its cable unplugged at the dock strip) and set down in front.
6. `meshsat-1450-assembly-6-dock.png`: the empty case: the dock strip E6 with its eleven float clamps and the pigtails from the end-wall couplers, the block E5, the sensor modules, the connector plate leads.

Reassembly is the same sequence in reverse: pack into the cradle and its cable in, the rod stack lowered onto the dock (the float clamps align the SMP-MAX plugs), the face plate onto the frame and its ten screws, lid closed. Nothing has been built; the pictures are the design intent.
