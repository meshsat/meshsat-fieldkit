#!/usr/bin/env python3
"""The pack's protection, judged against the cell maker's own numbers (rule BAT-001, 18 September 2026).

BAT-001 is a BLOCKER on board P and had no instrument: the thresholds of the BQ4050's protection subsystem live
in data flash and this tree never said what they are, so nothing could compare one with the cell's own limit.
`pcb_pack_protection.yaml` is that configuration written down and `pack_protection.py` judges it. These are the
rules of the judgement: the derivation in each direction, the transcription guard that re-reads every quoted
limit from the cell's own specification, and the requirement's own words about software.

27 September 2026 (stream w4dp, S-45): THE TABLE DESCRIBES THE DRAWN CIRCUIT, AND THIS FILE HOLDS IT TO THE NETLIST.
For nine days the table's `secondary_protection` said "no second protector, no chemical fuse, PTC tied off" while
board P's committed netlist carried all three (decision 40's floor, since faf8c981), and nothing here noticed,
because the table was judged only against the cell's document and a list of references. `floor_on_netlist` reads the
floor's CONNECTIONS on the netlist (regen_compare.parse_net, never a grep): the second level on the cell taps, its
COUT and the gauge's FUSE meeting at the fuse gate, the arming jumper, the heater switch on the chemical fuse's heater
terminal, the fuse in the cell path, the under-voltage hold on the discharge FET's gate, and the PTC element with
PTCEN on BAT. The table must declare the floor present exactly when the netlist carries it, both ways. The table's
hardware rows (`level: hardware`) are judged by the same gate against the same cell limits, and every one of them
that fails names the open finding that carries it; a row whose gap is closed must drop its finding."""
import copy, os, re, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import pack_protection as P
import regen_compare


def _t():
    return copy.deepcopy(P.load())


def _level(f):
    return f.get("level") or "primary"


def _fails_by_function(r, t):
    """{function id: [failure text]} for the failures the gate attributes to a function (its text starts with the id)."""
    ids = sorted((f["id"] for f in t["functions"]), key=len, reverse=True)
    out = {}
    for x in r["fails"]:
        fid = next((i for i in ids if x.startswith(i + " ")), None)
        out.setdefault(fid, []).append(x)
    return out


def t_the_committed_table_meets_the_cells_own_limits_and_names_every_protection():
    """THE ACCEPTABLE FIXTURE, and it is the real table: the gauge's nine functions, every threshold inside the limit
    it is derived from at the pack's WORST parallel count, every device on board P's netlist, and every quoted limit
    found in the cell maker's own document. The failures it does report are the hardware level's, each on a row that
    names its open finding (since 27 September 2026; before that it was the one sentence about software)."""
    t = _t()
    r = P.judge(t, P.NETLIST)
    assert r["checks"] > 30, r
    by = _fails_by_function(r, t)
    assert None not in by, "a failure the table cannot attribute to a function: %s" % by.get(None)
    rows = {f["id"]: f for f in t["functions"]}
    primary = [fid for fid in by if _level(rows[fid]) == "primary"]
    assert not primary, "the committed table fails a derivation check on the gauge's rows: %s" % {k: by[k] for k in primary}
    for fid in by:
        assert rows[fid].get("open"), "%s fails (%s) and names no open finding that carries it" % (fid, by[fid])
    assert not any("INDEPENDENT OF ANY SOFTWARE" in x for x in r["fails"]), r["fails"]


def _open_without_failure(t, r):
    by = _fails_by_function(r, t)
    return sorted(f["id"] for f in t["functions"] if f.get("open") and f["id"] not in by)


