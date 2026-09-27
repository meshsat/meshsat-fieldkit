# W5 draft: the hardware and firmware contract of the V2 field kit (round 2)

Workstream W5 of MESHSAT-1357. Round 1 written 25 September 2026 against `e6291404`; this round 2 written 26 September
2026 (00:10 CEST) against `main` at `82dd1e4d`. The six schematic generators are byte-identical between the two commits (`git diff e6291404 82dd1e4d --
v2/ecad/tools/gen_sch_*.py` is empty), so every generator line number below holds at both. **Draft for the integrator,
not a ruling.** Prototype design: nothing here has been built, powered or measured. Every statement is marked
**VERIFIED** (the artefact was read: a generator line, a netlist, a datasheet clause), **INFERRED** (reasoned from verified
facts, not measured) or **PLAUSIBLE** (a mechanism that holds on the verified topology but rests on a parameter no held
document bounds). A number that no held document gives is **TBD** with its effect stated. Nothing here is a
certification.

Round 2 applies the adjudications A01 (expander power-up), A02 (charger without a host), A07 (pack SMBus lead) and A11
(what EMCON does to each radio), and fixes every defect the W5 challenger raised. Section 9 maps each defect to its fix.
Finding IDs are now `W5-Fn` everywhere, and the test IDs in `v2/docs/TEST-PLAN.md` section 7 are `HWn`, so the two
numberings no longer collide.

## 0. Sources read

