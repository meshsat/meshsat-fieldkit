# L4-E13: a panel whose open circuit is bounded inside REQ-016's window (U-03, layer 4, MESHSAT-1357)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured, and **no physical unit is accepted**.
This is L4-E9's unresolved choice **U-03** (finding O-1 of `../l4e/L4-ENERGY-ARCHITECTURE.md`): a solar panel whose
open-circuit voltage at the coldest operating temperature is bounded at or under 25 V, at a useful power, compatible with
the stage's 17.6 V hold and portable. Second issue, after the collaborator's check `checks/astra-check-l4e13-1.md` (NOT
YET: B1 the acceptance contract, B2 the classification, four minors; the last section maps each item to its change). Every
figure below is printed by `l4e13_panel.py` into `l4e13_panel.out` (section named); the script reads the makers' rows from
the pinned documents, runs the energy record's replay in-process (it must print `../l4e/l4e_replay.out` byte for byte) and
uses its model, its day and its A1 and A2 runs unchanged. Evidence classes: MAKER, MAKER-PAGE (a maker's web page,
transcribed), RECORD, LITERATURE, MODELED, INFERRED, ASSUMPTION, SESSION.

## The requirement and the envelope (out 1)

REQ-016 (`v2/ecad/tools/pcb_requirements.yaml`), verbatim: "The solar input charges the pack through board E's LT8705A
stage from a panel inside its declared window: an open-circuit voltage of at most 25 V at the panel's coldest operating
temperature, the panel held at 17.6 V by the stage's input regulation, and at most 100 W into the stage." Its acceptance
names F2 and J_SOLAR at 10 A. D-34 keeps the window unchanged. The text constrains the panel's own open circuit: a series
diode or a clamp in the window is not a substitute (D4 is judged apart under TRN-001).

**Temperature: -20 C**, REQ-024's in-use minimum (`pcb_envelope.yaml` agrees); the records settle that reading (L4-ENERGY,
"What stays INCONCLUSIVE"). With no irradiance the cells sit at the ambient (cold-soaked), and the open circuit answers a
burst of light at once, before the cells warm, so the envelope puts its largest irradiance on cells still at -20 C.

**Irradiance: G_MAX = 2111.4 W/m2** (SESSION). It is (1 + E) x E0: E0, the extraterrestrial irradiance at perihelion,
1361 / (1 - 0.0167)^2 = 1407.6 W/m2 (physical constants), which no clear sky exceeds on a plane facing the sun; E = 0.50 from
the read source, quoted with attribution in `v2/vendor/solar/irradiance-enhancement-sources-2026-10-02.md` (Mol and van
Heerwaarden 2025, Atmos. Chem. Phys. 25, p.1, CC BY 4.0: "In cloud fields with enough optically thin area, such as
altocumulus, forward escape alone can drive areas of irradiance enhancement of over 50 % of clear-sky irradiance.").
Why so high: the enhancement is taken on the extraterrestrial irradiance, not on the clear-sky one (about 1000 W/m2 at noon
in the Netherlands, the Cabauw record of Mol, Knap and van Heerwaarden 2023, p.8), so it covers the kit's in-use altitude to
3000 m (D-02c), a snow-covered ground's reflection (the 2025 source, p.5) and more enhancement than the source names,
without a season or weather correlation. The cost is small because the open circuit grows with ln G: A(T) x ln(G_MAX /
1000) = A(T) x 0.7474, about 0.68 V on the SunPower panel at -20 C.

**Useful power: above 1.3656 W at the stage's input.** The stage draws its own drive and quiescent power from its output,
42.3 mA, 1.27 W at L4-E5's raised EXTVCC (L4-E7, INFERRED there); at its declared 0.93 (the replay) the input must exceed
1.27 / 0.93 before any charge reaches the pack.

## The result (out 3, 10, 11)

**U-03: CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC).** Two routes close U-03; the decision admits either
(`classify()`):

