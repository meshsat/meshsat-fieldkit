#!/usr/bin/env python3
"""Post-route length matching (B14, 5 Sep 2026): Freerouting does not length-match a differential pair, so the short leg gets a trombone
meander inserted into one of its straight segments where the layer is free beside it. Usage: meander.py <board.kicad_pcb> <net name> <extra mm> [amplitude mm]
The board is rewritten in place; the caller runs DRC afterwards and reverts if the hard count rose. Prints 'meander: ...' lines."""
import sys, math, pcbnew
FromMM, ToMM = pcbnew.FromMM, pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1]); netname = sys.argv[2]; extra = float(sys.argv[3]); A = float(sys.argv[4]) if len(sys.argv) > 4 else 1.4
net = b.GetNetInfo().GetNetItem(netname) or b.GetNetInfo().GetNetItem("/" + netname)
if not net: print("meander: net not found", netname); sys.exit(1)
tracks = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and t.GetNetCode() == net.GetNetCode() and not t.IsLocked()]
n_bumps = max(1, math.ceil(extra / (2 * A))); A = extra / (2 * n_bumps)          # 2A per bump
w = tracks[0].GetWidth() / 1e6 if tracks else 0.2; clr = 0.15; p = w + clr + 0.25   # pitch between the legs of one bump
need_len = 2 * p * n_bumps + 2.0; depth = A + w + clr + 0.1
def items_on(layer):
    out = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T: bb = t.GetBoundingBox(); out.append(("via", t.GetNetCode(), bb))
        elif t.GetLayer() == layer: out.append(("trk", t.GetNetCode(), t.GetBoundingBox(), t))
    for fp in b.GetFootprints():
        for pd in fp.Pads():
            if pd.IsOnLayer(layer) or pd.GetAttribute() == pcbnew.PAD_ATTRIB_PTH: out.append(("pad", pd.GetNetCode(), pd.GetBoundingBox()))
    for z in b.Zones():
        if z.GetIsRuleArea() and z.IsOnLayer(layer) and z.GetDoNotAllowTracks(): out.append(("keep", -1, z.GetBoundingBox()))
    return out
def free(layer, x0, y0, x1, y1, me):
    box = pcbnew.BOX2I(pcbnew.VECTOR2I(int(min(x0, x1) * 1e6), int(min(y0, y1) * 1e6)), pcbnew.VECTOR2I(int(abs(x1 - x0) * 1e6), int(abs(y1 - y0) * 1e6)))
    for it in items_on(layer):
        if len(it) == 4 and it[3] is me: continue
        if it[2].Intersects(box): return False
    edge = b.GetBoardEdgesBoundingBox()
    return edge.Contains(box.GetOrigin()) and edge.Contains(box.GetEnd())
best = None
for t in sorted(tracks, key=lambda t: -t.GetLength()):
    L = ToMM(t.GetLength())
    if L < need_len: break
    s, e = t.GetStart(), t.GetEnd(); sx, sy, ex, ey = ToMM(s.x), ToMM(s.y), ToMM(e.x), ToMM(e.y)
    if abs(sx - ex) > 0.01 and abs(sy - ey) > 0.01: continue        # axis-parallel segments only
    horizontal = abs(sy - ey) < 0.01
    for side in (1, -1):
        if horizontal: x0, x1 = min(sx, ex) + 1.0, max(sx, ex) - 1.0; y0, y1 = sy + side * (w / 2 + clr), sy + side * depth
        else: y0, y1 = min(sy, ey) + 1.0, max(sy, ey) - 1.0; x0, x1 = sx + side * (w / 2 + clr), sx + side * depth
        if free(t.GetLayer(), x0, y0, x1, y1, t): best = (t, side, horizontal); break
    if best: break
if not best: print("meander: no straight segment of %.1f mm with %.1f mm free beside it on net %s" % (need_len, depth, netname)); sys.exit(1)
t, side, horizontal = best; s, e = t.GetStart(), t.GetEnd(); layer, width = t.GetLayer(), t.GetWidth()
sx, sy, ex, ey = ToMM(s.x), ToMM(s.y), ToMM(e.x), ToMM(e.y)
# walk from the start toward the end: u along the track, v toward the free side
if horizontal: u = (1.0 if ex > sx else -1.0, 0.0); v = (0.0, side)
else: u = (0.0, 1.0 if ey > sy else -1.0); v = (side, 0.0)
pts = [(sx, sy)]; cx, cy = sx + u[0] * 1.0, sy + u[1] * 1.0; pts.append((cx, cy))
for i in range(n_bumps):
    pts.append((cx + v[0] * A, cy + v[1] * A)); cx, cy = cx + u[0] * p, cy + u[1] * p; pts.append((cx + v[0] * A, cy + v[1] * A)); pts.append((cx, cy)); cx, cy = cx + u[0] * p, cy + u[1] * p; pts.append((cx, cy))
pts.append((ex, ey))
b.Remove(t)
for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
    if abs(x1 - x0) < 1e-6 and abs(y1 - y0) < 1e-6: continue
    nt = pcbnew.PCB_TRACK(b); nt.SetStart(pcbnew.VECTOR2I(int(round(x0 * 1e6)), int(round(y0 * 1e6)))); nt.SetEnd(pcbnew.VECTOR2I(int(round(x1 * 1e6)), int(round(y1 * 1e6)))); nt.SetWidth(width); nt.SetLayer(layer); nt.SetNet(net); b.Add(nt)
pcbnew.SaveBoard(sys.argv[1], b)
print("meander: %s +%.2f mm as %d bumps of %.2f mm on %s from (%.1f, %.1f) to (%.1f, %.1f), side %+d" % (netname, extra, n_bumps, A, b.GetLayerName(layer), sx, sy, ex, ey, side))
