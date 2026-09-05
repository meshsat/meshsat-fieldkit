#!/usr/bin/env python3
"""Close the connections a DRC report lists as unconnected: grid A* on F.Cu/B.Cu with vias, obstacles from every other-net copper item.
Usage: stub_router.py <board.kicad_pcb> <drc.json> [plane_nets=GND,+5V,+3V3,CELL+]"""
import sys, re, math, json, heapq, pcbnew, numpy as np
from pcbnew import VECTOR2I, FromMM
BOARD, DRC = sys.argv[1], sys.argv[2]
PLANES = set((sys.argv[3] if len(sys.argv) > 3 else "GND,+5V,+3V3,CELL+").split(","))
G = float(__import__("os").environ.get("STUB_GRID", "0.05"))   # grid, mm (STUB_GRID=0.1 for long connections)
CLR = 0.16                   # clearance to other copper, mm (board rule 0.15)
HOLE_CLR = 0.30              # clearance to a drilled pad or a mounting hole: the board's hole clearance rule is 0.25, and the 0.1 mm grid needs a margin over it (B12, 4 Sep: six 0.24 mm misses against two NPTH holes)
b = pcbnew.LoadBoard(BOARD); drc = json.load(open(DRC))
eb = b.GetBoardEdgesBoundingBox()
X0, Y0 = eb.GetLeft() / 1e6 - 1.0, eb.GetTop() / 1e6 - 1.0
NX, NY = int(eb.GetWidth() / 1e6 / G) + 20, int(eb.GetHeight() / 1e6 / G) + 20
def cell(x_mm, y_mm): return int(round((x_mm - X0) / G)), int(round((y_mm - Y0) / G))
def mm(v): return v / 1e6
LAYERS = [pcbnew.F_Cu, pcbnew.B_Cu]; INNER = [pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu]   # inner layers up to six-layer boards (B15)
# ---- rasterisation helpers (grid index j = x, i = y)
def disc(mask, cx, cy, r):
    i0, i1 = max(0, int((cy - r - Y0) / G)), min(NY - 1, int((cy + r - Y0) / G) + 1); j0, j1 = max(0, int((cx - r - X0) / G)), min(NX - 1, int((cx + r - X0) / G) + 1)
    if i1 < i0 or j1 < j0: return
    ys = (np.arange(i0, i1 + 1) * G + Y0)[:, None]; xs = (np.arange(j0, j1 + 1) * G + X0)[None, :]
    mask[i0:i1 + 1, j0:j1 + 1] |= (xs - cx) ** 2 + (ys - cy) ** 2 <= r * r
def segment(mask, ax, ay, bx, by, r):
    i0, i1 = max(0, int((min(ay, by) - r - Y0) / G)), min(NY - 1, int((max(ay, by) + r - Y0) / G) + 1); j0, j1 = max(0, int((min(ax, bx) - r - X0) / G)), min(NX - 1, int((max(ax, bx) + r - X0) / G) + 1)
    if i1 < i0 or j1 < j0: return
    ys = (np.arange(i0, i1 + 1) * G + Y0)[:, None]; xs = (np.arange(j0, j1 + 1) * G + X0)[None, :]
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else np.clip(((xs - ax) * dx + (ys - ay) * dy) / L2, 0, 1)
    mask[i0:i1 + 1, j0:j1 + 1] |= (xs - (ax + t * dx)) ** 2 + (ys - (ay + t * dy)) ** 2 <= r * r
def poly(mask, sps, grow):
    """SHAPE_POLY_SET grown by `grow` mm: rasterise by Contains on a bbox scan (coarse but exact enough at 0.1 mm)."""
    bb = sps.BBox(); r = grow
    i0, i1 = max(0, int((mm(bb.GetTop()) - r - Y0) / G)), min(NY - 1, int((mm(bb.GetBottom()) + r - Y0) / G) + 1); j0, j1 = max(0, int((mm(bb.GetLeft()) - r - X0) / G)), min(NX - 1, int((mm(bb.GetRight()) + r - X0) / G) + 1)
    if i1 < i0 or j1 < j0: return
    ys = (np.arange(i0, i1 + 1) * G + Y0)[:, None]; xs = (np.arange(j0, j1 + 1) * G + X0)[None, :]
    inside = np.zeros((i1 - i0 + 1, j1 - j0 + 1), dtype=bool)
    grown = pcbnew.SHAPE_POLY_SET(sps); 
    if grow > 0:
        try: grown.Inflate(FromMM(grow), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, FromMM(0.05))
        except Exception:
            try: grown.Inflate(FromMM(grow), 16)
            except Exception: pass
    for ii in range(inside.shape[0]):
        for jj in range(inside.shape[1]):
            if grown.Contains(VECTOR2I(FromMM(X0 + (j0 + jj) * G), FromMM(Y0 + (i0 + ii) * G))): inside[ii, jj] = True
    mask[i0:i1 + 1, j0:j1 + 1] |= inside
