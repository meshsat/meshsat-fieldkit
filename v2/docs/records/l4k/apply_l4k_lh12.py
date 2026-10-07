#!/usr/bin/env python3
"""K-03 (record l4k, MESHSAT-1357, W131, 7 October 2026): record l4e9's Layer 5 handover entry LH-12 restated to the register's
R-28, and test_l4e9's reading of LH-12 restated with it. FOR THE INTEGRATOR, on set 33's integrated tree; not applied on fnd/l4k.

The contradiction (the DESK-gate assessment's K-03, standing on main be07863b): FAN_OK and its three rows are WITHDRAWN,
  be07863b:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:306 "| WITHDRAWN | 3g |" (R-210; R-211 and R-212 the same at :307, :308),
and R-28 reads K4's off-list "the fans NOT on it: round 8's fans while keyed WITHDRAWN 5 October 2026 with R-210 to R-212" and
"LH-12's text is restated by its owner record the same way (set 31, PC-08)" (be07863b:...DOWNSTREAM-REGISTER.md:134), while
  be07863b:v2/docs/records/l4e9/LAYER5-HANDOVER.md:28 still proposes "the outlets, the heater and the fans off while keyed (the
  fans' supplies through FAN_OK, R-210 to R-212)" in state DRAFTED.
The authoritative value is R-28's (the owner's rejection of FAN_OK, the P0 brief of 5 October 2026). LH-12 keeps its id, its row
IF-10 and its state DRAFTED (it still carries a contract instruction: FW-A05's floors at REQ-018's pass lines); its fans clause is
quoted and marked WITHDRAWN, its round 8 basis kept as dated history, and its Why cell names D-17's correction as the register does
(R-227 and R-238; C-ALLTX rev 3 at the cap's top needs 15.1308 V, a MODEL margin of 0.3692 V under 15.5 V, record l9t5's
l9t5_f01.out, be07863b line 145, set 32's line 167: the figure is unchanged there).

Why a script and not an edit on fnd/l4k (authority SESSION, W131; reversed by running the two edits by hand on set 33's tree):
LAYER5-HANDOVER.md is not changed by set 32, but its sha256 is pinned by record l5pwr's l5pwr_contracts.out (its input line
`hand`), an output set 32 regenerates (fnd/int32 4c8196a0). An edit here would leave that pin stale on this branch and collide
with set 32's regeneration; applied on set 33's tree, the chain re-pins it once.

Outputs that move after the apply (named for set 33's regeneration, not regenerated here): v2/docs/records/l5pwr/l5pwr_contracts.out
(the `hand` sha256 line; no figure of LH-12 is read by l5pwr_contracts.py). record l4e9's l4e9_power_path.out reads the handover
table's count and its IF rows only (12 entries, IF-10 kept): unchanged.

The test (v2/ecad/tools/tests/test_l4e9.py, t_decision_d11s_all_transmit_floor_on_the_final_drafts_is_open_and_its_design_out_bounded):
its line `"the fans off while keyed" in lh[0][2]` held round 8's proposal as current; restated on the same line to hold LH-12 at
R-28's reading (the fans NOT on it, FAN_OK named once and only inside the WITHDRAWN quotation, the floors and DRAFTED kept). Basis:
R-28 and R-210 to R-212 WITHDRAWN (the register, lines 134 and 306 to 308 at be07863b). The old LH-12 row fails the restated line
(no "the fans NOT on it"), so the line refuses the text it replaces.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _l4k_apply import run  # noqa: E402

HAND = "v2/docs/records/l4e9/LAYER5-HANDOVER.md"
TEST = "v2/ecad/tools/tests/test_l4e9.py"

OLD_ROW = ("| LH-12 | HW-FW-CONTRACT.md FW-A05: K4's off-list with the fans (round 8, D-17's design-out; Layer 9's L9P-F01 on the final "
           "drafts) | In \"the outlets and the heater off while keyed\" read \"the outlets, the heater and the fans off while keyed (the "
           "fans' supplies through FAN_OK, R-210 to R-212)\"; the floors stay \"SoC floors 15.5 V and 12.4 V rest\", REQ-018's pass "
           "lines (round 7's 16.1 V text withdrawn: a raised floor narrows REQ-018). Why: the basis (every transmitter keyed, "
           "non-transmit loads typical, the standby card off, every other load at HIGH) at 18 A needs 16.214 V rest at R_cell 0.06 "
           "Ohm on the final drafts; with the five fans off while keyed at most 15.374 V (a bound), at least +0.126 V under 15.5 V, "
           "CONDITIONAL on R-213; the firmware owner implements it (R-28) | IF-10 | DRAFTED |")
NEW_ROW = ("| LH-12 | HW-FW-CONTRACT.md FW-A05: K4's off-list and the floors (round 8's fans clause WITHDRAWN 5 October 2026 with "
           "R-210 to R-212, the owner's rejection of FAN_OK; D-17's correction the PA drain-current cap, R-227 and R-238; Layer 9's "
           "L9P-F01 on the final drafts) | In \"the outlets and the heater off while keyed\" nothing is added for the fans: round 8's "
           "reading \"the outlets, the heater and the fans off while keyed (the fans' supplies through FAN_OK, R-210 to R-212)\" is "
           "WITHDRAWN, so K4's off-list is the one the register's R-28 states, the fans NOT on it; the floors stay \"SoC floors 15.5 "
           "V and 12.4 V rest\", REQ-018's pass lines (round 7's 16.1 V text withdrawn: a raised floor narrows REQ-018). Why: D-17's "
           "correction is the PA drain-current cap (R-227 and R-238, F01 / D-17 PROVISIONAL): C-ALLTX rev 3 at the cap's top needs "
           "15.1308 V, a MODEL margin of 0.3692 V under 15.5 V (record l9t5's l9t5_f01.out); round 8's basis (16.214 V rest needed "
           "at 18 A at R_cell 0.06 Ohm on the final drafts, at most 15.374 V with the five fans off while keyed, CONDITIONAL on "
           "R-213) is WITHDRAWN history; the firmware owner implements R-28. Restated 7 October 2026 by record l4k (the DESK-gate "
           "assessment's K-03; R-28: LH-12 is restated by its owner record the same way) | IF-10 | DRAFTED |")

OLD_TEST = ('    assert len(lh) == 1 and "the fans off while keyed" in lh[0][2] and "SoC floors 15.5 V and 12.4 V rest" in lh[0][2] '
            'and lh[0][4] == "DRAFTED"\n')
NEW_TEST = ('    assert len(lh) == 1 and "SoC floors 15.5 V and 12.4 V rest" in lh[0][2] and lh[0][4] == "DRAFTED" and "the fans NOT on '
            'it" in lh[0][2] and lh[0][2].count("FAN_OK") == 1 and "R-210 to R-212)\\" is WITHDRAWN" in lh[0][2], "LH-12 must read '
            'K4\'s off-list as R-28 states it, round 8\'s fans clause WITHDRAWN (K-03, record l4k, 7 October 2026; basis: the '
            'register\'s R-28 and R-210 to R-212 WITHDRAWN)"\n')

EDITS = [(HAND, OLD_ROW, NEW_ROW), (TEST, OLD_TEST, NEW_TEST)]

if __name__ == "__main__":
    sys.exit(run("apply_l4k_lh12 (K-03)", EDITS))
