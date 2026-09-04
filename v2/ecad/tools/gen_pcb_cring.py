#!/usr/bin/env python3
# RETIRED with C5 (5 Sep 2026, appendix 32.34): the sealed e-paper window carries a lens on the face, so the flush-glass spacer ring R1 has no use
# and its 0.1 mm web could not be fabricated. Kept for the record; no chain calls it.
"""PCB-C spacer ring (R1): a 1.0 mm FR-4 frame, no copper, between the WeAct 3.7 module's lands and the panel underside so the glass face ends flush
with the panel face (0.95 glass + 0.05 tape + 1.0 ring + 0.05 tape = 2.05 against the 2.0 mm panel). Same window as the panel, same module outline.
Usage: gen_pcb_cring.py <out.kicad_pcb>"""
import math, sys, os, pcbnew
from pcbnew import VECTOR2I, FromMM
OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-c-ring.kicad_pcb"
W, H, R = 105.79, 53.80, 1.4; GLASS = (92.99, 53.0); CLR = (0.6, 0.3); OX, OY = 60.0, 30.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
board = pcbnew.BOARD(); board.SetCopperLayerCount(2)
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-C spacer ring for the 3.7 in e-paper"); tb.SetRevision("A (R1)"); tb.SetDate("2026-09-03"); tb.SetCompany("MeshSat")
tb.SetComment(0, "MESHSAT-709. 1.0 mm FR-4, no copper, black. Taped between the WeAct 3.7 module lands and the PCB-C underside. tools/gen_pcb_cring.py"); board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.0)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
def shape(layer, width=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetLayer(layer); s.SetWidth(FromMM(width)); board.Add(s); return s
def line(x1, y1, x2, y2, layer, width=0.1):
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2)); return s
def arc(cx, cy, r, a0, a1, layer, width=0.1):
    am = (a0 + a1) / 2.0; pt = lambda a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*pt(a0)), P(*pt(am)), P(*pt(a1))); return s
def rounded_rect(x0, y0, x1, y1, r, layer, width=0.1):
    line(x0 + r, y0, x1 - r, y0, layer, width); line(x1, y0 + r, x1, y1 - r, layer, width); line(x1 - r, y1, x0 + r, y1, layer, width); line(x0, y1 - r, x0, y0 + r, layer, width)
    arc(x1 - r, y0 + r, r, 270, 360, layer, width); arc(x1 - r, y1 - r, r, 0, 90, layer, width); arc(x0 + r, y1 - r, r, 90, 180, layer, width); arc(x0 + r, y0 + r, r, 180, 270, layer, width)
rounded_rect(-W / 2, -H / 2, W / 2, H / 2, R, pcbnew.Edge_Cuts)
gx, gy = GLASS[0] / 2 + CLR[0], GLASS[1] / 2 + CLR[1]; rounded_rect(-gx, -gy, gx, gy, 1.0, pcbnew.Edge_Cuts)
for (x, y) in ((-W / 2 + 2.80, -H / 2 + 2.80), (W / 2 - 2.80, -H / 2 + 2.80), (-W / 2 + 2.80, H / 2 - 2.80), (W / 2 - 2.80, H / 2 - 2.80)):
    fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/MountingHole.pretty", "MountingHole_3.2mm_M3"); fp.SetReference("H%d" % (len(list(board.GetFootprints())) + 1)); fp.SetValue("module hole, alignment"); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetPosition(P(x, y)); board.Add(fp)
t = pcbnew.PCB_TEXT(board); t.SetText("RING 1.0"); t.SetPosition(P(-W / 2 + 2.7, 0)); t.SetLayer(pcbnew.F_SilkS); t.SetTextSize(VECTOR2I(FromMM(1.0), FromMM(1.0))); t.SetTextThickness(FromMM(0.16)); t.SetTextAngleDegrees(90); board.Add(t)
pcbnew.SaveBoard(OUT, board); print("saved", OUT, "window %.2f x %.2f" % (2 * gx, 2 * gy))
