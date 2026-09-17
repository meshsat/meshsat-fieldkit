#!/usr/bin/env python3
"""A part's pin map judged against its own LAND (MESHSAT-862, 17 September 2026).

`ic()` has refused an unlisted pin since 10 September and every part written another way was still trusted. Board
E's Q7, the hot-swap pass FET on the shore and vehicle DC entry, is a CSD19532Q5B on a PowerPAK SO-8, whose pads
are 1, 2, 3 SOURCE, 4 GATE and 5 DRAIN. It was written with the three-pin Q_NMOS_GDS map, so the GATE net and the
DRAIN net landed on two SOURCE pins, the real gate and the whole drain tab carried nothing, and the assembled part
would have tied HS_GATE, HS_S and DC_HS together through its own source metal with no gate drive at all: the
LM5069's inrush limiting and overcurrent protection would not have existed on a board that is finished copper.

Board A met the same trap on 7 September (appendix 32.36) and fixed its own helper. Nothing held the two together,
so the rule is now the engine's: every distinct pad number a land carries takes a net or the word NC.

The fixtures use this project's OWN library, which travels with the tree, so they run on the runner as well as
where KiCad is.
"""
import os, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)


def _kisch():
    import kisch
    kisch.P.clear(); kisch._LANDS.clear(); kisch.UNCHECKED.clear(); del kisch.PHANTOM[:]
    return kisch


def t_a_map_that_misses_a_pad_of_its_own_land_is_refused():
    """THE DEFECTIVE FIXTURE: board E's Q7 in miniature, a map naming three of a land's eight pads."""
    kisch = _kisch()
    pads = kisch.land_pads("meshsat:PogoTargets_2x4")
    assert pads and len(pads) == 8, "the fixture's own land did not resolve: %r" % (pads,)
    try:
        kisch.part("X1", "Connector_Generic", "Conn_01x03", "a three-pin map on an eight-pad land",
                   "meshsat:PogoTargets_2x4", {"1": "A", "2": "B", "3": "C"})
    except SystemExit as e:
        assert "4" in str(e) and "does not name" in str(e), "refused for the wrong reason: %s" % e
        return
    raise AssertionError("a map naming three of eight pads was accepted")


def t_a_map_that_names_every_pad_passes_and_NC_is_a_real_answer():
    """THE ACCEPTABLE FIXTURE: the same land with every pad named, one of them a deliberate no-connect."""
    kisch = _kisch()
    nets = {str(i): "N%d" % i for i in range(1, 8)}
    nets["8"] = "NC"
    kisch.part("X2", "Connector_Generic", "Conn_01x08", "every pad named", "meshsat:PogoTargets_2x4", nets)
    assert kisch.P and kisch.P[-1]["ref"] == "X2", "a complete map was refused"


def t_a_net_that_lands_on_no_pad_of_the_part_is_refused():
    """A map pin the land does not carry lands nowhere. It is harmless where the same net also sits on a pad the
    land HAS (board E's TDSON-8 FETs name 5, 6, 7, 8 for a drain the land merges into pad 5) and it is a refusal
    where it does not, because then the net never reaches the part at all."""
    kisch = _kisch()
    nets = {str(i): "N%d" % i for i in range(1, 9)}
    nets["9"] = "ONLY_HERE"
    try:
        kisch.part("X3", "Connector_Generic", "Conn_01x09", "a net on a pad that does not exist",
                   "meshsat:PogoTargets_2x4", nets)
    except SystemExit as e:
        assert "ONLY_HERE" in str(e) and "never reaches" in str(e), "refused for the wrong reason: %s" % e
        return
    raise AssertionError("a net whose only pin has no pad was accepted")


def t_a_phantom_pin_beside_a_real_one_is_reported_and_not_refused():
    kisch = _kisch()
    nets = {str(i): "N%d" % i for i in range(1, 9)}
    nets["9"] = "N8"                       # the same net as pad 8, which the land does have
    kisch.part("X4", "Connector_Generic", "Conn_01x09", "a merged pad written out", "meshsat:PogoTargets_2x4", nets)
    assert any(r[0] == "X4" and r[3] == "9" for r in kisch.PHANTOM), \
        "the phantom pin was neither refused nor reported: %r" % (kisch.PHANTOM,)


def t_the_engine_checks_every_part_and_the_layout_says_what_it_could_not_judge():
    s = open(os.path.join(TOOLS, "kisch.py"), encoding="utf-8").read()
    assert "check_land(ref, value, _fp, _nets)" in s, "part() no longer judges the map against the land"
    l = open(os.path.join(TOOLS, "schlayout.py"), encoding="utf-8").read()
    assert "_lands()" in l and "KISCH_LANDS_STRICT" in l, \
        "the layout stage neither reports the land check nor refuses when a land could not be read"


def t_board_e_writes_its_power_fets_on_the_five_pad_map():
    """The fix at the source, in the file that carried the defect."""
    s = open(os.path.join(TOOLS, "gen_sch_e.py"), encoding="utf-8").read()
    i = s.index("def nfet(")
    region = s[i:i + 2000]
    assert '{"1": s, "2": s, "3": s, "4": g, "5": d}' in region, \
        "board E's FET helper does not put the source on 1, 2, 3, the gate on 4 and the drain on 5"
    call = [l for l in region.split("\n") if "part(" in l and "Conn_01x05" in l]
    assert call, "the helper does not write the five-pad connector symbol board A uses for this land"
    assert "Q_NMOS_GDS" not in call[0], "the three-pin symbol is still used on a five-pad land"
