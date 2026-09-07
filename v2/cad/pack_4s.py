#!/usr/bin/env python3
"""The built 4S pack's enclosure (appendix 32.62, 7 Sep 2026): a printed box for the east pocket of the Peli 1450 beside A22 (the pocket is about 58 x 240 x 48 mm
under B16's overhang). Outer 56 x 236 x 46, 2 mm walls and floor, a fold-over lid on four M3 (PEM nuts bonded in the corners), the cell block pocket
(3 x 2 x 3 18650 cells = 4S4P with two spare sites, 56 x 195 x 37 wrapped, or 2 x 2 x 3 21700 cells) at the west end, the BMS board bay (the P1 board
70 x 44 x 1.6 standing on four M3 bosses, parts up) at the east end, a cable notch for the XT60 and SMBus leads, two strap slots in the floor for the pack's
own hook-and-loop, four VHB pads under the floor. Usage: pack_4s.py <out dir>   (build123d). Writes pack-4s-box.step/.stl and pack-4s-lid.step/.stl; prints the sizes."""
import sys, os
from build123d import Box, Location, Vector, Plane, BuildSketch, Locations, RectangleRounded, extrude, export_step, export_stl, Cylinder
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
OW, OL, OH = 56.0, 236.0, 46.0                  # outer (X across the pocket, Y along the wall, Z up)
WALL, FLOOR, LID_T = 2.0, 2.0, 2.0
IW, IL, IH = OW - 2 * WALL, OL - 2 * WALL, OH - FLOOR - LID_T   # 52 x 232 x 42 inside
CELLS = (52.0, 195.0, 37.0)                     # the wrapped 4S4P 18650 block
BOARD = (44.0, 70.0, 1.6)                       # the P1 board lies across the pocket at the east end (its 70 mm along Y)
BOSS_D, BOSS_H, BOSS_HOLE = 6.0, 5.0, 2.5       # M3 bosses (tapped or heat-set inserts) under the board's holes at (+-19, +-32) in board terms
def rrect(cx, cy, w, h, r, z0, depth):
    with BuildSketch(Plane.XY.offset(z0)) as sk:
        with Locations((cx, cy)): RectangleRounded(w, h, r)
    return extrude(sk.sketch, amount=depth)
def cyl(cx, cy, d, z0, depth): return Cylinder(d / 2, depth).moved(Location(Vector(cx, cy, z0 + depth / 2)))
box = rrect(0, 0, OW, OL, 4.0, 0, OH - LID_T)
box -= rrect(0, 0, IW, IL, 3.0, FLOOR, IH + 1)                                          # the pocket
BY = -OL / 2 + WALL + CELLS[1] / 2                                                       # the cell block sits at the west end (negative Y)
board_y = OL / 2 - WALL - 3.0 - BOARD[1] / 2                                             # the board bay at the east end
for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = sx * 19.0, board_y + sy * 32.0
        box += cyl(x, y, BOSS_D, FLOOR, BOSS_H); box -= cyl(x, y, BOSS_HOLE, FLOOR, BOSS_H + 1)
box -= Box(14.0, WALL + 2, 12.0).moved(Location(Vector(0, OL / 2, OH - LID_T - 6.0)))    # the cable notch in the east end wall (XT60 lead and the SMBus lead)
for sy in (-60.0, 60.0):                                                                 # strap slots through the floor for a 16 mm strap around the cell block
    box -= Box(IW + 2, 18.0, FLOOR + 2).moved(Location(Vector(0, BY + sy, FLOOR / 2)))
lid = rrect(0, 0, OW, OL, 4.0, 0, LID_T)
lid += rrect(0, 0, IW - 0.6, IL - 0.6, 2.5, -1.5, 1.5)                                  # a locating lip inside the walls
for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = sx * (OW / 2 - 4.0), sy * (OL / 2 - 4.0)
        box += cyl(x, y, 7.0, FLOOR, OH - LID_T - FLOOR); box -= cyl(x, y, 2.5, FLOOR, OH); lid -= cyl(x, y, 3.4, -2, LID_T + 4)   # M3 corner posts and the lid holes
bb = box.bounding_box()
export_step(box, os.path.join(OUT, "pack-4s-box.step")); export_stl(box, os.path.join(OUT, "pack-4s-box.stl"))
export_step(lid, os.path.join(OUT, "pack-4s-lid.step")); export_stl(lid, os.path.join(OUT, "pack-4s-lid.stl"))
print("pack-4s box %.1f x %.1f x %.1f mm (inside %.0f x %.0f x %.0f), cell block %s at Y %.1f, board bay at Y %.1f, volume %.0f mm3 (%.0f g in PETG); lid %.0f x %.0f x %.0f" % (
    bb.size.X, bb.size.Y, bb.size.Z, IW, IL, IH, CELLS, BY, board_y, box.volume, box.volume * 1.27e-3, OW, OL, LID_T))
print("PACK-4S-DONE")
