#!/usr/bin/env python3
"""The pair's layer change is judged before it is laid (MESHSAT-862, 14 September 2026).

With the END emissions asked about the partner before they exist (`PAIR_END_FIT`, 32.173), B19 lays 71 of 113
and **every own-legs refusal that remains names one emission**: 14 of them are `layer change` against `layer
change` and the rest a corridor leg run against one. The two VIA SITES are separated by a via plus the
clearance, which `pair_free` has always checked; the four SEGMENTS that reach them are not.

They are built and judged against each other at the post-lay gate's own bar inside `pair_free`, so a spot whose
copper cannot work is never taken and the search walks on to the next one, which is the whole point: a refusal
before the copper exists costs a candidate, a refusal after it exists costs the pair.
"""
import os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "pair_preroute.py")).read()


def _pair_free():
    i = SRC.find("def pair_free(")
    j = SRC.find("\n                    spot = None", i)
    assert i > 0 and j > i, "pair_free is gone or no longer followed by the spot search"
    return SRC[i:j]


def t_the_via_sites_are_still_separated():
    assert "vd + clr_c + 0.02" in _pair_free(), "the two via sites are no longer held apart"


def t_the_segments_are_judged_against_each_other():
    blk = _pair_free()
    assert "_seg_dist(" in blk, "the legs' layer-change segments are not compared"
    assert "clr_c - 0.005" in blk, "the bar is not the post-lay gate's"


def t_a_via_is_judged_against_the_other_legs_copper():
    assert "_pt_seg(" in _pair_free(), "a via of one leg is never checked against the other leg's pieces"


def t_it_is_the_same_knob_as_the_end_fit():
    blk = _pair_free()
    assert "if not END_FIT: return True" in blk, "the check cannot be turned off to measure it"
