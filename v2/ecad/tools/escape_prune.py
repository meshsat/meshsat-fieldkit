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
if not victims:
    import os
    _out = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "out", os.path.splitext(os.path.basename(sys.argv[1]))[0] + "-pruned.txt"); os.makedirs(os.path.dirname(_out), exist_ok=True); open(_out, "w").write("# none pruned\n")
    print("escape_prune: nothing to prune (0 pads; %s)" % _out); sys.exit(0)
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
pruned = []   # 8 Sep 2026 (MESHSAT-862): the pad each pruned escape belonged to, for pruned_gate.py after the route
pads = [(f.GetReference(), p) for f in b.GetFootprints() for p in f.Pads()]
for t in victims.values():
    pieces = list(chain(t)); found = None
    for o in pieces:
        ends = [o.GetPosition()] if o.GetClass() == "PCB_VIA" else [o.GetStart(), o.GetEnd()]
        for ref, p in pads:
            if p.GetNetname() == o.GetNetname() and any(p.GetBoundingBox().Contains(e) for e in ends): found = (ref, p); break
        if found: break
    pruned.append((t.GetNetname(), found[0] if found else "?", found[1].GetNumber() if found else "?", t.GetPosition().x / 1e6, t.GetPosition().y / 1e6))
    for o in pieces:
        if id(o) not in removed: removed.add(id(o)); b.Remove(o)
pcbnew.SaveBoard(sys.argv[1], b)
import os
out = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "out", os.path.splitext(os.path.basename(sys.argv[1]))[0] + "-pruned.txt")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as fh:
    fh.write("# net\tref\tpad\tx\ty (pads whose escape was pruned; pruned_gate.py requires the router to reach them)\n")
    for net, ref, num, x, y in pruned: fh.write("%s\t%s\t%s\t%.3f\t%.3f\n" % (net, ref, num, x, y))
print("escape_prune: %d escape pieces removed for %d pads (%s); pruned pads: %s" % (len(removed), len(victims), out, ", ".join("%s.%s" % (r, n) for _, r, n, _, _ in pruned)))
