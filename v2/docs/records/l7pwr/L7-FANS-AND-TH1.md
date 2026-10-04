# L7: the five IP68 fans (D-18, E11-35), the T-H1 mock-up bill and the dock lead's pulse capability (MESHSAT-1357, 3 October 2026)

Layer 7 record l7pwr, written by the Layer 7 author on branch `fnd/l7pwr` from the integration candidate `fnd/l4e9` at `2c240414`
under the owner's instruction of 2 October 2026 (continue autonomously; give physical verification a practical route; prepare
vendor questions and engineer briefs ready for action; buy nothing, send nothing). **Prototype design, desk arithmetic: nothing
has been bought, built, powered or measured.** Every figure below is printed by `l7pwr_fans_th1.py` in `l7pwr_fans_th1.out`
(its section in brackets); a maker's printed figure is MAKER, this record's arithmetic MODELED, a stated assumption ASSUMPTION, a
figure carried from a sibling document INFERRED, a figure no document prints NOT READ, never a guess. This record edits no L4
record, no generator, no CAD, not `pcb_interfaces.yaml` or `HW-FW-CONTRACT.md`: what those need is a FINDING naming its row
(section 5). Layer 6 (`records/l6pwr`, not in this base) integrates the fans' identity rows written here (section 2e).

## In short

- **The fans (D-18 settled, authority SESSION).** Mixers, board E `J_FAN1`/`J_FAN2`: **Sanyo Denki 9WL0612P4H001** (San Ace 60W, 60 x
  60 x 25, IP68, 12 V, 10.8 to 13.2 V, 0.17 A, 2.04 W, 27.5 CFM, 97 Pa, -20 to +70 C, 180,000 h at 60 C, pulse sensor and PWM).
  Coolers, board B `J_FAN1..3` over the three CM5 coolers: **Sanyo Denki 9WPA0412P6G001** (San Ace 40W, 40 x 40 x 20, IP68, 12 V,
  10.8 to 13.2 V, 0.17 A, 2.0 W, 13.4 CFM, 210 Pa, -20 to +70 C, 40,000 h at 60 C, pulse sensor and PWM). Alternatives: Sunon
  GF60151B7-1E00U-AE9 (prints -10 C, no tachometer) and Sunon GF40282B3-1000U-SEP (24 V, 28 mm thick, range and life not read).
- **No fan of any maker read prints a range covering VSYS_E's 9.494 to 17.375 V** (every 12 V class stops at 13.2 or 13.8 V, every
  24 V class starts at 21.6 V), and **no 5 V IP68 40 mm fan exists** in the lines read: both sites need a **regulated 12.0 V fan
  feed** (board E from VSYS_E; board B a per-slot step-up or a 12 V from board A), FINDINGS for the Layer 8 generator owners,
  with the J_FAN headers 4-wire (12 V, GND, PWM, TACH) in place of board E's low-side chopping.
- **Downstream (round 2, set 28 F-14; section 11):** restated on the DRAFTED rails, parsed from L4-E11 section 18 and record l8r2:
  the mixers on U22's +12V_FAN draw 0.2524 A each from VSYS_E at the floor (9.508 V, U22 at the draft's 0.85), U22 0.5208 A with
  both and its quiescent; VSYS_E's total **1.3208 A** at full speed, as L4-E11 declares on the dock, 89.8 % of U42's least limit; the
  hold's fans with their converters' losses **7.50 W** against the model's 1.950 W (+0.555 W/K on E5's line if run flat out; the
  controls' duty decides, R-150; T-H1 logs the fans' own draw). D-18's settlement and the T-H1 bill hold.
- **The CM5 cooler is a passive heatsink** (Raspberry Pi's product brief, 56 x 41 x 12.7 mm, USD 5): the "cooler fan" is a fan
  added over it; the pick fits inside the cooler's 41 mm width at Y 48 to 88 and clears the backer's underside by 2.76 mm on the
  cooler's own height (0.32 mm on panel1450's 21.0 mm envelope): a Layer 7 CAD finding, with the brackets and the mixers' sites.
- **T-H1's mock-up:** the complete bill, every price read 3 October 2026 and dated: **EUR 639.76** excl. VAT, **GBP 887.00**,
  **USD 147.38**, four items with no read price (the dummy pack block, the fan brackets, consumables, an optional chamber point)
  and no EU price for the 60 mm fan; the specimen statement and the pass lines on one page (`T-H1-MOCKUP-SPEC.md`).
- **The dock lead** (60 mm of 24 AWG): the hard short's 566 A for 4.5 us is 2.14 % of the wire's fusing current from 70 C (26457
  A by Onderdonk's relation), 1/2186 of its fusing I2t, an adiabatic rise of 0.214 K; the eFuse's retry setting 1.802 A is 53 % of
  ECSS-Q-ST-30-11C Rev.2 Annex C's 3.4 A single-wire rating (the rms of the duty 46 %). The wiring is not the branch's limiting
  element; **the 813 contact's pulse capability is printed nowhere** and is the drafted question to Preci-Dip
  (`clarification/preci-dip-813.txt`, nothing sent) and E11-38's bench item.

## 1. The task, the rules read, and what this record does not do

The brief: the three Layer 7 items of L4-E9's prototype qualification route (section 5d: T-H1's row "price not read ... the fans:
nothing to buy until D-18 names them"; E11-35's row "the fans themselves, once named"; E11-38's row "one Preci-Dip 813 contact and
24 AWG", send list "none"). Read first: the owner's instruction of 2 October 2026, CLAUDE.md's sections 2, 4c and 5 (the rulings:
no vent anywhere and five IP68 internal fans, appendix 32.53; the Peli 1450 at any cost; engineering decisions are the session's,
21 September 2026; never ask the owner, 26 September 2026), and the workers' rules. The acceptance the fans answer is REQ-043
(`pcb_requirements.yaml`): "each of the five fans is one its maker rates IP68 in the maker's own datasheet, filed under
v2/vendor/fans/ with the pick, with a published operating range covering -20 C to the inside-air bar part_temps.py computes from
pcb_envelope.yaml; the part is D-18's (a 40 mm IP68 fan that fits the coolers); a fan without that rating is a change of this
statement, recorded as such" [1]. D-18 is the foundation batch's one conditional item: "it arises only if Delta's 40 mm IP68 fan
does not fit the coolers; if it does, the session settles it under the owner's standing rule of 26 September 2026 and records the
option it takes" (CONOPS section 7, ARCHITECTURE 8.2, W4-F9). It arises (section 2c), and this record settles it.

