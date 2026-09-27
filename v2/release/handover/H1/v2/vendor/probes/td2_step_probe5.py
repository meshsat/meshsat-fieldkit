import sys
from build123d import import_step
shape = import_step(sys.argv[1]); faces = shape.faces()
GL = 4.30   # glass underside is at 4.32: everything with max Z below this is the body
xs=[];ys=[]
for f in faces:
    fb = f.bounding_box()
    if fb.max.Z <= GL: xs += [fb.min.X, fb.max.X]; ys += [fb.min.Y, fb.max.Y]
print('BODY envelope below the glass (Z<=%.2f): X %.3f..%.3f (%.2f)  Y %.3f..%.3f (%.2f)' % (GL, min(xs), max(xs), max(xs)-min(xs), min(ys), max(ys), max(ys)-min(ys)))
for z0, z1 in ((3.0, 4.30), (1.0, 3.0), (-1.5, 1.0), (-4.5, -1.5), (-10, -4.5)):
    xs=[];ys=[]
    for f in faces:
        fb = f.bounding_box()
        if fb.max.Z <= z1 and fb.min.Z >= z0 - 0.01: xs += [fb.min.X, fb.max.X]; ys += [fb.min.Y, fb.max.Y]
    if xs: print('  slice Z %5.2f..%5.2f: X %7.3f..%7.3f  Y %7.3f..%7.3f' % (z0, z1, min(xs), max(xs), min(ys), max(ys)))
print('faces that set the body extremes (|X|>48.5 or Y<-83.5 or Y>81.5), below the glass:')
n=0
for f in faces:
    fb = f.bounding_box()
    if fb.max.Z > GL: continue
    if fb.max.X > 48.5 or fb.min.X < -48.5 or fb.min.Y < -83.5 or fb.max.Y > 81.5:
        n+=1
        if n<=14: print('  %-9s X %7.2f..%7.2f Y %7.2f..%7.2f Z %6.2f..%6.2f area %.1f' % (f.geom_type.name, fb.min.X, fb.max.X, fb.min.Y, fb.max.Y, fb.min.Z, fb.max.Z, f.area))
print('  count', n)
print('corner cylinders of the body (r 0.5..8) near the four body corners:')
for f in faces:
    if f.geom_type.name != 'CYLINDER': continue
    r = f.radius
    if r is None or r < 0.5 or r > 8: continue
    fb = f.bounding_box()
    if fb.max.Z > GL: continue
    cx=(fb.min.X+fb.max.X)/2; cy=(fb.min.Y+fb.max.Y)/2
    if abs(cx) > 44 and (cy < -78 or cy > 76): print('  r=%.2f at (%.2f, %.2f) Z %.2f..%.2f' % (r, cx, cy, fb.min.Z, fb.max.Z))
print('glass corner cylinders (r 5..10, Z>4.3):')
for f in faces:
    if f.geom_type.name != 'CYLINDER': continue
    r = f.radius
    if r is None or r < 5 or r > 10: continue
    fb = f.bounding_box()
    if fb.min.Z < 4.3: continue
    print('  r=%.2f at (%.2f, %.2f) Z %.2f..%.2f' % (r, (fb.min.X+fb.max.X)/2, (fb.min.Y+fb.max.Y)/2, fb.min.Z, fb.max.Z))
