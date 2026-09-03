#!/usr/bin/env python3
"""Fallback for a single copper_edge_clearance hit against an inner cutout: move the offending track's endpoints near the hit point away from it.
Usage: nudge_edge_track.py <board> <net> <layer F.Cu|B.Cu> <hit_x> <hit_y> <away_x> <away_y> [radius_mm=4]  (case-frame mm; OX/OY of the panel)"""
import sys, pcbnew
from pcbnew import VECTOR2I, FromMM
OX, OY = 297.0, 210.0
b = pcbnew.LoadBoard(sys.argv[1]); net, layer = sys.argv[2], sys.argv[3]; hx, hy, ax, ay = map(float, sys.argv[4:8]); rad = float(sys.argv[8]) if len(sys.argv) > 8 else 4.0
L = pcbnew.F_Cu if layer == "F.Cu" else pcbnew.B_Cu; n = 0
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T or t.GetNetname() != net or t.GetLayer() != L: continue
    for getter, setter in ((t.GetStart, t.SetStart), (t.GetEnd, t.SetEnd)):
        p = getter(); x, y = p.x / 1e6 - OX, OY - p.y / 1e6
        if (x - hx) ** 2 + (y - hy) ** 2 <= rad ** 2:
            setter(VECTOR2I(FromMM(OX + x + ax), FromMM(OY - (y + ay)))); n += 1
pcbnew.SaveBoard(sys.argv[1], b); print("moved %d endpoints of %s on %s by (%.2f, %.2f)" % (n, net, layer, ax, ay))
