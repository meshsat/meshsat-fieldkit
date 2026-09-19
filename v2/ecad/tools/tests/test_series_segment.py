#!/usr/bin/env python3
"""ONE PATH'S WATTS ARE COUNTED ONCE, AND EVERY SEGMENT OF IT IS STILL JUDGED (rule THM-001, 20 September 2026).

A conductor run is usually several nets. Board A's charge bus leaves the FE stage's boost FET as `FE_OUT`,
crosses the ISNS shunt R11 and becomes `VBUS20`, crosses the input shunt R16 and continues as `CH_ACN` to the
charger's high-side FET. The USB-C outlet is four nets in series at 3 A. Every one of those segments needs a
RAIL declaration, because `intent.node()` says in its own first line that it describes a net that is not a
rail and `dc_drop` solves no potential on one: that is how sixteen DC conductors on board A came to be
measured by no power rule at all, two of them carrying 4.81 A and 6.26 A in conductors IPC rates at 0.40.

But `thermal.py` sums every declared rail's volts times amps into the board's power figure, so declaring the
segments without saying what they are counts one path's watts twice, three times or four. That defect was
introduced on 20 September by the first two conversions and is closed here rather than argued about: a rail
that is a segment says `series_of=<the rail whose watts it carries>`, thermal excludes it from the sum and
from the loss questions, and dc_drop, derate, via_current and rail_crossings go on judging its copper exactly
as they judge any rail's. That is the whole point of the declaration.

The two fixtures the standard asks for are both here for each rule: a DEFECTIVE input whose expected verdict
is a refusal, and an ACCEPTABLE one whose expected verdict is that nothing is flagged.
"""
import os, sys, json, tempfile, importlib

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)


def _fresh():
    """intent.py holds one module-level dict, so a rule that declares rails starts from a clean one."""
    import intent
    importlib.reload(intent)
    return intent


def t_a_segment_must_name_a_rail_that_exists():
    """DEFECTIVE: the named path is not a declared rail, so its watts are counted nowhere."""
    i = _fresh()
    i.rail("VBUS20", 20.0, 6.0, 8.0, "R11", loads={"R16": 6.0})
    try:
        i.rail("CH_ACN", 20.0, 6.0, 8.0, "R16", loads={"Q7": 6.0}, series_of="NO_SUCH_RAIL")
    except SystemExit as e:
        assert "not a declared rail" in str(e), str(e)
        return
    raise AssertionError("a segment named a rail that does not exist and the declaration was accepted")


def t_a_segment_of_a_real_rail_is_accepted():
    """ACCEPTABLE: board A's own case, and it must not be flagged."""
    i = _fresh()
    i.rail("VBUS20", 20.0, 6.0, 8.0, "R11", loads={"R16": 6.0})
    i.rail("CH_ACN", 20.0, 6.0, 8.0, "R16", loads={"Q7": 6.0}, series_of="VBUS20")
    assert i._I["rails"]["CH_ACN"]["series_of"] == "VBUS20"


def t_a_segment_cannot_carry_more_than_its_path():
    """DEFECTIVE: the arithmetic that makes the exclusion safe is that the segment's current is the path's."""
    i = _fresh()
    i.rail("VBUS20", 20.0, 6.0, 8.0, "R11", loads={"R16": 6.0})
    try:
        i.rail("CH_ACN", 20.0, 9.0, 12.0, "R16", loads={"Q7": 9.0}, series_of="VBUS20")
    except SystemExit as e:
        assert "cannot carry more than the path" in str(e), str(e)
        return
    raise AssertionError("a segment declared more current than the path it belongs to and was accepted")


def t_a_node_is_not_something_a_segment_may_point_at():
    """DEFECTIVE: a node carries no watts, so excluding a segment against one loses the path's power."""
    i = _fresh()
    i.node("PD_VPWR", 15.0, "a profile ceiling")
    try:
        i.rail("PD_SW", 15.0, 3.0, 3.0, "Q27", loads={"R138": 3.0}, series_of="PD_VPWR")
    except SystemExit as e:
        assert "not a declared rail" in str(e), str(e)
        return
    raise AssertionError("a segment pointed at a node and the declaration was accepted")


def _thermal_rows(rails):
    """thermal.py's own accounting, run on a rail table with no board (the rows and the sum are pure)."""
    import thermal
    rows, total = [], 0.0
    for net, r in sorted(rails.items()):
        v = float(r.get("volts") or 0); amp = float(r.get("amps_peak") or 0)
        if v <= 0 or amp <= 0: continue
        if r.get("series_of"):
            rows.append((net, "segment")); continue
        total += v * amp; rows.append((net, "counted"))
    return rows, total


def t_thermal_counts_one_path_once():
    """Both fixtures in one: the same three conductors, declared as segments and not.

    Without the declaration the 160 W path is counted three times, which is the number the board's power
    figure would have carried; with it, once. The rule fails on the tool as it stood, because `series_of`
    did not exist and there was no way to say it.
    """
    import thermal
    assert "series_of" in open(os.path.join(TOOLS, "thermal.py")).read(), \
        "thermal.py does not know what a series segment is, so it cannot count a path once"
    path = {"FE_OUT": dict(volts=20.0, amps_peak=8.0),
            "VBUS20": dict(volts=20.0, amps_peak=8.0),
            "CH_ACN": dict(volts=20.0, amps_peak=8.0)}
    _, undeclared = _thermal_rows(path)
    assert abs(undeclared - 480.0) < 1e-6, undeclared      # the defect, stated as a number
    path["FE_OUT"]["series_of"] = "VBUS20"; path["CH_ACN"]["series_of"] = "VBUS20"
    rows, declared = _thermal_rows(path)
    assert abs(declared - 160.0) < 1e-6, declared
    assert sorted(rows) == [("CH_ACN", "segment"), ("FE_OUT", "segment"), ("VBUS20", "counted")], rows


def t_a_segment_is_still_a_rail_to_every_rule_that_reads_copper():
    """The declaration must not become an exemption: only thermal may look at it.

    `series_of` answers one question, whose power figure carries this conductor's watts. If any tool that
    judges COPPER learned to skip a segment, the declaration would undo the very fix it was written for.
    """
    import re
    for name in ("dc_drop.py", "derate.py", "via_current.py", "rail_crossings.py", "power_copper.py"):
        p = os.path.join(TOOLS, name)
        if not os.path.exists(p): continue
        src = open(p, encoding="utf-8").read()
        assert "series_of" not in src, \
            "%s reads series_of: a segment is a rail to every rule that judges copper, and only thermal may " \
            "exclude it from its power sum" % name
