#!/usr/bin/env python3
"""Per-tile features and labels for the learned critic (MESHSAT-862 Stage E, 8 Sep 2026). From a pre-route board the FEATURES per TILE mm
square: pad count, fine-pitch pad count, escape via count, locked track length, the escape-envelope overlap area of place_audit.py, the number
of nets crossing the tile (HPWL boxes that intersect it), rule-area coverage; from the routed board and its DRC JSON the LABELS: unconnected
items whose ends fall in the tile, hard violations in the tile, router via count, track length. One CSV row per tile with the board name, the
pre-route hash and the sample id, appended to a results file. The analytical arm (E2) is place_audit.py's collision prediction read back
from the same rows; the supervised arm (E3) trains on the feature columns.

Usage: tile_labels.py <preroute.kicad_pcb> <routed.kicad_pcb> <drc.json> <out.csv> [--tile 10] [--sample ID]"""
import sys, os, json, csv, hashlib, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from place_audit import fine_pitch, escape_envelopes, overlap

def main(a):
    if len(a) < 4: print(__doc__); return 2
    tile = float(a[a.index("--tile") + 1]) if "--tile" in a else 10.0; sample = a[a.index("--sample") + 1] if "--sample" in a else ""
    pre = pcbnew.LoadBoard(a[0]); rt = pcbnew.LoadBoard(a[1]); d = json.load(open(a[2]))
    h = hashlib.sha256(open(a[0], "rb").read()).hexdigest()[:12]
    bb = pre.GetBoardEdgesBoundingBox(); x0, y0 = bb.GetLeft() / 1e6, bb.GetTop() / 1e6; nx, ny = int(bb.GetWidth() / 1e6 / tile) + 1, int(bb.GetHeight() / 1e6 / tile) + 1
    def key(x, y): return (int((x / 1e6 - x0) // tile), int((y / 1e6 - y0) // tile))
    F = {}
    def f(k, name, v=1):
        F.setdefault(k, {}); F[k][name] = F[k].get(name, 0) + v
    fps = list(pre.GetFootprints()); finefps = [fp for fp in fps if fine_pitch(fp)]
    env, escaped = escape_envelopes(pre, finefps)   # the measured escape fans of the pre-route board (place_audit.py)
    for fp in fps:
        fine = fp in finefps
        for p in fp.Pads():
            k = key(p.GetPosition().x, p.GetPosition().y); f(k, "pads")
            if fine: f(k, "fine_pads")
        if fine and escaped.get(fp.GetReference(), (0, []))[1]: f(key(fp.GetPosition().x, fp.GetPosition().y), "unescaped_pads", len(escaped[fp.GetReference()][1]))
    for t in pre.GetTracks():
        if t.GetClass() == "PCB_VIA": f(key(t.GetPosition().x, t.GetPosition().y), "escape_vias")
        else: f(key(t.GetStart().x, t.GetStart().y), "locked_len", t.GetLength() / 1e6)
    refs = sorted(env)
    for i in range(len(refs)):
        for j in range(i + 1, len(refs)):
            ox, oy = overlap(env[refs[i]], env[refs[j]])
            if ox > 0 and oy > 0:
                e = env[refs[i]]; cx, cy = (max(e[0], env[refs[j]][0]) + min(e[2], env[refs[j]][2])) / 2, (max(e[1], env[refs[j]][1]) + min(e[3], env[refs[j]][3])) / 2
                f(key(cx * 1e6, cy * 1e6), "env_overlap", ox * oy)
    nets = {}
    for fp in fps:
        for p in fp.Pads():
            if p.GetNetCode() > 0: nets.setdefault(p.GetNetname(), []).append((p.GetPosition().x / 1e6, p.GetPosition().y / 1e6))
    for n, pts in nets.items():
        if len(pts) < 2: continue
        xa, xb, ya, yb = min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)
        for gx in range(int((xa - x0) // tile), int((xb - x0) // tile) + 1):
            for gy in range(int((ya - y0) // tile), int((yb - y0) // tile) + 1): f((gx, gy), "nets_crossing")
    for z in pre.Zones():
        if not z.GetIsRuleArea(): continue
        zb = z.GetBoundingBox()
        for gx in range(int((zb.GetLeft() / 1e6 - x0) // tile), int((zb.GetRight() / 1e6 - x0) // tile) + 1):
            for gy in range(int((zb.GetTop() / 1e6 - y0) // tile), int((zb.GetBottom() / 1e6 - y0) // tile) + 1): f((gx, gy), "rule_area")
    L = {}
    def l(k, name, v=1):
        L.setdefault(k, {}); L[k][name] = L[k].get(name, 0) + v
    for u in d.get("unconnected_items", []):
        for it in u.get("items", [])[:1]:
            p = it.get("pos", {}); l(key(p.get("x", 0) * 1e6, p.get("y", 0) * 1e6), "opens")
    from hardset import HARD_POST, exempt
    for v in d.get("violations", []):
        if v.get("type") in HARD_POST and not exempt(v):
            for it in v.get("items", [])[:1]:
                p = it.get("pos", {}); l(key(p.get("x", 0) * 1e6, p.get("y", 0) * 1e6), "hard")
    for t in rt.GetTracks():
        if t.IsLocked(): continue
        if t.GetClass() == "PCB_VIA": l(key(t.GetPosition().x, t.GetPosition().y), "router_vias")
        else: l(key(t.GetStart().x, t.GetStart().y), "router_len", t.GetLength() / 1e6)
    cols = ["board", "sample", "prehash", "tx", "ty", "pads", "fine_pads", "unescaped_pads", "escape_vias", "locked_len", "env_overlap", "nets_crossing", "rule_area", "opens", "hard", "router_vias", "router_len"]
    new = not os.path.exists(a[3]); rows = 0
    with open(a[3], "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        if new: w.writeheader()
        for gx in range(nx):
            for gy in range(ny):
                k = (gx, gy); fe = F.get(k, {}); la = L.get(k, {})
                if not fe.get("pads") and not la: continue
                w.writerow(dict(board=os.path.basename(a[0]), sample=sample, prehash=h, tx=gx, ty=gy, **{c: round(fe.get(c, 0), 2) for c in cols[5:13]}, **{c: round(la.get(c, 0), 2) for c in cols[13:]})); rows += 1
    print("tile_labels: %d tiles of %.0f mm written for %s (pre-route %s, opens %d, hard %d)" % (rows, tile, sample or os.path.basename(a[1]), h, sum(x.get("opens", 0) for x in L.values()), sum(x.get("hard", 0) for x in L.values())))
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
