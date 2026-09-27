# MeshSat Field Kit engineering red-team review

**Pack:** `meshsat-fieldkit-code-2026-09-15.zip`  
**Review date:** 15 September 2026  
**Scope:** efficiency, architecture, correctness, maintainability, reproducibility, failure semantics, observability, and agentic-system fitness. This is not a security assessment.

## Executive summary

The 15 September pack is a substantial engineering improvement over the 10 and 12 September packs. The control plane is now explicit, the current hard-DRC policy is centralized, the route supervisor propagates attempt failures, the agent has a typed knob registry, one-variable experiments are enforced, tool fingerprints are runner-generated, historical evidence ledgers are verified before use, patch regressions are checked on the red and green sides, placement runs have an implementation, and arm boards are retained.

However, I would **not enable autonomous promotion or release** yet. Three decision-boundary defects can still turn incomplete or invalid evidence into a green result:

1. `final_gate.py` can return PASS while parts certification is open, quote-only boards remain held, or an expected board folder is absent.
2. `agent/loop.py` can accept a partial result set after a runner failure and can return PASS for an all-ILLEGAL experiment set.
3. The Freerouting quality programme still ranks and gates evidence measured under the obsolete six-type DRC basis. Every shipped baseline is six-type, and all **233 stored rows with metrics** are six-type.

The system is well designed at the conceptual level, but its last remaining weakness is exactly where an agentic system is most sensitive: **the transition from evidence to decision**.

My current readiness estimate is:

| Use | Readiness | Assessment |
|---|---:|---|
| Human-supervised proposal generation | **85–90%** | Useful now; mechanical validation is materially stronger. |
| Controlled parallel experiments | **70–80%** | Useful with an operator checking completeness and experiment scope. |
| Unattended design iteration | **60–70%** | Too much risk of partial or mis-scoped evidence being accepted. |
| Autonomous artifact promotion | **35–45%** | Not ready because final release truth is not fail-closed. |

These percentages are engineering estimates, not measured reliability statistics.

## Review method

- Inventoried 391 archive entries: 234 Python files, 45 shell files, 69 JSON files, and 11 Markdown files.
- Parsed all 234 Python files with Python's AST parser: **0 syntax failures**.
- Parsed all 45 shell files with `bash -n`: **0 syntax failures**.
- Compared the implementation against the 12 September pack and its prior findings.
- Traced the deterministic runner, agent proposal/validation/runner/judge/reviewer loop, ledgers, artifact retention, quality benchmark, shared pre-route/finish chains, and final release gate.
- Inspected the 62 Python test files: 476 `t_*` test functions are present in this archive; 32 test files use source-text assertions.
- Did **not execute project code, KiCad, routers, generators, or the project test suite**. This is a static engineering review.

## Priority findings

