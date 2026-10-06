# The supplier validation and remaining engineering annex: U-01, U-02, U-04 and E11-29 (5 October 2026; written 15:30 to 15:34 CEST, reframed 15:55 under the owner's amendment of 15:45, part 19; amended 6 October 2026 for the NEXT set, sections 6 to 8)

**Purpose (the owner's clarification, `handover/OWNER-INSTRUCTION-2026-10-05.md` part 19).** The project's deliverable is the most complete,
internally consistent engineering package that desk engineering, modelling, simulation and review can produce, for a RECEIVING COMPANY
to complete, physically validate and manufacture. This annex is that company's validation and remaining-engineering scope for the four
items the desk cannot close (a fifth, E11-37, added on 6 October 2026 in section 7): for each, the claim the missing fact supports, why the held evidence does not establish it, the specimen,
measured quantity and pass limit, the capability needed, the affected outputs that stay PROVISIONAL until it is known, and a labelled
cost as supporting information. **The owner is NOT asked to supply a bench, buy equipment, book a test, answer a procurement question
or authorise an experiment before the handover.** No supplier is assumed engaged; its engineering and laboratory capability remain to
be confirmed. Nothing here is a request for a requirement change, a purchase, an outside contact, fabrication or energisation. **Amendment of 6 October 2026** (branch `fnd/w3annex` from set 30's integration commit 2c, `53a68c7c`): written for the NEXT set and NOT merged into set 30's freeze; the coordinator adopts it there, re-pins and regenerates what reads this page, and fills the promoted sha where section 6 reads `__INTEGRATED__`. It adds E11-37 (section 7), states R17's design target as record l4e11 prints it, R-159's restatement, the lower-source back-feed's placement and D-06's two meanings (section 6), and keeps every line of sections 1 to 5 where it was (words are added inside lines only). It accepts nothing.

Three states are kept apart throughout: the LAYER DESK PACKAGE (editable design, analysis, internal consistency, reviews and the scoped
supplier work: complete or not within the declared scope); DESIGN AND QUALIFICATION (open defects, provisional choices, unverified
assumptions, the supplier validation still required); FABRICATION RELEASE (its own gate, BLOCKED where its criteria are unmet). An
architecture uncertainty is not erased by this framing: where a measurement could change a component, topology, arrangement or layout,
the affected outputs are named and kept provisional. A desk-fixable defect is never parked here. Prototype framing: nothing is built,
bought or measured. Money labels: VERIFIED (read on the named page at the named date), INDICATOR (a distributor's figure the record read),
ESTIMATE (the coordinator's, from the named basis), NOT READ. Rates: ECB 5 October 2026, 1 EUR = 1.1225 USD = 0.85033 GBP = 2.0002 NZD.
The vendors' own pages (TI, Pico, Peli, Mouser, Digikey) render prices by script and gave none to a plain GET today.

## 1. U-02, the sealed case's heat rejection (ARCHITECTURE-LEVEL; T-H1)

**The existing per-mode reconciliation** is L4-E12's section 16 (`records/l4e12/L4E12-ELECTRONICS-THERMAL.md`, 16.3 the nodes and
limits, 16.5 the margins, 16.6 what one point closes, 16.7 the procedure) and the procedure `records/l4e12/T-H1-PROCEDURE-DRAFT.md`
(section 6: pass, fail, inconclusive, and what each result decides). Its lines, each with the requirement, the component limit, the
heat path assumed and the prediction:

| Point | Requirement and governing limit (as ruled) | Heat into the case (counted once, 16.2) | Need, and pass at a reading of at least | Where the model puts it (1.22 to 2.85 W/K, the coefficient ends; a MODEL range, not a physical bound) | What T-H1 decides, and the next action on a fail |
|---|---|---|---|---|---|
| M1 (K1, K2) heat stage on the pack, +40 C, lid open | REQ-024 / E3-A; the SGP41's Table 4 +50 C as ruled (CFL-002 open); under the owner's option C, A or B the cells' hot stop H1 | 25.536 W | 2.554 W/K, pass at 2.905 (as ruled); 1.666, pass at 1.804 (under C, A, B) | as ruled: ABOVE the model's top (2.85): reachable only with the route (fins on the free strips, the loads led into the plate, the lid skin); under C, A, B: inside the range | SCREENS an uncertain route as ruled (bare reading, then the same point with the route fitted); a fail with the route fitted shows THAT arrangement failing under those conditions: it is rejected or revised and the remaining permitted routes (L4-E12 sections 9, 10 and 13) are assessed; a requirement question reaches the owner only when the evidence shows no permitted route holds, or as an explicit trade-off |
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
lines (M6, M7 on that row): those are a MISSING STORAGE QUALIFICATION, a vendor statement (OW-4), not heat rejection. A measured local temperature over a mandatory limit with a route fitted demonstrates that THAT arrangement fails under those conditions, nothing more: the disposition is to reject or revise the arrangement and assess the remaining permitted routes; a requirement change is put to the owner only when the evidence shows why one is necessary, or as an explicit trade-off. Modelled shortfalls, missing vendor specifications and measured failures stay three different things.

**The mock-up, summed (T-H1 is a receiving-company validation task; the owner is not asked to buy, book or run it; OW-8 stays a drafted authorisation text, not a request):**

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
| **Sum of the listed items** | | **EUR 1,191.08 to 1,326.08 with stand-in fans and two loggers** (EUR 781.08 to 916.08 with one logger; +EUR 129 with the picked Sanyo Denki fans in place of the stand-ins); the paid case apart | ESTIMATE, dated 5 October 2026 (the first sum, 1,100 to 1,250, was mis-added; corrected by the owner's review, part 19); excludes the paid case, any missing bench instrument, labour, delivery and the tax treatment where unstated. A stand-in fan changes what the run represents (its draw and flow differ from the picked fan's): a run on stand-ins is labelled so, and the fans' MEASURED draw replaces the model's share (T-H1 section 2) |

Who runs it: the receiving company's bench or laboratory (cost NOT QUOTED; its capability to be confirmed). A +60 C chamber run only if the company judges it needed (OW-8's text). Duration: the draft's point matrix, several hours a point (section 4). Until it runs, the outputs that depend on the conductance stay PROVISIONAL: L4-E12's selection (c) and the hold's trigger window, the fan duty rows (L7), the hot-stop lines of CONOPS 4c's reduced mode, and REQ-024's and REQ-052's acceptance rows.

## 2. U-04, the charger (B1) on the battery FET pair (ARCHITECTURE-LEVEL; E11-31 / R-161)

**The missing fact.** The BQ25730's sheet bounds VSYS in all three modes (D1, D3, D4) but prints neither the held pack current with
CHRG_INHIBIT set and a source present through OUR pair Q39/Q40 (with Q42) and board E on VSYS_E, nor D2's load-step response against the
2.054 V margin with OUR inductor, output capacitors and compensation. Those decide whether (B1) as composed serves the kit's modes.

**Two evidence routes that do NOT depend on the whole-kit fabrication release** (the owner's P1 point: the test must not wait for the
release it informs). Both are limited evidence builds under the constitution's section 10, for the receiving company: their own engineering review of the exact circuit under test, a controlled test plan, no energising of an unresolved hazardous path (the pack simulated by a bench source with a current limit and the breaker's function stood in by the bench's limit) and, if ever run, the applicable purchase and execution authorisation. This annex asks the owner for none of it; neither setup is certified executable by any review yet.

| Route | Specimen | What it represents | What transfers to the final circuit | What stays layout- or part-specific (open after it) | Capability and who | Cost |
|---|---|---|---|---|---|---|
| (R1) TI's evaluation module BQ25730EVM, as sold, with its own FETs | the controller on TI's reference layout | the controller's mode behaviour: VSYS regulation in each mode (D1, D3, D4), the CHRG_INHIBIT behaviour and sequencing, the start from cold, the VSYS_MIN accuracy (A11-18) | the controller's behaviour and register settings; the piecewise mode table of E11-31 (section 15d) | the held pack current through OUR pair's body diodes and its drive (E11-29, E11-37; E11-37's own row is section 7); D2's step response with OUR inductor and capacitors (TI's parts differ); R17's sense layout; thermal | a bench with a programmable source (9 to 25 V, 100 W class), an electronic load and a 4S pack or a pack simulator; the receiving company's or a nominated laboratory's bench (engagement unconfirmed; nobody in house) | the module's price NOT READ (TI's page renders it by script); ESTIMATE from TI's EVM class: USD 100 to 200; the bench instruments assumed at hand |
| (R2) a controlled coupon of the drafted charger block | a small 4-layer coupon carrying exactly `apply_gen_sch_a_charger.py`'s block as drafted (the BQ25730, Q39, Q40, Q42, R17, the inductor, the capacitors, the sense and the FET drive), with test points | OUR circuit as drawn, apart from board A's planes | everything (R1) transfers plus the held pack current through our pair, D2 with our parts, R17's layout; the same coupon can carry TP-E11-29's FET fixture (section 3 below), one build for two qualifications | board A's plane resistance and thermal environment; the composed return (V6-B1) | fabrication and assembly by a board house (JLCPCB or NextPCB, five pieces) and the same bench as (R1); the coupon's design review before ordering (its own gate, not the kit's) | ESTIMATE EUR 150 to 300 for five assembled coupons, from the September 2026 JLC lines in `release/revA/order/ORDER-LOG.md` (a small 4-layer board EUR 20 to 60, assembly EUR 50 to 150, parts about EUR 40); NOT QUOTED |

**Recommendation to the receiving company (SESSION):** (R2) answers U-04's question for our circuit; (R1) answers the controller's part sooner and cheaper and can run first. Neither requires the whole-kit fabrication release; each is a scoped validation task with its own review. OW-7's questions to TI (Q-TI-15 to Q-TI-18) stay drafted and UNSENT and would sharpen (R1). Until one runs, (B1)'s mode table (E11-31), D2's step margin and the held pack current stay PROVISIONAL in L4-E11's page and L4-E9's rows IF-10 and U-04.
The pass limits are R-161's as printed (pack absent VSYS at least 12.054 V; inhibited with SRN over 12.546 V, VSRN plus 150 mV within
2 percent; under 12.054 V at least 12.054 V; between at least 11.96 V; the held pack current under the limit the record states; D2's
step within 2.054 V).

## 3. U-01, the cell (ARCHITECTURE-LEVEL; D-06's pocket) and what each evidence route proves

**Guaranteed by the maker (Saft MP 176065 xtd datasheet, Doc. 31109-2-0625, held back):** the windows (charge -30 to +85 C, discharge -40
to +85 C, storage allowable -40 to +85 C), the 2.5 V cut-off, the capacity rows. **Recommended, not guaranteed at temperature:** 11 A
continuous and 22 A pulses, which "Can vary depending on temperatures" (footnote 2). The kit needs 10 A continuous, 18 A for 60 s and
20 A for 2 s at the modelled cells, -20 to +80 C, plus the storage dwell and recovery of LO-01e to LO-01g. The ruled 35E is unsuitable on
its own published rows (LO-01d to LO-01g). D-06 in this section is the foundation decision of the pack, not L4-E9's defect D-06 (section 6.5).

| Route | What it proves | What it does NOT prove | Decision it supports | Cost and capability |
|---|---|---|---|---|
| (a) Saft's statement (OW-9, the drafted request `records/l4e10/clarification/saft-mp176065xtd.txt`, UNSENT) | the maker's warranted envelope: current at temperature for the three points, charge below 0 C, the storage dwell and recovery, termination, the minimum capacity | the fit (the mock-up) and the pack's behaviour as built | the cell-limit rows LO-01d to g read MET for the Saft option on a maker's guarantee; ADOPTION of a 4S1P Saft pack is a SEPARATE owner decision (OW-3), not asked here | the drafted request is sent by whichever party engages Saft (the receiving company or a nominated channel; engagement unconfirmed); no money; UNSENT today |
| (b) the limited sample qualification (L4-E10 10g): ONE cell, a chamber -40 to +85 C, a 25 A load, the kit's three current points at the modelled temperatures, the storage dwell and recovery, about two weeks | THAT specimen's behaviour at THOSE tested conditions: whether the route is excluded or not excluded at the kit's points | a maker's guarantee; pack-level behaviour (4S1P series balance, the interconnects' heat, the gauge's view of the string); production variation across cells and lots; the fit | a SCREEN: continue the Saft route's engineering (the pack design on the published windows with the screened currents) or stop it; it does not support adoption by itself | one cell NZ$ 238.72 = EUR 119 (distributor pages read 1 to 2 October); the chamber and load run NOT QUOTED (a nominated laboratory or the receiving company; engagement unconfirmed); nobody in house |
| (c) the printed mock-up of four cells in the pocket (OW-9; no purchase) | the fit of a 4S1P in D-06's pocket (58 x 160 x 48 mm under B16's overhang) | anything electrical | the fit line of U-01 | no money; the session prepares the model; the receiving company prints and fits it |
| (d) the alternative HL18650V 4S3P (OW-2) | its rows only once Topwell's signed specification arrives or a lot soak (24 h at +71 C and at -33 C at 30 percent) is run | | the fallback route | about USD 42 a pack (INDICATOR, 1 October); the request drafted, UNSENT |

