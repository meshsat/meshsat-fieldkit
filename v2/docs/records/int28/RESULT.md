# RESULT: the set 28 preparation (MESHSAT-1357, 3 October 2026, branch `fnd/int28` from `f08e1342`)

Prototype design: nothing here has been built, powered or measured. This page records what the set 28 preparation did and found, for
the coordinator who re-bases this branch onto set 27's final commit and promotes set 28. Times are CEST. Every sha is read from the
tree at the time named.

## 0. In short

- Layers 5, 6 and 7's first passes are merged onto the Layer 4 line in the order L5, L6, L7 (three merge commits); two textual
  conflicts (sources.txt, PROCUREMENT.md), both resolved by keeping both layers' additions verbatim, Layer 6's first.
- L5-F01: the three Layer 4 readers that pin the files Layer 5 wrote are brought to the merged tree and regenerated through
  `regen_out.py` (L4-E5's output byte-identical; L4-E11's and L4-E9's regenerated); one consequential re-pin in L4-E7 (its pin of
  L4-E5's script), its output byte-identical.
- L5-F02: the five registry readings bound to PANEL.md are rebound with one evidence entry each; `rules_lib.py requirements` reads 0
  errors; REQUIREMENTS-TRACE.md re-rendered (five entries, five bindings, nothing else); the Layer 3 R2 pages re-rendered (the
  registry's sha and five evidence counts); the decisions page current.
- Layer 6's identity block is in the merged yaml; `part_identities.py check` reads 0 problems on this host once the held sheets are
  staged (section 3).
- PCB-ETA.md reads stale in this worktree as it did at the base: a worker-tree condition (the ETA page renders from gitignored
  journals), not an effect of these layers; left unrendered (section 8, F-1).
- The duplicate "## 8." in PROCUREMENT.md (one per layer) is left as merged, with the renumber prepared and not run (section 8, F-2).
- The module tests: section 4.
- Owed to the coordinator: the re-base and the re-run of `apply_set28.py`, the freeze (with the reqs pins of L4-E10, L4-E12 and
  L4-E13 that the freeze helper does not cover), the box re-takes of section 5, the LAYER-STATUS rows of section 7.

## 1. The merges and the conflicts

| Order | Branch, tip | Commit on fnd/int28 | Conflicts | Resolution |
|---|---|---|---|---|
| 1 | `fnd/l5pwr` 1e18a1ca | `247fa5c6` | none (clean) | |
| 2 | `fnd/l6pwr` eda42b78 | `06dc8275` | none (clean) | |
| 3 | `fnd/l7pwr` 2087060b | `2b759e9e` | `v2/vendor/sources.txt` (both appended after line 485), `v2/docs/parts/PROCUREMENT.md` (both appended a section after section 7) | both sides kept, ours (Layer 6) then theirs (Layer 7), by `resolve_both_sides.py` (PROCUREMENT.md with `--md`, one empty line between the sides, which is Layer 7's own leading blank line that git had folded into the context); asserted: sources.txt = base + Layer 6's 9 lines + Layer 7's 5 lines (485 to 499 lines), PROCUREMENT.md = base + Layer 6's section (6935 characters) + Layer 7's section (4404 characters), verbatim; `v2/vendor/SOURCES.yaml` auto-merged and re-parsed: 18 to 19 top-level keys (`documents_filed_l7pwr` new), `parts` 98 to 114 (Layer 6's sixteen), `owed` 17 to 18, Layer 7's block equal to its branch's |

The common base of the three branches is `2c240414` (L4-E9's consolidation at set 27's candidate); my base `f08e1342` is that line plus
L4-E11's designator fix and L4-E7's rounds 3 and 4. Nothing of either side was dropped or rewritten; the consequence, two sections
numbered 8 in PROCUREMENT.md, is finding F-2.

## 2. The scripts and what each changed

### 2a. `stage_held_sheets.py` (a prerequisite, not in the brief)

A fresh worktree holds no `held/` sheet (gitignored by their terms), and every Layer 4 reader that pins one refuses before anything
else: L4-E5's reproduction chain (`l3batt/runtime.py`, Samsung's INR21700-50E sheet), L4-E11 (TI's BQ25730, TPS4811-Q1, CSD19536KTT,
TPS1663; Nexperia's BUK6Y10-30P; Diodes' DS13012; Vishay's SQJ403EP; AOS's AONS21357; Murata's two), L4-E9 (Littelfuse's 997). The
stager copies each pinned held path from a sibling checkout on this host whose copy has the pinned sha256 (nothing fetched): 43 of 44
pinned paths staged, plus 7 more by their pinned sha (L4-E7's three held Samsung readings and four sheets of other records).
The stager's first version reported Panasonic's ZA sheet (`v2/vendor/power/held/panasonic-za-eehza1h330xp-2017-11-07.pdf`) as missing:
it had read the hash on the line AFTER the path (INA169's `4690d49c`) as that sheet's pin, so the main checkout's copy (`43628e509458b899`,
the pin L4-E7 and its fetch script carry) looked unverified. The sheet was then fetched by L4-E7's own `fetch_held_back.py` from the
address its catalogue reading records (LCSC's copy; sha256 matching, 83496 bytes) and the stager corrected to same-line pins, with
paths that carry no same-line pin left to its sha pass. After that: 44 held paths named, 43 with a same-line pin, all present and
verified, 0 missing; the one without a same-line pin (the ZA sheet) present at its pinned sha.

### 2b. `apply_set28_repins.py` (L5-F01): the pins, old to new (sha256/16)

| File | Pin | Before | After | How |
|---|---|---|---|---|
| `records/l4e5/l4e5_source_control.py` | `CONTRACT` (HW-FW-CONTRACT.md) | `1c211e467d81b8b7` | unchanged | the mechanism: `contract_bytes()` reads the tree's file while it is the pinned one, else the pinned bytes at `CONTRACT_COMMIT = 2c240414` (L4-E9's FROM_COMMIT mechanism); see section 9, D-1 |
| `records/l4e5/l4e5_source_control.out` | | `f9c98ec5c43ada0e` | `f9c98ec5c43ada0e` | regen_out: "already identical" (the output prints no pin; the figures are read where they were written) |
| `records/l4e7/l4e7_stage_settings.py` | `L4E5_PY` (L4-E5's script) | `4315c900db1426f7` | `f171efe8e7ddb1e8` | the one consequential re-pin outside the three named readers (L4-E7 re-runs L4-E5's script as its reproduction 0b); section 9, D-2 |
| `records/l4e7/l4e7_stage_settings.out` | | `acfa35d8bd3a9a07` | unchanged | the output prints no pin; regen_out could not re-prove it: L4-E7's reader refuses (exit 3) on its own panel-lead guard, which L4-E9's register fired before set 28 (F-7); the pin is the current sha of L4-E5's script and the output is the committed one |
| `records/l4e11/l4e11_power.py` | `hwfw` | `1c211e467d81b8b7` | `7b8cb44aeb554791` | the merged contract |
| | `panel` | `b396d028b41e880d` | `3f380ef79c6bc54a` | the merged PANEL.md |
| | `arch` (L4-E9's page) | `0978b101bb4fc572` | `fce14ef53fdafd49` | stale since `f08e1342` re-wrote the page (pre-existing, not the merges'); the same re-pin the freeze helper makes; section 9, D-3 |
| | `reqs` (pcb_requirements.yaml) | `b624ac495650a359` | `435d515f6184f7bd` | after the rebind of 2c |
| | `l4e5` (L4-E5's output) | `f9c98ec5c43ada0e` | unchanged | |
| | need() texts | FW-C08, FW-A14 and PANEL.md's cold-hold sentence as before E11-03 | the texts Layer 5 wrote, quoted from the merged files (the behaviour cell of each row; the section 10 sentence carrying "below 0 C" and "above 3 C") | the fourth, "high = the shore ... nothing charges.", unchanged and kept after a check; each pattern matches its merged text exactly once |
| `records/l4e11/l4e11_power.out` | | `3ac6044c45ed9639` | `70c6408c759fface` after step 2, `648e262f7033bc4b` after the rebind | the diff: the three pins' lines in section 0 and the two "as written" quotes (FW-C08, FW-A14); no figure |
| `records/l4e9/l4e9_power_path.py` | `hwfw` | `1c211e467d81b8b7` | `7b8cb44aeb554791` | |
| | `ifaces` (pcb_interfaces.yaml) | `9ec50ccfae3b70a0` | `22aeae7530c8f523` | |
| | `l4e11` (L4-E11's output) | `3ac6044c45ed9639` | `70c6408c759fface` after step 2, `648e262f7033bc4b` after the rebind | |
| | `reqs` | `b624ac495650a359` | `435d515f6184f7bd` | |
| | `l4e5`, `l4e7r` | unchanged | unchanged | guards: re-pinned only if those outputs change |
| `records/l4e9/l4e9_power_path.out` | | `09bbb34345d80597` | `b760cb3af1444b36` after step 2, `41530bb0ba320fb9` after the rebind | the diff: the pins' lines in section 0 only |
| `records/l5pwr/l5pwr_contracts.out` | (prints l4e9out, l4e11out) | printed `cb25ecbb1f210924` and `e287cbffb247de4a` (the outputs at its base `2c240414`) | `918577e4164a0084` | the reader prints the shas of what it read and binds through regen_out; test_l5pwr's "output reproduced" failed from the merge onwards (my base `f08e1342` already carried other L4 outputs) and after the regenerations; regenerated last (section 4) |
| `records/l7pwr/l7pwr_fans_th1.out` | (prints reqs) | printed `b624ac495650a359` | `cd1f8842af426285` | the same: the registry's sha after the rebind; regenerated last |

Order of every run: L4-E5, L4-E7, L4-E11, L4-E9, then Layer 5's and Layer 7's outputs, each through `_bin/regen_out.py` (two runs,
byte-identical, every printed pin the tree's). The L4-E9 pins that are NOT re-pinned here and belong to the freeze: none went stale by this preparation (L4-E10's, L4-E12's
and L4-E13's outputs are unchanged on this branch); they go stale when the coordinator re-pins `reqs` in those three readers and
regenerates them (section 6).

### 2c. `apply_set28_rebind.py` (L5-F02)

CFL-001, CFL-005, CFL-014, CFL-015 and CFL-016: `v2/docs/PANEL.md@b396d028b41e880d` to `@3f380ef79c6bc54a` (the page of `89b9ac6b`
found in the history by its sha), one evidence entry each (the file's path first; of the page's 12 sections one differs, section 10, and
11 are byte-identical; the sentence replaced and the four sentences written quoted; what the record rests on and that it is
byte-identical: CFL-001 sections 1 and 2, CFL-005 section 7, CFL-014 the strap, VSYS and bench-question sentences, CFL-015 the pack
SMBus lead sentences, CFL-016 sections 1, 6 and 7; re-deciding nothing). `evidence_result` PASS unchanged on all five; only those five
records changed, each by `evidence` and `evidence_bound_to`; the entries carry no word the ENV-002 claims screen counts. A second run
refuses "already applied".

### 2d. The regeneration runs

Four `--write` runs were needed on this branch, each logged in the preparation session's scratch area and summarised here: run 1 refused at
L4-E5 (no held sheets in the worktree: `l3batt/runtime.py` could not find Samsung's INR21700-50E sheet; 2a answers it); run 2 regenerated
L4-E5 "already identical" and refused at L4-E11 on its stale `arch` pin (F-4; D-3 answers it); run 3 regenerated L4-E5 (identical), L4-E11
(`70c6408c759fface`) and L4-E9 (`b760cb3af1444b36`), the step 2 commit `8d6e1df8`; run 4, after the rebind, re-pinned `reqs` in L4-E11 and
L4-E9 and regenerated L4-E11 (`648e262f7033bc4b`) and L4-E9 (`41530bb0ba320fb9`), the step 3 commit `a8b03c1a`. L4-E7's output was
then run on its own through regen_out: REFUSED, both runs exit 3 on L4-E7's own guard (F-7), the committed output left unchanged; the step 2b commit `d34d030e` carries the pin. Every regeneration: two runs byte-identical, every printed
pin the tree's, the committed file replaced atomically or left as it was.

## 3. The check lines

| Check | At the base `f08e1342` | After the merges | After the rebind and re-pins |
|---|---|---|---|
| `rules_lib.py requirements` | 145 records, 0 errors | 5 errors (the five CFL rows bound to PANEL.md at `b396d028`) | **145 requirement record(s), 0 error(s), 0 warning(s)** |
| `rules_render.py --requirements --check` | current | REFUSED (the registry does not validate) | **REQUIREMENTS-TRACE.md is current** (re-rendered: 4659 lines; the diff is five entries, five bindings, five separators) |
| `rules_render.py --check` | 7 documents, 1 out of date (PCB-ETA.md) | 6 documents, 1 out of date, 1 refused | **7 document(s), 1 out of date: PCB-ETA.md**, the same as at the base (F-1); CURRENT-EVIDENCE.md not rendered here (no audit in a worker tree) |
| `decisions_render.py --check` | current (exit 0) | current | **current (exit 0)** |
| `handover/layer3/render_l3r2.py --check` | 3 pages, 0 out of date | 3 pages, 0 out of date (the pages print the registry's sha, unchanged by the merges) | after the rebind: REQUIREMENTS-L3-R2.md out of date (test_l3r2 found it); re-rendered: **3 page(s), 0 out of date**; the diff: the header's registry sha `b624ac495650a359` to `435d515f6184f7bd` and the five records' evidence counts (26 to 27, 49 to 50, 24 to 25, 32 to 33, 95 to 96), nothing else; the commit `step 3b`. Every registry commit since `e5286397` re-rendered this page with the trace, so this is the recipe, not a reopening of Layer 3 (the acceptance binds the normative digest, which an evidence entry does not move) |
| `part_identities.py check` | boards c, 175 rows, 87 selections, READ 18, UNREAD 16, DECODED 10, 16 problems (exit 1): the 16 held-back sheets not on this host | | **boards c, 175 rows, 87 selections, 0 rows uncovered, RESOLVED bindings READ 21, DECODED 23, 0 problems (exit 0)**: the held sheets staged by 2a, the Layer 6 block outside `selections:` as designed |
| `l6pwr/apply_part_identities_block.py --check` | | | "already carries drafted_identities_l4_power: a second application is refused" (exit 3, the designed answer after the merge) |

## 4. The module tests

### 4a. The full run of the brief's 26 files

`env -C v2/ecad/tools/tests python3 run.py test_requirements test_l3r2 test_l3r4 test_l3r5 test_l3am test_l3_reaccept test_public_hygiene
test_l4e4_provisional test_l4e4 test_l4e5 test_l4e6 test_r11dep test_l4e7 test_l4e8 test_l4e9 test_l4e10 test_l4e11 test_l4e12 test_l4e13
test_l4close test_l4e_svg_readers test_l5pwr test_l6pwr test_l7pwr test_interfaces test_part_identities`, in the background with no timeout,
04:43 to 07:34 CEST (2 h 51 min on the shared host at load 13 to 15, beside the coordinator's freeze regenerations), on the tree at
`d34d030e` (before step 3b's re-render, the test restatement and the Layer 5/7 regeneration below):

**`tests: 403 passed, 105 failed, 1 skipped`**

| File | PASS | FAIL | SKIP | The failures, in one line |
|---|---|---|---|---|
| test_interfaces | 10 | | | |
| test_l3am | 8 | | | |
| test_l3r2 | 26 | 1 | | `t_l3r2_check_refuses_a_hand_edited_copy`: REQUIREMENTS-L3-R2.md stale (it prints the registry's sha) |
| test_l3r4 | 15 | | | |
| test_l3r5 | 21 | | | |
| test_l3_reaccept | 3 | | | |
| test_l4close | 14 | | | |
| test_l4e10 | 2 | 20 | | every predicate that runs the reader: `l4e10_cell_thermal.py refused (exit 2)` |
| test_l4e11 | 50 | 1 | | `t_the_charge_holds_are_a_state_table...`: "FW-C08 as written no longer asserts SHORE_INHIBIT on the cold hold" |
| test_l4e12 | 2 | 24 | | every predicate that runs the reader: `l4e12_thermal.py refused (exit 2)` |
| test_l4e13 | 1 | 18 | | every predicate that runs the reader: `l4e13_panel.py refused (exit 2)` |
| test_l4e4 | 12 | | | |
| test_l4e4_provisional | 2 | | | |
| test_l4e5 | 17 | | | (L4-E5's mechanism, D-1, holds: the output reproduced, the draft applies once to the base) |
| test_l4e6 | 13 | | | |
| test_l4e7 | 4 | 39 | | every predicate that runs the reader: `l4e7_stage_settings.py refused (exit 3)` |
| test_l4e8 | 19 | | | |
| test_l4e9 | 53 | | | (the re-pinned reader; its output reproduced) |
| test_l4e_svg_readers | 2 | | | |
| test_l5pwr | 11 | 1 | | `t_output_reproduced_byte_for_byte`: the output printed the shas of L4-E9's and L4-E11's pages and outputs at its base `2c240414` |
| test_l6pwr | 10 | | | |
| test_l7pwr | 10 | 1 | | `t_output_reproduced_byte_for_byte`: the output printed the registry's sha before the rebind |
| test_part_identities | 27 | | | |
| test_public_hygiene | 4 | | | |
| test_r11dep | 2 | | | |
| test_requirements | 65 | | 1 | `t_no_real_record_reads_pass_on_evidence_that_does_not_count` SKIP: out/rule-audit is not in a worker tree |

### 4b. Every failure, its cause and its disposition

| Cause | Failures | Disposition |
|---|---|---|
| REQUIREMENTS-L3-R2.md stale after the rebind (the Layer 3 R2 pages print the registry's sha and the records' evidence counts; every registry commit since `e5286397` re-rendered them with the trace) | test_l3r2, 1 | FIXED here: `render_l3r2.py` re-rendered (step 3b, `0d9d0b3d`; the driver's step 3b and check 6e); re-run in 4c |
| A predicate pinned the pre-E11-03 wording of FW-C08 ("below 0 C" in the quoted cell) and failed on the day Layer 5 restated the row: a rule about history | test_l4e11, 1 | FIXED here: restated as a property (D-7): the quoted "as written" text IS the contract's FW-C08 behaviour cell read from the tree, and the cell is in one of the two states the record knows (the cold hold on SHORE_INHIBIT, U4-F1 open; or never for a temperature hold, U4-F1 resolved by E11-03); re-run in 4c |
| The Layer 5 and 7 readers print the shas of what they read (L4-E9's and L4-E11's pages and outputs; the registry) and bind their outputs through regen_out; L4-E9's and L4-E11's outputs were regenerated and the registry rebound, and the pages at my base already differed from their base `2c240414` | test_l5pwr 1, test_l7pwr 1 | FIXED here: both regenerated through regen_out (`l5pwr_contracts.out` `918577e4164a0084`, `l7pwr_fans_th1.out` `cd1f8842af426285`; the diff of each is its section 0's shas, no figure); the re-pin script's last stage; re-run in 4c |
| L4-E10, L4-E12 and L4-E13 pin `pcb_requirements.yaml` at `b624ac495650a359` and refuse after the rebind (`435d515f6184f7bd`); L4-E10 also pins L4-E9's page at `0978b101` and L4-E13 L4-E7's output at `b0d0953e`, both stale since `f08e1342` (F-4) | test_l4e10 20, test_l4e12 24, test_l4e13 18 | NOT fixed here, by the brief (the three named readers only): the coordinator's freeze with the reqs re-pin (section 6 item 2); every one of the 62 is the reader's refusal, not a predicate of the record |
| L4-E7's reader refuses (exit 3) on its own panel-lead guard, fired by L4-E9's register row R-180 since `2c240414` (F-7) | test_l4e7, 39 | NOT fixed here: L4-E7's author (the guard greps prose and reads its own figure quoted back); the freeze's stability pass meets it too |
| `out/rule-audit` is gitignored and not in a worker tree | test_requirements, 1 SKIP | the box (the suite's own condition) |

### 4c. The re-run of the four fixed files

RERUN

## 5. The box re-takes owed (the coordinator's)

| Reading | Why | Where |
|---|---|---|
| `interfaces.py` on every board (A, B, C, D, E, P, E5) | `pcb_interfaces.yaml` is a CONFIG_INPUT of `interfaces.py` and moved `9ec50ccfae3b70a0` to `22aeae7530c8f523` (Layer 5's power contracts); the seven tracked readings `v2/ecad/pcb-*/routed/interfaces_*.verdict.json` pin the old sha | the box, `retake_schematic_phase.py` as after H2 (L5-F02's second half) |
| the identity readings (stream w5identc, `records/w5identc/readings/check-board-c-b874b744.json` pins `pcb_part_identities.yaml` at `1f4c513cf50bccfb`) | the yaml carries Layer 6's block (outside `selections:`; `part_identities.py check` reads the same selections, so the re-take is expected to repeat the reading with the new file sha) | the box with the held sheets |
| `rules_status.py` (the readiness audit, CURRENT-EVIDENCE.md, the per-board status pages, PCB-ETA.md) | `pcb_requirements.yaml` changed (five evidence entries and bindings; the registry's digest moves), `pcb_interfaces.yaml` changed | the box suite's two passes, then the renderers on the box |
| L4-E10, L4-E12, L4-E13 regenerated | each refuses (exit 2) on `v2/ecad/tools/pcb_requirements.yaml is not the pinned file` after the rebind (read on this tree, 3 October 07:35), their `reqs` pin `b624ac495650a359` against `435d515f6184f7bd`; L4-E10 and L4-E11 also pinned L4-E9's page (L4-E10's still does) and L4-E13 L4-E7's output (both pre-existing at `f08e1342`) | desk, the freeze helper plus the reqs re-pin (section 6) |

## 6. What remains for the coordinator

1. **The re-base onto set 27's final commit** (L4-E11's fan-feed round `af4672f4` merged, the pin-chain freeze). Then
   `python3 v2/docs/records/int28/apply_set28.py`: it stages the held sheets, re-runs the rebind (the five rows at set 27 are still
   bound to `b396d028`), checks the registry, re-renders the trace page and the Layer 3 R2 pages, re-runs the re-pins with every sha read from the tree (L4-E11's
   `arch` pin will already be the freeze's; L4-E5's mechanism is in place), checks the identity block and the renderers. If the re-base
   replays the merges, `resolve_both_sides.py` resolves the same two files the same way.
2. **The freeze** (`_bin/freeze_l4_chain.sh`) after the re-base, with one addition it does not make: re-pin `pcb_requirements.yaml`
   (`b624ac495650a359` to the tree's) in `l4e10_cell_thermal.py`, `l4e12_thermal.py` and `l4e13_panel.py` before regenerating them; the
   helper then re-pins L4-E9's pins of their outputs and regenerates L4-E9 (and its stability pass covers L4-E7, whose output is
   byte-identical after 2b).
3. **The box re-takes** of section 5, then the renderers on the box (PCB-ETA.md, F-1).
4. **PROCUREMENT.md's two sections numbered 8** (F-2): run `apply_set28_procurement_renumber.py --write` or leave it.
5. **The LAYER-STATUS rows** of section 7, the integrator's to set.
6. **L4-E9's round 5** as planned (re-pin L4-E10/E11/E12, L4-E12's fan register row, the U rows): the brief's own item, outside this
   preparation.

## 7. Proposed LAYER-STATUS rows for Layers 5, 6 and 7 (the integrator sets them; texts in the page's own form)

Each row is `| Item | Acceptance item (short) | After set 28 | Evidence, or what remains |`, composed from the three records' own
"criteria moved" sections (`records/l5pwr/L5-POWER-CONTRACTS.md` section 6, `records/l6pwr/L6-POWER-PARTS.md` section 4,
`records/l7pwr/L7-FANS-AND-TH1.md` section 6). A row not listed keeps its H2 text. No state is raised to MET by these passes.

### Layer 5. Partitioning and interfaces (header: "At set 28: IN_PROGRESS; Layer 5's power pass, records/l5pwr, wrote Layer 4's power results into the three contract files; no release check has judged this layer")

| 5.2 | every interface owned at both ends with its connector | PARTLY | further: IF-AE-DOCK, IF-PE-PACK, IF-AB-POWER and IF-EXT-USB carry every pass-2 field (hc5's `check_contract_fields.py --all`; IF-EXT-USB gained its `ends`; `records/l5pwr`); eight of the first twelve still lack them; the IDC headers' MPNs (EQ-21); E5's end has no part or src (no schematic, L5-F08) |
| 5.4 | electrical levels stated per interface | PARTLY | further: the power interfaces' levels with their Layer 4 basis and marks (IF-EXT-DC both inputs, IF-AE-DOCK, IF-PE-PACK, IF-EXT-USB, IF-E-FANS; `records/l5pwr`); the kit I2C bus's three segments (SC-59); the rest as at `e3aedb25` |
| 5.5 | power capacity of each power interface with margin | PARTLY | further: IF-EXT-DC's currents against the breaker, the fuses and the interconnect; IF-AE-DOCK's in-service and fault currents against the 9 A pins and pin 1 against the 813 under U42; the outlet's trip against its 3 A contracts and the 5 A receptacle; the PoE monitor's scale (`records/l5pwr`); open: I-03's PS-ALLTX (INCONCLUSIVE at both ends), E5's targets and the ground share (S-74, S-75), the ribbon and SMP-MAX ratings, the 813's pulse capability (E11-38: Layer 7's bound on published relations and its drafted maker question, `records/l7pwr` section 4) |
| 5.6 | sequencing across interfaces | PARTLY (from OPEN) | L4-E9 section 4's source changes, startup, shutdown and faults as sequencing fields; the fans' start (FW-E11), the shedding sequence (FW-A21), the boot writes (FW-A23); `power_line_states` (`records/l5pwr`); the SLOT_EN hold still in no generator (OWED, Layer 8, board C or A; L5-F06), so H2's named item stays open; HOT-R1 (S-57, EQ-22) |
| 5.7 | reset, default and cable-out states for every control line | PARTLY | further: every power line of L4-E9 section 4 has its reset, default and cable-out state and its firmware row (`records/l5pwr`); TX_INHIBIT_n's fail-safe level (EQ-25); the rest as at `e3aedb25` |
| 5.11 | firmware obligations affecting hardware explicit | PARTLY | further: FW-A19 to FW-A23, FW-C15, FW-E11 to FW-E13 added; FW-A09, FW-A14, FW-A16 and FW-C08 restated; PANEL.md section 10 restated (E11-03); V-A11, V-C15, V-E11 to V-E16; the reduced-mode duties of layer 2's m13; the SGP41's switch and carrier TMP117 not drawn (FW-E12 over parts OWED, L5-F03) |
| 5.13 | interface contracts consistent with the tree | PARTLY | the drawn board first, every draft DRAFTED with its register row; `check_contracts.py` PASS 99 of 99 unchanged before and after the pass; `pcb_interfaces.yaml` at `22aeae7530c8f523` is a CONFIG_INPUT of `interfaces.py`, so its readings on every board await their re-take (set 28's box re-takes) |

Not moved by set 28: 5.1, 5.3 (MET, the same reading before and after), 5.8, 5.9, 5.10, 5.12, 5.14, 5.15.

### Layer 6. Components (header: "At set 28: IN_PROGRESS; the power parts Layer 4 selected are identified and sourced by records/l6pwr; the fans by records/l7pwr; nothing reselected, nothing on a committed netlist")

| 6.1 | exact manufacturer, MPN, package and grade per fitted part | **OPEN**, toward PARTLY for the power parts | the 28 power parts of L4-E5 to L4-E11: 14 RESOLVED on a page that prints the part number, 14 UNRESOLVED with their reason, grades read at the source for 21, in the block `drafted_identities_l4_power` of `pcb_part_identities.yaml` (outside `selections:`, on no committed netlist; `records/l6pwr`); the fans Sanyo Denki 9WL0612P4H001 and 9WPA0412P6G001 selected with their makers' pages (`records/l7pwr`); board C's slice as at H2; the rest as at H2 (no MPN field, EQ-21) |
| 6.2 | supporting documents with revision, source and currency | PARTLY | further: 17 makers' documents named with title, revision, URL and sha256 (10 held back under their terms with `records/l6pwr/fetch_held_back.py`, every one fetched and matching on 3 October 2026), Samsung's pages excerpted; Layer 7's five filed (Sunon's IP56/68 brochure, Same Sky's CFM-60BG68 sheet, Sanyo Denki's pages transcribed, Raspberry Pi's cooler brief, Preci-Dip's SLC catalogue; `documents_filed_l7pwr`); owed: the ZK sheet's URL, Samsung's MLCC catalogue, Milliohm's HoLLR sheet, Nexperia's packing legend (SOURCES.yaml `owed`), the 35E maker copy; the documents START-HERE section 8 names are not held |
| 6.3 | selection rationale recorded | PARTLY | further: one sentence per power part pointing at its Layer 4 decision (`records/l6pwr`); the fans' selection row by row with its authority fields and alternative (`records/l7pwr` section 2); not for the passive and connector majority |
| 6.6 | procurement constraints and alternatives | PARTLY | further: dated readings for 32 codes, an alternative or NOT READ per part, the five-kit need against stock (`PROCUREMENT.md` section 8, Layer 6; two stock pools read); the fans' and the T-H1 set's dated readings (`PROCUREMENT.md`, Layer 7's section); the eleven findings L6P-F01 to L6P-F11 with the Layer 4 row each affects, of which L6P-F01 (the R221 collision) is answered by L4-E11's R228 (`787e7b15`) and L6P-F04 and L6P-F10 by L4-E7's round 4 (`f73b07ea`); HX6096NL's readings not filed |
| 6.8 | a current, versioned BOM with identity per board | PARTLY | NOT MOVED: the power parts are on no committed BOM; their identities are staged for the Layer 8 regeneration (`apply_part_identities_block.py --write` after any `build_table.py` run); the H2 NOT_FOR_FAB BOMs as at H2 |

Not moved by set 28: 6.4, 6.5, 6.7, 6.9, 6.10, 6.11.

### Layer 7. Mechanical and enclosure (header: "At set 28: IN_PROGRESS; records/l7pwr settles the fans (D-18), specifies the T-H1 mock-up with its bill and bounds the dock lead's pulse capability; nothing built")

| 7.5 | connector, cable and service access | PARTLY | the connector plate (C3) drawn; the jumper plug (M17g, M17x) and the sealed RJ45 open; the dock lead's pulse and duty capability bounded on published relations (Onderdonk, Preece, ECSS Annex C; `records/l7pwr` section 4), its wire's maker rating owed; the 813 contact's current-time capability a drafted maker question (`records/l7pwr/clarification/preci-dip-813.txt`, not sent) |
| 7.8 | thermal interfaces specified | PARTLY | the PA flange sensor drawn on D (`76235aad`); the five IP68 fans picked (D-18 settled by the session, `records/l7pwr`: Sanyo Denki 9WL0612P4H001 mixers on board E, 9WPA0412P6G001 cooler fans on board B), their regulated 12.0 V feed a Layer 8 finding (no maker's range covers VSYS_E or the 5 V slot rail; L4-E11's section 18 drafts the mixers' rail on `fnd/l4e11`), their mounting a CAD item; the conductance (EQ-05) waits on T-H1 |
| 7.9 | critical fit uncertainties resolved by suitable evidence | **OPEN** | FEA-007: the mock-up (L-07, EQ-08) and the desk items; the empty-case T-H1 mock-up specified with its complete bill (`records/l7pwr/T-H1-MOCKUP-SPEC.md`: EUR 639.76 excl. VAT, GBP 887.00, USD 147.38 read on 3 October 2026, four items to quote), so the owner's purchase decision has prices; a new fit item: the cooler fan's 2.76 mm (0.32 mm) to the backer |
| 7.10 | later physical checks allocated, deferral justified | PARTLY | FEA-007 stages the YES rows at layout entry on the decision they move; FEA-004's heat-test staging stays in CONTINUATION-BRIEF 5.1's misplacements; the heat test T-H1 is allocated to the prototype bench with its specimen, bill, pass lines and the owner's authorisation named (`records/l7pwr`, `records/l4e12/T-H1-PROCEDURE-DRAFT.md`) |

Not moved by set 28: 7.1 to 7.4, 7.6, 7.7, 7.11 to 7.17.

## 8. Findings of this preparation

| ID | Finding | Owner, next action |
|---|---|---|
| F-1 | `rules_render.py --check` reads `PCB-ETA.md differs from what the registry renders` at the base `f08e1342` and after every step here. The ETA page renders from gitignored journals (the run history) a worker tree does not hold, as `rules_render.py`'s own `requirements_main` docstring states, so a render here would replace the committed page with a thinner one; not rendered. Not an effect of Layers 5, 6 or 7 | the coordinator: render on the box at promotion |
| F-2 | PROCUREMENT.md carries two sections headed "## 8." (Layer 6's power parts, then Layer 7's fan picks); both records, Layer 7's README and test_l7pwr name "section 8". Kept as merged (no content rewritten); `apply_set28_procurement_renumber.py` renumbers Layer 7's to 9 with its three mentions and the test's assertion | the integrator decides; one command |
| F-3 | L4-E5's reader needs four pre-draft texts of FW-A16 and FW-E04 and captures the record's figures from them; L4-E5's own draft (applied by Layer 5 as register row R-23 assigns) removed them from the tree. Re-pinning the CONTRACT key to the merged file cannot work; the record now reads the contract where it analysed it (D-1). A round of L4-E5 that restates its reading on the restated rows would retire the mechanism | Layer 4, when L4-E5 is next opened; no action needed for set 28 |
| F-4 | L4-E11's pin of L4-E9's page (`0978b101`) and L4-E10's were already stale at `f08e1342` (the consolidation round 3 re-wrote the page), as was L4-E13's pin of L4-E7's output (`b0d0953e` against `acfa35d8`, L4-E7's rounds 3 and 4): L4-E11 and L4-E13 refused on the base before any merge. L4-E11's is re-pinned here (D-3); L4-E10's and L4-E13's are the freeze's | the coordinator's freeze |
| F-5 | The stager's first association of a pin to Panasonic's ZA sheet was wrong (the next line's hash, INA169's); the sheet was fetched by L4-E7's own `fetch_held_back.py` (sha matching) and the stager corrected (2a). No record was wrong | closed here; a fresh worktree runs the stager, and a record's own fetch script where a sheet has no local copy |
| F-7 | L4-E7's reader refuses on the integrated line: its guard walks every .md and .yaml under v2 (vendor, release, l4e7 and out left out) and refuses when a text names a solar or panel lead, cable or extension within 120 characters of a length in metres, so that no other document states the panel lead's length it derives from a1solar's 5 m estimate. L4-E9's register row R-180 (`DOWNSTREAM-REGISTER.md` line 268, `L4-POWER-ARCHITECTURE.md` line 471) restates L4-E7's own round 2 result ("two conductors 6.09 mm apart over 5 m") and says in the same sentence that "a vehicle or shore lead in the panel's receptacle is not the kit's panel lead"; the guard reads that restatement as a document stating the length. The row is in both files at `2c240414` and `f08e1342`, so the refusal predates set 28 (L4-E7's output at `acfa35d8` was printed on `fnd/l4e7`, where the row did not exist) and the freeze helper's stability pass over L4-E7 will meet it. A detector that greps prose, firing on its own figure quoted back | L4-E7's author: restate the guard on the derivation's own input (a1solar's figure, by file and pin) or exempt the records that cite L4-E7 by row; the coordinator's freeze meanwhile notes L4-E7 as not regenerable on the line |
| F-6 | A fresh worktree holds none of the held sheets and every Layer 4 reader refuses first on that; the readers' tests then fail on the host for the sheets, not for the records. `stage_held_sheets.py` answers it from local copies; a fetch script per record exists | every fresh worktree: run the stager first |

## 9. Decisions taken (authority: SESSION, under the owner's standing rule of 26 September 2026; none asks the owner)

| ID | Decision | Why | Reversed by |
|---|---|---|---|
| D-1 | L4-E5 reads HW-FW-CONTRACT.md where it analysed it: the tree's file while it is the pinned one, else the pinned bytes at `2c240414` (`contract_bytes()`, the FROM_COMMIT mechanism of L4-E9 and L4-E11); the pin value unchanged, no prose or figure changed, the output byte-identical | the brief's re-pin to the merged file refuses at "FW-A16's rule not found": the restated FW-A16 no longer prints the 9/12/24 V figures, O-33's 54 and 93 W or the "3.25 A at every adapter removal" clause, and FW-E04 no longer says "for FW-A16"; those captures are the record's figures, which this preparation may not change. The record's "as written" now means as written at `2c240414`, before its own draft was applied | a round of L4-E5 restating its reading on the restated rows (F-3) |
| D-2 | L4-E7's pin of L4-E5's script re-pinned (`4315c900` to `f171efe8`), the only pin outside the three named readers | the pin was current at the base and stale only because of D-1; L4-E7 re-runs L4-E5's script as its reproduction 0b and its output prints no pin, so the output stays byte-identical (proved by regen_out, 2d) | reverting D-1 |
| D-3 | L4-E11's `arch` pin re-pinned to L4-E9's current page | stale since `f08e1342` (F-4); without it L4-E11 cannot regenerate on this branch, and the brief asks for its regeneration; it is the same re-pin `freeze_l4_chain.sh` makes for L4-E11, so the freeze finds it already made | the freeze helper, which makes the same change |
| D-4 | The two "## 8." headings kept as merged; the renumber prepared, not run (F-2) | the brief: no content of either side dropped or rewritten; the renumber touches Layer 7's page, README and test | the integrator running the prepared script |
| D-5 | The held sheets staged from sibling checkouts by their pinned sha; one (Panasonic's ZA) fetched by L4-E7's own `fetch_held_back.py` from the address its catalogue reading records, sha matching | the readers refuse without them; a local verified copy is the same bytes the fetch checks; a maker's public document fetched by the record's script is not an outside contact | removing the ignored `held/` folders |
| D-7 | test_l4e11's predicate on FW-C08 restated as a property (the quoted cell is the contract's, read from the tree, and in one of the two states the record knows) | it pinned the pre-E11-03 wording and failed on the day Layer 5 restated the row: a rule that fails when its subject is fixed is a rule about history; the brief: restate it as a property | a Layer 4 round that re-reads L4-E11 on the restated contract may tighten it to the resolved state alone |
| D-6 | The reqs pins of L4-E9 and L4-E11 re-pinned after the rebind (the brief's step order 2 then 3 kept in the commits; the re-pin run repeated after the rebind) | both readers pin `pcb_requirements.yaml`, which the rebind changes; `apply_set28.py` runs the rebind first | none needed |

## 10. Not claimed

No hardware result; no test of the Layer 4 to 7 engineering; the module tests of section 4 establish their tested behaviour on this
host only; the box re-takes and the freeze are not done; PCB-ETA.md and CURRENT-EVIDENCE.md are not rendered here; the AI checks of the
three layer records are not re-done; nothing was bought, sent or published.
