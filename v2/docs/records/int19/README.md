# Integration set 18 (MESHSAT-1357, branch `fnd/int19`, 30 September 2026): the Layer 3 closure

Prototype design: nothing is bought, built or measured. The integrating session's records for set 18, from main
`6582bd41`. Layer 3's requirements completion is kept apart from circuit, PCB, thermal, runtime and product
verification (D-28, D-29).

| Step | Commit | What it did |
|---|---|---|
| 1 | `faf3a67b` | merge of `fnd/l3feas` at `c11b99d3`: the Layer 3 feasibility record (CHECK-2 accepted) |
| 2 | `5edb03c8` | merge of `fnd/l3batt` at `63897fc3`: the runtime-and-battery comparison and the illustrative tablet service budget (CHECK-3 accepted) |
| 3 | `302fff6d` | merge of `fnd/l3r5` at `72fec7fd`: the closure pass on the owner's clarifications D-26 to D-37 |
| 4 | `020669a7` | merge of `fnd/l3r5` at `c183c086`: the first fix round on the engineering collaborator's closure check (B1 to B3, M1; D-38) |
| 5 | `b3b0a0ad` | merge of `fnd/l3r5` at `d08929ea`: the second fix round (B2 held to the rulings structurally, the owner's clarification of history against current status), D-22 carried into REQ-072's acceptance, D-39 (the owner's conditional authorisation) and check 3 |
| 6 | this commit | `apply_rebind_page_set18.py`: CON-010 and REQ-044 rebound to the evidence page the set renders (`85256b70`, stable over two full render orders; FEA-008 is its change), `dryrun.out` regenerated (its only change is the validator's warning count, 2 to 0, on each chain: the two warnings were these bindings) |

**The closure's checks, attributed.** The engineering collaborator (Astra, `gpt-6-astra` at `xhigh`, read-only)
checked the closure twice, the owner's allowance of one assessment and one targeted follow-up: check 1 (`72fec7fd`)
and check 2 (`c183c086`) read NOT ACCEPTED; check 2 accepted B1, B3 and M1. Check 3 is Claude's (the coordinating
session's) verification of B2's final correction and D-22's trace at `a66c4e5b`, by its own check `verify_b2.py` and
the targeted tests; it is not a model review and not an Astra check, and Astra never examined those revisions. All
three are in `../l3r5/checks/`. M2 (a citation of `CODEX-WORKER.md` section 7) closes here: main carries that section.

**Acceptance.** D-39 authorises the baseline's acceptance once the gates pass and is not itself evidence that they
did. The acceptance is its own record (`baseline_acceptance` in `handover/layer3/l3r2.yaml`, `../l3r5/apply_l3r5_accept.py`),
filed against the promoted revision after this set's clean-clone check and box suite pass; the results are added
below when they exist.

## The gates on the candidate `b4b199d0`

- **Validators:** `rules_lib` 145 requirement records, 0 errors, 0 warnings; 59 rules, 0 errors; `render_l3r2` 3 pages
  current; `reissue.py --check` and `--map --check` current; `rules_render` 16 documents current and the trace current;
  `decisions_render --check` current; the full render order reaches the same evidence page (`85256b70`) twice after the
  commit, 0 tracked files changed.
- **The merge, verified mechanically by the coordinator** (no reviewer agent: the owner's list for this set names none
  and asks for no further reviews): the files of each stream equal its tip (`c11b99d3`, `63897fc3`, `d08929ea`); main's
  own files (the Codex worker notes, the execution plan, the H3-R1 release, the hygiene test) equal main `6582bd41`;
  the only set-specific changes are the two page bindings and the pages they re-render; main is an ancestor, so the
  promotion is a fast-forward.
- **A clone holding only the candidate branch** (`--no-local --single-branch`), the evidence archive installed (950
  files, sha256/16 `67fc5dbc3fc6b9bc`): every merge present; the full render order 0 changed, the page stable twice;
  validators 0 errors 0 warnings; the dry run reproduced byte for byte; `verify_b2.py` 0 findings, its fixtures as
  required; `test_requirements`, `test_l3r2`, `test_l3r4`, `test_l3r5` and `test_public_hygiene` 132 passed, 0 failed.
- **The full suite on the rented box** at the exact commit, 22:31:36 to 23:06:24 CEST: 2369 passed, 0 failed, 3 skipped
  (host properties: a path pinned by a routing profile exists there, no numba, pcbnew importable), EXIT 0, no tracked
  file changed. Judged by the coordinator's promotion gate on the log, never by a wrapper's exit code (a shell line
  ending in `echo` exits 0 whatever the runner returned): the log names the candidate, its last EXIT reads 0, the totals
  read 0 failed and match the result lines, no module failed to load, and 200 of 200 test modules of the candidate's tree
  produced results, `test_public_hygiene` among them (4 tests). The gate was shown to fail on controlled copies of a
  real log (EXIT 1, one failing test, the hygiene module removed with consistent totals, a load failure, another
  commit). A defect of the runner is recorded, not needed for promotion: `run.py`'s name filter reports success when a
  named module is absent (0 tests run from it); the box suite runs unfiltered.
- **Promoted** by fast-forward: main at `b4b199d0`, pushed, mirror synced.

## After promotion: the acceptance guards, then the acceptance

The coordinator's acceptance-guard check (`../l3r5/checks/verify_acceptance.py`, expected outcomes written as literals
from the closure criteria) found the acceptance script would file a record with a gate condition unmet (the status
level stayed DRAFTED, but no acceptance record may exist while a criterion is unmet). The script now refuses unless the
gate's five conditions read MET; `t_l3r5_acceptance_refused_while_a_criterion_is_unmet` fails on the old script and
passes on the new; the check that the gate never reads MET with a row unsettled gains a fixture (D-35 removed); the
tests that read the tree's acceptance state now hold before and after the record. The check reads 11 of 11 on main
before the acceptance. Then `baseline_acceptance` is filed against `b4b199d0` under D-39 with this record and the three
checks as its evidence, the pages rendered, and LAYER-STATUS's layer 3 brought to it.
