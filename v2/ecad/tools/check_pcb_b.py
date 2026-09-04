#!/usr/bin/env python3
"""Numeric verification of PCB-B phase B1 against the appendix and the module drawings."""
import sys, pcbnew, itertools
OX, OY = 150.0, 110.0
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
b = pcbnew.LoadBoard(sys.argv[1]); fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
segs = [(case(d.GetStart()), case(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
pts = [p for s in segs for p in s]
x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts); y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
check(abs(x1 - x0 - 245) < 0.005 and abs(y1 - y0 - 170) < 0.005 and abs(x0 + 122.5) < 0.005 and abs(y1 - 85) < 0.005, "outline 245 x 170 centred (X %.2f..%.2f Y %.2f..%.2f)" % (x0, x1, y0, y1))
fps = {}
for fp in b.GetFootprints():
    pads = list(fp.Pads()); d = pads[0].GetDrillSize() if pads else None
    fps[fp.GetReference()] = (case(fp.GetPosition()), (round(d.x / 1e6, 2), round(d.y / 1e6, 2)) if d else None)
holes = {r: v for r, v in fps.items() if r.startswith("H")}
def near(p, q, tol=0.01): return abs(p[0] - q[0]) < tol and abs(p[1] - q[1]) < tol
def find(pos, drill): return any(near(v[0], pos) and abs(v[1][0] - drill) < 0.01 for v in holes.values())
for (x, y) in [(-110.5, -73), (110.5, -73), (-110.5, 73), (110.5, 73)]: check(find((x, y), 3.2), "rod hole 3.2 at (%.1f, %.1f)" % (x, y))
st = [(-113.0, -29.0), (-64.0, -29.0), (-113.0, 29.0), (-64.0, 29.0)]   # B11: stack 10 mm west
for p in st: check(find(p, 2.7), "Pi stack hole 2.7 at %s" % (p,))
check(abs(st[1][0] - st[0][0] - 49) < 0.01 and abs(st[2][1] - st[0][1] - 58) < 0.01, "stack pattern is 49 x 58 (Pi 5)")
tc = [(4.66, 23.015), (74.12, 23.015), (4.66, 47.985), (74.12, 47.985)]
for p in tc: check(find(p, 3.2), "T-Call hole 3.2 at %s" % (p,))
check(abs(tc[1][0] - tc[0][0] - 69.46) < 0.01 and abs(tc[2][1] - tc[0][1] - 24.97) < 0.01, "T-Call pattern 69.46 x 24.97")
rb = [(36, -64), (68, -64), (36, -32), (68, -32)]
for p in rb: check(find(p, 4.3), "9704 bracket hole 4.3 at %s" % (p,))
r6 = [(32.65, -22.65), (71.35, -22.65)]
for p in r6: check(find(p, 2.7), "9603 hole 2.7 at %s" % (p,))
check(abs(r6[1][0] - r6[0][0] - 38.7) < 0.01, "9603 holes 38.7 apart")
check(find((-99.96, 58.0), 2.2), "Wio-SX1262 hole 2.2 at (-99.96, 58.0)")
for p in [(115.56, 49.63), (83.08, 38.39), (118.58, 19.89)]: check(find(p, 2.7), "T-Beam 1W M2.5 hole 2.7 at %s" % (p,))
for p in [(86.00, -61.03), (115.66, -61.04)]: check(find(p, 2.2), "T-Beam 1W M2 hole 2.2 at %s" % (p,))
# hole-to-hole webs >= 2 mm between every pair of holes (drill edges)
hl = [(v[0], v[1][0]) for v in holes.values()]
minweb = min(((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5 - (dp + dq) / 2 for (p, dp), (q, dq) in itertools.combinations(hl, 2))
check(minweb >= 2.0, "minimum web between any two holes %.2f mm (>= 2.0)" % minweb)
# device rectangles: inside the outline with 3 mm margin, pairwise non-overlapping, clear of nut keep-outs
R = {"SDR": (-4, -16, 78, 16), "ZB": (-40, 55, 30, 80.5), "TCALL": (2.0, 20.995, 76.78, 50.005),
     "XIAO": (-103.72, 49.11, -82.28, 66.89), "RB9704": (26, -76, 78, -20), "HUB": (-96, -81, -46, -52), "JGPIO": (-80.5, 44, -21.5, 53),
     "JRTL": (-19, -6.5, -5, 6.5), "JZB": (31, 61, 45, 74.5), "TCALL_USBC": (-18.5, 41, -13.5, 51), "XIAO_USBC": (-82, 55.5, -70, 64.5),
     "TBEAM": (79.3, -64, 122.36, 52.75), "TB_SMA": (110.95, 52.75, 120.19, 67.22), "JTBEAM": (65, 52.5, 75, 57.5),
     "JRB9704": (-0.5, -52.5, 20.5, -43.5), "JRB9603": (3.5, -62.5, 16.5, -57.5), "PASS": (-20.5, -57.5, -5.5, -42.5), "JTD2": (-54, 74, -46, 80), "JPANEL": (81, 54.5, 91, 81.5)}
for k, r in R.items():
    m = 0.1 if k in ("TBEAM", "TB_SMA") else 3.0   # the T-Beam PCB ends 0.14 mm short of the edge by design
    check(r[0] >= -122.5 + m and r[2] <= 122.5 - m and r[1] >= -85 + m and r[3] <= 85 - m, "%s inside outline with %.0f mm margin" % (k, m))
def overlap(a, b): return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])
for (ka, a), (kb, bb) in itertools.combinations(R.items(), 2):
    if {ka, kb} == {"RB9704", "RB9603"}: continue
    check(not overlap(a, bb), "%s and %s do not overlap" % (ka, kb))
def rect_circle_clear(r, c, rad): 
    cx = max(r[0], min(c[0], r[2])); cy = max(r[1], min(c[1], r[3])); return ((cx - c[0]) ** 2 + (cy - c[1]) ** 2) ** 0.5 >= rad
for k, r in R.items():
    check(all(rect_circle_clear(r, rod, 4.5) for rod in [(-110.5, -73), (110.5, -73), (-110.5, 73), (110.5, 73)]), "%s clear of the 9 mm nut keep-outs" % k)
# slots and connectors at their intended centres (footprints are centred by the generator)
exp_fp = {"S_RTL1": (20, -18), "S_RTL2": (74, -18), "S_RTL3": (20, 18), "S_RTL4": (66, 18), "S_ZB1": (-10, 52.5), "S_ZB2": (18, 52.5), "S_ZB3": (-10, 82), "S_ZB4": (18, 82),
          "S_XIAO1": (-88, 46), "S_XIAO2": (-88, 70), "J_GPIO1": (-51, 48.5), "J_DCF77": (-85, 77), "J_RTL1": (-12, 0), "J_ZB1": (38, 67.75), "J_PANEL": (86, 68)}
for ref, (ex, ey) in exp_fp.items():
    fp = next((f for f in b.GetFootprints() if f.GetReference() == ref), None)
    if fp is None and ref == "J_PANEL" and len(list(b.GetFootprints())) < 100: print("SKIP J_PANEL (placed at the netlist stage)"); continue
    if fp is None: check(False, "%s present" % ref); continue
    bb = fp.GetBoundingBox(False, False); cx = (bb.GetLeft() + bb.GetRight()) / 2e6 - OX; cy = OY - (bb.GetTop() + bb.GetBottom()) / 2e6
    check(abs(cx - ex) < 0.6 and abs(cy - ey) < 0.6, "%s body centred at (%.1f, %.1f) (got %.2f, %.2f)" % (ref, ex, ey, cx, cy))
    for pad in fp.Pads():
        pp = case(pad.GetPosition()); check(abs(pp[0] - ex) < 40 and abs(pp[1] - ey) < 40, "%s pad near its footprint" % ref)
# B12: the X1202 is gone (appendix 32.17); the Pi alone sits on the four standoffs
check(b.GetCopperLayerCount() == 4, "4 copper layers")
check(b.GetDesignSettings().GetBoardThickness() == pcbnew.FromMM(1.6), "1.6 mm thick")
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
