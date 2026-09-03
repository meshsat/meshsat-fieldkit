#!/usr/bin/env python3
"""Numeric verification of PCB-C C3 (the panel in the Peli 1520PF frame) against Peli drawing 1523-314-000, the TD2 STEP and the MIL-STD-1472 layout rules."""
import sys, math, pcbnew
OX, OY = 297.0, 210.0
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
b = pcbnew.LoadBoard(sys.argv[1]); fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
segs = [(case(d.GetStart()), case(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
td2_segs = [sg for sg in segs if max(sg[0][1], sg[1][1]) < 60.0 and min(sg[0][1], sg[1][1]) > -70.0 and max(abs(sg[0][0]), abs(sg[1][0])) < 100.0]   # the display aperture only (the e-paper window sits at Y 73..127)
pts = [p for s in segs for p in s]
x0, x1, ybot, ytop = min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)
check(abs((x1 - x0) - 442.0) < 0.005 and abs((ytop - ybot) - 311.0) < 0.005 and abs(x0 + 221.0) < 0.005, "panel outline 442.000 x 311.000 centred (got %.3f x %.3f)" % (x1 - x0, ytop - ybot))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
# 1. the 16 frame screws on 431.8 x 301.2 (Peli 1523-314-000), Ø3.2 pads on GND
exp = [(x, y) for x in (-177.3, -88.6, 0.0, 88.6, 177.3) for y in (-150.6, 150.6)] + [(x, y) for x in (-215.9, 215.9) for y in (-110.7, 0.0, 110.7)]
holes = [fps["H%d" % i] for i in range(1, 17) if "H%d" % i in fps]
check(len(holes) == 16, "16 frame screw footprints (got %d)" % len(holes))
hp = [case(h.GetPosition()) for h in holes]
check(all(any(abs(p[0] - x) < 0.01 and abs(p[1] - y) < 0.01 for p in hp) for (x, y) in exp), "frame screws on the 431.8 x 301.2 pattern, no corner holes")
check(all(list(h.Pads())[0].GetDrillSize().x == pcbnew.FromMM(3.2) and list(h.Pads())[0].GetNetname() == "GND" for h in holes), "every frame screw is a Ø3.2 pad on GND (frame bond, MIL-STD-461)")
# 2. aperture (STEP body + 0.4) and the glass bearing band
ipts = [p for s in td2_segs for p in s if -200 < p[0] < 200 and -140 < p[1] < 140]
ax0, ax1, ay0, ay1 = min(p[0] for p in ipts), max(p[0] for p in ipts), min(p[1] for p in ipts), max(p[1] for p in ipts)
ex = (-85.275 - 2.935 - 0.4, 83.275 - 2.935 + 0.4, -49.855 - 10.0 - 0.4, 49.855 - 10.0 + 0.4)
check(all(abs(a - e) < 0.005 for a, e in zip((ax0, ax1, ay0, ay1), ex)), "aperture X %.3f..%.3f Y %.3f..%.3f = TD2 body + 0.4 per side" % (ax0, ax1, ay0, ay1))
gx0, gx1, gy0, gy1 = -94.66, 94.66, -70.12, 50.12
check(min(ax0 - gx0, gx1 - ax1, ay0 - gy0, gy1 - ay1) >= 6.0, "glass bears on the panel by >= 6 mm on every side")
check(gx1 <= 211.3 - 5 and gy1 <= 145.6 - 5 and gy0 >= -145.6 + 5, "glass outline inside the frame window (422.6 x 291.2) by 5 mm")
band = [z for z in b.Zones() if z.GetIsRuleArea() and "tape band" in z.GetZoneName()]
check(len(band) == 1 and band[0].GetDoNotAllowTracks() and band[0].GetDoNotAllowVias() and band[0].GetDoNotAllowPads(), "tape-band rule area present: no tracks, vias or pads under the glass flange")
# 3. panel controls: pitch >= 25 mm between switch centres, all inside the window by 3 mm, 3 mm clear of every frame screw, nothing but LEDs over the Pi stack
sw = {r: case(fp.GetPosition()) for r, fp in fps.items() if r.startswith("SW_")}
check(len(sw) == 7, "seven panel switches (got %d)" % len(sw))
pairs = [(a, c_) for i, a in enumerate(sw) for c_ in list(sw)[i + 1:]]
dmin = min(math.hypot(sw[a][0] - sw[c_][0], sw[a][1] - sw[c_][1]) for a, c_ in pairs)
check(dmin >= 25.0, "switch centre pitch >= 25 mm (MIL-STD-1472 gloved use), min %.1f" % dmin)
def bbox(fp):
    bb = fp.GetBoundingBox(False, False); return (bb.GetLeft() / 1e6 - OX, OY - bb.GetBottom() / 1e6, bb.GetRight() / 1e6 - OX, OY - bb.GetTop() / 1e6)
bad = []
for r, fp in fps.items():
    if r.startswith("H"): continue
    l, bt, rt, tp = bbox(fp)
    if fp.IsFlipped(): continue                                        # underside cluster: not on the visible face
    if l < -211.3 + 3 or rt > 211.3 - 3 or bt < -145.6 + 3 or tp > 145.6 - 3: bad.append(r + "@window")
    for (x, y) in exp:
        cx = max(l, min(x, rt)); cy = max(bt, min(y, tp))
        if math.hypot(cx - x, cy - y) < 1.7 + 3.0: bad.append(r + "@screw")
check(not bad, "every visible part inside the window by 3 mm and 3 mm clear of the frame screws (%s)" % bad)
stack = (-121.0, -48.5, -36.0, 48.5); over = []
for r, fp in fps.items():
    if r.startswith("H") or fp.IsFlipped(): continue
    l, bt, rt, tp = bbox(fp)
    if not (rt <= stack[0] or l >= stack[2] or tp <= stack[1] or bt >= stack[3]) and not r.startswith("D"): over.append(r)
check(not over, "only LEDs sit over the Pi + X1202 + cooler footprint (%s)" % over)
under = [r for r, fp in fps.items() if fp.IsFlipped()]
check(all(bbox(fps[r])[1] > 50 and bbox(fps[r])[0] > 130 for r in under if r not in ("J_X1202SW", "J_PIJ2", "R32", "R33")), "underside cluster stays on the back strip's east part")
check(b.GetCopperLayerCount() == 2 and b.GetDesignSettings().GetBoardThickness() == pcbnew.FromMM(2.0), "2 copper layers, 2.0 mm thick")
# e-paper recessed window (C4): aperture 94.19 x 53.6 centred on the module centre (30, 100), two tape lands and the body keep-out on the underside, nothing placed under the module
EPD_C = (30.0, 100.0)
win = [seg for seg in segs if 30 - 60 < min(seg[0][0], seg[1][0]) and max(seg[0][0], seg[1][0]) < 30 + 60 and 100 - 40 < min(seg[0][1], seg[1][1]) and max(seg[0][1], seg[1][1]) < 100 + 40]
if win:
    wx0 = min(min(a[0], b[0]) for a, b in win); wx1 = max(max(a[0], b[0]) for a, b in win); wy0 = min(min(a[1], b[1]) for a, b in win); wy1 = max(max(a[1], b[1]) for a, b in win)
    check(abs(wx1 - wx0 - 94.19) < 0.05 and abs(wy1 - wy0 - 53.6) < 0.05 and abs((wx0 + wx1) / 2 - EPD_C[0]) < 0.05 and abs((wy0 + wy1) / 2 - EPD_C[1]) < 0.05, "e-paper window 94.19 x 53.6 centred at (30, 100) (got %.2f x %.2f at %.2f, %.2f)" % (wx1 - wx0, wy1 - wy0, (wx0 + wx1) / 2, (wy0 + wy1) / 2))
else: check(False, "e-paper window present")
names = [z.GetZoneName() for z in b.Zones() if z.GetIsRuleArea()]
check(sum(1 for n in names if n.startswith("e-paper tape land")) == 2 and any(n.startswith("e-paper module body") for n in names), "e-paper underside rule areas (two lands, one body)")
mod = (EPD_C[0] - 52.9 - 1.0, EPD_C[1] - 26.9 - 1.0, EPD_C[0] + 52.9 + 1.0, EPD_C[1] + 26.9 + 1.0)
under = [fp.GetReference() for fp in b.GetFootprints() if fp.IsFlipped() and len(list(fp.Pads())) > 0 and not (fp.GetBoundingBox(False, False).GetRight() / 1e6 - OX < mod[0] or fp.GetBoundingBox(False, False).GetLeft() / 1e6 - OX > mod[2] or OY - fp.GetBoundingBox(False, False).GetTop() / 1e6 < mod[1] or OY - fp.GetBoundingBox(False, False).GetBottom() / 1e6 > mod[3])]
check(not under, "no underside part under the e-paper module (found %s)" % under)
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
