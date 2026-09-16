#!/usr/bin/env python3
"""What each board turns into heat (rule THM-001, MESHSAT-862, 16 September 2026).

The registry carried this as a blocker with "no dissipation estimate exists for any board" while the enclosure
is sealed by ruling and holds a 30 W transmit stage. These rules hold the shape of the first half: every number
comes from the board or from a declaration with its basis, and the half that is missing says so instead of
being invented."""
import os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "thermal.py"), encoding="utf-8").read()


def t_a_rail_with_no_declared_efficiency_is_unknown_and_never_estimated():
    assert "no efficiency declared" in SRC, "a rail with no efficiency is silently given one"
    i = SRC.index("eff = r.get(\"efficiency\")")
    seg = SRC[i:i + 700]
    assert "unknown.append" in seg, "the unknown rails are not collected"
    assert "0.9" not in seg and "0.85" not in seg, "an efficiency is assumed in the code rather than declared"


def t_the_verdict_is_inconclusive_while_any_rail_is_unknown():
    assert "_v.INCONCLUSIVE if (unknown or not rows)" in SRC, \
        "a board with unknown losses could read as a pass"


def t_the_junction_temperature_is_not_invented():
    assert "ENV-001" in SRC, "the tool does not say which half is missing"
    for w in ("junction", "ambient"):
        assert w in SRC, "the tool does not name what it cannot compute (%s)" % w
    assert "GetTemperature" not in SRC


def t_the_thermal_path_is_measured_off_the_board():
    i = SRC.index("def path_of(")
    seg = SRC[i:i + 600]
    assert "GetPads" in seg or "Pads()" in seg, "the pad area is not measured"
    assert "PCB_VIA" in seg, "the vias in the courtyard are not counted"
