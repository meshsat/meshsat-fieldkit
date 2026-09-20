#!/usr/bin/env python3
"""An exposed pad's thermal vias, and the thing that was refusing all of them.

MESHSAT-862, 12 September 2026, found on board P during the orderability pass. The chain printed
`4 thermal via(s) refused for what is on the other side` for two runs and nobody could say which pad or
why. The answer: KiCad draws a modern exposed pad as ONE copper pad plus a grid of SOLDER PASTE
apertures, and an aperture is a pad too, on F.Paste only, with no number and no net. `escape.py`'s
`clear()` read the BQ4050's nine apertures as pads of another net and refused all four thermal vias of
the exposed pad they belong to, on every board carrying such a land.

What that cost on P: the gas gauge and primary protector finished with the ONE via `zone_pad_via.py`
rescues at the pad centre, the router then ran three `/BAT_F` segments 0.51 mm from it on B.Cu, the
ground fill retreated by its clearance, and a QFN-32 exposed pad ended with no ground connection to the
bottom layer at all. `check_pcb_p` refused the board for it, one failure of 143 on a board that is
0 hard and 0 unrouted.
"""
import os, re, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)


def _src(name):
    return open(os.path.join(TOOLS, name), encoding="utf-8").read()


def t_a_paste_aperture_is_not_an_obstacle_to_a_via():
    """The obstacle list is built from pads that exist on copper. A pad on F.Paste alone is solder
    stencil, not metal, and blocks nothing."""
    s = _src("escape.py")
    assert "_is_copper" in s, "escape.py no longer filters its obstacle pads by copper layer"
    m = re.search(r"allpads = \[(.*?)\]\n", s, re.S)
    assert m, "allpads is not where this rule expected it"
    assert "if _is_copper(p)" in m.group(1), \
        "allpads takes every pad again, paste apertures included: %s" % m.group(1)[-120:]
    assert "IsCopperLayer" in s, "the copper test is not asked of the layer set"


def t_a_refused_thermal_via_names_its_pad_and_what_it_hit():
    """A count is not a diagnosis. `escape.py` printed only how many vias it refused, so two runs of
    board P reported the same four and neither said which pad lost them."""
    s = _src("escape.py")
    assert "ep_pads" in s and "exposed pad %s.%s" in s, \
        "escape.py reports a refusal count and not which exposed pad lost which via"
    assert "NO VIA AT ALL" in s, "an exposed pad that ends with no thermal via at all is not called out"
    assert "LAST[0]" in s.split("ep_why.append")[1][:120], \
        "the refusal reason clear() already recorded is not carried into the report"


def t_a_via_is_alive_only_where_both_of_its_ends_are():
    """`stitch_prune` kept a via because two tracks landed on it; both were on F.Cu and the via spans
    F.Cu to B.Cu, so its pour end was dead, which is the exact defect the tool exists for."""
    s = _src("stitch_prune.py")
    assert "TopLayer()" in s and "BottomLayer()" in s, \
        "stitch_prune still counts tracks without asking which of the via's two ends they are on"
    assert "ends_on(pos, net, layer=L)" in s, "the track test is not per layer"
    assert "def pad_at(pt, net, layer=None)" in s, \
        "the pad test is not per layer, so a pad on one side declares the other side live"


def t_the_via_site_search_also_knows_that_paste_is_not_copper():
    """THE SAME DEFECT IN A SECOND TOOL, five days later (17 September 2026). `return_via._site_free` is
    the one site test behind three rules: PLC-001 through `place_audit` (has this plane pad anywhere to
    go), RET-004 through `return_via` itself, and PLC-002 through `gnd_grid`. It walked every pad of
    every footprint and skipped only pads of its OWN net, and an aperture carries no net at all, so one
    sitting 0.11 mm from the middle of the pad it belongs to refused the site. Board A's three TPS2596
    eFuses read `no via site` for their own thermal pads on a board whose ground plane is directly
    underneath them, which is a PLC-001 failure about the tool rather than about the board."""
    s = _src("return_via.py")
    body = s.split("def _site_free")[1].split("\ndef ")[0]
    assert "IsOnCopperLayer" in body, \
        "_site_free takes every pad again, paste apertures included, so no exposed pad can hold a via"
    assert 'GetNumber() == ""' in body, "the unnumbered aperture is not named as what it is"


