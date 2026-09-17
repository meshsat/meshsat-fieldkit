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


# ---------------------------------------------------------------- the selection criteria (ECSS-Q-ST-30-11C Rev.2 6.17)
# Rules PWR-003 and BAT-002 carried "no authority for the SELECTION CRITERIA" from the day the registry was
# written: the fuses' own datasheets name SAE J1284 and ISO 8820-3, neither is free, and the makers' guides sit
# behind a host that refuses this one. ECSS publishes a derating standard free, from a body this project
# already cites twice, and clause 6.17 is the criterion. Transcribed in
# v2/vendor/standards/ecss-q-st-30-11c-rev2-2021-06-23.md.

FUSED = GOOD.replace('protection: {ref: F1, what: "25 A blade"',
                     'protection: {ref: F1, kind: fuse, what: "25 A blade"')


def t_a_fuse_inside_the_published_derating_is_a_note_and_not_a_failure():
    """10 A of a 25 A fuse is 40 percent, inside Table 6-17's 65."""
    r = _run(FUSED)
    assert not r["derate_fails"], r["derate_fails"]
    assert any("inside the 65 percent" in n for n in r["notes"]), r["notes"]


def t_a_fuse_past_the_published_derating_with_no_justification_is_refused():
    """20 A of a 25 A fuse is 80 percent. The standard states its number for CERMET fuses and 6.17.1a requires
    another technology's derating to be JUSTIFIED, so the gate asks for that justification rather than either
    failing a blade fuse against a limit the standard does not set for it or passing it against nothing."""
    r = _run(FUSED.replace("continuous_a: 10.0", "continuous_a: 20.0"))
    assert any("65 percent" in f and "derating_basis" in f for f in r["derate_fails"]), r["derate_fails"]
    assert not r["fails"], "a selection finding is PWR-003's and must not fail the chain's own end-to-end rule: %s" % r["fails"]


def t_the_same_fuse_with_a_written_justification_passes():
    r = _run(FUSED.replace("continuous_a: 10.0",
                           'continuous_a: 20.0\n   derating_basis: "the blade fuse maker rates this holder for '
                           'continuous duty at 80 percent to 70 C and the case never reaches it"'))
    assert not r["derate_fails"], r["derate_fails"]
    assert any("the board declares why" in n for n in r["notes"]), r["notes"]


def t_a_source_that_cannot_deliver_three_times_the_rating_is_refused():
    """ECSS 6.17.3c, and it is technology-independent: a fuse the source cannot blow quickly is not protection.
    50 A at worst against a 25 A fuse is twice, not three times."""
    r = _run(FUSED.replace("low: 100,", "low: 50,"))
    assert any("three times" in f for f in r["derate_fails"]), r["derate_fails"]


def t_an_unknown_fault_current_is_named_and_not_assumed():
    r = _run(FUSED.replace("low: 100,", "low: 0,"))
    assert any("is not established" in n for n in r["notes"]), r["notes"]
    assert not r["derate_fails"], r["derate_fails"]


def t_each_board_is_judged_on_its_own_stages():
    """One board's fuse at 80 percent failed two BLOCKER rules on four boards before the split."""
    two = FUSED + """
 - id: TWO
   board: E
   from: "the inlet"
   to: "the bus"
   continuous_a: 8.0
   peak_a: 10.0
   conductor: {what: "a band", rating_a: 12.0, basis: "v2/vendor/battery/littelfuse-287-atof.pdf"}
   prospective_fault_a: {low: 100, high: 300, basis: "v2/vendor/battery/samsung-35e-orbtronic.pdf"}
   protection: {ref: F9, kind: fuse, what: "10 A blade", rating_a: 10.0, interrupting_a: 1000.0,
                basis: "v2/vendor/battery/littelfuse-287-atof.pdf"}
   protects: ONE
"""
    r = _run(two)
    assert r["by_board"].get("p") == ["ONE"], r["by_board"]
    assert r["by_board"].get("e") == ["TWO"], r["by_board"]
    mine = [f for f in r["derate_fails"] if f.split(":")[0].strip() in r["by_board"]["e"]]
    assert mine and not [f for f in r["derate_fails"] if f.split(":")[0].strip() in r["by_board"]["p"]], r["derate_fails"]


def t_the_authority_is_in_the_tree_and_the_gate_names_it():
    src = open(os.path.join(TOOLS, "energy_chain.py"), encoding="utf-8").read()
    assert "ECSS-Q-ST-30-11C Rev.2" in src, "the gate does not name the standard its number comes from"
    doc = os.path.join(os.path.dirname(os.path.dirname(TOOLS)), "vendor", "standards",
                       "ecss-q-st-30-11c-rev2-2021-06-23.md")
    assert os.path.exists(doc), "the transcribed clauses are not in the tree: %s" % doc
    t = open(doc, encoding="utf-8").read()
    assert "65 %" in t and "6.17.3" in t and "sha256" in t, "the transcription is missing its number or its provenance"


