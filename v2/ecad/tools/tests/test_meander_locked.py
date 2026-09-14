#!/usr/bin/env python3
"""A pair the pre-router laid end to end has no unlocked copper, and the length gate then refuses a board
nothing can fix (MESHSAT-862, 14 September 2026).

Board A's four ribbon legs are 12 to 25 segments each and **all of their length is locked**: the pre-router
lays the corridor, the offset legs and the stubs into the pads, and what the router adds is junction pieces
of 0.03 mm and under. `meander.py` only ever considered unlocked track, so on A27 it placed nothing at any
amplitude and the pair gate refused the board three rounds running for USB_D8 at 1.77 mm and USB_WALL at
1.50, on a board otherwise one connection from a deliverable.

`MEANDER_LOCKED=1` offers that net's locked copper, and `pair_match.sh` asks for it. The safety does not
change: pair_match re-runs the DRC after every round and reverts the board whole if the hard count rises,
which is the same contract `stub_accept` and `stitch_prune` work under.

CORRECTED 14 September 2026, and the correction is the reason this file exists twice over. The offer was
first gated on the net having NO unlocked copper, which is what "the pre-router lays it end to end" was
taken to mean. The board says otherwise: `/USB_D8_N` has 12 segments and FOUR OF THEM ARE UNLOCKED, at
0.03, 0.00, 0.00 and 0.00 mm, the router's own junction pieces, while the 109.45 mm run with room beside it
is locked. A gate written on a hypothesis passed on a tool that could never fire. The offer is now made
ALONGSIDE the unlocked copper, and a probe of all four of A27's legs finds two or three windows each at
every amplitude of the ladder where it found none before.
"""
import os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEA = open(os.path.join(TOOLS, "meander.py")).read()
PM = open(os.path.join(TOOLS, "pair_match.sh")).read()


def t_locked_copper_is_offered_alongside_the_unlocked_not_only_in_its_absence():
    i = MEA.find('os.environ.get("MEANDER_LOCKED"')
    assert i > 0, "the knob does not exist"
    line = MEA[MEA.rfind("\n", 0, i) + 1:i]
    assert "not tracks" not in line, (
        "the offer is gated on the net having no unlocked copper; A27's legs carry four unlocked "
        "segments of 0.03 mm and under, so this gate can never fire on the boards it was written for")
    body = MEA[i:i + 900]
    assert "tracks = every" in body, "the locked copper is never put in front of the search"


def t_the_offer_is_measured_against_the_whole_net():
    i = MEA.find('os.environ.get("MEANDER_LOCKED"')
    body = MEA[i:i + 900]
    assert "len(every) > len(tracks)" in body, (
        "the announcement and the swap must be decided by comparing the whole net with its unlocked part, "
        "not by the unlocked part being empty")


def t_it_is_off_by_default():
    i = MEA.find('os.environ.get("MEANDER_LOCKED"')
    assert '"0"' in MEA[i:i + 60], "the default is not off"


def t_the_caller_asks_for_it_and_keeps_its_drc_guard():
    assert "MEANDER_LOCKED=1 python3 ../tools/meander.py" in PM, "pair_match does not ask for it"
    assert "hard" in PM and "revert" in PM.lower(), "the round is no longer judged by the DRC"


def t_the_offer_is_announced_with_the_numbers_that_decided_it():
    assert "MEANDER_LOCKED is on, so its locked copper is offered too" in MEA, (
        "a board changed this way says nothing about it")
    i = MEA.find("MEANDER_LOCKED is on, so its locked copper is offered too")
    assert "unlocked segments of" in MEA[max(0, i - 200):i], (
        "the line does not say how much of the net was unlocked, which is the number that made this a defect")
