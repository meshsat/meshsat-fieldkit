#!/usr/bin/env python3
"""Rule PWR-001 judged on the NETLIST (26 September 2026, MESHSAT-1357).

PWR-001 is verified at the schematic phase and its evidence scope is the schematic, and until this day its only reading
came from the BOARD: a reading that could be current only on a layout carrying the netlist, which is the one thing a
board waiting to ENTER layout does not have. intent_checks.rails_on_netlist judges it on the committed netlist and the
intent file beside it, both recorded by sha. These fixtures hold it both ways: what must pass, what must fail, and
that it never needs KiCad."""
import os, sys, json, shutil, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import intent_checks as IC


# THE FIXTURES' SCRATCH DIRECTORIES ARE REMOVED WHEN THE RUN ENDS (integration of 27 September 2026, the fourth
# independent check's hygiene item: every run left about ten directories of 230 KB under /tmp on the shared runner).
import atexit as _atexit
_TMPDIRS = []


def _mkdtemp(prefix):
    d = tempfile.mkdtemp(prefix=prefix)
    _TMPDIRS.append(d)
    return d


_atexit.register(lambda: [shutil.rmtree(d, ignore_errors=True) for d in _TMPDIRS])


def _node(x):
    """(ref, pin, pintype) or (ref, pin, pintype, pinfunction) as KiCad 9 writes the node, the function first."""
    r, p, t = x[:3]
    fn = (' (pinfunction "%s")' % x[3]) if len(x) > 3 and x[3] else ""
    return '      (node (ref "%s") (pin "%s")%s (pintype "%s"))' % (r, p, fn, t)


def _write(d, comps, nets, rails, nodes=None, kicad9=True, stem="pcb-zz-fixture", classes=None, bypass=None,
           clamps=None):
    """A netlist in KiCad 9.0.9's own shape (the nets section closes on the last net's line when kicad9) and its
    intent file beside it. nets: {name: [(ref, pin, pintype[, pinfunction])]}; comps: {ref: value}; classes: {net:
    class}, Default otherwise; bypass: the intent's bypass entries [{cap, part, pin, net}]."""
    os.makedirs(os.path.join(d, "out"), exist_ok=True)
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in sorted(comps.items()))
    items = list(nets.items())
    body = []
    for i, (name, nodes_) in enumerate(items, 1):
        ns = "\n".join(_node(x) for x in nodes_)
        body.append('    (net (code "%d") (name "/%s") (class "%s")\n%s)' % (i, name, (classes or {}).get(name, "Default"),
                                                                            ns))
    if kicad9:
        txt = "(export (version \"E\")\n  (components\n%s  )\n  (nets\n%s))\n" % (c, "\n".join(body) + ")")
    else:
        txt = "(export (version \"E\")\n  (components\n%s  )\n  (nets\n%s\n  )\n)\n" % (c, "\n".join(body))
    p = os.path.join(d, "out", stem + ".net")
    open(p, "w").write(txt)
    json.dump({"rails": rails, "nodes": nodes or {}, "bypass": bypass or [], "pair_classes": {}, "clamps": clamps or {}},
              open(os.path.join(d, "out", stem + "-intent.json"), "w"))
    return p


def _rail(src, loads, amps=1.0):
    return {"volts": 3.3, "amps_typ": amps, "amps_peak": amps, "source": src, "loads": loads}


BASE_COMPS = {"L1": "4.7u", "U1": "buck", "U2": "MCU", "C1": "10u", "F1": "5A", "J1": "IN"}
BASE_NETS = {"+3V3": [("L1", "2", "passive"), ("U2", "1", "power_in"), ("C1", "1", "passive")],
             "SW": [("L1", "1", "passive"), ("U1", "3", "passive")],
             "VIN": [("F1", "2", "passive"), ("U1", "1", "passive")],
             "RAW": [("J1", "1", "passive"), ("F1", "1", "passive")],
             "GND": [("U1", "2", "passive"), ("U2", "2", "passive"), ("C1", "2", "passive"), ("J1", "2", "passive")]}
BASE_RAILS = {"+3V3": _rail("L1", {"U2": 0.5}, 0.5), "VIN": _rail("F1", {"U1": 1.0}, 1.0),
              "RAW": _rail("J1", {"F1": 1.0}, 1.0)}
BASE_NODES = {"SW": {"v_max": 5.0, "v_min": 0.0, "basis": "the buck's switch node"}}


def _judge(**kw):
    d = _mkdtemp("pwr001-")
    args = dict(comps=dict(BASE_COMPS), nets=dict(BASE_NETS), rails=dict(BASE_RAILS), nodes=dict(BASE_NODES))
    args.update(kw)
    p = _write(d, **args)
    return IC.rails_on_netlist(p), p, d


def _fails(r):
    return [t for ok, t in r["checks"] if not ok]


def t_a_netlist_whose_power_nets_are_all_declared_rails_passes():
    r, _p, _d = _judge()
    assert not _fails(r), _fails(r)
    assert r["counts"]["declared_rails"] == r["counts"]["power_nets"] == 3, r["counts"]
    # the switch node behind the buck's inductor carries the rail's current and is declared as a node: reported
    assert any(x.startswith("SW ") for x in r["declared_nodes"]), r["declared_nodes"]
    assert not r["undecided"], r["undecided"]


def t_an_undeclared_power_symbol_net_fails():
    nets = dict(BASE_NETS); nets["+5V"] = [("U2", "3", "passive"), ("C1", "3", "passive")]
    r, _p, _d = _judge(nets=nets)
    assert any("+5V" in t for t in _fails(r)), r["checks"]


def t_an_undeclared_net_carrying_a_supply_pin_fails_whatever_it_is_called():
    """Board B's SIM1_VCC is fed by the modem through the M.2 socket and has no power symbol: the SIM holder's own
    VCC pin types it power_in. The rule's false-positive analysis says a module-supplied rail is still a rail."""
    comps = dict(BASE_COMPS, J2="SIM")
    nets = dict(BASE_NETS); nets["SIM_VCC"] = [("J2", "1", "power_in"), ("C1", "4", "passive")]
    r, _p, _d = _judge(comps=comps, nets=nets)
    assert any("SIM_VCC" in t and "supply pin" in t for t in _fails(r)), r["checks"]


def t_a_conductor_behind_a_declared_rails_fuse_must_be_declared():
    rails = dict(BASE_RAILS); del rails["RAW"]
    r, _p, _d = _judge(rails=rails)
    f = _fails(r)
    assert any("RAW" in t and "series conductor" in t for t in f), f


def t_a_declared_rail_that_is_not_in_the_netlist_fails():
    rails = dict(BASE_RAILS); rails["+1V8"] = _rail("U1", {"U2": 0.1}, 0.1)
    r, _p, _d = _judge(rails=rails)
    assert any("+1V8" in t and "is a net of the netlist" in t for t in _fails(r)), r["checks"]


def t_a_rail_whose_load_is_not_on_it_does_not_say_where_its_current_goes():
    rails = dict(BASE_RAILS); rails["+3V3"] = _rail("L1", {"U9": 0.5}, 0.5)
    r, _p, _d = _judge(rails=rails)
    assert any("+3V3" in t and "U9" in t for t in _fails(r)), r["checks"]
    rails["+3V3"] = _rail("L1", {}, 0.5)
    r, _p, _d = _judge(rails=rails)
    assert any("+3V3" in t and "says nowhere" in t for t in _fails(r)), r["checks"]


def t_the_last_net_of_a_kicad9_netlist_is_judged():
    """R4T-F1: KiCad 9.0.9 closes the nets section on the last net's own line. An undeclared rail placed LAST must
    still be found, in the new shape and in the old one."""
    for k9 in (True, False):
        nets = dict(BASE_NETS); nets["+12V"] = [("U1", "5", "passive"), ("C1", "5", "passive")]   # last
        d = _mkdtemp("pwr001-last-")
        p = _write(d, dict(BASE_COMPS), nets, dict(BASE_RAILS), dict(BASE_NODES), kicad9=k9)
        r = IC.rails_on_netlist(p)
        assert any("+12V" in t for t in _fails(r)), (k9, r["checks"])
        nl, _v = IC.read_netlist(p)
        assert "+12V" in nl and nl["+12V"]["nodes"], (k9, sorted(nl))


