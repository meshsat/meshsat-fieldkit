#!/usr/bin/env python3
"""MeshSat logo (full lockup, monochrome production treatment per the brand guide section 7) as filled silkscreen polygons.
Source: tools/logo_meshsat.json, traced from the approved sticker master (MeshSat_sticker_80x31mm_EXACT.pdf, 1753 ppi mask), never redrawn.
Usage as a module: add_logo(board, P, cx, cy, width_mm, layer). Standalone: logo_silk.py <out.kicad_pcb> renders a 100 x 30 test board."""
import json, os, sys, pcbnew
from pcbnew import VECTOR2I, FromMM
HERE = os.path.dirname(os.path.abspath(__file__))
def add_logo(board, P, cx, cy, width_mm, layer=pcbnew.F_SilkS, mirror=False):
    d = json.load(open(os.path.join(HERE, "logo_meshsat.json"))); x0, y0, x1, y1 = d["bbox"]
    s = width_mm / (x1 - x0); mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    def pt(x, y):
        X = (x - mx) * s; Y = (y - my) * s
        if mirror: X = -X
        return P(cx + X, cy - Y)          # artwork y grows downward; P() maps case y up
    n = 0
    for poly in d["polys"]:
        sps = pcbnew.SHAPE_POLY_SET(); sps.NewOutline()
        for x, y in poly["ext"]: v = pt(x, y); sps.Append(v.x, v.y)
        for hole in poly["holes"]:
            h = sps.NewHole(0)
            for x, y in hole: v = pt(x, y); sps.Append(v.x, v.y, 0, h)
        sps.Fracture()
        for k in range(sps.OutlineCount()):
            o = sps.Outline(k); one = pcbnew.SHAPE_POLY_SET(); one.NewOutline()
            for i in range(o.PointCount()): q = o.CPoint(i); one.Append(q.x, q.y)
            sh = pcbnew.PCB_SHAPE(board); sh.SetShape(pcbnew.SHAPE_T_POLY); sh.SetPolyShape(one); sh.SetLayer(layer); sh.SetFilled(True); sh.SetWidth(0); board.Add(sh); n += 1
    return n, width_mm * (y1 - y0) / (x1 - x0)
if __name__ == "__main__":
    out = sys.argv[1]; OX, OY = 50.0, 15.0
    def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
    b = pcbnew.BOARD()
    for (ax, ay, bx, by) in ((-50, -15, 50, -15), (50, -15, 50, 15), (50, 15, -50, 15), (-50, 15, -50, -15)):
        seg = pcbnew.PCB_SHAPE(b); seg.SetShape(pcbnew.SHAPE_T_SEGMENT); seg.SetStart(P(ax, ay)); seg.SetEnd(P(bx, by)); seg.SetLayer(pcbnew.Edge_Cuts); seg.SetWidth(FromMM(0.1)); b.Add(seg)
    n, h = add_logo(b, P, 0, 0, 75.0)
    pcbnew.SaveBoard(out, b); print("logo polygons:", n, "height %.2f mm at 75 mm wide" % h)
