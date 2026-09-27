# Board B (compute): layout constraints

**Bound to the H2 line (after H2, 27 September 2026).** Candidate re-read at `ef144760`: phase B21, netlist
`v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net` sha256/16 `8b78c59754a6a0c7` (board B's round 8 at `b76c18cb`, last
changed by set 5 at `caba1876`), intent `pcb-b-compute-intent.json` `162fcb9b95f680a7`; the committed board file
`2e64b5bf2d9cd3bc` carries B21's older netlist (SCH-002 FAIL) and 416 unrouted connections. Section 2's table is
checked against `calc/rail_widths.py` on that intent: every rail it lists reads the same; the H2 intent declares seventeen
more supplies, each at most 0.3 A typical (the added row, marked **H2**). Board B is not at layout entry: **7 reasons at H2**
(`CURRENT-EVIDENCE.md`): SI-001 INCONCLUSIVE, RF-002 FAIL (EQ-25), FEA-001, FEA-002, FEA-003, FEA-006, FEA-007. Known
changes of the H2 line to the rest of this sheet: round 8 is merged (`b76c18cb`: the fabric's locked break-before-make,
FAB-01 to FAB-04, EMCON on each module's own rail, the 5G module's supply removed in hardware, the M.2 socket's
locating holes, F1 the MF-MSMF110), and set 5 declared every supply from its maker's sheet with decision 42's class on
every decoupling entry (`caba1876`); PANEL_5V's row is corrected below. Every other line below is the reading at `e3aedb25`, not re-read against the H2 netlist; where it and a record disagree, the record governs (README).

As first written: a view over the records at `main` `e3aedb25` (conventions and shared rules: [README.md](README.md)),
candidate then netlist `669d02d07aeaae4b`, intent `cf461c0b75ce368b`, 16 blocker lines, round 8 not yet integrated
(the lines below were to be re-read on its merge; FB-FAB-1 to FB-FAB-5 of `v2/docs/feasibility/FAILOVER-FABRIC.md`
closed on it first).

**Board B has no layout candidate yet and no layout should start from this sheet alone**: its stackup is undecided
(section 1) and its escape and placement strategy is FB-FAB-6, owed by Q-B-ESC-2 and decision 43's whole-board run.

## 1. Stackup and layer use: UNDECIDED

- **As built:** six layers, JLC06161H-3313, 1 oz outer, 0.0152 mm inner: F sig, In1 GND, In2 sig, In3 sig, In4 four
  split 5 V planes (+5V_DEV, +5V_S1, +5V_S2, +5V_S3), B sig (zone census of B21; `B-FEASIBILITY.md` section 3.2).
- **Candidates and what decides between them:** `v2/docs/STACKUP-DECISIONS.md` section 4. In short: option A2 (In3 to
  GND) gives three controlled routing layers on a board that did not route with four; eight layers (JLC08161H-2116,
  recorded in `STACKS`, owner decision 43's measurement) give four. **The session's recommendation for decision 43's
  run input, not a decision:** S G S G P S G S, 5 V domains on In4, pairs on In5 kept inside one 5 V region or with a
  stitching capacitor at every crossing (RET-003). Price: none; the eight-layer price goes to the owner before any
  order (decision 43).
- **Two sides assembled:** B21 carries 464 SMD footprints on its back; the underside rule is "never beneath a
  fine-pitch part whose escapes need the vias" (`gen_pcb_b3.py:155`, quoted in decision 42).

## 2. Power: band widths at the declared currents

From `calc/rail_widths.py` (decision 35, 10 K). Where a maker's figure exceeds the declaration (POWER-THERMAL PWR-F01,
F03, F05), the maker's figure is the one to size to, and the row says so.

