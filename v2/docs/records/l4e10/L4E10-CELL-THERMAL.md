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

- **FEA-008 stays open as an engineering obligation; no owner decision is forced.** A missing cell whose sheet covers the
  levels is a component limitation plus missing feasibility evidence, not a contradiction between owner requirements
  (D-29, D-36, `l3r2.yaml` cell_provenance). Every open row keeps at least one route that is INCONCLUSIVE on named facts;
  no row has every route rejected on bounded evidence, the only condition that would warrant the owner's decision.
- **LO-01a (in use, +40 C) is CONDITIONAL on the enclosure's measured conductance.** The cell rating alone holds from
  1.2455 W/K on the pack, FEA-008's own criterion with the +59 C abort from 1.3154 W/K, the complete E3-A and E3-L pass
  line from **1.6664 W/K** (the SGP41's +55 C inside air on shore). T-H1 must read at least 1.666 W/K in both lid states.
  The pocket coupling lowers the cells to 58.64 C on the pack, but on shore they reach 59.30 C (past the +59 C abort) and
  the air 63.42 C: a partial fallback for the cells, never a substitute for the conductance.
- **LO-01h is CONDITIONAL on procurement** (Ver. 1.1 covers both storage rows). **LO-01b and LO-01c have no collision.**
- **LO-01d to LO-01g are OPEN, each with its next bounded action done where makers' documents allow** (section 4b):
  - LO-01g: one lithium primary sized from Saft's LSH 20 sheet: 5S strings driving the existing mat direct, 10 to 20
    cells (1.0 to 2.0 kg, 0.54 to 1.07 L of cells), 25.8 to 35.9 h of hold with a 26 % reserve kept; they cannot sit in
    the pocket (0.056 to 0.121 L of room), so Layer 7's free volume is the missing fact, with F2 at about -30 C a
    separate obstacle. The pack-fed heater stays rejected on the gauge's shutdown path alone; its durations are model
    sensitivities.
  - E5: the profile is MIL-STD-810H Method 507.6 Procedure II (a 23 C conditioning, ten cycles 30-60-60-30-30 C, a return
    to 23 C); latent storage (Rubitherm RT57HC) fits only marginally at the best corner (0.102 L) and not at the worst
    (7.1 L).
  - LO-01d: latent storage keeps the cells under +60 C at the best corner (0.012 L) but not at the worst (0.203 L), and the
    complete E3-O pass is rejected: the cells must stay under H1's no-act 55.79 C with the chamber at 55 C, a 0.79 K window
    against a 3 K melting area. LO-01f: latent storage needs 0.275 to 1.175 L: rejected within the pocket.
  - Powered cooling, corrected: rejecting into the sealed case puts the air at 86.4 to 144.8 C at the worst corners
    (rejected there); at the best corners and for a higher COP it stays INCONCLUSIVE on a cooler's sheet.
- **Selected: A1, the Samsung INR18650-35E as ruled (D-06) with local thermal management; no spend now.** No cell change
  is taken, and no approved constraint is changed.

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

Every required charging, discharging, transport and storage condition with its duration, configuration, charge state and
recovery. A rejection is kept only where physics or a bounded figure gives it; a route with a missing input is
INCONCLUSIVE. Where TEST-PLAN states no charge state (E3-A, E3-L, E3-H, E3-O, E5, E4-T's transport case, E4-P), that
charge state is a named missing input; the thermal figures do not depend on it.

| Id | Condition | Ambient, duration, configuration | Limit (MAKER) | Power | Gap | Result |
|---|---|---|---|---|---|---|
| C01 | discharge in use, lid closed (E3-L at +40 C) | +40 C, 4 h, the heat stage, pack fitted | -10 to 60 C surface; +59 C abort | the pack | 3.29 K at the bound's worst corner; none on 32.53 | CREDIBLE, CONDITIONAL on T-H1 (the face plate gives no gain: the block sits under board B and the plate, the air's main exit, runs near the air) |
| C02 | on shore at the hot edge (E3-L's second half, E3-A's 2 h on shore, E5-A) | +40 C, lid open or closed, pack idle | +60 C (REQ-046's note, REQ-077) | the input | 2.12 K lid closed; lid open 60.49 C air, 60.39 C cells on the pack | CREDIBLE, CONDITIONAL on T-H1, both lid states |
| C03 | E3-A's +25 C point, 4 h, three loaded modules on shore | +25 C, the stage C1 selects | +60 C; T3 42 C | the input | none for the cells; charging recorded | NO GAP |
| C04 | E3-L's +20 C and +30 C levels; E3-L started once with the lid already closed, entering the reduced mode once the lid is read | 4 h each, on the pack then on shore | +60 C; SGP41 +55 C air | pack, input | none: cells 52.04 C (reduced mode) and 53.29 C (heat stage) | NO GAP |
| C05 | E3-H's stepped run (protection test): at +40 C lid closed held until the hot stop acts or its 4 h pass; repeated with the sensor controller held in reset (TMP117 at +55.0 C shed, +56.0 C shutdown, released at +45.0 C); restart once the hottest cell reads +46.5 C or less and 30 minutes have passed, after H2 by MAIN | from +40 C by 2 K an hour to at most +55 C | no cell at +59 C before H1 and H2 | input, pack | none for the cells; whether H2 is reached depends on the minimum load (P15 forces it) | NO GAP for the cells |
| C06 | discharge, cold edge (E4-O) | -20 C, 4 h, warm | -10 C floor | pack or input | none (-5.52 C) | NO GAP |
| C07 | start from a pack below about -10 C | the start | -10 C floor | input or warming | out of scope (D-02d) | NOT REQUIRED |
| C08 | charging, hot | -20 to +40 C | 0 to 45 C; T3 42 C | the input | none by requirement | NO GAP |
| C09 | charging, cold (mat before charge) | -20 C, warm-up then charge | UTC 1.0 C, panel hold +3 C | the input (7.5 W into the cells, 1.0 W regulator loss into the air) | the mat lifts the idle cells to 12.44 C | CREDIBLE (existing mat) |
| C10 | +55 C operating margin (E3-O) | +55 C, 4 h, on an input, pack fitted | +60 C; H1 +56.5 C; "no shutdown" | the input | 1.63 to 14.22 K | OPEN: passive design and latent storage rejected against the complete pass; cooling and a cell INCONCLUSIVE |
| C11 | E5's humid cycle (Method 507.6 Procedure II: 23 C conditioning, ten 24 h cycles 30-60-60-30-30 C, return to 23 C; checks near the ends of cycles 5 and 10) | 95 % RH, on an input, the kit logging, pack fitted | +60 C | the input | at least 6.63 K | OPEN: latent storage marginal at the best corner; cooling and a cell INCONCLUSIVE |
| C12 | +71 C storage margin (E3-S) | +71 C, 24 h, stored at 30 %, gauge in shutdown | storage 1 month to 60 C at 30 % | **zero** (a separate source only if added) | 11 K | OPEN: the calculated insulation and latent storage rejected within the pocket; cooling and a cell INCONCLUSIVE |
| C13 | -33 C storage margin (E4-S) | -33 C, 24 h, stored | floor -20 C; discharge floor -10 C | **zero** (a separate primary only if added) | 13 K; 33 K | OPEN: a pack-fed heater rejected on the shutdown path; a primary-fed heater sized, INCONCLUSIVE on its place, a thermostat and F2 |
| C14 | storage in the envelope | -20 to +45 C 3 months; -20 to +25 C a year | Ver. 1.1 rows at 30 % | zero | none (Ver. 1.1) | CREDIBLE (procurement) |
| C15 | E3-T stored and transport soak | +58 C set point +-2 K, 24 h; ex-factory (storage) or its charge (transport) | 1 month to 60 C at 30 %; full charge: 20 days at 60 C, 95 % recovered (7.10) | zero | none: the top tolerance reaches the limit | NO GAP |
| C16 | E4-T cold soak; return: full function after return to 25 C, capacity within 5 % of its value before (PROVISIONAL) | the governing floor, 24 h | -20 C at 30 %; F2's floor -20 C | zero | none for the cells; F2's storage line open | NO GAP for the cells |
| C17 | E3-P: pack alone, armed, full charge, then 2 A from +58 C | +58 C +-2 K, 24 h, then until the gauge stops it | 7.10's full-charge storage; discharge to 60 C | the test load | none by construction: OTD must stop the discharge before any cell exceeds +60 C and recover at or below +52.5 C; no immediate refusal is claimed (the reading may be low) | NO GAP |
| C18 | E4-P: pack alone, cold; recovery as E4-T | as E4-T, 24 h | -20 C at 30 %; no cold recovery figure | zero | none at the ex-factory state | NO GAP |
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
- **The pocket coupling (a partial fallback for the cells).** East face to the east wall through a gap filler in the
  9.68 mm M4b gap (k 1.0 W/mK, ASSUMPTION), base to the floor through the heater mat (1.5 mm, k 0.2 W/mK, ASSUMPTION),
  four faces in the air (5 to 15 W/m2K), W4's films (INFERRED): f = 0.824 to 0.485. At LO-01a's worst corner on the pack
  the cells fall to 58.64 C (inside +60 C and the +59 C abort) but stay over H1 (by 2.14 K) and the air stays 61.94 C;
  **on shore the cells reach 59.30 C, past the +59 C abort, and the air 63.42 C.**
- **Cold end, MODELED.** With the coupling the cells at -20 C fall to -10.24 C; holding -8.0 C takes 0.38 W into the
  cells, 0.44 W from the battery (1.0 % of PS-IDLE-SPEC). Charging at -20 C: the mat's 7.5 W into the cells (MAKER) and
  its regulator's 1.0 W into the air lift the idle cells to 12.44 C (12.84 C with the coupling), over the +3 C hold.
- **Storage hold times, INFERRED.** After 24 h the cells lag the ambient by 0.21 K (hot) and 0.18 K (cold) as one node,
  0.351 K and 0.301 K as two nodes (the slowest kit: 9340 J/K beside the cells' 660 J/K, 0.70 W/K to ambient, 0.1481 W/K
  to the cells). The first issue's 218 to 452 Wh heated the whole kit; the pack alone is below.
- **The calculated insulation, bounded.** For 24 h of hold from the most favourable start, with the cells' own heat
  capacity, the pack's coupling must fall under 0.0207 W/K (+71 C) or 0.0173 W/K (-33 C), that is 24.6 mm or 30.3 mm at
  k 0.02 W/mK (ASSUMPTION) against 0.77 to 2.66 mm of room: that arrangement is rejected. Added sensible or latent
  storage is bounded separately (4b).
- **LO-01g, the -33 C storage margin, in three cases** (ambient and cell temperatures kept apart; one calculation
  boundary at the source's terminals; series path 0.1222 to 0.3400 W/K). The nominal comparison of 38.1 to 106.1 Wh with
  the pack's 144.7 Wh is **withdrawn** as a feasibility basis.
  - **(i) a warm pack kept inside its limits, fed by the pack.** The heater discharges the cells, so the setpoint is
    UTD's -9.0 C reading plus the published 0.86 K cold budget, -8.14 C: 3.37 to 9.30 W at the pack's terminals; at the
    fast corner the 8.20 W into the cells exceeds the mat's own 7.5 W at 12 V, a further inability. The figures 11.9 to
    28.9 Wh and 1.3 to 8.6 h are **model sensitivities**, not usable energy (capacity x nominal voltage x ageing x charge
    x an assumed cold factor; MAKER 7.5's point is a full charge, a 3 h temperature change and 3.4 A to 2.65 V). Missing:
    the terminal energy over the partial-charge voltage curve, the cutoff, the temperature history. **The rejection rests
    on the shutdown path alone:** in REQ-025's stored state "the device turns off the FETs" (MAKER, SLUUAQ3A 5.4.2).
  - **(i) a warm pack kept inside its limits, fed by a separate primary battery:** sized in 4b.
  - Recovery: E4-O follows E4-S; a pack held at the -20 C floor is below the -10 C discharge floor, so E4-O starts from an
    input or after warming, as TEST-PLAN and D-02d already allow.
  - **(ii) a pack already cold-soaked:** below -20 C it has left its storage row and no heater undoes that; between -20
    and -10 C the pack may not discharge and the gauge holds its FET off below UTD (recovery -4.0 C), so only a separate
    source can rewarm it, 0.133 to 0.183 Wh per K plus losses.
  - **(iii) heating lost or spent:** the cells pass -20 C 0.30 to 1.09 h after a pack-fed hold stops, at once for a hold
    at the floor, so the setpoint's margin must cover depletion; nothing records the event in shutdown (a named item).
  - Cool-down credit, ASSUMPTION (E4-S's start state is not stated; from the sheet's 23 C): 1.57 to 4.57 h before the
    pack reaches -8.14 C, 2.58 to 7.27 h before -20 C.
- **Powered cooling, corrected (check 2).** Heat pumped out of the block into the inside air returns to the air it came
  from, so the air gains only the cooler's input Q_c/COP; an equilibrium exists wherever G_e > G_b/COP. With COP 0.5 to
  1.0 (ASSUMPTION): at the worst corners of E3-O and E5 the air reaches **86.4 to 144.8 C**, past every part limit of
  OPERATING-ENVELOPE.md section 2: rejected into the sealed case there. At the best corners the cells can be held for
  0.86 to 3.44 W of input, the air 0.70 to 1.48 K above its uncooled value (which already passes F2 and the SGP41). Sent
  out of the case instead, the cooler needs 0.051 to 1.009 W/K of path and the pack's own skin path is 0.054 to 0.090 W/K
  (E3-O's best corner only). INCONCLUSIVE at the best corners and for a higher COP: a cooler's sheet, the input's spare
  power and the volume are missing.
- **PWR-F12 and P13, MODELED.** 18 A for 60 s from +55 C warms the cells 1.37 to 3.24 K (to 56.37 to 58.24 C). P13's hour
  at 10 A puts 4.67 to 8.00 W into the cells, 10.5 to 54.0 K over the block's air, so its "hot limit" must be held at the
  cell surface.

## 4b. The open rows' next bounded actions, from makers' documents and without a purchase (`.out` 3n)

The block's room beyond the 1.0 mm minimums is 0.056 L at the worst stack and 0.121 L as designed (INFERRED, CASE-MARGINS
and SHORTLIST). Latent storage is Rubitherm RT57HC (MAKER, filed under `v2/vendor/battery/pcm/`): melting area 55 to 58
C, 240 kJ/kg +-7.5 % (latent and sensible over 49 to 64 C), 0.9 kg/l solid; taken **favourable to the material** (all
258 kJ/kg latent at 58 C, solid density, no container, perfect contact), so a "does not fit" holds and a "fits" stays
CONDITIONAL. A two-node enthalpy model (the kit and the block) runs each profile.

- **(a) LO-01g, one lithium primary from its maker's sheet** (Saft LSH 20, Li-SOCl2, D size, Document 31015-2-0426,
  held back): 13 Ah under 14 mA at +20 C, 3.6 V, at most 1.8 A continuous, -60 to +85 C, 33.4 x 61.31 mm, 100 g, about
  3.8 g of lithium, UN 3090 and UN 3091, self-discharge under 3 % a year; its curves are typical, not minimum (the
  maker's own words), read by eye at -40 C and -20 C (INFERRED). One boundary: the string drives the existing mat
  (19.2 ohm) through a thermostat, no regulator. Setpoint: the -20 C floor plus thermostat 3 K + gradient 2 K + margin
  2 K (ASSUMPTION, no thermostat part held); reserve kept: 20 % typical against minimum + 6 % self-discharge over two
  years (ASSUMPTION). 4S cannot carry the fast corner (its on-power under the 6.80 W average); **5S on the -40 C curve:
  10 to 20 cells (2 to 4 strings), 1.0 to 2.0 kg, 0.54 to 1.07 L of cells, 25.8 to 35.9 h with the reserve kept, duty at
  most 0.72.** The cells cannot sit in the pocket (0.121 L at most): Layer 7's free volume elsewhere in the case is the
  missing fact. F2 sits at about -30 C, below its -20 C floor: a separate obstacle (Eaton, or the heated zone over board
  P). Sequence: the pack to its ex-factory charge and the gauge to shutdown (REQ-025); the storage heater armed; its
  thermostat on the coldest cell connects the string to the mat, isolated from the kit's 12 V feed (a circuit item for
  the generator owners); the pack never discharges; disarmed at the end of storage. Scope: E4-S's 24 h at -33 C from a
  warm stored kit; not a cold start, not in use.
- **(b) E5's profile.** TEST-PLAN cites "507" with Procedure II's levels; MIL-STD-810H Method 507.6 (transcribed at
  `v2/vendor/standards/mil-std-810h-method-507-6.md`) gives a 23 C conditioning for at least 24 h, ten 24 h cycles (0 h
  30 C, 2 h 60 C, 8 h 60 C, 16 h 30 C, 24 h 30 C) at 95 % RH, operational checks near the ends of the fifth and tenth
  cycles, then a return to 23 C until stable; the cycle's mean is 43.75 C. The air's mean is 50.82 C (best) to 64.24 C
  (worst); without storage the cells peak at 66.72 to 79.63 C. They stay under +60 C through the conditioning and ten
  cycles with **0.092 kg (0.102 L) at the best corner** (between the worst-stack and the designed room: marginal) and
  **6.41 kg (7.12 L) at the worst** (no fit). INCONCLUSIVE on the conductance and the built room; which procedure E5 means
  is the plan owner's to confirm.
- **(c) LO-01d, E3-O's 4 h at +55 C from a kit stabilised at the chamber.** Without storage the cells peak at 61.26 C
  (best) and 72.42 C (worst); under +60 C with **0.011 kg (0.012 L) at the best corner, inside the room, and 0.183 kg
  (0.203 L) at the worst, outside it.** The complete E3-O pass ("no shutdown") needs the cells under H1's no-act limit of
  55.79 C with the chamber already at 55 C: a **0.79 K window against the material's 55 to 58 C melting area**, so latent
  storage is rejected against the present hot-stop ladder.
- **LO-01f, E3-S's 24 h at +71 C from the storage envelope's cold edge:** under +60 C with 0.248 kg (0.275 L) at the best
  corner and 1.057 kg (1.175 L) at the worst, both beyond the room: rejected within D-06's pocket on figures favourable
  to the material. **LO-01g:** no maker's sheet of a material freezing between -20 and -10 C is held: INCONCLUSIVE.

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
