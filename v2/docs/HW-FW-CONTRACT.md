# MeshSat field kit V2: hardware and firmware contract

**Version 1, 27 September 2026 (MESHSAT-1357, pre-PCB layer 5).** Read against `main` at `e3aedb25`; round 8's circuit
candidates (`fnd/r8a` to `fnd/r8p`, integrated in part on `fnd/r8int1`) are named where they change a row and are never
treated as merged. Prototype design: nothing here has been built, ordered, powered or measured, and no row has been
shown on a bench. Written by the layer 5 closer; the reviews it has had are AI reviews and are labelled so. **While it
was being written `main` moved to `84e52461`, which integrates round 8 for boards A, C, D, E and P and the battery packet
(board B's round 8 is still a candidate): section 4 says which ROUND 8 rows are therefore drawn on `main`.** The rows'
facts stay cited at `e3aedb25`; the rows added after review (FW-B19, SC-HF-06, HF-F06 to F08) are read at `84e52461`. The rows of the second release attempt of layers 1 to 3 (27 September 2026: FW-C09's C1 target, FW-C13, FW-C14, FW-E10 and V-C13 for the hot stop and HOT-R1, section 8's registry ids) are read at `953f5658`.

This page is the itemised contract between the circuit and the firmware that runs on it: for each obligation, the
hardware fact it rests on (net, part, pin, reset and default state, cited by path at `e3aedb25`), what the firmware must
do, why, and how the obligation is verified. It replaces the two worktree drafts that `ARCHITECTURE.md` section 10,
`records/r4a/r4-decisions.md` and `review-packets/battery/CHARGER-STATE-SEQUENCE.md` cited without a path a reader
could open (`w5-hw-fw-contract.md` round 2 and `r4-hwfw-contract.md`); both are filed byte for byte beside it as
records (`v2/docs/records/w5/w5-hw-fw-contract.md`, `v2/docs/records/r4a/r4-hwfw-contract.md`), and where they and this
page differ, this page is current and they are history. The IDs FW-A01 to FW-A16 keep their meaning;
every other ID is new here. `ARCHITECTURE.md` section 10 stays the summary, `PANEL.md` stays the panel controller's
own page, and where the three differ this page is the itemised statement; the other two are corrected with it (27 September
2026).

## 0. How to read it

- **Evidence words.** VERIFIED: read in the netlist, the generator line or the maker's document cited. INFERRED: reasoned
  or computed from verified facts, not measured. PLAUSIBLE: a mechanism that holds on the verified topology but rests on
  a parameter no held document bounds. TBD: no source in this tree; the effect is stated.
- **Citations.** `A:U27.8` is board A's netlist (`v2/ecad/pcb-a-power-a23/out/pcb-a-power.net`, sha256/16
  `7b08510106687b3d`), reference U27, pin 8. The other netlists: B `pcb-b-compute-b19` (`669d02d07aeaae4b`), C
  `pcb-c-display-c8` (`2834f0d8c4071d56`), D `pcb-d-aprs-d9` (`f13d8b70099ab03e`), E `pcb-e1-dock-e7`
  (`d910e49c5f5f50b2`), P `pcb-p-pack-p2` (`4342c4cbe1b43dc4`). Generator lines are at `e3aedb25`.
