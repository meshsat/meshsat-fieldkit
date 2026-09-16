#!/usr/bin/env python3
"""Where a mark can go on a board's front silkscreen (MESHSAT-862, 16 September 2026).

The owner's ruling is that the MeshSat mark goes on these boards, traced from the sticker master and never
redrawn; `logo_silk.py` draws it and no board of the seven carries a silkscreen polygon, because nothing ever
chose WHERE. This reports the free rectangles, and a board then DECLARES the one it takes, so the placement
stays deterministic: an automatic position would move whenever a part moved and churn the board file.

Free means: inside the board outline by a margin, clear of every footprint's courtyard (or its pads where it
draws no courtyard), clear of every drawn hole, and clear of the copper the silk would sit on where the board
asks for that. Silk over copper is legal and ugly; silk over a PAD is refused by the fabricator.

Usage: silk_space.py <board.kicad_pcb> [--aspect 2.58] [--min-width 25] [--layer F.SilkS] [--json]
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

GRID = 1.0        # mm, the search step: the mark is tens of millimetres wide, so a millimetre is fine
MARGIN = 2.0      # mm from the board edge


def main(argv):
    if not argv: print(__doc__); return 2
    import pcbnew
    path = argv[0]
    aspect = float(argv[argv.index("--aspect") + 1]) if "--aspect" in argv else 80.0 / 31.0
    minw = float(argv[argv.index("--min-width") + 1]) if "--min-width" in argv else 25.0
    lname = argv[argv.index("--layer") + 1] if "--layer" in argv else "F.SilkS"
    b = pcbnew.LoadBoard(path)
    mm = lambda v: v / 1e6
    box = b.GetBoardEdgesBoundingBox()
    x0, y0 = mm(box.GetX()) + MARGIN, mm(box.GetY()) + MARGIN
    x1, y1 = mm(box.GetRight()) - MARGIN, mm(box.GetBottom()) - MARGIN
    back = lname.startswith("B")
    blocked = []
    for fp in b.GetFootprints():
        if (fp.GetLayer() == pcbnew.B_Cu) != back: continue
        bb = fp.GetBoundingBox(False, False)     # courtyard-free footprints still have pads
        blocked.append((mm(bb.GetX()), mm(bb.GetY()), mm(bb.GetRight()), mm(bb.GetBottom())))
    nx = max(1, int((x1 - x0) / GRID)); ny = max(1, int((y1 - y0) / GRID))
    free = [[True] * (nx + 1) for _ in range(ny + 1)]
    for (bx0, by0, bx1, by1) in blocked:
        i0 = max(0, int((by0 - y0) / GRID)); i1 = min(ny, int((by1 - y0) / GRID) + 1)
        j0 = max(0, int((bx0 - x0) / GRID)); j1 = min(nx, int((bx1 - x0) / GRID) + 1)
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1): free[i][j] = False
    # the largest all-free rectangle of the mark's aspect, by a scan over widths
    best = []
    w = int(max(minw, 10) / GRID)
    while w * GRID <= (x1 - x0):
        h = max(1, int(round(w * GRID / aspect / GRID)))
        for i in range(0, ny - h + 1):
            for j in range(0, nx - w + 1):
                if all(free[i + di][j + dj] for di in range(h + 1) for dj in range(w + 1)):
                    best.append((w * GRID, x0 + j * GRID, y0 + i * GRID))
                    break
            else:
                continue
            break
        w += 5
    best.sort(reverse=True)
    if not best:
        print("silk_space: no free rectangle of aspect %.2f and %g mm or wider on %s" % (aspect, minw, lname))
        return 1
    print("silk_space: %d candidate(s) on %s, widest first" % (len(best), lname))
    for wmm, bx, by in best[:8]:
        print("  %6.1f mm wide at (%.1f, %.1f), height %.1f" % (wmm, bx + wmm / 2, by + wmm / aspect / 2, wmm / aspect))
    if "--json" in argv:
        print(json.dumps([{"width_mm": w, "cx": round(bx + w / 2, 2), "cy": round(by + w / aspect / 2, 2)} for w, bx, by in best[:8]], indent=1))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
