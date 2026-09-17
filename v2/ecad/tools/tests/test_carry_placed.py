#!/usr/bin/env python3
"""The placement's evidence may only be carried to a board that still has that placement (rule PLC-001,
17 September 2026).

THE DEFECT, on the tree this was written against: `finish.sh` copied `hardset-placed`, `place_audit` and
`regionfit` from the route tree's `out/` into the board's `routed/` snapshot with `cp`. That is a verdict
about one file being moved into a directory holding another; nothing compared the two, and a verdict carrying
no board identity could not be compared later either. The evidence looked current and belonged to nothing.
"""
import os, sys, json, tempfile
import carry_placed as C

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _p(**refs):
    """A placement: reference -> (x_nm, y_nm, degrees, side)."""
    return dict(refs)


def t_a_board_nothing_moved_on_carries_its_placement():
    a = _p(U1=(1000000, 2000000, 0.0, "F"), C1=(5000000, 2000000, 90.0, "B"))
    assert C.differences(a, dict(a)) == []


def t_a_part_that_moved_refuses_the_carry():
    a = _p(U1=(1000000, 2000000, 0.0, "F"))
    b = _p(U1=(1000000, 2500000, 0.0, "F"))
    d = C.differences(a, b)
    assert len(d) == 1 and "U1 moved 0.500 mm" in d[0], d


def t_a_rounding_of_a_micrometre_is_not_a_move():
    """A board rewritten by KiCad can round a coordinate; a part that moved cannot hide inside a micrometre."""
    a = _p(U1=(1000000, 2000000, 0.0, "F"))
    assert C.differences(a, _p(U1=(1000600, 2000000, 0.0, "F"))) == []
    assert C.differences(a, _p(U1=(1002000, 2000000, 0.0, "F"))) != []


def t_a_rotation_or_a_side_change_is_a_move():
    a = _p(U1=(0, 0, 0.0, "F"))
    assert "turned" in C.differences(a, _p(U1=(0, 0, 90.0, "F")))[0]
    assert "changed side" in C.differences(a, _p(U1=(0, 0, 0.0, "B")))[0]


def t_a_part_added_or_lost_between_the_two_boards_is_named():
    assert "C9 is on the routed board and was not placed" in C.differences(_p(U1=(0, 0, 0.0, "F")),
                                                                          _p(U1=(0, 0, 0.0, "F"), C9=(1, 1, 0.0, "F")))
    assert "C9 is on the placed board and not on the routed one" in C.differences(_p(C9=(1, 1, 0.0, "F")), {})


def t_the_carried_verdict_names_both_boards_and_keeps_its_result():
    rec = {"verdict": "PASS", "counts": {"hard": 0}, "note": "placed", "inputs": {"drc": "out/x-placed-drc.json"}}
    got = C.rewrite(rec, "aaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbb", "pcb-d-aprs.kicad_pcb", 412)
    assert got["verdict"] == "PASS", got
    assert got["inputs"]["board"]["sha256_16"] == "bbbbbbbbbbbbbbbb", got["inputs"]
    assert got["inputs"]["measured_board"] == {"sha256_16": "aaaaaaaaaaaaaaaa", "stage": "placed"}, got["inputs"]
    assert got["carried"]["footprints_compared"] == 412, got["carried"]
    assert "412 footprint positions" in got["note"], got["note"]
    assert rec["inputs"] == {"drc": "out/x-placed-drc.json"}, "the original verdict must not be edited in place"


def t_the_finish_proves_the_carry_instead_of_copying_it():
    """THE STRUCTURAL HALF: the defective tree copied the three files with `cp` and is the fixture here."""
    s = open(os.path.join(TOOLS, "finish.sh"), encoding="utf-8").read()
    assert "carry_placed.py" in s, "the finish does not prove the placement carry"
    bad = [l.strip() for l in s.splitlines()
           if "cp " in l and "routed/" in l and any(v in l for v in ("hardset-placed", "place_audit", "regionfit", "_pv"))]
    assert not bad, "the placement's evidence is still copied without proof:\n  " + "\n  ".join(bad)


def t_the_identity_it_writes_is_the_one_the_registry_compares():
    """`rules_status._named_board` reads `inputs.board`, either a dict with sha256_16 or a bare string. A
    carried verdict has to answer that question or it is anonymous again."""
    sys.path.insert(0, TOOLS)
    import rules_status as S
    rec = C.rewrite({"verdict": "PASS", "inputs": {}}, "a" * 16, "c" * 16, "b.kicad_pcb", 7)
    assert S._named_board(rec) == "c" * 16, S._named_board(rec)
