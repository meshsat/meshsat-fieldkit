# l9pwr: Layer 9 item 9.1, the power budget on the current design (MESHSAT-1357)

3 October 2026, the Layer 9 author, worktree `l9pwr` on branch `fnd/l9pwr` from set 28's tip `37bc2f1d` (round 1, `38ef774c`);
**round 2, 4 October 2026, on branch `fnd/l9pwr2` from main `64cd25ee`** with `fnd/l9pwr` merged (`--no-ff`), the record's only
author since round 1's context ran out; **round 3, 4 October 2026, on branch `fnd/l9r3` from set 29's line `e58e906a`** (a tool
correction by the record's author for that round; the table at the end of this page). Prototype design, desk arithmetic: nothing has been built, powered or measured. This
folder brings record rv-pwr's power model to the current design with margins and sensitivities. It edits no generator,
requirement, registry record or other record's file; rv-pwr's committed outputs stay as they are (other records pin them). The
drafts of Layers 4, 8 and 9 it models are printed DRAFTED and none is applied.

| File | What it is |
|---|---|
| `L9-POWER-BUDGET.md` | The page: round 2 in short; the totals per state on four trees (rv-pwr as committed, the generators as drawn, round 1's drafted tree and round 2's); what differs from rv-pwr and how each change is taken (D1 to D10); the converters against their limits and the four LM5176 5.1 V stages side by side; the pack path's elements; the reconciliation with Layer 4, record l8r2 and record l9stk; the sensitivities; the margin findings with class, status and owner; what other records' authors own; the decisions taken |
| `l9pwr_budget.py` | The script, run from the repository root: `python3 v2/docs/records/l9pwr/l9pwr_budget.py` (stdlib and pdftotext, about a second). It imports `v2/docs/records/rv-pwr/pwr_budget.py` unchanged, pins its inputs by sha256, parses every figure from its source (a record's output, a generator, a draft, a maker's datasheet), refuses when a figure is not found, reproduces rv-pwr on rv-pwr's own tree and every overlapping figure of another record from that record's inputs, then prints the current design's budget |
| `l9pwr_budget.out` | Its output, committed, regenerated only through `_bin/regen_out.py` (two byte-identical runs and every pin current): 0 the pins and the copies' sources; 1 the differences and how they are taken; 2 the model check; 3 the totals, 3b round 1's DRAFTED against round 2's; 4 the waterfall; 5 per state every load, rail and converter against its limit, 5b the LM5176 5.1 V stages side by side; 6 the pack current, 6b the pack path's elements; 7 D-11's floors with the step ladder and L4-E9 round 7's rule; 8 the reconciliation; 9 the sensitivities; 10 the findings; 11 the predicates |
| `inputs/` | Round 2's copies of other records' files, each made with `git show` at its commit and renamed `.txt` (record l8r2 at `89924e40`: its output and four drafts; L4-E9 at `3737df82`: section 30 of its output); `inputs/SOURCES.txt` gives each source, commit, branch and sha256. Record l9stk's protection output was a copy at `2c8b29fb` until round 3, which retired it: the script reads the tree's `v2/docs/records/l9stk/l9stk_protection.out` |

Test: `v2/ecad/tools/tests/test_l9pwr.py`, run isolated with `env -C v2/ecad/tools/tests python3 run.py test_l9pwr test_public_hygiene`.

## Round 4 (4 October 2026, task T5 on `fnd/l9t5`): C1 and the case row C-ALLTX rev 2

- **C1 (CORRECTED, the last step of out 1):** PS-ALLTX carries the standby WiFi card off in every scenario, as REQ-018's acceptance
  and CONOPS 4a define the state; DRAWN and round 1's tree keep rv-pwr's state. On DRAFTED, PS-ALLTX at the pack moves from
  174.23 / 209.89 / 292.03 W to 174.23 / 208.47 / 279.63 W; its raw HIGH row at VBAT from 276.373 W (17.4792 V) to 265.274 W (16.8626 V).
- **Out 7b:** C-ALLTX rev 2 computed from the row's text at the VBAT the case sets: 241.039 W at VBAT, **needs 15.5162 V** at 18 A,
  **deficit +0.292 W** against the 240.747 W allowance. The row's quoted 16.214 V is D-11's basis (out 7), printed beside it.
- **Did not move:** L9P-F01's 16.214 V (D-11's basis), L9P-F03's 7.181 A and 7.472 A, every state but PS-ALLTX, every converter's
  margin but slot 3's in PS-ALLTX at HIGH (3.2639 A, the standby card off). One predicate restated: PS-ALLTX joins PS-SURV below round
  1's PLAN.
- The uncertainty, the approaches and the corrections are record l9t5's (`v2/docs/records/l9t5/`).

## Round 3 (4 October 2026, the integration of set 29): a tool correction, what moved and what did not

