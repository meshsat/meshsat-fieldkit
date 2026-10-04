# int28b: integration set 28 (Layers 5 to 9's rounds onto set 27's frozen candidate; MESHSAT-1357)

Prototype design: nothing here has been built, powered or measured. This folder is the record of integration set 28 of 3 October 2026,
branch `fnd/int28b` from set 27's frozen candidate `94971c8c`: seven branches merged in the coordinator's order, the Layer 4 readers
that pin the files those rounds rewrote brought to the merged tree, the chain frozen with `_bin/freeze_l4_chain.sh`, the outputs of
Layers 5 to 9 that print those pins regenerated, and the checks and module tests run. It supersedes the set 28 preparation of
`records/int28/` (branch `fnd/int28`, `a1f696de`), whose scripts are reused here and which the r2 branches carry in their history.
The owner's instruction of 2 October 2026 (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-02.md`) binds it: no requirement changes, no
Layer 4 record's prose or figures change (pins and L4-E11's need() texts only), every regeneration goes through `_bin/regen_out.py`,
nothing is bought or sent. `RESULT.md` holds the outcome.

| File | What it is |
|---|---|
| `RESULT.md` | The merges and their resolutions, each re-pin (file, old sha, new sha), the check and test lines with every failure's cause and owner, the box re-takes owed, the proposed LAYER-STATUS rows for Layers 5, 6, 7, 8 and 12 |
| `apply_set28b.py` | The driver: the steps after the merges in dependency order (held sheets, the rebind, the registry, the trace and Layer 3 R2 pages, the L4 pins, the freeze, the later outputs, the identity blocks, the checks); each step idempotent, a reader's refusal reported and the chain continued |
| `apply_set28b_repins.py` | `--stage pins`: L4-E8 (lcsc_fill), L4-E11 (contract, PANEL.md, registry, L4-E5's output, L4-E9's page, and its need() texts for FW-C08, FW-A14 and PANEL.md's cold hold in Layer 5's wording), L4-E12 (lcsc_fill, L4-E8's output), L4-E9 (contract, interfaces, registry, L4-E5's, L4-E7's, L4-E8's and L4-E11's outputs, lcsc_fill, L4-E7's page at `d562e75a`), each regenerated through regen_out when it changed; `--stage later`: every output of Layers 5 to 9 whose printed pins no longer bind, regenerated. Every sha read from the tree at run time |
| `apply_set28b_rebind.py` | L5R3-F01: CFL-001, 005, 014, 015 and 016 rebound to Layer 5 round 3's PANEL.md and ASSEMBLY.md, seven bindings, each record's ground asserted byte-identical or changed only in PI-button lines (refused otherwise), one evidence entry per record and file |
| `apply_set28_rebind.py` | Copied from `records/int28/`: CFL-001, 005, 014, 015 and 016 rebound to the tree's PANEL.md with one evidence entry each; on this tree it reads "already applied" (the r2 branches carry int28's rebind and PANEL.md is unchanged since) |
| `resolve_both_sides.py` | Copied from `records/int28/` and extended: `--ours` keeps ours in a conflict block whose lines are all PINS entries (used for L4-E9's and L4-E11's pins at the l5r2 merge); without it both sides are kept, ours first |
| `stage_held_sheets.py` | Copied from `records/int28/`, its sha pass corrected (it skipped named paths without a same-line pin): stages the makers' held-back sheets from sibling checkouts, each verified by a record's pin |
| `scan_printed_pins.py` | Lists every committed output under `v2/docs` whose printed pins (regen_out's R4) are not the tree's: the outputs to regenerate after a merge |

## Run order (what was run, in this order, on 3 October 2026)

1. The seven merges, each `git merge --no-ff --no-commit`, resolved, pre-commit checked on the staged diff, committed as the owner.
2. `stage_held_sheets.py --write`; `apply_set28b_repins.py --stage pins --write`.
3. `bash _bin/freeze_l4_chain.sh <worktree>` (never edited).
4. `apply_set28b_repins.py --stage later --write`.
5. After each later merge (Layer 5 round 3, L4-E9 round 6, L4-E7's guard, Layer 5's F-12 round, Layers 6 and 7's rounds, the
   firmware's round 3): `apply_set28b_rebind.py --write` where PANEL.md or ASSEMBLY.md moved, then steps 2 to 4 again; six freezes.
6. The checks, `verify_l3am`, `verify_acceptance` and the single module run on the final tip (RESULT.md sections 3 and 4).

## Promotion (4 October 2026)

Promoted to main as `d834e6a7` (`d834e6a7be211d1cdd1b18ded54bec1c427048fd`) by fast-forward, pushed and mirrored. Gated by
`_bin/suite_gate.py` on three passes of that exact commit: the box on Python 3.12 (2747 passed, 0 failed, 13 skipped), the box on
Python 3.11 for test_l4e10 and test_l4e12 (48 passed, 0 failed), the runner for test_l4e7 (50 passed, 0 failed, 1 skipped, the gated
recompute); 228 of 228 modules, the tree unchanged after each pass. `v2/ecad/tools/candidate_guard.py check` passed before each pass
against the manifest recorded at the frozen commit (984 evidence files, four historical outputs declared unbound by path: cx1's check,
h2's and h3's counts, s99's stage; L4-E7's results cache frozen), and on main after the fast-forward.

Two earlier candidates were refused on the way, both by the coordinator's own errors, and are kept here as such:
- `37bc2f1d` (not pushed, reset): the requirements registry was edited by the CON-010/REQ-044 page rebind after the Layer 4
  freeze, so every Layer 4 record refused on its registry pin; the pages had been rendered without the full evidence archive. The
  order was redone (evidence, render, rebind, then freeze) and the owner's amendment added `candidate_guard.py`, which refuses such
  a candidate before any suite runs.
- `3b9aa97d`: one test failed (test_l4e9's page and output tables): `apply_close_r197.py` wrote "OPEN 0" into L4-E9's page counts row,
  which the output omits; corrected by `apply_close_r197_fix.py`, then a targeted run of every module reading L4-E9's files before
  the suite.

The proposed LAYER-STATUS rows (RESULT.md section 7) are not applied in this set: LAYER-STATUS.md is read by tests, so the rows go
into set 29 under its own gate. The supplier package re-issued from this commit is
`MESHSAT-SUPPLIER-HANDOVER-RELEASE-CANDIDATE-d834e6a7.zip` (12,894,538 bytes, sha256 29ed399a...).