# ---- parse the unconnected pairs
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
def item_of(it):
    d = it.get("description", ""); pos = it.get("pos", {}); x, y = pos.get("x"), pos.get("y")
    m = re.match(r"(?:PTH pad|Pad) (\S+) \[([^\]]+)\] of (\S+)(?: on (\S+))?", d)
    if m:
        fp = fps.get(m.group(3)); pad = next((p for p in fp.Pads() if p.GetNumber() == m.group(1)), None) if fp else None
        return dict(kind="pad", net=m.group(2), pad=pad, x=x, y=y, layer=(m.group(4) or "*").rstrip(","))   # PTH pads carry no layer in the DRC text
    m = re.match(r"Via \[([^\]]+)\]", d)
    if m: return dict(kind="via", net=m.group(1), x=x, y=y, layer="*")
    m = re.match(r"Track \[([^\]]+)\] on (\S+)", d)
    if m: return dict(kind="track", net=m.group(1), x=x, y=y, layer=m.group(2).rstrip(","))
    return None
pairs = []
for v in drc.get("unconnected_items", []):
    its = [item_of(i) for i in v.get("items", [])]
    if len(its) == 2 and all(its): pairs.append(its)
print("unconnected pairs:", len(pairs))
def netname(n): return n[1:] if n.startswith("/") else n
# ---- build obstacle maps once per net (other-net copper)
def build_maps(net):
    trk = {L: np.zeros((NY, NX), dtype=bool) for L in LAYERS}    # track-centre forbidden (inflated by CLR + w/2)
    via = np.zeros((NY, NX), dtype=bool)                          # via-centre forbidden (inflated by CLR + via_r on every layer)
    w2, vr = TW / 2, VIA_D / 2
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):   # hole to hole against drilled pads of any net
                c = p.GetPosition(); d = p.GetDrillSize(); disc(via, mm(c.x), mm(c.y), mm(max(d.x, d.y)) / 2 + VIA_DR / 2 + 0.30)
            if p.GetNetname() == net: continue
            anyL = next((L for L in LAYERS + INNER if p.IsOnLayer(L)), pcbnew.F_Cu)
            for L in LAYERS:
                if p.IsOnLayer(L): poly(trk[L], p.GetEffectivePolygon(L), (HOLE_CLR if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) else CLR) + w2)
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) or any(p.IsOnLayer(L) for L in INNER + LAYERS): poly(via, p.GetEffectivePolygon(anyL), CLR + vr)
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":                                  # hole to hole (0.30 mm) against every via, its own net included (B13, 5 Sep: two SDA vias 0.175 mm apart)
            c = t.GetPosition(); disc(via, mm(c.x), mm(c.y), mm(t.GetDrillValue()) / 2 + VIA_DR / 2 + 0.30)
        if t.GetNetname() == net: continue
        if t.GetClass() == "PCB_VIA":
            c = t.GetPosition(); r = mm(t.GetWidth(pcbnew.F_Cu)) / 2
            for L in LAYERS: disc(trk[L], mm(c.x), mm(c.y), r + CLR + w2)
            disc(via, mm(c.x), mm(c.y), r + CLR + vr)
        else:
            a, e = t.GetStart(), t.GetEnd(); r = mm(t.GetWidth()) / 2; L = t.GetLayer()
            if L in trk: segment(trk[L], mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + CLR + w2)
            segment(via, mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + CLR + vr)
    for z in b.Zones():
        if z.GetIsRuleArea():
            for L in LAYERS: poly(trk[L], z.Outline(), CLR + w2)
            poly(via, z.Outline(), CLR + vr)
    for d in b.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_CIRCLE:
            c = d.GetCenter(); r = mm(d.GetRadius())
            for L in LAYERS: disc(trk[L], mm(c.x), mm(c.y), r + 0.5 + w2)
            disc(via, mm(c.x), mm(c.y), r + 0.5 + vr)
    m = int(0.6 / G) + 12   # board margin (1 mm grid offset + 0.6 mm edge clearance)
    for M in list(trk.values()) + [via]:
        M[:m, :] = True; M[-m:, :] = True; M[:, :m] = True; M[:, -m:] = True
    return trk, via
