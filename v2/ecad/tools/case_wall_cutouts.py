#!/usr/bin/env python3
"""1:1 drilling template for the two MIL-DTL-38999 wall receptacles on the Peli 1520 base (appendix 32.13 ruling 6, 32.29).

Shore DC: Glenair D38999/20 shell 13 wall-mount receptacle with round holes (D0), front panel mount: flange 28.9 mm square,
four holes on a 23.01 mm square, hole 19.05 mm (Glenair panel cut-out sheet, type B, shell 12-13: AA .750; 233-105 dimension
table shell 13: C BSC .906, E .136/.120 holes, B sq 1.138/1.114).
USB host: Glenair 233-370 shell 15 wall-mount receptacle D0: flange 31.29 mm square, four holes on a 24.61 mm square, hole
23.01 mm (233-370 sheet: 2x .969 (24.61), 4x .132/.124; cut-out sheet type B shell 14-15: AA .906), panel .0625 to .250 in.
Frame: case-centred, X along the long axis, Z up from the floor of the base cavity. The wall is the long wall on the dock's
entry side (the strip's J_DCIN sits at case (-104, -106)). Prints 1:1 on A4 landscape; check the 100 mm bar with a rule.
Usage: case_wall_cutouts.py <out.pdf>"""
import sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# --- placement (case frame, mm): X along the wall, Z above the cavity floor
DC = dict(name="SHORE DC  D38999/20 shell 13, D0, front mount", x=-110.0, z=55.0, hole=19.05, flange=28.9, pattern=23.01, screw=3.3)
USB = dict(name="USB HOST  233-370 shell 15, D0, front mount", x=-72.0, z=55.0, hole=23.01, flange=31.29, pattern=24.61, screw=3.3)
WALL_X0, WALL_X1 = -150.0, -30.0          # the strip of wall drawn
BOSS_X = [-148.8, -151.5, -48.7, -51.4, -133.3, -152.4, -8.6]   # frame-leg drill points on either long wall (appendix 25.1), keep 19 mm clear
FLOOR_TO_RIM = 124.87                     # cavity depth (25.1)
WALL_T = float(sys.argv[2]) if len(sys.argv) > 2 else None   # wall thickness at the cut, from the probe (vendor/peli/wall.py)

out = sys.argv[1] if len(sys.argv) > 1 else "wall-cutouts-1to1.pdf"
c = canvas.Canvas(out, pagesize=landscape(A4)); W, H = landscape(A4)
# paper mapping: 1:1, case X to the right, Z up; the wall strip sits in the middle of the sheet
ox = W / 2 - (WALL_X0 + WALL_X1) / 2 * mm; oz = 60 * mm
def P(x, z): return ox + x * mm, oz + z * mm
def line(x1, z1, x2, z2, w=0.3, dash=None):
    c.setLineWidth(w)
    if dash: c.setDash(*dash)
    c.line(*P(x1, z1), *P(x2, z2)); c.setDash()
def circle(x, z, d, w=0.4):
    c.setLineWidth(w); px, pz = P(x, z); c.circle(px, pz, d / 2 * mm, stroke=1, fill=0)
def text(x, z, s, size=8, angle=0, anchor="l"):
    px, pz = P(x, z); c.saveState(); c.translate(px, pz); c.rotate(angle); c.setFont("Helvetica", size)
    if anchor == "c": c.drawCentredString(0, 0, s)
    elif anchor == "r": c.drawRightString(0, 0, s)
    else: c.drawString(0, 0, s)
    c.restoreState()
def cross(x, z, r=4):
    line(x - r, z, x + r, z, 0.2); line(x, z - r, x, z + r, 0.2)
def dim(x1, x2, z, label, above=True):
    line(x1, z, x2, z, 0.25); line(x1, z - 1.5, x1, z + 1.5, 0.25); line(x2, z - 1.5, x2, z + 1.5, 0.25)
    text((x1 + x2) / 2, z + (1.5 if above else -4), label, 7, anchor="c")
def vdim(x, z1, z2, label):
    line(x, z1, x, z2, 0.25); line(x - 1.5, z1, x + 1.5, z1, 0.25); line(x - 1.5, z2, x + 1.5, z2, 0.25)
    text(x + 1.5, (z1 + z2) / 2, label, 7, angle=90, anchor="c")

