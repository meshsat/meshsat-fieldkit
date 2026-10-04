# l8p: W4DP-F2's breaker drawn for boards P, E and A (Layer 8, MESHSAT-1357)

Layer 8 record `l8p`, 4 October 2026, branch `fnd/l8p` from main `64cd25ee`. It draws record `l9stk` section 15's design
(branch `fnd/l9stk` at `0d72880b`, its latest changes CONFIRMED AS CONDITIONAL):
- an LM5069-1 latch-off breaker on board P;
- its make-last dock enable loop through boards E and A, with an RC hold through a diode;
- the PTC thermal guard on board A;
- the restart inhibit C-1c on the breaker pad (DD-8, owned here);
- round 3 (branch `fnd/l8p2` from `fnd/l8p` at `e1bc3cba`): B-R2's route R1, a reverse-charge detector on board P that holds the
  loop's return low while a latched or held-off breaker passes a charge, read by board A on the contact it already has (task
  L4-E11's round 9, `fnd/l4e11r9` at `e60a94a8`, section 19h).

Round 1 drew the record at `2c8b29fb`; round 2 (the same day) follows its move.

This is prototype design: generator text and netlists only. Nothing is built, powered or measured, and **nothing here is
applied to the tree**. Every apply script refuses the repository's own generator until a `RELEASE.md` beside it names an
accepted check of this record; none exists.

| File | What it is |
|---|---|
| `L8P-BREAKER.md` | The record page: the drafts, the values with their l9stk sections, the SESSION choices, C-1c's budget and conditions (E-12b, E-10, the lockout, the NTC's assumed tolerance), the designators, the order constraints for L4-E9's change list, the interface rows owed, the regeneration and the netlist check, findings for other authors, residuals, and (section 12) B-R2: why no existing element serves, the detector, its thresholds and limits, the service, the interface owed to L4-E11, E-14 as it now reads and E-12c. |
| `apply_gen_sch_p_breaker.py` | DRAFT, board P: U101 LM5069-1, R101 and R102 (4 and 7.5 mOhm), Q101 and Q102 CSD18510Q5B, R103 8.45 k, C101 10 nF, C102 22 nF, D101 SMCJ18A, C104 and C105. The enable inverters Q103 and Q104 with R106 to R109, and the hold: R104, C103, R105 and D102 1N4148W. The restart inhibit: RT101 NXRT15 on the pad, R110 to R113, U102 OPA187, Q105 and Q106 gated by PGD (R114 to R117), C106. TP101 to TP106. Round 3, the reverse-charge detector: U103 and U104 OPA187, D103 BZT52C12, R118 to R129, C107 to C110, Q107 and Q108 on DOCK_EN_RET, TP107 and TP108. J_SMB as a 1x7 (5 DOCK_EN_RET, 6 ground, 7 DOCK_EN_OUT). R6, R7, R19 and Q2's source on BRK_VIN. |
| `apply_gen_sch_e_enable.py` | DRAFT, board E: J_SMB as a 1x7 pin for pin; J_BLK pins 3 and 5 on the loop with 4 ground between. |
| `apply_gen_sch_a_ptc.py` | DRAFT, board A: J_DOCK pins 3 and 5 on the loop with 4 ground between; RT1 PRF15BB103 on the battery FETs' copper. |
| `check_l8p_netlist.py` | What the regenerated netlists must show, parsed: the breaker, the loop on each board, the hold, the restart inhibit and its PGD gate, the reverse-charge detector (REV), the ground contact between the loop conductors, and the loop's continuity across the boards. It reads NOT DRAWN on the committed netlists. |
| `gen_netlist.py` | A generator's own part table written as a KiCad-form netlist on a host without KiCad: a stand-in layout step, with `intent.write` run. |
| `fetch_held_back.py` | TI's OPA187 sheet (SBOS807E) into `v2/vendor/ti/held/`, checked by sha256 (held back by TI's notice). |
| `l8p_drafts.py`, `l8p_drafts.out` | The inputs pinned by sha256, the values found in l9stk's text, C-1c's budget read from the makers' sheets, B-R2's detector (section 3b), each draft on a scratch copy, the composition in L4-E9's order, the designators, the regeneration and the netlist check, the intent, and the findings. Regenerated with `_bin/regen_out.py`. |
| `inputs/` | Record l9stk's section 15, its protection output and its design constants at `0d72880b`, L4-E7's backstop draft of `fnd/l4e7r6` at `914a2f5a`, and task L4-E11's sections 19h and 15c (the LDO-mode precharge) at `e60a94a8`, byte for byte, with `inputs/SOURCES.txt`. |

Tests: `v2/ecad/tools/tests/test_l8p.py`. Run `python3 run.py test_l8p test_l8r2 test_public_hygiene` from the tests folder.
