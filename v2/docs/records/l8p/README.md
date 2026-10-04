# l8p: W4DP-F2's breaker drawn for boards P, E and A (Layer 8, MESHSAT-1357)

Layer 8 record `l8p`, 4 October 2026, branch `fnd/l8p` from main `64cd25ee`. It draws record `l9stk` section 15's design
(branch `fnd/l9stk` at `0d72880b`, its latest changes CONFIRMED AS CONDITIONAL):
- an LM5069-1 latch-off breaker on board P;
- its make-last dock enable loop through boards E and A, with an RC hold through a diode;
- the PTC thermal guard on board A;
- the restart inhibit C-1c on the breaker pad (DD-8, owned here).

Round 1 drew the record at `2c8b29fb`; round 2 (the same day) follows its move.

This is prototype design: generator text and netlists only. Nothing is built, powered or measured, and **nothing here is
applied to the tree**. Every apply script refuses the repository's own generator until a `RELEASE.md` beside it names an
accepted check of this record; none exists.

| File | What it is |
|---|---|
| `L8P-BREAKER.md` | The record page: the drafts, the values with their l9stk sections, the SESSION choices, C-1c's budget and conditions (E-12b, E-10, the lockout, the NTC's assumed tolerance), the designators, the order constraints for L4-E9's change list, the interface rows owed, the regeneration and the netlist check, findings for other authors, and residuals. |
| `apply_gen_sch_p_breaker.py` | DRAFT, board P: U101 LM5069-1, R101 and R102 (4 and 7.5 mOhm), Q101 and Q102 CSD18510Q5B, R103 8.45 k, C101 10 nF, C102 22 nF, D101 SMCJ18A, C104 and C105. The enable inverters Q103 and Q104 with R106 to R109, and the hold: R104, C103, R105 and D102 1N4148W. The restart inhibit: RT101 NXRT15 on the pad, R110 to R113, U102 OPA187, Q105 and Q106 gated by PGD (R114 to R117), C106. TP101 to TP106. J_SMB as a 1x7 (5 DOCK_EN_RET, 6 ground, 7 DOCK_EN_OUT). R6, R7, R19 and Q2's source on BRK_VIN. |
| `apply_gen_sch_e_enable.py` | DRAFT, board E: J_SMB as a 1x7 pin for pin; J_BLK pins 3 and 5 on the loop with 4 ground between. |
| `apply_gen_sch_a_ptc.py` | DRAFT, board A: J_DOCK pins 3 and 5 on the loop with 4 ground between; RT1 PRF15BB103 on the battery FETs' copper. |
| `check_l8p_netlist.py` | What the regenerated netlists must show, parsed: the breaker, the loop on each board, the hold, the restart inhibit and its PGD gate, the ground contact between the loop conductors, and the loop's continuity across the boards. It reads NOT DRAWN on the committed netlists. |
| `gen_netlist.py` | A generator's own part table written as a KiCad-form netlist on a host without KiCad: a stand-in layout step, with `intent.write` run. |
| `fetch_held_back.py` | TI's OPA187 sheet (SBOS807E) into `v2/vendor/ti/held/`, checked by sha256 (held back by TI's notice). |
| `l8p_drafts.py`, `l8p_drafts.out` | The inputs pinned by sha256, the values found in l9stk's text, C-1c's budget read from the makers' sheets, each draft on a scratch copy, the composition in L4-E9's order, the designators, the regeneration and the netlist check, the intent, and the findings. Regenerated with `_bin/regen_out.py`. |
| `inputs/` | Record l9stk's section 15, its protection output and its design constants at `0d72880b`, and L4-E7's backstop draft of `fnd/l4e7r6` at `914a2f5a`, byte for byte, with `inputs/SOURCES.txt`. |

Tests: `v2/ecad/tools/tests/test_l8p.py`. Run `python3 run.py test_l8p test_l8r2 test_public_hygiene` from the tests folder.
