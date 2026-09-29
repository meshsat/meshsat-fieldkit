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
- 13:33 to 13:34 `tests/run.py contract inhibit requirements`: 289 passed, 4 failed, 5 skipped. The four are
  `test_requirements`' registry and trace-page tests, failing on set 12's own state: PASS records (CON-017, CON-025, CFL-001,
  CFL-004, CFL-016) are bound to `gen_sch_b.py` and boards B and C's netlists at their hashes before set 12's regeneration.
  No record binds `tx_inhibit.py` or its tests, and this stream's commits touch only those two files and this folder, so the
  rebind is the integrator's, as after every regeneration. The tree's committed `inhibit_chain_<letter>` verdicts were written
  by the unfixed walk and are re-taken by the integrator with the tool change (no gate was run in the tree here).

## Where the stream stands (29 September 2026, 13:34)

All 21 FAILs are the instrument: 2 asserted-line rows (the panel's buffer behind its series resistor R52 not recognised as
the line's source), 18 transmitter rows inherited from them, and 1 census row (U543, a TPS3808 whose value names the
RockBLOCK, undeclared). No circuit defect; no apply script. With the fixed walk: set 12 reads 0 FAIL, 11 UNDECIDED, 15 PASS;
main reads byte for byte what set 12's unfixed walk read on main (0 FAIL, 11 UNDECIDED, 15 PASS). For the integrator: merge
`fnd/rf2walk`, re-take RF-002 (`inhibit_chain_<letter>`) and the rest of set 12's re-take, rebind the registry records bound
to board B and C's regenerated netlists and `gen_sch_b.py`, render.
