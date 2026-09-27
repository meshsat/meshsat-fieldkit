# V2 engineering red team, round four, 15 September 2026: the code pack at 0d5993d

Against `meshsat-fieldkit-code-2026-09-15.zip` (`v2/ecad/tools`, `v2/cad`, five documents; no board files, no appendix, no
`out/`). Same lens as rounds one to three: efficiency, architecture, engineering. Method: the measurement battery of the
earlier rounds re-run on this tree, the 476-rule suite run here (460 pass, 7 fail, 9 skip), every round-three item checked
against the code, the new pieces read (`rail_prune.py`, the pre-lay stage, the knob registry, the place run shape, the
twelve A profiles), and the arithmetic of the last three days taken from the profiles and the finish's own comments.

## Verdict

Twelve of the fourteen round-three items are done in code, including all four I asked for first: the placed-board DRC
now blocks before the pair passes with a declared allowance, the `"place"` run shape exists in the runner and the registry
carries five `PLACE_*` knobs, the prediction gate refuses a value the best row already meets, and the exec chokepoint is
an argv. The suite went from 258 rules to 476 and the mutation script from 10 proofs to 23. The jar is built at box start.

Then the mechanism built for B was not pointed at B. `agent/templates/b.json` is unchanged since 12 September
(`_runs: "pair"`, "22 of 48 on this pass"), the newest committed arm is from the 11th, and B is "quote only, not routed".
The three days went to A and C: **eleven A profiles after A24 (A25 to A35) and seven C profiles (C11 to C17), each a full route of
up to five or six hours from a fresh placement**, to close the last four opens and two pour items on A, with the finish
growing a closer per phase. The finish is now ten copper-editing passes after the router, guarded by five hand-rolled
keep-or-revert blocks, one of which runs twice because two of the closers undo each other's preconditions.

