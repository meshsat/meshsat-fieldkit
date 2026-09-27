#!/usr/bin/env python3
"""One current-rating model, in one place (decision 35, ruled 21 September 2026).

The model a conductor is judged against was typed into THREE files: `dc_drop.ipc_limit`, `power_copper.width_for`
and `via_current.ampacity` each carried IPC-2221A's constants, which is one decision with three answers in one
tree and is the shape the DRC policy had before the hard set was centralised.

The rules here hold what the ruling says: the bar is the lowest any published Annex D fit allows at that area,
it is asked from one function, it never reads higher than IPC-2221A alone, and the sizer and the judge agree.
"""
import os
import re
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)


def t_the_bar_is_the_lowest_published_model_at_every_area():
    """The defective case is the old behaviour: above the crossover IPC-2221A reads HIGHER than IPC-2152, and
    a bar that reads higher than a published model is the thing decision 35 ruled out."""
    import track_current as tc
    xo = tc.crossover(10.0)
    assert 0.2 < xo < 0.35, xo
    for a in (0.01, 0.05, 0.1, xo * 0.9, xo * 1.5, 1.0, 4.0):
        v, model = tc.conservative(a, 10.0)
        assert all(v <= tc.rating(a, 10.0, m) + 1e-12 for m in tc.MODELS), (a, v, model)
    # above the crossover it must be STRICTLY below the old single fit, or the ruling changed nothing at all
    assert tc.conservative(1.0, 10.0)[0] < tc.rating(1.0, 10.0, "IPC-2221A") * 0.9


def t_below_the_crossover_nothing_moves():
    """The acceptable case, and it is why the ruling moved no reading: every conductor and every pour cell
    this project measures is below the crossover, where IPC-2221A is already the lowest fit."""
    import track_current as tc
    assert abs(tc.crossover_min(10.0) - 0.1706) < 0.001, tc.crossover_min(10.0)
    for a in (0.0141, 0.0226, 0.0293, 0.1, 0.15):
        v, model = tc.conservative(a, 10.0)
        assert model == "IPC-2221A", (a, model)
        assert abs(v - tc.rating(a, 10.0, "IPC-2221A")) < 1e-12


def t_no_tool_carries_the_constants_itself():
    """One place decides, and the rule reads the CODE and not the words.

    Its first version was a regex over the lines, and it fired on this commit's OWN docstring in `dc_drop`,
    which quotes the formula it replaced so that a reader knows what changed. A docstring is not a statement:
    the file is PARSED and only real numeric constants in real expressions count, which is the same correction
    this project made to the `col(out, xL + 1.0` rule on 21 September and to the `import os as _x` rule before
    it."""
    import ast
    bad = []
    for fn in sorted(os.listdir(TOOLS)):
        if not fn.endswith(".py") or fn == "track_current.py":
            continue
        path = os.path.join(TOOLS, fn)
        try:
            tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, float) and node.value in (0.725, 0.7252):
                bad.append("%s:%d carries the IPC exponent %s" % (fn, getattr(node, "lineno", 0), node.value))
    assert not bad, "the current-rating model is typed outside track_current.py: %s" % bad


def t_the_sizer_and_the_judge_agree():
    """A band laid to `width_for` must pass `ipc_limit` on the copper it lays, or the generator lays what the
    gate refuses. They were separate implementations of one formula until today."""
    import track_current as tc
    for amps in (1.0, 3.0, 6.0, 10.0, 18.0):
        for oz, internal in ((1.0, False), (0.5, True), (2.0, False)):
            w = tc.width_for_current(amps, oz=oz, dT=10.0, internal=internal)
            area = w * 0.035 * oz
            allowed, _m = tc.conservative(area, 10.0)
            if not internal:
                allowed *= tc.EXTERNAL_FACTOR
            assert allowed >= amps - 1e-6, (amps, oz, internal, w, allowed)