- **Verification column.** An existing check is named by its own ID: FW-A15 items (this page, section 3.1), O-CHG-1 to 8
  (`CHARGER-STATE-SEQUENCE.md` section 6), E-01 to E-12 (`feasibility/EMCON.md` section 6), Z-EXP-A to C
  (`feasibility/ZEROIZE.md` section 5), A1 to A14 (`ARCH-PCB-B-IOHA.md` section 13), P10 to P15 (`TEST-PLAN.md` section 7; P15, the hot stop forced at room temperature, since 27 September 2026,
  as round 8's battery stream drafts it). A check this page adds is a V-nn row of section 5, for `TEST-PLAN.md`'s owner to take
  into the plan.
- **State column.** DRAWN: the hardware the row relies on is in the netlist at `e3aedb25`. ROUND 8: drawn only in a round 8
  candidate. OWED: the hardware is not drawn. FIRMWARE: nothing to draw; the obligation is firmware or provisioning.

## 1. The controllers and what each owns

| Controller | Board, part | Powered from | Reset, boot, recovery | Watchdog | Debug and programming |
|---|---|---|---|---|---|
| panel controller | C, U3 RP2040 | C's TLV75533 U5 from `PANEL_5V` = B's F1 off `+5V_DEV` (`C:U5.1`) | RUN pull-up, TP3; BOOTSEL by solder jumper JP1; USB bootloader over bank 1 | RP2040 hardware watchdog, firmware-enabled (FW-C02) | TP1 SWCLK, TP2 SWDIO, TP3 RUN |
| sensor controller | E, U10 RP2040 | E's AP63205, EN tied to CELL_F: on whenever a pack is fitted | RUN pull-up, TP12; BOOTSEL JP1 | RP2040 hardware watchdog (FW-E09) | TP10, TP11, TP12 |
| three compute modules | B, U30A/B to U32A/B CM5 | slot rails `+5V_S1..3` from A, enabled by `SLOT_EN1..3` | eMMC; `J_RPIBOOTx` jumper and `J_FLASHx` USB-C for rpiboot; PMIC_EN and PWR_BUT not connected | OS watchdog (INFERRED; the held CM5 datasheet names none) | `J_DBGx` UART0 and module I2C |
| three I/O supervisors | B, U41, U51, U61 STM32H743VIT6 | a private AP2112K 3.3 V each off `+5V_DEV`, fit-to-disable jumper `J_IOCOFF_x` | RC reset; BOOT0 10 k to GND: flash boot only | IWDG and BOR (option bytes TBD: RM0433 not held) | SMD SWD land (3V3, SWDIO, SWCLK, NRST, GND) |
| pack gauge | P, U1 BQ4050 | the cells | internal | AFE watchdog; host watchdog HWD 10 s by explicit write (BAT-F10) | P test points; SMBus from E |
| pack second level | P, U2 BQ7720700 | the cells | none | none (hardware thresholds) | TP15 |
| charger | A, U3 BQ25731 (a target, not a controller) | VBUS20 / VSYS | POR defaults (FW-A01 to A03) | its own 175 s watchdog | kit I2C 0x6B |

Other configured parts and who configures them (all by the panel controller over the kit bus unless named): the seven
PCA9555 expanders (A U27 0x21, U28 0x24; B U6 0x20, U7 0x25; C U1 0x22, U2 0x23; D U16 0x26), the six INA226 (A, 0x40 to
0x47), the TPS23861 PoE controller (B U5, 0x28), the KSZ9897R switch (B U1, 0x5F), the ATECC608B (B U8, 0x60), the
DS3231 clock (B U9, 0x68), the TMP117 (B U10, 0x49), the VEML7700 (C U_LIGHT, 0x10) and, from round 8, the ADS1115 on D
(U22, 0x48). The modules own their USB and PCIe devices (the RM520N-GL, the two AW7915-AED cards, the LimeSDR, the
RockBLOCK 9704, the two E72, the LG290P, the QMX) through the bridge software.

## 2. The heartbeat, resolved

Two records disagreed: `PANEL.md` section 3 (line 79 at `e3aedb25`) says a slot "toggles its line at 1 Hz while its
supervisor runs"; `ARCHITECTURE.md` section 10.1 says the module's GPIO16 toggles while the bridge runs. **The netlist
settles it (VERIFIED):** `HB_CM1` is `B:U30A.29`, the CM5's GPIO16 (`gen_sch_b.py:257`, pin 29 = GPIO16), with R157 10 k to
`+3V3_CM1`; the level stage Q105 (a 2N7002, gate on `+3V3_CM1`, `gen_sch_b.py:822`) joins it to `HB1`, which R158 holds
at `+3V3_DEV`. `HB1` goes to `B:J_PANEL.18` and to pin 30 of all three supervisors (U41, U51, U61). Slots 2 and 3 are the
same through Q205 and Q305. So **the source is the compute module's GPIO16, driven by the bridge software; the panel
controller (GPIO10 to 12) and the three supervisors (pins 30 to 32) only listen.** No supervisor drives a heartbeat. A dark
module leaves its line held HIGH by R158, so liveness is the 1 Hz toggle, never a level. `PANEL.md` section 3's row
for GPIO10 to 12 is corrected with this page. Rows FW-B01, FW-B11 and FW-C05.

## 3. Contract rows

### 3.1 Board A: power controller, charger, monitors and enables (FW-A01 to FW-A16)

Written by board A's author in round 4 and filed here with each fact re-read on board A's netlist at `e3aedb25`. One
citation is corrected (FW-A16: FE_PGOOD is `A:U27.20`, not U28 pin 20).

| ID | Hardware fact at `e3aedb25` | Firmware obligation | Why | Verification | State |
|---|---|---|---|---|---|
| FW-A01 | BQ25731 `A:U3` (0x6B, SDA pin 12, SCL pin 13, `gen_sch_a.py:710`); input sense R16 10 mOhm (VBUS20 to CH_ACN, `:716`) | After every charger power-on reset, write ChargeOption1 RSNS_RAC = 0b FIRST, before any input-current register; read it back at every service | the POR value 1b assumes 5 mOhm, so every input-current figure reads half the true current until written (SLUSE66A 9.3.5) | V-A01 (register read-back after POR); FW-A15 item 10 | FIRMWARE |
| FW-A02 | charge sense R17 5 mOhm (VBAT to CELL_FUSED, `gen_sch_a.py:47`); 4S strap R26 13.3 k over R27 40.2 k (75 % of VDDA, 4S window, `:771`) | ChargeCurrent at most 3.0 A (the nearest code at or below), lower as the gauge's temperature and state of charge ask, and at least board E's always-on draw above the wanted cell current (BAT-F06) | 3 cells in parallel at the 35E's 1,020 mA cycle-life charge current is 3.06 A: session item S-20 under D-06 (the owner's D-06 names "a lower charge setting for cell life" among its session items); it replaces the old 4 A design setting | V-A01; O-CHG-3 | FIRMWARE |
| FW-A03 | the BQ25731's own watchdog, 175 s (SLUSE66A 8.6, tWDI) | Keep WDTMR_ADJ enabled and service it inside 175 s; terminate a charge by ChargeCurrent 0 with the watchdog on | a crashed host then falls back to 256 mA (TI E2E 1316778), never to its last setting | FW-A15 items 1 and 2; O-CHG-2, O-CHG-3 | FIRMWARE |
| FW-A04 | the kit loads sit on VSYS (net VBAT) with the pack beyond R17 (`gen_sch_a.py:18-48`) | Set the IDCHG and PROCHOT thresholds against the pack protection (20 A for 2 s, `pcb_pack_protection.yaml`), not against charge | since S-04 the IBAT reading sees the whole kit load through R17 | V-A02 | FIRMWARE |
| FW-A05 | the outlet interlock `A:U30` NAND: OUTLET_OK = NOT (TR_APRS AND PA_EN) into U26 gates 3 and 4 (`gen_sch_a.py:1104`) | Keep the key-down rules K1 to K5 and the in-key guard C4, thresholds set by the session under D-11 (`feasibility/POWER-THERMAL.md` 7.2, PROVISIONAL; 9.3; S-14), with the panel and the bridge: at most 60 s per key-down, 2 s apart; gates at +55 C cells, +50 C air, +75 C flange; the outlets and the heater off while keyed; SoC floors 15.5 V and 12.4 V rest; unkey above 18 A, a cell under 2.70 V or the flange at +85 C | owner ruling D-11 rules that every radio may transmit at once for a declared key-down time above a declared state of charge; the thresholds are set by the session under D-11 ("The session sets both thresholds"; `POWER-THERMAL.md` 7.2, PROVISIONAL), as is the outlet interlock, which drops the outlets only while the PA keys | V-C09; P13 | FIRMWARE (thresholds PROVISIONAL) |
| FW-A06 | `A:U27.8` IO0_4 = POE_SW_EN (R114 pull-down); `A:U28.13` IO1_0 = PD_SW_EN (R143); POE_EN and PD_EN = the software bit AND OUTLET_OK (`A:U26.8-13`) | These bits are the software holds; a PoE or USB-C drop while the PA keys is expected, not a fault | S-14 | V-A03 | DRAWN |
| FW-A07 | `A:U28.4` IO0_0 = USBX_EN into eFuse U32 (0.89 A), held off by R190 4.7 k; `A:U28.5` IO0_1 = USBX_FLT, open drain, R187 10 k to +3V3, active low | Turn the Glenair port's VBUS on when the port is in use, for its uses under D-12 (the wall USB data port, and the console and key-fill port); report USBX_FLT | owner ruling D-12 (the port and its uses); VBUS off at power-up is board A's R190 | V-A03 | DRAWN |
| FW-A08 | six PCA9555 with output registers FFh at power-on (TI SCPS131J): `A:U27`, `A:U28`, `B:U6`, and C's U1, U2 and D's U16 | Write the OUTPUT registers before the CONFIGURATION registers on every boot; never write DEV_EN (`A:U27.11`, R42 100 k to +3V3, ON at power-up) = 0 except as the last act of a shutdown | configuring first drives every output high for a moment (W2 F-SQ-07); DEV_EN removes the panel's own supply | V-C01; O-CHG-8 | DRAWN |
| FW-A09 | six INA226 on the kit bus: U8 0x40 (+5V_S1, R31 5 mOhm), U9 0x41 (+5V_S2, R35 6 mOhm), U10 0x44 (+5V_S3, R39 5 mOhm), U11 0x45 (+5V_DEV, R43 6 mOhm), U14 0x46 (+13V8_PA, R55 6 mOhm), U17 0x47 (+54V_POE, R71 20 mOhm); alerts wired-OR on INA_ALERT (`A:U27.19`) | Calibrate each for its own shunt (full scale 81.92 mV over the shunt: 16.38 A, 13.65 A, 16.38 A, 13.65 A, 13.65 A, 4.10 A); set the alert limits from the stage limits | R35, R43 and R55 are the LM5176 ISNS shunts since round 4 | V-A04 | DRAWN; **U17's inputs sit at 54 V, over the INA226's 40 V absolute maximum: finding HF-F02** |
| FW-A10 | PI_SHDN_REQ: LTC2954 INT (`A:U1.5`) open drain with R3 10 k to +3V3 (`gen_sch_a.py:261`); panel GPIO18 (`C:U3.29`); each module's GPIO6 through Q{s}02 | ACTIVE LOW everywhere. The panel never drives it high: output value 0, toggle the output enable; it reads the pin as an input to see MAIN taps (INT low for at least 32 ms) | two drivers of opposite sense would fight on an open-drain net (W5-F6); INT has no current rating to hold against a high drive | V-C03 | DRAWN |
| FW-A11 | PI_KILL: panel GPIO19 (`C:U3.30`) to `A:Q1` gate (2N7002), which pulls KILL (`A:U1.8`) low; R5 1 k to GND (`gen_sch_a.py:263`) | Push-pull output driven LOW before the first SLOT_EN goes high, never tri-stated or made an input while a slot is powered; drive high to kill (3.3 mA into R5) | a powered slot can lift PI_KILL through its level stage's body diode (W5-F5); R5 at 1 k holds it under Q1's threshold only while nothing else acts | V-C03; V-C04 | DRAWN |
| FW-A12 | MAIN: LTC2954ITS8-1 (`A:U1`, -40 to 85 C), PDT capacitor C152 680 nF (`gen_sch_a.py:262`) | An ordinary press raises INT only: the panel requests module shutdown, waits for the heartbeats to stop, then asserts PI_KILL. Holding MAIN about 4.4 s (3.3 to 6.0 s) forces the kit off with no shutdown; PANEL.md states the hold time | W5-F2 corrected | V-C03 | DRAWN |
| FW-A13 | heater: eFuse `A:U22` (ILM 1.0 A, EN = HEAT_EN `A:U27.6`, R112 pull-down) into buck U33 TPS62933 at 12.0 V to `A:J_HEAT` | No duty limit for the mat's rating (the buck regulates 12.0 V, 7.5 W); the thermal policy (warm before charge below -10 C at the cell) and K4 (heater off while the PA keys) stay firmware | F-PR-06; K4, set by the session under D-11 (`POWER-THERMAL.md` 7.2, PROVISIONAL) | V-C09 | DRAWN |
| FW-A14 | CHG_INHIBIT `A:U27.4` IO0_0, R21 4.7 k to GND, drives Q6 | Held low (charger enabled) at power-up; asserted only by firmware | S-08 | O-CHG-8 | DRAWN |
| FW-A15 | the bench readings owed before any FW-A row is trusted | (1) ChargeCurrent and the SRP-SRN current at POR and after 175 s with no host; (2) ChargeCurrent after an adapter removal; (3) the MAIN force-off time with C152; (4) PI_KILL's level with three slots powered and the panel in reset; (5) each LM5176 stage at no load and full load; (6) the BAT46W bootstrap recharge peaks; (7) each LM5176 loop by injection at its buck and boost ends and its load step; (8) the USB-C outlet's profile changes 15 to 5 V and 9 to 5 V; (9) the VBUS20 bulk capacitors' temperature rise and share; (10) the front end's start-up from the vehicle entry alone at 9, 12 and 24 V, the restart into a charged VBUS20 and the VINDPM read back; (11) a charger load release at IIN_DPM | every row above is a paper design | the list itself (full text: `records/r4a/r4-hwfw-contract.md`, filed with this page) | OWED (bench) |
| FW-A16 | BQ25731 IIN_HOST (REG 0x0F/0E) and InputVoltage (REG 0x0B/0A); board E's VIN_MON = 0.0909 x VIN_RAW (`E:R40` 100 k over R41 10 k, `E:U10.39` GPIO27 ADC1, `gen_sch_e.py:569`), reported over USB; FE_PGOOD on `A:U27.20` IO1_7 (R13 100 k to +3V3) | (a) Hold the charger's input at or under 80 % of board E's guaranteed vehicle entry at the present VIN_RAW: IIN_HOST at or below 0.80 x 4.80 A x 0.93 x VIN_RAW / 20.7 V (1.55 A at 9 V, 2.07 A at 12 V, 4.14 A at 24 V); the 9 V figure while VIN_RAW is unknown. (b) With no adapter present, write IIN_HOST to the 9 V figure (the charger resets it to 3.25 A at every adapter removal, SLUSE66A 9.3.6). (c) Once FE_PGOOD is high, write VINDPM to about 18.5 V. (d) FW-A01 first. With only the panel's tracker feeding, the rule caps charge at about 54 W against the tracker's 93 W, a recorded reduction (O-33) | board E's LM5069 limits the vehicle entry at 4.85 to 6.15 A; a limiting constant-power front end collapses the bus | FW-A15 item 10 | FIRMWARE; ROUND 8: board E declares VIN_RAW at 14.10 A (R8E-N01, `fnd/r8int1` bc0f562f): the 80 % figure is unchanged, the dock contacts are not (IF-AE-DOCK) |

### 3.2 Panel controller, board C (FW-C01 to FW-C14)

