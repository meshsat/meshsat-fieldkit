# L4-E10: the cell and thermal design of the battery path against the temperature requirements (FEA-008)

MESHSAT-1357, layer 4 task L4-E10, 2 October 2026. **Prototype design, desk arithmetic: nothing has been bought, built,
powered or measured, and no kit has been field deployed.** Every figure comes from `l4e10_cell_thermal.out` (the script
`l4e10_cell_thermal.py` beside this page reproduces it byte for byte) and carries its class: MAKER (a maker's
specification, clause named), MODELED (the tree's power and thermal model, `records/rv-pwr/pwr_budget.py` and
`records/hc2/pwr_red2.py`, imported unchanged and reproduced first), INFERRED (method stated), ASSUMPTION (a figure no
held document gives), CONDITIONAL (holds only on a stated condition). The work follows the owner's refinement of
2 October 2026: a feasibility screen of every condition first, the cells compared alongside the thermal measures, the
simplest defensible solution selected, and where none qualifies the exact conflict and at most three options.

## 1. The answer in short

- **No collision in use on the design record's conductance; one at the independent bound's worst corner (LO-01a).** At
  +40 C, lid closed, in the heat stage, the cells on the pack reach 63.29 C at the lowest conductance in the record
  (Layer 3's 62.12 C inside air plus the cells' own I2R, a 3.29 K gap; Layer 3 printed the 2.12 K on the air). It
  closes once the measured lid-closed conductance with fans is at least **1.246 W/K** (on an input 1.164 W/K); below
  that, a pocket coupling measure brings the worst corner to 58.64 C. **CONDITIONAL on T-H1 and E3-L.**
- **Storage inside the envelope (LO-01h) is met by Ver. 1.1 of the present cell's sheet; CONDITIONAL on the lot bought
  following that revision** (Version 1.0 misses it by 20 K and 2 K).
- **The four qualification-margin rows LO-01d (+55 C operation, 4 h), LO-01e (E5's +60 C humid dwell), LO-01f (+71 C
  storage, 24 h) and LO-01g (-33 C storage, 24 h) cannot be closed with the pack fitted on any held evidence.** Thermal
  design is rejected for all four by the screen (three have the ambient itself at or past the cells' limit and two of
  those have no power at all), no 18650 maker's specification held covers them, and board P's chemical fuse F2 leaves
  its own -20 to +60 C range at every one of them. This is the conflict of section 7, put to the owner with three options.