**Three actions, kept apart (the owner's part 19, item 4):** (1) a REQUEST FOR EVIDENCE (OW-9's drafted letter to Saft: no money, no change; UNSENT); (2) a LIMITED EXPERIMENT (route (b), the one-cell screen, a receiving-company task); (3) ADOPTION of a 4S1P Saft pack (OW-3), which changes the pack's cell and is NOT requested by this annex. The owner-approved pack baseline (the 4S pack family in D-06's pocket, as ruled on 7 September and in the foundation batch of 25 and 26 September) stands until an actual change is authorised; the handover carries the Saft option as a PROPOSAL with its evidence state. **What remains unproven at pack level even after (a) and (b):** the built pack's thermal coupling to the air (U-02's T-H1 and T-H2), the
string's balance and the gauge's calibration (Layer 12), the pack's own I2R at 18 A in the pocket (L4-E10's figures are MODEL). The
architecture decision (b) can support is the smallest one: whether the Saft route stays the selected candidate for the engineering that
follows; adoption needs (a) or a lot qualification, and the fit needs (c).

## 4. E11-29, the three paralleled battery FETs (a QUALIFICATION, kept apart from the architecture blockers)

TP-E11-29 (`test-procedures/TP-E11-29.md`, L4-E11 round 16) is written and NOT EXECUTABLE until L4-E9 restates R-159 and a supplier
agrees in writing to the fixture requirement: the net heat at each heating lead's joint at most 10 mW in every state (the supplier
demonstrates it by three thermocouples or a reference coupon). Targets: Zw at most 37.59 K/W, R17 at most 0.294 K/W, the pours 0.1 mOhm (R17's 0.294 K/W is record l4e11's three-place print of the one computed target its row E11-29 prints as 0.29 K/W, section 6.2; R-159 is restated on the set 30 candidate and the procedure stays NOT EXECUTABLE on the supplier's written agreement, section 6.3).
Specimen: the FET pair and Q42 on a coupon with the record's pours (route (R2) above can carry it). Capability: a supplier's or
laboratory bench with the heating leads, thermocouples and the record's method (none secured). Cost: NOT QUOTED; folded into (R2)'s
estimate if the same coupon carries both. Its fallback if the sharing fails: lower-resistance FETs or a fourth, a design change inside
UDC-1, not an architecture change.

## 5. What this annex asks of the owner (nothing) and what it hands to the receiving company

Asked of the owner: nothing. The drafted texts OW-3, OW-7, OW-8 and OW-9 remain in L4-E9's owner table as drafted authorisations and
letters, UNSENT and unexecuted; none is a condition of the handover. No requirement, pack, case, service or spend change is requested.

Handed to the receiving company, as its validation and remaining-engineering scope, each with specimen, quantity, pass limit and the
outputs it keeps provisional: T-H1 (section 1), U-04's route (R1) and/or (R2) with E11-29's fixture on the same coupon if (R2)
(sections 2 and 4), the Saft route's evidence (section 3: Saft's statement and/or the one-cell screen, with adoption apart), E11-37's statement or bench (section 7). Its
engineering and laboratory capability are to be confirmed; no supplier is engaged.

