#!/usr/bin/env python3
"""Differential-pair pre-router (MESHSAT-862 rule 1 of appendix 32.67, 8 Sep 2026): Freerouting has no pair routing, so every released pair was
two lone traces millimetres apart (32.66). This lays both legs of a pair as LOCKED copper before Freerouting runs, at the class width w and
gap s, on the class's allowed layers (rule 2), so the router only sees two finished nets.

Method (the stub router's grid, 0.1 mm): the pair's centreline is routed by A* from the midpoint between the two P and N starts to the
midpoint between the two ends, on a map where every other-net copper item is grown by (clearance + w + s/2), the pair's half envelope; a
through via costs VIA_COST and is only allowed where two via sites (0.9 mm apart along the local normal) are free. The path is simplified to
straight runs; each run is offset by +-(w + s)/2 on its layer, consecutive runs meet at their offset intersection (a mitre); at a layer change
each leg gets its own via 0.9 mm from the centreline with a jog; at the ends short stubs join the offset ends to the pads (or to the escape
vias when the pads carry locked escapes). Everything added is locked. A pair whose centreline finds no path is reported and left to the
router (the gate then calls it UNCOUPLED). The caller runs DRC.

Usage: pair_preroute.py <board.kicad_pcb> [--pairs STEM,STEM] [--layers F.Cu,In2.Cu] [--classes USB,DIFF100] [--test] [--grid 0.1]
  prints one line per pair and `pair_preroute: N of M pairs laid`, exit 1 when a pair failed."""
import sys, os, re, math, json, heapq
import pcbnew, numpy as np
from pcbnew import VECTOR2I, FromMM
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CLR = 0.16; HOLE_CLR = 0.30; VIA_COST = 60.0; VIA_SPLIT = 0.9
_ALL = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "In3.Cu": pcbnew.In3_Cu, "In4.Cu": pcbnew.In4_Cu, "B.Cu": pcbnew.B_Cu}

def mm(v): return v / 1e6

class Grid:
    def __init__(self, b, g):
        self.b, self.G = b, g; eb = b.GetBoardEdgesBoundingBox()
        self.X0, self.Y0 = eb.GetLeft() / 1e6 - 1.0, eb.GetTop() / 1e6 - 1.0
        self.NX, self.NY = int(eb.GetWidth() / 1e6 / g) + 20, int(eb.GetHeight() / 1e6 / g) + 20
    def cell(self, x, y): return int(round((x - self.X0) / self.G)), int(round((y - self.Y0) / self.G))
    def xy(self, j, i): return self.X0 + j * self.G, self.Y0 + i * self.G
    def disc(self, M, cx, cy, r):
        G, X0, Y0, NX, NY = self.G, self.X0, self.Y0, self.NX, self.NY
        i0, i1 = max(0, int((cy - r - Y0) / G)), min(NY - 1, int((cy + r - Y0) / G) + 1); j0, j1 = max(0, int((cx - r - X0) / G)), min(NX - 1, int((cx + r - X0) / G) + 1)
        if i1 < i0 or j1 < j0: return
        ys = (np.arange(i0, i1 + 1) * G + Y0)[:, None]; xs = (np.arange(j0, j1 + 1) * G + X0)[None, :]
        M[i0:i1 + 1, j0:j1 + 1] |= (xs - cx) ** 2 + (ys - cy) ** 2 <= r * r
    def seg(self, M, ax, ay, bx, by, r):
        G, X0, Y0, NX, NY = self.G, self.X0, self.Y0, self.NX, self.NY
        i0, i1 = max(0, int((min(ay, by) - r - Y0) / G)), min(NY - 1, int((max(ay, by) + r - Y0) / G) + 1); j0, j1 = max(0, int((min(ax, bx) - r - X0) / G)), min(NX - 1, int((max(ax, bx) + r - X0) / G) + 1)
        if i1 < i0 or j1 < j0: return
        ys = (np.arange(i0, i1 + 1) * G + Y0)[:, None]; xs = (np.arange(j0, j1 + 1) * G + X0)[None, :]
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
        t = 0 if L2 == 0 else np.clip(((xs - ax) * dx + (ys - ay) * dy) / L2, 0, 1)
        M[i0:i1 + 1, j0:j1 + 1] |= (xs - (ax + t * dx)) ** 2 + (ys - (ay + t * dy)) ** 2 <= r * r
    def poly(self, M, sps, grow):
        bb = sps.BBox(); G, X0, Y0, NX, NY = self.G, self.X0, self.Y0, self.NX, self.NY; r = grow
        i0, i1 = max(0, int((mm(bb.GetTop()) - r - Y0) / G)), min(NY - 1, int((mm(bb.GetBottom()) + r - Y0) / G) + 1); j0, j1 = max(0, int((mm(bb.GetLeft()) - r - X0) / G)), min(NX - 1, int((mm(bb.GetRight()) + r - X0) / G) + 1)
        if i1 < i0 or j1 < j0: return
        grown = pcbnew.SHAPE_POLY_SET(sps)
        if grow > 0:
            try: grown.Inflate(FromMM(grow), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, FromMM(0.05))
            except Exception:
                try: grown.Inflate(FromMM(grow), 16)
                except Exception: pass
        for ii in range(i0, i1 + 1):
            for jj in range(j0, j1 + 1):
                if grown.Contains(VECTOR2I(FromMM(X0 + jj * G), FromMM(Y0 + ii * G))): M[ii, jj] = True

