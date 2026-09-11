# The control plane: the programme, and what the estate already provides (MESHSAT-862)

Written 11 September 2026. **This document exists because the plan it replaces lived in
`~/.claude/plans/` and was overwritten three times.** A plan an owner ruling depends on belongs in the
repository. `CLAUDE.md` points here now, not at a filename that gets recycled.

## Why

Two engineering red teams reviewed the code pack on 10 September and the answer pack the same evening.
Owner ruling about 17:00 that day: **everything, in the red teams' order**, board work frozen. Owner
ruling 11 September: **plumbing first, then the boards**, after round two showed that an agent plumbed
onto today's channels "makes the same wrong calls faster and journals them clean".

Round two's own arithmetic is why the order is what it is. Per-iteration wall 3x to 5x and usable
experiments per compute-hour 4x to 5x come from **code and gating**; the agent's own increment is 1.3x
to 2x; **design quality does not move with the loop at all**. What the loop adds is width of search, and
width pays only against an objective that is already trustworthy.

## Where the nine stages stand (measured 11 September)

| stage | state |
|---|---|
| 1 verdict integrity, 2 run semantics, 3 schematic engine, 4 per-pass session, 5 pair kernel | done |
| 6 negotiated router | **obsolete**: built, measured on four schedules, rejected (22 to 25 of 113 against greedy 56, appendix 32.103) |
| 7 orchestration | **half**: `full_*.sh` 21 to 7, `finish_*.sh` 31 to 15; **7 tools write a verdict JSON, 18 gates do not**; 13 unbounded `grep` waits |
| 8 gate tests and shared constants | **part**: 6 test files, no per-gate fixtures, no `design_<x>.py`, no `appendix_check.py` |
| 9 solver and leftovers | **mostly**: `PAIR_BUDGET` 0, `impedance_2d` wired, `dc_drop` documents its solver |

Two P0s raised by the static review of the answer pack were already closed before it was written:
`f4c754e` landed 32 minutes after the reviewed pack was cut, `test_hardset` now reads every text file
rather than `.py` only, and the two finishes named as evidence no longer exist.

## The packaging question, settled by fact

Round two says the pipeline should stop reimplementing a control plane and honour Territory Grounder's
contracts, leaving open whether it runs inside TG or beside it. **It runs beside it, and this is not a
preference: TG has no job-submission API.** Its write surface is deliberately narrow; every mutating
governance route requires an operator session, and the only machine-writable routes are an ingest push
and a session replay. A machine principal cannot vote or change the mode.

So: **copy the formats, not the control plane.** Four are fully specified as data and are what this
pipeline adopts.

| what | where it is specified | what we do |
|---|---|---|
| job spec | TG `core/actuate/opschema/opschema.json`, Go type at `opschema.go:143-192` | our stage catalogue takes its shape: op class, params with types, a fixed argv template, a safety tier from a closed set, a rollback template |
| action identity | TG `core/manifest/manifest.go:66-79` | `action_id = SHA-256(canonical JSON of {target, op_class, params, reversible})`, refusing to hash invalid UTF-8 |
| ledger row | TG `core/audit/ledger.go:85-105`, DDL `0003`, REVOKE `0015`, witness `0092` | length-prefixed fields, `prev_hash` chained, and a periodic external witness of the head |
| prediction and verdict rows | TG `0002_infragraph_prediction`, `0004`, `0042`; finops-agora `schema.sql:35-53` and `:85-95` | identity columns written once at commit; only the verifier writes scores |

**The one nuance worth repeating:** in TG the never-auto floor sits *above* the posture check, so a
floor-class operation is refused identically in Shadow and in Full-auto. Mirror that order, not the
older prose that puts the mode check first.

## What we take from finops-agora, ranked

1. **A CI-enforced pin on which files may touch the actuator.** `agora/validation/execution_paths.py`
   is about 65 lines: a pinned allowlist of call sites, a tree scan, and a gate that fails when the
   real set differs from the pin. It exists because an evidence string had falsely claimed a "sole
   authority" that the code did not have. **This is the single highest value-per-line idea for us**:
   the analogue is a pin on which files may write a gerber, a BOM or an order set.
2. **Make it schema-impossible to act without a committed prediction.** Their `fk_order_pred` foreign
   key means an order cannot be inserted without a prediction row. Our analogue is that an experiment
   row cannot exist without a `predict: {metric, op, value, basis}`.
