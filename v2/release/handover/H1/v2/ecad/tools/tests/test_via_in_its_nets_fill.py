#!/usr/bin/env python3
"""A LOCKED VIA IS CARRIED BY ITS NET'S COPPER, NOT BY EVERY ZONE THAT CONTAINS IT (21 September 2026).

`copper_checks` asks that a locked via of a poured net sit inside that pour's FILL, because a via the fill has
retreated from carries nothing. Where two zones of ONE net share a layer, KiCad gives the copper to the
higher-priority zone and the lower one's fill has a hole exactly there, which is what priority is for. Asking
every containing zone to cover the via therefore fails a board that is right.

MEASURED: board A's gate read one FAIL on A98's, A99's and A99C's finished boards, always `/VBAT` at
(145.1, 64.4) with `VBAT plane In2 (west and middle columns)` (priority 0, 9,795 mm2) named. On the same
board `VBAT plane In2 (tongue under the converter row)` (priority 2, 115 mm2) contains that point in its
FILL, and nothing else of any net lies within 2.5 mm of it. So the via is carried, the gate was wrong, and
with this fix board A's best finished boards read ALL PASS.

The pure predicate is driven directly here, so these run where KiCad is not."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)


def _pred():
    """copper_checks imports pcbnew at module level on some hosts, so the predicate is read out by ast."""
    import ast
    src = open(os.path.join(TOOLS, "copper_checks.py"), encoding="utf-8").read()
    fn = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "covered_on_its_layer"]
    assert fn, "copper_checks no longer carries covered_on_its_layer"
    ns = {}
    exec(compile(ast.Module(body=fn, type_ignores=[]), "copper_checks.py", "exec"), ns)
    return ns["covered_on_its_layer"]


def t_a_via_the_higher_priority_zone_carries_is_not_a_failure():
    """THE DEFECTIVE FIXTURE, which is board A's own case: two zones of one net on one layer, the via inside
    both outlines and inside only the higher-priority zone's fill."""
    f = _pred()
    rows = [("VBAT plane In2 (west and middle columns)", True, False),
            ("VBAT plane In2 (tongue under the converter row)", True, True)]
    assert f(rows) is None, "a via the net's own copper reaches on that layer was reported: %s" % (f(rows),)


def t_a_via_no_fill_of_its_net_reaches_is_still_named():
    """THE ACCEPTABLE FIXTURE, and the reason the rule exists: the fill has retreated from the via and no
    other zone of that net covers it, so it carries nothing and must still be named."""
    f = _pred()
    rows = [("VBAT plane In2 (west and middle columns)", True, False),
            ("VBAT plane In2 (tongue under the converter row)", True, False)]
    assert f(rows) == ["VBAT plane In2 (west and middle columns)",
                       "VBAT plane In2 (tongue under the converter row)"], f(rows)
    assert f([("one zone", True, False)]) == ["one zone"], "the single-zone case stopped being judged"
    assert f([("one zone", False, False)]) is None, "a via outside every outline is not this rule's subject"


def t_the_gate_asks_the_question_once_per_layer():
    """The grouping is the fix: the question is asked of the net's copper ON A LAYER, so a via is judged once
    per layer it passes through and never once per zone."""
    src = open(os.path.join(TOOLS, "copper_checks.py"), encoding="utf-8").read()
    assert "for _L in sorted({z.GetFirstLayer() for z in inside}):" in src, \
        "the via check no longer groups the containing zones by layer"
    assert "covered_on_its_layer([" in src, "the gate does not take its answer from that one predicate"
