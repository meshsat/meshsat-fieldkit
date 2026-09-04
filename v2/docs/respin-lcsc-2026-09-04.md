# LCSC / JLCPCB part numbers for the 177 uncoded BOM lines

Source list: `lcsc-needed.txt` (177 lines, seven boards A19, B12, C4, D5, E4).

Method. Every code below was looked up on the JLCPCB assembly parts catalogue through
`https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`,
which is the data behind `https://jlcpcb.com/partdetail/<code>` and carries the
manufacturer part number, the package, the library type (base = Basic, expand = Extended,
`preferredComponentFlag` = Preferred) and the live stock count. Each chosen code was then
re-queried by its exact code as a second pass, and every one came back with the same
manufacturer part, package and library type recorded here. The same direct code lookup was
run on every alternative and substitute named in this document, so no code appears here that
was not read back from its own catalogue record. Stock figures are those seen on
4 September 2026 and move constantly. No login was used, nothing was added to a cart.

One code is quoted with zero stock and is quoted only to record that it exists: C620505
(UNI-ROYAL 0603WAF3032T5E, 30.3k) in section 3.1. Every code recommended for use had stock
when it was read.

Preference order applied: Basic first, then Preferred (neither carries the per line feeder
fee), then Extended.

Totals: **70 lines resolved with an exact match**, **2 lines resolved only with a
substitute of a different value** (section 3), **105 lines skipped as not JLC assembled**
(section 2).

---

## 1. Resolved lines

Package column is the package string JLCPCB itself reports for the code.
Source URL is `https://jlcpcb.com/partdetail/<code>`; the LCSC mirror of the same code is
`https://www.lcsc.com/product-detail/<code>.html`.

### Resistors, 0603, 1 percent

| value | footprint | LCSC code | manufacturer part | package | Basic or Extended | stock seen | source URL |
|---|---|---|---|---|---|---|---|
| 1.02k 1% (2.0 A) | R_0603 | C2998111 | FOJAN FRC0603F1021TS | 0603 | Extended | 22,788 | https://jlcpcb.com/partdetail/C2998111 |
| 10.0k 1% (RFBOUT2) | R_0603 | C25804 | UNI-ROYAL 0603WAF1002T5E | 0603 | Basic | 27,960,868 | https://jlcpcb.com/partdetail/C25804 |
| 10k 1% | R_0603 | C25804 | UNI-ROYAL 0603WAF1002T5E | 0603 | Basic | 27,960,868 | https://jlcpcb.com/partdetail/C25804 |
| 100k 1% (ILIM) | R_0603 | C25803 | UNI-ROYAL 0603WAF1003T5E | 0603 | Basic | 25,342,138 | https://jlcpcb.com/partdetail/C25803 |
| 102k 1% (both lines) | R_0603 | C2933126 | FOJAN FRC0603F1023TS | 0603 | Extended | 232,672 | https://jlcpcb.com/partdetail/C2933126 |
| 105k 1% | R_0603 | C16840 | UNI-ROYAL 0603WAF1053T5E | 0603 | Extended | 122,457 | https://jlcpcb.com/partdetail/C16840 |
| 115k 1% (RFBOUT1) | R_0603 | C22783 | UNI-ROYAL 0603WAF1153T5E | 0603 | Extended | 109,490 | https://jlcpcb.com/partdetail/C22783 |
| 12.0k 1% (RBIAS) | R_0603 | C22790 | UNI-ROYAL 0603WAF1202T5E | 0603 | Basic | 1,606,099 | https://jlcpcb.com/partdetail/C22790 |
| 13.7k 1% | R_0603 | C22793 | UNI-ROYAL 0603WAF1372T5E | 0603 | Extended | 83,330 | https://jlcpcb.com/partdetail/C22793 |
| 15.0k 1% (SHDN) | R_0603 | C22809 | UNI-ROYAL 0603WAF1502T5E | 0603 | Basic | 5,381,841 | https://jlcpcb.com/partdetail/C22809 |
| 16.5k 1% | R_0603 | C22812 | UNI-ROYAL 0603WAF1652T5E | 0603 | Extended | 116,820 | https://jlcpcb.com/partdetail/C22812 |
| 17.4k | R_0603 | C2930069 | FOJAN FRC0603F1742TS | 0603 | Extended | 350,592 | https://jlcpcb.com/partdetail/C2930069 |
| 2.7k 1% (REXT) | R_0603 | C13167 | UNI-ROYAL 0603WAF2701T5E | 0603 | Basic | 1,510,882 | https://jlcpcb.com/partdetail/C13167 |
| 20k 1% | R_0603 | C4184 | UNI-ROYAL 0603WAF2002T5E | 0603 | Basic | 7,920,837 | https://jlcpcb.com/partdetail/C4184 |
| 215k 1% (RT 202 kHz) | R_0603 | C5713280 | FOJAN FRC0603F2153TS | 0603 | Extended | 30,090 | https://jlcpcb.com/partdetail/C5713280 |
| 301k 1% (500 kHz) | R_0603 | C2933194 | FOJAN FRC0603F3013TS | 0603 | Extended | 101,483 | https://jlcpcb.com/partdetail/C2933194 |
| 33.2k 1% | R_0603 | C23003 | UNI-ROYAL 0603WAF3322T5E | 0603 | Extended | 136,555 | https://jlcpcb.com/partdetail/C23003 |
| 34.8k 1% | R_0603 | C2933204 | FOJAN FRC0603F3482TS | 0603 | Extended | 57,921 | https://jlcpcb.com/partdetail/C2933204 |
| 4.7k 1% (PROG) | R_0603 | C23162 | UNI-ROYAL 0603WAF4701T5E | 0603 | Basic | 28,323,487 | https://jlcpcb.com/partdetail/C23162 |
| 7.50k 1% (RFBIN2) | R_0603 | C23234 | UNI-ROYAL 0603WAF7501T5E | 0603 | Basic | 1,777,007 | https://jlcpcb.com/partdetail/C23234 |
| 75k 1% | R_0603 | C23242 | UNI-ROYAL 0603WAF7502T5E | 0603 | Basic | 756,139 | https://jlcpcb.com/partdetail/C23242 |
| 8.87k | R_0603 | C2998144 | FOJAN FRC0603F8871TS | 0603 | Extended | 166,224 | https://jlcpcb.com/partdetail/C2998144 |

All twenty-two are thick film, 100 mW, 75 V, plus or minus 1 percent, 100 ppm per degree C,
which matches the 1 percent the BOM lines ask for. The two FOJAN and UNI-ROYAL houses are
interchangeable at these values; where both existed the higher stocked was taken.

