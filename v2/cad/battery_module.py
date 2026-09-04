#!/usr/bin/env python3
"""Battery module enclosure, lid and floor cradle for the MeshSat field kit (MESHSAT-791, appendix 32.27 and 32.30).

Cells: twelve Samsung INR18650-35E welded 1S12P as a flat 4 x 3 block, 75.2 x 197.7 x 19.7 mm wrapped (32.27 section 3).
Enclosure: printed, two parts, 2.5 mm walls, outer 81 x 221 x 27.5, cavity 76 x 216 x 22.5 with the heater mat (RS PRO 245-556, 50 x 150,
7.5 W, 1.4 mm, self-adhesive, 32.32) on the floor under the cells, the cells against the north end and
a 66 x 14 x 6 pocket at the south end for the protection board (either candidate of 32.27), a grommeted lead exit and six vent
slots in the south wall, eight M3 heat-set inserts for the lid. Cradle: printed tray 83 x 224 x 5 with 1 mm rails, two 25 mm strap
channels, four 20 x 20 recesses for VHB 5952 pads; it sits in the east floor band at case X 120 to 203, Y -139 to 85 (32.30).
Usage: battery_module.py <out dir>   (build123d, ~/.venv-cad on the laptop). Writes STEP and STL per part and prints the sizes.
Module frame: X across the width, Y along the length (south end at Y 0, the lead end), Z up from the cradle's underside."""
import sys, os
from build123d import Box, Cylinder, Location, Vector, Axis, export_step, export_stl, Plane

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
W, L, H = 81.0, 221.0, 27.5          # enclosure outer (32.30, grown 1 mm in length and 1.5 mm in height for the heater mat, 32.32)
T = 2.5                               # wall and floor
LID = 2.5
CW, CL, CH = W - 2 * T, L - 2 * T, H - T - LID     # cavity 76 x 216 x 22.5: cells 19.7 over the 1.4 mm heater mat, 1.4 mm spare
POCKET = (66.0, 14.0, 6.0)            # protection board pocket at the south end, inside the cavity
CRW, CRL, CRH, RAIL = 83.0, 224.0, 5.0, 1.0

def box(w, l, h, x=0.0, y=0.0, z=0.0):
    """Box with its minimum corner at (x, y, z)."""
    return Box(w, l, h).moved(Location(Vector(x + w / 2, y + l / 2, z + h / 2)))

# --- enclosure base: outer shell minus the cavity (open at the top, the lid closes it)
base = box(W, L, H - LID)
base -= box(CW, CL, CH + 1.0, T, T, T)                      # cavity, cut through the open top
# pocket rib: a 2 mm rib across the cavity 16 mm from the south wall keeps the cells off the protection board; a 6 mm gap in it passes the heater mat leads
base += box(CW / 2 - 3.0, 2.0, 8.0, T, T + POCKET[1] + 2.0, T); base += box(CW / 2 - 3.0, 2.0, 8.0, W / 2 + 3.0, T + POCKET[1] + 2.0, T)
# heater mat outline on the floor (RS PRO 245-556, 50 x 150 x 1.4, self-adhesive): a 0.3 mm deep witness so it is placed the same way every time, centred under the cells
base -= box(50.4, 150.4, 0.3, W / 2 - 25.2, T + POCKET[1] + 4.0 + (CL - POCKET[1] - 4.0 - 150.4) / 2, T)
# lid bosses with insert holes: eight, at the corners and the mid-sides, 6 mm square, full cavity height
for (bx, by) in [(T, T), (W - T - 6, T), (T, L - T - 6), (W - T - 6, L - T - 6), (T, L / 2 - 3), (W - T - 6, L / 2 - 3), (W / 2 - 3, T), (W / 2 - 3, L - T - 6)]:
    base += box(6.0, 6.0, CH, bx, by, T)
    base -= Cylinder(2.0, 6.0).moved(Location(Vector(bx + 3, by + 3, H - LID - 3.0)))   # 4.0 mm hole, 6 deep, for an M3 heat-set insert
# lead exit: 8 mm hole through the south wall, 12 mm up, 20 mm from the west face
base -= Cylinder(4.0, T + 2.0).rotate(Axis.X, 90).moved(Location(Vector(20.0, T / 2, 12.0)))
# vent slots: six 1.2 x 8 slots through the south wall, 6 mm up, 8 mm apart from the middle
for k in range(6):
    base -= box(1.2, T + 2.0, 8.0, W / 2 - 20 + 8 * k - 0.6, -1.0, 6.0)
# --- lid: plate with eight countersunk M3 holes matching the bosses and a 1 mm locating lip inside the cavity
lid = box(W, L, LID, 0, 0, H - LID)
lid += box(CW - 0.4, CL - 0.4, 1.0, T + 0.2, T + 0.2, H - LID - 1.0)
for (bx, by) in [(T, T), (W - T - 6, T), (T, L - T - 6), (W - T - 6, L - T - 6), (T, L / 2 - 3), (W - T - 6, L / 2 - 3), (W / 2 - 3, T), (W / 2 - 3, L - T - 6)]:
    lid -= Cylinder(1.7, LID + 3.0).moved(Location(Vector(bx + 3, by + 3, H - LID)))
    lid -= box(6.0, 6.0, 1.0, bx, by, H - LID - 1.0)          # clear the lip over each boss
# --- cradle: tray under the enclosure, rails at the sides, two strap channels, four pad recesses
cradle = box(CRW, CRL, CRH, -(CRW - W) / 2, -(CRL - L) / 2, -CRH)
cradle += box(RAIL, CRL, 6.0, -(CRW - W) / 2, -(CRL - L) / 2, 0)
cradle += box(RAIL, CRL, 6.0, W + (CRW - W) / 2 - RAIL, -(CRL - L) / 2, 0)
for cy in (L / 2 - 60.0, L / 2 + 60.0):
    cradle -= box(CRW + 2.0, 26.0, 3.0, -(CRW - W) / 2 - 1.0, cy - 13.0, -CRH)            # strap channel under the tray
for (px, py) in [(6.0, 8.0), (W - 26.0, 8.0), (6.0, L - 28.0), (W - 26.0, L - 28.0)]:
    cradle -= box(20.0, 20.0, 1.0, px, py, -CRH)                                        # VHB pad recess
for name, part in (("battery-module-base", base), ("battery-module-lid", lid), ("battery-module-cradle", cradle)):
    bb = part.bounding_box(); export_step(part, os.path.join(OUT, name + ".step")); export_stl(part, os.path.join(OUT, name + ".stl"))
    print("%-24s %6.1f x %6.1f x %5.1f mm, volume %.0f mm3" % (name, bb.size.X, bb.size.Y, bb.size.Z, part.volume))
print("MODULE-CAD-DONE")
