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
    assert "advisory=advisory_for(rows)" in src, \
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


def t_every_barrel_over_its_rating_is_named_not_only_its_rails_worst():
    """The counts are per rail; the EVIDENCE has to be per barrel (18 September 2026).

    `via_current` takes each rail's worst barrel and reports that one, which is right for the count and the
    denominator ("4 rails judged, 1 over their weakest transition"). It is wrong for the reader, who is the
    person about to draw copper at the site: board D's +5V_SA crosses layers TWICE and each crossing is a
    single 0.40 mm barrel carrying the whole 1.10 A of the solved mesh, at (71.4, 74.2) and at (68.9, 82.0).
    The record said "one barrel" for a day, D15's locked copper was drawn for the first, and the second was
    found only when `barrel_sites.py` listed them all. The verdict carries `over_barrels` beside `over` now and
    its evidence names each one; measured on board D: over 1, over_barrels 2.
    """
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "via_current.py"), encoding="utf-8").read()
    assert "bad_sites" in src, "via_current no longer collects the over-rated barrels beside the per-rail worst"
    assert '"over_barrels": len(bad_sites)' in src, "the barrel count is not in the verdict's counts"
    assert "evidence=(bad + bad_sites)" in src, "the evidence is the per-rail list alone, so a second over-rated site is invisible"


def t_the_barrel_count_a_current_needs_is_arithmetic_the_generator_can_ask():
    """The rule's failure has one shape and the generator could always have avoided it (18 September 2026).

    Every PI-003 failure measured today is a layer transition given ONE barrel where the solved mesh puts more
    current through it than one barrel's wall carries: board D 1.22, board E 1.48 at the fuse and 1.32 at the
    dock block, board A as far as 3.77 over thirty-two sites on five rails. The generator knows the point, the
    drill and the rail's declared current, so the count is arithmetic, and `power_copper.stitch(..., amps=)`
    refuses a stitch that is short rather than leaving it for `via_current` to find after the route.

    The numbers below are this project's own curve at a 10 K rise and the fabricator's plating: a 0.40 mm barrel
    carries 0.90 A, a 0.30 mm 0.74, a 0.50 mm 1.05. Ceil, never round."""
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import via_current as vc
    assert vc.barrels_for(3.396, 0.40) == 4, "board A's worst VBUS20 transition needs four 0.40 mm barrels"
    assert vc.barrels_for(1.091, 0.30) == 2, "board E's fuse transition needs two 0.30 mm barrels"
    assert vc.barrels_for(1.387, 0.50) == 2, "board E's dock-block barrel needs a second at 0.50 mm"
    assert vc.barrels_for(0.5, 0.40) == 1, "a current inside one barrel's rating asks for one"
    assert vc.barrels_for(0.91, 0.40) == 2, "a current one percent over a barrel's rating asks for two, not one"


def t_a_stitch_that_is_short_of_barrels_refuses_the_board():
    """The check is at generation time, where it is still free to answer."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "power_copper.py"),
               encoding="utf-8").read()
    assert "def stitch(self, net, pts, drill=0.4, width=0.8, amps=None)" in src, "stitch takes no current"
    assert "need = self.barrels_for(amps, drill)" in src, "stitch does not ask how many barrels the current needs"
    # the message, not a window of characters: a char window broke the moment the hole-to-hole check was added
    # above it, which is a rule failing for where code sits rather than for what it does (18 September 2026)
    body = src[src.index("    def stitch("):src.index("    def rail_run(")]
    assert "and needs %d at a 10 K rise" in body, "a stitch short of barrels does not refuse the board by name"


def t_a_cluster_places_the_barrels_the_current_needs_and_keeps_the_hole_to_hole_floor():
    """The other half of the count rule (18 September 2026): where the room is known, the tool places them.

    Board A has thirty-two transitions to answer and typing three coordinates apiece is how a table of ninety-six
    numbers gets one wrong. `power_copper.cluster` takes the point, the axis the site may spread along (which
    `barrel_sites.py` reports, pad by pad) and the current, and places the count `via_current.barrels_for` gives,
    centred so a barrel already there keeps its copper. The default pitch is the drill plus 0.4 mm, which holds
    this project's own 0.30 mm hole-to-hole floor at every drill it uses."""
    import os, re
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "power_copper.py"),
               encoding="utf-8").read()
    body = src[src.index("    def cluster("):src.index("    def rail_run(")]
    # 19 September 2026: the count still comes from the current, now through the site's measured skew, which
    # defaults to 1.0 and leaves every existing call exactly where it was.
    assert "n = self.barrels_for(float(amps) * float(skew), drill)" in body, "the count does not come from the current"
    assert "(drill + 0.4)" in body, "the default pitch does not keep the hole-to-hole floor"
    assert "span / 2.0" in body, "the cluster is not centred on the site, so an existing barrel loses its place"


