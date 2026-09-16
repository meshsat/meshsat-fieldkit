#!/usr/bin/env python3
"""A reference's prefix is its LETTERS, not its first character (rule CMP-001, 16 September 2026).

`derate.py` decides whether a part carries a RATING from its reference designator, and it took one character
to do it. `T` is a tantalum capacitor, so `TP` was read as one too, and a test point's value string is the NET
IT TAPS: board C's `TP6` carried the value "+5V", was judged as a part rated 5.0 V against the 5.0 V rail it
taps, and failed for wanting a 20 percent margin over itself. CMP-001 is a BLOCKER, so that single line stopped
board C's whole chain at the pre-route gate, on both grid arms, for a defect that is not on the board.

This is the recurring shape of the project written down once more: a guard whose condition is a HYPOTHESIS
about the data. The hypothesis here was that one character names a part family.

Two fixtures, both ways, as the standard requires: a DEFECTIVE netlist whose expected verdict is FAIL, and an
ACCEPTABLE netlist whose expected verdict is PASS. The acceptable one is board C's own case.
"""
import os, sys, json, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import derate


def _fixture(d, comps, nets, rails):
    os.makedirs(d, exist_ok=True)
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in sorted(comps.items()))
    n = ""
    for i, (name, nodes) in enumerate(sorted(nets.items()), 1):
        body = "".join('      (node (ref "%s") (pin "%s"))\n' % (r, p) for r, p in nodes)
        n += '    (net (code %d) (name "/%s")\n%s    )\n' % (i, name, body)
    p = os.path.join(d, "b.net")
    open(p, "w").write("(export (version E)\n  (components\n%s  )\n  (nets\n%s  )\n)\n" % (c, n))
    json.dump({"rails": {k: {"volts": v} for k, v in rails.items()}}, open(os.path.join(d, "b-intent.json"), "w"))
    return p


def _run(p, cwd):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "derate.py"), p], cwd=cwd,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def t_a_test_point_is_not_a_tantalum():
    """THE ACCEPTABLE FIXTURE, expected verdict PASS. Board C's own case: TP6 taps +5V and its value string is
    the net name. Nothing on this board is under-rated."""
    d = tempfile.mkdtemp(prefix="derate-tp-")
    p = _fixture(d, {"TP6": "+5V", "TP7": "+3V3", "C1": "10u 16V", "U1": "REG"},
                 {"+5V": [("TP6", "1"), ("C1", "1"), ("U1", "3")],
                  "+3V3": [("TP7", "1"), ("U1", "5")],
                  "GND": [("C1", "2"), ("U1", "2")]},
                 {"+5V": 5.0, "+3V3": 3.3})
    rc, out = _run(p, d)
    assert rc == 0, "a test point was judged as a rated part:\n%s" % out[-600:]
    assert "TP6" not in out, "a test point reached the judgement at all:\n%s" % out[-600:]


def t_an_under_rated_capacitor_is_still_refused():
    """THE DEFECTIVE FIXTURE, expected verdict FAIL. Board A's finding of 12 September in miniature: a 50 V
    part on the Power over Ethernet stage's 54 V output. The exclusion above must not buy it a pass."""
    d = tempfile.mkdtemp(prefix="derate-poe-")
    p = _fixture(d, {"C9": "22u 50V X7R 1210", "TP9": "VPOE", "U2": "PoE"},
                 {"VPOE": [("C9", "1"), ("TP9", "1"), ("U2", "4")],
                  "GND": [("C9", "2"), ("U2", "2")]},
                 {"VPOE": 54.0})
    rc, out = _run(p, d)
    assert rc == 1, "a 50 V part on a 54 V rail passed:\n%s" % out[-600:]
    assert "C9" in out and "64.8 V" in out, out[-600:]
    assert "TP9" not in out, "the test point on the same rail was judged too:\n%s" % out[-600:]


def t_the_prefix_is_every_leading_letter():
    """The unit behind both fixtures, so a new designator prefix is decided in ONE place. A one-character test
    cannot separate these four."""
    assert derate.rated_kind("T6") and derate.rated_kind("C12") and derate.rated_kind("F2")
    assert not derate.rated_kind("TP6") and not derate.rated_kind("FID1") and not derate.rated_kind("MH3")
    assert not derate.rated_kind("R7") and not derate.rated_kind("U9")
