# Independent check of stream w5si2 (AI review), 28 September 2026

AI review by a checker session that wrote none of what it checked. It is not a qualified engineering review.
Prototype design work: nothing has been built, ordered or measured. MESHSAT-1357, layer 9, rule SI-001.

Checked: branch `fnd/w5si2`, tip `f84243ba`, worktree `/home/claude-runner/worktrees/meshsat-fieldkit/w5si2`
(read only), base `85ad1193`. Integration line `fnd/int8`, at `097b6cf7` when the check began and at `a8607eab`
when it ended (five commits of the Codex pilot's records, `pcb_interfaces.yaml` and `pcb_requirements.yaml`).
Everything I wrote is under `/home/claude-runner/worktrees/meshsat-fieldkit/_scratch/chk-w5si2/`. No worktree and
no main checkout was written; no gate, `rules_status.py` or renderer was run in any tree other than my scratch
clones; nothing on the rented box; no network (the fetch script was not run).

Times are from `date` on the runner: started 19:43 CEST, this page finished at 20:07 CEST.

## 1. The merge as it will happen

Scratch clone `view/` (`git clone --shared`), branch `chk` from `origin/fnd/int8` at `097b6cf7`,
`git merge --no-ff origin/fnd/w5si2`.

Result: three conflicts, all append-append at the end of a file (both branches added lines after the same last
line of the base). Each has ONE hunk:

| File | HEAD side (int8) | w5si2 side | Nature |
|---|---|---|---|
| `.gitignore` lines 36 to 44 | the `AGENTS.md` rule with its two comment lines (Codex worker) | the `v2/vendor/*/ibis/*.ibs` rule with its two comment lines | mechanical: keep both |
| `v2/vendor/sources.txt` lines 349 to 376 | 12 lines: `materials/`, `qrp-labs/`, `standards/mil-std-810h-method-514-8.md` (stream w5tray) | 13 lines `ti/ibis/*.ibs` and `st/ibis/...ibs`, each "NOT IN THE REPOSITORY ..." | mechanical: keep both |
| `v2/vendor/vendor-status.txt` lines 268 to 295 | 12 lines, the same w5tray files | 13 lines, the same models, `current` | mechanical: keep both |

I resolved all three by keeping both sides, HEAD's lines first, and committed (`9d99f551` in the clone). Check:
`git diff --stat origin/fnd/w5si2 HEAD -- <the three files>` shows only int8's 3 + 12 + 12 added lines. No other
file conflicted; the registry and the trace page did NOT conflict (the stream changes neither on the branch, its
registry changes are the drafts). Model files in the clone: `git ls-files | grep -c '\.ibs$'` = 0, on disk 0.

Rehearsed again at int8's new tip `a8607eab` in a second clone (`int8-plain/`, branch `chk2`): the same three
files, the same single hunks at the same lines. Resolved the same way; the seven drafts then applied there in the
absent state (all exit 0, decisions 48 to 54, CFL-016 rebound `b5f7162443d5ad91` to `4e1ff91f98e06b72`) and
`rules_lib.py requirements` read 144 records, 0 errors; `rules_lib.py` 59 rules, 0 errors.

## 2. The drafts, both model states

### 2a. No model present (clone `view/`, after the merge)

The seven drafts run in the author's order, each `--root <clone>`, from outside the clone:

| Draft | exit | Its first line (as printed) |
|---|---|---|
| 1 `apply_rules_status_config_inputs.py` | 0 | `rules_status.CONFIG_INPUTS['edge_length.py']: 64 inputs (6 before): the data file, the manifest that pins the makers' models, 50 document(s), 1 listing, 6 netlists; no model is declared` |
| 2 `apply_rules_status_pinned_models.py` | 0 | `rules_status.py: PINNED_INPUTS, _recorded_model and _pinned_state added above _config_state, which asks _pinned_state before it answers BOUND (61 lines added)` |
| 3 `apply_sources_yaml_ibis.py` | 0 | `SOURCES.yaml: 9 document rows and one owed line added, every address, revision and sha256 read from v2/vendor/ibis-manifest.yaml; the models in this tree: ABSENT (0 of 13 present)` |
| 4 `apply_board_b_declarations.py` | 0 | `board B: SW?_IN and SW?_O? declared RF and BOB's basis corrected (its class kept); gen_pcb_b3.py PATTERNS 40 entries become 41: ...` |
| 5 `apply_board_c_declarations.py` | 0 | `boards/c.json: signal_classes 50 entries (46 before): EMCLAMP_Y, EMCLAMP_G, EMCON_RD and EMCON_RD_R declared LOW_SPEED_OR_DC after EMCON_HW (decision W5SI2-D1, authority SESSION)`; in memory before: 11 undecided (4 no declaration + 7 model absent), after: 7 (0 + 7), had they been CLOCKED_DIGITAL: 9 (0 + 9); layout-bound 16 in all three; models ABSENT (6 asked, 6 absent) |
| 6 `apply_coverage_si001.py` | 0 | `pcb_rules_coverage.yaml SI-001: note extended by 3789 characters, remediation's action replaced, owner and execution kept`; `THE MODELS WHEN THE COUNTS WERE TAKEN: ABSENT: 11 model(s) a reading asked for were NOT in the tree (...)`; `AND: this paragraph was written WITHOUT the models. It says so.` |
| 7 `apply_decisions_w5si.py` | 0 | `pcb_decisions.yaml: decisions 48 to 54 added (SESSION, ruled)`; `pcb_requirements.yaml: 1 record(s) bound to pcb_decisions.yaml@b5f7162443d5ad91 rebound to @4e1ff91f98e06b72 ... CFL-016` |

Second run of each: exit 2, one line, `REFUSED: already applied ...; nothing was written` (drafts 1 and 4 add
their line number). Outputs: `absent/*.run1.txt`, `absent/*.run2.txt`.

On a plain int8 clone WITHOUT the merge (`int8-plain/`, before its merge), `--dry-run` of each: drafts 1, 2, 3, 5,
6, 7 refuse with exit 2 and the sentence `REFUSED: v2/ecad/tools/ibis_read.py is not in the tree ...: stream w5si2
(fnd/w5si2) is not merged into this tree, and this draft changes a file for what that stream brings; nothing was
written`; draft 4 dry-runs with exit 0 (`dry run, nothing written: boards/b.json 3 entries; gen_pcb_b3.py PATTERNS
40 entries become 41`), which the README section 7 discloses as a design decision. Outputs: `int8-plain-refusals/`.

Tests, from the clone's `v2/ecad/tools/tests` with `python3 run.py <name>` (the clone IS a git repository, so the
commit-dating paths run; int8 carries more tests than the author's scratch views did):

| Test file | Models absent | Models present (after the copy) |
|---|---|---|
| edge_length | 41 passed, 0 failed, 1 skipped | 42 passed, 0 failed, 0 skipped |
| ibis_models | 6 passed, 0 failed, 0 skipped | 6 passed, 0 failed, 0 skipped |
| pinned_models | 6 passed, 0 failed, 0 skipped | 6 passed, 0 failed, 0 skipped |
| rules_status | 36 passed, 0 failed, 1 skipped | 36 passed, 0 failed, 1 skipped |
| evidence_class | 28 passed, 0 failed, 0 skipped | 28 passed, 0 failed, 0 skipped |
| signal_class, netclass, netlist_classes, rules_registry | 8, 13, 3, 5 passed, 0 failed | not re-run |
| decision_register | 3 passed, 0 failed, 2 skipped | not re-run |
| requirements | 68 passed, 2 failed, 1 skipped (`t_check_refuses_a_hand_edited_trace_page`, `t_the_trace_page_is_generated_not_hand_kept`), then 70 passed, 0 failed, 1 skipped after `rules_render.py --requirements` | not re-run |

`rules_lib.py`: `rules_lib: 59 rule(s), 0 error(s), 0 warning(s), fingerprint 635ff031f210f48c`.
`rules_lib.py requirements`: `rules_lib: 144 requirement record(s), 0 error(s), 0 warning(s)` (with the warning
`out/rule-audit is not in this tree`, the clone's).
`rules_render.py --requirements`: `rules_render: wrote ../../docs/REQUIREMENTS-TRACE.md (3976 lines)` in the clone.

### 2b. Models present

The thirteen ignored files copied from the worktree into the clone's `v2/vendor/ti/ibis/` and `st/ibis/`:
`git check-ignore -v` names `.gitignore:41:v2/vendor/*/ibis/*.ibs`; `git status --short` shows no model;
`git ls-files` finds none. `ibis_fetch.py --check` (fetches nothing): `state PRESENT: 13 present, 0 absent, 0
differ, of 13`.

The seven drafts were also run, once and then a second time, in a third clone (`view-present/`, the merge commit
with the models copied in): all exit 0 then exit 2 `REFUSED: already applied`. Board C in memory: before 4
undecided (4 no declaration), after 0, had they been CLOCKED_DIGITAL 6 by a figure, 31 by a bound, 0 undecided,
25 layout-bound; layout-bound 23 before and after; coverage note extended by 3413 characters, `THE MODELS WHEN THE
COUNTS WERE TAKEN: PRESENT ... (13 of the 13 the manifest pins were in the tree)`. Outputs: `present/drafts/`.

### 2c. SI-001 on the six declared netlists, both states, my own runs

`edge_length.py --netlist <netlist> --out-dir <my scratch>` from the clone's `v2/ecad/tools` for
`pcb-a-power-a23`, `pcb-b-compute-b19`, `pcb-c-display-c8`, `pcb-d-aprs-d9`, `pcb-e1-dock-e7`, `pcb-p-pack-p2`
(the phase directories CONFIG_INPUTS names). Exit 3 (INCONCLUSIVE) on every board in both states. Counts read from
the `edge_length.verdict.json` and `edge_length.table.json` I wrote (`absent/si001/`, `present/si001/`), each row
checked to sum:

| State | Board | signal | slow | non-slow | figure | bound | undecided (no decl + model absent + other) | answered | layout-bound (figure-held + BOUND_DECIDES) | models | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| present | A | 290 | 170 | 120 | 7 | 75 | 38 (38 + 0 + 0) | 19 | 63 (1 + 62) | PRESENT 5 asked | INCONCLUSIVE |
| present | B | 886 | 324 | 562 | 103 | 451 | 8 (8 + 0 + 0) | 361 | 193 (40 + 153) | PRESENT 10 | INCONCLUSIVE |
| present | C | 134 | 101 | 33 | 4 | 29 | 0 (0 + 0 + 0) | 10 | 23 (0 + 23) | PRESENT 6 | INCONCLUSIVE |
| present | D | 135 | 88 | 47 | 20 | 19 | 8 (8 + 0 + 0) | 26 | 13 (2 + 11) | PRESENT 5 | INCONCLUSIVE |
| present | E | 83 | 42 | 41 | 4 | 37 | 0 | 10 | 31 (0 + 31) | NOT_ASKED | INCONCLUSIVE |
| present | P | 40 | 20 | 20 | 0 | 5 | 15 (15 + 0 + 0) | 4 | 1 (0 + 1) | NOT_ASKED | INCONCLUSIVE |
| present | all | 1568 | 745 | 823 | 138 | 616 | 69 (69 + 0 + 0) | 430 | 324 (43 + 281) | | |
| absent | A | 290 | 170 | 120 | 6 | 71 | 43 (38 + 5 + 0) | 19 | 58 (0 + 58) | ABSENT 5 of 5 | INCONCLUSIVE |
| absent | B | 886 | 324 | 562 | 30 | 142 | 390 (8 + 382 + 0) | 61 | 111 (0 + 111) | ABSENT 10 of 10 | INCONCLUSIVE |
| absent | C | 134 | 101 | 33 | 4 | 22 | 7 (0 + 7 + 0) | 10 | 16 (0 + 16) | ABSENT 6 of 6 | INCONCLUSIVE |
| absent | D | 135 | 88 | 47 | 20 | 16 | 11 (8 + 3 + 0) | 26 | 10 (2 + 8) | ABSENT 5 of 5 | INCONCLUSIVE |
| absent | E | 83 | 42 | 41 | 4 | 37 | 0 | 10 | 31 (0 + 31) | NOT_ASKED | INCONCLUSIVE |
| absent | P | 40 | 20 | 20 | 0 | 5 | 15 (15 + 0 + 0) | 4 | 1 (0 + 1) | NOT_ASKED | INCONCLUSIVE |
| absent | all | 1568 | 745 | 823 | 64 | 293 | 466 (69 + 397 + 0) | 130 | 227 (2 + 225) | | |

Published figures by kind (from the per-net rows): present IBIS 74, STANDARD 64; absent STANDARD 64 only.
74 nets are MAKER with the models and not MAKER without; 426 of the 823 non-slow nets read identically in both
states.

Author's numbers beside mine: present 138 / 616 / 69, absent 64 / 293 / 466, board C undecided 4 to 0 (present) and
11 to 7 (absent), layout-bound 23 and 16, layout-bound totals 324 (43 + 281) and 227 (2 + 225), every board
INCONCLUSIVE in both states, 74 IBIS and 64 USB 2.0: ALL REPRODUCED, on the merged int8 line rather than the
author's own branch.

## 3. The judgement

**SI-001's INCONCLUSIVE is earned on each board.** On every board at least one layout-bound net is decided by a
bound (`bound_decided_nets` of 62, 153, 23, 11, 31, 1 with the models), and in the absent state every net that
waits on a model reads UNDECIDED with reason kind MODEL_ABSENT naming the file, never by the record's own
`edge_ns`. No net is decided by a figure its maker does not publish: the 138 are 74 IBIS cells (held to their own
V-t tables) and 64 USB 2.0 class records. A bound is called a bound (`decided_by: BOUND`, `edge_ns 0.0`, the bound
driver named, for example EPD_CS: `RPI-RP2040: U3 pin 7 GPIO5`).

**ER-D17, an absent model decides nothing.** From my two runs:
- board B `SEL1_A`: present `MAKER, IBIS, 0.451 ns, ST-STM32H743, U41 pin 22 PA0_WKUP, io8_ft_hs_3v3 f typ`;
  absent `UNDECIDED, MODEL_ABSENT`.
- board A `INA_ALERT`: present `MAKER, IBIS, 5.89 ns, TI-PCA9555, U27 pin 19 P16, PCA9555_P_33 r max`; absent
  `UNDECIDED, MODEL_ABSENT`.
- a net that must not change and does not: board C `USB_DM_R`: `MAKER, STANDARD, 4.0 ns, USB2-FS` in both states;
  board C `EPD_CS`: `BOUND, 0.0 ns, RPI-RP2040, U3 pin 7 GPIO5` in both states.
- note the direction of the fail-closed rule: a net with a bound driver AND a driver whose model is absent reads
  UNDECIDED (not BOUND) in the absent state (board C `SCL`: present BOUND by the RP2040, absent UNDECIDED
  MODEL_ABSENT). That is more conservative than a bound and it is what ER-D17 says.

**ER-D16, the V-t guard, reproduced by my own reader** (`my_ramp_check.py`, written for this check, no code
shared with `ibis_read.py`): over the thirteen files, 585 driven cells, 537 with a table, 522 hold, 15 contradicted,
48 with no table: the author's five numbers exactly. The 15 are PCA9555_INT_50/33/25 (f typ, min, max; INT_25 f min
holds) and TMP117 sda_1p8/3p3/5p0. The four cells by hand (first crossings, linear interpolation between the
table's rows):
- `[Model] PCA9555_INT_33 dV/dt_f max = 2.06/1.21E-10`, R_load 500: the 500 ohm falling table's swing is 3.439 V,
  dV 2.06 V is 59.9 percent of it (inside 50 to 70); the table falls from 20 to 80 percent in 0.605 ns (both
  crossings between the rows at 91 ns 3.6 V and 92 ns 0.1893 V), the cell's 0.121 ns is 0.200 of it: CONTRADICTED.
- `PCA9555_INT_33 dV/dt_f typ = 1.84/2.36E-10`: swing 3.053 V, dV 60.3 percent; table 1.200 ns (rows 92 ns 3.3 V,
  93 ns 1.827 V, 94 ns 0.2486 V), cell 0.236 ns is 0.197 of it: CONTRADICTED.
- `TMP117 sda_3p3 dV/dt_f max = 0.534433/7.67568e-09`, R_load 967: swing 3.569 V, dV 0.534 V is 15.0 percent
  (outside 50 to 70); table 34.02 ns, cell 7.676 ns is 0.226 of it: CONTRADICTED.
- one of the 522 that hold: `LVC1G57_OUT_33 dV/dt_f max = 2.18/2.21E-10`, R_load 500: swing 3.54 V, dV 61.6
  percent; table 0.2079 ns, cell 0.221 ns is 1.063 of it: HOLDS. This is the cell board C's EMCLAMP_Y basis cites.
The two record changes follow from the files: PCA9555's 3.3 V models are A and SCL (inputs, drive nothing), P
(i/o: r 7.15/10.2/5.89, f 6.33/7.17/5.96 ns, all six hold), SDA (open drain, f 88.1/111/72.3), INT (flagged); the
fastest unflagged cell is P_33 r max 5.89 ns, so 0.121 to 5.89 ns. TMP117's 3.3 V models are add and scl (inputs),
alert (open sink, f 16.86/23.4/12.61, `alert_3p3 f max 2.14113/1.26129e-08` holds: dV 60.0 percent, dt 1.002 of
the table's 12.59 ns), sda (flagged); so 7.6757 to 12.6129 ns. Both flagged pins sit on nets a bound already
decides (EXP_INT by the PCA9555 INT pin reads BOUND with the model present, my board C row confirms it; the kit
SDA by the RP2040), so no count moved, as the record says.

**W5SI2-D1, board C's four nets.** From the netlist (`3fddbb3edcd4248a`) itself: `/EMCLAMP_Y` = U14 pin 4, R48
pin 1; `/EMCLAMP_G` = Q7 pin 1 (G), R48 pin 2, R49 pin 1; `/EMCON_RD` = U13 pin 4, R46 pin 1; `/EMCON_RD_R` = R46
pin 2, U3 pin 32 GPIO21. Values: U13 `74LVC1G17 ... Diodes 74LVC1G17W5-7`, U14 `SN74LVC1G57DBVR ... 2-input NOR ...
6 In2 EMCON_HW`, R46 1k, R48 100R, R49 10k, Q7 Si2300DS, D22 the EMCON amber lamp. `/EMCON_HW` feeds U13 pin 2 and
U14 pin 6 (and U9, J_PANEL pin 8, TP11). So the four ARE copies of the EMCON inhibit, no connector, switch or
test point on them, one ends at a FET gate behind 100R with 10 k to ground, the other at a GPIO read as a level
behind 1 k. The class definition is quoted from `signal_class.py` (lines 34 to 36, verified) and `edge_length.py`
(line 245, verified). `EMCON_HW` and `TX_INHIBIT_n` are LOW_SPEED_OR_DC in `c.json` already (verified). The record
says what changes under CLOCKED_DIGITAL (README section 5 table; the draft prints it on the tree it runs on; my
runs: present 6/31/0, 12 answered, 25 layout-bound; absent 4/24/9, 18 layout-bound) and how to reverse. The
drivers' edges are stated (U14 0.221 ns by the IBIS cell I reproduced; U13's maker prints tPD only on DS35124 p. 6,
verified with pdftotext; RP2040 a slew bit only). The declaration does not pass the board, and it says so. I judge
it honest, with one disclosure gap (minor item m1 below).

**The eight desk remedies and the fifteen not closable: each reason is a source or a structural fact.**
Verified in the held PDFs with pdftotext: Hardware design with RP2040 p. 10 "the QSPI pins of RP2040 should be wired
directly to the flash, using short connections to maintain the signal integrity" (QSPI, not closable); p. 11 "Try and
keep the layout as short as possible" (crystal nodes, CLK-001 first); UM10204 Rev. 6 p. 58 "series resistors (Rs) of,
for example, 300 Ω can be used for protection ... designers must add the additional resistance into their
calculations for Rp and allowable bus capacitance" (kit bus, four boards); RP2040 datasheet p. 617 Table 625 VOH
2.62 V min at IOVDD 3.3 V and VOL 0.5 V max (the 170 and 125 ohm pad bounds follow: 0.68 V / 4 mA and 0.5 V /
4 mA; the 33 ohm is named a proposal, not computed to a match). Structural: SWD lines driven only by a bench probe
(TP1, TP2 on the netlist); EPD_SW a converter switch node (F-Q1 item 5, 32 siblings in class SW); Q3_G a lamp FET gate
from TR_APRS, a declared static level, and no 74LVC1G34 model is held (TI's nor Diodes'); HB1 to HB3 driven from
board B (board C's netlist has no driver of them); a resistor at the receiving end terminates nothing. None is a
guess. The `board_c_remedies.py` simulation is filed with its listing (`readings/board-c-remedies.txt`); I did
not re-run it (it edits tables in memory; the reasons above were checked instead).

## 4. The earlier checks' items

The brief speaks of an "edges" check with five minor items in `check-1/`. What the branch holds:
- `v2/docs/records/w5si/check-1/RESULT-w5si-check-1.json` is the FIRST pass's check: `mergeable: false`, three
  blocking items (bound-governed "maker-held" nets, the PATTERNS deletion, BOB's class) and thirteen minor items.
  Answered in `w5si-record.md` sections 6 and 8, item by item; I verified by grep: `ibis_read.py` returns UNKNOWN for
  an untyped model and reads `[Model Selector]` in both spellings (lines 25, 26, 100, 248 to 261); all 13 IBIS records
  carry `supply:` (13 of 13); ER-D10 cites FW-K02 and FW-B08 (data file header lines 103 to 107); `inputs_cited` on
  the clock inputs (6 occurrences); decisions as rows (draft 7); the remediation stays LAB and HARDWARE (verified in
  the clone after draft 6: `owner = LAB`, `execution = HARDWARE`); the search listing `edge-search.txt` is a declared
  input (`inputs.search_listing d08bc489782c976b`).
- The "edges" lens check of the SECOND pass (`fnd/w5si` at 7f7721c4, 27 September) is not filed in the tree; it is in
  the integrator's workflow journal (`wf_b5270c7e-b36/journal.jsonl` line 7): `mergeable: true`, no blocking item,
  TEN minor items M1 to M10. Of those, M5 (a [Ramp] cell's dV not checked; TMP117 sda 0.15 of the swing) is closed by
  ER-D16, and M9 (sources.txt labelled a 16-digit prefix as the sha256) is answered by the re-issued vendor lines
  (each says `sha256/16 ..., the full sha256 in the manifest`, verified on the pca9555 line). The other eight (M1
  three fail-open netlist shapes on no committed netlist, M2 DS3231 row wording, M3 TPS25740 dead rows, M4 CP2102N
  RI pattern, M6 tables slightly faster than cells, M7 HUB* nets answered by the USB class, M8 two edges on the same
  USB lines, M10 board B's U10 legend) are CARRIED in README section 9 ("first lens M1 ..., M2, M3, M4, M6, M7, M8,
  M10, not in this stream's list, the next author"), none closed silently.
- The drafts check (`int7/checks/w5si-check-2-drafts.md`, 28 September): B1, B2, B3 and M1 to M10 are each closed
  in README section 1; verified by my runs: B1 (no model tracked, fail closed in both states, rules_status pinned
  path tested on a git fixture), B2 (the coverage paragraph's counts, state and kinds are read at run time; the
  absent-state text says ABSENT and names 11 files), B3 (the decisions draft derives the netlist sha and the BOB lines
  and asserts the facts), M1 (CFL-016 rebound by draft 7), M2 (draft 6 prints the re-render owed), M3
  (`test_edge_length` 41 passed 1 skipped without the models), M4 (every draft refuses in one sentence, exit 2, seen
  on plain int8), M5 (owed line with address and full sha, `SOURCES.yaml` diff), M6 (each vendor line names the
  header's wording, 5 PROHIBITS_DISTRIBUTION and 8 COPYRIGHT_NO_GRANT), M7 (74 IBIS, 64 STANDARD; "AI review" in
  the coverage note), M8 (ER-D16), M9 (stated in draft 1's output), M10 (F-BOB names both revisions, lines 11 to 13).

## 5. Publication and provenance

- `git -C <worktree> ls-files | grep -c '\.ibs$'` = 0; the thirteen files are on disk in the worktree only, matched by
  `.gitignore` line 38 `v2/vendor/*/ibis/*.ibs` (added by the branch; the comment says the owner's decision is pending).
- The manifest's sha256 AND byte count equal the files in the worktree: 13 of 13 (computed by me).
- `ibis_fetch.py` was NOT run with `--fetch` (no network); `--check` only, which fetches nothing.
- Cited documents held under `v2/vendor/` at the sha256/16 the record cites: SCES414P `078364de617898af`
  (`ti/ti-sn74lvc1g57.pdf`), DS35124 `029f345a1e7be917` (`diodes/diodes-74lvc1g17.pdf`), RP2040 datasheet
  `be56fbb75ba0ae9e`, UM10204 Rev. 6 `b7619700e8bb9dd4`, Hardware design with RP2040 `51c4f430153fcdbf`; the data
  file `0689086680f7a4a4`, the board C netlist `3fddbb3edcd4248a` and the listing `d08bc489782c976b` as cited.
  Revisions: DS35124 prints `Rev. 8 - 2` on every page but page 6, whose footer prints `Rev. 7 - 2` (a maker's
  inconsistency in the PDF; the record's Rev. 8-2 is the document's).
- `sources.txt` and `vendor-status.txt` lines: present for the two datasheets this stream cites directly and for
  all thirteen models (13 + 13 lines, each naming maker, literature number, address, how the .ibs is taken out of
  the zip, fetch dates, sha256/16 with a pointer to the full sha in the manifest, file rev, and the header's wording).
  UM10204 has a `sources.txt` line (341) and NO `vendor-status.txt` line; the two RP2040 documents are covered by
  folder-level lines only (`rp2040` in both lists). Those three files predate this stream (UM10204 is on main from
  `0da2778b`), so it is a carry item for the vendor lists, not a defect of this stream.
- Every one of the 90 citations of the data file is checked by the tool on every run; my six readings in both
  states carried no citation failure (`contradicted_nets = 0` on every board).

## 6. Prose and scope

- `git diff --stat main...fnd/w5si2`: 59 files, 10188 insertions, 75 deletions; tools (`edge_length.py`,
  `ibis_read.py`, `ibis_manifest.py`, `ibis_fetch.py`, `pcb_edge_rates.yaml`, three test files), the manifest, the
  two vendor lists, `.gitignore`, and the records. No registry, board table, generator or rule file is changed on the
  branch: those changes are the drafts.
- Em or en dashes in the added lines of the branch: 0. In the text the drafts wrote into the clone: 0.
- "AI review": in `README.md` (twice), `w5si-record.md`, the coverage note ("after two AI reviews, neither a
  qualified engineering review").
- Prototype framing: "nothing here has been built, ordered or measured", "No reading on this page is a PASS".
- No claim of a result not obtained that I could find: the fetch is logged; the scratch readings are filed with their
  listings; the tests are stated per state; the record says what it did not run.
- No requirement lowered: SI-001's rule is untouched (fingerprint `e67c393563c5d8ce` in my verdicts,
  `635ff031f210f48c` for the set); the coverage remediation keeps LAB and HARDWARE; ER-D16 can only remove a figure;
  ER-D17 makes the reading more conservative without the models; W5SI2-D1 is a class declaration on content with the
  non-slow alternative shown and INCONCLUSIVE in both.

## 7. Items

Blocking: none.

Minor:
- m1. W5SI2-D1 does not disclose that LOW_SPEED_OR_DC is also the class both EMC return rules skip
  (`v2/ecad/tools/return_via.py` line 177 and `ref_change.py` lines 127 to 128, `slow += 1; continue`), the effect
  check-1's third blocking item named for BOB. For these four nets the class's own question (does a reference EXIST)
  is arguably the right one (a lamp FET gate and a GPIO level), but the sentence belongs in
  `apply_board_c_declarations.py`'s docstring (lines 20 to 40) and README section 5, as the BOB basis has it.
- m2. `fnd/int8` moved from `097b6cf7` to `a8607eab` during this check. The merge at the new tip conflicts in the same
  three appended files only and the drafts apply there; rehearse once more at integration time if int8 moves again.
- m3. Draft 6 writes the paragraph of the state it runs in. Run on this host's integration checkout, which holds no
  model, it writes the ABSENT counts (64 / 293 / 466) into the registry, honest but "of another state" as the draft
  itself prints. Copy the thirteen ignored files from the w5si2 worktree into the integration checkout (they stay
  ignored) or run `ibis_fetch.py --fetch` there before draft 6, so the registry carries the counts the box re-take
  will reproduce; otherwise the re-take record must say so.
- m4. The `.gitignore` conflict must be resolved by hand (both blocks kept); a resolution that keeps only HEAD's
  would drop the ignore rule and a later `git add -A` in a checkout that holds the models would stage them. Check
  `git check-ignore -v v2/vendor/ti/ibis/pca9555.ibs` after the merge.
- m5. UM10204 lacks a `vendor-status.txt` line and the two RP2040 documents have folder-level lines only (section 5);
  predates the stream; for the vendor lists' owner.
- m6. The brief's "five minor items" of an edges check in `check-1/` does not match the tree: check-1 is the first
  pass's refusing check (3 blocking, 13 minor), and the edges lens (10 minor) is only in the workflow journal. The
  integrator may want the edges-lens result filed beside the records like the drafts check is.
- m7. `apply_board_b_declarations.py` applies on a tree without the stream (dry-run exit 0 on plain int8); disclosed
  in README section 7; keep the order so its readings are re-taken with the rest.

Recommendations for the integration, in order: merge (resolve the three files by keeping both sides); confirm the
ignore rule; put the models in place (ignored) or fetch them; drafts 1 to 7; `rules_render.py`,
`rules_render.py --requirements`, `decisions_render.py`; commit; SI-001 re-taken on all six boards together on the
box with the models fetched there (`ibis_fetch.py --fetch`, then `--check`), and board B's and board C's other
readings that declare their board tables.

## 8. What was run, exact last lines

See sections 2a to 2c. Scratch outputs: `absent/`, `present/`, `newtip/`, `int8-plain-refusals/`,
`my_ramp_check.py`. The model copies I made into `view/` and `view-present/` were removed at the end of the check;
the only copies remain in the author's worktree.

## 9. Not checked, and why

- Nothing on the rented box, no KiCad, no full suite (the rules). The routed half of SI-001 and `retake_gate.sh`
  were not run.
- `ibis_fetch.py --fetch`: not run (no network from a check); the author's fetch log was read, not reproduced.
- The IBIS models were not simulated into a line; the [Ramp] fixtures were taken as the makers state them.
- The 39 bound families' documents were not re-searched beyond the five pages quoted above; `edge-search.txt` was
  not re-derived.
- `board_c_remedies.py` (the simulation of the five remedy steps) was not re-run; its reasons were checked against
  the sources instead.
- `test_pinned_models.py` runs on its own temporary git repository; the pinned-state path was not exercised on a
  real evidence tree (none in the clone carries a SI-001 reading taken with the models).
