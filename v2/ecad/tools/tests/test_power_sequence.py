#!/usr/bin/env python3
"""What switches each rail, and the deadlock a schematic cannot show (rule PWR-002, 16 September 2026).

PWR-002 asks for a written sequencing statement per board and read "no verification" on four of them. The
statement is now a declaration on each rail in the intent (the part whose enable pin switches it, or
`always_on` with the reason there is no such part), and this checks the declaration against the netlist.

The one thing it DECIDES is the failure that is invisible on a drawing: a rail whose enable is driven only by a
device powered from that same rail cannot start. Everything else it reports.

Deriving the switch instead of declaring it was tried and withdrawn within the hour: the rail's net often
begins several passives away from its switch (board A's +5V_S1 starts at the sense shunt R31, behind it S1_OUT,
behind that the inductor L3, and only then U4), and a walk across two-pin passives reached 28 candidate parts
on that board. A search that answers "one of twenty-eight" is not an answer; the fixtures below hold the
declaration form instead.
"""
import os, sys, json, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import power_sequence as P


def _board(d, comps, nets, rails):
    os.makedirs(os.path.join(d, "out"), exist_ok=True)
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in sorted(comps.items()))
    n = ""
    for i, (name, nodes) in enumerate(sorted(nets.items()), 1):
        body = "".join('      (node (ref "%s") (pin "%s") (pinfunction "%s"))\n' % (r, p, f) for r, p, f in nodes)
        n += '    (net (code %d) (name "/%s")\n%s    )\n' % (i, name, body)
    net = os.path.join(d, "out", "b.net")
    open(net, "w").write("(export (version E)\n  (components\n%s  )\n  (nets\n%s  )\n)\n" % (c, n))
    json.dump({"rails": rails}, open(os.path.join(d, "out", "b-intent.json"), "w"))
    return net


def t_a_rail_whose_enable_hangs_off_itself_is_refused():
    """THE DEFECTIVE FIXTURE. U2 drives the enable of the rail that powers U2: it cannot start, and no DRC, no
    gate and no drawing in this project would have said so."""
    d = tempfile.mkdtemp(prefix="seq-dead-")
    net = _board(d,
                 {"U1": "buck", "U2": "expander", "R1": "10k"},
                 {"VOUT": [("U1", "5", "VOUT"), ("U2", "1", "VDD")],
                  "VIN": [("U1", "3", "VIN")],
                  "BUCK_EN": [("U1", "2", "BUCK_EN"), ("U2", "4", "BUCK_EN")],
                  "GND": [("U1", "4", "GND"), ("U2", "2", "GND")]},
                 {"VOUT": {"volts": 5.0, "source": "U1", "switch": "U1"}})
    r = P.judge(net)
    assert r["deadlocks"], r
    assert "powered from VOUT itself" in r["deadlocks"][0], r["deadlocks"]


def t_the_same_board_with_the_driver_on_another_rail_passes():
    """THE ACCEPTABLE FIXTURE: one net changed, the expander now runs from a rail that is up first."""
    d = tempfile.mkdtemp(prefix="seq-ok-")
    net = _board(d,
                 {"U1": "buck", "U2": "expander", "R1": "10k"},
                 {"VOUT": [("U1", "5", "VOUT")],
                  "VIN": [("U1", "3", "VIN"), ("U2", "1", "VDD")],
                  "BUCK_EN": [("U1", "2", "BUCK_EN"), ("U2", "4", "BUCK_EN")],
                  "GND": [("U1", "4", "GND"), ("U2", "2", "GND")]},
                 {"VOUT": {"volts": 5.0, "source": "U1", "switch": "U1"},
                  "VIN": {"volts": 12.0, "source": "U1", "always_on": True, "always_on_why": "the input"}})
    r = P.judge(net)
    assert not r["deadlocks"] and not r["unresolved"], r


def t_a_rail_with_no_declaration_is_unresolved_and_never_a_pass():
    d = tempfile.mkdtemp(prefix="seq-bare-")
    net = _board(d, {"R1": "shunt"}, {"VOUT": [("R1", "2", "")], "X": [("R1", "1", "")]},
                 {"VOUT": {"volts": 5.0, "source": "R1"}})
    r = P.judge(net)
    assert r["unresolved"] and "declares neither a switch nor" in r["unresolved"][0], r


def t_always_on_needs_a_reason():
    """A declaration without a reason is an assertion, which is the thing this registry refuses everywhere."""
    d = tempfile.mkdtemp(prefix="seq-why-")
    net = _board(d, {"F1": "fuse"}, {"VOUT": [("F1", "2", "")], "X": [("F1", "1", "")]},
                 {"VOUT": {"volts": 14.4, "source": "F1", "always_on": True}})
    r = P.judge(net)
    assert any("no reason" in u for u in r["unresolved"]), r


def t_an_enable_net_may_be_named_where_its_name_is_not_en_shaped():
    """Board P's pack terminal is switched by the gauge through DSG_R, which no pattern over names would find."""
    d = tempfile.mkdtemp(prefix="seq-named-")
    net = _board(d, {"U1": "gauge", "Q2": "fet", "R9": "5k1"},
                 {"PACK_P": [("Q2", "3", "PACK_P")], "DSG_R": [("U1", "28", "DSG_R"), ("R9", "1", "")],
                  "VBAT": [("U1", "26", "VCC")], "GND": [("U1", "9", "GND")]},
                 {"PACK_P": {"volts": 14.4, "source": "Q2", "switch": "U1", "enable_net": "DSG_R"},
                  "VBAT": {"volts": 14.4, "source": "U1", "always_on": True, "always_on_why": "the cells"}})
    r = P.judge(net)
    assert not r["unresolved"], r
    assert any(row.get("enable") == "DSG_R" for row in r["rows"]), r["rows"]


def t_an_indexed_enable_net_is_still_an_enable():
    """SLOT_EN1, SLOT_EN2 and SLOT_EN3 are board A's three slot converters, and the first pattern matched none
    of them because it required EN to be the last characters of the name."""
    assert P.EN.search("SLOT_EN1") and P.EN.search("DEV_EN") and P.EN.search("EN")
    assert not P.EN.search("HS_UVLO") and not P.EN.search("+5V")


def t_a_rail_may_declare_several_sources():
    """Board B's GND is held at zero at four connectors, and the always-on branch joined that list into a
    string and crashed the gate on the one board with 36 rails (16 September 2026)."""
    d = tempfile.mkdtemp(prefix="seq-multi-")
    net = _board(d, {"J1": "vh", "J2": "vh"},
                 {"GND": [("J1", "2", "GND"), ("J2", "2", "GND")]},
                 {"GND": {"volts": 0.0, "source": ["J1", "J2"], "always_on": True,
                          "always_on_why": "the return, which nothing switches"}})
    r = P.judge(net)
    assert not r["unresolved"] and not r["deadlocks"], r
    row = next(x for x in r["rows"] if x["rail"] == "GND")
    assert row["source"] == ["J1", "J2"], row
