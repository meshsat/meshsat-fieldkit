# SELECTION: the panel for Option A(i) (stream a1solar, MESHSAT-1357, 29 September 2026)

Second issue, after the independent AI check of `9f93a9fc` (`checks/check-1.md`): the decision's gate on
REQ-016 (check minor 4), REQ-016's temperature reading (minor 5), the deployment rule from the plane grid (B1), the
SunPower documents held back by their terms (minor 8) and "on this model" where a result is stated (minor 10).

Prototype design: nothing is bought, built or measured. AI review, not a qualified review. Every figure is the maker's
own, quoted from the file named, or is printed by `array_calc.py` (`array_calc.out`, section named). The owner's
instruction of 29 September 2026: about 400 Wp into a 200 W solar stage, and real panel specifications selected before
the array's wiring and the stage's input ratings are fixed. M1, REQ-072 and REQ-016 are not changed here.

## 1. What the selection has to answer

A panel for a carried kit (folding, semi-rigid or blanket preferred; a rigid 12 V class set as the reference) whose maker
publishes the figures the entry is rated from: Pmax, Voc, Isc, VMPP, IMPP, the temperature coefficients, the operating
range, size, mass, ingress rating and connector. Where a maker publishes no coefficient, it is bounded at the worst value
among the monocrystalline documents held (Voc -0.35 %/K and Pmax -0.45 %/K from Victron, Isc +0.05 %/K from Renogy),
which is a bound within this set, not the technology's worst anywhere; `array_calc.out` marks each such figure BOUND.

## 2. The candidates, the makers' figures

All at STC (1000 W/m2, 25 C cells, AM 1.5). Documents under `v2/vendor/solar/`, each with its line in
`v2/vendor/sources.txt` and its publication decision there. **SunPower's three documents are held back from the public
tree by their terms** (two installation guides reading "All rights reserved", a distributor's re-branded datasheet with
no terms): they are cited by URL and sha256 in `sources.txt` under `solar/held/`, an ignored folder that
`fetch_held_back.py` (beside this page) fills and checks; the figures quoted below from them are as read on 29 September.

