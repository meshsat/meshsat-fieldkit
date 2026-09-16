#!/usr/bin/env python3
"""A closure that reaches the goal CELL must finish on the COPPER (MESHSAT-862, 16 September 2026).

Board A35's round two routed 0 hard with 13 connections open, and its stub router printed, for net after net,
"the path reached a goal CELL whose copper it does not touch". A cell is a goal when the target's raster covers
it, and the closure is then laid to that cell's CENTRE. Two things are done about it here and they are of
different kinds. The first is a repair that can only help: before the closure is given up, one short segment is
laid from that centre to the exact nearest point of this net's own copper, and it is kept only if KiCad's
unconnected count falls. The second is an admission: the obvious explanation, that the centre sits outside the
copper, is NOT supported by the arithmetic of these rasterisers, which sample cell centres against the shape's
own half width. So the refusal now carries the two distances and the counts that would settle it, instead of a
sentence that sounds like a diagnosis.

The arithmetic is transcribed here because `stub_router.py` needs pcbnew at module level, and a structural rule
below keeps the transcription honest: the source must still try to land on the copper before it gives up.
"""
import os, re, math

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(TOOLS, "stub_router.py")


def _nearest_on_segment(px, py, ax, ay, ex, ey):
    dx, dy = ex - ax, ey - ay; L2 = dx * dx + dy * dy
    u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return ax + u * dx, ay + u * dy


def t_the_refusal_reports_the_two_distances_that_would_explain_it():
    """A message that names a cause it did not measure is how an evening goes on the wrong theory.

    The first version of this change assumed the goal cell centre sat outside the copper it stands for, and the
    arithmetic says otherwise: these rasterisers mark a cell when its CENTRE is within the shape's own half
    width, so the centre is ON the copper, and a 0.20 mm closure ending there overlaps a 0.10 mm track by more
    than a tenth of a millimetre. The assumption was wrong, so the refusal now carries the measurement instead
    of a story: how far each end of the path really is from this net's nearest copper on its own layer, and
    what KiCad's unconnected count did. The next board that hits it will say why."""
    s = open(SRC, encoding="utf-8").read()
    i = s.find("NOT CLOSED:")
    assert i > 0
    msg = s[i:i + 700]
    for want in ("start %.3f", "end %.3f", "unconnected"):
        assert want in msg, "the refusal does not report %r, so its cause stays a guess" % want


def t_landing_puts_the_end_on_the_copper_itself():
    """The nearest point on the target segment is on the segment, and the offset goes to zero."""
    ax, ay, ex, ey = 10.0, 10.0, 20.0, 10.0
    px, py = 15.03, 10.12                       # a goal cell centre 0.12 mm off a horizontal track
    tx, ty = _nearest_on_segment(px, py, ax, ay, ex, ey)
    assert abs(ty - ay) < 1e-9 and ax <= tx <= ex, (tx, ty)
    assert math.hypot(tx - px, ty - py) <= math.hypot(px - ax, py - ay), "the landing point must be the nearest one"
    # and landing on an end point rather than past it
    tx2, ty2 = _nearest_on_segment(5.0, 10.0, ax, ay, ex, ey)
    assert (tx2, ty2) == (ax, ay), (tx2, ty2)


def t_the_source_tries_to_land_before_it_gives_the_closure_up():
    """A structural rule: a future edit cannot quietly drop the retry and leave the message behind."""
    s = open(SRC, encoding="utf-8").read()
    assert "def _nearest_copper(" in s, "the landing helper is gone"
    i_land = s.find("_nearest_copper(net,")
    i_give = s.find("NOT CLOSED:")
    assert i_land > 0 and i_give > 0, (i_land, i_give)
    assert i_land < i_give, "the closure is given up before it tries to finish on the copper"
    seg = s[i_land:i_give]
    assert "_unconnected()" in seg, "the retry must be judged by KiCad's connectivity, never assumed"


def t_the_retry_is_kept_only_when_it_connects():
    """The same law the rest of this pipeline runs on: a change is kept only if the number moves."""
    s = open(SRC, encoding="utf-8").read()
    i = s.find("_U2 = _unconnected() if landed else None")
    assert i > 0, "the retry does not measure"
    seg = s[i:i + 400]
    assert "_U2 < _U" in seg, "the retry is kept without proving it connected"
