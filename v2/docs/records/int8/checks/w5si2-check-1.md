mergeable: yes

AI review of stream w5si2 (`fnd/w5si2` at `f84243ba`, base `85ad1193`) by a checker that wrote none of it; not a
qualified engineering review. Prototype design: nothing built, ordered or measured. Full notes:
`/home/claude-runner/worktrees/meshsat-fieldkit/_scratch/chk-w5si2/CHECK.md`.

## Blocking items

None.

## Minor items

- m1. W5SI2-D1 does not say that LOW_SPEED_OR_DC is also the class both EMC return rules skip
  (`v2/ecad/tools/return_via.py` line 177, `ref_change.py` lines 127 to 128), the effect check-1's third blocking
  item named for BOB. For a lamp FET gate and a GPIO level the class's own question (a reference EXISTS) is arguably
  right, but the sentence belongs in `v2/docs/records/w5si/apply/apply_board_c_declarations.py` (docstring lines 20
  to 40) and `v2/docs/records/w5si2/README.md` section 5.
- m2. `fnd/int8` moved from `097b6cf7` to `a8607eab` during the check. Rehearsed at both: the same three
  append-append conflicts, the drafts apply at both; rehearse again if int8 moves before the merge.
- m3. Draft 6 writes the paragraph of the state it runs in: on an integration checkout without the models it writes
  the ABSENT counts (64 / 293 / 466) into `pcb_rules_coverage.yaml`. Put the thirteen ignored files in place (copy from
  the w5si2 worktree, or `ibis_fetch.py --fetch`) before draft 6, or the re-take record must say so (the draft prints
  this itself).
- m4. The `.gitignore` conflict must be resolved by keeping both blocks; a HEAD-only resolution drops the ignore rule.
  Verify with `git check-ignore -v v2/vendor/ti/ibis/pca9555.ibs` after the merge.
- m5. UM10204 has a `sources.txt` line (341) but no `vendor-status.txt` line; the two RP2040 documents have
  folder-level lines only. Pre-existing files (UM10204 on main from `0da2778b`), for the vendor lists' owner.
- m6. The brief's "edges check with five minor items in check-1" does not match the tree: `check-1/` is the first
  pass's refusing check (3 blocking, 13 minor, all answered in `w5si-record.md` sections 6 and 8); the edges lens of
  7f7721c4 (`mergeable: true`, TEN minor items) is only in the integrator's workflow journal
  (`wf_b5270c7e-b36/journal.jsonl` line 7). Of its ten, M5 is closed by ER-D16 and M9 by the re-issued vendor lines;
  M1, M2, M3, M4, M6, M7, M8, M10 are carried in README section 9 with an owner. Consider filing that result beside
  the records as the drafts check is.
- m7. `apply_board_b_declarations.py` applies on a tree without the stream (dry-run exit 0 on plain int8), disclosed
  in README section 7; keep the order.

## Counts, the author's beside mine (both states, six declared netlists, seven drafts applied)

| Reading | Author, present | Mine, present | Author, absent | Mine, absent |
|---|---|---|---|---|
| by a published figure | 138 (74 IBIS + 64 USB 2.0) | 138 (74 IBIS + 64 STANDARD) | 64 | 64 (all STANDARD) |
| by a bound | 616 | 616 | 293 | 293 |
| undecided | 69 | 69 (69 + 0 + 0) | 466 (69 + 397) | 466 (69 + 397 + 0) |
| layout-bound | 324 (43 + 281) | 324 (43 + 281) | 227 (2 + 225) | 227 (2 + 225) |
| board C undecided, before to after W5SI2-D1 | 4 to 0 | 4 to 0 | 11 to 7 | 11 to 7 |
| board C layout-bound | 23 | 23 | 16 | 16 |
| board C had they been CLOCKED_DIGITAL | 6 / 31 / 0, 25 layout-bound | the same | 4 / 24 / 9, 18 | the same |
| verdict, every board | INCONCLUSIVE | INCONCLUSIVE (exit 3) | INCONCLUSIVE | INCONCLUSIVE |

Per board (mine, present): A 7/75/38, B 103/451/8, C 4/29/0, D 20/19/8, E 4/37/0, P 0/5/15. Absent: A 6/71/43
(38 + 5), B 30/142/390 (8 + 382), C 4/22/7 (0 + 7), D 20/16/11 (8 + 3), E 4/37/0, P 0/5/15. Every row sums.
Taken with `edge_length.py --netlist ... --out-dir <my scratch>` on the merged int8 line, not on the author's branch.