| | Victron BlueSolar Mono 150W-12V (reference) | Renogy RNG-100DB-H | SunPower SPR-E-Flex-100 | PowerFilm F16-7200 | PowerFilm 120W (30V) | BLUETTI PV420 |
|---|---|---|---|---|---|---|
| kind | rigid, glass and aluminium frame | semi-rigid flexible laminate | semi-rigid flexible laminate | folding blanket, amorphous Si | folding blanket, amorphous Si | one-piece folding |
| document | `victron-bluesolar-monocrystalline-panels-datasheet-en.pdf` p.1 | `renogy-rng-100db-h-flexible-100w-datasheet-2018.pdf` p.2 | held back: `held/sunpower-spr-e-flex-100-datasheet-523809-revd.pdf`; `held/sunpower-flex-safety-installation-524958-revf.pdf` Table 1, 3.0, 5.1, 5.2 | `powerfilm-f16-7200-120w-foldable-15v-spec.pdf` p.2 | `powerfilm-120w-foldable-30v-spec.pdf` p.2 | `bluetti-pv420-product-page-2026-09-29.md` (the maker's page, transcribed) |
| Pmax | 150 W (+-3 %) | 100 W | 100 W (+6/-3 %) | 120 W | 120 W | 420 W |
| VMPP / IMPP | 18.2 V / 8.25 A | 18.9 V / 5.29 A | 17.1 V / 5.9 A | 15.4 V / 7.2 A | 30.8 V / 3.6 A | not published |
| Voc / Isc | 22.3 V / 8.69 A | 22.5 V / 5.75 A | 21.4 V / 6.3 A | 21.9 V / 9.1 A | 43.7 V / 4.6 A | 44.3 V / 12.2 A |
| Voc coefficient | -0.35 %/K | -0.31 %/K | -58.9 mV/K (-0.275 %/K) | -0.300 %/K | -0.300 %/K | not published (BOUND -0.35) |
| Isc coefficient | +0.04 %/K | +0.05 %/K | +2.6 mA/K (+0.041 %/K) | +0.109 %/K | +0.109 %/K | not published (BOUND +0.05) |
| Pmax coefficient | -0.45 %/K | -0.42 %/K | -0.35 %/K | -0.200 %/K | -0.200 %/K | not published (BOUND -0.45) |
| NOCT | not published | 45 +- 2 C | not published | not published | not published | not published |
| operating range | -40 to +85 C | -40 to +85 C | -40 to +85 C (guide 5.1) | not published | not published | **-10 to +65 C** |
| size, mass | 1485 x 668 x 30 mm, 11 kg | 1219 x 549 x 2 mm, 1.9 kg | 1153 x 556 x 20 mm, 2.0 kg | 2197 x 1397 mm open, 368 x 356 x 76 folded, 2.9 kg | as F16-7200 | 2675 x 975 open, 975 x 660 x 45 folded, 14 kg |
| ingress | not stated ("sealed, waterproof" box) | box IP68, connectors IP67 | box IP67 (guide 5.2) | not stated; "Not designed for use in the rain" | as F16-7200 | IP65 |
| connector | MC4 (PV-ST01), 900 mm | "Solar Connectors" (30 A, 1000 V, IP67), 12 AWG | Tyco PV4-S, 4 mm2, 450 mm | Aptiv Weather Pack | Aptiv Metri-Pack | MC4 |
| max system voltage, series fuse | 1000 V, not published | 600 V, 15 A | **45 V**, 15 A; "not UL or IEC certified" (guide Table 1) | not published | not published | not published |

The maker's clause every rating below also uses (SunPower 524958 Rev F, 3.0, the only such clause in a held document):
"the values of ISC and VOC marked on the modules should be multiplied by a factor of 1.25 when determining component
voltage ratings, conductor capacities, fuse sizes and size of controls connected to the module output", with NEC 690-8's
"additional 1.25 Safety factor" named as possibly applicable (NEC itself is not held).

**Disagreements between makers' documents, kept:** PowerFilm's 30 V sheet prints part number F32-3600 where the maker's
product page names F16-3600 (the electrical figures are the sheet's). SunPower's installation guide Rev A (copyright
2016, held back and cited by URL and sha256 as `held/sunpower-flex-safety-installation-524958-reva.pdf`) gives the E-Flex-100 as VMPP 17.5 V, IMPP 5.8 A, Voc
21 V, Isc 6.2 A and 45 V maximum system voltage; Rev F and datasheet Rev D (both held back) agree on 17.1 V, 5.9 A, 21.4 V and
6.3 A. Both are kept; the worse for every rating (Voc 21.4 V, Isc 6.3 A) is what `array_calc.py` uses, and the 45 V
stands in both issues that print a figure (Rev F leaves the cell to its certification note). Every issue of the guide adds that
the rated characteristics "are within 10% of measured values". Renogy's product
page (rendered by script; no document reached this host) now says "22% Efficiency" where the held 2018 sheet says 21 %
cell efficiency, so the current production may differ from the sheet: see 4 and README's bench and procurement items.
The EcoFlow 400W's figures conflict between pages (the coordinator's record: Voc 39.3 against 48 V, Isc 12.2 against
11 A) and no maker's document is held; it stays not selectable.

## 3. What each candidate can do for about 400 Wp (`array_calc.out` sections 2, 5, 6; ARRAY.md for the chosen one)

| candidate | wiring, Wp | array | V rating (cold Voc; 1.25 clause) | I rating (1.25 x 1.25 x hot Isc) | mass, area | the finding |
|---|---|---|---|---|---|---|
| Victron 150W-12V | 1S3P, 450 | three rigid panels | 25.8; 27.9 V | 41.5 A | 33 kg, 3.0 m2 | the reference; no series fuse rating published; 3S (77 V cold, 84 V by the clause) exceeds the LT8705A's 80 V |
| Renogy RNG-100DB-H | **2S2P, 400** | four semi-rigid panels | **51.3; 56.3 V** | **18.4 A (20 A fuse)** | **7.6 kg, 2.7 m2** | inside 60 V; one string cannot be back-fed past its 15 A fuse rating (7.35 A); fixed-voltage ratio 0.990 on this model (0.987 to 0.992 across the fits) |
| Renogy RNG-100DB-H | 1S4P, 400 | four in parallel | 25.6; 28.1 V | 36.8 A | 7.6 kg, 2.7 m2 | back-feed into one panel 22.1 A, over its 15 A series fuse rating: a fuse per panel; 12.9 A into the stage at 200 W |
| Renogy RNG-100DB-H | 4S1P, 400 | one string | 102.6; 112.5 V | 9.2 A | | over the LT8705A's 80 V: excluded |
| SunPower SPR-E-Flex-100 | 1S4P, 400 | four in parallel | 24.1; 26.8 V | 40.1 A | 8.0 kg, 2.6 m2 | with the PowerFilm 15 V model (24.9 V), the only candidates whose cold Voc stays under REQ-016's 25 V at -20 C cells (at the panels' own -40 C limit neither does: 25.23 and 26.17 V, `array_calc.out` 13); back-feed 24.1 A over its 15 A; the maker warns against parallel wiring "without proper system and safety protection" (guide 4.0) |
| SunPower SPR-E-Flex-100 | 2S2P, 400 | two strings | 48.1; 53.5 V | 20.1 A | | **over the maker's own 45 V maximum system voltage**: excluded by its maker |
| PowerFilm F16-7200 / 30 V | 1S4P, 480 | four blankets | 24.9; 27.4 V (15 V model) or 49.6; 54.6 V (30 V model) | 59.7 A or 30.2 A | 11.6 kg, 12.3 m2 | amorphous: 39 W/m2, so about 400 Wp covers 10 to 12 m2; no operating range; not for rain; its fixed-voltage figure is not computed (the no-shunt model cannot represent its fill factor, `array_calc.out` section 3) |
| BLUETTI PV420 | 1, 420 | one folding panel | 51.3; 55.4 V (BOUND) | 19.5 A (BOUND) | 14 kg, 2.6 m2 | no VMPP, IMPP or coefficient published; its -10 C to +65 C range excludes the envelope's -20 C and the +70 C cells: not selectable |

