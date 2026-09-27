#!/usr/bin/env python3
"""The pack's protection, judged against the cell maker's own numbers (rule BAT-001, 18 September 2026).

BAT-001 is a BLOCKER on board P and had no instrument: the thresholds of the BQ4050's protection subsystem live
in data flash and this tree never said what they are, so nothing could compare one with the cell's own limit.
`pcb_pack_protection.yaml` is that configuration written down and `pack_protection.py` judges it. These are the
rules of the judgement: the derivation in each direction, the transcription guard that re-reads every quoted
limit from the cell's own specification, and the requirement's own words about software."""
import copy, os, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import pack_protection as P


def _t():
    return copy.deepcopy(P.load())


def t_the_committed_table_meets_the_cells_own_limits_and_names_every_protection():
    """THE ACCEPTABLE FIXTURE, and it is the real table: nine functions, every threshold inside the limit it is
    derived from at the pack's WORST parallel count, every device on board P's netlist, and every quoted limit
    found in the cell maker's own document. The one failure it does report is the requirement's other half."""
    r = P.judge(_t(), P.NETLIST)
    assert r["checks"] > 30, r
    other = [f for f in r["fails"] if "INDEPENDENT OF ANY SOFTWARE" not in f]
    assert not other, "the committed table fails a derivation check: %s" % other


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
    assert any("BELOW the cell maker's own overdischarge_protect_v" in f for f in r["fails"]), r["fails"]


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
    """BAT-001 asks for protection in hardware INDEPENDENT OF ANY SOFTWARE. Board P carries one BQ4050 whose
    thresholds live in data flash, no second protector, no chemical fuse and a PTC tied off; the only element
    that needs no firmware is a 25 A blade fuse, which does not protect a cell from over-voltage, over-discharge
    or heat. That is a finding about the design and the gate says it in the requirement's own words."""
    r = P.judge(_t(), P.NETLIST)
    assert any("INDEPENDENT OF ANY SOFTWARE" in f for f in r["fails"]), r["fails"]
    t = _t()
    t["pack"]["secondary_protection"] = {"present": True, "why": "a fixture: a second protector IC on the cell taps"}
    r2 = P.judge(t, P.NETLIST)
    assert not any("INDEPENDENT OF ANY SOFTWARE" in f for f in r2["fails"]), \
        "the sentence stands even where the pack declares a protector independent of the gauge"


def t_a_device_the_board_does_not_carry_is_not_a_protection():
    t = _t()
    t["devices"]["U9"] = {"part": "a part nobody placed", "what": "a fixture", "software": False}
    r = P.judge(t, P.NETLIST)
    assert any("board P's netlist has no such reference" in f for f in r["fails"]), r["fails"]


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
