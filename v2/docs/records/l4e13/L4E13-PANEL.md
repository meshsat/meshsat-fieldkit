# L4-E13: a panel whose maker bounds its open circuit inside REQ-016's window (U-03, layer 4, MESHSAT-1357)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured. This is L4-E9's unresolved choice
**U-03** (finding O-1 of `../l4e/L4-ENERGY-ARCHITECTURE.md`): a solar panel whose MAKER's document bounds its open-circuit
voltage at the coldest operating temperature, with the sheet's own tolerance and temperature coefficient, at or under 25 V,
at a useful power, compatible with the stage's 17.6 V hold and portable. Every figure below is printed by
`l4e13_panel.py` into `l4e13_panel.out` (section named); the script reads the makers' rows from the pinned documents, runs
the energy record's replay in-process (it must print `../l4e/l4e_replay.out` byte for byte) and uses its model, its day and
its A1 and A2 runs unchanged. Evidence classes: MAKER, MAKER-PAGE (a maker's web page, transcribed), RECORD, MODELED,
INFERRED, ASSUMPTION, SESSION.

## The requirement (out 1)

REQ-016 (`v2/ecad/tools/pcb_requirements.yaml`), verbatim: "The solar input charges the pack through board E's LT8705A
stage from a panel inside its declared window: an open-circuit voltage of at most 25 V at the panel's coldest operating
temperature, the panel held at 17.6 V by the stage's input regulation, and at most 100 W into the stage." Its acceptance
names F2 and J_SOLAR at 10 A. D-34 keeps the window unchanged. The text constrains the panel's own open circuit: a series
diode or a clamp in the window is not a substitute (D4 is judged apart under TRN-001).

The coldest operating temperature is **-20 C**, REQ-024's in-use minimum (`pcb_envelope.yaml` agrees); the records settle
that reading (L4-ENERGY, "What stays INCONCLUSIVE"). With no irradiance the cells sit at the ambient; the bound puts STC
irradiance on cells still at -20 C (a cold, clear sunrise before the cells warm), the usual worst case for the open
circuit; less irradiance only lowers Voc. An edge-of-cloud 1250 W/m2 is printed as a sensitivity, not as part of the bound.

## The result

**No candidate qualifies, so U-03 stays an unresolved choice (not a downstream purchase item).** It decides the solar
source, not the topology: REQ-016's window, the stage, its hold and the drafted input limit stay. REQ-016 need not change,
so no owner question is raised.

| | SunPower SPR-E-Flex-100 (the present candidate) | BougeRV 100W N-Type Fiberglass Foldable | Solbian SX 156 |
|---|---|---|---|
| Maker's document | datasheet 523809 Rev D p.1 ("Typical Electrical Data"); guide 524958 Rev F Table 1 and its note (PDF p.3, printed p.2), 5.1 (PDF p.4); both held back | the maker's product page, transcribed (`v2/vendor/solar/bougerv-sp001-...-2026-10-02.md`); no STC statement, no NOCT | SX series datasheet, February 2023, p.2 (the SX 156 column, the STC note) and p.1; held back |
| Rated Voc, coefficient | 21.4 V, -58.9 mV/K (-0.2752 %/K) | 19.6 V, -0.3 %/K | 21.3 V, -0.32 %/K |
| Voc band the maker prints | "within 10% of measured values" (guide): 0.9091 to 1.1111 x rated | -5 % / +10 % on the Voc row | **none** (only "Positive power tolerance (0%, +5%)", on Pmax) |
| Voc at -20 C, typical row | 24.050 V | 22.246 V | 24.367 V |
| **Voc at -20 C at the band's top (out 3)** | **26.723 V** (26.428 V on the absolute coefficient; 26.190 V on the records' reading, rated x 1.10) | **24.471 V** (24.641 V at 1250 W/m2) | not bounded: the sheet gives no maximum |
| Bounded at or under 25 V by the printed band | **NO** (-1.723 V) | **yes** (+0.529 V) | **NO** (needs a band top of at most +2.60 %) |
| Vmp at STC; over SC-37's day (out 4) | 17.10 V; 15.69 to 16.70 V | 16.70 V; 15.16 to 16.00 V | 17.60 V; 16.26 to 17.16 V |
| Hold inside the curve at noon at the conditioned upper corner 18.813 V, over the band | **NO** (band bottom: Voc at noon 18.228 V) | **NO** (rated: 18.420 V; band bottom 17.499 V, under the nominal hold too) | yes (rated: 19.942 V; no band to test) |
| Energy into the stage, nominal hold 17.593 V, drafted limit 3.4713 A (Wh a day) | 350.0 (band bottom 137.9, top 414.2) | 245.0 (band bottom 4.7, top 410.7) | 528.3 (156 Wp; the limit binds 5 h) |
| At the conditioned upper corner 18.813 V | 240.0 (band bottom 0.0) | 0.0 | 398.3 |
| A2 unserved at 48 h, nominal trace (06 / 18 UTC, out 8) | 986.9 / 1196.1 Wh | 1348.5 / 1255.3 Wh | 678.6 / 734.1 Wh |
| Power into the stage at 1000 W/m2, cells at -20 C, the band's worst (out 5) | 108.7 W as drawn, 86.2 W with the limit | 111.5 W as drawn, 81.4 W with the limit | 161.5 W as drawn, 81.4 W with the limit |
| Hot Isc (+70 C, band top); x 1.25 | 7.12 A; 8.90 A (inside 10 A) | 7.28 A; 9.10 A (inside 10 A) | 9.61 A; 12.01 A (over 10 A) |
| Portable class (out 6) | semi-flexible laminate, 1153 x 556 x 20 mm, 2.00 kg, -40 to +85 C | folding, 1059 x 775 x 20 mm open, about 236 x 381 x 65 mm folded, 2.00 kg, **-20 to +60 C** | flexible laminate, 1364 x 683 x 2 mm, 2.24 kg, -40 to +85 C |
| **Qualifies (out 10)** | no | no | no |

