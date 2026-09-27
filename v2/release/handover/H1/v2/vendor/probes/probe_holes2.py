import sys, time
from build123d import import_step
t0 = time.time(); path = sys.argv[1]; zsel = float(sys.argv[2]) if len(sys.argv) > 2 else None
shape = import_step(path)
faces = shape.faces()
horiz = []
for f in faces:
    if f.geom_type.name != "PLANE": continue
    try: n = f.normal_at()
    except Exception: continue
    if abs(abs(n.Z) - 1.0) < 1e-3: horiz.append(f)
horiz.sort(key=lambda f: -f.area)
cands = [f for f in horiz if zsel is None or abs(f.center().Z - zsel) < 0.05]
for f in cands[:2]:
    fb = f.bounding_box()
    print("FACE area %.0f z %.2f X %.2f..%.2f Y %.2f..%.2f" % (f.area, f.center().Z, fb.min.X, fb.max.X, fb.min.Y, fb.max.Y))
    ow = f.outer_wire(); print("  outer wire edges:", len(ow.edges()))
    for w in f.inner_wires():
        es = w.edges(); circ = [e for e in es if e.geom_type.name == "CIRCLE"]
        wb = w.bounding_box()
        if circ and len(es) <= 2:
            e = circ[0]; c = e.arc_center
            print("  HOLE circle r %.2f at (%.2f, %.2f)" % (e.radius, c.X, c.Y))
        else:
            print("  cutout %d edges bbox X %.2f..%.2f Y %.2f..%.2f (%.1f x %.1f)" % (len(es), wb.min.X, wb.max.X, wb.min.Y, wb.max.Y, wb.size.X, wb.size.Y))
# solids overview: bbox of each solid larger than 3 mm (connectors, fan, shell)
try:
    sol = shape.solids()
    print("solids:", len(sol))
    big = []
    for s in sol:
        b = s.bounding_box()
        if max(b.size.X, b.size.Y, b.size.Z) >= 4.0: big.append((b.size.X * b.size.Y * b.size.Z, b))
    big.sort(key=lambda t: -t[0])
    for v, b in big[:25]:
        print("  solid X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f (%.1f x %.1f x %.1f)" % (b.min.X, b.max.X, b.min.Y, b.max.Y, b.min.Z, b.max.Z, b.size.X, b.size.Y, b.size.Z))
except Exception as e:
    print("solids err", e)
print("done %.0fs" % (time.time() - t0))