Not done here, by the brief: no edit of a generator, a registry, an interface sheet, the firmware contract or a CAD file; no
purchase, no contact, no requirement change. The circuit changes the picks force are findings for the Layer 8 owners (section 5);
the fit items are findings for v2/cad's owner.

## 2. The fans

### 2a. The sites as drawn [1]

- **Mixers, board E** (`gen_sch_e.py`): `J_FAN1`, `J_FAN2`, 3 pins (1 CELL_F, 2 FANn_SW, 3 FANn_TACH), "12 V class fan on the pack
  node, low-side PWM, tachometer": the low side chopped by Q9/Q10 (2N7002) from U10's FAN1_PWM/FAN2_PWM (RP2040 GPIO8, 9), the
  tach pulled to +3V3_E6 by 10k into GPIO10, 11, SS14 flybacks D7/D8, 0.1 A declared each. L4-E11's draft
  `apply_gen_sch_e_aux.py` (not applied) moves pin 1 and the diodes to **VSYS_E**, board A's VSYS over the dock's pin 1 behind the
  eFuse U42: **9.494 V** at U42's least limit at the supplement floor, **17.375 V** with the charge held (L4-E11 17a); the start
  limits **0.3356 A each** (both together) and **0.5713 A** (one at a time, the other at 0.1 A) under U42's least limit 1.471 A
  with U12's 0.8 A; E11-39 staggers the starts with a PWM ramp (R-188).
- **Coolers, board B** (`gen_sch_b.py`): `J_FAN1..3`, JST-SH 1.0 4 pins (1 +5V_Sn, 2 GND, 3 FAN_TACHOn, 4 FAN_PWMn; code C160390)
  to the module's Fan_Tacho (1.8k pull-up to CM5_3.3V) and Fan_PWM (open drain) pins (CM5 datasheet 2.11), 0.1 A declared on the
  slot's 5.1 V rail.
