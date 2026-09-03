#!/usr/bin/env python3
"""Give named SMD pads on a plane net a via: try positions along the pad's outward axis with a small via, checking clearance geometrically.
Usage: fix_gnd_pads.py <board> <REF:pad,REF:pad,...> [net]"""
import sys, math, pcbnew
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1]); targets = [t.split(":") for t in sys.argv[2].split(",")]; NET = sys.argv[3] if len(sys.argv) > 3 else "GND"
VIA_D, VIA_DR, TW, CLR = FromMM(0.6), FromMM(0.3), FromMM(0.25), FromMM(0.2)
pads = [(p, p.GetPosition(), max(p.GetSize().x, p.GetSize().y) / 2, p.GetNetname()) for fp in b.GetFootprints() for p in fp.Pads()]
vias = [(v.GetPosition(), v.GetWidth() / 2, v.GetNetname()) for v in b.GetTracks() if v.GetClass() == "PCB_VIA"]
tracks = [(t.GetStart(), t.GetEnd(), t.GetWidth() / 2, t.GetLayer(), t.GetNetname()) for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]
edges = b.GetBoardEdgesBoundingBox()
def seg_dist(p, a, c):
    ax, ay, cx, cy, px, py = a.x, a.y, c.x, c.y, p.x, p.y
    dx, dy = cx - ax, cy - ay; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
def clear(pt, r, layer, me):
    if not (edges.GetLeft() + FromMM(1.0) < pt.x < edges.GetRight() - FromMM(1.0) and edges.GetTop() + FromMM(1.0) < pt.y < edges.GetBottom() - FromMM(1.0)): return False
    for p, pp, pr, net in pads:
        if p is me or (pp.x == me.GetPosition().x and pp.y == me.GetPosition().y): continue
        if net == NET and layer is None: continue
        if math.hypot(pt.x - pp.x, pt.y - pp.y) < pr + r + CLR: return False
    for vp, vr, net in vias:
        if math.hypot(pt.x - vp.x, pt.y - vp.y) < vr + r + CLR: return False
    for s, e, tr, tl, net in tracks:
        if layer is not None and tl != layer: continue
        if seg_dist(pt, s, e) < tr + r + CLR: return False
    return True
done = 0
for ref, num in targets:
    fp = next(f for f in b.GetFootprints() if f.GetReference() == ref); pad = next(p for p in fp.Pads() if p.GetNumber() == num)
    c = pad.GetPosition(); fc = fp.GetPosition(); sx, sy = pad.GetSize().x, pad.GetSize().y
    th = math.radians(pad.GetOrientationDegrees()); L = (math.cos(th), -math.sin(th)) if sx >= sy else (math.sin(th), math.cos(th))
    u = (c.x - fc.x, c.y - fc.y)
    if L[0] * u[0] + L[1] * u[1] < 0: L = (-L[0], -L[1])
    layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu; half = max(sx, sy) / 2; ok = False
    for off in [half + FromMM(d / 100.0) for d in range(60, 320, 15)]:
        for side in (0, 0.35, -0.35, 0.7, -0.7):
            v = VECTOR2I(int(c.x + L[0] * off - L[1] * side * FromMM(1)), int(c.y + L[1] * off + L[0] * side * FromMM(1)))
            samples = [VECTOR2I(int(c.x + (v.x - c.x) * k / 8.0), int(c.y + (v.y - c.y) * k / 8.0)) for k in range(2, 9)]
            if clear(v, VIA_D / 2, None, pad) and all(clear(pt, TW / 2, layer, pad) for pt in samples) and all(clear(pt, TW / 2, None, pad) for pt in samples[-2:]):
                via = pcbnew.PCB_VIA(b); via.SetPosition(v); via.SetDrill(VIA_DR); via.SetWidth(VIA_D); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); b.Add(via)
                t = pcbnew.PCB_TRACK(b); t.SetStart(c); t.SetEnd(v); t.SetWidth(TW); t.SetLayer(layer); t.SetNet(pad.GetNet()); b.Add(t)
                vias.append((v, VIA_D / 2, NET)); tracks.append((c, v, TW / 2, layer, NET)); ok = True; done += 1; break
        if ok: break
    print("  %s pad %s: %s" % (ref, num, "via added" if ok else "NO ROOM"))
f = pcbnew.ZONE_FILLER(b); f.Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b); print("fix_gnd_pads: %d/%d" % (done, len(targets)))
