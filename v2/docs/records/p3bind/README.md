# p3bind: the layout constraint sheets bound to their inputs

MESHSAT-1357, 27 September 2026, worker stream `p3bind`, branch `fnd/p3bind` from `760d7f41` (the set 6 candidate).
**Prototype design: no V2 board has been fabricated, ordered, assembled or powered, and no board is ready for
layout.** This folder is the record of one stream's work; the integrating session is the one writer of `main`.

## What was asked

The independent review of handover H2 (`v2/docs/reviews/2026-09-27-h2-independent-review.md`, section 3 A) found
board A's sheet giving VIN_RAW as 12.31 A and 11.92 mm while the committed intent file declared 14.10 A. Commit
`ecfe5414` re-bound the sheets by hand. Set 6 then changed every board's netlist, and nobody re-ran the calculation
or re-bound the sheets. The task: a check that fails when a sheet and its inputs part, and the sheets re-bound.

## What is in the tree after it

| What | Where |
|---|---|
| the check | `v2/ecad/tools/constraints_bound.py` |
| its fixtures, and the test of the real tree | `v2/ecad/tools/tests/test_constraints_bound.py` |
| the calculation, with the model stated, board E5's table and a second table at the maker's figures | `v2/docs/layout-constraints/calc/rail_widths.py`, `rail_widths.out` |
| the seven sheets: a new opening paragraph, the `bound` block, section 2's tables | `v2/docs/layout-constraints/{A,B,C,D,E,E5,P}.md` |
| the form of the block, the check and how to re-bind | `v2/docs/layout-constraints/README.md`, "The bound block" |
| the registration, for the integrator to run | `apply_rule_and_coverage.py` here |

## The files of this folder

| File | What it is |
|---|---|
| `rail_moves.py`, `rail-moves.md` | the current calculation run on the inputs of `e3aedb25`, `ef144760` (H2) and `760d7f41` (set 6), read out of git: which rows are new, gone or moved at each step. It is where a note's "it was 12.31 A, 11.92 mm at `e3aedb25`" comes from |
| `rail_commits.py`, `rail-commits.md` | for every rail whose declared currents differ from `e3aedb25`'s, the first commit whose intent file carries today's pair, with the rail's own note. It is where a note's commit comes from |
| `rebind_sheets.py` | the re-binding itself: the sheets as they stood at `760d7f41`, the tool's tables, and the notes, each quotation asserted to be a substring of the intent file's own note for its rail. It refuses a sheet edited since; running it again writes nothing |
| `apply_rule_and_coverage.py` | rule DOC-003 with its full text, its coverage entry, `rules_status.CONFIG_INPUTS`, the re-take's `WRITERS` and the sweep. Applied and tried in a scratch clone on the box; never in this tree |
| `box/` | the rented box's logs: the full suite's summary at each commit it ran on (`suite-<commit>.summary.txt`: every line that is not a PASS, the count, the exit code, git status before and after), the registration's trial (`trial.sh`, `trial-91f4bab6.log`, `trial-91f4bab6-decisions-render.txt`) and the first trial at `8099222e` (`apply-tests.log`, `apply2.log`) |

## What set 6 changed, measured

From `rail-moves.md` (the same calculation on each candidate's inputs, so a difference is a declaration's):