## 4. The design basis: four Renogy RNG-100DB-H, two in series, two strings in parallel

```
decision: A1SOLAR-01, the panel and wiring of Option A(i)'s array
authority: SESSION
authority_why: an engineering selection among makers' documents inside the owner's instruction (about 400 Wp into a
  200 W stage, real specifications first); it spends nothing, buys nothing and changes no requirement (REQ-016's
  restatement is listed for the owner in ARRAY.md 5, not made)
ruled_by: SESSION under the owner's standing rule of 26 September 2026 (stream a1solar)
ruled_on: 2026-09-29
choice: Renogy RNG-100DB-H x 4 (400 Wp STC), 2S2P, into board E's LT8705A stage with its input held at 34.3 V
  (R8 232k over R9 8.45k, ARRAY.md 3)
reversed_by: a current Renogy sheet whose figures move a rating in ARRAY.md (re-run array_calc.py with the worse of the
  two sheets), a maker's refusal of series wiring, or an owner ruling that keeps the array's voltage near REQ-016's 25 V
  (then SunPower SPR-E-Flex-100 x 4 in 1S4P, with a fuse per panel and a 40 A entry, ARRAY.md 4)
gate: the 2S2P basis STANDS ONLY ONCE THE OWNER RESTATES REQ-016 (ARRAY.md 5); until then it is the recommendation, the
  1S4P SunPower array remains a standing option, board E's drafts (ARRAY.md 6) are not applied, and the decision is not
  entered in tools/pcb_decisions.yaml (the integrator enters it with the owner's REQ-016 ruling)
```

**Why this one.** (1) Its maker publishes every figure the entry is rated from, including the only NOCT in the set, the
operating range that covers the envelope's -20 C cells and +70 C, the box and connector ingress (IP68, IP67) and a
series fuse rating; (2) its 600 V system voltage allows the series pair, which the SunPower's 45 V does not; (3) 2S2P
halves the current of all-parallel wiring (a 20 A entry against 40 A; 18.4 against 36.8 A before the fuse's
standard step), needs no fuse per string (7.35 A of
back-feed under the 15 A rating) and keeps the array inside 60 V even by the 1.25 clause (56.3 V); (4) it is the
lightest per watt of the fully specified panels (52.6 Wp/kg, 7.6 kg for 400 Wp; the rigid reference is 33 kg); (5) the
stage holding a fixed 34.3 V keeps 0.990 of what a maximum-power tracker would take on the September day on this model
(0.987 to 0.992 across the three fits, `array_calc.out` 12), so the stage needs no tracking loop on this model
(`energy_runs.out` 1).

**What it costs, stated.** It is a semi-rigid panel, not a folding one: four panels of 1219 x 549 mm travel flat beside
the case, and on this model the two-pack design case meets in both its typical and adverse cases only with the panels
propped at 20 to 50 degrees facing within 15 degrees of south (ARRAY.md 7, from each plane's own PVGIS day; laid flat it
is NOT MET in either case, `energy_runs.out` 6), so a folding stand is part of the array. Its held sheet is 2018's, from a retailer's copy; the maker's current page could not be read by this host, and
its efficiency line differs. The series pair raises board E's panel entry from 25 to 35 V class parts to 60 to 100 V
class parts (ARRAY.md 6) and takes REQ-016's voltage to about 52 V (ARRAY.md 5), which is the owner's to rule.

**Not chosen, and why.** BLUETTI PV420 (the one-piece fold that would deploy fastest): no VMPP, IMPP or coefficient, and
a range that stops at -10 C. PowerFilm (the military-tested blanket): amorphous at 39 W/m2, so 10 to 12 m2 for the
array, no operating range and not for rain; kept as the option if a blanket is required whatever the area. SunPower:
cannot be wired in series by its maker's rating and was "presently not UL or IEC certified" by its maker's 2019
guide; kept as the reversal
for an all-parallel array. Victron: rigid, 33 kg for three panels; the reference only.
