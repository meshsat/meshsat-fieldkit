#!/usr/bin/env python3
"""Close DRC-listed gaps with straight tracks, one at a time, keeping each only if a fresh kicad-cli DRC shows no new clearance/short/crossing.
Usage: gap_closer_checked.py <board> <drc.json>"""
import sys, re, json, math, subprocess, shutil, os, pcbnew
from pcbnew import VECTOR2I, FromMM
BOARD, DRC = sys.argv[1], sys.argv[2]
HARD = ("clearance", "shorting_items", "tracks_crossing", "hole_clearance", "copper_edge_clearance")
def run_drc(path):
    pro = os.path.splitext(BOARD)[0] + ".kicad_pro"; tpro = os.path.splitext(path)[0] + ".kicad_pro"
    if os.path.exists(pro) and not os.path.exists(tpro): shutil.copy(pro, tpro)   # kicad-cli reads the design rules from the project file next to the board
    out = path + ".drc.json"; subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", out, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    d = json.load(open(out)); os.remove(out)
    return sum(1 for v in d["violations"] if v["type"] in HARD), len(d.get("unconnected_items", []))
base_hard, base_unr = run_drc(BOARD); print("baseline: hard %d, unrouted %d" % (base_hard, base_unr))
d = json.load(open(DRC))
def item_of(b, it):
    desc = it.get("description", ""); pos = it.get("pos", {}); x, y = FromMM(pos.get("x", 0)), FromMM(pos.get("y", 0))
    m = re.match(r"(?:PTH pad|Pad) (\S+) \[([^\]]+)\] of (\S+) on (\S+)", desc)
    if m:
        fp = next((f for f in b.GetFootprints() if f.GetReference() == m.group(3)), None); pad = next((p for p in fp.Pads() if p.GetNumber() == m.group(1)), None) if fp else None
        return ("pad", pad, m.group(2), m.group(4).rstrip(","))
    m = re.match(r"Via \[([^\]]+)\]", desc)
    if m: return ("via", VECTOR2I(x, y), m.group(1), "*")
    m = re.match(r"Track \[([^\]]+)\] on (\S+)", desc)
    if m: return ("track", VECTOR2I(x, y), m.group(1), m.group(2).rstrip(","))
    return None
closed = 0
for v in d.get("unconnected_items", []):
    b = pcbnew.LoadBoard(BOARD); its = [item_of(b, i) for i in v.get("items", [])]
    if len(its) != 2 or not all(its): continue
    (ka, oa, na, la), (kb, ob, nb, lb) = its
    if ka != "pad": (ka, oa, na, la), (kb, ob, nb, lb) = (kb, ob, nb, lb), (ka, oa, na, la)
    if ka != "pad": print("  skip (no pad):", na); continue
    pad = oa; net = pad.GetNet(); layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu; c = pad.GetPosition()
    # target point: pad centre / via centre / nearest point of the closest same-net track on the pad's layer to the reported position
    if kb == "pad": t = ob.GetPosition(); tl = layer
    elif kb == "via": t = ob; tl = layer
    else:
        best = None
        for tr in b.GetTracks():
            if tr.GetClass() != "PCB_TRACK" or tr.GetNetname() != pad.GetNetname(): continue
            a, e = tr.GetStart(), tr.GetEnd(); dx, dy = e.x - a.x, e.y - a.y; L2 = dx * dx + dy * dy
            u = 0 if L2 == 0 else max(0, min(1, ((c.x - a.x) * dx + (c.y - a.y) * dy) / L2)); q = VECTOR2I(int(a.x + u * dx), int(a.y + u * dy))
            dist = math.hypot(q.x - c.x, q.y - c.y)
            if tr.GetLayer() == layer and (best is None or dist < best[0]): best = (dist, q, tr.GetLayer())
        if best is None or best[0] > FromMM(6.0): print("  skip: no nearby same-layer track for", na); continue
        t = best[1]; tl = best[2]
    w = FromMM(0.2 if min(pad.GetSize().x, pad.GetSize().y) < FromMM(0.4) else 0.25)
    tr = pcbnew.PCB_TRACK(b); tr.SetStart(c); tr.SetEnd(t); tr.SetWidth(w); tr.SetLayer(layer); tr.SetNet(net); b.Add(tr)
    tmp = BOARD + ".try.kicad_pcb"; pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(tmp, b)
    hard, unr = run_drc(tmp)
    tpro = os.path.splitext(tmp)[0] + ".kicad_pro"
    if os.path.exists(tpro): os.remove(tpro)
    if hard <= base_hard and unr < base_unr:
        shutil.move(tmp, BOARD); base_hard, base_unr = hard, unr; closed += 1; print("  closed %s (%.2f mm): hard %d, unrouted %d" % (na, math.hypot(t.x - c.x, t.y - c.y) / 1e6, hard, unr))
    else:
        os.remove(tmp); print("  rejected %s: hard %d (was %d), unrouted %d (was %d)" % (na, hard, base_hard, unr, base_unr))
print("gap_closer_checked: closed %d, final hard %d, unrouted %d" % (closed, base_hard, base_unr))