ER-D16 by my own reader (`my_ramp_check.py`, independent of `ibis_read.py`): 585 driven cells, 537 with a table,
522 hold, 15 contradicted, 48 without a table, the author's five numbers; the 15 are PCA9555 INT and TMP117 SDA cells.
By hand: `PCA9555_INT_33 f max 2.06/1.21E-10`: dV 59.9 percent of the 500 ohm table's 3.439 V swing, dt 0.121 ns is
0.200 of the table's 0.605 ns (rows 91 ns 3.6 V and 92 ns 0.1893 V): CONTRADICTED. `f typ 1.84/2.36E-10`: 60.3
percent, 0.236 ns is 0.197 of 1.200 ns: CONTRADICTED. `TMP117 sda_3p3 f max 0.534433/7.67568e-09`: dV 15.0 percent
of 3.569 V, 7.676 ns is 0.226 of 34.02 ns: CONTRADICTED. `LVC1G57_OUT_33 f max 2.18/2.21E-10`: 61.6 percent, 0.221 ns
is 1.063 of 0.2079 ns: HOLDS (the cell EMCLAMP_Y's basis cites). The two record changes follow: PCA9555's fastest
unflagged 3.3 V cell is P_33 r max 5.89 ns (P cells 7.15/10.2/5.89/6.33/7.17/5.96 all hold; SDA 72.3; INT flagged),
so 0.121 to 5.89; TMP117's is alert_3p3 f max 12.61 ns (holds: dV 60.0 percent, dt 1.002; alert 16.86/23.4/12.61;
sda flagged), so 7.6757 to 12.6129. Both flagged pins sit on nets a bound decides (EXP_INT, kit SDA): no count moved.

ER-D17 from my two runs: board B `SEL1_A` present MAKER IBIS 0.451 ns (ST-STM32H743, U41 pin 22), absent UNDECIDED
MODEL_ABSENT; board A `INA_ALERT` present MAKER IBIS 5.89 ns (TI-PCA9555 U27 pin 19), absent UNDECIDED MODEL_ABSENT.
Unchanged in both states: board C `USB_DM_R` MAKER STANDARD 4.0 ns (USB2-FS) and `EPD_CS` BOUND 0.0 ns (RPI-RP2040
U3 pin 7). 74 nets move from MAKER to UNDECIDED without the models; 426 of 823 read identically. A net with a bound
driver and an absent-model driver reads UNDECIDED without the model (board C `SCL`), more conservative than a bound.

W5SI2-D1 checked on the netlist (`3fddbb3edcd4248a`): `/EMCLAMP_Y` U14.4 to R48.1; `/EMCLAMP_G` Q7.1 (G), R48.2,
R49.1; `/EMCON_RD` U13.4 to R46.1; `/EMCON_RD_R` R46.2 to U3.32 GPIO21; U13 Diodes 74LVC1G17W5-7, U14 SN74LVC1G57DBVR
as a NOR of TX_INHIBIT_n and EMCON_HW, R46 1k, R48 100R, R49 10k, Q7 Si2300DS, D22 the EMCON amber lamp. Class quoted
from `signal_class.py` lines 34 to 36 and `edge_length.py` line 245; EMCON_HW and TX_INHIBIT_n already
LOW_SPEED_OR_DC in `c.json`; the CLOCKED_DIGITAL alternative is computed and shown; the reversal is named. Honest.
The eight desk remedies and fifteen not closable rest on sources I read in the held PDFs with pdftotext (Hardware
design with RP2040 p. 10 "wired directly to the flash", p. 11 "as short as possible"; UM10204 Rev. 6 p. 58 "series
resistors (Rs) of, for example, 300 Ω"; RP2040 datasheet p. 617 Table 625 VOH 2.62 V, VOL 0.5 V; SCES414P p. 6 tPD
only; DS35124 p. 1 "standard push-pull output") or on structure (bench probe, switch node, drivers on board B, a
receiving-end resistor terminates nothing); none is a guess.

## The merge

