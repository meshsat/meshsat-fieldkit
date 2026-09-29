# Stream rf2walk, running log (MESHSAT-1357, RF-002 on set 12)

Newest last. Times CEST, read from `date`. Worktree `/home/claude-runner/worktrees/meshsat-fieldkit/rf2walk`, branch
`fnd/rf2walk` from `fnd/int13` at `e41df395` (set 12: stream d4emcon's `apply_b_d4e.py` and `apply_c_d4e_f1.py` applied,
boards B and C regenerated, `readback_d4e.py` holding on both). Author: stream d4emcon's author. Prototype framing: every
reading is of a committed netlist or a maker's document; nothing is built.

- 13:16 Brief read (`_runs/claude/rf2walk/BRIEF.md`); worktree created. `check_contracts.py` run into a scratch directory
  (`env -C <scratch> VERDICT_DIR=<scratch>`, never from `v2/ecad`): 21 FAIL, byte for byte the coordinator's
  `contracts-int13-e41df395.txt`; the tree stays clean. Main (`2c7730a4`) read in a scratch copy of its whole `v2/ecad`
  (`git archive`): main's own tool gives main's file back unchanged (0 FAIL); the set 12 tool on main's netlists reads 0 FAIL,
  11 UNDECIDED (`7dc74508`, stream d4emcon's earlier walk rows, makes four of main's PASS rows UNDECIDED on the radios' own
  pins and adds the PA gate-bias row). A narrower copy (the out/ files only) refused every board as UNKNOWN GENERATOR: the
  netlist provenance check needs the generators' whole input closure.
- 13:17 to 13:20 The two asserted-line FAILs read from the walk's own code (`tx_inhibit.census`, `_line_sources`,
  `fail_safe`): the panel's buffer is recognised as a line's source only when its output is ON the line (`n in SOURCES`).
  Since D4E-F1, U9 pin 4 sits on `EMCON_HW_DRV` behind R52, so (a) the census, reaching it from `EMCON_HW` through R52 and
  from `TX_INHIBIT_n` through D23 and R52, reads "a second BUF output", and (b) `fail_safe` finds no source on board C, never
  takes board C down, and solves the line with U9 powered and driving 3.3 V through R52: 3.18 V, "no source on the line at
  all". The 18 transmitter rows fail on their line alone ("its line EMCON_HW fails" or "TX_INHIBIT_n fails"). The census
  row fails on U543, whose value names the RockBLOCK and which no list classifies. Every one of the 21 is the instrument.
- 13:20 to 13:24 Fix 1 (`drive_net`, `_source_output`, `_line_sources`, the census's buffer clause): a net that carries,
  test points aside, exactly one mapped logic output whose inputs all sit on asserted lines and one end of a two-pin
  resistor whose other end is an asserted line is that line's drive net, and the output its source. Set 12 then: 1 FAIL
  (the census), `TX_INHIBIT_n` PASS, `EMCON_HW` UNDECIDED "C D23 (BAT46W): a diode whose reverse current no held sheet
  states" in the two states with board C down.
- 13:24 D23 read from its maker (Diodes DS30044 Rev. 20-2, `v2/vendor/diodes/diodes-bat46w.pdf`): IR 0.3 uA at VR 1.5 V
  (+25 C) and 5.0 uA at VR 1.5 V, TJ +60 C; nothing at +85 C, the walk's column; Figure 2 is typical only. Fix 2
  (`REVERSE_IDEAL`): a diode is passive, so its reverse current cannot carry the net above the far node; where the far node
  is the OTHER asserted line (whose own fail-safe level the walk judges on the same states), the reverse direction enters
  the network as an ideal one-way element, and a state that fails only with it is UNDECIDED (the second solve, as for
  ASSUMED). In set 12's states it never conducts (TX_INHIBIT_n sits below EMCON_HW in every state), and EMCON_HW reads 0.584 V
  worst (J_AB1 unplugged, board C down), TX_INHIBIT_n 0.578 V worst. First written for any unfixed far node; that changed
  the existing BAT54 fixture's reason (the MCU pin's unbounded off-state current named instead of the diode), so it was
  narrowed to the other asserted line: no existing test or wording moves.
- 13:25 Fix 3: U543 declared in ACCESSORIES from TI SBVS050N page 1 (a supervisor whose one output is an open drain), as
  U221 was by stream w4b. Set 12: 0 FAIL, 11 UNDECIDED, 15 PASS; main with the fixed walk: byte-identical to the unfixed set
  12 walk's reading of main (0 FAIL, 11 UNDECIDED).
