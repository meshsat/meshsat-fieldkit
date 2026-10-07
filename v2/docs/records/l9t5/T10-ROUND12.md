**ROUND 12 (T10; row (b)'s last corrections on its targeted recheck Q-183, W163; 7 October 2026, W167, branch `fnd/l4hod`, the one writer after W159, and for N4's HO-E part `fnd/l4hoe`, the one writer after W152): DONE: N1 HO-D's pass reading restated CONDITIONAL on E-17 and E-17 extended to read the regulator's junction at HO-D's pass top 0.6819 A (pass at most 125 C, 82.5 C/W at zero ground current) in T10 11a (e), (h), (j) and (k), V-B20, FW-B24's source cell, the ledger's restatement, the change-list rows R-248 and R-250, record l4hod's J4, section 8 and page, and the connected record's item 6; N2 V-B23's hold-off vector a short of the 3.3 V output to ground holding the rail under BOR; N3 test_l9t5_rowb holds the contract's HO-D band equal to l4hod.out's J4 (W163's M3 and M4 FAIL against it); N4 the residual old-edge text (canq and l4canen read the tree's l4reg output, T10-CANQ.md's note, L4REG's W138-1 end condition and W138-2's reason, L4LIM-SCREEN's W159-D4 sentence; on fnd/l4hoe `l9t5_hoe.out` on the envelope 0.5878 A); N5 the four change-list rows' class read against their acceptance and noted; N6 the hold-off across a peer's own reset specified. NOT DONE: no independent check (none is owed: these are conditions, a test vector, a test assertion and record text, the coordinator's clerical reading); nothing applied; no circuit changed. NEXT: the coordinator's reading, then set 33. Nothing in this kit has been built, bought, powered or measured; nothing here closes a cx46 item.**

# T10 round 12: row (b)'s last corrections after its targeted recheck

- **Author:** W167 (Claude), MESHSAT-1357, 7 October 2026 from 12:08 CEST (times from `date`, Europe/Amsterdam). Branch `fnd/l4hod`
  from `23384006` (W159's round 11); `fnd/l4hoe` from `003338e3` (W152) for N4's HO-E item only.
- **Failure cases read against:** W163's report (`_runs/claude/w163rechkrowb/REPORT-FULL-AS-RECEIVED.md`, an AI review): row (b)
  SUPPORTED AS CONDITIONAL on E-17, W146-F10, F6's assumption under V-B25 and N1's E-17 reading; N1 to N3 to be fixed before set 33,
  N4 to N6 notes. Row (b)'s focused check (W157) and its targeted recheck (W163) are spent (constitution section 6): this round changes
  no circuit, raises no verdict and asks for no further check; the coordinator reads it as clerical.
- **Case rows:** as round 11 (C-DEV rev 2's T10 figures, 14.0k corner, 76.25 C inside air, revision V).

## 1. The findings and what this round did

| Id | W163's class | What was wrong | Correction | Where it is held |
|---|---|---|---|---|
| N1 | should fix | HO-D's "a lost limit never passes" rests on TI's printed JEDEC theta, which T10 11a (e) itself names no bound at the site; at E-17's admitted 95.7 C/W a limit passing at the pass top 0.6819 A reads 132.8 C | restated CONDITIONAL on E-17 read at the pass top; E-17 extended: the same sites' junction carried to an input current of 0.6819 A, pass at most 125 C, 82.5 C/W at zero ground current. Never a tightened HO-D reading: a healthy limiter already reads up to 0.6326 A | `l9t5_t10.out` 11a (e) (E-17), (h) (L4A-57's HO-D sentence), (j) (the qualification limits' row) and (k); `apply_hw_fw_contract_rowb.py` V-B20 and FW-B24's source cell; `apply_remeng_rowb.py`'s first row; `apply_l4e9_changelist_rowb.py` R-248 and R-250; `l4hod.out` J4, section 8 and its judge predicate; `L4HOD.md` section 5 (the bold claim and J4's row), section 11 task 7, sections 12 and 14; `l9t5_connected.out` 11a (d) item 6 (read from J4); `L4REG.md`'s E-17 cell and W138-1's end condition; `L4LIM-SCREEN.md` |
| N2 | should fix | V-B23's vector loaded the 3.3 V rail through 10 Ohm (0.33 A): the regulator stays in regulation and the supervisor keeps running, so FW-B22's restart never fires and three failed restarts are never produced | the 3.3 V output shorted to ground, holding the rail under BOR so the supervisor cannot boot whether or not its limiter latches (the TPS737's foldback current is TYPICAL only, so it may sit either side of IOSmin; both outcomes keep the rail down); expected: the peers' restart rule acts (no TXD edge and no state frame for 2 s), three failed restarts, then EN low between retries 600 s apart, the hold-off read in both peers' state frames | `apply_hw_fw_contract_rowb.py` V-B23; `test_l9t5_rowb.t_v_b23_hold_off_vector_holds_the_rail_under_bor` (the 10 Ohm vector as a mutant FAILS) |
| N3 | should fix | no test held the contract's HO-D band: W163's M3 (V-B25 back to 0.6140 A) and M4 (FW-B24 back to 0.6140 A) both passed | `test_l9t5_rowb.t_the_contract_hod_band_equals_l4hod_j4`: the page rowb writes, its FW-B24 PASS band and V-B25 reading band equal J4's healthy reading band read from `l4hod.out`; M3 and M4 are in the test as mutants and FAIL; run against copies of the rowb script carrying M3 and M4, the test itself FAILS (section 4) | the test |
| N4 | note | the residual old-edge text: `l9t5_canq.out` line 62 and `T10-CANQ.md` line 125 quoted 0.4702 to 0.5704 A through canq's input copy `9fbda7a6`; L4REG's W138-1 end condition said 98.6 C/W; W138-2's reason text (W159's authority row) cited 3.4921 V; fnd/l4hoe's `l9t5_hoe.out` printed 0.5704 A and 161.0 C | canq reads the tree's `l4reg_compare.out` (0.4702 to 0.5878 A; its row 8 conclusion unchanged); `T10-CANQ.md` keeps W138's quotation and adds the envelope after it; W138-1's end condition on 95.7 C/W and 0.5878 A; W138-2's reason 3.4255 V against 3.4965 V (-0.0710 V, `l4reg_compare.out` section 4 (4) (f)); L4LIM-SCREEN's 98.6 C/W kept by W159-D4 with that sentence; found on the way, the same class: l4canen read the same copy and printed 23.5 mJ and 2.35 mW, now 24.2 mJ and 2.42 mW from the tree's output; on fnd/l4hoe the HO-E record reads the envelope from a copy of fnd/l4hod 23384006's `l4reg_compare.out` (`inputs/l4reg-l4reg_compare-d6c7e771.out`, SOURCES-HOE.txt): 0.5878 A, 163.5 C, 14.82 C/W | `l9t5_canq.out`, `l4canen.out`, `L4REG.md`, `L4LIM-SCREEN.md`, `T10-CANQ.md`, `inputs/SOURCES-canq.txt`; fnd/l4hoe `l9t5_hoe.out`, `HO-E-COMPARISON.md` |
| N5 | note | rows R-247 to R-250 carry SETTLED WORK and "no open question" next to acceptance cells that say CONDITIONAL and PROVISIONAL | read and NOTED (SESSION W167-D3): the class is L4-E9's own (cons_classes gives every DRAFTED step-B implementation row outside its tables SETTLED WORK, and test_l9t5 holds the applied register to it); it names the row's step, not its acceptance. The draft's docstring reads each row's class against its Acceptance cell, the page note says it where the change list is read, and R-248's and R-250's Acceptance cells now name their conditions in full | `apply_l4e9_changelist_rowb.py`; `test_l9t5_rowb.t_the_change_list_class_is_read_against_its_acceptance` |
| N6 | note | the hold-off's state across a peer's own reset was not specified | specified (SESSION W167-D2), no new state: the hold-off is each peer's own (its count and its held vote, in RAM, not kept across its reset; FW-B24's backup-register record is HO-D's alone); a peer that resets drops its vote, canen's 2-of-2 hold releases and the target is powered; once that peer has rejoined it counts afresh with the other peer's vote held, both holding again 24.8 s after its rejoin, the target powered for 18.8 s of it (MODEL on the DRAFTED cadence and the boot ASSUMPTION) | `l9t5_t10.out` 11a (f) (iii); FW-B22 in `apply_hw_fw_contract_rowb.py`; `test_l9t5_rowb.t_the_hold_off_across_a_peers_reset_is_specified` |

## 2. The figures (each a MODEL on PRINTED rows; nothing measured)

| Figure | Value | Where |
|---|---|---|
| HO-D's pass top (J4) | 0.6819 A | `l4hod.out` J4 (carried in T10 as `R10_HOD_TOP`, held equal by test) |
| the site's theta that holds 125 C at the pass top, IGND = 0 | 82.5 C/W (48.75 K over 0.8669 V x 0.6819 A) | T10 11a (e); J4 |
| the pass top's junction at E-17's limit at IOSmax (95.7 C/W) | 132.8 C | T10 11a (e); J4 |
| the pass top's junction on the printed 76.0 C/W | 121.2 C | `l4hod.out` section 8 |
| a peer's own reset in the hold-off: from its rejoin to both holding again | 24.8 s (2.0 s decision, two 10 s periods, 2.0 s hold, 0.800 s rejoin window) | T10 11a (f) (iii) |
| of which the target is powered | 18.8 s | T10 11a (f) (iii) |
| W138-2's T10-A3 with the 0.3 ohm sense kept, on the envelope | 3.4255 V against 3.4965 V, -0.0710 V | `l4reg_compare.out` section 4 (4) (f) |
| l4canen's latched attempt and its average | 24.2 mJ, 2.42 mW | `l4canen.out` |
| HO-E: the controller at the envelope's top, all of it in the controller | 163.5 C on 45.0 C/W; H-3's theta at most 14.82 C/W | fnd/l4hoe `l9t5_hoe.out` section 2 and 4 |

## 3. SESSION decisions of this round

Each under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026; ruled_by W167 (Claude), MESHSAT-1357;
ruled_on 2026-10-07; reversed_by none (the way back is the last column).

| Id | Decision | authority | authority_why | To reverse |
|---|---|---|---|---|
| W167-D1 | N1 restated CONDITIONAL on E-17 read at the pass top (W163's recommendation), the pass top carried into T10 as a figure held equal to J4 by a test rather than read (record l4hod reads `l9t5_t10.out`, so reading J4 there would make a regeneration cycle, constitution section 8) | SESSION | record text and a measurement's extension; no part, net, figure of the test or verdict changes; tightening HO-D's reading instead fails a healthy part (0.6326 A), so one option stands | E-17 read at the site at or under 82.5 C/W removes the condition; a cycle-free reading route for T10 (a stage that runs after record l4hod) replaces the carried figure |
| W167-D2 | N6: the hold-off kept in RAM per peer, not across its own reset, the bound stated (24.8 s, 18.8 s powered) | SESSION | it specifies the drafted behaviour without a new mechanism; the persistent alternative (the hold-off recorded in the backup registers and re-voted at boot) is a firmware design change that this clerical round, after the spent recheck, may not introduce, and it would rest on F6's retention assumption; one option stands within this round | record the hold-off in each peer's backup registers and re-assert its vote at boot (a firmware change with its own check) |
| W167-D3 | N5 noted, not restated: the rows keep L4-E9's class, the reading written where the rows are read | SESSION | the class is generated by L4-E9's cons_classes and held by test_l9t5's rule; restating it means changing L4-E9's tables and that rule together, the integrator's and L4-E9's owner's work; the conditions are in the Acceptance cells | add R-248 and R-250 to L4-E9's PHY_EXTRA (or RE_ROWS) with test_l9t5's rule at set 33 |
| W167-D4 | N4: canq and l4canen read the tree's `l4reg_compare.out` (in their dependency order after it); fnd/l4hoe's HO-E reads a byte copy of fnd/l4hod 23384006's, filed with its sha256 | SESSION | a record reads its inputs from its own tree (WORKER-RULES); fnd/l4hoe has no record l4reg, so the copy is the house's route; the band is W159-D2's, no figure is chosen here | read the copies again (the band back to the tested row's 0.5704 A, which W159-D2 rejects) |

## 4. Evidence

- N3's mutants against the real test (7 October 2026, 12:40 CEST): copies of `apply_hw_fw_contract_rowb.py` with V-B25's band top at
  0.6140 A (M3) and FW-B24's at 0.6140 A (M4), `test_l9t5_rowb.t_the_contract_hod_band_equals_l4hod_j4` pointed at each copy:
  unmutated PASS; M3 FAIL; M4 FAIL (the assertion names J4's band, 0.4345 to 0.6326 A, against the row read). The same two mutants
  are also held inside the test, on the page rowb writes.
- Every regenerated output passed `_bin/regen_out.py`'s four conditions (two identical runs, exit 0, every pin current), in dependency
  order: `l9t5_t10`, `l4reg_compare`, `l9t5_canq`, `l9t5_canmb`, `l4canen`, `l4hod`, `l8r2_dist`, `l9t5_connected`, `l4lim_screen`;
  a pass after the last source edit found all nine already identical (a fixed point, 12:50 to 12:56 CEST).
- The tests as run.py printed them are in section 5.

## 5. Reproduce and the tests

From the repository root, in the order of section 4, each through `_bin/regen_out.py <worktree> <script> <output>`; the apply drafts
only on scratch copies (t10, canq, rowb; `apply_l4e9_changelist_rowb.py --check`). Tests: `env -C v2/ecad/tools python3 tests/run.py
test_l9t5_rowb.` and the modules W159 and W163 ran.

Tests on fnd/l4hod (7 October 2026, 12:39 to 12:50 CEST, each module as run.py printed it): test_l4reg "tests: 8 passed, 0 failed,
0 skipped"; test_l9t5_canmb 10/0/0; test_l9t5_canq 22/0/0; test_l4canen 11/0/0; test_l4hod 12/0/0; test_l9t5_rowb 18/0/0 (13 before
this round, five new: N1, N2, N3, N5, N6; 18/0/0 again at 12:56 after its docstring); test_w11l9t5 8/0/0; test_l4small 10/0/0;
test_remeng 17/0/0; test_applier_state 20/0/0; test_l4lim 8/0/0; test_pdftext_input 19/0/0; test_l9t5 42/0/0; test_l4e9 64/0/0;
test_l8r2 40/0/0: W159's fifteen modules, 309 passed, 0 failed, 0 skipped. The modules W163 added: test_recpack 7/0/0; test_w9l9t5
11/0/0; test_lstat31 16/0/0; test_w20oneliners 9/0/0; test_dgate2 26/0/0; test_w42cite 8/0/0; test_l8p 33/0/0; test_res32 14/1/0,
its failure test_res32.t_every_cited_file_of_the_coordinator_exists_and_carries_its_quote on the coordinator's own files outside the
repository (`_runs/int32/placeholders_check.py` line 10 and `_runs/int32/placeholders-deferred.tsv` no longer carry the quotes
`records/int32/RESULT.md` cites), which no file of this round touches (W163's clone skipped those three tests).

Tests on fnd/l4hoe (12:28 to 12:58 CEST): test_l9t5_hoe 21/1/0 first (the page cited 15.27 C/W, which the restated output no longer
prints), then 22/0/0 with the page restated; test_pdftext_input 19/0/0; test_applier_state 20/0/0; test_l9t5 42/0/0.

The constitution was read and is acknowledged (sections 3 to 6 and 8): each correction is held against its own failure case, no
circuit changes, no verdict is raised, no regeneration cycle is made, and no further check is spent.
