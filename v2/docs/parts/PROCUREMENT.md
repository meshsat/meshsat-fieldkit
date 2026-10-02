# Procurement constraints, supported alternatives and grade findings (pre-PCB layer 6)

Prototype design (MESHSAT-1357, closer hc6, 27 September 2026). Nothing has been built, bought for assembly, powered or
deployed. The order set stays quarantined (decision 41) and every purchase stays with the owner: this page orders
nothing, logs into nothing and puts nothing in a cart. Every stock figure is a reading of a public page at the time
given, and it is true only at that time.

**Judged at** main `53a98a71` (the six committed netlists, `v2/ecad/tools/lcsc_fill.py`, `v2/release/revA/order/JLC-CERTIFIED.tsv`):
round 8's boards A, D and E are integrated there; boards B, C and P are byte-identical to `e3aedb25`, where the layer 6
audit was taken. Quantities are per kit from the netlists, times five kits (the owner's "minimum 5 of each"). Board B's
round 8 part changes (the DS3231SN land, the U.FL codes, the key-B socket's locating holes) are in worktree `r8b`, not
on main; where one moves a row below it is said. Round 8's new codes on A and D (C2657885, C139409, C37593, C113780)
have no row in the certification table yet (the round 8 re-take left A32, D12 and E17 without a folder), so their
readings here are this page's own.

Companion pages: `v2/docs/parts/STM32H743-COMPATIBILITY.md` (the supervisor matrix), `v2/docs/parts/GRADE-CHECK.md`
(generated: every fitted active part and connector against the envelope, from `grade-sources.yaml` by
`grade_check.py`), and the readings in `v2/docs/parts/readings/`.

## 1. How the readings were taken

| Source | What was asked | When (UTC, 27 September 2026) | File |
|---|---|---|---|
| JLCPCB public parts API (the endpoint `jlc_certify.py:40` uses) | stock by LCSC code for 58 critical codes; keyword searches for alternatives | 00:02 to 00:20 | `readings/jlc-2026-09-27.json` |
| LCSC public product detail | model, stock, parameters, datasheet link for every code on a fitted BOM line (203 codes) | 00:04 to 00:07, 00:24 | `readings/lcsc-2026-09-27.json` |
| FindChips (Supplyframe's public aggregator page) | authorised and broker distributor offers for 51 order codes | 00:03 to 00:16 | `readings/findchips-2026-09-27.json` |
| Makers' pages and sheets | ranges, order codes and suffixes (Ground Control, Mill-Max, JST, Wurth, Pulse, Radiall, Preci-Dip) | 00:08 to 00:26 | filed in `v2/vendor/` (section 7) |
| JLCPCB public parts API, second reading | round 8's new codes on main and every constrained code of sections 2 and 3 again; keyword searches for HX6096NL | 03:59 to 04:06 | `readings/jlc-r8-main-2026-09-27.json` |
| Makers' pages, second pass | Pulse's product finder (HX6096NL sheet); URL checks of held documents (AsiaRF, Raspberry Pi, Radiall, Glenair, Xenarc) | 03:56 to 04:05 | section 7 |

FindChips repeats one stock figure across a distributor's packaging rows (cut tape, reel, Digi-Reel); the largest
figure per distributor is quoted, never the sum. A broker offer (Win Source, Chip Stock, Chip 1 Exchange, Unikey,
Bristol) is listed for completeness and is **not** a supported source for this prototype (HC6-SC-12).

## 2. The five constraints the audit named

### 2.1 Board P F2, the chemical fuse Eaton SCF9550-30-05 (C3670061)

- **Readings.** JLCPCB 0 (00:18:42Z), LCSC 0 (00:05:28Z); DigiKey 907 cut tape (283-SCF9550-30-05CT-ND), Avnet 0
  (lead time 12 weeks, MOQ 3000), Sager 0 (FindChips 00:13:37Z). Need 5.
- **Single source.** Eaton only; the SCF9550 order code fixes the cell count and the trip element, so no other code
  of the family is a drop-in: SCF9550-45-07 (C3667292, JLCPCB stock 10) is a 45 A part for a different cell count
  and stays a mismatch.
- **Alternatives, each a mismatch until the owed battery review R-BAT accepts it:** the Littelfuse ITV9550
  30 A family (`v2/vendor/battery/littelfuse-itv9550-30a.pdf`, SOURCES `pack-chemical-fuse-alternative`, evaluated
  and not fitted; every ITV9550 code at JLCPCB read 0 at 00:02:44Z), and the Dexerials SFK series
  (`v2/vendor/battery/dexerials-sfk-series-datasheet.pdf`, refused in round 4 for want of a published temperature range
  and land: `v2/vendor/vendor-status.txt`, FUSE-INTERPRETATION.md).
- **Grade.** "Operating temperature: -20 C to +60 C" (AT_LIMIT at the envelope's floor) and "Storage temperature:
  -10 C to +40 C < 90% RH, Storage duration: 1 year" (`v2/vendor/battery/eaton-scf9550-elx1135.pdf`, General
  specifications). The storage line reads like a shelf condition for the unmounted part; if it applies to the mounted
  fuse, it is narrower than the envelope's storage (-20 to +45 C) and the -33 C and +71 C margins. **Question for
  R-BAT and for Eaton (VENDOR_CONFIRMATION):** does the storage figure bind the assembled pack?
- **HC6-SC-9.** Buy SCF9550-30-05 from an authorised distributor and fit it as a hand-fit (consigned) line on board P,
  declared in board P's own `lcsc-allow.txt` (lcsc_fill reads only the board's own list, SOURCES
  `wrong_model_that_stands`); no alternative is adopted. Reverse if JLCPCB restocks before the order.

### 2.2 Board P U2, the second-level protector TI BQ7720700DSSR (C3681715)

- **Readings.** JLCPCB 3 (00:18:41Z), LCSC 3 (00:05:28Z): short of 5. DigiKey 2648 (cut tape, reel and Digi-Reel,
  FindChips 00:13:40Z). A search for the 250-piece reel BQ7720700DSST returned only DSSR offers.
- **Single source.** TI only; the "00" variant is the threshold set (OV 4.325 V, UV 2.25 V, OT 70 C) the pack design
  rests on; another BQ77207xx variant is a different protector, not an alternative.
- **Grade.** TA -40 to +85 C (`v2/vendor/battery/ti-bq77207.pdf`, Recommended Operating Conditions): INSIDE.
- **HC6-SC-9 (same rule).** Consign from an authorised distributor (DigiKey holds 2648) if JLCPCB still reads below 5
  at order time; the part does not change.

### 2.3 Board B Y1 to Y4, the 25 MHz crystal Yajingxin TAXM25M4RFBCCT2T (C164047)

- **Readings.** JLCPCB 3 (00:18:28Z, and again 3 at 04:00:03Z), LCSC 0 (00:04:46Z) against a need of 20 (four per kit: Y1 on the KSZ9897R, Y2 to
  Y4 on the three supervisors). FindChips shows LCSC with 19,150 at 00:13:45Z; LCSC's own API read 0 nine minutes
  earlier, so the aggregator's figure is taken as stale.
- **The criteria a replacement must meet.** The KSZ9897R's Table 6-12 (ESR at most 50 Ohm, +-50 ppm, 100 uW;
  `v2/vendor/cluster/ksz9897.pdf`, DS00002330E p.181) and the STM32H743's HSE criterion (gm_crit at or below
  Gmcritmax 1.5 mA/V, DS12110 Rev 11 Table 131). `STM32H743-COMPATIBILITY.md` section 7 computes both.
