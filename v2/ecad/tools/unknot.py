#!/usr/bin/env python3
"""unknot.py <board.kicad_pcb> <drc.json> [radius mm]

Removes the router's knots (7 Sep 2026, A22 runs 8 and 10): Freerouting 1.9.0 leaves a tangle where two nets' tracks overlap at one spot near a
fine-pitch escape column (20 to 25 shorting_items within a millimetre, a different spot every run; the pre-route board is clean). Every unlocked
track named by a shorting_items or tracks_crossing item goes, plus every unlocked track of the same nets whose end lies within `radius`
(default 1.5 mm) of the violation; the opens this creates are closed by the stub router afterwards (the finish re-runs the DRC in between).
Prints 'unknot: N tracks removed at K spots (nets ...)'."""
import sys, json, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); d = json.load(open(sys.argv[2])); R = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
by_uuid = {t.m_Uuid.AsString(): t for t in b.GetTracks()}
spots, victims, names = [], set(), set()
for v in d.get("violations", []):
    if v["type"] not in ("shorting_items", "tracks_crossing"): continue
    nets = set()
    for it in v.get("items", []):
        t = by_uuid.get(it.get("uuid", ""))
        if t is None or t.GetClass() != "PCB_TRACK" or t.IsLocked(): continue
        victims.add(t.m_Uuid.AsString()); nets.add(t.GetNetCode()); names.add(t.GetNetname())
    if nets: spots.append((v["items"][0]["pos"]["x"], v["items"][0]["pos"]["y"], nets))
for t in b.GetTracks():
    if t.GetClass() != "PCB_TRACK" or t.IsLocked(): continue
    u = t.m_Uuid.AsString()
    if u in victims: continue
    for x, y, nets in spots:
        if t.GetNetCode() not in nets: continue
        if any(abs(p.x / 1e6 - x) <= R and abs(p.y / 1e6 - y) <= R for p in (t.GetStart(), t.GetEnd())): victims.add(u); break
n = 0
for u in victims:
    t = by_uuid.get(u)
    if t is not None: b.Remove(t); n += 1
if n: b.Save(sys.argv[1])
print("unknot: %d tracks removed at %d spots (nets %s)" % (n, len({(round(x), round(y)) for x, y, _ in spots}), ", ".join(sorted(names)) or "none"))
