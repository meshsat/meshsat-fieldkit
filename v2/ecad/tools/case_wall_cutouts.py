#!/usr/bin/env python3
"""1:1 templates for the two MIL-DTL-38999 wall receptacles and the nine SMA bulkheads on the Peli 1450 base (appendix 32.13 ruling 6, 32.29, 32.40 items 4, 8 and 9, 32.42; the 1520 version of 4 Sep is in the history).

The receptacles do not mount on the case wall directly: the 1520's inner wall drafts about 2 degrees and its outer skin is
ribbed, so a flanged connector could not seal on either face. Both sit on one flat aluminium plate (82 x 54 x 3 mm) bolted
over a window in the long wall on the dock's entry side, with a 2 mm closed-cell gasket between plate and wall. The plate
carries the exact Glenair cut-outs; the wall only needs two hole-saw holes and six screw holes.

Shore DC: Glenair D38999/20 shell 13 wall-mount receptacle, round holes (D0), front panel mount on the plate: flange 28.9
square, four holes on a 23.01 square, plate hole 19.05 (Glenair panel cut-out sheet type B, shell 12-13: AA .750; 233-105
table shell 13: C BSC .906, E .136/.120, B sq 1.138/1.114).
USB host: Glenair 233-370 shell 15 wall-mount receptacle D0: flange 31.29 square, four holes on a 24.61 square, plate hole
23.01 (233-370 sheet: 2x .969 (24.61), 4x .132/.124; cut-out sheet type B shell 14-15: AA .906), panel .0625 to .250 in.
Case (Peli 1450, drawing 1451-931 and its DXF in vendor/peli/1450): base 109 deep, lid 45, floor 371 x 259 at the rim, five inner ribs on the long
walls at X -170, -95, -18, +60, +137, hinge clusters outside at X -167 to -74 and +58 to +160, plain end walls with ribs at the corners, frame skirt
from Z 100. Wall: the BACK long wall, the hinge side (case +Y); the plate stands upright between the ribs at X -95 and -18 (32.40 item 9).
Frame: case-centred, X along the long axis, Z up from the cavity floor. Both sheets are drawn as seen from OUTSIDE the back
wall, so case +X is on the viewer's left. Sheets 3 and 4 put the seven SMA antenna bulkheads on the two end walls. 1:1 on A4 landscape; check the 100 mm bar with a rule.  Usage: case_wall_cutouts.py <out.pdf>"""
import sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

PLATE = dict(cx=-56.0, cz=54.0, w=54.0, h=82.0, t=3.0)     # 1450: the plate stands upright between the back wall ribs at X -95 and -18 (32.40 item 9)
SCREWS = [(-79.0, 82.0), (-33.0, 82.0), (-79.0, 54.0), (-33.0, 54.0), (-79.0, 26.0), (-33.0, 26.0)]   # M4, wall and plate: two columns 46 apart, three rows 28 apart
DC = dict(name="DC: D38999/20 sh. 13 D0", x=-56.0, z=34.0, hole=19.05, flange=28.9, pattern=23.01, screw=3.3, wall_hole=29.0)
USB = dict(name="USB: 233-370 sh. 15 D0", x=-56.0, z=74.0, hole=23.01, flange=31.29, pattern=24.61, screw=3.3, wall_hole=29.0)
BOSS_X = [-95.0, -18.0]           # the 1450 back wall's inner ribs nearest the plate (five ribs at X -170, -95, -18, +60, +137 per the 1451-931 DXF, section B-B)
VIEW = -1.0                        # seen from outside the back wall: case +X to the viewer's left
FLOOR_TO_RIM = 109.0; CHAMFER = 10.0   # 1451-931: base 109 deep; the floor fillet read at about 10 mm

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
def text(x, z, s, size=8, angle=0, anchor="l", paper=False):
    """Text at a case position (mirrored with the view) or, with paper=True, at a paper offset x in mm from the sheet centre."""
    px, pz = (W / 2 + x * mm, oz + z * mm) if paper else P(x, z); c.saveState(); c.translate(px, pz); c.rotate(angle); c.setFont("Helvetica", size)
    {"c": c.drawCentredString, "r": c.drawRightString}.get(anchor, c.drawString)(0, 0, s); c.restoreState()
