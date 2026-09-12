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
