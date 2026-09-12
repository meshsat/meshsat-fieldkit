#!/usr/bin/env python3
"""direct_close.py <board.kicad_pcb> <drc.json> [--max=3.0] [--width=0] [--via=0.45/0.25] [--dry] [--json=out.json]

The closure the router stopped short of, proposed as geometry and judged by the DRC (12 September 2026, MESHSAT-862).

A routed board of this set ends with a handful of connections open, and they are not all the same thing. Five of
C10's nine open nets have a loose track END 0.74 to 1.76 mm from the pad it should reach, ON THE SAME LAYER, and
A24's three are the same shape. The stub router answers "FAILED pad -> track" for every one of them with fourteen
million free cells in its window, so what it lacks is not room: it searches a 0.1 mm raster in which every cell
next to the target pad is inside somebody's clearance, while the track that would actually close the gap is a
straight 0.7 mm segment ending ON that pad, where the pad's own clearance does not apply to its own net.

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
import sys, os, json, math, subprocess, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew, hardset
from verdict import write as verdict_write

mm = lambda v: v / 1e6
FromMM = pcbnew.FromMM


def counts(board_path, report):
    r = subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), "drc.sh"), board_path, report],
                       capture_output=True, text=True)
    if r.returncode != 0: return None
    try: c = hardset.counts(hardset.load(report))
    except Exception: return None
    return c["hard"], c["unrouted"]



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


def anchor(b, net, ex, ey, layer):
    """the real copper of this net nearest the point the DRC named: a pad centre, a via centre, or a track END
    (never the middle of a track, where a closure would make a T the connectivity engine does not see)"""
    P = pcbnew.VECTOR2I(FromMM(ex), FromMM(ey))
    best = None
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() != net: continue
            if layer and not p.IsOnLayer(b.GetLayerID(layer)): continue
            d = math.hypot(mm(p.GetPosition().x - P.x), mm(p.GetPosition().y - P.y))
            if best is None or d < best[0]: best = (d, p.GetPosition(), [l for l in p.GetLayerSet().CuStack()], "pad %s.%s" % (f.GetReference(), p.GetNumber()))
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        if t.GetClass() == "PCB_VIA":
            d = math.hypot(mm(t.GetPosition().x - P.x), mm(t.GetPosition().y - P.y))
            if best is None or d < best[0]: best = (d, t.GetPosition(), [l for l in t.GetLayerSet().CuStack()], "via")
            continue
        if layer and t.GetLayer() != b.GetLayerID(layer): continue
        for q in (t.GetStart(), t.GetEnd()):
            d = math.hypot(mm(q.x - P.x), mm(q.y - P.y))
            if best is None or d < best[0]: best = (d, q, [t.GetLayer()], "track end")
    return best


def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    bp, drcp = argv[0], argv[1]
    opt = lambda k, d: next((a.split("=", 1)[1] for a in argv if a.startswith("--%s=" % k)), d)
    MAXD = float(opt("max", "4.0")); WIDTH = float(opt("width", "0")); DRY = "--dry" in argv
    VD, VDR = (float(v) for v in opt("via", "0.45/0.25").split("/"))
    work = os.path.splitext(bp)[0] + "-close-drc.json"
    trial = os.path.splitext(bp)[0] + "-close-trial.kicad_pcb"
    before = counts(bp, work)
    if before is None: print("direct_close: the DRC did not run on the board as given"); return 3
    H0, U0 = before
    print("direct_close: board as given: hard %d unrouted %d" % (H0, U0))
    pairs = parse_items(json.load(open(drcp)))
    closed = 0; tried = 0; rows = []
    for it in pairs:
        net = it["net"]; b = pcbnew.LoadBoard(bp)
        A = anchor(b, net, it["ends"][0]["x"], it["ends"][0]["y"], it["ends"][0]["layer"])
        B = anchor(b, net, it["ends"][1]["x"], it["ends"][1]["y"], it["ends"][1]["layer"])
        if not A or not B:
            rows.append({"net": net, "result": "no copper of the net at one end the DRC named"}); continue
        gap = math.hypot(mm(A[1].x - B[1].x), mm(A[1].y - B[1].y))
        common = [l for l in A[2] if l in B[2]]
        if gap > MAXD:
            print("direct_close: %-14s %.3f mm apart (%s to %s): beyond --max=%.1f, left to the router" % (net, gap, A[3], B[3], MAXD))
            rows.append({"net": net, "result": "beyond max", "gap_mm": round(gap, 3)}); continue
        if not common:
            print("direct_close: %-14s %s and %s share no copper layer" % (net, A[3], B[3]))
            rows.append({"net": net, "result": "no shared layer", "gap_mm": round(gap, 3)}); continue
        L = common[0] if len(common) == 1 else (A[2][0] if A[2][0] in common else common[0])
        tried += 1
        shapes = [("direct", [A[1], B[1]]),
                  ("L via x", [A[1], pcbnew.VECTOR2I(B[1].x, A[1].y), B[1]]),
                  ("L via y", [A[1], pcbnew.VECTOR2I(A[1].x, B[1].y), B[1]])]
        got = None
        for name, pts in shapes:
            b = pcbnew.LoadBoard(bp); n = b.FindNet(net)
            if n is None: break
            w = FromMM(WIDTH) if WIDTH else None
            if w is None:
                w = next((t.GetWidth() for t in b.GetTracks() if t.GetNetname() == net and t.GetClass() == "PCB_TRACK"), FromMM(0.2))
            for p, q in zip(pts, pts[1:]):
                if p == q: continue
                t = pcbnew.PCB_TRACK(b); t.SetStart(p); t.SetEnd(q); t.SetWidth(w); t.SetLayer(L); t.SetNet(n); t.SetLocked(True); b.Add(t)
            pcbnew.ZONE_FILLER(b).Fill(b.Zones())
            pcbnew.SaveBoard(trial, b)
            pro = os.path.splitext(bp)[0] + ".kicad_pro"; tpro = os.path.splitext(trial)[0] + ".kicad_pro"
            if os.path.exists(pro): subprocess.run(["cp", pro, tpro])
            r = counts(trial, work)
            if r is None: continue
            H1, U1 = r
            if H1 <= H0 and U1 < U0:
                got = (name, H1, U1)
                if not DRY: subprocess.run(["cp", trial, bp]); H0, U0 = H1, U1
                break
        if got:
            closed += 1
            print("direct_close: %-14s closed %.3f mm, %s to %s on %s (%s); hard %d unrouted %d"
                  % (net, gap, A[3], B[3], b.GetLayerName(L), got[0], got[1], got[2]))
            rows.append({"net": net, "result": "closed", "shape": got[0], "gap_mm": round(gap, 3), "from": A[3], "to": B[3]})
        else:
            print("direct_close: %-14s %.3f mm, %s to %s on %s: no shape the DRC accepts" % (net, gap, A[3], B[3], b.GetLayerName(L)))
            rows.append({"net": net, "result": "refused", "gap_mm": round(gap, 3), "from": A[3], "to": B[3]})
    for f in (trial, os.path.splitext(trial)[0] + ".kicad_pro"):
        if os.path.exists(f): os.remove(f)
    print("direct_close: %d closed of %d tried (%d open pair(s) named by the DRC)" % (closed, tried, len(pairs)))
    verdict_write("direct_close", "PASS", counts={"closed": closed, "tried": tried, "open_pairs": len(pairs)},
                  denominator=len(pairs), note="a closure the router stopped short of, proposed as geometry and judged by the DRC",
                  evidence=rows)
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