def t_an_intent_with_no_rail_fails_closed_and_a_missing_intent_is_inconclusive():
    r, p, d = _judge(rails={})
    assert _fails(r) and "carries at least one rail" in _fails(r)[0], r["checks"]
    os.remove(os.path.join(d, "out", "pcb-zz-fixture-intent.json"))
    r2 = IC.rails_on_netlist(p)
    assert r2["missing_input"] and "intent" in r2["missing_input"], r2
    out = _mkdtemp("pwr001-v-")
    rc = IC.write_rails_verdict(r2, out_dir=out, quiet=True)
    v = json.load(open(os.path.join(out, "intent_rails.verdict.json")))
    assert rc == 3 and v["verdict"] == "INCONCLUSIVE" and v["missing_input"], v


def t_the_verdict_records_the_netlist_and_the_intent_by_sha_and_never_an_absolute_path():
    """A reading records what it judged by content, the netlist by its content identity too (a regenerated copy with
    a new export date binds by it), and a path under a temporary directory would be refused as a fixture's."""
    r, p, _d = _judge()
    out = _mkdtemp("pwr001-v-")
    rc = IC.write_rails_verdict(r, out_dir=out, quiet=True, board="zz")
    v = json.load(open(os.path.join(out, "intent_rails.verdict.json")))
    assert rc == 0 and v["verdict"] == "PASS", v
    net, it = v["inputs"]["netlist"], v["inputs"]["intent"]
    assert net["path"].endswith(".net") and len(net["sha256_16"]) == 16, net
    assert net.get("content16") and len(net["content16"]) == 16, net
    assert it["sha256_16"] and it["path"].endswith("-intent.json"), it
    for x in (net["path"], it["path"]):
        assert not x.startswith("/"), "a recorded path is absolute: %s" % x
    assert v["rules"] == ["PWR-001"] and v["writer"]["file"], v


def t_the_netlist_mode_needs_no_kicad_and_the_board_mode_says_so_when_it_is_missing():
    import importlib
    m = importlib.reload(IC)
    assert hasattr(m, "rails_on_netlist")
    if m.pcbnew is None:
        try:
            m.run(None, lambda ok, t: None, "x.kicad_pcb")
        except SystemExit as e:
            assert "--netlist" in str(e), e
        else:
            raise AssertionError("the board checks ran without pcbnew")


def t_the_board_run_writes_intent_rails_from_the_netlist_beside_the_board():
    """Where the netlist a board was placed from sits beside it, PWR-001's reading is the netlist's, so a run on a
    layout that is not the candidate's can never stand in front of it; the board's own rail lines fall to
    intent_other, which the finish blocks on."""
    src = open(os.path.join(TOOLS, "intent_checks.py"), encoding="utf-8").read()
    i = src.index('if __name__ == "__main__":')
    main = src[i:]
    assert "_nl = rails_on_netlist(_net)" in main, "the board run does not judge the netlist beside the board"
    assert "write_rails_verdict(_nl" in main, "the board run does not write intent_rails from the netlist"
    j = main.index('if name == "intent_rails" and _nl is not None:')
    assert "continue" in main[j:j + 400], "the board's rail lines are still claimed by intent_rails"


def t_a_load_current_that_is_not_a_number_is_refused_and_does_not_crash_the_reading():
    rails = dict(BASE_RAILS); rails["+3V3"] = _rail("L1", {"U2": "half an amp"}, 0.5)
    r, _p, _d = _judge(rails=rails)
    assert any("+3V3" in t and "not a non-negative number" in t for t in _fails(r)), r["checks"]


# ---- second pass (26 September 2026): the independent check found the first reading PASSED boards A, C, D, E and P
# while their own intent files decoupled supplies nobody declared. The generators type nearly every supply pin passive
# (A 32 of 34, C 17 of 19, D 16 of 17, P 3 of 3), and a switched supply behind a FET was never followed. These fixtures
# hold the corrected criteria both ways, on the shapes the check named: a passive-typed VDD pin, a FET-switched rail.

def _with(extra_nets, extra_comps=None, rails=None, nodes=None, classes=None, bypass=None, clamps=None):
    comps = dict(BASE_COMPS, **(extra_comps or {}))
    nets = dict(BASE_NETS); nets.update(extra_nets)
    return _judge(comps=comps, nets=nets, rails=rails if rails is not None else dict(BASE_RAILS),
                  nodes=nodes if nodes is not None else dict(BASE_NODES), classes=classes, bypass=bypass, clamps=clamps)


# a part's own core supply, as board C's RP2040 makes it: VREG_VOUT into its own DVDD pins, typed passive, and a
# capacitor from it to ground
DVDD = {"C_DVDD": [("U2", "45", "passive", "VREG_VOUT"), ("U2", "23", "passive", "DVDD"), ("C9", "1", "passive")],
        "GND2": [("C9", "2", "passive")]}


def _dvdd(**kw):
    nets = {"C_DVDD": DVDD["C_DVDD"]}
    # the decoupling capacitor's other pin is on the fixture's ground net
    base = dict(BASE_NETS); base["GND"] = BASE_NETS["GND"] + [("C9", "2", "passive")]
    comps = dict(BASE_COMPS, C9="1u")
    nets_all = dict(base); nets_all.update(nets); nets_all.update(kw.pop("extra", {}))
    return _judge(comps=dict(comps, **kw.pop("comps", {})), nets=nets_all, **kw)


def t_a_passive_typed_supply_pin_decoupled_to_ground_is_a_power_net_and_must_be_declared():
    r, _p, _d = _dvdd()
    f = _fails(r)
    assert any("C_DVDD" in t and "supply pin by name" in t and "C9" in t for t in f), r["checks"]
    # declared as a rail with its source and load on it: passes
    rails = dict(BASE_RAILS); rails["C_DVDD"] = _rail("U2", {"U2": 0.02}, 0.02)
    r2, _p, _d = _dvdd(rails=rails)
    assert not _fails(r2), _fails(r2)
    # declared as a node (the part's own regulator output, stated with its voltage): reported, not refused
    nodes = dict(BASE_NODES); nodes["C_DVDD"] = {"v_max": 1.1, "v_min": 0.0, "basis": "the RP2040's core regulator"}
    r3, _p, _d = _dvdd(nodes=nodes)
    assert not _fails(r3), _fails(r3)
    assert any(x.startswith("C_DVDD ") for x in r3["declared_nodes"]), r3["declared_nodes"]


def t_a_supply_pin_the_intents_bypass_list_decouples_is_a_power_net_without_a_capacitor_in_the_netlist():
    nets = {"PCM_VDD": [("U2", "5", "passive", "VDD"), ("R9", "2", "passive")], "X9": [("R9", "1", "passive")]}
    r, _p, _d = _with(nets, {"R9": "1.5k"}, bypass=[{"cap": "C19", "part": "U2", "pin": "5", "net": "PCM_VDD"}])
    assert any("PCM_VDD" in t and "bypass list" in t for t in _fails(r)), r["checks"]


def t_supply_pins_of_two_parts_on_one_net_make_it_a_power_net():
    nets = {"VBAT": [("U2", "76", "passive", "VBAT"), ("U3", "6", "passive", "VBAT"), ("BT1", "1", "passive", "+")]}
    r, _p, _d = _with(nets, {"U3": "RTC", "BT1": "CR2032"})
    assert any("VBAT" in t and "2 parts" in t for t in _fails(r)), r["checks"]


def t_a_node_that_carries_supply_pins_of_two_parts_is_a_rail_and_is_refused_as_a_node():
    nets = {"VBAT": [("U2", "76", "passive", "VBAT"), ("U3", "6", "passive", "VBAT")]}
    nodes = dict(BASE_NODES); nodes["VBAT"] = {"v_max": 3.3, "v_min": 0.0, "basis": "coin cell"}
    r, _p, _d = _with(nets, {"U3": "RTC"}, nodes=nodes)
    assert any(t.startswith("node VBAT supplies one part at most") for t in _fails(r)), r["checks"]


