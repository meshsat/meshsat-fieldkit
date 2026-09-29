# a1solar: Option A(i)'s solar panel, the array's wiring and the entry it sets (MESHSAT-1357)

Stream a1solar, branch `fnd/a1solar`, 29 September 2026; **second issue** after the independent AI check of `9f93a9fc`
(`checks/check-1.md`, mergeable no: B1 the deployment rule, B2 the adverse ratio, minors 1 to 10, each
answered below and in LOG.md). The coordinator's state record of 02:45 was replaced by this page; its Victron and EcoFlow
readings are carried into SELECTION.md. **Prototype design: nothing is bought, built or measured. AI review, not a
qualified review.** The owner's instruction of that day: Option A(i), about 400 Wp into a 200 W solar stage, with real
panel specifications selected before the array's wiring and the stage's input ratings are fixed; M1 and REQ-072
unchanged; no purchase and no requirement change authorised.

| file | what it is |
|---|---|
| `SELECTION.md` | six candidates from their makers' documents (Victron 150W-12V rigid reference, Renogy RNG-100DB-H, SunPower SPR-E-Flex-100, PowerFilm 120 W foldable at 15 V and 30 V, BLUETTI PV420; EcoFlow 400W carried as not selectable), the bounds where a maker publishes nothing, and the design basis as SESSION decision A1SOLAR-01 with its gate on REQ-016 |
| `ARRAY.md` | the three wirings of four panels; the recommended 2S2P; the set point and window; the entry's fuse and connector ratings; what REQ-016 would have to become (the owner's); section 6, the GATED draft list for board E's writer; section 7, the energy model's inputs and the planes the array may face |
| `array_calc.py`, `array_calc.out` | the makers' figures, every wiring near 400 Wp, single-diode fits and their Rs bracket, the fixed-voltage ratio on the September mean day, the hotter cells' own loss, the E96 divider choice, REQ-016's -20 C and -40 C readings; pins its committed inputs by sha256 and refuses a held-back document that is present but not the pinned file |
| `energy_runs.py`, `energy_runs.out` | both energy design cases with the chosen array's ratios (typical and corrected adverse), `records/energy/energy_architecture.py` and a1elec's `energy_two_pack.py` imported unchanged and pinned, after reproducing their own published figures (exit 4 otherwise); section 6, the two-pack case on 50 planes, each on its own PVGIS mean day |
| `inputs/pvgis-leiden-daily-profile-2005-2020.json` | PVGIS DRcalc's mean-day profile of the 40 degree south plane, the file `energy_inputs.yaml` names (sha256 4d974567...), copied from `fnd/a1elec`; the anchor of the plane grid |
| `fetch_held_back.py` | fetches SunPower's three held-back documents into the ignored `v2/vendor/solar/held/` and checks their sha256 (tested into a scratch folder: all three matched) |
| `apply_records_readme_row.py` | DRAFT for the integrator: adds this folder's row to `v2/docs/records/README.md` after the `energy/` row; tested on a scratch copy; not executed in the tree |
| `LOG.md` | the running log |

Filed by this stream under `v2/vendor/solar/`, each with its `sources.txt` line and publication decision: the Renogy
RNG-100DB-H sheet (2018, a retailer's copy of the maker's sheet), PowerFilm's two 120 W foldable sheets (the maker's
site), a transcription of BLUETTI's PV420 page, and 49 PVGIS 5.2 DRcalc answers for Leiden under `pvgis-planes/`.
**Held back by their terms, cited by URL and sha256:** SunPower's E-Flex datasheet 523809 Rev D and its flexible modules'
Safety and Installation Instructions 524958 Rev F and Rev A. Declared in `v2/vendor/vendor-status.txt` (`solar current`)
and in the folder table of `v2/vendor/README.md`. Victron's sheet was filed by the integrator.

## What is shown at desk (model and arithmetic, not measurement)

- **The design basis:** four Renogy RNG-100DB-H (400 Wp) wired 2S2P (SELECTION.md 4): cold Voc 51.3 V at -20 C cells
  (54.1 V at the panel's -40 C limit; 56.3 V by SunPower's 1.25 clause, the rating basis); hot Isc 11.8 A at +70 C, 14.7 A
  with the edge-of-cloud factor, a **20 A** fuse and entry; no string fuse (7.35 A of back-feed under the 15 A series
  fuse rating); 7.6 kg and 2.7 m2 of panel.
