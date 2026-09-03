#!/usr/bin/env python3
"""Add a fanout via + short track for every SMD pad that the DRC reports unconnected on a plane net (GND, +5V).
Usage: fanout_vias.py <board.kicad_pcb> <drc.json> [reroute_nets...]  (nets listed get their tracks/vias deleted for re-routing)"""
import sys, re, json, math, pcbnew
from pcbnew import VECTOR2I, FromMM
BOARD, DRC = sys.argv[1], sys.argv[2]; REROUTE = sys.argv[3:]
b = pcbnew.LoadBoard(BOARD)
d = json.load(open(DRC))
targets = set()
for v in d.get("unconnected_items", []):
    for it in v.get("items", []):
        m = re.match(r"Pad (\S+) \[([^\]]+)\] of (\S+) on (F|B)\.Cu", it.get("description", ""))
        if m and m.group(2) in ("GND", "+5V"): targets.add((m.group(3), m.group(1), m.group(2)))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
added = 0
for ref, num, netname in sorted(targets):
    fp = fps.get(ref)
    if fp is None: continue
    pad = next((p for p in fp.Pads() if p.GetNumber() == num), None)
    if pad is None or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD: continue
    c = pad.GetPosition(); f = fp.GetPosition()
    dx, dy = c.x - f.x, c.y - f.y; n = math.hypot(dx, dy)
    if n < 1: dx, dy, n = 1.0, 0.0, 1.0
    ux, uy = dx / n, dy / n
    half = max(pad.GetSize().x, pad.GetSize().y) / 2
    off = half + FromMM(0.65)
    vpos = VECTOR2I(int(c.x + ux * off), int(c.y + uy * off))
    layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
    net = pad.GetNet()
    via = pcbnew.PCB_VIA(b); via.SetPosition(vpos); via.SetDrill(FromMM(0.4)); via.SetWidth(FromMM(0.8)); via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(net); b.Add(via)
    t = pcbnew.PCB_TRACK(b); t.SetStart(c); t.SetEnd(vpos); t.SetWidth(FromMM(0.4)); t.SetLayer(layer); t.SetNet(net); b.Add(t)
    added += 1
print("fanout vias added:", added, "of", len(targets), "targets")
removed = 0
for tr in list(b.GetTracks()):
    if tr.GetNetname() in REROUTE:
        b.Remove(tr); removed += 1
if REROUTE: print("removed %d track/via items on %s for re-routing" % (removed, REROUTE))
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(BOARD, b); print("saved")