def t_a_supply_named_pin_nothing_corroborates_is_undecided_and_holds_the_reading_inconclusive():
    """A USB hub's VBUS detect on its divider (board B's TUSB8041 USB_VBUS: 0 to 1.155 V through 90.9k and 10k) and a
    codec's VIN that is a microphone input (board D's PCM2912A) name a supply and are none: neither refused nor
    passed. Declaring the net as a node settles it."""
    nets = {"HUB_VBUS": [("U2", "48", "passive", "USB_VBUS"), ("R7", "2", "passive"), ("R8", "1", "passive")],
            "RDIV": [("R7", "1", "passive")], "GND": BASE_NETS["GND"] + [("R8", "2", "passive")]}
    r, _p, _d = _with(nets, {"R7": "90.9k", "R8": "10k"})
    assert not _fails(r), _fails(r)
    assert "HUB_VBUS" in r["undecided"], r["undecided"]
    out = _mkdtemp("pwr001-v-")
    rc = IC.write_rails_verdict(r, out_dir=out, quiet=True)
    v = json.load(open(os.path.join(out, "intent_rails.verdict.json")))
    assert v["verdict"] == "INCONCLUSIVE" and rc == 3, v
    assert any("HUB_VBUS" in e and "undecided" in e for e in v["evidence"]), v["evidence"]
    nodes = dict(BASE_NODES); nodes["HUB_VBUS"] = {"v_max": 1.155, "v_min": 0.0, "basis": "VBUS detect divider"}
    r2, _p, _d = _with(nets, {"R7": "90.9k", "R8": "10k"}, nodes=nodes)
    assert not r2["undecided"] and not _fails(r2), (r2["undecided"], _fails(r2))


def t_a_net_the_bypass_list_decouples_at_a_pin_that_names_no_supply_is_undecided():
    """Board A's ISNS+ filters: the intent's bypass list names the capacitor, and the pin is a current-sense input."""
    nets = {"FE_ISNS_P": [("U1", "14", "passive", "FE_ISNS_P"), ("R9", "2", "passive")], "X9": [("R9", "1", "passive")]}
    r, _p, _d = _with(nets, {"R9": "100R"}, bypass=[{"cap": "C128", "part": "U1", "pin": "14", "net": "FE_ISNS_P"}])
    assert not _fails(r), _fails(r)
    assert "FE_ISNS_P" in r["undecided"] and "bypass" in r["undecided"]["FE_ISNS_P"], r["undecided"]
    # third pass: TI's pin table makes the LM5176's pin 14 the current-sense amplifier's input, which settles it
    r2, _p, _d = _with(nets, {"R9": "100R", "U1": "LM5176PWPR buck-boost controller"},
                       bypass=[{"cap": "C128", "part": "U1", "pin": "14", "net": "FE_ISNS_P"}])
    assert not r2["undecided"] and "sense" in r2["settled"].get("FE_ISNS_P", ""), (r2["undecided"], r2["settled"])


def t_a_net_of_a_power_class_in_the_netlist_is_a_power_net_and_the_hv_clearance_class_is_undecided():
    nets = {"SW_P": [("U1", "7", "passive"), ("U2", "7", "passive")], "POE_GATE": [("U1", "8", "passive")]}
    r, _p, _d = _with(nets, classes={"SW_P": "PWR", "POE_GATE": "HV"})
    assert any("SW_P" in t and "power class PWR" in t for t in _fails(r)), r["checks"]
    assert "POE_GATE" in r["undecided"] and not any("POE_GATE" in t for t in _fails(r)), (r["undecided"], _fails(r))


def t_the_class_split_covers_every_power_class_signalnets_knows():
    import signalnets
    assert IC.CLASS_POWER | IC.CLASS_UNDECIDED | IC.CLASS_GROUND == frozenset(signalnets.POWER_CLASSES), \
        "a power class was added to signalnets without a place in PWR-001's split"
    assert not (IC.CLASS_POWER & IC.CLASS_UNDECIDED) and not (IC.CLASS_POWER & IC.CLASS_GROUND)


# the FET-switched rail of board C: +3V3 names the P-FET Q5 as a load, source on the rail, gate on an enable line,
# drain on the e-paper's supply
FET = {"EPD_VCC": [("Q5", "3", "passive", "D"), ("U3", "1", "passive")],
       "EPD_PWR_n": [("Q5", "1", "input", "G"), ("U2", "9", "passive")]}


def _fet(rails_extra=None, extra_nets=None, **kw):
    nets = dict(FET); nets.update(extra_nets or {})
    nets["+3V3"] = BASE_NETS["+3V3"] + [("Q5", "2", "passive", "S")]
    rails = dict(BASE_RAILS); rails["+3V3"] = _rail("L1", {"U2": 0.5, "Q5": 0.05}, 0.55)
    rails.update(rails_extra or {})
    return _with(nets, {"Q5": "AO3401A", "U3": "e-paper"}, rails=rails, **kw)


def t_a_declared_switch_load_is_followed_to_its_drain_and_the_switched_supply_must_be_declared():
    r, _p, _d = _fet()
    assert any("EPD_VCC" in t and "switch output" in t and "Q5" in t for t in _fails(r)), r["checks"]
    assert not any("EPD_PWR_n" in t for t in _fails(r)), "the gate line was taken for the channel"
    r2, _p, _d = _fet(rails_extra={"EPD_VCC": _rail("Q5", {"U3": 0.05}, 0.05)})
    assert not _fails(r2), _fails(r2)


def t_a_rail_on_a_transistors_gate_passes_no_current_through_it():
    """Board D's level shifters: +3V3_D8 is declared with the 2N7002 gates as loads; their channels are signals."""
    nets = {"X_PTT": [("Q4", "3", "passive", "D")], "PTT": [("Q4", "2", "passive", "S")]}
    nets["+3V3"] = BASE_NETS["+3V3"] + [("Q4", "1", "input", "G")]
    rails = dict(BASE_RAILS); rails["+3V3"] = _rail("L1", {"U2": 0.5, "Q4": 0.001}, 0.5)
    r, _p, _d = _with(nets, {"Q4": "2N7002"}, rails=rails)
    assert not _fails(r), _fails(r)


def t_an_undeclared_switched_supply_passes_the_current_on_through_its_next_switch():
    """Board C's LED rail: the rail's current reaches LED_RAIL_SW through a two-terminal switch, and the high-side FET
    Q1 on it passes it to LED_RAIL. Both are power nets, and both are named."""
    nets = {"LED_RAIL_SW": [("SW1", "1", "passive"), ("Q1", "2", "passive", "S")],
            "LED_RAIL": [("Q1", "3", "passive", "D"), ("R21", "1", "passive")],
            "Q1_G": [("Q1", "1", "input", "G"), ("R15", "2", "passive")], "RX": [("R21", "2", "passive")],
            "RY": [("R15", "1", "passive")]}
    nets["+3V3"] = BASE_NETS["+3V3"] + [("SW1", "2", "passive")]
    rails = dict(BASE_RAILS); rails["+3V3"] = _rail("L1", {"U2": 0.5, "SW1": 0.35}, 0.85)
    r, _p, _d = _with(nets, {"SW1": "toggle", "Q1": "AO3401A", "R21": "300R", "R15": "10k"}, rails=rails)
    f = _fails(r)
    assert any("LED_RAIL_SW" in t and "series conductor" in t for t in f), f
    assert any(t.startswith("power net LED_RAIL is") and "switch output" in t for t in f), f
    assert not any("Q1_G" in t for t in f), "the gate line was taken for the channel"