# ---------------------------------------------------------------------------------------------------------
# THE FUSE MAKER'S OWN DERATING (rule PWR-003, 17 September 2026).
#
# ECSS-Q-ST-30-11C Rev.2 Table 6-17 gives 65 percent for a fuse and its own 6.17.1a says that row is stated
# for Cermet and that another technology's derating shall be JUSTIFIED. Board E's shore inlet carries 8 A of a
# 10 A automotive blade fuse, which is 80 percent, and it read FAIL against a number nobody wrote for a blade
# fuse. The justification is published in the datasheet this tree already holds, as a table of allowed load
# against ambient, and it is read here instead of being paraphrased.

def t_the_table_is_read_at_the_next_higher_published_column():
    import energy_chain as E
    t = E.derating_tables()["atof287"]
    assert E.allowed_load(t, 10.0, 20) == (10.0, 20.0), E.allowed_load(t, 10.0, 20)
    assert E.allowed_load(t, 10.0, 56) == (8.0, 65.0), "56 C must be read at the 65 C column, never interpolated"
    assert E.allowed_load(t, 10.0, 65) == (8.0, 65.0)
    assert E.allowed_load(t, 10.0, 66) == (7.0, 85.0)


def t_an_ambient_past_the_last_column_has_no_answer():
    """A fuse judged against a number nobody published is what this file exists to stop."""
    import energy_chain as E
    t = E.derating_tables()["atof287"]
    assert E.allowed_load(t, 10.0, 130) == (None, None)
    assert E.allowed_load(t, 12.0, 20) == (None, None), "a rating the maker does not publish has no figure"


def t_the_transcribed_table_still_matches_the_datasheet_in_this_tree():
    """THE TRANSCRIPTION GUARD. The first draft of pcb_fuse_derating.yaml was typed by eye and nine of its
    thirteen rows were shifted one column, which reads a 15 A fuse's 20 degree figure as its 65 degree one.
    The table is re-extracted from the PDF here, so a typed number cannot drift from the document."""
    import subprocess, re, os, energy_chain as E
    pdf = os.path.join(os.path.dirname(os.path.dirname(TOOLS)), "vendor", "battery", "littelfuse-287-atof.pdf")
    if not os.path.isfile(pdf): raise AssertionError("the ATOF datasheet is not in the tree: %s" % pdf)
    try:
        txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    except FileNotFoundError:
        return                                  # no pdftotext on this host: the other rules still hold
    pat = re.compile(r"(?<![\d.])(1|2|3|4|5|7\.5|10|15|20|25|30|35|40)A\s+((?:\d+\s+){6}\d+)(?!\d)")
    got = {float(m.group(1)): [int(x) for x in m.group(2).split()] for m in pat.finditer(txt)}
    assert len(got) == 13, "the datasheet's own table did not read back: %d row(s)" % len(got)
    have = (E.derating_tables()["atof287"].get("ratings") or {})
    for rating, row in got.items():
        mine = have.get(rating) or have.get(int(rating) if rating == int(rating) else rating)
        assert mine == row, "the %s A row here is %s and the datasheet says %s" % (rating, mine, row)


def t_a_stage_naming_a_table_and_no_ambient_is_refused():
    """The table is a function of ambient; naming it without one would be an exemption wearing a citation."""
    r = _run(FUSED.replace("continuous_a: 10.0",
                           "continuous_a: 20.0\n   derating: {table: atof287}"))
    assert any("no ambient" in f for f in r["derate_fails"]), r["derate_fails"]


def t_a_stage_naming_a_table_nobody_publishes_is_refused():
    r = _run(FUSED.replace("continuous_a: 10.0",
                           "continuous_a: 20.0\n   derating: {table: madeup99, ambient_c: 40}"))
    assert any("no such table" in f for f in r["derate_fails"]), r["derate_fails"]


def t_the_makers_table_decides_where_it_exists_and_refuses_an_overload():
    """25 A fuse, 20 A continuous: 80 percent, which the ECSS Cermet row refuses. The maker's own 25 A row is
    23 A at its 20 C column and 19 A at its 65 C column, so the SAME load is a pass in a cool place and a
    failure in a warm one, which is the whole point of reading the table rather than a percentage."""
    ok = _run(FUSED.replace("continuous_a: 10.0",
                            "continuous_a: 20.0\n   derating: {table: atof287, ambient_c: 18}"))
    assert not ok["derate_fails"], ok["derate_fails"]
    assert any("allows 23.0 A at its 20 C column" in n for n in ok["notes"]), ok["notes"]
    bad = _run(FUSED.replace("continuous_a: 10.0",
                             "continuous_a: 20.0\n   derating: {table: atof287, ambient_c: 60}"))
    assert any("allows 19.0 A at its 65 C column" in f for f in bad["derate_fails"]), bad["derate_fails"]


def t_the_shore_inlet_passes_on_the_maker_s_figure_and_says_it_has_no_margin():
    """The acceptable fixture AND the honest reading: 8.0 A against the 8.0 A the maker allows at 65 C is a
    pass with nothing left, and it must not read like a pass at 40 percent."""
    import subprocess, sys, os
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "energy_chain.py")],
                       capture_output=True, text=True, cwd=TOOLS)
    out = r.stdout
    assert "SHORE_INPUT: F1 carries 8.0 A where atof287 allows 8.0 A at its 65 C column" in out, out[-1500:]
    assert "no margin against the maker's own figure" in out, out[-1500:]