def t_a_hardware_row_that_passes_drops_its_open_finding():
    """Both ways: a row whose gap is closed and still names an open finding keeps a finding alive that the gate no
    longer supports. On the committed table every row that names one fails; give the under-voltage row a threshold at
    or above the guideline's 2.30 V (the custom part W4DP-F1 names) and it passes, and its `open` is then stale."""
    t = _t()
    assert _open_without_failure(t, P.judge(t, P.NETLIST)) == [], "a committed row names an open finding and passes"
    for f in t["functions"]:
        if f["id"] == "SECOND_LEVEL_CELL_UNDER_VOLTAGE":
            assert f.get("open"), "the fixture needs the committed row's open finding"
            f["threshold"]["value"] = 2.35
    assert _open_without_failure(t, P.judge(t, P.NETLIST)) == ["SECOND_LEVEL_CELL_UNDER_VOLTAGE"]


def t_every_hardware_row_is_on_a_part_that_needs_no_firmware():
    """A row claiming the requirement's `in hardware, independent of any software` on a part whose table entry says
    software: true would pass the words without the substance, so every hardware row's device is software: false, and
    the five functions BAT-001 names each have a hardware row."""
    t = _t()
    hw = [f for f in t["functions"] if _level(f) == "hardware"]
    for f in hw:
        d = t["devices"].get(f["device"]) or {}
        assert d.get("software") is False, "%s is on %s, whose entry does not say it needs no firmware" % (f["id"], f["device"])
    covered = " ".join(f["id"] for f in hw)
    for word in ("OVER_VOLTAGE", "UNDER_VOLTAGE", "OVER_CURRENT", "SHORT_CIRCUIT", "OVER_TEMPERATURE"):
        assert word in covered, "BAT-001 names %s and the hardware level has no row for it" % word.lower()


def t_a_trip_point_outside_the_cells_own_limit_is_refused():
    """THE DEFECTIVE FIXTURE. A pack over-current threshold at 26 A reads fine against four cells in parallel
    (32 A) and is over the limit at three (24 A), which is the configuration this pack may be built in, so the
    judgement is made at the worst parallel count. An under-voltage trip below the cell maker's own
    over-discharge protection voltage is refused the same way."""
    t = _t()
    for f in t["functions"]:
        if f["id"] == "PACK_OVER_CURRENT_DISCHARGE": f["threshold"]["value"] = 26.0
        if f["id"] == "CELL_UNDER_VOLTAGE": f["threshold"]["value"] = 2.20
    r = P.judge(t, P.NETLIST)
    assert any("26.0 A and 3 cells in parallel are rated 24.0 A" in f for f in r["fails"]), r["fails"]
    assert any(f.startswith("CELL_UNDER_VOLTAGE trips at 2.2, BELOW the cell maker's own overdischarge_protect_v")
               for f in r["fails"]), r["fails"]


def t_a_limit_quoting_something_the_document_does_not_say_is_refused():
    """The transcription guard, which is the fuse table's lesson (17 September 2026: nine of thirteen typed rows
    were shifted a column). Every limit carries the string as it appears in the cell's specification and the
    gate looks for it there; a number typed from memory cannot survive that. Where the host cannot read a PDF
    at all the gate says so in a note instead of passing quietly."""
    t = _t()
    t["cell"]["limits"]["discharge_cutoff_v"]["quote"] = "2.85V"
    r = P.judge(t, P.NETLIST)
    if not r["quotes_checked"]:
        assert any("not re-checked" in n for n in r["notes"]), r["notes"]
        return
    assert any("quotes '2.85V'" in f for f in r["fails"]), r["fails"]


def t_a_protection_the_requirement_names_cannot_be_left_out():
    t = _t()
    t["functions"] = [f for f in t["functions"] if f["id"] != "PACK_SHORT_CIRCUIT_DISCHARGE"]
    r = P.judge(t, P.NETLIST)
    assert any("short circuit" in f for f in r["fails"]), r["fails"]


def t_a_function_with_no_prototype_test_is_refused():
    """Half of this rule's acceptance criteria is the test that will demonstrate the threshold on the prototype.
    A table of numbers with nothing to measure them against is a table of intentions."""
    t = _t()
    for f in t["functions"]:
        if f["id"] == "CELL_OVER_VOLTAGE": f["test"] = "check it"
    r = P.judge(t, P.NETLIST)
    assert any("names no prototype test" in f for f in r["fails"]), r["fails"]


