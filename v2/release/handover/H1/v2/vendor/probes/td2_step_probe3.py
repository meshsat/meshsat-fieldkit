import sys
from build123d import import_step
shape = import_step(sys.argv[1])
faces = shape.faces()
pl = []
for f in faces:
    if f.geom_type.name != "PLANE": continue
    fb = f.bounding_box()
    pl.append((f.area, f.center().Z, fb.min.X, fb.max.X, fb.min.Y, fb.max.Y, fb.min.Z, fb.max.Z))
pl.sort(key=lambda t: -t[0])
print("largest planar faces: area  z  X-range  Y-range")
for a,z,x0,x1,y0,y1,z0,z1 in pl[:16]:
    print("  %9.1f  z=%7.2f  X %7.2f..%7.2f  Y %7.2f..%7.2f" % (a, z, x0, x1, y0, y1))
print("planar faces near the standoff positions (|x|~35.5 or 24.5), area>3:")
for a,z,x0,x1,y0,y1,z0,z1 in pl:
    cx=(x0+x1)/2; cy=(y0+y1)/2
    if a>3 and a<60 and (abs(abs(cx)-35.5)<1.5 or abs(abs(cx)-24.5)<1.5):
        print("  a=%6.1f z=%6.2f x=%6.2f y=%6.2f  span %.1fx%.1f" % (a,z,cx,cy,x1-x0,y1-y0))
print("cylinders r<=1.6 at |x|~35.5 or 24.5, with z ranges:")
for f in faces:
    if f.geom_type.name != "CYLINDER": continue
    r=f.radius
    if r is None or r>1.6: continue
    fb=f.bounding_box(); cx=(fb.min.X+fb.max.X)/2; cy=(fb.min.Y+fb.max.Y)/2
    if abs(abs(cx)-35.5)<1.5 or abs(abs(cx)-24.5)<1.5:
        print("  r=%.2f x=%6.2f y=%6.2f z=%6.2f..%6.2f" % (r,cx,cy,fb.min.Z,fb.max.Z))
