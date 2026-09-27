# STM32H743 compatibility matrix: board B's three I/O supervisors

Prototype design (MESHSAT-1357, pre-PCB layer 6, closer hc6, 27 September 2026). Nothing on this page has been built,
bought for assembly, powered or measured. It is a desk comparison of ST's own documents against the committed
schematic, made by the session; it is not a qualified engineer's review and not a test.

**The question (owner condition 1, CON-017, S-41, D-13).** The design first named the STM32H753VI for the supervisors
U41, U51 and U61 (`v2/docs/research-io-supervisor-2026-09-09.md:3-4`); the purchase code C114409 buys the
STM32H743VIT6, and owner ruling D-13 of 26 September 2026 accepted the H743 with software-verified boot as the
prototype's floor. Since `458b2873` the symbol, value and order line name the STM32H743VIT6
(`v2/ecad/tools/gen_sch_b.py:1145-1146`). Condition 1 says a substitution is a mismatch until it is shown compatible. This page is the
proof CON-017 clause (3) asks for: every pin, peripheral and electrical feature the schematic uses, read in the H743's
own documents, set against the H753 the design first named, and every H753-only unit checked for a dependence.

**Judged at** main `e3aedb25`: `v2/ecad/tools/gen_sch_b.py` sha256/16 `dedaf34ce285e5ff` (lines 281-289 the pin table,
1085-1158 the control plane) and the committed netlist `v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net` sha256/16
`669d02d07aeaae4b` (U41, U51 and U61 read pin by pin). The round 8 board B candidate in worktree `r8b` changes one net
on these parts (pin 33, PC5, reads `EMCON_SUP`, a 74LVC1G34 copy of `EMCON_HW`, EMCON finding L1); every pin number,
pin function and alternate function below is the same in that candidate (netlist compared pin by pin for all three
supervisors on 27 September 2026). Re-checked at main `53a98a71`, where round 8's boards A, D and E are integrated:
`gen_sch_b.py` and board B's netlist are byte-identical there (sha256/16 `dedaf34ce285e5ff` and `669d02d07aeaae4b`), so
every row below stands.

## 0. Verdict

| Clause | State | Evidence |
|---|---|---|
| CON-017 (1) the schematic, symbol and BOM name the STM32H743VIT6, pin map unchanged | MET (held since `458b2873`) | `gen_sch_b.py:1146`; netlist value of U41, U51, U61; `v2/docs/records/r4b/pin_parity.py` (100 of 100 pins agree between DS12110 Figure 5 and DS12117 Figure 4) |
| CON-017 (2) regeneration parity traced | MET (CON-017 evidence, clamp-symbol merge) | `v2/ecad/tools/pcb_requirements.yaml` CON-017 evidence |
| CON-017 (3) compatibility matrix of every peripheral and feature used, with DS12110 sources | **MET by this page** (sections 2 to 6) | DS12110 Rev 10 and Rev 11, RM0433 Rev 8, ES0392 Rev 15, AN4938 Rev 7 |
| CON-017 (4) the supervisor firmware builds for the STM32H743 | **OPEN, allocated to the firmware stage** (section 8): no supervisor firmware exists, and nothing the layout decides depends on it | none; proposed registry change in `drafts/hc6/apply_registry.py` |
| Dependence on an H753-only unit (CRYP, HASH, secure access mode, RSS, secure-only flash) | **NONE** in any requirement, generator line or feasibility page (section 5) | RM0433 Rev 8 Table 2, p.103 |

Seven findings the design must carry. None changes a pin, a land or a net; they are procurement, firmware and
record obligations, each placed at the stage where its evidence can exist:

- **F1, silicon revision (procurement and firmware).** The design uses both FDCAN controllers. ES0392 Rev 15 section
  2.24.2 ("Wrong data may be read from message RAM by the CPU when using two FDCANs", workaround: none) is present on
  silicon revision Y and W and absent on X and V; so are 2.2.8 (PCROP areas may be unprotected, which touches D-13's
  verified boot) and 2.2.14 (leakage when an input is above VDD, which is the dark-controller case of IOHA A4). The
  supervisors must be revision V or X: marking V or X, REV_ID 0x2003 or 0x2001 in DBGMCU_IDC (ES0392 Table 2, p.1;
  RM0433 p.3208). Checked at goods-in (ASSEMBLY) and read by the firmware at boot. Session choice HC6-SC-1.
- **F2, the kit bus (firmware contract).** A supervisor is an I2C target on the same SDA and SCL as the expanders, the
  PoE controller, the holdover clock and the secure element (`ARCHITECTURE.md` 5.5). ES0392 2.19.9 ("Transmission
  stalled after first byte transfer", a state in which the peripheral is stalled in target mode with clock stretching
  enabled) would hold SCL and stop the whole bus; 2.19.3 needs the I2C kernel clock at 10 MHz or more in Fast mode;
  2.19.10 holds SDA low if SMBus timeouts are used in target mode. Obligations in section 6. Session choice HC6-SC-2.