def t_a_pack_whose_every_protection_is_firmware_fails_the_requirements_own_words():
    """BAT-001 asks for protection in hardware INDEPENDENT OF ANY SOFTWARE. A pack whose every protection is one
    BQ4050 with thresholds in data flash, no second protector, no chemical fuse and a PTC tied off (board P before
    faf8c981) fails in the requirement's own words; the committed table, which declares decision 40's floor that the
    netlist carries (the next test holds the two together), does not carry the sentence."""
    t = _t()
    t["pack"]["secondary_protection"] = {"present": False, "why": "a fixture: the gauge alone, as board P was before faf8c981"}
    t["functions"] = [f for f in t["functions"] if _level(f) == "primary"]
    r = P.judge(t, P.NETLIST)
    assert any("INDEPENDENT OF ANY SOFTWARE" in f for f in r["fails"]), r["fails"]
    r2 = P.judge(_t(), P.NETLIST)
    assert not any("INDEPENDENT OF ANY SOFTWARE" in f for f in r2["fails"]), \
        "the committed table declares the floor and the gate still reads the pack as firmware-only"


def t_a_device_the_board_does_not_carry_is_not_a_protection():
    t = _t()
    t["devices"]["U9"] = {"part": "a part nobody placed", "what": "a fixture", "software": False}
    r = P.judge(t, P.NETLIST)
    assert any("board P's netlist has no such reference" in f for f in r["fails"]), r["fails"]


# ------------------------------------------------------------------------------------------ the table against the netlist
def _read(path):
    return regen_compare.parse_net(open(path, encoding="utf-8", errors="replace").read())


def _pins(nets):
    """{(ref, pin): net} with the leading slash of a sheet path taken off the net name."""
    return {(r, p): n.lstrip("/") for n, nodes in nets.items() for r, p, _f, _t in nodes}


def floor_on_netlist(comps, nets):
    """Decision 40's floor as board P draws it, read on the netlist: returns the list of what is MISSING (empty when
    every connection is there). Pins are the makers': BQ4050 SLUSC67B pin table (23 PTC, 24 PTCEN, 25 FUSE, 32 BAT),
    BQ77207 SLUSEG7D 12-Pin Functions (1 VDD, 8 V1, 9 VSS, 10 COUT, 11 DOUT), SCF9550 ELX1135 (1 and 2 the fuse, 3
    the heater), AO3400A and 2N7002 in SOT-23 (1 G, 2 S, 3 D), the CSD17570Q5B PowerPAK (4 G, 5 D)."""
    pin = _pins(nets)
    at = lambda r, p: pin.get((r, str(p)))
    two = lambda r: {at(r, "1"), at(r, "2")}
    missing = []
    def need(ok, what):
        if not ok: missing.append(what)
    val = lambda r: (comps.get(r) or {}).get("value") or ""
    need("BQ7720700" in val("U2"), "U2 is a BQ7720700 second level (value %r)" % val("U2"))
    need("SCF9550" in val("F2"), "F2 is the SCF9550 chemical fuse (value %r)" % val("F2"))
    need("AO3400A" in val("Q3") and "2N7002" in val("Q5"), "Q3 an AO3400A and Q5 a 2N7002")
    cells = {at("J_CELL", k) for k in ("2", "3", "4", "5")}
    need(at("U2", 9) == "GND" and at("J_CELL", 1) == "GND", "U2's VSS and J_CELL's B- on the cell block's negative")
    need(all(any(n in {at(r, 1), at(r, 2)} for r in ("R24", "R25", "R26", "R27")) for n in cells),
         "every cell tap J_CELL 2 to 5 reaches U2's inputs through its own filter resistor (R24 to R27)")
    need(at("U2", 8) in {at("R24", 1), at("R24", 2)} - {at("J_CELL", 2)}, "U2 V1 behind R24 from the first tap")
    cout, fuse_g = at("U2", 10), at("JP1", 1)
    need(bool(cout) and cout != fuse_g and two("R29") == {cout, fuse_g}, "U2 COUT reaches FUSE_G through R29")
    need(two("R30") == {at("U1", 25), fuse_g}, "the gauge's FUSE (U1 pin 25) reaches FUSE_G through R30")
    need(bool(fuse_g) and at("JP1", 2) == at("Q3", 1) and at("JP1", 2) != fuse_g, "JP1 between FUSE_G and Q3's gate")
    need(at("Q3", 2) == "GND" and at("Q3", 3) == at("F2", 3), "Q3 sinks F2's heater terminal (pin 3) to the negative")
    need(two("F1") == {at("F2", 1), at("J_CELL", 5)} and at("F2", 2) in {at("Q1", k) for k in ("1", "2", "3")},
         "F1 from the cell block's positive into F2, and F2 into the charge FET Q1's source: the fuse in the cell path")
    dsg_g = at("Q2", 4)
    need(two("R28") == {at("U2", 11), "GND"} and at("Q5", 1) == at("U2", 11) and at("Q5", 2) == "GND"
         and at("Q5", 3) == dsg_g and bool(dsg_g), "U2 DOUT turns Q5 on, which holds the discharge FET Q2's gate at VSS")
    need(two("RT1") == {at("U1", 23), at("U1", 32)} and at("U1", 24) == at("U1", 32),
         "the PTC element RT1 from the gauge's PTC pin to BAT, with PTCEN on BAT (not tied to VSS)")
    return missing


