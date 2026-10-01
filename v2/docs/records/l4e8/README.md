# l4e8: board A's VBUS20 bulk bank re-sized (layer 4 task L4-E8, MESHSAT-1357)

Prototype design, desk arithmetic. This folder closes finding B-4 of `../l4e/L4-ENERGY-ARCHITECTURE.md` (every EEHZK1V331P on
VBUS20 at most its 2.8 A rating at the 2:1 ESR spread) at both R11 outcomes L4-E4 and L4-E6 leave open (8 mOhm, 7.262 A; 7 mOhm,
8.300 A, only if bench V-A07 fails).

Each capacitor's current is derived from the node's topology, the operating conditions and the makers' equations. The figures of
the generator's lost dense analysis (`drafts/scripts/ripple_dense.py` of 26 September 2026, in neither this tree nor its history)
are a consistency check, reconciled where they differ.

| File | What it is |
|---|---|
| `L4E8-BANK.md` | The page: the derivation, the reconciliation table, the drawn bank at L4-E6's highest permitted currents, the decision on its sharing basis, the selected bank's per-can margins at frequency and temperature, the named uncertainties, the loop, what else the capacitance moves, bench row 7b.8, the interaction with L4-E4 and L4-E6, and what L4-E4's release still needs |
| `ripple_dense.py` | The calculation (standard library, PyYAML; pdftotext for the makers' sheets). Run from the repository root: `python3 v2/docs/records/l4e8/ripple_dense.py > v2/docs/records/l4e8/ripple_dense.out`. About six minutes on the runner, one process (the search is coarsened, as its docstring and out 3 state) |
| `ripple_dense.out` | Its output, committed; the script reproduces it byte for byte |
| `CORRECTIONS-DRAFT.md` | DRAFTS ONLY: the text proposed for `gen_sch_a.py`'s third fix-up comment and for `r11_dep.py`'s carried bank figures (and L4-E6's, which take them) |
| `apply_gen_sch_a_bank.py` | DRAFT for board A's generator owner: the front end's `bulk=` line in `v2/ecad/tools/gen_sch_a.py`, `--bank 8` (default, C236 and C237 added) or `--bank 7` (C236 to C239). See its docstring for the mode, the refusals and the composition |
| `inputs/recovered/` | The predecessor's drafts as a session transcript holds them, filed as cited inputs (their code is never run here) |
| `README.md` | This list |

**The draft's mode and refusals.**
- `--check` by default, writing only with `--write`.
- It refuses a second application and any designator already in use.
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
- the re-review's point;
- the drawn node's recorded corner;
- the chosen bank at the 2:1 spread at 8 mOhm, on the decision grids and converged, with the layout basis, and the drawn bank's
  failure there;
- the rating's frequency correction.

They also read the committed output's consistency and convergence lines.

## Inputs (every file the script reads, pinned by sha256 in its `PINS`)

| File | sha256 | Source |
|---|---|---|
| `v2/ecad/tools/gen_sch_a.py` | `6a136feec6c9cf4e...` | board A's generator, this tree, parsed by its syntax tree |
| `v2/ecad/pcb-a-power-a23/out/pcb-a-power.net` | `6c40250c47195ebb...` | board A's committed netlist |
| `v2/docs/records/r4a/r4-decisions.md` | `2e5a0c20fc9d4f25...` | the round 4 record: the lost analysis's bands, grids and figures |
| `v2/vendor/ti/lm5176-datasheet.pdf` | `98191bec36d43771...` | TI SNVSAI1D (June 2017, revised August 2021), https://www.ti.com/lit/ds/symlink/lm5176.pdf (`v2/vendor/sources.txt`, `SOURCES.yaml`) |
| `v2/vendor/ti/bq25731-datasheet.pdf` | `3e5e927fdf63cf6a...` | TI SLUSE66A, https://www.ti.com/lit/ds/symlink/bq25731.pdf (`SOURCES.yaml`: byte-identical to ti.com on 2026-09-25) |
| `v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf` | `5455014606c0b676...` | Panasonic Industry, ZK series catalog (pages dated 01-Apr-22 and 1-Dec-23), LCSC's copy for C454360, filed by commit `ada94128` on 4 September 2026; its URL is not recorded in `v2/vendor/sources.txt` |
| `v2/ecad/tools/pcb_envelope.yaml` | `35cf43a2b7098a76...` | the kit's envelope: `worst_inside_air_c` |
| `v2/docs/records/l4e4/l4e4_limits.py` and `.out` | `d4a484439a7b5303...`, `f68bf6951a6361ca...` | L4-E4's record, its `compute()` run in-process for `band()` (it re-runs `r11_dep.py` in a child) |
| `v2/docs/records/r11dep/r11_dep.py` and `.out` | `c5e9d5713abfcb07...`, `f9d2c6f23fab3edc...` | the R11 dependency record, pinned as L4-E4 reads it |
| `v2/docs/records/l4e6/l4e6_fault_handling.py` and `.out` | `5f97b5b34fb1d0e5...`, `4f7cefb270f326d1...` | L4-E6's record: `o["hi"]`'s expression (parsed), its printed currents, B-4 lines, boundaries and L1's qualifying temperature |
| `inputs/recovered/bulk_ripple-r4a-fixup-A-1136.py` | `c6b55794a762ecee...` | the second fix-up's `bulk_ripple.py`, recovered from a session transcript (`<worktrees>/_recovered/older/r4a-fixup-A-1136/`), cited for the waveform construction, the 4096-point DFT, the network split and the half bridge's ESR and ESL figures |
| `inputs/recovered/loop_design-r4a-fixup-A-1024.py` | `fe0d946bc020d4b6...` | the fix-up's `loop_design.py`, recovered the same way (`r4a-fixup-A-1024/`), cited for the loop model. The second fix-up's edits to it (the five ZK parts, the front end re-described with fifteen ceramics, `LOOP_WIDE`) are in that session's transcript and in `r4-decisions.md` |

No catalogue reading is used. The can's code (C278516) and the ceramic's (C596319) are the generator's own, carried unchanged.