| rail | typ / peak A | one outer face, mm | inner, mm | barrels 0.3 / 0.4 / 0.5 mm | note |
|---|---|---:|---:|---|---|
| +5V_S2 | 4.2 / 5.0 | 2.17 | 13.64 | 7 / 6 / 5 | the 5G slot; board A declares 2.5 A typical on the same rail (IF-AB-POWER, `pcb_interfaces.yaml`, status DISAGREE) |
| +5V_S1, +5V_S3 | 2.5 / 5.0 | 1.06 | 6.36 | 7 / 6 / 5 | the slot rails, planes on In4 today |
| +5V_DEV | 3.8 / 6.0 | 1.89 | 11.36 | 9 / 7 / 6 | typical 3.80 A against 3.56 A of declared children, peak 6.0 against 9.72 (`boards/b.json` `_b_feeders_declared_and_the_device_rail_is_short_at_peak`) |
| +3V3_S2A, +3V3_M2C2 | 3.0 / 4.0 | 1.37 | 8.18 | 6 / 5 / 4 | the RM520N-GL socket |
| **+3V3_S1A, +3V3_S3A, +3V3_M2C1, +3V3_M2C3** | declared 0.5 / 1.5; **maker 3.0 A** | **1.37 at 3.0 A** | 8.18 | 5 / 4 / 3 at 3.0 A | PWR-F01: AsiaRF asks a 3.3 V supply of 3 A (2.5 A minimum) for the AW7915-AED; size as for 3.0 A until the declaration is corrected |
| +1V2_KSZ | declared 0.5 / 0.8; **maker 1.21 A** | 0.39 at 1.21 A | 2.34 | 2 / 2 / 2 | PWR-F03 (KSZ9897R at 1000 Mb/s) |
| +2V5_KSZ | declared 0.15 / 0.25; maker 0.33 A | 0.07 | 0.39 | 1 / 1 / 1 | PWR-F03 |
| +1V1_S1..S3 | 0.4 / 0.7; maker's four-SS row 0.778 A | 0.21 at 0.778 A | 1.27 | 2 / 1 / 1 | PWR-F05; the kit's mix uses the 395 mA row |
| +3V3_S1B..S3B | 0.9 / 1.8 | 0.26 | 1.56 | 3 / 3 / 2 | |
| +1V0_S1..S3 | 0.8 / 1.2 | 0.22 | 1.32 | 2 / 2 / 2 | |
| +3V3_DEV | 1.2 / 2.0 | 0.39 | 2.31 | 3 / 3 / 2 | |
| +5V_LIME | 1.2 / 3.0 | 0.39 | 2.31 | 5 / 4 / 3 | the SDR bay's eFuse; peak with +5V_RB is the fabric question of `_b_feeders_declared...` |
| +5V_RB | 0.15 / 2.0 | 0.02 | 0.13 | 3 / 3 / 2 | the satellite modem's transmit burst sets the barrels |
| **PANEL_5V** | 0.6 / 0.6 (board C declares 1.0 A peak) | **0.80 mm** | 0.89 | 1 / 1 / 1 | **H2:** F1 is the MF-MSMF110 (1.1 A hold) since round 8, `b76c18cb`, so the 1.23 A track clears the hold and PWR-003 reads PASS; as first written: behind F1, a 2.0 A hold, 3.5 A trip polyfuse: the copper must clear the hold (0.78 mm at 2.0 A on 1 oz outer); **0.8 mm is the recorded answer** (`boards/b.json` `_panel_5v_fuse_why`; `pcb_energy_chain.yaml` known finding B_PANEL_5V; PWR-003 FAIL on B) |
| +54V_POE | 0.3 / 0.6 | 0.06 | 0.34 | 1 / 1 / 1 | spacing governs, section 8 |
| GND | 10 / 21 | a plane | a plane | 29 / 24 / 20 per transition at 21 A | the return of the four input rails; carried by the In1 plane and outer pours |
| the rest (CM, IOC, ZB, LORA, CAM, HDMI, QMX) | under 0.3 typical | under 0.1 | | 1 to 3 | |
| **H2**, declared in the H2 intent: VBUS_FLASH1 to 3, SIM1_VCC, SIM2_VCC, SIMC2_VCC, VBAT_RTC, POE_P, MDI_A_P, MDI_A_N, and the +54V_POE returns MDI_B_P, MDI_B_N, POE_DRAIN, POE_SEN; GNSS_VDD_RF, GNSS_BIAS, GNSS_ANT | 0.30 / 0.60 at most | 0.06 at most | 0.34 at most | 1 / 1 / 1 | spacing governs the 54 V ones (section 8); `calc/rail_widths.out` board B |

## 3. Pairs: targets, geometry, budgets

Targets and intra-pair bars from `pcb_interfaces.yaml` (the host's and the module's own clauses) and decision 36:

