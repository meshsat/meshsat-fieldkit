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
check(abs(x1 - x0 - 285) < 0.01 and abs(y1 - y0 - 60) < 0.01 and abs(y1 + 51) < 0.01, "strip 285 x 60 at Y -111..-51 (got X %.1f..%.1f Y %.1f..%.1f)" % (x0, x1, y0, y1))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
for ref, (x, y) in (("H1", (-110.5, -73.0)), ("H2", (110.5, -73.0))):
    p = case(fps[ref].GetPosition()) if ref in fps else None
    check(p is not None and abs(p[0] - x) < 0.01 and abs(p[1] - y) < 0.01 and abs(list(fps[ref].Pads())[0].GetDrillSize().x / 1e6 - 3.2) < 0.01, "%s rod pass-through Ø3.2 at (%.1f, %.1f)" % (ref, x, y))
jd = fps.get("J_DOCK"); bb = jd.GetBoundingBox(False, False) if jd else None
check(all(not fp.IsFlipped() for fp in b.GetFootprints()), "no part on the underside (it sits on the floor)")
for ref in ("J_DCIN", "F1", "U1", "U2", "R3", "R4", "U3", "Q1", "D1", "U4", "Q2", "U5", "L1", "R5", "J_SOLAR", "F2", "J_BATT", "J_BLK", "P_CP", "P_CN", "J_TS", "J_KS"): check(ref in fps, "%s present" % ref)
# E4 height rule (32.18, 32.19 AO): every part north of Y -80 is under PCB-A at 13.4 mm; the tall parts must sit south of it
TALL = {"F1": 16.3, "F2": 16.3, "J_BATT": 10.5, "J_DCIN": 8.0, "J_SOLAR": 8.0, "J_TS": 7.5, "J_KS": 7.5, "C11": 7.7, "C12": 7.7, "C24": 6.9, "C25": 6.9, "L1": 10.0, "U1": 10.2}
for ref, h in TALL.items():
    if ref in fps:
        bb = fps[ref].GetBoundingBox(False, False); top = OY - bb.GetTop() / 1e6
        check(h <= 12.0 or top <= -80.0, "%s (%.1f mm tall) sits south of the PCB-A edge or under 12 mm (top edge at Y %.1f)" % (ref, h, top))
for (x, y) in [(-153.0, -74.5), (-118.0, -74.5), (-153.0, -65.5), (-118.0, -65.5)]: check(find((x, y), 3.2) is not None, "block standoff hole at (%.1f, %.1f)" % (x, y))
for x, cy in [(-100, -66), (-84, -66), (-26, -66), (-12, -66), (70, -66), (92, -66), (103, -64)]:
    check(find((x, cy - 10.0), 3.2) is not None and find((x, cy + 10.0), 3.2) is not None, "float clamp holes at X %.0f" % x)
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
