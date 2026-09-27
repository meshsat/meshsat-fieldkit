#!/usr/bin/env python3
"""Decision 42: which nets are poured on which copper layers of a committed board, and the stackup's layer list.
Text reader; a zone counts as a plane only when it carries filled copper (filled_polygon) on that layer, with the
filled area summed by the shoelace formula. Usage: dec_planes.py <board.kicad_pcb>"""
import sys, collections
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from dec_geometry import parse, kids, kid

b = parse(open(sys.argv[1], encoding="utf-8").read())
layers = [l[1] for l in kid(b, "layers")[1:] if isinstance(l, list) and l[1].endswith(".Cu")]
st = kid(kid(b, "setup"), "stackup")
thick = []
if st:
    for L in kids(st, "layer"):
        t = kid(L, "thickness"); ty = kid(L, "type")
        thick.append((L[1], ty[1] if ty else "", float(t[1]) if t else None))
area = collections.defaultdict(float)
for z in kids(b, "zone"):
    net = kid(z, "net_name"); net = net[1] if net and len(net) > 1 else ""
    for fp in kids(z, "filled_polygon"):
        lay = kid(fp, "layer")[1]
        pts = [(float(x[1]), float(x[2])) for x in kids(kid(fp, "pts"), "xy")]
        a = 0.0
        for i in range(len(pts)):
            x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % len(pts)]; a += x1 * y2 - x2 * y1
        area[(lay, net)] += abs(a) / 2
print(sys.argv[1]); print("  copper layers:", layers)
for t in thick: print("  stack:", t)
for (lay, net), a in sorted(area.items(), key=lambda kv: (layers.index(kv[0][0]) if kv[0][0] in layers else 99, -kv[1])):
    if a >= 50: print("  %-6s %-16s %8.0f mm2" % (lay, net, a))
