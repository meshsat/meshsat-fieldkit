#!/usr/bin/env python3
"""Take the router's own copper off a rail the rail's copper already carries (MESHSAT-862, 15 September 2026).

Freerouting never sees a pour: the rail bands, islands and planes the placement generators lay are zones, and a zone is
not in the DSN. So for every rail pad the router lays a wire of its own to the nearest copper it does see, and where
the rail already runs from source to load in a band the router lays a 0.5 mm inner track IN PARALLEL with it. The
solver then puts a share of the rail's current through that track because it is a conductor of the net, and IPC-2221
refuses it: A32's VIN_RAW carries 8 A up a 6 mm B.Cu band and 0.63 A of it in a 0.5 mm In2 track the whole way,
ratio 1.60, on a board whose band alone reads MET. 32.191 saw the same mechanism at a GAP in the copper; this is the
mechanism with no gap at all.

The rule: an UNLOCKED track or via on a rail net (the intent file's rails, the nets dc_drop judges) comes off when
the net stays as connected without it, judged by the board's own connectivity after each removal, longest piece
first. A piece that is the only path stays. The pours are not refilled between trials: removing a track never
shrinks a pour, so a connection that survives on the stale fill survives on the fresh one, and the finish refills
before anything judges. Locked copper (escapes, pre-router pairs, the rail copper itself, hand closures) is never
touched. Prints what came off, per rail, with the length.
"""
import sys, os, json, math, pcbnew

BOARD = sys.argv[1]
stem = os.path.splitext(os.path.basename(BOARD))[0]
here = os.path.dirname(os.path.abspath(BOARD))
ip = os.path.join(here, "out", stem + "-intent.json")
if not os.path.exists(ip): print("rail_prune: no intent file (%s), nothing judged" % ip); sys.exit(0)
rails = json.load(open(ip)).get("rails") or {}
names = list(rails) if isinstance(rails, dict) else [r.get("net") for r in rails]
b = pcbnew.LoadBoard(BOARD)
def netname(n): return n[1:] if n.startswith("/") else n
want = {netname(n) for n in names if n}
def unconnected():
    b.BuildConnectivity(); return b.GetConnectivity().GetUnconnectedCount(False)
u0 = unconnected()
removed = {}; length = {}
for n in sorted(want):
    # tracks and vias only: an arc (the pre-router's corners) has no start and end to put back and is left alone
    pieces = [t for t in b.GetTracks() if not t.IsLocked() and netname(t.GetNetname()) == n and t.GetClass() in ("PCB_TRACK", "PCB_VIA")]
    def L(t): return 0.0 if t.GetClass() == "PCB_VIA" else math.hypot(t.GetStart().x - t.GetEnd().x, t.GetStart().y - t.GetEnd().y) / 1e6
    pieces.sort(key=lambda t: (t.GetClass() == "PCB_VIA", -L(t)))   # tracks longest first, then vias
    for t in pieces:
        keep = (t.GetClass(), t.GetNetCode(), t.GetLayer(), t.GetStart(), t.GetEnd(), t.GetWidth(),
                (t.GetDrill(), t.GetViaType(), t.TopLayer(), t.BottomLayer()) if t.GetClass() == "PCB_VIA" else None)
        b.Remove(t)
        if unconnected() > u0:
            if keep[0] == "PCB_VIA":
                v = pcbnew.PCB_VIA(b); v.SetPosition(keep[3]); v.SetWidth(keep[5]); v.SetDrill(keep[6][0]); v.SetViaType(keep[6][1]); v.SetLayerPair(keep[6][2], keep[6][3]); v.SetNetCode(keep[1]); b.Add(v)
            else:
                s = pcbnew.PCB_TRACK(b); s.SetStart(keep[3]); s.SetEnd(keep[4]); s.SetWidth(keep[5]); s.SetLayer(keep[2]); s.SetNetCode(keep[1]); b.Add(s)
            continue
        removed[n] = removed.get(n, 0) + 1; length[n] = length.get(n, 0.0) + L(t)
for n in sorted(removed): print("rail_prune:   %-10s %d router piece(s) off, %.1f mm; the rail's own copper carries it" % (n, removed[n], length[n]))
if removed: pcbnew.SaveBoard(BOARD, b)
print("rail_prune: %d router piece(s) off %d rail(s) of %d, unconnected %d -> %d (%s)" % (sum(removed.values()), len(removed), len(want), u0, unconnected(), "board written" if removed else "nothing to do"))
