#!/usr/bin/env python3
"""The pre-router measures its own two legs and gives the short one the difference back (14 September 2026).

Board A's USB_D8 comes off the pair pass at P 140.32 mm and N 138.54, **the same 1.77 mm in every route**,
because the mismatch is this pass's corner geometry and not the router's: on an offset pair the outer leg is
longer than the inner by about the pitch times the turn, and a winding corridor adds those up. The owner's
length gate is 1 mm, and `meander.py` could place nothing, because a pair laid end to end here leaves no
unlocked copper and no free band beside it.

Two properties matter. The bumps go on the short leg's OWN copper, away from the partner, and every candidate
is judged by `partner_clear` before any copper exists, which is the same test the end emissions pass. And the
pair's net NAMES and its net OBJECTS are different things in this scope: the first version read `pn` as an
object and died with an AttributeError on the first pair of the first arm.
"""
import os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "pair_preroute.py")).read()


def t_the_equaliser_exists_and_is_asked_for_by_a_knob():
    assert "def _equalise" in SRC, "there is no equaliser"
    assert 'os.environ.get("PAIR_LEG_MATCH"' in SRC, "it cannot be turned off to measure it"


def t_every_bump_is_judged_before_it_is_laid():
    i = SRC.find("def _equalise")
    blk = SRC[i:i + 4200]
    assert "partner_clear(cand" in blk, "the bumps are not judged against the partner"
    assert "board_remove(b, t)" in blk and blk.find("partner_clear(cand") < blk.find("board_remove(b, t)"), \
        "copper is removed before the replacement is judged"


def t_the_bump_goes_away_from_the_partner():
    i = SRC.find("def _equalise")
    blk = SRC[i:i + 4200]
    assert "AWAY from the partner" in blk, "nothing chooses the side"


def t_the_names_are_not_the_objects():
    i = SRC.find("_lens = {pn")
    assert i > 0, "the length measurement is gone"
    blk = SRC[i:i + 700]
    assert "_lens = {pn: 0.0, nn: 0.0}" in blk, "the net names are being used as objects again"
    assert "(net_n, net_p)" in blk or "(net_p, net_n)" in blk, "the equaliser is not given the net objects"


def t_a_pair_inside_the_tolerance_is_left_alone():
    assert "LEG_MATCH_TOL" in SRC and 'os.environ.get("PAIR_LEG_MATCH_TOL", "0.5")' in SRC
