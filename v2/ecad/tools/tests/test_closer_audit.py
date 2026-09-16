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


def t_three_classes_are_covered_on_the_boards_that_declare_the_grid_and_not_on_the_others():
    """The per-board half, and the state of the set on 16 September 2026: D and E declare the ground-via grid
    and are covered; A, C and P do not and are not, which is a design item rather than a bookkeeping one."""
    for letter in ("d", "e"):
        assert not C.judge(letter=letter)["uncovered"], letter
    for letter in ("a", "c", "p"):
        u = C.judge(letter=letter)["uncovered"]
        assert len(u) == 3, (letter, u)
        assert all("gnd_grid" in x for x in u), u


def t_a_board_with_no_chain_has_no_closers():
    r = C.judge(letter="e5")
    assert not r["uncovered"] and not r["fails"], r
    assert any("no chain" in n for n in r["notes"]), r["notes"]
