#!/usr/bin/env python3
"""Close pad-to-track near misses the router left (track ends within ~1.5 mm of its pad): add a via if the
layers differ, then a short track into the pad. Usage: finish_stubs.py <board> <drc.json>"""
import sys, re, json, math, pcbnew
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1]); d = json.load(open(sys.argv[2]))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
if len(d.get("unconnected_items", [])) > 20:
    print("finish_stubs: board is not routed (%d unconnected), nothing done" % len(d.get("unconnected_items", []))); sys.exit(0)
allpads = [(q.GetPosition(), max(q.GetSize().x, q.GetSize().y) / 2, q.GetNetname()) for fp in b.GetFootprints() for q in fp.Pads()]
def path_clear(a, bpt, net):
    for k in range(1, 6):
        x = a.x + (bpt.x - a.x) * k / 6; y = a.y + (bpt.y - a.y) * k / 6
        for qp, qr, qn in allpads:
            if qn != net and math.hypot(x - qp.x, y - qp.y) < qr + FromMM(0.35): return False
    return True
LAYER = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu}
fixed = 0
for v in d.get("unconnected_items", []):
    items = v.get("items", [])
    pad = None; trk = None
    for it in items:
        m = re.match(r"(?:PTH pad|Pad) (\S+) \[([^\]]+)\] of (\S+)", it.get("description", ""))
        if m and pad is None:
            fp = fps.get(m.group(3)); p = next((x for x in fp.Pads() if x.GetNumber() == m.group(1)), None) if fp else None
            if p: pad = p
        m2 = re.match(r"Track \[([^\]]+)\] on (\S+)", it.get("description", ""))
        if m2: trk = (m2.group(2), it.get("pos", {}))
    if pad is None or trk is None: continue
    layer_name, pos = trk
    c = pad.GetPosition(); tp = VECTOR2I(int(pos["x"] * 1e6), int(pos["y"] * 1e6))
    # find the actual track object nearest to that position with the pad's net
    best = None
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK" or t.GetNetname() != pad.GetNetname(): continue
        for e in (t.GetStart(), t.GetEnd()):
            dist = math.hypot(e.x - c.x, e.y - c.y)
            if dist < FromMM(3.5) and (best is None or dist < best[0]): best = (dist, e, t)
    if best is None: continue
    dist, e, t = best
    if dist > FromMM(1.6) or (dist > FromMM(0.9) and not path_clear(e, c, pad.GetNetname())): print("  skip %s pad %s: path not clear" % (pad.GetParentFootprint().GetReference(), pad.GetNumber())); continue
    padlayer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else (pcbnew.B_Cu if pad.IsOnLayer(pcbnew.B_Cu) else None)
    if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH: padlayer = t.GetLayer()
    if padlayer is None: continue
    if t.GetLayer() != padlayer:
        via = pcbnew.PCB_VIA(b); via.SetPosition(e); via.SetDrill(FromMM(0.3)); via.SetWidth(FromMM(0.7)); via.SetViaType(pcbnew.VIATYPE_THROUGH)
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); b.Add(via)
    nt = pcbnew.PCB_TRACK(b); nt.SetStart(e); nt.SetEnd(c); nt.SetWidth(t.GetWidth()); nt.SetLayer(padlayer); nt.SetNet(pad.GetNet()); b.Add(nt)
    fixed += 1; print("  closed %s pad %s (%s) from a %s track %.2f mm away" % (fps and pad.GetParentFootprint().GetReference(), pad.GetNumber(), pad.GetNetname(), layer_name, dist / 1e6))
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b); print("finish_stubs: %d closed" % fixed)
