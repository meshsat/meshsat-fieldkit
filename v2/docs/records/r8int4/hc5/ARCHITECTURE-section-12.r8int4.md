## 12. Interface contracts

The contracts are data in `v2/ecad/tools/pcb_interfaces.yaml`, section `board_to_board`: both ends, the pin map, the
state of every control line when the cable is out, the power carried, the hot-plug rule, which tool judges which part,
and the open findings. **Why that file.** It already holds each interface's requirements from the part that defines it,
so the contracts that Review C asks to be "owned on both ends" (`EXECUTION-PLAN.md`) sit beside them instead of in a
second registry. Its only reader, `interfaces.py` (rule INT-001), and its fixtures read the `interfaces` and `boards` keys
and nothing else; no rule's tool reads the contracts (the record script `records/hc5/check_contract_fields.py` reads
their fields, never their truth), and the map-identity checks they cite stay in `check_contracts.py` as
code, cited by section number (section 1 the J_PANEL map, 3 the rails, 4 and 5 the dock, 7 J_AB1, 7b J_AB2, 8
J_MEZZ1/J_HARN1, 10 the wall pair, 12 to 15 the inhibit line, 15b the pack leads, 15c the pack SMBus lead). So a contract
line is a contract, not a verdict. `check_contracts.py` read PASS 96 of 96 on the netlists at `e3aedb25` (the layer 5
audit's re-run in scratch, verdicts written outside the tree; RECORDED there, not committed); the committed INT-001
readings are AWAITING_REVALIDATION (TOOL_CHANGED) in `CURRENT-EVIDENCE.md`, and board E5's `interfaces_e5` is a PASS over
a denominator of 0 (all still so at `84e52461` and at `a8652172`, where a re-take alone would read CURRENT_CANDIDATE on
the six boards with a netlist).

**Thirty contracts since 27 September 2026.** The first twelve (26 September) covered the board-to-board ribbons,
leads and blind-mate row; the layer 5 closer added eighteen for the interfaces they left out: the external DC and solar
entry, Ethernet with PoE out, the monitor, the RF pigtails, board D's VHF port, the headsets, the camera, board E's pod,
sensor modules, tamper reed, water electrodes and fans, board A's heater, board P's cell leads, board B's cooler fans,
LimeSDR and RockBLOCK, and (round 8) board D's flange thermistor. **What each of the eighteen carries:** its ends (a board,
reference, part and source for every board end; the device, case or cable part, or TBD with its effect, for the other
end), harness, levels, current, default state, sequencing, mating, hot-plug rule, the tool that judges it, and a `tbd`
list; each of those fields holds a value, "n/a: reason" or "TBD: ... effect", and every `tbd` entry names its effect.
`records/hc5/check_contract_fields.py` asserts this on the file and prints which field is a value, n/a or TBD, contract by
contract (`records/hc5/check_contract_fields.out.txt`: 18 of 18). **The first twelve were written before that field list
and do not carry it:** they hold their content under `cable`, `power`, `cable_out_states` and `map_identity`, and the same
output lists, as information, the fields each has no key for (levels, current, sequencing, default state and mating on
most). So the layer's items for levels, current, sequencing, default states and mating are shown field by field for the
eighteen and not yet for the twelve; bringing the twelve to the same fields is the integrator's re-anchor action. The
hot-plug rules marked
"(proposed)" are the session's choice SC-HF-04 since the same day. The firmware obligations the contracts rest on are
itemised in `HW-FW-CONTRACT.md` (version 1), whose section 6 also budgets the kit I2C bus that IF-BC-PANEL, IF-AB-RIBBON
and IF-AD-HARNESS carry: as one segment it cannot meet the 300 ns rise its BQ25731, TPS23861 and ATECC608B require
(HF-F01), and the session took three segments behind two TCA9517A (SC-HF-02), owed on boards A and B.