- 13:25 to 13:29 Tests (`tests/test_tx_inhibit.py`, three new, each with an acceptable and a defective fixture):
  `t_the_panels_buffer_behind_its_series_resistor_is_the_lines_own_source`,
  `t_a_diodes_reverse_current_toward_a_line_is_bounded_by_that_lines_own_level`,
  `t_a_supervisor_whose_value_names_the_rockblock_is_classified_only_when_declared`. The file: 136 passed, 0 failed. The
  three new tests on the unfixed walk (a scratch copy of the tools with HEAD's `tx_inhibit.py`): all three FAIL. Readings
  filed under `readings/`.
- 13:29 to 13:33 Circuit question answered from the walk and the documents: the 3.18 V is U9 itself (push-pull, DS35124),
  taken powered in a state the walk misnamed "no source", 3.465 V through R52 into R58 parallel R102 at their adverse ends,
  plus about 111 uA of pin currents. D23 merges `EMCON_HW`'s pin currents into `TX_INHIBIT_n` (0.243 V on main to 0.354 V
  with board C down, all four boards; per-fragment levels read with a spy on `_judge_fs`: `EMCON_HW` identical to main in
  every fragment, `TX_INHIBIT_n` higher only in the fragments that hold board C, worst 0.578 V in A and D alone, unchanged);
  its reverse element never conducts. No circuit defect, no apply script. README.md written with the table of the 21 FAILs,
  the readings and what remains (the 11 UNDECIDED rows, the same rows as main's under the same walk, their grounds narrower on
  set 12 for the RockBLOCK, the E22 and both E72).
- 13:33 `tests/run.py contract inhibit requirements`: 289 passed, 4 failed, 5 skipped. The four are
  `test_requirements`' registry and trace-page tests, failing on set 12's own state: PASS records (CON-017, CON-025, CFL-001,
  CFL-004, CFL-016) are bound to `gen_sch_b.py` and boards B and C's netlists at their hashes before set 12's regeneration.
  No record binds `tx_inhibit.py` or its tests, and this stream's commits touch only those two files and this folder, so the
  rebind is the integrator's, as after every regeneration. The tree's committed `inhibit_chain_<letter>` verdicts were written
  by the unfixed walk and are re-taken by the integrator with the tool change (no gate was run in the tree here).

## Where the stream stands (29 September 2026, 13:33)

All 21 FAILs are the instrument: 2 asserted-line rows (the panel's buffer behind its series resistor R52 not recognised as
the line's source), 18 transmitter rows inherited from them, and 1 census row (U543, a TPS3808 whose value names the
RockBLOCK, undeclared). No circuit defect; no apply script. With the fixed walk: set 12 reads 0 FAIL, 11 UNDECIDED, 15 PASS;
main reads byte for byte what set 12's unfixed walk read on main (0 FAIL, 11 UNDECIDED, 15 PASS). For the integrator: merge
`fnd/rf2walk`, re-take RF-002 (`inhibit_chain_<letter>`) and the rest of set 12's re-take, rebind the registry records bound
to board B and C's regenerated netlists and `gen_sch_b.py`, render.

## Second round: the independent check of set 12 (branch `fnd/rf2walk2` from `fnd/int13` at `eafb324d`)

- 13:56 The check read (`_scratch/chk-set12/CHECK.md`, read only; its `_chk/` scripts run from a scratch cwd with the tools
  directory as argument, nothing written there): mergeable no, 1 blocking, 7 minor; the remedies B-1 to B-5 and D4E-F1 hold
  at the stated worst case. Worktree `rf2walk2` created from `fnd/int13` at `eafb324d`.
- 13:57 to 13:59 B1 (blocking). The check's CX9, two 74LVC1G34 on board B cross-coupled between the two lines (each input on
  one line, each output on the other, behind its own 330R or directly), read PASS on both lines under this stream's first
  walk: each gate was classed "the line's own source" and `fail_safe` took board B down with it in every state, so the
  powered latch was never solved; the direct form had read PASS under every walk since the on-net rule. Fix in
  `tx_inhibit.py`: `_switch_board(nl)`, a board carrying a SW part with a pin on an asserted line (board C's SW_EMCON on
  TX_INHIBIT_n); a logic output counts as a line's own source (the census's on-net clause, `_source_output`, so
  `drive_net` and `_line_sources`) only on that board; and `_fs_base` no longer forces a counted source off whatever its
  rails do (`off` empty): the toggle's board down removes the rails it makes, and a gate on a rail that board receives over a
  plugged ribbon stays powered and is solved.