def build_maps(gr, b, layers, nets, half, via_r):
    """Forbidden centreline cells per layer (other-net copper grown by half + CLR) and forbidden via-centre cells (any layer)."""
    trk = {L: np.zeros((gr.NY, gr.NX), dtype=bool) for L in layers}; via = np.zeros((gr.NY, gr.NX), dtype=bool)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            pth = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
            if pth: c = p.GetPosition(); d = p.GetDrillSize(); gr.disc(via, mm(c.x), mm(c.y), mm(max(d.x, d.y)) / 2 + 0.2 + 0.30)
            if p.GetNetname() in nets: continue
            for L in layers:
                if p.IsOnLayer(L): gr.poly(trk[L], p.GetEffectivePolygon(L), (HOLE_CLR if pth else CLR) + half)
            anyL = next((L for L in layers if p.IsOnLayer(L)), None)
            if anyL is not None or pth: gr.poly(via, p.GetEffectivePolygon(anyL if anyL is not None else pcbnew.F_Cu), CLR + via_r + VIA_SPLIT)
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA": c = t.GetPosition(); gr.disc(via, mm(c.x), mm(c.y), mm(t.GetDrillValue()) / 2 + 0.2 + 0.30 + VIA_SPLIT)
        if t.GetNetname() in nets: continue
        if t.GetClass() == "PCB_VIA":
            c = t.GetPosition(); r = mm(t.GetWidth(pcbnew.F_Cu)) / 2
            for L in layers: gr.disc(trk[L], mm(c.x), mm(c.y), r + CLR + half)
        else:
            a, e = t.GetStart(), t.GetEnd(); r = mm(t.GetWidth()) / 2; L = t.GetLayer()
            if L in trk: gr.seg(trk[L], mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + CLR + half)
            gr.seg(via, mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + CLR + via_r + VIA_SPLIT)
    for z in b.Zones():
        if z.GetIsRuleArea():
            for L in layers:
                if z.IsOnLayer(L) and z.GetDoNotAllowTracks(): gr.poly(trk[L], z.Outline(), CLR + half)
            if z.GetDoNotAllowVias(): gr.poly(via, z.Outline(), CLR + via_r + VIA_SPLIT)
    m = int(0.8 / gr.G) + 12
    for M in list(trk.values()) + [via]: M[:m, :] = True; M[-m:, :] = True; M[:, :m] = True; M[:, -m:] = True
    return trk, via

