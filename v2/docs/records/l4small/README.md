**W133 (7 October 2026), stream l4small, branch `fnd/l4small` from main `be07863b`. DONE: the apply scripts of L4A-60 (revision X not admitted, SESSION L9T5-D11), L4A-80 (the B2 sweep, SESSION L4E7-D1) and W130's correction 2 (R-208's R264 and C264), each dry-run on main's files and on set 32's (fnd/int32 `4c8196a0`); record l4e7's decision L4E7-D1 written in `B2-PRESENCE.md` section 8. NOT DONE: the tests with the scripts applied, the acceptance greps, test_l4small. NEXT: apply in the worktree uncommitted, regenerate, run the affected tests, restore.**

# Stream l4small: Layer 4's register tasks L4A-60 and L4A-80, and W130's correction 2 (MESHSAT-1357)

Worker W133 for the coordinator, from the AI-scope register's draft 2 (`_runs/l4ai/REGISTER.draft.md`, section 9 items 3 and 4,
found fit by W127) and W130's check of the RIC commits ("Corrections needed" item 2). Record text and SESSION decisions with their
reversals: no circuit, net, part, figure, verdict or state of a cx46 item changes, and no cx46 item closes. Nothing in this kit has
been built, bought, powered or measured.

Set 32 (`fnd/int32`, be07863b..4c8196a0) changes most of the files these tasks touch, so every such file is changed ONLY by an apply
script beside its record, run by the set 33 integrator on the integrated tree; this branch commits the scripts, not their results.
One engine (`l4small_edit.py`) holds the checks every script makes (E1 to E6: each old text once, the new text different and not yet
present, a second run refused, no line moved, insertion only where a page keeps its history, the result re-parsed, all or nothing).

## The apply scripts (UNAPPLIED; the integrator's, in this order)

| Script | Files | Then regenerate |
|---|---|---|
| `records/l9t5/apply_l4small_revx.py` | `T10-ROUND5.md` (9 insertions and section W133, the decision L9T5-D11), `L9T5-CASES.md`, `l9t5_t10.py`, `l9t5_connected.py`, `apply_hw_fw_contract_t10.py` | `l9t5_t10.out`, `l9t5_connected.out` and their dependants |
| `records/l9t5/apply_l4small_layer6.py` | `v2/docs/parts/STM32H743-COMPATIBILITY.md` (F1, five matrix rows, HC6-SC-1), `v2/docs/parts/PROCUREMENT.md` (U41, U51, U61), CON-017's evidence pin and item (3) in `pcb_requirements.yaml` and `REQUIREMENTS-TRACE.md` | `rules_render.py --requirements --check` |
| `records/l4close/apply_l4small_ledger.py` | `REMAINING-ENGINEERING.md` (RE-8, RE-18, HO-G, two summary rows), `P0-POWER-LIST.md` (one quotation), `l4e9_power_path.py` and `L4-POWER-ARCHITECTURE.md` (the ledger rows' copies, SUP8G) | `l4e9_power_path.out` |
| `records/l4small/apply_l4small_register.py` | `DOWNSTREAM-REGISTER.md` R-208 (W130's correction 2; the two cited lines read at apply time) | `l4e9_power_path.out` |
| `records/l4small/apply_l4small_b2.py` | `apply_gen_sch_e_p0sol_b2.py` (the owner-request refusal; the tree's generator refused always), `records/l9t5/apply_l4e9_changelist_p0.py` (docstring label) | `l4e7_p0sol.out`, `l9t5_connected.out` (their pins of the two drafts) |
| `records/l4small/apply_l4small_tests.py` | `test_w11l9t5.py` (the restated generator check), `test_l4e7.py` (a docstring label) | none |

Committed directly (no set 32 or l4k change): `records/l4e7/B2-PRESENCE.md` section 8 (L4E7-D1, appended), this folder.

## SESSION decisions (under the owner's ruling of 21 September 2026 and his standing rule of 26 September 2026)

| Id | Decision | Why | To reverse |
|---|---|---|---|
| L9T5-D11 | revision X NOT ADMITTED; the supervisors revision V only; the rev X qualification an UNSELECTED OPTION | record l9t5, `T10-ROUND5.md` section W133 (written by `apply_l4small_revx.py`), with authority_why, ruled_by, ruled_on and reversed_by | as written there |
| L4E7-D1 | no presence-pair route is taken up; HO-G outside the baseline with nothing resting on it; the B2 draft refuses the tree's generator always | record l4e7, `B2-PRESENCE.md` section 8 (committed here), with its fields | as written there |
| W133-D1 | the two decisions live in their records' own decision lists, not in `tools/pcb_decisions.yaml` | that file indexes the numbered decisions of `OWNER-DECISIONS-2026-09-11.md` and the rule-board pairs they hold (`decisions_render.py`, `test_decision_register.py`); neither decision is in that record or holds a pair, and record l9t5 and record l4e7 already keep their SESSION decisions on their pages (L9T5-D1 to D10; B2-PRESENCE section 6); rendering `OWNER-DECISIONS-OPEN.md` on this tree would also read an `out/rule-audit` this worktree does not hold | add each as decision 60 and 61 with a heading in the record and render the page where the rule audit is |
| W133-D2 | `apply_l4small_b2.py` and `apply_l4small_register.py` sit in this folder, not beside records l4e7 and l4e9 | L4-E9's generator refuses any `records/l4e*/apply_*.py` its change list does not name (`l4e9_power_path.py` lines 6687 to 6689; also `test_l4e9.py` lines 233 to 247 and 1159, `test_l4e7.py` line 1104): beside those records they stopped `apply_l4e9_changelist_p0.py --check` (found by `test_w11l9t5`) | move them back and add them to L4-E9's OUT_OF_BASELINE |
| W133-D3 | every edit to a page that keeps its history is an insertion (the old words stay, labelled), and no edit moves a line | record l9t5's pages are held to it (`test_w9l9t5`), the ledger and the register are cited by line everywhere, and the earlier words are the evidence of what was superseded | none needed |
| W133-D4 | CON-017's statement and acceptance stay as written: clause (5), revision V or X, is the erratum's bound, which revision V meets; only its evidence pin of the compatibility page is rebound | narrowing the requirement would be a registry amendment the selection does not need (constitution section 1: amend only when necessary) | restate clause (5) to revision V by a controlled amendment |
| W133-D5 | R-208's two citations read their line numbers at apply time | set 32 moves the l8p reading from line 420 to 432; W130's numbers are main's | write the numbers by hand |
