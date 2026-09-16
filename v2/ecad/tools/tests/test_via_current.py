#!/usr/bin/env python3
"""The via that carries a rail across layers (rule PI-003, MESHSAT-862, 16 September 2026).

"About 2.5 A per 0.4 mm hole" has been in a generator comment since 5 September and nothing ever measured a
board against it. These are the arithmetic's own checks: the barrel is geometry, the current is IPC-2221's
curve with the internal constant, and the plating thickness is the fabricator's published 18 um. The functions
are pure, so this file needs no KiCad."""
import os, sys, math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import via_current as vc


def t_the_barrel_is_an_annulus_of_the_plating_thickness():
    i, area = vc.ampacity(0.3, 10)
    want = math.pi * (0.3 + 0.018) * 0.018
    assert abs(area - want) < 1e-9, (area, want)


def t_a_three_tenths_via_carries_about_one_amp_at_twenty_kelvin():
    """The calibration point. The industry's own rule of thumb for a 0.3 mm via is one ampere, and it is worth
    knowing that this expression lands there before any board is judged by it: a formula that disagreed with
    the number every engineer carries would be a formula with a unit error in it."""
    i, _ = vc.ampacity(0.3, 20)
    assert 0.9 <= i <= 1.1, "a 0.3 mm via at 20 K reads %.2f A, which is not the number the trade uses" % i


def t_the_record_s_own_figure_is_the_one_this_refutes():
    """5 September's comment says about 2.5 A per 0.4 mm hole. At the fabricator's plating and a 10 K rise the
    same via carries under one ampere, and even at 20 K it is 1.2. The comment is nearly three times the
    computed figure, which is the reason this rule exists rather than a reason to doubt the arithmetic: the
    comment cites nothing and this cites the barrel."""
    i10, _ = vc.ampacity(0.4, 10)
    i20, _ = vc.ampacity(0.4, 20)
    assert i10 < 1.0 and i20 < 1.5, (i10, i20)


def t_capacity_rises_with_the_hole_and_with_the_rise():
    a = [vc.ampacity(d, 10)[0] for d in (0.2, 0.3, 0.4, 0.5)]
    assert a == sorted(a), a
    assert vc.ampacity(0.3, 20)[0] > vc.ampacity(0.3, 10)[0]


def t_a_site_is_the_group_of_barrels_that_sit_together():
    pts = [(0, 0), (1.0, 0), (0, 1.0),          # one transition
           (30.0, 30.0), (30.5, 30.0),          # another, far away
           (60.0, 0)]                            # a lone via
    g = vc.sites(pts, 6.0)
    assert sorted(len(x) for x in g) == [1, 2, 3], [len(x) for x in g]


def t_two_vias_carry_twice_one_via_and_the_weakest_site_decides():
    one, _ = vc.ampacity(0.3, 10)
    assert abs((one * 2) - (vc.ampacity(0.3, 10)[0] + vc.ampacity(0.3, 10)[0])) < 1e-12


def t_the_verdict_is_advisory_until_it_knows_which_via_the_current_crosses():
    """Its first run on real boards found something on all seven, and most of it is one false shape.

    A rail's weakest SITE is often a lone stitch via at the end of a pour, carrying almost none of the rail's
    current, while the current itself travels in a band with a field of vias under it: board E's CELL_F reads
    "18 A through 1 via" and board P's FUSED the same, which is not what that copper does. The arithmetic is
    right and the attribution is not. A gate that refuses eleven rails on board A for a reason its own author
    doubts is the heuristic-as-law this registry exists to remove, so the verdict is a measurement until the
    per-via current comes from the solved mesh.

    16 SEPTEMBER 2026, THE SECOND HALF: it comes from the solved mesh now. `dc_drop.py` computes the current in
    every barrel on its way to the density verdict and writes them beside the board, and where every judged
    rail has them the attribution is a measurement and the flag comes off. The rule is no longer "always
    advisory"; it is "advisory exactly when at least one rail is still attributed rather than measured", which
    is what this asserts, because a flag that is hard-coded either way cannot express that."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "via_current.py"),
               encoding="utf-8").read()
    assert "advisory=not _all_measured" in src, \
        "the advisory flag no longer follows whether the attribution was measured"
    assert "advisory=True" not in src, "the flag is hard-coded on, so a measured board stays advisory for ever"
    assert "-via-currents.json" in src, "via_current does not look for the solved barrel currents"
    dc = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dc_drop.py"),
              encoding="utf-8").read()
    assert "-via-currents.json" in dc, "dc_drop does not write the barrel currents it already computes"


def t_an_advisory_verdict_does_not_decide_a_rule():
    """The verdict channel has carried the flag since 15 September and the readiness reader did not look at it,
    so a tool whose own author had marked it "not a bar" would still have failed its rule on every board."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rules_status.py"),
               encoding="utf-8").read()
    i = src.index('res = rec.get("result") or rec.get("verdict")')
    seg = src[i:i + 900]
    assert 'rec.get("advisory")' in seg, "rules_status reads an advisory measurement as a verdict"


def t_the_generators_via_sizing_report_is_a_measurement_or_silence():
    """16 September 2026. The first version of the hand-over report divided the RAIL'S WHOLE CURRENT by one
    barrel's rating at every site and called 29 of board A's 31 sites short. That is the same attribution
    error that kept this rule advisory all day, moved to generation time: a rail with several hand-overs splits
    its current between them and a stitch site inside a pour carries almost none of it. A generator cannot know
    the split and a solved mesh can, so the report names a site only where a barrel MEASURED there is over its
    own wall's rating, and says nothing at all where the board has never been solved. With the measurement it
    names 13 sites, and two of them already carry four and six barrels, which is the finding: a via group does
    not share evenly and more of them is the remedy, not a different number typed into the file."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gen_pcb_a3.py"),
               encoding="utf-8").read()
    body = src[src.index("def _size("):src.index("def row(net")]
    assert "if not _VIA_MEASURED: return" in body, \
        "the sizing report speaks about boards it has no measurement for"
    assert "amps / max(barrel_a" not in body and "ceil(amps /" not in body, \
        "the rail's whole current is being attributed to a single site again"
    assert '_b[2]' in body and 'hypot' in body, "the report does not read the measured barrels near the site"


def t_a_site_that_already_has_the_barrels_is_a_sharing_problem_and_says_so():
    """The second reading of the same report, 16 September 2026. Three of the thirteen sites carry four or six
    barrels and still have one over its rating: there the count is not the defect, the SHARING is, and the
    first sentence ("this site wants about 4") read as though four more were needed. The site's own total is
    measured so the report can tell a shortage of holes from copper that feeds one of them."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gen_pcb_a3.py"),
               encoding="utf-8").read()
    body = src[src.index("def _size("):src.index("def row(net")]
    assert "total = sum(" in body, "the site's whole current is never summed, so a share cannot be computed"
    assert "ceil(total /" in body, "the wanted count is still taken from one barrel rather than from the site"
    rep = src[src.index("if _VIA_SHORT:"):src.index("elif _VIA_MEASURED:")]
    assert "do not SHARE" in rep, "a site with barrels enough is still reported as wanting more"
    assert "the site carries" in rep, "the report does not say what the site carries"
