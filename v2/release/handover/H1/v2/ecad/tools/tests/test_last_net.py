#!/usr/bin/env python3
"""The last net of a KiCad 9 netlist is read by every netlist tool (R4T-F1, fixed in four more tools on 26 September
2026, MESHSAT-1357).

KiCad 9.0.9 closes the nets section on the last net's own line (`...)))))`). The look-ahead these tools used ended a
net at a newline and the section's closing bracket, which never comes, so the last net of every committed netlist was
dropped: on the six committed netlists at 45bde541 it was an unconnected pin's placeholder each time, which is luck and
not a property. port_protect and check_contracts were fixed by the r4t stream; derate, clock_check, ground_system and
netlist_board here. Each fixture below puts the net that decides the answer LAST, and first proves that the old
look-ahead really does miss it, so the fixture cannot pass for the wrong reason."""
import os, sys, re, json, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)

OLD = r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\n    \(net |\n  \)\n)'


def _k9(d, comps, nets, stem="pcb-zz-last"):
    """A netlist in KiCad 9.0.9's shape: the nets section closes on the last net's own line."""
    os.makedirs(d, exist_ok=True)
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in comps.items())
    body = []
    for i, (name, nodes) in enumerate(nets, 1):
        ns = "\n".join('      (node (ref "%s") (pin "%s") (pintype "passive"))' % (r, p) for r, p in nodes)
        body.append('    (net (code "%d") (name "/%s") (class "Default")\n%s)' % (i, name, ns))
    p = os.path.join(d, stem + ".net")
    open(p, "w").write("(export (version \"E\")\n  (components\n%s  )\n  (nets\n%s)))\n" % (c, "\n".join(body)))
    return p


def _old_misses(p, name):
    got = [m.group(1).lstrip("/") for m in re.finditer(OLD, open(p).read(), re.S)]
    assert name not in got, "the fixture does not reproduce R4T-F1: the old look-ahead reads %s" % name


def t_derate_judges_a_part_on_the_last_net():
    import derate
    d = tempfile.mkdtemp(prefix="last-derate-")
    p = _k9(d, {"C1": "10u 16V X5R", "U1": "LDO"},
            [("GND", [("C1", "2"), ("U1", "2")]), ("+24V", [("C1", "1"), ("U1", "1")])])
    json.dump({"rails": {"+24V": {"volts": 24.0, "amps_typ": 0.1, "amps_peak": 0.1, "source": "U1", "loads": {"C1": 0.0}}}},
              open(os.path.join(d, "pcb-zz-last-intent.json"), "w"))
    _old_misses(p, "+24V")
    r = derate.judge(p)
    assert r["bad"] and "C1" in r["bad"][0], r


def t_clock_check_reads_a_crystal_node_that_is_the_last_net():
    import clock_check
    d = tempfile.mkdtemp(prefix="last-clk-")
    p = _k9(d, {"Y1": "12 MHz", "C1": "15p", "C2": "15p", "U1": "MCU"},
            [("GND", [("C1", "2"), ("C2", "2")]), ("XIN", [("Y1", "1"), ("C1", "1"), ("U1", "20")]),
             ("XOUT", [("Y1", "3"), ("C2", "1"), ("U1", "21")])])
    _old_misses(p, "XOUT")
    rows, bad = clock_check.judge(p)
    assert not bad and rows and rows[0]["nets"] == ["XIN", "XOUT"], (rows, bad)


def t_ground_system_sees_a_second_ground_that_is_the_last_net():
    import ground_system
    d = tempfile.mkdtemp(prefix="last-gnd-")
    p = _k9(d, {"L1": "choke", "U1": "X"},
            [("GND", [("L1", "2"), ("U1", "2")]), ("VIN", [("L1", "1"), ("U1", "1")]), ("GND_V", [("L1", "4")])])
    _old_misses(p, "GND_V")
    r = ground_system.judge(p)
    assert r["grounds"] == ["GND", "GND_V"], r


def t_netlist_board_reads_the_pins_of_the_last_net():
    import netlist_board
    d = tempfile.mkdtemp(prefix="last-nb-")
    p = _k9(d, {"R1": "10k", "U1": "X"}, [("A", [("R1", "1"), ("U1", "1")]), ("B", [("R1", "2"), ("U1", "2")])])
    _old_misses(p, "B")
    nl = netlist_board.read_netlist(p)
    assert nl.get("R1", {}).get("2") == "B" and nl.get("U1", {}).get("2") == "B", nl


def t_no_tool_this_stream_owns_keeps_the_old_look_ahead():
    bad = []
    for f in ("derate.py", "clock_check.py", "ground_system.py", "netlist_board.py", "intent_checks.py",
              "edge_length.py"):
        if r"(?=\n    \(net |\n  \)\n)" in open(os.path.join(TOOLS, f), encoding="utf-8").read(): bad.append(f)
    assert not bad, "still ending a net at a closing bracket KiCad 9 never writes: %s" % bad
