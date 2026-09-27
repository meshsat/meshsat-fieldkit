#!/usr/bin/env python3
"""B4 post-route fixes on the routed board: drop the two sub-0.7 mm dangling GND stubs, tidy the silkscreen (mirrors gen_pcb_b.py)."""
import sys, pcbnew
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1]); OX, OY = 150.0, 110.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
# dangling = a track end that touches no other track end, via or pad; only remove such stubs shorter than 1 mm
tracks = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]; vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
ends = {}
for t in tracks:
    for pt in (t.GetStart(), t.GetEnd()): ends[(pt.x, pt.y)] = ends.get((pt.x, pt.y), 0) + 1
viapos = set((v.GetPosition().x, v.GetPosition().y) for v in vias)
pads = [p for fp in b.GetFootprints() for p in fp.Pads()]
def connected(pt, layer):
    if ends.get((pt.x, pt.y), 0) > 1 or (pt.x, pt.y) in viapos: return True
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
    if tx.startswith("MESHSAT FIELD KIT  -  CARRIER PCB-B"):
        d.SetText("PCB-B COMPUTE  REV A (B4)"); d.SetPosition(P(70, -79.0)); d.SetTextSize(VECTOR2I(FromMM(1.6), FromMM(1.6))); d.SetTextThickness(FromMM(0.26)); moved += 1
    elif tx.startswith("MESHSAT-709  |  245 x 170"):
        d.SetText("MESHSAT-709 | 245x170x1.6 4L | matte black | 2026-09-02"); d.SetPosition(P(70, -82.5)); d.SetTextSize(VECTOR2I(FromMM(1.1), FromMM(1.1))); d.SetTextThickness(FromMM(0.18)); moved += 1
    elif tx == "BACK WALL (+Y)":
        d.SetPosition(P(-55, 71.5)); d.SetTextSize(VECTOR2I(FromMM(1.2), FromMM(1.2))); moved += 1
    elif tx.startswith("J_DCF77: 3V3 GND"):
        d.SetText("DCF77: 3V3 GND T P1"); d.SetPosition(P(-66, 82.5)); d.SetTextSize(VECTOR2I(FromMM(0.9), FromMM(0.9))); moved += 1
    elif tx.startswith("J_GPIO1  Pi 40-pin ribbon"):
        d.SetText("Pi 40-pin ribbon"); d.SetPosition(P(-28, -32.5)); moved += 1
    elif tx == "J_TCALL1 pigtail":
        b.Remove(d); moved += 1
pcbnew.SaveBoard(sys.argv[1], b); print("post_fix_b4: removed %d dangling GND stubs, %d silk texts fixed" % (len(rm), moved))