| ID | Hardware fact at `e3aedb25` | Firmware obligation | Why | Verification | State |
|---|---|---|---|---|---|
| FW-C01 | boot order: GPIO19 PI_KILL, GPIO18 PI_SHDN_REQ, GPIO22 ZEROIZE_SW (`C:U3.34`, R10 10 k up, readable at the first instruction, `gen_sch_c.py:110-123`), the expanders, the charger, GPIO13 to 15 SLOT_EN (`C:U3.16-18`) | 1. PI_KILL low; 2. PI_SHDN_REQ released; 3. read ZEROIZE_SW and the wipe-pending record, complete any pending wipe; 4. every expander's outputs before its configuration (FW-A08); 5. the charger (FW-A01 to A03, A16); 6. SLOT_EN1..3 one at a time. Never the RP2040-E5 USB fix; a BOOTSEL activity mask of 0 or GPIO25 only | D-03 (slots power only after ZEROIZE is read); W5-F1, W5-F5, W5-F6 | V-C01 | DRAWN |
| FW-C02 | RP2040 watchdog; SLOT_EN held low by A's R30, R34, R38 (100 k) and the pad pull-downs | Hardware watchdog on, with PADS_BANK0, IO_BANK0 and SIO excluded from its reset scope (PSM and RESETS WDSEL), boot reason logged; update by SWD or in-application, never through the ROM bootloader while slots run | a pad reset drops every slot (W5-F4); the SLOT_EN hold across a panel reset is not drawn | V-C02 | FIRMWARE; the hold (ARCHITECTURE.md 4.3) OWED |
| FW-C03 | MAIN tap on PI_SHDN_REQ (FW-A10); PI_KILL (FW-A11) | Shutdown: on a MAIN tap or the PI button (`C:J_PIJ2`, short press) raise the request by pulling PI_SHDN_REQ low at least 200 ms, wait for HB1..3 to stop toggling, then PI_KILL high; the PI button held 8 s is PI_KILL | W5-F2, W5-F6 | V-C03 | DRAWN |
| FW-C04 | ZEROIZE_SW only on GPIO22; U12 copies it to ZEROIZE_HW for test points, nothing acts on ZEROIZE_HW; the ATECC608B `B:U8` at 0x60 on the kit bus | Level-sensitive: closed 5 s = the crypto-erase of `feasibility/ZEROIZE.md` section 3.4 (both KEKs by GenKey mode 0x04, verify, tell the running modules to drop RAM keys, then drop SLOT_EN1..3; the RP2040 timer alarm armed at step 0 cuts the slots at 3.0 s); a wipe-pending record in flash resumes an interrupted wipe; re-arm only when the toggle returns; the tamper reed never wipes | owner ruling D-03 (decision 30): the trigger, the order, the level sensitivity and the reed's logging only; the steps and timings are `feasibility/ZEROIZE.md` 3.4's design | Z-EXP-A, Z-EXP-B, Z-EXP-C | FIRMWARE (Z-EXP bench owed) |
| FW-C05 | HB1..3 on GPIO10 to 12 (`C:U3.13-15`), no pull on C, held high on B by R158, R258, R358 | Inputs only, no pad pulls; a slot is alive while its line toggles at 1 Hz; declare it lost after 3 s without an edge; the display owner is re-elected from the live slots | section 2 | V-C05 | DRAWN |
| FW-C06 | HDMI_SEL1, HDMI_SEL2 on GPIO16, 17 (`C:U3.27-28`); B's R15, R16 100 k pull-downs (`gen_sch_b.py:903`) | Follow the bridge's display owner; with no instruction select the lowest slot with a live heartbeat; never select a dark slot | FAB-04; ROUND 8 (`fnd/r8b`): R15, R16 10 k and the display switches enabled only while the selected slot is powered (U519, U520) | A12 | DRAWN; ROUND 8 changes the pulls |
| FW-C07 | EMCON: GPIO21 reads EMCON_HW (`C:U3.32`); TX_INHIBIT_n and EMCON_HW are driven only by the toggle and U9 | GPIO21 is an input, never an output; on every EMCON edge assert the software holds as well (queue every send, AT+CFUN on the 5G module where the bridge can, rfkill on the module and card radios); an EMCON release never re-enables a radio the operator had off; show EMCON on the e-paper | D-05; NEED-08 | E-01 to E-12 | DRAWN; ROUND 8 (`fnd/r8c`): GPIO21 reads EMCON_RD_R behind U13 and R46 1 k, so a misconfigured pin cannot reach the line |
| FW-C08 | SHORE_INHIBIT on GPIO20 (`C:U3.31`); A R118 and E R26 100 k pull-downs; E's Q8 pulls the hot-swap UVLO low when it is high | Boot low; assert on the bridge's request when the pack reads below 0 C and clear above 3 C, or when the operator sets "no charge" | `PANEL.md` section 10; THERMAL-COORDINATION L3 | V-C08 | DRAWN |
| FW-C09 | the power controls C1 to C4 and K1 to K5 act through `A:U27` (POE_SW_EN, HEAT_EN, PA_SW_EN), `A:U28` (PD_SW_EN), SLOT_EN and the gauge's readings from the sensor controller | Keep C1 (at +50 C inside air or +55 C on any cell, shed to the reduced mode of slots 2 and 3; reached again there, to the heat stage's one module, slot 3 after BANK-R1 and slot 2 as board B is generated; restore 5 K below; `CONOPS.md` section 4c, corrected 27 September 2026), C2 (outlets shed at 9.0 A for 10 s or +50 C cell, USB-C first), C3 (current trigger for C1), C4 and K1 to K5 (FW-A05); hold C2 and C3 while PA_EN and 10 s after; ROUND 8 fallback: when the sensor controller's pack readings stop for 10 s, shed to the reduced mode with both outlets off; past the heat stage, the hot stop is FW-C13 and FW-C14 | `POWER-THERMAL.md` 7.2, 9.3; `THERMAL-COORDINATION.md` section 7 (round 8); `CONOPS.md` section 4c (C1's target) | V-C09 | FIRMWARE (PROVISIONAL thresholds) |
| FW-C10 | SOS_SW on GPIO28 (`C:U3.40`), maintained toggle | Closed 2 s = SOS: the bridge sends the distress message over the bearers that are up, Iridium first when nothing else is; under EMCON it queues and tells the operator | owner ruling D-10 (what SOS sends, over which bearers, and that it never transmits through EMCON); the 2 s hold is `PANEL.md`'s | V-C10 | FIRMWARE |
| FW-C11 | the panel's 3.3 V feeds C's two PCA9555 and the VEML7700 on the kit bus; C's USBLC6-2SC6 U7 has its VBUS pin on C's +3V3 (`C:U7.5`) | Never switch the panel's 3.3 V with the ribbon attached | an unpowered PCA9555 or the ESD array's diodes clamp the bus | V-K02 | DRAWN |
| FW-C12 | the panel's USB device on bank 1 (`USB_PNL`, `B:J_PANEL.15-16`) | The bridge protocol: indicator states, lighting, sounder, e-paper page, display select, shutdown and kill, charge inhibit; reports every switch and hardware line, heartbeats, firmware version and build hash, last reset reason. The wire format is **MESHSAT-837, outside this repository** (handover gap, section 9) | `PANEL.md` section 11 | V-C12 | FIRMWARE (format not in the tree) |
| FW-C13 | the hot stop's actor (read at `953f5658`; `CONOPS.md` section 4c): `SLOT_EN1..3` on GPIO13 to 15, `PI_SHDN_REQ` on GPIO18 and `PI_KILL` on GPIO19 (`C:U3`; `PI_KILL` through `J_AB1` pin 10 to `A:Q1` and the LTC2954's `KILL`, `gen_sch_a.py` lines 269 and 273); the switched loads' software enables on `A:U27` (0x21) and `A:U28` (0x24); the charger at 0x6B, ChargeOption0 bit 0 `CHRG_INHIBIT` (TI SLUSE66A 9.4.1 and 9.6.1) | H1, on HOT-R1 at 5 Hz (FW-C14) or, with the line held high, board B's TMP117 at +55.0 C in two readings in a row: ask every running module for a clean shutdown on `PI_SHDN_REQ` and drop `SLOT_EN1..3` once each has stopped or 60 s have passed; turn off the monitor, the pack heater, board D, PoE, the USB-C outlet, the wall port's VBUS and the PA and HF software holds through `A:U27` and `A:U28`; set `CHRG_INHIBIT`, never board A's `CHG_INHIBIT` line (it puts the charger in HIZ, whose converter stops, and moves the kit's load onto the pack, `gen_sch_a.py` line 782); keep `+3V3_DEV`, which feeds this controller; MASTER WARN flashing and the e-paper "HOT STOP: COOLING" with the hottest reading. Leave H1 only when the line is back at 1 Hz (or the TMP117 reads +45.0 C or less) and 30 minutes have passed since the stop, then raise the heat stage's one module. H2, on the line held low or, with it held high, the TMP117 at +56.0 C in two readings in a row with H1 acting: write the e-paper "HOT SHUTDOWN: RESTART WITH MAIN WHEN COOL", then drive `PI_KILL` high as FW-C03 does | REQ-077; SC-49; `CONOPS.md` section 4c | P15 and E3-H (`TEST-PLAN.md`); V-C13 | FIRMWARE; its line DRAWN (HOT-R1, SC-70) |
| FW-C14 | HOT-R1 at the panel controller (read at `953f5658`): board A's `DOCK_SPARE` (`A:J_DOCK` pin 12, `gen_sch_a.py` line 226) lands on `A:U27` pin 18, whose change raises `EXP_INT` (`A:U27` pin 1 with `R110`, line 1267), this controller's interrupt (`J_AB1` pin 13, `B:J_PANEL` pin 6, GPIO24); the line's pull-up is `A:R216` (10 k to +3V3, U27's own VCC) and its driver board E's open drain `E:Q11` (FW-E10), drawn by stream w4ae (SC-70) | Decode the line's four states from `A:U27`'s input at each `EXP_INT`: toggling at 1 Hz, the cells read and below H1; at 5 Hz, H1; held low, H2 (a line shorted to ground included); held high, the sensor controller lost (unpowered, in reset, hung or the contact open); a line is held when no edge comes for 3 s, the rule FW-C05 applies to a heartbeat. Read it at every start-up before any slot is raised, as `ZEROIZE_SW` is read (FW-C01): held low, write the H2 page and drive `PI_KILL` again; at 5 Hz, raise no slot until it is back at 1 Hz; held high, start under the TMP117's two steps. With the line held high apply FW-C13's steps to board B's TMP117 (`B:U10`, 0x49 on the kit bus) at +55.0 C and +56.0 C, released at +45.0 C, together with `THERMAL-COORDINATION.md` section 7's fallback (the reduced mode, the outlets off). Service every `EXP_INT` by reading `A:U27`'s input port 1, which clears the interrupt that port raised (TI SCPS131J 8.4.1), then write a command byte other than 00h (the errata of 8.4.1.1): `EXP_INT` is wired-OR across boards A, B and C, and a toggling line asserts it twice a second (ten times in H1), so an unserviced U27 would hold it low for every other source; poll the port at least once a second as well, because a held line makes no edge | REQ-077; SC-50; SC-70; `CONOPS.md` section 4c | P15; V-C13 | DRAWN (SC-70) |

### 3.3 Board B: modules, supervisors and board B's devices (FW-B01 to FW-B19)