def t_a_stitch_that_puts_two_holes_too_close_refuses_the_board():
    """The tool knows its own pitch and its own drill (18 September 2026).

    Board E's dock-block barrels went from 0.5 to 0.7 mm to carry 1.39 A, and the same call also held the ten
    barrels at the source pad on a 0.8 mm pitch, which at 0.7 mm of hole is 0.10 mm hole to hole against the
    0.2995 mm the board's rules ask: eight hole_to_hole violations on the placed board. The DRC caught it, which
    is what the DRC is for, and a stitch call could have said it before the board existed. Points of DIFFERENT
    calls are not compared, because a call is one cluster and two clusters far apart are the normal case."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "power_copper.py"),
               encoding="utf-8").read()
    body = src[src.index("    def stitch("):src.index("    def rail_run(")]
    assert "_floor = drill + 0.2995" in body, "the stitch does not know the hole-to-hole floor"
    assert "hole to hole against the 0.2995" in body, "the refusal does not say what it measured"
    assert body.index("_floor = drill") < body.index("for x, y in pts:"), "the check runs after the copper is laid"


def t_a_barrel_the_mesh_solved_and_found_over_its_rating_decides_this_reading():
    """THE DEFECTIVE CASE (18 September 2026). Board E read INCONCLUSIVE with TWO barrels over their own wall
    at 10 K on rails `dc_drop` had solved, because a fourth declared rail carried no solved current at all and
    the flag was `not _all_measured`. An absence somewhere else on the board was softening a failure that had
    already been measured, which is the opposite of this project's own rule that absence is never a pass: here
    absence was being allowed to un-fail a reading. The attributed branch can only ADD failures to the
    measured ones, so a measured rail over its barrels is a failure whatever the coverage."""
    rows = [dict(net="CELL_F", measured=True, ok=False),
            dict(net="VIN_RAW", measured=True, ok=True),
            dict(net="PV_P", measured=False, ok=True)]
    assert vc.advisory_for(rows) is False, \
        "a rail the mesh solved and found over its rating is held back by another rail nobody solved"


def t_a_reading_that_would_otherwise_pass_keeps_the_flag_while_a_rail_is_attributed():
    """THE ACCEPTABLE CASE. Nothing measured is over its rating and one rail still has no solved current, so
    the reading cannot say the board passes: the attributed rail's own weakest cluster is an assumption about
    where the current goes, not a measurement, and the flag is what keeps it out of the verdict. Both ends
    matter, because a flag hard-coded either way expresses neither."""
    rows = [dict(net="CELL_F", measured=True, ok=True), dict(net="PV_P", measured=False, ok=True)]
    assert vc.advisory_for(rows) is True, "an attributed rail no longer holds an otherwise passing reading back"
    assert vc.advisory_for([dict(net="CELL_F", measured=True, ok=True)]) is False, \
        "a board whose every rail is measured still reads advisory"


def t_a_cluster_sized_on_a_measured_skew_places_the_barrel_an_even_split_would_miss():
    """THE DEFECTIVE FIXTURE, and it is board E's own numbers (19 September 2026). `cluster` sized CELL_F's
    fuse transition from the total and placed TWO barrels of 0.50 mm; the solved mesh then put 1.198 A through
    one of them and 0.611 A through the other, so the site passes 1.809 A and shares it about two to one, and
    the near barrel is over its 1.05 A wall while the arithmetic says the pair is enough. With n barrels the
    worst carries amps * skew / n, so the count that keeps it under the wall is barrels_for(amps * skew).
    The arithmetic is `via_current`'s, which is pure; `power_copper` imports pcbnew and cannot run here, so
    the wiring is read from its source the way the sibling rule above reads it."""
    import os
    assert vc.barrels_for(1.809, 0.5) == 2, vc.barrels_for(1.809, 0.5)
    assert vc.barrels_for(1.809 * 1.325, 0.5) == 3, vc.barrels_for(1.809 * 1.325, 0.5)
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "power_copper.py"),
               encoding="utf-8").read()
    body = src[src.index("    def cluster("):src.index("    def rail_run(")]
    assert "float(amps) * float(skew)" in body, "the skew does not reach the count"


def t_the_default_skew_is_an_even_split_so_no_existing_call_moves():
    """THE ACCEPTABLE FIXTURE: a caller that has measured nothing gets exactly the count it got yesterday."""
    import os, re
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "power_copper.py"),
               encoding="utf-8").read()
    m = re.search(r"def cluster\(self[^)]*\)", src)
    assert m and "skew=1.0" in m.group(0), m.group(0) if m else "no cluster signature"
    assert vc.barrels_for(1.091 * 1.0, 0.5) == vc.barrels_for(1.091, 0.5), "the default moved a count"


def t_a_skew_below_an_even_split_is_refused():
    """A skew is the WORST share over the even one and cannot be less than one; a number below it is a
    mistake, and a generous mistake in this direction takes barrels off a rail."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "power_copper.py"),
               encoding="utf-8").read()
    body = src[src.index("    def cluster("):src.index("    def rail_run(")]
    assert "float(skew) < 1.0" in body and "raise ValueError" in body, "a skew below 1.0 is not refused"
