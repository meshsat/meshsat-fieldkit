#!/usr/bin/env python3
"""A SEGMENT OF A POWER PATH DECLARED AS A NODE IS COPPER NO POWER RULE LOOKS AT (rules PI-001, PI-002).

Board A had sixteen of them and every one was found BY HAND, by reading a generator: two measured at 4.81 A
and 6.26 A in conductors IPC rates at 0.40, and eight more that turned out to include the whole 45 W USB-C
outlet. `power_path.py` asks the question mechanically from a netlist and the intent beside it, so it runs
where KiCad is not, and it found ZERO on all six boards once board A's own were declared, which is the answer
to "does this exist anywhere else" that reading six generators could not give.

Two fixtures both ways, as the standard requires, and both synthetic so they say exactly one thing each.
"""
import os, sys, json, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import power_path


def _net(nets):
    """A KiCad 9 netlist: the code IS quoted and every node line carries pinfunction and pintype."""
    refs = sorted({r for v in nets.values() for r, _ in v})
    s = "(export (version \"E\")\n  (components\n"
    s += "".join('    (comp (ref "%s") (value "x"))\n' % r for r in refs)
    s += "  )\n  (nets\n"
    for i, (name, nodes) in enumerate(sorted(nets.items()), 1):
        s += '    (net (code "%d") (name "/%s") (class "Default")\n' % (i, name)
        s += "".join('      (node (ref "%s") (pin "%s") (pinfunction "p") (pintype "passive"))\n' % (r, p)
                     for r, p in nodes)
        s += "    )\n"
    return s + "  ))\n"


NETS = {
    "VBUS20": [("R11", "2"), ("R16", "1"), ("U2", "12")],      # the rail between the two shunts
    "FE_OUT": [("Q5", "5"), ("R11", "1")],                     # before the source shunt
    "CH_ACN": [("R16", "2"), ("Q7", "5")],                     # after the load shunt
    "FE_CSF": [("U2", "16"), ("R90", "2")],                    # the controller's sense filter, NOT a segment
    "GND":    [("R90", "1"), ("Q5", "1"), ("Q7", "1"), ("U2", "5")],
    # the controller's own pins, so U2 touches more than three nets as a real twenty-eight pin part does.
    # The threshold is THREE because a pass-through really can have three: a FET is drain, source and gate,
    # and a linear regulator is in, out and ground. The fixture's first version gave U2 exactly three nets
    # and the rule could not tell it from a switch, which is the fixture being wrong and not the rule.
    "FE_SS":   [("U2", "8"), ("R91", "1")],
    "FE_COMP": [("U2", "9"), ("R92", "1")],
    "FE_RT":   [("U2", "6"), ("R93", "1")],
}
RAIL = dict(volts=20.0, amps_typ=6.0, amps_peak=8.0, source="R11", loads={"R16": 6.0, "U2": 0.3})


def _run(intent, nets=NETS):
    with tempfile.TemporaryDirectory() as td:
        n = os.path.join(td, "b.net"); open(n, "w").write(_net(nets))
        i = os.path.join(td, "b-intent.json"); json.dump(intent, open(i, "w"))
        rows = power_path.segments(intent, power_path.parse_netlist(n)[0])
        return sorted(r["node"] for r in rows)


def t_a_segment_declared_as_a_node_is_found_at_both_ends_of_its_rail():
    """DEFECTIVE: the conductors on the far side of the rail's SOURCE and of its LOAD are both segments.

    A walk that knew only loads found `CH_ACN` and missed `FE_OUT`, which is the first version of this file.
    """
    intent = dict(rails={"VBUS20": RAIL},
                  nodes={"FE_OUT": dict(v_max=20.0, v_min=0.0, basis="the stage output"),
                         "CH_ACN": dict(v_max=20.0, v_min=0.0, basis="the charger input")})
    assert _run(intent) == ["CH_ACN", "FE_OUT"], _run(intent)


def t_the_same_conductors_declared_as_rails_are_not_flagged():
    """ACCEPTABLE: board A's own state after 20 September, and it must read clean."""
    seg = dict(volts=20.0, amps_typ=6.0, amps_peak=8.0, source="R11", loads={"Q7": 6.0}, series_of="VBUS20")
    intent = dict(rails={"VBUS20": RAIL, "FE_OUT": seg, "CH_ACN": seg}, nodes={})
    assert _run(intent) == [], _run(intent)


def t_a_controllers_other_pins_are_not_segments_of_its_rail():
    """DEFECTIVE the other way: a rail's loads include its controller, and an IC does not hand its rail
    current to an arbitrary pin. The first version walked out of U2's pin 16 and called the stage's own
    current-sense filter a segment of a 6 A path. The test is how many nets the part touches, not its name."""
    intent = dict(rails={"VBUS20": RAIL},
                  nodes={"FE_CSF": dict(v_max=1.0, v_min=0.0, basis="the filtered current-sense input")})
    assert _run(intent) == [], _run(intent)


def t_a_ground_a_return_and_a_switching_node_are_never_segments():
    """Three exclusions, each a FACT in the declaration rather than a name: a declared zero (a ground, and
    board P's PACK_N return, which cannot be judged against a percentage of its own 50 mV); and a switching
    node, which the intent marks by a negative v_min or by naming what it rides on."""
    nets = dict(NETS); nets["FE_SW2"] = [("R11", "1"), ("Q5", "5")]
    intent = dict(rails={"VBUS20": RAIL},
                  nodes={"GND": dict(v_max=0.0, v_min=0.0, basis="the board's reference"),
                         "FE_SW2": dict(v_max=20.0, v_min=-1.0, basis="the boost-side switching node")})
    assert _run(intent, nets) == [], _run(intent, nets)


def t_a_netlist_it_parsed_nothing_from_is_inconclusive_and_not_a_pass():
    """The first parse matched `(code \\d+)` unquoted against a file that quotes it, read ZERO nets out of a
    413-part netlist and reported a clean answer. A reading taken from nothing is never a pass."""
    src = open(os.path.join(TOOLS, "power_path.py"), encoding="utf-8").read()
    assert "if not nets:" in src and "missing_input=\"a readable netlist\"" in src, \
        "power_path can report a clean answer from a netlist it parsed nothing out of"
    with tempfile.TemporaryDirectory() as td:
        n = os.path.join(td, "empty.net"); open(n, "w").write("(export (version \"E\"))\n")
        assert power_path.parse_netlist(n)[0] == {}
