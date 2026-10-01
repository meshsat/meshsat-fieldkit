# L4-E10: the cell and thermal design of the battery path against the temperature requirements (FEA-008)

MESHSAT-1357, layer 4 task L4-E10, 2 October 2026, revised the same day after the collaborator's check 1
(`checks/astra-check-l4e10-1.md`, NOT YET; section 12 maps each item to its change). **Prototype design, desk
arithmetic: nothing has been bought, built, powered or measured, and no kit has been field deployed.** Every figure comes
from `l4e10_cell_thermal.out` (the script `l4e10_cell_thermal.py` reproduces it byte for byte) and carries its class:
MAKER (a maker's specification, clause named), MODELED (the tree's power and thermal model, `records/rv-pwr/pwr_budget.py`
and `records/hc2/pwr_red2.py`, imported unchanged and reproduced first), INFERRED (method stated), ASSUMPTION (a figure no
held document gives), CONDITIONAL (holds only on a stated condition). The order follows the owner's refinement of
2 October 2026: a feasibility screen of every condition, the routes bounded, the cells alongside, the simplest defensible
selection, then the owner's bounded checks of the same day.

## 1. The answer in short

- **FEA-008 stays open as an engineering obligation; no owner decision is forced.** A missing cell whose sheet covers the levels is a
  component limitation plus missing feasibility evidence, not a contradiction between owner requirements (D-29, D-36,
  `l3r2.yaml` cell_provenance). Every open row keeps at least one route that is INCONCLUSIVE on named inputs, and no row
  has every route rejected on bounded evidence, which is the only condition under which escalation would be warranted.
- **LO-01a (in use, +40 C) is CONDITIONAL on the enclosure's measured conductance.** Three thresholds are kept apart
  (lid closed or open, with fans, the heat stage at PLAN heat): the cell rating alone holds from 1.2455 W/K on the pack;
  FEA-008's own criterion with the +59 C abort from 1.3154 W/K; the complete E3-A and E3-L pass line from **1.6664 W/K**,
  set by the SGP41's +55 C inside air on shore (H1 not acting needs 1.5300 W/K, 1.6043 W/K with the 0.71 K reading-high
  term). T-H1 must read at least 1.666 W/K in both lid states. At the independent bound's lowest the cells reach 63.29 C
  lid closed and 60.39 C lid open; on appendix 32.53's figures 56.22 C. The pocket coupling fallback lowers the cells to
  58.64 C but leaves the inside air at 61.94 C, so it never replaces the conductance.
- **LO-01h is CONDITIONAL on procurement** (Ver. 1.1 covers both storage rows; Version 1.0 does not). **LO-01b and
  LO-01c have no collision.**
- **LO-01d to LO-01g are OPEN, each with bounded routes.** Passive design is rejected only where a bound shows it (the
  +55 C margin; 24.6 mm and 30.3 mm of insulation for the storage margins against at most 2.66 mm of room). For LO-01g
  the comparison of 38.1 to 106.1 Wh with the pack's nominal 144.7 Wh is **withdrawn** as a feasibility basis: on usable
  energy, a heater fed by the pack (a discharge, held at -8.14 C) lasts only 1.3 to 8.6 h of the 24 h at the stored
  charge and has no protected path in the gauge's shutdown; a heater fed by a separate primary source stays INCONCLUSIVE
  until that source's usable energy at -33 C is known. E5's thermal storage waits on its profile, powered cooling on a
  cooler's sheet and the input's spare power, a cell route on a maker's specification and a protection redesign.
- **Selected: A1, the Samsung INR18650-35E as ruled (D-06) with local thermal management; no spend now.** No cell change is
  taken, and no approved constraint is changed.

## 2. The collisions restated from their sources (`.out` section 1)

Governing limits (MAKER, Samsung INR18650-35E Ver. 1.1, `samsung-35e-orbtronic.pdf` 3.12, 3.13): charge 0 to 45 C and
discharge -10 to 60 C at the cell surface; storage 1 month -20 to 60 C, 3 months -20 to 45 C, 1 year -20 to 25 C, at the
ex-factory 30 % charge; at full charge the maker's own 20 days at 60 C with at least 3,183 mAh (95 %) recovered (7.10).
Version 1.0 (`samsung-35e-akkuzentrum.pdf` 3.15, 3.16): the same windows as ambient, storage from 0 C, 1 year 0 to 23 C.

