"""A pour born without a via refuses the placement (21 September 2026).

place_audit's island line was a WARN and it named board A's defect on every chain from A87 to A92: each rail's
In3 run ended in a column KiCad had renamed to GND (it sat in the load capacitor's ground pad), so the six load
bank islands carried no via of their own net before any route and the run dead-ended a layer below them. The
WARN was printed six times and read by nobody. Measured across the set before the bar moved: zero on every clean
chain (A85, A86, A93, B23, C24, D27, D30, E30, P9), 6 to 9 on exactly the defective arms, one VBAT In2 piece on
A69 and A70. So the line is a refusal now, with the erc-allow idiom (`pour-island-allow.txt` beside the board
names a net and says why).
"""
import os
from harness import Skip
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(os.path.dirname(HERE), "place_audit.py"), encoding="utf-8").read()


def t_an_islanded_pour_before_the_route_is_a_refusal_and_not_a_warning():
    body = SRC[SRC.index("    if _isl:"):SRC.index("    elif _zones and not _unfilled")]
    assert "WARN  %d pour island(s) already carry no via" not in body, "the islanded pour is still a warning nobody reads"
    assert 'lines.append("FAIL  %d pour island(s) already carry no via or plated pad of their own net BEFORE any' in body, \
        "the islanded pour does not fail the placement"
    assert "coll += 1" in body, "the refusal does not reach the verdict: coll is what decides place_audit's exit"


def t_a_known_island_is_declared_beside_the_board_and_still_counted():
    body = SRC[SRC.index("    if _isl:"):SRC.index("    elif _zones and not _unfilled")]
    assert 'pour-island-allow.txt' in body, "there is no way to declare a known islanded pour"
    assert 'lines.append("ALLOW %d pour island(s)' in body, "an allowed island is not reported"
    # the allow line names the NET, matched against the island's own "<net> on <layer>" prose, never a substring of a reason
    assert 'i.split(" on ")[0] == l.split()[0].lstrip("/")' in body, "an allow line does not match on the net name"
    # and no board of the set declares one today: the count is zero on every clean chain, which is the measurement
    for L in "abcdep":
        for d in os.listdir(os.path.join(os.path.dirname(HERE), "..")):
            if d.startswith("pcb-") and os.path.isfile(os.path.join(os.path.dirname(HERE), "..", d, "pour-island-allow.txt")):
                raise AssertionError("%s declares an islanded pour; the set read zero when the bar moved, so say why in the file and here" % d)


def t_a_site_on_the_islands_own_boundary_is_on_the_island():
    """21 September 2026, D31: a 1 mm2 piece of board D's F.Cu ground pour between R15 and R13 was refused as copper
    nothing reaches while its one connection, R15's ground pad with the fanout's via in it, sat on the island's top
    edge to the micrometre; PointInside answers False on the outline itself and KiCad's own fill had marked the
    polygon connected. A via or pad centre within 0.1 mm of the outline is on the island."""
    body = SRC[SRC.index("    _isl, _padonly, _unfilled, _zones"):SRC.index("    n_esc = sum(")]
    assert "_ON = 100000" in body, "no accuracy for a site on the outline"
    assert body.count("PointInside(pcbnew.VECTOR2I(int(pt.x), int(pt.y)), _ON)") == 2, \
        "the via/plated-pad test and the surface-pad test do not both take the outline accuracy"
    assert "PointInside(pcbnew.VECTOR2I(int(pt.x), int(pt.y)))" not in body, "a site test still asks the outline with no accuracy"


def t_an_island_that_carries_a_surface_pad_of_its_own_net_is_reported_and_not_refused():
    """21 September 2026: an island whose only site is a surface pad of its own net is reached by whatever reaches the
    pad (the router's job on a fanout-skipped pad, read by pruned_gate after the route), so it is reported; board A's
    six F.Cu load bank islands of A87 to A92 read that way, and the refusal there is the VBAT In2 piece and the In3
    runs, which carry no pad of their net at all."""
    body = SRC[SRC.index("    _isl, _padonly, _unfilled, _zones"):SRC.index("    n_esc = sum(")]
    assert 'pad.GetDrillSizeX() == 0 and pad.IsOnLayer(_lay)' in body, "the surface pads of the island's own net are not collected"
    assert "_padonly.append(_line); continue" in body, "an island on a surface pad of its net is not set apart"
    assert 'lines.append("WARN  %d pour island(s) reach only a surface pad of their own net and no via or plated pad' in body, \
        "the pad-only island is not reported"
    # and it is set apart BEFORE the refusal list, so it can never count as a collision
    assert body.index("_padonly.append(_line); continue") < body.index("_isl.append(_line)")
    assert "if _refused:" in body and "coll += 1" in body[body.index("if _refused:"):]


def t_kicads_point_test_says_outside_on_the_outline_and_inside_with_the_accuracy_the_judge_passes():
    """THE API FACT THE RULE RESTS ON, pinned where pcbnew is (21 September 2026). `SHAPE_LINE_CHAIN.PointInside`
    answers False for a point exactly on the outline and True for the same point with the judge's 0.1 mm
    accuracy; the island judge passes that accuracy at both of its site tests. If a KiCad build ever changes this
    the rule's proof is gone and this says so before a chain does."""
    try: import pcbnew
    except ImportError: raise Skip("pcbnew is not importable here")
    MM = 1000000
    o = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in ((0, 0), (10, 0), (10, 5), (0, 5)): o.Append(pcbnew.VECTOR2I(x * MM, y * MM))
    o.SetClosed(True)
    on_edge = pcbnew.VECTOR2I(3 * MM, 0)            # on the bottom edge, as R15's pad centre sat on the island's top edge
    inside = pcbnew.VECTOR2I(3 * MM, 2 * MM)
    assert o.PointInside(inside), "a point plainly inside reads outside: the fixture is wrong, not the judge"
    assert not o.PointInside(on_edge), "PointInside now answers True on the outline: the accuracy argument is no longer needed"
    assert o.PointInside(on_edge, 100000), "PointInside with the judge's 0.1 mm accuracy does not take a point on the outline"
    assert not o.PointInside(pcbnew.VECTOR2I(3 * MM, -200000), 100000), "the accuracy reaches 0.2 mm outside: it is too loose"

