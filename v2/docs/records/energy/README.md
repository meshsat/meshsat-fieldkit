# energy: mission M1's energy reconciliation (MESHSAT-1357)

Stream `energy`, branch `fnd/energy` from the integration set's tip `038037ed`, 28 September 2026. The owner's
instruction of that day: preserve M1 and REQ-072 as written, reconcile the energy budget against verified loads,
usable battery energy, night duration and solar contribution, present every change explicitly, keep unmet
criteria visible. **Prototype design: nothing built, ordered or measured; an AI review.**

| file | what it is |
|---|---|
| `ENERGY-RECONCILIATION.md` | the record, sections 1 to 7: the loads with their kinds, the usable energy, the night, the solar input, the balance and the conflict, the options ranked, the smallest justified changes (every set holds its state for all 72 hours; 7c the sun-following schedule with its reduced hours a day per month and set, added 29 September 2026); section 8 the one 4S6P pack |
| `DECISION-PARAGRAPH.md` | the owner's sheet, under 120 words |
| `energy_inputs.yaml` | every input with its document, page and kind; the loads of PS-IDLE-SPEC as the tree's model prints them; the state rules; the pack; the solar resource and chain; the pockets |
| `energy_budget.py` | the tool: pins the inputs by sha256 (refuses a changed one by name), recounts the states, discharges the pack, computes the night, the solar day, the hour-by-hour balance, the sensitivity and the options; deterministic output |
| `energy_budget.out` | its output, byte for byte what the record quotes |
| `night_bounds.py`, `night_bounds.out` | the night state's LOW / PLAN / HIGH (11.02 / 16.20 / 39.67 W) on the tree's model: imports `records/rv-pwr/pwr_budget.py` unchanged (pinned) and reproduces PS-SURV-R's 12.78 / 23.27 / 46.94 W as its check (second issue, review items m1 and m2) |
| `packfit_west.py`, `packfit_west.out` | a second block in the west pocket judged with A06's `pack_fit.py` imported unchanged (pinned): the block alone fits, its board P fits nowhere beside, on top or in the east pocket (second issue, review item B1) |
| `energy_4s6p.py`, `energy_4s6p.out` | section 8: the second block in the west pocket in parallel with the first under the one board P (one 4S6P pack): the gauge's words, balancing, currents, the one charge current, the strings' sharing, S-85, the harness, the drop-zone conflict, the energy runs (M1 as written, the night state, two day schedules) and the consequences; imports `energy_budget.py` and A06's `pack_fit.py` unchanged (pinned), reproduces `energy_budget.simulate` on four cases before printing |
| `DECISION-OPTIONS.md` | the owner's options sheet (29 September 2026): A the full mission (the architecture of section 9), B today's limits, C reduced service as a separate conditional alternative; REQ-072 FAIL in each until a design is built and tested |
| `energy_architecture.py`, `energy_architecture.out` | section 9: M1 from the requirement side. Imports `energy_budget.py` unchanged, checks its pinned inputs, and sweeps storage (4S x 3 to 80 strings), panel (100 to 1500 Wp), window (100 W to none) and load; prints the storage floor, the smallest pack per window, the consumption each storage allows, the margins at +15 and +20 C and the 2.80 V line |
| `apply_records_readme_row.py` | DRAFT for the integrator: adds this folder's row to `v2/docs/records/README.md`; not executed |
| `apply_req072_evidence_note.py` | DRAFT for the integrator: adds one evidence line to REQ-072 in `pcb_requirements.yaml`, verdict and statement untouched; not executed |

Run: `python3 v2/docs/records/energy/energy_budget.py > v2/docs/records/energy/energy_budget.out` from the
repository root (about 0.3 s; PyYAML). Checks made on 28 September 2026: two runs byte-identical; a changed
`energy_inputs.yaml` refused with exit 2 naming it; a changed pinned file refused with exit 3 naming it; no em or
en dash in the folder.

**Second issue (28 September 2026)**, after an independent AI review of `fc8cf808`: blocking items B1 (west
pocket), B2 (the solar stage's 100 W is not held by the stage; routes A and B) and B3 (the decision paragraph), and
minor items m1 to m11, answered in `ENERGY-RECONCILIATION.md` (its header lists where). **Third issue (28 September 2026)**, after the re-check of `7697c172`: R1 (four universal sentences scoped, section
7b of the record and of `energy_budget.out`) and R2 (Route B's sense resistor 10 mOhm, its worst case at TRK_OUT's
15.56 V and the stage's 0.90). Run order: `night_bounds.py`
and `packfit_west.py` first (their outputs are pinned inputs of `energy_budget.py`), then `energy_budget.py`.

**Section 8 (29 September 2026)**, the integrator's follow-up: one 4S6P pack under one board P. Run
`python3 v2/docs/records/energy/energy_4s6p.py > v2/docs/records/energy/energy_4s6p.out` (about 0.6 s). Checks: two runs
byte-identical; a run on a copied root identical; a changed `gen_sch_p.py` refused with exit 3 naming it; a changed
file of `energy_inputs.yaml`'s pinned list refused with exit 3 naming it.

Reused, cited, not duplicated: stream d4energy's `energy_data.yaml` (branch `fnd/d4energy`, commit `9b43e274`)
for the load citations and the pack's curve readings, and the PVGIS mean-day profile it filed at `71be4943`.

**Fourth issue (29 September 2026)**, on the owner's ruling that reduced capability does not replace M1 or REQ-072:
section 9 of the record and `energy_architecture.py` (second issue the same day, after an independent AI review filed in
`checks/check-section9.md` with the checker's own recomputation `checks/recompute.py` and `.out`: REQ-016 restated as a
trade against the array, the transport sentence withdrawn, the model pinned by sha256). It refuses with exit 2 when
`energy_inputs.yaml` is not the pinned file and exit 3 when `energy_budget.py` or a pinned input changed. Run it after
`energy_budget.py`:
`python3 v2/docs/records/energy/energy_architecture.py > v2/docs/records/energy/energy_architecture.out` (about 1 s).

## Reproducing every figure

Environment: Python 3.11 with PyYAML (nothing else; no network). From the repository root, in this order:

```
python3 v2/docs/records/energy/night_bounds.py   > v2/docs/records/energy/night_bounds.out
python3 v2/docs/records/energy/packfit_west.py   > v2/docs/records/energy/packfit_west.out
python3 v2/docs/records/energy/energy_budget.py  > v2/docs/records/energy/energy_budget.out
python3 v2/docs/records/energy/energy_4s6p.py    > v2/docs/records/energy/energy_4s6p.out
python3 v2/docs/records/energy/energy_architecture.py > v2/docs/records/energy/energy_architecture.out
git diff --exit-code v2/docs/records/energy/     # every output byte-identical to the committed one
```

`energy_budget.py` refuses to run when `energy_inputs.yaml` or any file its `pinned:` list names is missing or has
changed (exit 2 or 3, naming the file); the list is the PVGIS monthly file, the two Samsung INR18650-35E documents,
the tree's power model outputs, board E's generator and this folder's two helper outputs. `night_bounds.py` and
`packfit_west.py` import `records/rv-pwr/pwr_budget.py` and A06's `pack_fit.py` unchanged and pin them. Every result is a
model result on the September reference day (PVGIS's monthly-average hourly profile), not a field-weather reliability
claim.
