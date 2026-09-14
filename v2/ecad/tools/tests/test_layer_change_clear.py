#!/usr/bin/env python3
"""The pair's layer change is judged before it is laid, at the right bar (MESHSAT-862, 14 September 2026).

With the END emissions asked about the partner before they exist (`PAIR_END_FIT`, 32.173), B19 lays 71 of 113
and **every own-legs refusal that remains names one emission**: 14 of them are `layer change` against `layer
change` and the rest a corridor leg run against one. The two VIA SITES are separated by a via plus the
clearance, which `pair_free` has always checked; the four SEGMENTS that reach them are not.

They are built and judged against each other inside `pair_free`, so a spot whose copper cannot work is never
taken and the search walks on to the next one: a refusal before the copper exists costs a candidate, a refusal
after it exists costs the pair.

THE BAR IS THE POINT, and the first version had it wrong in the way this file now exists to prevent. Written
with the CLASS clearance between the pair's own two tracks, one arm took B19 from 71 of 113 to **58**, against
the 22 of 48 to 9 that appendix 32.135 records for the identical error in the fold test forty lines above. The
two legs arrive at a layer change AT THE PAIR PITCH, which on the inner-layer DIFF100 geometry is 0.257 mm
against a class demand of 0.257, so a rasterised candidate wobbles across the bar and the spot is refused.
Track against track is a FOLD detector, half the pair's own pitch. A VIA of one leg against a track of the
other keeps the class number: a 0.4 to 0.7 mm via beside the partner's track is not a marginal geometry, and
the post-lay gate judges it at the class clearance with no pair exemption anywhere.
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


def t_track_against_track_is_a_fold_detector_and_not_a_clearance_test():
    """32.135's finding, made twice in this file: at the class clearance this cost B19 thirteen pairs
    (71 of 113 to 58), the same thirteen the fold test above records (22 of 48 to 9)."""
    blk = _pair_free()
    i = blk.find("for a_ in P_[:2]:")
    assert i > 0, "the track-against-track loop is gone"
    seg_loop = blk[i:blk.find("for a_, other in", i)]
    assert "min(clr_c + wid(" in seg_loop and "2.0 * abs(dof(" in seg_loop, (
        "the pair's own two tracks are judged at the class clearance; they arrive at a layer change at the "
        "pair pitch, which IS that number, so every rasterised candidate reads as a violation")
    assert "clr_c - 0.005" not in seg_loop, "the gate's clearance bar is still the demand between the two tracks"


def t_a_via_keeps_the_class_number():
    blk = _pair_free()
    i = blk.find("for a_, other in")
    assert i > 0, "the via loop is gone"
    via_loop = blk[i:]
    assert "_bar" in via_loop, (
        "a via of one leg against the other leg's track is not a marginal geometry and must keep the class "
        "clearance the post-lay gate judges it at")


def t_a_via_is_judged_against_the_other_legs_copper():
    assert "_pt_seg(" in _pair_free(), "a via of one leg is never checked against the other leg's pieces"


def t_it_has_a_knob_of_its_own_and_it_is_off():
    """MEASURED 14 September 2026, one variable, same placed board, the declared B19 baseline: no test lays
    71 of 113 (38 DIFF100 + 33 USB), the class clearance 58 (36 + 22), the fold detector 57 (33 + 24).

    The test is correct copper and it costs pairs at either bar, which is 32.95's law restated: on a greedy
    pass with no rip-up a bar that refuses a spot moves the failure rather than the pair. It is off, and it is
    its OWN knob rather than PAIR_END_FIT's, because END_FIT is worth +16 on the same board and the two must
    be separable."""
    blk = _pair_free()
    assert "if not LAYER_FIT: return True" in blk, "the check cannot be turned off on its own to measure it"
    assert 'LAYER_FIT = os.environ.get("PAIR_LAYER_CHANGE_FIT", "0")' in SRC, "the knob is missing or is on by default"
    assert "if not END_FIT: return True" not in blk, "it still rides on the end fit's knob, so neither can be measured"
