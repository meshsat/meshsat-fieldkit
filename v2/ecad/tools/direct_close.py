#!/usr/bin/env python3
"""direct_close.py <board.kicad_pcb> <drc.json> [--max=4.0] [--width=0] [--via=0.45/0.25] [--layers=In2.Cu,In3.Cu] [--dry]

The closure the router stopped short of, proposed as geometry and judged by the DRC (12 September 2026, MESHSAT-862).

A routed board of this set ends with a handful of connections open, and they are not all the same thing. A24's
were short: /CELL+ was 9.59 mm of clear board and /VBUS20 0.80 mm, both refused by the stub router, which
searches a 0.1 mm raster in which every cell next to the target pad is inside somebody's clearance, while the
track that would close the gap ends ON that pad, where the pad's own clearance does not apply to its own net.

C10's eleven, measured with this tool, are NOT that shape: every one is 39 to 298 mm, a connection the router
never made. They were read as short ones first, by comparing each loose track end with the nearest pad of its
net, and the nearest pad of the net is not the pad the connection is missing to (it was usually one already
connected). Whatever measures an open has to read the DRC's own pair, which is what this tool does now.

So this tool proposes the obvious geometry rather than searching for it: a straight locked track from the loose
end to the pad, then the two L shapes, and it keeps the first that the DRC accepts. Every attempt is judged on
the board itself, one closure at a time, and reverted unless the hard count is unchanged and the unconnected
count drops. It is the `fix_a15_node.py` pattern (a bar on top of the router's tracks, checked for crossings)
with the waypoints computed instead of typed, and it never runs before the router: a connection this closes is
one the router and the stub router both gave up on.

Every pair it works on is one the DRC itself named, at the two positions the DRC named them at: the first
version looked for the nearest pad of the net to a loose track end and proposed a closure to a pad that was
already connected (A24's +3V3, 2.035 mm to U11.1, where the DRC's own item said C104). The nearest copper of
the net to each named position is then the anchor, and it is a pad centre, a via centre or a track END, never
the middle of a track, where a closure would make a T the connectivity engine does not see.

Prints one line per open with what it tried and what happened, and `direct_close: N closed of M`."""
import sys, os, re, json, math, subprocess, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew, hardset
from verdict import write as verdict_write

mm = lambda v: v / 1e6
FromMM = pcbnew.FromMM


def counts(board_path, report):
    r = subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), "drc.sh"), board_path, report],
                       capture_output=True, text=True)
    if r.returncode != 0: return None
    try: d = hardset.load(report); c = hardset.counts(d)
    except Exception: return None
    return c["hard"], c["unrouted"], d



def parse_items(drc):
    """Every unconnected pair the DRC names, with the two POSITIONS it names them at. The DRC is the only
    authority on which two pieces are apart: the first version of this tool looked for the nearest pad of the
    net to a loose end and proposed a closure to a pad that was already connected (A24's +3V3, 12 September)."""
    out = []
    for u in drc.get("unconnected_items", []):
        its = u.get("items", [])
        if len(its) != 2: continue
        net = ""; ends = []
        for it in its:
            d = it.get("description", "")
            if "[" in d and "]" in d and not net: net = d[d.index("[") + 1:d.index("]")]
            p = it.get("pos") or {}
            if "x" not in p: ends = []; break
            lay = None
            if " on " in d: lay = d.rsplit(" on ", 1)[1].split(",")[0].strip()
            ends.append({"x": float(p["x"]), "y": float(p["y"]), "layer": lay, "what": d})
        if net and len(ends) == 2: out.append({"net": net, "ends": ends})
    return out


def pieces_of(b, net):
    """every piece of copper of this net, as (kind, point, layers, label); a track contributes both its ends"""
    out = []
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() != net: continue
            out.append(("pad", p.GetPosition(), [l for l in p.GetLayerSet().CuStack()],
                        "pad %s.%s" % (f.GetReference(), p.GetNumber()), p))
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        if t.GetClass() == "PCB_VIA": out.append(("via", t.GetPosition(), [l for l in t.GetLayerSet().CuStack()], "via", t))
        else:
            out.append(("end", t.GetStart(), [t.GetLayer()], "track end", t))
            out.append(("end", t.GetEnd(), [t.GetLayer()], "track end", t))
    return out


