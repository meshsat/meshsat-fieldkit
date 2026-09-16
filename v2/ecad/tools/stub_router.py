#!/usr/bin/env python3
"""Close the connections a DRC report lists as unconnected: grid A* on F.Cu/B.Cu with vias, obstacles from every other-net copper item.
Usage: stub_router.py <board.kicad_pcb> <drc.json> [plane_nets=GND,+5V,+3V3,CELL+]"""
import os, sys, re, math, json, heapq, pcbnew, numpy as np
import netclass
from pcbnew import VECTOR2I, FromMM
BOARD, DRC = sys.argv[1], sys.argv[2]
_PLANES_ARG = sys.argv[3] if len(sys.argv) > 3 else None   # resolved against the board below
G = float(__import__("os").environ.get("STUB_GRID", "0.05"))
WIN_SCALE = float(__import__("os").environ.get("STUB_WIN_SCALE", "1.0"))   # 7 Sep 2026: the search window around the two ends (8 or 15 mm) times this; A22 closes its last gaps at 2.5   # grid, mm (STUB_GRID=0.1 for long connections)
CLR = 0.16                   # the fallback clearance to other copper, mm (board rule 0.15); the real bar is per pair of nets, below
HOLE_CLR = 0.30              # clearance to a drilled pad or a mounting hole: the board's hole clearance rule is 0.25, and the 0.1 mm grid needs a margin over it (B12, 4 Sep: six 0.24 mm misses against two NPTH holes)
b = pcbnew.LoadBoard(BOARD); drc = json.load(open(DRC))
# 12 September 2026 (MESHSAT-862): PLANES WAS A HARD-CODED STRING, "GND,+5V,+3V3,CELL+", and a net in it takes a
# different branch below: its goal becomes ANY cell a via may stand in, on the assumption that the plane carries
# the rest of the connection. A24 has no +3V3 pour. So for /+3V3 the router never searched for the other cluster
# at all: it dropped one via beside the source and reported "closed: 0 tracks, 1 vias, path 1 cells", twice, in two
# separate runs, and the DRC named the same open pair after both. The set is the nets that have a FILLED zone on
# this board, which is the only thing that makes the assumption true; the argument still overrides it.
PLANES = (set(_PLANES_ARG.split(",")) if _PLANES_ARG else
          {(z.GetNetname()[1:] if z.GetNetname().startswith("/") else z.GetNetname())
           for z in b.Zones() if not z.GetIsRuleArea() and z.GetFilledArea() > 0})
print("stub_router: plane nets on this board: %s" % (", ".join(sorted(PLANES)) or "none"))
eb = b.GetBoardEdgesBoundingBox()
X0, Y0 = eb.GetLeft() / 1e6 - 1.0, eb.GetTop() / 1e6 - 1.0
NX, NY = int(eb.GetWidth() / 1e6 / G) + 20, int(eb.GetHeight() / 1e6 / G) + 20
def cell(x_mm, y_mm): return int(round((x_mm - X0) / G)), int(round((y_mm - Y0) / G))
def mm(v): return v / 1e6
_ALL = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "In3.Cu": pcbnew.In3_Cu, "In4.Cu": pcbnew.In4_Cu, "B.Cu": pcbnew.B_Cu}
# STUB_LAYERS (6 Sep 2026): the layers the stub router may route on, default the two outer ones; B15 passes F.Cu,In2.Cu,In3.Cu,B.Cu (In1 and In4 are planes).
LAYERS = [_ALL[x.strip()] for x in __import__("os").environ.get("STUB_LAYERS", "F.Cu,B.Cu").split(",") if x.strip() in _ALL] or [pcbnew.F_Cu, pcbnew.B_Cu]
INNER = [l for l in _ALL.values() if l not in LAYERS]
def _pad_layer(p):
    """A copper layer the pad is REALLY on. GetEffectivePolygon(layer) on a layer the pad does not have crashes the
    binding: with STUB_LAYERS naming inner layers only (A24, 9 Sep 2026) the old fallback handed an inner layer to a
    front-side SMD pad and the process died with a segmentation fault, exit 139, and no Python traceback at all."""
    for L in LAYERS + INNER:
        if p.IsOnLayer(L): return L
    seq = list(p.GetLayerSet().CuStack()) if hasattr(p.GetLayerSet(), "CuStack") else []
    return seq[0] if seq else pcbnew.F_Cu