def cross(x, z, r=4):
    line(x - r, z, x + r, z, 0.2); line(x, z - r, x, z + r, 0.2)
def dim(x1, x2, z, label):
    line(x1, z, x2, z, 0.25); line(x1, z - 1.5, x1, z + 1.5, 0.25); line(x2, z - 1.5, x2, z + 1.5, 0.25); text((x1 + x2) / 2, z + 1.5, label, 7, anchor="c")
def vdim(x, z1, z2, label):
    line(x, z1, x, z2, 0.25); line(x - 1.5, z1, x + 1.5, z1, 0.25); line(x - 1.5, z2, x + 1.5, z2, 0.25); text(x - VIEW * 1.8, (z1 + z2) / 2, label, 7, angle=90, anchor="c")
def _unused():
    pass
def scale_bar(x, z):
    """A 100 mm bar drawn in paper coordinates at paper offset x (mm from the sheet centre)."""
    c.setLineWidth(1.0); c.line(W / 2 + x * mm, oz + z * mm, W / 2 + (x + 100) * mm, oz + z * mm)
    c.setLineWidth(0.6); c.line(W / 2 + x * mm, oz + (z - 2) * mm, W / 2 + x * mm, oz + (z + 2) * mm); c.line(W / 2 + (x + 100) * mm, oz + (z - 2) * mm, W / 2 + (x + 100) * mm, oz + (z + 2) * mm)
    text(x + 50, z - 5, "100 mm at 1:1 (print at 100 percent, no fit to page)", 7, anchor="c", paper=True)
def notes(lines, z0):
    import textwrap
    k = 0
    for n in lines:
        for part in textwrap.wrap(n, 150): text(-140, z0 - 3.6 * k, part, 6.2, paper=True); k += 1
        k += 0.4

# ---------------- sheet 1: the wall, seen from outside the case
x0, x1 = PLATE["cx"] - 60, PLATE["cx"] + 60
line(x0, 0, x1, 0, 0.8); text(72, -1, "cavity floor, Z 0", 7, paper=True)
line(x0, CHAMFER, x1, CHAMFER, 0.3, (2, 2)); text(72, CHAMFER - 1, "floor fillet ends, Z 10", 6, paper=True)
line(x0, FLOOR_TO_RIM, x1, FLOOR_TO_RIM, 0.8); text(72, FLOOR_TO_RIM - 1, "rim, Z 109", 7, paper=True); line(x0, 100, x1, 100, 0.3, (2, 2)); text(72, 99, "frame skirt from Z 100", 6, paper=True)
for bx in BOSS_X:
    if x0 < bx < x1: rect(bx - 3, 25, bx + 3, 95, 0.3, (1, 1)); text(bx, 104, "inner rib", 5, anchor="c"); text(bx, 101, "(inside)", 5, anchor="c")
rect(PLATE["cx"] - PLATE["w"] / 2, PLATE["cz"] - PLATE["h"] / 2, PLATE["cx"] + PLATE["w"] / 2, PLATE["cz"] + PLATE["h"] / 2, 0.3, (3, 2))
text(PLATE["cx"], PLATE["cz"] - PLATE["h"] / 2 - 4, "plate outline 54 x 82 upright, gasket the same", 6.5, anchor="c")
for r in (DC, USB):
    circle(r["x"], r["z"], r["wall_hole"], 0.7); cross(r["x"], r["z"], 8); text(r["x"], r["z"] - r["wall_hole"] / 2 - 4, "hole saw %.0f" % r["wall_hole"], 7, anchor="c")
