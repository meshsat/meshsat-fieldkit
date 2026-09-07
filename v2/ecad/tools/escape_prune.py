#!/usr/bin/env python3
"""Remove the locked escape pieces (stubs, knees, vias) that a pre-route DRC finds in a hard violation, so the router fans those pads itself.
Usage: escape_prune.py <board.kicad_pcb> <drc.json>
B16 (7 Sep 2026): the M.2 B-key socket's escapes for two SIM pins crossed each other after every geometric guard in escape.py; two pads out of
1285 escapes are the router's job. A pruned pad's stub goes with its via, so nothing locked dangles."""
import sys, json, math, pcbnew
HARD = ("clearance", "shorting_items", "hole_clearance", "hole_to_hole", "tracks_crossing")
b = pcbnew.LoadBoard(sys.argv[1]); d = json.load(open(sys.argv[2]))
locked = [t for t in b.GetTracks() if t.IsLocked()]
def at(pos):
    x, y = pos["x"] * 1e6, pos["y"] * 1e6
    return [t for t in locked if math.hypot(t.GetPosition().x - x, t.GetPosition().y - y) < 60000 or (t.GetClass() == "PCB_TRACK" and (math.hypot(t.GetStart().x - x, t.GetStart().y - y) < 60000 or math.hypot(t.GetEnd().x - x, t.GetEnd().y - y) < 60000))]
victims = {}
for v in d["violations"]:
    if v["type"] not in HARD: continue
    items = v.get("items", [])
    hits = [(i, t) for i in items for t in at(i["pos"]) if i.get("description", "").startswith(("Track", "Via"))]
    if not hits: continue
    # drop the escape of the item listed second (the DRC lists the pair; one pruned pad frees the other)
    i, t = hits[-1]
    victims[id(t)] = t
if not victims: print("escape_prune: nothing to prune"); sys.exit(0)
# take the whole escape of each victim's pad: every locked same-net piece chained to it within 4 mm
removed = set()
def chain(t):
    out = {id(t): t}; frontier = [t]
    while frontier:
        cur = frontier.pop(); ends = [cur.GetPosition()] if cur.GetClass() == "PCB_VIA" else [cur.GetStart(), cur.GetEnd()]
        for o in locked:
            if id(o) in out or o.GetNetname() != cur.GetNetname(): continue
            oends = [o.GetPosition()] if o.GetClass() == "PCB_VIA" else [o.GetStart(), o.GetEnd()]
            if any(math.hypot(e.x - f.x, e.y - f.y) < 20000 for e in ends for f in oends): out[id(o)] = o; frontier.append(o)
    return out.values()
for t in victims.values():
    for o in chain(t):
        if id(o) not in removed: removed.add(id(o)); b.Remove(o)
pcbnew.SaveBoard(sys.argv[1], b)
print("escape_prune: %d escape pieces removed for %d pads" % (len(removed), len(victims)))
