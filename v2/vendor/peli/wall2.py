"""Wall section of the 1520 base by boolean intersection with a thin slab (fast; the point probe wall.py is the slow cross-check).
Prints, for each station, the vertices of the section sorted by height, so the inner and outer wall surfaces can be read off.
Usage: wall2.py <base STEP>  (build123d). STEP frame: Y down from the rim (0) to the floor (-124.87), Z across the case."""
import sys
from build123d import import_step, Box, Location, Vector
shape = import_step(sys.argv[1])
def station(name, box):
    sect = shape.intersect(box)
    vs = sorted({(round(v.X, 2), round(v.Y, 2), round(v.Z, 2)) for v in sect.vertices()}, key=lambda t: (-t[1], t[2], t[0]))
    print("== %s: %d vertices, volume %.0f mm3" % (name, len(vs), sect.volume))
    for v in vs: print("   X %8.2f  Y %8.2f  Z %8.2f" % v)
for x in (-100.0, -80.0, -120.0):
    station("long wall (-Z side) at X %.0f" % x, Box(0.02, 135.0, 80.0).moved(Location(Vector(x, -65.0, -165.0))))
station("long wall (+Z side) at X -100", Box(0.02, 135.0, 80.0).moved(Location(Vector(-100.0, -65.0, 165.0))))
station("end wall (-X) at Z -60", Box(80.0, 135.0, 0.02).moved(Location(Vector(-225.0, -65.0, -60.0))))
print("WALL2-DONE")
