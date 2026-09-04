#!/usr/bin/env python3
"""A19 node bars on top of the routed board (crossing-checked against every other-net track and via, like fix_a17_node.py):
CELL+ : the four 9 A pins (J_CP1..4, underside, X -145..-133, Y -73) -> a 8 mm bar north to Y -60 -> east along Y -60 to X -56 (charger BAT pads)
        with taps north to the node pad (pad 1) of F3, F4, F5 and F2 on the fuse row at Y -46; the pre-charge pin joins through R51.
CELL_N: the four return pins (J_CN1..4, Y -67) -> bar east along Y -64 to the shunt R52 pad 1 (X -130, Y -60); R52 pad 2 is GND (plane + vias).
Usage: fix_a19_node.py <board.kicad_pcb>"""
import sys, pcbnew
from pcbnew import VECTOR2I, FromMM
OX, OY = 150.0, 110.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
b = pcbnew.LoadBoard(sys.argv[1]); nets = b.GetNetInfo()
pads = {}
for fp in b.GetFootprints():
    for pd in fp.Pads(): pads[(fp.GetReference(), pd.GetNumber())] = (pd.GetPosition().x / 1e6 - OX, OY - pd.GetPosition().y / 1e6)
existing = {}; vias = []
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        vias.append(((t.GetPosition().x / 1e6 - OX, OY - t.GetPosition().y / 1e6), t.GetNetname(), t.GetWidth() / 1e6)); continue
    existing.setdefault(t.GetLayer(), []).append(((t.GetStart().x / 1e6 - OX, OY - t.GetStart().y / 1e6), (t.GetEnd().x / 1e6 - OX, OY - t.GetEnd().y / 1e6), t.GetNetname(), t.GetWidth() / 1e6))
def segdist(a, b_, c, d):
    import math
    def pdist(p, a, b_):
        ax, ay = a; bx, by = b_; px, py = p; dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
        t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2)); return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
    def cross(o, a, b_): return (a[0] - o[0]) * (b_[1] - o[1]) - (a[1] - o[1]) * (b_[0] - o[0])
    d1, d2, d3, d4 = cross(c, d, a), cross(c, d, b_), cross(a, b_, c), cross(a, b_, d)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and d1 != 0 and d2 != 0 and d3 != 0 and d4 != 0: return 0.0
    return min(pdist(a, c, d), pdist(b_, c, d), pdist(c, a, b_), pdist(d, a, b_))
def clear(p, q, w, net, layer):
    for (a, b_, n, ew) in existing.get(layer, []):
        if n == net: continue
        if segdist(p, q, a, b_) < w / 2 + ew / 2 + 0.25: return False
    for (c, n, vw) in vias:
        if n == net: continue
        if segdist(p, q, c, c) < w / 2 + vw / 2 + 0.25: return False
    return True
def track(x1, y1, x2, y2, w, layer, netname):
    t = pcbnew.PCB_TRACK(b); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2)); t.SetWidth(FromMM(w)); t.SetLayer(layer); t.SetNet(nets.GetNetItem(netname)); b.Add(t)
    existing.setdefault(layer, []).append(((x1, y1), (x2, y2), netname, w))
bad = []
def path(pts, w, net, layers=(pcbnew.F_Cu, pcbnew.B_Cu)):
    for L in layers:
        for p, q in zip(pts, pts[1:]):
            if clear(p, q, w, net, L): track(p[0], p[1], q[0], q[1], w, L, net)
            else: bad.append((net, b.GetLayerName(L), p, q))
BAR_Y, RET_Y = -60.0, -64.0
cps = [pads[("J_CP%d" % k, "1")] for k in range(1, 5)]; cns = [pads[("J_CN%d" % k, "1")] for k in range(1, 5)]
xw, xe = min(p[0] for p in cps) - 2.0, -56.0
path([(xw, BAR_Y), (xe, BAR_Y)], 8.0, "/CELL+")                                   # the node bar
for p in cps: path([p, (p[0], BAR_Y)], 4.0, "/CELL+")                              # each 9 A pin up to the bar
for ref in ("F3", "F4", "F5", "F2"):
    n = pads[(ref, "1")]; path([(n[0], BAR_Y), n], 4.0, "/CELL+")                     # taps to the fuse node pads
for k in ("22", "23"):
    n = pads[("U20", k)]; path([(xe, BAR_Y), (xe, n[1]), n], 2.5, "/CELL+")           # charger BAT pads
r52 = pads[("R52", "1")]
path([(cns[0][0] - 2.0, RET_Y), (r52[0], RET_Y), r52], 6.0, "/CELL_N")
for p in cns: path([p, (p[0], RET_Y)], 3.0, "/CELL_N")
pcbnew.SaveBoard(sys.argv[1], b); b = pcbnew.LoadBoard(sys.argv[1]); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)
print("A19 bars placed; blocked segments: %s" % (bad if bad else "none"))
