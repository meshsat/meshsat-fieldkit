#!/usr/bin/env python3
"""1:1 templates for the two MIL-DTL-38999 wall receptacles on the Peli 1520 base (appendix 32.13 ruling 6, 32.29).

The receptacles do not mount on the case wall directly: the 1520's inner wall drafts about 2 degrees and its outer skin is
ribbed, so a flanged connector could not seal on either face. Both sit on one flat aluminium plate (82 x 54 x 3 mm) bolted
over a window in the long wall on the dock's entry side, with a 2 mm closed-cell gasket between plate and wall. The plate
carries the exact Glenair cut-outs; the wall only needs two hole-saw holes and six screw holes.

Shore DC: Glenair D38999/20 shell 13 wall-mount receptacle, round holes (D0), front panel mount on the plate: flange 28.9
square, four holes on a 23.01 square, plate hole 19.05 (Glenair panel cut-out sheet type B, shell 12-13: AA .750; 233-105
table shell 13: C BSC .906, E .136/.120, B sq 1.138/1.114).
USB host: Glenair 233-370 shell 15 wall-mount receptacle D0: flange 31.29 square, four holes on a 24.61 square, plate hole
23.01 (233-370 sheet: 2x .969 (24.61), 4x .132/.124; cut-out sheet type B shell 14-15: AA .906), panel .0625 to .250 in.
Case: cavity 124.87 deep, inner wall from the shoulder to 108 mm down at a 2 degree draft, then a 17 mm chamfer to the
floor; frame-leg bosses on the inner walls at X +-8.6, +-48.7, +-51.4, +-133.3, +-148.8, +-151.5, +-152.4 between 67 and
71 mm above the floor (appendix 25.1, vendor/peli/wall2.py section). Every through-hole here keeps 7 mm or more from them.
Wall: the BACK long wall, the hinge side (case +Y). The front wall carries the handle, the pressure valve, two rib clusters and
both latch straps (Peli customer drawing 1521-931), and its inner ribs leave no centre leg, so nothing flat and free is left there.
Frame: case-centred, X along the long axis, Z up from the cavity floor. Both sheets are drawn as seen from OUTSIDE the back
wall, so case +X is on the viewer's left. 1:1 on A4 landscape; check the 100 mm bar with a rule.  Usage: case_wall_cutouts.py <out.pdf>"""
import sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

PLATE = dict(cx=-92.0, cz=55.0, w=82.0, h=54.0, t=3.0)
SCREWS = [(-120.0, 78.0), (-92.0, 78.0), (-64.0, 78.0), (-120.0, 32.0), (-92.0, 32.0), (-64.0, 32.0)]   # M4, wall and plate
DC = dict(name="DC: D38999/20 sh. 13 D0", x=-110.0, z=55.0, hole=19.05, flange=28.9, pattern=23.01, screw=3.3, wall_hole=29.0)
USB = dict(name="USB: 233-370 sh. 15 D0", x=-74.0, z=55.0, hole=23.01, flange=31.29, pattern=24.61, screw=3.3, wall_hole=29.0)
BOSS_X = [-133.3, -8.6]           # the back wall's inner ribs nearest the plate (frame-leg drill points at X +-8.6, +-133.3, +-152.4)
VIEW = -1.0                        # seen from outside the back wall: case +X to the viewer's left
FLOOR_TO_RIM = 124.87; CHAMFER = 16.7

out = sys.argv[1] if len(sys.argv) > 1 else "wall-cutouts-1to1.pdf"
c = canvas.Canvas(out, pagesize=landscape(A4)); W, H = landscape(A4)
ox = W / 2 - PLATE["cx"] * mm; oz = 64 * mm
def P(x, z): return ox + VIEW * (x - PLATE["cx"]) * mm + PLATE["cx"] * mm, oz + z * mm
def line(x1, z1, x2, z2, w=0.3, dash=None):
    c.setLineWidth(w)
    if dash: c.setDash(*dash)
    c.line(*P(x1, z1), *P(x2, z2)); c.setDash()
def circle(x, z, d, w=0.4):
    c.setLineWidth(w); px, pz = P(x, z); c.circle(px, pz, d / 2 * mm, stroke=1, fill=0)
def rect(x0, z0, x1, z1, w=0.4, dash=None):
    c.setLineWidth(w)
    if dash: c.setDash(*dash)
    (ax, az), (bx, bz) = P(x0, z0), P(x1, z1); c.rect(min(ax, bx), min(az, bz), abs(bx - ax), abs(bz - az), stroke=1, fill=0); c.setDash()
