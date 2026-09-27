#!/usr/bin/env python3
"""The list ANA-001 measures against is complete (MESHSAT-862, 19 September 2026).

`sensitive_nodes.py` refuses a SENSITIVE declaration that names a power terminal: a net carrying a transistor
or an inductor pad is a conductor of the switching loop and not a node behind a filter (18 September 2026).
Nothing asked the other half. The rule measures each sensitive node's clearance from the nearest SWITCHING
copper, and which copper is switching is a declaration, so a switching net nobody declared is copper the
reading never looks at, and the PASS that comes back is taken against an incomplete list.

`switch_list.py` is the report that names the candidates. It decides nothing, because whether a given power
node is switching for this rule is a judgement (a synchronous converter's midpoint certainly; a hot-swap pass
element arguably not), and it reads the netlist and the board's own text rather than pcbnew, so it runs where
KiCad is not.
"""
import os, sys, json, tempfile, shutil

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import switch_list as S


def _netlist(rows):
    """rows: [(net, [(ref, pin, pinfunction), ...]), ...] -> a KiCad-shaped netlist file."""
    out = ["(export (version \"E\")", " (nets"]
    for i, (net, nodes) in enumerate(rows, 1):
        out.append('  (net (code "%d") (name "/%s")' % (i, net))
        for ref, pin, fn in nodes:
            out.append('   (node (ref "%s") (pin "%s") (pinfunction "%s") (pintype "passive"))' % (ref, pin, fn))
        out.append("  )")
    out.append(" )")
    out.append(")")
    return "\n".join(out)


def _tree(rows, zones=(), patterns=None):
    d = tempfile.mkdtemp(prefix="switchlist-")
    n = os.path.join(d, "b.net"); open(n, "w").write(_netlist(rows))
    b = os.path.join(d, "b.kicad_pcb")
    open(b, "w").write("(kicad_pcb\n" + "".join(
        '  (zone (net 1) (net_name "%s") (layer "F.Cu") (hatch edge 0.5))\n' % z for z in zones) + ")\n")
    y = os.path.join(d, "sens.yaml")
    body = "boards:\n x:\n" + ("  switch_nets: [%s]\n" % ", ".join('"%s"' % p for p in patterns)
                               if patterns is not None else "")
    open(y, "w").write(body)
    return d, n, b, y


def _judge(rows, zones=(), patterns=None):
    d, n, b, y = _tree(rows, zones, patterns)
    old = S.SENS
    try:
        S.SENS = y
        return S.judge(n, b, "x")
    finally:
        S.SENS = old
        shutil.rmtree(d, ignore_errors=True)


SWNODE = ("SW_A", [("Q1", "1", "D"), ("Q2", "2", "S"), ("L1", "1", "1")])
RAIL = ("VOUT", [("L1", "2", "2"), ("C1", "1", "1")])


def t_a_switching_node_nobody_declared_is_named():
    """THE DEFECTIVE FIXTURE: a transistor's drain and an inductor's pad on one net, and the declaration does
    not match it. Expected verdict FAIL, with the parts that make it a candidate named."""
    r = _judge([SWNODE, RAIL], patterns=["NOTHING_*"])
    assert [c["net"] for c in r["undeclared"]] == ["SW_A"], r
    assert r["undeclared"][0]["transistors"] == ["Q1", "Q2"], r
    assert r["undeclared"][0]["inductors"] == ["L1"], r


def t_the_same_node_inside_the_declaration_is_not_named():
    """THE ACCEPTABLE FIXTURE: the identical netlist with a pattern that matches. Expected verdict PASS."""
    r = _judge([SWNODE, RAIL], patterns=["SW_*"])
    assert r["undeclared"] == [], r
    assert r["declared"] == ["SW_A"], r
    assert len(r["shaped"]) == 1, r


def t_a_poured_net_is_a_rail_by_construction():
    """Every converter's output pour carries the pad that feeds it, so a poured net is not a candidate. Board
    E's DC_HS and board A's VBAT are exactly this case on the real boards."""
    r = _judge([SWNODE, RAIL], zones=("/SW_A",), patterns=["NOTHING_*"])
    assert r["undeclared"] == [], r
    assert "SW_A" in r["planes"], r


def t_a_gate_net_is_not_a_switching_node():
    """A gate carries a transistor pad and is the thing that DRIVES the switching, not the switching copper.
    Two gates on one net would otherwise read as a half bridge."""
    r = _judge([("GATE", [("Q1", "4", "G"), ("Q2", "4", "G"), ("R1", "1", "1")])], patterns=["NOTHING_*"])
    assert r["shaped"] == [], r


def t_a_board_that_declares_nothing_is_told_so_rather_than_passed():
    """An undeclared zero is not a declared one (the house law of 19 September, in the third place). Boards B
    and C declare no switch_nets at all and ANA-001 has no denominator on them."""
    r = _judge([SWNODE], patterns=None)
    assert r["declares_nothing"] and not r["declared_zero"], r
    r2 = _judge([SWNODE], patterns=[])
    assert r2["declared_zero"] and not r2["declares_nothing"], r2


def t_it_reads_the_netlist_and_the_board_text_and_never_pcbnew():
    """It has to run where KiCad is not, because the question is about a DECLARATION and is asked before the
    copper, the same reason sensitive_nodes' declaration half runs on the runner."""
    src = open(os.path.join(TOOLS, "switch_list.py"), encoding="utf-8").read()
    assert "import pcbnew" not in src and "pcbnew." not in src, "the report imports the board reader"


def t_it_is_advisory_because_whether_a_node_is_switching_is_a_judgement():
    src = open(os.path.join(TOOLS, "switch_list.py"), encoding="utf-8").read()
    assert "advisory=True" in src, "a report that decides a rule is not a report"