def t_a_switch_whose_pin_roles_nothing_reads_is_answered_only_by_a_declared_rail_that_names_it():
    """A power FET whose pin functions are net names and whose part number has no held row: nothing says which of its
    other nets is the channel. None declared: refused. The gate line declared as a node: still refused, because a node
    names no source and a gate line is one of those nets (TSN-D16, the second independent check of 26 September). The
    channel declared as a rail that names the switch as its source: answered."""
    nets = {"DSG_G": [("Q2", "4", "passive", "DSG_G"), ("U2", "12", "passive")],
            "SWX": [("Q2", "5", "passive", "SWX"), ("U1", "12", "passive")]}
    nets["+3V3"] = BASE_NETS["+3V3"] + [("Q2", "1", "passive", "+3V3"), ("Q2", "2", "passive", "+3V3")]
    rails = dict(BASE_RAILS); rails["+3V3"] = _rail("L1", {"U2": 0.5, "Q2": 1.0}, 1.5)
    comps = {"Q2": "XQ9999 30 V N-FET"}
    r, _p, _d = _with(nets, comps, rails=rails)
    assert any("Q2" in t and "gate or base role" in t for t in _fails(r)), r["checks"]
    nodes = dict(BASE_NODES); nodes["DSG_G"] = {"v_max": 12.0, "v_min": 0.0, "basis": "the discharge FET's gate"}
    r2, _p, _d = _with(nets, comps, rails=rails, nodes=nodes)
    assert any("Q2" in t and "gate or base role" in t for t in _fails(r2)), "a gate line declared as a node " \
        "answered the switch: %s" % _fails(r2)
    rails3 = dict(rails); rails3["SWX"] = _rail("Q2", {"U1": 1.0}, 1.0)
    r3, _p, _d = _with(nets, comps, rails=rails3)
    assert not any("gate or base role" in t for t in _fails(r3)), _fails(r3)


def t_a_power_fet_whose_pins_are_named_after_their_nets_is_read_from_its_held_datasheet():
    """Board P's CSD17570Q5B: the symbol names each pin after its net, and TI's SON 5x6 drawing (1 to 3 source, 4 gate,
    5 to 8 drain) reads the roles, so the rail's current is followed to the drain and the gate line is not taken for
    the channel."""
    nets = {"DSG_G": [("Q2", "4", "passive", "DSG_G"), ("U2", "12", "passive")],
            "SWX": [("Q2", "5", "passive", "SWX"), ("U1", "12", "passive")]}
    nets["+3V3"] = BASE_NETS["+3V3"] + [("Q2", "1", "passive", "+3V3"), ("Q2", "2", "passive", "+3V3")]
    rails = dict(BASE_RAILS); rails["+3V3"] = _rail("L1", {"U2": 0.5, "Q2": 1.0}, 1.5)
    r, _p, _d = _with(nets, {"Q2": "CSD17570Q5B 30 V N-FET, discharge switch"}, rails=rails)
    f = _fails(r)
    assert not any("gate or base role" in t for t in f), f
    assert any(t.startswith("power net SWX is") and "switch output" in t for t in f), f
    assert not any("DSG_G" in t for t in f), "the gate line was taken for the channel"


def t_the_supply_token_grammar():
    yes = ("VDD", "DVDD", "IOVDD", "HPVDD", "VCCA", "VDDIO", "VDD_RF", "VBUS", "USB_VBUS", "VIN", "VREG_VIN", "VCAP",
           "BAT", "VBAT", "3V3", "3.3V", "E6_DVDD", "VCC", "HPVSS", "VSS", "AVSS", "VSSA", "VEE")
    no = ("VREF", "VCOM", "VGH", "VSYNC", "PBI", "SDA", "GPIO25", "D", "S", "G", "VOUT", "ISNS_P", "PTCEN", "Pin_3",
          "", None, "V_BCKP", "UIM-PWR", "VDH")
    assert all(IC._supply_named(x) for x in yes), [x for x in yes if not IC._supply_named(x)]
    assert not any(IC._supply_named(x) for x in no), [x for x in no if IC._supply_named(x)]


# ---- third pass (26 September 2026): the second independent check found two real supplies no count and no undecided
# list held (board D's AMP_HPVSS on the TPA6132A2's HPVSS pin, board E's TRK_LDO33 on the LT8705A's "Pin_4"), and the
# general cause: kinds (1) to (5) admitted a net only through a name inside a grammar, and on these netlists a pin's name
# is the maker's (HPVSS), the net's own (board A's TPS25740 pin 1 reads "PD_VTX") or a number ("Pin_4"). Pass (6) fails
# closed: every net carrying the mark of a supply is counted, declared, settled by what is read, or undecided. Each
# fixture holds one rule of it both ways.

def _gnd_cap(ref):
    """The ground pin of a two-pin capacitor, added to the fixture's ground net."""
    return BASE_NETS["GND"] + [(ref, "2", "passive")]


def _verdict(r):
    out = _mkdtemp("pwr001-v-")
    IC.write_rails_verdict(r, out_dir=out, quiet=True)
    return json.load(open(os.path.join(out, "intent_rails.verdict.json")))


def _declared(v=5.0, why="fixture"):
    """A node declaration: the net's voltage and why."""
    return {"v_max": v, "v_min": min(0.0, v), "basis": why}


def t_a_negative_supply_pin_named_in_the_vss_family_is_a_power_net_off_ground_and_not_on_it():
    """The TPA6132A2's HPVSS: the charge pump's negative output, decoupled to ground. On a net that is not ground a
    VSS or VEE pin names a supply; on ground it is the part's ground and nothing is asked."""
    nets = {"AMP_HPVSS": [("U7", "8", "passive", "HPVSS"), ("C29", "1", "passive")], "GND": _gnd_cap("C29")}
    comps = {"U7": "XAMP9 headphone amplifier", "C29": "1u"}
    r, _p, _d = _with(nets, comps)
    assert any(t.startswith("power net AMP_HPVSS is") and "HPVSS" in t for t in _fails(r)), r["checks"]
    r2, _p, _d = _with(nets, comps, nodes=dict(BASE_NODES, AMP_HPVSS=_declared(-1.8, "the charge pump's output")))
    assert not _fails(r2) and not r2["undecided"], (_fails(r2), r2["undecided"])
    on_ground = {"GND": _gnd_cap("C29") + [("U7", "10", "passive", "VSS")],
                 "AMP_OUT": [("U7", "5", "passive", "OUTR"), ("C29", "1", "passive")]}
    r3, _p, _d = _with(on_ground, comps)
    assert not any("GND" in t for t in _fails(r3)), _fails(r3)


def t_a_pin_known_only_by_its_number_is_read_from_the_held_datasheet_and_unread_it_is_undecided():
    """Board E's LT8705A: every pin reads "Pin_N". Its held datasheet makes pin 4 the 3.3 V regulator output, so the
    net is a power net. The same net on a part no row reads is undecided: the reading never passes over it."""
    nets = {"TRK_LDO33": [("U5", "4", "passive", "Pin_4"), ("C20", "1", "passive")], "GND": _gnd_cap("C20")}
    r, _p, _d = _with(nets, {"U5": "LT8705A buck-boost controller, 38-lead QFN", "C20": "1u"})
    assert any(t.startswith("power net TRK_LDO33 is") and "held datasheet" in t and "LDO33" in t for t in _fails(r)), \
        r["checks"]
    assert r["inputs"].get("document_1", {}).get("path") == "v2/vendor/power/lt8705a.pdf", r["inputs"]
    r2, _p, _d = _with(nets, {"U5": "XQ8705 buck-boost controller", "C20": "1u"})
    assert not _fails(r2) and "TRK_LDO33" in r2["undecided"], (_fails(r2), r2["undecided"])
    assert _verdict(r2)["verdict"] == "INCONCLUSIVE"


def t_a_pin_named_after_its_net_is_read_from_the_held_datasheet_and_unread_it_is_undecided():
    """Board A's TPS25740A: the symbol names pin 1 "PD_VTX", after its net. TI's pin table makes it the transmit
    driver's supply bypass, so the net is a power net. Echoed by a part no row reads, it is undecided."""
    nets = {"PD_VTX": [("U18", "1", "passive", "PD_VTX"), ("C93", "1", "passive")], "GND": _gnd_cap("C93")}
    r, _p, _d = _with(nets, {"U18": "TPS25740ARGER USB-C PD source controller", "C93": "100n"})
    assert any(t.startswith("power net PD_VTX is") and "VTX" in t for t in _fails(r)), r["checks"]
    r2, _p, _d = _with(nets, {"U18": "XPD2574 USB-C PD source controller", "C93": "100n"})
    assert "PD_VTX" in r2["undecided"] and not _fails(r2), (r2["undecided"], _fails(r2))


