#!/usr/bin/env python3
"""A closure is searched at the clearance the net's CLASS asks for (MESHSAT-862, 14 September 2026).

The width and the via of a stub closure were taught to read the net's class on 13 September, after "every stub
closure since has been laid at the default 0.25 mm with a 0.6/0.3 via" (32.157). The CLEARANCE was left behind
as the literal 0.16 mm, for every net of every board.

It is wrong in the direction that costs connections. C12 ends 0 hard with two opens, `/PWM1` and `/HB2`, and
both pads sit in open ground: nothing within 2.12 mm of TP29, nothing but its own partner's tracks within
1.65 mm of R44. A board-wide search at a 0.1 mm grid on three layers came back with no path for either in
eight minutes, because the lanes it would have to use were laid at the panel's own class number and a map
built at 0.16 mm closes them.

KiCad's rule is that the clearance between two items is the LARGER of their two classes', so that is what the
obstacle map uses, net by net, with the grid's own hundredth of a millimetre on top. `stub_accept` still
judges the result with the board's DRC, which is what makes a finer search safe to try.
"""
import os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = open(os.path.join(TOOLS, "stub_router.py")).read()


def t_the_clearance_comes_from_the_class():
    assert "def net_clr(" in SR, "there is no per-net clearance at all"
    assert "netclass.class_of(_ASSIGN" in SR, "the project's own netclass assignments are not read"


def t_the_larger_of_the_two_classes_decides():
    i = SR.find("def build_maps(")
    body = SR[i:i + 2600]
    assert "def clr_to(other): return max(_me, net_clr(other))" in body, (
        "the map does not take the larger of the two nets' clearances, which is KiCad's own rule")


def t_no_obstacle_is_still_inflated_by_the_literal():
    i = SR.find("def build_maps(")
    body = SR[i:SR.find("\n    for d in b.GetDrawings()", i)]
    for bad in ("CLR + w2", "CLR + vr"):
        for line in body.splitlines():
            if bad in line and "HOLE_CLR" not in line and "GetIsRuleArea" not in line and "z.Outline()" not in line:
                raise AssertionError("an obstacle is still inflated by the literal clearance: %s" % line.strip()[:90])


def t_the_number_is_printed():
    assert "clearance %.3f mm from its own class" in SR, (
        "the clearance a search ran at is not printed, which is how 0.25 mm on a 0.5 mm class survived a week")


def t_the_literal_survives_as_the_fallback():
    assert "CLR = 0.16" in SR, "a net whose class cannot be resolved has no answer at all"
    assert "_CLR_CACHE[n] = CLR if v is None else v + 0.01" in SR, "the fallback is not the literal"


def t_a_track_goal_is_the_tracks_copper_and_not_a_disc_around_a_point():
    """A31's stub router laid ten closures and took all ten back with 'reached a goal cell whose copper it
    does not touch'. The fallback goal for a track item was a 0.15 mm DISC around the point the DRC named,
    so a path could stop up to 0.15 mm off the copper, and a 0.2 mm closure ending there overlaps nothing.
    The other-cluster goal already stamps every track at its own width; the fallback does the same now, and
    keeps the disc only for a point no segment of the net is near."""
    i = SR.find("def copper_cells(")
    body = SR[i:SR.find("\nINNER_GOAL = None", i)]
    assert "segment(M, mm(a.x), mm(a.y), mm(e.x), mm(e.y), mm(t.GetWidth()) / 2)" in body, (
        "a track goal is still a disc around the DRC's point rather than the track's own copper")
    assert "if not found: disc(M, item[\"x\"], item[\"y\"], 0.15)" in body, "the disc is gone entirely, so a point with no segment near it has no goal"


def t_the_stub_router_with_nothing_to_close_leaves_before_pcbnew_can_crash_it():
    """C17's second re-finish (15 Sep 2026): the board was already at 0 unrouted, the stub router printed
    `unconnected pairs: 0`, went on to build its maps and died with exit 139, and the finish refused the board for
    the crash. A run with no pair to close must say so and leave through os._exit before any pcbnew teardown."""
    s = open(os.path.join(TOOLS, "stub_router.py")).read()
    i = s.find('print("unconnected pairs:", len(pairs))'); assert i > 0
    body = s[i:i + 900]
    assert "if not pairs:" in body and "os._exit(0)" in body and "closed 0 of 0" in body, (
        "a stub router with nothing to close still walks into the map build and pcbnew's teardown")
