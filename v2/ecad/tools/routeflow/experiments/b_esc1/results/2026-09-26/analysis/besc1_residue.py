#!/usr/bin/env python3
"""besc1_residue.py <trial dir> <arm> <out.json>: read-only analysis of Q-B-ESC-1's final S3 board (EXPERIMENTAL).

For every S3 net left split on <arm>/s3.kicad_pcb: its copper clusters (pads, tracks, vias joined by direct copper
adjacency; no S3 net carries a zone, so this is exact), the missing connections as a minimum spanning tree between
the pad-bearing clusters (nearest anchor points: pad centres, track ends, via centres), and for each end of each
missing connection the local facts: what the end is, whether the input board had an escape on that pad, the foreign
copper around it per layer, rule areas over it, and which partition region it sits in. Writes nothing on the board."""
import sys, json, math, collections
sys.path.insert(0, "/root/besc1/v2/ecad/tools")
import pcbnew

T, ARM, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
part = json.load(open("%s/%s/part.json" % (T, ARM)))
NETS = set(part["groups"]["S3"]); BOXES = part["boxes"]; MARGIN = float(part["margin"])


def pid(p):
    return "%s.%s" % (p.GetParentFootprint().GetReference(), p.GetNumber())


def P(v):
    return (round(v.x / 1e6, 3), round(v.y / 1e6, 3))