| Row | Kind | Condition (source) | Cell temperature (MODELED) | Gap | Layer 3 reproduced |
|---|---|---|---|---|---|
| LO-01a | in use | +40 C, the heat stage, on the pack then on shore (E3-A, E3-L) | lid closed: air 62.12 C, cells on the pack 63.29 C (bound); 56.22 C (32.53). Lid open at the bound's lowest: cells on the pack 60.39 C, air on shore 60.49 C | 3.29 K lid closed (2.12 K on the air); lid open past +60 C as well | yes (62.1 C) |
| LO-01b | in use | -20 C once warm (E4-O) | cells -5.52 C | none (4.48 K inside) | n/a |
| LO-01c | in use | charging, window reached at -17.8 to +34.6 C | held off outside the window | none | n/a |
| LO-01d | margin | +55 C, 4 h, on an input (E3-O) | air 61.63 to 74.22 C; cells on the pack up to 75.39 C | 1.63 to 14.22 K | yes |
| LO-01e | margin | 10 cycles of 24 h, 30 to 60 C, 95 % RH, on an input (E5) | pack idle at the air, 66.63 to 79.22 C | at least 6.63 K | yes |
| LO-01f | margin | +71 C, 24 h, stored, inputs unplugged (E3-S) | +71 C | 11 K | yes |
| LO-01g | margin | -33 C, 24 h, stored (E4-S) | -33 C | 13 K (Ver. 1.1); 33 K (Version 1.0) | yes |
| LO-01h | in use | storage -20 to +45 C 3 months, -20 to +25 C a year | the ambient | none (Ver. 1.1); 20 K and 2 K (Version 1.0) | yes |

## 3. The feasibility screen (`.out` section 2)

Every required charging, discharging, transport and storage condition with its duration, configuration and charge
state. A rejection is kept only where physics or a bounded figure gives it; a route with a missing input is INCONCLUSIVE.