The desk work of P0-1 to P0-8 does not wait for any of it, and a desk-solvable defect is never moved into this annex.

## 6. Amendment of 6 October 2026: the set 30 note and four reconciliations (record text for the NEXT set)

**Status.** Written on branch `fnd/w3annex` from set 30's integration commit 2c, `53a68c7c` (on `fnd/p0pwr`), read from 03:10 CEST
on 6 October 2026, by the worker the coordinator's brief names W3. **This branch is NOT merged into set 30's freeze; it is adopted
in the next set**, where the coordinator re-pins and regenerates what reads this page and TP-E11-29 (the procedures' checker output
`test-procedures/tp_check.out` prints TP-E11-29's sha256) and writes the promoted sha where this section reads `__INTEGRATED__`.
Sections 1 to 5 keep every line where it was: each edit there adds words inside an existing line, so a citation of this annex by
line (the remaining-engineering ledger, L4-E9's page and generator, set 31's record, the DESK-gate draft) still finds its text.
Nothing here accepts, closes, verifies or promotes anything; it designs nothing, computes no figure, consumes no review and changes no
verdict. Prototype framing: nothing in the kit is built, bought, powered or measured; a MODEL figure is desk arithmetic.

**Citation form.** `[ALIAS:N]` is line N and `[ALIAS:N-M]` lines N to M of the file the alias names, as it reads in this branch's
tree (every file below is byte-identical to `53a68c7c` except TP29, which this branch edits and which is cited as it now reads; on set 31, 6 October 2026, the citations under REM, B2, P11 and OWN that later revisions of those files moved are re-cited to their lines on `fnd/int31cite`, the ledger included as it reads there). A
file on another branch is cited as text only, by commit, path and line, read with `git show` (the worker rule that a record reads its
inputs from its own tree): Slot L's DESK-gate draft `fnd/dgate` `249e9e47`, `v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.draft.md`
("DGA" below), and Slot M's ledger amendment `fnd/ledgerfix` `99bbc0c6`, `v2/docs/records/l4close/REMAINING-ENGINEERING.md` ("REM-M"
below). The module `v2/ecad/tools/tests/test_w3annex.py` holds every citation and quotation of sections 6 to 8 against these files.

