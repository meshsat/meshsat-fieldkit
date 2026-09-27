#!/usr/bin/env python3
"""dsn_confine.py <in.dsn> <out.dsn> <part.json> <group> <layer ...>
Confine one partition job to its own region (research note v2/docs/research-parallel-autorouting.md, lesson of the 7 Sep 2026 merge: unconfined
concurrent region jobs route through each other's columns and collide). For every other region in part.json's "boxes" a keepout over that region's
core (its box shrunk by the margin) is added to the DSN's structure on every listed routing layer; the margins between regions stay free for both
neighbours. The group's own region and the global nets' space are untouched. Case-frame x (mm) to DSN um: (x + 150) * 1000; y spans the board."""
import sys, json, re
dsn_in, dsn_out, pj, group = sys.argv[1:5]; layers = sys.argv[5:]
part = json.load(open(pj)); boxes = part.get("boxes", {}); M = float(part.get("margin", 8.0)); OX = 150.0
s = open(dsn_in).read()
i = s.find("(structure"); assert i >= 0, "no structure section"
depth = 0; j = i
while j < len(s):
    if s[j] == "(": depth += 1
    elif s[j] == ")":
        depth -= 1
        if depth == 0: break
    j += 1
struct = s[i:j]
ys = [float(v) for v in re.findall(r"\(path pcb 0((?:\s+-?[\d.]+\s+-?[\d.]+)+)", struct)[0].split()[1::2]] if "(path pcb 0" in struct else []
y0, y1 = (min(ys), max(ys)) if ys else (-210000.0, -10000.0)
blocks = []; n = 0
for r, (bx0, bx1) in boxes.items():
    if r == group: continue
    cx0, cx1 = bx0 + M, bx1 - M
    if cx1 - cx0 < 2.0: continue
    X0, X1 = (cx0 + OX) * 1000.0, (cx1 + OX) * 1000.0
    for lay in layers:
        blocks.append('    (keepout "conf_%s_%s" (polygon %s 0  %.0f %.0f  %.0f %.0f  %.0f %.0f  %.0f %.0f  %.0f %.0f))' % (r, lay, lay, X0, y1, X1, y1, X1, y0, X0, y0, X0, y1)); n += 1
out = s[:j] + "\n" + "\n".join(blocks) + "\n  " + s[j:]
open(dsn_out, "w").write(out)
print("dsn_confine: %s confined with %d keep-outs over %s on %s" % (group, n, [r for r in boxes if r != group], layers))
