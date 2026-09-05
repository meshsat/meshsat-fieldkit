#!/usr/bin/env python3
"""Battery module enclosure, lid and floor cradle for the MeshSat field kit (MESHSAT-791; appendix 32.27, 32.30, and 32.40 item 8 for the Peli 1450).

Cells: twelve Samsung INR18650-35E welded 1S12P, since 5 Sep 2026 as ONE ROW of twelve UPRIGHT cells (18.65 dia x 65.2 mm each, 223.8 mm of row) so the
module stands along the west end wall of the Peli 1450, whose strips beside the stack (44 mm) and end margins (38 mm) cannot take the flat 4 x 3 block.
Enclosure: printed, two parts, 2.5 mm walls, outer 229 x 24 x 78, cavity 224 x 19 x 73: the cells stand on the floor, the nickel strips and the protection
board (either candidate of 32.27, 66 x 14 x 6) lie on top of the cells under the lid, the heater mat (RS PRO 245-556, 50 x 150 x 1.4, 32.32) sits on the
inside of the long wall, a grommeted lead exit and six vent slots in the south end wall, eight M3 heat-set inserts for the lid. Cradle: printed tray
233 x 28 x 5 with 1 mm rails, two 25 mm strap channels, four 20 x 20 recesses for VHB 5952 pads; it sits on the floor along the west end wall at case
X -174 to -150, Y -114.5 to +114.5 (32.42). Top of the module at 78 mm: the end-wall SMA bulkheads sit at Z 88 (32.40 item 8).
Usage: battery_module.py <out dir>   (build123d, ~/.venv-cad on the VM). Writes STEP and STL per part and prints the sizes.
Module frame: X across the width (24), Y along the row (south end at Y 0, the lead end), Z up from the cradle's underside."""
import sys, os
from build123d import Box, Cylinder, Location, Vector, Axis, export_step, export_stl

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
CELL_D, CELL_H, N = 18.65, 65.2, 12
T = 2.5                               # wall and floor
LID = 2.5
TOP = 8.0                             # nickel strips and the protection board over the cells
W, L, H = CELL_D + 2 * T + 0.35, N * CELL_D + 2 * T + 0.4, T + CELL_H + TOP + LID   # 24 x 229 x 78 (rounded in the record)
CW, CL, CH = W - 2 * T, L - 2 * T, H - T - LID                                    # cavity 19 x 224 x 73
BOARD = (66.0, 14.0, 6.0)             # protection board, lying along the row on top of the cells at the south end
CRW, CRL, CRH, RAIL = W + 4.0, L + 4.0, 5.0, 1.0

def box(w, l, h, x=0.0, y=0.0, z=0.0):
    """Box with its minimum corner at (x, y, z)."""
    return Box(w, l, h).moved(Location(Vector(x + w / 2, y + l / 2, z + h / 2)))

# --- enclosure base: outer shell minus the cavity (open at the top, the lid closes it)
base = box(W, L, H - LID)
base -= box(CW, CL, CH + 1.0, T, T, T)                      # cavity, cut through the open top
# cell witness: twelve 0.3 mm deep circles on the floor so the welded row is placed the same way every time
for k in range(N):
    base -= Cylinder(CELL_D / 2 + 0.2, 0.3).moved(Location(Vector(W / 2, T + 0.2 + CELL_D / 2 + k * CELL_D, T + 0.15)))