- **HC6-SC-3.** C9006 YXC X322525MOB4SI: JLCPCB basic library, 165,557 (00:18:29Z); YXC sheet ESR 50 Ohm, C0 3 pF,
  CL 12 pF, gm_crit 1.11 mA/V, pads 1/3 crystal and 2/4 ground (the `Crystal_GND24` symbol). Alternate C91750 Seiko
  Epson X1E0000210139, 6,098 (00:18:30Z), ESR 40 Ohm. The same land and load capacitors; the code change is board B's
  author's (`gen_sch_b.py:1150` and Y1's line).

### 2.4 Board D U2, the NiceRF SA868 order code (NOT_PINNED)

- **What the makers' documents give.** The held sheet V1.3 (`v2/vendor/nicerf/nicerf-sa868-datasheet-v1.3.pdf`) lists
  UHF 400 to 480 MHz, VHF 134 to 174 MHz and a 350 band as variants of one module and no order code. NiceRF's product
  page (Internet Archive capture of 2026-09-22 of
  `https://www.nicerf.com/item/2w-embedded-walkie-talkie-module-sa868`, fetched 00:02Z) offers "SA868 2W Embedded walkie
  talkie moduleV1.4", a newer sheet than the one held; its file host did not resolve from this host, and nicerf.com
  answered HTTP 403 to every product page.
- **The catalogue trap.** JLCPCB lists **SA868-U** (C3001507, stock 1, UHF) and **SA868S** (C52140339, stock 0, a
  different model). Neither is the part: the kit's APRS channel is 144.800 MHz, in the VHF variant only, and the S
  model is a substitution under condition 1.