- **F3, the HSE crystal (part choice).** The fitted 25 MHz C164047 meets the oscillator criterion on its maker's own
  sheet (gm_crit 0.67 mA/V against Gmcritmax 1.5 mA/V), but it is NO_STOCK (3 against 20) and LCSC's parametric for it
  states 80 Ohm where the maker's sheet states 30 Ohm maximum. Any replacement is chosen by the same computation;
  section 7 gives it for two stocked candidates. Session choice HC6-SC-3 (recommendation to board B's author).
- **F4, document currency.** DS12110 Rev 10 (March 2023), the revision every record cites, is superseded by Rev 11
  (13 January 2026), which updated the pin table, the alternate function table, the operating conditions, VCAP, the
  I/O static characteristics and the I2C characteristics. Every row used here was re-read in Rev 11: no used pin,
  alternate function or relied-on value changed (sections 2 and 3). Rev 11 is filed.
- **F5, rev Y tables cited for a rev V part.** DS12110 carries two electrical sections, section 6 for silicon revision
  Y and section 7 for revision V. `gen_sch_b.py:1020` and `:1108-1114` cite Rev 10 Tables 21, 22, 24 and 60, which are
  the revision Y section. The revision V tables (Rev 10 Tables 119, 120, 122, 157; Rev 11 Tables 109, 110, 112, 147)
  give the same figures the design relies on: TT_xx input 4.0 V absolute maximum, "Positive injection is not possible
  on these I/Os", and TT_xx leakage +-250 nA (section 4). No circuit change; the citation should name section 7 (a
  comment for board B's author, recorded in `drafts/hc6/README.md`).
- **F6, the watchdog starts in hardware (provisioning).** `ARCHITECTURE.md` 6.1 has "option-byte start TBD (RM0433 not
  held)". RM0433 is now held: IWDG1_SW = 0 in the user option bytes makes "the watchdog ... automatically enabled at
  power-on" (RM0433 Rev 8 p.179; FLASH_OPTSR bit 4, p.214), clocked by the LSI and "active even if the main clock
  fails" (p.1894). Session choice HC6-SC-4: hardware watchdog, IWDG frozen in neither Stop nor Standby, written at
  provisioning with the other option bytes.
- **F7, the records disagree.** `v2/vendor/SOURCES.yaml` (io-supervisor-mcu, `update_45bde541`: identity MATCH, reopen
  conditions settled), `ARCHITECTURE.md:586` at `53a98a71` ("Owner condition 1 is not closed by the text"), `ARCH-PCB-B-IOHA.md`
  section 6 ("baseline 3x STM32H753", I2C on PB1/PB2 as an open finding) and section 10a (the rename "has not been
  done yet"), and S-41 (supervisor addresses 0x30 to 0x32, where `ARCHITECTURE.md` 5.5 took 0x34 to 0x36 under
  I3-F01) describe four different states. Patches that make them agree with this page are in `drafts/hc6/`.

## 1. Documents read

| Document | Revision | File in this tree | sha256/16 | Source and currency |
|---|---|---|---|---|
| ST DS12110, STM32H742xI/G STM32H743xI/G datasheet | Rev 10, 30 March 2023 | `v2/vendor/st/st-stm32h743xi-datasheet.pdf` | `9b27d1d993a8bc5b` | Wayback copy (st.com refuses this host); **superseded by Rev 11** |
| ST DS12110 | **Rev 11, 13 January 2026** (PDF dated 15 to 21 January 2026) | `v2/vendor/st/st-stm32h743xi-datasheet-rev11.pdf` (filed now) | `f6e620179006c8c4` | `https://web.archive.org/web/20260827112637id_/https://www.st.com/resource/en/datasheet/stm32h743vi.pdf`, fetched 2026-09-26T23:51Z; the archive served it gzip-encoded and the filed file is the decompressed body; the capture of 2026-03-18 (`20260318060051id_`) is byte-identical; st.com answered this host with an HTTP/2 INTERNAL_ERROR at 2026-09-26T23:49Z |
| ST DS12117, STM32H753xI datasheet | Rev 9, March 2023 | `v2/vendor/st/st-stm32h753xi-datasheet.pdf` | `3bf346d8a511843a` | Wayback copy; the newest archived capture is of 2023-06-08, so a newer revision is not excluded (the H753 is not fitted; it is read only for what it adds) |
| ST RM0433, STM32H742, STM32H743/753 and STM32H750 reference manual | **Rev 8, January 2023** (3353 pages) | `v2/vendor/st/st-rm0433-rev8.pdf` (filed now, 40.7 MB) | `9ba54135736a47a3` | `https://web.archive.org/web/20251014013150id_/https://www.st.com/resource/en/reference_manual/rm0433-stm32h742-stm32h743753-and-stm32h750-value-line-advanced-armbased-32bit-mcus-stmicroelectronics.pdf`, fetched 2026-09-26T23:50Z; newest capture 2025-10-14, still Rev 8 |
| ST ES0392, device errata | **Rev 15, September 2025** | `v2/vendor/st/st-es0392-rev15.pdf` (filed now) | `effe23b2b79ec4ee` | `https://web.archive.org/web/20260526205148id_/https://www.st.com/resource/en/errata_sheet/es0392-stm32h742xig-stm32h743xig-and-stm32h753xi-device-errata-stmicroelectronics.pdf`, fetched 2026-09-26T23:52Z, served gzip-encoded, filed decompressed |
| ST AN4938, hardware development | Rev 7, 29 October 2024 | `v2/vendor/st/st-an4938-rev7.pdf` | `217b5dcbfdd27cec` | Wayback copy of 2025-07-26 (SOURCES.yaml io-supervisor-mcu) |

