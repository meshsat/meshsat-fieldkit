# L4-E13: a panel whose open circuit is bounded inside REQ-016's window (U-03, layer 4, MESHSAT-1357)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured, and **no physical unit is accepted**.
This is L4-E9's unresolved choice **U-03** (finding O-1 of `../l4e/L4-ENERGY-ARCHITECTURE.md`): a solar panel whose
open-circuit voltage at the coldest operating temperature is bounded at or under 25 V, at a useful power, compatible with
the stage's 17.6 V hold and portable. Third issue, after the collaborator's check (`checks/astra-check-l4e13-1.md`, NOT
YET: B1, B2, four minors) and its targeted recheck (`checks/astra-check-l4e13-2.md`, NOT YET on B1 only: the irradiance
bound, A-1's extrapolation, A-2's inputs, A-3's envelope; B2 and the minors closed but one wording). The last two sections
map each item to its change. Every figure below is printed by `l4e13_panel.py` into `l4e13_panel.out` (section named); the
script reads the makers' rows from the pinned documents, runs the energy record's replay in-process (it must print
`../l4e/l4e_replay.out` byte for byte) and uses its model, its day and its A1 and A2 runs unchanged.

## The requirement and its three checks (out 1)

REQ-016 (`v2/ecad/tools/pcb_requirements.yaml`), verbatim: "The solar input charges the pack through board E's LT8705A
stage from a panel inside its declared window: an open-circuit voltage of at most 25 V at the panel's coldest operating
temperature, the panel held at 17.6 V by the stage's input regulation, and at most 100 W into the stage." Its acceptance
names F2 and J_SOLAR at 10 A and states "Protection is judged apart from the window, under rule TRN-001". D-34 keeps the
window unchanged. The text constrains the panel's own open circuit: a series diode or a clamp is not a substitute.

The decision follows that split, in three separate checks:

1. **The window (normal operation, REQ-016's rated quantity).** The makers' rated Voc row is defined at 1000 W/m2
   (SunPower 523809 p.1, "Typical Electrical Data at STC: 25°C, 1000 W/m² and AM 1.5"; Solbian's STC note and BougeRV's rows
   alike), moved to the coldest operating temperature, **-20 C** (REQ-024's in-use minimum; the records settle the reading).
   No irradiance above 1000 W/m2 enters the window. The earlier G_MAX of 2111.4 W/m2 is **withdrawn as a decision input**.
2. **The disturbance check (component limits during an irradiance burst on cold-soaked cells, seconds to minutes),**
   judged apart under TRN-001 against the lowest rating on PV_P (out 11). It is made indifferent to any irradiance maximum.
3. **Useful charging (A-2):** the stage's input above its own drive and quiescent power over its efficiency, 1.27 W /
   0.93 = **1.365591 W** (L4-E7's 42.3 mA, 1.27 W at L4-E5's raised EXTVCC, INFERRED there; the replay's declared 0.93).

Context only, never a bound: the extraterrestrial irradiance at perihelion, E0 = 1407.6 W/m2; the read source's "over 50 %
of clear-sky irradiance" for cloud enhancement (Mol and van Heerwaarden 2025, CC BY 4.0, quoted in
`v2/vendor/solar/irradiance-enhancement-sources-2026-10-02.md`); the clear-sky noon irradiance near 1000 W/m2 at Cabauw.

## The result (out 3, 10, 11, 12)

**U-03: CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC).** Two routes close U-03; the decision admits either
(`classify()`).

| | SunPower SPR-E-Flex-100 (the identified unit) | BougeRV 100W N-Type Fiberglass Foldable | Solbian SX 156 |
|---|---|---|---|
| Maker's document | datasheet 523809 Rev D p.1 ("Typical Electrical Data"); guide 524958 Rev F Table 1 and its note (PDF p.3, printed p.2), 3.0 (PDF p.2), 5.1 (PDF p.4); both held back | the maker's product page, transcribed (`v2/vendor/solar/bougerv-sp001-...-2026-10-02.md`); no STC statement, no NOCT | SX series datasheet, February 2023, p.2 (the SX 156 column, the STC note) and p.1; held back |
| Rated Voc, coefficient | 21.4 V, -58.9 mV/K (-0.2752 %/K), no limits printed | 19.6 V, -0.3 %/K, no limits printed | 21.3 V, -0.32 %/K, no limits printed |
| Voc band the maker prints | "within 10% of measured values" (guide): 0.9091 to 1.1111 x rated | -5 % / +10 % on the Voc row | **none** (only "Positive power tolerance (0%, +5%)", on Pmax) |
| Rated row in the window (-20 C, 1000 W/m2) | 24.050 V | 22.246 V | 24.367 V |
| **The band's top in the window, route 1 (out 3)** | **26.723 V** (the scenario, relative coefficient; 26.428 V the extrapolation, absolute coefficient; neither warranted) | **24.471 V** | not bounded: no maximum exists on the sheet |
| What a warranted band on Voc at STC would have to stay inside | 20.1188 to 22.2449 V | 20.0179 to 22.0264 V | 20.0944 to 21.8531 V |
| Hold inside the curve at noon at the conditioned upper corner 18.813 V (out 4) | NO over the band (band bottom: 18.228 V); yes at the rated row (20.051 V) | NO (rated: 18.420 V) | yes on the nominal model only (19.942 V; no band) |
| **Route 1 (bounded AND held AND portable)** | no | no | no |
| Route 2 on a unit equal to the typical rows: A-1 / A-2 lower bound / A-3(b) (out 10) | 24.1505 V / 27.0849 W / 8.1817 A: all pass | 22.346 V / 0.000 W / 8.44 A: A-2 fails | 24.467 V / 41.671 W / 12.25 A: A-3(b) fails with the transferred factor |
| Energy into the stage, nominal hold 17.593 V, drafted limit 3.4713 A (out 8) | 350.0 Wh a day (A2 short 986.9 / 1196.1 Wh at 48 h) | 245.0 Wh | 528.3 Wh (156 Wp) |
| Portable class (out 6) | semi-flexible laminate, 1153 x 556 x 20 mm, 2.00 kg | folding, 1059 x 775 x 20 mm open, 2.00 kg, rated -20 to +60 C only | flexible laminate, 1364 x 683 x 2 mm, 2.24 kg |

**Route 1 (a maker-bound sheet) closes nothing.** In the window SunPower's band (10 % of measured) reaches 26.723 V
(over 25 V); BougeRV's (-5 / +10 %) is bounded at 24.471 V but its rated curve sits under the hold's upper corner, so it
gives the stage nothing there; Solbian prints no band. A maker's warranted band would have to stay inside the windows in
the table; the drafts in `clarification/` ask SunPower and Solbian for one (the owner sends them; the session contacts no
outside party). For a printed band to close route 1, its spread (top over bottom) must be at most 1.0875 to 1.1079 for
these three curve shapes (out 7), about +-4.2 to +-5.1 %.

**Route 2 (a controlled unit) is feasible, so U-03 is a conditional downstream selection, not an architecture-level
choice.** REQ-016's window, the stage, its hold and the drafted limit stay; the panel is selected at Layer 6 by measuring one
identified unit against the contract below. It is CONDITIONAL on: a bought unit passing A-1, A-2 and A-3(b) by its own
measurement; L4-E7's drafted input limit applied (A-3(a), A-4; its 96.25 W CONDITIONAL); A-3(c)'s connector and conductor
rating at Layer 5/6; the disturbance check's assumption and M3's n; the unit's trace rerun. None of these can overturn the
architecture: A-3(c) is a connector rating (REQ-016's "rated 10 A" is a minimum) and the rest decide a unit, not the
topology. **NO PHYSICAL UNIT IS ACCEPTED**: none is bought or measured; the purchase and the measurement are the owner's
actions (money). REQ-016 need not change, so no owner question is raised.

## PANEL-ACC: the contract for one identified unit (out 10)

**The unit (SESSION): one SunPower SPR-E-Flex-100, recorded by serial number.** Under the same contract BougeRV's rated
curve gives the stage nothing at the corner (A-2), and Solbian's rated row passes A-1 with 0.533 V to spare against
SunPower's 0.849 V while its hot short circuit is 9.80 A before any allowance, over 10 A with the 1.25 factor its own maker
does not print (SunPower's, transferred). SunPower's 1.25 is its own instruction, and it is the energy record's pinned panel.

**The measurements on the unit** (Layer 6): M1, the I-V curve at STC (Isc, Voc25, Vmp, Imp); M2, Voc at -20 +- 1 C cells
and 1000 W/m2 (a cooled flash or a cold-chamber measurement), Vm20; M3, Voc at 25 C at a second irradiance of at most 500
W/m2, giving the slope A25 = dVoc / d ln G and n = A25 / (Ns kT/q at 298.15 K); A-2's current reading below. M5 (Voc above
1000 W/m2 on the cold unit) is optional and not an acceptance row.

**The measurement specification (SESSION, a requirement on the measurement, not a claim about a laboratory):** expanded
uncertainties (k = 2) at or under U_V 0.10 V on each voltage (M2's cell temperature inside it), U_A 10 % of A25, U_I 2 % of
a current, U_G 2 % of A-2's irradiance setting, U_TC 1.0 K on A-2's cell temperature.

**The acceptance, on the unit's own measurements:**
- **A-1, the window:** Vm20 + U_V <= 25.000 V. No slope, no extrapolation, no temperature scaling.
- **A-2, useful charging, measured** at SC-37's noon corner offset to the conservative side: irradiance at or under
  520.7 W/m2 minus U_G (510.3 W/m2 at the specification), cells at or above 35.65 C plus U_TC (36.65 C), the current I read
  at the panel voltage 18.813 V + I x R_lead (the 5 m lead, 0.0465 Ohm, ESTIMATE as the record states it); P = 18.813 V x I;
  accepted on **P - U_P strictly above 1.365591 W**, U_P = 18.813 V x sqrt((U_I I)^2 + (dI/dV U_V)^2) with dI/dV the measured
  local slope. The offsets are conservative: on the model at the corner, dI/dG is +0.00446 A per W/m2 (less light, less
  current) and dI/dT is -0.06749 A/K (warmer cells, less current) for the rated unit (+0.00361 and -0.09478 for the floor
  unit), and the hold's 18.813 V lies above Vmp there (16.267 V; 15.442 V for the floor unit).
- **A-3, the entry, three cases:**
  - (a) normal operation: the entry carries the stage's input current, bounded by L4-E7's drafted limit and independent of
    irradiance, at most 99.6739 W / 25.000 V = **3.9870 A** (the design floor's worst corner, stack C), CONDITIONAL with A-4;
  - (b) a sustained input fault (a short downstream of F2, D4 failing short): the panel's Isc for hours at +70 C cells,
    (1 + U_I), x 1.25, at or under 10 A: **8.1817 A** for the typical unit. The 1.25 is the maker's own sizing allowance,
    printed in section 3.0 of guide 524958 Rev F (PDF p.2; the coordinator's direction named section 5.1, which holds the
    operating temperature): "Under normal conditions, a photovoltaic module may experience conditions that produce more
    current and/or voltage than reported at Standard Test Conditions. Accordingly, the values of ISC and VOC marked on the
    modules should be multiplied by a factor of 1.25 when determining component voltage ratings, conductor capacities, fuse
    sizes and size of controls connected to the module output.";
  - (c) the enhancement transient during an existing input fault (a double contingency): F2 opening is the safe outcome; if
    F2 holds, J_SOLAR and PV_IN carry Isc_hot (1 + U_I) x G_T / 1000 for the event, **13.8200 A** for the typical unit at
    G_T = 2111.4 W/m2, a SESSION design level for this case only (the source's enhancement on E0, not a claimed maximum).
    J_SOLAR's held catalogue (JST VH) prints "Current rating: 10 A AC/DC" and a -40 to +105 C range and no short-time
    overload: a COMPONENT_LIMITATION, carried as PANEL-ACC row A-3(c): J_SOLAR and PV_IN rated at least that current at their
    maximum ambient, or a bench row. A 20 A part would cover the case up to 3056 W/m2, 2.17 x E0.
- **A-4, the 100 W into the stage:** CONDITIONAL on L4-E7's drafted input limit applied on board E and its bench rows; the
  unit's maximum at -20 C and 1000 W/m2 is 117.4 W, over 100 W as drawn (out 5).

**Demonstration on a unit equal to the typical rows** (INFERRED: the sheet's coefficient, the larger of its two readings,
gives Vm20 24.0505 V; the energy record's fit gives the curve): **A-1 24.1505 V, margin 0.8495 V**; **A-2** I 1.5508 A,
P 29.1760 W, dI/dV -1.0674 A/V, U_P 2.0911 W, **lower bound 27.0849 W**; A-3 (a) 3.9870 A, (b) 8.1817 A, (c) 13.8200 A.

**The window** for a unit of this curve shape: **Voc25 from 20.315 V to 22.156 V** (A-2's floor, 0.9493 x rated, to A-1's
ceiling, 1.0353 x rated), and **Vm20 at most 24.900 V**. The rated 21.4 V lies inside it. A laboratory without a cold chamber
could extrapolate Vm20 from M1 with a coefficient measured to within 27.7 % for the rated unit; the contract keeps M2
measured.

**The energy** (the drafted limit, the replay's A1 and A2):

| Unit and hold | Wh a day | A1 unserved at 48 h (06 / 18 UTC) | A2 unserved at 48 h | A2 least addition 48 / 72 h |
|---|---|---|---|---|
| the rated unit, the conditioned upper corner 18.813 V | 240.0 Wh | 1559.2 / 1595.8 Wh | 1352.7 / 1255.3 Wh | +1166.1 / +2000.1 Wh |
| the rated unit, the nominal hold 17.593 V | 350.0 Wh | 1367.4 / 1368.1 Wh | 986.9 / 1196.1 Wh | +979.2 / +1719.7 Wh |
| the floor unit, the conditioned upper corner 18.813 V | 52.3 Wh | 1872.5 / 1878.1 Wh | 1510.9 / 1555.1 Wh | +1486.5 / +2480.8 Wh |

The rated unit's two rows equal L4-E7's own (its "NEW conditioned upper end" and "NEW nominal" rows). The floor unit sits on
the useful-power line at A-2's conservative corner; it charges, but little. The endurance objective's shortfall stands as the
energy record states it.

## The disturbance check (out 11)

**The limit.** The lowest rating on PV_P for a current-limited source held for minutes is D4's printed standoff: the
SMCJ28A's **VR 28.0 V**, at most 1 uA there (Littelfuse SMCJ sheet p.2: VR 28.0, VBR 31.10 to 34.40 V at 1 mA, VC 45.4 V at
33.1 A, IR 1 uA). The sheet prints VBR(TJ) = VBR(25 C) x (1 + aT (TJ - 25)) with aT 0.1 %/C typical (p.1), so the cold VBR
minimum at -20 C is 29.70 V (a typical coefficient). C11 and C12's 35 V lie above.

**The irradiance term, by junction physics.** dVoc / d ln G <= n x Ns x kT/q, Ns 32 (the sheet), T 253.15 K (kT/q 0.021815 V).
n_max = 2 is a **MODELLING_ASSUMPTION**: a silicon junction's ideality lies between 1 (diffusion current) and 2 (recombination
in the depletion region). M3's measured n = A25 / (Ns kT/q at 298.15 K) must read at or under 2 with its uncertainty, else
this check is re-judged; the typical unit's fit gives n 1.2981 (1.4279 with U_A).

**The coldest cells are the worst case.** d/dT [Voc(T, 1000) + n Ns kT/q ln(G / 1000)] = beta + n Ns k/q ln(G / 1000). Up to
the threshold below, the second term is at most 3.000 V / 253.15 K = 0.011851 V/K, against the sheet's coefficient of at least
0.0589 V/K in magnitude: the derivative stays negative, so cells warmer than -20 C give less.

**The threshold.** A unit at A-1's ceiling (Vm20 + U_V = 25.000 V) reaches D4's 28.0 V standoff at G = 1000 exp(3.000 V /
(n Ns kT/q)):

| n | V per unit of ln G at -20 C | threshold | x E0 |
|---|---|---|---|
| 1.2981 (the typical unit's fit, INFERRED) | 0.9062 V | 27401 W/m2 | 19.47 |
| **2 (n_max, the decision row)** | 1.3961 V | **8574 W/m2** | **6.09** |
| 3 (a sensitivity) | 2.0942 V | 4189 W/m2 | 2.98 |

**Result: the disturbance check is implied by A-1 for every plane-of-array irradiance below 8574 W/m2 (n <= 2)**, 6.09 times
the extraterrestrial irradiance; no irradiance maximum is a decision input. **ASSUMPTION:** the plane-of-array irradiance
stays below that threshold (the read enhancement on E0 gives 2111.4 W/m2, context only). **Its impact if it fails:** D4 rises
above its standoff and conducts under 1 mA until its VBR (29.70 V cold minimum), with no damage below VBR. **Its
verification:** none beyond M3's n check (M5 optional). Cross-check: SunPower's own allowance, 1.25 x Voc for component voltage
ratings, gives 26.75 V on the rated row and 27.69 V at the window's Voc25 ceiling, both under the 28.0 V standoff.

## Each candidate's maker rows, with their sources (out 2, 3)

**SunPower SPR-E-Flex-100.** Datasheet 523809 Rev D (a distributor's issue, January 2023; held back) p.1, under "Typical
Electrical Data at STC: 25°C, 1000 W/m² and AM 1.5": Pnom 100 W, power tolerance +6/-3 %, Vmpp 17.1 V, Impp 5.9 A, Voc
21.4 V, Isc 6.3 A, voltage coefficient -58.9 mV/C, current +2.6 mA/C, power -0.35 %/C, 32 cells, 2 kg. Guide 524958 Rev F
(held back), Table 1's note on PDF p.3: "Rated electrical characteristics are within 10% of measured values at Standard Test
Conditions of: 1000W/m2, 25°C cell temperature and solar spectral irradiation of AM 1.5 spectrum." Read in its own words
(|rated - measured| at most 10 % of measured), a unit's Voc lies between 19.455 V and 23.778 V at STC. In the window that top
gives 26.723 V as a SCENARIO with the coefficient relative to the unit's Voc, and 26.428 V as an EXTRAPOLATION with the
printed absolute coefficient; neither is a warranted maximum, the maker printing no coefficient limits.

**BougeRV SP001.** The product page's "Product Specifications" table (fetched 2026-10-02T04:28Z, HTML sha256
ffc8cf99...; transcribed and filed): "Open Circuit Voltage Voc (V): 19.6V(-5%,+10%)", "Temperature Coefficient Voc:
-0.3%/℃", "Max. Power Voltage Vmp (V): 16.7V(-5%,+10%)", "Operating Temperature Limits: -4℉ ~ +140℉". In the window the band's
top is 24.471 V, bounded; its rated curve sits under the hold's upper corner. The page states no test conditions (taken as
STC, an ASSUMPTION) and no NOCT; its Vmp x Imp is 103.0 W against its 100 W; its operating limit of +60 C sits under the
cells' 73.8 C in full sun at the envelope's +40 C (INFERRED).

**Solbian SX 156.** SX series datasheet p.2 (February 2023; held back), the SX 156 column: 156 W, Vmp 17.6 V, Imp 8.9 A, Voc
21.3 V, Isc 9.4 A, NOCT 45 +- 2 C, Voc -0.32 %/C, 32 cells, 2.24 kg; the STC note "Measurements carried out according to
the Standard IEC 61215 requirements"; p.1 "Positive power tolerance (0%, +5%)". No Voc tolerance anywhere on the sheet: not
bounded. Its hold compatibility is on the nominal model only, since no band exists to test.

## The hold and the energy (out 4, 5, 8)

The hold is L4-E7's selected one (drafted, not applied): 17.593 V nominal, 16.970 / 18.221 V with EA3 at its typical gain,
**16.420 / 18.813 V the widest conditioned band** (EA3 at half, the resistors' drifts), and the input limit 3.4713 A (its
lowest 3.1404 A). The energy is the replay's: PVGIS's figure for the panel's Wp on SC-37's mean September day times the
single-diode model's operating point over its own maximum-power point (the method check reproduces the replay's 373.5 /
350.0 / 280.6 Wh and L4-E7's 369.7 / 350.0 / 307.9 / 375.0 / 240.0 Wh, and A1 and A2 at L4-E7's nominal row, out 0). The
noon screen (the open circuit above the hold corner) is a necessary model condition, not proof of useful power; PANEL-ACC's
A-2 measures the power. Every panel takes over 100 W at the cold, bright corner as drawn; the window's 100 W rests on L4-E7's
drafted limit (96.25 W to 25 V, CONDITIONAL on five unprinted values).

## The screen (out 9)

Fourteen makers' documents were read on 2 October 2026 and not taken (`inputs/screen-2026-10-02.json`, each with its address
and sha256; none filed): Solbian's SP, SR and SX issues of 2017 to 2023 and its 2011 manual, Sunman's eArche 2019 sheet and
its 2023 RV and marine guide, Merlin Solar's Panther, Rich Solar, wattstunde, Offgridtec, SLD Tech's drawing and Victron's
12 V rows. This is search history: it records what was read and why it was set aside, not proof that no other panel can
qualify. The makers who print an open-circuit band at all print 5 to 10 %.

## Decisions taken (SESSION, under the owner's standing rule of 26 September 2026)

```
decision: L4E13-01, the window and the disturbance check
authority: SESSION
authority_why: REQ-016's own text: its rated quantity is the open circuit at the coldest temperature, and "Protection is
  judged apart from the window, under rule TRN-001"; the records settle -20 C (REQ-024, D-02a)
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: the window is the rated Voc row (1000 W/m2) at -20 C; the disturbance check is D4's 28 V standoff against a unit at
  A-1's ceiling under an irradiance burst, bounded by junction physics (n_max = 2); no irradiance maximum is a decision input
reversed_by: a ruling that REQ-016 includes irradiance above 1000 W/m2, or a measured n above 2 on the unit (M3)
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
choice: the conditioned upper corner 18.813 V; useful power above 1.27 W / 0.93 = 1.365591 W at the stage's input at SC-37's
  noon, measured on the conservative side; the decision checked on EA3's typical band too (unchanged)
reversed_by: measured EA3 gain and resistor drifts (bench 7b.12), or the stage's measured drive power
```

```
decision: L4E13-04, the two further candidates
authority: SESSION
authority_why: at most two by the brief; chosen by what they test
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: BougeRV SP001 (the only maker's document found whose printed Voc band bounds it in the window) and Solbian SX 156
  (the maker's full sheet with the best hold match, Vmp 17.6 V, and no Voc band)
reversed_by: a maker's document printing a Voc band of at most about +-4 % on a panel rated near 21 V
```

```
decision: L4E13-05, PANEL-ACC's unit, measurements, specification and A-3(c)'s design level
authority: SESSION
authority_why: an acceptance contract inside REQ-016 and O-1's controlled-unit closure; it spends nothing (the purchase and
  the measurement stay the owner's); A-3(c)'s level is a design level for a double contingency, not a claimed maximum
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: one SunPower SPR-E-Flex-100 by serial number; M1 to M3 and A-2's reading; U_V 0.10 V, U_A 10 %, U_I 2 %, U_G 2 %,
  U_TC 1.0 K (k = 2); A-1 to A-4; G_T 2111.4 W/m2 for A-3(c) only
reversed_by: a laboratory unable to meet the specification, a unit outside the window, or a Layer 5/6 connector choice that
  settles A-3(c) another way
```

```
decision: L4E13-06, U-03
authority: SESSION
authority_why: by the brief's and the checks' rule; REQ-016 need not change, money and outside contact stay the owner's
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

A bought unit and its measurement (PANEL-ACC, the owner's purchase); the makers' written Voc bands (the drafts); J_SOLAR's
and PV_IN's rating for A-3(c) (COMPONENT_LIMITATION, Layer 5/6); the disturbance check's assumption, verified only by M3's n;
the hold's band (L4-E7's EA3 gain and drifts, bench 7b.12); the input limit's 100 W (L4-E7, CONDITIONAL); the unit's own
trace rerun.

## The first check's items and their changes (checks/astra-check-l4e13-1.md)

| Item | Change (second issue; see the third issue below where it moved again) |
|---|---|
| B1, the acceptance contract | PANEL-ACC built around one identified SunPower unit, with measurements, a specification and acceptance rows A-1 to A-4 (out 10) |
| B2, the classification | `classify()` admits a maker-bound sheet or a controlled unit; U-03 reads CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC); no physical unit is accepted (out 12) |
| Minor, 26.723 against 26.428 V | printed apart as a SCENARIO (relative coefficient) and an EXTRAPOLATION (absolute coefficient), neither warranted (out 3) |
| Minor, Solbian's band at the hold | relabelled nominal-model compatibility only, no band existing (out 4) |
| Minor, Solbian's 9.61 A | relabelled nominal at +70 C, the 1.25 factor marked as transferred from SunPower's guide (out 5) |
| Minor, the screen | stated as search history, not proof that no other panel can qualify (out 9) |

## The recheck's items and their changes (checks/astra-check-l4e13-2.md)

| Item | Change (third issue) |
|---|---|
| B1, the irradiance bound | G_MAX withdrawn as a decision input. The window is REQ-016's rated quantity at 1000 W/m2 and -20 C; the disturbance check is judged apart (REQ-016: "Protection is judged apart from the window, under rule TRN-001") against D4's 28 V standoff, bounded by junction physics; it holds for every irradiance below 8574 W/m2 (n <= 2), so no irradiance maximum enters the decision (out 1, 11) |
| B1, A-1's model uncertainty | A-1 is Vm20 + U_V <= 25.000 V on M2's direct measurement at -20 C and 1000 W/m2: no slope, no extrapolation, no temperature scaling. M3's slope only verifies n <= 2 for the disturbance check (out 10, 11) |
| B1, A-2's inputs | A-2 is a direct measurement at the noon corner offset to the conservative side, accepted on P - U_P above 1.365591 W, U_P from U_I and U_V through the measured dI/dV; the model's signs show the offsets conservative and the hold above Vmp (out 10) |
| B1, A-3's envelope | A-3 split three ways: (a) normal operation under L4-E7's limit, 3.9870 A; (b) a sustained input fault with the maker's 1.25 (its section 3.0 quoted), 8.1817 A; (c) the enhancement transient during a fault at a stated design level, 13.8200 A, a COMPONENT_LIMITATION carried as PANEL-ACC row A-3(c) for J_SOLAR and PV_IN (out 10) |
| B2 and the minors | closed by the recheck; kept |
| Remaining minor, 27.475 V | the band-top-over-envelope figures are removed: route 1 is read in the window only (26.723 V the scenario, 26.428 V the extrapolation) (out 3) |
| Also | the route-2 window moves to Voc25 20.315 to 22.156 V and Vm20 at most 24.900 V; the typical unit's A-1 margin to 0.8495 V; the worst accepted units' energy table to the rated unit's own traces (240.0 and 350.0 Wh, L4-E7's rows) and the floor unit (52.3 Wh); the clarification drafts carry the window's bands (20.12 to 22.24 V, 20.10 to 21.85 V) |

## Reproduce

`python3 v2/docs/records/l4e13/l4e13_panel.py > v2/docs/records/l4e13/l4e13_panel.out` from the repository root (about a
minute and a half; needs the held documents: `v2/docs/records/a1solar/fetch_held_back.py` and
`v2/docs/records/l4e13/fetch_held_back.py`). Tests: `env -C v2/ecad/tools/tests python3 run.py test_l4e13`.
