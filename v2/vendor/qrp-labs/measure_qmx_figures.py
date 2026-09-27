#!/usr/bin/env python3
"""Scale the QRP Labs QMX's end panels and top face from the maker's own figures (MESHSAT-1357, 27 Sep 2026, the QMX lid tray r2, S-63).

The maker states the enclosure as "95 x 63 x 25mm without protrusions" (qmx-product-page-2026-09-27.txt; assembly manual 1.04r page 2,
qmx-assembly-1_04r-pages-1-3-20-21-75-78.pdf) and draws its two end panels and its top face, undimensioned, in the operating manual 1_04_004
(qmx-operating-manual-1_04_004.pdf pages 7, 8 and 13). The three figures are the manual's embedded rasters, extracted pixel for pixel
(`pdfimages -png`, poppler) into qmx-crops/opman-1_04_004-p7-left-panel.png, -p8-right-panel.png and -p13-top-face.png. This script:

  1. finds each panel figure's outline and scales it to the maker's 63 x 25 panel (the outlines' aspect is printed as the check: a figure
     that is not to scale would not come out at 2.52);
  2. scales every closed hole inside the outline (jack holes and the four corner screws) to mm, from the panel's left edge as the figure is
     drawn (the panel seen from outside, the top face up) and from its bottom edge;
  3. scales the top-face figure at the same mm per pixel (its short side is the 63 mm width; its long side then reads the extrusion between
     the two end panels) and finds the LCD window, the two encoder holes, the two button holes and the microphone hole;
  4. cross-checks the right panel against the maker's product photograph qmx-product-photo-qmx4-right-panel.jpg (the panel face on, from
     https://qrp-labs.com/images/qmx/1/qmx4.jpg): a homography from the four corner-screw centres, whose places the figure gives, maps the
     photograph's jack centres to panel mm. The pixel points were picked by the session on the full-resolution photograph over a 50 px grid
     (PHOTO_POINTS below; each within about 3 px, about 0.25 mm).

Nothing here is a maker dimension: every figure is SCALED from an undimensioned maker figure (INFERRED), and where the figure and the
photograph disagree the tray takes both (lid_tray_qmx_r2.py). Needs Pillow and numpy (v2/cad/requirements-cad.lock); no other library.
Usage: measure_qmx_figures.py [out file]   (prints the table; with an argument also writes it)."""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CROPS = os.path.join(HERE, "qmx-crops")
PANEL_MM = (63.0, 25.0)                      # the maker's end panel, width x height (the enclosure's 63 x 25 section)
LENGTH_MM = 95.0                             # the maker's overall length over the end panels
FIGURES = {"left": "opman-1_04_004-p7-left-panel.png", "right": "opman-1_04_004-p8-right-panel.png", "top": "opman-1_04_004-p13-top-face.png"}
PHOTO = "qmx-product-photo-qmx4-right-panel.jpg"
# photograph pixel points (x, y), picked by the session on the 1280 x 823 image: the four corner-screw centres and the three jack centres
PHOTO_POINTS = {"screw TL": (232, 283), "screw TR": (920, 293), "screw BL": (228, 505), "screw BR": (907, 540),
                "RF": (287, 420), "PTT": (522, 460), "USB": (667, 480), "USB left end": (610, 480), "USB right end": (725, 480),
                "USB top": (667, 460), "USB bottom": (667, 502)}