LI = {L: i for i, L in enumerate(LAYERS)}; LR = {i: L for L, i in LI.items()}
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
def zpoly(mask, sps, grow):
    """A FILLED zone rasterised fast, because a pour is board-sized and `poly` asks Contains per cell.

    The pre-router learnt this on 10 September 2026 and the lesson travels with the code: matplotlib fills every
    sub-path whatever its winding, so a polygon's HOLES cannot be sub-paths of the same Path or the whole
    outline comes out solid. Outlines and holes are rasterised separately and the holes are subtracted, and the
    grow is applied by KiCad's own Inflate before any of that, so the geometry stays KiCad's."""
    try:
        from matplotlib.path import Path as _Path
    except Exception:
        return poly(mask, sps, grow)      # no matplotlib here: correct and slow beats wrong and fast
    g = pcbnew.SHAPE_POLY_SET(sps)
    if grow > 0:
        try: g.Inflate(FromMM(grow), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, FromMM(0.05))
        except Exception:
            try: g.Inflate(FromMM(grow), 16)
            except Exception: pass
    bb = g.BBox()
    i0, i1 = max(0, int((mm(bb.GetTop()) - Y0) / G) - 1), min(NY - 1, int((mm(bb.GetBottom()) - Y0) / G) + 1)
    j0, j1 = max(0, int((mm(bb.GetLeft()) - X0) / G) - 1), min(NX - 1, int((mm(bb.GetRight()) - X0) / G) + 1)
    if i1 < i0 or j1 < j0: return
    ys = np.arange(i0, i1 + 1) * G + Y0; xs = np.arange(j0, j1 + 1) * G + X0
    XX, YY = np.meshgrid(xs, ys)
    pts = np.column_stack([XX.ravel(), YY.ravel()])
    inside = np.zeros(pts.shape[0], dtype=bool)
    for oi in range(g.OutlineCount()):
        ring = g.Outline(oi)
        pv = [(mm(ring.CPoint(k).x), mm(ring.CPoint(k).y)) for k in range(ring.PointCount())]
        if len(pv) >= 3: inside |= _Path(pv).contains_points(pts)
        for hi in range(g.HoleCount(oi)):
            h = g.Hole(oi, hi)
            hv = [(mm(h.CPoint(k).x), mm(h.CPoint(k).y)) for k in range(h.PointCount())]
            if len(hv) >= 3: inside &= ~_Path(hv).contains_points(pts)
    mask[i0:i1 + 1, j0:j1 + 1] |= inside.reshape(XX.shape)


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
def netname(n): return n[1:] if n.startswith("/") else n
# STUB_NETS (14 September 2026): only these nets are attempted, everything else in the report is left alone.
# It is what makes this tool usable BEFORE the route as well as after it. Board C's `/EPD_SDA` is 249 mm from
# J_EPD pin 14 to U3 pad 5 across a panel that is a ring, and on the ROUTED board there is no lane left for it:
# four routes in a row left it, or left another net exactly like it, because the strips are the only corridors
# and whoever gets there first takes them. On the PLACED board those strips are empty. A search that cannot
# find a path through other people's copper finds one easily before they lay it, and a locked lane is
# something the router then works around, which is the `bus_a21.py` pattern of 5 September with the waypoints
# searched instead of typed.
_WANT = {n.strip().lstrip("/") for n in __import__("os").environ.get("STUB_NETS", "").split(",") if n.strip()}
for v in drc.get("unconnected_items", []):
    its = [item_of(i) for i in v.get("items", [])]
    if len(its) == 2 and all(its):
        if _WANT and netname(its[0]["net"]) not in _WANT: continue
        pairs.append(its)
