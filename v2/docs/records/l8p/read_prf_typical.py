#!/usr/bin/env python3
"""read_prf_typical.py: the reading of Murata's typical R-T curve for the BB characteristic (record l8p, round 5, MESHSAT-1357,
4 October 2026). A reading aid, not a gate: it prints the table that l8p_drafts.py carries as PRF_BB_TYP, labelled INFERRED.

Murata's PRF series sheet (v2/vendor/battery/murata-prf-series.pdf, DM-SA16-E056 Rev.1 201608) draws the resistance change R/R25
against temperature only as a TYPICAL curve (3.2, p.5, "Graph-1"; 3.3.2 calls it "typical curve"), one curve per temperature
characteristic code (BG to BA, AR, AS), normalised to R25 and not drawn per resistance group. The figure has no text layer, so the
curve is read from the page's raster:
  1. pdftoppm renders page 5 at 400 dpi (poppler-utils);
  2. the axes are calibrated on the page's own grid: the decade lines 1000, 100 and 10 at 626 px a decade, and the 5 C columns;
  3. the BB curve is followed from R/R25 = 2.0 (the sixth steep curve from the left, about 100 C): row by row upwards on its steep
     part, column by column leftwards on its flat part, taking the stroke's centre;
  4. below about 73 C the B curves merge into one stroke, so the flat part is reported only down to 77 C, and the figure's lowest
     stroke (any curve, -20 to 125 C) and the bundle's top edge at -20 C are reported as bounds instead.
The reading's resolution is about 0.2 K and 1 % of R/R25 at 400 dpi; the curve itself is typical. Needs pdftoppm and Pillow; run
from the repository root:  python3 v2/docs/records/l8p/read_prf_typical.py  (writes its raster only into a temporary folder)."""
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
SHEET = os.path.join(ROOT, "v2", "vendor", "battery", "murata-prf-series.pdf")
DPI = 400
DEC = 626.0                       # px a decade at 400 dpi (the 1000, 100 and 10 lines at 845.5, 1469.0 and 2097.5)
Y1 = 2723.5                       # R/R25 = 1 (from the decade lines; the 0.9, 0.8 and 0.7 lines read at 2755, 2785 and 2824)
PX_K = 2 * 5.972                  # px a kelvin (the 5 C columns, -20 C at x = 700)
X_M20 = 700.0


def X(t):
    return X_M20 + PX_K * (t + 20.0)


def T(x):
    return (x - X_M20) / PX_K - 20.0


def Y(r):
    return Y1 - DEC * math.log10(r)


def R(y):
    return 10 ** ((Y1 - y) / DEC)


def main():
    try:
        from PIL import Image
    except ImportError:
        print("read_prf_typical: Pillow is not installed"); return 2
    with tempfile.TemporaryDirectory(prefix="l8p_prf_") as d:
        subprocess.run(["pdftoppm", "-f", "5", "-l", "5", "-r", str(DPI), "-png", SHEET, os.path.join(d, "p")], check=True)
        png = [f for f in os.listdir(d) if f.endswith(".png")][0]
        im = Image.open(os.path.join(d, png)).convert("L")
    px = im.load()
    dark = lambda x, y: px[x, y] < 110
    gridx = {x for x in range(int(X(-20)) - 3, int(X(160)) + 3) if dark(x, int(Y(0.15)))}

    def runs_row(y, x0, x1):
        g = []
        for x in range(x0, x1):
            if dark(x, y):
                if g and x - g[-1][-1] <= 1: g[-1].append(x)
                else: g.append([x])
        return [(a[0] + a[-1]) / 2.0 for a in g if len(a) >= 5]

    def runs_col(x, y0, y1):
        g = []
        for y in range(y0, y1):
            if dark(x, y):
                if g and y - g[-1][-1] <= 1: g[-1].append(y)
                else: g.append([y])
        return [((a[0] + a[-1]) / 2.0, len(a)) for a in g if len(a) >= 7]

    # the steep part, row by row upwards from R/R25 = 2.0 at about 100 C
    pts = {}
    y = int(Y(2.0)); xs = [c for c in runs_row(y, int(X(95)), int(X(105)))]
    x = min(xs, key=lambda c: abs(c - X(100.4)))
    while y > int(Y(470.0)):
        cs = [c for c in runs_row(y, int(x) - 30, int(x) + 30) if not any(abs(c - g) <= 2 for g in gridx)]
        if cs:
            x = min(cs, key=lambda c: abs(c - x))
            pts[round(R(y), 4)] = round(T(x), 2)
        y -= 1
    steep = sorted((t, r) for r, t in pts.items())
    # the flat part, column by column leftwards from 100 C
    yc = Y(2.0); flat = []
    for xi in range(int(X(100.4)), int(X(77.0)), -1):
        if any(abs(xi - g) <= 2 for g in gridx):
            continue
        cs = runs_col(xi, int(yc) - 30, int(yc) + 30)
        if not cs:
            continue
        c = min(cs, key=lambda c: abs(c[0] - yc))
        yc = c[0]
        flat.append((round(T(xi), 2), round(R(yc), 4)))
    # bounds: the lowest stroke of any curve from -20 to 125 C, and the bundle's top edge at -20 C
    low = None
    for xi in range(int(X(-20)) + 3, int(X(125))):
        if any(abs(xi - g) <= 2 for g in gridx):
            continue
        cs = runs_col(xi, int(Y(1.6)), int(Y(0.5)))
        if cs:
            c = max(cs, key=lambda c: c[0])
            if low is None or c[0] > low[0]:
                low = (c[0], xi)
    xt = int(X(-19.5))
    while any(abs(xt - g) <= 2 for g in gridx):
        xt += 1
    cs = [c for c in runs_col(xt, int(Y(2.0)) + 4, int(Y(0.9)))]
    top = min(c[0] - c[1] / 2.0 for c in cs)
    print("read_prf_typical: Murata DM-SA16-E056 Rev.1, 3.2 (p.5), the BB curve, R/R25 against T (typical, read at %d dpi)" % DPI)
    table = sorted(set([(t, r) for t, r in flat if t >= 77.0][::12] + [s for s in steep][::25]))
    for t, r in table:
        print("  %7.2f C  %9.4f" % (t, r))
    print("  the lowest stroke of any curve, -20 to 125 C: R/R25 %.3f at %.1f C" % (R(low[0]), T(low[1])))
    print("  the bundle's top edge at -19.5 C: R/R25 %.3f" % R(top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