| Board | Inputs moved by set 6 | Rows of the power table |
|---|---|---|
| A | netlist and intent file (`c4ad8350`; the intent's `written` stamp alone) | none of 34 |
| B | netlist and intent file (`910da406`) | none of 58 |
| C | netlist and intent file (`e28f91a6`) | +3V3 moved (0.12 / 0.20 A to 0.15 / 0.72 A); EPD_VCC, LED_RAIL_SW, LED_RAIL new; 5 rows where there were 2 |
| D | netlist and intent file (`932cf9d7`; a node, RLY_K) | none of 6 |
| E | netlist and intent file (`c4ad8350`; two nodes) | none of 15 |
| E5 | neither (board file `686b29a734c55b9a`, chain `a09ca0293afd1f7c`) | its table is new: 2 rows |
| P | netlist and intent file (`932cf9d7`) | BAT_F, VCC_F, SEC_VDD, SW, SCP_HTR new; 10 rows where there were 5 |

So the sheets were stale in their HASHES on six boards and in their NUMBERS on two. Nothing told the two kinds apart
until the calculation was run, which is the argument for the check failing on a hash.

## What was run on the box, and what it read

Every run is of `tests/run.py` whole, by `_bin/box_suite.sh`, in a clone of its own under `/root/p3bind/` with the
evidence of `/root/r8int6/evidence-head.tar`. The set 6 baseline the branch starts from, `760d7f41`, reads 2015
passed, 0 failed, 3 skipped there (`/root/r8int6/suite-box.log`).

| Commit | Result | Skipped | git status after the run |
|---|---|---|---|
| `0db41248` | 2047 passed, 0 failed, 3 skipped, EXIT 0 | the three below | ` M v2/docs/CURRENT-EVIDENCE.md` |
| `91f4bab6` | 2050 passed, 0 failed, 3 skipped, EXIT 0 | the three below | ` M v2/docs/CURRENT-EVIDENCE.md` |
| `74cc831c`, the last commit that changes a tool, a test, a sheet or the calculation | **2051 passed, 0 failed, 3 skipped, EXIT 0** | the three below | ` M v2/docs/CURRENT-EVIDENCE.md` |

The branch's last commit adds this folder's record of those runs and nothing else (`git diff --stat 74cc831c..` names
files of `v2/docs/records/p3bind/` alone), so its own suite run cannot be filed in it; its result is in the stream's
final message to the integrator and its log is on the box under `/root/p3bind/`.

- **The three skips, the baseline's own:** `test_finish_order.t_routeflow_validate_agrees_with_these_rules` (the
  profiles pin `/root/gitlab/...`, which exists on the box and is not the tree under test),
  `test_pairsearch.t_the_three_implementations_agree` (no numba on the box's interpreter) and
  `test_per_board_contract_verdict.t_without_pcbnew_the_tool_writes_its_own_verdict_declaring_the_absence` (pcbnew IS
  importable there, so its absence cannot be shown). None is this stream's.
- **CURRENT-EVIDENCE.md is modified by the run, and by the baseline's run in the same line**: "127 more changed only
  their first failing cause" becomes "120 more" (`git diff` in `/root/r8int6/suite` at `760d7f41` is the same one
  line). A test renders the page in the clone; it is not this stream's change and this stream did not touch the page.

**The registration's trial** (`box/trial.sh` at `91f4bab6`, a throwaway clone): `apply_rule_and_coverage.py` applied,
exit 0, and refused a second run, exit 1; `rules_lib.py validate` 60 rules, 0 errors; the re-take's plan 80 commands
over seven boards, 0 errors, with `constraints_bound.py --board <letter>` on each; the re-take in place wrote
`constraints_bound_<letter>` PASS on A, B, C, D, E, E5 and P; after `rules_render.py` (16 documents, 0 out of date)
**DOC-003 read PASS, CURRENT_CANDIDATE, BOUND on all seven boards**; the full suite in that state read 2049 passed,
1 failed, 3 skipped, the one failure being the decisions page's count of pairs, which `decisions_render.py` renders
(338 to 345), after which its test file read 5 passed, 0 failed. The suite was not run a second time whole after
that render.

## Decisions taken by this stream

Each is the session's, taken under the owner's standing rule of 26 September 2026 (the recommended option, recorded,
no question asked): `authority: SESSION`, `ruled_by: p3bind under the owner's standing rule of 26 September 2026`,
`ruled_on: 2026-09-27`. None changes a requirement, a protection or an acceptance limit, and none lowers a width.