| | SunPower SPR-E-Flex-100 (the identified unit) | BougeRV 100W N-Type Fiberglass Foldable | Solbian SX 156 |
|---|---|---|---|
| Maker's document | datasheet 523809 Rev D p.1 ("Typical Electrical Data"); guide 524958 Rev F Table 1 and its note (PDF p.3, printed p.2), 5.1 (PDF p.4); both held back | the maker's product page, transcribed (`v2/vendor/solar/bougerv-sp001-...-2026-10-02.md`); no STC statement, no NOCT | SX series datasheet, February 2023, p.2 (the SX 156 column, the STC note) and p.1; held back |
| Rated Voc, coefficient | 21.4 V, -58.9 mV/K (-0.2752 %/K), no limits printed | 19.6 V, -0.3 %/K, no limits printed | 21.3 V, -0.32 %/K, no limits printed |
| Voc band the maker prints | "within 10% of measured values" (guide): 0.9091 to 1.1111 x rated | -5 % / +10 % on the Voc row | **none** (only "Positive power tolerance (0%, +5%)", on Pmax) |
| Rated row at -20 C: STC irradiance; the envelope | 24.050 V; 24.728 V | 22.246 V; 22.765 V | 24.367 V; 24.961 V |
| **The band's top over the envelope, route 1 (out 3)** | **27.475 V**: the scenario 26.723 V (relative coefficient) or the extrapolation 26.428 V (absolute coefficient), plus 0.753 V for G_MAX | **25.042 V**: 24.471 V plus 0.571 V | not bounded: no maximum exists on the sheet |
| What a warranted band on Voc at STC would have to stay inside | 20.1188 to 21.6356 V | 20.0179 to 21.5240 V | 20.0944 to 21.3337 V |
| Hold inside the curve at noon at the conditioned upper corner 18.813 V (out 4) | NO over the band (band bottom: 18.228 V); yes at the rated row (20.051 V) | NO (rated: 18.420 V) | yes on the nominal model only (19.942 V; no band) |
| **Route 1 (bounded AND held AND portable)** | no | no | no |
| Route 2, PANEL-ACC on a unit equal to the typical rows: A-1 / A-2 / A-3 (out 10) | 24.8955 V / 26.68 W / 8.18 A: all pass | 22.917 V / 0.00 W / 8.44 A: A-2 fails | 25.120 V / 41.06 W / 12.25 A: A-1 and A-3 fail |
| Energy into the stage, nominal hold 17.593 V, drafted limit 3.4713 A (out 8) | 350.0 Wh a day (A2 short 986.9 / 1196.1 Wh at 48 h) | 245.0 Wh | 528.3 Wh (156 Wp) |
| Hot Isc (+70 C); x 1.25 (out 5) | 7.12 A at the band's top; 8.90 A | 7.28 A at the band's top; 9.10 A | 9.61 A nominal (no Isc band); 12.01 A with the factor transferred from SunPower's guide, over 10 A |
| Portable class (out 6) | semi-flexible laminate, 1153 x 556 x 20 mm, 2.00 kg | folding, 1059 x 775 x 20 mm open, 2.00 kg, rated -20 to +60 C only | flexible laminate, 1364 x 683 x 2 mm, 2.24 kg |

**Route 1 (a maker-bound sheet) closes nothing today.** No maker's document read bounds its band over the envelope:
SunPower's band (10 % of measured) reaches 27.475 V, BougeRV's (-5 / +10 %) 25.042 V (it was under 25 V only at STC
irradiance, 24.471 V), and Solbian prints none. A maker's warranted band would have to stay inside the windows in the
table; the drafts in `clarification/` ask SunPower and Solbian for one (the owner sends them; the session contacts no
outside party). For a printed band to close route 1 its spread (top over bottom) must be at most 1.0617 to 1.0775 for these
three curve shapes (out 7), about +-3.0 to +-3.7 %.

