#!/usr/bin/env python3
"""count_open.py: the decisive number of the board B escape trial Q-B-ESC-1 (v2/docs/B-FEASIBILITY.md section 7).

EXPERIMENTAL. This measures one partition group of one board; it is not a gate, writes no verdict and decides nothing
about any board phase.

Usage:
  count_open.py <board.kicad_pcb> <part.json> <group> [--ses route.ses] [--parts U301,U302,...] [--json out.json]

The number: OPEN = the sum, over every net of the group (part.json "groups"[group]), of the ratsnest edges KiCad's own
connectivity reports for that net alone. A ratsnest edge is one missing connection between two copper clusters of the
net, so a net whose pads are all joined reads 0 and a net split in three reads 2. It is taken from pcbnew connectivity,
never from a DRC report (the DRC's unconnected list on this board is capped, RECORDED in b.json).

How one net is read alone, and why it is exact. The Python binding of KiCad 9 does not expose a per-net ratsnest
(`GetRatsnestForNet` returns an unwrapped object and `GetConnectedItems` needs a type vector SWIG cannot build; both
probed on the box on 25 September 2026). So the board is loaded once, every copper item's net is set to 0 in memory
(the board is never saved), and each net under test gets its own items back, one net at a time, before
`BuildConnectivity()` and `GetUnconnectedCount(False)`. A net-0 item takes part in no ratsnest, so the count is that
net's own. To keep this cheap a first pass walks each net's pads, tracks and vias with `GetConnectedPads` and
`GetConnectedTracks` (direct copper adjacency, no zones); a net that walk finds joined is joined, because leaving zones
out can only miss a connection, never invent one. Only the nets the walk finds split are read the exact way.

--ses imports a Freerouting session into the loaded board first (`ImportSpecctraSES` plus the via drills from
ses_via_drill), without a zone fill and without saving: the light per-pass reading plateau_watch.py uses. The final
reading of the trial is taken on the board ses_import_lock.py wrote (filled), without --ses.

Also reported: the pads of the named parts that sit outside their net's largest cluster (the residue, by part and
pad, read from the walk; on a net that carries a zone the walk can over-split, so those rows are marked), and the
group's copper per layer (track length and segment count) and via count."""
import sys, os, json, time, hashlib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, TOOLS)
import pcbnew  # noqa: E402

DEFAULT_PARTS = "U301,U302,U309,U310,U32B"


def opt(a, flag, default=None):
    if flag in a:
        i = a.index(flag)
        if i + 1 < len(a) and not a[i + 1].startswith("--"):
            return a[i + 1]
    return default


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pad_id(p):
    return "%s.%s" % (p.GetParentFootprint().GetReference(), p.GetNumber())


def walk_clusters(b, conn, pads):
    """Clusters of one net's pads by direct copper adjacency (pads, tracks, arcs, vias; zones not followed)."""
    left = {pad_id(p): p for p in pads}
    clusters = []
    while left:
        start = next(iter(left.values()))
        seen_items = set()
        got = set()
        stack = [start]
        while stack:
            it = stack.pop()
            key = it.m_Uuid.AsString()
            if key in seen_items:
                continue
            seen_items.add(key)
            if it.GetClass() == "PAD":
                got.add(pad_id(it))
            for q in conn.GetConnectedPads(it):
                if q.m_Uuid.AsString() not in seen_items:
                    stack.append(q)
            for t in conn.GetConnectedTracks(it):
                if t.m_Uuid.AsString() not in seen_items:
                    stack.append(t)
        got.add(pad_id(start))
        for g in got:
            left.pop(g, None)
        clusters.append(sorted(got))
    return clusters


