# l9pwr: Layer 9 item 9.1, the power budget on the current design (MESHSAT-1357)

3 October 2026, the Layer 9 author, worktree `l9pwr` on branch `fnd/l9pwr` from set 28's tip `37bc2f1d` (round 1, `38ef774c`);
**round 2, 4 October 2026, on branch `fnd/l9pwr2` from main `64cd25ee`** with `fnd/l9pwr` merged (`--no-ff`), the record's only
author since round 1's context ran out. Prototype design, desk arithmetic: nothing has been built, powered or measured. This
folder brings record rv-pwr's power model to the current design with margins and sensitivities. It edits no generator,
requirement, registry record or other record's file; rv-pwr's committed outputs stay as they are (other records pin them). The
drafts of Layers 4, 8 and 9 it models are printed DRAFTED and none is applied.

| File | What it is |
|---|---|
| `L9-POWER-BUDGET.md` | The page: round 2 in short; the totals per state on four trees (rv-pwr as committed, the generators as drawn, round 1's drafted tree and round 2's); what differs from rv-pwr and how each change is taken (D1 to D10); the converters against their limits and the four LM5176 5.1 V stages side by side; the pack path's elements; the reconciliation with Layer 4, record l8r2 and record l9stk; the sensitivities; the margin findings with class, status and owner; what other records' authors own; the decisions taken |
| `l9pwr_budget.py` | The script, run from the repository root: `python3 v2/docs/records/l9pwr/l9pwr_budget.py` (stdlib and pdftotext, about a second). It imports `v2/docs/records/rv-pwr/pwr_budget.py` unchanged, pins its inputs by sha256, parses every figure from its source (a record's output, a generator, a draft, a maker's datasheet), refuses when a figure is not found, reproduces rv-pwr on rv-pwr's own tree and every overlapping figure of another record from that record's inputs, then prints the current design's budget |
| `l9pwr_budget.out` | Its output, committed, regenerated only through `_bin/regen_out.py` (two byte-identical runs and every pin current): 0 the pins and the copies' sources; 1 the differences and how they are taken; 2 the model check; 3 the totals, 3b round 1's DRAFTED against round 2's; 4 the waterfall; 5 per state every load, rail and converter against its limit, 5b the LM5176 5.1 V stages side by side; 6 the pack current, 6b the pack path's elements; 7 D-11's floors with the step ladder and L4-E9 round 7's rule; 8 the reconciliation; 9 the sensitivities; 10 the findings; 11 the predicates |
| `inputs/` | Round 2's copies of other records' files, each made with `git show` at its commit and renamed `.txt` (record l8r2 at `89924e40`: its output and four drafts; record l9stk at `2c8b29fb`: its protection output; L4-E9 at `3737df82`: section 30 of its output); `inputs/SOURCES.txt` gives each source, commit, branch and sha256 |

Test: `v2/ecad/tools/tests/test_l9pwr.py`, run isolated with `env -C v2/ecad/tools/tests python3 run.py test_l9pwr test_public_hygiene`.

## Proposed LAYER-STATUS rows (for the integrator; LAYER-STATUS.md is not edited here)

| Item | Acceptance item (short) | Proposed state | Evidence, or what remains |
|---|---|---|---|
| 9.1 | current power calculations with margins and sensitivities | **PARTLY** | `records/l9pwr` round 2 (`l9pwr_budget.py`, reproduces rv-pwr within 1e-9 W and every figure of another record it overlaps from that record's inputs, round 1's tree rebuilt for L4-E9 round 7 and record l8r2): per state LOW / PLAN / HIGH per load and rail, every converter against its maker's rating or drafted limit, the pack side, on the generators at main `64cd25ee` (DRAWN) and with the Layer 4, 8 and 9 drafts (DRAFTED, ten drafts, not applied): the profile 43.30 W drawn, 44.58 W drafted (round 1 44.20 W; rv-pwr 42.82 W); sensitivities per state and over 12 to 16.8 V; six margin findings: L9P-F01 (D-11's all-transmit floor: 16.214 V needed against L4-E9 round 7's 16.1 V, its rule giving 16.4 V) open for L4-E9, L9P-F02 resolved in the drafts (CONDITIONAL on l8r2's C4-1 to C4-6); remains: the record's one focused review, L9P-F01's correction, the T-tier loads, the re-run once the drafts are applied |
| 9.2 | current energy calculations with sensitivities | **OPEN** (unchanged) | PROVISIONAL; REQ-072 FAIL at desk; `energy_budget.py` and L4-E9's endurance rest on rv-pwr's 42.8 W profile, which l9pwr moves to 43.30 W drawn and 44.58 W drafted (energy-only 2.49 h and 2.42 h on L4-E10's 107.9 Wh, a consequence printed in l9pwr's R3, not this item's closure) |