def astar(gr, layers, trk, via, start, goal, window):
    LI = {L: i for i, L in enumerate(layers)}
    (jmin, imin), (jmax, imax) = window
    passable = {LI[L]: ~trk[L] for L in layers}
    sL, sj, si = start; gL, gj, gi = goal
    for L in range(len(layers)):
        for (jj, ii) in ((sj, si), (gj, gi)):   # the two ends are enterable on every layer
            passable[L][max(0, ii - 3):ii + 4, max(0, jj - 3):jj + 4] = True
    def h(L, i, j): return math.hypot(i - gi, j - gj)
    dist = {}; prev = {}; pq = []
    for L in ([LI[sL]] if sL in LI else list(range(len(layers)))):
        s = (L, si, sj); dist[s] = 0.0; heapq.heappush(pq, (h(L, si, sj), 0.0, s))
    steps = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
    n = 0; found = None
    while pq:
        f, d, s = heapq.heappop(pq)
        if d > dist.get(s, 1e18): continue
        L, i, j = s; n += 1
        if (i, j) == (gi, gj) and (gL not in LI or L == LI[gL]): found = s; break
        if n > 6000000: break
        for di, dj, c in steps:
            ni, nj = i + di, j + dj
            if not (imin <= ni <= imax and jmin <= nj <= jmax): continue
            if not passable[L][ni, nj]: continue
            if di and dj and not (passable[L][i, nj] and passable[L][ni, j]): continue
            nd = d + c; t = (L, ni, nj)
            if nd < dist.get(t, 1e18): dist[t] = nd; prev[t] = s; heapq.heappush(pq, (nd + h(L, ni, nj), nd, t))
        if not via[i, j]:
            for oL in range(len(layers)):
                if oL == L or not passable[oL][i, j]: continue
                nd = d + VIA_COST; t = (oL, i, j)
                if nd < dist.get(t, 1e18): dist[t] = nd; prev[t] = s; heapq.heappush(pq, (nd + h(oL, i, j), nd, t))
    if found is None: return None
    path = [found]
    while path[-1] in prev: path.append(prev[path[-1]])
    return list(reversed(path))


def smooth(gr, pts_cells, passable):
    """Greedy line-of-sight simplification of a run's cells [(i, j)...] on one layer: keep the farthest point reachable by a straight segment
    whose samples all stay passable (the 8-direction grid path zigzags at cell scale, and offsetting a zigzag makes the legs cross)."""
    if len(pts_cells) <= 2: return list(pts_cells)
    def clear(a, b):
        (i0, j0), (i1, j1) = a, b; n = max(abs(i1 - i0), abs(j1 - j0)) * 2 + 1
        for k in range(n + 1):
            u = k / n; i = int(round(i0 + u * (i1 - i0))); j = int(round(j0 + u * (j1 - j0)))
            if not passable[i, j]: return False
        return True
    out = [pts_cells[0]]; k = 0
    while k < len(pts_cells) - 1:
        m = len(pts_cells) - 1
        while m > k + 1 and not clear(pts_cells[k], pts_cells[m]): m -= 1
        out.append(pts_cells[m]); k = m
    return out

def stub_path(gr, passable, start_xy, goal_xy, window):
    """A short A* for one track from start to goal (mm) on one layer's passable map; returns [(x, y)...] smoothed, or None."""
    sj, si = gr.cell(*start_xy); gj, gi = gr.cell(*goal_xy)
    for (jj, ii) in ((sj, si), (gj, gi)): passable[max(0, ii - 2):ii + 3, max(0, jj - 2):jj + 3] = True
    (jmin, imin), (jmax, imax) = window
    dist = {(si, sj): 0.0}; prev = {}; pq = [(0.0, 0.0, (si, sj))]; found = None; n = 0
    steps = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
    while pq:
        f, d0, (i, j) = heapq.heappop(pq)
        if d0 > dist.get((i, j), 1e18): continue
        if (i, j) == (gi, gj): found = (i, j); break
        n += 1
        if n > 400000: break
        for di, dj, c in steps:
            ni, nj = i + di, j + dj
            if not (imin <= ni <= imax and jmin <= nj <= jmax) or not passable[ni, nj]: continue
            if di and dj and not (passable[i, nj] and passable[ni, j]): continue
            nd = d0 + c
            if nd < dist.get((ni, nj), 1e18): dist[(ni, nj)] = nd; prev[(ni, nj)] = (i, j); heapq.heappush(pq, (nd + math.hypot(ni - gi, nj - gj), nd, (ni, nj)))
    if found is None: return None
    path = [found]
    while path[-1] in prev: path.append(prev[path[-1]])
    path.reverse(); cells = smooth(gr, path, passable)
    return [gr.xy(j, i) for i, j in cells]