def t_a_held_role_that_supplies_nothing_settles_a_marked_net_and_no_row_leaves_it_undecided():
    """The LM5176's soft-start pin with its capacitor: marked (M1), settled by TI's pin table (SS, a timing pin), so
    the reading passes with the net in the census as settled; on a part no row reads it holds the reading."""
    nets = {"FE_SS": [("U3", "8", "passive", "FE_SS"), ("C7", "1", "passive")], "GND": _gnd_cap("C7")}
    r, _p, _d = _with(nets, {"U3": "LM5176PWPR buck-boost controller", "C7": "47n"})
    assert not _fails(r) and not r["undecided"], (_fails(r), r["undecided"])
    assert "FE_SS" in r["settled"] and "timing" in r["settled"]["FE_SS"], r["settled"]
    assert r["census"]["FE_SS"] == "settled" and _verdict(r)["verdict"] == "PASS"
    r2, _p, _d = _with(nets, {"U3": "XLM5176 buck-boost controller", "C7": "47n"})
    assert "FE_SS" in r2["undecided"] and _verdict(r2)["verdict"] == "INCONCLUSIVE", r2["undecided"]


def t_an_oscillator_net_and_a_net_of_resistors_and_capacitors_alone_are_settled():
    nets = {"XIN": [("Y1", "1", "passive"), ("U2", "20", "passive", "XIN"), ("C5", "1", "passive")],
            "COMPC": [("R9", "2", "passive"), ("C6", "1", "passive")], "COMP": [("R9", "1", "passive")],
            "GND": BASE_NETS["GND"] + [("C5", "2", "passive"), ("C6", "2", "passive")]}
    r, _p, _d = _with(nets, {"Y1": "12 MHz", "C5": "15p", "C6": "10n", "R9": "4.7k"})
    assert not r["undecided"], r["undecided"]
    assert "crystal" in r["settled"]["XIN"] and "only resistors" in r["settled"]["COMPC"], r["settled"]
    # the crystal is what settles XIN: without it the unread XIN pin leaves the net undecided
    nets2 = dict(nets); nets2["XIN"] = [("U2", "20", "passive", "XIN"), ("C5", "1", "passive")]
    r2, _p, _d = _with(nets2, {"C5": "15p", "C6": "10n", "R9": "4.7k"})
    assert "XIN" in r2["undecided"], r2["undecided"]


def t_a_link_resistor_to_a_power_net_marks_a_net_with_no_integrated_circuit_and_a_pull_up_does_not():
    """Board B's SIM2_VCC: the modem's second SIM supply, through the 0R eSIM link R272 to a declared supply and out
    of an M.2 pin the socket names GPIO_4. No capacitor, no name: only the link marks it. A 10k pull-up to a
    connector pin marks nothing."""
    nets = {"SIM2_VCC": [("J2", "48", "bidirectional", "GPIO_4"), ("R272", "1", "passive")],
            "SIMC2_VCC": [("R272", "2", "passive"), ("J3", "1", "power_in", "VCC")]}
    # SIMC2_VCC is a power net by its typed pin and, as on board B today, not declared (a declared rail naming R272
    # as its source would carry its current on to SIM2_VCC by kind (5) instead)
    r, _p, _d = _with(nets, {"J2": "M.2 socket", "J3": "SIM holder", "R272": "0R (eSIM option link)"})
    assert "SIM2_VCC" in r["undecided"] and "R272" in r["undecided"]["SIM2_VCC"], r["undecided"]
    r2, _p, _d = _with(nets, {"J2": "M.2 socket", "J3": "SIM holder", "R272": "10k"})
    assert "SIM2_VCC" not in r2["undecided"] and r2["census"]["SIM2_VCC"] == "unmarked", r2["census"]["SIM2_VCC"]


def t_a_mark_travels_along_a_dc_link_from_an_undecided_net():
    """Board B's antenna feed: VDD_RF through the 10R R23 to GNSS_BIAS, through L3 to GNSS_ANT and the antenna socket.
    GNSS_BIAS is marked by the link; GNSS_ANT only through L3 from GNSS_BIAS, which is undecided, not counted."""
    nets = {"GNSS_BIAS": [("R23", "2", "passive"), ("L3", "1", "passive")],
            "GNSS_ANT": [("L3", "2", "passive"), ("J4", "1", "passive"), ("C42", "1", "passive")],
            "GNSS_RF_IN": [("C42", "2", "passive"), ("U4", "11", "passive", "RF_IN")]}
    nets["+3V3"] = BASE_NETS["+3V3"] + [("R23", "1", "passive")]
    r, _p, _d = _with(nets, {"R23": "10R", "L3": "27nH", "J4": "U.FL", "C42": "47p", "U4": "GNSS module"})
    assert "GNSS_BIAS" in r["undecided"], r["undecided"]
    assert "GNSS_ANT" in r["undecided"] and "undecided net GNSS_BIAS" in r["undecided"]["GNSS_ANT"], r["undecided"]
    # the DC block: a capacitor to an undecided net does not carry the mark on
    assert "GNSS_RF_IN" not in r["undecided"], r["undecided"]


def t_a_bootstrap_on_a_switch_node_and_a_charge_pumps_flying_nodes_are_marked():
    """M2: a capacitor to a power net (the bootstrap across the buck's switch node) and a capacitor across two pins of
    the one part on both nets (a charge pump's flying capacitor). With the part's held row they are power nets; with
    no row they are undecided."""
    nets = {"BST": [("U1", "6", "passive", "BST"), ("C8", "1", "passive")],
            "SW": BASE_NETS["SW"] + [("C8", "2", "passive")],
            "CPP": [("U9", "11", "passive", "CPP"), ("C30", "1", "passive")],
            "CPN": [("U9", "9", "passive", "CPN"), ("C30", "2", "passive")]}
    r, _p, _d = _with(nets, {"C8": "100n", "C30": "1u", "U9": "XAMP charge pump", "U1": "XBUCK"})
    assert {"BST", "CPP", "CPN"} <= set(r["undecided"]), r["undecided"]
    r2, _p, _d = _with(nets, {"C8": "100n", "C30": "1u", "U9": "TI TPA6132A2 headphone amplifier",
                              "U1": "TPS62933DRLR 3 A buck"})
    f = _fails(r2)
    for n in ("BST", "CPP", "CPN"):
        assert any(t.startswith("power net %s is" % n) and "held datasheet" in t for t in f), (n, f)


def t_a_clamp_the_intent_declares_marks_nothing_and_an_undeclared_diode_to_a_rail_does():
    nets = {"SIG": [("D5", "2", "passive", "A"), ("J5", "1", "passive"), ("U2", "30", "passive", "GPIO1")]}
    nets["+3V3"] = BASE_NETS["+3V3"] + [("D5", "1", "passive", "K")]
    comps = {"D5": "BAT54 clamp", "J5": "header"}
    r, _p, _d = _with(nets, comps)
    assert "SIG" in r["undecided"] and "D5" in r["undecided"]["SIG"], r["undecided"]
    r2, _p, _d = _with(nets, comps, clamps={"D5": {"direction": "uni", "protected": "SIG", "return": "+3V3"}})
    assert "SIG" not in r2["undecided"], r2["undecided"]