- **HC6-SC-10.** The order code is **SA868-V** (NiceRF's band suffix, as its SA868-U and SA818S-V catalogue entries
  show). This is INFERRED from the maker's naming, not read in a NiceRF ordering table, so it carries a
  VENDOR_CONFIRMATION at purchase (the owner's) and the V1.4 sheet is owed. Reverse if NiceRF names the VHF variant
  otherwise.

### 2.5 Board B J_M2C2, the Quectel RM520N-GL order code (NOT_PINNED)

- **What exists.** Distributors list RM520NGLAA-M20-SGASA, -ESIM, -ESIM15, -PC15, -FC23 and RM520NGLAP-M20-SGASA
  (FindChips 00:03:33Z). Avnet describes -SGASA as the "MMWAVE M.2 FORM" standard SKU, RoHS true, lead time 13 weeks;
  the -ESIM variants carry an embedded SIM and read RoHS false; -PC15, -FC23 and the AP variant are not decoded by any
  held Quectel document. Stock: DigiKey 0 (MOQ 100, tray), Avnet 0; brokers only otherwise.
- **HC6-SC-11.** The order code is **RM520NGLAA-M20-SGASA**: the standard global SKU, a physical SIM through the
  socket's UIM lines (board B carries nano-SIM holders), RoHS. INFERRED from distributors' descriptions; a Quectel
  ordering document is owed and a VENDOR_CONFIRMATION goes with the purchase (the owner's, bought as a card).
- **Not an alternative.** RM520N-EU (the held hardware design V1.1 covers it) has five antenna ports (Table 32) against
  the GL's four, so the antenna plan changes.
- **Grade.** Operating -30 to +75 C, extended -40 to +85 C with 3GPP deviations (hardware design V1.1): INSIDE.

## 3. Single-source critical parts

"Critical" is SOURCES.yaml's own criterion (safety, a mission function, or a contested identity). Need = per kit x 5.
"Authorised" is the largest franchised-distributor figure FindChips showed. Every part here comes from one maker;
the "Alternative" column names what is supported and its state under condition 1.

| Part (order code) | Board, refs | Need | JLCPCB (UTC 00:18-00:19) | Authorised distributors (FindChips) | Constraint | Alternative and its state |
|---|---|---|---|---|---|---|
| ST STM32H743VIT6 (C114409) | B U41, U51, U61 | 15 | 4265 | DigiKey 0, Farnell 0, TME 39, Schukat 176 | revision V or X only (HC6-SC-1); franchised stock thin | STM32H743VIT6TR C5271084 (894, same part on reel): MATCH; STM32H753VIT6 C730206 (0): the first-named part, not needed |
| Microchip KSZ9897RTXI (C638299) | B U1 | 5 | 205 | DigiKey 4969, Avnet 44 | none | none needed |
| Diodes PI7C9X2G404SLBFDEX (C500767) | B U101, U201, U301 | 15 | 2770 | DigiKey 70 | franchised stock thin | PI7C9X2G304SL (held sheet) is a 3-port part: not a drop-in |
| TI TUSB8041IRGCR (C544686) | B U102, U202, U302 | 15 | 3180 | DigiKey 1304 | none | none needed |
| TI TMUXHS4212IRKSR (C3656912) | B U109, U209, U309 | 15 | 3909 | DigiKey 0, TME 0 | JLCPCB is the only franchised-grade stock read; the I suffix is the -40 to +105 C part | TMUXHS4212 without I is 0 to +70 C: not an alternative |
| TI TPS23861PWR (C93245) | B U5 | 5 | 26 | DigiKey 8813 | none | none needed |
| Pulse H5007NL (C6384935) | B T1 | 5 | 306 | DigiKey 6838, Farnell 632 | **grade OUTSIDE (0 to 70 C), and no PoE rating on its sheet while it carries the 802.3at feed** | HX6096NL, section 4 (HC6-SC-6) |
| Microchip ATECC608B-SSHDA-T (C1518769) | B U8 | 5 | 2342 | Avnet 8000, DigiKey 534 | the part choice waits on Z-EXP-A/B (FB-ZER-1, the owner's purchase) | SLB 9673 TPM 2.0 fallback, no JLCPCB stock (ARCHITECTURE.md line 1043 at `53a98a71`) |
| ADI DS3231SN#T&R (C9866) | B U9 | 5 | 4686 | DigiKey 5933 | the land at `e3aedb25` is SOIC-8 for a 16-pin part (round 8 r8b draws SOIC-16W) | none needed once r8b merges |
| TI BQ4050RSMR (C157570) | P U1 | 5 | 15945 | DigiKey 5311 | none | none needed |
| Keystone 3568 mini blade holder (no code) | A F1; E F1, F2, F3; P F1 | 25 | not placed by JLCPCB (through-hole) | not read: FindChips answered unrelated parts for the bare number (00:15:35Z) | hand-fit; route `v2/ecad/tools/jlc-handfit.txt:66` (DigiKey), allow lines on E and P since round 8 | none; range TBD (no Keystone sheet held, GRADE-CHECK.md) |
| TI BQ7720700DSSR (C3681715) | P U2 | 5 | **3** | DigiKey 2648 | short at JLCPCB | section 2.2 |
| Eaton SCF9550-30-05 (C3670061) | P F2 | 5 | **0** | DigiKey 907 | short at JLCPCB | section 2.1 |
| TI BQ25731RSNR (C2871872) | A U3 | 5 | 1137 | DigiKey 0 | franchised 0 | none needed while JLCPCB holds stock |
| TI LM5176PWPR (C442493) | A (7 stages) | 35 | 12309 | DigiKey 332 | none | none needed |
| TI TPS25740ARGER (C544309) | A U18 | 5 | 2949 | DigiKey 0 | franchised 0 | TPS25740B (held sheet) is another variant: a mismatch until compared |
| TI TPS259631DDAR (C2155778) | A, B (6 per kit) | 30 | 4423 | DigiKey 2576 | none | none needed |
| ADI LTC2954ITS8-1#TRPBF (C2657885, round 8, on main) | A U1 | 5 | **0** (00:18:48Z and 03:59:54Z) | DigiKey 4807 | **short at JLCPCB**; the code the design had before, #TRMPBF (C580654, 197), is not in the maker's order table and stays a condition 1 mismatch (SOURCES `power-button-controller`, `update_r8a`) | consign #TRPBF from DigiKey (HC6-SC-9); the part does not change |
| TI SN74AUP1G08DBVR (C139409, round 8) | A U35 to U38, the PA and HF rails' EMCON gates | 20 | 12,485 (03:59:56Z) | not read | none | none needed; another maker's 74AUP1G08 would be a substitution under condition 1 |
| TI ADS1115IDGSR (C37593, round 8) | D U22, the PA flange temperature ADC | 5 | 33,574 (03:59:57Z) | not read | TI only | none needed |
| ADI LT8705AEUHF#TRPBF (C674164) | E U5 | 5 | **3** | DigiKey 2438 (reel), 155 (#PBF tube) | **short at JLCPCB** (not named by the audit; found here) | LT8705AEUHF#PBF is the same part in a tube (the ordering table of the sheet LCSC serves lists #PBF and #TRPBF on one row): MATCH; consign from DigiKey |
| Quectel LG290P03AAMD (C29781241) | B U11 | 5 | 73 | DigiKey 35 | thin | none needed at 5 kits |
| Ebyte E22-900M30S (C411294) | B U12 | 5 | 551 | none franchised | Ebyte only | none needed |
| Ebyte E72-2G4M20S1E (C5352930) | B U13, U14 | 10 | **0** | none | **short at JLCPCB** (not named by the audit; found here) | Ebyte direct as a hand-fit module; no other maker makes this pin-out |
| Amphenol 10164227-1004A1RLF (C7435219) | B (6 receptacles) | 30 | 1238 | DigiKey 66 | JLCPCB is the stock | none needed |
| TE 2199119-3 (C590866) | B J_M2C2 | 5 | 1427 | DigiKey 8926 | land holes owed on main (S-12, r8b draws them) | none needed |
| TE 2199230-4 (C2977809) | B J_M2C1, J_M2C3 | 10 | 6464 | Farnell 7656 | none | none needed |
| TI TCAN334DR (C2871143) | B (6) | 30 | 479 | DigiKey 0, Farnell 317 | none | TCAN334GDR (5 Mbps, same pins) is not needed at 1 Mbps |
| Radiall R222M00720 (no code) | A J_BM1 to J_BM11 | 55 | not in catalogue | DigiKey 1335 | hand-fit; Radiall only | none (the blind-mate pair is a Radiall system) |
| Radiall R222M80500 (dock cable plugs) | dock block, one per receptacle | 55 | not in catalogue | DigiKey 349 as R222M80500W, 0 as R222M80500 | Radiall only | R222M80500W: "Packaging ... Unit 'W' option" on Radiall's own TDS p.2, so MATCH (packing) |
| Preci-Dip 813-S1-012-10-016101 (no code) | A J_DOCK | 5 | not in catalogue | DigiKey 18 (JRH listing), 0 (Preci-Dip listing) | **Preci-Dip only, 18 units seen** | none adopted: another spring connector is a different height and stroke (a mismatch, and the dock gap rule of 32.18 rests on it) |
| Mill-Max 0858-0-15-20-82-14-11-0 (no code) | A J_CP1-4, J_CN1-4 | 40 | not in catalogue | DigiKey 18646, Farnell 1401 | hand-fit (HC6-SC-8) | none needed; J_PRE1's longer pin has no order code (NOT_PINNED) |
| Raspberry Pi CM5108064 | B, three per kit (bench) | 15 | not in catalogue | Farnell 0, TME 0 | owner-side purchase through Raspberry Pi resellers | CM5108064B listed by Farnell (0): suffix not decoded |
| Ground Control RockBLOCK 9704 SMA | B, bench | 5 | not in catalogue | none listed | maker only; the maker's page publishes no order code | none |
| Lime Microsystems LimeSDR Mini v2 (v2.4) | B bay, bench | 5 | not in catalogue | none listed | **grade OUTSIDE (0 to 70 C)** | section 4 |
| AsiaRF AW7915-AED | B, two per kit (bench) | 10 | not in catalogue | none listed | **grade OUTSIDE (0 or -10 to 70 C)** | section 4 |
| NiceRF SA868-V | D U2 (bench) | 5 | SA868-U only (wrong band) | none | section 2.4 | none |
| Quectel RM520NGLAA-M20-SGASA | B J_M2C2 (bench) | 5 | not in catalogue | DigiKey 0, Avnet 0 | section 2.5 | none |
| Xenarc 709GNK | face plate | 5 | not in catalogue | DigiKey 6 | thin | none |
| Mitsubishi RA30H1317M1 | face plate | 5 | not in catalogue | brokers only | Mitsubishi only; the -501 and -101 suffixes the brokers list are not decoded | none; a qualified RF review should name the suffix |
| Amphenol PolyPhaser GTH-SFF-AL | wall | per jack | not in catalogue | Pasternack 0 | maker only | none |
| Glenair 233-370 USB feed-through | wall | 5 | not in catalogue | FindChips returned unrelated parts | made to order by Glenair | none |

## 4. Grade findings that need a decision (from `GRADE-CHECK.md`)

`GRADE-CHECK.md` judges 146 identities on the boards at `53a98a71` (every coded active part and connector by its code, and every
uncoded line by footprint; three of them are copper with no component) and 19 modules, cells and wall parts. Its findings:

| Finding | Part | Evidence | What it holds | Session recommendation |
|---|---|---|---|---|
| OUTSIDE, cold; PoE rating absent | Pulse H5007NL, board B T1 | "Operating Temperature 0 C to 70 C" (`v2/vendor/pulse/pulse-h5007nl.pdf` p.1). T1's media-side centre taps carry the 802.3at feed (`POE_P` on pin 24, `POE_DRAIN` on pin 21; `gen_sch_b.py:866-869`), and the HC500.O sheet states no DC current or voltage rating for any part it lists; Microchip's Table 7-2 lists H5007NL for data only | the wall Ethernet port below 0 C, and the PoE out function at any temperature (condition 1: a part not documented for a function the design gives it is a mismatch until proven) | **HC6-SC-6: HX6096NL** (Pulse; C5339289 HX6096NL, JLCPCB 146, or the reel HX6096NLT C5359044, 323, both at 04:05:50Z). Its sheet (`v2/vendor/pulse/pulse-hx6096nl-datasheet-rev-a.pdf`, filed tonight) reads "OPERATING TEMPERATURE -40 C - +85 C", "DC CURRENT/VOLTAGE RATING 720 mA, @ 57 V (CONTINUOUS)" and "MEETS IEEE 802.3 SPECIFICATION"; its pin numbering is T1's own (chip side TCT1 1 ... TD4 11/12, media side MCT1 24 ... MX4 14/13) and its suggested land (24 x 0.76 mm on 1.27 mm, rows 12.70 mm inner and 16.51 mm outer) is the one `meshsat:Pulse_H5007NL` already draws, so no pad moves. The body grows from 17.53 x 12.20 x 5.51 to 18.16 x 12.2 x 6.60 mm (placement and stack-height input). Residual for R-PWR (the PoE PSE): Microchip's Table 7-1 asks 350 uH minimum at 8 mA; Pulse guarantees 350 uH at +25 C with 24 mA of bias and 300 uH across -40 to +85 C. The generator line (`gen_sch_b.py:869`) is board B's author's. **Withdrawn:** HX5008NL, which this page first recommended from Microchip's Table 7-2, has no PoE rating in HC500.O and needs a new land; HX5004NL has neither a PoE rating nor an OCL figure. The CND-tek HX6096NLTP-CND (C47575006) is another maker's part and is not the recommendation (HC6-SC-12) |
| OUTSIDE, cold and storage | LimeSDR Mini v2, v2.4 | "Operating Temperature 0 C to +70 C, Commercial-grade; Storage Temperature 0 C to +70 C" (`v2/vendor/limesdr/myriadrf-limesdr-mini-2-0-page-20260925.html`) | the SDR receiver below 0 C, and its storage in the kit below 0 C | open: (a) an industrial-grade USB SDR in the same bay (a part search and the bay's L7 fit are owed), (b) a carve-out in OPERATING-ENVELOPE.md, which narrows the kit and is not the session's to take, (c) warming the bay before use, which needs a heat source the design does not have. The SDR is not in D-01's core (CONOPS 2a), so this holds no core acceptance; it does hold NEED-07 for that function |
| OUTSIDE, cold | AsiaRF AW7915-AED (two) | "Temperature Operating: 0 C ~ +70 C" (`v2/vendor/wifi/asiarf-AW7915-AED_V1.pdf`); the maker's page of 26 September reads -10 C ~ +70 C | the kit-to-kit WiFi link below 0 C (or -10 C); CONOPS 2a exercises it through IOHA test A11 | open: an extended-temperature M.2 2230 E-key card with the mt76 driver the P2P mission needs (a search is owed; the socket and land do not change, so the choice can wait until before purchase without touching layout); the carve-out option is not the session's |
| AT_LIMIT, cold (no margin at -20 C) | CM5 module, Xenarc 709GNK, Wurth 692122030100 USB 3 A, SGP41 (also +55 C against 51 C of air), C&K ATP16 and ATP19 switches, Floyd Bell sounder class, SCF9550, GCT SIM8060 (one of its two sheets), Amass XT60-M, Bulgin PX0833 | `GRADE-CHECK.md` | nothing at the envelope; the -33 C qualification margin is a survive-and-recover line | none: the envelope is met; each is reported for the margin tests of TEST-PLAN E3/E4 |
| TBD, no range read | Keystone 3568 and 3034 holders, the sixteen 3 mm panel LEDs, the headset jacks, the J_PRE1 pin, commodity pin headers, the Molex 208658 HDMI receptacle (molex.com and LCSC's copy did not answer), SS14 (C51897884, no sheet), QMX, the fans, the pack cells, the CR2032 cell, the sensor modules on headers | `GRADE-CHECK.md` | NEED-07 for each; none is a mission part except the pack cells (owed by the pack pick) | the NOT_PINNED ones get a range when they get an order code |

## 5. Interface parts identified tonight (session picks)

| Id | Pick | Why | Reversal |
|---|---|---|---|
| HC6-SC-7 | IDC box headers: Wurth WR-BHD 61202621621 (2x13, JLCPCB C17586777), 61201621621 (2x8, C5364137), 61201021621 (2x5, C4355000), all -40 to +105 C, 3 A per contact; mating IDC sockets WR-BHD 61202623021, 61201623021, 61201023021 (1 A per contact, -40 to +105 C); flat cable WR-CAB 63912615521CAB, 63911615521CAB, 63911015521CAB (1.27 mm, 28 AWG, 1 A, -25 to +105 C, UL AWM 2651 105 C 300 V). Board C's SMD 2x13 header: XFCN BH254VS-26P (C48687640, LCSC parametric -40 to +105 C) | one maker for header, socket and cable, with sheets fetched from we-online.com (section 7); the ribbon's 1 A per conductor is the figure the interface capacity rows (layer 5) must be checked against | a different maker if the land comparison (below) fails; the SMD header is the weakest pick (no maker sheet read) |
| HC6-SC-8 | Mill-Max 0858-0-15-20-82-14-11-0 for J_CP1-4 and J_CN1-4 (82 spring, "12 Amp High Force" on Mill-Max's page; the 085X family is "Continuous 9 amps @ 10 C temperature rise", catalogue page 28) | the part the land was drawn for (`respin-footprints-2026-09-04.md` section 5), DigiKey 18,646 | none planned |
| HC6-SC-12 | buy only from JLCPCB/LCSC stock or franchised distributors; no broker stock | counterfeit and relabelled-revision risk, which F1 (silicon revision) makes concrete for the supervisors | none |

**Land comparisons these picks create (CMP-002's identity-and-land half, owed at layout entry):** the Wurth
WR-BHD recommended hole pattern against KiCad's `IDC-Header_2x13_P2.54mm_Vertical_NarrowPad` (and the 2x5, 2x8
lands); the XFCN drawing against `IDC-Header_2x13_P2.54mm_Vertical_SMD`; the Mill-Max 0858's ".044 in (1,118 mm)"
mounting hole for its ".040 in (1,016 mm)" tail against the land's 1.3 mm drill (`respin-footprints-2026-09-04.md`
section 5 took its hole from the strip page's 1.32 mm): a solder mount tolerates the larger hole, but the pin's
squareness then rests on the assembly fixture, which ASSEMBLY.md should say.

## 6. Session choices on this page

HC6-SC-3 (crystal), HC6-SC-6 (magnetics), HC6-SC-7 (IDC), HC6-SC-8 (Mill-Max), HC6-SC-9 (consign SCF9550 and
BQ7720700), HC6-SC-10 (SA868-V), HC6-SC-11 (RM520NGLAA-M20-SGASA) and HC6-SC-12 (sources) are the session's, taken
under the owner's standing rule of 26 September 2026 because each follows from the makers' documents and no owner
judgement is standing; each names its reversal above. HC6-SC-1, -2, -4 and -5 are on `STM32H743-COMPATIBILITY.md`.
None changes a requirement, a function or a protection; the generator lines that would carry HC6-SC-3, -6, -7 and -8
belong to the board authors and are listed in `drafts/hc6/README.md` of the worktree that wrote this page.

## 7. Documents filed tonight

| File | What | sha256/16 | Source |
|---|---|---|---|
| `v2/vendor/st/st-stm32h743xi-datasheet-rev11.pdf` | ST DS12110 Rev 11 (13 January 2026) | `f6e620179006c8c4` | Internet Archive, capture 20260827112637 (gzip body decompressed); capture 20260318060051 identical |
| `v2/vendor/st/st-rm0433-rev8.pdf` | ST RM0433 Rev 8 (January 2023), 40.7 MB | `9ba54135736a47a3` | Internet Archive, capture 20251014013150 |
| `v2/vendor/st/st-es0392-rev15.pdf` | ST ES0392 Rev 15 (September 2025) | `effe23b2b79ec4ee` | Internet Archive, capture 20260526205148 (gzip body decompressed) |
| `v2/vendor/connectors/jst-vh-catalogue.pdf` | JST VH connector catalogue (PDF of 9 January 2026) | `d51e669c597988b2` | https://www.jst-mfg.com/product/pdf/eng/eVH.pdf, 00:21Z |
| `v2/vendor/connectors/wurth-wr-bhd-box-header-61202621621.pdf`, `-61201621621.pdf`, `-61201021621.pdf` | Wurth WR-BHD box headers (dated 2026-08-30) | `38509e478ba394d0`, `0df87add7e40d43c`, `dbaa4765e57457ac` | https://www.we-online.com/components/products/datasheet/<code>.pdf, 00:20Z |
| `v2/vendor/connectors/wurth-wr-bhd-idc-socket-61202623021.pdf`, `-61201623021.pdf`, `-61201023021.pdf` | Wurth WR-BHD female IDC connectors (dated 2022-08-30) | `6f7254b5bcf6f837`, `9477ffdc02af6355`, `259dc513fa09e911` | as above |
| `v2/vendor/connectors/wurth-wr-cab-ribbon-63912615521cab.pdf`, `-63911615521cab.pdf`, `-63911015521cab.pdf` | Wurth WR-CAB flat cable (dated 2026-08-21) | `fdee657377aed9ac`, `b076f824f67b9ee7`, `4b4b78e0c17b7f1d` | as above |
| `v2/vendor/connectors/wurth-wr-com-usb3-a-692122030100.pdf` | Wurth 692122030100 USB 3.0 A (board B J_LIME's land) | `df28a01bf0fb46ac` | as above |
| `v2/vendor/connectors/millmax-0858-product-page-20260927.html` | Mill-Max 0858 product page | `7a11ec390b01e69f` | https://www.mill-max.com/products/discrete-spring-loaded-pins/spring-loaded-pin-with-standard-tail/0858, 00:12Z |
| `v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf` | Mill-Max "Rugged, High Current Spring Pins" (catalogue page 28, 2014) | `8ef40cd98d95c653` | https://www.mill-max.com/sites/default/files/external/assets/2017-12/Rugged%20Spring%20Pins.pdf, 00:13Z |
| `v2/vendor/rockblock/groundcontrol-rockblock-9704-product-page-20260927.html` | Ground Control product page | `3ee56a034ace33a7` | https://www.groundcontrol.com/product/rockblock-9704/, 00:08Z |
| `v2/vendor/rockblock/groundcontrol-docs-rockblock-9704-specification-20260927.html` | Ground Control specification page | `30bad6e0074bea49` | https://docs.groundcontrol.com/iot/rockblock-9704/specification, 00:08Z |
| `v2/vendor/crystals/yajingxin-taxm25m4rfbcct2t-spec-2026-08-26.pdf` | Yajingxin specification of the fitted 25 MHz crystal | `cf02a0872e39ea73` | LCSC's datasheet link for C164047, 00:04Z |
| `v2/vendor/crystals/yxc-ysx321sl-x322525mob4si.pdf` | YXC YSX321SL (X322525MOB4SI) | `7bc18549e407d8e3` | LCSC's datasheet link for C9006, 00:05Z |
| `v2/vendor/crystals/epson-tsx-3225-x1e0000210139.pdf` | Seiko Epson FA-238/TSX-3225 sheet | `4e9c0baa33e30d2d` | LCSC's datasheet link for C91750, 00:05Z |
| `v2/vendor/pulse/pulse-hx6096nl-datasheet-rev-a.pdf` | Pulse HX6096NL, datasheet rev. A (07/30/15), 3 sheets, raster | `76b47ba60ec87752` | https://productfinder.pulseeng.com/doc_type/WEB301/doc_num/HX6096NL/doc_part/HX6096NL.pdf, 04:05:06Z (declared in `vendor-noindex.txt`) |

The held RockBLOCK 9704 data sheet (`v2/vendor/rockblock/rb9704-datasheet-RB9704-001-JUN26.pdf`) was re-fetched from
https://www.groundcontrol.com/wp-content/uploads/2026/07/RockBLOCK-9704-Data-Sheet.pdf at 00:26Z and is byte-identical
(its currency is confirmed and its URL is now known). The Pulse sheet LCSC serves for HX5004NLT is byte-identical to the
held `pulse-h5007nl.pdf`. Three more held files came back byte-identical from their makers at 03:56Z to 03:57Z, which
records their URLs: `wifi/asiarf-AW7915-AED-datasheet.pdf` (AsiaRF's 260505 one-page sheet), `cm5/cm5-datasheet.pdf`
(datasheets.raspberrypi.com), `rf/radiall-smp-max-series-R222M-D1C004XEe.pdf` (radiall.com). Not confirmed: the Radiall
per-part data sheets and the Glenair sheets (both makers answered HTTP 403) and the Xenarc manual and drawing (served
through a script); the Internet Archive was offline at 03:57Z, so their currency stays unconfirmed. The sources.txt and vendor-status.txt lines for these files are drafts
(`drafts/hc6/vendor-lines.patch`), because both files are shared.

## 8. The power parts Layer 4 selected (Layer 6 record l6pwr, 3 October 2026)

The parts L4-E5 to L4-E11 selected exist only in release-guarded drafts (`apply_*.py` under `v2/docs/records/l4e*/`), on no
committed netlist; this section carries their procurement readings so that Layer 8 applies the drafts with the codes and stock in
view. Every figure is a public reading of 2 October 2026, 23:20 UTC (`v2/docs/records/l6pwr/inputs/lcsc-2026-10-02.json`, LCSC's
product detail; `jlc-search-2026-10-02.json`, JLCPCB's parts search), true at that time only. Need = per kit x 5. The identities,
documents, grades and findings are in `v2/docs/records/l6pwr/L6-POWER-PARTS.md` (`l6pwr_parts.out`); this page orders nothing.

| Part (code) | Board, refs | Need | LCSC stock (JLCPCB assembly) | Price USD (at qty) | Constraint | Alternative and its state |
|---|---|---|---|---|---|---|
| TI BQ25730RSNR (C5219071) | A U3 (L4-E11 draft) | 5 | **0** | 2.8553 (1), 2.7966 (10) | **no LCSC stock** (E11-32, R-162); the drawn BQ25731RSNR C2871872 reads 1125 | BQ25731RSNR, the same land: no battery FET, arrangement (A) with E11-24's bank |
| Nexperia BUK6Y10-30PX (C3278350) | A Q39, Q40 (L4-E11 draft) | 10 | 67 (67) | 2.0603 (1), 1.7386 (10) | thin; the PX suffix is not printed by the sheet (L6P-F02); the suffix-less C2846047 reads 0 | Vishay SQJ403EP: another land drawing, one FET with a case heat path: not a drop-in |
| TI TPS16630PWPR (C1849461, this reading; the draft carries none) | A U42 (L4-E11 draft) | 5 | 1141 | 2.8002 (1), 2.3521 (10) | none; R221 collides with L4-E8's ballast designators (L6P-F01) | none on the PWP land (p.36 lists TPS16630 alone in HTSSOP-20) |
| Diodes B540C-13-F (C72264) | A D23 (L4-E11 draft) | 5 | 52515 | no ladder at 1 (min buy 5) | none | B550C-13-F, the same sheet and land: VF 0.70 V |
| Milliohm HoJLR2512-3W-8mR-1% (C2904240) | A R11 (L4-E4, kept by L4-E5) | 5 | 9600 | 0.0832 (10) | the 7 mOhm fallback C2904239 reads 1830 (R-155) | WSL2512 at 8 mOhm: 1 W at 70 C against 3 W |
| Milliohm HoJLR2512-3W-12mR-1% (C2904242) | A R12 (L4-E6) | 5 | 3405 | no ladder at 1 (min buy 5) | none | as above |
| Milliohm HoJLR2512-3W-5mR-1% (C2903482) | A R227 (L4-E9); R138 (L4-E4) | 10 | 106575 | no ladder at 1 (min buy 5) | none | a WSL2512 at 5 mOhm cannot carry R227's 1.037 W fault bound at 1 W |
| Milliohm HoJLR2512-3W-45mR-1% (C2903491) | A R221 to R226 (L4-E8) | 30 | 15860 | 0.0621 (10) | the designator collision L6P-F01 | a WSL2512 at 45 mOhm fits (0.35 W) |
| Panasonic EEHZK1V331P (C278516) | A C163, C178, C179, C180, C199, C200 (drawn, kept by L4-E8) | 30 | 6246 (6246) | 0.8074 (1), 0.6449 (10) | the rated temperature rise is not printed (L4-E8 B4) | EEHZK1V331V (vibration-proof, the same row) |
| Panasonic EEHZK1V181P (C242139) | A C236 (L4-E11 draft) | 5 | 2843 | 1.1407 (1), 0.9588 (10) | none | EEHZK1V181V |
| Samsung CL10B332KB8NNNC (C1613) | A C6 (L4-E8: Cc2 3.3 nF) | 5 | 32760 | no ladder at 1 (min buy 20) | no maker page read (DOCUMENT_OWED) | any 3.3 nF 50 V X7R 0603 (the loop check judges it) |
| TI TPS48110AQDGXRQ1 (C17556513) | E U6 (L4-E11 entry), U21 (L4-E7 guard) | 10 | 326 | 4.4674 (1), 4.0004 (10) | the DGX-19 land is owed (E11-01); the guard's instance PROVISIONAL (L4-E7 round 3); the rating basis L6P-F10 | TPS48111AQDGXRQ1: no OV pin, latch-off: the guard loses its function |
| TI CSD19536KTT (C2687963) | E Q7 (L4-E11 entry) | 5 | 611 | 4.4897 (1), 3.9324 (10) | none | NOT READ (the family's SOA figures decide E11-17) |
| TI CSD19532Q5B (C473333) | E Q1 (L4-E9), Q12, Q13 (L4-E7 guard) | 15 | 2522 | 2.1572 (1), 1.8436 (10) | Q13's hot leakage: D-11 CONDITIONAL | NOT READ |
| Littelfuse SMCJ30A (C224048, this reading; the draft carries none) | E D4 (L4-E7 guard) | 5 | 15670 | 0.2982 (5), 0.2375 (50) | PROVISIONAL (the guard) | Diodes SMCJ30A-13-F C135160 (1417): another maker, condition 1 |
| Littelfuse SMCJ40CA (C80273) | E D11 (L4-E7 guard); D10 (entry, on main) | 10 | 4925 | no ladder at 1 (min buy 5) | PROVISIONAL (the guard) | SMCJ40A (unidirectional): not equivalent for D-11 |
| Samsung CL32B225KCJSNNE (C55151, this reading; the draft carries none) | E C131, C132, C135, C136 (L4-E7 guard) | 20 | **0** (4654) | 0.1599 (1), 0.1352 (10) | **no LCSC retail stock**, JLCPCB's assembly pool holds it; no temperature range on the maker's page (L6P-F08); PROVISIONAL | another maker's 2.2 uF 100 V X7R 1210, re-bounded on its own curves |
| Samsung CL32B106KBJNNNE (C138687, this reading) | E C133, C134, C71 to C74 (L4-E7 guard and backstop) | 30 | 16710 (30940) | 0.3288 (1), 0.2609 (10) | as above | as above |
| Samsung CL31B106KBHNNNE (C89632) | E C13, C14 (drawn) | 10 | **0** (109264) | no ladder at 1 (min buy 5) | **no LCSC retail stock**, JLCPCB's assembly pool holds it | as above |
| Vishay WSL2512R0700FEA (C2076144) | E R60 to R64 (L4-E7R backstop) | 25 | 1970 | 0.8059 (1), 0.6645 (10) | none | WSL2512R0700DEA (0.5 percent) halves the trip's resistor error |
| Milliohm HoLLR2512-3W-4.5mR-1% (C2985708) | E R19 (entry), R87 (guard) | 10 | 4225 | no ladder at 1 (min buy 5) | the HoLLR series sheet is not held (L6P-F09) | a HoJLR2512 4.5 mOhm code, if one exists: the held sheet would apply |
| TI INA169NA/3K (C44322) | E U18 (L4-E7R backstop) | 5 | 61868 | 1.138 (1), 0.8704 (10) | none | INA139NA/3K (40 V, the same land) |
| TI TPS3701DDCR (C132788) | E U19 (L4-E7R backstop) | 5 | 26813 | 0.6932 (1), 0.5536 (10) | none | TPS3700DDCR (18 V, the same land) |
| TI TPS3808G33DBVR (C43698) | E U20 (L4-E7R backstop) | 5 | 36030 | 0.4435 (1), 0.3466 (10) | none | TPS3808G33DBVT (the same part, small reel) |
| Samsung SDI INR18650-35E (no code) | P, the 4S3P pack (D-06) | 60 | owner-side purchase | USD 8.25 a cell (the l3batt reading, an indicator) | the qualification margins are outside every printed row (L4-E10, U-01) | the Saft MP 176065 xtd is the labelled PROPOSAL (below); a cell change is the owner's |
| Saft MP 176065 xtd (no code; PROPOSAL only) | P, a 4S1P (not adopted) | 4 | owner-side (Saft's distributors) | NZ$ 238.72 a cell (SIMPOWER listing archived 2025-01-16) | current at temperature and the storage dwell AWAITING Saft (R-168); the pocket's fit (R-167) | none (it is the alternative) |

**Readings of two stock pools.** LCSC's product detail reports LCSC's retail stock; JLCPCB's parts search reports the assembly
pool. Three Samsung ceramics read 0 at LCSC and thousands at JLCPCB on the same minute; an order for assembly is judged on JLCPCB's
figure at its time, a consigned purchase on LCSC's or a franchised distributor's.

**Codes the drafts owe (L6P-F06).** TPS16630PWPR C1849461, Littelfuse SMCJ30A C224048, CL32B225KCJSNNE C55151 and CL32B106KBJNNNE
C138687 are this record's readings for drafts that carry no LCSC code; the generator edit is Layer 8's with the draft.
**Reselected: nothing.** The findings L6P-F01 to L6P-F11 are in the record's output with the Layer 4 row each affects.
