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


# ---------------------------------------------------------------------------------------------------------
# THE PRE-ROUTER MOVES PARTS, AND THAT IS NOT A BREACH (17 September 2026, found by this tool's first run).
#
# Board D's placed snapshot and its committed board differ by R20 and R21, 1.600 mm each: the two series
# resistors of a USB pair, swapped by the pre-router's station swap, which runs before the router and is a
# measured, recorded operation. So there are two boards before the route, and the placement that SHIPPED is
# the one the pre-route DRC measured, over the same fifteen hard types and after every part move.

def t_the_stage_travels_in_the_carried_verdict():
    got = C.rewrite({"verdict": "PASS", "inputs": {}}, "a" * 16, "b" * 16, "x.kicad_pcb", 211, stage="pre-route")
    assert got["inputs"]["measured_board"]["stage"] == "pre-route", got["inputs"]
    assert got["carried"]["from"] == "pre-route", got["carried"]
    assert "from the pre-route board" in got["note"], got["note"]


def t_the_fallback_is_the_pre_route_board_and_only_the_hard_set_comes_with_it():
    """place_audit is about escape fans at the parts the pre-router just moved, so it is NOT carried under the
    fallback; the hard-set judgement is, because it was taken after the move."""
    assert C.CARRY_PREROUTE == ("hardset-pre-route-drc",), C.CARRY_PREROUTE
    assert "place_audit" not in C.CARRY_PREROUTE
    import inspect
    src = inspect.getsource(C.main)
    assert "moved_pre" in src and "CARRY_PREROUTE" in src, "the fallback is gone from main"


def t_a_board_whose_parts_moved_with_no_pre_route_board_carries_nothing():
    """The refusal still exists: without a board that matches, this board's placement was never measured."""
    import inspect
    src = inspect.getsource(C.main)
    assert "if moved and pre:" in src, "the fallback must be conditional on a pre-route board existing"
    assert "was never measured and nothing is carried" in src


# ---------------------------------------------------------------------------------------------------------
# AN EXCHANGE OF SEATS IS NOT A MOVE (17 September 2026, and this is what board D actually did).
#
# R20 and R21 read 1.600 mm from where the placed snapshot put them, and they are in each other's seats: the
# pre-router's PAIR_SWAP, which exchanges a pair's two series resistors and runs before the router. Two parts
# of the SAME LAND exchanging two seats changes no courtyard, no hole and no clearance relation, because the
# set of occupied seats is identical. Any other move is a move.

def _p5(**refs):
    """A placement carrying the footprint id: reference -> (x, y, deg, side, fpid)."""
    return dict(refs)


def t_two_parts_of_one_land_exchanging_seats_is_not_a_move():
    a = _p5(R20=(132000000, 86400000, 0.0, "F", "R_0402"), R21=(132000000, 88000000, 0.0, "F", "R_0402"))
    b = _p5(R20=(132000000, 88000000, 0.0, "F", "R_0402"), R21=(132000000, 86400000, 0.0, "F", "R_0402"))
    assert C.differences(a, b) == [], C.differences(a, b)
    assert C.swaps(a, b, ["R20", "R21"]) == ["R20 took R21's seat", "R21 took R20's seat"]


def t_two_parts_of_different_lands_exchanging_seats_is_a_move():
    """A 0402 in an 0805's seat is a different board, whatever the coordinates say."""
    a = _p5(R20=(132000000, 86400000, 0.0, "F", "R_0402"), C9=(132000000, 88000000, 0.0, "F", "C_0805"))
    b = _p5(R20=(132000000, 88000000, 0.0, "F", "R_0402"), C9=(132000000, 86400000, 0.0, "F", "C_0805"))
    assert C.swaps(a, b, ["R20", "C9"]) is None
    assert len(C.differences(a, b)) == 2, C.differences(a, b)


def t_one_part_moving_into_a_free_seat_is_still_a_move():
    a = _p5(R20=(132000000, 86400000, 0.0, "F", "R_0402"), R21=(132000000, 88000000, 0.0, "F", "R_0402"))
    b = _p5(R20=(132000000, 90000000, 0.0, "F", "R_0402"), R21=(132000000, 88000000, 0.0, "F", "R_0402"))
    d = C.differences(a, b)
    assert len(d) == 1 and d[0].startswith("R20 moved"), d


def t_a_rotation_inside_a_swap_is_a_move():
    """Same seats, different angle: the copper under one of them is not the same."""
    a = _p5(R20=(0, 0, 0.0, "F", "R_0402"), R21=(0, 1600000, 0.0, "F", "R_0402"))
    b = _p5(R20=(0, 1600000, 90.0, "F", "R_0402"), R21=(0, 0, 0.0, "F", "R_0402"))
    assert C.swaps(a, b, ["R20", "R21"]) is None
    assert C.differences(a, b) != []


def t_the_fallback_is_carried_under_the_name_the_rule_asks_by():
    """A second verdict NAME in the coverage map makes the fallback mandatory for every board, and a stale
    copy of it then answers for a board that never took it: board P read PRE_AUDIT from an 11 September file
    for ten minutes this morning because of exactly that. The pre-route judgement is carried as
    `hardset-placed`, and what it is travels inside the verdict."""
    import inspect, yaml, os
    src = inspect.getsource(C.main)
    assert '"hardset-placed" if n in CARRY_PREROUTE' in src, "the fallback no longer lands under one name"
    cov = yaml.safe_load(open(os.path.join(TOOLS, "pcb_rules_coverage.yaml")))["coverage"]["PLC-001"]
    named = [x.strip() for x in cov["verification"]["verdict"].split(",")]
    assert "hardset-pre-route-drc" not in named, "the fallback is named as a rule verdict again: %s" % named
    assert named == ["hardset-placed", "place_audit"], named
