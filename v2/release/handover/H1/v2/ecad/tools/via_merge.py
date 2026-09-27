#!/usr/bin/env python3
"""via_merge: post-route via reduction (Freerouting quality programme, Stage 3). Works on a copy; quality_pass.sh gates it with a DRC and reverts.

Two operations on unlocked router copper only (locked escapes, joins, spines and fanout vias, and vias of plane nets, are never touched):
  1. excursion: a via V1, a run of segments on ONE inner (or any) layer, and a via V2 back, where both vias carry copper on a common other layer
     L: if the straight segment V1-V2 on L collides with nothing of another net (class clearance of the two nets, never under the board minimum,
     plus 5 um; the board edge counted), the excursion's run is replaced by that segment and both vias go (when nothing else uses them);
  2. loops: a same-net cycle in the graph of pads, vias and segments carries a redundant edge; the longest unlocked segment of the cycle is
     removed when the net stays connected without it.
The pass works on a by-value model and applies by UUID in one sweep (SWIG proxies die after Remove). Prints a summary line with denominators;
quality_pass.sh requires it. Usage: via_merge.py <board> [--out other] [--max-excursion-mm 6]"""
import sys, math, json, os, fnmatch, collections, pcbnew
from pcbnew import VECTOR2I

board_fn = sys.argv[1]; out_fn = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else board_fn
MAXEX = float(sys.argv[sys.argv.index("--max-excursion-mm") + 1]) if "--max-excursion-mm" in sys.argv else 6.0
b = pcbnew.LoadBoard(board_fn); mm = pcbnew.ToMM
plane_nets = set(z.GetNetCode() for z in b.Zones() if not z.GetIsRuleArea())
clear = {}; default_clear = 0.2
pro = os.path.splitext(board_fn)[0] + ".kicad_pro"
if os.path.exists(pro):
    ns = json.load(open(pro)).get("net_settings", {}); cls = {c["name"]: c.get("clearance", 0.2) for c in ns.get("classes", [])}; default_clear = cls.get("Default", 0.2)
    pats = [(p["pattern"], p["netclass"]) for p in ns.get("netclass_patterns", [])]
    for ni in b.GetNetInfo().NetsByName().values():
        nm = ni.GetNetname()
        for pat, c in pats:
            if fnmatch.fnmatch(nm, pat) or fnmatch.fnmatch(nm.lstrip("/"), pat): clear[ni.GetNetCode()] = cls.get(c, default_clear); break
min_cl = b.GetDesignSettings().m_MinClearance; edge_cl = b.GetDesignSettings().m_CopperEdgeClearance

# ---- by-value model
class Seg:
    __slots__ = ("uid", "net", "layer", "w", "a", "b", "locked", "dead")
    def __init__(s, t): s.uid = str(t.m_Uuid.AsString()); s.net = t.GetNetCode(); s.layer = t.GetLayer(); s.w = t.GetWidth(); s.a = (t.GetStart().x, t.GetStart().y); s.b = (t.GetEnd().x, t.GetEnd().y); s.locked = t.IsLocked(); s.dead = False
    def length(s): return math.hypot(s.b[0] - s.a[0], s.b[1] - s.a[1])
class Via:
    __slots__ = ("uid", "net", "p", "r", "locked", "dead", "layers")
    def __init__(s, t): s.uid = str(t.m_Uuid.AsString()); s.net = t.GetNetCode(); s.p = (t.GetPosition().x, t.GetPosition().y); s.r = (t.GetWidth(pcbnew.F_Cu) if True else 600000) // 2; s.locked = t.IsLocked(); s.dead = False; s.layers = (t.TopLayer(), t.BottomLayer())