- **Selected: S1, the Samsung INR18650-35E as ruled (D-06), no spend.** The current-revision Samsung INR18650-30Q is not
  recommended (it moves no margin row on its own sheet, misses LO-01h's year and costs 11.9 % of the energy); the one
  lead that reaches the four margin rows, a wide-temperature HL18650V, rests on a product page and needs a new fuse.
- **FEA-008 cannot close now.** It closes on: T-H1's lid-closed conductance (or the coupling measure) with E3-L and
  E3-H for LO-01a; the lot's revision for LO-01h; and the owner's decision of section 7 for LO-01d to LO-01g.

## 2. The collisions restated from their sources (`.out` section 1)

Governing limits (MAKER, Samsung INR18650-35E Ver. 1.1, `v2/vendor/battery/samsung-35e-orbtronic.pdf` 3.12, 3.13):
charge 0 to 45 C and discharge -10 to 60 C at the cell surface; storage 1 month -20 to 60 C, 3 months -20 to 45 C,
1 year -20 to 25 C, each at the ex-factory 30 % charge; "Don't leave, charge or use the battery in a car or similar place
where inside of temperature may be over 60°C". Version 1.0 (`samsung-35e-akkuzentrum.pdf` 3.15, 3.16): the same windows
as ambient, storage from 0 C and 1 year 0 to 23 C. The inside-air temperatures are MODELED from the heat stage's PLAN heat
(PS-SURV-R 23.27 W plus the cells' 0.174 W; PS-SURV 21.73 W plus 0.152 W) on the record's two conductance sets.

| Row | Kind | Condition (source) | Cell temperature (MODELED) | Gap | Layer 3 reproduced | What acceptance requires |
|---|---|---|---|---|---|---|
| LO-01a | in use | +40 C, a mission, battery-powered, heat stage (E3-A, E3-L) | air 62.12 C lid closed (bound) / 55.63 C (32.53); cells on the pack 63.29 C / 56.22 C | 3.29 K on the pack (2.12 K on the air); none on 32.53 | yes (62.1 C) | every cell at or under +60 C and the +59 C abort, thermocouple on every cell |
| LO-01b | in use | -20 C once warm (E4-O) | cells -5.52 C (highest conductance) | none (4.48 K inside) | n/a | every cell at or above -10 C once warm |
| LO-01c | in use | charging; window reached at -17.8 to +34.6 C by state | held off outside the window | none | n/a | T3 in E3-A's pass line |
| LO-01d | margin | +55 C, 4 h, on an input (E3-O) | air 61.63 to 74.22 C; cells on the pack up to 75.39 C | 1.63 to 14.22 K | yes | every cell inside its limit for 4 h, recovery, no shutdown |
| LO-01e | margin | 10 cycles of 24 h, 30 to 60 C, 95 % RH, on an input (E5) | pack idle at the air, 66.63 to 79.22 C | at least 6.63 K | yes | every cell inside its limit through the dwells, capacity recovered |
| LO-01f | margin | +71 C, 24 h, stored, inputs unplugged (E3-S) | +71 C (no self-heating) | 11 K | yes | a cell whose sheet covers +71 C for 24 h at the stored charge |
| LO-01g | margin | -33 C, 24 h, stored (E4-S) | -33 C | 13 K (Ver. 1.1); 33 K (Version 1.0) | yes | a cell whose sheet covers -33 C for 24 h |
| LO-01h | in use | storage -20 to +45 C 3 months, -20 to +25 C a year | the ambient | none (Ver. 1.1); 20 K and 2 K (Version 1.0) | yes | the bought lot's sheet covers both, checked at procurement |

## 3. The feasibility screen (`.out` section 2)

Every required charging, discharging, transport and storage condition, with the actual durations and configurations;
the approaches judged early. Hold times (INFERRED): the cells' own time constant in the pocket is 1081 to 4457 s (0.30
to 1.24 h); the closed, stopped kit's is 1.53 to 3.97 h (appendix 32.53's 8 to 10 kJ/K over the lid-closed still-air
bound), so after 24 h from the most favourable start the cells lag a storage margin's ambient by at most 0.21 K (hot)
and 0.18 K (cold). Holding the cells at the limit for those 24 h would move 185 to 383 Wh (hot) or 218 to 452 Wh
(cold), against the pack's 144.7 Wh nominal and zero power available in storage.