| Priority | Confidence | Finding | Engineering impact |
|---|---:|---|---|
| **P0** | **99%** | `final_gate.py` does not make parts certification authoritative. It records `rc_j` at line 75 and prints it at lines 85–87, but the returned verdict at lines 93–97 depends only on deliverable failures and contracts. | The final gate can report PASS while `jlc_certify.py` is OPEN. A release aggregator that is greener than one of its component gates is not a release gate. |
| **P0** | **99%** | Quote-only and missing boards do not block `final_gate.py`. Quote folders are counted as held at lines 83–87 but are ignored by the PASS condition. `newest_folders()` returns only folders that exist, and neither default mode nor `--boards` compares the discovered set with the required set. | A held board or absent deliverable can disappear from the denominator and the board set can still read PASS. This contradicts the file's own claim that a folder cannot pass by being forgotten. |
| **P0** | **99%** | The agent loop can accept a partial or failed cycle. `run_spec()` returns the runner exit code, but lines 199–207 proceed whenever at least one matching row exists. There is no requirement for exactly one row per requested arm, no duplicate check, and no refusal on non-zero `rc`. | If one of eight arms writes a row and the runner then fails, the cycle can be drafted, reviewed, and returned as PASS using one-eighth of the requested evidence. Python exposes `CompletedProcess.returncode` and `check_returncode()` specifically so the caller can distinguish this state. |
| **P0** | **99%** | `agent/loop.py` can return PASS for an all-ILLEGAL result set. Lines 281–296 treat INFRA_FAIL, UNMEASURED, and UNMEASURABLE as bad, but omit ILLEGAL. The runner's aggregate correctly fails when no legal row exists; the loop ignores that runner status when rows exist. | The outer control plane can invert the deterministic runner's decision. This is the exact boundary an agent must never be allowed to soften. |
| **P0/P1** | **99%** | The quality programme is still based on obsolete six-type DRC evidence. `routeflow/bench/baseline.json` contains six baselines with `hard_types_checked: 6`. Of 236 stored result rows, 233 carry metrics and every one says six types. `bench_report.py:20–32` identifies the issue, but `bench_compare.py:27–37` still ranks the rows, and the Stage 4 promotion logic at `bench_report.py:60–86` does not exclude `six_type`. | A router configuration or Freerouting version can be promoted using boards that were never judged by the current 15-type hard set. The report's asterisk is disclosure, not a gate. |
| **P1** | **99%** | Agent evidence is not scoped to the experiment context. `evidence.pack()` loads all rows from every supplied ledger and computes `best_pairs`, `worst_pairs`, summaries, and repeat signatures across them without filtering by letter, board, stage, placed-board hash, tool fingerprint, or DRC-policy version (`agent/evidence.py:114–142`). | A result from another board or another tool basis can raise the claimed “best on this board,” refuse a valid proposal as a repeat, or force an impossible prediction. Scientifically different populations are merged into one cohort. |
| **P1** | **99%** | Placement support is implemented but not plumbed into evidence selection. `agent/loop.py:160–173` loads the template, then calls `evidence.pack()` without `spec_template=template`; evidence therefore defaults to the pair stage. | A placement template can validate and run manually, but the proposer will not be shown the five placement knobs. The advertised architecture and the actual proposal surface disagree. |
| **P1** | **98%** | `arms.run_arm()` ignores every `pair_preroute.py` return code (`arms.py:137–156`). A missing summary is converted into `pairs=0, of=0`, not a process failure. | A usage error, validation failure, crash, or killed pass can become a measured MISSED/MET row if enough expected text was printed. Exit code 1 is a documented partial-routing result here, so the fix is not simply `check=True`: the runner needs a closed exit-status contract and must require one valid summary per pass. |
| **P1** | **98%** | `_drc_of()` ignores the `hardset.py` return code and does not remove the old counts file before running it (`arms.py:196–215`). | If hardset fails while a same-named count file exists, an old hard/unrouted count can be accepted for a new board. This is especially likely during repeats or reused output directories. |
| **P1** | **99%** | Retained experiment artifacts are mutable by name. Logs, DRC files, counts, and kept boards use `arm-<name>` paths (`arms.py:124–203`). Names are not required to be unique across cycles, and `--allow-repeat` explicitly permits replay. | A later cycle can overwrite the board and reports referenced by an earlier ledger row. The ledger retains a hash, but the evidence bytes needed to inspect that row no longer exist under that identity. |
| **P1** | **98%** | The placed-board DRC in `full.sh` fails open for execution. Line 124 explicitly swallows `drc.sh` failure; lines 136–138 print UNMEASURED and then continue into the expensive pair and fanout stages. | An infrastructure failure defeats the intended cheap-before-expensive gate, wastes routing time, and allows a design run whose baseline legality was never established. |
| **P1** | **98%** | `ledger.append()` is a check-then-append sequence without a lock (`ledger.py:58–68`). Multiple agent processes can read the same head and append rows with the same sequence and previous hash. | Concurrent cycles can break the chain or create ambiguous ordering. A system explicitly designed for parallel width needs a concurrency-safe evidence store. Python's documented `fcntl.flock()` supports an exclusive lock for this purpose. |
| **P1** | **98%** | The routeflow experiment's project lock remains check-then-write (`routeflow.py:677–688`). | Two experiments can both observe no live lock holder and then overwrite the same pre-route board and `out/par/exp-*` directories. This is a previously identified architectural defect that remains open. |
| **P2** | **99%** | The new DRC cost measurement never executes. `drc.sh` exits at line 45; the timer/report block is at lines 47–59. | The intended evidence for reducing the twelve DRC calls in `finish.sh` is never produced, so the pipeline cannot quantify one of its clearest optimization targets. |
| **P2** | **99%** | The schema accepts prediction value `0`, but `arms.py:278–284` rejects it through a truthiness check. | A legitimate prediction such as exactly zero or at most zero is accepted by one contract layer and refused by the next. Use key/type presence, not truthiness. |
| **P2 architecture** | **97%** | `pair_preroute.py` remains a 236 KB module whose `main()` spans roughly 1,970 lines. | The central algorithm is difficult to unit-test, profile, reason about, or safely mutate. The extracted `pairsearch.py` is a good start, but orchestration, occupancy, geometry, scoring, rollback, matching, and reporting remain fused. |
| **P2 tests** | **98%** | Many important tests prove token presence instead of behavior. For example, `test_final_gate.py` checks that strings such as `newest_folders`, `QUOTE`, and `INCONCLUSIVE` exist but never executes the decision matrix. Overall, 32 of 62 test files use source-text assertions. | The suite can stay green while the final boolean is wrong, which is exactly what happened in `final_gate.py`. Structural tests are useful for architectural pins, but decision code needs executable truth-table fixtures. |