### Thermistor

| value | footprint | LCSC code | manufacturer part | package | Basic or Extended | stock seen | source URL |
|---|---|---|---|---|---|---|---|
| 103AT-2 10k NTC (gauge temperature) | R_0603 | C13564 | Murata NCP18XH103F03RB | 0603 | Extended | 395,089 | https://jlcpcb.com/partdetail/C13564 |

This is the board mounted gauge thermistor, so it is a real SMD placement, not the leaded
bead on the E4 lead. It is 10 k, plus or minus 1 percent, in 0603. See section 3 for the
beta constant note.

### Resistors, other packages

| value | footprint | LCSC code | manufacturer part | package | Basic or Extended | stock seen | source URL |
|---|---|---|---|---|---|---|---|
| 0.05R 1% 1206 | R_1206 | C601088 | Milliohm HoYH1206-1W-50mR-1% | 1206 | Extended | 22,094 | https://jlcpcb.com/partdetail/C601088 |
| 0.1R 1% 1206 | R_1206 | C2903496 | Milliohm HoJLR1206-1W-100mR-1% | 1206 | Extended | 69,410 | https://jlcpcb.com/partdetail/C2903496 |
| 10R 2W 2512 | R_2512 | C414890 | UNI-ROYAL HP122WF100JT4E | 2512 | Extended | 4,513 | https://jlcpcb.com/partdetail/C414890 |

Both shunts are 1 W current sense alloy parts at plus or minus 1 percent. If the temperature
coefficient matters at the gauge, `C601102` (HoLR1206-1W-50mR-1%-75ppm, Extended, 20,598
seen) is the 75 ppm version of the 0.05R. The 2512 is 2 W, plus or minus 1 percent, 75 ppm,
300 V; `C840605` (BOURNS CRM2512-FX-10R0ELF, Extended, 6,865 seen) is the equivalent if the
UNI-ROYAL stock of 4,513 looks thin at build time.

### Capacitors

| value | footprint | LCSC code | manufacturer part | package | Basic or Extended | stock seen | source URL |
|---|---|---|---|---|---|---|---|
| 100p | C_0603 | C14858 | Samsung CL10C101JB8NNNC | 0603 | Basic | 4,346,278 | https://jlcpcb.com/partdetail/C14858 |
| 1n | C_0603 | C1588 | Samsung CL10B102KB8NNNC | 0603 | Basic | 10,362,079 | https://jlcpcb.com/partdetail/C1588 |
| 3.3n | C_0603 | C1613 | Samsung CL10B332KB8NNNC | 0603 | Basic | 366,159 | https://jlcpcb.com/partdetail/C1613 |
| 10n | C_0603 | C57112 | Fenghua 0603B103K500NT | 0603 | Basic | 9,281,445 | https://jlcpcb.com/partdetail/C57112 |
| 27p | C_0603 | C107045 | YAGEO CC0603JRNPO9BN270 | 0603 | Preferred | 1,014,256 | https://jlcpcb.com/partdetail/C107045 |
| 47n | C_0603 | C1622 | Samsung CL10B473KB8NNNC | 0603 | Basic | 1,128,744 | https://jlcpcb.com/partdetail/C1622 |
| 470n 25V | C_0603 | C1623 | Samsung CL10B474KA8NNNC | 0603 | Basic | 3,726,933 | https://jlcpcb.com/partdetail/C1623 |
| 2.2u | C_0603 | C57895 | Samsung CL10A225KA8NNNC | 0603 | Extended | 867,699 | https://jlcpcb.com/partdetail/C57895 |
| 4.7u | C_0805 | C1779 | Samsung CL21A475KAQNNNE | 0805 | Basic | 2,988,300 | https://jlcpcb.com/partdetail/C1779 |
| 4.7u 25V | C_1206 | C132170 | YAGEO CC1206KKX7R9BB475 | 1206 | Extended | 245,314 | https://jlcpcb.com/partdetail/C132170 |
| 4.7u 50V | C_1206 | C132170 | YAGEO CC1206KKX7R9BB475 | 1206 | Extended | 245,314 | https://jlcpcb.com/partdetail/C132170 |
| 10u 25V | C_1206 | C89632 | Samsung CL31B106KBHNNNE | 1206 | Extended | 390,230 | https://jlcpcb.com/partdetail/C89632 |
| 10u 50V | C_1206 | C89632 | Samsung CL31B106KBHNNNE | 1206 | Extended | 390,230 | https://jlcpcb.com/partdetail/C89632 |
| 22u 25V | C_1206 | C12891 | Samsung CL31A226KAHNNNE | 1206 | Basic | 1,507,845 | https://jlcpcb.com/partdetail/C12891 |
| 100u 10V | C_1206 | C6119961 | HRE CGA1206X5R107M100NT | 1206 | Extended | 31,458 | https://jlcpcb.com/partdetail/C6119961 |
| 10u 25V 1210 | C_1210 | C2918497 | Samwha CS3225X7R106K250NRK | 1210 | Extended | 47,097 | https://jlcpcb.com/partdetail/C2918497 |
| 22u 10V X7R 1210 | C_1210 | C2918511 | Samwha CS3225X7R226K250NRL | 1210 | Extended | 134,245 | https://jlcpcb.com/partdetail/C2918511 |
| 22u 25V X7R 1210 | C_1210 | C2918511 | Samwha CS3225X7R226K250NRL | 1210 | Extended | 134,245 | https://jlcpcb.com/partdetail/C2918511 |

Dielectrics as seen on the pages: C14858 and C107045 are C0G/NP0 50 V; C1588, C1613, C57112,
C1622, C1623, C132170, C89632, C2918497 and C2918511 are X7R; C57895, C1779, C12891 and
C6119961 are X5R. All meet or beat the voltage the line asks for.

Three deliberate merges, each of which removes one feeder line from the order:

- `4.7u 25V` and `4.7u 50V` in 1206 both take C132170, a 50 V X7R part. The 25 V line is
  covered by a 50 V part with margin to spare, and the 25 V only candidates were thin
  (C380365 at 8,543, C277508 at 1,929).
- `10u 25V` and `10u 50V` in 1206 both take C89632, a 50 V X7R Samsung part with 390,230 in
  stock, better than any 25 V only candidate.
