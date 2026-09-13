#!/usr/bin/env python3
"""A tool that judges copper against the FILL must refuse an unfilled board (MESHSAT-862, 13 September 2026).

`stitch_prune.py` removes a locked via "the pour has abandoned", which it reads as: the zone's outline contains
the via and the zone's FILL does not. On a board whose zones carry no fill that is true of every via of every
pour: a dry run on A26's board after the gate, which leaves it unfilled, offered to remove **366 of its 660
locked vias**. Nothing was lost, because the finish refills before it calls this, but a tool whose safety
depends on its caller's ordering is one edit away from the four dead paths of 32.153.

`copper_checks.run` already refuses the same input with "refill before the gate", so this is that rule where
the other reader of the fill lives.
"""
import os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "stitch_prune.py")).read()


def t_stitch_prune_refuses_a_board_with_no_fill():
    assert "GetFilledArea() > 0" in SRC, "stitch_prune never asks whether anything is filled"
    i = SRC.find("GetFilledArea() > 0")
    blk = SRC[i - 200:i + 600]
    assert "INCONCLUSIVE" in blk, "an unfilled board is not a PASS and not a FAIL: it is inconclusive"
    assert "nothing removed" in blk or "no via could be judged" in blk, "the refusal does not say that nothing was removed"


def t_the_refusal_comes_before_any_via_is_judged():
    i = SRC.find("GetFilledArea() > 0")
    j = SRC.find("for v in vias:")
    assert 0 < i < j, "the fill check must come before the loop that removes vias"


def t_copper_checks_refuses_the_same_input():
    src = open(os.path.join(TOOLS, "copper_checks.py")).read()
    assert "refill before the gate" in src, "the other reader of the fill lost its guard"