def copper_cells(item, net):
    """Cells covered by the item's own copper, per layer."""
    out = {}
    if item["kind"] == "pad" and item["pad"] is not None:
        for L in LAYERS:
            if item["pad"].IsOnLayer(L):
                M = np.zeros((NY, NX), dtype=bool); poly(M, item["pad"].GetEffectivePolygon(L), 0.0); out[L] = M
    elif item["kind"] == "via":
        for L in LAYERS:
            M = np.zeros((NY, NX), dtype=bool); disc(M, item["x"], item["y"], 0.25); out[L] = M
    else:
        L = pcbnew.F_Cu if item["layer"] == "F.Cu" else pcbnew.B_Cu if item["layer"] == "B.Cu" else None
        if L is not None:
            M = np.zeros((NY, NX), dtype=bool); disc(M, item["x"], item["y"], 0.15); out[L] = M
        else:                                   # inner layer: every cell along the segment(s) of this net near the point, on both outer layers (reached with a via)
            lname = item["layer"]; M = np.zeros((NY, NX), dtype=bool); found = 0
            for t in b.GetTracks():
                if t.GetClass() != "PCB_TRACK" or t.GetNetname() != net or b.GetLayerName(t.GetLayer()) != lname: continue
                a, e = t.GetStart(), t.GetEnd(); dx, dy = mm(e.x) - mm(a.x), mm(e.y) - mm(a.y); L2 = dx * dx + dy * dy
                u = 0 if L2 == 0 else max(0, min(1, ((item["x"] - mm(a.x)) * dx + (item["y"] - mm(a.y)) * dy) / L2))
                if math.hypot(item["x"] - (mm(a.x) + u * dx), item["y"] - (mm(a.y) + u * dy)) < 0.3:
                    segment(M, mm(a.x), mm(a.y), mm(e.x), mm(e.y), 0.05); found += 1
            item["inner"] = True; out[pcbnew.F_Cu] = M.copy(); out[pcbnew.B_Cu] = M.copy()
    return out