- `22u 10V X7R 1210` and `22u 25V X7R 1210` both take C2918511, a 25 V X7R part with 134,245
  in stock. The genuine 10 V X7R 1210 parts are all thin (Murata C913632 at 3,971, KEMET
  C561843 at 253) and a 25 V part in the same case size has better DC bias behaviour at 10 V
  than a 10 V part does. If a true 10 V part is wanted anyway, C913632
  (Murata GCM32ER71A226KE12L, Extended, 3,971 seen) is the one to use.

Notes on two lines that state no voltage:

- `4.7u` in 0805: C1779 is the Basic part and is 25 V X5R. The brief asked for 50 V where the
  package allows, and a 50 V 0805 4.7 uF does exist (C20416422, CCTC TCC0805X7R475K500FT,
  Extended, 87,746 seen). C1779 is named as the pick because it is Basic and has 2.99 M in
  stock; swap to C20416422 if this sits on anything above the 5 V rails.
- `2.2u` in 0603: no 50 V part exists in that case size. C57895 is 25 V X5R. A 25 V X7R
  alternative is C99228 (Fenghua 0603B225K250NT, Extended, 598,237 seen).

One line where Basic is not usable: `100u 10V` in 1206. The Basic 1206 100 uF part is C15008
(Samsung CL31A107MQHNNNE) but it is rated 6.3 V, below the 10 V the line states, so the
Extended C6119961 is the pick.

### Resettable fuses, 1812

| value | footprint | LCSC code | manufacturer part | package | Basic or Extended | stock seen | source URL |
|---|---|---|---|---|---|---|---|
| 0.5A hold 1812 | Fuse_1812 | C17313 | BOURNS MF-MSMF050-2 | 1812 | Extended | 148,708 | https://jlcpcb.com/partdetail/C17313 |
| 2A hold 1812 | Fuse_1812 | C210837 | BOURNS MF-MSMF200-2 | 1812 | Extended | 17,441 | https://jlcpcb.com/partdetail/C210837 |
| 2.5A hold 1812 | Fuse_1812 | C210838 | BOURNS MF-MSMF250/16X-2 | 1812 | Extended | 17,017 | https://jlcpcb.com/partdetail/C210838 |

Hold and trip currents match the values asked for (0.5 A hold / 1 A trip, 2 A hold / 4 A trip,
2.5 A hold / 5 A trip). Working voltages differ and are worth a look: MF-MSMF050-2 is 15 V,
MF-MSMF200-2 is **8 V**, MF-MSMF250/16X-2 is 16 V. The 0.5 A and 2 A parts sit on B12, whose
rails are 5 V, so 8 V is adequate but has little headroom. If a higher rating is wanted,
C960026 (BHFUSE BSMD1812-200-30V, Extended, 57,052 seen, 30 V, 2 A hold / 4 A trip) is a
drop in for the 2 A line. The 2.5 A part is on A19 and its net is not given in the input
list; 16 V covers a 12 V rail but not shore DC up to 36 V, so confirm which net it guards.

### Crystals, 3225

| value | footprint | LCSC code | manufacturer part | package | Basic or Extended | stock seen | source URL |
|---|---|---|---|---|---|---|---|
| 12 MHz 3225 | Crystal_SMD_3225-4Pin | C9002 | YXC X322512MSB4SI | SMD3225-4P | Basic | 167,759 | https://jlcpcb.com/partdetail/C9002 |
| 24 MHz 3225 | Crystal_SMD_3225-4Pin | C70571 | YXC X322524MRB4SI | SMD3225-4P | Extended | 34,453 | https://jlcpcb.com/partdetail/C70571 |

C9002 is 20 pF load capacitance, plus or minus 10 ppm, 80 ohm ESR, minus 40 to plus 85 C.
C70571 is 18 pF load capacitance, plus or minus 10 ppm, 50 ohm ESR, same temperature range.
The 18 pF part was chosen for the 24 MHz line because A19 carries the only `27p` line in the
input list, and a pair of 27 pF loading caps gives a circuit load of roughly 16.5 pF once a
few pF of stray is allowed, which suits an 18 pF crystal rather than the 12 pF or 20 pF
alternatives. See section 3 for the matching question on the 12 MHz part.

### Discrete semiconductors

| value | footprint | LCSC code | manufacturer part | package | Basic or Extended | stock seen | source URL |
|---|---|---|---|---|---|---|---|
| 2N7002 (three lines) | SOT-23 | C8545 | Jiangsu Changjing 2N7002 | SOT-23 | Basic | 2,264,195 | https://jlcpcb.com/partdetail/C8545 |
| BC847 (two lines) | SOT-23 | C20069135 | hongjiacheng BC847B | SOT-23 | Preferred | 21,073 | https://jlcpcb.com/partdetail/C20069135 |
| BC857 | SOT-23 | C556165 | Slkor BC857B | SOT-23 | Extended | 98,937 | https://jlcpcb.com/partdetail/C556165 |
| BAT54 (two lines) | D_SOD-123 | C7502705 | BAT54W | SOD-123 | Preferred | 164,024 | https://jlcpcb.com/partdetail/C7502705 |
| SMBJ5.0A | D_SMB | C113974 | MDD SMBJ5.0A | DO-214AA (SMB) | Extended | 157,139 | https://jlcpcb.com/partdetail/C113974 |
| SMCJ33A (two lines) | D_SMC | C42371548 | hongjiacheng SMCJ33A | SMC (DO-214AB) | Preferred | 55,259 | https://jlcpcb.com/partdetail/C42371548 |
| SMBJ15A (see note) | D_SMC | C42371550 | hongjiacheng SMCJ15A | SMC (DO-214AB) | Preferred | 5,964 | https://jlcpcb.com/partdetail/C42371550 |

C8545 is 60 V, 115 mA, N channel, the standard 2N7002. C20069135 is the B gain grade of the
BC847, 45 V, 100 mA, NPN; if 21,073 in stock is uncomfortable, C181140 (Guangdong Hottech
BC847B, Extended, 563,983 seen) is the volume alternative, at the cost of one feeder fee.
C556165 is the B grade BC857, 45 V, 100 mA, PNP, with no Basic or Preferred equivalent found.