| n | Decision | Why | Reverse by |
|---|---|---|---|
| 1 | **A rail the intent file declares a series segment or the return of a pack-path rail, at that rail's own typical and peak currents, is pack path** and is judged at PWR-F12's 18 A. The list typed per board stays, as the roots | Set 6 declared board P's SW, "the common drain of Q1 and Q2 ... the pack's whole current", `series_of` SCP_OUT. The typed list did not know it and the first run sized it at its typical 10 A: 4.08 mm at 2 oz between two segments of one conductor sized at 11.95 mm. The narrower figure is the one a layout would have followed. The currents must be equal because `series_of` is also written on a branch (board B's PANEL_5V at 0.6 A of +5V_DEV's 3.8 A) | `pack_path` in `rail_widths.py` returns the roots alone; SW then reads 4.08 mm |
| 2 | **Board E5 has a generated table**, its currents read from the energy chain's stage DOCK_BLOCK (`continuous_a`, `peak_a`) on its board file's two pack nets | E5's sheet quoted the model's figures in a sentence, which nothing could compare with anything. E5 has no intent file; the chain's stage is the record E5's sheet already cited for what the block carries. The chain declares no voltage and the cell says so | remove `NO_INTENT["e5"]` and `"e5"` from `ORDER`; E5's sheet then declares its board file and has no table |
| 3 | **Reading the chain needs PyYAML**, for E5 alone | the chain is YAML and a detector parses. The six boards with an intent file still need the standard library and the two model modules alone | read E5's currents from another committed record |
| 4 | **A second table sizes board B's under-declared rails at their maker's figure** (`SIZED_TO`: PWR-F01, F03, F05) | The sheet gave those widths already, typed by hand ("1.37 at 3.0 A"). A width is the tool's output or it is not in a table, and dropping the rows would have left a layout sizing a 3 A socket rail at 0.12 mm. The figures are the findings of `POWER-THERMAL.md` section 10, VERIFIED there; this stream did not re-read the makers' sheets. The check refuses an entry once the declaration reaches the figure | empty `SIZED_TO`; the first table's notes still name the findings |
| 5 | **The governing current prints to two decimals** (it printed to one) | 0.15 A printed as "0.1" and 0.02 A as "0.0" | the format in `cells` |
| 6 | **A sheet declares its committed board file too** (boards with a schematic) | the older sections' readings were taken on that layout, and the sheets named its hash in prose, unchecked. Every declared input is compared, read by the calculation or not | remove the `board_file` line from a block |
| 7 | **README.md's table of candidates carries no hash** | it was a second typed copy of what each sheet says, and a copy is what goes stale | restore the hashes; nothing checks them |
| 8 | **The H2 binding's paragraph is kept in each sheet** under the lead "As re-bound to the H2 line ..., kept as that binding's record" | it names what the H2 line changed in the sections this stream did not re-read, which a reader of those sections needs | delete the paragraph when the other sections are re-read |
| 9 | **The rule proposed is DOC-003, BLOCKER, SCHEMATIC, one verdict per board**, not waivable | see `apply_rule_and_coverage.py`. BLOCKER because a sheet that is not the candidate's must not be what layout entry is handed; SCHEMATIC because that is the stage before layout entry; per board because a sheet is a board's | the integrator does not run the script, or edits `release_effect` to MUST_JUSTIFY in it first |
| 10 | **A history-free extraction is not failed for its history**: a declared commit is compared with git only where git answers for the tree and the clone is not shallow; the hashes are compared everywhere | the review's section 5: tests that need git history fail in an extraction of the handover ZIP, and a supported route must not | make `git_state` returning None a failure in `judge` |

## Open items, each with its next action

