#!/usr/bin/env python3
"""A via site is judged against a pad's COPPER, never against a circle of its size (MESHSAT-862, 20 Sep 2026).

Board D's chain ended `PREROUTE-DONE BLOCK 1` for days on one `clearance` violation: `Pad 2 [/+5V_D8] of D1`
against a locked `Via [GND]` at (70.925, 67.604999), 0.1115 mm where the PWR class asks 0.1270. Two
attributions were wrong before a per-stage DRC named the stage, and both were wrong for the same reason, a
count over a window with TWO writers in it: board D declares `fanout_nets = "GND"`, so `prefanout` lays a via
per ground pad and `gnd_grid` lays its lattice, and the 1,378 vias between the placed board and the pre-lay
snapshot are the sum of the two.

Run one at a time with a DRC after each, the stage names itself: placed hard 2 (two same-part mask items),
prefanout hard 3 with the clearance, gnd_grid hard 4 and the clearance UNCHANGED, so the grid neither laid it
nor should have removed it (`_own_hard` only offers the vias gnd_grid itself placed, which is correct).

THE CAUSE: both in-pad fallbacks measured CENTRE TO CENTRE against `qr + VIA_D / 2 + INPAD_CLR` with `qr =
max(size.x, size.y) / 2` used as a CIRCLE radius. A circle of the long half-dimension does not contain a
rectangle's corners, so a via approaching a land ALONG ITS DIAGONAL passes while its copper does not, and it
is too STRICT along the short axis for the same reason. D1 is a 2.500 x 2.300 SMB land and the via sits in
C9 pad 2, 1.9313 mm away on the diagonal against a demand of 1.6750: accepted, and the real gap from the
ring to that copper is 0.1137 mm. The same file's `_crosses` has judged against the polygon since this
morning, for this reason, on the other half of the tool.

MEASURED, one variable, the same placed board: fanout **90 vias (5 in the pad) and 15 pads skipped becomes
93 (8 in the pad) and 12 skipped**, and the hard set **3 {solder_mask_bridge 2, clearance 1} becomes 2
{solder_mask_bridge 2}**. It gains three plane vias because the circle was wrong in BOTH directions, and C9
pad 2 declines itself with `no room for a fanout via`.

The fifth instance this week of one shape: a guard whose question is cheaper than the fact it guards."""
import os, re, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)


def _src():
    return open(os.path.join(TOOLS, "prefanout.py"), encoding="utf-8").read()


def t_no_via_site_is_judged_by_a_circle_of_the_pads_own_size():
    """THE DEFECT ITSELF. Fails on the tree this rule was written against, where the second in-pad fallback
    read `all(math.hypot(c.x - qp.x, c.y - qp.y) >= qr + VIA_D / 2 + INPAD_CLR ...)`."""
    s = _src()
    for m in re.finditer(r"hypot\([^)]*\)\s*>=\s*qr\s*\+", s):
        raise AssertionError("a via site is still judged against a circle of the pad's own size: %s"
                             % s[max(0, m.start() - 60):m.end() + 40].replace("\n", " "))
    assert "_other_net_clear" in s, "prefanout has no polygon-based clearance test for a via site"


def t_the_polygon_test_is_asked_by_both_in_pad_fallbacks():
    """There are TWO of them and only one had any other-net test at all. The `skip_fp` branch, which gives a
    fine part's exposed pad its plane via, asked ONLY whether a via was already within `VIA_D + 0.35`: no
    pads, no tracks, no rule areas, no board edge. It never caused board D's item (C9 is an 0805 and
    `is_fine` is false for it) and it is the same hole one branch along."""
    s = _src()
    assert s.count("_other_net_clear(c, pad.GetNetname()") == 2, \
        "the polygon test is asked by %d in-pad fallback(s), not 2" % s.count("_other_net_clear(c, pad.GetNetname()")
    head = s.split("if skip_fp:")[1][:900]
    assert "_other_net_clear" in head, "the fine-part exposed-pad branch still lays a via with no other-net test"
    assert "_seg_dist(c, a_, e_)" in head, "the fine-part exposed-pad branch still ignores laid tracks"


def t_the_cheap_circle_survives_only_as_a_pre_filter():
    """A polygon call per pad per candidate is a SWIG call per pad per candidate, which is why the tool
    carried a circle in the first place. The reach the tuple already carries bounds how far a pad's copper
    can be from its centre, so the polygon is asked only of pads that could possibly be close, and the
    pre-filter can only ever ADMIT a pad to the real test."""
    s = _src()
    fn = s.split("def _other_net_clear(")[1].split("\ndef ")[0]
    assert "qreach + need" in fn, "the polygon test has no cheap pre-filter and runs a SWIG call per pad"
    assert "continue" in fn and "Collide(c, int(need))" in fn, \
        "the pre-filter does not fall through to the polygon, so it is deciding on its own"


def t_the_measurement_is_recorded_where_the_next_reader_looks():
    """A tool change without its number is a claim. Board D's file carries the before and after."""
    d = open(os.path.join(TOOLS, "boards", "d.json"), encoding="utf-8").read()
    assert "90 vias" in d and "93" in d, "board D's file does not carry the fanout count before and after"
    assert "0.1137" in d or "0.1115" in d, "board D's file does not carry the gap that was accepted"