if _WANT: print("stub_router: STUB_NETS names %d net(s); %d of the report's pairs are on them" % (len(_WANT), len(pairs)))
print("unconnected pairs:", len(pairs))
if not pairs:
    # 15 September 2026 (MESHSAT-862): C17's second re-finish, on a board already at 0 unrouted, died here with exit 139 and
    # took the finish with it (a stub-router crash refuses the board by rule). With no pair to close there is no map to
    # build, no fill to run and nothing to save; the board is untouched, and the interpreter is left before pcbnew's
    # teardown can segfault it, the way direct_close leaves its trials.
    print("stub_router: closed 0 of 0 (nothing to close, the board is untouched)"); sys.stdout.flush(); os._exit(0)
# ---- THE CLEARANCE BETWEEN TWO NETS IS THE LARGER OF THEIR TWO CLASSES', NEVER A LITERAL (14 September 2026).
# The width and the via of a closure were taught to read the net's class on 13 September and the CLEARANCE was
# left as 0.16 mm for every net of every board. On C that is wrong in the direction that costs connections: the
# panel's own classes are finer than 0.16, so a lane laid at the class number reads as blocked, and a
# board-wide 0.1 mm search for /PWM1 and /HB2 came back with no path at all in eight minutes on a board whose
# two ends are both in open ground. The bar is the class clearance plus one hundredth of a millimetre, the same
# margin over the rule that 0.16 was over the board's 0.15; CLR stays the answer for a net that cannot be
# resolved, and the board's own DRC still decides, through `stub_accept`, whether a closure is kept.
_PRO_CLASSES, _ASSIGN = {}, None
try:
    _pro_j = __import__("json").load(open(__import__("os").path.splitext(BOARD)[0] + ".kicad_pro"))
    _ns_j = _pro_j.get("net_settings", {})
    _ASSIGN = _ns_j.get("netclass_assignments")
    for _c in _ns_j.get("classes", []):
        if _c.get("name") and _c.get("clearance") is not None: _PRO_CLASSES[_c["name"]] = float(_c["clearance"])
except Exception: pass
_CLR_CACHE = {}
def net_clr(n):
    """the class clearance of one net plus the grid's margin; CLR when no class resolves"""
    n = netname(n or "")
    if n not in _CLR_CACHE:
        v = None
        try:
            cl = netclass.class_of(_ASSIGN, n)
            if cl and cl in _PRO_CLASSES: v = _PRO_CLASSES[cl]
        except Exception: v = None
        if v is None: v = _PRO_CLASSES.get("Default")
        _CLR_CACHE[n] = CLR if v is None else v + 0.01
    return _CLR_CACHE[n]
