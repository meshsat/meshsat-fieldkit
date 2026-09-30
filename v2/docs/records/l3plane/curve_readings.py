#!/usr/bin/env python3
"""curve_readings.py: the makers' own efficiency curves for board E's stage (LT8705A) and board A's front end (LM5176),
read at their nearest printed operating points (stream l3plane, MESHSAT-1357, 30 September 2026; the independent check
CHECK-1 of 6a283b25, item B2).

Every figure printed is INFERRED: a reading of a TYPICAL curve (TA 25 C) of the maker's own demonstration circuit, at an
operating point near but not equal to the kit's, by pixel from the page rendered at 300 dpi. It is not a figure the maker
states for board E or board A, and it establishes no efficiency for either.

How: pdftoppm renders the page; the plot's frame is found by its dark lines inside a stated window and checked against
the gridlines the axis labels imply (refuse, exit 3, if they are not where the scale puts them); the curve is found by its
colour in a column at each current, away from the gridlines and the legend, and its centre line is mapped to the scale.

Run from the repository root:  python3 v2/docs/records/l3plane/curve_readings.py > v2/docs/records/l3plane/curve_readings.out
Needs pdftoppm and Pillow. Deterministic for the pinned PDFs."""
import hashlib
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
from PIL import Image  # noqa: E402
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import netlist_sexp as N  # noqa: E402
NET_E = "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"

LM5176 = ("v2/vendor/ti/lm5176-datasheet.pdf", 9)
LT8705A = ("v2/vendor/power/lt8705a.pdf", 41)


def refuse(msg):
    sys.stderr.write("curve_readings: %s; refusing\n" % msg)
    sys.exit(3)


def render(rel, page):
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", "300", "-png", os.path.join(TOP, rel),
                        os.path.join(td, "p")], check=True)
        name = [f for f in os.listdir(td) if f.endswith(".png")][0]
        im = Image.open(os.path.join(td, name)).convert("RGB")
        im.load()
        return im


def dark(p):
    return p[0] < 80 and p[1] < 80 and p[2] < 80


def frame(im, xr, yr, min_h, min_v):
    px = im.load()
    rows = [y for y in range(*yr) if sum(1 for x in range(*xr) if dark(px[x, y])) > min_h]
    cols = [x for x in range(*xr) if sum(1 for y in range(*yr) if dark(px[x, y])) > min_v]
    groups = []
    for v in rows:
        if groups and v - groups[-1][-1] <= 1:
            groups[-1].append(v)
        else:
            groups.append([v])
    cg = []
    for v in cols:
        if cg and v - cg[-1][-1] <= 1:
            cg[-1].append(v)
        else:
            cg.append([v])
    return [sum(g) / len(g) for g in groups], [sum(g) / len(g) for g in cg]


def read(im, box, xscale, yscale, xs, is_colour, ymax=None, skip=()):
    """The curve's centre, in axis units, in the column of each x, from the pixels is_colour accepts."""
    (left, top, right, bot), (x0, x1), (y0, y1) = box, xscale, yscale
    px = im.load()
    out = []
    for x in xs:
        cx = int(round(left + (right - left) * (x - x0) / (x1 - x0)))
        ys = []
        for dx in range(-3, 4):
            ys += [y for y in range(int(top) + 4, int(ymax or bot) - 4) if is_colour(px[cx + dx, y])]
        if not ys:
            out.append((x, None))
            continue
        ys.sort()
        cl, cur = [], [ys[0]]
        for y in ys[1:]:
            if y - cur[-1] <= 3:
                cur.append(y)
            else:
                cl.append(cur)
                cur = [y]
        cl.append(cur)
        best = max(cl, key=len)
        yc = (best[0] + best[-1]) / 2.0
        out.append((x, y1 + (y0 - y1) * (yc - top) / (bot - top)))
    return out


