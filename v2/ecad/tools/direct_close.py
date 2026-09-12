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

Prints one line per open with what it tried and what happened, and `direct_close: N closed of M`."""
import sys, os, json, math, subprocess, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew, hardset
from verdict import write as verdict_write

mm = lambda v: v / 1e6
FromMM = pcbnew.FromMM


def loose_ends(b, net):
    """every track end of this net that no other piece of the net touches (SWIG hands out a fresh proxy per
    iteration, so pieces are compared by INDEX and by position, never by `is`: that trap is in the record twice)"""
    items = [(i, t) for i, t in enumerate(b.GetTracks()) if t.GetNetname() == net]
    pads = [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == net]
    out = []
    for i, t in items:
        if t.GetClass() != "PCB_TRACK": continue
        for p in (t.GetStart(), t.GetEnd()):
            n = 0
            for j, u in items:
                if j == i: continue
                if u.GetClass() == "PCB_VIA": n += (u.GetPosition() == p)
                else: n += (u.GetStart() == p or u.GetEnd() == p)
            for q in pads: n += bool(q.HitTest(p))
            if n == 0: out.append((p, t.GetLayer(), t.GetWidth()))
    return out


def open_nets(drc):
    nets = []
    for u in drc.get("unconnected_items", []):
        for it in u.get("items", []):
            d = it.get("description", "")
            if "[" in d and "]" in d:
                n = d[d.index("[") + 1:d.index("]")]
                if n not in nets: nets.append(n)
                break
    return nets


def counts(board_path, report):
    r = subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), "drc.sh"), board_path, report],
                       capture_output=True, text=True)
    if r.returncode != 0: return None
    try: c = hardset.counts(hardset.load(report))
    except Exception: return None
    return c["hard"], c["unrouted"]


def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    bp, drcp = argv[0], argv[1]
    opt = lambda k, d: next((a.split("=", 1)[1] for a in argv if a.startswith("--%s=" % k)), d)
    MAXD = float(opt("max", "3.0")); WIDTH = float(opt("width", "0")); DRY = "--dry" in argv
    VD, VDR = (float(v) for v in opt("via", "0.45/0.25").split("/"))
    work = os.path.splitext(bp)[0] + "-close-drc.json"
    b = pcbnew.LoadBoard(bp)
    before = counts(bp, work)
    if before is None: print("direct_close: the DRC did not run on the board as given"); return 3
    H0, U0 = before
    print("direct_close: board as given: hard %d unrouted %d" % (H0, U0))
    drc = json.load(open(drcp))
    todo = open_nets(drc)
    closed = 0; tried = 0; rows = []
    for net in todo:
        b = pcbnew.LoadBoard(bp)   # reload: the previous closure may have been kept
        ends = loose_ends(b, net)
        pads = [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == net]
        cands = []
        for pos, L, w in ends:
            for q in pads:
                if not q.IsOnLayer(L): continue
                g = mm(int(math.hypot(pos.x - q.GetPosition().x, pos.y - q.GetPosition().y)))
                if g <= MAXD: cands.append((g, pos, q.GetPosition(), L, w, q.GetParentFootprint().GetReference() + "." + q.GetNumber()))
        if not cands:
            rows.append({"net": net, "result": "no end within %.2f mm of a pad on its own layer" % MAXD}); continue
        g, a, c, L, w, ref = min(cands, key=lambda r: r[0])
        tried += 1
        shapes = [("direct", [a, c]),
                  ("L via x", [a, pcbnew.VECTOR2I(c.x, a.y), c]),
                  ("L via y", [a, pcbnew.VECTOR2I(a.x, c.y), c])]
        got = None
        for name, pts in shapes:
            b = pcbnew.LoadBoard(bp)
            n = b.FindNet(net)
            if n is None: break
            width = FromMM(WIDTH) if WIDTH else w
            for p, q in zip(pts, pts[1:]):
                if p == q: continue
                t = pcbnew.PCB_TRACK(b); t.SetStart(p); t.SetEnd(q); t.SetWidth(width); t.SetLayer(L); t.SetNet(n); t.SetLocked(True); b.Add(t)
            pcbnew.ZONE_FILLER(b).Fill(b.Zones())
            trial = os.path.splitext(bp)[0] + "-close-trial.kicad_pcb"
            pcbnew.SaveBoard(trial, b)
            pro = os.path.splitext(bp)[0] + ".kicad_pro"; tpro = os.path.splitext(trial)[0] + ".kicad_pro"
            if os.path.exists(pro): subprocess.run(["cp", pro, tpro])
            r = counts(trial, work)
            if r is None: continue
            H1, U1 = r
            if H1 <= H0 and U1 < U0:
                got = (name, H1, U1)
                if not DRY:
                    subprocess.run(["cp", trial, bp]); H0, U0 = H1, U1
                break
        if got:
            closed += 1
            print("direct_close: %-14s closed %.3f mm to %s on %s (%s); hard %d unrouted %d"
                  % (net, g, ref, b.GetLayerName(L), got[0], got[1], got[2]))
            rows.append({"net": net, "result": "closed", "shape": got[0], "gap_mm": round(g, 3), "to": ref})
        else:
            print("direct_close: %-14s %.3f mm to %s on %s: no shape the DRC accepts" % (net, g, ref, b.GetLayerName(L)))
            rows.append({"net": net, "result": "refused", "gap_mm": round(g, 3), "to": ref})
    for f in (os.path.splitext(bp)[0] + "-close-trial.kicad_pcb", os.path.splitext(bp)[0] + "-close-trial.kicad_pro"):
        if os.path.exists(f): os.remove(f)
    print("direct_close: %d closed of %d open net(s) with an end near a pad (%d open net(s) in all)" % (closed, tried, len(todo)))
    verdict_write("direct_close", "PASS", counts={"closed": closed, "tried": tried, "open_nets": len(todo)},
                  denominator=len(todo), note="a closure the router stopped short of, proposed as geometry and judged by the DRC",
                  evidence=rows)
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
