#!/usr/bin/env python3
"""besc1_viasite.py <trial dir> <arm> <residue.json> <out.json>: read-only, EXPERIMENTAL (Q-B-ESC-1).

Second version, 27 September 2026: every copper item is KiCad's own shape for it (pcbnew GetEffectiveShape per copper
layer: a pad's roundrect, rectangle, oval or custom outline, a track's segment with its width, a via's circle) and
every clearance is KiCad's own SHAPE Collide test. The first version modelled each pad as its bounding rectangle,
which over-states the copper at a rounded corner; three readings turned on that (U301.102 and U301.106 on A8's final
board and U301.86 on A6's input board, each with a site at 2 to 8 micrometres over the clearance).

For every pad that ends a missing S3 connection on the arm's final board (from besc1_residue.py) and lies in the S3
region, on two boards, the arm's INPUT board (placement and the escape pass's copper, before any routing) and its
FINAL board (after the router): the nearest via site within 3 mm of the pad centre, on a 0.05 mm grid centred on the
pad (the centre itself excluded), that
  (1) holds a through via of copper diameter D at 0.127 mm or more from every copper item of another net on every
      copper layer, and
  (2) is reached from the pad centre by a straight 0.127 mm track on the pad's own layer at 0.127 mm or more from every
      copper item of another net on that layer (the pad itself and its own net's copper are not obstacles),
for D = 0.40 (the escape pass's via on 0.4 mm rows), 0.70 (the router's via for the signal classes of S3 in this DSN)
and 0.80 (its via for PWR_S3). For the nearest site of each D it gives the site, the nearest foreign item to the via
and its distance to 1 micrometre, and how many sites the grid holds for that D (counted up to 25; nearest first, so
the nearest site always clears by less than one grid step, and it is the count that says whether a site is a
single point at the edge of the clearance or one of many). What the search leaves out, both ways: zone fills are not obstacles (they yield) and
drilled holes are not checked against holes or against copper by hole clearance, so a site found is not proof a via
fits; only straight stubs and grid points are tried, so a site not found is not proof that none exists."""
import sys, json, math, collections
sys.path.insert(0, "/root/besc1/v2/ecad/tools")
import pcbnew

T, ARM, RES, OUT = sys.argv[1:5]
CLR = 127000; TW = 127000; R = 3000000; STEP = 50000; BUCKET = 500000; DS = (0.40, 0.70, 0.80)
res = json.load(open(RES))
targets = {}
for net, v in res["nets"].items():
    for e in v["edges"]:
        for s in ("a", "b"):
            x = e[s]
            if x["item"]["kind"] == "pad" and x["region"].startswith("S3"):
                targets[x["item"]["ref"]] = net


def pid(p):
    return "%s.%s" % (p.GetParentFootprint().GetReference(), p.GetNumber())