**Route 2 (a controlled unit) is feasible, so U-03 is a conditional downstream selection, not an architecture-level
choice.** REQ-016's window, the stage, its hold and the drafted limit stay; the panel is selected at Layer 6 by measuring
one identified unit against the contract below. It is CONDITIONAL on: a bought unit passing A-1 to A-3 by its own
measurement; L4-E7's drafted input limit applied (A-4, its 96.25 W CONDITIONAL); the unit's trace rerun (A1, A2).
**NO PHYSICAL UNIT IS ACCEPTED**: none is bought or measured; the purchase and the measurement are the owner's actions
(money). REQ-016 need not change, so no owner question is raised.

## PANEL-ACC: the contract for one identified unit (out 10)

**The unit (SESSION): one SunPower SPR-E-Flex-100, recorded by serial number.** Why: a unit equal to its typical rows
passes A-1 to A-3 at the specification, where BougeRV's rated curve gives nothing at the corner (A-2) and Solbian's rated
row is over the envelope (A-1) and over the entry with the transferred factor (A-3). It is the energy record's pinned panel,
and its rated row has the largest cold margin of the hold-matched panels.

**The measurements on the unit** (Layer 6, an I-V characterization over temperature and irradiance):
- M1, the I-V curve at STC (25 C cells, 1000 W/m2): Isc, Voc25, Vmp, Imp.
- M2, Voc at -20 +- 1 C cells and 1000 W/m2 (a cooled flash or a cold-chamber measurement): Vm20.
- M3, Voc at 25 C at a second irradiance of at most 500 W/m2: the irradiance slope A25 = dVoc / d ln G.
- M4, Voc at a warm point of at least +40 C cells and 1000 W/m2: the warm-side coefficient beta (relative, from 25 C).

**The measurement specification (SESSION, a requirement on the measurement, not a claim about a laboratory):** the
laboratory states its expanded uncertainties (k = 2), each at or under: U_V 0.10 V on each Voc (the cell temperature's own
uncertainty inside it), U_A 10 % of A25, U_beta 10 % of beta, U_I 2 % of Isc. The sheet's coefficient carries no limits, so
the coefficient is measured on the unit, and the cold point is measured, not extrapolated: extrapolating it from Voc25 would
need U_beta at or under 3.46 % for the rated unit.

**The acceptance, on the unit's own figures:**
- **A-1, the cold envelope:** Vm20 + U_V + A25 (1 + U_A) x (253.15 / 298.15) x ln(2111.4 / 1000) <= 25.000 V, that is
  Vm20 + 0.10 + A25 x 0.698023 <= 25.000 V. This is the unit's maximum open circuit plus its uncertainty over the envelope.
- **A-2, useful charging at the applicable hold corner** (the conditioned upper corner, 18.813 V): on the unit's own curve
  (its M1 points) at Voc25 - U_V, beta (1 + U_beta) and A25 (1 + U_A), the stage's input at SC-37's noon (520.7 W/m2, cells
  35.65 C, the 5 m lead) strictly above 1.3656 W; then its day traced through the replay (A1, A2).
- **A-3, the entry:** Isc (1 + U_I) at +70 C cells by the sheet's coefficient, x 1.25, at or under F2's and J_SOLAR's 10 A.
- **A-4, the 100 W into the stage:** CONDITIONAL on L4-E7's drafted input limit applied on board E and its bench rows; the
  unit's maximum at -20 C and 1000 W/m2 is 117.4 W, over 100 W as drawn (out 5). Not a measured condition of the unit.

**Demonstration on a unit equal to the typical rows** (INFERRED: the sheet's coefficient, the larger of its two readings,
gives Vm20 24.050 V; the fit gives A25 1.0673 V; a real unit replaces each by its measurement): **A-1 24.8955 V**, margin
0.1045 V (24.050 + 0.10 + 0.7450); **A-2 26.68 W** at the noon corner; **A-3 8.18 A** (6.545 A before the factor). All pass.

**The window** for a unit of this curve shape: **Voc25 from 20.395 V to 21.490 V** (A-2's floor, 0.9530 x rated, to A-1's
ceiling, 1.0042 x rated), and **Vm20 at most 24.152 V**. The rated 21.4 V lies inside it. The unit's own measurements
decide; these are the specification's limits for its shape.

