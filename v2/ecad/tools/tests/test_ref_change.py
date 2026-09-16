#!/usr/bin/env python3
"""The reference conductor before and after a transition (rule RET-003, MESHSAT-862, 16 September 2026).

RET-003 was a blocker with nothing implementing it. What it needed first was a measurement, because the answer
decides what the rule can demand: a transition that keeps its reference owes nothing, one between two ground
planes owes the ground via RET-004 already gates, and one between two DIFFERENT reference nets owes a capacitor
between them, which is the only path the return has. Measured on every board, board A is the only one with the
third case, 35 vias, because its In2 carries a GND pour and a VBAT pour side by side.

These rules hold the shape of the tool rather than the boards: the fixtures for the geometry are the boards
themselves and they live in the sweep."""
import os, json

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "ref_change.py"), encoding="utf-8").read()


def t_the_reference_is_sampled_beside_the_via_not_in_its_anti_pad():
    i = SRC.index("def net_at(")
    seg = SRC[i:i + 1400]
    assert "r=1.0" in seg and "cos(a)" in seg, \
        "the reference is sampled at the via's own centre, where the fill has retreated and every sample reads empty"


def t_the_gate_judges_only_the_case_that_is_its_own():
    assert "return_stitch" in SRC, "the rule has no verdict"
    i = SRC.index('_v.write("return_stitch"')
    seg = SRC[max(0, i - 2000):i]
    assert "power_vias" in seg, "the gate judges something other than the transitions between different nets"
    assert "RET-004" in SRC, "the tool does not say which case belongs to the other rule"


def t_a_board_that_declares_no_distance_is_inconclusive_and_never_a_pass():
    i = SRC.index('_bt.value(letter, "stitch_cap_mm")')
    seg = SRC[i:i + 1400]
    assert "if r is None" in seg and "_v.INCONCLUSIVE" in seg, "an undeclared distance would pass the board"


def t_board_a_declares_the_distance_with_its_reason():
    d = json.load(open(os.path.join(TOOLS, "boards", "a.json"), encoding="utf-8"))
    assert d.get("stitch_cap_mm") == 3.0, d.get("stitch_cap_mm")
    why = d.get("_stitch_cap_mm_why") or ""
    assert "OURS" in why and "decoupling" in why, "the declared distance does not say where it comes from"