def t_a_switch_to_ground_and_an_open_drain_sink_settle_and_the_same_to_a_rail_does_not():
    """Board C's SOS toggle: the switch pulls a debounced input to ground, and the RP2040's GPIO28 (held pin table)
    reads it. Board B's hub reset: a 2N7002 whose source is on ground sinks the TUSB8041's GRSTz. The same switch or
    transistor with its other side on a rail passes that rail onto the net, and nothing settles it."""
    nets = {"SOS_SW": [("SW_SOS", "1", "passive", "Pin_1"), ("R9", "1", "passive"), ("C19", "1", "passive"),
                       ("U3", "40", "passive", "GPIO28_A2")],
            "RST_n": [("Q3", "3", "passive", "D"), ("U102", "50", "passive", "GRSTz"), ("C163", "1", "passive"),
                      ("R141", "1", "passive")],
            "HUB_VOTE": [("Q3", "1", "input", "G")]}
    nets["GND"] = BASE_NETS["GND"] + [("SW_SOS", "2", "passive"), ("C19", "2", "passive"), ("C163", "2", "passive"),
                                      ("Q3", "2", "passive", "S")]
    nets["+3V3"] = BASE_NETS["+3V3"] + [("R9", "2", "passive"), ("R141", "2", "passive")]
    comps = {"SW_SOS": "SOS toggle", "R9": "10k", "C19": "100n", "U3": "RP2040 panel controller", "Q3": "2N7002",
             "U102": "TI TUSB8041IRGCR four-port USB 3.0 hub", "C163": "1u", "R141": "10k"}
    r, _p, _d = _with(nets, comps)
    assert not r["undecided"], r["undecided"]
    assert "switch to ground" in r["settled"]["SOS_SW"] and "sinks to ground" in r["settled"]["RST_n"], r["settled"]
    nets2 = dict(nets)
    nets2["GND"] = BASE_NETS["GND"] + [("C19", "2", "passive"), ("C163", "2", "passive")]
    nets2["+3V3"] = nets["+3V3"] + [("SW_SOS", "2", "passive"), ("Q3", "2", "passive", "S")]
    r2, _p, _d = _with(nets2, comps)
    assert {"SOS_SW", "RST_n"} <= set(r2["undecided"]), r2["undecided"]


def t_a_part_number_is_read_where_the_value_begins_and_not_in_its_description():
    """Board P's PTC thermistor names the gauge it serves in its value field ("the BQ4050 PTC input"): it is not a
    BQ4050, and its pin 1 is not the gauge's PBI supply."""
    nets = {"PTC": [("RT1", "1", "passive"), ("C13", "1", "passive"), ("U5", "23", "passive", "PTC")],
            "GND": _gnd_cap("C13") + [("RT1", "2", "passive")]}
    r, _p, _d = _with(nets, {"RT1": "PRF15BB103 chip PTC 10k: the BQ4050 PTC input", "C13": "100n",
                             "U5": "BQ4050RSMR: SMBus gas gauge"})
    assert not any("PTC" in t for t in _fails(r)), _fails(r)
    assert "PTC" in r["settled"] and "U5.23 PTC" in r["settled"]["PTC"], r["settled"]


def t_the_census_gives_every_net_exactly_one_disposition_and_the_verdict_counts_them():
    nets = {"FE_SS": [("U3", "8", "passive", "FE_SS"), ("C7", "1", "passive")], "GND": _gnd_cap("C7"),
            "SDA": [("U2", "7", "bidirectional", "SDA"), ("U3", "1", "passive", "FE_EN")],
            "MYSTERY": [("U4", "3", "passive", "Pin_3"), ("C8", "1", "passive")]}
    nets["GND"] = nets["GND"] + [("C8", "2", "passive")]
    r, _p, _d = _with(nets, {"U3": "LM5176PWPR", "C7": "47n", "U4": "XYZ", "C8": "1u"})
    nl, _v = IC.read_netlist(_p)
    assert set(r["census"]) == set(nl), set(nl) ^ set(r["census"])
    assert r["census"]["FE_SS"] == "settled" and r["census"]["MYSTERY"] == "undecided"
    assert r["census"]["SDA"] == "unmarked" and r["census"]["SW"] == "declared node" and r["census"]["GND"] == "ground"
    assert r["census"]["+3V3"] == "counted", r["census"]
    v = _verdict(r)
    assert v["counts"]["settled"] == 1 and v["counts"]["census_nets"] == len(nl), v["counts"]
    assert v["evidence"][0].startswith("census of the %d nets" % len(nl)), v["evidence"]
    assert any(e.startswith("settled, it supplies nothing: FE_SS") for e in v["evidence"]), v["evidence"]
    assert any(e.startswith("undecided, named and not counted (1): MYSTERY") for e in v["evidence"]), v["evidence"]


def t_the_census_and_every_undecided_name_survive_the_evidence_cap():
    """verdict.write keeps 50 evidence lines. A board with more refusals and undecided nets than that (board B names 28
    and 22) still carries the census and every undecided net's name in its reading."""
    extra, gnd = {}, list(BASE_NETS["GND"])
    comps = {}
    for i in range(60):
        extra["P%02d" % i] = [("U%d" % (10 + i), "1", "passive", "Pin_1"), ("C%d" % (10 + i), "1", "passive")]
        gnd.append(("C%d" % (10 + i), "2", "passive"))
        comps["U%d" % (10 + i)] = "XQ"; comps["C%d" % (10 + i)] = "1u"
    extra["GND"] = gnd
    r, _p, _d = _with(extra, comps)
    assert len(r["undecided"]) == 60, len(r["undecided"])
    v = _verdict(r)
    assert len(v["evidence"]) == 50 and v["evidence"][0].startswith("census of the"), v["evidence"][:2]
    names = next(e for e in v["evidence"] if e.startswith("undecided, named and not counted (60): "))
    assert all("P%02d" % i in names for i in range(60)), names[:200]


# ---- fourth pass (27 September 2026): the third check's blocking item, board A's VMON ------------------------------
EFUSE = "TPS259631DDAR eFuse +3V3 -> EF_OUT"


def _efuse(out_nodes, value=EFUSE, extra=None):
    """An eFuse U5 on the fixture's +3V3 rail: IN (pin 4) on the rail, GND (pin 1) on ground, OUT (pin 5) on EF_OUT
    with the nodes given and nothing else, the way board A's U21 feeds the monitor lead J_MON."""
    nets = {"+3V3": BASE_NETS["+3V3"] + [("U5", "4", "passive", "IN")],
            "GND": BASE_NETS["GND"] + [("U5", "1", "passive", "GND")],
            "EF_OUT": [("U5", "5", "passive", "EF_OUT")] + list(out_nodes)}
    nets.update(extra or {})
    return nets, {"U5": value}


def t_an_efuse_output_is_a_power_net_by_its_held_pin_table_even_where_nothing_on_it_marks_a_supply():
    """TI's TPS2596 pin table types pin 5 "Power Output". Delivered to a three-pin connector whose other pins are a
    ground and a signal, the output carries no capacitor, no two-terminal link and no lead: only the held row reads it,
    and it must be declared; declared as a rail with its source and load, nothing is refused on it."""
    nets, comps = _efuse([("J5", "1", "passive", "Pin_1")],
                         extra={"MON_SIG": [("J5", "3", "passive", "Pin_3"), ("U2", "7", "passive", "PA7")]})
    nets["GND"] = nets["GND"] + [("J5", "2", "passive", "Pin_2")]
    comps["J5"] = "monitor lead (3-pin): + - sense"
    r, _p, _d = _with(nets, comps)
    assert any(t.startswith("power net EF_OUT is") and "U5.5 OUT" in t for t in _fails(r)), r["checks"]
    rails = dict(BASE_RAILS); rails["EF_OUT"] = _rail("U5", {"J5": 1.2}, 1.2)
    r2, _p, _d = _with(nets, comps, rails=rails)
    assert not any("EF_OUT" in t for t in _fails(r2)), _fails(r2)
    # the other way: the same output from a part no row reads, beside a signal, is marked by nothing (the limit the
    # coverage note states; the suite's power-part sweep holds every power part on the boards to a held row)
    comps2 = dict(comps, U5="XEF2596 eFuse")
    r3, _p, _d = _with(nets, comps2)
    assert r3["census"]["EF_OUT"] == "unmarked", r3["census"]["EF_OUT"]


