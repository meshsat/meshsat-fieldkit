# l9pwr: Layer 9 item 9.1, the power budget on the current design (MESHSAT-1357)

3 October 2026, the Layer 9 author, worktree `l9pwr` on branch `fnd/l9pwr` from set 28's tip `37bc2f1d`. Prototype design,
desk arithmetic: nothing has been built, powered or measured. This folder brings record rv-pwr's power model to the current
design with margins and sensitivities. It edits no generator, requirement, registry record or other record's file; rv-pwr's
committed outputs stay as they are (other records pin them). The drafts of Layers 4 and 8 it models are printed DRAFTED and
none is applied.

| File | What it is |
|---|---|
| `L9-POWER-BUDGET.md` | The page: the totals per state on three trees (rv-pwr as committed, the generators as drawn, the drawn tree with the drafts), what differs from rv-pwr and how each change is taken, the converters against their limits, the reconciliation with Layer 4, the sensitivities, the margin findings with class and owner, what other records' authors own, the decisions taken |
| `l9pwr_budget.py` | The script, run from the repository root: `python3 v2/docs/records/l9pwr/l9pwr_budget.py` (stdlib and pdftotext, about a second). It imports `v2/docs/records/rv-pwr/pwr_budget.py` unchanged, pins 26 inputs by sha256, parses every figure from its source (a record's output, a generator, a draft, a maker's datasheet), refuses when a figure is not found, reproduces rv-pwr on rv-pwr's own tree and every overlapping Layer 4 figure from that record's inputs, then prints the current design's budget |
| `l9pwr_budget.out` | Its output, committed, regenerated only through `_bin/regen_out.py` (two byte-identical runs and every pin current): 0 the pins; 1 the differences and how they are taken; 2 the model check; 3 the totals; 4 the waterfall step by step; 5 per state every load, rail and converter against its limit; 6 the pack current; 7 D-11's floors; 8 the reconciliation; 9 the sensitivities and the efficiency over 12 to 16.8 V; 10 the findings; 11 the predicates |

Test: `v2/ecad/tools/tests/test_l9pwr.py`, run isolated with `env -C v2/ecad/tools/tests python3 run.py test_l9pwr test_public_hygiene`.

## Proposed LAYER-STATUS rows (for the integrator; LAYER-STATUS.md is not edited here)

| Item | Acceptance item (short) | Proposed state | Evidence, or what remains |
|---|---|---|---|
| 9.1 | current power calculations with margins and sensitivities | **PARTLY** | `records/l9pwr` (`l9pwr_budget.py`, reproduces rv-pwr within 1e-9 W and every Layer 4 figure it overlaps from that record's inputs): per state LOW / PLAN / HIGH per load and rail, every converter against its maker's rating or drafted limit, the pack side, on the generators at `37bc2f1d` (DRAWN) and with the Layer 4 and 8 drafts (DRAFTED, not applied): the profile 43.30 W drawn, 44.20 W drafted (rv-pwr 42.82 W); sensitivities per state and over 12 to 16.8 V; six margin findings, L9P-F01 (D-11's all-transmit floor on the drafts, a demonstrated analysis defect for L4-E9) open; remains: the record's one focused review, L9P-F01's correction, the T-tier loads (8.4 W of the profile; rv-pwr's maker questions unsent), the re-run once the drafts are applied |
| 9.2 | current energy calculations with sensitivities | **OPEN** (unchanged) | PROVISIONAL; REQ-072 FAIL at desk; `energy_budget.py` and L4-E9's endurance rest on rv-pwr's 42.8 W profile, which l9pwr moves to 43.30 W drawn and 44.20 W drafted (energy-only 2.49 h and 2.44 h on L4-E10's 107.9 Wh, a consequence printed in l9pwr's R3, not this item's closure) |
