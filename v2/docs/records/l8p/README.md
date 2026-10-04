# l8p: W4DP-F2's breaker drawn for boards P, E and A (Layer 8, MESHSAT-1357)

**Round 5 (4 October 2026 evening, branch `fnd/l8p2`): the check V1's condition C4 DONE on this branch; L8P-F06 and L8P-F07 OPEN.**
- Done: `check_l8p_netlist.py`'s board A EN group admits DD-7's readers by pin (L4E11-R10-F2), three mutations of the composed board A
  fail it; the compositions use L4-E11's round 10 drafts (`fnd/l4e11r10` at `a09e9a60`, byte-for-byte copies listed in
  `inputs/SOURCES.txt` round 5) with no stand-in, boards E and A run to their end; `l8p_drafts.out` regenerated through
  `_bin/regen_out.py`; the page's 12f restated from L4-E11's 20c and 20d (quoted, a test reads every quote against the copies), 12i,
  section 9, and the new 12j: L8P-F06 (the breaker FETs' hot off leakage inside L4-E11's 0.846 mA latch) and L8P-F07 (RT1's printed
  points; on Murata's typical curve the guard reaches the first inverter's turn-off at record l9stk's held 18 A reading), the Murata
  and TI questions DRAFTED and UNSENT, TDK's B59721A and Murata's PRF15BA102 named and not selected; `test_l8p` (15 passed),
  `test_l8r2` and `test_public_hygiene` pass.
- The scratch merge with `a09e9a60` (read-only: `git merge-tree --write-tree` of `85447c4e` and `a09e9a60`, no merge in progress):
  CLEAN, tree `66e753a7`; it brings only `records/l4e11/` and `test_l4e11.py`. On that tree, built as a scratch overlay (L4-E11's
  held sheets linked read-only from other worktrees and checked by its `fetch_held_back.py`): `l8p_drafts.py` prints this
  `l8p_drafts.out` byte for byte, `test_l8p` 15 passed, `test_l4e11` 65 passed, 0 failed, 0 skipped. That meets V1's closure for C4
  on a scratch merge; the committed candidate and its suite are the integrator's.
- Next: the independent check V2 of the changed technical claims (F06, F07, the alternative parts) with T2, T3 and T4; record l9stk's
  guard round for F07; L4-E11's latch budget for F06.

Layer 8 record `l8p`, 4 October 2026, branch `fnd/l8p` from main `64cd25ee`. It draws record `l9stk` section 15's design
(branch `fnd/l9stk` at `0d72880b`, its latest changes CONFIRMED AS CONDITIONAL):
- an LM5069-1 latch-off breaker on board P;
- its make-last dock enable loop through boards E and A, with an RC hold through a diode;
- the PTC thermal guard on board A;
- the restart inhibit C-1c on the breaker pad (DD-8, owned here);
- round 3 (branch `fnd/l8p2` from `fnd/l8p` at `e1bc3cba`): B-R2's route R1, a reverse-charge detector on board P that holds the
  loop's return low while a latched or held-off breaker passes a charge, read by board A on the contact it already has (task
  L4-E11's round 9, `fnd/l4e11r9` at `e60a94a8`, section 19h);
- round 4 (the same branch): the correction of design defect DD-5 (BAT-F20), an ideal diode beside the charge switch Q1, so the
  discharge no longer crosses Q1's body diode while the gauge holds the charge FET off (case row C-PROT with CHGIN = 1).

Round 1 drew the record at `2c8b29fb`; round 2 (the same day) follows its move.

This is prototype design: generator text and netlists only. Nothing is built, powered or measured, and **nothing here is
applied to the tree**. Every apply script refuses the repository's own generator until a `RELEASE.md` beside it names an
accepted check of this record; none exists.

| File | What it is |
|---|---|
| `L8P-BREAKER.md` | The record page: the drafts, the values with their l9stk sections, the SESSION choices, C-1c's budget and conditions (E-12b, E-10, the lockout, the NTC's assumed tolerance), the designators, the order constraints for L4-E9's change list, the interface rows owed, the regeneration and the netlist check, findings for other authors, residuals, and (section 12) B-R2: why no existing element serves, the detector, its thresholds and limits, the service, the interface owed to L4-E11, E-14 as it now reads and E-12c; and (section 13) DD-5: the three approaches, the ideal diode, its acceptance on C-PROT with every figure labelled, the closure credit and what stays open (E-8, E-16, E-12d). |
| `apply_gen_sch_p_breaker.py` | DRAFT, board P: U101 LM5069-1, R101 and R102 (4 and 7.5 mOhm), Q101 and Q102 CSD18510Q5B, R103 8.45 k, C101 10 nF, C102 22 nF, D101 SMCJ18A, C104 and C105. The enable inverters Q103 and Q104 with R106 to R109, and the hold: R104, C103, R105 and D102 1N4148W. The restart inhibit: RT101 NXRT15 on the pad, R110 to R113, U102 OPA187, Q105 and Q106 gated by PGD (R114 to R117), C106. TP101 to TP106. Round 3, the reverse-charge detector: U103 and U104 OPA187, D103 BZT52C12, R118 to R129, C107 to C110, Q107 and Q108 on DOCK_EN_RET, TP107 and TP108. J_SMB as a 1x7 (5 DOCK_EN_RET, 6 ground, 7 DOCK_EN_OUT). R6, R7, R19 and Q2's source on BRK_VIN. |
| `apply_gen_sch_p_idealdiode.py` | DRAFT, board P, round 4 (DD-5), after the breaker draft: Q109 CSD17570Q5B beside Q1 under U105 LM74700-Q1, C111, R130, D104, R131, C112 to C115, TP109. |
| `apply_gen_sch_e_enable.py` | DRAFT, board E: J_SMB as a 1x7 pin for pin; J_BLK pins 3 and 5 on the loop with 4 ground between. |
| `apply_gen_sch_a_ptc.py` | DRAFT, board A: J_DOCK pins 3 and 5 on the loop with 4 ground between; RT1 PRF15BB103 on the battery FETs' copper. |
| `check_l8p_netlist.py` | What the regenerated netlists must show, parsed: the breaker, the loop on each board, the hold, the restart inhibit and its PGD gate, the reverse-charge detector (REV), the ideal diode beside Q1 (DIO), the ground contact between the loop conductors, and the loop's continuity across the boards. It reads NOT DRAWN on the committed netlists. |
| `gen_netlist.py` | A generator's own part table written as a KiCad-form netlist on a host without KiCad: a stand-in layout step, with `intent.write` run. |
| `fetch_held_back.py` | TI's OPA187 sheet (SBOS807E) into `v2/vendor/ti/held/` and, round 5, TDK's superior-series PTC sheet into `v2/vendor/battery/held/`, each checked by sha256 (held back by their notices). |
| `read_prf_typical.py` | Round 5: the reading of Murata's typical BB curve (DM-SA16-E056 Rev.1, 3.2) that `l8p_drafts.py` carries as `PRF_BB_TYP`, INFERRED; a reading aid, not a gate. |
| `l8p_drafts.py`, `l8p_drafts.out` | The inputs pinned by sha256, the values found in l9stk's text, C-1c's budget read from the makers' sheets, B-R2's detector (section 3b), DD-5's acceptance (section 3c), each draft on a scratch copy, the composition in L4-E9's order, the designators, the regeneration and the netlist check, the intent, and the findings. Regenerated with `_bin/regen_out.py`. |
| `inputs/` | Record l9stk's section 15, its protection output and its design constants at `0d72880b`, L4-E7's backstop draft of `fnd/l4e7r6` at `914a2f5a`, and task L4-E11's sections 19h and 15c (the LDO-mode precharge) at `e60a94a8`, byte for byte, with `inputs/SOURCES.txt`; round 5: L4-E11's round 10 drafts and its sections 20c, 20d and 20e at `a09e9a60`. |

Tests: `v2/ecad/tools/tests/test_l8p.py`. Run `python3 run.py test_l8p test_l8r2 test_public_hygiene` from the tests folder.