def t_a_lead_with_only_ground_beside_it_is_undecided_until_the_part_that_feeds_it_is_read():
    """M5, the general mark for the blocking item's shape: board A's J_MON is a two-pin lead, pin 2 on ground, and U21's
    OUT on pin 1. From a part no row reads the lead is undecided (INCONCLUSIVE, never PASS); from the held TPS2596 it is
    counted; from a held pin that supplies nothing (the LTC2954's push-button input) it is settled, and the lead is
    said to carry what that pin carries."""
    nets, comps = _efuse([("J6", "1", "passive", "Pin_1")], value="XEF2596 eFuse")
    nets["GND"] = nets["GND"] + [("J6", "2", "passive", "Pin_2")]
    comps["J6"] = "monitor supply lead (JST-VH): + -"
    r, _p, _d = _with(nets, comps)
    assert "EF_OUT" in r["undecided"] and "M5 a lead: J6" in r["undecided"]["EF_OUT"], r["undecided"]
    assert not _fails(r) and _verdict(r)["verdict"] == "INCONCLUSIVE", _fails(r)
    r2, _p, _d = _with(nets, dict(comps, U5=EFUSE))
    assert any(t.startswith("power net EF_OUT is") for t in _fails(r2)), r2["checks"]
    pb = {"MAIN_PB": [("U6", "2", "passive", "PB"), ("J7", "1", "passive", "Pin_1")],
          "GND": BASE_NETS["GND"] + [("J7", "2", "passive", "Pin_2"), ("U6", "4", "passive", "GND")]}
    r3, _p, _d = _with(pb, {"U6": "LTC2954ITS8-1 push-button on/off controller", "J7": "push-button lead"})
    assert "MAIN_PB" in r3["settled"] and "the lead J7.1" in r3["settled"]["MAIN_PB"], (r3["settled"], r3["undecided"])
    r4, _p, _d = _with(pb, {"U6": "XPB2954 push-button controller", "J7": "push-button lead"})
    assert "MAIN_PB" in r4["undecided"], r4["undecided"]
    # a connector whose other pin is not on ground is no lead
    pb2 = {"MAIN_PB": pb["MAIN_PB"], "OTHER": [("J7", "2", "passive", "Pin_2"), ("U2", "9", "passive", "PA9")]}
    r5, _p, _d = _with(pb2, {"U6": "XPB2954 push-button controller", "J7": "two-wire cable"})
    assert r5["census"]["MAIN_PB"] == "unmarked", r5["census"]["MAIN_PB"]


def t_a_net_the_netlist_classes_sense_is_undecided_until_declared_or_read():
    """M6: board P's cell taps CELL1 to CELL3 are class SENSE in the netlist and run from the cell block's connector
    through resistors only. The class is the schematic's own statement that the conductor senses a supply: undecided
    until the board declares it (or a held pin on it reads it); the same net of the default class is unmarked."""
    nets = {"CELL1": [("J8", "2", "passive", "Pin_2"), ("R8", "1", "passive"), ("R9", "1", "passive")],
            "VC1_F": [("R8", "2", "passive")], "SEC_V1": [("R9", "2", "passive")],
            "GND": BASE_NETS["GND"] + [("J8", "1", "passive", "Pin_1")]}
    comps = {"J8": "cell tap sense wires (JST-XH 1x5)", "R8": "100R", "R9": "1k"}
    r, _p, _d = _with(nets, comps, classes={"CELL1": "SENSE"})
    assert "CELL1" in r["undecided"] and "M6" in r["undecided"]["CELL1"], r["undecided"]
    nodes = dict(BASE_NODES); nodes["CELL1"] = _declared(3.6, "a cell tap: sense and balance current only")
    r2, _p, _d = _with(nets, comps, classes={"CELL1": "SENSE"}, nodes=nodes)
    assert "CELL1" not in r2["undecided"] and r2["census"]["CELL1"] == "declared node", r2["census"]["CELL1"]
    r3, _p, _d = _with(nets, comps)
    assert r3["census"]["CELL1"] == "unmarked", r3["census"]["CELL1"]


def t_the_switched_return_of_a_load_is_marked_and_an_open_drain_line_to_a_connector_is_not():
    """M4's low side (the first check of this round): board P's SCP_HTR joins the SCF9550's heater terminal to Q3's
    drain, whose source is on ground, so the fuse-blow current returns through it: marked, and the fuse's unread
    heater pin leaves it undecided. The same transistor pulling a connector's pin (a module's W_DISABLE line on board
    B) is an open-drain control line and is not marked."""
    nets = {"SCP_HTR": [("F2", "3", "passive", "Pin_3"), ("Q3", "3", "passive", "D")],
            "FUSE_GQ": [("Q3", "1", "input", "G"), ("R32", "1", "passive")],
            "VIN": BASE_NETS["VIN"] + [("F2", "1", "passive", "Pin_1")], "F2_OUT": [("F2", "2", "passive", "Pin_2")],
            "GND": BASE_NETS["GND"] + [("Q3", "2", "passive", "S"), ("R32", "2", "passive")]}
    comps = {"F2": "SCF9550-30-05 self-control fuse", "Q3": "AO3400A", "R32": "1M"}
    r, _p, _d = _with(nets, comps)
    assert "SCP_HTR" in r["undecided"] and "switched return of F2" in r["undecided"]["SCP_HTR"], r["undecided"]
    nets2 = dict(nets); nets2["SCP_HTR"] = [("J9", "3", "passive", "Pin_3"), ("Q3", "3", "passive", "D")]
    nets2["VIN"] = BASE_NETS["VIN"]; del nets2["F2_OUT"]
    r2, _p, _d = _with(nets2, {"J9": "M.2 socket", "Q3": "2N7002", "R32": "1M"})
    assert r2["census"]["SCP_HTR"] == "unmarked", r2["census"]["SCP_HTR"]


def t_a_ground_pin_its_datasheet_names_is_a_power_net_off_ground_and_nothing_on_ground():
    """A held row's GROUND role: the TPS2596's GND pin on a net that is not a ground carries the part's return current
    and is counted; on ground it is ground and nothing is asked."""
    nets, comps = _efuse([("C11", "1", "passive")], extra={"EF_RTN": [("R11", "1", "passive")]})
    nets["GND"] = BASE_NETS["GND"] + [("C11", "2", "passive"), ("R11", "2", "passive")]
    nets["EF_RTN"] = nets["EF_RTN"] + [("U5", "1", "passive", "GND")]
    comps.update({"C11": "1u", "R11": "0.01R"})
    rails = dict(BASE_RAILS); rails["EF_OUT"] = _rail("U5", {"C11": 0.0}, 1.0)
    r, _p, _d = _with(nets, comps, rails=rails)
    assert any(t.startswith("power net EF_RTN is") and "a ground pin" in t for t in _fails(r)), r["checks"]
    nets2, comps2 = _efuse([("C11", "1", "passive")])
    nets2["GND"] = nets2["GND"] + [("C11", "2", "passive")]
    r2, _p, _d = _with(nets2, dict(comps2, C11="1u"), rails=rails)
    assert r2["census"]["GND"] == "ground" and not any("a ground pin" in t for t in _fails(r2)), _fails(r2)


def t_a_connector_whose_value_names_a_held_part_is_not_that_part():
    """Board B's J_GNSS2 is a bench header whose value reads "LG290P UART2 (bench): GND TX RX"; the module itself is
    U11. A connector is never read as the part its value field names."""
    held, _docs = IC.held_roles({"J_GNSS2": "LG290P UART2 (bench): GND TX RX", "J1": "LG290P antenna"})
    assert not held, held
    held2, _docs = IC.held_roles({"U11": "Quectel LG290P03AAMD GNSS RTK module"})
    assert held2.get(("U11", "9"), (None, None))[1] == IC.ROLE_SUPPLY, held2.get(("U11", "9"))