| source | identity |
|---|---|
| `gen_sch_a.py`, `gen_sch_b.py`, `gen_sch_c.py`, `gen_sch_d.py`, `gen_sch_e.py`, `gen_sch_p.py` | at `82dd1e4d`, unchanged since `e6291404`; sha256 prefixes 02271970ab6a, 37d958e6851c, 547ad39ae051, f1fef1594efd, 5cf0b323d51c, 0d2b0aae207a |
| committed netlists | `pcb-a-power-a23/out/pcb-a-power.net` (last commit `0d1e2ef6`), `pcb-p-pack-p2/out/pcb-p-pack.net` (`a0b707f9`), `pcb-e1-dock-e7/out/pcb-e1-dock.net` (`824ec9d4`); read by the adjudicators (A01, A02, A07) and, for Q1 and KILL, here |
| regeneration parity | A11 regenerated A, B and D on the box at `82dd1e4d`: connectivity identical to the committed netlists, 0 named nets differing (A 282, B 1852, D 172 nets). C by generator sha only. This contract relies on that for A, B and D (condition 5) |
| STM32H753xI datasheet | `vendor/st/st-stm32h753xi-datasheet.pdf`, DS12117 Rev 9 (March 2023), sha256 3bf346d8a511 |
| RP2040 datasheet | `vendor/rp2040/rpi-rp2040-datasheet.pdf`, build 3184e62 (2025-02-20), sha256 be56fbb75ba0 |
| CM5 datasheet | `vendor/cm5/cm5-datasheet.pdf`, Release 3, sha256 80070fefd8db |
| LTC2954 | `vendor/power/ltc2954.pdf`, marker 2954fb, sha256 1e9e2567d15e |
| TI TPS62933 | `vendor/ti/ti-tps62933.pdf`, SLUSEA4D (revised August 2022), sha256 16ec2eac43c7 |
| TI PCA9555 | `vendor/ti/ti-pca9555.pdf`, SCPS131J, sha256 9b5cc24c3c9e |
| Diodes AP64500 | `vendor/diodes/diodes-ap64500.pdf`, DS41979 Rev 5-2, sha256 d3bcdc7dd4ca |
| TI TPS2596 (TPS259631) | `vendor/power/tps2596.pdf`, SLVSET8A, sha256 66f6bae4494f |
| TI LM5176 | `vendor/ti/lm5176-datasheet.pdf`, SNVSAI1D, sha256 98191bec36d4 (as read by A01 and A11) |
| TI TPS22810 | `vendor/ti/ti-tps22810-load-switch.pdf`, SLVSDH0C, sha256 10450eedecbc |
| TI SN74LVC08A | `vendor/ti/ti-sn74lvc08a-quad-and.pdf`, SCAS283W, sha256 9cefbf42c72e |
| TI BQ25731 | `vendor/ti/bq25731-datasheet.pdf`, SLUSE66A, sha256 3e5e927fdf63; byte-identical to TI's current copy (A02) |
| TI BQ25730 (sibling, for the diff) | SLUSE65A, https://www.ti.com/lit/ds/symlink/bq25730.pdf, fetched 25 Sep 2026 by A02, sha256 e41ef289 |
| TI E2E thread 1316778 | "BQ25731 ChargeCurrent Start Up Behavior", TI expert reply 23 Jan 2024, fetched 25 Sep 2026 by A02 |
| TI BQ4050 | `vendor/battery/ti-bq4050.pdf`, SLUSC67B (revised October 2017), sha256 2664e33fe6d6 |
| Samsung INR18650-35E | `vendor/battery/samsung-35e-orbtronic.pdf`, Ver. 1.1 (9 July 2015), sha256 5ec577b952b9 |
| CJ 2N7002 (LCSC C8545, the code board B's `nfet()` helper names) | rev J, September 2016, fetched from datasheet.lcsc.com by A01, sha256 7941fb423af7; **held in the session scratchpad, not in `v2/vendor/`** |
| Microchip ATECC608B | `vendor/microchip/microchip-atecc608b-datasheet.pdf`, DS40002239A, **summary only**, sha256 519e2edac0de |
| Quectel RM520N hardware design | v1.0 (2022-07-15) and Series v1.1 (2023-03-16), section 4.4.1 |
| AsiaRF AW7915-AED | `vendor/wifi/`, "Last Updated: 04/22/2026", sha256 babcddfd36fe: silent on W_DISABLE |
| Linux mainline mt76 | torvalds/linux f14572c203d5 (25 Sep 2026), fetched whole by A11: no rfkill code in `mt7915/`; `mt7921` and `mt7925` poll the pin |

**Documents this contract needs and the tree does not hold (TBD, each narrows a firmware rule):** ST RM0433 (option
bytes, IWDG hardware mode, BOR levels), the BQ4050 Technical Reference Manual SLUUAQ3 (data flash, SEALED, SHUTDOWN,
the host watchdog), the ATECC608B full datasheet (NDA), a 2N7002 sheet in `v2/vendor/` for the parts actually fitted
(board A's Q1 and Q6 carry no LCSC code in the A23 netlist), the AW7915-AED W_DISABLE1# behaviour (AsiaRF), the RM520N
AT commands manual, the QMX supply arrangement.

## 1. The controllers and what each owns

| controller | where | powered from | reset | boot and recovery | watchdog | debug access | diagnostics it can give |
|---|---|---|---|---|---|---|---|
| 3 x Raspberry Pi CM5 (CM5108064, wireless) | B, U30A/B, U31A/B, U32A/B | slot rail `+5V_Sx` from A's AP64500 enabled by `SLOT_ENx` (gen_sch_a.py:426-428) | none on the carrier: PMIC_EN and PWR_BUT are NC (gen_sch_b.py:378-379, 570) | eMMC; `J_RPIBOOTx` jumper to GND plus `J_FLASHx` USB-C device port for rpiboot (gen_sch_b.py:567-569) | SoC watchdog in the OS (INFERRED: the held CM5 datasheet does not mention one); the panel controller watches `HBx` (PANEL.md section 5); the IOCTRL quorum watches `HBx` for bank failover | `J_DBGx` 1x5: GND, UART0 TX/RX, module I2C (gen_sch_b.py:571) | LED_nACT and LED_nPWR, heartbeat GPIO16 to `HBx`, console UART0 |
| 3 x STM32H753VI I/O supervisors IOCTRL-A/B/C (**part bought is STM32H743VIT6: an open component mismatch, condition 1**) | B, U41/U51/U61 | private AP2112K-3.3 off `+5V_DEV` each (gen_sch_b.py:803-806) | RC only: 10k to own 3.3 V, 100 nF (gen_sch_b.py:831) | BOOT0 10k to GND (gen_sch_b.py:832): flash boot; the ST system bootloader is reachable only by SWD or by a jump from application firmware | IWDG and BOR only, by design (gen_sch_b.py:794-797) | 5-pad SMD SWD land: 3V3, SWDIO, SWCLK, NRST, GND (gen_sch_b.py:840-841). No SWO, no UART | green LED on PB0, two CAN-FD fabrics, read-back of four voted bits (PE8..PE11), status on the kit I2C bus (**not achievable as wired, W5-F3**) |
| RP2040 panel controller | C, U3 | C's TLV75533 from `+5V` = `PANEL_5V` = B's F1 off `+5V_DEV` (gen_sch_b.py:757, gen_sch_c.py:98-102) | RUN 10k pull-up, TP3 (gen_sch_c.py:118, 122) | QSPI W25Q16; BOOTSEL by solder jumper JP1 (gen_sch_c.py:119); USB bootloader over bank 1 | RP2040 watchdog, software-configured | TP1 SWCLK, TP2 SWDIO, TP3 RUN; GND TP8 (gen_sch_c.py:122, 244) | LED_STAT D18, USB CDC and HID, every switch and hardware line read back (PANEL.md section 11) |
| RP2040 sensor controller | E, U10 | AP63205 whose EN is tied to CELL_F: always on while the pack is connected (gen_sch_e.py:90) | RUN 10k, TP12 | QSPI W25Q16, BOOTSEL solder jumper JP1 (gen_sch_e.py:361) | RP2040 watchdog | TP10 SWCLK, TP11 SWDIO, TP12 RUN; GND TP4 | LED2, USB (bank 3 via A's J_DOCK), fan tachometers, water, climate, **the pack gauge on pins 4 and 5 = GPIO2 and GPIO3 = the RP2040's I2C1 block** although the nets are named SDA0/SCL0 (A07; W5-F9) |
| BQ4050 gauge and protector | P, U1 | the cell block (BAT, PBI, VCC) | internal; SHUTDOWN and start-up thresholds per SLUSC67B electrical characteristics | ROM firmware, data flash configured at pack build (TRM not held) | AFE watchdog (SLUSC67B 6.8); a "Host Watchdog Timeout Protection" feature (SLUSC67B 7.3.1), configuration TBD (W5-F18) | TP1..TP10 incl. BTP_INT, CHG_R, DSG_R, SMBC, SMBD (gen_sch_p.py:173) | SMBus status, lifetime data, permanent-failure flags |

**Other devices whose configuration is firmware and must be owned by someone** (VERIFIED as placed; owners are
proposals): the BQ25731 charger (kit I2C target at 0x6B, volatile registers, its own 175 s watchdog, W5-F10), the six
INA226 monitors and the three output PCA9555 (A's U27 and U28, B's U6; W5-F1), the KSZ9897R, the ATECC608B, four
CP2102N bridges, two E72 CC2652P radios (in-system flash through the CP2102N RTS to RESET_N and DTR to DIO_15, plus a
cJTAG header each: gen_sch_b.py:686-692), the RM520N and AW7915 modules, the LimeSDR, the QMX, the SA868, the RockBLOCK
9704.

## 2. Power-control states, from the netlist

Labels are `PC-n` (power control). They are sequence states, not the load states: A05 names those `PS-*` (PS-OFF,
PS-IDLE and so on) and W1 keeps S1 to S5 for its simultaneity cases, so no label here collides with either. The boot
sequence matches A01's S0 to S4.

| state | how it is entered | what is alive and at what level (VERIFIED from the generators unless marked) |
|---|---|---|
| PC-0 pack connected, kit off | pack fitted, MAIN not pressed | BQ4050 (P); LTC2954 U1 on VBAT (6 to 12 uA, 2954fb); the sensor RP2040 (gen_sch_e.py:90). U1 holds RAIL_EN low, so A's `+3V3` is off and U27/U28 are unpowered; CHG_INHIBIT is held low by R21 (gen_sch_a.py:348), so the charger is not in HiZ, but a host-free charger does not usefully charge (W5-F10). **KILL already sits at VBAT through R4 (W5-F15)** |
| PC-1 MAIN held | MAIN held 26 to 41 ms (tDB,ON, 2954fb) | U1's open-drain EN releases and R2 pulls RAIL_EN to VBAT, **over the TPS62933's 6 V EN absolute maximum (W5-F15)**; U12 brings up A's `+3V3`; the KILL blanking (400 to 650 ms) starts |
| PC-2 expanders out of reset | A's `+3V3` up | U27 and U28 come out of power-on reset as inputs with internal pull-ups, output registers FFh (SCPS131J). Per A01 (INFERRED nominal): DEV_EN about 1.7 V against the AP64500's 1.25 V max, **nominally ON, not guaranteed**; MON_EN, HEAT_EN, D8_EN about 1.66 V, nominally ON, but U21 and U22 conduct only while VBAT is below about 12.9 to 13.4 V (their OVLO dividers, a W2 finding); POE_EN and PD_EN OFF (0.30 V nominal, 0.74 V worst, below the LM5176's 1.17 V); PA_SW_EN and HF_SW_EN about 1.9 V, inside the LVC08's undefined band; CHG_INHIBIT about 1.66 V inside the 2N7002's 1.0 to 2.5 V threshold spread, erring toward HiZ; SLOT_EN1..3 OFF, guaranteed |
| PC-3 device rail up | DEV_EN nominally on | `+5V_DEV` soft-starts (4 ms); D8's 5 V, B's `+3V3_DEV` and U6 (same pattern: LIME_SW_EN, RB_SW_EN, LORA_ON, ZB_ON, CAM_EN undefined; KSZ_RST, 5G_OFF, 5G_RESET nominally asserted; WL_nDIS1..3, BT_nDIS1..3, RB_IEN, RB_CTRL high through the internal pull-up into unpowered loads); `PANEL_5V`, C's LDO, the panel RP2040 boots; EMCON_HW goes high if the toggle is released (U9). From here until the panel firmware writes U27, PA_EN and HF_EN are undefined (A01) |
| PC-4 panel firmware takes the bus | panel firmware running | the boot order of section 6. **With no panel firmware (blank, crashed, BOOTSEL) the kit stops at PC-3 with no module running** (A01) |
| PC-5 run | SLOT_EN1..3 driven high | slots, modules, bank fabric, radios per their enables |
| PC-6 clean shutdown | MAIN tap (INT low from tDB,OFF 26 to 41 ms) or the PI button through the panel controller | `PI_SHDN_REQ` reaches every module (level stages, gen_sch_b.py:574); the panel waits for heartbeats to stop, then drives `PI_KILL` high, Q1 pulls KILL low and U1 releases EN (gen_sch_a.py:173). DEV_EN is never written 0 before this last step (A01) |
| PC-7 forced off | MAIN held longer than tPD,MIN + tPDT | tPD,MIN is 52 to 82 ms with PDT floating (gen_sch_a.py:171, pin 7 NC): an ordinary press forces the kit off with no shutdown (W5-F2) |
| PC-8 slot power-cycle | panel drops `SLOT_ENx` | module and its card rails off; the bank moves to its neighbour (IOHA) |
| PC-9 panel absent, in reset or in BOOTSEL | ribbon out, C unpowered, RP2040 in reset | `SLOT_EN1..3` held low by A's 100k and the RP2040 pad pull-downs: no module runs (W5-F4). **If slots were powered when the panel reset, the decaying slots can lift PI_KILL and switch the whole kit off (W5-F5, PLAUSIBLE)** |
| PC-10 supply lost and returned | pack removed or swapped, a BQ4050 discharge trip, VBAT below U1's UVLO (2.2 to 2.5 V falling, 2954fb) | "When power is first applied to the LTC2954, the part initializes the output pins. Any DC/DC converters connected to the EN pin will therefore be held off" (2954fb, Turn On): **the kit stays off until MAIN is pressed** (W5-F17). Whether shore keeps VBAT above the UVLO after a pack trip is TBD |

## 3. Findings (each a contract item; severity is the workstream's proposal)

**W5-F1, major, INFERRED (nominal levels per adjudication A01; topology and datasheet numbers VERIFIED). No expander-driven
enable has a designed power-up state: the device rail comes up only by an unspecified parameter, and five lines sit in
undefined bands.** The fitted part is the TI PCA9555PWR (LCSC C2864778), which "is identical to the PCA9535, except for
the inclusion of the internal I/O pullup resistor" (SCPS131J 8.1); the I/O diagram draws 100 k (Fig 8-2); IIL is given
only as a maximum of -100 uA at 0 V, with no minimum (6.5). Against the 100 k pull-downs the power-up levels are (A01,
node_calc): **DEV_EN** 1.71 V nominal (1.87 V at the ICC-implied 82 k) against the AP64500's VEN_H 1.25 V max, ON
unless the internal pull-up is weaker than about 181 k, which no datasheet limit excludes: **nominally ON, not
guaranteed**. **MON_EN, HEAT_EN, D8_EN** 1.66 V, nominally ON. **POE_EN and PD_EN** (U28 pin 13, gen_sch_a.py:547, which
round 1 missed) OFF: the collapsed LM5176 divider leaves R75 or R134 (10 k) in parallel, so each node is 0.30 V nominal
and 0.74 V at the IIL bound, below the LM5176's VEN(OP) minimum 1.17 V (SNVSAI1D); at the high end the stage may sit in
standby. Round 1's "the PoE boost runs at power-up" is withdrawn. **PA_SW_EN, HF_SW_EN** about 1.9 V and
**CHG_INHIBIT** about 1.66 V: undefined (LVC08 VIH 2.0 V, VIL 0.8 V; 2N7002 Vth 1.0 to 2.5 V), CHG_INHIBIT erring toward
the charger in HiZ. **SLOT_EN1..3** OFF, guaranteed. On B's U6 (gen_sch_b.py:740-743) LIME_SW_EN, RB_SW_EN, LORA_ON,
ZB_ON and CAM_EN are undefined; KSZ_RST, 5G_OFF and 5G_RESET nominally assert; WL_nDIS1..3, BT_nDIS1..3, RB_IEN and
RB_CTRL (round 1 missed the last two) have no pull-down and go high. B's comment (gen_sch_b.py:729-733) assumes the
PCA9535's "high-impedance inputs". **Nothing but the panel can write U27**: the only master on the kit bus is C's RP2040,
which itself runs from `+5V_DEV` (A01 item 3). **Fix, engineering, the session's (A01):** (a) re-terminate R42 from GND
to A's `+3V3` (a per-stage `rpg` argument to `buck5` at gen_sch_a.py:407, stage D at :429): DEV_EN then sits at 3.33 V
whenever MAIN has enabled `+3V3`, whatever the internal pull-up, and the panel can still shed the rail by driving the pin
low; (b) change the other pull-downs from 100 k to 4.7 k (A: R21, R103, R104, R111, R112, R113; B: R48, R50 to R53,
optionally R60 to R62): worst case 0.49 V, below every OFF threshold, at 0.71 mA per line driven high; (c) a PCA9535 on
U27, U28 and U6 is the alternative to (b) only: it is a part substitution and a mismatch until proven (no datasheet held,
JLC code TBD), and **it must come with (a)**, because a PCA9535 with R42 still to GND is a hard deadlock (EN at 0.1 to
0.2 V, below VEN_L 1.03 V, and no master). If W2 changes the LM5176 EN/UVLO dividers (its F-SQ-04), re-check POE_EN and
PD_EN: the 10 k that holds them off today is part of that divider. Firmware contract in section 6. Rules: SCH-004,
PWR-002 ("bounded by design rather than by luck"). The recorded `inhibit_chain_a/b` verdicts (RF-002, PASS 18 Sep) check
that each pull-down exists, not what it wins against. Test: HW1.

**W5-F2, major, VERIFIED. MAIN forces the kit off on an ordinary press.** LTC2954 pin 7 (PDT) floats (gen_sch_a.py:171),
so EN releases after tPD,MIN = 52 to 82 ms of PB held low (2954fb electrical table), before any module can shut down. A
clean shutdown needs a press longer than tDB,OFF (26 to 41 ms) and shorter than tPD,MIN: in the worst case a window of
about 11 ms. Recommendation: a PDT capacitor from the sheet's formula CPDT = 1.56e-4 uF/ms x (tPDT - 1 ms): 0.47 uF for
about 3 s, 0.78 uF for about 5 s; PANEL.md then states the hold time. Test: HW4.

**W5-F3, major, VERIFIED. The supervisors' I2C status path cannot use an I2C peripheral as wired.** ARCH-PCB-B-IOHA
section 6 gives the three supervisors kit-bus addresses 0x30 to 0x32; the generator lands SDA and SCL on pins 35 and 36
(gen_sch_b.py:824), which are PB1 and PB2 (gen_sch_b.py:261). DS12117 Rev 9 Table 10 gives neither an I2C function.
Free I2C-capable pins: PB6/PB7 (pins 92/93, I2C1 or I2C4) and PB10/PB11 (pins 46/47, I2C2). Recommendation: SDA to PB7,
SCL to PB6. Also VERIFIED: PD0/PD1 carry FDCAN1_RX/TX and PB12/PB13 carry FDCAN2_RX/TX. Condition 1: read on the H753
sheet; the H743 comparison is W6's.

**W5-F4, major, VERIFIED (wiring and pad reset), INFERRED (firmware reach). A kit without its panel does not compute,
and a panel reset that restores the pads powers off all three modules.** `SLOT_ENx` have only a 100 k pull-down on A
("a slot with no controller line stays off", gen_sch_a.py:407) and the RP2040 pads reset with the pull-down enabled
(PADS_BANK0 PDE reset 0x1). ARCH-PCB-B-IOHA already names the ribbon as a whole-kit control failure (section 10, and
FMEA row 12: "unmitigated common mode"); this finding adds the controller's own resets to it. Scope, narrowed from round
1: (i) the ribbon out, C unpowered, the RP2040 held in RUN or entering BOOTSEL all drop every slot rail; (ii) a watchdog
reset drops them only if the firmware lets the watchdog reset the pads: PSM WDSEL and RESETS WDSEL exist (reset value 0),
so the firmware can exclude PADS_BANK0, IO_BANK0 and SIO (whether the SDK's start-up code then resets IO_BANK0 anyway is
TBD, a firmware check); (iii) a panel firmware update **through the ROM USB bootloader** cannot be driven from a module,
because entering BOOTSEL powers that module off. **An in-application update** (the running firmware writes the new image
to flash and reboots with the pads preserved) is not blocked by the hardware; the module is power-cycled only if the final
reboot resets the pads. Options: (a) keep "no panel, no compute", update the panel by SWD or in-application only, and
configure the watchdog to preserve the pads; (b) make `SLOT_ENx` default ON (pull-up on A, the controller drives low to
turn a slot off), which only becomes safe after W5-F5 is fixed; (c) a latch on A that holds the last commanded slot state
across a controller reset. Recommendation: (a) now, because it needs no board change, and (b) or (c) decided together with
W5-F5, since the three modules exist to remove single points of failure (appendix 32.52) and the panel controller is one.
Engineering under the 21 September ruling unless the owner wants "no panel, no compute" as a product property. Test: HW5.

**W5-F5, major (raised from minor), PLAUSIBLE. A powered compute slot can switch the whole kit off through PI_KILL
whenever the panel is not actively driving PI_KILL low.** Topology, VERIFIED: each slot's `level()` stage
(gen_sch_b.py:309-312, :575) is a 2N7002 with its gate on the module's 3.3 V, its source on `PI_KILL_CMs` with a 10 k
pull-up to that rail, and its drain on `PI_KILL`; the body diode points from the module side into `PI_KILL`. On A,
`PI_KILL` is held only by R5 100 k (gen_sch_a.py:173), plus the panel RP2040's 50 to 80 k pad pull-down while its GPIO19
is not driven, and it is the gate of Q1, which pulls KILL low (A23 netlist: Q1.3 on KILL with R4 and U1.8). With
nothing driving `PI_KILL`, one to three powered slots lift it to about 2.0 to 2.9 V (drafts/r2calc/pi_kill_backdrive.out;
the body-diode drop at microamps, 0.3 to 0.7 V, is an assumption), against Q1's 1.0 / 1.6 / 2.5 V threshold (CJ 2N7002,
C8545; Q1's own part code is TBD). Q1 needs to sink only about 168 uA to take KILL under its 0.6 V threshold, and a KILL
low longer than 30 us releases EN (2954fb). The 400 to 650 ms KILL blanking protects only the first half second after
power-on. **Windows today:** (1) a panel watchdog or RUN reset while modules run, when the pads reset and the slot rails
decay; (2) a panel firmware that raises any `SLOT_EN` before it has made GPIO19 a push-pull low output; (3) if W5-F4
option (b) were taken, every panel reset. The same stage shape on `EMCON_HW` (Q106/Q206/Q306, gen_sch_b.py:472, 480, 498)
and `PI_SHDN_REQ` stays masked: EMCON_HW is driven push-pull by C's U9 whenever the panel is present and every slot is
off when it is absent, and lifting `PI_SHDN_REQ` moves it toward "no request". **Firmware rule:** GPIO19 is a push-pull
output driven low before the first `SLOT_EN` goes high, never tri-stated or made an input while any slot is powered.
**Hardware options (engineering, the session's):** (a) replace each `PI_KILL` level stage by a unidirectional buffer
with Ioff powered from the module side (74LVC1G34 class, input on `PI_KILL`), so a module can never drive the net;
(b) a much stronger pull-down on `PI_KILL`: at least 1.0 k to hold it under Q1's 1.0 V minimum threshold with three
slots up (the panel then sources 3.3 mA to kill). Recommendation (a). Tests: HW3, HW5.

**W5-F6, major, VERIFIED. `PI_SHDN_REQ` has two drivers of opposite sense.** The LTC2954's INT is an open-drain output
that asserts LOW for a shutdown request, pulled up by A's R3 100 k (gen_sch_a.py:171-172; 2954fb pin functions). The
same net is the panel's GPIO18 (gen_sch_c.py:113), which PANEL.md:51 (section 3, the pin map) drives "high for 200 ms".
No document fixes the sense the module software reads, so both readings are stated: (i) if the modules read low as a
request, the only sense the LTC2954 can produce, then the panel's idle low is a permanent request while it runs; (ii) if
they read high as the request, as PANEL.md implies, then a MAIN tap (INT low) is invisible to them and the LTC2954's own
request path is lost. Either way a push-pull driver sits on an open-drain active-low net. While the RP2040 is in reset its
pull-down against R3 leaves the line at about 1.1 to 1.5 V. **Contract:** `PI_SHDN_REQ` is ACTIVE LOW everywhere; the
panel never drives it high (output value 0, toggle the output enable; read it as an input to see MAIN taps). PANEL.md
line 51 changes (section 7 here); PANEL.md section 5 states no polarity and needs no change. Hardware recommendation: R3
to 10 k so the reset state reads a clean high. Test: HW7.

**W5-F7, major, VERIFIED. EMCON does nothing to the three CM5 radios, and the rule's PASS does not say so.** RF-002
requires "Every transmitter can be inhibited by a hardware path that does not depend on software" (pcb_rules.yaml);
appendix 32.50 item 3 says "EMCON kills every transmitter in hardware". WL_nDIS1..3 and BT_nDIS1..3 have exactly two
nodes each, the CM5 pin (89 or 91) and U6 (gen_sch_b.py:378, 743; A11 netlist read). The CM5 datasheet (section 2.1)
makes these the hardware disables and says each "may only be driven low; it can't be driven high"; U6 is push-pull, and
with W5-F1 its internal pull-up already holds the pins high into an unpowered module through the module's 1.8 k pull-up
(section 3.1: "No pins should be powered before the 5 V rail is active"). A firmware path exists (the panel reads
EMCON_HW on GPIO21 and masters U6) but it is software. `inhibit_chain_b` (RF-002, PASS, 18 Sep) checks chain shape, not
every transmitter. Recommendation: open-drain pull-downs from EMCON_HW on all six pins (one 74LVC07 class part or six
FETs), U6's bits for these pins used only as open-drain (output 0 or input), and an RF-002 instrument that lists every
`rf_transmit` part and its inhibit path. Test: HW2.

**W5-F8, major (raised from minor), VERIFIED (documents) and TBD (behaviour), from A11. The M.2 radios' EMCON is a
module input, never a supply cut, and for the two WiFi link cards its effect is unproven.** Card rails follow
`PCIE_PWR_ENx` only (gen_sch_b.py:406); 5G `FULL_CARD_POWER_OFF#` comes only from U6 via Q207. EMCON_HW pulls
W_DISABLE1# low through Q106, Q206 and Q306 (gen_sch_b.py:472, 480, 498). RM520N: "Driving it LOW will set the module to
airplane mode. In airplane mode, the RF function will be disabled" (HD v1.0 and v1.1, 4.4.1): transmit stops and so does
receive, while the module stays powered and the host link stays up. Whether any AT setting can disable the pin's effect
is TBD (AT manual not held). AW7915-AED: the maker's sheet says nothing about W_DISABLE, and mainline Linux `mt7915` has no
rfkill code (A11; `mt7921` and `mt7925` do poll the pin). **If the card ignores the pin, EMCON removes nothing from two
kit-to-kit transmitters.** Contract: RF-002 must not count either AW7915 as inhibited until HW11 passes; the software hold
(rfkill on the interface, section 4) is asserted on every EMCON edge meanwhile. Appendix 32.56 (line 2930) promised "the
5G module's supply switch" and "the WiFi card's 3.3 V buck enable" under EMCON; the generated boards have neither, a
design-record against generator mismatch to record, not a fact about the boards. Tests: HW2, HW11.

**W5-F9, major, VERIFIED (from A07). The pack SMBus lead has no single connector, and the gauge reaches only the sensor
controller.** P's J_SMB is a JST-XH B4B-XH-A, 1x4, 2.50 mm: 1 SMBC, 2 SMBD, 3 GND (the cell side, upstream of the 2 mOhm
shunt R10), 4 PRES (gen_sch_p.py:152, 155, 172). E's J_SMB is a generic 2.54 mm pin header 1x6 (key `PH6` means pin header,
gen_sch_e.py:119, 130, 136): 1 SDA0, 2 SCL0, 3 SDA1, 4 SCL1, 5 GND, 6 GND, left over from the withdrawn BB-2590/U.
ASSEMBLY.md:60's "XH2.5 x 6" matches neither. A straight lead would put clock on data, hold the sensor bus data at 0 V,
toggle PRES with every sensor clock and carry no ground. The only reader is E's RP2040 U10: pins 4 and 5 are GPIO2 and
GPIO3, **the I2C1 block** (RP2040 datasheet Table 279), although the nets and gen_sch_e.py:349 say I2C0. The BQ25731 on
A is an I2C target at 0x6B with no conductor to P and no thermistor input (SLUSE66A 9.5.1; pin table). So PANEL.md:128 and
:155 and appendix 32.62's "the charger BQ25731 of A22 already speaks SMBus to it" are false. **Fix (A07, engineering):**
E's J_SMB becomes a JST-XH 1x4 with 1 SCL0, 2 SDA0, 3 GND, 4 NC (C594232 fills in); P's J_SMB pin 3 moves to PACK_N as
TI's Figure 21 does (otherwise the lead's ground wire bypasses the shunt and carries about 5 to 8 percent of the pack
current, INFERRED); a J_SMB contract in `check_contracts.py`. **Firmware contract:** the sensor controller opens `i2c1`
on GPIO2/3 for the gauge; the battery bar and the pack temperature (the BQ4050's TS1) reach the panel from the sensor
controller over USB through the bridge; PANEL.md:155's cold-charge SHORE_INHIBIT rule takes the pack temperature from
there, not from the charger. Adjacent defect for its own issue (A07): P's D2 USBLC6-2SC6 has VBUS on VCC_F (PACK_P
through R7 1 k, gen_sch_p.py:116, 171), 12 to 16.8 V against VRM 5.25 V, a continuous 5 to 11 mA clamp. W3 owns the
connector contract. Test: HW13.

**W5-F10, major (raised from minor), VERIFIED (strap, topology) and INFERRED (the POR value), from A02. A kit with no
running host does not charge usefully.** (1) **As generated nothing charges a 4S pack:** R26 60.4 k from VDDA and R27
40.2 k (gen_sch_a.py:350; A23 netlist) put 39.96 percent on CELL_BATPRESZ, inside SLUSE66A's 2S window (35 to 48.5
percent), although the generator's own comment says 4S; 2S sets ChargeVoltage 8.4 V and a latching SYSOVP of 11.7 to
12.2 V, below the 4S pack (W2 F-CH-01). (2) The BQ25731's ChargeCurrent at POR and after its 175 s watchdog is 256 mA per
TI (E2E 1316778, 23 Jan 2024: "Looks like there is a mistake in the description. The POR value is indeed 256mA");
SLUSE66A contradicts itself (the header 0080h, 9.3.21.1, 9.4.1 and Table 9-8 say 256 mA; the 9.6.2 text and the Figure
9-15 caption say 0 A, and A02 found both copied word for word from the BQ25730's SLUSE65A). Round 1's VERIFIED is
withdrawn: INFERRED, bench confirmation owed. (3) Even with the strap fixed, the 256 mA passes the charge shunt R17 and
every kit load sits on VBAT on the pack side of R17 (A23 netlist; the part has no BATFET), so shore delivers at most
256 mA (3.1 to 4.3 W) to load and pack together, below every declared operating mode: the pack loses charge unless a
host-free kit's residual load is below 256 mA (TBD). (4) The ChargeCurrent value after an adapter removal is TBD (0 A per
the inherited text, or 256 mA). (5) A host that set WDTMR_ADJ = 00b before it crashed leaves its last ChargeCurrent in
force until an adapter removal, a CELL pin low or a POR. (6) RSNS_RAC defaults to 5 mOhm while board A's input sense R16
is 10 mOhm, so the input-current scaling is wrong until a host writes RSNS_RAC = 0b (A02). **So PANEL.md:155 "a kit with
a crashed panel still charges" is false as wired** (round 1 called it true at 256 mA: refuted in effect). **Contract:**
the kit-bus master writes RSNS_RAC, ChargeVoltage (4S), ChargeCurrent and the input limit after every charger POR and
services the watchdog in under 175 s; the watchdog is left enabled, so a crashed host falls back to the 256 mA default
rather than to its last setting; charge temperature is the BQ4050's (its charge window in data flash), since the
BQ25731 has no thermistor input. Test: HW8.

**W5-F11, major, VERIFIED. No generator places the tamper switch, although it is approved and its input is sited.**
Appendix 32.50 item 6 (line 2790) approved "Case-open and tamper switch feeding ZEROIZE logic and the log", and the
approved floor plan of 32.52 item 4 (line 2848) lists "the tamper switch input" on E6. A grep of `tamper` over
gen_sch_*.py finds nothing. **This is an implementation omission, not an owner question** (round 1 asked it; withdrawn):
add a sealed switch under the frame to a sensor-controller input on E, which is powered whenever the pack is fitted
(gen_sch_e.py:90), so a lid opening is logged with the kit off. Only a withdrawal would be the owner's, and none is
proposed.

**W5-F12, minor, VERIFIED. ARCH-PCB-B-IOHA contradicts itself on the ring, and the generator settles it.** The failover
host is `f = s % 3 + 1` (gen_sch_b.py:543, used at 547 and 552): bank 1 to slot 2, bank 2 to slot 3, bank 3 to slot 1.
IOHA section 4 agrees; section 15 is the reverse ring.

**W5-F13, minor, INFERRED. EMCON-gated radios are back-powered through their host bridges.** The E72 CP2102N bridges run
from `+5V_DEV` and drive RESET_N and DIO_15 through RTS and DTR (gen_sch_b.py:692) while `+3V3_ZB` is cut by EMCON
(gen_sch_b.py:693); the RockBLOCK bridge, and U6's RB_IEN and RB_CTRL (W5-F1), are the same shape. Contract: the bridge
lines are held low (or the bridges suspended) while EMCON is asserted; hardware option: bridge VIO from the gated rail.
Rule: PWR-002.

**W5-F14, minor, VERIFIED. Two documents cite tests the test plan never carried.** gen_sch_d.py:192-194 (the hub crystal
margin "is in TEST-PLAN.md") and RED-TEAM-2026-09-09.md:261 (the 10-minute 30 W key-down, "the one the test plan already
contains"). Neither was in TEST-PLAN.md; both are now PROPOSED tests HW10 and HW9.

**W5-F15, major, VERIFIED (W2 F-SQ-02, re-read here). The power controller holds two pins above their absolute maximum
whenever the pack is fitted.** `r("R4", "100k", "KILL", "VBAT")` (gen_sch_a.py:172) against "KILL ... -0.3V to 7V"
(2954fb, Absolute Maximum Ratings); the datasheet's own instruction for KILL is "connect to a low voltage output supply
(see Figure 6)". And `r("R2", "100k", "RAIL_EN", "VBAT")` puts U12's EN at VBAT (12 to 16.8 V) whenever U1's open-drain EN
is released, against the TPS62933's "EN -0.3 6" V (SLUSEA4D 8.1; recommended maximum 5.5 V). The LTC2954's own EN output
is rated to 33 V, so the over-stress is on U12, and on U1's KILL input from the moment the pack is fitted (PC-0). If U12's
EN is damaged the kit cannot boot at all, whatever the expanders do (A01 unknowns). **Fix options (engineering, the
session's):** KILL: R4 to A's `+3V3`, the converter output U1 enables (the datasheet's Figure 6 arrangement); `+3V3`
rises within the 400 ms minimum blanking (INFERRED from the TPS62933 soft start), and KILL then also shuts the kit down if
the logic rail collapses. RAIL_EN: either delete R2, since the TPS62933's EN has its own pull-up ("Driving EN high or
leaving this pin floating enables the converter", pin table; Ip 0.7 uA at 1.0 V) and the LTC2954 says its EN "can
connect directly to a DC/DC converter shutdown pin that provides an internal pull-up", or keep a divider from VBAT (W2:
100 k over 47 k gives 5.4 V at 16.8 V and 3.2 V at 10 V, above VEN_RISE 1.28 V max). Firmware consequence: none, but
bring-up must not power a board built to the current generators from the pack. Test: HW4.

**W5-F16, major, VERIFIED (W2 F-SQ-03, re-read here). The power controller is a 0 to 70 C part in a -20 to +40 C kit.**
U1 is `LTC2954CTS8-1` (gen_sch_a.py:171); the sheet's order table rates LTC2954CTS8-1 at 0 to 70 C and LTC2954ITS8-1 at
-40 to 85 C (2954fb). The adopted operating envelope is -20 to +40 C ambient (OPERATING-ENVELOPE.md section 4, decision
34). Fix: the I grade. What JLC code C683782 actually ships is W6's to confirm. The MAIN button is the kit's only way on,
so a cold-start failure of this part is a whole-kit failure below 0 C (INFERRED). Test: HW4 at -20 C.

**W5-F17, minor, VERIFIED (datasheet), INFERRED (triggers). After a supply loss the kit stays off until someone presses
MAIN.** 2954fb, Turn On: "When power is first applied to the LTC2954, the part initializes the output pins. Any DC/DC
converters connected to the EN/EN pin will therefore be held off." U1 is on VBAT; once VBAT falls below its UVLO (2.2 to
2.5 V falling) and returns, the kit does not restart by itself. Triggers: a pack swap, a BQ4050 discharge-FET trip, a
pack below its SHUTDOWN threshold. Whether shore holds VBAT up without the pack is TBD (the charger regulates CH_SRP,
which feeds VBAT only through R17 and F1, W5-F10). A kit on a vehicle input after an overnight pack trip is therefore
off in the morning. Declared behaviour needed: either "stays off, MAIN restarts it" written into PANEL.md and the
operator procedure, or an auto-restart path (for example PB pulsed by the sensor controller, which is always on), an
engineering choice unless the owner wants unattended restart as a product property. Test: HW12.

**W5-F18, minor, VERIFIED (feature exists), TBD (configuration). The gauge has a host watchdog that nothing services
today.** SLUSC67B 7.3.1 lists "Host Watchdog Timeout Protection" among the BQ4050's primary safety features; its
behaviour and default are in SLUUAQ3, not held. With W5-F9 unfixed no host can reach the gauge at all; once fixed, the
sensor controller is the only host. If the feature is enabled in the data flash image, a sensor-controller crash could
act on the FETs (TBD). Contract: the data flash image states whether it is enabled; if it is, the sensor controller polls
the gauge inside its timeout. Test: HW13.

## 4. EMCON, radio by radio (A11, as generated at `82dd1e4d`, regeneration parity proven on A, B and D)

Asserted means SW_EMCON closed: TX_INHIBIT_n low, and EMCON_HW follows it low through C's U9 (gen_sch_c.py:136, 143,
173). With the ribbon out both lines read low on A, B and D (R102, R145; R58, R59; R2), so every gated transmitter is
inhibited, and no module runs (W5-F4).

| radio | board | what EMCON does (VERIFIED unless marked) | kind | receive under EMCON |
|---|---|---|---|---|
| SA868 VHF exciter (APRS) | D | KEY = PTT_ANY AND TX_INHIBIT_n drives SA_PTT_n (gen_sch_d.py:274-275); the exciter's supply and PD are not touched; the resting relay joins antenna to exciter | transmit only | **continues** |
| RA30H1317M1 30 W PA | A rail, D bias | PA_EN = EMCON_HW AND PA_SW_EN into the LM5176 enable (gen_sch_a.py:535-536); PA_KEY = KEY AND PA_EN drops the relay and VGG (gen_sch_d.py:276) | rail and bias | n/a |
| QMX HF | A | HF_EN = EMCON_HW AND HF_SW_EN into the LM5176 U15 enable: `+12V_HF` (the QMX DC input) off; VBUS_QMX from B stays up | power | lost (the manual puts receive on the DC supply; INFERRED that USB alone does not run it) |
| LimeSDR Mini 2.4 | B | LIME_EN = EMCON AND hub PWRCTL1 AND LIME_SW_EN into eFuse U23, its only supply (gen_sch_b.py:699, 725) | power | lost |
| RockBLOCK 9704 | B | RB_EN into eFuse U24, +5V_RB = J_RB9704 pin 15, the only supply wired (gen_sch_b.py:704, 725) | power | lost (no MT messages or ring alerts) |
| E22-900M30S LoRa | B | E22_EN into load switch U21, the module's only VCC (gen_sch_b.py:680, 725); TXEN is driven only by slot 3 GPIO4 | power | lost |
| two E72 (Zigbee, Thread) | B | E72_EN into load switch U22, `+3V3_ZB` (gen_sch_b.py:693, 727) | power | lost |
| RM520N 5G | B | Q206 pulls W_DISABLE1# low; the card rail follows PCIE_PWR_EN2 only | airplane mode, module powered | lost |
| two AW7915-AED WiFi link cards | B | Q106 and Q306 pull W_DISABLE1# low; W_DISABLE2# has a pull-up only; rails follow PCIE_PWR_EN only | request only | **TBD: may remove nothing (W5-F8)** |
| three CM5 on-module WiFi and BT | B | nothing in hardware (W5-F7) | none | continues, and so does transmit |
| LG290P GNSS, RM520N GNSS, DCF77, AS3935 | B, E | none | receive only | continues |

**So today EMCON means "power down" for the SDR, Iridium, LoRa, Zigbee, Thread and HF, airplane mode for 5G, transmit-only
for VHF/APRS alone, unproven for the WiFi link cards and absent for the CM5 radios.** Whether EMCON should keep every
receiver that can listen without transmitting is the owner question A11 states (W1's D-05); this contract records the
state, it does not choose.

**Firmware contract for EMCON:** (1) the software holds (`*_SW_EN`, `LORA_ON`, `ZB_ON`, AT+CFUN=4 on the 5G module,
rfkill on the CM5 radios and the AW7915 interfaces) are asserted on the EMCON edge as well as by hardware, because W5-F7
and W5-F8 leave gaps; (2) nothing drives TX_INHIBIT_n (check_contracts.py:342-343 already enforces it); (3) EMCON release
does not re-enable a radio the operator had off; (4) while EMCON is asserted the bridges to gated radios hold their lines
low (W5-F13). The TX lamp follows D's KEY only (gen_sch_d.py:281): it shows the APRS transmitter and no other.

## 5. ZEROIZE: what the hardware does today, and the options (decision 30 made concrete)

**Four descriptions disagree and the netlist matches none of the first three.** V2-SPEC.md:34 "element wiped, disk-key
wipe line asserted"; PANEL.md:112 "wiped by the supervisor on the falling edge (hardware line to the slots)"; the toggle's
own value string at gen_sch_c.py:174 "ZEROIZE_HW low = wipe the secure element and assert the disk-key wipe (32.52)";
decision 30 (pcb_decisions.yaml:207-233) "the panel controller does the wipe". VERIFIED from the generators: the only
listener is the panel RP2040's GPIO22 (gen_sch_c.py:113, pin 34); the line has pull-ups on C (R10) and A (R117, 10 k,
gen_sch_a.py:573), passes B from J_PANEL pin 10 to J_AB1 pin 20 with a test point, and ends on D at a test point
(gen_sch_d.py:323). There is **no disk-key wipe line** and no supervisor input. The ATECC608B sits on the kit bus that the
panel masters (gen_sch_b.py:750).

**What state ZEROIZE must affect (the inventory; what is erased is decision 30's to rule):** (1) the ATECC608B's secret
slots; (2) the keys of the three modules' encrypted NVMe drives and eMMC; (3) key material in module RAM; (4) credentials
on the modules (WiFi mesh keys, Winlink, TAK certificates); (5) the panel controller's own flash (event log, enrolment
state). Not erasable by this design: the SIM cards, the RockBLOCK's and the 5G module's own identities, the LimeSDR and
QMX internal state.

**Triggers:** the ZEROIZE toggle closed 5 s (PANEL.md section 9); the tamper switch once built (W5-F11); no remote trigger
is specified and none is proposed.

| option | mechanism | covers modules that are off | cost | residual |
|---|---|---|---|---|
| Z-A (decision 30's recommendation on file) | the panel overwrites the SE's secret slots on the falling edge plus 5 s, then messages every running module over USB to erase its keys | no | firmware only | a module that is off or wedged keeps its keys |
| Z-B (W5's recommendation to the owner) | crypto-erase by design: every drive and eMMC key is wrapped by a key held only in the SE, unwrapped at boot through the panel (the only SE master); ZEROIZE destroys the SE slots first, then messages running modules to drop RAM keys, then drops `SLOT_EN1..3` | yes | firmware and provisioning; no board change | DRAM remanence after power removal (INFERRED); the panel becomes a boot dependency for every drive (W5-F4 makes it a whole-kit one) |
| Z-C | Z-B plus ZEROIZE_HW into each IOCTRL supervisor and each module GPIO | yes, without the panel firmware | a board B change | more copper and more ways to wipe by accident; reopens the H753/H743 question (W6) |

**Limit on the SE (VERIFIED absence):** the held ATECC608B document is the summary; how a locked slot is overwritten and
which slots can be made erasable is in the NDA datasheet. So the provisioning slot map must be designed with ZEROIZE in
it; a slot configured as permanent can never be zeroized. TBD until the full datasheet is on file.

**After power loss (the toggle is maintained, gen_sch_c.py:174):** proposal: level-sensitive. At boot the panel reads
ZEROIZE_HW before anything else; if closed, it completes the wipe before enabling any slot, with a "wipe pending" record
in its flash so an interrupted wipe resumes. The kit re-arms only after the toggle is returned. Edge-only fails toward
keeping the keys; that is the owner's risk choice.

**The public test plan does not pre-empt the ruling:** TEST-PLAN.md HW6 lists the measurements every option needs and
leaves its acceptance criterion to be written from the option decision 30 rules. The criterion W5 proposes for Z-B (the
SE's pre-wipe public keys no longer returned or the slot refuses the operation; a signature under the old identity no
longer verifies; every drive, including an off module's, fails to unlock from a cold boot; an interrupted wipe completes
at the next boot; no re-arm until the toggle returns; the time from the arming edge to "complete" measured against
appendix 32.50 item 5's "keys wiped in milliseconds") stays here, in the draft, until the ruling.

## 6. Diagnostics and watchdog contract, and the boot order

- **Panel RP2040, boot order (A01 section 5, W5-F1, W5-F5, W5-F6, W5-F10):** (1) GPIO19 `PI_KILL` push-pull LOW first, and never
  released while any slot is powered; (2) GPIO18 `PI_SHDN_REQ` pull-down off, output value 0, output disabled (released);
  (3) read ZEROIZE_HW; (4) for U27, U28 and U6, **write the output registers before the configuration registers** (the
  default output register is FFh: writing configuration first drives POE_EN and PD_EN to 3.3 V and starts both LM5176
  stages), with DEV_EN kept at 1; (5) service the charger (RSNS_RAC, ChargeVoltage for 4S, ChargeCurrent, input limit,
  watchdog left enabled and serviced in under 175 s); (6) `SLOT_EN1..3` one at a time. **Never write DEV_EN = 0 except as
  the last act of a shutdown**: it removes the panel's own supply and U27 holds that state until `+3V3` falls. Hardware
  watchdog on, with PADS_BANK0, IO_BANK0 and SIO excluded from its reset scope (W5-F4); boot reason logged. Reports over
  USB: every switch and hardware line, heartbeats, firmware version and build hash, last reset reason.
- **Sensor RP2040:** watchdog on; GPIO15 (SHORE_INHIBIT read-back, gen_sch_e.py:354) is never an output; the gauge on
  `i2c1` (GPIO2/3) once W5-F9 is fixed, polled inside the BQ4050 host-watchdog time if that feature is enabled (W5-F18);
  reports pack state and TS1 temperature over USB.
- **IOCTRL supervisors:** IWDG started by option byte (RM0433 not held: TBD), BOR level set, a controller without quorum
  does not act (IOHA FMEA row 8), votes and read-back published on CAN and, after W5-F3, I2C. Add SWO (PB3) to the SWD
  land.
- **CM5 modules:** OS watchdog enabled (INFERRED availability), heartbeat on GPIO16 at 1 Hz only while the bridge runs,
  never force link speed on KSZ ports 1 to 3 (decision 29), treat `PI_SHDN_REQ` low as the request (W5-F6); `EEPROM_nWP`
  floats (gen_sch_b.py:570), so the bootloader EEPROM is writable by software: a security posture to rule on.
- **BQ4050:** SEALED in the field; data flash written from a reviewed image at pack build and read back by checksum; PF
  flags and lifetime data read by the sensor controller; decision 40 stays open.
- **Charger:** owned by the kit-bus master (W5-F10).

## 7. Corrections for other documents (integrator input; this workstream edits none of them)

- **PANEL.md:** a ready patch is `drafts/w5-panel-md.patch` (lines 51, 111, 112, 128, 130, 155). Line 111 is also
  assigned to W7 by A11; the integrator applies one of the two.
- **ARCH-PCB-B-IOHA.md:** section 15's ring (W5-F12); test A14's "with the SDR" (the LimeSDR is powered off by EMCON:
  A11); section 6's supervisor I2C pins (W5-F3).
- **OPERATING-ENVELOPE.md:** section 2 still says the pack cells are "still owed a sheet"; the Samsung INR18650-35E sheet
  Ver. 1.1 is held (`vendor/battery/samsung-35e-orbtronic.pdf`, sections 3.12 and 3.13) and gives the same 0 to 45 C
  charge and -10 to 60 C discharge (cell surface) the table uses. Its line 89 ("the pack thermistor on the charger's
  JEITA input") is false for the BQ25731 (A02).
- **CONOPS.md:137** (W1): "HW (charger TS input)" and "a crashed panel still charges (by design)" are false (A02, W5-F10).
- **ASSEMBLY.md:45, :60, :140** (A07): the pack lead and the charger thermistor.
- **V2-SPEC.md:34** and the SW_ZERO value string (gen_sch_c.py:174): the disk-key wipe line does not exist (section 5).

## 8. Owner decision candidates (updated)

1. **Qualification margins** (E3 +55 C operation and +71 C storage, E4 -33 C storage, E5 30 to 60 C, all outside the
   adopted envelope). Options and recommendation unchanged from round 1, now written into TEST-PLAN.md section 1b. The
   probable source of +71 C and -33 C is MIL-STD-810's climatic categories (Methods 501 and 502), TBD because the
   standard is not held; appendix 32.50 item 16e approved a MIL-STD-810 plan, not those levels by name. The plan was
   approved on 6 September, ten days before the envelope was first committed (16 September, `d122a261`).
2. **ZEROIZE semantics (decision 30)**, section 5: Z-A, Z-B (recommended), Z-C; level-sensitive or edge-only after power
   loss.
3. **MIL-STD-461 edition and limit curves** for M1 to M5: choose before any lab money; until then every run is
   characterisation.
4. **What EMCON keeps listening to** (A11's owner question, which W1 carries as D-05): stated here only so the batch does
   not ask it twice.

Withdrawn from round 1: the tamper switch (W5-F11: approved and sited, so implementing it is engineering).

## 9. Round-2 disposition of the challenger's defects and missing items

| challenger item | what changed |
|---|---|
| F10 256 mA treated as VERIFIED | W5-F10 rewritten per A02: INFERRED, TI E2E 1316778 and the SLUSE65A diff cited; the strap and the R17 topology added; adapter-removal value TBD; WDTMR_ADJ = 00b case; RSNS_RAC; TEST-PLAN HW8 rewritten |
| F5 "masked today" fails for PI_KILL | W5-F5 raised to major, PLAUSIBLE, with the arithmetic in `drafts/r2calc/pi_kill_backdrive.py`; boot-order rule added (section 6 step 1); hardware options; HW3 and HW5 scope KILL and RAIL_EN |
| LTC2954 KILL abs max and C grade missed | W5-F15 (KILL and U12's EN over their absolute maxima) and W5-F16 (C grade), W2's evidence re-read; HW4 checks both |
| F1 overclaims, misses PD_EN, RB_IEN/RB_CTRL, LM5176 threshold | W5-F1 rewritten per A01: nominal and undefined states, PoE/PD OFF, U28 PD_EN and U6 RB_IEN/RB_CTRL added, LM5176 VEN(OP) cited; the PCA9535 recommendation demoted to an alternative that must come with R42 |
| F4 and F6 overstated; bootloader line | W5-F4 narrowed to the ROM USB bootloader route, the in-application route stated, IOHA section 10 and FMEA row 12 cited; W5-F6 states both readings and that section 5 needs no change; section 1 bootloader line softened |
| TEST-PLAN silent condition changes | reverted; every change listed in TEST-PLAN.md section 0; the E1/E2 powered state and the E5 criterion scope are PROPOSALS in section 1c |
| TEST-PLAN cites drafts, ID collision, Z-B acceptance | tests renamed HW1 to HW13; no draft is cited; HW6 acceptance pending decision 30 |
| TEST-PLAN factual slips | ten days (envelope first committed 16 Sep); the held 35E sheet cited in 1a; the TRACO sentence rewritten |
| +71 C / -33 C source | "probable source MIL-STD-810 climatic categories, TBD" recorded in TEST-PLAN 1a and 1b |
| test-access numbering | `drafts/w5-test-access.md` aligned to HWn and W5-Fn |
| missing: recovery after pack loss | W5-F17 and HW12; PC-10 in section 2 |
| missing: BQ4050 host watchdog | W5-F18 and HW13 |
| missing: requirement IDs | recorded open in TEST-PLAN section 0 (TBD, assigned by the integrator) |
| missing: tamper is a non-decision | W5-F11 rewritten; owner candidate withdrawn |
