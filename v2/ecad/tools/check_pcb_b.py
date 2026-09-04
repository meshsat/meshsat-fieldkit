#!/usr/bin/env python3
"""Numeric verification of PCB-B (B13) against the appendix and the module drawings."""
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
rb = [(36, -64), (68, -64), (36, -32), (68, -32)]
for p in rb: check(find(p, 4.3), "9704 bracket hole 4.3 at %s" % (p,))
r6 = [(32.65, -22.65), (71.35, -22.65)]
for p in r6: check(find(p, 2.7), "9603 hole 2.7 at %s" % (p,))
check(abs(r6[1][0] - r6[0][0] - 38.7) < 0.01, "9603 holes 38.7 apart")
placed = len(list(b.GetFootprints())) > 100          # the netlist stage has run: the module, the socket and the small parts are on the board
for (x, y) in [(-104.5, -24.0), (-104.5, 24.0), (-71.5, -24.0), (-71.5, 24.0)]:
    check(find((x, y), 2.7), "CM5 M2.5 hole 2.7 at (%.1f, %.1f) (module 55 x 40 centred (-88, 0), holes 33 x 48)" % (x, y))
if placed:
    for ref, cx in (("U30A", -105.0), ("U30B", -71.0)):
        f = next((f for f in b.GetFootprints() if f.GetReference() == ref), None)
        check(f is not None, "%s (CM5 receptacle) present" % ref)
        if f is None: continue
        smd = [case(p.GetPosition()) for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
        check(len(smd) == 100, "%s has 100 pads (got %d)" % (ref, len(smd)))
        xs = sorted(set(round(p[0], 2) for p in smd)); ys = sorted(set(round(p[1], 2) for p in smd))
        check(len(xs) == 2 and abs(xs[1] - xs[0] - 3.08) < 0.02 and abs((xs[0] + xs[1]) / 2 - cx) < 0.05, "%s rows 3.08 mm apart centred x %.1f (got %s)" % (ref, cx, xs))
        check(len(ys) == 50 and abs(ys[-1] - ys[0] - 19.6) < 0.02 and abs((ys[0] + ys[-1]) / 2 + 2.5) < 0.05, "%s 50 positions at 0.4 mm over 19.6 mm centred y -2.5 (got %d over %.2f)" % (ref, len(ys), ys[-1] - ys[0]))
        check(all(-108 < p[0] < -68 and -27.5 < p[1] < 27.5 for p in smd), "%s pads inside the module outline" % ref)
    for ref in ("J_LTE1", "J_SIM1", "U40", "U41", "U42", "J_DISP", "J_FLASH", "J_AB1", "BT1", "J_FAN", "U1", "U20", "U21", "U31", "U32", "U34"):
        check(ref in fps, "%s present" % ref)
    if "J_LTE1" in fps:
        j = next(f for f in b.GetFootprints() if f.GetReference() == "J_LTE1")
        lt = [case(p.GetPosition()) for p in j.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH]
        check(len(lt) == 2, "LTE socket carries its two M2.5 standoff holes (got %d)" % len(lt))
        bb = j.GetBoundingBox(False, False); r = (bb.GetLeft() / 1e6 - OX, OY - bb.GetBottom() / 1e6, bb.GetRight() / 1e6 - OX, OY - bb.GetTop() / 1e6)
        check(-33 <= r[0] and r[2] <= 27 and 51 <= r[1] and r[3] <= 83, "LTE card and socket inside the north band (-32..26, 52..82) (got %.1f..%.1f, %.1f..%.1f)" % r)
    j = next((f for f in b.GetFootprints() if f.GetReference() == "J_AB1"), None)
    if j is not None: check(j.IsFlipped(), "J_AB1 on the underside")
# hole-to-hole webs >= 2 mm between every pair of holes (drill edges), NPTH pads of the module and the socket included
hl = [(v[0], v[1][0]) for v in holes.values()]
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH and fp.GetReference() not in holes: hl.append((case(p.GetPosition()), p.GetDrillSize().x / 1e6))
minweb = min(((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5 - (dp + dq) / 2 for (p, dp), (q, dq) in itertools.combinations(hl, 2))
check(minweb >= 2.0, "minimum web between any two holes %.2f mm (>= 2.0)" % minweb)
# device rectangles: inside the outline with 3 mm margin, pairwise non-overlapping, clear of nut keep-outs
R = {"CM5": (-108, -27.5, -68, 27.5), "COOLER": (-108.5, -28, -67.5, 28), "SDR": (-4, -16, 78, 16), "RB9704": (26, -76, 78, -20),
     "HUB": (-66, -34, -22, -14), "BUCK": (-58, -84, -36, -60), "CM5X": (-58, -58, -22, -36), "FLASH": (-24, -84, -14, -66), "CTRL": (-119.5, -64, -100, -30),
     "PWR": (-86, -72, -62, -44), "MODC": (-119.5, -18, -110, 0), "LTE": (-32, 52, 26, 82), "LTEP": (-62, 40, -20, 51), "GNSS": (-118, 44, -96, 66), "LORA": (-94, 44, -74, 66),
     "ZB": (84, 16, 104, 52), "ZBP": (105, 16, 118, 40), "TPS": (84, -60, 104, -30), "RB": (-19, -40, 15, -19.5), "JRTL": (-19, -6.5, -5, 6.5), "JPANEL": (81, 54.5, 91, 81.5),
     "JRB9704": (-0.5, -52.5, 20.5, -43.5), "JRB9603": (3.5, -62.5, 16.5, -57.5), "PASS": (-20.5, -57.5, -5.5, -42.5), "JTD2": (-46, 74, -38, 80), "JDCF": (-91, 74, -79, 80),
     "JFLASH": (-35, -82.5, -25, -73.5), "JDISP": (-57, 6, -43, 14), "JSIM": (-51.5, 52.5, -38.5, 67.5), "BT1": (-58.5, 16.5, -33.5, 39.5), "JFAN": (-67, 32, -61, 36),
     "JV_M": (-98, -72, -86, -52), "JV_PI": (-118, -28, -110, -20)}
for k, r in R.items():
    m = 3.0
    check(r[0] >= -122.5 + m and r[2] <= 122.5 - m and r[1] >= -85 + m and r[3] <= 85 - m, "%s inside outline with %.0f mm margin" % (k, m))
def overlap(a, b): return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])
for (ka, a), (kb, bb) in itertools.combinations(R.items(), 2):
    if {ka, kb} in ({"CM5", "COOLER"},): continue
    check(not overlap(a, bb), "%s and %s do not overlap" % (ka, kb))
def rect_circle_clear(r, c, rad):
    cx = max(r[0], min(c[0], r[2])); cy = max(r[1], min(c[1], r[3])); return ((cx - c[0]) ** 2 + (cy - c[1]) ** 2) ** 0.5 >= rad
for k, r in R.items():
    check(all(rect_circle_clear(r, rod, 4.5) for rod in [(-110.5, -73), (110.5, -73), (-110.5, 73), (110.5, 73)]), "%s clear of the 9 mm nut keep-outs" % k)
# slots and connectors at their intended centres (footprints are centred by the generator)
exp_fp = {"S_RTL1": (20, -18), "S_RTL2": (74, -18), "S_RTL3": (20, 18), "S_RTL4": (66, 18), "J_DCF77": (-85, 77), "J_RTL1": (-12, 0), "J_PANEL": (86, 68), "U30A": (-105, -2.5), "U30B": (-71, -2.5), "J_FLASH": (-30, -78), "J_DISP": (-50, 10)}
for ref, (ex, ey) in exp_fp.items():
    fp = next((f for f in b.GetFootprints() if f.GetReference() == ref), None)
    if fp is None and ref in ("J_PANEL", "U30A", "U30B", "J_FLASH", "J_DISP") and not placed: print("SKIP %s (placed at the netlist stage)" % ref); continue
    if fp is None: check(False, "%s present" % ref); continue
    bb = fp.GetBoundingBox(False, False); cx = (bb.GetLeft() + bb.GetRight()) / 2e6 - OX; cy = OY - (bb.GetTop() + bb.GetBottom()) / 2e6
    check(abs(cx - ex) < 0.6 and abs(cy - ey) < 0.6, "%s body centred at (%.1f, %.1f) (got %.2f, %.2f)" % (ref, ex, ey, cx, cy))
    for pad in fp.Pads():
        pp = case(pad.GetPosition()); check(abs(pp[0] - ex) < 40 and abs(pp[1] - ey) < 40, "%s pad near its footprint" % ref)
check(b.GetCopperLayerCount() == 4, "4 copper layers")
check(b.GetDesignSettings().GetBoardThickness() == pcbnew.FromMM(1.6), "1.6 mm thick")
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
