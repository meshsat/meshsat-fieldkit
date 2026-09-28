# energy: mission M1's energy reconciliation (MESHSAT-1357)

Stream `energy`, branch `fnd/energy` from the integration set's tip `038037ed`, 28 September 2026. The owner's
instruction of that day: preserve M1 and REQ-072 as written, reconcile the energy budget against verified loads,
usable battery energy, night duration and solar contribution, present every change explicitly, keep unmet
criteria visible. **Prototype design: nothing built, ordered or measured; an AI review.**

| file | what it is |
|---|---|
| `ENERGY-RECONCILIATION.md` | the record, sections 1 to 7: the loads with their kinds, the usable energy, the night, the solar input, the balance and the conflict, the options ranked, the smallest justified changes |
| `DECISION-PARAGRAPH.md` | the owner's sheet, under 120 words |
| `energy_inputs.yaml` | every input with its document, page and kind; the loads of PS-IDLE-SPEC as the tree's model prints them; the state rules; the pack; the solar resource and chain; the pockets |
| `energy_budget.py` | the tool: pins the inputs by sha256 (refuses a changed one by name), recounts the states, discharges the pack, computes the night, the solar day, the hour-by-hour balance, the sensitivity and the options; deterministic output |
| `energy_budget.out` | its output, byte for byte what the record quotes |
| `apply_records_readme_row.py` | DRAFT for the integrator: adds this folder's row to `v2/docs/records/README.md`; not executed |
| `apply_req072_evidence_note.py` | DRAFT for the integrator: adds one evidence line to REQ-072 in `pcb_requirements.yaml`, verdict and statement untouched; not executed |

Run: `python3 v2/docs/records/energy/energy_budget.py > v2/docs/records/energy/energy_budget.out` from the
repository root (about 0.3 s; PyYAML). Checks made on 28 September 2026: two runs byte-identical; a changed
`energy_inputs.yaml` refused with exit 2 naming it; a changed pinned file refused with exit 3 naming it; no em or
en dash in the folder.

Reused, cited, not duplicated: stream d4energy's `energy_data.yaml` (branch `fnd/d4energy`, commit `9b43e274`)
for the load citations and the pack's curve readings, and the PVGIS mean-day profile it filed at `71be4943`.
