#!/usr/bin/env python3
"""The stored-energy chain is checked, not drawn (rules BAT-002 and PWR-003, 16 September 2026).

Both rules are BLOCKERs and both read "no verification" on four boards: the chain crosses four boards with two
25 A blades, an XT60 and 12 AWG wiring, and nothing drew it end to end. A chain nobody has drawn is one whose
weakest stage is unknown, and the weakest stage is where a fault burns a conductor instead of opening a fuse.

The gate's own first run earned its keep: it refused the stage that carried the pack node's 18 A peak while
naming a 2 A eFuse as its protection, which is an element that opens in normal use. The stage was wrong, not
the check, and the chain now carries the eFused branches as their own stage.

Fixtures both ways for each of the four coordination tests, plus the committed chain, which must pass.
"""
import os, sys, tempfile, textwrap

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import energy_chain as E

GOOD = """
schema_version: "1.0.0"
stages:
 - id: ONE
   board: P
   from: "the cells"
   to: "the fuse"
   continuous_a: 10.0
   peak_a: 18.0
   conductor: {what: "a band", rating_a: 30.0, basis: "v2/vendor/battery/littelfuse-287-atof.pdf"}
   prospective_fault_a: {low: 100, high: 300, basis: "v2/vendor/battery/samsung-35e-orbtronic.pdf"}
   protection: {ref: F1, what: "25 A blade", rating_a: 25.0, interrupting_a: 1000.0, i2t_a2s: 1000.0,
                basis: "v2/vendor/battery/littelfuse-287-atof.pdf"}
   protects: null
"""


def _chain(text):
    d = tempfile.mkdtemp(prefix="chain-")
    p = os.path.join(d, "chain.yaml"); open(p, "w").write(text)
    return p


def _run(text, ecad=None):
    return E.check(_chain(text), ecad or tempfile.mkdtemp(prefix="noecad-"))


def t_the_acceptable_fixture_passes():
    r = _run(GOOD)
    assert not r["fails"], r["fails"]
    assert r["checked"] >= 6, r


def t_an_element_above_the_conductor_it_protects_is_refused():
    """The coordination, in one line: a fuse above its conductor's rating means the conductor is the fuse."""
    r = _run(GOOD.replace("rating_a: 30.0", "rating_a: 20.0"))
    assert any("the conductor is the fuse" in f or "only 20.0 A" in f for f in r["fails"]), r["fails"]


def t_an_element_below_the_paths_own_peak_is_refused():
    r = _run(GOOD.replace("rating_a: 25.0, interrupting_a", "rating_a: 12.0, interrupting_a"))
    assert any("opens in normal use" in f for f in r["fails"]), r["fails"]


def t_an_element_that_cannot_interrupt_the_fault_is_refused():
    r = _run(GOOD.replace("interrupting_a: 1000.0", "interrupting_a: 100.0"))
    assert any("interrupts" in f for f in r["fails"]), r["fails"]


def t_a_number_whose_source_is_not_in_the_tree_is_refused():
    """A rating whose basis file is not here is not a rating, it is a claim."""
    r = _run(GOOD.replace("v2/vendor/battery/samsung-35e-orbtronic.pdf", "v2/vendor/battery/does-not-exist.pdf"))
    assert any("not in this tree" in f for f in r["fails"]), r["fails"]


def t_a_citation_is_not_refused_for_its_punctuation():
    """The gate's own first run refused two true citations for a trailing colon and a trailing `);`, which is
    the false positive this project spent the morning removing from derate.py."""
    r = _run(GOOD.replace("basis: \"v2/vendor/battery/littelfuse-287-atof.pdf\"",
                          "basis: \"see v2/vendor/battery/littelfuse-287-atof.pdf, Ratings table);\""))
    assert not [f for f in r["fails"] if "not in this tree" in f], r["fails"]


def t_a_broken_chain_is_refused():
    r = _run(GOOD.replace("protects: null", "protects: NOWHERE"))
    assert any("not a stage" in f for f in r["fails"]), r["fails"]


def t_the_committed_chain_passes_every_check():
    """The chain this project ships, judged in this tree. It is the acceptable fixture that matters."""
    r = E.check()
    assert not r["fails"], r["fails"]
    assert r["stages"] >= 8 and r["checked"] >= 50, r


def t_a_tree_without_the_vendor_library_leaves_the_citations_unjudged():
    """16 September 2026, found in the sweep within minutes of the gate landing: the sweep runs in a tree
    archived from v2/ecad alone, so every basis file read as missing and eleven TRUE citations were reported as
    failures. A missing library says nothing about whether a fuse is above its conductor, so the coordination
    is judged as always and the citations are counted as unjudged, which is neither a pass nor a failure."""
    r = E.check(vendor="/nonexistent-vendor-library")
    assert not r["fails"], r["fails"]
    assert r["unjudged_citations"] > 0 and r["vendor_seen"] is False, r
    assert any("vendor library is not in this tree" in n for n in r["notes"]), r["notes"]


def t_an_empty_vendor_library_is_not_the_same_as_an_absent_one():
    """A folder that EXISTS and does not hold the file is a citation that does not resolve, which is the thing
    the check is for. Only the absence of the library itself is unjudgeable."""
    import tempfile
    r = E.check(vendor=tempfile.mkdtemp(prefix="empty-vendor-"))
    assert r["fails"] and r["vendor_seen"] is True, r