| ID | Hardware fact at `e3aedb25` | Firmware obligation | Why | Verification | State |
|---|---|---|---|---|---|
| FW-B01 | module GPIO16 (`B:U30A.29`, U31A, U32A) through Q{s}05 to HB{s} | Toggle at 1 Hz only while the bridge runs; stop when it stops; never a steady level | section 2 | V-C05 | DRAWN |
| FW-B02 | module GPIO6 (`B:U30A.30`) on PI_SHDN_REQ_CM{s} through Q{s}02, R{s}54 10 k to the module's 3.3 V | Input only; LOW is the shutdown request; shut down cleanly and stop the heartbeat | W5-F6 | V-C03 | DRAWN |
| FW-B03 | module GPIO17 (`B:U30A.50`) on PI_KILL_CM{s} through Q{s}03 | Input only, never driven | the stage's body diode already lifts PI_KILL (W5-F5); a driven pin would lift it further | V-C04 | DRAWN |
| FW-B04 | module GPIO22 (`B:U30A.46`) on GNSS_PPS_CM{s} through Q{s}04 | Input only (the LG290P's time pulse) | NEED-11 | V-B04 | DRAWN |
| FW-B05 | module Ethernet pairs to KSZ9897R ports 1 to 3 through 100 nF, no magnetics | Never force link speed on ports 1 to 3; auto-negotiation stays on | decision 29; INT-002 | INT-003 | DRAWN |
| FW-B06 | module WL_nDisable and BT_nDisable pulled low by open drains from EMCON_ON and U6's off requests (`B:U6.13-18`) | rfkill on EMCON as the software half; the U6 bits are requests (write 1 = off) | D-05 | E-08 | DRAWN; ROUND 8 (`fnd/r8b` L3): EMCON_ON made per slot from the module's own 3.3 V |
| FW-B07 | EEPROM_nWP floats on every module | The secure-boot posture of the modules is decided once Raspberry Pi's secure-boot document is read (not held); until then the bootloader EEPROM is writable by software | D-13, S-40 | V-B07 | OWED (decision) |
| FW-B08 | supervisors' I2C1: SCL PB6 pin 92, SDA PB7 pin 93 on the kit bus (`gen_sch_b.py:1136-1140`), FT_f pins | I2C1 target only, at **0x34 (U41), 0x35 (U51), 0x36 (U61)**; never a master, never drive SCL, never drive SDA except to acknowledge or answer as an addressed target, never answer or address 0x60 or 0x30 to 0x32; internal pull-ups off (PUPDR 00); answer from a prepared buffer, stretching SCL at most 1 ms | Z-C3 (`feasibility/ZEROIZE.md`); I3-F01 (0x30 is the TPS23861's broadcast address) | V-B08 | FIRMWARE |
| FW-B09 | two CAN fabrics per supervisor on TCAN334D (1 Mbps parts) | CAN FD at 1 Mbps or less; quorum 2 of 3; a supervisor without quorum does not act | FAB-05; IOHA FMEA row 8 | A4 to A7 | DRAWN |
| FW-B10 | IWDG and BOR; BOOT0 10 k to GND; SWD land | IWDG started by option byte, BOR level set (both TBD: RM0433 not held); software-verified boot (D-13 floor); images only over SWD | D-13 | V-B10 | FIRMWARE (S-40, S-41) |
| FW-B11 | HB1..3 on pins 30 to 32; EMCON_HW on pin 33 (PC5) | Inputs only | a driven pin on EMCON_HW would defeat the line | E-11 | DRAWN; ROUND 8 (`fnd/r8b` L1): pin 33 reads EMCON_SUP through U506 |
| FW-B12 | voted outputs SEL, HUBRST, WSEC per supervisor into the 2-of-3 voters, 21 pull-downs R480 to R500 (100 k at main) | Change a voted bit no faster than once per 1 ms and only with quorum; the break-before-make is hardware | FAB-03, FAB-04; the delays are 40.8 to 192 us per stage in round 8 (INFERRED) | A10 | DRAWN; ROUND 8: 10 k pulls, cascade BBM (`fnd/r8b`) |
| FW-B13 | U6 0x20 outputs KSZ_RST, LIME_SW_EN, RB_SW_EN, LORA_ON, ZB_ON, CAM_EN, 5G_OFF, 5G_RESET, six radio off requests, RB_SW_IEN (the RockBLOCK's ENABLE request since stream w4b; U536 ANDs it with EMCON_HW into RB_IEN), RB_CTRL; U7 0x25 inputs and eleven spares (`gen_sch_b.py:1036`, `:1040`) | Outputs before configuration (FW-A08); the panel raises RB_SW_IEN only after +5V_RB is up, writes it low on EMCON, and after a release raises it again only once RB_STATUS reads low (Ground Control's I_EN/I_BTD order; `PANEL.md` correction (17)); U7's spares stay inputs until SC-HF-02's segment enable is drawn (then IO1_7 drives it, default isolated) | W5-F1 | V-C01 | DRAWN |
| FW-B14 | TPS23861 `B:U5` at 0x28 (A3 open), broadcast 0x30 (SLUSBX9I 7.3.13); PoE rail from A (POE_EN = POE_SW_EN AND OUTLET_OK) | The panel configures the port (802.3at, class 4 at most, the rail's 0.6 A), never writes 0x30 except for address programming, and waits at least 100 ms between writes to 0x30 and 0x31 during a scan | NEED-05; I3-F01 | V-B14 | DRAWN |
| FW-B15 | KSZ9897R `B:U1` management at 0x5F, a slave only, strapped for I2C | Optional management by the panel; the switch works unmanaged from its straps | DS00002330E 4.9.2 | V-B14 | DRAWN |
| FW-B16 | ATECC608B-SSHDA-T `B:U8` at 0x60 (factory address TBD until Z-EXP-A A0) | Provision the slot map of `feasibility/ZEROIZE.md` 3.1 (Z-C1 to Z-C3); wake at 100 kHz; only the panel commands it | decision 30 | Z-EXP-A | FIRMWARE |
| FW-B17 | DS3231 `B:U9` 0x68 on the CR2032 (BT1); TMP117 `B:U10` 0x49 | Set time from GNSS, hold it on loss; read the cooler-area temperature for C1 | NEED-11 | V-B17 | DRAWN; ROUND 8: U9 becomes DS3231SN# on its own SO-16 land |
| FW-B18 | RM520N-GL on `B:J_M2C2`: 5G_OFF (FULL_CARD_POWER_OFF# via Q207) and 5G_RESET from U6; W_DISABLE1# pulled low by EMCON | Airplane mode (AT+CFUN) as care before an operator-requested power-down; on EMCON the hardware acts first | D-05, SD-EMC-1 | E-05, E-12 | DRAWN; ROUND 8 (`fnd/r8b` SD-EMC-1): the socket rail is removed by hardware on EMCON, Tpr held by U221 (180 to 420 ms) on release; the bridge waits for re-enumeration and never forces it |
| FW-B19 | the monitor's touch USB on board D's spare hub port `D:J_USB3` (PH 1x4: +5V_D8, USB3_N, USB3_P, GND; TUSB2046I U4 port 3, full speed), which reaches board B's bank 3 hub port 1 as `USB_D8` (SC-HF-06; `pcb_interfaces.yaml` IF-MON; D netlist `0dad82b4b6a79290` at `84e52461`, the same port at `e3aedb25`) | The HAL on the module that owns bank 3 shares the touch HID device over the kit network to the display owner, and moves the share when either changes, so touch always reaches the module whose HDMI the panel has selected (FW-C06); the display owner's UI takes touch only from that share; under Blackout the UI ignores touch (`CONOPS.md` Blackout row) | appendix 32.52 line 2837: "The HAL shares USB and serial devices to the other modules over the network ... so every module sees every device"; SC-HF-06 | V-B19 | DRAWN (the port; the lead is made up at build); FIRMWARE (the share) |

### 3.4 Board D (FW-D01 to FW-D03)

| ID | Hardware fact at `e3aedb25` | Firmware obligation | Why | Verification | State |
|---|---|---|---|---|---|
| FW-D01 | PCA9555 `D:U16` 0x26 (A2, A1 to +3V3, `gen_sch_d.py:684`): inputs X_COS_n, X_PTT_HS1_n, X_PTT_HS2_n, X_KEY, X_PA_KEY; outputs X_SA_PD, X_AMP_EN, X_MMUTE; eight spares | Outputs before configuration; the PTT and KEY states are read-backs only (the KEY gate is hardware) | W5-F1 | V-C01 | DRAWN |
| FW-D02 | ROUND 8 (`fnd/r8int1` 76235aad): ADS1115 `D:U22` at 0x48 reads the PA flange NTC on `D:J_FLANGE` | Read the flange at 1 s during every key-down; K2 gate at +75 C, C4 cut at +85 C; a missing reading counts as too hot | PWR-F15; POWER-THERMAL 7.2 | V-C09 | ROUND 8 |
| FW-D03 | the SA868 exciter on D, programmed over its UART | The band lock of owner ruling D-04: the exciter is programmed only inside the operator's licence and the EU limits | D-04 (owed) | V-D03 | FIRMWARE (OWED) |

### 3.5 Sensor controller, board E (FW-E01 to FW-E10)

| ID | Hardware fact at `e3aedb25` | Firmware obligation | Why | Verification | State |
|---|---|---|---|---|---|
| FW-E01 | gauge SMBus on GPIO2 SMBD, GPIO3 SMBC (`E:U10.4-5`), the RP2040's I2C1 block; `E:J_SMB` JST-XH 1x4 in board P's order | Open I2C1 on GPIO2/3 at 100 kHz (SMBUS_GAUGE); poll the gauge well inside its 10 s host watchdog (BAT-F10: HWD 10 s by explicit write); report state of charge, cell voltages, the four cell temperatures and the pack current over USB at 1 s during a key-down (C4) | the gauge's host watchdog stops charging when its host is silent | O-CHG-7 | DRAWN |
| FW-E02 | PRES: `E:U10.28` GPIO17 behind R54 1 k, R55 1 M to +3V3_E6 (`gen_sch_e.py:523`); board P holds PRES low with R14 10 k | Turn GPIO17's pad pull-down OFF before reading PRES; low = the lead is in | a pad pull-down reads an absent lead as present (round 4 open item 10) | V-E02 | DRAWN |
| FW-E03 | SHORE_INHIBIT read-back on GPIO15 (`E:U10.18`), R26 100 k to GND | Input only | an output would fight the panel's line | V-C08 | DRAWN |
| FW-E04 | VIN_MON on GPIO27 ADC1 (0.0909 x VIN_RAW), CELL_MON on GPIO28 ADC2 (0.180 x the pack, R42 100 k over R43 22 k) | Report both over USB at 1 s for FW-A16 | FW-A16 | FW-A15 item 10 | DRAWN |
| FW-E05 | lid and tamper reed on `E:J_TAMP` to GPIO16 through R53 10 k, R52 100 k to +3V3_E6 (`gen_sch_e.py:542`); normally open, closed by the lid magnet | Log every change with a time, kit on or off; never trigger ZEROIZE; report the lid state for the reduced mode | owner ruling D-03 ("the tamper and lid switch logs only"); REQ-036 | V-E05 | DRAWN |
| FW-E06 | water electrodes PAD_W1, PAD_W2 on GPIO26 ADC0 (WATER_SENSE, R39) | Report water on the floor; the hazard action (pack shutdown over SMBus) per NEED-12 | NEED-12 | E6 (immersion) | DRAWN |
| FW-E07 | mixer fans on `E:J_FAN1`, `J_FAN2` (CELL_F, low-side switch, tachometer): PWM GPIO8, 9; tach GPIO10, 11 | Run the mixers with the lid closed and on C1's triggers; report a stopped fan | ruling of 7 Sep 2026 (no vent) | V-E07 | DRAWN |
| FW-E08 | Geiger supply U16 TPS22810 enabled by GEIGER_EN on GPIO18; DCF77 on GPIO6; AS3935 IRQ on GPIO14; the sensor bus SDA1/SCL1 on GPIO4/5 | Keep the Geiger off the always-on path except when measuring; the sensor bus is this controller's own and never the kit bus | standby drain (ARCHITECTURE.md section 11) | V-E08 | DRAWN |
| FW-E09 | always on while a pack is fitted | Hardware watchdog on; for storage command the gauge's SHUTDOWN over SMBus | standby drain | V-E08 | FIRMWARE |
| FW-E10 | HOT-R1 at the sensor controller (read at `953f5658`): `E:U10` GPIO19 (pin 30) drives `HOT_R1_G`, the gate of `E:Q11` (2N7002, `R58` 100 k to GND), whose open drain pulls board E's contact `BLK_SPARE` (`J_BLK` pin 12, `TP7`) low; drawn by stream w4ae (SC-70) | Read the four cell thermistors in the gauge's `DAStatus2()` (TS1 to TS4, `ManufacturerAccess()` 0x0072, TI SLUUAQ3A 13.1.48) once a second (FW-E01's poll) and drive the line: toggled at 1 Hz, each edge after a fresh reading of all four, while the hottest is below +56.5 C; at 5 Hz from the second reading in a row at or above +56.5 C until the hottest reads +46.5 C or less; held low (the 2N7002 on) from the second reading in a row at or above +57.0 C for as long as it stays there, then 5 Hz; release the line (held high by the pull-up: the lost-controller state) after 3 s without a good gauge reading, and never hold it low on a fault: the RP2040 watchdog's reset leaves GPIO19 an input, and the gate pull-down keeps the line high; run the mixer fans at full speed in H1 and H2; keep the watchdog's period plus the longest interval between an edge of the line and the next watchdog kick under FW-C14's 3 s (for example a period of at most 1.5 s with the kick in the reading loop; the timeout runs from the last kick while the held-line clock runs from the last edge), so a controller that hangs with GPIO19 high is reset, and its pads released, before the panel controller reads the line as held low | REQ-077; SC-49, SC-50, SC-70; `CONOPS.md` section 4c | P15; V-C13 | DRAWN (SC-70) |

### 3.6 Pack, board P (FW-P01 to FW-P03)

| ID | Hardware fact at `e3aedb25` | Firmware obligation | Why | Verification | State |
|---|---|---|---|---|---|
| FW-P01 | BQ4050 `P:U1`, data flash per `review-packets/battery/PRIMARY-CONFIGURATION.md` | Every word of the golden image written explicitly and read back after a reset at commissioning: FET control on, OTFET, CHGIN, CHGSU, CHGFET, 4 cells, four cell thermistors, COV 4250 mV, OCC 5000 mA, the charge window of `THERMAL-COORDINATION.md` (round 8: UTC 1.0 C, OTC 44.0 C, T1 1 C, T3 42 C, T4 43 C), HWDF = 1 with HWD Delay 10 s, SUV permanent fail at 1.0 V | BAT-F05, BAT-F10, BAT-F13, BAT-F14 | O-CHG-1; P10 to P14 | FIRMWARE (image) |
| FW-P02 | the same | SEALED in the field; lifetime data and PF flags read by the sensor controller | decision 40 open | O-CHG-1 | FIRMWARE |
| FW-P03 | fuse arming jumper `P:JP1` (FUSE_G to FUSE_GQ), open as built | Closed at commissioning after the image is verified | the FUSE output drives F2 | P-checklist (ASSEMBLY.md section 8) | DRAWN |

### 3.7 The kit I2C bus (FW-K01 to FW-K05)

| ID | Hardware fact at `e3aedb25` | Firmware obligation | Why | Verification | State |
|---|---|---|---|---|---|
| FW-K01 | master: `C:U3` I2C0 on GPIO0 SDA, GPIO1 SCL (`C:U3.2-3`); 36 pins on SDA and 35 on SCL across A, B, C, D (section 6) | **Standard-mode, 100 kHz nominal**; the achieved clock is lower by the rise time and the controller's clock synchronisation (INFERRED about 93 kHz); `feasibility/ZEROIZE.md`'s budget re-run at 90 kHz passes every line (section 6.4). Never Fast-mode on the current copper | the ZEROIZE budget assumed 100 kHz and no record declared the clock | V-K01 | FIRMWARE |
| FW-K02 | pull-ups: B R54, R55 2.2 k to +3V3_DEV (`gen_sch_b.py:1044`), C R7, R8 2.2 k to +3V3 (`gen_sch_c.py:137`); the KSZ9897R's internal 58 k +-30 % | No internal pull-up on any participant (RP2040 GPIO0/1 pads, STM32 PB6/PB7); the panel's GPIO0/1 at the default 4 mA drive and slow slew, so the fall time sits between the specification's floor and the ATECC608B's 100 ns | the pull-up current is already 2.94 mA of the weakest parts' 3 mA (section 6.2) | V-K01 | DRAWN |
| FW-K03 | the address map of section 6.1 | Reserved: 0x30 (TPS23861 broadcast); supervisors 0x34 to 0x36; no two targets on one address; a scan waits 100 ms between writes to 0x30 and 0x31 | I3-F01 | V-K01 | FIRMWARE |
| FW-K04 | the BQ25731, INA226 and ATECC608B reset their interface after 25 to 35 ms of SCL low (SMBus timeouts) | The master never holds SCL low longer than 10 ms, including inside an interrupt; a stuck bus is recovered with nine SCL pulses and a STOP, and logged | SLUSE66A 8.6; SBOS547; DS40002239B | V-K02 | FIRMWARE |
| FW-K05 | OWED (SC-HF-02): the supervisors' segment buffer U_S, EN from U7 IO1_7 through a 1 ms delay and a Schmitt buffer (section 6.7), low at power-up | Enable the supervisors' segment only for the panel's own transactions to it and disable it before any secure-element transaction and before a wipe; after each U7 write that moves EN, wait 5 ms with the bus idle before the next transaction, so EN changes only on an idle bus (TI SCPS245E 7.3.2) | SC-HF-02; R7 of `feasibility/ZEROIZE.md` | Z-EXP-C; V-K03 | OWED |

## 4. What round 8 changes in these rows

Round 8 is not merged at `e3aedb25`. Where a candidate moves a row, the row names it; the list, for the integrator. **At
`84e52461`** `main` carries r8a (`c0133147`), r8d (`76235aad`), r8e (`bc0f562f`, the clamp bar `45f6d83f`), r8c
(`9f28c238`), r8p (`7bef62bd`) and the battery packet (`dd39fb15`, `73d5df1e`); a row whose State reads ROUND 8 for one of
those is DRAWN on `main` from that commit. `fnd/r8b` is still a candidate.

| Candidate | Rows it moves | What |
|---|---|---|
| `fnd/r8a` (in `fnd/r8int1` c0133147) | FW-A05, FW-C07 | PA_EN and HF_EN now also read TX_INHIBIT_n (U35, U37 SN74AUP1G08); R102 10 k 1 %. No new firmware duty: nothing drives TX_INHIBIT_n (check_contracts section 13) |
| `fnd/r8b` | FW-B06, FW-B11, FW-B12, FW-B17, FW-B18, FW-C06, FW-K03 | per-slot EMCON_ON; EMCON_SUP; 10 k vote and select pulls; cascade break-before-make; DS3231SN; the 5G rail removed by hardware with Tpr held; the supervisors' addresses written as 0x34 to 0x36 |
| `fnd/r8c` | FW-C07 | GPIO21 reads EMCON_RD_R behind U13 and R46; the hardware EMCON lamp D22 needs no firmware |
| `fnd/r8d` (in `fnd/r8int1` 76235aad) | FW-D02 | ADS1115 at 0x48 for the flange; +5V_TX gated by +3V3_D8's band |
| `fnd/r8e` (in `fnd/r8int1` bc0f562f) | FW-A16 | VIN_RAW declared at 14.10 A from both feeds; the 80 % rule stands |
| `fnd/r8bat` | FW-C09, FW-P01 | the pack readings' 10 s fallback to the reduced mode; the round-8 charge window in the golden image |
| `fnd/w4b` (r8int6) | FW-B13 | the RockBLOCK's ENABLE is EMCON_HW AND U6's request RB_SW_IEN in U536; the panel raises the request only with +5V_RB up and, after an EMCON, only once RB_STATUS reads low (`feasibility/EMCON.md` 4c) |
| `fnd/w4c` | FW-C07; RAIL_SENSE, which no FW-C row covers yet (the contract writer's) | TX_INHIBIT_n's `R14` 2.2 k 1 % and `R50` 10 k 1 % (EQ-25): no firmware duty, nothing drives the line; RAIL_SENSE (GPIO 26, ADC0) now reads `LED_RAIL_SW` through the `R15`/`R51` divider (W4C-F1): about 2.5 V present, 0 V at BLACKOUT (PANEL.md section 3) |

## 5. Verification items this contract adds (V-nn)

Each is a bench or review step on the built prototype or on the firmware; none has run. `TEST-PLAN.md`'s owner files
them in the plan; until then this table is where they are defined.

| ID | Covers | Method and pass condition |
|---|---|---|
| V-A01 | FW-A01, A02 | read ChargeOption1, ChargeCurrent, ChargeVoltage after a charger POR and after every panel reboot; each equals the written value |
| V-A02 | FW-A04 | IDCHG and PROCHOT limits read back; a 20 A load step raises PROCHOT before the gauge's OCD1 |
| V-A03 | FW-A06, A07 | each software bit toggles its stage; PoE and USB-C drop with the PA keyed and return after; USBX_FLT reads low into a shorted port |
| V-A04 | FW-A09 | each INA226 against a reference meter at 10, 50 and 100 % of its rail's declared current |
| V-B04 | FW-B04 | PPS edges seen on each module with the LG290P locked |
| V-B07 | FW-B07 | review of the module secure-boot configuration against Raspberry Pi's document |
| V-B08 | FW-B08 | bus capture over a full boot and a status poll: no supervisor START, no answer at 0x30 to 0x32 or 0x60; clock stretch under 1 ms |
| V-B10 | FW-B10 | option bytes read back over SWD; a corrupted image refused by the verified boot |
| V-B14 | FW-B14, B15 | PoE class and power on a class 4 load; KSZ management reads at 0x5F |
| V-B17 | FW-B17 | holdover drift over 24 h with GNSS off |
| V-B19 | FW-B19, SC-HF-06 | the touch enumerates at full speed on bank 3's owner; with the display moved to each slot in turn (FW-C06) a touch lands on the selected module within 2 s; the touch controller's VBUS current measured (it sets board D's J_USB3 budget line, HF-F06) |
| V-C01 | FW-C01, A08, B13, D01 | scope on POE_EN, PD_EN, PA_EN, HF_EN, DEV_EN and SLOT_EN1..3 from MAIN press to run: no glitch high on any enable other than DEV_EN; the slots only after ZEROIZE_SW is read |
| V-C02 | FW-C02 | watchdog reset with three slots running: no slot rail drops |
| V-C03 | FW-C03, A10 to A12, B02 | MAIN tap, PI short press and PI 8 s hold: clean shutdown order, INT never driven high, force-off at 3.3 to 6.0 s |
| V-C04 | FW-A11, B03 | PI_KILL level with three slots powered and the panel held in RUN reset: under Q1's minimum threshold |
| V-C05 | FW-C05, B01 | stop the bridge on one slot: its line stops toggling, the panel declares it lost within 3 s and moves the display |
| V-C08 | FW-C08, E03 | SHORE_INHIBIT asserted: the inputs stop; released: they restart |
| V-C09 | FW-C09, A05, A13, D02 | C1 to C4 and K1 to K5 each tripped by an injected reading on the bench; the round-8 10 s fallback by halting the sensor controller |
| V-C10 | FW-C10 | SOS with EMCON asserted queues and tells; released, it sends |
| V-C12 | FW-C12 | the bridge protocol exercised end to end once MESHSAT-837's format is in the tree |
| V-C13 | FW-C13, C14, E10 | `TEST-PLAN.md` P15 at room temperature on the pack and on shore (every step of the hot stop forced by a substituted cell thermistor, the release rules, the four line states, the start-up read, the TMP117 stand-in) and E3-H; a step that did not act reads NOT_VERIFIED |
| V-D03 | FW-D03 | the SA868 refuses a frequency outside the configured band |
| V-E02 | FW-E02 | PRES reads high with the lead out and low with it in |
| V-E05 | FW-E05 | lid events logged with the kit off; no wipe |
| V-E07 | FW-E07 | a stalled fan reported within 5 s |
| V-E08 | FW-E08, E09 | standby drain with the kit off inside `ARCHITECTURE.md` section 11's figure |
| V-K01 | FW-K01 to K03 | SCL frequency, rise and fall times on each segment's farthest pin: tr at most 300 ns, tf between 12 ns and 100 ns, fSCL at least 90 kHz; a full address scan finds each target once |
| V-K02 | FW-K04, C11 | a target held low for 40 ms: the master recovers the bus and logs it; the panel's 3.3 V held off with the ribbon in: the bus reads stuck and nothing is written |
| V-K03 | SC-HF-02 | with the segments drawn: a SEG-A target's read while the ATECC608B and VEML7700 are idle: neither answers or wakes |

## 6. The kit I2C bus: speed, pull-ups and capacitance (computed)

Computed by `v2/docs/records/hc5/kit_i2c_budget.py` from the four netlists and the makers' documents; its output is
`kit_i2c_budget.out.txt` (netlists at `e3aedb25`) and `kit_i2c_budget.round8-d.out.txt` (board D from `fnd/r8int1`,
which adds the ADS1115). Desk arithmetic, INFERRED on VERIFIED figures. Re-run on `main` at `84e52461`, where round 8 is
integrated for A, C, D, E and P, the output is the round 8 one line for line (only the netlist label differs): board C's
round 8 adds no pin to SDA or SCL, so `kit_i2c_budget.round8-d.out.txt` is the reading on `main`.

### 6.1 Who is on it

| Address | Board | Part | Rise time it states | Low it reads |
|---|---|---|---|---|
| 0x10 | C | VEML7700 U_LIGHT | 1000 ns at 100 kHz | 0.4 V max |
| 0x20, 0x25 | B | PCA9555 U6, U7 | 1000 ns (standard mode) | 0.3 VCC |
| 0x21, 0x24 | A | PCA9555 U27, U28 | 1000 ns | 0.3 VCC |
| 0x22, 0x23 | C | PCA9555 U1, U2 | 1000 ns | 0.3 VCC |
| 0x26 | D | PCA9555 U16 | 1000 ns | 0.3 VCC |
| 0x28 (0x30 broadcast) | B | TPS23861 U5 (SDAI and SDAO both on SDA) | **300 ns from 0.8 to 2.3 V** | 0.9 V |
| 0x34, 0x35, 0x36 | B | STM32H743 U41, U51, U61 (targets, FW-B08) | (configurable) | 0.3 VDD |
| 0x40, 0x41, 0x44 to 0x47 | A | INA226 U8 to U11, U14, U17 (U14's A0 on SDA and U17's A0 on SCL add a pin each) | 1000 ns at 100 kHz | 0.3 VS |
| 0x48 (round 8) | D | ADS1115 U22 | **300 ns** | 0.3 VDD |
| 0x49 | B | TMP117 U10 | 1000 ns at 100 kHz | 0.3 V+ |
| 0x5F | B | KSZ9897R U1 (internal 58 k pull-up on both lines) | none stated | 0.9 V |
| 0x60 | B | ATECC608B U8 | **300 ns rise, 100 ns fall** | 0.5 V |
| 0x68 | B | DS3231 U9 | 300 ns (fast-mode table; standard mode accepted, note 6) | 0.3 VCC |
| 0x6B | A | BQ25731 U3 | **300 ns, any clock** | **0.4 V max** |
| master | C | RP2040 U3, GPIO0/1 | | 0.8 V |

Plus the ESD array U7 on C (2.5 typ, 3.5 max pF per line), test points A TP17/18, B TP10/11, C TP42/43, and the IDC headers
at both ends of the three ribbons. Sources in the script's header. Four targets state a 300 ns rise at every clock they
accept (BQ25731, TPS23861, ATECC608B and round 8's ADS1115); running the bus slower does not relax that.

### 6.2 Pull-ups

The drawn pull-ups are 2.2 k on B and 2.2 k on C per line, with the KSZ9897R's 58 k +-30 %: 1,019 ohm at -5 % and a
+3.40 V rail, 1,080 nominal, 1,138 ohm at +5 %. The weakest sinks on the bus (PCA9555, INA226, TMP117, DS3231, VEML7700,
ADS1115) guarantee 0.4 V at 3 mA, which puts the floor at (3.40 - 0.4) / 3 mA = 1,000 ohm (UM10204 7.1). The drawn value
meets it at 2.94 mA: **the pull-ups cannot be made stronger.**

### 6.3 One segment, as drawn: the budget fails (finding HF-F01)

At the rise-check Rp the four 300 ns targets allow at most 311 pF (30 to 70 %) and the TPS23861's fixed 0.8 to 2.3 V
thresholds at a 3.20 V rail allow 269 pF; at nominal, 328 and 303 pF. Against that:

| Line | Pins, bound (maker maximum, else UM10204's 10 pF) | Pins, nominal (maker typical) | Ribbons (490 mm at 47.5 pF/m, 3M 3365) | Left for copper, bound / nominal | Copper laid on the committed layouts |
|---|---|---|---|---|---|
| SDA | 267 pF | 143 pF | 23 pF | **-21 pF** / 137 pF | 1,568 mm: 157 to 345 pF at 1.0 to 2.2 pF/cm |
| SCL | 255 pF | 141 pF | 23 pF | **-9 pF** / 139 pF | 1,452 mm: 145 to 319 pF |

(With round 8's ADS1115: 277 and 265 pF of pins, -31 and -19 pF left.) The fixed part alone exceeds the bound's
limit, and at typical pin capacitance the copper already laid (A32, B21, C24, D12; older layouts, B21 not fully routed)
takes the total to 323 to 417 pF against 303 pF at the most favourable per-length figure. UM10204's 400 pF ceiling is
also crossed at the upper end. **The bus as one segment cannot meet the rise time four of its targets require, at any
per-length figure in the range and at typical pin capacitance; the bound includes failure, and the decision that removes
it is a schematic one, so it is taken now (SC-HF-02) and not left to a bring-up measurement.**

### 6.4 Speed

Standard-mode at 100 kHz nominal (FW-K01). The Fast-mode margin does not exist on this bus; nothing on it needs more
than the ZEROIZE budget's clock. The achieved SCL frequency is below the programmed one by the rise time and the RP2040
I2C block's clock synchronisation (INFERRED, about 93 kHz at 300 ns rise); `feasibility/ZEROIZE.md` says a clock below
100 kHz is a new input to its budget, so the budget was re-run at 90 kHz (`records/rv-zer/zeroize/zer_budget.py` with
`F_I2C = 90_000`, filed as `records/hc5/zer/zer_budget.py` with its outputs `run-90kHz.txt` and `run-100kHz.txt`): nominal sequence 0.521 s (0.517 s at 100 kHz), worst case in specification 0.825 s,
longest transfer 6.72 ms against the 10 ms HAL timeout, step 5 by 1.504 s, every pass line held and 10 of 10 planted
defects caught. The clock therefore stays at 100 kHz programmed, never below 90 kHz achieved (V-K01).

### 6.5 The session's choice: three segments (SC-HF-02, the registry's SC-59)

| Segment | Members | Pull-ups | Limit (bound / nominal) | Fixed (bound / nominal) | Copper left, bound, at 2.2 pF/cm |
|---|---|---|---|---|---|
| TRUNK | the master and board C; on B the expanders U6, U7, the ATECC608B, the DS3231, the TMP117; J_PANEL and J_AB1; one I/O of each new buffer | B's and C's 2.2 k (1,155 ohm at +5 %) | 307 / 322 pF (30 to 70 %: ATECC608B) | SDA 148 / 100 pF | 159 pF, **about 720 mm** |
| SEG-A | board A's nine targets and board D's (round 8: two), J_MEZZ1; behind a TCA9517A U_A on A, its A side local, its B side on the trunk, EN tied high | new 1.2 k to A's +3V3 | 281 / 295 pF (30 to 70 %: BQ25731, ADS1115) | SDA 129 / 53 pF (round 8: 139 / 63) | 152 pF, about 690 mm (round 8: 644 mm) |
| SEG-S | board B's three supervisors, the TPS23861 and the KSZ9897R; behind a TCA9517A U_S on B, its A side on the trunk, its B side theirs, EN from U7 IO1_7 through a delay (section 6.7), isolated by default | new 1.5 k to +3V3_DEV, with the KSZ's 58 k | 198 / 224 pF (TPS23861's thresholds) | SDA 65 / 45 pF | 133 pF, about 600 mm |

Why this and not another: the TCA9517A is held (`v2/vendor/ti/ti-tca9517a-i2c-buffer.pdf`, SCPS245E) and each of its
sides takes 400 pF; its B side presents a buffered low of 0.45 to 0.6 V, so a part that reads 0.4 V as its highest low
(the BQ25731) must sit on an A side, which puts board A's buffer with its A side local; two B sides may never join, so
only one B side is on the trunk; the parts on SEG-S all read 0.9 V or more as low. SEG-S also isolates the three
supervisors from the secure element whenever the panel has not opened their segment, which removes R7 (b) to (d) of
`feasibility/ZEROIZE.md` outside the panel's own status windows. Its I/Os are high-impedance when unpowered, so a dark
segment does not clamp the trunk. The laid copper fits: board A's 418 to 503 mm and board D's 20 to 34 mm are inside
SEG-A's 690 mm; the trunk carries board C's 464 to 478 mm and board B's trunk run, which together must stay under about
720 mm per line at 2.2 pF/cm (the layout constraint handed on, section 6.6).

Residual, stated: the ATECC608B (0.5 V) and VEML7700 (0.4 V) on the trunk see U_A's buffered low only in bits a SEG-A
target drives, never in a START, STOP or their own address, so neither can misread a condition that concerns it
(INFERRED; V-K03). Reversed by: a part with no static offset on either side (LTC4300A class, not held; a parts search), or
a rise-time accelerator on one segment, either of which would be taken only on a maker's document showing it meets the
300 ns targets at the bound. Taken by the session under the owner's standing rule of 26 September 2026; the circuit is
board A's and board B's to draw (section 6.7).

### 6.6 Constraints handed to layout

- Per line, the kit-bus copper of each segment at or under: TRUNK 159 pF (about 720 mm at 2.2 pF/cm, 990 mm at 1.6),
  SEG-A 152 pF (round 8: 142 pF), SEG-S 133 pF, each read with the field solver on the board's own stackup
  (`impedance_2d.py`'s atlc) before layout exit; an overrun is a finding, not a waiver.
- Board C: the RP2040, both expanders, the VEML7700 and the ESD array grouped at `J_PANEL`; board B: U_S and the trunk's
  parts between `J_PANEL` and `J_AB1`, the SEG-S run to the three supervisor pockets as a separate trunk from U_S.
- SDA and SCL keep a ground neighbour on at least one side in each ribbon's pin map where a revision allows it (today
  they are adjacent on all three: 26.7 pF/m balanced, about 9 pF over the panel ribbon, INFERRED acceptable at the chosen
  edge rates).

### 6.7 What boards A and B draw (the circuit brief for SC-HF-02)

TI TCA9517A, DGK VSSOP-8 (SCPS245E Table 4-1: 1 VCCA, 2 SCLA, 3 SDAA, 4 GND, 5 EN, 6 SDAB, 7 SCLB, 8 VCCB), one 100 nF at
VCCA and one at VCCB (section 9); its JLCPCB code and a certification row are the parts stream's (a new part is a
mismatch until proven, owner condition 1).

- **Board A, U_A:** VCCA and VCCB on A's `+3V3`; A side (pins 2, 3) to A's local SDA and SCL, which U3, U8 to U11, U14,
  U17, U27, U28, `J_MEZZ1` pins 10 and 11 and TP17/18 keep; B side (pins 6, 7) to `J_AB1` pins 11 and 12 as the new nets
  on the trunk side; EN (pin 5) to VCCB (the internal pull-up already holds it high; tie it for a definite level); new
  pull-ups 1.2 k to `+3V3` on the A side's two lines. Nothing on the B side needs a pull-up on A: the trunk's are on B and
  C. Place U_A at `J_AB1`.
- **Board B, U_S:** VCCA and VCCB on `+3V3_DEV`; A side to the trunk's SDA and SCL; B side to the new SEG-S lines, which
  U41, U51, U61 (pins 93, 92), U5 (SDA pins 4 and 5, SCL pin 3) and U1 (pins 98, 101) move onto; new pull-ups 1.5 k to
  `+3V3_DEV` on the B side's lines. EN from U7 IO1_7 (pin 20, EXP_SPARE11 today) through 10 k and 100 nF into a 74LVC1G17
  (the part and the arrangement board B's round 8 uses for its select delays, `fnd/r8b` FAB-03), 10 k from IO1_7 to GND so the segment is
  isolated at power-up (the PCA9555's internal pull-up against 10 k sits near 0.3 V, under the Schmitt input's low
  threshold at its datasheet values: INFERRED, read on board B's author's sheet). The 1 ms delay moves every EN edge past
  the STOP of the U7 write that caused it; the firmware waits 5 ms (FW-K05).
- **Net names across the connectors:** `J_PANEL` and `J_AB1` keep the trunk's SDA and SCL on the same pins, so
  `check_contracts.py` sections 1 and 7 are unchanged. Board A's local lines take new names (for example `SDA_A`,
  `SCL_A`) and so does board D's end of the harness, or `check_contracts.py`'s ALIAS list gains the pair: section 8
  compares `J_MEZZ1` with `J_HARN1` by name. Board B's SEG-S lines take new names the same way; nothing crosses a
  connector on them.
- **Check it on the netlist:** `kit_i2c_budget.py`'s segment table re-run with the segments read from the regenerated
  netlists, once its reader (which reads the nets named SDA and SCL today) is given the new names; and `check_contracts.py`
  PASS across the set.

## 7. Findings this page raises

| ID | Severity | Finding | Evidence | Owner |
|---|---|---|---|---|
| HF-F01 | major | The kit I2C bus as one segment cannot meet the 300 ns rise its BQ25731, TPS23861, ATECC608B (and round 8's ADS1115) require: pins and ribbons alone exceed the bound's limit, the laid copper exceeds the nominal one, and the pull-ups are at the 3 mA floor | section 6.3; `records/hc5/kit_i2c_budget.out.txt` | boards A and B (SC-HF-02); layout (6.6) |
| HF-F02 | major | INA226 `A:U17` monitors the 54 V PoE rail with IN+ on POE_OUT and IN- on +54V_POE (`gen_sch_a.py:950`): TI SBOS547 section 5.1 gives IN+ and IN- an absolute maximum of 40 V, and section 5.5 note 1 says "Do not apply more than 36 V". A damaged monitor can hold the kit bus. Options: sense on the stage's VBAT input side (12 to 16.8 V), a low-side shunt in the rail's return, or a part rated for the rail (a substitution needs its maker's document) | `A:U17.9-10`; `v2/vendor/ti/ti-ina226.pdf` sections 5.1 and 5.5 note 1 | board A's author |
| HF-F03 | minor | FW-A16 cited FE_PGOOD on U28 pin 20; it is `A:U27.20` (IO1_7) | board A's netlist | this page (corrected) |
| HF-F04 | minor | The mixer-fan and camera leads differ between the netlist and `ASSEMBLY.md` section 4: E's J_FAN1/2 and B's J_CAM are 2.54 mm pin headers, the leads table says SH and PH housings | E and B netlists; `ASSEMBLY.md` section 4 | ASSEMBLY.md's writer; boards B and E (IF-E-FANS, IF-CAM) |
| HF-F05 | minor | E's fans take the pack node (CELL_F, up to 16.8 V) as a "12 V class fan"; no fan part is picked, so the fan's rating against 16.8 V is TBD | `E:J_FAN1.1` | board E's author (IF-E-FANS) |
| HF-F06 | major (raised from minor at integration, after hc5's second review: a fault on the touch lead removes board D, whose APRS path is a prototype 1 core function under D-01) | Board D's spare hub port `J_USB3`, which SC-HF-06 gives the monitor's touch USB, takes its VBUS straight from `+5V_D8` with no port limit (the TUSB2046I's PWRON3_n is unconnected), so a fault on the touch lead is cleared only by board A's eFuse U23 (TPS259631, 2.0 A) and takes board D (the VHF path and the headsets) down with it; and `gen_sch_d.py` budgets J_USB3 at 0.05 A where USB 2.0 section 7.2.1 allows a device one unit load (100 mA) unconfigured and five (500 mA) configured | `D:J_USB3.1`; `A:U23` (TPS259631 +5V_DEV to +5V_D8, ILM 2.0 A); D's rail budget (`gen_sch_d.py` loads, `J_USB3: 0.05`); USB 2.0 section 7.2.1 (`records/hc5/usb-2-0-clauses-cited.md`) | board D's author, before board D's layout entry (open item S-61): a current-limited switch on J_USB3's VBUS (the TPS2065C, held as `ti-tps2065c-slvsau6i.pdf`, is the kit's existing part for this) and the budget line at the touch's measured draw (V-B19) |
| HF-F07 | minor | Board E's Geiger pulse `GEIGER_PULSE` reaches the RP2040's GPIO7 through R48 22 R only: no pull, no divider, no clamp. The module (a RadiationD-v1.1 class board, part not picked) runs on 5 V from U16; if its output idles at 5 V it exceeds the RP2040's IOVDD + 0.5 V absolute maximum at an IO (RP2040 datasheet Table 622, VERIFIED). Also on E: the mixer-fan switches Q9, Q10 have no gate pull-down and rest on the RP2040's pad pull-down (PADS_BANK0 PDE reset 1, RP2040 datasheet Table 341) | E netlist `f3c1ad6153002976` (`R48`, `U10.9`, `Q9`, `Q10`) | board E's author: pick the module and read its output stage; a divider or a clamp to +3V3_E6 if it is 5 V; discrete gate pull-downs on Q9 and Q10 |
| HF-F08 | minor | `IF-EXT-ETH`'s first draft said INT-001 judges the MDI pairs; it judges `SWP4_*` (the switch to the magnetics), and nothing judges `MDI_A..D` (the magnetics T1 to `J_ETH`): they match neither `ETH*` nor `SWP*`, sit in the HV net class, carry no declared tolerance and read 2.74 to 14.68 mm on B21, and the switch's checklist states no number for them (the record since 21 September 2026) | `pcb_interfaces.yaml` boards.b; `interfaces.py` (fnmatchcase); `gen_pcb_b3.py:576`; `pcb_decisions.yaml` decisions 29 and 36 (correction of 21 September 2026) | board B's next phase (a class or a tolerance from a source, or the MDI side stated as unjudged at layout entry); the contract says so |

## 8. Session choices taken here (under the owner's standing rule of 26 September 2026)

**Entered in the registry (27 September 2026, the second release attempt of layers 1 to 3; layer 3's release check, R5).** The requirements registry (`v2/ecad/tools/pcb_requirements.yaml`, `session_choices`) is the one record of a session choice: these six are its SC-58 to SC-63, each naming its ID here as `drafted_as`, and `rules_lib.py requirements` refuses any SC- id the registry or a page of `v2/docs/` or `v2/docs/handover/` cites that no registry entry defines. The IDs below are the drafts' names, kept so that the pages citing them still read.

| ID | Registry | Question | Taken | Why | Reversed by |
|---|---|---|---|---|---|
| SC-HF-01 | SC-58 | Which heartbeat source is the contract | the compute module's GPIO16 under the bridge; panel and supervisors listen | the netlist (section 2); `ARCHITECTURE.md` 10.1 already says so | a generator change that moves the source |
| SC-HF-02 | SC-59 | How the kit I2C bus meets its targets' rise time | three segments behind two TCA9517A (section 6.5) | the one-segment bound fails and the pull-ups are at the floor; the held buffer does it and also narrows ZEROIZE's R7 | a no-offset buffer or an accelerator shown by a maker's document (6.5) |
| SC-HF-03 | SC-60 | The kit bus clock | Standard-mode, 100 kHz programmed, at least 90 kHz achieved | the ZEROIZE budget holds at 90 kHz; no part needs more | a measured rise time that allows Fast-mode on every segment, and a need for it |
| SC-HF-04 | SC-61 | The hot-plug rules `pcb_interfaces.yaml` marked "(proposed)" | adopted as written: IF-BC-PANEL, IF-AB-RIBBON, IF-AB-POWER, IF-A-PA and IF-LID-HF are mated and unmated with the kit off | a partly seated ribbon can assert PI_KILL or drop SLOT_EN; VH leads carry up to 6 A | an interlock that makes live mating safe |
| SC-HF-05 | SC-62 | The supervisors' status stretch and the master's SCL hold | at most 1 ms stretch; the master never holds SCL low over 10 ms | three targets reset their interface at 25 to 35 ms | none needed |
| SC-HF-06 | SC-63 | Where the Xenarc 709GNK's touch USB connects, and how it follows the display owner (the audit's unresolved decision; `ASSEMBLY.md` named "a B16 slot hub header" with no designator) | board D's spare hub port `J_USB3` (PH 1x4), through a USB A receptacle to PH adapter lead made up at build; the touch follows the display owner by the HAL's network share (FW-B19). Carried, with this board end, in `pcb_interfaces.yaml` IF-MON, `ARCHITECTURE.md` section 12 (IF-MON's row; `J_USB3` is no longer among the ports given no contract), `ASSEMBLY.md` section 4's touch row and build step 9, and `PANEL.md` section 1's Pass-throughs row | every one of board B's twelve hub ports is allocated (`gen_sch_b.py:764-766`); `J_USB3` exists for a lead made up at build, needs no board B change (B's floor plan is open under FB-FAB-6), matches the leads table's PH housing, and a full-speed hub carries a HID touch (USB 2.0 section 7.1 Table 7-1: a high-speed capable device attaches at full speed first; `records/hc5/usb-2-0-clauses-cited.md`); appendix 32.52 makes the HAL's network share the kit's way to reach a device on another module. Costs, carried as HF-F06: J_USB3's VBUS has no port limit and its budget line is 0.05 A | a board B port reallocation or added downstream capacity on B (the audit's two options), after which J_USB3 returns to spare |

## 9. What this page does not claim, and what stays open

- No row is shown on a bench; the V-nn items, FW-A15, O-CHG-n, E-nn, Z-EXP and P-nn are all owed.
- SC-HF-02 is a decision, not a circuit: until boards A and B draw it, HF-F01 stands and the layer 5 "electrical levels"
  acceptance item stays open for the kit bus.
- HF-F02 changes board A's circuit; it is not drawn. HF-F06 and HF-F07 change boards D and E; neither is drawn.
- SC-HF-06 gives the touch USB a board end with no board change, but its costs (HF-F06) are owed to board D, and the
  touch reaching the display owner is a firmware share (FW-B19), not a hardware path.
- The panel's USB wire format is MESHSAT-837, outside this repository: a recipient cannot implement FW-C12 from the tree.
- The SLOT_EN hold across a panel reset (FW-C02) is not drawn; while it is not, a panel reset powers off every module.
- The supervisors' option bytes and the gauge's host watchdog behaviour rest on documents the tree does not hold (ST
  RM0433; TI SLUUAQ3A is held for the gauge).
- The kit bus figures are desk arithmetic: 10 pF per pin where a maker publishes no maximum, 1.0 to 2.2 pF/cm of copper by
  closed form. A field-solver reading and V-K01 on the built boards are owed.
- The hot stop's rows (FW-C13, FW-C14, FW-E10) rest on HOT-R1, drawn on boards A and E since 27 September 2026 (SC-70;
  `records/w4ae/hot_r1_trace.py` reads the path on the committed netlists); the rows themselves are firmware, verified
  at P15 and E3-H (V-C13), and REQ-077 reads INCONCLUSIVE at desk, held by FEA-004.

## 10. Change record

| Version | Date | Change |
|---|---|---|
| 1 | 27 September 2026 | First filing: FW-A01 to A16 from board A's round 4 (FW-A16's FE_PGOOD citation corrected); the panel, board B, D, E, P and kit-bus rows from W5 round 2 with A01, A02, A07 and A11 applied, re-read at `e3aedb25`; round 8's changes listed; the heartbeat resolved; the kit I2C budget computed; HF-F01 to F05; SC-HF-01 to 05 |
| 1 (completed) | 27 September 2026 | After an AI review the same day: FW-A02, A05 and A13 cite the session's items under D-06 and D-11 instead of presenting them as the owner's; FW-A07 keeps the port's uses as D-12 gives them (the first filing had narrowed them to key fill and console); FW-C04, C10 and E05 say which part of each row the owner's ruling carries; FW-B19, V-B19, HF-F06 to F08 and SC-HF-06 added; section 4 says which round 8 rows are on `main` at `84e52461` |
| 1 (second review fixes) | 27 September 2026 | After the second AI review: SC-HF-06's board end (`D:J_USB3`) is carried the same way in every page that names the monitor's touch lead (`ASSEMBLY.md` build step 9 and `PANEL.md` section 1 joined section 4's row and IF-MON; `ARCHITECTURE.md` section 12 no longer lists `J_USB3` as given no contract); IF-BA-RF's D-07 note says board A's site at X +46 is in no generator and board E's cavity at X 46 is drawn since `45f6d83f`; the drafts re-checked against `main` at `a8652172` |
| 1 (integration) | 27 September 2026 | Merged at the r8int4 integration onto `main` `38dcd764` (board B's round 8 there): the registry takes S-59 (SC-HF-02), S-60 (HF-F02), S-61 (SC-HF-06 and HF-F06), S-62 (HF-F07) and CON-026 (the kit bus rise time); PANEL.md section 7's new paragraph gives the weakest targets' 3 mA as the sink their datasheets rate at 0.4 V (the claims screen, ENV-002); V-B19 moved into section 5; FW-A08 counts six expanders; HF-F06 raised to major and carried before board D's layout entry; `ARCHITECTURE.md` section 12 keeps board B's round 8 facts on IF-BC-PANEL; IF-AE-RF and the section 2 and W4-F10 lines of `ARCHITECTURE.md` say board E's cavity at X 46 is drawn; IF-E-WATER, IF-E-SENSORS, IF-DA-VHF, IF-MON and IF-EXT-DC take the second review's wording items; the handover pages carry SC-HF-06 where they named the touch lead |
| 1 (second release attempt) | 27 September 2026 | After the release checks of layers 1 to 3 (`fnd/rel2`, at `953f5658`): FW-C09 takes C1 as `CONOPS.md` section 4c defines it (the reduced mode of slots 2 and 3, then the heat stage's one module); FW-C13, FW-C14 and FW-E10 carry the hot stop and HOT-R1 (layer 2's finding B4 and the layer 3 release check's note for layer 5), with V-C13 on `TEST-PLAN.md` P15; section 8's six choices are the registry's SC-58 to SC-63 (layer 3's R5), and section 0 names P15 |
| 1 (HOT-R1 drawn) | 27 September 2026 | By stream w4ae after HOT-R1 was drawn on boards A and E (SC-70): FW-C13, FW-C14 and FW-E10 read DRAWN with the parts' designators (`A:R216`, `E:Q11`, `E:R58`); FW-C14 gains the `EXP_INT` service (the port read, the PCA9555 errata) and the once-a-second poll, FW-E10 the watchdog bound under FW-C14's 3 s; section 9's hot stop line follows |