INNER_GOAL = None
def other_cluster_cells(a, net, viamap):
    global INNER_GOAL; INNER_GOAL = np.zeros((NY, NX), dtype=bool)
    """Rasterise the copper of every same-net item that is NOT geometrically connected to the source pad (union-find over touching items)."""
    items = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == net: items.append(("pad", p))
    for t in b.GetTracks():
        if t.GetNetname() == net: items.append(("via" if t.GetClass() == "PCB_VIA" else "trk", t))
    parent = list(range(len(items)))
    def find(i):
        while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
        return i
    def union(i, j): parent[find(i)] = find(j)
    def pts(kind, it):
        if kind == "trk": return [it.GetStart(), it.GetEnd()]
        return [it.GetPosition()]
    def touches(ki, ii, kj, ij):
        if ki == "pad" and kj == "pad": return False
        if ki == "pad": kj, ij, ki, ii = ki, ii, kj, ij
        # ii is a track/via, ij a pad or track/via
        for q in pts(ki, ii):
            if kj == "pad":
                if ij.HitTest(q): return True
            else:
                for r in pts(kj, ij):
                    if abs(q.x - r.x) < 2000 and abs(q.y - r.y) < 2000: return True
                if kj == "via" and abs(q.x - ij.GetPosition().x) < FromMM(0.35) and abs(q.y - ij.GetPosition().y) < FromMM(0.35): return True
        if ki == "via" and kj == "trk":
            for r in pts(kj, ij):
                if abs(r.x - ii.GetPosition().x) < FromMM(0.35) and abs(r.y - ii.GetPosition().y) < FromMM(0.35): return True
        return False
    n = len(items)
    for i in range(n):
        ki, ii = items[i]; bi = ii.GetBoundingBox()
        for j in range(i + 1, n):
            kj, ij = items[j]
            if not bi.Intersects(ij.GetBoundingBox()): continue
            if touches(ki, ii, kj, ij) or touches(kj, ij, ki, ii): union(i, j)
    if a["kind"] == "pad" and a.get("pad") is not None:
        src_idx = next(i for i, (k, it) in enumerate(items) if k == "pad" and it.GetPosition() == a["pad"].GetPosition() and it.GetParentFootprint().GetReference() == a["pad"].GetParentFootprint().GetReference())
    else:                                                          # source is a via or a track end (ripped-up runs): nearest same-net via/track to the reported position
        ax, ay = FromMM(a["x"]), FromMM(a["y"])
        def d_item(it):
            k, o = it
            if k == "pad": return float("inf")
            ps = [o.GetPosition()] if k == "via" else [o.GetStart(), o.GetEnd()]
            return min(((q.x - ax) ** 2 + (q.y - ay) ** 2) ** 0.5 for q in ps)
        src_idx = min(range(len(items)), key=lambda i: d_item(items[i]))
    root = find(src_idx); out = {L: np.zeros((NY, NX), dtype=bool) for L in LAYERS}; cnt = 0
    for i, (k, it) in enumerate(items):
        if find(i) == root: continue
        cnt += 1
        if k == "pad":
            for L in LAYERS:
                if it.IsOnLayer(L): poly(out[L], it.GetEffectivePolygon(L), 0.0)
        elif k == "via":
            c = it.GetPosition()
            for L in LAYERS: disc(out[L], mm(c.x), mm(c.y), 0.2)
        else:
            L = it.GetLayer(); s_, e_ = it.GetStart(), it.GetEnd(); r = mm(it.GetWidth()) / 2
            if L in out: segment(out[L], mm(s_.x), mm(s_.y), mm(e_.x), mm(e_.y), r)
            else:
                M = np.zeros((NY, NX), dtype=bool); segment(M, mm(s_.x), mm(s_.y), mm(e_.x), mm(e_.y), 0.05); M &= ~viamap
                for L2 in LAYERS: out[L2] |= M
                INNER_GOAL[...] |= M
    print("  other-cluster items: %d of %d" % (cnt, n))
    return out

def route(net, src, goal_cells, trk, via, window):
    (jmin, imin), (jmax, imax) = window
    LI = {pcbnew.F_Cu: 0, pcbnew.B_Cu: 1}; LR = {0: pcbnew.F_Cu, 1: pcbnew.B_Cu}
    starts = [(LI[L], i, j) for L, M in src.items() for i, j in zip(*np.nonzero(M)) if not trk[L][i, j] or True]
    goal = np.zeros((2, NY, NX), dtype=bool)
    for L, M in goal_cells.items(): goal[LI[L]] |= M
    passable = {0: ~trk[pcbnew.F_Cu], 1: ~trk[pcbnew.B_Cu]}
    for L, M in src.items(): passable[LI[L]] |= M          # own pad copper is always enterable
    for L, M in goal_cells.items(): passable[LI[L]] |= M
    dist = {}; prev = {}; pq = []
    for s in starts:
        dist[s] = 0.0; heapq.heappush(pq, (0.0, s))
    steps = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
    found = None; n = 0
    while pq:
        d, s = heapq.heappop(pq)
        if d > dist.get(s, 1e18): continue
        L, i, j = s; n += 1
        if goal[L, i, j]: found = s; break
        if n > int(__import__("os").environ.get("STUB_MAXN", "4000000")): break
        for di, dj, c in steps:
            ni, nj = i + di, j + dj
            if not (imin <= ni <= imax and jmin <= nj <= jmax): continue
            if not passable[L][ni, nj]: continue
            if di and dj and not (passable[L][i, nj] and passable[L][ni, j]): continue
            nd = d + c; t = (L, ni, nj)
            if nd < dist.get(t, 1e18): dist[t] = nd; prev[t] = s; heapq.heappush(pq, (nd, t))
        if not via[i, j] and not src_is_here(src, L, i, j):
            oL = 1 - L
            if passable[oL][i, j]:
                nd = d + VIA_COST; t = (oL, i, j)
                if nd < dist.get(t, 1e18): dist[t] = nd; prev[t] = s; heapq.heappush(pq, (nd, t))
    if found is None: return None
    path = [found]
    while path[-1] in prev: path.append(prev[path[-1]])
    return list(reversed(path))
