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
victims = {}; causes = {}
for v in d["violations"]:
    if v["type"] not in HARD: continue
    items = v.get("items", [])
    hits = [(i, t) for i in items for t in at(i["pos"]) if i.get("description", "").startswith(("Track", "Via"))]
    if not hits: continue
    # drop the escape of the item listed second (the DRC lists the pair; one pruned pad frees the other)
    # Prune the ESCAPE, never the pre-routed pair. Both are locked, so "locked" cannot tell them apart; length can. An escape piece is a
    # stub of a millimetre or two from a pad to its via, a pre-routed differential leg is tens of millimetres, and on B17 this tool was
    # deleting 34 mm pair legs that the pair pre-router had just laid to a controlled geometry (9 Sep 2026 01:00, MESHSAT-862). Among the
    # locked items the DRC names, take the shortest; a via counts as a short piece because it is one.
    def _len(tr):
        return 0.3 if tr.GetClass() == "PCB_VIA" else math.hypot(tr.GetStart().x - tr.GetEnd().x, tr.GetStart().y - tr.GetEnd().y) / 1e6
    i, t = min(hits, key=lambda h: _len(h[1]))
    # 8 Sep 2026 (MESHSAT-862): record WHY, not only what. 118 of B17's pads lost their escape with nothing in the log to say what they
    # collided with, so the placement could not be corrected. The counterparty is the other item of the DRC pair.
    other = next((o for o in items if o is not i), None)
    victims[id(t)] = t; causes[id(t)] = (v["type"], (other or {}).get("description", "?")[:70])
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
    ty, oth = causes.get(id(t), ("?", "?"))
    pruned.append((t.GetNetname(), found[0] if found else "?", found[1].GetNumber() if found else "?", t.GetPosition().x / 1e6, t.GetPosition().y / 1e6, ty, oth))
    for o in pieces:
        if id(o) not in removed: removed.add(id(o)); b.Remove(o)
pcbnew.SaveBoard(sys.argv[1], b)
import os
out = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "out", os.path.splitext(os.path.basename(sys.argv[1]))[0] + "-pruned.txt")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as fh:
    fh.write("# net\tref\tpad\tx\ty\tviolation\twhat it collided with (pruned_gate.py requires the router to reach these pads)\n")
    for net, ref, num, x, y, ty, oth in pruned: fh.write("%s\t%s\t%s\t%.3f\t%.3f\t%s\t%s\n" % (net, ref, num, x, y, ty, oth))
print("escape_prune: %d escape pieces removed for %d pads (%s); pruned pads: %s" % (len(removed), len(victims), out, ", ".join("%s.%s" % (r, n) for _, r, n, _, _, _, _ in pruned)))
import collections
_c = collections.Counter("%s vs %s" % (ty, oth.split("[")[0].strip()) for _, _, _, _, _, ty, oth in pruned)
for _k, _n in _c.most_common(8): print("escape_prune:   %4d  %s" % (_n, _k))