## Earlier findings: current status

| Earlier finding | 15 September status | Notes |
|---|---|---|
| One hard-DRC definition | **Current code fixed; evidence migration incomplete** | Current consumers import `hardset`, but benchmark baselines and all metric-bearing stored rows still use six types. |
| Pair negotiator masks final lay status | **Fixed** | `pair_negotiate.py:72–79` now returns the laying process status and refuses a missing summary. |
| Route supervisor masks background failures | **Fixed for the production route path** | `route_parallel.sh:12–27` tracks each PID and returns non-zero when attempts fail; routeflow distinguishes no-score infrastructure failure. |
| Reused route directories/logs | **Fixed** | Routeflow creates a fresh timestamped run directory and records resolved configuration/provenance. |
| Unbounded finish waits | **Fixed** | The shared finish has a deadline. |
| Stale netlist accepted after failed export | **Fixed** | `full.sh` removes the old netlist, checks the schematic build status, and requires a new non-empty netlist. |
| Pair-grid class-global cache | **Fixed** | Cache ownership was moved away from the previous unsafe global form. |
| One-variable experiment contract | **Fixed** | `_max_knobs` defaults to one and is mechanically enforced. |
| Prediction metric ignored | **Fixed** | The schema requires the template's closed metric. |
| Broad source-derived knob allowlist | **Fixed** | `agent/knobs.json` is now authoritative and typed; source scanning is used as a completeness check. |
| Missing tool/source fingerprint | **Fixed for new arm rows** | The runner computes a tools-tree fingerprint. Context filtering still needs to use it. |
| Historical ledger consumed without verification | **Fixed for evidence packs** | `graded_rows()` verifies each supplied ledger before reading it. The current-cycle result ledger still needs before/after verification. |
| Patch test not proved red before fix | **Fixed** | `agent/patch.py` applies test hunks to the baseline and requires the named selector to fail before the patch and pass after it. |
| Placement schema without runner implementation | **Runner fixed; proposer plumbing incomplete** | `arms.py` implements placement runs, but the loop does not pass the template into evidence selection. |
| Winning arm artifacts deleted | **Partly fixed** | Boards are kept, but name-based paths allow later cycles to overwrite them. |
| Experiment lock race | **Open** | The routeflow experiment project lock is still check-then-write. |

## Strong architecture recommendation

Keep the agent outside PCB truth. The model should propose hypotheses and explain results; deterministic code should own execution, grading, eligibility, promotion, and release.

### 1. Make a cycle a first-class immutable object