The decision is the same on EA3's typical hold band (upper corner 18.221 V): no candidate qualifies (out 10).

**The exact gap (out 7).** No maker's document read prints an open-circuit band narrow enough for this window. A panel is
bounded only while its band top is at most k_bound (25 V over its rated Voc at -20 C) and held only while its band bottom
is at least k_reach (the conditioned upper corner, 18.813 V, over its rated Voc at noon on SC-37's day). Both hold for some
rating only while the band's spread (top over bottom) is at most W = k_bound / k_reach: **1.0875 to 1.1079** for these three
curve shapes, a symmetric band of about +-4.2 to +-5.1 %. SunPower's printed spread is 1.2222 and BougeRV's 1.1579: no
rating of either shape with its band fits both limits. BougeRV's rated row is itself under its reach floor (k_reach 1.0213):
its rating, not only its band, is too low for the hold. The two panels whose rated rows match the hold need a maker's band
of **+3.95 / -6.17 %** (SunPower) and **+2.60 / -5.66 %** (Solbian).

**The next bounded action.**
1. The makers' written open-circuit band for the two hold-matched panels: `clarification/sunpower-spr-e-flex-100.txt` and
   `clarification/solbian-sx-156.txt` (drafts; the owner sends them, the session contacts no outside party). They ask for
   a warranted Voc limit at STC, the coefficient's limits, the current revision, and a per-unit flash-test report.
2. Failing a written band, O-1's own alternative closure, a **controlled unit** at Layer 6: the unit bought (the owner's
   money) is accepted only when its Voc, measured at a known cell temperature and irradiance and corrected to STC with its
   expanded uncertainty U (the coefficient's own uncertainty inside U), lies in **20.079 V + U to 22.245 V - U**
   (SPR-E-Flex-100) or **20.094 V + U to 21.853 V - U** (SX 156). The floor is the hold's necessary condition; the unit's
   own trace, rerun, decides its energy.

Neither action changes REQ-016, the stage or the topology.

**The downstream item, PANEL-ACC (Layer 6, component selection; the purchase is the owner's).** Accept the bought panel
when the maker's document of the bought revision, filed with its sha256, bounds Voc at -20 C at or under 25 V by out 3's
rule and its band keeps the hold inside the curve by out 4's rule, or, failing a printed band, when the unit itself passes
the window above; then rerun its trace through the replay's section 12 and L4-E7's section 5 (A1 and A2), and re-read the
entry's 10 A for its hot short circuit (the SX 156's 9.61 A, 12.01 A by SunPower's 1.25 clause, would re-open it).

## Each candidate's bound, with its source

**SunPower SPR-E-Flex-100** (out 2, 3). Datasheet 523809 Rev D (a distributor's issue, January 2023; held back) p.1, under
"Typical Electrical Data at STC: 25°C, 1000 W/m² and AM 1.5": Pnom 100 W, power tolerance +6/-3 %, Vmpp 17.1 V, Impp 5.9 A,
Voc 21.4 V, Isc 6.3 A, voltage coefficient -58.9 mV/C, current +2.6 mA/C, power -0.35 %/C, 32 cells, 2 kg. Guide 524958
Rev F (held back), Table 1's note on PDF p.3: "Rated electrical characteristics are within 10% of measured values at
Standard Test Conditions of: 1000W/m2, 25°C cell temperature and solar spectral irradiation of AM 1.5 spectrum." Read in
its own words (|rated - measured| at most 10 % of measured), a unit's Voc lies between 21.4 / 1.1 = 19.455 V and
21.4 / 0.9 = 23.778 V. At -20 C: 26.723 V with the coefficient relative to the unit's Voc, 26.428 V with the printed mV/K,
26.190 V on the reading the records took (rated x 1.10, L4-ENERGY O-1). Every reading is over 25 V: **the maker's own
document puts the maximum above the window**; the typical row (24.050 V) is inside it by 0.950 V, but the maker does not
exclude a unit over 25 V.

**BougeRV SP001** (out 2, 3). The product page's "Product Specifications" table (fetched 2026-10-02T04:28Z, HTML sha256
ffc8cf99...; transcribed and filed): "Open Circuit Voltage Voc (V): 19.6V(-5%,+10%)", "Temperature Coefficient Voc:
-0.3%/℃", "Max. Power Voltage Vmp (V): 16.7V(-5%,+10%)", "Operating Temperature Limits: -4℉ ~ +140℉". At -20 C:
19.6 x 1.10 x (1 + 45 x 0.003) = **24.471 V**, bounded with 0.529 V to spare (24.206 V with the coefficient's change on
the rated Voc; 24.641 V at 1250 W/m2). It does not qualify: its curve sits under the hold. The page states no test
conditions (taken as STC, an ASSUMPTION) and no NOCT; its Vmp x Imp is 103.0 W against its 100 W; its fuse row prints no
number; its operating limit of +60 C sits under the cells' 73.8 C in full sun at the envelope's +40 C (INFERRED); its
output is a DC barrel port and USB ports (its manual, read, not filed).

**Solbian SX 156** (out 2, 3). SX series datasheet p.2 (February 2023; held back), the SX 156 column: 156 W, Vmp 17.6 V,
Imp 8.9 A, Voc 21.3 V, Isc 9.4 A, NOCT 45 +- 2 C, Voc -0.32 %/C, 32 cells, 2.24 kg; the STC note "Measurements carried out
according to the Standard IEC 61215 requirements"; p.1 "Positive power tolerance (0%, +5%)". No Voc tolerance anywhere on
the sheet: **not bounded**. Its typical row gives 24.367 V at -20 C, 0.633 V under, so a band top of +2.60 % at most would
do. Its Vmp at STC equals the hold's nominal, the best hold match read; its 156 W leans on the drafted input limit every
bright hour (5 h on SC-37's day).

## The hold and the energy (out 4, 5, 8)

The hold is L4-E7's selected one (drafted, not applied): 17.593 V nominal, 16.970 / 18.221 V with EA3 at its typical gain,
**16.420 / 18.813 V the widest conditioned band** (EA3 at half, the resistors' drifts), and the input limit 3.4713 A (its
lowest 3.1404 A). The energy is the replay's: PVGIS's figure for the panel's Wp on SC-37's mean September day times the
single-diode model's operating point over its own maximum-power point (the method check reproduces the replay's 373.5 /
350.0 / 280.6 Wh and L4-E7's 369.7 / 350.0 / 307.9 / 375.0 / 240.0 Wh, and A1 and A2 at L4-E7's nominal row, out 0). On
the design day the nominal hold (17.593 V) sits above every candidate's maximum-power voltage (15.2 to 17.2 V over the day
at the rated rows), so the energy falls as the hold moves to its upper corner. The 100 W screening stimulus gives 982.6 Wh a day; the SunPower nominal
trace gives 350.0 Wh and the SX 156's 528.3 Wh (A2 then 678.6 / 734.1 Wh short at 48 h, against 986.9 / 1196.1 Wh). Every
candidate takes over 100 W at the cold, bright corner as drawn; the window's 100 W rests on L4-E7's drafted limit
(96.25 W to 25 V, CONDITIONAL on five unprinted values), for every panel alike.

## The screen (out 9)

Fourteen makers' documents were read on 2 October 2026 and not taken (`inputs/screen-2026-10-02.json`, each with its address
and sha256; none filed): Solbian's SP, SR and SX issues of 2017 to 2023 and its 2011 manual (no Voc tolerance; the SP 32 is
over 25 V on its typical row), Sunman's eArche 2019 sheet and its 2023 RV and marine guide (no coefficient or tolerance on
the 32-cell model; the 12 V models near 25 V at STC), Merlin Solar's Panther (a 24 V class; "within +/- 10%"), Rich Solar,
wattstunde and Offgridtec (24 V classes), SLD Tech's drawing (no coefficient, no tolerance) and Victron's 12 V rows (over
25 V on their typical rows). The makers who print an open-circuit band at all print 5 to 10 %.