- **The stage needs no tracker, on this model:** held at a fixed 34.29 V (drafted R8 232k over R9 8.45k; 33.05 to 35.57 V
  with FBIN's range and 1 percent resistors) it keeps 0.990 of what a maximum-power tracker would take on the September
  mean day with a 5 m lead (0.987 to 0.992 across three fits of the panel).
- **Board E as generated does not take this array** at 200 W: 25 V class parts on the panel entry, a 32 V DC blade
  fuse, a 10 A connector and wall pair, a BAT54 boost diode; and it senses no input or output current, so the 200 W
  window is the model's clip, not a limit on the board (ARRAY.md 3, 6). All-parallel wiring keeps the voltage but
  doubles every current (40 A entry) and needs a fuse per panel; four in series exceeds the LT8705A's 80 V.
- **The energy model's inputs:** STC 400 Wp unchanged; the performance ratio becomes **0.9326 typical** and **0.8573
  adverse** (corrected: the hotter cells' own loss, 0.9765, is now charged, with the resistors' tolerance and the worst
  fit). At 40 degrees facing south both design cases MEET on this model: section 9's 4S18P with 90.6 / 26.5 Wh (typical,
  +20 / +15 C) and 87.8 / 23.7 Wh (adverse); a1elec's two-pack case with **30.7 Wh** at its lowest (typical, lid 0.5 Wh)
  and **27.9 Wh** (adverse, lid 0.0 Wh, down to a lid at +10.8 C).
- **The plane decides the result, and the rule is now from each plane's own PVGIS day:** the two-pack case meets in
  both the typical and the adverse case at **20 to 50 degrees of slope facing within 15 degrees of south** (also 30 and 40
  degrees at 30 degrees west, and 60 degrees at 0 and 15 degrees west); **flat does not meet in either case**; 45 degrees
  east never meets in both (in the typical case only at 20 and 30 degrees, under 4 Wh) and 30 degrees east never meets
  the adverse case. The first issue's rule (30 to 60 degrees within 45
  degrees of south, from multiplied factors on a scaled day) is withdrawn (ARRAY.md 7).

REQ-072 stays FAIL: nothing here is drawn, built or tested.

## DRAFTS for board E's writer (ARRAY.md 6), GATED

**Not applied to `gen_sch_e.py` before the owner restates REQ-016**: they contradict its acceptance as written. Then:
R8 232k and R9 8.45k (34.29 V); Q3 and Q4 to an 80 or 100 V class; C11 and C12 to a 63 V class or higher; C13, C14, C15
and C64 to 100 V; D4 to a 58 V standoff class with the surge basis stated against the LT8705A's 80 V; D5 (BAT54, 30 V) to
a diode above 56.3 V; F2 at 20 A and 56.3 V DC or more with an interrupting rating above the kit-side fault current (a
MINI 297 is 32 V DC, 1000 A at 32 V); J_SOLAR, the wall's solar pair and the lead at 20 A or more; PV_IN and PV_P
re-declared (34.29 V, 6.05 A, 14.70 A peak, v_max 56.3 V); **the 200 W window implemented** (an input or output sense
resistor and the stage's current regulation) or every downstream part rated for what the inductor limit passes;
TRK_OUT's _TRK_A re-derived from the MAXIMUM buck valley threshold (102 mV, 20.4 A over 5 mOhm); L1 (XAL1510-103ME,
Isat 26.3 A, Irms 22 A at 40 K) not shown adequate at that threshold (about 24.6 A peak). The writer checks each against
the maker's document; this stream has not.

## The owner's (not changed here)

