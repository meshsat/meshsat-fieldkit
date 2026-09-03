import sys
from build123d import import_step
shape = import_step(sys.argv[1])
bb = shape.bounding_box()
print("BBOX X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f" % (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z))
print("SIZE %.3f x %.3f x %.3f" % (bb.size.X, bb.size.Y, bb.size.Z))
faces = shape.faces()
print("faces:", len(faces))
# footprint of everything below given Z levels (rear side), to find the hump outline
for zc in (-1.0, -2.5, -4.0, -6.0, -9.0, -12.0):
    xs=[];ys=[]
    for f in faces:
        fb = f.bounding_box()
        if fb.max.Z <= zc:
            xs += [fb.min.X, fb.max.X]; ys += [fb.min.Y, fb.max.Y]
    if xs:
        print("below Z=%6.2f: X %8.2f..%8.2f  Y %8.2f..%8.2f" % (zc, min(xs), max(xs), min(ys), max(ys)))
# planar faces: report the largest few by area with their Z (front glass, rear plates)
pl = [(f.area, f.center().Z, f.bounding_box()) for f in faces if f.geom_type.name == "PLANE"]
pl.sort(reverse=True)
print("largest planar faces (area, z, bbox):")
for a,z,fb in pl[:10]:
    print("  %9.1f  z=%7.2f  X %7.2f..%7.2f Y %7.2f..%7.2f" % (a, z, fb.min.X, fb.max.X, fb.min.Y, fb.max.Y))
# cylinders r 2.4..3.6 (standoff bodies)
print("cylinders r 2.4..3.6 (r, x, y, zmin, zmax):")
for f in faces:
    if f.geom_type.name != "CYLINDER": continue
    r = f.radius
    if r is None or r < 2.4 or r > 3.6: continue
    fb = f.bounding_box(); c = f.center()
    print("  r=%.2f x=%7.2f y=%7.2f z=%6.2f..%6.2f" % (r, (fb.min.X+fb.max.X)/2, (fb.min.Y+fb.max.Y)/2, fb.min.Z, fb.max.Z))