- 13:59 to 14:00 Readings, each `check_contracts.py` into scratch on a `git archive` of the whole `v2/ecad`: set 12 at
  `eafb324d` before and after, byte-identical (0 FAIL, 11 UNDECIDED, 114 PASS); main `2c7730a4` with the previous walk and
  with this one, byte-identical (0 FAIL, 11 UNDECIDED); main with its own walk 0 FAIL, 7 UNDECIDED (the `7dc74508` rows, as
  before). The check's `cx_walk.py` on the previous and the new walk (`readings/b1/check-cx-walk-*.txt`): CX9 behind and
  direct, and CX3, CX3b, CX3c, move from PASS to FAIL on EMCON_HW (and CX9 on TX_INHIBIT_n); every other counterexample reads
  as before. Fixtures `t_a_latch_of_two_buffers_across_the_lines_fails_both_lines` (CX9 on board B behind resistors and direct,
  and on board C from the +5V it receives, both lines FAIL; D4E-F1's shape still passes) and
  `t_a_follower_off_the_switchs_board_is_a_second_driver` (CX3b): `test_tx_inhibit` 138 passed; both new tests FAIL on the
  previous walk (CX9 on board B reads PASS on both lines there, on board C UNDECIDED and FAIL). `tests/run.py contract inhibit
  requirements evidence rules_status stale`: 388 passed, 0 failed, 8 skipped; the tree unchanged but for the two files.
- 14:00 to 14:07 The circuit minors of stream d4emcon's remedies drafted as `apply_b_chk12.py` against set 12's
  `gen_sch_b.py` (not applied; dry run, a scratch copy applied once and refused a second run, the result parses, the new
  module rail declarations evaluated for slots 1 to 3):
  M1 (minor 1) R238 49.9 k 1% (C23184, R297's code): held 72 uA (SCES308L 100 uA row), released 2.08 V at the module's
  nominal 100 k and at or over 1.19 V down to a 30.8 k pull-down, whose tolerance Quectel does not state.
  M2 (minor 2) R532 2.7 k 1% (C13167) keeps U543's sink at 0.955 mA at most up to its 2.90 V rising threshold, inside the
  1 mA VOL row; R527 20.0 k 1% (C4184) keeps the released level at 2.10 V (asserted 0.16 V, every rail lost 0.37 V);
  CT to +5V_DEV through R551 49.9 k 1%: td 180 to 420 ms. The 9704's I_EN-low-to-I_BTD-low time is in no held document:
  bench E-04 measures it, and CT becomes a capacitor if it can exceed 180 ms.
  M5 (minor 5) the module rails' loads and notes from set 12's netlist (U{s}12 to U{s}15 on every slot, already missing at
  round 8, slot 2's U220 and U554, slot 3's U544 to U553, 1 mA a gate) and +3V3_ZB's R536 to R538.
  Read-back `tools/readback_chk12.py` (parses the netlist and the intent JSON; a module rail's loads are compared with the
  logic parts the netlist puts on it): 10 FAIL of 11 on set 12's committed board B (only U543's open MR passes), as it must
  before regeneration; `tools/selftest_readback_chk12.py`: it passes a synthetic after-pair and fails three mutants.
- 14:07 to 14:09 EMCON.md section 4d.6 written (the check's minors on this stream's remedies corrected in place, the drafts
  named, the walk's change) and bench E-04 extended with the 9704's I_EN-low-to-I_BTD-low time; no claim word, no non-ASCII
  character; `test_requirements` 65 passed with the page changed (the seven records bound to it are FAIL or INCONCLUSIVE, so
  the moved page warns). `apply_rebind_page_rf2walk2.py` written for the integrator (the d4emcon page phase refuses a second
  run): tried in the worktree, 7 records rebound 173bc6357996d467 to the page's new sha, a second run refused, the registry
  restored. README.md gains the second round.

## Where the stream stands (29 September 2026, 14:10)

B1 closed in the walk (`149b15f7`): a gate is a line's own source only on the board carrying SW_EMCON and is solved by its own
rails; CX9 in both forms and CX3b fail as fixtures, and both fail on the previous walk; set 12 and main read byte for byte as
before (0 FAIL, 11 UNDECIDED, 15 PASS). The check's minors on this stream's remedies: drafted for board B as `apply_b_chk12.py`
(M1, M2, M5) with `tools/readback_chk12.py`, stated in EMCON.md 4d.6 (minors 3, 4, 6, 7), and bench E-04 extended.
Open: the 9704's shutdown time (E-04, sets U543's td), B-3's turn-on exposure, the module pull-down tolerance behind B-5,
the regeneration and read-back of `apply_b_chk12.py`, and the 11 UNDECIDED rows as listed in README.md.
