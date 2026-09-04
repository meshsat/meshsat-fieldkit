#!/usr/bin/env python3
"""Remove unused escape vias (signal nets only: nets without a zone) and the stub tracks left hanging behind them.
Works on a by-value model first, then removes the board items by UUID in one pass (SWIG proxies die after Remove)."""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); TOL = 2000
zoned = {z.GetNetname() for z in b.Zones() if not z.GetIsRuleArea()}
T = []; V = []
for t in b.GetTracks():
    if t.GetNetname() in zoned: continue
    u = str(t.m_Uuid.AsString())
    if t.GetClass() == "PCB_VIA": p = t.GetPosition(); V.append([u, t.GetNetname(), p.x, p.y, max(t.GetWidth(pcbnew.F_Cu) // 2, TOL)])
    elif t.GetClass() == "PCB_TRACK": s, e = t.GetStart(), t.GetEnd(); T.append([u, t.GetNetname(), s.x, s.y, e.x, e.y, t.GetWidth()])
P = [(pd.GetNetname(), pd) for fp in b.GetFootprints() for pd in fp.Pads()]
def same(x0, y0, x1, y1, tol=TOL): return abs(x0 - x1) <= tol and abs(y0 - y1) <= tol
def at_via(x, y, v): return ((x - v[2]) ** 2 + (y - v[3]) ** 2) ** 0.5 <= v[4]
def on_seg(x, y, t):
    ax, ay, ex, ey, w = t[2], t[3], t[4], t[5], t[6]; dx, dy = ex - ax, ey - ay; L2 = dx * dx + dy * dy
    if L2 == 0: return same(x, y, ax, ay)
    u = ((x - ax) * dx + (y - ay) * dy) / L2
    if u < -0.001 or u > 1.001: return False
    return ((ax + u * dx - x) ** 2 + (ay + u * dy - y) ** 2) ** 0.5 <= w / 2
gone = set(); rv = rt = 0
while True:
    changed = False
    for v in V:
        if v[0] in gone: continue
        # a track that passes over the via (the stub router's closing via lands on the middle of an inner-layer run) is a connection too
        n = sum(1 for t in T if t[0] not in gone and t[1] == v[1] and (at_via(t[2], t[3], v) or at_via(t[4], t[5], v) or on_seg(v[2], v[3], t)))
        if n <= 1: gone.add(v[0]); rv += 1; changed = True
    for t in T:
        if t[0] in gone: continue
        # a track that another same-net track branches from (its end lies on this track) carries that branch: keep it whole, dead tail and all
        # (C5, 4 Sep: the router left a locked escape stub's via unused and started its own track from the stub's middle; removing the stub cut the pad off)
        if any(u[0] not in gone and u is not t and u[1] == t[1] and (on_seg(u[2], u[3], t) or on_seg(u[4], u[5], t)) for u in T): continue
        for (x, y) in ((t[2], t[3]), (t[4], t[5])):
            touched = any(u[0] not in gone and u is not t and u[1] == t[1] and (same(u[2], u[3], x, y) or same(u[4], u[5], x, y) or on_seg(x, y, u)) for u in T)
            touched = touched or any(v[0] not in gone and v[1] == t[1] and at_via(x, y, v) for v in V)
            touched = touched or any(net == t[1] and pd.HitTest(pcbnew.VECTOR2I(int(x), int(y))) for net, pd in P)
            if not touched: gone.add(t[0]); rt += 1; changed = True; break
    if not changed: break
victims = [t for t in b.GetTracks() if str(t.m_Uuid.AsString()) in gone]
for t in victims: b.Remove(t)
pcbnew.SaveBoard(sys.argv[1], b); print("cleanup: %d dangling vias and %d hanging tracks removed" % (rv, rt))
