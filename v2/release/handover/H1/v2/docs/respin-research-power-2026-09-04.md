# PCB-A A19 power respin: documented part research

Date: 4 September 2026. Scope: items 1 to 6 of the coordinator's brief for the A19 power board (1S12P Samsung 35E node, 3.0 to 4.2 V, 42 Ah; SHORE_12V from a TRACO TEN 40-2412WIN on the dock strip; Pi 5 rail 5 V up to 5 A; module rail 5.05 V, 2.2 A continuous, 6.5 A worst-case bursts; JLCPCB assembly).

Method: every number below comes from a manufacturer document saved in this folder (`respin/`), cited as (file, page). Where I computed a value from a sheet equation the line says "computed". LCSC numbers and stock come from the JLCPCB parts API (`jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`, queried 4 Sep 2026); the lcsc.com search page itself is JavaScript-rendered and returned no part numbers to curl. Stock figures are a snapshot. No git repository was touched.

Added constraint (coordinator, mid-task): every part that stands on the dock strip under PCB-A (item 5, the LT8705A tracker stage, and any bulk capacitor named there) must be at most about 12 mm tall. Heights are quoted from the sheets in item 5 and low-profile parts are preferred.

## 0. Documents used (all in `respin/`)

| File | Document | Source and route |
|---|---|---|
| tps61288.pdf (pre-existing) | TI TPS61288, SLVSFP3C, Aug 2020 rev Mar 2022 | already in folder |
| tps2595.pdf (pre-existing) | TI TPS2595xx, SLVSE57C, Jun 2017 rev Apr 2018 | already in folder |
| bq25798.pdf | TI BQ25798, SLUSDV2C, May 2020 rev Jun 2026, 151 pages | ti.com/lit/ds/symlink/bq25798.pdf, direct |
| bq25792.pdf | TI BQ25792, SLUSDG1C, Jun 2020 rev Aug 2022, 143 pages | ti.com returned 404 today; Wayback capture 2022-10-27 of ti.com/lit/ds/symlink/bq25792.pdf |
| bq24610.pdf | TI BQ24610/BQ24617, SLUS892D, Dec 2009 rev Dec 2019 | ti.com direct |
| bq25601.pdf | TI BQ25601, SLUSCK5A, Mar 2017 rev Mar 2023 | ti.com direct |
| bq27441-g1.pdf | TI bq27441-G1, SLUSBH1C, Nov 2013 rev Dec 2014 | ti.com direct |
| bq34z100-g1.pdf | TI BQ34Z100-G1, SLUSBZ5D, Jan 2015 rev Apr 2021 | ti.com direct |
| max17048.pdf | Maxim/ADI MAX17048/MAX17049, 19-6171 Rev 7, 11/16 | analog.com refused curl; Wayback copy of analog.com/.../MAX17048-MAX17049.pdf |
| tps2596.pdf | TI TPS2596, SLVSET8A, May 2019 rev Aug 2019 | ti.com direct |
| tps3421.pdf | TI TPS3420/3421/3422, SBVS211B, Aug 2012 rev Apr 2015 | ti.com direct |
| lt8705a.pdf | ADI/Linear LT8705A, 8705af, 44 pages | analog.com refused curl; Wayback copy of analog.com/.../8705af.pdf |
| lt8705-farnell.pdf | Linear DC1924A demo manual (LT8705, 36 to 80 V in, 48 V 5 A out), dc1924af, 8 pages | farnell.com/datasheets/1753552.pdf (this URL is the demo manual, not the LT8705 datasheet) |
| ltc2954.pdf | Linear LTC2954, 2954fb, 18 pages | analog.com copy not archived; Wayback capture 2018-02-19 of cds.linear.com/docs/en/datasheet/2954fb.pdf |
| coilcraft-xal1060.pdf, coilcraft-xal1010.pdf, coilcraft-xal1510.pdf, coilcraft-ser2900.pdf | Coilcraft Documents 812, 804, 947, 644 | coilcraft.com/getmedia/... (URLs taken from the JLCPCB part records; the Coilcraft product pages answer 403) |
| wurth-74439370047/033/068/100.pdf, wurth-74435572200.pdf | Wurth WE-XHMI 1510 series and WE-HCI 74435572200 sheets, rev 2024-10-26 and 2025-02-06 | we-online.com/components/products/datasheet/<code>.pdf, direct |
| vishay-wsl.pdf | Vishay WSL, Document 30100, rev 23-Nov-2023 | vishay.com direct |
| bourns-css2h-2512.pdf, bourns-css2h-3920.pdf | Bourns CSS2H-2512 and CSS2H-3920 sheets | bourns.com direct |
| lcsc-panasonic-eehzk1v101xp.pdf | Panasonic ZK series (hybrid, 125 C, 4000 h) | LCSC-hosted copy (wmsc.lcsc.com) |
| lcsc-panasonic-35svpf39m.pdf | Panasonic OS-CON SVPF series | LCSC-hosted copy |
| lcsc-ralec-lr2512-23r005f4.pdf | RALEC LR series metal alloy low resistance resistors, 27 pages | LCSC-hosted copy |

Not obtained: the Cyntec CMLE105T sheet (only referenced through the TI table), the Semitec 103AT-2 thermistor sheet (only referenced through the TI sheets), a TDK sheet for the ceramic capacitors named in the LT8705A example.

## 1. Single-cell Li-ion charger from SHORE_12V, 3 A or more, TS input, I2C