def simplify(path):
    """[(layer index, i, j)] -> runs [(L, [(x,y)...])] with collinear points merged, split at vias."""
    runs = []; cur = [path[0]]
    for k in range(1, len(path)):
        a, c = path[k - 1], path[k]
        if a[0] != c[0]: runs.append(cur); cur = [c]; continue
        if len(cur) >= 2:
            p0, p1 = cur[-2], cur[-1]
            if (p1[1] - p0[1], p1[2] - p0[2]) == (c[1] - p1[1], c[2] - p1[2]): cur[-1] = c; continue
        cur.append(c)
    runs.append(cur); return runs

def offset_polyline(pts, d):
    """Offset a polyline (list of (x, y) mm) by d to its left; mitred joins."""
    if len(pts) < 2: return list(pts)
    segs = []
    for k in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[k], pts[k + 1]; dx, dy = bx - ax, by - ay; ln = math.hypot(dx, dy) or 1.0; nx, ny = -dy / ln * d, dx / ln * d
        segs.append(((ax + nx, ay + ny), (bx + nx, by + ny)))
    out = [segs[0][0]]
    for k in range(len(segs) - 1):
        (p1, p2), (p3, p4) = segs[k], segs[k + 1]
        d1 = (p2[0] - p1[0], p2[1] - p1[1]); d2 = (p4[0] - p3[0], p4[1] - p3[1]); den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9: out.append(p2); continue
        t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / den; ix, iy = p1[0] + t * d1[0], p1[1] + t * d1[1]
        if math.hypot(ix - p2[0], iy - p2[1]) > 3 * abs(d): out.append(p2); out.append(p3)   # a sharp bend: bevel instead of a long spike
        else: out.append((ix, iy))
    out.append(segs[-1][1]); return out