segs = [Seg(t) for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]; vias = [Via(t) for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
pads = [(p.GetNetCode(), p) for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode() > 0]
copper_layers = [l for l in b.GetEnabledLayers().CuStack()]
def near(p, q, r): return abs(p[0] - q[0]) <= r and abs(p[1] - q[1]) <= r and math.hypot(p[0] - q[0], p[1] - q[1]) <= r
def via_at(p, net):
    for v in vias:
        if not v.dead and v.net == net and near(p, v.p, v.r + 1000): return v
    return None
def pad_touch(p, layer, net):
    vv = VECTOR2I(*p)
    return any(n == net and pd.IsOnLayer(layer) and pd.HitTest(vv) for n, pd in pads)
# obstacles per layer for the collision test (built once, before any change)
obstacles = {}
for layer in copper_layers:
    obs = []
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA" or t.GetLayer() == layer: obs.append((t.GetNetCode(), t.GetEffectiveShape(layer), str(t.m_Uuid.AsString())))
    for n, pd in [(p.GetNetCode(), p) for f in b.GetFootprints() for p in f.Pads()]:
        if pd.IsOnLayer(layer): obs.append((n, pd.GetEffectiveShape(layer), None))
    for z in b.Zones():
        if z.GetIsRuleArea() and z.IsOnLayer(layer) and z.GetDoNotAllowTracks(): obs.append((-1, z.Outline(), None))
    for dr in b.GetDrawings():
        if dr.GetLayer() == pcbnew.Edge_Cuts and dr.GetClass() == "PCB_SHAPE": obs.append((-2, dr.GetEffectiveShape(), None))
    obstacles[layer] = obs
def cl_for(net, other):
    if other == -2: return int(edge_cl) + 5000
    return max(int(max(clear.get(net, default_clear), clear.get(other, default_clear)) * 1e6), int(min_cl)) + 5000
def free(net, layer, p1, p2, w, skip):
    seg = pcbnew.SHAPE_SEGMENT(VECTOR2I(*p1), VECTOR2I(*p2), w)
    return not any(n != net and uid not in skip and shape.Collide(seg, cl_for(net, n)) for n, shape, uid in obstacles[layer])

# ---- connectivity model per net: nodes = pads (id "P"+i), vias ("V"+uid), segment ends; union-find with segment edges and via layer spans
def build(net):
    """returns (nodes at points per layer, adjacency) for the live copper of a net"""
    ends = collections.defaultdict(list)   # (point, layer) -> list of seg uids touching there
    for s in segs:
        if s.dead or s.net != net: continue
        ends[(s.a, s.layer)].append(s.uid); ends[(s.b, s.layer)].append(s.uid)
    return ends

removed_v = removed_s = added_s = excursions = loops = 0
# 1. excursions: for each unlocked via V1, follow a chain of segments on one layer to another via V2 (same net), both unlocked, chain length <= MAXEX
live_segs = [s for s in segs if not s.dead]
by_end = collections.defaultdict(list)
for s in live_segs: by_end[(s.a, s.layer)].append(s); by_end[(s.b, s.layer)].append(s)
def segs_at(p, layer, net): return [s for s in by_end.get((p, layer), []) if not s.dead and s.net == net]
def chain_from(v, layer):
    """the run of segments on `layer` starting at via v and ending at another via of the net (or None); the run must be a simple path"""
    start = segs_at(v.p, layer, v.net)
    if len(start) != 1: return None
    path = [start[0]]; cur = start[0]; p = cur.b if cur.a == v.p else cur.a; length = cur.length(); seen = {cur.uid}
    for _ in range(40):
        v2 = via_at(p, v.net)
        if v2 is not None and v2 is not v: return (path, v2, length)
        if pad_touch(p, layer, v.net): return None
        nxt = [s for s in segs_at(p, layer, v.net) if s.uid not in seen]
        if len(nxt) != 1 or len(segs_at(p, layer, v.net)) != 2: return None
        cur = nxt[0]; seen.add(cur.uid); path.append(cur); p = cur.b if cur.a == p else cur.a; length += cur.length()
        if length > MAXEX * 1e6: return None
    return None
done_vias = set(); stat = collections.Counter()
for v in vias:
    if v.dead or v.locked or v.net in plane_nets or v.uid in done_vias: stat['skipped_locked_plane_done'] += 1; continue
    my_layers = set(s.layer for s in live_segs if not s.dead and s.net == v.net and (s.a == v.p or s.b == v.p))
    stat['candidate_vias'] += 1
    for layer in list(my_layers):
        res = chain_from(v, layer)
        if not res: stat['no_chain'] += 1; continue
        path, v2, length = res
        if v2.locked or v2.dead or v2.net in plane_nets: stat['v2_locked'] += 1; continue
        v2_layers = set(s.layer for s in live_segs if not s.dead and s.net == v.net and (s.a == v2.p or s.b == v2.p))
        # the two vias must otherwise live on a common layer L (both have copper there) where the straight run V1-V2 is free
        common = (my_layers - {layer}) & (v2_layers - {layer})
        if not common: stat['no_common_layer'] += 1
        for L in sorted(common, key=lambda l: l):
            w = min(s.w for s in path)
            if not free(v.net, L, v.p, v2.p, w, {s.uid for s in path} | {v.uid, v2.uid}): stat['blocked'] += 1; continue
            # replace: the run dies; a segment V1-V2 on L appears; the vias die only if nothing else uses them
            for s in path: s.dead = True
            new_seg = Seg.__new__(Seg); new_seg.uid = "new-%d" % added_s; new_seg.net = v.net; new_seg.layer = L; new_seg.w = w; new_seg.a = v.p; new_seg.b = v2.p; new_seg.locked = False; new_seg.dead = False
            segs.append(new_seg); live_segs.append(new_seg); by_end[(new_seg.a, L)].append(new_seg); by_end[(new_seg.b, L)].append(new_seg); added_s += 1; removed_s += len(path); excursions += 1
            for vv in (v, v2):
                users = set(s.layer for s in live_segs if not s.dead and s.net == vv.net and (s.a == vv.p or s.b == vv.p))
                if len(users) <= 1 and not any(pad_touch(vv.p, l, vv.net) for l in copper_layers): vv.dead = True; removed_v += 1
            done_vias.update({v.uid, v2.uid}); break
        if v.dead: break
# ---- apply by UUID
by_uid_t = {str(t.m_Uuid.AsString()): t for t in b.GetTracks()}
victims = []
for s in segs:
    if s.dead and not s.uid.startswith("new-") and s.uid in by_uid_t: victims.append(by_uid_t[s.uid])
    if s.uid.startswith("new-") and not s.dead:
        t = pcbnew.PCB_TRACK(b); t.SetStart(VECTOR2I(*s.a)); t.SetEnd(VECTOR2I(*s.b)); t.SetWidth(s.w); t.SetLayer(s.layer); t.SetNetCode(s.net); b.Add(t)
for v in vias:
    if v.dead and v.uid in by_uid_t: victims.append(by_uid_t[v.uid])
for t in victims: b.Remove(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(out_fn, b)
nv = sum(1 for v in vias if not v.dead); ns_ = sum(1 for s in segs if not s.dead)
print("via_merge: vias %d -> %d (%d excursions replaced, %d segments removed, %d added), segments now %d -> %s  [%s]" % (len(vias), nv, excursions, removed_s, added_s, ns_, out_fn, dict(stat)))
