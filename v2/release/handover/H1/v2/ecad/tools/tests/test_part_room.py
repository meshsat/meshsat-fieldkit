#!/usr/bin/env python3
"""Where a part's own support sits (a report, 21 September 2026).

A pad-to-pad open is read here as a placement question, and twice in one afternoon the question turned out to
be about the PARTNER rather than the part: board E's four remaining opens are U5's support parts 11.29 to
22.10 mm from the pins they serve, with U5 itself holding 11.40 mm clear to the west and the board's edge to
the south, and every one of board A's five LM5176 stages drives its FETs from 13.5 to 28.9 mm away.

The rule that matters is the one the first version got wrong: a part DIAGONALLY opposite blocks nothing, and
counting it reports a crowded part where the lane is open."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, HERE)


def _room():
    """`room_around` from the tool's own source, without importing the module, which needs pcbnew."""
    import ast
    src = open(os.path.join(TOOLS, "part_room.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "room_around"]
    assert fn, "part_room no longer carries room_around, which is the measurement itself"
    ns = {}
    exec(compile(ast.Module(body=fn, type_ignores=[]), "part_room.py", "exec"), ns)
    return ns["room_around"]


def t_a_part_in_the_same_band_is_what_blocks_the_lane():
    room_around = _room()
    mine = ("U5", 10.0, 10.0, 16.0, 18.0)
    r, w = room_around(mine, [("L1", 17.87, 12.0, 20.0, 15.0)])     # east, sharing the horizontal band
    assert abs(r["east"] - 1.87) < 1e-9, r
    assert w["east"] == "L1", w
    assert r["west"] > 1e8 and r["north"] > 1e8 and r["south"] > 1e8, r


def t_a_part_diagonally_opposite_blocks_nothing():
    """THE DEFECTIVE FIXTURE. A box that shares NO band with the part is not in any of its four lanes, and a
    tool that counted it would report a crowded part where the lane is open, which is the opposite of the
    reading this report exists to give."""
    room_around = _room()
    mine = ("U5", 10.0, 10.0, 16.0, 18.0)
    r, _ = room_around(mine, [("X1", 30.0, 30.0, 32.0, 32.0)])
    assert all(v > 1e8 for v in r.values()), "a diagonal neighbour was counted as blocking a lane: %s" % r


def t_the_nearest_in_each_direction_wins_and_it_is_named():
    room_around = _room()
    mine = ("U5", 10.0, 10.0, 16.0, 18.0)
    others = [("A", 0.0, 12.0, 5.0, 15.0), ("B", 0.0, 12.0, 8.0, 15.0)]   # both west, B nearer
    r, w = room_around(mine, others)
    assert abs(r["west"] - 2.0) < 1e-9 and w["west"] == "B", (r, w)


def t_it_measures_courtyards_and_says_it_is_not_a_seat_search():
    """A seat that is clear of courtyards can still be refused by the escape-fan predictor, which cost board A
    thirteen escapes on 20 September. The report must not read as one."""
    src = open(os.path.join(TOOLS, "part_room.py"), encoding="utf-8").read()
    assert "not a seat search" in src.lower(), "the report does not say what it is not"
    assert "place_audit" in src, "the report does not name the tool that answers the fan"
