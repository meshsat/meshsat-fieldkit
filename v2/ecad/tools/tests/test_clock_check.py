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
    # Since 16 September 2026 a crystal whose C_L nobody has declared is INCONCLUSIVE rather than PASS, and a
    # synthetic netlist belongs to no board and so declares none. The subject of this test is the RESISTOR, so
    # it is asked of the judgement rather than of the exit code: nothing about R1 may appear as a defect.
    rows, bad = clock_check.judge(p)
    assert not any("resistor" in b for b in bad), "the damping resistor was called a defect: %s" % bad
    assert rc in (0, 3), "a crystal with its damping resistor was refused:\n%s" % out[-500:]


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


def t_the_load_network_is_compared_with_the_part_s_own_load_capacitance():
    """The number that decides whether an oscillator runs on frequency is C_L, and it lives in a datasheet.
    The board declares it; the tool computes what the fitted capacitors present and compares."""
    import clock_check as C
    assert abs(C.presented_pf(15, 15, 3.0) - 10.5) < 0.01, "two 15 pF capacitors plus 3 pF of stray is 10.5 pF"
    assert abs(C.presented_pf(18, 18, 3.0) - 12.0) < 0.01
    assert C.presented_pf(None, 15, 3.0) is None, "a capacitor that is not a capacitance is not a load"


def t_the_rp2040_guide_s_own_worked_example_comes_out_where_it_says():
    """The Raspberry Pi hardware design guide works this arithmetic for the exact part on boards C and E:
    an ABM8-272-T3 wants 10 pF, two 15 pF capacitors give 7.5 pF in series, about 3 pF of pins and tracks is
    added, and 10.5 pF is 'close enough to the target of 10 pF'. A tool that disagreed with a vendor's own
    worked example would have the arithmetic wrong."""
    import clock_check as C
    p = C.presented_pf(15, 15, 3.0)
    assert 10.4 < p < 10.6, p
    assert abs(C.pull_ppm(10.0, p)) < 15, "a half-picofarad over target is a few parts per million, not tens"


def t_a_load_error_of_a_third_is_reported_in_parts_per_million():
    """Board B's three hub crystals carried an 18 pF part with 18 pF capacitors, which present 12 pF. The bar
    is 20 percent because of what the error DOES: this one is a third light and pulls the part about 54 ppm,
    which is more than a good crystal's whole tolerance."""
    import clock_check as C
    p = C.presented_pf(18, 18, 3.0)
    ppm = C.pull_ppm(18.0, p)
    assert 40 < ppm < 70, ppm
    assert abs(C.pull_ppm(12.0, p)) < 1, "the corrected 12 pF part is on frequency with the same capacitors"


def t_a_crystal_with_no_declared_load_capacitance_is_never_a_pass():
    src = open(os.path.join(TOOLS, "clock_check.py"), encoding="utf-8").read()
    assert "undeclared" in src and "_v.INCONCLUSIVE if undeclared" in src, \
        "a crystal whose C_L nobody wrote down passes silently"