| Id | Condition | Ambient, duration, configuration | Limit (MAKER) | Power | Gap | Result |
|---|---|---|---|---|---|---|
| C01 | discharge in use, lid closed (E3-L at +40 C) | +40 C, 4 h, the heat stage, pack fitted | -10 to 60 C surface; +59 C abort | the pack | 3.29 K at the bound's worst corner; none on 32.53 | CREDIBLE, CONDITIONAL on T-H1 (the face plate gives no gain: the block sits under board B and the plate, the air's main exit, runs near the air) |
| C02 | on shore at the hot edge (E3-L's second half, E3-A's 2 h on shore, E5-A) | +40 C, lid open or closed, pack idle | +60 C (REQ-046's note, REQ-077) | the input | 2.12 K lid closed; lid open 60.49 C air, 60.39 C cells on the pack | CREDIBLE, CONDITIONAL on T-H1, both lid states |
| C03 | E3-A's +25 C point, 4 h, three loaded modules on shore | +25 C, the stage C1 selects | +60 C; T3 42 C | the input | none for the cells; charging recorded | NO GAP |
| C04 | E3-L's +20 C and +30 C levels | 4 h each, on the pack then on shore | +60 C; SGP41 +55 C air | pack, input | none: cells 52.04 C (reduced mode) and 53.29 C (heat stage) | NO GAP |
| C05 | E3-H's stepped run (protection test) | from +40 C by 2 K an hour to at most +55 C | no cell at +59 C before H1 and H2 | input, pack | none for the cells; whether H2 is reached depends on the minimum load (P15 forces it) | NO GAP for the cells |
| C06 | discharge, cold edge (E4-O) | -20 C, 4 h, warm | -10 C floor | pack or input | none (-5.52 C) | NO GAP |
| C07 | start from a pack below about -10 C | the start | -10 C floor | input or warming | out of scope (D-02d) | NOT REQUIRED |
| C08 | charging, hot | -20 to +40 C | 0 to 45 C; T3 42 C | the input | none by requirement | NO GAP |
| C09 | charging, cold (mat before charge) | -20 C, warm-up then charge | UTC 1.0 C, panel hold +3 C | the input (7.5 W into the cells, 1.0 W regulator loss into the air) | the mat lifts the idle cells to 12.44 C | CREDIBLE (existing mat) |
| C10 | +55 C operating margin (E3-O) | +55 C, 4 h, on an input, pack fitted | +60 C; H1 +56.5 C; "no shutdown" | the input | 1.63 to 14.22 K | OPEN: passive design rejected (bounded); cooling and a cell INCONCLUSIVE |
| C11 | E5's humid cycle | 30 to 60 C, 95 % RH, 10 x 24 h (dwell and ramps not stated), on an input | +60 C | the input | at least 6.63 K | OPEN: every route INCONCLUSIVE on named inputs |
| C12 | +71 C storage margin (E3-S) | +71 C, 24 h, stored at 30 %, gauge in shutdown | storage 1 month to 60 C at 30 % | **zero** (a separate source only if added) | 11 K | OPEN: zero-power design rejected (24.6 mm needed); cooling and a cell INCONCLUSIVE |
| C13 | -33 C storage margin (E4-S) | -33 C, 24 h, stored | floor -20 C; discharge floor -10 C | **zero** (a separate primary only if added) | 13 K; 33 K | OPEN: a pack-fed heater rejected within REQ-025 (1.3 to 8.6 h of 24 h); a separately fed heater INCONCLUSIVE on named unknowns |
| C14 | storage in the envelope | -20 to +45 C 3 months; -20 to +25 C a year | Ver. 1.1 rows at 30 % | zero | none (Ver. 1.1) | CREDIBLE (procurement) |
| C15 | E3-T stored and transport soak | +58 C set point +-2 K, 24 h; ex-factory (storage) or its charge (transport) | 1 month to 60 C at 30 %; full charge: 20 days at 60 C, 95 % recovered (7.10) | zero | none: the top tolerance reaches the limit | NO GAP |
| C16 | E4-T cold soak | the governing floor, 24 h | -20 C at 30 %; F2's floor -20 C | zero | none for the cells; F2's storage line open | NO GAP for the cells |
| C17 | E3-P: pack alone, armed, full charge, then 2 A from +58 C | +58 C +-2 K, 24 h, then until the gauge stops it | 7.10's full-charge storage; discharge to 60 C | the test load | none: the discharge starts at or above OTD's 57.5 C reading, so the gauge refuses it (the pass line) | NO GAP |
| C18 | E4-P: pack alone, cold | as E4-T, 24 h | -20 C at 30 %; no cold recovery figure | zero | none at the ex-factory state | NO GAP |
| C19 | P13: 18 A for 60 s from +55 C; 10 A for 1 h at the hot limit | bench block, thermocouple on F2 | +60 C at the cells and F2 | the test load | key-down none (56.37 to 58.24 C); the hour's own 4.67 to 8.00 W lift the cells 10.5 to 54.0 K over the block's air | NO GAP if the limit is held at the cell surface (a definition item for P13's owner); F2 open |

## 4. The thermal routes, bounded (`.out` section 3)

- **LO-01a's thresholds, MODELED** (W/K from which each criterion holds; on shore the front end's and charger's loss on
  the loads adds 1.725 W):

  | Criterion | On the pack | On shore |
  |---|---|---|
  | cell rating, +60 C | 1.2455 | 1.2498 |
  | the +59 C abort (FEA-008's LO-01a) | 1.3154 | 1.3156 |
  | H1 not acting, no sensor allowance | 1.5300 | 1.5149 |
  | H1 with the 0.71 K reading-high term | 1.6043 | 1.5831 |
  | SGP41 inside air at most +55 C | 1.5630 | **1.6664** |
  | F2 at the inside air at most +60 C | 1.1723 | 1.2498 |

  The record's bounds are 1.06 to 2.49 W/K lid closed and 1.22 to 2.85 W/K lid open (independent), 1.5 to 2.0 and 3.0 to
  3.3 W/K (appendix 32.53). Dependencies that fail today and stay visible: board B as generated lacks BANK-R1, so E3-L's
  stage criteria fail wherever the heat stage is entered; F2's body (P13, PWR-F12); the gauge's ADC and gradient terms
  (P14); HIGH heat is not covered.
- **The pocket coupling (a fallback for the cells only).** East face to the east wall through a gap filler in the
  9.68 mm M4b gap (k 1.0 W/mK, ASSUMPTION), base to the floor through the heater mat (1.5 mm, k 0.2 W/mK, ASSUMPTION),
  four faces in the air (5 to 15 W/m2K), W4's films (INFERRED): f = 0.824 to 0.485. At LO-01a's worst corner the cells
  fall to 58.64 C (holds +60 C and the +59 C abort) but stay over H1 (fails by 2.14 K) and the air stays 61.94 C (SGP41
  fails by 6.94 K, F2 by 1.94 K).
- **Cold end, MODELED.** With the coupling the cells at -20 C fall to -10.24 C; holding -8.0 C takes 0.38 W into the
  cells, 0.44 W from the battery (1.0 % of PS-IDLE-SPEC). Charging at -20 C: the mat's 7.5 W into the cells (MAKER) and
  its regulator's 1.0 W into the air lift the idle cells to 12.44 C (12.84 C with the coupling), over the +3 C hold.
- **Storage hold times, INFERRED.** After 24 h the cells lag the ambient by 0.21 K (hot) and 0.18 K (cold) as one node,
  0.351 K and 0.301 K as two nodes (the slowest kit: 9340 J/K beside the cells' 660 J/K, 0.70 W/K to ambient, 0.1481 W/K
  to the cells). The first issue's 218 to 452 Wh heated the whole kit; the pack alone is below.
- **Passive storage routes, bounded.** For 24 h of hold from the most favourable start, the pack's coupling must fall
  under 0.0207 W/K (+71 C) or 0.0173 W/K (-33 C), that is 24.6 mm or 30.3 mm of insulation at k 0.02 W/mK (ASSUMPTION)
  against 0.77 to 2.66 mm of room in D-06's pocket: rejected within the pocket.
- **LO-01g, the -33 C storage margin, in three cases** (ambient and cell temperatures kept apart; one calculation
  boundary at the source's terminals: the mat's 7.5 W into the block, its regulator's 0.133 of that into the air, the
  gauge's 336 uA NORMAL draw when the pack feeds it; series path 0.1222 to 0.3400 W/K). The nominal comparison of 38.1 to
  106.1 Wh with the pack's 144.7 Wh is **withdrawn** as a feasibility basis.
  - **(i) a warm pack kept inside its limits.** Fed by the pack, the heater discharges the cells, so the discharge window
    governs and the setpoint is UTD's -9.0 C reading plus the published 0.86 K cold budget, -8.14 C (gradient and ADC
    TBD): 3.37 to 9.30 W at the pack's terminals. The usable energy at the stored 30 % charge, less the 5 % reserve, aged
    to 80 %, times the cold factor (unknown between MAKER 7.5's 0.41 and 1.0) is 11.9 to 28.9 Wh: **1.3 to 8.6 h of the
    24 h**, a reserve of -211.2 to -51.9 Wh; and in shutdown "the device turns off the FETs" (MAKER, SLUUAQ3A 5.4.2), so
    there is no protected path. Even with the gauge awake and a full charge, 4.9 to 32.6 h. Fed by a separate primary
    source the pack stays in its storage row: at the -20 C floor itself 1.59 to 4.42 W, 38.1 to 106.1 Wh driven direct
    (42.2 to 116.6 Wh through the regulator), plus 2.93 to 8.16 Wh per K of margin; a thermostat on the block,
    independent of the gauge and the kit, closes at its setpoint. Its usable energy at -33 C, the thermostat's tolerance,
    the gradient, a place and its transport classification are **named unknowns**: its duration is not computed. Its
    scope if they land: E4-S's 24 h from a warm stored kit. F2 sits at about -30.7 to -30.0 C there, below its -20 C
    floor (Eaton, or a heated zone over board P).
  - Recovery: E4-O follows E4-S; a pack held at the -20 C floor is below the -10 C discharge floor, so E4-O starts
    from an input or after warming, as TEST-PLAN and D-02d already allow.
  - **(ii) a pack already cold-soaked:** below -20 C it has left its storage row and no heater undoes that; between -20
    and -10 C the pack may not discharge and the gauge holds its FET off below UTD (recovery -4.0 C), so only a separate
    source can rewarm it, 0.133 to 0.183 Wh per K plus losses.
  - **(iii) heating lost or spent:** the cells pass -20 C 0.30 to 1.09 h after a pack-fed hold stops, at once for a hold
    at the floor, so the margin must cover depletion; nothing records the event in shutdown (a named item).
  - Cool-down credit, ASSUMPTION (E4-S's start state is not stated; from the sheet's 23 C): 1.57 to 4.57 h before the
    pack reaches -8.14 C, 2.58 to 7.27 h before -20 C.
- **E5's cycle.** TEST-PLAN states 10 cycles of 24 h between 30 and 60 C and no dwell or ramp. A passive network passes
  the cycle's mean, so storage can help only if the mean ambient is under 40.78 C (worst rise) to 53.37 C (best). For a
  symmetric cycle (mean 45 C, ASSUMPTION): impossible at the worst corner; at the best a 5.68 h time constant (the cool
  half's regeneration included), 14.4 to 21.2 mm of insulation or 3.0 to 9.1 kJ/K of added heat capacity, against at
  most 2.66 mm and a full pocket. INCONCLUSIVE until the profile is stated.
- **Powered cooling** (COP 0.5 to 1.0 and a hot side at most 30 K over its sink, ASSUMPTION): cold-side loads
  0.76 to 7.87 W (E3-O), 1.50 to 10.09 W (E5), 1.60 to 4.44 W (E3-S, 38 to 213 Wh from a separate source over 24 h). Rejecting the
  heat into the inside air does not converge at the worst corners at COP 0.5; through a path out of the case it needs
  0.051 to 1.009 W/K, and the pack's own skin path (0.054 to 0.090 W/K) serves only E3-O's best corner. INCONCLUSIVE: a
  cooler's sheet, the input's spare power, the volume and a sealed path out of the case are missing.
- **PWR-F12 and P13, MODELED.** 18 A for 60 s from +55 C warms the cells 1.37 to 3.24 K (to 56.37 to 58.24 C). P13's hour
  at 10 A puts 4.67 to 8.00 W into the cells, 10.5 to 54.0 K over the block's air, so its "hot limit" must be held at the
  cell surface.

## 5. The cells, alongside (`.out` section 4)

| | S1 Samsung INR18650-35E (as ruled) | S2 Samsung INR18650-30Q, current revision (30Q6) | S3 HL18650V, wide temperature |
|---|---|---|---|
| Document | Ver. 1.1 (MAKER, filed) | V1.0, 2020/01/17 (MAKER, held back); its 2015 Version 1.0 and a 2024 draft read | Yichun Topwell Power's product page (not a specification: INFERRED) |
| Charge / discharge | 0 to 45 C / -10 to 60 C surface | ambient 0 to 45 / -20 to 60 C; surface 0 to 50 / -20 to 80 C | -20 to 60 C / -40 to 85 C (basis not stated) |
| Storage | 1 month -20 to 60, 3 months -20 to 45, 1 year -20 to 25 C at 30 % | 1 month -20 to 60, 3 months -20 to 45, 1 year -20 to 23 C at 30 % | 30 days -40 to 80, 3 months -40 to 60, 6 months -20 to 45, 12 months -20 to 25 C; no charge state |
| Energy nominal / usable / hours (DR-01 FAIL for all) | 144.7 Wh / 108.1 Wh / 2.52 h | 127.4 / 95.2 Wh / 2.22 h (-11.9 %) | 121.0 / 90.4 Wh / 2.11 h (-16.4 %) |
| At -10 C (aged) | 44.3 Wh | 71.4 Wh | not stated |
| Current against PS-ALLTX (6.0 A a cell) | 8 A | 15 A | 10 A |
| Fit in the east pocket | the ruled block | smaller | +0.50 mm against 0.77 mm of room |
| Rows its own limits cover | h | none (h fails at 23 C) | all six, on the page's figures |
| Protection and charger | none | 4.2 V unchanged; gauge data; above +60 C, the redesign below | 4.2 V; gauge data; the redesign below |
| Unit price | USD 8.25 | USD 6.99 | USD 3.50 (a marketplace seller) |

**The protection and control redesign is the entry cost of any cell used above +60 C.** Keeping H1 and H2 at their
35E-derived readings still stops every module in the hot margins. U2's variants are not drop-ins (MAKER, SLUSEG7D p.3):
the 80 C BQ7720701 and BQ7720702 change OVP to 4.275 V and UVP to 2.0 V (and 02 the OV delay to 4 s); the 83 C BQ7720704
changes COUT to an open-drain active pulldown. The hot ladder (C1, H1, H2, OTD, SOT, U2's OT and voltage thresholds, the
PTC) and F2's replacement must be re-specified together, with their tolerance, nuisance-trip and permanent-trip bounds
recomputed for storage and powered operation. This record does not specify it.

**The bounded shortlist (`.out` 4b).** A1, the 35E with local thermal management (the enclosure for LO-01a, the coupling
for the cells, a separately fed heater for LO-01g, a cooler for the hot margins): keeps D-06's pack and pocket, the
sealed case and REQ-025's stored state; adds parts whose purchase is the owner's spend when made; **selected**. A2, a
compatible alternative cell with the protection redesign: changes the cell D-06 names (spend, D-06's parenthesis), 11.9 to
16.4 % less usable energy. A3, an insulated pack enclosure (24.6 to 30.3 mm): cannot sit in D-06's shrink-wrapped pocket,
so it changes an approved constraint; not selected while A1's routes stand. A heater fed by the pack would change
REQ-025's stored state likewise.

Read and set aside: LG INR18650HG2 (its own 5.1 cautions limit discharge to 60 C; its year at 20 C fails LO-01h) and
Molicel INR-18650-P28A (ambient discharge to 60 C, no storage clause). Assessed in check 1, not held and not read here: a
Saft MP174565 xtd prismatic cell, as 4S1P only 58.4 Wh and 8 A continuous against the pack's 18 A, so not a substitute
inside D-06.

## 6. The decision per row, with its complete acceptance (`.out` section 5)

| Row | Decision | Evidence | Complete acceptance | Routes |
|---|---|---|---|---|
| LO-01a | **CONDITIONAL** | MAKER, MODELED, INFERRED, ASSUMPTION | E3-A and E3-L at +40 C, on the pack then on shore: every cell at or under +60 C and the +59 C abort, H1 not acting, inside air at or under +55 C (SGP41), F2's body at or under +60 C, the stage's bearers live (REQ-052), C1 to C3 and K2 at their triggers, no permanent protection | the measured conductance, at least 1.666 W/K in both lid states (CONDITIONAL); the coupling for the cells only (CONDITIONAL) |
| LO-01b | NO COLLISION | MAKER, MODELED | E4-O: every cell at or above -10 C once warm | none needed |
| LO-01c | NO COLLISION | MAKER, MODELED | E3-A's T3, T4 and OTC lines; E4-O's floor and the panel's hold | none needed |
| LO-01d | **OPEN** | MAKER, MODELED, INFERRED, ASSUMPTION | E3-O, pack fitted: every cell inside its limit for 4 h, no shutdown, recovery | passive REJECTED (bounded); cooling INCONCLUSIVE; a cell with the redesign INCONCLUSIVE |
| LO-01e | **OPEN** | as LO-01d | E5, pack fitted: every cell inside its limit through the dwells, capacity recovered | storage over the cycle INCONCLUSIVE (profile); cooling INCONCLUSIVE; a cell INCONCLUSIVE |
| LO-01f | **OPEN** | as LO-01d | E3-S, pack fitted: every cell inside its storage limit for 24 h at the stored charge (a cell covering +71 C, or the cells held under +60 C), capacity recovered | passive REJECTED (24.6 mm); cooling from a separate source INCONCLUSIVE; a cell INCONCLUSIVE |
| LO-01g | **OPEN** | as LO-01d | E4-S, pack fitted: every cell inside its storage row for 24 h (or a cell covering -33 C), capacity recovered | passive REJECTED (30.3 mm); a pack-fed heater REJECTED within REQ-025 (1.3 to 8.6 h of 24 h, no protected path); **a separately fed heater INCONCLUSIVE on named unknowns**; a cell INCONCLUSIVE |
| LO-01h | **CONDITIONAL** | MAKER | the bought lot's sheet covers -20 C for 3 months and +25 C for a year; E4-T at the floor | procurement |

No row is recorded as CLOSED, and no cell change is taken.

## 7. Why no owner decision is forced, and the exact remaining facts

Escalation is warranted only once every engineering route of a row within the requirements is shown unavailable on
bounded evidence; no row is there (rows with every route rejected: none). The selected approach, A1, changes no approved
constraint; A2, A3 and a pack-fed heater would (D-06's cell or pocket, REQ-025's stored state), and none is needed while
A1's routes stand. A1's purchases are the owner's spend only when made.

| Row | The exact missing fact | The next bounded engineering action |
|---|---|---|
| LO-01a | the enclosure's conductance, lid open and closed with fans (at least 1.666 W/K); BANK-R1, F2's body, the gauge's ADC and gradient terms | T-H1 on the prototype; BANK-R1 by board B's owner |
| LO-01d | a thermoelectric module's maker sheet at 0.76 to 7.87 W of cold-side load, the input's spare power during E3-O, the volume, a sealed path out; F2 (Eaton) | size one module class from a maker's sheet against section 4's loads |
| LO-01e | E5's dwell and ramp profile (TEST-PLAN states only its limits), then as LO-01d | the profile stated by TEST-PLAN's owner, the bound recomputed on it |
| LO-01f | a storage source and cooler at 1.60 to 4.44 W with a sealed path out, or a cell covering +71 C with the redesign; F2 | as LO-01d, with a storage source |
| LO-01g | a primary source's usable energy at -33 C covering 38.1 to 106.1 Wh plus 2.93 to 8.16 Wh per K of margin and its reserve; the thermostat's tolerance; the gradient; a place; its transport classification; F2 at about -30 C | read one lithium primary maker's sheet at -33 C and size it against section 4 |
| LO-01h | the lot's specification revision | the purchase record |

**Possible later changes, none proposed now:** A, a requirement change (the four margin levels shown with the pack out of
the exposure, as REQ-074 and REQ-051's deviations already run them; reserved to the owner by D-29). B, a resource change
(a wide-temperature 18650 with the protection redesign; about USD 42 a pack, 121.0 Wh nominal against 144.7, 16.4 % less
usable; D-06's "about 145 Wh" restated; his spend approval). C, the existing state: FEA-008 open as the session's
obligation, a release gate on those rows, needing no ruling.

## 8. The battery path's other thermal items (`.out` section 6)

- **F2** (Eaton SCF9550-30-05, MAKER ELX1135): operating -20 to +60 C; storage -10 to +40 C below 90 % RH (whether that
  covers a mounted part is not stated). At about the inside air (INFERRED) it is past +60 C at LO-01a's worst corner
  (62.12 C) and at LO-01d to LO-01g. Questions drafted for Eaton (`clarification/eaton-scf9550.txt`, extending Q-E2).
- **U2 (BQ7720700):** its 70 C trip lies somewhere in 62.7 to 77.5 C at the network, so +71 C storage **permits** a
  destructive trip of a fitted pack; it does not make one certain.
- **The gauge's thresholds** (OTC 44.0, OTD 57.5, UTC 1.0, UTD -9.0 C) stay inside REQ-046's windows; none moves. With
  the coupling the block gains a gradient, so the thermistors go on the hottest cells and P14 is re-measured.

## 9. What stays CONDITIONAL, and how each is verified

| Item | Condition | Verification |
|---|---|---|
| LO-01a | the measured conductance at least 1.666 W/K in both lid states (1.3154 W/K for FEA-008's own criterion) | T-H1 with the dummy block, then E3-A, E3-L and E3-H with a thermocouple on every cell |
| LO-01a, the coupling | film and filler figures, board B's underside; the cells only | E3-L with the coupled block; P14 |
| LO-01h | the lot follows Ver. 1.1 | the purchase record; E4-T |
| LO-01g, a separately fed heater | a primary source's usable energy at -33 C, an independent thermostat, the gradient, a place, F2 | the parts' sheets; then E4-S with the pack fitted, a thermocouple on every cell |

## 10. Downstream items (owner by layer; acceptance)

| Owner | Item | Acceptance |
|---|---|---|
| Session (layer 4) | the INCONCLUSIVE routes: E5's profile, LO-01g's primary-source parts, a cooler's sheet, the input's spare power, Samsung's reading and the HL18650V's specification (drafts in `clarification/`) | each route bounded or rejected |
| Layer 6, components | the lot's revision (LO-01h); Eaton on F2; for any cell route, the protection and control redesign | documents filed; the redesign's bounds computed |
| Layer 7, mechanical | the coupling only if T-H1 reads under 1.666 W/K; a primary source's place if LO-01g's separately fed heater is pursued | E3-L, E4-S |
| Layer 8, generator owners | none now; under a cell route, `gen_sch_p.py` (U2, F2) and `pcb_pack_protection.yaml` | the protection suite |
| Layer 9, pre-layout | board P's place (F2 at the air), thermistors on the hottest cells | P13, P14 |
| Prototype bench | T-H1 in both lid states; E3-A, E3-L, E3-H; E4-O; P13 at the cell surface; P14; P15 | each TEST-PLAN pass line |
| Firmware owner | the mat's thermostat on battery (coupling only); an independent thermostat for a self-heating store | E4-O, E4-S |
| Board B's owner | BANK-R1 in `gen_sch_b.py` (E3-L's stage criteria) | E3-L |
| Owner | none asked now | |

## 11. Decisions taken by the session (authority: SESSION, under the owner's standing rule of 26 September 2026)

| Decision | Why the session's | Reversed by |
|---|---|---|
| S1 selected; S2 not recommended; no cell spend proposed | engineering selection within D-06; no requirement changes and no money | the owner choosing B, or a new maker's specification |
| FEA-008 kept as an open engineering obligation, not escalated | no row has every route rejected (check 1, R4) | a row whose every route is rejected on bounded evidence |
| The coupling is a fallback for the cells only | it cannot meet the air criteria, which only the enclosure meets | T-H1 below 1.666 W/K with the cells the binding item |
| An idle pack on an input is held to +60 C | REQ-046's note and REQ-077 read it so | a maker's statement on the rest state |
| The HL18650V's figures are INFERRED | a page, no test conditions or charge state | the signed specification |
| One sheet filed, four held back | each file's terms, read conservatively | the makers' permission |

## 12. Check 1 and how each item is answered

| Item | Change |
|---|---|
| R1, LO-01a's closure | three thresholds kept apart (rating 1.2455, FEA-008's +59 C 1.3154, the complete pass line 1.6664 W/K on shore by the SGP41); lid open added (60.39 C, 60.49 C); the coupling shown against every criterion; failing dependencies listed |
| R2, the screen | rows C03 to C05 and C15 to C19: E3-A's sequence, E3-L's levels, E3-H, E3-T and E3-P with 7.10's full-charge evidence, E4-T, E4-P, P13 |
| R3, the routes | the whole-kit 218 to 452 Wh corrected to the pack's 38.1 to 106.1 Wh (then withdrawn as a feasibility basis, below); LO-01g bounded in three cases on usable energy; E5 bounded on its stated limits, INCONCLUSIVE on its profile; cooling given its loads, balance and needed conductance, INCONCLUSIVE on named inputs; the passive storage rejections bounded (24.6 and 30.3 mm) |
| R4, the framing | reclassified as component limitations and missing evidence; no owner decision; A and B possible later changes, C the existing state |
| R5, option B's protection | the redesign stated as B's entry cost, with U2's variant table read from SLUSEG7D p.3 |
| M1 | the mat's 7.5 W into the cells, 1.0 W regulator loss into the air: 12.44 C and 12.84 C |
| M2 | one-node residuals labelled as such; two-node 0.351 K and 0.301 K printed |
| M3 | +71 C permits a destructive trip, not certain |
| Saft lead | noted as assessed, not held |
| The owner's bounded checks (2 October 2026) | the nominal comparison withdrawn; LO-01g in three cases on usable energy at the stored charge, with the setpoint from UTD and the published cold budget, the reserve, the regulator's loss and the gauge's draw in one boundary; the profiles and acceptance conditions mapped (section 3); the shortlist A1 to A3 with A1 selected; the exact missing facts and next actions (section 7) |

## 13. Files

`l4e10_cell_thermal.py` and `.out` (section 0 reproduces `pwr_budget.out` and `.json`, `pwr_red2.out` and
`hotstop_bounds.out` byte for byte and pins 31 inputs by sha256; section 8 prints the predicates);
`fetch_held_back.py`; `inputs/`; `clarification/` (Topwell, Eaton); `checks/astra-check-l4e10-1.md`; `README.md`. The
tests: `env -C v2/ecad/tools/tests python3 run.py test_l4e10 test_public_hygiene`. No generator, BOM, registry or
Layer 3 file is changed.
