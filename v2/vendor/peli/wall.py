"""Wall profile of the 1520 base for the connector cut-outs: at a few X stations on the -Z long wall (the case-frame -Y wall,
where the dock's shore entry sits), walk Z outward at every height and print where the solid starts and stops.
Usage: wall.py <base STEP>  (build123d, ~/.venv-cad on the laptop). Frame: the STEP's own, Y down from the rim at 0, Z across."""
import sys
from build123d import import_step, Vector
shape = import_step(sys.argv[1])
def spans(x, y, z0, z1, step):
    out, inside, start = [], False, None; z = z0
    while z <= z1:
        i = shape.is_inside(Vector(x, y, z))
        if i and not inside: start = z
        if not i and inside: out.append((start, z - step))
        inside = i; z += step
    if inside: out.append((start, z1))
    return out
for x in (-100.0, -80.0, -120.0):
    print("== X = %.0f, -Z wall: solid spans in Z (mm) per height Y" % x)
    for k in range(0, 49):
        y = -2.5 * k - 2.5
        s = spans(x, y, -195.0, -125.0, 0.1)
        print("  Y %7.1f : " % y + "  ".join("%.1f..%.1f (%.1f)" % (a, b, b - a) for a, b in s))
print("== end wall at X -254..-200, Z = -60, per height")
for k in range(0, 49):
    y = -2.5 * k - 2.5
    out, inside, start = [], False, None; xx = -256.0
    while xx <= -195.0:
        i = shape.is_inside(Vector(xx, y, -60.0))
        if i and not inside: start = xx
        if not i and inside: out.append((start, xx - 0.1))
        inside = i; xx += 0.1
    if inside: out.append((start, xx))
    print("  Y %7.1f : " % y + "  ".join("%.1f..%.1f (%.1f)" % (a, b, b - a) for a, b in out))
print("WALL-PROBE-DONE")