# ---- build obstacle maps once per net (other-net copper)
def build_maps(net):
    trk = {L: np.zeros((NY, NX), dtype=bool) for L in LAYERS}    # track-centre forbidden (inflated by the clearance + w/2)
    via = np.zeros((NY, NX), dtype=bool)                          # via-centre forbidden (inflated by the clearance + via_r on every layer)
    w2, vr = TW / 2, VIA_D / 2
    _me = net_clr(net)
    def clr_to(other): return max(_me, net_clr(other))   # KiCad's own rule: the larger of the two classes decides
    print("  %s: clearance %.3f mm from its own class, and per obstacle the larger of the two" % (net, _me))
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):   # hole to hole against drilled pads of any net
                c = p.GetPosition(); d = p.GetDrillSize(); disc(via, mm(c.x), mm(c.y), mm(max(d.x, d.y)) / 2 + VIA_DR / 2 + 0.30)
            if p.GetNetname() == net: continue
            anyL = _pad_layer(p)
            for L in LAYERS:
                if p.IsOnLayer(L): poly(trk[L], p.GetEffectivePolygon(L), (HOLE_CLR if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) else clr_to(p.GetNetname())) + w2)
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) or any(p.IsOnLayer(L) for L in INNER + LAYERS): poly(via, p.GetEffectivePolygon(anyL), clr_to(p.GetNetname()) + vr)
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":                                  # hole to hole (0.30 mm) against every via, its own net included (B13, 5 Sep: two SDA vias 0.175 mm apart)
            c = t.GetPosition(); disc(via, mm(c.x), mm(c.y), mm(t.GetDrillValue()) / 2 + VIA_DR / 2 + 0.30)
        if t.GetNetname() == net: continue
        if t.GetClass() == "PCB_VIA":
            c = t.GetPosition(); r = mm(t.GetWidth(pcbnew.F_Cu)) / 2
            _c = clr_to(t.GetNetname())
            for L in LAYERS: disc(trk[L], mm(c.x), mm(c.y), r + _c + w2)
            disc(via, mm(c.x), mm(c.y), r + _c + vr)
        else:
            a, e = t.GetStart(), t.GetEnd(); r = mm(t.GetWidth()) / 2; L = t.GetLayer()
            _c = clr_to(t.GetNetname())
            if L in trk: segment(trk[L], mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + _c + w2)
            segment(via, mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + _c + vr)
    for z in b.Zones():
        if z.GetIsRuleArea():
            for L in LAYERS:
                if z.IsOnLayer(L) and z.GetDoNotAllowTracks(): poly(trk[L], z.Outline(), CLR + w2)   # a rule area binds only on its own layers (the board-wide In1/In4 track keep-outs must not block In2/In3)
            if z.GetDoNotAllowVias(): poly(via, z.Outline(), CLR + vr)
            continue
        # EVERY FILLED POUR OF ANOTHER NET IS AN OBSTACLE, and until 16 September 2026 not one of them was in
        # this map. Only tracks, vias, pads and rule areas were, so a closure was free to run straight through
        # a ground plane: on board A that is most of the board. The closures were not silently accepted, which
        # is why this survived so long. They were laid, KiCad's connectivity was asked, the count went UP
        # (/POE_EN 13 unconnected to 114, /PD_EN 13 to 79: a short merges clusters and the ratsnest explodes),
        # and every piece came back off with "the path reached a goal CELL whose copper it does not touch".
        # The tool had been searching a board it could not see, and its own guard was the only thing standing
        # between that and a shorted board. Twelve of board A's opens sat behind this.
        if z.GetFilledArea() <= 0 or netname(z.GetNetname()) == netname(net): continue
        _c = clr_to(z.GetNetname())
        for L in LAYERS:
            if not z.IsOnLayer(L): continue
            try: fp_ = z.GetFilledPolysList(L)
            except Exception: fp_ = None
            if fp_ is None or fp_.OutlineCount() == 0: continue
            zpoly(trk[L], fp_, _c + w2)
            zpoly(via, fp_, _c + vr)
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
        L = _ALL.get(item["layer"]); L = L if L in LAYERS else None
        if L is not None:
            # 14 September 2026: THE GOAL IS THE TRACK'S COPPER, NOT A DISC AROUND THE POINT THE DRC NAMED. A 0.15 mm
            # disc at a track end let the path stop at a cell up to 0.15 mm off the copper, and a 0.2 mm closure
            # ending there overlaps nothing: the closure is laid, KiCad's connectivity does not move, and the
            # pieces are taken back off with "reached a goal cell whose copper it does not touch". The segments
            # of this net that pass within 0.3 mm of the named point are stamped at their own width, which is
            # what the other-cluster goal already does for every track it holds; the disc stays as the fallback
            # for a point no segment is near.
            M = np.zeros((NY, NX), dtype=bool); found = 0
            for t in b.GetTracks():
                if t.GetClass() != "PCB_TRACK" or t.GetNetname() != net or t.GetLayer() != L: continue
                a, e = t.GetStart(), t.GetEnd(); dx, dy = mm(e.x) - mm(a.x), mm(e.y) - mm(a.y); L2 = dx * dx + dy * dy
                u = 0 if L2 == 0 else max(0, min(1, ((item["x"] - mm(a.x)) * dx + (item["y"] - mm(a.y)) * dy) / L2))
                if math.hypot(item["x"] - (mm(a.x) + u * dx), item["y"] - (mm(a.y) + u * dy)) < 0.3:
                    segment(M, mm(a.x), mm(a.y), mm(e.x), mm(e.y), mm(t.GetWidth()) / 2); found += 1
            if not found: disc(M, item["x"], item["y"], 0.15)
            out[L] = M
        else:                                   # inner layer: every cell along the segment(s) of this net near the point, on both outer layers (reached with a via)
            lname = item["layer"]; M = np.zeros((NY, NX), dtype=bool); found = 0
            for t in b.GetTracks():
                if t.GetClass() != "PCB_TRACK" or t.GetNetname() != net or b.GetLayerName(t.GetLayer()) != lname: continue
                a, e = t.GetStart(), t.GetEnd(); dx, dy = mm(e.x) - mm(a.x), mm(e.y) - mm(a.y); L2 = dx * dx + dy * dy
                u = 0 if L2 == 0 else max(0, min(1, ((item["x"] - mm(a.x)) * dx + (item["y"] - mm(a.y)) * dy) / L2))
                if math.hypot(item["x"] - (mm(a.x) + u * dx), item["y"] - (mm(a.y) + u * dy)) < 0.3:
                    segment(M, mm(a.x), mm(a.y), mm(e.x), mm(e.y), 0.05); found += 1
            item["inner"] = True
            for L2 in LAYERS: out[L2] = M.copy()
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
                # A TRACK END ON ANOTHER TRACK'S BODY IS A CONNECTION, and this test only ever compared ENDS
                # (16 September 2026). KiCad connects a T-junction, and the record already carries the lesson
                # for post_fix_b13, which cut such a foot off because it read the same way. Here the effect is
                # the opposite and quieter: the union-find splits ONE KiCad cluster into two, the search is
                # given a goal that is already connected to its source, the closure is laid, KiCad's count does
                # not move and the piece comes back off. That is board A's A37 finish refusing a closure whose
                # two ends it measured at 0.000 mm from the net's own copper, with 22 unconnected before and
                # 22 after. A cluster test stricter than the connectivity it stands for invents work.
                if kj == "trk" and ij.GetClass() == "PCB_TRACK":
                    _a, _b = ij.GetStart(), ij.GetEnd(); _w = ij.GetWidth() / 2 + 2000
                    _dx, _dy = _b.x - _a.x, _b.y - _a.y; _l2 = _dx * _dx + _dy * _dy
                    if _l2 > 0:
                        _u = max(0.0, min(1.0, ((q.x - _a.x) * _dx + (q.y - _a.y) * _dy) / _l2))
                        if (q.x - (_a.x + _u * _dx)) ** 2 + (q.y - (_a.y + _u * _dy)) ** 2 <= _w * _w: return True
                    elif abs(q.x - _a.x) <= _w and abs(q.y - _a.y) <= _w: return True
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
    starts = [(LI[L], i, j) for L, M in src.items() if L in LI for i, j in zip(*np.nonzero(M))]
    goal = np.zeros((len(LAYERS), NY, NX), dtype=bool)
    for L, M in goal_cells.items():
        if L in LI: goal[LI[L]] |= M
    passable = {LI[L]: ~trk[L] for L in LAYERS}
    for L, M in src.items():
        if L in LI: passable[LI[L]] |= M          # own pad copper is always enterable
    for L, M in goal_cells.items():
        if L in LI: passable[LI[L]] |= M
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
            for oL in range(len(LAYERS)):   # a through via reaches every routing layer
                if oL == L or not passable[oL][i, j]: continue
                nd = d + VIA_COST; t = (oL, i, j)
                if nd < dist.get(t, 1e18): dist[t] = nd; prev[t] = s; heapq.heappush(pq, (nd, t))
    if found is None: return None
    path = [found]
    while path[-1] in prev: path.append(prev[path[-1]])
    return list(reversed(path))