def _close(mask):
    """A one-pixel binary closing (dilate, then erode) with a 3 x 3 square, numpy only."""
    def shifted(m, fill):
        p = np.pad(m, 1, constant_values=fill)
        return [p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    d = np.logical_or.reduce(shifted(mask, False))
    return np.logical_and.reduce(shifted(d, True))


def _components(free):
    """4-connected components of a boolean image: a list of (ys, xs) arrays, numpy plus an explicit stack."""
    H, W = free.shape
    seen = np.zeros_like(free, dtype=bool)
    out = []
    for y0 in range(H):
        for x0 in range(W):
            if not free[y0, x0] or seen[y0, x0]:
                continue
            stack = [(y0, x0)]; seen[y0, x0] = True; ys = []; xs = []
            while stack:
                y, x = stack.pop(); ys.append(y); xs.append(x)
                for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= ny < H and 0 <= nx < W and free[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; stack.append((ny, nx))
            out.append((np.array(ys), np.array(xs)))
    return out


def panel(name):
    a = np.asarray(Image.open(os.path.join(CROPS, FIGURES[name])).convert("L")).astype(float)
    ys, xs = np.nonzero(a < 128)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    sx, sy = PANEL_MM[0] / (x1 - x0), PANEL_MM[1] / (y1 - y0)
    holes = []
    for ys_, xs_ in _components(~_close(a < 160)):
        if ys_.min() <= y0 or ys_.max() >= y1 or xs_.min() <= x0 or xs_.max() >= x1:
            continue                                               # the outside, or the panel's own face
        w, h = xs_.max() - xs_.min() + 1, ys_.max() - ys_.min() + 1
        if w < 30 or h < 20 or w > 300:
            continue                                               # letters, the corner screws' inner rings, the face
        cx, cy = (xs_.min() + xs_.max()) / 2.0, (ys_.min() + ys_.max()) / 2.0
        holes.append(((cx - x0) * sx, (y1 - cy) * sy, w * sx, h * sy))
    return dict(px=(x0, x1, y0, y1), aspect=(x1 - x0) / float(y1 - y0), mm_per_px=(sx, sy), holes=sorted(holes))


def top_face(mm_per_px):
    a = np.asarray(Image.open(os.path.join(CROPS, FIGURES["top"])).convert("RGB")).astype(int)
    blue = (a[:, :, 2] > 150) & (a[:, :, 0] < 150)
    ys, xs = np.nonzero(blue)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    s = mm_per_px
    out = dict(px=(x0, x1, y0, y1), width_mm=(y1 - y0) * s, length_mm=(x1 - x0) * s)
    comps = []
    for ys_, xs_ in _components(~_close(blue)):
        if ys_.min() <= y0 or ys_.max() >= y1 or xs_.min() <= x0 or xs_.max() >= x1:
            continue
        w, h = xs_.max() - xs_.min() + 1, ys_.max() - ys_.min() + 1
        if 20 <= w <= 80 and 20 <= h <= 80:
            comps.append(((xs_.min() + xs_.max()) / 2.0, (ys_.min() + ys_.max()) / 2.0, w, h))
    # the LCD window: the rounded rectangle whose outline crosses column 340 inside the band between the grooves
    col = [y for y in range(y0 + 1, y1) if blue[y, 340]]
    inner = [y for y in col if 110 < y < 360]
    row = [x for x in range(x0 + 1, x1) if blue[(inner[0] + inner[-1]) // 2, x]]
    out["lcd_px"] = (row[0], row[-1], inner[0], inner[-1])
    out["circles_px"] = sorted(comps)
    return out, (x0, y0)


def homography(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    return np.linalg.svd(np.array(A, float))[2][-1].reshape(3, 3)


def main(argv):
    L, R = panel("left"), panel("right")
    lines = ["QMX end panels and top face scaled from the maker's undimensioned figures (operating manual 1_04_004 pp. 7, 8, 13) to the maker's",
             "63 x 25 panel; SCALED, INFERRED, not maker dimensions. Positions: x from the panel's left edge as drawn (the panel seen from outside,",
             "top face up), y from its bottom edge; hole sizes are the figure's openings.", ""]
    for nm, P in (("LEFT panel (p. 7: Paddle, Audio, DC)", L), ("RIGHT panel (p. 8: RF, PTT, USB)", R)):
        lines.append("%s: outline %d..%d x %d..%d px, aspect %.3f (63/25 = 2.520), %.4f x %.4f mm/px" % ((nm,) + tuple(P["px"]) + (P["aspect"],) + tuple(P["mm_per_px"])))
        for x, y, w, h in P["holes"]:
            lines.append("  hole  x %5.1f  y %5.1f   %4.1f x %4.1f" % (x, y, w, h))
    s = (L["mm_per_px"][0] + R["mm_per_px"][0]) / 2.0
    T, (tx0, ty0) = top_face(s)
    lines += ["", "TOP face (p. 13) at %.4f mm/px (the panels' scale): outline %d..%d x %d..%d px = %.1f long x %.1f wide mm" % ((s,) + tuple(T["px"]) + (T["length_mm"], T["width_mm"])),
              "  (the long side is the extrusion between the end panels: %.1f against the maker's 95 overall, so each end panel stands about %.1f;"
              % (T["length_mm"], (LENGTH_MM - T["length_mm"]) / 2.0),
              "   x below is from the LEFT end panel's outer face (VOL side), y from the BACK long edge (the edge away from the knobs))"]
    pan = (LENGTH_MM - T["length_mm"]) / 2.0
    lx0, lx1, ly0, ly1 = T["lcd_px"]
    lines.append("  LCD window  x %5.1f .. %5.1f   y %5.1f .. %5.1f" % ((lx0 - tx0) * s + pan, (lx1 - tx0) * s + pan, (ly0 - ty0) * s, (ly1 - ty0) * s))
    for cx, cy, w, h in T["circles_px"]:
        lines.append("  circle      x %5.1f   y %5.1f   d %4.1f   (%.1f from the front, knob, edge)" % ((cx - tx0) * s + pan, (cy - ty0) * s, w * s, T["width_mm"] - (cy - ty0) * s))
    # photograph cross-check of the right panel
    src = [(3.0, 22.0), (60.0, 22.0), (3.0, 3.0), (60.0, 3.0)]
    dst = [PHOTO_POINTS[k] for k in ("screw TL", "screw TR", "screw BL", "screw BR")]
    Hinv = homography(dst, src)
    lines += ["", "RIGHT panel on the maker's photograph %s (homography on the four corner screws at x 3/60, y 3/22 of the figure):" % PHOTO]
    for k in ("RF", "PTT", "USB", "USB left end", "USB right end", "USB top", "USB bottom"):
        p = Hinv @ np.array([PHOTO_POINTS[k][0], PHOTO_POINTS[k][1], 1.0]); x, y = p[:2] / p[2]
        lines.append("  %-13s x %5.1f  y %5.1f" % (k, x, y))
    txt = "\n".join(lines) + "\n"
    sys.stdout.write(txt)
    if len(argv) > 1:
        open(argv[1], "w", encoding="utf-8").write(txt)


if __name__ == "__main__":
    main(sys.argv)