def src_is_here(src, L, i, j):
    M = src.get({0: pcbnew.F_Cu, 1: pcbnew.B_Cu}[L])
    return M is not None and M[i, j]
def emit(net_item, path):
    net = net_item; LR = {0: pcbnew.F_Cu, 1: pcbnew.B_Cu}
    # merge straight runs
    segs = []; cur = [path[0]]
    for k in range(1, len(path)):
        a, c = path[k - 1], path[k]
        if a[0] != c[0]:                      # via
            segs.append(("trk", cur)); segs.append(("via", c)); cur = [c]; continue
        if len(cur) >= 2:
            p0, p1 = cur[-2], cur[-1]
            if (p1[1] - p0[1], p1[2] - p0[2]) == (c[1] - p1[1], c[2] - p1[2]): cur[-1] = c; continue
        cur.append(c)
    segs.append(("trk", cur))
    nt = nv = 0
    for kind, v in segs:
        if kind == "via":
            L, i, j = v; via = pcbnew.PCB_VIA(b); via.SetPosition(VECTOR2I(FromMM(float(X0 + j * G)), FromMM(float(Y0 + i * G)))); via.SetDrill(FromMM(VIA_DR)); via.SetWidth(FromMM(VIA_D))
            via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(net); b.Add(via); nv += 1
        else:
            for k in range(1, len(v)):
                a, c = v[k - 1], v[k]
                if (a[1], a[2]) == (c[1], c[2]): continue
                t = pcbnew.PCB_TRACK(b); t.SetStart(VECTOR2I(FromMM(float(X0 + a[2] * G)), FromMM(float(Y0 + a[1] * G)))); t.SetEnd(VECTOR2I(FromMM(float(X0 + c[2] * G)), FromMM(float(Y0 + c[1] * G))))
                t.SetWidth(FromMM(TW)); t.SetLayer(LR[a[0]]); t.SetNet(net); b.Add(t); nt += 1
    return nt, nv
