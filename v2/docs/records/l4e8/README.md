# l4e8: board A's VBUS20 bulk bank re-sized (layer 4 task L4-E8, MESHSAT-1357)

Prototype design, desk arithmetic. This folder closes finding B-4 of `../l4e/L4-ENERGY-ARCHITECTURE.md` (every EEHZK1V331P on
VBUS20 at most its 2.8 A rating at the 2:1 ESR spread) at both R11 outcomes L4-E4 and L4-E6 leave open (8 mOhm, 7.262 A; 7 mOhm,
8.300 A, only if bench V-A07 fails). The generator's dense node analysis it needs (`drafts/scripts/ripple_dense.py` of the
third fix-up, 26 September 2026) is in neither this tree nor its history; it is rebuilt here and validated against every
figure its record carries before it is used.

| File | What it is |
|---|---|
| `L4E8-BANK.md` | The one page: the bank as drawn, the rebuild and its validation table, the drawn bank at L4-E6's highest permitted currents against r11_dep.py's scaling, the decision and its reasons, the loop, what else the bank's capacitance moves, what stays INCONCLUSIVE with its measurement, bench row 7b.8 restated, the interaction with L4-E4 and L4-E6, and what L4-E4's release still needs |
| `ripple_dense.py` | The rebuild and the record's script (standard library; pdftotext for the makers' sheets). Run from the repository root: `python3 v2/docs/records/l4e8/ripple_dense.py > v2/docs/records/l4e8/ripple_dense.out`. It pins every file it reads (the generator, the netlist, r4-decisions.md, the three makers' sheets, L4-E4's and L4-E6's scripts and outputs, r11_dep.py and its output), runs L4-E4's `compute()` in-process for the highest permitted currents L4-E6 takes as `o["hi"]`, validates the rebuild, then evaluates, re-sizes and checks the loop. About three and a half minutes on the runner (a coarsened search, stated in its docstring and section 3) |
| `ripple_dense.out` | Its output, committed; the script reproduces it byte for byte |
| `apply_gen_sch_a_bank.py` | DRAFT for board A's generator owner: the front end's `bulk=`, `cout_extra=` and `cout_pre=` in `v2/ecad/tools/gen_sch_a.py`, `--bank 8` (default) or `--bank 7`. Default `--check`, writes only with `--write`, refuses a second application and any designator already in use, and refuses the repository's own generator until a `RELEASE.md` beside it reads "released: yes" and names an accepted check of L4-E8 (`check: <path>`). Composes with L4-E4's `apply_gen_sch_a_r11.py` and `apply_gen_sch_a_r138.py` and L4-E6's `apply_gen_sch_a_r12.py` in every order on disjoint lines. Never applied to the tree here |
| `README.md` | This list |

The predicates are held by `v2/ecad/tools/tests/test_l4e8.py`; run it with
`env -C v2/ecad/tools/tests python3 run.py test_l4e8`. The tests recompute the properties (the re-review's point, the drawn
node's recorded corner, the chosen bank at the 2:1 spread at 8 mOhm, the drawn bank's failure there) and read the committed
output's validation table; they do not re-run the whole script.

**Run order.** `ripple_dense.py` first (it refuses with exit 2 if a pinned input changed, 3 if an input cannot be parsed, 4 if a
reproduction or a predicate fails, and prints no section past 4 unless the rebuild is validated); then `test_l4e8`.

**Sources outside the tree, cited and not read by the script.** The predecessor's recovered draft,
`<worktrees>/_recovered/older/r4a-fixup-A-1136/tree/drafts/scripts/bulk_ripple.py` (sha256 `c6b55794a762ecee...`, recovered
from a session transcript; it is the second fix-up's version), and its loop model,
`<worktrees>/_recovered/older/r4a-fixup-A-1024/tree/drafts/scripts/loop_design.py` (sha256 `fe0d946bc020d4b6...`), with the
edits that followed them in that session's transcript (`r4a-fixup-A-1136/bash.log`). They gave the waveform construction, the
4096-point DFT, the two-node split, the half bridge's ESR and ESL figures and the loop model's corners; the bands, the grids'
counts and every figure validated against come from `gen_sch_a.py` and `v2/docs/records/r4a/r4-decisions.md`, which are in the
tree.