def main():
    for rel, _pg in (LM5176, LT8705A):
        if not os.path.exists(os.path.join(TOP, rel)):
            refuse("%s missing" % rel)
    P = print
    P("THE MAKERS' EFFICIENCY CURVES AT THEIR NEAREST PRINTED POINTS (curve_readings.py, stream l3plane, MESHSAT-1357).")
    P("Every figure INFERRED: a pixel reading of a TYPICAL curve (TA 25 C) of the maker's own demonstration circuit, not a")
    P("figure for board E or board A. Nothing is measured.")
    P("")
    # LM5176, SNVSAI1D p.9, Figure 6-2 (right plot): VOUT 12 V, fsw 300 kHz, L1 4.7 uH; y 80 to 100 %, x 0 to 6 A
    im = render(*LM5176)
    rows, cols = frame(im, (1400, 2260), (480, 1110), 600, 450)
    top = [r for r in rows if 500 < r < 530]
    bot = [r for r in rows if 1050 < r < 1090]
    left = [c for c in cols if 1420 < c < 1450]
    right = [c for c in cols if 2210 < c < 2240]
    if not (top and bot and left and right):
        refuse("SNVSAI1D p.9 Figure 6-2's frame not found")
    box = (left[0], top[0], right[0], bot[0])
    px = im.load()
    for v in (96, 92, 88, 84):
        y = int(round(box[1] + (100 - v) / 20.0 * (box[3] - box[1])))
        if sum(1 for x in range(int(box[0]) + 20, int(box[2]) - 20) if px[x, y][0] < 150) < 400:
            refuse("SNVSAI1D p.9 Figure 6-2's %d %% gridline is not where the scale puts it" % v)
    fh = hashlib.sha256(open(os.path.join(TOP, LM5176[0]), "rb").read()).hexdigest()[:16]
    pts = read(im, box, (0.0, 6.0), (80.0, 100.0), (2.5, 3.5, 4.5, 5.5, 5.9), dark)
    P("1. LM5176 (board A's front end, U2): TI SNVSAI1D %s sha256/16 %s, p.9 Figure 6-2 'Efficiency vs Load'," % (LM5176[0], fh))
    P("   VOUT 12 V, fsw 300 kHz, L1 4.7 uH, the VIN = 9 V curve: a boost at a ratio of 1.33 (board A: 15.1 V to 20 V, 1.32).")
    P("   " + "; ".join("%.1f A %.1f %%" % (x, v) for x, v in pts if v is not None))
    fe = [v for x, v in pts if x >= 5.5 and v is not None]
    P("   READING at 5.5 to 6 A (board A's front end carries U3's 6.1 A): %.1f to %.1f %% (INFERRED). Board A differs: 20 V out," % (min(fe), max(fe)))
    e6 = [v for x, v in pts if x == 5.9 and v is not None][0] / 100.0      # the reading nearest 6 A
    i_plot = 12.0 * 6.0 / e6 / 9.0
    i_board = 6.1 * 20.0 / 0.93 / 15.1
    P("   about 200 kHz, 10 uH, CSD19532Q5B. The plot's load current is its OUTPUT current: at 6 A out its 9 V curve draws about")
    P("   %.1f A in (12 V x 6 A / %.3f / 9 V), close to board A's %.1f A in at 6.1 A out (6.1 A x 20 V / 0.93 / 15.1 V): the" % (
        i_plot, e6, i_board))
    P("   currents are alike, the voltages and the circuit are not (second issue: CHECK-2 minor 6 corrected this sentence).")
    P("")
    # LT8705A, 8705af p.41: 12 V 15 A converter from 7.5 V to 55 V; y 80 to 100 %, x 0 to 15 A
    im = render(*LT8705A)
    rows, cols = frame(im, (1700, 2280), (1850, 2400), 380, 380)
    top = [r for r in rows if 1860 < r < 1890]
    bot = [r for r in rows if 2355 < r < 2385]
    left = [c for c in cols if 1730 < c < 1755]
    right = [c for c in cols if 2225 < c < 2250]
    if not (top and bot and left and right):
        refuse("8705af p.41's efficiency frame not found (top %s bottom %s left %s right %s)" % (top, bot, left, right))
    box = (left[0], top[0], right[0], bot[0])
    px = im.load()
    for v in (96, 92, 88, 84):
        y = int(round(box[1] + (100 - v) / 20.0 * (box[3] - box[1])))
        if sum(1 for x in range(int(box[0]) + 20, int(box[2]) - 20) if px[x, y][0] < 200) < 250:
            refuse("8705af p.41's %d %% gridline is not where the scale puts it" % v)
    legend_top = box[1] + (100 - 86.5) / 20.0 * (box[3] - box[1])      # the legend box starts below 86.5 %

    def green(p):
        return p[1] > 100 and p[0] < 110 and p[2] < 130 and p[1] - p[0] > 40

    def blue(p):
        return p[2] > 140 and p[0] < 110 and p[2] - p[0] > 60
    xs = (1.0, 1.5, 2.0, 3.0, 4.5, 6.0, 7.5, 9.0, 10.5, 12.0, 13.5, 14.6)
    g = read(im, box, (0.0, 15.0), (80.0, 100.0), xs, green, ymax=legend_top)
    b = read(im, box, (0.0, 15.0), (80.0, 100.0), xs, blue, ymax=legend_top)
    fh = hashlib.sha256(open(os.path.join(TOP, LT8705A[0]), "rb").read()).hexdigest()[:16]
    t41 = subprocess.run(["pdftotext", "-layout", "-f", "41", "-l", "41", os.path.join(TOP, LT8705A[0]), "-"],
                         capture_output=True, text=True, check=True).stdout
    e = N.load(os.path.join(TOP, NET_E))
    q3, q4 = e["components"]["Q3"]["value"].split(" ")[0], e["components"]["Q4"]["value"].split(" ")[0]
    same = "M1: INFINEON %s" % q3 in t41 and "M2: INFINEON %s" % q4 in t41
    P("2. LT8705A (board E's tracker stage, U5): ADI 8705af %s sha256/16 %s, p.41 '12V, 15A Output Converter Accepts" % (LT8705A[0], fh))
    P("   7.5V to 55V Input', 'Efficiency vs Output Current'. Its buck switches M1 and M2 %s board E's Q3 %s and Q4 %s as" % (
        "ARE" if same else "are NOT", q3, q4))
    P("   generated (NETLIST %s; ARRAY.md section 6's draft moves both to an 80 or 100 V part for the 2S2P array):" % NET_E)
    P("   VIN 35 V (a buck, 35 to 12 V; board E: 34.3 to 15.1 V): " + "; ".join("%.1f A %.1f %%" % (x, v) for x, v in g if v is not None))
    P("   VIN 20 V: " + "; ".join("%.1f A %.1f %%" % (x, v) for x, v in b if v is not None))
    st = [v for x, v in g if 6.0 <= x <= 12.0 and v is not None]
    P("   READING at 6 to 12 A on the 35 V curve (board E's stage delivers up to about 12 A at 15.1 V): %.1f to %.1f %% (INFERRED)." % (min(st), max(st)))
    P("   At light load the curve falls: the 1 to 3 A readings above (the steep part of the curve, where a pixel is worth more).")
    P("")
    P("3. WHAT THE READINGS ARE NOT: a figure for board E or board A, at their voltages, frequencies, inductors, FETs,")
    P("   copper or temperature, or weighted over the reference day's hours. They show")
    P("   that the makers' own designs run above the energy model's declared 0.93 at the nearest points; they do not")
    P("   establish 0.93, or any other figure, for the kit.")
    P("")
    P("END.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
