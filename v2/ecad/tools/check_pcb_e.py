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
check(abs(x1 - x0 - 267) < 0.01 and abs(y1 - y0 - 68) < 0.01 and abs(y1 + 45) < 0.01 and abs(x1 - 118) < 0.01, "strip 267 x 68 at X -149..118, Y -113..-45 (got X %.1f..%.1f Y %.1f..%.1f)" % (x0, x1, y0, y1))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
for ref, (x, y) in (("H1", (-110.5, -73.0)), ("H2", (110.5, -73.0))):
    p = case(fps[ref].GetPosition()) if ref in fps else None
    check(p is not None and abs(p[0] - x) < 0.01 and abs(p[1] - y) < 0.01 and abs(list(fps[ref].Pads())[0].GetDrillSize().x / 1e6 - 3.2) < 0.01, "%s rod pass-through Ø3.2 at (%.1f, %.1f)" % (ref, x, y))
jd = fps.get("J_DOCK"); bb = jd.GetBoundingBox(False, False) if jd else None
check(all(not fp.IsFlipped() for fp in b.GetFootprints()), "no part on the underside (it sits on the floor)")
for ref in ("J_DCIN", "F1", "U3", "Q1", "D1", "U6", "Q7", "L2", "U4", "Q2", "U5", "L1", "R5", "J_SOLAR", "F2", "J_BATT", "F3", "J_BLK", "P_CP", "P_CN", "U10", "U11", "U12", "U13", "U14", "U15", "J_SMB", "J_POD", "J_FAN1", "J_FAN2"): check(ref in fps, "%s present" % ref)
def find(xy, d):
    for r, f in fps.items():
        if r.startswith("H") and abs(case(f.GetPosition())[0] - xy[0]) < 0.05 and abs(case(f.GetPosition())[1] - xy[1]) < 0.05 and abs(list(f.Pads())[0].GetDrillSize().x / 1e6 - d) < 0.05: return f
    return None
# E4 height rule (32.18, 32.19 AO): every part north of Y -80 is under PCB-A at 13.4 mm; the tall parts must sit south of it
TALL = {"F1": 16.3, "F2": 16.3, "F3": 16.3, "J_BATT": 10.5, "J_DCIN": 8.0, "J_SOLAR": 8.0, "C11": 7.7, "C12": 7.7, "C24": 6.9, "C25": 6.9, "L1": 10.0, "L2": 8.0, "J_SMB": 14.0, "J_POD": 14.0, "J_LTG": 14.0, "J_GEIGER": 14.0, "J_DCF": 14.0, "J_FAN1": 14.0, "J_FAN2": 14.0}
for ref, h in TALL.items():
    if ref in fps:
        bb = fps[ref].GetBoundingBox(False, False); top = OY - bb.GetTop() / 1e6; right = bb.GetRight() / 1e6 - OX
        check(h <= 12.0 or top <= -80.0 or right <= -121.0, "%s (%.1f mm tall) sits south of the PCB-A edge, west of X -121 or under 12 mm (top edge Y %.1f, right edge X %.1f)" % (ref, h, top, right))
for (x, y) in [(-104.0, -63.0), (-66.0, -63.0), (-104.0, -83.0), (-66.0, -83.0)]: check(find((x, y), 3.2) is not None, "block standoff hole at (%.1f, %.1f)" % (x, y))
for x, cy in [(-52, -66), (-38, -66), (-24, -66), (-10, -66), (4, -66), (18, -66), (32, -66), (60, -66), (74, -66), (88, -66), (102, -66)]:
    check(find((x, cy - 10.0), 3.2) is not None and find((x, cy + 10.0), 3.2) is not None, "float clamp holes at X %.0f" % x)
# 8 Sep 2026 (MESHSAT-862 Stage C): the intent gates (return path under the pair-class nets, decoupling loops, the rails of the intent file)
if any(t.GetClass() == "PCB_TRACK" and not t.IsLocked() for t in b.GetTracks()):
    import os as _os3, sys as _sys3; _sys3.path.insert(0, _os3.path.dirname(_os3.path.abspath(__file__))); import intent_checks as _ic; print(_ic.run(b, check, sys.argv[1]))
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