## Decisions taken (SESSION, under the owner's standing rule of 26 September 2026)

```
decision: L4E13-01, the temperature and irradiance of the bound
authority: SESSION
authority_why: a reading of the records' settled temperature, no owner judgement standing (REQ-024 and D-02a give -20 C)
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: cells at the -20 C ambient under STC irradiance; 1250 W/m2 a sensitivity, not the bound
reversed_by: a ruling that REQ-016 is read at the panel's own lower limit, or with an irradiance enhancement
```

```
decision: L4E13-02, SunPower's 10 % sentence and the coefficient
authority: SESSION
authority_why: the maker's words and the larger of two readings; no measurement or owner choice moves it
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: |rated - measured| at most 10 % of measured (19.455 to 23.778 V); the coefficient relative to the unit's Voc and,
  where printed in mV/K, also absolute; the bound is the largest reading; the records' rated x 1.10 printed beside it
reversed_by: the maker's written limit (clarification/sunpower-spr-e-flex-100.txt)
```

```
decision: L4E13-03, the hold the panel is judged against and the predicate
authority: SESSION
authority_why: L4-E7's selected settings give the band; the widest conditioned band is the conservative reading
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: compatible with the hold when the panel's open circuit at noon on SC-37's day exceeds the conditioned upper corner
  18.813 V at every point of its printed band (a necessary condition; the energy is printed beside it); the decision is
  checked on EA3's typical band too (unchanged)
reversed_by: measured EA3 gain and resistor drifts (bench 7b.12) that narrow the band
```

