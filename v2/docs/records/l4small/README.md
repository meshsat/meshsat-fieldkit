**W133 (7 October 2026, 04:21 to 05:45 CEST), stream l4small, branch `fnd/l4small` from main `be07863b`. DONE: L4A-60 (revision X not admitted, SESSION L9T5-D11), L4A-80 (the B2 wording swept, SESSION L4E7-D1) and W130's correction 2 (R-208's R264 and C264), as six apply scripts for set 33 and record l4e7's `B2-PRESENCE.md` section 8; each script dry-run on main and on set 32's tip `06d064ff`, and with record l4k's five scripts in both orders (byte-identical); applied in this worktree uncommitted, the direct outputs regenerated, the affected tests run, then restored. NOT DONE: no independent check has read any of it (the register's targeted check of L4A-80 is owed); the dependency pass after the scripts (the coordinator's, section 4); the l4e7 re-key the Layer 6 script owes. NEXT: the coordinator applies the scripts in set 33 (section 4).**

# Stream l4small: Layer 4's register tasks L4A-60 and L4A-80, and W130's correction 2 (MESHSAT-1357)

Worker W133 for the coordinator, from the AI-scope register's draft 2 (`_runs/l4ai/REGISTER.draft.md`, section 9 items 3 and 4,
found fit by W127) and W130's check of the RIC commits ("Corrections needed" item 2). Record text and SESSION decisions with their
reversals: no circuit, net, part, figure, verdict or state of a cx46 item changes, and no cx46 item closes (cx46 CORRECTIONS NOT
CLOSED; Layer 4's DESK gate NOT PASSED; power-design closure and fabrication release BLOCKED). Nothing in this kit has been built,
bought, powered or measured.

Set 32 (`fnd/int32`) changes most of the files these tasks touch, so every such file is changed ONLY by an apply script, run by the
set 33 integrator on the integrated tree; this branch commits the scripts, not their results. One engine (`l4small_edit.py`) holds
the checks every script makes (E1 to E6: each old text once, the new text different and not yet present, a second run refused, a
partial state refused, no line moved, insertion only where a page keeps its history, the result re-parsed, all or nothing).

## 1. The apply scripts (UNAPPLIED; the integrator's)

| Script | Files | Then regenerate |
|---|---|---|
| `records/l9t5/apply_l4small_revx.py` | `T10-ROUND5.md` (9 insertions and section W133, the decision L9T5-D11), `L9T5-CASES.md` (2), `l9t5_t10.py` (7 literals: 10a, 10h (1), 10i, 10j (f), the disposition, L9T5-F22, a predicate's words), `l9t5_connected.py` (3), `apply_hw_fw_contract_t10.py` (FW-B20's row: "revision X NOT ADMITTED"; its docstring) | `l9t5_t10.out`, `l9t5_connected.out` |
| `records/l9t5/apply_l4small_layer6.py` | `v2/docs/parts/STM32H743-COMPATIBILITY.md` (F1, five matrix rows, HC6-SC-1), `v2/docs/parts/PROCUREMENT.md` (U41, U51, U61: "revision V ONLY"), CON-017's evidence pin and item (3) in `pcb_requirements.yaml` and `REQUIREMENTS-TRACE.md`, the registry digest in `handover/layer3/REQUIREMENTS-L3-R2.md`'s header | see section 4: OWES THE L4-E7 RE-KEY |
| `records/l4close/apply_l4small_ledger.py` | `REMAINING-ENGINEERING.md` (RE-8's task and its two quoted lines, RE-18, HO-G, two summary rows), `P0-POWER-LIST.md` (one quotation), `l4e9_power_path.py` and `L4-POWER-ARCHITECTURE.md` (the ledger rows' copies, SUP8G) | `l4e9_power_path.out` and the outputs that pin the page |
| `records/l4small/apply_l4small_register.py` | `DOWNSTREAM-REGISTER.md` R-208: W130's words inserted after set 31's applied row WP-22, the two cited lines read at apply time (main: 420 and 79; set 32: 432 and 79) | `l4e9_power_path.out` |
| `records/l4small/apply_l4small_b2.py` | `apply_gen_sch_e_p0sol_b2.py`: the refusal that made route B2 wait on an owner ruling restated, and the tree's generator refused always, whatever record l4e7's RELEASE.md says | `l4e7_p0sol.out` |
| `records/l4small/apply_l4small_tests.py` | `test_w11l9t5.py` (the restated generator check), `test_l4e7.py` (a docstring label) | none |

Committed directly (neither file is changed by set 32 or by `fnd/l4k`): `records/l4e7/B2-PRESENCE.md` section 8 (L4E7-D1, appended,
no line moved), this folder, and `v2/ecad/tools/tests/test_l4small.py`.

## 2. SESSION decisions (under the owner's ruling of 21 September 2026 and his standing rule of 26 September 2026)

| Id | Decision | Why | To reverse |
|---|---|---|---|
| L9T5-D11 | revision X NOT ADMITTED; the supervisors revision V only; a lot of any other revision refused; the rev X qualification an UNSELECTED OPTION | record l9t5, `T10-ROUND5.md` section W133 (written by `apply_l4small_revx.py`), with authority, authority_why, ruled_by, ruled_on and reversed_by | as written there (the register's RE-8 M-B, or an owner item if revision V's supply becomes a money question) |
| L4E7-D1 | no presence-pair route is taken up; HO-G outside the baseline with nothing resting on it; the withdrawn B2 draft refuses the tree's generator always | record l4e7, `B2-PRESENCE.md` section 8, with the same fields | as written there |
| W133-D1 | the two decisions live in their records' own decision lists, not in `tools/pcb_decisions.yaml` | that file indexes the numbered decisions of `OWNER-DECISIONS-2026-09-11.md` and the rule-board pairs they hold (`decisions_render.py`, `test_decision_register.py`); neither decision is in that record or holds a pair; records l9t5 and l4e7 keep their SESSION decisions on their pages (L9T5-D1 to D10; B2-PRESENCE section 6); the rendered `OWNER-DECISIONS-OPEN.md` reads an `out/rule-audit` this worktree does not hold | add each as a numbered decision with a heading in the record and render the page where the rule audit is |
| W133-D2 | `apply_l4small_b2.py` and `apply_l4small_register.py` sit in this folder, not beside records l4e7 and l4e9 | L4-E9's generator refuses any `records/l4e*/apply_*.py` its change list does not name (`l4e9_power_path.py` lines 6687 to 6689; `test_l4e9.py` lines 233 to 247 and 1159; `test_l4e7.py` line 1104): beside those records they stopped `apply_l4e9_changelist_p0.py --check` (found by `test_w11l9t5`) | move them and add them to L4-E9's OUT_OF_BASELINE |
| W133-D3 | every edit to a page that keeps its history is an insertion (the old words stay, labelled), and no edit moves a line | record l9t5's pages are held to it (`test_w9l9t5`), the ledger and the register are cited by line, applied rows must stand once (`test_w24l4e9`: a replacement inside WP-22 failed it, so W130's words are inserted after it) | none needed |
| W133-D4 | CON-017's statement and acceptance stay as written (clause (5), revision V or X, is the erratum's bound, which revision V meets), and so do the Layer 1 to 3 pages that state that bound (`ARCHITECTURE.md` lines 622 and 1290, `ARCH-PCB-B-IOHA.md` line 176, the Layer 3 issue's acceptance); only the evidence pin of the compatibility page is rebound | narrowing the requirement would be a registry amendment the selection does not need (constitution section 1), and IOHA is the evidence of four requirements | restate clause (5) to revision V by a controlled amendment, the three pages with it |
| W133-D5 | R-208's two citations read their line numbers at apply time | set 32 moves the l8p reading from line 420 to 432; W130's numbers are main's | write the numbers by hand |
| W133-D6 | the change-list draft's docstring sentence on route B2 is left to record l4k's K-24 (`apply_l4k_changelist.py`) | both streams edited the same sentence and each script refused the other's result; K-24 already marks it as the text of `7070f106` | none needed |

## 3. The acceptances (the applied tree, `git grep` over v2 without `v2/release`, `v2/vendor`, the checks as received, `inputs/`, the integration records int*, patch files, the owner's instructions and this stream's own scripts)

- **L4A-60, no current instruction admits revision X.** Pattern: `V or X`, `0x2001`, `waits on V-B20`, `admitted only by V-B20`,
  `accepted only after the supplier's V-B20`, `until its own qualification`, `HELD on V-B20`, `rev X part's (qualification|V-B20|admission)`,
  `three rev X STM32H743VIT6`, `rev X (stays )?on V-B20`. 85 lines: 42 carry L9T5-D11 on the line; 13 have it within two lines
  (the compatibility page's F1 line 41, T10-ROUND5 55 and 206, the ledger 324 and 328, `l9t5_t10.py` 819, 820 and 1325 with the
  output's 434, 435 and 647, the restated test's two old literals); 10 state or quote CON-017 (5)'s bound (the registry 6443, the
  trace 986, the Layer 3 issue 404 and its digest, T10-ROUND5 22, the t10 generator 324 and 1821 with the output's 271 and 700,
  `test_l9t5` 655); 2 are labelled history or the decision's own reason (T10-ROUND5 52, round 6's "kept as written only as history,
  not an instruction", and 254, L9T5-D11's authority_why); 3 are the Layer 2 pages of W133-D4; 15 are history (LAYER-STATUS 540 and
  541, the K-26 quotes; the DESK-gate assessment 437 and its draft 336; `hc6-review.md` 17; the P0 list's draft 2 line 73; record
  l9t5's README 410, 451 and 463; the tests' literals of earlier text in test_recpack, test_w11l9t5 and test_w20oneliners).
  `test_l4small.t_no_current_instruction_admits_revision_x` holds this as a predicate (every such wording within 400 characters of
  L9T5-D11 unless it states CON-017 (5)'s bound or round 6's labelled history) and fails on the old text and on one label removed.
