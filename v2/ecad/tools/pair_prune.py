#!/usr/bin/env python3
"""Take a pre-routed pair the DRC refuses off the board, whole, before anything else is laid on it.

15 September 2026 (MESHSAT-862). B19's first route for a deliverable never started: the pre-route DRC on the pair copper
read 64 hard of the fifteen types, every one of them laid by the pair pre-router (the placed board reads 0), and a board
that carries locked copper the finish will refuse is a route to a refused board six hours later. Three of the causes were
fixed at their source the same night (the inner gap cushion, the via-in-pad site check, `pair_preroute.py`); this tool is
the floor under whatever the pre-router still gets wrong: two pairs crossing on In3 (ETH1_P2 across SWP2_B, laid 121 mm
earlier), a leg entering U209 across the neighbouring pad of its own pair, a hop via 0.09 mm from the partner's leg.

The rule: a hard violation (hardset's set, its exemptions honoured) that names a locked piece belonging to a laid pair marks
that pair, and a marked pair loses ALL of its laid copper on BOTH nets, so the router lays it uncoupled and the impedance
judge measures the router's version against the declared fraction. Never a piece: a pair with one leg removed is a pair the
judge reads as coupled where it is not (escape_prune's own note of 9 Sep 2026 on B17). What tells a laid pair's piece from
an escape stub on the same net is the CHAIN it belongs to: the pre-router's legs are tens of millimetres of locked copper
joined end to end, an escape is a stub of a millimetre or two to its via, so a locked chain over ESCAPE_MM is pair copper
and a shorter one is left to escape_prune, which runs after the fanout and takes the escape.

Exit 0 when nothing was pruned, 2 when something was (full.sh holds a board that declares no coupled fraction on it)."""
import sys, os, json, math, pcbnew, hardset

ESCAPE_MM = 5.0
HARD = hardset.HARD_PRE

b = pcbnew.LoadBoard(sys.argv[1]); d = json.load(open(sys.argv[2]))
stem = os.path.splitext(os.path.basename(sys.argv[1]))[0]
out = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "out", stem + "-pair-pruned.txt")
os.makedirs(os.path.dirname(out), exist_ok=True)


def base_of(net):
    n = net.lstrip("/")
    return n[:-2] if n.endswith(("_P", "_N")) else None


def other_of(net):
    return net[:-1] + ("N" if net.endswith("P") else "P")


locked = [t for t in b.GetTracks() if t.IsLocked() and base_of(t.GetNetname())]


def ends(t):
    if t.GetClass() == "PCB_VIA": return [(t.GetPosition().x, t.GetPosition().y)]
    return [(t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)]


# the locked chains per net: union by shared end points (a via's centre is an end point on every layer)
parent = {}
def find(i):
    while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
    return i
by_pt = {}
for i, t in enumerate(locked):
    parent[i] = i
    for x, y in ends(t):
        key = (t.GetNetname(), round(x / 1000), round(y / 1000))   # 1 um bins
        if key in by_pt: parent[find(i)] = find(by_pt[key])
        else: by_pt[key] = i
chain_len = {}
for i, t in enumerate(locked):
    r = find(i)
    L = 0.0 if t.GetClass() == "PCB_VIA" else math.hypot(t.GetStart().x - t.GetEnd().x, t.GetStart().y - t.GetEnd().y) / 1e6
    chain_len[r] = chain_len.get(r, 0.0) + L


def at(pos):
    x, y = pos["x"] * 1e6, pos["y"] * 1e6
    hits = []
    for i, t in enumerate(locked):
        if math.hypot(t.GetPosition().x - x, t.GetPosition().y - y) < 60000: hits.append(i)
        elif t.GetClass() == "PCB_TRACK" and (math.hypot(t.GetStart().x - x, t.GetStart().y - y) < 60000 or math.hypot(t.GetEnd().x - x, t.GetEnd().y - y) < 60000): hits.append(i)
    return hits


marked = {}
for v in d.get("violations", []):
    if v["type"] not in HARD or hardset.exempt(v): continue
    items = v.get("items", [])
    for it in items:
        if not it.get("description", "").startswith(("Track", "Via")): continue
        for i in at(it["pos"]):
            if chain_len[find(i)] <= ESCAPE_MM: continue   # an escape stub: escape_prune's, after the fanout
            base = base_of(locked[i].GetNetname())
            other = next((o.get("description", "?")[:70] for o in items if o is not it), "?")
            marked.setdefault(base, []).append("%s: %s against %s" % (v["type"], it["description"][:60], other))

if not marked:
    open(out, "w").write("")
    print("pair_prune: nothing to prune (0 pairs; %s)" % out); sys.exit(0)

removed = 0; lines = []
for base, why in sorted(marked.items()):
    n = 0
    for i, t in enumerate(locked):
        if base_of(t.GetNetname()) == base and chain_len[find(i)] > ESCAPE_MM:
            b.Remove(t); n += 1
    removed += n
    lines.append("%s: %d locked piece(s) removed on both nets; %s" % (base, n, "; ".join(why[:3]) + (" (+%d more)" % (len(why) - 3) if len(why) > 3 else "")))
    print("pair_prune:   %s" % lines[-1])
pcbnew.SaveBoard(sys.argv[1], b)
open(out, "w").write("\n".join(lines) + "\n")
print("pair_prune: %d pair(s) the DRC refused removed whole, %d locked pieces, so the router lays them uncoupled (%s)" % (len(marked), removed, out))
sys.exit(2)