The critical path (B's 113 pairs, every one required) has not moved since the 12th. The tool that decides it is 2,790
lines with a 1,971-line `main()` and 59 environment knobs, 32 of which nothing sets.

---

## Critical

### C1. The place run shape was built and B was never run through it

`arms.py:120-133` implements `"place"`: regenerate through `full.sh` with `PLACE_*` in the environment, stop after the
placement, run the pair passes on what it produced. `agent/knobs.json` registers `PLACE_COUPLE_GAP`, `PLACE_FINE_MARGIN`,
`PLACE_GAP`, `PLACE_NO_UNDER_FINE`, `PLACE_PTH_OBSTACLE` at stage `place`. `agent/schema.py:52` maps the shape. Every piece
round three asked for is there.

`agent/templates/b.json:23`: `"_runs": "pair"`. `d.json:19`: the same. `arms/` holds `b19-slack.json` and
`b19-stubvia.json`, both of 11 September. Nothing in the tree has ever asked the runner for a placement arm, and the
record's own diagnosis (32.146, 32.147: the wall is at the stations, the couple gap moved the number) is three days old.
Meanwhile B's placed board carried 20 hard violations on the 12th and `full.sh:123-132` now blocks a placed board above
an allowance of zero, which `boards/b.json` does not declare; if those 20 stand, B's chain now stops at the placed-board
gate, correctly, and the only way to B's pairs is a placement change, which is the run shape nobody has run.

**Fix.** A `b-place.json` template: `_runs: "place"`, the five placement knobs proposable, the same passes, `_max_arms` 4,
and the loop pointed at it for a day of box time. Declare B's `placed_hard_allowance` with its number and section, or fix
the 20 first; either is a placement decision the loop can now measure.

### C2. Eighteen full routes in three days to close four opens, and the finish became a second router

`routeflow/a25.json` to `a35.json`: eleven profiles after A24, `passes [18]`, `timeout 18000`, differing from one another in
the phase string and a `_phase_note` and in nothing else. `c11.json` to `c17.json`: seven, at six hours each. The A35 note
reads: A34 "routed 0 hard, 4 open (three GND pads a via short of their plane, one 0.5 mm VBUS20 gap) and its gate refused
two pour items: the PA rail head island filled 51 of 102 mm2 with router tracks across it (a track keep-out on the island
now), and a locked VBAT stitch via the In2 fill had abandoned, which stitch_prune could only remove after rail_prune had
taken the router track ending on it (the finish prunes twice now)." Each phase found one defect after a five-hour route,
fixed one instance in a generator, and routed again.

The finish that judges those routes now runs, after Freerouting: `unknot`, `cleanup_dangling` three times,
`zone_pad_via`, `pour_stitch`, `cont_route`, `stub_router`, `stub_accept`, `stitch_prune` twice, `direct_close`,
`quality_pass`, `silk_fix_all`, `rail_prune`. Ten tools that lay or remove copper, with 22 DRC runs per finish (16 in
`finish.sh`, six in the scripts it calls; 18 in round three, 14 in round one). `rail_prune.py:1-9` says why it exists:
"Freerouting never sees a pour ... where the rail already runs from source to load in a band the router lays a 0.5 mm
inner track in parallel with it", and `dc_drop` then reads the rail as failed. That is a defect the pipeline already knows
how to prevent for planes: `prefanout.py` gives every plane pad a locked via and stub before the route so the router sees
it connected and lays nothing. Rail pads get no such fanout, so the router lays the wire, `rail_prune` removes it after
connectivity trials, and `stitch_prune` has to run a second time on the copper that leaves.

**Fix, in this order.** (a) A locked fanout from every rail pad into its band before the route, the plane treatment
extended to the intent file's rails; `rail_prune` stays as the guard and should then remove nothing. (b) The classes the
last eleven phases found, as policies in the generators rather than instances: every rail island gets its track keep-out
when it is laid; every plane pad without a via within reach is a placed-board defect, which `place_audit.py` can predict
before a route the way it predicts collisions. (c) Then a phase is a generator change plus one route, not eleven.

### C3. `pair_preroute.py` grew again, and the knob registry is provenance for accretion

| | 10 Sep | 12 Sep | 15 Sep |
|---|---:|---:|---:|
| lines | 1,563 | 2,497 | 2,790 |
| `main()` lines | 1,077 | 1,733 | 1,971 (`:819` to `:2790`) |
| `PAIR_*` knobs read | 32 | 53 | 59 |
| experiment knobs set by no board, arm or template | | 30 | 32 of 47 |

`agent/knobs.json` now registers 65 knobs with a type, a default, a category and a stage, and a completeness rule keeps it
in step with the source. That is better provenance than round three had. It also makes the accretion permanent: the 32
experiment knobs nothing sets (`PAIR_LEG_RETRY`, recorded in 32.146 as laying no pairs; `PAIR_RIPUP` and its three
companions, rejected on 10 September; `PAIR_FOLD_TEST`, `PAIR_FAN_BACK`, `PAIR_UNMERGE`, ...) are each a code path in a
function nobody can hold in view, and each is in the agent's search space by category. Round-three C3 asked for the
opposite direction: a knob that won becomes the code, a knob that lost is deleted with its section cited.

**Fix.** The same as round three, with the registry as the worklist: for each experiment knob nothing sets, either the
record shows it lost (delete the branch, cite the section) or it was never measured (measure it once through the loop
or delete it). Then the split. `main()` at two thousand lines is the file the reviewer agent is asked to read.

---

## High

### H1. The supervisor still versions by filename

`routeflow/` holds 34 profiles: thirteen for A, nine for C, three for B, three for D, three for E, three for P. Consecutive
profiles differ only in the phase string (`diff a34.json a35.json`: five lines, all `A34` to `A35`, plus the note). The
chains fixed this on 10 September (`boards/<letter>.json`, `PHASE` a parameter); the supervisor is where round two's H3 and
round three's H2 both said the copy pattern remained, and it now has twice as many copies. The profiles also still carry
the pass ceilings (`passes [18]`, `[30]`, `[45]`) that existed because a cut run left nothing; `onstart.sh:28` now builds
the per-pass jar and `fr_jar.sh` refuses to route without it, so the ceilings protect nothing and cost the best pass on
every board. `routeflow.py:165` still carries the `NO_SESSION` remedy.

**Fix.** One profile per letter, the phase from `boards/<letter>.json` or the command line, the note in the record; passes
raised to the timeout; the `NO_SESSION` branch deleted (the jar is now a precondition, so its absence is `INFRA_FAIL`).

### H2. Five copies of the keep-or-revert guard, and the one that measured the wrong thing cost a phase

`finish.sh:104` (stub router, reverted on hard), `:113-125` (the stub stage, reverted on unrouted after A25 went from 13
opens to 81 with the first guard passing), `:141-159` (`prune_stitch`, reverted on hard or unrouted, called at `:159` and
again at `:190`), `:165-173` (`direct_close`, "judged by the DRC below"), and `full.sh:216-236` (the pre-lay, reverted on
hard alone). Five hand-rolled snapshot, run, DRC, compare, restore blocks with three different comparison rules, and the
comment at `:106-112` records that the difference between two of those rules was the A25 phase.

**Fix.** One shell function, `guarded <label> <snapshot> <command...>`: snapshot, run, `drc.sh`, `hardset --counts`,
compare hard AND unrouted against the board it was handed, keep or restore, one verdict JSON with both counts and the
seconds. Five blocks become five lines and the next closer gets the right rule without being able to choose a wrong one.

### H3. The suite on a code-only checkout: seven failures, and the Skip path that was written for it has a NameError

`tests/run_tests.sh` here: 460 pass, 7 fail, 9 skip. Five of the seven are missing artefacts (no `release/`, no appendix,
no project files, no `.git`), which round-three M1 said should `Skip`. One of them is the Skip: `test_finish_order.py:147`
raises `Skip("no phase project directories in this checkout ...")` and the file imports `os, re, sys, json, glob` (`:21`),
so the rule fails with `name 'Skip' is not defined`. The path added for the host without artefacts has never run on a host
without artefacts. Only 8 of 62 test files raise `Skip` at all; ten that read `release/`, a board or the appendix do not.
The seventh failure looks real: `test_order_codes` finds three fill rules naming lands no generator draws (`5032`,
`IDC-Header_2x10_P2.54mm_Vertical_SMD`, `PinHeader_1x08_P2.54mm_Vertical_SMD`), rules that can never fire.

**Fix.** A `need(path, why)` helper in `harness.py` that raises `Skip`, used by every rule that reads an artefact; the
import; the three dead fill rules deleted or their lands restored. The pack's own note says "469 rules"; the tree has 476.

### H4. The documents a reader is pointed to are three days behind a three-day-old programme

`v2/README.md:39` "Regenerating a board" still describes `full_<board>.sh`, `route_parallel.sh '<attempt list>'` and
`finish_<board>.sh`, the chain of 9 September; the tree runs `full.sh`, `routeflow.py` and `finish.sh` from
`boards/<letter>.json`. `docs/CONTROL-PLANE.md` and `docs/AGENTIC-SYSTEM.md` are byte-identical to the 12 September pack:
nothing about the place run shape, the registry, the falsifiability bar, `rail_prune`, the pre-lay, or A25 to A35. The
README's board table names A24 while the profiles are at A35, and `test_public_tables` exists to catch exactly that but
cannot run without `release/`. The design record presumably has all of it; a reader of the public tree cannot tell.

**Fix.** The README's pipeline section rewritten from `full.sh`'s own header (it is already the better description); a
dated "state" section at the top of `CONTROL-PLANE.md` regenerated from the ledger; the board table generated from the
deliverable folders by the same rule that tests it.

---

## Medium

### M1. The A phases are discovering placed-board defects after a route

Of A35's four items, two are answerable before any route: a GND pad "a via short of its plane" is a fanout the placed
board lacks, and a rail island without a track keep-out is a generator omission visible in the placed board. The
placement predictor (`place_audit.py`) predicts collisions and decoupling; it does not predict these two classes, and B
now declares its verdict advisory (`place_audit_gate_off`). Add the two classes to the predictor and the eleven-phase
shape of C2 shortens by the phases those classes cost.

### M2. The pre-lay is a per-board closer in the chain, not a rule

`full.sh:216-236`: `prelay_nets` in `boards/c.json` names a net the router "will not take" (249 mm across a ring) and lays it
with the stub router before the route, guarded by hard count only. It is the fifth special-case closer declared per board
(`cont_route`, `direct_close`, `stitch_prune`, `rail_prune`, `prelay`). Each is a fact about one board turned into a stage.
The pattern is the finish of C2 arriving in the pre-route chain.

### M3. Nothing pushes a clean routed board off the box

Round-three M5: written as a lesson in `CONTROL-PLANE.md` ("a routed board that exists only in a rented box's untracked copy
directory exists nowhere"); `finish.sh`, `finish_board.sh` and `routeflow.py` still write the deliverable under the
checkout on the box and nothing commits or uploads it. The board hash is in the ledger; the board is not anywhere.

### M4. The loop's verdict still grades the write-up

Round-three L3, not taken: `agent/loop.py:294` writes `agent_loop` PASS when the reviewer approved the entry and FAIL when
it did not, whatever the arm's grade. Name it `entry_review`, or carry the arm verdict as the verdict and the review as a
count.

---

## Low

- **L1.** `_max_arms` defaults to 1 (`agent/loop.py:172`); the loop is serial unless a template says otherwise, and no
  template does.
- **L2.** `finish.sh` prints no elapsed time; `drc.sh` writes its seconds (round-three H3, done) and nothing sums them.
  One `SECONDS` line at the end of the finish, and the 22 DRC seconds added up, would say what the finish costs.
- **L3.** `tests/test_agent_contract.py` is 46 rules; the mutation script proves 23. The other 23 and the 105 source-grep
  rules across the suite (of 476) rest on process.
- **L4.** `README-CODE.txt`: 469 rules; the tree has 476. `v2/README.md`: "Freerouting 1.9.0" and `~/bin/freerouting-1.9.0.jar`;
  the pipeline refuses that jar.

---

## What is good, so the review is honest

The placed-board gate before the pair passes; the place run shape in the runner with its own timeout and its own log; a
knob registry with categories, stages and a completeness rule; the falsifiability bar with best and worst rows; the argv
chokepoint; the verdict files handed to the reviewer; the git fingerprint on every row, with a dirty tree graded
UNMEASURED; `drc.sh` timed and hashed; the jar built at box start and refused when absent; 23 mutation proofs; a rule
that checks every reserved pattern still matches a line; `rail_prune.py`'s docstring, which says exactly why the tool
should not have to exist; and the A25 lesson written into the finish the same day (the guard that measured the wrong
count). The programme still fixes the tool that produced the defect. It has not yet stopped adding tools.

## What I would do next, in order

1. **C1**: `b-place.json` and a day of the loop on B with the placement knobs. The mechanism is built; this is the run.
2. **C2(a)**: the rail fanout before the route. An afternoon, and `rail_prune`'s second pass goes with it.
3. **H2**: the `guarded` function. An afternoon. The next closer inherits the A25 rule instead of rediscovering it.
4. **H1**: profiles by letter, passes to the timeout, `NO_SESSION` deleted. An hour.
5. **H3**: `need()` and the import. An hour. Run the suite once on a checkout with nothing generated, and keep doing so.
6. **M1**: the two placed-board classes into `place_audit.py`, so an A phase is found before a route.
7. **C3**: the 32 registry-only knobs to code or to the record; then the split.
8. **H4**: the three documents brought to the 15th, or replaced by a pointer to the sections that are.

## What I could not verify from the pack

- Whether B's placement still carries the 20 hard violations of the 12th, and therefore whether B's chain is blocked at the
  new placed-board gate: no board, no `boards/b.json` allowance.
- The actual duration of the A and C phases: the profiles carry the ceilings (5 and 6 hours), not the runs.
- Whether the three dead fill rules are dead in the repository or only in this pack, which has no footprint library.
