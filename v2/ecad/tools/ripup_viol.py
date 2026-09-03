#!/usr/bin/env python3
"""Rip up the track run behind a router clearance violation so stub_router.py can re-close it cleanly.
For each DRC 'clearance' item between two tracks of different nets on the same layer, the whole connected
run (same net, same layer, joined end to end) of the first item's net is removed. Usage: ripup_viol.py <board> <drc.json> [both]"""
import sys, json, re, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); d = json.load(open(sys.argv[2])); BOTH = len(sys.argv) > 3 and sys.argv[3] == "both"
TOL = 2000
def same(p, q): return abs(p.x - q.x) <= TOL and abs(p.y - q.y) <= TOL
def parse(desc):
    m = re.match(r"Track \[([^\]]+)\] on (\S+?),", desc); return (m.group(1), m.group(2)) if m else None
victims = []
for v in d.get("violations", []):
    if v["type"] != "clearance" or len(v.get("items", [])) != 2: continue
    a, c = (parse(i.get("description", "")) for i in v["items"])
    if not a or not c or a[0] == c[0] or a[1] != c[1]: continue
    for k, (net, layer) in enumerate((a, c)):
        if k == 1 and not BOTH: break
        pos = v["items"][k]["pos"]; p = pcbnew.VECTOR2I(pcbnew.FromMM(pos["x"]), pcbnew.FromMM(pos["y"]))
        cands = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK" and t.GetNetname() == net and b.GetLayerName(t.GetLayer()) == layer]
        if not cands: continue
        def dist(t):
            a0, e0 = t.GetStart(), t.GetEnd(); dx, dy = e0.x - a0.x, e0.y - a0.y; L2 = dx * dx + dy * dy
            u = 0 if L2 == 0 else max(0.0, min(1.0, ((p.x - a0.x) * dx + (p.y - a0.y) * dy) / L2))
            return ((a0.x + u * dx - p.x) ** 2 + (a0.y + u * dy - p.y) ** 2) ** 0.5
        seed = min(cands, key=dist); run = {id(seed): seed}; frontier = [seed]
        while frontier:
            t = frontier.pop()
            for u in cands:
                if id(u) in run: continue
                if any(same(x, y) for x in (t.GetStart(), t.GetEnd()) for y in (u.GetStart(), u.GetEnd())): run[id(u)] = u; frontier.append(u)
        victims.append((net, layer, list(run.values())))
seen = set(); n = 0
for net, layer, run in victims:
    for t in run:
        key = (t.GetNetname(), t.GetLayer(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y)
        if key in seen: continue
        seen.add(key); b.Remove(t); n += 1
    print("ripup: %s on %s, %d segments" % (net, layer, len(run)))
pcbnew.SaveBoard(sys.argv[1], b); print("ripup: %d segments removed" % n)