for sx, sz in SCREWS: circle(sx, sz, 4.5, 0.5); cross(sx, sz, 3)
text(PLATE["cx"], PLATE["cz"] + PLATE["h"] / 2 + 6, "6 x 4.5 for M4, columns 46 apart, rows 28 apart", 6.5, anchor="c")
vdim(x0 + 4, 0, DC["z"], "34.0 above the floor"); vdim(x0 + 10, DC["z"], USB["z"], "40.0"); dim(SCREWS[0][0], SCREWS[1][0], 96, "46.0"); vdim(x1 - 4, SCREWS[4][1], SCREWS[0][1], "56.0 (28.0 pitch)")
text(DC["x"], FLOOR_TO_RIM + 12, "DC hole X %.1f Z %.0f, USB hole X %.1f Z %.0f" % (DC["x"], DC["z"], USB["x"], USB["z"]), 7, anchor="c")
text(x0, FLOOR_TO_RIM + 3, "X %.0f" % x0, 7); text(x1, FLOOR_TO_RIM + 3, "X %.0f" % x1, 7, anchor="r"); text(0, FLOOR_TO_RIM + 16, "seen from OUTSIDE the back wall: case +X is to your left", 7, anchor="c", paper=True)
scale_bar(-140, -10)
notes(["SHEET 1 of 4: BACK WALL. MeshSat field kit, Peli 1450 base (32.40 item 4), the BACK long wall (hinge side), seen from OUTSIDE, so case +X is on your left. Case frame: X along the long axis from the case centre, Z up from the cavity floor. The plate stands upright between the inner ribs at X -95 and -18 (item 9) and between the hinge clusters (X -167 to -74, +58 to +160).",
       "Two hole-saw holes for the receptacle bodies and six M4 clearance holes for the connector plate. Tape this sheet on the outer skin with its floor line level with the inside floor (transfer the height from inside).",
       "The plate, not the wall, carries the sealing faces: the inner wall drafts and the outer skin is not flat, so a flanged receptacle cannot seal on the case itself (the 1520 study of 32.29; the 1450 drawing 1451-931 in vendor/peli/1450 shows the same construction).",
       "Why the back wall: the front wall carries the handle, the pressure valve, two rib clusters and both latch straps (Peli drawing 1521-931), and the end walls are too narrow between their ribs. Every through-hole here keeps 7 mm or more from the back wall's inner ribs (X -133.3 and -8.6 nearest, frame-leg drill points at 67 to 71 mm above the floor, appendix 25.1); the hinge sits at the rim, 43 mm above the plate.",
       "Cut order: mark, drill the six 4.5 holes, hole-saw the two 29 holes from outside, deburr both faces, dry-fit the plate, then gasket. The floor fillet ends about 10 mm up; the plate starts at Z 13."], -17)
c.showPage()

# ---------------- sheet 2: the plate, seen from outside (the face the plugs mate to)
rect(PLATE["cx"] - PLATE["w"] / 2, PLATE["cz"] - PLATE["h"] / 2, PLATE["cx"] + PLATE["w"] / 2, PLATE["cz"] + PLATE["h"] / 2, 0.8)
for r in (DC, USB):
    x, z, s = r["x"], r["z"], r["pattern"] / 2
    circle(x, z, r["hole"], 0.7); cross(x, z, 6)
    rect(x - r["flange"] / 2, z - r["flange"] / 2, x + r["flange"] / 2, z + r["flange"] / 2, 0.3, (2, 2))
    for dx in (-s, s):
        for dz in (-s, s): circle(x + dx, z + dz, r["screw"], 0.4); cross(x + dx, z + dz, 2.5)
    text(x + 32, z, r["name"], 6.5, anchor="c", angle=90); text(x, z + 3.5, "%.2f" % r["hole"], 6, anchor="c"); text(x + s + 2.5, z + s - 1, "4 x %.1f" % r["screw"], 5.5)
