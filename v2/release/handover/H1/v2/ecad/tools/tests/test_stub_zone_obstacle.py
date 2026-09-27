#!/usr/bin/env python3
"""A filled pour of another net is an obstacle, and until 16 September 2026 not one was in the map.

The stub router's obstacle map took tracks, vias, pads and rule areas. It did not take FILLED ZONES, so a
closure was free to run straight through a ground plane, which on board A is most of the board. The closures
were not silently accepted: they were laid, KiCad's connectivity was asked, and the count went UP, because a
short merges clusters and the ratsnest explodes (/POE_EN 13 unconnected to 114, /PD_EN 13 to 79). Every piece
came back off under a message blaming the goal cell. The tool had been searching a board it could not see and
its own guard was the only thing between that and a shorted board.

The structural rules here are cheap and they hold the shape: the zone loop must not stop at rule areas, the
same net's own pour must never be an obstacle (it is the target), and the fast rasteriser must keep holes out
of the fill (matplotlib fills every sub-path whatever its winding, which cost the pre-router a day on
10 September)."""
import os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "stub_router.py"), encoding="utf-8").read()


def t_a_filled_pour_of_another_net_is_in_the_obstacle_map():
    """...BY DEFAULT, which is the half that matters (18 September 2026). The pour branch grew a flag so the
    PRE-LAY stage can take the pours out of the map (nothing is routed yet and the chain re-fills before it
    judges anything); a finish must never do that, because it is what shorted board A's ground. So the rule
    reads the whole zone block, not a fixed number of characters of it - the first version sliced 2,500 and the
    comment explaining the flag pushed the assertion out of its own window - and it requires the default to be
    ON."""
    assert "GetFilledPolysList" in SRC, "no filled zone reaches the stub router's obstacle map"
    i = SRC.index("for z in b.Zones():")
    seg = SRC[i:SRC.index("for d in b.GetDrawings():", i)]
    assert "GetFilledArea()" in seg, "the zone loop does not look at the fill"
    assert "zpoly(trk[" in seg and "zpoly(via" in seg, "a pour blocks neither tracks nor vias"
    assert 'STUB_POUR_OBSTACLE", "1"' in SRC, "the pour obstacle can be turned off and its default is not ON"


def t_the_boards_own_net_is_a_target_and_never_an_obstacle():
    """The pour of the net being closed is the thing the closure is trying to REACH. It moved behind
    `_want_zone` when the map learnt to count (19 September 2026), so this asks the predicate rather than the
    line the skip used to be written on; what it has always been about is that the two names are compared
    NORMALISED, because a pour's net reads `/GND` or `GND` depending on how the zone was made and an unequal
    comparison would put the net's own copper in its own way."""
    i = SRC.index("GetFilledArea() <= 0")
    seg = SRC[i:i + 200]
    assert "_want_zone(z.GetNetname())" in seg, \
        "the net being closed would be blocked by its own pour, which is the thing it is trying to reach"
    import ast
    fn = next((n for n in ast.walk(ast.parse(SRC))
               if isinstance(n, ast.FunctionDef) and n.name == "_want_zone"), None)
    assert fn is not None, "the predicate that decides whether a pour is this net's own is gone"
    body = ast.get_source_segment(SRC, fn) or ""
    assert "netname(zn)" in body and "netname(net)" in body, \
        "a pour's net is compared unnormalised, so `/GND` and `GND` read as two different nets"


def t_the_fast_rasteriser_subtracts_its_holes():
    i = SRC.index("def zpoly(")
    seg = SRC[i:SRC.index("\n\n\n", i)]
    assert "HoleCount" in seg and "&= ~" in seg, \
        "holes are not subtracted: matplotlib fills every sub-path whatever its winding, so the pour would come out solid"
    assert "return poly(mask, sps, grow)" in seg, "there is no fallback where matplotlib is absent"


def t_the_rule_area_branch_still_ends_where_it_did():
    """A rule area is not a pour and must not fall through into the fill branch."""
    i = SRC.index("if z.GetIsRuleArea():")
    seg = SRC[i:i + 700]
    assert "continue" in seg, "a rule area falls through into the filled-zone branch"