| Contract | Ends | Carries | Judged today by | Open items |
|---|---|---|---|---|
| IF-BC-PANEL | B J_PANEL, C J_PANEL (2x13) | PANEL_5V, kit I2C, every safety line, heartbeats, slot enables, panel USB | `check_contracts.py` section 1 (map identity) | the SLOT_EN hold (4.3); I3-F01 (supervisor addresses, a firmware contract); HF-F01 and SC-HF-02 (the kit bus); EMCON L1 and L2 (drawn at desk on B and C in their round 8; C's GPIO21 is off the line since `9f28c238`); FAB-04 on HDMI_SEL1/2 (10 k since board B's round 8 (27 September 2026)); B_PANEL_5V: F1 an MF-MSMF110 (1.1 A hold) under the 1.23 A conductor since then, its hold 0.95 A at 40 C against board C's 1.0 A peak (4.5); the ribbon and IDC parts have no MPN (their rating is TBD) |
| IF-AB-RIBBON | A J_AB1, B J_AB1 (2x13) | control lines to A, USB to D and E, the kit I2C | section 7 | the SLOT_EN hold; EMCON L2 (R102 10 k 1 % in board A's round 8); HF-F01 |
| IF-AB-WALL | A J_AB2, B J_AB2 (2x5) | the wall USB pair, on A to the Glenair 233-370 behind U32 (D-12) | sections 7b and 10 | W4-F17 (the header under board D); the J_AB2 lead length (no row in `ASSEMBLY.md` section 4) |
| IF-AB-POWER | A and B J_5V_S1..3, J_5V_DEV, J_54V (VH) | slot rails, device rail, 54 V | section 3 (net presence) | the two ends' current declarations disagree (I-03: +5V_S2 A 2.5 A against B 4.2 A typical, 5.63 A coincident; +5V_DEV A 3.2 A against B 3.8 A); the JST-VH rating document is not held |
| IF-AD-HARNESS | A J_MEZZ1 and J_MEZZ_PWR1, D J_HARN1 and J_PWR1 | D's USB, inhibit, PA_EN, I2C, 3.3 V and 5 V | section 8 (not the 5 V lead) | W4-F17; EMCON L4 on D (closed at desk in board D's round 8 but for bench E-11); PWR-F15 drawn in round 8 as IF-D-FLANGE; HF-F01 |
| IF-AE-DOCK | A J_DOCK and pack pins, E5, E J_BLK, P_CP, P_CN | VIN_RAW, CELL+, pre-charge, USB, SHORE_INHIBIT; lifted only by the D-14 procedure, with a cap over E5 | sections 4 and 5; `block_contract.py` needs pcbnew | the VIN_RAW contacts: 12.31 A declared on A gives 3.08 A of 3.5 A per contact with even sharing and no margin for one open (R4A-N13); board E's round 8 declares 14.10 A, 3.53 A each, over the rating at nominal (R8E-N01); A04-D2 on the A32 board; BAT-F06 (stated, section 4.4) |
| IF-PE-PACK | P W_P, W_N, J_SMB; E J_BATT, J_SMB | pack power, gauge SMBus and PRES on JST-XH 1x4 at both ends in P's pin order | section 15b (the power pair) and 15c (the SMBus lead, since `93138ac1`) | PRES's contract (P's R14 10 k stays; E's GPIO17 pad pull-down off before a read, FW-E02); PWR-F12 |
| IF-AC-MAINSW | C J_MAINSW, A J_MAINSW | the MAIN button | none | none open in the circuit (`458b2873`) |
| IF-AE-RF | A J_BM1..11, E float clamp bar, the end-wall arrestors | eleven RF paths as generated, twelve under D-07 | `check_pcb_e.py`, which reads board A's `RF_X` (and since round 8 D-07's X 46, the pitch, seats, holes and the bar outline) | the clamp bar drawn in round 8 (A09, R4E-07, `45f6d83f`), not placed, with board E's SENS region under it to re-seat at layout entry; ANT3's site on A (D-07); the jumpers to the arrestors (`CASE-MARGINS.md` 3.4) |
| IF-A-PA | A J_PA, D J_VGG, J_PAIN, J_PAOUT, the PA module | 13.8 V limited by its stage's own loop, bias at 4.48 V, RF | none | F-PR-02 (drain current, bench); D-04 band lock (FW-D03) |
| IF-LID-HF | A J_HF, J_RF2, B J_QMX, the QMX | 12 V, USB, HF antenna | none | W3-F25 (checks) |
| IF-EXT-USB | the wall ports | data on the Glenair 233-370 (console and key fill) behind U32; the USB-C power only, with the CC ESD array U31 (D-12, D-17) | section 10 (the wall pair) | none (the `ASSEMBLY.md` row is corrected since `9a151c78`) |
| IF-EXT-DC | E J_DCIN, J_SOLAR (VH); the D38999 receptacle, shell 13, contacts A to D | 9 to 36 V vehicle or shore, and a 100 W panel | none | the receptacle's MPN (`CASE-MARGINS.md` section 6); the VH and size 16 contact ratings read into the record; R8E-N01 downstream |
| IF-EXT-ETH | B J_ETH (RJHSE5380); a sealed RJ45 on the plate | 1000BASE-T, PoE out 802.3at from U5 | INT-001 judges `SWP4_*` (the switch to the magnetics) through `SWP*`; nothing judges `MDI_A..D` (the magnetics to J_ETH), which match no pattern and carry no declared tolerance | the MDI side unjudged (HF-F08; decisions 29 and 36's correction of 21 September 2026); the sealed RJ45; GND-002's shell to CHASSIS (not drawn); the PoE class offered |
| IF-MON | A J_MON (VH), B J_HDMI, D J_USB3 (the touch, SC-HF-06); the Xenarc 709GNK | the pack node behind U21 (1.2 A), HDMI from the display switches, the touch USB at full speed on board D's hub, shared by the HAL to the display owner (FW-B19) | INT-001 on the HDMI pairs (HDMI_CM5 on B) and on the touch pair (USB_FULL_SPEED on D) | HF-F06 (J_USB3's VBUS has no port limit and is budgeted 0.05 A against the touch's unknown draw); FAB-02, FAB-04; a latching HDMI plug |
| IF-BA-RF | B's U.FL sites, the modules' MHF4 and SMA ports; A J_RF3 to J_RF11 | GNSS (with its active antenna's DC bias, which the GTH-SFF-AL arrestor passes), LoRa, WiFi link, 5G, Iridium, SDR, WiFi 2.4 | none | ANT3 (D-07): board A's site at X +46 is in no generator (`gen_pcb_a.py` `RF_X` has eleven sites), while board E's cavity at X 46 is drawn since `45f6d83f`; each path's loss at its own length |
| IF-DA-VHF | D J_ANT, A J_RF1 (SMA, RG-316 120 mm) | the 30 W VHF output | none | RG-316, SMA and SMP-MAX power figures at 144 MHz |
| IF-HS | C J_HSJ1/2 (U-174/U), D J_HS1/2 (PH 1x5) | speaker, microphone, PTT per headset | none | the U-174/U drawing and its pin assignment |
| IF-CAM | B J_CAM, the camera module | USB 2.0 and switched 5 V | INT-001 on CAM_D* | the camera part; the housing differs between the netlist and `ASSEMBLY.md` (HF-F04) |
| IF-E-POD | E J_POD; the M8 receptacle and the outside pod | the sensor controller's own I2C and 3.3 V, leaving the case | none | the M8 and pod parts; ESD at the plate; the sensor bus capacitance with the outside cable |
| IF-E-SENSORS | E J_DCF, J_GEIGER, J_LTG; three modules | pulse inputs, the sensor bus, the Geiger's switched 5 V | none | the module parts; the Geiger pulse's level into GPIO7 (HF-F07) |
| IF-E-TAMP | E J_TAMP (XH 1x2); the Littelfuse reed | the lid state, always powered | none | none (logs only: owner ruling D-03, "the tamper and lid switch logs only") |
| IF-E-WATER | E PAD_W1/2; two floor strips | the water sense on an ADC input | none | the electrode material; the threshold (bench) |
| IF-E-FANS | E J_FAN1/2; two IP68 fans | the pack node, a low-side switch, a tachometer | none | the fan part and its rating at 16.8 V (HF-F05); the housing (HF-F04); gate pull-downs on Q9, Q10 (HF-F07) |
| IF-A-HEAT | A J_HEAT (XH 1x2); the RS PRO 245-556 mat | 12.0 V, 7.5 W behind U22 | none | none |
| IF-P-CELLS | P W_BP, W_BN, J_CELL, J_TS, J_TS2; the 4S3P block | the pack current, the cell taps, five thermistors | none (section 15b judges the outgoing leads) | the connection order at pack build; PWR-F12 |
| IF-B-FANS | B J_FAN1..3 (SH 1x4); the three coolers | the slot rail, PWM and tachometer on each module's own pins | none | the fan part and current |
| IF-B-LIME | B J_LIME (USB 3 A); the LimeSDR Mini 2.4 | USB 3.0 and +5V_LIME behind U23, removed under EMCON | INT-001 on LIME_SS*, LIME_D* | none |
| IF-B-RB9704 | B J_RB9704 (IDC 2x8); the RockBLOCK 9704 | UART, control and status, +5V_RB behind U24, removed under EMCON | none | SD-EMC-2 back-feed through the control lines (U6's internal pull-ups hold RB_IEN and RB_CTRL high until U6 is configured); no `ASSEMBLY.md` row for the 16-way lead |
| IF-D-FLANGE | D J_FLANGE (XH 1x2, round 8); the flange NTC | the PA flange temperature for K2 and C4 | none | the NTC's bond; PWR-F16 |

Not given a contract, deliberately: sockets that carry a module on its own board (the M.2 sockets, the SIM holders,
the CM5 receptacles), the bench-only headers (`J_DBGx`, `J_FLASHx`, `J_RPIBOOTx`, `J_IOCOFF_x`, the SWD and cJTAG lands,
`J_GNSS2`) and the e-paper's flex (on board C alone). The bench access these give is NEED-14's, in `ASSEMBLY.md`
section 8 and each board's bring-up page. Board D's hub port `J_USB3` is not in this list: since the session's choice
SC-HF-06 it is the board end of the monitor's touch lead, contracted in IF-MON above and in `ASSEMBLY.md` section 4 and
build step 9 and `PANEL.md` section 1.
