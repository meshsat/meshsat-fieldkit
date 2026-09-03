#!/usr/bin/env python3
"""PCB-D post-route: silkscreen tidy on the routed board (mirrors gen_pcb_d.py) and removal of sub-1 mm dangling stubs."""
import sys, pcbnew
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1]); OX, OY = 100.0, 100.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
tracks = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]; vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
ends = {}
for t in tracks:
    for pt in (t.GetStart(), t.GetEnd()): ends[(pt.x, pt.y)] = ends.get((pt.x, pt.y), 0) + 1
pads = [p for fp in b.GetFootprints() for p in fp.Pads()]
def connected(pt, layer):
    if ends.get((pt.x, pt.y), 0) > 1: return True
    for v in vias:
        if abs(v.GetPosition().x - pt.x) < FromMM(0.45) and abs(v.GetPosition().y - pt.y) < FromMM(0.45): return True
    for p in pads:
        if p.IsOnLayer(layer) and p.HitTest(pt): return True
    return False
rm = [t for t in tracks if t.GetLength() < FromMM(1.0) and (not connected(t.GetStart(), t.GetLayer()) or not connected(t.GetEnd(), t.GetLayer()))]
for t in rm: b.Remove(t)
moved = 0
for d in list(b.GetDrawings()):
    if d.GetClass() != "PCB_TEXT": continue
    tx = d.GetText()
    if tx == "J_HARN1 to PCB-A J_MEZZ1":
        d.SetLayer(pcbnew.B_SilkS); d.SetMirrored(True); d.SetTextAngleDegrees(0); d.SetPosition(P(-33, 22.5)); moved += 1
    elif tx == "J_PWR1 CELL+ GND":
        d.SetLayer(pcbnew.B_SilkS); d.SetMirrored(True); d.SetTextAngleDegrees(0); d.SetPosition(P(-33, -20.5)); moved += 1
    elif tx.startswith("MESHSAT PCB-D APRS BOARD  REV A"):
        d.SetText("PCB-D APRS BOARD REV A | MESHSAT-709/748 | 2026-09-02"); d.SetPosition(P(10, -1.5)); d.SetTextSize(VECTOR2I(FromMM(1.0), FromMM(1.0))); moved += 1
    elif tx.startswith("UNDERSIDE, faces PCB-A"):
        d.SetText("underside faces PCB-A: jumpers + test points"); d.SetPosition(P(10, -5.0)); d.SetTextSize(VECTOR2I(FromMM(0.85), FromMM(0.85))); moved += 1
pcbnew.SaveBoard(sys.argv[1], b); print("post_fix_d: removed %d dangling stubs, %d silk texts fixed" % (len(rm), moved))