def main(a):
    if not a: print(__doc__); return 2
    board = a[0]; test = "--test" in a; g = float(a[a.index("--grid") + 1]) if "--grid" in a else 0.1
    b = pcbnew.LoadBoard(board); gr = Grid(b, g)
    pro = os.path.splitext(board)[0] + ".kicad_pro"; assign = {}; classes = {}
    if os.path.exists(pro):
        d = json.load(open(pro)); assign = d.get("net_settings", {}).get("netclass_assignments", {}); classes = {c["name"]: c for c in d.get("net_settings", {}).get("classes", [])}
    def cls_of(n):
        c = assign.get(n) or assign.get("/" + n.lstrip("/")) or assign.get(n.lstrip("/")); return (c[0] if isinstance(c, list) and c else c) or "Default"
    want_classes = set(a[a.index("--classes") + 1].split(",")) if "--classes" in a else {"USB", "DIFF100", "PCIE", "HDMI"}
    layers = [_ALL[x] for x in (a[a.index("--layers") + 1].split(",") if "--layers" in a else os.environ.get("PAIR_LAYERS", "F.Cu,B.Cu").split(",")) if x in _ALL]
    names = {str(n): n for n in b.GetNetInfo().NetsByName().keys()}
    stems = sorted({n[:-2] for n in names if n.endswith("_P") and n[:-2] + "_N" in names})
    if "--pairs" in a: stems = [s for s in stems if s.lstrip("/") in set(a[a.index("--pairs") + 1].split(","))]
    stems = [s for s in stems if cls_of(s + "_P") in want_classes]
    laid = 0; report = []; swapped = set()

    def dist_p(p, q): return math.hypot(p.GetPosition().x - q.GetPosition().x, p.GetPosition().y - q.GetPosition().y) / 1e6
    def anchor(p):
        """An escape via of the pad when one exists (a locked via of its net within 3 mm), else the pad: (x, y, layer or None for a via, object)."""
        vs = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA" and t.IsLocked() and t.GetNetname() == p.GetNetname() and math.hypot(t.GetPosition().x - p.GetPosition().x, t.GetPosition().y - p.GetPosition().y) < 3e6]
        if vs: v = min(vs, key=lambda t: math.hypot(t.GetPosition().x - p.GetPosition().x, t.GetPosition().y - p.GetPosition().y)); return (mm(v.GetPosition().x), mm(v.GetPosition().y), None, v)
        L = next((L for L in layers if p.IsOnLayer(L)), None); return (mm(p.GetPosition().x), mm(p.GetPosition().y), L, p)

    for stem in stems:   # a swapped pair is appended and laid again
        pn, nn = stem + "_P", stem + "_N"; cl = classes.get(cls_of(pn), {}); w = float(cl.get("diff_pair_width", cl.get("track_width", 0.2))); s = float(cl.get("diff_pair_gap", 0.15))
        vd, vdr = float(cl.get("via_diameter", 0.6)), float(cl.get("via_drill", 0.3)); half = w + s / 2; d = (w + s) / 2
        pads = {net: [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == net] for net in (pn, nn)}
        # a real leg is a chain of pads (connector, series resistor, ESD diode, hub pin): match each P pad to the nearest N pad within 5 mm (a station),
        # order the stations along the leg by nearest neighbour from the outermost one; unmatched pads (a lone test point) stay the router's stubs
        pool = list(pads[nn]); stations = []
        for p in sorted(pads[pn], key=lambda p: p.GetPosition().x):
            if not pool: break
            q = min(pool, key=lambda q: dist_p(p, q))
            if dist_p(p, q) <= 5.0: stations.append((p, q)); pool.remove(q)
        if len(stations) < 2: report.append("SKIP  %s: fewer than two matched stations (P %d, N %d pads)" % (stem, len(pads[pn]), len(pads[nn]))); continue
        def mid(st): return ((st[0].GetPosition().x + st[1].GetPosition().x) / 2e6, (st[0].GetPosition().y + st[1].GetPosition().y) / 2e6)
        far = max(stations, key=lambda st: sum(math.hypot(mid(st)[0] - mid(o)[0], mid(st)[1] - mid(o)[1]) for o in stations))
        order = [far]; rest = [st for st in stations if st is not far]
        while rest:
            nxt = min(rest, key=lambda st: math.hypot(mid(st)[0] - mid(order[-1])[0], mid(st)[1] - mid(order[-1])[1])); order.append(nxt); rest.remove(nxt)
        sections = list(zip(order[:-1], order[1:]))
        for t in [t for t in b.GetTracks() if t.GetNetname() in (pn, nn) and not t.IsLocked()]: b.Remove(t)   # a previous route of the pair goes; the locked escapes stay
        trk, via = build_maps(gr, b, layers, {pn, nn}, half, vd / 2)
        trk1, _via1 = build_maps(gr, b, layers, {pn, nn}, w / 2 + 0.15, vd / 2)   # the single-track map for the legs and stubs, 0.15 mm extra for the mask dam at through-hole pads
        net_p, net_n = b.GetNetInfo().GetNetItem(pn), b.GetNetInfo().GetNetItem(nn); added = 0; cells = 0; nruns = 0; failed = None; twist = None
        def seg(x1, y1, x2, y2, L, net):
            nonlocal added
            if math.hypot(x2 - x1, y2 - y1) < 0.01: return
            t = pcbnew.PCB_TRACK(b); t.SetStart(VECTOR2I(FromMM(x1), FromMM(y1))); t.SetEnd(VECTOR2I(FromMM(x2), FromMM(y2))); t.SetWidth(FromMM(w)); t.SetLayer(L); t.SetNet(net); t.SetLocked(True); b.Add(t); added += 1
        def via_at(x, y, net):
            nonlocal added
            v = pcbnew.PCB_VIA(b); v.SetPosition(VECTOR2I(FromMM(x), FromMM(y))); v.SetWidth(FromMM(vd)); v.SetDrill(FromMM(vdr)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net); v.SetLocked(True); b.Add(v); added += 1
        for (pa, na), (pb, nb) in sections:
            A = [anchor(pa), anchor(na)]; B = [anchor(pb), anchor(nb)]
            sx, sy = (A[0][0] + A[1][0]) / 2, (A[0][1] + A[1][1]) / 2; gx, gy = (B[0][0] + B[1][0]) / 2, (B[0][1] + B[1][1]) / 2
            sL = A[0][2] if A[0][2] == A[1][2] else None; gL = B[0][2] if B[0][2] == B[1][2] else None
            sj, si = gr.cell(sx, sy); gj, gi = gr.cell(gx, gy); win = 25.0
            window = (gr.cell(min(sx, gx) - win, min(sy, gy) - win), gr.cell(max(sx, gx) + win, max(sy, gy) + win))
            window = ((max(0, window[0][0]), max(0, window[0][1])), (min(gr.NX - 1, window[1][0]), min(gr.NY - 1, window[1][1])))
            path = astar(gr, layers, trk, via, (sL, sj, si), (gL, gj, gi), window)
            if path is None: failed = "%s -> %s" % (pa.GetParentFootprint().GetReference(), pb.GetParentFootprint().GetReference()); break
            runs = simplify(path); cells += len(path); nruns += len(runs)
            first = runs[0]; (x0, y0) = gr.xy(first[0][2], first[0][1]); (x1, y1) = gr.xy(first[-1][2], first[-1][1]) if len(first) > 1 else (gx, gy)
            cross = (x1 - x0) * (A[0][1] - y0) - (y1 - y0) * (A[0][0] - x0); p_side = 1 if cross > 0 else -1   # which leg is left of the centreline: the P anchor's side
            prev_end = None; lp = ln = None
            # the far end: the P anchor must lie on the same side of the centreline as at the near end, or the legs would have to cross (a twist)
            last = runs[-1]; (lx0, ly0) = gr.xy(last[0][2], last[0][1]) if len(last) > 1 else gr.xy(runs[-2][-1][2], runs[-2][-1][1]); (lx1, ly1) = gr.xy(last[-1][2], last[-1][1])
            cross_b = (lx1 - lx0) * (B[0][1] - ly0) - (ly1 - ly0) * (B[0][0] - lx0)
            if (1 if cross_b > 0 else -1) != p_side and abs(cross_b) > 1e-9 and math.hypot(B[0][0] - B[1][0], B[0][1] - B[1][1]) > 0.5:
                twist = "%s -> %s" % (pa.GetParentFootprint().GetReference(), pb.GetParentFootprint().GetReference()); break
            smoothed = [smooth(gr, [(c[1], c[2]) for c in run], ~trk[layers[run[0][0]]]) for run in runs]
            def legs_clear(sm):   # both offset legs of every run against the single-track map
                for r_i, run in enumerate(runs):
                    L = layers[run[0][0]]; pts = [gr.xy(j, i) for i, j in sm[r_i]]
                    if len(pts) == 1: pts = pts * 2
                    for poly in (offset_polyline(pts, d), offset_polyline(pts, -d)):
                        for k in range(len(poly) - 1):
                            (x1, y1), (x2, y2) = poly[k], poly[k + 1]; n = int(math.hypot(x2 - x1, y2 - y1) / gr.G) + 2
                            for q in range(n + 1):
                                u = q / n; jj, ii = gr.cell(x1 + u * (x2 - x1), y1 + u * (y2 - y1))
                                if 0 <= ii < gr.NY and 0 <= jj < gr.NX and trk1[L][ii, jj]: return False
                return True
            if not legs_clear(smoothed): smoothed = [[(c[1], c[2]) for c in run] for run in runs]   # the raw grid path: more pieces, but inside the corridor
            for r_i, run in enumerate(runs):
                L = layers[run[0][0]]; pts = [gr.xy(j, i) for i, j in smoothed[r_i]]
                if len(pts) == 1: pts = pts * 2
                lp = offset_polyline(pts, d * p_side); ln = offset_polyline(pts, -d * p_side)
                for poly, net in ((lp, net_p), (ln, net_n)):
                    for k in range(len(poly) - 1): seg(poly[k][0], poly[k][1], poly[k + 1][0], poly[k + 1][1], L, net)
                if r_i > 0:   # the layer change: two vias VIA_SPLIT from the centreline on this run's first normal, with jogs on both layers
                    (ax, ay), (bx, by) = pts[0], pts[1]; dx, dy = bx - ax, by - ay; ll = math.hypot(dx, dy) or 1.0; nx, ny = -dy / ll, dx / ll
                    Lprev = layers[runs[r_i - 1][0][0]]
                    for sign, net, poly_start, prev_poly_end in ((p_side, net_p, lp[0], prev_end[0]), (-p_side, net_n, ln[0], prev_end[1])):
                        vx, vy = ax + nx * VIA_SPLIT * sign, ay + ny * VIA_SPLIT * sign
                        seg(prev_poly_end[0], prev_poly_end[1], vx, vy, Lprev, net); via_at(vx, vy, net); seg(vx, vy, poly_start[0], poly_start[1], L, net)
                prev_end = (lp[-1], ln[-1])
            firstL = layers[runs[0][0][0]]; lastL = layers[runs[-1][0][0]]
            first_pts = [gr.xy(j, i) for i, j in smoothed[0]]; last_pts = [gr.xy(j, i) for i, j in smoothed[-1]]
            if len(first_pts) == 1: first_pts = first_pts * 2
            if len(last_pts) == 1: last_pts = last_pts * 2
            lp0, ln0 = offset_polyline(first_pts, d * p_side)[0], offset_polyline(first_pts, -d * p_side)[0]
            lp1, ln1 = offset_polyline(last_pts, d * p_side)[-1], offset_polyline(last_pts, -d * p_side)[-1]
            for (x, y, aL, obj), (ex, ey), L, net in ((A[0], lp0, firstL, net_p), (A[1], ln0, firstL, net_n), (B[0], lp1, lastL, net_p), (B[1], ln1, lastL, net_n)):
                SL = L if (aL is None or aL == L) else aL
                if aL is not None and aL != L: via_at(ex, ey, net)          # the pad sits on another layer: a via at the offset end, the stub on the pad's layer
                pm = ~trk1[SL] if SL in trk1 else None
                win2 = (gr.cell(min(ex, x) - 4, min(ey, y) - 4), gr.cell(max(ex, x) + 4, max(ey, y) + 4)); win2 = ((max(0, win2[0][0]), max(0, win2[0][1])), (min(gr.NX - 1, win2[1][0]), min(gr.NY - 1, win2[1][1])))
                sp = stub_path(gr, pm.copy(), (ex, ey), (x, y), win2) if pm is not None else None
                if sp and len(sp) >= 2:
                    for k in range(len(sp) - 1): seg(sp[k][0], sp[k][1], sp[k + 1][0], sp[k + 1][1], SL, net)
                    seg(sp[-1][0], sp[-1][1], x, y, SL, net)
                else: seg(ex, ey, x, y, SL, net)
        if twist:
            # the P leg changes side between two stations: when the far station is two identical passives (the series resistors of the two legs), swapping
            # their positions is a legal pre-route placement move that untwists the pair (the packer placed them in arbitrary order); done once, then the pair is laid again
            (pa2, na2) = next(sec[1] for sec in sections if "%s -> %s" % (sec[0][0].GetParentFootprint().GetReference(), sec[1][0].GetParentFootprint().GetReference()) == twist)
            fa, fb = pa2.GetParentFootprint(), na2.GetParentFootprint()
            if fa is not fb and fa.GetFPIDAsString() == fb.GetFPIDAsString() and fa.GetOrientation() == fb.GetOrientation() and not fa.IsLocked() and not fb.IsLocked() and stem not in swapped:
                pa_, pb_ = fa.GetPosition(), fb.GetPosition(); fa.SetPosition(pb_); fb.SetPosition(pa_); swapped.add(stem)
                for t in [t for t in b.GetTracks() if t.GetNetname() in (pn, nn)]: b.Remove(t)   # its locked pieces so far go with the retry
                report.append("SWAP  %s: %s and %s exchanged positions to untwist the pair; laid again" % (stem, fa.GetReference(), fb.GetReference())); stems.append(stem); continue
            report.append("TWIST %s: the P leg changes side between the stations %s (a crossing would be needed; left to the router)" % (stem, twist)); continue
        if failed: report.append("FAIL  %s: no centreline path for the section %s on %s at w %.2f s %.2f (%d of %d sections laid before it)" % (stem, failed, ",".join(b.GetLayerName(L) for L in layers), w, s, sections.index(next(sec for sec in sections if "%s -> %s" % (sec[0][0].GetParentFootprint().GetReference(), sec[1][0].GetParentFootprint().GetReference()) == failed)), len(sections))); continue
        laid += 1; report.append("LAID  %s: class %s w %.2f s %.2f, %d sections over %d stations, %d cells, %d runs, %d pieces added" % (stem, cls_of(pn), w, s, len(sections), len(stations), cells, nruns, added))
    out = board if not test else board.replace(".kicad_pcb", "-pairs.kicad_pcb")
    pcbnew.SaveBoard(out, b)
    for l in report: print("pair_preroute: " + l)
    print("pair_preroute: %d of %d pairs laid -> %s" % (laid, len(stems), out))
    return 0 if laid == len(stems) else 1

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
