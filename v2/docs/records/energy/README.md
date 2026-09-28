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
| `DECISION-OPTIONS.md` | the owner's options sheet for section 8, at most 250 words, three options, REQ-072 FAIL in each |
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