| Alias | File |
|---|---|
| ANX | `v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md` (this page) |
| TP29 | `v2/docs/test-procedures/TP-E11-29.md` |
| E11 | `v2/docs/records/l4e11/l4e11_power.out` |
| E11PY | `v2/docs/records/l4e11/l4e11_power.py` |
| E11P | `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` |
| TIQ | `v2/docs/records/l4e11/clarification/TI-QUESTIONS.md` |
| P0L | `v2/docs/records/l4close/P0-POWER-LIST.md` |
| REM | `v2/docs/records/l4close/REMAINING-ENGINEERING.md` |
| CX45 | `v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md` |
| CX46 | `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md` |
| L4E9 | `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md` |
| REG | `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md` |
| SET31 | `v2/docs/records/l4e9/SET31-CHANGES.md` |
| P11 | `v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md` |
| B2 | `v2/docs/records/l4e7/B2-PRESENCE.md` |
| SOLO | `v2/docs/records/l4e7/l4e7_p0sol.out` |
| OWN | `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md` |
| OWN30 | `v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md` |

### 6.1 The set 30 note: what moved since this annex was written (dated 6 October 2026)

Sections 1 to 5 were written on 5 October 2026 between 15:30 and 16:00 CEST (commits `4f3fe604` and `b539b1b4`), before the P0
candidate's checks cx45 and cx46. Since then, on the set 30 candidate that the coordinator promotes as `__INTEGRATED__`:

- the P0 candidate was checked twice and the method ended: cx45, "P0 CANDIDATE: NOT CONFIRMED." [CX45:10]; cx46, "P0 RECHECK:
  CORRECTIONS NOT CLOSED." [CX46:10], filed as "the second negative on the method, which ends it" (the filing's head, [CX46:3]);
- the remaining-engineering ledger carries this annex's four items as HO-H to HO-K [REM:549-581] and counts "qualification 1;
  external architecture fact 3" [REM:669]; its amendment of 6 October 2026 adds E11-37 as HO-L and the back-feed's reading to HO-F
  (REM-M lines 584-636 and 522-535, text only);
- set 31 restated R-159 "from E11-29's row word for word (in its Acceptance)" [SET31:44] (section 6.3);
- the DESK-gate draft named E11-37 and the back-feed as unplaced (DGA lines 258-263, its A4.4 and A4.5) and listed K-06, K-09, K-12
  and K-23 against these two pages and their neighbours (DGA lines 316, 319, 322 and 333); sections 6.2 to 7 answer them;
- the promoted revision: `__INTEGRATED__` (the coordinator's, at adoption).

Unchanged by any of it: the four items' routes, specimens, pass limits, costs and capabilities in sections 1 to 5, and what is asked
of the owner, nothing [ANX:113].

### 6.2 R17's design target: one computed figure, two prints (K-12)

- **What the record computes.** One design target for R17's coupling into a junction: the largest coupling at which R17's line plus
  twice its propagated U stays at or under R17's limit, 1 K/W ("R17's design target: its line passes with twice its U" [E11PY:5957];
  the solve [E11PY:5967]; "R17's coupling at most 1 K/W" in the row [E11:500]).
- **How it prints it.** To three places: "R17's coupling target: at most 0.294 K/W (its line passes with twice its U)" [E11:1922]
  (`fmt(S["z17_t"], 3)`, [E11PY:6120]), "R17 at most 0.294 K/W" in round 16's selection [E11:1975] ([E11PY:6313]), and the reading on
  a coupon at the design target, "R17 0.294 K/W, U 0.353 K/W (119.9 %)" [E11:1913]. To two places: "R17's coupling at most 0.29 K/W"
  in the row E11-29 [E11:500] (`fmt(R["S26"]["z17_t"], 2)`, [E11PY:6382]), the row R-159 restates word for word [REG:255] and
  TP-E11-29 quotes [TP29:713]. 0.294 + 2 x 0.353 = 1.000 K/W, the limit (DERIVED from the printed figures).
