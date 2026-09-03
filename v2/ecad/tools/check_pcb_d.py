#!/usr/bin/env python3
"""Numeric verification of PCB-D phase D1 against PCB-A's site and the DMR858M datasheet."""
import sys, pcbnew, itertools, math
OX, OY = 100.0, 100.0
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
b = pcbnew.LoadBoard(sys.argv[1]); fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
segs = [(case(d.GetStart()), case(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
pts = [p for s in segs for p in s]
x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts); y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
check(abs(x1 - x0 - 80) < 0.005 and abs(y1 - y0 - 62) < 0.005 and abs(x0 + 40) < 0.005 and abs(y1 - 31) < 0.005, "outline 80 x 62 centred (X %.2f..%.2f Y %.2f..%.2f)" % (x0, x1, y0, y1))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
holes = {r: (case(fp.GetPosition()), round(list(fp.Pads())[0].GetDrillSize().x / 1e6, 2)) for r, fp in fps.items() if r.startswith("H")}
def find(pos, drill): return any(abs(v[0][0] - pos[0]) < 0.01 and abs(v[0][1] - pos[1]) < 0.01 and abs(v[1] - drill) < 0.01 for v in holes.values())
for (x, y) in [(-35, -26), (35, -26), (-35, 26), (35, 26)]: check(find((x, y), 3.2), "M3 standoff hole 3.2 at (%d, %d) = PCB-A site (10/80, +-26)" % (x, y))
# module pads: 24, two rows 2.54 pitch, per datasheet V1.2 p.10 (rotated: SMA east)
u2 = fps.get("U2"); check(u2 is not None, "U2 DMR858M placed")
if u2:
    pads = {p.GetNumber(): case(p.GetPosition()) for p in u2.Pads() if p.GetNumber()}
    check(len(pads) == 24, "U2 has 24 pads (%d)" % len(pads))
    mc = case(u2.GetPosition()); ys = sorted(set(round(p[1], 2) for p in pads.values()))
    check(len(ys) == 2 and abs(ys[1] - ys[0] - 36.15) < 0.02, "two pin rows %.3f mm apart (module 38.69 wide, holes 1.27 mm inboard)" % (ys[1] - ys[0] if len(ys) == 2 else 0))
    for n in range(1, 12): check(abs(pads[str(n)][0] - pads[str(n + 1)][0] - 2.54) < 0.01 and pads[str(n)][1] > mc[1], "pin %d east of pin %d by 2.54 on the NORTH row (datasheet front-left row)" % (n, n + 1))
    for n in range(13, 24): check(abs(pads[str(n + 1)][0] - pads[str(n)][0] - 2.54) < 0.01 and pads[str(n)][1] < mc[1], "pin %d east of pin %d by 2.54 on the SOUTH row (datasheet front-right row)" % (n + 1, n))
    drills = {round(p.GetDrillSize().x / 1e6, 2) for p in u2.Pads() if p.GetNumber()}
    check(drills == {1.0}, "module pin holes drill 1.0 for 2.54 mm sockets (%s)" % sorted(drills))
    npth = [case(p.GetPosition()) for p in u2.Pads() if not p.GetNumber()]
    exp = [(mc[0] + 58.31 / 2 - 2.81, mc[1] + 38.69 / 2 - 2.96), (mc[0] - 58.31 / 2 + 2.86, mc[1] - 38.69 / 2 + 2.73)]
    check(len(npth) == 2 and all(any(abs(a[0] - e[0]) < 0.01 and abs(a[1] - e[1]) < 0.01 for a in npth) for e in exp), "two M2.5 standoff holes at the module's 3.00 mm holes (NE 2.81/2.96, SW 2.86/2.73)")
    check(abs(pads["1"][0] - pads["24"][0]) < 0.01 and abs(pads["12"][0] - pads["13"][0]) < 0.01, "rows aligned: pin 1 over pin 24, pin 12 over pin 13")
    check(abs(pads["1"][0] - (mc[0] + 14.095)) < 0.01, "pin 1 at 15.06 mm from the module's SMA edge (%.3f)" % (pads["1"][0] - mc[0]))
    check(mc[0] + 58.31 / 2 <= 41.5 and mc[0] - 58.31 / 2 >= -20.0, "module PCB (58.31 long) with its SMA end at most 1.5 mm past the east edge (centre X %.2f)" % mc[0])
# connectors where the harness expects them; everything inside the outline; nothing on a standoff face
for ref, (ex, ey) in {"J_HARN1": (-33, 6), "J_PWR1": (-33, -14)}.items():
    fp = fps.get(ref)
    if fp is None: check(False, "%s present" % ref); continue
    bb = fp.GetBoundingBox(False, False); cx = (bb.GetLeft() + bb.GetRight()) / 2e6 - OX; cy = OY - (bb.GetTop() + bb.GetBottom()) / 2e6
    check(abs(cx - ex) < 0.6 and abs(cy - ey) < 0.6, "%s body centred at (%.1f, %.1f) (got %.2f, %.2f)" % (ref, ex, ey, cx, cy))
bad = []
for ref, fp in fps.items():
    if ref.startswith("H"): continue
    bb = fp.GetBoundingBox(False, False); l, r_, t, bt = bb.GetLeft() / 1e6 - OX, bb.GetRight() / 1e6 - OX, OY - bb.GetTop() / 1e6, OY - bb.GetBottom() / 1e6
    if ref == "U2":   # the module body: 58.31 x 38.69 around its centre, SMA end may pass the edge by 1.5 mm
        mc = case(fp.GetPosition()); l, r_, bt, t = mc[0] - 29.155, min(mc[0] + 29.155, 39.7), mc[1] - 19.345, mc[1] + 19.345
    if l < -39.7 or r_ > 39.7 or bt < -30.7 or t > 30.7: bad.append(ref)
    for (sx, sy) in [(-35, -26), (35, -26), (-35, 26), (35, 26)]:
        cx = max(l, min(sx, r_)); cy = max(bt, min(sy, t))
        if math.hypot(cx - sx, cy - sy) < 3.75: bad.append(ref + "@standoff")
check(not bad, "all footprints inside the outline and off the standoff faces (%s)" % bad)
check(b.GetCopperLayerCount() == 4, "4 copper layers"); check(b.GetDesignSettings().GetBoardThickness() == pcbnew.FromMM(1.6), "1.6 mm thick")
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