**The energy of the worst accepted units** (each at its acceptance's worst curve, the drafted limit, the replay's A1 and A2):

| Unit and hold | Wh a day | A1 unserved at 48 h (06 / 18 UTC) | A2 unserved at 48 h | A2 least addition 48 / 72 h |
|---|---|---|---|---|
| the rated unit, the conditioned upper corner 18.813 V | 205.5 Wh | 1628.4 / 1645.8 Wh | 1381.7 / 1340.9 Wh | +1224.8 / +2088.2 Wh |
| the rated unit, the nominal hold 17.593 V | 336.4 Wh | 1389.8 / 1390.1 Wh | 1010.1 / 1250.7 Wh | +1002.4 / +1754.5 Wh |
| the floor unit, the conditioned upper corner 18.813 V | 16.0 Wh | 1943.6 / 1946.5 Wh | 1541.5 / 1555.1 Wh | +1548.7 / +2574.2 Wh |

The floor unit sits on the useful-power line at noon by construction; it charges, but little. The 100 W screening stimulus
gives 982.6 Wh a day; the unadjusted SunPower trace 350.0 Wh. The endurance objective's shortfall stands as the energy
record states it.

**The downstream item, PANEL-ACC (Layer 6, component selection; the purchase is the owner's):** accept the panel by route 1
(the bought revision's document, filed with its sha256, bounds its band over the envelope at or under 25 V and keeps the hold
inside the curve, out 3 and out 4) or by route 2 (the identified unit passes A-1 to A-3 at the specification, out 10); in
either case rerun its trace through the replay's section 12 and L4-E7's section 5 (A1 and A2), keep F2's and J_SOLAR's 10 A
(A-3) and the 100 W on L4-E7's limit (A-4).

## Each candidate's maker rows, with their sources (out 2, 3)

**SunPower SPR-E-Flex-100.** Datasheet 523809 Rev D (a distributor's issue, January 2023; held back) p.1, under "Typical
Electrical Data at STC: 25°C, 1000 W/m² and AM 1.5": Pnom 100 W, power tolerance +6/-3 %, Vmpp 17.1 V, Impp 5.9 A, Voc
21.4 V, Isc 6.3 A, voltage coefficient -58.9 mV/C, current +2.6 mA/C, power -0.35 %/C, 32 cells, 2 kg. Guide 524958 Rev F
(held back), Table 1's note on PDF p.3: "Rated electrical characteristics are within 10% of measured values at Standard Test
Conditions of: 1000W/m2, 25°C cell temperature and solar spectral irradiation of AM 1.5 spectrum." Read in its own words
(|rated - measured| at most 10 % of measured), a unit's Voc lies between 19.455 V and 23.778 V at STC. At -20 C and STC
irradiance that top gives 26.723 V as a SCENARIO with the coefficient relative to the unit's Voc, and 26.428 V as an
EXTRAPOLATION with the printed absolute coefficient; neither is a warranted maximum, the maker printing no coefficient
limits. With the envelope's irradiance the band's top reaches 27.475 V.

**BougeRV SP001.** The product page's "Product Specifications" table (fetched 2026-10-02T04:28Z, HTML sha256
ffc8cf99...; transcribed and filed): "Open Circuit Voltage Voc (V): 19.6V(-5%,+10%)", "Temperature Coefficient Voc:
-0.3%/℃", "Max. Power Voltage Vmp (V): 16.7V(-5%,+10%)", "Operating Temperature Limits: -4℉ ~ +140℉". At -20 C and STC
irradiance the band's top is 24.471 V; over the envelope 25.042 V, over 25 V. Its rated curve also sits under the hold's
upper corner. The page states no test conditions (taken as STC, an ASSUMPTION) and no NOCT; its Vmp x Imp is 103.0 W
against its 100 W; its operating limit of +60 C sits under the cells' 73.8 C in full sun at the envelope's +40 C (INFERRED).

**Solbian SX 156.** SX series datasheet p.2 (February 2023; held back), the SX 156 column: 156 W, Vmp 17.6 V, Imp 8.9 A, Voc
21.3 V, Isc 9.4 A, NOCT 45 +- 2 C, Voc -0.32 %/C, 32 cells, 2.24 kg; the STC note "Measurements carried out according to
the Standard IEC 61215 requirements"; p.1 "Positive power tolerance (0%, +5%)". No Voc tolerance anywhere on the sheet: not
bounded. Its hold compatibility is on the nominal model only, since no band exists to test; its rated row alone is
24.961 V over the envelope.

## The hold and the energy (out 4, 5, 8)

The hold is L4-E7's selected one (drafted, not applied): 17.593 V nominal, 16.970 / 18.221 V with EA3 at its typical gain,
**16.420 / 18.813 V the widest conditioned band** (EA3 at half, the resistors' drifts), and the input limit 3.4713 A (its
lowest 3.1404 A). The energy is the replay's: PVGIS's figure for the panel's Wp on SC-37's mean September day times the
single-diode model's operating point over its own maximum-power point (the method check reproduces the replay's 373.5 /
350.0 / 280.6 Wh and L4-E7's 369.7 / 350.0 / 307.9 / 375.0 / 240.0 Wh, and A1 and A2 at L4-E7's nominal row, out 0). The
noon screen (the open circuit above the hold corner) is a necessary model condition, not proof of useful power; PANEL-ACC's
A-2 asks for power above the useful-power line on the unit's own curve. Every panel takes over 100 W at the cold, bright
corner as drawn; the window's 100 W rests on L4-E7's drafted limit (96.25 W to 25 V, CONDITIONAL on five unprinted values).

