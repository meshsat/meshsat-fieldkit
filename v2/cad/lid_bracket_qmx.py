#!/usr/bin/env python3
"""Lid bracket for the QRP Labs QMX HF transceiver (appendix 32.60 item 5, session decision under the owner's requirement, veto open): the assembled unit
(95 x 63 x 25 mm enclosure) rides in a printed tray screwed to the Peli 1450 lid's inner face over the east third of the face (over the buttons, clear
of the Xenarc box and of the tablet bracket in the west third), its USB-C lead, 12.0 V lead and BNC-to-SMA jumper in the lid harness. A tray with 2 mm
walls, two strap slots for a 16 mm hook-and-loop strap, four M3 tabs for the lid (bosses or nut plates: the lid's inner face is unribbed in the STEP;
the bond is the assembler's, recorded in ASSEMBLY.md), a 6 mm lip at the open end so the unit cannot slide out with the lid shut, cable notches on
the connector end. Usage: lid_bracket_qmx.py <out dir>   (build123d). Writes lid-bracket-qmx.step and .stl; prints the sizes.
PLACE (C5 of v2/docs/CASE-MARGINS.md, 27 Sep 2026, the session's choice SC-07): the tray sits at case X 102.0 to 171.0 (panel1450.QMX_TRAY_X),
1.5 mm west of its 9 Sep place, so its east edge keeps 2.08 inside the lid's flat ceiling (1.70 at the worst, M19 MET); it still covers the
buttons at X 150. The part itself is unchanged; M3 (the space under it for the face parts) stays OPEN on the button and lever heights (T9).
The part's numbers are module constants so the case release's placement sheet (v2/cad/case_drawings.py, sheet 14) reads them instead of
retyping them; importing this module builds nothing (27 Sep 2026, MESHSAT-1357, the layer 7 fixer c7). PLACE_Y is the tray's place across the
case, unchanged since 9 September 2026 (ASSEMBLY.md's QMX tray row, "Y -51.5 to 71.5 in the plate frame"; v2/cad/render/scene.py QY 10.0); the
tray's local Y (its 69.0 width) runs along the case's X and its local X (123.0 over the tabs) along the case's Y, as scene.py places it."""
import sys, os

UNIT = (95.0, 63.0, 25.0)                 # the QMX enclosure (manual 1.04: 95 x 63 x 25, 220 g)
CLEAR, WALL, FLOOR = 1.0, 2.0, 2.0
IW, IL, IH = UNIT[0] + 2 * CLEAR, UNIT[1] + 2 * CLEAR, UNIT[2] + 1.0
OW, OL, OH = IW + 2 * WALL, IL + 2 * WALL, IH + FLOOR
LIP_H = 6.0                                # the retaining lip on the open (lid-hinge) end
TAB = (12.0, 8.0, 3.0)                     # M3 tabs at the four corners
TAB_HOLE = 3.4                             # the tabs' M3 clearance hole
SLOT = (3.0, 18.0, 15.0)                   # two strap slots through the floor: x width, y length, centres at +-15.0 in x
NOTCH = (12.0, 10.0, 18.0)                 # two cable notches in the -x end wall: y width, depth from the top, centres at +-18.0 in y
OPEN_W = IW - 2 * 8.0                      # the side walls are open above the lip over this length in x, centred
POCKET_R, OUTER_R = 3.0, 4.0
# the four tabs and their holes in the part's own frame (x along the 101.0 length, y across the 69.0 width, z 0 on the tab face)
TAB_CENTRES = [(sx * (OW / 2 + TAB[0] / 2 - 1.0), sy * (OL / 2 - TAB[1] / 2)) for sx in (-1, 1) for sy in (-1, 1)]
HOLE_CENTRES = [(sx * (OW / 2 + TAB[0] / 2 + 1.5), sy * (OL / 2 - TAB[1] / 2)) for sx in (-1, 1) for sy in (-1, 1)]
LENGTH_OVER_TABS = OW + 2 * (TAB[0] - 1.0)  # 123.0: the part's length over its tabs
PLACE_Y = (-51.5, 71.5)                     # case Y of the part's length over its tabs (ASSEMBLY.md's QMX row since 9 Sep 2026; scene.py QY 10.0)
assert abs((PLACE_Y[1] - PLACE_Y[0]) - LENGTH_OVER_TABS) < 1e-9, "PLACE_Y must span the part's length over its tabs"


def build():
    from build123d import Box, Location, Vector, Plane, BuildSketch, Locations, RectangleRounded, extrude, Cylinder

    def rrect(cx, cy, w, h, r, z0, depth):
        with BuildSketch(Plane.XY.offset(z0)) as sk:
            with Locations((cx, cy)): RectangleRounded(w, h, r)
        return extrude(sk.sketch, amount=depth)

    def cyl(cx, cy, d, z0, depth): return Cylinder(d / 2, depth).moved(Location(Vector(cx, cy, z0 + depth / 2)))
    tray = rrect(0, 0, OW, OL, OUTER_R, 0, OH)
    tray -= rrect(0, 0, IW, IL, POCKET_R, FLOOR, IH + 1)                             # the pocket
    tray -= Box(OPEN_W, OL + 2, OH).moved(Location(Vector(0, 0, FLOOR + LIP_H + OH / 2)))   # open front and back above the lip: the unit drops in from the side, the lip keeps it
    for sx in (-1, 1):                                                               # two strap slots through the floor, 18 x 3 mm, 30 mm apart
        tray -= Box(SLOT[0], SLOT[1], FLOOR + 2).moved(Location(Vector(sx * SLOT[2], 0, FLOOR / 2)))
    for sx in (-1, 1):                                                               # cable notches on the connector end (USB-C, 12 V, BNC jumper) in the end wall
        tray -= Box(WALL + 2, NOTCH[0], NOTCH[1]).moved(Location(Vector(-OW / 2, sx * NOTCH[2], OH - 4.0)))
    tabs = None
    for (tx, ty), (hx, hy) in zip(TAB_CENTRES, HOLE_CENTRES):
        t = Box(TAB[0], TAB[1], TAB[2]).moved(Location(Vector(tx, ty, TAB[2] / 2)))
        t -= cyl(hx, hy, TAB_HOLE, -1, TAB[2] + 2)
        tabs = t if tabs is None else tabs + t
    return tray + tabs


if __name__ == "__main__":
    from build123d import export_step, export_stl
    OUT = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(OUT, exist_ok=True)
    part = build()
    bb = part.bounding_box()
    export_step(part, os.path.join(OUT, "lid-bracket-qmx.step")); export_stl(part, os.path.join(OUT, "lid-bracket-qmx.stl"))
    print("lid-bracket-qmx %.1f x %.1f x %.1f mm (tray %.0f x %.0f x %.0f inside), volume %.0f mm3 (%.0f g in PETG)" % (bb.size.X, bb.size.Y, bb.size.Z, IW, IL, IH, part.volume, part.volume * 1.27e-3))
    print("LID-BRACKET-DONE")
