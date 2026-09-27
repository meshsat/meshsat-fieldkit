import sys
from build123d import import_step, Vector
shape = import_step(sys.argv[1]); bb = shape.bounding_box()
def row(y, z, xs): return ''.join('#' if shape.is_inside(Vector(x, y, z)) else '.' for x in xs)
NX = 96
xs = [bb.min.X + (bb.max.X - bb.min.X) * (i + 0.5) / NX for i in range(NX)]
print('PLAN sections (X across, Z down), full X range %.1f..%.1f, Z range %.1f..%.1f' % (bb.min.X, bb.max.X, bb.min.Z, bb.max.Z))
for y in (-0.5, -4.0, -8.5, -13.0, -20.0, -30.0, -60.0, -99.0, -103.0, -107.0):
    print('-- Y = %.1f' % y)
    for j in range(0, 24):
        z = bb.min.Z + (bb.max.Z - bb.min.Z) * (j + 0.5) / 24
        print('  ' + row(y, z, xs))
print('SIDE profile at Z = 0 and Z = 60 (X across, Y down from 0 to %.1f)' % bb.min.Y)
for zc in (0.0, 60.0, 110.0):
    print('-- Z = %.1f' % zc)
    for k in range(0, 28):
        y = bb.max.Y - (bb.max.Y - bb.min.Y) * (k + 0.5) / 28
        print('  %7.2f ' % y + row(y, zc, xs))
print('END profile at X = 0 and X = 140 (Z across, Y down)')
zs = [bb.min.Z + (bb.max.Z - bb.min.Z) * (i + 0.5) / NX for i in range(NX)]
for xc in (0.0, 140.0, 156.0):
    print('-- X = %.1f' % xc)
    for k in range(0, 28):
        y = bb.max.Y - (bb.max.Y - bb.min.Y) * (k + 0.5) / 28
        print('  %7.2f ' % y + ''.join('#' if shape.is_inside(Vector(xc, y, z)) else '.' for z in zs))
