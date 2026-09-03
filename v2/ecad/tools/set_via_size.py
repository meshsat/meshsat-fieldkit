#!/usr/bin/env python3
"""Shrink a via at (x, y) KiCad mm (tolerance 0.03 mm) to the given diameter/drill. Usage: set_via_size.py <board> x y dia drill"""
import sys, pcbnew
from pcbnew import FromMM
b = pcbnew.LoadBoard(sys.argv[1]); x, y, dia, drill = map(float, sys.argv[2:6]); n = 0
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA" and abs(t.GetPosition().x - FromMM(x)) < FromMM(0.03) and abs(t.GetPosition().y - FromMM(y)) < FromMM(0.03):
        t.SetWidth(FromMM(dia)); t.SetDrill(FromMM(drill)); n += 1; print("  via %s at (%.3f, %.3f) -> %.2f/%.2f" % (t.GetNetname(), t.GetPosition().x / 1e6, t.GetPosition().y / 1e6, dia, drill))
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b); print("set_via_size: %d vias" % n)
