#!/usr/bin/env python3
"""besc1_passes.py <trial dir> <arm> <residue.json> <out.json> [workers]: read-only, EXPERIMENTAL (Q-B-ESC-1).

Second version, 27 September 2026. The first version listed, per split net, only the pads outside the net's LARGEST
copper cluster; where two or more clusters tie for largest, the one it kept as "main" was an accident of iteration
order, and a pad in it was never counted as open. That hid PCIE_PWR_EN3's U303.3 on A6 (three single-pad clusters
after passes 2 to 10) and over-counted A8's U301.108 (outside the largest cluster, yet joined to U301.105). This
version names no main cluster.

1. For the input board (pass 0) and every per-pass session the watcher copied (<arm>/watch/pass-NNN.ses, imported into
   a fresh load of the arm's input board with no zone fill and no save: the reading count_open.py --ses takes), it
   records per S3 net EVERY pad-bearing copper cluster (KiCad's connectivity: pads, tracks and vias joined by direct
   copper; no S3 net carries a zone). The per-pass total, the sum over nets of clusters less one, is checked against
   the watcher's passes.csv.
2. For every missing connection of the arm's final board (the edges of besc1_residue.py's residue-<arm>.json, a
   minimum spanning tree between the final board's pad-bearing clusters) it gives the connection's history. The
   connection joins two clusters of the FINAL board, X and Y. After a pass it is OPEN when no pad of X shares a copper
   cluster with any pad of Y in that pass's copper. Where both ends of the connection are pads it also gives the
   pad-to-pad reading (the two end pads in different clusters after the pass), which can only be open as often or more.
The final board's clusters are read from <arm>/s3.kicad_pcb the same way; a non-pad end of an edge (a track end or a
via) is placed in the cluster that has a track end or via at that point."""
import sys, os, json, glob, collections
sys.path.insert(0, "/root/besc1/v2/ecad/tools")
import multiprocessing as mp

T, ARM, RES, OUT = sys.argv[1:5]
WORKERS = int(sys.argv[5]) if len(sys.argv) > 5 else 6


def pid(p):
    return "%s.%s" % (p.GetParentFootprint().GetReference(), p.GetNumber())


def clusters(b, nets, want_anchor=False):
    """{net: [sorted pad ids per pad-bearing cluster]} for every net in `nets` (all nets, split or not), and when
    want_anchor, {net: [set of (x_nm, y_nm) anchor points per cluster]} for the same clusters."""
    b.BuildConnectivity(); conn = b.GetConnectivity()
    by_net = collections.defaultdict(list)
    for p in b.GetPads():
        if p.GetNetname() in nets:
            by_net[p.GetNetname()].append(p)
    for t in b.GetTracks():
        if t.GetNetname() in nets:
            by_net[t.GetNetname()].append(t)
    out = {}; anch = {}
    for n in sorted(nets):
        items = by_net.get(n, [])
        key = {it.m_Uuid.AsString(): i for i, it in enumerate(items)}
        par = list(range(len(items)))

        def f(i):
            while par[i] != i:
                par[i] = par[par[i]]; i = par[i]
            return i
        for i, it in enumerate(items):
            for q in list(conn.GetConnectedPads(it)) + list(conn.GetConnectedTracks(it)):
                j = key.get(q.m_Uuid.AsString())
                if j is not None:
                    par[f(i)] = f(j)
        cl = collections.defaultdict(list)
        for i, it in enumerate(items):
            cl[f(i)].append(it)
        padded = [c for c in cl.values() if any(it.GetClass() == "PAD" for it in c)]
        out[n] = sorted((sorted(pid(it) for it in c if it.GetClass() == "PAD") for c in padded), key=lambda c: (-len(c), c))
        if want_anchor:
            a = []
            for c in padded:
                s = set()
                for it in c:
                    if it.GetClass() in ("PAD", "PCB_VIA"):
                        v = it.GetPosition(); s.add((v.x, v.y))
                    else:
                        for v in (it.GetStart(), it.GetEnd()):
                            s.add((v.x, v.y))
                a.append((sorted(pid(it) for it in c if it.GetClass() == "PAD"), s))
            anch[n] = a
    return out, anch


