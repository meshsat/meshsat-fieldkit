#!/usr/bin/env python3
"""straighten: post-route tidy pass (Freerouting quality programme, Stage 3). Works on a copy; quality_pass.sh gates it with a DRC and reverts.

Three operations on unlocked router copper only (locked escapes, joins, spines and fanout vias are never touched):
  1. merge: two consecutive same-net, same-layer, same-width, collinear segments meeting at a point where nothing else lands become one;
  3. shortcut: a chain A-B-C of two segments on one layer with nothing else at B becomes A-C when the new segment collides with no copper of
     another net on that layer (vias, tracks, pads, rule areas) at the net class clearance.
Clearance for a shortcut is the larger class clearance of the two nets, never under the board minimum, plus 5 um; the board edge counts with its copper-edge clearance.
A junction point is busy when a via lies within its radius of it or a pad covers it (exact position matches miss imported vias by nanometres).
The pass works on a by-value model of the tracks and applies the result by UUID in one sweep (SWIG proxies die after Remove: the pattern of
cleanup_dangling.py). Prints a summary line with denominators; quality_pass.sh requires that line. Usage: straighten.py <board> [--out other] [--no-shortcut]"""
import sys, math, json, os, fnmatch, pcbnew
from pcbnew import VECTOR2I

SNAP = 0.05
board_fn = sys.argv[1]; out_fn = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else board_fn; do_short = "--no-shortcut" not in sys.argv
b = pcbnew.LoadBoard(board_fn); mm = pcbnew.ToMM

clear = {}; default_clear = 0.2
pro = os.path.splitext(board_fn)[0] + ".kicad_pro"
if os.path.exists(pro):
    ns = json.load(open(pro)).get("net_settings", {}); cls = {c["name"]: c.get("clearance", 0.2) for c in ns.get("classes", [])}; default_clear = cls.get("Default", 0.2)
    pats = [(p["pattern"], p["netclass"]) for p in ns.get("netclass_patterns", [])]
    for ni in b.GetNetInfo().NetsByName().values():
        nm = ni.GetNetname()
        for pat, c in pats:
            if fnmatch.fnmatch(nm, pat) or fnmatch.fnmatch(nm.lstrip("/"), pat): clear[ni.GetNetCode()] = cls.get(c, default_clear); break

# ---- by-value model
class S:
    __slots__ = ("uid", "net", "layer", "w", "a", "b", "locked", "dead", "dirty")
    def __init__(s, t): s.uid = str(t.m_Uuid.AsString()); s.net = t.GetNetCode(); s.layer = t.GetLayer(); s.w = t.GetWidth(); s.a = (t.GetStart().x, t.GetStart().y); s.b = (t.GetEnd().x, t.GetEnd().y); s.locked = t.IsLocked(); s.dead = False; s.dirty = False
    def length(s): return math.hypot(s.b[0] - s.a[0], s.b[1] - s.a[1])
