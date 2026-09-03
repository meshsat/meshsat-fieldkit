#!/usr/bin/env python3
"""Move a via (KiCad mm coords) by dx,dy and drag every track end that sat on it. Usage: nudge_via.py <board> x y dx dy"""
import sys, pcbnew
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1]); x, y, dx, dy = map(float, sys.argv[2:6])
old = VECTOR2I(FromMM(x), FromMM(y)); new = VECTOR2I(FromMM(x + dx), FromMM(y + dy)); moved = 0
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA" and abs(t.GetPosition().x - old.x) < 5000 and abs(t.GetPosition().y - old.y) < 5000:
        t.SetPosition(new); old = VECTOR2I(t.GetPosition().x - (new.x - old.x), t.GetPosition().y - (new.y - old.y)); moved += 1
for t in b.GetTracks():
    if t.GetClass() != "PCB_TRACK": continue
    if abs(t.GetStart().x - old.x) < 5000 and abs(t.GetStart().y - old.y) < 5000: t.SetStart(new); moved += 1
    if abs(t.GetEnd().x - old.x) < 5000 and abs(t.GetEnd().y - old.y) < 5000: t.SetEnd(new); moved += 1
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b); print("nudge_via: %d items moved" % moved)
