#!/usr/bin/env python3
"""One deliberate ground system, or a partition drawn on purpose (rule GND-001, 16 September 2026).

The rule asks for one of two things and the difference is in the netlist, not in anybody's opinion: the board
has ONE ground and says so, or every partition is declared with its crossing points and the signals that cross.
It read "generation intends to comply and nothing verifies it" on six boards.

Board E is why it matters. Its `GND_V`, the vehicle-side return, meets `GND` at exactly one part, the second
winding of the SRF1260 common-mode choke, and TWO SIGNALS cross that partition: the hot-swap's power-good and
the shore inhibit. Nothing in this tree said any of that until the gate found it, and the declaration it now
carries says the thing that matters most about it: this is a filter, not an isolation barrier, and must not be
read as one.
"""
import os, sys, json, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import ground_system as G


def _net(d, nets, values=None):
    os.makedirs(d, exist_ok=True)
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in sorted((values or {}).items()))
    n = ""
    for i, (name, nodes) in enumerate(sorted(nets.items()), 1):
        body = "".join('      (node (ref "%s") (pin "%s"))\n' % (r, p) for r, p in nodes)
        n += '    (net (code %d) (name "/%s")\n%s    )\n' % (i, name, body)
    p = os.path.join(d, "b.net")
    open(p, "w").write("(export (version E)\n  (components\n%s  )\n  (nets\n%s  )\n)\n" % (c, n))
    return p


def _judge(nets, decl, values=None):
    d = tempfile.mkdtemp(prefix="gnd-")
    p = _net(d, nets, values)
    keep = G.board_decl
    try:
        G.board_decl = lambda letter: decl
        return G.judge(p, "x")
    finally:
        G.board_decl = keep


def t_one_ground_declared_passes_and_undeclared_does_not():
    nets = {"GND": [("U1", "2"), ("C1", "2")], "VCC": [("U1", "1"), ("C1", "1")]}
    assert not _judge(nets, {"GND": {"what": "the one ground"}})["fails"]
    r = _judge(nets, {})
    assert r["fails"] and "does not declare it" in r["fails"][0], r


def t_a_second_ground_must_be_declared_with_its_crossing():
    """DEFECTIVE fixture: two grounds joined by a choke, nothing declared."""
    nets = {"GND": [("U1", "2"), ("L2", "4")], "GND_V": [("J1", "2"), ("L2", "3")],
            "VIN": [("J1", "1"), ("L2", "1")]}
    r = _judge(nets, {})
    assert any("not declared" in f for f in r["fails"]), r["fails"]
    assert r["crossings"] == {"L2": ["GND", "GND_V"]}, r["crossings"]


def t_the_declaration_makes_the_same_board_pass():
    """ACCEPTABLE fixture: the same netlist with the partition, its crossing and its crossing signal declared."""
    nets = {"GND": [("U1", "2"), ("L2", "4")], "GND_V": [("J1", "2"), ("L2", "3")],
            "VIN": [("J1", "1"), ("L2", "1")], "PGD": [("J1", "3"), ("U1", "5")]}
    decl = {"GND": {"what": "the board"},
            "GND_V": {"what": "the vehicle side", "crossings": ["L2"], "signals": ["PGD"]}}
    r = _judge(nets, decl)
    assert not r["fails"], r["fails"]
    assert ("PGD", ["GND", "GND_V"]) in r["signals"], r["signals"]


def t_a_signal_that_crosses_and_is_not_listed_is_refused():
    nets = {"GND": [("U1", "2"), ("L2", "4")], "GND_V": [("J1", "2"), ("L2", "3")],
            "SECRET": [("J1", "3"), ("U1", "5")]}
    decl = {"GND": {"what": "the board"}, "GND_V": {"what": "the vehicle side", "crossings": ["L2"]}}
    r = _judge(nets, decl)
    assert any("SECRET crosses the partition" in f for f in r["fails"]), r["fails"]


def t_a_declaration_that_has_drifted_from_the_board_is_refused():
    """A declaration naming a crossing the board does not have is worse than none: it reads as checked."""
    nets = {"GND": [("U1", "2"), ("L2", "4")], "GND_V": [("J1", "2"), ("L2", "3")]}
    decl = {"GND": {"what": "the board"},
            "GND_V": {"what": "the vehicle side", "crossings": ["L2", "L9"]}}
    r = _judge(nets, decl)
    assert any("L9" in f and "one ground only" in f for f in r["fails"]), r["fails"]


def t_board_e_is_declared_as_a_filter_and_not_as_isolation():
    """The sentence that matters in board E's own declaration, held as a rule: somebody reading GND_V as an
    isolation barrier would design to it, and it is joined to GND at DC through the choke."""
    p = os.path.join(TOOLS, "boards", "e.json")
    d = json.load(open(p, encoding="utf-8"))
    g = (d.get("grounds") or {}).get("GND_V") or {}
    assert g, "board E no longer declares its vehicle-side ground"
    assert "NOT an isolation barrier" in g.get("what", ""), g.get("what", "")[:120]
    assert g.get("crossings") == ["L2"], g.get("crossings")
    assert set(g.get("signals") or []) == {"DCIN_PGD", "SHORE_INHIBIT"}, g.get("signals")