## The screen (out 9)

Fourteen makers' documents were read on 2 October 2026 and not taken (`inputs/screen-2026-10-02.json`, each with its address
and sha256; none filed): Solbian's SP, SR and SX issues of 2017 to 2023 and its 2011 manual, Sunman's eArche 2019 sheet and
its 2023 RV and marine guide, Merlin Solar's Panther, Rich Solar, wattstunde, Offgridtec, SLD Tech's drawing and Victron's
12 V rows. This is search history: it records what was read and why it was set aside, not proof that no other panel can
qualify. The makers who print an open-circuit band at all print 5 to 10 %.

## Decisions taken (SESSION, under the owner's standing rule of 26 September 2026)

```
decision: L4E13-01, the envelope of the bound
authority: SESSION
authority_why: a reading of the records' settled temperature and a physical bound on irradiance from a read source; no owner
  judgement standing (REQ-024 and D-02a give -20 C)
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: cold-soaked cells at -20 C under G_MAX = 1.5 x the extraterrestrial irradiance at perihelion, 2111.4 W/m2
reversed_by: a ruling that REQ-016 is read at the panel's own lower limit, or a measured irradiance bound for the kit's sites
```

```
decision: L4E13-02, SunPower's 10 % sentence and the coefficient
authority: SESSION
authority_why: the maker's words and the larger of two readings; no measurement or owner choice moves it
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: |rated - measured| at most 10 % of measured (19.455 to 23.778 V); the relative-coefficient scenario and the
  absolute-coefficient extrapolation both printed, neither taken as warranted; the route-1 floor takes the higher of the two
reversed_by: the maker's written limit (clarification/sunpower-spr-e-flex-100.txt)
```

```
decision: L4E13-03, the hold the panel is judged against and the useful-power line
authority: SESSION
authority_why: L4-E7's selected settings give the band; the widest conditioned band is the conservative reading; the stage's
  own drive power is the least input that charges anything
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: the conditioned upper corner 18.813 V; useful power above 1.27 W / 0.93 = 1.3656 W at the stage's input at SC-37's
  noon; the decision checked on EA3's typical band too (unchanged)
reversed_by: measured EA3 gain and resistor drifts (bench 7b.12), or the stage's measured drive power
```

```
decision: L4E13-04, the two further candidates
authority: SESSION
authority_why: at most two by the brief; chosen by what they test
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: BougeRV SP001 (the only maker's document found whose printed Voc band bounds it at STC irradiance) and Solbian SX 156
  (the maker's full sheet with the best hold match, Vmp 17.6 V, and no Voc band)
reversed_by: a maker's document printing a Voc band of at most about +-3 % on a panel rated near 21 V
```