def clusters_of(b, net, items):
    """union-find over the net's own copper, so the two sides of an open are the two CLUSTERS and not the two
    pieces the DRC happened to name. A24's /+3V3 reads as 9.36 mm between the named pieces and the real gap
    between the two clusters is what a closure has to cross (12 September 2026)."""
    parent = list(range(len(items)))
    def find(i):
        while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
        return i
    def union(i, j):
        a, c = find(i), find(j)
        if a != c: parent[a] = c
    bypos = {}
    for i, (k, p, ls, lab, obj) in enumerate(items):
        bypos.setdefault((p.x, p.y), []).append(i)
        if k == "end":   # the two ends of one track are one piece
            pass
    for group in bypos.values():
        for j in group[1:]: union(group[0], j)
    # the two ends of the same track object are connected
    byobj = {}
    for i, (k, p, ls, lab, obj) in enumerate(items):
        byobj.setdefault(id(obj) if k != "end" else (obj.GetStart().x, obj.GetStart().y, obj.GetEnd().x, obj.GetEnd().y, obj.GetLayer()), []).append(i)
    for group in byobj.values():
        for j in group[1:]: union(group[0], j)
    # a point lying inside a pad of the net joins that pad
    pads = [(i, it) for i, it in enumerate(items) if it[0] == "pad"]
    for i, (k, p, ls, lab, obj) in enumerate(items):
        if k == "pad": continue
        for j, (k2, p2, ls2, lab2, pad) in pads:
            if pad.HitTest(p): union(i, j)
    return [find(i) for i in range(len(items))]


def anchor(b, net, end):
    """the real copper of this net at the piece the DRC named, at the position it named it at.

    The KIND matters and reading only the position got it wrong twice on A24 in one run: for `/VBUS20` the
    nearest copper to the Track item's position was pad U3.1, so the tool proposed U3.1 to U3.3 (two pads of one
    part, 0.8 mm apart, which is not the missing connection at all), and for `/CELL+` it anchored a Track item to
    pad R1.2 and called the gap 8.66 mm. A Pad item names its footprint and pad number; a Track item is anchored
    at a track END, never at the middle of a track, where a closure would make a T the connectivity engine does
    not see."""
    d = end["what"]; P = pcbnew.VECTOR2I(FromMM(end["x"]), FromMM(end["y"])); layer = end["layer"]
    m = re.search(r"[Pp]ad (\S+) \[[^\]]*\] of (\S+)", d)
    if m:   # "Pad 3 [/VBUS20] of U3 on F.Cu", "PTH pad 1 [/CELL+] of F1"
        num, ref = m.group(1), m.group(2)
        for f in b.GetFootprints():
            if f.GetReference() != ref: continue
            for p in f.Pads():
                if p.GetNumber() == num:
                    return (0.0, p.GetPosition(), [l for l in p.GetLayerSet().CuStack()], "pad %s.%s" % (ref, num))
    best = None
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        if t.GetClass() == "PCB_VIA":
            if d.startswith("Via") or d.startswith("PTH"):
                dd = math.hypot(mm(t.GetPosition().x - P.x), mm(t.GetPosition().y - P.y))
                if best is None or dd < best[0]: best = (dd, t.GetPosition(), [l for l in t.GetLayerSet().CuStack()], "via")
            continue
        if layer and t.GetLayer() != b.GetLayerID(layer): continue
        for q in (t.GetStart(), t.GetEnd()):
            dd = math.hypot(mm(q.x - P.x), mm(q.y - P.y))
            if best is None or dd < best[0]: best = (dd, q, [t.GetLayer()], "track end")
    if best is None:   # a zone, or a piece we do not model: fall back to the nearest pad of the net
        for f in b.GetFootprints():
            for p in f.Pads():
                if p.GetNetname() != net: continue
                dd = math.hypot(mm(p.GetPosition().x - P.x), mm(p.GetPosition().y - P.y))
                if best is None or dd < best[0]: best = (dd, p.GetPosition(), [l for l in p.GetLayerSet().CuStack()], "pad %s.%s" % (p.GetParentFootprint().GetReference(), p.GetNumber()))
    return best