Create a `cycle_id` before proposal and carry it through every arm, process, row, verdict, log, board, and review. An arm result is accepted only when all of these match the cycle declaration:

- exact `cycle_id` and `experiment_id`;
- exact board and stage;
- exact placed-board SHA-256;
- exact tool-tree and runner SHA-256;
- exact knob-registry and hardset-policy SHA-256;
- exactly one terminal result per requested arm;
- a runner-level terminal status of COMPLETE;
- every expected artifact present and hashable.

Do not correlate current-cycle rows by model-chosen arm name and sequence horizon alone.

### 2. Replace shared JSONL decision state with a transactional experiment store

For one machine, SQLite in WAL mode is enough and is simpler than building concurrency control around several JSONL files. A minimal model is:

```text
cycle(cycle_id, board_id, stage, context_hash, requested_arms, status)
arm(experiment_id, cycle_id, name, knobs_json, prediction_json, status)
artifact(sha256, experiment_id, role, immutable_path, size)
metric(experiment_id, metric, value, denominator, policy_version)
review(cycle_id, model, verdict, findings_json)
promotion(candidate_sha256, gate_set_version, status, promoted_at)
```

Use foreign keys and unique constraints to make partial and duplicate rows impossible to mistake for a complete cycle. Export signed/chained JSONL from the database for portability if desired; do not use an unlocked append file as the concurrent source of truth.

### 3. Define one stage-result contract

Every executable stage should return and persist the same machine-readable envelope:

```text
StageResult
  cycle_id
  stage
  status: PASS | FAIL | INCONCLUSIVE | INFRA_FAIL
  exit_code
  started_at
  finished_at
  input_artifact_hashes
  output_artifact_hashes
  tool_fingerprint
  policy_fingerprint
  metrics
  denominator
  diagnostics
```

Stdout remains diagnostic only. A supervisor must never reconstruct truth from a marker if it launched the producer and can read this result directly.

### 4. Version evidence eligibility, not only code

Define an `experiment_context_hash` over:

```text
board identity
+ placed-board SHA-256
+ tool-tree SHA-256
+ pair-runner SHA-256
+ knob-registry SHA-256
+ hardset-policy SHA-256
+ KiCad version
+ router/JAR SHA-256
+ pass definitions
+ resolved environment
```

Best/worst values, repeat detection, Pareto ranking, and promotion must operate only inside one compatible context. A policy change should make old evidence ineligible automatically. Historical six-type rows can remain in the record, but cannot enter a current 15-type decision.

### 5. Make final promotion a closed deterministic state machine

The release gate should require an exact board manifest, not discover whatever happens to exist:

```text
EXPECTED BOARDS PRESENT
AND no quote-only/held board
AND every verify_deliverable PASS
AND contracts PASS
AND parts certification PASS
AND current DRC-policy fingerprint
AND current artifact hashes
= PROMOTABLE
```

Any missing or unjudgeable input is INCONCLUSIVE; any component failure is FAIL. The agent may recommend promotion but must not change this result.

### 6. Store artifacts by content, then attach friendly names

Keep boards, DRC reports, logs, metrics, and resolved specs beneath a cycle directory or content-addressed path. Never overwrite an artifact referenced by an evidence row. A friendly `latest` pointer may move; evidence paths may not.

### 7. Split the pair router at measurable boundaries

Refactor `pair_preroute.main()` incrementally, preserving behavior:

```text
pair_router/
  config.py
  board_model.py
  occupancy.py
  stations.py
  search.py
  legs.py
  matching.py
  rollback.py
  metrics.py
  runner.py
```

The immediate objective is not fewer files. It is separable timing, deterministic fixtures, and independent tests for occupancy generation, candidate selection, legality, rollback, and reporting.

### 8. Shift test effort toward decision truth tables

Keep source-scanning tests for architectural rules such as “no gate imports the agent” or execution-path pins. For decision code, add executable fixtures covering every state combination. At minimum:

