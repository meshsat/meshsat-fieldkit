#!/usr/bin/env python3
"""The reservation never gives a capacitor a second footprint (20 September 2026).

`bypass_slots.reserve` walks the declared capacitors and calls the generator's own `place()` for each, and
`place()` CREATES a footprint. A capacitor the generator has already seated from its FIXED table is then on
the board twice under one reference: the net assignment walks the generator's `placed` map and reaches only
the first, so the duplicate's pads are saved with no net at all.

WHY IT WAS INVISIBLE. At HEAD every such capacitor fails the 3 mm search, because the pin of a fine-pitch
part sits on the edge of the escape fan this pass refuses, and the failure path REMOVES the footprint it
created, which takes the duplicate with it. An arm that let the search reach 6 mm turned that into eleven
duplicate references on board A (C4, C11, C63, C64, C106, C107 and the five ISNS filter capacitors) and
`netlist_board` blocked the chain at 2,134 of 2,148 comparisons.

The rule below is the mechanical half: `reserve` asks the board for the capacitor before it makes one. The
fixture half lives in test_bypass_place.py, where the pass is given real boards.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import block

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def t_the_reservation_asks_the_board_before_it_places_a_capacitor():
    src = open(os.path.join(TOOLS, "bypass_slots.py"), errors="replace").read()
    body = block(src, "def reserve(")
    assert body, "reserve() is not where this rule looks for it"
    i_find = body.find("FindFootprintByReference(cap)")
    i_place = body.find("place(cap,")
    assert i_find > 0, "reserve() never asks the board whether the capacitor is already on it"
    assert i_place > 0, "reserve() no longer calls place(), so this rule needs rewriting"
    assert i_find < i_place, ("reserve() calls place(cap, ...) before asking the board for it, which gives a "
                              "seated capacitor a second footprint under the same reference")


def t_a_seated_capacitor_is_left_where_the_generator_put_it():
    src = open(os.path.join(TOOLS, "bypass_slots.py"), errors="replace").read()
    body = block(src, "def reserve(")
    seg = body[body.find("FindFootprintByReference(cap)"):]
    seg = seg[:seg.find("place(cap,")] if "place(cap," in seg else seg
    assert "continue" in seg, ("a capacitor already on the board must be reported and left alone, not moved: "
                               "its seat is a decision with its own measurement")
    assert "SetPosition" not in seg, "the pass moves a capacitor the generator seated deliberately"

def t_the_reservation_writes_down_the_capacitors_the_generator_had_already_seated():
    """The pass that runs later cannot tell a seat from an accident unless this one says so.

    `bypass_place` moves any declared capacitor further than 3 mm from its pin to the first free spot it can
    find, and a seat chosen outside every region rectangle, escape fan and piece of laid copper is typically
    3 to 8 mm out. Board D's seat arms came back hard 33, then 30, then 30, and moving a measured seat with a
    weaker test is one of the things that can do that. The list is written beside the board so the later pass
    can leave those alone."""
    src = open(os.path.join(TOOLS, "bypass_slots.py"), errors="replace").read()
    body = block(src, "def reserve(")
    assert "-seated.json" in body, "reserve() does not write the seated list beside the board"
    assert "already" in body, "the seated list is not built from the capacitors it found already placed"


def t_the_later_pass_leaves_a_seated_capacitor_alone():
    src = open(os.path.join(TOOLS, "bypass_place.py"), errors="replace").read()
    body = block(src, "def main(")
    assert "-seated.json" in body, "bypass_place never reads the seated list"
    i = body.find("-seated.json")
    seg = body[i:]
    assert "not in seated" in seg or "seated" in seg.split("entries")[0], \
        "bypass_place reads the list and does not filter its entries by it"