def census(b):
    cu = [l for l in b.GetEnabledLayers().CuStack()]
    items = []   # (x0, y0, x1, y1, net, name, uuid, {layer: shape})
    for p in b.GetPads():
        shp = {l: p.GetEffectiveShape(l) for l in cu if p.IsOnLayer(l) and p.FlashLayer(l)}
        if shp:
            bb = p.GetBoundingBox()
            items.append((bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom(), p.GetNetname(), pid(p), p.m_Uuid.AsString(), shp))
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            shp = {l: t.GetEffectiveShape(l) for l in cu if t.FlashLayer(l)}
            name = "via %.2f" % (t.GetWidth(pcbnew.F_Cu) / 1e6)
        else:
            shp = {t.GetLayer(): t.GetEffectiveShape(t.GetLayer())}
            name = "track %s" % b.GetLayerName(t.GetLayer())
        bb = t.GetBoundingBox()
        items.append((bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom(), t.GetNetname(), name, t.m_Uuid.AsString(), shp))
    grid = collections.defaultdict(list)
    pad_r = int(max(DS) * 1e6 / 2) + CLR + 20000
    for k, it in enumerate(items):
        x0, y0, x1, y1 = it[0] - pad_r, it[1] - pad_r, it[2] + pad_r, it[3] + pad_r
        for gx in range(x0 // BUCKET, x1 // BUCKET + 1):
            for gy in range(y0 // BUCKET, y1 // BUCKET + 1):
                grid[(gx, gy)].append(k)
    return cu, items, grid


def near(grid, x, y):
    return grid.get((x // BUCKET, y // BUCKET), ())


def actual(shape, other, hi=2000000):
    """distance between two shapes to 1 um by bisection on KiCad's Collide"""
    if other.Collide(shape, 0):
        return 0
    lo = 0
    while hi - lo > 1000:
        m = (lo + hi) // 2
        if other.Collide(shape, m):
            hi = m
        else:
            lo = m
    return hi


def sites(board_path):
    b = pcbnew.LoadBoard(board_path)
    cu, items, grid = census(b)
    pads = {pid(p): p for p in b.GetPads()}
    out = {}
    n = R // STEP
    offs = sorted(((i * i + j * j), i, j) for i in range(-n, n + 1) for j in range(-n, n + 1) if (i or j) and (i * i + j * j) * STEP * STEP <= R * R)
    for ref, net in sorted(targets.items()):
        p = pads.get(ref)
        if p is None:
            continue
        me = p.m_Uuid.AsString()
        c = p.GetPosition()
        L = [l for l in cu if p.IsOnLayer(l)][0]
        row = {"layer": b.GetLayerName(L), "at": [round(c.x / 1e6, 3), round(c.y / 1e6, 3)]}
        best = {D: None for D in DS}; count = {D: 0 for D in DS}; okpts = {D: 0 for D in DS}
        for d2, i, j in offs:
            qx, qy = c.x + i * STEP, c.y + j * STEP
            cand = [items[k] for k in near(grid, qx, qy)]
            cand = [it for it in cand if it[4] != net and it[6] != me]
            ok = {}
            for D in DS:
                circ = pcbnew.SHAPE_CIRCLE(pcbnew.VECTOR2I(qx, qy), int(D * 1e6 / 2))
                good = True
                for it in cand:
                    if qx < it[0] - circ.GetRadius() - CLR or qx > it[2] + circ.GetRadius() + CLR or qy < it[1] - circ.GetRadius() - CLR or qy > it[3] + circ.GetRadius() + CLR:
                        continue
                    if any(s.Collide(circ, CLR) for s in it[7].values()):
                        good = False
                        break
                ok[D] = good
                if not good:
                    for D2 in DS:
                        if D2 > D:
                            ok[D2] = False
                    break
            if not any(ok.values()):
                continue
            for D in DS:
                if ok.get(D):
                    okpts[D] += 1
            if all(count[D] >= 25 for D in DS if ok.get(D)):
                continue
            q = pcbnew.VECTOR2I(qx, qy)
            stub = pcbnew.SHAPE_SEGMENT(c, q, TW)
            x0, x1, y0, y1 = min(c.x, qx) - TW - CLR, max(c.x, qx) + TW + CLR, min(c.y, qy) - TW - CLR, max(c.y, qy) + TW + CLR
            sc = set()
            for gx in range(x0 // BUCKET, x1 // BUCKET + 1):
                for gy in range(y0 // BUCKET, y1 // BUCKET + 1):
                    sc.update(grid.get((gx, gy), ()))
            good = True
            for k in sc:
                it = items[k]
                if it[4] == net or it[6] == me or L not in it[7]:
                    continue
                if it[2] < x0 or it[0] > x1 or it[3] < y0 or it[1] > y1:
                    continue
                if it[7][L].Collide(stub, CLR):
                    good = False
                    break
            if not good:
                continue
            for D in DS:
                if ok.get(D) and count[D] < 25:
                    count[D] += 1
                    if best[D] is None:
                        circ = pcbnew.SHAPE_CIRCLE(q, int(D * 1e6 / 2))
                        nf = None
                        for it in cand:
                            for l, s in it[7].items():
                                if abs(qx - (it[0] + it[2]) / 2) > 3e6 or abs(qy - (it[1] + it[3]) / 2) > 3e6:
                                    continue
                                a = actual(circ, s)
                                if nf is None or a < nf[0]:
                                    nf = (a, it[5], it[4], b.GetLayerName(l))
                        best[D] = {"nearest_site_mm": round(math.sqrt(d2) * STEP / 1e6, 3), "site_at": [round(qx / 1e6, 3), round(qy / 1e6, 3)],
                                   "nearest_foreign_to_via": None if nf is None else {"item": nf[1], "net": nf[2], "layer": nf[3], "mm": round(nf[0] / 1e6, 3)}}
        for D in DS:
            b_ = best[D] or {"nearest_site_mm": None}
            b_.update({"sites_found_up_to_25": count[D], "via_ok_points": okpts[D]})
            row["via_%.2f" % D] = b_
        out[ref] = row
        print(board_path.split("/")[-1], ref, row["layer"], [row["via_%.2f" % D]["nearest_site_mm"] for D in DS], flush=True)
    return out


if __name__ == "__main__":
    which = sys.argv[5] if len(sys.argv) > 5 else "both"
    result = {"label": "EXPERIMENTAL (Q-B-ESC-1) via-site search, KiCad's exact shapes (second version)", "arm": ARM,
              "method": __doc__.split("\n\n", 1)[1], "targets": targets}
    if which in ("both", "input"):
        result["input"] = sites("%s/%s/pcb-b-compute.kicad_pcb" % (T, ARM))
    if which in ("both", "final"):
        result["final"] = sites("%s/%s/s3.kicad_pcb" % (T, ARM))
    json.dump(result, open(OUT, "w"), indent=1)