### BQ25798 (bq25798.pdf)
- Input: VBUS operating range 3.6 to 24 V, 30 V absolute maximum (p1; EC table VVBUS_OP p9). ACOVP default 26 V, options 7/12/22/26 V (p3). 12 V from the TRACO is inside the range.
- Topology: buck-boost, four integrated switching MOSFETs, integrated BATFET, integrated input and charge current sensing, 750 kHz or 1.5 MHz (p1). NVDC power path, SYS held at or above VSYSMIN (p1).
- Charge current: ICHG register REG0x03/04, range 50 mA to 5000 mA, 10 mA step (p61). POR default 1 A for every cell count (p25, Table 7-2). Input current limit IINDPM 100 mA to 3300 mA, 10 mA step (p63).
- Charge voltage: VREG range 3000 to 18800 mV, 10 mV step (p60); for the 1s setting the allowed window is 3 V to 4.99 V, default 4.2 V (p25, Table 7-2). VSYSMIN 2.5 to 16 V, 250 mV step (p10, p59), 1s default 3.5 V (p25). Cell count and default switching frequency come from the PROG pin resistor at power-on and can be overridden through the CELL bits (p25, p26).
- TS input: fixed T1 and T5 comparators, VT1 rising 73.3 percent of REGN (0 C with a 103AT) and VT5 falling 34.2 percent of REGN (60 C with a 103AT) (p13, p14); programmable T2 through TS_COOL (5/10/15/20 C, default 10 C) and T3 through TS_WARM (40/45/50/55 C, default 45 C), all defined with RT1 = 5.24 kOhm and RT2 = 30.31 kOhm and a 103AT thermistor (p83). The TS resistor network is Figure 7-12 (p46); for T1 = 0 C and T5 = 60 C the sheet gives RT1 = 5.24 kOhm, RT2 = 30.31 kOhm (p46). The pin table recommends a 103AT-2 10 kOhm thermistor (p5). Charge current and voltage in the cool and warm windows are programmable (JEITA_ISETC, JEITA_ISETH, JEITA_VSET, p82).
- Safety timer: fast-charge timer CHG_TMR = 5, 8, 12 or 24 h (limits 4.5 to 5.5, 7.2 to 8.8, 10.8 to 13.2, 21.6 to 26.4 h; p17), default 12 h (p41); pre-charge timer 2 h (p17). EN_CHG_TMR = 0 disables the fast-charge timer (p44, register p69). TMR2X_EN halves the clock during input DPM or thermal regulation (p44). A 42 Ah bank at 3 A needs about 14 h (computed): select the 24 h option or disable the timer.
- Status for the Pi: I2C target address 0x6B (p53, p54); 16-bit ADC for voltages, currents and TS (p1); TS_COLD/COOL/WARM/HOT status and flag bits (p92, p102); timer status bits (p90).
- Extras over the BQ25792: VOC-sampling MPPT for a PV input and Backup Mode (p1, p3).
- Package: RQM, 29-pin VQFN-HR, 4.0 x 4.0 mm (p1, p4).
- LCSC: BQ25798RQMR C2876593, extended, stock 223.

### BQ25792 (bq25792.pdf)
- Same family: 3.6 to 24 V VBUS (p1; EC VVBUS_OP p10), 5 A with 10 mA resolution (p1), timer options 12 h and 24 h rows (p19) and EN_CHG_TMR disable (p41), same VT1 73.3 percent and VT5 34.2 percent thresholds (p15), QFN-29 4 x 4 mm (p3). Comparison table p3: no MPPT, no Backup Mode, otherwise the same pinout and package as the BQ25798. I2C address 0x6B (bq25792.txt lines 3118 and 3205, section 9).
- LCSC: BQ25792RQMR C2862876, extended, stock 5471 (far better stocked than the BQ25798 today).

### BQ24610 (bq24610.pdf)
- Stand-alone (no I2C) synchronous buck charger controller, 5 to 28 V VCC operating range, 1 to 6 cells, up to 10 A charge current, VQFN-24 (RGE) 4.00 x 4.00 mm (p1, p4, p7).
- Charge current: ICHARGE = V(ISET1) / (20 x RSR), ISET1 0 to 2 V, full-scale sense 100 mV, RSR 10 mOhm default (p17, eq 2); ITERM = V(ISET2) / (100 x RSR) (p18, eq 5). External sense resistors RAC and RSR, external MOSFETs and inductor (BOM p31).
- TS: VLTF 73.5 percent of VREF (cold), VHTF 37 percent (hot), VTCO 34.4 percent (cut-off), 400 ms deglitch (p9); charge suspends outside the window (p21).
- Safety timer: tCHARGE = CTTC x KTTC with KTTC = 5.6 min/nF, CTTC 0.01 to 0.11 uF for 1 to 10 h (p10, p18); accuracy specified only up to 0.11 uF (p10). TTC tied to VREF disables the timer but keeps termination; TTC low disables both (p5, p18). For a 14 h charge the timer must therefore be disabled (TTC to VREF).
- LCSC: BQ24610RGER C19384, stock 1149.

### BQ25601 (bq25601.pdf)
- 1-cell 3 A buck charger, I2C, input 3.9 to 13.5 V operating, 22 V absolute maximum, WQFN-24 4.00 x 4.00 mm (p1).
- ICHG 0 to 3000 mA, 60 mA step (p10); VBATREG 3.856 to 4.624 V, 32 mV step (p10).
- TS: VT1 73.3 percent, VT2 68 percent (cool: charge to ICHG/2 and 4.2 V), VT3 44.7 percent, VT5 34.2 percent of VREGN (p11, p12); RT1/RT2 equations p23.
- Safety timer: CHG_TIMER = 5 h or 10 h (10 h row specified 8 to 12 h, p13), default 10 h (p38); EN_TIMER bit disables it (p24, p38); half-clock during DPM/JEITA cool/thermal regulation (p24). 14 h at 3 A needs the timer disabled.
- Caveat: the 13.5 V maximum operating input leaves little margin above a nominal 12 V rail.
- LCSC: BQ25601RTWR C468236, stock 5649.

