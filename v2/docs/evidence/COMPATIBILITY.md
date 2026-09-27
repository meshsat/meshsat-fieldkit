# Evidence compatibility register

MESHSAT-1357, 26 September 2026. Review of that day (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`,
section 1): "Reuse unaffected evidence only with a recorded dependency/compatibility rationale. A tool documentation
change need not invalidate a calculation; a changed matching or polarity algorithm can." Prototype design: nothing
here is built or measured.

This page is the record that rationale lives in. `rules_status.py` reads the block at the end (`registers`,
`_compatible`) and classes a reading VALID_HISTORICAL only when an entry pins BOTH versions by content:

- `kind: tool`: `tool` (the writer file name), `then` (the reading's code bundle sha16, `code_bundle.sha16`; for a
  reading written before the bundle, the writer sha256/16 it carries), `now` (the sha16 of that writer's code bundle in
  this tree, `rules_status._bundle_now16`). Since 26 September 2026 (the review of the 22:35 progress report, finding
  D2) a reading's tool is its code bundle, the entry script and every local module it imports (`verdict.code_bundle`),
  so an entry's rationale has to answer for EVERY file of the bundle that moved, and a later edit of any of them changes
  `now` and stops the entry applying by itself.
- `kind: artefact`: `rule`, `board` (letter), `input` (`netlist`), `then` (the sha256/16 the verdict recorded),
  `now` (the sha256/16 the board's phase directory holds).
- `kind: config` (added 26 September 2026, second round): `rule`, `board`, `input` (the configuration file, relative
  to `v2/ecad`, exactly as `rules_status.CONFIG_INPUTS` resolves it), `then` (the sha256/16 of that file in the tree
  of `recorded_in`, the first commit that holds the reading's bytes), `now` (the sha256/16 of the file in this tree),
  and the claim that makes the change harmless in a form a test re-derives from git: `keys` (the JSON keys the tool
  reads, equal in `then` and `now`, absent in both counting as equal) or `additions_only: true` (no line of `then` is
  removed or altered in `now`). `v2/ecad/tools/tests/test_evidence_class.py` re-checks every entry whose `now` is the
  file in the tree; an entry whose `now` no longer matches applies to nothing and is inert. Since the third round
  (26 September 2026, on a checker's finding) a config entry also names the ONE reading it vouches for: `verdict`
  (its path relative to `v2/ecad`) and `reading` (that verdict's `ts`, which the test reads back from the verdict in
  `recorded_in`), and `rules_status._config_state` matches on `reading` too, so an older reading of the same rule and
  board that becomes the newest one read is not reused under an entry written for another.
- Every entry carries `rationale` (what was compared and why the rule's inputs are unchanged), `summary` (one line for
  the generated page), `method`, `ruled_by` and `ruled_on`. An engineering entry is taken by the session under the
  owner's standing rule of 26 September 2026.

A register that cannot be parsed is an error, and every reading then reads AWAITING_REVALIDATION (cause
REGISTER_UNREADABLE); it is never read as empty.

## Configuration entries (4), 26 September 2026

`rules_status.py` binds configuration since the second round on this stream: a reading is current only when every
configuration input its writer is declared to read (`CONFIG_INPUTS`, each entry audited by reading the tool) is
unchanged since the reading. At `1f614233` four readings that are otherwise current (the netlist or board file they
recorded is the candidate's, the tool is byte for byte the writer) were taken before one configuration input was last
committed. Each change was read and compared (VERIFIED, `git show` of the version in the tree that first recorded the
reading, against the file at `1f614233`); none touches what the tool reads, so each reading is reused as
VALID_HISTORICAL, taken by the session under the owner's standing rule of 26 September 2026:

| rule, board | reading (ts, UTC) | input | recorded in | then | now | what changed after the reading | what the tool reads of it |
|---|---|---|---|---|---|---|---|
| TRN-001, A | `pcb-a-power-a23/routed/port_protect_a.verdict.json` (2026-09-21 18:58:08) | `tools/boards/a.json` | `774736fd` | c688759b926e49c1 | 0fd6672749bc8875 | `ff367886`, `1bf7fca1`: two prose keys added (`_a99r_is_the_control_half_...`, `_a101_is_read_...`) | `external_ports`, `_external_ports_why`, `name` (`port_protect.py:99`, `:228-230`, `:248-251`, `:271-272`): equal |
| TRN-001, B | `pcb-b-compute-b19/routed/port_protect_b.verdict.json` (2026-09-21 18:58:08) | `tools/boards/b.json` | `774736fd` | 3d74adebe8ec0523 | 1a4c6b0ce47d5d42 | `9bd0d629`: one prose key added (`_t1_magnetics_is_a_commercial_temperature_part_why`) | the same three keys: equal |
| MEC-001, E5 | `pcb-e5-block/routed/check_pcb_e5.verdict.json` (2026-09-21 12:52:57) | `tools/boards/e5.json` | `a783ab33` | cb8ea31408f4b343 | 6bc23f492d8bc88d | `7bc4e4c2`: `conformal_coated` and its reason added (ISO-001's column, decision 34) | `copper_layers` (`check_pcb_e5.py:38`): absent in both, so the tool's default of 2 both times |
| RTE-001, E5 | `pcb-e5-block/routed/fab_limits.verdict.json` (2026-09-21 12:53:03) | `../vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md` | `a783ab33` | 1ff75a9a83c909fc | 123b9bf63df2c803 | `d468613e`: 8 lines added, none removed: a correction note that the 2 oz PTH annular floor (0.254 mm) is published | nothing at run time; its constants (`fab_limits.py:33-49`: track and spacing by copper weight, via hole and diameter, NPTH, via in pad) cite the document and no annular ring is among them |

The other inputs of these readings are unchanged since before them (the intent files of A and B, committed 20
September; E5's project file, 4 September), and board E5's footprints were read to confirm the declared zero of its
CMP-001 reading: 17 footprints, all targets, mounting holes and wire lands (`pcb-e5-block/pcb-e5-block.kicad_pcb`,
sha256/16 686b29a734c55b9a), no rated part.

**Since the code bundle (26 September 2026), the two E5 readings above (MEC-001, RTE-001) read TOOL_CHANGED before
their configuration is judged:** a module each writer imports was committed after the reading, so the entry script
alone no longer shows the tool unchanged. Their configuration entries stay as the record of what was compared; they
apply again when the readings are re-taken, or when a `kind: tool` entry answers for the modules that moved. The
readings of TRN-001 on A and B awaited revalidation for other causes already.

Not reused, and why: REL-001 on all seven boards (`reliability.py` records no netlist and picks the newest
`<stem>*/out/<stem>.net` by modification time, `reliability.py:47`, so no rationale can say which netlist it read; and
`faf8c981` added board E's J_TAMP class to `pcb_reliability.yaml` after every reading), and E5's STK-001 (`d468613e`
changed `stackup_write.py`, whose STACKS table the gate compares against, and the order notes it reads were rebuilt in
`29f00554`). Both await a re-take.

## Tool and artefact entries on 26 September 2026: none, and why

Every tool change behind a reading that still decides a required rule-board pair was examined (42 pairs at `1f614233`
with this stream's evidence classes; 37 answered by the writer's own hash, 5 by commit date). For each exact case the
version that wrote the reading was located in git by its sha256/16 and its syntax tree compared with the current
file's, docstrings removed. **None is a documentation-only change**, so no entry can be written honestly:

| writer file | wrote the reading | that version is commit | now | comparison | pairs it decides |
|---|---|---|---|---|---|
| `check_pcb_a.py` | ebc59caeff549765 | `a798f382` | ed09e95458341aa0 | code changed (`168a9dcb`, decision 36 pair tolerance) | A MEC-001 |
| `check_pcb_b.py` | 40bd02191fab1a9e | `a798f382` | e6274969b1525ef3 | code changed (`168a9dcb`, decision 36) | B MEC-001 |
| `check_pcb_e.py` | 928c2e173e7afbe9 | `2750eb8d` | 9eb2cf85f6445e5f | code changed (`faf8c981`, the round-4 E corrections) | E MEC-001 |
| `dc_drop.py` | 41f2d086fb80907b | none: no committed version has this hash, an uncommitted copy wrote it | 0b28f57e0a09a385 | cannot be compared | B, C, D, E, P PI-001 and PI-002 |
| `dc_drop.py` | 99937ee8deef38d8 | `6470c35a` | 0b28f57e0a09a385 | code changed (`06c9eda0`, decision 35 current model) | A PI-001, PI-002 |
| `hardset.py` | af5a0e35d8ecd656 | `97ebaec9` | be29a44c4a592876 | code changed (`52cbada9`, the unrouted list cap) | B PLC-001 |
| `interfaces.py` | 462f21176406879c | none: an uncommitted copy | 314ebb0fd5bd49e4 | cannot be compared | INT-001 on all seven boards |
| `netlist_board.py` | 309086c5bd63d252 | `07e53438` | 0dcead399b4dfa4f | code changed (`6104cb81`, SCH-002 now compares part values and lands: a matching change) | SCH-002 on A, B, C, D, E, P |
| `port_protect.py` | 4cd61075adea9def | `7f82fe8e` | f99d9cfc6698197a | code changed (`caa104a3`, decision 31 clamp judgement) | E5 TRN-001 |
| `return_via.py` | d32e465cef7c5146 | `bff7a4f4` | b61d138e54955dd4 | code changed (`14a43af7`, decision 32) | A, B RET-004 |
| `via_current.py` | 7dc42ecca2119b97 | none: an uncommitted copy | 92ed84ac1612fd54 | cannot be compared | B, C, D, E PI-003 |
| `via_current.py` | 9313a4354608f03a | `d1097434` | 92ed84ac1612fd54 | code changed (`06c9eda0`, decision 35) | A PI-003 |

By commit date only (the readings predate the `writer` field): `hardset-placed` (PLC-001 on A, C, D, E, P), taken 17
and 18 September, before `hardset.py` last changed on 21 September 12:44. A commit date says the order of events and
nothing about what changed, so no entry can be written for these either.

No artefact entry is written. The readings that recorded a netlist other than the current one (25 pairs, cause
NETLIST_MISMATCH) fall in two groups:

| board | netlist the readings recorded | held by commit | pairs |
|---|---|---|---|
| A | 3a1b2e4a7684648d | none (regenerated in a box tree on 21 September) | CMP-001, SCH-004, SCH-005 |
| B | 24a4e4d89b577ae6 | none | CLK-001, CMP-001, SCH-004, SCH-005 |
| C | 48d223ce3eecf2e0 | none | CLK-001, CMP-001, SCH-005 |
| C | ba01b558b949d4f2 | `8ce0b892` (before the round-4 corrections) | TRN-001 |
| D | 52d6155a8cfd0cc6 | none | CLK-001, CMP-001, SCH-004, SCH-005 |
| D | ad23d6e925d06353 | `824ec9d4` | TRN-001 |
| E | 7fb0f4714657251a | none | CLK-001, CMP-001, SCH-004, SCH-005 |
| E | a7784a00cc7a89db | `824ec9d4` | TRN-001 |
| P | 98b7ca3616305d88 | none | CMP-001, SCH-004, SCH-005 |
| P | ab2dc5662cb4eb44 | `a0b707f9` | TRN-001 |

A netlist no commit holds cannot be compared with anything. For the four that a commit holds, the current netlists of
C, D, E and P are the round-4 corrections of `faf8c981`, which change parts and pins by design (reversed clamps, new
protection parts), so the inputs of TRN-001 (every exposed port's clamp) are exactly what changed. For boards A and B
the current netlists were committed on 20 September (`0d1e2ef6`, `8ce0b892`) and the readings of 21 September were
taken on a regenerated copy whose content is not on file; the gates run on netlists alone, so a re-take on the
committed files (runner or box, no layout) is cheaper than any rationale.

Method, reproducible from this tree: for a verdict's `writer`, `git log --format=%H -- v2/ecad/tools/<file>`, then
`git show <commit>:v2/ecad/tools/<file> | sha256sum` until the first 16 hex digits equal the writer's `sha16`, then
`ast.dump` of both versions with each module, class and function docstring removed. The instrument is the writer
file only; a change in a module it imports is not seen (stated on `v2/docs/CURRENT-EVIDENCE.md`).

## Tool entries of 27 September 2026: three, and why

MESHSAT-1357, the second release attempt of layers 1 to 3 (branch `fnd/rel2` from `953f5658`). Layer 3's release check
(`v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md`, finding R5) asked the requirements validator in
`v2/ecad/tools/rules_lib.py` to refuse any SC- id that no session choice of the registry defines. `rules_lib.py` is in
the code bundle of two writers whose readings are current on `953f5658`: `intent_checks.py` (PWR-001 on boards A, D and
E, the `intent_rails` readings of 27 September 2026 00:26 UTC, bundle 5aa3d5157698ae2a) and `derate.py` (CMP-001 on E5,
bundle 4c4fc2aca3d8e542). Any edit of the file changes both bundles, so without an entry `rules_status.py` reads the
four TOOL_CHANGED. The edit cannot reach either writer, and `v2/docs/records/rel2/tool_compat.py` shows it from the
files (output `v2/docs/records/rel2/tool_compat.out`):

| writer | then | now | files of the bundle that moved | what moved in it | reached by the bundle |
|---|---|---|---|---|---|
| `intent_checks.py` | 5aa3d5157698ae2a | 3261e823102e587f | `rules_lib.py` only (c0458c53923d7925, the file at `953f5658`, to 6154bd6c15bdfa6b) | the syntax trees with docstrings removed differ in `validate_requirements` and `main` (its `requirements` command) and in six added names: `SC_CITING_GLOBS`, `_SC_CITED`, `_SC_DRAFT`, `_strings_of`, `session_choice_citing_files`, `undefined_session_choice_citations`; nothing removed | none: no file of the bundle takes any of those names from the module (`intent_checks.py:881` and `:937` import it for the reference prefix, `verdict.py` for the rules' fingerprints, both unchanged) |
| `derate.py` | 4c4fc2aca3d8e542 | 1e03e805d1e67712 | `rules_lib.py` only (the same change) | the same | none (`derate.py:68` imports it for the reference prefix) |

This is a dependency rationale, not the documentation-only one the section above asks of an older tool: the moved file's
change is code, and what makes it harmless to these readings is that nothing the two writers run reaches it. The entries
pin both bundles by content, so any later edit of any file of either bundle stops them applying by themselves. Taken by
the session under the owner's standing rule of 26 September 2026.

**A third entry, for `edge_length.py` (the release finalizer of layers 1 to 3, the same day).** The change was rebased
onto main `91894cd7`, where the consolidated re-take (`8ea7867e`, `5ca81eea`) had made the SI-001 readings of boards A,
B, C, D, E and P current (`edge_length.py`, bundle 9882ad1bc5620724, with `rules_lib.py` at c0458c53923d7925); a render
of the rebased branch read all six TOOL_CHANGED. `v2/docs/records/rel2/tool_compat.py 91894cd7` over those twelve
verdict files (`out/` and `routed/` of each board; output `v2/docs/records/rel2f/tool_compat_edge_length.out`) shows the
same: `rules_lib.py` is the only file of the bundle that moved (c0458c53923d7925 to 6154bd6c15bdfa6b, the same change as
above), and no file of the bundle reaches a changed or added name (`edge_length.py:384` and `:440` call only
`board_facts()`, unchanged). With it, every reading the rules_lib.py change reaches on `91894cd7` reads VALID_HISTORICAL
and counts as current: SI-001 on boards A, B, C, D, E and P through this entry, PWR-001 on the same six and CMP-001 on
all seven through the two above (81 current rows before the rebase, 81 after: 62 CURRENT_CANDIDATE and 19 VALID_HISTORICAL).

<!-- evidence-register: compatibility -->
```yaml
compatibility:
  - kind: config
    rule: TRN-001
    board: a
    input: tools/boards/a.json
    recorded_in: 774736fd
    verdict: pcb-a-power-a23/routed/port_protect_a.verdict.json
    reading: "2026-09-21T18:58:08Z"
    then: c688759b926e49c1
    now: 0fd6672749bc8875
    keys: [external_ports, _external_ports_why, name]
    summary: "boards/a.json gained two prose keys after the reading; the three keys port_protect reads are equal"
    rationale: "ff367886 and 1bf7fca1 added the prose keys _a99r_is_the_control_half_and_it_says_board_a_has_nothing_to_grow_a_fence_from and _a101_is_read_and_the_sense_pre_lay_answers_ana001_where_the_fence_could_not. port_protect.py reads external_ports, _external_ports_why and name (port_protect.py:99, :228-230, :248-251, :271-272), which are equal in both versions."
    method: "git show 774736fd:v2/ecad/tools/boards/a.json against the file at 1f614233, json keys compared"
    ruled_by: session
    ruled_on: 2026-09-26
    authority: "taken by the session under the owner's standing rule of 26 Sep 2026"
  - kind: config
    rule: TRN-001
    board: b
    input: tools/boards/b.json
    recorded_in: 774736fd
    verdict: pcb-b-compute-b19/routed/port_protect_b.verdict.json
    reading: "2026-09-21T18:58:08Z"
    then: 3d74adebe8ec0523
    now: 1a4c6b0ce47d5d42
    keys: [external_ports, _external_ports_why, name]
    summary: "boards/b.json gained one prose key after the reading; the three keys port_protect reads are equal"
    rationale: "9bd0d629 added the prose key _t1_magnetics_is_a_commercial_temperature_part_why. port_protect.py reads external_ports, _external_ports_why and name, which are equal in both versions."
    method: "git show 774736fd:v2/ecad/tools/boards/b.json against the file at 1f614233, json keys compared"
    ruled_by: session
    ruled_on: 2026-09-26
    authority: "taken by the session under the owner's standing rule of 26 Sep 2026"
  - kind: config
    rule: MEC-001
    board: e5
    input: tools/boards/e5.json
    recorded_in: a783ab33
    verdict: pcb-e5-block/routed/check_pcb_e5.verdict.json
    reading: "2026-09-21T12:52:57Z"
    then: cb8ea31408f4b343
    now: 6bc23f492d8bc88d
    keys: [copper_layers]
    summary: "boards/e5.json gained conformal_coated after the reading; copper_layers, the one key check_pcb_e5 reads, is absent in both"
    rationale: "7bc4e4c2 added conformal_coated and _conformal_coated_why (ISO-001's column, decision 34). check_pcb_e5.py:38 reads copper_layers with a default of 2; the key is absent in both versions, so the tool compared the board with 2 copper layers both times."
    method: "git show a783ab33:v2/ecad/tools/boards/e5.json against the file at 1f614233, json keys compared"
    ruled_by: session
    ruled_on: 2026-09-26
    authority: "taken by the session under the owner's standing rule of 26 Sep 2026"
  - kind: config
    rule: RTE-001
    board: e5
    input: ../vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md
    recorded_in: a783ab33
    verdict: pcb-e5-block/routed/fab_limits.verdict.json
    reading: "2026-09-21T12:53:03Z"
    then: 1ff75a9a83c909fc
    now: 123b9bf63df2c803
    additions_only: true
    summary: "the fabricator document gained a correction note on the 2 oz PTH annular floor, a number fab_limits does not judge"
    rationale: "d468613e added 8 lines and removed none: a correction that the 2 oz PTH annular floor, 0.254 mm, is published. fab_limits.py opens no part of the document at run time; its constants (fab_limits.py:33-49) are track and spacing by copper weight, via hole and diameter, NPTH and via in pad, and no annular ring is among them."
    method: "git diff 4b90ba4b d468613e of the document (the version in a783ab33 is 4b90ba4b's), and the constants of fab_limits.py read"
    ruled_by: session
    ruled_on: 2026-09-26
    authority: "taken by the session under the owner's standing rule of 26 Sep 2026"
  - kind: tool
    tool: intent_checks.py
    then: 5aa3d5157698ae2a
    now: 3261e823102e587f
    summary: "rules_lib.py gained the requirements validator's SC- id check; nothing intent_checks.py's bundle reaches moved"
    rationale: "The only file of the bundle that moved is rules_lib.py (c0458c53923d7925 at 953f5658 to 6154bd6c15bdfa6b). With docstrings removed its syntax tree differs in validate_requirements and main and in six added names (SC_CITING_GLOBS, _SC_CITED, _SC_DRAFT, _strings_of, session_choice_citing_files, undefined_session_choice_citations), none removed; no file of the bundle takes any of them from the module (intent_checks.py:881 and :937 use it for the reference prefix, verdict.py for the rules' fingerprints, which are unchanged)."
    method: "v2/docs/records/rel2/tool_compat.py 953f5658 with the intent_rails verdicts of boards A, D and E and E5's derate verdict; output v2/docs/records/rel2/tool_compat.out"
    ruled_by: session
    ruled_on: 2026-09-27
    authority: "taken by the session under the owner's standing rule of 26 Sep 2026"
  - kind: tool
    tool: derate.py
    then: 4c4fc2aca3d8e542
    now: 1e03e805d1e67712
    summary: "rules_lib.py gained the requirements validator's SC- id check; nothing derate.py's bundle reaches moved"
    rationale: "The only file of the bundle that moved is rules_lib.py (the same change as intent_checks.py's entry: validate_requirements and main changed, six names added, none removed). derate.py:68 uses the module for the reference prefix and verdict.py for the rules' fingerprints, neither of which changed, and no file of the bundle takes a changed or added name from it."
    method: "v2/docs/records/rel2/tool_compat.py 953f5658 with E5's derate verdict; output v2/docs/records/rel2/tool_compat.out"
    ruled_by: session
    ruled_on: 2026-09-27
    authority: "taken by the session under the owner's standing rule of 26 Sep 2026"
  - kind: tool
    tool: edge_length.py
    then: 9882ad1bc5620724
    now: 5b817048ed7bc29f
    summary: "rules_lib.py gained the requirements validator's SC- id check; nothing edge_length.py's bundle reaches moved"
    rationale: "The only file of the bundle that moved is rules_lib.py (c0458c53923d7925, the file at 91894cd7, to 6154bd6c15bdfa6b: validate_requirements and main changed, six names added, none removed, as in the two entries above). edge_length.py:384 and :440 call the module's board_facts() only, which did not change, and no file of the bundle takes a changed or added name from it."
    method: "v2/docs/records/rel2/tool_compat.py 91894cd7 with the edge_length verdicts of boards A, B, C, D, E and P (out and routed); output v2/docs/records/rel2f/tool_compat_edge_length.out; script v2/docs/records/rel2f/apply_compat.py"
    ruled_by: session
    ruled_on: 2026-09-27
    authority: "taken by the session under the owner's standing rule of 26 Sep 2026"
```