Scratch clone from `origin/fnd/int8` (`097b6cf7`), `git merge --no-ff origin/fnd/w5si2`: three conflicts, each
one append-append hunk at the end of the file: `.gitignore` lines 36 to 44 (int8's `AGENTS.md` rule against
w5si2's `v2/vendor/*/ibis/*.ibs` rule), `v2/vendor/sources.txt` lines 349 to 376 (w5tray's 12 lines against the 13
model lines), `v2/vendor/vendor-status.txt` lines 268 to 295 (the same 12 against 13). All mechanical: keep both,
HEAD's first; resolved so in the clone (commit `9d99f551`). No other file conflicted; the registry and the trace page
are not touched by the branch. The same three, same hunks, at `a8607eab`.

## What I ran, exact last lines

- Drafts 1 to 7 on the merged clone with no model: each `exit=0`; second runs each `exit=2` and one line, for example
  `REFUSED: already applied (apply_rules_status_config_inputs.py line 143); nothing was written`. Key lines:
  `64 inputs (6 before) ... no model is declared`; `61 lines added`; `9 document rows and one owed line added ... ABSENT
  (0 of 13 present)`; `PATTERNS 40 entries become 41`; `signal_classes 50 entries (46 before)`; `note extended by 3789
  characters, remediation's action replaced, owner and execution kept`; `decisions 48 to 54 added (SESSION, ruled)`;
  `CFL-016` rebound `b5f7162443d5ad91` to `4e1ff91f98e06b72`.
- The same seven in a third clone with the models present: `exit=0` then `exit=2`; `note extended by 3413 characters`,
  `THE MODELS WHEN THE COUNTS WERE TAKEN: PRESENT ... (13 of the 13 ...)`.
- On plain int8 without the merge, `--dry-run`: drafts 1, 2, 3, 5, 6, 7 `exit=2` `REFUSED: v2/ecad/tools/ibis_read.py is
  not in the tree ...: stream w5si2 (fnd/w5si2) is not merged into this tree ...; nothing was written`; draft 4 `exit=0`
  `dry run, nothing written`.
- Tests (`run.py <name>`, models absent): edge_length `41 passed, 0 failed, 1 skipped`; ibis_models `6 passed, 0
  failed, 0 skipped`; pinned_models `6 passed, 0 failed, 0 skipped`; rules_status `36 passed, 0 failed, 1 skipped`;
  evidence_class `28 passed, 0 failed, 0 skipped`; signal_class 8, netclass 13, netlist_classes 3, rules_registry 5
  passed, 0 failed; decision_register `3 passed, 0 failed, 2 skipped`; requirements `68 passed, 2 failed, 1 skipped`
  (the two stale-trace-page tests), then `70 passed, 0 failed, 1 skipped` after `rules_render.py --requirements`
  (`wrote ../../docs/REQUIREMENTS-TRACE.md (3976 lines)`). Models present: edge_length `42 passed, 0 failed, 0
  skipped`; ibis_models 6; pinned_models 6; rules_status `36 passed, 0 failed, 1 skipped`; evidence_class 28.
- `rules_lib.py`: `59 rule(s), 0 error(s), 0 warning(s), fingerprint 635ff031f210f48c`; `rules_lib.py requirements`:
  `144 requirement record(s), 0 error(s), 0 warning(s)` (also at the new int8 tip after the drafts).
- `edge_length.py --netlist` on six boards, both states: `exit=3` each, verdict INCONCLUSIVE, counts above.
- `ibis_fetch.py --check` (fetches nothing) with the models copied in: `state PRESENT: 13 present, 0 absent, 0 differ,
  of 13`. Manifest sha256 and byte count against the worktree files: 13 of 13 match (my computation).
- Publication: `git -C <worktree> ls-files | grep -c '\.ibs$'` = 0; `.gitignore` line 38 holds the rule; the clone
  with the models copied in shows none in `git status`. Dashes in the branch's added lines: 0; in the drafts'
  written text: 0. "AI review" present in both records and in the coverage note.

## Not checked, and why

The rented box, KiCad, the full suite, `retake_gate.sh` and the routed half of SI-001 (the rules). `ibis_fetch.py
--fetch` (no network from a check; the author's log was read). No IBIS model simulated into a line. The 39 bound
families' documents beyond the five pages quoted; `edge-search.txt` not re-derived. `board_c_remedies.py` not
re-run (its reasons checked against the sources instead). The pinned-state path of `rules_status` only through
`test_pinned_models.py` on its own git fixture, not on an evidence tree with a SI-001 reading taken with the models.
My model copies in the scratch clones were removed at the end; the only copies remain in the author's worktree.