def read_pass(args):
    ses, nets = args
    import pcbnew, ses_via_drill
    b = pcbnew.LoadBoard("%s/%s/pcb-b-compute.kicad_pcb" % (T, ARM))
    ok = True
    if ses:
        ok = pcbnew.ImportSpecctraSES(b, ses)
        ses_via_drill.restore_board(b, ses)
    cl, _ = clusters(b, nets)
    return (os.path.basename(ses)[5:8] if ses else "000"), bool(ok), {n: c for n, c in cl.items() if len(c) > 1}


if __name__ == "__main__":
    import pcbnew
    nets = set(json.load(open("%s/%s/part.json" % (T, ARM)))["groups"]["S3"])
    sessions = sorted(glob.glob("%s/%s/watch/pass-*.ses" % (T, ARM)))
    with mp.get_context("fork").Pool(WORKERS) as pool:
        got = pool.map(read_pass, [(None, nets)] + [(s, nets) for s in sessions])
    passes = {k: v for k, ok, v in got}
    imports = {k: ok for k, ok, v in got}
    totals = {k: sum(len(c) - 1 for c in v.values()) for k, v in passes.items()}
    import csv
    csvtot = {"%03d" % int(r["observed"]): int(r["open"]) for r in csv.DictReader(open("%s/%s/watch/passes.csv" % (T, ARM)))}
    # final board clusters and anchors
    fb = pcbnew.LoadBoard("%s/%s/s3.kicad_pcb" % (T, ARM))
    fcl, fan = clusters(fb, nets, want_anchor=True)
    res = json.load(open(RES))
    routed = [k for k in sorted(passes) if k != "000"]
    hist = []
    for net, v in sorted(res["nets"].items()):
        assert sorted(fcl[net]) == sorted(v["pad_clusters"]), (net, fcl[net], v["pad_clusters"])

        def side(end):
            it = end["item"]
            if it["kind"] == "pad":
                return [c for c, s in fan[net] if it["ref"] in c][0], it["ref"]
            x, y = int(round(end["at"][0] * 1e6)), int(round(end["at"][1] * 1e6))
            hits = [c for c, s in fan[net] if any(abs(x - sx) <= 1000 and abs(y - sy) <= 1000 for sx, sy in s)]
            assert len(hits) == 1, (net, end["at"], len(hits))
            return hits[0], None
        for e in v["edges"]:
            X, pa = side(e["a"]); Y, pb = side(e["b"])
            assert X != Y, (net, X)
            row = {"net": net, "cluster_a": X, "cluster_b": Y, "end_a": pa, "end_b": pb, "open_after": [], "pad_to_pad_open_after": [] if (pa and pb) else None}
            for k in routed:
                cl = passes[k].get(net)
                if cl is None:
                    continue   # the net is whole after this pass
                where = {}
                for i, c in enumerate(cl):
                    for p in c:
                        where[p] = i
                if not ({where.get(p) for p in X} & {where.get(p) for p in Y}) - {None}:
                    row["open_after"].append(k)
                if pa and pb and where.get(pa) != where.get(pb):
                    row["pad_to_pad_open_after"].append(k)
            hist.append(row)
    out = {"label": "EXPERIMENTAL (Q-B-ESC-1) per-pass clusters and connection histories (second version)", "arm": ARM,
           "method": __doc__.split("\n\n", 1)[1], "imports_ok": imports, "totals": totals, "passes_csv": csvtot,
           "totals_equal_passes_csv": all(totals[k] == csvtot.get(k) for k in routed),
           "passes": passes, "connections": hist}
    json.dump(out, open(OUT, "w"), indent=1)
    print(ARM, "totals", [totals[k] for k in sorted(totals)], "equal passes.csv:", out["totals_equal_passes_csv"])
    for r in hist:
        print("%-16s %-14s %-14s open %2d of %d %s pad-to-pad %s" % (
            r["net"], r["end_a"] or "copper", r["end_b"] or "copper", len(r["open_after"]), len(routed),
            ",".join(str(int(k)) for k in r["open_after"]),
            None if r["pad_to_pad_open_after"] is None else "%d (%s)" % (len(r["pad_to_pad_open_after"]), ",".join(str(int(k)) for k in r["pad_to_pad_open_after"]))))
