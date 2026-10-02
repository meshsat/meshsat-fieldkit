# L4-E10: the cell and thermal design of the battery path against the temperature requirements (FEA-008)

MESHSAT-1357, layer 4 task L4-E10, 2 October 2026, revised the same day after the collaborator's checks 1 and 2
(`checks/astra-check-l4e10-1.md` and `-2.md`, both NOT YET; section 12 maps each item to its change) and the owner's
instruction of the same day (a bounded comparison of complete approaches, the least complex one recommended). **Prototype
design, desk arithmetic: nothing has been bought, built, powered or measured, and no kit has been field deployed.** Every
figure comes from `l4e10_cell_thermal.out` (the script `l4e10_cell_thermal.py` reproduces it byte for byte) and carries
its class: MAKER (a maker's document, clause named), MODELED (the tree's power and thermal model,
`records/rv-pwr/pwr_budget.py` and `records/hc2/pwr_red2.py`, imported unchanged and reproduced first), INFERRED (method
stated), ASSUMPTION (a figure no held document gives), CONDITIONAL (holds only on a stated condition).

## 1. The answer in short

- **Recommended: approach (II), a wide-temperature 18650 (the HL18650V class) in D-06's 4S3P with the protection and the
  gauge re-derived.** Of the three complete approaches compared on the same profiles (section 6) it is the only one with
  no row rejected and no added energy storage, and it adds no subsystem. It is a recommendation, not taken: no cell
  change and no spend now. **FEA-008 stays open**: a defensible next step does not close it.
- **Its supported margins at the conditioned corner** (the enclosure LO-01a needs anyway, 1.666 W/K, every other
  parameter at its worst): E3-O's cells 68.86 C, 11.14 K under the page's +80 C and 6.93 K under the re-derived H1;
  E5's 74.73 C, 5.27 K and 1.06 K; E3-S's +71 C, 9.00 K; E4-S's -33 C, 7.00 K inside -40 C; U2 moved to the 83 C
  BQ7720704, whose lowest trip (75.7 C, INFERRED) clears every level by at least 0.97 K. Energy: 90.4 Wh usable against
  108.1 (16.4 % less), 121.0 Wh nominal.
- **The architecture-level uncertainty:** the HL18650V's figures are a maker's product page (Yichun Topwell Power), not a
  signed specification, and no 18650 with a signed specification covering +71 C and -33 C storage was found. If the
  specification does not confirm a row, that row falls back to (III), which has no in-pocket route for LO-01f and needs
  added energy storage for LO-01g.
- **(I), the 35E with local thermal management, does not qualify:** its storage rows (E3-S, E4-S) need a second energy
  store, and with the corrected cooler balance its hot rows rest on a cooler in the sealed case of 8.18 to 35.21 W at the
  conditioned corner, lifting the inside air 4.9 to 21.1 K onto and past the +70 C parts (INCONCLUSIVE); latent storage
  needs 0.162 L (E3-O) and 1.489 L (E5) against at most 0.087 L. **(III)**, latent storage and a primary-fed storage
  heater, is rejected at LO-01d to LO-01f, and its primary battery (10 to 20 Saft LSH 20 cells, 470 to 940 Wh nominal,
  3.2 to 6.5 times the pack) is added energy storage whose compatibility with D-06 is the owner's.
- **A finding outside FEA-008, common to every approach:** at the conditioned corner the uncooled inside air settles at
  70.00 C in E3-O and tends to 75.00 C in E5's 60 C dwell, at or past the +70 C parts (the SA868, the AW7915-AED cards,
  the LimeSDR, the Xenarc); it is named for the kit's thermal owner (section 10).
- **No owner decision is forced** (no row has every route rejected). The recommendation needs the owner for two things
  outside the session's authority: (1) now, sending the drafted request for the signed specification
  (`clarification/topwell-hl18650v.txt`); (2) once it confirms the rows, approving the cell change inside D-06's 4S3P,
  which restates D-06's "about 145 Wh" to about 121 Wh nominal and, with the cell, the cell-derived numbers of REQ-046
  and REQ-077, and its spend (about USD 42 a pack at the marketplace price).
- **U-01 by mode (section 14, 2 October 2026):** the HL18650V's charge, discharge and storage rows each with their
  condition and class (all MAKER-PAGE; the cold charge row garbled, no pulse, cold capacity, termination, storage charge
  state or recovery stated); the drafted charge ranges for the 4S3P (0.84 A to 16.40 V from -9 C, 1.68 A from 1 C, the
  drawn 3.00 A from 11 C); usable energy 90.2 Wh at +25 C against the 35E's 107.9 Wh, the cold end a bracket; the threshold
  of each row at which the architecture moves.
