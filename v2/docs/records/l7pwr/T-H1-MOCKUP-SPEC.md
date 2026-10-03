# T-H1, the empty-case conductance test: the mock-up specification and its bill (one page for the owner's purchase decision and the test's decision)

MESHSAT-1357, Layer 7 record l7pwr, 3 October 2026. **Prototype design: nothing has been bought, built, powered or measured;
no cart, no login, no quote asked.** The procedure is `records/l4e12/T-H1-PROCEDURE-DRAFT.md` as revised for L4-E12's section
17; this page adds what the owner buys to run it (the bill, every item with a public price read and dated, or NOT READ), what the
specimen is and what its result transfers, and the pass lines the coordinator judges a point by, so that the purchase and the
test's decision stand on one page. Every figure is printed by `l7pwr_fans_th1.py` in `l7pwr_fans_th1.out` (sections 5 and 6).
**Authorisation to perform** (the spend below, the bench, the people) is the owner's; **acceptance of a result** is the
coordinator's check of the filed record against L4-E12's sections 16 and 17 (the procedure's section 0): the two stay apart.

## 1. The specimen

An empty current-moulding **Peli 1450** with its **1450PF** panel frame and a **3 mm aluminium plate blank** at CASE-MARGINS C1's
outline (377.2 x 263.0 mm, the ten 4.6 mm holes at Peli's insert bores) in the face's place, on its feet on a bench in still room
air, shaded; **no boards**: resistive heaters on 3 mm aluminium blanks at the boards' outlines on the kit's standoffs, set per
point to the mode's heat **less the fans' measured draw** (P = the heaters + the fans, counted once); the **five picked fans in
their places** (three Sanyo Denki 9WPA0412P6G001 over Raspberry Pi CM5 coolers on board B's blank, two Sanyo Denki 9WL0612P4H001
mixers at the stack's ends) on their own logged supply channel; a dummy pack block (channel 16); **sixteen type K channels** on
two PicoLog TC-08 loggers, junction offsets read in an isothermal soak before each series.

**What it represents:** the sealed case's conductance between the mixed inside air and the ambient, for each heat, lid state and
fan state, with the frame, the plate and the fans as built; the plate, wall and floor fractions; the hold reference's offset
(channel 5 less channel 6).

**What transfers to the final kit:** that conductance, fully: the case, the frame, the plate and the fans are the kit's own
parts (a passing point replaces L4-E12's bound, which credits the fans' flow at zero). **What does not transfer:** the boards'
local temperatures, the cells' rise in the pocket, the junctions and the parts' local air in the built kit (T-H2, THM-001 and
U-01 keep their own evidence); lid-closed and fans-off states need their own points; the room-to-+40 C translation is a model
(L4-E12 16.4), never a validation; a sample result is evidence for this case and these fans, not a production limit.

## 2. The bill (prices read 3 October 2026; indicators at the tier named, never quotes)

| Group | Qty | Item | Unit price | Currency | Status | Source, availability or lead as printed |
|---|---|---|---|---|---|---|
| case | 1 | Peli 1450 Protector case, current moulding (CASE-MARGINS T1's identity check on receipt) | 168.90 | EUR excl. VAT (211.13 incl.) | READ | flight-cases.eu (Guardique Products A/S); "Normal in stock" |
| case | 1 | Peli 1450PF Special Application Panel Frame Kit (frame, o-ring, 10 inserts, 4 screws) | 29.66 | EUR excl. VAT (a special price; regular 32.96) | READ | flight-cases.eu; stock not shown |
| plate and blanks | 1 | 3 mm EN AW-5754 plate blank 377.2 x 263.0 (C1's outline; its holes and R16 corners are not in the shop's price) | 28.03 | EUR excl. VAT | MODELED | metaalshopper.nl, 278.07 EUR/m2 plus 0.44 per piece, over 0.0992 m2; shipped within 6 working days |
| plate and blanks | 1 | board B's blank 330 x 200 (B16's outline) | 18.79 | EUR excl. VAT | MODELED | as above, 0.0660 m2 |
| plate and blanks | 1 | board A's blank 240 x 160 | 11.12 | EUR excl. VAT | MODELED | as above, 0.0384 m2 |
| plate and blanks | 1 | board E's blank 267 x 68 | 5.49 | EUR excl. VAT | MODELED | as above, 0.0182 m2 |
| plate and blanks | 1 | board D's blank 100 x 80 | 2.66 | EUR excl. VAT | MODELED | as above, 0.0080 m2 |
| plate and blanks | 1 | board C's U, 344 x 228 outer less the 240 x 176 window (panel1450's strips) | 10.50 | EUR excl. VAT | MODELED | as above, 0.0362 m2 |
| plate and blanks | 1 | the metal shop's handling charge, once per order | 9.95 | EUR | READ | metaalshopper.nl |
| heat | 3 | Arcol HS50 6R8 J aluminium-housed wirewound resistor, 6.8 ohm 50 W (21.2 W each at 12.0 V) | 5.04 | EUR | READ | RS stock number 160922, stock 921 (the FindChips reading); Farnell 4044345 at 3.65, stock 0 |
| heat | 1 | dummy pack block: an aluminium block at the pack's outline (FEA-008's dummy pack, channel 16) | NOT READ | EUR | NOT READ | a metal shop's quote |
| fans | 2 | Sanyo Denki 9WL0612P4H001 San Ace 60W IP68, the picked mixer fan | 73.69 | USD | READ (USD) | Sager, a US distributor, stock 0 (the FindChips reading); no EU row served, an EU price NOT READ |
| fans | 3 | Sanyo Denki 9WPA0412P6G001 San Ace 40W IP68, the picked cooler fan | 58.83 | EUR | READ | RS stock number 101593, stock 51 (the FindChips reading); Farnell 4218284 at 76.83, stock 0 |
| fans | 3 | Raspberry Pi Cooler for Compute Module 5 (the passive heatsink the cooler fans sit on) | 4.49 | EUR excl. VAT (5.43 incl.) | READ | kiwi-electronics.com KW-3425; 75 in stock |
| fans | 5 | fan brackets (the cooler fans over the heatsinks, the mixers at the stack's ends): printed or bent parts | NOT READ | EUR | NOT READ | a Layer 7 CAD part to draw first |
| instruments | 2 | Pico Technology PicoLog TC-08 (8 thermocouple channels plus CJC) | 349.00 | GBP (VAT treatment not stated) | READ | picotech.com; "Currently In Stock" |
| instruments | 18 | Pico SE000 type K thermocouple, exposed tip, PTFE, 1 m (sixteen channels, two spares) | 10.50 | GBP (VAT treatment not stated) | READ | picotech.com |
| supplies | 2 | KORAD KA3005P 0 to 30 V, 0 to 5 A programmable supply with USB/RS232 logging (the heaters' and the fans' channels) | 74.79 | EUR excl. VAT (89.00 incl. 19 %; list 109.00) | READ | reichelt.com; "Available on 10/9/2026" as printed |
| consumables | 1 | thermal compound, M2.5 and M3 hardware, standoffs, JST SH 1.0 and 24 AWG leads, tape for the junctions | NOT READ | EUR | NOT READ | consumables |
| room | 1 | the ambient: still room air, shaded, 0.5 m clear around the case; an optional confirming chamber point at +40 C or +60 C | NOT READ | EUR | NOT READ | a laboratory's service only if the owner wants the chamber point |

**Totals of the prices read:** **EUR 639.76** (excl. VAT where the page states it), **GBP 887.00**, **USD 147.38**; the
currencies are not converted (no rate was read). **Four items have no read price** (the dummy pack block, the fan brackets, the
consumables, the optional chamber point) and the 60 mm fan has no EU price read. The heaters' three resistors are the
procedure's count (one, two or three give about 21, 42 and 64 W); the places table below spreads them. The readings are filed in
`inputs/prices-2026-10-03.json` and `inputs/findchips-fans-heaters-2026-10-03.json`; a broker row is not a supported source.

## 3. The points, the heaters and the pass lines (restated from the procedure; the figures L4-E12's 17.2 and 17.4)

Each point runs the fans its mode runs (the hold and the heat stage: slot 3's cooler fan and the two mixers; the profile: all
five), from their own supply channel; the heaters are set to the mode's heat less the fans' **measured** draw. The table's
settings use the model's fan draw and are recomputed from the measured one (V = sqrt(P_heater x 6.8 ohm) per heater; this
record recomputes each printed setting and they agree to 0.01 V).

| Point | Mode | Heat into the case | Heaters (model's fans) | Setting |
|---|---|---|---|---|
| M2, M6 | the heat stage on shore with the ballasts (E3-A's 2 h at +40 C; E3-O at +55 C) | 27.086 W | 25.136 W (1.950 W) | one heater at 13.07 V |
| M1 | the heat stage on the pack (E3-A's 4 h at +40 C) | 25.536 W | 23.586 W (1.950 W) | one heater at 12.66 V |
| M4 | as M2, lid closed (E3-L) | 27.086 W | 25.136 W (1.950 W) | one heater at 13.07 V |
| M3 | as M1, lid closed (E3-L) | 25.536 W | 23.586 W (1.950 W) | one heater at 12.66 V |
| M7 | E5's hold with the ballasts | 21.587 W | 19.637 W (1.950 W) | one heater at 11.56 V |
| M5 | the profile PS-IDLE-SPEC on the pack (REQ-014 at +20 C) | 43.413 W | 40.443 W (2.970 W) | two heaters at 11.73 V each |
| M8, M9 | the profile charging on the design day | 52.134 W | 49.164 W (2.970 W) | two heaters at 12.93 V each |

The heaters' places (W, plan; the fans are real): board B 14.972 / 14.972 / 12.057 / 26.234 / 26.234; board A 4.284 / 4.284 /
3.903 / 3.464 / 3.464; the front end and the charger 1.725 / none / 1.345 / none / 6.620; board C and the face 1.500 / 1.500 /
1.500 / 7.500 / 7.500; board D and the PA 1.500 / 1.500 / none / 1.500 / 1.500; board E 1.155 / 1.155 / 0.832 / 1.155 / 3.245;
the pack none / 0.174 / none / 0.590 / 0.600 (the columns M2 M4 M6; M1 M3; M7; M5; M8 M9).

**Pass per point:** the reading less its expanded uncertainty (k = 2) at or over the line's need (a reading at or over the
threshold below); **fail** under it; **inconclusive** when the endpoint (0.1 K/h drift over an hour, or a three-time-constant
fit) is not met or a supply, a fan's draw or the ambient drifts in the averaging hour. No temperature requirement is relaxed to
make a point pass. The owner's CFL-002 decides which column applies; both are recorded.

| Point (lid open, fans on unless named) | Governing line as ruled: need, pass at a reading of at least | Under CFL-002's C, A or B | Decides |
|---|---|---|---|
| M2 at 27.086 W | the SGP41's Table 4: 2.709 W/K, 3.081 W/K | the idle cells' H1: 1.642 W/K, 1.767 W/K | the heat stage on shore at +40 C (E3-A's 2 h) |
| M6 (the same point) | the e-paper unpowered (INFERRED from its operating row): 5.417 W/K, 7.758 W/K | the same | E3-O at +55 C; once PDi states a storage range at or over +70 C, the +70 C class: 1.806 W/K, 1.958 W/K |
| M1 at 25.536 W | the SGP41's Table 4: 2.554 W/K, 2.905 W/K | the cells' H1: 1.666 W/K, 1.804 W/K | the heat stage on the pack at +40 C (E3-A's 4 h) |
| M4 at 27.086 W, lid closed | 2.709 W/K, 3.081 W/K | 1.642 W/K, 1.767 W/K | E3-L on shore |
| M3 at 25.536 W, lid closed | 2.554 W/K, 2.905 W/K | 1.666 W/K, 1.804 W/K | E3-L on the pack |
| M7 at 21.587 W | the e-paper unpowered: no conductance at E5's +60 C | the same | E5 only once PDi states a storage range; then the LimeSDR's +70 C storage row: 2.159 W/K, 2.455 W/K (U-02's line) |
| M5 at 43.413 W | C1's +50 C: 1.447 W/K, 1.508 W/K | the same | the profile unshed at REQ-014's +20 C |
| M8, M9 at 52.134 W | T4 on the charging cells: 2.025 and 2.525 W/K, 2.123 and 2.677 W/K | the same | a running charge on the design day's cold and warm ends; a charge start (T3): 1.810 and 2.200 W/K, 1.889 and 2.315 W/K |
| fans off, M2's heat | none | none | the failure case: the coupled parts' plate at most 69.82 C on W4's still values |
| channel 5 less channel 6 within +-0.899099 K | | | the hold's trigger window exists with the reference where it is; otherwise the reference moves to the mixed air |

Four lines lie over the modelled outside capacity even with the combined route (L4-E12 17.9: M3 and M4 as ruled, a modelled
shortfall of the analysed arrangement; M6 and M7 on the e-paper's row, a missing storage qualification): a point there reads
the conductance and is not expected to pass those lines; the SGP41's port air and the e-paper's window temperature are logged
as channels apart from the mixed air. Where a line is reachable only with the combined route (class (ii)), a bare reading under
it is followed by the same point with the route fitted (lid open).

## 4. What the fans add to the test

The picked fans are the kit's own, so the test reads the conductance with the real fans for the first time (L4-E12's bound
credits their flow at zero): the two mixers 1.56 m3/min free air together (the model's representatives 0.60 to 1.21 m3/min), the
three cooler fans 0.38 m3/min each. Their drawn power is logged per fan where measurable (the procedure's record, section 7);
at full speed the hold's three fans draw 6.08 W against the model's 1.950 W, so the heaters' setting must follow the measured
draw, as the procedure already requires. In the kit the fans' converters (U22 on board E, the step-up per cooler on board B) add 0.72
and 0.35 W at full speed (record l7pwr section 11, round 2): the bench supply feeds the fans at 12.0 V without them, so those losses
are board heat the heaters carry when a mode's heat is restated on the picked fans. The fans' maximum operating temperature is +70 C, 1.35 K over the hold's 68.65 C
trigger on the mixed air: a point near the hold's line runs them at their printed limit.

## 5. The decision this page serves

The owner's decision is the purchase of the list above (section 2, EUR 639.76 plus GBP 887.00 plus USD 147.38 of read prices
and the four items to quote) and the authorisation of the bench (OW-8). The test's decision is section 3's lines, per point and
per CFL-002 column, through the coordinator's check of the filed record (the procedure's section 7). Neither closes U-02 by
itself: a passing point closes the conductance it reads for that configuration.
