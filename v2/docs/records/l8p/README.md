# l8p: W4DP-F2's breaker drawn for boards P, E and A (Layer 8, MESHSAT-1357)

Layer 8 record `l8p`, 4 October 2026, branch `fnd/l8p` from main `64cd25ee`. It draws record `l9stk` section 15's design
(branch `fnd/l9stk` at `2c8b29fb`, CONFIRMED AS CONDITIONAL): an LM5069-2 breaker on board P with its make-last dock enable
loop through boards E and A and the PTC thermal guard on board A.

This is prototype design: generator text and netlists only. Nothing is built, powered or measured, and **nothing here is
applied to the tree**. Every apply script refuses the repository's own generator until a `RELEASE.md` beside it names an
accepted check of this record; none exists.

| File | What it is |
|---|---|
| `L8P-BREAKER.md` | The record page: the drafts, the values with their l9stk sections, the SESSION choices, the designators, the order constraints for L4-E9's change list, the interface rows owed, the regeneration and the netlist check, findings for other authors, and residuals. |
| `apply_gen_sch_p_breaker.py` | DRAFT, board P: U101 LM5069-2, R101 and R102 (4 and 7.5 mOhm), Q101 and Q102 CSD18510Q5B, R103 8.45 k, C101 10 nF, C102 22 nF, D101 SMCJ18A, C104 and C105. The enable inverters Q103 and Q104 with R104 to R109 and C103 (the RC hold), TP101 to TP104. J_SMB as a 1x7 (5 DOCK_EN_RET, 6 ground, 7 DOCK_EN_OUT). R6, R7, R19 and Q2's source on BRK_VIN. |
| `apply_gen_sch_e_enable.py` | DRAFT, board E: J_SMB as a 1x7 pin for pin; J_BLK pins 3 and 5 on the loop with 4 ground between. |
| `apply_gen_sch_a_ptc.py` | DRAFT, board A: J_DOCK pins 3 and 5 on the loop with 4 ground between; RT1 PRF15BB103 on the battery FETs' copper. |
| `check_l8p_netlist.py` | What the regenerated netlists must show, parsed: the breaker, the loop on each board, the ground contact between the loop conductors, and the loop's continuity across the boards. It reads NOT DRAWN on the committed netlists. |
| `gen_netlist.py` | A generator's own part table written as a KiCad-form netlist on a host without KiCad: a stand-in layout step, with `intent.write` run. |
| `l8p_drafts.py`, `l8p_drafts.out` | The inputs pinned by sha256, the values found in l9stk's text, each draft on a scratch copy, the composition in L4-E9's order, the designators, the regeneration and the netlist check, the intent, and the findings. Regenerated with `_bin/regen_out.py`. |
| `inputs/` | Record l9stk's section 15, its protection output and its design constants at `2c8b29fb`, byte for byte, with `inputs/SOURCES.txt`. |

Tests: `v2/ecad/tools/tests/test_l8p.py`. Run `python3 run.py test_l8p test_l8r2 test_public_hygiene` from the tests folder.