def main(a):
    if len(a) < 3:
        print(__doc__)
        return 2
    board_path, part_path, group = a[0], a[1], a[2]
    ses = opt(a, "--ses")
    parts = set(filter(None, (opt(a, "--parts", DEFAULT_PARTS) or "").split(",")))
    out_json = opt(a, "--json")
    t0 = time.time()
    part = json.load(open(part_path))
    nets = set(part["groups"].get(group, []))
    if not nets:
        print("count_open: group %s has no nets in %s" % (group, part_path))
        return 2
    b = pcbnew.LoadBoard(board_path)
    imported = None
    if ses:
        ok = pcbnew.ImportSpecctraSES(b, ses)
        import ses_via_drill
        ses_via_drill.restore_board(b, ses)
        imported = {"ses": ses, "ses_sha256": sha256(ses), "import_ok": bool(ok)}
        if not ok:
            print("count_open: ImportSpecctraSES returned False for %s" % ses)
            return 2
    b.BuildConnectivity()
    conn = b.GetConnectivity()
    board_ratsnest_total = conn.GetUnconnectedCount(False)

    pads_by_net = collections.defaultdict(list)
    for p in b.GetPads():
        if p.GetNetname() in nets:
            pads_by_net[p.GetNetname()].append(p)
    zone_nets = {z.GetNetname() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() in nets}

    walk = {}
    for n in sorted(nets):
        ps = pads_by_net.get(n, [])
        walk[n] = walk_clusters(b, conn, ps) if ps else []
    suspects = sorted(n for n, cl in walk.items() if len(cl) > 1)

    # exact per-net ratsnest for the nets the walk found split
    items = [("pad", p) for p in b.GetPads()] + [("track", t) for t in b.GetTracks()] + \
            [("zone", z) for z in b.Zones() if not z.GetIsRuleArea()]
    orig = []
    for kind, it in items:
        orig.append(it.GetNetCode())
    by_code = collections.defaultdict(list)
    for (kind, it), code in zip(items, orig):
        by_code[code].append(it)
    code_of = {}
    for (kind, it), code in zip(items, orig):
        nm = it.GetNetname()
        if nm in nets:
            code_of[nm] = code
    for kind, it in items:
        it.SetNetCode(0)
    per_net = {}
    for n in suspects:
        code = code_of.get(n)
        if code is None:
            per_net[n] = len(walk[n]) - 1
            continue
        for it in by_code[code]:
            it.SetNetCode(code)
        b.BuildConnectivity()
        per_net[n] = b.GetConnectivity().GetUnconnectedCount(False)
        for it in by_code[code]:
            it.SetNetCode(0)
    for (kind, it), code in zip(items, orig):
        it.SetNetCode(code)
    b.BuildConnectivity()

    open_total = sum(per_net.values())
    residue = collections.defaultdict(list)
    for n in suspects:
        if per_net.get(n, 0) == 0:
            continue
        cl = sorted(walk[n], key=len, reverse=True)
        for c in cl[1:]:
            for pid in c:
                ref = pid.split(".", 1)[0]
                if ref in parts:
                    residue[ref].append({"pad": pid, "net": n, "zone_net": n in zone_nets})
    copper = collections.defaultdict(lambda: {"tracks_mm": 0.0, "segments": 0})
    vias = 0
    for t in b.GetTracks():
        if t.GetNetname() not in nets:
            continue
        if t.GetClass() == "PCB_VIA":
            vias += 1
            continue
        layer = b.GetLayerName(t.GetLayer())
        copper[layer]["tracks_mm"] += t.GetLength() / 1e6
        copper[layer]["segments"] += 1
    for v in copper.values():
        v["tracks_mm"] = round(v["tracks_mm"], 1)
    res = {
        "label": "EXPERIMENTAL (Q-B-ESC-1)",
        "board": os.path.abspath(board_path), "board_sha256": sha256(board_path),
        "part_json": os.path.abspath(part_path), "part_json_sha256": sha256(part_path), "group": group,
        "imported": imported, "copper_layers": b.GetCopperLayerCount(),
        "nets_in_group": len(nets), "nets_with_pads": len(pads_by_net), "zone_nets": sorted(zone_nets),
        "open": open_total, "open_nets": sorted(n for n, v in per_net.items() if v),
        "per_net_open": {n: v for n, v in sorted(per_net.items()) if v},
        "walk_split_nets": len(suspects),
        "residue": {k: v for k, v in sorted(residue.items())},
        "copper_by_layer": dict(sorted(copper.items())), "vias": vias,
        "board_ratsnest_total": board_ratsnest_total,
        "seconds": round(time.time() - t0, 1),
    }
    if out_json:
        with open(out_json, "w") as f:
            json.dump(res, f, indent=1)
    print("count_open: group %s open %d over %d nets (%d split by the walk), residue %s, vias %d, %.1f s"
          % (group, open_total, len(nets), len(suspects),
             {k: len(v) for k, v in res["residue"].items()}, vias, res["seconds"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
