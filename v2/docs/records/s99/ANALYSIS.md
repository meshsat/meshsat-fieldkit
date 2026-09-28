# S-99: board A's +5V_DEV converter against the PS-ALLTX coincident demand

Stream s99, MESHSAT-1357, 28 September 2026, from the integration set's tip `2b7c9374`. **AI engineering analysis**
(desk calculation and AI review), not a qualified engineering review. Prototype design: no V2 board has been built,
ordered or measured; every figure below is a declaration, a maker's published figure or arithmetic on them, and the
label on each says which. The arithmetic is `dev_stage.py` (inputs pinned by sha256, output `dev_stage.out`).

Corrected by job `cx3-s99-correction` from base `684639c4feb39b425d9e51590df80a45442f966e`.
`CORRECTION.md` answers the first AI review. The original input hashes and valid sense-path work are retained.

## 0. Result in five lines

1. The fitted stage is an LM5176 buck-boost (U7) from VBAT (12.4 to 16.8 V) to 5.088 V, four CSD19532Q5B, a 6.8 uH
   XAL1010, a 5 mOhm cycle-by-cycle shunt in the low-side FETs' common source and a **6 mOhm average-loop shunt on
   the OUTPUT side** (R43, between Q35's drain and the +5V_DEV rail), CCM without hiccup, 47 nF soft start.
2. The average loop regulates the **output** current to 43 to 57 mV across R43: **7.06 A (minimum, with 1 percent and a
   hot shunt) / 8.33 A (typical) / 9.65 A (maximum)**. The cycle-by-cycle valley limit sits at 13.1 to 19.0 A of
   inductor current and never acts at the demand; the average loop is the governing limiter.
3. Under an assumed coincident plateau, M = 7.322235 A, D = 8.900 A and P = 9.761220 A
   (9.770759 A with R186 at -1 percent). No tier is below the conditional 7.056897 A minimum.
   The P-tier uses an extrapolated wall limit, not a guaranteed 1 kohm maximum. Timing and complete-rail
   collapse remain unresolved; the datasheet gives no closed-loop time constant or onset bound.
4. Re-rating to 5.0 mOhm fails BOTH the 8.9 A demand at its 8.514851 A initial minimum (8.468276 A with
   assumed hot-shunt TCR) and the lead's 10 A rating at its 11.515152 A initial / 11.578835 A hot maximum.
   The 5.6 mOhm alternative also fails both tests. A higher threshold alone is not capacity evidence.
5. **Recommendation for SESSION: option B, the D8 split**, after the corrections below. The remaining stage
   carries 6.900 A declared and 5.942235 A M-tier with margins 0.156897 A and 1.114661 A against 7.056897 A.
   P = 8.171220 A (8.180759 A with R186 tolerance), still above that minimum. B and B plus the wall-port
   interlock both remain configurations; B preserves console availability. M/P load reconciliation, actual
   waveform, collapse/recovery, timing and thermal verification stay open, as section 5 specifies.

## 1. The fitted stage (from the generator and the netlist)

Source: `v2/ecad/tools/gen_sch_a.py`, the `lm5176(...)` helper (lines 359 to 655) and its `SD` call (lines 1013 to
1018), the intent rail at line 120, the netlist `v2/ecad/pcb-a-power-a23/out/pcb-a-power.net` (sha256
`0a2b5908...`), parsed by `dev_stage.py` section 1 (every part below read PASS against its expected value).

| Element | Fitted | Where |
|---|---|---|
| Controller | U7 LM5176PWPR (HTSSOP-28), VIN and BIAS on VBAT (`bias="VBAT"`, R4A-N6), VISNS on VBAT, VOSNS on +5V_DEV | helper pin map; SD call |
| Output voltage | R40 53.6k 1 percent over R41 10k 1 percent on FB: 0.800 V x 6.36 = **5.088 V** (5.012 to 5.164 V over VREF's 0.788 to 0.812 V, resistor tolerance not added) | SNVSAI1D p.6 VREF; netlist |
| FETs | Q32 buck high side (HDRV1, VBAT to SD_SW1), Q33 buck low side (LDRV1, SD_SW1 to SD_CS), Q34 boost low side (LDRV2, SD_SW2 to SD_CS), Q35 boost high side (HDRV2, SD_OUT to SD_SW2): all CSD19532Q5B, 100 V, 4.6 mOhm typical at VGS 6 V | helper `nfet` lines; SLPS414B p.3 |
| Inductor | L6 6.8 uH XAL1010-682ME, +-20 percent, Isat 21.8 A (30 percent drop), Irms 14.0 A at 20 K rise, 18.5 A at 40 K, DCR 8.10 typ / 8.90 max mOhm | Coilcraft 804-1 (revised 02/25/26) |
| Cycle-by-cycle sense | **R177 5 mOhm 1 percent 2512 from SD_CS (the common source of Q33 and Q34) to GND**; CS and CSG filtered by R180/R181 100 R and C145 1 nF at pins 16 and 15 | netlist: R177 pin 1 on SD_CS, Q33 and Q34 pins 1 to 3 on SD_CS |
| Average-loop sense | **R43 6 mOhm 1 percent 2512 (Vishay WSL25126L000FEA, C843882) between SD_OUT (Q35's drain tab, pin 5) and +5V_DEV**: the OUTPUT side; ISNS(+) pin 14 from SD_OUT and ISNS(-) pin 13 from +5V_DEV through R182/R183 100 R with C146 1 nF at the pins | netlist: R43 pin 1 on SD_OUT with Q35 pin 5, pin 2 on +5V_DEV; helper `isns_filter` |
| Frequency | R115 40.2k on RT: 1 / (40.2k x 116 pF + 190 ns) = **206 kHz** nominal, 180 to 232 kHz over the fSW(1) spread of 175 to 225 at 40 k | SNVSAI1D p.17 equation 5, p.6 |
| Slope | C140 470 pF on SLOPE | SD call `cslope` |
| Compensation | R132 2.2k, C115 100 nF (COMP to COMPC to GND), C141 1 nF (COMP to GND); loop design figures on the call: PM 68 degrees, GM 15.1 dB, crossover 2.9 to 9.4 kHz | SD call `comp` |
| Soft start | C142 47 nF (`css` default): illustrative nominal start-up estimate t_ss = 47 nF x 0.8 V / 5 uA = 7.52 ms, not an average-loop response bound | SNVSAI1D p.16 equation 3, p.6 ISS |
| Mode | R179 100k from MODE to VCC: MODE at VCC, **CCM, hiccup disabled**; a sustained overload is held in cycle-by-cycle limit, not hiccupped | SNVSAI1D p.3 pin table, p.20 table 7.4.2 |
| VCC and bootstrap | C143 4.7 uF on VCC (6.95 to 7.88 V); D7, D8 BAT46W bootstrap diodes; C144, C46 100 nF 25 V boot capacitors | SD call; SNVSAI1D p.6 |
| Input capacitors | C47, C48 10 uF 50 V X7R 1210 on VBAT (the input loop); C220 100 nF at the VIN pin; C194 100 nF at BIAS | SD call `vin_cap`, `bias_cap` |
| Output capacitors | C49, C50, C51 22 uF 25 V 1210 and C167 to C169 150 uF 25 V EEHZK1E151XP hybrid polymer, all on +5V_DEV (after the shunt; no `cout_pre` on this stage) | SD call `cout`, `bulk` |
| Enable | DEV_EN straight into EN/UVLO (`en_div=False`), R42 100k pull-up to +3V3: **on whenever board A's 3.3 V is up**, the panel can shed it | line 1020 |
| Monitor | U11 INA226 (0x45) across R43: IN+ on SD_OUT, IN- and VBUS on +5V_DEV | line 1021 |
| Local loads of the rail | U23 TPS259631 eFuse to +5V_D8 (R98 453 R: ILM 2.0 A nominal), switched by D8_EN; U32 TPS259631 eFuse to VBUS_WALL (R186 1 k: 0.9142 A nominal by corrected equation 7; the held label says 0.89 A), switched by USBX_EN; J_5V_DEV (JST-VH B2P-VH) to board B | lines 1308, 1533 |
| Declaration | `_intent.rail("+5V_DEV", 5.0, 4.0, 6.9, "R43", loads={"J_5V_DEV": 3.2, "U23": 0.5, "U32": 0.3}, ..., switch="U7", efficiency=0.90, fed_from="VBAT")`: 4.0 A typical, 6.9 A peak = board B's 6.0 A plus the wall port's 0.9 A with **the D8 mezzanine at zero**, as cx1 found | line 120 and its comment at 116 to 119 |

Operating point: VBAT is 12.4 V (REQ-018's PA-alone floor) to 16.8 V (service maximum) against 5.088 V out, so the
stage is always in **buck** (D = 0.30 to 0.41); Q35 is on continuously and carries the whole output current, Q34 is
off (SNVSAI1D 7.3.14 p.19). Inductor ripple in CCM: 2.14 A at 12.4 V, 2.53 A at 16.8 V, 3.62 A at the corner (L
minus 20 percent, 180 kHz).

## 2. The maker's words

| Document | Where | What it says, and how it is used here |
|---|---|---|
| TI LM5176, SNVSAI1D, June 2017 revised August 2021, `v2/vendor/ti/lm5176-datasheet.pdf` | p.3 to 4 pin table, ISNS(+)/ISNS(-) | "An optional current sense resistor connected between ISNS(+) and ISNS(-) can be located either on the input side or on the output side of the converter. If the sensed voltage ... reaches 50 mV, a slow constant current (CC) control loop becomes active and starts discharging the soft-start capacitor to regulate the drop across ISNS(+) and ISNS(-) to 50 mV." On this stage the resistor is on the output side (section 1), so the loop limits the **output** current 1:1. |
| same | p.7, VSNS | "Average current loop regulation target 43 / 50 / 57 mV" (test condition VISNS(-) 24 V, sweep ISNS(+), VSS 0.8 V); ISNS pin bias 3 uA; Gm of the soft-start pulldown amplifier 1 mS (at 55 mV, VSS 0.5 V). The 43 to 57 mV band is taken as the regulation point as published. |
| same | p.7, VCS(BUCK), VCS(BOOST) | Buck **valley** threshold 66 / 80 / 94 mV (HTSSOP-28); boost peak 100 / 120 / 140 mV. |
| same | p.16, 7.3.4 and 7.3.5 | "When average input or output current limiting is active, the soft-start capacitor is discharged by the constant current loop transconductance (gm) amplifier"; "In buck operation, the sensed valley voltage across the CSG and CS pins is limited to VCS(BUCK). The high-side buck switch skips a cycle if the sensed voltage does not fall below this threshold during the buck switch off time." |
| same | p.17, 7.3.6 | "The average current limiting circuit uses an additional current sense resistor connected in series with the input supply or output voltage ... compares it with an internal 50-mV reference. If the drop across the sense resistor is greater than 50 mV, the gm amplifier gradually discharges the soft-start capacitor. When the soft-start capacitor discharges below the feedback reference voltage, VREF, the output voltage of the converter decreases to limit the input or output current." Equation 4: ICL(AVG) = 50 mV / RSNS. **No time constant is stated**; section 4b uses CSS, gm, VSS(CL) and VREF only for illustrative estimates, not bounds. |
| same | p.17 (7.3.5 continued), p.20 table 7.4.2, p.13 overview | Hiccup only when MODE selects it; otherwise "the LM5176 will operate in cycle-by-cycle current limiting as long as the overload condition persists". This stage: no hiccup. |
| same | p.6 | ISS 3.75 / 5 / 6.35 uA; VSS(CL) 1.21 V (SS clamp); VREF 0.788 / 0.800 / 0.812 V; fSW(1) 175 / 200 / 225 kHz at RT 40 k; VCC 6.95 / 7.35 / 7.88 V. |
| same | p.23 to 24, 8.2.2.4 and 8.2.2.7 | Equation 18: inductor peak in buck current limit = 80 mV / RSENSE + (VIN(MAX) - VOUT) / (L Fsw) x VOUT / VIN(MAX); equation 23: RSENSE(BUCK) = 80 mV / IOUT(MAX); "The filter resistance should not exceed 100 ohm" (the fitted 100 R). |
| same | p.25 to 26, 8.2.2.12 and 8.2.2.13 | Equations 31 to 34: QH1 conduction D I^2 R and switching 0.5 VIN IOUT (tr + tf) Fsw; QL1 conduction (1 - D) I^2 R; QH2 conduction I^2 R (on continuously in buck). Used for the illustrative loss scenario of section 4e, not an upper bound. |
| same | p.30, 10.1 | "When using the average current loop, divide the overall capacitor (CIN or COUT) between the two sides of the sense resistor to ensure small cycle-by-cycle ripple." This stage has no `cout_pre`: all output capacitance is after R43 (an observation for the stage owner; the ISNS filter R182/R183/C146 is the sheet's other remedy and is fitted). |
| TI CSD19532Q5B, SLPS414B, December 2013 revised May 2017, `v2/vendor/power/ti-csd19532q5b-n-fet.pdf` | p.3 | RDS(on) 4.6 typ / 5.7 max mOhm at VGS 6 V, ID 17 A (25 C); tr 6 ns, tf 6 ns at VGS 10 V, RG 0, ID 17 A; Coss 706 / 918 pF; Qrr 249 nC at 17 A; VSD 0.8 / 1.0 V; RthJA 50 C/W and RthJC 0.8 C/W on a 1 in2, 2 oz pad; TJ 150 C. The RDS(on) versus temperature curve was not read numerically: a factor 1.5 is assumed and labelled. |
| Coilcraft XAL1010, document 804-1 revised 02/25/26, `v2/vendor/power/coilcraft-xal1010.pdf` | p.1, the -682ME row and notes 5 and 6 | 6.8 uH +-20 percent, DCR 8.10 / 8.90 mOhm, Isat 21.8 A ("DC current at 25 C that causes an inductance drop of 30 percent"), Irms 14.0 A (20 C rise) and 18.5 A (40 C rise), "for reference only". |
| Vishay WSL, document 30100 revision 23-Nov-2023, `v2/vendor/vishay/vishay-wsl-power-metal-strip.pdf` | p.1 and p.2 | WSL2512 1.0 W at +70 C; component TCR +-110 ppm/C for 5 to 6.9 mOhm; F code +-1 percent; operating range -65 to +170 C; the derating curve on p.3 was not read numerically. |
| TI INA226, SBOS547C, June 2011 revised August 2026, `v2/vendor/ti/ti-ina226.pdf` | electrical characteristics | Shunt voltage input range -81.9175 to 81.92 mV, LSB 2.5 uV, bus 0 to 36 V. |
| JST VH catalogue, `v2/vendor/connectors/jst-vh-catalogue.pdf` (revision not printed) | p.1 | "Current rating: 10 A ... when using AWG #16 with the standard type header"; 7 A "when using AWG #18 with the shrouded type header"; contact resistance 10 mOhm initial, 20 mOhm after test. |
| TI TPS2596, SLVSET8A, May 2019 revised August 2019, `v2/vendor/power/tps2596.pdf` | p.6 and printed p.28 equation 7 | RILM [ohm] = 903 [A ohm] / (ILIM [A] - 0.0112 [A]), so positive load current ILIM = 903/RILM + 0.0112 A: **0.9142 A at 1 kohm**. At 453 ohm: 1.83 / 2.004 / 2.147 A (U23); at 909 ohm: 0.949 / 1.005 / 1.051 A, VDS = 0.5 V. Scaling the 909 ohm ratio gives a high estimate 0.956044 A, or 0.965583 A with R186 at -1 percent. Neither is a guaranteed 1 kohm maximum. |
| NiceRF SA868, datasheet v1.3 (2022-8), `v2/vendor/nicerf/nicerf-sa868-datasheet-v1.3.pdf` | p.4, current consumption | RX 60 mA; TX high power 900 typ / 1000 max mA. The exciter on D8 keys with the PA in PS-ALLTX. |
| Ebyte E22-900M30S user manual v1.20, `v2/vendor/lora/ebyte-e22-900m30s-user-manual-en-v1.20.pdf` | p.3 (PDF), "Instant power consumption" | TX current 650 mA typical, RX 14 mA, no maximum printed, no airtime figure. |
| Ground Control, RockBLOCK 9704 hardware page, snapshot 2026-09-27, `v2/vendor/rockblock/groundcontrol-docs-rockblock-9704-hardware-20260927.txt` (web page, no printed revision) | "V_IN+" and "Charge Current" | DC input "4.0V and 5.3VDC, at a maximum of 500mA" (the comparison assumes the default charger configuration); the supercapacitor charge current "limited to ~460mA" by default, "~800mA" with a pad bridged; the transmit burst is fed from the supercapacitors, so the input limit is separate from the transmit burst; the 500 mA comparison is conditional on the default configuration and supplies no duration. Product datasheet RB9704-001-JUN26 p.2: 60 mW idle, 1.4 W max. |
| MyriadRF LimeSDR Mini pages, snapshots 25 and 26 September 2026, `v2/vendor/limesdr/` | setup page, product page | "supply power (5V, 900 mA) via the USB type-A connector"; maximum power 4.5 W (USB 3.0 power limit). |
| Microchip KSZ9897R, DS00002330D (2019), `v2/vendor/microchip/microchip-ksz9897-datasheet.pdf` | p.169 Table 6-1 | AVDDL 460 mA + DVDDL 750 mA TYPICAL at 25 C and 1.2 V, 1000 Mbps, all ports 100 percent utilisation (read directly here; it is PWR-F03's figure). |
| TI TPS62933, SLUSEA4D, June 2021 revised August 2022, `v2/vendor/ti/ti-tps62933.pdf` (the option's part) | electrical characteristics; Table 10-2 | VIN 3.8 to 30 V, 3 A; IHS_LIMIT 4.2 / 5 / 5.8 A; for 5 V at 500 kHz: 52.5k / 10k, 6.8 uH, 20 uF typical and 10 uF minimum effective COUT; SS at least 6.8 nF. |
| Coilcraft XAL6060, document 887-1 revised 02/25/26, `v2/vendor/coilcraft/coilcraft-xal60xx-series.pdf` (the option's inductor) | the -682ME row | 6.8 uH, DCR 18.9 / 20.8 mOhm, Isat 9.2 A, Irms 7.0 / 9.0 A. |

Not held, and it matters: a LoRa airtime figure at the configured spreading factor (the E22 manual has none; the
Semtech SX1262 sheet is not under `v2/vendor/lora/`), an Iridium IMT session duration (Ground Control's pages give
none), a maker maximum for the E22's transmit current, and the WSL2512's thermal resistance on a board.

## 3. The loads that can coincide in PS-ALLTX

PS-ALLTX (CONOPS section 5, REQ-018's acceptance): every transmitter keyed for at most 60 s, the accessory outlets
(PoE, USB-C) off at their 0 W minimum contract, the pack heater and the standby WiFi card off, the other loads at
typical. The D-11 interlock drops **POE_EN and PD_EN only** (U30 forms OUTLET_OK = NOT (TR_APRS AND PA_EN); U26
sections 3 and 4 gate the two enables, `gen_sch_a.py` lines 1320 to 1376). D8_EN (U23, the mezzanine) and USBX_EN
(U32, the wall host port) are plain expander bits (U27 pin 7, U28 pin 4, lines 1470 and 1474) with no interlock, and
DEV_EN is pulled up. So in PS-ALLTX the three groups below are all live on +5V_DEV.

### 3a. Board B over J_5V_DEV (19 loads of `gen_sch_b.py` lines 84 to 97; intent sha256 `96ee391b...`)

The table in `dev_stage.out` section 3 gives every load: its declared allocation, its child rail's typical and peak
referred to 5.0 V (a converted child at V x I / (efficiency x 5.0)), the figure used for the M-tier and its basis.
The elements that matter:

| Load | Figure in PS-ALLTX | Label | Duration and repetition |
|---|---|---|---|
| U23, LimeSDR Mini 2.4 (transmitting) | 0.90 A | MAKER (host supplies 5 V, 900 mA; 4.5 W maximum) | assumed continuous for the comparison, no transmit waveform held; the declared 3.0 A peak is the eFuse's ILM, a switch setting, not a load figure |
| U21, E22-900M30S LoRa transmit | 0.65 A (0.70 declared peak) | MAKER (650 mA typical) | one packet's airtime, not held; the regulatory cap is 10 percent duty at 27 dBm (CONOPS section 5); a packet can coincide with the key-down start, so the comparison assumes its transmit figure through the plateau; this is not a measured duration |
| U24, RockBLOCK 9704 transmitting | 0.50 A (0.46 default charger) | MAKER (DC input maximum 500 mA; the burst is drawn from the supercapacitors) | input current depends on recharge state; the limit does not establish a continuous plateau; the declared 2.0 A peak is a project allocation above the maker's own input limit, kept in the D-tier |
| U25, +3V3_DEV buck (the always-on fabric: switch I/O, voters, GNSS, the two Zigbee radios' switch) | 0.90 A typical + 0.15 A for both Zigbee radios transmitting (+3V3_ZB 0.30 peak over 0.10 typical) = 1.05 A; 1.50 A at the child's 2.0 A peak | PROJECT | continuous |
| U26, KSZ9897R 1.2 V buck | 0.342 A | MAKER typical at 25 C (1.21 A at 1.2 V at 1000 Mbps, all ports busy) through project efficiency 0.85, not a maximum; the parent's 0.15 A is below it (PWR-F03) | continuous |
| F1 panel (board C), F3 QMX USB, U28 camera, F2 HDMI | 0.60, 0.30, 0.25 (0.50 peak), 0.10 (0.50 peak) A | PROJECT (allocations and port contracts) | continuous |
| U106, U206, U306 hub cores; U40, U50, U60 supervisor LDOs; U15 to U18 CP2102N | 3 x 0.104 (0.181 peak), 3 x 0.12 (0.25 peak), 4 x 0.02 A | PROJECT (child rails; the LDOs' parent entries of 0.05 A are below their children's 0.12 A, S-98 M7) | continuous |

The AP2112 entries reuse output-current allocations as approximate input current. The correct model is
IIN = IOUT + IGND (positive currents into VIN and out through load/GND), per DS39724 Rev.2-2 pp.2,8.
At VIN 4.3 V and no load the sheet gives IQ 55 uA typical / 80 uA maximum; that no-load row is not a
loaded ground-current bound. Reconciliation must include ground current without treating the LDOs as constant power.

Sums on the lead: **declared load sum 5.18 A** (the intent's own entries, against a declared 3.8 A typical and 6.0 A
peak); **M-tier 5.44 A**; **P-tier 7.22 A** (transmitters at maker figures, everything else at its declared child
peak); every declared limit with the eFuse settings counted as loads 10.8 A, above board B's own 6.0 A peak and the
lead's 10 A, which is not a load case but a declaration inconsistency for board B's owner (S-98).

### 3b. Board D, the D8 mezzanine behind U23 (intent sha256 `8d9f3b22...`, `gen_sch_d.py` lines 56 to 165)

The SA868 exciter keys with the PA (PA_KEY = KEY AND PA_EN on board D), so its transmit current is part of
PS-ALLTX for the whole key-down: **SA868 TX 0.90 A typical / 1.00 A maximum (MAKER)** through U21's +5V_TX branch
(plus U15 and the relay K1 at 0.02 A each), and the mezzanine's other loads 0.44 A (the 3.3 V LDO 0.17, the hub LDO
0.04, the PCM2912A codec 0.10, the monitor's touch port 0.05, U7 0.05, U3 0.03, all declared). **D8 M-tier 1.38 A
(1.48 A at the exciter's maximum); P-tier 1.59 A (+5V_TX's declared 1.15 A peak); D-tier 2.0 A (U23's nominal
limit, 1.83 to 2.15 A by SLVSET8A).** Duration: the key-down, at most 60 s, at least 2 s between key-downs (K1); the
APRS planning profile is a beacon of about 1 s every 10 minutes at a fixed site, at most one a minute on the move
(CONOPS section 5), but REQ-018's acceptance is the 60 s case.

### 3c. The wall host port behind U32

A USB 2.0 device on the Glenair feed-through (console or key fill, D-12): **0.50 A (BOUND, a bus-powered USB 2.0
device's maximum, conditional on that device class)**; corrected equation 7 gives 0.9142 A nominal.
The P-tier uses the 909 ohm row's ratio extrapolated to 1 kohm: 0.956044 A, or 0.965583 A with the
1 percent resistor at 990 ohm. These are estimates, not guaranteed maxima; declared 0.9 A (D-tier).
Nothing in PS-ALLTX's definition removes it, and a self-powered console draws about nothing; the M-tier keeps the
0.5 A bound because the mode does not say the port is empty.

### 3d. The coincident profile

For comparison only, assume all listed currents coincide and remain constant for a **60 s plateau**.
REQ-018 requires regulation through a 60 s key-down, but this does not establish each load's waveform.
Ebyte v1.20 printed p.2 gives no airtime; the RockBLOCK charger limit gives no plateau duration;
the LimeSDR supply figure gives no transmit waveform. The following is a conditional demand scenario:

| Tier | Composition | Converter output |
|---|---|---|
| D (cx1) | every declared limit: B 6.0 + D8 2.0 + wall 0.9 | **8.90 A** |
| Dt (cx1) | declared, D8 at its typical: B 6.0 + D8 1.0 + wall 0.9 | 7.90 A |
| M | maker figures where held, declared typicals elsewhere, every transmitter keyed: B 5.44 + D8 1.38 + wall 0.50 | **7.32 A** (7.42 A with the exciter at its 1.0 A maximum) |
| P | maker figures for the transmitters, declared child peaks elsewhere: B 7.215176 + D8 1.590 + wall 0.956044 | **9.761220 A**, or 9.770759 A with R186 -1 percent |

The registry's own model (POWER-THERMAL.md line 709) puts the rail's HIGH case at 7.8 A, between the M- and D-tiers.

## 4. The comparison

### 4a. The average loop (output-side sense, so the demand compares 1:1)

Threshold on the fitted R43: 43 / 50 / 57 mV over 6 mOhm = 7.17 / 8.33 / 9.50 A; with the +-1 percent initial
tolerance **7.10 to 9.60 A**; with the shunt 50 K hot (TCR +-110 ppm/K, 0.55 percent) **7.06 to 9.65 A**. The ISS
over gm offset (3.75 to 6.35 uA over 1 mS is 3.75 to 6.35 mV, 0.6 to 1.1 A on 6 mOhm) is named, not added: the VSNS
row is specified at VSS 0.8 V, so the published band is taken as the regulation point.

| Tier | Demand | vs minimum 7.06 A | vs typical 8.33 A | vs maximum 9.65 A |
|---|---|---|---|---|
| D | 8.90 A | **FAIL by 1.84 A** | FAIL by 0.57 A | PASS 0.75 A |
| Dt | 7.90 A | FAIL by 0.84 A | PASS 0.43 A | PASS 1.75 A |
| M | 7.32 A | **FAIL by 0.27 A (3.8 percent)** | PASS 1.01 A | PASS 2.33 A |
| Mx | 7.42 A | FAIL by 0.37 A | PASS 0.91 A | PASS 2.23 A |
| P | 9.761220 A | FAIL by 2.704324 A | FAIL by 1.427887 A | **FAIL by 0.112191 A** |

**Verdict: FAIL, conditional on the load figures.** Even the M-tier, built from the makers' figures and the boards'
own typicals, sits above the loop's minimum. Sustained demand at that level can invoke limiting.
This does not establish onset, complete-rail collapse or the actual PS-ALLTX waveform.

### 4b. Illustrative timing and unresolved collapse

SNVSAI1D pp.6-7,16-17 gives **no closed-loop time constant or guaranteed onset interval**.
CSS/gm = 47 nF / 1 mS = 47 us is a dimensional ratio only. Assume CSS = 47 nF, constant typical gm =
1 mS, initial SS = 1.21 V, VREF = 0.8 V, and constant positive overdrive DeltaV relative to the effective
regulation point. If the NET SS discharge current is assumed to equal gm * DeltaV, then
`t = CSS * (1.21 - 0.8) / (gm * DeltaV)` [s]. Current out of CSS is positive and dVSS/dt is negative.
This assumes net current rather than establishing the pullup/pulldown balance; no ISS offset is added to
VSNS, which is specified at VSS = 0.8 V. gm itself is typical at 55 mV differential and VSS = 0.5 V.

The **illustrative estimates, not bounds**, are 64.233, 5.668 and 1.853 ms for 0.3, 3.4 and 10.4 mV.
Assuming the output tracks SS with gain 5.088/0.8 then gives illustrative droop magnitudes 40.6, 460.1 and
1407.3 V/s; dVOUT/dt is negative. Neither calculation proves that any actual radio burst lasts long enough
for limiting, or that a shorter burst can be supported by the capacitors.

A regulated buck can draw more input current as voltage falls while maintaining fixed output power and
assumed efficiency. AP2112 LDOs instead draw output current plus ground current (DS39724 Rev.2-2 pp.2,8).
Dropout, UVLO, load response and restart change that model. **Complete-rail collapse and recovery remain
INCONCLUSIVE.** Board A and B owners must measure simultaneous SS, rail voltage and branch/load current
through actual PS-ALLTX bursts and controlled overload steps, including dropout/UVLO and recovery.
Those waveforms determine loop onset, droop and any collapse, rather than the dimensional 47 us ratio.

### 4c. The cycle-by-cycle limit at the demand

Buck valley limit 66 / 80 / 94 mV over 5 mOhm (+-1 percent): 13.07 / 16.0 / 19.0 A of inductor valley current; as
an output current (valley plus half the ripple) 14.3 / 17.3 / 20.3 A. At the D-tier's 8.9 A the inductor valley is
7.63 A, 5.4 A under the lowest limit; the inductor peak with the worst ripple is 10.7 A against Isat 21.8 A and Irms
14.0 A. **PASS: the cycle-by-cycle limit never acts at the coincident demand; the average loop is the governing
limiter.** Observation for the stage owner, not S-99's verdict: at the tolerance corner (VCS 94 mV, R177 minus 1
percent, L minus 20 percent, 180 kHz) the backstop's inductor peak in a hard overload is 22.6 A, 0.8 A over Isat
(INFERRED); the dynamic ordering of the two loops is unverified; hard shorts and overload steps require waveform assessment.

### 4d. The shunt

R43 dissipates **0.321691 W nominal or 0.324908 W at +1 percent** at the 7.322235 A M-tier
(P = I^2 R, positive loss), 0.48 W at 8.9 A and 0.56 W at the initial loop maximum 9.6 A:
32.49, 48 and 56 percent using +1 percent resistance
of the WSL2512's 1.0 W at +70 C. **PASS on the rating up to +70 C ambient**; above +70 C the sheet's derating curve
applies (not read numerically). The element's temperature rise, which sets the TCR term, needs the board's copper
around the 2512 land: **INCONCLUSIVE: layout calculation then actual shunt-temperature measurement** (a scenario of +50 K was assumed
above and costs 0.55 percent of threshold). R177 carries the low-side share only: 0.28 W at 8.9 A.

### 4e. The FETs (illustrative thermal scenario, not an upper bound)

At 8.9 A with RDS(on) 5.7 mOhm x 1.5 hot (assumed), the sheet's edges slowed 3 x under the LM5176's 1.8 / 1.1 ohm
drivers (assumed), Qrr scaled to the current, on the sheet's 1 in2 2 oz pad (RthJA 50 C/W):

| FET | 12.4 V in | 16.8 V in | Rise on the sheet's pad |
|---|---|---|---|
| Q35 boost high side, on continuously | 0.68 W | 0.68 W | +34 K |
| Q32 buck high side | 0.28 cond + 0.41 sw + 0.02 Coss + 0.33 Qrr = 1.03 W | 0.21 + 0.55 + 0.03 + 0.45 = 1.24 W | +62 K |
| Q33 buck low side | 0.40 cond + 0.17 dead time = 0.56 W | 0.47 + 0.17 = 0.64 W | +32 K |
| Q34 boost low side | off | off | 0 |

Stage loss scenario at 16.8 V: FETs 2.6 W, shunts 0.76 W, DCR 0.70 W (core loss not held): about 4.0 W, efficiency
about 0.92 against the declared 0.90 floor. From +50 C inside air (K2's ceiling at key-down start) the hottest FET
calculates to about 112 C against TJ 150 C: **a scenario, no thermal PASS or upper bound**.
The typical switching times were specified at VDS 50 V, VGS 10 V, ID 17 A and RG 0; assumed multipliers
3 and 1.5 do not establish maxima on this board. RthJA is board dependent. Layout loss/thermal calculations
must be followed by actual FET and shunt temperature measurements with switching waveforms over intended
loads, VBAT and ambient, including the 60 s key-down and recovery. Check junction estimates and shunt
rating/TCR against those results. PT-4 retains this obligation; no bench figure exists (FW-A15).

### 4f. Copper, monitor, lead

- **Board A copper:** the filed `dc_drop` and `dc_density` verdicts of 21 September (board sha 58e26c67, judged at
  the declared 4.0 / 6.9 A) hold +5V_DEV and SD_OUT as MET, with no per-rail margin recorded. At 8.9 A the density
  reading scales by 1.29: **INCONCLUSIVE until `dc_density` runs on the regenerated board with the corrected
  declaration** (calculation, not measurement). PI-001 and PI-002 on board A read FAIL today on other rails (CH_SRP,
  PD_VPWR, PD_VBUS and ten more), so the board is not at a copper verdict anyway.
- **INA226 U11:** 58.2 mV at the loop's maximum 9.6 A, 71 percent of the +-81.92 mV range; bus 5.09 V of 36 V; LSB
  2.5 uV reads 0.42 mA. **PASS.** The calibration register is a firmware item (the generator's own note).
- **JST VH lead J_5V_DEV at 6.0 A (B's declared peak):** 10 A rating for AWG 16 with the standard header, margin
  4.0 A, **PASS**; 5.44 A (M) and 7.22 A (P) also under it. The lead's voltage drop (25 mV in the copper plus up to 240
  mV in four contacts at 10 mOhm against a 2 percent budget with no lead share) is S-98's open item, unchanged here.
- **The D8 lead J_MEZZ_PWR1 (VH, AWG 18 per ASSEMBLY.md section 4)** at 1.4 to 2.0 A: JST states no rating for AWG 18
  with the standard header (cx1's J1 finding for +54V_POE): **INCONCLUSIVE**, the same enquiry text serves both.

### 4g. What the stage asks of VBAT

At 0.90 efficiency: 3.25 A at 15.5 V for the D-tier (4.06 A at 12.4 V), **2.670648 A for the M-tier** at 5.088 V out and 15.5 V in
(IIN = VOUT * IOUT / (eta * VIN), positive battery draw). VBAT's load map
carries Q32 at 2.0 A typical; the 8.9 A case is 1.25 A over that entry at 15.5 V. REQ-018's pack current (18 A
peak) is FEA-004's; the increment is noted for the energy chain's owner, not judged here.

### 4h. Hand recomputation of the marginal case

The loop's minimum with the tolerances: 0.043 V / (0.006 ohm x 1.01 x (1 + 110e-6 x 50)) = 0.043 / (0.006 x 1.01 x
1.0055) = 0.043 / 0.0060933 = **7.0569 A**. After option B the D-tier demand is 6.0 + 0.9 = 6.9 A: margin 7.0569 -
6.9 = **0.157 A**, the script's 0.16 A. The M-tier before any change: 5.442 + 1.380 + 0.500 = 7.322 A; margin 7.0569
- 7.322 = **-0.265 A**, the script's -0.27 A.

## 5. The options

"Raising the threshold alone is not evidence of adequate capacity" (the owner's instruction): every option is judged
at every downstream element.

| Option | What it does | Result at the loop's minimum (D / M / P tiers) | Downstream test | Two-part test (21 September ruling) |
|---|---|---|---|---|
| A. Re-rate: R43 5.0 mOhm (or 5.6) | initial +/-1% loop 8.514851 / 10.000000 / 11.515152 A; hot max 11.578835 A (at 5.6: 7.602546 / 8.928571 / 10.281385 A; hot max 10.338246 A) | D FAIL (8.9 > 8.514851 initial, > 8.468276 hot), M PASS, P FAIL at 5.0 | **FAILS at the lead:** the loop's hot maximum 11.578835 A (10.338246 A) is over the JST VH's 10 A contact rating in a board-B fault that a CCM stage without hiccup holds indefinitely, with no other protection on the lead (board B has no input fuse on +5V_DEV, only a TVS). Absolute FET current ratings do not prove switching or thermal capacity; inductor, shunt and routed copper require their own checks. Raising the threshold is not evidence of adequate capacity. 6 mOhm is pinned by the lead, the generator's own reason. Rejected. | would be the session's, but it fails the test above |
| B. The D8 mezzanine on its own buck from VBAT | a TPS62933 (C3200405, fitted twice on board A) at 5.088 V (53.6k / 10k), 6.8 uH XAL6060-682ME (Isat 9.2 A over the part's 5.8 A maximum high-side limit; Coilcraft 887-1), two 22 uF 10 V 1210, 10 uF 25 V + 100 nF input, 10 nF SS, 100 nF boot, EN on RAIL_EN; U23 stays as the mezzanine's eFuse (2.0 A limit, OVLO, D8_EN) fed from the new rail | **D 6.900 A PASS by 0.156897 A; M 5.942235 A PASS by 1.114661 A; P 8.171220 A FAIL by 1.114324 A (8.180759 A with R186 tolerance, FAIL by 1.123863 A)** | new buck at 2.0 A: ripple 1.04 A, peak 2.52 A against IHS_LIMIT 4.2 A minimum: PASS; VBAT +0.91 A at 12.4 V, +0.4 A typical (the VBAT map takes a U41 entry); board area about 1.5 cm2 and ten new component references (U41, L13, C227-C232, R217, R218); the inductor order code needs parts-stream certification | changes no line of `tools/reserved.json` (no class names `gen_sch_a.py`); spends nothing the owner decides (a BOM line inside the board, no purchase); changes no claim about the kit (the mezzanine keeps its 5 V, its 6 percent budget improves because the new source is regulated at the load's end); accepts no residual risk a measurement here cannot remove (the P-tier is board B's declarations and the bench's). **The session's.** |
| C. B plus the wall host port on the outlet interlock | U26's spare section 1 (inputs at GND today): USBX_EN_HW = USBX_EN AND OUTLET_OK, into U32's EN; no new part | D 6.00 A PASS by 1.06 A; M 5.44 A PASS by 1.61 A; P 7.22 A FAIL by 0.16 A | the console or key-fill device loses VBUS for each PA key-down (up to 60 s) and re-enumerates after; a self-powered console only loses the port | extends D-11 (an owner ruling) to a port D-12 defines as the console: a claim about the kit's behaviour; B meets the conditional declared demand while preserving console availability: under the standing rule of 26 September the session takes the recommendation, which is **not now**; kept as the fallback: removes declared 0.9 A, M-tier 0.5 A or estimated P-tier 0.956044 A (0.965583 A with R186 tolerance) |
| D. Declare the 8.9 A bound with the fold-back named (cx1's third option) | a declaration only | unchanged FAIL | leaves REQ-018's "every rail in regulation" unmet on the record | not an engineering option |
| E. Move D8 or the wall port to +5V_S1 / +5V_S3 (AP64500, 5 A) | | | S1 4.65 A PLAN in PS-ALLTX (PWR-F02, 7 percent margin), S3 about 4.2 A with its card off (cx1): no headroom for 1.4 to 2.0 A | rejected on the numbers |

**Recommendation, authority SESSION: option B, now, in board A's circuit round**, with option C held as the
fallback. **Both B and B plus the interlock remain configurations.** The owner's standing rule of
26 September supports SESSION choosing B because it preserves console availability while lowering the declared
demand below the loop minimum without moving the lead protection point; it uses parts the board already certifies; it removes the mezzanine
from a rail whose 2 percent budget it was sharing (A's +5V_D8 note: the eFuse-to-header copper alone spent 2.68
percent of a 6 percent budget shared with board D). The recommendation remains a circuit candidate, not closure of S-99. The following remain unresolved:

- M/P tiers versus the loop: reconcile S-98 allocations, LDO ground current and maker typicals, obtain a
  guaranteed TPS2596 1 kohm maximum or assess the actual setting, and measure coincident current at the
  converter shunt and J_5V_DEV. The pre-split M-tier exceeds the minimum by 0.265339 A; post-split M-tier
  passes only as a conditional allocation. Both pre- and post-split P-tiers fail the minimum.
- Timing and capacitor support: obtain configured radio airtime/waveform documents where available;
  measure current deficit, SS and rail voltage with actual bursts and load steps. No onset bound is held.
- Collapse/recovery: A/B owners measure rail current versus falling voltage, dropout, UVLO and restart
  with fitted loads; the AP2112s do not support a blanket constant-power model.
- Thermal capacity: A owner performs layout loss/thermal analysis and PT-4 FET/shunt temperature and
  switching-waveform measurements over intended operating conditions.

Reversal: delete the stage and return U23's input to +5V_DEV (the draft's replacements in reverse).

## 6. Item 4: every remaining INCONCLUSIVE made actionable

The table per rail is `RAILS-ACTIONABLE.md`. The five mode currents combine project allocations, supply
requirements, typicals and some component maxima; these do not establish complete rail maxima or waveforms.
Each keeps a documentation/calculation action and a separately named bench test (TEST-PLAN.md, new rows PT-1 to PT-5
proposed) that decides the mode current. Design-critical uncertainty stays on its gate: +5V_DEV's coincident demand
blocks board A's layout entry until option B is applied and PWR-001 and INT-001 re-taken; +5V_S2's 7.28 A all-peak
bound (cx1) blocks nothing today but is a P-tier item of the same kind; +54V_POE's AWG 18 rating blocks the cable
release, not the boards.

## 7. Deliverables and checks

- `dev_stage.py`, `dev_stage.out`: corrected arithmetic with the same four input hashes; required checks and
  reproducibility evidence are recorded in `CORRECTION.md` and `correction_checks.out`.
- `apply_d8_split_draft.py`: five replacements, ten new references; only `--check` is executed. S99-DEV
  includes the entire declaration note and its preceding comment. The integrator must rebase its old
  text onto stream s98's integrated line; exact held and expected s98 old/new text is in `CORRECTION.md`.
- `REGISTRY-DRAFT.md` remains unapplied. PWR-001 and INT-001 are future integrator checks, not run here.
- Dash scan covers only this job's changed files. No generator, registry or verdict writer was changed or run.
