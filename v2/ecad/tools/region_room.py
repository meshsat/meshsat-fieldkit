#!/usr/bin/env python3
"""How much room a packer region has to grow into, and in which direction.

MESHSAT-862, 13 September 2026, owner ruling 13: the session may resize board B's overflowing regions, board
B only, one at a time, each reported with its overflow before and after. **A rectangle cannot be sized from a
warning.** What decides it is the room around it: the regions of the SAME side (two of one side may never
intersect, `tests/test_region_overlap.py`), the fixed parts standing in the way, and the board outline.

It reads the region table `regionfit.record` writes beside the board (`out/<stem>-regions.json`) and the board
itself for the fixed parts and the outline, and for every region it reports, per direction, how far the edge
could move before it meets something, and what it would meet first.

It changes nothing. The rectangles live in `gen_pcb_<x>3.py`'s `REGIONS`, which is on the never-auto floor.

Usage: region_room.py <board.kicad_pcb> [--json out.json] [--only NAME,NAME]
"""
import sys, os, json, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict

# ABUTTING REGIONS ARE THE DESIGN HERE, not a defect: each slot column is a row of rectangles that share
# their edges (S1_SWIC ends where S1_SWE begins), and `test_region_overlap` forbids only regions that
# INTERSECT. The first version grew every neighbour by half a millimetre before testing, so a region that
# already touched one reported zero room in all four directions, which is the one answer that cannot be
# right (13 September 2026). A shared edge is not an overlap: the test is strict, with an epsilon.
EPS = 0.01


def _overlap(a, b, eps=0.0):
    """Do two rectangles (x0, y0, x1, y1), y either way up, share AREA? A shared edge does not."""
    ax0, ax1 = sorted((a[0], a[2])); ay0, ay1 = sorted((a[1], a[3]))
    bx0, bx1 = sorted((b[0], b[2])); by0, by1 = sorted((b[1], b[3]))
    return (ax0 + eps < bx1 and bx0 + eps < ax1 and ay0 + eps < by1 and by0 + eps < ay1)


def room(rect, side, others, blockers, outline, step=0.5, limit=80.0):
    """{direction: (millimetres free, what stops it)} for one rectangle.

    Measured by walking the edge out in half-millimetre steps until the grown rectangle would touch a region
    of the same side, a blocker, or the outline. A walk rather than an intersection sum, because a region can
    be stopped by a different thing in each direction and the NAME of what stops it is the useful half.
    """
    out = {}
    x0, y0, x1, y1 = rect
    lo_x, hi_x = sorted((x0, x1)); lo_y, hi_y = sorted((y0, y1))
    for d, (dx0, dy0, dx1, dy1) in (("west", (-1, 0, 0, 0)), ("east", (0, 0, 1, 0)),
                                    ("south", (0, -1, 0, 0)), ("north", (0, 0, 0, 1))):
        free, why = 0.0, "the %.0f mm search limit" % limit
        g = 0.0
        while g + step <= limit:
            g += step
            # THE STRIP BEING ADDED, NOT THE WHOLE GROWN RECTANGLE (13 September 2026). Board B's ETH region
            # already overlaps the fixed magnetics T1 by a tenth of a millimetre at its northern edge, so
            # testing the grown rectangle reported zero room in ALL FOUR directions and read as boxed in on
            # every side by a part that sits past one edge. A region is asking what is in the way of GROWING,
            # and what it already overlaps is a different question, one the placed board answers.
            cand = ((lo_x - g, lo_y, lo_x, hi_y) if d == "west" else
                    (hi_x, lo_y, hi_x + g, hi_y) if d == "east" else
                    (lo_x, lo_y - g, hi_x, lo_y) if d == "south" else
                    (lo_x, hi_y, hi_x, hi_y + g))
            whole = (lo_x + dx0 * g, lo_y + dy0 * g, hi_x + dx1 * g, hi_y + dy1 * g)
            hit = None
            if outline and not (outline[0] <= whole[0] and whole[2] <= outline[2]
                                and outline[1] <= whole[1] and whole[3] <= outline[3]):
                hit = "the board outline"
            if hit is None:
                for nm, r, sd in others:
                    if sd != side:
                        continue
                    if _overlap(cand, r, EPS):
                        hit = "region %s" % nm
                        break
            if hit is None:
                for nm, r in blockers:
                    if _overlap(cand, r, EPS):
                        hit = "fixed part %s" % nm
                        break
            if hit:
                why = hit
                break
            free = g
        out[d] = (round(free, 2), why)
    return out


