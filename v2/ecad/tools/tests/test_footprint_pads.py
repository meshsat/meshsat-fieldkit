#!/usr/bin/env python3
"""No generated land may short itself (MESHSAT-862, 12 September 2026).

The agentic loop's legality guard measured B19's PLACED board at 150 hard DRC violations, and 126 of
them were pad against pad. They were not a placement overlap: they were pads of the SAME part, on the
two host-select mux lands drawn on 9 September from TI's own drawings. A land pattern whose own pads
overlap makes every instance of that part unbuildable, and six of them sit on this board.

Nothing had ever asked. `test_footprint_library.py` checks that a generator does not name a stock land
directly and that the lands it writes exist; it does not look at the geometry. This does, and it is the
cheapest possible rule: **two pads with different numbers may not overlap.** Overlap, not clearance,
because clearance depends on the net class and the board, and overlap is wrong on every board there is.

It reads the `.kicad_mod` files as text, so it runs anywhere, with no KiCad.
"""
import os, re, glob
from harness import Skip   # noqa: F401

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRETTY = os.path.join(os.path.dirname(TOOLS), "meshsat.pretty")

# A land whose own pads touch ON PURPOSE, with the reason. The Skyworks part merges its ground land into
# the exposed soldering area and the data sheet draws it that way, so the two pieces are both pad "2".
ALLOW = {("Skyworks_SKY13351_MLPD-6_1x1mm", "2", "2"): "the ground land runs into the exposed area, data sheet 201132I figure 12"}


def _pads(path):
    """[(number, x, y, w, h, layers)] of every pad with a footprint-relative position."""
    t = open(path, errors="replace").read()
    out = []
    for m in re.finditer(r'\(pad\s+"([^"]*)"\s+(\w+)\s+(\w+)\s*\(at ([-\d.]+) ([-\d.]+)(?:\s+[-\d.]+)?\)\s*\(size ([\d.]+) ([\d.]+)\)([^\n]*)', t):
        num, _kind, shape, x, y, w, h, rest = m.groups()
        if not num:                      # an unnumbered pad is paste or mask, not copper
            continue
        if '"F.Cu"' not in rest and '"B.Cu"' not in rest and "*.Cu" not in rest:
            continue
        out.append((num, float(x), float(y), float(w), float(h), shape))
    return out


def _overlap(a, b):
    """Rectangles, which is the generous reading: a round or oval pad fits inside its own box."""
    ax0, ax1 = a[1] - a[3] / 2, a[1] + a[3] / 2
    ay0, ay1 = a[2] - a[4] / 2, a[2] + a[4] / 2
    bx0, bx1 = b[1] - b[3] / 2, b[1] + b[3] / 2
    by0, by1 = b[2] - b[4] / 2, b[2] + b[4] / 2
    dx = min(ax1, bx1) - max(ax0, bx0)
    dy = min(ay1, by1) - max(ay0, by0)
    return (dx, dy) if (dx > 1e-6 and dy > 1e-6) else None


def t_no_generated_land_shorts_itself():
    if not os.path.isdir(PRETTY):
        raise Skip("no meshsat.pretty beside the tools")
    bad = []
    for path in sorted(glob.glob(os.path.join(PRETTY, "*.kicad_mod"))):
        name = os.path.basename(path)[:-10]
        pads = _pads(path)
        for i in range(len(pads)):
            for j in range(i + 1, len(pads)):
                a, b = pads[i], pads[j]
                if a[0] == b[0]:
                    continue                       # two pieces of one pad are one net by construction
                o = _overlap(a, b)
                if not o:
                    continue
                if (name, a[0], b[0]) in ALLOW or (name, b[0], a[0]) in ALLOW:
                    continue
                bad.append("%s: pad %s at (%.3f, %.3f) %.2fx%.2f overlaps pad %s at (%.3f, %.3f) %.2fx%.2f "
                           "by %.3f x %.3f mm" % (name, a[0], a[1], a[2], a[3], a[4], b[0], b[1], b[2], b[3], b[4], o[0], o[1]))
    if bad:
        raise AssertionError("%d land(s) short themselves, so every instance is unbuildable:\n  %s"
                             % (len(bad), "\n  ".join(bad[:14])))