| Interface | Nets (board b assignments) | Class | Target | Intra-pair | Length limit |
|---|---|---|---|---|---|
| PCIE_CM5 | PCIE* | USB | 90 ohm plus or minus 10 % (CM5 2.3) | 0.10 mm | none published; pair-to-pair matching unnecessary |
| PCIE_M2_MODULE | NVME*, CARD* RX/TX/CLK | USB | 85 ohm plus or minus 10 % (RM520N-GL); 90 meets both ends | 0.70 mm | 200 mm |
| USB3_CM5 | HOST*, BANK*, MUX*, LIME_SS* | USB | 90 ohm plus or minus 10 % | 0.10 mm | none held |
| USB2_CM5 | USB*, HUB*, LIME_D*, CAM_D*, QMX_D* | USB | 90 ohm plus or minus 10 % | 0.15 mm | none held |
| ETHERNET_CM5 | ETH*, SWP* | DIFF100 | 100 ohm plus or minus 10 % | 0.15 mm | pair-to-pair differences under 50 mm |
| HDMI_CM5 | HDMI*_D*, HDMI*_CK_* | DIFF100 | 100 ohm plus or minus 10 % | 0.15 mm | none held |

- **Geometry on the six-layer stack as built** (`calc/stack_solves.out`): outer 0.130 / 0.127 mm for 90 ohm and
  0.098 / 0.127 or 0.125 / 0.200 for 100 ohm; the class table's USB 0.127 / 0.13 and DIFF100 0.127 / 0.20 meet them on
  the outer layers (90.7 and 99.2 ohm). **In2 and In3 do not:** B21's DIFF100 on In2 reads 110.5 ohm over In4's plane
  and 140.5 where In4 is split (`STACKUP-DECISIONS.md` section 4). So on six layers as built, **controlled pairs run on
  F.Cu and B.Cu only**, which is the pre-router's own layer set (`boards/b.json` pair_layers), and the router's pairs on
  In2 and In3 are out of tolerance.
- **On the eight-layer candidate:** one width per target on every routing layer, 0.148 / 0.127 mm for 90 ohm and
  0.112 / 0.127 for 100 ohm (section 1; `STACKUP-DECISIONS.md` section 4).
- **The transformerless module links** (INT-002, `reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md` section 6, bound to 48 nets
  by digest `262e8b039e833d02`): 100 ohm differential; legs matched within 0.15 mm; pair-to-pair differences under
  50 mm; **one series 0.1 uF capacitor per conductor with nothing between the switch pin and the capacitor** (Microchip
  DS00004151A clause 6.6). The capacitors' voltage and dielectric are not in the netlist (INT-002 section 5 item 3).
- **Channel budgets: none held** (FB-FAB-7). The placement screen's lengths the layout must budget against
  (`FAILOVER-FABRIC.md` section 8.3, Manhattan between footprint origins on B21, so a routed run is longer): PCIe
  upstream 117.6 / 140.0 / 129.0 mm; switch to NVMe 53.9 / 44.5 / 57.7 and to card 81.1 / 70.7 / 88.5 mm (the RM520N's
  200 mm is met); USB home 185.2 / 117.9 / 196.6 mm; **USB failover up to 255.2 mm plus the TMUXHS4212's insertion loss
  (-1.3 dB at 5 GHz)**; **HDMI up to 396.2 mm through two TS3DV642**; LimeSDR 217.0 mm; Ethernet 92.8 / 162.8 / 232.8 mm.
  A per-link budget from a primary document is owed before the fabric's placement is frozen (FEA-003's layout-entry
  stage).
- **Reference clocks:** every clock output pair of the switch is AC coupled and source terminated on the corrected
  netlist, and the corrected slot 3 seats **18 parts beside U301** (six at its north-row pins, twelve at its east-row
  clock outputs) in a pocket that had 0.0 mm of room (FAB-08, `FAILOVER-FABRIC.md`; `B-FEASIBILITY.md` section 1).

## 4. Return paths

- Board B's signal table makes most nets strict (`boards/b.json` `signal_classes`, "most of this table is strict").
  On six layers as built, a B.Cu pair crossing between the slot rails' planes on In4 crosses a reference-plane split
  (`B-FEASIBILITY.md` section 3.2, INFERRED from the zone list): keep B.Cu pairs inside one In4 region, or carry a
  stitching capacitor at the crossing (RET-003).
- RET-004's 1.5 mm ground via applies outside the fine-pitch fans; the three CM5 receptacles' 0.4 mm rows are fans.

## 5. Decoupling (decision 42)

- **Other side allowed on board B** outside every fan box, never over a through-hole part, never for the STM32H743 in
  its LQFP or for a converter (`DECOUPLING.md` section 6), judged at in-plane distance plus 3.7 mm on the six-layer
  stack.