closed = 0
for it1, it2 in pairs:
    net = it1["net"]; netobj = b.FindNet(net)
    if netobj is None or netobj.GetNetCode() <= 0: net = netname(net); netobj = b.FindNet(net)
    if netobj is None or netobj.GetNetCode() <= 0: print("  skip: net not found", it1["net"]); continue
    net = netobj.GetNetname()
    TW = 0.25; VIA_D, VIA_DR, VIA_COST = 0.6, 0.3, 50.0
    try:
        nc = netobj.GetNetClass(); TW = max(0.25, min(mm(nc.GetTrackWidth()), 0.4)); VIA_D = max(0.6, mm(nc.GetViaDiameter())); VIA_DR = max(0.3, mm(nc.GetViaDrill()))
    except Exception: pass
    fine = [it for it in (it1, it2) if it["kind"] == "pad" and it["pad"] is not None and min(mm(it["pad"].GetSize().x), mm(it["pad"].GetSize().y)) < 0.4]
    if fine: TW = 0.2                                              # leaving a fine-pitch pad: thinnest allowed track
    trk, via = build_maps(net)
    # source = the pad if there is one, else the other item; goal = other item, or any via-able cell for plane nets
    a, c = (it1, it2) if it1["kind"] == "pad" else (it2, it1)
    src = copper_cells(a, net)
    if not src: print("  skip: no source copper for", a); continue
    if a.get("inner"):                                             # the source is an inner-layer track: start only where the joining via may stand
        for L in list(src): src[L] &= ~via
        if not any(M.any() for M in src.values()): print("  skip: no via-legal cell on the inner-layer source", a); continue
    if netname(net) in PLANES and not (a["kind"] == "pad" and c["kind"] == "pad"):   # pad-to-pad on a plane net: route it, do not just drop a via
        goal_cells = {pcbnew.F_Cu: ~via, pcbnew.B_Cu: ~via}
        for L in LAYERS: goal_cells[L] &= ~trk[L]
        win = 8.0
    else:
        goal_cells = other_cluster_cells(a, net, via); win = 15.0
        if not any(M.any() for M in goal_cells.values()):
            goal_cells = copper_cells(c, net)
            if c.get("inner"):
                for L in LAYERS: goal_cells[L] &= ~via
                INNER_GOAL = goal_cells[pcbnew.F_Cu] | goal_cells[pcbnew.B_Cu]
        else:
            c = dict(c); c["inner"] = True                      # any goal may sit on an inner layer or need a via: allow the closing via
    xs = [a["x"], c["x"]]; ys = [a["y"], c["y"]]
    window = (cell(min(xs) - win, min(ys) - win), cell(max(xs) + win, max(ys) + win))
    window = ((max(0, window[0][0]), max(0, window[0][1])), (min(NX - 1, window[1][0]), min(NY - 1, window[1][1])))
    ns = sum(int(M.sum()) for M in src.values()); (jmin, imin), (jmax, imax) = window
    ng = sum(int((M[imin:imax + 1, jmin:jmax + 1]).sum()) for M in goal_cells.values())
    nfree = sum(int((~trk[L][imin:imax + 1, jmin:jmax + 1]).sum()) for L in LAYERS)
    print("  %s: source cells %d, goal cells in window %d, free cells in window %d, window %s" % (net, ns, ng, nfree, window))
    path = route(net, src, goal_cells, trk, via, window)
    if path is None:
        print("  FAILED: %s  %s -> %s" % (net, a.get("kind"), c.get("kind")))
        Ls = next(iter(src)); jc, ic = cell(a["x"], a["y"]); R = int(2.0 / G)
        for i in range(ic - R, ic + R + 1, 2):
            row = ""
            for j in range(jc - R, jc + R + 1, 2):
                if not (0 <= i < NY and 0 <= j < NX): row += " "; continue
                row += "S" if src[Ls][i, j] else ("G" if any(M[i, j] for M in goal_cells.values()) else ("#" if trk[Ls][i, j] else "."))
            print("    " + row)
        continue
    nt, nv = emit(netobj, path)
    L_end, i_end, j_end = path[-1]
    end_is_inner = c.get("inner") and INNER_GOAL is not None and INNER_GOAL[i_end, j_end]
    last_is_via = len(path) >= 2 and path[-1][0] != path[-2][0]   # the path's own last step already put a via on the end cell
    if ((netname(net) in PLANES and not (a["kind"] == "pad" and c["kind"] == "pad")) or end_is_inner) and not last_is_via:   # plane or inner-track goal reached on an outer layer: drop a via at the end (A19, 4 Sep: a path that changed layer half-way reached an In2 track on B.Cu and got no closing via because the old test was "no via in the path")
        L, i, j = path[-1]; v2 = pcbnew.PCB_VIA(b); v2.SetPosition(VECTOR2I(FromMM(float(X0 + j * G)), FromMM(float(Y0 + i * G)))); v2.SetDrill(FromMM(VIA_DR)); v2.SetWidth(FromMM(VIA_D))
        v2.SetViaType(pcbnew.VIATYPE_THROUGH); v2.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v2.SetNet(netobj); b.Add(v2); nv += 1
    first_is_via = len(path) >= 2 and path[0][0] != path[1][0]
    if a.get("inner") and not first_is_via:                        # inner-layer source reached on an outer layer: the joining via at the start (A19, 4 Sep: a B.Cu stub end 0.02 mm from an In2 track stayed open)
        L, i, j = path[0]; v3 = pcbnew.PCB_VIA(b); v3.SetPosition(VECTOR2I(FromMM(float(X0 + j * G)), FromMM(float(Y0 + i * G)))); v3.SetDrill(FromMM(VIA_DR)); v3.SetWidth(FromMM(VIA_D))
        v3.SetViaType(pcbnew.VIATYPE_THROUGH); v3.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v3.SetNet(netobj); b.Add(v3); nv += 1
    closed += 1; print("  closed %s: %d tracks, %d vias, path %d cells" % (net, nt, nv, len(path)))
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(BOARD, b); print("stub_router: closed %d of %d" % (closed, len(pairs)))
