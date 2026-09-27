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
    # The RAIL LOOP, not a fixed number of characters after a line. The first version of this took the next
    # 700 bytes, which is a window that a comment can push the code out of: it failed on 16 September when the
    # loop gained the paragraph explaining why a hot-swap FET is not a converter, with the collection it was
    # looking for eight lines further down and perfectly correct (this file's own brittle-window lesson, the
    # same one tests/test_driver_hygiene.py learnt about one-line shell loops).
    i = SRC.index("eff = r.get(\"efficiency\")")
    seg = SRC[i:SRC.index("for d in declared", i)]
    assert "unknown.append" in seg, "the unknown rails are not collected"
    for lit in ("0.9,", "0.9)", "= 0.9", "0.85"):
        assert lit not in seg, "an efficiency is assumed in the code rather than declared: %r" % lit


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


def t_the_sum_of_every_rail_s_peak_is_not_called_a_board_power():
    """The first run printed 1,056 W for board A and 777 for board P (MESHSAT-862, 16 September 2026).

    That is what adding the peak of every rail gives you when the list includes a pack node's fault-current
    rating and three slot rails that never peak together. A number like that inside a verdict is worse than no
    number, because the next reader takes it for the board's power. The board total is the DISSIPATION, which
    is what this rule is about, and the throughput keeps its name."""
    assert "watts_peak_sum_not_simultaneous" in SRC, "the counts still call it the board's power"
    assert "NOT a board power" in SRC, "the printed line does not say what the number is not"
