import sys, zipfile, os
from build123d import import_step
z = zipfile.ZipFile(sys.argv[1]); name = z.namelist()[0]
if not os.path.exists(name): z.extract(name)
shape = import_step(name)
faces = shape.faces()
# PCB top face = largest plane at z~1.5..1.6
pcb = max((f for f in faces if f.geom_type.name == "PLANE" and 1.4 < f.center().Z < 1.7), key=lambda f: f.area)
fb = pcb.bounding_box()
print("PCB top face bbox X %.2f..%.2f Y %.2f..%.2f z=%.2f area %.1f" % (fb.min.X, fb.max.X, fb.min.Y, fb.max.Y, pcb.center().Z, pcb.area))
ow = pcb.outer_wire()
vs = [(round(v.X, 2), round(v.Y, 2)) for v in ow.vertices()]
print("outer wire vertices (%d):" % len(vs))
# print vertices sorted along the perimeter as given
for v in vs: print("   ", v)
print("inner wires (holes) in the PCB top face: %d" % len(pcb.inner_wires()))
for w in pcb.inner_wires():
    wb = w.bounding_box()
    print("   hole bbox X %.2f..%.2f Y %.2f..%.2f -> centre (%.2f, %.2f) dia %.2f x %.2f" % (wb.min.X, wb.max.X, wb.min.Y, wb.max.Y, (wb.min.X+wb.max.X)/2, (wb.min.Y+wb.max.Y)/2, wb.size.X, wb.size.Y))
print("cylinders 1.0 <= r <= 3.5 (holes / standoffs / SMA):")
seen = {}
for f in faces:
    if f.geom_type.name != "CYLINDER": continue
    r = f.radius
    if r is None or r < 1.0 or r > 3.5: continue
    b = f.bounding_box(); cx = (b.min.X + b.max.X) / 2; cy = (b.min.Y + b.max.Y) / 2
    key = (round(r, 2), round(cx, 1), round(cy, 1)); seen.setdefault(key, []).append((b.min.Z, b.max.Z))
for (r, x, y), zs in sorted(seen.items()):
    print("   r=%.2f x=%7.2f y=%8.2f z=%6.2f..%6.2f" % (r, x, y, min(a for a, b in zs), max(b for a, b in zs)))
# tallest features above the PCB (connector, SMA) and below
print("planes above z>3 (top parts) and below z<0 (bottom parts), largest 6 each:")
for lo, hi in ((3.0, 99), (-99, -0.05)):
    pl = sorted([(f.area, f.center().Z, f.bounding_box()) for f in faces if f.geom_type.name == "PLANE" and lo < f.center().Z < hi], key=lambda t: -t[0])[:6]
    for a, zc, b in pl:
        print("   %7.1f z=%6.2f X %7.2f..%7.2f Y %8.2f..%8.2f" % (a, zc, b.min.X, b.max.X, b.min.Y, b.max.Y))