Rev 11 reads "refer to RM0399 reference manual" in its I2C section (p.297); RM0399 is the STM32H745/755/747/757 manual,
so that is a documentation slip, and RM0433 is the manual for this part (its own title and ES0392's applicability line).

## 2. Identity, package and grade

| Item | STM32H743VIT6 (fitted) | STM32H753VIT6 (first named) | Verdict |
|---|---|---|---|
| Ordering code | V = 100 pins, I = 2 MB flash, T = LQFP, 6 = -40 to +85 C (DS12110 Rev 11 section 9, p.346; Rev 10 p.348) | same scheme (DS12117 Rev 9 section 9) | the code buys the part the land and the pin table describe |
| Package | LQFP-100 14 x 14 mm, 0.5 mm pitch; pinout Figure 5, p.55 of both revisions | DS12117 Figure 4, p.55 | 100 of 100 pins agree (`records/r4b/pin_parity.py`, RECORDED) |
| Operating range | TA -40 to +85 C at maximum power dissipation, TJ -40 to +125 C (105 C at VOS0) (Rev 11 Table 112, p.210) | same | against `v2/ecad/tools/pcb_envelope.yaml`: -20 C floor and 51 C worst inside air (part_temps.py's bar): **INSIDE**, 34 K below the TA limit |
| Storage | TSTG -65 to +150 C (Rev 11 Table 111, p.208) | same | covers the -33 C and +71 C qualification margins |
| Stock | C114409 CERTIFIED (`JLC-CERTIFIED.tsv:582-584` at `53a98a71`, the reading of 26 September 2026: 4270); JLCPCB 4265 at 2026-09-27T04:00:07Z; tape-and-reel C5271084 | C730206 stock 0 | see `v2/docs/parts/PROCUREMENT.md` |

## 3. Every pin the schematic uses

Net names are supervisor A's (U41); B and C carry the same functions on their own `IOCB_`/`IOCC_` nets, the shared
`HB1..3`, `BSEL1..3`, `WIFI_SEC`, `EMCON_HW`, `SCL`, `SDA`, and their own `SEL`, `HUBRST` and `WSEC` bits. I/O
structure is DS12110 Table 9's column, read in Rev 10 and in Rev 11 (pp. 64 to 88): identical for every row. Pins
not listed are unconnected (56) or supplies (14).

| Pin | Name | I/O structure | Net (U41) | Use | Function and mode | Source (DS12110 Rev 11; Rev 10 in brackets) | Verdict |
|---|---|---|---|---|---|---|---|
| 12 | PH0 | FT | `IOCA_XI` | HSE crystal | OSC_IN, additional function | Table 9; section 7.3.7 Table 131 p.229 | MATCH (section 7 for the crystal) |
| 13 | PH1 | FT | `IOCA_XO` | HSE crystal | OSC_OUT | as above | MATCH |
| 14 | NRST | RST | `IOCA_RST_n` | reset, 10 k to 3V3, 100 nF to GND | bidirectional, internal pull-up RPU 30 to 50 k | Table 152 p.248 (Table 162) | MATCH; the 100 nF is Figure 74's "Recommended NRST pin protection" (0.1 uF, p.248), and the external 10 k sits in parallel with RPU |
| 22 | PA0 | FT_a | `SEL1_A` | voted bank 1 select, output | GPIO push-pull | Table 9 | MATCH |
| 23 | PA1 | FT_ha | `SEL2_A` | voted bank 2 select, output | GPIO | Table 9 | MATCH |
| 24 | PA2 | FT_a | `SEL3_A` | voted bank 3 select, output | GPIO | Table 9 | MATCH |
| 25 | PA3 | FT_ha | `HUBRST1_A` | voted hub 1 reset, output | GPIO | Table 9 | MATCH |
| 28 | PA4 | TT_a | `HUBRST2_A` | voted hub 2 reset, output | GPIO; injection 0/0 on PA4, PA5 (Table 110) | Table 9, Table 110 p.208 | MATCH as an output (100 k pull-down only; nothing drives it from outside) |
| 29 | PA5 | TT_ha | `HUBRST3_A` | voted hub 3 reset, output | GPIO; as PA4 | as PA4 | MATCH |
| 30 | PA6 | FT_a | `HB1` | module 1 heartbeat, input | GPIO input | Table 9 | MATCH |
| 31 | PA7 | TT_a | `HB2` | module 2 heartbeat, input | GPIO input, TT: 4.0 V absolute | Table 9, Table 109 | MATCH (section 4) |
| 32 | PC4 | TT_a | `HB3` | module 3 heartbeat, input | GPIO input, TT | as PA7 | MATCH |
| 33 | PC5 | TT_a | `EMCON_HW` (r8b: `EMCON_SUP`) | EMCON state, input only (round 6 O-06) | GPIO input, TT | as PA7 | MATCH; firmware keeps it an input (section 6) |
| 34 | PB0 | FT_a | `IOCA_LED_A` | alive LED, sinks through 1 k from 3V3 | GPIO output, about 1.3 mA | Table 110 (IIO 20 mA per pin) | MATCH |
| 37 | PE7 | TT_ha | `WSEC_A` | voted WiFi changeover, output | GPIO | Table 9 | MATCH |
| 38 | PE8 | TT_ha | `BSEL1` | read-back of voted bank 1, input | GPIO input | Table 9 | MATCH |
| 39 | PE9 | TT_ha | `BSEL2` | read-back, input | GPIO input | Table 9 | MATCH |
| 40 | PE10 | FT_ha | `BSEL3` | read-back, input | GPIO input | Table 9 | MATCH |
| 41 | PE11 | FT_ha | `WIFI_SEC` | read-back of the WiFi changeover, input | GPIO input | Table 9 | MATCH |
| 48, 73 | VCAP | S | `IOCA_VCAP` | LDO output, 2 x 2.2 uF | regulator ON | Table 114 p.211 (CEXT 2.2 uF, ESR under 100 mOhm, two capacitors) | MATCH |
| 51 | PB12 | FT_u | `IOCA_CAN2_RX` | fabric B receive | **FDCAN2_RX, AF9** | Table 10 p.91 (Table 11 p.90) | MATCH; FT_u is supplied by VDD when not in USB use (Table 9 note 7) |
| 52 | PB13 | FT_u | `IOCA_CAN2_TX` | fabric B transmit | **FDCAN2_TX, AF9** | Table 10 p.91 (Table 11 p.90) | MATCH |
| 72 | PA13 | FT | `IOCA_SWDIO` | SWD pads | JTMS-SWDIO, AF0, pull-up after reset | Table 10 p.90 (Table 10 p.89); RM0433 p.533 | MATCH |
| 76 | PA14 | FT | `IOCA_SWCLK` | SWD pads | JTCK-SWCLK, AF0, pull-down after reset | as PA13 | MATCH |
| 81 | PD0 | FT_h | `IOCA_CAN1_RX` | fabric A receive | **FDCAN1_RX, AF9** | Table 10 p.92 (Table 13 p.92) | MATCH |
| 82 | PD1 | FT_h | `IOCA_CAN1_TX` | fabric A transmit | **FDCAN1_TX, AF9** | Table 10 p.92 (Table 13 p.92) | MATCH |
| 92 | PB6 | FT_f | `SCL` | kit bus clock, target | **I2C1_SCL, AF4**, Fm+ capable | Table 10 p.90 (Table 11 p.89) | MATCH |
| 93 | PB7 | FT_fa | `SDA` | kit bus data, target | **I2C1_SDA, AF4** | Table 10 p.90 (Table 11 p.89) | MATCH |
| 94 | BOOT0 | B | `IOCA_BOOT0` | 10 k to GND | boot from BOOT_ADD0, factory 0x0800 0000 (user flash) | RM0433 Table 9 p.138, section 4.4.7 p.181; BOOT0 absolute 9.0 V (Table 109) | MATCH |
| 6 | VBAT | S | `+3V3_IOCA` | tied to the rail | no battery; AN4938: "it is mandatory to connect this pin to an external power supply" | AN4938 Rev 7 section 2.2 p.12 | MATCH |
| 20, 21 | VREF+, VDDA | S | `+3V3_IOCA` | tied to the rail | VDDA 0 to 3.6 V when ADC, DAC, OPAMP, COMP and VREFBUF are unused (Table 112) | Table 112 p.209 | MATCH; AN4938's 100 nF + 1 uF on VDDA is W6-F7, fixed in the r8b candidate (G7) |
| 11, 27, 50, 75, 100 | VDD | S | `+3V3_IOCA` | 3.3 V from a private AP2112K | 1.71 to 3.6 V on LQFP100 (no PDR_ON pin; Table 2 note 5) | Table 112; Table 2 p.22 | MATCH |

## 4. Electrical features the design relies on

| Feature | What the design relies on | H743 (DS12110 Rev 11, revision V section) | Same in Rev 10 and in the revision Y section | H753 (DS12117 Rev 9) | Verdict |
|---|---|---|---|---|---|
| Inputs from rails other than the controller's own (HB1..3 pulled to `+3V3_DEV`, voter read-backs on `+3V3_DEV`, `EMCON_HW` from board C's buffer) | VIN within the operating limit while powered | TT_xx: -0.3 to VDD + 0.3 V; others: up to Min(VDD, VDDA, VDD33USB) + 3.6 V (Table 112 p.209). `+3V3_DEV` (AP63203) and the private rail (AP2112K-3.3) are both nominal 3.3 V; the worst difference of the two regulators' stated tolerances has to stay inside 0.3 V | yes (Table 24 / Table 122) | same | MATCH; the regulator tolerance comparison belongs to the power review (R-PWR) and is not re-derived here |
| A dark controller (LDO held off by `J_IOCOFF_x`, IOHA A4 and A6) with its TT inputs at 3.3 V | no damage and no back-feed | "Input voltage on TT_xx pins" absolute maximum 4.0 V, not VDD-relative (Table 109 p.207); note 3 of Table 110: "Positive injection is not possible on these I/Os and does not occur for input voltages lower than the specified maximum value" | yes: Rev 10 Tables 21, 22 (rev Y) and 119, 120 (rev V) | same | MATCH, and silicon revision V or X avoids erratum 2.2.14 (F1) |
| FT pins on the kit bus while a controller is dark | the bus is not loaded by a dark controller | FT_xxx absolute maximum Min(Min(VDD..) + 4.0, 6 V), so 4.0 V at VDD = 0, and no positive injection (Tables 109, 110) | yes | same | MATCH |
| Pull-down strength on the 21 controller outputs (100 k today, 10 k owed by FAB-04) | a dark or resetting controller presents high impedance | "During and just after reset, the alternate functions are not active and most of the I/O ports are configured in analog mode" (RM0433 Rev 8 p.533); TT_xx and FT_xx leakage +-250 nA, FT_u +-350 nA (Table 147 p.241) | yes (Table 60 / Table 157) | same | MATCH; the value is FAB-04's, not this page's |
| Supply range and brownout | runs from a 3.3 V LDO; resets cleanly as it falls | 1.71 to 3.6 V on LQFP100; BOR thresholds: VBOR0 1.58 to 1.68 V falling, VBOR3 2.54 to 2.68 V falling, PVD levels to 2.94 V (Table 116 p.212) | yes | same | MATCH; BOR level is a provisioning choice (HC6-SC-5) |
| Output drive | LED at about 1.3 mA; voter inputs (CMOS) | 20 mA per pin, 140 mA total (Table 110) | yes | same | MATCH |
| Thermal grade | inside air 51 C worst | TA to +85 C (suffix 6), TJ to +125 C | yes | same | INSIDE |

## 5. Peripherals and features, and what the H753 adds

| Feature | Used by the design | H743 source | H753 | Verdict |
|---|---|---|---|---|
| FDCAN1 and FDCAN2 (two independent heartbeat fabrics) | yes, both | DS12110 p.2: "2x CAN controllers: 2 with CAN FD, 1 with time-triggered CAN (TT-CAN)"; RM0433 section 56.2 p.2462 (ISO 11898-1:2015, CAN FD up to 64 bytes; TTCAN on FDCAN1 only); one shared 10 Kbyte message RAM (p.2459, p.2464; 2560 words, p.2473) | same peripheral | MATCH. Firmware: at or below 1 Mbps (the TCAN334D is a 1 Mbps part, SLLSEQ7F Device Comparison, FAB-05), which means classic CAN or CAN FD without bit-rate switching; revision V or X only (ES0392 2.24.2, F1) |
| FDCAN kernel clock from the 25 MHz HSE | yes ("CAN-FD bit timing needs a crystal, not the HSI", `gen_sch_b.py:1150`) | FDCANSEL = 00 selects hse_ck, "default after reset" (RM0433 p.412) | same | MATCH: 25 MHz gives 25 time quanta per bit at 1 Mbps with prescaler 1 |
| I2C1 as a target on the kit bus | yes (status reads by the panel; addresses 0x34, 0x35, 0x36 under I3-F01) | DS12110 p.2: "4x I2Cs FM+ interfaces (SMBus/PMBus)"; RM0433 section 47.2 p.1950: target and controller modes, 7-bit addressing, "Multiple 7-bit slave addresses (2 addresses, 1 with configurable mask)", optional clock stretching; kernel clock I2C123SEL default rcc_pclk1, alternatives pll3_r, hsi_ker, csi_ker (p.415); minimum i2c_ker_ck 8 MHz for Fast mode with the analog filter (Rev 11 Table 192 p.298) | same | MATCH, with the errata obligations of section 6 (F2) |
| GPIO (voted outputs, heartbeat and read-back inputs, LED) | yes | Table 9; reset state analog (RM0433 p.533) | same | MATCH |
| Independent watchdog (IWDG) | yes, the controller's only watchdog (`gen_sch_b.py:1093`) | DS12110 p.2 "2x watchdogs (independent and window)"; LSI clocked, "stays active even if the main clock fails" (RM0433 p.1894); hardware start by option byte IWDG1_SW = 0 (p.179, p.214) | same | MATCH (HC6-SC-4) |
| Window watchdog (WWDG) | no | ES0392 2.2.23: not functional below VDD 2.7 V at VOS0 or VOS1, no workaround | same | not used; stays unused |
| SWD debug | yes, SMD pads per controller | DS12110 p.2 "SWD & JTAG interfaces"; PA13/PA14 AF0 | same | MATCH |
| System bootloader | not used in service (BOOT0 to GND) | Rev 11 section 3.4 p.27 now lists FDCAN, USART, I2C, SPI and USB-DFU for the bootloader; entered only through BOOT_ADD1 with BOOT0 high, or a firmware jump | same | not used; a field update path over FDCAN is available if the firmware stage wants one |
| Flash protection for software-verified boot (D-13): readout protection, write protection, PCROP | yes, the D-13 floor | DS12110 p.1 "Security: ROP, PC-ROP, active tamper"; RM0433 sections 4.5.2 write protection p.183, 4.5.3 RDP p.184, 4.5.4 PCROP p.189 | same, plus secure access mode | MATCH on revision V or X (ES0392 2.2.8 PCROP may be unprotected on revision Y) |
| CRC unit and true random number generator | available to firmware (image check, nonces) | DS12110 p.1 "CRC calculation unit", p.2 "True random number generators (3 oscillators each)" | same | available; not required by any record |
| **CRYP** (AES 128/192/256, DES, TDES) | **no** | not present: RM0433 Rev 8 Table 2 p.103, "Cryptographic processor (CRYP) ... Not available" on STM32H742xI/G and STM32H743xI/G | DS12117 p.2 "Cryptographic acceleration: AES 128, 192, 256, TDES"; section 3.28 p.41 | no dependence |
| **HASH** (MD5, SHA-1, SHA-2, HMAC) | **no** | not present (RM0433 Table 2) | DS12117 p.2 "HASH (MD5, SHA-1, SHA-2), HMAC" | no dependence; D-13's verified boot hashes in software |
| **Secure access mode, root secure services (RSS), flash secure-only area, secure firmware install** | **no** | not present (RM0433 Table 2; DS12110 revision history "Removed secure firmware upgrade support") | DS12117 p.1 "secure firmware upgrade support, Secure access mode", section 3.3.2 p.25; RM0433 section 5.3 p.247 | no dependence; a hardware root of trust is D-13's production trigger, not a prototype requirement |

**Where a dependence was looked for.** `v2/ecad/tools/pcb_requirements.yaml` (CON-017, S-41, D-13), `v2/docs/CONOPS.md`
D-13 row, `v2/docs/V2-SPEC.md` lines 34 and 135, `v2/docs/ARCHITECTURE.md` 5.5 and 10.3,
`v2/docs/ARCH-PCB-B-IOHA.md` sections 6 and 10a, `v2/docs/feasibility/ZEROIZE.md` (section 7, "This design uses no
supervisor function at all: the panel RP2040, the ATECC608B and the modules' LUKS do the whole job", and rule Z-C3),
`v2/docs/feasibility/FAILOVER-FABRIC.md` section 4.9, and every `gen_sch_*.py`: no requirement, generator line or
feasibility page asks a supervisor for CRYP, HASH, secure access mode, RSS or a secure-only flash area. ZEROIZE
destroys a key the ATECC608B holds; the supervisors only have to leave the bus alone (Z-C3, residual R7).

## 6. Errata that touch what the design uses (ES0392 Rev 15)

| Erratum | Status by silicon revision Y,W / X / V (Table 3) | Design effect | Obligation, and where it lands |
|---|---|---|---|
| 2.24.2 Wrong data may be read from message RAM by the CPU when using two FDCANs; workaround none | N / - / - | both fabrics would be unreliable on Y or W parts | revision V or X only: goods-in marking check (ASSEMBLY) and a REV_ID check at boot that refuses to run both fabrics on 0x1003 (firmware). HC6-SC-1 |
| 2.24.3 Desynchronisation with edge filtering enabled | A / A / A | first bit of a frame mis-sampled, error frame | firmware leaves EFBI cleared (edge filtering off) |
| 2.24.4 Tx FIFO messages inverted with a dedicated Tx buffer and FIFO mixed | A / A / A | heartbeat order | firmware uses the Tx FIFO or queue alone (TFQM consistent) |
| 2.24.5 DAR mode transmission failure due to lost arbitration | A / A / A | only in DAR (no automatic retransmission) mode | firmware does not use DAR |
| 2.19.3 Wrong data sampling when tSU;DAT is shorter than one I2C kernel clock period | P / P / P | a misread address, byte or ACK on the kit bus | I2C kernel clock at least 10 MHz in Fast mode, 4 MHz in Standard mode (the erratum's own figures); HSI (64 MHz) through I2C123SEL = 10 meets both with margin |
| 2.19.6 Spurious controller transfer upon own target address match | P / P / P | only if the supervisor also acts as a controller on the kit bus | firmware never masters the kit bus (it is a target only, which Z-C3 also requires) |
| 2.19.9 Transmission stalled after first byte transfer (target mode, clock stretching on) | A / A / A | **a stalled target holds SCL and stops every device on the kit bus**, including board A's expanders and the secure element | firmware writes the first byte into I2C_TXDR before the transfer starts and keeps the APB to kernel clock ratio outside 1.5 to 3 (the erratum's workaround); a stuck-bus recovery on the panel side is already a controller duty |
| 2.19.10 SDA held low upon SMBus timeout expiry in target mode | A / A / A | a stuck SDA if SMBus timeouts are used | firmware does not enable the SMBus timeout in target mode, or applies the erratum's PE reset sequence |
| 2.2.8 PCROP-protected areas may be unprotected | A / - / - | D-13's verified boot | revision V or X (F1) |
| 2.2.14 Unexpected leakage current on I/Os when VIN higher than VDD | A / - / - | the dark-controller case (IOHA A4, A6) | revision V or X (F1) |
| 2.2.21 480 MHz not available on Y and W | P / P / P | none: the supervisors are bounded well below 400 MHz by their LDO (PWR-F04) | none |
| 2.2.23 WWDG not functional below VDD 2.7 V at VOS0/VOS1 | N / N / N | none: the design uses the IWDG | keep the WWDG unused |

## 7. The HSE crystal against the oscillator criterion

DS12110 Rev 11 Table 131 p.229: HSE 4 to 48 MHz, maximum critical crystal transconductance **Gmcritmax 1.5 mA/V** at
start-up. The criterion (ST AN2867, cited by the same table's note) is gm_crit = 4 x ESR x (2 pi F)^2 x (C0 + CL)^2
at or below Gmcritmax. The board draws 18 pF on each side (`gen_sch_b.py:1152`), so CL = 9 pF + stray, which is 12 pF
at 3 pF stray. Board B's other 25 MHz crystal, Y1 on the KSZ9897R, takes the same part and must also meet Microchip's
Table 6-12 (ESR at most 50 Ohm, +-50 ppm, drive 100 uW; `v2/vendor/cluster/ksz9897.pdf`, DS00002330E p.181).

| Crystal | Maker's sheet (as served by LCSC) | ESR max | C0 max | CL | gm_crit | Against 1.5 mA/V | KSZ9897 Table 6-12 | Stock |
|---|---|---|---|---|---|---|---|---|
| C164047 Yajingxin TAXM25M4RFBCCT2T (fitted) | YJX specification, issue 2026-08-26, sha256/16 `cf02a0872e39ea73` | 30 Ohm | 3 pF | 12 pF | 0.67 mA/V | margin 2.25 | ESR 30, +-10/+-20 ppm: meets | 3 (JLCPCB, 2026-09-26): NO_STOCK |
| C9006 YXC X322525MOB4SI (YSX321SL family) | YXC YSX321SL sheet, sha256/16 `7bc18549e407d8e3` | 50 Ohm (16 to 31 MHz) | 3 pF | 12 pF | 1.11 mA/V | margin 1.35 | ESR 50 at the limit, +-10/+-20 ppm, drive to 200 uW: meets | 165,557 (JLCPCB 00:04Z) / 60,575 (LCSC 00:05Z), basic library |
| C91750 Seiko Epson X1E0000210139 (TSX-3225) | Epson TSX-3225 sheet, sha256/16 `4e9c0baa33e30d2d` | 40 Ohm (21 to 48 MHz) | not stated; 3 pF assumed | 12 pF | 0.89 mA/V (at 3 pF) | margin 1.69 | ESR 40, +-10 ppm: meets | 5,870 (LCSC 00:05Z) |

LCSC's parametric data for C164047 says "ESR 80 Ohm" and "+-50 ppm" where the maker's sheet says 30 Ohm and +-20 ppm:
a distributor's transcription is not the part's specification, which is why this table reads the sheets.
Pin assignment: the YXC sheet's "Top View Crystal Connection" puts the crystal on pads 1 and 3 and GND on 2 and 4, the
`Crystal_GND24` symbol's assignment. The drive level the H743's oscillator applies is not stated by ST as a number;
it is a bring-up measurement (AN2867 method), allocated to PROTOTYPE, and both candidate sheets rate the crystal to
at least 100 uW. **HC6-SC-3:** replace C164047 on Y1 to Y4 with C9006 (every parameter the criterion needs is on its
maker's sheet, basic library, deep stock), C91750 as the stated alternate; the generator line is board B's author's
(`drafts/hc6/README.md` carries the recommendation). Reverse by keeping C164047 if JLCPCB restocks it before order.

## 8. What stays open, and why at that stage

- **CON-017 clause (4), the firmware build.** No supervisor firmware exists (CON-017 evidence). The build proves the
  toolchain targets the part and the peripheral configuration of sections 5 and 6 compiles and runs; it cannot change a
  pin, a land, a net or a part, because sections 3 to 5 settle those from ST's documents. It is therefore allocated to
  the firmware stage (earliest evidence PROTOTYPE, when the firmware and a board exist), not held at SCHEMATIC where it
  would block the schematic record on a deliverable the layout does not need (audit stage-gate cycle 2). Proposed as a
  registry change in `drafts/hc6/apply_registry.py` (CON-017 `final_phase: PROTOTYPE`, S-41 narrowed to the build).
- **Silicon revision at goods-in** (F1): ASSEMBLY, a marking read on the delivered parts; before that, the purchase
  instruction in `PROCUREMENT.md` names the constraint.
- **Firmware contract items** (sections 5 and 6): FDCAN at or below 1 Mbps, EFBI off, one Tx mode, no DAR; I2C target
  at 0x34 to 0x36, never a controller, kernel clock at least 10 MHz, first byte preloaded, no SMBus timeout; IWDG in
  hardware mode; BOR level; PC5 input only; REV_ID check at boot. These belong in the supervisor firmware specification
  when it is written (`ARCHITECTURE.md` 10.4 lists the open contract items).

## 9. Session choices taken on this page (standing rule of 26 September 2026)

Each is the session's, taken because no owner judgement is standing and the recommendation follows from the documents;
none changes a requirement, a function or a protection.

| Id | Choice | Why | Reversal |
|---|---|---|---|
| HC6-SC-1 | The supervisors are bought and accepted only as silicon revision V or X; the firmware reads REV_ID at boot and refuses to run both FDCAN fabrics on revision Y or W | ES0392 2.24.2 has no workaround and the design uses both FDCANs; 2.2.8 and 2.2.14 touch D-13 and IOHA A4 | if ST withdraws 2.24.2 for revision Y in a later ES0392, or if one fabric is dropped (which would lower NEED-03's two-path requirement and is not proposed) |
| HC6-SC-2 | The kit-bus target obligations of section 6 (2.19.3, 2.19.6, 2.19.9, 2.19.10) join the supervisor firmware contract | a stalled target would stop the kit bus, which carries power control and ZEROIZE's secure element | if the supervisors leave the kit bus (IOHA's reversal of I3-F01: a separate supervisor bus) |
| HC6-SC-3 | Y1 to Y4 move from C164047 to C9006 (YXC X322525MOB4SI), C91750 (Epson X1E0000210139) as alternate | C164047 is NO_STOCK; C9006 meets both the H743 criterion (1.11 mA/V against 1.5) and the KSZ9897's ESR limit on its maker's sheet | keep C164047 if restocked; take C91750 if C9006's margin (1.35) is judged thin by the qualified review |
| HC6-SC-4 | The IWDG starts in hardware (IWDG1_SW = 0) and runs in Stop and Standby (IWDG_FZ_STOP = IWDG_FZ_SDBY = 1), set at provisioning | the IWDG is each controller's only watchdog (`gen_sch_b.py:1093`); a software start leaves a window before the firmware arms it | software start, if a bring-up tool needs the controller to sit halted without resets |
| HC6-SC-5 | BOR level VBOR3 (2.54 to 2.68 V falling) | the private rail is 3.3 V and the TCAN334D is specified from 3.0 V (SLLSEQ7F Recommended Operating Conditions); the highest BOR keeps the core out of the region where the transceiver is outside its range, and the transceiver's own VCC undervoltage protection covers the gap | a lower BOR level if bring-up shows resets on load steps the rail rides through |
