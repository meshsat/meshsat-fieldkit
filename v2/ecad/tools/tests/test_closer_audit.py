#!/usr/bin/env python3
"""Prevention before repair (rule PLC-002, 16 September 2026).

Every repair in the finish is a defect the placement or the route did not prevent. The rule asks each closer to
name its defect class and why prevention was not possible, and asks the predictor to cover the classes repaired
more than once.

The check that makes it a gate is completeness: the list of copper-changing stages comes from finish.sh itself,
so a stage added to the finish and not declared is a failure rather than a silence. And the coverage question
is answered PER BOARD, because the prevention for three of these classes is a ground-via grid laid before the
route, and a grid is declared board by board: it is not free, and board P measured it at 21 open connections
against 0 without.
"""
import os, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import closer_audit as C

GOOD = """
schema_version: "1.0.0"
closers:
 - {tool: alpha.py, changes_copper: true, defect_class: "a thing", why_prevention_failed: "because", repeated: false}
"""


def _fin(d, body):
    p = os.path.join(d, "finish.sh"); open(p, "w").write(body); return p


def _cl(d, body):
    p = os.path.join(d, "closers.yaml"); open(p, "w").write(body); return p


def t_a_stage_in_the_finish_that_is_not_declared_is_refused():
    d = tempfile.mkdtemp(prefix="cl-")
    r = C.judge(_cl(d, GOOD), _fin(d, "python3 $T/alpha.py x\npython3 $T/beta.py y\n"))
    assert any("beta.py" in f for f in r["fails"]), r["fails"]


def t_the_same_finish_with_both_declared_passes():
    d = tempfile.mkdtemp(prefix="cl2-")
    body = GOOD + ' - {tool: beta.py, changes_copper: true, defect_class: "another", why_prevention_failed: "reason", repeated: false}\n'
    r = C.judge(_cl(d, body), _fin(d, "python3 $T/alpha.py x\npython3 $T/beta.py y\n"))
    assert not r["fails"] and not r["uncovered"], r


def t_a_reader_stage_is_not_asked_to_declare_a_repair():
    """hardset and the DRC read the board; they are not repairs and must not be demanded of."""
    d = tempfile.mkdtemp(prefix="cl3-")
    r = C.judge(_cl(d, GOOD), _fin(d, "python3 $T/alpha.py x\npython3 $T/hardset.py y\n$T/drc.sh z\n"))
    assert not r["fails"], r["fails"]


def t_a_repeated_class_with_no_prevention_is_uncovered():
    d = tempfile.mkdtemp(prefix="cl4-")
    body = GOOD.replace("repeated: false", "repeated: true")
    r = C.judge(_cl(d, body), _fin(d, "python3 $T/alpha.py x\n"))
    assert r["uncovered"] and "alpha.py" in r["uncovered"][0], r


def t_the_committed_declaration_covers_every_stage_of_the_real_finish():
    """The completeness check against this project's own finish, which is the one that matters."""
    r = C.judge()
    assert not r["fails"], r["fails"]
    assert r["declared"] == r["in_finish"], (r["declared"], r["in_finish"])


def t_the_grid_class_is_covered_where_the_grid_is_declared_and_not_where_it_is_not():
    """The per-board half. On 16 September this read three classes on the boards without a grid; two of those
    three were measured that evening and have a prevention that does not depend on a grid at all (prefanout
    lays the plane-pad vias, and the refill plus the band keep-outs stop a pour retreating from its own stitch
    via). What is left is the one that is honestly unprevented: a pour island with no via of its own net,
    which fires on every board and every round. D and E declare the grid and are covered.

    17 September 2026: board P left this list without declaring anything. It MEASURED the grid on its own
    copper, 21 open connections against 0 without it, and refused it with those numbers in its board file,
    which is the rule's second half answered rather than ignored.

    17 September 2026, later: BOARD C JOINED IT, by the same route and with its own numbers. C24 without the
    grid routed 0 hard and 0 unrouted of 133 nets in 1 h 21 min; C25 with a 2.1 mm grid ran its full 6 h cap to
    21 unrouted, closed none of them in a further hour of stub routing, and made the very thing the grid is
    supposed to prevent worse (2 islands stitched and 5 left, against 1 and 2 on the control). Board A has the
    measurement as of tonight as well and has not written it down yet, because its arms are still running: it
    is the one board still named here."""
    for letter in ("c", "d", "e", "p"):
        assert not C.judge(letter=letter)["uncovered"], letter
    for letter in ("a",):
        u = C.judge(letter=letter)["uncovered"]
        assert len(u) == 1, (letter, u)
        assert "pour_stitch" in u[0] and "gnd_grid" in u[0], u


def t_a_board_with_no_chain_has_no_closers():
    r = C.judge(letter="e5")
    assert not r["uncovered"] and not r["fails"], r
    assert any("no chain" in n for n in r["notes"]), r["notes"]


