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
# Every candidate's geometry is read as plain numbers BEFORE the first connectivity build: after BuildConnectivity() the
# python wrappers of the pieces come back as bare SwigPyObjects (no .x, no Cast), measured on KiCad 9.0.9, 15 Sep 2026.
cands = []
for n in sorted(want):
    for t in b.GetTracks():
        if t.IsLocked() or netname(t.GetNetname()) != n or t.GetClass() not in ("PCB_TRACK", "PCB_VIA"): continue
        via = t.GetClass() == "PCB_VIA"
        s_, e_ = t.GetPosition(), (t.GetPosition() if via else t.GetEnd())
        cands.append(dict(t=t, net=n, via=via, code=t.GetNetCode(), layer=t.GetLayer(), sx=s_.x, sy=s_.y, ex=e_.x, ey=e_.y, w=t.GetWidth(),
                          drill=t.GetDrill() if via else 0, vtype=t.GetViaType() if via else 0, top=t.TopLayer() if via else 0, bot=t.BottomLayer() if via else 0,
                          L=0.0 if via else t.GetLength() / 1e6))
cands.sort(key=lambda c: (c["net"], c["via"], -c["L"]))   # per rail: tracks longest first, then vias
u0 = unconnected()
removed = {}; length = {}
for c in cands:
    b.Remove(c["t"])
    if unconnected() > u0:   # the only path: it goes back as it was
        if c["via"]:
            v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(c["sx"], c["sy"])); v.SetWidth(c["w"]); v.SetDrill(c["drill"]); v.SetViaType(c["vtype"]); v.SetLayerPair(c["top"], c["bot"]); v.SetNetCode(c["code"]); b.Add(v)
        else:
            k = pcbnew.PCB_TRACK(b); k.SetStart(pcbnew.VECTOR2I(c["sx"], c["sy"])); k.SetEnd(pcbnew.VECTOR2I(c["ex"], c["ey"])); k.SetWidth(c["w"]); k.SetLayer(c["layer"]); k.SetNetCode(c["code"]); b.Add(k)
        continue
    removed[c["net"]] = removed.get(c["net"], 0) + 1; length[c["net"]] = length.get(c["net"], 0.0) + c["L"]
for n in sorted(removed): print("rail_prune:   %-10s %d router piece(s) off, %.1f mm; the rail's own copper carries it" % (n, removed[n], length[n]))
if removed: pcbnew.SaveBoard(BOARD, b)
print("rail_prune: %d router piece(s) off %d rail(s) of %d, unconnected %d -> %d (%s)" % (sum(removed.values()), len(removed), len(want), u0, unconnected(), "board written" if removed else "nothing to do"))
