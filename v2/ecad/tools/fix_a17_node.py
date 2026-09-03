#!/usr/bin/env python3
"""A17 pack node bars (A16 bars plus F3 and the boost feed) on top of the routed board, with a crossing check against every existing track of another net on the chosen layer.
CELL_N straight between the XT60 pin 2 pads; CELL+ from J_PACK.1 west to X-5.5, north to Y 42.5, east to F1's node pad and on to F2's node pad from above;
CELL_X from F1's other pad east to X+6, south to the XT60 pin 1; MEZZ_CELL from F2's other pad down a clear column to the VH header pin 1.
Usage: fix_a17_node.py <board.kicad_pcb>"""
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
        vias.append(((t.GetPosition().x / 1e6 - OX, OY - t.GetPosition().y / 1e6), t.GetNetname(), t.GetWidth() / 1e6)); continue   # A17: vias block bars on every layer
    existing.setdefault(t.GetLayer(), []).append(((t.GetStart().x / 1e6 - OX, OY - t.GetStart().y / 1e6), (t.GetEnd().x / 1e6 - OX, OY - t.GetEnd().y / 1e6), t.GetNetname(), t.GetWidth() / 1e6))
def segdist(a, b_, c, d):
    """minimum distance between segments ab and cd"""
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
def path_any(pts, w, net):
    """place on whichever single layer is clear for every segment, else report"""
    for L in (pcbnew.F_Cu, pcbnew.B_Cu):
        if all(clear(p, q, w, net, L) for p, q in zip(pts, pts[1:])):
            for p, q in zip(pts, pts[1:]): track(p[0], p[1], q[0], q[1], w, L, net)
            return b.GetLayerName(L)
    return None
p1, p2 = pads[("J_PACK", "1")], pads[("J_PACK", "2")]; x1, x2 = pads[("J_X1202BAT", "1")], pads[("J_X1202BAT", "2")]
f1n, f1x = pads[("F1", "1")], pads[("F1", "2")]; f2n, f2m = pads[("F2", "1")], pads[("F2", "2")]; mz = pads[("J_MEZZ_PWR1", "1")]
path([p2, x2], 4.0, "/CELL_N")
wx = p1[0] - 5.5
path([p1, (wx, p1[1]), (wx, f1n[1]), f1n], 3.0, "/CELL+")                    # pack pad, west detour, fuse F1 node pad (its lower pad)
path([f1n, (f2n[0], f1n[1]), f2n], 2.5, "/CELL+")                             # F1 node pad east to F2 node pad, along the fuse-pad row
cx, cy = f2n[0] + 4.0, x1[1] + 2.4                                            # CELL_X: from F1's upper pad east past F2's node pad, down east of it, back west above the XT60
path([f1x, (cx, f1x[1]), (cx, cy), (x1[0], cy), x1], 2.5, "/CELL_X")
placed = None
for cx in (f2m[0], f2m[0] + 1.5, f2m[0] + 3.0, f2m[0] - 1.5, f2m[0] + 4.5, f2m[0] + 6.0):
    placed = path_any([f2m, (cx, f2m[1]), (cx, mz[1]), mz], 2.5, "/MEZZ_CELL")
    if placed: print("MEZZ_CELL column at X %.1f on %s" % (cx, placed)); break
if not placed: bad.append(("/MEZZ_CELL", "any", f2m, mz))
# A17: CELL+ from the pack pad's west detour south to F3's node pad; BOOST_CELL from F3's other pad to the inductor L2 (else the router's 1.5 mm BOOST-class track stands)
f3n, f3x = pads[("F3", "1")], pads[("F3", "2")]; l2 = pads[("L2", "1")]
path([(wx, p1[1]), (wx, f3n[1]), f3n], 3.0, "/CELL+")
placed3 = None
for cy in (f3x[1], f3x[1] - 1.5, f3x[1] + 1.5, f3x[1] - 3.0, f3x[1] + 3.0):
    placed3 = path_any([f3x, (f3x[0], cy), (l2[0], cy), l2], 2.5, "/BOOST_CELL")
    if placed3: print("BOOST_CELL bar at Y %.1f on %s" % (cy, placed3)); break
if not placed3: print("BOOST_CELL bar not placed: the router copper stands")
pcbnew.SaveBoard(sys.argv[1], b); b = pcbnew.LoadBoard(sys.argv[1]); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)
print("bars placed; F1 node pad %s, F2 node pad %s; blocked segments: %s" % (f1n, f2n, bad if bad else "none"))