The script refused on set 29's tree at its read of +12V_FAN's efficiency in L4-E11's `apply_gen_sch_e_aux.py` (L4-E11's round 9
broke the declaration over two lines when it corrected finding L8P-F03). It was the only stale read. The declaration and the
battery FETs are now parsed from the drafts; record l9stk's protection output is read from the tree. It closes no finding:
L9P-F01 (D-17) and L9P-F03 (I-03) stay OPEN as round 2 left them.

| Figure | Before (`e58e906a`, round 2's output at `51821143`) | Now | Cause |
|---|---|---|---|
| out 0, eight pins: L4-E9's page, L4-E11's output and its two drafts, L4-E12's output, the requirements registry, record l9stk's protection output, `inputs/SOURCES.txt` | round 2's | this tree's | set 29's merges and freeze; the l9stk copy retired |
| out 0, the copies' list | names the l9stk copy at `2c8b29fb` | names the tree's file as read with no copy | the copy retired |
| out 1, D9's text and figure line | "LM5069-2", "l9stk at 2c8b29fb" | "the LM5069-1 (latch-off, l9stk 15.4b)", read from the output | record l9stk 15.4b selects the -1 |
| out 1, D1's and D10's text and D10's figure line | "its designator L4-E11's" | "L4-E11's charger draft writes Q39, Q40, Q42" | L4-E11's round 9 drafts the third FET |
| out 11, predicates | 31 | 32: the draft's battery FETs are the three record l9stk selected | round 3 |

**No figure moved.** In particular:

| Figure | Value, before and now |
|---|---|
| L9P-F01, the all-transmit basis's needed rest voltage (out 7) | 16.214 V (16.014 V with the coolers at the maker's 2.0 W) |
| L9P-F03, the device rail (out 5, 5b) | 7.181 A at 5.1 V and 7.472 A at the least load voltage 4.9019 V, against the loop's least 7.0957 A |
| the pack path (out 6b) | 0.038064 Ohm drafted (0.038068 on round 1's tree); the three battery FETs 7.0453 mOhm against the pair's 10.568 |
| what L4-E9 reads from its copy at `51821143` (out 6, 7, 8 and 10: the pack current, the floors, R1, R1c, R8, R10, L9P-F01) | every line unchanged; R8's fan input 15.1125 W, which L4-E9's fans-off bound 15.374 V subtracts, is unchanged |
| every state's LOW / PLAN / HIGH, every converter's margin, every sensitivity | unchanged |

**Order of regeneration:** `l9stk_stackups.py`, `l9stk_copper.py`, `l9stk_protection.py`, then `l9pwr_budget.py`, each through
`_bin/regen_out.py`. This record pins L4-E9's page, L4-E11's output and drafts, L4-E12's output and the requirements registry
by sha256, so a regeneration or re-pin of any of them owes a regeneration here. The copy of L4-E9's round 7 section 30
(`3737df82`, the 16.1 V floor L4-E9's round 8 has since withdrawn) is kept as round 2 read it: R11 and L9P-F01 reproduce and
judge that figure, and restating them on L4-E9's round 8 is this record's next round, not this correction.

## Proposed LAYER-STATUS rows (for the integrator; LAYER-STATUS.md is not edited here)

| Item | Acceptance item (short) | Proposed state | Evidence, or what remains |
|---|---|---|---|
| 9.1 | current power calculations with margins and sensitivities | **PARTLY** | `records/l9pwr` round 2 (`l9pwr_budget.py`, reproduces rv-pwr within 1e-9 W and every figure of another record it overlaps from that record's inputs, round 1's tree rebuilt for L4-E9 round 7 and record l8r2): per state LOW / PLAN / HIGH per load and rail, every converter against its maker's rating or drafted limit, the pack side, on the generators at main `64cd25ee` (DRAWN) and with the Layer 4, 8 and 9 drafts (DRAFTED, ten drafts, not applied): the profile 43.30 W drawn, 44.58 W drafted (round 1 44.20 W; rv-pwr 42.82 W); sensitivities per state and over 12 to 16.8 V; six margin findings: L9P-F01 (D-11's all-transmit floor: 16.214 V needed against L4-E9 round 7's 16.1 V, its rule giving 16.4 V) open for L4-E9, L9P-F02 resolved in the drafts (CONDITIONAL on l8r2's C4-1 to C4-6); remains: the record's one focused review, L9P-F01's correction, the T-tier loads, the re-run once the drafts are applied |
| 9.2 | current energy calculations with sensitivities | **OPEN** (unchanged) | PROVISIONAL; REQ-072 FAIL at desk; `energy_budget.py` and L4-E9's endurance rest on rv-pwr's 42.8 W profile, which l9pwr moves to 43.30 W drawn and 44.58 W drafted (energy-only 2.49 h and 2.42 h on L4-E10's 107.9 Wh, a consequence printed in l9pwr's R3, not this item's closure) |