The BAT54 pick was verified twice because the suffix is misleading. The LCSC product page
for C7502705 (https://www.lcsc.com/product-detail/C7502705.html) reports it as a single
Schottky diode, 30 V, 200 mA, 800 mV at 100 mA, in **SOD-123**, with 163,150 in stock, even
though "BAT54W" usually names a SOD-323 part in Western catalogues. The SOD-123 package on
both the JLCPCB and LCSC records matches the `D_SOD-123` footprint. It is a single diode,
not a dual, which is what the two `INTVCC -> BOOST` lines need.

C42371548 and C42371550 are 1.5 kW TVS diodes in DO-214AB, matching the `D_SMC` land. The
SMBJ15A line is a package mismatch and is dealt with in section 3.

### Integrated circuits and the optocoupler

| value | footprint | LCSC code | manufacturer part | package | Basic or Extended | stock seen | source URL |
|---|---|---|---|---|---|---|---|
| AP2112K-3.3 (two lines) | SOT-23-5 | C51118 | Diodes AP2112K-3.3TRG1 | SOT-25-5 | Extended | 64,839 | https://jlcpcb.com/partdetail/C51118 |
| TPS2065CDBV (see note) | SOT-23-6 | C353882 | TI TPS2065CDBVR | SOT-23-5 | Extended | 7,204 | https://jlcpcb.com/partdetail/C353882 |
| TPS22810DRV | WSON-6-1EP_2x2mm | C527679 | TI TPS22810DRVR | WSON-6-EP (2x2) | Extended | 9,875 | https://jlcpcb.com/partdetail/C527679 |
| TPS563201 3.3 V buck | SOT-23-6 | C116592 | TI TPS563201DDCR | SOT-23-THIN-6 | Extended | 90,592 | https://jlcpcb.com/partdetail/C116592 |
| TPS61089 boost | Texas_VQFN-RNR0011A-11 | C165129 | TI TPS61089RNRR | VQFN-11-HR-EP (2x2.5) | Extended | 2,502 | https://jlcpcb.com/partdetail/C165129 |
| EL817S / PC817 optocoupler | SOP-4 | C109227 | Lite-On LTV-817S-TA1-C | SMD-4P | Basic | 198,412 | https://jlcpcb.com/partdetail/C109227 |

C51118 is the genuine Diodes Incorporated part, 3.3 V fixed, 600 mA, with enable. JLCPCB
writes its package as "SOT-25-5", which is the same body and land as SOT-23-5.

C527679 is the WSON version of the TPS22810 (3 A, 2.7 to 18 V), which is what the
`WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm` footprint wants. The SOT-23-6 version of the same
device exists as C205990 but would not fit that land.

C116592 is the DDC package, which TI calls TSOT-23-6 and JLCPCB writes as SOT-23-THIN-6. It
is 0.95 mm pitch on the same land geometry as SOT-23-6, so the existing footprint is
compatible; it is a thinner body, not a different land. Worth one look at the placement
preview, but not a blocker.

C165129 is the only stocked TPS61089 (the RNRT variant, C131352, shows zero stock). 2,502 in
stock is comfortable for a five board run but it is the thinnest line in the set, so it is
the one to order early.

C109227 is a Basic part, which is unusual for an optocoupler and worth taking. It is the
surface mount LTV-817S in the 4 pin SMD body that matches `SOP-4_3.8x4.1mm_P2.54mm`, 5 kV
isolation, 35 V collector emitter.

### LED

| value | footprint | LCSC code | manufacturer part | package | Basic or Extended | stock seen | source URL |
|---|---|---|---|---|---|---|---|
| amber hub | LED_0603 | C965802 | XINGLIGHT XL-1608UYC-06 | 0603 | Extended | 1,101,818 | https://jlcpcb.com/partdetail/C965802 |

590 nm yellow/amber, 435 mcd at 20 mA, 2.4 V forward, 120 degree. The only Basic 0603 LED in
the JLCPCB library is the red C2286 (Hubei KENTO KT-0603R); there is no Basic or Preferred
amber or yellow in 0603, so this line costs one feeder fee whichever amber part is used.

---

## 2. Lines skipped as not JLC assembled (105 lines)

| count | what | footprints | why |
|---|---|---|---|
| 16 | 3 mm panel indicators (BAT1 to BAT5, CHG, GPS, LTE, MCAUT, MESH, MSG, MWARN, SAT, SHORE, SOSACT, TX) | `LED_D3.0mm` | panel mounted through hole indicators, fitted by hand behind the C4 face |
| 10 | JST VH 2 pin power leads (5 V M1, M2, Pi rails, mezzanine boost feed, shore DC in, panel in, cell node) | `JST_VH_B2P-VH_1x02_P3.96mm_Vertical` | through hole connector |
| 10 | solder jumpers (BUSJ, CS, EPD RES, PANEL_ID, UART RX/TX select, channel bits CH1/2/4/8) | `SolderJumper-2`, `SolderJumper-3` | copper features on the board, no part to place |
| 9 | JST XH leads (heating pad, DCF77 remote, Touch Display 2 5 V, MAIN button, Pi J2, X1202 switch, Kelvin sense, module thermistor, front wall LED row) | `JST_XH_B2B-XH-A`, `B4B-XH-A`, `B10B-XH-A` | through hole connectors, and several are described as leads |
| 8 | IDC ribbon headers (A to B 2x7 both sides, APRS mezzanine 2x8, RockBLOCK 9704 2x8, PCB-A J_MEZZ1 2x8, panel ribbon 2x10 both sides, Pi 5 GPIO 2x20) | `IDC-Header_2x07/2x08/2x10/2x20_P2.54mm_Vertical` | through hole connectors |
| 7 | SMA jacks (IRID, LORA, LTE, SDR, UHF, WIFI24, WIFI58 pigtails) | `SMA_Amphenol_132134-11_Vertical` | RF connector, excluded by the brief |
| 7 | SMP-MAX slide on receptacles (same seven paths to the dock) | `Radiall_SMPMAX_R222M00720` | blind mate RF connector, excluded by the brief |
| 6 | mini blade fuse holders (10 A x3, 15 A, 10 A panel input, 7.5 A) | `Fuseholder_Blade_Mini_Keystone_3568` | Keystone 3568 holders and their blades, bench fitted |
| 5 | USB-A receptacles (RTL-SDR, ZigBee, GPS, WiFi, Glenair wall host port) | `USB_A_Stewart_SS-52100-001_Horizontal` | excluded by the brief |
| 4 | Coilcraft XAL inductors (1.5uH XAL6030-152MEB, 2.2uH XAL1010-222MED, 2.2uH XAL4030-222MEB, 3.3uH XAL4020-332MEB) | `L_Coilcraft_XAL*` | no JLCPCB equivalent, hand soldered |
| 4 | panel controls (MAIN 19 mm momentary, PI 16 mm, TEST/ACK 16 mm, LIGHTING DPDT ON-ON-ON) | `PanelSwitch_16mm`, `PanelSwitch_19mm`, `PanelToggle_DPDT` | panel mounted mechanical parts |
| 3 | guarded toggles (SOS, EMCON, ZEROIZE) | `GuardedToggle_SPDT` | panel mounted mechanical parts, ruled to APEM 5636ADKB-2V |
| 3 | 9 A spring pins (CELL+, CELL_N return, pre-charge pin) | `Mill-Max_0858_power_pin` | spring pins, excluded by the brief |
| 2 | solder pads for 12 AWG wire (CELL+ targets, return targets) | `SolderPad_8x6` | pads, not parts |
| 2 | pogo pin block (spring pins to the dock block 2x6, solder lands 2x6) | `PogoPins_2x6`, `PogoTargets_2x6` | spring pins and lands |
| 2 | pin headers (e-paper module lead 1x8, SWD/DFU 1.27 mm 1x7) | `PinHeader_1x08_P2.54mm`, `PinHeader_1x07_P1.27mm` | through hole headers |
| 1 | RockBLOCK 9603 PicoBlade 10 | `Molex_PicoBlade_53047-1010` | through hole connector |
| 1 | TRACO TEN 40-2412WIN converter | `Converter_DCDC_TRACO_TEN40-110xxWIRH_THT` | through hole module, bench fitted |
| 1 | battery module lead XT60-M | `AMASS_XT60-M_1x02_P7.20mm_Vertical` | through hole connector, described as a lead |
| 1 | DMR858M 5 W UHF module | `DMR858M` | already marked DNP bench, sits on two 1x12 sockets |
| 1 | USB-C pigtail header JST-PH | `JST_PH_B4B-PH-K_1x04_P2.00mm` | through hole connector |
| 1 | active piezo 5 V 85 dB | `Buzzer_12x9.5RM7.6` | through hole buzzer, 7.6 mm pitch |
| 1 | DNP 100R (mirror now via Q4) | `R_0603` | marked DNP, deliberately not fitted |

That last line is the only skipped one with a usable code if the decision is reversed:
100R 0603 1% is **C22775** (UNI-ROYAL 0603WAF1000T5E, 0603, Basic, 14,125,233 seen,
https://jlcpcb.com/partdetail/C22775).

---

## 3. Open items and things to decide

Two lines have no exact part, and four more have a match but carry a question that only the
design side can settle.

### 3.1 `5.24k 1% (RT1 JEITA)` and `30.31k 1% (RT2 JEITA)`, A19, not orderable as drawn

Neither value exists in the JLCPCB library. This is not a stock problem, it is that neither
is a standard value: the E96 series runs 5.11, 5.23, 5.36 and 30.1, 30.9, 31.6, so 5.24k and
30.31k fall between the rungs. They are the computed numbers from the TI BQ25792 JEITA
worked example rather than values you can buy.

What was tried: JLCPCB keyword search on `0603 5.24k 1%`, `5.24k`, `5.24kohm resistor`,
`5K24 0603`, `resistor 5.24`, and on the two likely manufacturer part numbers
`0603WAF5241T5E` and `RC0603FR-075K24L`; the same for `30.31k`. The only hits on "5.24k"
anywhere in the library are two FUJITSU relays whose coil resistance happens to be 5.24 k.
As a control, `5.11k`, `5.23k` and `5.62k` all return full pages of 0603 1 percent parts, so
the library is not simply failing to index that decade. The LCSC web search was also tried
directly and returns a JavaScript shell with no part codes in the HTML, so it added nothing.
`30.3k` does exist as C620505 (UNI-ROYAL 0603WAF3032T5E) but shows **zero stock**.

Nearest stocked substitutes, both verified:

| wanted | substitute | LCSC code | manufacturer part | package | Basic or Extended | stock seen | error |
|---|---|---|---|---|---|---|---|
| 5.24k 1% | 5.23k 1% | C23068 | UNI-ROYAL 0603WAF5231T5E | 0603 | Extended | 73,049 | 0.19 percent low |
| 30.31k 1% | 30.1k 1% | C23000 | UNI-ROYAL 0603WAF3012T5E | 0603 | Extended | 106,059 | 0.69 percent low |

Both errors are inside the 1 percent tolerance band of the parts themselves, so in practice
the divider moves less than the part spread does. Even so this changes the JEITA trip
temperatures slightly and it is a generator change, not a BOM edit, so it needs whoever set
the JEITA window to confirm. Flagging rather than deciding.

### 3.2 `TPS2065CDBV` is a 5 pin part on a 6 pad land, A19 and B12

The BOM line gives the footprint as `SOT-23-6`. TI's DBV package for the TPS2065C is a
**5 pin** SOT-23: TI's own part page for TPS2065CDBVR
(https://www.ti.com/product/TPS2065C/part-details/TPS2065CDBVR) gives DBV as 5 pin SOT-23,
and JLCPCB reports SOT-23-5 for C353882 and for every other TPS2065 orderable in the
library. There is no 6 pin variant of this device; the 6 and 8 pin siblings are different
part numbers. So either the footprint is wrong or the schematic symbol is. This affects both
A19 and B12 and would not assemble as drawn. The code is right (C353882, TPS2065CDBVR,
Extended, 7,204 seen); the land needs checking before those two lines go to the cart.

### 3.3 `SMBJ15A` on a `D_SMC` land, E4

SMBJ is the DO-214AA (SMB) body; SMC is DO-214AB, which is the larger case. The value text
and the footprint disagree. Two clean ways out, both verified:

- Keep the `D_SMC` land and change the value to **SMCJ15A**: C42371550 (hongjiacheng, SMC
  DO-214AB, Preferred, 5,964 seen). Same 15 V standoff and 24.4 V clamp, 1.5 kW instead of
  600 W, so it is strictly the better protector and it matches the two SMCJ33A parts already
  on that board.
- Or change the footprint to `D_SMB` and keep SMBJ15A: C908796 (GOODWORK SMBJ15A, DO-214AA
  SMB, Extended, 76,626 seen).

The first is recommended because it is a value change in the generator and no board change,
and it keeps all three TVS parts on E4 in one case size. The dict in section 4 uses the
SMCJ15A code on the assumption the land is kept; change it if the other route is taken.

### 3.4 Thermistor beta constant, A19

The line names a **103AT-2**, which is a Semitec leaded glass bead with a beta of 3435 K.
The board mounted 0603 part found for it, C13564 (Murata NCP18XH103F03RB), is 10 k plus or
minus 1 percent but its beta is **3380 K**. Both read 10 k at 25 C, so the resistance at
room temperature is identical, but the curve diverges away from 25 C and any gauge
coefficients derived from a 3435 K table will read a degree or two out at the ends of the
range. This ties into 3.1: if the JEITA and gauge tables are being recomputed anyway, do it
once against whichever thermistor is actually fitted. Note that the separate leaded 103AT on
the E4 charger lead is unaffected, it is in the skipped list.

### 3.5 Crystal load capacitance on B12

C9002, the 12 MHz Basic part, is specified for a 20 pF load, which wants roughly 33 to 39 pF
loading capacitors on each leg. B12's loading capacitors are not in this input list, so they
already carry codes and their value was not checked here. If they turn out to be 27 pF like
the A19 pair, the right 12 MHz part is a 12 pF load type instead, for instance C133337
(Yajingxin TAXM12M4RFBCCT2T, SMD3225-4P, Extended, 26,029 seen) or C50430 (YXC
X322512MMB4SI, 10 pF, Extended, 8,317 seen). Worth one grep of the B12 netlist before
ordering. Marked uncertain because the loading caps were outside the input list.

### 3.6 Fuse working voltage on A19

`2.5A hold 1812` takes C210838, rated 16 V. The input list does not say which net it guards.
16 V covers a 12 V rail with margin but not shore DC, which the E4 lines show reaching 36 V.
If it sits anywhere upstream of the converters this part is wrong and a 30 V or higher class
1812 should be used instead. Uncertain until the net is known.

---

## 4. Python dict block

Same style as the existing table: regex on the value, footprint substring. Regexes are
anchored and written so that no two collide (for example `^102k 1%` and `^105k 1%` are
separate parts, and `^10k 1%` cannot match `100k 1%` because the character after `10` is a
digit, not a `k`). The `$` anchors on the bare capacitor values keep the 1206 and 1210 lines
apart even before the footprint substring is consulted.

```python
LCSC = {
    # ---- resistors, 0603, 1% (thick film, 100 mW, 75 V) ----
    (r"^1\.02k 1%", "R_0603"): "C2998111",
    (r"^10\.0k 1%", "R_0603"): "C25804",
    (r"^10k 1%", "R_0603"): "C25804",
    (r"^100k 1%", "R_0603"): "C25803",
    (r"^102k 1%", "R_0603"): "C2933126",
    (r"^105k 1%", "R_0603"): "C16840",
    (r"^115k 1%", "R_0603"): "C22783",
    (r"^12\.0k 1%", "R_0603"): "C22790",
    (r"^13\.7k 1%", "R_0603"): "C22793",
    (r"^15\.0k 1%", "R_0603"): "C22809",
    (r"^16\.5k 1%", "R_0603"): "C22812",
    (r"^17\.4k\b", "R_0603"): "C2930069",
    (r"^2\.7k 1%", "R_0603"): "C13167",
    (r"^20k 1%", "R_0603"): "C4184",
    (r"^215k 1%", "R_0603"): "C5713280",
    (r"^301k 1%", "R_0603"): "C2933194",
    (r"^33\.2k 1%", "R_0603"): "C23003",
    (r"^34\.8k 1%", "R_0603"): "C2933204",
    (r"^4\.7k 1%", "R_0603"): "C23162",
    (r"^7\.50k 1%", "R_0603"): "C23234",
    (r"^75k 1%", "R_0603"): "C23242",
    (r"^8\.87k\b", "R_0603"): "C2998144",

    # substitutes: 5.24k and 30.31k are not E96 and are not stocked (findings 3.1)
    (r"^5\.24k 1%", "R_0603"): "C23068",     # 5.23k fitted instead, 0.19% low
    (r"^30\.31k 1%", "R_0603"): "C23000",    # 30.1k fitted instead, 0.69% low

    # board mounted gauge thermistor (beta 3380 K, not the 103AT's 3435 K, findings 3.4)
    (r"^103AT-2 10k NTC", "R_0603"): "C13564",

    # ---- resistors, other packages ----
    (r"^0\.05R 1% 1206$", "R_1206"): "C601088",
    (r"^0\.1R 1% 1206$", "R_1206"): "C2903496",
    (r"^10R 2W 2512$", "R_2512"): "C414890",

    # ---- capacitors ----
    (r"^100p$", "C_0603"): "C14858",
    (r"^1n$", "C_0603"): "C1588",
    (r"^3\.3n$", "C_0603"): "C1613",
    (r"^10n$", "C_0603"): "C57112",
    (r"^27p$", "C_0603"): "C107045",
    (r"^47n$", "C_0603"): "C1622",
    (r"^470n 25V$", "C_0603"): "C1623",
    (r"^2\.2u$", "C_0603"): "C57895",
    (r"^4\.7u$", "C_0805"): "C1779",
    (r"^4\.7u 25V$", "C_1206"): "C132170",   # 50 V part, covers both 1206 4.7u lines
    (r"^4\.7u 50V$", "C_1206"): "C132170",
    (r"^10u 25V$", "C_1206"): "C89632",      # 50 V part, covers both 1206 10u lines
    (r"^10u 50V$", "C_1206"): "C89632",
    (r"^22u 25V$", "C_1206"): "C12891",
    (r"^100u 10V$", "C_1206"): "C6119961",
    (r"^10u 25V 1210$", "C_1210"): "C2918497",
    (r"^22u 10V X7R 1210$", "C_1210"): "C2918511",   # 25 V part, better bias at 10 V
    (r"^22u 25V X7R 1210$", "C_1210"): "C2918511",

    # ---- resettable fuses ----
    (r"^0\.5A hold 1812$", "Fuse_1812"): "C17313",
    (r"^2A hold 1812$", "Fuse_1812"): "C210837",
    (r"^2\.5A hold 1812$", "Fuse_1812"): "C210838",  # 16 V only, check the net (3.6)

    # ---- crystals ----
    (r"^12 MHz 3225$", "Crystal_SMD_3225"): "C9002",   # 20 pF load, confirm B12 caps (3.5)
    (r"^24 MHz 3225$", "Crystal_SMD_3225"): "C70571",  # 18 pF load, suits the 27p pair

    # ---- discrete semiconductors ----
    (r"^2N7002\b", "SOT-23"): "C8545",
    (r"^BC847\b", "SOT-23"): "C20069135",
    (r"^BC857\b", "SOT-23"): "C556165",
    (r"^BAT54\b", "D_SOD-123"): "C7502705",
    (r"^SMBJ5\.0A$", "D_SMB"): "C113974",
    (r"^SMCJ33A\b", "D_SMC"): "C42371548",
    (r"^SMBJ15A$", "D_SMC"): "C42371550",    # SMCJ15A, matches the SMC land (findings 3.3)

    # ---- ICs and optocoupler ----
    (r"^AP2112K-3\.3\b", "SOT-23-5"): "C51118",
    (r"^TPS2065CDBV\b", "SOT-23-6"): "C353882",   # part is SOT-23-5, land mismatch (3.2)
    (r"^TPS563201\b", "SOT-23-6"): "C116592",
    (r"^TPS22810DRV\b", "WSON-6"): "C527679",
    (r"^TPS61089\b", "Texas_VQFN-RNR0011A-11"): "C165129",
    (r"^EL817S / PC817", "SOP-4"): "C109227",

    # ---- LED ----
    (r"^amber hub$", "LED_0603"): "C965802",

    # DNP as drawn; uncomment only if the Q4 mirror resistor is fitted after all
    # (r"^DNP 100R\b", "R_0603"): "C22775",
}
```

---

## 5. Count

| outcome | lines |
|---|---|
| resolved with an exact match | 70 |
| resolved only with a substitute value (5.24k, 30.31k) | 2 |
| skipped as not JLC assembled | 105 |
| **total** | **177** |

Counted by BOM line, the 72 resolved lines break down as 23 Basic, 8 Preferred and
41 Extended.

Counted by distinct part instead, the 65 dict entries collapse to **61 distinct LCSC codes**
(four codes are shared between two lines each: C25804 across `10.0k` and `10k`, and the three
capacitor merges below). Of those 61 codes, **20 are Basic and 5 are Preferred**, neither of
which carries the per line feeder fee, and **36 are Extended** and do. The three merges in
section 1 (C132170 for both 1206 4.7u lines, C89632 for both 1206 10u lines, C2918511 for
both 1210 22u lines) already removed three Extended fees.

The dict in section 4 was run back against `lcsc-needed.txt` as a check: all 72 assemblable
lines match exactly one entry, none match zero, and none match two.

Nothing in the list failed to load. The LCSC search page will not render without JavaScript
and returned no part codes, but it was only needed as a cross check and the JLCPCB catalogue
answered every query directly.

---

## 6. Follow ups of 4 September, and one correction to section 3.4

Three questions came back from the coordinator after the first pass. Same method: every code
below was read from its own JLCPCB catalogue record, and this time the structured attribute
fields were pulled rather than the free text `describe` string, because on one part the two
disagree (see the Littelfuse note in 6.1). Section 5 above is unchanged; the counts there
still stand.

### 6.1 A 30 V class 1812 PTC for the SHORE_12V heating pad feed

The net is now known: the PTC sits between SHORE_12V and the heating pad feed, and the TVS on
that rail is the SMCJ15A of 3.3, which clamps at **24.4 V maximum**. The C210838 named in
section 1 is a 16 V part, so it is indeed under rated for a clamp event and must be replaced.

Recommended swap, an exact hold current match for the part it replaces:

| item | value |
|---|---|
| LCSC code | **C52748011** |
| manufacturer part | LUTE 1812L250/30GR |
| package | 1812 (4.73 x 3.41 x 1.5 mm) |
| library | Extended |
| stock seen | 19,625 |
| **hold current** | **2.5 A** |
| **trip current** | **5 A** |
| **maximum voltage** | **30 V** |
| maximum fault current | 40 A |
| resistance, initial minimum | 15 mOhm |
| resistance, post trip maximum | 90 mOhm |
| time to trip, maximum | 2.5 s |
| power dissipation | 1 W |
| operating temperature | -40 to +85 C |
| source | https://jlcpcb.com/partdetail/C52748011 |

30 V against a 24.4 V clamp leaves about 5.6 V of margin, which is the answer to the
question asked. Note what the rating means: a PTC maximum voltage is the voltage the device
must be able to interrupt while tripped, so the comparison against the TVS clamp voltage is
the right one, and a brief clamp event is well inside it.

Alternative, if higher stock and lower series resistance matter more than an exact 2.5 A:

| item | value |
|---|---|
| LCSC code | **C20617446** |
| manufacturer part | LUTE 1812L260/30GR |
| library | Extended |
| stock seen | 34,079 |
| hold current | 2.6 A |
| trip current | 5 A |
| maximum voltage | 30 V |
| maximum fault current | 40 A |
| resistance, initial minimum | 10 mOhm |
| resistance, post trip maximum | 70 mOhm |
| time to trip, maximum | 2.5 s |
| source | https://jlcpcb.com/partdetail/C20617446 |

Series resistance is worth one thought on a heating pad feed, because a PTC is a resistor in
the path all the time. The post trip maximum of 90 mOhm on C52748011 means that after a trip
and reset the worst case drop at 2 A is 180 mV and the part dissipates 0.36 W into its own
1 W budget. C20617446 is better on both counts (70 mOhm, and 10 mOhm initial rather than 15).

Two candidates were looked at and rejected, both worth recording:

- **C54300299** (LUTE 1812L260/33GR) would be the 33 V version of the same family, and its
  part number implies 2.6 A at 33 V. JLCPCB carries **no attribute fields and no datasheet
  link** for this code, only the package and a stock figure of 2,385. Its ratings are
  therefore **unverified** and it is not recommended. Reading a hold current and a voltage
  out of the part number would be exactly the guessing the brief rules out.
- **C315954** (Littelfuse MINISMDC260F-2) looked like a 60 V, 2.6 A part in the free text
  `describe` string. Its structured attributes give **Voltage - Max = 6 V**, not 60 V, which
  matches Littelfuse's own MINISMDC260F specification. The `describe` string concatenates
  numbers without units in a way that can be read wrongly, and this is the one case in this
  whole exercise where it would have produced a wrong answer. Stock is 1 in any case.

No 1812 PTC at 2.5 A class and 60 V is stocked. 30 V is the best available in this case size
at this current, and it clears the clamp voltage.

### 6.2 Crystal load capacitance, and the 33 pF loading capacitor

Both load capacitances confirmed from the parts' own attribute fields, not from the search
summary:

| code | part | frequency | **load capacitance** | tolerance | stability | ESR | library | stock seen |
|---|---|---|---|---|---|---|---|---|
| C9002 | YXC X322512MSB4SI | 12 MHz (PCB-B) | **20 pF** | plus or minus 10 ppm | plus or minus 20 ppm | 80 Ohm | Basic | 167,759 |
| C70571 | YXC X322524MRB4SI | 24 MHz (PCB-A) | **18 pF** | plus or minus 10 ppm | plus or minus 20 ppm | 50 Ohm | Extended | 34,453 |

Both are -40 to +85 C. Datasheets:
https://www.lcsc.com/datasheet/lcsc_datasheet_2403291504_YXC-Crystal-Oscillators-X322512MSB4SI_C9002.pdf
and
https://www.lcsc.com/datasheet/lcsc_datasheet_2403291504_YXC-Crystal-Oscillators-X322524MRB4SI_C70571.pdf

Loading capacitor for the 20 pF part:

| value | footprint | LCSC code | manufacturer part | package | Basic or Extended | stock seen | source URL |
|---|---|---|---|---|---|---|---|
| 33p | C_0603 | **C1663** | Samsung CL10C330JB8NNNC | 0603 | **Basic** | 1,433,141 | https://jlcpcb.com/partdetail/C1663 |

Read from its own attribute fields: Capacitance 33 pF, Voltage Rating 50 V, Tolerance plus or
minus 5 percent, Temperature Coefficient **C0G**. It is a Basic part, so this line costs no
feeder fee. The best Extended alternative is C107047 (YAGEO CC0603JRNPO9BN330, NP0, 50 V,
plus or minus 5 percent, 3,153,779 seen) if Samsung stock ever moves.

The existing 27 pF part is confirmed as asked:

| code | part | capacitance | voltage | dielectric | tolerance | library | stock seen |
|---|---|---|---|---|---|---|---|
| C107045 | YAGEO CC0603JRNPO9BN270 | 27 pF | **50 V** | **NP0** | plus or minus 5 percent | Preferred | 1,014,256 |

NP0 and C0G are the same EIA characteristic under two names, C0G being the EIA code and NP0
the older industry term, so this part is a genuine class 1 dielectric and is correct on a
crystal rather than only in a feedforward path. Nothing needs to change on that line.

Arithmetic for the record, using the usual `CL = C/2 + Cstray`:

- PCB-B, 12 MHz, C9002 at 20 pF, with 33 pF each leg: 33/2 + 4 = 20.5 pF against a 20 pF
  specification.
- PCB-A, 24 MHz, C70571 at 18 pF, with the existing 27 pF each leg: 27/2 + 4 = 17.5 pF
  against an 18 pF specification.

Both land within half a pF of the crystal specification, which at these frequencies and a
plus or minus 20 ppm stability grade is well inside the pulling range. The 4 pF stray figure
is an **assumption**, being a typical allowance for short 0603 traces plus oscillator pin
capacitance; it was not measured and is not on any datasheet. If the real layout stray is
nearer 2 pF or 6 pF the numbers move by about plus or minus 2 pF, which is still inside range
for both, so the choice of 33 pF and 27 pF is robust to that uncertainty either way.

### 6.3 C13564, the gauge thermistor, and a correction to section 3.4

Confirmed from the part's own attribute fields:

| item | value |
|---|---|
| LCSC code | C13564 |
| manufacturer part | Murata NCP18XH103F03RB |
| package | 0603 (1.6 x 0.8 mm) |
| **library type** | **Extended** (not Basic, not Preferred) |
| stock seen | 395,089 |
| resistance at 25 C | 10 kOhm |
| **resistance tolerance** | **plus or minus 1 percent** |
| **B constant tolerance** | **plus or minus 1 percent** |
| **B constant (25/50 C)** | **3380 K** |
| **B constant (25/85 C)** | **3434 K** |
| **B constant (25/100 C)** | **3455 K** |
| operating temperature | -40 to +125 C |
| power | 100 mW, dissipation factor 1 mW per degree C |
| maximum steady state current | 310 uA |
| datasheet | https://www.lcsc.com/datasheet/lcsc_datasheet_1810311113_Murata-Electronics-NCP18XH103F03RB_C13564.pdf |
| source | https://jlcpcb.com/partdetail/C13564 |

**Correction to section 3.4.** That section said the part has "a beta of 3380 K" against the
103AT-2's 3435 K and warned the curves diverge. That comparison was between two different
intervals and overstated the problem. Murata does not quote one beta for this part, it quotes
three, and the interval that matches how a 103AT is normally specified is **B(25/85), which
is 3434 K against the 103AT-2's 3435 K**. Over the 25 to 85 C span the two curves are within
1 K of each other, which is inside the plus or minus 1 percent B tolerance of the Murata part
and is effectively no difference at all.

What this means for the gauge configuration:

- Do not write the gauge against a single beta figure. Use the interval that covers the
  operating window, or better, use Murata's own resistance versus temperature table for the
  XH curve, which is what the plus or minus 1 percent B tolerance is specified against.
- From 25 C up to 85 C, a configuration already written for a 103AT at 3435 K will track this
  part almost exactly.
- The divergence is at the cold end, below 25 C, where the 25/50 interval figure of 3380 K
  applies. That is the region to check if the kit is expected to report pack temperature
  below freezing, which given the heating pad on the same board it plainly is.
- Both tolerances are plus or minus 1 percent, resistance and B constant, so the part is a
  precision grade rather than a plus or minus 5 percent commodity thermistor. The gauge can
  be trusted to about a quarter of a degree near 25 C from the part alone.

Section 3.4 should be read as superseded by this entry. The rest of 3.4 stands: this is the
board mounted gauge sensor on PCB-A, and the leaded 103AT on the E4 charger lead is a
separate part in the skipped list and is unaffected.

### 6.4 Dict block for the follow ups

Paste alongside the block in section 4. The first entry replaces the `2.5A hold 1812` line
that is already there, it does not sit next to it.

```python
LCSC_FOLLOWUP = {
    # 6.1 replaces C210838 (16 V) on the SHORE_12V heating pad feed.
    # 30 V max, clears the SMCJ15A 24.4 V clamp. Hold 2.5 A, trip 5 A.
    (r"^2\.5A hold 1812$", "Fuse_1812"): "C52748011",

    # 6.2 loading capacitors for the 20 pF crystal C9002 on PCB-B.
    # 33 pF, 50 V, C0G, plus or minus 5 percent, and a Basic part.
    (r"^33p$", "C_0603"): "C1663",
}
```

Two notes on pasting this. The `2.5A hold 1812` key is byte for byte the key already in
section 4, so a plain `dict.update()` does the replacement cleanly and nothing else needs
editing. The `^33p$` key assumes the generator writes the new PCB-B loading capacitors as a
bare `33p`, matching how the existing `27p` line is written; if it writes them as
`33p 50V` or similar the anchor needs relaxing to `^33p\b`.

No change is needed for C9002, C70571, C107045 or C13564. All four codes in section 4 stay
as they are; this follow up only confirmed their specifications.
