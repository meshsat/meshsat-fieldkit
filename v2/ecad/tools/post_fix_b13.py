#!/usr/bin/env python3
"""B13 post-route fixes: the B4 tidy-up (sub-1 mm dangling stubs, silk texts) plus two joins the router left open on the first B13 route
(5 Sep 2026): the 5V_RTL branch end 0.42 mm short of its trunk near the SDR channel, and U20 pin 23 (SDA) to the SDA via of U21 pin 23
over In1 east of the two expanders (the stub router's 294-cell detour crossed two clearances). Coordinates in KiCad board units (OX 150, OY 110)."""
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
def K(x, y): return VECTOR2I(FromMM(x), FromMM(y))          # absolute KiCad coordinates (as in the DRC report)
def track(net, layer, a, c, w):
    t = pcbnew.PCB_TRACK(b); t.SetStart(K(*a)); t.SetEnd(K(*c)); t.SetWidth(FromMM(w)); t.SetLayer(layer); t.SetNet(b.FindNet(net)); b.Add(t); return t
def via(net, x, y, d=0.45, dr=0.25):
    v = pcbnew.PCB_VIA(b); v.SetPosition(K(x, y)); v.SetWidth(FromMM(d)); v.SetDrill(FromMM(dr)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(b.FindNet(net)); b.Add(v); return v
joins = 0
if b.FindNet("/5V_RTL") and b.FindNet("/SDA"):
    # 1. 5V_RTL: the branch (137.46, 93.92)-(136.32, 95.82)-... ends 0.42 mm north of the F.Cu trunk at y 93.50
    track("/5V_RTL", pcbnew.F_Cu, (137.46, 93.92), (137.46, 93.50), 0.25); joins += 1
    # 2. SDA: U20 pin 23 (39.81, 141.85) east on F.Cu past the neighbours' escape vias to a via at (43.10, 141.85), In1 south at x 43.10 (clear of
    #    the UART0_TX via at 43.78 and the +3V3 In1 end at 42.63), under the +3V3 via at (42.15, 152.70), up to the SDA via at (42.15, 151.40)
    track("/SDA", pcbnew.F_Cu, (39.81, 141.85), (43.10, 141.85), 0.2); via("/SDA", 43.10, 141.85)
    track("/SDA", pcbnew.In1_Cu, (43.10, 141.85), (43.10, 152.00), 0.2); track("/SDA", pcbnew.In1_Cu, (43.10, 152.00), (42.15, 152.00), 0.2); track("/SDA", pcbnew.In1_Cu, (42.15, 152.00), (42.15, 151.40), 0.2); joins += 1
pcbnew.SaveBoard(sys.argv[1], b); print("post_fix_b13: removed %d dangling stubs, %d silk texts fixed, %d joins added" % (len(rm), moved, joins))