```
decision: L4E13-04, the two further candidates
authority: SESSION
authority_why: at most two by the brief; chosen by what they test
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: BougeRV SP001 (the only maker's document found whose printed Voc band bounds it under 25 V at -20 C) and
  Solbian SX 156 (the maker's full sheet with the best hold match, Vmp 17.6 V, and no Voc band)
reversed_by: a maker's document printing a Voc band of at most about +-4 % on a panel rated near 21 V
```

```
decision: L4E13-05, U-03
authority: SESSION
authority_why: by the brief's rule; REQ-016 need not change, money and outside contact stay the owner's
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: U-03 stays an unresolved choice (no candidate is bounded by its maker's band and held); next, the makers' written
  bands (drafts filed) and, failing those, the controlled-unit acceptance at Layer 6 (PANEL-ACC)
reversed_by: a maker's written band that passes out 3 and out 4 (U-03 then becomes PANEL-ACC's purchase)
```

```
decision: L4E13-06, the third-party documents
authority: SESSION
authority_why: the owner's rule of 27 September 2026 and the brief's (held back unless redistribution is clearly allowed)
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (task L4-E13)
ruled_on: 2026-10-02
choice: Solbian's SX sheet held back (no terms stated), fetched by fetch_held_back.py into the ignored
  v2/vendor/solar/held/ and pinned; BougeRV's page filed as a transcription of its specification table (the page and its
  manual not filed); the fourteen screen documents cited by address and sha256 only; v2/vendor/sources.txt carries the two lines
reversed_by: a maker's grant to redistribute
```

## What stays open

The makers' written Voc bands (the drafts), or a controlled unit; the coefficient limits (no maker prints one); the hold's
band (L4-E7's EA3 gain and drifts, bench 7b.12); the input limit's 100 W (L4-E7, CONDITIONAL); the trace of the panel
actually bought (one mean September day, an INFERRED 47 C NOCT for SunPower and BougeRV); the entry's 10 A if a 9.4 A class
panel is bought.

## Reproduce

`python3 v2/docs/records/l4e13/l4e13_panel.py > v2/docs/records/l4e13/l4e13_panel.out` from the repository root (about a
minute and a half; needs the held documents: `v2/docs/records/a1solar/fetch_held_back.py` and
`v2/docs/records/l4e13/fetch_held_back.py`). Tests: `env -C v2/ecad/tools/tests python3 run.py test_l4e13`.