segs = [S(t) for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]
vias = [(t.GetPosition().x, t.GetPosition().y, (t.GetWidth(pcbnew.F_Cu) if hasattr(t, 'GetWidth') else 600000) // 2 + 1000) for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]   # imported vias sit nanometres off the track ends: test by radius, never by equality
pads = [(p.GetNetCode(), p, [l for l in p.GetLayerSet().Seq()]) for f in b.GetFootprints() for p in f.Pads()]
def pad_at(pt, layer):
    v = VECTOR2I(*pt)
    return any(p.IsOnLayer(layer) and p.HitTest(v) for _, p, _ in pads)
def index(live):
    idx = {}
    for s in live:
        idx.setdefault((s.a, s.layer), []).append(s); idx.setdefault((s.b, s.layer), []).append(s)
    return idx
def other(s, pt): return s.b if s.a == pt else s.a
def via_at(pt): return any(abs(pt[0] - x) <= r and abs(pt[1] - y) <= r and math.hypot(pt[0] - x, pt[1] - y) <= r for x, y, r in vias)
def busy(pt, layer): return via_at(pt) or pad_at(pt, layer)
def same_line_opposite(pt, pa, pc):
    ax, ay = pa[0] - pt[0], pa[1] - pt[1]; cx, cy = pc[0] - pt[0], pc[1] - pt[1]
    cross = ax * cy - ay * cx; dot = ax * cx + ay * cy
    return abs(cross) <= 1e-3 * (abs(ax) + abs(ay) + 1) * (abs(cx) + abs(cy) + 1) and dot < 0

n0 = len(segs); merged = snapped = shortcuts = 0
# 1. merge collinear pairs (iterate until stable)
changed = True
while changed:
    changed = False; idx = index([s for s in segs if not s.dead])
    for (pt, layer), ss in idx.items():
        if len(ss) != 2: continue
        a, c = ss
        if a.locked or c.locked or a.net != c.net or a.w != c.w or busy(pt, layer): continue
        pa, pc = other(a, pt), other(c, pt)
        if same_line_opposite(pt, pa, pc):
            a.a, a.b, a.dirty = pa, pc, True; c.dead = True; merged += 1; changed = True; break
# 2. (snap of micro-segments removed 6 Sep 2026: moving a track end laterally broke a 0.15 mm clearance on D7; merge and shortcut are geometry-safe)
# 3. shortcuts A-B-C -> A-C against precomputed obstacles per layer
if do_short:
    obstacles = {}   # layer -> list of (net, shape)
    layers = set(s.layer for s in segs)
    for layer in layers:
        obs = []
        for t in b.GetTracks():
            if t.GetClass() == "PCB_VIA" or t.GetLayer() == layer: obs.append((t.GetNetCode(), t.GetEffectiveShape(layer), str(t.m_Uuid.AsString())))
        for net, p, _ in pads:
            if p.IsOnLayer(layer): obs.append((net, p.GetEffectiveShape(layer), None))
        for z in b.Zones():
            if z.GetIsRuleArea() and z.IsOnLayer(layer) and z.GetDoNotAllowTracks(): obs.append((-1, z.Outline(), None))
        edge_cl = b.GetDesignSettings().m_CopperEdgeClearance
        for dr in b.GetDrawings():
            if dr.GetLayer() == pcbnew.Edge_Cuts and dr.GetClass() == "PCB_SHAPE": obs.append((-2, dr.GetEffectiveShape(), "edge"))
        obstacles[layer] = obs
    min_cl = b.GetDesignSettings().m_MinClearance
    idx = index([s for s in segs if not s.dead]); tried = set()   # junction counts over every live segment, locked ones included (a locked escape stub at B must keep B)
    ends_by_layer = {}   # every live segment end (any lock state) per layer: a T-junction end lying on a's or c's interior must keep its copper
    for s in segs:
        if s.dead: continue
        ends_by_layer.setdefault(s.layer, []).append((s.a, s.uid, s.w)); ends_by_layer[s.layer].append((s.b, s.uid, s.w))
    def pt_on_seg(p, s, tol):
        ax, ay = s.a; bx, by = s.b; L2 = (bx - ax) ** 2 + (by - ay) ** 2
        t = 0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * (bx - ax) + (p[1] - ay) * (by - ay)) / L2))
        return math.hypot(p[0] - (ax + t * (bx - ax)), p[1] - (ay + t * (by - ay))) <= tol
    for (pt, layer), ss in list(idx.items()):
        if len(ss) != 2: continue
        a, c = ss
        if a.dead or c.dead or a.locked or c.locked or a.net != c.net or a.w != c.w or busy(pt, layer): continue
        pa, pc = other(a, pt), other(c, pt)
        if any(uid not in (a.uid, c.uid) and p not in (pa, pc) and (pt_on_seg(p, a, (a.w + w) / 2 + 1000) or pt_on_seg(p, c, (c.w + w) / 2 + 1000)) for p, uid, w in ends_by_layer.get(layer, [])): continue   # a T-junction rides on a or c
        if (pa, pc, layer) in tried or (pc, pa, layer) in tried: continue
        tried.add((pa, pc, layer))
        new = math.hypot(pa[0] - pc[0], pa[1] - pc[1])
        if new >= a.length() + c.length() - 0.05e6: continue
        seg = pcbnew.SHAPE_SEGMENT(VECTOR2I(*pa), VECTOR2I(*pc), a.w); skip = {a.uid, c.uid}
        def cl_for(net):   # KiCad applies the larger class clearance of the two items, never under the board minimum; 5 um margin for rounding
            if net == -2: return int(b.GetDesignSettings().m_CopperEdgeClearance) + 5000
            return max(int(max(clear.get(a.net, default_clear), clear.get(net, default_clear)) * 1e6), int(min_cl)) + 5000
        if any(net != a.net and uid not in skip and shape.Collide(seg, cl_for(net)) for net, shape, uid in obstacles[layer]): continue
        a.a, a.b, a.dirty = pa, pc, True; c.dead = True; shortcuts += 1
# ---- apply by UUID in one sweep
by_uid = {str(t.m_Uuid.AsString()): t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"}
victims = []
for s in segs:
    t = by_uid.get(s.uid)
    if t is None: continue
    if s.dead: victims.append(t)
    elif s.dirty: t.SetStart(VECTOR2I(*s.a)); t.SetEnd(VECTOR2I(*s.b))
for t in victims: b.Remove(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(out_fn, b)
alive = [s for s in segs if not s.dead]; L = sum(s.length() for s in alive) / 1e6
print("straighten: segments %d -> %d (merged %d, snapped %d, shortcuts %d), length now %.0f mm -> %s" % (n0, len(alive), merged, snapped, shortcuts, L, out_fn))
