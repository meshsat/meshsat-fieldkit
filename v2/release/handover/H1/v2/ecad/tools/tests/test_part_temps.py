#!/usr/bin/env python3
"""A part's own operating range against the envelope this project adopted (rule CMP-001, 21 September 2026).

The envelope was adopted on 21 September and nothing in this project compared a part to it: CMP-001 is written
about absolute maximum ratings and `derate.py` reads voltage alone. The first part read under the new envelope
was outside it, which is why this exists.

THE DEFECTIVE FIXTURE is a part rated from 0 C on a kit whose ambient floor is -20: it must be reported as
outside its own range, with the number of kelvin. THE ACCEPTABLE FIXTURES are the two ways a part is not a
failure: a range that covers the envelope, and a part the envelope's own carve-out declares (the e-paper below
-15 C), which is REPORTED and never silently passed.

The fourth rule holds the thing this tool must never do: invent a range. A part with no row is UNDECLARED and
counted, and the verdict stays advisory while thirty of nearly two thousand part instances carry a range.
"""
import os
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)


def _files():
    import yaml
    return (yaml.safe_load(open(os.path.join(TOOLS, "pcb_envelope.yaml"), encoding="utf-8")),
            yaml.safe_load(open(os.path.join(TOOLS, "pcb_part_temps.yaml"), encoding="utf-8")))


def t_a_part_that_is_outside_the_envelope_at_the_cold_end_is_reported():
    """The defective fixture, and it is the real one: board B's T1 is a 0 to +70 C magnetics module."""
    import part_temps as PT
    env, decl = _files()
    res, _m, _w = PT.judge(env=env, parts=decl, only="b")
    fails = res["b"]["fails"]
    assert any("T1" in f and "coldest 20 K" in f for f in fails), \
        "the 0 to +70 C part on a -20 C envelope was not reported: %s" % fails[:3]


def t_a_part_whose_range_covers_the_envelope_passes():
    """The acceptable fixture: the same board's compute modules are -20 to +85 C parts and must not appear."""
    import part_temps as PT
    env, decl = _files()
    res, inside_max, _w = PT.judge(env=env, parts=decl, only="b")
    rows = [r for r in res["b"]["rows"] if "Compute Module" in r["part"]]
    assert rows, "the compute modules were not matched at all, so this fixture proves nothing"
    assert all(r["min_c"] <= env["ambient_c"]["in_use"]["min"] and r["max_c"] >= inside_max for r in rows), rows[:2]
    assert not [f for f in res["b"]["fails"] if "Compute Module" in f], res["b"]["fails"][:2]


def t_a_declared_carve_out_is_reported_and_never_silently_passed():
    """The e-paper is outside its range below -15 C and the envelope says what happens; the reading has to
    carry the envelope's own words rather than dropping the part from the list."""
    import part_temps as PT
    env, decl = _files()
    res, _m, _w = PT.judge(env=env, parts=decl, only="c")
    notes = res["c"]["notes"]
    assert any("e-paper" in n and "degraded display" in n for n in notes), notes[:2]
    assert not [f for f in res["c"]["fails"] if "e-paper" in f], "a declared carve-out was failed instead of reported"


def t_a_part_with_no_published_range_is_counted_and_never_assumed():
    """The gap is this file's, not the board's, and the tool has to say so: an undeclared part is counted and
    the verdict stays advisory while the declared set is a fraction of the components."""
    import part_temps as PT
    env, decl = _files()
    res, _m, _w = PT.judge(env=env, parts=decl)
    undec = sum(len(v["undeclared"]) for v in res.values())
    judged = sum(len(v["rows"]) for v in res.values())
    assert undec > judged, "the declaration covers more than it can, which this rule did not expect"
    src = open(os.path.join(TOOLS, "part_temps.py"), encoding="utf-8").read()
    assert "advisory=True" in src, "the verdict is not advisory while the denominator is this small"
    # and the cells, whose sheet this tree does not hold, are in the owed list with their reason
    assert any("cells" in str(o.get("name", "")) for o in decl.get("owed", [])), decl.get("owed")


def t_the_hot_bar_comes_from_the_envelopes_own_carve_out():
    """The worst inside air is not the ambient maximum plus the loaded rise: the envelope's carve-out runs the
    reduced mode above +35 C, so the bar is the larger of 40 + 10 and 35 + 16, and the tool must compute it
    from the data rather than carry a literal."""
    import part_temps as PT
    env, _decl = _files()
    m, why = PT.inside_air_max(env)
    assert m == 51, m
    assert "reduced mode" in why, why
    src = open(os.path.join(TOOLS, "part_temps.py"), encoding="utf-8").read()
    assert "= 51" not in src, "the inside-air bar is a literal in the tool"