- **The reading here.** The same computed figure at two roundings, not two targets, and neither is a pass line: R17's pass line is
  "the largest coupling plus U" at most "1 K/W" [E11P:2929], quoted by TP-E11-29 [TP29:738]. This annex's 0.294 K/W [ANX:105] and
  TP-E11-29's [TP29:207-208], [TP29:785] are the record's three-place print; the register's and the row's 0.29 K/W the same figure
  rounded. For layout the target is read as the row prints it, at most 0.29 K/W, which meets both prints (SESSION, section 8). No
  page of this branch prints the target to more places than the record does. The register's own note of the difference stands: "the
  annex and TP-E11-29 print R17's as 0.294 K/W" [REG:255].

### 6.3 R-159 restated; TP-E11-29 stays NOT EXECUTABLE (K-06)

Section 4 says the procedure "is written and NOT EXECUTABLE until L4-E9 restates R-159 and a supplier agrees in writing to the
fixture requirement" [ANX:103-104]. On the set 30 candidate set 31 restated R-159 from E11-29's row word for word [SET31:44]; the
register's cell opens "L4-E11's E11-29 row, word for word" and ends that TP-E11-29 "stays NOT EXECUTABLE until its quotation and its
check are re-taken against this restatement and a supplier agrees the fixture requirement" [REG:255]; set 31 took the same reading
("still NOT EXECUTABLE until its quotation and check are re-taken against the restatement and a supplier agrees the fixture
requirement" [SET31:80-81]). This branch re-takes the quotation: TP-E11-29 quotes the restated R-159 cell [TP29:613-666] and the
restated 5d Specimen cell [TP29:130-133], and states its first condition on them [TP29:718-724]. The check's committed output is the
coordinator's to re-take at adoption; no supplier has agreed. **The narrower statement:** TP-E11-29 stays NOT EXECUTABLE; its first
condition is met on the promoted set (`__INTEGRATED__`) once the coordinator re-takes the check there, not before; the second, a
supplier's written agreement, is not met. Set 29's per-FET 45.88 K/W still stands in L4-E9's D-14 rows, U-04's row and UDC-1's
comparison [SET31:120-122], [L4E9:1401]: those are L4-E9's to restate in the next set, not this annex's; this annex's targets are
E11-29's row's [ANX:105].

### 6.4 The lower-source back-feed: remaining engineering inside E-1, S1's row (b) its later validation (A4.5, K-23)

This annex carries no row of S1: S1 and its added row (b) are record l4e7's request P1-1 [P11:144], [P11:154-160]. Its reading here,
the narrower one, is the ledger's HO-F as amended on 6 October 2026 (REM-M lines 522-535 and section 6 item E, lines 720-727; text
only). The case: a stiff source below the stage's voltage, arriving after a withdrawal, draws the stage's charge back through Q12's
body diode; no record computes it ("Not computed here" [B2:183-186]; "not computed here" [SOLO:402]), so it neither fails nor passes. It
is REMAINING ENGINEERING inside E-1 (D-10), where cx46 places it: "D-10's E-1 retains F1-F4 and the lower-source back-feed case."
[CX46:95]. The receiving company computes it on E-1's corrected circuit as part of E-1's correction, against E-1's own requirement
that every part stays within its makers' absolute maximum ratings during the fault [P11:72] and S1's criterion for the case, "Q12's
body-diode current inside its pulsed rating" [P11:160]; **S1's row (b) is the later validation of that computation, not a substitute
for it.** Grounds, the owner's part 23: "Supplier item S1 must carry that engineering problem, rather than presenting it solely as an
unperformed validation test." [OWN:681] and "A planned measurement alone does not establish that the selected protection works."
[OWN:702]; cx46: "S1 is expressly subsequent qualification of a correction, not closure of the current circuit." [CX46:95]. This annex
does not hand it over as a validation item; the ledger hands it over as remaining engineering (HO-F), and this annex sets no limit
for it. Record l4e7's own words
("validation P1-1's S1 (row added)" [B2:183-186]; "Validation: P1-1's S1" [SOLO:403]) are not this annex's file and stand as written
(section 8).

### 6.5 D-06: two items under one identifier (K-09)

