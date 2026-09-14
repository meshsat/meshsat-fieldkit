#!/usr/bin/env python3
"""A pair the pre-router laid end to end has no unlocked copper, and the length gate then refuses a board
nothing can fix (MESHSAT-862, 14 September 2026).

Board A's four ribbon legs are 8 to 20 segments each and **every one of them is locked**: the pre-router lays
the corridor, the offset legs and the stubs into the pads, and the router adds nothing. `meander.py` only ever
considered unlocked track, so on A27 it placed nothing at any amplitude and the pair gate refused the board
three rounds running for USB_D8 at 1.77 mm and USB_WALL at 1.50, on a board otherwise one connection from a
deliverable.

`MEANDER_LOCKED=1` offers the locked copper of that net WHEN THERE IS NO UNLOCKED COPPER, and `pair_match.sh`
asks for it. The safety does not change: pair_match re-runs the DRC after every round and reverts the board
whole if the hard count rises, which is the same contract `stub_accept` and `stitch_prune` work under.
"""
import os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEA = open(os.path.join(TOOLS, "meander.py")).read()
PM = open(os.path.join(TOOLS, "pair_match.sh")).read()


def t_locked_copper_is_offered_only_when_there_is_no_unlocked_copper():
    i = MEA.find('os.environ.get("MEANDER_LOCKED"')
    assert i > 0, "the knob does not exist"
    blk = MEA[max(0, i - 200):i]
    assert "if not tracks" in blk, "locked copper is offered even when unlocked copper exists"


def t_it_is_off_by_default():
    i = MEA.find('os.environ.get("MEANDER_LOCKED"')
    assert '"0"' in MEA[i:i + 60], "the default is not off"


def t_the_caller_asks_for_it_and_keeps_its_drc_guard():
    assert "MEANDER_LOCKED=1 python3 ../tools/meander.py" in PM, "pair_match does not ask for it"
    assert "hard" in PM and "revert" in PM.lower(), "the round is no longer judged by the DRC"


def t_the_offer_is_announced():
    assert "no unlocked copper" in MEA, "a board changed this way says nothing about it"
