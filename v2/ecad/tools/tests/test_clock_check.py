#!/usr/bin/env python3
"""The crystal load network (rule CLK-001, MESHSAT-862, 16 September 2026).

A crystal with no load capacitors, or with one, does not start. It is the cheapest way to have a board that is
perfectly routed, perfectly assembled and dead: nothing electrical is wrong with it, the part simply never
oscillates, and every other check in this project passes it.

The first version of this check called a SERIES DAMPING RESISTOR a defect, on four boards at once, and board
D's own crystal carries the reason for that resistor in its value string: "Rd 1.5k per SLLS413 figure 6". That
is this project's recurring shape, a guard whose condition is a hypothesis about the data, so it has a rule of
its own here.
"""
import os, sys, json, tempfile, subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import clock_check


def _net(d, comps, nets):
    """comps: {ref: value}. nets: {net: [(ref, pin), ...]}."""
    os.makedirs(d, exist_ok=True)
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in sorted(comps.items()))
    n = ""
    for i, (name, nodes) in enumerate(sorted(nets.items()), 1):
        body = "".join('      (node (ref "%s") (pin "%s"))\n' % (r, p) for r, p in nodes)
        n += '    (net (code %d) (name "/%s")\n%s    )\n' % (i, name, body)
    p = os.path.join(d, "b.net")
    open(p, "w").write("(export (version E)\n  (components\n%s  )\n  (nets\n%s  )\n)\n" % (c, n))
    return p


def _run(p, cwd):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "clock_check.py"), p], cwd=cwd,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def t_a_crystal_with_one_load_capacitor_is_refused():
    d = tempfile.mkdtemp(prefix="clk-one-")
    p = _net(d, {"Y1": "12 MHz", "C1": "15p", "U1": "MCU"},
             {"XIN": [("Y1", "1"), ("C1", "1"), ("U1", "20")],
              "XOUT": [("Y1", "3"), ("U1", "21")],
              "GND": [("C1", "2"), ("Y1", "2"), ("Y1", "4")]})
    rc, out = _run(p, d)
    assert rc == 1, "a crystal with one load capacitor passed:\n%s" % out[-400:]
    assert "no load capacitor" in out, out[-400:]


def t_two_load_capacitors_of_different_values_are_refused():
    d = tempfile.mkdtemp(prefix="clk-mismatch-")
    p = _net(d, {"Y1": "12 MHz", "C1": "15p", "C2": "22p", "U1": "MCU"},
             {"XIN": [("Y1", "1"), ("C1", "1"), ("U1", "20")],
              "XOUT": [("Y1", "3"), ("C2", "1"), ("U1", "21")],
              "GND": [("C1", "2"), ("C2", "2")]})
    rc, out = _run(p, d)
    assert rc == 1, "an unbalanced load pair passed:\n%s" % out[-400:]
    assert "off frequency" in out, out[-400:]


def t_a_series_damping_resistor_is_not_a_defect():
    """The false positive this check shipped with, and the reason it has a rule. Board D's hub crystal carries
    the resistor's justification in its own value string."""
    d = tempfile.mkdtemp(prefix="clk-damp-")
    p = _net(d, {"Y1": "6 MHz (CL 20 pF; Rd 1.5k per SLLS413 figure 6)", "C1": "27p", "C2": "27p",
                 "R1": "1.5k", "U1": "HUB"},
             {"XTAL1": [("Y1", "1"), ("C1", "1"), ("U1", "20")],
              "XTAL2R": [("Y1", "3"), ("C2", "1"), ("R1", "1")],
              "XTAL2": [("R1", "2"), ("U1", "21")],
              "GND": [("C1", "2"), ("C2", "2")]})
    rc, out = _run(p, d)
    assert rc == 0, "a crystal with its damping resistor was refused:\n%s" % out[-500:]


def t_a_second_driving_part_on_a_crystal_node_is_refused():
    d = tempfile.mkdtemp(prefix="clk-stub-")
    p = _net(d, {"Y1": "12 MHz", "C1": "15p", "C2": "15p", "U1": "MCU", "U2": "somebody else"},
             {"XIN": [("Y1", "1"), ("C1", "1"), ("U1", "20"), ("U2", "5")],
              "XOUT": [("Y1", "3"), ("C2", "1"), ("U1", "21")],
              "GND": [("C1", "2"), ("C2", "2")]})
    rc, out = _run(p, d)
    assert rc == 1, "a second driver on a crystal node passed:\n%s" % out[-400:]
    assert "driving parts" in out, out[-400:]


def t_a_board_with_no_crystal_is_inconclusive_and_never_a_pass():
    d = tempfile.mkdtemp(prefix="clk-none-")
    p = _net(d, {"U1": "MCU"}, {"GND": [("U1", "1")]})
    rc, out = _run(p, d)
    assert rc == 3, "a board with no crystal did not come out INCONCLUSIVE:\n%s" % out[-300:]


def t_the_committed_boards_pass_where_they_have_a_netlist():
    """The real boards. A board whose netlist is not in this tree is skipped, not assumed."""
    import glob
    from harness import Skip
    ecad = os.path.dirname(TOOLS)
    nets = sorted(glob.glob(os.path.join(ecad, "pcb-*", "out", "*.net")))
    if not nets: raise Skip("no netlist in this tree")
    bad = []
    for n in nets:
        rows, errs = clock_check.judge(n)
        if errs: bad.append("%s: %s" % (os.path.basename(n), "; ".join(errs)[:160]))
    assert not bad, "crystals that would not start: %s" % bad