3. **A plan that was never executed cannot become counted evidence**
   (`eval_population.executed_evidence_population()`). Our exact trap: a board that passed its gates
   but was never routed or built must not enter the evidence cohort. **155 of 191 benchmark rows were
   INELIGIBLE for precisely this reason** when the benchmark was regraded.
4. **A standing envelope instead of per-action approval**: caps declared once, every cap positive or
   the envelope is refused, an empty allowlist means deny-all rather than permit-all, and
   `approved_by` recorded. Their note is that a human gate nobody answers is a liveness hazard.
5. **A kill switch that is file-authoritative, needs a written reason to clear, and has at least one
   condition that trips regardless of any configured threshold.**
6. **A daily chained Merkle root over the append-only tables with an off-database witness** — and
   write the verifier they admit they did not.

## What claude-gateway would give us, and what it would cost

It is a working control plane, not a document: session dispatch with PID supervision and resume, a 30
second cooldown, per-slot concurrency locks with a race-safe atomic claim, a dropped-work requeue with
attempt and age caps, a progress feed, a token and cost tripwire with kill authority, a memory cap per
session, a three-band autonomy gate with a non-configurable floor, a hash-chained governance log and
about twenty audit tables.

Two things would have to be true for an ECAD lane, and both are concrete:

- **Everything is keyed on a YouTrack issue id.** Locks, cooldown, dedup, audit, reconcile and requeue
  all key on it. An experiment pipeline wanting thousands of cheap runs fights this; one that models a
  *campaign* as an issue and its arms as work units fits natively, and the `work_units` / `features`
  tables already exist for that fan-out.
- **Its shadow-mode allowlist is infra-shaped and default-deny.** `kicad-cli`, `pcbnew`, `ngspice` and
  `make` are unknown verbs and would be blocked. The clean precedent is a cwd-pinned lane exemption
  with a mandatory audit line per admitted action, drilled three ways before being trusted, rather than
  widening the shared allowlist for everyone.

## The lessons that map onto defects this project has already had

These are other people's incidents, and each one is a shape we have hit:

- **Never derive "is the lane armed" from a proxy.** Their false-green recurred four times because
  armed-ness was inferred from a row count instead of asking the component that would act. Ours:
  `routeflow` journalled `ROUTED_CLEAN` on six types while the finish refused on fifteen.
- **A monitor that is blind is better than one that lies**, and both must be distinguished.
- **Test that each halt can actually fire, in both directions.** Two of their halts were structurally
  inert from launch because their inputs were hard-coded zero. Ours: the pair ruling's matcher had
  never fired because an `if !` tested the wrong command, and the deliverable DRC histogram had never
  printed because its pattern was a grep error.
- **A green test suite can actively defend a bug.** They found a test pinning the defect as intended
  behaviour. Every fix ships with a test proved meaningful by failing on the pre-fix tree.
- **When a module states a discipline, check that every input obeys it.** Their evidence clock hashed
  the repo-wide git HEAD into a strategy identity fifteen lines below a comment explaining why an
  over-sensitive hash would destroy the forward record.
- **Cost truth is a precondition, not a report.** Their entire result was decided by a fee that was
  absent from the arithmetic and present in the dashboard. Ours is the layer-count review: no
  like-for-like four against six quote has ever been taken, and the promotion was never costed.
- **Publish the denominator beside the verdict, always, including at zero.** `0 of 3,383` is evidence;
  a bare `0` is what a broken query, an unwired store and a healthy system all produce identically.
  `verdict.py` already enforces this.

## Order of work

**Stage 0, the preconditions, and they are most of the value.** One verdict channel across the 18 gates
that still decide on stdout; determinism, because the chain differs from itself by 48 lines of board
geometry across two runs of identical input; a board hash in and out of every stage; deadlines on the
13 unbounded waits; a passing and a failing fixture per gate as the admission rule for the catalogue.

**Stage 1, the runner and the ledger**, in the shapes above.

**Stage 2, the agent in band**: a runner with no model, a supervisor that is data rather than code, an
agent that proposes and never actuates, a separate reviewer with fresh eyes before "done", and the
owner as the floor.

**Stage 3, width**, and only then the board work: the pair end geometry, the floor plan, the layer P0.

## What this does not promise

That the boards get better. That is what the reviews say plainly, and repeating it here is the point of
the document.