- **REQ-016:** for the recommended 2S2P it would read "at most 200 W into the stage; open-circuit voltage at most 51.3 V
  at -20 C cells (54.1 V at -40 C), every part on the panel entry rated above 56.3 V; the array held at 34.3 V (33.0 to
  35.6 V); F2 20 A and at least 56.3 V DC with an interrupting rating above the kit-side fault current; J_SOLAR, the wall
  pair and the lead at least 20 A". For 1S4P: 25.6 V at -20 C (27.0 V at -40 C, 28.1 V by the clause), 16.7 to 17.6 V,
  40 A and a fuse per panel. **This record reads REQ-016's "coldest operating temperature" as the envelope's -20 C
  cells.** As written (25 V) REQ-016 admits neither the chosen panel (25.64 V alone at -20 C) nor the Victron reference
  (25.81 V); at -20 C it admits the SunPower (24.05 V) and PowerFilm's 15 V model (24.86 V) in parallel, and at the
  panels' own -40 C limit none of the candidates (25.23 and 26.17 V). ARRAY.md 5; `records/energy/DECISION-OPTIONS.md`
  A names the decision. **A1SOLAR-01 stands only once REQ-016 is restated**; until then 1S4P SunPower remains a standing
  option.
- **Purchase:** none is made or prepared here. Before one, the current Renogy sheet (below).
- **The kit's claimed form:** four 1219 x 549 mm panels and their stand travel with the kit (section 9i's "about 2
  square metres" is 2.7 m2 for this panel), and the operator sets them at 20 to 50 degrees facing within 15 degrees of
  south (a CONOPS line, the owner's to accept; the grid's result on this model, its thinnest margins 3.3 Wh at 20
  degrees and 15 east in the adverse case, 8.9 Wh at 50 and 15 east, 9.5 Wh at 20 and 15 west; planes between grid
  points are not run; re-checked in `checks/check-2.md`).

## What the bench owes (and procurement before it)

1. **The current Renogy RNG-100DB-H sheet from the maker** (the held one is 2018's retailer copy; the maker's page says
   22 percent efficiency against the sheet's 21 percent cell efficiency): re-run `array_calc.py` with the worse of the
   two sheets; a moved rating moves ARRAY.md.
2. One panel's I-V curve at a known irradiance and cell temperature against the three fits (`array_calc.out` 12), and
   the 2S2P array's open-circuit voltage on a cold clear morning.
3. The stage at 34.3 V in and 15.1 V out at 200 W: its efficiency (the chain's 0.93 was declared near unity ratio), its
   input regulation holding the set point, the power it takes with no current regulation, its inductor current at the
   limit, its temperature; its current limit at the 9 V bus corner.
4. The panels' cell temperature propped in the sun against the NOCT model (the adverse case takes 10 K more), and the
   lead's drop at 6 A.
5. The stand: that it holds four panels at 20 to 50 degrees in wind (the SunPower guide warns of flapping; Renogy says
   nothing), the deployment time, and a day's harvest on planes turned east and west against the grid's model result.

## Reproducing

From the repository root (Python 3.11, PyYAML for `energy_runs.py`; no network):

```
python3 v2/docs/records/a1solar/array_calc.py  > v2/docs/records/a1solar/array_calc.out    # about 2 s
A1ELEC_ROOT=<a root holding fnd/a1elec's records/a1elec> \
python3 v2/docs/records/a1solar/energy_runs.py > v2/docs/records/a1solar/energy_runs.out   # about 9 s
```

`energy_runs.py` looks for a1elec's `energy_two_pack.py` (sha256 81694b2b..., `fnd/a1elec` at `06568798`) under
`A1ELEC_ROOT`, by default this repository's root, which holds it once `fnd/a1elec` is merged. Before that, a scratch root
of symlinks to this tree's `v2/vendor`, `v2/ecad` and `v2/docs/records/*` plus `git archive fnd/a1elec
v2/docs/records/a1elec` serves; built that way it reproduced a1elec's own `energy_two_pack.out` byte for byte. Checks
made on the second issue: each script run twice, outputs byte-identical; `array_calc.py` identical with the held-back
documents present in `held/` and absent; the 40/0 DRcalc answer fetched again byte-identical to the anchor; no host
name, path or date in either output; no em or en dash in the folder.

**For the integrator:** the three SunPower PDFs were committed in this branch's first issue (`ab7f85d2`, `c90e10f4`)
and removed in `6fa0f576`. A merge that keeps this branch's history would publish them with it; squash the branch (or
otherwise leave those two commits out of `main`) to keep them out of the public mirror.
