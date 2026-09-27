#!/usr/bin/env python3
"""Lid bracket for the QRP Labs QMX HF transceiver (appendix 32.60 item 5, session decision under the owner's requirement, veto open): the assembled unit
(95 x 63 x 25 mm enclosure) rides in a printed tray screwed to the Peli 1450 lid's inner face over the east third of the face (over the buttons, clear
of the Xenarc box and of the tablet bracket in the west third), its USB-C lead, 12.0 V lead and BNC-to-SMA jumper in the lid harness. A tray with 2 mm
walls, two strap slots for a 16 mm hook-and-loop strap, four M3 tabs for the lid (bosses or nut plates: the lid's inner face is unribbed in the STEP;
the bond is the assembler's, recorded in ASSEMBLY.md), a 6 mm lip at the open end so the unit cannot slide out with the lid shut, cable notches on
the connector end. Usage: lid_bracket_qmx.py <out dir>   (build123d). Writes lid-bracket-qmx.step and .stl; prints the sizes."""
import sys, os
from build123d import Box, Location, Vector, Plane, BuildSketch, Locations, RectangleRounded, extrude, export_step, export_stl, Cylinder

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
UNIT = (95.0, 63.0, 25.0)                 # the QMX enclosure (manual 1.04: 95 x 63 x 25, 220 g)
CLEAR, WALL, FLOOR = 1.0, 2.0, 2.0
IW, IL, IH = UNIT[0] + 2 * CLEAR, UNIT[1] + 2 * CLEAR, UNIT[2] + 1.0
OW, OL, OH = IW + 2 * WALL, IL + 2 * WALL, IH + FLOOR
LIP_H = 6.0                                # the retaining lip on the open (lid-hinge) end
TAB = (12.0, 8.0, 3.0)                     # M3 tabs at the four corners
def rrect(cx, cy, w, h, r, z0, depth):
    with BuildSketch(Plane.XY.offset(z0)) as sk:
        with Locations((cx, cy)): RectangleRounded(w, h, r)
    return extrude(sk.sketch, amount=depth)
def cyl(cx, cy, d, z0, depth): return Cylinder(d / 2, depth).moved(Location(Vector(cx, cy, z0 + depth / 2)))
tray = rrect(0, 0, OW, OL, 4.0, 0, OH)
tray -= rrect(0, 0, IW, IL, 3.0, FLOOR, IH + 1)                                  # the pocket
tray -= Box(IW - 2 * 8.0, OL + 2, OH).moved(Location(Vector(0, 0, FLOOR + LIP_H + OH / 2)))   # open front and back above the lip: the unit drops in from the side, the lip keeps it
for sx in (-1, 1):                                                               # two strap slots through the floor, 18 x 3 mm, 30 mm apart
    tray -= Box(3.0, 18.0, FLOOR + 2).moved(Location(Vector(sx * 15.0, 0, FLOOR / 2)))
for sx in (-1, 1):                                                               # cable notches on the connector end (USB-C, 12 V, BNC jumper) in the end wall
    tray -= Box(WALL + 2, 12.0, 10.0).moved(Location(Vector(-OW / 2, sx * 18.0, OH - 4.0)))
tabs = None
for sx in (-1, 1):
    for sy in (-1, 1):
        t = Box(TAB[0], TAB[1], TAB[2]).moved(Location(Vector(sx * (OW / 2 + TAB[0] / 2 - 1.0), sy * (OL / 2 - TAB[1] / 2), TAB[2] / 2)))
        t -= cyl(sx * (OW / 2 + TAB[0] / 2 + 1.5), sy * (OL / 2 - TAB[1] / 2), 3.4, -1, TAB[2] + 2)
        tabs = t if tabs is None else tabs + t
part = tray + tabs
bb = part.bounding_box()
export_step(part, os.path.join(OUT, "lid-bracket-qmx.step")); export_stl(part, os.path.join(OUT, "lid-bracket-qmx.stl"))
print("lid-bracket-qmx %.1f x %.1f x %.1f mm (tray %.0f x %.0f x %.0f inside), volume %.0f mm3 (%.0f g in PETG)" % (bb.size.X, bb.size.Y, bb.size.Z, IW, IL, IH, part.volume, part.volume * 1.27e-3))
print("LID-BRACKET-DONE")
