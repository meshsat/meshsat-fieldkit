#!/usr/bin/env python3
"""route_metrics: the router-agnostic instrument of the Freerouting quality programme (plan of 6 Sep 2026, Stage 1).

Measures a routed board from its .kicad_pcb and its kicad-cli DRC JSON, never from a router log, so a Freerouting 1.9 result, a 2.x result,
a hand-routed board or a TopoR session all get the same numbers:
  completion (unrouted of N connections, nets), hard DRC by type, vias total / locked / router-added and per net, track length total / per
  layer / per net, segments and micro-segments, bends, the longest nets, per-net detour ratio (routed length over the pads' minimum spanning
  tree; median and p90), differential-pair skew for every *_P/*_N pair, layer balance, plus run-time fields the caller passes in.
Fail closed: a board with connected pads and no tracks, or a DRC JSON without a violations list, is UNMEASURABLE (exit 3), never zeros.
Usage: route_metrics.py <board.kicad_pcb> <drc.json|-> --json <out.json> [--wall S] [--autoroute MIN] [--optimizer MIN] [--tag NAME]"""
import sys, os, json, math, re, collections, statistics, pcbnew

HARD = ("clearance", "shorting_items", "tracks_crossing", "hole_clearance", "hole_to_hole", "copper_edge_clearance")

def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

def mst_length(points):
    """Prim's minimum spanning tree over pad centres (mm), the shortest any router could connect them with straight runs."""
    if len(points) < 2: return 0.0
    n = len(points); inside = [False] * n; best = [float("inf")] * n; best[0] = 0.0; total = 0.0
    for _ in range(n):
        u = min((i for i in range(n) if not inside[i]), key=lambda i: best[i]); inside[u] = True; total += best[u]
        ux, uy = points[u]
        for v in range(n):
            if not inside[v]:
                d = math.hypot(points[v][0] - ux, points[v][1] - uy)
                if d < best[v]: best[v] = d
    return total