def text(x, z, s, size=8, angle=0, anchor="l"):
    px, pz = P(x, z); c.saveState(); c.translate(px, pz); c.rotate(angle); c.setFont("Helvetica", size)
    {"c": c.drawCentredString, "r": c.drawRightString}.get(anchor, c.drawString)(0, 0, s); c.restoreState()
def cross(x, z, r=4):
    line(x - r, z, x + r, z, 0.2); line(x, z - r, x, z + r, 0.2)
def dim(x1, x2, z, label):
    line(x1, z, x2, z, 0.25); line(x1, z - 1.5, x1, z + 1.5, 0.25); line(x2, z - 1.5, x2, z + 1.5, 0.25); text((x1 + x2) / 2, z + 1.5, label, 7, anchor="c")
def vdim(x, z1, z2, label):
    line(x, z1, x, z2, 0.25); line(x - 1.5, z1, x + 1.5, z1, 0.25); line(x - 1.5, z2, x + 1.5, z2, 0.25); text(x + 1.8, (z1 + z2) / 2, label, 7, angle=90, anchor="c")
def scale_bar(x, z):
    line(x, z, x + 100, z, 1.0); line(x, z - 2, x, z + 2, 0.6); line(x + 100, z - 2, x + 100, z + 2, 0.6); text(x + 50, z - 5, "100 mm at 1:1 (print at 100 percent, no fit to page)", 7, anchor="c")
def notes(lines, z0):
    import textwrap
    k = 0
    for n in lines:
        for part in textwrap.wrap(n, 150): text(PLATE["cx"] - 70, z0 - 3.6 * k, part, 6.2); k += 1
        k += 0.4

# ---------------- sheet 1: the wall, seen from outside the case
x0, x1 = PLATE["cx"] - 70, PLATE["cx"] + 70
line(x0, 0, x1, 0, 0.8); text(x1 + 1, -1, "cavity floor, Z 0", 7)
line(x0, CHAMFER, x1, CHAMFER, 0.3, (2, 2)); text(x1 + 1, CHAMFER - 1, "inner chamfer ends, Z 16.7", 6)
line(x0, FLOOR_TO_RIM, x1, FLOOR_TO_RIM, 0.8); text(x1 + 1, FLOOR_TO_RIM - 1, "rim, Z 124.87", 7)
for bx in BOSS_X:
    if x0 < bx < x1: rect(bx - 3, 30, bx + 3, 71, 0.3, (1, 1)); text(bx, 73, "inner rib", 5, anchor="c"); text(bx, 27, "(inside)", 5, anchor="c")
rect(PLATE["cx"] - PLATE["w"] / 2, PLATE["cz"] - PLATE["h"] / 2, PLATE["cx"] + PLATE["w"] / 2, PLATE["cz"] + PLATE["h"] / 2, 0.3, (3, 2))
text(PLATE["cx"] + PLATE["w"] / 2 + 2, PLATE["cz"] + PLATE["h"] / 2 - 3, "plate outline 82 x 54, gasket the same", 6.5)
for r in (DC, USB):
    circle(r["x"], r["z"], r["wall_hole"], 0.7); cross(r["x"], r["z"], 8); text(r["x"], r["z"] - r["wall_hole"] / 2 - 4, "hole saw %.0f" % r["wall_hole"], 7, anchor="c")
for sx, sz in SCREWS: circle(sx, sz, 4.5, 0.5); cross(sx, sz, 3)
text(SCREWS[0][0] - 8, SCREWS[0][1] - 1, "6 x 4.5 for M4", 6.5, anchor="r")
dim(DC["x"], USB["x"], 22, "36.0"); dim(SCREWS[0][0], SCREWS[2][0], 86, "56.0 (28.0 pitch)"); vdim(x0 + 4, 0, DC["z"], "55.0 above the floor"); vdim(x1 - 4, SCREWS[3][1], SCREWS[0][1], "46.0")
text(DC["x"], FLOOR_TO_RIM + 3, "DC hole X %.1f" % DC["x"], 7, anchor="c"); text(USB["x"], FLOOR_TO_RIM + 9, "USB hole X %.1f" % USB["x"], 7, anchor="c")
text(x0, FLOOR_TO_RIM + 3, "X %.0f" % x0, 7, anchor="r"); text(x1, FLOOR_TO_RIM + 3, "X %.0f  (case +X is to your left: you face the back wall from outside)" % x1, 7)
scale_bar(x0, -10)
notes(["SHEET 1 of 2: WALL. MeshSat field kit, Peli 1520 base, the BACK long wall (hinge side), seen from OUTSIDE, so case +X is on your left. Case frame: X along the long axis from the case centre, Z up from the cavity floor.",
       "Two hole-saw holes for the receptacle bodies and six M4 clearance holes for the connector plate. Tape this sheet on the outer skin with its floor line level with the inside floor (transfer the height from inside).",
       "The plate, not the wall, carries the sealing faces: the 1520 inner wall drafts about 2 degrees and the outer skin is ribbed (envelope STEP, vendor/peli/wall2.py), so a flanged receptacle cannot seal on the case itself.",
       "Why the back wall: the front wall carries the handle, the pressure valve, two rib clusters and both latch straps (Peli drawing 1521-931), and the end walls are too narrow between their ribs. Every through-hole here keeps 7 mm or more from the back wall's inner ribs (X -133.3 and -8.6 nearest, frame-leg drill points at 67 to 71 mm above the floor, appendix 25.1); the hinge sits at the rim, 43 mm above the plate.",
       "Cut order: mark, drill the six 4.5 holes, hole-saw the two 29 holes from outside, deburr both faces, dry-fit the plate, then gasket. The chamfer at the floor begins 16.7 mm up; nothing here reaches it."], -17)
