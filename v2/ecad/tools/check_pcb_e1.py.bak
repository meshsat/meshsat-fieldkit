#!/usr/bin/env python3
"""Numeric verification of PCB-E1 DOCK: outline, rod pass-throughs, the target block where PCB-A's J_DOCK lands, nothing on the underside."""
import sys, pcbnew
OX, OY = 150.0, 110.0
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
b = pcbnew.LoadBoard(sys.argv[1]); fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
segs = [(case(d.GetStart()), case(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
pts = [p for s in segs for p in s]; x0, x1, y0, y1 = min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)
check(abs(x1 - x0 - 250) < 0.01 and abs(y1 - y0 - 44) < 0.01 and abs(y1 + 51) < 0.01, "strip 250 x 44 at Y -95..-51 (got X %.1f..%.1f Y %.1f..%.1f)" % (x0, x1, y0, y1))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
for ref, (x, y) in (("H1", (-110.5, -73.0)), ("H2", (110.5, -73.0))):
    p = case(fps[ref].GetPosition()) if ref in fps else None
    check(p is not None and abs(p[0] - x) < 0.01 and abs(p[1] - y) < 0.01 and abs(list(fps[ref].Pads())[0].GetDrillSize().x / 1e6 - 3.2) < 0.01, "%s rod pass-through Ø3.2 at (%.1f, %.1f)" % (ref, x, y))
jd = fps.get("J_DOCK"); bb = jd.GetBoundingBox(False, False) if jd else None
check(jd is not None and abs((bb.GetLeft() + bb.GetRight()) / 2e6 - OX + 12.0) < 0.3 and abs(OY - (bb.GetTop() + bb.GetBottom()) / 2e6 + 70.0) < 0.3, "J_DOCK target block centred at (-12, -70) = PCB-A's J_DOCK pins")
check(all(not fp.IsFlipped() for fp in b.GetFootprints()), "no part on the underside (it sits on the floor)")
for ref in ("J_DCIN", "F1", "U1", "U2", "R3", "R4", "J_AUX", "Q1", "D1"): check(ref in fps, "%s present" % ref)
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
