#!/usr/bin/env python3
"""PCB-E2 RF JUNCTION STRIP: a 2.0 mm FR-4 shelf on the Peli 1520's +Z (front) wall, 57.8 mm below the rim, carrying seven SMA female-female
bulkhead couplers (vertical; D-hole per the Amphenol Connex 132170 drawing rev D: Ø6.50 with the flat at 6.00 across, i.e. 2.75 mm off centre; panel 2.0 to 6.5 mm) so the device pigtails plug from above and the wall pigtails from below.
Mounts on the case's pre-marked wall drill points (1521-931 Bottom STEP: X +-8.6, +-133.3, +-152.4 at Y -57.4/-57.8 on the +Z wall) with M3 screws.
Usage: gen_pcb_e2.py <out.kicad_pcb>. Frame: strip-local, +X along the wall (case X), +Y away from the wall into the cavity."""
import math, sys, os, pcbnew
from pcbnew import VECTOR2I, FromMM
OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-e2-rfjunction.kicad_pcb"
L, W, R = 330.0, 32.0, 3.0
WALL_PTS = [(-152.4, 4.0), (-133.3, 4.0), (-8.6, 4.0), (8.6, 4.0), (133.3, 4.0), (152.4, 4.0)]     # M3 clearance Ø3.4, 4 mm from the wall edge (the strip's -Y edge lies on the wall)
COUPLERS = [(-135, "UHF"), (-90, "SDR"), (-45, "WIFI1"), (0, "WIFI2"), (45, "LTE"), (90, "IRID"), (135, "LORA")]   # 45 mm pitch, SMA nut Ø8 both sides
OX, OY = 200.0, 100.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
board = pcbnew.BOARD()
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-E2 RF JUNCTION STRIP"); tb.SetRevision("A (E3)"); tb.SetDate("2026-09-04"); tb.SetCompany("MeshSat")
tb.SetComment(0, "MESHSAT-709. Mechanical strip on the 1520 front wall: 7 SMA F-F bulkhead couplers, device pigtails from above. tools/gen_pcb_e2.py"); board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(2.0)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
def shape(layer, width=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetLayer(layer); s.SetWidth(FromMM(width)); board.Add(s); return s
def line(x1, y1, x2, y2, layer, width=0.1):
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2)); return s
def arc(cx, cy, r, a0, a1, layer, width=0.1):
    am = (a0 + a1) / 2.0; pt = lambda a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*pt(a0)), P(*pt(am)), P(*pt(a1))); return s
def circle(cx, cy, d, layer, width=0.1):
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetStart(P(cx, cy)); s.SetEnd(P(cx + d / 2.0, cy)); return s
def rounded_rect(x0, y0, x1, y1, r, layer, width=0.1):
    line(x0 + r, y0, x1 - r, y0, layer, width); line(x1, y0 + r, x1, y1 - r, layer, width); line(x1 - r, y1, x0 + r, y1, layer, width); line(x0, y1 - r, x0, y0 + r, layer, width)
    arc(x1 - r, y0 + r, r, 270, 360, layer, width); arc(x1 - r, y1 - r, r, 0, 90, layer, width); arc(x0 + r, y1 - r, r, 90, 180, layer, width); arc(x0 + r, y0 + r, r, 180, 270, layer, width)
def text(txt, x, y, layer, size=2.0, thick=0.3, angle=0.0):
    t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(P(x, y)); t.SetLayer(layer); t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(thick)); t.SetTextAngleDegrees(angle); board.Add(t)
    return t
def dhole(cx, cy, d, flat):
    """D-shaped cutout on Edge.Cuts: circle of diameter d with one flat at distance `flat` from the centre (anti-rotation for the coupler)."""
    a = math.degrees(math.acos(flat / (d / 2)))                      # half-angle of the flat, seen from the centre
    yf = (d / 2) * math.sin(math.radians(a))
    arc(cx, cy, d / 2, a, 360.0 - a, pcbnew.Edge_Cuts)               # big arc from the flat's upper end (a) the long way round to its lower end (-a)
    line(cx + flat, cy + yf, cx + flat, cy - yf, pcbnew.Edge_Cuts)   # the flat itself, at x = +flat
def mounting_hole(ref, x, y, d, value):
    fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/MountingHole.pretty", "MountingHole_3.2mm_M3" if d <= 3.3 else "MountingHole_3.2mm_M3")
    if fp is None: raise SystemExit("mounting hole footprint missing")
    fp.SetReference(ref); fp.SetValue(value); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetPosition(P(x, y)); board.Add(fp); return fp
rounded_rect(-L / 2, 0, L / 2, W, R, pcbnew.Edge_Cuts)
for i, (x, y) in enumerate(WALL_PTS, 1): mounting_hole("H%d" % i, x, y, 3.4, "M3 to the case wall drill point"); circle(x, y, 7.0, pcbnew.F_SilkS, 0.12)
for i, (x, name) in enumerate(COUPLERS, 1):
    dhole(x, 18.0, 6.5, 2.75); circle(x, 18.0, 9.0, pcbnew.F_SilkS, 0.15); text(name, x, 27.5, pcbnew.F_SilkS, 2.5, 0.4)   # E3: flat 6.00 across per the 132170 drawing (was 6.25)
text("MESHSAT PCB-E2 RF JUNCTION  -  device pigtails above, wall pigtails below  -  RF HAZARD DURING TX", 0, 9.5, pcbnew.F_SilkS, 1.4, 0.22)
t_ = text("front wall (+Z) side  |  screws M3 into the 1520 wall drill points 57.8 below the rim", 0, 30.0, pcbnew.B_SilkS, 1.6, 0.25); t_.SetMirrored(True)
pcbnew.SaveBoard(OUT, board)
s = open(OUT).read().replace('(paper "A4")', '(paper "A3")'); open(OUT, "w").write(s)
print("saved", OUT, "couplers:", len(COUPLERS), "wall points:", len(WALL_PTS))