def free_rects(w, h, side, others, blockers, outline, step=2.0):
    """Every place on one side where a w by h rectangle fits with nothing of that side in it.

    13 September 2026: board B's GAP12 is 18 mm wide and owner decision 11 put a 23.79 mm coin cell holder
    in it, which is the whole of its 64.7 mm overflow and cannot be fixed by resizing a pocket with 2 mm of
    room. A part that fits nowhere in its own region has to go somewhere, and somewhere is a measurement,
    not a guess. Coarse on purpose: a 2 mm grid, reporting distinct areas rather than every offset.
    """
    x0, y0, x1, y1 = outline
    found = []
    y = y0 + 1.0
    while y + h <= y1 - 1.0:
        x = x0 + 1.0
        while x + w <= x1 - 1.0:
            cand = (x, y, x + w, y + h)
            clash = any(_overlap(cand, r, EPS) for nm, r, sd in others if sd == side)
            if not clash:
                clash = any(_overlap(cand, r, EPS) for nm, r in blockers)
            if not clash:
                found.append((round(x, 1), round(y, 1)))
                x += w
            else:
                x += step
        y += step
    return found


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("--json")
    ap.add_argument("--only")
    ap.add_argument("--free", help="W,H,side: where a W by H mm rectangle fits on that side")
    a = ap.parse_args(argv)
    import pcbnew
    stem = os.path.splitext(os.path.basename(a.board))[0]
    table = os.path.join(os.path.dirname(os.path.abspath(a.board)), "out", "%s-regions.json" % stem)
    if not os.path.exists(table):
        return verdict.write("region_room", verdict.INCONCLUSIVE, counts={"regions": 0}, denominator=0,
                             evidence=["no region table at %s: run the placement generator first" % table],
                             inputs={"board": a.board},
                             note="the room around a region cannot be measured without the region table")
    d = json.load(open(table, encoding="utf-8"))
    regions = d["regions"]; over = d.get("overflow", {})
    b = pcbnew.LoadBoard(a.board)
    # the packer's frame: x right from OX, y DOWN from OY, which is what the rectangles are written in
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "gen_pcb_%s3.py" % stem.split("-")[1][0]), encoding="utf-8").read() if False else ""
    ox, oy = 150.0, 110.0
    for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen_pcb_b3.py"), encoding="utf-8"):
        if line.startswith("OX, OY = "):
            ox, oy = (float(v) for v in line.split("=")[1].split(","))
            break
    bb = b.GetBoardEdgesBoundingBox()
    outline = (pcbnew.ToMM(bb.GetLeft()) - ox, oy - pcbnew.ToMM(bb.GetBottom()),
               pcbnew.ToMM(bb.GetRight()) - ox, oy - pcbnew.ToMM(bb.GetTop()))
    fixed = []
    for f in b.GetFootprints():
        if not f.IsLocked() and f.GetReference() not in _fixed_refs():
            continue
        fb = f.GetBoundingBox(False, False)
        fixed.append((f.GetReference(), (pcbnew.ToMM(fb.GetLeft()) - ox, oy - pcbnew.ToMM(fb.GetBottom()),
                                         pcbnew.ToMM(fb.GetRight()) - ox, oy - pcbnew.ToMM(fb.GetTop()))))
    # A MOUNTING HOLE IS NOT A FIXED PART and it stops a region just as hard (13 September 2026): the first
    # free-space query on board B answered with the south-east corner, which carries H19 and H20 and their
    # keep-outs. Holes and the small named keep-outs drawn around them are blockers too; the board-wide
    # bands are not, which is `gen_pcb_b3._load_obstacles`'s own rule, so the same 30 mm cap applies.
    # A THROUGH-HOLE PAD OCCUPIES BOTH SIDES. This is owner decision 11's whole subject made mechanical: a
    # front region over a back part's through-hole pins is a short, which is why the coin cell had to leave
    # GAP23. The first BATT pocket this tool proposed sat over U42's /+3V3_IOCA pin and reproduced it exactly
    # (13 September 2026), so every PTH and NPTH pad on the board is a blocker for a region of EITHER side.
    for f in b.GetFootprints():
        for pd in f.Pads():
            if pd.GetAttribute() not in (pcbnew.PAD_ATTRIB_NPTH, pcbnew.PAD_ATTRIB_PTH):
                continue
            hb = pd.GetBoundingBox()
            kind = "hole" if pd.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else "through-hole pin"
            fixed.append(("%s %s.%s" % (kind, f.GetReference(), pd.GetNumber()),
                          (pcbnew.ToMM(hb.GetLeft()) - ox, oy - pcbnew.ToMM(hb.GetBottom()),
                           pcbnew.ToMM(hb.GetRight()) - ox, oy - pcbnew.ToMM(hb.GetTop()))))
    for z in b.Zones():
        if not z.GetIsRuleArea():
            continue
        zb = z.GetBoundingBox()
        w, h = pcbnew.ToMM(zb.GetWidth()), pcbnew.ToMM(zb.GetHeight())
        if w > 30.0 or h > 30.0:
            continue
        fixed.append(("keep-out %s" % (z.GetZoneName() or "unnamed")[:18],
                      (pcbnew.ToMM(zb.GetLeft()) - ox, oy - pcbnew.ToMM(zb.GetBottom()),
                       pcbnew.ToMM(zb.GetRight()) - ox, oy - pcbnew.ToMM(zb.GetTop()))))
    others = [(r["name"], r["rect"], r["side"]) for r in regions]
    if a.free:
        fw, fh, fside = a.free.split(",")
        hits = free_rects(float(fw), float(fh), fside.strip(),
                          [(r["name"], r["rect"], r["side"]) for r in regions], fixed, outline)
        print("region_room: %s by %s mm on the %s fits in %d place(s)" % (fw, fh, fside, len(hits)))
        for x, y in hits[:24]:
            print("   at (%.1f, %.1f) to (%.1f, %.1f)" % (x, y, x + float(fw), y + float(fh)))
        return verdict.write("region_room", verdict.PASS, counts={"free_places": len(hits)},
                             denominator=max(len(hits), 1),
                             evidence=["%s by %s on the %s: %d place(s)" % (fw, fh, fside, len(hits))],
                             inputs={"board": a.board}, note="where a rectangle of that size fits on that side")
    want = set((a.only or "").split(",")) if a.only else None
    rows, ev = [], []
    print("%-9s %6s  %-22s %-22s %-22s %s" % ("region", "over", "west", "east", "south", "north"))
    for r in regions:
        if want and r["name"] not in want:
            continue
        rm = room(r["rect"], r["side"], [o for o in others if o[0] != r["name"]], fixed, outline)
        rows.append({"name": r["name"], "rect": r["rect"], "side": r["side"], "refs": r["refs"],
                     "overflow_mm": over.get(r["name"], 0.0), "room": {k: v[0] for k, v in rm.items()},
                     "stopped_by": {k: v[1] for k, v in rm.items()}})
        cell = lambda k: "%5.1f %s" % (rm[k][0], rm[k][1][:15])
        print("%-9s %6.1f  %-22s %-22s %-22s %s"
              % (r["name"], over.get(r["name"], 0.0), cell("west"), cell("east"), cell("south"), cell("north")))
        if over.get(r["name"], 0.0):
            ev.append("%s overflows %.1f mm; room W %.1f E %.1f S %.1f N %.1f"
                      % (r["name"], over[r["name"]], rm["west"][0], rm["east"][0], rm["south"][0], rm["north"][0]))
    if a.json:
        json.dump({"regions": rows}, open(a.json, "w", encoding="utf-8"), indent=1)
        print("region_room: %s" % a.json)
    return verdict.write("region_room", verdict.PASS, counts={"regions": len(rows),
                         "overflowing": sum(1 for r in rows if r["overflow_mm"])},
                         denominator=len(rows), evidence=ev[:20], inputs={"board": a.board, "table": table},
                         note="the room each region has to grow into, and what stops it")


def _fixed_refs():
    """The references `gen_pcb_b3.py` places at planned positions: they are the blockers a region must respect."""
    import re
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen_pcb_b3.py")
    s = open(p, encoding="utf-8").read()
    m = re.search(r"^FIXED = \{(.*?)\n\n", s, re.S | re.M)
    return set(re.findall(r'"([A-Za-z_0-9]+)":', m.group(1))) if m else set()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
