#!/usr/bin/env python3
"""What the resistive mesh computes and what it keeps (rule PI-002 and its neighbours, MESHSAT-862).

`dc_drop` solves a potential at every cell of every judged rail and used to report one number from it. Twice
now the thing a rule needed was already inside that solve: the barrel currents on 16 September, which took
PI-003 from an attributed reading to a measured one, and the pad potentials on the 18th, without which no
Kelvin question can be asked at all. These rules hold the shape of the tool; the boards are the fixtures and
they live where KiCad is."""
import os, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)




def t_the_solved_drop_at_every_pad_is_written_beside_the_board():
    """The mesh already computes it and used to throw it away, which is the 16 September lesson about the
    barrel currents repeated (18 September 2026).

    A rail's sense tap is only a Kelvin connection if the copper between the tap and the element it senses
    carries no drop that matters. Board A's charger reads its input current across a 10 mOhm shunt whose high
    side taps the VBUS20 POUR rather than the shunt's own pad, against a 60 mV full scale, and there was no way
    to ask how large that error is: the pass solves the potential at every node and reported one number, the
    worst drop. It writes the pad potentials now, so the question is a subtraction.

    The rule holds three things: the map is collected, it is written beside the board under its own name, and
    it carries the drop rather than an absolute potential (the source is the zero)."""
    src = open(os.path.join(TOOLS, "dc_drop.py"), encoding="utf-8").read()
    assert "_pad_v = {}" in src, "the pad potentials are not collected"
    assert "_pad_v.setdefault(net, []).append(" in src, "nothing is put in the map"
    assert "-pad-potentials.json" in src, "the map is never written beside the board"
    assert '"drop_v"' in src, "the field is not a drop, so two pads cannot be subtracted"
    i = src.find("_pad_v.setdefault(net, []).append(")
    j = src.find("drop = abs(v).max()")
    assert 0 < j < i, "the pads are read before the mesh is solved"
