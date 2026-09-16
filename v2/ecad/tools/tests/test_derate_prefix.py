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


# 16 September 2026: THE NODES, THE BIAS AND THE PROTECTOR. Before these, `derate.py` judged 48 parts on board
# A and NONE AT ALL on board C, because a rule that only knows about rails cannot ask about the nets where the
# highest voltages on a board actually live: switching nodes, bootstraps, charge pumps and a transmitter's
# output. Each rule below is paired with the text or the case it was written against.
import os as _os, sys as _sys, json as _json, tempfile as _tempfile, subprocess as _subprocess

_TOOLS = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_sys.path.insert(0, _TOOLS)


def _brd(d, rows, rails=None, nodes=None):
    """A netlist of (ref, value, [nets]) plus the intent file beside it."""
    _os.makedirs(d, exist_ok=True)
    comps = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v, _n in rows)
    by_net = {}
    for ref, _v, nets in rows:
        for n in nets: by_net.setdefault(n, []).append(ref)
    body = ""
    for i, (net, refs) in enumerate(sorted(by_net.items()), 1):
        nodes_s = "".join('      (node (ref "%s") (pin "1"))\n' % r for r in refs)
        body += '    (net (code %d) (name "/%s")\n%s    )\n' % (i, net, nodes_s)
    p = _os.path.join(d, "brd.net")
    open(p, "w").write("(export (version E)\n  (components\n%s  )\n  (nets\n%s  )\n)\n" % (comps, body))
    _json.dump({"rails": rails or {}, "nodes": nodes or {}},
               open(_os.path.join(d, "brd-intent.json"), "w"))
    return p


def _run_derate(p, d):
    r = _subprocess.run([_sys.executable, _os.path.join(_TOOLS, "derate.py"), p],
                        capture_output=True, text=True, cwd=d)
    return r.returncode, r.stdout + r.stderr


def t_an_indicator_is_not_an_inductor():
    """The defective case, from board B. `LED11`'s value is "green 5 V S1", the colour and the rail it shows.
    The prefix test was on the FIRST character, "L" is an inductor, and the "5 V" in that prose was read as a
    5 V rating and judged against the 5 V rail it sits on: three false refusals on a correct design, under a
    BLOCKER rule, which would have stopped board B's chain."""
    import derate
    assert derate.rated_kind("L11") is True, "an inductor is a rated part"
    assert derate.rated_kind("LED11") is False, "an indicator is being read as an inductor again"
    assert derate.rated_kind("TP6") is False and derate.rated_kind("T6") is True
    d = _tempfile.mkdtemp(prefix="derate-led-")
    p = _brd(d, [("LED11", "green 5 V S1", ["P5", "GND"])],
             rails={"P5": {"volts": 5.0, "amps_typ": 1.0}}, nodes={"GND": {"v_max": 0.0, "basis": "reference"}})
    rc, out = _run_derate(p, d)
    assert rc == 0, "an indicator was refused for its own colour:\n%s" % out[-600:]


def t_a_bootstrap_capacitor_is_judged_on_the_bias_and_not_on_the_height():
    """The acceptable case: a 25 V capacitor between a node 61 V above ground and the switching node it rides
    on. It sees the driver's own supply and nothing else, which is why every bootstrap part on this set is a
    small one. The defective reading is the same board with the ride removed."""
    rows = [("C1", "100n 25V", ["BOOT2", "SW2"])]
    nodes_ok = {"SW2": {"v_max": 54.0, "v_min": -1.0, "basis": "the boost node"},
                "BOOT2": {"v_max": 61.6, "v_min": 0.0, "basis": "the bootstrap", "rides_on": "SW2", "bias_v": 7.6}}
    d = _tempfile.mkdtemp(prefix="derate-boot-ok-")
    rc, out = _run_derate(_brd(d, rows, nodes=nodes_ok), d)
    assert rc == 0, "a bootstrap capacitor was refused for the height of the node it rides on:\n%s" % out[-600:]
    nodes_bad = {k: {kk: vv for kk, vv in v.items() if kk not in ("rides_on", "bias_v")}
                 for k, v in nodes_ok.items()}
    d2 = _tempfile.mkdtemp(prefix="derate-boot-bad-")
    rc2, out2 = _run_derate(_brd(d2, rows, nodes=nodes_bad), d2)
    assert rc2 == 1, "without the declared ride the same part must be refused, or the rule proves nothing"


def t_a_protector_is_judged_on_its_standoff_against_the_working_voltage():
    """The finding: an SMCJ33A stood off 33 V on a line specified to 36, on board A and twice on board E. A
    suppressor below its line's working maximum conducts in service instead of only on a transient. It is
    asked BEFORE the value string is read for a rating, because board A's part states no volts in its value
    and board E's happens to mention "50 V 100 ms" in a note: the same part and the same defect, and only one
    of them was caught while the order was decided by prose."""
    d = _tempfile.mkdtemp(prefix="derate-tvs-bad-")
    p = _brd(d, [("D2", "SMCJ33A (VIN_RAW clamp)", ["VIN", "GND"])],
             rails={"VIN": {"volts": 12.0, "v_work": 36.0, "amps_typ": 1.0}},
             nodes={"GND": {"v_max": 0.0, "basis": "reference"}})
    rc, out = _run_derate(p, d)
    assert rc == 1 and "stands off 33.0" in out, out[-700:]
    d2 = _tempfile.mkdtemp(prefix="derate-tvs-ok-")
    p2 = _brd(d2, [("D2", "SMCJ40A (VIN_RAW clamp)", ["VIN", "GND"])],
              rails={"VIN": {"volts": 12.0, "v_work": 36.0, "amps_typ": 1.0}},
              nodes={"GND": {"v_max": 0.0, "basis": "reference"}})
    rc2, out2 = _run_derate(p2, d2)
    assert rc2 == 0, "the 40 V part on the same 36 V line must pass:\n%s" % out2[-600:]


def t_a_part_the_part_maker_specifies_is_judged_by_that_citation():
    """Board C's e-paper pumps. Their peaks live in a driver inside the panel's glass whose datasheet is not
    published; the panel maker's own driving-circuit note specifies the capacitor instead. Declaring a voltage
    would be inventing one and reporting the net as unknown loses a real comparison, so the citation is the
    comparison and the verdict counts it separately."""
    d = _tempfile.mkdtemp(prefix="derate-vendor-")
    p = _brd(d, [("C30", "1u 25V", ["EPD_VGH", "GND"])],
             nodes={"EPD_VGH": {"v_max": None, "basis": "a charge pump inside the panel",
                                "vendor_reference": "PDI driving-circuit note rev 02: Capacitors 25V 0603"},
                    "GND": {"v_max": 0.0, "basis": "reference"}})
    rc, out = _run_derate(p, d)
    assert rc == 0, out[-600:]
    v = _json.load(open(_os.path.join(d, "out", "derate.verdict.json")))
    assert v["counts"]["by_vendor_reference"] == 1, v["counts"]
    assert any("PDI" in e for e in v["evidence"]), v["evidence"]


def t_a_node_with_neither_a_voltage_nor_a_citation_is_refused_at_declaration():
    """Absence is never a pass, and it is refused where the declaration is written rather than where it is
    read: a node with no number and no citation is a typo, not a design."""
    import importlib, intent
    importlib.reload(intent)
    try:
        intent.node("X", None, "no idea")
    except SystemExit as e:
        assert "no vendor reference" in str(e), e
    else:
        raise AssertionError("a node with no voltage and no citation was accepted")
