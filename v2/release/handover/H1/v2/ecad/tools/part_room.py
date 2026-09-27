#!/usr/bin/env python3
"""Where does a part's own support sit? (a REPORT, 21 September 2026)

A pad-to-pad open is this project's shorthand for a pad with no lane out at any resolution, which it reads as
a placement question; what it does not say is WHOSE placement. Board E's last four opens were pad to pad at
U5's pins, and the answer was not U5's room, which is 11.40 mm clear to the west and open to the board's edge
to the south: it was that the parts on the other end of those four nets sit 11.29 to 22.10 mm away, packed
into two regions on opposite sides of the tracker. Asked of board A the same afternoon, every one of its five
LM5176 stages drives its FETs from 13.5 to 28.9 mm away, and one of those gate drives is an open the router
never closed.

So this reports two things about a named part: the clear distance from its courtyard to the nearest other
courtyard in each of the four directions, which says whether it can be moved or grown into; and for each net
named, the distance from that net's pad ON THIS PART to the nearest pad of the same net elsewhere, which says
how far its support has been placed. Both are read off a placed or routed board.

IT DECIDES NOTHING AND IT IS NOT A SEAT SEARCH. A seat is chosen by a chain that ends PREROUTE-DONE OK, the
D31-to-D32 procedure; what this gives is the number that says whether looking for one is worth an hour. It
measures courtyards, not fans: a seat that is clear here can still be refused by the escape-fan predictor,
which is what `place_audit` is for and what cost board A thirteen escapes on 20 September.

Usage: part_room.py <board.kicad_pcb> <REF> [net,net,...]
"""
import sys
import pcbnew

MM = 1e6


def room_around(mine, others):
    """The clear distance from `mine` to the nearest box in each direction, and whose it is.

    Boxes are (ref, x0, y0, x1, y1) in millimetres, and only a box that SHARES A BAND with `mine` counts:
    a part diagonally opposite blocks nothing, and a tool that counted it would report a crowded part where
    the lane is open. Pure arithmetic, so it runs where KiCad is not."""
    _, x0, y0, x1, y1 = mine
    room = {"west": 9e9, "east": 9e9, "north": 9e9, "south": 9e9}
    who = {}
    for ref, ox0, oy0, ox1, oy1 in others:
        if oy1 > y0 and oy0 < y1:                      # shares a horizontal band
            if ox1 <= x0 and x0 - ox1 < room["west"]:
                room["west"] = x0 - ox1; who["west"] = ref
            if ox0 >= x1 and ox0 - x1 < room["east"]:
                room["east"] = ox0 - x1; who["east"] = ref
        if ox1 > x0 and ox0 < x1:                      # shares a vertical band
            if oy1 <= y0 and y0 - oy1 < room["north"]:
                room["north"] = y0 - oy1; who["north"] = ref
            if oy0 >= y1 and oy0 - y1 < room["south"]:
                room["south"] = oy0 - y1; who["south"] = ref
    return room, who


def boxes(bd, skip=None):
    out = []
    for o in bd.GetFootprints():
        if skip is not None and o.GetReference() == skip:
            continue
        try:
            b = o.GetCourtyard(o.GetLayer()).BBox()
        except Exception:                              # a footprint with no courtyard blocks nothing here
            continue
        out.append((o.GetReference(), b.GetLeft() / MM, b.GetTop() / MM, b.GetRight() / MM, b.GetBottom() / MM))
    return out


bd = pcbnew.LoadBoard(sys.argv[1])
REF = sys.argv[2]
NETS = [n for n in (sys.argv[3].split(",") if len(sys.argv) > 3 else []) if n]

fp = bd.FindFootprintByReference(REF)
if fp is None:
    raise SystemExit("%s: no such footprint" % REF)
c = fp.GetCourtyard(fp.GetLayer()).BBox()
x0, y0, x1, y1 = c.GetLeft() / MM, c.GetTop() / MM, c.GetRight() / MM, c.GetBottom() / MM
print("%s courtyard %.2f x %.2f at (%.2f, %.2f) to (%.2f, %.2f) on %s"
      % (REF, x1 - x0, y1 - y0, x0, y0, x1, y1, bd.GetLayerName(fp.GetLayer())))

room, who = room_around((REF, x0, y0, x1, y1), boxes(bd, skip=REF))
for d in ("west", "east", "north", "south"):
    v = room[d]
    print("  %-6s %s" % (d, "clear to the board's own edge" if v > 1e8
                         else "%.2f mm to %s" % (v, who.get(d, "?"))))

if NETS:
    print("the named nets' own pads on this part and their partners elsewhere:")
    for n in NETS:
        mine = [(p.GetNumber(), p.GetPosition().x / MM, p.GetPosition().y / MM)
                for p in fp.Pads() if p.GetNetname().lstrip("/") == n]
        others = [(o.GetReference(), p.GetNumber(), p.GetPosition().x / MM, p.GetPosition().y / MM)
                  for o in bd.GetFootprints() if o.GetReference() != REF
                  for p in o.Pads() if p.GetNetname().lstrip("/") == n]
        if not mine:
            print("  %-12s no pad of it on %s" % (n, REF)); continue
        for num, px, py in mine:
            best = sorted(((((px - ox) ** 2 + (py - oy) ** 2) ** 0.5, r, pn) for r, pn, ox, oy in others),
                          key=lambda t: t[0])[:2]
            print("  %-12s %s.%s at (%.2f, %.2f) -> %s"
                  % (n, REF, num, px, py,
                     ", ".join("%s.%s %.2f mm" % (r, pn, d) for d, r, pn in best) or "no other pad of this net"))
