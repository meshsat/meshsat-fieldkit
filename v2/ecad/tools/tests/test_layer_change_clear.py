#!/usr/bin/env python3
"""The layer-change fit (14 September 2026) was measured to cost 14 pairs on B19 and switched off behind
`PAIR_LAYER_CHANGE_FIT`; on 15 September 2026 (red team round four C3: a knob that lost is deleted with its section cited)
the branch and the knob were deleted, appendix 32.185. This file holds that they stay gone and that the via sites of a
layer change are still separated by the via plus the class clearance, which is the half of the check that was never in
question."""
import os
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "pair_preroute.py"), errors="replace").read()


def t_the_via_sites_are_still_separated():
    assert "if abs(2 * split_) < vd + clr_c + 0.02: return False" in SRC, "the two via sites of a layer change are no longer held apart by the via plus the clearance"


def t_the_measured_loser_is_gone_and_the_record_says_where():
    assert "PAIR_LAYER_CHANGE_FIT" not in SRC and "LAYER_FIT" not in SRC, "the deleted knob is back"
    assert "32.185" in SRC, "the deletion does not cite the measurement"
    doc = os.path.join(TOOLS, "..", "..", "docs", "PAIR-PREROUTER-KNOBS.md")
    if os.path.exists(doc): assert "PAIR_LAYER_CHANGE_FIT" in open(doc, errors="replace").read(), "the knob map does not record the removal"