for sx, sz in SCREWS: circle(sx, sz, 4.5, 0.5); cross(sx, sz, 3)
dim(PLATE["cx"] - PLATE["w"] / 2, PLATE["cx"] + PLATE["w"] / 2, PLATE["cz"] + PLATE["h"] / 2 + 12, "54.0"); vdim(PLATE["cx"] + PLATE["w"] / 2 + 8, PLATE["cz"] - PLATE["h"] / 2, PLATE["cz"] + PLATE["h"] / 2, "82.0")
dim(DC["x"], USB["x"], PLATE["cz"] - PLATE["h"] / 2 - 6, "36.0"); dim(PLATE["cx"] - PLATE["w"] / 2, DC["x"], PLATE["cz"] - PLATE["h"] / 2 - 12, "23.0"); dim(SCREWS[3][0], SCREWS[5][0], PLATE["cz"] - PLATE["h"] / 2 - 18, "56.0 (28.0 pitch), screw rows 4.0 in from the top and bottom edges")
scale_bar(-140, -10)
notes(["SHEET 2 of 4: CONNECTOR PLATE, 54 wide x 82 tall x 3 mm aluminium (5052 or 6061), upright, shore DC below and USB above 40 mm apart, edges broken, seen from OUTSIDE the case. Gasket: 2 mm closed-cell neoprene or EPDM, same outline and holes, between plate and wall.",
       "Shore DC: Glenair D38999/20 shell 13 wall mount with round holes (D0), front panel mount: hole 19.05, four M3 clearance holes on a 23.01 square, flange 28.9 square. Its own gasket seals to the plate.",
       "USB host: Glenair 233-370 shell 15 wall mount D0, front panel mount: hole 23.01, four M3 clearance holes on a 24.61 square, flange 31.29 square; the 3 mm plate is inside its 1.6 to 6.35 mm panel range.",
       "Both receptacles on a Glenair 930-001 silicone flange gasket (930-001S06 under the shell 13, 930-001S07 under the shell 15, 0.030 in thick; their hole patterns match the receptacles): flange outside, gasket, plate, then the receptacle's own nuts inside; M3 x 10 stainless with spring washers. Plate to wall: six M4 x 16 stainless with EPDM-bonded sealing washers under the outside heads, washers both sides, Nyloc nuts inside; torque 1.2 N m in a cross pattern so the gasket loads evenly.",
       "Pin functions, cables and the dock leads: appendix 32.29 and ASSEMBLY.md section 4. Seen from outside the back wall (case +X to your left), as sheet 1. Nothing here has been cut yet."], -17)
c.showPage()