def t_the_fanout_also_knows_that_paste_is_not_copper():
    """THE SAME DEFECT IN A THIRD TOOL, eight days later (20 September 2026). `prefanout.py` builds its
    obstacle list from every pad of every footprint with no copper test at all, so an exposed pad's paste
    grid reads as a crowd of OTHER-net pads and each one takes 0.5 mm of lane away from every fanout
    candidate near it. It is the same sentence as 32.151 and 32.218 and it is worth stating once more:
    a pad that exists on no copper layer is not an obstacle to anything."""
    s = _src("prefanout.py")
    m = re.search(r"allpads = \[(.*?)\]\n", s, re.S)
    assert m, "prefanout.py no longer builds an allpads list"
    assert "if _is_copper(p)" in m.group(1), \
        "the fanout's obstacle list takes every pad again, paste apertures included"
    assert "IsCopperLayer" in s, "the copper test is not asked of the layer set"


def t_a_fanout_stub_may_not_cross_another_nets_copper():
    """20 September 2026, appendix 32.270, and it cost a placement change that read free. The dense sample
    along a fanout stub tested TRACKS only, on the reasoning that `crossing a laid track is the defect;
    passing a pad is not`. Passing is not, OVERLAPPING is: two locked GND stubs left their own FET's
    ground pad at forty-five degrees and clipped their own part's drain tab by sixty-five micrometres,
    with the via and all three sample points clear, and board A's whole chain blocked on four hard items.
    The lane rule of 9 September is untouched and still decides at the three sample points; what is added
    is the board's own clearance against another net's POLYGON, because a circle around a 3.81 by 3.91 mm
    drain tab would refuse every stub that passes beside it."""
    s = _src("prefanout.py")
    body = s.split("def _crosses")[1].split("\n                if clear(")[0]
    assert "Collide" in body, "the dense sample still tests tracks only, so a stub may cross a pad"
    assert "INPAD_CLR" in body, "the dense pad test is not at the board's own clearance"
    assert "FromMM(0.5)" not in body, \
        "the dense sample took the LANE rule with it, which 9 September measured at 18 fanout vias"


def t_a_refused_thermal_site_says_what_is_already_on_the_pad():
    """20 September 2026, board A's Q2. All four of its thermal sites read `via(/VIN_RAW)`, which is the
    0.3 mm hole-to-hole rule against a via of the pad's OWN net, and the line said `got 0 thermal via(s)
    of 4` for a tab that already carried SIX vias inside it and two more touching. A count is not a
    diagnosis and a refusal by the pad's own copper is not a gap: the refusals still travel, and the
    number already there travels beside them, because that is what separates a stitched pad from a bare
    one. The `NO VIA AT ALL` marker belongs only to a pad that has none either way."""
    s = _src("escape.py")
    assert "already on the pad" in s, "the thermal report no longer says what is on the pad"
    tail = s.split("for ref, num, net, laid, want, why")[1]
    assert "laid or have" in tail, \
        "the NO VIA AT ALL marker is printed for a pad that is already stitched by its own net"


def t_the_thermal_vias_are_asked_of_every_footprint_and_not_only_the_fine_pitch_ones():
    """The exposed-pad block sat INSIDE the fine-pitch loop (17 September 2026, appendix 32.218), so a PowerPAK
    SO-8, a SOIC-8 with a tab or a WSON-6 was never asked: 32 of board A's 39 exposed pads carried no via on the
    cut A32. It is a function now, called once in the fine-pitch loop and once in a loop over the coarse parts."""
    s = _src("escape.py")
    assert "def thermal_vias(fp):" in s, "the exposed-pad block is not a function any loop can call"
    assert s.count("    thermal_vias(fp)") >= 2, "thermal_vias is called from fewer than two loops: the coarse parts are not asked"
    i = s.index("# THE COARSE PARTS")
    assert "if is_fine(fp)" in s[i:i + 600] and "thermal_vias(fp)" in s[i:i + 900], \
        "the coarse-part loop does not skip the fine parts and call thermal_vias"


def t_a_two_terminal_part_has_no_tab_and_a_tab_is_the_largest_pad_by_a_margin():
    """Asked of every footprint (18 September 2026, B22's first pre-route), the size test alone read a power
    inductor's two pads and a 2512 resistor's pads as exposed pads wanting a thermal via: a tab is at least twice
    the footprint's median pad and the footprint has at least three."""
    s = _src("escape.py")
    i = s.index("def thermal_vias(fp):")
    body = s[i:i + 6000]
    assert "len(_areas) < 3" in body and "2 * _areas[len(_areas) // 2]" in body, \
        "thermal_vias does not require a tab to be the largest pad by a margin on a part with three or more pads"
