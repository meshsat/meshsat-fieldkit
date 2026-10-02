# l4e8: board A's VBUS20 bulk bank re-sized (layer 4 task L4-E8, MESHSAT-1357)

Prototype design, desk arithmetic. This folder closes finding B-4 of `../l4e/L4-ENERGY-ARCHITECTURE.md` (every EEHZK1V331P on
VBUS20 at most its 2.8 A rating) at both R11 outcomes L4-E4 and L4-E6 leave open (8 mOhm, 7.262 A; 7 mOhm, 8.300 A, only if bench
V-A07 fails).

Each capacitor's current is derived from the node's topology, the operating conditions and the makers' equations. The figures of
the generator's lost dense analysis (`drafts/scripts/ripple_dense.py` of 26 September 2026, in neither this tree nor its history)
are a consistency check, reconciled where they differ.

This is the second fix round, after the collaborator's check of `5ff06474` and its recheck of `cc95fe1f`:
- coincident harmonics are added at the worst phase;
- the front end's frequency comes from its specified row;
- the lifetime is CONDITIONAL;
- every can's current is held by a conservative BOUND over arbitrary independent cans and passives, checked against brute-force
  sampling, rather than by a search;
- the loop is checked over the cans' whole cold ESR envelope.

The bank becomes the six drawn cans, each behind its own 45 mOhm ballast resistor. The front end's Cc2 becomes 3.3 nF, and both
go in with L4-E6's R12 12 mOhm.

