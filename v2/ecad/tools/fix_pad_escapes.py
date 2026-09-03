#!/usr/bin/env python3
"""Close unconnected fine-pitch pads whose net already runs on another layer: re-create the escape the router ripped up.
For each unconnected item with a pad: a via along the pad's outward axis (offsets tried in turn), a top-layer stub from the pad to the via,
and a straight segment on the track's layer from the via to the nearest open end of the net's copper. Each attempt is kept only if a DRC run
shows no hard violation and one fewer unconnected item. Usage: fix_pad_escapes.py <board.kicad_pcb> <drc.json>"""
import sys, re, json, math, subprocess, os, pcbnew
from pcbnew import VECTOR2I, FromMM
BOARD, DRC = sys.argv[1], sys.argv[2]
HARD = ("clearance", "shorting_items", "tracks_crossing", "hole_clearance", "hole_to_hole", "copper_edge_clearance")
def drc(path):
    out = path + ".drc.json"; subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", out, path], capture_output=True)
    d = json.load(open(out)); hard = sum(1 for v in d["violations"] if v["type"] in HARD); return hard, len(d.get("unconnected_items", [])), d
b = pcbnew.LoadBoard(BOARD); d = json.load(open(DRC))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
def padof(desc):
    m = re.match(r"(?:PTH pad|Pad) (\S+) \[([^\]]+)\] of (\S+)", desc)
    if not m: return None
    fp = fps.get(m.group(3)); return next((p for p in fp.Pads() if p.GetNumber() == m.group(1)), None) if fp else None
hard0, unr0, _ = drc(BOARD); print("baseline: hard %d unrouted %d" % (hard0, unr0))
closed = 0
for v in d.get("unconnected_items", []):
    pads = [p for p in (padof(i.get("description", "")) for i in v.get("items", [])) if p]
    if not pads: continue
    pad = pads[0]; net = pad.GetNet(); c = pad.GetPosition(); fp = pad.GetParentFootprint(); fc = fp.GetPosition()
    dx, dy = c.x - fc.x, c.y - fc.y
    ax = (1 if dx > 0 else -1, 0) if abs(dx) > abs(dy) else (0, 1 if dy > 0 else -1)
    ends = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK" or t.GetNetCode() != net.GetNetCode(): continue
        ends += [(t.GetStart(), t.GetLayer()), (t.GetEnd(), t.GetLayer())]
    if not ends: print("  no copper at all for", net.GetNetname()); continue
    tgt, layer = min(ends, key=lambda e: math.hypot(e[0].x - c.x, e[0].y - c.y))
    print("  %s pad %s (%s): open end %.2f mm away on %s" % (fp.GetReference(), pad.GetNumber(), net.GetNetname(), math.hypot(tgt.x - c.x, tgt.y - c.y) / 1e6, b.GetLayerName(layer)))
    done = False
    for off in (1.4, 2.0, 2.6, 3.2, 3.8):
        vp = VECTOR2I(int(c.x + ax[0] * FromMM(off)), int(c.y + ax[1] * FromMM(off)))
        via = pcbnew.PCB_VIA(b); via.SetPosition(vp); via.SetDrill(FromMM(0.3)); via.SetWidth(FromMM(0.7)); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(net); b.Add(via)
        t1 = pcbnew.PCB_TRACK(b); t1.SetStart(c); t1.SetEnd(vp); t1.SetWidth(FromMM(0.2)); t1.SetLayer(pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu); t1.SetNet(net); b.Add(t1)
        t2 = pcbnew.PCB_TRACK(b); t2.SetStart(vp); t2.SetEnd(tgt); t2.SetWidth(FromMM(0.2)); t2.SetLayer(layer); t2.SetNet(net); b.Add(t2)
        tmp = BOARD + ".try.kicad_pcb"; pcbnew.SaveBoard(tmp, b); h, u, _ = drc(tmp)
        if h == 0 and u < unr0 - closed: print("    offset %.1f mm: hard 0, unrouted %d -> kept" % (off, u)); closed += 1; done = True; break
        print("    offset %.1f mm: hard %d unrouted %d -> undone" % (off, h, u))
        for x in (via, t1, t2): b.Remove(x)
    if not done: print("    could not close %s" % net.GetNetname())
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(BOARD, b)
h, u, _ = drc(BOARD); print("fix_pad_escapes: closed %d, final hard %d unrouted %d" % (closed, h, u))
for x in (BOARD + ".try.kicad_pcb", BOARD + ".try.kicad_pcb.drc.json", BOARD + ".drc.json", BOARD + ".try.kicad_pro"):
    if os.path.exists(x): os.remove(x)