"D-06's pocket" [ANX:81] (and [ANX:96]) names the foundation decision D-06, the pack ("D-06's one 4S3P pack stands" [OWN30:33]), and
its pocket under B16 [ANX:93]. It is not L4-E9's defect D-06, the vehicle entry's interconnect [L4E9:1022], RESOLVED [L4E9:1380]. The
identifier is not renamed here (set 31 kept both [SET31:111-112]); the reading is stated in section 3 [ANX:87] so that a receiving
company does not read one for the other.

## 7. E11-37, the charger's gate drive into the three battery FETs (REMAINING ENGINEERING; the P0 list's row P0-8; added 6 October 2026)

**Class.** The P0 list files the row as "E11-37, the charger's gate drive into three FETs" [P0L:25], class 2, "missing evidence
boundable at the desk" [P0L:11]; L4-E9 reads it as "a qualification gap, not a demonstrated failure" of the battery FETs
[L4E9:1134-1135]. This annex carries it as REMAINING ENGINEERING, the ledger's reading (HO-L, REM-M lines 586-593, text only):
"E11-37 STAYS OPEN: no printed figure decides a three-device gate load against TI's 5 nF" [E11:1459], and its answer decides a design
choice, "the choice between (S1) and (S2) for the final design" [E11P:1551], rather than testing a finished one. It is NOT a
demonstrated failure (no record computes a failing case), and it is not one of the P0 list's ARCH rows (its class is 2 [P0L:25]);
on a negative answer the records' options are UDC-1's own [L4E9:1401]. It is kept apart from the four items above.

**The open case.** BATDRV, the BQ25730's battery-FET gate drive, into the three-device network Q39, Q40 and Q42 on one node (rebound
from the pair in round 9 [E11:1110-1116]): supplement entry, the ideal diode's 30 mV regulation, LDO mode at VSYS_MIN, each FET's
share of the current and each junction on the shared pour, at -20, 25 and 70 C [E11:508].

**The bound from the printed limit, and what it does not decide.** TI prints a selection rule with no drain-source voltage, "the Ciss
of P-channel MOSFET should be chosen less than 5 nF" (SLUSE65A p.92, [TIQ:74]). Nexperia prints the BUK6Y10-30P's Ciss as a TYPICAL
only, "2.36 nF at -15 V (Table 7), no maximum" [E11:942]: the three are 7.08 nF typical at -15 V and about 8.61 nF near 0 V, "1.416
and 1.722 times TI's 5 nF" [E11:1111]. From printed maxima: QG(tot) at most 64 nC each, 192 nC for the three [TIQ:100-102];
RBATDRV_ON at most 6 kOhm and RBATDRV_OFF at most 2.1 kOhm [E11:944], so BATDRV's time constants into the three are 42.48 us on at
-15 V, 51.66 us on near 0 V and 18.08 us off (MAKER, INFERRED) [E11:1112]; the charge inhibit's Q49 moves at most 192 nC and BATDRV
sinks at most 3.83 mA while it holds [E11:1450-1451]. Not bounded by any printed figure: what TI's 5 nF protects, and so whether the
three's gate load is inside it [E11:1459].

**The vendor question, drafted and UNSENT.** Q-TI-17 [TIQ:74-78], extended to three devices [TIQ:96-110] and given (e) and (f) in
round 11 [TIQ:112-125]: "Nothing here has been sent, and no answer is assumed." [TIQ:3-4], and "an answer stated as a limit settles
the row for production, a typical figure does not" [TIQ:6-7]. The P0 list: "TI's answer Q-TI-17, UNSENT (vendor)" [P0L:25]; section
2 keeps OW-7's questions "drafted and UNSENT" [ANX:76].

**The receiving company's task: specimen, measured quantity and pass limit** (one of the two routes the records state, [E11:508],
[REG:279]). (a) TI's statement of what the 5 nF bounds for three P-channel FETs on one BATDRV, stated as a limit [TIQ:6-7]; or (b)
the bench of block E11-37 [E11P:1673-1690]: specimen "TI's BQ25730 evaluation hardware modified as drafted, or the controlled first
prototype of board A" [E11P:1677], at -20, 25 and 70 C ambient [E11P:1680], each drain's current read within 2 % and each junction
recorded [E11P:1683-1687]; pass "supplement entry, the 30 mV ideal-diode regulation without oscillation, LDO mode inside its printed
band" [E11P:1455]; "a result with the pair does not transfer to the three, nor the three's to the pair." [E11P:1688-1689].
Capability: the evaluation hardware or the first prototype, a chamber for -20 and 70 C, probes of at least 100 MHz bandwidth
[E11P:1687]; none secured, no supplier engaged. Cost: NOT QUOTED; route (R1)'s evaluation module (section 2), modified as
drafted, is that specimen's base, its price NOT READ.