def t_a_tool_that_changes_copper_and_that_nothing_runs_is_named():
    """Three times a tool has been written, tested and left in the directory while the rule it was written for
    went on failing: bypass_place.py for a day, widen_net.py for the morning it was written, and logo_silk.py
    since the mark was traced, which is why no board of the seven carries a silkscreen polygon. A tool nobody
    runs is a plan, not a tool."""
    import closer_audit as C
    idle = C.never_invoked()
    assert isinstance(idle, list)
    import yaml, os
    d = yaml.safe_load(open(os.path.join(TOOLS, "pcb_closers.yaml"), encoding="utf-8"))
    declared = {e["tool"] for e in (d.get("idle_tools") or [])}
    assert not (set(idle) - declared), "copper-changing tools nothing runs and nothing declares: %s" % sorted(set(idle) - declared)
    assert all(str(e.get("why", "")).strip() for e in (d.get("idle_tools") or [])), "an idle tool with no reason"


def t_a_declaration_is_not_an_invocation():
    """The first version read the yaml files too, so pcb_closers.yaml naming a tool it declares IDLE became its
    own proof that something runs it, and the same for every tool named in the coverage map. A comment is not
    an invocation either: the paragraph explaining this rule names logo_silk.py, which took it off its own
    list."""
    import os
    src = open(os.path.join(TOOLS, "closer_audit.py"), encoding="utf-8").read()
    i = src.index("def invoked_names(")
    w = src[i:i + 1400]
    assert '"*.yaml"' not in w, "a yaml declaration still counts as an invocation"
    assert 'l.split("#", 1)[0]' in w, "a mention in a comment still counts as an invocation"


def t_the_mark_the_owner_ruled_is_drawn_by_a_stage_and_placed_by_a_declaration():
    """No board of the seven carried a silkscreen polygon: logo_silk.py could draw the mark and nothing chose
    where it goes. The position is declared per board, never found at generation time, because a position that
    moves whenever a part moves rewrites the board file on every generation."""
    import os, json
    full = open(os.path.join(TOOLS, "full.sh"), encoding="utf-8").read()
    assert "logo_stage.py" in full, "no chain draws the mark"
    src = open(os.path.join(TOOLS, "logo_stage.py"), encoding="utf-8").read()
    assert '_bt.value(letter, "logo")' in src, "the position is not read from the board's own declaration"
    assert "not drawing a second mark" in src, "a second run would draw the mark twice"
    a = json.load(open(os.path.join(TOOLS, "boards", "a.json"), encoding="utf-8"))
    assert a.get("logo", {}).get("width_mm"), "board A declares no position for the mark"
    assert a["logo"].get("why"), "the position is declared with no reason"


def t_a_prevention_measured_and_refused_is_an_answer():
    """Board P, 17 September 2026. A DECLARED ZERO IS AN ANSWER AND AN UNDECLARED ZERO IS NOT is this
    project's rule everywhere else and this gate did not apply it: board P measured the ground-via grid on its
    own copper, 21 open connections against 0 without it, wrote the numbers into `boards/p.json` and declared
    none, and PLC-002 still read the island class as one nobody had covered. Measuring a prevention and
    refusing it with evidence IS the second half of the rule; not having measured it is not.

    The distinction is the basis: a board whose reason still says NOT MEASURED has not answered."""
    import json, tempfile, os as _o
    sys.path.insert(0, TOOLS)
    import closer_audit as ca
    d = tempfile.mkdtemp(); b = _o.path.join(d, "boards"); _o.makedirs(b)
    def write(letter, obj):
        json.dump(obj, open(_o.path.join(b, "%s.json" % letter), "w"))
    write("x", {"gnd_grid": {"pitch": 2.1}})
    write("y", {"_gnd_grid_why": "measured on this board: 21 open with it against 0 without"})
    write("z", {"_gnd_grid_why": "NOT MEASURED ON THIS BOARD YET"})
    write("w", {})
    old = ca.HERE
    try:
        ca.HERE = d
        assert ca.board_declares("x", "gnd_grid") == ca.DECLARED
        assert ca.board_declares("y", "gnd_grid") == ca.REFUSED, "a measured refusal is not read as an answer"
        assert ca.board_declares("z", "gnd_grid") == ca.SILENT, "'not measured yet' counts as an answer"
        assert ca.board_declares("w", "gnd_grid") == ca.SILENT
    finally:
        ca.HERE = old


def t_the_boards_that_have_not_measured_it_are_still_uncovered():
    """Executed on the real tree: the gate must still name a board that has said nothing."""
    sys.path.insert(0, TOOLS)
    import closer_audit as ca
    said = {L: ca.board_declares(L, "gnd_grid") for L in ("a", "c", "d", "e", "p")}
    assert said["d"] == ca.DECLARED and said["e"] == ca.DECLARED, said
    assert said["p"] == ca.REFUSED, "board P's measured refusal is not in its board file any more: %s" % said["p"]
    for L in ("a", "c"):
        if said[L] == ca.SILENT:
            r = ca.judge(letter=L)
            assert any("pour_stitch" in u for u in r["uncovered"]), \
                "board %s has not measured the grid and the class reads as covered" % L.upper()