def t_the_table_declares_the_floor_the_netlist_carries_both_ways():
    """S-45's defect as a property. The committed netlist carries decision 40's floor and the table declares it
    present, naming parts that are all on the netlist and all in `devices`; take one connection out of a copy of the
    netlist (PTCEN back on VSS, the pre-faf8c981 state) and the floor is missing, so a table that still declared it
    present would be refused; and a table saying absent beside a netlist that carries it is refused too."""
    comps, nets = _read(P.NETLIST)
    t = _t()
    miss = floor_on_netlist(comps, nets)
    sec = t["pack"]["secondary_protection"]
    assert not miss, "board P's committed netlist lacks the floor: %s" % miss
    assert sec.get("present") is True, "the netlist carries the floor and the table declares it absent: %s" % sec
    for ref in sec.get("parts") or []:
        assert ref in t["devices"], "the floor names %s and `devices` does not describe it" % ref
        assert ref in comps, "the floor names %s and board P's netlist has no such reference" % ref
    # the defective fixture: PTCEN on VSS and U2 gone from the fuse gate
    nets2 = {n: list(v) for n, v in nets.items()}
    for n in list(nets2):
        nets2[n] = [x for x in nets2[n] if (x[0], x[1]) not in (("U1", "24"), ("R29", "1"), ("R29", "2"))]
    nets2.setdefault("GND", []).append(("U1", "24", "PTCEN", "input"))
    miss2 = floor_on_netlist(comps, nets2)
    assert any("PTCEN" in m for m in miss2) and any("COUT" in m for m in miss2), miss2


def t_every_protection_function_is_in_the_test_plan():
    """Half of this rule's acceptance criteria is the test that will demonstrate the threshold on the prototype,
    and a test that lives only in a YAML file is not a test plan: `v2/docs/TEST-PLAN.md` is the document a person
    reads before the bench, so every function in the table is in it by name. The two cannot drift without this
    rule failing, which is the same shape as the rotation table and its own CSV."""
    doc = os.path.join(os.path.dirname(os.path.dirname(TOOLS)), "docs", "TEST-PLAN.md")
    txt = open(doc, encoding="utf-8").read().lower()
    for f in P.load()["functions"]:
        name = f["id"].replace("_", " ").lower()
        assert name in txt, "the test plan does not carry %s, so its prototype test is written down in one place only" % f["id"]
    assert "decision 40" in txt, "the test plan does not say which half of BAT-001 no bench test can answer"