```
decision: L4E13-05, PANEL-ACC's unit, measurements and specification
authority: SESSION
authority_why: an acceptance contract inside REQ-016 and O-1's controlled-unit closure; it spends nothing (the purchase and
  the measurement stay the owner's)
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: one SunPower SPR-E-Flex-100 by serial number; M1 to M4; U_V 0.10 V, U_A 10 %, U_beta 10 %, U_I 2 % (k = 2); A-1 to A-4
reversed_by: a laboratory unable to meet the specification (then a tighter cold margin is needed), or a unit outside the window
```

```
decision: L4E13-06, U-03
authority: SESSION
authority_why: by the brief's and the check's rule; REQ-016 need not change, money and outside contact stay the owner's
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC): route 2 stands, route 1 stays open beside it; no unit accepted
reversed_by: route 2 found infeasible (no unit passes, or the specification cannot be met) with route 1 still closed: U-03
  then returns to an architecture-level choice
```

```
decision: L4E13-07, the third-party documents
authority: SESSION
authority_why: the owner's rule of 27 September 2026 and the brief's (held back unless redistribution is clearly allowed)
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: Solbian's SX sheet held back (no terms stated), fetched by fetch_held_back.py into the ignored v2/vendor/solar/held/
  and pinned; BougeRV's page filed as a transcription of its specification table; the two CC BY 4.0 irradiance papers
  quoted with attribution (redistribution allowed; not filed whole, for size); the fourteen screen documents cited by
  address and sha256 only; v2/vendor/sources.txt carries the three lines
reversed_by: a maker's grant to redistribute
```

## What stays open

A bought unit and its measurement (PANEL-ACC, the owner's purchase); the makers' written Voc bands (the drafts); the hold's
band (L4-E7's EA3 gain and drifts, bench 7b.12); the input limit's 100 W (L4-E7, CONDITIONAL); the unit's own trace rerun.

## The check's items and their changes (checks/astra-check-l4e13-1.md)

| Item | Change |
|---|---|
| B1, the acceptance contract | PANEL-ACC is built around one identified SunPower unit: the envelope adds G_MAX = 2111.4 W/m2 with its reason; the coefficient is measured on the unit (M2 at -20 C, M4 warm) because the sheet bounds none; U_V, U_A, U_beta, U_I are the specification; A-1 bounds the unit's maximum plus its uncertainty at or under 25.000 V over the envelope; A-2 asks for power above the useful-power line at the conditioned upper corner and traces it through the replay; A-3 and A-4 keep the 10 A entry and the conditional 100 W (out 1, 10) |
| B2, the classification | `classify()` admits a maker-bound sheet or a controlled unit; U-03 reads CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC); no physical unit is accepted, the purchase stays the owner's (out 11) |
| Minor, 26.723 against 26.428 V | printed apart as a SCENARIO (relative coefficient) and an EXTRAPOLATION (absolute coefficient), neither warranted (out 3) |
| Minor, Solbian's band at the hold | relabelled nominal-model compatibility only, no band existing (out 4) |
| Minor, Solbian's 9.61 A | relabelled nominal at +70 C, the 1.25 factor marked as transferred from SunPower's guide (out 5) |
| Minor, the screen | stated as search history, not proof that no other panel can qualify (out 9) |
| Also | the route-1 bounds now include the envelope's irradiance, which moves BougeRV from bounded (24.471 V at STC) to not bounded (25.042 V); the clarification drafts carry the route-1 windows over the envelope |

## Reproduce

`python3 v2/docs/records/l4e13/l4e13_panel.py > v2/docs/records/l4e13/l4e13_panel.out` from the repository root (about a
minute and a half; needs the held documents: `v2/docs/records/a1solar/fetch_held_back.py` and
`v2/docs/records/l4e13/fetch_held_back.py`). Tests: `env -C v2/ecad/tools/tests python3 run.py test_l4e13`.
