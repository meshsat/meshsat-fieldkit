#!/usr/bin/env python3
"""What carries load and what sees cycling (rule REL-001, 16 September 2026).

The kit is carried, so every connector mated in the field is a wear item and every board-mounted jack is a
lever with the case as its fulcrum. The rule asks for the list per board with the cycles, the load and the
measure; it read "no verification" on seven boards.

The check that makes it a gate is completeness: every part in the netlist whose value names a connector, a
socket, a holder or a jack must fall in exactly one declared class, because a list covering nine of a board's
eleven jacks reads as complete. 111 parts across six boards fall in 23 classes today.

It tests nothing, and says so: REL-001 is verified at the PROTOTYPE and no board has been built.
"""
import os, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import reliability as REL


def _tree(comps):
    d = tempfile.mkdtemp(prefix="rel-")
    prj = os.path.join(d, "pcb-x-test"); os.makedirs(os.path.join(prj, "out"))
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in sorted(comps.items()))
    open(os.path.join(prj, "out", "pcb-x-test.net"), "w").write(
        "(export (version E)\n  (components\n%s  )\n  (nets\n  )\n)\n" % c)
    return d


def _run(sheet, comps):
    d = _tree(comps)
    p = os.path.join(d, "rel.yaml"); open(p, "w").write(sheet)
    import rules_lib as R
    keep = R.board_facts
    try:
        R.board_facts = lambda *a, **k: {"x": {"project": "pcb-x-test"}}
        return REL.judge(p, d, "x")["x"]
    finally:
        R.board_facts = keep


GOOD = """
schema_version: "1.0.0"
boards:
 x:
   classes:
    - {name: "the jacks", refs: ["J_RF*"], cycles: 500, basis: "the SMA standard", load: "a wrench", measure: "the case wall takes it"}
"""


def t_a_wear_part_in_no_class_is_refused():
    """THE DEFECTIVE FIXTURE: two jacks declared, a third connector on the board and nobody has looked at it."""
    r = _run(GOOD, {"J_RF1": "SMA jack", "J_RF2": "SMA jack", "J_PWR1": "JST-VH socket"})
    assert any("J_PWR1" in f for f in r["fails"]), r["fails"]


def t_the_same_board_with_every_class_declared_passes():
    sheet = GOOD + '    - {name: "power", refs: ["J_PWR*"], cycles: 30, basis: "JST VH", load: "a lead", measure: "a tie"}\n'
    r = _run(sheet, {"J_RF1": "SMA jack", "J_PWR1": "JST-VH socket"})
    assert not r["fails"], r["fails"]


def t_a_class_with_no_cycle_figure_must_say_why():
    sheet = GOOD.replace("cycles: 500", "cycles: null")
    r = _run(sheet, {"J_RF1": "SMA jack"})
    assert any("does not say why" in f for f in r["fails"]), r["fails"]
    sheet2 = GOOD.replace("cycles: 500, basis: \"the SMA standard\"",
                          "cycles: null, basis: \"no mating-cycle figure is published for this part\"")
    r2 = _run(sheet2, {"J_RF1": "SMA jack"})
    assert not r2["fails"], r2["fails"]


def t_a_class_without_a_load_or_a_measure_is_refused():
    for k in ("load", "measure"):
        sheet = GOOD.replace('%s: "%s"' % (k, {"load": "a wrench", "measure": "the case wall takes it"}[k]), '%s: ""' % k)
        r = _run(sheet, {"J_RF1": "SMA jack"})
        assert any(("carries no %s" % k) in f for f in r["fails"]), (k, r["fails"])


def t_a_declared_count_that_does_not_match_the_board_is_refused():
    sheet = GOOD.replace('refs: ["J_RF*"]', 'refs: ["J_RF*"], count_expected: 3')
    r = _run(sheet, {"J_RF1": "SMA jack", "J_RF2": "SMA jack"})
    assert any("expects 3" in f for f in r["fails"]), r["fails"]


def t_the_committed_list_covers_every_wear_part_of_every_board():
    r = REL.judge()
    fails = [f for v in r.values() for f in v["fails"]]
    assert not fails, fails
    assert sum(v["covered"] for v in r.values()) >= 100, r
