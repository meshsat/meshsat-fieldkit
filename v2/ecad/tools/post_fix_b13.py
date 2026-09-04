#!/usr/bin/env python3
"""B13 post-route fixes: the B4 tidy-up (sub-1 mm dangling stubs, silk texts) plus a zone refill at the end, so the DRC that follows
sees the planes as they will be exported (a stale fill reported every new via as a plane clearance violation on 5 Sep 2026)."""
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
def on_track(pt, layer, net, me):
    """The point lies on the middle of another same-net track of the layer (a T-junction; 5 Sep: the 0.42 mm 5V_RTL branch foot was cut off as a stub)."""
    for t in tracks:
        if t is me or t.GetLayer() != layer or t.GetNetCode() != net: continue
        a, e = t.GetStart(), t.GetEnd(); dx, dy = e.x - a.x, e.y - a.y; L2 = dx * dx + dy * dy
        if L2 == 0: continue
        u = max(0.0, min(1.0, ((pt.x - a.x) * dx + (pt.y - a.y) * dy) / L2))
        if ((a.x + u * dx - pt.x) ** 2 + (a.y + u * dy - pt.y) ** 2) ** 0.5 <= t.GetWidth() / 2: return True
    return False
def connected(pt, layer, net=None, me=None):
    if ends.get((pt.x, pt.y), 0) > 1 or (pt.x, pt.y) in viapos: return True
    for v in vias:
        if abs(v.GetPosition().x - pt.x) < FromMM(0.45) and abs(v.GetPosition().y - pt.y) < FromMM(0.45): return True
    for p in pads:
        if p.IsOnLayer(layer) and p.HitTest(pt): return True
    if net is not None and on_track(pt, layer, net, me): return True
    return False
rm = [t for t in tracks if t.GetLength() < FromMM(1.0) and (not connected(t.GetStart(), t.GetLayer(), t.GetNetCode(), t) or not connected(t.GetEnd(), t.GetLayer(), t.GetNetCode(), t))]
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
joins = 0   # 5 Sep 01:10: no hand joins any more; the stub router closes SDA (hole-to-hole rule added) and the cleanup keeps the 5V_RTL T-junction
pcbnew.SaveBoard(sys.argv[1], b); b = pcbnew.LoadBoard(sys.argv[1]); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)   # refill the planes around whatever changed before the DRC
print("post_fix_b13: removed %d dangling stubs, %d silk texts fixed, %d joins added, zones refilled" % (len(rm), moved, joins))
