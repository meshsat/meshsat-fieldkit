#!/usr/bin/env python3
"""A single-ended controlled line is the width its own stackup makes 50 ohm (rule RF-001, MESHSAT-862,
16 September 2026).

Every board declares an RF class with a 50 ohm single-ended target and impedance_check judges PAIRS: the
string `z_se` does not appear in it. The target was declared on every board and read by nothing, which is what
the rule's own coverage note said in words. These are the arithmetic's checks; the board fixtures need KiCad
and live in the sweep."""
import os, sys, math

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import impedance_check as I
SRC = open(os.path.join(TOOLS, "rf_line.py"), encoding="utf-8").read()


def t_fifty_ohm_microstrip_is_about_two_heights_wide():
    """The calibration point every transmission-line table starts from: on FR-4 a 50 ohm microstrip is about
    twice as wide as its height above the reference. A tool that disagreed would have a unit error."""
    h, t, er = 0.2104, 0.035, 4.4
    w50 = next(w for w in [x / 1000 for x in range(100, 900)] if I.z_microstrip(w, h, t, er) <= 50)
    assert 1.6 <= w50 / h <= 2.2, w50 / h


def t_the_same_width_inside_the_stack_is_half_the_impedance():
    """Board A's finding, as arithmetic. Its RF class is 0.35 mm, which is about 50 ohm as a microstrip on the
    outer layer it was drawn for, and about 25 on In2 between two planes. The width is right and the layer is
    not, which is the shape of defect this rule exists to catch."""
    micro = I.z_microstrip(0.35, 0.2104, 0.035, 4.4)
    strip = I.z_stripline(0.35, 0.167, 0.035, 4.4)
    assert 45 <= micro <= 60, micro
    assert strip < micro / 1.7, (strip, micro)


def t_a_pair_is_not_judged_as_two_single_ended_lines():
    assert "paired = {n for n in names" in SRC, "a pair's legs are judged single-ended"
    assert 'classes.get(cl) or {}).get("z_diff")' in SRC, "a class with a differential target is judged here too"


def t_the_differential_calibration_is_not_borrowed():
    """impedance_check's solver points and its 0.967 correction were measured on differential geometries.
    Applying either to a single-ended line would be an assumption wearing a measurement's clothes."""
    assert "z = closed" in SRC, "the closed form is not used on its own"
    assert "calibrated(" not in SRC.split("def main")[1].split("z = closed")[0][-400:], \
        "the pair calibration is still applied to a single-ended line"


def t_a_board_with_no_rf_and_facts_that_say_so_passes():
    assert 'f.get("rf_transmit") is False' in SRC, "a board with no RF cannot answer with a declared zero"
    assert '"judged": 0' in SRC, "the declared zero carries no count"


def t_the_remedy_is_declared_on_the_board_and_not_hidden_in_a_tool():
    """The fix for board A's eleven lines is the LAYER, not the width: 0.35 mm is about 50 ohm outside and 25
    inside. They are pre-laid on an outer layer before the router runs, and the declaration carries the
    measurement that forced it."""
    import json, os
    a = json.load(open(os.path.join(TOOLS, "boards", "a.json"), encoding="utf-8"))
    g = a.get("prelay_groups") or []
    assert g, "board A declares no pre-lay group for its RF paths"
    rf = [x for x in g if "RF_" in x.get("nets", "")]
    assert rf, "the RF paths are not in a pre-lay group"
    assert rf[0]["layers"] == "F.Cu,B.Cu", "the RF group is not restricted to the outer layers"
    assert "25.5 ohm" in rf[0].get("why", ""), "the declaration does not carry the measurement"
    full = open(os.path.join(TOOLS, "full.sh"), encoding="utf-8").read()
    assert "prelay_groups" in full, "no chain reads the pre-lay groups"
    # ASK FOR THE TWO LINES AND THEIR ORDER, never for a slice. This rule read 1,500 characters after the
    # anchor and broke on 19 September when a paragraph about a group's own clearance was written between
    # them, which is the same failure `test_prelay` had on 18 September and the reason `harness.block` exists.
    i = full.index("get('prelay_groups')")
    j = full.index('STUB_LAYERS="$GLAYERS"')
    assert i < j, "the group's own layers do not reach the search"
    assert full.index('read -r GNETS GLAYERS', i) < j, "the loop does not read the layers before using them"
