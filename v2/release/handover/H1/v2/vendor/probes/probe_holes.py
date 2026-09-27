import sys, math, time
from build123d import import_step
t0 = time.time()
path = sys.argv[1]
shape = import_step(path)
bb = shape.bounding_box()
print("BBOX X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f SIZE %.2f x %.2f x %.2f  (import %.0fs)" % (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z, bb.size.X, bb.size.Y, bb.size.Z, time.time()-t0))
faces = shape.faces(); print("faces", len(faces))
planes = [f for f in faces if f.geom_type.name == "PLANE"]
# largest horizontal planes (candidate PCB faces)
horiz = []
for f in planes:
    try:
        n = f.normal_at(); 
    except Exception: continue
    if abs(abs(n.Z) - 1.0) < 1e-3: horiz.append(f)
horiz.sort(key=lambda f: -f.area)
print("largest horizontal planes (area, z, bbox):")
for f in horiz[:8]:
    fb = f.bounding_box(); print("  area %.0f z %.2f  X %.2f..%.2f Y %.2f..%.2f" % (f.area, f.center().Z, fb.min.X, fb.max.X, fb.min.Y, fb.max.Y))
# vertical cylinders (holes / posts): radius 0.4..4.0, axis along Z
holes = {}
for f in faces:
    if f.geom_type.name != "CYLINDER": continue
    try:
        r = f.radius
    except Exception:
        continue
    fb = f.bounding_box()
    dz = fb.size.Z; dx = fb.size.X; dy = fb.size.Y
    if r is None: continue
    # axis along Z when the XY extent ~ 2r and Z extent > 0.5
    if abs(dx - 2*r) < 0.05 and abs(dy - 2*r) < 0.05 and dz > 0.5 and 0.4 <= r <= 4.0:
        c = ((fb.min.X + fb.max.X)/2, (fb.min.Y + fb.max.Y)/2)
        key = (round(c[0],1), round(c[1],1), round(r,2))
        holes.setdefault(key, []).append((round(fb.min.Z,2), round(fb.max.Z,2)))
print("vertical cylinders (x, y, r) -> z spans:")
for k in sorted(holes): print("  ", k, holes[k][:3])
# horizontal cylinders with r 2.9..3.4 (SMA thread) or 1.2..2 (USB-C shell corners) 
print("horizontal cylinders r 2.5..3.5 (SMA candidates):")
seen=set()
for f in faces:
    if f.geom_type.name != "CYLINDER": continue
    try: r = f.radius
    except Exception: continue
    if r is None or not (2.5 <= r <= 3.5): continue
    fb = f.bounding_box()
    if abs(fb.size.Z - 2*r) < 0.1 and (abs(fb.size.X - 2*r) < 0.1 or abs(fb.size.Y - 2*r) < 0.1):
        key=(round((fb.min.X+fb.max.X)/2,1), round((fb.min.Y+fb.max.Y)/2,1), round((fb.min.Z+fb.max.Z)/2,1), round(r,2), round(max(fb.size.X,fb.size.Y),1))
        if key in seen: continue
        seen.add(key); print("  ", key)
print("done %.0fs" % (time.time()-t0))
