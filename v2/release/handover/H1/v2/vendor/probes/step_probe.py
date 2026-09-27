import sys, zipfile, os
from build123d import import_step
path = sys.argv[1]
if path.endswith('.zip'):
    z = zipfile.ZipFile(path); name = [n for n in z.namelist() if n.lower().endswith(('.step','.stp'))][0]
    if not os.path.exists(name): z.extract(name)
    path = name
shape = import_step(path)
bb = shape.bounding_box()
print("BBOX X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f SIZE %.2f x %.2f x %.2f" % (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z, bb.size.X, bb.size.Y, bb.size.Z))
faces = shape.faces(); print("faces", len(faces))
planes = sorted([f for f in faces if f.geom_type.name == "PLANE"], key=lambda f: -f.area)
print("largest planes:")
for f in planes[:6]:
    b = f.bounding_box(); print("  %8.1f z=%7.2f X %7.2f..%7.2f Y %7.2f..%7.2f" % (f.area, f.center().Z, b.min.X, b.max.X, b.min.Y, b.max.Y))
pcb = planes[0]
print("largest plane outer wire vertices:", [(round(v.X, 2), round(v.Y, 2)) for v in pcb.outer_wire().vertices()][:40])
print("largest plane inner wires (holes) with size >= 1.8 mm:")
for w in pcb.inner_wires():
    b = w.bounding_box()
    if b.size.X >= 1.8 or b.size.Y >= 1.8:
        print("   centre (%.2f, %.2f) size %.2f x %.2f" % ((b.min.X+b.max.X)/2, (b.min.Y+b.max.Y)/2, b.size.X, b.size.Y))
print("cylinders 1.2 <= r <= 3.5:")
seen = {}
for f in faces:
    if f.geom_type.name != "CYLINDER": continue
    r = f.radius
    if r is None or r < 1.2 or r > 3.5: continue
    b = f.bounding_box(); key = (round(r, 2), round((b.min.X+b.max.X)/2, 1), round((b.min.Y+b.max.Y)/2, 1)); seen.setdefault(key, []).append((b.min.Z, b.max.Z))
for (r, x, y), zs in sorted(seen.items()):
    print("   r=%.2f x=%7.2f y=%8.2f z=%6.2f..%6.2f" % (r, x, y, min(a for a, b in zs), max(b for a, b in zs)))
