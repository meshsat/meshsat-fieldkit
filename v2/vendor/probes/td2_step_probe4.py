import sys
from build123d import import_step
shape = import_step(sys.argv[1]); faces = shape.faces()
print('cylinders r<=3.5 within 6 mm of a tab lug (+-35.35, -67.06/72.94): r, centre, z-range')
for f in faces:
    if f.geom_type.name != 'CYLINDER': continue
    r = f.radius
    if r is None or r > 3.5: continue
    fb = f.bounding_box(); cx = (fb.min.X + fb.max.X) / 2; cy = (fb.min.Y + fb.max.Y) / 2
    for tx in (-35.35, 35.35):
        for ty in (-67.06, 72.94):
            if abs(cx - tx) < 6 and abs(cy - ty) < 6: print('  r=%.3f at (%.2f, %.2f) z %.2f..%.2f' % (r, cx, cy, fb.min.Z, fb.max.Z))
print('cylinders r<=3.5 within 4 mm of a Pi standoff (+-24.5, -17.27/40.73):')
for f in faces:
    if f.geom_type.name != 'CYLINDER': continue
    r = f.radius
    if r is None or r > 3.5: continue
    fb = f.bounding_box(); cx = (fb.min.X + fb.max.X) / 2; cy = (fb.min.Y + fb.max.Y) / 2
    for tx in (-24.5, 24.5):
        for ty in (-17.27, 40.73):
            if abs(cx - tx) < 4 and abs(cy - ty) < 4: print('  r=%.3f at (%.2f, %.2f) z %.2f..%.2f' % (r, cx, cy, fb.min.Z, fb.max.Z))
print('deepest non-standoff, non-lug faces (z < -4.5), any type:')
seen = 0
for f in faces:
    fb = f.bounding_box()
    if fb.min.Z >= -4.5: continue
    cx = (fb.min.X + fb.max.X) / 2; cy = (fb.min.Y + fb.max.Y) / 2
    near_so = any(abs(cx - tx) < 4 and abs(cy - ty) < 4 for tx in (-24.5, 24.5) for ty in (-17.27, 40.73))
    near_lug = any(abs(cx - tx) < 6 and abs(cy - ty) < 6 for tx in (-35.35, 35.35) for ty in (-67.06, 72.94))
    if not near_so and not near_lug:
        seen += 1
        if seen <= 12: print('  %s at (%.2f, %.2f) X %.1f..%.1f Y %.1f..%.1f z %.2f..%.2f' % (f.geom_type.name, cx, cy, fb.min.X, fb.max.X, fb.min.Y, fb.max.Y, fb.min.Z, fb.max.Z))
print('  total such faces:', seen)