- **Class R:** the seven TPS62933, the AP64500 slot bucks, the AP63203 (U25) and the TPS23861's supply.
- **Generator items owed** (`DECOUPLING.md` section 8.3): G4 (the 0.1 uF at VIN on all seven TPS62933), G5 (C37 and C38
  re-declared against the TS3DV642 VCC pins), G6 (declare the STM32H743, PI7C9X2G404SL, TUSB8041, KSZ9897R, TMUXHS4212,
  TS3USB221A and CP2102N capacitors with classes; none is declared today), G7 (the STM32H743's VDDA 100 nF plus 1 uF,
  four more 0.1 uF on the TUSB8041 core, the KSZ9897R per the maker's example, the CP2102N's 4.7 uF plus 0.1 uF at
  VREGIN), G10 (U25's C4 at pin 3, C5 and C6 against the output loop; U27's C12 class L, C13 class D).
- **The PI7C9X2G404SL's requirement is TBD:** its datasheet gives none; the Diodes question is drafted, not sent
  (`records/rv-dec/dec-request-diodes-pi7c9x2g404sl.md`).
- DEC-001's PASS of 30 of 30 on B21 is 30 blanket allowances, not evidence (`DECOUPLING.md` section 9).

## 6. Placement

1. **The floor plan is the open question, not a setting** (`B-FEASIBILITY.md` sections 3.3 and 5): each slot's fabric
   sits 85 to 90 mm from its receptacle beyond the M.2 row; the three switch pockets have 0.0 mm of room; the room on the
   board is elsewhere (WIFISW 38.5 mm north, IOCA 19.0, S1_RAILB 19.0, S2_RAILB 16.0). The paper study of option A4 (each
   slot's switch, hub and muxes beside its receptacle's B half, north of the M.2 row) with A2 and A7 is owed; board B's
   rectangles were released by owner ruling 13, so this is the session's.
2. **Escape:** through vias only at the fabricator; via-in-pad (filled and capped, the default on six layers and up)
   has never been used for the fine-pitch signal escapes and needs an `escape.py` mode and a fabricator answer
   (`B-FEASIBILITY.md` option A3). Q-B-ESC-2 (section 7.9) tests the escape and placement remedy on the corrected
   netlist.
3. **Hot parts** (`POWER-THERMAL.md` 9.2): KSZ9897RTXI +28.7 K junction to air on a six-layer JESD51 board (11.3 C/W at
   2.54 W); PI7C9X2G404SL +16 to +27 K (25.5 C/W); the AP2112K supervisor LDOs U40, U50, U60 at 184 C/W: +43 K at PLAN,
   **+152 K at the STM32H743's 400 MHz maximum, past the part's 150 C absolute maximum at any inside air** (PWR-F04:
   bound the supervisor clock to 200 MHz VOS3, +63 K, or feed the LDOs from 3.3 V; board B's owner and the firmware
   contract); U27 (the KSZ's 2.5 V) +49 K. Each takes copper area and vias under its tab as its package allows.
4. **T1, the H5007NL magnetics, is rated 0 to +70 C** against the -20 to +40 C envelope (`boards/b.json`
   `_t1_magnetics_is_a_commercial_temperature_part_why`); keep it away from the hot parts above. The HX5004NL is the
   maker's extended-temperature part in the same mechanical group; pin compatibility is not claimed.
5. **INT-002's fallback made cheap (open, the board B stream's decision):** decision 29 keeps the three module links
   capacitive; its fallback is magnetics, today a respin. A DNP magnetics footprint on the three links would make it a
   population change (`CURRENT-EVIDENCE.md`; INT-002 section 5). Not decided here.
6. **U8, the secure element:** its part and land are FEA-001's layout-entry stage (the ATECC608B pass records, or the
   SLB 9673 or SE050E2HQ1 on the U8 site); nothing else on board B depends on it (`ZEROIZE.md` section 7).
7. **Case:** B is 330 x 200 mm; the stack lifts out through the frame window with 9.83 mm per side in X nominal and
   8.25 at the worst of Peli's figures (M7, MET); the setting legs keep 4.52 mm to B's corner at the worst (M21f); the
   east bundle's lane beside B's edge is M17d (OPEN) and M17x reads OPEN, FAILS AS ASSUMED at the worst (-0.38 against
   1.0) until the jumper plug is picked (`CASE-MARGINS.md` 3.2, finding 27). The monitor body over the CM5 heatsinks is
   M1, OPEN. Outline growth is bounded by those rows (`B-FEASIBILITY.md` option A6).
