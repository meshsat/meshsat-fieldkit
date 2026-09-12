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
            cand = (lo_x + dx0 * g, lo_y + dy0 * g, hi_x + dx1 * g, hi_y + dy1 * g)
            hit = None
            if outline and not (outline[0] <= cand[0] and cand[2] <= outline[2]
                                and outline[1] <= cand[1] and cand[3] <= outline[3]):
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


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("--json")
    ap.add_argument("--only")
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
    others = [(r["name"], r["rect"], r["side"]) for r in regions]
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
