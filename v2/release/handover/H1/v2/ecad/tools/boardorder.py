#!/usr/bin/env python3
"""A stable order for the passes that LAY copper (MESHSAT-862, stage 0b, 11 September 2026).

Measured, not argued. Two runs of the D pre-route chain on identical input produced boards that differ in
**four tracks and four vias of 391 items**: the escape stubs of `/MICAMP_OUT` and `/SAU_RST`, each a locked
track and its via, at different positions. Footprints, zones and every other track were identical, and
pinning `PYTHONHASHSEED` changed nothing.

The chain is this:

  1. KiCad mints a random `(uuid ...)` for every item it writes, and the order footprints appear in the file
     follows from that, so two saves of the same board are not the same bytes and not the same order.
  2. `escape.py` and `prefanout.py` iterate `board.GetFootprints()`, which is that order.
  3. Both lay GREEDILY, treating copper already laid as an obstacle. Whichever footprint is reached first
     takes the room.

So which escape fits was decided by a random number. On D it cost two stubs; on a congested board it is the
difference between a pad that escapes and a pad the router has to fan itself, and nothing anywhere would
have reported it. `escape.py`'s own log gave the only visible tell: `no escape for U15 pad 5` printed before
`U5` in one run and after it in the other.

`footprints()` sorts by reference, which is unique on a board and is also the order a person reads a
netlist in. The tie-break is position, for the footprints a generator left without a reference.

THIS IS FOR LOOPS THAT DECIDE, not for loops that read. A pass that rasterises every pad as an obstacle
gets the same raster whatever order it walks in, and sorting there would be noise in a diff; the docstring
says so rather than leaving the next reader to wonder why some loops are sorted and some are not.
"""


def footprints(board):
    """Every footprint, in an order that does not depend on a random UUID."""
    return sorted(board.GetFootprints(),
                  key=lambda f: (f.GetReference(), f.GetPosition().x, f.GetPosition().y))


def zones(board):
    """Every zone, in a stable order: net, layer, priority, name, then the first corner."""
    def key(z):
        try:
            o = z.Outline().Outline(0)
            first = (o.CPoint(0).x, o.CPoint(0).y) if o.PointCount() else (0, 0)
        except Exception:
            first = (0, 0)
        return (z.GetNetname(), z.GetLayer(), z.GetAssignedPriority(), z.GetZoneName() or "", first)
    return sorted(board.Zones(), key=key)


def tracks(board):
    """Every track and via, in a stable order: layer, start, end, width, net."""
    return sorted(board.GetTracks(),
                  key=lambda t: (t.GetLayer(), (t.GetStart().x, t.GetStart().y),
                                 (t.GetEnd().x, t.GetEnd().y), t.GetNetname()))
