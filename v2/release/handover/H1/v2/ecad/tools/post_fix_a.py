#!/usr/bin/env python3
"""PCB-A post-route clean-up on the routed board (each step guarded, board always saved)."""
import sys, re, json, math, pcbnew
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1]); d = json.load(open(sys.argv[2])); OX, OY = 150.0, 110.0
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
try:
    for fp in b.GetFootprints():
        if fp.GetReference() in ("J_MEZZ_PWR1", "U13", "U14", "U15", "U16", "U17", "U18"): fp.Reference().SetVisible(False)
    print("reference hidden")
except Exception as e: print("note: hide ref:", e)
try:
    mode = getattr(pcbnew, "ISLAND_REMOVAL_MODE_ALWAYS", None); n = 0
    for z in b.Zones():
        if z.GetIsRuleArea(): continue
        z.SetIslandRemovalMode(getattr(pcbnew, "ISLAND_REMOVAL_MODE_ALWAYS", 0))
        n += 1
    print("island removal set on %d zones (mode %s)" % (n, mode))
except Exception as e: print("note: islands:", e)
def padof(desc):
    m = re.match(r"(?:PTH pad|Pad) (\S+) \[([^\]]+)\] of (\S+)", desc)
    if not m: return None
    fp = fps.get(m.group(3)); return next((p for p in fp.Pads() if p.GetNumber() == m.group(1)), None) if fp else None
closed = 0
import os
try:
    for v in ([] if os.environ.get("NO_GAPS") else d.get("unconnected_items", [])):
        items = [i.get("description", "") for i in v.get("items", [])]
        pads = [p for p in (padof(x) for x in items) if p]
        if not pads: continue
        pad = pads[0]; c = pad.GetPosition(); best = None
        def nearest_on(t):
            a, e = t.GetStart(), t.GetEnd(); dx, dy = e.x - a.x, e.y - a.y; L2 = dx * dx + dy * dy
            if L2 == 0: return a
            u = max(0.0, min(1.0, ((c.x - a.x) * dx + (c.y - a.y) * dy) / L2)); return VECTOR2I(int(a.x + u * dx), int(a.y + u * dy))
        for t in b.GetTracks():
            if t.GetNetname() != pad.GetNetname(): continue
            if t.GetClass() == "PCB_VIA": e = t.GetPosition()
            elif t.GetLength() >= FromMM(0.05): e = nearest_on(t)
            else: continue
            dist = math.hypot(e.x - c.x, e.y - c.y)
            if dist < FromMM(2.5) and (best is None or dist < best[0]): best = (dist, e, t)
        if best is None: print("  no nearby copper for", pad.GetParentFootprint().GetReference(), pad.GetNumber()); continue
        dist, e, t = best
        padlayer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
        if t.GetClass() != "PCB_VIA" and t.GetLayer() != padlayer:
            via = pcbnew.PCB_VIA(b); via.SetPosition(e); via.SetDrill(FromMM(0.3)); via.SetWidth(FromMM(0.7)); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); b.Add(via)
        nt = pcbnew.PCB_TRACK(b); nt.SetStart(e); nt.SetEnd(c); nt.SetWidth(FromMM(0.3)); nt.SetLayer(padlayer); nt.SetNet(pad.GetNet()); b.Add(nt); closed += 1
        print("  closed %s pad %s (%s), %.2f mm" % (pad.GetParentFootprint().GetReference(), pad.GetNumber(), pad.GetNetname(), dist / 1e6))
except Exception as e: print("note: gaps:", e)
print("gaps closed:", closed)
try:
    rm = 0
    for dr in list(b.GetDrawings()):
        if dr.GetLayer() == pcbnew.F_SilkS and dr.GetClass() == "PCB_SHAPE":
            bb = dr.GetBoundingBox(); cx = (bb.GetLeft() + bb.GetRight()) / 2e6 - OX; cy = OY - (bb.GetTop() + bb.GetBottom()) / 2e6
            if -14 < cx < -2 and -23 < cy < -13: b.Remove(dr); rm += 1
    print("silk segments removed:", rm)
except Exception as e: print("note: silk:", e)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b); print("saved")