def src_is_here(src, L, i, j):
    M = src.get(LR[L])
    return M is not None and M[i, j]
def emit(net_item, path):
    net = net_item
    # Merge straight runs. This compared the vector of the run so far against the next STEP, so after one merge
    # the run was two cells long and the step one, the test failed, and it appended: a straight 20-cell run came
    # out as TEN segments instead of one. A 2,178-cell closure on board E therefore emitted 992 tracks, and
    # `stub_accept.py` refused it as "carpeting, not a closure" at its 400-item cap, which left the board one
    # open short through three router rounds. The path was always fine; the emission was not (11 September 2026).
    # The direction of the current run is carried instead, and every step is one grid cell by construction.
    segs = []; cur = [path[0]]; run = None
    for k in range(1, len(path)):
        a, c = path[k - 1], path[k]
        if a[0] != c[0]:                      # via: the run ends here whatever its direction
            segs.append(("trk", cur)); segs.append(("via", c)); cur = [c]; run = None; continue
        step = (c[1] - a[1], c[2] - a[2])
        if step == (0, 0): continue
        if step == run: cur[-1] = c           # same direction: extend the segment rather than start another
        else: cur.append(c); run = step
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

def _nearest_copper(net, L, x, y, reach=1.2):
    """The nearest point of this net's own copper on layer L to (x, y), or None.

    16 September 2026, board A35. The search reaches a GOAL CELL and the closure is emitted to that cell's
    CENTRE, which is the grid's idea of the copper, not the copper. A cell is a goal when the target's raster
    covers it, so the centre can sit a fraction of a cell outside the real edge, and a narrow closure laid to
    it then overlaps nothing: KiCad's connectivity does not move and the pieces are taken back off. Twelve of
    board A's opens sat behind that message, /POE_EN and /VBUS20 among them, each a path that was found and
    thrown away for the last few hundredths of a millimetre. So before giving up, the closure is finished ON
    the copper: the nearest point of this net's own track or pad is computed exactly and one short segment is
    laid to it. The retry is judged the same way as the closure itself, by KiCad's connectivity, and if it
    still does not connect everything comes off as before."""
    best = None
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        if t.GetClass() == "PCB_VIA":
            px, py = mm(t.GetPosition().x), mm(t.GetPosition().y)
        elif t.GetLayer() == L:
            ax, ay = mm(t.GetStart().x), mm(t.GetStart().y); ex, ey = mm(t.GetEnd().x), mm(t.GetEnd().y)
            dx, dy = ex - ax, ey - ay; L2 = dx * dx + dy * dy
            u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2))
            px, py = ax + u * dx, ay + u * dy
        else:
            continue
        d = math.hypot(x - px, y - py)
        if d <= reach and (best is None or d < best[0]): best = (d, px, py)
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() != net or not pad.IsOnLayer(L): continue
            px, py = mm(pad.GetPosition().x), mm(pad.GetPosition().y)
            d = math.hypot(x - px, y - py)
            if d <= reach and (best is None or d < best[0]): best = (d, px, py)
    return None if best is None else (best[1], best[2])

