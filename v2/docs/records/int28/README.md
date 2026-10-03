# int28: the preparation of integration set 28 (Layers 5, 6 and 7's first passes onto the Layer 4 line; MESHSAT-1357)

Prototype design: nothing here has been built, powered or measured. This folder is the record of the set 28 preparation of 3 October
2026 (branch `fnd/int28` from `fnd/l4e9`'s consolidation round 3 at `f08e1342`): the three layer branches merged, the Layer 4 readers
that pin the files Layer 5 wrote brought to the merged tree, the five registry readings bound to PANEL.md rebound, the checks run, and
what remains for the coordinator who promotes set 28 after set 27. The owner's instruction of 2 October 2026
(`v2/docs/handover/OWNER-INSTRUCTION-2026-10-02.md`) binds it; the preparation changes no requirement, no L4 record's prose or figures
(pins, one reading mechanism and need() texts only), buys nothing and contacts nobody. `RESULT.md` holds the outcome.

| File | What it is |
|---|---|
| `RESULT.md` | The result: the merge order and the two conflicts with their resolution, each re-pin (file, old sha, new sha), the check lines, the module test line with every failure named and dispositioned, the box re-takes owed, the proposed LAYER-STATUS rows for Layers 5, 6 and 7, and what remains for the coordinator |
| `apply_set28.py` | The driver: the steps after the merges in their dependency order (held sheets, rebind, registry, trace page, re-pins and regeneration, identity block, the checks), each step idempotent; a step reporting "already applied" is accepted |
| `resolve_both_sides.py` | The merge-conflict resolver used for `v2/vendor/sources.txt` and `v2/docs/parts/PROCUREMENT.md`: both sides kept, ours (Layer 6) first, no line dropped or changed; refuses a file without markers |
| `stage_held_sheets.py` | Stages the makers' held-back sheets (gitignored `held/` folders) from sibling checkouts on this host, each verified by the sha256 a record pins; nothing fetched. A fresh worktree holds none and every Layer 4 reader that pins one refuses without it |
| `apply_set28_rebind.py` | L5-F02: CFL-001, CFL-005, CFL-014, CFL-015 and CFL-016 rebound from PANEL.md's old content to the merged page, one evidence entry each (what differs, what each rests on, re-deciding nothing); the pattern of `records/retake6/apply_rebind_current_evidence.py` |
| `apply_set28_repins.py` | L5-F01: `l4e5_source_control.py` reads the contract where it analysed it (its own draft was applied by Layer 5; pin unchanged), `l4e11_power.py` re-pinned (hwfw, panel, reqs, l4e5) with its need() texts for FW-C08, FW-A14 and PANEL.md's cold hold quoted from the merged files, `l4e9_power_path.py` re-pinned (hwfw, ifaces, reqs, l4e5, l4e11); the three outputs regenerated through `_bin/regen_out.py` in the order L4-E5, L4-E11, L4-E9. Every sha read at run time |
| `apply_set28_procurement_renumber.py` | PREPARED, NOT RUN: the merged PROCUREMENT.md carries two sections numbered 8 (Layer 6's, then Layer 7's); this renumbers Layer 7's to 9 with its three mentions and its test's assertion. Running it rewrites Layer 7's text, which the preparation was told not to do: the integrator's call |

## Run order (what was run, in this order, on 3 October 2026)

1. `git merge --no-ff fnd/l5pwr` (1e18a1ca), `fnd/l6pwr` (eda42b78), `fnd/l7pwr` (2087060b); the two conflicts of the third resolved
   with `resolve_both_sides.py` (sources.txt; PROCUREMENT.md with `--md`).
2. `stage_held_sheets.py --write` (the readers refuse without the held sheets; 43 of 45 pinned paths staged from siblings, plus
   L4-E7's three held Samsung readings by their sha; Panasonic's ZA sheet has no verified copy on this host).
3. `apply_set28_repins.py --write` (L4-E5's mechanism, L4-E11's pins and texts, L4-E9's pins; three regenerations).
4. `apply_set28_rebind.py --write`; `env -C v2/ecad/tools python3 rules_lib.py requirements`; `rules_render.py --requirements`;
   `apply_set28_repins.py --write` again (the reqs pins of L4-E9 and L4-E11, their regeneration).
5. `records/l6pwr/apply_part_identities_block.py --check` (the block is in the merged yaml); `part_identities.py check`.
6. The renderers' `--check`; the module tests of the brief in the background (`RESULT.md` section 5).

On a re-run (the branch re-based onto set 27's final commit): `apply_set28.py` runs steps 2 to 5 in dependency order; the merges and the
resolution are the coordinator's with `resolve_both_sides.py` ready.
