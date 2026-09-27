#!/usr/bin/env python3
"""An island gets more than one candidate spot before it is given up (MESHSAT-862, 13 September 2026).

`pour_stitch` found the point in an island furthest from any other copper, placed a via there, and if the DRC's
hard count rose it took the via out and left the island. E8's LAST open connection was exactly that case: a
13.4 mm2 GND island in the sensor-header field whose clearest point sits between J_LTG's own through-hole pins,
where a via is a hole-clearance violation. One spot, one answer, one open board.

It keeps the clearest few now, spread at least a millimetre apart so they are not the same answer twice, and
each is judged by the same DRC the first was: the acceptance contract does not change, only the number of
shapes tried, which is `direct_close`'s pattern of 12 September.
"""
import os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "pour_stitch.py")).read()


def t_more_than_one_spot_is_collected():
    assert "SPOTS" in SRC, "there is no cap on the candidate spots, so none are collected"
    assert "spots.append" in SRC, "the island still keeps a single point"


def t_the_spots_are_spread_apart():
    i = SRC.find("spots.append")
    blk = SRC[max(0, i - 300):i + 120]
    assert "> 1.0" in blk, "nothing keeps two candidates from being the same point"


def t_a_refused_via_is_followed_by_the_next_spot():
    i = SRC.find("raised hard %d -> %d, taken out")
    blk = SRC[i:i + 400]
    assert "continue" in blk, "a refused via still ends the island"
    assert "trying the next spot" in blk, "the log does not say that another spot is coming"


def t_every_spot_is_judged_by_the_same_drc():
    i = SRC.find("for _try, (_d, _x, _y) in enumerate(spots)")
    assert i > 0, "the spots are not tried in a loop"
    blk = SRC[i:i + 900]
    assert "st = measure()" in blk and "st[0] > cur[0]" in blk, "the acceptance test changed with the loop"


def t_the_option_is_documented_and_read():
    assert "--spots=" in SRC, "the knob is not readable from the command line"
    assert "[--spots=6]" in SRC, "the usage line does not offer it"