- final gate: missing board, quote-only board, deliverable fail, contracts inconclusive/fail, certification fail, all pass;
- agent loop: runner non-zero with zero/some/all rows, duplicate row, wrong cycle, all ILLEGAL, mixed legal/illegal, broken result ledger;
- evidence: two boards, two stages, two placed hashes, two tool fingerprints, and old/new hardset policies in one ledger;
- arms: expected partial exit, unexpected process failure, missing summary, hardset failure with stale counts present, repeated arm names.

Mutation tests should change the final boolean or status transition, not only remove a source token.

## Efficiency recommendations

The code is now capable of wide parallel search, so correctness of accounting is higher leverage than another routing heuristic. After the P0/P1 items are fixed:

1. Repair `drc.sh` timing so the system measures actual DRC cost.
2. Key a DRC result cache by board SHA-256, matching project-file SHA-256, KiCad version, DRC invocation, and policy version. Reuse only exact matches.
3. Replace whole-project `copytree` per arm with a declared minimal input set or filesystem reflinks where available; continue isolating mutable board files.
4. Record CPU time, peak RSS, I/O bytes, and per-stage wall time in `StageResult`, then optimize the top measured consumer.
5. Decompose `pair_preroute` before making more algorithmic changes so occupancy, stub search, corridor search, and stamping can be profiled and changed independently.
6. Keep Pareto results over legality, unrouted count, pair completion, pair skew, vias, track length, DC drop, impedance deviation, and wall/resource cost. Do not collapse hard legality constraints into a soft scalar score.

## Expected effect after remediation

Probability-weighted engineering estimate:

| Outcome after P0/P1 remediation | Estimate |
|---|---:|
| Agent cycles that are reproducible and scientifically comparable | **85–92% probability** |
| Useful iteration throughput versus operator-driven serial work | **2–4×** on a suitably sized runner |
| Human supervision time reduction | **60–80%** |
| Measurable PCB-quality improvement from broader search | **60–70% probability of 10–25% improvement in exposed metrics** |
| Dramatic quality improvement above 40% without richer objectives | **Below 10% probability** |

The fastest safe path is therefore:

1. Fix `final_gate.py` truth semantics and add behavioral decision fixtures.
2. Make cycle completeness, runner status, and ILLEGAL results authoritative in `agent/loop.py`.
3. Quarantine every six-type benchmark and regenerate the six baselines under the current policy.
4. Introduce an immutable cycle/context identity and scope all evidence to it.
5. Make ledgers and experiment locks concurrency-safe.
6. Repair DRC timing, profile the real pipeline, then optimize measured hotspots.
7. Refactor `pair_preroute` by measurable boundaries.

Until steps 1–4 are complete, keep the agent at **proposal + supervised experimentation**, with no autonomous promotion.

## Official behavior cross-checks

- Python documents that `subprocess.run()` returns a `CompletedProcess`, whose `returncode` is the child status, and that `check=True` / `check_returncode()` makes a non-zero status explicit: <https://docs.python.org/3/library/subprocess.html>
- Python documents `fcntl.flock()` and the `LOCK_EX` / `LOCK_NB` locking operations suitable for serializing a file-backed append or claim: <https://docs.python.org/3/library/fcntl.html>
- KiCad documents `pcb drc`, JSON report output, and that violation-specific exit code 5 applies only with `--exit-code-violations`: <https://docs.kicad.org/master/en/cli/cli.html#pcb-drc>
- GNU Bash documents `set`, `errexit`, pipelines, and `pipefail`; `set -uo pipefail` does not by itself stop a script after an ordinary failed command: <https://www.gnu.org/software/bash/manual/bash.html#The-Set-Builtin>

## Bottom line

This is no longer an ad-hoc shell collection with an agent bolted on. It is becoming a real experimental control plane. The architecture is moving in the right direction, and most of the 12 September agent-contract defects were addressed thoughtfully.

The remaining work is not more agent capability. It is making **completion, cohort identity, legality, and release truth impossible to misstate**. Once those four boundaries are deterministic and fail-closed, the system should make PCB iteration materially faster and can plausibly improve the boards through broader, better-accounted search.
