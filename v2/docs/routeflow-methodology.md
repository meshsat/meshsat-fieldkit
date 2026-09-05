# Routeflow: agentic plumbing around Freerouting (5 Sep 2026)

Freerouting is the only open-source autorouter that talks to KiCad, and it is the weakest tool in the pipeline: no progress output, a
multi-threaded optimiser its own log calls broken, no length matching, a silent timeout that leaves no session. The evening of 5 Sep 2026
showed what that costs when the plumbing around it is loose: a generator that failed without a traceback was filtered out of a chain log and
the gate then judged the previous board; a stub router that could not import numpy crashed in every finish since the move to the VM and the
filter showed one line of it; three route attempts thrashed for 75 minutes and produced nothing to look at. None of those were Freerouting's
fault. They were the plumbing certifying instead of catching.

This note audits three agentic repositories on the same runner (`~/gitlab/products/territory-grounder/grounder`, `~/gitlab/n8n/logos`, its
lineage `~/gitlab/n8n/finops-agora` and `~/gitlab/n8n/claude-gateway`) for the practices that transfer, and records how `tools/routeflow.py`
applies them. Nothing here replaces the generators, the gates or the chain scripts; routeflow supervises them.

## 1. What the audit found and where each practice came from

| Practice | Source | Applied here as |
|---|---|---|
| **Fail closed: no verdict without a committed prediction; the model never grades its own outcome; verdicts are mechanical** | finops-agora invariants 2 and 3, logos invariants 1 and 2 | a run profile states the expected outcome (`expect`) before the route starts; every verdict number (hard, unrouted, vias, pair mismatch) comes from DRC JSON and the gate scripts, never from reading a log or an image; the session's visual audit is a signal that guides a remedy, never a pass |
| **Mutate toward emptiness: a gate must print its denominator; "found nothing" gets its own state; kill it with an EMPTY input before trusting it** | territory-grounder AGENTS.md TG-365 | every stage predicate reads its own artefact (a `saved` line, a `.ses` file, a parseable DRC JSON, a `clean` flag) and refuses when the artefact is absent; numbers print with denominators (`unrouted 5 of 1157 nets`, `hard 0 of 6 checked types`); `routeflow.py selftest` feeds each predicate an empty or missing input and demands the blocking state |
| **Explicit status vocabulary, append-only record** | logos Articles V and XVII, finops-agora | `out/routeflow/journal.jsonl` gets one line per stage transition with a fixed vocabulary (below); corrections are new lines, never edits |
| **Deterministic identity and dedup** | logos invariant 6, finops-agora 6 | a run id is the hash of the tools' git revision, the profile and the pre-route board; the journal shows when the same inputs were routed before |
| **Deterministic rules decide; the LLM proposes** | finops-agora 4, logos 4, territory-grounder guardrail 7 (the model never authors an executed command) | the remedy table is code: a failure signature maps to a profile change (threads, passes, timeout, power layers) and a bounded number of rounds; anything outside the table stops with a named state for the session to fix in the generators; routeflow never edits a generator and never composes a shell command from model text |
| **Live-verify before selecting work; deploy-verify after** | territory-grounder operating loop steps 2 and 8 | `routeflow.py preflight` checks the host (imports, binaries, jar, memory, load, the service group, the tools tree at origin/main, no other route running) before any stage; the finish's deliverable existence is verified after, not assumed |
| **One route at a time, mechanically** | owner ruling 5 Sep 13:30 (memory and swap) | a lock file names the board that owns the router; a second run waits or refuses |
| **Eval gate before a behaviour change; scorecard traps written down** | territory-grounder guardrail 8 and `tg-eval-runner` | a change to a chain, gate or route parameter is tried on the board it is meant for and graded against `expect` before it becomes the profile default; the known traps (a 9999 winner "finishes" through the stub router; a filtered generator; a stale plane fill counting a legal via as a violation) are in the remedy table's guard clauses |
| **Fresh-eyes review at a stated confidence before "done"** | territory-grounder delivery bar v1.1 and `tg-code-reviewer` | a board is DONE when the finish committed a deliverable AND a separate review (the gate outputs, the DRC JSON and the audit image read by a session that did not run the chain) records a verdict; the visual audit ruling of 5 Sep (no human look) is satisfied by the audit image being produced and read every time a run stops |
| **Counts are generated, not hand-written** | finops-agora 11, logos 12, claude-gateway 2026-06-11 | via counts, open counts, pair lengths and run durations in the appendix and the release notes come from the journal (`routeflow.py status --markdown`) |
| **Verify agent output against live sources** | claude-gateway 2026-06-26 | the summary a session posts is regenerated from the journal and the DRC JSON, not from memory of the log |
| **Autonomy boundary: decide, do, record; a short list of reserved classes** | territory-grounder TG-488 | routeflow decides the remedies inside the table and its round budget; what needs a generator change, a rule change (layer count, keep-outs), a part move or money is a named stop for the session, and design rulings stay the owner's |
| **Worker split: cheap deterministic labour, the expensive model only where judgement is needed** | logos `zai_agent.py`, invariant 11 | the supervisor is plain Python with no model in the loop; the session is called only on a named stop |