c.showPage()

# ---------------- sheet 2: the plate, seen from outside (the face the plugs mate to)
rect(PLATE["cx"] - PLATE["w"] / 2, PLATE["cz"] - PLATE["h"] / 2, PLATE["cx"] + PLATE["w"] / 2, PLATE["cz"] + PLATE["h"] / 2, 0.8)
for r in (DC, USB):
    x, z, s = r["x"], r["z"], r["pattern"] / 2
    circle(x, z, r["hole"], 0.7); cross(x, z, 6)
    rect(x - r["flange"] / 2, z - r["flange"] / 2, x + r["flange"] / 2, z + r["flange"] / 2, 0.3, (2, 2))
    for dx in (-s, s):
        for dz in (-s, s): circle(x + dx, z + dz, r["screw"], 0.4); cross(x + dx, z + dz, 2.5)
    text(x, 72.5, r["name"], 6.5, anchor="c"); text(x, z + 3.5, "%.2f" % r["hole"], 6, anchor="c"); text(x + s + 2.5, z + s - 1, "4 x %.1f" % r["screw"], 5.5)
for sx, sz in SCREWS: circle(sx, sz, 4.5, 0.5); cross(sx, sz, 3)
dim(PLATE["cx"] - PLATE["w"] / 2, PLATE["cx"] + PLATE["w"] / 2, PLATE["cz"] + PLATE["h"] / 2 + 12, "82.0"); vdim(PLATE["cx"] + PLATE["w"] / 2 + 8, PLATE["cz"] - PLATE["h"] / 2, PLATE["cz"] + PLATE["h"] / 2, "54.0")
dim(DC["x"], USB["x"], PLATE["cz"] - PLATE["h"] / 2 - 6, "36.0"); dim(PLATE["cx"] - PLATE["w"] / 2, DC["x"], PLATE["cz"] - PLATE["h"] / 2 - 12, "23.0"); dim(SCREWS[3][0], SCREWS[5][0], PLATE["cz"] - PLATE["h"] / 2 - 18, "56.0 (28.0 pitch), screw rows 4.0 in from the top and bottom edges")
scale_bar(PLATE["cx"] - 70, -10)
notes(["SHEET 2 of 2: CONNECTOR PLATE, 82 x 54 x 3 mm aluminium (5052 or 6061), edges broken, seen from OUTSIDE the case. Gasket: 2 mm closed-cell neoprene or EPDM, same outline and holes, between plate and wall.",
       "Shore DC: Glenair D38999/20 shell 13 wall mount with round holes (D0), front panel mount: hole 19.05, four M3 clearance holes on a 23.01 square, flange 28.9 square. Its own gasket seals to the plate.",
       "USB host: Glenair 233-370 shell 15 wall mount D0, front panel mount: hole 23.01, four M3 clearance holes on a 24.61 square, flange 31.29 square; the 3 mm plate is inside its 1.6 to 6.35 mm panel range.",
       "Both receptacles: flange outside, gasket, plate, then the receptacle's own nuts inside; M3 x 10 stainless with spring washers. Plate to wall: six M4 x 16 stainless, washers both sides, Nyloc nuts inside; torque 1.2 N m in a cross pattern so the gasket loads evenly.",
       "Pin functions, cables and the dock leads: appendix 32.29 and ASSEMBLY.md section 4. Seen from outside the back wall (case +X to your left), as sheet 1. Nothing here has been cut yet."], -17)
c.showPage(); c.save(); print("wrote", out)