- **U-01 consolidated (section 15, 2 October 2026; restated after Astra's B5):** the Saft MP 176065 xtd as a 4S1P pack in
  D-06's pocket is supported on published manufacturer evidence for its TEMPERATURE WINDOWS (charge -30 to +85 C,
  discharge -40 to +85 C, storage allowable -40 to +85 C). Current and temperature together (10 A continuous, 18 A for
  60 s, the protection's 20 A for 2 s at the modelled cell temperatures; charge below 0 C) and the storage dwell and
  recovery are AWAITING Saft or a limited sample qualification (section 15g). The route is not yet adoptable: those, the
  fit along the axis and the owner's approval (about 82 Wh nominal, 53.5 to 55.1 Wh usable) remain. LO-01a's complete
  pass and LO-01e rest on T-H1 for every cell. The pocket's room is corrected to 0.0865 L (section 15a).
- **The battery comparison (section 16, the owner's amendment of 2 October 2026):** on one boundary the approved 35E pack
  gives 144.72 Wh nominal and 107.9 Wh usable (2.52 h); the Saft route 81.76 Wh nominal and 53.5 to 58.8 Wh usable (1.25 to
  1.37 h). The 43.5 % cut compares the 35E's minimum with the Saft's typical; like for like it is 45.1 %. The evidence
  supports the Saft route's cell limits, not yet its adoption: the fit mock-up, the 18 A peak and T-H1 stay awaited, and the
  owner's approval is required.
- **The thermal architecture criterion (criterion 1) is not met by this record.** Every LO row now has a route that is not
  rejected; LO-01a stays CONDITIONAL on T-H1 (at least 1.666 W/K in both lid states) for every approach, LO-01h on the
  lot, and LO-01d to LO-01g rest on a product page until the signed specification arrives.

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
| C10 | +55 C operating margin (E3-O) | +55 C, 4 h, on an input, pack fitted | +60 C; H1 +56.5 C; "no shutdown" | the input | 1.63 to 14.22 K | OPEN: (II) recommended, CONDITIONAL (6.93 K under the re-derived H1); passive design and latent storage rejected; cooling INCONCLUSIVE with its cost to other parts |
| C11 | E5's humid cycle (Method 507.6 Procedure II: 23 C conditioning, ten 24 h cycles 30-60-60-30-30 C, return to 23 C; checks near the ends of cycles 5 and 10) | 95 % RH, on an input, the kit logging, pack fitted | +60 C | the input | at least 6.63 K | OPEN: (II) recommended, CONDITIONAL (1.06 K under the re-derived H1); latent storage rejected within the pocket (section 15a); cooling INCONCLUSIVE with its limits named |
| C12 | +71 C storage margin (E3-S) | +71 C, 24 h, stored at 30 %, gauge in shutdown | storage 1 month to 60 C at 30 % | **zero** (a separate source only if added) | 11 K | OPEN: (II) recommended, CONDITIONAL (9.00 K under the page's +80 C); the calculated insulation and latent storage rejected within the pocket; cooling needs a second energy store |
| C13 | -33 C storage margin (E4-S) | -33 C, 24 h, stored | floor -20 C; discharge floor -10 C | **zero** (a separate primary only if added) | 13 K; 33 K | OPEN: (II) recommended, CONDITIONAL (7.00 K inside the page's -40 C); a pack-fed heater rejected on the shutdown path; a primary-fed heater is added energy storage under D-06 |
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
  boundary at the source's terminals; series path 0.1222 and 0.3400 W/K). The nominal comparison of 38.1 to 106.1 Wh with
  the pack's 144.7 Wh is **withdrawn** as a feasibility basis.
  - **(i) a warm pack kept inside its limits, fed by the pack.** The heater discharges the cells, so the setpoint is
    UTD's -9.0 C reading plus the published 0.86 K cold budget, -8.14 C: 3.37 to 9.30 W at the pack's terminals; at the
    fast corner the 8.20 W into the cells exceeds the mat's own 7.5 W at 12 V, a further inability. The figures 11.9 to
    28.9 Wh and 1.3 to 8.6 h are **model sensitivities**, not usable energy (capacity x nominal voltage x ageing x charge
    x an assumed cold factor; MAKER 7.5's point is a full charge, a 3 h temperature change and 3.4 A to 2.65 V). Missing:
    the terminal energy over the partial-charge voltage curve, the cutoff, the temperature history. **The rejection rests
    on the shutdown path alone:** in REQ-025's stored state "the device turns off the FETs" (MAKER, SLUUAQ3A 5.4.2).
  - **(i) a warm pack kept inside its limits, fed by a primary battery:** added energy storage under D-06, bounded in 4b,
    not adopted.
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
  out of the case instead, the cooler needs 0.051 to 0.525 W/K (E3-O, COP 1.0) up to 0.150 to 1.009 W/K (E5, COP 0.5)
  of path, and the pack's own skin path is 0.054 to 0.090 W/K (E3-O's best corner only). INCONCLUSIVE at the best corners and for a higher COP: a cooler's sheet, the input's spare
  power and the volume are missing; at the conditioned corner (4c) it lifts the air onto the +70 C parts. Fed by the pack rather than the
  input, it would cut the 2.52 h at PS-IDLE-SPEC to 2.34 to 2.47 h (best corner) or 1.39 to 2.12 h (conditioned corner).
- **PWR-F12 and P13, MODELED.** 18 A for 60 s from +55 C warms the cells 1.37 to 3.24 K (to 56.37 to 58.24 C). P13's hour
  at 10 A puts 4.67 to 8.00 W into the cells, 10.5 to 54.0 K over the block's air, so its "hot limit" must be held at the
  cell surface.

## 4b. The open rows' bounded measures, from makers' documents and without a purchase (`.out` 3n)

The block's room beyond the 1.0 mm minimums is 0.056 L at the worst stack and 0.087 L as designed (0.0865 L, corrected in section 15a; INFERRED, CASE-MARGINS
and SHORTLIST). Latent storage is Rubitherm RT57HC (MAKER, filed under `v2/vendor/battery/pcm/`): melting area 55 to 58
C, 240 kJ/kg +-7.5 % (latent and sensible over 49 to 64 C), 0.9 kg/l solid; taken **favourable to the material** (all
258 kJ/kg latent at 58 C, solid density, no container, perfect contact), so a "does not fit" holds and a "fits" stays
CONDITIONAL. A two-node enthalpy model (the kit and the block) runs each profile.

- **(a) LO-01g, a lithium primary for a storage heater: ADDED ENERGY STORAGE, a proposal under D-06, bounded and not
  adopted** (Saft LSH 20, Li-SOCl2, D size, Document 31015-2-0426, held back): 13 Ah under 14 mA at +20 C, 3.6 V, 47 Wh,
  at most 1.8 A continuous, -60 to +85 C, 33.4 x 61.31 mm, 100 g, about 3.8 g of lithium, UN 3090 and UN 3091. One
  boundary: the string drives the existing mat (19.2 ohm) through a thermostat, no regulator. Setpoint: the -20 C floor
  plus thermostat 3 K + gradient 2 K + margin 2 K (ASSUMPTION, no thermostat part held); reserve kept: 20 % typical
  against minimum + 6 % self-discharge over two years (ASSUMPTION). 4S cannot carry the fast corner (its on-power under
  the 6.80 W average); **5S on the -40 C curve: 10 to 20 cells (2 to 4 strings), 1.0 to 2.0 kg, 0.54 to 1.07 L of
  cells, 25.8 to 35.9 h with the reserve kept, duty at most 0.72.**
  - **Against D-06:** those cells hold 470 to 940 Wh nominal, 3.2 to 6.5 times the pack's 144.7 Wh, and 38 to 76 g of
    lithium: a second energy store beside D-06's one pack. Calling it a heater supply does not settle its compatibility
    with D-06 (one 4S3P pack, internal storage, no external battery); adopting it is the owner's.
  - **Output at the actual load and temperature:** 704 mA on, 2.703 V a cell, 4.39 Ah, 9.5 W into the mat on the -40 C
    curve (742 mA, 4.82 Ah, 10.6 W at the hold's air), from the maker's curves, which are typical, not minimum (its own
    words), read by eye (INFERRED).
  - **Startup:** the pulse figures hold "after initial stabilisation" and no figure is given at -33 C after storage
    (missing). **Ageing and self-discharge:** under 3 % a year at +20 C, typical values "relative to cells stored up to
    one year at + 30°C max", with storage recommended at +30 C at most against the kit's envelope to +45 C, E3-T's +58 C
    and E3-S's +71 C: its energy after storage in the kit is unsupported until Saft answers. **Replacement:** as a set
    ("Do not mix new and used cells") every two years (ASSUMPTION). **Controls:** a thermostat on the coldest cell,
    independent of the gauge. **Unintended charging:** "Do not recharge", so the string reaches the mat only through a
    blocking path the kit's 12 V feed cannot back-drive (two series diodes, a circuit draft). **Fit:** outside the pocket
    (0.087 L at most), so Layer 7's free volume. F2 sits at about -30 C, below its -20 C floor (Eaton).
  - **The three cases:** (i) keeping a warm pack is its job; (ii) a pack already cold-soaked is rewarmed only from this
    store, 0.133 to 0.183 Wh per K; (iii) lost control: with the store spent or the thermostat failed open the cells pass
    -20 C 0.30 to 1.09 h later; failed closed, the mat runs at 9.5 W, the cells settle at -5.0 to 44.8 C (inside their
    storage row) and the store is spent in 12.5 to 24.9 h.
  - Sequence: the pack to its ex-factory charge and the gauge to shutdown (REQ-025); the heater armed; the thermostat
    connects the string to the mat; the pack never discharges; disarmed at the end of storage. Scope: E4-S's 24 h at
    -33 C from a warm stored kit; not a cold start, not in use.
- **(b) E5's profile.** TEST-PLAN cites "507" with Procedure II's levels; MIL-STD-810H Method 507.6 (transcribed at
  `v2/vendor/standards/mil-std-810h-method-507-6.md`) gives a 23 C conditioning for at least 24 h, ten 24 h cycles (0 h
  30 C, 2 h 60 C, 8 h 60 C, 16 h 30 C, 24 h 30 C) at 95 % RH, operational checks near the ends of the fifth and tenth
  cycles, then a return to 23 C until stable; the cycle's mean is 43.75 C. The air's mean is 50.82 C (best) to 64.24 C
  (worst); without storage the cells peak at 66.72 to 79.63 C. They stay under +60 C through the conditioning and ten
  cycles with **0.092 kg (0.102 L) at the best corner**, over the designed room's 0.087 L, and **6.41 kg (7.12 L) at the
  worst**: no fit at any corner, so latent storage is rejected for E5 within the pocket (section 15a); which procedure E5
  means is the plan owner's to confirm.
- **(c) LO-01d, E3-O's 4 h at +55 C from a kit stabilised at the chamber.** Without storage the cells peak at 61.26 C
  (best) and 72.42 C (worst); under +60 C with **0.011 kg (0.012 L) at the best corner, inside the room, and 0.183 kg
  (0.203 L) at the worst, outside it.** The complete E3-O pass ("no shutdown") needs the cells under H1's no-act limit of
  55.79 C with the chamber already at 55 C: a **0.79 K window against the material's 55 to 58 C melting area**, so latent
  storage is rejected against the present hot-stop ladder.
- **LO-01f, E3-S's 24 h at +71 C from the storage envelope's cold edge:** under +60 C with 0.248 kg (0.275 L) at the best
  corner and 1.057 kg (1.175 L) at the worst, both beyond the room: rejected within D-06's pocket on figures favourable
  to the material. **LO-01g:** no maker's sheet of a material freezing between -20 and -10 C is held: INCONCLUSIVE.
- **Each latent store's history (no fresh store is assumed):** E3-O starts from the kit stabilised at +55 C with the
  material solid at the bottom of its melting area (favourable: partial melting below 55 C is not counted); E5's store is
  carried through the conditioning and all ten cycles in one run, refreezing only as the cycle's 30 C part allows; E3-S
  starts at the storage envelope's cold edge (favourable). Once a store is spent the cells follow the no-storage
  response (E3-O 61.26 to 72.42 C, E5 66.72 to 79.63 C, E3-S 70.65 to 71.00 C). Between required exposures a store
  resets only below 55 C, which each test's own return to ambient provides; a kit taken from one hot exposure to the next
  without it starts with a spent store.

## 4c. The conditioned corner (`.out` 3o)

Every approach carries LO-01a's condition, T-H1 reading at least 1.666 W/K in each lid state. With the kit's conductance
at that floor and every other parameter at its worst (the heat stage on shore, the lowest heat capacities, the fastest
block), on the same profiles as 4b (MODELED): E3-O's air settles at 70.00 C and the cells peak at 68.86 C in the 4 h;
E5's air averages 58.75 C over the cycle and the cells peak at 74.73 C. Here (I)'s cooler into the sealed case takes
8.18 to 25.69 W (E3-O, COP 1.0 to 0.5) and 11.21 to 35.21 W (E5) and lifts the air to 74.9 to 96.1 C, 4.9 to 21.1 K over
the uncooled 70.00 C (E3-O) and 75.00 C (E5's 60 C dwell), onto and past the +70 C parts of OPERATING-ENVELOPE.md
section 2 (the SA868, the AW7915-AED cards, the LimeSDR, the Xenarc) and at COP 0.5 the CM5's +85 C: INCONCLUSIVE on the
input's spare power and on that cost to other functions. Latent storage needs 0.162 L (E3-O) and 1.489 L (E5) against
at most 0.087 L: rejected. Near the best corner (3.30 W/K with the other parameters favourable) 0.86 to 3.44 W of input
holds the cells.

**Outside FEA-008 and common to every approach:** at this corner the uncooled air settles at 70.00 C in E3-O and tends
to 75.00 C in E5's 60 C dwell, at or past the +70 C parts' limits. It is a finding for the kit's thermal owner (section
10), not a battery path item, and it does not separate the three approaches.

## 5. The cells, alongside and beyond the held set (`.out` sections 4 and 4c)

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
| Unit price | USD 8.25 | USD 6.99 | USD 3.50 (a marketplace seller) |

**Beyond the held set** (the makers' own published lines, `inputs/cells-beyond-held-2026-10-02.json`):
- **LiFePO4, Lithium Werks APR18650M1B** (MAKER product page; its data sheet sits behind a registration form): 3.3 V,
  1.15 Ah minimum, 3.96 Wh, discharge -30 to 60 C, charge 0 to 60 C, storage -40 to 70 C. As 4S3P: 47.5 Wh nominal
  (-67 %) at 13.2 V with a 3.6 V charge a cell, so the charger's voltage, the gauge's chemistry and U2's thresholds all
  change; it covers LO-01g but no hot margin: set aside.
- **Lithium titanate, Toshiba SCiB** (MAKER brochure, held back): prismatic cells from 2.9 Ah (W63 x D14 x H97 mm),
  2.3 and 2.4 V, "as low as -30°C": not an 18650, and 4S would sit near 9.6 V: set aside.
- **UltraXel HL18650T** (MAKER flyer, images only, held back): 1950 mAh minimum, discharge -40 to 85 C, no storage rows;
  its text claims "> 90%" recovery after 1000 h at 80 C while its own chart (read by eye) shows 1.51 of 2.07 Ah (73 %)
  after 1120 h at 80 C and 4.1 V; 84.2 Wh as 4S3P (-42 %): set aside, a second maker's statement of the class's range.
- No 18650 with a maker's signed specification covering +71 C and -33 C storage was found; the HL18650V's page carries
  the class's only stated storage rows. LG HG2 and Molicel P28A were read and set aside earlier (their own 60 C limits).

## 6. One bounded comparison of three complete approaches (`.out` 4d)

The same profiles for all three: LO-01a at +40 C (E3-A, E3-L), the hot margins at the conditioned corner (4c), E3-S and
E4-S as stated (24 h, stored, zero power from the pack), the storage envelope. The enclosure LO-01a needs (T-H1 at least
1.666 W/K) is common to all three.

| | (I) the 35E with local thermal management | (II) RECOMMENDED: a wide-temperature 18650 (HL18650V class) in D-06's 4S3P | (III) the 35E with auxiliary thermal energy |
|---|---|---|---|
| Maker limits | Ver. 1.1: discharge -10 to 60 C, storage 1 month -20 to 60 C (MAKER) | the page: discharge -40 to 85 C, charge -20 to 60 C, storage 30 days -40 to 80 C (INFERRED) | the 35E's; RT57HC melting 55 to 58 C; LSH 20 -60 to +85 C, storage recommended at +30 C at most (MAKER) |
| Usable energy | 108.1 Wh (2.52 h); 2.34 to 2.47 h with a pack-fed cooler at the best corner | 90.4 Wh (2.11 h), 16.4 % less; 121.0 Wh nominal | the pack's 108.1 Wh; the primary serves the heater only |
| Thermal demand | coolers: 0.86 to 3.44 W (best corner), 8.18 to 35.21 W (conditioned); E3-S 52 to 117 Wh from a second store; E4-S 58.7 to 163.2 Wh from a second store | none added (the existing mat for charging; the cell charges from -20 C at 0.1C to 4.1 V) | none electrical for the store; the heater 2.44 to 6.80 W on average |
| Mass and volume | a cooler (no sheet held), an E3-S store, 1.0 to 2.0 kg (0.54 to 1.07 L) of primary cells outside the pocket | the same block; 44 g a cell against 50 g at most (72 g a pack less at most); +0.50 mm against 0.77 mm | store 0.162 L (E3-O) and 1.489 L (E5) conditioned, 0.275 to 1.175 L (E3-S), against 0.087 L; the primary as (I) |
| Maintenance | the primary replaced as a set every two years (ASSUMPTION); the cooler | the pack as today; at least 500 cycles at 25 C (page) | the store none; the primary as (I) |
| Implementation | a cooler and its control, a storage-time store and cooler, a primary string with thermostat and blocking path, Layer 7 volume | the cell; U2 to BQ7720704 (83 C, OVP 4.275 V, UVP 2.0 V, COUT an open-drain active pulldown: F2's drive re-drawn); the ladder C1 75.0, H1 76.5, H2 77.0, OTD 77.5 C (first cut, today's offsets under +80 C); SOT, the PTC, the release; the gauge's data and cold cutoffs | a sealed container round the block; a primary string with thermostat and blocking path |
| Constraints changed | D-06: a second energy store (E3-S, E4-S) | D-06's "about 145 Wh"; the spend (cell_provenance); REQ-046's windows and REQ-077's +60 C restated with the cell | D-06: a second energy store |
| Remaining uncertainty | LO-01d, LO-01e rest on a cooler of up to 35 W lifting the air onto the +70 C parts (the input's spare power not derived); LO-01f, LO-01g need added storage | the signed specification (architecture level); U2's window re-run; T-H1 and F2 (common) | LO-01d (H1's window), LO-01e (conditioned), LO-01f (pocket) rejected; LO-01g needs added storage |

| Row | (I) | (II) | (III) |
|---|---|---|---|
| LO-01a | CONDITIONAL (T-H1) | CONDITIONAL (T-H1) | CONDITIONAL (T-H1) |
| LO-01b, LO-01c | no collision | no collision | no collision |
| LO-01d | INCONCLUSIVE: a cooler of 8.18 to 25.69 W lifting the air 4.9 to 15.4 K | CONDITIONAL: 11.14 K under +80 C, 6.93 K under H1, 6.84 K under U2 | REJECTED (H1's window) |
| LO-01e | INCONCLUSIVE: a cooler of 11.21 to 35.21 W lifting the air 6.7 to 21.1 K | CONDITIONAL: 5.27, 1.06 and 0.97 K | REJECTED at the conditioned corner |
| LO-01f | needs added energy storage (D-06) | CONDITIONAL: 9.00 K under +80 C, 4.70 K under U2 | REJECTED within the pocket |
| LO-01g | needs added energy storage (D-06) | CONDITIONAL: 7.00 K inside -40 C | needs added energy storage (D-06) |
| LO-01h | CONDITIONAL (the lot) | CONDITIONAL: 0 K at the envelope's rows (the page's rows equal them) | CONDITIONAL (the lot) |

Added subsystems: (I) 3, (II) 0, (III) 2. Rows rejected: (I) none, (II) none, (III) LO-01d to LO-01f. Rows needing added
energy storage: (I) LO-01f and LO-01g, (III) LO-01g. **(II) is the least complex approach with a defensible basis.** Its idle hot
limit is the page's 30-day storage row (+80 C), the lower of its hot rows; E5's conditioning and ten cycles and E3-S's
24 h stay inside those 30 days. LO-01a's cells sit at 55.25 C on the pack, 29.75 K under +85 C and 20.54 K under the
re-derived H1. At the bound's worst corner (an enclosure under LO-01a's line) E5's cells reach 79.63 C, over the
re-derived H1 and U2's lowest trip, so (II) carries T-H1's condition as LO-01a does.

## 7. The decision per row (`.out` section 5)

| Row | Decision | Evidence | Complete acceptance | Routes |
|---|---|---|---|---|
| LO-01a | **CONDITIONAL** | MAKER, MODELED, INFERRED, ASSUMPTION | E3-A and E3-L at +40 C, on the pack then on shore: every cell at or under +60 C and the +59 C abort, H1 not acting, inside air at or under +55 C (SGP41), F2's body at or under +60 C, no permanent protection action | the enclosure at 1.666 W/K (T-H1); the coupling for the cells only |
| LO-01b | NO COLLISION | MAKER, MODELED | E4-O: every cell at or above -10 C once warm | none needed |
| LO-01c | NO COLLISION | MAKER, MODELED | E3-A's T3, T4 and OTC lines; E4-O's floor and the panel's hold | none needed |
| LO-01d | **OPEN** | MAKER, MODELED, INFERRED, ASSUMPTION | E3-O, pack fitted: every cell inside its limit for 4 h, no shutdown, recovery | (II) CONDITIONAL (recommended); (I) cooling INCONCLUSIVE (rejected at the worst corner); passive and latent storage REJECTED |
| LO-01e | **OPEN** | as LO-01d | E5, pack fitted: every cell inside its limit through the cycles, operational checks, capacity recovered | (II) CONDITIONAL; latent storage REJECTED within the pocket (section 15a); cooling INCONCLUSIVE with its limits named |
| LO-01f | **OPEN** | as LO-01d | E3-S, pack fitted: every cell inside its governing storage limit for 24 h at the stored charge, capacity recovered | (II) CONDITIONAL; insulation and latent storage REJECTED; cooling needs a second store (D-06) |
| LO-01g | **OPEN** | as LO-01d | E4-S, pack fitted: every cell inside its storage row for 24 h, capacity recovered | (II) CONDITIONAL; insulation and the pack-fed heater REJECTED; latent storage INCONCLUSIVE (no sheet); the primary-fed heater a proposal under D-06 |
| LO-01h | **CONDITIONAL** | MAKER | the lot's sheet covers -20 C for 3 months and +25 C for a year; E4-T at the floor | procurement (Ver. 1.1) |

No row is recorded as CLOSED, and no cell change is taken.

## 8. The owner items, and what could overturn the recommendation

No row has every route rejected (rows with every route rejected: none), so no owner decision is forced. A missing cell
rating is a component limitation plus missing feasibility evidence, not a contradiction between owner requirements
(D-29, D-36, cell_provenance). **The recommendation needs the owner for exactly two things:**
1. **Now:** send the drafted request for the HL18650V's signed product specification to Yichun Topwell Power
   (`clarification/topwell-hl18650v.txt`); the session contacts no outside party.
2. **Once that specification confirms the page's rows at the stored charge:** approve the cell change inside D-06's
   4S3P, which restates D-06's "about 145 Wh" to about 121 Wh nominal (90.4 Wh usable, 16.4 % less) and, with the cell,
   the cell-derived numbers of REQ-046 (charge 0 to 45 C, discharge -10 to 60 C) and REQ-077 (the cell maker's +60 C),
   and its spend (USD 3.50 a cell at the marketplace price, about USD 42 a pack).

**Architecture-level uncertainty (could overturn it):** the signed specification not confirming storage at +71 C or
-33 C at the stored charge, or reading the idle limit lower than +80 C. Then that row falls back to (III): LO-01f has no
in-pocket route, and LO-01g's primary-fed heater needs the owner's ruling on added energy storage under D-06.
**Downstream, not architectural:** U2's variant window at the network re-run, the ladder's settings, the gauge's
chemistry data, F2's replacement (common to every approach), T-H1's measured conductance (common).

**Possible later changes, none proposed now:** A, a requirement change (the four margin levels shown with the pack out
of the exposure, as REQ-074 and REQ-051's deviations already run them; reserved to the owner by D-29); C, (III)'s added
energy store for LO-01g under a ruling on D-06, only if the specification leaves LO-01g.

## 9. The battery path's other thermal items (`.out` section 6)

- **F2** (Eaton SCF9550-30-05, MAKER ELX1135): operating -20 to +60 C; storage -10 to +40 C below 90 % RH (whether that
  covers a mounted part is not stated). At about the inside air (INFERRED) it is past +60 C at LO-01a's worst corner
  (62.12 C) and at LO-01d to LO-01g, under every approach. Questions drafted for Eaton (`clarification/eaton-scf9550.txt`).
- **U2 (BQ7720700 today):** its 70 C trip lies somewhere in 62.7 to 77.5 C at the network, so +71 C storage permits a
  destructive trip of a fitted pack under (I) and (III); under (II) it moves to the BQ7720704 (lowest trip 75.7 C,
  INFERRED from the same network tolerance).
- **The gauge's thresholds** (OTC 44.0, OTD 57.5, UTC 1.0, UTD -9.0 C) stay inside REQ-046's windows; this record moves
  none. Under (II) the windows and the ladder move with the cell. With the coupling the block gains a gradient, so the
  thermistors go on the hottest cells and P14 is re-measured.
- **PWR-F12 and P13:** as section 4 (key-down 56.37 to 58.24 C; P13's hour 4.67 to 8.00 W into the cells).

## 10. Downstream items (owner by layer; acceptance)

| Owner | Item | Acceptance |
|---|---|---|
| Session (layer 4) | with the signed specification: U2's variant window at the network, the ladder (C1 75.0, H1 76.5, H2 77.0, OTD 77.5 C first cut), SOT, the PTC, the release, the gauge's data and cold cutoffs; 4d's margins re-run on the specification's rows | every margin of section 6 positive at the conditioned corner |
| Layer 6, components | the HL18650V's signed specification and the maker behind the listings; the lot; F2 above +60 C and below -20 C (Eaton) or another self-control protector | the documents filed and read |
| Layer 7, mechanical | the coupling only if T-H1 reads under 1.666 W/K; nothing for (II) | E3-L, E4-S |
| Layer 8, generator owners | under (II): `gen_sch_p.py` (U2 to BQ7720704 with its COUT drive, F2) and `pcb_pack_protection.yaml` re-derived | the protection suite |
| Layer 9, pre-layout | board P's place (F2 at the air), thermistors on the hottest cells | P13, P14 |
| Prototype bench | T-H1 in both lid states; E3-A, E3-L, E3-H, E3-O, E5 with a thermocouple on every cell; E3-S, E4-S with the pack fitted; E4-O; P13 at the cell surface; P14; P15 | each TEST-PLAN pass line; 4c's corner replaced by the measured conductance |
| TEST-PLAN's owner | confirm E5 as Method 507.6 Procedure II; under (II), restate the cell-derived numbers (the +59 C abort, E3-P's +58 C, the +60 C pass lines) | the plan's revision |
| Firmware owner | under (II), the gauge image with the new cell's data and the re-derived ladder | E3-H, E3-P |
| Board B's owner | BANK-R1 in `gen_sch_b.py` (E3-L's stage criteria) | E3-L |
| The kit's thermal owner (outside FEA-008) | the +70 C parts against E3-O's and E5's inside air at the conditioned corner (70.00 and 75.00 C), common to every approach | E3-O, E5 |
| Owner | the two items of section 8 | |

## 11. Decisions taken by the session (authority: SESSION, under the owner's standing rule of 26 September 2026)

| Decision | Why the session's | Reversed by |
|---|---|---|
| (II) recommended, not taken; no spend proposed now | an engineering comparison within D-06's size; the cell change and the spend stay the owner's (cell_provenance) | the signed specification not confirming the rows, or the owner declining the change |
| The hot margins judged at the conditioned corner | every approach carries LO-01a's 1.666 W/K, so the corner below it is not a design point | T-H1 reading under that line |
| (II)'s idle limit read from the page's 30-day storage row, the ladder kept at today's offsets | the lower of the page's hot rows; the offsets carry the published error budget | the signed specification's rows and basis |
| U2's lowest trip shifted by the BQ7720700's 7.3 K (INFERRED) | the network's tolerance analysis is not re-run here | that re-run |
| The primary battery a proposal under D-06, not adopted | it is added energy storage, 3.2 to 6.5 times the pack | an owner ruling on D-06 |
| FEA-008 kept open, not escalated | no row has every route rejected | a row whose every route is rejected on bounded evidence |
| Third-party files filed or held back | each file's terms, read conservatively | the makers' permission |

## 12. Checks 1 and 2, the owner's instruction, and what each correction changes

| Item | Change, and its effect on the numbers, margins or verdict |
|---|---|
| Check 1 (R1 to R5, M1 to M3) | answered in the previous revision: LO-01a's three thresholds, the screen's rows C03 to C05 and C15 to C19, LO-01g in three cases, the framing as component limitations, the redesign as option B's entry cost |
| Check 2, R2 (the mappings) | C04, C05, C16 to C18 mapped (the lid-closed start; E3-H's hold and its repeat with the sensor controller in reset, TMP117 at +55.0 and +56.0 C, released at +45.0 C; the restart at +46.5 C after 30 minutes; the return to 25 C with capacity within 5 %; OTD's recovery at +52.5 C); no thermal figure moves; unstated charge states named as missing inputs: minor |
| Check 2, R3 (usable energy) | the pack-fed heater's 11.9 to 28.9 Wh and 1.3 to 8.6 h labelled model sensitivities; the rejection rests on the shutdown path alone: minor |
| Check 2, R3 (passive storage) | the rejection narrowed to the calculated insulation (24.6 and 30.3 mm, unchanged); latent storage bounded on its own (4b, 4c): new routes, REJECTED or INCONCLUSIVE; each row's decision unchanged |
| Check 2, R3 (the cooler balance) | was: the loop did not close at the worst corner for COP 0.5 (heat counted twice); now: it closes, with the air at 86.4 to 144.8 C (worst) and 74.9 to 96.1 C (conditioned): REJECTED into the sealed case at the worst corner, INCONCLUSIVE at the conditioned corner (8.18 to 35.21 W, the air lifted 4.9 to 21.1 K onto the +70 C parts); E3-S's second store: 38 to 213 Wh with the heat sent out of the case (a sealed path missing), 52 to 117 Wh into the sealed case at the best corner, no equilibrium at the worst for COP 0.5. Material: (I)'s hot rows now carry that cooler |
| Check 2, R3 (E5) | from INCONCLUSIVE on a missing profile to Method 507.6 Procedure II: latent storage 0.102 L at the best corner (over the corrected 0.087 L room, section 15a), 1.489 L at the conditioned and 7.12 L at the worst corner. Material for (III) |
| Check 2, minor R1 | the coupling on shore: cells 59.30 C (past the +59 C abort), air 63.42 C; LO-01a's decision and 1.666 W/K unchanged: minor for the row |
| Check 2, minor R2 | C17: OTD stops the discharge before +60 C and recovers at or below +52.5 C, no immediate refusal claimed: minor |
| Check 2, minor R3 | the fast corner's 8.20 W against the mat's 7.5 W: a further inability of a route already rejected: minor |
| The owner's instruction of 2 October 2026 | the selection itself changes: one comparison of three complete approaches (section 6), cells researched beyond the held set (section 5), the primary battery a bounded proposal under D-06, each measure bounded (4b), (II) recommended |

## 13. Files

`l4e10_cell_thermal.py` and `.out` (section 0 reproduces `pwr_budget.out` and `.json`, `pwr_red2.out` and
`hotstop_bounds.out` byte for byte and pins 49 inputs by sha256, L4-E12's output at its commit among them; section 8 prints
the predicates; section 9 is U-01 by mode, section 10 its consolidation, section 11 the battery comparison); `fetch_held_back.py`; `inputs/` (the Topwell
page, the prices of 1 and 2 October, Saft's curves read by eye, the cells beyond the held set); `clarification/` (Topwell,
Eaton, Saft); `checks/`; `README.md`. The tests:
`env -C v2/ecad/tools/tests python3 run.py test_l4e10 test_public_hygiene`. No generator, BOM, registry or Layer 3 file
is changed.

## 14. U-01 by mode: the limits established separately, the charging constraints, usable energy (`.out` section 9; 2 October 2026)

The owner's instruction of 2 October 2026: charging, discharging and storage limits established separately with their
conditions, and usable energy and the charging constraints for the proposed cell. **No cell is adopted and every setting
below is a draft; FEA-008 stays open until the signed specification and the owner's approval.** Classes in this section:
MAKER (a maker's signed document or datasheet), MAKER-PAGE (a maker's product page: no signature, no test conditions),
INFERRED (computed, method stated), ASSUMPTION, SESSION (a draft setting chosen here).

### 14a. The HL18650V class's limits by mode (MAKER-PAGE: Yichun Topwell Power's product page, `inputs/topwell-hl18650v-page-2026-10-01.json`)

| Mode | Row | Figure | Condition as the page states it | The signed specification must confirm |
|---|---|---|---|---|
| Charge | window | -20 to 60 C (a headline) | basis (cell surface or ambient) and state of charge not stated | the basis; the window at every state of charge |
| Charge | coldest row | 0.1C (0.28 A a cell) to 4.1 V | printed "-20 -10<T<=0 C": legible from -10 C; -20 to -10 C not legible | the band's lower edge, current and voltage |
| Charge | middle row | 0.2C (0.56 A a cell) to 4.2 V | 0 < T <= 10 C; C is the 2.80 Ah minimum (0.56 A = 0.2C) | the temperature basis |
| Charge | warm row | 0.5C (1.40 A a cell, its maximum continuous charge) to 4.2 V | 10 < T < 60 C; no derating toward the hot end | any derating or time limit at 4.2 V above 45 C |
| Charge | method and end | CC/CV to 4.2 V; standard charge 0.56 A | termination current not stated | the termination current at 4.2 V and 4.1 V |
| Discharge | window | -40 to 85 C (a headline) | basis and current not stated | the basis; the current at the window's ends |
| Discharge | end voltage | 2.75 V (0 to 85 C), 2.50 V (-20 to 0 C), 2.00 V (-40 to -20 C) | the current not stated | the current behind each end voltage |
| Discharge | current | 10 A continuous; no pulse figure | no temperature or duration stated | the pulse current and duration; any derating |
| Discharge | capacity | 2.90 Ah typical, 2.80 Ah minimum at 0.2C | temperature not stated; nothing at the cold end | the capacity at -20 and -40 C at 0.2C and 0.5C |
| Storage | rows | -20 to 25 C 12 months; -20 to 45 C 6 months; -40 to 60 C 3 months; -40 to 80 C within 30 days | state of charge, recovery and self-discharge not stated | each row's state of charge, recovery and self-discharge |
| Rest | high charge, hot | not stated | the kit on an input in E3-O and E5 holds the pack up to its charge | the recovery after E5's ten cycles and E3-O's 4 h |
| Other | | at most 18 mOhm; about 44 g; at least 500 cycles (25 C, 0.5C / 1C) | no end-of-life capacity | the capacity after the stated cycles |

**Comparable 18650s with makers' own sheets, context only and never a substitute for the HL18650V's figures:** Samsung's
INR18650-30Q V1.0 of 2020 (signed, held back): surface discharge -20 to 80 C, ambient charge 0 to 45 C, storage 1 month
-20 to 60 C at 30 % of charge, 60 % of capacity at -20 C and 75 % at -10 C at 10 A, a full charge stored 30 days at 60 C
recovering at least 2,320 mAh (80 % of rated); its Version 1.0 of 2015 (signed): surface discharge to 75 C, storage 1
month -30 to 60 C at 40 % of charge, recovery 90 %; Molicel's INR-18650-P28A data sheet ("for reference only", not
signed): ambient charge 0 to 60 C, discharge -40 to 60 C. **The page's rows beyond every comparable are charge below
0 C, storage above +60 C and storage below -30 C**: the rows most exposed to a narrower signed figure.

### 14b. The charging constraints in D-06's 4S3P (drafts, never applied)

The BQ25731 has no cell temperature input, ends a charge only on the host's word, straps 16.800 V for 4S and trips BATOVP at
104 % of ChargeVoltage (MAKER, SLUSE66A, through `review-packets/battery/CHARGER-STATE-SEQUENCE.md`). The windows are the
gauge's: the BQ4050's ranges T1, T2, T5, T6, T3 and T4 set ChargingCurrent() and ChargingVoltage() per range and UTC holds
the charge FET off (MAKER, SLUUAQ3A 14.4 and 2.11); the host relays them to the charger. Today: UTC 1.0 C (recovery 5.0 C),
T1 1 C, T3 42 C, T4 43 C, OTC 44.0 C, the kit's hold below +3 C.

| Range (draft, SESSION) | Page's band | Page's current for the pack | Set current | Charge voltage, pack (BATOVP) |
|---|---|---|---|---|
| Low Temp, T1 -9 C to T2 1 C | -10 to 0 C | 0.1C, 0.84 A | 0.84 A | 4.10 V a cell, 16.40 V (17.06 V) |
| Standard Temp low, T2 1 C to T5 11 C | 0 to 10 C | 0.2C, 1.68 A | 1.68 A | 4.20 V a cell, 16.80 V (17.47 V) |
| Recommended and Standard Temp high, T5 11 C to T3 42 C | 10 to 60 C | 0.5C, 4.20 A | 3.00 A (the drawn limit, 0.357C) | 4.20 V a cell, 16.80 V (17.47 V) |

- **Thresholds:** UTC -9.0 C (recovery -5.0 C), each threshold kept today's 1.0 K inside its band edge; T3 42 C, T4 43 C
  and OTC 44.0 C kept (SESSION: inside the page's +60 C, for cell life; reversed by the signed charge rows); the kit's hold
  below -7 C; the gauge's CUV from 2.50 V to 2.75 V a cell (the page's end above 0 C; the kit's graceful line at 3.00 V
  under load acts first); the termination current: none on the page, TI's default 250 mA kept (ASSUMPTION).
- **Below the cold charge limit** no charge starts (UTC holds the charge FET; the host starts none). The mat (U22 on
  VBAT = VSYS) warms the block first. On battery it is a discharge load under the cells' discharge rows, so its energy
  comes out of usable energy (14c); with an input and the charge FET off it is fed through VSYS by the source,
  CONDITIONAL on U-04's VSYS regulation (L4-E11). The 35E cannot feed it below UTD's -9.0 C reading; the HL18650V's page
  lets the pack feed it down to -40 C.

### 14c. Usable energy, not nameplate

The tree's energy chain (`records/energy/energy_budget.py`, behind L4-E9's battery-only figure) at PS-IDLE-SPEC 42.8 W, the
run ending at the graceful line of 3.00 V a cell under load (before either cell's end voltage), aged to 0.80. **The ageing
allowance** is REQ-014 and SC-23's replacement point, the basis of the 35E's figure, so the two compare; for the HL18650V
it is an ASSUMPTION: the page gives 500 cycles and no end-of-life capacity, and its rest at high charge in the hot is
unstated (the 30Q6's signed full-charge row loses up to 20 % in 30 days at 60 C).

| Pack | +25 C | Cells at -5.52 C (LO-01b, -20 C ambient, the kit's heat) | Cold start, cells at -20 C | The heater, out of usable energy |
|---|---|---|---|---|
| 35E (D-06) | **107.9 Wh, 2.52 h** (the replay's figure reproduced) | 54.0 Wh (44.5 Wh at its -10 C floor, 1.04 h) | out of scope (D-02d): no discharge below its floor | none at that corner; 0.44 W with the coupling fitted (0.45 Wh over the run) |
| HL18650V (II) | **90.2 Wh, 2.11 h** (16.4 % less; the 35E's curve shapes, ASSUMPTION) | 45.1 to 69.6 Wh (ASSUMPTION: the 35E's own factor 0.500 to the 30Q6's 0.772) | 37.2 to 54.1 Wh (ASSUMPTION: 0.4124 to 0.600) | none required by its rows; a warm-up of a cold-soaked block from -20 C: to T1 -9 C 1.6 to 2.8 Wh, to T2 1 C 3.4 to 12.3 Wh, to T5 11 C 5.7 Wh or not reached at the high corner (the mat alone stops at 2.1 C) |

The objective (REQ-072, 48 to 72 h at 42.8 W) is 2054 to 3082 Wh; both packs stay far under it (DR-01 FAIL either way).
**Where they enter:** L4-E9 section 10's U-01 bullet reads 90.4 Wh against 108.1 Wh (this record's first chain) and
every shortfall growing by at most 17.7 Wh; this chain gives 90.2 Wh, 17.7 Wh less than the 35E's 107.9 Wh, the same
growth. REQ-014 takes the aged figure; REQ-046 the charge rows of 14b and the discharge window with its end voltages;
REQ-077 the idle limit of 14d (+80 C on the page). None is applied.

### 14d. What the signed specification would change

| Row | Confirmed | A narrower figure: the threshold where the architecture moves | No answer | Fallback and its cost |
|---|---|---|---|---|
| Idle hot limit (30-day row, +80 C) | 4d's margins stand | under 78.94 C H1 acts in E5's dwell (E5 does not require it idle, INFERRED); under 74.73 C E5's cells pass the limit; under 73.07 C E3-O loses "no shutdown"; under 71.00 C E3-S fails; under 68.86 C E3-O's cells pass it | CONDITIONAL; U-01 a release gate | E3-O and E5: (I)'s cooler, 8.18 to 35.21 W, INCONCLUSIVE; E3-S: no route within D-06's pocket, requirement change A (the owner's; no spend, the kit not claimed at that level with its own pack) |
| Storage floor (-40 C rows) | LO-01g closes on the cell | warmer than -33 C | as above | (III)'s primary-fed heater, 470 to 940 Wh of added storage (an owner's ruling under D-06), or requirement change A |
| State of charge of the storage rows | no change | below REQ-025's stored charge (30 %) | as above | the stored charge restated (REQ-025, the owner's) or the fallback above |
| Rest at high charge, hot | no change | a loss beyond TEST-PLAN's recovery line | as above | a High Temp range to 4.1 V a cell above T3 or L4-E12's hold of the charge (SESSION levers); not architecture-level |
| Charge below 0 C | the drafts of 14b | refused | T1 at +1 C, the mat first | as the 35E today; no architecture effect |
| Charge current from +10 C | the drawn 3.0 A stands | under 0.357C | as above | the set current lower, and the solar day's stored energy with it (L4-E9's replay) |
| Continuous discharge | no change | under 6.0 A a cell (PS-ALLTX's 18 A) | as above | D-06's 4S3P cannot carry PS-ALLTX with this cell: back to (I) |
| End voltage | no energy change | above the graceful 3.00 V under load | as above | usable energy falls with the end fraction |
| Minimum capacity | no change | any: 3.22 Wh of usable energy per 100 mAh a cell (INFERRED) | as above | not architecture-level (DR-01 already FAIL) |

Cold capacity, cycle life and the basis move 14c's figures and the ageing allowance, not the architecture. With no answer
every row stays CONDITIONAL, the owner's second item cannot proceed, and U-01 stays a release gate (the existing state,
needing no ruling). **The drafted request gained questions 7 to 10** (`clarification/topwell-hl18650v.txt`): the cold
charge band and termination, the pulse current, the cold capacity, the end-of-life capacity and self-discharge;
questions 1, 2 and 6 already asked for the storage rows with their charge and recovery, the basis with the rest at high
charge, and the gauge's data.

## 15. U-01 consolidated: suitability by mode, the conductance bound, published specifications, the missing fact (`.out` section 10; 2 October 2026)

The owner's question of 2 October 2026: charge, discharge and storage suitability established separately with usable
energy; whether published makers' specifications suffice or a vendor answer is genuinely necessary; a supported route
within the approved arrangement, the adoption approval retained; and, where evidence is missing, exactly what it must
establish. **No cell is adopted.**

### 15a. The pocket's room, corrected

The independent verifier's item 3 (`records/l4close/VERIFICATION-2026-10-02.md` at 08841dfa) was right: CASE-MARGINS row
M5 carries escaped pipes in its margin text, so the plain split read M5 at +11.74 mm, the superseded flat-floor figure.
The script now splits rows on unescaped pipes only and reads the "Chosen: nominal" column by its header: M4b +9.68, M5
+3.65, M6 +4.42 mm. **The room as designed moves from 0.1215 L to 0.0865 L** (0.0559 L at the worst stack, unchanged).
What moved: E5's latent storage at the best corner (0.102 L) no longer fits, so approach (III)'s E5 route is REJECTED
within the pocket (it was INCONCLUSIVE, a marginal fit). Every other fit and rejection stands: E3-O's best corner 0.012 L
still fits; E3-S, E5's other corners and the primary cells were already outside.

### 15b. Suitability by mode

| Cell | Charge | Discharge | Storage |
|---|---|---|---|
| Samsung INR18650-35E, Ver. 1.1 (D-06's ruled cell; MAKER) | **suitable on published evidence**: LO-01c (REQ-046's 0 to 45 C) and the cold charge (REQ-046: the mat warms the pack below 0 C; C09) | **suitable** for LO-01a (+40 C, D-02) and LO-01b (-20 C once warm, D-02d); **unsuitable on published evidence** for LO-01d (+55 C, D-02a, E3-O: the cells 61.26 to 72.42 C against +60 C) | **suitable** for LO-01h (D-02, REQ-025) and E3-T's +58 C; **unsuitable on published evidence** for LO-01f (+71 C, D-02a, E3-S), LO-01g (-33 C, D-02a, E4-S) and LO-01e (E5's dwell, SC-03: the idle pack at 74.73 C at the conditioned corner) |
| HL18650V (the proposal of section 6; MAKER-PAGE) | **suitable only with a vendor answer** (the page's rows; the coldest garbled; no termination); the cold charge served by the mat as for the 35E | **suitable only with a vendor answer** (LO-01a, LO-01b, LO-01d: -40 to +85 C, no basis, no pulse, no cold capacity) | **suitable only with a vendor answer** (LO-01e to LO-01h: the page's rows, no state of charge, no recovery) |
| Saft MP 176065 xtd (Doc. n 31109-2-0625, June 2025; MAKER, held back) | **window suitable on published evidence**: LO-01c (-30 to +85 C, CC/CV 4.2 V); the drawn 3.0 A from 0 C to T3's 42 C under the printed 5.6 A (the sheet qualifies it only below 0 C, its footnote 4); the cold charge by the mat. **Charge current below 0 C AWAITING Saft or the sample qualification** | **window suitable on published evidence**: -40 to +85 C for LO-01a, LO-01b, LO-01d. **Current and temperature together AWAITING Saft or the sample qualification**: 10 A continuous, 18 A for 60 s and the gauge's 20 A for 2 s on one cell, at -20, -10, +45, +60, +70 and +80 C (the sheet: "Can vary depending on temperatures. Consult Saft", footnote 2) | **window suitable on published evidence**: allowable -40 to +85 C covers +71 C, -33 C, E5's dwell and the envelope. **Dwell and recovery AWAITING Saft or the sample qualification**: 24 h at +71 C and at -33 C at 30 %, E5's rest at full charge, the capacity after each |

The cell limits are the cell's; whether the cells stay inside them in LO-01a, LO-01d and LO-01e is the enclosure's.

### 15c. The conductance bound carried into the routes

U-02's conservative bound (L4-E12 at aab69775, the fans' flow credited at zero): E3-O lid open 0.607 W/K, lid closed
0.537; E5 lid open 0.566, lid closed 0.505; +40 C lid open 0.598, lid closed 0.524. On the bound E3-O's cells peak at
80.29 C and E5's at 99.50 C. The conductance each row needs (W/K; LO-01a judged lid closed, so the full T-H1 gives it;
"U2 at today's network" is the 83 C variant on today's thermistor network, INFERRED and movable by a re-derived network):

| Cell | Row | Cell limit | No hot stop | U2 at today's network | The reading T-H1 must give (L4-E12's bands 2.462 / 1.516 / 1.410 / 1.199 / 0.951 / 0.644) |
|---|---|---|---|---|---|
| 35E | LO-01a | 1.246 | 1.604 | | 1.410 for the cell limit; 2.462 for no hot stop and the complete pass (1.666) |
| 35E | LO-01d | 4.996 | none suffices | | over every band |
| 35E | LO-01e | none suffices | none suffices | | none |
| HL18650V | LO-01a | 0.604 | 0.677 | 0.679 | 0.644 and 0.951; the complete pass 2.462 |
| HL18650V | LO-01d | 0.624 | 0.914 | 0.921 | 0.951 and 1.199 |
| HL18650V | LO-01e | 1.195 | 1.547 | 1.557 | 1.410 and 2.462 |
| MP 176065 xtd | LO-01a | 0.535 | 0.592 | 0.679 | 0.644 (lid open it holds on the bound's 0.598); the complete pass 2.462 |
| MP 176065 xtd | LO-01d | 0.361 | 0.578 | 0.921 | **holds on the bound** (0.607) for the cell limit and no hot stop |
| MP 176065 xtd | LO-01e | 0.932 | 1.145 | 1.557 | 1.199 and 1.410 |

- **T-H1 decides** LO-01a's complete pass (the SGP41's air, 1.666 W/K) and LO-01e for every cell. LO-01d holds on the
  bound only with the MP 176065 xtd (U2's network re-derived above the hot stop); the HL18650V needs 0.624 W/K and the
  35E 4.996 W/K, which no reading in reach gives.
- **Rows that hold on the bound for every cell:** LO-01b (the cells at about +53 C at -20 C ambient: warmer, not colder);
  LO-01c (the gauge holds charging off; on the bound a running kit at PS-IDLE-SPEC reaches T3's 42 C window only below
  -30.6 C ambient, an energy consequence for L4-E9, not a cell limit); LO-01f, LO-01g and LO-01h (zero power: the kit's
  time constant rises to 5.5 h and the cells still follow the ambient within 0.013 of the step in 24 h, so these rows are
  the cell's rating alone).

### 15d. Do published specifications suffice?

Candidates within the arrangement (a 4S Li-ion pack at the 14.4 V class in D-06's pocket), at most three:

| Candidate | Rows covered on published evidence | Usable energy in the pocket | Fit | Cost | What it changes downstream |
|---|---|---|---|---|---|
| **Saft MP 176065 xtd**, prismatic Li-ion, 4S1P (MAKER datasheet, held back) | the temperature windows of every cell limit row (charge -30 to +85 C, discharge -40 to +85 C, storage allowable -40 to +85 C); current and temperature together, and the storage dwell and recovery, AWAITING Saft or the sample qualification (15g) | 81.6 Wh nominal (typical); **53.5 to 55.1 Wh usable, 1.25 to 1.29 h** (the tree's chain, aged 0.80, the 35E's curve shapes ASSUMPTION; Saft publishes no minimum capacity) | growth +6.90 / +4.85 / +0.20 mm (axis, across, height) against 5.30 / 9.68 / 3.42 as designed and 0.77 / 6.38 / 2.66 at the worst stack: not with the 35E block's 3.00 mm of wrap; **CONDITIONAL on at most 1.40 mm of wrap along the axis** and M5's chosen placement (OPEN: T4); failing it the pocket changes, a proposal for the owner | NZ$ 238.72 a cell (a distributor's listing archived in January 2025), NZ$ 954.88 for four | D-06 restated (the cell, 4S1P prismatic, about 82 Wh nominal); REQ-046 and REQ-077's cell-derived numbers; U2 and the ladder under +85 C; the gauge's 1P data; a prismatic holder; the charger's 16.8 V and the CUV's 2.50 V unchanged (its cut-off is 2.5 V) |
| Yichun Topwell Power HL18650V, 18650 Li-ion, 4S3P (MAKER-PAGE) | every row on the page, none on a specification | 121.0 Wh nominal; 90.2 Wh usable, 2.11 h | +0.50 mm along the axis against 0.77 mm at the worst stack | USD 3.50 a cell (a marketplace seller), about USD 42 a pack | section 9: D-06 restated (about 121 Wh), REQ-046 and REQ-077, U2, the ladder, the gauge's data and cold ranges |
| Lithium Werks APR18650M1B, 18650 LiFePO4, 4S3P (MAKER product page) | LO-01g only (storage -40 to 70 C); not +71 C, not E3-O or E5 (discharge to 60 C) | 47.5 Wh nominal | the 18650 block | not read | a 13.2 V class pack: outside the 14.4 V class, a proposal, not a candidate |

**Verdict, restated after Astra's B5: published specifications suffice for the TEMPERATURE WINDOWS of every cell limit row
with the Saft MP 176065 xtd, not for current and temperature together.** Saft's recommended currents "Can vary depending
on temperatures" (its footnote 2), so the kit's 10 A continuous, 18 A for 60 s and 20 A for 2 s at the modelled cell
temperatures, charge below 0 C, and the storage dwell and recovery need Saft's answer or the limited sample qualification
of 15g. The HL18650V's rows need a vendor answer (or a lot soak in its place).

### 15e. The missing facts and their smallest resolution

| Route | The exact missing fact (row, condition) | Vendor answer or experiment | Cost and duration |
|---|---|---|---|
| Saft MP 176065 xtd | every row, D-06's pocket: whether four cells fit along the axis with at most 1.40 mm of wrap and spacers as designed | a dimensional mock-up of four cells at the sheet's maximum dimensions in the pocket at the built stack | printed blocks; hours; no purchase |
| Saft MP 176065 xtd | every discharge row (LO-01a, LO-01b, LO-01d): one cell carrying 10 A continuously, 18 A for 60 s and 20 A for 2 s at -20, -10, +45, +60, +70 and +80 C, from full charge and 30 % | Saft's statement (expanded draft: `clarification/saft-mp176065xtd.txt`), or the limited sample qualification of 15g | one cell (NZ$ 238.72), a chamber, a 25 A load; about two weeks |
| Saft MP 176065 xtd | the storage rows (LO-01e, LO-01f, LO-01g): the dwell and recovery at +71 C and -33 C for 24 h at 30 %, and E5's rest at full charge | the same | within the same qualification |
| Saft MP 176065 xtd | usable energy: the minimum capacity (the sheet gives a typical 5.6 Ah) | measured on the lot at receipt | with the purchase |
| HL18650V | LO-01f at +71 C and LO-01g at -33 C, both 24 h at the stored 30 %; LO-01e's rest at full charge; the page's +80 C idle row | the signed specification (drafted), or a lot soak: sample cells 24 h at +71 C and 24 h at -33 C at 30 %, ten 507.6 cycles at full charge, capacity before and after at 0.2C and +25 C | about ten cells (USD 35.00), an oven, a -40 C freezer and a capacity tester; about 4 days for the soaks and 12 for the cycles; evidence for that lot, not a production guarantee |
| every route | LO-01a's complete pass and LO-01e (and LO-01d unless the MP 176065 xtd): the enclosure's conductance | T-H1 (U-02's experiment) | L4-E12 section 14.6 |

### 15f. U-01's class

**A SUPPORTED ROUTE EXISTS ON PUBLISHED MANUFACTURER EVIDENCE FOR THE TEMPERATURE WINDOWS:** the Saft MP 176065 xtd as a
4S1P pack in D-06's pocket, every cell limit row's window printed by its maker. **NOT YET ADOPTABLE:** current and
temperature together and the storage dwell and recovery AWAIT Saft or the limited sample qualification (15g), the fit
awaits the mock-up, and the adoption awaits the owner's approval (D-06's cell and energy, about 82 Wh nominal against
about 145 Wh, and the spend). With it LO-01d's cells stay inside the temperature window on the conservative bound (the
current at that temperature awaiting 15g); LO-01a's complete pass and LO-01e rest on T-H1 for every cell. The HL18650V stays the higher-energy
alternative (90.2 against 55.1 Wh usable), resting on its vendor answer or a lot soak. Missing evidence is not shown to be
impossible: each missing fact has its check above. FEA-008 stays open until the adoption, the fit and T-H1.

### 15g. The limited sample qualification (a definition; the owner's purchase; nothing is bought here)

It substitutes for Saft's answer on the current-at-temperature and storage rows only, as evidence for that lot.

- **Sample:** one cell of the lot to be fitted (three if the owner prefers a spread), never fitted afterwards.
- **Before and after every step:** the capacity at +25 C, C/5 to 2.5 V after CC/CV 4.2 V (its own baseline); the 1 kHz
  impedance; the thickness at full charge; the open-circuit voltage after 24 h.
- **Steps** (a thermocouple on the surface, the cell soaked to temperature first):
  - D1: 10 A continuous from full charge to the kit's graceful 3.00 V under load, at -20, -10, +45, +60, +70 and +80 C;
  - D2: 18 A for 60 s at full charge and at 30 %, at the same temperatures;
  - D3: 20 A for 2 s (the gauge's OCD) at -20 C and at +80 C, at 30 %;
  - C1: the drawn 3.0 A from 0 C and at +45 C to 4.2 V (0.1C at -10 and -20 C only if charging below 0 C is wanted);
  - S1, S2: 24 h at +71 C and 24 h at -33 C, each at 30 %; S3: ten 24 h cycles of Method 507.6 Procedure II at full
    charge (E5's rest).
- **Pass, every step:**
  - the surface at or under +85 C;
  - the voltage at or over the CUV's 2.50 V under load;
  - no venting or leak;
  - after the step, the capacity at least 95 % of the cell's own before, the impedance at most 1.20 times its own before,
    and the thickness at most 1.0 mm over its own before.
  - These thresholds are SESSION choices: TEST-PLAN's 5 % recovery line, an impedance margin, and the pocket's height
    allowance for wrap.
- **Its limits:** evidence for that lot and that sample only, at the temperatures and currents run; not a production
  guarantee, not Saft's derating, and not a substitute for E3-O, E5, E3-S and E4-S with the pack fitted.
- **Equipment and time:** a chamber from -40 to +85 C, a 25 A load, a CC/CV source and a logger; about two weeks.

**The owner's items for this route:** approval of the cell change inside D-06's pocket (4S1P prismatic, about 82 Wh
nominal; REQ-046 and REQ-077's cell-derived numbers with it) and its spend; sending Saft's drafted questions if the
bench pulse is not preferred. The Topwell request stays for the HL18650V alternative.

## 16. The battery comparison: the approved pack against the Saft route (`.out` section 11; the owner's amendment of 2 October 2026, 14:20)

One compact comparison on one boundary. **GUARANTEED** = a maker's printed limit; **MODELLED** = this record's model, its
assumptions named; **AWAITING** = evidence owed, and by whom. **This section approves neither the cell change nor a
purchase: both stay the owner's.**

| | Approved pack (D-06) | Saft route (a proposal) |
|---|---|---|
| Part and specification | Samsung SDI INR18650-35E; product specification Ver. 1.1, 2015-07-09 (GUARANTEED, filed) | Saft MP 176065 xtd; datasheet Doc. n 31109-2-0625, June 2025 (GUARANTEED, held back) |
| Chemistry, rechargeability | lithium-ion, rechargeable (GUARANTEED) | lithium-ion, rechargeable (GUARANTEED) |
| Arrangement | 4S3P, 12 cylindrical 18650 cells (D-06; the cell sizes GUARANTEED) | 4S1P, 4 prismatic cells (the sizes GUARANTEED; the pack's fit MODELLED, AWAITING the mock-up) |
| Nominal energy | 12 x 3.35 Ah (the minimum, 0.2C to 2.65 V) x 3.60 V = **144.72 Wh**, D-06's "about 145 Wh" (GUARANTEED inputs); 149.04 Wh on the typical 3.45 Ah | 4 x 5.60 Ah (typical, C/5 to 2.5 V) x 3.65 V = **81.76 Wh** (GUARANTEED as typical); 79.39 Wh on an assumed minimum (ASSUMPTION: Saft prints none) |
| Usable energy, one boundary | **107.9 Wh, 2.52 h** at +20 C; 44.5 Wh, 1.04 h with the cells at -10 C (MODELLED) | **53.5 to 55.1 Wh, 1.25 to 1.29 h** on the 35E's curves at the same current; 57.0 to 58.8 Wh, 1.33 to 1.37 h at the same C-rate; 22.1 to 24.3 Wh at -10 C (MODELLED; no Saft discharge or cold curve: AWAITING Saft) |
| Charge limits | 0 to 45 C at the surface; CC-CV 4.2 V; 1.70 A standard, 1.02 A for cycle life, 2.00 A at most a cell; ends at 0.02C (GUARANTEED) | the window -30 to +85 C and CC/CV 4.2 V; 5.6 A at most, with Saft's note only below 0 C (GUARANTEED); the drawn 3.0 A from 0 C to 42 C under it; any current below 0 C AWAITING Saft or the sample qualification; the termination AWAITING Saft |
| Discharge limits | -10 to 60 C at the surface; 8 A continuous, 13 A not continuous (no duration); cut-off 2.65 V (GUARANTEED) | the window -40 to +85 C and the cut-off 2.5 V (GUARANTEED); 11 A continuous and 22 A pulses, which "Can vary depending on temperatures" (footnote 2): the kit's 10 A continuous, 18 A for 60 s and 20 A for 2 s on one cell at -20 to +80 C AWAITING Saft or the sample qualification |
| Storage limits | 1 month -20 to 60 C, 3 months -20 to 45 C, 1 year -20 to 25 C at 30 %, recovery over 80 % (GUARANTEED) | the window: allowable -40 to +85 C, recommended +15 to +30 C (GUARANTEED); the dwell (24 h at +71 C and at -33 C at 30 %, E5's rest) and the recovery, none printed: AWAITING Saft or the sample qualification |
| Physical fit | the ruled block, 56.65 x 133.5 x 38.1 mm, 0.2881 L (GUARANTEED cell sizes) | four cells 0.308 L with terminals; along the axis +6.90 mm against 5.30 mm as designed, so at most 1.40 mm of wrap and spacers (the 35E block uses 3.00 mm); the room round the block 0.0865 L as designed, 0.0559 L at the worst stack; thickness at the beginning of life and full charge, "can increase with temperature and during battery life" (MODELLED fit; AWAITING the mock-up, the session and Layer 7, and Saft's life thickness) |
| Charger (the drawn BQ25731) | strap 16.800 V = 4 x 4.20 V; set 3.0 A = 1.00 A a cell; BATOVP 17.47 V; the gauge's taper 250 mA = 0.083 A a cell; the CUV 2.50 V (the 35E's pack guideline terminates at 2.50 V) (GUARANTEED settings, compatible) | the same 16.800 V; 3.0 A a cell against 5.6 A; BATOVP 17.47 V; taper 0.250 A a cell against no printed termination; the CUV 2.50 V against the 2.5 V cut-off (compatible; the termination AWAITING Saft) |
| Protection | U2 BQ7720700 (OVP 4.325 V, UVP 2.25 V, OT 70 C); the gauge's UTC 1.0, T3 42, OTC 44.0, OTD 57.5, UTD -9.0 C; F2 Eaton SCF9550-30-05, 30 A for 4 to 5 cells (compatible as drawn) | the same parts protect it as drawn, the gauge's thresholds inside its windows; using its +85 C needs U2's 83 C variant and a re-derived network and the ladder (drafts); the pack's 10 A, 18 A and the gauge's 20 A trip pulse fall on one cell, at temperature AWAITING Saft or the sample qualification; the gauge's capacity and chemistry data AWAITING (TI's list or a learning cycle, the firmware owner) |
| Cost | USD 8.25 a cell, USD 99.00 for 12 (the l3batt reading; a quote AWAITING the purchase) | NZ$ 238.72 a cell, NZ$ 954.88 for 4 (a distributor's listing archived in January 2025; a quote AWAITING the owner's purchase) |

### 16a. 145 Wh to 82 Wh, step by step

- **D-06's "about 145 Wh"** is 12 cells x 3.35 Ah (Ver. 1.1's printed minimum) x 3.60 V = **144.72 Wh**. A 3.5 Ah label
  would give 151.20 Wh, a figure Ver. 1.1 does not print; the typical 3.45 Ah gives 149.04 Wh.
- **The Saft route** is 4 cells x 5.60 Ah (typical) x 3.65 V = **81.76 Wh**.
- **The steps:** the count x0.3333 (12 to 4), the capacity a cell x1.6716 (3.35 to 5.60 Ah), the voltage x1.0139 (3.60
  to 3.65 V): **x0.5650 in all, 43.5 % less.**
- That figure compares the 35E's minimum with the Saft's typical. Like for like the cut is **45.1 %**, on typicals
  (149.04 against 81.76 Wh) and on minimums (144.72 against an assumed 79.39 Wh).

### 16b. 2.52 h to 1.25 to 1.29 h, step by step

One boundary for both (MODELLED, the tree's chain `records/energy/energy_budget.py`):
- PS-IDLE-SPEC, 42.8 W at the pack;
- the kit's graceful line, 3.00 V a cell under load, or the 5 % reserve, whichever comes first (the line, for both);
- ageing 0.80 (REQ-014, SC-23);
- +20 C, and the cells at -10 C as the cold point.

| Pack | Current a cell | Rate factor | Mean voltage | End fraction | +20 C | -10 C cells |
|---|---|---|---|---|---|---|
| 35E 4S3P | 0.99 A | 0.9966 | 3.604 V | 0.934 | **107.9 Wh, 2.52 h** | 44.5 Wh, 1.04 h |
| Saft 4S1P (a) same current, assumed minimum | 3.08 A | 0.9735 | 3.470 V | 0.910 | 53.5 Wh, 1.25 h | 22.1 Wh, 0.52 h |
| Saft 4S1P (a) same current, typical | 3.08 A | 0.9735 | 3.470 V | 0.910 | 55.1 Wh, 1.29 h | 22.7 Wh, 0.53 h |
| Saft 4S1P (b) same C-rate, assumed minimum | 3.08 A (curves at 1.90 A) | 0.9865 | 3.595 V | 0.923 | 57.0 Wh, 1.33 h | 23.5 Wh, 0.55 h |
| Saft 4S1P (b) same C-rate, typical | 3.08 A (curves at 1.84 A) | 0.9872 | 3.599 V | 0.924 | 58.8 Wh, 1.37 h | 24.3 Wh, 0.57 h |

- **Most of the change is the energy:** x0.5650 nominal takes 2.52 h to about 1.42 h if the usable fraction stayed the 35E's.
- **The rest is the usable fraction:** 107.9 / 144.7 = 0.7453 for the 35E, 55.1 / 81.8 = 0.6735 for the Saft at (a).
  - The single parallel cell carries the whole pack current, 3.08 A against 0.99 A.
  - On the 35E's curves it loses x0.9768 in rate factor, x0.9494 in mean voltage over nominal and x0.9744 in end fraction:
    x0.9037 in all.
  - At the same C-rate (b) most of that penalty goes, because 3.08 A is only 0.55C of the Saft's typical capacity.
- **The reported 1.25 to 1.29 h is the conservative end, (a).** The Saft's own discharge curve would settle where it lies
  between 1.25 and 1.37 h (AWAITING Saft or a measurement).
- **Earlier figures on other boundaries, reconciled:**
  - the 35E's 108.1 Wh (pwr_budget.py's chain: a rate factor, a 0.05 ohm sag and the 5 % reserve) against 107.9 Wh here;
  - 44.3 Wh at -10 C (the sheet's 1C point) against 44.5 Wh here;
  - the Saft's 53.5 to 55.1 Wh of section 10 is (a) here.

**The endurance objective stays apart from the mandatory rows.** REQ-072's 48 to 72 h (2054 to 3082 Wh at 42.8 W; an
objective, D-28) is far beyond either pack on battery alone (DR-01 FAIL either way). The mandatory rows are LO-01a to
LO-01h (REQ-046, REQ-077, D-02, D-02a).

### 16c. The recommendation, as far as the evidence goes

- **What the Saft route resolves:** the temperature windows of every cell-limit row on its maker's published datasheet:
  the +55 C and E5 rows' cell temperatures, +71 C and -33 C storage, the cold charge by the mat. With it, LO-01d's cells
  stay inside the window on U-02's conservative bound (section 15c). It does not yet resolve current and temperature
  together, nor the storage dwell and recovery (Astra's B5).
- **What it costs:**
  - energy, 81.76 against 144.72 Wh nominal (45.1 % less like for like);
  - runtime, 1.25 to 1.37 h against 2.52 h on battery alone (modelled);
  - money, NZ$ 954.88 for four cells against USD 99.00 for twelve (indicators, not quotes);
  - the changes downstream: D-06 restated, REQ-046 and REQ-077's cell-derived numbers, U2 and the ladder, the gauge's
    data, and a prismatic holder.
- **What stays awaited:**
  - the fit mock-up (the session and Layer 7; no purchase);
  - current and temperature together: 10 A continuous, 18 A for 60 s and 20 A for 2 s on one cell at -20 to +80 C,
    charge below 0 C, and the storage dwell and recovery (Saft's answer, the expanded draft, or the limited sample
    qualification of 15g: the owner's purchase of one cell);
  - the termination current, the life thickness, the minimum and cold capacity (Saft);
  - the gauge's data (TI or a learning cycle);
  - T-H1 for LO-01a's complete pass and LO-01e, for every cell (U-02).
- **The recommendation:** the evidence supports the Saft route as the one cell route whose limits are printed by its
  maker for every margin row's temperature window. It does **not yet** support adoption: current and temperature together,
  the storage dwell and recovery and the fit are unproven, and T-H1 decides the hot rows for any cell. Next, with no
  purchase, the mock-up; then Saft's answer or the sample qualification.
  Adoption is then the owner's call, weighing the energy and runtime above.
- **The alternatives' standing:**
  - The HL18650V route keeps more energy (90.2 Wh usable, 2.11 h) but rests on its maker's page until the signed
    specification or a lot soak.
  - The 35E as ruled meets the in-use rows (LO-01a to LO-01c on T-H1, LO-01h) on published evidence and fails the
    margin rows LO-01d to LO-01g on published evidence. It stands only with a requirement change: the owner's, by D-29;
    the margins shown with the pack out of the exposure.
- **The owner's approval of the cell change and of any purchase is required and is not given here.**