## 2. The status vocabulary (one word per journal line)

`PREFLIGHT_FAIL`, `GENERATING`, `GATE_BLOCKED` (a FAIL line, or a generator that did not save), `ROUTING`, `NO_SESSION` (the limit hit with no
`.ses`), `ROUTED_HARD` (hard violations in the winner), `ROUTED_OPEN` (opens only), `FINISHING`, `FINISH_REFUSED`, `TOOL_CRASH` (a stage exited
non-zero or printed a traceback), `CLEAN`, `COMMITTED`, `STOPPED_BUDGET` (the remedy rounds are spent), `STOPPED_NEEDS_GENERATOR` (the signature
has no remedy in the table). "Clean" keeps its 6 Sep 2026 meaning: `check_pcb_*.py` ALL PASS on the filled board, 0 unrouted, 0 of the six hard
DRC types, pairs within 1 mm.

## 3. The remedy table (the failure classes of 5 Sep 2026, each with its evidence)

| Signature (computed from the artefacts) | Remedy (a profile change, one round) | Evidence |
|---|---|---|
| `NO_SESSION` on every attempt | if inner plane layers exist and are not yet power layers: `power_layers` = the plane layers, `timeout` x 2; else `timeout` x 2 once | B15 run 1: three attempts, 75 min, nothing; E1 showed power layers halve the pass time |
| `ROUTED_HARD` where every hard item lies on one layer, between two nets, in fragments under 0.5 mm | `threads` = 1 | B15 run 3: 39 items, all In3, +3V3 against WIFI_DIS, the documented multi-thread optimiser defect |
| `ROUTED_OPEN` after the finish (the stub router could not close them) | `passes` +30 percent, one more attempt | B15 runs 2 and 3: the same five opens at 60 and 100 passes |
| hard items dominated by `copper_edge_clearance` | stop, `STOPPED_NEEDS_GENERATOR` (an edge keep-out band belongs in the outline generator) | C6 run 3: six tracks 0.3 mm from the right edge |
| the same opens on every run at adjacent same-net pins (a connector's paired pins, a fine-pitch part's consecutive rail pads, a pass-through ESD diode) | stop, `STOPPED_NEEDS_GENERATOR`; the fix is `tools/join_adjacent_pins.py` in the pre-route chain (a locked joiner makes each group one island) | B15 runs 2 and 3: J_PANEL pins 1 and 2, the hub's +3V3 escapes; 26 joins on B15, no DRC change |
| the generator log has no `saved` line | stop, `GATE_BLOCKED` with the log's tail | C6 run 1: the footprint that KiCad could not load |
| a stage exits non-zero or prints `Traceback` | stop, `TOOL_CRASH` with the traceback | the stub router without numpy |
| a gate prints any `FAIL` line, whatever else it prints | stop, `GATE_BLOCKED` with the FAIL lines | B14 run 1 lesson: two `RESULT: ALL PASS` lines and a FAIL between them |

The round budget defaults to two automatic remedies per board; the third stop goes to the session with the journal and the audit image.

## 4. What routeflow does not do

It does not edit generators, footprints or rule areas; it does not move parts after routing; it does not choose layer counts; it does not
touch the JLCPCB cart or the release; it does not run two routes at once; it does not decide when a board is "final" (owner). It runs the
existing stage scripts with fixed argument vectors, judges their artefacts, records every transition, applies the table, and stops with a
name when the table ends.

## 5. Delivery bar for a board (from the territory-grounder bar, restated for hardware)

1. **Generated**: the pre-route chain ran and its own `saved` lines are in its logs.
2. **Gated**: `check_pcb_*.py` ALL PASS with no FAIL line; pre-route DRC without hard items.
3. **Routed**: a session file exists for the winner; `hard 0 of 6 types`, `unrouted 0 of N nets` on the filled board; pairs within 1 mm.
4. **Finished**: the deliverable folder has the gerber zip with every copper layer, BOM, CPL, DRC report; the finish committed it.
5. **Reviewed**: a fresh-eyes pass over the gate outputs, the DRC JSON and the audit image recorded a verdict with a stated confidence.
6. **Recorded**: the journal's generated numbers are in the design record and the release notes; the issue carries the same numbers.

## 6. Files

- `v2/ecad/tools/routeflow.py`: the supervisor (`preflight`, `run <profile>`, `status <project>`, `selftest`).
- `v2/ecad/tools/routeflow/*.json`: one profile per board phase (the argument vectors, the route parameters, the expectation, the deliverable).
- `out/routeflow/journal.jsonl` in each project: the append-only record; `out/routeflow/<run>/` the captured stage logs.
- `v2/ecad/tools/route_audit.py`, `pair_audit.py`: the images the session reads when a run stops.