| Id | Condition | Ambient, duration, configuration | Limit (MAKER) | Power for thermal control | Gap | Approaches | Screen |
|---|---|---|---|---|---|---|---|
| C01 | discharge in use, hot edge | +40 C, a mission, pack fitted, discharging | -10 to 60 C surface | the pack | 3.29 K at the bound's worst corner; none on 32.53 | the heat is the kit's own: moving it out works; the enclosure conductance decides (break-even, T-H1); fallback, couple the block to the skin; a path to the face plate rejected (the block sits on the floor under board B, and the plate, the air's main exit, runs near the air); a lower heat stage rejected (REQ-052's set) | CREDIBLE, CONDITIONAL on T-H1 |
| C02 | idle on an input, hot edge (E5-A included) | +40 C, pack idle at the inside air | +60 C (REQ-046's note, REQ-077) | the input | 2.12 K lid closed (bound); none lid open | as C01; the hot stop acts first, FEA-004's | CREDIBLE |
| C03 | discharge in use, cold edge | -20 C once warm, E4-O 4 h | -10 C floor | the pack | none (-5.52 C) | none needed | NO GAP |
| C04 | start from a pack below about -10 C | the start | -10 C floor | input or warming | out of scope (D-02d) | none required | NOT REQUIRED |
| C05 | charging, hot | -20 to +40 C | 0 to 45 C; T3 42 C | the input | none by requirement | held off (REQ-046; D-02b's consequence) | NO GAP |
| C06 | charging, cold (mat before charge) | -20 C, warm-up then charge | from 0 C; UTC 1.0 C, the panel's +3 C hold | the input (8.5 W regulated mat) | the mat lifts the cells to 14.69 C | powered heating with a source present, the existing hold-then-warm start | CREDIBLE (existing mat) |
| C07 | +55 C operating margin (E3-O) | +55 C, 4 h, on an input, pack fitted | +60 C; H1 at a reading of +56.5 C | the input | 1.63 to 14.22 K | fans cannot cool below +55 C and the cells may sit only 5 K over it against a 6.63 to 19.22 K rise; insulation gives no hold for 4 h and in steady state would need 6.7 to 13.7 mm at k 0.02 W/mK (ASSUMPTION) against 0.77 to 2.66 mm of room; coupling: best f 0.485 against 0.260 needed at the worst corner; a Peltier stage has no volume and rejects into the sealed case; the hot stop keeps the cells safe but stops every module (E3-O's "no shutdown" fails), and with the coupling the cells pass H1's reading at every corner | REJECTED (thermal); cell route only |
| C08 | E5's humid dwell | 30 to 60 C, 95 % RH, 10 x 24 h (dwell length not stated in TEST-PLAN), on an input, pack fitted | +60 C | the input | at least 6.63 K; the chamber is at the limit | fans cannot cool below the chamber; no hold over ten days; active cooling as C07 | REJECTED (thermal); cell route only |
| C09 | +71 C storage margin (E3-S) | +71 C, 24 h, stored, inputs unplugged, gauge in shutdown | storage -20 to 60 C, 1 month, 30 % | **zero** | 11 K; the ambient alone exceeds the limit | no power for any active means; settles within 0.21 K in 24 h | REJECTED (thermal); a cell whose sheet covers it only |
| C10 | -33 C storage margin (E4-S) | -33 C, 24 h, stored | floor -20 C (Ver. 1.1); 0 C (Version 1.0) | **zero** | 13 K; 33 K | heating would need 218 to 452 Wh with no source; settles within 0.18 K | REJECTED (thermal); a cell whose sheet covers it only |
| C11 | storage in the envelope | -20 to +45 C 3 months; -20 to +25 C a year | Ver. 1.1's rows | zero | none (Ver. 1.1) | procurement of a Ver. 1.1 lot (BAT-F09) | CREDIBLE (procurement) |
| C12 | transport and stored soaks (REQ-074) | E3-T +58 C, E4-T at the sheet's floor, 24 h, kit off | the sheet's storage limits | zero | none by construction | none needed | NO GAP |
| C13 | PA key-down (PWR-F12) | 18 A for 60 s from C1's +55 C cell trigger | +60 C surface | the pack | none for the cells (56.37 to 58.24 C); F2 open | the existing gates K2, C4 | NO GAP for the cells |

## 4. The thermal measures, only where the screen found a route (`.out` section 3)

- **Break-even (LO-01a), MODELED.** The cells stay at or under +60 C on the pack from a lid-closed fan-on conductance
  of 1.246 W/K (on an input 1.164 W/K), and under H1's +56.5 C reading from 1.530 W/K (1.410 W/K). The record's bounds
  are 1.06 to 2.49 W/K (independent) and 1.5 to 2.0 W/K (appendix 32.53): T-H1 decides which side holds.
- **The pocket coupling measure, the fallback below the break-even (not adopted now).** The block's east face against
  the east wall through a gap filler in the 9.68 mm M4b gap (k 1.0 W/mK, ASSUMPTION), its base on the floor through the
  heater mat (1.5 mm, k 0.2 W/mK, ASSUMPTION; the mat's sheet states neither), the other four faces left in the inside
  air at the record's 5 to 15 W/m2K; wall and outside films from W4's bound (INFERRED). The cells then follow the air's
  rise by f = 0.824 (worst) to 0.485 (best); at LO-01a's worst corner 58.64 C on the pack (1.36 K inside +60 C) and
  57.97 C on an input, under H1's reading only at the best corner (51.99 C). The worst corner is insensitive to the
  filler (3 W/mK adds 0.0015 W/K). The inside air there moves from 62.12 C to 61.94 C.
- **Its cost at the cold end (LO-01b), MODELED.** The coupled block at -20 C in PS-IDLE-SPEC reaches -10.24 C on the
  highest conductance (against -5.52 C without the measure): the mat must hold it at -8.0 C (1 K over UTD's -9.0 C
  reading, INFERRED margin), 0.39 W average on battery, 0.9 % of PS-IDLE-SPEC's 42.82 W (a firmware thermostat).
- **Charging at the cold end, MODELED.** The existing regulated 8.5 W mat on input power lifts the idle pack to
  14.69 C at -20 C (15.68 C with the coupling measure), over UTC's 1.0 C and the panel's +3 C hold. No new part.
- **Placement, INFERRED.** The block's top lies about 3.66 mm under board B's underside (CASE-MARGINS M6), which has no
  local model; a hotter underside raises f, so T-H1's dummy block carries a thermocouple on that face. Board P beside
  the block puts F2 at about the inside air (section 8).

## 5. The cells, alongside (`.out` section 4)

At most three solutions, each inside D-06's single 4S3P in the east pocket. Energy is MODELED with `pwr_budget.usable`
at PS-IDLE-SPEC 42.82 W, +20 C, aged to 80 % (the 35E's rate table used for all three, INFERRED for S2 and S3).

| | S1 Samsung INR18650-35E (as ruled) | S2 Samsung INR18650-30Q, current revision (30Q6) | S3 HL18650V, wide temperature |
|---|---|---|---|
| Document | Ver. 1.1 (MAKER, filed) | V1.0, application date 2020/01/17 (MAKER, held back: "Confidential Proprietary"); also its 2015 Version 1.0 and a 2024 customer draft, read | Yichun Topwell Power's product page (a page, not a specification: classed INFERRED) |
| Charge | 0 to 45 C surface | 0 to 45 C ambient; 0 to 50 C surface | -20 to 60 C, reduced rates below +10 C |
| Discharge | -10 to 60 C surface | -20 to 60 C ambient; -20 to 80 C surface ("must re-discharge release < 60") | -40 to 85 C (basis not stated) |
| Storage | 1 month -20 to 60, 3 months -20 to 45, 1 year -20 to 25 C, at 30 % | 1 month -20 to 60, 3 months -20 to 45, 1 year -20 to 23 C, at 30 % | 30 days -40 to 80, 3 months -40 to 60, 6 months -20 to 45, 12 months -20 to 25 C; no state of charge, no recovery figure |
| Pack energy, nominal / usable / battery-only | 144.7 Wh / 108.1 Wh / 2.52 h | 127.4 Wh / 95.2 Wh / 2.22 h (-11.9 %) | 121.0 Wh / 90.4 Wh / 2.11 h (-16.4 %) |
| At -10 C (aged, the sheet's cold point) | 44.3 Wh (0.41 at 1C) | 71.4 Wh (0.75 at 10 A) | not stated |
| DR-01 (REQ-072, 48 to 72 h) | FAIL | FAIL, wider | FAIL, wider |
| Current against PS-ALLTX (6.0 A a cell, 60 s) | 8 A continuous: carries it | 15 A: carries it | 10 A: carries it |
| Cycle terms | 60 % after 500 cycles (1.02 A charge, 3.4 A discharge) | 60 % after 250 cycles (4 A, 15 A: not comparable) | "at least 500 times" (25 C, 0.5C/1C) |
| Fit in the east pocket (INFERRED) | the ruled block | smaller by 0.50 / 0.45 / 0.30 mm | +0.50 mm along the axis against 0.77 mm of room: fits |
| Protection and charger | none | 4.2 V (BQ25731 unchanged), gauge chemistry data; the ladder stays at the 60 C basis unless Samsung reads its ambient as the outside air | 4.2 V; gauge data; U2 off its 70 C (80 or 83 C variants exist), SOT moved, **a fuse for F2's place beyond -20 to +60 C: none held** |
| Rows its own limits cover (a, d, e, f, g, h) | h only | none (h fails at the 23 C year) | all six, on the page's figures |
| Thermal-control burden | the design's (C1, hot stop, mat on input); coupling only below the break-even | the same | the same; storage levels on the cell's own rating, no power |
| Evidence outstanding | T-H1, E3-L, E3-H, the lot's revision | those, plus Samsung's reading of its ambient clause | the maker's signed specification, the maker's identity, F2's replacement, U2, gauge data, UN 38.3 papers |
| Unit price (spend) | USD 8.25 (Battery Junction, l3batt's reading) | USD 6.99 (18650 Battery Store, in stock) | USD 3.50 (a marketplace seller, 10 to 4,999 pieces) |

Read and set aside: LG INR18650HG2 (BCY-PS-HG2-Rev0; held back), whose 2.9 gives discharge to 75 C but whose own 5.1
cautions say -20 to 60 C, with a one-year storage top of 20 C (fails LO-01h); Molicel INR-18650-P28A (filed), ambient
discharge -40 to 60 C and no storage clause. Prices and the page were read on 1 October 2026 at 22:12 UTC
(`inputs/`). None of these readings is a purchase.

## 6. The decision per row (`.out` section 5)

| Row | Decision | Evidence | Verification |
|---|---|---|---|
| LO-01a | **CONDITIONAL**: thermal design; no measure above the break-even, the coupling measure below it | MAKER, MODELED, INFERRED, ASSUMPTION | T-H1 (lid closed, fans, the dummy block's thermocouples), then E3-L and E3-H with the pack fitted at +40 C, a thermocouple on every cell |
| LO-01b | NO COLLISION | MAKER, MODELED (bounded) | E4-O with the pack fitted |
| LO-01c | NO COLLISION | MAKER, MODELED (bounded) | E3-A's T3 line, E4-O's charge floor |
| LO-01d | **NOT CLOSABLE** on held evidence: the owner's decision (section 7) | MAKER, MODELED, INFERRED | after the decision: E3-O with the pack fitted, or as REQ-051's deviation |
| LO-01e | **NOT CLOSABLE**: the owner's decision | MAKER, MODELED, INFERRED | E5 likewise |
| LO-01f | **NOT CLOSABLE**: the owner's decision | MAKER, MODELED, INFERRED | E3-S likewise |
| LO-01g | **NOT CLOSABLE**: the owner's decision | MAKER, MODELED, INFERRED | E4-S likewise |
| LO-01h | **CONDITIONAL**: procurement | MAKER | the purchase record names the lot's specification revision (Ver. 1.1; BAT-F09); E4-T at the governing floor |

No row is recorded as CLOSED, and no cell change is taken.

## 7. The conflict, and the owner's options

**Exactly.** D-02a's +55 C operation (4 h, E3-O), +71 C storage (24 h, E3-S) and -33 C storage (24 h, E4-S), and SC-03's
E5 dwell to +60 C (10 x 24 h), each with the pack fitted as FEA-008's acceptance reads them (REQ-051; D-29: no cell
exemption; the stored kit keeps its pack, REQ-025 and SC-19; no power in storage), against the cell maker's +60 C
(discharge at the surface, storage for one month at 30 % charge), its -20 C storage floor and its prohibition of a
place over 60 C (35E Ver. 1.1 3.12, 3.13 and the handling list). Every 18650 maker's specification held stops at +60 C
in storage, and none covers storage below -30 C (the 2015 30Q). The ambient alone reaches or passes the limit in E3-S,
E4-S and E5; in E3-O the kit's own heat adds 6.63 to 19.22 K over +55 C. Bound with it: D-06 (one 4S3P 18650 pack of
about 145 Wh in the east pocket), REQ-074 (the cells never past their own storage limits; the pack comes out for such
exposure) and board P's F2 (-20 to +60 C), which every one of the four levels also leaves. **The collision is between
D-02a with SC-03, as FEA-008 reads them, and D-06 with REQ-074.**

**The one decision:** for these four levels, is the kit's margin to be shown with its pack fitted (which needs a cell
and a fuse no held specification covers), or with the pack removed and stored apart, as REQ-074 already instructs and
REQ-051's deviations already run (the reading D-29 reserves to the owner)?

| Option | What it is | Consequence |
|---|---|---|
| **A** | Keep the 35E (D-06 as ruled); show these four levels with the pack out of the exposure | No spend, no energy lost, no part changed. The kit is not claimed at those four levels with its own pack. FEA-008's rows d to g close by his decision; a and h stay CONDITIONAL on their verification |
| **B** | A wide-temperature 18650 inside D-06's 4S3P (the HL18650V class): first the maker's signed specification (the draft in `clarification/`, no money), then a fuse for F2's place, U2's variant, gauge data, UN 38.3 papers | About USD 42 for one pack of 12 at USD 3.50 (sample lots extra); 121.0 Wh nominal against 144.7 (16.4 % less usable), so D-06's "about 145 Wh" is restated and DR-01 widens (2.11 h against 2.52 h); closes d to g only if every outstanding item lands; his spend approval and D-06's restatement first (cell_provenance) |
| **C** | Keep rows d to g open as a release gate, no reading and no spend, until a cell and a fuse with makers' specifications are found | The power architecture's closure criterion 1 stays failing on those four rows |

**Session's recommendation, not adopted (D-29 reserves the reading to the owner): A**, because no held maker's
specification of an 18650 lithium-ion cell covers the storage levels, the cell maker forbids the condition, REQ-074
already takes the pack out for it, and option B rests on a product page and a fuse nobody has found.

## 8. The battery path's other thermal items (`.out` section 6)

- **F2 (Eaton SCF9550-30-05, MAKER ELX1135):** operating -20 to +60 C; storage -10 to +40 C below 90 % RH for a year
  (whether that line covers a mounted part is not stated); endurance lines +105 C for 1000 h and -40 C for 500 h are
  test conditions, not a rating. Board P sits beside the block, so F2 is at about the inside air or the cells
  (INFERRED): past its range at LO-01a's worst corner (62.12 C air), at LO-01d to LO-01g, and, if its storage line
  applies, at both ends of the storage envelope. The questions are drafted for Eaton (`clarification/eaton-scf9550.txt`,
  extending Q-E2).
- **PWR-F12's key-down:** 18 A for 60 s (6.0 A a cell) from C1's +55 C warms the cells 1.37 to 3.24 K adiabatically
  (MODELED), to 56.37 to 58.24 C, inside +60 C; F2's own 0.32 to 0.81 W rise is unpublished, so its margin stays
  PWR-F12's (P13). The coupling measure changes neither figure; its time constant (1554 to 3773 s) is about today's.
- **U2 (BQ7720700):** its fixed 70 C over-temperature trips from 62.7 C at the network, so at +71 C storage and at the
  +55 C margin's worst air a fitted pack would blow F2 and be retired: option B needs the 80 C or 83 C variant.
- **The gauge's thresholds** (OTC 44.0, OTD 57.5, UTC 1.0, UTD -9.0 C) stay inside REQ-046's windows; this record moves
  none. With the coupling measure the block gains a gradient (wall side cooler, the side under board B hotter), so the
  thermistors go on the hottest cells and P14's gradient term is re-measured (INFERRED).

## 9. What stays CONDITIONAL, and how each is verified

| Item | Condition | Verification |
|---|---|---|
| LO-01a, no measure | the lid-closed fan-on conductance is at least 1.246 W/K (1.164 on an input) | T-H1, then E3-L and E3-H with the pack fitted |
| LO-01a, coupling measure (if T-H1 reads lower) | the film and filler figures (INFERRED, ASSUMPTION) and board B's underside | E3-L with the pack fitted and the coupled block; P14's gradient |
| LO-01b with the coupling measure | the mat's 0.39 W thermostat on battery | E4-O |
| LO-01h | the lot follows Ver. 1.1 | the purchase record; E4-T |
| Option B, if chosen | the maker's signed specification and a fuse for F2's place | the documents filed; then E3-S, E4-S, E3-O and E5 with the pack fitted |

## 10. Downstream items (owner by layer; acceptance)

| Owner | Item | Acceptance |
|---|---|---|
| Layer 6, components | the 35E lot's revision on the purchase record (LO-01h); Eaton's answer on F2 (storage line, above +60 C); under B only, the cell's specification, a fuse for F2's place, U2's variant | the documents filed and read |
| Layer 7, mechanical | if T-H1 reads under 1.246 W/K: the block's east face and base coupled to the skin, the hold-down (M4a, M5 OPEN) designed around it | E3-L with the pack fitted, every cell at or under +60 C at +40 C lid closed |
| Layer 8, generator owners | none now; under B, `gen_sch_p.py` (U2, F2) and `pcb_pack_protection.yaml`'s thresholds re-derived | the protection suite |
| Layer 9, pre-layout analysis | board P's place against the block (F2 at the air passes +60 C at LO-01a's worst corner); thermistors on the hottest cells | F2's body at or under +60 C in E3-A, E3-L and P13; P14 measured |
| Prototype bench | T-H1 with the dummy pack block; E3-A, E3-L, E3-H with a thermocouple on every cell; E4-O; P13; P14 | each run's TEST-PLAN pass line; the break-even replaced by the measured conductance |
| Firmware owner | only with the coupling measure: the mat's thermostat on battery at the cold end, its use in the energy budget | E4-O's log |
| Owner | the decision of section 7 (A, B or C); no spend is asked now | his ruling in the register |

## 11. Decisions taken by the session (authority: SESSION, under the owner's standing rule of 26 September 2026)

| Decision | Why the session's | Reversed by |
|---|---|---|
| S1 selected; S2 not recommended; no cell spend proposed now | engineering selection within D-06; no requirement changes and no money is spent | the owner choosing option B, or a new maker's specification |
| The coupling measure is a fallback, not adopted now | it buys 4.65 K at the worst corner, costs a cold-end thermostat, and is not needed on the design record's conductance; T-H1 decides | T-H1 below 1.246 W/K |
| An idle pack on an input is held to +60 C | REQ-046's note and REQ-077 already read it so; the maker's sheets give no rest-state figure | a maker's statement on the rest state |
| The HL18650V's figures are INFERRED, not MAKER | a product page with no test conditions, state of charge or recovery figure | the maker's signed specification |
| One sheet filed (Molicel P28A), four held back (three Samsung, one LG) | each file's terms, read conservatively (the owner's rule of 27 September 2026); `fetch_held_back.py` refetches them by sha256 | the makers' permission |

## 12. Files

`l4e10_cell_thermal.py` and `.out` (section 0 reproduces `pwr_budget.out` and `.json`, `pwr_red2.out` and
`hotstop_bounds.out` byte for byte and pins 29 inputs by sha256; section 8 prints the predicates);
`fetch_held_back.py`; `inputs/` (the HL18650V page and the price readings); `clarification/` (drafts for the owner to
send: Topwell for the specification, Eaton for F2); `README.md`. The tests: `env -C v2/ecad/tools/tests python3 run.py
test_l4e10 test_public_hygiene`. No generator, BOM, registry or Layer 3 file is changed, so no draft apply script is
needed.