**On a negative answer (the engineer's choice and its draft).** "the pair, its bar 20.39 K/W measured on the coupon, Q42 removed (a
draft then owed)" [E11:1462-1463], or (S2), one BUK6Y10-30P with a heat path through the case [L4E9:1401]; the pair is under 5 nF only
on a typical figure, "CONDITIONAL, Q-TI-17 (e)" [E11:1440], so that fallback also rests on TI's answer. Both are UDC-1's own options
[L4E9:1401]; with the pair, TP-E11-29 runs with two gates against the fallback line [TP29:839-840].

**Outputs kept PROVISIONAL or OPEN until it is answered.** D-14, "CONDITIONAL on E11-29, E11-30 and E11-36 with E11-37 OPEN"
[L4E9:1134]; UDC-1's selection (S1), reversed by "a negative Ciss answer or bench (R-183)" [L4E9:1401]; R-183, OWED [REG:279]; E-1's
installed acceptance (i)(a), reversed by "a negative answer to Q-TI-17 (E11-37): then (ii), a draft owed" [E11P:2416]; the charger
draft's release (E11-27) [E11P:1455]; the three's production conformance, which "needs one of them (record l9stk's C3)"
[E11P:1885-1886]; route (R1) of section 2, after which E11-37 stays open [ANX:73]. Not affected by the count: IF-1's hold and DD-7's
inhibit [E11:1450-1451]. State on this tip: "E11-37 OPEN (TI or the bench)" [E11:1465]. Nothing here is bought, sent or measured.

## 8. What this amendment leaves to other files, and its SESSION decisions

**The DESK-gate draft's K items whose file is not one of these two pages** (DGA lines 311-338; untouched here, each its owner's):
K-01, K-02, K-05, K-07, K-10, K-11, K-19, K-25 and K-27 (no stumble on the candidate, by DGA's own column); K-03 (LH-12 in
`LAYER5-HANDOVER.md`); K-04 and K-15 (the P0 list); K-08 (E-1's two meanings, L4-E9's page and register, record l4e7); K-13 (record
l4e7's request P1-1); K-14 (record l8p's one release); K-16 (record efuse); K-17 (the ledger's item C); K-18 (cx45 as filed); K-20,
K-21 and K-26 (records l9t5 and l8r2); K-22 (cx46 and record l9t5, no state changes); K-23's record l4e7 side ([B2:183-186], [SOLO:403],
[P11:154-160]; this page's side is section 6.4); K-06's L4-E9 side (set 29's 45.88 K/W per FET in D-14's rows, U-04's row and UDC-1's
comparison, [SET31:120-122]); K-24 (record l4e7 and the change-list draft); K-28 (the connected output and
L4-E9's pins). K-06, K-09 and K-12 are answered on these pages (sections 6.3, 6.5 and 6.2).

**SESSION decisions** (under the owner's standing rule of 26 September 2026; each with its reason and its reversal):

1. **The brief's "S1 row (b) of the annex" read as a placement statement.** This annex never carried S1; the narrowest change that
   makes it consistent with HO-F is section 6.4, which places the back-feed and leaves record l4e7's text to its owner. Reversed by:
   the coordinator moving S1 into this annex.
2. **R17's target for layout read as the row prints it, 0.29 K/W.** Reason: the lower print meets both, so it claims less. Reversed
   by: record l4e11 printing one figure.
3. **E11-37 carried as REMAINING ENGINEERING, the ledger's class**, with the P0 list's class 2 and L4-E9's "qualification gap" quoted
   beside it. Reason: the narrower claim about the design (no three-device network treated as finished and awaiting a test). Reversed
   by: TI's answer stated as a limit that admits the three, or the coordinator's P0 list classing the row otherwise.
4. **TP-E11-29's quotes of R-159 and of 5d's Specimen re-taken here**, and the stale fixture anchor in `test_test_procedures.py`
   moved onto the re-taken quote with its basis. Reason: set 31 names the re-take as owed [SET31:80-81], [REG:255], and the page is
   this branch's. Reversed by: a further restatement of R-159, which re-takes them again.
5. **Sections 1 to 5 edited inside their lines only.** Reason: other records cite this page by line. Reversed by: the coordinator
   re-flowing the page at adoption and re-pinning those citations.