- **The air the fans must cover:** REQ-043's -20 C floor; the board air at the margin 62.1 C (L4-E12); the hold's trigger 68.65 C
  of mixed air, the fans running in E5 (L4-E12 keeps them on; with the fans stopped E5's air is 72.38 to 85.36 C).

### 2b. The candidates, row by row (MAKER unless marked) [2]

At most three candidates per site were compared, from the makers' own documents: Sanyo Denki's product-database pages
(transcribed with each page's sha256 in `v2/vendor/fans/sanyo-denki-splash-proof-fan-pages-2026-10-03.md`), Sunon's IP56/68/GR487
brochure 239-E (filed) with the catalogue 240-A extract, and Same Sky's CFM-60BG68 series sheet (filed). Sanyo Denki's own site
refused this host (HTTP 403), its product database did not; Delta's 40 mm IP68 part numbers are served by script and did not
reach this host (open-picks.txt said the same on 11 September); the maker named by distributors as a lower-power 40 mm IP68 Sanyo
model (9WP0412H6001) answers HTTP 404 on the maker's database and is not a candidate.

| Model | Maker | Size (mm) | V | Range (V) | A | W | rpm | CFM | Pa | dB(A) | Temp (C) | Life (h) | IP | Lines |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 9WL0612P4H001 | Sanyo Denki | 60 x 60 x 25, aluminium | 12 | 10.8 to 13.2 | 0.17 | 2.04 | 6150 | 27.5 | 97 | 36 | -20 to +70 | 180,000 at 60 C | IP68 | pulse sensor, PWM (4 wires) |
| 9WL0612P4J001 | Sanyo Denki | 60 x 60 x 25, aluminium | 12 | 10.8 to 13.2 | 0.39 | 4.68 | 8650 | 38.8 | 182 | 47 | -20 to +70 | 180,000 at 60 C | IP68 | pulse sensor, PWM |
| GF60151B7-1E00U-AE9 | Sunon | 60 x 60 x 15, 2-ball | 12 | 4.5 to 13.8 (INFERRED, the B6 sheet) | 0.08 | 0.96 | 3900 | 18.2 | 32 (MODELED from 0.13 inch-H2O) | 29.8 | -10 to +70 (INFERRED) | 70,000 at 40 C (INFERRED) | IP68 | two leads: no tach, no PWM |
| CFM-6025BG68-135-253-22 | Same Sky | 60 x 60 x 25, ball | 12 | 10.8 to 13.2 | 0.09 max (0.06 typ) | 0.86 max (0.72 typ) | 3500 | 14.7 | 37 (MODELED) | 25.3 | -10 to +70 | 70,000 at 40 C | IP68 | tach and PWM; soft start |
| 9WL0624P4H001 | Sanyo Denki | 60 x 60 x 25, aluminium | 24 | 21.6 to 26.4 | 0.08 | 1.92 | 6150 | 27.5 | 97 | 36 | -20 to +70 | 180,000 at 60 C | IP68 | pulse sensor, PWM |
| 9WPA0412P6G001 | Sanyo Denki | 40 x 40 x 20, plastic, ribbed | 12 | 10.8 to 13.2 | 0.17 | 2.0 | 13700 | 13.4 | 210 | 44 | -20 to +70 | 40,000 at 60 C | IP68 | pulse sensor, PWM (4 wires) |
| GF40282B3-1000U-SEP | Sunon | 40 x 40 x 28, 2-ball | 24 | NOT READ | NOT READ | NOT READ | 10500 | 14.7 | 182 (MODELED) | 46.8 | NOT READ | NOT READ | IP68 | not printed |
| 9WPA0424P6G001 | Sanyo Denki | 40 x 40 x 20, plastic, ribbed | 24 | 21.6 to 26.4 | 0.09 | 2.0 | 13700 | 13.4 | 210 | 44 | -20 to +70 | 40,000 at 60 C | IP68 | pulse sensor, PWM |

**Starting current: no maker prints one** (NOT READ); Same Sky prints a soft start on all models and a 7 V typical starting
voltage; Sunon prints a 4.5 V starting voltage. Every maximum operating temperature read is +70 C, 1.35 K over the hold's 68.65 C
trigger on the mixed air. The GF60151 family's range, temperature and life come from Sunon's GF60151B6 specification for
approval as a distributor hosts it (`inputs/sunon-gf60151b6-spec-reading-2026-10-03.md`, not filed: not the maker's site), INFERRED
for the B7.

### 2c. The judgement [2]

| Model | Site, supply as drawn | Range covers it | -20 to 62.1 C | 68.65 C | IP68 | Tach | PWM | Life at 60 C | I on the supply at the floor behind the drafted 12 V converter, full speed (A, MODELED; round 2: the drafts' 0.85 at 9.508 V and 5.0 V) |
|---|---|---|---|---|---|---|---|---|---|
| 9WL0612P4H001 | mixer, 9.494 to 17.375 V | NO | yes | yes | yes | yes | yes | yes | 0.252 |
| 9WL0612P4J001 | mixer | NO | yes | yes | yes | yes | yes | yes | 0.579 |
| 9WL0624P4H001 | mixer | NO | yes | yes | yes | yes | yes | yes | 0.238 |
| GF60151B7-1E00U-AE9 | mixer | NO | NO (-10 C) | yes | yes | NO | NO | NO (40 C) | 0.119 |
| CFM-6025BG68-135-253-22 | mixer | NO | NO (-10 C) | yes | yes | yes | yes | NO (40 C) | 0.106 |
| 9WPA0412P6G001 | cooler, 5.1 V | NO | yes | yes | yes | yes | yes | yes | 0.500 (a step-up from +5V_Sn) |
| 9WPA0424P6G001 | cooler, 5.1 V | NO | yes | yes | yes | yes | yes | yes | 0.500 |
| GF40282B3-1000U-SEP | cooler, 5.1 V | NOT READ | NOT READ | NOT READ | yes | NO | NO | NO | NOT READ |

Two findings decide the shape of the pick before any candidate:
1. **No candidate's printed operating range covers VSYS_E's 9.494 to 17.375 V.** The 12 V class stops at 13.2 V (Sanyo Denki,
   Same Sky) or 13.8 V (Sunon); the 24 V class starts at 21.6 V. VSYS_E runs 12.054 to 17.375 V in service (over every 12 V range
   most of the time) and down to 9.494 V at the floor. `gen_sch_e.py`'s "12 V class fan on the pack node" was never inside a
   printed range: CELL_F is 12 to 16.8 V. **The mixers therefore need a regulated 12.0 V rail on board E** (section 5, F-L7-01).
2. **No 5 V IP68 40 mm fan exists in the lines read**: Sunon's IP68 GF series is 12 and 24 V (the 40 mm models 24 V only); Sanyo
   Denki's 40 mm splash-proof models are 12 and 24 V; Same Sky starts at 60 mm; Delta's are NOT READ. **The cooler fans cannot run
   from the slot's 5.1 V as drawn: they need a 12 V feed on board B** (F-L7-02). REQ-043's "a 40 mm IP68 fan that fits the
   coolers" is kept; its supply is what changes.

### 2d. The selection (authority: SESSION) [2]

| Site | Selected | Why | Alternative |
|---|---|---|---|
| mixers (2), board E | **Sanyo Denki 9WL0612P4H001** | the only 60 mm IP68 candidate that prints REQ-043's -20 C AND a life at 60 C (180,000 h) AND a tachometer (FW-E07/V-E07's stalled-fan report within 5 s) AND a PWM input; the lowest-power model of its family (2.04 W at full speed against the plan's 0.72 W per mixer; the controls' duty decides the running power); 27.5 CFM free air against the model's representatives 10.6 to 21.3 CFM. Price indicator USD 73.69 at 1 (Sager, a US distributor, stock 0); an EU price NOT READ | **Sunon GF60151B7-1E00U-AE9**: 12 V, 4.5 to 13.8 V, 0.96 W, 18.2 CFM, 2-ball, IP68, EUR 39.79 at 1 (RS, stock 73); it prints -10 C (fails REQ-043's floor: taking it would be a change of the statement, recorded openly) and has no tachometer or PWM lead. Same Sky's CFM-6025BG68-135-253-22 (0.72 W typical, tach and PWM) also prints -10 C |
| coolers (3), board B | **Sanyo Denki 9WPA0412P6G001** | the only 40 mm IP68 fan whose maker's page this host reached; it prints -20 C, 40,000 h at 60 C, a pulse sensor and a PWM input for the module's Fan_Tacho and Fan_PWM; 13.4 CFM free air against the representative MF30060V2's 3.7 CFM; its 2.0 W at full speed is 3.5 times the plan's 0.57 W per cooler fan (the module's PWM duty decides). Price indicator EUR 58.83 at 1 (RS, stock 51; Farnell 76.83, stock 0) | **Sunon GF40282B3-1000U-SEP**: 24 V IP68 40 x 40 x 28, 14.7 CFM, 46.8 dB(A), USD 16.40 at 1 (Sager, stock 0): its range, temperature and life NOT READ (brochure row only), a 24 V feed, and 28 mm thick where the pick's 20 mm already leaves 2.76 mm (section 2g) |

**Authority fields.** `authority: SESSION`. `authority_why`: D-18 is written as a conditional the session settles when it arises
(CONOPS 7, the standing rule of 26 September 2026); the pick spends no money (nothing is bought), changes no claim (the IP68
statement is kept, no vent is opened), protects no line of `reserved.json`, and leaves one residual risk a measurement in this
tree removes (the start current, E11-35's bench row); the engineering test of 21 September 2026 leaves it the session's.
`ruled_by`: the Layer 7 author (session l7pwr). `ruled_on`: 2026-10-03. `reversed_by`: a fan whose maker prints a range covering
the site's supply as drawn, -20 C and a life at or over 60 C; or the owner changing REQ-043's IP68 statement openly. The registry
entry (a session choice in `pcb_requirements.yaml`'s `session_choices`, the integrator's file; no id is assigned here) is proposed
in section 5 (F-L7-09).

### 2e. The identity rows for Layer 6 (`records/l6pwr` integrates them)

| Field | mixer | cooler fan |
|---|---|---|
| MPN | 9WL0612P4H001 | 9WPA0412P6G001 |
| maker, family | Sanyo Denki, San Ace 60W Splash Proof Fan | Sanyo Denki, San Ace 40W Splash Proof Fan (9WPA type) |
| package | 60 x 60 x 25 mm, aluminium frame, 120 g, four leads (12 V, GND, pulse sensor, PWM); the hole pattern NOT READ (CAD behind a form; the 60 mm class standard is 50.0 mm on 4.3 mm holes) | 40 x 40 x 20 mm, plastic frame, ribbed, 47 g, four leads; the hole pattern NOT READ (the 40 mm class standard is 32.0 mm on 4.3 mm holes) |
| document, revision | the maker's product-database page as served 3 October 2026 (sha256 of the HTML ec42c4a8744d8a2b...), transcribed in `v2/vendor/fans/sanyo-denki-splash-proof-fan-pages-2026-10-03.md`; the instruction manual M0011876C is behind a download form, NOT READ | the page as served 3 October 2026 (sha256 90a9c2d2fc1f7457...), the same file; manual M0011876C NOT READ |
| grade against the envelope and the margins | operating -20 to +70 C: INSIDE the envelope (-20 to +40 C) and the +55 C margin; the hold's 68.65 C mixed air 1.35 K under the limit; storage temperature NOT READ | the same |
| life | 180,000 h at 60 C (215,000 at 40 C), the maker's expected life | 40,000 h at 60 C (70,000 at 40 C) |
| price and availability (indicators) | USD 73.69 at 1, Sager, stock 0 (FindChips, 3 October 2026 00:27 UTC); no EU row | EUR 58.83 at 1, RS 101593, stock 51; Farnell 4218284 EUR 76.83, stock 0 (the same reading) |
| what is owed | the starting current (bench, E11-35); the PWM input level and the hole pattern (the manual); an EU price | the same, plus the fit (section 2g) |

Filed with the pick under `v2/vendor/fans/` as REQ-043 asks (the transcription; the pages are served by script), registered in
`v2/vendor/sources.txt` and `v2/vendor/SOURCES.yaml` (`documents_filed_l7pwr`), and in `PROCUREMENT.md` section 8.

### 2f. What the picks change downstream [3]

MODELED on the makers' full-speed figures. **Round 2 (set 28 F-14):** the rows below are restated on the drafted rails, read
from the drafts and L4-E11's output (round 1 had typed a 0.90 converter at 9.494 V); section 11 lists every figure that moved.

| Item | Change | For |
|---|---|---|
| the mixers' feed | a regulated **12.0 V rail on board E from VSYS_E** (the fans' range 10.8 to 13.2 V; VSYS_E 9.494 to 17.375 V); `J_FAN1`/`J_FAN2` become **4-wire** (12 V, GND, PWM, TACH): the low-side chopping of Q9/Q10 and the SS14 flybacks D7/D8 are retired, the FETs re-used as open-drain PWM drivers (the fan's PWM input level NOT READ), the tach stays on its 10k pull-up. With the fans on a switched low side as drawn, the tachometer's open-collector return would ride the switched node: the 4-wire fan removes that | Layer 8, board E's generator owner (F-L7-01); R-177/E11-33; the register's R-179 |
| the mixers' current on VSYS_E at the floor behind U22 | as drafted (L4-E11 section 18): U22 LTC3115-1 from VSYS_E to +12V_FAN at 11.512 to 12.431 V, its loads J_FAN1 and J_FAN2 at 0.17 A each, efficiency 0.85 (L4-E11's ASSUMPTION); at the floor 9.508 V **0.2524 A per mixer** at full speed (the fan's 2.04 W), **U22's input 0.5208 A** with both and its 16 mA quiescent, as L4-E11 prints; the plan's 1.44 W for both: 0.1942 A. The start: with the other mixer and U12 running, U42's least limit leaves 3.26 W at the rail, 1.60 times a fan's running power (L4-E11: 1.6); the start current is NOT READ, so E11-35's bench row stands; 17a's per-fan limits on VSYS_E are superseded by the rail | E11-35 / R-179 (the bench) |
| the dock feed's current (E11-35) and U42's setting | VSYS_E's drafted loads U12 0.8 A and U22 0.52 A, declared 1.32 A (parsed from the draft): **1.3208 A at full speed**, equal to L4-E11's declaration on IF-AE-DOCK, 89.8 % of U42's least limit 1.4713 A, 0.1505 A in hand; at the plan's duty 0.9942 A; one 813 contact at 37.7 % of 3.5 A. Round 1's finding (1.277 A over a 1.0 A declaration) is closed by the draft | L4-E11's rows R-177 and R-181 (F-L7-04, closed in draft) |
| the coolers' feed | as drafted by record l8r2 (`apply_gen_sch_b_fans12.py`): a per-slot TPS61089 step-up from +5V_Sn to 11.51 to 12.43 V behind a TPS259631 eFuse, the slot's load row 0.69 A at 5.0 V (2.8 W of fan over 0.80, record l8r2's round 6 envelope; 0.47 A in round 2), so 0.70 W lost per running fan; the header stays JST SH in that draft (record l7r2 F-R2-08 asks JST PH) | Layer 8 board B (F-L7-02, drafted) |
| the firmware stagger (E11-39, R-188) | kept: the PWM ramp now drives the fan's PWM input, not a chopped supply; a 4-wire fan's own soft start is NOT READ for Sanyo Denki (Same Sky prints one) | the firmware owner (F-L7-05) |
| the heat into the case | at full speed, every converter's loss counted: the hold's fans **7.50 W** (slot 3's cooler 2.0 and its step-up's 0.70, the two mixers 4.08 and U22's 0.72 from L4-E11 18a) against the model's 1.950 W (+5.55 W; E5's line +0.555 W/K at L4-E12's 0.100 W/K per W); the profile's five fans with their converters 12.90 W against 2.970 W (set 29, on record l8r2's round 6 row; the sums' basis is finding F-L7-12). The controls set the duty (R-150); T-H1 runs the fans from a 12.0 V bench supply, so the converters' losses are board heat its heaters carry | L4-E12 / the Layer 4 coordinator (F-L7-06); R-150 |
| the airflow the picks deliver (free air, MAKER) | the two mixers 1.56 m3/min together (the representatives GF60151B9 to B6: 0.60 to 1.21 m3/min), the three cooler fans 0.38 m3/min each; over the case's free air of about 0.0101 m3 (MODELED, the boards not subtracted) the mixers' free-air flow is 2.6 case volumes a second, an upper bound (the delivered flow sits on the fan curve under its 97 Pa maximum; no system curve is held). L4-E12's bound credits the flow at zero; T-H1's reading with these fans replaces the credit | T-H1 (R-104); L4-E12 |
| the layout footprint | board E: the 12 V rail's parts (a TPS62933-class buck, its inductor and capacitors) and two 4-pin headers in place of the 3-pin `J_FAN` with Q9/Q10, D7/D8 and R44 to R47 re-purposed; board B: three step-ups (or a 12 V entry) beside `J_FAN1..3` | Layer 8 (the generators), Layer 10 (the layout) |

### 2g. Mounting (the case records) [4]

- **The CM5 cooler is passive.** Raspberry Pi's Cooler for Compute Module 5 is a heatsink, 56 x 41 x 12.7 mm, four M2.5 x 8 screws
  from below the carrier through the module's holes (product brief RP-008184-DS-1, December 2024, filed; list price USD 5, in
  production until at least January 2036). ASSEMBLY.md's "the coolers clipped on with their fan leads" and panel1450.py's 30 x 30 x
  30 fan envelope describe a fan the maker does not supply: the "cooler fan" is a fan added over the cooler.
- **The pick's place:** 40 x 40 x 20 flat over the fins at the cooler's north end, X -92.5 to -52.5 on slot 1 (the cooler's -93 to
  -52: inside its 41 mm width), Y 48 to 88 (north of the monitor's edge at Y +45.745 by 2.255 mm, as panel1450 places the fan
  envelope, up to the backer's top strip at Y 88).
- **Z:** board B's top 50.60; module and receptacle 5.86; the cooler 12.7; the fan 20: top at **89.16** (on the cooler's own
  height) or **91.60** (on panel1450's 21.0 mm heatsink envelope); the backer's underside 91.92 (face 106.52, plate 3.0, standoffs
  10.0, backer 1.6): **clearance 2.76 mm** (cooler height) or **0.32 mm** (envelope) where the backer's strip reaches; the plate's
  underside 103.52 (14.36 mm) over the open window. Which applies depends on the fan's Y against STRIP_T's inner edge at Y 88 and
  on what hangs under the plate in the window there: a Layer 7 CAD item, not settled here.
- **Owed to v2/cad (F-L7-03):** the fan envelope in `panel1450.py`'s B16_TALL (40 x 40 x 20 at Y 48 to 88 in place of 30 x 30 x 30
  at Y 48 to 78), the Z check above, a bracket to the cooler's M2.5 screws or the module's standoffs (the fan's hole pattern NOT
  READ: the 40 mm class standard is 32.0 mm on 4.3 mm holes), the mixers' sites "at the stack's ends" (ASSEMBLY.md section 4;
  CASE-MARGINS section 7 lists their positions as owed) with the 60 x 60 x 25 frame, and the harness of ten fan leads.

## 3. The T-H1 mock-up [5, 6]

`T-H1-MOCKUP-SPEC.md` is the one page: the specimen (an empty current-moulding Peli 1450 with the 1450PF frame and the 3 mm
plate blank; heaters on blanks at the boards' outlines set to each mode's heat less the fans' measured draw; the five picked fans
in their places on their own logged supply; sixteen type K channels on two TC-08 loggers), what transfers (the case's conductance
by heat, lid state and fan state, fully; not the boards' local temperatures), the bill and the pass lines. The bill, every price
read 3 October 2026 (indicators, never quotes): the case EUR 168.90 and the frame 29.66 excl. VAT (flight-cases.eu, in stock); the
plate blank 28.03 and five board blanks 48.56 plus 9.95 handling (metaalshopper.nl, 3 mm EN AW-5754 at 278.07 EUR/m2, MODELED per
piece, 6 working days); three Arcol HS50 6R8 J heaters at 5.04 (RS, stock 921); two 9WL0612P4H001 at USD 73.69 (Sager, stock 0; no
EU price read); three 9WPA0412P6G001 at 58.83 (RS, stock 51); three Raspberry Pi CM5 coolers at 4.49 (Kiwi Electronics, 75 in
stock); two PicoLog TC-08 at GBP 349 and eighteen SE000 type K at GBP 10.50 (picotech.com, in stock); two KORAD KA3005P supplies
at 74.79 excl. VAT (reichelt.com, "Available on 10/9/2026"). **Totals of the prices read: EUR 639.76, GBP 887.00, USD 147.38**
(not converted); **no read price:** the dummy pack block, the fan brackets, the consumables, the optional chamber point. The
heater settings of the draft (13.07, 12.66, 11.56, 11.73 and 12.93 V) are recomputed here as sqrt(P_heater x 6.8 ohm) and agree
to 0.01 V; the pass lines per point and per CFL-002 column are restated from the draft's section 6.

What the picks change in the draft (F-L7-07): the stand-in "Same Sky CFM-6025BG68, 12 V, the -22 variant" becomes the picked
Sanyo Denki fans; the fans run from a 12.0 V bench channel; the model's fan draw (1.950 and 2.970 W) is replaced by the measured
one, as the draft already requires; the fans' maximum operating temperature +70 C is 1.35 K over the hold's trigger.

## 4. The dock contact and wiring pulse capability (E11-38) [7]

**The lead:** 60 mm of 24 AWG from board E's `J_BLK` to the dock block's land (ASSEMBLY.md section 4): copper d = 0.5106 mm (the
AWG definition), 0.2047 mm2 = 404.0 circular mils; ECSS-Q-ST-30-11C Rev.2 Table C-1: 105 mOhm/m at 20 C.

**The pulse (L4-E11 17a case (2)):** at most 566 A for at most 4.5 us, 1.441 A2s. Onderdonk's relation in its general form, I =
A sqrt(log10(1 + (Tm - Ta)/(234 + Ta)) / (33 t)) with A in circular mils and t in seconds (the public note's form; it reproduces
the note's worked example at 177.8 A against 178 printed; this record uses 234 + Ta, the conservative spelling, 26457 against
30675 A at 70 C with the note's own 234 - Ta): the 24 AWG's fusing current at 4.5 us is **27865 A from 25 C, 26457 A from 70 C,
26018 A from 85 C** (the spring's limit). The short's 566 A is **2.14 %** of the 70 C figure and its I2t **1/2186** of the wire's
3150 A2s to melt at that time; the adiabatic rise of the copper from the pulse is **0.214 K** (ECSS's resistance per metre over
copper's 385 J/kgK and 8960 kg/m3, textbook constants). Onderdonk's relation is stated as accurate to about 10 s (its source); at
4.5 us the adiabatic assumption it rests on is the physical case.

**The retry duty (cases (3) and (4)):** at most 1.802 A for at most 1.5 s, then off at least 0.5 s, a duty of at most 0.75:
1.802 A is **53 %** of ECSS Annex C's **3.4 A** single-wire rating of AWG 24 (a 70 C environment, a 150 C wire, radiation alone, in
vacuum: the conservative side of the kit's sealed air), the duty's rms 1.561 A is 46 %; Preece's steady fusing current of the
bare wire 29.2 A. **The continuous draw (round 2):** 1.3208 A declared by L4-E11 18b and recomputed here (39 %). The 50 K
rule of ECSS 6.32.4a (the wire's surface 50 C under the maker's maximum rating) cannot be applied: the harness wire's maker and
rating are not named in ASSEMBLY.md (24 AWG only), a Layer 7 harness item (F-L7-08).

**So the wiring is not the branch's limiting element** on these published relations; what is printed nowhere is the **813
contact's** capability under the pulse (the piston-to-barrel interface, the gold plating, whether the spring carries current) and
under the retry duty at 85 C: Preci-Dip's SLC catalogue (filed, the maker's site) prints "OPERATING CURRENT Max. 3.5 A" and
"CONTACT RESISTANCE 10 mOhm (static measurement, halfway position)" for the 813 solder-tail series and "Max. 3.5 A / 7A peak" with
no duration for its surface-mount series only. **The question is drafted** at `clarification/preci-dip-813.txt` (five questions:
the single-pulse peak or I2t at about 5 us and the failure mode, the repetitive duty at 85 C and the 3.5 A's temperature validity,
the resistance criterion and whether 10 mOhm is a maximum, the spring's share of the current, the S1 plating specification),
**nothing sent**; L4-E9 5d's E11-38 row "What to send: none" now has this draft (F-L7-10). E11-38's bench rows stand.

## 5. Findings for other layers (each names its row; nothing is edited here)

| Id | For | Finding |
|---|---|---|
| F-L7-01 | Layer 8, board E's generator owner (R-177/E11-33, R-179) | DRAFTED by L4-E11 section 18 (U22 LTC3115-1, +12V_FAN, four-pin headers; set 28 integrates it): the mixers need a regulated 12.0 V rail from VSYS_E (a TPS62933-class buck as board A's VHEAT, or equivalent) and 4-wire `J_FAN1`/`J_FAN2` (12 V, GND, PWM, TACH); Q9/Q10 as open-drain PWM drivers (the fan's PWM input level NOT READ), D7/D8 retired, the tach pull-up kept; VSYS_E's declared loads become U12 0.8 A plus the fans at their full-speed draw (0.239 A each at the floor) or a firmware-bound duty |
| F-L7-02 | Layer 8, board B's generator owner (the `J_FAN1..3` rows; the slot rail comments) and Layer 5 (the bay harness) | DRAFTED by record l8r2 (a per-slot TPS61089 step-up and eFuse): the cooler fans need 12.0 V: a per-slot step-up from +5V_Sn (0.436 A each at full speed; an empty slot stays off) or a 12 V feed from board A over the bay harness; the header's pin 1 becomes 12 V; the slot budget's 0.1 A fan row becomes 2.0 W at 12 V per slot at full speed |
| F-L7-03 | Layer 7 CAD (v2/cad's owner; panel1450.py B16_TALL; CASE-MARGINS section 7; ASSEMBLY.md) | the CM5 cooler is passive (its brief filed); the fan envelope 40 x 40 x 20 at Y 48 to 88 replaces 30 x 30 x 30 at Y 48 to 78; the Z clearance to the backer 2.76 mm (0.32 mm on the 21.0 envelope) to resolve against STRIP_T and what hangs under the plate; a bracket to the cooler's M2.5 screws or the standoffs; the mixers' sites at the stack's ends (60 x 60 x 25); ASSEMBLY.md's "clipped on with their fan leads" to restate |
| F-L7-04 | L4-E11 (R-177, R-181) and the Layer 4 coordinator | CLOSED in draft (round 2): VSYS_E is declared 1.32 A (U12 0.8 + U22 0.52), 1.3208 A at full speed; as first written: VSYS_E's total 1.277 A at full speed exceeds the declared 1.0 A by 0.277 A (86.8 % of U42's least limit 1.471 A); the eFuse's setting and the "fans' start with no limiting" row of E11-38 are to be judged at the fans' real draw; the dock feed's declared value moves to 1.277 A (36.5 % of the 813's 3.5 A) |
| F-L7-05 | the firmware owner (R-188, FW-E07) | the stagger and ramp drive a PWM input, not a chopped supply; the tachometer report (V-E07's 5 s) now has a pulse sensor on every fan; the fans' maximum +70 C is 1.35 K over the hold's trigger: the hold's fan duty is a setting to write |
| F-L7-06 | L4-E12 / the Layer 4 coordinator (R-150, R-142) | set 29: with the converters' losses 7.50 W in the hold, 12.90 W in the profile (round 2: 7.15 and 11.85 W, before record l8r2's round 6 envelope; the sums' basis is F-L7-12); as first written: the picked fans' full-speed power (6.08 W in the hold, 10.08 W in the profile) against the model's 1.950 and 2.970 W: the line moves 0.100 W/K per W unless the controls' duty holds the plan's figures; the fans' flow (1.56 m3/min free air for the mixers) replaces the bound's zero credit only through T-H1's reading; R-142's "operating range reaching the mixed air at the line (70.0 C in E5) with margin" is met with 0 K of margin at +70 C and 1.35 K at the hold's trigger |
| F-L7-07 | L4-E12's owner (T-H1-PROCEDURE-DRAFT.md section 1), the TEST-PLAN owner (R-151) | the stand-in Same Sky fans become the picked Sanyo Denki fans on a 12.0 V bench channel; `T-H1-MOCKUP-SPEC.md` is the bill and specimen page to cite; L4-E9 5d's T-H1 row "price not read" now reads EUR 639.76, GBP 887.00, USD 147.38 with four items to quote |
| F-L7-08 | Layer 7 harness (ASSEMBLY.md section 4) | the dock's twelve 24 AWG signal wires have no maker or temperature rating named; ECSS 6.32.4a's 50 K rule and the insulation's rating at 85 C body temperature wait on it |
| F-L7-09 | the integrator (`pcb_requirements.yaml` session choices; `OWNER-DECISIONS-OPEN.md`; CONOPS section 7's D-18 row) | D-18 settled by the session: proposed text "D-18, the IP68 fans: the session takes Sanyo Denki 9WL0612P4H001 (mixers) and 9WPA0412P6G001 (coolers), both IP68, -20 to +70 C, with pulse sensor and PWM; no fan of any maker read covers VSYS_E's or the slot rail's voltage as drawn, so both sites take a regulated 12.0 V feed (Layer 8); authority SESSION under the standing rule of 26 September 2026, record l7pwr; reversed by a fan printing a covering range, -20 C and a life at or over 60 C, or by an open change of REQ-043" |
| F-L7-10 | L4-E9's record (section 5d, the send list; E11-38's row) | the Preci-Dip draft `records/l7pwr/clarification/preci-dip-813.txt` joins the send list (the owner chooses the channel); E11-38's "What to send: none" becomes this draft |
| F-L7-11 | Layer 6 (records/l6pwr) | the identity rows of section 2e; the starting current, the PWM input level and the hole patterns NOT READ (the maker's manual M0011876C is behind a form: a maker request, or the bench); an EU price for the 60 mm fan |
| F-L7-12 | this record's next round, with L4-E12 (R-150) | set 29: the cooler chain's heat is summed on two bases (the fan at the maker's rated 2.0 W, the step-up's loss on record l8r2's bounded 2.75 W envelope): 2.70 W a fan, against 2.50 W on the rated basis and 3.45 W on the bounded one; the hold's 7.50 W and the profile's 12.90 W carry that mix. One basis per use is owed: the plan's duty on the rated figure, the bound on the envelope |

## 6. The Layer 7 criteria moved (v2/docs/handover/LAYER-STATUS.md, the integrator's page; proposed cell texts)

| Item | Was (at H2) | Proposed now | Why |
|---|---|---|---|
| 7.8 thermal interfaces specified | PARTLY: "the PA flange sensor drawn on D; the fans unsettled (D-18); the conductance (EQ-05)" | PARTLY: "the PA flange sensor drawn on D; the five IP68 fans picked (D-18 settled by the session, record l7pwr: Sanyo Denki 9WL0612P4H001 and 9WPA0412P6G001), their 12.0 V feed a Layer 8 finding, their mounting a CAD item; the conductance (EQ-05) waits on T-H1" | the fans are settled with their maker's figures; the thermal interface itself (the conductance) is still unmeasured |
| 7.9 critical fit uncertainties resolved by suitable evidence | OPEN: "FEA-007: the mock-up (L-07, EQ-08) and the desk items" | OPEN: "FEA-007: the mock-up (L-07, EQ-08) and the desk items; the empty-case T-H1 mock-up is specified with its bill (records/l7pwr/T-H1-MOCKUP-SPEC.md), the owner's purchase decision now has prices; a new fit item: the cooler fan's 2.76 mm (0.32 mm) to the backer" | a specification with a bill is not evidence; the fan adds a fit item |
| 7.10 later physical checks allocated, deferral justified | PARTLY: "FEA-007 stages the YES rows at layout entry on the decision they move; FEA-004's heat-test staging stays in CONTINUATION-BRIEF 5.1's misplacements" | PARTLY: "...; the heat test T-H1 is allocated to the prototype bench with its specimen, bill, pass lines and the owner's authorisation named (records/l7pwr, l4e12)" | the allocation is complete for T-H1; the other checks as before |
| 7.5 connector, cable and service access | PARTLY: "the connector plate (C3) drawn; the jumper plug (M17g, M17x) and the sealed RJ45 open" | PARTLY: "...; the dock lead's pulse and duty capability bounded on published relations (records/l7pwr section 4), its wire's maker rating owed; the 813 contact's capability a drafted maker question" | a bound on the lead, a question on the contact |

## 7. Decisions taken by the session (authority: SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026)

| Decision | Why the session's | Reversed by |
|---|---|---|
| D-18 settled: Sanyo Denki 9WL0612P4H001 (mixers) and 9WPA0412P6G001 (coolers) | section 2d's authority fields: the conditional item's own text, no money, no claim change, a residual risk the bench removes | a fan printing a covering range, -20 C and a life at or over 60 C; an open change of REQ-043 |
| both sites take a regulated 12.0 V fan feed rather than a fan on the raw supply | no fan of any maker read prints a range covering VSYS_E or the slot rail; a fan outside its printed range would be a guess | a maker's fan with a printed range that covers the supply as drawn |
| the maker's figures are judged at full speed; the plan's lower figures are a duty the controls set | a maker prints the rated point; the duty is firmware, logged by T-H1 | the picked fans' power read at the duty on the bench (R-150) |
| the Sunon GF60151B6 specification is READ from a distributor's copy and not filed | this record's rule: held documents from the maker's site only; the figures are needed for the alternative | Sunon's own copy, fetched and filed |
| the bill is computed per currency without conversion | no exchange rate was read; a converted total would carry an unread figure | a rate read and dated |
| the plate and the blanks are priced from a per-m2 page | the shop prices by area; the piece price is arithmetic, labelled MODELED | the shop's quote for the cut pieces |
| Onderdonk's relation is taken with 234 + Ta | the smaller fusing current; the note's own spelling is reproduced beside it | a wire maker's pulse rating |
| the dock lead is bounded on ECSS Annex C's vacuum rating | the published conservative side for the kit's sealed air; a space standard reported as such | the harness wire's own rating once named |

## 8. Assumptions

- A 12 V converter's efficiency 0.90 (both the step-down on board E and the step-up on board B): round 1 only; round 2 reads the drafts' own 0.85 (L4-E11's and record l8r2's ASSUMPTION).
- Copper's specific heat 385 J/kgK and density 8960 kg/m3 (the adiabatic rise); the melting point 1083 C (the fusing note's).
- The case's free air about 0.0101 m3 (the base's 375 x 261 at Z 15.3 to the plate's underside at 103.52, the boards not subtracted).
- The fans' hole patterns at the 40 mm and 60 mm classes' standard (32.0 and 50.0 mm on 4.3 mm holes), NOT READ from the maker.
- The 24 AWG's conductor diameter from the AWG definition (0.5106 mm), not from the harness wire's own sheet (not named).
- Sunon's GF60151B7 carries its family's range, temperature and life (INFERRED from the B6 sheet).

## 9. Files

`L7-FANS-AND-TH1.md` (this page); `T-H1-MOCKUP-SPEC.md`; `l7pwr_fans_th1.py` and `.out`; `inputs/` (the price and aggregator
readings, the Sunon reading, the ECSS transcription, the fusing sources); `clarification/preci-dip-813.txt`; the makers' documents
under `v2/vendor/fans/`, `v2/vendor/cm5/` and `v2/vendor/precidip/` with their `sources.txt` lines and the `SOURCES.yaml` block
`documents_filed_l7pwr`; `PROCUREMENT.md` section 8; the test `v2/ecad/tools/tests/test_l7pwr.py`.

## 10. Not claimed

Nothing here is built, bought, powered or measured. The fans are selected on their makers' printed rows; their starting current,
PWM input level and hole patterns are not read; the case's conductance with them is T-H1's reading, not this record's. The
software test establishes this record's own arithmetic and text, not any property of a fan, a case or a contact.

## 11. Round 2: the budget on the drafted rails (set 28 finding F-14, 3 October 2026)

Set 28's integration found this record refusing: it had grepped `apply_gen_sch_e_aux.py` for VSYS_E's loads as L4-E11 first drafted
them (`U12 0.8, J_FAN1 0.1, J_FAN2 0.1`), and L4-E11 section 18 then rewrote the auxiliary domain: the mixers moved onto **+12V_FAN**,
a U22 LTC3115-1 buck-boost from VSYS_E (four-pin headers, VSYS_E's loads `U12 0.8, U22 0.52`, declared 1.32 A; +12V_FAN's loads the
two mixers at 0.17 A, efficiency 0.85), with section 18b declaring 1.3208 A on the dock. This round (branch `fnd/l7pwr2` from set 28's
`5515ecc0`) **parses** the draft with Python's `ast` (the module's string constants, then every `_intent.rail` call in them), reads
L4-E11's printed figures of 18a and 18b from `l4e11_power.out`, reads record l8r2's cooler step-up row from its draft, and restates
every figure that rested on them. The round-1 figures are parsed from this record's output at `2087060b` (in this branch's history).

| Figure | Round 1 | Round 2 | Why |
|---|---|---|---|
| a mixer's input current on VSYS_E at the floor, full speed | 0.239 A | **0.2524 A** | the draft's 0.85 at 9.508 V for round 1's typed 0.90 at 9.494 V |
| both mixers (U22's input) | 0.477 A | **0.5208 A** | the same, and U22's 16 mA quiescent; equal to L4-E11's printed figure |
| VSYS_E's total with U12 at full speed | 1.277 A | **1.3208 A** | equal to L4-E11's declaration; the draft declares 1.32 A |
| against U42's least limit | 86.8 % | **89.8 %** | 0.1505 A in hand (L4-E11: 0.1504) |
| VSYS_E at the plan's duty | 0.969 A | **0.9942 A** | as L4-E11 |
| the dock contact's share of 3.5 A | 36.5 % | **37.7 %** | as L4-E11 |
| the hold's fans' heat at full speed | 6.08 W | **7.15 W** | U22's 0.72 W (L4-E11 18a) and the cooler step-up's 0.35 W (record l8r2) counted |
| E5's line shift at full speed | +0.413 W/K | **+0.520 W/K** | from the heat |
| the profile's five fans' heat | 10.08 W | **11.85 W** | the converters' losses |
| a cooler fan's slot current | 0.436 A | **0.47 A** | record l8r2's row (0.85 at 5.0 V) |
| the dock lead's continuous draw against ECSS's 3.4 A | 38 % | **39 %** | the declared 1.3208 A |

**At set 29 (4 October 2026; the coordinator's integration correction, finding F-L7-12).** Record l8r2's round 6 restated the
coolers' feed (the slot's load row 0.69 A at 5.0 V: the fan's bounded 2.75 W envelope over 0.80), and this record's script reads
that row from the tree. Four figures of the table above moved again: the hold's fans' heat **7.50 W** (round 2: 7.15), E5's line
shift **+0.555 W/K** (+0.520), the profile's five fans' heat **12.90 W** (11.85) and a cooler fan's slot current **0.69 A** (0.47);
the step-up's loss per running fan is 0.70 W (0.35). The other rows stand. The two heat sums now mix two bases: the fan's own
power stays the maker's rated 2.0 W while the step-up's loss is taken on the bounded envelope, 2.70 W a cooler chain, against
2.50 W on the rated basis alone and 3.45 W on the bounded one. Which basis each use takes is this record's next round's to state
(F-L7-12).

**Unchanged:** the fan picks and every maker row; the mounting and the fit finding; the T-H1 bill (EUR 639.76, GBP 887.00, USD
147.38, four items to quote: no item rests on VSYS_E's loads), its heater settings and pass lines; the dock lead's pulse figures.

**D-18 holds.** The drafted rails sit inside the picked fans' printed 10.8 to 13.2 V: U22's output 11.512 to 12.431 V (L4-E11 18a) and
the coolers' step-up 11.51 to 12.43 V (record l8r2); the draft's +12V_FAN loads are the picked mixer's printed 0.17 A each. Round 1's
F-L7-01 and F-L7-02 are drafted by those records and F-L7-04 is closed in draft. **The T-H1 bill holds**; what the rails add for the
test is a note: T-H1 runs the fans from a 12.0 V bench supply, so U22's and the step-ups' losses (0.72 and 0.70 W at full speed) are
board heat that the heaters carry when a mode's heat is restated on the picked fans (R-150, F-L7-06).

Not claimed: the converters' efficiency is the drafts' ASSUMPTION (0.85 for U22, 0.80 for the coolers' step-up since record l8r2's round 6), not a maker's curve at these points; nothing is measured.

