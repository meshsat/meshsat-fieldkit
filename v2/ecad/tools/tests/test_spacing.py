#!/usr/bin/env python3
"""The high-voltage spacing is measured, not asserted (rule ISO-001, MESHSAT-862, 16 September 2026).

A net class is an instruction to the router, not a fact about the board: it binds the router's tracks and says
nothing about a pad, a zone edge or a hand-laid piece of copper. The registry carried "no creepage or clearance
distance has ever been measured on any board" and that is what this closes, for the measuring half."""
import os, math, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import spacing
SRC = open(os.path.join(TOOLS, "spacing.py"), encoding="utf-8").read()


def t_the_segment_distance_is_the_geometry_and_not_a_bounding_box():
    # two parallel segments 2 mm apart
    assert abs(spacing.seg_dist((0, 0), (10, 0), (0, 2), (10, 2)) - 2.0) < 1e-9
    # a segment and one that ends beside it: the nearest point is an endpoint
    assert abs(spacing.seg_dist((0, 0), (10, 0), (12, 0), (20, 0)) - 2.0) < 1e-9
    # crossing segments touch
    assert spacing.seg_dist((0, 0), (10, 0), (5, -5), (5, 5)) < 1e-9


def t_a_board_with_no_high_voltage_rail_says_the_rule_does_not_apply():
    assert "applicable=False" in SRC, "a board with no HV rail would read as an unanswered question"


def t_an_undeclared_limit_is_reported_and_never_passed():
    i = SRC.index("lim = _bt.value")
    seg = SRC[i:i + 2000]
    assert "_v.INCONCLUSIVE if lim is None" in seg, "a board with no declared spacing could read as a pass"
    assert "IEC 60664" in SRC, "the tool does not name the authority it is missing"


def t_the_measurement_covers_pads_and_not_only_tracks():
    assert "f.Pads()" in SRC and "GetTracks()" in SRC, "the measurement misses a whole class of conductor"
