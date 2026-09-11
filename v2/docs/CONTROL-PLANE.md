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
| 7 orchestration | **stage 0a and 0c done 11 Sep**: `full_*.sh` 21 to 7, `finish_*.sh` 31 to 15; **24 tools write a verdict JSON, none decides on stdout**; every journal row carries its board hashes; every wait bounded |
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

## What the first day of the programme measured (11 September 2026)

**Stage 0 closed and found a real defect**: a random KiCad UUID decided which escapes fit, worth four tracks
and four vias of 391 on D. After `boardorder.py`: D 0 of 391 across three runs, A 0 of 1483, C 0 of 556.

**Phase A's two levers were measured and both under-delivered against their written predictions.**

| lever | predicted | measured |
|---|---|---|
| C2, the corridor end tested where the stubs start | +15 or better of 23 pairs | **+3** (53 to 56 of 113) |
| C3, the occupancy maps counted once | maps 1,010 s to under 120 | **514 s to 388 s, 1.32x** |

**The review's classification of the failures was wrong for this board.** It counts 23 as "no stub path
reached the PAD"; the measured profile is **30 "no stub path AT VIA" and 32 of all failures dying at a via
rather than a pad**. Those are a different code path, and the record's own 32.90 profile said so in August.
The other 30 are "the legs clear no smoothing", for which the review prescribes a bevel that has been in the
tool since 10 September.

**The review's proposed map expression was unsafe.** `all & ~own_P & ~own_N` frees cells that another net
blocks wherever two grown rasters overlap, which on a dense board is wherever two nets run within twice the
clearance. The maps count rather than OR.

**Two of my own changes were wrong and only measurement caught them:** the counted map was slower than what
it replaced until the copper was indexed by net, and making every "0 of 0" INCONCLUSIVE would have blocked
board C, whose declared design is to carry no impedance target.

**What this says about the plan.** Stage 0 was worth what it claimed. Phase A's levers were not, and the
honest next lever is the one both profiles name and neither review costed: the stub-to-escape-via geometry at
the fine-pitch parts. **A prediction written before a run is the only reason any of this is known**, and
three of the sixteen arms now queued predict a loss on purpose.

## What the first day's evening measured (11 September 2026, 20:00 CEST)

**The sixteen-arm sweep answered Phase A, and mostly by refusing it.** One placed B19 board, one knob per arm,
113 pairs, graded against predictions written before the run.

| arm | predicted | measured of 113 |
|---|---|---|
| base | 53 | **54** |
| `PAIR_CORRIDOR_SLACK=0.08` | >= 55 | **60** |
| `PAIR_CORRIDOR_SLACK=0.15` | <= 53 | **59** |
| slim retry 0.03 | >= 55 | 56 |
| the leg test (`PAIR_END_LEGS`) | >= 60 | 55 |
| the escape-via entry | >= 65 | **54** |
| the escape-via entry with the leg test | >= 68 | **54** |
| the escape-via entry with the slim retry | >= 66 | **49** |
| the staircase turned OFF | <= 45 | **55** |
| 30 corridor-end candidates | >= 62 | **58** |
| 60 corridor-end candidates | >= 62 | **59** |
| wider search window, longer strip, more expansions | mixed | 55, 55, 55 |

**Three things come out of it and none of them is the thing the plan expected.**

**The escape-via entry is not a lever on this board.** It was the largest single number in the record (+27 on B,
32.95) and it is worth zero here: 54 against 54, and 49 when combined. Measured on D the same evening it is
worth **minus two** (1 of 5 against 3 of 5). It stays a per-pair fallback and nothing more.

**The corridor slack is the largest lever, and the default sits in a hole.** 0.08 gives 60 and 0.15 gives 59 against
0.12's 54. A default beaten on both sides is not a local optimum, so the second sweep walks 0.04 to 0.20 rather
than guessing a third value. That sweep is queued.

**The end-candidate count is a second real lever, and reading a partial run nearly hid it.** At 30 and 60
candidates the DIFF100 pass laid three FEWER pairs than base, and on the half-finished run that is all there
was to see. The USB pass then laid seven and eight MORE, for totals of 58 and 59. **A pass count read before
the run ends is not a measurement**, and the arms exist precisely so that the number is taken once.

**Nine of the sixteen predictions were wrong, three of them badly.** That is the instrument working: an arm
that cannot miss teaches nothing, and the three deliberate-loss arms were the ones that came closest to being
right. What the ladder of 32.95 called levers were mostly noise at plus or minus one pair around 54, and only a
written prediction makes that visible rather than encouraging.

