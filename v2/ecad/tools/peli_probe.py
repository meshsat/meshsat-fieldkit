#!/usr/bin/env python3
"""Numbers from Peli's CAD for the case integration (appendix 23.1). Usage: peli_probe.py <case bottom STEP> <case top STEP> <frame STEP>
Case models: Y is up, rim at Y = 0. Frame model: Z is up, frame top at the largest horizontal face level.
Prints depths, outlines, the frame's window, body, skirt and insert-hole pattern, and the case wall drill points."""
import sys
from build123d import import_step
def planes(shape):
    out = []
    for f in shape.faces():
        if f.geom_type.name != "PLANE": continue
        fb = f.bounding_box(); out.append((f.area, fb))
    return out
def levels(pl, axis):   # horizontal faces (constant on the given axis) grouped by level
    lv = {}
    for a, fb in pl:
        lo, hi = getattr(fb.min, axis), getattr(fb.max, axis)
        if abs(hi - lo) < 0.01: lv.setdefault(round(lo, 2), []).append((a, fb))
    return lv
def report_case(bottom, top):
    b = import_step(bottom); bb = b.bounding_box(); pl = planes(b); lv = levels(pl, "Y")
    inner = {y: [(a, f2) for a, f2 in v if f2.size.X < bb.size.X - 5 and f2.size.Z < bb.size.Z - 5] for y, v in lv.items()}   # faces strictly inside the shell
    floor_y, floor = max(((y, max(v, key=lambda t: t[0])) for y, v in inner.items() if y < -5 and v), key=lambda t: t[1][0])
    print("CASE BOTTOM: exterior %.1f x %.1f, height %.1f (Y %.2f..%.2f)" % (bb.size.X, bb.size.Z, bb.size.Y, bb.min.Y, bb.max.Y))
    print("  floor at Y %.2f: %.1f x %.1f (X %.2f..%.2f, Z %.2f..%.2f)  -> base cavity depth %.2f" % (floor_y, floor[1].size.X, floor[1].size.Z, floor[1].min.X, floor[1].max.X, floor[1].min.Z, floor[1].max.Z, -floor_y))
    walls = [(a, fb) for a, fb in pl if abs(fb.max.X - fb.min.X) < 0.05 and fb.size.Y > 20]
    for a, fb in sorted(walls, key=lambda t: -t[0])[:6]: print("  end wall face at X %.2f, Y %.2f..%.2f, Z +-%.2f (area %.0f)" % (fb.min.X, fb.min.Y, fb.max.Y, fb.max.Z, a))
    walls = [(a, fb) for a, fb in pl if abs(fb.max.Z - fb.min.Z) < 0.05 and fb.size.Y > 20]
    for a, fb in sorted(walls, key=lambda t: -t[0])[:6]: print("  side wall face at Z %.2f, Y %.2f..%.2f, X +-%.2f (area %.0f)" % (fb.min.Z, fb.min.Y, fb.max.Y, fb.max.X, a))
    print("  wall drill points (cylinders r 2..3):")
    for f in b.faces():
        if f.geom_type.name != "CYLINDER" or f.radius is None or not 2 <= f.radius <= 3: continue
        fb = f.bounding_box(); print("    r=%.2f at X %.1f Y %.1f Z %.1f" % (f.radius, (fb.min.X + fb.max.X) / 2, (fb.min.Y + fb.max.Y) / 2, (fb.min.Z + fb.max.Z) / 2))
    t = import_step(top); tb = t.bounding_box(); tl = levels(planes(t), "Y")
    tin = {y: [(a, f2) for a, f2 in v if f2.size.X < tb.size.X - 5 and f2.size.Z < tb.size.Z - 5] for y, v in tl.items()}
    ceil_y, ceil = max(((y, max(v, key=lambda q: q[0])) for y, v in tin.items() if y > 5 and v), key=lambda q: q[1][0])
    print("CASE TOP (lid): height %.1f; ceiling at Y %.2f: %.1f x %.1f -> lid cavity depth %.2f" % (tb.size.Y, ceil_y, ceil[1].size.X, ceil[1].size.Z, ceil_y))
def report_frame(frame):
    f = import_step(frame); fb = f.bounding_box(); pl = planes(f); lv = levels(pl, "Z")
    print("FRAME: outer %.2f x %.2f, height %.2f (Z %.2f..%.2f)" % (fb.size.X, fb.size.Y, fb.size.Z, fb.min.Z, fb.max.Z))
    for z, v in sorted(lv.items()):
        a = sum(q[0] for q in v); big = max(v, key=lambda q: q[0])[1]
        if a > 30: print("  level Z %.2f: area %.0f, extent %.2f x %.2f" % (z, a, big.size.X, big.size.Y))
    vx = [(a, fb2) for a, fb2 in pl if abs(fb2.max.X - fb2.min.X) < 0.05 and fb2.size.Y > 50]
    vy = [(a, fb2) for a, fb2 in pl if abs(fb2.max.Y - fb2.min.Y) < 0.05 and fb2.size.X > 50]
    for a, fb2 in sorted(vx, key=lambda q: -q[0])[:6]: print("  vertical face X %.2f: Y +-%.2f, Z %.2f..%.2f" % (fb2.min.X, fb2.max.Y, fb2.min.Z, fb2.max.Z))
    for a, fb2 in sorted(vy, key=lambda q: -q[0])[:6]: print("  vertical face Y %.2f: X +-%.2f, Z %.2f..%.2f" % (fb2.min.Y, fb2.max.X, fb2.min.Z, fb2.max.Z))
    print("  cylinders (holes and corners):")
    seen = set()
    for fc in f.faces():
        if fc.geom_type.name != "CYLINDER" or fc.radius is None: continue
        fb2 = fc.bounding_box(); key = (round(fc.radius, 2), round((fb2.min.X + fb2.max.X) / 2, 1), round((fb2.min.Y + fb2.max.Y) / 2, 1))
        if key in seen: continue
        seen.add(key); print("    r=%.2f at (%.1f, %.1f) Z %.2f..%.2f" % (key[0], key[1], key[2], fb2.min.Z, fb2.max.Z))
if __name__ == "__main__":
    report_case(sys.argv[1], sys.argv[2]); report_frame(sys.argv[3])