8. **Test access:** 88 test points; J_DBG1 to J_DBG3 (each module's console UART and I2C), J_RPIBOOT1 to J_RPIBOOT3
   with J_FLASH1 to J_FLASH3 (each module's eMMC over USB), J_ZBDBG1 and J_ZBDBG2 (the CC2652P cJTAG), and U42, U52,
   U62 (SWD pads of the three supervisors) on the committed netlist. The committed B21 board carries a through-hole SWD
   land where the netlist carries the SMD one (W7-R2-01, `ARCHITECTURE.md` line 194). Bring-up order:
   `PCB-BRING-UP.md` board B (8 inputs applied, 19 rails measured).

## 7. Protection placement (TRN-001)

| Port | Conductor | Part | Constraint |
|---|---|---|---|
| J_ETH (the internal RJ45 whose patch lead reaches the sealed wall jack) | the four MDI pairs, T1 to the jack | T1 (magnetics) | keep T1 at J_ETH; the MDI pairs have no entry in `pcb_interfaces.yaml` and no declared tolerance (decision 36's measurement found them judged by neither number), so an entry is owed before their geometry is judged |
| J_54V (PoE feed, leaves the case on the same wall jack) | +54V_POE | D2 SMBJ58A (intent clamps) | at the connector, ground return short and on the plane (decision 31's placement rule) |

The slot rails carry D101, D201, D301 SMBJ6.0A, +5V_DEV D1 SMBJ5.0A and +3V3_M2C2 D520 SMBJ5.0A (intent clamps).
TRN-001 reads FAIL on board B on the clamp symbol only (`PCB-RULE-STATUS-B.md` TRN-001 row); no decision 31 hold is on
board B.

## 8. Spacing (ISO-001)

+54V_POE (54 V): at least 0.160 mm outer coated, 0.150 mm inner, 0.500 mm where the coating is masked (the RJ45, the
M.2 and module receptacles, the test points). B21 reads PASS, closest 0.183 mm (`routed/spacing.verdict.json`).

## 9. Thermal

- The modules: three CM5 under coolers with their own fans (J_FAN1 to J_FAN3; fan picks are D-18), the TMP117 under
  the coolers reads the pocket (`gen_sch_b.py` line 1050). The inside-air bound includes failure for three loaded
  modules at +20 C on the independent bound (`POWER-THERMAL.md` 9.1 and 9.2; FEA-004), and three-module redundancy in the
  heat depends on the enclosure test.
- The AW7915-AED (0 to +70 C, 4 to 9 W own rise TBD, no heat path designed) and the LimeSDR Mini (0 to +70 C) are
  outside the envelope's cold end (PWR-F09); the RM520N-GL has up to 5.6 W of own rise TBD. Their sockets' copper and
  the airflow path are layout inputs the enclosure test decides.

## 10. Analyses that need placed or routed geometry, or hardware

| Stage | What | Needs |
|---|---|---|
| before layout (experiment) | Q-B-ESC-2 on the corrected netlist; decision 43's whole-board eight-layer route; the A4 / A2 / A7 paper study; per-link channel budgets (FB-FAB-7) | the round 8 merge; box time inside the existing allocation |
| PLACED_BOARD | SCH-002, DEC-001, GND-002, IMP-002, THM-001, PLC-001 (13 of 75 on B21), MEC-001 | a placement that seats every part (`region_room` read) |
| ROUTED_BOARD | PI-001 to PI-003 (section 2, PANEL_5V's 0.8 mm), RET-001 to RET-004, IMP-001 and PAIR-001 (section 3), RF-001 (the module radios' feeds), ISO-001, GND-001, STK-001, EMC-001, RTE, VIA, PLN | a complete route |
| FABRICATION_RELEASE | FEA-003 (routed-length extraction against each budget; the fabricator's impedance record for the chosen stack; R-HSD, the qualified high-speed review, not approved); FEA-001 (U8 on its land, Z-EXP-B maxima); FEA-002 (RF-002 on the current netlist); FEA-006 | the routed candidate; the owner's approval for R-HSD |
| PROTOTYPE | INT-003 (each module link up at 1000M full duplex with auto-negotiation, line rate, no error); IOHA A1 to A14; FB-FAB-8 (the reference clock at each socket, six downstream links at Gen 2); `TEST-PLAN.md` E3; `PCB-BRING-UP.md` board B | a built board |

## 11. Open items this sheet cannot close

- The stackup and layer use (decision 43's run; the price to the owner).
- FB-FAB-1 to FB-FAB-8 (`FAILOVER-FABRIC.md` section 10), the corrected netlist on `main` first.
- PWR-F01, F03, F04, F05 declarations (board B's owner).
- The coupling capacitors' rating and the magnetics-footprint fallback (INT-002 follow-ups).
