# The external decision packet: U-01, U-02, U-04 and E11-29 made actionable (5 October 2026, 15:50 CEST)

Written by the coordinator under the owner's review of P0 checkpoint 1 (`handover/OWNER-INSTRUCTION-2026-10-05.md`, part 18) and his
instruction of 14:20 (part 15, section 5: "Identify the specimen, measured quantity, pass limit, required capability and owner; do not
claim a planned test has passed"). It reuses the records' analyses; nothing is reopened without evidence. Prototype framing: nothing is
built, bought or measured. **No purchase, outside contact or requirement change is authorised by this packet; every request stays
UNSENT.** Money figures carry their label: VERIFIED (read on the named page at the named date), INDICATOR (a distributor's figure the
record read), ESTIMATE (the coordinator's, from the named basis), NOT READ. Rates: ECB 5 October 2026, 1 EUR = 1.1225 USD = 0.85033
GBP = 2.0002 NZD. The vendors' own pages (TI, Pico, Peli, Mouser, Digikey) render prices by script and gave none to a plain GET today.

## 1. U-02, the sealed case's heat rejection (ARCHITECTURE-LEVEL; T-H1)

**The existing per-mode reconciliation** is L4-E12's section 16 (`records/l4e12/L4E12-ELECTRONICS-THERMAL.md`, 16.3 the nodes and
limits, 16.5 the margins, 16.6 what one point closes, 16.7 the procedure) and the procedure `records/l4e12/T-H1-PROCEDURE-DRAFT.md`
(section 6: pass, fail, inconclusive, and what each result decides). Its lines, each with the requirement, the component limit, the
heat path assumed and the prediction:

| Point | Requirement and governing limit (as ruled) | Heat into the case (counted once, 16.2) | Need, and pass at a reading of at least | Where the model puts it (1.22 to 2.85 W/K, the coefficient ends; a MODEL range, not a physical bound) | What T-H1 decides, and the next action on a fail |
|---|---|---|---|---|---|
| M1 (K1, K2) heat stage on the pack, +40 C, lid open | REQ-024 / E3-A; the SGP41's Table 4 +50 C as ruled (CFL-002 open); under the owner's option C, A or B the cells' hot stop H1 | 25.536 W | 2.554 W/K, pass at 2.905 (as ruled); 1.666, pass at 1.804 (under C, A, B) | as ruled: ABOVE the model's top (2.85): reachable only with the route (fins on the free strips, the loads led into the plate, the lid skin); under C, A, B: inside the range | SCREENS an uncertain route as ruled (bare reading, then the same point with the route fitted); a fail with the route fitted and a measured local temperature over the limit is the only DEMONSTRATED CONFLICT that becomes an owner requirement question |
| M2 (K1, K2, K9) heat stage on shore, +40 C | REQ-024 / E3-A; the same limits | 27.086 W | 2.709, pass at 3.081 (as ruled); 1.642, pass at 1.767 (under C, A, B) | as ruled: ABOVE the model's top; under C, A, B: inside | as M1 |
| M3, M4 lid closed (E3-L), +40 C | REQ-052 / E3-L; the SGP41's Table 4 as ruled | 25.536 / 27.086 W | 2.554 / 2.709, pass at 2.905 / 3.081 | OVER the model even with the route: a **MODELLED SHORTFALL OF THE ANALYSED ARRANGEMENT** (0.275 W/K = 2.749 W; 0.430 W/K = 4.300 W) | MEASURES a design currently predicted to miss this line; a reading under it is expected and is an engineering task (the arrangement, the hold), not new information; under C, A or B the governing line is H1 (1.804 / 1.767), inside the range |
| M5 (K6) the profile on the pack, +20 C | REQ-014; C1's +50 C inside-air trigger | 43.413 W | 1.447, pass at 1.508 | inside the range (lower half) | SCREENS; a fail puts C1's shedding inside REQ-014's profile: routes of sections 9 and 10 measured on the same point |
| M6 (K9) E3-O at +55 C | D-02a's margin; the e-paper's +60 C operating row read for storage (INFERRED) or the +70 C class | 27.086 W | 5.417, pass at 7.758 (e-paper row); 1.806, pass at 1.958 (+70 C class) | e-paper row: OVER any model (a **MISSING STORAGE QUALIFICATION**, Pervasive Displays' statement, OW-4, unsent); +70 C class: inside the range | the +70 C class is SCREENED; the e-paper line is not a heat-rejection question but a missing vendor statement |
| M7 (K10) E5's +60 C dwell under the hold | the e-paper's row (no room at the ambient) or the LimeSDR's +70 C storage row (U-02's line) | 21.587 W | none (e-paper row); 2.159, pass at 2.455 (U-02's line) | e-paper row: MISSING STORAGE QUALIFICATION (the whole 21.587 W); U-02's line: upper part of the range | SCREENS U-02's line; on a fail the record's fallbacks F4 (the plate coupling, E5 held to 1.564 W/K), F3 (the deeper hold, 1.552), both (1.125), F1 fins sized from the measured split |
| M8, M9 (K7, K8) charging on the design day | SC-37; the gauge's charge start T3 42 C and the running charge's T4 | 52.134 W | 1.810 / 2.200, pass at 1.889 / 2.315 | inside the range | SCREENS; a fail bounds the charge current on the design day (Layer 9's budget) |
| fans off at M2's heat | the failure case | 27.086 W | none (a reading) | | the coupled parts' plate at most 69.82 C on W4's still values |

**Decision check, in the owner's words.** The spend does NOT confirm a supported route anywhere that governs: no governing line lies under
the model's conservative end (only K3's 0.941 and K4's 0.620 W/K do, and they do not govern). It **SCREENS an uncertain route** on
M5, M7 (U-02's line), M8, M9 and, under CFL-002's option C, A or B, on M1 to M4. As ruled today (the SGP41's Table 4) it **MEASURES a
design predicted to miss** M1 and M2 bare (reachable only with the route) and M3 and M4 even with the route. It cannot pass the e-paper
lines (M6, M7 on that row): those are a MISSING STORAGE QUALIFICATION, a vendor statement (OW-4), not heat rejection. The one thing a
reading changes for the architecture: a measured local temperature over a mandatory limit with the route fitted makes a line a
DEMONSTRATED CONFLICT and an owner requirement question; everything else is an engineering task on the arrangement.

**The mock-up, summed (the owner's authorisation OW-8; the session cannot run it):**

| Item | Qty | Price | Label and basis |
|---|---|---|---|
| Peli 1450, current moulding | 1 | EUR 85.74 paid (75.00 + fees) | the owner's used case, bought 6 September 2026 (appendix "Case purchase"); its identity check against the 1451-931 figures on receipt still owed; a new one would be EUR 211.13 incl. VAT (READY-TO-ACT 5.2, flight-cases.eu, VERIFIED then) |
| 1450PF panel frame kit | 1 | EUR 37.08 incl. VAT (29.66 excl.) | VERIFIED in READY-TO-ACT 5.2 (flight-cases.eu listing, special price; regular 41.20); not yet bought |
| 3 mm aluminium plate blank, the C1 outline (377.2 x 263.0) | 1 | EUR 30 to 60 | ESTIMATE (a sheet-metal service, JLCCNC "from 2 days"; price NOT READ) |
| stack heaters, aluminium-housed wirewound 50 W class, 6.8 Ohm | 3 | EUR 15 to 30 | ESTIMATE (distributor class pricing; NOT READ today) |
| PA patch block, 100 W class, 2.2 Ohm | 1 | EUR 10 to 20 | ESTIMATE |
| fans, five, the picked Sanyo Denki 9WL0612P4H001 or stand-ins of the class | 5 | picked: USD 73.69 at 1 (Sager, stock 0) x 5 = USD 368 = EUR 328; stand-ins: Sunon GF60151B7-1E00U-AE9 EUR 39.79 at 1 (RS) x 5 = EUR 199 | INDICATOR (L7-FANS-AND-TH1.md row "mixers"); the Same Sky CFM-6025BG68-22 of the draft NOT READ |
| PicoLog TC-08 loggers (sixteen channels) | 2 (or 1 if one is at hand) | GBP 349 each (VERIFIED, READY-TO-ACT 5.2, VAT treatment not stated) = EUR 410 each at today's rate | the draft needs sixteen channels; READY-TO-ACT listed one, unbought |
| type K thermocouples, fine wire | 16 | EUR 80 to 160 | ESTIMATE |
| bench supply with two logged channels (heaters, fans) | 1 | assumed at hand | not costed; if absent, NOT READ |
| **Sum** | | **about EUR 1,100 to 1,250 with stand-in fans and two loggers** (EUR 700 to 850 with one logger; +EUR 130 for the picked fans); the case already paid apart | ESTIMATE, dated 5 October 2026, excluding the plate's and consumables' exact quotes and anyone's time |

Who runs it: the owner's bench, or a laboratory (cost NOT QUOTED; a quote is an outside contact, the owner's). A +60 C chamber run
only if wanted, at a laboratory (OW-8). Duration: the draft's point matrix, several hours a point (section 4).

## 2. U-04, the charger (B1) on the battery FET pair (ARCHITECTURE-LEVEL; E11-31 / R-161)

**The missing fact.** The BQ25730's sheet bounds VSYS in all three modes (D1, D3, D4) but prints neither the held pack current with
CHRG_INHIBIT set and a source present through OUR pair Q39/Q40 (with Q42) and board E on VSYS_E, nor D2's load-step response against the
2.054 V margin with OUR inductor, output capacitors and compensation. Those decide whether (B1) as composed serves the kit's modes.

**Two evidence routes that do NOT depend on the whole-kit fabrication release** (the owner's P1 point: the test must not wait for the
release it informs). Both are limited evidence builds under the constitution's section 10: their own engineering review of the exact
circuit under test, a controlled test plan, no energising of an unresolved hazardous path (the pack simulated by a bench source with a
current limit and the breaker's function stood in by the bench's limit), and the owner's purchase and execution authorisation.

| Route | Specimen | What it represents | What transfers to the final circuit | What stays layout- or part-specific (open after it) | Capability and who | Cost |
|---|---|---|---|---|---|---|
| (R1) TI's evaluation module BQ25730EVM, as sold, with its own FETs | the controller on TI's reference layout | the controller's mode behaviour: VSYS regulation in each mode (D1, D3, D4), the CHRG_INHIBIT behaviour and sequencing, the start from cold, the VSYS_MIN accuracy (A11-18) | the controller's behaviour and register settings; the piecewise mode table of E11-31 (section 15d) | the held pack current through OUR pair's body diodes and its drive (E11-29, E11-37); D2's step response with OUR inductor and capacitors (TI's parts differ); R17's sense layout; thermal | a bench with a programmable source (9 to 25 V, 100 W class), an electronic load and a 4S pack or a pack simulator; the owner's bench or a supplier's (none secured) | the module's price NOT READ (TI's page renders it by script); ESTIMATE from TI's EVM class: USD 100 to 200; the bench instruments assumed at hand |
| (R2) a controlled coupon of the drafted charger block | a small 4-layer coupon carrying exactly `apply_gen_sch_a_charger.py`'s block as drafted (the BQ25730, Q39, Q40, Q42, R17, the inductor, the capacitors, the sense and the FET drive), with test points | OUR circuit as drawn, apart from board A's planes | everything (R1) transfers plus the held pack current through our pair, D2 with our parts, R17's layout; the same coupon can carry TP-E11-29's FET fixture (section 3 below), one build for two qualifications | board A's plane resistance and thermal environment; the composed return (V6-B1) | fabrication and assembly by a board house (JLCPCB or NextPCB, five pieces) and the same bench as (R1); the coupon's design review before ordering (its own gate, not the kit's) | ESTIMATE EUR 150 to 300 for five assembled coupons, from the September 2026 JLC lines in `release/revA/order/ORDER-LOG.md` (a small 4-layer board EUR 20 to 60, assembly EUR 50 to 150, parts about EUR 40); NOT QUOTED |

**Recommendation (SESSION, within the owner's rule that purchases are his):** (R2) is the route that answers U-04's question for our
circuit; (R1) answers the controller's part sooner and cheaper and can run first on the owner's bench. Neither requires the whole-kit
release; each needs its own authorisation (OW-7's questions to TI, Q-TI-15 to Q-TI-18, stay drafted and UNSENT and would sharpen (R1)).
The pass limits are R-161's as printed (pack absent VSYS at least 12.054 V; inhibited with SRN over 12.546 V, VSRN plus 150 mV within
2 percent; under 12.054 V at least 12.054 V; between at least 11.96 V; the held pack current under the limit the record states; D2's
step within 2.054 V).

## 3. U-01, the cell (ARCHITECTURE-LEVEL; D-06's pocket) and what each evidence route proves

**Guaranteed by the maker (Saft MP 176065 xtd datasheet, Doc. 31109-2-0625, held back):** the windows (charge -30 to +85 C, discharge -40
to +85 C, storage allowable -40 to +85 C), the 2.5 V cut-off, the capacity rows. **Recommended, not guaranteed at temperature:** 11 A
continuous and 22 A pulses, which "Can vary depending on temperatures" (footnote 2). The kit needs 10 A continuous, 18 A for 60 s and
20 A for 2 s at the modelled cells, -20 to +80 C, plus the storage dwell and recovery of LO-01e to LO-01g. The ruled 35E is unsuitable on
its own published rows (LO-01d to LO-01g).

| Route | What it proves | What it does NOT prove | Decision it supports | Cost and capability |
|---|---|---|---|---|
| (a) Saft's statement (OW-9, the drafted request `records/l4e10/clarification/saft-mp176065xtd.txt`, UNSENT) | the maker's warranted envelope: current at temperature for the three points, charge below 0 C, the storage dwell and recovery, termination, the minimum capacity | the fit (the mock-up) and the pack's behaviour as built | ADOPTION of the route (OW-3) on a maker's guarantee: the cell-limit rows read MET | the owner sends the request; no money |
| (b) the limited sample qualification (L4-E10 10g): ONE cell, a chamber -40 to +85 C, a 25 A load, the kit's three current points at the modelled temperatures, the storage dwell and recovery, about two weeks | THAT specimen's behaviour at THOSE tested conditions: whether the route is excluded or not excluded at the kit's points | a maker's guarantee; pack-level behaviour (4S1P series balance, the interconnects' heat, the gauge's view of the string); production variation across cells and lots; the fit | a SCREEN: continue the Saft route's engineering (the pack design on the published windows with the screened currents) or stop it; it does not support adoption by itself | one cell NZ$ 238.72 = EUR 119 (distributor pages read 1 to 2 October); the chamber and load run NOT QUOTED (a laboratory, an outside contact, the owner's); nobody in house |
| (c) the printed mock-up of four cells in the pocket (OW-9; no purchase) | the fit of a 4S1P in D-06's pocket (58 x 160 x 48 mm under B16's overhang) | anything electrical | the fit line of U-01 | no money; the session can prepare the model, the owner prints |
| (d) the alternative HL18650V 4S3P (OW-2) | its rows only once Topwell's signed specification arrives or a lot soak (24 h at +71 C and at -33 C at 30 percent) is run | | the fallback route | about USD 42 a pack (INDICATOR, 1 October); the request drafted, UNSENT |

**What remains unproven at pack level even after (a) and (b):** the built pack's thermal coupling to the air (U-02's T-H1 and T-H2), the
string's balance and the gauge's calibration (Layer 12), the pack's own I2R at 18 A in the pocket (L4-E10's figures are MODEL). The
architecture decision (b) can support is the smallest one: whether the Saft route stays the selected candidate for the engineering that
follows; adoption needs (a) or a lot qualification, and the fit needs (c).

## 4. E11-29, the three paralleled battery FETs (a QUALIFICATION, kept apart from the architecture blockers)

TP-E11-29 (`test-procedures/TP-E11-29.md`, L4-E11 round 16) is written and NOT EXECUTABLE until L4-E9 restates R-159 and a supplier
agrees in writing to the fixture requirement: the net heat at each heating lead's joint at most 10 mW in every state (the supplier
demonstrates it by three thermocouples or a reference coupon). Targets: Zw at most 37.59 K/W, R17 at most 0.294 K/W, the pours 0.1 mOhm.
Specimen: the FET pair and Q42 on a coupon with the record's pours (route (R2) above can carry it). Capability: a supplier's or
laboratory bench with the heating leads, thermocouples and the record's method (none secured). Cost: NOT QUOTED; folded into (R2)'s
estimate if the same coupon carries both. Its fallback if the sharing fails: lower-resistance FETs or a fourth, a design change inside
UDC-1, not an architecture change.

## 5. What this packet asks of the owner, and what it does not

Asks (each an action under his authority, none a question): OW-8 (T-H1, with the sum above), OW-3 and OW-9 (the Saft route: send the
request and/or authorise the one-cell screen), OW-7 (TI's questions), the authorisation of (R1) and/or (R2) for U-04 with E11-29's
fixture on the same coupon if (R2). Does not ask: any requirement change, any change of pack, case, service or spend ceiling. The desk
work of P0-1 to P0-8 does not wait for any of it.