def t_a_crystal_settles_its_net_and_an_oscillator_with_a_supply_pin_does_not():
    """A crystal or resonator has two terminals on nets of their own (a can's other pins on ground): its net is an
    oscillator's. A part of the same prefix with a third live net is an oscillator with a supply pin, and its supply
    net is read like any other (the first check of this round: latent on the six boards)."""
    nets = {"XIN": [("Y1", "1", "passive"), ("C5", "1", "passive"), ("U2", "20", "passive", "XIN")],
            "XOUT": [("Y1", "3", "passive"), ("U2", "21", "passive", "XOUT")],
            "GND": BASE_NETS["GND"] + [("Y1", "2", "passive"), ("Y1", "4", "passive"), ("C5", "2", "passive")]}
    r, _p, _d = _with(nets, {"Y1": "12 MHz 4-pad crystal", "C5": "15p"})
    assert "oscillator" in r["settled"].get("XIN", ""), (r["settled"], r["undecided"])
    osc = {"OSC_VDD": [("Y2", "4", "passive"), ("C6", "1", "passive")],
           "OSC_EN": [("Y2", "1", "passive"), ("U2", "22", "passive", "PA22")],
           "CLK": [("Y2", "3", "passive"), ("U2", "23", "passive", "PA23")],
           "GND": BASE_NETS["GND"] + [("Y2", "2", "passive"), ("C6", "2", "passive")]}
    r2, _p, _d = _with(osc, {"Y2": "25 MHz oscillator", "C6": "100n"})
    assert "OSC_VDD" in r2["undecided"], (r2["settled"].get("OSC_VDD"), r2["undecided"])


def t_a_capacitor_to_an_analogue_or_power_ground_is_decoupling():
    """M1 reads the ground family (AGND, PGND): a supply decoupled only to an analogue ground is marked. A capacitor
    to a net that is not a ground and not a supply marks nothing."""
    nets = {"VREF_X": [("U9", "3", "passive", "Pin_3"), ("C9", "1", "passive")], "AGND": [("C9", "2", "passive")]}
    r, _p, _d = _with(nets, {"U9": "XQ", "C9": "1u"})
    assert "VREF_X" in r["undecided"] and "M1" in r["undecided"]["VREF_X"], r["undecided"]
    nets2 = {"VREF_X": nets["VREF_X"], "FOO": [("C9", "2", "passive")]}
    r2, _p, _d = _with(nets2, {"U9": "XQ", "C9": "1u"})
    assert r2["census"]["VREF_X"] == "unmarked", r2["census"]["VREF_X"]


# THE FIFTH PASS (integration, 27 September 2026): the fourth independent check's blocking item and its fixture gap.
# Board C's e-paper boost, as gen_sch_c.py draws it: L1 from the supply to EPD_SW, the boost switch Q6 (gate on
# EPD_GDR, source on EPD_RESE, drain on EPD_SW) and the 0.47R shunt R43 from EPD_RESE to ground, with the panel's RESE
# sense pin J_EPD.3 on it. EPD_SW carries the inductor's current and the board declares it as a node.
def _boost(nodes_extra=None):
    nets = {"+3V3": BASE_NETS["+3V3"] + [("L6", "1", "passive")],
            "EPD_SW": [("L6", "2", "passive"), ("Q6", "3", "passive", "D")],
            "EPD_RESE": [("Q6", "2", "passive", "S"), ("R43", "1", "passive"), ("J_EPD", "3", "passive", "Pin_3")],
            "EPD_GDR": [("Q6", "1", "input", "G"), ("J_EPD", "2", "passive", "Pin_2")],
            "GND": BASE_NETS["GND"] + [("R43", "2", "passive"), ("J_EPD", "8", "passive", "Pin_8")]}
    comps = {"L6": "10uH boost inductor", "Q6": "Si2300DS boost switch", "R43": "0.47R 1%",
             "J_EPD": "24-way ZIF for the e-paper flex"}
    nodes = dict(BASE_NODES, EPD_SW=_declared(25.0, "the boost switch node"))
    nodes.update(nodes_extra or {})
    return nets, comps, nodes


def t_a_declared_node_that_carries_a_mark_passes_it_on_and_one_that_carries_none_does_not():
    """DEFECTIVE (the fourth check's finding, board C's EPD_RESE): the boost switch's source net carries the inductor's
    current every on-phase, and the tool before this pass read it unmarked, because `hot` held the counted nets and the
    declared rails only and EPD_SW, marked M3 through L1, is a declared node. It reads undecided now, by M4 through
    Q6's channel. ACCEPTABLE: the gate net beside it (EPD_GDR) is not marked through the gate; and a declared node that
    carries no mark itself passes nothing on (board B's eSIM lines: a node reached by a 0R link would otherwise mark
    the SIM holder's side, SIM2_IO_C here)."""
    nets, comps, nodes = _boost()
    r, _p, _d = _with(nets, comps, nodes=nodes)
    assert "EPD_RESE" in r["undecided"], (r["census"].get("EPD_RESE"), r["undecided"])
    assert "M4 the channel of Q6 with the net EPD_SW" in r["undecided"]["EPD_RESE"], r["undecided"]["EPD_RESE"]
    assert r["census"]["EPD_SW"] == "declared node", r["census"]["EPD_SW"]
    assert r["census"]["EPD_GDR"] == "unmarked", r["census"]["EPD_GDR"]
    assert not _fails(r) and _verdict(r)["verdict"] == "INCONCLUSIVE", _fails(r)
    # the same drawing with EPD_RESE declared: a declaration settles it
    r2, _p, _d = _with(nets, comps, nodes=dict(nodes, EPD_RESE=_declared(0.4, "the boost switch's current shunt")))
    assert "EPD_RESE" not in r2["undecided"] and r2["census"]["EPD_RESE"] == "declared node", r2["census"]["EPD_RESE"]
    # a declared node with no mark of its own: the eSIM data line behind a 0R link stays unmarked
    esim = {"SIM2_IO": [("U9", "7", "passive", "SIM_IO"), ("R272", "1", "passive")],
            "SIM2_IO_C": [("R272", "2", "passive"), ("J3", "7", "passive", "IO")]}
    r3, _p, _d = _with(esim, {"U9": "XMODEM eSIM host", "R272": "0R", "J3": "eSIM socket"},
                       nodes=dict(BASE_NODES, SIM2_IO=_declared(1.8, "the SIM data line")))
    assert r3["census"]["SIM2_IO_C"] == "unmarked", (r3["census"]["SIM2_IO_C"], r3["undecided"].get("SIM2_IO_C"))


def t_a_connector_on_a_net_with_any_mark_but_a_lead_or_a_sense_class_is_read_by_nothing():
    """The fourth check's fixture gap: a connector is passed over (it carries what the board's read pins carry) only
    when every mark on the net is M5 or M6. DEFECTIVE, board E's WATER_SENSE: a capacitor to ground (M1) and the SENSE
    class (M6) beside the electrode pad and an RP2040 ADC pin; the pad is read by nothing, so the net is undecided (the
    mutant `lead = bool(marks)` settled it). ACCEPTABLE: the same net with the SENSE class alone is settled by the held
    GPIO, and the settle names the lead."""
    nets = {"WET": [("C51", "1", "passive"), ("PAD_W2", "1", "passive", "Pin_1"), ("U3", "40", "passive", "GPIO28_A2"),
                    ("R39", "1", "passive")],
            "GND": BASE_NETS["GND"] + [("C51", "2", "passive"), ("R39", "2", "passive")]}
    comps = {"C51": "100n", "PAD_W2": "water electrode (bare copper)", "U3": "RP2040 sensor controller", "R39": "1M"}
    r, _p, _d = _with(nets, comps, classes={"WET": "SENSE"})
    assert "WET" in r["undecided"] and "M1" in r["undecided"]["WET"], (r["settled"].get("WET"), r["undecided"])
    assert "PAD_W2.1" in r["undecided"]["WET"], r["undecided"]["WET"]
    nets2 = {"WET": [x for x in nets["WET"] if x[0] != "C51"], "GND": BASE_NETS["GND"] + [("R39", "2", "passive")]}
    r2, _p, _d = _with(nets2, comps, classes={"WET": "SENSE"})
    assert "WET" in r2["settled"] and "the lead PAD_W2.1" in r2["settled"]["WET"], (r2["settled"], r2["undecided"])