- **L4A-80, no selected, recommended or owner-request wording for B2.** Pattern: `waits on the/an owner`, `Decision asked`,
  `decision is asked`, `Recommendation`, `(recommended)`, `recommends adopting`, `Adopt the presence pair`, `B2 selected`,
  `selected by the coordinator`, `if the owner adopts`, `PROPOSAL until the owner`, `partial proposal` in any case, on lines naming
  B2 or the presence pair. 17 lines, none current: the DESK-gate assessment and its draft (the findings that list the old words),
  the P0 list's line 130 (the old heading at `4d0ff8a2`), record l9t5's README 182 and 401 (W9's labelled history), the change-list
  draft's docstring (record l4k's K-24 marks it) and its applied payload PY_EDITS (history), the tests' bad-word lists and the
  labelled docstring, and two unrelated "Recommendation" lines. `test_l4small.t_no_selected_recommended_or_owner_request_wording_for_b2`
  holds it as a predicate and fails on the old text.

## 4. Tests (verbatim totals from `tests/run.py`) and what set 33 owes

On the committed branch (the scripts unapplied, 05:00 CEST): test_l4small 10 passed, 0 failed, 0 skipped; test_w11l9t5 8 passed,
0 failed, 0 skipped; test_w9l9t5 11 passed; test_w4l4e7 9 passed; test_remeng 17 passed; test_lstat31 16 passed; test_recpack 7
passed; test_w15class 8 passed; test_w20oneliners 9 passed; test_w28q40 7 passed; test_applier_state 20 passed; test_l9t5 42 passed;
test_l4e9 64 passed (each 0 failed, 0 skipped); test_l4e7 64 passed, 0 failed, 1 skipped (L4E7_RECOMPUTE not set).

