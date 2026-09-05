#!/usr/bin/env python3
"""Post-route length matching (B14, 5 Sep 2026): Freerouting does not length-match a differential pair, so the short leg gets trombone meanders
inserted into its straight segments (any angle) wherever the layer is free beside them, until the requested extra length is reached.
Usage: meander.py <board.kicad_pcb> <net name> <extra mm> [amplitude mm]   (run in the project directory; the caller runs DRC and reverts on harm)
Prints 'meander: ...' lines and exits 1 when the extra length could not be placed."""
import sys, math, pcbnew
FromMM, ToMM = pcbnew.FromMM, pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1]); netname = sys.argv[2]; remaining = float(sys.argv[3]); A_MAX = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
net = b.GetNetInfo().GetNetItem(netname) or b.GetNetInfo().GetNetItem("/" + netname)
if not net: print("meander: net not found", netname); sys.exit(1)
CLR = 0.15; MARGIN = 0.8
def strip_shape(x0, y0, x1, y1, w_out):
    """polygon covering the band from the segment's far edge out to w_out on side v (mm in, polygon in nm)"""
    p = pcbnew.SHAPE_POLY_SET(); p.NewOutline()
    for x, y in ((x0, y0), (x1, y1), (x1 + w_out[0], y1 + w_out[1]), (x0 + w_out[0], y0 + w_out[1])): p.Append(int(round(x * 1e6)), int(round(y * 1e6)))
    return p
def obstacles(layer, me):
    out = []
    for t in b.GetTracks():
        if t is me: continue
        if t.Type() == pcbnew.PCB_VIA_T or t.GetLayer() == layer: out.append(t.GetEffectiveShape(layer))
    for fp in b.GetFootprints():
        for pd in fp.Pads():
            if pd.IsOnLayer(layer) or pd.GetAttribute() == pcbnew.PAD_ATTRIB_PTH: out.append(pd.GetEffectiveShape(layer))
    for z in b.Zones():
        if z.GetIsRuleArea() and z.IsOnLayer(layer) and z.GetDoNotAllowTracks(): out.append(z.Outline())
    return out
edge = b.GetBoardEdgesBoundingBox()
def free_window(t, side, depth, need):
    """the longest free run (start offset, length) along track t on the given side, at least `need` long, or None"""
    s, e = t.GetStart(), t.GetEnd(); sx, sy, ex, ey = ToMM(s.x), ToMM(s.y), ToMM(e.x), ToMM(e.y); L = math.hypot(ex - sx, ey - sy)
    if L < need + 2 * MARGIN: return None
    ux, uy = (ex - sx) / L, (ey - sy) / L; vx, vy = -uy * side, ux * side
    obs = obstacles(t.GetLayer(), t); step = 0.5; n = int(L / step)
    ok = []
    for i in range(n + 1):
        a = i * step; x0, y0 = sx + ux * a, sy + uy * a; x1, y1 = sx + ux * min(a + step, L), sy + uy * min(a + step, L)
        strip = strip_shape(x0 + vx * (CLR + 0.1), y0 + vy * (CLR + 0.1), x1 + vx * (CLR + 0.1), y1 + vy * (CLR + 0.1), (vx * depth, vy * depth))
        inside = all(edge.Contains(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6))) for x, y in ((x0 + vx * depth, y0 + vy * depth), (x1 + vx * depth, y1 + vy * depth)))
        ok.append(inside and not any(strip.Collide(o, int(CLR * 1e6)) for o in obs))
    best = None; run = 0
    for i, f in enumerate(ok + [False]):
        if f: run += 1
        else:
            if run * step >= need + 2 * MARGIN and (best is None or run > best[1]): best = ((i - run) * step, run)
            run = 0
    return (best[0], best[1] * step) if best else None
placed = 0.0; passes = 0
while remaining > 0.1 and passes < 12:
    passes += 1; w = 0.2
    tracks = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and t.GetNetCode() == net.GetNetCode() and not t.IsLocked()]
    if tracks: w = ToMM(tracks[0].GetWidth())
    p = w + CLR + 0.25                       # pitch between the two legs of one bump; a bump adds 2 A
    choice = None
    for A in (A_MAX, 1.0, 0.7, 0.5):
        n_want = max(1, math.ceil(remaining / (2 * A))); need = 2 * p * n_want
        for t in sorted(tracks, key=lambda t: -t.GetLength()):
            for side in (1, -1):
                fw = free_window(t, side, A + w + CLR + 0.1, min(need, 2 * p * 2))
                if fw:
                    n_fit = min(n_want, int((fw[1] - 2 * MARGIN) / (2 * p)))
                    if n_fit >= 1 and (choice is None or n_fit > choice[3]): choice = (t, side, fw, n_fit, A)
            if choice and choice[3] >= n_want: break
        if choice: break
    if not choice: break
    t, side, (off, wlen), n_fit, A = choice; A = min(A, remaining / (2 * n_fit))
    s, e = t.GetStart(), t.GetEnd(); sx, sy, ex, ey = ToMM(s.x), ToMM(s.y), ToMM(e.x), ToMM(e.y); L = math.hypot(ex - sx, ey - sy)
    ux, uy = (ex - sx) / L, (ey - sy) / L; vx, vy = -uy * side, ux * side; layer, width = t.GetLayer(), t.GetWidth()
    a0 = off + MARGIN; pts = [(sx, sy), (sx + ux * a0, sy + uy * a0)]; cx, cy = pts[-1]
    for i in range(n_fit):
        pts.append((cx + vx * A, cy + vy * A)); cx, cy = cx + ux * p, cy + uy * p; pts.append((cx + vx * A, cy + vy * A)); pts.append((cx, cy)); cx, cy = cx + ux * p, cy + uy * p; pts.append((cx, cy))
    pts.append((ex, ey)); b.Remove(t)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if math.hypot(x1 - x0, y1 - y0) < 1e-4: continue
        nt = pcbnew.PCB_TRACK(b); nt.SetStart(pcbnew.VECTOR2I(int(round(x0 * 1e6)), int(round(y0 * 1e6)))); nt.SetEnd(pcbnew.VECTOR2I(int(round(x1 * 1e6)), int(round(y1 * 1e6)))); nt.SetWidth(width); nt.SetLayer(layer); nt.SetNet(net); b.Add(nt)
    added = 2 * A * n_fit; placed += added; remaining -= added
    print("meander: %s +%.2f mm as %d bumps of %.2f mm on %s along (%.1f, %.1f)-(%.1f, %.1f) side %+d, %.2f mm still to place" % (netname, added, n_fit, A, b.GetLayerName(layer), sx, sy, ex, ey, side, max(remaining, 0)))
pcbnew.SaveBoard(sys.argv[1], b)
if remaining > 0.1: print("meander: could not place the last %.2f mm on %s" % (remaining, netname)); sys.exit(1)
print("meander: %s lengthened by %.2f mm in %d passes" % (netname, placed, passes))