### Recommendation, item 1
BQ25798 (or the BQ25792 when MPPT/backup are not wanted and stock decides; the pinout and package are the same, p3 of either sheet). Reasons from the sheets: 12 V input inside 3.6 to 24 V; 3 A programmable in 10 mA steps up to 5 A; 1s VREG window 3 to 4.99 V; JEITA with fixed 0 C and 60 C limits and programmable cool/warm points on a 103AT network; 24 h timer or timer off for the 14 h charge; I2C status and 16-bit ADC readable by the Pi; single QFN with all FETs and current sensing inside. Bench-fit item: a 103AT-2 10 kOhm thermistor on the pack (Semitec 103AT-2 is on LCSC as C5346323, through-hole, stock 0; the sheet's thresholds are defined for that part only).

## 2. Fuel gauge for a 42 Ah single cell on I2C

### BQ27441-G1 (bq27441-g1.pdf)
- Single-cell system-side Impedance Track gauge, external 10 mOhm 1 percent high-side sense resistor, factory pre-calibrated for 10 mOhm (p1, p4), 12-pin SON 2.50 x 4.00 mm (p1), 400 kHz I2C (p1).
- Coulomb counter input range VSR = BAT plus or minus 25 mV (p7, section 8.10). With the 10 mOhm resistor the sheet is built around, that is plus or minus 2.5 A (computed); the kit's 15 A bursts would give 150 mV. Absolute maximum differential across SRP-SRN is 2 V (p5), so the bursts are not destructive, but they are outside the measured range.
- Capacity: the data sheet lists DesignCapacity() as a mAh register (p12) and states no capacity ceiling itself; the TRM is not among the documents fetched, so no ceiling is claimed here.
- Sense resistor guidance: 1 percent, 50 ppm, 1 W (p16).
- LCSC: BQ27441DRZR-G1B C473374, stock 589.
- Verdict: unsuitable at 15 A with the 10 mOhm the sheet is calibrated for.

### BQ34Z100-G1 (bq34z100-g1.pdf)
- Wide-range Impedance Track gauge, batteries from 3 V to 65 V, capacities up to 29 Ah and currents up to 32 A "with standard configuration options" (p1); larger packs use the SCALED configuration flag, in which the 1 mAh and 1 mA units are scaled through calibration (p15, p16). A 42 Ah design capacity therefore needs the scaled setup (Design Capacity data flash range 0 to 32767 mAh, p25).
- Coulomb counter input range V(SR) = V(SRN) minus V(SRP), minus 0.125 V to plus 0.125 V (p6, section 6.10); the sense resistor sits in the low side of the battery circuit (p10). BAT pin input range up to 5 V (p5), so a 1S cell connects without the external divider; the "Voltage Divider" calibration parameter defaults to 5000 mV (p29).
- External NTC thermistor supported (p1). I2C device address 0xAA/0xAB (8-bit write/read) (p41). Package 14-pin TSSOP 5.00 x 4.40 mm (p1).
- LCSC: BQ34Z100PWR-G1 C91302, stock 6777.

### MAX17048 (max17048.pdf)
- 1-cell ModelGauge fuel gauge, voltage-based (no sense resistor, "does not accumulate errors, unlike coulomb counters"), plus or minus 7.5 mV/cell measurement (p1). VDD 2.5 to 4.5 V (p2). No capacity setting exists; the model is voltage-derived, and the sheet says ModelGauge performs best with a custom model (p7). I2C slave address fixed to 0x6C write / 0x6D read (p16). Packages 8-pin TDFN-EP 2 x 2 mm or WLP (p1, p18).
- LCSC: MAX17048G+T10 C2682616, stock 15439.

### Sense element for the BQ34Z100-G1 (15 A bursts, 2.2 A continuous)
- Value: with the plus or minus 125 mV input range (p6) the resistor must be at most 125 mV / 15 A = 8.3 mOhm (computed); 5 mOhm gives 75 mV at 15 A and 11 mV at 2.2 A (computed). Dissipation 15 A squared x 5 mOhm = 1.13 W during bursts, 24 mW at 2.2 A (computed).
- RALEC LR2512-23R005F4: metal alloy 2512, code "3" = 3 W, R005 = 5 mOhm, F = plus or minus 1 percent (lcsc-ralec-lr2512-23r005f4.pdf p1 part-number key; p3 table, 2512 3 W row, 2.6 to 10 mOhm at TCR within plus or minus 25 ppm/C). LCSC C154688, stock 15492. Recommended.
- Bourns CSS2H-2512K-5L00: 5.0 mOhm / 2.5 W (bourns-css2h-2512.pdf p1), and CSS2H-3920K-5L00: 5.0 mOhm / 3 W (bourns-css2h-3920.pdf p1); both marked "available upon request" (p1 of each); LCSC CSS2H-3920K-5L00 C2931257 stock 0.
- Vishay WSL2512: 1.0 W at 70 C, 0.003 to 0.5 Ohm (vishay-wsl.pdf p1); below the 1.13 W burst figure, so not chosen.

### Recommendation, item 2
BQ34Z100-G1 with a 5 mOhm 3 W 2512 low-side shunt (RALEC LR2512-23R005F4), Kelvin-connected SRP/SRN, external NTC, I2C to the Pi; the 42 Ah capacity is entered with the SCALED configuration (p15). Fallback with no shunt: MAX17048 (voltage-based, any capacity, but no coulomb counting under 15 A bursts). The BQ27441-G1 is ruled out by its plus or minus 25 mV sense range (p7).

## 3. TPS61288 rails

*(Note 4 Sep night: the rail A caveat below (13.1 A peak against the 12 A guaranteed limit) was written for a single module rail; the owner's ruling of appendix 32.21 splits the module loads over two converters, each about 6.5 A on the cell side at 3.0 V, so the caveat and the open decision at the end of this item are closed.)* (tps61288.pdf, SLVSFP3C)

### Device facts
- 18 V, 15 A fully integrated synchronous boost, 2.5 x 3.0 mm VQFN-HR 11-pin (RQQ) (p1, p5); VIN 2.0 to 18 V, 2.4 V minimum for start-up (p1); recommended operating: VOUT 4.5 to 18 V, effective L 0.8 to 5.6 uH, effective CIN 1 to 10 uF, effective COUT 10 to 1000 uF (p5).
- Switching frequency 440 / 500 / 600 kHz min/typ/max (p6). Switch peak current limit ILIM 12 / 15 / 17.1 A min/typ/max (p6). RDS(on) 8.5 mOhm high side, 6.5 mOhm low side (p6). VREF 0.588 / 0.6 / 0.612 V (p6). KCOMP 13.5 A/V, GEA 180 uS (p6).
- Pins: FB, COMP, PGND, SW (4, 9), VOUT, EN, VIN, BST, AGND, VCC (p4). There is no MODE pin: PFM at light load and PWM at heavy load are automatic (p1, p10). EN: logic high enables, low is shutdown (p4); VIH 1.2 V max, VIL 0.4 V min, internal pull-down 850 to 1100 kOhm (p6); "other pins" absolute maximum 6 V (p5). Shutdown current 2.1 uA max (p6).
- Two orderables: TPS61288 (HotRod) and TPS61288L (HotRod Lite), "TPS61288L is recommended with thermal improvement" (p1). LCSC: TPS61288RQQR C5219223 stock 2029; TPS61288LRQQR C7498841 stock 7139.
- FB divider: R1 = (VOUT minus VREF) x R2 / VREF (p14, eq 1); keep R2 below 300 kOhm; add 27 pF across R2 when R2 exceeds 15 kOhm (p14).
- Inductor: 1.0 to 4.7 uH; IDC = VOUT x IOUT / (VIN x eta) (eq 2), IPP = VIN x (1 minus VIN/VOUT) / (L x fSW) (eq 3), ILpeak = IDC + IPP/2 (eq 4); design with fSW minimum, L minus 30 percent and a low efficiency; set the current limit above ILpeak and choose an inductor with saturation current above the current limit (p14, p15). Table 9-2 recommended parts: Cyntec CMLE105T-2R2MS-99 (2.2 uH, 4.5 mOhm, 26 A sat / 19.5 A heat, 10.3 x 11.5 x 5.0 mm), CMLE105T-1R0MS-99 (1.0 uH, 36 / 25.5 A), Coilcraft XAL1060-222ME (2.2 uH, 4.95 mOhm max, 32 A sat / 20 A heat, 10.0 x 11.3 x 6.0 mm), Sumida 104CDMCCDS-2R2MC (p15).
- Capacitors: 0.1 uF at the VIN pin, more than 1.0 uF at VCC (figure uses 2.2 uF), 10 uF input for under 100 mV input ripple, three 22 uF ceramic output "for most applications", DC-bias derating warning (p13, p15); BST 0.1 uF between BST and SW (p4). Output ripple: Vripple_dis = (VOUT minus VIN_MIN) x IOUT / (VOUT x fSW x COUT), Vripple_ESR = ILpeak x RC_ESR (p16, eq 5 and 6).
- Compensation: crossover at most the lower of fSW/10 and fRHPZ/5, fRHPZ = RO x (1 minus D) squared / (2 pi L) (p17, eq 10); RC = 2 pi x VOUT x CO x fC / ((1 minus D) x VREF x GEA x KCOMP) (eq 12), CC = RO x CO / (2 RC) (eq 13), CP = RESR x CO / RC, open if under 10 pF (eq 14) (p17).

### Rail A: 5.05 V module rail, 6.5 A worst-case bursts, VIN 3.0 V (all computed from the equations above)
- IDC = 5.05 x 6.5 / (3.0 x 0.90) = 12.2 A (12.9 A at eta 0.85).
- With L = 2.2 uH minus 30 percent = 1.54 uH and fSW = 440 kHz: IPP = 3.0 x (1 minus 3.0/5.05) / (1.54 uH x 440 kHz) = 1.8 A; ILpeak = 13.1 A (13.8 A at eta 0.85).
- Finding: ILpeak exceeds the 12 A minimum current limit (p6). The 6.5 A burst at 3.0 V is only covered by the 15 A typical limit, not the guaranteed one. With 4.7 uH (3.29 uH at minus 30 percent) IPP falls to 0.84 A and ILpeak to 12.6 A, still above 12 A. Guaranteed output at 3.0 V with 2.2 uH: (12 minus 0.9) x 3.0 x 0.9 / 5.05 = 5.9 A. At VIN = 3.3 V: IDC = 11.1 A, IPP = 1.7 A, ILpeak = 11.9 A, inside the 12 A minimum. So either the burst spec must accept the typical limit, or the burst must be limited (about 5.9 A guaranteed at 3.0 V), or the low-cell cut-off raised to 3.3 V for full burst capability.
- FB: R2 = 13.7 kOhm, R1 = 102 kOhm gives VOUT = 0.6 x (1 + 102/13.7) = 5.067 V (0.3 percent above 5.05 V, smaller than the plus or minus 2 percent VREF tolerance on p6); alternative 105 kOhm / 14.3 kOhm gives 5.006 V. R2 under 15 kOhm, so no 27 pF capacitor (p14).
- Output capacitance for 100 mV ripple: COUT_eff = (5.05 minus 3.0) x 6.5 / (5.05 x 440 kHz x 0.1 V) = 60 uF effective; six 22 uF 10 V 1210 ceramics with DC-bias derating (sheet's derating warning p15), more if the transient response wants it.
- Input: 10 uF plus 0.1 uF at the VIN pin (p15); VCC 2.2 uF (p13); BST 0.1 uF (p4).
- Compensation starting values: D = 0.406, RO = 5.05/6.5 = 0.78 Ohm, fRHPZ = 0.78 x 0.594 squared / (2 pi x 2.2 uH) = 19.8 kHz, fC = 4 kHz; RC = 2 pi x 5.05 x 60 uF x 4 kHz / (0.594 x 0.6 x 180 uS x 13.5) = 8.8 kOhm (use 8.87 kOhm), CC = 0.78 x 60 uF / (2 x 8.8 kOhm) = 2.7 nF, CP = RESR x 60 uF / 8.8 kOhm = 34 pF for 5 mOhm ESR (use 33 pF). Confirm with a bode measurement; the sheet asks for 45 degrees phase margin and 10 dB gain margin (p17).
- Inductor: Coilcraft XAL1010-222MED, 2.2 uH, DCR 2.55 typ / 2.80 max mOhm, SRF 22 MHz, Isat 34.0 A, Irms 24.5 A at 20 C rise / 32.0 A at 40 C rise (coilcraft-xal1010.pdf, Document 804-1, p1), height 10.0 mm max (p4). LCSC C5125746, stock 263. The TI-listed XAL1060-222ME (2.2 uH, DCR 4.50 typ / 4.95 max mOhm, SRF 25 MHz, Isat 32 A, Irms 13.9 / 20.0 A, coilcraft-xal1060.pdf Document 812-1 p1; height 6.0 mm max, p3) is LCSC C7392419 with stock 0. Both saturate far above the 17.1 A maximum current limit (p6), as the sheet requires (p15). The Cyntec CMLE105T-2R2MS is C17584519, stock 0.
- Thermal: the input current is 12 A in bursts through a 2.5 x 3 mm package; the sheet's own remark prefers the TPS61288L for thermal improvement (p1). Use TPS61288LRQQR (also the better stocked orderable).

### Rail B: 5.1 V Pi rail, 5 A, VIN 3.0 V (computed)
- IDC = 5.1 x 5 / (3.0 x 0.90) = 9.4 A (10.0 A at eta 0.85); IPP = 3.0 x (1 minus 3.0/5.1) / (1.54 uH x 440 kHz) = 1.8 A; ILpeak = 10.4 A (10.9 A at eta 0.85), inside the 12 A minimum limit (p6). Guaranteed at 3.0 V.
- FB: R1 = 75.0 kOhm, R2 = 10.0 kOhm gives exactly 0.6 x 8.5 = 5.100 V; R2 under 15 kOhm, no 27 pF.
- COUT_eff = (5.1 minus 3.0) x 5 / (5.1 x 440 kHz x 0.1 V) = 47 uF effective: four to six 22 uF 10 V 1210.
- Compensation: D = 0.412, RO = 1.02 Ohm, fRHPZ = 25.5 kHz, fC = 5 kHz; RC = 8.8 kOhm, CC = 1.02 x 47 uF / (2 x 8.8 kOhm) = 2.7 nF, CP = 27 pF at 5 mOhm ESR.
- Same inductor (XAL1010-222MED) and same input/VCC/BST capacitors.
- Is a different part better for the Pi rail? By its sheet the TPS61288 covers 5.1 V at 5 A from 3.0 V with margin to the guaranteed limit; a second TPS61288L keeps one footprint, one inductor and one compensation recipe on the board. No other converter sheet was fetched, so no alternative is claimed.

### Recommendation, item 3
Two TPS61288LRQQR stages with XAL1010-222MED inductors: rail A 102 k / 13.7 k (5.067 V), rail B 75.0 k / 10.0 k (5.100 V), 6 x 22 uF and 4 to 6 x 22 uF outputs, 10 uF + 0.1 uF inputs, 2.2 uF VCC, 0.1 uF BST, RC 8.87 k / CC 2.7 nF / CP 33 pF starting values. Design decision for the owner: the 6.5 A burst on rail A at 3.0 V input is above the guaranteed current limit (12 A min, p6); it fits the typical limit only.

## 4. High-side switch for the 12 V heating pad, up to 2 A from SHORE_12V, GPIO controlled

### TPS2595 (tps2595.pdf, SLVSE57C)
- 2.7 V to 18 V, 4 A, 34 mOhm eFuse, WSON-8 2.00 x 2.00 mm (p1); input range 2.7 to 18 V (p5). Variants (p3): TPS259520/21 clamp the output at 3.8 V, TPS259530/31/33 at 5.7 V (unusable on 12 V), TPS259570 (no OV clamp, latch-off, active-high EN) and TPS259571 (no OV clamp, auto-retry, active-high EN). EN/UVLO absolute maximum 7 V (p5), so a 3.3 V GPIO drives it; UVLO rising threshold 1.2 V (p28).
- Current limit: RILM between 487 Ohm (4.42 A maximum) and 5000 Ohm (p1, p5); RILM = 2000 / (ILIMIT minus 0.04) with ILIMIT in A and RILM in Ohm (p28, eq 6; the sheet's example 3.7 A gives 546 Ohm). EC points: 487 Ohm gives 3.87 / 4.17 / 4.42 A, 1780 Ohm gives 1.09 / 1.17 / 1.24 A, 4420 Ohm gives 0.46 / 0.49 / 0.52 A (p7).
- For 2 A: RILM = 2000 / 1.96 = 1020 Ohm, E96 1.02 kOhm, limit about 2.0 A (computed). For a 2 A load with headroom, RILM = 806 Ohm gives 2000/806 + 0.04 = 2.52 A (computed). Inrush is set by CdVdt, IINRUSH = COUT x VIN / TdVdT (p28, eq 8). Dissipation at 2 A: 4 x 34 mOhm = 0.14 W (computed).
- LCSC: TPS259571DSGR C471038 stock 3234 (auto-retry); TPS259570DSGR C1849463 stock 5197 (latch-off).

### TPS2596 (tps2596.pdf, SLVSET8A)
- 2.7 to 19 V, 0.125 to 2 A, 89 mOhm eFuse with current monitor, SOIC-8 (DDA, PowerPAD) 4.91 x 3.9 mm (p1). RILM 453 to 7869 Ohm (p5); RILM = 903 / (ILIM minus 0.0112) (p28, eq 7); 453 Ohm gives 1.83 / 2.004 / 2.147 A (p6). A 2 A heater sits at the very top of its range.
- LCSC: TPS259631DDAR C2155778 stock 4862; TPS259621DDAR C2155774 stock 683.

### Recommendation, item 4
TPS259571DSGR (auto-retry) or TPS259570DSGR (latch-off), RILM = 806 Ohm (about 2.5 A) or 1.02 kOhm (about 2.0 A), EN from a Pi GPIO, WSON-8 2 x 2 mm. No discrete P-FET plus driver needed.

## 5. LT8705A tracker stage outline (lt8705a.pdf, 8705af) with the 12 mm height constraint

### Sheet facts
- 80 V VIN and VOUT synchronous 4-switch buck-boost controller; VIN 2.8 V (needs EXTVCC above 6.4 V) to 80 V, VOUT 1.3 to 80 V; quad N-channel gate drivers; synchronizable fixed frequency 100 to 400 kHz; input current, input voltage, output current and output voltage feedback loops; MODE pin for Burst Mode, discontinuous or forced continuous (p1). Improved pin-compatible version of the LT8705, recommended for new designs (p1). Packages: 38-lead 5 x 7 mm QFN (UHF) and 38-lead TSSOP (FE) (p2); orderables LT8705AEFE, LT8705AIFE, LT8705AHFE, LT8705AEUHF, LT8705AIUHF (p3).
- Regulation voltages: FBOUT 1.207 V (1.193 to 1.222), FBIN 1.205 V (1.184 to 1.226), FBIN error amp gm 130 umho, FBIN bias 10 nA (p4). FBIN absolute maximum 30 V (p2).
- Input voltage regulation: "By connecting a resistor divider between VIN, FBIN and GND, the FBIN pin provides a means to regulate the input voltage ... if VIN is provided by a relatively high impedance source (i.e., a solar panel) and the current draw pulls VIN below a preset limit, VC will be reduced, thus reducing current draw from the input supply"; VIN(MIN) = 1.205 V x (1 + RFBIN1/RFBIN2); do not use forced continuous mode with it, use discontinuous or Burst Mode (p29; same statement p18). This is a fixed input-voltage setpoint, not a searching MPPT.
- Output: VOUT = 1.207 V x (1 + RFBOUT1/RFBOUT2) (p29); RFBOUT1 = (VOUT/1.207 V minus 1) x RFBOUT2 (p38).
- Frequency: fOSC = 43,750 / (RT + 1) kHz with RT in kOhm; RT = 43,750 / fOSC minus 1 kOhm (p21); EC points RT 365 k = 120 kHz, 215 k = 202 kHz, 124 k = 350 kHz (p6).
- Current sense: maximum sense threshold VCSP minus VCSN 102 / 117 / 132 mV in boost mode at minimum M3 duty, VCSN minus VCSP 69 / 86 / 102 mV in buck mode at minimum M2 duty (LT8705AE/AI, p3). RSENSE procedure: choose RSENSE below both RSENSE(MAX,BOOST) and RSENSE(MAX,BUCK) with 30 percent or more margin, ripple 30 to 50 percent (p22, p23); worked example 12 V to 36 V at 2 A gives 12.4 mOhm (p23). Minimum inductance equations L(MIN1,BOOST), L(MIN2,BOOST) and the buck minimum, all scaling with RSENSE / (0.08 x f) (p24, p37); worked example 8 to 25 V in, 12 V 5 A out, 350 kHz, 8.7 mOhm (p37).
- MOSFET selection: RDS(on) from the allowed dissipation, worked example 1.3 W allows below 15.4 mOhm, Fairchild FDMS7672 (6.9 mOhm at 4.5 V) chosen for all four switches, switching loss estimate with 20 ns edges (p37, p38).
- Typical applications: front page 36 to 80 V in, 48 V 5 A out, 22 uH, 10 mOhm RSENSE, RT 215 k (202 kHz), FBOUT 392 k / 10 k (p1), parts L1 22 uH Wurth 74435572200 or Coilcraft SER2918H-223, M1/M3 FDMS86104, M2/M4 FDMS86101 (p39). Closest to 100 W at a low output voltage: "12V, 15A Output Converter Accepts 7.5V to 55V Input", 190 kHz, L1 Coilcraft SER2915H-682 6.8 uH, RSENSE Susumu KRL6432E-M-R003-F-T1 3 mOhm, M1 Infineon BSC028N06NS, M2 BSC039N06NS, M3/M4 BSC015NE2LS5I, CIN2 4.7 uF 100 V TDK C4532X7S2A475M, COUT1 10 uF 25 V TDK C4532X7R1E106M, COUT2 330 uF 25 V Panasonic 25SEPF330M (p41). Also "12V Output Converter Accepts 4V to 80V Input" (p44).
- DC1924A demo (lt8705-farnell.pdf): LT8705, 36 to 80 V in, 48 V 5 A, 200 kHz, 100 V MOSFETs, Wurth 74435572200 fitted, Coilcraft SER2918H-223 as the larger option, Vishay Si7892BDP suggested for lower voltages (p1), BOM p5 onward.

### Setpoints for this design (computed from the equations above)
- Panel MPP about 17 to 18 V: VIN(MIN) = 1.205 x (1 + RFBIN1/RFBIN2). RFBIN1 = 102 kOhm, RFBIN2 = 7.50 kOhm gives 17.6 V; 100 kOhm / 7.50 kOhm gives 17.3 V. At a 22 V open-circuit panel FBIN sits at 1.5 V, far below the 30 V limit (p2). Because the setpoint is fixed, make RFBIN2 selectable on test (or a trimmer) so the MPP voltage can be matched to the actual panel.
- VOUT 15 V: RFBOUT1 = 115 kOhm, RFBOUT2 = 10.0 kOhm gives 1.207 x 12.5 = 15.09 V.
- Frequency 200 kHz (the sheet's 100 W class examples run 190 to 202 kHz, p1 and p41): RT = 43,750/200 minus 1 = 218 kOhm, use 215 kOhm (202 kHz typ, p6).
- Currents: 100 W gives about 6.7 A output at 15 V and 5.7 A input at 17.5 V. The stage runs mostly in the buck region and enters boost when the panel sags below 15 V.
- RSENSE estimate from the buck-mode minimum threshold (69 mV, p3): with 40 percent ripple the peak inductor current is about 8.0 A, so RSENSE at most 69 mV / 8.0 A = 8.6 mOhm, with the sheet's 30 percent margin about 6 mOhm: use 5 mOhm (for example the same RALEC LR2512-23R005F4 as item 2, 3 W) or the 3 mOhm Susumu part of the p41 example. Run the sheet's full procedure (p22 to p24, which uses the sense-voltage vs duty-cycle graph) before freezing it.
- Inductor value: the sheet's p41 example uses 6.8 uH at 190 kHz for 12 V 15 A; for 15 V at 6.7 A a 6.8 to 10 uH part at 200 kHz gives about 1 A peak-to-peak ripple in the buck region ((17.5 minus 15) x 0.857 / (10 uH x 200 kHz), computed) and satisfies the minimum-inductance equations by a wide margin for a 5 mOhm sense resistor.

### Inductor candidates with heights (12 mm limit)
| Part | L | Isat | Irms / IR | DCR | Body | Height (sheet) | LCSC |
|---|---|---|---|---|---|---|---|
| Coilcraft XAL1510-103MED | 10 uH | 26.3 A | 16 A at 20 C rise, 22 A at 40 C rise | 6.80 typ / 9.00 max mOhm | 15.2 x 16.2 mm | 10.0 mm max (coilcraft-xal1510.pdf p3; ratings p1) | C3911782, stock 182 |
| Coilcraft XAL1510-682MED | 6.8 uH | 36.0 A | 19 / 26 A | 4.17 / 4.60 mOhm | 15.2 x 16.2 mm | 10.0 mm max (p3; ratings p1) | C3911560, stock 237 |
| Wurth 74439370100 (WE-XHMI 1510) | 10 uH | 12.9 A at 10 percent drop, 31.2 A at 30 percent | IR 11.5 A at delta T 40 K, IRP 19.6 A | 6.4 typ / 7.04 max mOhm | 15.4 x 16.4 mm | 10.0 mm max (wurth-74439370100.pdf p1) | C2042106, stock 0 |
| Wurth 74439370068 (WE-XHMI 1510) | 6.8 uH | 17.8 A / 40.05 A | IR 15 A, IRP 25.3 A | 4.1 / 4.51 mOhm | 15.4 x 16.4 mm | 10.0 mm max (p1) | C5914153, stock 0 |
| Coilcraft SER2915H-682 (sheet's p41 part) | 6.8 uH | 30.0 / 34.5 / 36.2 A at 10/20/30 percent drop | 20 A at 20 C rise, 30 A at 40 C rise | 1.86 / 2.05 mOhm | 27.9 x 19.8 mm | 15.36 mm max (coilcraft-ser2900.pdf p2; ratings p1) | not searched; exceeds 12 mm |
| Coilcraft SER2918H-223 (front-page part) | 22 uH | 12.0 / 14.0 / 15.0 A | 20 / 28 A | 2.60 / 2.86 mOhm | 27.9 x 19.8 mm | 17.78 mm max (p2) | C17398237, stock 32; exceeds 12 mm |
| Wurth 74435572200 (front-page part, WE-HCI) | 22 uH | 9 A at 10 percent, 11 A at 30 percent | IR 11 A at delta T 50 K | 14.6 mOhm | 18.2 x 18.2 mm | vertical dimensions 9.1 plus or minus 1.0 mm and 8.9 plus or minus 0.3 mm on the drawing (wurth-74435572200.pdf p1), so at most 10.1 mm | C2651193, stock 165; Isat 9 A is marginal for 8 A peaks |

Choice: XAL1510-103MED (or -682MED), 10.0 mm tall, stocked, Isat and Irms well above the 8 A peaks.

### MOSFETs
- 60 V class from the sheet's p41 example, all Infineon TDSON-8 5 x 6 mm (low-profile power QFN; the sheet gives no height, the package is about a millimetre class): BSC028N06NS (M1) C148250 stock 19665; BSC039N06NS (M2) C534330 stock 676; BSC015NE2LS5I (M3, M4) C3278724 stock 272. The 100 V onsemi pair of the front page (FDMS86104 C891087 stock 4, FDMS86101 C102622 stock 3020) is over-specified for a 22 V panel. The 30 V FDMS7672 of the worked example (C463468, stock 43) leaves too little margin above a 22 V open-circuit panel. Size the RDS(on) with the sheet's dissipation procedure (p37, p38).

### Capacitors with heights (12 mm limit)
| Part | Rating | Ripple / ESR | Size (dia x L) | LCSC |
|---|---|---|---|---|
| Panasonic EEHZK1V101XP (ZK hybrid) | 35 V, 100 uF | 1700 mA at 100 kHz / 125 C, ESR 35 mOhm | 6.3 x 7.7 mm (lcsc-panasonic-eehzk1v101xp.pdf p2 ratings row; size table p1) | C454360, stock 4906 |
| Panasonic 35SVPF39M (OS-CON SVPF) | 35 V, 39 uF | 2800 mA at 100 kHz / 105 C, ESR 30 mOhm | 8.0 x 6.9 mm, size code E7 (lcsc-panasonic-35svpf39m.pdf p2 row; size table p1) | C189474, stock 552 |
| Panasonic 25SEPF330M (sheet's p41 COUT2) | 25 V, 330 uF | not fetched | not fetched | not searched |
| TDK C4532X7R1E106M (sheet's p41 COUT1) | 25 V, 10 uF, 1812 ceramic | n/a | height not fetched | not searched |

Choice: input bulk on the panel side at 35 V rating (a 36-cell panel open-circuit voltage is above the 25 V of the sheet's example parts): two to three EEHZK1V101XP (7.7 mm tall) plus 100 V-rated ceramics as in the sheet's example; output at 15 V: EEHZK1V101XP or 35SVPF39M (6.9 mm) plus 25 V ceramics. Every candidate above is under 8 mm.

### Height constraint summary (item 5, dock strip)
Inductor XAL1510-103MED 10.0 mm max; Wurth WE-XHMI 1510 10.0 mm max; the sheet's SER2915H (15.36 mm) and SER2918H (17.78 mm) are excluded; capacitors 7.7 mm and 6.9 mm; MOSFETs and the TSSOP-38 controller are low-profile packages. Nothing recommended for the tracker stage exceeds 10 mm.

### Controller availability
LT8705AIFE#PBF C674167 stock 1, LT8705AHFE#PBF C674165 stock 5, LT8705AEUHF not listed; the older LT8705EFE#PBF C108002 stock 116 (the LT8705A sheet describes the A as the pin-compatible improved version, p1). Stock on the A version is thin; this is an owner decision item.

### Recommendation, item 5
Outline only: LT8705A (TSSOP-38), 200 kHz (RT 215 k), FBIN 102 k / 7.50 k (17.6 V setpoint, selectable on test), FBOUT 115 k / 10.0 k (15.1 V), RSENSE about 5 mOhm after the sheet's procedure, XAL1510-103MED, BSC028N06NS / BSC039N06NS / BSC015NE2LS5I, EEHZK1V101XP bulk capacitors; MODE in discontinuous or Burst Mode as the sheet requires for input-voltage regulation (p29).

## 6. Main power control: latching push-button that enables the two boosts, with a Pi-side power-loss line

### LTC2954 (ltc2954.pdf, 2954fb)
- Pushbutton on/off controller with microprocessor interrupt; 2.7 V to 26.4 V; 6 uA; EN output (LTC2954-1: open-drain EN, active high, "low leakage EN output allows DC/DC converter control"; LTC2954-2: EN-bar for circuit breaker control); INT open-drain; KILL input with an accurate 0.6 V threshold; 8-pin 3 x 2 mm DFN and ThinSOT (TSOT-23-8) (p1). Supply range in the EC table 2.7 to 26.4 V (p3).
- Timing: turn-on debounce tDB,ON 32 ms (26 to 41 ms), plus 6.4 s/uF on the ONT pin (p3, p6); turn-off interrupt debounce 32 ms (p3); forced power-down after tPD,MIN 64 ms plus 6.4 s/uF on the PDT pin (p3, p6); KILL turn-on blanking 512 ms (p3, p6).
- Behaviour (pin functions, p6): PB to ground through a momentary switch; internal 100 k pull-up, withstands 10 kV HBM, can be pulled to 26.4 V. EN asserts after a valid turn-on and releases if KILL is not driven high within 512 ms of turn-on, if KILL is driven low during operation, or if PB is held for tPD,MIN + tPDT. INT asserts low after a turn-off press so the processor can do housekeeping and then pull KILL low. The EN pin can connect directly to a converter shutdown pin that has an internal pull-up, otherwise an external pull-up is required (p6); "if unused, connect KILL to a low voltage output supply" (p6).
- LCSC: LTC2954CTS8-1#TRPBF C683782 stock 2476 (TSOT-23-8); LTC2954ITS8-2#TRPBF C580656 stock 822.

### TPS3421 (tps3421.pdf, SBVS211B)
- TPS3420/3421/3422 pushbutton reset timers in a 1.45 x 1.00 mm USON-6 (p1); TPS3421EG: 0 s delay, 7.5 s hold, 400 ms reset pulse (p11). It produces a reset pulse after a long press; it is not a latching on/off power controller. LCSC TPS3421EGDRYR C2067262 stock 2561. Not the fit for this function.

### Documented arrangement for the kit (from the LTC2954 and TPS61288 sheets)
- LTC2954-1 on the cell node (3.0 to 4.2 V, inside 2.7 to 26.4 V, ltc2954 p3). PB to the panel push button.
- EN (open drain, ltc2954 p6) pulled up to the cell node and wired to both TPS61288 EN pins: TPS61288 EN needs above 1.2 V for high and has an 850 to 1100 kOhm internal pull-down (tps61288 p6), absolute maximum 6 V (p5), so the cell node is a valid pull-up source and the pull-down needs an external pull-up (the sheet's "otherwise a pull-up resistor to an external supply is required", ltc2954 p6).
- KILL pulled up from the 5.1 V Pi rail through a resistor: the rail rises as soon as EN asserts, satisfying the 512 ms blanking rule (ltc2954 p6), and a Pi GPIO through an open-drain transistor pulls KILL low after the OS has halted, which releases EN and switches both boosts off.
- INT to a Pi GPIO with a 3.3 V pull-up: this is the power-loss / shutdown-request line (asserted low for at least 32 ms on a press, p6).
- A long press (64 ms plus 6.4 s/uF on PDT; 1 uF gives about 6.5 s, computed from p6) forces power off without the Pi.

### Recommendation, item 6
LTC2954CTS8-1#TRPBF with EN to both TPS61288 EN pins, KILL from the Pi rail with a GPIO pull-down, INT to a Pi GPIO.

## 7. Recommended parts

| Part | Function | LCSC number (stock 4 Sep 2026) | Document file |
|---|---|---|---|
| BQ25798RQMR (alternate BQ25792RQMR) | 1S charger from SHORE_12V, 3 A, JEITA TS, I2C 0x6B | C2876593 (223); alternate C2862876 (5471) | bq25798.pdf; bq25792.pdf |
| Semitec 103AT-2 | pack thermistor the charger's thresholds are defined for | C5346323 (0, through-hole, bench fit) | bq25798.pdf p5 (thermistor sheet not fetched) |
| BQ34Z100PWR-G1 | fuel gauge, 42 Ah with SCALED configuration, low-side shunt | C91302 (6777) | bq34z100-g1.pdf |
| RALEC LR2512-23R005F4 | 5 mOhm 3 W 2512 shunt for the gauge (and a candidate LT8705A sense resistor) | C154688 (15492) | lcsc-ralec-lr2512-23r005f4.pdf |
| MAX17048G+T10 | fallback voltage-based gauge, no shunt | C2682616 (15439) | max17048.pdf |
| TPS61288LRQQR, two | 5.05 V module rail and 5.1 V Pi rail boosts | C7498841 (7139); non-L C5219223 (2029) | tps61288.pdf |
| Coilcraft XAL1010-222MED, two | 2.2 uH boost inductors, Isat 34 A, 10.0 mm tall | C5125746 (263); alternate XAL1060-222MEC C7392419 (0), 6.0 mm | coilcraft-xal1010.pdf; coilcraft-xal1060.pdf |
| TPS259571DSGR (or TPS259570DSGR) | 12 V heater eFuse, RILM 806 Ohm (2.5 A) or 1.02 kOhm (2.0 A) | C471038 (3234); C1849463 (5197) | tps2595.pdf |
| LT8705AIFE#PBF | tracker stage controller (outline) | C674167 (1); LT8705AHFE C674165 (5); older LT8705EFE C108002 (116) | lt8705a.pdf |
| Coilcraft XAL1510-103MED (or -682MED) | tracker inductor, 10.0 mm tall | C3911782 (182); C3911560 (237) | coilcraft-xal1510.pdf |
| Infineon BSC028N06NS, BSC039N06NS, BSC015NE2LS5I | tracker MOSFETs M1, M2, M3/M4 (sheet's 12 V 15 A example) | C148250 (19665); C534330 (676); C3278724 (272) | lt8705a.pdf p41 |
| Panasonic EEHZK1V101XP | 35 V 100 uF hybrid bulk capacitor, 7.7 mm tall | C454360 (4906) | lcsc-panasonic-eehzk1v101xp.pdf |
| Panasonic 35SVPF39M | 35 V 39 uF OS-CON, 6.9 mm tall | C189474 (552) | lcsc-panasonic-35svpf39m.pdf |
| LTC2954CTS8-1#TRPBF | push-button on/off controller, EN to the boosts, INT to the Pi, KILL from the Pi | C683782 (2476) | ltc2954.pdf |

Open decisions for the owner: (a) accept the typical rather than guaranteed TPS61288 current limit for the 6.5 A burst at 3.0 V, or limit the burst / raise the low-cell cut-off; (b) BQ25798 versus BQ25792 (MPPT and backup mode against stock); (c) LT8705A stock (single digits at LCSC today) versus the older LT8705.
