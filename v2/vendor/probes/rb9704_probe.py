import sys, zipfile, os
from build123d import import_step
z = zipfile.ZipFile(sys.argv[1]); name = z.namelist()[0]
if not os.path.exists(name): z.extract(name)
shape = import_step(name)
bb = shape.bounding_box()
print("BBOX X %.2f..%.2f  Y %.2f..%.2f  Z %.2f..%.2f  SIZE %.2f x %.2f x %.2f" % (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z, bb.size.X, bb.size.Y, bb.size.Z))
faces = shape.faces(); print("faces", len(faces))
pl = []
for f in faces:
    if f.geom_type.name == "PLANE":
        fb = f.bounding_box(); pl.append((f.area, f.center().Z, fb.min.X, fb.max.X, fb.min.Y, fb.max.Y))
pl.sort(key=lambda t: -t[0])
print("largest planes (area z X-range Y-range):")
for a, zc, x0, x1, y0, y1 in pl[:8]:
    print("  %8.1f z=%6.2f X %7.2f..%7.2f Y %7.2f..%7.2f" % (a, zc, x0, x1, y0, y1))
print("cylinders r<=3.5 (r, x, y, zrange), deduplicated by axis:")
seen = {}
for f in faces:
    if f.geom_type.name != "CYLINDER": continue
    r = f.radius
    if r is None or r > 3.5: continue
    fb = f.bounding_box(); cx = (fb.min.X + fb.max.X) / 2; cy = (fb.min.Y + fb.max.Y) / 2
    key = (round(r, 1), round(cx), round(cy))
    seen.setdefault(key, []).append((fb.min.Z, fb.max.Z))
for (r, x, y), zs in sorted(seen.items()):
    print("  r=%.1f x=%4d y=%4d z=%6.2f..%6.2f n=%d" % (r, x, y, min(a for a, b in zs), max(b for a, b in zs), len(zs)))