**And the boards moved while the arms ran.** E routed to 0 hard and 0 unrouted (179 vias, 6.2 minutes, the stub
router closing its one open), C is routing, P routed and finished every electrical gate, A placed clean and
`check_contracts` passes 40 of 40 with it present. Four defects in the verdict channel were found and fixed in
the process, every one of them a writer that had been wrong for as long as nobody read it; they are in
`project_unread_channel_defects.md` and in appendix 32.113 and 32.114.

## Order of work

**Stage 0, the preconditions, and they are most of the value.**

| item | state on 11 September |
|---|---|
| 0a one verdict channel | **done**: seventeen more gates write `out/<tool>.verdict.json` with counts, denominator and evidence, and exit with it; no driver greps a gate's prose; no finish runs its board gate twice. `tests/test_verdict_channel.py` holds the shape, and its four structural rules fail on the pre-fix tree |
| 0b determinism | **done and proved**: the cause was a random KiCad UUID, not Python. Two runs of D differed in **four tracks and four vias of 391** (the `/MICAMP_OUT` and `/SAU_RST` escape stubs) because `escape.py` walks the board in file order, that order follows the uuid KiCad mints per item, and the pass lays greedily. `boardorder.py` fixes it in the four laying passes. After: **D 0 of 391 across three runs, A 0 of 1483, C 0 of 556**. `tests/determinism.sh <letter> [runs]` is the standing check; `board_diff.py` is what makes the question answerable, since `diff` reported 26,142 lines of 36,724 on C and the largest bucket was `(uuid` |
| 0c board hash per stage | **done**: `journal()` attaches the hash of every board file of that board that exists when the row is written, so in and out are the same field on consecutive rows. `provenance.json`'s board hash is `board_sha_before_run` now, because it was a true value under a name that claimed something else |
| 0d waits and fixtures | **done**: every wait bounded (the twelve finishes on 10 Sep, `long_route.sh` on 11 Sep, which waited on any Freerouting process started outside its own flock). `tests/test_gate_fixtures.py` carries a passing and a failing fixture for the gates that judge a file, a folder or a number, and **the admission rule**: a gate with no fixture and no declared debt fails the suite. Five are declared, printed on every run, and all five need a board |

Two things found by doing this rather than by planning it, both of the same class as everything else here:
`PREROUTE_STOP_AFTER_PLACE=1` was silently a no-op on E and P, whose chains have no pair classes, so the
placed snapshot the pre-router measurements rest on was never written for them; and `pcb-b-compute/` carried
`b5m.kicad_pcb`, the 2 September B5 board, which sorts before the real one, so a wave script that globbed the
directory exported a BOM for B from a nine-day-old board with 160 footprints against the current 951. **That
B BOM must be re-exported, and nothing downstream consumed it:** `out/` is not tracked, so it never reached
the repository, and the parts certification reads the deliverable folders under `v2/release/revA/boards/`
rather than these exports, taking B from `meshsat-pcb-b-revA-B16-quote` as the newest B deliverable. The
certification's 150 B rows are therefore sound. The damage was one wrong file on the rented box, and the
only reason anyone noticed is that the exporter printed the name `b5m`.

**Stage 0 is complete as of 11 September 2026 05:30 CEST.** 53 tests pass, 5 skip for want of pcbnew on the
runner; routeflow's selftest is 52 of 52; the six board gates were run on real boards on the box.

**Stage 1, the runner and the ledger**, in the shapes above.

**Stage 2, the agent in band**: a runner with no model, a supervisor that is data rather than code, an
agent that proposes and never actuates, a separate reviewer with fresh eyes before "done", and the
owner as the floor.

**Stage 3, width**, and only then the board work: the pair end geometry, the floor plan, the layer P0.

**Correction, 11 September 2026.** The phase copy directories are not tracked in git, so the routed C10, D10,
A24 and E7 boards went with box 50216670 when it was destroyed. Those routes were already throwaway under
32.95, since the pre-router has changed and every board is regenerated, and no deliverable was lost. But the
plan's phase D2 assumed C10 could have its deliverable cut from the board as it stood, and it cannot: C must
be re-routed first. **A routed board is an artefact. One that exists only in a rented box's untracked copy
directory exists nowhere**, and either the phase copies are tracked or a route that reaches 0 hard is
committed the same hour.

## What this does not promise

That the boards get better. That is what the reviews say plainly, and repeating it here is the point of
the document.