| n | Item | Next action |
|---|---|---|
| O1 | **Sections 1 and 3 onward of every sheet are not re-read on the set 6 candidate.** Each sheet says so in its opening and in its block's `older` line | the workers who re-read those sections correct the block's `current` and `older` lines and the opening paragraph when they do; `constraints_bound.py` holds the two lines' presence, not their truth |
| O2 | **Board A's PRECHG is sized at nil.** Its typical current is 0 and PI-001 judges a conductor at the typical current, so the table gives 0.00 mm for a conductor that carries 1.68 A while the pack's node charges. The barrels are at the peak (3 / 2 / 2). The same shape: board B's +5V_RB (0.15 A typical, 2.0 A burst), board C's EPD_VCC (0.03 A, 0.52 A) | board A's owner, with PI-001's writer: say in the rule what a conductor whose current is a transient is sized at. Until then the note on the row says what the zero is. Not changed here: it is a rule's question, not a table's |
| O3 | **`calc/stack_solves.out` is bound by nothing.** It depends on the stacks and the pair classes, not on a netlist, and needs atlc | a check of the same kind on the box, where atlc is: the output against a fresh solve, and the sheets' section 3 geometry against the output |
| O4 | **A table's note column is not compared.** The notes written here quote the intent file, and `rebind_sheets.py` asserted every quotation; a note edited by hand later is unchecked | if notes keep carrying figures, move them into a file the check reads (rail, mark, commit, quotation) and render the column from it |
| O5 | **Board C's +3V3 is declared at a 0.72 A peak on an LDO rated 500 mA** (U5, TLV75533). The intent file says so itself and gives its reason; the row's note quotes it | board C's owner: "U5's average through a refresh is an open item read at bring-up" (the intent file's words). Named here because the sheet is where a layout engineer meets it |
| O6 | **The handover pages still say the sheets are bound to the H2 line**: `v2/docs/handover/LAYER-STATUS.md` row 9.8 and the layer 9 integrator line, `START-HERE.md` known gap 8, `CONTINUATION-BRIEF.md` line 62, `H2-RESPONSE.md` M4. `v2/docs/STACKUP-DECISIONS.md` line 322 calls the calculation "stdlib plus" the two modules; board E5's table needs PyYAML now | the integrator and the handover pages' worker: "bound to the set 6 candidate (`760d7f41`) with a check, `constraints_bound.py`; section 2 re-read, the other sections at `e3aedb25` with the H2 line's marks" |
| O7 | **The copies of the sheets under `v2/release/handover/H1/` are H1's** and are not this tree's sheets | none: a snapshot is what it was. The check reads `v2/docs/layout-constraints/` alone |
| O9 | **`v2/ecad/tools/power_path.py` carries an invalid escape sequence**: `parse_netlist`'s docstring quotes a pattern, `(code \d+)`, in a string that is not raw (the compiler reports the statement's line, 51; the text stands on line 55). Python 3.12 on the box prints a SyntaxWarning each time the file is compiled or parsed, in the suite's log beside whichever test was running; Python 3.11 on the runner says DeprecationWarning. Found reading the suite's log; not this stream's file and not changed here | the tools' owner: make the docstring raw. A warning today, an error in a later Python |
| O8 | **The registration is not applied.** Until it is, `constraints_bound.py` decides no rule and no page reads it; the test of the real tree in the suite is what holds the sheets meanwhile | the integrator runs `apply_rule_and_coverage.py`, the re-take on the box, `rules_render.py` and `decisions_render.py` (the script's header lists the steps, in the order the trial ran them, and what the pages will show) |

## For the index of `v2/docs/records/README.md` (the integrator's file)

| folder | whose records |
|---|---|
| `p3bind/` | the layout constraint sheets bound to their inputs (27 September 2026, branch `fnd/p3bind` from `760d7f41`): the comparison of the power tables over three candidates and the commit of every moved rail, the script that re-bound the seven sheets from their text at `760d7f41`, the registration of `constraints_bound.py` as rule DOC-003 for the integrator to run, and the box's logs of the suite and of the registration's trial |