# heater mat witness on the inside of the west long wall (50 x 150 x 1.4 self-adhesive, 32.32): 0.3 mm deep, centred along the row, 8 mm above the floor
base -= box(0.3, 150.4, 50.4, T - 0.3, L / 2 - 75.2, T + 8.0)
# board shelf: two 1.5 mm ledges at the south end, 2 mm below the lid, hold the protection board above the cells' strips
base += box(1.5, BOARD[0] + 2.0, 1.5, T, T, H - LID - BOARD[2] - 2.0); base += box(1.5, BOARD[0] + 2.0, 1.5, W - T - 1.5, T, H - LID - BOARD[2] - 2.0)
# lid bosses with insert holes: eight, four per long wall, 4 x 4 mm, full cavity height (the cavity is 19 wide, so the bosses sit in the wall thickness plus 1.5)
for (bx, by) in [(T - 1.0, T), (W - T - 3.0, T), (T - 1.0, L - T - 4.0), (W - T - 3.0, L - T - 4.0), (T - 1.0, L / 3 - 2.0), (W - T - 3.0, L / 3 - 2.0), (T - 1.0, 2 * L / 3 - 2.0), (W - T - 3.0, 2 * L / 3 - 2.0)]:
    base += box(4.0, 4.0, CH, bx, by, T)
    base -= Cylinder(2.0, 6.0).moved(Location(Vector(bx + 2, by + 2, H - LID - 3.0)))   # 4.0 mm hole, 6 deep, for an M3 heat-set insert
# lead exit: 8 mm hole through the south end wall, 60 mm up (beside the board), centred
base -= Cylinder(4.0, T + 2.0).rotate(Axis.X, 90).moved(Location(Vector(W / 2, T / 2, H - LID - 12.0)))
# vent slots: six 1.2 x 8 slots through the south end wall, 6 mm up, 2.5 mm apart
for k in range(6):
    base -= box(1.2, T + 2.0, 8.0, W / 2 - 7.5 + 2.5 * k, -1.0, 6.0)
# --- lid: plate with eight countersunk M3 holes matching the bosses and a 1 mm locating lip inside the cavity
lid = box(W, L, LID, 0, 0, H - LID)
lid += box(CW - 0.4, CL - 0.4, 1.0, T + 0.2, T + 0.2, H - LID - 1.0)
for (bx, by) in [(T - 1.0, T), (W - T - 3.0, T), (T - 1.0, L - T - 4.0), (W - T - 3.0, L - T - 4.0), (T - 1.0, L / 3 - 2.0), (W - T - 3.0, L / 3 - 2.0), (T - 1.0, 2 * L / 3 - 2.0), (W - T - 3.0, 2 * L / 3 - 2.0)]:
    lid -= Cylinder(1.7, LID + 3.0).moved(Location(Vector(bx + 2, by + 2, H - LID)))
    lid -= box(4.0, 4.0, 1.0, bx, by, H - LID - 1.0)          # clear the lip over each boss
# --- cradle: tray under the enclosure, rails at the sides, two strap channels, four pad recesses
cradle = box(CRW, CRL, CRH, -(CRW - W) / 2, -(CRL - L) / 2, -CRH)
cradle += box(RAIL, CRL, 8.0, -(CRW - W) / 2, -(CRL - L) / 2, 0)
cradle += box(RAIL, CRL, 8.0, W + (CRW - W) / 2 - RAIL, -(CRL - L) / 2, 0)
for cy in (L / 2 - 70.0, L / 2 + 70.0):
    cradle -= box(CRW + 2.0, 26.0, 3.0, -(CRW - W) / 2 - 1.0, cy - 13.0, -CRH)            # strap channel under the tray
for py in (8.0, L / 2 - 10.0, L - 28.0):
    cradle -= box(20.0, 20.0, 1.0, W / 2 - 10.0, py, -CRH)                                # VHB pad recess (three along the row)
for name, part in (("battery-module-base", base), ("battery-module-lid", lid), ("battery-module-cradle", cradle)):
    bb = part.bounding_box(); export_step(part, os.path.join(OUT, name + ".step")); export_stl(part, os.path.join(OUT, name + ".stl"))
    print("%-24s %6.1f x %6.1f x %5.1f mm, volume %.0f mm3" % (name, bb.size.X, bb.size.Y, bb.size.Z, part.volume))
print("MODULE-CAD-DONE")