| File | What it is |
|---|---|
| `L4E8-BANK.md` | The page: the status, the recheck and what changed, the bound and why it is conservative, the decision, the chosen bank's rating, ballast and energy term, the loop over the cold envelope, the transient figures, the reconciliation table, bench row 7b.8, the named uncertainties, the interaction with L4-E4 and L4-E6, and what L4-E4's release still needs |
| `ripple_dense.py` | The calculation (standard library, PyYAML; pdftotext for the makers' sheets). Run from the repository root: `python3 v2/docs/records/l4e8/ripple_dense.py > v2/docs/records/l4e8/ripple_dense.out`. About eight minutes on the runner, one process. The search of sections 4 and 5 is coarsened as its docstring and out 3 state; section 6's bound does not sample |
| `ripple_dense.out` | Its output, committed; the script reproduces it byte for byte |
| `CORRECTIONS-DRAFT.md` | DRAFTS ONLY: the text proposed for `gen_sch_a.py`'s third fix-up comment and for `r11_dep.py`'s carried bank figures (and L4-E6's, which take them), per spread |
| `apply_gen_sch_a_bank.py` | DRAFT for board A's generator owner: a 45 mOhm ballast resistor (R221 to R226) in series with each of the front end's six cans in `v2/ecad/tools/gen_sch_a.py`, and the front end's Cc2 (C6) at 3.3 nF. See its docstring for the mode, the refusals, the order with L4-E6's R12 and the composition |
| `checks/astra-check-l4e8-1.md` | The engineering collaborator's check of `5ff06474` (accepted: no; blockers B1 to B4 and four minors), filed as received. The page's section "The recheck, and what changed" closes with how its items stand |
| `checks/astra-check-l4e8-2.md` | The engineering collaborator's targeted recheck of `cc95fe1f` (accepted: no; R1/R2 the bound over fully independent cans not established, R4 the cold-loop closure rule too weak; the last collaborator run on L4-E8), filed as received. The page's section "The recheck, and what changed" maps each item to its change |
| `checks/check-l4e8-3.md` | Claude's (the coordinator's) verification at `a282c8b7` after the collaborator's two runs: the bound's construction read, `mink` and `inv_hull` tested with the coordinator's own random cases, the output reproduced, the tests run (accepted: yes; B-4 closed at R11 8 mOhm, the 7 mOhm fallback CONDITIONAL); not a model review and not an Astra check |
| `inputs/recovered/` | The predecessor's drafts as a session transcript holds them, filed as cited inputs (their code is never run here) |
| `README.md` | This list |

**The draft's mode and refusals.**
- `--check` by default, writing only with `--write`.
- It refuses a second application and any designator already in use.
- It refuses the repository's own generator until L4-E6's R12 12 mOhm is in the front end's call (the ORDER).
- It refuses the repository's own generator until a `RELEASE.md` beside it reads "released: yes" and names an accepted check of
  L4-E8 (`check: <path>`).
- It composes with L4-E4's `apply_gen_sch_a_r11.py` and `apply_gen_sch_a_r138.py` and L4-E6's `apply_gen_sch_a_r12.py` in every
  order on disjoint lines.
- It was never applied to the tree here.

## Run order

1. `ripple_dense.py`. Its exit codes:
   - 2: a pinned input changed;
   - 3: an input cannot be parsed;
   - 4: a reproduction or a predicate failed.
2. `env -C v2/ecad/tools/tests python3 run.py test_l4e8`.

The tests recompute the properties rather than re-running the whole script:
- the re-review's point and the drawn node's recorded corner;
- the check's two counterexamples, the coincidence (B1) and the siblings' ESL (B2);
- the frequency envelope;
- the unbounded no-floor bank, and the drawn bank's failure;
- the bound's enclosures on random points;
- each bin's bound against brute-force sampling, and the committed figure against end-to-end samples;
- the committed bound at both outcomes and every smaller catalogue value excluded;
- the rating's frequency correction and the lifetime printed CONDITIONAL;
- the loop at both ends of the cold envelope with the chosen Cc2, and the drawn Cc2's failure there;
- the draft's changes (the ballast and Cc2 only) and its refusal of the repository's generator without L4-E6's R12.

They also read the committed output's consistency and convergence lines.

## Inputs (every file the script reads, pinned by sha256 in its `PINS`)

| File | Source |
|---|---|
| `v2/ecad/tools/gen_sch_a.py` | board A's generator, this tree, parsed by its syntax tree |
| `v2/ecad/pcb-a-power-a23/out/pcb-a-power.net` | board A's committed netlist |
| `v2/docs/records/r4a/r4-decisions.md` | the round 4 record: the lost analysis's bands, grids and figures |
| `v2/vendor/ti/lm5176-datasheet.pdf` | TI SNVSAI1D (June 2017, revised August 2021), https://www.ti.com/lit/ds/symlink/lm5176.pdf (`v2/vendor/sources.txt`, `SOURCES.yaml`) |
| `v2/vendor/ti/bq25731-datasheet.pdf` | TI SLUSE66A, https://www.ti.com/lit/ds/symlink/bq25731.pdf (`SOURCES.yaml`: byte-identical to ti.com on 2026-09-25) |
| `v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf` | Panasonic Industry, ZK series catalog (pages dated 01-Apr-22 and 1-Dec-23), LCSC's copy for C454360, filed by commit `ada94128` on 4 September 2026; its URL is not recorded in `v2/vendor/sources.txt` |
| `v2/vendor/passives/milliohm-hojlr2512-series.pdf` | the HoJLR2512 series sheet (the ballast's range, TCR, 3 W, its derating from 70 C to zero at 170 C and its operating range), as `r11_dep.py` pins it |
| `v2/vendor/passives/held/uniroyal-series-11cd644d.pdf` | UNI-ROYAL thick film chip resistors (RT's part, 0603WAF4022T5E): held back by the maker's terms, installed with the held evidence; its URL is in `v2/vendor/sources.txt` |
| `v2/ecad/tools/lcsc_fill.py` | RT's order code and tolerance; the 0603 capacitors Cc2 is chosen from |
| `v2/ecad/tools/pcb_envelope.yaml` | the kit's envelope: `worst_inside_air_c` and the in-use minimum |
| `v2/docs/records/l4e4/inputs/jlc-search-hojlr2512-3w-2026-10-01.json` | L4-E4's catalogue reading: the ballast values in stock |
| `v2/docs/records/l4e4/l4e4_limits.py` and `.out` | L4-E4's record, its `compute()` run in-process for `band()` (it re-runs `r11_dep.py` in a child) |
| `v2/docs/records/r11dep/r11_dep.py` and `.out` | the R11 dependency record, pinned as L4-E4 reads it |
| `v2/docs/records/l4e6/l4e6_fault_handling.py` and `.out` | L4-E6's record: `o["hi"]`'s expression (parsed), its printed currents, B-4 lines, boundaries and L1's qualifying temperature |
| `inputs/recovered/bulk_ripple-r4a-fixup-A-1136.py` | the second fix-up's `bulk_ripple.py`, recovered from a session transcript (`<worktrees>/_recovered/older/r4a-fixup-A-1136/`), cited for the waveform construction, the 4096-point DFT, the network split and the half bridge's ESR and ESL figures |
| `inputs/recovered/loop_design-r4a-fixup-A-1024.py` | the fix-up's `loop_design.py`, recovered the same way (`r4a-fixup-A-1024/`), cited for the loop model. The second fix-up's edits to it are in that session's transcript and in `r4-decisions.md` |