Applied in this worktree, uncommitted (all six scripts; `l9t5_t10.out`, `l4e7_p0sol.out` with the registry held at HEAD,
`l4e9_power_path.out` after `repin_l4e9.py`, `l9t5_connected.out` regenerated with `_bin/regen_out.py`): 37 of 46 modules
pass with 0 failed (the 13 above and test_w7rem 9, test_lstat32 13, test_dgate 19, test_dgate2 26, test_entrypage 16,
test_w17p0list 8, test_w23cite 8, test_w3annex 10, test_w8l5 6, test_w30entry 9, test_res31 18, test_l4e_svg_readers 2, test_w5l8p
5, test_test_procedures 14, test_w14l5 4, test_requirements 65 (1 skipped), test_l3r5 21, test_l3r4 15, test_candidate_guard 6,
test_l5r4 7, test_l8p 33, test_decision_register 3 (2 skipped), test_l4e9 64). Failed, with the cause:
- test_w13l4e9 7 passed, 2 failed and test_w24l4e9 9 passed, 2 failed: the first register script replaced text inside WP-22;
  CORRECTED (W133-D3): with the insertion, 9 passed, 0 failed and 11 passed, 0 failed.
- test_l3r2 25 passed, 2 failed: the Layer 3 issue's header prints the registry's digest; CORRECTED: the Layer 6 script now writes
  it, and `render_l3r2.py --check` then reads "3 page(s), 0 out of date" (`rules_render.py --requirements --check`: current).
- test_l3am 7 passed, 1 failed: it compares test files changed in the working tree (`git diff --name-only HEAD`) with the Layer 3
  amendment's list; an artefact of an uncommitted application, absent once set 33 commits (never "layer 3 amendment" in a subject).
- The dependency pass owed (outputs that pin a changed file and were not regenerated here): test_l5pwr 15/1, test_l7pwr 11/1,
  test_l8gnd 11/1, test_l8r2 37/3, test_l9t5 40/2 (`l9t5_case.out`, `l9t5_drafts.out`), test_l4e11 19/63 and test_l4e12 2/24 (their
  generators refuse the rebound registry until re-pinned). Pins found: `L4-POWER-ARCHITECTURE.md` by ten outputs,
  `pcb_requirements.yaml` by eight, the register by four, `PROCUREMENT.md` by `l5r2_interfaces.out`.
- test_l4e7: with the registry applied the cache KEY moves and the test began recomputing L4-E7's solver on this host; stopped
  after 12 minutes (exit 143). With the registry held at HEAD and every other script applied: 64 passed, 0 failed, 1 skipped.

**For the coordinator:** `apply_l4small_layer6.py` alone moves record l4e7's cache KEY (`pcb_requirements.yaml` is a whole-file
KEY input; set 32's typed boundary covers `l4e11_power.out` only), so it owes the L4-E7 recompute on a rented box: apply it in a set
that re-keys anyway, or after the boundary is extended to the registry entries the solver reads. The other five scripts leave the
KEY (checked: none of their files is a KEY input). Every script was checked on set 32's tip and with record l4k's five scripts in
either order: the same bytes. W130's correction 1 (paragraph 0a) is set 32's, not this stream's.

Constitution acknowledged (sections 3, 4, 5 and 8): text and decision tasks, each with its acceptance as a parsed predicate that
fails on the old text; no test changed to obtain green (test_w11l9t5's one restated expectation has its basis and a refused
mutant); no heavy run kept on this host.