def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    bp, drcp = argv[0], argv[1]
    opt = lambda k, d: next((a.split("=", 1)[1] for a in argv if a.startswith("--%s=" % k)), d)
    MAXD = float(opt("max", "4.0")); WIDTH = float(opt("width", "0")); DRY = "--dry" in argv
    VD, VDR = (float(v) for v in opt("via", "0.45/0.25").split("/"))
    DETOUR = [x for x in opt("layers", "").split(",") if x]   # free layers to try a two-via detour on
    work = os.path.splitext(bp)[0] + "-close-drc.json"
    trial = os.path.splitext(bp)[0] + "-close-trial.kicad_pcb"
    before = counts(bp, work)
    if before is None: print("direct_close: the DRC did not run on the board as given"); return 3
    H0, U0 = before[0], before[1]; D0 = before[2]
    print("direct_close: board as given: hard %d unrouted %d" % (H0, U0))
    pairs = parse_items(json.load(open(drcp)))
    closed = 0; tried = 0; rows = []
    for it in pairs:
        net = it["net"]; b = pcbnew.LoadBoard(bp)
        A = anchor(b, net, it["ends"][0]); B = anchor(b, net, it["ends"][1])
        if A and B:
            # the closest pair of points between the two CLUSTERS the DRC's two pieces belong to
            items_ = pieces_of(b, net); lab = clusters_of(b, net, items_)
            def near_idx(pt):
                return min(range(len(items_)), key=lambda i: (items_[i][1].x - pt.x) ** 2 + (items_[i][1].y - pt.y) ** 2)
            ca, cb = lab[near_idx(A[1])], lab[near_idx(B[1])]
            if ca != cb:
                best = None
                for i, (k1, p1, l1, n1, o1) in enumerate(items_):
                    if lab[i] != ca: continue
                    for j, (k2, p2, l2, n2, o2) in enumerate(items_):
                        if lab[j] != cb: continue
                        if not [l for l in l1 if l in l2]: continue
                        d2 = (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2
                        if best is None or d2 < best[0]: best = (d2, (0.0, p1, l1, n1), (0.0, p2, l2, n2))
                if best and best[0] < (A[1].x - B[1].x) ** 2 + (A[1].y - B[1].y) ** 2:
                    A, B = best[1], best[2]
        if not A or not B:
            rows.append({"net": net, "result": "no copper of the net at one end the DRC named"}); continue
        gap = math.hypot(mm(A[1].x - B[1].x), mm(A[1].y - B[1].y))
        common = [l for l in A[2] if l in B[2]]
        if gap > MAXD:
            print("direct_close: %-14s %.3f mm apart (%s to %s): beyond --max=%.1f, left to the router" % (net, gap, A[3], B[3], MAXD))
            rows.append({"net": net, "result": "beyond max", "gap_mm": round(gap, 3)}); continue
        if not common:
            # TWO ENDS ON DIFFERENT LAYERS ARE NOT A REFUSAL, they are a hop (12 September 2026, board C10).
            # C10 ended its third round at 0 hard and one open: U3 pad 10 on B.Cu, 1.7 mm from a track of its
            # own net on In2. The tool already lays a via wherever a shape changes layer (the detour shapes
            # below do), and it was declining to use that for the one case where a via is the whole answer.
            # This is `fix_d10_hubdm1.py`'s closure with the waypoints computed: a locked via and a short
            # locked track to the pad, judged by the DRC like every other shape here.
            La, Lb = A[2][0], B[2][0]
            tried += 1
            shapes = [("hop at %s" % B[3], [(La, A[1]), (La, B[1]), (Lb, B[1])]),
                      ("hop at %s" % A[3], [(La, A[1]), (Lb, A[1]), (Lb, B[1])]),
                      ("hop, L via x", [(La, A[1]), (La, pcbnew.VECTOR2I(B[1].x, A[1].y)), (La, B[1]), (Lb, B[1])]),
                      ("hop, L via y", [(La, A[1]), (La, pcbnew.VECTOR2I(A[1].x, B[1].y)), (La, B[1]), (Lb, B[1])])]
            L = La
        else:
            L = common[0] if len(common) == 1 else (A[2][0] if A[2][0] in common else common[0])
            tried += 1
            shapes = [("direct", [(L, A[1]), (L, B[1])]),
                      ("L via x", [(L, A[1]), (L, pcbnew.VECTOR2I(B[1].x, A[1].y)), (L, B[1])]),
                      ("L via y", [(L, A[1]), (L, pcbnew.VECTOR2I(A[1].x, B[1].y)), (L, B[1])])]
        # and the same geometry one layer down, which is what the router would have done: a short stub on the
        # anchors' own layer, a via at each end of it, and the run between them on a free layer. A's /+3V3 and
        # /VBUS20 are both refused on F.Cu for crossing other nets, and a detour is the only shape left that is
        # not hand work (12 September 2026).
        for Ld in ([b.GetLayerID(x) for x in DETOUR if b.GetLayerID(x) >= 0 and b.GetLayerID(x) != L] if common else []):
            f = min(0.6 / gap, 0.33) if gap > 0 else 0.33
            a1 = pcbnew.VECTOR2I(int(A[1].x + (B[1].x - A[1].x) * f), int(A[1].y + (B[1].y - A[1].y) * f))
            b1 = pcbnew.VECTOR2I(int(B[1].x + (A[1].x - B[1].x) * f), int(B[1].y + (A[1].y - B[1].y) * f))
            shapes.append(("via down to %s" % b.GetLayerName(Ld), [(L, A[1]), (L, a1), (Ld, a1), (Ld, b1), (L, b1), (L, B[1])]))
        got = None; whys = []
        for name, pts in shapes:
            b = pcbnew.LoadBoard(bp); n = b.FindNet(net)
            if n is None: break
            w = FromMM(WIDTH) if WIDTH else None
            if w is None:
                w = next((t.GetWidth() for t in b.GetTracks() if t.GetNetname() == net and t.GetClass() == "PCB_TRACK"), FromMM(0.2))
            for (lp, p), (lq, q) in zip(pts, pts[1:]):
                if lp != lq:
                    v = pcbnew.PCB_VIA(b); v.SetPosition(p); v.SetWidth(FromMM(VD)); v.SetDrill(FromMM(VDR))
                    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(n); v.SetLocked(True); b.Add(v)
                    continue
                if p == q: continue
                t = pcbnew.PCB_TRACK(b); t.SetStart(p); t.SetEnd(q); t.SetWidth(w); t.SetLayer(lp); t.SetNet(n); t.SetLocked(True); b.Add(t)
            pcbnew.ZONE_FILLER(b).Fill(b.Zones())
            pcbnew.SaveBoard(trial, b)
            pro = os.path.splitext(bp)[0] + ".kicad_pro"; tpro = os.path.splitext(trial)[0] + ".kicad_pro"
            if os.path.exists(pro): subprocess.run(["cp", pro, tpro])
            r = counts(trial, work)
            if r is None: continue
            H1, U1, D1 = r
            if H1 <= H0 and U1 < U0:
                got = (name, H1, U1)
                if not DRY: subprocess.run(["cp", trial, bp]); H0, U0 = H1, U1
                break
            # a refusal that does not name what it hit is the defect `escape_prune` was corrected for on 9 September
            was = collections.Counter((v.get("type"), " / ".join(i.get("description", "")[:44] for i in v.get("items", []))) for v in D0.get("violations", []) if v.get("type") in hardset.HARD_POST)
            now = collections.Counter((v.get("type"), " / ".join(i.get("description", "")[:44] for i in v.get("items", []))) for v in D1.get("violations", []) if v.get("type") in hardset.HARD_POST)
            new_hits = [k for k in (now - was)][:4]
            for t_, w_ in new_hits[:2]: whys.append("      %s: %s | %s" % (name, t_, w_))
            if H1 <= H0 and U1 >= U0 and not new_hits: whys.append("      %s: legal, and it closed nothing (unrouted %d)" % (name, U1))
        if got:
            closed += 1
            print("direct_close: %-14s closed %.3f mm, %s to %s on %s (%s); hard %d unrouted %d"
                  % (net, gap, A[3], B[3], b.GetLayerName(L), got[0], got[1], got[2]))
            rows.append({"net": net, "result": "closed", "shape": got[0], "gap_mm": round(gap, 3), "from": A[3], "to": B[3]})
        else:
            print("direct_close: %-14s %.3f mm, %s to %s on %s: no shape the DRC accepts" % (net, gap, A[3], B[3], b.GetLayerName(L)))
            for w_ in whys[:14]: print("direct_close: %s" % w_)
            rows.append({"net": net, "result": "refused", "gap_mm": round(gap, 3), "from": A[3], "to": B[3]})
    for f in (trial, os.path.splitext(trial)[0] + ".kicad_pro"):
        if os.path.exists(f): os.remove(f)
    print("direct_close: %d closed of %d tried (%d open pair(s) named by the DRC)" % (closed, tried, len(pairs)))
    verdict_write("direct_close", "PASS", counts={"closed": closed, "tried": tried, "open_pairs": len(pairs)},
                  denominator=len(pairs), note="a closure the router stopped short of, proposed as geometry and judged by the DRC",
                  evidence=rows)
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
