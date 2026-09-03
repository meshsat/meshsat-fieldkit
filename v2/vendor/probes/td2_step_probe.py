# Probe the official Touch Display 2 (7 inch) STEP: bbox, and every cylindrical face with r <= 3 mm (holes / standoffs)
import sys
from build123d import import_step, Axis
path = sys.argv[1]
shape = import_step(path)
bb = shape.bounding_box()
print("BBOX min", tuple(round(v,3) for v in (bb.min.X, bb.min.Y, bb.min.Z)), "max", tuple(round(v,3) for v in (bb.max.X, bb.max.Y, bb.max.Z)))
print("SIZE", round(bb.size.X,3), round(bb.size.Y,3), round(bb.size.Z,3))
solids = shape.solids()
print("solids:", len(solids))
cyl = []
for f in shape.faces():
    if f.geom_type.name != "CYLINDER":
        continue
    try:
        r = f.radius
    except Exception:
        continue
    if r is None or r > 3.5:
        continue
    c = f.center()
    ax = f.normal_at(f.center()) if False else None
    cyl.append((round(r,3), round(c.X,2), round(c.Y,2), round(c.Z,2)))
# collapse duplicates (same r and XY within 0.05)
seen = {}
for r,x,y,z in cyl:
    key = (r, round(x*2)/2, round(y*2)/2)
    seen.setdefault(key, []).append(z)
print("small cylinders (r, x, y): z-range, count")
for (r,x,y), zs in sorted(seen.items()):
    print(f"  r={r:5.2f}  x={x:8.2f}  y={y:8.2f}  z={min(zs):7.2f}..{max(zs):7.2f}  n={len(zs)}")