# ---------------- sheet 3: the seven SMA antenna bulkheads on the two end walls (the wall strip E3 is retired, 32.13 ruling 5)
# Amphenol Connex 132170 SMA female-female bulkhead coupler: 6.5 mm D-hole with the flat at 6.00 across (vendor/rf drawing), 8 mm nut.
# Four sites per end wall at Y -60, -30, +30, +60 between the wall's inner ribs (none on the 1450 end walls), 55 mm above the floor.
SMA_Z = 88.0   # 1450 (32.40 item 8): above the battery row (top 78 mm) along the west end wall, below the frame skirt (Z 100 to 109)
WEST = [(-72.0, "UHF"), (-24.0, "WIFI 2.4"), (24.0, "GNSS"), (72.0, "SDR")]        # west end wall (case -X): the strip's four western clamps; since B13 the third path carries the NEO-M9N antenna (the CM5 antenna is dual-band, one path)
EAST = [(-96.0, "LTE"), (-48.0, "IRIDIUM"), (0.0, "LORA"), (48.0, "WIFI P2P A"), (96.0, "WIFI P2P B")]   # five sites at one height, 48 mm apart so the Iridium patch clears its neighbours  # east end wall (case +X); B14: the spare took the first WiFi P2P lead, the second sits in a second row at Z 90 (clear of the Iridium patch, whose top is at Z 82)
def end_wall(title, sites, y_sign, ox_paper):
    """One end wall seen from OUTSIDE: paper x = case Y times y_sign (so the viewer's left is the right case direction)."""
    def Q(y, z): return W / 2 + (ox_paper + y_sign * y) * mm, oz + z * mm
    c.setLineWidth(0.8); c.line(*Q(-129.5, 0), *Q(129.5, 0)); c.line(*Q(-129.5, FLOOR_TO_RIM), *Q(129.5, FLOOR_TO_RIM))
    c.setLineWidth(0.3); c.setDash(1, 1); c.line(*Q(-129.5, 100), *Q(129.5, 100))
    for ry in (-76.0, 76.0):
        qx, qz = Q(ry, 100); c.rect(qx - 3 * mm, qz - 20 * mm, 6 * mm, 20 * mm, stroke=1, fill=0)
    if y_sign > 0:
        qx, qz = Q(-114.5, 0); c.rect(qx, qz, 229 * mm, 78 * mm, stroke=1, fill=0); c.setFont("Helvetica", 6); c.drawCentredString(qx + 114.5 * mm, qz + 40 * mm, "battery row inside, 229 x 78 (top 78)")
    c.setDash()
    for site in sites:
        y, name = site[0], site[1]; z = site[2] if len(site) > 2 else SMA_Z
        qx, qz = Q(y, z); c.setLineWidth(0.7); c.circle(qx, qz, 3.25 * mm, stroke=1, fill=0)
        c.setLineWidth(0.5); c.line(qx + 2.75 * mm, qz - 1.73 * mm, qx + 2.75 * mm, qz + 1.73 * mm)   # the D flat at 6.00 across
        c.setLineWidth(0.2); c.line(qx - 5 * mm, qz, qx + 5 * mm, qz); c.line(qx, qz - 5 * mm, qx, qz + 5 * mm)
        c.setFont("Helvetica", 6.5); c.drawCentredString(qx, qz + 5 * mm, name); c.drawCentredString(qx, qz - 7 * mm, "Y %+.0f" % y if z == SMA_Z else "Y %+.0f  Z %.0f" % (y, z))
    c.setFont("Helvetica", 7); qx, qz = Q(0, FLOOR_TO_RIM + 4); c.drawCentredString(qx, qz, title)
    qx, qz = Q(0, -4); c.drawCentredString(qx, qz, "cavity floor, Z 0; holes at Z %.0f; rim Z 109, frame skirt from Z 100, frame-leg bosses at Y +-76 near the rim" % SMA_Z)
for k, (title, sites, sign) in enumerate((("WEST end wall (case -X), seen from outside: case +Y to your right", WEST, 1.0), ("EAST end wall (case +X), seen from outside: case +Y to your left", EAST, -1.0))):
    if k: c.showPage()
    end_wall(title, sites, sign, 0.0)
    scale_bar(-140, -14)
    notes(["SHEET %d of 4: the SMA antenna bulkheads on this end wall of the Peli 1450, 88 mm above the floor (32.40 item 8): west UHF, WIFI 2.4, GNSS, SDR at Y -72, -24, +24, +72; east LTE, IRIDIUM, LORA, WIFI P2P A, WIFI P2P B at Y -96, -48, 0, +48, +96. Print at 100 percent." % (3 + k),
       "Coupler: Amphenol Connex 132170 SMA female-female bulkhead (vendor/rf), 6.5 mm D-hole with the flat filed to 6.00 across so the coupler cannot turn when a pigtail is torqued; 8 mm nut and lock washer inside, the NBR O-ring 6.5 x 1.0 under the outside hex.",
       "The sites sit on the plain band of the end walls (ribs only at the corners, 1451-931) and above the battery row along the west wall (top 78 mm) with the frame skirt 12 mm above them. Inside, an RG-316 jumper runs from each coupler to its float nest on the strip: west wall to the UHF, WIFI 2.4, GNSS and SDR nests, east wall to LTE, IRIDIUM and LORA (about 150 to 250 mm each); the two WIFI P2P couplers take IPEX pigtails straight from the M.2 card on PCB-B, no nest.",
       "Outside, the antenna pigtails screw on as before, 0.45 N m once. The retired wall strip E3 carried these same seven couplers; only their home changed."], -22)
c.showPage(); c.save(); print("wrote", out)