closed = 0
# 12 September 2026 (MESHSAT-862): a closure that does not close is worse than a refusal, because the finish and
# the record both read the count. A24's /+3V3 was reported "closed: 0 tracks, 1 vias, path 1 cells" TWICE, in two
# separate runs, and the DRC named the same open pair afterwards both times: the search reached a GOAL CELL, which
# is the target cluster's copper grown by the margin, and dropped a via in it that touches no copper at all. Every
# closure is now checked against KiCad's own connectivity and taken back off the board when it did not connect.
def _unconnected():
    try:
        b.BuildConnectivity(); return b.GetConnectivity().GetUnconnectedCount(False)
    except Exception:
        return None
_U = None   # taken lazily, just before the first closure: BuildConnectivity on a board with nothing to close is
            # work nobody asked for, and the finish that found this crashed inside the stub router with an empty
            # log on a board that had zero opens (12 September 2026)
for it1, it2 in pairs:
    net = it1["net"]; netobj = b.FindNet(net)
    if netobj is None or netobj.GetNetCode() <= 0: net = netname(net); netobj = b.FindNet(net)
    if netobj is None or netobj.GetNetCode() <= 0: print("  skip: net not found", it1["net"]); continue
    net = netobj.GetNetname()
    TW = 0.25; VIA_D, VIA_DR, VIA_COST = 0.6, 0.3, 50.0
    # 13 September 2026, measured: BOTH halves of this were dead, and the second was dead because of the first.
    # On KiCad 9 `netobj.GetNetClass()` returns a bare SwigPyObject with no methods, so the line below raises
    # AttributeError; the project-file fallback written on 7 September to repair exactly that was nested INSIDE
    # the same try, after the raising statement, so it was never reached on any board. Every stub closure since
    # has been laid at this TW of 0.25 mm (0.2 leaving a fine pad) with a 0.6/0.3 via, whatever the net's class
    # asked for: on board C that is 0.25 mm for a RAIL net whose class width is 0.5. The two lookups are
    # separate statements now, so a failure of one cannot silence the other.
    try:
        nc = netobj.GetNetClass(); TW = max(0.25, min(mm(nc.GetTrackWidth()), 1.0)); VIA_D = max(0.6, mm(nc.GetViaDiameter())); VIA_DR = max(0.3, mm(nc.GetViaDrill()))
    except Exception: pass
    # The project's explicit netclass_assignments (written by the placement generators) are the truth here, and
    # they are read whether or not pcbnew answered. `net` is the net NAME by this point, a string.
    _cl = None
    try:
        _pro = __import__("json").load(open(__import__("os").path.splitext(BOARD)[0] + ".kicad_pro")); _ns = _pro.get("net_settings", {})
        _cl = netclass.class_of(_ns.get("netclass_assignments"), net)
        if _cl:
            _c = [c for c in _ns.get("classes", []) if c.get("name") == _cl]
            if _c: TW = max(0.25, min(float(_c[0].get("track_width", TW)), 1.0)); VIA_D = max(0.6, float(_c[0].get("via_diameter", VIA_D))); VIA_DR = max(0.3, float(_c[0].get("via_drill", VIA_DR)))
    except Exception: pass
    # The width a closure is laid at was never printed, which is how 0.25 mm on a 0.5 mm class survived a week.
    print("  %s: class %s, track %.3f mm, via %.2f/%.2f mm" % (net, _cl or "(none resolved)", TW, VIA_D, VIA_DR))
    fine = [it for it in (it1, it2) if it["kind"] == "pad" and it["pad"] is not None and min(mm(it["pad"].GetSize().x), mm(it["pad"].GetSize().y)) < 0.4]
    if fine: TW = 0.2                                              # leaving a fine-pitch pad: thinnest allowed track
    # 15 September 2026 (MESHSAT-862), A32's last open. A closure is no wider than the piece it joins: /VBUS20 at U3 pad 3
    # was a TRACK end, the pad's own 0.2 mm escape stub, and the search asked for the NODE class's 0.5 mm track with a
    # 0.80/0.40 via through a 0.4 mm QFN's escape field, so it FAILED "track -> track" at a board-wide window while a
    # 0.25 mm run fits. A track end takes that track's width (never under 0.2), and a closure at or under 0.25 mm takes
    # the board's own minimum via, the one the escapes are laid with.
    for it in (it1, it2):
        if it["kind"] != "track" or it.get("x") is None: continue
        px, py = FromMM(it["x"]), FromMM(it["y"])
        ends = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK" and t.GetNetname() == net
                and min(math.hypot(t.GetStart().x - px, t.GetStart().y - py), math.hypot(t.GetEnd().x - px, t.GetEnd().y - py)) < 60000]
        if ends:
            w_end = min(mm(t.GetWidth()) for t in ends)
            if w_end < TW: print("  %s: the track end joined is %.2f mm wide, the closure takes that width instead of the class's %.2f" % (net, w_end, TW)); TW = max(0.2, w_end)
    if TW <= 0.25:
        _ds = b.GetDesignSettings(); _vd, _vdr = max(0.4, mm(_ds.m_ViasMinSize)), max(0.2, mm(_ds.m_MinThroughDrill))
        if _vd < VIA_D: print("  %s: a %.2f mm closure takes the board's minimum via %.2f/%.2f instead of the class's %.2f/%.2f" % (net, TW, _vd, _vdr, VIA_D, VIA_DR)); VIA_D, VIA_DR = _vd, _vdr
    trk, via = build_maps(net)
    # source = the pad if there is one, else the other item; goal = other item, or any via-able cell for plane nets
    a, c = (it1, it2) if it1["kind"] == "pad" else (it2, it1)
    src = copper_cells(a, net)
    if not src: print("  skip: no source copper for", a); continue
    if a.get("inner"):                                             # the source is an inner-layer track: start only where the joining via may stand
        for L in list(src): src[L] &= ~via
        if not any(M.any() for M in src.values()): print("  skip: no via-legal cell on the inner-layer source", a); continue
    if netname(net) in PLANES and not (a["kind"] == "pad" and c["kind"] == "pad"):   # pad-to-pad on a plane net: route it, do not just drop a via
        goal_cells = {L: ~via for L in LAYERS}
        for L in LAYERS: goal_cells[L] &= ~trk[L]
        win = 8.0 * WIN_SCALE
    else:
        goal_cells = other_cluster_cells(a, net, via); win = 15.0 * WIN_SCALE
        if not any(M.any() for M in goal_cells.values()):
            goal_cells = copper_cells(c, net)
            if c.get("inner"):
                for L in LAYERS: goal_cells[L] &= ~via
                INNER_GOAL = np.zeros((NY, NX), dtype=bool)
                for M in goal_cells.values(): INNER_GOAL |= M
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
    if _U is None: _U = _unconnected()
    _n_before = len(list(b.GetTracks()))
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
    _U1 = _unconnected()
    if _U is not None and _U1 is not None and _U1 >= _U:
        # the last fraction of a cell: finish on the copper itself before giving the closure up
        landed = 0
        for (Lp, ip, jp) in (path[-1], path[0]):
            ex, ey = float(X0 + jp * G), float(Y0 + ip * G)
            near = _nearest_copper(net, LR[Lp], ex, ey)
            if near is None: continue
            tx, ty = near
            if math.hypot(tx - ex, ty - ey) < 1e-6: continue
            t2 = pcbnew.PCB_TRACK(b); t2.SetStart(VECTOR2I(FromMM(ex), FromMM(ey))); t2.SetEnd(VECTOR2I(FromMM(tx), FromMM(ty)))
            t2.SetWidth(FromMM(TW)); t2.SetLayer(LR[Lp]); t2.SetNet(netobj); b.Add(t2); landed += 1
        _U2 = _unconnected() if landed else None
        if _U2 is not None and _U is not None and _U2 < _U:
            nt += landed; _U1 = _U2
            print("  landed on the copper: %s  %d short segment(s) from the goal cell centre to the net's own edge" % (net, landed))
        else:
            for t in list(b.GetTracks())[_n_before:]: b.Remove(t)
            b.BuildConnectivity()
            # THE MEASUREMENT, not a story. The obvious explanation (the goal cell centre sitting outside the
            # copper it stands for) is not supported by these rasterisers, which sample a cell CENTRE against
            # the shape's own half width, so the centre is on the copper and a 0.20 mm closure ending there
            # overlaps a 0.10 mm track. Rather than name a cause nothing measured, the refusal carries the two
            # end distances and the counts, and the next board that hits it says why (16 September 2026).
            def _gap(pt):
                Lp, ip, jp = pt; ex, ey = float(X0 + jp * G), float(Y0 + ip * G)
                near = _nearest_copper(net, LR[Lp], ex, ey, reach=5.0)
                return -1.0 if near is None else math.hypot(near[0] - ex, near[1] - ey)
            print("  NOT CLOSED: %s  %s -> %s (a path was found and it did not connect: start %.3f mm and "
                  "end %.3f mm from this net's nearest copper on their own layers, unconnected %s before and "
                  "%s after; %d piece(s) taken back off)"
                  % (net, a.get("kind"), c.get("kind"), _gap(path[0]), _gap(path[-1]),
                     _U, _U1, nt + nv + landed))
            continue
    _U = _U1 if _U1 is not None else _U
    closed += 1; print("  closed %s: %d tracks, %d vias, path %d cells" % (net, nt, nv, len(path)))
# A PASS THAT CLOSED NOTHING WRITES NOTHING (16 September 2026, A35's round two: both candidate closures were
# taken back off, and the fill-and-save of the unchanged board then segfaulted in KiCad's filler, exit 139, which
# the finish correctly refused as a tool crash. The board was identical to the input, so the whole write was a
# risk taken for no change. Filling and saving are the two most expensive and least safe things this tool does.)
if closed == 0:
    print("stub_router: closed 0 of %d, the board is untouched (nothing to fill and nothing to save)" % len(pairs))
else:
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(BOARD, b)
    print("stub_router: closed %d of %d" % (closed, len(pairs)))
