#!/usr/bin/env python3
"""The post-route barrel fixer stops when a round buys nothing (20 September 2026).

`via_parallel` lays parallel barrels beside a via the solved mesh puts over its rating, in rounds, because a
chain of barrels moves the worst one along. It has stopped a round that made the set WORSE since 18
September; a round that changed NOTHING stood, and on board E's E30 that is three rounds of exactly nothing:

    round 1: 36 over, kept 33 vias at 16 barrels, worst barrel 10.84 -> 8.89
    round 2: 58 over, kept 18 vias at 17 barrels, worst barrel  8.89 -> 8.89
    round 3: 57 over, kept  8 vias at 11 barrels, worst barrel  8.89 -> 8.89
    round 4: 54 over, kept  2 vias at  5 barrels, worst barrel  8.89 -> 8.89

Twenty-eight drilled holes that buy no ratio, with a third of what each round tried refused by the DRC and
taken back off with its links. The count of over-rated barrels GROWS as the pass works, because every via it
lays is itself a barrel the next round judges, which is why round 2 saw 58 where round 1 saw 36: the count is
not the measure and the WORST RATIO is.
"""
import os, re, subprocess, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(TOOLS, "via_parallel.py")


def _round_block(src):
    """The text of the round loop's outcome, from where the round's worst ratio is measured."""
    i = src.find("worst_after = _worst(")
    assert i >= 0, "via_parallel no longer measures the round's worst ratio"
    j = src.find("worst_before = worst_after", i)
    assert j > i, "via_parallel no longer carries the worst ratio into the next round"
    return src[i:j]


def t_a_round_that_does_not_improve_the_worst_ratio_ends_the_pass():
    """THE PROPERTY. Not 'does not make it worse': a round that leaves the worst ratio where it found it has
    bought nothing, and its vias are holes in a board."""
    blk = _round_block(open(SRC, encoding="utf-8").read())
    assert "worst_before[0] - 1e-6" in blk, (
        "via_parallel keeps a round that leaves the worst ratio unchanged; the test is an IMPROVEMENT, not "
        "the absence of harm")
    assert blk.count("break") >= 2, "the round loop does not end on both the no-gain and the worse case"


def t_a_round_that_buys_nothing_takes_its_vias_back_off():
    """And it is put BACK, not merely stopped after: the vias of a round that bought nothing are drilled
    holes with no ratio behind them, and the pass already keeps a copy for exactly this."""
    blk = _round_block(open(SRC, encoding="utf-8").read())
    head = blk[:blk.find("worst_before[0] + 1e-6")] if "worst_before[0] + 1e-6" in blk else blk
    assert "shutil.copy(round_bak, path)" in head, (
        "the no-gain branch does not restore the round's own backup before it stops")


# A PROOF AGAINST HISTORY IS NOT A RULE AND IT EXPIRES AT THE NEXT COMMIT (20 September 2026, within the
# hour it was written). This file carried a third test asserting that the two properties above are FALSE of
# `git show HEAD:...via_parallel.py`, which is how the change was proved before it landed. The moment the
# change was committed, HEAD became the new file and the test failed on its own success. The proof belongs in
# the commit that makes the change and in the appendix entry beside it, which is where this project's
# convention already puts it; what stays here is the PROPERTY, which is true of the tool for as long as the
# tool is right. The measurement that motivates it is in the docstring above and does not need git to check.