def region(x):
    cx = x - 150.0
    for r, (a, b) in BOXES.items():
        if a <= cx < b:
            return r + (" core" if (a + MARGIN) <= cx <= (b - MARGIN) else " margin")
    return "outside boxes"


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def seg_cross(p1, p2, q1, q2):
    def o(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2, d3, d4 = o(q1, q2, p1), o(q1, q2, p2), o(p1, p2, q1), o(p1, p2, q2)
    return (d1 * d2 < 0) and (d3 * d4 < 0)


b = pcbnew.LoadBoard("%s/%s/s3.kicad_pcb" % (T, ARM))
pre = pcbnew.LoadBoard("%s/%s/pcb-b-compute.kicad_pcb" % (T, ARM))
CU = [b.GetLayerName(l) for l in b.GetEnabledLayers().CuStack()]
b.BuildConnectivity(); conn = b.GetConnectivity()
pre.BuildConnectivity(); pconn = pre.GetConnectivity()
pre_pads = {pid(p): p for p in pre.GetPads()}

# copper census for proximity: (layer, kind, net, geometry)
geo = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        geo.append(("*", "via", t.GetNetname(), P(t.GetPosition()), None, t.GetWidth(pcbnew.F_Cu) / 2e6 if hasattr(t, "GetWidth") else 0.2))
    else:
        geo.append((b.GetLayerName(t.GetLayer()), "track", t.GetNetname(), P(t.GetStart()), P(t.GetEnd()), t.GetWidth() / 2e6))
for p in b.GetPads():
    bb = p.GetBoundingBox()
    lays = [b.GetLayerName(l) for l in p.GetLayerSet().CuStack()]
    for L in lays:
        geo.append((L, "pad", p.GetNetname(), (bb.GetLeft() / 1e6, bb.GetTop() / 1e6), (bb.GetRight() / 1e6, bb.GetBottom() / 1e6), pid(p)))
rule_areas = []
for z in b.Zones():
    if z.GetIsRuleArea():
        rule_areas.append({"name": z.GetZoneName(), "layers": [b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
                           "no_tracks": z.GetDoNotAllowTracks(), "no_vias": z.GetDoNotAllowVias(), "z": z})


def clearance(pt, net, radius=2.0):
    """per copper layer: nearest foreign copper edge distance (mm, bounding-box for pads) and item count within radius"""
    out = {L: {"nearest_mm": None, "n_within_%.1f" % radius: 0} for L in CU}
    for (L, kind, n, a, bb, w) in geo:
        if n == net:
            continue
        if kind == "track":
            d = seg_dist(pt, a, bb) - w
        elif kind == "via":
            d = math.hypot(pt[0] - a[0], pt[1] - a[1]) - (w or 0.2)
        else:
            dx = max(a[0] - pt[0], 0, pt[0] - bb[0]); dy = max(a[1] - pt[1], 0, pt[1] - bb[1]); d = math.hypot(dx, dy)
        if d > radius + 1.0:
            continue
        lays = CU if L == "*" else [L]
        for LL in lays:
            if LL not in out:
                continue
            o = out[LL]
            if o["nearest_mm"] is None or d < o["nearest_mm"]:
                o["nearest_mm"] = round(max(d, 0.0), 3)
            if d <= radius:
                o["n_within_%.1f" % radius] += 1
    return out


def rules_at(pt):
    v = pcbnew.VECTOR2I(int(pt[0] * 1e6), int(pt[1] * 1e6))
    return [{"name": r["name"], "layers": r["layers"], "no_tracks": r["no_tracks"], "no_vias": r["no_vias"]}
            for r in rule_areas if r["z"].Outline().Contains(v)]


def crossings(a, c, net):
    """foreign tracks crossed per layer by the straight line a-c, and foreign vias within 0.3 mm of it"""
    out = collections.Counter(); vias = 0
    for (L, kind, n, p1, p2, w) in geo:
        if n == net:
            continue
        if kind == "track" and seg_cross(a, c, p1, p2):
            out[L] += 1
        elif kind == "via" and seg_dist(p1, a, c) < 0.3 + (w or 0.2):
            vias += 1
    return dict(out), vias


def describe(item, pt):
    if item.GetClass() == "PAD":
        p = item; ref = pid(p)
        lays = [b.GetLayerName(l) for l in p.GetLayerSet().CuStack()]
        pp = pre_pads.get(ref)
        pre_esc = None
        if pp is not None:
            pre_esc = [("via" if t.GetClass() == "PCB_VIA" else pre.GetLayerName(t.GetLayer())) for t in pconn.GetConnectedTracks(pp)]
        fp = p.GetParentFootprint()
        neigh = []
        for q in fp.Pads():
            if q.GetNumber() == p.GetNumber():
                continue
            d = math.hypot((q.GetPosition().x - p.GetPosition().x) / 1e6, (q.GetPosition().y - p.GetPosition().y) / 1e6)
            if d <= 1.05:
                neigh.append({"pad": pid(q), "net": q.GetNetname(), "d_mm": round(d, 2),
                              "copper_on_it": len(list(conn.GetConnectedTracks(q)))})
        bb = p.GetBoundingBox()
        return {"kind": "pad", "ref": ref, "pinfunction": p.GetPinFunction(), "layers": lays if len(lays) < 3 else "through",
                "pad_mm": [round(bb.GetWidth() / 1e6, 3), round(bb.GetHeight() / 1e6, 3)],
                "copper_on_pad_final": [("via" if t.GetClass() == "PCB_VIA" else b.GetLayerName(t.GetLayer())) for t in conn.GetConnectedTracks(p)],
                "escape_on_input_board": pre_esc, "neighbours_within_1mm": neigh}
    if item.GetClass() == "PCB_VIA":
        return {"kind": "via", "layers": "through", "locked": item.IsLocked()}
    return {"kind": "track end", "layer": b.GetLayerName(item.GetLayer()), "width_mm": item.GetWidth() / 1e6, "locked": item.IsLocked()}


result = {"label": "EXPERIMENTAL (Q-B-ESC-1) residue analysis", "arm": ARM, "copper_layers": CU, "nets": {}}
for net in sorted(NETS):
    pads = [p for p in b.GetPads() if p.GetNetname() == net]
    tracks = [t for t in b.GetTracks() if t.GetNetname() == net]
    items = pads + tracks
    key = {it.m_Uuid.AsString(): i for i, it in enumerate(items)}
    par = list(range(len(items)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    for i, it in enumerate(items):
        for q in list(conn.GetConnectedPads(it)) + list(conn.GetConnectedTracks(it)):
            j = key.get(q.m_Uuid.AsString())
            if j is not None:
                par[find(i)] = find(j)
    cl = collections.defaultdict(list)
    for i, it in enumerate(items):
        cl[find(i)].append(it)
    padded = [c for c in cl.values() if any(it.GetClass() == "PAD" for it in c)]
    if len(padded) < 2:
        continue
    orphans = [c for c in cl.values() if not any(it.GetClass() == "PAD" for it in c)]

    def anchors(c):
        out = []
        for it in c:
            if it.GetClass() in ("PAD", "PCB_VIA"):
                out.append((P(it.GetPosition()), it))
            else:
                out.append((P(it.GetStart()), it)); out.append((P(it.GetEnd()), it))
        return out
    A = [anchors(c) for c in padded]
    pairs = []
    for i in range(len(padded)):
        for j in range(i + 1, len(padded)):
            best = None
            for (pa, ia) in A[i]:
                for (pb, ib) in A[j]:
                    d = math.hypot(pa[0] - pb[0], pa[1] - pb[1])
                    if best is None or d < best[0]:
                        best = (d, pa, ia, pb, ib)
            pairs.append((best[0], i, j, best))
    pairs.sort(key=lambda x: x[0])
    uf = list(range(len(padded)))

    def f2(i):
        while uf[i] != i:
            uf[i] = uf[uf[i]]; i = uf[i]
        return i
    edges = []
    for d, i, j, best in pairs:
        if f2(i) != f2(j):
            uf[f2(i)] = f2(j)
            _, pa, ia, pb, ib = best
            cr, vc = crossings(pa, pb, net)
            edges.append({"length_mm": round(d, 3),
                          "a": {"at": pa, "region": region(pa[0]), "item": describe(ia, pa), "clearance": clearance(pa, net), "rule_areas": rules_at(pa)},
                          "b": {"at": pb, "region": region(pb[0]), "item": describe(ib, pb), "clearance": clearance(pb, net), "rule_areas": rules_at(pb)},
                          "straight_line_foreign_track_crossings": cr, "straight_line_foreign_vias": vc})
    result["nets"][net] = {
        "pad_clusters": [sorted(pid(it) for it in c if it.GetClass() == "PAD") for c in sorted(padded, key=len, reverse=True)],
        "cluster_copper": [dict(collections.Counter(("via" if it.GetClass() == "PCB_VIA" else b.GetLayerName(it.GetLayer())) for it in c if it.GetClass() != "PAD")) for c in sorted(padded, key=len, reverse=True)],
        "orphan_copper_clusters": len(orphans), "open": len(padded) - 1, "edges": edges}
result["open_total"] = sum(v["open"] for v in result["nets"].values())
json.dump(result, open(OUT, "w"), indent=1, default=str)
print("besc1_residue %s: open %d over %d nets" % (ARM, result["open_total"], len(result["nets"])))