# the wall strip: floor line and rim line
line(WALL_X0, 0, WALL_X1, 0, 0.8); text(WALL_X1 + 1, -1, "cavity floor (Z 0)", 7)
line(WALL_X0, FLOOR_TO_RIM, WALL_X1, FLOOR_TO_RIM, 0.8); text(WALL_X1 + 1, FLOOR_TO_RIM - 1, "rim (Z %.2f)" % FLOOR_TO_RIM, 7)
for x in BOSS_X:
    if WALL_X0 < x < WALL_X1:
        line(x, FLOOR_TO_RIM - 57.8, x, FLOOR_TO_RIM - 53.6, 1.2); text(x, FLOOR_TO_RIM - 62, "leg boss", 5, angle=90, anchor="r")
# the two receptacles
for r in (DC, USB):
    x, z, s = r["x"], r["z"], r["pattern"] / 2
    circle(x, z, r["hole"], 0.6); cross(x, z, 6)
    c.setDash(2, 2); c.setLineWidth(0.3); px, pz = P(x - r["flange"] / 2, z - r["flange"] / 2); c.rect(px, pz, r["flange"] * mm, r["flange"] * mm, stroke=1, fill=0); c.setDash()
    for dx in (-s, s):
        for dz in (-s, s): circle(x + dx, z + dz, r["screw"], 0.4); cross(x + dx, z + dz, 2.5)
    text(x, z + r["flange"] / 2 + (3 if r is DC else 9), r["name"], 6.5, anchor="c")
    text(x, z - r["flange"] / 2 - 5, "hole %.2f, 4 x %.1f on %.2f sq" % (r["hole"], r["screw"], r["pattern"]), 6.5, anchor="c")
# dimensions: X from the case centre line (marked at the right if in range), Z from the floor
dim(DC["x"], USB["x"], 28, "%.1f" % (USB["x"] - DC["x"]))
vdim(WALL_X0 + 6, 0, DC["z"], "%.1f from the floor" % DC["z"])
text(WALL_X0, FLOOR_TO_RIM + 4, "X %.1f" % WALL_X0, 7); text(WALL_X1, FLOOR_TO_RIM + 4, "X %.1f" % WALL_X1, 7, anchor="r")
text(DC["x"], FLOOR_TO_RIM + 4, "DC centre X %.1f" % DC["x"], 7, anchor="c"); text(USB["x"], FLOOR_TO_RIM + 10, "USB centre X %.1f" % USB["x"], 7, anchor="c")
# scale bar and notes
bx = WALL_X0; line(bx, -18, bx + 100, -18, 1.0); line(bx, -20, bx, -16, 0.6); line(bx + 100, -20, bx + 100, -16, 0.6); text(bx + 50, -24, "100 mm at 1:1 (print at 100 percent, no fit to page)", 7, anchor="c")
notes = ["MeshSat field kit, Peli 1520 base: wall receptacle cut-outs, long wall on the dock entry side, viewed from OUTSIDE the case.",
         "Case frame: X along the long axis from the case centre, Z up from the cavity floor. Both flanges sit on the outer wall face (front panel mount), bodies inside.",
         "Shore DC: Glenair D38999/20 shell 13 wall mount D0 (hole 19.05, four M3 clearance holes on a 23.01 square, flange 28.9 square).",
         "USB host: Glenair 233-370 shell 15 wall mount D0 (hole 23.01, four M3 clearance holes on a 24.61 square, flange 31.29 square); panel 1.6 to 6.35 mm at the cut.",
         "Centres X -110 and X -72 keep 19 mm or more from every frame-leg boss on either long wall (appendix 25.1). Centre height 55 mm above the floor clears the strip, the block and the stack.",
         ("Wall at the cut: %.1f mm from the STEP section (vendor/peli/wall.py). " % WALL_T if WALL_T else "Wall thickness at the cut: see appendix 32.29 (STEP section). ") + "Spot-face the inside to 6 mm where the wall is thicker, so the 233-370 body reaches through.",
         "Drill the four screw holes first through the template, then hole-saw the centre. Deburr, dry-fit, gasket outside, nuts inside with the receptacle's own hardware. Do not machine near the latch or handle bosses."]
for i, n in enumerate(notes): text(WALL_X0, -32 - 4.2 * i, n, 6.5)
c.showPage(); c.save(); print("wrote", out)
