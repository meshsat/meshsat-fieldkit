# Verdicts invalidated on 26 September 2026: test-fixture output in the tree's evidence

MESHSAT-1357, review of 26 September 2026 (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`, section 1:
"Invalidate and regenerate evidence affected by the four contaminating fixtures. Fixing the tests prevents recurrence
but does not repair previously written verdicts."). Prototype design: nothing here is built or measured.

## How the invalidation works

`rules_status.py` reads the block at the end of this page and refuses every verdict file whose sha256 is listed,
wherever the file sits (`_verdicts`, `registers`). The invalidation therefore holds in every checkout that still
carries the file: the runner's gitignored copies, a box clone, a fresh worktree. Moving a file to an archive name is
done as well where this session may write; on the runner's main checkout the move is owed to the integrator (below),
and until it is made the content hash already keeps the file out of every reading.

## Method

1. The four fixtures named by the review, and what each writes when it runs from a directory with no `VERDICT_DIR`
   (the verdict goes to `out/` under the process's working directory, `v2/ecad/tools/verdict.py`, `write()`, the
   line `out_dir = out_dir or os.environ.get("VERDICT_DIR") or "out"`):

   | fixture | test (file:line at `1f614233`) | writes | signature | fixed in |
   |---|---|---|---|---|
   | F1 | `v2/ecad/tools/tests/test_board_gates.py:93` `t_a_zone_on_a_net_the_board_does_not_have_is_refused` | `check_zone_nets.verdict.json` | `inputs.board.path` = `zone.kicad_pcb`, FAIL | `2ba560ec` |
   | F2 | `v2/ecad/tools/tests/test_board_gates.py:112` `t_a_zone_on_a_real_net_passes` | `check_zone_nets.verdict.json` | `inputs.board.path` = `zone-ok.kicad_pcb`, PASS | `2ba560ec` |
   | F3 | `v2/ecad/tools/tests/test_finish_order.py:148` `t_routeflow_validate_agrees_with_these_rules` | `routeflow_validate.verdict.json` | `inputs.profile` = the last profile of the loop (`p.json`) | `2ba560ec` |
   | F4 | `v2/ecad/tools/tests/test_gate_fixtures.py:473` `t_a_blocked_code_can_name_the_land_it_is_wrong_on` | `lcsc_fill.verdict.json` | denominator 1, `inputs` empty | `82dd1e4d` |

   This scan found a fifth writer whose output was never removed: `v2/ecad/tools/tests/test_hardset.py:69`
   `t_a_broken_report_is_never_a_pass`, which wrote `hardset.verdict.json` with `inputs.drc.path` under
   `/tmp/hardset-test-*` until `1554a59c` (18 September 2026 20:16 CEST) gave it a directory of its own. The round-1
   review of the `2ba560ec`/`82dd1e4d` investigation (workstream W7) named a sixth, `test_energy_chain.py:298`
   (`cwd=TOOLS`): it runs the real chain on the real `pcb_energy_chain.yaml`, so its output is a real reading in a
   stray directory, not fixture data. An AST scan of every `subprocess` call in `tests/test_*.py` that starts a
   verdict-writing tool (35 calls whose own expression names no `VERDICT_DIR` or `--out-dir`) found each of the others given a
   temporary working directory, a `VERDICT_DIR` in the environment it builds, or an output beside a temporary input,
   except `test_rule_gate_mapping.py:98` and
   `:221`, which render the real tree by design and so write real readings, not fixture data.
2. Every `*.verdict.json` under `v2/` in the runner's main checkout at `1f614233` was read on 26 September 2026
   between 14:05 and 14:35 CEST: **855 files**, of which **790** sit where the readiness reads (`v2/ecad/out/` 75, `v2/ecad/pcb-*/out/`
   102, both gitignored; `v2/ecad/pcb-*/routed/` 613, tracked). Each was matched against the signatures above and
   against any recorded input path under a temporary directory. The same scan ran over the round-6 candidate trees
   (`wt/r4a`, `wt/r4b`, `wt/r6d`, `wt/r4t`) and the pending `wt/i1`, `wt/i3`: none carries a fixture signature.
3. Git history: every committed version of `check_zone_nets`, `lcsc_fill`, `routeflow_validate` and `hardset`
   verdicts, the `hardset-*` labelled ones included, was searched for the signatures and for a recorded input under
   `/tmp/`. **No fixture output was ever tracked.** The count first given here, 60 commits, was wrong; a checker
   counted 68 commits and 755 file versions, and the re-count of the third round reads 68 commits on all refs
   (`git log --all -- '*check_zone_nets*.verdict.json' '*lcsc_fill*.verdict.json' '*routeflow_validate*.verdict.json'
   '*hardset*.verdict.json'`) and 727 versions added or modified in them (`git show --name-only --diff-filter=AMR`
   per commit; the two counts differ by what each counts as a version). Neither search found a signature.

## Result: in the readiness read path (VERIFIED, file read)

| file (gitignored) | written | signature | fixture | rules it decides | action |
|---|---|---|---|---|---|
| `v2/ecad/out/hardset.verdict.json` | 2026-09-18T17:59:55Z, `tools.git_head` `2d88cb59bb7d` | `inputs.drc.path` `/tmp/hardset-test-tdl0deyh/bad.json`, INCONCLUSIVE of 0 | test_hardset.py:69, 16 minutes before its fix `1554a59c` | none (`rules: []`; the bare name `hardset` is no coverage verdict, `v2/ecad/tools/pcb_rules_coverage.yaml`) | invalidated by content; archive owed on main |
| `v2/ecad/out/routeflow_validate.verdict.json` | 2026-09-25T19:47:55Z, `4812f72c4491+dirty` | `inputs.profile` `p.json`, PASS of 20 | F3, 1 h 6 min before `2ba560ec` | none (`rules: []`) | invalidated by content; archive owed on main; real reading re-taken (below) |

Neither decided a rule, so **no readiness result moves** when they are refused: the audit before and after this
change reads 212 PASS, 41 FAIL and 80 INCONCLUSIVE of 333 pairs.

Previously present and already gone: a fixture `v2/ecad/out/lcsc_fill.verdict.json` (F4, `2026-09-25T20:32:57Z`,
PASS of 1, inputs `{}`), recorded in the round-1 results and chosen over the real readings of boards C and P for
CMP-002 and SUP-001 at that time. It is absent from the main checkout at `1f614233`; the real readings that replace it
were re-taken on 26 September 07:30Z during the order-set rebuild and are tracked at `29f00554`:
`v2/ecad/pcb-c-display-c8/routed/lcsc_fill.verdict.json` (PASS of 71), `v2/ecad/pcb-p-pack-p2/routed/lcsc_fill.verdict.json`
(FAIL of 23: F1 C4661 WRONG_MODEL), `v2/ecad/pcb-e5-block/routed/lcsc_fill.verdict.json` (PASS of 0).

## Result: outside the readiness read path (VERIFIED, file read)

`rules_status.py` reads only a board's phase directory `out/` and `routed/` and the set-level `v2/ecad/out/`
(`_project_dirs`). These files are not read by any readiness computation. They are listed in the register too, so a
copy moved into a read path is refused.

| file (gitignored) | written | signature |
|---|---|---|
| `v2/ecad/tools/out/hardset.verdict.json` | 2026-09-18T17:12:24Z | `/tmp/hardset-test-_k4rz_gv/bad.json` |
| `v2/ecad/tools/out/lcsc_fill.verdict.json` | 2026-09-21T16:09:31Z | F4: PASS of 1, inputs `{}` |
| `v2/ecad/tools/out/routeflow_validate.verdict.json` | 2026-09-21T16:09:29Z | F3: `p.json` |
| `v2/ecad/tools/tests/out/hardset.verdict.json` | 2026-09-16T12:40:13Z | `/tmp/hardset-test-iypyf8qy/bad.json` |
| `v2/ecad/tools/tests/out/lcsc_fill.verdict.json` | 2026-09-21T21:15:28Z | F4 |
| `v2/ecad/tools/tests/out/routeflow_validate.verdict.json` | 2026-09-21T21:15:26Z | F3 |

`v2/ecad/tools/out/` also holds 50 real readings taken by hand from the tools directory (16 to 21 September) and the
six `energy_chain*` readings of `test_energy_chain.py:298`; none is fixture data and none is read, so none is listed.

## Not fixture output, recorded because an input points into a temporary directory

`v2/ecad/pcb-c-display-c8/routed/doc_provenance_c.verdict.json`, `v2/ecad/pcb-e5-block/routed/doc_provenance_e5.verdict.json`
and `v2/ecad/pcb-p-pack-p2/routed/doc_provenance_p.verdict.json` (tracked, `29f00554`, 2026-09-26T07:30:39Z) name the
release folder of the order-rebuild worktree `wt/d41`. `diff -rq` of that folder against the main checkout's
`v2/release/revA` differs in one file only, `order/ROTATION-CHECKLIST.md`, which `faf8c981` re-rendered afterwards.
They are real readings of another checkout, not fixture output, and are not invalidated. Their evidence class is
AWAITING_REVALIDATION (cause TEMP_INPUT) until re-taken in this tree.

## Re-taken

- `routeflow_validate`: re-taken for all six profiles on the runner at 2026-09-26T12:34:57Z to 12:34:59Z from
  `tools.git_head` `1f614233998c`, writer `routeflow.py` sha16 `48d635a821b6e751`, each into its own scratch
  directory: a 20/20, b 20/20, c 23/23, d 20/20, e 20/20, p 20/20, all PASS. It decides no rule and one file name
  cannot hold six profiles, so the readings are not placed in `v2/ecad/out/`; the absence there is the correct state.
- `hardset`: nothing to re-take. The labelled readings the rules read (`hardset-placed`, `hardset-routed-board-gate`)
  are written by the finish chain; a bare `hardset` verdict at set level has no legitimate writer.
- `check_zone_nets` (F1, F2): no contaminated copy exists in this tree (the fixtures skip without pcbnew on the runner;
  the incident of `2ba560ec` was in a box clone). Nothing to re-take.
- `lcsc_fill` (F4): re-taken on 26 September 07:30Z for C24, P4 and E5 (above). Boards A, B, D and E have no order
  folder at their declared phase, so there is no BOM to read and the rules stay INCONCLUSIVE with that reason.

## Owed, outside this stream's files

- **Integrator, on the runner's main checkout:** move the two read-path files to archive names so no reader globs
  them (the content hash already refuses them):
  `mv v2/ecad/out/hardset.verdict.json v2/ecad/out/hardset.INVALIDATED-2026-09-26.json` and
  `mv v2/ecad/out/routeflow_validate.verdict.json v2/ecad/out/routeflow_validate.INVALIDATED-2026-09-26.json`
  (and the six under `v2/ecad/tools/out/` and `v2/ecad/tools/tests/out/` the same way). This stream's worktree
  holds copies and has moved them.
- **Tests owner:** `v2/ecad/tools/tests/run.py:73` compares `before.get(n, v) != v`, so a verdict a run CREATES is
  never flagged; only one it changes is. That is how F3 and F4 wrote new files unseen (round-1 finding W7-F5). The
  guard also watches only `v2/ecad/out/`, not a phase directory's `out/` or `tools/out/`.

<!-- evidence-register: invalidated -->
```yaml
invalidated:
  - path: v2/ecad/out/hardset.verdict.json
    sha256: 60c9b17b89da183945eac848f03b0ab7174422e43f6123c3a6bd12c4d3e748bc
    fixture: tests/test_hardset.py:69 t_a_broken_report_is_never_a_pass, before 1554a59c
  - path: v2/ecad/out/routeflow_validate.verdict.json
    sha256: 61cf4faa6de71f0a4fec15dc522f0289bcbf8a446a64c048c4510de481e7ba1f
    fixture: tests/test_finish_order.py:148 t_routeflow_validate_agrees_with_these_rules, before 2ba560ec
  - path: v2/ecad/tools/out/hardset.verdict.json
    sha256: f208f87ccf8780223c058bda26d5febec255bff3c3ace4a66f6a097796d700a8
    fixture: tests/test_hardset.py:69, before 1554a59c
  - path: v2/ecad/tools/out/lcsc_fill.verdict.json
    sha256: e8a0a657f6151807d92c0b225f62173e25a4948443680e4d87224924391ce714
    fixture: tests/test_gate_fixtures.py:473, before 82dd1e4d
  - path: v2/ecad/tools/out/routeflow_validate.verdict.json
    sha256: cead1c15da7ed3bf95f4c6cf812ed326d0d0ad11f567a16f248a37415c64588c
    fixture: tests/test_finish_order.py:148, before 2ba560ec
  - path: v2/ecad/tools/tests/out/hardset.verdict.json
    sha256: 472cc65a8398e2a7cdb4eb645ee4717e0dc330516542bed6a7f18d4777e2e6d9
    fixture: tests/test_hardset.py:69, before 1554a59c
  - path: v2/ecad/tools/tests/out/lcsc_fill.verdict.json
    sha256: 72298d8a4b1816377949dadc20e3f1d30b1978b24444f13a8d516650e7f2f674
    fixture: tests/test_gate_fixtures.py:473, before 82dd1e4d
  - path: v2/ecad/tools/tests/out/routeflow_validate.verdict.json
    sha256: 593517f3eb1c4c510293f0daa372ff70206deead8fb76a999f3257f39373e009
    fixture: tests/test_finish_order.py:148, before 2ba560ec
```