def main():
    board_fn, drc_fn = sys.argv[1], sys.argv[2]; out_fn = arg("--json")
    b = pcbnew.LoadBoard(board_fn); mm = pcbnew.ToMM
    tracks = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]; vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    pads = [(f.GetReference(), p) for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode() > 0]
    if pads and not tracks: print("UNMEASURABLE: connected pads and no tracks in", board_fn); sys.exit(3)
    drc = None
    if drc_fn != "-":
        try: drc = json.load(open(drc_fn))
        except Exception as e: print("UNMEASURABLE: DRC JSON unreadable:", e); sys.exit(3)
        if not isinstance(drc.get("violations"), list): print("UNMEASURABLE: DRC JSON has no violations list"); sys.exit(3)
    nets = {code: ni.GetNetname() for code, ni in b.GetNetInfo().NetsByNetcode().items() if code > 0}
    # per-net tallies
    len_net = collections.Counter(); seg_net = collections.Counter(); via_net = collections.Counter(); via_net_locked = collections.Counter()
    len_layer = collections.Counter(); micro = 0; bends = 0
    by_net_layer = collections.defaultdict(list)
    for t in tracks:
        L = mm(t.GetLength()); code = t.GetNetCode(); len_net[code] += L; seg_net[code] += 1; len_layer[b.GetLayerName(t.GetLayer())] += L
        if L < 0.1: micro += 1
        by_net_layer[(code, t.GetLayer())].append(t)
    # bends: consecutive same-net same-layer segments meeting at a point with a direction change
    for (code, layer), segs in by_net_layer.items():
        ends = collections.defaultdict(list)
        for s in segs:
            ends[(s.GetStart().x, s.GetStart().y)].append(s); ends[(s.GetEnd().x, s.GetEnd().y)].append(s)
        for pt, ss in ends.items():
            if len(ss) == 2:
                a, c = ss
                da = (a.GetEnd().x - a.GetStart().x, a.GetEnd().y - a.GetStart().y); dc = (c.GetEnd().x - c.GetStart().x, c.GetEnd().y - c.GetStart().y)
                cross = da[0] * dc[1] - da[1] * dc[0]
                if abs(cross) > 1e-6 * (abs(da[0]) + abs(da[1]) + 1) * (abs(dc[0]) + abs(dc[1]) + 1): bends += 1
    for v in vias:
        via_net[v.GetNetCode()] += 1
        if v.IsLocked(): via_net_locked[v.GetNetCode()] += 1
    locked_tracks = sum(1 for t in tracks if t.IsLocked()); locked_len = sum(mm(t.GetLength()) for t in tracks if t.IsLocked())
    # detour ratio per net: routed length / MST of the net's pad centres (nets with 2+ pads and some copper)
    pads_net = collections.defaultdict(list)
    for ref, p in pads: pads_net[p.GetNetCode()].append((mm(p.GetPosition().x), mm(p.GetPosition().y)))
    detour = {}
    for code, pts in pads_net.items():
        if len(pts) < 2 or len_net[code] <= 0: continue
        m = mst_length(pts)
        if m > 1.0: detour[nets.get(code, str(code))] = round(len_net[code] / m, 3)
    dvals = sorted(detour.values())
    # differential pairs: *_P / *_N with matching stems
    pairs = {}
    for code, name in nets.items():
        stem = name[:-2] if name.endswith(("_P", "_N")) else None
        if stem: pairs.setdefault(stem, {})[name[-1]] = len_net[code]
    skew = {stem: round(abs(v["P"] - v["N"]), 3) for stem, v in pairs.items() if "P" in v and "N" in v}
    # DRC numbers
    hard = collections.Counter(); unrouted = None
    if drc is not None:
        for v in drc["violations"]:
            if v["type"] in HARD: hard[v["type"]] += 1
        unrouted = len(drc.get("unconnected_items", []))
    total_len = sum(len_net.values()); n_nets = len([c for c in nets if pads_net.get(c)]); n_conn = sum(max(0, len(p) - 1) for p in pads_net.values())
    longest = sorted(((round(L, 1), nets.get(c, str(c))) for c, L in len_net.items()), reverse=True)[:10]
    layer_share = {k: round(v / total_len, 3) for k, v in len_layer.items()} if total_len else {}
    res = {
        "board": os.path.basename(board_fn), "tag": arg("--tag", ""), "copper_layers": b.GetCopperLayerCount(),
        "nets": n_nets, "connections": n_conn, "pads": len(pads),
        "unrouted": unrouted, "hard": sum(hard.values()), "hard_by_type": dict(hard), "hard_types_checked": len(HARD),
        "vias": len(vias), "vias_locked": sum(via_net_locked.values()), "vias_router": len(vias) - sum(via_net_locked.values()), "vias_per_net": round(len(vias) / max(1, n_nets), 3),
        "tracks": len(tracks), "tracks_locked": locked_tracks, "length_mm": round(total_len, 1), "length_locked_mm": round(locked_len, 1), "length_per_pad_mm": round(total_len / max(1, len(pads)), 2),
        "length_by_layer_mm": {k: round(v, 1) for k, v in len_layer.items()}, "layer_share": layer_share,
        "layer_balance": round(max(layer_share.values()) / max(1e-9, min(layer_share.values())), 2) if len(layer_share) > 1 else None,
        "micro_segments": micro, "bends": bends, "longest_nets_mm": longest,
        "detour_median": round(statistics.median(dvals), 3) if dvals else None, "detour_p90": round(dvals[int(0.9 * (len(dvals) - 1))], 3) if dvals else None, "detour_nets": len(dvals),
        "pair_skew_mm": skew, "pairs_over_1mm": sum(1 for v in skew.values() if v > 1.0),
        "wall_seconds": float(arg("--wall", 0) or 0), "autoroute_minutes": float(arg("--autoroute", 0) or 0), "optimizer_minutes": float(arg("--optimizer", 0) or 0),
    }
    if out_fn: json.dump(res, open(out_fn, "w"), indent=1)
    print("metrics %s: unrouted %s of %d connections, hard %d of %d types, vias %d (router %d) on %d nets = %.2f/net, length %.0f mm, segments %d (micro %d, bends %d), detour median %s p90 %s, pairs over 1 mm %d" % (
        res["board"], res["unrouted"], n_conn, res["hard"], len(HARD), res["vias"], res["vias_router"], n_nets, res["vias_per_net"], total_len, len(tracks), micro, bends, res["detour_median"], res["detour_p90"], res["pairs_over_1mm"]))

if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    main()
